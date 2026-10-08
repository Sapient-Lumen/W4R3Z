# Pilot Program: Starter Pack Kit

## Purpose
Prove that Starter Pack Kit can turn recommendation layers into reviewable starter repos **without** becoming another opaque template engine or another “blessed boilerplate” catalog.

The pilot should show five things early:
1. the chosen starter visibly imports its upstream lane/stack/workenv/policy truths;
2. rendered files have explicit ownership and drift boundaries;
3. refresh works when imported inputs change;
4. org overlays can add local requirements without losing provenance;
5. starter repos can generate bounded human/assistant guidance without replacing canonical docs;
6. direct and delegated renderer paths can both be recorded honestly instead of hidden behind boilerplate.

## Ranked rollout

### 1) Conservative CLI / internal-tool starter
Why first:
- low coordination cost,
- high demand,
- easy to inspect,
- and close to the “starter set of crates” problem Rust explicitly called out.

Minimum bar:
- `starter-subject/v0`
- `starter-sources/v0` importing atlas/adoption inputs
- `starter-layout/v0`
- `starter-render-plan/v0`
- `starter-support-profile/v0`
- `starter-check-report/v0`
- one rendered repo with explicit file ownership

Graduation question:
- can a reviewer see why this starter exists, which files are upstream-derived, and what needs re-checking later?

### 2) HTTP / service starter
Why second:
- it proves the kit can import richer productization and workenv truth;
- it forces runtime settings, local dev posture, and support/docs concerns into scope.

Minimum bar:
- import service-productization and workenv truths
- render workspace/env/runtime defaults with ownership boundaries
- validate one docs/example flow and one bootstrap flow
- emit one render report showing what the chosen renderer handled versus what remained local
- emit one refresh report after a simulated upstream change

Graduation question:
- can the starter survive real config/env/productization inputs without collapsing into framework-specific boilerplate?

### 3) Embedded or no_std starter
Why third:
- it proves Starter Pack can sit above specialized template ecosystems instead of trying to replace them;
- it forces target/toolchain/native/bootstrap posture to stay explicit.

Minimum bar:
- import target/toolchain assumptions
- preserve specialized template provenance
- emit a render report showing what the kit validated versus what it delegated to the external bootstrapper

Graduation question:
- can the kit honestly describe a starter whose real rendering path uses domain-specific tooling?

### 4) Org overlay + refresh lane
Why fourth:
- local overlays are where starter repos usually fork and drift;
- this is the sharpest test of whether the design really avoids hard-fork chaos.

Minimum bar:
- base starter + overlay starter
- forbidden-drift zones
- overlay diff report
- refresh showing an upstream change and a local conflict

Graduation question:
- can a team customize a starter while still knowing what remains inherited from upstream?

### 5) Derived guide / assistant-context lane
Why fifth:
- this is high leverage, but only after the canonical starter artifacts are trustworthy.

Minimum bar:
- derive one short human quickstart
- derive one bounded assistant context
- both must cite artifact freshness and ownership boundaries

Graduation question:
- can the kit improve docs/assistant output without making them the new source of truth?

## Scorecard
A pilot candidate scores well when it:
- imports real upstream starter inputs instead of inventing everything locally;
- preserves file ownership and overlay boundaries clearly;
- records freshness and refresh honestly;
- proves at least one direct render path and one delegated adapter path;
- proves at least one real validation flow;
- and reduces hidden starter drift rather than only generating prettier boilerplate.

## Failure modes to reject
Reject pilot outcomes that mostly produce:
- another template engine,
- one giant starter YAML blob,
- framework-specific glue with no provenance,
- generated repos that cannot explain their imports,
- or assistant outputs with no bounded freshness or ownership story.

## Expected outcome
If the pilot succeeds, the next archive move should be to treat **Starter Pack Kit** as the missing execution bridge between:
- choosing a lane,
- realizing a repo,
- and keeping that repo refreshable over time.
