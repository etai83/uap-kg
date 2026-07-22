# uap-kg system + product specification (v1)

| Field | Value |
|-------|--------|
| **Status** | **`spec-complete`** |
| **Version** | 1.0 |
| **Completed** | 2026-07-22 |
| **Audience** | Implementers (human or agent); sole product user is the **curator** |
| **Destination** | Written system+product **spec** for a personal UAP/NHI research knowledge graph from YouTube |
| **Not this document** | Running pipeline, graph DB choice, UI pixels, multi-user product |

**Spec complete ≠ product built.** This document locks model and product IA decisions so implementation can proceed **without reopening ontology, identity, claim shape, or approval rules**. Building is a **separate effort**.

**Normative hierarchy**

1. This file is the **single reading surface** for implementers.  
2. Decision assets under [`docs/research/`](../research/) are **authoritative long-form detail**.  
3. Where restatement and asset conflict, **use the asset and file an explicit conflict** — do not silent-merge.  
4. Domain language: [`CONTEXT.md`](../../CONTEXT.md) only.

**Abbreviations used here:** OQ = open question · SoT = source of truth.

---

## 0. Front matter

### 0.1 How to read

1. **§1** — product scope, seed channels, pilot.  
2. **§§2–3** — intake and speech pipeline (recommended stacks).  
3. **§§4–12** — write-path legality (layers, provenance, claims, identity, research objects, approval).  
4. **§13** — product UX information architecture (not pixels).  
5. **§14** — object/edge checklist for storage design.  
6. **§15** — pass/fail scenarios.  
7. **Appendix A** — deferred / out-of-scope / forbidden (first-class scope, not omissions).

### 0.2 Ticket → section index

| Issue | Title | Spec section(s) | Decision asset |
|------:|-------|-----------------|----------------|
| #2 | Seed channel set for v1 | §1.2–1.3 | [`seed-channel-set-v1.md`](../research/seed-channel-set-v1.md) |
| #12 | YouTube ingestion options | §2 | [`youtube-ingestion-options.md`](../research/youtube-ingestion-options.md) |
| #13 | Speaker diarization options | §3 | [`speaker-diarization-options.md`](../research/speaker-diarization-options.md) |
| #3 | Epistemic layer ontology | §4 | [`epistemic-layer-ontology.md`](../research/epistemic-layer-ontology.md) |
| #7 | Provenance minimum | §5 | [`provenance-minimum.md`](../research/provenance-minimum.md) |
| #6 | Claim model | §6 | [`claim-model.md`](../research/claim-model.md) |
| #4 | Event identity rule | §7 | [`event-identity-rule.md`](../research/event-identity-rule.md) |
| #11 | Topics vs events | §8 | [`topics-vs-events.md`](../research/topics-vs-events.md) |
| #5 | Speaker identity and alias merge | §9 | [`speaker-identity-and-alias-merge.md`](../research/speaker-identity-and-alias-merge.md) |
| #10 | Speaker credibility signals | §10 | [`speaker-credibility-signals-v1.md`](../research/speaker-credibility-signals-v1.md) |
| #8 | Contradiction and open-question model | §11 | [`contradiction-and-open-question-model.md`](../research/contradiction-and-open-question-model.md) |
| #9 | Human approval workflow | §12 | [`human-approval-workflow.md`](../research/human-approval-workflow.md) |
| #14 | Multi-telling compare UX | §13 | [`multi-telling-compare-ux.md`](../research/multi-telling-compare-ux.md) |
| #15 | Spec document outline | Outline + exit criteria | [`spec-document-outline.md`](../research/spec-document-outline.md) |
| #1 | Wayfinder map | Product framing | GitHub map issue |

### 0.3 Document non-goals

- Building the pipeline, graph store, or UI.  
- Public multi-user product, accounts, collaboration.  
- Broad opportunistic YouTube scrape / keyword harvest.  
- Automated live publishing of AI claims without human approval (**forbidden**, not deferred).  
- Wireframes, DB engine choice, multi-language product (Appendix A).

### 0.4 Implementability bar

An implementer must be able to:

1. Name every first-class object using `CONTEXT.md` terms.  
2. Enforce write-path legality (layer matrix, provenance minimum, identity gates, approval states) without inventing policy.  
3. Build review + multi-telling UX that only exposes decided actions and dimensions.  
4. Choose storage/UI tech later without reopening §§4–13.

---

## 1. Product framing and v1 scope

### 1.1 User and primary job

| Axis | Decision |
|------|----------|
| User | Sole **curator** — personal research tool |
| Primary job | Reconstruct and **cross-check the story** of real-world happenings across seed-channel **Tellings** |
| Evidence model | Hard epistemic typing + provenance |
| UX spine | **Event timeline** + **multi-telling compare** (§13) |

### 1.2 Seed channel set (committed)

Exactly **three** YouTube channels until the pilot corpus is fixed and a later expansion decision is made:

| # | Channel | Handle | Soft epistemic role |
|---|---------|--------|---------------------|
| 1 | Jesse Michels (American Alchemy) | [`@JesseMichels`](https://www.youtube.com/@JesseMichels) | Synthesis + investigative interview |
| 2 | Area52 (Chris Ramsay) | [`@Area52Investigations`](https://www.youtube.com/@Area52Investigations) | Community synthesis / popularizer |
| 3 | Danny Jones | [`@dannyjones`](https://www.youtube.com/@dannyjones) | Long-form interview host (broader fringe; UAP thick vertical) |

**Inclusion rules**

- **Density** on shared cases + **soft role diversity** (soft quotas never force zero multi-source overlap).  
- **English-only**; **YouTube only** as SoT (“episode” = YouTube video).  
- Prefer core UAP/NHI/disclosure as primary channel focus; curator may name a broader long-form host (Danny Jones).  
- **Hard exclusions:** non-English primary; not YouTube; pure clip-repost/mirrors; AI-voice essay mills; no original long-form.  
- Stance/disinfo: **curator veto at naming**, not a formal list taxonomy.  
- **No expansion beyond 3** until pilot corpus is fixed for first build.

**Detail:** [`seed-channel-set-v1.md`](../research/seed-channel-set-v1.md)

### 1.3 Pilot corpus

| Axis | Decision |
|------|----------|
| Size | ~**10 videos per channel** (~**30 total**) |
| Selection | **Curator selects every video** |
| Duration | Long-form preferred (~≥20–30 min) as guidance — not a hard reject for essential short primary-source clips |
| Profile effort | Research/profile only in wayfinding; **no bulk ingest required for this spec** |

**Seeded pool (3 / ~30)** — remaining picks are curator operational (Appendix A):

| Channel | Title | URL |
|---------|--------|-----|
| Jesse Michels | Proof That NASA Censored Moon Photos (and The Astronauts Knew!) | https://youtu.be/uVVqFg2v7ro |
| Area52 | Jesse Michels, UAPGerb & Chris Ramsay - Flying Saucer Diner | https://youtu.be/HFLBDi87888 |
| Danny Jones | “There Were 23 of Us” Area 51 Officer Finally Comes Clean \| TD Barnes | https://youtu.be/5hhKLqUbrYQ |

### 1.4 In scope / out of scope (v1 product)

| In scope | Out of scope |
|----------|----------------|
| Fixed seed channels + pilot videos | Open scrape / keyword harvest |
| Metadata + ToS-aware transcript path | Standing AV archive as product architecture |
| Layered KG + person/event/topic entities | Multi-user / RBAC / collaboration |
| AI-proposed, curator-gated live graph | Auto-live extraction claims |
| Event timeline + multi-telling compare | Publish/export product (deferred if ever) |
| Qualitative speaker credibility notes | Composite trust scores |

### 1.5 Standing preferences (locked)

1. Hard typed epistemic layers + provenance vs content edges.  
2. Named **Person** nodes + diarized attributions; cross-video identity via person, not labels.  
3. **Event** = real-world happening, not video beat.  
4. AI proposes; **curator** approves before live (catalog raw exception).  
5. UX spine: **event timeline** + **multi-telling compare**.

---

## 2. Source intake (YouTube)

**Detail:** [`youtube-ingestion-options.md`](../research/youtube-ingestion-options.md)

### 2.1 Metadata (primary path)

| Rule | Requirement |
|------|-------------|
| API | Google Cloud + **YouTube Data API v3** for public catalog metadata |
| Enumeration | Curated channel allowlist → channel → uploads playlist → video details |
| Persist | Stable IDs: `channelId`, `videoId`, `publishedAt`, title, description, duration, tags, caption-available, URLs |
| Stats | Volatile; treat as **cache** with policy-aware refresh/delete |
| Search | Prefer playlist enumeration over expensive search for “all videos of channel” |

### 2.2 Transcripts (tiered)

| Priority | Approach |
|----------|----------|
| 1 | Owner cooperation (OAuth / Studio export) |
| 2 | Manual / semi-manual official transcript for sparse high-value videos |
| 3 | Description / chapters / comments as weak text proxies |
| Default avoid | Automated third-party caption scrape pipelines as the **standing** ingestion layer |

There is **no bulk third-party caption API** suitable as the default product path (research conclusion).

### 2.3 Audio / ASR posture

- Automated download of AV as a **standing architecture** is a documented risk area (Appendix A).  
- Product correctness must **not** depend on redistributing isolated audio tracks.  
- If personal ASR is used, treat it as a constrained personal-research path — **not** a “ToS-cleared default product claim.”

### 2.4 Playback

- Playback via YouTube embed / open on YouTube.  
- Do not require a local AV archive for multi-telling or jump-to-timestamp *product* definition.  
- Jump still needs resolvable time anchors in the graph (§5).

### 2.5 Catalog exception

Official **catalog raw** (channel/video identity and public metadata snapshots) and mechanical media-track pointers may enter **`live` without claim-level approval** (§4, §12). Speech structure and all extractions remain gated.

---

## 3. Speech pipeline (ASR + diarization)

**Detail:** [`speaker-diarization-options.md`](../research/speaker-diarization-options.md)  
**Identity writes:** §9 (never auto-live person nodes from labels alone).

### 3.1 Two distinct problems

| Problem | Output |
|---------|--------|
| Diarization | Episode-local **speaker labels** (`SPEAKER_00`, …) |
| Name attribution | Label → **Person** (curator-gated for live) |

### 3.2 Recommended default stack (R)

| Path | Stack |
|------|--------|
| Local default | **WhisperX** + **pyannote** for ASR + diarization on long-form English interviews |
| Hosted name ID (optional) | **AssemblyAI** when needed |

Stack is **recommended**, not ontology — may change without reopening §§4–12.

### 3.3 Good-enough bar

- Quality sufficient for **human-reviewed** person mapping on typical 2–4 speaker long-form interviews.  
- Prefer **false-reject** over silent wrong merges for live person writes.

### 3.4 Failure modes implementers must plan for

- Split/merge speaker clusters.  
- Ads / announcers / audience.  
- Unknown third voice.  
- Host appearing as guest on another channel (same Person, guest role for that video).  
- Confidence scores as review assist only — **never** a live gate substitute.

---

## 4. Epistemic layer ontology

**Detail:** [`epistemic-layer-ontology.md`](../research/epistemic-layer-ontology.md)

### 4.1 Five hard layers (machine ids fixed)

Order: `raw` → `processed` → `claim` → `inference` → `assumption`

| Machine id | One-line definition |
|------------|---------------------|
| `raw` | Uninterpreted source capture: catalog facts + immutable media anchors |
| `processed` | Normalized structure from raw **without** world-truth (spans, speaker-attributed utterances) |
| `claim` | Attributed, checkable assertion a speaker made; recording ≠ truth verdict |
| `inference` | Conclusion **not stated as such** in source; reasoning over claims |
| `assumption` | Provisional scaffolding premise; not established by source text |

- One required `layer` enum per layered node.  
- **Layer is immutable** after create.  
- Entity identities (Person, Channel, Video catalog, Event, Topic) sit **outside** the five-layer spine.

### 4.2 Edges

| Axis | Rule |
|------|------|
| Edges layered? | **No** |
| `edge_kind` | **provenance** vs **content** |
| Enforcement | Write path validates legal endpoint matrices; illegal pairs are **hard errors** |

**Direction (provenance):** dependent → support (claim `EXTRACTED_FROM` utterance).

### 4.3 Provenance matrix (v1)

| Predicate | Legal source → target | Notes |
|-----------|----------------------|-------|
| `DERIVED_FROM` | processed → raw | Structural derivation |
| `EXTRACTED_FROM` | claim → processed | Primary claim grounding |
| `GROUNDED_IN` | claim → raw | Optional sugar **only if** processed path also exists |
| `BASED_ON` | inference → claim \| inference | ≥1 claim required for live inference |
| `RESTS_ON` | inference (or rare claim) → assumption | Scaffolding dependency |
| `PROPOSED_BY` | any layered → agent | Actor ref |
| `APPROVED_BY` | any layered → curator | Required on live transition for gated objects |
| `SUPERSEDES` | same layer → same layer | Versioning |

### 4.4 Illegal provenance (hard reject)

| Pattern | Why |
|---------|-----|
| assumption → claim (any silent upgrade) | Masquerade |
| inference → claim (as promotion) | Re-extract as claim only if speaker said it |
| claim → raw only, no processed path | Skips who-said-what structure |
| In-place layer rewrite / `PROMOTED_TO` same id | Layer immutability |

### 4.5 Promotion

Promotion **never** rewrites type in place. It creates a **new** higher-layer node with legal provenance to lower support (optional supersession of a prior proposal).

### 4.6 AI vs curator

- AI may propose any non-catalog extraction into **`proposed`**.  
- Only curator completes gated objects to **`live`**.  
- Catalog raw exception: §2.5 / §12.

---

## 5. Provenance minimum

**Detail:** [`provenance-minimum.md`](../research/provenance-minimum.md)

### 5.1 Honesty bar

Minimum is what a solo curator needs to:

1. Re-open the video at the right time,  
2. See who was labeled speaking,  
3. Re-run or distrust a pipeline,  
4. Explain why a node exists.

Not enterprise audit theater.

### 5.2 Media anchors (raw)

**Catalog raw** (auto-live eligible):

| Field | Required |
|-------|----------|
| `channel_id` + durable locator | Yes |
| `video_id` | Yes |
| `published_at`, title, duration | Yes for useful catalog |

**Media-track raw** (ASR / caption / diarization anchors):

| Field | Required |
|-------|----------|
| `video_id` | Yes |
| Track kind | Yes |
| Artifact ref | Yes |
| Time base (if timed) | Yes |
| Coarse acquisition method | Yes (e.g. `owner_export`, `personal_asr`) |
| Extraction run id | Yes for processing jobs |

### 5.3 Extraction run

- First-class process identity for pipeline or curator write invocation.  
- Tool/model/version live **on the run**; nodes store `extraction_run_id`.  
- Not required for pure API catalog rows.

### 5.4 Required chain by layer

| Layer | Minimum chain |
|-------|----------------|
| **Processed** (speech) | `video_id` + timestamp span + quote text + speaker label (or unresolved) + `DERIVED_FROM` raw + extraction run |
| **Claim** | ≥1 `EXTRACTED_FROM` processed with full path to raw; run id; Person if live attributed claim |
| **Inference** | ≥1 `BASED_ON` claim + rationale + run; media via claims (no direct video/time required) |
| **Assumption** | Statement + why-introduced + run; **no** fake `EXTRACTED_FROM` |

Denormalized video/time/quote on claims are **recommended UX caches**, not substitutes for edges.

### 5.5 Hard rejects

- Live claim with only claim→raw shortcut (missing processed path).  
- Live claim with only `SPEAKER_n` attribution (no approved Person).  
- Jump-to-timestamp inventing times from Event keys or upload date alone.

### 5.6 Optional in v1

Char/token offsets, full hyperparams, content hashes, PROV-O export, credibility scores on provenance, channel id duplicated on every claim, word-level confidence arrays.

---

## 6. Claim model

**Detail:** [`claim-model.md`](../research/claim-model.md)

### 6.1 Definition

A **Claim** is a graph node with `layer=claim` that records:

> **Speaker S asserts proposition P**, grounded in processed (hence raw) evidence from a specific video (and timestamps), optionally about world **Event** E.

Claims are the **unit of narrative comparison** across Tellings. They are **recorded assertions**, not endorsements that P is true.

### 6.2 Claim vs inference vs assumption

| | Claim | Inference | Assumption |
|--|-------|-----------|------------|
| Source | Speaker **said** it | Beyond transcript | No asserting quote |
| Spine | → processed → raw | `BASED_ON` claims | `RESTS_ON` scaffolding |
| SUPPORTS/CONTRADICTS | Yes | Yes | **No** as evidence |
| Unsure speaker is *correct*? | Still a **claim** | — | — |

### 6.3 Atomicity

- Live claims: **one atomic proposition**.  
- Compounds: split before live (conjunctions, fact+explanation, multi-object independent facts).  
- AI may stage compound drafts for “split these?” UI — never live unsplit.

### 6.4 Spec-level fields (logical)

| Field / edge | Live required? | Definition |
|--------------|----------------|------------|
| `id`, `layer=claim`, lifecycle | Yes | Identity + immutability of layer |
| `claim_text` | Yes | Normalized atomic proposition |
| `claim_kind` | Yes (default) | `world_assertion` \| `meta_speech` \| `self_report` |
| `ATTRIBUTED_TO` → Person | Yes for live | Approved episode map; unresolved only on **proposed** |
| `ABOUT_EVENT` | Preferred | Unbound allowed when keys insufficient |
| `ABOUT_TOPIC` | Optional | Thematic; not Event substitute |
| `EXTRACTED_FROM` → processed | Yes (≥1) | Primary grounding |
| Processed → raw path | Yes | Video + time recoverable |
| `PROPOSED_BY` / run id | Yes (AI) | Process identity |
| `APPROVED_BY` | Yes on live | Curator |

**Optional:** polarity, modality, extraction_confidence (review assist only), quote excerpt for UI.

**Out of v1 claim schema:** true/false verdicts; credibility scores; auto-dedupe of paraphrases into one claim id.

### 6.5 Multi-speaker dialogue

- One claim per atomic proposition **per speaker**.  
- Attribute to who **uttered** the words.  
- Host paraphrase of guest ≠ guest claim (unless guest affirms on guest’s own spans).  
- Host `meta_speech` may be UI-minimized; never silently merged into guest.

### 6.6 Cross-telling

Two videos → **two claim nodes**. Optional `SAME_ASSERTION_AS` for paraphrastic same assertable — **never collapse ids**.

---

## 7. Event identity and Tellings

**Detail:** [`event-identity-rule.md`](../research/event-identity-rule.md)

### 7.1 Event ≠ video beat

| Term | Meaning |
|------|---------|
| **Event** | Real-world happening (or coherent multi-day incident / campaign parent) |
| **Beat** | In-video structural unit — organizes media, never is an Event |
| **Telling** | One account of an Event in a specific video (or continuous segment) |
| **Multi-telling** | ≥2 Tellings of the same Event across sources |

Competing explanations of one happening stay **one Event** with multiple claims.

### 7.2 Identity keys (weighted)

| Key | Role |
|-----|------|
| K1 Public name / case label | Strong when discourse has a stable name |
| K2 Time window | Date or interval; partial OK |
| K3 Place / theater | Waterspace, base, city, range, hearing venue, … |
| K4 Principal actors / platforms | Witnesses, units, ships, agencies — **not** retelling host |
| K5 Documentary anchors (optional) | Hearing ID, report, FOIA, canonical news date |

**Non-keys:** topic alone; video id; upload date; claim interpretation (“NHI” vs “drone”); speaker who discussed it.

### 7.3 Merge / split / nesting

- **Merge candidates:** stable name + compatible keys; or strong time+place+actors; or same documentary anchor.  
- **Hard split:** non-overlapping time; incompatible theater; different canonical cases; follow-up years later (hearing/release) = **related distinct Events**.  
- **Claim-only divergence** → same Event, competing claims.  
- **Nested:** shallow parent → child when discourse treats campaign as one story and multi-telling needs sub-foci.  
- **Multi-day:** prefer one parent with optional phase children.

### 7.4 Uncertainty

| State | Behavior |
|-------|----------|
| Confirmed same/distinct | Curator-gated live merge/split |
| Provisional same | Separate IDs + **provisional identity link**; optional **provisional identity bundle** for compare |
| Unknown | Separate + **identity OQ** |

**Never silent auto-merge of high-stakes Events.** AI proposes; curator approves.

### 7.5 Authority

AI proposes Event create/merge/split; **curator** approves live identity commits.

---

## 8. Topics (vs Events)

**Detail:** [`topics-vs-events.md`](../research/topics-vs-events.md)

### 8.1 Core distinction

- **Topic:** thematic **type** (controlled taxonomy entity).  
- **Event:** instance-level **happening**.  
- Sharing a Topic **never** merges Events. Topics are **non-keys** for Event identity.

### 8.2 Representation

- Lightweight Topic nodes: canonical name + optional aliases + optional shallow parent.  
- Curator-owned controlled taxonomy (~**15–40** terms v1).  
- Free strings are **surface tags** on processed until mapped to Topics.

### 8.3 Attachment

| Attach to | Role |
|-----------|------|
| Event, Claim (primary) | `ABOUT_TOPIC` content edges |
| Inference (allowed) | Same |
| Video catalog (optional) | Browse aboutness |
| Processed | Surface tags only until mapped + approved |

### 8.4 Non-negotiables

1. Do not mint mega-Events from themes.  
2. Do not merge Events because they share Topics.  
3. General theses without fixable keys → Claims + Topic, not invented Event.  
4. Multi-telling stays **Event-scoped**; Topics are filters / secondary browse.

### 8.5 Live gate

AI proposes assignments/new terms; **curator approves** before live.

---

## 9. Speaker identity and aliases

**Detail:** [`speaker-identity-and-alias-merge.md`](../research/speaker-identity-and-alias-merge.md)

### 9.1 Label ≠ Person

`SPEAKER_n` is episode-local. It is **not** a Person and has **no** cross-video identity until mapped through a Person.

### 9.2 Layer model

| Layer | Object | Scope |
|-------|--------|-------|
| L0 | Speaker label | One video/job |
| L1 | Episode attribution (label → person?) | One video |
| L2 | Person node (+ aliases) | Graph-global |
| L3 | Claim attribution | Graph |

Live L3 requires approved L1 + live/active L2.

### 9.3 Person lifecycle

`proposed` → `candidate` → `active` | `merged-away` | `deprecated`

- Create/active requires canonical display name, identity evidence, curator approve.  
- Do not mint persons solely because diarization emitted a new label.

### 9.4 Host vs guest defaults

| Case | Policy |
|------|--------|
| Seed hosts (Jesse Michels, Chris Ramsay, Danny Jones) | Strong **provisional** channel–host defaults; first host person + mappings still curator-confirmed; later clean host maps batch-eligible |
| Guests | Title/description/credits + optional LLM/API as **proposals only** |
| Host on another channel | Same Person node; **guest** role for that video |
| Ads / audience / announcer VO | **Unresolved** — no person mint |

### 9.5 Aliases

- One **canonical display name** per person; typed aliases (nickname, handle, spelling_variant, title_form, …).  
- Channel/show brands are **not** person aliases (Area52 ≠ Chris Ramsay as a name bridge).  
- Normalized string equality **never** alone merges live nodes.

### 9.6 Unresolved speakers

- Stay as episode-scoped unresolved labels.  
- **No** `Unknown Person N` live nodes.  
- **No** cross-video join of unresolved IDs.

### 9.7 Merge evidence

| Never live-merge on | May propose on | Must approve |
|---------------------|----------------|--------------|
| String-only match | Multi-signal (aliases + context, voiceprint + name family) | Create person, collision alias, merge two actives, first guest attribution |

Prefer false reject. Voiceprints / AssemblyAI name ID / LLM maps are **proposal signals** only.

---

## 10. Speaker credibility (v1)

**Detail:** [`speaker-credibility-signals-v1.md`](../research/speaker-credibility-signals-v1.md)

### 10.1 Definition

Soft research metadata on a **Person** — not identity, not epistemic layer, not claim truth.

### 10.2 In-scope signals

1. **Curator free-text annotations** (primary).  
2. **Role labels** (descriptive: host, guest, witness-participant, secondhand, researcher/journalist, official/institutional, …) — not trust multipliers.  
3. **Consistency observations** (person × Event): agree / conflict / drift / insufficient_data — AI proposes candidates with claim IDs; live annotations curator-gated.

### 10.3 Hard forbids

- Composite trust scores, reliability %, reputation scrapes as graph truth.  
- Auto hide/down-rank claims by credibility.  
- Credibility objects on `SPEAKER_n` / unresolved labels.  
- Using credibility to create/merge/split persons or Events.

### 10.4 Seed-channel note

Hosts get descriptive host role defaults on their channels. Subscriber counts are **not** credibility signals.

---

## 11. Contradiction, agreement, gaps, open questions

**Detail:** [`contradiction-and-open-question-model.md`](../research/contradiction-and-open-question-model.md)

### 11.1 Core job

On a **focus Event** (or **provisional identity bundle**), surface **agreement**, **conflict**, and **gaps**. Not a global dump of disagreements.

### 11.2 Content edges

| Predicate | Participants |
|-----------|--------------|
| `SUPPORTS`, `CONTRADICTS`, `SAME_ASSERTION_AS` | **claim \| inference** only |

**Assumptions never** evidence endpoints of SUPPORTS / CONTRADICTS.

### 11.3 Contradiction record

First-class research object **outside** the five layers: packages conflict pairs, optional research facet, status, curator notes. Not a truth verdict; not an Event split.

Lifecycle: `proposed` → `open` → `resolved` | `wontfix` (+ `rejected` / `superseded`).

On resolve: claims stay live recorded assertions — **no winner collapse**, no auto truth flags.

### 11.4 Open Question

First-class research object. Kinds (v1): `identity`, `claim_conflict`, `coverage_gap`, `key_disagreement`, `attribution`, `other`.

Lifecycle: `proposed` → `open` → `resolved` | `wontfix` (+ `rejected`).

- System/AI may propose.  
- **Only curator** opens, resolves, or wontfixes.

### 11.5 Coverage gaps

Missing assertable content on a facet under focus scope. Derived UI and/or OQ of kind `coverage_gap`. Do **not** invent opposing claims to fill gaps. Explicit missing premise scaffolding is an **assumption**, not a gap claim.

### 11.6 Identity vs claim conflict

“Same Event as X?” is an **identity OQ** / provisional link — **not** a claim contradiction.

### 11.7 Agreement

Prefer `SAME_ASSERTION_AS` and/or `SUPPORTS`. Agreement clusters may be **derived** for UX; not a required stored type in v1.

---

## 12. Human approval workflow

**Detail:** [`human-approval-workflow.md`](../research/human-approval-workflow.md)

### 12.1 Lifecycle (layered nodes)

| State | Meaning | Default multi-telling evidence? |
|-------|---------|--------------------------------|
| `proposed` | Draft; not approved | No (review only) |
| `live` | Curator-approved | Yes |
| `rejected` | Declined; retained for audit | No |
| `superseded` | Replaced via `SUPERSEDES` | No (successor yes) |

Orthogonal to epistemic layer, person states, event provisionality, topic lifecycle.

### 12.2 Who may write live

| Actor | Create proposed | Set live on gated objects |
|-------|-----------------|---------------------------|
| AI / pipeline | Yes | **Never** |
| System catalog ingest | Optional | Catalog raw exception only |
| Curator | Yes | **Yes** (only human path) |

### 12.3 Auto-land vs must-approve

| Auto-land | Must approve before live |
|-----------|---------------------------|
| Catalog raw + mechanical media-track pointers | processed, claim, inference, assumption |
| Stats snapshot cache (catalog-adjacent) | Person create / alias / merge / episode map |
| | Event merge/split commits |
| | Topic mint / live assignment |
| | Live credibility annotations |
| | Contradiction records & OQs as live research state |

**Not auto-land:** ASR-derived processed; high-confidence claims; host defaults without curator action.

### 12.4 Live checklists (approve gates)

Approval is a **hard error** if checklist fails.

**Processed:** `layer=processed`; legal `DERIVED_FROM` raw; video_id + timestamp span + quote; speaker_label or explicit unresolved; extraction_run_id + PROPOSED_BY; APPROVED_BY on transition.

**Claim:** atomic claim_text; ≥1 EXTRACTED_FROM live/co-approved processed; processed→raw resolves; ATTRIBUTED_TO active Person with approved episode map; run id + PROPOSED_BY; APPROVED_BY. Unresolved-speaker claims stay proposed by default.

**Inference:** non-empty rationale; ≥1 BASED_ON claim live/co-approved; no masquerade as claim; run + APPROVED_BY.

**Assumption:** statement + why-introduced; no fake EXTRACTED_FROM; run + APPROVED_BY.

**Episode map / Person:** canonical name + evidence for create; video_id + speaker_label + person_id + method for map; multi-signal + approve for merge.

### 12.5 Bundles, batch, atomic co-approval

- Default review unit: **video-scoped approval bundle**.  
- **Batch approve** allowed when each node passes its checklist and dependencies close.  
- **Atomic co-approval** preferred when post-state is matrix-legal (e.g. processed + claim + episode map).  
- Never confidence-timer auto-live; never hide layer badges.

### 12.6 Supersession

Do not patch live semantic content in place. Mint new same-layer node, `SUPERSEDES` prior, prior → `superseded`. Provenance runs preserved.

### 12.7 Surfaces (IA only)

Primary: approval bundle review; item drill-down; approve actions reused from multi-telling (§13). No wireframes required for spec completeness.

---

## 13. Multi-telling product UX

**Detail:** [`multi-telling-compare-ux.md`](../research/multi-telling-compare-ux.md)

### 13.1 Dual spine

1. **Event timeline** — chronological index of world Events (by Event time window, **not** upload date).  
2. **Multi-telling compare** — line up Tellings for one focus.

Topics **filter** navigation only; never become compare identity.

### 13.2 Focus scope

- One **focus Event**, or  
- Explicit **provisional identity bundle** (“compare as if same” without collapsing IDs).  

Never “everything under Topic X” as one happening.

### 13.3 Default sections (IA)

**Timeline**

- Identity strip · chronological Event list · filters (time, Topic, channel/video, identity state, multi-telling density) · provisional/duplicate hints · OQ badges · entry to compare.

**Compare**

1. Focus header (name, keys, identity state, parent/child exits, Topic chips as filters)  
2. Telling strip (per video/segment: channel, video, speakers, claim counts)  
3. Claims board (primary; rows = **live atomic claims**; inferences only if clearly badged)  
4. Agreement (derived clusters via SAME_ASSERTION_AS / SUPPORTS)  
5. Conflict (open contradiction records + poles with media jumps)  
6. Gaps & open questions (coverage by facet + first-class OQs; identity OQs elevated in provisional mode)  
7. Provenance / media (video + timestamp + quote via claim→processed→raw)

Secondary (nice-to-have): scaffolding panel (assumptions, non-evidence); qualitative credibility notes only — **no trust scores**.

### 13.4 Comparison dimensions (must answer)

| Dimension | What it answers |
|-----------|-----------------|
| Who | ATTRIBUTED_TO Person |
| What | atomic claim_text (+ kind/layer badge) |
| When said | video + timestamp span |
| About | focus Event keys + optional research facet |
| Agreement | same-assertable / support clusters |
| Conflict | CONTRADICTS + contradiction records (not identity doubt) |
| Gaps | empty facets ± OQs |
| Provenance | legal grounding path + lifecycle badge |

### 13.5 Minimum actions (v1 must)

| Action | Rule |
|--------|------|
| **Approve claim** | proposed→live with full §6/§5/§12 checklist; optional atomic co-approve of processed + episode map; AI never sets live |
| **Mark open question** | Curator creates/promotes OQ on focus/bundle; AI only proposes |
| **Jump to timestamp** | Open media at claim’s provenance span; **disabled** if grounding incomplete |

**Strongly recommended:** reject claim; bind to Event; mark same-assertion; open/resolve contradiction; switch confirmed↔provisional mode; navigate parent/child Events.

### 13.6 Forbidden patterns

- Assumptions as evidence/conflict rows.  
- Trust-ranked speaker cards as primary compare unit.  
- Silent proposed-as-live evidence.  
- Topic-as-Event compare scope.  
- Jump inventing times without grounding path.  
- Multi-user social chrome / consensus meters.

### 13.7 Visibility

Default: **live** claims and open research objects. Proposed only in review overlay / provisional mode.

### 13.8 Pilot framing

Jesse Michels · Area52 · Danny Jones multi-telling density is the design pilot. Sparse “single Telling only” states are honest and allowed.

---

## 14. End-to-end object catalog

Checklist for implementers — every item must be representable; storage tech is Appendix A.

### 14.1 Layered nodes

| Type | Notes |
|------|--------|
| raw | Catalog + media anchors |
| processed | Speech spans, structure, surface tags |
| claim | Atomic attributed assertions |
| inference | Beyond transcript; premises required |
| assumption | Scaffolding only |

### 14.2 Entities (outside five layers)

Channel · Video (catalog) · Person · Alias · Event · Topic · Extraction run · Speaker label (episode-local, not entity identity) · Telling (modeling concept / grouping)

### 14.3 Research / workflow objects

Contradiction record · Open Question · Consistency observation · Approval bundle · Provisional identity link · Provisional identity bundle · Episode map / attribution

### 14.4 Edge catalog (minimum families)

**Provenance:** DERIVED_FROM, EXTRACTED_FROM, GROUNDED_IN (sugar only with full path), BASED_ON, RESTS_ON, PROPOSED_BY, APPROVED_BY, SUPERSEDES, run linkage  

**Content:** ABOUT_EVENT, ABOUT_TOPIC, ATTRIBUTED_TO, SUPPORTS, CONTRADICTS, SAME_ASSERTION_AS, ELABORATES (as allowed)  

**Identity:** provisional identity links; person merge audit  

Exact predicate spellings follow decision assets; do not invent parallel synonym predicates.

### 14.5 Orthogonal axes

| Axis | Values |
|------|--------|
| Epistemic layer | raw / processed / claim / inference / assumption |
| Lifecycle (layered) | proposed / live / rejected / superseded |
| Person state | proposed / candidate / active / merged-away / deprecated |
| Event identity | confirmed vs provisional links / bundles |
| Topic lifecycle | proposed / live / deprecated |
| Open question | proposed / open / resolved / wontfix / rejected |
| Contradiction | proposed / open / resolved / wontfix / rejected / superseded |

---

## 15. Worked scenarios (normative intent)

Full narratives live in research assets. Spec requires these **pass/fail intents**.

### 15.1 Clean 2-speaker interview

Catalog live → ASR/diarize → provisional host/guest map → processed spans → atomic claims proposed → bundle batch approve → claims live with full grounding → appear on Event compare.

### 15.2 Cross-channel multi-telling

Same Event discussed on ≥2 seed channels → distinct claim nodes per telling → SAME_ASSERTION_AS / SUPPORTS for agreement · CONTRADICTS + contradiction record for conflict · jump works on each pole.

### 15.3 Uncertain Event identity

Do not silent-merge high-stakes candidates → provisional links + identity OQ → optional provisional bundle compare → claims stay on their Event ids with membership badges.

### 15.4 Correction after live

Edit creates new same-layer node + SUPERSEDES; old superseded; history walkable; default views use successor.

### 15.5 Must fail (write-path)

| Attempt | Result |
|---------|--------|
| Assumption as claim or evidence pole | Reject |
| Live claim without processed→raw path | Reject |
| Live claim with only SPEAKER_n attribution | Reject |
| Live person merge on string match alone | Reject |
| Topic-only Event merge | Reject |
| Auto-live extraction claims | Reject |
| Compound multi-proposition live claim | Reject (split first) |
| Jump to timestamp without grounding | Disable / reject |

---

## 16. Glossary

Canonical definitions: [`CONTEXT.md`](../../CONTEXT.md).

Do not introduce product synonyms for typed concepts (e.g. do not call Events “topics,” claims “facts,” or SPEAKER labels “persons”).

---

## Appendix A — Deferred / open

Explicit fog graduation. These are **not** model reopeners when left undecided.

| Item | Disposition | Notes |
|------|-------------|-------|
| Graph storage / query technology | Deferred | Must express §14 objects/edges/lifecycle |
| Scale beyond pilot / full-channel ingest | Deferred | Channel count fixed at 3 until pilot complete |
| Non-English / multi-language | Out of scope v1 | English-only |
| Non-YouTube sources | Out of scope v1 | Destination is YouTube-sourced |
| Composite credibility scores | Out of scope v1 | §10 qualitative only |
| Export / publish / share subgraphs | Deferred | Personal tool first |
| Refresh cadence for new uploads | Deferred | Catalog path reusable |
| Exact seed Topic term list | Deferred (curator) | Rules in §8 |
| Remaining pilot video picks (~27) | Curator operational | Does not reopen §1.2 |
| Legal treatment of personal ASR on third-party audio | Deferred (policy) | §2 documents risk |
| Exact ASR/diarization vendor thresholds & SKUs | Recommended only | §3 |
| Wireframes / shortcuts / notifications | Out of model-spec scope | IA is normative |
| Multi-user roles / RBAC | Out of scope | Solo curator |
| Numeric DB types, indexes, APIs | Implementation | Conceptual fields only |
| Automated paraphrase clustering thresholds | Deferred | Human gate remains |
| True/false verified claim flags | Deferred | Curator-owned if added |
| Public multi-user product | Out of scope | map #1 |
| Broad opportunistic scrape | Out of scope | map #1 |
| Auto-live AI claims | **Forbidden** | Standing preference |

---

## Appendix B — Decision asset index

| Asset | Path |
|-------|------|
| Spec document outline (exit criteria) | [`docs/research/spec-document-outline.md`](../research/spec-document-outline.md) |
| Seed channel set | [`docs/research/seed-channel-set-v1.md`](../research/seed-channel-set-v1.md) |
| YouTube ingestion | [`docs/research/youtube-ingestion-options.md`](../research/youtube-ingestion-options.md) |
| Speaker diarization | [`docs/research/speaker-diarization-options.md`](../research/speaker-diarization-options.md) |
| Epistemic layer ontology | [`docs/research/epistemic-layer-ontology.md`](../research/epistemic-layer-ontology.md) |
| Provenance minimum | [`docs/research/provenance-minimum.md`](../research/provenance-minimum.md) |
| Claim model | [`docs/research/claim-model.md`](../research/claim-model.md) |
| Event identity | [`docs/research/event-identity-rule.md`](../research/event-identity-rule.md) |
| Topics vs events | [`docs/research/topics-vs-events.md`](../research/topics-vs-events.md) |
| Speaker identity | [`docs/research/speaker-identity-and-alias-merge.md`](../research/speaker-identity-and-alias-merge.md) |
| Speaker credibility | [`docs/research/speaker-credibility-signals-v1.md`](../research/speaker-credibility-signals-v1.md) |
| Contradiction & open questions | [`docs/research/contradiction-and-open-question-model.md`](../research/contradiction-and-open-question-model.md) |
| Human approval | [`docs/research/human-approval-workflow.md`](../research/human-approval-workflow.md) |
| Multi-telling UX | [`docs/research/multi-telling-compare-ux.md`](../research/multi-telling-compare-ux.md) |
| Glossary | [`CONTEXT.md`](../../CONTEXT.md) |

---

## Appendix C — Policy cheat-sheet

```
Product who/what/scope?          → §1
Catalog / transcripts / audio?   → §2
Who spoke when / ASR labels?     → §3  (Person writes still §9)
Layer / promotion / masquerade?  → §4
How do we know where it came from? → §5
Recorded assertion unit?         → §6
Real-world happening?            → §7
Theme / taxonomy?                → §8
Named human / SPEAKER_n / merge? → §9
Soft trust metadata?             → §10
Agreement / conflict / gap / OQ? → §11
Proposed → live / batch / supersede? → §12
Timeline or compare UI?          → §13
DB / language / pixels / multi-user? → Appendix A
```

---

## Document history

| Date | Change |
|------|--------|
| 2026-07-22 | Skeleton created from closed wayfinder decisions + outline. Status: `skeleton`. |
| 2026-07-22 | Prose-filled §§0–16 + appendices to depth bar; status → **`spec-complete`**. Map destination met. |

---

## Exit criteria (met)

| Gate | Status |
|------|--------|
| A. Outline accepted (#15) | Met |
| B. Decision tickets #2–#15 closed | Met |
| C. Spec complete (this document) | **Met** — sections 0–16 + App A–B filled; write-path + UX IA specified; fog in App A; CONTEXT.md language |
| D. Map complete (#1) | Met when map closed with pointer here |

**Spec complete ≠ product built.**
