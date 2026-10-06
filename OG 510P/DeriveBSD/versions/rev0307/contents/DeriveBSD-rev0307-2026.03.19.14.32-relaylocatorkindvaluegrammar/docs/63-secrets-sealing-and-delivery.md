# Secrets sealing and delivery (design)

DeriveBSD must avoid “secrets in images” and also avoid giving the control plane universal plaintext access.

## Goals
- secrets are not part of store identity
- secrets injection is explicit and policy-governed
- support offline provisioning
- support “sealed secrets” where hosts can only decrypt what they should

## v1 baseline (practical)
- secrets are delivered out-of-band to a host-local secrets service
- `derive-vmmd` requests secrets by *reference* at launch time
- secrets are delivered into guests via the injection channel (docs/28 + docs/36)

### Identity-gated secrets (optional lane)

For larger deployments, prefer **secretless** patterns:
- workloads obtain a short-lived identity (SVID-style)
- brokers grant narrowly-scoped operations/tokens based on that identity

This keeps static credentials out of images and makes secret access auditable and policy-bound.

See: `docs/181-workload-identity-and-secretless-deploys.md`.

### At-rest protection (optional)
- if policy requires, store secret-bearing datasets as ZFS-encrypted roots and record key-use evidence (see `docs/146-zfs-native-encryption-for-generations.md`)

## Sealed secrets (optional, future-ready)
Support encryption envelopes:
- recipient = host identity key (or TPM-backed key)
- policy decides which hosts can decrypt which secret refs
- rotation is a policy event (re-encrypt envelopes)

## Audit requirements
- never log secret values
- log secret *references* and policy decisions with correlation ids

See RFC-0039.
Last updated: 2026-02-24
