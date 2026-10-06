# Repo signing UX lessons (pkg-style ergonomics)

DeriveBSD should have strong signing/provenance **without** a painful operational UX.

FreeBSD pkg repository tooling provides useful ergonomics to learn from:
- explicit signature modes
- simple client-side repo configuration
- fingerprint-based trust bootstrap

## DeriveBSD direction

- keep trust policy as data (`spec/trust.policy.schema.json`)
- allow “signature modes” to be expressed as policy:
  - what must be signed
  - what attestations must exist
  - expiry / rollback protections for channel metadata

## Non-goals (v1)

- copying pkg’s formats wholesale

See RFC-0078.
Last updated: 2026-02-23
