# Revision 0288 — runtime-truth backend chooser

This revision closes the main honest gap left by revision 0287: runtime input
selection now consumes the same helper/protocol truth that doctor already knew.

## What changed

- made Wayland keyboard/pointer backend auto-selection probe-aware in
  `src/vhk/system/input.py`
- runtime chooser now treats these as different states instead of flattening
  them into “binary exists”:
  - `dotoolc` with a daemon known ready
  - `dotoolc` with daemon state unknown
  - `dotoolc` with daemon explicitly known inactive/failed
  - `ydotool` with a reachable daemon socket
  - `ydotool` with socket state unknown
  - `ydotool` with socket explicitly missing/unreachable
  - `wtype` with virtual-keyboard support confirmed
  - `wtype` with virtual-keyboard support unknown
  - `wtype` with virtual-keyboard support explicitly absent
- updated `wtype` fallback paths (`Key`, `KeyDown`, `KeyUp`, `TypeText`) so they
  also prefer readiness-aware helper fallbacks instead of blindly retrying any
  helper seen on `PATH`
- added focused runtime tests for:
  - skipping `dotoolc` when daemon inactivity is actually known
  - skipping `wtype` when virtual-keyboard absence is actually known
  - skipping `ydotool` when socket absence is actually known
  - preserving command-shape tests by making runtime facts explicit in the test
    harness
- updated docs:
  - `README.md`
  - `docs/INPUT_BACKENDS.md`
  - `docs/PLAN_2026.03.17_LINUX_NATIVE_AHK_PARITY.md`
  - `docs/RESEARCH_2026.03.17_RUNTIME_SELECTION_FROM_CAPABILITY_PROBES.md`

## Why this matters

A Linux-native automation system cannot stop at “planner honesty” if execution
still quietly makes different assumptions.

This patch makes VHK more coherent:

- doctor says what is actually ready
- readiness/host-review packs preserve that truth
- runtime now follows the same truth when choosing helper lanes

That coherence is strategically important because Linux automation failure is
very often **not** about missing features. It is about hidden mismatches between:

- protocol availability
- daemon lifecycle
- permission state
- what the runtime guessed from PATH

## What passed

- `tests/test_input_backend_overrides.py`
- `tests/test_dotool_integration.py`
- `tests/test_wayland_backends.py`
- `tests/test_doctor_cli.py`
- `tests/test_plan_project_cli.py`
- `tests/test_lint_project_cli.py`
- `tests/test_readiness_pack_cli.py`
- `tests/test_runtime_pack_cli.py`
- `tests/test_setup_pack_cli.py`
- `tests/test_portability_pack_cli.py`

## Remaining honest gap

- runtime still caches probe results per environment signature for pragmatism;
  a future pass could add explicit cache invalidation or a lightweight session
  dossier refresh command for long-lived operators who start/stop daemons while
  VHK is already running
- `dotool` and `ydotool` remain separate ecosystems with different readiness
  surfaces (service vs socket). A future unified input-lane dossier could make
  those differences more reviewable without pretending they are the same tool
