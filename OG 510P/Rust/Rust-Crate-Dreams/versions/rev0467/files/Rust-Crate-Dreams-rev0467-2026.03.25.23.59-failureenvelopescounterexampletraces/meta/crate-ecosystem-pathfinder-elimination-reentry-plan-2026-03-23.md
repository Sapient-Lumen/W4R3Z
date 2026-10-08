# Crate ecosystem pathfinder elimination / re-entry plan — 2026-03-23

This note exists to sharpen **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** into a more implementation-ready product.
The archive already had good material for:

- candidate import and basis receipts,
- interop/runtime/target fit,
- starter-set freezing,
- watch/revisit policy,
- and freeze-time replay.

What it still lacked was one boring receiver-facing story for **excluded but plausible candidates**.

## Main product shift

A credible pathfinder should now provide not just a ranked winner and a frozen starter set, but a **durable explanation for excluded candidates**.

That means the product must answer three more questions:

1. **Was this candidate excluded because it lost on trade-offs, or because it failed a hard gate?**
2. **What exact change would let this candidate re-enter consideration?**
3. **Which later public-surface changes must *not* silently resurrect it?**

## Why this became more urgent

Three ecosystem realities sharpen the gap:

1. **Public choice surfaces are getting richer**
   - crates.io now shows SLOC and carries `pubtime` in index entries,
   - Cargo `info` gives a compact package snapshot and may pick a version by MSRV,
   - docs.rs remains a highly visible support surface.

2. **Those surfaces are still not decision authority**
   - crates.io search ordering is still openly unresolved,
   - `cargo add` and `cargo info` are import surfaces rather than task-lane verdicts,
   - docs visibility can improve without solving target, policy, or lock-in mismatches.

3. **Teams forget losers faster than winners**
   - once a starter set is frozen, later reviewers often know the chosen crate but not why the obvious runner-up or famous alternative was kept out,
   - which creates avoidable churn, repeated debates, and silent criterion drift.

## What the crate should provide other people now

In addition to ranked choice and replay/watch artifacts, the crate should provide:

1. **A candidate-elimination receipt**
   - whether the candidate was `runner_up_not_chosen`, `blocked_by_hard_constraint`, `blocked_by_policy`, `out_of_scope`, or `manual_review_only`,
   - which axes blocked it,
   - which evidence refs supported the exclusion,
   - and whether the exclusion is reversible.

2. **A candidate-reentry policy**
   - which evidence classes can reopen consideration,
   - which ones are advisory only,
   - and whether re-entry merely permits reconsideration or can automatically re-import the candidate.

3. **A no-silent-resurrection guarantee**
   - changes in search order, popularity, docs polish, or SLOC visibility must not silently overturn a hard exclusion unless the stated re-entry conditions are met.

## First-class artifacts for this pass

### `candidate-elimination.receipt.json`

Purpose: capture one candidate-specific exclusion in a small durable object.

Suggested fields:
- `task_lane`
- `candidate`
- `elimination_class`
- `blocking_axes`
- `evidence_refs`
- `reversible`
- `reentry_policy_ref`
- `freeze_timebox_ref`
- `manual_review_required`

### `candidate-reentry.policy.json`

Purpose: declare what changes can reopen review for an excluded candidate.

Suggested fields:
- `task_lane`
- `candidate`
- `reentry_conditions[]`
- `non_reentry_signals[]`
- `decision_authority`
- `manual_review_required`

## Suggested workflow

### `cargo pathfinder freeze`
Emit the normal decision pack plus one or more `candidate-elimination.receipt.json` files for notable losers or policy-blocked alternatives.

### `cargo pathfinder reconsider --candidate <name>`
Load the candidate’s elimination receipt and re-entry policy, import new evidence, and render whether reconsideration is actually justified.

### `cargo pathfinder doctor`
Flag:
- runner-up status being mistaken for hard exclusion,
- search/order or popularity drift being mistaken for re-entry authority,
- docs/SLOC improvements being mistaken for solved target or policy gaps,
- and freeze-time exclusions being overwritten without an explicit receipt diff.

## Distinctions the implementation must keep explicit

### Runner-up is not blocked
A candidate that merely lost on trade-offs should be distinguishable from one that failed a hard gate.

### Re-entry is not replacement
A candidate becoming eligible again should trigger reconsideration, not silent starter-set replacement.

### Visibility change is not eligibility change
Better docs, a nicer landing page, new search order, or a smaller-looking crate page do not by themselves erase a missing feature, target gap, or policy mismatch.

### Candidate-specific re-entry is not starter-set watch state
`decision-watch.report` describes the frozen winner’s review status.
`candidate-reentry.policy` describes whether an excluded candidate may be reconsidered.

## Good proving grounds

1. a candidate excluded for MSRV mismatch that only re-enters after the team’s floor changes or the crate ships a compatible release,
2. a candidate that becomes more visible in search/docs/SLOC but still lacks required target/runtime support,
3. a portable pathfinder bundle that keeps winner, loser, and re-entry conditions separate.

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://github.com/rust-lang/crates.io/discussions/9325
- https://doc.rust-lang.org/cargo/commands/cargo-add.html
- https://doc.rust-lang.org/cargo/commands/cargo-info.html
- https://docs.rs/about/builds
