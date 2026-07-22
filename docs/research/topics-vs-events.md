# Topics vs events relationship

Decision asset for [Topics vs events relationship](https://github.com/etai83/uap-kg/issues/11)  
Part of [Wayfinder: UAP YouTube knowledge graph spec](https://github.com/etai83/uap-kg/issues/1)

**Depends on:** [Event identity rule](./event-identity-rule.md) (#4), [Epistemic layer ontology](./epistemic-layer-ontology.md) (#3)  
**Status:** Recommended decision (batch defaults; aligned to standing map preferences).  
**Scope:** Spec-level ontology only — no storage schema, API, or implementation code.  
**Downstream consumers:** Claim model (#6), Multi-telling compare UX (#14), Contradiction / open question (#8), any browse/filter UI.

---

## Question

How do **topics discussed** relate to **real-world events** in the model?

Decide: topics as free tags, controlled taxonomy, or nodes; whether topics hang off videos, claims, events, or all three; v1 minimum.

---

## Decision summary

| Axis | Decision |
|------|----------|
| Topic vs Event | **Topics are thematic types**; **Events are instance happenings**. Never collapse one into the other |
| Representation | **Lightweight Topic nodes** (entities outside the five epistemic layers), not free-text-only strings on live graph edges |
| Vocabulary for v1 | **Small controlled taxonomy** (curator-owned seed list + aliases). AI may propose free surface strings that map into the taxonomy; free strings alone do **not** mint live Topics |
| Primary attachment | **Event** and **Claim** (and optionally Inference) via content edges `ABOUT_TOPIC` |
| Optional attachment | **Video** (catalog-level “episode is largely about…”) for browse only; **processed** spans may carry **surface tags** that are not yet Topic nodes |
| Non-attachment for identity | Topics are **explicit non-keys** for Event sameness (per #4). Sharing a topic never merges Events |
| Hierarchy | **Shallow optional parent** on Topics only (e.g. `UAP encounters` → `Navy UAP`). No deep ontology engineering in v1 |
| Programs / eras | Long-running programs and discourse eras (e.g. “AAWSAP/AATIP”, “disclosure”) are **Topics** (or later dedicated Program entities) — **not** mega-Events |
| Live gate | AI proposes topic assignments; **curator approves** before live (same standing preference as other extractions). Taxonomy term create/edit is curator-owned |
| v1 minimum | Seed taxonomy ~15–40 terms; Event + Claim primary links; optional Video aboutness; no free-tag explosion; no topic-driven Event collapse |

---

## Core distinction (non-negotiable)

| Concept | What it is | Example | What it is **not** |
|---------|------------|---------|---------------------|
| **Event** | A particular real-world happening (or coherent multi-day incident) with identity keys (name, time, place, actors…) | *Nimitz* / Tic Tac encounters (≈ Nov 2004, SOCAL) | A theme, a YouTube chapter, “everything about Navy UAP” |
| **Topic** | A **type / theme** of discussion used to index and filter | `Navy UAP`, `crash retrieval`, `Moon anomalies`, `congressional UAP hearings` | A single incident; a substitute Event ID |
| **Telling** | One video’s (or segment’s) account of an Event | Fravor on Danny Jones recounting Tic Tac | A topic bucket |
| **Claim** | An attributed, checkable assertion (epistemic layer) | “The object had no exhaust plume” | A topic label |

**Primary job alignment:** reconstruct and cross-check story across channels. The UX spine remains **event timeline + multi-telling compare**. Topics are **navigation and clustering aids**, not the spine. Multi-telling is always scoped to a **focus Event** (or provisional identity bundle), never to “everything under topic X” as if that were one happening.

### Anti-collapse rules

1. **Do not mint a mega-Event** from a topic (“all Moon censorship”, “all crash retrievals”, “the disclosure process”).
2. **Do not merge Events** because they share topics (anti-key already in #4).
3. **Do not reify a general thesis** as an Event: “NASA has long censored Moon anomalies” is a **claim cluster under a Topic**, plus zero or more **specific Events** (mission/frame/date) when keys exist.
4. **Do not force multi-year programs into one Event.** Prefer Topic (and optional Program entity later); attach discrete hearings, leaks, and ops as separate Events that `ABOUT_TOPIC` the program theme.

---

## Representation: controlled taxonomy as Topic nodes

### Why not free tags only (v1)

Free tags alone fragment a ~30-video pilot (`disclosure` / `Disclosure` / `gov disclosure` / `UAP disclosure`) and make multi-channel browse unreliable. They remain useful as **provisional surface strings** during extraction, but live graph membership requires a **taxonomy term**.

### Why not a heavy open ontology (v1)

Full hierarchical knowledge-engineering (SKOS world models, dozens of relations) is out of scope for a personal pilot. We need **consistent filters**, not a publication-grade thesaurus.

### Chosen middle: lightweight Topic entity + controlled seed list

| Property (spec-level) | Rule |
|----------------------|------|
| Kind | **Entity node** outside the five epistemic layers (same family as Person, Channel, Event-as-identity) |
| Fields (conceptual) | Canonical display name; optional aliases; optional single parent Topic; short description; lifecycle `proposed` \| `live` \| `deprecated` |
| Machine id | Stable id once live; display name may change without changing identity |
| Aliases | Normalize synonyms into one Topic (`Tic Tac motif` is **not** an Event alias — motif language maps to Topic `UAP craft morphology` or similar; named cases stay Events) |
| Create | Curator-owned for seed list; AI may **propose** new terms; no silent mint of live Topics from free text |
| Deprecate | Soft-hide; reassign edges rather than delete history |

### Seed taxonomy guidance (illustrative, not frozen catalog)

Curator locks the actual list at pilot time. Illustrative clusters for this discourse:

| Cluster | Example terms |
|---------|----------------|
| Encounter / sensor | `Navy UAP`, `military encounters`, `civilian sightings`, `sensor / FLIR` |
| Case families (as themes) | Use **sparingly** as topics only when discourse is thematic; prefer Event nodes for named cases |
| Programs / orgs | `AATIP / AAWSAP`, `legacy crash-retrieval claims`, `special access programs` |
| Disclosure / politics | `congressional UAP hearings`, `whistleblowers`, `FOIA / declassification` |
| Cosmology / fringe adjacents (pilot-adjacent) | `Moon / Apollo anomalies`, `consciousness / NHI`, `historical civilization claims` |
| Epistemic method | `witness testimony`, `document analysis`, `skepticism / prosaic explanations` |

**Size target for v1:** roughly **15–40 live terms**. Prefer merging near-duplicates over growing the list. New terms require curator approval.

---

## Where Topics attach

### Primary (required capability in v1)

| Endpoint | Edge (content) | Purpose |
|----------|----------------|---------|
| **Event → Topic** | Event `ABOUT_TOPIC` Topic (or inverse query) | Theme index on the timeline: “show Events tagged Navy UAP” without merging them |
| **Claim → Topic** | Claim `ABOUT_TOPIC` Topic | Cross-telling thematic compare of assertions that may or may not yet bind cleanly to an Event |

Also allowed (already sketched in #3): **Inference → Topic** when an inference is explicitly about a theme rather than only about an Event.

**Cardinality:** many-to-many. One Event or Claim may have several Topics; one Topic indexes many Events/Claims.

**Confidence / provenance:** topic assignment may be AI-proposed with confidence; live assignment is curator-gated. Provenance fields belong to #7; this ticket only requires that assignment is not silent auto-live.

### Optional (nice-to-have in v1; do not block pilot)

| Endpoint | Role | Rule |
|----------|------|------|
| **Video → Topic** | Catalog-level aboutness (“this episode is largely about X”) | Optional; **never** replaces Event/Claim links. Useful for pilot video selection and browse. A video discussing five Events should still have those Events linked; video-level topics are coarse. |
| **Processed span → surface tag** | Extraction aid | Per #3: surface topic tags on a span stay at **processed** layer. They are **not** live Topic nodes until mapped via `ABOUT_TOPIC` (or promoted assignment) to taxonomy terms. Free surface strings may remain for search but do not define the taxonomy. |

### Explicit non-primary

| Do not treat as primary | Why |
|-------------------------|-----|
| Topic as only home for a claim that has a clear Event | Prefer Claim `ABOUT_EVENT` when the referent is a happening; Topic is additional indexing |
| Topic hanging only off Person | “This person always talks about X” is out of v1 scope (optional later as derived facet) |
| Topic as Event identity key | Forbidden (#4) |

### Recommended default extraction path

```
processed utterance/span
  → (optional) surface tag strings
  → propose Claim (+ ABOUT_EVENT when keys exist)
  → propose ABOUT_TOPIC on Claim and/or Event
  → curator approves live Topics + edges
```

If a speaker asserts a general thesis with **no** fixable Event keys, create **Claim(s) + Topic** and **do not** invent a mega-Event.

---

## Relation model (Event × Topic × Claim)

```
Topic (type/theme)          Event (instance happening)
   ▲                            ▲
   │ ABOUT_TOPIC                │ ABOUT_EVENT
   │                            │
 Claim / Inference ─────────────┘
        │
        └── EXTRACTED_FROM → processed → raw (video anchors)
```

| Pattern | Model |
|---------|--------|
| Named case discussed under a theme | Event *Nimitz* 2004 `ABOUT_TOPIC` `Navy UAP`; Claims `ABOUT_EVENT` that Event (and may also `ABOUT_TOPIC`) |
| General thesis, no single incident | Claims `ABOUT_TOPIC` `Moon / Apollo anomalies`; **no** single Event “all censorship” |
| Hearing about past cases | Hearing = its own Event; related to prior encounter Events; Topics e.g. `congressional UAP hearings` + `whistleblowers` |
| Program-era discourse | Topic `AATIP / AAWSAP`; individual ops/testimony = Events; not one Event for the whole program |
| Same motif, different incidents | Shared Topic (e.g. craft morphology); **distinct Events** when keys differ |

### Multi-telling and topics

- **Compare UX (#14)** remains Event-scoped (confirmed Event or provisional bundle).
- Topics may **filter the Event list** or **filter claims inside a compare**, but “compare topic X” is **not** a substitute for Event identity.
- Cross-topic claim browse is allowed as a secondary research view; it must not imply shared identity of underlying happenings.

---

## Controlled taxonomy vs free tags (final pick)

| Option | v1 verdict |
|--------|------------|
| Free tags only | **Reject** as sole live model |
| Heavy formal ontology | **Reject** for v1 scope |
| **Controlled taxonomy as Topic nodes** | **Adopt** |
| Free surface strings at processed | **Allow** as extraction assist only |
| AI-proposed new taxonomy terms | **Allow** as proposals; curator commits |

**Normalization light rules:**

- Case-fold and trivial punctuation do not create new Topics.
- Aliases map to one Topic (`crash retrievals` ≈ `legacy crash retrieval program claims` if curator so binds).
- Prefer curator merge of near-duplicate Topics over parallel live synonyms.

---

## v1 minimum (personal pilot: 3 channels, ~30 videos)

Must have:

1. Distinction Event ≠ Topic documented and enforced in write rules (no topic-as-event minting).
2. Topic entity with canonical name + optional aliases + optional single parent.
3. Seed controlled list (~15–40 terms), curator-editable.
4. Live edges: **Event–Topic** and **Claim–Topic** (`ABOUT_TOPIC`).
5. AI propose / curator approve for assignments and new terms.
6. Topics excluded from Event sameness keys.

Nice-to-have (same pilot, not blockers):

7. Video-level Topic aboutness for browse.
8. Processed surface tags before taxonomy mapping.
9. Inference `ABOUT_TOPIC`.
10. Shallow Topic parent for filters (one level).

Explicitly deferred:

- Program / Organization entity type separate from Topic (may peel off later from program-like Topics).
- Automatic topic clustering / embedding-only live writes.
- Public taxonomy publication or multi-user vocabulary governance.
- Deep SKOS-style relations (broader/narrower beyond one parent, related-match pipelines).

---

## Worked examples (pilot-adjacent)

### 1) *Nimitz* / Tic Tac across channels

| Object | Modeling |
|--------|----------|
| Happening | **Event:** *Nimitz* / Tic Tac (2004) with keys from #4 |
| Themes | Topics: `Navy UAP`, `military encounters`, optionally `sensor / FLIR` |
| Videos | Each interview/synthesis is a **Telling** source; optional Video `ABOUT_TOPIC` `Navy UAP` |
| Claims | e.g. kinematics claims `ABOUT_EVENT` Nimitz; may also `ABOUT_TOPIC` `Navy UAP` |

**Illegal:** One Event node “all Navy UAP.”

### 2) Jesse Michels — NASA Moon photo censorship (pilot pool video)

| Referent | Model |
|----------|--------|
| Specific mission/frame/date if fixed | **Event(s)** + Topic `Moon / Apollo anomalies` |
| General “NASA censored Moon anomalies” thesis | **Claims** + Topic; **not** one mega-Event |
| Multi-telling later | Only when multiple Tellings share the **same Event keys** |

### 3) TD Barnes / Area 51 (Danny Jones pilot pool)

| Referent | Model |
|----------|--------|
| Discrete recounted happenings | Separate **Events** when time/place/actors differ |
| “Area 51 work / special access culture” as theme | **Topic** (e.g. program/facility theme); not one Event for a career |
| Claims about a specific VIP visit or test | Claim → that Event (+ Topics) |

### 4) Grusch / 2023 hearings

| Happening | Event | Topics (examples) |
|-----------|-------|-------------------|
| 26 July 2023 House hearing | Its own Event | `congressional UAP hearings`, `whistleblowers` |
| Closed SSCI sessions | Distinct Event(s) | same Topics; **not** merged via topic |
| Alleged retrieval programs as general discourse | Claims + Topic `legacy crash-retrieval claims`; specific alleged retrievals become Events only when keys support it |

---

## Implications for blocked / related tickets

| Ticket | Implication |
|--------|-------------|
| **#4 Event identity** | Confirmed: Topics are types; Events are instances; topics remain non-keys. Mega-Event anti-patterns reinforced. |
| **#3 Epistemic layer** | `ABOUT_TOPIC` endpoints refined: primary Claim \| Inference \| Event-entity; processed keeps **surface tags** only until mapped. Topic entity has no `layer`. |
| **#6 Claim model** | Claims should support optional multi-Topic links; Event link remains preferred when a happening is identified; unbound thematic claims are valid. |
| **#8 Contradiction** | Claim conflicts stay on shared Event or explicit claim–claim edges; two claims under the same Topic alone are **not** automatic contradictions about one happening. |
| **#14 Multi-telling UX** | Spine stays Event-scoped; Topics are filters and secondary browse, not compare identity. |
| **#7 Provenance** | Topic assignment should record proposer/approver like other extractions (fields deferred to #7). |

---

## Out of scope for this decision

- Graph database schema / ID format
- Exact seed term list freeze (curator at pilot load)
- Embedding or classifier choice for auto-suggest
- Program / Organization entity beyond “use Topic for now”
- Credibility or truth of topical claims (#10, claim/epistemic work)

---

## Decision log

| Date | Decision |
|------|----------|
| 2026-07-22 | Adopt Topic as thematic type (lightweight entity + controlled taxonomy); Event remains instance happening; primary attachments Event + Claim; optional Video / processed surface tags; forbid topic-driven mega-Events and topic-based Event merge; v1 sized for ~30-video personal pilot. |

## Profile / decision date

Decided 2026-07-22 for the wayfinder spec. Spec-only; no implementation. Recommended decision via batch defaults (no interactive grilling).
