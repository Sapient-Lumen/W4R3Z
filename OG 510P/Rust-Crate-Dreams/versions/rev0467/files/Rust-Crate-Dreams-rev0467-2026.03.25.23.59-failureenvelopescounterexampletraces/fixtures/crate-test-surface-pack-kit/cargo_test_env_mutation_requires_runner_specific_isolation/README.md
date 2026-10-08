# cargo_test_env_mutation_requires_runner_specific_isolation

This scenario freezes a common downstream-testing lie:

> “the helper only tweaks environment variables during tests, so it is isolated enough.”

That is not runner-neutral.
Rust's testing docs say `cargo test` runs tests in parallel by default and warn against shared state, while `std::env::set_var` is unsafe outside single-threaded programs on non-Windows platforms. nextest's process-per-test model changes that posture, but nextest explicitly says this reasoning does not apply back to `cargo test`.
