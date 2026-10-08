# Rematch worlds should turn capture-targeted positive waits into margin-floor batch caps

The last two passes separated waiting into two pieces:

- economics: whether a shared-state exact batch is worth holding open at all,
- operations: how long to wait once that economic gate is already positive.

That gave two exact rules:

- wait iff `p * state_prefix_bits / (n(n+1)) > c`,
- and if waiting is positive, the smallest timeout for capture target `alpha` depends only on arrival hazard `p`.

The next operational question is the one an implementor will actually face:

- given a capture target `alpha`, what current batch lengths are still admissible if the policy must realize at least `m` expected bits per script by that timeout?

The answer is still closed form.

Let

- `gain = state_prefix_bits / (n(n+1))`,
- `p` be per-tick same-state arrival hazard,
- `c` be hold cost in bits per script per tick,
- `alpha` be the desired fraction of asymptotic positive wait value to capture,
- `T_min(alpha, p)` be the minimum timeout from the previous pass,
- `beta(alpha, p) = 1 - (1 - p)^T_min(alpha,p)` be the **actual** capture fraction reached by that minimum timeout,
- `m` be the desired realized net margin by timeout.

Then the realized expected net value at that timeout is exactly

- `beta(alpha, p) * (gain - c/p)`.

So the target-margin condition is

- `beta(alpha, p) * (gain - c/p) >= m`.

Multiply through by `p` and substitute the earlier marginal-gain law, and the whole condition becomes

- `p * state_prefix_bits / (n(n+1)) >= c + p * m / beta(alpha, p)`.

That is the useful synthesis.
The capture-targeted realized-margin policy is **exactly equivalent** to the old positive-wait gate with one extra scalar tax:

- `effective_hold_cost = c + p * m / beta(alpha, p)`.

So future implementors should think in three layers.

1. Arrival hazard chooses timeout through `alpha`.
2. Desired realized margin `m` adds a tax `p * m / beta(alpha, p)`.
3. The batch stays open only while the old quadratic gate remains above this effective cost.

That yields the direct state-specific cap

- `p * state_prefix_bits / (n(n+1)) >= effective_hold_cost`.

And the all-state guardrail on the current path is just the seven-bit lower envelope:

- `p * 7 / (n(n+1)) >= effective_hold_cost`.

Two consequences matter.

First, timeout is still an arrival-only control.
The state family and batch length do **not** affect `T_min(alpha, p)`.
They affect only whether the target realized margin is feasible once that timeout has been fixed.

Second, a stricter realized-margin target looks exactly like extra holding cost.
Higher capture targets help because `beta(alpha, p)` rises, which shrinks the tax `p * m / beta(alpha, p)`.
So longer arrival-only timeouts can justify larger admissible batches not by changing economics directly, but by letting more of the asymptotic upside count toward the required realized margin floor.

That is the operational control rule the inheritor needs:

- choose an arrival-only timeout target,
- convert the required realized upside into one effective cost number,
- then apply the same quadratic close rule with either the state-specific prefix bits or the universal seven-bit floor.
