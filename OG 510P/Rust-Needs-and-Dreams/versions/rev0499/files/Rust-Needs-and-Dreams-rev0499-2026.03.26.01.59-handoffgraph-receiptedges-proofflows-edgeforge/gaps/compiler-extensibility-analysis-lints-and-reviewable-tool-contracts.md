# Gap: compiler-attached Rust tools still lack reviewable extension contracts

Rust increasingly depends on **tools that attach to the compiler** rather than merely compile ordinary crates.
These include:
- SemVer and API-compatibility analyzers;
- custom lint packs and assurance-heavy lint families;
- MIR- and rustdoc-backed analyzers;
- guidance/fix/report tools that sit above compiler outputs;
- conformance, safety, and verification consumers that need compiler-derived evidence;
- and future tooling built on `rustc_public`, reflection work, cargo plumbing, or later extension hooks.

But the ecosystem still lacks a portable way to say:
- **how** a tool attaches to the compiler or Cargo,
- **what** subject and configuration it actually analyzed,
- **which** stability and completeness promises it makes,
- **what** findings, witnesses, edits, or evidence it emitted,
- and **what** downstream CI/editor/release/safety consumers may legitimately conclude.

Today those answers are scattered across:
- nightly flags and compiler-driver glue;
- rustdoc JSON or MIR exporter details;
- Clippy configuration and tool-specific CLI flags;
- README caveats about required toolchain versions;
- issue threads about “this output is stable enough for us”;
- and private maintainer memory about which tool versions still work together.

That fragmentation is precisely what keeps promising compiler-aware tooling from becoming durable ecosystem infrastructure.

## Why this now matters more
Several current Rust signals make the missing seam unusually explicit:

- The Rust vision work says Rust should **double down on extensibility**, specifically beyond the earliest compilation stages, and names Stable MIR and build-std as examples of the needed direction.
- The StableMIR / `rustc_public` goal is explicitly about publishing a stable compiler-facing crate so tool developers can build analyzers, linters, dev environments, and other applications without tying themselves directly to compiler internals.
- The July 2025 project-goals update says the `stable_mir` crate had already been refactored into `rustc_public` and the work had shifted to release/testing infrastructure and the path to publishing.
- The `cargo-semver-checks` goal is an unusually concrete proof point: it is popular enough to be considered for Cargo integration, but still blocked by cross-crate visibility, type precision, witness-generation infrastructure, and unstable-ish compiler-facing inputs.
- That same goal explicitly documents a past failure mode: `semverver` depended on compiler-internal APIs, became high-maintenance, and ended up deprecated. Rust clearly needs a better contract for compiler-attached tools than “keep chasing nightly internals.”
- The 2026 flagship themes make the demand broader, not narrower: safety-critical lints in Clippy, prototype reflection, build-std design work, and cargo plumbing commands all point toward a larger ecosystem of compiler-adjacent tools that need cleaner attachment and handoff boundaries.
- Cargo’s current development notes keep repeating that Cargo cannot be everything to everyone and that plugins matter. That strongly suggests the missing contribution is a **companion contract layer**, not a fantasy where every good tool is instantly absorbed into Cargo.

Taken together, the missing problem is not merely “how do we write one more analyzer?”
The missing problem is:

**how does Rust let compiler-attached tools become reviewable, comparable, and supportable ecosystem products instead of brittle one-off integrations?**

## What is missing
The ecosystem still lacks a portable layer that keeps these truths distinct but composable:

1. **Attachment truth**
   - whether a tool attaches via rustdoc JSON, `rustc_public`, MIR export, Clippy, witness compilation, Cargo plumbing, custom drivers, or a future hook;
   - whether the lane is stable, nightly, experimental, or internal-to-the-tool;
   - what the attachment point can and cannot observe.

2. **Subject and configuration truth**
   - which package/workspace/target/profile/features/edition/toolchain were analyzed;
   - whether foreign items, cross-crate items, proc-macro expansions, or generated code were in scope;
   - whether the tool reasoned about source, rustdoc JSON, MIR, type-check witnesses, or a mix.

3. **Capability and stability truth**
   - what classes of findings or guarantees the tool claims to provide;
   - what false-positive / false-negative or incompleteness boundaries are known;
   - whether a result is advisory, gating, or only fit for local exploration.

4. **Result and handoff truth**
   - whether the output is a lint set, witness report, compatibility verdict, guidance catalog, fix pack, conformance report, or another evidence family;
   - how CI, editors, release review, policy, or safety consumers import it;
   - what they are forbidden to conclude automatically.

5. **Product and support truth**
   - install/update posture;
   - supported Rust/toolchain ranges;
   - docs/examples/support posture;
   - release and maintenance expectations for the tool itself.

## What this should not become
This should **not** become:
- one universal compiler-plugin ABI declared before the design space is ready;
- another Cargo-merger wishlist that treats every promising plugin as destined for `cargo` core;
- a fake “stable analyzer” badge that hides nightly or incomplete lanes;
- a single schema that flattens lints, witness compilers, MIR analyzers, spec tools, and generated fixes into one output shape;
- or a compiler-internals wrapper dressed up as ecosystem infrastructure.

The missing contribution is a **reviewable compiler-extensibility boundary** above today’s analyzers, lints, and assurance tools.

## What a worthy contribution would look like
A real contribution here would define a thin artifact family and workflow that can:
- declare **which compiler/Cargo attachment lane** a tool uses;
- capture the exact analysis subject and configuration;
- record the tool’s capability, completeness, and stability posture;
- export results and handoffs in a form other tools can consume;
- support side-by-side comparison of multiple compiler-aware tools without pretending they are equivalent;
- and let Cargo/CI/editor/release/safety consumers import the same facts instead of screen-scraping bespoke outputs.

That contribution would not replace all existing tools.
It would make them **compose**.

## Likely shape of the solution
The strongest path is an explicit **Compiler Extensibility Stack** that composes:
- **MIR Analysis Kit** for compiler-derived semantic exports;
- **Lint Governance Stack** for selected policy, findings, debt, and fix handoffs;
- **Compile Guidance Kit** for maintainer-authored diagnostics/help/example truth;
- **Conformance Traceability Stack** for spec/assurance consumers;
- and imports from **Tooling Contract Stack**, **Toolchain Productization Stack**, and **Support Envelope / CLI Productization** where a tool needs discovery, activation, or support truth.

This would let Rust talk honestly about compiler-aware tools as **products with attachment contracts**, not just “nightly experiments that happen to be useful.”

## Why this belongs in the archive now
The archive already had strong lower layers:
- compile-time authority and replacement work;
- MIR analysis;
- lint governance;
- compile guidance;
- conformance/safety evidence;
- Cargo plumbing and tooling-contract concerns.

What it still lacked was the explicit synthesis saying that a worthy contribution may need to be **the product layer for compiler-attached tools themselves**, not only another analyzer, macro helper, or build wrapper.

That is the layer most likely to turn current official momentum into something durable.

## References (signals)
- What do people love about Rust?
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- Publish first version of StableMIR on crates.io:
  https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
- Project goals update — July 2025 (`stable_mir` → `rustc_public` update):
  https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- Continue resolving `cargo-semver-checks` blockers for merging into Cargo:
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- Prototype a new set of Cargo plumbing commands:
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- Rust in 2026 flagships:
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- This Development-cycle in Cargo: 1.94:
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
