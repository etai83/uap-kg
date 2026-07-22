# uap-kg system + product specification (v1)

| Field | Value |
|-------|--------|
| **Status** | `skeleton` — structure + decision pointers; prose fill toward `spec-complete` per `docs/research/spec-document-outline.md` |
| **Audience** | Implementers and future tickets; sole product user is the **curator** |
| **Destination** | Written system+product **spec** for a personal UAP/NHI research knowledge graph from YouTube |
| **Not this document** | Running pipeline, graph DB choice, UI pixels, multi-user product |

**Spec complete ≠ product built.** Closing model debates and filling this document meets the wayfinder map destination. Implementation is a separate effort.

**Normative detail** lives in decision assets under `docs/research/`. This file is the **single reading surface**: short restatements + pointers. Where restatement and asset conflict, **fix the asset and file an explicit conflict** — do not silent-merge.

**Language:** use terms from [`CONTEXT.md`](../../CONTEXT.md) only.

---

## 0. Front matter

### 0.1 How to read

1. Read **§1** for product scope.  
2. Use **§§4–12** for write-path and research-object rules.  
3. Use **§13** for product UX information architecture.  
4. Use **§14** as an object/edge checklist.  
5. Treat **Appendix A** as first-class: deferred items are **not** accidental omissions.

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
| #15 | Spec document outline | outline + exit criteria | [`spec-document-outline.md`](../research/spec-document-outline.md) |
| #1 | Wayfinder map | product framing | GitHub map issue |

### 0.3 Document non-goals

- Building the pipeline, graph store, or UI.  
- Public multi-user product, accounts, collaboration.  
- Broad opportunistic YouTube scrape / keyword harvest.  
- Automated live publishing of AI claims without human approval (**forbidden**, not deferred).

---

## 1. Product framing and v1 scope

### 1.1 User and primary job

- **User:** sole **curator** (personal research tool).  
- **Primary job:** reconstruct and **cross-check the story** of real-world happenings across seed-channel **Tellings** — with hard epistemic typing and provenance.  
- **Detail:** map #1 destination; UX spine in §13.

### 1.2 Seed channel set (committed)

Exactly **three** YouTube channels until the pilot corpus is fixed and a later expansion decision is made:

1. Jesse Michels (American Alchemy) — `@JesseMichels`  
2. Area52 — `@Area52Investigations`  
3. Danny Jones — `@dannyjones`  

**Rules:** English-only; YouTube only as source-of-truth; density on shared cases + soft epistemic role diversity; personal curator veto at naming — not a formal “disinfo” taxonomy.

**Detail:** [`seed-channel-set-v1.md`](../research/seed-channel-set-v1.md)

### 1.3 Pilot corpus

- Target **~10 videos per channel (~30 total)**.  
- **Human selects every video.** Long-form preferred (~≥20–30 min) as guidance, not a hard reject for essential short primary-source clips.  
- Completing the remaining picks is **curator operational** (Appendix A); it does not reopen seed rules.

### 1.4 In scope / out of scope (v1 product)

| In scope | Out of scope |
|----------|----------------|
| Fixed seed channels + pilot videos | Open scrape / keyword harvest |
| Metadata + ToS-aware transcript path | Standing AV archive product architecture |
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

- Google Cloud + **YouTube Data API v3** for public catalog metadata.  
- Curated channel allowlist → channel → uploads playlist → video details.  
- Persist **stable identifiers** (channelId, videoId, publishedAt, title, description, duration, tags, caption-available, URLs).  
- Volatile stats: treat as cache with policy-aware refresh/delete.  
- Prefer playlist enumeration over expensive search for “all videos of channel.”

### 2.2 Transcripts (tiered)

| Priority | Approach |
|----------|----------|
| 1 | Owner cooperation (OAuth / Studio export) |
| 2 | Manual / semi-manual official transcript for sparse high-value videos |
| 3 | Description / chapters / comments as weak text proxies |
| Default avoid | Automated third-party caption scrape pipelines as the standing ingestion layer |

### 2.3 Audio / ASR posture

- Automated download of AV as a **standing architecture** is a documented risk area (Appendix A).  
- Product correctness must not depend on redistributing isolated audio tracks.  
- If personal ASR is used, treat it as a constrained personal-research path, not a “ToS-cleared default product claim.”

### 2.4 Playback

- Playback via YouTube embed / open on YouTube.  
- Do not require a local AV archive for multi-telling or jump-to-timestamp *product* definition (jump still needs resolvable time anchors in the graph — §5).

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

- **Local default:** WhisperX (or Whisper + pyannote) for ASR + diarization on long-form English interviews.  
- **Hosted name ID (optional):** AssemblyAI when needed.  
- Stack is **recommended**, not ontology — may change without reopening §§4–12.

### 3.3 Good-enough bar

- Quality sufficient for **human-reviewed** person mapping on typical 2–4 speaker long-form interviews.  
- Prefer false-reject over silent wrong merges for live person writes.

### 3.4 Failure modes implementers must plan for

- Split/merge speaker clusters; ads/announcers; unknown third voice; host/guest swap across shows; confidence not a live gate substitute.

---

## 4. Epistemic layer ontology

**Detail:** [`epistemic-layer-ontology.md`](../research/epistemic-layer-ontology.md)

### 4.1 Five hard layers (machine ids fixed)

`raw` → `processed` → `claim` → `inference` → `assumption`

- One required `layer` enum per layered node.  
- **Layer is immutable** after create.  
- Entity identities (Person, Channel, Video catalog, Event, Topic) sit **outside** the five-layer spine.

### 4.2 Edges

- Edges are **not** layered.  
- `edge_kind`: **provenance** vs **content**.  
- Typed predicates with legal endpoint constraints (matrices in the decision asset).

### 4.3 Promotion

- Promotion never rewrites type in place.  
- Creates a **new** higher-layer node with legal provenance to lower support.

### 4.4 Illegal masquerade (hard reject)

- Assumption ↛ claim or inference.  
- Inference ↛ claim.  
- Claim ↛ raw/processed.  
- Assumptions never participate as evidence endpoints of SUPPORTS / CONTRADICTS.

### 4.5 AI vs curator

- AI may propose any non-catalog extraction into **`proposed`**.  
- Only curator completes gated objects to **`live`**.  
- Catalog raw exception: §2.5 / §12.

---

## 5. Provenance minimum

**Detail:** [`provenance-minimum.md`](../research/provenance-minimum.md)

### 5.1 Media anchors (raw)

- YouTube `video_id` + channel identity.  
- Timed track references (caption/ASR/diarization artifacts) when speech is involved.  
- **Timestamp span** (`t_start`, `t_end`) on processed speech that grounds claims.

### 5.2 Extraction run

- First-class record of a pipeline or curator write invocation.  
- Tool/model identity + timestamp; nodes reference the run.

### 5.3 Required grounding by layer (normative spine)

| Layer | Minimum chain |
|-------|----------------|
| Processed (speech) | → raw media anchors (video + time when speech) |
| Claim | `EXTRACTED_FROM` processed → raw; video + time recoverable |
| Inference | Premises via claims (and optional live inferences); no new media required |
| Assumption | Scaffolding links; **not** media-grounded as if it were a claim |

### 5.4 Hard rejects

- Live claim with only claim→raw shortcut (missing processed path).  
- Live claim with only `SPEAKER_n` attribution (no approved Person).  
- Jump-to-timestamp inventing times from Event keys or upload date alone.

### 5.5 Optional in v1

Full list of non-requirements is in the decision asset (e.g. heavy citation export formats). Do not block pilot on optional packaging.

---

## 6. Claim model

**Detail:** [`claim-model.md`](../research/claim-model.md)

### 6.1 Definition

A **Claim** records: **Speaker S asserts proposition P**, grounded in processed (hence raw) evidence from a specific video, optionally about Event E.

- Recorded assertion **≠** verdict that P is true.  
- Compare unit for multi-telling (§13).

### 6.2 Atomicity

- Live claims: **one atomic proposition**.  
- Compounds: non-live staging only; split before live.

### 6.3 Spec-level fields (gist)

- Identity + `layer=claim` + lifecycle.  
- **Claim kinds (v1):** `world_assertion` \| `meta_speech` \| `self_report`.  
- Attribution → Person (live); provisional label path only while `proposed`.  
- `ABOUT_EVENT` preferred; **unbound claim** allowed when keys insufficient.  
- `ABOUT_TOPIC` optional sugar.  
- Grounding: EXTRACTED_FROM processed + resolvable raw anchors.  
- `PROPOSED_BY` / `APPROVED_BY` as applicable.

### 6.4 Relations (normative gist)

- Provenance: EXTRACTED_FROM, DERIVED_FROM chain, PROPOSED_BY, APPROVED_BY, SUPERSEDES.  
- Content: ABOUT_EVENT, ABOUT_TOPIC, ATTRIBUTED_TO, SUPPORTS, CONTRADICTS, SAME_ASSERTION_AS, ELABORATES (as allowed by matrices).  
- Two videos → **two claim nodes**; link with `SAME_ASSERTION_AS` if paraphrastic same assertable — never collapse ids.

### 6.5 Multi-speaker dialogue

- Attribute to the speaker who **uttered** the words (default).  
- Host framing vs guest claim remain separate nodes when both assert.  
- Host meta_speech may be UI-minimized; still not silently merged into guest.

### 6.6 Explicitly out of claim schema (v1)

Truth/verified flags; credibility scores; DB types — Appendix A / §10.

---

## 7. Event identity and Tellings

**Detail:** [`event-identity-rule.md`](../research/event-identity-rule.md)

### 7.1 Event ≠ video beat

- **Event:** real-world happening (or coherent multi-day incident / campaign parent).  
- **Beat:** in-video structural unit — organizes media, never is an Event.  
- Competing explanations of one happening stay **one Event** with multiple claims.

### 7.2 Identity keys (v1)

Weighted: public name/case label; time window; place/theater; principal actors/platforms; optional documentary anchors.

**Non-keys:** topic alone; video id; speaker who discussed it; claim wording.

### 7.3 Merge / split / nesting

- Same Event when weighted keys match the same real-world referent.  
- Split when high-stakes keys conflict without resolution.  
- Parent/child for campaign → day → encounter style nesting.  
- Multi-day: prefer one parent with optional phase children when public discourse treats one incident.

### 7.4 Uncertainty

- **Provisional identity link** + **identity open question** — never silent high-stakes auto-merge.  
- **Provisional identity bundle** for “compare as if same” without collapsing ids (§13).

### 7.5 Telling

One **account of an Event** as presented in a specific video (or continuous segment), with speakers/claims/provenance. Multiple Tellings per Event across seed channels is the multi-telling unit.

### 7.6 Authority

AI proposes Event create/merge/split; **curator** approves live identity commits.

---

## 8. Topics (vs Events)

**Detail:** [`topics-vs-events.md`](../research/topics-vs-events.md)

### 8.1 Core distinction

- **Topic:** thematic **type** (controlled taxonomy entity).  
- **Event:** instance-level **happening**.  
- Sharing a Topic never merges Events.

### 8.2 Representation

- Lightweight Topic nodes: canonical name + optional aliases + optional shallow parent.  
- Curator-owned controlled taxonomy; free strings are **surface tags** until mapped.

### 8.3 Attachment

- **Primary:** Event and Claim.  
- **Optional:** video-level aboutness for browse.  
- **Processed:** surface tags only (not live Topics until mapped + approved).

### 8.4 Programs / eras

Long-running programs and discourse eras are **Topics** in v1 (unless later split into a dedicated Program entity) — not mega-Events.

### 8.5 v1 minimum

- Seed taxonomy roughly **15–40** terms (exact strings curator-owned — Appendix A).  
- No free-tag explosion as live ontology.  
- AI proposes assignments; curator approves live.

---

## 9. Speaker identity and aliases

**Detail:** [`speaker-identity-and-alias-merge.md`](../research/speaker-identity-and-alias-merge.md)

### 9.1 Label ≠ Person

`SPEAKER_n` is episode-local. It never is a Person node and has no cross-video identity until mapped through a Person.

### 9.2 Person lifecycle

`proposed` → `candidate` → `active` | `merged-away` | `deprecated`

- Create/active requires canonical display name, identity evidence, curator approve.  
- Do not mint persons solely because diarization emitted a new label.

### 9.3 Episode attribution

- Mapping speaker label → Person (or **unresolved speaker**).  
- Seed-channel **host defaults** provisional from channel identity; still curator-gated for live claim attribution.  
- Guest from title/description/metadata + review.

### 9.4 Aliases

- Typed alternate strings for the same Person.  
- Normalization for matching ≠ changing canonical display name.  
- Channel/show brands are not person aliases.

### 9.5 Unresolved

Unknown voices, ads, audience, low-confidence clusters → unresolved. **No unknown person nodes.** No cross-video merge of unresolved labels.

### 9.6 Merge / split

- String similarity alone never live-merges.  
- Multi-signal evidence catalog; human approve for live merge.  
- Split rare; audit trail retained.

### 9.7 Confidence

Numeric thresholds guide **proposals only**; never auto-live. Prefer false reject.

---

## 10. Speaker credibility (v1)

**Detail:** [`speaker-credibility-signals-v1.md`](../research/speaker-credibility-signals-v1.md)

### 10.1 Definition

Soft research metadata about a **Person** — not identity, not epistemic layer, not claim truth.

### 10.2 In-scope signals

1. **Curator annotations** (primary).  
2. **Role labels** (descriptive: host, guest, witness-participant, secondhand, researcher/journalist, official/institutional, …) — not trust multipliers.  
3. **Consistency observations** (person × Event): agree / conflict / drift / insufficient data — derived candidates AI-proposed; live annotations curator-gated.

### 10.3 Hard forbids

No system-invented composite trust scores, reliability %, reputation scores as objective metrics in v1.

### 10.4 Separation checklist

Identity clean before credibility; same-person conflict may also appear as claim contradiction (§11) without becoming a global grade.

---

## 11. Contradiction, agreement, gaps, open questions

**Detail:** [`contradiction-and-open-question-model.md`](../research/contradiction-and-open-question-model.md)

### 11.1 Core job

On a **focus Event** (or **provisional identity bundle**), surface **agreement**, **conflict**, and **gaps**. Not a global dump of disagreements.

### 11.2 Content edges

- Participants: **claim | inference** only.  
- Predicates: `SUPPORTS`, `CONTRADICTS`, `SAME_ASSERTION_AS` (and other legal content edges from §4/§6).  
- **Assumptions never** evidence endpoints.

### 11.3 Contradiction record

First-class research object **outside** the five layers: packages conflict pairs, optional **research facet**, status, curator notes. Not a truth verdict; not an Event split.

### 11.4 Open Question

First-class research object with kinds (v1 include: identity, claim-conflict follow-up, coverage gap, key disagreement, attribution, other).

Lifecycle: `proposed` → `open` → `resolved` | `wontfix` (+ `rejected` for bad proposals).

- System/AI may propose; **only curator** opens, resolves, or wontfixes.

### 11.5 Coverage gaps

Missing assertable content on a facet under focus scope. Derived UI and/or open question of kind `coverage_gap`. Do not invent opposing claims to fill gaps. Explicit missing premise scaffolding is an **assumption**, not a gap claim.

### 11.6 Identity vs claim conflict

“Same Event as X?” is an **identity open question** / provisional link — **not** a claim contradiction.

### 11.7 Agreement

Prefer `SAME_ASSERTION_AS` and/or `SUPPORTS`. Optional agreement cluster may be **derived** for UX; not a required stored type in v1.

---

## 12. Human approval workflow

**Detail:** [`human-approval-workflow.md`](../research/human-approval-workflow.md)

### 12.1 Lifecycle (layered nodes)

`proposed` | `live` | `rejected` | `superseded`

Orthogonal to epistemic layer, person states, event provisionality, topic lifecycle.

### 12.2 Sole live gate

**Curator only** transitions gated objects to `live`. AI never sets live on gated objects.

### 12.3 Auto-land vs must-approve

| Auto-land | Must approve before live |
|-----------|---------------------------|
| Catalog raw + mechanical media-track pointers | processed, claim, inference, assumption |
| | Person create / alias / merge / episode map |
| | Event merge/split commits |
| | Topic mint / live assignment |
| | Live credibility annotations |
| | Contradiction records & open questions as live research state |

### 12.4 Live checklists

Per-object checklists in the decision asset (processed span, claim, inference, assumption, episode map/person). Implementers must not invent weaker gates.

### 12.5 Bundles, batch, atomic co-approval

- Default review unit: **video-scoped approval bundle**.  
- **Batch approve** allowed when each node passes its checklist and dependencies close.  
- **Atomic co-approval** preferred when post-state is matrix-legal.  
- Never confidence-timer auto-live; never hide layer badges.

### 12.6 Supersession

Do not patch live semantic content in place. Mint new same-layer node, `SUPERSEDES` prior, prior → `superseded`.

### 12.7 Surfaces (IA only)

Primary: approval bundle review; item drill-down; approve actions re-used from multi-telling (§13). No wireframes required for spec completeness.

---

## 13. Multi-telling product UX

**Detail:** [`multi-telling-compare-ux.md`](../research/multi-telling-compare-ux.md)

### 13.1 Dual spine

1. **Event timeline** — chronological index of world Events (by Event time window, not upload date).  
2. **Multi-telling compare** — line up Tellings for one focus.

Topics **filter** navigation only; never become compare identity.

### 13.2 Focus scope

- One **focus Event**, or  
- Explicit **provisional identity bundle**.  

Never “everything under Topic X” as one happening.

### 13.3 Default sections (IA)

**Timeline:** identity strip · chronological list · filters · provisional/duplicate hints · open-question badges · entry to compare.

**Compare:** focus header · Telling strip · Claims board · Agreement · Conflict · Gaps & open questions · Provenance/media · optional scaffolding & credibility side panels.

### 13.4 Comparison dimensions (must answer)

Who (Person) · What (`claim_text`) · When said (video + timestamp) · About when/where (Event keys / facet) · Agreement · Conflict · Gaps · Provenance path · Lifecycle badge.

### 13.5 Minimum actions (v1 must)

1. **Approve claim** (reuses §12 checklists).  
2. **Mark open question**.  
3. **Jump to timestamp** via claim → processed → raw; disabled if grounding incomplete.

Strongly recommended: reject; bind to Event; mark same-assertion; open/resolve contradiction; switch confirmed vs provisional mode; navigate parent/child Events.

### 13.6 Forbidden patterns

- Assumptions as evidence/conflict rows.  
- Trust-ranked speaker cards as primary compare unit.  
- Silent proposed-as-live evidence.  
- Topic-as-Event compare scope.  
- Jump inventing times without grounding path.

### 13.7 Visibility

Default: **live** claims and open research objects. Proposed only in review overlay / provisional mode.

### 13.8 Seed pilot framing

Jesse Michels · Area52 · Danny Jones multi-telling density is the design pilot (shared guests/cases). Not an exhaustive corpus requirement for IA correctness.

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

Channel · Video (catalog) · Person · Alias · Event · Topic · (Telling as modeling concept / grouping) · Extraction run · Speaker label (episode-local, not entity identity)

### 14.3 Research / workflow objects

Contradiction record · Open Question · Consistency observation · Approval bundle · Provisional identity link · Provisional identity bundle · Episode map / attribution

### 14.4 Edge catalog (minimum families)

- **Provenance:** DERIVED_FROM, EXTRACTED_FROM, GROUNDED_IN (sugar only with full path), RESTS_ON, PROPOSED_BY, APPROVED_BY, SUPERSEDES, run linkage  
- **Content:** ABOUT_EVENT, ABOUT_TOPIC, ATTRIBUTED_TO, SUPPORTS, CONTRADICTS, SAME_ASSERTION_AS, ELABORATES (as allowed)  
- **Identity:** provisional identity links; person merge audit  

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

---

## 15. Worked scenarios (normative intent)

Full narratives: research assets. Spec requires these **pass/fail intents**.

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
| Remaining pilot video picks | Curator operational | Does not reopen §1.2 |
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

## Document history

| Date | Change |
|------|--------|
| 2026-07-22 | Skeleton created from closed wayfinder decisions + `spec-document-outline.md`. Status: `skeleton`. |
