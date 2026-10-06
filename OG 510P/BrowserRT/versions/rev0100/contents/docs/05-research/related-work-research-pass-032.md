# Related-work research pass 032 — overload-governance histories

Current revision: rev0055

This pass keeps BrowserRT on the fake-provider/release-tier side of the staircase. The research pressure is not to claim production resilience; it is to name the overload-governance contract clearly enough that future sessions can compose it without losing the non-claims.

## Sources to steal from

- Google SRE cascading-failure and overload guidance: retries can amplify failures; overload handling must shed or degrade work before a dependency collapses.
- Envoy overload manager and circuit-breaking/retry-budget surfaces: resource monitors, triggers, actions, circuit breakers, and retry budgets are separate surfaces that must compose.
- Kubernetes API Priority and Fairness: classify work into priority levels and flows; admission and queueing policy are system-level contracts.
- Reactive Streams: backpressure is part of the protocol, not just a buffer implementation detail.
- Existing BrowserRT rungs: watermark admission, retry-budget admission, circuit-breaker/bulkhead, provider-resilience histories, and storage-lane admission models.

## Stolen idea

BrowserRT should eventually treat overload governance as a composed provider story:

```txt
admission gate -> bulkhead/circuit gate -> storage-lane placement -> retry policy -> retry budget -> provider mutation -> trace/history/model
```

Each gate should be able to say no before the next gate mutates state. Rejections are not accidents; they are first-class outcomes with trace evidence.

## Rev0037 tempering

Rev0037 does not build production overload control. It adds a fake-provider model oracle that verifies a composed history surface. The proof checks targeted and generated histories for success, retry success, retry-budget exhaustion, non-idempotent retry rejection, bulkhead rejection, open-circuit rejection, admission watermark rejection, admission health rejection, hard-limit rejection, critical bypass, no-provider-mutation on rejected finals, and lease release accounting.

## Why this belongs now

Future OPFS/browser spending will be expensive. The cube should know the expected overload-governance vocabulary before storage providers become durable, quota-bound, or browser-fixture-heavy. Rev0037 makes the model surface cheap enough for release-tier testing.
