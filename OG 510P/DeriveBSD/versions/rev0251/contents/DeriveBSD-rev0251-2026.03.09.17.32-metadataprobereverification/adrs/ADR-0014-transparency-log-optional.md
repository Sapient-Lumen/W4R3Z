# ADR-0014: Transparency log is optional; policy-gated (proposed)

- Status: proposed
- Date: 2026-02-23

## Context

Transparency logs (CT-shaped append-only logs, witness cosigning, SCITT-style ledgers) are a powerful way to make
mis-issuance and equivocation *detectable*.

However, making a transparency log a **baseline dependency** creates operational risk:
- verification becomes dependent on log availability
- “public internet assumptions” leak into private fleets
- offline/airgapped environments become second-class

DeriveBSD wants the benefits **without** turning transparency into a global SPOF.

## Decision

Transparency log integration is **optional** and **policy-gated**.

1) **No unconditional online dependency**
- A DeriveBSD system must be able to verify the artifacts required to boot and run from locally available material.
- If a policy requires transparency, the required verification material must be mirrorable (e.g., checkpoints, proofs, or
  bundle-like receipts).

2) **Transparency is an evidence lane, not the authority model**
- Release authority remains channel metadata and publish receipts (threshold keys, policy-defined roles).
- Transparency proofs/receipts are *additional evidence* that policy may require.

3) **Support multiple log shapes**
- CT-style Merkle logs (inclusion proofs + checkpoints)
- witness-cosigned checkpoints
- SCITT-style receipts/ledgers

DeriveBSD represents this as typed objects and receipts (`spec/transparency.proof.schema.json`,
`spec/log.checkpoint.receipt.schema.json`, `spec/export.transparency.entry.schema.json`, `spec/release.transparency.entry.schema.json`).

## Consequences

- Systems can choose: no transparency, internal transparency, public transparency, or hybrids.
- Fleet policy can require transparency for specific classes:
  - releases
  - key directories (authority policies, trust bundles)
  - publisher identity bindings
- Offline fleets can satisfy transparency requirements by mirroring checkpoints/proofs and pinning trust roots.

## Notes / references

- Sigstore’s Rekor is an existence proof of “signature transparency as a service”, but DeriveBSD does not depend on it.
  See: https://docs.sigstore.dev/logging/overview/
- TUF remains the baseline anti-rollback / metadata security model; transparency is complementary.
  See: https://theupdateframework.github.io/specification/latest/

