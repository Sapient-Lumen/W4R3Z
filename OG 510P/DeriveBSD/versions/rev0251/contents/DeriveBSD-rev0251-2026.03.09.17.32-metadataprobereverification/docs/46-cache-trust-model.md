# Cache trust model (signed artifacts, untrusted mirrors)

DeriveBSD assumes mirrors/caches can be malicious.
Trust comes from cryptographic verification and policy.

## Principles
- Mirrors are untrusted blob stores.
- Clients verify digests + signatures + required attestations (`adrs/ADR-0009-artifact-verification.md`).
- Trust policy selects trusted keys per namespace/target kind.

## Remote caches (extra threat surface)

Remote caching can introduce **action-cache poisoning** risks if a client accepts “this output is correct” claims without verifying the bytes.
DeriveBSD treats remote caches as *untrusted*, and only accepts outputs when they verify against:

- digest-addressed blobs/trees (CAS)
- required signatures and attestations
- policy decision records bound into the Plan digest

See: `docs/170-remote-cache-threat-model.md`.

Trust policy is data (schema + example):
- `spec/trust.policy.schema.json`
- `spec/examples/trust.policy.json`

## Optional add-ons
- transparency logs for public audit (see `docs/59-transparency-log-rekor.md`)
- channel metadata anti-freeze/rollback protections (`docs/61-channel-metadata-tuf-inspired.md`)
- cache witness quorums (Trustix-style reproducibility corroboration): `docs/190-cache-witness-quorums-trustix.md`

Last updated: 2026-02-24
