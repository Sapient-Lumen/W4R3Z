# Rematch worlds should not panic-close positive batches after geometric miss streaks

Future inheritors should treat a pure no-arrival streak as **economically irrelevant evidence** under the current shared-state equiprobable exact batching model.

The new checkpoint-extension law closes a practical gap left by the earlier wait-value, timeout-capture, and timeout-batch-cap passes.
Those earlier laws told us:
- when waiting is economically positive,
- how much asymptotic upside a finite timeout captures,
- and how timeout/margin promises translate into batch caps.

What was still easy to mishandle operationally was the live writer loop itself.
A batch that has already waited several empty ticks can *feel* stale, and an implementor may be tempted to close it early just because “it has already waited long enough with no hit.”
Under a stationary geometric same-state arrival model, that intuition is wrong.

## Exact rule

If one more same-state exact script arrives each tick with probability `p`, the current shared-state batch length is `n`, the current state prefix cost is `state_prefix_bits`, and holding the batch costs `c` bits per script per tick, then:

- the conditional value of granting **one more tick right now** is exactly
  `p * state_prefix_bits / (n(n+1)) - c`,
- and the conditional value of granting **H more ticks right now** is exactly
  `(1 - (1 - p)^H) * (state_prefix_bits / (n(n+1)) - c / p)` whenever `p > 0`.

Nothing in either expression depends on how many empty ticks have already elapsed.
The elapsed miss streak cancels because the geometric arrival law is memoryless.

## Operational consequence

So future implementors should separate two different statements:

1. **Start-of-wait planning**: the ex-ante value of scheduling later and later extra ticks decays geometrically because fewer runs survive long enough to reach them.
2. **Checkpoint continuation**: once the writer has already reached a checkpoint with no arrival, the value of one more tick is the same sign test it was before.

That means:
- do **not** panic-close a positive batch merely because it has already waited through several misses,
- do close when the precommitted timeout budget is exhausted,
- and do re-evaluate only if the arrival hazard, hold cost, or shared feasible state has actually changed.

## All-state guardrail

On the current path, the exact lower envelope remains the seven-bit state family.
So the universal checkpoint rule is:

`7p / (n(n+1)) - c`

for one more tick, and

`(1 - (1 - p)^H) * (7/(n(n+1)) - c/p)`

for `H` more ticks whenever `p > 0`.

## How to use it

A good live policy is now straightforward:
- use the earlier laws to decide whether the batch is worth waiting on at all,
- choose the timeout horizon from explicit service or latency constraints,
- and while that horizon remains available, do **not** treat miss streak age by itself as a reason to abort a still-positive batch.

If an implementor wants age-sensitive behavior anyway, that age penalty should be modeled explicitly as an additional cost or deadline.
It should not be smuggled in by pretending the geometric miss streak changed the batching economics when it did not.
