# rev0306 cube deep audit

## Highest-risk seam inspected

The riskiest unfinished work is still the returned-owner-evidence lane. The
project can prepare packets, clock contact, route a returned CSV, build an
intake bundle, seed a workbench, and prepare review/decision/live-window bridges;
what it does not yet have is a real owner-returned packet. That means every local
validator fixture is dangerous if it can look like field input.

`rev0306` audited the gap left after the field-lane split: returned CSV checks
blocked archive fixtures and smoke markers, but a plausible CSV placed under
checker scratch could still reach some returned-reply branches before intake
blocking. That is wasteful and risky because a maintainer could spend time
triaging validator byproducts instead of the real owner return.

## Correction made

The returned CSV guard now treats archive-local scratch as field input only when
it is in the live `FT-0181` field lane. It blocks:

- `scratch/checks/...`;
- `scratch/releases/...`;
- legacy `scratch/<non-field>/...`;
- any path component beginning with `check-`, `smoke-`, `test-`, or `fixture-`.

The field router's scratch firebreak was also widened so an intentional
`SCRATCH=scratch` debug run ignores the exact `checks` and `releases` lanes, not
just prefix-named children.

## Refactor choice

The change is deliberately small. It does not create a new schema, queue item, or
branch family. It edits shared guard code and checker fixtures, then adds one
regression: a syntactically valid checker-scratch CSV is blocked with
`RETURNED-CSV-SOURCE-BLOCKED` before returned-reply work can run.

## What remains risky

The remaining risk is human-operational, not archive-internal: the real owner CSV
must still be kept outside the release archive or intentionally placed in the
field lane, and the operator must run `owner-field-next` first. Direct intake and
repair targets still exist because they are useful after a routed command fails,
but they should not become the normal path.

## Next useful work

The next highest-value pass should keep shrinking the distance from a real owner
return to a human review decision. Prefer command summaries, smaller review
surfaces, and stronger source/hash checks over new doctrine. If no real owner
packet arrives, the correct state remains live and blocked, not more elaborate.
