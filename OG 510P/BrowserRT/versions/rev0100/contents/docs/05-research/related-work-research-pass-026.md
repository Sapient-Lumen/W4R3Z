# Related-work research pass 026 — resilience governors

Revision: rev0031

## Question

What should BrowserRT steal from circuit-breaker, bulkhead, retry-budget, and overload-governance systems before it spends OPFS/browser budget?

## Sources and steals

### Resilience4j CircuitBreaker

Resilience4j frames a circuit breaker as a finite-state machine with `CLOSED`, `OPEN`, and `HALF_OPEN` states, backed by count- or time-based sliding windows. The useful steal is not the Java API; it is the separation between permission acquisition, outcome recording, pre-aggregated window snapshots, and state transitions.

BrowserRT steal:

- `tryAcquire()` must be separate from `release()` / outcome recording.
- Circuit state transitions must be trace events.
- The first baby proof should use a count-based sliding window before any real-time/timer surface.
- `HALF_OPEN` must have bounded probe admission.

### Resilience4j Bulkhead

Resilience4j distinguishes circuit breakers from bulkheads: a circuit breaker decides whether a dependency is likely to fail, while a bulkhead constrains concurrent access. That distinction is essential for BrowserRT because a storage provider can be healthy but saturated, or unhealthy even when no operations are in flight.

BrowserRT steal:

- Treat bulkhead capacity as a separate lease counter.
- Bulkhead rejection must not mutate lease accounting.
- Do not merge bulkhead and circuit state into one vague “unavailable” flag.

### Hystrix

Hystrix made dependency isolation concrete by using per-dependency thread pools / bulkheads and by letting a single probe through after an open sleep window. BrowserRT should not copy Hystrix’s thread-pool model, but it should steal the isolation vocabulary.

BrowserRT steal:

- Provider isolation is a first-class reliability primitive.
- Half-open probes are deliberate and bounded.
- Fallback behavior must be explicit rather than hidden.

### Envoy

Envoy treats circuit breakers as resource limits and explicitly discusses retry budgets so retries cannot explode into cascading failures. This maps to BrowserRT’s existing retry-budget lane.

BrowserRT steal:

- Circuit-breaking, retry-budget, and bulkhead policies must be composable.
- Static limits and dynamic retry budgets are different tools.
- Overflows/rejections need traceable counters.

### Azure cloud patterns

Azure’s Circuit Breaker and Bulkhead pattern docs are useful because they explain the user-facing goal: avoid wasting work against a dependency likely to fail, and isolate pools so one failing area does not exhaust unrelated resources.

BrowserRT steal:

- Future docs must explain why BrowserRT rejects work early.
- Resilience policies are not “performance optimizations”; they are overload safety contracts.
- Every resilience proof needs non-claims around real durability, timers, SLOs, and production safety.

## Cube decision

Rev0031 adds the baby rung: `CircuitBreakerBulkheadController` with a fake-provider, virtual-tick, count-window proof.

It intentionally does **not** add OPFS/browser integration, wall-clock timers, adaptive tuning, cross-lane coupling, production circuit-breaker semantics, or exact implementations of any researched system.
