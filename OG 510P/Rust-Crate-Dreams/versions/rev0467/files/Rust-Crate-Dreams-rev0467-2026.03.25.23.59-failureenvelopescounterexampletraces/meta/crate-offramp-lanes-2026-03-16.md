# Crate off-ramp lane boundaries — 2026-03-16

This note exists so future archive passes do **not** collapse half a dozen nearby ideas into one fake “better deprecation tooling” story.

## The distinct lane

**P-0515 Crate Off-Ramp Pack Kit** is about the receiver-facing artifact for leaving a crate, API lane, feature lane, or unsafe version range:

- successor maps,
- observed deprecation/advisory/yank facts,
- checked exit recipes,
- compatibility classifications for replacements,
- sunset phases,
- and explicit manual-review zones.

## What it is not

### 1. Not crate health metadata

**P-0011** answers broad maintenance/governance questions like activity, MSRV, and succession posture.
**P-0515** answers the receiver-facing question: **what should a user do now that this crate wants them to leave?**

### 2. Not task-first crate choice

**P-0509** helps answer **which crate to choose** for a task.
**P-0515** assumes the user is already depending on the current crate and needs an exit path.

### 3. Not a producer-side support claim contract

**P-0510** is about what a crate claims to support right now.
**P-0515** is about how that crate hands users a successor path, stopgap, or honest `no_successor` answer.

### 4. Not compile-time guidance packs

**P-0512** is about failure-path guidance when using a chosen crate version.
**P-0515** is about leaving the crate or deprecating part of its surface.

### 5. Not runtime handoff/support bundles

**P-0513** is about what happens after a crate fails at runtime.
**P-0515** is about what maintainers hand users when continued adoption is no longer recommended.

### 6. Not release-to-release upgrade packs

**P-0514** is about migrating from version N to N+1 of the same crate.
**P-0515** is about leaving that crate, lane, or version family entirely, possibly for a successor crate.

### 7. Not advisory clients, outdated-version checkers, or ban policies

`cargo-audit`, `cargo-deny`, and `cargo-outdated` tell users that risk or staleness exists.
They do **not** by themselves define a stable maintainer-authored artifact for successor planning and checked exit recipes.

### 8. Not publish/yank tooling or governance transfer policy

Cargo and crates.io own publish, yank, and ownership mechanics.
**P-0515** consumes those facts; it does not replace registry policy or transfer workflows.

## Working rule for future passes

When a pass proposes another crate in this area, it must state explicitly whether the missing value is about:

1. **crate health / governance posture**,
2. **task-first crate choice**,
3. **current support / interop claims**,
4. **compile-time guidance**,
5. **runtime failure handoff**,
6. **release-to-release upgrade packs**,
7. **successor / deprecation / off-ramp packs**,
8. **advisory / ban / outdated detection**,
9. or **publish/yank / ownership mechanics**.

Do **not** let the archive quietly rephrase off-ramp support as “better advisories”, “better docs”, or “better deprecation notes”.
