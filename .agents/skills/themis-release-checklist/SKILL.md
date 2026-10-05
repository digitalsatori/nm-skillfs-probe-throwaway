---
name: themis-release-checklist
description: "Use when a Shine Themis series batch reaches a batch boundary (bug stop, feature freeze, release preparation, or after a major overhaul lands) and must pass the release-batch gate: an executable eight-group checklist (scope ledger, code gates, semantics/upgrades, interaction/visual, copy/naming, assets, runtime residue, closeout) with per-item commands, pass criteria, evidence, and automation flags. Run once per batch, NOT per PR - the per-PR tiered CI owns that layer."
metadata:
  internal: true
---

# Shine Themis release-batch checklist

A batch that cannot show its gate evidence does not ship. This skill turns the
cross-surface inconsistencies that used to be found by eyeball ("the store copy
drifted on 19.0", "the bench still had tour rows", "the screenshot shipped with
placeholder icons") into fixed gates with commands, pass criteria, and evidence.

## When to run this

At a **batch boundary**, exactly once per batch:

- bug stop (the moment bug fixes are frozen into a release batch),
- feature freeze,
- release preparation,
- after a major overhaul lands.

**Not per PR.** Per-PR verification is the tiered CI's job (see
themis-dispatch-playbook for how dispatches map to tools and acceptance).
This checklist is the batch-level sweep across all five lines and all four
modules at once - the layer no single PR's CI sees.

## Who runs this

The main-home crew (the side with local docker, the bench host, and the
`shine-themis-pro` workbench clone). The runner executes the automatable items
and assembles the evidence page; every visual item names its human viewer.
Merge authority stays with the captain throughout.

## The pass rule

- Every item marked **automated** or **partial** must show its **raw tool
  output** in the evidence page - a self-declared "gate GREEN" counts for
  nothing (themis-dispatch-playbook pre-flight rule 6).
- Every `DRIFT` line is fixed or explained; every `FETCH FAILED` line must sit
  on an `upgrade|migration` entry and be manually diffed (item 5).
- Every **visual item** names its URL/bench, its viewer, and a verdict on the
  evidence page. "I looked at it" without a URL is not a verdict.
- The batch passes only when the one-page evidence template (below) is
  complete. Partial evidence = the batch does not pass, whatever the individual
  items say.

## Tool-name verification record

All `tools/` names below were verified against the series repository
`origin/main` **2026-10-01** (head `34473b0`, "[ADD] tools: consolidate the
week's one-off scripts into standard tools (#23)"): 13 files, including
`tools/README.md` (the tool index), the six standard entry points
`lane-run.sh` / `upgrade-path.sh` / `bench-refresh.sh` / `scenario-check.sh` /
`assets-capture.sh` / `ee-up.sh`, and the two standing gates
`check-manifests.py` / `check-engine-drift.sh`. The pre-consolidation names
`ci_ui_scenarios.py`, `ci_upgrade_check.sh`, `ui_lane.sh` still exist, and
`.github/workflows/ci.yml` still calls those three - so the unified entry
points are fixed but CI has not switched over yet. Use the new names in batch
runs; touch the old names only when editing CI itself. Re-verify with
`ls tools/` + `git log -1 origin/main` before trusting this section after a
long gap.

Re-verify any skill or tool name against the live repositories before citing
it in dispatch text: the seven sibling skills live in
`.agents/skills/<name>/SKILL.md` of odoo-dev-skills; there are no others.

---

## Group 1 - Scope ledger

### 1.1 Batch change inventory, classified by audience

- **What**: every commit in the batch, classified as customer-visible
  (fix / behaviour improvement → release branches) vs repo-internal
  (tools / docs / CI → `main` only).
- **How**:
  ```sh
  cd <series-clone> && git fetch origin
  git log --oneline origin/20.0@{push}..origin/20.0        # or vs the batch base tag
  git diff --stat <prev-batch-head>..origin/20.0 -- ':!tools' ':!.github' ':!*.md'
  ```
  Repeat the second command with `-- tools .github` for the repo-internal set.
- **Pass**: each listed change appears in exactly one audience column, and
  nothing is "both" (a fix that needs tool changes is two changes).
- **Evidence**: the classified commit list, pasted.
- **Automation**: automated (the listing; the per-change audience call is human).

### 1.2 Five-line necessity walk

- **What**: for each customer-visible change: is it needed on all four release
  lines (20.0/19.0/18.0/17.0) plus `main`? Engine changes and data fixes
  normally are; Odoo-version-specific workarounds may not be.
- **How**: walk the 1.1 list line by line with
  `git log --oneline origin/<line> -5 -- <paths>` per line to confirm presence
  or record the deliberate skip.
- **Pass**: every customer-visible change is either present on all five lines
  or carries a written reason for the lines it skips. Release branches take
  direct commits + normal push (no PR/squash/force); only `main` goes through a
  non-draft PR (themis-series-layout section 1, MBA-home learnings).
- **Evidence**: the walk table (change × five lines × present/skipped+reason).
- **Automation**: partial.

---

## Group 2 - Code gates

### 2.1 Manifest gate on every line

- **What**: `tools/check-manifests.py` on `main`, `20.0`, `19.0`, `18.0`,
  `17.0` - required keys, `depends` only `web`, version prefix matches branch,
  `hooks_pro.py` canonical, no hard-coded sibling names.
- **How** (fresh source per line, no worktree needed):
  ```sh
  git -C <series-clone> archive origin/<line> | tar -x -C /tmp/sts-<line>
  cd /tmp/sts-<line> && python3 tools/check-manifests.py <line>
  ```
- **Pass**: clean exit on all five lines; any finding is fixed, not waived -
  the store indexes the whole repository, one bad manifest can unpublish every
  module (themis-series-layout section 6).
- **Evidence**: raw output per line.
- **Automation**: automated.

### 2.2 Engine drift gate on every line

- **What**: `tools/check-engine-drift.sh` per line - every vendored engine file
  byte-identical to `digitalsatori/shine-themis-pro@main` (pro is the fan-out
  source; themis-series-layout section 4). The judge source must be fresh: the
  script fetches pro live (gh api / raw.githubusercontent) - run it after
  `git fetch origin` and never against a cached one-off pro copy; the
  offline fallback snapshot `/Users/tony/backups/shine-themis-pro.git` lags the
  mini workbench.
- **How**: inside each `/tmp/sts-<line>` from 2.1: `bash tools/check-engine-drift.sh`
- **Pass**: final line `GREEN` on all five lines; every `DRIFT` line fixed or
  explained; an engine fix always lands in pro first, then is copied here.
- **Evidence**: full raw output per line, `GREEN` last line visible.
- **Automation**: automated.

### 2.3 FETCH FAILED manual diff

- **What**: in 2.2's output, `FETCH FAILED` entries - by design these occur on
  `upgrade|migration` scripts because pro is not on GitHub
  (themis-dispatch-playbook rule 7).
- **How**: for each `FETCH FAILED` line, diff the repo copy against the local
  pro clone by hand:
  ```sh
  ssh tony@tonymac-mini.taile2f97c.ts.net cat <pro-clone>/<path> | diff - <line-tmp>/<path>
  ```
- **Pass**: `FETCH FAILED` appears only on `upgrade|migration` entries, each
  manually diffed clean; any other `FETCH FAILED` is a red gate.
- **Evidence**: the manual diffs, pasted.
- **Automation**: partial.

### 2.4 Test suites, raw counts, per line per module

- **What**: each module's test suite on each line, plus the module-owned files
  outside the engine (`tests/__init__.py`, `test_*.py`) which drift silently -
  check them against pro's same-line versions after any engine sync
  (MBA-home learnings).
- **How**: `tools/lane-run.sh shine_themis_<series> --ref origin/<line>` for
  each of the four modules on each line being released (disposable lane: fresh
  db, own postgres, removed on exit; prints raw result counts).
- **Pass**: raw counts show 0 failures / 0 errors on every run; a suite that
  did not run counts as failed, not as absent.
- **Evidence**: the lane's raw count lines per module per line.
- **Automation**: automated.

---

## Group 3 - Semantics and upgrades

### 3.1 Upgrade path: old head → new head → idempotent re-upgrade

- **What**: install at the previous head, upgrade to the new head, upgrade
  again - asserting module state, `latest_version`, the preset xmlid set, and
  no `ERROR` in the log. `tools/upgrade-path.sh` performs all three steps and
  the assertions.
- **How**:
  ```sh
  tools/upgrade-path.sh shine_themis_<series> origin/<line>~15 origin/<line> --version <N>
  ```
  (pre-ref = an older customer-ish state; post-ref = the batch head).
- **Pass**: the tool's assertions all hold; media/preset rows do not double on
  the re-upgrade (themis-theme-sourcing section 10).
- **Evidence**: the raw tool output per module.
- **Automation**: automated.

### 3.2 Migration gate

- **What**: `migrations/<x.y.z>/` endpoint dirs may only be added by batches
  that follow the series' first store release. The series is **not yet
  published** → this batch must add **none**. Existing endpoint dirs
  (historical cleanup migrations) are grandfathered; they are not permission to
  add more.
- **How**:
  ```sh
  git -C <series-clone> diff --name-only <prev-batch-head>..origin/<line> -- '*/migrations/*'
  ```
- **Pass**: empty output on all lines while unpublished. After the first store
  release this gate flips: every version bump must carry its cleanup migration
  in a **new endpoint dir on every affected line** - Odoo only runs an endpoint
  script when `installed_version < endpoint <= new_version`, so a cleanup hung
  only on an old endpoint never runs on a database that already passed it
  (MBA-home learnings).
- **Evidence**: the (empty) diff output per line.
- **Automation**: automated.

---

## Group 4 - Interaction and visual

### 4.1 CE scenario pass on a real bench

- **What**: theme switch through the real tray, launcher card count (official
  entry count), preferences Theme tab, home wallpaper layers - and a deliberate
  look at **Corporate Dark** on the home screen.
- **How**: refresh the bench to the batch head, then
  ```sh
  tools/bench-refresh.sh <series>
  tools/scenario-check.sh http://old-mac.taile2f97c.ts.net:8102 \
      --scenarios s1-picker,s2-launcher,s3-prefs,s4-wallpaper
  ```
  Then switch to Corporate Dark via the tray (s1 does the switching) and view
  the home screen - that last look is a visual item (V2 below).
- **Pass**: all four scenarios report pass; the launcher card count matches the
  expected official entry count.
- **Evidence**: raw scenario output + bench URL.
- **Automation**: automated (Corporate Dark look: visual item V2).

### 4.2 EE parity pass

- **What**: the same interaction set on Enterprise - the engine must behave
  identically with `web_enterprise` installed.
- **How**:
  ```sh
  tools/ee-up.sh up <series> --edition ee
  tools/scenario-check.sh <ee-lane-url> --scenarios s1-picker,s2-launcher,s3-prefs,s4-wallpaper
  ```
- **Pass**: all four scenarios pass on the EE lane.
- **Evidence**: raw scenario output + EE lane URL.
- **Automation**: automated.

### 4.3 Icon gate before every screenshot

- **What**: no screenshot may be taken before the tool has asserted the
  module's icons actually rendered - a placeholder-icon set shipped once
  (assets-screenshot-refix, 2026-10). The gate lives inside
  `scenario-check.sh` and `assets-capture.sh`; never weaken or bypass it.
- **How**: no separate step - the gate is part of every capture; a gate failure
  means no screenshot, full stop.
- **Pass**: every screenshot in the evidence page was produced by a gated
  capture run.
- **Evidence**: the capture runs' output lines showing the gate pass.
- **Automation**: automated.

---

## Group 5 - Copy and naming

### 5.1 Manifest name/summary verbatim across lines

- **What**: the four release lines × four modules - `name` and `summary` must
  be character-identical to 20.0 (the outward-facing canonical line).
- **How**:
  ```sh
  extract='import ast,sys; d=ast.literal_eval(sys.stdin.read()); print(d["name"]); print(d["summary"])'
  for m in quiet vivid serene cozy; do
    for line in 17.0 18.0 19.0; do
      diff <(git show origin/20.0:shine_themis_$m/__manifest__.py | python3 -c "$extract") \
           <(git show origin/$line:shine_themis_$m/__manifest__.py | python3 -c "$extract") \
        && echo "OK $line/shine_themis_$m"
    done
  done
  ```
- **Pass**: `OK` for all 12 combinations, zero diff lines.
- **Evidence**: the full loop output.
- **Automation**: automated.

### 5.2 Outward-facing copy is English only

- **What**: every string a customer can see - manifest `name` / `summary` /
  `description`, store listing text, license/author fields - contains no CJK
  characters.
- **How**:
  ```sh
  for line in 20.0 19.0 18.0 17.0; do
    git archive origin/$line shine_themis_* | tar -x -C /tmp/sts-cjk-<line>
    grep -rnP '[\x{4e00}-\x{9fff}\x{3000}-\x{30ff}]' /tmp/sts-cjk-<line>/shine_themis_*/__manifest__.py && echo "CJK FOUND" || echo "CLEAN $line"
  done
  ```
  (on macOS use `perl -ne 'print if /[\x{4e00}-\x{9fff}]/' ` instead of `grep -P`.)
- **Pass**: `CLEAN` on every line; the quoted copy in the evidence page is the
  English text itself, not a description of it.
- **Evidence**: the grep output per line.
- **Automation**: automated.

### 5.3 Card image = first `_screenshot` image

- **What**: in each module's `images/`, the store card image is the first image
  whose filename ends in `_screenshot` - today `card_screenshot.png`, and it
  must stay first (no second `*_screenshot` file may jump ahead of it).
- **How**:
  ```sh
  for m in shine_themis_quiet shine_themis_vivid shine_themis_serene shine_themis_cozy; do
    git ls-tree --name-only origin/20.0:$m/images/ | grep '_screenshot' | head -2
  done
  ```
- **Pass**: exactly one `*_screenshot` entry per module, and it is the intended
  card image (`card_screenshot.png`).
- **Evidence**: the listing output per module.
- **Automation**: automated.

---

## Group 6 - Assets

### 6.1 Asset completeness per module per line

- **What**: cover, card image, feature shots, and home/launcher screenshots all
  present for all four modules on every release line (the canonical 8-file set:
  `cover.jpg`, `card_screenshot.png`, `feature_*.jpg`, `shot_*.jpg`).
- **How**:
  ```sh
  for line in 20.0 19.0 18.0 17.0; do for m in shine_themis_*; do
    echo "== $line/$m"; git ls-tree --name-only origin/$line:$m/images/
  done; done
  ```
  Compare against the previous batch's listing; new files need a reason, gone
  files need a bigger one.
- **Pass**: the 8-file set complete everywhere; no unexplained deltas.
- **Evidence**: the per-line listings.
- **Automation**: automated.

### 6.2 Each image matches its name

- **What**: `shot_home.jpg` really shows the home screen, `shot_launcher.jpg`
  the launcher, `shot_sales.jpg` a sales view, `shot_home_dark.jpg` dark mode -
  a renamed or recycled image ships wrong content to the store.
- **How**: `tools/assets-capture.sh --check --out <set-dir>` validates naming +
  dimensions mechanically; the content match itself is eyeball work (visual
  item V3).
- **Pass**: `--check` clean on dimensions/naming; V3 verdict recorded.
- **Evidence**: `--check` output + V3 verdict.
- **Automation**: partial.

### 6.3 No near-duplicate pair within a module

- **What**: two almost-identical images in one module's set read as a mistake
  on the listing (same scene, same angle, 95% overlap).
- **How**: open each module's image set side by side and judge (visual item
  V3); there is no tool for this today.
- **Pass**: viewer records "no near-duplicates" per module.
- **Evidence**: V3 verdict with the viewer's name.
- **Automation**: visual.

### 6.4 No 404s, size budget holds

- **What**: every asset URL referenced by the batch (store listing, description
  page images) resolves; each module stays within the media size budget
  (≤ 25 MB module total, themis-theme-sourcing section 9).
- **How**:
  ```sh
  for u in $(cat asset-urls.txt); do curl -sIL -o /dev/null -w '%{http_code} %{url_effective}\n' "$u"; done
  git archive origin/20.0 shine_themis_* | tar -x -C /tmp/sts-size && du -sh /tmp/sts-size/shine_themis_*/
  ```
- **Pass**: every URL answers `200`; every module ≤ 25 MB.
- **Evidence**: the curl table and the `du` totals.
- **Automation**: partial (the URL list itself is assembled by hand).

---

## Group 7 - Endpoint and runtime residue

### 7.1 Bench residue clean after refresh

- **What**: a refreshed bench must not serve stale asset bundles or carry tour
  state: `/web/assets/%` attachments cleared, `tour_enabled=false` for all
  users, `web_tour_tour` table empty. `tools/bench-refresh.sh` performs exactly
  these three cleanups as part of every refresh.
- **How**: after `tools/bench-refresh.sh <series>`, prove it:
  ```sh
  ssh <BENCH_HOST> docker exec fm-spot-<series>-pg psql -U odoo -d shine_<series> -c \
    "SELECT (SELECT count(*) FROM ir_attachment WHERE url LIKE '/web/assets/%') AS assets,
            (SELECT count(*) FROM res_users WHERE tour_enabled) AS tours_on,
            (SELECT count(*) FROM web_tour_tour) AS tour_rows;"
  ```
  Then hard-refresh the browser (visual item V2 doubles as the serving check).
- **Pass**: the query returns `0 / 0 / 0`; the hard refresh renders clean.
- **Evidence**: the psql output row + bench URL.
- **Automation**: automated.

---

## Group 8 - Closeout

### 8.1 All five lines pushed, heads recorded

- **What**: `main`, `20.0`, `19.0`, `18.0`, `17.0` all pushed, and the exact
  head hash of each line recorded in the evidence page.
- **How**:
  ```sh
  git -C <series-clone> fetch origin
  for line in main 20.0 19.0 18.0 17.0; do
    echo "$line $(git -C <series-clone> rev-parse origin/$line)"
  done
  ```
- **Pass**: each recorded hash matches the post-push `origin/<line>`; nothing
  pushed after the gates ran (if a push lands later, re-run the gates).
- **Evidence**: the five `line hash` rows, timestamped.
- **Automation**: automated.

### 8.2 The "not doing this batch" ledger

- **What**: an explicit list of what this batch deliberately does NOT do, each
  with a reason - the standing antidote to silent scope creep and to "was that
  forgotten?" review questions.
- **How**: the runner drafts it from the batch discussion; the captain-adjacent
  wording is judged by a human (visual item V4).
- **Pass**: the ledger exists, is non-empty or explicitly says "nothing
  deferred", and every entry has a reason.
- **Evidence**: the ledger section in the evidence page.
- **Automation**: visual.

### 8.3 One-page evidence with the spotcheck bench address

- **What**: the whole batch's evidence on one page a reviewer can audit in a
  single pass - and it must contain the spotcheck bench URL used for groups
  4/7.
- **How**: fill the template below; the bench address is the URL passed to
  `scenario-check.sh` (default bench host `tony@old-mac`, e.g.
  `http://old-mac.taile2f97c.ts.net:8102`).
- **Pass**: template fully filled; every automated item's raw output reachable
  from the page; every visual item has viewer + URL + verdict.
- **Evidence**: the evidence page itself (this is the deliverable).
- **Automation**: partial.

---

## Visual items (human-look gates)

| # | What the eye decides | Where to look | Pass looks like |
|---|----------------------|---------------|-----------------|
| V1 | Store listing look-and-feel: card image right, description reads well, "choose one series" note present | apps.odoo.com listings for the four series | Verdict per listing with the listing URL |
| V2 | Corporate Dark on the real bench home: palette, wallpaper, tray; also the post-refresh serving check | The bench from 4.1, after hard refresh | Verdict + screenshot (icon-gated) + bench URL |
| V3 | Image-name correspondence and no near-duplicate pair per module | The `images/` set of each module (6.2/6.3) | Verdict per module, viewer named |
| V4 | "Not doing this batch" ledger wording (8.2) | The evidence page | Captain-readable ledger, viewer named |
| V5 | Evidence page is one-page auditable (8.3) | The evidence page | Verdict that a reviewer can pass it in one read |

A visual item without a named viewer, a URL, and a verdict is an open gate.

---

## One-page evidence template

```markdown
# Release-batch evidence: <batch slug> (<date>)
Runner: <name>   Bench: <URL from groups 4/7>

## Heads (8.1)
main <hash> | 20.0 <hash> | 19.0 <hash> | 18.0 <hash> | 17.0 <hash>

## Scope (1.1, 1.2)
<classified commit list> <five-line walk table>

## Code gates (2.1-2.3)
<raw check-manifests.py + check-engine-drift.sh output per line,
DRIFT explanations, FETCH FAILED manual diffs>

## Tests (2.4)
<per line × per module raw count table>

## Upgrades & migrations (3.1, 3.2)
<raw upgrade-path.sh output per module> <empty migration diffs per line>

## Interaction & visual (4.1-4.3)
<raw scenario output CE + EE, capture runs with icon gate, bench URL>

## Copy & naming (5.1-5.3)
<verbatim-diff loop output, CJK grep output, card-image listing>

## Assets (6.1-6.4)
<completeness listings, --check output, curl table, du totals>

## Runtime residue (7.1)
<psql 0/0/0 row + bench URL>

## Not doing this batch (8.2)
<ledger with reasons>

## Visual verdicts (V1-V5)
<each: what, viewer, URL, verdict>
```

## Boundaries

- This checklist verifies; it does not fix. A red gate sends work back through
  themis-dispatch-playbook routing to the owning skill.
- Do not extend this skill into orchestration: one day it may become a script,
  but only after two batches have proven the checklist's shape.
- The underlying disciplines are not duplicated here: environment/container
  rules in odoo-environment, media rules in themis-theme-sourcing, store-asset
  specs in odoo-store-assets, arrangement/publishing in themis-series-layout,
  module testing discipline in odoo-development, demo videos in
  demo-video-recording.
