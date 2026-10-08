# Scenario — release-plz / semver checks look green, but the workspace upgrade lane is still partial

This scenario freezes a common false-positive story for **P-0514**:

- a workspace uses `release-plz`,
- `cargo-semver-checks` reports no public API break for the published library crate,
- local dependency versions are updated across the workspace,
- but only the published library lane was actually witnessed.

Why it matters:

`release-plz` is valuable producer-side release substrate.
But a version bump across a workspace is **not** the same claim as “the downstream upgrade lane for every member, example, and binary was exercised”.

The example `package-scope.report` therefore keeps the distinction explicit:

- `core-lib` is the subject and was witnessed,
- `cli` is a binary companion and was only declared,
- `examples/demo` is example-only and was excluded,
- and manual review remains for binary/example startup paths.
