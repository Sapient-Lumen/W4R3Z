# rev0253 inbound-capture shell and vault-stage refactor

## Mission move

rev0253 closes the next execution risk after the inbound-vault precommit: a future reply could arrive and still be mishandled because the archive had a rule saying “stage raw bytes” but no concrete public-shell capture surface or staging command for that specific external-contact lane.

This revision adds the missing bridge:

`not-sent .eml -> send-proof not-sent/no-proof -> inbound-vault precommit -> inbound-capture shell/staging tool -> response triage/vault intake later`

The new bridge is deliberately boring and narrow. It does not send a message. It does not start a response clock. It does not create custody. It gives a future operator one safe way to convert a raw RFC 5322/RFC 6532 message or provider export into a public hash/size/MIME shell while keeping raw bytes outside the release tree.

## New surfaces

- `schemas/external-contact-inbound-capture-shell.schema.json`
- `examples/external-contact-inbound-capture-shell-rev0253-no-inbound.json`
- `tools/stage_external_contact_inbound_capture.py`
- `tools/audit_external_contact_inbound_capture_shell.py`
- `fixtures/negative-tests/external-contact-inbound-capture-shell-public-raw-leak.json`
- `examples/external-contact-inbound-vault-precommit-rev0253-no-inbound.json`

## Acceptance rule

A future inbound candidate can become a public shell only if the raw input is outside the public release tree. The public shell may record hash, size, MIME/type, parse booleans, and routing constraints. It may not publish raw bytes, full headers, private vault paths, retention text, personal data, trade secrets, or counterparty secrets.

Header parsing, DKIM, SPF, DMARC, and ARC remain transport/authentication assessment only. RFC 5322 defines the Internet Message Format, including the `Date` field; RFC 6532 extends Internet Message Format/MIME for UTF-8 headers; RFC 8617 describes ARC as an authenticated message-handling chain; and RFC 9989 describes DMARC and obsoletes RFCs 7489 and 9091. None of those standards supplies counterparty authority, consent, custody, personhood recognition, waiver, adverse inference, or live-floor credit by itself.

## Audit/refactor

`tools/lint_archive.py` now runs `audit_external_contact_inbound_capture_shell.py`. The new audit checks that the current shell is `pre-dispatch-no-inbound`, tool-generated, bound to the current inbound-vault precommit, and locked against public raw-byte leakage, response-clock start, response creation, custody, intake, import, authority, waiver, adverse inference, recognition, and floor effects.

The inbound-vault precommit is upgraded to `external-contact-inbound-vault-precommit-v0.2` so the precommit and capture shell reference each other. This turns “stage raw bytes later” from a textual promise into a release-blocking path.

## Non-claims

No organization was contacted. No message was sent. No response clock started. No inbound artifact exists. No raw-reply private vault root was selected. No transport proof exists. No response, custody, intake, import, recognition, waiver, adverse inference, payment, entitlement, public backstop, or live-floor effect exists.
