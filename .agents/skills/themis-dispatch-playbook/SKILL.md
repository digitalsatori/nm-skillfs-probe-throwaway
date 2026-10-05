---
name: themis-dispatch-playbook
description: "Use when composing, dispatching, or picking up a fleet task brief: route one of six task categories (engine port & version-line alignment, multi-module batch sync & copy batches, migration endpoints & upgrade paths, theme media sourcing & pack entry, store assets, live verification & bench refresh incl. EE) to its required skill, its series-repo tools/ script (existing or pending solidification), its shared pre-flight checks, and its acceptance evidence form. Routing layer only - the six domain skills own the actual disciplines."
metadata:
  internal: true
---

# Fleet dispatch playbook (six task categories)

A routing layer between a task brief and the six domain skills. It answers the
captain's standing complaint: a dispatched crew must know the required skill,
the required tool, and the acceptance command **at pickup time**, not discover
them by trial. This skill owns ONLY routing, the shared pre-flight checks, and
the acceptance-evidence forms. Every domain rule lives in its own skill - the
templates below point at them, never restate them.

The six domain skills, in one line each:

- **odoo-development** - writing/changing module code or migrations; version
  awareness, branch and release discipline, tests, verification pipeline.
- **odoo-environment** - provisioning/operating containers and benches;
  compose, mounts, lifecycle, filestore pairing.
- **themis-series-layout** - shine-themis-series repo structure, engine
  fan-out, publishing; the arrangement rules.
- **themis-theme-sourcing** - sourcing/licensing/composing theme media;
  channels, licences, media standard, size budget, verification.
- **odoo-store-assets** - covers, screenshots, description pages, pricing,
  listing registration; store specs and compliance.
- **demo-video-recording** - testreel demo videos and screenshots cut from
  takes; the captain's demo requirements.

## Pre-flight checks (every task, before the first tool call)

One line each; every line traces to a fleet learning or a named skill section.

1. `zsh -lic 'env | grep -i proxy'` - a proxy var whose port is not listening
   kills every model request (`Connection error.`, zero tokens); confirm with
   `nc -z 127.0.0.1 <port>` and one A/B call with/without the var; fix is
   machine-side (open the port or drop the export). [main-home learnings:
   环境与机器]
2. A test container must mount a **persistent filestore**; container `Up` or a
   login page 200 is NOT "usable" - judge by an in-container DB query or Odoo
   log DB-connection errors. [main-home learnings: 测试与验收; odoo-environment
   "Container lifecycle"]
3. Before any screenshot/video capture, assert the target actually rendered -
   tools report steps "successful" even when a click silently no-ops; verify
   with the 1 fps contact sheet. [demo-video-recording "Pipeline gotchas"]
4. Work moved across machines travels as **committed content only**
   (`git archive`); uncommitted worktree state does not travel. [main-home
   learnings: 测试与验收]
5. A version-line task starts with `git fetch`, then branches/rebases from the
   **current** `origin/<line>` head - a branch off a stale head ships a fake
   rollback and the push is (correctly) rejected. [main-home learnings:
   派工与交付]
6. A self-declared "gate GREEN" counts for nothing: require the RAW tool
   output, and a **fresh judge source** (`git archive <pro-ref>` to a local
   temp dir, not a one-off pulled copy). [main-home learnings: 验收纪律]
7. In the drift gate, `upgrade|migration` entries report `FETCH FAILED` by
   design (pro is not on GitHub) - compare those manually against the local
   pro clone. [main-home learnings: 验收纪律]
8. External-facing copy is English only (including in-image text and video
   subtitles); run a CJK-character self-check before delivery. [main-home
   learnings: 商店与对外]
9. macOS has no `timeout` command - use `gtimeout` or
   `ssh -o ConnectTimeout`. [MBA-home learnings]
10. `shine-themis-series` is ~850 MB with a ~600 MB worktree - check disk
    before cloning or dispatching parallel work on it. [MBA-home learnings]
11. After an engine sync, also diff the module-owned files OUTSIDE
    check-engine-drift.sh's ENGINE_FILES (tests/__init__.py, test_*.py) - they
    silently go stale. [MBA-home learnings]
12. Installing into a container needs `--network=host` + the Tsinghua pip
    source; unpack big archives under `/home/tony/`, not the `/tmp` tmpfs.
    [main-home learnings: 测试与验收]
13. Real-machine/container verification runs on the target repo's existing
    lane scaffolding under `tools/` - never a hand-rolled container flow;
    health criterion and pitfall write-back in odoo-environment "Verification
    lanes". [odoo-environment "Verification lanes"]

## Series-repo tools: status at a glance

`shine-themis-series/tools/` today (verify before relying: `ls` the repo):

| Tool | Status | Purpose |
| `check-engine-drift.sh` | existing | repo-level engine-drift gate vs pro (themis-series-layout section 4) |
| `check-manifests.py` | existing | manifest + guard-file health for every module (themis-series-layout section 6) |
| `hooks_pro_canonical.py` | existing | canonical pro hooks copy that check-manifests.py compares against |
| `ci_ui_scenarios.py` | existing | browser UI scenarios S1-S4 for the series (headless chromium over CDP) |
| `ci_upgrade_check.sh` | existing | heavy-tier upgrade-path check for one module (three legs) |
| `ui_lane.sh` | existing | local browser-scenario lane per module, CE or EE (`ee` needs EE_ADDONS) |
| `lane-run.sh` | 待固化 | expected: one command = scratch lane up + install + module tests for one module on one line |
| `upgrade-path.sh` | 待固化 | expected: canonical upgrade-path check across release branches (today ci_upgrade_check.sh covers it) |
| `bench-refresh.sh` | 待固化 | expected: refresh a review bench = re-export modules to the mount dir → `-u <module>` → restart container |
| `scenario-check.sh` | 待固化 | expected: canonical browser-scenario pass (today ci_ui_scenarios.py + ui_lane.sh cover it) |
| `assets-capture.sh` | 待固化 | expected: capture cover/screenshot set from a real take's frames on the real version container |
| `ee-up.sh` | 待固化 | expected: bring up an EE bench (community image + enterprise branch exported from the mini clone) |

A template below cites the existing files by real name and the pending ones as
待固化 - do not invoke a 待固化 name until it lands in `tools/`.

## Dispatch templates

### 1. Engine port / version-line alignment

- **适用场合**: port an engine change from `shine-themis-pro` into
  `shine-themis-series`; align a series module's line (17.0/18.0/19.0/20.0 or
  main) with its pro counterpart; fan one engine fix out to every series on a
  line.
- **必读技能**: themis-series-layout sections 1-4 (publishing unit,
  self-contained modules, engine source of truth, drift control);
  odoo-development "Branch and release discipline" (dev line vs frozen
  release branches, every fix lands twice). Note: release branches 17.0-20.0
  take direct commits + normal push (no PR, no squash, no force); only `main`
  goes through a non-draft PR. [MBA-home learnings]
- **必用工具**: `tools/check-engine-drift.sh`, `tools/check-manifests.py`,
  `tools/hooks_pro_canonical.py`; `lane-run.sh` 待固化.
- **验收命令与证据形式**: pre-flight 5 (fetch, branch from current
  `origin/<line>`); paste check-engine-drift.sh's **full raw output** - pass
  = final line `GREEN`, every `DRIFT` line explained or fixed, and
  `FETCH FAILED` appearing only on `upgrade|migration` entries (pre-flight 7,
  with the manual diff vs the local pro clone pasted); paste the branch point
  (`git merge-base` / head hash) proving it sits on current `origin/<line>`;
  paste the diff of the module-owned test files outside ENGINE_FILES
  (pre-flight 11).

### 2. Multi-module batch sync & copy batches

- **适用场合**: apply one batch change (theme set, copy text, manifest facts)
  across every series module on one or more version lines; copy batches that
  must stay verbatim-identical across lines.
- **必读技能**: odoo-development "Branch and release discipline" points 4, 6,
  7 (fix lands twice; content markers, not commit counts; post-merge checklist
  on every release branch, outward-facing line is 20.0); themis-series-layout
  sections 6-7 (store facts, naming).
- **必用工具**: `tools/check-manifests.py`, `tools/check-engine-drift.sh`;
  `scenario-check.sh` 待固化 (today per-module via ci_ui_scenarios.py /
  ui_lane.sh, see template 6).
- **验收命令与证据形式**: per line, paste `git show origin/<line>:<file> |
  grep -c <marker>` for 3-5 stable markers (odoo-development point 6); paste
  check-manifests.py raw output per line; paste `git diff --numstat
  main..<line>` reviewed for foreign files; pre-flight 8 (CJK grep on shipped
  copy, clean); a UI-affecting batch additionally needs template 6's
  entry-point walk before merge.

### 3. Migration endpoints & upgrade paths

- **适用场合**: writing or carrying `migrations/<version>/` endpoint scripts
  (including cleanup migrations re-attached at each new endpoint); proving a
  module upgrades from the previous release, from an older customer-ish
  state, and re-upgrades idempotently.
- **必读技能**: odoo-development (migration scripts, verification pipeline,
  version awareness); themis-theme-sourcing section 10 for media-carrying
  modules (three upgrade paths; media rows must not double). Rule: a version
  bump must ship the cleanup migration again at the NEW endpoint dir - Odoo
  only runs an endpoint script when installed_version < endpoint <=
  new_version. [MBA-home learnings]
- **必用工具**: `tools/ci_upgrade_check.sh` (heavy-tier upgrade check, needs
  full checkout + compose db up); `upgrade-path.sh` 待固化 (canonical name
  for the same across release branches); `tools/check-manifests.py`.
- **验收命令与证据形式**: paste ci_upgrade_check.sh's **full output** - pass
  = all three legs (prev release head → HEAD, older ref → HEAD, re-upgrade)
  complete without ParseError; paste `ls <module>/migrations/` showing the
  endpoint dirs for the line; for media modules paste the preset/media row
  counts before and after the repeated upgrade (equal, themis-theme-sourcing
  section 10).

### 4. Theme media sourcing & pack entry

- **适用场合**: sourcing, licensing, or composing media for a theme or pack;
  merging a finished candidate batch onto the switchable test bench for the
  captain's batch review.
- **必读技能**: themis-theme-sourcing (the whole skill is the discipline:
  section 1 channels + helper scripts, 2 licences and `meta`, 3 batch-entry
  workflow, 4-6 media/palette requirements, 9 size budget, 10 pre-production
  verification, 11 portfolio balance); themis-series-layout section 3 (series
  modules carry ONE background resource per theme).
- **必用工具**: themis-theme-sourcing `scripts/media-search.py`,
  `scripts/media-fetch.py`, `scripts/cinemagraph.sh` (in the skill dir; copy
  next to the work); `bench-refresh.sh` 待固化 (refresh the candidate bench;
  today the manual procedure in main-home learnings: 商店与对外 评审台).
- **验收命令与证据形式**: paste the candidate table and the contact sheet;
  paste the motion measurement (>= 3/255, method in themis-theme-sourcing
  section 3); grep the provenance `meta` blob per asset (source/author/license
  present); paste actual sizes (video/image subtotals + module total <= 25 MB,
  section 9); state the portfolio slot filled ("fills dark + green", section
  11); nothing merges before the captain's batch sign-off (section 3).

### 5. Store assets (cover / screenshots / description page)

- **适用场合**: covers, screenshots, `static/description/index.html`, CE/EE
  badges, pricing notes, and listing registration for any module release.
- **必读技能**: odoo-store-assets (asset specs, description structure,
  compliance, registration); demo-video-recording (testreel recording,
  screenshots-from-frames, rule 10 dark mode for 17+; rough-cut-axi there is
  optional, only for takes with voice-over - English-only outward copy, no
  unreleased-feature leaks).
- **必用工具**: testreel (npm, per demo-video-recording); `assets-capture.sh`
  待固化 (capture cover/screenshot set from a real take's frames).
- **验收命令与证据形式**: real renders only - state the container/port the
  render came from; paste the take's contact sheet and `sips -g pixelWidth -g
  pixelHeight` (or ffprobe) for the cover (1920x960, 2:1) and the 5-7
  screenshots (~1800px, 16:9, English); pre-flight 8 CJK grep clean; paste a
  grep proving index.html has no JS and no external links except the
  canonical video; dark-mode rule honored for 17+ (demo-video-recording rule
  10); YouTube unlisted URL pasted and VIDEO_ID backfilled into the
  description page (demo-video-recording rule 11).

### 6. Live verification & bench refresh (incl. EE)

- **适用场合**: verifying a landed change on a real bench (CE or EE) before or
  after merge; refreshing a review bench to a new head; running the browser
  scenario suite.
- **必读技能**: odoo-environment (container lifecycle, filestore pairing,
  task boundaries); themis-theme-sourcing section 10 (verify at the real
  entry point for theme work); for UI/front-end changes walk the REAL entry
  (Action/menu → view) like a user before merge. [main-home learnings:
  测试与验收]
- **必用工具**: `tools/ui_lane.sh` (local browser-scenario lane, `ee` needs
  `EE_ADDONS`), `tools/ci_ui_scenarios.py` (scenarios S1-S4); `ee-up.sh`
  待固化 (EE bench: community image + enterprise branch exported from the
  mini clone; today manual at ports 8110-8113); `bench-refresh.sh` 待固化.
- **验收命令与证据形式**: paste the lane's `result.txt` (or scenario output)
  raw, S1-S4 pass lines visible; prove the bench is truly usable with an
  in-container DB query (e.g. preset count) or the Odoo log - not just
  container `Up`/login 200 (pre-flight 2); for UI changes paste the
  real-entry proof (screenshot taken after asserting the icons rendered,
  pre-flight 3); after asset changes: clear `/web/assets/%` → restart
  container → hard refresh [main-home learnings: 测试与验收]; when relevant
  paste the `/websocket` 101 handshake result (odoo-environment).
