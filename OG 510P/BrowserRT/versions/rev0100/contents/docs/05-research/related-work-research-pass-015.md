# Related-work research pass 015 — admission control and overload governance

Revision: rev0028

## Research seam

This pass asks what BrowserRT should steal from systems that survive overload rather than merely buffering it.

The answer: BrowserRT needs an admission-control vocabulary before it grows more providers. Spill mailboxes proved that data can move from hot memory to a cold provider, but a runtime must also decide when not to admit work at all.

## Sources consulted

Recorded in `artifacts/research/RELATED-WORK-SOURCE-REGISTRY.json` and `artifacts/research/TEST-FACILITY-RESEARCH-REGISTRY.json` without raw external URLs.

New source families added or extended:

- Reactive Streams demand and non-blocking backpressure.
- Netty write-buffer high/low watermarks.
- Aeron publication offer/back-pressure behavior.
- Apache Flink backpressure monitoring and upstream propagation.
- TCP congestion control and AIMD vocabulary.
- Netflix concurrency-limits.
- Envoy adaptive concurrency filter.
- Kubernetes API Priority and Fairness.
- SRE overload handling and load shedding.
- Token bucket / traffic shaping vocabulary.

## What to steal

### Demand is a protocol, not a hint

Reactive Streams makes demand explicit. BrowserRT should not treat producer speed as an accident. Producer admission, queue capacity, consumer demand, and overflow behavior should be visible in the mailbox/provider contract.

### Watermarks are state transitions

Netty write-buffer watermarks are useful because they are not a vague “almost full” warning. They create a state transition: above high watermark, the channel becomes not writable; below low watermark, it becomes writable again.

BrowserRT should preserve this shape:

```txt
below low        → open
between low/high → cautious
above high       → congested
above hard limit → reject
```

### Backpressure must propagate upstream

Flink’s backpressure framing is useful because overload in one operator fills buffers and propagates to upstream operators. BrowserRT lanes should eventually surface similar pressure propagation in task graphs and traces.

### Offer failure is a normal outcome

Aeron’s `offer`-style pressure vocabulary is useful: a producer tries to publish and may receive temporary backpressure rather than being allowed to grow unbounded memory.

### Adaptive limits are tempting but dangerous

Netflix concurrency-limits and Envoy adaptive concurrency show the future direction: dynamically tune allowed in-flight work from observed latency or pressure. But rev0025 does not attempt that. First we need deterministic watermarks, trace events, and rejection semantics.

### Fairness belongs at admission time

Kubernetes API Priority and Fairness is useful pressure: classify work and protect important traffic from best-effort floods. BrowserRT should not just have a single global full/empty state.

### Load shedding must be explainable

SRE overload guidance points toward graceful degradation and load shedding, but warns that complex degraded modes can create new problems. BrowserRT should trace every rejection and make the policy inspectable.

## Translation into BrowserRT

New noun:

```txt
WatermarkAdmissionController
```

New proof:

```txt
ipc:admission-watermark-proof
```

New trace events:

```txt
admission:create
admission:admit
admission:high-watermark
admission:reject
admission:release
admission:low-watermark
admission:provider-unhealthy
admission:provider-healthy
```

## Design warning

Spill is not a substitute for admission control. A runtime that always spills can hide overload until recovery, compaction, or quota handling becomes the failure site.

## Non-claims

This pass does not claim adaptive concurrency, latency sampling, fairness scheduling, browser behavior, OPFS admission, performance, or cross-browser correctness.
