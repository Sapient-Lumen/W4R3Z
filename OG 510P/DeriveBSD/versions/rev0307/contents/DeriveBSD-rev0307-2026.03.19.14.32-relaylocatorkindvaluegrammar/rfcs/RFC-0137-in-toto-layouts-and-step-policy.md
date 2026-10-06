# RFC-0137: Supply chain step policies with in-toto layouts

Status: **Draft**  
Last updated: 2026-02-24

## Problem

DeriveBSD can already emit attestations (provenance, SBOMs, tests) as DSSE-wrapped in-toto statements.

However, per-artifact attestations do not specify:
- which steps *must* exist across a workflow
- who is authorized to perform each step
- how step inputs/outputs must chain

Without a workflow policy, teams end up re-encoding this in bespoke CI glue.

## Proposal

Add an optional lane based on in-toto’s **layout** concept:

- `supplychain-layout-policy` object binds a specific layout digest and its trust roots
- `supplychain-verify-receipt` evidence object records verification results for a given artifact

Promotion/publishing policies may require `supplychain-verify-receipt == pass`.

## Data model

See:
- `spec/supplychain.layout.policy.schema.json`
- `spec/supplychain.verify.receipt.schema.json`

## Integration points

- Channel publishing: high-assurance channels may require a verified receipt for every artifact target.
- CI builders: emit receipts as part of `derive build` / `derive attest`.
- Explainability: `derive explain` can show which step failed (missing attestation, wrong signer, mismatched materials/products).

## Threat model highlights

- compromised CI step produces artifacts without required tests
- “shadow release” performed by an unauthorized functionary
- substitution attacks where intermediate outputs are swapped

## Rollout plan

1) Start as a “warn-only” lane (receipt emitted but not required).
2) Allow namespaces/channels to require receipts for selected targets.
3) Add default layout templates for common pipelines (source → build → test → sign → publish).

## Open questions

- do we standardize a DeriveBSD mapping from Plan steps to layout step names?
- should we additionally emit a summary attestation (verification summary) as a DSSE in-toto statement for portability?
