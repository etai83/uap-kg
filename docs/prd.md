# Product requirements: uap-kg v1

| Field | Value |
|-------|--------|
| **Product** | uap-kg — personal UAP/NHI research knowledge graph |
| **Version** | 1.0 |
| **Status** | Requirements locked (model + IA). Product **not** built. |
| **Owner** | Sole **curator** (personal research tool) |
| **Date** | 2026-08-14 |
| **Normative model** | [`docs/spec/uap-kg-v1.md`](spec/uap-kg-v1.md) (`spec-complete`) |
| **Glossary** | [`CONTEXT.md`](../CONTEXT.md) |

This PRD states **what the product must do for the curator** and **how we know v1 is done**.  
Write-path legality, ontology, and identity rules live in the spec. **If this file and the spec conflict, the spec wins.**

---

## 1. Problem

UAP / NHI / disclosure discourse is split across long-form YouTube interviews. The same real-world happening is told many times, by different speakers, with overlapping and contradictory assertions.

Today the curator’s workflow is linear media: watch, remember, search transcripts by keyword, keep notes outside the source. That fails at the actual job:

- **Who said what**, on which video, at which second?
- Are two tellings about the **same Event** or different ones?
- Which statements **agree**, **conflict**, or leave **gaps**?
- What is **recorded speech** vs **our inference** vs an **assumption** we smuggled in?

Without typed claims and provenance, cross-checking becomes vibes. With un-gated AI extraction, the graph becomes untrustworthy fiction.

---

## 2. Job to be done

> As the sole curator, I need to **reconstruct and cross-check the story** of real-world happenings across a small, fixed set of YouTube channels — with hard epistemic types and a path back to the source — so I can compare tellings without losing who said what or inventing “facts.”

**UX spine (product, not pixels):**

1. **Event timeline** — chronological index of world Events (by Event time window, not upload date).  
2. **Multi-telling compare** — line up Tellings of one focus Event (or an explicit provisional identity bundle).

---

## 3. User

| Role | Who | Authority |
|------|-----|-----------|
| **Curator** | The only user. You. | Names channels and pilot videos; is the **only** path from `proposed` → `live` for extractions, person maps, Event merges, and research objects. |

There are no other roles. No accounts, no collaboration, no public audience.

---

## 4. Goals and non-goals

### 4.1 Goals (v1)

| ID | Goal |
|----|------|
| G1 | Ingest a **fixed seed** of English YouTube channels and a **human-chosen** pilot corpus. |
| G2 | Turn long-form video into **proposed** processed speech (who spoke when + text + time) with provenance. |
| G3 | Extract **atomic claims** a speaker actually made; never auto-publish them as live. |
| G4 | Bind claims to **Persons** and (when keys exist) **Events**. |
| G5 | Let the curator **approve / reject / supersede** in a video-scoped review bundle. |
| G6 | Compare ≥2 Tellings of the same Event: who / what / when-said / agreement / conflict / gaps / jump to timestamp. |
| G7 | Keep **assumption** and **inference** from masquerading as **claim**. |

### 4.2 Non-goals (v1)

| Not this product |
|------------------|
| Public multi-user app, accounts, RBAC, collaboration |
| Open YouTube scrape / keyword harvest |
| Auto-live AI claims or “the system believes this is true” |
| Composite trust / reputation scores |
| Standing local AV archive as the product |
| Multi-language or non-YouTube sources |
| Publish / export product (deferred) |
| Pixel-perfect design system |

---

## 5. Scope

### 5.1 Sources

| Item | Requirement |
|------|-------------|
| Channels | Exactly **3** until a later expansion: [Jesse Michels](https://www.youtube.com/@JesseMichels), [Area52](https://www.youtube.com/@Area52Investigations), [Danny Jones](https://www.youtube.com/@dannyjones) |
| Medium | YouTube only (episode = YouTube video) |
| Language | English only |
| Pilot | **30 videos** (10 per channel), curator-selected — [`docs/pilot-corpus.md`](pilot-corpus.md) |
| First build slice | C2 cluster (Lazar / Area 51) is the implementation proving ground — [`docs/plans/v1-vertical-slice.md`](plans/v1-vertical-slice.md) |

### 5.2 In vs out (product)

| In | Out |
|----|-----|
| Catalog metadata (YouTube Data API) | Bulk third-party caption scrape as standing architecture |
| Personal local ASR + diarization (yt-dlp audio → MLX Whisper + pyannote) | Claiming a ToS-cleared commercial ingest product |
| Layered graph: raw → processed → claim → inference → assumption | Soft untyped “notes as facts” |
| Person nodes + episode maps | Treating `SPEAKER_00` as identity |
| Events (happenings) vs Topics (themes) | Mega-Events from themes; topic-as-compare-scope |
| Qualitative credibility notes | Numeric trust scores |
| Contradiction records + open questions | Auto truth verdicts / winner collapse |

---

## 6. Primary user journeys

### J1 — Ingest a video

1. Curator (or pipeline) catalogs the video → catalog **live**.  
2. Audio is obtained (yt-dlp bestaudio) and transcribed + diarized locally.  
3. Processed spans land as **`proposed`**.  
4. Host/guest episode maps proposed (seed hosts get strong defaults, still gated).  
5. Claim extractor proposes **atomic** claims with `EXTRACTED_FROM` spans.  
6. Curator reviews a **video-scoped approval bundle** and promotes checklist-green nodes to **live**.

### J2 — Compare tellings of one Event

1. Curator opens a **focus Event** (or provisional identity bundle).  
2. Sees Tellings by channel/video, live claims on a board.  
3. Reads who / what / when-said; jumps to YouTube at the span.  
4. Surfaces agreement, conflict, and gaps (open questions).  
5. Can approve a proposed claim, mark an OQ, or bind a claim to the Event — without bypassing live gates.

### J3 — Correct after live

1. Curator does not patch live semantics in place.  
2. New same-layer node + `SUPERSEDES`; old becomes `superseded`.  
3. Default views follow the successor; history remains walkable.

---

## 7. Functional requirements

Priority: **P0** = v1 must ship for “product usable on pilot slice”; **P1** = v1 complete on full pilot; **P2** = after v1 or optional.

### 7.1 Catalog and intake — P0

| ID | Requirement |
|----|-------------|
| F-CAT-1 | Persist stable YouTube `channel_id` / `video_id`, title, `published_at`, duration. |
| F-CAT-2 | Catalog raw **may auto-land live** (inventory, not narrative). |
| F-CAT-3 | Playback is YouTube embed / open URL — product must not require a local media archive. |
| F-CAT-4 | Speech path records `acquisition_method` honestly (`personal_asr`, etc.). |

### 7.2 Speech → processed — P0

| ID | Requirement |
|----|-------------|
| F-SP-1 | Produce processed spans: text, `speaker_label`, `[t_start, t_end)`. |
| F-SP-2 | All extraction-derived processed nodes start **`proposed`**. |
| F-SP-3 | Default local stack: yt-dlp bestaudio → 16 kHz WAV → [audio_transcriber](https://github.com/razamit/audio_transcriber) (MLX Whisper + pyannote). |
| F-SP-4 | `SPEAKER_n` is episode-local only — never a Person. |

### 7.3 Identity — P0

| ID | Requirement |
|----|-------------|
| F-ID-1 | Seed hosts (Jesse Michels, Chris Ramsay, Danny Jones) get provisional channel–host defaults; first live map still curator-confirmed. |
| F-ID-2 | Guests: proposals from titles/credits/LLM; live map always gated. |
| F-ID-3 | No live claim attributed only to `SPEAKER_n`. |
| F-ID-4 | No `Unknown Person N` nodes; unresolved stays episode-local. |
| F-ID-5 | Live person merge requires multi-signal evidence + curator; never string-only. |

### 7.4 Claims and layers — P0

| ID | Requirement |
|----|-------------|
| F-CL-1 | Live claim = one atomic proposition the speaker **said**; recording ≠ truth verdict. |
| F-CL-2 | Live claim requires `EXTRACTED_FROM` processed → raw (video + time) + `ATTRIBUTED_TO` active Person + `APPROVED_BY`. |
| F-CL-3 | Split compounds before live. |
| F-CL-4 | Two videos → two claim nodes; optional `SAME_ASSERTION_AS`. |
| F-CL-5 | Prefer `ABOUT_EVENT`; **unbound** allowed — do not invent Events. |
| F-CL-6 | Hard reject: assumption/inference as claim; claim→raw with no processed path; auto-live claims. |

### 7.5 Events and topics — P0 / P1

| ID | Requirement | Pri |
|----|-------------|-----|
| F-EV-1 | Event = real-world happening, not a video beat. | P0 |
| F-EV-2 | Identity keys: name, time window, place, actors/platforms, optional docs. | P0 |
| F-EV-3 | Uncertain sameness → provisional link + identity OQ; no silent high-stakes merge. | P0 |
| F-EV-4 | Topics = thematic types (small controlled list); never Event identity keys; filter-only in compare. | P1 |

### 7.6 Approval — P0

| ID | Requirement |
|----|-------------|
| F-AP-1 | Lifecycle: `proposed` \| `live` \| `rejected` \| `superseded` (orthogonal to layer). |
| F-AP-2 | Only curator sets `live` on gated objects. |
| F-AP-3 | Default review unit = **video-scoped approval bundle**; batch OK if each node is checklist-green. |
| F-AP-4 | Corrections via supersession, not in-place rewrite. |

### 7.7 Multi-telling UX — P0 (IA), pixels P2

| ID | Requirement |
|----|-------------|
| F-UX-1 | Dual spine: Event timeline + multi-telling compare. |
| F-UX-2 | Compare scoped to one focus Event or explicit provisional bundle — never “everything under Topic X.” |
| F-UX-3 | Default evidence = **live** claims only. |
| F-UX-4 | Dimensions: who, what, when-said, about, agreement, conflict, gaps, provenance. |
| F-UX-5 | Minimum actions: **approve claim**, **mark open question**, **jump to timestamp** (disabled if grounding incomplete). |
| F-UX-6 | Assumptions never appear as evidence/conflict rows. |

### 7.8 Research objects — P1

| ID | Requirement |
|----|-------------|
| F-RS-1 | First-class contradiction records + open questions (kinds include identity, conflict, coverage gap). |
| F-RS-2 | AI proposes; curator opens / resolves / wontfix. |
| F-RS-3 | Resolve does not collapse winning claims or mint truth flags. |
| F-RS-4 | Credibility = optional notes + role labels + person×event consistency — **no scores**. |

---

## 8. Success criteria

### 8.1 Product-complete (v1)

The curator can, on the **pilot corpus** (or at least the C2 slice for an interim milestone):

1. Catalog and process videos without auto-live narrative.  
2. Approve a claim and jump to the correct YouTube second.  
3. Open one Event and see ≥2 Tellings from different seed channels.  
4. Distinguish claim vs inference vs assumption in the UI.  
5. Correct a live claim via supersession.  
6. Never see a live claim that fails the spec checklists.

### 8.2 Vertical-slice milestone (now)

Matches [`docs/plans/v1-vertical-slice.md`](plans/v1-vertical-slice.md) D1–D8: C2 videos (Lazar / Area 51) through approve + compare. **This is the next ship target.** Full 30-video ingest is **not** required for slice done.

### 8.3 What we do not measure

No DAU, no viral growth, no “accuracy %” as a published score. Honesty of provenance beats coverage.

---

## 9. Constraints and risks

| Constraint / risk | Product implication |
|-------------------|---------------------|
| Personal ASR on third-party audio | Allowed as personal research path; do **not** market as ToS-cleared; do not redistribute audio (`data/` is local). |
| YouTube download fragility (SABR / cookies / JS challenges) | yt-dlp recipe documented; fallback is captions or hosted STT — still record method. |
| Long-form (2–3h) diarization | Jobs may take tens of minutes; UI/CLI must show job status; no silent failure. |
| Apple Silicon MLX stack | Current ASR tool is Mac-only; that is acceptable for v1 personal use. |
| LLM claim extraction | Proposals only; span-grounded; curator gate. |
| Solo curator time | Batch approve for clean 2-speaker interviews; item review for messy panels. |

---

## 10. Current product state (2026-08-14)

| Area | State |
|------|--------|
| Model / IA / glossary | **Done** — spec-complete, wayfinder map closed |
| Pilot list | **30 / 30 confirmed** |
| Audio download | **Working** (`scripts/download_audio.py`) |
| Transcribe + diarize | **Working on short clips**; long jobs need a reliable runner + viewer |
| Graph store / approval UI / Event compare UI | **Not built** |
| Transcript viewer | **None** (text/JSON files only) |

---

## 11. Release shape

| Release | Ships when |
|---------|------------|
| **Slice** | C2: catalog + speech + maps + proposed claims + approve + Event compare (minimal UI or CLI+HTML) |
| **v1** | Slice + remaining P1 on pilot (topics filter, OQs/contradictions, full 30 ingest path) |
| **Later** | Channel expansion, refresh cadence, export, storage upgrade — only after v1 |

---

## 12. Document map

| Need | Read |
|------|------|
| This PRD (product *what* / *why*) | `docs/prd.md` |
| Implementer law | [`docs/spec/uap-kg-v1.md`](spec/uap-kg-v1.md) |
| Terms | [`CONTEXT.md`](../CONTEXT.md) |
| Decision detail | [`docs/research/`](research/) |
| Pilot videos | [`docs/pilot-corpus.md`](pilot-corpus.md) |
| Next build plan | [`docs/plans/v1-vertical-slice.md`](plans/v1-vertical-slice.md) |
| Speech how-to | [`docs/speech-pipeline.md`](speech-pipeline.md) |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-08-14 | Initial PRD assembled from locked spec, pilot, and current pipeline state. |
