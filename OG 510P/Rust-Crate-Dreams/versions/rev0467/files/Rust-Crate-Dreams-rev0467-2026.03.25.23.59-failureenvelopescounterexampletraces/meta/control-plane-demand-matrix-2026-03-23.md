# Control-plane demand matrix — 2026-03-23

This note exists to make broad archive planning **wider and more honest at the same time**.

The archive now has many proposals.
The recurring planning mistake is to jump from “here is a real Rust subculture” to “therefore the repo needs another sector-specific crate proposal.”
Often the sharper missing seam is still a **shared control-plane crate**.

This matrix asks a simpler question:

> Across a wide range of real Rust use cases, which archive lanes keep showing up as the best next missing building blocks?

## Main judgment

Across a very wide set of use cases, the strongest repeating needs are still:

1. **crate choice / starter-set decision infrastructure** — P-0509,
2. **dependency transition / exit infrastructure** — P-0535,
3. **debug / support / target truth infrastructure** — P-0486 and P-0484,
4. **machine-usable, cited crate knowledge** — P-0536,
5. **concurrency/runtime semantics and deployment truth** — P-0538 and P-0532,
6. **compile/build/test workflow evidence** — P-0537 and adjacent build/test lanes,
7. **crate stewardship / health / public-boundary truth** — P-0011 and P-0431.

That is why the archive should usually deepen these lanes before opening another narrow sector track.

## Matrix

### 1. Teaching / newcomer / CLI baseline
**Why it matters:** many people first meet the ecosystem through CLI tools, config, logging, error handling, and small utility crates.

**Top missing lanes:**
- **P-0509 Pathfinder**
- **P-0536 Knowledge Pack**
- **P-0011 Crate Health**

**What those crates should provide other people:**
- one teachable starter set,
- one explanation of why obvious alternatives lost,
- one short cited knowledge pack that matches what docs.rs and official docs can actually support,
- one maintenance/support posture summary that is more honest than popularity.

### 2. Backend and async service teams
**Why it matters:** async/server work is a major flagship and still a real pain area.

**Top missing lanes:**
- **P-0538 Concurrency Contract**
- **P-0532 Async Runtime Assurance**
- **P-0509 Pathfinder**
- **P-0486 Debuggability Support**

**What those crates should provide other people:**
- portable semantics bundles for channels/tasks/runtime assumptions,
- deployment-topology and capability-route truth,
- starter-set choice under runtime constraints,
- and clear debugging posture for async stacks, tasks, and post-mortem support.

### 3. GUI / game / creative-app loops
**Why it matters:** fast iteration, state handoff, hot-update ceilings, and debugging all matter here.

**Top missing lanes:**
- **P-0537 Compile Iteration Feedback**
- **P-0486 Debuggability Support**
- **P-0509 Pathfinder**

**What those crates should provide other people:**
- edit-to-feedback receipts,
- coverage / activation / stale-code honesty,
- debugger/session/visualizer capability truth,
- and lane-aware stack choices that separate teaching defaults from shipping defaults.

### 4. Embedded / edge / device stacks
**Why it matters:** these teams care about `no_std`, toolchains, target support, build-std, and low-level dependency control.

**Top missing lanes:**
- **P-0484 Toolchain & Target Support**
- **P-0535 Dependency Lifecycle Transition**
- **P-0509 Pathfinder**
- **P-0532 Async Runtime Assurance** when async is present

**What those crates should provide other people:**
- target and exercised-environment receipts,
- build-std / allocator / linker / prerequisite truth,
- replace-or-pin plans for fragile dependencies,
- and starter-set decisions that respect `no_std`, MSRV, and device constraints.

### 5. Kernel / low-level / Rust-for-Linux-adjacent work
**Why it matters:** toolchain support, specific language capability boundaries, and long-lived support windows matter more than generic crate selection.

**Top missing lanes:**
- **P-0484 Toolchain & Target Support**
- **P-0535 Dependency Lifecycle Transition**
- **P-0431 Public Dependency Boundary**
- **P-0427 Rust Specification Witness** in the more proof-heavy cases

**What those crates should provide other people:**
- exact support-class and prerequisite declarations,
- dependency placement and public-boundary truth,
- stable replacement/off-ramp plans,
- and specification/evidence artifacts where long-lived or audited support matters.

### 6. Safety-critical / regulated delivery
**Why it matters:** official 2026 work makes this explicit.

**Top missing lanes:**
- **P-0433 MC/DC Coverage Workbench**
- **P-0427 Rust Specification Witness**
- **P-0535 Dependency Lifecycle Transition**
- **P-0484 Toolchain & Target Support**
- **P-0011 Crate Health**

**What those crates should provide other people:**
- evidence bundles,
- qualification- and audit-friendly receipts,
- dependency and toolchain support truth,
- continuity/maintenance posture,
- and conformance/lint/coverage artifacts that survive later review.

### 7. Wasm browser / component / plugin ecosystems
**Why it matters:** Wasm Components are now a flagship, and many support claims are target- and packaging-sensitive.

**Top missing lanes:**
- **P-0484 Toolchain & Target Support**
- **P-0509 Pathfinder**
- **P-0536 Crate Knowledge Pack**
- sector-specific **Wasm plugin / component workbenches** only when they add real evidence seams

**What those crates should provide other people:**
- host-vs-target support receipts,
- starter-set decisions that distinguish browser/client/component/plugin cases,
- and target-aware knowledge packs that do not confuse docs visibility with runnable support.

### 8. C++ / FFI / mixed-language systems
**Why it matters:** official goals keep C++ interop alive, and these teams need more than one thin binding crate.

**Top missing lanes:**
- **P-0484 Toolchain & Target Support**
- **P-0535 Dependency Lifecycle Transition**
- **P-0509 Pathfinder**
- interop workbenches only where dialect/profile evidence is central

**What those crates should provide other people:**
- ABI/toolchain/support truth,
- migration and source-parity receipts,
- lane-aware starter choices for wrappers/generators/interop stacks,
- and evidence kits where profile or loss accounting matters.

### 9. Data / numerics / GPU / scientific pipelines
**Why it matters:** format/layout/device truth and mixed-language/runtime packaging are the recurring pain, not one giant “science supercrate”.

**Top missing lanes:**
- **P-0509 Pathfinder**
- **P-0535 Dependency Lifecycle Transition**
- **P-0484 Toolchain & Target Support**
- sector workbenches only where format/layout/conformance truth is the actual seam

**What those crates should provide other people:**
- starter-set choices for data pipelines or numerics stacks,
- device/toolchain/layout constraints,
- off-ramp plans for risky dependencies,
- and conformance or loss-aware evidence when crossing formats or ecosystems.

### 10. Build / test / platform / internal tooling authors
**Why it matters:** many ecosystem pains are really operational tooling pains.

**Top missing lanes:**
- **P-0537 Compile Iteration Feedback**
- **P-0536 Crate Knowledge Pack**
- **P-0486 Debuggability Support**
- **P-0431 Public Dependency Boundary**
- **P-0125 Cargo SBOM Precursor Workbench**

**What those crates should provide other people:**
- build/test/iteration receipts,
- machine-usable crate facts,
- debuggability support bundles for shipped binaries,
- public dependency and SBOM-adjacent artifacts for internal platforms.

## Promotion rule that follows from the matrix

Before adding a new sector proposal, explicitly ask:

1. would this use case be better served by deepening **P-0509**, **P-0484**, **P-0486**, **P-0535**, **P-0536**, **P-0537**, **P-0538**, **P-0532**, **P-0011**, or **P-0431**?
2. if not, what exact evidence seam escapes them?
3. what portable artifact would the new lane export that these lanes cannot?

If those answers stay weak, **deepen instead of append**.

## Sources
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h1/async.html
- https://rust-lang.github.io/rust-project-goals/2025h1/seamless-rust-cpp.html
- https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
- https://rust-lang.github.io/rust-project-goals/2025h2/build-std.html
- https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- https://rust-lang.github.io/rust-project-goals/2025h2/reference-expansion.html
- https://rust-lang.github.io/rust-project-goals/2025h2/FLS-up-to-date-capabilities.html
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://docs.rs/about/rustdoc-json
- https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
