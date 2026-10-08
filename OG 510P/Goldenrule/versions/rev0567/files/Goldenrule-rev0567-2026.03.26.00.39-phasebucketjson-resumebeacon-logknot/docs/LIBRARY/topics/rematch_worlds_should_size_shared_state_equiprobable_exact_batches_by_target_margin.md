# Rematch worlds should size shared-state equiprobable exact batches by target margin

The previous pass compressed the shared-state equiprobable exact transport story to seven affine expected-margin families. That already made it easy to *evaluate* the expected advantage of amortizing state transport across a batch.

This pass turns that evaluation law into a direct planning rule.

If a future inheritor wants at least `t` expected bits of advantage from `shared interval-state prefix once + local choice prefixes`, the minimum batch length is now available in closed form.

For any realized state family with affine expected margin

- `slope * n + intercept`,

use

- `max(1, ceil((t - intercept) / slope))`.

That removes the need to scan batch lengths at all.

On the current path the universal worst family is still the regular eight-bit interior singleton law `43n/9 - 8`, so the exact all-state guarantee becomes

- `ceil(9(t + 8) / 43)`.

That gives an inheritor a one-line batch-sizing rule for the equiprobable shared-state exact regime:

- target `0` or `1` expected bits universally: use batch length `2`,
- target `2` or `5` expected bits universally: use batch length `3`,
- target `10` expected bits universally: use batch length `4`,
- target `20` expected bits universally: use batch length `6`.

This rule is deliberately scoped.

- It is for the **equiprobable within-state exact-branch** model.
- It should not replace the earlier worst-case safe/strict threshold laws for adversarial or branch-sensitive batches.
- It is useful when planning around a desired savings target rather than merely asking whether amortization wins at all.
