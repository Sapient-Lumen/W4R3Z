# Sigsum as a lightweight transparency lane (optional)

Transparency logs are useful when you want more than “the bytes are signed”:
you want **detection** of targeted / unexpected signing events.

Sigstore/Rekor is one popular option, but DeriveBSD should also consider **Sigsum** as a
*minimalistic* alternative: it focuses on **public logging of signed checksums** so that
any signature a client accepts can be monitored for misuse.

References:
- Sigsum overview: https://www.sigsum.org/
- Sigsum design notes (inclusion proofs, witnesses): https://git.sigsum.org/sigsum/tree/doc/design.md

## What Sigsum buys us

- **Key-usage transparency**: “this key signed this digest at this time” becomes publicly observable.
- **Detection of targeted signing attacks**: if an attacker can sign malicious artifacts for *one* target,
  transparency still exposes the signing event to monitors.
- **Smaller moving parts** than many “general transparency” stacks: log, witnesses, monitors.

This is *not* prevention. A client may still accept a malicious but signed artifact.
The point is to make such events **discoverable** and attributable.

## Mapping to DeriveBSD’s model

DeriveBSD already requires:
- digest verification
- signatures (trust-policy selected keys)
- provenance attestations

Sigsum adds an optional evidence object:

`transparency.sigsum.v1`:
- `artifact_digest` (the thing being accepted)
- `signature_digest` (or the signer key id + sig)
- `log_id`
- `inclusion_proof`
- `tree_head` (+ witness signatures)

Policy can require this evidence for promotion/consumption.

### Where it plugs in

- **Cache publish**: when publishing an artifact, the publisher logs the signed checksum and
  stores the inclusion proof alongside the artifact metadata.
- **Client verify**: `derive verify` checks that the accepted signature is accompanied by a valid
  inclusion proof up to a sufficiently witnessed tree head.
- **Monitoring**: independent monitors watch logs for key usage and alert on policy violations.

## Design constraints (to keep it sane)

- **Optional + policy-gated**: never force a single transparency mechanism.
- **Offline-verifiable bundles**: store proof material as content-addressed blobs so `derive verify`
  does not need network.
- **Separation of concerns**: transparency evidence is *additional* to signatures/attestations,
  not a replacement.

See RFC-0088.

For split-view defenses and witnessed checkpoints, see: `docs/187-witnessed-transparency-checkpoints.md`.


Last updated: 2026-02-23
