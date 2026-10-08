## Execution addendum (rev0456)
Read `design/compatibility-claims-execution-blueprint-2026Q1.md` first when the question is no longer only “why does this seam matter?” but “what should the worthy contribution actually ship in theory and practice?”.

Interpretation rule:
- this note remains the contract/band explanation;
- the new execution blueprint is now the primary answer for build shape, proving lanes, and refusal boundaries;
- **Support Envelope** remains the platform/runtime/docs execution layer beneath this broader band; and
- imported debugger, acceptance, MSRV/toolchain, and public-boundary truths should remain adjacent owners rather than being silently absorbed.

# Design: Rust compatibility claims contract 2026Q1 (`cargo compat`, `compat-pack/v0`)

## Goal
Promote **compatibility claims** into a first-class Rust ecosystem contract layer.

The worthy contribution here is **not** another badge, another hosted matrix, another CI-wrapper, or another universal "supported" score.
It is the missing reviewable layer that says:

**what support a Rust subject declares, what was actually observed, which debugger tuples and visualizer lanes really work, which advanced pattern families are accepted on which compiler lanes, and what downstream docs/release/support/policy/safety consumers may honestly say.**

Read this together with:
- [`design/compatibility-claims-stack.md`](./compatibility-claims-stack.md)
- [`design/compatibility-claims-lane-map.md`](./compatibility-claims-lane-map.md)
- [`design/support-envelope-kit.md`](./support-envelope-kit.md)
- [`design/support-envelope-pilot-program.md`](./support-envelope-pilot-program.md)
- [`design/acceptance-surface-kit.md`](./acceptance-surface-kit.md)
- [`design/debuggability-stack.md`](./debuggability-stack.md)
- [`proposals/epic-compatibility-claims-stack.md`](../proposals/epic-compatibility-claims-stack.md)
- [`gaps/compatibility-claims-platform-debugger-and-acceptance-contracts.md`](../gaps/compatibility-claims-platform-debugger-and-acceptance-contracts.md)

## Why this seam matters now
Fresh official signals make this frontier much more concrete than it looked when the archive first named it.

- Rust’s target-tier policy already distinguishes target support from **host-tool** support, which means "supported target" is formally more structured than many crates and products communicate.
  https://doc.rust-lang.org/beta/rustc/target-tier-policy.html
- The official platform-support tables now carry real runtime-floor notes for many targets — minimum macOS versions, Linux kernel floors, glibc floors, ABI notes, and CPU-feature assumptions — which means support is not reducible to a target triple.
  https://doc.rust-lang.org/beta/rustc/platform-support.html
- Official support posture keeps moving in public: `x86_64-apple-darwin` was demoted to Tier 2 with host tools for Rust 1.90, while Rust 1.91 promoted `aarch64-pc-windows-msvc` to Tier 1. That makes support drift a normal review surface rather than a rare exception.
  https://blog.rust-lang.org/2025/08/19/demoting-x86-64-apple-darwin-to-tier-2-with-host-tools/
  https://blog.rust-lang.org/2025/10/30/Rust-1.91.0/
- docs.rs changed its default target list in October 2025. That proves docs-target posture is part of the public compatibility story, not a hidden rendering detail.
  https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- The 2025 State of Rust survey says online docs remain the preferred canonical reference while LLM/editor mediation rises. That sharply increases the value of attachable compatibility truth over prose-only caveats.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The Rust debugging survey makes debugger-family/version/OS support, visualizers, async debugging, and Rust expression evaluation explicit ecosystem concerns. That means debugger support is a compatibility lane in its own right.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- The next-solver goal explicitly aims to extend the new solver into lints and rustdoc, which means compiler-lane acceptance for advanced patterns will keep changing in ways downstream users may need to declare and diff.
  https://rust-lang.github.io/rust-project-goals/2025h2/next-solver.html
- The safety-critical adoption writeup explicitly recommends target-focused readiness checklists and ecosystem-wide MSRV conventions. That is unusually direct evidence that support posture needs to be reviewable, long-lived, and auditable rather than left to scattered issue threads and internal team memory.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/

Taken together, those signals say Rust is getting stronger at individual leaves — target policy, docs metadata, debugger work, acceptance evolution — but still lacks one honest layer for **compatibility-claim truth**.

## What changed in the archive’s understanding
The archive already had the ingredients for a compatibility story.
What it did **not** yet have was a clear statement that this is now the strongest next **support/claim-shaping** move rather than a pile of adjacent support/debugger/acceptance notes.

The new reading is:
- [`design/support-envelope-kit.md`](./support-envelope-kit.md) owns platform / docs / runtime-floor posture;
- [`design/acceptance-surface-kit.md`](./acceptance-surface-kit.md) owns advanced-pattern and compiler-lane posture;
- [`design/debuggability-stack.md`](./debuggability-stack.md) owns debugger-tuple / visualizer / async-inspection posture;
- **Compatibility Claims** is the thin composition layer that keeps those imported truths separate while making them reviewable and diffable together.

That is a stronger and more buildable claim than “support matters” or “debugging matters” in the abstract.

## The missing distinction
A worthy contribution here must keep at least six truths explicit.

### 1) Support-envelope truth
- dev-host
- source-build
- release-artifact
- docs-surface
- runtime-floor
- declared vs observed evidence

### 2) Debugger-tuple truth
- debugger family / version / OS / target / toolchain tuple
- visualizer availability
- async-inspection posture
- expression-evaluation posture
- partial vs supported vs watch lanes

### 3) Acceptance-surface truth
- named advanced pattern families
- stable / beta / nightly / experimental compiler lanes
- expected pass / fail / xfail posture
- workaround and reason-coded drift

### 4) Change truth
- what changed between releases
- what changed between toolchains
- whether the change widened, narrowed, or merely reclassified support

### 5) Consumer-summary truth
- docs-facing summary
- release-facing summary
- support-facing summary
- CI/policy/audit/safety-facing summary
- explicit forbidden conclusions for each consumer class

### 6) Handoff truth
- what the compatibility layer may conclude directly
- what still belongs to support-envelope, debugger, or acceptance owners
- what remains uncertain or imported without re-validation

## What a worthy contribution would look like in theory and practice
In theory, the right contribution is a thin contract layer:
- narrow enough to stay honest;
- structured enough to survive CI, release notes, docs pages, support handoffs, and assistant consumption;
- and modest enough to avoid becoming the one true support platform.

In practice, the worthy contribution looks like:
- a reference companion CLI, `cargo compat`;
- one attachable bundle family, `compat-pack/v0`;
- imports from Support Envelope, Debuggability, and Acceptance Surface rather than schema imperialism;
- explicit reason-coded diffs across releases or toolchain changes;
- and bounded renderers for docs, releases, support pages, CI, policy, audit, and assistants.

The MVP should be able to answer:
- which compatibility lanes exist for this crate/workspace/product,
- which lanes are declared vs observed,
- which debugger tuples actually worked,
- which advanced patterns are accepted on which compiler lanes,
- what changed since the previous release,
- and what each downstream consumer may safely say.

That is already a major ecosystem improvement over today’s combination of README prose, CI matrices, docs.rs defaults, issue templates, and maintainer memory.

## Ranked execution order
### 1) Public support-envelope + docs-surface lane
Prove:
- one real subject can export support-envelope entries for dev-host, source-build, release-artifact, and docs-surface;
- docs.rs target defaults and local declared targets stay visible instead of being flattened into one support bit;
- and a release/support consumer summary can import that truth honestly.

### 2) Debugger tuple lane
Prove:
- one real subject can attach debugger-family/version/OS/toolchain tuples;
- visualizer posture remains explicit;
- and support claims no longer imply debugger support automatically.

### 3) Advanced acceptance lane
Prove:
- one real subject can publish named advanced pattern families;
- stable/beta/nightly/experimental acceptance posture remains visible;
- and next-solver-related drift can be described without calling everything a regression.

### 4) Compatibility diff lane
Prove:
- one release-to-release or toolchain-to-toolchain diff can widen/narrow/reclassify support without losing origin;
- and downstream consumers can tell whether the change was platform, debugger, acceptance, or docs-surface in nature.

### 5) Long-lived / safety-oriented lane
Prove:
- one bounded support/audit/safety summary can import compatibility truth without pretending to automate certification;
- and target-readiness / MSRV / long-lived support notes remain explicit instead of folkloric.

## What not to build
Do **not** build:
- a hosted compatibility portal that becomes another platform empire;
- a universal compatibility badge;
- another CI matrix visualizer pretending screenshots are the source of truth;
- or a mega-schema that silently redefines support-envelope, debugger, and acceptance owners out of existence.

The point is a **reviewable contract layer**, not a new control tower.

## Archive consequence
The archive should now treat **Compatibility Claims** as the clearest next **support/claim-shaping** move beneath:
- Support Envelope,
- Debuggability,
- and Acceptance Surface.

That does **not** make it the broad new #1 ecosystem need.
It does mean the repo now has enough substrate to say a concrete, worthy, machine-usable thing about this frontier.
