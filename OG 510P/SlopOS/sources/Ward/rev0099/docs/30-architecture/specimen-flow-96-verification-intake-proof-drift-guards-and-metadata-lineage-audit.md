# Specimen flow 96 — verification intake, proof-drift guards, and metadata lineage audit

## Scenario

A public governance status surface previously showed a mismatch. Ward recorded outcome observation, opened rollback-remediation review, closed the review with quarantine sustained, and later acknowledged a remediation handoff. Harbor now reports an implementation/recheck proof.

## Flow

1. Ward loads the source remediation-closure receipt by path and byte digest.
2. The verification-intake receipt mirrors the closure state, closure id, target, recipient class, projection policy, closure-scope digest, and closure-evidence digest.
3. The proof is bound to a proof source class, proof channel, proof subject digest, audience, purpose, validation result, and verifier-conflict check.
4. If proof verifies, Ward records `external_remedy_proof_verified_quarantine_sustained`.
5. If proof fails, Ward records `external_remedy_proof_failed_quarantine_sustained`.
6. If proof is missing, Ward records `external_proof_absent_escalated_still_held`.
7. If proofs conflict, Ward records `proof_conflict_held_quarantine_sustained`.
8. Helm renders the state with a no-authority watermark.
9. SlopOS may attach the receipt as context, but source packet replay and separate authority remain required.

## Refusal edge

The verified proof fixture intentionally keeps `quarantine_clearance_authorized=false`. Ward can record proof intake; it cannot silently turn proof into remedy completion, export authority, action re-enable, learning use, or status-pointer mutation.

## Audit edge

The metadata lineage audit fails if the revision receipt, surface status, manifest, ledgers, context pack, README, or latest docs disagree about the current pass. This keeps the cube's self-description from drifting as the governance receipt family grows.
