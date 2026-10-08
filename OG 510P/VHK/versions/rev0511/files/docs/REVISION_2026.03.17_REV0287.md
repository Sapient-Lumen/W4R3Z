# Revision 0287 — daemon-truth input lanes

This revision hardens one of VHK's most Linux-specific seams: daemon-backed Wayland helper lanes.

## What changed

- added `probe_dotoold()` to the doctor layer so VHK can distinguish:
  - one-shot `dotool` availability
  - `dotoolc` present but no proven daemon
  - an actually active `dotoold` lane
- extended `vhk doctor --json` with a new `dotoold` section
- tightened the capability matrix so Wayland text/pointer injection now:
  - recommends `dotoolc` only when the daemon-backed lane is actually ready
  - falls back to one-shot `dotool` honestly when that is the only confirmed route
  - emits explicit notes when `dotoolc` is installed but `dotoold` is not proven
- extended doctor advice so operators get a concrete warning when `dotoolc` is present without a ready daemon
- repaired a separate readiness-pack wiring gap while working in this area:
  - `gen-readiness-pack` now passes its captured host snapshot through to the writer again
  - readiness output once more reflects real host state instead of drifting to `unknown`
- added focused tests for:
  - `dotoolc` without daemon readiness
  - `dotoold` active with `dotoolc` preferred
  - readiness-pack regression coverage
- updated:
  - `README.md`
  - `docs/INPUT_BACKENDS.md`
  - `docs/RESEARCH_2026.03.17_DAEMON_READINESS_AND_INPUT_LANES.md`

## Why this matters

A Linux-native automation tool cannot afford to collapse these into the same story:

- “the binary exists”
- “the kernel permissions are okay”
- “the long-lived helper lane is actually ready for repeated playback”

That distinction matters on real Wayland hosts because:

- `wtype` depends on compositor protocol exposure
- `ydotool` depends on socket reachability and `/dev/uinput` policy
- `dotoolc` depends on a daemon lifecycle that is easy to assume and easy to forget

VHK should therefore keep **daemon truth** visible in doctor/readiness/planning output instead of quietly treating every helper binary as production-ready.

## What passed

- `tests/test_doctor_cli.py`
- `tests/test_input_backend_overrides.py`
- `tests/test_readiness_pack_cli.py`
- `tests/test_route_selection_pack_cli.py`
- `tests/test_session_fit_pack_cli.py`
- `tests/test_target_route_pack_cli.py`
- `tests/test_window_contracts.py`
- `tests/test_host_contract_pack_cli.py`
- `tests/test_capability_audit_pack_cli.py`
- `tests/test_claim_pack_cli.py`
- `tests/test_promotion_pack_cli.py`

## Remaining honest gap

- runtime backend auto-selection still prefers `dotoolc` from tool presence alone; doctor/readiness now tell the truth, but a future runtime pass should use the same daemon-readiness knowledge when choosing helper clients automatically
- `ydotool` and `dotool` readiness are still modeled differently (`socket` vs `service`) because the upstream ecosystems are different; a future “input route dossier” surface could unify them for operators without pretending they work the same way
