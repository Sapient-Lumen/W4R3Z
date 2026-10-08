# rev0265 delivery-status DSN gate refactor

## Purpose

This revision closes the next practical gap after the send-trace shell: delivery, bounce, delay, and DSN evidence. A future human dispatch can create several machine-generated artifacts before any human counterparty replies: SMTP transcript fragments, provider sent/delivered UI, Delivery Status Notifications, delayed-delivery notices, bounces, Message-ID/ENVID correlations, DKIM/DMARC/ARC authentication observations, and provider receipts. Those artifacts are useful transport evidence, but they are not counterparty responses and must not be used to start or close a response/no-response path by themselves.

## Risk corrected

The risky shortcut was: sent-looking trace plus a DSN or provider delivery indicator becomes a response clock, no-response shell, decline, waiver, custody, authority proof, or floor effect. rev0265 adds a dedicated delivery-status record and staging tool to interrupt that shortcut. Failed delivery means channel/counterparty reselection, not adverse inference. Delayed delivery means watch or retry, not no-response. Delivered or relayed status means transport review, not human reply.

## New release-blocking surfaces

- `schemas/external-contact-delivery-status-record.schema.json`
- `examples/external-contact-delivery-status-record-rev0265-pre-dispatch-no-status.json`
- `tools/stage_external_contact_delivery_status.py`
- `tools/audit_external_contact_delivery_status_record.py`
- `fixtures/negative-tests/external-contact-delivery-status-dsn-as-response.json`

The execution record is upgraded to `external-contact-execution-record-v0.8` and now binds the delivery-status record. The send-proof record, send-trace shell, response triage record, dispatch authorization card, inbound vault precommit, and inbound capture shell list the new delivery-status surface in related surfaces.

## Operational rule

A future delivery-status artifact must be staged outside the release tree. The public archive may carry only a shell: hash, size, MIME/status format, broad DSN action classification, source trace ref, and no raw bytes. Raw DSN content, personal headers, provider account identifiers, private vault paths, SMTP transcript details, and tokens stay out of public release.

## Clock rule

A response clock may not start from a DSN, bounce, provider delivery UI, Message-ID correlation, or delivery timestamp alone. Any future clock requires at least: signed dispatch authorization, actual sent_at, private outbound transport trace, send-proof record updated to a sent state, and no failed/delayed delivery-status blocker. Even then, the delivery-status artifact is transport evidence only, not a counterparty reply.

## Current state

No organization was contacted. No message was sent. No transport trace exists. No DSN, bounce, delay notice, delivered status, provider export, or SMTP transcript exists. No response clock started. No failed-gate shell, custody record, formal response, intake, import, recognition, waiver, adverse inference, or live-floor effect exists.
