# Incident bundles carry attestation proof by digest

**Tier:** B (Cross-cutting evidence boundary)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation, supply-chain  
**Patterns:** Plan→Apply→Receipt, Bundles  

DeriveBSD already decided that measured posture should be explicit, receipted, and reviewable.
This doc fixes the smaller but implementation-shaping support/export question the archive still left fuzzy in practice:

**how does the official incident/support bundle contract name the exact measured-boot evidence, verifier reference scope, and verifier judgment that materially shaped the incident?**

The answer is intentionally narrow.
It is not a verifier backend, not a promise to export raw TPM logs, and not permission to smuggle screenshots or portal dumps into bundle truth.
It is the missing decision that makes the existing attestation support-handoff lane real.

See also:
- ADR: `adrs/ADR-0229-incident-bundles-carry-attestation-proof-by-digest.md`
- attestation lane: `docs/226-platform-posture-and-attestation-results-as-evidence.md`
- measured-boot lane: `docs/176-measured-boot-attestation.md`
- boot manifests + replay: `docs/313-boot-manifests-and-eventlog-replay.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- support handoff contract: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`
- bundle plans: `docs/253-bundle-plans-and-deterministic-exports.md`
- evidence spine: `docs/229-evidence-spine-overview.md`

## Why this needs a hard decision

The attestation lane already existed:

- `boot.attestation` captured exact measured-boot evidence,
- `attestation.reference` captured the verifier/reference scope used to judge that evidence,
- and `attestation.receipt` captured the verifier's time-bounded judgment.

But the official support/export contract still lagged behind that design in practice.
`incident.bundle` could already carry `boot_attestation_digest`, `attestation_reference_digest`, and `attestation_receipt_digests`, but the archive still did not explicitly teach that support handoff should use those typed joins when measured posture materially shaped the incident.
Canonical bundle plans also could not request that lane explicitly, which left the attestation story half-real even though the bundle metadata already had the right fields.

A coherent archive should let support bundles answer three different questions distinctly:

- **what exact measured-boot evidence did the host produce?**
- **what reference scope/policy did the verifier compare it against?**
- **what exact verifier judgment materially participated?**

## Accepted boundary

### 1) Bundles may carry exact attestation posture proof

Support bundles should not force readers to infer measured posture from verifier dashboards, portal screenshots, or ticket prose.

- `boot_attestation_digest` names the exact `boot.attestation` object that materially belongs to the incident.
- `attestation_reference_digest` names the exact `attestation.reference` object that explains the verifier/reference scope.
- `attestation_receipt_digests` name the exact `attestation.receipt` objects that explain the verifier's judgment.

That keeps exact measured posture on the official support contract without teaching the bundle to carry verifier-private debug databases or raw TPM material as routine truth.

### 2) Keep evidence, reference scope, and verdict distinct

This is the design cut worth preserving.
The archive does **not** collapse attestation posture into one generic verifier-debug field.

- `boot_attestation_digest` is the typed join for the exact measured-boot evidence.
- `attestation_reference_digest` is the typed join for the exact verifier/reference scope.
- `attestation_receipt_digests` are the typed joins for the exact verifier judgments.

That keeps “what the host proved,” “what it was compared against,” and “what the verifier concluded” separately explainable.

### 3) The official selectors are now treated as real

The canonical include surface now carries `boot_attestation`, `attestation_reference`, and `attestation_receipts`.
Because `bundle.plan.selection.include` reuses `incident.bundle` include knobs, the same selectors apply both when planning a support bundle and when recording what the final bundle included.

That means official support-bundle planning can stop treating measured posture as prose-only.
`bundle.plan` should use those selectors when the incident is posture/admission/identity-shaped.

### 4) Attestation evidence stays metadata-first on the routine handoff lane

This boundary does not promote raw event logs, verifier databases, portal exports, or screenshots into the official bundle truth model.
The bundle contract remains metadata-first:

- exact `boot_attestation_digest` for measured-boot evidence,
- exact `attestation_reference_digest` for verifier/reference scope,
- exact `attestation_receipt_digests` for verifier judgments,
- no routine verifier-private blob lane hidden inside support collection.

That keeps the attestation lane usable across A–D without degrading the isolation story.

## Practical meaning by product shape

### A / secure fleet host

Fleet incidents can now prove exactly what measured posture the host presented, what reference scope it was judged against, and what verifier judgment materially gated admission or secret release.

### B / secure workstation

Workstation support handoff can now export exact posture proof when brokered actions depend on measured state, without shipping raw firmware logs or verifier portal dumps.

### C / general-purpose OS

C keeps compatibility adapters possible, but the Derive-managed support story now has a typed answer for measured posture instead of verifier screenshots or shell archaeology.

### D / appliance / factory / regulatory

Production and audit lanes can now show exact posture evidence and verifier judgment during an incident window without turning support bundles into raw attestation exports.

## Guardrail

- `tools/check_attestation_bundle_contract.py`

The guardrail checks that the official bundle selector and metadata surfaces keep measured posture explicit, that canonical bundle examples bind the real `boot.attestation`, `attestation.reference`, and `attestation.receipt` digests, and that the relevant docs keep teaching the same attestation/support-bundle story.

## What remains open

This doc does **not** fix:

- the exact default bundle templates for every posture/admission incident class,
- whether future support handoffs should also join richer event-log replay material directly,
- how many recent verifier receipts bundle templates should keep by default,
- or broader verifier-specific debug export lanes.

The expensive hard decision is smaller:
DeriveBSD incident bundles no longer get to mention measured posture only in prose while hand-waving the exact `boot.attestation`, `attestation.reference`, and `attestation.receipt` proof.

Last updated: 2026-03-21r369
