# Product-profile default vocabulary boundary

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** reproducibility, isolation, operability  
**Patterns:** Registry→Diff→Gate  

DeriveBSD wants A/B/C/D to be real compilation targets without turning
`product.profiles` into a second policy language.

This doc fixes the boundary around `product.profiles.defaults`.

See also:
- ADR: `adrs/ADR-0091-product-profile-default-vocabulary-boundary.md`
- telemetry overlap decision: `adrs/ADR-0093-no-separate-telemetry-product-profile-key.md`, `docs/503-telemetry-is-not-a-product-profile-default-boundary.md`
- product profiles: `docs/411-product-profiles-as-compilation-target.md`
- schema: `spec/product.profile.schema.json`
- example: `spec/examples/product.profiles.json`

## Accepted boundary

`product.profiles.defaults` is a **flat map of symbolic default lanes**.
It is intentionally small, stable, and comparative across product shapes.

That means:

- default keys are an allowlisted vocabulary, not arbitrary feature names,
- default values are symbolic strings, not nested policy objects,
- structured policy still lives in dedicated schemas,
- and hard product-shape promises remain in `required_invariants` plus the per-lane docs.

## Canonical default-key registry

The default-key vocabulary for v0 is:

<!-- registry:start -->
- `runtime` — runtime execution posture / primary isolation lane
- `removable_media` — removable-media intake posture
- `usb_isolation` — USB / device-domain mediation posture
- `network_egress` — outbound network authority posture
- `dns_resolution` — DNS mediation posture when hostnames are used
- `network_ingress` — inbound listen / service exposure posture
- `networking` — host topology mutation posture
- `remote_assistance` — support / remote-control posture
- `private_keys` — private-key handling posture
- `home_identity` — human identity / home-state posture
- `data_at_rest` — data-at-rest encryption / unlock posture
- `evidence` — evidence collection posture
- `evidence_exports` — export / support handoff posture
- `firmware_updates` — firmware update posture
- `updates` — host update delivery / finalization posture
- `store_retention` — store retention / garbage-collection posture
- `installation_recovery` — installation / recovery posture
- `destructive_reprovision` — destructive reprovision / reset posture
- `kernel_mutation` — runtime kernel mutation posture
- `device_authority` — device-node / raw-device authority posture
- `high_risk_approvals` — high-risk approval / quorum posture
- `operator_access` — operator-access posture
- `time_authority` — trustworthy-time posture
- `trust_bundles` — trust-root / trust-bundle posture
- `platform_provenance` — measured platform / attestation posture
- `workload_identity` — service / workload identity posture
- `backups` — backup / restore posture
- `compat` — compatibility-adapter posture
- `devshells` — developer-shell posture
- `interactive_ui` — interactive desktop/UI posture
- `fuzzing` — fuzzing / regression-gate posture
<!-- registry:end -->

## Why this boundary matters

The canonical observability/export posture remains split across `evidence`, `evidence_exports`, and `network_egress`; `telemetry` is intentionally **not** a separate default key (see `docs/503-telemetry-is-not-a-product-profile-default-boundary.md`).

Without a fixed vocabulary, `product.profiles` quietly becomes a second options tree:
new keys appear ad hoc, old ones overlap, and A/B/C/D drift from being
reviewable compilation targets into a bag of half-policy folklore.

The archive already has dedicated artifacts for structured authority and policy.
Profiles should choose *posture* and *default lane*, not absorb those artifacts.

## What belongs elsewhere

Do **not** add a new default key when the real need is one of these:

- a structured authority/policy object with its own schema,
- a new runtime or evidence lane,
- a profile-specific implementation detail,
- or prose-only nuance that belongs in `notes` / `required_invariants`.

If the change alters the stable cross-profile vocabulary itself, that is an ADR-scale decision.

## How to extend the vocabulary

Adding, renaming, or removing a default key requires all of:

1. an ADR,
2. updating `spec/product.profile.schema.json`,
3. updating this registry doc,
4. updating relevant profile docs / examples,
5. keeping the guardrails green.

This makes vocabulary growth intentionally expensive enough to prevent drift.

## Guardrails

- `tools/check_product_profiles.py` keeps the critical A/B/C/D posture values and invariants wired.
- `tools/check_profile_default_vocabulary.py` keeps the schema allowlist, this registry doc, and the example profile file aligned.

## Practical reading rule

When reviewing a profile change, ask two questions in order:

1. is this a change to an **existing default key/value**?
2. or is someone trying to invent a **new vocabulary key** that should really be a dedicated spec or ADR?

That simple split keeps product profiles small, comparable, and implementable.

Last updated: 2026-03-08r232
