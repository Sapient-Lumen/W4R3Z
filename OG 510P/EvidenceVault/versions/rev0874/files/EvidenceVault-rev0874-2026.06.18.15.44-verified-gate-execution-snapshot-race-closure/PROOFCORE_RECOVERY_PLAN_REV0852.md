
# Proofcore recovery plan — rev0852

This plan is the immediate correction after learning that EvidenceVault began as a SNARKs-adjacent proof exploration.

## New mission sentence

EvidenceVault should become a **proof-carrying research vault**: a datacube where every important claim can be traced to evidence, public inputs, commitments, verifier code or explicit non-machine-checkable status, provenance, and rights posture.

## Phase 0 — do not overclaim

The current overlay exposes the proof lineage through indexes and ledgers, not through runnable proof payloads. Do not claim a SNARK, zero-knowledge property, verifier result, or mathematical correctness from this overlay alone.

## Phase 1 — recover the proof map

Build a canonical-path-to-role table with at least these roles:

- `paper_or_render`
- `source`
- `schema`
- `abi_ir_or_protocol_ir`
- `public_input_or_commitment`
- `witness_or_witness_policy`
- `verifier_code`
- `accept_fixture`
- `reject_fixture`
- `attestation_or_receipt`
- `governance_or_rights`
- `unknown`

Start with `zkrtp`, `streamfold`, `sources/ocf_llm/tools/verifiers/`, and `schemas/*proof*` / `schemas/*circuit*` / `schemas/*commitment*`.

## Phase 2 — define one minimal proofcore lane

The first lane should answer one narrow question:

```text
Claim: <one exact statement>
Public inputs: <hash roots / commitments / statement bytes>
Witness: <private, unavailable, synthetic, or none>
Verifier: <command and code identity>
Expected accept: <fixture path and output>
Expected reject: <negative fixture path and output>
Rights status: <component/license decision>
```

Only after this exists should the project generalize to a wider framework.

## Phase 3 — decide the word "SNARK"

Use `SNARK` only when the recovered artifact really binds to a succinct non-interactive argument system. Use `proof-carrying receipt`, `certificate`, `attestation`, or `verifiable claim` for the broader machinery when zero-knowledge or succinctness is not actually established.

## Phase 4 — stop conditions for cloudtainer work

Do more infrastructure hardening only when it protects one of these invariants:

- proofcore artifact identity cannot be spoofed;
- verifier inputs cannot be swapped;
- rights gates cannot be bypassed;
- provenance/signature boundaries cannot be confused;
- repeated scans can be avoided with a content-addressed cache.

Otherwise, the next unit of work should recover proofcore content, not add another wrapper.

## Phase 5 — publication boundary

Publication remains blocked until owner/upstream rights decisions are resolved. Once rights are resolved, regenerate RIGHTS, SPDX, RO-Crate, proofcore manifests, and publication queue decisions from one source of truth.
