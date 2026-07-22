# Speaker credibility signals (v1)

Decision asset for [Speaker credibility signals (v1)](https://github.com/etai83/uap-kg/issues/10)  
Part of [Wayfinder: UAP YouTube knowledge graph spec](https://github.com/etai83/uap-kg/issues/1)

**Depends on:** [Speaker identity and alias merge](./speaker-identity-and-alias-merge.md) (#5), [Event identity rule](./event-identity-rule.md) (#4), [Epistemic layer ontology](./epistemic-layer-ontology.md) (#3), [Seed channel set v1](./seed-channel-set-v1.md) (#2)  
**Scope:** Spec-level policy for what **speaker credibility** means in v1, which signals are in scope, and hard forbids on fake trust scores. No implementation, no scoring algorithm.

---

## Question

What does **credibility** mean for a speaker in v1, and which signals are in scope?

Decide: qualitative notes vs scores, consistency-across-tellings vs external reputation, and what the system must never invent as "trust scores."

---

## Decision summary

| Axis | Decision |
|------|----------|
| What credibility **is** | **Soft research metadata** attached to (or about) a **Person** — curator judgment + observable graph signals. **Not** person identity, **not** an epistemic layer, **not** a truth verdict on claims |
| Qualitative vs numeric | **Qualitative-first.** Curator free-text notes, optional structured role/stance tags, and **observable consistency observations**. **No** composite 0–100 / star / “trust index” in v1 |
| Consistency across tellings | **In scope when multi-telling data exists.** May surface as derived observations (same speaker’s claims on the same Event agree / conflict / shift). Never auto-promoted to a numeric trust score |
| External reputation | **Out of scope as objective input.** No scraping Wikipedia authority, social follower counts, “debunker ratings,” academic h-index, or third-party “trust APIs” as if they were facts about the person |
| Invented trust scores | **Hard forbid.** System must never mint, scrape, or display a synthetic “trust score,” “credibility rating,” or “reliability %” as if it were measured truth |
| Identity vs credibility | **Person identity ≠ credibility.** Who someone *is* (node, aliases, episode maps) is decided in #5. Credibility never creates, merges, or splits person nodes |
| Epistemic separation | Credibility does **not** sit in the five-layer spine (`raw`…`assumption`). It does **not** rewrite claim layer, truth value, or Event identity |
| Honesty stance | This is a **solo personal research tool**. Signals help the curator remember and compare; they are **not** forensic witness ratings or court-ready reliability metrics |

---

## Core principle

> **Credibility in v1 is the curator’s working sense of a speaker, plus what the graph can honestly observe about that speaker’s own tellings.**  
> It is **not** a system-computed reputation, **not** social proof, and **not** a substitute for reading the claims.

Standing map preferences honored:

- Extractions are **AI-proposed, human-approved before live**.
- Person identity stays clean enough that credibility histories do not fork across aliases (#5 hook).
- Event identity is independent of witness reputation (#4: credibility does **not** change Event identity).
- Claims remain recorded assertions, not verdicts (#3).

---

## What “credibility” means (v1 definition)

**Speaker credibility (v1)** = optional, soft, curator-owned research metadata about a **Person**, optionally enriched by **observable, provenance-backed consistency signals** derived from that person’s claims across Tellings of Events already in the graph.

It answers, for the curator:

- “What do *I* currently think about how this person shows up in this corpus?”
- “When this person has spoken about the same Event more than once (or across channels), where are they consistent or inconsistent?”
- “What role does this person usually occupy (host, witness-participant, researcher, etc.) — as a label, not a score?”

It does **not** answer:

- “Is this person objectively trustworthy on a 0–1 scale?”
- “What does the internet think of them?”
- “Should the system down-rank their claims automatically?”

### Soft metadata, not hard ontology

| Concern | Owns it | Credibility may… | Credibility must not… |
|---------|---------|-------------------|------------------------|
| **Person identity** (#5) | Person node lifecycle | Attach notes/signals *to* an active person | Create, merge, split, or deprecate persons |
| **Epistemic layer** (#3) | Node `layer` enum | Sit beside claims as research annotation | Change layer, masquerade as claim/inference truth |
| **Event identity** (#4) | Event keys + curator merge | Note that a speaker’s tellings of Event X conflict | Split/merge Events because a speaker is “unreliable” |
| **Claim truth** (#6 later) | Claim model / curator judgment | Inform *reading* of claims | Auto-reject, auto-weight, or delete claims |

---

## In-scope signals (v1)

Three families only. All are optional; a Person may have **none**.

### S1 — Curator annotations (primary)

Human-authored, first-class for v1.

| Signal | Form | Live gate |
|--------|------|-----------|
| **Credibility note** | Free-text note(s) on a Person (dated, editable, supersedable) | Curator-authored; no AI auto-live prose that pretends to be the curator’s judgment |
| **Optional stance / caveat tags** | Small closed set, e.g. `primary_witness`, `secondhand_reteller`, `host_synthesizer`, `institutional_official`, `curator_flag_caution`, `curator_flag_high_value` | Curator sets; AI may **propose** tags only |
| **Per-claim or per-telling caveat** (optional) | Short note on a specific claim/telling link (“this recounting differs from their 2022 interview”) | Curator; may be AI-proposed text for review |

**Policy:** Qualitative notes are the **default** representation of “credibility.” Prefer a clear sentence over a number.

### S2 — Role labels (descriptive, not evaluative)

Role is **what function the person plays in discourse / in the happening**, not how much to “trust” them.

| Role label (illustrative v1 set) | Meaning |
|----------------------------------|---------|
| `host` | Channel host / interviewer on seed channels (Jesse Michels, Chris Ramsay, Danny Jones in host seat) |
| `guest` | Interviewed speaker |
| `witness_participant` | Claims direct sensory / operational involvement in an Event |
| `secondhand` | Relays others’ accounts |
| `researcher_or_journalist` | Frames investigation / synthesis |
| `official_or_institutional` | Speaks from role in agency, military, lab, etc. (as *stated or evidenced*, not scraped bio score) |

Rules:

- Roles may be **episode-scoped** (Jesse is `host` on his channel, `guest` on Danny Jones / Area52) and/or **person-default**.
- Roles are **labels**, never converted into a weighted trust multiplier in v1.
- Role ≠ identity evidence and ≠ credibility score.

### S3 — Consistency-across-tellings (derived observation, when data exists)

**In scope only when** the graph already has enough multi-telling structure:

- Same **Person** attributed on ≥2 live claims (or tellings) that the curator (or confirmed Event links) treat as about the **same Event** (or an explicit provisional Event bundle), **or**
- Same Person’s claims about the same Event keys that multi-telling compare can already align (#4 / #14).

| Observable (conceptual) | What it is | What it is not |
|-------------------------|------------|----------------|
| **Agreement cluster** | Multiple tellings from this person align on stated facts about Event E | Proof those facts are true |
| **Conflict cluster** | This person’s tellings of Event E contradict each other (or sharply shift) | Automatic “liar” score |
| **Scope shift** | Same person narrows/expands claims over time (recorded as observation + pointers) | Scraped “reliability trend” |
| **No multi-telling data** | Signal **absent** (UI: “insufficient tellings”) | Not a low score; **missing**, not zero |

**Derivation rules:**

1. Observations must point at **concrete claim/telling IDs** (and Event focus). No floating “inconsistent speaker” badge without evidence links.
2. AI may **propose** consistency observations; **curator approves** before they are treated as live research annotations (same spirit as extraction gates).
3. Consistency is **person × event** (and optionally person × topic later) — **not** a global person reputation number rolled up from all events.
4. Cross-**person** contradiction (A vs B on Event E) belongs to contradiction / multi-telling compare (#8, #14), not to a single speaker’s credibility score. A speaker-level note may *mention* “conflicts with Fravor on X” only as curator prose or a linked open question — not as auto-scoring.

### Seed-channel reality check (S3 applicability)

| Channel / pattern | Credibility signal practicality in early pilot |
|-------------------|-----------------------------------------------|
| **Jesse Michels** | Often synthesis / multi-guest; host role label + curator notes dominate until same guests reappear on multi-telling Events |
| **Area52 (Chris Ramsay)** | Host + panels; guest consistency only when guests also appear on Jesse/Danny (or repeat on Area52) about the **same Event** |
| **Danny Jones** | Long-form single-guest deep dives; **best early home for S3** when a guest retells a famous case (e.g. Nimitz) also covered on other seed channels — still person×event observations, not a Danny-global score |

Hosts (Jesse, Chris, Danny) get **role defaults** as hosts on their channels; credibility notes remain optional and **non-numeric**. Guest appearances of a host on another seed channel do not invent a second reputation object — same Person, same soft metadata.

---

## Out of scope / hard forbids (v1)

### Never invent or present as objective

| Forbidden artifact | Why |
|--------------------|-----|
| **Composite trust score** (0–1, 0–100, stars, letter grades) | Implies measured reliability the corpus cannot support; seduces UI into fake precision |
| **Scraped external reputation** as graph truth | Follower counts, Wikipedia “notability,” RationalWiki/ Metabunk “ratings,” news “reliability charts,” academic metrics — **not** in-scope inputs for v1 credibility |
| **Vendor / API “speaker trust”** | No third-party trust API written onto Person as fact |
| **Auto down-rank / hide claims** by speaker score | Credibility must not silently filter the claim graph in v1 |
| **Credibility-driven identity merge/split** | Unreliable speakers are still one Person if identity evidence says so; two reliable people with the same name stay two Persons |
| **Credibility-driven Event merge/split** | Per #4: witness reputation does not change Event identity |
| **Treating host popularity as evidence quality** | Channel sub counts (profile trivia only) are **not** credibility signals |
| **“Unknown speaker” reputation** | Unresolved speaker labels (#5) have **no** credibility object; no “Anonymous trust: N/A” nodes |

### Explicit non-signals (do not model as credibility)

| Non-signal | Belongs elsewhere |
|------------|-------------------|
| Diarization / attribution confidence | Identity pipeline (#5, #13) |
| Claim extraction confidence | Claim / provenance tickets |
| Epistemic layer | Ontology (#3) |
| Open questions / contradictions between people | #8 / multi-telling UX |
| Legal guilt, security-clearance fantasy ratings | Nowhere in this personal tool |

---

## Qualitative notes vs scores (normative choice)

| Approach | v1 status |
|----------|-----------|
| Curator free-text notes | **Canonical** |
| Small role / flag tag set | **Allowed** (descriptive) |
| Person×event consistency observations with evidence pointers | **Allowed** when multi-telling data exists |
| Numeric per-signal diagnostics for **engineering** (e.g. “N conflicting claim pairs found”) | **Allowed only as internal counts in derived observations** — must not be relabeled “trust = 0.37” |
| Published composite **trust / credibility score** on Person | **Forbidden in v1** |

**Rationale (solo research honesty):** With ~30 pilot videos across three channels, any global score would be sparse, biased by who got airtime, and easy to over-read. Notes + linked observations match how a single researcher actually works.

If a future version wants scores, it requires a **new decision**: calibrated definition, visible methodology, and still no silent claim filtering — out of scope here.

---

## Consistency-across-tellings vs external reputation (normative choice)

| Source of judgment | v1 |
|--------------------|----|
| **Internal graph: same person, same event, multiple tellings** | **In scope** as observable consistency signals (S3) |
| **Internal graph: curator reading** | **In scope** as notes (S1) |
| **External web reputation / authority graphs** | **Out of scope** as automated credibility input |
| **Curator pasting an external link into a note** (“see interview criticism URL”) | **Allowed** as ordinary curator prose / bookmark — **not** parsed into a score |

External material may inform the **human**; the system must not launder it into a fake objective rating.

---

## What the system may derive vs must never invent

### May derive (with provenance + human gate for live annotations)

1. Role proposals from episode context (host on seed channel; guest named in title) — still confirmable.
2. Person×event consistency **candidates**: pairs/groups of this person’s claims about Event E that multi-telling logic flags as agree / conflict / drift.
3. Counts and lists: “3 live claims by P about Event E; 1 conflict pair proposed.”
4. Reminders: “No second telling by P for Event E yet” (absence, not a low score).

### Must never invent

1. A **trust score**, **credibility rating**, or **reliability percentage** for a Person.
2. A score built from **external reputation scrapes** or social metrics.
3. Auto-generated prose that states “P is unreliable / reliable” as **system fact** without being either (a) curator text or (b) a clearly labeled proposed observation tied to claim IDs.
4. Credibility objects on **speaker labels**, channels-as-persons, or ads/unresolved clusters.
5. Using credibility to **rewrite** identity, layer, or Event sameness.

---

## Data shape (conceptual, non-schema)

Enough structure for implementers later; not DDL.

```
Person (identity: #5)
  └── credibility_profile? (optional soft bag)
        ├── notes[]: { text, created_at, author=curator, superseded_by? }
        ├── role_labels[]: { role, scope: person|episode, video_id?, evidence? }
        ├── flags[]: closed-set curator flags
        └── consistency_observations[]: {
              person_id,
              focus_event_id | provisional_bundle_id,
              kind: agree | conflict | drift | insufficient_data,
              support_claim_ids[],
              summary?,          # curator-approved or proposed
              status: proposed | live | rejected,
              derived_by?
            }
```

**Invariants:**

- Deleting or merging persons follows #5; consistency observations **re-point** or recompute; they do not block identity merge.
- No field named `trust_score`, `credibility_score`, or equivalent on Person in v1.
- Default research views show claims and tellings **without** requiring a credibility profile to exist.

---

## Worked examples

### Example A — TD Barnes on Danny Jones (single deep telling)

1. Person **TD Barnes** active; episode attribution approved.  
2. Many claims about Area 51–era Events from **one** primary telling.  
3. **S3:** `insufficient_data` for cross-telling consistency on those Events (unless other seed videos with Barnes on the same Event exist).  
4. **S1:** Curator may note “detailed operational color; treat secondhand program claims carefully.”  
5. **Forbidden:** `trust_score: 0.82` because the interview was long and confident.

### Example B — Same witness motif across channels (multi-telling)

1. Event: *Nimitz* / Tic Tac (2004) confirmed.  
2. Person **Fravor** (illustrative) appears on Danny Jones and is discussed/quoted on Jesse Michels / Area52.  
3. Only **Fravor’s own attributed claims** enter Fravor’s S3 observations; host paraphrases are host speech (#3).  
4. If Fravor’s own tellings align on keys → `agree` observation with claim ID list.  
5. If a later telling shifts a date/detail → `drift` or `conflict` with pointers — **still no** global Fravor score.

### Example C — Host synthesis (Jesse Michels)

1. Jesse as `host` + often `researcher_or_journalist` on his channel; `guest` when on Area52/Danny.  
2. Credibility notes may track “synthesis-heavy; verify load-bearing guest claims at source.”  
3. Jesse’s **editorial framing** is not a witness reliability score for the guest.  
4. **Forbidden:** inflating Jesse’s “credibility” from American Alchemy subscriber count.

### Example D — Conflicting tellings by one guest

1. Guest G asserts claim C1 about Event E on video V1 and incompatible C2 on V2.  
2. System may propose consistency observation `conflict` with `{C1, C2}` + Event E.  
3. Curator approves observation and/or writes a note.  
4. Both claims can remain **live** as recorded assertions; contradiction UX (#8) surfaces the tension.  
5. **Forbidden:** auto-suppress C2 because “credibility dropped.”

### Example E — Unresolved speaker

1. `SPEAKER_03` never mapped.  
2. **No** credibility profile. No anonymous trust object.  
3. Map to a Person first (#5); only then may soft metadata attach.

---

## Separation checklist (normative)

| If you are tempted to… | Do this instead |
|------------------------|-----------------|
| Score a person to sort claim quality | Use multi-telling compare + contradiction model; optional curator note |
| Scrape “are they credible?” from the web | Curator reads externally; paste thoughts into a **note** if desired |
| Merge two person nodes because both seem sketchy | Identity evidence only (#5) |
| Split an Event because the witness is disputed | Event keys + curator (#4); disputes are claims/open questions |
| Put credibility in `layer` | Keep soft metadata outside the five-layer spine (#3) |
| Rate unresolved labels | Leave unresolved; no person, no profile |

---

## Downstream implications

| Ticket / area | Implication |
|---------------|-------------|
| **#5 Person identity** | Credibility attaches only to **active** persons; merges reassign notes/observations to survivor; aliases share one profile |
| **#4 Event identity** | S3 is keyed by Event (or provisional bundle); credibility never drives Event merge |
| **#3 Epistemic layers** | Credibility is not a layer; does not promote/demote claims |
| **#6 Claim model** | Claims do not embed system trust scores; optional per-claim curator caveat is annotation, not layer |
| **#8 Contradiction / open question** | Cross-person conflicts stay here; same-person conflicts may **also** feed S3 observations |
| **#9 Human approval** | Live consistency observations and AI-proposed tags/notes follow propose → curator approve |
| **#14 Multi-telling UX** | Prefer showing evidence-linked consistency observations over any badge that looks like a score |
| **Seed channels** | Role defaults for three hosts; no reputation import from channel metrics |

---

## Out of scope for this decision

- UI wireframes for note editors (only: no score-primary chrome in v1)
- Automated NLI / contradiction classifiers (may **propose** S3; policy above still applies)
- Legal/defamation posture for storing critical notes (personal tool; curator-owned prose)
- Full claim truth-value workflow
- Future numeric models (explicit reopen required)

---

## Policy cheat-sheet

```
What is speaker credibility in v1?
  → Soft metadata: curator notes + role labels + optional
    person×event consistency observations.
  → Not identity. Not epistemic layer. Not claim truth.

Scores?
  → No composite trust/credibility scores.
  → Internal counts on linked claims are OK only as observation detail,
    never marketed as a trust index.

External reputation?
  → Do not scrape or import as objective signals.
  → Curator may mention external views in free-text notes.

Consistency across tellings?
  → In scope when multi-telling data exists for same person + same event.
  → Absent data = missing signal, not low trust.

Never:
  → Invent trust scores
  → Auto-filter claims by speaker reputation
  → Attach credibility to SPEAKER_n / unresolved
  → Let credibility merge persons or events
```

---

## Sources / related decisions

1. Issue #10 — Speaker credibility signals (v1) — https://github.com/etai83/uap-kg/issues/10  
2. Issue #5 decision — [speaker-identity-and-alias-merge.md](./speaker-identity-and-alias-merge.md) (identity ≠ credibility; downstream hook)  
3. Issue #4 decision — [event-identity-rule.md](./event-identity-rule.md) (credibility does not change Event identity)  
4. Issue #3 decision — [epistemic-layer-ontology.md](./epistemic-layer-ontology.md) (credibility score ≠ layer)  
5. Issue #2 decision — [seed-channel-set-v1.md](./seed-channel-set-v1.md)  
6. Standing preference: solo personal research tool; AI-proposed / human-approved extractions  

---

## Decision date

Recorded 2026-07-22 as the recommended resolution for issue #10 (batch completion with recommended defaults; no interactive grilling).
