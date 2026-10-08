# Cargo resolver explanation — proof-carrying fixture lanes (2026-03-16)

Purpose: keep **P-0468 Cargo Resolver Explanation Kit** focused on the reviewable evidence layer that is still missing.

## Main judgment

The next worthwhile work on P-0468 is **not** another graph library, another alternate resolver, or another human-only tree wrapper.
It is the boring fixture and receipt layer above Cargo’s existing and emerging resolver substrate.

That boundary is sharper now because:

- the PubGrub-in-Cargo goal explicitly says the new resolver should have **complete output** with enough information to determine it made the right decision,
- Cargo’s resolver docs still describe a two-stage story: lockfile generation as-if all workspace features are enabled, then a second pass for actual compile-time features,
- unstable docs now define three explicit feature-unification policies (`selected`, `workspace`, `package`),
- and `cargo tree` still documents itself as *pretty close* rather than exactly equivalent to the actual build plan.

So the missing crate layer is:

1. a **capture lock**,
2. a **family of small reason/report schemas**,
3. an **exactness and evidence-source receipt**,
4. and a **fixture corpus** for the most confusing resolver-pressure scenarios.

## What belongs inside P-0468

A worthy P-0468 crate may own:

- `resolve-why.lock`
- feature-cause reports
- version-choice reports
- duplicate-build grouping
- lane / target / participant scope reports
- dependency-origin / feature-origin / dependency-identity reports
- exactness / evidence-source receipts
- diff reports between captures
- scenario packs and compliance tests for tools that emit those artifacts

## What does **not** belong inside P-0468

Do not silently collapse these together:

- Cargo’s actual resolver implementation,
- PubGrub integration work,
- build-analysis history warehousing,
- workspace-boundary discovery,
- mixed-MSRV policy planning,
- semver witness publication checks,
- and broad support/debug doctor flows.

The crate should consume those surfaces where appropriate, not impersonate them.

## Recommended scenario families

For the next few passes, prefer scenarios that are maximally likely to confuse real users and tool authors:

1. **Mixed-MSRV shared-version compromise**
   - one member pulls versions down,
   - another could use a newer version,
   - the receipt must say whether the result is heuristic, lockfile-carried, or policy-shaped.

2. **Single-member question blurred by workspace-wide feature pressure**
   - the subject asked about one package,
   - workspace feature-unification or investigative surfaces let another package influence the answer,
   - the receipt must say so.

3. **Inherited / renamed dependency policy drift**
   - effective feature/default-feature behavior comes partly from `[workspace.dependencies]`,
   - feature tokens use a renamed local dependency key,
   - target-specific clauses or hidden `dep:` aliases make the answer only conservative.

## Archive stance

Prefer:

- schema-first fixture packs,
- exactness vocabulary that distinguishes observed / reconstructed / manual-review-required,
- and proposal work that says what another tool author could implement against.

Avoid:

- claiming that `cargo tree` or `cargo metadata` alone are exact resolver truth,
- inventing a new graph-serialization crate and calling it explanation,
- or flattening package selection, participant scope, and feature-origin into one fake “why enabled” answer.

## Sources

- PubGrub in Cargo goal: https://rust-lang.github.io/rust-project-goals/2025h1/pubgrub-in-cargo.html
- Cargo dependency resolution: https://doc.rust-lang.org/cargo/reference/resolver.html
- Cargo unstable features (`resolver.feature-unification`): https://doc.rust-lang.org/cargo/reference/unstable.html
- `cargo tree`: https://doc.rust-lang.org/cargo/commands/cargo-tree.html
