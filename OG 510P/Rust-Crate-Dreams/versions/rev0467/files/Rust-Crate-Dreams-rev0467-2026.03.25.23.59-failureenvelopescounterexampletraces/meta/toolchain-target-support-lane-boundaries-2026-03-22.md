# Toolchain & target support lane boundaries — 2026-03-22

This note exists to keep **P-0484 Toolchain & Target Support Contract Kit** sharp after the latest 2026 support/stability signals.
The official ecosystem now makes “target-readiness checklists” look especially valuable, but that also makes it easier to blur P-0484 into neighboring lanes.

## Main judgment

**P-0484** should own the whole-project support contract for:

- effective toolchain selection,
- requested versus effective components/targets,
- target support classes,
- docs.rs public target posture,
- external prerequisites,
- exercise scope,
- and a new first-class **target-readiness report**.

It should **not** absorb every nearby support, build, MSRV, linker, docs, or API lane.

## The six truths P-0484 should keep separate

### 1. Override lineage
Which selector actually made the toolchain effective?
`cargo +toolchain`, `RUSTUP_TOOLCHAIN`, directory overrides, toolchain files, and defaults do not mean the same thing.

### 2. Support class
What does the project claim for a target or host lane?
`fully_supported`, `ci_verified`, `docs_only`, `compile_only`, `manual_setup_required`, `nightly_only`, and `manual_review_required` should remain explicit.

### 3. Exercise scope
What was really exercised?
`compile`, `docs`, `run`, `test`, `bench`, `host_build_script`, and `host_proc_macro` must stay separate.

### 4. External prerequisites
Which linkers, runners, SDKs, sysroots, boards, kernels, or env vars still matter outside Rust itself?
A rustup-installable target is not the same thing as a project-usable target.

### 5. Docs posture
What public target surface is the project publishing via docs.rs metadata and defaults?
Hosted docs visibility is a real support signal, but it is not equivalent to runtime support.

### 6. Target readiness
What concrete target-adoption facts would another team want before taking the lane seriously?
That means at least:

- Rust-project target tier,
- project support class,
- `std` / `no_std` posture,
- last known tested environment,
- important blockers,
- required external prerequisites,
- and which scopes were actually exercised.

### 7. Imported upstream authority
What support-shaping facts came from Rust-project policy, rustup host availability, docs.rs defaults, or Cargo docs?
Those upstream facts matter, but they are not identical to the project's own support class.

### 8. Public docs surface
What target/default posture is actually visible on docs.rs, and did it come from explicit metadata or implicit service defaults?
Hosted docs visibility is real evidence, but it is not equivalent to runtime or test support.

## What P-0484 must stay separate from

### Separate from **P-0036 MSRV Workspace Lab**
MSRV policy activation, command-family floors, and lockfile-authoring truth are related but distinct.
P-0484 may import them, but should not absorb them.

### Separate from linker-lane / native-build diagnosis
P-0484 can say a linker or SDK is required.
It should not become a full native-build failure explainer or toolchain bootstrap manager.

### Separate from **P-0472 Docs.rs Build Parity & Evidence Kit**
Docs posture belongs in P-0484, but hosted-build parity and issue replay remain a different lane.

### Separate from **P-0451** item-level cfg / availability truth
Whole-project support posture is not the same as item-level API availability.

### Separate from release-quality lanes like **P-0483**
A project may support many targets and still publish a weak or unstable public API.
Those questions should not collapse together.

## New `0.1` artifact worth promoting now

### `target-readiness.report.json`

This should be the receiver-facing checklist artifact that the January 2026 safety-critical post implicitly asks for.
A good `0.1` report should capture:

- `target`
- `rust_project_target_tier`
- `project_support_class`
- `std_posture`
- `last_known_tested_environment`
- `known_blockers`
- `required_external_prerequisites`
- `exercise_scope`
- `evidence`
- `review_status`

That gives another team a more honest answer than “the target exists” or “CI built once”.

## Anti-flattening reminders

Do not say:

- “Tier 2 means this project supports it.”
- “docs.rs built it so the target is fine.”
- “rustup ships a host for it, so this project supports it.”
- “docs.rs shows that target by default, so the project promised that target.”
- “The target is installed, therefore tests run.”
- “The repo pins stable, therefore the contributor saw the repo pin.”
- “It is a `no_std` target, so support expectations are obvious.”

Those are exactly the hidden assumptions P-0484 should make visible.

## Sources

- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/12/Rustup-1.29.0/
- https://rust-lang.github.io/rustup/overrides.html
- https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- https://docs.rs/about/metadata
- https://rust-lang.github.io/rfcs/2803-target-tier-policy.html
- https://doc.rust-lang.org/edition-guide/rust-2024/cargo-resolver.html
