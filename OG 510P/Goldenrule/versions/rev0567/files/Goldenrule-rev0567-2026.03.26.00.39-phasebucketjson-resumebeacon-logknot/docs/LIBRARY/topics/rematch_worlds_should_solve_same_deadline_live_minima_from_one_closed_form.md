# Rematch worlds should solve same-deadline live minima from one closed form

Future inheritors should not compute positive same-deadline stateless live minima in two conceptual stages when the archive already supplies an exact direct formula.
The earlier passes established that:
- a positive blind-commit promise with required capture `alpha` needs minimum timeout `ceil(log(1 - alpha) / log(1 - p))`, and
- the matching same-deadline live minimum is the odd image `2K - 1` of that blind minimum timeout `K`.

Those two steps collapse into one exact controller rule.

## Exact direct formula

Let

- `delta = p * state_prefix_bits / (n(n + 1)) - hold_cost`, and
- `alpha = p * margin_floor / delta` whenever `delta > 0`.

Then the minimum nominal deadline of a same-deadline stateless live controller is exactly:

- `1` when `margin_floor = 0`, because immediate close already preserves the promise,
- `1` when `p = 1` and `alpha <= 1`, because certain arrival captures the full asymptotic upside immediately,
- `2 * ceil(log(1 - alpha) / log(1 - p)) - 1` when `0 < alpha < 1` and `p < 1`,
- **no finite deadline** when `alpha = 1` and `p < 1`, because the target equals the asymptotic upside,
- and **impossible** when `delta <= 0` or `alpha > 1`.

So the inheritor can solve the positive same-deadline live minimum directly from batch length, hazard, hold cost, promised margin, and shared-prefix bits without first materializing an intermediate timeout object.

## All-state guardrail

The seven-bit all-state guarantee uses the exact same formula with `state_prefix_bits = 7`.
That means a universal controller can test positive promise admission from the same direct formula, just against the lower envelope instead of a realized state.

## Operational consequence

A same-deadline live controller can be compiled from primitives in one pass:

1. compute `delta`,
2. classify the context as zero-floor, finite, asymptotic-only, or impossible,
3. if it is finite, emit the odd nominal deadline from the direct formula,
4. and treat every even deadline as a redundant duplicate of the odd rung below it.

This keeps the implementation surface smaller and makes the positive-promise admission path easier to audit.
