# rev0271 send-attempt abort-proof runbook

This runbook is the operator-facing complement to the current action spine.

1. Read `examples/current-action-spine-rev0271-reviewer-first-no-send.json` and `examples/last-mile-operator-checklist-rev0271-reviewer-first-no-send.json`.
2. Prepare private operator identity/signature evidence outside the public release tree. If it is missing, record `NO-SEND-FAIL-CLOSED`.
3. Prepare private roots for sent copy, transport proof, raw inbound material, classification notes, and sealed evidence. If any root is missing or inside the public tree, record `NO-SEND-FAIL-CLOSED`.
4. Recheck route locator and route fit immediately before any send. A public contact route is not consent or authority.
5. Recompute message body and `.eml` hashes at send time. A dry-run hash is not a send-time hash.
6. If every private condition passes, the human may perform exactly the signed branch. If any condition fails, do not send.
7. Whether the result is abort, failed-send, delivery-only, auto-ack, decline, referral, silence, narrow yes, or private-data request, record the disposition before public narration.

The current rev0271 public transaction ledger is `examples/send-attempt-transaction-ledger-rev0271-no-signature-aborted.json`. It records the present state as aborted before send because signature and private-root gates are not satisfied.
