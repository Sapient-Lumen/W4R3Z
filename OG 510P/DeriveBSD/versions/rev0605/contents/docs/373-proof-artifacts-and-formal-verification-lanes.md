# Proof artifacts and formal verification lanes (treat proofs like supply-chain evidence)

Formal verification is not a default requirement for DeriveBSD.
But a greenfield system can still steal the most important operational lesson from verified systems:

> **When proofs exist, treat them as first-class artifacts**: digestable, reproducible, reviewable, and tied to the exact source + toolchain.

seL4 is the canonical prior art: a microkernel with machine-checked proofs covering functional correctness and (in parts of the story) refinement down toward the implementation. References:
- seL4 overview: https://sel4.systems/
- seL4 whitepaper (proof overview): https://sel4.systems/About/seL4-whitepaper.pdf
- “Comprehensive formal verification of an OS microkernel” (Klein et al., 2014): https://sel4.systems/Research/pdfs/comprehensive-formal-verification-os-microkernel.pdf
- seL4 verification project background: https://trustworthy.systems/projects/OLD/seL4-verification/


Other under-copied prior art: **formally proven message parsers** (EverParse). This is a great fit for a greenfield system because protocol and file-format parsers are frequent bug sources.
- EverParse overview: https://www.microsoft.com/en-us/research/blog/everparse-hardening-critical-attack-surfaces-with-formally-proven-message-parsers/

## DeriveBSD direction

Add an **optional lane** where “verification results” are handled like other evidence:

- Proofs are *versioned artifacts* with stable digests.
- Proof inputs are explicit:
  - source tree digest(s)
  - spec/model digest(s)
  - theorem prover/compiler versions
  - build flags and proof scripts
- Proof outputs produce receipts (success/failure) and can be independently replayed.

This is the same engineering stance as reproducible builds and witnessed rebuilders:

See:
- reproducible generations: `docs/367-reproducible-generations-and-determinism-checks.md`
- witness rebuilders: `docs/116-witness-rebuilders-diffoscope.md`

## What we standardize (minimal)

### 1) A “proof bundle” object
A proof bundle is a content-addressed directory/closure containing:
- proof scripts
- models/specs used
- toolchain pinset
- replay instructions

Treat it like any other artifact closure.

### 2) A “proof receipt”
Receipts should record:
- proof bundle digest
- verifier identity (CI runner, witness, or external auditor)
- replay environment digest (toolchain closure)
- timestamp and policy context

### 3) Policy hooks
Make it possible (not mandatory) to say:
- “this channel requires proof receipts for kernel/UAPI changes”
- “this component’s contract must have a proof receipt before it can be promoted”

This fits naturally into:
- contract diff gates: `docs/370-contract-registries-and-api-diff-gates.md`
- kernel UAPI diff gates: `docs/362-uapi-surface-registry-and-compat-gates.md`
- promotion gates: `docs/166-test-receipts-and-promotion-gates.md`

## The real win: shrinking the trust gap

Even when we are *not* proving things, adopting “proofs are artifacts” gives useful structure:
- model-checking outputs are artifacts (`spec/modelcheck.receipt.schema.json` exists for this style)
- fuzzing coverage, crash triage, and minimization artifacts can be treated the same way

It pushes DeriveBSD toward:
- explicit assumptions
- replayable evidence
- fewer “hand-wavy security claims”

## Non-goals

- We are not promising a verified kernel.
- We are not choosing Isabelle/Coq/Lean/etc.

The goal is simply: **if verification exists, it is operationally usable and reviewable**.
