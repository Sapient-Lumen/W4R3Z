# Design: Compile-Time Surface Pilot Program (`cargo ct pilot`, `ct-surface-pack/v0`)

## Goal
Make the archive's compile-time work executable by treating it as a **stack**, not one isolated kit:
- [`design/compile-time-capabilities-kit.md`](./compile-time-capabilities-kit.md) for authority, observation, determinism, and policy
- [`design/build-extension-kit.md`](./build-extension-kit.md) for structured replacement of common imperative `build.rs` patterns
- [`design/macro-workflow-kit.md`](./macro-workflow-kit.md) for inventory, cost/debug artifacts, and migration planning
- [`design/scriptkit.md`](./scriptkit.md) as an adjacent share/repro lane for tiny Rust programs and bug reports

A worthy contribution here is not merely a sandbox demo, a nicer macro debugger, or a one-off cargo-script wrapper. It is a ranked rollout plan that shows how Rust can move compile-time work from **ambient execution and folklore** toward **reviewable authority, structured replacement, explicit profile ladders, and migration paths**.

## Why this needs its own design layer
The archive already has strong pieces, but they still risk being treated as separate projects:
- Compile-Time Capabilities can become “the sandbox idea”.
- Build Extension can become “metabuild, but tidier”.
- Macro Workflow can become “cargo-expand plus reports”.
- ScriptKit can become “cargo-script adoption glue”.

That separation misses the real opportunity. Current Rust signals point to one shared frontier:
1. **Compile-time execution authority is under pressure.** Build scripts and proc-macros still execute arbitrary host code; Cargo's sandboxed-build-script work is explicitly exploring per-crate permissions and a common configuration surface.  
   https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
2. **The ecosystem wants fewer proc-macros where possible.** The accepted macro-improvements goal explicitly aims to make `macro_rules!` capable enough to replace many proc-macro use cases, with faster builds and smaller supply chains as stated benefits.  
   https://rust-lang.github.io/rust-project-goals/2025h1/macro-improvements.html
3. **Build performance work needs better compile-time truth.** The compiler-performance survey says developers want to understand why builds are slow, and proc-macros/build scripts are part of that story.  
   https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
4. **Caching and reproducibility depend on input truth.** The user-wide-cache goal says sandboxing can provide more precise `build.rs` / proc-macro inputs and help verify idempotence.  
   https://rust-lang.github.io/rust-project-goals/2024h2/user-wide-cache.html
5. **New first-class compile-time lanes are appearing.** Cargo-script remains a 2026 flagship and had concrete implementation progress in late 2025; reflection-and-comptime also had concrete compiler progress and ongoing blocker work in the December 2025 goal update.  
   https://rust-lang.github.io/rust-project-goals/2026/flagships.html  
   https://blog.rust-lang.org/2026/01/05/project-goals-2025-december-update/

So the right “epic” contribution is broader than one tool: **a compile-time surface stack** with explicit authority lanes, named governance profiles, structured replacement lanes, workflow artifacts, and migration evidence.

## Working thesis
A serious contribution here should make it possible to answer all of these cleanly:
- What compile-time code executed, in which lane, with what authority?
- Which common `build.rs` patterns could have been expressed declaratively instead?
- Which proc-macros are expensive, hard to debug, or ripe for migration?
- Which tiny repros or scripts can be packaged and replayed without repo scaffolding?
- Which compile-time behaviors are temporary transition debt versus long-term supported lanes?

## The stack
### 1) Compile-Time Capabilities Kit
Owns:
- unit inventory
- execution lanes
- declared capabilities
- observed behavior
- invalidation / input truth
- determinism / cacheability findings
- waivers and policy decisions

This is the authority substrate.

### 2) Build Extension Kit
Owns:
- declarative build-step intent
- parameter passing
- generated-output declarations
- Cargo-mediated final-artifact uplift
- honest fallback-to-imperative reporting

This is the structured replacement lane.

### 3) Macro Workflow Kit
Owns:
- proc-macro inventory
- expansion/debug/cost artifacts
- hotspot and dependency-weight visibility
- migration hints toward declarative or reflection/comptime alternatives

This is the workflow and transition-planning layer.

### 4) ScriptKit (adjacent lane)
Owns:
- shareable single-file packages
- lock/caching conventions
- replayable script artifacts
- a low-friction reproduction path for issues, docs, and utilities

This is not the authority substrate, but it is an important proving ground for portable compile-time packaging and issue-attachable evidence.

## Governance profiles
The pilot program should now be read together with [`design/compile-time-profile-ladder.md`](./compile-time-profile-ladder.md).

That ladder keeps the archive honest about what counts as progress:
- **`ambient-observed`** for legacy / adoption-first workspaces that can at least inventory and observe compile-time units;
- **`declared-native`** for workspaces that have explicit capabilities and input surfaces;
- **`narrow-native`** for workspaces that still need native execution but can justify tighter scopes;
- **`portable-sandbox`** for isolated lanes with materially stronger cache / repro / policy posture;
- **`declared-no-run`** for structured replacements such as `links` overrides or declarative build extensions;
- **`language-first`** for cases moved into declarative macros, const contexts, reflection/comptime, or equivalent future lanes.

The point is not to force every unit to the same destination. The point is to make the destination explicit and diffable.

## Ranked pilot program
### Pilot 1 — Strict build-script authority lane
Use a workspace with real `build.rs` activity and explicit CI policy pressure.

Must prove:
- `ct-unit-manifest/v0`, `ct-capability-profile/v0`, and `ct-observation-report/v0` are enough to review what ran;
- `ct-profile-fit-report/v0` can explain why the subject is only `ambient-observed` or `declared-native`, and what blocks `narrow-native`;
- network/process/env/file scopes can be made explicit without pretending all builds are pure;
- determinism and input-surface findings are useful to cache/repro tools.

Why first:
- it exercises the hardest trust boundary directly;
- it composes with policy, trust, cache, and reproducibility work;
- it gives the stack a serious “review this before merge” posture.

### Pilot 2 — Proc-macro-heavy workflow lane
Use a workspace with several derives/attributes and visible compile-time cost or debugging pain.

Must prove:
- macro inventory, expansion, cost, and debug artifacts remain distinct from capability/policy artifacts;
- proc-macro lanes can be reviewed for both authority and workflow pain;
- `ct-profile-fit-report/v0` can show whether a macro-heavy workspace should aim for `narrow-native`, `portable-sandbox`, or `language-first` instead of one fake end state;
- migration hints can point toward declarative-macro or reflection/comptime futures without claiming automatic conversion.

Why second:
- it connects performance, debuggability, and supply-chain size to the same frontier;
- it is the clearest place to show why macro workflow must not be absorbed into the sandbox story.

### Pilot 3 — Structured replacement lane (`links` override / metabuild / delegated steps)
Use one or more crates where imperative behavior can be reduced or replaced.

Must prove:
- declarative replacements are represented as first-class success, not as missing functionality;
- `build-ext-manifest/v0` and `build-ext-report/v0` stay separate from compile-time authority facts;
- `declared-no-run` becomes a named success profile, not just “the build script happened not to run this time”;
- “fallback to imperative” is visible and reason-coded.

Why third:
- it turns the archive from “review arbitrary execution better” into “reduce arbitrary execution where possible”.

### Pilot 4 — Shareable repro / script lane
Use a small single-file repro, educational example, or internal utility built on cargo-script.

Must prove:
- one-file packages can still carry lock/toolchain/provenance truth;
- issue-attachable packs are more legible than “clone this repo and run these steps” folklore;
- when a script pulls proc-macros or build scripts, its pack can point back to the same compile-time surface artifacts;
- small-program lanes can still declare which compile-time profile they satisfy instead of living outside the governance story.

Why fourth:
- it keeps the stack honest about small-program ergonomics and bug-report reproducibility;
- it gives the archive one concrete answer to “how do we make ideal Rust feel lighter without giving up evidence?”

### Pilot 5 — Future-facing transition lane
Use an experimental or design-only lane that compares today's proc-macro/build-script posture with a possible future lane (declarative macros, reflection/comptime, or a more isolated proc-macro execution lane).

Must prove:
- transition hints are recorded explicitly rather than implied;
- the archive can talk about future compile-time lanes without pretending they are already stable reality;
- current and future lanes remain comparable enough to aid migration planning;
- `language-first` stays a real migration target rather than a vague promise.

Why fifth:
- it prevents the stack from freezing current proc-macro/build-script patterns as the eternal end state.

## Shared schema discipline
Every pilot must keep these truths separate:
1. **authority** vs **workflow ergonomics**
2. **ambient execution** vs **structured replacement**
3. **declared** vs **observed** behavior
4. **current supported lane** vs **future migration target**
5. **repro/share artifact** vs **policy verdict**
6. **host-only execution facts** vs **target-facing package claims**

## Overlap boundaries
- **Policy Kit** consumes compile-time authority and waiver outputs; it does not define them.
- **Build Cache Kit** consumes determinism/input truth; it does not define compile-time units.
- **Change Impact Kit** uses compile-time invalidation facts; it does not replace them.
- **Native Dependency Kit** models provider selection and link plans; it does not own compile-time permissions.
- **Semantic Context Kit** may consume macro/build artifacts for richer tooling, but it should not become the authority source of truth.
- **Compatibility Claims Stack** stays about support/acceptance truth, not compile-time execution authority.

## What not to do
Do not turn this into:
- one mega-format that hides authority, workflow, and transition differences;
- a claim that all compile-time execution can be sandboxed immediately;
- a generic “safe build” badge;
- or an excuse to duplicate Cargo and compiler-team work.

The job is narrower and more powerful:
**make compile-time work legible enough that Rust can progressively replace, isolate, and govern it.**
