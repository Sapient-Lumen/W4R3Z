## Frontier note (rev0402)
This gap should now be read as evidence for the explicit **Semantic Context Contract** frontier.

Interpretation rule:
- the missing seam is not merely “cross-crate semver blockers”; it is the broader absence of one reviewable boundary for **subject identity, authority lanes, merge/completeness, and consumer imports** across semver, docs, fix, IDE, CI, and assistant workflows.


# Gap: Cross-crate semantic context is still too fragmented

## Summary
Rust now has enough promising machine-readable pieces that the next high-leverage ecosystem contribution is **not** another one-off consumer of those pieces.
It is the missing **semantic-context substrate** that lets many tools talk about the same build subject honestly.

Today, if a tool wants to answer a question like:
- what public items are actually visible in this build context?
- which dependency features are active recursively?
- which foreign item came from which crate and under which cfg/feature assumptions?
- can I reuse docs.rs rustdoc JSON here, or do I need a local build?
- is this answer coming from rustdoc JSON only, or from a deeper compiler-backed merge?

…it usually has to assemble that answer by hand from a custom mix of Cargo metadata, lockfiles, local builds, rustdoc JSON, ad hoc caches, private heuristics, and sometimes compiler internals.

That is not just inconvenient.
It means every serious tool ends up building a different partial workspace index and a different set of completeness assumptions.

## Why this matters now
- The accepted Cargo plumbing goal says Cargo’s programmatic surface is too thin and explicitly notes that `cargo metadata` can include dependency resolution but **excludes feature resolution**. It also lays out phases like **resolve features** and **plan build** as first-class parts of the build pipeline.
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- The 2025 GSoC plumbing prototype actually implemented subcommands like `resolve-features` and `plan-build`, which is strong evidence that the right next step is reusable machine-facing context, not more scraping of porcelain UX.
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- The July 2025 `cargo-semver-checks` update is unusually explicit about the remaining blockers for correct cross-crate work:
  - docs.rs hosting rustdoc JSON helps as a cache,
  - but the ecosystem still lacks a way to determine recursively active dependency features from Cargo interfaces,
  - and correct cross-crate combination still needs `rmeta`-based support.
  https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- docs.rs now builds and hosts rustdoc JSON directly, says it is useful for programmatic inspection of docs and types, and warns consumers to check `format_version` because different Rustdoc versions matter.
  https://docs.rs/about/rustdoc-json
- StableMIR publication work exists specifically to let tool authors analyze compiled crates and their dependencies without direct dependence on compiler internals, and the 2025 GSoC results say the refactoring to publish `rustc_public` independently with proper versioning support was completed for the tooling ecosystem.
  https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Cargo’s 1.93 development-cycle post says Cargo is already thinking about unifying structured-report schemas with Cargo’s JSON output to support a faster, more flexible `cargo fix` architecture. That is strong evidence that machine-facing data-plane quality is now a mainstream Cargo concern, not a niche tooling hobby.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/

## What is still missing
The ecosystem still lacks one portable answer to these basic questions:

### 1. What subject is this answer about?
A workspace, one package, one target/profile/feature set, a docs.rs-hosted release, and a CI artifact are not interchangeable.
Yet many tools still answer semantic questions without making the subject explicit enough.

### 2. Which inputs were actually used?
Was the answer based on:
- Cargo resolution facts,
- metadata fallbacks,
- local rustdoc JSON,
- docs.rs rustdoc JSON,
- compiler-side merge support,
- `rustc_public` / StableMIR exports,
- or some mix of the above?

Those should not be invisible implementation details.

### 3. How complete is the merge?
If recursive dependency features could not be known precisely, or if cross-crate merging fell back to rustdoc JSON only, or if one crate was missing a suitable docs.rs artifact, the tool should be able to say that structurally.

### 4. Which downstream answer is being claimed?
A semver check, a doc item lookup, a lint/fix context query, and an assistant-context export are different consumer questions. They should not each require a different hidden workspace index.

### 5. Can the result be diffed and attached?
Teams need to compare semantic context across PRs, releases, toolchains, or caches without rerunning every expensive step or reverse-engineering each tool’s custom cache layout.

## Why this is strategic
This is a worthy ecosystem contribution because it sits underneath many other important contributions:
- semver/public-API tooling,
- docs/search/discoverability tooling,
- compiler-aware lint/fix flows,
- IDE/editor integration,
- CI/review bots,
- assistant-style bounded-context generation.

In other words, this is not “one more consumer feature”.
It is the **missing shared data plane** that can keep many future tools from hardening around incompatible partial truths.

## What “good” looks like
A good solution would let a maintainer or tool produce one attachable pack that answers:
1. what workspace/package/target/profile/features/cfg/toolchain subject was captured?
2. which Cargo-resolution and build-planning facts were available?
3. which semantic input lanes were used (docs.rs rustdoc JSON, local rustdoc JSON, `rmeta`, `rustc_public`, etc.)?
4. what merge/completeness/confidence story applies?
5. which derived semantic answers came out of that context?
6. what changed relative to another pack?

That would give Rust something it currently lacks: a way for multiple tools to reuse **one semantic capture** instead of rebuilding incompatible caches and silently divergent assumptions.

See:
- `design/semantic-context-lane-map.md`
- `design/semantic-context-kit.md`
- `proposals/epic-semantic-context-kit.md`
