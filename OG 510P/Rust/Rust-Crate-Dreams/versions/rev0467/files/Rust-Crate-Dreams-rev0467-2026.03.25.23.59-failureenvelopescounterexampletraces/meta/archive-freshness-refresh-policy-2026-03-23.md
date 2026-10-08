# Archive freshness / evidence refresh policy — 2026-03-23

This note is repo hygiene.
It is not a crate proposal.

It exists because the archive now has enough moving parts that future passes need a stable rule for how fresh web facts are imported and how reranks are justified.

## Main judgment

Future refreshes should use a **small core watch set** and record what changed.

Without that, later passes are too likely to:
- silently reuse stale assumptions,
- over-browse and lose the decision basis,
- or let one new post cause an unearned full rerank.

## Core watch set for broad refresh passes

When doing a broad ecosystem refresh, check these first:

1. **Rust challenges / vision / adoption signals**
   - current challenge posts
   - current survey results

2. **Rust project goals / flagships**
   - current flagship pages
   - specific goal pages directly touched by promoted proposals

3. **Cargo substrate**
   - build scripts reference
   - FAQ / rebuild diagnostics
   - unstable Cargo features when a promoted proposal depends on them
   - active testing / transition posts such as build-dir work

4. **docs.rs substrate**
   - builds
   - metadata
   - rustdoc JSON

5. **crates.io trust / security substrate**
   - development updates
   - malicious crate / policy updates
   - security advisories that materially change the support story

6. **domain-specific official writeups**
   - safety-critical
   - embedded / Linux / Wasm / target support
   - only when the current pass actually touches those lanes

## Evidence classes

Every fresh claim imported into the archive should be mentally tagged as one of:

- **evergreen official docs**
- **current project-goal / roadmap signal**
- **current operational / policy signal**
- **current incident / advisory signal**
- **manual inference from several official sources**

Do not quietly treat those evidence classes as interchangeable.

## Refresh contract for each broad pass

Each broad pass should record, in at least one entry or meta note:

1. which sources in the core watch set were re-checked,
2. what changed since the last pass,
3. what did **not** change,
4. which proposals were materially affected,
5. whether the result was:
   - no rerank,
   - salience rerank only,
   - practical queue change only,
   - or both.

## Salience vs shipability rule

Broad refreshes must preserve two separate judgments:

- **salience** — how important the missing crate looks for the territory,
- **shipability** — how realistic the next reviewable `0.1` looks under current substrate.

Do not let future passes flatten those into one ranking.
That flattening is the fastest route to archive drift.

## File discipline rule

When a pass adds new docs, prefer adding:
- one entry,
- one frontier or ranking note,
- one concrete product-plan note,
- and at most one meta-hygiene note,

instead of spraying many thin overlapping files.

Deepening beats document sprawl.

## Citation / freezing rule

Inside the archive itself:
- prefer canonical URLs,
- prefer exact page names,
- prefer “as of this pass” language when the source is volatile,
- and do not rely on search-result snippets as if they were the final authority.

For official docs that are mostly stable, it is acceptable to reuse them across passes.
For policy posts, advisories, surveys, and project-goal pages, broad refreshes should re-check them before making current claims.

## Promotion rule

A proposal should only be promoted on fresh signals when at least one of these became stronger:
- clearer official pain signal,
- clearer upstream substrate,
- clearer receiver-facing artifact seam,
- clearer cross-domain leverage,
- or clearer believable `0.1`.

If the new source did not materially strengthen one of those, prefer **deepen without reranking**.

## Amnesia resistors for future LLM passes

Before opening a new lane or reranking the frontier, future passes should explicitly ask:

1. is this really a new horizontal seam,
2. or is it another example that should deepen an existing lane,
3. and did a fresh source actually change the answer, or just restate the existing repo judgment?

If the source only restates the existing repo judgment, append lightly or do not rerank.

## Default recommendation

For the next several broad refreshes, start with:
- latest entry,
- latest frontier-salience note,
- latest practical queue note,
- latest epic scorecard application,
- latest archive memory anchor,
- then refresh the core watch set above.

That should keep the archive current **without** making it forget what it already learned.
