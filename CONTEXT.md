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
