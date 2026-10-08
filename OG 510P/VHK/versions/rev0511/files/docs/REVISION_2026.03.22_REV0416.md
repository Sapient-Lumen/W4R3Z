# REV0416 — restart receipt for the resident X11/i3 runtime

Revision 0416 adds a generated `bin/restart_runtime_json.sh` helper for the flagship warm-runtime lane.

## What changed

- added `src/vhk/project/runtime_restart_receipt.py`
- generated `bin/restart_runtime_json.sh` beside `reload_runtime_json.sh`
- changed warm-runtime restart tickets to recommend the new helper instead of raw `systemctl` command strings
- exposed the helper in `control-plane.json`, fused stack helper metadata, and recommended entrypoints
- tightened docs so restart is now treated as a first-class machine-readable repair surface for the resident daemon

## Why it matters

The repo already knew when the daemon had to be restarted from the current X11/i3 session, but the recommended route was still an opaque shell chain. This revision makes restart a bounded control-plane actuation with a receipt that a private LLM or operator can inspect without guessing whether the daemon actually came back on the right desktop session with the expected watcher/runtime contract.
