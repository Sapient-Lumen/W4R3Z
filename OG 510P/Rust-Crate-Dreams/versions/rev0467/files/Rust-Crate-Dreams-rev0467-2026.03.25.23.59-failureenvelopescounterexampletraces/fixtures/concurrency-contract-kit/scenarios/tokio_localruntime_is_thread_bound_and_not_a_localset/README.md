# Scenario: Tokio `LocalRuntime` is thread-bound and not a `LocalSet`

This scenario proves that local-runtime support should not be flattened into generic local-context support.

The important facts are:
- `LocalRuntime` can drive `!Send` tasks without a `LocalSet`;
- it cannot be moved between threads or driven from different threads;
- and it is explicitly incompatible with `LocalSet`.
