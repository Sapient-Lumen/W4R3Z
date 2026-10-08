# Cargo contention topology boundaries — 2026-03-08

## Main judgment

**P-0490 Cargo Lock Contention Witness Kit** is now ready for a more implementation-shaped reading.

The strongest missing value is not merely “a lock wait receipt”.
It is a small bundle that keeps **root identity**, **sharing topology**, and **wrapper/cache-mode context** separate enough that another person can tell what sort of contention they are looking at.

## Three root classes that should stay separate

Current Cargo and rust-analyzer docs make three different root classes explicit enough that future revisions should not flatten them together:

1. **target-dir** — where final build artifacts and user-facing outputs like docs or timings live.
2. **build-dir** — where intermediate Cargo/rustc artifacts live; this is now documented separately from target-dir.
3. **package/index cache roots** — Cargo home registry/index/git caches coordinated by Cargo cache-locking.

A good P-0490 bundle should be able to say:

- “the target-dir remained shared even after a build-dir change”,
- “the build-dir was isolated but the package cache still serialized dependency work”,
- or “the roots were shared, but wrapper-induced cache separation means the cost is not just waiting”.

## Wrapper and cache-mode context is not optional folklore

Current docs also make wrapper context more first-class than before:

- rust-analyzer documents `cargo.buildScripts.useRustcWrapper`, override-command knobs, and a dedicated `cargo.targetDir` mitigation.
- Cargo documents `RUSTC_WRAPPER` and `RUSTC_WORKSPACE_WRAPPER`, and explicitly says the workspace wrapper affects the filename hash so artifacts are cached separately.

That means future passes should not reduce wrapper context to a casual note.
If wrapper or cache-mode drift materially changes the diagnosis, the bundle should export a small `wrapper-context.receipt.json` rather than burying that fact in prose.

## What this crate should not become

### Not P-0494
P-0494 is still the crate that answers **what tool-facing workflow actually built**.
P-0490 can reuse tool-role facts from that stack, but should stay on **blocking / waiting / shared-root topology**.

### Not P-0489
P-0489 is still about **which tools scrape Cargo’s internal build-dir layout and how they migrate**.
P-0490 may mention build-dir roots, but should not turn into a consumer migration planner.

### Not P-0469
P-0469 is still about **why work rebuilt**.
P-0490 is about **why progress stalled**.
The same session can involve both, but the support artifact should keep them distinct.

## Best next repo moves

Future passes on this frontier should prefer:

1. freezing vocabulary for `root-sharing.report.json` and `wrapper-context.receipt.json`,
2. scenario bundles that separate target-dir, build-dir, and package-cache waits,
3. conservative diagnoses for wrapper mismatch and cache-mode split,
4. and explicit path / process-name redaction rules.

They should not drift into:

- another generic Cargo performance dashboard,
- a scheduler or lock arbiter,
- or a pseudo-universal “parallel build fix” crate.

## Sources

- https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- https://rust-analyzer.github.io/book/faq.html
- https://rust-analyzer.github.io/book/configuration
- https://doc.rust-lang.org/cargo/reference/build-cache.html
- https://doc.rust-lang.org/cargo/reference/environment-variables.html
- https://doc.rust-lang.org/beta/nightly-rustc/cargo/util/cache_lock/index.html
- https://doc.rust-lang.org/cargo/reference/unstable.html#build-dir-new-layout
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
