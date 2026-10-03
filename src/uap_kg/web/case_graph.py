"""Multi-case graph for the Graph page.

Each entity stays inside its case. A same_surface link joins two entities only
when the normalized name and the type are the same and the cases differ.
Arrow and AARO stay apart because their names differ.
"""

from __future__ import annotations

import json
from pathlib import Path

from uap_kg.extract.claim_entities import norm

WEB = Path(__file__).resolve().parent
REPO = WEB.parents[2]

CASES = (
    {
        "id": "borland",
        "short": "Borland",
        "video_id": "K4gYHs84BIc",
        "case_file": "borland_case.json",
    },
    {
        "id": "grusch",
        "short": "Grusch",
        "video_id": "kRO5jOa06Qw",
        "case_file": None,
    },
    {
        "id": "corbell",
        "short": "Corbell",
        "video_id": "-XdvIrexF08",
        "case_file": None,
    },
)


def clip(text: str, limit: int) -> str:
    clean = " ".join((text or "").split())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 1].rstrip() + "…"


def _read_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text())
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _catalog_titles(repo: Path) -> dict[str, str]:
    store = _read_json(repo / "data" / "ui_store.json") or {}
    titles = {}
    for video in store.get("videos") or []:
        video_id = video.get("id")
        title = video.get("title")
        if video_id and title:
            titles[video_id] = title
    return titles


def _entity_rows(payload: dict | None, case_payload: dict | None) -> list[dict]:
    rows = []
    seen = set()
    for entity in (payload or {}).get("entities") or []:
        entity_id = entity.get("id")
        name = entity.get("name") or ""
        if not entity_id or not name:
            continue
        seen.add(entity_id)
        mentions = entity.get("mentions") or []
        quote = ""
        spans = set()
        for mention in mentions:
            if not isinstance(mention, dict):
                continue
            if not quote:
                quote = mention.get("quote") or ""
            if mention.get("span_index") is not None:
                spans.add(mention["span_index"])
        rows.append(
            {
                "id": entity_id,
                "name": name,
                "type": entity.get("type") or "object",
                "quote": quote,
                "spans": spans,
            }
        )
    for entity in (case_payload or {}).get("entities") or []:
        entity_id = entity.get("id")
        if not entity_id or entity_id in seen:
            continue
        rows.append(
            {
                "id": entity_id,
                "name": entity.get("name") or "",
                "type": entity.get("type") or "object",
                "quote": "",
                "spans": set(),
            }
        )
    return rows


def _co_mention_links(prefix: str, entities: list[dict]) -> list[dict]:
    """Items named in the same spoken moment are connected. This is not a claim."""
    by_span: dict[object, list[str]] = {}
    for entity in entities:
        node_id = f"{prefix}:{entity['id']}"
        for span in entity.get("spans") or ():
            by_span.setdefault(span, []).append(node_id)
    links = []
    seen = set()
    for members in by_span.values():
        unique = list(dict.fromkeys(members))
        if len(unique) < 2:
            continue
        for index, left in enumerate(unique):
            for right in unique[index + 1 :]:
                pair = (left, right) if left < right else (right, left)
                if pair in seen:
                    continue
                seen.add(pair)
                links.append(
                    {"source": pair[0], "target": pair[1], "kind": "co_mention", "caseId": prefix}
                )
    return links


def graph_payload(repo: Path | None = None) -> dict:
    root = repo or REPO
    titles = _catalog_titles(root)
    cases = []
    nodes = []
    links = []

    for spec in CASES:
        case_path = WEB / "data" / spec["case_file"] if spec["case_file"] else None
        case_payload = _read_json(case_path) if case_path else None
        entity_payload = _read_json(root / "data" / "entities" / f"{spec['video_id']}.entities.json")
        ready = entity_payload is not None or case_payload is not None
        title = ""
        if case_payload and isinstance(case_payload.get("case"), dict):
            title = case_payload["case"].get("title") or ""
        title = title or titles.get(spec["video_id"]) or spec["short"]
        entities = _entity_rows(entity_payload, case_payload) if ready else []
        claims = (case_payload or {}).get("claims") or []
        persons = (case_payload or {}).get("persons") or []
        cases.append(
            {
                "id": spec["id"],
                "short": spec["short"],
                "title": title,
                "video_id": spec["video_id"],
                "entities": len(entities),
                "claims": len(claims),
                "ready": ready,
            }
        )
        if not ready:
            continue
        prefix = spec["id"]
        for person in persons:
            nodes.append(
                {
                    "id": f"{prefix}:{person['id']}",
                    "caseId": prefix,
                    "caseShort": spec["short"],
                    "kind": "person",
                    "entityType": "",
                    "label": person.get("name") or "",
                    "full": person.get("name") or "",
                    "quote": person.get("role") or "",
                    "claimant": "",
                    "speaker": "",
                    "tStart": None,
                    "tEnd": None,
                    "videoId": spec["video_id"],
                    "val": 4,
                }
            )
        names = {person["id"]: person.get("name") or "" for person in persons}
        for claim in claims:
            node_id = f"{prefix}:{claim['id']}"
            nodes.append(
                {
                    "id": node_id,
                    "caseId": prefix,
                    "caseShort": spec["short"],
                    "kind": "claim",
                    "entityType": "",
                    "label": clip(claim.get("text") or "", 42),
                    "full": claim.get("text") or "",
                    "quote": claim.get("quote") or "",
                    "claimant": names.get(claim.get("claimant_id") or "", ""),
                    "speaker": claim.get("speaker_label") or "",
                    "tStart": claim.get("t_start"),
                    "tEnd": claim.get("t_end"),
                    "videoId": spec["video_id"],
                    "val": 1.4,
                }
            )
            claimant = claim.get("claimant_id")
            if claimant:
                links.append(
                    {
                        "source": node_id,
                        "target": f"{prefix}:{claimant}",
                        "kind": "made",
                        "caseId": prefix,
                    }
                )
            for entity_id in claim.get("entity_ids") or []:
                links.append(
                    {
                        "source": node_id,
                        "target": f"{prefix}:{entity_id}",
                        "kind": "about",
                        "caseId": prefix,
                    }
                )
        for link in (case_payload or {}).get("links") or []:
            kind = link.get("kind") or "elaborates"
            if kind not in {"elaborates", "contradicts", "same_assertion"}:
                continue
            links.append(
                {
                    "source": f"{prefix}:{link.get('source')}",
                    "target": f"{prefix}:{link.get('target')}",
                    "kind": kind,
                    "caseId": prefix,
                }
            )
        for entity in entities:
            node_id = f"{prefix}:{entity['id']}"
            nodes.append(
                {
                    "id": node_id,
                    "caseId": prefix,
                    "caseShort": spec["short"],
                    "kind": "entity",
                    "entityType": entity["type"],
                    "label": clip(entity["name"], 42),
                    "full": entity["name"],
                    "quote": clip(entity.get("quote") or "", 220),
                    "claimant": "",
                    "speaker": "",
                    "tStart": None,
                    "tEnd": None,
                    "videoId": spec["video_id"],
                    "val": 1,
                }
            )
        links.extend(_co_mention_links(prefix, entities))

    nodes, links = _join_same_names(nodes, links)
    return {"cases": cases, "nodes": nodes, "links": links}


def _join_same_names(nodes: list[dict], links: list[dict]) -> tuple[list[dict], list[dict]]:
    """One node for each name and type. Connections move onto that node."""
    groups: dict[tuple[str, str], list[dict]] = {}
    for node in nodes:
        if not node.get("caseIds"):
            node["caseIds"] = [node["caseId"]] if node.get("caseId") else []
        if node.get("kind") != "entity":
            continue
        key = (norm(node.get("full") or ""), node.get("entityType") or "")
        if len(key[0]) < 3:
            continue
        groups.setdefault(key, []).append(node)

    alias: dict[str, str] = {}
    drop: set[str] = set()
    for key, members in groups.items():
        if len(members) < 2:
            continue
        new_id = "name:" + key[1] + ":" + key[0]
        best = max(
            members,
            key=lambda item: (sum(char.isupper() for char in item.get("full") or ""), len(item.get("full") or "")),
        )
        case_ids: list[str] = []
        shorts: list[str] = []
        for member in members:
            alias[member["id"]] = new_id
            if member is not best:
                drop.add(member["id"])
            if member.get("caseId") and member["caseId"] not in case_ids:
                case_ids.append(member["caseId"])
                shorts.append(member.get("caseShort") or member["caseId"])
        best["id"] = new_id
        best["label"] = clip(best.get("full") or "", 42)
        best["caseIds"] = case_ids
        best["caseShort"] = " · ".join(shorts)
        best["val"] = 1 + 0.8 * max(0, len(case_ids) - 1)

    kept = [node for node in nodes if node["id"] not in drop]
    combined: dict[tuple, dict] = {}
    order: list[tuple] = []
    for link in links:
        if link.get("kind") == "same_surface":
            continue
        source = alias.get(link["source"], link["source"])
        target = alias.get(link["target"], link["target"])
        if not source or not target or source == target:
            continue
        kind = link.get("kind") or "about"
        undirected = kind == "co_mention"
        left, right = (source, target)
        if undirected and left > right:
            left, right = right, left
        mark = (left, right, kind)
        case_ids = list(link.get("caseIds") or [])
        if link.get("caseId"):
            case_ids.append(link["caseId"])
        if mark not in combined:
            combined[mark] = {"source": left, "target": right, "kind": kind, "caseIds": []}
            order.append(mark)
        for case_id in case_ids:
            if case_id and case_id not in combined[mark]["caseIds"]:
                combined[mark]["caseIds"].append(case_id)

    node_ids = {node["id"] for node in kept}
    kept_links = [
        link
        for link in (combined[mark] for mark in order)
        if link["source"] in node_ids and link["target"] in node_ids
    ]
    return kept, kept_links
