# MC/DC coverage frontier — 2026-03-22

## Main judgment

The worthy crate in this lane is not a new percentage reporter.
It is a crate that helps other people review **what decision inventory was in scope, what constructs the current toolchain can actually support, whether independence pairs were demonstrated, and what run lineage backs that claim**.

## Why now

Current upstream signals line up unusually well:

- Rust 2026 lists **implement MC/DC coverage support** as a safety-critical milestone;
- rustc’s source-based coverage workflow is already real and documented;
- branch / MC/DC modes still carry unstable or caveat-heavy edges;
- and the official branch-coverage limitations issue now gives a concrete construct taxonomy the archive can model.

## The support-contract split this lane needs

A serious crate here should keep these truths separate:

1. **decision authority** — what decision inventory was authoritative;
2. **construct support** — what branching forms were supported, unsupported, or excluded;
3. **independence evidence** — whether each condition has a witnessed independence pair;
4. **caveat basis** — which unstable flags, toolchain limitations, or known issues still constrain trust;
5. **evidence lineage** — which runs and merged profiles actually back the verdict.

## Why this is better than another dashboard

A dashboard can summarize results.
It cannot by itself tell a reviewer whether `match` arms were out of scope, whether MC/DC was preview-only, whether doctests were omitted, or whether a partial result still requires manual review.

## Practical lane boundary

- raw coverage instrumentation and profile emission belong to rustc/LLVM;
- workflow wrapping belongs to tools like `cargo-llvm-cov`;
- **support-contract truth** belongs here.
