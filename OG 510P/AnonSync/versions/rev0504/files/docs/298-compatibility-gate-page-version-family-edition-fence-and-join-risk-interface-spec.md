# Compatibility gate page — version family, edition fence, and join risk interface spec

## Purpose

The archive already has release-channel, cohort, and migration language.
What it still lacked was one ordinary page for another recurring operator question:

> if I join, link, update, or mix these seats and subjects, is the result safe, sync-only compatible, risky, or blocked?

This page exists so compatibility truth does not fragment into FAQ snippets, update warnings, and post-failure folklore.

## Core rule

Compatibility is not one boolean.
The product must distinguish at least:

- wire/data compatibility
- identity/join compatibility
- control-plane/profile compatibility
- capability/edition compatibility
- subject-specific safety consequences

If the operator still has to mentally merge `can sync`, `can link`, `can update`, and `should never mix` into one decision, the page is not explicit enough.

## Fixed review order

Every serious compatibility-gate page should render the same sections in the same order:

1. **Compatibility verdict**
2. **Cohort matrix**
3. **Subject and state consequences**
4. **Admissible actions**
5. **Receipts and review history**

### 1) Compatibility verdict

This section should answer:

- which candidate seats, profiles, and subjects are under review
- whether the current verdict is `fully compatible`, `data-compatible only`, `join-risk`, `upgrade-required`, or `blocked`
- whether the verdict is steady or conditional on extra steps
- which boundary dominates the verdict

The operator must be able to answer: **what is the strongest honest compatibility verdict for this exact mix?**

### 2) Cohort matrix

This section should have stable rows for:

- runtime/build family
- protocol/schema family
- service/profile family
- capability/edition family
- storage/state-root continuity assumptions
- subject-kind or authority-family constraints

For each row the page should show:

- `current value` on each side
- `match class`
- `risk if mixed`
- `required action`

The operator must be able to answer: **which layer matches, which layer does not, and which mismatch matters most?**

### 3) Subject and state consequences

This section should show:

- whether existing subject configuration is preserved, shadowed, duplicated, downgraded, or at risk
- whether linking is safe, merely sync-safe, or unsafe
- whether storage-root continuity is required to avoid forked local worlds
- whether any subject kinds or authority paths are specifically blocked

The operator must be able to answer: **what concrete harm could happen if I ignore the warning?**

### 4) Admissible actions

Example actions:

- `Proceed — fully compatible`
- `Proceed after updating cohort X`
- `Proceed in sync-only mode, not linked mode`
- `Export and import through reviewed successor path`
- `Block and explain`

The page must not offer an undifferentiated `Continue` when the difference between `sync-safe` and `join-safe` is material.

The operator must be able to answer: **what is the strongest safe next action from here?**

### 5) Receipts and review history

This section should show:

- previous compatibility reviews
- updates or migrations already performed
- version/capability receipts
- exported evidence packet for support or audit

The operator must be able to answer: **what proof supports this gate verdict?**

## States

Use a small stable vocabulary:

- `fully compatible`
- `data-compatible only`
- `join-risk`
- `upgrade-required`
- `blocked`

## Main surface

A compact **Compatibility gate** card should show:

- current verdict
- strongest blocking boundary
- affected subjects count
- safest next action

## Key prohibitions

The product must not:

- present one green `compatible` label when only wire/data compatibility is true
- treat storage continuity and identity continuity as obvious side details
- hide edition/capability fences until after the attempted join or update
- let a blocked mix silently degrade into duplicate or shadow state without a reviewed plan
