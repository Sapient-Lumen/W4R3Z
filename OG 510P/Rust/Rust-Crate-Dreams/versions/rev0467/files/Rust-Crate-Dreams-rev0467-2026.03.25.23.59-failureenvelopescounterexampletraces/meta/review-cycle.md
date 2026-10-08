# Review cycle

This archive should not become a graveyard of stale ideas.

## Cadence
- **Weekly**: add 1 entry in `entries/YYYY-MM-DD.md` if new signals appear.
- **Monthly**: review top 10 proposals by score and update:
  - `last_reviewed`
  - feasibility assumptions
  - “prior art” changes (new crates may have solved it)

## Staleness rules
- If a proposal has no progress for 6 months, change `status` to `archived` or add a concrete “why not” note in `meta/decision-log.md`.
- If a proposal becomes solved by a new crate or Cargo feature, mark it `archived` and link the replacement.

Last updated: 2026-03-01
