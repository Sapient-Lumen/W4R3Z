# Scenario — nightly doctest error code is code-level proof, not message-level proof

A crate uses nightly rustdoc error-number checks for a `compile_fail` example.
This proves the snippet still emits a particular error code, but it does not make the exact message/help text a stable contract.

Why it matters:
- rustdoc’s unstable doctest error-code feature is useful for code-level checks,
- the rustdoc book also says those codes are not guaranteed to be the only thing emitted from version to version,
- so the lane should usually classify this as `code_stable_shape_flexible`, not `exact_snapshot`.
