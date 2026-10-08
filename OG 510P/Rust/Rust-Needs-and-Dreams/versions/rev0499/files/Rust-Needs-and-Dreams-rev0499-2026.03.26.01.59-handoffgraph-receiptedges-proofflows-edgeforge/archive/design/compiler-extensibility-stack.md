# Design: Compiler Extensibility Stack (MIR Analysis + Lint Governance + Compile Guidance + Conformance Traceability)

## Goal
Treat **compiler-attached Rust tools** as a first-class ecosystem layer with reviewable contracts.

The missing contribution is not one universal plugin ABI, one more nightly-only analyzer, or a campaign to merge every good tool into Cargo.
It is an explicit stack that lets Rust describe:
- how a tool attaches to compiler or Cargo surfaces,
- what subject/configuration it actually analyzed,
- what stability and capability promises it makes,
- what result families it emits,
- and how downstream consumers may safely import those results.

The archive already had many of the pieces.
What it still lacked was the synthesis saying that these pieces together define a real frontier for **compiler-extensibility products**.

## References (signals)
- The Rust vision work explicitly recommends **doubling down on extensibility** and says many future extensions — including theorem proving, GPU programming, distributed systems, and safety-critical tooling — want access beyond the earliest compilation stages. It names Stable MIR and build-std as examples.
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- The StableMIR goal says publishing compiler-facing crates is meant to enable analyzers, linters, dev environments, and other tools to work reliably across Rust versions without depending directly on compiler internals.
  https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
- The July 2025 goals update says `stable_mir` had become `rustc_public` and the effort had moved to release automation and an MCP toward publication.
  https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- The `cargo-semver-checks` goal shows real ecosystem demand: the tool is good enough to target Cargo integration, but still needs better cross-crate visibility, more precise type information, and witness-generation infrastructure.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- The same goal also documents the lesson from `semverver`: compiler-internal API dependence leads to chronic maintenance pain and eventual abandonment.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- Rust’s 2026 flagship themes explicitly include safety-critical lints in Clippy, prototype reflection, build-std design work, and cargo plumbing commands. Those are direct signals that compiler-adjacent tooling is becoming more important, not less.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo’s current development notes reiterate that Cargo cannot be everything to everyone and that plugins matter.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

## Why this needs its own synthesis layer
The archive already had:
- **Compile-Time Surface Stack** for code that runs while building the subject;
- **MIR Analysis Kit** for compiler-derived semantic export surfaces;
- **Lint Governance Stack** for selected policy, findings, debt, and fixpacks;
- **Compile Guidance Kit** for crate-authored diagnostics/help/example truth;
- **Conformance Traceability Stack** for spec and assurance consumers.

That is a strong substrate.
It is **not** yet the same thing as a clear answer to questions like:
- what kind of compiler attachment is this tool using;
- what stability promise is attached to that lane;
- whether a result is a lint, a witness, a derived graph, a fix candidate, or an assurance artifact;
- when a downstream consumer may gate on the output versus treat it as advisory;
- and how a tool graduates from “interesting nightly project” to “reviewable ecosystem component”.

Without that synthesis layer, the archive risks two bad outcomes:
1. **extension-point theater** — every new exporter or compiler hook gets treated as if it automatically creates a healthy tooling ecosystem;
2. **tooling theater** — useful but fragile tools get described as if they were already portable, stable, and composable.

## Design principles
1. **Attachment lanes must be declared explicitly.**
   Tools must say whether they attach through rustdoc JSON, `rustc_public`, MIR export, Clippy, witness compilation, Cargo plumbing, custom drivers, or a future hook.
2. **Subject identity is part of the result.**
   A compiler-aware result without exact package/workspace/target/profile/feature/toolchain identity is not reviewable enough.
3. **Capability and stability are separate truths.**
   A tool can be highly valuable while still being nightly-only or incomplete. That should be visible rather than hidden.
4. **Result families must stay distinct.**
   Lints, compatibility witnesses, derived graphs, compile guidance, fix packs, and conformance evidence are related but not interchangeable.
5. **Consumer permissions matter.**
   CI, editors, release review, policy, and assurance consumers should each know what they may and may not conclude from a given artifact.
6. **Plugins and companions are a valid end state.**
   Success is not defined by merging everything into Cargo.
7. **Tool product truth matters too.**
   Install/update/support posture and toolchain support for the tool itself remain part of the ecosystem contract.

## Stack layers
### 1) Attachment layer: how the tool observes or participates
This layer answers:
- which compiler/Cargo surface the tool uses;
- whether the lane is stable, nightly, experimental, or internal-to-the-tool;
- what observation scope or mutation authority exists.

Relevant archive components:
- [`design/mir-analysis-kit.md`](./mir-analysis-kit.md)
- [`design/compile-guidance-kit.md`](./compile-guidance-kit.md)
- [`design/compile-time-capabilities-kit.md`](./compile-time-capabilities-kit.md)
- [`design/build-interop-kit.md`](./build-interop-kit.md)

### 2) Subject/config layer: what exactly was analyzed
This layer answers:
- which package/workspace/target/profile/features/toolchain were in scope;
- whether cross-crate items, proc-macro expansions, generated code, or foreign items were visible;
- what inputs were imported (rustdoc JSON, MIR, witness programs, reports, etc.).

Relevant archive components:
- [`design/repo-composition-stack.md`](./repo-composition-stack.md)
- [`design/manifest-truth-stack.md`](./manifest-truth-stack.md)
- [`design/toolchain-productization-stack.md`](./toolchain-productization-stack.md)
- [`design/semantic-context-kit.md`](./semantic-context-kit.md)

### 3) Result layer: what kind of tool output this is
This layer answers:
- whether the output is a lint baseline, compatibility witness, query report, derived graph, fix pack, guidance pack, or conformance report;
- what completeness/incompleteness caveats attach to it;
- whether it is advisory or gating.

Relevant archive components:
- [`design/lint-governance-stack.md`](./lint-governance-stack.md)
- [`design/mir-analysis-kit.md`](./mir-analysis-kit.md)
- [`design/compile-guidance-kit.md`](./compile-guidance-kit.md)
- [`design/conformance-traceability-stack.md`](./conformance-traceability-stack.md)
- [`design/edit-workflow-kit.md`](./edit-workflow-kit.md)

### 4) Consumer layer: how others import the output
This layer answers:
- what CI, editor, release, policy, support, or safety consumers can import;
- what human review is still required;
- what conclusions are forbidden to automate.

Relevant archive components:
- [`design/policy-kit.md`](./policy-kit.md)
- [`design/public-api-kit.md`](./public-api-kit.md)
- [`design/support-envelope-kit.md`](./support-envelope-kit.md)
- [`design/package-admission-stack.md`](./package-admission-stack.md)

### 5) Product layer: how the tool itself ships and is supported
This layer answers:
- install/update identity;
- supported Rust/toolchain ranges;
- docs/example/support posture;
- release/provenance posture.

Relevant archive components:
- [`design/cli-productization-stack.md`](./cli-productization-stack.md)
- [`design/distribution-contract-stack.md`](./distribution-contract-stack.md)
- [`design/release-pipeline-kit.md`](./release-pipeline-kit.md)
- [`design/support-envelope-kit.md`](./support-envelope-kit.md)

## Artifact family
### 1. `tool-subject/v0`
Records:
- tool identity and version
- subject identity (package/workspace/release under analysis)
- target/profile/features/toolchain scope
- lane summary

### 2. `compiler-attachment-profile/v0`
Records:
- attachment family (`rustdoc-json`, `rustc_public`, `mir-export`, `clippy`, `witness-compile`, `cargo-plumbing`, `custom-driver`, etc.)
- stability posture (`stable`, `nightly`, `experimental`, `internal`)
- required flags/components/toolchains
- visibility limits and known blind spots

### 3. `analysis-input-profile/v0`
Records:
- imported inputs and provenance
- whether cross-crate/generated/foreign items were visible
- whether results depend on witness programs or synthetic compilations
- freshness / reproducibility notes

### 4. `tool-capability-profile/v0`
Records:
- result families the tool can emit
- known false-positive / false-negative / incompleteness posture
- whether the output is advisory, gating, or exploration-only
- whether auto-fix / auto-gate is allowed

### 5. `tool-result-report/v0`
Records:
- reason-coded findings, witnesses, derived graphs, diffs, or guidance
- machine-vs-human rendering boundaries
- attachment to supporting evidence
- uncertainty and waiver fields

### 6. `tool-consumer-handoff/v0`
Records:
- intended consumers (CI, editor, release review, safety review, policy, atlas, etc.)
- what they may import directly
- mandatory human-review boundaries
- forbidden automatic conclusions

### 7. `tool-pack/v0`
Bundle for review and reuse:
- subject
- attachment profile
- input profile
- capability profile
- result report(s)
- consumer handoff
- optional release/support attachments

## What a worthy contribution would look like in practice
A serious contribution here would:
- prove at least one stable-ish or supportable attachment lane;
- preserve nightly / incomplete lanes honestly instead of hiding them;
- let more than one consumer import the output without bespoke scraping;
- make it easier for maintainers to understand what a tool actually checked;
- leave behind diffable artifacts rather than screenshots or prose-only claims;
- and compose with Cargo/rustdoc/rustc/clippy motion rather than fighting it.

The bar is **not**:
- a one-off nightly demo;
- a magical compiler plugin story;
- or a polished dashboard that conceals scope and incompleteness.

The bar is a **portable contract layer for compiler-attached tools**.

## Boundaries and non-goals
- **Not Compile-Time Surface Stack:** that stack governs code that runs during the subject’s build (`build.rs`, proc-macros, replacements, profiles). Compiler Extensibility Stack governs external tools and consumers attached to compiler/Cargo surfaces.
- **Not one universal plugin ABI:** multiple attachment lanes may remain legitimate for a long time.
- **Not a replacement for MIR Analysis / Lint Governance / Compile Guidance / Conformance Traceability:** this stack coordinates them.
- **Not a blanket promise of stability:** explicit instability is acceptable when rendered honestly.

## Immediate archive consequence
The archive should now treat:
- **MIR Analysis Kit**,
- **Lint Governance Stack**,
- **Compile Guidance Kit**,
- and **Conformance Traceability Stack**

as one explicit **Compiler Extensibility Stack** in frontier discussions.

That does **not** demote the lower layers.
It clarifies that together they now form one of the more plausible paths toward an epic ecosystem contribution.

See also: [`proposals/epic-compiler-extensibility-stack.md`](../proposals/epic-compiler-extensibility-stack.md) for the explicit proposal-layer framing of this seam as a worthy ecosystem contribution.
