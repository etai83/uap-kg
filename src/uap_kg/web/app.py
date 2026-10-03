"""Aetheris navigator — FastAPI."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import BaseModel, Field

from . import store
from .case_graph import graph_payload

HERE = Path(__file__).resolve().parent
# Python 3.14 + Jinja default cache can choke on unhashable cache keys.
_env = Environment(
    loader=FileSystemLoader(str(HERE / "templates")),
    autoescape=select_autoescape(["html", "xml"]),
    cache_size=0,
)
templates = Jinja2Templates(env=_env)

app = FastAPI(title="Aetheris Intel", version="0.1.0")
app.mount("/static", StaticFiles(directory=str(HERE / "static")), name="static")


def _page(request: Request, name: str, active: str, **extra):
    return templates.TemplateResponse(
        request, name, {"active": active, **extra}
    )


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse("/timeline")


@app.get("/timeline", response_class=HTMLResponse)
def timeline(request: Request):
    return _page(request, "timeline.html", "timeline")


@app.get("/review", response_class=HTMLResponse)
def review(request: Request, video: str | None = None):
    return _page(request, "review.html", "review", video_id=video or "")


@app.get("/transcripts", response_class=HTMLResponse)
def transcripts(request: Request, video: str | None = None):
    return _page(request, "transcripts.html", "transcripts", video_id=video or "")


@app.get("/compare", response_class=HTMLResponse)
def compare(request: Request, event: str | None = "EVT-89-014"):
    return _page(request, "compare.html", "compare", event_id=event or "EVT-89-014")


@app.get("/graph", response_class=HTMLResponse)
def graph(request: Request):
    return _page(request, "graph.html", "graph")


@app.get("/api/graph")
def api_graph():
    return graph_payload()


@app.get("/catalog", response_class=HTMLResponse)
def catalog(request: Request):
    return _page(request, "catalog.html", "catalog")


@app.get("/case/borland", response_class=HTMLResponse)
def case_borland(request: Request):
    return _page(request, "case.html", "case")


@app.get("/case/borland/sigma", response_class=HTMLResponse)
def case_borland_sigma(request: Request):
    return _page(request, "case_sigma.html", "case")


@app.get("/api/cases/borland")
def api_case_borland():
    path = HERE / "data" / "borland_case.json"
    if not path.is_file():
        raise HTTPException(404, "borland case is not built")
    return json.loads(path.read_text())


@app.get("/docs-link", include_in_schema=False)
def docs_link():
    return RedirectResponse("/catalog")


# ---------- API ----------


@app.get("/api/bootstrap")
def api_bootstrap():
    data = store.load()
    videos = data["videos"]
    for v in videos:
        v["has_spans"] = bool(store.spans_for_video(v["id"]))
    return {
        "videos": videos,
        "events": data["events"],
        "claims": data["claims"],
        "open_questions": data["open_questions"],
        "event_count": len(data["events"]),
        "pending_claims": sum(1 for c in data["claims"] if c["lifecycle"] == "proposed"),
    }


@app.get("/api/videos/{video_id}/spans")
def api_spans(video_id: str):
    data = store.load()
    video = next((v for v in data["videos"] if v["id"] == video_id), None)
    if not video:
        raise HTTPException(404, "unknown video")
    spans = store.spans_for_video(video_id)
    return {"video": video, "spans": spans}


@app.post("/api/claims/{claim_id}/lifecycle")
def api_claim_lifecycle(claim_id: str, body: dict):
    target = body.get("lifecycle")
    if target not in {"live", "rejected", "superseded", "proposed"}:
        raise HTTPException(400, "invalid lifecycle")
    data = store.load()
    claim = next((c for c in data["claims"] if c["id"] == claim_id), None)
    if not claim:
        raise HTTPException(404, "unknown claim")
    if target == "live" and claim["lifecycle"] != "proposed":
        raise HTTPException(400, "only proposed claims can be approved")
    claim["lifecycle"] = target
    store.save(data)
    return claim


@app.post("/api/videos/{video_id}/claims/lifecycle")
def api_claims_lifecycle_bulk(video_id: str, body: dict):
    target = body.get("lifecycle")
    if target not in {"live", "rejected"}:
        raise HTTPException(400, "invalid lifecycle")
    data = store.load()
    if not any(v["id"] == video_id for v in data["videos"]):
        raise HTTPException(404, "unknown video")
    updated = 0
    for claim in data["claims"]:
        if claim.get("video_id") != video_id:
            continue
        if claim.get("lifecycle") != "proposed":
            continue
        claim["lifecycle"] = target
        updated += 1
    store.save(data)
    return {"video_id": video_id, "lifecycle": target, "updated": updated}


class OqIn(BaseModel):
    event_id: str
    text: str
    kind: str = "other"
    priority: str = "medium"


@app.post("/api/open-questions")
def api_add_oq(body: OqIn):
    data = store.load()
    n = len(data["open_questions"]) + 1
    item = {
        "id": f"OQ-{n:02d}",
        "event_id": body.event_id,
        "kind": body.kind,
        "text": body.text.strip(),
        "priority": body.priority,
        "lifecycle": "open",
    }
    if not item["text"]:
        raise HTTPException(400, "empty question")
    data["open_questions"].append(item)
    store.save(data)
    return item


class VideoIn(BaseModel):
    id: str = Field(min_length=11, max_length=11)
    title: str = "Untitled ingest"
    channel: str = "Unknown"


@app.post("/api/videos")
def api_add_video(body: VideoIn):
    data = store.load()
    if any(v["id"] == body.id for v in data["videos"]):
        return next(v for v in data["videos"] if v["id"] == body.id)
    video = {
        "id": body.id,
        "channel": body.channel,
        "handle": "",
        "title": body.title,
        "published": "",
        "duration_s": 0,
        "asr": "queued",
        "extraction": "pending",
    }
    data["videos"].insert(0, video)
    store.save(data)
    return video


@app.post("/api/reset")
def api_reset():
    return store.reset()
