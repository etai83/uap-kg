# YouTube ingestion options for curated channels

**Issue:** #12 — YouTube ingestion options for curated channels  
**Date:** 2026-07-18  
**Scope:** Personal research tool (not a redistribution product)  
**Disclaimer:** This document summarizes what primary YouTube/Google sources state. It is **not legal advice**. Policy text can change; re-check linked sources before implementation.

---

## Question

What are the viable, Terms-of-Service–aware options for obtaining **video metadata + transcripts** (and optionally **audio**) from a **fixed set of curated YouTube channels** for a personal research / knowledge-graph tool?

---

## Options table

| Option | What you get | Official path? | Works for third-party channels? | ToS posture (per primary sources) | Practical notes |
| --- | --- | --- | --- | --- | --- |
| **A. YouTube Data API v3 — metadata only** | Channel info, upload lists, titles, descriptions, tags, duration, stats, thumbnails, `contentDetails.caption` (presence), embed HTML, etc. | Yes | Yes (public data with API key) | Aligns with API Services ToS + Developer Policies when used as documented | Preferred path for cataloging curated channels |
| **B. YouTube Data API v3 — Captions list/download** | Caption track metadata + actual caption file (SRT/TTML/etc. via `tfmt`) | Yes | **No** for others’ videos without edit rights | Allowed only when authorized; download requires permission to **edit** the video | Designed for owners/partners managing their own captions |
| **C. In-product viewer transcript UI** | Human-readable transcript while watching | Yes (product feature) | Yes if captions exist | Viewing is personal use as enabled by the Service; **bulk automation is not** | Help Center: “Show transcript” for videos with captions |
| **D. Creator / rights-holder export or OAuth** | Full captions via Studio download or via Captions API with owner OAuth | Yes | Only with cooperation | Strongest compliance path for third-party transcript text | Manual Studio download or app authorized by channel owner |
| **E. yt-dlp / scrapers / timedtext clients** | Metadata, subtitles (manual + auto), audio, video | No (third-party) | Often works technically | Conflicts with user ToS automation/download rules and API Developer Policies (scraping, AV download, separate audio) | Documented here only as a **capability** reference, not a ToS-compliant recommendation |
| **F. Audio download + ASR (self or cloud)** | Homegrown transcript from isolated audio | No for acquisition | Depends on acquisition | Separating/downloading audio is explicitly discouraged/prohibited under API policies and download restrictions under user ToS | Even personal ASR inherits how audio was obtained |
| **G. YouTube Premium offline** | Offline viewing of videos you choose | Yes (product) | For personal viewing | Product feature; Developer Policies say do not allow offline outside YT Premium experience | Not an ingestion/API pipeline for a KG |

---

## Trade-offs

### 1. Metadata (high confidence, official)

**Mechanism (Data API):**

1. Resolve channel: `channels.list` with `id`, `forHandle`, or `forUsername`; request `part=contentDetails,snippet,statistics` as needed.  
   - Source: [Channels: list](https://developers.google.com/youtube/v3/docs/channels/list), [Channels resource](https://developers.google.com/youtube/v3/docs/channels) (`contentDetails.relatedPlaylists.uploads`).
2. Enumerate uploads: `playlistItems.list` with the channel’s uploads playlist ID.  
   - Source: [PlaylistItems: list](https://developers.google.com/youtube/v3/docs/playlistItems/list) (quota cost 1 unit).
3. Enrich videos: `videos.list` with video IDs; parts such as `snippet`, `contentDetails`, `statistics`, `status`, `topicDetails`.  
   - Source: [Videos: list](https://developers.google.com/youtube/v3/docs/videos/list), [Videos resource](https://developers.google.com/youtube/v3/docs/videos).
4. Caption **presence** (not text): `contentDetails.caption` on the video resource indicates whether captions are available.  
   - Source: [Videos resource](https://developers.google.com/youtube/v3/docs/videos) (`contentDetails.caption`).

**Quota:** Default project allocation is limited (order of 10,000 units/day for most endpoints; read list methods are typically 1 unit). Documented defaults and costs: [Data API Overview — Quota usage](https://developers.google.com/youtube/v3/getting-started#quota). Extensions require compliance audit: [API form](https://support.google.com/youtube/contact/yt_api_form).

**Storage (API Data):** Developer Policies allow temporary storage of **non-authorized** API data for as long as needed for the API Client’s purposes, **but not longer than 30 calendar days**, after which data must be **deleted or refreshed**. Statistics retrieved without channel-owner authorization fall under this non-authorized regime.  
- Source: [Developer Policies § III.E.4](https://developers.google.com/youtube/terms/developer-policies#e.-handling-youtube-data-and-content).

**Trade-off:** Excellent for a curated-channel **catalog and graph of metadata**. Does **not** deliver transcript text for others’ videos.

### 2. Official captions API (owner-centric)

**What exists:**

- `captions.list` — lists tracks for a `videoId`; response does **not** include caption text. Requires OAuth (`youtube.force-ssl` or `youtubepartner`). Quota: **50 units**.  
  - Source: [Captions: list](https://developers.google.com/youtube/v3/docs/captions/list), [Captions resource](https://developers.google.com/youtube/v3/docs/captions).
- `captions.download` — returns the caption track as a binary file; optional `tfmt` / `tlang`. Quota: **200 units**.  
  - **Official constraint:** “This method requires the user to have permission to **edit** the video.”  
  - Source: [Captions: download](https://developers.google.com/youtube/v3/docs/captions/download).

**Trade-off:** First-party and policy-aligned for **your own** channels or channels that **authorize your app** as editor/partner. **Not** a public-transcript API for arbitrary curated creators.

### 3. Product UI transcripts (human-scale)

YouTube Help documents that viewers can open **Show transcript** for videos that have captions, read along, and jump by line.  
- Source: [View video transcripts](https://support.google.com/youtube/answer/15930243).

Creators manage captions (including download of **their** subtitle files) in YouTube Studio.  
- Sources: [Add subtitles & captions](https://support.google.com/youtube/answer/2734796), [Edit or remove captions](https://support.google.com/youtube/answer/2734705), [Use automatic captioning](https://support.google.com/youtube/answer/6373554).

**Trade-off:** Compliant for personal viewing/use of Service features; **not** designed as a bulk export API. Automating the UI or undocumented endpoints runs into automation/scraping rules below.

### 4. Prohibitions most relevant to “transcripts + audio” pipelines

From **YouTube Terms of Service** (consumer Service):

- Access/use Content only as specifically permitted by the Service, with prior written permission, or as permitted by applicable law; includes restrictions on **download**, distribute, alter, etc.  
- **No automated means** (robots, botnets, scrapers) except public search engines per `robots.txt`, YouTube’s prior written permission, or applicable law.  
- Personal, non-commercial viewing/listening; not for uses that treat the Service as a content warehouse for other products.  
- Source: [YouTube Terms of Service](https://www.youtube.com/t/terms) (“Permissions and Restrictions”).

From **YouTube API Services Terms of Service**:

- No rights to reproduce or distribute audiovisual content except through the API Services **in accordance with the Agreement**.  
- On termination/suspension, delete API Data in your possession.  
- Source: [API Services Terms of Service](https://developers.google.com/youtube/terms/api-services-terms-of-service) (§§ 16.3, 24.3).

From **Developer Policies**:

| Topic | Rule (paraphrase of policy text) | Source |
| --- | --- | --- |
| Audiovisual download/cache | Must not download, import, backup, cache, or store copies of YouTube audiovisual content without prior written approval; must not make content available for offline playback | [§ III.E.1](https://developers.google.com/youtube/terms/developer-policies#e.-handling-youtube-data-and-content) |
| Scraping | Must not scrape YouTube/Google Applications or obtain scraped YouTube data/content | [§ III.E.6](https://developers.google.com/youtube/terms/developer-policies#e.-handling-youtube-data-and-content) |
| Separate audio/video | Must not separate, isolate, or modify audio or video components of AV content made available via API Services; must not promote those components separately | [§ III.I](https://developers.google.com/youtube/terms/developer-policies#i.-additional-prohibitions) |
| Non-API tech for API Data / AV | Must not use any technology other than YouTube API Services to access or retrieve API Data, including any portion of YouTube audiovisual content | [§ III.I.14](https://developers.google.com/youtube/terms/developer-policies#i.-additional-prohibitions) |
| Undocumented services | Must not use undocumented APIs without express permission; only authorized documentation means | [§ III.D.7](https://developers.google.com/youtube/terms/developer-policies#d.-accessing-youtube-api-services) |
| Offline / audio extract (guidance) | Do not allow download for offline outside YT Premium; do not offer download/separate audio tracks | [Developer Policies Guide](https://developers.google.com/youtube/terms/developer-policies-guide) |

**Implication for option E (yt-dlp etc.):**  
yt-dlp is a third-party CLI that can download media and write subtitles (`--write-subs`, auto-subs, `--skip-download`, metadata JSON, etc.). Capability summary: [yt-dlp README](https://github.com/yt-dlp/yt-dlp/blob/master/README.md). That capability does **not** create a license under YouTube’s ToS/API policies. For a tool that also uses the official API, Developer Policies further require not encouraging/obtaining scraped data and not using non-API tech for AV/API Data.

**Implication for option F:** ASR after isolating audio conflicts with the same download/separate-audio rules when audio comes from YouTube outside permitted product features.

### 5. Personal research tool vs redistribution product

| Factor | Personal research tool | Redistribution / multi-user product |
| --- | --- | --- |
| API Client privacy/ToS links | Still apply if you use YouTube API Services | Full III.A privacy policy, branding, RMF, etc. |
| Scraping / AV download | Still restricted by user ToS and (if using APIs) Developer Policies | Same + higher enforcement/audit risk |
| 30-day API data refresh | Applies to stored API Data | Same |
| Caption ownership path | Can pursue per-channel cooperation | Needs systematic rights workflow |
| “Personal non-commercial use” language | Helps for **viewing** via the Service; does **not** clearly authorize bulk download or scraper-based corpus building | N/A |

There is **no** public Google/YouTube “research corpus API” for third-party video transcripts documented in the Data API reference.

---

## Recommendation for a personal research tool

**Primary path (implement first): official metadata ingestion only.**

1. Google Cloud project + YouTube Data API v3 enabled; API key for public read; avoid unnecessary OAuth scopes.  
   - [Getting started](https://developers.google.com/youtube/v3/getting-started), [Registering an application](https://developers.google.com/youtube/registering_an_application).
2. Curated channel allowlist → `channels.list` → uploads playlist → paginated `playlistItems.list` → batched `videos.list`.
3. Persist **stable identifiers** (channelId, videoId, publishedAt, title, description, duration, tags, caption-available flag, URLs) and treat volatile stats as cache with **≤30-day refresh/delete** per Developer Policies III.E.4.
4. Link out to YouTube for playback (embed/player or open on YouTube); do not store AV copies.
5. Respect quota; prefer `playlistItems` over expensive `search.list` for “all videos of channel.”

**Transcripts (tiered, ToS-aware):**

| Priority | Approach | When |
| --- | --- | --- |
| 1 | **Owner cooperation** — channel authorizes OAuth app *or* exports captions from Studio | Ideal for high-value curated sources |
| 2 | **Manual / semi-manual** — use official “Show transcript” or creator-provided text for sparse, high-value videos | Small N, human-in-the-loop research |
| 3 | **Description / chapters / comments via Data API** as weak text proxies | When captions unavailable and owner path not open |
| 4 | **Do not build** automated yt-dlp/timedtext/scraper pipelines as the default ingestion layer for this project if the goal is ToS-aware compliance | Technical capability ≠ policy permission |

**Audio:** Treat as **out of scope** for automated ingestion unless you have **prior written approval** from YouTube and/or clear rights from the content owner. Prefer watching/listening in-product; do not store isolated audio tracks from YouTube for ASR as a standing architecture.

**Architecture sketch (compliant-leaning):**

```text
Curated channel IDs
        │
        ▼
 YouTube Data API v3
 (channels → playlistItems → videos)
        │
        ▼
 Local KG: metadata + links + caption_available
        │
        ├── optional: owner-OAuth captions.download / Studio SRT
        └── optional: human-curated transcript notes
        │
        ▼
 Playback: YouTube embed / open on YouTube (no AV archive)
```

---

## Open risks

1. **No third-party caption download in Data API** — `captions.download` requires edit permission; there is no documented public transcript download method.  
2. **30-day storage rule** for non-authorized API Data — long-lived KG mirrors of API fields may need periodic refresh/delete design; exact treatment of purely “public” facts vs API-derived stores is a policy interpretation risk (not legal advice).  
3. **Quota ceilings** — large backfills of many channels can exhaust daily units; extensions need audit.  
4. **Policy change / enforcement** — YouTube may modify ToS/API policies; scrapers break technically and legally independently.  
5. **Copyright of speech/content** — even when captions are viewable, building a durable corpus may raise rights issues under copyright law beyond YouTube’s contract terms (jurisdiction-specific; not covered here).  
6. **Using both API and scrapers** — Developer Policies prohibit obtaining scraped YouTube data and using non-API tech for API Data/AV; hybrid designs increase compliance risk.  
7. **“Personal use” is not a bulk-download license** — user ToS personal viewing language does not clearly authorize automated archive building.  
8. **Auto-captions quality** — even when obtained via owner tools, ASR captions may be inaccurate ([automatic captioning help](https://support.google.com/youtube/answer/6373554)).  
9. **Partner/MCN paths** (`youtubepartner` scope) — may unlock more for content owners; not available to unrelated researchers by default.  
10. **Termination cleanup** — API ToS requires deletion of API Data on agreement termination.

---

## Sources

### Primary — Google / YouTube

| Document | URL |
| --- | --- |
| YouTube Terms of Service | https://www.youtube.com/t/terms |
| YouTube API Services Terms of Service | https://developers.google.com/youtube/terms/api-services-terms-of-service |
| YouTube API Services — Developer Policies | https://developers.google.com/youtube/terms/developer-policies |
| Complying with YouTube’s Developer Policies (examples) | https://developers.google.com/youtube/terms/developer-policies-guide |
| YouTube Data API Overview (quota, parts) | https://developers.google.com/youtube/v3/getting-started |
| API Reference index | https://developers.google.com/youtube/v3/docs |
| Channels resource / list | https://developers.google.com/youtube/v3/docs/channels · https://developers.google.com/youtube/v3/docs/channels/list |
| PlaylistItems: list | https://developers.google.com/youtube/v3/docs/playlistItems/list |
| Videos resource / list | https://developers.google.com/youtube/v3/docs/videos · https://developers.google.com/youtube/v3/docs/videos/list |
| Captions resource / list / download | https://developers.google.com/youtube/v3/docs/captions · https://developers.google.com/youtube/v3/docs/captions/list · https://developers.google.com/youtube/v3/docs/captions/download |
| View video transcripts (Help) | https://support.google.com/youtube/answer/15930243 |
| Add / edit captions; automatic captioning (Help) | https://support.google.com/youtube/answer/2734796 · https://support.google.com/youtube/answer/2734705 · https://support.google.com/youtube/answer/6373554 |
| API Compliance / quota form | https://support.google.com/youtube/contact/yt_api_form |

### Secondary — tool capabilities only (not legal authority)

| Document | URL | Use in this memo |
| --- | --- | --- |
| yt-dlp README | https://github.com/yt-dlp/yt-dlp/blob/master/README.md | Documents technical ability to fetch metadata, subs, and media; **not** YouTube permission |

---

## Revision

| Date | Change |
| --- | --- |
| 2026-07-18 | Initial research for issue #12 from primary Google/YouTube sources |
