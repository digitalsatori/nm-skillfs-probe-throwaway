---
name: demo-video-recording
description: "Record app-store demo videos for Odoo modules with testreel. Use when recording a demo video for compare-widget or any Odoo module release, writing or editing a testreel JSON recording definition, validating a recording before capture, uploading a demo video to YouTube, or producing cover variants and screenshots from a recording. Encodes the captain's hard requirements for demo content."
metadata:
  internal: true
---

# Demo video recording with testreel

These instructions are for an agent recording app-store demo videos for Odoo
modules in the firstmate fleet.
The tool is **testreel** (decided by the captain, 2026-09-02). Do not
substitute another tool without flagging the substitution and its dependency
footprint. For takes that contain voice-over, `rough-cut-axi` is an optional
local helper (see "Optional: rough-cut-axi for narrated takes" below);
regular editing of our no-audio material stays on the existing flows.

## MUST-READ: captain's demo requirements (before recording)

1. **No login segment.** Inject cookies or a `storageState` so the video
   starts post-login. Never record the login screen.
2. **Speed up selection.** Global `speed` ~1.4x + short `pauseAfter`; only
   operations worth watching keep long pauses.
3. **Demo every field type once**: char, text, integer, float, boolean,
   selection, many2one, date, many2many (one of integer/float is enough).
4. **m2m matrix**: toggle "Show tags as matrix" and tick matrix boxes on camera.
5. **Copy reference, not copy all.** Select records first, then copy the
   reference value. Never demo the global copy-all.
6. **Undo 3-4 times** after edits. Gotcha: once the undo stack is empty the
   Undo button is `disabled` and a strict click hangs ~30s - author exactly as
   many undo clicks as there are operations.
7. **Zoom only at three moments**: (a) the two "show option" clicks,
   (b) selecting the reference, (c) clicking the copy button. Nowhere else.
8. **Base video shows no editing** (editing is ECV's feature); record base with
   ECV uninstalled when possible.
9. **ECV video shows the full editing flow.**
10. **Dark mode on camera from Odoo 17 up.** Demo videos (and the screenshot
    sets cut from them) for 17/18/19 must show dark mode - a dark-mode segment
    in the video or at least one dark-mode screenshot in the store assets.
    15/16 exempt. If dark mode renders unreliably on a target version, include
    it only where it actually works and state that boundary in the recording
    report.
11. **After recording**: upload unlisted to YouTube with
    `~/dsh-test/yt-upload-req.py`, title includes the version; backfill the
    VIDEO_ID into the description page.
12. **Screenshots come from video frames** so stills and video always match;
    covers use a cover_variants.py-style overlay on a real frame.

## Tool: testreel

testreel is an npm package that drives Playwright: a JSON recording definition
becomes a polished screen recording with cursor overlay, window chrome, and
zoom animation.

Install (once per machine):

```bash
npm i testreel playwright
npx playwright install chromium
```

Core commands:

```bash
npx testreel validate recording.json    # validate without recording - always run first
npx testreel recording.json --dry-run   # dry run: no video, actions echoed
npx testreel recording.json             # record (webm default)
npx testreel recording.json --format mp4
npx testreel recording.json --format gif
npx testreel recording.json --headed    # visible browser, for debugging selectors
npx testreel recording.json --setup setup.json   # separate setup (pre-recording) file
npx testreel login https://host --save-state state.json  # interactive login -> storageState
```

Output goes to `./testreel-output/`: the video, PNG screenshots, and an
`output.json` manifest.

Bundled docs are at `node_modules/testreel/dist/docs/` after install
(recording-definitions.md, actions.md, authentication.md, cli.md).
The JSON schema is `recording-definition.schema.json` in the testreel repo
(github.com/sneg55/testreel); reference it from the definition file for IDE
autocomplete.

## JSON definition structure

Top-level keys (per `recording-definition.schema.json`):

| Key | Purpose |
|-----|---------|
| `url`, `viewport` | Target page and window size (1440x900 verified). |
| `cookies` / `storageState` / `localStorage` | Auth injection - see below. |
| `setup` | Steps run before recording starts (never captured on video). |
| `speed` | Global playback speed multiplier (>1 speeds the video up). |
| `chrome` | macOS-style window chrome around the page. |
| `background` | Padding, rounded corners, solid/gradient. |
| `outputFormat` | `webm` (default), `mp4`, `gif` - overridable via `--format`. |
| `steps` | Ordered list of actions. |

Step actions: `click`, `type`, `fill`, `keyboard`, `wait`, `hover`, `select`,
`clear`, `scroll`, `navigate`, `screenshot`, `zoom`.

Every step accepts:

- `pauseAfter` - milliseconds to hold after the step (default 500).
- `speed` - per-step speed multiplier overriding the global one.
- `timeout` - selector timeout (default 2000).
- `waitFor` - selector or `networkidle` to wait for before the action.

Auth without a login segment: inject a `session_id` cookie for the Odoo host
via `cookies`, or load a saved session with `storageState` (create it once
with `testreel login --save-state`). The recording then starts already
logged in.

Zoom: a `click` step accepts `"zoom": 2` (zoom into the target at 2x,
animated, then zoom back out); a standalone `zoom` action (`selector` or
`x`/`y` + `scale`) also exists. Consecutive zoomed clicks pan between targets.

String values support `${ENV_VAR}` substitution - use it for URLs and
secrets instead of committing them.

Example (abridged from the verified scout config):

```json
{
  "url": "http://localhost:8030/odoo/action-84",
  "viewport": { "width": 1440, "height": 900 },
  "outputFormat": "mp4",
  "speed": 1.4,
  "cookies": [
    { "name": "session_id", "value": "${ODOO_SESSION_ID}",
      "domain": "localhost", "path": "/" }
  ],
  "steps": [
    { "action": "wait", "ms": 2500 },
    { "action": "click", "selector": ".o_list_table tbody tr:nth-child(1) .o_list_record_selector input", "pauseAfter": 300 },
    { "action": "click", "selector": "td[data-fname='vceo'][data-res-id='1'] span.o_ecv_clickable", "pauseAfter": 1200 },
    { "action": "fill", "selector": ".o_ecv_editor input.o_input", "text": "45.50", "pauseAfter": 400 },
    { "action": "keyboard", "key": "Enter", "pauseAfter": 1200 },
    { "action": "click", "selector": ".o_ecv_star >> nth=0", "zoom": 2, "pauseAfter": 1000 }
  ]
}
```


## Pipeline gotchas (from scout runs)

- `--format mp4` post-passes through ffmpeg zoompan; zoom windows are
  expressed in pre-speed (1/speed) timestamps, so do not be confused when
  frame-sampling output.
- Record against a snapshot env, not a live module worktree - mounting live
  worktrees mid-recording caused version drift and broke ECV editability.
  Long-lived vs workspace-mounted demo instances: see odoo-environment
  ("Demos mount the workspace path, not a long-lived path").
- Keep the filestore paired with its DB when restoring demo environments -
  rule owned by odoo-environment (a fresh `/var/lib/odoo` against a reused
  DB corrupts asset serving).
- ECV edits write real data; a failed run leaves edits behind. Restore demo
  values via RPC after a botched take.
- **Verify every take with a 1 fps contact sheet before editing.** testreel
  reports all steps "successful" even when a click landed on a UI state that
  silently no-ops (e.g. a dropdown item below the viewport fold, a menu that
  re-rendered between query and click). Generate one image per second and
  read it before cutting:
  `ffmpeg -i take.mp4 -vf "fps=1,scale=300:-1,tile=10x5" -frames:v 1 sheet.png`.
  Every wasted edit pass downstream costs more than this one command.
  Applicability: not just a viewport-fold issue - any click can no-op
  silently, so run the sheet for every take even when the page layout is
  simple and nothing sits below the fold.
- Prefer `setup`-block page logins over hand-crafted cookie injection
  (same no-login-segment result, but the session is earned through the real
  page). On multi-db Odoo, log in at `/web/login?db=<name>` or you land on
  the database selector.

## Optional: rough-cut-axi for narrated takes (not the main path)

**Optional local helper, not the main path**: our demo/promo material has no
audio track (on-screen English text only - no narration, no TTS), so regular
editing stays on the existing flows (clapper section below, or ad-hoc ffmpeg
cutting as in the module repos' `postprocess.sh`). Reach for rough-cut-axi
only when a take does contain voice-over. It opens raw takes into a project
without modifying the source files; the project lives under
`~/.rough-cut-axi/projects/<project-id>` and every edit stays a reviewable
`timeline.json` in the project until it is applied. Project directories are
local working state - never commit them into any repository.

No ElevenLabs key is needed unless you run the `transcribe` step (step 2
below - the only step that wants a key, via `rough-cut-axi auth elevenlabs
--api-key <key>`); without a key everything else works unchanged.

Workflow:

1. `rough-cut-axi open <video-files...>` - open the raw takes into a project;
   originals are not modified.
2. `rough-cut-axi transcribe <project-dir>` - produce the transcript (the
   only step that needs the ElevenLabs key).
3. Review loop - `rough-cut-axi snapshot <project-dir>` hands the agent the
   timeline context (`--range <start:end>` narrows it by output time);
   `rough-cut-axi server [--port <port>]` serves the local editor so a human
   reviews in the browser; `rough-cut-axi poll <project-dir>` reads the queued
   prompts/feedback, and `--agent-reply <text>` records the agent's reply.
4. `rough-cut-axi apply <project-dir> --ops <ops.json>` - apply only safe /
   approved edit operations (a JSON ops file); `--approved` is required only
   for broad plans of more than three operations.
5. `rough-cut-axi render <project-dir>` - ffmpeg render of the approved
   timeline; writes `renders/final.mov` (ProRes/PCM editing handoff) as the
   preview/final cut. Publish per MUST-READ rule 11 (unlisted YouTube upload,
   VIDEO_ID backfill).
6. `rough-cut-axi end <project-dir>` - close the project when done.

## Composing highlight reels with clapper (recording -> film)

Main path for regular editing of our no-audio takes (rough-cut-axi is only
for narrated material): when the deliverable is an edited highlight video
(captions, music, title cards) rather than a single continuous take, the
clapper skill composes testreel output cleanly:

- Copy the raw takes into the clapper project's `public/` and map each scene
  to a take segment with clapper's deterministic `<Video src startFrom>`:
  scene duration defines how much of the take plays, `startFrom` (seconds)
  picks the entry point. Captions/branding go in `data.ts`, never inline.
- Record takes at `speed: 1.4` so UI work feels brisk, then keep
  `playbackRate: 1` in the film - cuts give the rhythm, not speed ramps.
- Map take timestamps BEFORE writing scenes: one frame per second of each
  take (the contact sheet above), note the second each action lands, and
  put the numbers in the declarative scene plan (`data.ts`). Re-probe after
  ANY re-record - timestamps shift with server load - so a re-record is a
  timestamp patch, not a re-edit.

## Where recording definitions live

Store testreel JSON definitions in the module repo's root `assets/record/`
directory (e.g. `assets/record/record_demo_19.json`), never inside the Odoo
module directory itself - they are release-asset tooling, not shipped code.
Existing examples: the compare-widget repo's `assets/record/`
(`record_demo.py`, `cover_variants.py`, `postprocess.sh`).
