# Trait-solver drift frontier — 2026-03-22

This note keeps **P-0442 Trait Solver Drift Witness Kit** from collapsing into neighboring lanes.

## The sharper problem now

The ecosystem does not merely need a way to run old/new compiler tests.
It needs a way to answer, for a changed case:

1. **which solver lane actually ran**,
2. **what kind of obligation changed**,
3. **whether the difference is semantic, diagnostic, or scope-only**,
4. **what normalization happened before that judgment**,
5. **and how a minimized repro maps back to the original case**.

## Why current substrate is finally enough

- The next-solver goal is explicitly about stabilization work for `-Znext-solver=globally`, public testing, and broader rustdoc/lint use.
- Stable Rust 1.84 already made coherence a default next-solver lane.
- The dev guide documents real solver-behavior and diagnostics differences.
- Witness-generation work in `cargo-semver-checks` proves the value of compiler-decided witness programs.

## What a worthy crate should provide other people

A worthy crate in this lane should provide:

- one **comparison-lane receipt** others can trust,
- one **corpus-authority receipt** explaining what kind of case this is,
- one **obligation-class report** that avoids hand-wavy “solver changed” explanations,
- one **diagnostic-normalization receipt** for diagnostic-only claims,
- one **minimization-lineage receipt** for reduced repros,
- and one **portable support bundle** for CI and issue filing.

If a candidate tool cannot do those things, it is still mostly compiler folklore.
