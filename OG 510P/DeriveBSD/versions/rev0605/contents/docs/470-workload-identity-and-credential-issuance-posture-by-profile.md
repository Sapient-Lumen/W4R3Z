# Workload identity and credential-issuance posture by profile

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, supply-chain, operability  
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt  

DeriveBSD already knows how to **issue**, **broker**, and **receipt** identity-shaped artifacts.
What this doc decides is narrower and more important for coherence:
**what is the default workload-identity / credential-issuance posture in each product shape?**

This is intentionally **not** a mesh or PKI-stack doc.
It is a product-default decision.

See also:
- ADR: `adrs/ADR-0060-workload-identity-and-credential-issuance-posture-by-profile.md`
- workload identity lane: `docs/181-workload-identity-and-secretless-deploys.md`
- PKI + identity lifecycle: `docs/228-pki-and-identity-lifecycle-as-evidence.md`
- dynamic service identities: `docs/240-dynamic-service-identities.md`
- product profiles: `docs/411-product-profiles-as-compilation-target.md`

## Why this needs a hard decision

Systems that avoid deciding their workload-identity posture eventually decide it through drift:

- services ship with long-lived API tokens or cloud credentials,
- humans and workloads share the same trust/account artifacts,
- production images carry static shared secrets because “mesh later” never arrives,
- and compatibility exceptions quietly become the only path anybody uses.

DeriveBSD already says secrets, brokers, identities, and attestations matter.
That only becomes coherent if the archive fixes the **default authority model for workload credentials** instead of leaving it to sidecars, wikis, and environment-variable folklore.

## Product-shape defaults

| Profile | `workload_identity` default | Practical meaning |
|---|---|---|
| A (`fleet_host`) | `brokered-short-lived-digest-bound-headless` | Fleet services get short-lived workload identity bound to what is running; shared static service tokens are not the baseline. |
| B (`workstation`) | `brokered-short-lived-appvm-preferred-user-identity-separate` | AppVMs and local service-like workloads should prefer short-lived workload identity, while human login/account authority remains a separate lane. |
| C (`general_os`) | `brokered-preferred-explicit-static-token-adapter` | Workload identity is preferred, but classic static-token/file-credential workflows remain as explicit adapters for compatibility. |
| D (`appliance_factory`) | `brokered-attested-short-lived-no-static-production-secrets` | Production/factory workloads use short-lived identities by default; static shared production secrets are out of bounds in shipped images and normal station workflows. |

These values live in `spec/examples/product.profiles.json` and are guarded by `tools/check_product_profiles.py`.

## Cross-profile invariants

Regardless of profile:

- issuance must be short-lived and receipted rather than “drop a token on disk and hope rotation exists later”
- workload identity must bind to what is actually running or to an explicit reviewed adapter declaration
- human identity and workload identity remain separate authority lanes
- trust-bundle and issuer changes stay typed, visible, and reviewable
- static shared secrets are an explicit exception path, not a silent baseline

## What this fixes by profile

### A) Secure fleet host (`fleet_host`)

Default: `brokered-short-lived-digest-bound-headless`

- Fleet services should authenticate with short-lived workload identity.
- Issuance should bind to deployment/runtime identity rather than to host-local token files.
- Secret retrieval should prefer identity → brokered operation/token exchange over image-baked API keys.

### B) Secure workstation (`workstation`)

Default: `brokered-short-lived-appvm-preferred-user-identity-separate`

- Workstation AppVMs and local service-like tools should prefer short-lived workload identity where service auth is needed.
- Human login/account authority remains separate: personal browser sessions, OIDC, and user-held credentials are not the same thing as workload identity.
- This keeps “cloud/dev ergonomics” compatible with a real no-static-token baseline.

### C) General-purpose OS (`general_os`)

Default: `brokered-preferred-explicit-static-token-adapter`

- Workload identity is the preferred derived lane.
- Compatibility paths for legacy software, classic config files, or static tokens remain possible, but must be explicit adapters.
- That keeps C viable without silently redefining stricter A/B/D posture.

### D) Appliance factory / regulatory (`appliance_factory`)

Default: `brokered-attested-short-lived-no-static-production-secrets`

- Production and factory services should use short-lived identities by default.
- Issuance may depend on attested/measured or other stronger admission lanes.
- Shipping or normalizing shared production tokens/secrets in images, stations, or service kits is out of bounds.

## What this does *not* decide

Still open:

- trust-domain naming and federation shape
- exact selector vocabulary and digest/instance binding rules
- which key-handle/backing choices are day-0 defaults (TPM, platform keystore, broker-held, in-guest)
- exact workload API transport and adapter surface
- detailed issuance/evidence budgets, redaction, and learning ergonomics

That work stays implementation-level.
This doc only fixes the product-default boundary so the archive can keep converging without drifting.

## Design cue from current systems

A few lessons are stable:

- short-lived workload identity is a smaller default surface than shared static credentials
- attestation or selector-based binding matters because “which workload got this identity?” must be answerable
- human sign-in and workload identity are different authority problems and get worse when merged
- dynamic secret/token issuance is useful when it is derived from identity and leasing rather than embedded in images or app state

DeriveBSD should steal those lessons while keeping the issuer stack replaceable.

Last updated: 2026-03-06r199
