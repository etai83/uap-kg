# Domain glossary

Ubiquitous language for the personal UAP/NHI research knowledge graph. No implementation detail.

## Terms

### Seed channel set

The **fixed, named list of YouTube channels** the product treats as first-class sources for v1. Not an open scrape and not merely illustrative examples in the spec. v1 commits to exactly three channels (Jesse Michels / American Alchemy, Area52, Danny Jones) until a later expansion decision.

### Pilot corpus

The **human-selected set of YouTube videos** drawn from the seed channel set for the first intended load (~10 videos per seed channel, ~30 total). Selection is fully curator-owned; long-form is preferred but not a hard rule for essential short clips.

### Channel

A **YouTube channel** used as a durable source identity (handle + channel URL). Podcast mirrors on other platforms are out of scope for v1 source-of-truth; only the YouTube upload counts.

### Curator

The **sole human user** of the system. Owns channel naming vetoes, pilot video selection, and approval of AI-proposed extractions before they go live. Person-node creates, alias attaches, merges, and live speaker→person attributions require curator confirmation.

### Person

A **named real-world individual** in the knowledge graph (host, guest, or other speaker the curator chooses to track). Distinct from episode-local diarization labels. Live person nodes are curator-approved; systems may only propose candidates.
_Avoid_: speaker (use for diarization labels or role, not the graph entity), SPEAKER_00 (label only)

### Alias

An **alternate string that denotes the same person** as an existing person node (nickname, handle, spelling variant, title-bearing form such as “Dr. X”, former public name). Channel or show brands are not person aliases. Aliases do not create new people.
_Avoid_: aka (informal), duplicate name (implies error), synonym (wrong type)

### Speaker label

An **episode-local diarization ID** (e.g. `SPEAKER_00`, `spk_1`) meaning “this acoustic cluster within one video/job.” It is not a person node and has no identity continuity across videos until mapped through a person.
_Avoid_: person id, speaker node, identity

### Episode attribution

The **mapping from a speaker label on one video to a person** (or to unresolved). Provisional until the curator approves it for live claim attribution.
_Avoid_: merge (person–person only), identification (vendor feature, not the approved mapping)

### Unresolved speaker

A **speaker label left without a person mapping**. Used for unknown voices, ads, audience, or low-confidence clusters. Does not mint a person node and does not merge across videos.
_Avoid_: unknown person node, anonymous person (implies a person entity)

### Canonical display name

The **curator-facing primary name** of a person node. Other surface forms are aliases. Normalization for matching (case, honorifics, punctuation) is not the same as changing the canonical display name.
_Avoid_: legal name (optional alias type only), handle (alias type)

### Person merge

The **curator-approved collapse of two person records into one** when evidence shows they are the same individual. Weak string match alone is never sufficient for a live merge. Distinct from mapping two speaker labels on one video to the same person.
_Avoid_: alias attach (no node deleted), cross-video label join (forbidden; join only via person)

### Epistemic layer

One of five **hard types** on proposition-like nodes: raw, processed, claim, inference, assumption. Layer is set at create time and never rewritten in place. Entity identities (person, channel, video catalog object, world event) sit outside the five-layer spine.
_Avoid_: confidence band, soft type, free-text “kind”, credibility score (those are separate concerns)

### Raw

**Uninterpreted source capture**: official catalog facts and immutable media anchors (video identity, timestamps, caption/ASR references, diarization turn ids). Catalog raw may enter live without claim-level approval; it does not assert world-truth.
_Avoid_: source (ambiguous), original, evidence (overloaded)

### Processed

**Normalized structure derived from raw without asserting world-truth**: cleaned spans, speaker-attributed utterances, segment boundaries, surface tags on a span.
_Avoid_: cleaned claim, parsed claim, intermediate claim

### Claim

An **attributed, checkable assertion** about the world or a speaker’s explicit assertion, grounded in processed (hence raw) evidence via extraction provenance. Recording a claim is not a verdict that the proposition is true.
_Avoid_: fact, finding, statement (too vague), quote (quotes live at processed unless extracted)

### Inference

A **conclusion not stated as such in the source**, derived by explicit reasoning from one or more claims (and optionally other live inferences). Must not be relabeled as a claim.
_Avoid_: insight, conclusion (untyped), synthesis (UX term only)

### Assumption

A **provisional premise** adopted to scaffold analysis, not established by source text or a valid inference chain. Must never masquerade as a claim or inference.
_Avoid_: hypothesis (reserve if later formalized), guess, implicit claim

### Provenance edge

An edge that records **why a node exists or what it depends on** (e.g. derived from, extracted from, based on, rests on, proposed by, approved by). Direction is dependent → support. Distinct from content edges.
_Avoid_: source link (ambiguous), citation (document-only metaphor)

### Extraction run

A **first-class record of one pipeline or curator write invocation** that produced layered nodes (ASR, diarization, claim extract, inference propose, manual edit). Carries tool/model identity and timestamp; nodes reference the run rather than duplicating tool blobs.
_Avoid_: job (ambiguous ops term alone), session (UI), batch (may group many runs)

### Media anchor

The **raw locator set** that ties graph content to source media: primarily a YouTube `video_id` (and its catalog channel), plus timed track references (caption/ASR/diarization artifacts) when speech is involved. Catalog raw *is* the anchor; processed/claims point back to it.
_Avoid_: source (ambiguous), citation, evidence (overloaded)

### Timestamp span

A **closed-open time range on a video timeline** (`t_start`, `t_end`) locating speech or structure. Required on processed speech spans that ground claims.
_Avoid_: duration alone, chapter (structural beat), “around minute X” without bounds for live grounding

### Quote span

The **transcript or caption text** of a processed span (and, via extraction, the supporting text behind a claim). Stored with the processed node; claims may denormalize a primary quote for UI but must still `EXTRACTED_FROM` processed.
_Avoid_: paraphrase-as-quote, claim wording (claim text may summarize; the quote span is the source wording)

### Grounding path

The **required chain of legal provenance edges from a higher-layer node down to raw media anchors** (e.g. claim → processed → raw). Optional denormalized video/time/quote fields never replace a missing path.
_Avoid_: soft link, “see also”, claim→raw-only shortcut

### Content edge

An edge that records a **semantic relation** among propositions or to entities (about event/topic, attributed to person, supports, contradicts, elaborates). Content edges never change epistemic layer.
_Avoid_: related to (untyped), link

### Proposed

Lifecycle state: node is **AI- or human-drafted and not yet curator-approved**. Visible for review; not used as live graph evidence in default research views.
_Avoid_: draft (UI synonym ok), pending (ambiguous)

### Live

Lifecycle state: node is **curator-approved** and participates in default queries, timelines, and multi-telling compare. Orthogonal to epistemic layer.
_Avoid_: published (implies external publish), active (ambiguous)

### Promotion

Creating a **new higher-layer node** with legal provenance to lower support. Never an in-place change of a node’s layer field.
_Avoid_: upgrade, cast, retype

### Event

A **real-world happening** (or coherent multi-day incident / campaign parent) that speakers refer to — independent of any single video. Identity uses weighted keys: public name/case label, time window, place/theater, principal actors or platforms, and optional documentary anchors. Competing explanations of the same happening remain one Event with multiple claims. Entity identity sits outside the five epistemic layers.
_Avoid_: video segment, chapter, beat, topic (thematic type — not an instance), “the episode” (source media)

### Telling

One **account of an Event** as presented in a specific video (or continuous segment of that video), including which speakers said what. Multiple videos—and multiple segments in one video—can each contribute a Telling of the same Event. A Telling is not itself an Event.
_Avoid_: claim (layer type), transcript, episode summary

### Multi-telling

The research pattern of **lining up two or more Tellings of the same Event** (typically across seed channels) to reconstruct the story, compare agreement and conflict, and attach provenance. Product UX spine: **event timeline** + **multi-telling compare** scoped to a focus Event (or an explicit provisional identity bundle).
_Avoid_: cross-video search (too generic), stitch, compilation

### Provisional identity link

A **first-class, non-collapsing** association between Event nodes (or candidate referents) when sameness is suspected but not curator-confirmed. Used instead of silent auto-merge—especially for high-stakes named cases. Often paired with an open question (“same incident as X?”).
_Avoid_: soft merge, automatic dedupe, “probably the same” without a recorded link

### Beat (video beat)

An **in-video structural unit** (chapter, clip, continuous discussion stretch). Beats organize source media; they are **not** Events. One beat may discuss several Events; one Event may span many beats across videos.
_Avoid_: event, scene (ambiguous with world events)

### Atomic claim

A claim that expresses **one checkable proposition** — single speaker attribution, independently approvable, and usable in support/contradict compare without internal “and/or” ambiguity. Live claims must be atomic.
_Avoid_: summary claim, bullet list claim, multi-fact paragraph

### Compound claim

Speech or a draft extraction that **bundles two or more independent propositions**. Allowed only as non-live staging for split review; must be split into atomic claims before live.
_Avoid_: rich claim, full utterance (utterances live at processed)

### Claim text

The **normalized declarative proposition** stored on a claim node (the multi-telling compare surface). Close paraphrase of what the speaker asserted; not a raw transcript dump and not a multi-paragraph summary.
_Avoid_: quote (evidence excerpt), paraphrase cluster id, title

### Claim kind

A **v1 classifier** on a claim: `world_assertion` (about the world/happening), `meta_speech` (about what was said or claimed), or `self_report` (speaker’s own experience/role). Does not change epistemic layer.
_Avoid_: layer, genre, topic

### Unbound claim

A claim with **no `ABOUT_EVENT` binding** because event keys are insufficient or identity is unresolved. Still a first-class claim with attribution and provenance; curator may bind later. Prefer unbound over inventing an Event.
_Avoid_: orphan (implies error), floating fact, topic-only claim (topics are optional sugar)

### Meta-claim

A claim of kind **`meta_speech`**: the attributed speaker asserts something about **speech or testimony** (including third-party claims). Does not auto-import the third party’s world-assertion without separate grounding.
_Avoid_: host paraphrase merged into guest (forbidden silent merge), inference about dialogue

### Same-assertion link

A content edge (`SAME_ASSERTION_AS`) between **two distinct claim nodes** that express the same (or paraphrastic) assertion across tellings or videos. Does **not** collapse them into one claim id.
_Avoid_: merge claims, dedupe to one node, synonym

### Grounding span

The **processed utterance or text span** a claim is extracted from (`EXTRACTED_FROM`), itself derived from raw video/time anchors. Live claims require this path so “who said what, when, in which video” remains recoverable.
_Avoid_: citation only, screenshot, memory

### Speaker credibility

**Soft research metadata** about a Person: curator notes, optional role/flag labels, and (when multi-telling data exists) person×event consistency observations. Not person identity, not an epistemic layer, and not a verdict that claims are true or false. v1 is qualitative-first; composite trust scores are out of scope.
_Avoid_: trust score, credibility rating, reliability %, reputation score (forbidden as system-invented objective metrics in v1)

### Role label

A **descriptive tag** for the function a person plays in discourse or in a happening (e.g. host, guest, witness-participant, secondhand, researcher/journalist, official/institutional). Episode-scoped or person-default. Labels are not trust multipliers and do not create identity.
_Avoid_: trust tier, authority level, credibility grade

### Consistency observation

A **provenance-backed note that the same person’s claims/tellings about the same Event agree, conflict, or drift** (or that multi-telling data is insufficient). Derived candidates may be AI-proposed; live annotations are curator-gated. Scoped person×event (or provisional event bundle)—not a global reputation number.
_Avoid_: trust score, reliability index, speaker grade

### Topic

A **thematic type** of discussion used to index and filter the graph (e.g. Navy UAP, crash retrieval, Moon anomalies, congressional hearings). Represented as a lightweight entity node outside the five epistemic layers, drawn from a **curator-owned controlled taxonomy** (canonical name + optional aliases + optional shallow parent). A Topic may index many Events and Claims; it is never itself an Event. Sharing a Topic does not merge Events. Long-running programs or discourse eras are modeled as Topics in v1 unless later split into a dedicated program entity.
_Avoid_: event, tag (alone — free strings are not live Topics), category (UI synonym only), mega-event (anti-pattern)

### Surface tag

A **free or provisional thematic string** attached at the **processed** layer (span/utterance) during extraction. Surface tags assist search and mapping; they do **not** mint live Topic nodes until mapped into the controlled taxonomy and curator-approved.
_Avoid_: topic node, live topic, free-tag-as-ontology

### Contradiction record

A **first-class research object** (outside the five epistemic layers) that packages a logical conflict among live claims and/or inferences about a focus Event or provisional identity bundle — member pointers, optional facet, status, and notes. Built on `CONTRADICTS` edges; not a sixth layer, not a truth verdict, and not an Event split. Assumptions never appear as evidence poles.
_Avoid_: conflict score, winner claim, sixth layer, topic-only auto-conflict

### Open question

A **first-class, curator-gated research object** that records unsettled research state (identity doubt, claim-conflict follow-up, coverage gap, key disagreement, attribution, or other). Lifecycle: proposed → open → resolved | wontfix (plus rejected for bad proposals). System/AI may propose; only the curator opens, resolves, or wontfixes. Distinct from a claim and from a contradiction record (though it may reference either).
_Avoid_: soft claim, uncertainty layer, TODO comment without structure

### Coverage gap

**Missing assertable content** under a focus Event (or provisional bundle) for a research facet — nobody (adequately) claimed it in the live graph. Surfaced as a derived coverage view and/or an open question of kind `coverage_gap`. Not a contradiction; do not invent opposing claims to fill it. Explicit scaffolding of a missing premise is an **assumption**, not a gap claim.
_Avoid_: contradiction, empty event, failed extraction (pipeline issue, not research gap)

### Conflict pair

Two **live claims or inferences** linked by a `CONTRADICTS` content edge (and typically members of one contradiction record) that assert incompatible content on a comparable facet about the same focus Event or provisional bundle. Identity “same Event?” pairs are **not** conflict pairs.
_Avoid_: disagreement on emphasis only, topic co-occurrence, assumption-vs-claim as evidence

### Rejected

Lifecycle state: node was **curator-declined** and is retained for audit (and optional re-proposal learning). Not used as live graph evidence.
_Avoid_: deleted (implies gone), failed extraction (pipeline status, not curator decision)

### Superseded

Lifecycle state: node was **replaced by a newer same-layer successor** via a `SUPERSEDES` edge. History remains walkable; default views use the live successor.
_Avoid_: deleted, edited in place, promoted (promotion is a new higher layer)

### Supersession

The **versioning pattern** for corrections: mint a new same-layer node, link it with `SUPERSEDES` to the prior node, and set the prior node to `superseded` when the successor is live. Layer never changes; live semantic payloads are not patched in place.
_Avoid_: in-place edit of live content, layer upgrade, soft delete without successor

### Catalog exception

Policy that **official YouTube catalog raw** (channel identity, video identity, public metadata snapshots) and **mechanical media-track pointers** may enter **`live` without claim-level / extraction approval**. Speech structure, claims, and identity writes remain gated.
_Avoid_: auto-approve extractions, trust all API fields as claims

### Approval bundle

The **default review unit** for a personal solo workflow: a video-scoped set of related proposals (episode maps, processed spans, claims, optional inferences) presented together so the curator can batch- or item-approve with dependency closure.
_Avoid_: global approve-all, silent auto-live batch

### Atomic co-approval

A **single curator action** that flips multiple dependent nodes to `live` together only when the **post-state** is matrix-legal (e.g. episode map + processed + claim in one gesture).
_Avoid_: approve top node while supports stay proposed, partial fail-open

### Batch approve

Curator-selected **multi-node approve** within a scope (usually one video bundle) where **each** node independently passes its live checklist and dependencies are satisfied or co-included. Never driven by confidence timers alone; never hides epistemic layer.
_Avoid_: auto-land, approve-all-time, confidence auto-live

### Live gate

The **hard rule that only the curator** may transition gated objects to `live`. AI and pipelines may write `proposed` freely; they may not complete extraction-derived nodes, person identity writes, or other gated entities to live state.
_Avoid_: publish pipeline, auto-merge to production

### Event timeline

The **chronological index of world Events** (by Event time window, not upload date) that forms one half of the product UX spine. Used to browse, filter, and select a focus Event (or provisional identity bundle) before multi-telling compare. Topics may filter the list; they are not timeline nodes.
_Avoid_: video upload feed, channel playlist, topic stream as substitute timeline

### Focus Event

The **single Event currently scoped** for multi-telling compare (confirmed or working node). All default claims, contradiction records, coverage gaps, and open questions on the compare surface hang on this focus (or on an explicit provisional identity bundle instead).
_Avoid_: selected video, selected topic, “current episode”

### Provisional identity bundle

An **explicit multi-Event compare scope** linking Event candidates connected by provisional identity links so the curator can “compare as if same” without collapsing IDs. Claims remain on their Event IDs and are badged by membership; identity open questions stay prominent. Distinct from a confirmed single focus Event.
_Avoid_: silent merge, soft-delete of Event IDs, topic cluster as bundle

### Research facet

A **short label for what aspect of an Event** a claim, agreement cluster, contradiction, or coverage cell is about (e.g. time, place, kinematics, object_description, origin_explanation, sensors). Facets organize multi-telling columns and gap matrices; they are not an epistemic layer and not Event identity keys.
_Avoid_: topic (thematic type across many Events), layer, credibility score

### Compare unit

The **primary row of multi-telling compare**: a **live atomic claim** (optionally a live inference, clearly badged). Assumptions are never compare units in evidence or conflict tables.
_Avoid_: video, telling-as-row-only without claims, raw quote without claim extraction, trust-ranked speaker card

### Jump to timestamp

The **minimum media action** that opens the source video at the claim’s (or contradiction pole’s) provenance timestamp span via the legal claim → processed → raw path, with quote context when available. Disabled when grounding is incomplete; never invents a time from Event keys or upload date alone.
_Avoid_: open channel home, open video at 0:00 without span, jump from assumption “inspired by” links as if they were grounding

### Video (catalog)

A **YouTube video identity** in the knowledge graph (stable `video_id` plus public metadata snapshot): title, channel, published time, duration, caption-available flag, URLs. Catalog raw may enter live without claim-level approval. Not an Event and not a Telling by itself; Tellings and processed spans hang on videos as media.
_Avoid_: episode (informal synonym only — source of truth is the YouTube video), event, beat

### Episode map

The **per-video mapping of speaker labels to Person candidates or unresolved**, with review status (needs_review / approved / rejected). Staging for live claim attribution; host defaults may seed the map but do not auto-live person writes.
_Avoid_: person merge (cross-person collapse), global speaker graph, diarization output alone

### Nested Event

An Event that participates in a **parent/child** structure (e.g. multi-day campaign parent with day or encounter children). Multi-telling compare defaults to a chosen focus Event (parent or child), not an automatic rollup of all descendants as one claim board without explicit scope.
_Avoid_: topic hierarchy as event tree, video chapter tree as event tree

### Agreement (multi-telling)

The research surface where **live claims or inferences about the same focus Event (or provisional bundle) assert the same or mutually supporting content**, typically via `SAME_ASSERTION_AS` and/or `SUPPORTS`. Optional agreement clusters may be **derived for UX**; they are not a required stored node type in v1 and are not truth verdicts.
_Avoid_: claim merge into one id, consensus score, majority vote as ontology

### Edge kind

The **top-level classification of a graph edge** as either **provenance** (why a node exists / what it depends on) or **content** (semantic relations among propositions or to entities). Edges are not epistemic layers; layer lives on nodes only.
_Avoid_: soft link, untyped “related to”, layer on edge

### Spec complete

Status of the written **system+product specification** when every required section is filled to the implementability bar (normative rules + decision pointers + deferred appendix), with no open model debates on closed wayfinder subjects. **Spec complete does not mean the product is built.**
_Avoid_: MVP shipped, pipeline done, map abandoned without writing the spec
