# Multi-telling compare UX requirements

Decision asset for [Multi-telling compare UX requirements](https://github.com/etai83/uap-kg/issues/14)  
Part of [Wayfinder: UAP YouTube knowledge graph spec](https://github.com/etai83/uap-kg/issues/1)

**Depends on:** [Event identity rule](./event-identity-rule.md) (#4), [Claim model](./claim-model.md) (#6), [Provenance minimum](./provenance-minimum.md) (#7), [Contradiction and open-question model](./contradiction-and-open-question-model.md) (#8), [Human approval workflow](./human-approval-workflow.md) (#9), [Topics vs events](./topics-vs-events.md) (#11)  
**Related:** [Speaker credibility signals (v1)](./speaker-credibility-signals-v1.md) (#10), [Seed channel set v1](./seed-channel-set-v1.md) (#2)  
**Status:** Recommended decision (batch defaults; no interactive grilling).  
**Scope:** Spec-level **information architecture** for the dual UX spine (event timeline + multi-telling compare). Sections, comparison dimensions, and minimum actions only — **not** visual design, wireframes, pixels, layout libraries, or implementation code.  
**Product posture:** Solo personal research tool. No multi-user roles, notifications chrome, sharing, or collaborative review workflow in v1.

---

## Question

What must the **event timeline + multi-telling compare** surface include in the v1 spec (information architecture, not pixels)?

Decide: default layout sections, comparison dimensions (who said what when, agreement/conflict, provenance), and the minimum actions (approve claim, mark open question, jump to timestamp).

---

## Decision summary

| Axis | Decision |
|------|----------|
| Dual spine | **Event timeline** (browse/select happenings) **+ multi-telling compare** (line up Tellings of one focus). Topics filter navigation only; they never become the compare identity |
| Focus scope | Compare always scoped to one **focus Event** (confirmed) **or** an explicit **provisional identity bundle** (“compare as if same”). Never “everything under Topic X” as one happening |
| Compare units | **Live atomic claims** are the primary rows. Live **inferences** may appear **clearly badged**. **Assumptions never** enter evidence / conflict tables |
| Default sections (timeline) | Identity strip · chronological Event list · filters · provisional/duplicate hints · open-question badges · entry to compare |
| Default sections (compare) | Focus header · Telling strip · Claims board · Agreement · Conflict · Gaps & open questions · Provenance / media · Optional scaffolding & credibility side panels |
| Comparison dimensions | **Who** (Person) · **What** (`claim_text`) · **When said** (video + timestamp) · **About when/where** (Event keys / claim facet) · **Agreement** · **Conflict** · **Gaps** · **Provenance path** · **Lifecycle badge** |
| Min actions (v1 must) | **Approve claim** · **Mark open question** · **Jump to timestamp** |
| Strongly recommended actions | Reject claim · Bind claim to Event · Mark same-assertion · Open/resolve contradiction record · Switch confirmed vs provisional mode · Navigate parent/child Events |
| Default visibility | **Live** claims (and open research objects) only. Proposed appears in optional review overlay / provisional mode — never as silent evidence |
| Solo chrome | Single curator; no RBAC, no multi-reviewer queues, no social proof. Review and compare share the same lifecycle gates (#9) |

---

## Core principle

> **Reconstruct and cross-check the story of a real-world happening across seed-channel Tellings.**  
> The timeline answers *which happenings exist and in what order*.  
> Multi-telling answers *who said what, when (in which video), where they agree or conflict, what is missing, and how to re-open the source media*.  
> Claims remain recorded assertions — not truth verdicts. Uncertainty stays legible via provisional identity and open questions.

Standing contracts honored:

- Event ≠ video beat; Telling ≠ Event (#4).
- Live atomic claims are compare units; two videos → two claim nodes (#6).
- Jump-to-media requires resolvable claim → processed → raw path (#7).
- Agreement / conflict / gaps are first-class research surfaces (#8).
- Approve-from-compare reuses human-approval checklists; AI never sets live (#9).
- Topics filter lists; they do not scope identity (#11).
- No composite trust scores; optional person×event consistency notes only (#10).

---

## Dual spine (normative IA)

```
┌─────────────────────────────────────────────────────────────────┐
│  EVENT TIMELINE                                                 │
│  browse / filter / select happenings                            │
│  → choose focus Event or open provisional bundle                │
└────────────────────────────┬────────────────────────────────────┘
                             │ enter compare
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  MULTI-TELLING COMPARE                                          │
│  claims × tellings of that focus                                │
│  agreement · conflict · gaps · provenance jumps · min actions   │
└─────────────────────────────────────────────────────────────────┘
```

| Spine half | Job | Does **not** |
|------------|-----|--------------|
| **Event timeline** | Index world happenings by identity keys (name, time, place, actors); show density of Tellings/claims; surface identity uncertainty and open questions at Event grain | Treat a Topic as a timeline node; treat a video chapter as an Event |
| **Multi-telling compare** | Line up ≥1 Telling of the focus; present claims as compare rows; surface agreement, conflict, gaps; enable media jump and research actions | Collapse paraphrases into one claim id; auto-merge Events; show assumptions as evidence |

**Navigation rule:** Timeline → select focus → Compare. Compare may deep-link *back* to related Events (parent/child, related hearing, provisional peers) without losing the current focus context until the curator explicitly changes focus.

---

## Modes

| Mode | When | Default compare content |
|------|------|-------------------------|
| **Confirmed Event** | Focus is a single Event ID the curator treats as confirmed (or non-provisional working node) | Live claims with `ABOUT_EVENT` = focus; open contradiction records; open OQs on that Event; derived coverage |
| **Provisional bundle** | Curator (or approved research state) explicitly compares two+ Event candidates linked by provisional identity | Claims bound to any member of the bundle, **badged by which Event ID they currently hang on**; identity OQs **prominent**; no presentation that implies confirmed merge |
| **Review overlay** (optional, not default evidence) | Curator wants speed-approve proposed claims about the focus | Proposed claims **badged** `proposed`; approving runs full #9 checklist. Still not “live graph evidence” until live |

**Illegal UX:** Silent “compare as same” that hides provisional state. Silent inclusion of proposed claims in agreement/conflict counts.

---

## Default layout sections

Sections are **IA regions** (what information must be available and groupable). Order below is **recommended reading order**, not a pixel layout.

### A — Event timeline surface

| Section | Must include (content, not chrome) | Notes |
|---------|-------------------------------------|-------|
| **A1. Timeline identity strip** | Product context: personal research tool; seed-channel corpus scope (Jesse Michels, Area52, Danny Jones; ~30-video pilot) as filterable source set | No multi-user identity switcher |
| **A2. Filters** | Time window; Topic (taxonomy); channel / video; identity state (`confirmed` / `provisional` / has open identity OQ); “has multi-telling” (≥2 Tellings or ≥2 source videos); search by public name / alias | Topics **filter** only |
| **A3. Chronological Event list** | Each row: canonical display name + aliases hint; time window; place/theater summary; principal actors summary; Telling count (distinct videos/segments); live claim count; open contradiction count; open OQ count; identity-state badge | Sort primary = Event time window (not upload date) |
| **A4. Nested structure** | Parent/child affordance when nesting exists (campaign → day/encounter). Selecting a child changes focus; parent remains navigable | Shallow trees per #4 |
| **A5. Related but distinct** | Links to related Events that must **not** be merged (e.g. 2017 video release related to 2004 *Nimitz*; public hearing vs closed session) | Relation labels may be coarse in v1 |
| **A6. Provisional / duplicate hints** | “Possible duplicate of…” / provisional identity peers; entry to provisional-bundle compare | Never auto-collapse |
| **A7. Entry actions** | Open multi-telling compare for this Event; open provisional bundle compare when peers exist | Primary research path |

**Timeline empty / sparse states:** Show honest empty (“no live claims yet”, “single telling only”) — not fake multi-telling density.

### B — Multi-telling compare surface

| Section | Must include | Notes |
|---------|--------------|-------|
| **B1. Focus header** | Focus Event (or bundle) display name; identity keys summary (K1–K4 at least: name, time, place, actors); identity state; child Events list if any; related distinct Events (exit ramps); Topic chips as **filters**, not identity | Bundle mode: list member Event IDs + identity OQ |
| **B2. Telling strip** | One card/column entry per **Telling**: video identity (title, channel, `video_id`), segment span if not whole video, primary speakers (Persons), claim count for this focus, link to open video | Telling = account of the focus Event in a video/segment (#4) — not a claim |
| **B3. Claims board (primary work surface)** | Rows = **live atomic claims** about the focus (optionally live inferences, badged). Each row exposes the **comparison dimensions** below. Groupable by facet and/or by Telling | Default filter: live only |
| **B4. Agreement panel** | Derived clusters from `SAME_ASSERTION_AS` / `SUPPORTS` among live claims (and badged inferences). Show speakers + Telling sources per cluster | Do **not** collapse claim ids |
| **B5. Conflict panel** | Open **Contradiction records** for the focus: poles (claim/inference texts), speakers, facet, links to jump-to-media on each pole, status | Resolved/wontfix filterable; default = active `open` |
| **B6. Gaps & open questions** | (1) Derived **coverage** summary by facet (empty / thin / covered); (2) **Open Questions** with kind badge (`identity`, `claim_conflict`, `coverage_gap`, `key_disagreement`, `attribution`, `other`) | Identity OQs elevated in provisional mode |
| **B7. Provenance / media region** | For the selected claim (or contradiction pole): video, timestamp span, quote span, speaker Person + label path, grounding path honesty (processed present) | Powers **jump to timestamp** |
| **B8. Scaffolding panel (secondary)** | Live **assumptions** that inferences about this focus rest on — clearly labeled non-evidence | Never mixed into B4/B5 evidence tables |
| **B9. Credibility side (optional, non-primary)** | Person role labels + curator notes + person×event consistency observations when present (#10) | **No** trust scores, stars, or reliability % |

### Section minimum for v1 pilot

**Must ship conceptually** for the dual spine:

- Timeline: A2 (basic filters), A3, A6, A7  
- Compare: B1, B2, B3, B4, B5, B6, B7  

**Nice-to-have same pilot, not blockers:**

- Deep nesting UI (A4), rich related-graph (A5), B8, B9, full facet matrix polish  

**Explicitly out of v1 IA:**

- Multi-user assignment, comment threads as social product, public share links, “community consensus” meters, score-primary speaker chrome, topic-as-compare-focus mode

---

## Comparison dimensions (normative)

Each claim row (and each contradiction pole) must make these dimensions recoverable. They are the **axes of multi-telling research**, not CSS columns.

### D1 — Who said it

| Element | Source |
|---------|--------|
| **Person** | `ATTRIBUTED_TO` active Person |
| Role context (optional) | Host / guest / witness_participant etc. when labeled (#10) |
| Unresolved | Not a default compare unit; if shown at all, hard-badge and exclude from agreement/conflict counts |

### D2 — What was asserted

| Element | Source |
|---------|--------|
| **`claim_text`** | Atomic normalized proposition (#6) |
| Claim kind | `world_assertion` \| `meta_speech` \| `self_report` |
| Layer badge | `claim` vs `inference` (inferences always badged) |
| Polarity / modality | When present (denial, hedged, secondhand) — display aids, not layer changes |
| Quote excerpt | Supporting quote for reading; does not replace `claim_text` |

### D3 — When it was said (source time)

| Element | Source |
|---------|--------|
| **Video** | `video_id` + catalog title/channel via raw path |
| **Timestamp span** | Processed `[t_start, t_end)` (denorm on claim recommended) |
| Channel | Inherited from video (seed channels: Jesse Michels, Area52, Danny Jones) |
| Telling membership | Which Telling card this claim belongs to for the focus Event |

### D4 — What world time / place it is about

| Element | Source |
|---------|--------|
| **Focus Event keys** | Header: name, time window, place, actors |
| Claim facet (optional) | e.g. `kinematics`, `object_description`, `origin_explanation`, `time`, `place`, … (#8) |
| Event binding status | `bound` \| `provisionally_bound` \| (unbound claims stay off default board until bound or curator attaches) |

### D5 — Agreement

| Element | Source |
|---------|--------|
| Same assertable peers | `SAME_ASSERTION_AS` links |
| Support | `SUPPORTS` edges |
| Cluster membership | Derived agreement cluster under facet / text similarity assist |

### D6 — Conflict

| Element | Source |
|---------|--------|
| Contradicting poles | `CONTRADICTS` among claim\|inference only |
| Contradiction record | First-class package: facet, members, lifecycle |
| **Not** identity doubt | “Same Event?” → Open Question `identity`, not D6 |

### D7 — Gaps / unsettled research

| Element | Source |
|---------|--------|
| Coverage emptiness | Derived facet matrix |
| Open questions | First-class OQ objects (#8) |
| Assumptions | Scaffolding only (B8) — visible gap, not opposing claim |

### D8 — Provenance honesty

| Element | Source |
|---------|--------|
| Grounding path | claim → processed → raw (#7) |
| Extraction run | Via claim / processed run ids (for distrust/re-run, not primary UI) |
| Lifecycle | `live` (default); `proposed` only in review overlay |
| Approval | Live implies curator `APPROVED_BY` existed (#9) |

### Dimension matrix (what default compare must answer)

| Question curator asks | Dimensions | Section home |
|----------------------|------------|--------------|
| Who said what? | D1 + D2 | B3 |
| In which video, at what time? | D3 + D8 | B2, B3, B7 |
| About which happening? | D4 + B1 | B1, B3 |
| Do tellings align? | D5 | B4 |
| Do tellings conflict? | D6 | B5 |
| What’s missing / unresolved? | D7 | B6 |
| Can I hear/see the source? | D3 + D8 | B7 + **jump** action |

---

## Minimum actions (v1)

### Must-have (ticket normative three + implied enablement)

| Action | Effect | Rules |
|--------|--------|-------|
| **1. Approve claim** | `proposed` → `live` for a claim about the focus (optionally co-approve processed + episode map in one atomic action) | Full claim checklist (#6/#7/#9). Never bypass attribution or grounding path. Batch only if each node is checklist-green |
| **2. Mark open question** | Create (or promote to `open`) an **Open Question** anchored to the focus Event / provisional bundle, optionally linked to claims, contradiction, or facet | Curator-owned open/resolve. AI may only leave `proposed` candidates. Kinds per #8 |
| **3. Jump to timestamp** | Open/focus the source media at the claim’s (or pole’s) **provenance timestamp span**, with quote context | Requires resolvable media path. Prefer primary `EXTRACTED_FROM` span; if multiple supports, jump to primary and list others |

These three are the **minimum interactive contract** for the compare surface. Without them, multi-telling is a static dump.

### Strongly recommended (same pilot if cheap)

| Action | Effect |
|--------|--------|
| **Reject claim** | `proposed` → `rejected` (optional reason) |
| **Bind claim to Event** | Add `ABOUT_EVENT` when text unchanged; supersede if meaning changes |
| **Mark same assertion** | Add `SAME_ASSERTION_AS` between two **live** claims (ids remain distinct) |
| **Propose / open contradiction** | Package conflict poles into Contradiction record (+ edges) under focus |
| **Resolve / wontfix** contradiction or OQ | Lifecycle transitions per #8; claims remain live |
| **Switch mode** | Confirmed Event ↔ Provisional bundle |
| **Change focus** | Parent/child or related Event; preserve trail back |
| **Correct claim** | New same-layer claim + `SUPERSEDES` (#9) — not in-place live edit |
| **Filter by Topic / channel / facet / speaker** | View filters only |

### Forbidden actions / anti-patterns

| Forbidden | Why |
|-----------|-----|
| Auto-live claims from compare similarity | #9 live gate |
| Collapse two claims into one id on “agree” | #6 `SAME_ASSERTION_AS` keeps two nodes |
| Treat assumption as conflict pole | #3 / #8 |
| Silent Event merge from compare | #4 curator merge only |
| Jump without a real timestamp path | Fake media honesty |
| Trust-score sort of speakers | #10 |
| Topic-scoped “compare all Navy UAP as one Event” | #11 / #4 |
| Multi-user assign / approve-as-someone-else | Solo tool |

---

## Claims board — row information contract

For each default-visible claim row, the surface must expose (directly or one expand away):

1. **`claim_text`**  
2. **Person** (`ATTRIBUTED_TO`)  
3. **Telling / video** identity  
4. **Timestamp span** (and jump affordance)  
5. **Lifecycle** badge (`live`; `proposed` only in overlay)  
6. **Layer** badge if inference  
7. **Event binding** badge if provisional  
8. **Facet** when set  
9. Links into **agreement cluster** and/or **contradiction record** membership when any  
10. **Primary quote** (or expand-to-quote)

Optional one-expand-away: modality, extraction confidence (review assist only), run id, full grounding path, related OQs.

---

## Agreement, conflict, and gaps (UX contracts from #8)

### Agreement

- Primary: clusters of live claims linked by `SAME_ASSERTION_AS` and/or mutual `SUPPORTS`.  
- Display: shared assertable summary + list of (Person, video, timestamp, claim_text).  
- Action: jump per member; optional “mark same assertion” for curator-confirmed paraphrase pairs.  
- **Never** delete or merge claim nodes when agreeing.

### Conflict

- Primary: **open Contradiction records** on the focus (or bundle).  
- Display: facet, N poles (≥2), each pole’s who/what/when + jump.  
- Identity uncertainty is **not** listed here — it lives under Open Questions (`identity`) and provisional header state.  
- Resolving a record does **not** remove live claims or mint a truth verdict.

### Gaps

- Derived: facets with zero (or curator-defined inadequate) live claims.  
- First-class: OQ `coverage_gap` when the curator wants a tracked TODO.  
- **Do not** invent opposing claims to fill empty cells.

### Summary counts (derived, optional header chips)

Illustrative honesty metrics on the focus:

- N Tellings · N live claims · N agreement clusters · N open conflicts · N open OQs · coverage “empty facets” count  

Counts use **live / open** research state only in default mode.

---

## Provenance and jump-to-timestamp (normative)

### Jump target resolution

```
Selected claim (or contradiction pole)
  → primary EXTRACTED_FROM processed span
      → video_id
      → [t_start, t_end)
      → quote text
      → speaker_label (+ Person via episode map)
  → open media at t_start (highlight span through t_end when player allows)
```

| Case | Behavior |
|------|----------|
| Single support span | Jump there |
| Multiple `EXTRACTED_FROM` | Jump primary; list alternates |
| Inference selected | Jump not direct — expand `BASED_ON` claims; user jumps a premise claim |
| Assumption selected | **No** media jump as evidence; show “no source quote (scaffolding)” |
| Broken path | Action disabled + explicit “grounding incomplete” — do not invent a time |

### What jump must never do

- Open a random point in the video because “the Event was discussed somewhere.”  
- Jump using upload date or channel home.  
- Present host paraphrase timestamps as the guest’s claim grounding.

---

## Lifecycle visibility (compare vs review)

| Object state | Default compare (evidence) | Review overlay / queue |
|--------------|----------------------------|-------------------------|
| Claim `live` | **Yes** | Yes |
| Claim `proposed` | **No** | Yes (approve/reject) |
| Claim `rejected` / `superseded` | No (history toggle optional) | Audit |
| Contradiction `open` | **Yes** (conflict panel) | Yes |
| Contradiction `proposed` | No | Yes |
| OQ `open` | **Yes** | Yes |
| OQ `proposed` | No | Yes |
| Assumption `live` | Scaffolding panel only | Yes |
| Inference `live` | Yes if badged | Yes |

Approve/reject from compare **are the same gates** as the video approval bundle (#9) — shortcuts, not a second lifecycle.

---

## Seed pilot framing (Jesse Michels · Area52 · Danny Jones)

IA must work for the committed ~30-video pilot patterns:

| Pattern | Timeline expectation | Compare expectation |
|---------|---------------------|---------------------|
| Shared famous case (*Nimitz* / Tic Tac) across channels | One focus Event; multiple Tellings | Full agreement/conflict value |
| Long single-guest deep dive (e.g. TD Barnes on Danny Jones) | Many Events from one video | Compare may be single-Telling + later multi when other channels hit same Events |
| Synthesis / panel (Jesse, Area52) | Host framing + guest claims | Strict attribution; host meta_speech optional/minimal |
| Related disclosure Events (hearing vs encounter vs media release) | Distinct timeline nodes + related links | Do not force one compare focus |
| Moon photo / thematic thesis without fixed keys | Prefer Topic + unbound claims; Event only when keys exist | No mega-Event “all censorship” compare |

**Sparse honesty:** “Only 1 Telling in corpus” is a valid compare state — still show claims, OQs, and jumps; agreement/conflict panels may be empty without shame UI.

---

## Worked IA walkthrough (illustrative)

### Focus: *Nimitz* / Tic Tac (2004) — confirmed Event

1. **Timeline:** Event row shows time ≈ Nov 2004, SOCAL, Fravor/Nimitz keys; Telling count ≥2 (e.g. Danny Jones interview + Area52/Jesse synthesis).  
2. **Open compare (confirmed mode):** Header keys + Topics `Navy UAP` as filters.  
3. **Telling strip:** Video A (Danny / guest Fravor), Video B (synthesis channel).  
4. **Claims board:** Live atomic claims — shape, no rotors, kinematics, etc. — each with Person + jump.  
5. **Agreement:** Cluster on “no visible propulsion / no rotors” via `SAME_ASSERTION_AS`.  
6. **Conflict:** Open record if another live claim asserts conventional jet plume / pure terrestrial drone as incompatible pole.  
7. **Gaps:** Empty `sensors` facet → derived gap; curator **marks OQ** “Which platform held primary radar track?”  
8. **Actions:** Jump to Fravor quote; approve a still-proposed atomic split claim; mark OQ.

### Provisional bundle

1. Video mentions “Tic Tac-like 2015 East Coast” provisionally linked to 2004 *Nimitz*.  
2. Compare mode = **provisional bundle**; identity OQ “Same incident as Nimitz 2004?” is header-prominent.  
3. Claims stay on their Event IDs; no silent merge; conflict table only among claims the curator treats as co-focused under the bundle.

---

## Downstream contracts

### Implementers may assume

- Dual surfaces: timeline + compare; Event-scoped focus.  
- Section set B1–B7 as required information regions.  
- Dimensions D1–D8 available per claim row.  
- Min actions: approve claim, mark open question, jump to timestamp.  
- Data dependencies satisfied by #4–#11 decision assets already recorded.

### What this ticket does **not** require

- Exact column vs card layout, density, fonts, breakpoints.  
- Player technology (YouTube embed vs local).  
- Keyboard shortcuts, command palette, or animation.  
- NLI thresholds for proposing agreement/conflict (detectors stay propose-only).  
- Storage schema or API shapes.

---

## Policy cheat-sheet

```
Spine?
  → Event timeline + multi-telling compare
  → Focus = confirmed Event OR explicit provisional bundle
  → Topics filter only — never compare identity

Compare units?
  → Live atomic claims (primary)
  → Live inferences only if badged
  → Assumptions never as evidence rows

Default sections (compare)?
  → Focus header · Telling strip · Claims board
  → Agreement · Conflict · Gaps/OQs · Provenance/media

Dimensions?
  → Who · What · When-said (video+time) · About (Event/facet)
  → Agreement · Conflict · Gaps · Provenance · Lifecycle

Min actions?
  → Approve claim (same #9 gates)
  → Mark open question (curator opens)
  → Jump to timestamp (via claim→processed→raw)

Never?
  → Proposed-as-silent-evidence
  → Trust scores
  → Topic-as-Event compare
  → Collapse claim ids on agree
  → Assumption poles in conflict table
  → Multi-user product chrome
```

---

## Decision log

| Date | Decision |
|------|----------|
| 2026-07-22 | Adopt dual-spine IA (event timeline + multi-telling compare); Event/provisional-bundle focus only; default sections A2–A3/A6–A7 + B1–B7; comparison dimensions who/what/when-said/about/agreement/conflict/gaps/provenance; min actions approve claim, mark open question, jump to timestamp; live atomic claims as units; solo-tool chrome; no visual design in this asset. |

## Decision date

Recorded 2026-07-22 as the recommended resolution for issue #14 (batch completion with recommended defaults; no interactive grilling).

---

## Sources / related

1. Issue #14 — Multi-telling compare UX requirements — https://github.com/etai83/uap-kg/issues/14  
2. Issue #4 — [event-identity-rule.md](./event-identity-rule.md)  
3. Issue #6 — [claim-model.md](./claim-model.md)  
4. Issue #7 — [provenance-minimum.md](./provenance-minimum.md)  
5. Issue #8 — [contradiction-and-open-question-model.md](./contradiction-and-open-question-model.md)  
6. Issue #9 — [human-approval-workflow.md](./human-approval-workflow.md)  
7. Issue #10 — [speaker-credibility-signals-v1.md](./speaker-credibility-signals-v1.md)  
8. Issue #11 — [topics-vs-events.md](./topics-vs-events.md)  
9. Issue #2 — [seed-channel-set-v1.md](./seed-channel-set-v1.md)  
