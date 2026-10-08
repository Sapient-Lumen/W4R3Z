# Revision 0282 — mpv JSON IPC pack

This revision turns the first app-native media lane into a concrete export.

## Added

- `vhk gen-mpv-pack`
- `src/vhk/project/mpv_pack.py`
- `tests/test_mpv_pack_cli.py`
- planner command wiring so mpv-targeted app-native lanes now point at a real pack

## What the new pack writes

- `vhk.mpv.routes.yml` — reviewable route catalog for mpv-targeted macros with inferred JSON IPC actions
- `vhk.mpv.commands.json` — machine-readable command ledger and skipped-route list
- `bin/*.sh` — thin wrappers around local mpv JSON IPC using `socat` / `nc -U`
- `README.md` — operator-facing explanation of assumptions and limits

## Design stance

This pack stays deliberately conservative:

- it only exports macros that already target mpv
- it only emits routes when the macro name / description / binding keys imply a reviewable command such as pause, stop, next, previous, seek, volume, mute, or fullscreen
- it does not pretend to discover a live socket path; helpers default to `${XDG_RUNTIME_DIR:-/tmp}/mpv.socket` unless the operator overrides `MPV_SOCKET`
