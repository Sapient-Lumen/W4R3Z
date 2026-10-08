# Rematch worlds should gate shared-state equiprobable exact batch waiting by arrival hazard and hold cost

The previous pass answered a purely local question:

- if one more same-state exact script definitely arrives, how many expected bits per script is that extra item worth?

That marginal-gain law is necessary but not sufficient for a live writer.
A writer also needs to price **waiting**.

This pass adds the missing operational bridge.

Assume the writer currently holds a shared-state exact batch of length `n`.
Assume one more same-state exact script arrives each tick with independent probability `p`.
Assume holding the current batch open costs `c` bits per script per tick in latency / service-value terms.
Assume the writer flushes immediately on success or after a timeout `T`.

Then the previous marginal law gives the gross gain of a successful extra item:

- `gain = state_prefix_bits / (n(n+1))`.

Under the geometric arrival model, the expected net value of waiting is exactly

- `(1 - (1 - p)^T) * (gain - c/p)`.

That is the key compression result.

The timeout `T` changes only the **scale** of the expected value through the success-capture factor `1 - (1 - p)^T`.
It does **not** change the sign as long as `p > 0`.
So the waiting decision itself collapses to one timeout-free inequality:

- wait iff `p * state_prefix_bits / (n(n+1)) > c`.

On the current path every realized state still has only a `7`-bit or `8`-bit state prefix, so the all-state guarantee becomes

- wait iff `p * 7 / (n(n+1)) > c`.

That makes the implementor's job much simpler.

- First decide whether the arrival hazard and hold cost make waiting **positive at all**.
- Only then choose a timeout for operational reasons such as latency caps or queue discipline.
- Do not let the timeout masquerade as an economic decision knob when the sign is already determined by `p`, `c`, and the current marginal-gain family.

On the current audited path, the universal all-state strict-positive schedules are already compact:

- with `p = 1/4` and `c = 1/10`, wait only through current batch length `3`,
- with `p = 1/2` and `c = 1/10`, wait through `5`,
- with `p = 3/4` and `c = 1/10`, wait through `6`,
- with `p = 1/2` and `c = 1/4`, wait through `3`,
- with `p = 1/4` and `c = 1/2`, wait only through `1` on an all-state guarantee.

So future sessions should treat the geometric-arrival wait-value law as the operational wrapper around the earlier marginal-gain law:

- use `state_prefix_bits / (n(n+1))` to price the extra item,
- multiply by arrival hazard `p` to get expected per-tick gross value,
- compare that directly to hold cost `c`,
- and keep timeout `T` as a magnitude / service-level knob rather than a sign-changing decision variable.
