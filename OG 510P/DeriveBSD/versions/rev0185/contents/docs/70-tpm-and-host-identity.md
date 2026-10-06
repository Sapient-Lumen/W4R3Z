# TPM / measured boot (optional): host identity + sealed secrets

DeriveBSD’s baseline security model does **not** require a TPM, but TPM support can unlock:
- **sealed secrets** (host can decrypt only when in an expected boot state)
- **strong host identity** for “which host ran which artifact”
- **measured boot** attestations for high-assurance zones

## FreeBSD reality signals

- FreeBSD provides `tpm2-tools` in ports (TPM2 CLI tooling).
- There is ongoing FreeBSD work/discussion around TPM2 integration in the EFI bootloader to retrieve a GELI passphrase (`tpm2_passphrase`) (not a guarantee, but a signal the space is active).

References are in `docs/32-curated-references.md`.

## DeriveBSD design (policy-gated)

### Host identity key (optional)
- A host may have a `host_identity_pubkey` registered in trust policy.
- Policy may require certain channels/targets to run only on hosts with registered identities.

### Sealed secret envelopes (optional)
- A secret envelope is encrypted to a host recipient key (TPM-backed where available).
- Policy decides:
  - which hosts can decrypt
  - whether the boot measurement state must match (future tier)

### Evidence and audit
When TPM features are enabled, DeriveBSD logs:
- host identity key id
- whether a sealed secret was used (reference only, never plaintext)
- any attestation bundle digests (see docs/71)

## Non-goals (v1)
- mandatory TPM presence
- full remote attestation pipeline
- measured boot enforcement before we have stable FreeBSD primitives and tooling

Last updated: 2026-02-24
