# REV0396 — explicit flagship and LLM control contracts in the warm stack

## What changed

- `control-plane.json` now carries three explicit machine-readable contracts for the generated i3/X11 warm stack:
  - `product_contract`
  - `llm_authoring_contract`
  - `session_activation_contract`
- `product_contract` now makes the flagship lane explicit instead of leaving it spread across README prose:
  - i3 on X11 as the primary target
  - session-bound long-lived user service as the preferred runtime shape
  - thin emit -> busd -> execution dispatch as the hot path
  - record -> cleanup -> replay -> inspect -> refine as the preferred authoring loop
  - broad Wayland / portal-first / off-lane adapter work as demoted or vaulted
- `llm_authoring_contract` now makes the private-LLM path explicit in one read:
  - preferred project-triage entrypoints
  - preferred per-macro entrypoints
  - explicit edit/review/execute loop ordering
  - checked-dispatch vs direct-run policy
  - source/review mutation guardrails
- `session_activation_contract` now carries the X11 session-activation sync posture that the warm runtime depends on, including bridge variables and the preferred `dbus-update-activation-environment --systemd ...` command
- `stack_state_json.sh` now mirrors those three contracts under `control_plane` so the fused live runtime snapshot keeps both the runtime truth and the product/LLM/session contract in one place
- rewrote `docs/ARCHITECTURE.md` around the real i3/X11-first runtime shape instead of the earlier generic scaffold story
- added `docs/FLAGSHIP_RUNTIME_SPEC_2026.03.21.md` as a short explicit spec for the mainline product lane
- tightened `README.md` so the new flagship/runtime spec and architecture docs are first-class start points

## Why this matters

The repo already had the right direction, but too much of the real product contract still lived in scattered narrative docs and implied wrapper behavior.

This revision moves the most important decisions onto the actual generated control plane. A private LLM or operator can now inspect one machine-readable artifact and recover:

- what VHK is primarily for
- which runtime shape is preferred
- how source editing and review should proceed
- how warm dispatch differs from direct runs
- which session-environment sync step belongs to the X11 lane

That makes the repo easier to steer, easier to automate, and less likely to drift back into broad Linux-generalized ambiguity.

## Tests

- `python -m py_compile src/vhk/cli.py`
- `test_gen_i3_busd_stack_writes_flagship_runtime_handoff`
- `test_generated_stack_state_json_carries_fused_control_plane`
