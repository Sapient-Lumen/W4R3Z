# Design: Cargo Build Interop Contract 2026Q1

## Thesis
The next worthy Rust ecosystem contribution in this band is **not** another Cargo wrapper, another `rust-project.json` generator, or another editor-specific integration shim.
It is a thin **Cargo build interop contract** that turns today's fragmented machine-facing surfaces into one reviewable boundary for:
- **workspace discovery**,
- **workspace / unit graph identity**,
- **build-plan intent**,
- **execution-event truth**,
- and bounded **adapter / handoff** layers for IDEs, CI, wrappers, and larger build systems.

This is the archive's existing **Build Interop Kit** promoted into an explicit frontier note because the upstream evidence now says Cargo-in-larger-build-systems is not a side quest.
It is one of the ecosystem's missing shared surfaces.

## Why now
The official signals have converged unusually well:
- Rust's 2026 flagship “Building blocks” roadmap explicitly includes **integrate Cargo into larger build systems** and **prototype cargo plumbing commands**.  
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The accepted Cargo plumbing goal already decomposes build orchestration into explicit phases — locate project, read manifests, read/write lockfile, resolve features, plan a build, execute a build, and stage final artifacts — and says later commands should accept the outputs of earlier ones.  
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- Cargo's external-tools docs still say the stable tool boundary is mainly `cargo metadata`, `--message-format=json`, and custom subcommands. Those are valuable, but they do not yet form one stable Rust workspace / plan / event contract for external orchestrators.  
  https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo removed the old unstable `build-plan` feature and explicitly pointed toward plumbing commands, `--unit-graph`, and structured logging as the better direction.  
  https://doc.rust-lang.org/cargo/CHANGELOG.html
- Cargo's unstable `--unit-graph` docs now say the format gives a more complete view of dependency relationships as Cargo sees them, and that `cargo metadata` fundamentally cannot represent some newer feature relationships across dependency kinds.  
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo 1.94 development notes show the machine-facing direction getting more real: structured logging work is active, `cargo report rebuild` and `cargo report sessions` exist, and workspace/config discovery is still sharp enough to poison unrelated builds.  
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- rust-analyzer now documents `workspace.discoverConfig` and a JSONL discover-command protocol for generating `rust-project.json`, but also warns that the output format is provisional and may change. It also exposes `{label}`-aware override commands, which proves editors already need stable mapping from file/save context to Cargo package IDs or external build labels.  
  https://rust-analyzer.github.io/book/configuration
- Fuchsia is a concrete proof of demand: its documented Rust editor workflow depends on a GN-generated `rust-project.json`, and the docs explicitly warn about rust-analyzer version / format mismatch risk.  
  https://fuchsia.dev/fuchsia-src/development/languages/rust/editors
- Outside Rust specifically, the Build Server Protocol exists because IDE ↔ build-tool integration otherwise degenerates into bespoke pairwise glue for targets, compile/test/run/debug actions, and progress reporting.  
  https://build-server-protocol.github.io/docs/specification.html

Together, those signals say the missing thing is no longer “better advice for build-tool authors.”
The missing thing is a bounded, reusable **workspace/graph/plan/event contract** above today's partial ingredients.

## What this frontier is actually changing
This note promotes the repo's earlier interop work as the next **outer-build-system / shared-workspace-surface** move.
It does **not** claim to be:
- the new overall #1 ecosystem need,
- a replacement for Build-State Evidence,
- a replacement for the Cargo artifact contract,
- or a universal external-build-system abstraction that erases Cargo.

The frontier change is narrower:
- keep **Build-State Evidence** as the strongest broad/buildable contribution;
- keep **Rust inner-loop contract** as the clearest build/debug bundle-shaping move;
- keep **Cargo artifact contract** as the clearest final-output / handoff seam;
- but promote **Build Interop Kit** as the clearest next **workspace-graph / plan / event / adapter** move for Cargo in larger build systems.

## Problem statement
Today, a serious downstream tool that wants to answer “what Rust workspace am I building, what units are in scope, what build intent was selected, and what is happening while it executes?” still has to reconstruct that story from a patchwork of:
- `cargo metadata`,
- unstable `--unit-graph`,
- `--message-format=json`,
- structured-logging experiments and new Cargo report commands,
- editor-specific discovery hooks,
- generated `rust-project.json`,
- and outer-build-system labels or generated-source conventions.

That patchwork is enough to build point integrations.
It is not enough to create one durable import layer for:
- IDEs,
- large monorepos,
- remote-build and wrapper tooling,
- CI orchestration,
- reproducible bug attachments,
- or future assistants that need bounded machine-readable context instead of scraping whatever each repo happened to invent.

## The worthy contribution
The worthy contribution is a thin contract family centered on the archive's existing interop substrate.

### Core truths that must stay separate
1. **Workspace-discovery truth**  
   Which file, buildfile, or repo root was used to discover a Rust workspace or target context, and what canonical workspace identity resulted.

2. **Workspace / unit-graph truth**  
   Which packages, crates, targets, generated sources, toolchain/sysroot identities, package IDs, and optional external labels make up the Rust graph under review.

3. **Build-plan truth**  
   Which command intent, package/target selection, feature posture, dynamic-expansion boundaries, and artifact intents were selected — without pretending every final shell command is statically knowable up front.

4. **Execution-event truth**  
   Which session started, which unit ran, why something rebuilt, what blocked, and what artifacts or diagnostics were emitted while the build actually happened.

5. **Adapter / handoff truth**  
   Which downstream consumers — rust-analyzer, BSP, CI wrappers, bug reports, monorepo tooling — are reading a native Cargo-aligned surface versus a projected adapter.

## Relationship to the Cargo artifact contract
This frontier is adjacent to, but distinct from, `design/cargo-artifact-contract-2026Q1.md`.

- **Build interop contract** answers: workspace discovery, graph identity, build intent, execution events, and adapter surfaces.
- **Cargo artifact contract** answers: final-output identity, origin/staging/uplift semantics, sidecars, and downstream artifact handoffs.

A worthy repo must keep both because larger-build-system integration fails if graph/plan/events are missing, while release/inventory/repro/support consumers fail if final-output identity and artifact-sidecars are missing.
The archive should not flatten those into one fake “Cargo integration” blob.

## Reference shape
A first serious version should still look like the archive's earlier interop family, but with the separation from artifact surfaces made explicit:
- `workspace-discovery/v0`
- `workspace-graph/v0`
- `build-plan/v0`
- `cargo-events/v0`
- `interop-pack/v0`

What changes in this revision is the emphasis:
- treat these as the likely **companion layer above current Cargo, rust-analyzer, and outer-build-system machine surfaces**;
- treat BSP as an adapter target rather than the source of truth;
- and keep final-artifact identity in the adjacent artifact contract instead of stuffing it into interop by accident.

## MVP in theory and practice
A worthy MVP would prove five concrete things.

### 1. Discovery can be frozen honestly
The tool must record how the workspace was found, which roots or buildfiles mattered, and what canonical identity resulted.

### 2. Cargo-native and non-Cargo labels can coexist
The tool must preserve Cargo package IDs while allowing outer labels from GN/Bazel/Buck-like systems without forcing one naming scheme to erase the other.

### 3. Build intent can be exported without lying
The tool must export units, edges, features, build-script and proc-macro boundaries, and dynamic-expansion points without pretending unstable commands or final shell lines already solve everything.

### 4. Execution can be streamed with stable correlation
The tool must export session and unit identity, start/end events, rebuild reasons, waits/locks, and diagnostic/artifact references in a way CI, IDEs, and bug reports can all correlate.

### 5. Adapters can stay adapters
The tool must prove rust-analyzer/BSP/outer-build-system consumers can import projected views without those projections becoming the canonical schema.

## Recommended CLI posture
A reference implementation could expose something like:
- `cargo interop discover`
- `cargo interop export-workspace`
- `cargo interop plan`
- `cargo interop events`
- `cargo interop validate`
- `cargo interop pack`

The first implementation should import native Cargo and rust-analyzer-adjacent surfaces where possible, state clearly what remains unstable, and fail closed when it cannot widen an observed graph/plan/event fact into a stronger claim.

## What this should not become
Do **not** turn this into:
- a new one-true build system,
- a required BSP layer,
- a replacement for Cargo metadata or Cargo report work,
- another repo-specific `rust-project.json` generator sold as a standard,
- or a giant hosted integration portal.

The right contribution is thinner and more reusable than that.

## Why this matters strategically
This frontier is “epic” because it sits exactly where several other archive priorities keep needing the same truth:
- **Build-State Evidence** wants stable session/unit/event identity.
- **Rust inner-loop contract** wants graph + event truth that composes with editor and debug workflows.
- **Cargo artifact contract** wants an adjacent but distinct upstream layer for selected subject and execution context.
- **Workspace Environment** wants one bounded handoff between human/editor/CI/agent views and the actual Rust workspace under build.
- **Large-build-system adoption** needs a Rust-native contract that outer orchestrators can project into, not just brittle bespoke glue.

That is why this revision promotes the seam now instead of leaving it as a clever lower-level note.

## Read this with
- `design/build-interop-kit.md`
- `gaps/build-system-interop-and-cargo-plumbing.md`
- `proposals/epic-build-interop-kit.md`
- `design/cargo-artifact-contract-2026Q1.md`
- `design/build-state-evidence-stack.md`
- `design/rust-inner-loop-contract-2026Q1.md`
- `design/workspace-environment-stack.md`
