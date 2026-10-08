# Revision 0419 — ticket extractors for the resident loop

Revision 0419 adds two smaller generated control-plane surfaces for the i3/X11
resident loop:

- `bin/warm_runtime_ticket_json.sh`
- `bin/primary_macro_work_ticket_json.sh`

Both extract the highest-leverage bounded handoffs from `stack_state_json.sh`
into smaller machine-readable tickets, with matching text helpers:

- `bin/warm_runtime_ticket.sh`
- `bin/primary_macro_work_ticket.sh`

This does not replace the fused stack. It makes the private-LLM/operator loop
more practical when it already knows it only needs the resident-runtime repair
answer or the selected-macro next-lane answer.

Code and tests:

- Added generator support and control-plane manifest entries for the four new
  helpers.
- Added focused helper extraction tests in
  `tests/test_primary_macro_work_ticket_cli.py`.
- Updated generated-stack smoke coverage in `tests/test_i3_busd_stack_cli.py`.
