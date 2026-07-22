# Epistemic layer ontology

Decision asset for [Epistemic layer ontology](https://github.com/etai83/uap-kg/issues/3)  
Part of [Wayfinder: UAP YouTube knowledge graph spec](https://github.com/etai83/uap-kg/issues/1)

**Status:** Recommended decision (batch grilling with defaults aligned to standing map preferences).  
**Scope:** Spec-level ontology only — no storage schema, API, or implementation code.  
**Downstream consumers:** Claim model (#6), Provenance minimum (#7), Human approval workflow (#9), Contradiction model (#8).

---

## Decision summary

| Axis | Decision |
|------|----------|
| Layer spine | **Five hard types, ordered:** `raw` → `processed` → `claim` → `inference` → `assumption` |
| Canonical names | Keep ticket names as machine ids; Title Case in prose. **No renames.** |
| What is typed | **Nodes** carry a single required `layer` enum. **Edges** do not have a layer; they have an `edge_kind` (provenance vs content) and a typed predicate with legal endpoint constraints. |
| Layer mutability | **Layer is immutable** after a node is created. “Promotion” never rewrites type in place; it creates a **new** higher-layer node with a provenance edge to the lower one (and optional supersession of a prior proposal). |
| Live gate | **Curator** is sole human approver. AI may **propose** any non-catalog extraction; nothing extraction-derived is **live** without curator approval. |
| Catalog exception | **Raw catalog** nodes from official YouTube metadata (channel, video identity, public stats snapshot) may enter live without claim-level approval. Everything derived from speech/text extraction still gates. |
| Illegal masquerade | Assumption must never appear as claim or inference; inference must never appear as claim; claim must never appear as raw/processed. UI and write-path reject illegal type pairs. |

---

## Canonical names and one-line definitions

Machine id is the only legal value of a node’s `layer` field.

| Order | Machine id | Display name | One-line definition |
|------:|------------|--------------|---------------------|
| 1 | `raw` | Raw | Uninterpreted source capture: official catalog facts and immutable media anchors (video identity, timestamps, caption/ASR bytes reference, diarization turn ids). |
| 2 | `processed` | Processed | Normalized structure derived from raw **without asserting world-truth**: cleaned spans, speaker-attributed utterances, segment boundaries, surface topic tags on a span. |
| 3 | `claim` | Claim | An attributed, checkable assertion about the world **or** a speaker’s explicit assertion, grounded in processed (hence raw) evidence. |
| 4 | `inference` | Inference | A conclusion **not stated as such** in the source, derived by explicit reasoning from one or more claims (and optionally other live inferences). |
| 5 | `assumption` | Assumption | A provisional premise adopted to scaffold analysis; **not** established by source text or valid inference chain. |

### What each layer is *for* (research job)

| Layer | Job in “reconstruct & cross-check narratives” |
|-------|-----------------------------------------------|
| Raw | Anchor every later node to *where it came from* (which video, which time range, which track). |
| Processed | Make speech/text queryable and attributable (“who said what, when”) without deciding truth. |
| Claim | Unit of narrative comparison across tellings, speakers, and videos. |
| Inference | Explicit curator/AI reasoning steps that go beyond the transcript. |
| Assumption | Make gaps visible instead of smuggling them into claims. |

### Explicit non-goals of each layer

| Layer | Is **not** |
|-------|------------|
| Raw | A paraphrase, summary, or “what they meant.” |
| Processed | Evidence that something in the world is true. |
| Claim | The system’s belief that the proposition is true (claims are *recorded assertions*, not verdicts). |
| Inference | A re-label of a quote; if the speaker said it, it is a claim (or processed utterance), not an inference. |
| Assumption | A soft claim. It has no source quote that asserts it. |

---

## Node vs edge enforcement

### Nodes

1. Every epistemic content node has exactly one `layer ∈ {raw, processed, claim, inference, assumption}`.
2. Layer is set at create time and **cannot be patched**. Wrong layer ⇒ reject write or create a different node.
3. Nodes also carry lifecycle state orthogonal to layer: at minimum **`proposed` | `live` | `rejected` | `superseded`** (exact workflow belongs to #9; ontology requires the distinction).
4. **Entity nodes that are not epistemic propositions** (Person, Channel, Video-as-catalog-object, Event-as-world-happening identity) sit **outside** the five-layer spine. They may be *linked to* layered nodes but do not themselves have `layer`. (Event identity and speaker identity are separate tickets; this ontology only forbids putting “Person” or “Event” *inside* the five epistemic layers.)

### Edges

Edges are typed by **`edge_kind`** + **predicate**:

| edge_kind | Role | Layer rule |
|-----------|------|------------|
| **provenance** | “This node exists because of that node / actor / process.” | Endpoints must satisfy the **provenance legal matrix** below. |
| **content** | Semantic relations among propositions and entities (about, supports, contradicts, co-refers, etc.). | Endpoints must satisfy the **content legal matrix** below. Content edges never rewrite layer. |

**Enforcement locus (spec requirement):**

- Write path validates `(source.layer, predicate, target.layer)` (or entity target) against the matrices.
- Illegal pairs are hard errors, not warnings.
- UI surfaces layer badges from the **node** field only; edge labels never imply a layer upgrade.

---

## Provenance edges (legal matrix)

Provenance predicates (v1 set — Claim model / Provenance tickets may add fields, not loosen layer rules):

| Predicate | Meaning | Legal source → target | Notes |
|-----------|---------|----------------------|-------|
| `DERIVED_FROM` | Structural derivation | `processed` → `raw` | e.g. utterance span from transcript track + video |
| `EXTRACTED_FROM` | Proposition pulled from structured speech/text | `claim` → `processed` | Primary grounding of claims in utterances/spans |
| `GROUNDED_IN` | Multi-hop or aggregate grounding (optional sugar) | `claim` → `raw` | Allowed **only if** a path claim→processed→raw also exists or is created in the same write; never a substitute for missing processed |
| `BASED_ON` | Inference premises | `inference` → `claim` or `inference` → `inference` | At least one `BASED_ON` claim required for live inference |
| `RESTS_ON` | Explicit scaffolding | `inference` → `assumption` or `claim` → `assumption` (rare) | Marks that the upper node depends on an unproven premise |
| `PROPOSED_BY` | Agent provenance | any layered node → Agent/System identity | Not a layer endpoint; actor ref |
| `APPROVED_BY` | Human gate record | any layered node → Curator identity | Required transition into `live` for gated layers |
| `SUPERSEDES` | Versioning among same-layer nodes | same layer → same layer | e.g. revised claim wording; does not change layer |

### Illegal provenance (hard reject)

| From → To | Why illegal |
|-----------|-------------|
| `assumption` → `claim` via any “is-a” or silent upgrade | Assumption must not masquerade as claim |
| `inference` → `claim` via promotion edge | Inferences are not source-grounded assertions; re-assert from evidence as a new claim if the speaker actually said it |
| `claim` → `raw` only, with no processed path | Skips attribution structure; breaks “who said what” |
| `processed` → `claim` (as if processed were a claim) | Wrong direction and wrong type role |
| Any edge that treats layer as mutable | No `PROMOTED_TO` that rewrites the same node id’s layer |
| `raw` → anything as “derived content” | Raw does not derive from higher layers |

**Direction convention:** provenance arrows point **from dependent → support** (the claim `EXTRACTED_FROM` the utterance; the inference `BASED_ON` the claim). Content edges may use either narrative direction as defined per predicate, but must document it.

---

## Content edges (legal matrix)

Content predicates relate meaning. They do **not** establish epistemic rank.

| Predicate (illustrative v1) | Typical endpoints | Allowed? |
|----------------------------|-------------------|----------|
| `ABOUT_EVENT` | `claim` \| `inference` → Event entity | Yes |
| `ABOUT_TOPIC` | `claim` \| `inference` \| `processed` → Topic | Yes (topics ticket may refine) |
| `ATTRIBUTED_TO` | `claim` \| `processed` → Person | Yes; person writes still human-gated per prior decision |
| `SUPPORTS` | `claim`\|`inference` → `claim`\|`inference` | Yes |
| `CONTRADICTS` | `claim`\|`inference` → `claim`\|`inference` | Yes |
| `ELABORATES` | `claim` → `claim` | Yes |
| `SAME_ASSERTION_AS` | `claim` → `claim` | Yes (cross-video paraphrase link; still two claims) |
| `SUPPORTS` / `CONTRADICTS` involving `assumption` | `assumption` as endpoint | **No** as if it were evidence; assumptions only connect via `RESTS_ON` provenance |
| Content edge from `raw` asserting world truth | `raw` → Event as “this happened” | **No** — raw only anchors; use claim |

Contradiction modeling detail is ticket #8; this matrix only freezes **which layers may participate**.

---

## Promotion, human gates, and AI rights

### Definitions

- **Propose:** write a node (and edges) in state `proposed`. Visible to curator; **not** used as live graph evidence in default research views.
- **Live:** curator-approved; participates in multi-telling compare, timelines, and default queries.
- **Promotion:** creating a **new** node at a higher layer with legal provenance to lower support — never flipping `layer` on an existing id.

### What AI may do vs what requires curator action

| Action | AI may propose? | Curator required before live? |
|--------|-----------------|-------------------------------|
| Ingest raw **catalog** (channel, video metadata via official API) | System may write | **No** (catalog exception) |
| Attach raw media anchors (time range refs, track ids) tied to catalog video | System may write | **No** if purely mechanical; **Yes** if identity is interpretive |
| Create `processed` utterance / span / diarized turn mapping | Yes | **Yes** |
| Map diarization label → Person node | Yes | **Yes** (prior: human confirm before person-node writes) |
| Create `claim` from processed span | Yes | **Yes** |
| Create `inference` from claims | Yes | **Yes** |
| Create `assumption` | Yes (or curator-authored) | **Yes** to be live scaffolding |
| Mark claim true/false / credibility score | Out of scope for this ontology; if present later, **curator-owned** | **Yes** |
| Auto-publish any extraction as live | **No** | N/A — forbidden by standing preference |

### What may never be promoted without human action

These are **always** human-gated; AI cannot complete them to live state:

1. Any `processed`, `claim`, `inference`, or `assumption` node becoming **live**.
2. Any **Person** identity commit or merge used as attribution target (per speaker decision).
3. Any attempt to treat an **assumption** as a **claim** (must mint a new claim from source evidence, not promote).
4. Any attempt to treat an **inference** as a **claim** (same rule).
5. Bulk “approve all” of mixed layers in a way that hides layer badges (workflow #9 may allow bulk approve, but each node retains its true layer).

### Illegal promotions (summary)

| Forbidden transition | Correct alternative |
|--------------------|---------------------|
| assumption ⇢ claim (same node or silent relabel) | Leave assumption; if source actually states it, create **new** claim `EXTRACTED_FROM` processed |
| inference ⇢ claim | If the speaker said it, extract claim from processed; if not, keep inference |
| processed ⇢ claim without extraction + approval | Create claim node with `EXTRACTED_FROM` + curator approve |
| claim ⇢ inference without new reasoning node | Create inference with `BASED_ON` edges and stated rationale |
| anything ⇢ raw | Impossible; raw is source-side only |

---

## Lifecycle × layer (write rules)

| Layer | Create as proposed | Create as live | In-place layer change |
|-------|--------------------|----------------|------------------------|
| `raw` (catalog) | Optional | Allowed | Forbidden |
| `raw` (interpretive anchor) | Default | Only after curator if interpretive | Forbidden |
| `processed` | Default for AI | Only via approval | Forbidden |
| `claim` | Default for AI | Only via approval | Forbidden |
| `inference` | Default for AI | Only via approval; requires ≥1 live (or co-approved) `BASED_ON` claim | Forbidden |
| `assumption` | Default | Only via approval | Forbidden |

A live inference may not depend solely on proposed claims. Spec rule: **all `BASED_ON` / `RESTS_ON` supports must be live** for the inference to be live (or approved in the same atomic curator action).

---

## Worked examples (UAP interview context)

Examples use seed-set style content (illustrative; not corpus commitments).

### Example A — Guest factual assertion → claim

**Video:** Danny Jones interview with TD Barnes (pilot pool example).  
**Transcript span (raw):** caption/ASR bytes for video `5hhKLqUbrYQ`, t=01:12:40–01:12:55.  
**Processed:** utterance U1, `ATTRIBUTED_TO` Person?TD_Barnes (proposed until curator confirms), text: *“There were 23 of us…”*  
**Claim C1 (proposed → live on approve):** *Speaker TD Barnes asserts that twenty-three people were involved in [the relevant Area 51 cohort / program under discussion].*  
**Edges:** C1 `EXTRACTED_FROM` U1; U1 `DERIVED_FROM` raw track; C1 `ATTRIBUTED_TO` Person?TD_Barnes; C1 `ABOUT_EVENT` Event?Area51_program (event identity per #4).

**Illegal:** Writing C1 as `layer=inference` because “we’re not sure.” Uncertainty is a claim property / open-question (#8), not a layer downgrade of a direct quote.

### Example B — Host framing vs guest claim

**Video:** Area52 panel with Jesse Michels.  
**Processed U2 (host):** “So you’re saying the craft was non-human.”  
**Processed U3 (guest):** “I’m saying the materials analysis is inconsistent with known alloys.”  

| Node | Layer | Text / content |
|------|-------|----------------|
| C2 | claim | Host asserts that guest asserted non-human craft (meta-claim about conversation) — only if product keeps host paraphrases; else leave as processed only |
| C3 | claim | Guest asserts materials analysis inconsistent with known alloys |

**Rule of thumb:** Prefer claims that track **what the attributed speaker actually asserted**. Host paraphrase is either processed-only or a separate claim about the host’s speech — never silently merged into the guest’s claim.

### Example C — Inference (beyond the transcript)

**Live claims:** C3 (materials inconsistent…); C4 (guest asserts sample chain of custody to lab X).  
**Inference I1:** *If C3 and C4 are accurate, lab X possessed anomalous material samples.*  
**Edges:** I1 `BASED_ON` C3; I1 `BASED_ON` C4.  
**Not a claim:** No speaker said the conditional conclusion in those words as a world assertion in the grounding spans.

### Example D — Assumption (gap made visible)

**Inference I2:** Cross-video synthesis that two descriptions refer to the same craft retrieval.  
**Assumption A1:** *Place-name “the ranch” in video A co-refers to Skinwalker Ranch as named in video B.*  
**Edges:** I2 `RESTS_ON` A1; I2 `BASED_ON` claims…  

**Illegal:** Creating claim C_x “It was Skinwalker Ranch” with no speaker saying so, labeled as claim. That is A1 or a curator-owned claim with empty extraction (forbidden — claims require `EXTRACTED_FROM` processed).

### Example E — Raw catalog vs extraction

**Raw catalog:** Video node for Jesse Michels upload `uVVqFg2v7ro`, title, channel id, publishedAt — **live** via API ingest.  
**Raw anchor:** transcript track ref + time codes.  
**Processed / claims about NASA moon-photo censorship:** all **proposed** until curator approves.

---

## Downstream contracts (for blocked tickets)

### Claim model (#6) may assume

- Claims are always `layer=claim`.
- Every live claim has ≥1 `EXTRACTED_FROM` → `processed` (and processed → raw path).
- Attribution is via content/provenance to Person, not by overloading layer.
- Claims do not encode system truth values; optional status fields are separate.

### Provenance minimum (#7) may assume

- Provenance predicates and dependent→support direction above.
- Layer matrices are normative; provenance ticket adds required *fields* (tool version, model id, time, span offsets), not new silent promotions.

### Human approval workflow (#9) may assume

- Lifecycle states include at least proposed/live/rejected/superseded.
- Curator is sole approver.
- Catalog raw exception as specified.
- Atomic multi-node approve allowed if all endpoints remain matrix-legal when live.

### Contradiction / multi-telling (#8, #14) may assume

- Compare units are primarily **live claims** (and optionally live inferences, clearly badged).
- Assumptions never enter support/contradict tables as evidence.

---

## Open items deliberately out of this ticket

- Exact claim schema fields (polarity, modality, confidence UI) — #6  
- Minimum provenance field set — #7  
- Approval UX steps and queues — #9  
- Event identity — #4  
- Speaker merge rules — #5  
- Whether host paraphrases are first-class claims by default — product preference; default here: **attribute to the speaker who uttered the words**  

---

## Decision log

| Date | Decision |
|------|----------|
| 2026-07-22 | Adopt five-layer spine with canonical machine ids `raw`, `processed`, `claim`, `inference`, `assumption`; node-enforced immutable layer; provenance vs content edges; curator live gate for all extractions; catalog raw exception; illegal assumption/inference masquerade rules. |
