# Gap: compile-time guidance and developer-facing tooling extensions

## What is missing
Rust increasingly has the **pieces** for crate-authored compile-time guidance and tooling extensions, but it still lacks a portable, reviewable way to describe and validate them as ecosystem infrastructure.

Today there is no standard way to describe, review, and ship:
- which compile-time diagnostics a crate or tool intentionally emits,
- which lint ids, categories, default severities, standards mappings, and fixability claims it defines,
- which proc-macro or build-time DSL errors are part of the supported user surface,
- which pipeline hooks a crate relies on (proc-macros, build scripts, delegated build steps, StableMIR-based analyzers, Clippy-style lint packs, code generation helpers),
- which capabilities, determinism assumptions, caching limits, or host requirements those hooks need,
- which compile-fail / UI examples demonstrate the intended guidance quality,
- and which "extensibility" proposals are really just ad hoc one-offs that cannot be reviewed or composed outside one project.

Rust's own vision work now makes the missing seam explicit: it recommends **doubling down on extensibility**, including better diagnostics and guidance from crates plus ways for crates to integrate at more stages of the compilation workflow.
That is stronger than “tooling could improve.”
It says the ecosystem needs a **shared contract for supportive extensions**.

Sources:
- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://doc.rust-lang.org/reference/attributes/diagnostics.html
- https://doc.rust-lang.org/reference/procedural-macros.html

## The current seam is fragmented
Rust already has meaningful evidence that this area matters:
- the diagnostic attribute namespace and `#[diagnostic::on_unimplemented]` / `#[diagnostic::do_not_recommend]` give library authors a stable way to influence compiler messages,
- Clippy and the 2026 safety-critical flagship make it clear that domain-specific lint lanes are strategic, not incidental,
- StableMIR is being published to crates.io so tool builders can analyze compiled Rust without depending directly on compiler internals,
- Cargo-side work on build-script delegation and multiple build scripts shows pressure to make build-time extension points more structured,
- and `trybuild` exists because proc-macro and compile-time diagnostics are already important enough to need snapshot-style UI testing.

Those are strong ingredients.
What Rust still lacks is the **artifact family that says what a crate/tool extends, what guidance it promises, what hooks it uses, and what was actually checked**.

Without that, compile-time UX still degenerates into one of four bad outcomes:
1. diagnostics live inside bespoke macros or lints with no portable catalog or policy surface;
2. custom lint packs and compile-time DSLs become effectively undocumented mini-compilers;
3. build-time integration grows in power without reviewable capability/determinism truth;
4. teams test guidance informally, but months later no one can reconstruct which errors, notes, fixes, or examples were meant to be stable.

Sources:
- https://doc.rust-lang.org/reference/attributes/diagnostics.html
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
- https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- https://docs.rs/trybuild

## Why this matters
This gap matters because some of Rust's biggest ecosystem wins come from **developer-facing supportiveness**, not just runtime speed or type-system power.

A good compile-guidance layer would help with:
1. **crate-authored supportiveness** — libraries and macro DSLs can publish stable diagnostic identities, help text, examples, and non-goals instead of treating compiler output as accidental;
2. **reviewable lint ecosystems** — safety, style, policy, and domain-specific lint packs can be compared and governed without flattening them into one universal severity score;
3. **extensibility honesty** — teams can see which hooks touch parsing, expansion, build steps, MIR analysis, or generated code and what those hooks assume about the host or cacheability;
4. **better editor/CI integration** — rust-analyzer, CI, and policy tooling can consume declared guidance and hook metadata instead of reverse-engineering custom workflows;
5. **safer growth of advanced domains** — safety-critical, verification-heavy, and DSL-heavy stacks can standardize their compile-time guidance posture without each inventing a bespoke governance format;
6. **amnesia resistance** — compile-time user experience stops living only in failing test snapshots, issue threads, and maintainer memory.

The same vision work that recommends better crate diagnostics also says compilation-workflow extensibility matters for areas like interop, theorem proving, GPU work, and safety-critical systems.
That means the missing contribution is not merely a prettier lint runner.
It is a **portable boundary for supportive compile-time surfaces and extension hooks**.

Sources:
- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
- https://docs.rs/trybuild

## What “good” looks like
A worthy contribution here is **not** another monolithic compiler plugin platform, another lint engine that tries to replace Clippy, or a magical schema that claims to model every future Rust extension.

It is a shared compile-guidance boundary:
- one `guidance-surface/v0` describing the developer-facing compile/build surface a crate or tool owns,
- one `diagnostic-catalog/v0` describing compile-time diagnostics, notes, fix-it hints, links, and stability expectations,
- one `lint-catalog/v0` describing lint ids, groups, severities, standards mappings, and machine-applicability posture,
- one `pipeline-hook-profile/v0` describing which extension hooks are used and what capabilities/determinism/caching assumptions they carry,
- one `guidance-example-catalog/v0` describing compile-fail / UI examples and golden guidance cases,
- one `guidance-check-report/v0` recording what diagnostics, lints, examples, and hook checks actually ran,
- and one `guidance-pack/v0` bundle for CI, docs, IDEs, policy tools, and later archaeology.

That would let Rust treat compile-time guidance and developer-facing extensibility as **reviewable product surfaces** instead of scattered implementation details.

## Non-goals
This gap should not be used to:
- replace rustc, Clippy, rust-analyzer, or proc-macro internals,
- collapse runtime/application diagnostics into compile-time guidance,
- force every lint pack or macro DSL into one shared style guide,
- or bless one extension mechanism as the only legitimate path.

The job is smaller and more practical:
**make compile-time guidance and extension hooks legible, diffable, and reviewable across the ecosystem.**
