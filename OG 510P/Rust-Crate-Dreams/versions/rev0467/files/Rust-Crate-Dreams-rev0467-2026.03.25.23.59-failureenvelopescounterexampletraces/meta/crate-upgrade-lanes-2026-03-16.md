# Crate upgrade-pack lane boundaries — 2026-03-16

This note exists so future archive passes do **not** collapse half a dozen nearby ideas into one fake “better release tooling” story.

## The distinct lane

**P-0514 Crate Upgrade Pack Kit** is about the receiver-facing artifact for one crate release-to-release transition:

- supported `from -> to` upgrade lanes,
- imported hazard facts,
- machine-fix receipts,
- smallest before/after recipes,
- checked feature/target/runtime matrices,
- and explicit manual-review zones.

## What it is not

### 1. Not task-first crate choice

**P-0509** helps answer **which crate to choose** for a task.
**P-0514** assumes the user already chose the crate and is now asking **how to upgrade it**.

### 2. Not a producer-side support claim contract

**P-0510** is about what a crate claims to support right now.
**P-0514** is about what changed between releases and what a downstream user must do about it.

### 3. Not a shared interop profile pack

**P-0511** defines reusable ecosystem boundaries like runtime-neutral async APIs or shared `http`/`tower-service` expectations.
**P-0514** may point to those profiles when they change, but it is not itself the shared contract.

### 4. Not compile-time guidance packs

**P-0512** is about failure-path guidance when using a given crate version.
**P-0514** is about migrating between versions of that crate.

### 5. Not runtime handoff/support bundles

**P-0513** is about what happens after a crate fails at runtime.
**P-0514** is about what people need before or during an upgrade.

### 6. Not SemVer witness evidence or public-API release review

**P-0244** and **P-0483** are about evidence for whether a release is compatible or publicly ready.
**P-0514** is about the downstream-facing migration pack above those analyses.

### 7. Not release automation or changelog generation

`release-plz`, `cargo-release`, and changelog tools help maintainers publish releases.
They do **not** by themselves define a stable downstream artifact for hazards, machine-fix lanes, and checked migration recipes.

### 8. Not a universal codemod framework

Some upgrade lanes may include machine-applicable fixes or codemod hooks.
That does **not** mean the proposal should become a general refactoring platform.

## Working rule for future passes

When a pass proposes another crate in this area, it must state explicitly whether the missing value is about:

1. **task-first crate choice**,
2. **current support/interop claims**,
3. **shared interop profiles**,
4. **compile-time guidance**,
5. **runtime failure handoff**,
6. **release-to-release upgrade packs**,
7. **SemVer/public-API evidence**,
8. or **release automation/changelog tooling**.

Do **not** let the archive quietly rephrase upgrade support as “better docs”, “better semver checks”, or “better release automation”.
