# Speaker diarization options for long-form video

**Issue:** [#13 — Speaker diarization options for long-form video](https://github.com/itaiharpaz/uap-kg/issues/13)  
**Researched:** 2026-07-18  
**Scope:** Practical options for **speaker diarization + name attribution** on long-form YouTube interviews/podcasts, for person-node attribution with human review in a personal UAP research pipeline.

---

## Question

What are the practical options for **speaker diarization** (“who spoke when?”) and **name attribution** (“which person node is that?”) on long-form YouTube interviews and podcasts?

We care about:

1. Separating speakers into stable labels across a 1–3+ hour episode.
2. Mapping those labels to real person names (host, guest, panelists) so claims can be attributed to **person nodes**.
3. Quality that is **good enough with human review**, not fully automatic KG ingestion.
4. Cost and operational fit for a low-volume personal research pipeline (not call-center scale).

**Two distinct problems** (most stacks solve only the first):

| Problem | Output | Typical support |
| --- | --- | --- |
| **Diarization** | `SPEAKER_00` / `spk_0` / word-level speaker tags | Almost all options |
| **Name attribution / identification** | `SPEAKER_00` → “Leslie Kean” | Only some APIs (voiceprints or known-name/role mapping); otherwise manual or LLM-assisted |

---

## Options comparison

### Summary table

| Option | Type | STT included? | Diarization | Name attribution | Long-form fit | Cost signal (public, ~2026) | Best for |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **pyannote.audio `community-1`** | Open-source (local GPU) | No | Excellent open SOTA | No (IDs only); premium voiceprint ID via pyannoteAI | Strong; exclusive diarization helps STT align | Free compute + HF token; GPU required | Local diarization backbone |
| **pyannoteAI (`precision-2` + voiceprints)** | Hosted API | Optional STT orchestration | Premium; better DER than community-1 | **Yes** — voiceprints (`/voiceprint` + `/identify`) | Strong | Developer €19/mo incl. hours; P2 diarization ~€0.112/h (Developer) / €0.096/h (Starter); ID ~€0.146–0.125/h; voiceprint €0.015 each | Recurring speakers + confidence scores |
| **WhisperX** | Open-source pipeline | Yes (Whisper / faster-whisper) | Via pyannote | No (speaker IDs only) | Strong for long audio; word-level timestamps | Free compute; needs HF token for pyannote | End-to-end local ASR + diarization |
| **NVIDIA NeMo** | Open-source toolkit | Separate ASR collection | Sortformer (E2E) + cascaded clustering | No built-in name ID | Cascaded better for unknown #speakers / long sessions; Sortformer capped ~4 spk | Free compute; GPU | Research / fine-tuning, not simplest path |
| **AssemblyAI** | Hosted STT API | Yes | Yes (`speaker_labels`) | **Yes** — name/role via Speech Understanding | Strong for podcasts/interviews | U3.5 Pro $0.21/hr + diarization $0.02/hr (+ experimental $0.065/hr); Speaker Identification +$0.02/hr; $50 free credits | Fast path with known guest names |
| **Deepgram** | Hosted STT API | Yes (Nova) | Yes (`diarize_model`); word-level speaker + confidence (batch) | No native names (numeric speakers only) | Strong; batch diarizer v2 | Nova-3 pre-recorded ~$0.0048/min (~$0.29/hr); diarization add-on $0.0020/min streaming (pre-recorded listed as included in some plan matrices — verify current page) | Cheap fast STT + diarization |
| **Google Cloud Speech-to-Text** | Hosted STT API | Yes | Yes (`diarizationConfig`, min/max speakers) | No (numeric `speakerLabel`) | Supported; check language support page | V2 standard ~$0.016/min (~$0.96/hr) first 500k min; dynamic batch $0.003/min; diarization not separately itemized on pricing page | If already on GCP |
| **AWS Transcribe** | Hosted STT API | Yes | Yes; **max 30 speakers**; labels `spk_0`… | No (numeric only) | Batch + streaming | Diarization **included** in standard pricing; batch example ~$0.006–0.024/min depending on tier/region (verify regional rate card) | If already on AWS |

Prices change; treat numbers as **signals** and re-check vendor pages before budgeting.

---

### 1. pyannote.audio (open-source) + pyannoteAI (hosted)

**Primary sources:** [pyannote-audio GitHub](https://github.com/pyannote/pyannote-audio), [community-1 model card](https://huggingface.co/pyannote/speaker-diarization-community-1), [pyannoteAI site](https://www.pyannote.ai/), [pricing](https://www.pyannote.ai/pricing), [voiceprint identification tutorial](https://docs.pyannote.ai/tutorials/identification-with-voiceprints).

**Capabilities**

- Open pipeline **`pyannote/speaker-diarization-community-1`** (pyannote.audio 4.x, CC-BY-4.0): mono 16 kHz; auto downmix/resample; optional `num_speakers` / `min_speakers` / `max_speakers`.
- Outputs turn-level speaker labels (`speaker_0`, …). **Exclusive** speaker diarization (`output.exclusive_speaker_diarization`) simplifies aligning diarization turns with imprecise ASR timestamps.
- Published DER benchmarks (2025-09) show **community-1** better than legacy **3.1** on most sets; premium **precision-2** further improves (e.g. CALLHOME part 2: 28.5 → 26.7 → 16.6 DER).
- Local speed on H100: community-1 ~31–37 s per hour of audio; precision-2 (self-hosted) ~14 s/hour on reported benchmarks.
- **pyannoteAI premium:** `precision-2` diarization, confidence scores, **voiceprints**, **speaker identification**, STT orchestration (Parakeet / Whisper Large v3 turbo).
- Identification flow: enroll ≤30 s clean single-speaker clip → voiceprint → `/identify` against multi-speaker audio with confidence per candidate and optional match threshold.

**Limits**

- Open models do **not** map to human names; only speaker indices.
- HF user agreement + access token required for community-1.
- Voiceprints do **not** improve diarization accuracy; they only label clusters. False matches possible if voiceprints of people not present are included.
- Voiceprint job outputs deleted after 24 hours — store embeddings yourself.
- GPU strongly preferred for local runs.

**Cost signals**

- Local community-1: infra only (GPU time).
- Hosted (Developer plan): €19/month including substantial monthly hours; overage rates include Precision-2 diarization ~€0.112/h, Community-1 hosted ~€0.035/h, identification ~€0.146/h, voiceprint €0.015 each (Starter slightly lower per-hour on P2). Free trial credits advertised (e.g. identification hours + voiceprints).

**Name attribution path:** Best-in-class for **biometric** re-ID of recurring UAP researchers/hosts if you enroll voiceprints. Still needs human gate before person-node commit.

---

### 2. WhisperX

**Primary sources:** [m-bain/whisperX](https://github.com/m-bain/whisperX), paper [arXiv:2303.00747](https://arxiv.org/abs/2303.00747).

**Capabilities**

- Batched Whisper ASR (faster-whisper backend; up to ~70× realtime claimed for large-v2).
- Forced alignment (wav2vec2) for **word-level timestamps**.
- **Speaker diarization** via pyannote (`DiarizationPipeline`; currently community-1 / HF token).
- CLI: `--diarize` with optional `--min_speakers` / `--max_speakers`.
- Assigns speaker IDs onto aligned words/segments (`assign_word_speakers`).

**Limits** (documented by authors)

- “Diarization is far from perfect.”
- Overlapping speech handled poorly by Whisper and WhisperX.
- Alignment dictionary misses some tokens (numbers, currency) → no timing.
- Language-specific alignment models required for non-English.
- Dependency stack (CUDA, pyannote, HF agreements) can be fragile to set up.
- No built-in name attribution.

**Cost signals**

- Free software; cost = local/cloud GPU. Suitable for bulk offline processing of YouTube rips.

**Name attribution path:** Diarize + transcribe locally → map `SPEAKER_00/01` to host/guest via (a) episode metadata + first-speaker heuristics, (b) LLM prompt with known guest list + transcript snippets, (c) optional pyannoteAI voiceprints on the same audio.

---

### 3. NVIDIA NeMo

**Primary sources:** [NeMo speaker diarization overview](https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/asr/speaker_diarization/intro.html), [models](https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/asr/speaker_diarization/models.html), [Sortformer HF notes](https://huggingface.co/nvidia/diar_streaming_sortformer_4spk-v2.1).

**Capabilities**

- **End-to-end Sortformer** (incl. streaming): frame-level speaker activity; arrival-time ordered labels.
- **Cascaded pipeline:** VAD (MarbleNet) → embeddings (TitaNet) → clustering → optional neural diarizer (MSDD / TS-VAD). Cascaded systems have **fewer restrictions on speaker count and session length**.
- Can combine with NeMo ASR for speaker-attributed transcripts.
- Fine-tuning and research-grade configurability.

**Limits**

- Sortformer / streaming Sortformer: typically **max ~4 speakers**; degrades beyond that. Training configs often use `session_len_sec: 90` chunks; long sessions need chunking/post-processing.
- Heavier engineering surface than WhisperX or a SaaS API.
- No first-class “name this person” product feature.

**Cost signals**

- Open-source; GPU required. No per-minute SaaS fee.

**Name attribution path:** Same post-hoc mapping as WhisperX; overkill unless you need to train/adapt on domain audio.

---

### 4. AssemblyAI

**Primary sources:** [Pricing](https://www.assemblyai.com/pricing), [Speaker identification blog/docs](https://www.assemblyai.com/blog/assemblyai-speaker-identification-diarization), [Diarization update](https://www.assemblyai.com/blog/speaker-diarization-update).

**Capabilities**

- Async STT with `speaker_labels=True` (utterance + word-level speakers).
- Hints: `speakers_expected` or `speaker_options` (min/max expected speakers). Default optimization ~up to **10** speakers; higher counts possible with options but accuracy may drop.
- **Speaker Identification** (Speech Understanding): maps labels to **names** or **roles** given `known_values` (e.g. `["Joe Rogan", "David Grusch"]` or `["Host", "Guest"]`). Can run in same request as transcription or on an existing diarized transcript.
- Experimental diarization tier for high speaker count / difficult audio.
- Streaming supports diarization; **identification is async-only**.

**Limits**

- Identification requires diarization first; names max 35 characters.
- Name/role mapping is **not** the same as biometric voiceprint matching — it relies on provided known values + model reasoning over the conversation context. Wrong guest list → wrong labels.
- Multichannel billed per channel.

**Cost signals** (async, public rate card)

| Item | ~USD / hour of audio |
| --- | --- |
| Universal-3.5 Pro | $0.21 |
| Universal-2 | $0.15 |
| Diarization (standard) | +$0.02 |
| Diarization (experimental) | +$0.065 |
| Speaker Identification | +$0.02 |
| Example: U3 Pro + diarization + ID | **~$0.25/hr** |

$50 free credits on signup (verify current promo).

**Name attribution path:** Strong **productized** fit when YouTube title/description already names host + guest(s). Feed those strings as `known_values`.

---

### 5. Deepgram

**Primary sources:** [Diarization docs](https://developers.deepgram.com/docs/diarization), [Pricing](https://deepgram.com/pricing), [community note on names](https://github.com/orgs/deepgram/discussions/475).

**Capabilities**

- Batch diarizer **v2** (`diarize_model=latest` / `v2`); streaming diarizer v1.
- Word-level `speaker` indices; batch also returns `speaker_confidence`.
- Compatible with Nova family (not Whisper Cloud models for diarization).
- Utterances + punctuation for readable speaker-labeled transcripts.

**Limits**

- **Numeric speakers only** — no built-in name/role assignment (must post-process).
- Whisper model path does not support diarization.

**Cost signals**

- Nova-3 pre-recorded on the order of **~$0.0048/min (~$0.29/hr)** PAYG (model tier dependent; confirm current pricing page).
- Speaker diarization listed as feature; streaming add-on historically **~$0.0020/min**; pre-recorded inclusion vs add-on has varied by plan presentation — re-verify before cost modeling.
- $200 free credit often advertised for new accounts.

**Name attribution path:** Cheap diarized transcript → external name mapping (metadata + LLM + optional voiceprints).

---

### 6. Google Cloud Speech-to-Text

**Primary sources:** [Multiple speakers / diarization](https://docs.cloud.google.com/speech-to-text/docs/multiple-voices), [Pricing](https://cloud.google.com/speech-to-text/pricing).

**Capabilities**

- `diarizationConfig` with `minSpeakerCount` / `maxSpeakerCount`.
- Word-level `speakerLabel` / `speaker_tag`.
- Supported on recognize + streaming (V2 features API).
- Language support is feature-gated — check [supported languages](https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages).

**Limits**

- No native person-name mapping.
- Diarization quality historically mixed on long multi-party podcasts vs specialized diarizers (validate on your audio).
- Multi-channel billing multiplies cost by channel count.

**Cost signals**

- V2 standard recognition: **$0.016/min** (~$0.96/hr) for first 500k min/month; volume tiers lower.
- Dynamic batch: **$0.003/min** (~$0.18/hr) for deferred processing.
- Diarization not listed as a separate SKU on the public pricing page (included in recognition processing when enabled).

**Name attribution path:** Post-process only.

---

### 7. Amazon Transcribe

**Primary sources:** [Partitioning speakers](https://docs.aws.amazon.com/transcribe/latest/dg/diarization.html), [Pricing](https://aws.amazon.com/transcribe/pricing/).

**Capabilities**

- Batch and streaming speaker partitioning.
- Up to **30** unique speakers (`spk_0` … `spk_29`).
- `ShowSpeakerLabels` + `MaxSpeakerLabels` in job settings.
- Official pricing text states standard pricing **includes** speaker diarization (along with custom vocabularies, language ID, etc.).

**Limits**

- Labels are indices, not names.
- S3 + IAM + job orchestration overhead for a personal pipeline.
- Regional tiered pricing; free tier 60 min/month for first 12 months.

**Cost signals**

- Official examples cite batch on the order of **$0.006/min** in some illustrations and tiered standard rates commonly cited around **$0.024/min** Tier 1 in US regions depending on product presentation — **always use the regional rate card in the console calculator**.
- Diarization included (no separate add-on SKU for basic speaker partitioning).

**Name attribution path:** Post-process only.

---

### Feature matrix: what you get for person-node work

| Capability | pyannote OSS | pyannoteAI | WhisperX | NeMo | AssemblyAI | Deepgram | Google STT | AWS Transcribe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Who spoke when | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Word-level speakers | via align | via STT orch. | ✓ | with ASR | ✓ | ✓ | ✓ | ✓ |
| Hint # of speakers | ✓ | ✓ | ✓ | config | ✓ | limited | min/max | MaxSpeakerLabels |
| Confidence on speaker | premium | ✓ | partial | research | model-dep. | batch speaker_confidence | limited | limited |
| **Map to real names** | ✗ | **voiceprint** | ✗ | ✗ | **name/role API** | ✗ | ✗ | ✗ |
| Recurring speaker re-ID across episodes | DIY embeddings | **voiceprints** | DIY | DIY | weak (per-job known_values) | DIY | DIY | DIY |
| Offline / no audio leave machine | ✓ | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |

---

## Good-enough bar for human-reviewed person nodes

For a **personal UAP research KG**, “good enough” is **not** SOTA DER on DIHARD. It is a pipeline that produces reviewable speaker-attributed text so a human can safely link claims to person nodes.

### Acceptance criteria (recommended)

1. **Stable speaker clusters within an episode**  
   Primary host and main guest(s) are usually consistent labels for most of their talk time. Occasional mid-utterance swaps are OK if rare and easy to spot.

2. **Recoverable turn boundaries**  
   Enough segment/word timestamps to jump to video and fix errors (WhisperX / API word times help).

3. **Explicit provisional mapping to names**  
   Labels attach to **candidate** person entities (from episode metadata, description, or voiceprint), not silent auto-merge into the graph.

4. **Human confirmation gate**  
   UI or checklist: “Confirm SPEAKER_00 = Leslie Kean for this episode?” before creating/updating person-node edges.

5. **Uncertainty preserved**  
   Store `speaker_label`, `attributed_person_id?`, `attribution_method`, `confidence`, `needs_review`. Unmapped speech stays as anonymous speaker, not a wrong person.

6. **Cost/time for a 2-hour interview**  
   - Local WhisperX/pyannote: tens of minutes on a consumer GPU, $0 API.  
   - AssemblyAI-class API: on the order of **~$0.50** for STT+diarization+ID on 2 hours.  
   - Human review: often 5–15 minutes if labels are mostly right; longer if crosstalk/panel chaos.

7. **Episode types that meet the bar more easily**  
   - 2-speaker interview (host + guest), clean mics, English.  
   - Known guest name in title/description.

8. **Episode types that often fail the bar without extra work**  
   - Large panels, remote callers with similar codecs, heavy overlap, music beds, non-English code-switch without model support.

### Practical quality target

| Metric (episode-level, human-estimated) | Target |
| --- | --- |
| Main guest talk-time correctly attributed after review | ≥ ~95% of guest words |
| Host vs guest confusion rate before review | Low enough that fixing takes minutes, not full re-listen |
| False person-node links after review | **~0** (hard requirement) |
| Unattributed residual speech | Allowed (e.g. audience, ads) |

Diarization error rate (DER) from academic benchmarks is a **proxy**, not the product metric. A 15–25% DER podcast can still be usable if errors concentrate in short backchannels and the human review step is mandatory.

---

## Failure modes

### A. Diarization failures

| Failure | Symptom | Impact on person nodes |
| --- | --- | --- |
| **Speaker swap / confusion** | Guest and host labels flip after similar laughter or codec change | Wrong person on long spans of claims |
| **Over-segmentation** | Too many speaker IDs for few people | Fragmented attribution; harder review |
| **Under-segmentation** | Multiple people share one label | Merged person nodes / mixed claims |
| **Overlap / crosstalk** | Simultaneous speech assigned to one speaker or dropped | Missed or misowned statements |
| **Short turns / backchannels** | “Yeah/right” assigned to wrong speaker | Usually low impact; noisy analytics |
| **Long-form drift** | Labels unstable over multi-hour audio | Cumulative misattribution without chunk consistency strategy |
| **Music / ads / SFX** | Non-speech treated as speech or fractures speakers | Garbage segments in transcript |
| **Remote vs studio timbre** | Same person on phone vs in-room split into two IDs | Duplicate provisional speakers |
| **Sortformer-style max-speaker caps** | Extra panelists collapsed into 4 labels | Systematic merge errors |

### B. Name attribution failures

| Failure | Symptom | Impact |
| --- | --- | --- |
| **Wrong known_values** | API maps labels to incorrect provided names | High-confidence wrong person nodes if auto-committed |
| **Missing guest in list** | Identification forces best available name | Silent mislabel |
| **Voiceprint false accept** | Threshold too low; absent person matched | Cross-episode contamination |
| **Voiceprint false reject** | Threshold too high; known guest stays `SPEAKER_01` | Manual fix needed (safe failure) |
| **Homophones / title confusion** | “Dr. X” vs full legal name vs handle | Duplicate entities in KG |
| **LLM mapping hallucination** | Model invents speaker names from world knowledge | Plausible but false attribution |
| **First-speaker heuristic fails** | Cold open is guest, not host | Systematic host/guest swap |

### C. Operational failures

| Failure | Impact |
| --- | --- |
| HF license / token not accepted for pyannote | Pipeline break |
| GPU OOM on large Whisper models | Need smaller model / batch size |
| API multichannel double billing | Surprise cost on stereo YouTube extracts |
| Storing raw audio in third-party cloud | Privacy/policy concern for sensitive interviews |
| No human review UI | Errors flow into graph as facts |

---

## Recommendation for personal UAP research pipeline

### Default path (best balance of quality, cost, control)

**Local: WhisperX (or Whisper + pyannote community-1) for ASR + diarization**, then **human review for name → person node**.

Rationale:

1. YouTube long-form interviews are usually **2–4 speakers**, English, offline batch — ideal for local processing.
2. pyannote **community-1** is currently the leading open diarization baseline; WhisperX already wires it with word-level alignment.
3. $0/hour API cost matters when processing many multi-hour episodes.
4. UAP research often benefits from **keeping source audio processing local** until you decide what leaves the machine.
5. Name attribution from **episode metadata** (channel = host; title/description = guest) is usually sufficient for the common 2-person interview pattern, with a 2-minute human confirm.

**Suggested pipeline sketch**

```
YouTube URL
  → download audio (yt-dlp / similar)
  → WhisperX large-v2/v3 + --diarize (+ min/max speakers if known)
  → provisional map:
        SPEAKER_00/01 ← episode metadata + optional LLM assist
  → review UI: confirm/correct speaker↔person
  → only then write person-node attributions + claim edges
```

### When to add paid identification

| Situation | Recommendation |
| --- | --- |
| Same hosts/guests recur across many episodes | **pyannoteAI voiceprints** (or local embedding gallery) for re-ID + confidence |
| One-off interview, names known from title | **AssemblyAI** speaker identification with `known_values`, or free local + manual map |
| No GPU, want minimum engineering | **AssemblyAI** (~$0.25/hr STT+diar+ID) or **Deepgram** STT+diarize + manual/LLM names |
| Already deep in AWS/GCP | Transcribe / Google STT diarization; still add your own name layer + review |
| Panels with >4 speakers, research training | NeMo **cascaded** diarizer or pyannote; avoid Sortformer-only |

### What not to do

- Do **not** auto-commit API speaker names into the KG without review.
- Do **not** treat diarization confidence as person-identity confidence.
- Do **not** start with NeMo unless you need training/customization — higher complexity than needed for v1.
- Do **not** rely on first-speaker = host without a check (cold opens, ads, clips).

### Phased adoption

1. **Phase 0:** 3–5 diverse episodes (2-person clean; remote guest; 3+ panel) through WhisperX + pyannote; measure human fix time.  
2. **Phase 1:** Metadata-based name mapping + mandatory review checkbox in the ingest tool.  
3. **Phase 2 (optional):** Voiceprint gallery for high-frequency persons (hosts, frequent guests).  
4. **Phase 3 (optional):** SaaS fallback (AssemblyAI/Deepgram) when local GPU unavailable.

### Cost sketch (illustrative)

| Path | ~2-hour interview |
| --- | --- |
| WhisperX local | Electricity/GPU only |
| AssemblyAI U3 Pro + diar + ID | ~$0.50 |
| Deepgram Nova-3 + diarization | ~$0.60–1.00 depending on add-ons |
| Google STT V2 standard | ~$1.90 |
| pyannoteAI P2 diarization only | ~€0.22 + optional ID |

For a personal corpus of tens to low hundreds of hours/year, **local WhisperX/pyannote dominates on cost**; SaaS wins on **setup speed** and **built-in name features**.

---

## Sources

### Open-source / models

1. pyannote.audio toolkit — https://github.com/pyannote/pyannote-audio  
2. pyannote speaker-diarization-community-1 — https://huggingface.co/pyannote/speaker-diarization-community-1  
3. Community-1 announcement — https://www.pyannote.ai/blog/community-1  
4. WhisperX repository — https://github.com/m-bain/whisperX  
5. WhisperX paper — https://arxiv.org/abs/2303.00747  
6. NVIDIA NeMo speaker diarization intro — https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/asr/speaker_diarization/intro.html  
7. NeMo diarization models — https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/asr/speaker_diarization/models.html  
8. NVIDIA Streaming Sortformer model card (speaker limits) — https://huggingface.co/nvidia/diar_streaming_sortformer_4spk-v2.1  

### Hosted APIs

9. pyannoteAI product — https://www.pyannote.ai/  
10. pyannoteAI pricing — https://www.pyannote.ai/pricing  
11. pyannoteAI voiceprint identification tutorial — https://docs.pyannote.ai/tutorials/identification-with-voiceprints  
12. AssemblyAI pricing — https://www.assemblyai.com/pricing  
13. AssemblyAI speaker identification & diarization — https://www.assemblyai.com/blog/assemblyai-speaker-identification-diarization  
14. AssemblyAI diarization accuracy update — https://www.assemblyai.com/blog/speaker-diarization-update  
15. Deepgram speaker diarization docs — https://developers.deepgram.com/docs/diarization  
16. Deepgram pricing — https://deepgram.com/pricing  
17. Deepgram discussion: numeric labels only — https://github.com/orgs/deepgram/discussions/475  
18. Google Cloud STT multiple speakers — https://docs.cloud.google.com/speech-to-text/docs/multiple-voices  
19. Google Cloud STT pricing — https://cloud.google.com/speech-to-text/pricing  
20. Amazon Transcribe speaker partitioning — https://docs.aws.amazon.com/transcribe/latest/dg/diarization.html  
21. Amazon Transcribe pricing — https://aws.amazon.com/transcribe/pricing/  

### Notes on source freshness

- Pricing and model SKUs change frequently; figures above reflect public pages retrieved **2026-07-18**.  
- Always re-verify rate cards and feature flags before implementation.  
- Academic DER tables are from vendor/model cards (pyannote 2025-09 benchmarks), not independent third-party audits of podcast audio.

---

## Appendix: decision cheat-sheet

```
Need names with minimal code, happy to pay ~$0.25/hr?
  → AssemblyAI (speaker_labels + speaker_identification)

Need best open diarization + full control, have GPU?
  → pyannote community-1 (+ WhisperX for ASR/timestamps)

Need biometric re-ID of recurring people?
  → pyannoteAI voiceprints (or DIY embeddings on top of pyannote)

Already on AWS/GCP and only need labels?
  → Transcribe / Google STT + your own name layer

Need to train on custom messy audio?
  → NeMo cascaded pipeline
```
