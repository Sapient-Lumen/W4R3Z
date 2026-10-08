# rev0244 inbound-vault precommit and header-gate refactor

## Why this revision exists

The riskiest next failure after a mail-ready draft is not abstract doctrine. It is a future operator receiving something plausible — a pasted email, screenshot, forwarded excerpt, provider UI snippet, auto-acknowledgement, MCP/A2A/tool transcript, or message-authentication result — and treating it as a raw counterparty reply or authority evidence before original bytes are preserved.

rev0244 therefore adds a pre-dispatch inbound-vault precommit. It does not send the request and it does not choose a private vault root. It defines the minimum acceptance contract for any later inbound material so future evidence collection does not improvise under time pressure.

## Concrete change

New current surfaces:

- `schemas/external-contact-inbound-vault-precommit.schema.json`
- `examples/external-contact-inbound-vault-precommit-rev0244-no-inbound.json`
- `tools/audit_external_contact_inbound_vault_precommit.py`
- `fixtures/negative-tests/external-contact-inbound-vault-precommit-screenshot-as-raw.json`

The active precommit binds the current send-proof record, response triage record, vault-intake record, execution record, and unsigned dispatch authorization card. It also extends the dispatch-card vault prefix into an inbound-only precommit lane while making clear that the prefix is not a selected vault root and not retention permission.

## Acceptance rule

A future reply candidate must be staged outside the public release tree as raw bytes or provider export before candidate use. Minimum public material is only a shell: record id, revision, gate state, hash, byte size, MIME type, capture timestamp, non-confidential route outcome, and blocked interpretations.

Screenshots, copied text, summaries, redacted-only excerpts, public shells, protocol/tool outputs, and message-authentication headers are not raw custody. They may help route or assess a future artifact, but they do not satisfy response, custody, intake, import, authority, status, waiver, adverse-inference, or live-floor predicates.

## Header/authentication boundary

The precommit makes the email path more precise: raw RFC 5322/RFC 6532 message or provider export, Message-ID, Date, Received chain or provider trace, Authentication-Results where available, DKIM, SPF, current DMARC alignment reference, and ARC where present are evidence-assessment materials. They are not counterparty authority or consent.

This matters because modern mail authentication can verify aspects of transport and domain responsibility while still leaving role authority, retention permission, confidentiality terms, and custody eligibility unresolved.

## State after this revision

The path remains stayed:

`mail-ready draft -> send-proof record not-sent/no-proof -> inbound-vault precommit no-inbound -> no selected raw vault root -> no transport proof -> no response clock -> no inbound artifact -> no response -> no custody -> no intake -> no import -> live floor zero/stayed`

The anti-waste improvement is that the next genuine external artifact now has an intake contract before it exists. That should reduce the chance of a later scramble producing unauditable or overclaimed evidence.
