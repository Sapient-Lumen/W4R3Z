# Rematch worlds should cap batches directly from fixed timeouts and margin floors

The last passes gave the inheritor two exact controls:

- choose whether waiting is economically positive at all,
- and if a batch promise is fixed, solve the minimum timeout that can still realize it.

But a live implementor often starts somewhere else:

- the service already has a timeout budget `T`,
- the product promise requires realized expected upside at least `m`,
- and the scheduler needs to know the **largest current batch length** it may keep open under that timeout.

That inversion is also closed form.

Let

- `state_prefix_bits = s`,
- `current batch length = n`,
- `arrival hazard = p`,
- `hold cost = c`,
- `fixed timeout = T`,
- `target realized margin = m`.

From the earlier geometric-arrival law, the fixed timeout captures exactly

- `beta_T(p) = 1 - (1 - p)^T`

of the asymptotic positive wait value.

So the realized margin condition is

- `beta_T(p) * (s / (n(n+1)) - c / p) >= m`

whenever `p > 0`.

Multiply through by `p` and solve for the admissible quadratic budget:

- `n(n+1) <= p * s / (c + p * m / beta_T(p))`.

So the maximum admissible batch length is exactly the largest integer `n` satisfying that inequality.

That is the operational rule the archive was missing.
Future implementors no longer need to move through an intermediate capture target.
They can take the timeout they will actually run, compute one effective denominator,
then read off the batch cap directly.

The same rule explains what timeout does.
Longer timeouts help only through the capture factor `beta_T(p)`.
As `T` increases,

- `beta_T(p)` rises,
- the effective realized-margin tax `p * m / beta_T(p)` falls,
- and the admissible batch cap can only stay flat or grow.

So timeout ladders are monotone by construction.
That is exactly the shape an online planner wants.
It can increase patience only when larger batches are worth it, with no risk that extra patience makes a previously admissible batch suddenly invalid.

One small simplification is especially useful.
At one tick,

- `beta_1(p) = p`.

So the fixed-timeout denominator becomes

- `c + p * m / p = c + m`.

That means a one-tick timeout treats the realized margin floor as a literal extra cost term,
independent of arrival hazard.
The hazard still appears upstairs in `p * s`,
but the promise tax itself is just `m`.

The all-state guardrail is the same law with the exact seven-bit lower envelope:

- `n(n+1) <= 7p / (c + p * m / beta_T(p))`.

So the inheritor now has both batch-cap surfaces in exact closed form:

- choose a **capture target** first and cap by the minimum timeout that achieves it, or
- choose the **actual timeout budget** first and cap the batch directly.

Those are the same economics seen from opposite ends of the control loop.
