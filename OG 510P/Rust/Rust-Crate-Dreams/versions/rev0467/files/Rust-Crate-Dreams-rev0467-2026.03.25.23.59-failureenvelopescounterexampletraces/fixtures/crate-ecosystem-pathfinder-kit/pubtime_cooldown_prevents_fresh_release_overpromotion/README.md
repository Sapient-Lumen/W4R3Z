# Scenario — `pubtime_cooldown_prevents_fresh_release_overpromotion`

This fixture exists to prove that **P-0509** should not silently promote a newly published crate into a starter set just because it suddenly looks fresh, visible, or exciting.

The review question is not “should this crate be imported?”
It is “is this signal mature enough to help freeze a default stack without human review?”

## What the scenario should force

- `candidate-import.report.json` may import the candidate.
- `evidence-origin.report.json` should mark publication time and registry metrics as **registry metadata**, not task-fit proof.
- `freshness-window.policy.json` should keep a recent publish in a cooldown or review-first class.
- `decision-pack.report.json` should prefer `manual_review_required` or keep the mature incumbent ahead until the freshness window clears.

## Why it matters

crates.io now records `pubtime` in the index and exposes cleaner Cargo-only download counts.
That is useful signal, but it should not let a recommendation engine become a “latest thing wins” machine.
