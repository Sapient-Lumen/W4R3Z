# Custody authority evidence binder and proof refactor runbook

This runbook handles the seam between candidate-challenge disposition and the custody authority gate. Its purpose is to prevent custody authority from being inferred from booleans, protocol messages, public shells, private-vault locators, redactions, elapsed time, or operator confidence.

## Required order

1. Confirm vault intake and normalization did not stay or reject the inbound material.
2. Confirm candidate challenge opened from normalized candidate material rather than from a shell, private-vault locator, redaction, protocol output, unsafe archive, or synthetic control.
3. Confirm candidate-challenge disposition exists and is human-reviewed.
4. Build a custody authority evidence binder. Do not use custody-gate flags as evidence.
5. Bind each authority prerequisite to a specific cited evidence reference.
6. Mark the binder `verified-for-custody-gate` only when every required authority ref is present, human-reviewed, class-scoped, independently timestamped, and safe for the receipt class.
7. Feed the custody gate only with both a qualifying candidate disposition and a qualifying authority evidence binder.
8. Recompute the admission graph and live floor after any real binder/gate change.

## Authority refs required before eligibility

A positive binder must cite evidence for manual contact, request trace, subject or representative authority, receipt-class scope, verifier adapter, independent timestamp, non-host retention, sealed/public parity, redaction boundary, dependency independence, and public authority limitations.

Any missing evidence keeps the binder blocked. A blocked binder may explain next steps, but it cannot create custody or feed custody-gate eligibility.

## Never enough by itself

These cannot satisfy authority evidence:

- operator checkbox or command-line flag;
- elapsed time or silence;
- automated acknowledgement, ticket, bounce, or mailbox rule;
- MCP, A2A, API, relay, or other protocol/tool output;
- redacted-only copy;
- public shell;
- private-vault locator;
- synthetic fixture or quarantine control;
- raw confidence note by the release steward.

## Current rev0236 state

`examples/custody-authority-evidence-binder-rev0236-pre-dispatch-no-authority.json` is pre-dispatch/no-authority. `examples/counterparty-artifact-custody-gate-rev0236-pending-challenge.json` binds to that evidence binder and blocks. The current admission graph includes `AUTHORITY_EVIDENCE_BINDER` and confirms no current binder can be consumed.

## Operator rule

Do not prepare custody from a closed candidate disposition unless the authority evidence binder independently verifies the authority chain. A custody gate may only authorize preparation of a separate custody record; it does not create response, intake, import, status recognition, waiver, entitlement, reserve, or live-floor credit.
