# rev0273 operator authority packet compiler refactor

rev0273 moves the active path one step closer to real execution without sending anything. rev0271 recorded the public send-attempt outcome as `NO-SEND-FAIL-CLOSED`; rev0273 adds a compiled operator-authority packet that binds that transaction ledger to the branch template, private-root shell, route-freshness ledger, exact message bytes, response-disposition playbook, failed-gate shell, and six-artifact pilot state.

The new public compiler surface is `examples/operator-authority-packet-compiler-rev0273-reviewer-first-no-signature.json`. Its current result is `NOT-ACTIONABLE-NO-PRIVATE-AUTHORITY`.

The point is not another registry layer. The point is to prevent a human operator from having to reconstruct the final authority path from scattered surfaces at the moment when mistakes are most expensive. The packet says, in one place, what exists publicly, what is still missing privately, what must be recomputed at send time, and what aborts the branch.

## Risk addressed

The archive had accumulated good gates, but the last-mile execution proof still depended on reading multiple objects in the right order. That creates a practical risk: a future operator could see green lint, a no-send ledger, an action spine, a checklist, and a route ledger and mistakenly treat the bundle as authorization.

rev0273 fails that path closed. A compiled packet is still not a signature, not a selected branch, not a private vault root, not send-time hash recompute, not transport proof, not response classification, and not a live-floor input.

## Substance added

- Public compiler object binding the active last-mile sources and hashes.
- Builder: `tools/build_operator_authority_packet.py`.
- Audit: `tools/audit_rev0273_operator_authority_packet.py`.
- Operator runbook: `docs/30-transition/rev0273-operator-authority-packet-runbook.md`.
- Queue refactor: the three first-artifact lanes now receive into the compiler, but remain open unless private authority and evidence capture actually exist.
- Route freshness refresh: Eleos remains the primary reviewer-first route; AIID remains secondary route-fit or incident-learning only; Conscium remains fallback/referral.

## Current result

`NO-SEND-FAIL-CLOSED` remains the current transaction result. The compiler also records `NOT-ACTIONABLE-NO-PRIVATE-AUTHORITY` because no private operator identity/signature, no signed branch value, no selected private roots, and no send-time recompute exist.

## Non-progress rule

The following do not move A1 or A2: more doctrine, more registry surfaces, route score, public locator, green lint, stale hashes, an unsigned template, a dry-run vault shell, a contact draft, delivery metadata without a signed branch, auto-acknowledgement, silence, or a failed-gate public summary.

Only a future private signed branch plus selected private roots plus fresh route/hash recompute plus transport or failed-send capture can move the field chain.
