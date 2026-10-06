# RFC-0045: Optional TPM host identity + sealed secrets

- Status: draft
- Created: 2026-02-23

## Summary
Define how DeriveBSD can optionally use TPM-backed keys for host identity and sealed secret envelopes.

## Goals
- policy-gated optional feature
- offline verifiability
- never log secrets
- future tier: measured boot attestations

## References
- tpm2-tools on FreeBSD
- FreeBSD EFI bootloader TPM2 discussion/bug for GELI passphrase retrieval (signal)
