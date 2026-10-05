---
name: odoo-development
description: "Develop, customize, or debug Odoo modules. Use when creating a new Odoo extension, fixing an Odoo bug, customizing Odoo behavior, migrating a module between Odoo versions, investigating Odoo framework APIs, or writing Odoo tests. Covers version awareness, research discipline, coding standards, and the verification pipeline."
metadata:
  internal: true
---

# Odoo module development

Instructions for an agent writing Odoo module code (models, views, business
logic, tests) inside the firstmate fleet.

- Environment setup / Docker compose / mounting / smoke tests → **odoo-environment** skill.
- Store assets (cover, description, screenshots, videos) → **odoo-store-assets** + demo-video-recording.

## MUST-READ CORE (every task, before any code)

These three rules apply to **every** Odoo task. Skip nothing here; the rest of
this skill is reference — read the section you need when you need it.

### 1. Version awareness — never code from memory alone
LLM training data mixes Odoo 10-19 patterns freely. **Confirm the target
version's API against local source before writing.**

Read the migration guide depth **by task type** (do not over-read):
- **API/architecture/view-type change** (migration, new view type, JS assets, RPC) → read `~/odoo/oca/wiki/Migration-to-version-X.0.md` for the target version + **one before and one after** (3 docs). Reading backward prevents using removed APIs; forward prevents using APIs that don't exist yet.
- **Pure incremental** (add a field/view/model using existing patterns in this repo) → read target version guide only, or skip if you are copying a same-version pattern already in the codebase.
- Then read `references/pitfalls.md` — the repeated-error ledger. If your task touches a listed pattern, apply its fix. If you hit a NEW problem, add it to the ledger (with evidence: file:line or the actual error).

### 2. Information hygiene — do not guess
Every Odoo fact must be confirmed against a local authoritative source,
at **two stages**:
1. **Before coding** — verify API/syntax/conventions against `~/odoo/src/` and `~/odoo/oca/`.
2. **When debugging** — before guessing a fix, search `~/odoo/src/` for similar
   tests/patterns/errors and `~/odoo/oca/` for modules solving the same problem.
   The answer is almost always in the source.

### 3. Bounded debugging — two attempts, then stop
If a fix fails TWICE, stop. Do not try a third variation.
1. First failure → re-read migration wiki / source (the answer is usually documented).
2. Second failure → report to firstmate: what was tried, the obstacle, the
   simplest path forward. Let firstmate decide.

A task that "needs simulating every mode" means the answer is in docs, not more
experiments. Exceeding the dispatch brief's timebox without a material result
means report, not continue.

---

## Reference: read the section your task needs

### Local source layout (`~/odoo/`)

| Dir | Content | Versions |
|-----|---------|----------|
| `src/` | odoo/odoo full repo | branches 19.0 + 20.0, on 20.0 |
| `enterprise/` | odoo/enterprise full repo | branches 18.0-20.0, on 20.0 |
| `documentation/` | odoo/documentation | all versions |
| `oca/` | OCA modules by functional area | per-repo version |
| `oca/wiki/` | OCA migration guides | 8.0-19.0 |
| `oca/maintainer-tools/` | OCA quality tools (pre-commit etc.) | `.venv/` at root |

`git -C ~/odoo/src checkout <branch>` to read a specific version's code.
Project repos/compose live at project-specific paths — use the task brief's paths.

### Research discipline: OCA-first (with a skip condition)

For **generic business requirements**, before building:
1. Search OCA (`~/odoo/oca/`) for an existing module.
2. **Full match** → recommend it directly.
3. **Partial match** → study/extend/adapt.
4. **Older-version only** → migrate forward.
5. **Native replacement** → check if Odoo core/enterprise absorbed it.

**Skip OCA-first for niche or innovative extensions** (e.g. compare-merge style
novel views): there is no precedent to find. Go straight to design.
The check is: *would a generic Odoo shop need this?* If no, skip the search.

### Coding standards

Follow OCA conventions, with **our project defaults** overriding where noted.

**Module structure** (OCA layout): models/, views/, data/, security/,
controllers/, wizard/, report/, tests/, static/src/{js,scss,xml}/, i18n/,
readme/ (DESCRIPTION.rst etc.), migrations/<ver>/pre|post-migration.py,
hooks.py. File names `[a-z0-9_]`; singular module names unless model is plural.

**`__manifest__.py` — our defaults (override OCA):**
- `author`: `Shine IT` (company, not individual — do NOT append ", OCA")
- `support`: `contact@openerp.cn`; `website`: `https://www.openerp.cn`
- `license`: `OPL-1` for paid App Store releases, `LGPL-3` for open source
- Required keys: name, version, license, images, author, website, installable
- Version `OdooMajor.x.y.z` (x=breaking, y=feature, z=bugfix)

**XML conventions:** `<record>` with id before model; `<menuitem>`/`<template>`
shortcuts for menus/QWeb; `noupdate=1` on `<odoo>` root or data tag.
XML IDs: `<model>_view_<type>`, `<model>_action(_detail)`, `<model>_menu(_action)`,
`<module>_group_<name>`, `<model>_rule_<group>`.

**Commits:** `[TAG] module: summary` (≤50 chars). Tags: FIX/IMP/ADD/REM/MIG/REF.
English, present imperative, one logical change per commit.

**Migration scripts:** breaking changes ship `migrations/<version>/` scripts;
cross-version at minimum document changes in README.

### Verification pipeline (decision tree)

```
implement → local smoke (odoo-environment skill) → push → CI is the final gate
```

- **no-mistakes Test step** = targeted verification only (screenshot for visual,
  focused tests for logic, XML/view checks for manifest edits). Never a full
  `--test-tags` Docker run — that duplicates CI and wastes ~15 min.
  Whether the gate is skipped is decided by the dispatch brief (default: targeted).
- **CI** (`.github/workflows/test.yml`, 2-3 min) = final authority. Builds test
  image + Chromium, starts PG, installs module, runs `--test-tags=/<module>`.
  Red CI → fix and re-push.
- Every Odoo repo root carries `.no-mistakes.yaml` with empty `commands.test`.

**Pre-commit (lint/format):**
```bash
source ~/odoo/oca/maintainer-tools/.venv/bin/activate
pre-commit run --all-files   # in the module dir; Ruff via OCA config
```

### Tests

Base classes: `TransactionCase` (savepoint per test), `SingleTransactionCase`
(fast, no savepoints), `HttpCase` (HTTP/tours).

**Non-negotiable setup:** `tests/__init__.py` must explicitly import every test
module (`from . import test_foo`); test modules are NOT imported in the module's
own `__init__.py`.

**Pattern:**
```python
from odoo.tests.common import TransactionCase
from odoo.tests import tagged

@tagged('post_install', '-at_install')
class TestMyFeature(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.record = cls.env['my.model'].create({'name': 'Test'})
    def test_logic(self):
        self.record.do_something()
        self.assertEqual(self.record.state, 'done')
```

**Key helpers:** `browse_ref('xml.id')` / `ref('xml.id')`; `assertRecordValues`;
`odoo.tests.Form(model)` to fire onchange (does NOT fire on direct writes).

**Hard rules:**
- Every bug fix ships a test that fails without the fix; new modules test all functions.
- TransactionCase/SingleTransactionCase: create data in setUpClass, never rely on demo.
- HttpCase/tours: use demo data or common setup; NEVER `cr.commit()` (rollback
  cleans up). Tours use `@tagged('post_install', '-at_install')`.
- Tags: `post_install,-at_install` (standard), `at_install`, `external,-standard`
  (excluded by default).

**Run tests:**
```bash
odoo-bin -d <db> -i <module> --test-enable                       # full module
odoo-bin -d <db> --test-file=addons/<module>/tests/test_foo.py   # single file
odoo-bin -d <db> --test-tags=/<module>,post_install              # by tag
odoo-bin -d <db> --test-tags=:TestMyFeature.test_logic           # specific
```
`--test-tags` implies `--test-enable`; module must be installed first (`-i` once).

### Branch and release discipline (dev line vs frozen release branches)

`main` is the **development line**, not "the latest release": it tracks the Odoo
version currently under development (17/18/19 during their dev windows, then 20),
so it runs ahead of every published version by design.

1. **`main` = dev line.** Do new development on `main`, against the
   in-development Odoo version.
2. **Version branches are the release line.** Create `17.0` / `18.0` / `19.0`
   (the newest one aligned with `main`), publish from there (store assets,
   pricing, GitHub release, apps.odoo.com registration), and treat each as a
   **frozen release branch** from that point on.
3. **Divergence is normal.** `main` keeps moving to the next Odoo version, so it
   inevitably forks from the release branches. "Behind `main`" is part of a
   release branch's definition, not a defect to repair.
4. **Every bug fix lands twice.** Apply it on `main` *and* on each release branch
   that needs it, adapted to that version's code. Content matches; history
   differs; the change is written a second time, not merged.
5. **Does it belong in a release branch?** Customer-visible → yes (behavior
   fixes, user-facing copy, manifest/listing flags, data corrections). Internal
   only → `main` only (pure development, docs, scaffolding, repo tooling).
6. **Never measure a release branch by commit count.** `main` squash-merges and
   release branches replay changes line by line, so patch-equivalence tools
   (`git cherry`, `patch-id`) report content that is already present as missing.
   Compare **content features** instead: pick 3-5 stable greppable markers
   (manifest keys, literal copy strings, function/constant names, record counts,
   directory presence, view field names) and run per branch:
   `git show origin/<branch>:<file> | grep -c <marker>`.
7. **After every merge, run the checklist on every release branch** — 17.0 / 18.0
   / 19.0 / 20.0 (the outward-facing release branch is `20.0`, not `main`), and
   fill each gap on the spot. Copy/text changes must match `main` verbatim, and
   one worker applies them everywhere so the wording stays identical.
8. **Acceptance evidence comes from the outward-facing release branch** — the
   store and customers read `20.0`, not `main`.

### Version migration reference

`~/odoo/oca/wiki/Migration-to-version-X.0.md` = canonical breaking-change
reference (API renames, view syntax, JS assets, RPC, XML schema). When debugging
version-confusion errors, cross-reference the guide before code fixes.

### Odoo 19 frontend notes (not in the migration wiki)

- **Tours in Docker:** `HttpCase.start_tour()` needs websocket-client + Chromium;
  on ARM64 use Playwright (`python3 -m playwright install chromium`); install
  system deps via apt first (`--with-deps` fails in Docker).
- **Custom view type:** override `_get_view_info()` on `ir.ui.view`
  (include `multi_record: True` for multi-record views) or `loadView()` throws.
- **Owl 2 controller props:** declare Model/Renderer props as `Function`, not
  `Object` — a mismatch silently renders an empty view, no console error.
- **Hoot dropdown:** synthetic click may miss Dropdown's native listener; use
  `document.querySelector(...).click()` in the tour's run callback.
