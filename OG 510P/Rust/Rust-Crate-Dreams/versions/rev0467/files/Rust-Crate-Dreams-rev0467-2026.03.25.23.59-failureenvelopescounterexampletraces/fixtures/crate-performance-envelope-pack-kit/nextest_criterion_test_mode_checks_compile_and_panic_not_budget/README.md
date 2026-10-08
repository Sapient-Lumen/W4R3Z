# nextest_criterion_test_mode_checks_compile_and_panic_not_budget

A crate runs Criterion benchmarks under `cargo nextest run --all-targets` in test mode.
That is useful because it checks that the benchmark target still compiles and does not panic.
It is **not** the same as a trusted performance measurement lane.

The fixture exists to force the pack to record:

- that test-mode evidence is still useful evidence,
- that `test`-profile / one-iteration runs should not silently inherit authoritative measurement meaning,
- and that execution intent belongs in a first-class artifact, not only in prose.
