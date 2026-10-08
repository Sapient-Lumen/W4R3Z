# Track A — Deployable Core (Evidence-based elections stack)

## Quick navigation
- [Curated bundle](BUNDLE.md)
- [Minimum viable release checklist](MVR_CHECKLIST.md)
- [Evidence API surface](../179-evidence-api-surface.md)
- [Observer kit walkthrough](../177-observer-kit-offline-verification-walkthrough.md)
- [Election lifecycle evidence map](../215-election-lifecycle-evidence-map.md)
- [Incident triage quickmap](../216-incident-triage-and-evidence-quickmap.md)
- [Court evidence bundle recipes](../211-court-evidence-bundle-recipes.md)
- [Incident comms as evidence](../186-incident-communications-as-evidence.md)
- [PublicNotice feeds (bounded discovery)](../200-publicnotice-feeds-and-mirror-index.md)
- [Official channel directory (where to look)](../203-official-channel-directory-as-evidence.md)
- [Well-known discovery (bootstrap from domain)](../204-well-known-election-stack-discovery.md)
- [Cache/freshness posture for public pointer surfaces](../205-cache-and-freshness-controls-for-public-surfaces.md)
- [Digest cards (low-bandwidth publication)](../206-digest-cards-and-low-bandwidth-publication.md)
- [Public surface parity snapshots (split-view evidence)](../201-public-surface-parity-snapshots.md)
- [Compact request-context notes (req/vary/age)](../232-compact-request-context-notes.md)
- [Public fingerprint report (mirror equality checks)](../226-public-fingerprint-report-for-publishable-packets.md)
- [Public surface inspection challenges (escalate split views)](../202-public-surface-challenges-and-escalating-split-views.md)
- [Comms authenticity (synthetic media minimum)](../194-synthetic-media-and-comms-authenticity-minimum-controls.md)
- [Rumor control + status boards](../195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md)
- [Official surface security snapshots](../199-official-surface-security-snapshots.md)
- [Precinct closeout evidence (poll tapes + seals)](../197-precinct-closeout-evidence-capture-and-publication.md)
- [Closeout index (omission detection)](../198-precinct-closeout-index-and-omission-detection.md)

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
5. `../63-election-night-reporting-and-public-results-security.md` + `../104-audience-targeted-suppression-and-parity.md`
6. `../131-monitor-accountability-and-public-inspections.md`
7. `../145-mmd-style-deadlines-for-evidence-publication.md` + `../174-coverage-accounting-and-representativeness.md` + `../187-publication-compliance-and-coverage.md`
8. Operational layer: `../08-operations.md` and the checklists in `../../artifacts/checklists/`
9. Public comms as evidence: `../186-incident-communications-as-evidence.md` + `../194-synthetic-media-and-comms-authenticity-minimum-controls.md`

## Track A “definition of done” (evidence-centric)
- The **claim/evidence matrix** (`../../artifacts/claims/claim-evidence-matrix.csv`) is populated for
  all Track A claims and each claim maps to:
  - at least one **Proof Obligation** (`../159-proof-obligations-ledger.md`)
  - concrete evidence objects (schemas) + checklists/drills
- A release gate exists (`../162-release-and-ci-evidence-pipeline.md`) that prevents silent drift.

## Evidence packaging
Track A evidence artifacts SHOULD be published as `EvidenceEnvelope` objects (see `docs/173` and `docs/176`) and bundled in public packets verifiable offline (see `docs/177`).
