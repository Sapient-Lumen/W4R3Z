# Rematch worlds should solve target batch promises by minimum timeout

The last pass answered one operational question:

- if a capture target `alpha` is fixed first, what is the largest batch length that still clears a realized margin floor `m`?

That is the right rule when product or policy has already committed to a capture target.
But an implementor often faces the reverse question:

- we want to keep a current shared-state batch of length `n` open,
- we need realized expected upside at least `m`,
- and we want the **smallest** timeout that makes that promise true.

That inversion is also closed form.

Let

- `state_prefix_bits = s`,
- `current_batch_length = n`,
- `arrival hazard = p`,
- `hold cost = c`,
- `target realized margin = m`.

From the earlier wait-value law, the asymptotic positive wait value is

- `s / (n(n+1)) - c / p`

whenever `p > 0`.

So the fixed-batch promise is feasible by timeout `T` exactly when

- `(1 - (1 - p)^T) * (s / (n(n+1)) - c / p) >= m`.

If the denominator is positive, divide through and get the real control variable:

- `required_capture = p * m / (p * s / (n(n+1)) - c)`.

That creates a clean decision ladder.

1. If `p * s / (n(n+1)) - c < 0`, the chosen batch is already negative even in the infinite-time limit.
2. If `p * s / (n(n+1)) - c = 0`, only target margin `0` is attainable.
3. If `required_capture > 1`, the target margin exceeds the asymptotic upside, so no timeout can rescue that batch.
4. If `required_capture = 1`, only `p = 1` gives a finite timeout; otherwise the target sits exactly on the asymptotic boundary and needs infinite patience.
5. If `0 <= required_capture < 1`, the minimum timeout is just the earlier arrival-only timeout law with `required_capture` substituted for `alpha`.

So future implementors can plan in either direction.

- Forward form: choose capture target first, then cap batch length.
- Reverse form: choose batch length first, then solve the minimum timeout.

These are exact duals of the same waiting economics.

Operationally, the reverse form is often the cheaper online primitive.
A scheduler can propose a batch length `n`, compute one scalar `required_capture`, and immediately know whether the request is

- impossible,
- asymptotic-only,
- or achievable at a specific finite timeout.

The same inversion gives an all-state guardrail by replacing `s` with the universal seven-bit lower envelope:

- `required_capture_universal = p * m / (p * 7 / (n(n+1)) - c)`.

So the inheritor now has both control surfaces needed for service design:

- **fix timeout target, recover admissible batch size**, or
- **fix batch promise, recover required timeout**.
