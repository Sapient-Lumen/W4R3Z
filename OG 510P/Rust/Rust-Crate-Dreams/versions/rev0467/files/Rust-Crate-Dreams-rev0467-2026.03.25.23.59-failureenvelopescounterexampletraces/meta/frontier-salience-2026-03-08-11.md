# Frontier salience scan — 2026-03-08 (eleventh pass)

## Main judgment

This pass again did **not** add another top-level proposal.

Instead, it made **P-0490 Cargo Lock Contention Witness Kit** more implementation-ready.
The upstream Rust/Cargo story is now explicit enough that the archive should stop treating live blocking as a vague performance complaint.
The missing layer is a **portable witness bundle** above Cargo/rust-analyzer locking substrate.

## Ranked frontier after this pass

1. **P-0469 Cargo Rebuild Explanation Kit**
   - Still the strongest immediate incubation target because the per-run support story is universal and the bundle is easy to justify.
2. **P-0468 Cargo Resolver Explanation Kit**
   - Now clearly differentiated from raw graph tooling and increasingly close to a buildable first artifact family.
3. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
   - Still the sharpest tool-workflow parity layer.
4. **P-0490 Cargo Lock Contention Witness Kit**
   - Rose because the official substrate is now explicit enough that the first artifact contract can be very small and very honest.
5. **P-0046 buildscript-ux-kit**
6. **P-0486 Debuggability Support Contract Kit**
7. **P-0035 cargo-build-insights**
8. **P-0059 buildscript-testkit**
9. **P-0058 native-deps-kit**
10. **P-0489 Cargo Build-Dir Consumer Transition Kit**

## Why P-0490 improved

Five current facts matter here:

- rust-analyzer’s FAQ now states directly that rust-analyzer and manual Cargo commands can block one another,
- rust-analyzer configuration now documents `cargo.targetDir` precisely as a way to avoid that blocking at the cost of duplicated artifacts,
- Cargo’s build-dir-layout goal now frames finer-grained locking and reduced tool contention as explicit upstream motivation,
- Cargo’s unstable `build-dir-new-layout` docs repeat that locking/caching motivation,
- and Cargo’s cache-lock internals make package/index cache coordination a real substrate rather than a rumor.

That means **P-0490** does not need to invent a profiler or a new scheduler.
It can be precise about its 0.1 contract:

- one cache-root manifest,
- one lock-wait receipt,
- one conservative collision diagnosis,
- one mitigation plan,
- optionally one process-role snapshot,
- and one diff for comparing old/new witness bundles.

## What should happen next

The best next passes on this frontier should prefer:

1. scenario bundles for shared-target-dir conflicts, package-cache waits, and mitigated separate-target-dir setups,
2. vocabulary alignment across **P-0494 / P-0490 / P-0489**,
3. conservative provenance/confidence fields,
4. and explicit path/process redaction rules.

They should **not** add another generic “Cargo IDE friction” idea unless it is clearly distinct from:

- parity / fallback artifacts,
- live blocking witnesses,
- build-dir consumer migration,
- or rebuild explanation.

## Sources

- rust-analyzer FAQ: https://rust-analyzer.github.io/book/faq.html
- rust-analyzer configuration: https://rust-analyzer.github.io/book/configuration
- Cargo build-cache docs: https://doc.rust-lang.org/cargo/reference/build-cache.html
- Cargo cache-lock internals: https://doc.rust-lang.org/beta/nightly-rustc/cargo/util/cache_lock/index.html
- Cargo unstable features (`build-dir-new-layout`): https://doc.rust-lang.org/cargo/reference/unstable.html#build-dir-new-layout
- Cargo build-dir layout goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- 2025 State of Rust survey results: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
