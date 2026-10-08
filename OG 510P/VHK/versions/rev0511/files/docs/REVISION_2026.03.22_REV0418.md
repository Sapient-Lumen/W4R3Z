# Revision 0418 — selected-macro work ticket for the warm X11/i3 lane

Revision 0418 makes the fused resident stack more useful to the private-LLM and
operator loop without widening Linux scope. `stack_state_json.sh` now carries
`primary_macro_work_ticket`, a selected-macro handoff that chooses one bounded
lane from the already-fused recorder, cleanup, replay, acceptance, warm-runtime,
and execution tickets.

## What changed

- Added `primary_macro_work_ticket` to the fused stack JSON and text summary.
- Added helper metadata so `macro_author_queue_json` and `next_action_json` can
  advertise the selected macro work-ticket stage, source ticket, status, route,
  and recommended command.
- Added focused end-to-end coverage in
  `tests/test_primary_macro_work_ticket_cli.py` for four selected-macro states:
  recorder-first, ready-for-signoff, runtime-repair-before-dispatch, and clean
  execution.
- Tightened README/runtime/LLM docs so the repo now says explicitly that the
  flagship stack should answer not only *is the resident runtime honest?* but
  also *which selected-macro lane comes next?*

## Why it matters

This keeps the i3/X11-first control plane closer to a one-read authoring loop.
The private LLM no longer has to re-derive recorder-versus-cleanup-versus-replay
priority from multiple sibling tickets on every turn; the stack still carries
those detailed tickets, but it now also carries one bounded answer for the next
selected-macro lane.
