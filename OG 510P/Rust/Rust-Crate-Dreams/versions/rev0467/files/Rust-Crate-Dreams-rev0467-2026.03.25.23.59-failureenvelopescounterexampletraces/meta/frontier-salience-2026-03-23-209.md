# Frontier salience 209 — pathfinder now needs explicit exclusion receipts and candidate re-entry honesty

## Main judgment

The next worthwhile deepening for **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** is no longer another ranking model.
It is a receiver-facing contract for **why a candidate was excluded** and what exact evidence would let it re-enter consideration later.

## Why this matters now

- the March 2026 challenges write-up still says crate choice is shaped by choice paralysis, tacit knowledge, and undiscoverable crates;
- public surfaces influencing choice are getting richer, not simpler: crates.io now shows SLOC and carries `pubtime` in the index;
- Cargo `info` and `cargo add` expose helpful package-selection surfaces without becoming task-fit authority;
- docs.rs remains a powerful support-visibility surface, but its builds are nightly, target-aware, and cross-compiled for non-default targets;
- crates.io search ordering is still openly unresolved and currently falls back to weighted text ranking plus lexical tie-breaking.

That combination makes a common failure mode more likely: teams remember the winner, but forget whether a loser was merely a runner-up, truly blocked by a hard constraint, or only excluded because the evidence was too weak at freeze time.

## What the sharper crate should provide

A stronger **P-0509** should now publish:

- `candidate-elimination.receipt.json`
- `candidate-reentry.policy.json`
- bundle inventory that keeps chosen answer, excluded candidates, and re-entry conditions separate
- doctor rules that reject fake “this crate is back in because it looks more popular/search-visible/docs-polished today” stories

## Boundary reminder

This is still **not** a generic search engine, popularity score, trust score, or auto-migration policy.
It is the pathfinder-layer artifact that lets another team review:

- why a candidate was out,
- whether that exclusion was reversible,
- what evidence class could reopen consideration,
- and when human review is still required.
