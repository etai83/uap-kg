# Contradiction and open-question model

Decision asset for [Contradiction and open-question model](https://github.com/etai83/uap-kg/issues/8)  
Part of [Wayfinder: UAP YouTube knowledge graph spec](https://github.com/etai83/uap-kg/issues/1)

**Depends on:** [Epistemic layer ontology](./epistemic-layer-ontology.md) (#3), [Event identity rule](./event-identity-rule.md) (#4), [Claim model](./claim-model.md) (#6), [Topics vs events](./topics-vs-events.md) (#11)  
**Related:** [Speaker credibility signals (v1)](./speaker-credibility-signals-v1.md) (#10), [Provenance minimum](./provenance-minimum.md) (#7)  
**Status:** Recommended decision (batch defaults; aligned to standing map preferences).  
**Scope:** Spec-level model for contradictions, gaps, and open questions so multi-telling compare can surface agreement, conflict, and missing coverage. No DB columns, API, or implementation code.  
**Downstream consumers:** Multi-telling compare UX (#14), Human approval workflow (#9), optional consistency observations (#10).

---

## Question

How does the system represent **contradictions**, **gaps**, and **open questions** so multi-telling compare can surface them?

Decide: first-class node types vs derived views, who may create open questions (system vs human), and lifecycle (open → resolved / wontfix).

---

## Decision summary

| Axis | Decision |
|------|----------|
| Core job | Multi-telling compare must surface **agreement**, **conflict**, and **gaps** on a focus **Event** (or explicit **provisional identity bundle**) — not a global dump of disagreements |
| Graph primitives | Content edges remain first-class: `SUPPORTS`, `CONTRADICTS`, `SAME_ASSERTION_AS` among **claim \| inference** only. **Assumptions never participate as evidence endpoints** |
| Contradiction packaging | **First-class Contradiction records** (research objects **outside** the five epistemic layers) package one or more conflict pairs for lifecycle, curator notes, and UX — not derived-only ephemeral query rows |
| Open questions | **First-class Open Question** research objects (also outside the five layers), with typed kinds and lifecycle **proposed → open → resolved \| wontfix** (plus **rejected** for bad proposals) |
| Gaps | **Coverage gaps** are first-class only when promoted to an Open Question (or an Assumption when scaffolding is explicit). Pure absence may be **derived** for UI (“no claim yet on facet X”) |
| Identity vs claim conflict | **Identity open questions** (“same Event as X?”) are **not** claim contradictions. Claim contradictions require competing propositions about a shared focus Event / provisional bundle |
| Who creates | **AI / system detect candidates** → `proposed`; **curator opens** (creates or promotes to live `open`) and alone **resolves / wontfix**; curator may author from scratch |
| Live gate | Standing preference: AI propose; **curator approve** before default multi-telling views treat records as live research state |
| Assumptions | May make gaps **visible** via `RESTS_ON`; **never** count as evidence in contradiction pairs or support edges |
| Agreement | Prefer `SAME_ASSERTION_AS` (paraphrase same assertable) and/or `SUPPORTS`; optional Agreement cluster is **derived** for UX — not required as a stored type in v1 |

---

## Core principle

> **Claims (and optional inferences) are the compare units. Contradiction records and open questions are curator-gated research annotations that make conflict and missing knowledge durable — without inventing a sixth epistemic layer or smuggling assumptions into evidence.**

Standing contracts honored:

- Compare units are primarily **live atomic claims**; live inferences may participate **clearly badged** (#3, #6).
- Assumptions **never** enter `SUPPORTS` / `CONTRADICTS` tables as evidence (#3).
- Competing explanations of one happening stay on **one Event**; identity uncertainty uses **provisional links + identity open questions**, not claim-contradiction collapse (#4).
- Shared **Topic alone** never implies two claims contradict each other about one happening (#11).
- Same-person conflict may **also** feed person×event consistency observations (#10); cross-person conflict lives primarily here.

---

## Three surfaces multi-telling needs

| Surface | What the curator sees | Graph home |
|---------|----------------------|------------|
| **Agreement** | Tellings that say (roughly) the same thing | `SAME_ASSERTION_AS`, `SUPPORTS`; optional derived agreement clusters |
| **Conflict** | Tellings that cannot both be true under a shared facet / polarity | `CONTRADICTS` edges + **Contradiction records** |
| **Gaps** | What nobody asserted (or what is only scaffolded) | Derived facet absence; **Open Question** `coverage_gap`; **Assumption** for explicit scaffolding |

These are complementary. A gap is not a contradiction. An identity doubt is not a claim contradiction. An assumption is not a claim.

---

## First-class vs derived (normative v1 pick)

### Adopt (first-class, durable)

| Object | Why first-class |
|--------|-----------------|
| Content edges `SUPPORTS`, `CONTRADICTS`, `SAME_ASSERTION_AS` | Normative semantic relations among propositions (#3, #6) |
| **Contradiction record** | Lifecycle, notes, Event focus, multi-pair packaging for UX; survives re-runs of detectors |
| **Open Question** | Explicit research TODO with resolution history; hangs on Event / provisional link / contradiction / claim set |

### Allow as derived (no required stored type in v1)

| View | How produced |
|------|----------------|
| Agreement cluster | Grouping of claims linked by `SAME_ASSERTION_AS` / high-support within focus Event |
| Facet coverage matrix | “Which research facets have ≥1 live claim under this Event?” |
| Detector candidate lists | NLI / heuristic “might contradict” before edges/records exist |
| Multi-telling summary counts | “3 agree / 1 conflict pair / 2 open questions” |

### Reject for v1

| Anti-pattern | Why |
|--------------|-----|
| Contradiction as a sixth `layer` | Layers are epistemic rank of propositions, not research annotations |
| Contradiction **only** as ephemeral UI compute with no stored edges/records | Loses curator judgment, resolution, and audit |
| Auto-live detector output | Standing propose/approve preference |
| Collapsing two claim nodes into one “winner” | Claims remain recorded assertions; contradiction does not delete or truth-verdict them |
| Topic-scoped auto-contradiction | Sharing a topic ≠ shared Event / shared assertable |

**Rationale:** Pure edges without packaging make multi-telling UX rebuild “which conflicts matter on this Event?” every time. Pure derived views cannot hold **resolved / wontfix** honestly. Hybrid = edges for legality + first-class records for research workflow.

---

## Legal participants (hard rules)

### Who may be endpoints of SUPPORTS / CONTRADICTS

| Endpoint layer | Allowed? |
|----------------|----------|
| `claim` | **Yes** (primary) |
| `inference` | **Yes** (always badged as inference in UX) |
| `assumption` | **No** as evidence endpoint |
| `processed` / `raw` | **No** |
| Person / Topic / Video | **No** (entities are not propositions) |

### Focus scoping for multi-telling conflict

A **Contradiction record** for default multi-telling compare should attach to:

1. A **confirmed Event**, or  
2. An **explicit provisional identity bundle** (compare-as-if-same mode per #4 / #14),

and its member claims should be:

- **Live** (or co-approved in the same curator action), and  
- Bound to that Event / provisional targets (`ABOUT_EVENT` or `provisionally_bound`), **or** explicitly attached by curator as unbound-but-about-this-focus (rare; prefer bind first).

**Illegal packaging:**

| Situation | Correct handling |
|-----------|------------------|
| Two claims only share a Topic | Not a contradiction about one happening; optional topical browse only |
| “Same Event?” identity doubt | **Identity open question** + provisional link — **not** a claim Contradiction record |
| One side is only an Assumption | Keep `RESTS_ON`; do **not** mint `CONTRADICTS` with the assumption |
| Host paraphrase vs guest without guest assertion | Fix attribution first (#6); do not invent guest side of a pair |
| Compound unsplit claims | Split to atomic claims first; contradiction needs clear polarity per proposition |

### Contradiction vs identity (non-negotiable)

| Conflict type | Is it a claim contradiction? | Model |
|---------------|------------------------------|-------|
| Speakers disagree on explanation, craft type, intent, count, kinematics about **one** Event | **Yes** | `CONTRADICTS` + Contradiction record on that Event |
| Speakers give different exact dates/places that still fit one window/alias set | Usually **claims about keys** or open question on the Event — not automatic Event split (#4) | Claim-level conflict and/or Open Question `key_disagreement` |
| Unclear whether two referents are the **same happening** | **No** | Provisional identity link + Open Question `identity` |
| Same speaker shifts story across tellings | **Yes** (claim conflict); may also feed #10 consistency observation | Both allowed; distinct jobs |

---

## Content edges (normative detail)

Direction convention for content edges here: **either narrative direction is allowed if documented on the edge**, but multi-telling UX treats `CONTRADICTS` as **symmetric for display** (store undirected logical pair; if directed storage is used, UI always shows both poles).

| Predicate | Meaning for multi-telling | Notes |
|-----------|---------------------------|-------|
| `CONTRADICTS` | Propositions cannot both hold under a shared assertable / facet (polarity or incompatible values) | claim\|inference ↔ claim\|inference only |
| `SUPPORTS` | One proposition makes the other more plausible / elaborates consistent detail | Not a truth verdict |
| `SAME_ASSERTION_AS` | Paraphrastic **same** assertable across tellings/videos | **Two claim nodes remain** (#6) |
| `ELABORATES` | Clarifies / narrows without conflicting | Not agreement or conflict by itself |

### When to mint CONTRADICTS vs leave separate

Mint (or propose) `CONTRADICTS` when:

1. Both sides are live claim or live inference, and  
2. They concern the **same focus Event / provisional bundle** (or curator explicitly pairs them), and  
3. They assert **incompatible** content on a comparable facet (e.g. “no exhaust” vs “clear jet plume”; “23 people” vs “about 50”; “non-human” vs “classified terrestrial only” as mutually exclusive framings the curator accepts as conflict).

Do **not** mint merely because:

- Speakers emphasize different aspects of a compatible story, or  
- One claim is more specific (`ELABORATES` / support), or  
- Modalities differ without content clash (“I think…” vs “I know…” on the same content → usually not CONTRADICTS unless product treats certainty as the assertable).

### Facet (optional but recommended for UX)

Contradiction records and open questions may name a **facet** string from a small closed or curated set, e.g.:

`time`, `place`, `actors`, `object_description`, `kinematics`, `sensors`, `propulsion_signature`, `origin_explanation`, `program_affiliation`, `chain_of_custody`, `count_or_scale`, `identity_of_referent` (for claim-level mis-ID, not Event merge).

Facets are **labels for compare columns**, not a new ontology layer. v1 may start with free-ish curator facet tags and tighten later.

---

## Contradiction record (first-class research object)

### Definition

A **Contradiction record** is a durable research object that packages **one logical conflict** for multi-telling: the competing propositions, focus Event (or provisional bundle), optional facet, status, and curator notes.

It is **not**:

- An epistemic layer node  
- A verdict that one side is false  
- An Event split  
- A credibility score  

### Conceptual fields (spec-level)

| Field | Required for live open record? | Definition |
|-------|--------------------------------|------------|
| `id` | Yes | Stable id |
| `focus_event_id` **or** `provisional_bundle_id` | Yes | Multi-telling scope |
| `member_refs[]` | Yes (≥2) | Pointers to claim and/or inference ids that conflict |
| `edge_refs[]` | Recommended | Underlying `CONTRADICTS` edge ids (may be 1:1 or multi-pair) |
| `facet` | Recommended | What the conflict is about |
| `summary` | Optional | Short human/AI-proposed description of the tension |
| `lifecycle` / status | Yes | See lifecycle below |
| `PROPOSED_BY` / `APPROVED_BY` | Yes as appropriate | Actor provenance (packaging owned with #7 / #9) |
| `notes[]` | Optional | Curator research notes |
| `related_open_question_ids[]` | Optional | If escalated or paired with an OQ |
| `supersedes` | Optional | Revised packaging of the same conflict |

### Pair vs multi-way

| Shape | v1 rule |
|-------|---------|
| **Binary pair** | Default: two poles (claim A vs claim B) |
| **Multi-way** | Allowed when ≥3 mutually incompatible poles on the same facet (store as one record with N members, or N−1 binary edges under one record) |

Prefer **one record per facet-level conflict cluster** on an Event, not one record per every pairwise edge explosion, when several claims restate the same two poles (`SAME_ASSERTION_AS` clusters on each side).

### Lifecycle (Contradiction record)

| State | Meaning | In default multi-telling conflict list? |
|-------|---------|----------------------------------------|
| `proposed` | Detector/AI/curator draft; not approved | No (review queue only) |
| `open` | Live research conflict the curator accepts as real tension | **Yes** |
| `resolved` | Curator judged the tension closed for *research purposes* (see resolution kinds) | Yes, but **resolved** badge / filterable out of “active conflicts” |
| `wontfix` | Acknowledged but not pursuing (noise, out of scope, unresolvable and not load-bearing) | Default hide from active; keep in history |
| `rejected` | Proposal was wrong (false conflict, bad endpoints, illegal layers) | No |
| `superseded` | Replaced by a better packaging of the same tension | No (successor is) |

**Resolution kinds** (on `resolved` — research disposition, **not** world-truth court verdict):

| `resolution_kind` | Meaning |
|-------------------|---------|
| `curator_accepts_pole` | Curator notes which pole they currently treat as working hypothesis (optional pointer) — **does not** delete other claims |
| `compatible_after_reinterpret` | On closer reading, not truly incompatible (may soft-close edges or leave with note) |
| `split_focus` | Conflict dissolved by rebinding claims to distinct Events (identity work #4) |
| `insufficient_evidence` | Left as historical open tension with no further action; prefer `wontfix` if abandoning |
| `other` | Free note |

**Important:** Resolving a contradiction record **does not** auto-set claim truth flags (out of scope / later) and **does not** remove live claims.

---

## Open Question (first-class research object)

### Definition

An **Open Question** is a durable, curator-gated research object that records **something the graph does not yet settle** — a missing fact, an identity doubt, a key disagreement, or an explicit follow-up — so multi-telling and timeline UX can surface it.

Open questions make **uncertainty legible**. They are not claims, not inferences, and not a soft layer downgrade of a direct quote (#3).

### Kinds (v1)

| `question_kind` | Use when | Typical hang-offs |
|-----------------|----------|-------------------|
| `identity` | “Same Event as X?” / “Do these two referents co-refer?” | Provisional identity link; candidate Events |
| `claim_conflict` | Conflict needs a follow-up question beyond the record itself | Contradiction record; claim pair |
| `coverage_gap` | Expected facet has **no** (adequate) live claim under the focus | Event; optional facet |
| `key_disagreement` | Tellings disagree on Event keys (date/place) without forced split | Event; claims about keys |
| `attribution` | Who said it / which Person mapping is still open | Speaker label / proposed claim (usually blocks live claim #5/#6) |
| `other` | Curator research TODO that does not fit above | Free attachment |

**Identity open questions are not claim contradictions.** They may **reference** provisional identity and may block treating two Event IDs as one compare focus until resolved — but they do not put two Event nodes into `CONTRADICTS`.

### Conceptual fields

| Field | Required for live `open`? | Definition |
|-------|---------------------------|------------|
| `id` | Yes | Stable id |
| `question_text` | Yes | Human-readable question |
| `question_kind` | Yes | Enum above |
| `focus_event_id` and/or `provisional_bundle_id` and/or other anchors | At least one anchor | What the question is about |
| `related_claim_ids[]` / `related_contradiction_ids[]` / `related_assumption_ids[]` | Optional | Evidence of why the question exists |
| `lifecycle` / status | Yes | See below |
| `resolution_note` | On resolve/wontfix | Why closed |
| `resolved_by` / timestamps | On close | Actor audit |
| `PROPOSED_BY` | For AI/system proposals | Agent/system |
| `priority` | Optional | Curator triage (`low` \| `normal` \| `high`) — not a trust score |

### Lifecycle (Open Question)

```
proposed  →  open  →  resolved
                  ↘  wontfix
rejected  (from proposed, or rare kill of bad open)
```

| State | Meaning | Default multi-telling |
|-------|---------|----------------------|
| `proposed` | System/AI/curator draft | Review only |
| `open` | Active research question | **Surface** on Event / compare |
| `resolved` | Answered enough for curator purposes | History; optional “resolved OQs” panel |
| `wontfix` | Will not pursue | History; default hide from active |
| `rejected` | Invalid / duplicate / nonsense proposal | No |

**Who may transition:**

| Transition | AI / system | Curator |
|------------|:-----------:|:-------:|
| Create as `proposed` | **Yes** (detect/propose) | **Yes** |
| Create directly as `open` | **No** | **Yes** |
| `proposed` → `open` | **No** | **Yes** |
| `open` → `resolved` \| `wontfix` | **No** | **Yes** |
| `proposed` → `rejected` | **No** (may auto-expire policies later) | **Yes** |
| Reopen `resolved`/`wontfix` → `open` | **No** | **Yes** |

### Who creates open questions (normative)

| Actor | May do |
|-------|--------|
| **System detectors** | Propose OQs (identity candidates, coverage gaps, conflict follow-ups) with evidence pointers |
| **AI extraction / reasoning agents** | Propose OQs when extraction hits ambiguity (unbound claim, key clash, scaffolded assumption) |
| **Curator** | Open any kind; sole authority to promote to `open`, resolve, wontfix, reject |

**Standing rule:** nothing extraction- or detector-derived is **live `open`** without curator action — same spirit as claim live gate.

---

## Gaps (how they relate)

Gaps are **missing knowledge**, not opposing knowledge.

| Gap form | Representation | Enters contradiction pairs? |
|----------|----------------|------------------------------|
| **Derived coverage gap** | UI/query: focus Event has 0 live claims on facet F | No |
| **Open Question `coverage_gap`** | First-class when curator (or approved proposal) wants it tracked | No |
| **Assumption scaffolding** | Assumption + `RESTS_ON` from inference (or rare claim) | **No** as evidence; makes the gap **visible** |
| **Unbound claim** | Claim exists but Event not bound (#6) | Not a gap about Event E until bound; may spawn attribution/identity OQ |

**Rule:** Do **not** invent a fake opposing claim to “fill” a gap. Prefer Open Question or Assumption.

### Gap vs contradiction (examples)

| Situation | Model |
|-----------|--------|
| Fravor telling asserts no rotors; another telling asserts jet exhaust on same Event | **Contradiction** |
| No telling in corpus asserts altitude | **Coverage gap** (derived ± OQ) |
| Inference assumes “the ranch” = Skinwalker | **Assumption** (+ optional OQ if identity of place is load-bearing) |
| Two videos might be same incident | **Identity OQ** + provisional link |

---

## Agreement (multi-telling complement)

Agreement is required for honest compare (not only conflict).

| Mechanism | v1 role |
|-----------|---------|
| `SAME_ASSERTION_AS` | Primary cross-telling “same assertable” link; two claims remain |
| `SUPPORTS` | Consistent reinforcement / partial support |
| Derived agreement cluster | UX grouping under a facet for “these tellings align” |
| Optional Agreement record | **Out of v1 required set** — derive from edges unless UX later needs lifecycle on agreement (unlikely) |

**Do not** collapse paraphrases into one claim id (#6).

---

## Creation pipeline (conceptual)

```
Live claims (± inferences) on focus Event / provisional bundle
        │
        ├─► detectors / AI propose:
        │     CONTRADICTS / SUPPORTS / SAME_ASSERTION_AS edges (proposed)
        │     Contradiction records (proposed)
        │     Open Questions (proposed): identity | conflict | coverage_gap | …
        │
        ├─► curator reviews (#9)
        │     approve edges + records + OQs → open/live research state
        │     reject false conflicts / bad pairs
        │
        └─► multi-telling UX (#14)
              agreement clusters (derived)
              open contradiction records
              open questions
              coverage matrix (derived)
              never list assumptions as evidence rows
```

### Detector honesty

1. Detectors produce **candidates** only.  
2. Confidence scores are **review assists**, not trust scores and not auto-live (#10 forbids fake credibility scores; same spirit here).  
3. Illegal endpoint pairs are **hard reject** on write, even if a detector suggests them.  
4. Re-running detectors must **not** wipe curator-approved records; propose new/duplicate candidates for merge or reject.

---

## Worked examples (UAP seed-style)

### Example 1 — Cross-person claim contradiction (same Event)

**Focus Event:** *Nimitz* / Tic Tac (2004).  
**Claim C1 (Fravor, Danny Jones):** “The object had no visible means of propulsion / no rotors.”  
**Claim C2 (Guest B, Area52 panel):** “It was likely a classified terrestrial drone with conventional propulsion signatures.”  

| Object | Content |
|--------|---------|
| Edge | C1 `CONTRADICTS` C2 (facet: `origin_explanation` / `propulsion_signature`) |
| Contradiction record R1 | focus=Nimitz; members={C1,C2}; status=`open` after curator approve |
| Open Question (optional) | “Is terrestrial drone compatible with Fravor’s no-propulsion description under this Event?” kind=`claim_conflict` |

Both claims remain **live**. No Event split. No assumption as a pole.

### Example 2 — Agreement across tellings

**C3** (Fravor interview A) and **C4** (Fravor or aligned retelling B): both assert capsule/Tic-Tac shape, no wings.  
→ `SAME_ASSERTION_AS` (and/or `SUPPORTS`); derived agreement cluster under facet `object_description`.  
**Not** a contradiction record.

### Example 3 — Identity open question (not a contradiction)

Video A recounts “Tic Tac-like” 2015 East Coast; video B is 2004 Nimitz.  
Keys conflict on time (and often place).  

| Correct | Incorrect |
|---------|-----------|
| Distinct Events (default split) or provisional link + OQ `identity`: “Same incident as Nimitz 2004?” | Minting C_a `CONTRADICTS` C_b as if one Event |
| Claims stay on their Event IDs | Silent merge to force a contradiction table |

### Example 4 — Coverage gap

Focus Event has rich kinematics claims but **no** live claim about sensor track ownership.  

| Step | Action |
|------|--------|
| Derived | Coverage matrix shows empty facet `sensors` |
| Proposed OQ | “Which platform held primary radar track?” kind=`coverage_gap` |
| Curator | Promotes to `open` or ignores (gap stays derived-only) |

No fake claim invented.

### Example 5 — Assumption must not enter the pair

Inference I1 about co-reference of “the ranch” `RESTS_ON` Assumption A1.  
Guest claim C5 asserts materials anomaly at “the ranch.”  
Another claim C6 asserts materials prosaic at Skinwalker Ranch.  

| Legal | Illegal |
|-------|---------|
| If curator binds both to same Event **and** treats ranch co-ref as settled, C5 `CONTRADICTS` C6 | C5 `CONTRADICTS` A1 |
| OQ identity/place + keep A1 as scaffolding until settled | Promoting A1 to claim without source speech |

### Example 6 — Same-person conflict + credibility hook

Guest G asserts incompatible altitudes about Event E on two videos.  
→ Contradiction record on E with {C7, C8}; both live.  
→ Optional #10 consistency observation `conflict` person×event with same claim ids.  
→ **No** auto trust score; **no** auto-suppress C8.

### Example 7 — Resolution without deleting claims

Curator later decides the two “altitude” claims used different flight phases (compatible after reinterpret).  

| Action | Result |
|--------|--------|
| R_alt status → `resolved`, `resolution_kind=compatible_after_reinterpret` | Active conflict list clears |
| Claims C7, C8 stay live | History preserved |
| Optional: retire or annotate `CONTRADICTS` edge per curator | Edges may remain with “resolved record” superseding active display |

---

## Multi-telling UX contracts (#14)

Default compare on a **focus Event** (or provisional bundle) should be able to show:

1. **Claims by facet / telling** with provenance jump (video + time via #7).  
2. **Agreement** groups (`SAME_ASSERTION_AS` / support).  
3. **Open contradiction records** with both poles, speakers, and links to media.  
4. **Open questions** (identity separate from claim_conflict / coverage_gap).  
5. **Coverage gaps** (derived matrix ± OQs).  
6. **Inferences badged**; **assumptions only in scaffolding panel**, never in evidence conflict table.  
7. Modes: **Confirmed Event** vs **Provisional bundle** — identity OQs prominent in provisional mode (#4).

Out of scope for this ticket: wireframes, exact column layout, NLI model choice.

---

## Downstream contracts

### Multi-telling compare UX (#14) may assume

- Durable Contradiction records and Open Questions with the lifecycles above.  
- Edge legality: claim|inference only; no assumption evidence rows.  
- Identity OQs distinct from claim conflicts.  
- Agreement via `SAME_ASSERTION_AS` / `SUPPORTS` + derived clusters.

### Human approval (#9) may assume

- Proposed edges/records/OQs enter review; curator transitions to open/live research state.  
- Atomic approve of claim pair + CONTRADICTS edge + contradiction record is allowed if matrix-legal.  
- Bulk approve must not hide layer badges or illegal endpoints.

### Speaker credibility (#10) may assume

- Cross-person conflicts stay primarily here.  
- Same-person conflicts may dual-write optional consistency observations pointing at the same claim ids.  
- No composite scores from conflict counts.

### Claim model (#6) / Ontology (#3) remain normative

- This ticket **does not** loosen layer matrices.  
- Atomic claims remain the preferred conflict poles.  
- Unbound claims are not silently retargeted into Event conflict tables.

### Event identity (#4) remains normative

- Claim-only divergence → same Event + contradiction model.  
- Referent sameness uncertainty → provisional link + identity open question.

---

## Out of scope for this decision

- Graph DB schema / ID format  
- NLI / embedding thresholds for auto-propose  
- Claim true/false verdict workflow  
- UI wireframes for compare (#14)  
- Public debate scoring or “community consensus”  
- Auto-deleting claims when a contradiction is resolved  

---

## Policy cheat-sheet

```
Agreement?
  → SAME_ASSERTION_AS / SUPPORTS (claims stay separate nodes)
  → Derived clusters OK for UX

Conflict about the same Event (or provisional bundle)?
  → CONTRADICTS between claim|inference only
  → Package as Contradiction record (first-class)
  → Lifecycle: proposed → open → resolved | wontfix

Same Event identity uncertain?
  → Provisional link + Open Question kind=identity
  → NOT a claim contradiction

Gap (nobody said it)?
  → Derived coverage and/or Open Question kind=coverage_gap
  → Assumption if scaffolding inference — never as CONTRADICTS endpoint

Who creates?
  → System/AI propose candidates
  → Curator opens, resolves, wontfix, rejects

Never:
  → Assumptions as evidence in contradiction pairs
  → Auto-live detector conflicts
  → Sixth epistemic layer for contradictions
  → Topic-only auto-contradiction
  → Collapse claims into one “winner” node on resolve
```

---

## Decision log

| Date | Decision |
|------|----------|
| 2026-07-22 | Adopt hybrid model: legal content edges (SUPPORTS/CONTRADICTS/SAME_ASSERTION_AS) + first-class Contradiction records and Open Questions outside the five-layer spine; gaps as derived coverage ± OQ/assumption; AI/system propose, curator opens/resolves/wontfix; identity OQs distinct from claim conflicts; assumptions never evidence endpoints. |

## Decision date

Recorded 2026-07-22 as the recommended resolution for issue #8 (batch completion with recommended defaults; no interactive grilling).
