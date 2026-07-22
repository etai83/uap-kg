# Human approval workflow

Decision asset for [Human approval workflow](https://github.com/etai83/uap-kg/issues/9)  
Part of [Wayfinder: UAP YouTube knowledge graph spec](https://github.com/etai83/uap-kg/issues/1)

**Depends on:** [Epistemic layer ontology](./epistemic-layer-ontology.md) (#3), [Claim model](./claim-model.md) (#6), [Provenance minimum](./provenance-minimum.md) (#7), [Speaker identity and alias merge](./speaker-identity-and-alias-merge.md) (#5)  
**Related:** [Event identity rule](./event-identity-rule.md) (#4), [Speaker credibility signals v1](./speaker-credibility-signals-v1.md) (#10), [Topics vs events](./topics-vs-events.md) (#11)  
**Status:** Recommended decision (batch defaults; personal solo tool — efficient review without silent auto-live).  
**Scope:** Spec-level lifecycle states, approval units, auto-land rules, versioning/supersession, and review posture. No UI wireframes, storage schema, or implementation code.

**Downstream consumers:** Contradiction model (#8), Multi-telling compare UX (#14), any write-path / review-queue implementation.

---

## Question

What are the states and rules for **AI-proposed → human-approved → live** graph objects?

Decide: object statuses, batch vs item review, what can auto-land as raw/processed without approval, and whether edits create new versions.

---

## Decision summary

| Axis | Decision |
|------|----------|
| Lifecycle states (epistemic layered nodes) | **`proposed` \| `live` \| `rejected` \| `superseded`** — orthogonal to epistemic layer |
| Sole approver | **Curator** only. AI/system may propose; AI may **never** set `live` on gated objects |
| Catalog raw exception | Official YouTube **catalog raw** (channel, video identity, public metadata snapshot) and **mechanical track refs** may enter **`live` without claim-level approval** |
| Everything else gated | All extraction-derived `processed`, `claim`, `inference`, `assumption`, Person create/alias/merge/episode map, Event merge/split, Topic mint, credibility live annotations → **curator before live** |
| Review unit | **Bundle-first, item-capable.** Default review surface is a **video-scoped approval bundle** (episode maps + processed + claims together); curator may drill to **item approve/reject** |
| Batch approve | **Allowed** for a personal solo tool when each selected node passes its live checklist and dependency rules; never a layer-hiding “approve all soup” |
| Auto-land | **Catalog raw + mechanical media anchors only.** No silent auto-live for processed/claims/inferences/assumptions/persons |
| Edits / corrections | **Immutable layer preference:** do **not** patch live semantic content in place. Mint a **new same-layer node**, `SUPERSEDES` the old, set old → `superseded` |
| Multi-telling (#14) | Default compare uses **`live` atomic claims** only; approve actions in compare UX are the same lifecycle transitions, never bypass checks |

---

## Core principle

> **Proposed is cheap; live is curated truth-for-this-tool.**  
> AI drafts freely into `proposed`. The curator is the only path to `live`.  
> Catalog facts from the official API may land live because they are source inventory, not extractions.  
> Once live, corrections **version** (new node + supersede) rather than rewrite history.

Standing contracts honored from #3 / #5 / #6 / #7:

- Layer is immutable; promotion creates a **new** higher-layer node.
- Lifecycle is orthogonal to layer.
- Live claims need full grounding path + approved attribution.
- Live inferences need live (or co-approved) claim premises.
- Person identity writes are human-gated.
- Approval records `APPROVED_BY` without stripping extraction-run identity.

---

## Lifecycle states

### Canonical set (layered epistemic nodes)

Applies to nodes with `layer ∈ {raw, processed, claim, inference, assumption}` when they participate in the propose→live pipeline. Catalog raw may skip `proposed` (see Auto-land).

| State | Meaning | Default research views / multi-telling? | Editable semantic content? |
|-------|---------|------------------------------------------|----------------------------|
| **`proposed`** | AI- or curator-drafted; not yet approved | **No** (review queue / provisional mode only) | Staging edits allowed **before** first live (still prefer supersede if already shared as proposal history) |
| **`live`** | Curator-approved; participates as graph evidence | **Yes** | **No in-place** content rewrite; correct via supersession |
| **`rejected`** | Curator declined; retained for audit / re-proposal learning | **No** | Frozen; optional note why rejected |
| **`superseded`** | Replaced by a newer same-layer successor via `SUPERSEDES` | **No** (successor is); history navigable | Frozen; points to successor |

### Orthogonal axes (do not overload lifecycle)

| Axis | Values | Owned by |
|------|--------|----------|
| Epistemic **layer** | raw / processed / claim / inference / assumption | #3 — immutable on the node |
| Person states | proposed / candidate / active / merged-away / deprecated | #5 — person entities, not layered nodes |
| Episode map `review_status` | needs_review / approved / rejected | #5 |
| Event identity | provisional vs confirmed merge | #4 |
| Topic lifecycle | proposed / live / deprecated | #11 |

**Rule:** A claim’s lifecycle is independent of its layer. A `live` claim is still a claim, not a verdict of world-truth.

### Terminal vs resumable

| Transition | Allowed? | Notes |
|------------|----------|-------|
| `proposed` → `live` | Yes | Requires live checklist + `APPROVED_BY` |
| `proposed` → `rejected` | Yes | With optional reject reason |
| `rejected` → `proposed` | Yes | Only via **new proposal** or explicit **reopen** that re-enters review (prefer mint new node if content changed) |
| `live` → `rejected` | **No** as silent un-approve | Use **supersede** with a corrective successor, or **withdraw** pattern: supersede with empty-successor policy only if product needs “retract”; v1 default = supersede with corrected node or mark superseded by a “withdrawn” successor note |
| `live` → `superseded` | Yes | When successor is approved live (or atomic co-approve) |
| `superseded` → anything | **No** | Terminal history |
| Any → change `layer` | **Forbidden** | #3 |

### Withdrawal (v1 minimal)

If the curator needs to remove a live node from default views without a content replacement:

1. Mint successor (same layer) whose payload is an explicit **withdrawal** (or curator sets a `withdrawn` flag on a superseding stub — implementation choice).  
2. `SUPERSEDES` old → old becomes `superseded`.  
3. Successor may be `live` as a tombstone **or** the product may treat “superseded with no live successor content” as sufficient hiding — **prefer always having a live successor pointer** so history is walkable.

v1 does **not** require a fifth lifecycle enum value `withdrawn`; supersession covers it.

---

## Who may write what

| Actor | May create `proposed` | May set `live` | May reject | May supersede (propose successor) |
|-------|----------------------|----------------|------------|-----------------------------------|
| **AI / pipeline** | Yes (gated object classes) | **Never** | No | May propose successor as `proposed` |
| **System ingest (catalog)** | Optional | **Yes** for catalog raw exception only | N/A | Catalog refresh = update snapshot policy (#12), not claim supersession |
| **Curator** | Yes | **Yes** (only human path for gated classes) | Yes | Yes (approve successor + supersede) |

Every non-catalog create still gets `PROPOSED_BY` (or equivalent) and `extraction_run_id` per #7. Live transition adds `APPROVED_BY` + approval timestamp.

---

## Auto-land vs must-approve

### Auto-land (may enter `live` without claim-level / extraction approval)

| Object | Auto-live? | Conditions |
|--------|------------|------------|
| **Channel** catalog identity | **Yes** | Official API / committed seed channel inventory |
| **Video** catalog identity + official metadata snapshot | **Yes** | Official Data API fields; refresh does not approve claims |
| **Mechanical raw track refs** | **Yes** | Pointers only: artifact URI/hash, track kind, video_id, acquisition method — **no** interpretive speech structure |
| Stats snapshot cache | **Yes** (as catalog-adjacent cache) | Volatile; not evidence for claims |

These are **source inventory and anchors**, not narrative extractions.

### Must approve before `live` (hard gate)

| Object | Gate | Notes |
|--------|------|-------|
| `processed` utterances / spans / diarized structure | Curator | Default AI create = `proposed` |
| Episode attribution (label → Person) | Curator | #5; required before live claim attribution |
| Person create / alias attach / merge | Curator | #5 |
| `claim` | Curator | Full live checklist (#6 + #7) |
| `inference` | Curator | Premises must be live or co-approved |
| `assumption` | Curator | Live scaffolding only after approve |
| Event merge / split / high-stakes confirm | Curator | #4 |
| Topic mint / live topic assignment | Curator | #11 |
| Consistency observations / AI credibility tags | Curator | #10 |
| Interpretive raw anchors | Curator if interpretive | Pure mechanical refs auto-land; identity-interpretive anchors do not |

### Explicit non-auto-land (common confusions)

| Temptation | Rule |
|------------|------|
| “ASR is mechanical, so processed can auto-live” | **No.** Processed is extraction-derived structure (who said what when). Gated. |
| “High extraction confidence → auto-live claim” | **No.** Confidence is review assist only (#6). |
| “Host default on seed channel → auto-live person map” | **No.** One-click / batch eligible, still curator (#5). |
| “Bulk approve all extractions for a video” | **Allowed as curator action** if per-node checks pass — not silent system auto-land. |
| “Approve claim without approving supporting processed” | **No** unless processed is already live or co-approved in the **same atomic action**. |

---

## Live checklists (approve gates)

Approval is refused (hard error) if the checklist fails. UI should surface failures, not soft-warn into live.

### Processed (speech span)

- [ ] `layer=processed`  
- [ ] Legal `DERIVED_FROM` → raw path  
- [ ] `video_id` + timestamp span + quote/transcript text  
- [ ] `speaker_label` or explicit unresolved / non_speech  
- [ ] `extraction_run_id` + `PROPOSED_BY`  
- [ ] Curator `APPROVED_BY` on transition  

### Claim

- [ ] `layer=claim`, atomic `claim_text` (no compound live)  
- [ ] ≥1 `EXTRACTED_FROM` → **live or co-approved** processed  
- [ ] Processed→raw path resolves (video + time + text)  
- [ ] `ATTRIBUTED_TO` → **active** Person with **approved** episode map for supporting span(s)  
  - Unresolved-speaker claims: **stay proposed** by default; live only if product explicitly allows badged unresolved (prefer not for multi-telling units)  
- [ ] `extraction_run_id` + `PROPOSED_BY`  
- [ ] Curator `APPROVED_BY`  

### Inference

- [ ] `layer=inference` + non-empty rationale  
- [ ] ≥1 `BASED_ON` → claim that is **live or co-approved in this action**  
- [ ] All `BASED_ON` / `RESTS_ON` supports end **live** after the atomic action  
- [ ] No masquerade as claim  
- [ ] Run identity + `APPROVED_BY`  

### Assumption

- [ ] Statement + why-introduced  
- [ ] **No** fake `EXTRACTED_FROM`  
- [ ] Run identity + `APPROVED_BY`  

### Episode map / Person (from #5, workflow view)

- [ ] Person create: canonical name + ≥1 identity evidence + curator approve → active  
- [ ] Episode map: video_id + speaker_label + person_id + method/evidence + approve  
- [ ] Merge: multi-signal evidence + curator approve  

---

## Dependency and atomic co-approval

### Rule: no dangling live tops

A node may not become `live` if a **required support** remains non-live after the action.

| Dependent | Supports that must be live (or co-approved) |
|-----------|-----------------------------------------------|
| Claim | Extracted-from processed; attributed Person + episode map |
| Inference | All `BASED_ON` claims; any `RESTS_ON` assumptions used as scaffolding |
| Processed | Raw anchors (catalog/mechanical may already be live) |

### Atomic co-approval (allowed and preferred)

Curator may approve a **bundle** in one action when the resulting end-state is matrix-legal:

Example happy path for one guest assertion:

1. Episode map `SPEAKER_01` → Person P (approve → approved map; create P if needed).  
2. Processed U1 (approve → live).  
3. Claim C1 `EXTRACTED_FROM` U1, `ATTRIBUTED_TO` P (approve → live).  

**One curator gesture** may apply all three if the UI presents them as a linked bundle and validation runs on the **post-state**.

### Order when not atomic

If approving piecemeal: **Person/map → processed → claim → inference**.  
Rejecting a lower support does not auto-delete dependents; dependents stay `proposed` or fail their next approve attempt.

### Reject cascade (v1)

- Rejecting a claim does **not** auto-reject its processed span (span may still be useful).  
- Rejecting an episode map **blocks** live claims that need that attribution; proposed claims remain proposed.  
- Rejecting a person create blocks maps/claims pointing at it.

---

## Batch vs item review (solo tool posture)

### Product context

This is a **personal solo research tool**, not multi-reviewer enterprise workflow. Review UX optimizes for:

1. **Throughput** on a clean 2-speaker interview.  
2. **Safety** on panels, messy diarization, and compound extractions.  
3. **Jump-to-video** via provenance (#7) on every item.

### Default review unit: video-scoped **approval bundle**

| Bundle contents (typical) | Review mode |
|---------------------------|-------------|
| Episode speaker maps for the video | Batch-confirm clean host/guest maps; item-fix conflicts |
| Processed spans (main speakers) | Often batch-approve high-quality ASR spans; item-fix garbage/ads |
| Proposed atomic claims for the video | **Primary care surface** — batch only when checklist-green |
| Optional inferences/assumptions | Item review by default (rarer, higher stakes) |

### Batch approve rules

**Allowed when all of:**

1. Curator explicitly selects a set (or “all checklist-green in this bundle”).  
2. **Each** node independently passes its live checklist.  
3. Dependency closure is satisfied (or co-included in the same batch).  
4. Layer badges remain true — batch never retypes or hides layer.  
5. Compound claim drafts are **not** in the batch (must split first).  
6. Unresolved-speaker claims are **excluded** from multi-telling-oriented batch defaults.

**Forbidden:**

- System timer or confidence threshold auto-batch without curator click.  
- “Approve all extractions ever” global without scope.  
- Batch that would live an inference on still-proposed claims without co-including those claims.

### Item review (required or preferred)

| Situation | Prefer item |
|-----------|-------------|
| Panel / multi-guest / crosstalk | Per-label maps; per-claim |
| Low attribution confidence | #5 medium/low bands |
| Compound → split decisions | Per atomic child |
| Host meta_speech keep vs discard | Per item |
| Inference / assumption | Default item |
| Event merge / person merge | Always deliberate item (or dedicated merge UI) |
| Any validation failure in a green batch | Drop failed items; do not fail-open |

### One-click approve

Eligible for **single-bundle one-click** when signals are clean (aligns with #5 high-confidence host/guest maps):

- Seed-channel 2-speaker interview  
- Host + title-named guest maps proposed  
- Atomic claims with clear quotes and approved maps  
- No conflicting signals  

One-click is still a **curator action** that runs the full checklist — not auto-land.

### Reject and skip

| Action | Effect |
|--------|--------|
| **Reject** | Node → `rejected`; optional reason; not evidence |
| **Skip / leave proposed** | Remains in queue; default views ignore it |
| **Edit then approve** | Prefer: edit creates **new proposed** successor (or mutate only while still proposed and never live); then approve successor |

---

## Versioning and supersession (edits)

### Immutable layer preference (normative)

1. **`layer` never changes** on an existing id (#3).  
2. **Live semantic payload** (claim_text, inference rationale, assumption statement, processed span text used as grounding) is **not patched in place** after live.  
3. Corrections mint a **new node** at the **same layer** with a new `extraction_run_id` (or `manual_curator_edit` run).  
4. New node `SUPERSEDES` old node; old → `superseded` when successor becomes live (or in the same atomic approve).  
5. Edges that pointed at the old node for **default views** re-point or resolve via successor; audit keeps history.

### What counts as an “edit”

| Change | Handling |
|--------|----------|
| Fix claim wording / polarity / atomicity | New claim + `SUPERSEDES`; re-approve |
| Fix processed transcript text that grounds claims | New processed + supersede; **claims** that extracted from old should be re-grounded or superseded (do not leave live claims on superseded-only supports without migration) |
| Remap speaker label → different Person | New/updated episode map (approve); claims may need supersession if attribution changes |
| Strengthen ABOUT_EVENT binding | Prefer additive edge if unbound→bound without changing claim_text; if proposition scope changes, supersede claim |
| Catalog metadata refresh | Update catalog snapshot per ingestion policy — **not** SUPERSEDES on claims |
| Reject wrong proposal before live | `rejected` or delete-from-queue policy; no supersession required |
| Curator tweaks proposed (never live) text | In-place on `proposed` allowed for solo ergonomics **or** supersede-proposed chain; once live, supersede only |

### Supersession rules

| Rule | Detail |
|------|--------|
| Same layer only | `SUPERSEDES` is same-layer → same-layer (#3) |
| One primary successor | Prefer single live successor; chains allowed (A←B←C) |
| Approve gate | Successor defaults `proposed` until curator approves (curator-authored successor may still go proposed→live in one action) |
| Multi-telling | Compare uses **live** tip of chain; history available for audit |
| Provenance | Do not rewrite old run; new run on successor (#7) |
| Content edges | SUPPORTS/CONTRADICTS/SAME_ASSERTION_AS may need curator refresh; do not silently copy all edges if meaning changed |

### Migration when support is superseded

If processed U_old is superseded by U_new:

- Live claims still `EXTRACTED_FROM` U_old are **invalid for honesty** once U_old is non-live.  
- v1 policy: approving supersession of grounding processed **queues or requires** claim re-ground (new claim or edge migrate + checklist) before claims remain in default multi-telling.  
- Product may atomic-bundle: supersede U + re-ground claims in one curator action.

---

## Entity workflows (non-layered) — approval alignment

Entities sit **outside** the five-layer spine but share the propose→approve spirit.

| Entity action | Proposal | Live gate | Versioning note |
|---------------|----------|-----------|-----------------|
| Person create | AI/curator | Curator → active | Merge uses merged-away redirect (#5), not claim SUPERSEDES |
| Alias attach | AI/curator | Curator | Collision → merge review |
| Person merge | AI/curator | Curator | Survivor + audit |
| Episode map | AI/curator | Curator approve | Re-process may invalidate label ids → new maps |
| Event create | AI/curator | Curator for confirmed high-stakes; provisional allowed per #4 | Merge/split curator-owned |
| Topic mint / assign | AI/curator | Curator | Taxonomy curator-owned (#11) |

These do not use `layer`, but review UI may show them in the same **video bundle** (especially episode maps + persons).

---

## Queues and surfaces (spec-level, not wireframes)

### Primary surfaces

1. **Per-video review bundle** — default after an extraction run completes for a pilot video.  
2. **Global proposed inbox** — optional filter by layer, person, event, confidence.  
3. **Multi-telling compare (#14)** — operates on **live** claims; may offer “approve selected proposed claims about this Event” as a **shortcut into the same gates**, not a second lifecycle.

### Required review affordances (conceptual)

- Layer badge always visible.  
- Jump to `video_id` + timestamp + quote (#7).  
- Show `ATTRIBUTED_TO` / speaker_label / map status.  
- Checklist failures listed before approve enables.  
- Batch select + approve/reject.  
- Split compound draft into atomic claims.  
- Supersede / edit-as-new for corrections.

### Visibility rules

| Consumer | Sees `proposed`? | Sees `live`? | Sees `rejected` / `superseded`? |
|----------|------------------|--------------|----------------------------------|
| Default multi-telling / timeline | No | Yes | No (optional “history” toggle) |
| Review queue | Yes | Optional | Optional filter |
| Audit / provenance walk | Yes | Yes | Yes |

---

## Concrete approve actions for multi-telling (#14)

Multi-telling compare lines up **Tellings of a focus Event** using **live atomic claims** (optionally live inferences, clearly badged). Assumptions never enter as evidence (#3, #6).

### Actions that #14 may expose (all reuse this workflow)

| UX action | Lifecycle effect | Checks |
|-----------|------------------|--------|
| **Approve claim** | `proposed` → `live` | Full claim checklist; co-approve processed/map if needed |
| **Reject claim** | `proposed` → `rejected` | Optional reason; claim drops from compare candidates |
| **Approve supporting bundle** | Maps + processed + claim(s) → live together | Atomic co-approval rules |
| **Correct claim text** | New claim proposed → approve → `SUPERSEDES` old | Old live claim → superseded; compare switches to successor |
| **Bind unbound claim to Event** | Additive `ABOUT_EVENT` if text unchanged | If binding changes meaning, supersede instead |
| **Mark same assertion** | Add `SAME_ASSERTION_AS` between two **live** claims | Does not merge ids; both remain |
| **Propose contradiction** | Content edge among live claims/inferences | #8 owns model; still no auto-live without curator if edges are curated objects |
| **Approve inference in compare** | inference → live | Premises live; badge as inference not claim |

### What multi-telling must never do

- Treat `proposed` claims as agreed/conflict evidence in **default** compare.  
- Auto-live high-similarity paraphrases into one claim id.  
- Promote assumptions into the support/contradict table.  
- Bypass person attribution gates to “just show the quote as a claim.”

### Provisional mode

Compare may offer a **provisional mode** that *displays* proposed claims with badges for curator speed — still not “live graph evidence.” Approving from that mode runs the same checklist.

---

## Worked examples

### A — Clean Danny Jones 2-speaker interview (batch path)

1. Catalog video auto-lives via API.  
2. ASR/diarize run writes proposed processed spans + proposed maps (host default Danny; guest from title).  
3. Claim extract writes proposed atomic claims.  
4. Curator opens **video bundle**, sees all checklist-green → **one-click / batch approve** maps + processed + claims.  
5. Multi-telling can use those live claims when Event-bound.

### B — Panel with unknown third speaker (item path)

1. Host + named guest maps high confidence; third label unresolved.  
2. Curator batch-approves host/guest maps and their claims.  
3. Claims grounded only in unresolved label **stay proposed** (or rejected).  
4. No “Unknown Panelist” person minted (#5).

### C — Bad atomicity caught in review

1. AI proposes one compound claim with two facts.  
2. Approve disabled until split.  
3. Curator splits → two proposed claims → batch-approves both.

### D — Correction after live

1. Live claim C1 mis-paraphrases a number (“23” → “32” error).  
2. Curator creates C1′ with correct text, same grounding, `SUPERSEDES` C1.  
3. Approve C1′ → C1 becomes `superseded`.  
4. Multi-telling shows C1′; history retains C1.

### E — Inference blocked on proposed premises

1. I1 proposed `BASED_ON` C1, C2; C2 still proposed.  
2. Approve I1 alone → **hard fail**.  
3. Atomic approve C2 + I1 → both live.

### F — Catalog exception clarity

1. New seed video appears in channel uploads playlist → catalog raw **live** immediately.  
2. No transcript yet → no processed/claims.  
3. Later extraction → all gated nodes `proposed` until curator.

---

## Policy cheat-sheet

```
Catalog channel/video metadata (official API)?
  → Auto-live (catalog exception). No claim gate.

Mechanical raw track pointer only?
  → Auto-live.

Processed / claim / inference / assumption?
  → Create as proposed. Curator approve → live.
  → AI never sets live.

Person / episode map / merge / Event merge / Topic mint?
  → Curator before live (entity rules #4/#5/#11).

Review default?
  → Per-video bundle; batch if checklist-green; item when messy.

Batch approve?
  → Curator-selected; per-node checklist; dependency closure;
    no layer hiding; no confidence auto-land.

Live claim needs?
  → Atomic text + EXTRACTED_FROM live/co-approved processed
    + path to raw + ATTRIBUTED_TO active Person + approved map
    + APPROVED_BY.

Edit live content?
  → New same-layer node + SUPERSEDES; old → superseded.
  → Never patch layer; prefer not to patch live payload in place.

Multi-telling default?
  → Live atomic claims only.
  → Approve-from-compare uses these same gates (#14).
```

---

## Downstream contracts

### Contradiction model (#8) may assume

- Only **live** claims/inferences participate as default evidence endpoints.  
- Rejected/superseded nodes remain for audit, not active contradict tables.  
- Supersession may require re-validating or re-proposing contradiction edges.

### Multi-telling compare UX (#14) may assume

- Lifecycle filter: default **live** only.  
- Approve/reject/correct actions are defined here.  
- Bundle co-approval is legal and preferred for attribution+claim packs.  
- SAME_ASSERTION_AS links distinct live claims; no collapse-on-approve.

### Implementation / write path may assume

- State machine: proposed↔rejected, proposed→live, live→superseded (+ successor live).  
- Validation hooks = checklists above + #3 matrices + #7 path rules.  
- `APPROVED_BY` + timestamp on live transition; runs preserved.

---

## What this intentionally does not decide

- Exact review UI layout, keyboard shortcuts, or notification design.  
- Whether proposed nodes are hard-deleted vs retained forever (prefer retain).  
- Numeric confidence calibration.  
- Multi-user roles / RBAC (solo curator only).  
- Full contradiction object schema (#8).  
- Event merge UX details (#4).  
- Storage representation of lifecycle vs edges.

---

## Decision log

| Date | Decision |
|------|----------|
| 2026-07-22 | Adopt proposed/live/rejected/superseded lifecycle; curator sole live gate; catalog raw + mechanical track auto-land; all extractions and identity writes gated; video-scoped bundle review with checklist-safe batch approve; atomic co-approval for dependencies; live edits via same-layer SUPERSEDES (immutable layer preference); multi-telling approve actions reuse these gates. |

## Decision date

Recorded 2026-07-22 as the recommended resolution for issue #9 (batch completion with recommended defaults; no interactive grilling).

---

## Sources / related

1. Issue #9 — Human approval workflow — https://github.com/etai83/uap-kg/issues/9  
2. Issue #3 — [epistemic-layer-ontology.md](./epistemic-layer-ontology.md)  
3. Issue #6 — [claim-model.md](./claim-model.md)  
4. Issue #7 — [provenance-minimum.md](./provenance-minimum.md)  
5. Issue #5 — [speaker-identity-and-alias-merge.md](./speaker-identity-and-alias-merge.md)  
6. Issue #4 — [event-identity-rule.md](./event-identity-rule.md)  
7. Issue #10 — [speaker-credibility-signals-v1.md](./speaker-credibility-signals-v1.md)  
8. Issue #11 — [topics-vs-events.md](./topics-vs-events.md)  
