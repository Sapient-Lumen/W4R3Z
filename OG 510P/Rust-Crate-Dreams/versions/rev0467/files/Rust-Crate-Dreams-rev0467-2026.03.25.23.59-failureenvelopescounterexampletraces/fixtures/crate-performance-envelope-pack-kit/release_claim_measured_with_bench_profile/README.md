# release_claim_measured_with_bench_profile

A crate advertises a `release_latency` scenario, but the only checked recipe uses `cargo bench` defaults.
The fixture exists to force the pack to record:

- that `cargo bench` uses the `bench` profile by default,
- that profiling-friendly debug info and production-fidelity settings can pull in different directions,
- and that a receiver-facing performance claim must say whether the measured scenario actually matches the release story it is used to justify.

Expected artifact pressure:
- `metric-authority.policy` should still allow `wall_time_ms` as the authoritative metric.
- `environment-fidelity.receipt` should classify the run as `profile_mismatch` unless the release-vs-bench claim is explicitly reconciled.
- `noise-class.report` should usually be `manual_review_required` or `comparative_only` until the profile story is made honest.
