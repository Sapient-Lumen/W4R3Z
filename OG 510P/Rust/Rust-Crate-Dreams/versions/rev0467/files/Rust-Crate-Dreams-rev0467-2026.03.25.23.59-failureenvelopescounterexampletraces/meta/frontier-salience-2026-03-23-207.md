# Frontier salience 207 — pathfinder now needs freeze timeboxes, as-of replay, and knowability honesty

## Main judgment

The next worthwhile deepening for **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** is no longer another scoring formula.
It is a receiver-facing contract for **what was knowable when a starter set was frozen**, and how that old basis compares with the current ecosystem without silently rewriting history.

## Why this matters now

- the March 2026 Rust challenges post still says crate choice is shaped by choice paralysis, undiscoverable crates, and tacit knowledge;
- the 2025 State of Rust survey still says docs are canonical and still shows resource/compile pain, which pushes teams toward reusable starter sets instead of repeated bespoke research;
- crates.io now exposes `pubtime` in the index and explicitly names cooldown and replay-as-of-date use cases;
- crates.io search maintainers still describe ordering as a non-trivial unresolved problem rather than a solved recommendation layer;
- Cargo `add` and `info` expose useful package surfaces but still do not settle task fit or historical decision authority;
- docs.rs metadata and target-default changes prove that public support visibility can drift over time.

## What the sharper crate should provide

A stronger **P-0509** should now publish:

- `decision-timebox.receipt.json`
- `as-of-replay.report.json`
- bundle inventory that keeps freeze-time basis and current-view replay separate
- doctor rules that reject fake “the current winner was obviously the right historical choice” stories

## Boundary reminder

This is still **not** a better search engine, a blessed-crates council, or a popularity ranker.
It is the decision-layer artifact that lets another team review:

- what facts were in-bounds at freeze time,
- what changed later,
- what drift is visibility-only,
- and when human review is required.
