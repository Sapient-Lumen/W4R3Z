## Current note (rev0457)
Read this proposal together with `design/tooling-contract-execution-blueprint-2026Q1.md`.

What changed in rev0457 is not the core proposal-layer shape.
What changed is the archive’s interpretation:
- **Tooling Contract** now has a direct execution answer;
- the worthy contribution should be understood as **reference layer + report/pack command + adapter/import corpus**;
- and future proposal work should prove discovery/scope, graph/plan, execution/evidence, stability posture, adapter lossiness, and bounded handoffs before widening into a control-plane platform story.

# Epic Proposal: Tooling Contract Stack (`cargo tooling-contract` + `tooling-contract-pack/v0`)

## Why this is worthy
Rust’s ecosystem increasingly needs **machine-facing Cargo truth that can be reviewed like contracts instead of reconstructed from folklore, target-dir scraping, and tool-specific workarounds**.

The signals are unusually aligned:
- Rust’s 2026 flagships explicitly place **integrate Cargo into larger build systems** and **prototype cargo plumbing commands** inside the “Building blocks” agenda. That is a direct signal that Cargo-facing contracts are now strategic infrastructure work.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo’s accepted plumbing goal says the current programmatic surfaces are still too porcelain-oriented, that `cargo metadata` excludes feature resolution, and that `--build-plan` was not a durable answer. It also frames the build as explicit phases from project discovery through final-artifact staging.
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- Cargo’s stable external-tools docs still center on only three broad integration lanes — `cargo metadata`, `--message-format=json`, and custom subcommands — and explicitly recommend version-pinning `cargo metadata` with `--format-version`. That is useful, but it is not yet one coherent discovery → scope → plan → execute story.
  https://doc.rust-lang.org/cargo/reference/external-tools.html
  https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- Cargo’s build-cache docs now distinguish final artifacts in `target-dir` from intermediate artifacts in `build-dir`, while also saying the build-dir layout is internal and subject to change. The unstable book adds that `build.build-dir` was stabilized in Rust 1.91 and that `--build-plan` was removed in 1.93. That is a strong sign that users need contracts above Cargo internals, not more dependence on them.
  https://doc.rust-lang.org/cargo/reference/build-cache.html
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo’s build-analysis experiment now records JSONL session logs and exposes `cargo report sessions`, `cargo report timings`, and `cargo report rebuilds`, but the feature is still explicitly unstable. That means a worthy contribution should import report evidence honestly rather than mistake it for a finished stable interface.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo 1.94 reiterates that Cargo cannot be everything to everyone, highlights plugins, continues work on build-dir layout, target-dir locking, structured logging, and workspace/config discovery, and keeps “prototype cargo plumbing commands” in the no-progress-yet queue. That is almost a mission statement for a companion-layer proposal.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- rust-analyzer’s `cargo.targetDir` setting exists specifically to avoid lock contention from its own `cargo check` / build-script / proc-macro activity, at the cost of duplicating artifacts. That is exactly the sort of ecosystem pain a tooling-contract layer should make legible instead of hiding behind editor-specific folklore.
  https://rust-analyzer.github.io/book/configuration
- The March 2026 build-dir-v2 testing call says the build-dir is internal-only **but many projects need to rely on unspecified details due to missing features within Cargo**. That is one of the clearest possible demand signals for a thin contract layer.
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/

But the ecosystem still has no single honest handoff for **tooling-contract truth**.
That means IDEs, wrappers, CI systems, support engineers, release tooling, and outer build systems still have to reconstruct the answer from:
- workspace/config discovery behavior,
- `default-members` / cwd / explicit package-selection rules,
- `cargo metadata` snapshots,
- unstable unit-graph and report lanes,
- rust-analyzer or wrapper-specific workarounds,
- build-dir and dep-info scraping,
- and issue-thread archaeology when the stories disagree.

The missing contribution is a thin composition layer above those pieces, not a Cargo daemon, a BSP-only bridge, another target-dir scraper, or a universal monorepo control plane.

## Proposal
Define a **Tooling Contract Stack** with:
- a reference companion CLI, `cargo tooling-contract`;
- a thin linked bundle, `tooling-contract-pack/v0`;
- imported evidence from:
  - `workspace-report/v0` attachments,
  - `config-set/v0` attachments,
  - `workspace-graph/v0` attachments,
  - `build-plan/v0` attachments,
  - `cargo-events/v0` and build-state/report imports,
  - optional raw attachments (`cargo metadata`, `--unit-graph`, rust-analyzer discovery output, dep-info files, report JSONL logs);
- stable tooling-contract-facing artifacts:
  - `tooling-subject/v0`
  - `tooling-scope-report/v0`
  - `tooling-plan-register/v0`
  - `tooling-evidence-register/v0`
  - `tooling-consumer-handoff/v0`
  - `tooling-contract-pack/v0`

## Reference CLI shape
- `cargo tooling-contract export-scope`
  - emit `tooling-subject/v0` and `tooling-scope-report/v0` for one workspace / cwd / package-selection lane
- `cargo tooling-contract export-plan`
  - emit `tooling-plan-register/v0` linking graph / plan artifacts and marking dynamic-expansion boundaries
- `cargo tooling-contract import-evidence`
  - emit `tooling-evidence-register/v0` from `cargo report`, build-analysis logs, execution events, and optional raw attachments
- `cargo tooling-contract handoff --for <ide|ci|outer-build|docs|release|support|assistant>`
  - emit `tooling-consumer-handoff/v0`
- `cargo tooling-contract pack`
  - produce `tooling-contract-pack/v0`
- `cargo tooling-contract verify-pack <path>`
  - verify schema versions, checksums, imported-attachment integrity, and explicit stable-vs-experimental posture markers

This should stay a **thin composition layer**.
It should not replace Cargo, rust-analyzer, BSP, Bazel/Buck/GN, Cargo Report, or any future built-in plumbing commands.

## What `tooling-contract-pack/v0` should contain
- `manifest.json`
- `tooling-subject.json`
- `tooling-scope-report.json`
- `tooling-plan-register.json`
- `tooling-evidence-register.json`
- one or more `tooling-consumer-handoff.json` attachments
- imported workspace / config / graph / plan / execution / report attachments or pointers
- checksums, freshness, provenance, and generator identity
- explicit `stability_posture` fields for imported evidence
- optional docs / release / support / incident pointers

## Design principles
- **Discovery and scope come first.** If the tool cannot say what Cargo discovered and what packages were actually in scope, the rest is already suspect.
- **Plan truth stays distinct from live execution truth.** Dynamic build-script / proc-macro effects and report logs should not be smuggled into a fake deterministic plan.
- **Stable contracts stay distinct from experimental imports.** `cargo metadata` with a version pin is not the same kind of promise as nightly report logs or layout probes.
- **Adapters are allowed to be lossy, but not silently.** rust-analyzer, BSP, wrappers, and outer-build bridges each need explicit lossiness notes.
- **Plugin-first is a success mode.** “Useful as a companion tool” is a real win and often the right first destination.
- **Consumer conclusions stay bounded.** IDEs, CI, docs, release review, support, and assistants should each import an explicit handoff instead of freelancing from raw logs.

## Early implementation order
1. discovery / package-selection lane
2. graph / plan lane
3. build-analysis / report-import lane
4. rust-analyzer / IDE / outer-build adapter lane
5. docs / release / support / assistant handoff lane

That order follows the real ecosystem pressure: first stop tools from disagreeing about what repo and package set they mean, then stop them from disagreeing about intended work, then make experimental execution evidence importable, and only after that widen the consumer surface.

## Non-goals
- a universal Cargo daemon;
- a promise that build-dir internals are now stable forever;
- a BSP replacement or BSP-only design;
- a new universal monorepo manager;
- another wrapper that still depends on target-dir folklore while pretending not to;
- one schema that tries to normalize every build system and every Rust tool at once.

## Success bar
This becomes worthy when a maintainer or downstream consumer can answer:
- what Cargo discovered;
- what package/configuration scope was actually selected;
- what graph/plan Cargo intended to execute;
- what evidence came from stable contracts versus experimental imports;
- what actually ran, rebuilt, blocked, or duplicated;
- what adapter lossiness remained;
- and what a given consumer may safely conclude,

without scraping `target/`, reverse-engineering rust-analyzer settings, or triangulating from issue threads.

## Read this with
- `design/tooling-contract-stack.md`
- `design/tooling-contract-pilot-program.md`
- `design/repo-composition-stack.md`
- `design/build-interop-kit.md`
- `design/build-state-evidence-stack.md`
- `design/workspace-governance-kit.md`
- `design/config-set-kit.md`
