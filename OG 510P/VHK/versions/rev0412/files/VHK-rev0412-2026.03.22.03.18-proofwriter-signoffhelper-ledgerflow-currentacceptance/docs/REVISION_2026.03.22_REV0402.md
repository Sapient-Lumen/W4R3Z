# Revision 0402 — reload repairs now produce receipts

Date: 2026-03-22

## What changed

- added `src/vhk/project/runtime_reload_receipt.py`
- the internal `vhk.runtime.probe` acknowledgment now carries `runtime_state`
  with `runtime_epoch_id`, `reload_count`, `last_reload_reason`, and timestamps
- generated `bin/reload_runtime_json.sh` now:
  - probes the resident daemon before reload
  - emits the bus reload event
  - probes again until it can report a bounded reload receipt
- `warm_runtime_ticket` now recommends `./bin/reload_runtime_json.sh` for
  resident project-contract drift instead of a blind `reload && check` chain
- fused stack helper metadata now mirrors the daemon epoch/reload witness
- added targeted tests for runtime reload receipts and updated stack generation
  expectations

## Why it matters

A warm X11/i3 daemon can stay alive across many source edits. Once the repo was
able to detect stale in-memory project state, the next practical gap was repair
truth: after asking for a reload, could the control plane actually tell whether
that reload was observed?

This revision makes reload a first-class, machine-readable actuation surface. A
private LLM can now request a reload and get one bounded answer back:

- reload was observed and the daemon is now in sync
- contract is in sync but no new epoch was observed
- reload was observed but contract is still stale
- reload could not be emitted or verified
