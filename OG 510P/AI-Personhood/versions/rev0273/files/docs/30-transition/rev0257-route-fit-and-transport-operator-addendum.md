# rev0257 route-fit and transport operator addendum

This addendum exists to prevent the next operator from treating first contact as a doctrine problem. rev0257 burns down two blockers that did not require a human signature: route-fit review and transport-capture planning.

## What is now complete

- `examples/external-contact-route-fit-review-rev0257-aiid.json` completes a limited RAIC/AIID route-fit review for the current draft. The fit is only: collaboration/routing inquiry. It is not incident submission, personhood endorsement, custody, intake, import, retention permission, counterparty authority, or send authorization.
- `examples/external-contact-transport-capture-plan-rev0257-aiid.json` provides the exact capture plan for sent copy, transport trace, delivery/DSN status, and inbound raw reply. The plan is executable, but no private vault roots are selected in the public release.
- `examples/external-contact-send-readiness-gate-rev0257-aiid.json` now records those two blockers as satisfied while leaving the gate blocked.

## What is still blocked

The message must not be sent unless all of these are real, not inferred:

1. human signature over exact recipient, subject, body hash, payload hashes, sender role, route-fit review, conflict review, deadline policy, and public-shell limits;
2. sender authority for the account/channel;
3. conflict review;
4. send-time public locator recheck;
5. off-release private vault roots for outbound sent copy, transport trace, delivery/DSN status, and inbound raw reply;
6. send-time recompute of body, mail-ready draft, payload manifest, one-page note, and JSON request packet hashes.

## Operator sequence

Run:

```bash
python3 tools/audit_external_contact_route_fit_review.py
python3 tools/audit_external_contact_transport_capture_plan.py
python3 tools/audit_external_contact_send_readiness_gate.py
```

If any command fails, do not send. If all commands pass, the gate is still blocked until the six unresolved blockers above are satisfied.

## Release boundary

Do not place raw sent-message exports, provider traces, full headers, private vault paths, account identifiers, session details, tokens, DSNs, or raw replies in the public release tree. Public outputs are limited to hashes, sizes, MIME/type, timestamps where proven, status class, and non-authorizing public-shell summaries.

A route-fit review or transport-capture plan is not contact, authority, consent, response, custody, intake, import, recognition, waiver, adverse inference, or live-floor evidence.
