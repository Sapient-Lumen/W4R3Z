# Concurrency-contract lane boundaries — 2026-03-23

This note exists to keep **P-0538 Concurrency Contract Kit** sharp.

The archive now has enough nearby lanes that “concurrency support” could easily dissolve into a vague pile.
This file exists to stop that.

## What P-0538 owns

P-0538 owns **receiver-facing support contracts** for concurrency semantics that are otherwise scattered across crate docs, issue threads, and folklore.

The core review objects are:

- `reentrancy-scope.report.json`
- `progress-fairness.report.json`
- `wait-cancellation.report.json`
- `execution-context-boundary.report.json`
- `concurrency-support-bundle.manifest.json`

The lane is about questions like:

- can the same task, thread, callback chain, or actor re-enter this surface,
- what ordering / fairness / starvation story is promised,
- what happens if an acquisition attempt is cancelled or dropped while queued,
- which execution contexts are required, allowed, discouraged, or forbidden,
- and whether the public claim ceiling is strong, partial, or manual-review-only.

## What P-0538 does **not** own

### Not channel-capacity / overflow / shutdown truth
That belongs in **P-0529 Channel Surface Contract Kit**.

If the sharp question is about:
- bounded versus unbounded channels,
- send-side overflow policy,
- delivery guarantees,
- shutdown / close / drain behavior,
then stay in P-0529.

### Not queue/pool/cache/thread budget posture
That belongs in **P-0521 Crate Resource Surface Pack Kit**.

If the sharp question is about:
- pool size,
- worker count,
- cache growth,
- saturation or shed behavior,
- resource budgets,
then stay in P-0521.

### Not runtime family / service-topology choice
That belongs in **P-0532 Async Runtime Assurance Profile Kit**.

If the sharp question is about:
- Tokio versus Embassy versus RTIC,
- reactor/time-driver availability,
- bridge crates,
- deployment topology,
- runtime-capability routes,
then stay in P-0532.

### Not debugger / tracing / observability coverage
That belongs primarily in **P-0486 Debuggability Support Contract Kit** and adjacent observability lanes.

If the sharp question is about:
- stepping tasks,
- seeing async state in a debugger,
- production tracing,
- metrics export,
- visualizers,
then stay there.

### Not proving absence of races or deadlocks in the formal sense
That belongs in model-checking / verification / unsafe-review lanes.

P-0538 can publish the **declared semantics** a surface claims.
It does not certify the implementation as correct in all executions.

## Practical anti-duplication tests

Before adding to P-0538, ask:

1. is the missing thing a **semantic contract** or a **primitive implementation**?
2. is the sharp pain about **waiting semantics** or about **resource volume / capacity**?
3. is the question about **how a primitive behaves** or **which runtime family is present**?
4. does the proposed work export a receipt/report/bundle, or is it only another abstraction layer?
5. are reentrancy, fairness/progress, cancellation, and context kept distinct instead of silently implying one another?

## Preferred next artifacts

When the archive next deepens P-0538, prefer sharpening:

1. callback and FFI re-entry scope,
2. starvation / priority / writer-preference classes,
3. queue-place loss under cancellation,
4. async-vs-blocking context legality,
5. and portable support bundles that keep those claims separate.

Do not let future passes rephrase this lane into generic async help, generic lock wrapper design, generic runtime comparison, or generic “concurrency safe” marketing.
