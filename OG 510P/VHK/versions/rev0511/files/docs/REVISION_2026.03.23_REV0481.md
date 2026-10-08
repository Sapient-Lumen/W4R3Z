# Revision 0481 — shipped startup bridge helpers into the flagship i3/X11 stack

This revision turns the previously separate startup-bridge contract into actual flagship-stack artifacts.

## What changed

- `vhk gen-i3-busd-stack` now emits the missing session/startup bridge helpers directly into the generated stack:
  - `bin/sync_session_activation_env.sh`
  - `bin/verify_session_targets.sh`
  - `bin/verify_session_readiness.sh`
  - `bin/verify_startup_handoff.sh`
  - `bin/start_user_session.sh`
  - `autostart/<unit>.desktop`
- `control-plane.json` now carries `flagship_startup_bridge_contract` and `flagship_startup_bridge_summary` alongside the existing product/runtime/LLM contracts.
- The control-plane script manifest now classifies the new bridge/probe surfaces explicitly instead of leaving them outside the machine-readable operator/LLM story.
- The runtime-repair entry flow now uses the same bridge helpers it claims to depend on: verify readiness, sync activation environment, then reload/restart/start as needed.

## Why

The repo already had a good startup-owner/session-bridge contract on paper, but the flagship stack still only shipped the observability half of that story.

That left an awkward gap:

- the warm stack could report startup-owner drift
- but it did not export the small helper surfaces needed to resync session variables, probe readiness, and perform the bounded login/start bridge that the docs were already recommending

Revision 0481 closes that gap without widening the product lane.

## Product posture

This remains explicitly i3/X11-first:

- `graphical-session.target` stays the primary startup owner
- XDG autostart stays a fallback bridge, not a co-equal default owner
- ad hoc CLI runs remain available, but the resident user-service lane is the optimized path
- the control plane keeps the private-LLM story bounded to explicit source/edit/inspect/actuate surfaces

## Tests

- `pytest -q tests/test_i3_x11_flagship_startup_bridge.py tests/test_i3_x11_flagship_stack_bridge_pack.py tests/test_i3_busd_stack_cli.py`
