---
name: odoo-environment
description: "Probe: minimal description."
metadata:
  internal: true
---

# Odoo environment setup and operations

Instructions for an agent setting up or operating Odoo test/demo environments
inside the firstmate fleet. Environment work is its own discipline - it does
not need the coding standards in odoo-development.

## Directory layout convention

All Odoo project demo/Docker test code lives under `~/odoo-projects/<project>/`:

```
~/odoo-projects/<project>/
├── <version>/   # per-version module clones (15.0/16.0/17.0/18.0/19.0)
└── env/         # per-version docker-compose files (env/15.0/ etc.)
```

- Per-version clones support running multiple versions side by side.
- Clean containers, never delete code directories - environments can be
  relaunched any time.
- Test server ports: 15=8025 / 16=8026 / 17=8027 / 18=8028 / 19=8029.

## Mounting module sources

Add a module to a container's addons path by adding a read-only bind mount in
the project's docker-compose.yml `odoo` service volumes, then recreate the
container:

```yaml
volumes:
  - /Users/tony/odoo-projects/<project>/<version>/<module>:/mnt/extra-addons/<module>:ro
```

After editing compose: `docker compose -f <path> up -d` (recreates the odoo
container so the new mount takes effect).

## Local fast smoke test

Run a module's own tests locally for fast feedback (catches XML errors, view
registration failures, test failures):

```bash
docker compose -f <project>/docker-compose.yml exec odoo \
  odoo --db_host=db --db_user=odoo --db_password=odoo \
  -d test_smoke_$(date +%s) -i <module_name> \
  --test-tags=/<module_name> --stop-after-init
```

Acceptance criteria:
- Module installs without ERROR or ParseError in logs
- All module tests execute and pass
- No `Element odoo has extra content` or `Invalid view type` errors
- No missing template or asset compilation errors in server log

## Container lifecycle

- Restart: `docker compose -f <path> restart odoo` (or `docker restart <container>`)
- Recreate after compose change: `docker compose -f <path> up -d`
- Clean up test residue: `docker compose --profile test down --volumes`
- Fresh image: `docker compose build --pull odoo` (a stale local odoo:<version>
  image can reject `--with-demo` or fail with version-mismatch view errors)
- Keep the filestore paired with its DB: restoring a fresh `/var/lib/odoo`
  (or an emptied data dir) against a reused DB corrupts asset serving and
  silently breaks attachment/media links. Restore DB and filestore from the
  same backup, or rebuild both together.

## Verification lanes: use the repo's lane scaffolding

Real-machine or container verification always runs on the target repo's
existing lane scaffolding under `tools/` - check there first and follow the
tool's own `--help`; never hand-roll a container flow. Judge the lane healthy
by an in-container DB query or DB errors in the Odoo log - container `Up` or a
login page 200 is not "usable". New pitfalls are written back into that tool,
not left in a task directory.

## Upgrading modules with cross-module dependencies

When a module's new code references models/schema from another module (e.g. a
new settings view referencing a sibling module's session model), upgrade in the
right order or the dependent module fails to load:

```bash
odoo --db_host=db --db_user=odoo --db_password=odoo -d <db> \
  -u shine_ai_atlas -u shine_ai_mason
```

- **Order matters**: `-u` the upstream (dependency) module first, then the
  dependent module, then restart. Upgrading only the dependent module against a
  DB that hasn't loaded the new upstream schema fails with `ParseError` +
  `Failed to load registry` (e.g. `Model shine.ai.atlas.session has no table`).
- **Modular families upgrade together** (Odoo 19 `ir_model_inherit`): after a
  family is split into several modules, upgrade them all in one command —
  `-u shine_ai_atlas -u shine_ai_mason -u shine_ai_mason_studio`. Upgrading a
  single child (`-u shine_ai_mason_studio` only) fails on the parent's new
  abstract model with an `ir_model_inherit` error. This is the same rule as
  above: cross-module dependency upgrades must run together and/or in order,
  never one module alone.
- **`--http-port=8099` inside the container**: when running upgrade/test CLI in
  the container, the image's `--no-http` does not work and the default 8069 is
  already taken inside the container, so pass `--http-port=8099` explicitly.

## Demos mount the workspace path, not a long-lived path

A demo instance that mounts the disposable workspace path dies when that
workspace is returned (the instance loses its code). After landing, rebuild the
container from the main repository path so it survives: `docker compose -p
<proj> up -d`. Named volumes preserve the DB and config, so only the code mount
path changes — no data loss.

## WebSocket `/websocket` and reverse proxy

Odoo serves `/websocket` as an ordinary HTTP route (`bus/controllers/
websocket.py`), picked up by whatever server is running:

- **`workers=0` (threaded mode)** — the ThreadedServer serves long connections
  on the SAME port as normal requests (8069). No extra port, no proxy needed.
- **`workers>0` (prefork + gevent)** — the gevent server listens on
  `gevent_port` (default **8072**, `service/server.py` `config['gevent_port']`),
  so `/websocket` is on a separate port and you MUST front it with a proxy that
  forwards `/websocket` to 8072 and passes `Upgrade`/`Connection`.
- Defaults: `--workers` default is `0` (`tools/config.py`), `--gevent-port`
  default `8072`.
- Odoo itself rejects a WebSocket handshake without an `Origin` header.

### Test/demo environment convention: threaded mode, no proxy

- **Decision**: every test/demo environment uses `workers=0` (threaded mode)
  and NO proxy. Threaded mode serves `/websocket` on the same port as normal
  requests, so a proxy is pure overhead.
- Only a multi-worker (process) environment needs a proxy forwarding
  `/websocket` to `gevent_port` (8072); threaded mode serves it on 8069 directly.
- **Self-check**: send an Upgrade handshake to the environment's `/websocket`
  from the host and get a **101** — a 101 proves the long connection works, no
  need to inspect whether a proxy is present.

## Environment task boundaries

Environment setup tasks only need the environment ready (login 200, module
loaded, sources mounted at the right branch) - NOT functional verification of
the modules. Functional testing is a separate task.
