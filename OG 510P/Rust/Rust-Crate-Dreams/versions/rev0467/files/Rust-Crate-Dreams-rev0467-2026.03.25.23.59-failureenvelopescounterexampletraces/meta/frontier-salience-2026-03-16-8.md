# Frontier salience scan — 2026-03-16 (fix orchestration and Cargo plumbing)

This pass added one new proposal and refreshed one older proposal.
The stronger move was to sharpen a gap between **automation substrate** and **automation orchestration**.

The two focal crates are:

- **P-0507 Cargo Fix Campaign Kit**
- **P-0432 Cargo Plumbing Interop Kit**

## Main judgment

The 2025–2026 Cargo signals now point to a specific missing layer.

The official docs and guide already say:

- `cargo fix` works by running the equivalent of `cargo check`,
- edition migration may require multiple target/feature runs,
- and `cargo fix` may loop until no new warnings remain.

Then the 2025 GSoC and Cargo-cycle updates added two stronger signals:

- the `cargo-fixit` prototype showed that top-level orchestration, target-safe passes, and interactive selection are a real design seam,
- and the Cargo plumbing work showed that phase-shaped commands exist, but current Cargo APIs still force compromises like re-reading manifests from disk.

Together, that suggests the ecosystem is missing:

1. a **generic fix campaign crate** above `cargo fix` / `cargo check`, and
2. a **blocker-aware plumbing receipt crate** below higher-level tooling.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0489 Cargo Build-Dir Consumer Transition Kit**
3. **P-0244 SemVer API Diff Evidence Kit**
4. **P-0478 Cargo Future-Incompat Triage Kit**
5. **P-0507 Cargo Fix Campaign Kit**
6. **P-0432 Cargo Plumbing Interop Kit**
7. **P-0431 Public Dependency Boundary Kit**
8. **P-0477 Cargo Publish Receipt Join Kit**
9. **P-0175 Trusted Publishing Tooling Kit**
10. **P-0495 Cargo Artifact Dependency Adoption Kit**
11. **P-0484 Toolchain & Target Support Contract Kit**
12. **P-0472 Docs.rs Build Parity & Evidence Kit**

## Why P-0507 rose now

Earlier archive work had edition rehearsal and future-incompat triage, but not the more general “how do we actually run an automation campaign responsibly?” layer.

The `cargo-fixit` prototype made the missing value more concrete:

- decide which targets are safe to fix in a pass,
- coordinate which suggestions get applied,
- remove lock-heavy orchestration assumptions,
- and leave room for interactive or staged workflows.

That is not just an implementation detail.
That is a real crate opportunity.

## Why P-0432 rose again now

The Cargo plumbing work did not just validate the phase taxonomy.
It also validated that the current Cargo APIs still force compromises.

That means downstream tooling still needs a crate that can say:

- what the caller intended,
- what Cargo actually consumed,
- which phase outputs were official versus reconstructed,
- and where a blocker still exists.

This is a stronger proposal than a generic “tooling API wrapper”.

## What this pass did not do

It did **not** merge:

- edition migration,
- future-incompat ledgers,
- fix orchestration,
- and plumbing receipts

into one mega-proposal.

That restraint made the repo better.

## Sources

- `cargo fix` docs: https://doc.rust-lang.org/cargo/commands/cargo-fix.html
- Edition Guide advanced migrations: https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
- Cargo plumbing goal: https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- Cargo 1.90 development cycle update: https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
- GSoC 2025 results: https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
