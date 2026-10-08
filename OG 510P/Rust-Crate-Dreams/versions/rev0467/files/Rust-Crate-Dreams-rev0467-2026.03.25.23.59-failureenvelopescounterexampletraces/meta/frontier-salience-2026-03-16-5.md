# Frontier salience scan — 2026-03-16 (single-file handoff + source-parity honesty)

This pass again avoided adding another top-level proposal.
The stronger move was to sharpen two already-worthy workflow crates whose value became more concrete after fresh 2026 Cargo and project-goal signals:

- **P-0435 Cargo Script Workbench Kit**
- **P-0496 Cargo Vendor & Source Parity Kit**

## Main judgment

The Rust ecosystem still looks likelier to benefit from **coordination artifacts above real substrate** than from another clever leaf library.
In this pass, the clearest underbuilt frontier is **handoff honesty** for two newly sharper Cargo lanes:

- single-file packages that are about to become mainstream,
- and vendored/mirrored source setups that still need a portable parity story.

Three current signals especially matter:

1. the Rust project is now openly treating cargo script as a near-stable workflow for minimal reproducers, tutorials, and quick prototypes,
2. Cargo’s single-file package docs now state explicit defaults and boundaries like disabled auto-discovery, hashed target-dir placement, and target-dir lockfiles,
3. the Rust project is also explicitly pushing on crates.io mirroring and verification, which makes it more important—not less—to separate external mirror proofs from workspace-local source parity truth.

Together, those make **script handoff artifacts** and **mirror-honesty parity bundles** look more urgent than adding another fresh protocol-specific idea right now.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0489 Cargo Build-Dir Consumer Transition Kit**
3. **P-0496 Cargo Vendor & Source Parity Kit**
4. **P-0435 Cargo Script Workbench Kit**
5. **P-0484 Toolchain & Target Support Contract Kit**
6. **P-0472 Docs.rs Build Parity & Evidence Kit**
7. **P-0486 Debuggability Support Contract Kit**
8. **P-0036 MSRV Workspace Lab**
9. **P-0506 Cargo Workspace Boundary Doctor Kit**
10. **P-0242 Reproducible Build Evidence Kit**
11. **P-0465 BorrowSanitizer Workflow & Evidence Kit**
12. **P-0458 Async Dyn Transition Kit**

## Why P-0435 rose now

Cargo script is no longer just a nice idea or a long-running third-party workaround.
The official docs and 2026 program update make it clear that single-file packages are on the verge of becoming a normal Rust workflow for examples, issue repros, and tiny utilities.

What remains missing is not another launcher.
It is a **receipt and export-plan crate** that can tell another person:

- what Cargo inferred,
- where the lockfile and target-dir lived,
- what workspace/config behavior did or did not apply,
- and how to turn the script into a maintained package without losing provenance.

## Why P-0496 rose now

The new mirroring push makes source parity more—not less—important.
Verified mirrors are about external trust distribution.
But teams still need one boring workspace-local artifact that says:

- which logical source IDs resolved,
- which physical roots they collapsed onto,
- what the vendored/mirrored boundary actually covered,
- and what verification evidence still left path/git spillover or alias splits unresolved.

That makes **source parity and mirror-honesty bundles** stronger than another generic offline helper.

## Why this pass did not add another proposal

The archive already has enough proposal count.
The missing value here was **artifact shape**:

- a real fixture pack for cargo script,
- actual scenario bundles for source parity,
- and sharper lane-boundary notes so future passes do not collapse script portability, workspace discovery, and mirror verification into one fake Cargo result.

## Working rule for the next few passes

Prefer upgrades that add:

- small schema-first bundles,
- import boundaries to upstream verification work,
- explicit inferred-versus-observed vocabularies,
- and sharper lane notes for Cargo-adjacent support crates.

The archive is now large enough that **better boundary honesty beats more proposal count** surprisingly often.

## Sources

- Program management update — January 2026: https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- This development-cycle in Cargo: 1.94: https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Cargo unstable docs, single-file packages: https://doc.rust-lang.org/cargo/reference/unstable.html#single-file-packages
- Secure quorum-based cryptographic verification and mirroring for crates.io: https://rust-lang.github.io/rust-project-goals/2025h1/verification-and-mirroring.html
- Cargo source replacement: https://doc.rust-lang.org/cargo/reference/source-replacement.html
- Cargo registry index docs: https://doc.rust-lang.org/cargo/reference/registry-index.html
