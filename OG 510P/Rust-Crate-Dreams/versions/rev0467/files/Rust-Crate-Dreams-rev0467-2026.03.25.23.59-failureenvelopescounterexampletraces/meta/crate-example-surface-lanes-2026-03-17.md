# Crate example-surface lanes — 2026-03-17

This note keeps one specific crate lane from dissolving into vague “better docs/examples/tutorials” language.

## The lane this file is defending

The missing lane is:

- **receiver-facing crate example-surface contracts** — official quickstarts, runnable starter paths, example-support levels, environment assumptions, docs/example linkage, expected outputs, and release-to-release diffs.

The sharp question is:

> “What is the smallest officially supported path from zero to first success with this crate, and where do the examples I should trust actually live?”

## What it is not

### 1. Not task-first crate choice

**P-0509** is about choosing *which crate* to start with for a task.
**P-0524** is about the official start path *inside a chosen crate*.

### 2. Not compile-time guidance or failure-path support

**P-0512** is about diagnostics, recovery recipes, and helping users through failure states.
**P-0524** is about first-success and adoption-example surfaces before the user ever gets lost.

### 3. Not configuration/setup scenarios

**P-0516** is about feature/profile/env recipes and setup choices.
**P-0524** says which example demonstrates each scenario, what prerequisites it has, and what success looks like.

### 4. Not downstream test-surface contracts

**P-0523** is about fixtures, fake backends, scenario corpora, and deterministic seams for downstream tests.
**P-0524** is about onboarding, quickstarts, example surfaces, and first-success contracts.

### 5. Not docs rendering / docs.rs parity / hosting

**P-0472** and related docs lanes are about docs.rs build parity and documentation delivery surfaces.
**P-0524** may import docs.rs constraints, but its core artifact is the example-support contract a crate publishes to users.

### 6. Not tutorial publishing platforms

A tutorial CMS, docs portal, or hosted walkthrough system can publish content.
**P-0524** is narrower: it exists to make crate-authored example support explicit, reviewable, and diffable.

## Working rule for future passes

When a pass proposes another crate in this neighborhood, it must state explicitly whether the missing value is primarily about:

1. **task-first crate choice**,
2. **failure-path / compile-time guidance**,
3. **configuration/setup support**,
4. **downstream testing support**,
5. **docs rendering / docs.rs parity / hosting**,
6. **tutorial publishing platforms**,
7. or **receiver-facing example-surface contracts**.

Do **not** let the archive quietly collapse README examples, docs.rs presentation, tutorial sites, quickstart recipes, and test harnesses into one fake learning-support lane.

Future passes in this area should also name at least **two adjacent lanes considered but not promoted**, so archive memory retains the boundary instead of restating it later from scratch.
