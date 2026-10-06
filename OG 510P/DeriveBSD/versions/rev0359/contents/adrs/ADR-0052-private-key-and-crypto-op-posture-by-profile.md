# ADR-0052: Private-key and crypto-operation posture by profile

- **Status:** Accepted
- **Date:** 2026-03-06

## Context

DeriveBSD already has a credible **crypto authority** lane:
`docs/306-crypto-operations-portal-and-split-keys.md`, `docs/392-crypto-key-policies-and-nonexportable-handles.md`, and `docs/437-split-secrets-brokers.md` make a strong case for **operations, not key bytes**.

What the archive still lacked was the **product-shape default**.
Without that, A–D drift toward incompatible and unsafe assumptions:

- A quietly grows host-local file keys and ad-hoc agent sockets,
- B forgets that risky apps should request crypto operations rather than hold raw key bytes,
- C normalizes file-backed key sprawl as the default compatibility story,
- D ships production or manufacturing keys in places that should never hold them.

We do **not** need to decide every backend, receipt field, or protocol here.
We do need a stable, checkable answer to:

- whether non-exportable keys are the default,
- when user presence is required vs prohibited,
- where adapter fallbacks are acceptable,
- and how offline/quorum expectations differ across product shapes.

## Decision

We define private-key handling as a **profile-shaped default** and thread it into `spec/examples/product.profiles.json`.

### A) `fleet_host`

Default posture: `brokered-nonexportable-headless-policy-gated`

- Private-key use is brokered and non-exportable by default.
- Headless hosts do **not** assume interactive user presence.
- Policy/quorum gates may apply, but long-lived exportable private-key files on workload hosts are not the baseline.
- Agent/socket interop, if used, remains an explicit adapter lane rather than ambient host authority.

### B) `workstation`

Default posture: `brokered-nonexportable-user-presence-vault-preferred`

- Human-facing key use prefers split-key vaults, platform keystores, smartcards, or hardware-backed handles.
- Risky apps request crypto operations rather than receiving raw private-key bytes by default.
- User presence is the default for high-value interactive key use (sign/decrypt/auth), with secure-attention-gated prompts where applicable.
- Remembered authority must still land in leases or durable policy objects with revoke; ambient background signing is not the baseline.

### C) `general_os`

Default posture: `brokered-preferred-explicit-file-key-adapter`

- Brokered/non-exportable key use is preferred for derived workloads.
- File-backed keys or classic agent sockets may exist only as explicit, reviewable adapter fallbacks.
- Compatibility is allowed, but it stays killable and does not redefine the archive’s default trust model.

### D) `appliance_factory`

Default posture: `offline-or-hsm-quorum-nonexportable`

- Production/manufacturing/release keys stay offline, in HSM/KeyVM-style compartments, or otherwise non-exportable by default.
- Quorum/two-person controls are the default for high-value signing lanes.
- Interactive convenience prompts are not the authority model for production or evidence-bearing flows.
- Exportable private-key files in production/factory images are out of scope by default.

## Consequences

- Product profiles now carry a stable `private_keys` default.
- `tools/check_product_profiles.py` must enforce this boundary so the archive cannot silently drift back toward file-key sprawl or ambient signing authority.
- Open questions narrow to implementation detail: receipt redaction defaults, destination-tag vocabulary, broker identity/routing, backend mapping, and quorum thresholds by key class.

## Non-goals

- Choosing a single concrete key backend for every deployment.
- Designing the entire UI for presence prompts or release-signing ceremonies.
- Forcing every ecosystem integration to abandon adapters on day 0.
