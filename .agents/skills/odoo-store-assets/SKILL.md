---
name: odoo-store-assets
description: "Prepare Odoo App Store publishing assets: cover images, description page HTML, screenshots, store-listing copy, pricing notes. Use when a task is about store assets or marketing copy for an Odoo module (covers, index.html description, screenshots, CE/EE badges, dependency pricing) - NOT for module code (see odoo-development) and NOT for recording video (see demo-video-recording)."
metadata:
  internal: true
---

# Odoo App Store publishing assets

Instructions for preparing apps.odoo.com publishing assets for firstmate
fleet modules. Store-asset work is its own discipline - it does not need the
coding standards in odoo-development. Record videos per the demo-video-recording
skill (testreel), not ad hoc. `rough-cut-axi` is optional and only for takes
with voice-over (demo-video-recording "Optional: rough-cut-axi for narrated
takes"); our demo/promo material has no audio track. Outward-facing copy
stays English-only (in-image text and subtitles), and video material must not
leak unreleased features.

## MUST-READ CORE

1. **Real renders only.** Every screenshot, cover, and GIF must come from the
   real module UI on its real version container - never mockups, never
   placeholders, never another version's screenshot.
2. **Video via testreel** (demo-video-recording skill): in-place playback on
   the store page uses `media_iframe_video` + a YouTube VIDEO_ID. mp4 stays
   local (never committed); the store page embeds YouTube, not the file.
   **The store sanitizer strips bare `<iframe>` tags**: a hand-written
   `<iframe src="https://www.youtube.com/embed/...">` in `index.html` is
   silently removed and the video never renders on apps.odoo.com. Only the
   website-builder whitelisted form survives:

   ```html
   <div class="oe_span12" style="max-width: 1080px; margin: 0 auto;">
       <div class="media_iframe_video" data-oe-expression="https://www.youtube.com/embed/VIDEO_ID"></div>
   </div>
   ```

   Living examples: the compare_merge / base_compare_widget /
   edit_on_compare_view description pages (verified rendering on the store).
   Re-skins and new modules copy this structure - never a bare iframe.
3. **Captain flow** (in data/captain.md, authoritative): new full assets go
   through lavish review and only the captain approves the merge; backfill
   changes (video link, cross-links, overlay, demo data) merge directly after
   CI stays green.

## Asset specs (measured)

- **Cover**: 2:1 (1920x960), first image in manifest `images`; brand overlay
  (module name + slogan + summary).
- **Icon**: real PNG >= 100px at `static/description/icon.png`.
- **Screenshots**: png/gif/jpeg, English, ~1800px 16:9, 5-7 shots, from the
  real UI (extract them from the recorded take's frames - method in
  demo-video-recording).
- **Description page** `static/description/index.html`: MUST be HTML (official
  CRM template structure oe_container/oe_row/oe_slogan), English, no JS, no
  external links except the canonical video.
- **CE/EE badges**: description top shows Community + Enterprise side by side
  with ok.svg + labels; copy emphasizes both editions supported.
- **Dark mode manifest**: 15/16 declare none, 17+ declare dark - the manifest
  declares dark-mode support, and the demo material must show it
  (demo-video-recording rule 10).

## Description page structure

Follow the official CRM template. The Compare-family pages share this layout:
intro slogan + CE/EE badges, pricing pill near top (extension modules), demo
video (media_iframe_video), feature screenshots, Live demo GIF, pricing &
source, Support, Compare-family cross-links.

### Pricing notes (extensions with paid dependencies)

Show the dependency chain and what the buyer pays per scenario. Use the
orange-pill + strikethrough style (see ECV/Compare-Merge pages):
- Module's own price highlighted (orange pill).
- Strikethrough shows the full stack price.
- "If you already purchased <base> for Odoo X, you pay only US$Y one-time;
  otherwise the <base> price is included."
- List each dependency and its price; Odoo adds dependency prices at checkout.
- Every price in the pricing data must carry an explicit `currency` key; when
  omitted, the price defaults to EUR.

### Cross-links (Compare-family modules)

Every Compare-family module's description page links to the others, per
version: base_compare_widget (Compare Everything) <-> edit_on_compare_view
(Compare & Resolve) <-> compare_merge (Compare & Merge). Add a short "who this
builds on / what extends this" intro line + a Compare-family section near the
end with each module's apps.odoo.com URL for the page's own version.

## Compliance (must hold)

- No vendor lock-in (no activation keys; customers own data).
- No Enterprise subscription bypass code.
- External services clearly advertised.
- App price <= price on other platforms (Odoo takes 30%).
- Listing score factors: icon, cover, license, rating >= 3, HTML description.
- Not a clone of Enterprise modules.

## Registering a listing (registration and repo access)

- Registration = repo + version branch named exactly the Odoo version (`20.0`, ...), next to `main`.
- For the authoritative branch/release model (dev line vs frozen version branches), see
  odoo-development's "Branch and release discipline".
- Private repos need `online-odoo` ("Odoo Online", NOT `odoo-online`) as a collaborator there:
  easiest is `gh api -X PUT repos/<owner>/<repo>/collaborators/online-odoo`; it
  cannot grant read, so without `permission` it gives **write**, enough to register.
- Strict read-only is the only case for the web UI (Settings -> Collaborators -> Add people,
  keep default **Read**); the API returns `422 Cannot assign online-odoo permission of read`.
  Undo a mistake with `gh api -X DELETE repos/<owner>/<repo>/invitations/<id>`.
- A public repo needs no grant; publishing needs the portal account, YouTube upload, payout info.

## Recording definitions & assets live outside the module

Cover scripts and testreel JSON definitions live in the repo root
`assets/record/` - never inside the Odoo module directory (testreel workflow:
demo-video-recording). Recorded mp4s stay local (MUST-READ #2); GIFs and
screenshots small enough to commit may ship inside `static/description/`.
