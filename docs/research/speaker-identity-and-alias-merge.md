# Speaker identity and alias merge

Decision asset for [Speaker identity and alias merge](https://github.com/etai83/uap-kg/issues/5)  
Part of [Wayfinder: UAP YouTube knowledge graph spec](https://github.com/etai83/uap-kg/issues/1)

**Depends on:** [Speaker diarization options](./speaker-diarization-options.md) (#13), [Seed channel set v1](./seed-channel-set-v1.md) (#2)  
**Scope:** Spec-level policy for how **person nodes** are created, attributed from diarized speech, aliased, and merged across videos. No implementation.

---

## Question

How are **person nodes** created, merged, and attributed from diarized speech across videos?

Decide: alias policy, confidence thresholds, unknown-speaker handling, host vs guest defaults, and what evidence is required before two labels become one person.

---

## Decision summary

| Axis | Decision |
|------|----------|
| Diarization label vs person | **`SPEAKER_00` (etc.) is never a person node.** It is an episode-local **speaker label** until mapped with evidence + human gate for live writes |
| Creation path | AI/system may **propose** person candidates and mappings; **curator confirms** before any person-node create, alias attach, merge, or claim-attribution goes **live** |
| Live graph rule | No weak auto-merge; **string similarity alone never merges** live person nodes |
| Host defaults | Seed-channel hosts get **strong provisional defaults** (role + channel binding), still **curator-confirmed** once per host (and re-confirmed only on conflict) |
| Guests | Provisional map from title/description/credits + optional LLM assist; **always human-confirm** before live |
| Unknown speakers | Stay as **unresolved speaker labels** (episode-scoped); do **not** mint person nodes for noise/ads/audience |
| Alias policy | Canonical display name + typed aliases; normalize titles/punctuation; nicknames and handles are aliases, not separate people |
| Cross-video merge | Merge only with **multi-signal evidence** above thresholds **and** curator approval for live |
| Confidence model | Separate **diarization confidence**, **within-episode attribution confidence**, and **identity/merge confidence** — never collapse them |

---

## Core principle

> **Diarization answers “who spoke when *within this recording*.”**  
> **Person identity answers “which real-world person is that *across the graph*.”**  
> These are different layers. Bridging them is always **provisional until the curator approves** a live write.

Standing map preferences honored:

- Speakers → **named person nodes** + **diarized attributions**; cross-video merge is in scope.
- Extractions are **AI-proposed, human-approved before live**.
- **Human confirm before person-node writes** (from diarization research #13).

---

## Layer model

| Layer | Object | Scope | Example |
|-------|--------|-------|---------|
| **L0 — Diarization** | Speaker label | One video (or one processing job) | `SPEAKER_00`, `spk_1` |
| **L1 — Episode attribution** | Mapping speaker label → person candidate | One video | `SPEAKER_00` → candidate “Leslie Kean” |
| **L2 — Person identity** | Person node (+ aliases) | Graph-global | Person: Leslie Kean |
| **L3 — Claim attribution** | Edge from claim/segment → person | Graph | “X said Y” → Leslie Kean |

**Invariant:** Live claim attribution (L3) requires a live person (L2) and a confirmed episode mapping (L1). Unresolved speech may still exist as transcript with only L0.

---

## Person node lifecycle

### States

| State | Meaning | Live graph? |
|-------|---------|-------------|
| **Proposed** | System or curator suggested a person (name + optional aliases/evidence). Not yet approved. | No |
| **Candidate** | Linked provisionally to one or more speaker labels on one or more videos; still reviewable. | No (staging only) |
| **Active** | Curator-approved person node. May receive aliases and claim attributions. | Yes |
| **Merged-away** | Absorbed into another active person; retained only as historical alias / audit trail pointing to survivor. | No (redirect) |
| **Deprecated** | Wrong or unwanted person (not a merge). Soft-hidden; not used for new attributions. | No |

### Create (new person)

A **new active person node** may be written only when **all** hold:

1. A **canonical display name** is set (see Alias policy).
2. At least one **identity evidence** item is recorded (see Evidence catalog).
3. Curator has explicitly **approved** create (not merely “dismissed review queue noise”).
4. No active person already claims the same **primary identity key** (see Merge rules) — if conflict, force merge review instead of duplicate create.

**Do not create** a person node solely because diarization emitted a new `SPEAKER_n`.

### Attribute (episode mapping)

Within a video, map each material speaker label to:

- an **active** person, or  
- a **proposed/candidate** person pending approval, or  
- **unresolved** (leave unmapped).

Mapping fields (conceptual): `video_id`, `speaker_label`, `person_id?`, `attribution_method`, `attribution_confidence`, `evidence[]`, `review_status` (`needs_review` | `approved` | `rejected`).

Only `review_status = approved` mappings may drive **live** claim edges.

### Merge

Two person candidates/nodes become one only under **Merge rules** below. Merge is a **curator action** for live nodes; system may only propose merges.

### Split (rare)

If an over-merge is discovered (two real people collapsed), curator splits: survivor keeps disputed edges only when evidence supports them; orphaned attributions return to **needs_review**. Spec does not require automated split heuristics in v1.

---

## Relationship to diarization labels

From [speaker-diarization-options.md](./speaker-diarization-options.md):

| Rule | Detail |
|------|--------|
| **No identity inheritance** | `SPEAKER_00` in video A has **no** identity relationship to `SPEAKER_00` in video B |
| **No auto person mint** | Labels never become person nodes without L1 mapping + human gate for live |
| **Uncertainty preserved** | Store speaker_label even after mapping; re-review must be possible |
| **Diarization ≠ identity confidence** | A high diarization cluster score does not imply correct person name |
| **Pipeline default** | Local WhisperX + pyannote (IDs only) → metadata/LLM provisional map → human confirm. AssemblyAI name ID / voiceprints are **proposal signals**, not live truth |

### Within-episode speaker labels

- Stable for the **processing job** of that video.
- If re-processing changes labels (`SPEAKER_00` ↔ `SPEAKER_01` swap), remapping is required; do not assume prior label IDs.
- Prefer anchoring review UI to **time ranges + transcript snippets**, not raw label IDs alone.

---

## Host vs guest defaults

### Seed-channel hosts (v1)

Committed hosts from [seed-channel-set-v1.md](./seed-channel-set-v1.md):

| Channel | Host person (canonical display) | Notes |
|---------|----------------------------------|-------|
| Jesse Michels (American Alchemy) | **Jesse Michels** | Channel brand “American Alchemy” is **not** a person alias for Jesse |
| Area52 | **Chris Ramsay** | Channel name Area52 is a **Channel** identity, not a person; Chris may have alias “Chris Ramsey” only if evidenced as spelling variant — default spelling **Ramsay** |
| Danny Jones | **Danny Jones** | — |

### Host default policy

| Rule | Detail |
|------|--------|
| **Strong provisional default** | For a video on a seed channel, the system may **pre-select** the channel’s host person as the most likely map for the **primary host** speaker cluster |
| **Not silent auto-live** | First time a host is used in the graph: **curator confirms** host person create + first episode mapping. Later episodes on the **same channel** may pre-fill host mapping as provisional, still batch-confirmable |
| **Conflict re-confirm** | If signals disagree (e.g. guest-hosted episode, co-host, cold open, multi-host special), drop to full review — **no** host auto-assume |
| **Talk-time heuristic is assist only** | “Largest talk-time cluster = host” is a **proposal signal**, never sufficient alone for live write |
| **First-speaker heuristic is weak** | Cold opens, ads, and clips make first-speaker = host unsafe (per diarization research) |
| **Host on another channel** | When Jesse appears on Danny Jones, treat as **guest** mapping for that video — same person node, no second “Jesse-as-host” entity |

### Guest defaults

| Rule | Detail |
|------|--------|
| **Metadata-first** | Title, description, chapters, and pinned comment are primary **name proposal** sources |
| **known_values / LLM assist** | Allowed to propose maps; must record method + raw proposal |
| **Always human-confirm for live** | Even when title is “Interview with X” and only two speakers |
| **Recurring guest** | After person is **active**, later episodes may propose the same person from name match + optional voiceprint; still confirm on first link per episode (can be bulk-approved in review UI) |
| **Panel / multi-guest** | No host-style strong defaults; require explicit per-label confirmation |

### Co-hosts, announcers, ads

- Channel promos, mid-roll ads, and non-interview VO → **unresolved** unless curator deliberately attributes.
- Do **not** create person nodes for “Ad voice” or “Unknown announcer” by default.

---

## Alias policy

### Definitions

- **Canonical display name:** Curator-facing primary string for the person (usually public professional name as used in UAP discourse).
- **Alias:** Any other string that denotes the **same** person (nickname, handle, spelling variant, former name, title-bearing form).
- **Not an alias:** Organization names, show names, channel brands, case names, or “the guest” / “SPEAKER_01”.

### Canonical name rules

1. Prefer the name the person uses publicly in this domain (e.g. **Leslie Kean**, not a legal-only form unless that is their public byline).
2. Include a commonly used middle initial only if it is part of their public identity and disambiguates.
3. **One canonical display name** per active person; changes are curator edits (old canonical may become an alias).

### Alias types (typed)

| Type | Examples | Notes |
|------|----------|-------|
| `legal_or_full` | “Leslie Susan Kean” | Optional |
| `nickname` | “Les”, “Chris” | Only if actually used for that person |
| `handle` | `@JesseMichels`, YouTube handle | Channel handle for a **person-hosted** brand may alias the host **only when host ≡ channel persona**; Area52 does **not** alias to Chris Ramsay as a name string without curator intent |
| `spelling_variant` | “Ramsey” vs “Ramsay”, OCR/transcript typos | Low trust until confirmed |
| `title_form` | “Dr. Greer”, “Dr. Steven Greer” | Title-bearing forms are aliases of the person; **title is not a separate person** |
| `stage_or_credit` | Name as printed in episode credits | |
| `former` | Prior public name | Rare; keep as alias, do not split identity without evidence of two people |

### Normalization (matching, not display)

For **proposal matching** only (never the only merge evidence):

- Case-fold; strip honorifics (`Dr.`, `Mr.`, `Ms.`, `Prof.`) and trailing credentials (`PhD`, `MD`) into structured fields if needed.
- Collapse punctuation and extra whitespace.
- Optional: `Last, First` ↔ `First Last` reorder detection.
- **Do not** treat normalized equality alone as proof of identity for live merge.

### What becomes an alias vs a new person

| Situation | Action |
|-----------|--------|
| “Dr. Steven Greer” and “Steven Greer” | **Same person**; title_form alias |
| “Greer” alone in transcript | **Weak mention**; may propose link to existing Steven Greer if episode context fits; never create person “Greer” |
| “Lue Elizondo” / “Luis Elizondo” | **Same person** if public aliases; spelling/nickname alias after confirm |
| Two guests with same common name, different people | **Separate persons**; disambiguate via middle initial, affiliation, or curator note — **never merge on surname alone** |
| Channel “Area52” vs person “Chris Ramsay” | **Different entity types**; no alias bridge that makes the channel a person |
| Host nickname only (“Danny”) | Alias on **Danny Jones**, not a new person |

### Alias attach gate

- Adding an alias to an **active** person that could collide with another active person’s canonical/alias set → **merge review**, not silent attach.
- AI-proposed aliases → curator approve before live.

---

## Unknown and unresolved speakers

| Case | Handling |
|------|----------|
| Diarized but no reliable name | Keep **speaker label** + transcript; `person_id` null; `review_status` may stay `needs_review` or `rejected` (explicitly unmapped) |
| Audience / noise / music-as-speech | Prefer mark segment as **non-attributable** / exclude from person stats; **no person node** |
| “Someone said off-mic” | Unresolved; do not invent “Unknown Person N” **nodes** for live graph |
| Temporary working ID | Staging may use `unresolved:<video_id>:<speaker_label>` for UI only — **not** a person node, **not** mergeable across videos |
| Later identification | Curator maps label → existing or new person; backfill attributions on that video |

**Graph hygiene rule:** The live person inventory should contain **real people the curator cares about**, not every acoustic cluster the diarizer emitted.

---

## Evidence catalog

Evidence items support (a) episode attribution and (b) person merge. Each item has a **type**, **pointer** (video, URL, quote, timestamp), and **strength** (weak / moderate / strong).

| Evidence type | Typical strength | Use for |
|---------------|------------------|---------|
| **E1 Channel–host binding** | Strong for *provisional host map* on that channel’s videos | Host defaults |
| **E2 Explicit self-ID in speech** | Strong | Attribution + identity |
| **E3 Title/description names guest** | Moderate–strong (2-speaker interview) | Attribution proposal |
| **E4 Credits / show notes / description roll** | Moderate–strong | Attribution |
| **E5 Curator assertion** | Strong (by policy) | Any gate; still record as evidence |
| **E6 Prior approved mapping** same channel + same name string | Moderate | Recurring guest proposal |
| **E7 Voiceprint / speaker embedding match** to enrolled gallery | Moderate–strong (thresholded) | Cross-video re-ID **proposal** |
| **E8 Third-party name ID API** (e.g. AssemblyAI known_values) | Weak–moderate | Proposal only |
| **E9 LLM name map from transcript** | Weak–moderate | Proposal only |
| **E10 String / alias similarity** | Weak | Blocking alone for live merge |
| **E11 Shared affiliation + name** (e.g. same org + full name) | Moderate | Merge assist |
| **E12 Disambiguating biographical fact** said on tape or in trusted metadata | Strong | Merge / split |

---

## Confidence thresholds

Three **separate** scores (0–1 conceptual scale; exact calibration is implementation-later). Spec thresholds are **policy bands**.

### 1. Diarization confidence (cluster purity / label stability)

| Band | Meaning | Policy |
|------|---------|--------|
| High | Main speakers stable | Safe to spend human time mapping |
| Medium | Some swaps | Map with caution; expect fixes |
| Low | Chaos / many speakers | Prefer bulk “unresolved” for minor labels; only map hosts/main guests |

Does **not** by itself create or merge persons.

### 2. Within-episode attribution confidence (label → person candidate)

| Band | Typical signals | Auto-live? |
|------|-----------------|------------|
| **High (≥ ~0.85)** | Host default on seed channel **plus** consistent talk pattern; or 2-speaker + title names guest + no conflicting signals | **No** — still confirm, but eligible for **one-click approve** / batch approve |
| **Medium (~0.55–0.85)** | Metadata name + LLM agree; or voiceprint above match threshold | **No** — standard review |
| **Low (< ~0.55)** | String match only; conflicting guest lists; panel chaos | **No** — default leave unresolved or force careful review |

**Hard rule:** Attribution confidence **never** auto-writes live person edges regardless of band.

### 3. Identity / merge confidence (person A ≡ person B)

| Band | Required evidence pattern | Auto-live merge? |
|------|---------------------------|------------------|
| **High** | ≥ 2 **independent** signals, at least one **strong** (E2, E5, E12, or E7 above voiceprint accept threshold **and** name consistent), and **no** conflict | **No** — curator confirms merge |
| **Medium** | 2 moderate signals (e.g. E3+E6, E4+E11) without conflict | **No** — propose merge |
| **Low** | Name string / alias similarity only (E10); or single weak API/LLM suggestion | **Do not propose merge as default**; show as “possible duplicate” at most |

#### Numeric guidance for proposals (non-live)

| Action | Minimum proposal bar |
|--------|----------------------|
| Propose episode map host (seed channel) | E1 + diarization found ≥1 stable non-ad cluster |
| Propose episode map guest | E3 or E4 **or** (E9 + name appears in metadata) |
| Propose cross-video same person (already active) | Canonical/alias match **and** (E6 or E7 or E3 on new video) |
| Propose **merge of two active persons** | Merge confidence **High** pattern above |
| Voiceprint-only propose | Match score ≥ configured accept threshold **and** enrolled person already **active**; false-accept risk → always human gate (per #13) |

**Voiceprint reject path is the safe failure:** high threshold → person stays on speaker label → manual fix.

---

## Merge rules (when two labels / candidates become one person)

### Never merge (live) when

1. Only evidence is **string similarity** or shared first/last name.
2. Either side is still only a **speaker label** with no person candidate.
3. Conflicting strong evidence (different self-IDs, incompatible bio facts).
4. One side is a **channel/org** entity type and the other is a person (type mismatch).
5. Merge would attach a high-collision alias (e.g. “Mike”, “Chris”) without disambiguator.

### May propose merge when

1. **Same strong public identity** expressed via aliases (title forms, known nicknames) **and** at least one contextual co-occurrence (shared episodes, mutual references, or curator knowledge), or  
2. Voiceprint/embedding match above threshold **and** consistent name/alias family, or  
3. Curator asserts identity (E5) with optional supporting notes.

### Must human-approve for live when

- Creating a person, attaching a collision-prone alias, merging two actives, or approving first attribution of a guest on an episode.

### Merge mechanics (conceptual)

- Choose **survivor** active person (curator picks canonical).
- Loser’s canonical name and aliases become aliases on survivor (typed).
- Episode mappings and claim edges re-point to survivor.
- Loser state → `merged-away` with redirect.
- Audit: who merged, when, evidence snapshot.

### Cross-video identity (without full person merge UI)

Normal path for recurring people:

1. Person **P** is active (e.g. Leslie Kean).
2. New video proposes `SPEAKER_01` → **P** via metadata/voiceprint.
3. Curator approves **episode mapping** (not a person–person merge).

Person–person merge is only when **two person records** were created in error (duplicate nodes).

---

## Cross-video merge and re-identification rules

| Rule | Detail |
|------|--------|
| **No label continuity** | Never join `SPEAKER_i` across videos by index |
| **Join only via person** | Video A label and Video B label co-refer only if both map to same **person_id** |
| **Hosts** | Single person node per seed host; reused across all their channel episodes and guest appearances |
| **Guests** | Single person node reused when identity evidence supports; duplicates are merge-review fodder |
| **Gallery (optional phase)** | Voiceprint/embedding gallery enrolls only **active** persons, preferably from curator-confirmed clean segments |
| **Enrollment gate** | Do not enroll unresolved labels into the gallery |
| **Threshold discipline** | Prefer false reject over false accept for gallery matches (safer for research graph) |

---

## Worked examples (normative intent)

### Example A — Clean 2-person Jesse Michels interview

1. Diarization → `SPEAKER_00`, `SPEAKER_01`.  
2. System proposes: host default Jesse Michels → larger/host-like cluster; title guest “David Grusch” → other cluster.  
3. Attribution confidence high → review UI one-click.  
4. Curator approves → live mappings; claims may attach to those persons.  
5. No new person for Jesse if already active; guest created only if not already active (with approve).

### Example B — Area52 panel with Jesse as guest

1. Host default Chris Ramsay applies only as **proposal** for host cluster.  
2. Jesse Michels proposed from title/credits → **existing** Jesse person node.  
3. Third speaker unknown → left unresolved (no “Unknown Panelist” person).  
4. Curator confirms two maps; third stays L0 only.

### Example C — “Dr. X” vs full name

1. Existing active person “Steven M. Greer” with alias title_form “Dr. Greer”.  
2. New credit string “Dr. Steven Greer” → alias attach proposal, not new person.  
3. String-only “Greer” in another video without context → **no** auto map; optional weak suggestion.

### Example D — Duplicate person nodes

1. “Lue Elizondo” and “Luis Elizondo” both active from separate approves.  
2. System detects alias collision / high merge confidence → **propose merge**.  
3. Curator approves → one survivor, aliases retained.  
4. Until approve, both remain; claims stay on their nodes (no silent redirect).

### Example E — Diarizer split same guest into two labels

1. Remote guest becomes `SPEAKER_01` then later `SPEAKER_03` (timbre split).  
2. Both may map to same person after review (two episode mappings, one person).  
3. This is **not** a person merge; it is dual attribution of labels to one person.

---

## What this intentionally does not decide

- Full KG schema / property graph DDL.
- Exact UI wireframes (only that a confirm gate exists).
- Numeric voiceprint vendor thresholds (set at implementation; policy prefers false reject).
- Credibility or trust scores for persons (deferred to a later **speaker credibility signals** ticket; this doc only keeps identity clean enough for that work).
- Legal/ToS path for obtaining audio (see youtube-ingestion-options).

---

## Downstream hook: credibility signals

Identity policy above ensures:

- Claims can hang on **stable person_ids**, not diarization labels.
- Aliases do not fork credibility histories.
- Unresolved speech does not pollute person-level stats.
- Merge audit trails allow recomputing credibility after corrections.

Credibility scoring itself is **out of scope** here.

---

## Policy cheat-sheet

```
New SPEAKER_n on a video?
  → Episode-local label only. Never mint a person from the label alone.

Map label → person for live graph?
  → Need proposal evidence + curator approve.

Seed channel host?
  → Strong provisional default to the bound host person; still confirm
    (once for person, per-episode map can be batch-approved when clean).

Guest named in title, 2 speakers?
  → High-confidence proposal; one-click confirm; still not silent auto-live.

Unknown / ads / audience?
  → Leave unresolved. No person node.

“Dr. X” vs “X”?
  → Aliases of one person after confirm; strip titles for match, keep as alias forms.

Merge two person nodes?
  → Multi-signal evidence (not string-only) + curator approve.
  → Prefer false reject on biometric match.

Same person across videos?
  → Join only through person_id, never through SPEAKER index.
```

---

## Sources / related decisions

1. Issue #5 — Speaker identity and alias merge — https://github.com/etai83/uap-kg/issues/5  
2. Issue #13 research — [speaker-diarization-options.md](./speaker-diarization-options.md)  
3. Issue #2 decision — [seed-channel-set-v1.md](./seed-channel-set-v1.md)  
4. Standing map preferences: human confirm before person-node writes; AI-proposed / human-approved extractions; named persons + diarized attributions with cross-video merge  

---

## Decision date

Recorded 2026-07-22 as the recommended resolution for issue #5 (batch completion with recommended defaults).
