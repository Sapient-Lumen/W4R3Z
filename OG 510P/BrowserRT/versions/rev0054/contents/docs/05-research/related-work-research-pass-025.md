# Related-work research pass 025 — retry-budget history oracle

Revision: rev0031

## Research seam

This pass treats BrowserRT as a future **history-checked overload-governance runtime**. The rev0029 retry-budget proof established hand-picked semantics. Rev0030 asks whether those semantics can survive generated histories before future sessions spend browser or OPFS budget.

## Ideas stolen

- **Google SRE retry budgets / cascading failure guidance:** retries can amplify overload, so a runtime should budget and reject some retries instead of pretending every retry is free.
- **AWS backoff and jitter guidance:** retry timing must be desynchronized and bounded; BrowserRT keeps deterministic virtual ticks in tests rather than wall-clock claims.
- **Envoy retry budgets / circuit breaking:** retry budgets belong beside active-request accounting and backpressure, not buried inside individual call sites.
- **Resilience4j event-oriented fault-tolerance components:** retry, circuit breaker, bulkhead, rate limiter, and time limiter can emit events; BrowserRT should make retry-budget decisions trace-visible.
- **fast-check model-based testing:** generated commands should execute against both a model and the real system under test.
- **FoundationDB deterministic simulation:** deterministic seeded histories are valuable because future failures need to be reproducible inside cloudtainer windows.
- **Jepsen / history checking pressure:** a system should be judged against the claims it actually documents, not against marketing vocabulary.
- **TLA+ finite-model humility:** a model proof only proves the finite model and assumptions under test.

## Stolen design pressure

BrowserRT overload governance should eventually have:

```txt
policy config -> generated history -> reference model -> runtime execution -> invariant check -> trace artifact -> non-claim boundary
```

The project must avoid the trap of saying “retry budget” as if that means production retry-storm safety. Rev0030 only earns a deterministic model-walk proof for the fake retry-budget controller.

## New caution

A generated model walk can become misleading if it duplicates the implementation too closely. The mitigation is to make the artifact legible: record seeds, commands, observations, final snapshots, rejected cases, accepted cases, and non-claims. Future sessions can then inspect counterexamples instead of trusting a green checkmark.
