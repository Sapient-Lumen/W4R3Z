# Track A — Deployable Core (Evidence-based elections stack)

## Quick navigation
- [Curated bundle](BUNDLE.md)
- [Minimum viable release checklist](MVR_CHECKLIST.md)
- [Evidence API surface](../179-evidence-api-surface.md)
- [Observer kit walkthrough](../177-observer-kit-offline-verification-walkthrough.md)

This track is the **deployable core**: the parts of the archive that can wrap real-world election
workflows *today* (especially paper ballots / BMDs) while producing **court-usable evidence**
under partial compromise.


## Posture (A2 now, A3 later)
Track A is intentionally in **A2 (Balanced)** posture today: it prioritizes what can be evaluated, weighed, and deployed without overclaiming.

The long-horizon intent is **A3 (Ambitious)**: as the North Star ecosystem pieces become checkable (attestation, provenance, anti-capture governance), we will promote them into Track A through explicit claim/PO updates.

## What Track A claims (hard claims)
Track A claims are **hard claims**: they must map to proof obligations and evidence artifacts.

Canonical statement of claims/non‑claims:
- `../166-scope-and-claims-contract.md`
- `../167-non-claims-and-boundaries.md`

At a glance, Track A asserts:
- **Dispute‑ready evidence bundles** (PO-005)
- **No undetected equivocation / split‑worlds for published truths** (PO-002, PO-004)
- **Auditability under partial compromise** (PO-001..PO-005)
- **Anti‑grinding public inspections** (PO-101..PO-103)
- **Inspectable human process** (PO-003, PO-005)
- **Casting‑method agnosticism (paper‑compatible by default)**

## What Track A does NOT require
Track A does **not** require internet ballot return to be safe. It aims to improve *evidence and
auditability* regardless of casting method.

## Recommended read order
1. `../154-project-scope-and-track-map.md`
2. `../01-threat-model.md`
3. `../04-transparency-log.md`
4. `../23-witness-gossip-and-cross-checkpointing.md`
5. `../63-results-api-and-enr-hardening.md` + `../104-audience-targeted-suppression-and-parity.md`
6. `../131-monitor-accountability-and-public-inspections.md`
7. `../145-mmd-style-deadlines-for-evidence-publication.md` + `../149-coverage-metrics.md`
8. Operational layer: `../08-operations.md` and the checklists in `../../artifacts/checklists/`

## Track A “definition of done” (evidence-centric)
- The **claim/evidence matrix** (`../../artifacts/claims/claim-evidence-matrix.csv`) is populated for
  all Track A claims and each claim maps to:
  - at least one **Proof Obligation** (`../159-proof-obligations-ledger.md`)
  - concrete evidence objects (schemas) + checklists/drills
- A release gate exists (`../162-release-and-ci-evidence-pipeline.md`) that prevents silent drift.

## Evidence packaging
Track A evidence artifacts SHOULD be published as `EvidenceEnvelope` objects (see `docs/173` and `docs/176`) and bundled in public packets verifiable offline (see `docs/177`).
