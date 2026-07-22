# Seed channel set for v1

Decision asset for [Seed channel set for v1](https://github.com/etai83/uap-kg/issues/2)  
Part of [Wayfinder: UAP YouTube knowledge graph spec](https://github.com/etai83/uap-kg/issues/1)

## Decision summary

| Axis | Decision |
|------|----------|
| Spec role of list | **Committed starter set** (named channels, not illustrative examples) |
| Size | **Exactly 3** channels; no expansion beyond 3 until the pilot corpus is fixed for first build |
| Inclusion | **Density on shared cases** + **epistemic role diversity**, with **soft role quotas** (never sacrifice all multi-source overlap for role balance) |
| Language | **English-only** |
| Medium | **YouTube only** (source of truth); “episode” = YouTube video |
| Topic | Prefer **core UAP/NHI/disclosure** as primary channel focus; named channels may include a broader long-form host if the human curator vetoes in |
| Hard exclusions | Non-English primary; not YouTube; pure clip-repost/mirror channels; AI-voice essay mills; no original long-form discussion |
| Stance / “disinfo” | **Personal curator veto** at naming time — not a formal taxonomy in list rules |
| Pilot corpus | **~10 videos per channel (~30 total)**; **human selects every video**; long-form preferred (~≥20–30 min) as guidance, not a hard reject for essential short primary-source clips |
| This effort | **Profile channels for the spec**; no bulk ingest in the wayfinder map |

## Committed channels

| # | Channel | Handle | Channel URL | Epistemic role (soft) | Notes |
|---|---------|--------|-------------|----------------------|--------|
| 1 | Jesse Michels (American Alchemy) | `@JesseMichels` | https://www.youtube.com/@JesseMichels | Synthesis + investigative interview | Major UAP/NHI/disclosure vertical; also broader “nature of reality” |
| 2 | Area52 (hosted by Chris Ramsay) | `@Area52Investigations` | https://www.youtube.com/@Area52Investigations | Community synthesis / popularizer | Primary ongoing focus UAP / high strangeness / NHI |
| 3 | Danny Jones | `@dannyjones` | https://www.youtube.com/@dannyjones | Long-form interview host | Broader fringe culture show; UAP is a thick vertical — included by curator naming, not strict core-only rule |

Rough scale at profile time (order-of-magnitude only): Jesse Michels ~112K subs; Area52 ~65K; Danny Jones ~656K.

### Density rationale

Cross-presence among the three is already real (e.g. Area52 episodes featuring Jesse Michels; Danny Jones has hosted Jesse Michels and many shared-discourse guests). Soft role quotas at N=3 leave gaps (no dedicated skeptic or official-primary channel) — acceptable under the soft-quota rule.

## Pilot video pool

Target: ~30 videos (10 per channel). Curator supplies all IDs.

**Living list:** [`docs/pilot-corpus.md`](../pilot-corpus.md) — **30 / 30 confirmed** (2026-07-22).

| Channel | Count | Notes |
|---------|------:|-------|
| Jesse Michels | 10 | Grusch, Corbell, Lazar, Brazil, skeptic debate, … |
| Area52 | 10 | Lazar×3, Corbell, Skinwalker, gov videos, experiencers, Jesse diner |
| Danny Jones | 10 | TD Barnes, Pasulka, Bledsoe, Fox, McGwier, Farah, … |

Full titles + URLs + multi-telling clusters: `docs/pilot-corpus.md`.

## Profile date

Profiled 2026-07-22 from public YouTube channel/oembed metadata and public episode indexes. Not a legal or credibility adjudication.
