---
name: themis-series-layout
description: "Use when arranging Shine Themis series modules, deciding the repository or branch structure for a themis release, or publishing to apps.odoo.com. Encodes the captain's module-arrangement rules: one shared repository for all series, one self-contained module per series (each vendors its own engine, zero cross-module dependencies, depends on 'web' only), version lines as branches of that single repository so one store registration publishes every series' apps, mutual-exclusion declarations, store-fact-driven manifest CI, and the add-a-new-series workflow. For sourcing a theme's media see themis-theme-sourcing; this skill owns only the arrangement and publishing."
metadata:
  internal: true
---

# Themis series module arrangement

**One repository, many self-contained modules: every module vendors its own engine,
so one apps.odoo.com listing is one independent app; version lines are branches of
that single repository.** (Captain, 2026-09-23: all series share one library - he
registers the library's versions and thereby publishes many series' apps at once.)

## 1. The publishing unit is one repository

- All series live in **one repository: `shine-themis-series`**.
- **Each version line is a branch** of that repository: `main` (the dev line,
  currently tracking Odoo 20.0) plus frozen release branches `17.0`, `18.0`,
  `19.0`, `20.0`; ephemeral `fm/*` work branches come and go.
- On apps.odoo.com **each version branch is registered once**, and **every module in
  the repository publishes together** under that registration. Registering one new
  version of the library releases all series' apps simultaneously - that is the
  reason for the shared library.
- **Never open a new repository for a new series.**
- The generic Odoo branch/release discipline (dev line vs frozen version branches)
  is in odoo-development's "Branch and release discipline"; this section only
  records how that model is instantiated in the themis library.

## 2. Every module is self-contained

- **The engine is copied into every module.** Engine duplication inside the
  repository is intentional - do not extract a shared core module.
- **Zero dependencies between modules** and **no third-party modules**:
  `depends: ['web']` only.
- Why: otherwise one apps.odoo.com listing could not be an independent app. The
  store ships each customer only the zip of the module he bought; any dependency the
  customer does not have is a broken install (section 6).
- Historical alternative, recorded and rejected: a shared base module that the
  published listings depend on ("depending on an app that is itself not listed")
  does not work on the store. Rejected - do not revive it.

## 3. What each module carries

- Only its own themes. Per theme: **one background asset** (a 4K video or a single
  4K image) and **one palette sampled from that asset**.
- Plus the **Corporate light/dark pair** - the module ships its own Corporate
  themes and must not depend on the free edition for them.
- Media sourcing, licences, provenance, and the size budget are governed by
  `themis-theme-sourcing`; that skill does not duplicate this one's rules either.

## 4. Engine source of truth and drift control

- The authoritative engine implementation lives in the private workbench
  `shine-themis-pro`.
- Port the engine **once per supported version inside pro**, then **copy it into
  this repository per branch** - branch-to-branch, no per-series fan-out; every
  series module on a branch carries the same engine.
- The repo-level `tools/check-engine-drift.sh` compares every module's vendored
  engine against pro's corresponding branch (one repo-level check, not per-module).
  **Source unreachable: skip and print a
  prominent warning. Source reachable: the copies must be identical** - any diff
  fails the check.

## 5. Mutual exclusion

- All series share the same model (`shine.theme.preset`), so two series can never be
  installed side by side - coexistence is technically impossible, not merely
  discouraged.
- Every module declares exclusion against: the free edition `shine_themis`, the
  workbench `shine_themis_pro`, and every other series module in this repository.
- Store copy must state it plainly: installing another series replaces this one -
  each listing carries a "choose one series" note. (This is a deliverable reminder
  for the captain's backend work.)

## 6. Store facts that force this arrangement

- **The store indexes by repository.** A manifest error in any single module can
  take the whole repository's modules off the store. Therefore CI must run a
  **manifest health check** that parses every `*/__manifest__.py` and verifies:
  required keys present; `depends` contains only `web`; `version` prefix matches the
  branch's Odoo version.
- **One listing = one module**, and the customer's zip contains only the module he
  bought; he must satisfy dependencies himself. That is exactly why cross-module
  dependencies are forbidden (section 2).
- Manifest facts: `license: 'OPL-1'`; `price` and `currency` must always be set
  together, never one without the other.

## 7. Naming

- Repository: `shine-themis-series`.
- Module: `shine_themis_<series>`, e.g. `shine_themis_quiet`.
- Series names are emotion words: quiet / vivid / serene / cozy.

## 8. Adding a new series

1. Prototype the themes in pro first.
2. Define the theme set and grouping: light/dark and colour-family balance across
   the portfolio, each group roughly 5 light + 4 dark, every group includes
   Corporate.
3. Create the self-contained module in the shared repository, copying the engine
   from pro's corresponding branch (section 4).
4. Add the CI entries: manifest health check coverage and the drift check.
5. Verify on a desktop lane - real picker, real home screen.
6. Publish under the existing per-branch registrations of the shared library.
