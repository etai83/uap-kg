# Implementation plan: v1 vertical slice (C2)

**Status:** ready to execute  
**Date:** 2026-07-22  
**Normative law:** [`docs/spec/uap-kg-v1.md`](../spec/uap-kg-v1.md) (`spec-complete`)  
**Pilot list:** [`docs/pilot-corpus.md`](../pilot-corpus.md)  
**Language:** [`CONTEXT.md`](../../CONTEXT.md)

This is a **build plan**, not a model reopen. If the plan conflicts with the spec, **the spec wins**.

---

## 1. Goal

Prove the product job on a **real multi-telling Event**:

> Curator can open one focus Event, see Tellings from ≥2 seed channels, review **live atomic claims** with provenance, **approve** a proposed claim, and **jump to timestamp** on YouTube.

**Not a goal:** full 30-video ingest, graph DB beauty, Topic taxonomy UI, credibility scores, contradiction NLI, multi-user, export.

---

## 2. Success criteria (definition of done)

All must pass on the **C2 slice videos** below:

| # | Criterion | Spec ref |
|---|-----------|----------|
| D1 | Catalog **live** for each slice video (channel, video_id, title, published_at, duration) | §2, §12 catalog exception |
| D2 | For each video: transcript + diarization produce **proposed** processed spans with speaker labels + time spans | §3, §5 |
| D3 | Host/guest **episode maps** proposed; curator can approve host defaults for seed hosts | §9, §12 |
| D4 | AI (or scripted extractor) proposes **atomic claims** with `EXTRACTED_FROM` processed path | §6, §5 |
| D5 | Curator can **batch- or item-approve** processed + claims under a video-scoped approval bundle | §12 |
| D6 | One **focus Event** (C2) exists; ≥2 Tellings link claims via `ABOUT_EVENT` | §7, §13 |
| D7 | Multi-telling compare (minimal UI or CLI + HTML) shows: who, what, when-said, jump-to-timestamp | §13.4–13.5 |
| D8 | Hard rejects enforced: no live claim without Person; no live claim without processed→raw; no auto-live claims | §15.5 |

**Stretch (nice, not required for slice done):** one open contradiction or OQ; same-assertion link across two videos.

---

## 3. Slice scope

### 3.1 Videos in slice (start here)

| ID | Channel | Pilot # | URL | Why |
|----|---------|---------|-----|-----|
| `fZyKcJQZrDA` | Area52 | A3 | https://youtu.be/fZyKcJQZrDA | Lazar long interview — primary Telling |
| `SSeJ2883nF4` | Area52 | A4 | https://youtu.be/SSeJ2883nF4 | Second Lazar Telling on same channel |
| `d9tdJ2SkBKQ` | Jesse Michels | J10 | https://youtu.be/d9tdJ2SkBKQ | Cross-channel Lazar / Area 51 |
| `5hhKLqUbrYQ` | Danny Jones | D1 | https://youtu.be/5hhKLqUbrYQ | Area 51 program context (TD Barnes) |

**Phase-1a (optional shrink if timeboxed):** A3 + J10 only (2 videos, 2 channels) before adding A4 + D1.

**Phase-1b (after D1–D8):** add A2 (`vxumcYKCt-M` Lazar & Travis Walton diner).

**Do not** require full pilot (30) for slice done.

### 3.2 Focus Event (initial)

| Field | v1 working value (curator may refine) |
|-------|----------------------------------------|
| Working name | **Bob Lazar / S4 program claims (1989–public)** |
| Keys | K1: “Bob Lazar S4 / Area 51” discourse · K2: 1989+ public claims window · K3: S4 / Papoose / Area 51 theater · K4: Bob Lazar as principal speaker-participant in tellings |
| Identity note | Spec §7 may force **parent Event** (Lazar public claims) + **child** (specific alleged retrievals) later — start with **one parent**, split only if compare becomes incoherent |
| TD Barnes (D1) | Claims about Area 51 staffing/program may be **related Events** or same parent with facets — curator decides at first review; default: bind Area-51-program claims to a sibling Event *Area 51 industrial program (Barnes)* if keys conflict |

### 3.3 People to seed (manual / defaults)

| Person | Role | Default binding |
|--------|------|-----------------|
| Chris Ramsay | Host | Area52 host default |
| Jesse Michels | Host / guest | Jesse host; guest on A1-style crossovers |
| Danny Jones | Host | Danny host default |
| Bob Lazar | Guest | Map on A3, A4, J10 |
| TD Barnes | Guest | Map on D1 |
| Travis Walton | Guest | Only if A2 ingested |

---

## 4. Architecture (thin)

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐
│ YouTube API │────▶│ catalog raw  │────▶│ live catalog   │
└─────────────┘     └──────────────┘     └────────────────┘
                                                    │
┌─────────────┐     ┌──────────────┐     ┌─────────▼────────┐
│ yt-dlp      │────▶│ audio WAV +  │────▶│ proposed         │
│ bestaudio → │     │ ASR+diarize  │     │ processed spans  │
│ Whisper /   │     │ (pyannote)   │     │                  │
│ pyannote    │     └──────────────┘     └─────────┬────────┘
└─────────────┘                                    │
  see docs/speech-pipeline.md                      │
                      ┌────────────────────────────┤
                      ▼                            ▼
               episode map (prop.)          claim extract (prop.)
                      │                            │
                      └──────────┬─────────────────┘
                                 ▼
                        ┌────────────────┐
                        │ Approval bundle│  curator CLI or simple web
                        │ proposed→live  │
                        └───────┬────────┘
                                ▼
                        ┌────────────────┐
                        │ Event + compare│  minimal multi-telling view
                        └────────────────┘
```

### 4.1 Recommended stack (changeable without reopening ontology)

| Layer | Choice for slice | Rationale |
|-------|------------------|-----------|
| Language | **Python 3.11+** | ASR ecosystem (WhisperX/pyannote); fits research assets |
| Storage | **SQLite** first (or Postgres if you already run it) | Solo tool; migrate later |
| Schema style | Relational tables for entities + edges table | Expresses §14 without Neo4j |
| Catalog | YouTube Data API v3 | Spec §2 |
| ASR/diarize | **yt-dlp bestaudio → 16 kHz WAV → faster-whisper (or WhisperX) + pyannote** local; AssemblyAI only as backup | Spec §3 R; `docs/speech-pipeline.md` |
| Claim proposal | LLM over diarized transcript chunks (provider flexible; SpaceXAI/OpenAI/local) | Propose only → `proposed` |
| UI | **FastAPI + minimal HTML** (or CLI + Jinja) for approval + compare | Spec forbids multi-user chrome; pixels not law |
| Playback | YouTube embed / open URL at `t=` seconds | Spec §2.4 |

### 4.2 Repo layout (suggested)

```
src/uap_kg/
  catalog/          # YouTube metadata fetch + upsert
  speech/           # ASR + diarization jobs
  extract/          # claim proposal from processed
  store/            # schema, repositories
  approve/          # lifecycle transitions + checklists
  compare/          # event multi-telling queries
  web/ or cli/      # thin surfaces
tests/
  unit/             # checklist hard rejects
  integration/      # optional: fixture transcripts (no live YouTube in CI)
docs/plans/         # this file
```

Greenfield: create package when coding starts. No need to invent monorepo complexity.

---

## 5. Data model (minimum tables)

Logical only — names illustrative; must enforce checklists from spec §12.4.

| Table / concept | Key fields |
|-----------------|------------|
| `channel` | youtube_channel_id, handle, title |
| `video` | video_id PK, channel_id, title, published_at, duration_s, lifecycle (catalog live) |
| `extraction_run` | id, tool, model, version, started_at, params_json |
| `raw_track` | video_id, kind, artifact_uri, acquisition_method, run_id |
| `processed_span` | id, video_id, t_start, t_end, text, speaker_label, layer=processed, lifecycle, run_id |
| `person` | id, canonical_name, state |
| `alias` | person_id, type, value |
| `episode_map` | video_id, speaker_label, person_id?, status, method |
| `claim` | id, claim_text, claim_kind, layer=claim, lifecycle, run_id |
| `edge` | predicate, from_id, to_id, edge_kind |
| `event` | id, display_name, keys_json, identity_state |
| `approval_action` | actor, target_id, from_state, to_state, at |

**Enforce in application code (not optional):**

- Claim live ⇒ ≥1 EXTRACTED_FROM live/co-approved processed ⇒ DERIVED_FROM raw path  
- Claim live ⇒ ATTRIBUTED_TO active person + approved episode_map  
- Layer immutable; supersede = new row + SUPERSEDES edge  

---

## 6. Milestones

### M0 — Repo bootstrap (0.5 day)

- [ ] Python project (pyproject/uv/poetry), ruff/pytest, `.env.example`  
- [ ] SQLite schema migration for minimum tables  
- [ ] Seed channels + seed persons (hosts) as data  
- [ ] Load pilot IDs from `docs/pilot-corpus.md` (parse flat list or YAML export)

**Verify:** `pytest` green empty; DB migrates; 3 channels present.

### M1 — Catalog (0.5–1 day)

- [ ] YouTube Data API client (API key in env)  
- [ ] Upsert videos for slice IDs → **live** catalog raw  
- [ ] CLI: `uap catalog fetch --video-id …` / `--slice c2`

**Verify:** D1 — four (or two) videos queryable with stable metadata.

**Blocked by:** Google Cloud API key (curator task).

### M2 — Speech path (1–3 days, env-dependent)

**Locked approach (2026-08-12):** local long-form via yt-dlp audio, not caption scrape.

- [x] Recipe: `yt-dlp -f bestaudio` (+ Node EJS + browser cookies as needed) → ffmpeg **16 kHz mono WAV**  
- [x] Scripts: `scripts/download_audio.py`, `scripts/transcribe_diarize.py`  
- [x] Docs: `docs/speech-pipeline.md`  
- [ ] Install speech extras + `HF_TOKEN` for pyannote  
- [ ] Run download for C2 ids (or phase-1a A3+J10)  
- [ ] Run diarized ASR → `data/transcripts/<id>.spans.json` (**proposed** only)  
- [ ] Wire spans into store as processed + raw_track + extraction_run  

**Verify:** D2 — each slice video has spans with speaker labels + timestamps; jump offsets sane on spot-check.

**Smoke verified:** 20s of `uVVqFg2v7ro` downloaded and converted to WAV. Full multi-hour jobs need disk + time + HF token.

**Fallback:** AssemblyAI or manual captions if yt-dlp/YouTube breaks; still record acquisition_method honestly.

### M3 — Identity maps (0.5–1 day)

- [ ] Seed host defaults → proposed episode_maps  
- [ ] Guest name proposals (title/description heuristic + optional LLM)  
- [ ] Approve CLI: `uap approve episode-map …` / batch by video  

**Verify:** D3 — hosts active; Lazar/Barnes mapped on their videos before claims go live.

### M4 — Claim proposal (1–2 days)

- [ ] Chunk processed by speaker turn  
- [ ] LLM prompt: atomic claims only; refuse compounds; output claim_text + kind + span ids  
- [ ] Write claims as **proposed** with EXTRACTED_FROM + ATTRIBUTED_TO when map known  

**Verify:** D4 — ≥N proposed claims per video (target ≥10/video on long-form; quality > count).  
**Hard reject unit tests:** compound text rejected; claim without EXTRACTED_FROM rejected.

### M5 — Approval workflow (1 day)

- [ ] Video-scoped approval bundle list (proposed processed + maps + claims)  
- [ ] Item approve/reject + batch approve when checklist green  
- [ ] Atomic co-approve path for processed+claim  
- [ ] Record APPROVED_BY + timestamp  

**Verify:** D5 — curator can move a claim to live only when checklist passes; force-fail tests for SPEAKER_n-only live.

### M6 — Event + multi-telling compare (1–2 days)

- [ ] Create focus Event C2; optional sibling for Barnes if needed  
- [ ] Bind live claims `ABOUT_EVENT` (curator or assisted proposal)  
- [ ] Compare view: focus header, telling strip (by video), claims board, provenance jump (`https://youtube.com/watch?v=ID&t=SECs`)  
- [ ] Default filter: **live** claims only  

**Verify:** D6–D8 — open Event, see ≥2 Tellings, approve one claim from UI/CLI, jump opens correct time.

### M7 — Hardening for handoff (0.5–1 day)

- [ ] README: setup, API keys, how to run slice  
- [ ] Fixture transcript test (no network) for claim checklist  
- [ ] Note ASR/legal posture in README (link Appendix A)  
- [ ] Optional: export JSON snapshot of live C2 subgraph for demos  

**Slice complete** when M0–M6 verify + README exists.

---

## 7. Work sequence (critical path)

```
M0 bootstrap
  → M1 catalog (needs YT API key)
  → M2 speech (needs audio/transcript path + compute)
  → M3 maps
  → M4 claims (needs LLM key)
  → M5 approve
  → M6 event/compare
  → M7 docs
```

Parallelizable after M0: catalog schema work while waiting for API keys; unit tests for checklists anytime.

---

## 8. Explicit non-goals (slice)

| Out | When later |
|-----|------------|
| Full 30-video batch | After slice green |
| Contradiction auto-detect / NLI | After multi-telling works |
| Topic taxonomy UI | After compare usable |
| Credibility scores | Forbidden as scores; notes optional later |
| Neo4j / vector DB | Only if SQLite proves painful |
| Auto-live anything extraction-derived | Never |
| Multi-user auth | Never for v1 personal tool |
| Local media archive product | Prefer YouTube playback |

---

## 9. Risks and mitigations

| Risk | Mitigation |
|------|------------|
| YouTube ToS / audio download | Prefer captions/manual for slice; document personal-use ASR; no redistributed audio product | 
| Long-form diarization quality | Human approve maps; prefer false-reject; 2-speaker interviews first (A3, J10) |
| LLM invents claims not in transcript | Require span ids; show quote in review; reject if span text doesn’t support claim_text |
| Event identity ambiguity (Lazar vs Barnes) | Start one parent; split with curator note; provisional links if needed |
| GPU / WhisperX setup time | AssemblyAI or caption-first path for M2 |
| Scope creep to full pilot | Gate “30-video ingest” behind slice DoD |

---

## 10. Curator checklist (before coding day 1)

- [ ] YouTube Data API key (Google Cloud project)  
- [ ] Decision: **local WhisperX** vs **AssemblyAI** vs **caption-first** for M2  
- [ ] LLM API key for claim proposal (or defer M4 to manual claim entry for ultra-thin path)  
- [ ] Machine: enough disk/RAM for 2–4 long-form jobs  
- [ ] Confirm C2 Event naming (or accept working name in §3.2)

**Ultra-thin fallback** (if keys delayed): M1 with mock catalog JSON from oembed; M2 with hand-pasted transcript for **one** video; M4 manual claim entry — still validates approval + compare.

---

## 11. Test plan (minimum)

| Test | Type |
|------|------|
| Live claim without processed path → reject | unit |
| Live claim with only SPEAKER_n → reject | unit |
| Layer rewrite in place → reject | unit |
| Approve processed without DERIVED_FROM → reject | unit |
| Bundle batch only approves checklist-green nodes | unit/integration |
| Jump URL uses processed t_start, not Event year | unit |
| Fixture: 2 fake Tellings same Event → compare lists both | integration |

---

## 12. Estimation

| Path | Calendar (solo, part-time-ish) |
|------|--------------------------------|
| Happy path (keys ready, hosted STT) | **~1–2 weeks** |
| Local WhisperX + GPU friction | **~2–3 weeks** |
| Ultra-thin (1 video, manual claims) | **2–4 days** to learn approval+compare |

---

## 13. Next after slice green

1. Ingest remaining C2 videos (A2) then C1 disclosure cluster.  
2. Expand to full pilot 30 with batch catalog + speech queue.  
3. Add open questions + contradiction records (spec §11).  
4. Dual spine: Event timeline list of all Events.  
5. Only then: Topics, credibility notes, storage upgrade.

---

## 14. Execution entry points

When starting implementation, preferred order of agent sessions:

1. **M0+M1** — project + catalog for C2 IDs  
2. **M2+M3** — speech + maps for A3 + J10  
3. **M4+M5** — claims + approval  
4. **M6+M7** — Event compare + README  

Invoke with: *“Execute M0–M1 of docs/plans/v1-vertical-slice.md”* (or whole plan if autonomous).

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-22 | Initial vertical-slice plan for C2 (Lazar / Area 51) |
