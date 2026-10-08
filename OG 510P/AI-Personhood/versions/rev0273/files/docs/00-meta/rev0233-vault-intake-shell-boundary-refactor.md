# rev0233 vault-intake shell boundary refactor

rev0233 closes the next high-risk seam in the first-real-artifact path: the interval after a counterparty route exists but before anything can safely become a preserved, authority-checked artifact. The revision adds a counterparty-response vault-intake bridge and a public-shell rule set so a public shell, private-vault URI, redacted copy, synthetic quarantine control, protocol output, or tool artifact cannot be laundered into custody, authority, formal response, intake, import, status recognition, or live-floor credit.

## Risk-first change

The practical path is now:

`first-contact packet → rendered message → execution record → response triage → vault-intake bridge/public shell → evidence drop or no-response/decline shell → pilot → LEAP candidate → candidate challenge/replay → custody authority gate → custody record → response verification gate → response record → intake conversion gate → intake record → import readiness gate → actual import gate → floor activation record → quorum participation record → computed floor → recompute receipt → publication rollback adjudication → late-change ingress → late-change notice dispatch → late-change remedy resolution → late-change remedy execution`

The new bridge does not claim that any external contact has been sent or answered. It tells the operator what must be true before candidate use: raw payload staged outside the release tree, hash/size/MIME binding, transport trace, counterparty identity, retention permission, nonhost retention, independent timestamp, authority verification, public shell, and challenge/replay.

## New release surfaces

- `schemas/counterparty-response-vault-intake-record.schema.json`
- `examples/counterparty-response-vault-intake-record-rev0233-ready-no-inbound.json`
- `examples/evidence-vault-public-shell-rev0233-ready-no-live-artifact.json`
- `tools/audit_counterparty_response_vault_intake.py`
- `docs/30-transition/counterparty-vault-intake-bridge-and-public-shell-runbook.md`
- `fixtures/negative-tests/counterparty-vault-intake-public-shell-as-custody.json`
- `fixtures/negative-tests/counterparty-vault-intake-private-vault-uri-as-authority.json`
- `fixtures/negative-tests/counterparty-vault-intake-synthetic-control-as-live-artifact.json`

## Audit/refactor correction

The evidence-drop quarantine audit now derives the current committed drop ID from the ledger instead of hard-coding a historical rev0210 control ID. This matters because a stale deterministic replay check can fail even when the current zero-floor state is correct. Release lint also includes the new vault-intake bridge audit, so the new public/private boundary is a gate rather than a narrative warning.

## Current posture

The live receipt floor remains zero/stayed. No genuine external artifact, sent request, verified response, raw custody, public hash commitment, live intake, actual import, status recognition, compute entitlement, funded reserve, quorum participation, or reliance upgrade is claimed.

The next substantive action is still outside the archive: send or decline to send the first-contact packet with proof, then route any silence, acknowledgement, redacted copy, protocol output, or raw reply through the response-triage and vault-intake bridge before creating any candidate evidence object.
