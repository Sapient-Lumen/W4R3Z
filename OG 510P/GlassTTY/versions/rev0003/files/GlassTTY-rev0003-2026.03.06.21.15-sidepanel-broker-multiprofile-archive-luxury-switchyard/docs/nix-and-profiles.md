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
- `scripts/glasstty-profile.sh open <name> [url-or-extra-args...]`
- `scripts/launch-chromium-profile.sh <name> [extra args...]`

## Recommended practice

Keep at least two profiles:
- `main` for normal interactive work
- `lab` for experiments that may destabilize extension state
