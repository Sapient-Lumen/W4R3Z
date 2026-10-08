# rev0244 — mail-ready draft and send-proof record refactor

rev0244 moves the first-contact path one operational step closer to a real external event without claiming the event happened. rev0242 created a signable authorization card; rev0244 adds the concrete mail-ready draft and the proof object that must be completed after any future dispatch.

## Changed surfaces

- `examples/external-contact-mail-ready-draft-rev0244-aiid-not-sent.eml`
- `schemas/external-contact-send-proof-record.schema.json`
- `examples/external-contact-send-proof-record-rev0244-no-transport-proof.json`
- `tools/render_external_contact_mail_ready_draft.py`
- `tools/audit_external_contact_send_proof_record.py`
- `fixtures/negative-tests/external-contact-send-proof-record-draft-eml-as-sent.json`
- `schemas/external-contact-execution-record.schema.json`
- `examples/external-contact-execution-record-rev0244-ready-to-dispatch.json`
- `schemas/external-contact-dispatch-authorization-card.schema.json`
- `examples/external-contact-dispatch-authorization-card-rev0244-aiid-blocked-no-signature.json`

## Risk closed

The severe remaining failure mode was draft laundering: once a candidate-specific email file exists with a real public To header, an operator could accidentally or adversarially treat that file as a sent request. That would start a response/no-response clock against a never-contacted organization and could later be misused as a failed-gate shell, waiver, adverse inference, custody, intake, import, or live-floor basis.

rev0244 blocks that path by separating three states:

1. a rendered public message, which is only a human-readable body/hash control;
2. a mail-ready `.eml` draft, which is still not contact or transport proof;
3. a send-proof record, which remains `not-sent-no-proof` until actual sent_at, sender role, transport proof, message/header or screenshot hash, private trace locator, and deadline calculation from the real sent_at timestamp exist.

## Current result

No organization was contacted in rev0244. No message was sent. No Gmail draft, transport proof, response clock, no-response shell, failed-gate shell, inbound artifact, custody record, response record, intake, import gate, recognition claim, waiver, adverse inference, or live-floor effect exists.

The useful progress is narrower and concrete: the steward now has an exact candidate-specific draft artifact plus an auditable checklist for what must be captured if a future human-authorized dispatch occurs.
