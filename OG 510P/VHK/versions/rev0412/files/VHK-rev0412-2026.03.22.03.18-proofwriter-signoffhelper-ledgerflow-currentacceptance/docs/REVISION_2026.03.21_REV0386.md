# REV0386 — bounded live probe observation for the selected macro

## What changed

- `stack_state_json.sh` now derives `primary_macro_probe_observation` for the author-queue-selected macro
- the new selected-macro surface carries:
  - `status_id`
  - `source_id`
  - `probe_id`
  - `observation_source_id`
  - bounded `observed` facts
  - expected desktop target details
  - `inspect_commands`
  - a first `recommended` inspect command
- `sources.helpers.macro_author_queue_json` now mirrors selected-macro probe-observation ids and command
- `sources.helpers.macro_dispatch_gate_json` now mirrors selected-macro probe-observation ids
- `stack_state.sh` now prints selected-macro probe-observation status, probe id, source, summary, and command
- tightened `README.md`, `docs/LLM_AUTHOR_LOOP_CONTROL_PLANE.md`, and `docs/I3_X11_RUNTIME_STACK.md` around the new one-read X11/i3 observability lane

## Why this matters

The resident control plane already knew how to name blocker classes and repair commands, but that still left a practical gap during X11/i3 mismatch work: callers often had to reopen report or trace output just to see the one live observation that explained the refusal.

This revision keeps the selected-macro lane bounded while making it more useful. A private LLM or operator can now read one fused stack snapshot and see both the expected desktop target and the freshest observed mismatch sample before deciding whether to revise selectors, rerun, or retry checked dispatch.

## Tests

- `test_gen_i3_busd_stack_writes_flagship_runtime_handoff`
- `test_generated_stack_state_json_carries_primary_macro_repair_recipe`
- `test_generated_stack_state_json_carries_blocker_aware_desktop_target_recipe`
- `test_generated_stack_state_json_carries_primary_macro_probe_observation`
