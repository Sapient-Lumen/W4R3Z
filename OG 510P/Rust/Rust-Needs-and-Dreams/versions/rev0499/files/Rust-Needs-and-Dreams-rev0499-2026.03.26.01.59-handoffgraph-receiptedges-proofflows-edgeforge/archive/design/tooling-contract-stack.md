## Current note (rev0457)
Read this stack as the implementation substrate beneath `design/tooling-contract-execution-blueprint-2026Q1.md`.

What changed in rev0457 is not the basic shape of the stack.
What changed is the repo’s interpretation:
- **Tooling Contract** is now an explicit execution blueprint rather than only a synthesis stack;
- **Repo Composition**, **Build Interop**, and **Build-State Evidence** remain imported owners beneath it;
- and future revisions should not flatten discovery/scope, graph/plan, execution/evidence, stability posture, and consumer handoffs into one fake “Cargo tooling API”.

# Design: Tooling Contract Stack (Repo Composition + Build Interop + Build-State Evidence)

## Goal
Treat **Cargo-facing machine contracts** as a first-class ecosystem seam.

The Rust ecosystem does not just need better caches, prettier workspace docs, or one more wrapper around `cargo metadata`. It needs a coherent contract story for:
- **discovery** — which workspace/config layers Cargo found,
- **selection** — which packages and configurations were actually in scope,
- **planning** — which units/artifacts Cargo intended to build,
- **execution** — which events, rebuild reasons, and outputs actually occurred,
- **handoff** — which IDEs, CI systems, wrappers, or outer build systems consumed that truth next.

The archive should therefore stop treating repo composition, build interop, and build-state evidence as merely adjacent tooling ideas. Together they form a reusable **Tooling Contract Stack** for machine-facing Rust workflows.

The proposal-layer candidate for that stack should be a thin `cargo tooling-contract` / `tooling-contract-pack/v0` composition layer that links existing artifacts instead of replacing them.

## Why this seam matters now
Official Cargo signals are now unusually aligned:
- The 2026 roadmap explicitly puts **integrate Cargo into larger build systems** and **prototype cargo plumbing commands** inside the “Building blocks” flagship, which is a direct signal that machine-facing Cargo contracts are strategic rather than incidental.
- Cargo’s accepted plumbing goal says current programmatic surfaces are still too porcelain-oriented, that `cargo metadata` excludes feature resolution, that `--build-plan` was not durable, and that the build can be split into explicit phases from project discovery through final-artifact staging.
- Cargo’s stable external-tools docs still describe only three general-purpose integration surfaces: `cargo metadata`, `--message-format=json`, and custom subcommands. Those are valuable, but they do not yet form one coherent discovery→plan→execute contract story.
- Cargo’s build-cache docs now publicly distinguish **final artifacts** in `target-dir` from **intermediate build artifacts** in `build-dir`, while also stating that the build-dir layout is internal and subject to change.
- The March 2026 `build-dir-new-layout` call for testing says many projects rely on unspecified build-dir details because Cargo still lacks the right features. That is exactly the kind of pain that justifies an explicit contract layer.
- Cargo’s build-analysis experiment now emits JSONL session logs with rebuild reasons and report commands, but it is opt-in and explicitly not yet a user-facing stability promise. That makes an evidence-import stack more realistic than pretending the experimental logs are already the whole answer.
- rust-analyzer still exposes a dedicated `cargo.targetDir` escape hatch specifically to avoid lock contention from its own `cargo check` / build-script / proc-macro activity, at the cost of duplicating artifacts. That is a concrete sign that external tools still lack a better shared contract with Cargo.
- Cargo 1.94 reiterates that Cargo plugins matter because Cargo cannot be everything to everyone, which fits a plugin-first contract stack extremely well.

## References (signals)
- Rust 2026 roadmap (“Building blocks”): https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo plumbing goal: https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- Cargo external tools reference: https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo build cache reference: https://doc.rust-lang.org/cargo/reference/build-cache.html
- Cargo build-analysis / reports / build-dir-new-layout docs: https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo build-dir-layout goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- Build-dir-new-layout call for testing: https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Cargo 1.94 dev-cycle note: https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- rust-analyzer configuration (`cargo.targetDir`): https://rust-analyzer.github.io/book/configuration

## Current archive decision
The right contribution is **not**:
- a Cargo daemon that becomes the one true Rust control plane,
- a universal monorepo/workspace manager,
- a frozen copy of Cargo internals,
- or another wrapper that still relies on undocumented `target/` / `build/` folklore.

It is a stack with explicit boundaries:
- [`design/repo-composition-stack.md`](./repo-composition-stack.md) owns discovery roots, config layers, workspace inheritance, package-selection truth, and bounded execution matrices.
- [`design/build-interop-kit.md`](./build-interop-kit.md) owns machine-facing workspace graphs, build plans, execution events, and bridge/adaptation posture.
- [`design/build-state-evidence-stack.md`](./build-state-evidence-stack.md) owns rebuild reasons, cache/reuse/block truth, relink opportunities, and diagnosis imports.

Together they should be treated as one **Tooling Contract Stack**.

## What a worthy contribution would look like in practice
### 1) Start from existing outputs and gaps, not a mega-schema fantasy
Prefer linking and refining:
- `workspace-report/v0`
- `config-set/v0`
- `workspace-graph/v0`
- `build-plan/v0`
- `cargo-events/v0`
- Cargo report / build-analysis imports
- optional raw attachments (`cargo metadata`, `--unit-graph`, rust-analyzer discovery JSONL, dep-info files, session logs)

If a bundle is needed, keep it thin (e.g. `tooling-contract-pack/v0`) and mostly pointer-based.

A good epic candidate should therefore add only a small composition family above the imported artifacts: `tooling-subject/v0`, `tooling-scope-report/v0`, `tooling-plan-register/v0`, `tooling-evidence-register/v0`, `tooling-consumer-handoff/v0`, and `tooling-contract-pack/v0`.

### 2) Keep discovery and package selection first-class
A credible tooling-contract contribution must say:
- which workspace/config roots were discovered,
- which config layers mattered,
- which packages were in scope by default,
- what `cwd`, `default-members`, or explicit flags changed,
- and which bounded work matrix downstream consumers actually used.

Without that, tools keep claiming to represent “the repo” while silently meaning different things.

### 3) Keep graph/plan truth separate from execution/evidence truth
The stack must preserve the difference between:
- **what Cargo planned**,
- **what dynamic build-script/proc-macro expansion changed**,
- **what ran**,
- **what rebuilt and why**,
- **what blocked or reused**,
- and **what consumers later concluded**.

This matters because build-dir layout changes, report logs, and rust-analyzer coexistence pain all come from collapsing these layers too early.

### 4) Prefer import/export seams over tool replacement
The stack should help:
- IDEs and rust-analyzer-adjacent tools,
- CI systems,
- release/perf/policy consumers,
- non-Cargo or mixed build systems,
- docs/support/incident tooling.

It should not try to become a new build system.

## Shared success criteria
A strong tooling-contract contribution should let a reviewer answer six questions quickly:
1. Which workspace/config roots did Cargo discover?
2. Which packages/configs were actually in scope?
3. What graph/plan did Cargo intend to execute?
4. What actually ran, blocked, reused, or rebuilt?
5. Which facts were stable imports versus experimental/report-only imports?
6. Which downstream consumers imported that exact truth next?

If the stack cannot answer those questions, it is not yet ecosystem infrastructure.

## Ranked opportunity inside this stack
1. **Discovery-boundary and package-selection truth**
2. **Graph/plan truth with explicit dynamic-expansion boundaries**
3. **Build-analysis / rebuild-reason / cache-layout imports**
4. **IDE and outer-build consumer adapters**
5. **Release/docs/support handoff consumers**

That order matters. The archive should not jump straight to one universal build protocol.

## Boundaries / non-goals
- not a replacement for Cargo
- not a replacement for rust-analyzer
- not a replacement for BSP
- not a replacement for build-system-specific orchestration
- not a promise that build-dir internals become stable forever
- not a justification for more target-dir scraping

## Why this is an ecosystem contribution, not just build-tool nerding
This seam affects small and large Rust users alike:
- small repos suffer when docs/tests/editors/CI disagree about package scope,
- service teams suffer when rebuild reasons and cache contention are opaque,
- tool authors suffer when stable Cargo outputs are too coarse but internal layouts keep moving,
- outer-build users suffer when the only practical integration story is partial scraping plus folklore.

A real Tooling Contract Stack would reduce that ambient friction without requiring one giant Rust-platform vendor.

See also [`proposals/epic-tooling-contract-stack.md`](../proposals/epic-tooling-contract-stack.md) for the proposal-layer framing of this seam as a concrete ecosystem contribution rather than only a synthesis note.
