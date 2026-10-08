# Frontier salience scan — 2026-03-08 (twenty-fifth pass)

## Main judgment

This pass again did **not** add a new top-level proposal.

Instead, it upgraded **P-0490 Cargo Lock Contention Witness Kit** into a more implementation-shaped crate plan by freezing the boundary the archive still needed most in that frontier: **root-sharing topology and wrapper/cache-mode context** above live lock waits.

## Ranked frontier after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0469 Cargo Rebuild Explanation Kit**
3. **P-0490 Cargo Lock Contention Witness Kit**
4. **P-0496 Cargo Vendor & Source Parity Kit**
5. **P-0505 Cargo Host/Target Scope Contract Kit**
6. **P-0058 native-deps-kit**
7. **P-0503 Assurance Case Workbench Kit**
8. **P-0504 Linker Lane Contract & Diagnosis Kit**
9. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
10. **P-0486 Debuggability Support Contract Kit**

## Why P-0490 moved up

Seven current facts make it more concrete than before:

- the 2025 compiler performance survey says more than 35% of respondents considered IDE and Cargo blocking one another a big problem,
- rust-analyzer’s FAQ now explicitly documents that rust-analyzer and manual Cargo commands can block one another and recommends a separate target directory as the mitigation,
- rust-analyzer’s configuration docs expose `cargo.targetDir` and wrapper/override-command knobs that materially change contention topology,
- Cargo’s build-cache docs now explicitly separate **target-dir** from **build-dir**,
- Cargo’s environment/config docs say `RUSTC_WORKSPACE_WRAPPER` affects the filename hash so artifacts are cached separately,
- Cargo’s cache-lock internals still show package/index caches are coordinated with real locking rules,
- and the build-dir-layout goal plus unstable docs still frame the new layout as groundwork for finer-grained locking.

That means **P-0490** no longer needs to act like a single wait receipt is enough.
A sharper 0.1 contract is now:

- one cache-root manifest,
- one root-sharing report,
- one lock-wait receipt,
- optionally one wrapper-context receipt,
- one diagnosis report,
- and one mitigation plan.

## What changed in the archive

Added:

- `meta/cargo-contention-topology-boundaries-2026-03-08.md`
- `meta/frontier-salience-2026-03-08-25.md`
- `fixtures/cargo-lock-contention-witness-kit/root-sharing.report.schema.json`
- `fixtures/cargo-lock-contention-witness-kit/wrapper-context.receipt.schema.json`
- `fixtures/cargo-lock-contention-witness-kit/scenarios/build_dir_separated_target_still_shared/*`
- `fixtures/cargo-lock-contention-witness-kit/scenarios/wrapper_hash_split_same_target/*`
- `entries/2026-03-08-148.md`

Updated:

- `proposals/cargo-lock-contention-witness-kit.md`
- `fixtures/cargo-lock-contention-witness-kit/README.md`
- `README.md`
- `INDEX.md`
- `meta/known-existing.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/prioritization.md`
- `meta/territory-map.md`
- `meta/llm-hygiene.md`

## What should happen next

The best next passes should prefer:

1. freezing `root-sharing.report.json` vocabulary,
2. trying one real multi-tool workspace witness bundle,
3. and keeping wrapper-context receipts honest and optional.

They should **not** drift into:

- another generic Cargo/IDE doctor,
- a lock-arbitration daemon,
- or a faux-universal solution that claims target-dir separation eliminates build-dir and package-cache waits too.

## Sources

- Rust compiler performance survey 2025: https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- rust-analyzer FAQ: https://rust-analyzer.github.io/book/faq.html
- rust-analyzer configuration: https://rust-analyzer.github.io/book/configuration
- Cargo build-cache docs: https://doc.rust-lang.org/cargo/reference/build-cache.html
- Cargo environment variables: https://doc.rust-lang.org/cargo/reference/environment-variables.html
- Cargo cache-lock internals: https://doc.rust-lang.org/beta/nightly-rustc/cargo/util/cache_lock/index.html
- Cargo unstable features (`build-dir-new-layout`): https://doc.rust-lang.org/cargo/reference/unstable.html#build-dir-new-layout
- Cargo build-dir layout goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
