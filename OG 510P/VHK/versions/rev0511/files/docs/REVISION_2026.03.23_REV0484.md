# REV0484 — resident control plane install-lane ticket

This revision adds a compact installed-lane handoff module for the flagship i3/X11 stack.

## Added
- `src/vhk/project/i3_x11_flagship_stack_install_handoff.py`
- `tests/test_i3_x11_flagship_stack_install_handoff.py`
- `docs/DECISION_2026.03.23_RESIDENT_CONTROL_PLANE_INSTALL_LANE_TICKET.md`

## Why
The current stack can install, verify, and repair the warm resident lane, but the control plane still lacks one bounded installed-lane ticket that a private LLM can consume directly.

## What it standardizes
- `install_not_deployed`
- `repair_required`
- `start_recommended`
- `active`

## Next cut
Thread the new installed-lane ticket into `gen-i3-busd-stack`, `next_action_json.sh`, and `stack_state_json.sh` without regressing the current resident-runtime control plane.
