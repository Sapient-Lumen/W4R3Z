# Revision Summary — rev0098

Rev0098 focuses on row-level relationship integrity rather than additional doctrine.

Substantive changes:

- Added `tools/ledger_relationship_audit.py`.
- Added `META/Ledger-Relationship-Audit-current.*`.
- Added `SCHEMA/Ledger-Relationship-Audit-Fields-current.*`.
- Added release gate `gate_081`.
- Fixed `META/Public-Claim-Release-Ledger-current.*`: `release_0001` no longer points to current `qclaim_0001`, because current `qclaim_0001` belongs to `claim_0007`. The release row now uses an explicit historical pointer.
- Refactored release-change signature checks so stale signature readiness/status documents fail on any non-current revision/key token, not just one known stale key.
- Kept candidate, claim, source, evidence, office, and public payload expansion closed.

No candidates, claims, sources, public URLs, referrals, contacts, routes, service capacity, case/client details, images, stories, testimony, legal/medical guidance, or public-release permission were added.
