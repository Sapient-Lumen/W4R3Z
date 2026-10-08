# Documentation-example frontier — 2026-03-22

The archive now has enough documentation-oriented proposals that future passes should stop treating them as one blurry “docs quality” bucket.

## Current stack

1. **P-0455 Doctest Extraction & Support Contract Kit**
   - Owns the shared contract layer for:
     - extracted doctest manifests
     - rewrite lineage
     - execution mode
     - example support class
     - docs-example drift
2. **P-0481 Doctest Runtool Profile Kit**
   - Owns target-aware runner profiles, emulator/VM receipts, and ignore-target matrices.
   - Use this when the hard problem is the runtime wrapper or target execution environment.
3. **P-0472 Docs.rs Build Parity & Evidence Kit**
   - Owns local-vs-hosted docs.rs fidelity, metadata interpretation, sandbox-limit reports, and hosted-build imports.
   - Use this when the hard problem is docs.rs as a hosted service, not example semantics.
4. **P-0476 Rustdoc Coverage Review Bundle Kit**
   - Owns docs debt, API-surface coverage, example-coverage trends, and release-review planning.
   - Use this when the hard problem is missing docs, not example execution truth.
5. **P-0451 Cfg Availability Ledger Kit**
   - Owns visibility / availability truth for `cfg`-sensitive public APIs.
   - Use this when the hard problem is “item appears in docs but is not actually available,” not doctest extraction or execution.

## Shared judgment after this pass

The strongest missing documentation crate is not another docs site and not another quality score.
It is a **contract layer** that lets downstream users, reviewers, and maintainers inspect what documentation examples mean in practice.

## Design guardrails

When working in this frontier, keep these truths separate:

1. **manifest truth** — what rustdoc extracted
2. **rewrite truth** — what was injected or adapted after extraction
3. **execution truth** — how the example was compiled or run
4. **hosted-build truth** — what docs.rs rendered or failed to render
5. **coverage truth** — what public API still lacks good docs or examples

Do not let any of the following stand in for an honest documentation-support answer:

- “docs.rs is green”
- “`cargo test --doc` passed”
- “the crate uses `#[cfg(doc)]`”
- “the example is in the docs”
- “coverage went up”

Those are useful signals, not a full support contract.
