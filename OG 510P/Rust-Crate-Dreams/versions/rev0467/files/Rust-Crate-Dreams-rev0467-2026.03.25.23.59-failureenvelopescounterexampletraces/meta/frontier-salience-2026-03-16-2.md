# Frontier salience scan — 2026-03-16 (build-dir + debug-support refresh)

This pass again avoided adding another top-level proposal.
The better move was to strengthen two already-strong workflow crates with fresh 2026 signals and more concrete scenario packs:

- **P-0489 Cargo Build-Dir Consumer Transition Kit**
- **P-0486 Debuggability Support Contract Kit**

## Main judgment

The Rust ecosystem still looks likelier to benefit from **coordination artifacts above real substrate** than from another clever leaf library.
But this pass shifts more weight toward crates that help maintainers survive **tooling-layout churn** and **support-posture ambiguity** with honest review bundles.

Three current signals especially matter:

1. the 2025 State of Rust survey still says **resource usage** remains a major pain and that the debugging story remains a meaningful productivity limiter,
2. Cargo's March 2026 **Build Dir Layout v2** call for testing explicitly says many projects still rely on unspecified internal details and asks maintainers to rehearse real tests and release processes under the new layout,
3. the 2026 debugging survey says a strong debugging story must cover multiple debuggers across OSes, visualizers, async debugging, and expression evaluation.

Together, those signals make **migration receipts** and **support contracts** look more urgent than one more narrowly scoped implementation crate.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0489 Cargo Build-Dir Consumer Transition Kit**
3. **P-0486 Debuggability Support Contract Kit**
4. **P-0242 Reproducible Build Evidence Kit**
5. **P-0256 Evidence Bundle Core Kit**
6. **P-0485 Verification Campaign Workbench Kit**
7. **P-0264 Rust Conformance Harness Toolkit**
8. **P-0458 Async Dyn Transition Kit**
9. **P-0465 BorrowSanitizer Workflow & Evidence Kit**
10. **P-0200 WebAuthn & Passkeys Interop + Device Lab Kit**
11. **P-0503 Assurance Case Workbench Kit**
12. **P-0076 Local-first Sync Kit**

## Why P-0489 rose now

The March 2026 Cargo post no longer leaves the downstream problem abstract.
It names concrete failure modes like:

- inferring a `[[bin]]` path from a `[[test]]` path,
- build scripts or helpers recovering target-dir from `OUT_DIR` or executable paths,
- and brittle user-requested artifact lookup.

That means a crate which inventories those consumers, classifies their lane, and emits a conservative adapter plan is no longer speculative.
It is a direct answer to a live ecosystem migration problem.

## Why P-0486 rose now

Debugging support still hurts, but Rust now has enough substrate that the missing value is less “invent a debugger” and more “tell me what this build honestly supports.”

The 2026 debugging survey frames success as cross-debugger, cross-OS, visualizer-aware, async-capable support.
At the same time, Cargo is making artifact-location assumptions more visible by separating target-dir and build-dir more explicitly.

That makes a receiver-facing **support-posture + symbol-layout + drift** bundle unusually attractive: maintainers need to know not just where artifacts landed, but whether the symbol state and visualizer state needed for real support are still there.

## Working rule for the next few passes

Prefer upgrades that add:

- scenario packs tied to named upstream failure modes,
- lane-boundary notes,
- conservative adapter vocabularies,
- and sharper distinctions between location, support, and evidence.

The archive already has enough proposals that **specificity and handoff quality** are often worth more than proposal count.

## Sources

- 2025 State of Rust survey: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Build Dir Layout v2 call for testing: https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Rust debugging survey 2026: https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- Cargo build cache docs: https://doc.rust-lang.org/cargo/reference/build-cache.html
