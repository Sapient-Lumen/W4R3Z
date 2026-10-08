# REV0296 — promotion verification lanes

Date: 2026-03-17
Revision: rev0296

## What changed

This revision adds a new planner/review surface: `promotion_verification_plan`.

VHK already knew:

- which Linux-native input lane should own a promoted surface
- which activation route wakes it up and keeps it alive
- which operator-control lane owns status/reload/log loops
- which recovery lane owns rollback and re-entry

The missing Linux-native truth was the one operators actually need before they trust release language:

- what exact smoke/proof loop demonstrates that the promoted surface is alive on the target desktop?

`plan-project` now emits `promotion_verification_plan`, and the same surface is threaded into:

- `vhk plan-project` human output
- `gen-promotion-pack`
- `gen-capability-audit-pack`
- `gen-operator-pack`

## New surface

Each promoted surface now carries:

- `verification_posture`
- `primary_verification_lane_id`
- `verification_gate_ids`
- `smoke_loop`
- `live_probe`
- `acceptance_boundary`
- `proof_surfaces`
- `acceptance_checks`
- related host requirements, commands, cautions, and evidence

## Why this matters

Linux-native shipping often fails in a very specific way: the artifacts generate cleanly, but the real user-visible surface is still dead.

Examples:

- a text package exists, but the text daemon is not actually serving the active config/runtime tree
- a remapper config renders, but no live input-event proof has been captured yet
- a portal session exists, but it never reaches the activated/active state that matters in practice
- a watcher service is running, but no representative event has actually flowed through it
- a launcher entry exists, but nobody has verified that it is visible and wakes the intended downstream macro path

`promotion_verification_plan` keeps those proof loops explicit and attached to the promoted surface.

## Main code paths touched

- `src/vhk/project/strategy.py`
- `src/vhk/cli.py`
- `src/vhk/project/promotion_pack.py`
- `src/vhk/project/capability_audit_pack.py`
- `src/vhk/project/operator_pack.py`

## Tests exercised

Focused suites covering planner/promotion/audit/operator and adjacent packs were rerun after the change.
