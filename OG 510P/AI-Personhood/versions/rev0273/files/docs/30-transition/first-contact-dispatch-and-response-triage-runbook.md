# First-contact dispatch and response triage runbook

This runbook exists to stop the first external-contact step from becoming theatre. `examples/external-contact-request-packet-rev0239-first-artifact.json` is sendable, but only `examples/external-contact-execution-record-rev0239-ready-to-dispatch.json` can prove dispatch state, and only `examples/external-contact-response-triage-record-rev0239-pre-dispatch.json` or a successor can classify silence, decline, acknowledgement, redaction, protocol output, or reply.

## Dispatch rule

Before sending, capture the final outgoing body hash, channel, recipient organization class, sender role, date, and the no-status/no-waiver language. Do not send if the request asks for personhood recognition, legal conclusions, welfare findings, trade secrets, privileged material, or custody concessions.

A sent request is not receipt, custody, response, intake, import, authority, waiver, adverse inference, status recognition, or live-floor evidence. It is only a dispatch fact.

## Response triage

If nothing has been sent, keep the execution record in `not-sent-ready` or `no-send-recorded` state and do not publish a counterparty-facing failure. `no-send-recorded` is used when the release has a concrete reason not to send, such as no named counterparty, no sender authority, or no safe channel; it starts no response/no-response clock.

If the request is sent and the deadline is still open, publish nothing beyond a private dispatch note unless a public update is necessary to prevent confusion.

If the counterparty declines or the window expires, publish a failed-gate/no-response shell that names the gate state, request hash/path, channel class, date, and no-live-floor effect. Do not publish private contact details, raw reply bytes, trade secrets, privileged content, waiver language, or adverse-inference language.

If a reply arrives, first preserve raw bytes outside the public release tree. Then use `tools/stage_live_evidence_drop.py` or a successor private-vault workflow before creating any public shell. A redacted copy, screenshot, automated acknowledgement, protocol artifact, or polite reply does not satisfy custody.

## Next safe states

The only safe immediate outcomes are:

- `not-sent-ready` because dispatch remains possible but unconfirmed;
- `no-send-recorded` because a concrete blocker prevents dispatch and no response clock may start;
- `sent-awaiting-response` with transport proof and deadline;
- `declined` or `no-response-failed-gate-shell-ready` with no adverse inference;
- `response-received-quarantined` after private-vault staging, still with no custody, intake, import, or floor effect.

Any other path must fail closed.

## Response-triage handoff

After dispatch, do not interpret silence, decline, automated acknowledgement, redacted copy, protocol/tool output, or raw reply directly. Route the state through `examples/external-contact-response-triage-record-rev0239-pre-dispatch.json` and, if raw bytes are retained, through `tools/stage_live_evidence_drop.py` into an outside-release-tree private vault before any public shell.


## Rev0239 dispatch preflight rule

Dispatch preflight is mandatory before any send claim: the final outgoing body SHA-256, rendered-message path, request deadline, execution deadline, named counterparty, public channel locator, and sender authority must align. A no-send preflight cannot start a response clock, prepare a no-response shell, substitute for dispatch, create custody, open intake, enable import, or affect the live floor.
