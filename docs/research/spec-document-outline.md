# Spec document outline

Decision asset for [Spec document outline](https://github.com/etai83/uap-kg/issues/15)  
Part of [Wayfinder: UAP YouTube knowledge graph spec](https://github.com/etai83/uap-kg/issues/1)

## Question

What **sections and depth** must the final system+product **spec** contain so it is **implementable without reopening model debates**?

Decide: outline of the spec document and exit criteria for “spec complete” relative to closed wayfinder tickets.

---

## Decision summary

| Axis | Decision |
|------|----------|
| Spec role | **Normative system + product specification** for a personal UAP/NHI research KG from YouTube — **not** an implementation plan, build, or prototype |
| Primary path | Write decision asset here; assemble the actual v1 spec at **`docs/spec/uap-kg-v1.md`** as a skeleton that **points into** closed research assets (prefer pointers + short normative restatements over full rewrites) |
| Section mapping | Spec sections map **1:1** to closed model areas (tickets #2–#14 + ingestion/diarization research) plus product framing and deferred appendix |
| Depth bar | Each normative section must state: **decided rules**, **legal/illegal examples or cheat-sheet**, **live-gate / lifecycle**, and **pointers** to the research asset for full worked examples |
| Spec complete ≠ product built | Completing the written spec is the **map destination**. Building pipeline, DB, or UI is **out of scope** for map #1 |
| Exit: map complete | Outline **accepted** (this ticket resolved) **AND** all decision tickets closed **AND** fog either graduated into the spec **or** listed explicitly as deferred/out-of-scope |
| Exit: spec complete | `docs/spec/uap-kg-v1.md` fills every required section to the depth bar below, with no open “must decide before implement” holes on closed-ticket subjects |

---

## What “implementable without reopening model debates” means

An implementer (human or agent) can:

1. **Name every first-class object** (layers, entities, research objects) using glossary terms from `CONTEXT.md`.
2. **Enforce write-path legality** (provenance matrix, content-edge participants, identity gates) without inventing policy.
3. **Build review + multi-telling UX** that only exposes already-decided actions and dimensions.
4. **Pick tech later** (storage, exact models, wireframes) without reopening ontology, identity, claim shape, or approval rules.

If a choice is still required for a *product* build but was never a wayfinder ticket, it belongs in **Appendix: deferred / open** — not as silent ambiguity in the normative body.

---

## Recommended document path and packaging

| Artifact | Path | Role |
|----------|------|------|
| This decision (outline + exit criteria) | `docs/research/spec-document-outline.md` | Ticket #15 answer; map pointer |
| **Canonical v1 spec** | **`docs/spec/uap-kg-v1.md`** | Destination of map #1; single reading surface for implementers |
| Decision assets (normative detail) | `docs/research/*.md` | Authoritative long-form; spec **must not contradict** them |
| Ubiquitous language | `CONTEXT.md` | Glossary; spec uses these terms only |

### Assembly rules for `docs/spec/uap-kg-v1.md`

1. **One document**, sectioned per outline below.  
2. Prefer **short normative restatement + link** to the research asset over copying whole research docs.  
3. Worked examples may stay in research assets; the spec needs **enough** examples (or pointers) that the rule is unambiguous.  
4. Where research assets conflict (they should not), **later closed ticket + map Decisions-so-far** win; record an explicit conflict note rather than silent merge.  
5. Implementation tech (graph DB, UI framework, ASR vendor SKUs) stays **out of normative body** unless a research ticket already constrained it (ingestion ToS path, diarization default stack as *recommendation*).

---

## Spec outline (required sections)

Depth codes:

| Code | Meaning |
|------|---------|
| **N** | Normative rules (must / must not / may) — implementers treat as law |
| **P** | Product behavior / UX IA (information architecture, not pixels) |
| **R** | Recommended default stack / path (changeable without reopening ontology) |
| **X** | Explicit non-goals / deferred — no silent fog |

### 0. Front matter

| Subsection | Depth | Content | Source |
|------------|-------|---------|--------|
| 0.1 Title, version, status | N | `uap-kg` system+product spec v1; status `skeleton` → `spec-complete` | this ticket |
| 0.2 Product one-liner | N | Personal UAP/NHI research KG from curated YouTube; sole curator; primary job: reconstruct & cross-check stories | map #1 |
| 0.3 Non-goals of this document | X | No pipeline build; no multi-user product; no open scrape | map #1 Out of scope |
| 0.4 How to read | N | Glossary in `CONTEXT.md`; decision assets are normative detail; deferred appendix is not optional reading for scope | this ticket |
| 0.5 Ticket → section index | N | Table mapping GitHub issues #2–#15 to section numbers | this ticket |

### 1. Product framing and v1 scope

| Subsection | Depth | Content | Source |
|------------|-------|---------|--------|
| 1.1 User and job | N | Solo curator; reconstruct & multi-telling cross-check | map #1 |
| 1.2 Seed channel set | N | Exactly 3 committed channels; English/YouTube only; expansion freeze until pilot fixed | #2 → `seed-channel-set-v1.md` |
| 1.3 Pilot corpus | N | ~10 videos/channel (~30); curator selects all; long-form preferred not hard reject | #2 |
| 1.4 In scope / out of scope | N+X | What v1 product covers vs never (public multi-user, bulk scrape, auto-live AI claims) | map #1 + all tickets |
| 1.5 Standing preferences (locked) | N | Hard layers; person nodes; Event≠beat; AI propose / human live; dual UX spine | map #1 |

### 2. Source intake (YouTube)

| Subsection | Depth | Content | Source |
|------------|-------|---------|--------|
| 2.1 Metadata path | R+N | YouTube Data API v3 for catalog; stable IDs; volatile stats cache policy | #12 → `youtube-ingestion-options.md` |
| 2.2 Transcript tiers | R+N | Owner export / manual / weak proxies preferred; no bulk third-party caption scrape as default | #12 |
| 2.3 Audio / ASR posture | R+X | Automated AV download as standing architecture called out as risk; personal ASR path constraints | #12 |
| 2.4 Playback | N | Link/embed YouTube; do not require local AV archive for product correctness | #12 |
| 2.5 Catalog exception | N | Catalog raw may auto-land live | #3, #7, #9 |

### 3. Speech pipeline (ASR + diarization)

| Subsection | Depth | Content | Source |
|------------|-------|---------|--------|
| 3.1 Two problems | N | Diarization (`SPEAKER_n`) ≠ name attribution → Person | #13, #5 |
| 3.2 Default stack | R | WhisperX + pyannote (local) default; AssemblyAI when hosted name ID needed | #13 → `speaker-diarization-options.md` |
| 3.3 Good-enough bar | N | Quality targets + human review before person writes | #13 |
| 3.4 Failure modes | N | What the system must surface for review (split/merge speakers, ads, unknown) | #13, #5 |

### 4. Epistemic layer ontology

| Subsection | Depth | Content | Source |
|------------|-------|---------|--------|
| 4.1 Five layers | N | `raw` → `processed` → `claim` → `inference` → `assumption`; machine ids fixed | #3 → `epistemic-layer-ontology.md` |
| 4.2 Node vs edge | N | Layer on nodes only; edges have `edge_kind` provenance \| content | #3 |
| 4.3 Immutability and promotion | N | No in-place layer rewrite; promotion = new node + provenance | #3 |
| 4.4 Legal matrices | N | Provenance and content endpoint rules; illegal shortcuts | #3 |
| 4.5 AI rights vs curator | N | Propose vs live; catalog exception; illegal promotions | #3, #9 |

### 5. Provenance minimum

| Subsection | Depth | Content | Source |
|------------|-------|---------|--------|
| 5.1 Media anchors | N | video_id, channel, timestamp spans, track refs | #7 → `provenance-minimum.md` |
| 5.2 Extraction run | N | First-class process identity; tool/model + time | #7 |
| 5.3 Required chain by layer | N | Claim→processed→raw; inference via claims; assumption scaffolding | #7 |
| 5.4 Field checklist | N | Ticket’s named minimum fields | #7 |
| 5.5 Validation / hard rejects | N | No claim→raw-only live; no assumption-as-evidence | #7, #3 |

### 6. Claim model

| Subsection | Depth | Content | Source |
|------------|-------|---------|--------|
| 6.1 Definition and boundaries | N | Claim vs inference vs assumption; not truth verdict | #6 → `claim-model.md` |
| 6.2 Atomicity | N | One proposition per live claim; compound split rules | #6 |
| 6.3 Schema fields (spec-level) | N | Identity, kinds, attribution, aboutness, grounding | #6 |
| 6.4 Relations | N | EXTRACTED_FROM, ABOUT_EVENT, SAME_ASSERTION_AS, etc. | #6 |
| 6.5 Multi-speaker dialogue | N | Who is attributed; host vs guest defaults | #6 |
| 6.6 Unbound claims | N | Prefer unbound over inventing Events | #6, #4 |

### 7. Event identity and Tellings

| Subsection | Depth | Content | Source |
|------------|-------|---------|--------|
| 7.1 Event ≠ beat | N | Real-world happening vs video structure | #4 → `event-identity-rule.md` |
| 7.2 Identity keys | N | Name, time, place, actors/platforms, optional docs | #4 |
| 7.3 Merge / split / nesting | N | Weighted sameness; parent/child; multi-day | #4 |
| 7.4 Uncertainty | N | Provisional identity link + open question; no silent high-stakes merge | #4, #8 |
| 7.5 Telling | N | Account of Event in a video/segment | #4 |
| 7.6 Lifecycle hooks | N | Curator-approved merge/split for live | #4, #9 |

### 8. Topics (vs Events)

| Subsection | Depth | Content | Source |
|------------|-------|---------|--------|
| 8.1 Topic ≠ Event | N | Thematic type vs instance happening | #11 → `topics-vs-events.md` |
| 8.2 Controlled taxonomy | N | Lightweight Topic nodes; curator-owned seed list | #11 |
| 8.3 Attachment points | N | Primary: Event + Claim; surface tags at processed | #11 |
| 8.4 Non-keys | N | Topics never Event identity keys; no mega-Event collapse | #11, #4 |
| 8.5 v1 minimum | N | ~15–40 seed terms; free tags not live Topics | #11 |

### 9. Speaker identity and aliases

| Subsection | Depth | Content | Source |
|------------|-------|---------|--------|
| 9.1 Label ≠ Person | N | SPEAKER_n episode-local only | #5 → `speaker-identity-and-alias-merge.md` |
| 9.2 Person lifecycle | N | proposed → candidate → active / merged-away / deprecated | #5 |
| 9.3 Episode attribution | N | Label → Person map; host defaults for seed channels | #5 |
| 9.4 Alias policy | N | Typed aliases; normalization vs display | #5 |
| 9.5 Unknown / unresolved | N | No unknown person nodes | #5 |
| 9.6 Merge / split evidence | N | Multi-signal; human gate for live merge | #5 |
| 9.7 Confidence guidance | R | Numeric proposal thresholds only; false-reject preferred | #5 |

### 10. Speaker credibility (v1)

| Subsection | Depth | Content | Source |
|------------|-------|---------|--------|
| 10.1 Soft metadata | N | Not layer, not identity, not truth verdict | #10 → `speaker-credibility-signals-v1.md` |
| 10.2 In-scope signals | N | Curator notes; role labels; consistency observations | #10 |
| 10.3 Hard forbids | N | No composite trust scores as objective metrics | #10 |
| 10.4 Live gate | N | Live annotations curator-owned | #10, #9 |

### 11. Contradiction, agreement, gaps, open questions

| Subsection | Depth | Content | Source |
|------------|-------|---------|--------|
| 11.1 Compare surfaces | N | Agreement, conflict, gaps on focus Event / provisional bundle | #8 → `contradiction-and-open-question-model.md` |
| 11.2 Content edges | N | SUPPORTS / CONTRADICTS / SAME_ASSERTION_AS; claim\|inference only | #8, #6 |
| 11.3 Contradiction record | N | First-class research object; fields + lifecycle | #8 |
| 11.4 Open Question | N | Kinds + lifecycle proposed→open→resolved\|wontfix | #8 |
| 11.5 Coverage gaps | N | Derived and/or open question; not invented claims | #8 |
| 11.6 Identity vs claim conflict | N | Identity OQ ≠ claim contradiction | #8, #4 |
| 11.7 Assumptions | N | Never evidence poles | #8, #3 |

### 12. Human approval workflow

| Subsection | Depth | Content | Source |
|------------|-------|---------|--------|
| 12.1 Lifecycle states | N | proposed / live / rejected / superseded | #9 → `human-approval-workflow.md` |
| 12.2 Who may write live | N | Curator only for gated objects | #9 |
| 12.3 Auto-land vs must-approve | N | Catalog raw exception; everything extraction-derived gated | #9 |
| 12.4 Live checklists | N | Per-layer approve gates | #9 |
| 12.5 Bundles, batch, atomic co-approval | N | Video-scoped default; dependency closure | #9 |
| 12.6 Supersession | N | New same-layer node + SUPERSEDES | #9 |
| 12.7 Queues / surfaces (IA) | P | Review surfaces conceptual, not wireframes | #9 |

### 13. Multi-telling product UX

| Subsection | Depth | Content | Source |
|------------|-------|---------|--------|
| 13.1 Dual spine | P+N | Event timeline + multi-telling compare | #14 → `multi-telling-compare-ux.md` |
| 13.2 Focus scope | N | Focus Event or provisional identity bundle | #14, #4 |
| 13.3 Default sections | P | Timeline sections; compare sections | #14 |
| 13.4 Comparison dimensions | N | Who / what / when said / about / agree / conflict / gaps / provenance | #14 |
| 13.5 Minimum actions | N | Approve claim; mark open question; jump to timestamp | #14 |
| 13.6 Forbidden UX | N | Trust-ranked speaker cards as primary; assumptions as evidence rows; topic-as-Event | #14 |
| 13.7 Visibility | N | Live default; proposed only in review/provisional | #14, #9 |

### 14. End-to-end object catalog (implementation checklist)

| Subsection | Depth | Content | Source |
|------------|-------|---------|--------|
| 14.1 Layered nodes | N | raw, processed, claim, inference, assumption | #3–#7 |
| 14.2 Entities | N | Channel, Video, Person, Alias, Event, Topic, Telling (as modeling concept) | #2–#5, #11 |
| 14.3 Research objects | N | Contradiction record, Open Question, consistency observation, approval bundle | #8–#10, #9 |
| 14.4 Edge catalog | N | Provenance predicates + content predicates + SUPERSEDES | #3, #6–#8 |
| 14.5 Orthogonal axes | N | Layer × lifecycle × identity state | #3, #5, #9 |

### 15. Worked scenarios (normative intent)

| Subsection | Depth | Content | Source |
|------------|-------|---------|--------|
| 15.1 Clean 2-speaker interview path | N | Catalog → diarize → map → claims → batch approve → compare | #5, #9, #14 + seed |
| 15.2 Cross-channel multi-telling | N | Shared Event, agreement + conflict + jump | #4, #8, #14 |
| 15.3 Uncertain Event identity | N | Provisional bundle + identity OQ | #4, #8, #14 |
| 15.4 Correction after live | N | Supersession, not patch | #9 |
| 15.5 Illegal paths (must fail) | N | Assumption-as-claim; claim without grounding; silent person merge | #3, #5–#7 |

*(Full narrative examples may live in research assets; this section restates pass/fail intent.)*

### 16. Glossary pointer

| Subsection | Depth | Content | Source |
|------------|-------|---------|--------|
| 16.1 Canonical terms | N | “Use `CONTEXT.md`; do not introduce synonyms for typed concepts” | `CONTEXT.md` |
| 16.2 Spec-local abbreviations | N | Only if needed (e.g. OQ = open question) | this ticket |

### Appendix A — Deferred / open (explicit fog graduation)

Every map “Not yet specified” item and research “intentionally does not decide” item lands here as **deferred**, **out of scope for v1**, or **curator operational task** — never as silent holes in §§1–15.

| Item | Disposition | Notes |
|------|-------------|-------|
| Graph storage / query technology | **Deferred** | Choose after model locked; any store must express nodes/edges/lifecycle |
| Scale beyond pilot corpus / full-channel ingest | **Deferred** | v1 channel count fixed at 3 until pilot complete |
| Non-English / multi-language | **Out of scope v1** | English-only (#2) |
| Non-YouTube sources (PDF, podcasts, docs) | **Out of scope v1** | Destination is YouTube-sourced |
| Composite credibility / trust scores | **Out of scope v1** | Qualitative only (#10) |
| Export / publish / share of subgraphs | **Deferred** | Personal tool; no publish product |
| Refresh cadence for new channel uploads | **Deferred** | Operational; catalog path reusable |
| Exact seed Topic catalog (~15–40 terms) | **Deferred (curator)** | Rules decided (#11); list content is curator-owned |
| Remaining pilot video picks (~27) | **Curator operational** | Does not reopen seed rules (#2) |
| Legal risk treatment of personal ASR on third-party audio | **Deferred (policy)** | Ingestion research documents risk; product must not pretend ToS-free | #12 |
| Exact ASR/diarization vendor thresholds & SKUs | **Recommended only** | #13 defaults; swap without ontology change |
| Wireframes, keyboard shortcuts, notifications | **Out of scope of model spec** | IA is normative; pixels are not (#9, #14) |
| Multi-user roles / RBAC / collaboration | **Out of scope** | Solo curator |
| Numeric DB types, indexes, APIs | **Implementation** | Spec is conceptual fields |
| Automated paraphrase clustering thresholds | **Deferred** | Human gate remains for SAME_ASSERTION_AS (#6) |
| True/false / verified claim flags | **Deferred** | Curator-owned if ever added (#6) |
| Public multi-user product / accounts | **Out of scope** | map #1 |
| Broad opportunistic YouTube scrape | **Out of scope** | map #1 |
| Auto-live publishing of AI claims | **Forbidden** | Standing preference; not deferred |

### Appendix B — Decision asset index

| Ticket | Title | Asset |
|--------|-------|-------|
| #2 | Seed channel set for v1 | `docs/research/seed-channel-set-v1.md` |
| #3 | Epistemic layer ontology | `docs/research/epistemic-layer-ontology.md` |
| #4 | Event identity rule | `docs/research/event-identity-rule.md` |
| #5 | Speaker identity and alias merge | `docs/research/speaker-identity-and-alias-merge.md` |
| #6 | Claim model | `docs/research/claim-model.md` |
| #7 | Provenance minimum | `docs/research/provenance-minimum.md` |
| #8 | Contradiction and open-question model | `docs/research/contradiction-and-open-question-model.md` |
| #9 | Human approval workflow | `docs/research/human-approval-workflow.md` |
| #10 | Speaker credibility signals (v1) | `docs/research/speaker-credibility-signals-v1.md` |
| #11 | Topics vs events relationship | `docs/research/topics-vs-events.md` |
| #12 | YouTube ingestion options | `docs/research/youtube-ingestion-options.md` |
| #13 | Speaker diarization options | `docs/research/speaker-diarization-options.md` |
| #14 | Multi-telling compare UX requirements | `docs/research/multi-telling-compare-ux.md` |
| #15 | Spec document outline (this) | `docs/research/spec-document-outline.md` |
| — | Canonical assembled spec | `docs/spec/uap-kg-v1.md` |

---

## Exit criteria

### A. Outline accepted (this ticket #15)

- [x] Required section list exists and maps 1:1 to closed model areas  
- [x] Depth codes and “implementable without reopening debates” bar defined  
- [x] Canonical path for assembled spec chosen (`docs/spec/uap-kg-v1.md`)  
- [x] Deferred / open appendix enumerates map fog + research non-decisions  
- [x] Glossary gaps for load-bearing terms closed in `CONTEXT.md` (see deliverable)

### B. Decision tickets closed (map prerequisite)

All of the following must be **closed** (or explicitly reopened and re-closed after material change):

| # | Ticket | Status required |
|---|--------|-----------------|
| 2 | Seed channel set | Closed |
| 3 | Epistemic layer ontology | Closed |
| 4 | Event identity rule | Closed |
| 5 | Speaker identity and alias merge | Closed |
| 6 | Claim model | Closed |
| 7 | Provenance minimum | Closed |
| 8 | Contradiction and open-question model | Closed |
| 9 | Human approval workflow | Closed |
| 10 | Speaker credibility signals | Closed |
| 11 | Topics vs events | Closed |
| 12 | YouTube ingestion options | Closed |
| 13 | Speaker diarization options | Closed |
| 14 | Multi-telling compare UX | Closed |
| 15 | Spec document outline | Closed when outline accepted |

### C. Spec complete (destination of map #1)

`docs/spec/uap-kg-v1.md` is **spec complete** when **all** hold:

1. **Sections 0–16 + Appendix A–B present** with no placeholder-only normative holes on closed-ticket subjects.  
2. Each section **points to** its research asset and either restates the decision summary tables or embeds equivalent normative rules.  
3. **Write-path legality** is fully specified: layer matrix, provenance minimum, claim atomicity, identity gates, approval states.  
4. **Product UX IA** is fully specified for dual spine + min actions + forbidden patterns (not wireframes).  
5. **Appendix A** contains every residual fog item as deferred / OOS / curator-ops / forbidden — **no item left only on the map body**.  
6. Spec language uses **`CONTEXT.md` terms** only for domain concepts.  
7. Explicit banner: **Spec complete ≠ product built.** Implementation may start only after C; building is a **new** effort, not map completion work.

**Not required for C:**

- Running code, DB choice, UI pixels  
- Full 30-video pilot list filled  
- Exhaustive seed Topic string list  
- Legal opinion letter on ASR  

### D. Map complete (wayfinder #1)

Map #1 may be considered complete when:

1. **Outline accepted** (A) and ticket #15 resolved  
2. **All decision tickets closed** (B)  
3. **Spec complete** (C) **or** skeleton + outline accepted with explicit remaining prose-fill tasks that do **not** reopen model debates (prefer finish C in the same push as skeleton)  
4. **Fog graduated**: every Notes / Not-yet-specified item is either in the spec body or Appendix A  

**Map complete still means: written spec only — not a product.**

---

## Skeleton strategy (recommended path)

1. Create `docs/spec/uap-kg-v1.md` with full heading tree matching §§0–16 + appendices.  
2. Under each heading: 3–15 lines of normative gist + “**Detail:** `docs/research/...`” + optional “**Open only if:** …” pointing to Appendix A.  
3. Fill Appendix A from map fog + this document.  
4. Do **not** rewrite all research prose into the spec unless a section is too sparse to implement.  
5. When C is met, mark front-matter status `spec-complete` and close map #1 with pointer to the file (separate step; **not** done by this ticket alone if map update is reserved).

---

## Policy cheat-sheet

```
Is this about what the product is and for whom?
  → §1 Product framing

Is this catalog metadata / transcripts / audio?
  → §2 Source intake

Is this who spoke when / ASR labels?
  → §3 Speech pipeline  (Person writes still §9)

Is this layer type / promotion / illegal masquerade?
  → §4 Ontology

Is this “how do we know where this came from?”
  → §5 Provenance

Is this the recorded assertion unit?
  → §6 Claim model

Is this a real-world happening vs a theme vs a video beat?
  → §7 Event  |  §8 Topic  |  §2/§7 beat rules

Is this a named human / SPEAKER_n / merge?
  → §9 Speaker identity

Is this soft trust metadata (not truth of claim)?
  → §10 Credibility

Is this agreement / conflict / gap / open research state?
  → §11 Contradiction & OQ

Is this proposed → live / batch review / supersede?
  → §12 Approval

Is this timeline or compare UI?
  → §13 Multi-telling UX

Is this “which DB / language / pixels / multi-user?”
  → Appendix A (not a model reopening)
```

---

## Decision log

| Date | Decision |
|------|----------|
| 2026-07-22 | Adopt outline §§0–16 + Appendix A deferred fog + Appendix B index; canonical assembled path `docs/spec/uap-kg-v1.md`; exit criteria A–D for outline / tickets / spec complete / map complete; prefer skeleton with decision pointers over full research rewrite. |

## Decision date

2026-07-22
