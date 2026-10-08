# 164. Proof obligations registry (authoritative IDs + linkage)

**Track:** Shared

This project uses **proof obligations** to keep “what must be provable” stable even as
protocols, tooling, or documentation evolve.

- Narrative and rationale live in: `docs/159-proof-obligations-ledger.md`
- The **authoritative registry** of IDs and link targets lives in:
  `artifacts/proof_obligations/proof-obligations.csv`

## 164.1 Why a registry?

Without an authoritative registry, the archive drifts in subtle ways:

- Claims and hazards refer to obligations that get renamed or split.
- “Minimum viable release” for Track A becomes a debate, not a checklist.
- Review cadence gets fuzzy and hard to enforce.

A registry makes the project **machine-checkable** and **reviewable**.

## 164.2 Required fields (CSV)

Columns in `proof-obligations.csv`:

- `ProofObligationID` (stable, never reused)
- `Track` (A / B / C / Shared)
- `Title`
- `Statement` (one-line “must be provable” statement)
- `LinkedClaims` (semicolon-separated ClaimIDs)
- `LinkedHazards` (semicolon-separated HazardIDs)
- `RequiredEvidenceArtifacts` (semicolon-separated TYPE:path tokens; see `docs/163`)
- `VerificationLane` (e.g., “integration test”, “field drill”, “auditor replay”)

## 164.3 Change control rules

- Adding a new PO is allowed (prefer extending, not mutating).
- Renaming is allowed ONLY if the old ID is tombstoned with an alias note.
- Deleting a PO is forbidden once referenced by a claim/hazard/ADR.

## 164.4 Relationship to Track A “minimum viable release”

Track A releases are gated by a **small set of POs** (see `docs/track-a/MVR_CHECKLIST.md`).
This is the place where the “full election stack” concern gets resolved: Track A is
the deployable evidence stack, and its POs are explicit and auditable.
