# STATUS

## Phase

Scaffold-plus-plumbing complete.

## What exists

- docs and memory files
- Chromium MV3 extension with background coordinator
- side panel operator surface
- generic adapter registry with Claude as first real adapter
- Python native host with local UNIX-socket broker
- CLI commands for broker status, watch, request, read-prompt, read-latest, write-prompt
- Nix dev shell
- Chromium profile launcher and profile manager
- native-host manifest installer template and helper
- Python tests for protocol/state/broker paths

## What is proven in-container

- Python modules compile
- Python tests pass
- extension TypeScript typechecks with local stub typings
- extension build emits JavaScript under `extension/dist/`
- broker-backed `socket-status` smoke test works against a temporary local broker
- release packaging script creates a zip archive

## What is not yet proven against a real browser

- end-to-end native messaging round-trip in live Chromium with a real unpacked extension ID
- side-panel live interaction inside Chromium
- live Claude.ai DOM extraction against the current production UI
- `prompt.write` and `prompt.submit` behavior on Claude.ai
- transcript delta quality and noisiness on long pages

## Recommended next session target

Get `health.ping`, `socket-status`, and `read-prompt --wait` working end to end with a real unpacked extension ID and native-host manifest installed into an isolated Chromium profile.

## After that

- save Claude DOM fixtures from a live page
- improve Claude selector scoring
- add `prompt.submit` CLI command
- add a second adapter example to pressure-test the generic core
