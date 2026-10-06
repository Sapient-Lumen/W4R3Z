# Transparency logs (optional): Rekor as an audit amplifier

DeriveBSD supports signatures and attestations.
A transparency log can add append-only evidence of “this digest was signed”.

References:
- Sigstore docs: Rekor overview: https://docs.sigstore.dev/logging/overview/
- Rekor repository: https://github.com/sigstore/rekor
- Rekor v2 GA note (dsse + hashedrekord focus): https://blog.sigstore.dev/rekor-v2-ga/

## v1 stance
Optional, policy-gated:
- publish signatures/attestations
- verify inclusion proof before deploy (high-assurance channels)

## What Rekor buys us (and what it does not)

Buys:
- **public append-only evidence** that a given digest + identity + signature/attestation existed at a time
- easier third-party auditing (monitors can watch for unexpected signers)

Does not buy:
- correctness of the build itself (that’s what provenance + witness rebuilders are for)
- immunity to key compromise (it makes compromise *visible*, not impossible)

## DeriveBSD fit

If enabled by policy, DeriveBSD can log:
- artifact signatures
- DSSE in-toto attestations

and require inclusion evidence for deploys in high-assurance channels.

See RFC-0036 and ADR-0014.

Split-view defenses (witness cosigning / gossip): `docs/187-witnessed-transparency-checkpoints.md`.

Last updated: 2026-02-23
