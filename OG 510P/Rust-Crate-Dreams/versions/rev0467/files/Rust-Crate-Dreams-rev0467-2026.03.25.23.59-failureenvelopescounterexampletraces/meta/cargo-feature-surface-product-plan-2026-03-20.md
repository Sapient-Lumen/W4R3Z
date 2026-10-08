# Cargo Feature Surface Contract Kit — product plan (2026-03-20)

This note sharpens **P-0528 Cargo Feature Surface Contract Kit** into an implementation-ready `0.1` shape.

## Core question

If somebody started building **P-0528** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

The first implementation should not try to replace Cargo’s resolver or enumerate every possible feature combination.
It should provide one boring, reviewable contract layer above existing Cargo semantics and helper tools.

`0.1` should make four things first-class:

1. **public feature surface** — which feature names are actually part of the crate’s receiver-facing contract;
2. **activation profiles** — which named combinations are supported, sampled, recipe-only, or unsupported;
3. **conflict policy** — whether features compose, are exclusive, or fall back to one chosen behavior;
4. **unification risk** — where default leakage, resolver-v2 splitting, or workspace unification can still surprise downstream users.

## What `0.1` should provide other people

- one compact `feature-surface.receipt.json`
- one compact `activation-profile.report.json`
- one compact `conflict-policy.receipt.json`
- one compact `unification-risk.report.json`
- an optional `combination-witness.report.json`
- one rendered `feature-surface.summary.md`
- a diff command for release reviewers

## Commands worth shipping first

- `cargo feature-surface init`
- `cargo feature-surface observe`
- `cargo feature-surface check`
- `cargo feature-surface doctor`
- `cargo feature-surface summary`
- `cargo feature-surface diff <old> <new>`
- `cargo feature-surface pack`

## What to import, not reinvent

- `Cargo.toml` feature declarations and optional dependencies
- Cargo feature semantics from the Cargo Book
- `cargo tree -e features` outputs where available
- optional receipts from `cargo hack`
- optional receipts from `cargo-feature-combinations`
- optional workspace-hack receipts from `cargo hakari`

## Suggested `0.1` doctor warnings

- `default_surface_not_explicitly_named`
- `public_feature_looks_like_internal_dep_toggle`
- `exclusive_features_without_conflict_policy`
- `profile_claim_without_witness`
- `workspace_unification_receipt_missing`
- `resolver_v2_split_risk_missing`
- `all_features_green_but_profile_matrix_sparse`

## First proving-ground scenarios

1. **Grouped optional dependencies hidden behind a public group toggle**
2. **Mutually exclusive backend features with explicit compile-time failure**
3. **Resolver-v2 host/target split creating duplicate or divergent feature sets**

## What to leave for later

- solver-grade full-cause reconstruction for every feature edge
- hosted dashboards
- automatic feature-space minimization
- policy as a service for organizations
- aggressive cross-workspace synthesis that risks hiding ambiguity
