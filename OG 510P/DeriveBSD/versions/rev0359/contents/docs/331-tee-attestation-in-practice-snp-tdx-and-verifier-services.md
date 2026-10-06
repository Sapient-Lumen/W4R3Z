# TEE attestation in practice (SEV-SNP / TDX) + verifier services

This doc is intentionally practical: it points at real ecosystem shapes and highlights where DeriveBSD should *adapt* rather than invent.

It complements `docs/330-confidential-microvms-and-tee-attestation-as-evidence.md`.

## AMD SEV-SNP (high-level shape)

Typical flow:
- guest constructs a report request (includes nonce/reportdata)
- request is conveyed through the hypervisor to the firmware
- firmware returns an attestation report
- verifier validates signature chain and evaluates fields against policy/reference

Key operational details:
- evidence retrieval is usually exposed via a guest device and ioctl interface on Linux; FreeBSD adapters may differ
- verifiers often need access to AMD certificate distribution services or cached chains

## Intel TDX (high-level shape)

Typical shape:
- guest asks the TDX module for a TDREPORT (includes REPORTDATA)
- a quote is generated for remote verification
- verifier checks the quote against DCAP collateral (PCK cert chain, TCB info, QE identity)

Operational implications:
- a “quote verification service” pattern is common so fleets can centralize collateral fetching and caching

## Verifier services as part of the evidence spine

DeriveBSD should treat vendor verifiers as:
- adapter libraries
- or external services

Either way, the stable output is:
- a `tee.attestation.receipt` bound to a `tee.attestation.reference` and `tee.attestation.evidence` digest

## Interaction with secret release (KBS-shaped)

Many confidential-computing stacks use a key-broker service (KBS) that releases secrets only when evidence verifies.
DeriveBSD can reuse the shape, but bind decisions to:
- derived plan digests (closure + runtime manifest)
- Derive policy decisions + receipts

## References

See `docs/32-curated-references.md` (Confidential computing / TEEs).

Last updated: 2026-02-26r90
