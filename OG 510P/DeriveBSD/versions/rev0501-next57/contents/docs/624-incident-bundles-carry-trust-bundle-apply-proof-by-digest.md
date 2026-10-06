# Incident bundles carry trust-bundle apply proof by digest

**Tier:** B (Cross-cutting evidence boundary)  
**Profiles:** A, B, C, D  
**Pillars:** operability, supply-chain, reproducibility  
**Patterns:** Plan→Apply→Receipt, Bundles, Registry→Diff→Gate  

DeriveBSD already decided that trust roots are governed artifacts and that runtime trust views need typed apply proof.
This doc fixes the smaller but implementation-shaping support/export question the archive still left open:

**how does the official incident/support bundle contract carry proof of what exact trust view was actually served?**

The answer is intentionally narrow.
It is not a new PKI subsystem and not a new product-profile key.
It is the missing digest join between the existing trust-bundle apply receipt and the existing support-bundle contract.

See also:
- ADR: `adrs/ADR-0214-incident-bundles-carry-trust-bundle-apply-proof-by-digest.md`
- trust-view apply proof: `docs/622-trust-bundle-apply-receipts-bind-canonical-bundles-to-runtime-views.md`
- PKI lifecycle lane: `docs/228-pki-and-identity-lifecycle-as-evidence.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- support handoff contract: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`

## Why this needs a hard decision

`ADR-0212` already fixed the core trust boundary:

- `pki-trust-bundle` remains authoritative,
- `pki.trust.bundle.diff` remains the review surface,
- and `pki.trust.bundle.apply.receipt` proves the exact trust view a host or unit actually served.

But the official support/export contract still lagged behind that decision.
`incident.bundle` had room for the canonical trust bundle digest and issuance receipts, but not for the apply-proof receipts that explain what runtime trust view was really active.

That is expensive because it quietly pushes responders back toward renderer dumps, control-plane screenshots, or shell archaeology right after the archive had already paid to define a better answer.

A coherent archive should let support bundles answer both:

- **what trust roots were approved?**
- **what exact trust view was actually served?**

## Accepted boundary

### 1) Bundles keep review proof and apply proof separate

Support bundles should not collapse reviewed trust-root authority and runtime-view activation into one field.

- `pki_trust_bundle_digest` names the canonical reviewed trust bundle.
- `pki_trust_bundle_apply_receipt_digests` name the exact `pki.trust.bundle.apply.receipt` objects that prove what trust view was actually served.

This is the same split the archive already uses elsewhere:
review surfaces say **what changed** and apply receipts say **what actually took effect**.

### 2) The official selector is now typed

The canonical include surface now carries `pki_trust_bundle_apply_receipts`.
Because `bundle.plan.selection.include` reuses `incident.bundle` include knobs, the same selector works both when planning a bundle and when recording what the final bundle included.

That keeps trust-view activation proof on the official support-bundle lane instead of in `extra` or collector-private rules.

### 3) Include apply proof when trust-view activation matters

The rule is intentionally conditional.
The archive does **not** require every incident bundle to include every historical trust-view apply receipt.
Instead, bundles should carry recent `pki.trust.bundle.apply.receipt` digests when trust-view activation changed or is relevant to the incident/support story.

Examples:

- a rollout changed package-verification trust on a fleet host,
- a workstation support case needs to prove what system trust view was active,
- a service identity failure depends on which purpose-scoped trust roots a unit runtime actually consumed,
- or a factory/regulatory export needs exact proof of the approved trust view active during an event window.

### 4) renderer-private dumps remain stronger/debugging evidence

This boundary does not promote renderer/distributor state into the official bundle truth model.
Raw adapter dumps, extracted CAfiles, or control-plane-specific status output may still exist as explicit stronger/debug evidence, but the default support-bundle join stays digest-first:

- canonical bundle digest,
- apply-receipt digest,
- optional journal/event joins that point at the same proof.

That keeps renderer churn and support/export truth separate.

## Practical meaning by product shape

### A / secure fleet host

Fleet incidents often need to answer whether a new trust view really reached the generation or workload that failed.
This boundary lets support bundles prove that without normalizing renderer-private state dumps as the real source of truth.

### B / secure workstation

Workstation support cases need a humane answer to "what trust roots did this device really serve?" without turning support export into raw trust-store archaeology.
This boundary keeps the answer typed and reviewable.

### C / general-purpose OS

C keeps compatibility adapters real.
This boundary keeps the Derive-managed trust story explicit in bundles without pretending every foreign helper inherits the full authority model.

### D / appliance / factory / regulatory

Production and audit lanes often care about exact approved trust state at a specific moment.
This boundary gives deterministic bundle-ready proof of that state without making raw trust material the routine export artifact.

## Guardrail

- `tools/check_trust_bundle_apply_bundle_contract.py`

The guardrail checks that the official bundle selector and metadata surfaces carry trust-view apply proof explicitly, that the canonical bundle example binds real trust-bundle/apply-receipt digests, and that the relevant docs keep teaching the same review-vs-apply split.

## What remains open

This doc does **not** fix:

- the exact default bundle templates for every incident class,
- the retention policy for old trust-view apply receipts,
- the richer export path for raw trust diagnostics,
- or the final UX for displaying trust-view changes inside support tooling.

The expensive hard decision is smaller:
DeriveBSD incident bundles no longer get to carry only intended trust roots while hand-waving the exact served trust view.

Last updated: 2026-03-21r354
