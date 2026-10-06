# RFC-0060: Closure proofs

Status: draft

## Problem

DeriveBSD wants **prove closure** as a first-class property:
- no undeclared runtime dependencies
- no “surprise bytes” at activation/launch time
- explainable dependency sets for audit and incident response

Today we can compute closures, but we need a stable, verifiable *artifact* that:
- commits to the exact closure set
- is policy-verifiable (keys/expiry/namespace)
- composes with channel metadata (anti-freeze/rollback)

## Proposal

Define two objects:

1) **Closure manifest** (hashable JSON)
- roots (host generation or microVM bundle digests)
- list of store objects (path + digest)
- referenced runtime manifest digest (microVM)
- policy context digest(s)
- required attestation types (by digest / identifier)

2) **Closure proof** (signature)
- signs `closure_manifest_digest`
- includes: target kind, namespace/channel, expiry/epoch window
- verification uses policy-selected keys

## Why separate manifest and proof?

- the manifest is stable and can be embedded/cached
- the proof can rotate independently (key rollover, expiry)

## Non-goals (v1)

- proving *semantic equivalence* of two different closures
- complex witness graphs or ZK proofs
- solving reproducible builds; we only provide hooks

## Open questions

- do we require closure proofs for local-only workflows by default?
- should the closure manifest include a Merkle tree for large closures?

Pointers:
- `docs/90-closure-proof.md`
- `docs/61-channel-metadata-tuf-inspired.md`, `docs/62-replay-rollback-freeze.md`
- `adrs/ADR-0009-artifact-verification.md`
