# rev0273 current action spine refactor

This revision addresses the riskiest remaining pre-action failure: the archive can be correct in pieces while still too dispersed for a human operator to execute safely. The new current action spine binds the route ledger, authority expiry check, pre-send evidence bundle, authority handoff dry-run, reviewer-first packet, field workbook, response playbook, failed-gate shell, and last-mile checklist into one no-send execution path.

The change is deliberately operational rather than doctrinal. It does not add a new rights theory. It says the next real move is a private signed branch record or continued no-send.

New surfaces:

- `examples/current-action-spine-rev0273-reviewer-first-no-send.json`
- `examples/last-mile-operator-checklist-rev0273-reviewer-first-no-send.json`
- `docs/30-transition/rev0273-last-mile-operator-checklist.md`
- `tools/audit_rev0273_current_action_spine.py`

## Risk closed

A dispersed packet set can invite symbolic completion: a route score becomes authority, a green audit becomes readiness, a draft becomes contact, or a checklist becomes permission. rev0273 makes those substitutions fail. The spine says exactly which surfaces must be current, which hashes must be recomputed, which private roots must exist outside the public release, and which outcomes are non-progress.

## Still blocked

No private signature, private root, send, transport proof, delivery status, response clock, raw inbound artifact, custody, intake, import, reviewer appointment, welfare finding, or live-floor effect exists.

## Refactor

The operator-facing route now has one current decision point: no-send, defer, stop, or one exact reviewer-first send. Queue entries and front doors should point to the spine rather than requiring an operator to reconstruct the path from many registry surfaces. [REF-0776] [REF-0783]

## rev0273 send-attempt overlay

The current action spine now has an explicit transaction overlay: `examples/send-attempt-transaction-ledger-rev0273-no-signature-aborted.json`. That ledger records the present state as `NO-SEND-FAIL-CLOSED` because private operator identity/signature, private roots, and send-time recompute are missing. The overlay prevents a checklist or green audit from becoming a silent substitute for a signed branch decision.
