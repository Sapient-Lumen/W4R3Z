# Related-work research pass 016 — adaptive concurrency and congestion control

Revision: rev0028

## Research seam

This pass asks what BrowserRT should steal from systems that change limits while a system is running.

rev0025 already has deterministic watermarks. That is necessary, but not enough for the far version. A browser userspace kernel will eventually see changing device speed, changing memory pressure, changing OPFS pressure, changing GPU readback costs, changing tab visibility, and changing user-visible jank. A static limit will be wrong often.

## Sources consulted

Recorded in `artifacts/research/RELATED-WORK-SOURCE-REGISTRY.json` without raw external URLs.

New or extended source families:

- Netflix concurrency-limits and latency-derived limits.
- Envoy adaptive concurrency and gradient controller configuration.
- Google SRE overload handling, graceful degradation, and load shedding.
- CoDel controlled delay as estimator + setpoint + control loop.
- TCP-style AIMD and congestion-control vocabulary.
- Kubernetes API Priority and Fairness, carried forward as future fairness pressure.

## What to steal

### Limits should be observed, not only configured

Netflix concurrency-limits argues that systems have an inherent concurrency limit and that latency can expose when queuing begins. BrowserRT can steal the concept without copying the exact algorithms: observe a provider, infer pressure, then adjust admission.

### Min-latency probes are expensive but useful

Envoy adaptive concurrency periodically estimates an ideal minimum RTT and compares sampled latency against it. BrowserRT should eventually have probe windows for providers, but those probes need trace evidence and user-visible protection because a probe can temporarily reduce capacity.

### Delay is a control signal

CoDel frames queue management as an estimator, a setpoint, and a control loop. BrowserRT should think similarly for queues and lanes: measure delay, compare to a target, then admit, shed, spill, or lower quality.

### Load shedding must be boring and inspectable

SRE overload guidance is useful because it treats overload as inevitable. BrowserRT should make degraded service and rejection explicit. A rejection should be a traceable decision, not a surprise exception.

### Adaptive policy needs kill switches

The dangerous part of adaptive control is feedback instability. BrowserRT should always be able to freeze a limit, fall back to static watermarks, or disable a controller.

## Translation into BrowserRT

New noun:

```txt
AdaptiveConcurrencyController
```

New proof:

```txt
scheduler:adaptive-concurrency-proof
```

New trace events:

```txt
adaptive:create
adaptive:admit
adaptive:reject
adaptive:release
adaptive:window
adaptive:limit-increase
adaptive:limit-decrease
adaptive:probe
adaptive:provider-unhealthy
adaptive:provider-healthy
```

## Design warning

Adaptive concurrency is not magic. It can protect a runtime, but it can also oscillate, starve low-priority work, punish the wrong provider, or hide a real bug by shedding too aggressively.

The baby slice is therefore deterministic and fake-latency based. It proves contract shape, not production tuning.

## Non-claims

This pass does not claim a faithful Netflix Gradient2, Envoy gradient controller, TCP Vegas, BBR, PID, CoDel, Kubernetes fairness, real latency measurement, production tuning, browser behavior, or performance.
