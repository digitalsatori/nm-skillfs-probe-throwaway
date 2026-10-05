---
name: themis-theme-sourcing
description: "Use when sourcing, licensing, or composing media for a Shine Themis theme (background video + image set + palette): the channel APIs (Wikimedia / Pixabay / Pexels / Unsplash, API-only fetch), the captain-driven batch-entry workflow, licence rules and the `meta` provenance contract, the per-theme media standard and size budget, the cinemagraph recipe, display rules, the pro preset wiring, and pre-release verification. For module arrangement and publishing see themis-series-layout."
metadata:
  internal: true
---

# Shine Themis theme sourcing

One theme = **one real-motion background video** + **at least five 4K images in the
same colour family**, plus a palette sampled from that media. The "1 video + 5 images"
shape is the **floor**, not the ceiling: a theme may carry **6-10 assets** in total;
the only hard cap is the module size budget (section 9). A themed **pack** (version
library) is five such themes sharing one soft theme, named after an emotion word,
e.g. `shine-themis-pro-calm` - see the series model in
`references/pro-pack-mechanics.md` (loaded on demand).
**Scope: this standard governs the pro-family theme packs.** Series modules in
`shine-themis-series` carry ONE background resource per theme (video, else one
high-resolution image - captain call 2026-09-23); see themis-series-layout
section 3.

## 1. Resource channels

Keys live in the firstmate home's gitignored `.env` (never in a repo, never in a
skill, never in a commit). Search the environment, do not hard-code values.

| Channel | Gives | Key / env var |
|---|---|---|
| Wikimedia Commons | public-domain / CC0 / CC BY video and stills | none |
| Pixabay | 4K video + stills | `PIXABAY_API_KEY` |
| Pexels | 4K video, including long clips | `PEXELS_API_KEY` |
| Unsplash | very high resolution stills (up to 6K) | `UNSPLASH_ACCESS_KEY` |

Helper scripts in `scripts/` (copy them next to the work, they have no install step):

- `scripts/media-search.py` - query one or more channels, filter by usable licence and
  minimum width, emit a candidate table with ids/urls/licences.
- `scripts/media-fetch.py` - download a chosen candidate (with a size cap) and dump a
  probe frame per candidate into one contact sheet for visual review.
- `scripts/cinemagraph.sh` - turn one clip into a seamless local-motion background.

**API only.** The crew never opens or scrapes the providers' website pages; every
lookup and download goes through the channel APIs (see the batch-entry workflow,
section 3) - site pages risk triggering the sites' real-person verification and
pollute the shared egress IP.

## 2. Licence rules

1. Prefer, in order: **public domain / CC0** > **CC BY** > channel licences below.
   Never CC BY-SA for a paid module (share-alike would infect the product).
2. Channel licences, verified from the published terms:
   - **Pixabay Content License**: free commercial use, modification allowed, attribution
     not required; must not be resold "standalone" (unmodified) and content containing
     recognised trademarks must not be used commercially.
   - **Pexels License**: free commercial use, modification allowed, no attribution
     required; must not be resold unmodified, must not be re-distributed on a stock or
     wallpaper platform, and the terms explicitly allow use in "a template you sell".
   - **Unsplash License**: free commercial use; API use requires crediting the
     photographer with a link.
3. We always transform (crop, mask, loop, recolour, compose) - that is what keeps the
   "standalone resale" restriction satisfied. Never ship a raw download.
4. Record provenance in the preset `meta` blob, always: `source` (page URL), `author`,
   `license` (exact name), and `ai` when the asset is AI-generated. Attribution that a
   licence requires (CC BY, Unsplash) goes in the same blob.
5. AI-generated footage is acceptable and often the cleanest rights-wise; say so in
   `meta` rather than hiding it.
6. Only sources with an explicit commercial-use licence are collected - the section 1
   channels (Pixabay / Pexels / Unsplash via API, Wikimedia public domain).
   **Pinterest and other social platforms are inspiration only** - never a source,
   never recorded in `meta`.

## 3. Batch-entry workflow (captain-driven batches)

Sourcing runs in batches, driven by the captain's own browsing session:

1. The captain browses the licensed sites and drops **3-6 candidate links at a time**
   with the crew.
2. The crew resolves every link **through the channel API only** (`media-search.py` /
   `media-fetch.py` by id or URL). Never touch the website pages themselves (section 1).
3. **Auto-filter**, reject without human review: source width **< 3840**; any HUD,
   watermark, or title card; video motion **< 3/255** (measure: downscale two frames
   to 96x54 and take the mean absolute pixel difference on the 0-255 scale).
4. **Group by colour family, not by subject.** Subject matter is unrestricted; colour
   is what must match. Each theme = one video + five same-colour-family images,
   all >= 3840 wide at source.
5. Sample the palette from the grouped media and match the system colours to it
   (section 6).
6. Merge the finished candidates onto **one switchable test bench** (a scratch lane
   with all candidates installed side by side, switchable from the picker) and hand it
   to the captain for **batch review**. Nothing merges into a pack until he signs off
   on the batch.

## 4. Video requirement

A theme's background video is **original, real motion** - a living photograph comes
from what genuinely moves in the scene (water, drifting cloud/mist, leaves, smoke,
distant traffic), not from freezing a frame.

- **Ship at 2560x1440.** Never master at 3840 - downscale a 4K source instead.
- **<= 6 MB per video**, **8-12 seconds** long.
- **Seamless loop via a head-to-tail crossfade** of the whole real clip. Do not
  ping-pong a full-motion video - reversed motion reads as wrong. (Ping-pong stays
  inside the optional cinemagraph recipe, section 7.)
- **Motion amount >= 3/255** (the section 3 measurement) - the frame must visibly move.
- No HUDs, watermarks, title cards, burned-in graphics, or people in frame. Check
  every candidate by eye at full size before building.

Cinemagraphs (frozen frame + one local motion) are **not** the default; they survive
only as the optional "still" tier of a series' motion axis (three-axis model in
`references/pro-pack-mechanics.md`). The full recipe and its pitfalls live in
section 7.

Small deliberate experiments beyond this shape are allowed **when they are labelled as
experiments**, shown on the test machine, and only promoted to production after the
captain confirms.

## 5. Image requirement

Images rotate as the theme's wallpaper set, within the 6-10 asset total and the
size budget of section 9 (the 1-video + 5-image floor is defined in the intro).

- **>= 3840 px wide (4K)** and **<= 350 KB each** after encoding.
- **Same colour family as the theme's video**: the colour temperature of every image
  must sit close to the video's - never file far-apart colour temperatures into one
  theme. Subject is unrestricted.
- No watermarks, no recognisable brands, **no people in frame**.
- Provenance per asset goes into the preset `meta` blob (section 2, point 4):
  source page, author, licence.

## 6. Palette

Derive the palette **from the theme's own media group** (video frames + stills
together, so video and images share one palette), do not invent it: sample the media
(a ffmpeg one-pixel or palette read is enough), then set canvas/surfaces from the
dominant darks or lights and accent from the most saturated subject colour, and match
the system colours to the sample. The module enforces WCAG AA contrast floors (4.5
text, 3.0 action pair) at write time - let it fail and fix the values instead of
guessing.

## 7. Composition recipe (cinemagraph - optional "still" motion tier)

Use this only when a series' motion axis explicitly picks the **still** tier
(three-axis model: `references/pro-pack-mechanics.md`); the default theme video is
original real motion (section 4).

`scripts/cinemagraph.sh <clip> <out-prefix> [start-seconds]`:

1. Take a window of the clip, scale to the target width.
2. Freeze the frame at `start + 1s` as the static base.
3. Build a motion mask from frame differences (`tblend` + threshold + `tmix` + small
   blur). Blur only enough to feather the motion boundary.
4. Composite base + clip through the mask. **Use `alphamerge` + `overlay`, never
   `maskedmerge`** - `maskedmerge` collapses RGB input to luma and silently ships a
   greyscale theme.
5. Ping-pong: encode forward, encode `reverse`, concat with `-c copy`.
6. Stream-copy the concat; do not re-encode the final file.

The stronger variant, use it when the stills allow: take the **base frame from a
high-resolution still** (Unsplash 6K or a Pixabay/Unsplash still of the same scene) and
composite only the motion region from the clip on top. That keeps full detail in the
frame's 92-99% that never moves.

## 8. Display rules: scrim and scroll unfurl

- **Scrim (shade overlay): default 0.** No full-frame darkening layer. Fallback, only
  if legibility genuinely fails: a **local** treatment on the text strip / app name,
  never a full-bleed scrim. Nothing is added before the captain signs off on the
  approach.
- **Scroll unfurl has exactly one trigger: confirming a theme in the picker with
  Enter.** A hard refresh, a plain return to Home, Esc, previews, `enabled: false`,
  and reduced-motion **never** play the unfurl.
- Carousel display behaviour (pro packs) lives in
  `references/pro-pack-mechanics.md`.

## 9. Size budget

- **<= 25 MB per module.** That is the hard "Import module" limit on Odoo.sh and Odoo
  Online (official theme docs allow a zip < 50 MB, but the import path is the binding
  constraint; git installs are unlimited).
- **Target ~8 MB per theme set** (video + images), leaving headroom for the module's
  other themes.
- Every release report **must state actual sizes**: video and image subtotals plus the
  module total.
- When over budget, cut in this order: lower the encode bitrate -> step the
  resolution down -> drop assets.

## Pro-pack mechanics (loaded on demand)

Pro-repo shipping mechanics (preset XML, sync hooks, migrations, marketplace card
image), the pack layout, the three-axis series model, and carousel display
behaviour live in `references/pro-pack-mechanics.md` - load it when working on a
pro pack release.

## 10. Verification before anything reaches production

1. Boot a scratch lane on a free port (8030-8094 band) with a fresh database and the
   pro module; confirm the theme appears and the video/rotation actually play at the
   real entry point (open the picker, select the theme, look at the home screen).
   Keep the lane's filestore paired with its database (rule owned by
   odoo-environment).
2. Run the module tests on three paths, all green: fresh install, upgrade from an old
   release, and **upgrade from the currently published version**.
3. Re-run the upgrade twice and confirm the media rows do not double.
4. Show the captain the scratch lane (or the batch test bench of section 3); only
   after his confirmation does the theme go into the production theme repository /
   pack.

## 11. Portfolio balance

Balance is judged across the whole released set, not one theme at a time. Before
sourcing media for a new theme or pack, check all three axes:

- **Shade**: light and dark themes in roughly a 1:1 ratio - decide it: once the
  released counts differ by more than 2, the next theme must be the minority
  shade. A run of all-dark releases fails this section even when each theme is
  individually good.
- **Colour family**: rotate blue / teal / green / warm gold / orange-red / purple /
  neutral grey. Never ship the same colour family twice in a row.
- **Subject**: rotate snow mountain / sea / forest / fields / city / desert. This is
  a portfolio-level slot heuristic only - within one theme, media are grouped by
  colour family and subject is unrestricted (sections 3 and 5).

Look at the portfolio first, then pick media: the next theme fills the biggest open
slot, it is not one more "nice repeat" of what is already covered. Every release
report states which slot this set fills, e.g. "fills dark + green".

Current inventory and gap snapshot (refresh with every release):

- dark: warm orange / deep blue / deep blue-purple / dark amber
- light: warm neutral / warm gold
- Open gaps: **light + cool** (ice blue / mist white), **dark + green** (deep
  forest), **light + neutral grey** (minimalist); purple exists only on the dark side.
