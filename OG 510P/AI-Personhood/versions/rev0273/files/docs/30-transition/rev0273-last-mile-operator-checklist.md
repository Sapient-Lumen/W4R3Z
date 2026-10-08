# rev0273 last-mile operator checklist

Use this note only with `examples/current-action-spine-rev0273-reviewer-first-no-send.json` and `examples/last-mile-operator-checklist-rev0273-reviewer-first-no-send.json`. It is a no-send runbook unless a separate private signature exists outside the public release.

## Last-mile order

1. Decide branch privately: no-send, defer, stop, or one exact reviewer-first send.
2. Create or verify private vault roots outside the release tree.
3. Recheck the public route locator immediately before any send.
4. Recompute the exact message-body and `.eml` hashes.
5. Confirm recipient, subject, sender account, no-attachment scope, and one-shot limit.
6. Send at most once, or record no-send/defer/stop.
7. Preserve raw transport outcome privately.
8. Classify any inbound outcome before public narration.
9. Publish only a safe shell, and only after classification.

## Abort immediately

Abort if the signature is absent or expired, the locator changed, route freshness expired, private roots are missing, message bytes changed, attachments appear, the sender account differs, or any person tries to count delivery, auto-ack, referral, silence, route score, doctrine, registry count, or this checklist as success.

## Positive progress

The next substantive progress event is not another document. It is one of: a signed no-send/defer/stop record, a signed one-shot send authority record, private vault roots selected, a send-time hash/locator recheck, a raw transport artifact, or a classified human response/failed gate. [REF-0776] [REF-0783]

## rev0273 transaction overlay

Before any public claim that an action was attempted, the operator must either produce a private authority/root/send-time record or rely on the public abort ledger: `examples/send-attempt-transaction-ledger-rev0273-no-signature-aborted.json`. In this release the ledger is an abort/no-send record, not authority.
