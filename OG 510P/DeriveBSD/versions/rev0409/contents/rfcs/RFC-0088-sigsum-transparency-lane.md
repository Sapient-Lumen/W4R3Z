# RFC-0088: Sigsum transparency lane (optional)

Status: Draft

## Summary

Add an optional, lightweight transparency lane using **Sigsum**.

The goal is key-usage transparency for signatures that clients accept:
if a signing key is misused to produce a targeted malicious artifact, the signing event can be
detected by monitors.

References:
- Sigsum overview: https://www.sigsum.org/
- Sigsum design notes: https://git.sigsum.org/sigsum/tree/doc/design.md

## Goals

- Allow policy to require transparency for certain channels/fleets.
- Keep verification **offline-capable** by storing inclusion proofs as blobs.
- Avoid coupling DeriveBSD to any single transparency implementation.

## Non-goals

- Preventing signing attacks (transparency primarily enables detection).
- Replacing digest/signature/attestation verification.

## Design sketch

- New evidence object: `transparency.sigsum.v1`
  - binds `artifact_digest` to inclusion proof and witnessed tree head
- Publishing role submits signed checksums to a Sigsum log and stores returned proof material.
- Verification role checks:
  - signature validity (existing trust-policy)
  - proof validity up to a trusted witness quorum

See: `docs/131-sigsum-lightweight-transparency.md`.
