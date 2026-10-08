# rev0273 send-attempt transaction refactor

rev0270 made the action path legible, but it still left one operationally risky gap: an operator could stand in front of the action spine and still fail to produce a single, replayable record of why the action did or did not happen.

rev0273 adds a send-attempt transaction layer. It is deliberately not a doctrine note, not a registry entry, and not authority. It is a public, hash-bound transaction ledger for the current reviewer-first path that records each last-mile gate as pass-for-orientation, abort, or not-reached.

Current surfaces:

- `examples/send-attempt-transaction-ledger-rev0273-no-signature-aborted.json`
- `examples/operator-identity-signature-capture-template-rev0273-no-signature.json`
- `examples/private-root-selection-dryrun-shell-rev0273-no-private-root.json`
- `tools/build_send_attempt_transaction_ledger.py`
- `tools/audit_rev0273_send_attempt_transaction.py`

The current transaction result is `NO-SEND-FAIL-CLOSED` because the archive still lacks a private operator identity/signature record, signed branch value, selected private roots, send-time hash recompute, transport proof, and response classification.

This refactor changes the operator posture from “there is a checklist” to “there is a reproducible public abort ledger unless the private authority and custody preconditions are actually satisfied.”

## Anti-overclaim rule

The transaction ledger may prove that a no-send abort state was captured. It may not authorize send, start a response clock, prove delivery, prove a counterparty response, create custody, intake, import, reviewer appointment, welfare finding, recognition, or live-floor effect.
