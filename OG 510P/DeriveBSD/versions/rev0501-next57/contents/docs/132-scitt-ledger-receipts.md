# SCITT ledger receipts (optional)

DeriveBSD’s trust model already treats provenance/attestations as first-class objects.
The next step (optional) is **third-party, append-only publication** of those statements,
so that retroactive tampering and targeted distribution are harder to hide.

The IETF **SCITT** effort (“Supply Chain Integrity, Transparency, and Trust”) defines an
architecture and interoperable building blocks for this kind of supply-chain transparency.

References:
- SCITT WG charter/about (IETF Datatracker): https://datatracker.ietf.org/group/scitt/about/
- SCITT architecture draft (current draft on Datatracker): https://datatracker.ietf.org/doc/draft-ietf-scitt-architecture/

## What SCITT buys us

- A standardized way to publish signed supply-chain statements into a **transparent registry**
  and obtain **receipts** proving inclusion.
- A path to multi-vendor interoperability (different registries, shared verification semantics).

This is similar in spirit to transparency logs, but scoped to supply-chain statements and
deployment ecosystems.

## Mapping to DeriveBSD’s evidence objects

DeriveBSD typically emits a DSSE envelope containing an in-toto Statement (e.g. SLSA provenance).

SCITT can be treated as an *optional publication and receipt lane*:

`transparency.scitt.receipt.v1`:
- `statement_digest` (DSSE envelope digest)
- `registry_id`
- `receipt` (proof material returned by registry)
- `timestamp` (as asserted by the registry)

Policy can require SCITT receipts for:
- promotion into certain channels
- consumption on sensitive fleets

## How to keep this from bloating the system

- Treat receipts as small, content-addressed blobs.
- Allow multiple registries but keep the verification surface minimal:
  “does this receipt bind to this statement digest and registry identity?”
- Make publication asynchronous from builds: builders remain hostile; publication can happen
  from a separate, least-authority publisher role.

See RFC-0089.

Last updated: 2026-02-23
