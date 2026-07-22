# Provenance minimum

Decision asset for [Provenance minimum](https://github.com/etai83/uap-kg/issues/7)  
Part of [Wayfinder: UAP YouTube knowledge graph spec](https://github.com/etai83/uap-kg/issues/1)

**Depends on:** [Epistemic layer ontology](./epistemic-layer-ontology.md) (#3)  
**Related:** [YouTube ingestion options](./youtube-ingestion-options.md) (#12), [Speaker diarization options](./speaker-diarization-options.md) (#13), [Speaker identity and alias merge](./speaker-identity-and-alias-merge.md) (#5), [Event identity rule](./event-identity-rule.md) (#4)  
**Status:** Recommended decision (batch defaults; personal solo tool — honest minimum, not enterprise audit theater).  
**Scope:** Spec-level **required vs optional** provenance fields and legal chains back to source media. No storage schema or API.

**Downstream consumers:** Claim model (#6), Human approval workflow (#9), Contradiction model (#8), Multi-telling compare UX (#14).

---

## Question

What is the **minimum provenance** every non-raw object must carry back to source media?

Decide: required fields (channel, video id, timestamp span, speaker, quote/transcript span, extraction run id), and what is optional for v1.

---

## Decision summary

| Axis | Decision |
|------|----------|
| Core rule | Every **live** non-raw layered node must have a **complete legal provenance path** to its supports (per #3 matrices). For speech-grounded nodes, that path **must reach raw media anchors**. |
| Media anchor unit | **Video** (YouTube `video_id`) is the primary media object; **channel** is required on the catalog video (inherited), not re-copied on every claim. |
| Required for speech path | `video_id` + **timestamp span** + **transcript/quote span** + **speaker label** (or explicit unresolved) + **extraction run id** on the write that created the node |
| Person speaker | **Optional** on processed/claim until episode attribution is approved; live claim attribution to a Person still requires confirmed mapping (#5) |
| Inference / assumption | **No direct media fields required**; they chain via `BASED_ON` / `RESTS_ON` to claims (and claims to media). Still require **extraction/reasoning run identity** and actor provenance |
| Catalog raw exception | **Honored:** official catalog raw (channel, video identity, public metadata snapshot) may be live without claim-level approval and without extraction-run ceremony |
| Tool / model | **Required on extraction runs** (not duplicated as free-form blobs on every node); nodes **reference** the run |
| Honesty bar | Minimum is what a solo curator needs to **re-open the video at the right time, see who was labeled speaking, re-run or distrust a pipeline, and explain why a node exists** — not SOC2-grade field bloat |

---

## Core principle

> **Provenance answers: why does this node exist, and how do I get back to the bytes/time of the source?**  
> Edges establish **legal dependency** (`DERIVED_FROM`, `EXTRACTED_FROM`, `BASED_ON`, …).  
> Fields establish **locators and process identity** (which video, which seconds, which run, which tool).

Standing contracts from [epistemic-layer-ontology.md](./epistemic-layer-ontology.md):

- Provenance arrows: **dependent → support**.
- Live claim requires ≥1 `EXTRACTED_FROM` → `processed`, and that processed has a path to `raw`.
- `GROUNDED_IN` claim→raw is optional sugar **only if** the processed path also exists.
- Catalog raw may enter live without extraction gates; interpretive/extraction-derived material does not.
- This ticket **adds required fields**; it does **not** loosen layer matrices or invent silent promotions.

---

## Objects in scope

| Object class | In “every non-raw object”? | Media-back requirement |
|--------------|----------------------------|-------------------------|
| `processed` (utterance, span, segment, diarized turn mapping payload) | Yes | **Direct** media anchors |
| `claim` | Yes | **Via** processed (and thus raw); optional denormalized locators |
| `inference` | Yes | **Via** claims (transitive media path); no direct timestamp required |
| `assumption` | Yes | **No** source-media requirement (by definition has no asserting quote); process + rationale required |
| Entity nodes (Person, Channel, Video catalog, Event) | Outside five-layer spine | Not “non-raw epistemic objects”; entities use their own identity evidence (#4, #5). Videos **are** the media anchors others point at |
| Catalog `raw` | Raw | **Is** the anchor; minimum fields defined below for completeness |
| Interpretive / track `raw` (caption ref, ASR track ref, diarization job ref) | Raw | Locators + process identity; mechanical catalog-linked refs may skip claim gate per #3 |

---

## Media anchors (raw)

### Catalog raw (channel / video identity)

**May be live without claim-level approval** (catalog exception).

| Field | Required v1? | Notes |
|-------|:------------:|-------|
| `channel_id` (YouTube) | **Yes** | On Channel entity / catalog channel record |
| Channel URL or handle | **Yes** (at least one durable locator) | Prefer stable `channel_id` as key; handle for display |
| `video_id` (YouTube) | **Yes** | On Video catalog object |
| Canonical watch URL | Optional | Derivable from `video_id` |
| `published_at`, title, duration | **Yes** for useful catalog | From Data API; refresh policy per ingestion research |
| Caption-available flag | Optional | Useful pipeline signal |
| Stats (views, likes) | Optional / cache | Volatile; ≤30-day API-data discipline if stored as API Data |

**No** extraction run id required for pure official-API catalog ingest.

### Media-track raw (transcript / ASR / caption / diarization anchors)

These are raw **anchors** tied to a catalog video. They do not assert world-truth.

| Field | Required v1? | Notes |
|-------|:------------:|-------|
| `video_id` | **Yes** | Parent media |
| Track kind | **Yes** | e.g. `caption_manual`, `caption_auto`, `asr`, `diarization_turns`, `human_notes` |
| Track / artifact ref | **Yes** | Pointer to stored bytes, URI, or content hash the pipeline can resolve |
| Time base | **Yes** if timed | Seconds (float) preferred; document if ms |
| Source acquisition method | **Yes** (coarse) | e.g. `owner_export`, `studio_download`, `manual_transcript_ui`, `personal_asr`, `api_metadata_only` — honesty for ToS/risk, not legal advice |
| Extraction / ingest run id | **Yes** for ASR/diarization/caption **processing** jobs | Not for empty “metadata-only” catalog rows |
| Tool / model (via run) | **Yes** when run exists | Whisper / pyannote / vendor id + version |

---

## Extraction run (process identity)

An **extraction run** is the first-class record of “this pipeline invocation produced these nodes.”

### Required on every extraction run (v1)

| Field | Required | Example |
|-------|:--------:|---------|
| `extraction_run_id` | **Yes** | UUID |
| `started_at` (UTC) | **Yes** | ISO-8601 |
| `run_kind` | **Yes** | `asr`, `diarize`, `span_normalize`, `claim_extract`, `inference_propose`, `speaker_map_propose`, `manual_curator_edit` |
| `tool_name` | **Yes** | `whisperx`, `pyannote`, `llm-claim-extract`, `curator-ui` |
| `tool_version` or image digest | **Yes** when known; else `unknown` + note | Pin when possible |
| `model_id` | **Yes** when a model was used; else null | `large-v3`, vendor model name |
| `model_params` (coarse) | Optional | temperature, diarization min/max speakers |
| `input_video_ids[]` | **Yes** when media-scoped | Usually one video per run for v1 |
| `input_artifact_refs[]` | Optional | Prior run outputs consumed |
| `agent` / `PROPOSED_BY` target | **Yes** | system id or `curator` |
| `completed_at`, status | Optional but recommended | success / partial / failed |

### Node → run linkage

| Rule | Detail |
|------|--------|
| Non-catalog writes | Every `processed`, `claim`, `inference`, `assumption` created by a pipeline or AI pass **must** reference `extraction_run_id` of the run that wrote it (or a `manual_curator_edit` run) |
| Curator typed nodes | Still get a run (or equivalent audit stamp): who, when, that it was human-authored |
| Supersession | New node + `SUPERSEDES` + new run; do not rewrite old run history |
| Reprocessing | New run, new processed nodes (or explicit supersession). Diarization label IDs are **not** stable across runs (#5) |

**v1 stance:** Put tool/model/version **on the run**, not copied onto every claim field. Nodes only need `extraction_run_id` (+ edges).

---

## Required provenance by layer

### 1. Processed (direct media grounding)

**Legal edge:** ≥1 `DERIVED_FROM` → raw (track and/or catalog video anchor as defined in write path).

| Field / link | Required live v1? | Notes |
|--------------|:-----------------:|-------|
| `video_id` | **Yes** | Must match raw support |
| `channel_id` | Optional denorm | Prefer inherit from Video catalog; do not require re-entry |
| Timestamp span `[t_start, t_end)` | **Yes** | Seconds on video timeline; zero-width forbidden for speech spans that ground claims |
| Transcript / quote span text | **Yes** | Exact (or pipeline-normalized) text of the span |
| Char/token offsets into track | Optional | Nice for re-align; not required if full span text + times are stored |
| `speaker_label` | **Yes** | Episode-local (`SPEAKER_00`, …) **or** explicit `unresolved` / `non_speech` |
| `person_id` | Optional | Only after approved episode attribution (#5); null allowed |
| Attribution method / confidence | Optional on node; **required on episode-mapping record** when mapped | Keep diarization ≠ identity scores separate (#5, #13) |
| `extraction_run_id` | **Yes** | |
| `PROPOSED_BY` | **Yes** (edge or field) | |
| `APPROVED_BY` | **Yes** to become **live** | Curator |

**Hard reject:** live processed speech span with no `video_id`, no time range, or no text; or missing `DERIVED_FROM` raw path.

### 2. Claim (via processed)

**Legal edges:** ≥1 `EXTRACTED_FROM` → `processed`. Optional `GROUNDED_IN` → raw only if processed path exists. Content: `ATTRIBUTED_TO` Person when attributed.

| Field / link | Required live v1? | Notes |
|--------------|:-----------------:|-------|
| `EXTRACTED_FROM` processed | **Yes** (≥1) | Primary grounding |
| Transitive media path | **Yes** (validated) | processed → raw must resolve |
| Denormalized `video_id` | **Recommended**, not strictly required if always joinable | Helps multi-telling UX; treat as cache of support |
| Denormalized timestamp span | **Recommended** | Union or primary span of supports |
| Denormalized quote | **Recommended** | Primary supporting quote for UI |
| Speaker label (via processed) | **Yes** (on support) | Claim need not duplicate if edge is mandatory |
| `ATTRIBUTED_TO` Person | Required for **attributed** live claims | Unattributed claims only if product allows “unresolved speaker claims” — default: claims that assert a speaker said X need approved person **or** explicit unresolved policy on the claim |
| `extraction_run_id` | **Yes** | Claim-extraction run (may differ from ASR run) |
| `PROPOSED_BY` / `APPROVED_BY` | **Yes** for live | Per #3 |

**Hard reject:** live claim with no `EXTRACTED_FROM` processed; claim→raw only; empty extraction; assumption/inference masquerade.

**Default attribution policy (v1):** A live claim that represents **speech content** should carry approved `ATTRIBUTED_TO` Person when the supporting processed span has an approved episode mapping; if the span is unresolved, the claim may stay proposed or live as **speaker-unresolved** only if the UI badges that clearly — prefer not to promote unresolved-speaker claims as first-class multi-telling units.

### 3. Inference (via claims)

**Legal edges:** ≥1 `BASED_ON` → live (or co-approved) `claim`; optional further `BASED_ON` inference; optional `RESTS_ON` assumption. **No** requirement for direct `video_id` / timestamps.

| Field / link | Required live v1? | Notes |
|--------------|:-----------------:|-------|
| `BASED_ON` claim(s) | **Yes** (≥1 claim) | Per #3 live rule |
| Rationale / reasoning text | **Yes** | Why this conclusion is not itself a quote |
| `extraction_run_id` or manual run | **Yes** | |
| `PROPOSED_BY` / `APPROVED_BY` | **Yes** for live | |
| Direct media fields | **No** | Recover media by walking claim → processed → raw |
| Optional “focal video” | Optional | UX hint only |

**Hard reject:** live inference with only assumptions, only other proposed claims, or no rationale.

### 4. Assumption (scaffolding, not media)

**Legal edges:** typically targeted by `RESTS_ON` from inference (or rare claim). Assumptions are **not** extracted quotes.

| Field / link | Required live v1? | Notes |
|--------------|:-----------------:|-------|
| Statement text | **Yes** | What is being assumed |
| Why introduced / context note | **Yes** | e.g. “co-ref place name across two videos” |
| `extraction_run_id` or manual run | **Yes** | |
| `PROPOSED_BY` / `APPROVED_BY` | **Yes** for live | |
| Media anchors | **No** | Optional `inspired_by` video/claim links are optional, non-grounding |
| `EXTRACTED_FROM` | **Forbidden** as fake grounding | If a speaker said it, it is a claim, not an assumption |

---

## Field checklist (ticket’s named list)

| Candidate field | Processed | Claim | Inference | Assumption | Catalog raw |
|-----------------|:---------:|:-----:|:---------:|:----------:|:-----------:|
| **Channel** | inherit | inherit | n/a | n/a | **required** |
| **Video id** | **required** | via path (**recommend** denorm) | via claims | n/a | **required** |
| **Timestamp span** | **required** | via path (**recommend** denorm) | no | no | n/a (whole video) |
| **Speaker** (label) | **required** | via processed | no | no | n/a |
| **Speaker** (Person) | optional until map approved | required for attributed live claims | no | no | n/a |
| **Quote / transcript span** | **required** | via `EXTRACTED_FROM` (**recommend** denorm) | no (use rationale) | no (use statement) | n/a |
| **Extraction run id** | **required** | **required** | **required** | **required** | **no** for pure API catalog; **yes** for track processing |

---

## Speaker attribution provenance

Aligns with #5 / #13; provenance minimum **records** attribution process, does not redefine identity gates.

| Record | Required when | Fields (minimum) |
|--------|---------------|------------------|
| Episode mapping | Any live claim uses `ATTRIBUTED_TO` Person from a diarized span | `video_id`, `speaker_label`, `person_id`, `review_status=approved`, `attribution_method`, evidence pointers, `approved_by`, time |
| Mapping proposal | AI/system proposes map | Same + `extraction_run_id`, confidence band, method (`metadata`, `llm`, `voiceprint`, `host_default`, …) |
| Unresolved | No person | `person_id` null; do not mint person; spans still keep `speaker_label` |

**Never** treat diarization confidence as person-identity provenance sufficiency.

---

## Minimum chain diagrams

### Speech claim (normative happy path)

```text
Claim C (live)
  EXTRACTED_FROM → Processed utterance U
                      DERIVED_FROM → Raw track T (ASR/caption + times)
                      DERIVED_FROM → Raw catalog Video V (video_id)
  ATTRIBUTED_TO  → Person P   (only if episode map approved)
  PROPOSED_BY    → Agent/System
  APPROVED_BY    → Curator
  extraction_run_id → Run_claim (tool/model)
U.extraction_run_id → Run_asr_diarize (tool/model)
V.channel_id → Channel (catalog)
```

### Inference resting on a gap

```text
Inference I (live)
  BASED_ON  → Claim C1, Claim C2   (each fully grounded as above)
  RESTS_ON  → Assumption A
  rationale → "…"
  extraction_run_id → Run_infer
A has statement + why-introduced + run/approvals; A has no EXTRACTED_FROM
```

### Illegal shortcuts (hard reject)

```text
Claim ──GROUNDED_IN──► Raw video          # missing processed path
Claim ──EXTRACTED_FROM──► (nothing)
Inference ──BASED_ON──► Assumption only
Processed speech without [t_start,t_end) or text
Assumption labeled as Claim with a fabricated quote
```

---

## Optional for v1 (explicit non-requirements)

Do **not** block v1 live writes on these:

| Optional | Why deferred |
|----------|----------------|
| Full model hyperparameter dumps | Coarse model id + tool version is enough for personal re-run |
| Cryptographic content hashing of every span | Nice for integrity; not required for research UX |
| Multi-hop `GROUNDED_IN` edges | Optional sugar when denormalized locators exist |
| Char-level offsets into caption files | Times + text sufficient for jump-to-video |
| Word-level confidence arrays | Useful later for quality UI |
| Full agent chain-of-thought logs | Rationale field on inference is enough |
| External DOI / bibliographic citation objects | YouTube-first product |
| Cross-system W3C PROV-O export | Out of scope |
| Per-field data-classification labels | Solo tool |
| Channel id duplicated on every claim | Inherit from video |
| Numeric credibility scores on provenance | Ticket #10 |

---

## Catalog raw exception (restated)

| May enter **live** without claim-level approval | Still gated |
|-------------------------------------------------|------------|
| Channel catalog identity | Processed utterances |
| Video catalog identity + official metadata snapshot | Claims, inferences, assumptions |
| Mechanical raw track refs that only point at acquired artifacts **without** interpretive structure | Person create / merge / episode map |
| | Any node that asserts speech structure or world content |

Refreshing API metadata does not create extraction provenance for claims; it only updates catalog raw.

---

## Validation rules (write path, conceptual)

1. **Layer matrix first** — reject illegal predicates/endpoints (#3).  
2. **Path completeness** — for live `claim`, verify `EXTRACTED_FROM` processed and processed `DERIVED_FROM` raw with resolvable `video_id` + time span + text.  
3. **Run presence** — non-catalog layered creates require `extraction_run_id` resolving to a run with tool (and model if applicable).  
4. **Speaker** — processed speech requires `speaker_label` or explicit unresolved marker.  
5. **Person** — live `ATTRIBUTED_TO` requires approved episode mapping for that video+label (or curator-direct attribution evidence recorded).  
6. **Inference** — ≥1 live/co-approved claim premise + non-empty rationale.  
7. **Assumption** — no fake `EXTRACTED_FROM`; statement + why-introduced required.  
8. **Immutability** — do not patch away provenance; supersede with new nodes/runs.

---

## Worked examples

### A — Guest claim (Danny Jones style)

1. Catalog raw Video `5hhKLqUbrYQ` live via API (`channel_id`, title, …).  
2. Run `R1` (WhisperX+pyannote): raw ASR track + diarization turns.  
3. Processed U1: `video_id`, t=01:12:40–01:12:55, text *“There were 23 of us…”*, `speaker_label=SPEAKER_01`, `DERIVED_FROM` track+video, `extraction_run_id=R1`.  
4. Episode map approved: `SPEAKER_01` → Person TD Barnes.  
5. Run `R2` (claim extract): Claim C1 `EXTRACTED_FROM` U1, denorm quote+times optional, `ATTRIBUTED_TO` TD Barnes, proposed → curator `APPROVED_BY` → live.  
**Minimum satisfied.**

### B — Inference without new timestamps

Live C1, C2 grounded as above. Inference I1 `BASED_ON` C1,C2; rationale string; run `R3`; curator approve.  
**No** new video timestamp on I1; multi-telling UI walks supports for media.

### C — Assumption

A1: *“‘the ranch’ in video A co-refers to Skinwalker Ranch as named in video B.”*  
Why: cross-video synthesis scaffolding. Run + approve.  
**No** quote span required; if later a speaker explicitly asserts the co-ref, mint a **claim** from that span instead of promoting A1.

### D — Catalog-only video (no transcript yet)

Video catalog live. No processed/claims.  
**Valid.** Provenance minimum for non-raw objects does not apply until extractions exist.

---

## Downstream contracts

### Claim model (#6) may assume

- Live claims always have `EXTRACTED_FROM` processed with media-complete path.
- `extraction_run_id` on claim create.
- Denormalized video/time/quote are recommended caches, not substitutes for edges.
- Attribution provenance lives on episode mapping + `ATTRIBUTED_TO`.

### Human approval (#9) may assume

- Approval records `APPROVED_BY` + timestamp; does not strip run identity.
- Review UI can jump via processed (or denorm) `video_id` + timestamp span + quote.
- Bulk approve still requires each node to pass path validation when flipped live.

### Multi-telling / contradiction (#8, #14) may assume

- Compare units can always resolve **which video and when** for claims via provenance path.
- Inferences show badge + expandable support tree to media.
- Assumptions never appear as media-grounded evidence.

---

## What this intentionally does not decide

- Graph DB property names / indexes.  
- Exact review UI layout.  
- Numeric confidence calibration.  
- Whether denormalized locators are stored vs always joined (recommend store for UX).  
- Legal permissibility of a given acquisition method (ingestion research only flags posture).  
- Claim schema polarity/modality (#6).  

---

## Policy cheat-sheet

```
Non-raw live node?
  → Legal provenance edges for its layer (#3)
  → extraction_run_id (tool/model on the run)

Processed speech?
  → video_id + [t_start,t_end) + quote text + speaker_label|unresolved
  → DERIVED_FROM raw

Claim?
  → EXTRACTED_FROM processed (path to raw must resolve)
  → no claim→raw-only shortcut

Inference?
  → BASED_ON ≥1 claim + rationale; media via claims

Assumption?
  → statement + why; never fake EXTRACTED_FROM

Catalog channel/video metadata?
  → live without extraction-run theater (catalog exception)

Person on a claim?
  → approved episode map (or explicit unresolved policy) — identity gates from #5
```

---

## Decision log

| Date | Decision |
|------|----------|
| 2026-07-22 | Adopt minimum media-back chain: processed requires video + time span + quote + speaker label + run; claims require EXTRACTED_FROM processed (full path); inferences/assumptions chain without direct media fields but require run + rationale/why; tool/model on extraction runs; catalog raw exception preserved; optional denorm locators and enterprise PROV fields deferred for solo v1. |

---

## Sources / related

1. Issue #7 — Provenance minimum — https://github.com/etai83/uap-kg/issues/7  
2. Issue #3 — [epistemic-layer-ontology.md](./epistemic-layer-ontology.md)  
3. Issue #5 — [speaker-identity-and-alias-merge.md](./speaker-identity-and-alias-merge.md)  
4. Issue #12 — [youtube-ingestion-options.md](./youtube-ingestion-options.md)  
5. Issue #13 — [speaker-diarization-options.md](./speaker-diarization-options.md)  
6. Issue #4 — [event-identity-rule.md](./event-identity-rule.md)  
