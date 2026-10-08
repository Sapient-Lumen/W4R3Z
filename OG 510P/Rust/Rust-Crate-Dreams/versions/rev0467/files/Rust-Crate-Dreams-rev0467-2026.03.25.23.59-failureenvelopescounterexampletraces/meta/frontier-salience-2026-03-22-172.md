# Frontier salience refresh — 2026-03-22 (172)

## Main judgment

The next Cargo explainability pass should deepen **P-0469 Cargo Rebuild Explanation Kit**.

The sharpest remaining gap is no longer “can Cargo record build sessions?” and not merely “can it print a rebuild reason?”
The sharpest remaining gap is whether a downstream support bundle can say:

1. **why this baseline was the right one to compare against**, and
2. **what reverse-dependency fanout actually means**.

## Why this sharpened now

Current official substrate is finally explicit enough:

- Cargo unstable docs say build-analysis logs are persisted per invocation with a unique session id and queried via `cargo report sessions`, `cargo report timings`, and `cargo report rebuilds`.
- The Cargo 1.94 development-cycle update says `cargo report sessions` exists to find the id needed for the other report commands, which makes baseline selection a first-class downstream workflow rather than a hidden detail.
- The build-analysis goal says Cargo wants rebuild reasons and invocation metadata across runs, but also keeps schema evolution open during prototyping.
- The relink-don’t-rebuild goal says reverse dependencies still rebuild after non-interface edits, which means a support bundle must separate **observed fanout** from **proven interface impact**.

## What the crate should provide other people

A worthy P-0469 implementation should give another person:

- one receipt saying **why the baseline was chosen and which alternates were rejected**;
- one report saying **which dependents rebuilt and whether that implies anything stronger than observed fanout**;
- one exactness ledger saying which claims are imported, normalized, inferred, or manual-review-only;
- and one portable bundle another reviewer can read without local shell-history folklore.

## Why this is still distinct from adjacent lanes

- **P-0035** owns many-session warehousing.
- **P-0490** owns lock/wait diagnosis.
- **P-0494** owns tool-only parity and compile-time-deps drift.
- **P-0468** owns resolver and feature-cause chains.

P-0469 should stay on the smaller, support-ticket-sized question: **what rebuilt, compared to what, and how confidently can we say why?**
