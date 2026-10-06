# Related-work research pass 027 — resilience model oracles

Carry-forward revision: rev0033.

Rev0032 keeps BrowserRT in the fake-provider/resilience lane and asks a narrower question than rev0031: can the new circuit-breaker/bulkhead controller survive generated histories checked against a separate reference model?

## Sources and stolen ideas

- Resilience4j CircuitBreaker docs: finite state machine vocabulary, count/time sliding-window aggregation, failure-rate/slow-call-rate thresholds, and half-open recovery limits. Source: https://resilience4j.readme.io/docs/circuitbreaker
- Resilience4j Bulkhead docs: max concurrent call limits and explicit rejection when a bounded resource partition is full. Source: https://resilience4j.readme.io/docs/bulkhead
- Netflix Hystrix “How it works”: dependency isolation and bulkhead thinking; one failing dependency should not consume all runtime capacity. Source: https://github.com/netflix/hystrix/wiki/how-it-works
- Envoy circuit breaking docs: pending/parallel request/retry limits and resource-count circuit-breaking vocabulary. Source: https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/circuit_breaking
- Polly resilience pipeline docs and migration notes: resilience is not one primitive; retry, circuit breaker, timeout, rate limiting/concurrency limiting, fallback, and hedging compose as a pipeline. Sources: https://github.com/App-vNext/Polly and https://www.pollydocs.org/migration-v8.html
- fast-check model-based testing: express actions as commands against a model and the real implementation, then compare after each generated step. Source: https://fast-check.dev/docs/advanced/model-based-testing/

## What BrowserRT steals

BrowserRT should treat resilience controllers as **modelable policy machines**, not as mystical runtime knobs. The first model oracle is deliberately small:

```txt
tryAcquire -> maybe reject or create a lease
release    -> record success/failure/slow call and maybe transition
advance    -> virtual tick toward half-open
forceOpen  -> manual open gate
close      -> manual reset gate
```

The important shape is not the exact Resilience4j/Hystrix/Envoy/Polly algorithm. The important shape is that BrowserRT can state its own semantics, generate histories, and compare the real controller to a reference model.

## One-to-rule-them-all dream

The ambitious runtime could eventually have a resilience composition plane:

```txt
priority/fairness -> admission -> bulkhead -> circuit breaker -> retry budget -> retry policy -> storage/render/gpu provider
```

Every stage would emit trace events, expose snapshot validators, and have a model oracle before provider spending. The long-term dream is not “copy service-mesh resilience into the browser.” It is a browser userspace kernel that can keep local work from self-amplifying into jank, quota storms, worker death spirals, GPU queue overload, or OPFS pressure.

## Why this stays fake-provider

Real timers, real provider latency, OPFS durability, browser workers, and cross-tab contention are expensive and noisy inside the cloudtainer. Rev0032 therefore uses virtual ticks, deterministic seeds, and release-tier Node execution. That preserves fast feedback while strengthening semantics.

## Non-claims

- No OPFS circuit-breaker/bulkhead model proof.
- No browser Worker circuit-breaker/bulkhead model proof.
- No production resilience claim.
- No exact Resilience4j, Hystrix, Envoy, Polly, Azure, or SRE implementation claim.
- No wall-clock timer, latency-SLO, throughput, durability, or cross-browser claim.
- No exhaustive model checking or formal verification claim.
