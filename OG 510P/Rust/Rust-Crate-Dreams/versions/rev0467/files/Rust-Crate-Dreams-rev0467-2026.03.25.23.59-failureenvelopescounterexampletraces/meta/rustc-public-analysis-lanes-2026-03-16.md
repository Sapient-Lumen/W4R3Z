# rustc_public tooling lanes — 2026-03-16

This pass promoted **P-0429 rustc_public Analysis Workbench Kit** from a good idea to a sharper lane with fixtures, compatibility artifacts, and explicit boundaries.

## Main judgment

The official Rust compiler work around `rustc_public` is now concrete enough that the missing crate is *not* another plea for public compiler APIs.

The stronger missing layer is:

- **compatibility locks**,
- **tool capability matrices**,
- **minimized analyzer fixtures**,
- and **diffable evidence bundles** above `rustc_public`.

That judgment is stronger after:

- the accepted StableMIR / `rustc_public` project goal,
- the 2025 GSoC report describing the `rustc_public` / `rustc_public_bridge` refactor and compatibility infrastructure,
- the publishing MCP for a SemVer-compliant crates.io release,
- and the current nightly docs explicitly separating SemVer-oriented APIs from `rustc_internal` / `unstable` surfaces.

## The lane this repo now wants to protect

### P-0429 — workbench above `rustc_public`

This lane owns:

1. **one compatibility lock** for compiler range, `rustc_public` range, bridge posture, edition, and feature assumptions,
2. **one minimized fixture format** for analysis cases,
3. **one capability matrix** for what a tool actually supports,
4. **one analysis receipt** that classifies unsupported constructs and semver-exempt surface usage,
5. and **one diff format** for comparing tool or compiler results over time.

That is the reviewable “boring crate” layer still missing from the ecosystem.

## What this lane does **not** own

### 1. It is not the `rustc_public` publication / release-engineering lane

The compiler project itself owns:

- how `rustc_public` is versioned,
- how it is published,
- how it is split from `rustc_public_bridge`,
- and how dual maintenance works.

The archive should not rephrase that as a new crate opportunity unless the missing value is clearly outside compiler-team ownership.

### 2. It is not a `rustc_private` compatibility shim

A future pass should not let P-0429 drift into “pretend old compiler-internal tools will just keep working.”

The sharper value is:

- migration evidence,
- compatibility matrices,
- fixture portability,
- and unstable-surface detection,

not a fake stable façade over compiler internals.

### 3. It is not the formal semantics / counterexample lane

The archive already has **P-0456 Formality Counterexample Bridge Kit**.

That lane owns:

- rustc ↔ formality ↔ MiniRust divergence witnesses,
- minimized semantic counterexamples,
- and model-validation artifacts.

P-0429 instead owns the **tool adoption and compatibility substrate** above `rustc_public`.

### 4. It is not the Rust specification witness lane

The archive already has **P-0427 Rust Specification Witness Kit**.

That lane owns clause-linked executable examples and qualification-oriented spec drift witnesses.
P-0429 owns tool-facing compiler-interface locks and analyzer evidence.

### 5. It is not a future syntax / macro expansion catchall

The roadmap has hinted that there may eventually be a worthwhile public syntax / macro-expansion evidence lane.

If that lane appears, it must stay distinct from:

- MIR/public-IR compatibility,
- analyzer capability matrices,
- and semver-exempt bridge usage.

Do not let a future pass flatten parser / expansion evidence into “public IR”.

## Practical rule for future revisions

If a future proposal touches `rustc_public`, ask first whether the missing value is:

1. **publication / versioning of the official compiler crate**,
2. **tool compatibility locks + fixtures + evidence bundles**,
3. **formal semantics / counterexample exchange**,
4. **specification witnesses**,
5. or a future **syntax / macro expansion evidence** lane.

Only item **2** belongs to **P-0429**.

## Sources

- StableMIR / `rustc_public` goal: https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
- GSoC 2025 results: https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Compiler-team MCP: https://github.com/rust-lang/compiler-team/issues/949
- project-stable-mir / Rustc Librarification project: https://github.com/rust-lang/project-stable-mir
- nightly `rustc_public` docs: https://doc.rust-lang.org/nightly/nightly-rustc/rustc_public/index.html
