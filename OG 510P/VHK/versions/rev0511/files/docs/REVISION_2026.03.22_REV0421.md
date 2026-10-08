# Revision 0421 — selected-macro execute/signoff handoff

This revision keeps VHK centered on the i3/X11 resident-runtime lane and closes the next private-LLM control-plane gap.

## What changed

- Extended `primary_macro_work_ticket` with:
  - richer `entrypoints` for `warm_runtime_checked`, `warm_runtime_gate`, `direct_run`, `dispatch_history`, and `record_runtime_acceptance`
  - `execution_handoff` summarizing preferred execution mode, checked-dispatch readiness, and runtime-signoff status
  - matching signal fields so thinner consumers do not need to reopen the author loop just to recover execution state
- Extended macro contract/authoring surfaces so `record_runtime_acceptance` is a first-class generated-stack example instead of an out-of-band command
- Updated human summaries so `stack_state.sh` and `primary_macro_work_ticket.sh` print the new execute/signoff handoff fields
- Added focused test coverage for the new selected-macro handoff and contract surface

## Why it matters

The selected-macro ticket is now a real author→review→execute handoff instead of a source/review pointer that still forced a second helper hop to find the actual checked-dispatch, direct-run, or acceptance-write command.
