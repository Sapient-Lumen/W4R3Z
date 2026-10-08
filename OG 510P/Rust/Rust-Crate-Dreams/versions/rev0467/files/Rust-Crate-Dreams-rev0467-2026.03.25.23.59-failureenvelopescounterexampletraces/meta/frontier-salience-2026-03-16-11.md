# Frontier salience scan — 2026-03-16 (rustc_public compatibility locks and analyzer fixtures)

This pass did not add a new top-level proposal.
Instead, it upgraded **P-0429 rustc_public Analysis Workbench Kit** into a much more implementation-shaped lane.

## Main judgment

The missing crate here is no longer “please expose public compiler APIs.”

The official Rust/compiler work now makes that a weaker read than it was earlier:

- the StableMIR / `rustc_public` goal was accepted,
- the 2025 GSoC work finished the hard `rustc_public` / `rustc_public_bridge` refactor and dual-maintenance setup,
- the compiler-team MCP spells out the SemVer publication model,
- and the nightly docs now show a real split between SemVer-shaped public APIs and semver-exempt `rustc_internal` / `unstable` surfaces.

That combination makes the sharper missing layer:

1. a **compatibility lock**,
2. a **fixture + capability + receipt** bundle,
3. and an **unstable-surface quarantine report** above `rustc_public`.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0429 rustc_public Analysis Workbench Kit**
3. **P-0055 Cargo Workspace Toolchain Manifest Kit**
4. **P-0056 Cargo Install Policy & Cooldown Kit**
5. **P-0489 Cargo Build-Dir Consumer Transition Kit**
6. **P-0508 Cargo Build Script Delegation Kit**
7. **P-0244 SemVer API Diff Evidence Kit**
8. **P-0507 Cargo Fix Campaign Kit**
9. **P-0478 Cargo Future-Incompat Triage Kit**
10. **P-0484 Toolchain & Target Support Contract Kit**
11. **P-0477 Cargo Publish Receipt Join Kit**
12. **P-0480 Cargo Global Cache Policy & GC Receipt Kit**

## Why P-0429 rose now

Earlier versions of the archive already knew that public compiler interfaces mattered, but the proposal still sounded a bit like “tooling people might want snapshots.”

The official picture is much sharper now:

- `rustc_public` is being shaped for **SemVer publication**,
- the compiler team is explicitly solving **multi-compiler-version maintenance**,
- and the current docs already admit that some modules remain **outside SemVer guarantees**.

That means the missing coordination artifact is more specific than before:

- not “some IR snapshot,”
- but a **tool compatibility matrix**,
- a **public-IR lock**,
- a **fixture corpus**,
- and a **receipt that says whether the result is cleanly inside the intended public surface**.

## What this pass did not do

It did **not** collapse:

- `rustc_public` publication engineering,
- `rustc_private` migration pain,
- formal semantics / counterexample exchange,
- Rust specification witnesses,
- and potential future syntax / expansion evidence

into one fake “compiler tooling crate”.

That restraint improved the archive.

## Sources

- StableMIR / `rustc_public` goal: https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
- GSoC 2025 results: https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Compiler-team MCP: https://github.com/rust-lang/compiler-team/issues/949
- project-stable-mir / Rustc Librarification project: https://github.com/rust-lang/project-stable-mir
- nightly `rustc_public` docs: https://doc.rust-lang.org/nightly/nightly-rustc/rustc_public/index.html
