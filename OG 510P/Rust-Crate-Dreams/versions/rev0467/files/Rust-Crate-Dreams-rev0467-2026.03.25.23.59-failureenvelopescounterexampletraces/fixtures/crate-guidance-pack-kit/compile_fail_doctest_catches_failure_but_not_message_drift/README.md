# Scenario — compile_fail doctest catches failure but not message drift

A crate uses rustdoc `compile_fail` examples to prove a misuse still fails, but the actual compiler wording or replacement hint has changed.

Why it matters:
- rustdoc `compile_fail` is valuable proof that the bad example still fails,
- but it does **not** by itself prove that the emitted guidance is still the one users should trust,
- so the lane should usually classify this as `checked_failure_only` or `manual_review_required`, not `compiler_backed` across the whole recipe.
