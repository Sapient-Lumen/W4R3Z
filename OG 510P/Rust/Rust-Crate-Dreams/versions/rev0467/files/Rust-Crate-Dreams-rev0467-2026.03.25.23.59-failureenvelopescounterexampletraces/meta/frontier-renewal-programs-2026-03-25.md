# Frontier renewal programs — 2026-03-25

This note keeps the frontier broadly stable **while making long-term upkeep first-class**.

The archive no longer needs more sector inflation.
It needs sharper answers to:
- what another team must keep fresh,
- what that freshness actually costs,
- and which events force a cheap recheck versus a deeper review.

## Main judgment

The strongest missing Rust contributions are still mostly **receiver-facing control-plane kits**.
But many of the leading lanes should now be planned as shipping **renewal programs / freshness budgets / stewardship loops** rather than only packets or verdicts.

## Renewal-leverage board

### 1. P-0509 + P-0536 + minimal P-0535
**Role:** review / decision / renewal front door

Why first under this lens:
- it is the cleanest place to bind reviewed packets to actual renewal scopes;
- it can expose cheap rechecks versus deep reruns without hiding the difference;
- and it can hand another team a stewardship summary instead of leaving them with raw evidence debt.

What the crate should provide:
- `renewal-program.json`,
- `freshness-budget.json`,
- `renewal-ticket.json`,
- `renewal-ledger.jsonl`,
- `stewardship-summary.md`,
- and `supersession-record.json`.

### 2. P-0431 + P-0496 + P-0125
**Role:** continuity / parity / supersession trigger ring

Why second:
- recent alternate-registry, advisory, and source-parity realities keep showing that renewal is often event-driven, not just calendar-driven;
- this ring is where release change, registry change, mirror divergence, and public-boundary drift become explicit renewal triggers;
- and it is the natural place to make retirement and carry-forward posture reviewable.

What the crate should provide:
- event-trigger receipts,
- carry-forward / supersession notes,
- registry/mirror parity deltas,
- renewal-slice hints,
- and explicit stale/grace/retired transitions.

### 3. P-0472 + P-0484
**Role:** evidence-refresh supplier

Why third:
- docs.rs and target/toolchain surfaces are already machine-usable enough to support cheap freshness checks;
- support claims still need importable basis and rerunnable replay slices;
- but renewal meaning should stay above raw evidence capture.

What the crate should provide:
- freshness classes for imported basis,
- replayable evidence slices,
- support-basis diffs,
- docs/build/target staleness reasons,
- and named “too stale to trust” outcomes.

### 4. P-0486
**Role:** debugger renewal kit

Why fourth:
- the official debugging material keeps emphasizing debugger / OS / version variance;
- and that variance makes renewal expensive unless the crate defines matrix slices and expiry rules honestly.

What the crate should provide:
- debugger-matrix freshness windows,
- narrow rerun slices for changed debugger / OS / compiler tuples,
- async-scenario corpus reuse,
- and visible “approval expired on this tuple” states.

### 5. P-0537
**Role:** build / iteration drift renewal

Why fifth:
- build-analysis and build-dir layout work make this lane more plausible;
- but the substrate is still moving enough that renewal doctrine should borrow shared stewardship rules rather than invent its own first.

What the crate should provide:
- drift-triggered rerun slices,
- latency-budget expiry semantics,
- and “changed substrate, summary invalid” states.

### 6. P-0538
**Role:** concurrency semantics renewal

Why sixth:
- very important,
- but the cost of scenario maintenance is high and should likely borrow the same renewal vocabulary only after the front door and continuity ring prove a stable pattern.

## Why the broad frontier still stays stable

This renewal lens still does **not** justify resetting the archive toward giant umbrella frameworks for web, GUI, game, ML, or local-first work.
Those sectors may still have unmet needs, but the sharper cross-domain missing value is usually:
- keeping support claims alive,
- tracking when evidence ages out,
- reducing recurring review burden,
- and retiring stale decisions cleanly.

That is why the archive still prefers control-plane kits above broad sector reinventions.

## Guardrail

Do not strengthen a lane under the renewal lens unless the pass can name:
1. the **renewal unit**,
2. the **cheap rerun slice**,
3. the **deep rerun trigger**,
4. the **owner / escalation path**,
5. and the **retirement / supersession rule**.
