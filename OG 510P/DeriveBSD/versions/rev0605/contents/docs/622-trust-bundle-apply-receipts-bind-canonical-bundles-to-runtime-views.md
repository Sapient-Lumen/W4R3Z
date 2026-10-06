# Trust-bundle apply receipts bind canonical bundles to runtime views

**Tier:** B (Cross-cutting evidence boundary)  
**Profiles:** A, B, C, D  
**Pillars:** supply-chain, operability, reproducibility  
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt, Adapter→Shadow→Replace  

DeriveBSD already decided that trust roots are governed artifacts and that trust-bundle drift is reviewable.
This doc fixes the next smaller but more implementation-shaping question:
**what typed artifact proves which exact trust-bundle view a host or unit actually served?**

Put differently: **what exact trust view did this host/unit really serve?**

This is intentionally **not** a new product-profile key and **not** a new trust subsystem.
It is the missing receipt boundary between canonical `pki-trust-bundle` objects and the renderer/application adapters that make them runtime-usable.
This is not a new product-profile key.

See also:
- ADR: `adrs/ADR-0212-trust-bundle-apply-receipts-bind-canonical-bundles-to-runtime-views.md`
- trust-bundle posture by profile: `docs/480-trust-bundle-posture-by-profile.md`
- PKI lifecycle lane: `docs/228-pki-and-identity-lifecycle-as-evidence.md`
- trust bundles as artifacts: `docs/304-trust-bundles-and-ca-injection-as-artifacts.md`
- shadow-trust containment: `docs/327-shadow-trust-and-system-ca-governance.md`
- trust-bundle diff review surface: `docs/434-pki-trust-bundle-diff-as-review-surface.md`

## Why this needs a hard decision

The archive already had the right conceptual story:

- trust roots live in canonical `pki-trust-bundle` objects,
- drift is reviewed through `pki.trust.bundle.diff`,
- and renderers/adapters are not the source of truth.

But there was still no official answer to the operationally painful question:

**what exact trust view did this host or unit really serve?**

Without a typed receipt, the archive drifts back into folklore:

- the canonical bundle digest is known, but the concrete rendered CA view stays adapter-private,
- support bundles can name policy objects but not the exact output a workload consumed,
- shadow-trust investigations can identify bypasses but cannot point at the official trust view they bypassed,
- and changing distribution APIs (`certctl`, p11-kit extracts, Kubernetes trust managers, SPIFFE bundle delivery, etc.) quietly become the real truth instead of replaceable adapters.

A coherent archive needs a stable proof boundary that survives renderer and distribution churn.

## Official artifact

- Receipt kind: `pki.trust.bundle.apply.receipt`
- Schema: `spec/pki.trust.bundle.apply.receipt.schema.json`
- Example: `spec/examples/pki.trust.bundle.apply.receipt.json`

The receipt is **evidence-only**.
It proves that a canonical `pki-trust-bundle` digest was rendered and applied to a specific target view.
It does **not** replace the canonical bundle object as trust-root authority.

## Accepted boundary

### 1) Canonical trust roots stay authoritative

`pki-trust-bundle` remains the authority object for trust roots and intended use.
In other words, pki-trust-bundle remains authoritative.
`pki.trust.bundle.apply.receipt` is evidence about which canonical bundle digest actually reached a target runtime view.

### 2) The receipt binds bundle → target → rendered outputs

Each apply receipt binds together:

- `bundle_digest` — the canonical trust bundle that governed the act
- `purpose` — the purpose-scoped trust view (`public-web`, `internal-mtls`, `package-verification`, etc.)
- `target` — the host generation or unit runtime that received the view
- `renderings[]` — the deterministic output digests actually served to the adapter/runtime
- `result.status` — whether the apply actually succeeded, was rendered-only, was blocked, or failed

That is the minimum useful proof surface.

### 3) One receipt proves one view

One `pki.trust.bundle.apply.receipt` proves one canonical bundle/purpose/target view.
If a host generation or runtime consumes multiple trust bundles or purposes, that yields multiple receipts instead of one giant ambient trust-state blob.

### 4) Diff review and apply proof stay separate

`pki.trust.bundle.diff` answers **what changed**.
`pki.trust.bundle.apply.receipt` answers **what exact view was served**.

The archive should not collapse these into one object.
Review surfaces and activation proof solve different problems and compose better when kept separate.

### 5) Renderer and distributor APIs stay adapter territory

The receipt records deterministic output digests and target metadata, not raw adapter-private state dumps.
That keeps the archive stable even when external control-plane APIs churn.

Examples of adapter territory include:

- `certctl`-style trust-store management,
- p11-kit trust-module or extract adapters,
- NSS DB renderers,
- Kubernetes trust-bundle distributors,
- SPIFFE bundle delivery/federation helpers.

Those may change shape.
The canonical trust-root object and the apply-proof receipt do not.

### 6) Events should point at exact apply proof

`pki-event` may carry `pki_trust_bundle_apply_receipt_digest` for `pki.trust-bundle.updated` milestones.
That keeps journals and support bundles digest-joined to exact apply proof rather than vague “trust bundle changed” folklore. Official incident/support bundles now also have a typed join for that proof through `pki_trust_bundle_apply_receipt_digests`, so support handoff can carry both the reviewed canonical bundle digest and the exact served trust-view proof without promoting renderer-specific state into authority (`docs/624-incident-bundles-carry-trust-bundle-apply-proof-by-digest.md`).

## Practical meaning

### A) Secure fleet host

- Fleet lanes already keep trust roots purpose-scoped and diff-gated.
- This receipt now gives fleets typed proof of which purpose-scoped trust view was actually active for a host generation or service runtime.
- That is stronger and more portable than trusting whichever local trust-manager or package hook happened to run.

### B) Secure workstation

- Workstations already keep extra roots trusted-UI-visible instead of ambient.
- This receipt gives the humane support/export answer to “what system trust view did the device actually serve?” without normalizing raw store dumps.
- Trusted-UI-visible root changes can now point at exact apply proof instead of just policy objects.

### C) General-purpose OS

- C keeps compatibility adapters real.
- This receipt keeps the managed baseline explicit without pretending every foreign trust helper inherits the full Derive truth model.
- Adapter evidence remains explicit rather than silently redefining the canonical trust story.

### D) Appliance factory / regulatory

- D already requires fixed-purpose, strongly governed trust bundles.
- This receipt gives production/audit lanes deterministic proof of exactly which approved trust view was activated without turning raw trust material into the routine export artifact.

## Cross-profile invariants

Regardless of profile:

- `pki-trust-bundle` stays authoritative for trust roots,
- `pki.trust.bundle.diff` stays the compact review surface,
- `pki.trust.bundle.apply.receipt` is the digest-first proof of the actual served runtime view,
- renderer/distributor outputs remain adapter territory rather than new authority objects,
- and exported trust proof should stay smallest-sufficient by default.

## What remains open

This doc does **not** freeze:

- the final trust-portal API,
- the final renderer set shipped by default,
- the exact shadow-trust waiver object,
- the exact stronger export path for rich trust diagnostics,
- or the final mapping between build-time generation rendering and runtime delivery in every backend.

The expensive hard decision is smaller:
DeriveBSD now has a typed receipt for the exact trust-bundle view it served.

Last updated: 2026-03-21r354
