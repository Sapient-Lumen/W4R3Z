# Scenario — lockfile v4 update path can raise authoring floor without raising build floor

This scenario exists to prove that **pinned-lockfile buildability** and **ongoing lockfile authoring support** are different promises.

## Situation

- the workspace still builds on an older supported toolchain from a committed/pinned lockfile;
- contributors on newer Cargo run `cargo update` or `cargo generate-lockfile`;
- lockfile v4 becomes the authoring format, which older toolchains cannot read;
- the maintainer wants the archive to report that distinction honestly instead of pretending the whole support promise either stayed clean or fully broke.

## Expected artifact truth

- `command-family-floor.report` keeps `build` separate from `update`, `generate_lockfile`, and `package`;
- `lockfile-floor.receipt` records the authoring action, the lockfile version, and the fact that the authoring floor is higher than the supported build floor;
- the scenario must not pretend that a green build from an existing lockfile proves compatibility for ongoing lockfile-authoring work.
