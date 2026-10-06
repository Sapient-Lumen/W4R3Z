# Runtime dreambank 026 — BrowserRT as a resilience-governed kernel

Revision: rev0031

The dream is not “a circuit breaker utility.” The dream is that BrowserRT eventually has a resilience control plane that can sit in front of storage, GPU, network, media, render, mesh, and plugin providers.

## One-to-rule-them-all shape

A future BrowserRT provider call might pass through:

```txt
priority/fairness
  -> admission/watermark
  -> retry budget
  -> circuit breaker
  -> bulkhead lease
  -> provider execution
  -> outcome recorder
  -> trace/replay history
```

This would let the runtime answer:

- Should this work be admitted at all?
- Is the provider healthy enough to try?
- Is this retry allowed by budget and idempotency?
- Is the provider saturated?
- Should the failure open a circuit?
- Should a half-open probe be allowed?
- What trace evidence proves the decision?

## Why this belongs in BrowserRT

Browsers are hostile to accidental overload. A local app can freeze the main thread, fill memory, exhaust OPFS quota, saturate a worker pool, or spin forever on failed provider calls. BrowserRT’s job is to make those failure modes explicit and bounded.

## Rev0031 baby rung

The first implementation is deliberately small:

- count-based sliding window;
- virtual ticks, not wall-clock timers;
- closed/open/half-open states;
- bounded half-open probes;
- bulkhead active-lease cap;
- slow-call threshold;
- trace events;
- snapshot validation;
- release-tier proof and contract audit.

## Future rungs

- Model walks for generated circuit/bulkhead histories.
- Composition with retry-budget admission and storage-lane executor.
- Provider-integrated fake histories.
- OPFS storage-lane circuit proof only after fake-provider stability.
- Browser Worker proof only after OPFS spending is justified.
