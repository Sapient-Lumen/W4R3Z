# Nix and profile notes

GlassTTY assumes a Nix-friendly workflow but does not hardcode Nix into the protocol.

## Development shell

`flake.nix` provides a shell with:
- Python
- pytest
- Node.js
- TypeScript tooling
- Chromium
- jq/yq/rg/fd/git/zip/unzip

## Profile model

Profiles live under:

```text
$GLASSTTY_HOME/profiles/<name>
```

This makes it easy to keep:
- a main operator profile
- an experiment profile
- a future Playwright/automation profile

## Scripts

- `scripts/glasstty-profile.sh list`
- `scripts/glasstty-profile.sh info <name> [--pretty]`
- `scripts/glasstty-profile.sh open <name> [launch options or url-or-extra-args...]`
- `scripts/launch-chromium-profile.sh <name> [--remote-debugging-port PORT|auto] [--headless] [extra args...]`
- `python scripts/profile-report.py --pretty`

## Recommended practice

Keep at least two profiles:
- `main` for normal interactive work
- `lab` for experiments that may destabilize extension state

## Launch metadata

Each GlassTTY-managed profile now records `glasstty-profile.json` in the profile directory before Chromium starts. That file captures the browser executable, inferred browser family metadata, whether the unpacked extension was loaded, the most recent start URL, extra Chromium args, and whether remote debugging was requested. If that saved browser path is missing later, GlassTTY can now either fail strictly with an actionable message or explicitly replay the same profile through the currently discovered browser via `glasstty-profile.sh reopen --allow-discovered-browser-fallback`.

When Chromium writes `DevToolsActivePort`, `scripts/glasstty-profile.sh info <name> --pretty` and `python scripts/profile-report.py --pretty` will surface it beside the saved launch metadata. They now also probe whether the remembered endpoint is still listening on localhost and emit a ready-made `resume-proof` command, which makes CDP archaeology easier after an interrupted smoke run because the profile itself now remembers both the user-data-dir boundary and whether the debugging lane is still alive.

For an ephemeral debug port that still satisfies current Chrome security guidance around non-default user-data directories:

```bash
./scripts/glasstty-profile.sh open lab --remote-debugging-port auto http://127.0.0.1:8765/
./scripts/glasstty-profile.sh info lab --pretty
```
