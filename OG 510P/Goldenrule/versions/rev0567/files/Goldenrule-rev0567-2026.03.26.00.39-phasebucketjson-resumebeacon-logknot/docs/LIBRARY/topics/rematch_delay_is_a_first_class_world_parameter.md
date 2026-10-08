# Rematch Delay Is a First-Class World Parameter

The current leave/rematch proxy now supports one tighter operational lesson for the inheritor:

> Do not hide rematch delay as a fixed background constant.

## What the local snapshot says

The derived report in `artifacts/reports/rematch_proxy_delay_pressure_snapshot_20260306.{md,json}` reuses the existing proxy grid and asks a narrow question:

- how much payoff do leave-based policies lose when rematching costs `2` dead rounds instead of `0`?
- how does that loss change as extortion becomes more common in the pool?

For the compact handoff baseline `CCEEE` (`leave_after_break`):

- the delay penalty is `0.134055` at extortion share `0.2`,
- `0.189680` at extortion share `0.5`,
- and `0.301582` at extortion share `0.8`.

For the stronger-but-slightly-less-compact proxy winner `CCDDE`:

- the same penalty is `0.133138`, `0.185156`, and `0.263853`.

So delay is not cosmetic. It becomes more expensive precisely in the regimes where bad partners are common and leaving is most valuable.

## Why this matters

The earlier proxy result already said rematching changes the frontier. This refinement says something more specific:

- **search friction is part of the world**,
- not just a reporting nuisance,
- and not just an implementation detail to fill in later.

If a leave/rematch policy only looks good when replacement is free, then that is a property of a particular outside-option regime, not a general Golden-Rule-style win.

## What is still encouraging

Even after paying this delay tax, the simple `CCEEE` baseline still beats three important comparators in all nine tested cells:

- `always_c`,
- `mem1_courteous_firm_v1`,
- and the first-defect exit trap `DCECC`.

It is also nearly tied with `CCDDE`, losing only in the single harshest tested cell (`extortion=0.8`, `delay=2`).

That makes `CCEEE` a good inheritor baseline for the same reason it was already attractive: it is easy to explain, hard to mistake for a trap policy, and robust across the current proxy grid.

## Implementor guidance

1. Expose rematch delay / search friction as an explicit world field.
2. Sweep that field in every leave/rematch benchmark family.
3. Treat claims that hold only at one delay setting as provisional.
4. When the endogenous rematch world lands, test whether the current near-minimax `CCEEE` shape still survives once delay interacts with reputation, market thickness, and assortment.
