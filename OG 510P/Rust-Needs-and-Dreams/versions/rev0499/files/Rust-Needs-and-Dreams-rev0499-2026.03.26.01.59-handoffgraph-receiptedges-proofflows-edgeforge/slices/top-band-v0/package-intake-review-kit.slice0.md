# Kernel slice 0: Package Intake Review Kit

## Identity
- candidate: **Package Intake + Release Boundary Review**
- governing kernel: `kernels/top-band-v0/package-intake-review-kit.v0.md`
- current verdict context: `advance`
- slice codename: `package-intake-review-kit/slice0`

## Why this slice first
This slice should prove that one team can make **local, reviewable dependency or release-boundary decisions** with explicit route posture, waivers, and one replayed incident drill.
That is a better first milestone than a central trust service because current supply-chain reality is still route-specific and operator-specific.

## Exact deliverables
Ship only:
1. `policies/route-profiles/` with starter profiles for:
   - GitHub Trusted Publishing
   - GitLab.com Trusted Publishing
   - token-based publish
   - alternate registry
2. `schemas/intake-receipt-v0.schema.json`
3. `receipts/intake/`, `receipts/waivers/`, and `receipts/quarantine/`
4. `drills/incident-replays/` with one known incident-class drill
5. `crates/intake-cli/` or equivalent validator with:
   - `review`
   - `waive`
   - `quarantine`
   - `drill`

## Acceptance checks
The slice counts as done when it can:
- generate one review receipt from local project inputs;
- generate one waiver with owner and expiry;
- run one incident drill against a selected route profile;
- and make alternate-registry uncertainty explicit instead of silently inheriting crates.io assumptions.

## Proving grounds
Start with:
- one crates.io Trusted Publishing route,
- one token-publishing route,
- one alternate-registry route,
- one dependency-intake drill tied to a recent incident pattern.

## Imports and dependencies
Allowed imports:
- lockfile/manifest/dependency graph data
- workflow metadata
- current advisories or vulnerability signals
- optional capability-analysis output and provenance receipts when available

## Postponed work
Do **not** include yet:
- global scoring
- mandatory organization-wide policy enforcement
- hosted review dashboards
- automatic blocking across every workflow

## Failure receipts
Ship unsupported-state receipts for:
- route profiles that are incomplete
- advisory ambiguity
- unavailable provenance/capability signals
- alternate-registry assumptions carried from crates.io without proof

## Next-slice trigger
Take slice 1 only after multiple route profiles and one real team can use the kit without central services or hand-maintained spreadsheets doing the real work.
