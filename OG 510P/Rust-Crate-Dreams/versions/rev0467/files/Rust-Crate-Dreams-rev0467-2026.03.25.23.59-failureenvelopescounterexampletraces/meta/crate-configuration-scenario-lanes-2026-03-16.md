# Crate configuration-scenario lane boundaries — 2026-03-16

This note exists so future archive passes do **not** collapse half a dozen nearby ideas into one fake “better crate setup docs” story.

## The distinct lane

**P-0516 Crate Configuration Scenario Pack Kit** is about the receiver-facing artifact for configuring one chosen crate for a named real-world scenario:

- named usage scenarios,
- feature/env/profile/docs.rs bundles,
- smallest recipe snippets,
- checked target/profile/runtime matrices,
- explicit conflict classes,
- and diffable configuration surfaces.

## What it is not

### 1. Not task-first crate choice

**P-0509** helps answer **which crate to choose** for a task.
**P-0516** assumes the crate is already chosen and answers **which configuration scenario to use**.

### 2. Not a producer-side support claim contract

**P-0510** is about what a crate claims to support in general.
**P-0516** is about the named, receiver-facing recipes for actually instantiating that support.

### 3. Not a shared interop profile pack

**P-0511** defines reusable ecosystem boundaries like runtime-neutral async APIs or shared `http`/`tower-service` expectations.
**P-0516** may point to those profiles, but it is not itself the shared contract.

### 4. Not compile-time guidance packs

**P-0512** is about failure-path guidance when using a chosen crate version.
**P-0516** is about choosing and validating a configuration scenario before those failures happen.

### 5. Not runtime handoff/support bundles

**P-0513** is about what happens after a crate fails at runtime.
**P-0516** is about how to set the crate up in the first place.

### 6. Not release-to-release upgrade packs or off-ramp packs

**P-0514** is about moving from release N to N+1 of the same crate.
**P-0515** is about leaving a crate, lane, or version family.
**P-0516** is about configuring the currently chosen crate in the present tense.

### 7. Not generic Cargo config-layer receipts

Cargo config-layer tools explain precedence across `.cargo/config.toml`, env vars, and CLI overrides.
**P-0516** is narrower and more crate-authored: it names intended usage scenarios above raw precedence.

### 8. Not feature-powerset or combo testing by itself

`cargo-hack` and similar tools can test many combinations.
They do **not** by themselves define which named scenarios matter, which ones are preferred, and which ones are docs-only or manual-review-only.

### 9. Not feature documentation alone

Feature-doc tooling can render descriptions of flags.
That does **not** by itself produce a stable scenario contract with recipes, checks, and diffs.

## Working rule for future passes

When a pass proposes another crate in this area, it must state explicitly whether the missing value is about:

1. **task-first crate choice**,
2. **current support/interop claims**,
3. **shared interop profiles**,
4. **crate configuration scenarios**,
5. **compile-time guidance**,
6. **runtime failure handoff**,
7. **upgrade packs / off-ramp packs**,
8. **generic Cargo config provenance**,
9. or **feature-matrix testing / feature docs**.

Do **not** let the archive quietly rephrase scenario packs as “better README setup”, “better feature docs”, or “better Cargo config explanation”.
