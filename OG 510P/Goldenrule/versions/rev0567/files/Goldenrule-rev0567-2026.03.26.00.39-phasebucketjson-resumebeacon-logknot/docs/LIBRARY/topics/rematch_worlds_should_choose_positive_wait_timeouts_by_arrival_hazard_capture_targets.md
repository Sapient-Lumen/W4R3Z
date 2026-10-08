# Rematch worlds should choose positive-wait timeouts by arrival-hazard capture targets

The previous pass separated two questions that had been tangled together:

- should a live shared-state exact batch wait at all,
- and if yes, how long should it stay open?

The first question is already answered by the wait-value sign test:

- wait iff `p * state_prefix_bits / (n(n+1)) > c`.

Once that inequality is positive, the remaining timeout problem becomes much simpler than it first appears.

Let

- `gain = state_prefix_bits / (n(n+1))`,
- `p` be the per-tick same-state arrival hazard,
- `c` be per-script per-tick hold cost,
- `T` be the timeout.

Then the exact net wait value from the previous pass is

- `(1 - (1 - p)^T) * (gain - c/p)`.

So if waiting is positive, the asymptotic value as `T -> infinity` is just

- `gain - c/p`.

And a finite timeout captures exactly this fraction of that asymptotic positive value:

- `capture(T) = 1 - (1 - p)^T`.

That means timeout selection is **arrival-only**.
It no longer depends on the state family, batch length, or hold cost once those have already cleared the sign test.
Those quantities determine whether waiting is worth doing at all and how large the asymptotic upside is.
But the timeout needed to capture, say, 75% or 95% of that upside depends only on `p`.

So future implementors should choose timeout in two stages.

1. Run the economic gate:
   - if `p * state_prefix_bits / (n(n+1)) <= c`, do not wait.
2. If the gate is positive, pick a service target `alpha` in `(0, 1)` and use the smallest timeout with
   - `1 - (1 - p)^T >= alpha`.

For `0 < p < 1`, the closed form is

- `T_min(alpha, p) = ceil(log(1 - alpha) / log(1 - p))`.

For `p = 1`, every positive wait resolves in one tick, so `T_min = 1` for every `alpha <= 1`.

This gives compact arrival schedules immediately.
On the current audited path:

- if `p = 1/4`, capture at least `1/2`, `3/4`, `7/8`, `15/16`, `31/32` of the positive asymptotic value with timeouts `3`, `5`, `8`, `10`, `13`,
- if `p = 1/2`, use `1`, `2`, `3`, `4`, `5`,
- if `p = 3/4`, use `1`, `1`, `2`, `2`, `3`,
- if `p = 1`, use `1` throughout.

Two practical consequences matter.

First, finite timeout can never capture **all** of the asymptotic positive value unless `p = 1`.
So “100% capture” is not a meaningful finite operational target under uncertain arrival.
Treat it as an asymptote.

Second, expected wait ticks at the selected timeout are also arrival-only:

- `E[wait] = (1 - (1 - p)^T) / p`.

So the same schedule that controls value capture also controls service latency.
That is exactly the sort of compact control law the inheritor needs:

- economics decides whether to wait,
- arrival hazard decides how long to wait for any chosen fraction of the upside,
- and no state-specific retuning is needed after the wait gate has already gone positive.
