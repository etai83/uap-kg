# Event identity rule

Decision asset for [Event identity rule](https://github.com/etai83/uap-kg/issues/4)  
Part of [Wayfinder: UAP YouTube knowledge graph spec](https://github.com/etai83/uap-kg/issues/1)

## Decision summary

| Axis | Decision |
|------|----------|
| What an Event is | A **real-world happening** (or coherent multi-day incident) referred to by speakers — **not** a video segment, chapter, or in-video narrative beat |
| What a Telling is | One **account of an Event** as presented in a specific video (or continuous segment of that video), with speaker(s), claims, and provenance |
| Primary identity keys | **Public name** (when stable) + **time window** + **place / theater** + **principal actors or platforms** |
| Sameness test | Same real-world referent under a **weighted key match**, not identical wording across tellings |
| Nested structure | Events may have **parent / child** links (campaign → day → encounter); multi-telling compare defaults to a chosen **focus Event** |
| Multi-day incidents | Prefer **one parent Event** with optional **day/phase children** when public discourse treats them as one incident |
| Disagreement on keys | **Do not auto-merge** when high-stakes keys conflict without human resolution; keep separate or provisionally linked |
| Uncertain identity | **Provisional link** + **open question**; never silent auto-merge of high-stakes Events |
| Authority to merge/split | **Curator-approved** for live graph writes; AI may only propose |
| Relation to Topics | Events are **instance-level** happenings; Topics are **types / themes** of discussion (decided fully in #11) |

## Core distinction (non-negotiable)

### Event ≠ video beat

| Concept | Definition | Example |
|---------|------------|---------|
| **Event** | Something that happened (or is alleged to have happened) in the world, independent of any single video | The November 2004 USS *Nimitz* / Tic Tac encounters off San Diego |
| **Telling** | How a video (and its speakers) narrates that Event | Fravor’s account on Danny Jones; a Jesse Michels synthesis of the same case; an Area52 recap |
| **Beat / segment** | An in-video structural unit (chapter, monologue stretch, clip) | “Minute 42–58: guest describes Tic Tac” — **not** an Event node |

Two tellings that both discuss “the Tic Tac” refer to the **same Event** even if one is 3 minutes and one is 40 minutes. Two separate historical incidents that a host chains in one monologue are **two Events**, even if they sit in one continuous beat.

**Primary job alignment:** the UX spine is **event timeline + multi-telling compare**. Identity must answer: *which real-world happening are we lining up across Jesse Michels, Area52, and Danny Jones?*

## Identity keys

Keys are **evidence for sameness**, not a rigid composite primary key that fails if one field is missing. Match strength is scored; the curator gates live merges.

### Key set (v1)

| Key | Role | Granularity guidance | Missing / weak |
|-----|------|----------------------|----------------|
| **K1 — Public name / case label** | Strong anchor when discourse has a stable name | Prefer community-standard labels: “Nimitz / Tic Tac (2004)”, “GoFast”, “Gimbal”, “Phoenix Lights”, “Rendlesham”, “Grusch July 2023 SSCI hearing” | Many claims lack a name; do not invent branding. Use provisional labels (`unlabeled-encounter@approx-date@place`) until named |
| **K2 — Time window** | Primary discriminator among similar encounters | Prefer **calendar date or tight range**; multi-day campaigns use an interval. Partial dates OK (`2004-11`, `~Nov 2004`) | Vague (“years ago”, “during the program”) → low weight; may only support provisional links |
| **K3 — Place / theater** | Geographic or operational setting | Prefer named waterspace, base, city, range, or theater (“SOCAL OPAREA”, “Area 51 / Groom Lake”, “U.S. Capitol / SSCI SCIF”) | “Out west” / “in space” without further fix → weak |
| **K4 — Principal actors / platforms** | Who or what was involved as primary participants | Named persons, units, ships, aircraft, agencies, or clearly identified platforms (e.g. USS *Nimitz*, CDR Fravor, “Tic Tac object” as *observed object role*, not as ontology of craft type) | Anonymous “a pilot” alone is weak unless tied by K1–K3 |
| **K5 — Public / documentary anchors** (optional booster) | External referents that stabilize identity | Hearing date + committee; official report section; widely cited FOIA doc; canonical news date | Helpful when present; **not required** for personal KG events that only exist in oral history |

### Explicit non-keys (do not use as identity)

| Anti-key | Why |
|----------|-----|
| Video ID, channel, upload date | Source metadata; many videos → one Event |
| Speaker who is *retelling* (host, podcaster) | Attribution lives on the Telling, not the Event’s identity — unless that person is a **principal actor in the happening** (e.g. Fravor as witness-participant) |
| Claim content / interpretation | “It was NHI” vs “it was a secret drone” are **competing claims about** an Event, not different Events |
| Topic tags | “UAP”, “disclosure”, “Moon anomalies” are topical; see Topics vs Events (#11) |
| Emotional intensity or runtime spent | Editorial emphasis, not identity |

### Public name normalization (light rules)

- Treat well-known aliases as the same label cluster: “Tic Tac” ≈ “Nimitz incident” ≈ “2004 *Nimitz* encounters” **when** K2–K4 agree on the 2004 SOCAL carrier group events.
- Do **not** collapse distinct named cases that share a motif: “Tic Tac-like object in 2015” ≠ 2004 *Nimitz* Tic Tac.
- Prefer one **canonical display name** plus an **alias list** on the Event; aliases are not separate Events.

## Sameness criteria (merge vs split)

### Same Event (merge candidates)

Propose **same Event** when **any** of the following holds:

1. **Stable public name + compatible keys** — Same case label cluster and no hard conflict on K2–K4 (example: two videos both mean 2004 *Nimitz* / Tic Tac).
2. **Strong multi-key match without a name** — Compatible time window **and** place/theater **and** overlapping principal actors/platforms, with no hard conflict.
3. **Documentary anchor match** — Same hearing/report/incident ID (e.g. both clearly mean the 26 July 2023 House UAP hearing with Grusch/Fravor/Graves), even if casual speech is vague.

“Compatible” means: overlapping or nested time windows; same or clearly co-referring place; actor sets that intersect on principals (not merely sharing a host who discusses both).

### Distinct Events (split)

Keep or create **distinct Events** when **any** hard split condition holds:

1. **Hard time conflict** — Non-overlapping windows that cannot be reconciled as multi-day phases of one incident (e.g. 2004 vs 2015 East Coast ship incidents).
2. **Hard place conflict** — Incompatible theaters with no narrative of a linked multi-site campaign (SOCAL 2004 vs Arizona 1997 Phoenix Lights).
3. **Different public case identity** — Discourse and keys point at different canonical cases (Gimbal ≠ GoFast ≠ FLIR1/Tic Tac package components may still be **children** under a parent “2014–2015 Navy UAP videos release” campaign — see nesting).
4. **Retelling of a telling is not a new Event** — A host summarizing Fravor’s prior interview still points at the **same world Event**; the new video is a new **Telling**.
5. **Claim-only divergence** — Tellings disagree on explanation, intent, or craft type → **same Event**, competing claims (feeds contradiction model #8), **not** a split.

### Disagreement on date or place (merge/split rules)

| Situation | Rule |
|-----------|------|
| Tellings give different **exact dates** but same week/operation and same actors/place | Prefer **one Event** with a **time-window** (not a single day) and record date disagreement as **claim-level** or open question on the Event |
| Tellings give different **years** or non-overlapping windows | **Default split** unless a curator accepts a documented correction (misremembered year) and merges with provenance note |
| One telling has a precise date; another is vague but matches place + actors + name | **Same Event**; attach precision to the best-supported window; flag low-precision telling |
| Place names differ but are nested/alias (“San Clemente Island ops area” vs “off San Diego”) | **Compatible** → same Event |
| Place names conflict at country/theater level with no bridge | **Split** (or provisional link only if a speaker asserts they are the same incident — open question) |
| One telling relocates a famous case (e.g. claims Tic Tac was “in the Atlantic”) | Do **not** silent-merge with the canonical SOCAL Event; **provisional link** + open question “same as Nimitz 2004?” |

### High-stakes Events

Treat as **high-stakes** (stricter gate, no silent auto-merge):

- Named historical cases with public controversy (Nimitz, Phoenix Lights, Rendlesham, Roswell, etc.)
- Congressional / intelligence hearings and formal testimony events
- Incidents used as load-bearing evidence in disclosure narratives
- Any Event the curator marks sensitive

**Rule:** AI may propose merge/split; **live merge of high-stakes Events requires explicit curator approval.** Prefer over-split + provisional links over silent collapse.

## Nested events and multi-day incidents

### Nesting model

```
Parent Event (campaign / multi-day incident / hearing day-series)
├── Child Event (day, sortie, specific encounter, session)
│   └── Optional grandchild (single sensor track, single visual, etc.) — use sparingly in v1
└── Child Event …
```

**v1 guidance:** prefer **shallow** trees (parent + children). Grandchildren only when multi-telling compare truly needs a tighter focus (e.g. “Fravor visual” vs “Princeton SPY-1 tracks” under *Nimitz* 2004).

### When to use a parent

Create a **parent Event** when public discourse and research value treat a **bundle** as one incident **and** also discuss separable sub-happenings:

| Pattern | Parent | Children (examples) |
|---------|--------|---------------------|
| Multi-day ops | *Nimitz* carrier group UAP activity (≈ Nov 2004) | Specific Fravor/Underwood encounter window; Princeton tracking days; “Tic Tac” white paper / later public release as **documentary** child only if treated as a happening (usually: release is its own Event — see below) |
| Hearing series | “2023 UAP congressional testimony wave” (optional parent) | 26 July 2023 House hearing; Grusch’s closed SSCI session(s) as distinct if keys differ |
| Multi-site same night | Phoenix Lights (13 Mar 1997) | “V-shape over Phoenix” vs “flare drop over Estrella / Luke AFB explanation cluster” **only if** curator wants compare at that grain; otherwise one Event with competing claims |
| Program / campaign (careful) | “AAWSAP/AATIP era” is usually a **Topic or program entity**, not an Event — do not force program-years into a single Event |

### Multi-day rule of thumb

- If speakers say “the *Nimitz* incident” as **one story**, use **one parent Event** with a **time interval**.
- Promote a day/encounter to a **child Event** when at least one of:
  - Multiple tellings isolate that sub-happening for comparison, or
  - Keys (time of day, platform, witness set) cleanly separate it, or
  - Contradictions attach cleanly to the sub-happening rather than the whole campaign.

### Nested vs sequential distinct Events

| Speakers describe… | Model as… |
|--------------------|-----------|
| Phases of one continuous incident | Parent + children (or one Event with phases as structured notes if no multi-telling need) |
| Follow-up years later (investigation, leak, hearing about a past case) | **Separate Events**, linked by relation `about` / `concerns` / `testimony-regarding` (relation names finalized with claim/provenance tickets) — **not** the same Event as the original incident |
| Media package release (e.g. 2017 NYT / Pentagon videos) | **Its own Event** (a publication/disclosure happening), related to earlier encounter Events — do not merge release day with 2004 ops |

## Uncertain identity

### States

| State | Meaning | Graph behavior |
|-------|---------|----------------|
| **Confirmed same** | Curator (or policy-equivalent approval) accepted merge | Single Event ID; tellings point here |
| **Confirmed distinct** | Curator accepted split | Separate Event IDs; optional “related” link |
| **Provisional same** | AI or curator suspects sameness; not approved for collapse | Two Event nodes (or one provisional + candidates) connected by a **provisional identity link**; multi-telling compare may offer “compare as if same” without destroying IDs |
| **Unknown / open** | Insufficient keys | Keep separate; attach **open question** (“Same incident as X?”) |

### Rules for uncertainty

1. **Never silent auto-merge** high-stakes Events. Medium/low-stakes may auto-**propose** only; live write still follows human-approval preference.
2. **Provisional links are first-class** for research: they preserve doubt instead of forcing a false timeline node.
3. **Open questions** (see #8) should hang on provisional pairs: who asserted identity, which keys matched/conflicted, what would resolve it.
4. **Downstream claims** stay attached to the Event ID used at extraction time; on merge, claims re-parent with provenance of the merge decision; on split, claims must be re-assigned (curator-assisted).
5. When a telling is **ambiguous** (speaker could mean case A or B), attach the Telling to **neither** confirmed Event until resolved — or attach to a **provisional** target with low confidence — rather than guessing.

### What “uncertain” looks like in UX (spec-level, for #14)

- Timeline: provisional Events marked as such; optional “possible duplicate of…”.
- Multi-telling compare: explicit mode **Confirmed Event** vs **Provisional bundle**.
- No presentation that implies certainty the curator has not granted.

## Worked examples (UAP discourse)

### 1) *Nimitz* / Tic Tac (2004)

| Telling source (illustrative) | Points to |
|------------------------------|-----------|
| Pilot interview describing Nov 2004 SOCAL intercept of capsule-shaped object | **Event:** *Nimitz* / Tic Tac encounters (2004) |
| Later synthesis show recapping Fravor + Princeton + FLIR | **Same Event** (or parent + children if sub-encounters are split) |
| Discussion of 2017 public release of FLIR1 | **Distinct Event:** 2017 video/disclosure release, **related to** 2004 encounters |
| “Tic Tac-like” object on another ship years later | **Distinct Event** unless keys truly match 2004; motif similarity ≠ identity |

**Nested option:** Parent “*Nimitz* Nov 2004 UAP activity” → child “Fravor / White aircraft visual encounter”; child “Underwood FLIR sequence”; child “Princeton tracking”.

### 2) Grusch testimony / hearings (2023)

| Happening | Event identity |
|-----------|----------------|
| David Grusch’s **public** House hearing appearance (26 July 2023) with Fravor & Graves | **Event A** — public hearing (date + Capitol + named witnesses) |
| Grusch’s **closed** SSCI / intel committee sessions (different dates/venues) | **Event B** (or B1, B2…) — do **not** merge with the televised hearing solely because “Grusch testified” |
| Podcast retellings of what Grusch said about crash retrievals | **Tellings** of claims **about** alleged programs/incidents; the podcast airing is not Event A; load-bearing alleged retrievals are **other Events** (often low-key / provisional) if pinned to real-world happenings |

**Split rationale:** public hearing ≠ closed session (time/place/audience keys differ). **Link** with `related-testimony` / campaign parent only if useful.

### 3) Moon photo / NASA censorship claims (pilot-adjacent)

Pilot corpus includes synthesis content such as Jesse Michels on alleged NASA Moon photo censorship.

| Referent | Model |
|----------|--------|
| A **specific** mission photo, date, and claimed alteration instance | Candidate **Event** (or set of Events) if keys can be fixed (mission, frame, date) |
| “NASA has long censored Moon anomalies” as a general thesis | **Topic / claim cluster**, not one Event — avoid a mega-Event “all Moon censorship” |
| Apollo-era surface activity anecdotes tied to named mission/EVA | Separate Events per mission/EVA when keys support it; provisional when speakers blur missions |

**Rule of thumb:** if multi-telling compare would mix incompatible missions under one node, **split**. If speakers only ever argue a single famous frame, one Event is enough.

### 4) Same guest, different incidents

TD Barnes (or similar Area 51 witnesses) on Danny Jones may cover decades of work. Each discrete happening they recount (a specific test, a specific year, a specific VIP visit) is its **own Event** when keys differ. The **interview video** is one source with **many Tellings** (one per Event discussed).

## Lifecycle (spec-level)

```
AI extraction from video
  → proposes Event match (existing | new | provisional pair)
  → curator approves / edits / rejects
  → live Event graph updated
  → multi-telling index refreshed for that Event
```

- **Propose, don’t publish** (standing preference).
- Merges and splits after go-live leave an **audit note** (who, when, from→to IDs) — exact provenance schema is #7.
- Reversible merges preferred: keep tombstoned IDs or merge records so claims can be reassigned.

## Implications for blocked tickets

| Ticket | Implication |
|--------|-------------|
| **#11 Topics vs events** | Events = particular happenings with keys above; Topics = thematic types (e.g. “Navy UAP”, “Moon anomalies”, “crash retrieval”). A Topic may index many Events; an Event is not a Topic. |
| **#14 Multi-telling compare UX** | Compare is always scoped to one **focus Event** (confirmed) or an explicit **provisional bundle**. Show identity state, key summary, child Events, and link to related but distinct Events (e.g. hearing about a case). |
| **#8 Contradiction / open question** | Cross-telling conflicts on **explanation** stay on one Event; conflicts on **whether two referents are the same** are identity open questions, not claim contradictions. |
| **#6 Claim model** | Claims should reference Event IDs (or explicit “unbound” when no Event); identity uncertainty must not silently retarget claims. |

## Out of scope for this decision

- Graph database schema / ID format
- Automated clustering algorithms beyond “AI proposes”
- Full relation type taxonomy beyond the identity and nesting needs above
- Topic taxonomy (#11)
- Credibility of witnesses (#10) — credibility does **not** change Event identity
- Legal status of alleged events (happened vs not) — the KG stores **referents as used in discourse**; reality adjudication is claim/epistemic layer work (#3, #6), not identity collapse

## Profile / decision date

Decided 2026-07-22 for the wayfinder spec. Spec-only; no implementation.
