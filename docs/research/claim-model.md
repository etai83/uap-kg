# Claim model

Decision asset for [Claim model](https://github.com/etai83/uap-kg/issues/6)  
Part of [Wayfinder: UAP YouTube knowledge graph spec](https://github.com/etai83/uap-kg/issues/1)

**Depends on:** [Epistemic layer ontology](./epistemic-layer-ontology.md) (#3), [Event identity rule](./event-identity-rule.md) (#4), [Speaker identity and alias merge](./speaker-identity-and-alias-merge.md) (#5)  
**Status:** Recommended decision (batch grilling with defaults aligned to standing map preferences).  
**Scope:** Spec-level claim definition, v1 fields, atomicity, relations, multi-speaker extraction rules. No DB columns, API, or implementation code.  
**Downstream consumers:** Provenance minimum (#7), Contradiction / multi-telling (#8), Human approval workflow (#9), Multi-telling compare UX (#14).

---

## Question

What is a **claim** in this graph — required fields, allowed relations to event/speaker/source, and how it differs from inference and assumption?

Decide: claim schema for v1, atomicity (one proposition vs compound), and how multi-speaker dialogue becomes claims.

---

## Decision summary

| Axis | Decision |
|------|----------|
| What a Claim is | An **atomic, attributed, checkable assertion** that a **speaker explicitly made** (or a tightly scoped meta-assertion about speech), grounded in processed evidence — **not** a system truth verdict |
| Layer | Always `layer=claim` (immutable). Distinct from `inference` and `assumption` per #3 |
| Atomicity | **Prefer one proposition per claim.** Compound speech is **split** into atomic claims; keep a compound only as temporary AI staging, never live |
| Required for live | `layer`, lifecycle, **claim text**, ≥1 `EXTRACTED_FROM` → processed, `ATTRIBUTED_TO` → Person (or explicit unresolved path — see below), provenance path processed → raw (video + time anchors) |
| Event binding | Prefer `ABOUT_EVENT` when keys support it; **unbound claims** allowed when the world-happening is unclear (do not invent Events) |
| Multi-speaker | **One claim per proposition per speaker-turn (or contiguous same-speaker run).** Never blend two speakers into one claim |
| Host paraphrase | Attribute to the **speaker who uttered the words**. Host restatements of guest points are host claims (or stay processed-only), not silent guest claims |
| Truth / credibility | Out of scope for claim schema; optional later fields are curator-owned and orthogonal |
| Live gate | AI proposes; **curator approves** before live (standing preference) |

---

## Core definition

### Claim (normative)

A **Claim** is a graph node with `layer=claim` that records:

> **Speaker S asserts proposition P**, as grounded in processed utterance/span evidence from a specific video (and timestamps), optionally about a world **Event** E.

Claims are the **unit of narrative comparison** across Tellings, speakers, and videos (see multi-telling UX). They are **recorded assertions**, not endorsements that P is true.

### Claim vs Inference vs Assumption (hard boundaries)

| | **Claim** | **Inference** | **Assumption** |
|--|-----------|---------------|----------------|
| **Source grounding** | Speaker **said** (or clearly asserted) it; requires `EXTRACTED_FROM` processed | **Not** stated as such in the source | No source quote that asserts it |
| **Origin** | Extraction from speech/text | Explicit reasoning over claims (and optional inferences) | Scaffold adopted to fill a gap |
| **Provenance spine** | claim → processed → raw | inference `BASED_ON` claim(s) [+ optional inference] | Used via `RESTS_ON` from inference (or rare claim) |
| **May SUPPORTS / CONTRADICTS?** | Yes | Yes | **No** as evidence (#3, #8) |
| **Typical UAP use** | “Fravor asserts the object had no rotors” | “If custody and analysis claims hold, lab X held anomalous material” | “Place-name ‘the ranch’ co-refers to Skinwalker Ranch” |
| **Illegal relabel** | — | Must not be written as claim | Must not be written as claim or inference |

**Quick tests**

1. *Did a speaker assert this in the grounding spans?* → Claim (or leave as processed).  
2. *Is this a conclusion we draw beyond the transcript?* → Inference.  
3. *Are we filling a gap with an unproven premise?* → Assumption.  
4. *Are we unsure whether the speaker is correct?* → Still a **claim**; uncertainty is not a layer downgrade.

### What is not a claim

| Not a claim | Correct home |
|-------------|--------------|
| Transcript quote / cleaned span | `processed` |
| Video title, channel, publishedAt | `raw` catalog |
| “Therefore the two sightings are the same craft” with no speaker saying so | `inference` (and maybe `assumption` for identity gap) |
| Diarization label `SPEAKER_00` | Speaker label (#5), not a proposition |
| Event identity itself | Event entity (#4) |
| Host’s rhetorical question with no assertive content | Processed only (no claim) |
| Credibility score / true-false verdict | Future curator field / #10-adjacent; not claim layer |

---

## Atomicity

### Rule: one atomic proposition per live claim

An **atomic claim** expresses a single checkable assertion that can independently:

- be attributed to one speaker,
- be bound (or not) to one focus Event,
- participate in SUPPORTS / CONTRADICTS without internal “and/or” ambiguity,
- be approved or rejected without partial truth.

### What counts as atomic

| Pattern | Atomic? | Guidance |
|---------|---------|----------|
| Single factual assertion | Yes | “There were 23 people in the program.” |
| Single evaluative assertion | Yes | “The materials are inconsistent with known alloys.” |
| Assertion + time/place of **the same** assertion | Usually yes | Keep as one claim if the modifiers are part of one proposition (“…at Groom Lake in 1980”). |
| Two independent facts conjoined | No | Split: “There were 23 people” **and** “The program ran until 1989” → two claims |
| Assertion + explanation | No | Split: fact claim + causal/explanatory claim |
| Assertion about object A and object B | Usually no | Split unless the proposition is inherently relational (“A was larger than B” = one relational claim) |
| Quote embedding another speaker’s words | Careful | Prefer **meta-claim** (“Host asserts that guest claimed X”) **or** only extract guest claim from guest’s own spans — never invent guest assertion from host paraphrase alone |

### Compound → split rules

When AI (or curator) encounters compound speech:

1. **Identify conjuncts / independent assertables** (and, also, then, plus causal *because* clauses that add a second assertable).
2. **Mint one proposed claim per atomic proposition.**
3. Each child claim gets its own `EXTRACTED_FROM` (may share the same processed span or a sub-span when offsets exist).
4. Optional content edge: `ELABORATES` or a future `PART_OF_UTTERANCE` only if UX needs grouping — **v1 does not require a compound parent node**.
5. **Never approve a live claim whose text still contains two independent propositions.**

### Staging compound (non-live only)

AI may keep an internal **compound extraction draft** for review UI (“split these?”). That draft is **not** a live graph claim and must not receive `layer=claim` + `live` without split (or curator-forced single atomic rewrite).

### Minimal length / maximal paraphrase

- Claim text is a **normalized proposition**, not a raw transcript dump and not a multi-paragraph summary.
- Prefer close paraphrase that preserves **polarity, modality, numbers, names, and scope**.
- Do not “improve” the speaker by adding precision they did not state (that creates assumption or inference).

---

## v1 claim schema (spec-level fields)

Fields are **logical requirements**, not storage column names. Required vs optional is for **live** claims unless noted.

### Identity and type

| Field | Required | Definition |
|-------|----------|------------|
| `id` | Yes | Stable claim node id |
| `layer` | Yes | Always `claim`; immutable |
| `lifecycle` | Yes | At least `proposed` \| `live` \| `rejected` \| `superseded` (#9 owns transitions) |
| `claim_text` | Yes | Normalized atomic proposition in declarative English (or quoted tight paraphrase). This is the compare unit’s surface. |
| `claim_kind` | Yes (default) | Enum, v1: `world_assertion` \| `meta_speech` \| `self_report`. Default `world_assertion`. See kinds below. |

### Claim kinds (v1)

| `claim_kind` | Meaning | Example |
|--------------|---------|---------|
| `world_assertion` | Speaker asserts something about the world / a happening / an object / a program | “The object had no visible means of propulsion.” |
| `meta_speech` | Speaker asserts something about **what was said or claimed** (including third-party or prior testimony) | “Grusch told Congress that crash retrievals exist.” (when the **current** speaker is asserting that Grusch said it, grounded in *this* video’s speech) |
| `self_report` | Speaker asserts their own experience, perception, or role | “I was the commanding officer of the Black Aces.” |

Kinds refine extraction and contradiction UX; they **do not** change layer. A meta_speech claim is still a claim about the speaking act in *this* source, not an auto-import of the third party’s claim without their own grounding.

### Attribution and aboutness

| Field / edge | Required for live? | Definition |
|--------------|---------------------|------------|
| `ATTRIBUTED_TO` → Person | **Yes**, with one exception | Content edge to the person who uttered the assertion. Live person + approved episode mapping required for live claim (#5). |
| Unresolved attribution path | Exception only | If person mapping is not yet approved, claim may exist as **`proposed` only**, with provisional pointer to `speaker_label` + video (not a substitute Person). **No live claim with only SPEAKER_n attribution.** |
| `ABOUT_EVENT` → Event | Preferred, not always required | Content edge to the world Event the proposition concerns. |
| Unbound claim | Allowed | No `ABOUT_EVENT` when Event keys are insufficient; mark `event_binding_status = unbound` (or equivalent). Do not invent Events to force binding (#4). |
| `ABOUT_TOPIC` | Optional | Thematic index; Topics ticket (#11) may refine. Not a substitute for Event when an Event exists. |

### Grounding and provenance (required spine)

| Edge / field | Required for live? | Definition |
|--------------|---------------------|------------|
| `EXTRACTED_FROM` → processed | **Yes (≥1)** | Primary grounding: which utterance/span the proposition was pulled from. |
| Processed → raw path | **Yes** (via processed `DERIVED_FROM` raw) | Must be able to resolve to video + media anchors. |
| `GROUNDED_IN` → raw | Optional sugar | Allowed only if claim→processed→raw path also exists (#3). |
| Time range | **Yes** (via raw/processed anchors) | Start/end timestamps (or span offsets) for the grounding speech. Exact field packaging is #7; claim model **requires the capability**. |
| Video identity | **Yes** (via raw catalog) | Which YouTube video the speech came from. |
| Channel identity | Yes via video | Inherited from video’s channel. |
| `PROPOSED_BY` | Yes for AI extractions | Agent/system that proposed the claim. |
| `APPROVED_BY` | Yes on transition to live | Curator identity (#3, #9). |
| Extraction method / model notes | Recommended | Tool/model id, prompt version, etc. — field set owned by #7; claim model requires **that provenance is recordable**. |

### Optional v1 properties (allowed, not load-bearing)

| Field | Purpose | Notes |
|-------|---------|-------|
| `polarity` | `affirms` \| `denies` \| `questions` (if we ever claim-ify questions — default: don’t) | Default `affirms`. Explicit denial (“it was **not** a drone”) is still a claim with negative polarity or negated `claim_text`. |
| `modality` | How the speaker framed certainty: `asserted` \| `hedged` \| `reported_secondhand` \| `hypothetical_in_speech` | Does **not** demote to inference. Secondhand still claim if speaker asserted it. |
| `extraction_confidence` | AI confidence in extraction fidelity (0–1 conceptual) | Review assist only; never auto-live. Distinct from speaker credibility. |
| `quote_span` / excerpt | Short supporting quote for UI | Must not replace `claim_text`; quote is evidence display. |
| `language` | ISO code if ever multi-lingual | Default en for v1 seed corpus. |
| `supersedes` / `SUPERSEDES` | Revised wording of same assertion | Same-layer versioning (#3). |

### Explicitly out of v1 claim schema

| Deferred | Where |
|----------|-------|
| True / false / “verified” flags | Later; curator-owned if added |
| Credibility / trust scores | Speaker credibility signals / related work |
| Full contradiction object model | #8 |
| Approval queue UX | #9 |
| Numeric DB types, indexes | Implementation |
| Auto-dedupe of paraphrases into one claim id | Forbidden: two videos → two claims; link with `SAME_ASSERTION_AS` if useful |

---

## Allowed relations (normative for v1)

### Provenance (dependent → support)

| Predicate | Claim endpoint role | Legal | Notes |
|-----------|---------------------|-------|-------|
| `EXTRACTED_FROM` | claim → processed | **Required** for live | Primary |
| `GROUNDED_IN` | claim → raw | Optional | Never without processed path |
| `RESTS_ON` | claim → assumption | Rare | Only when claim interpretation depends on an explicit scaffolding assumption; prefer not to use for normal extractions |
| `PROPOSED_BY` | claim → Agent | Yes | |
| `APPROVED_BY` | claim → Curator | Yes on live | |
| `SUPERSEDES` | claim → claim | Yes | Revised claim text / correction |

**Illegal:** claim with only raw grounding; inference masquerading as claim; assumption relabeled claim.

### Content

| Predicate | Direction | Legal | Notes |
|-----------|-----------|-------|-------|
| `ATTRIBUTED_TO` | claim → Person | **Required** for live (see exception) | Speaker who asserted |
| `ABOUT_EVENT` | claim → Event | Preferred | Unbound allowed |
| `ABOUT_TOPIC` | claim → Topic | Optional | #11 |
| `SUPPORTS` | claim → claim \| inference | Yes | Detail in #8 |
| `CONTRADICTS` | claim → claim \| inference | Yes | Detail in #8 |
| `ELABORATES` | claim → claim | Yes | Same speaker thread or clarifying claim |
| `SAME_ASSERTION_AS` | claim → claim | Yes | Cross-video / cross-telling paraphrase **link**; **two claims remain** |

### Relation to Telling / Video / Beat

- A claim is **not** a Telling. A **Telling** is the account of an Event in a video (or continuous segment); claims are the extractable propositions inside that account (#4).
- Video and timestamp reachability is **mandatory via provenance**, not by treating Video as the claim’s “about” target.
- Beats/chapters may help UI navigation; they are not claim aboutness targets.

### Event binding status

| Status | Meaning | Multi-telling |
|--------|---------|---------------|
| `bound` | Has `ABOUT_EVENT` to a confirmed or curator-accepted Event | Default compare unit |
| `provisionally_bound` | Points at provisional Event / provisional identity bundle | Compare only in provisional mode (#4, #14) |
| `unbound` | No Event yet | Searchable; not dropped; curator may bind later |

**On Event merge/split:** claims re-parent with merge provenance; do not silently retarget (#4).

---

## Multi-speaker dialogue → claims

### Core rule

> **One atomic proposition → one claim → one primary `ATTRIBUTED_TO` person**  
> grounded in that speaker’s processed spans.

### Pipeline (conceptual)

```
raw (video + transcript/ASR + time anchors)
  → processed utterances (speaker_label, text, t0–t1)
  → episode attribution (speaker_label → Person) [#5]
  → proposed atomic claims (EXTRACTED_FROM + ATTRIBUTED_TO + optional ABOUT_EVENT)
  → curator approve → live
```

### Dialogue patterns

| Situation | Extraction rule |
|-----------|-----------------|
| Guest asserts fact | Claim attributed to **guest**; `EXTRACTED_FROM` guest utterance |
| Host asks; guest answers | Claims only from **assertive** guest (or host) content — questions alone are not claims |
| Host paraphrases guest (“So you’re saying X”) | **Host** claim of kind `meta_speech` **or** leave processed-only. **Do not** attribute X to the guest unless the guest affirmed X in their own spans |
| Guest affirms host paraphrase (“Exactly”) | Guest claim for X, grounded in guest affirmation span (and optionally linked `ELABORATES` / shared event); host paraphrase may stay processed or separate meta claim |
| Two guests disagree | Two claims, both `ABOUT_EVENT` same Event when applicable; `CONTRADICTS` is #8’s job (may be proposed) |
| Crosstalk / unresolved label | **No live claim** until episode attribution is resolved or claim remains proposed with unresolved pointer |
| Panel rapid-fire | Split by speaker turn; never “panel claims X” as one node without a Person |
| Same speaker, multi-hop monologue | Multiple atomic claims, same `ATTRIBUTED_TO`, possibly same Event |
| Speaker quotes a third party as testimony | `meta_speech` claim about what the third party allegedly said **as asserted by this speaker**; separate world-claims only if this speaker also asserts the world fact in their own voice **or** another source grounds the third party |

### Multi-speaker example (normative intent)

**Video:** Area52-style panel.  

| Processed | Speaker | Text (abbrev.) |
|-----------|---------|----------------|
| U1 | Host (Chris Ramsay) | “So the craft was non-human?” |
| U2 | Guest A | “I’m saying the materials analysis is inconsistent with known alloys.” |
| U3 | Guest B | “I wouldn’t go that far — it could be classified terrestrial.” |

| Claim | Text | ATTRIBUTED_TO | EXTRACTED_FROM | ABOUT_EVENT |
|-------|------|---------------|----------------|-------------|
| C1 | Materials analysis of the sample is inconsistent with known alloys. | Guest A | U2 | Event? (if bound) |
| C2 | The materials could be classified terrestrial technology. | Guest B | U3 | same Event if bound |

- U1 alone → no claim (question).  
- Do **not** create a guest claim “craft was non-human” from U1.  
- Optional: if Host later asserts “It was non-human,” that is a **host** claim.

### Host vs guest preference (product default)

Aligned with #3 open item default:

- Prefer claims that track **what the attributed speaker actually asserted**.
- Host framing questions and soft paraphrases default to **processed-only** unless the host clearly asserts or the product explicitly keeps host meta-claims for conversation structure.

---

## Lifecycle and approval hooks (#9)

| State | Claim may have | Used in multi-telling default views? |
|-------|----------------|--------------------------------------|
| `proposed` | Full schema draft; person may still be candidate | No |
| `live` | All required fields + approved attribution + EXTRACTED_FROM path | Yes |
| `rejected` | Retained for audit; not evidence | No |
| `superseded` | Replaced by newer same-layer claim | No (successor is) |

**Atomic approve:** curator may approve claim + related processed + person mapping together if matrix-legal when live (#3).  
**Bulk approve:** allowed only if each node retains true layer and required claim fields still hold (#9).

AI may propose; AI may **not** set live.

---

## Worked examples (UAP seed-style)

### Example 1 — Atomic guest claim (Danny Jones / Area 51 witness)

- **Processed U:** TD Barnes (mapped person, approved): “There were 23 of us…”  
- **Claim C:** “Twenty-three people were involved in [the program under discussion].”  
- **Edges:** `EXTRACTED_FROM` U; `ATTRIBUTED_TO` Person:TD Barnes; `ABOUT_EVENT` Event? (program cohort happening if keys support; else unbound); raw path → Danny Jones video + timestamps.  
- **Not inference:** Direct assertion in source.

### Example 2 — Compound split

- **Speech:** “The object had no rotors and it accelerated and disappeared.”  
- **Claims:**  
  - C_a: “The object had no rotors.”  
  - C_b: “The object accelerated [in the manner described].”  
  - C_c: “The object disappeared [from view / sensors as described].”  
- Shared attribution and likely same Event; three compare units for contradiction later.

### Example 3 — Same assertion across videos

- Fravor interview on channel A and recap on channel B both yield claims that the object had no visible rotors.  
- Two claim nodes; optional `SAME_ASSERTION_AS` link.  
- Multi-telling compares both Tellings of the same Event — not one collapsed claim id.

### Example 4 — Illegal assumption-as-claim

- Speakers say “the ranch” without naming Skinwalker.  
- **Forbidden:** live claim “It was Skinwalker Ranch” with no extractable assertion.  
- **Correct:** assumption for co-reference, or unbound/provisional Event work per #4.

### Example 5 — Inference stays inference

- Claims about materials anomaly + chain of custody to lab X exist.  
- “Lab X possessed anomalous material” as system conclusion → **inference** `BASED_ON` those claims, not a new extracted claim, unless a speaker stated that conclusion.

---

## Downstream contracts

### Contradiction / multi-telling (#8, #14) may assume

- Compare units are primarily **live atomic claims** (optionally live inferences, badged).
- Claims carry stable `claim_text`, attribution, event binding status, and video/time provenance.
- Cross-telling agreement uses `SAME_ASSERTION_AS` / semantic compare; conflict uses `CONTRADICTS` among claims (and inferences) — not assumptions as evidence.
- Identity conflicts (“same Event?”) are **not** claim contradictions (#4).

### Provenance minimum (#7) may assume

- Live claims require EXTRACTED_FROM + resolvable video/time anchors.
- Claim model does not loosen layer matrices; #7 adds field packaging (tool version, offsets, track ids).

### Human approval (#9) may assume

- Claims default to `proposed`; required-field checklist before live.
- Unresolved person attribution blocks live, not propose.
- Supersession for wording fixes without layer change.

### Topics (#11) may assume

- `ABOUT_TOPIC` is optional sugar; Event binding is the multi-telling spine.

---

## Open items deliberately out of this ticket

- Exact contradiction object and open-question schema — #8  
- Minimum provenance field list and serialization — #7  
- Approval queue UX, bulk actions — #9  
- Topic taxonomy — #11  
- Speaker credibility signals — later  
- Whether to default-keep host meta_speech claims in product UI — prefer minimal (processed-only) unless curator opts in  
- Automated paraphrase clustering thresholds for `SAME_ASSERTION_AS` proposals — implementation later; human gate remains  

---

## Policy cheat-sheet

```
Is it in the transcript as an assertion by a speaker?
  YES → candidate CLAIM (atomic). Ground with EXTRACTED_FROM.
  NO, but we conclude it → INFERENCE (BASED_ON claims).
  NO, and we’re filling a gap → ASSUMPTION (RESTS_ON).

Compound sentence with two facts?
  → SPLIT into atomic claims before live.

Who is ATTRIBUTED_TO?
  → The person who uttered the words (approved episode map).
  → Host paraphrase ≠ guest claim.

ABOUT_EVENT?
  → Bind when keys support; else unbound. Don’t invent Events.

Live claim minimum:
  layer=claim, claim_text, EXTRACTED_FROM processed→raw (video+time),
  ATTRIBUTED_TO live Person, lifecycle=live via curator.
```

---

## Decision log

| Date | Decision |
|------|----------|
| 2026-07-22 | Adopt atomic claim model: required live fields (text, EXTRACTED_FROM, attribution, video/time path); claim vs inference vs assumption boundaries per #3; compound split rules; multi-speaker one-claim-per-proposition-per-speaker; unbound Event allowed; SAME_ASSERTION_AS keeps two nodes; AI propose / curator live. |

## Decision date

Recorded 2026-07-22 as the recommended resolution for issue #6 (batch completion with recommended defaults).
