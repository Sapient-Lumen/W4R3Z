# REV0373 — stack state inlines primary macro contract

## What changed

- `stack_state_json.sh` now opens `macro_contract_json.sh <primary-macro>` when the author queue names a primary macro.
- The fused stack payload now carries that under `primary_macro_contract`.
- `sources.helpers.macro_contract_json` now mirrors key contract facts for fast triage:
  - `primary_macro_name`
  - `macro`
  - `interactive_inputs`
  - `desktop_target_source_id`
  - `prompt_step_count`
- `stack_state.sh` now prints the selected macro's contract macro name, target-source id, and derived preferred execution mode.
- `stack_state_json.sh` now runs subordinate helpers with stdin closed so the resident control plane stays non-interactive under failure pressure.

## Why this matters

The fused stack snapshot already carried the primary macro's checked-dispatch gate and latest matching run, but callers still had to reopen `macro_contract_json.sh <macro>` to see the selected macro's desktop target and generated invocation wrappers. This revision keeps the i3/X11-first control plane closer to a true one-read inspect → decide → execute handoff.

## Tests

Focused generated-stack tests cover:
- fused runtime board + primary contract
- fused primary checked gate + primary contract
- direct-run-only contract projection for the selected macro
