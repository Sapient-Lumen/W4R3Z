# RFC-0046: Attestation payload formats (DSSE + in-toto)

- Status: draft
- Created: 2026-02-23

## Summary
Standardize DeriveBSD attestation objects as DSSE envelopes containing in-toto statements and SLSA-style predicates.

## Goals
- consistent signing/verifying pipeline
- compatible with optional sigstore bundles and transparency logs
- stable JSON schemas for LLM tooling

## References
- in-toto attestation envelope spec
- sigstore bundle format
- SLSA attestation model
