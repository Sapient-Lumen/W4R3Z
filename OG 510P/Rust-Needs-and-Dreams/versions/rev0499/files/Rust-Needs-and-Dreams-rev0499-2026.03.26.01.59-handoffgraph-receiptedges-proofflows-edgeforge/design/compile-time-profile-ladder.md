# Design: Compile-Time Profile Ladder (`ct-profile-catalog/v0`, `ct-profile-fit-report/v0`)

## Goal
Give the broader **Compile-Time Surface Stack** a practical adoption ladder.

The archive now has:
- an authority substrate in [`design/compile-time-capabilities-kit.md`](./compile-time-capabilities-kit.md),
- a structured-replacement lane in [`design/build-extension-kit.md`](./build-extension-kit.md),
- a workflow/migration lane in [`design/macro-workflow-kit.md`](./macro-workflow-kit.md),
- and a share/repro lane in [`design/scriptkit.md`](./scriptkit.md).

What it still needed was a concrete answer to a harder question:

**How does a real workspace move from ambient compile-time execution toward something more governable without pretending every crate can jump directly to “fully sandboxed and declarative”?**

This file defines the missing transition layer: a small set of named profiles, plus explicit graduation criteria and reason-coded fit reports.

## Why this needs to exist
Current official Rust signals make the need for a profile ladder unusually clear:

- Cargo’s sandboxed-build-scripts goal is explicitly about per-crate permissions, shared configuration across build scripts and proc-macros, and a future where the sandboxed path can become the default.  
  https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
- The Rust Reference says proc-macros have the same security concerns as build scripts.  
  https://doc.rust-lang.org/reference/procedural-macros.html
- Cargo’s 1.94 development-cycle update says build scripts and proc-macros remain special pain points for target-dir locking and concurrent workflows, and it also adds `cargo report rebuild` to explain why rebuilds happen.  
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Macro-improvements work is explicitly trying to reduce proc-macro demand, with faster builds and smaller dependency chains as named benefits.  
  https://rust-lang.github.io/rust-project-goals/2025h1/macro-improvements.html
- Reflection-and-comptime plus const-traits/const-fn work show a second kind of pressure: the ecosystem wants to move some work into more language-shaped compile-time lanes rather than keep everything in host-native proc-macros or `build.rs`.  
  https://rust-lang.github.io/rust-project-goals/2025h2/reflection-and-comptime.html  
  https://rust-lang.github.io/rust-project-goals/2025h1/const-trait.html
- `cargo-script` remains a 2026 flagship, which means “tiny compile-time-adjacent packages” are also becoming more first-class and need a clearer place in the overall picture.  
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html

So the missing contribution is not merely a better sandbox or a better macro debugger. It is a **governance ladder** that lets teams say:
- where a unit sits today,
- which profile it is trying to reach,
- what blocks graduation,
- and which neighboring kit should help it move.

## New artifacts

### `ct-profile-catalog/v0`
A portable catalog of named compile-time profiles.

It records:
- profile identifier and version
- intended unit kinds (`build-script`, `proc-macro`, `links-override`, `declared-no-run`, `script`)
- allowed execution lanes
- required capability declarations
- required observation coverage
- required input-surface quality
- determinism / cacheability expectations
- permitted waiver classes
- expected downstream consumers (policy, cache, release, repro, trust)

Design rule: this is **not** a verdict about one workspace. It is the named contract a workspace can target.

### `ct-profile-fit-report/v0`
A report comparing one subject against one or more named profiles.

It records:
- subject identity + execution lane
- current profile fit (`meets`, `meets-with-waivers`, `does-not-meet`, `unknown`)
- blocker list with stable reason codes
- evidence used (declarations, observations, determinism reports, replacement reports, migration hints)
- recommended next moves
- whether the subject should move by:
  - narrowing authority,
  - improving declarations,
  - replacing imperative build steps,
  - reducing proc-macro reliance,
  - or moving compile-time logic into language-first lanes

Design rule: fit reports are **transition evidence**, not policy verdicts. Policy may consume them, but must not be collapsed into them.

## The ladder

### Profile A — `ambient-observed`
The minimum serious profile.

Use when:
- arbitrary native compile-time execution still exists,
- but the workspace is willing to inventory it and observe it honestly.

Requires:
- `ct-unit-manifest/v0`
- `ct-execution-lane/v0`
- best-effort `ct-observation-report/v0`

Allows:
- broad authority
- incomplete declarations
- unknown determinism

Forbids:
- pretending the workspace is “safe” or “portable”

Strategic role:
- this is the entry point for legacy codebases and large adoption stories.

### Profile B — `declared-native`
The first reviewable profile.

Use when:
- compile-time units still run natively,
- but declared capabilities and input surfaces are explicit enough to diff.

Requires:
- `ct-capability-profile/v0`
- `ct-input-surface/v0`
- declaration-vs-observation parity checks
- reason-coded waivers for undeclared authority

Allows:
- native execution
- bounded waivers
- some nondeterminism

Strategic role:
- this is the minimum profile that policy, cache, and trust tools can really build on.

### Profile C — `narrow-native`
The first governance-worthy native profile.

Use when:
- native compile-time execution remains necessary,
- but network/process/env/filesystem scopes are intentionally narrowed.

Requires:
- explicit narrow scopes
- blocker reasons for any broad accesses
- deterministic-input work that is good enough to matter for rebuild and cache reasoning

Typical examples:
- many `-sys` crates
- proc-macros that still need host-native execution but can be constrained

Strategic role:
- this is the highest realistic medium-term profile for a lot of today’s ecosystem.

### Profile D — `portable-sandbox`
The first strongly reusable profile.

Use when:
- execution is isolated enough that portability, determinism, and cacheability claims become materially stronger.

Requires:
- backend/runtime identity
- explicit blind-spot declarations
- observation coverage good enough to justify cache / repro consumers
- no hidden broad authority

Possible lanes:
- sandboxed build-script backend
- wasm proc-macro lane
- equivalent future isolated runtime

Strategic role:
- this is the profile that most directly composes with future shared-cache, remote-execution, and stronger policy stories.

### Profile E — `declared-no-run`
The ideal replacement profile for many current `build.rs` cases.

Use when:
- compile-time behavior is satisfied by `links` metadata overrides, declarative build extensions, or other no-run structured lanes.

Requires:
- no arbitrary unit execution for the covered behavior
- explicit generated-output or metadata truth
- diffable replacement artifacts

Strategic role:
- this is where Build Extension Kit and native metadata override work should aim.

### Profile F — `language-first`
The ideal migration profile for some proc-macro/build-script use cases.

Use when:
- compile-time work moved into declarative macros, const contexts, reflection/comptime, or other language-shaped lanes.

Requires:
- explicit record of the migration target
- compatibility / channel truth
- honest note about what remains experimental

Strategic role:
- this is the future-facing profile that prevents the archive from freezing current proc-macro/build-script patterns as the eternal design center.

## How the profiles compose with existing kits
- **Compile-Time Capabilities Kit** owns the profile catalog and fit reports because it owns lane, capability, observation, and determinism truth.
- **Build Extension Kit** is the main path from `ambient-observed` / `declared-native` toward `declared-no-run`.
- **Macro Workflow Kit** is the main path from macro-heavy native lanes toward `language-first` candidates.
- **ScriptKit** gives small packages and issue repros a lightweight lane that can still declare which profile they satisfy.
- **Policy Kit** may require a minimum profile, but should not silently redefine profile semantics.
- **Build Cache Kit** and **Change Impact Kit** consume profile-fit outputs because they care whether stronger reuse claims are warranted.

## Minimal reference UX
Extend `cargo ct` with:
- `cargo ct profiles`
  - show the built-in `ct-profile-catalog/v0`
- `cargo ct fit --profile <name>`
  - emit `ct-profile-fit-report/v0`
- `cargo ct graduate --profile <name>`
  - explain blockers and the shortest path to reach that profile

The goal is not a giant policy engine.
The goal is to make “what profile are we at, and why not higher?” answerable in a stable way.

## What this changes strategically
Without named profiles, the compile-time frontier tends to collapse into false binaries:
- safe vs unsafe
- sandboxed vs not
- macro vs no macro
- reproducible vs irredeemable

That is too coarse for real ecosystems.

The ladder above gives the archive a way to say:
- some code should be observed first,
- some code can be narrowed without replacement,
- some code should be replaced rather than sandboxed forever,
- and some code should migrate into language-shaped compile-time lanes instead of staying in host-native escape hatches.

That is a much stronger answer to what an “epic” Rust contribution would look like in practice.
