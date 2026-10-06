# Trust-bundle posture by profile

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** supply-chain, operability, reproducibility  
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt, Adapter→Shadow→Replace  

DeriveBSD already has the pieces to treat trust roots as governed artifacts instead of ambient files.
What this doc decides is narrower and more important for coherence:
**what is the default trust-bundle posture in each product shape?**

This is intentionally **not** a trust-portal or renderer-stack spec.
It is a product-default decision.

See also:
- ADR: `adrs/ADR-0070-trust-bundle-posture-by-profile.md`
- trust bundles as artifacts: `docs/304-trust-bundles-and-ca-injection-as-artifacts.md`
- shadow-trust containment: `docs/327-shadow-trust-and-system-ca-governance.md`
- trust-bundle diff review surface: `docs/434-pki-trust-bundle-diff-as-review-surface.md`
- trust-bundle apply proof: `docs/622-trust-bundle-apply-receipts-bind-canonical-bundles-to-runtime-views.md`
- product profiles: `docs/411-product-profiles-as-compilation-target.md`

## Why this needs a hard decision

Every system that avoids deciding trust-store posture eventually decides it through drift:

- fleet services grow embedded CA bundles because nobody blocked the shortcut,
- workstations silently inherit enterprise roots or app-shipped trust stores with no trusted-UI explanation,
- general-purpose systems cannot tell whether local CA overrides are a supported adapter or an embarrassing accident,
- and factory/regulatory deployments claim controlled trust posture while still accepting ad-hoc live root injection.

DeriveBSD already says trust roots and certificates matter.
That only means anything if the archive fixes the **default authority model for trust bundles** instead of leaving it to shell edits and library folklore.

## Product-shape defaults

| Profile | `trust_bundles` default | Practical meaning |
|---|---|---|
| A (`fleet_host`) | `purpose-scoped-diff-gated-shadow-trust-blocking` | Fleet trust roots are purpose-scoped governed artifacts; trust drift goes through typed diffs/review, and official lanes block embedded shadow trust by default. |
| B (`workstation`) | `system-visible-trusted-ui-extra-roots` | The workstation keeps a visible governed system trust baseline; extra enterprise/developer roots land through trusted UI and become reviewable instead of hiding in app sandboxes. |
| C (`general_os`) | `system-preferred-explicit-local-override` | Governed system trust remains preferred, but explicit local CA files/app-specific overrides remain viable adapters for compatibility and experimentation. |
| D (`appliance_factory`) | `fixed-purpose-offline-quorum-bundles` | Production/manufacturing trust roots are fixed-purpose, digest-bound artifacts distributed through offline or strongly approved lanes; live root injection is not the production default. |

These values live in `spec/examples/product.profiles.json` and are guarded by `tools/check_product_profiles.py`.

## Cross-profile invariants

Regardless of profile:

- trust roots should be versioned objects, not unexplained ambient file drift
- trust-bundle changes should be reviewable through typed diff surfaces
- interop renderers remain replaceable adapters rather than the source of truth
- the exact trust view actually served should be proveable through `pki.trust.bundle.apply.receipt` instead of adapter folklore
- purpose-scoped trust is preferable for high-risk lanes even when a profile permits local overrides
- shadow trust must be detectable even where compatibility adapters exist

## What this fixes by profile

### A) Secure fleet host (`fleet_host`)

Default: `purpose-scoped-diff-gated-shadow-trust-blocking`

- Fleet lanes keep trust roots purpose-scoped and digest-pinned.
- Trust-bundle drift is a reviewed operational event, not a package side effect.
- Shadow trust in official lanes is treated as a blocker unless explicitly waived.

### B) Secure workstation (`workstation`)

Default: `system-visible-trusted-ui-extra-roots`

- Workstations need a coherent story for enterprise roots, local proxies, and developer certificates.
- The hard decision is that these flows are allowed only through visible trusted-UI review, not silent app-local bundle mutation.
- This keeps B viable without normalizing invisible trust-root drift.

### C) General-purpose OS (`general_os`)

Default: `system-preferred-explicit-local-override`

- Governed system trust remains the recommended baseline.
- Local CA files, custom bundles, and app-specific trust stores remain explicit adapter territory rather than taboo or ambient default.
- This preserves broad software viability without weakening stricter A/B/D defaults.

### D) Appliance factory / regulatory (`appliance_factory`)

Default: `fixed-purpose-offline-quorum-bundles`

- Production/manufacturing trust roots should arrive as fixed-purpose approved artifacts.
- Stronger approval and offline/OOB handling are the normal posture for trust-root changes.
- “Just add this root on the box” is not acceptable production operational folklore.

## What this does *not* decide

Still open:

- the final canonical trust-bundle encoding(s)
- the exact trust-portal API / handle shape
- the exact shadow-trust waiver object and scanner pattern set
- the exact renderer count shipped on day-0
- workstation/general-OS UX details for inspecting bundle diffs and override scope

That work stays implementation-level.
This doc only fixes the product-default boundary so the archive can keep converging without drifting.

## Design cue from current systems

A few lessons are stable:

- shared trust interfaces help only when the **source of truth** stays explicit and reviewable
- workload-identity bundles and system trust bundles are related but not the same policy surface
- human-facing systems need visible extra-root workflows instead of pretending enterprise roots never happen
- high-assurance production shapes need fixed-purpose trust bundles because ad-hoc root injection destroys provenance

DeriveBSD should steal those lessons while keeping renderers and helper stacks replaceable.

Last updated: 2026-03-21r352
