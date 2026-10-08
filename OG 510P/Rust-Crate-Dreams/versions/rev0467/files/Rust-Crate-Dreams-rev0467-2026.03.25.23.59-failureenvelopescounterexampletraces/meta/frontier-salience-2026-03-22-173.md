# Frontier salience refresh — 2026-03-22 (173)

## Why P-0442 rose again

The archive already had a trait-solver witness idea, but current Rust sources make the sharper missing value clearer.

What changed is not just that the next solver exists.
It is that the transition now spans **multiple real lanes**:

1. the 2025H2 next-solver goal explicitly targets stabilization of `-Znext-solver=globally`, public testing, and expanded rustdoc/lint use;
2. stable Rust 1.84 already enabled the next-generation solver for coherence by default;
3. the rustc dev guide now documents material behavioral and diagnostic differences in the new solver, including canonicalization, proof trees, and fixpoint evaluation;
4. witness-generation work in `cargo-semver-checks` proved that “generate a witness and let rustc decide” is a viable strategy for hard type-level questions.

That makes the missing crate here less “another compiletest wrapper” and more a **support-contract layer for solver drift**.

## Main ranked takeaway

**P-0442 Trait Solver Drift Witness Kit** now deserves a full artifact-rich lane because it can offer something other crates do not:

- a lane receipt for which solver mode actually ran,
- an obligation-class report for what kind of trait-system question changed,
- a diagnostic-normalization receipt for when textual differences are normalized away,
- and minimization lineage for reduced repros.

## Why this beat adjacent ideas this pass

It beat a Polonius deepening pass because:

- the next solver already has a broader immediate surface across coherence, rustdoc, lints, and type-heavy libraries;
- the stable 1.84 coherence change means ordinary users are already exposed to lane splits;
- and the archive’s current P-0442 shape was still too early-stage compared with newer artifact-rich proposals.

It beat an EII or const-traits pass because the solver lane has a clearer review artifact vocabulary *today*.

## Boundaries to keep sharp

P-0442 should own:

1. solver-lane truth,
2. obligation-class classification,
3. diagnostic normalization,
4. minimized witness lineage,
5. and bundle exactness for trait-solver drift.

It should not silently become:

- a generic compile-fail runner,
- a Polonius / borrowck transition crate,
- a SemVer witness generator,
- or a generic rustc tracing dashboard.
