# Related-work research pass 029 — provider-resilience model histories

Current revision: rev0054

This pass moves one stair above rev0033's composed fake-provider histories. The new question is not merely whether `ProviderResilienceHistoryRunner` can compose storage-lane scheduling, persisted spill, retry policy, retry-budget admission, and circuit-breaker/bulkhead gates. The question is whether the composed behavior can be checked against an independent model over many deterministic histories.

## Ideas stolen

- **Porcupine / Knossos / Jepsen history checking:** a runtime proof should eventually emit histories that can be judged against a model, not just logs that look plausible. BrowserRT's baby rung uses sequential fake-provider histories rather than true concurrent linearizability checking.
- **FoundationDB deterministic simulation:** failures should be seed-addressable and replayable. The model proof uses deterministic generated scenarios so a future failure can be replayed by seed.
- **Resilience4j state-machine vocabulary:** circuit breakers are finite-state gates with closed/open/half-open transitions; that makes them modelable.
- **SRE retry-amplification pressure:** retries are observable work and must remain bounded by budgets, provider health, idempotency, and breaker/bulkhead gates.

## What rev0035 does not steal yet

- It does not implement a Porcupine/Knossos linearizability checker.
- It does not explore true concurrent operation histories.
- It does not model OPFS, browser Worker behavior, crash recovery, quota, eviction, timers, or real latency.
- It does not claim production resilience or retry-storm safety.

## Design consequence

BrowserRT providers should increasingly be developed in pairs:

```txt
implementation provider + reference model + generated history proof + contract audit + non-claims
```

The earned primitive this turn is `ProviderResilienceModelOracle`, which checks `ProviderResilienceHistoryRunner` outcomes against an independent model and caught a real lease-accounting bug during development.
