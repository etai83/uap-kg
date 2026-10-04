"""Multi-case graph for the Graph page.

Each entity stays inside its case. A same_surface link joins two entities only
when the normalized name and the type are the same and the cases differ.
Arrow and AARO stay apart because their names differ.
"""

from __future__ import annotations

import difflib
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from uap_kg.extract.claim_entities import norm

WEB = Path(__file__).resolve().parent
REPO = WEB.parents[2]
ALIAS_PATH = WEB / "data" / "node_same.json"

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


def graph_payload(repo: Path | None = None, alias_path: Path | None = None) -> dict:
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
                    "members": [f"{prefix}:{person['id']}"],
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
                    "members": [node_id],
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
                    "members": [node_id],
                }
            )
        links.extend(_co_mention_links(prefix, entities))

    nodes, links = _join_same_names(nodes, links)
    path = alias_path or ALIAS_PATH
    state = _load_state(path)
    if state["groups"] and not state["log"]:
        state["log"] = _legacy_entries(nodes, state["groups"])
        saved_at = ""
        if path.is_file():
            saved_at = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).replace(microsecond=0).isoformat()
        for entry in state["log"]:
            entry["at"] = saved_at
        state["groups"] = []
        if state["log"]:
            _save_state(path, state)
    nodes, links = _apply_log(nodes, links, state["log"])
    return {
        "cases": cases,
        "nodes": nodes,
        "links": links,
        "log": [_public_entry(index, entry) for index, entry in enumerate(state["log"], start=1)],
        "undo": [_public_entry(index, entry) for index, entry in enumerate(state["undo"][-1] if state["undo"] else [], start=1)],
    }


def clean_name_score(text: str) -> tuple:
    raw = (text or "").strip()
    if not raw:
        return (-100, 0, 0, 0, 0)
    lower = raw.lower()
    penalty = 0
    bad_prefixes = (
        "man named ", "woman named ", "guy named ", "person named ",
        "someone named ", "knew ", "about ", "per ", "from ", "to ", "with "
    )
    bad_suffixes = (
        " interview", " story", " voice", "'s voice", " won't",
        " didn't", " said", " told", " audio", " video"
    )
    for bp in bad_prefixes:
        if lower.startswith(bp):
            penalty += 15
    for bs in bad_suffixes:
        if lower.endswith(bs):
            penalty += 15
    words = raw.split()
    title_words = sum(1 for w in words if w and w[0].isupper() and (len(w) == 1 or w[1:].islower()))
    ratio = (title_words / len(words)) if words else 0
    return (-penalty, round(ratio, 2), title_words, -len(words), -len(raw))


def _name_rank(node: dict) -> tuple:
    full = node.get("full") or node.get("label") or ""
    return clean_name_score(full)


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
        best = max(members, key=_name_rank)
        case_ids: list[str] = []
        shorts: list[str] = []
        folded: list[str] = []
        for member in members:
            alias[member["id"]] = new_id
            if member is not best:
                drop.add(member["id"])
            if member.get("caseId") and member["caseId"] not in case_ids:
                case_ids.append(member["caseId"])
                shorts.append(member.get("caseShort") or member["caseId"])
            for item in member.get("members") or [member["id"]]:
                if item not in folded:
                    folded.append(item)
        best["id"] = new_id
        best["members"] = folded
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


def _digest(members: list[str]) -> str:
    text = "\n".join(sorted(members))
    return hashlib.sha256(text.encode()).hexdigest()[:12]


def _public_entry(index: int, entry: dict) -> dict:
    return {
        "index": index,
        "at": entry.get("at") or "",
        "keepLabel": entry.get("keep_label") or "",
        "replaceLabel": entry.get("replace_label") or "",
    }


def _blank_state() -> dict:
    return {"log": [], "undo": [], "groups": []}


def _entry_members(entry: dict) -> list[str]:
    values = []
    for key in ("keep_members", "replace_members"):
        for item in entry.get(key) or []:
            if isinstance(item, str) and item and item not in values:
                values.append(item)
    return values


def _clean_entry(entry: dict) -> dict | None:
    if not isinstance(entry, dict):
        return None
    keep = [item for item in entry.get("keep_members") or [] if isinstance(item, str) and item]
    replace = [item for item in entry.get("replace_members") or [] if isinstance(item, str) and item]
    if not keep or not replace:
        return None
    return {
        "at": entry.get("at") or "",
        "keep_label": entry.get("keep_label") or "",
        "keep_type": entry.get("keep_type") or "",
        "keep_members": keep,
        "replace_label": entry.get("replace_label") or "",
        "replace_members": replace,
    }


def _load_state(path: Path) -> dict:
    if not path.is_file():
        return _blank_state()
    try:
        payload = json.loads(path.read_text())
    except json.JSONDecodeError:
        return _blank_state()
    if not isinstance(payload, dict):
        return _blank_state()
    log = [item for item in (_clean_entry(entry) for entry in payload.get("log") or []) if item]
    undo = []
    for batch in payload.get("undo") or []:
        if not isinstance(batch, list):
            continue
        cleaned = [item for item in (_clean_entry(entry) for entry in batch) if item]
        if cleaned:
            undo.append(cleaned)
    groups = []
    for group in payload.get("groups") or []:
        if not isinstance(group, list):
            continue
        ids = [item for item in group if isinstance(item, str) and item]
        if len(ids) >= 2:
            groups.append(ids)
    return {"log": log, "undo": undo, "groups": groups}


def _save_state(path: Path, state: dict) -> None:
    if not state["log"] and not state["undo"]:
        if path.is_file():
            path.unlink()
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"log": state["log"], "undo": state["undo"]}, indent=2) + "\n")


def _case_pairs(node: dict) -> list[tuple[str, str]]:
    case_ids = node.get("caseIds") or []
    parts = [part for part in (node.get("caseShort") or "").split(" · ") if part]
    if len(parts) == len(case_ids):
        return list(zip(case_ids, parts))
    return [(case_id, case_id) for case_id in case_ids]


def _legacy_entries(nodes: list[dict], groups: list[list[str]]) -> list[dict]:
    """Turn an older group file into log entries. The kept name is the one already shown."""
    by_member: dict[str, dict] = {}
    for node in nodes:
        for member in node.get("members") or [node["id"]]:
            by_member[member] = node
    entries = []
    for group in groups:
        found: list[dict] = []
        seen: set[str] = set()
        for member in group:
            node = by_member.get(member)
            if node is None or node["id"] in seen:
                continue
            seen.add(node["id"])
            found.append(node)
        if len(found) < 2:
            continue
        keep = max(found, key=_name_rank)
        replace_members: list[str] = []
        replace_names: list[str] = []
        for node in found:
            if node is keep:
                continue
            if node.get("full"):
                replace_names.append(node["full"])
            for member in node.get("members") or [node["id"]]:
                if member not in replace_members:
                    replace_members.append(member)
        if not replace_members:
            continue
        entries.append(
            {
                "at": "",
                "keep_label": keep.get("full") or "",
                "keep_type": keep.get("entityType") or "",
                "keep_members": list(keep.get("members") or [keep["id"]]),
                "replace_label": " · ".join(replace_names),
                "replace_members": replace_members,
            }
        )
    return entries


def _apply_log(nodes: list[dict], links: list[dict], entries: list[dict]) -> tuple[list[dict], list[dict]]:
    """Replay saved joins. The kept node stays. The other node's links move onto it."""
    if not entries:
        return nodes, links
    alias: dict[str, str] = {}
    drop: set[str] = set()
    for entry in entries:
        keep_members = set(entry.get("keep_members") or [])
        replace_members = set(entry.get("replace_members") or [])
        wanted = keep_members | replace_members
        matching = [
            node
            for node in nodes
            if node["id"] not in drop and wanted.intersection(node.get("members") or [node["id"]])
        ]
        if len(matching) < 2:
            continue
        survivor = max(matching, key=lambda node: len(keep_members.intersection(node.get("members") or [])))
        folded: list[str] = []
        case_ids: list[str] = []
        shorts: list[str] = []
        names: list[str] = []
        for node in matching:
            for item in node.get("members") or [node["id"]]:
                if item not in folded:
                    folded.append(item)
            for case_id, short in _case_pairs(node):
                if case_id not in case_ids:
                    case_ids.append(case_id)
                    shorts.append(short)
            if node.get("full") and node["full"] not in names:
                names.append(node["full"])
            for alias_name in node.get("also") or []:
                if alias_name and alias_name not in names:
                    names.append(alias_name)
        new_id = "same:" + _digest(folded)
        old_ids = [node["id"] for node in matching]
        for node in matching:
            if node is not survivor:
                drop.add(node["id"])
        for old_id, target in list(alias.items()):
            if target in old_ids:
                alias[old_id] = new_id
        for old_id in old_ids:
            alias[old_id] = new_id
        curator_label = entry.get("keep_label") or ""
        if curator_label and clean_name_score(curator_label)[0] == 0:
            keep_label = curator_label
        else:
            all_candidate_names = [name for name in ([curator_label] + names + [survivor.get("full")]) if name]
            keep_label = max(all_candidate_names, key=clean_name_score) if all_candidate_names else (survivor.get("full") or "")
        survivor["id"] = new_id
        survivor["members"] = folded
        survivor["full"] = keep_label
        survivor["label"] = clip(keep_label, 42)
        survivor["caseIds"] = case_ids
        survivor["caseShort"] = " · ".join(shorts)
        survivor["curator"] = True
        survivor["also"] = [name for name in names if name and name != keep_label]
        survivor["val"] = max(survivor.get("val") or 1, 1 + 0.8 * max(0, len(case_ids) - 1))
        if entry.get("keep_type"):
            survivor["entityType"] = entry["keep_type"]
        if any(node.get("kind") == "entity" for node in matching):
            survivor["kind"] = "entity"
        survivor["quote"] = next((n.get("quote") for n in matching if n.get("quote")), survivor.get("quote") or "")
    kept = [node for node in nodes if node["id"] not in drop]
    return kept, _collapse_links(links, alias, {node["id"] for node in kept})


def _collapse_links(links: list[dict], alias: dict[str, str], node_ids: set[str]) -> list[dict]:
    combined: dict[tuple, dict] = {}
    order: list[tuple] = []
    for link in links:
        source = alias.get(link["source"], link["source"])
        target = alias.get(link["target"], link["target"])
        if not source or not target or source == target:
            continue
        kind = link.get("kind") or "about"
        left, right = (source, target)
        if kind == "co_mention" and left > right:
            left, right = right, left
        mark = (left, right, kind)
        if mark not in combined:
            combined[mark] = {"source": left, "target": right, "kind": kind, "caseIds": []}
            order.append(mark)
        for case_id in list(link.get("caseIds") or []) + ([link["caseId"]] if link.get("caseId") else []):
            if case_id and case_id not in combined[mark]["caseIds"]:
                combined[mark]["caseIds"].append(case_id)
    return [
        link
        for link in (combined[mark] for mark in order)
        if link["source"] in node_ids and link["target"] in node_ids
    ]


def mark_same(keep_id: str, replace_id: str, alias_path: Path | None = None) -> dict:
    path = alias_path or ALIAS_PATH
    payload = graph_payload(alias_path=path)
    by_id = {node["id"]: node for node in payload["nodes"]}
    if keep_id not in by_id or replace_id not in by_id:
        raise KeyError(keep_id if keep_id not in by_id else replace_id)
    if keep_id == replace_id:
        raise ValueError("Choose two different nodes.")
    keep = by_id[keep_id]
    replace = by_id[replace_id]
    if keep.get("kind") == "claim" or replace.get("kind") == "claim":
        raise ValueError("A claim stays a claim. Join entities or people.")
    keep_type = keep.get("entityType") or ("named_person" if keep.get("kind") == "person" else "")
    replace_type = replace.get("entityType") or ("named_person" if replace.get("kind") == "person" else "")
    if keep_type and replace_type and keep_type != replace_type:
        raise ValueError(
            f"Cannot merge '{keep.get('full')}' ({keep_type}) with '{replace.get('full')}' ({replace_type}). "
            "Both nodes must share the same entity type."
        )
    keep_name = (keep.get("full") or keep.get("label") or "").strip()
    replace_name = (replace.get("full") or replace.get("label") or "").strip()
    keep_words = [w.lower() for w in keep_name.split() if len(w) > 1]
    replace_words = [w.lower() for w in replace_name.split() if len(w) > 1]
    if len(keep_words) >= 2 and len(replace_words) >= 2:
        if keep_words[-1] != replace_words[-1] and keep_words[0] == replace_words[0]:
            raise ValueError(
                f"Cannot merge '{keep_name}' with '{replace_name}'. They appear to be distinct individuals."
            )
    chosen_label = max([keep_name, replace_name], key=clean_name_score)
    state = _load_state(path)
    state["log"].append(
        {
            "at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "keep_label": chosen_label,
            "keep_type": keep_type or replace_type or keep.get("entityType") or "",
            "keep_members": list(keep.get("members") or [keep_id]),
            "replace_label": replace_name,
            "replace_members": list(replace.get("members") or [replace_id]),
        }
    )
    state["undo"] = []
    _save_state(path, state)
    return graph_payload(alias_path=path)


def revert_log(index: int, alias_path: Path | None = None) -> dict:
    """Keep the first `index` joins. Later joins stay in the undo stack."""
    path = alias_path or ALIAS_PATH
    state = _load_state(path)
    if index < 0 or index > len(state["log"]):
        raise ValueError("That version is not in the log.")
    removed = state["log"][index:]
    state["log"] = state["log"][:index]
    if removed:
        state["undo"].append(removed)
    _save_state(path, state)
    return graph_payload(alias_path=path)


def restore_log(alias_path: Path | None = None) -> dict:
    """Put back the joins removed by the latest revert."""
    path = alias_path or ALIAS_PATH
    state = _load_state(path)
    if not state["undo"]:
        raise ValueError("There is no newer version to restore.")
    state["log"].extend(state["undo"].pop())
    _save_state(path, state)
    return graph_payload(alias_path=path)


def closest_items(
    node_id: str,
    type_filter: str = "all",
    limit: int = 10,
    repo: Path | None = None,
    alias_path: Path | None = None,
) -> list[dict]:
    """Find top closest and most relevant items for a given node in the graph."""
    payload = graph_payload(repo=repo, alias_path=alias_path)
    nodes_by_id = {node["id"]: node for node in payload["nodes"]}
    if node_id not in nodes_by_id:
        return []

    target = nodes_by_id[node_id]
    target_name = (target.get("full") or target.get("label") or "").strip().lower()

    # Precompute 1-hop direct neighbors and link kinds
    direct: dict[str, list[str]] = {}
    for link in payload["links"]:
        s, t = link["source"], link["target"]
        kind = link.get("kind") or "co_mention"
        if s == node_id:
            direct.setdefault(t, []).append(kind)
        elif t == node_id:
            direct.setdefault(s, []).append(kind)

    # Precompute 2-hop shared neighbors
    two_hop: dict[str, int] = {}
    for link in payload["links"]:
        s, t = link["source"], link["target"]
        if s in direct and t != node_id and t not in direct:
            two_hop[t] = two_hop.get(t, 0) + 1
        elif t in direct and s != node_id and s not in direct:
            two_hop[s] = two_hop.get(s, 0) + 1

    ranked: list[dict] = []
    for other_id, other in nodes_by_id.items():
        if other_id == node_id:
            continue

        other_type = other.get("entityType") or other.get("kind") or "object"
        if type_filter != "all":
            if type_filter in ("named_person", "person"):
                if other.get("kind") != "person" and other_type not in ("named_person", "person"):
                    continue
            elif type_filter == "claim":
                if other.get("kind") != "claim":
                    continue
            else:
                if other_type != type_filter:
                    continue

        score = 0
        reason = ""

        # Direct connection has highest priority
        if other_id in direct:
            kinds = direct[other_id]
            if "same_surface" in kinds:
                score = 100
                reason = "Same surface entity across cases"
            elif "same_assertion" in kinds:
                score = 95
                reason = "Asserts same claim"
            elif "contradicts" in kinds:
                score = 92
                reason = "Contradicts claim"
            elif "elaborates" in kinds:
                score = 90
                reason = "Elaborates claim"
            elif "about" in kinds:
                score = 85
                reason = "Subject of claim"
            elif "made" in kinds:
                score = 85
                reason = "Claimant on record"
            else:
                score = 75 + min(len(kinds), 5) * 4
                reason = f"Mentioned together ({len(kinds)} moments)"
        elif other_id in two_hop:
            cnt = two_hop[other_id]
            score = 40 + min(cnt, 5) * 6
            reason = f"Shares {cnt} connection{'s' if cnt != 1 else ''}"

        # Lexical similarity
        other_name = (other.get("full") or other.get("label") or "").strip().lower()
        if target_name and other_name and len(target_name) >= 3 and len(other_name) >= 3:
            ratio = difflib.SequenceMatcher(None, target_name, other_name).ratio()
            if target_name in other_name or other_name in target_name:
                ratio = max(ratio, 0.78)
            if ratio >= 0.7:
                name_score = int(ratio * 76)
                if name_score > score:
                    score = name_score
                    reason = f"Similar name ({int(ratio * 100)}%)"

        # Case affinity bonus
        target_cases = set(target.get("caseIds") or ([target["caseId"]] if target.get("caseId") else []))
        other_cases = set(other.get("caseIds") or ([other["caseId"]] if other.get("caseId") else []))
        if target_cases and other_cases and (target_cases & other_cases):
            score += 3

        if score > 0:
            ranked.append(
                {
                    "node": other,
                    "score": score,
                    "reason": reason,
                }
            )

    ranked.sort(key=lambda item: (item["score"], len(item["node"].get("full") or "")), reverse=True)
    return ranked[:limit]

