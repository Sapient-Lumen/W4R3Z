# rev0273 — route-first send/capture gate and reply ladder refactor

## Why this revision exists

rev0256 solved one practical failure mode by creating a no-attachment route-first draft. The remaining risk was that the executable machinery still centered the older attachment-bearing payload path. That left a dangerous gap: an operator could prefer the simpler route-first email but then rely on full-payload send-readiness language for proof, response triage, and stage-two decisions.

rev0273 makes the route-first branch an audited execution lane of its own.

## New high-signal surface

- `examples/external-contact-route-first-send-capture-gate-rev0273-aiid.json`
- `schemas/external-contact-route-first-send-capture-gate.schema.json`
- `tools/audit_external_contact_route_first_send_capture_gate.py`
- `fixtures/negative-tests/external-contact-route-first-send-capture-gate-draft-as-transport.json`
- `docs/30-transition/rev0273-route-first-send-and-reply-runbook.md`

The new gate binds the exact route-first body, `.eml`, recipient, subject, no-attachment limit, stage-two deferral, capture ladder, reply ladder, and remaining blockers.

## What became more executable

The preferred first-hop path is now:

1. route-first no-attachment draft only;
2. human signature and sender authority;
3. send-time public locator recheck;
4. private vault roots for sent copy, transport trace, delivery/DSN status, and raw reply;
5. final route-first body and `.eml` hash recompute;
6. actual send only if authorized;
7. sent-copy/provider trace capture before any response/no-response window starts;
8. reply classification before any stage-two payload decision.

The reply ladder now treats willingness to receive the packet as only a **stage-two authorization candidate**. It is not custody, intake, import, recognition, or live-floor evidence, and it cannot itself send the payload. A fresh human decision and final hash recompute remain required.

## Audit/refactor result

The route-first send/capture audit is wired into release lint. That is a deliberate refactor: the active path is no longer merely documented as preferred; it is machine-checked as the branch that a future operator must confront first.

The older full-payload path remains available only as stage two. It should not control the first read unless the human operator separately abandons the route-first branch.

## What remains blocked

No human signature exists. No sender authority exists. No send-time locator recheck exists. No private vault roots are selected. No final route-first hash recompute has been performed at dispatch time. No transport proof exists. No reply exists. No response clock exists. No custody, intake, import, recognition, or live-floor movement exists.

## Waste corrected

The waste corrected here is path ambiguity. The archive was spending care on a lower-friction first hop while still forcing operators to reason through the heavier stage-two send gate. rev0273 removes that mismatch and makes the lowest-friction path the clearest audited path.
