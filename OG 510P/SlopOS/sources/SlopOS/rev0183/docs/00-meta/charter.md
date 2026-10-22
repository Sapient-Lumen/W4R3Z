# Charter (canonical north star)

**Mission (canonical):** We are constructing a long-lived, evidence-tracked research archive to design—and then mechanically justify—a from-scratch Rust microkernel/micro-hypervisor whose claimed security/correctness properties (capability-mediated authority, isolation, well-formed state evolution, boot/provenance integrity, bounded `unsafe` obligations, and eventually selected info-flow/concurrency guarantees) are stated as explicit invariants over a rigorously defined abstract machine and refined through layered specifications into an implementable artifact with seL4-class assurance under explicit hardware/supply-chain assumptions (with hypervisor-first treated as a primary candidate), by continuously converting hypotheses into proofs/ADRs via prototypes, model checks, and machine-checked verification artifacts.

**Behaviors (canonical):**
constrain-claims, formalize-invariants, minimize-TCB, hypervisor-evaluate, spec-first, proof-driven, prototype-to-evidence,
model-check-fast, mechanize-refinement, isolate-unsafe, document-assumptions, harden-supplychain, reproduce-builds,
log-decisions, scope-sidechannels, stage-concurrency, pressure-test-abusecases, trace-evidence, promote-RFC→ADR, iterate-forever.

## Archive size discipline (non-negotiable)
- Prefer **pointers** (REF/EVID IDs) over pasted text or large artifacts.
- For heavyweight evidence (proofs, corpora, traces), prefer **CH-AREF** content-addressed references over embedding artifacts (D-AREF).
- One canonical source per concept: use registries + deprecations to prevent drift.
- Every “new thing” must justify itself as either (a) a decision surface, (b) an invariant/claim, or (c) evidence.
