# Gap: Rust reflection now needs a transition boundary, not another local winner

## Summary
Rust's reflection story is no longer a niche metaprogramming side quest.
It is now being pulled forward from three directions at once:
- the 2026 flagship slate explicitly includes **prototype reflection**;
- the 2025H2 reflection-and-comptime goal proposes a compile-time reflection path and directly says proc-macro derives have historically been hard to debug and bootstrap;
- and real userland lanes already exist, but they are **semantically different** rather than different implementations of one settled idea.

That last point matters.
Rust already has:
- **runtime reflection + registries** (`bevy_reflect`),
- **associated-const shape metadata** (`facet`),
- **object-safe visit-only inspection** (`valuable` and `tracing`'s `valuable` support),
- **schema / format tracing** (`serde_reflection`),
- and large derive-heavy ecosystems that still pay proc-macro cost because there is no better portable story yet.

What Rust still lacks is the **portable transition boundary above those lanes**.
Today maintainers can usually answer fragments such as:
- “this crate has runtime metadata and a registry,”
- “this lane only supports visit-only inspection,”
- “this library emits shape metadata through an associated const,”
- “this workflow still pays derive/proc-macro cost,”
- or “future compile-time reflection might help later.”

What they still struggle to answer cleanly is:
- what exact reflection lane a subject uses today,
- what proc-macro, registry, and orphan-rule workaround burden it still pays,
- what kind of introspection a downstream consumer can actually rely on,
- which adapters depend on mutation versus visit-only inspection versus schema tracing,
- what compile-time / const posture is merely aspirational versus real,
- and what migration a maintainer may honestly plan now versus defer.

That missing layer is not another runtime reflection crate, not another derive helper, not another registry macro, and not a premature universal reflect trait.
It is a **transition boundary above macro burden, runtime reflection, object-safe inspection, schema/shape lanes, and future compile-time reflection**.

## Why now
Current Rust signals make this much more concrete than it was even one revision ago:
- Rust’s 2026 flagship goals explicitly include **prototype reflection** inside **Constify all the things**, which makes reflection an active language-adjacent frontier instead of a purely userland curiosity;
- the reflection-and-comptime goal proposes a `const fn`-based reflection path, says proc-macro derives have historically been hard to debug and bootstrap, and explicitly says crates like `bevy_reflect` and `facet` would still exist afterwards with different goals;
- the macro-improvements goal says reducing proc-macro demand can make many projects build substantially faster and reduce dependency supply chains;
- the 2025 compiler-performance survey says stabilizing language features could remove some proc macros or build scripts;
- the August 2025 program-management update says Bevy and gamedev users raised reflection as a major pain point, explains that `derive(Reflect)`-style workflows are difficult to write and debug, and calls out orphan-rule friction for standard-library and foreign types;
- `bevy_reflect` remains a real runtime reflection lane with dynamic interaction and a `TypeRegistry` / `TypeRegistration` model;
- `facet` explicitly exposes a `SHAPE` associated const with layout/field/doc/attribute information;
- `valuable` explicitly scopes itself to object-safe value inspection, and `tracing`'s `valuable` support remains experimental and visit-oriented rather than a universal reflection substrate;
- `serde_reflection` explicitly traces serialization structure to derive format descriptions and says those descriptions can be stored under version control to prevent unintended format drift.

Sources:
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h2/reflection-and-comptime.html
- https://rust-lang.github.io/rust-project-goals/2025h1/macro-improvements.html
- https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- https://blog.rust-lang.org/inside-rust/2025/09/11/program-management-update-2025-08/
- https://docs.rs/bevy_reflect/latest/bevy_reflect/
- https://docs.rs/facet/latest/facet/
- https://docs.rs/valuable/latest/valuable/
- https://docs.rs/tracing/latest/tracing/field/index.html
- https://docs.rs/serde-reflection/latest/serde_reflection/

## The current seam is awkward
Today, reflection-transition truth gets improvised from incompatible ingredients:
- proc-macro inventory and folklore about build/debug burden,
- runtime reflection crates and registry conventions,
- inspect-only observability adapters,
- schema/shape extraction lanes,
- compile-time/const experiments,
- and human migration notes scattered across issues, talks, and framework docs.

That usually leads to six failures:
1. runtime reflection, inspect-only visitation, and schema tracing get flattened into one fake “reflection support” claim;
2. proc-macro cost disappears from the story right when reflection is discussed as a future replacement;
3. orphan-rule and foreign-type friction disappear behind “just derive it” folklore;
4. registry/discovery behavior gets hidden behind “auto registration” or framework magic;
5. compile-time reflection aspirations overclaim before real consumer lanes are compared;
6. each ecosystem (observability, editors, config, codegen, engines) invents its own migration language and cannot compare notes cleanly.

## Why this matters
This gap matters to:
1. **framework and engine authors** — because runtime registries, mutation semantics, and adapter expectations need honest boundaries;
2. **observability and diagnostics tooling** — because inspect-only lanes should not be mistaken for mutation, reconstruction, or schema guarantees;
3. **schema/codegen/config consumers** — because associated-const shape, serialization traces, and future core reflection are not interchangeable;
4. **maintainers of derive-heavy crates** — because migration planning needs to preserve today’s macro burden and tomorrow’s missing pieces;
5. **language and toolchain work** — because prototype reflection will be evaluated against real ecosystem lanes, not on a blank slate.

## What good looks like
A worthy contribution here is a thin composition layer above **Macro Workflow Kit**, **Reflection Surface Kit**, and **Const Surface Kit**.

It should provide at least:
- `reflection-transition-brief/v0` — why this comparison or migration subject exists and who it serves;
- `reflection-transition-subject/v0` — the exact crate/workspace/lane/consumer combination under review;
- `reflection-transition-pack/v0` — imported macro/reflection/const evidence with explicit caveats;
- `reflection-transition-diff/v0` — what changed between two reflection-transition points;
- `reflection-transition-handoff/v0` — bounded summaries for observability, editor/config, schema/codegen, maintenance, and assistant consumers.

The winning version should keep these distinctions visible:
- **current proc-macro burden** versus **current reflection semantics**,
- **runtime reflection** versus **visit-only inspection**,
- **schema/shape extraction** versus **general reflection**,
- **registry/discovery behavior** versus **type-shape stability**,
- **future compile-time reflection posture** versus **present migration readiness**,
- and **watch/wait outcomes** versus **adoption-ready lanes**.

The bar is not a better crate comparison page.
The bar is a durable, explainable, importable **reflection transition boundary** for ideal Rust as the language and ecosystem evolve.
