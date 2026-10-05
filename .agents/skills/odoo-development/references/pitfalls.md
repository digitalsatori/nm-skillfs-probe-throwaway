# Odoo Development Pitfalls Ledger

Repeated-error detection ledger. Every new pitfall encountered during Odoo
development is recorded here first. When the same pattern occurs twice or more,
it is promoted into the main SKILL.md body and removed from this ledger.

## How to use

- **Before starting any task**: read this file. If your task touches a
  pattern listed here, apply the documented solution.
- **When you hit a NEW problem**: add an entry below with date, symptom,
  root cause, and solution. Do not promote it to SKILL.md yourself.
- **When you hit a problem already listed here**: bump its `occurrences`
  counter. Firstmate promotes entries with `occurrences >= 2` into SKILL.md.

## Ledger

### Cross-project CI / build gotchas

These are cross-project engineering notes that bite when wiring CI or
rebuilding images across the fleet:

- **CI workflow branch allow-list**: `on.pull_request.branches` must include the
  target branch. With `branches: [main]`, a PR targeting a version branch does
  NOT trigger CI.
- **GitHub Actions `env:` does not expand shell variables**: the `env` block
  passes values verbatim; shell expansion only happens inside a `run:` step.
- **Pin the branch when cloning cross-repo dependencies**: follow the PR's
  target branch, or the container builds against the wrong version.
- **Check `FROM` per branch in Dockerfiles**: copying another version's
  Dockerfile without fixing `FROM` makes tests "pass" against the wrong
  container.
- **EE instances are readable reference source**: an EE instance (e.g.
  `omarchydoo-ee-odoo-1` on host port 8032) with `web_enterprise` installed lets
  you read EE scss/js in the container for a same-version comparison.

### 2026-09-12: Resetting test data must go through the ORM, not raw SQL

- **occurrences**: 1
- **symptom**: After resetting/rolling back test data, "ghost" fields and
  columns persist — shadow fields don't disappear, NOT NULL columns drift, and
  the agent "sees" fields the DB no longer has.
- **root cause**: reset scripts deleting fields via raw SQL do not invalidate
  the running Odoo process's in-process ORM registry cache, so ORM introspection
  keeps returning the deleted fields. All of "shadow field not disappearing",
  "NOT NULL drifted column", and "registry ghost field" are the same symptom —
  changing schema by bypassing the ORM.
- **solution**: do it in two layers, both required:
  1. Delete the field's `ir.model.fields` record through the ORM in
     `odoo shell` — `env['ir.model.fields'].browse(<field_id>).unlink()` — or
     remove the field from the model definition and `-u` the module. Either
     drops the column and clears shadow fields. Do NOT call `unlink()` on the
     test data records; that deletes rows, not the field, and does not drop the
     column or clear the registry ghost field.
  2. Always call `env.registry.signal_changes()` at the end to broadcast the
     registry change — committing alone does not invalidate the running
     instance's cached ghost fields (second hit: DB had zero residual rows but
     the tool still reported "field already exists").
     Version note: `signal_changes()` is the 19.0 name; 20.0 renamed it to the
     private `_signal_changes` (`odoo/orm/registry.py`) - check the target
     version's registry API before relying on it.
  Use raw SQL only for reading/confirming. When querying, `LIKE 'x_%'` treats
  `_` as a wildcard — use `~ '^x_'` or escape it.

### 2026-09-01: Odoo 15/16 backend compiles secondary palette to white

- **occurrences**: 1
- **symptom**: Buttons using `btn-outline-secondary` (or the `text-secondary`
  / `border-secondary` utilities) are white-on-white in the Odoo 15 and 16
  backends - invisible until hover fills the background.
- **root cause**: Both versions set the backend `$secondary`/secondary theme
  color to white (`bootstrap_review.scss` on 15, `bootstrap_overridden.scss
  $secondary: $white` on 16), so the generated outline-secondary/text-
  secondary/border-secondary rules compile to `#fff`. 17/18/19 compile dark
  colors (#495057 / #212529) and are unaffected.
- **solution**: Use `btn-link` + a `text-muted` icon (or
  `btn-outline-primary`) for small backend buttons on 15/16. Verify colors
  against the SERVED bundle (`/web/webclient/qweb/<hash>` for 15.0 qweb
  templates; `/web/assets/*web.assets_backend.min.css` for styles), not
  source scss - multiple conflicting utility rules can exist in one bundle.

### 2026-07-30: Module version must match Odoo series prefix

- **occurrences**: 1
- **symptom**: Version `19.1.0.0` makes module uninstallable (installable=False),
  0 tests run.
- **root cause**: `odoo/modules/module.py` `check_version()` requires the
  version to start with `release.major_version` (e.g. `19.0.`). `19.1.0.0`
  is treated as Odoo 19.1 series, not 19.0 + module minor.
- **solution**: Module version format is `OdooSeries.x.y.z` (e.g. `19.0.3.0.0`).
  The second number is the MODULE's minor version, never the Odoo minor.

### 2026-07-30: Registry override needs `force: true`

- **occurrences**: 1
- **symptom**: `registry.category("views").add("compare", ...)` throws "Cannot
  add key 'compare' in the views registry: it already exists"
- **root cause**: Patching an existing view type requires `force: true`:
  `registry.category("views").add("compare", view, { force: true })`.
  Without it, Odoo's registry refuses the duplicate key.
- **solution**: Add `{ force: true }` as third argument when overriding an
  existing registry entry. Prefer `patch()` from `@web/core/utils/patch` for
  component-level overrides.

### 2026-07-30: Dark mode styles must use `.dark.scss`

- **occurrences**: 1
- **symptom**: Colors hardcoded in plain `.scss` don't adapt in Odoo dark mode;
  highlights are invisible or low-contrast.
- **root cause**: Odoo ships dark-mode overrides in a separate `<file>.dark.scss`
  bundle loaded conditionally under `o_dark_mode`. Putting dark rules in the
  main `.scss` does not apply them in dark mode.
- **solution**: Create `static/src/scss/<name>.dark.scss` with dark-mode
  overrides and register it in `web.assets_backend` alongside the main SCSS.
  Reference the SCSS variables (`$o-gray-*`) for consistency.

### 2026-07-30: Tag/m2m values must resolve display names, not IDs

- **occurrences**: 1
- **symptom**: many2many_tags matrix shows raw record IDs instead of display
  names (e.g. "1, 2" instead of "electronics, premium").
- **root cause**: `orm.read(comodel, ids, ["name"])` may return raw fields;
  `display_name` must be requested explicitly, or resolved via
  `display_name` field read.
- **solution**: Always `orm.read(comodel, ids, ["display_name"])` for
  user-visible rendering. Never render raw IDs.

### 2026-07-30: `demo/` data not loaded during `--test-enable`

- **occurrences**: 1
- **symptom**: Tour tests (HttpCase) fail with "External ID not found" because
  demo data records are absent.
- **root cause**: Odoo 19 does not install demo data by default when running
  tests. `--demo all` must be passed, or records must live in `data/` with
  `noupdate="1"`.
- **solution**: Run tests with `--demo all` (flag is `--with-demo` in Odoo 19
  server command). Keep demo data in `demo/` key. Never move demo records to
  `data/` — that pollutes production installs.
