# Cube deep audit rev0285

Rev0285 audits the activation boundary after rev0284 closed the direct
`active_change` bypass. The remaining risk was a source-packet substitution: the
activation receipt could cite a real-looking local packet that was not the same
packet reviewed by the workbench/decision chain.

## What is healthy

The live lane is now largely executable rather than doctrinal. It starts from
the router, prepares one owner packet, records no-send blocks, records send and
reask logs only after human send/adaptation, ties returned CSV intake to active
contact clocks, and keeps workbench review, first-packet decision, ticket, and
card artifacts scratch-local and non-evidentiary.

Rev0285 keeps that shape and narrows activation to one source lineage.

## What was still risky

A local operator could create or select an unrelated CSV, pass its path to
`owner-activation-receipt`, and produce a receipt that looked like accepted
`SRC2+` activation. Rev0284 checked existence, path boundary, class, counts, and
hash integrity of that file. It did not yet prove the file hash was the same hash
preserved by the intake/workbench/decision chain.

That would have been wasteful and dangerous because it lets the archive appear
to advance while the actual owner-reviewed packet remains missing, stale, or
unmatched.

## Refactor made

- Added `decision_chain_source_csv_snapshot(...)` to `tools/ft0181_field_guards.py`.
- Updated `tools/record_ft0181_activation_receipt.py` so `--source-packet` must
  hash-match the decision-chain `source_csv.sha256`.
- Updated the activation receipt manifest with `decision_source_chain` and
  `source_packet.matches_decision_chain_source_csv_sha256=true`.
- Updated activation, ticket, live-window, and router validators so the valid
  path uses the same source packet hash from seed to receipt.
- Updated the router activation template to say the source packet must be the
  same returned owner CSV/file that seeded the decision.

## What remains outside the cloudtainer

The archive still cannot contact an owner or verify organizational authority by
itself. The new lineage check is necessary but not sufficient: it prevents local
packet substitution, but it does not create owner evidence, import custody,
readout evidence, public-claim support, or closure.

## Refactor posture

This pass changed an executable guard rather than adding another doctrine layer.
Future work should continue to prefer one-command field progress and hash-bound
source checks over new registries.
