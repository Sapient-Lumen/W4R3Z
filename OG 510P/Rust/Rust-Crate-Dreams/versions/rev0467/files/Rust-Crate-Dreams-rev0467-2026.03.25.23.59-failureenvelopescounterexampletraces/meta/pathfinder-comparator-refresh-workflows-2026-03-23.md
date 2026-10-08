# Pathfinder comparator and refresh workflows — 2026-03-23

## Purpose

This note makes the **P-0509 Pathfinder** lane more operational.

The main product lesson is:

> a worthy pathfinder should not just pick a starter set; it should also explain when to refresh that answer and how to revalidate it without pretending every change requires a whole new selection process.

## A better first-release shape

A good `0.1.0` for Pathfinder should support one very specific loop:

1. compare 3–8 plausible crates for one task profile,
2. freeze one starter-set choice with a basis lock,
3. record runner-ups and explicit exclusions,
4. record recheck triggers,
5. later, emit a revalidation report instead of silently re-running the whole decision from scratch.

## The packet family this implies

### Initial compare
- `task-profile.json`
- `decision-packet.manifest.json`
- `candidate-elimination.receipt.json`
- `starter-set.lock.json`
- `basis-lock.manifest.json`

### Later refresh
- `decision-revalidation.report.json`
- `recheck-trigger.matrix.json`
- `manual-gap.note.md`

## What the revalidation report should answer

It should answer four narrow questions:

1. **same task?**
   Are we still solving the same job for the same receiver class?

2. **same policy?**
   Are the same target, MSRV, trust, or delivery rules still in force?

3. **same leading choice?**
   Does the current evidence still support the same starter set?

4. **same runner-up set?**
   Did any excluded or runner-up crate newly cross a meaningful threshold?

If the answer to the first two is “no,” the tool should open a **new compare packet**.
If the answer to the first two is “yes,” then a **revalidation packet** is enough.

## Trigger classes worth supporting in 0.1

- `new_release_in_frozen_candidate_set`
- `new_advisory_or_security_import`
- `docs_surface_changed`
- `target_support_changed`
- `msrv_or_rust_floor_changed`
- `source_parity_or_registry_route_changed`
- `manual_policy_change`

## What this should provide other people

For another engineer or reviewer, Pathfinder should provide:
- one **frozen comparison packet**,
- one **short revalidation report**,
- visible **runner-ups and exclusions**,
- visible **recheck triggers**,
- and a visible **manual-review ceiling**.

That is much better than handing them a fresh ranked list each time something moves.

## Important non-claims

Pathfinder should not claim:
- that every public-surface improvement reopens architecture fit,
- that popularity or security signals override explicit exclusions,
- or that a revalidation packet is the same thing as a fresh decision under a changed task profile.

## Best immediate scenario hooks

The most credible first scenarios are:
- a runner-up remains visible but does not revive automatically,
- a docs.rs or support-surface change triggers review without rewriting history,
- an advisory import triggers revalidation but not automatic replacement,
- an MSRV or target change opens a new compare packet.

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://docs.rs/about/rustdoc-json
- https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html
