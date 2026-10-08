# Kernel interface contract 0: Package Intake Review Kit

## Identity
- candidate: **Package Intake + Release Boundary Review**
- governing kernel: `kernels/top-band-v0/package-intake-review-kit.v0.md`
- governing slice: `slices/top-band-v0/package-intake-review-kit.slice0.md`
- current verdict context: `advance`
- contract codename: `package-intake-review-kit/contract0`

## Contract scope
Fix the first explicit local surface for dependency and release-boundary review across route profiles.
This contract is for **local reviewable decisions**, not for global trust scoring.

## Public surfaces
### Commands
1. `intake review --route-profile <profile> --project <path> --out <receipt.json>`
2. `intake waive --receipt <receipt.json> --reason <text|file> --owner <id> --expires <date> --out <waiver.json>`
3. `intake quarantine --receipt <receipt.json> --reason <text|file> --out <quarantine.json>`
4. `intake drill --route-profile <profile> --scenario <id> --out <drill.json>`

### Rendered/operator surfaces
- one intake receipt
- one waiver receipt
- one quarantine receipt
- one incident drill report
- one unsupported-state receipt for profile or evidence gaps

## Required inputs
- route profile id
- project manifest and lockfile inputs
- workflow metadata where publishing or release boundary is involved
- registry / registry-route identity
- selected advisory or incident scenario for drills

## Emitted artifact families
- `route-profile/v0`
- `intake-receipt/v0`
- `waiver-receipt/v0`
- `quarantine-receipt/v0`
- `incident-drill-report/v0`
- `unsupported-state-receipt/v0`

Minimum intake-receipt fields should include:
- route profile id
- package or dependency scope reviewed
- owner / reviewer identity
- route assumptions
- provenance / publishing posture
- advisory / capability / provenance evidence imports used
- decision outcome
- required follow-ups
- expiry / re-review trigger

## Stable imports
Allowed stable imports:
- manifests and lockfiles
- dependency graph data
- workflow metadata
- explicit registry / route configuration
- current published advisories or equivalent review inputs

## Optional experimental imports
Allowed but caveated imports:
- capability-analysis outputs
- provenance receipts beyond baseline workflow metadata
- Cargo SBOM pre-cursor outputs
- registry-specific anomaly signals or vendor-specific data

Rule: alternate-registry posture must never silently inherit crates.io assumptions when proof is absent.

## Versioning and compatibility posture
- `contract0` is receipt-additive.
- Unknown evidence blocks must be ignorable.
- Every receipt must remain useful when optional experimental signals are absent.
- Waiver and quarantine receipts must preserve links back to the originating intake receipt.

## Negative states / receipts
The contract must preserve receipts for:
- incomplete route profiles
- unavailable provenance or capability signals
- alternate-registry uncertainty
- advisory ambiguity
- drills that do not reproduce the target route posture confidently

## Proving-ground invocation
A valid proving-ground run should include:
1. one crates.io Trusted Publishing route;
2. one token-based publish route;
3. one alternate-registry route with explicit uncertainty preserved;
4. one incident drill against a recent incident class or advisory shape.

## Refused expansions
Do **not** treat `contract0` as permission for:
- global trust scores,
- mandatory enterprise-wide enforcement,
- hosted dashboards,
- or organization-wide automatic blocking as the first product move.

## Exit criteria
This contract may widen only after:
- multiple route profiles are exercised successfully,
- at least one real team uses the local receipts without spreadsheets doing the real work,
- and route-specific uncertainty remains explicit instead of being normalized away.
