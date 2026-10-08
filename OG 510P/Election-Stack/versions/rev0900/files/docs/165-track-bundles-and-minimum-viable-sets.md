# 165. Track bundles and minimum viable sets (curated navigation)

**Track:** Shared

Large security-sensitive archives fail when they rely on “folk knowledge” for navigation.
This project uses **curated bundles** to provide stable entrypoints.

- Bundle definitions (source of truth): `artifacts/bundles/*.toml`
- Generated bundle pages:
  - `docs/track-a/BUNDLE.md`
  - `docs/track-b/BUNDLE.md`
  - `docs/track-c/BUNDLE.md`

Bundles are not normative specs; they are a **curated reading and onboarding path**.

## 165.1 Why bundles?

- Keeps onboarding fast (new maintainers can orient in ~30 minutes).
- Prevents scope confusion (“is the project about internet voting?”).
- Makes reviews easier (“this change touches a bundled doc; scrutiny is higher”).

## 165.2 Minimum viable release sets

Track A additionally has a **minimum viable release (MVR)** checklist generated from the PO registry,
claims, and hazards:

- Source of truth: `artifacts/proof_obligations/proof-obligations.csv`
- Generated checklist: `docs/track-a/MVR_CHECKLIST.md`
- Generation script: `scripts/gen_track_a_mvr.py`

The MVR checklist answers: **what is the smallest set of proof obligations we are willing to claim?**

## 165.3 Change rules

- Bundles may change often; they are editorial.
- MVR gating POs should change rarely, and only with an ADR when a change alters what Track A claims.
