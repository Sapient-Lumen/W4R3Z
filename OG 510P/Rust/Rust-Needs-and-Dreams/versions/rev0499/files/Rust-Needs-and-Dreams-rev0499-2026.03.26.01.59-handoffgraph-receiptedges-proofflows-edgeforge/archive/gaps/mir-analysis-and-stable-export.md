# Gap: MIR analysis and stable export artifacts

## What is missing
Rust is finally crossing the threshold where compiler-aware tooling can plausibly build on a public-ish interface instead of living forever on `rustc_private`. But the ecosystem still lacks a **reviewable MIR analysis boundary** that sits between the compiler and downstream tools.

The official signals are now strong enough that this gap is no longer speculative:
- the accepted 2025H1 goal was to publish StableMIR crate(s) to crates.io so tool developers can analyze compiled crates and dependencies without depending directly on compiler internals;
- the project has since been reframed as **`rustc_public`**, explicitly to emphasize a SemVer-compliant public interface rather than a promise that every detail is eternally frozen;
- the current compiler-team MCP proposes publishing `rustc_public` v0.1 to crates.io with SemVer, multi-compiler-version support, and a split architecture between `rustc_public` and `rustc_public_bridge`;
- and the project page now frames `rustc_public` as a foundation for sophisticated external analyses.

Sources:
- https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
- https://rust-lang.github.io/project-stable-mir/
- https://github.com/rust-lang/compiler-team/issues/949

## The current seam is sharper than it used to be
The practical problem is no longer merely “there is no stable MIR”. The sharper problem is that multiple serious consumers are converging on a moving substrate without a shared artifact layer:
- nightly docs still describe `rustc_public` as a WIP public interface that is completely unstable and only *intended* to be published eventually;
- the `rustc_internal` module is explicitly out of SemVer scope and exists as a temporary bridge until `rustc_public`’s IR is complete;
- `stable-mir-json` is concrete proof that people want portable MIR, but its own architecture note says it is a **compiler driver** that currently uses both StableMIR and rustc internals;
- MIR itself is still an active semantics frontier, not a frozen substrate: the 2025H2 move-elimination goal explicitly requires changing MIR move semantics and then teaching Miri to check the new model.

Sources:
- https://doc.rust-lang.org/nightly/nightly-rustc/rustc_public/index.html
- https://doc.rust-lang.org/beta/nightly-rustc/rustc_public/rustc_internal/index.html
- https://hackmd.io/%40cds-amal/SkgYPwTOuWg
- https://rust-lang.github.io/rust-project-goals/2025h2/mir-move-elimination.html

## Why this matters
Without a shared export/report boundary, every sophisticated consumer still tends to fall into one of four bad shapes:
1. **Pin to rustc internals** and pay churn tax every toolchain cycle.
2. **Hide analysis inside a custom driver** and make the output hard to diff, cache, or reuse.
3. **Emit one-off JSON** that downstream tools cannot safely compare or combine.
4. **Overclaim comparability** even when compiler versions or MIR semantics have changed.

That blocks exactly the kinds of ecosystem contributions Rust says it wants more of:
- semver and public-API checking that needs precise cross-crate/type information,
- safety and formal-methods tooling that wants contracts or lower-level operational facts,
- compiler-aware CI artifacts that can be attached to issues and release gates,
- analysis tools that want to compose instead of each inventing their own driver/export stack.

The upstream signals are unusually direct here. The `cargo-semver-checks` roadmap says precise type-sensitive compatibility checking still needs compiler-backed truth and witness generation, while the contracts goal says the compiler should expose annotated contracts to external tools. Those are both symptoms of the same missing substrate: a **queryable, packable analysis layer** over compiler-derived facts.

Sources:
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- https://rust-lang.github.io/rust-project-goals/2025h1/std-contracts.html

## What “good” looks like
A worthy ecosystem contribution here is **not** “standardize all of MIR forever” and it is not “write one blessed analyzer”.

It is a thinner, more realistic target:
- one `mir-subject/v0` that says exactly what was analyzed;
- one `mir-capture-profile/v0` that records the capture lane, semantic epoch, and selection policy;
- one `mir-capability-profile/v0` that declares coverage, escape hatches, and comparability limits;
- one `mir-observation-report/v0` that records what was actually captured and what was missing;
- one `mir-query-report/v0` / `mir-derived-graph/v0` family for downstream consumers;
- one `mir-diff-report/v0` that can say **comparable**, **partially comparable**, or **not comparable**;
- and one `cargo mir` workflow that can capture, diff, query, doctor, and pack those artifacts.

That gives the ecosystem a reusable boundary **before** every analyzer, verifier, and CI system cements a different incompatible driver format.
