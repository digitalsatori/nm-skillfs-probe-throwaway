# Pro-pack mechanics (reference, loaded on demand)

Owned by the themis-theme-sourcing skill; loaded when working on a **pro-family
theme pack** (e.g. `shine-themis-pro-calm`). The main SKILL.md body keeps only a
pointer here. Precedent: `odoo-development/references/pitfalls.md`.

## Shipping mechanics (pro repo)

- Preset data lives in `shine_themis_pro/data/presets_pro.xml`; media under
  `shine_themis_pro/static/backgrounds/<key>/` (one `.mp4` + the stills).
- Media is attached by a sync hook: add `KEY_PRESET_XMLID`, `KEY_BACKGROUNDS_DIR`,
  `KEY_SYNCED_KEY` constants plus a `sync_<key>_backgrounds(env)` wrapper, and call it
  from `sync_builtin_backgrounds(env)`.
- Post-init hooks run on INSTALL only. Any media change must also ship a
  `migrations/<new-version>/post-migration.py` calling `sync_builtin_backgrounds(env)`
  **and** bump the manifest version - Odoo runs migrations only on a version change, so
  a media swap with the same version silently does nothing.
- Sync keys are per preset and per version; repeated upgrades must not duplicate rows.
- Preset fields that matter: `key`, `name`, `sequence`, `built_in`, `native_shade`,
  `modes` (single-mode theme = one picker card; `both` = one card per shade), a
  `palette` JSON with a `light` and/or `dark` block, and the `meta` blob.
- Store assets: the marketplace card image is the first file in manifest `images`
  whose name ends in `_screenshot` - a landscape hero must not carry that suffix.

## Display rules: carousel (pro packs)

- **Carousel**: when the user picks carousel mode, the video joins the unified
  playlist (video -> image 1..N -> video); the video's slot lasts
  `max(carousel interval, video duration)`. In non-carousel mode the video remains
  the primary background.

## Pack layout and the three-axis series model

A pack (series) is a pro-family repository (or branch strategy) grouping five themes
of one **soft theme** - there are no hard requirements beyond the per-theme sections.
The series is defined on three axes:

- **Emotion**: melancholy / serene / mysterious / grand / joyful / romantic / ...
- **Colour temperature x brightness**: cool / warm / neutral x dark / light / mixed.
- **Motion degree**: still (the cinemagraph tier of SKILL.md section 7) / subtle /
  clearly flowing.

Name the pack after its emotion word, e.g. `shine-themis-pro-calm` (quiet, misty,
low-contrast mornings) or `shine-themis-pro-season`. **One theme of the five may
cross** its series' axis ranges - a deliberate outlier keeps the pack from feeling
stamped.

Every series keeps a **series card** (one page in the pack): a one-sentence emotion
declaration, the three-axis ranges, and the outlier allowance. Automatic scoring and
release reports check themes against the card, not against a rigid template.

Each theme in a pack follows the per-theme sections of SKILL.md unchanged (media,
palette, size budget, verification, portfolio balance); the pack only fixes the soft
theme, so palettes, motion amount, and still selection stay coherent across its five
themes.

Module arrangement and publishing for a series (which repository, which branches,
self-contained modules, apps.odoo.com listings) are governed by the
`themis-series-layout` skill - see it; those rules are not duplicated here.
