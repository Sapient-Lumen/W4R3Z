# Gap: Build-system interop and Cargo plumbing are still too provisional

## Summary
Rust increasingly needs to live inside **larger build systems, monorepos, editor workflows, wrappers, and restricted execution environments**. Cargo already exposes some machine-facing surfaces, but the story is still fragmented:
- `cargo metadata` is stable and versioned, but it is about package structure and resolved dependencies, not the full execution graph or live build state.
- `--message-format=json` reports diagnostics, artifacts, and build-script results, but it is not a full execution/event model and cannot control arbitrary output from other tools.
- `--unit-graph` is closer to Cargo’s real internal build graph, but it is still unstable.
- the old `--build-plan` experiment was removed entirely, with Cargo pointing toward plumbing commands, `--unit-graph`, and structured logging as the better path forward.
- rust-analyzer and non-Cargo build systems are converging on discovery hooks and `rust-project.json`, but the discover-command format is explicitly provisional and real ecosystems like Fuchsia still warn about version mismatches.

That means the missing contribution is not “yet another wrapper around `cargo metadata`”. The missing seam is a **stable discovery / graph / plan / event contract layer** that can sit between Cargo, rust-analyzer, IDEs, CI, wrappers, and non-Cargo build systems.

It is also not the same thing as the archive's newer **Cargo artifact contract** frontier: build interop is about how a Rust workspace is discovered, described, planned, and observed while it runs; artifact contract work is about what final outputs and sidecars Cargo exposed afterward.

## Why now
- Rust’s 2026 flagship themes explicitly call out **integrating Cargo into larger build systems** and **prototyping cargo plumbing commands** as part of the “Building blocks” roadmap. That is a direct signal that this is an ecosystem-level need, not a niche complaint.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The accepted 2025H1 Cargo plumbing goal says today’s machine-facing commands are still too porcelain-oriented, notes that `cargo metadata` excludes feature resolution, and explicitly frames third-party plumbing commands as the path for experimenting with what should be integrated upstream.
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- Cargo’s external-tools docs already say simple integration with IDEs and other build systems is a goal, but they also make the present boundary visible: stable package metadata, JSON build messages, and custom subcommands — useful primitives, but not yet a complete interop substrate.
  https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo 1.94 development notes show the machine-readable direction getting more real: structured logging work is active, `cargo report rebuild` and `cargo report sessions` were added, and workspace/configuration discovery is being revisited because accidental parent manifests/config files can still break builds in surprising ways.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- The Cargo changelog now records a major strategic move: the unstable `build-plan` feature was removed, with the Cargo team explicitly looking to plumbing commands, `--unit-graph`, and structured logging to fill the gap.
  https://doc.rust-lang.org/beta/cargo/CHANGELOG.html
- The unstable `--unit-graph` docs are unusually revealing: they say each unit corresponds to a compiler execution, that the structure is more complete than `cargo metadata`, and that `cargo metadata` fundamentally cannot represent feature relationships between dependency kinds under the newer resolver.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- rust-analyzer now documents `workspace.discoverConfig` as a way to generate `rust-project.json` on the fly for non-Cargo systems, with JSONL progress/error/finished events — but it also warns that the discover-command output format is provisional and subject to change.
  https://rust-analyzer.github.io/book/configuration
- rust-analyzer’s `check.overrideCommand` and `{label}` interpolation show another important seam: editor diagnostics already need a stable way to map from file/save actions to Cargo package IDs or external build labels.
  https://rust-analyzer.github.io/book/configuration
- Fuchsia is a concrete proof of demand: its documented Rust workflow uses a GN-generated `rust-project.json`, and the docs explicitly warn that the format is unstable enough to cause version mismatches with rust-analyzer.
  https://fuchsia.dev/fuchsia-src/development/languages/rust/editors
- Outside Rust specifically, the Build Server Protocol exists precisely because IDEs and build tools otherwise need bespoke per-pair integrations for source layouts, compiler options, compile/test/run actions, and more.
  https://build-server-protocol.github.io/docs/specification.html

## Concrete missing pieces
1. **Stable workspace discovery events**
   - progress / error / finished semantics
   - file/build-label context
   - canonical workspace identity
   - explicit compatibility policy
2. **A versioned workspace/build graph descriptor**
   - packages and crates
   - feature-resolved units
   - toolchain + sysroot identity
   - build labels / target labels for non-Cargo systems
   - canonicalized roots and generated-source paths
3. **A machine-readable build plan boundary**
   - command-intent and artifact-intent without pretending every final command line is static
   - build-script and proc-macro boundaries as first-class nodes
   - enough fidelity for IDEs, wrappers, and remote/distributed build orchestration
4. **A stable execution event stream**
   - session identity
   - unit start/end
   - artifact emission
   - rebuild reasons and block/wait states
   - correlation with Cargo report outputs
5. **Interop packs and adapters**
   - something portable to hand from build system → editor → CI → repro artifact
   - adapters to BSP, rust-analyzer, and Cargo-native report tools

## Desired properties
- Converge existing primitives instead of replacing Cargo.
- Preserve the distinction between **discovery**, **planning**, **execution**, and **post-hoc reports**.
- Work for pure Cargo workspaces and non-Cargo orchestrators.
- Be honest about what is static versus what depends on build-script output.
- Make labels, packages, and units traceable across tools.
- Reduce bespoke `rust-project.json` generators and log scraping.

## Distinction from nearby archive entries
- **Cargo Report Kit** standardizes post-build analysis artifacts such as timings and rebuild reports; this gap is about the more fundamental machine-facing discovery/plan/event boundary underneath those reports.
- **Workspace Governance Kit** is about Cargo-native inheritance, nested workspaces, profile/lint behavior, and explaining repo composition; this gap is about IDE/build-system interoperability even when Cargo is only one participant.
- **CompileDB Kit** focuses on native-code IDE support for `cc`/build.rs outputs; this gap is about Rust crate/unit discovery, planning, and execution surfaces.
- **Resolution Doctor Kit** explains dependency/version/feature outcomes; this gap is about transporting the selected workspace/unit graph to tools in a stable way.
