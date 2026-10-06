# Incident bundles carry secret-state and action proof by digest

**Tier:** B (Cross-cutting evidence boundary)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation, reproducibility  
**Patterns:** Broker→Lease→Receipt, Bundles  

DeriveBSD already decided that secret handling should be explicit, brokered, and metadata-first.
This doc fixes the smaller but implementation-shaping support/export question the archive still left fuzzy in practice:

**how does the official incident/support bundle contract name safe current secret posture and the exact secret actions that materially shaped the incident?**

The answer is intentionally narrow.
It is not a new secret store, not a provider debug dump, and not a permission slip to ship secret bytes.
It is the missing decision to make the existing `secret-snapshot` + `secret-receipt` joins real through the official support-handoff contract.

See also:
- ADR: `adrs/ADR-0227-incident-bundles-carry-secret-state-and-action-proof-by-digest.md`
- secret lane: `docs/223-secrets-and-key-management-as-evidence.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- support handoff contract: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`
- bundle plans: `docs/253-bundle-plans-and-deterministic-exports.md`
- evidence spine: `docs/229-evidence-spine-overview.md`

## Why this needs a hard decision

The secret lane already existed:

- `secret-policy` defines inventory and access rules,
- `secret-grant` / lease-shaped authority bound secret access,
- `secret-receipt` keeps provisioning / rotation / materialization explainable,
- and `secret-snapshot` is already the safe metadata surface for current secret posture.

But the official support/export contract still lagged behind that design in practice.
`incident.bundle` could already carry `secret_snapshot_digest` and `secret_receipt_digests`, but the archive still did not explicitly teach that support handoff should use those typed joins when credential health, rotation, unseal, or materialization materially shaped the incident.
Canonical bundle plans also failed to exercise the existing selectors, which left the support-handoff story weaker than the schema.

A coherent archive should let support bundles answer two different questions distinctly:

- **what safe secret posture existed at capture time?**
- **what exact secret actions materially participated in the incident?**

## Accepted boundary

### 1) Bundles may carry exact secret-state context

Support bundles should not force readers to infer current credential posture from provider dashboards, ticket notes, or screenshots.

- `secret_snapshot_digest` names the exact `secret-snapshot` object that belongs to the incident.
- The referenced `secret-snapshot` remains metadata-only and answers which secrets are configured, when they were last rotated, when they are next due, and whether health checks passed.

That keeps current secret posture on the official support contract without teaching the bundle to carry secret bytes.

### 2) Bundles may carry exact secret-action proof

When secret rotation, unseal, materialization, or revocation materially shaped the incident, the bundle may also carry exact `secret-receipt` proof.

- `secret_receipt_digests` name the exact `secret-receipt` objects that matter to the incident.
- Those receipts remain the typed, metadata-only proof of what action ran, through which backend/provider path, under which lease/rotation outcome.

That keeps action proof on typed evidence joins instead of provider dashboards or shell archaeology.

### 3) The official selectors are now treated as real

The canonical include surface already carries `secret_snapshot` and `secret_receipts`.
Because `bundle.plan.selection.include` reuses `incident.bundle` include knobs, the same selectors apply both when planning a support bundle and when recording what the final bundle included.

That means official support-bundle planning can stop treating the secret lane as prose-only.
`bundle.plan` should use `secret_snapshot` / `secret_receipts` when the incident is secret-shaped.

### 4) Keep safe state context separate from action proof

This is the design cut worth preserving.
The archive does **not** collapse all secret evidence into one generic credential-debug field.

- `secret_snapshot_digest` is the typed join for safe current credential posture.
- `secret_receipt_digests` are the typed joins for exact secret actions.

That keeps “what was true at capture time?” and “what exact secret action happened?” separately explainable.

### 5) Secret values stay off the routine support-handoff truth surface

This boundary does not promote raw secret bytes, plaintext env files, provider response bodies, or screenshots into the official bundle truth model.
The bundle contract remains metadata-first:

- exact `secret-snapshot` digest for safe current posture,
- exact `secret-receipt` digests for the participating secret actions,
- no routine secret-value export lane hidden inside support collection.

That keeps the secret lane usable across A–D without degrading the isolation story.

## Practical meaning by product shape

### A / secure fleet host

Fleet incidents can now prove safe credential posture and exact secret-rotation/materialization actions without normalizing provider dashboards or shell notes into support truth.

### B / secure workstation

Workstation support handoff can now export a typed secret-health snapshot and exact secret-action receipts when support needs to explain why an app failed after a brokered secret or attestation-gated release, without shipping raw secret material.

### C / general-purpose OS

C keeps compatibility adapters possible, but the Derive-managed support story now has a typed answer for secret health and exact secret actions instead of generic provider screenshots or env-file folklore.

### D / appliance / factory / regulatory

Production and audit lanes can now show safe current credential posture plus exact rotation/materialization proof without turning support bundles into secret-value carriers.

## Guardrail

- `tools/check_secret_bundle_contract.py`

The guardrail checks that the official bundle selectors and metadata surfaces keep secret state/action proof explicit, that canonical bundle examples bind the real `secret-snapshot` + `secret-receipt` digests, and that the relevant docs keep teaching the same secret/support-bundle story.

## What remains open

This doc does **not** fix:

- the exact UI for previewing secret-health context before export,
- how many recent secret receipts bundle templates should keep by default,
- whether future support handoffs should join `secret-event` summaries directly,
- or broader provider-specific debug export lanes.

The expensive hard decision is smaller:
DeriveBSD incident bundles no longer get to mention secret health or secret actions only in prose while hand-waving the exact `secret-snapshot` / `secret-receipt` proof.

Last updated: 2026-03-21r367
