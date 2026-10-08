# rev0022 refactor/audit notes

## Refactor

1. `src/muc5/ranker_policy.py` now includes `BlendedLinearRankerAgent`.
2. `src/muc5/public_agents.py` exposes three blended-ranker names through the public-agent factory.
3. `src/muc5/strategy_sets.py` now owns rev0022 mixed/ranker/MAP-Elites population builders.
4. `src/muc5/public_payoff.py` accepts optional prebuilt public agents and caches agents inside bulk payoff tables.

## New audit targets

rev0022 audit checks:

```text
blended ranker factory works
ranker race data exists and passed promotion/statistical gates
ranker race replay samples passed
ranker race C++ trace check has zero skipped events and zero mismatches
MAP-Elites ranker-variant data exists and passed promotion/statistical gates
MAP-Elites ranker-variant replay samples passed
MAP-Elites ranker-variant C++ trace check has zero skipped events and zero mismatches
new rev0022 docs/scripts/tests exist
```

## C++ policy

No new C++ file was added in rev0022. That is deliberate. The valuable C++ work this turn was to use the existing batch recorded-trace checker as a hard gate around new race outputs. The archive should not grow C++ surface area every turn unless the seam is stable and worth porting.
