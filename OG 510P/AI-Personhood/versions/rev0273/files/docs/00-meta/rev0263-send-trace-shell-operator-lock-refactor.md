# rev0263 send-trace shell and operator-lock refactor

## Mission move

rev0263 closes the next execution risk after the inbound-capture shell: a future human could finally send the RAIC/AIID first-contact draft but preserve only a screenshot, a copied `Message-ID`, a provider UI view, or partial authentication headers. That would be a weak and dangerous proof trail, because it could invite the archive to treat outbound-looking evidence as dispatch, response-clock start, no-response/failed-gate evidence, custody, authority, intake, import, recognition, waiver, adverse inference, or live-floor movement.

The new bridge is:

`NOT-SENT .eml -> signed dispatch card later -> private outbound transport trace later -> public send-trace shell later -> send-proof record update later -> only then response-clock evaluation`

Current rev0263 remains before the bridge: the send-trace shell is present only as a pre-dispatch/no-transport public shell. No raw trace, no sent timestamp, no `Message-ID`, no provider receipt, no SMTP trace, no public shell generated from raw transport evidence, and no response clock exist.

## New surfaces

- `schemas/external-contact-send-trace-shell.schema.json`
- `examples/external-contact-send-trace-shell-rev0263-no-transport.json`
- `tools/stage_external_contact_send_trace.py`
- `tools/audit_external_contact_send_trace_shell.py`
- `fixtures/negative-tests/external-contact-send-trace-shell-message-id-as-clock.json`
- upgraded `schemas/external-contact-send-proof-record.schema.json` to bind the send-trace shell
- upgraded `schemas/external-contact-dispatch-authorization-card.schema.json` to require send-trace-shell acceptance checks
- upgraded `schemas/external-contact-execution-record.schema.json` to bind the send-trace shell

## Acceptance rule

A future outbound transport trace may become a public shell only if the raw sent-message export, provider receipt, SMTP log, or equivalent raw trace is outside the public release tree. The public shell may disclose hash, size, MIME/type, trace format, header-presence booleans, sent/deadline booleans, routing state, and non-effect locks. It may not disclose raw sent-message bytes, full SMTP/provider headers, provider account identifiers, authentication tokens, private vault paths, personal data, counterparty secrets, or internal mail-server traces.

`Message-ID`, `Date`, `From`, `To`, `Received`, DKIM, DMARC, SPF, ARC, and provider-trace fields are useful transport/header evidence. They are not counterparty authority, consent, custody, response, intake, import, recognition, waiver, adverse inference, or live-floor evidence by themselves. They also cannot start the response clock unless the send-proof record is updated after signed authorization, actual `sent_at`, private raw transport trace retention, public send-trace shell creation, and deadline binding.

## Audit/refactor

`tools/audit_external_contact_send_trace_shell.py` verifies that the active send-trace shell is `pre-dispatch-no-transport`, bound to the current send-proof, execution, authorization card, and mail-ready draft, and locked against Message-ID/header/authentication shortcuts. `tools/stage_external_contact_send_trace.py` provides the future staging path and rejects raw traces inside the release tree.

The existing send-proof, dispatch-authorization, and execution-record schemas now carry explicit send-trace-shell bindings. This makes the future operator path concrete without pretending that the current release has sent anything.

## Non-claims

No organization was contacted. No message was sent. No transport proof exists. No outbound raw trace was staged. No response clock started. No inbound artifact exists. No raw-reply private vault root was selected. No response, custody, intake, import, recognition, waiver, adverse inference, payment, entitlement, public backstop, or live-floor effect exists.
