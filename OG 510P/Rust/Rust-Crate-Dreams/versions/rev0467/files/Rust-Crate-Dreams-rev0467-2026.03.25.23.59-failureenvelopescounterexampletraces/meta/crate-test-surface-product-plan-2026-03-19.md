# Crate test-surface product plan — 2026-03-19

This note exists to keep **P-0523 Crate Test Surface Pack Kit** disciplined.
The archive already decided that the missing value is a **receiver-facing fixture / fake-backend / deterministic-seam / scenario-topology contract**.
This refresh answers a narrower question:

> If somebody actually started building **P-0523** this week, what should version `0.1` look like now that Rust also has nextest record/replay, portable recordings, compile-fail harnesses, and richer snapshot-normalization substrate?

## Main judgment

A buildable `0.1` should still be a **small cargo subcommand plus library**.
But the center of gravity should now be slightly sharper:

- official fixture families,
- support levels,
- environment/topology requirements,
- scenario witnesses,
- **witness lineage**,
- and normalization boundaries.

The key change is that `0.1` should explicitly support **imported evidence** without confusing imported evidence with official support.

That means the crate should help maintainers publish one reviewable answer to:

- which fixtures, builders, fake backends, and helper modules are actually part of the crate’s intended support surface,
- which scenarios are representative enough to rely on,
- which seams exist for time, randomness, filesystem, network, environment, and process state,
- which topologies are intentionally supported for downstream tests,
- what host capabilities those topologies require,
- which scenario witnesses come from direct local runs versus imported runners or compile-fail harnesses,
- and what changed between releases.

It should **not** try to become a new test runner, mock framework, property-testing engine, snapshot system, or container orchestration tool.
Those are adjacent imports, not the product.

## What the crate should provide other people

For downstream users, release reviewers, and support engineers, the crate should provide:

1. **One compact downstream-testing contract** instead of folklore split across helper modules, README snippets, examples, CI YAML, and issue comments.
2. **A support-level policy** so teams can tell `officially_supported` apart from `best_effort_example`, `experimental`, or `manual_review_required`.
3. **A fixture catalog** so official builders, temp-state helpers, fake transports, transcript replayers, loopback harnesses, and test-only APIs are discoverable in one place.
4. **A deterministic-seam inventory** so users know whether time, randomness, environment variables, filesystem state, sockets, and process interaction can be controlled without patching internals.
5. **A topology/environment profile** so maintainers can state whether a scenario needs in-process-only setup, loopback networking, Docker, current-thread paused time, or real external credentials.
6. **A witness-lineage receipt** so another team can tell whether a scenario claim is backed by a direct local run, a compile-fail harness, a replayed CI recording, or only a manual-review claim.
7. **A normalization-boundary report** so stabilizers like redactions or sorted snapshot transforms stay visible instead of silently hiding semantics.
8. **A release diff** that makes hidden losses of test support loud.

For maintainers, the crate should provide:

1. a small pack file that is cheap to review,
2. explicit `manual_review_required` escape hatches instead of fake certainty,
3. a way to import existing helpers from `rstest`, Tokio, `wiremock`, `assert_cmd`, `tempfile`, `insta`, `proptest`, `trybuild`, `cargo-nextest`, and `testcontainers`,
4. one place to declare whether a recipe is a real supported contract or only imported evidence,
5. and a CI gate for “this release silently narrowed our test-support surface”.

## Recommended `0.1` command surface

### `cargo test-surface init`
Create a starter `test-surface-pack.toml` by importing obvious candidates from:

- maintainer-declared fixture modules,
- helper functions and fake backends,
- known async seams such as Tokio paused time,
- named example or docs scenarios when the maintainer opts in,
- selected adapters for `rstest`, `wiremock`, `assert_cmd`, `tempfile`, and `insta`,
- and optional imported evidence from `cargo-nextest` recordings or `trybuild` suites.

The generated pack should be incomplete on purpose.
Anything uncertain should be marked `manual_review_required` rather than guessed.

### `cargo test-surface capture`
Emit one normalized receipt bundle from a declared testing support workflow.
This should capture:

- fixture families,
- support levels,
- deterministic seams,
- scenario witnesses,
- topology classes,
- test-environment requirements,
- witness lineage,
- normalization boundaries,
- and imported evidence.

`capture` should work on imported artifacts too.
It must not require that every declared scenario executes in the same invocation.

### `cargo test-surface check`
Run the local validation pass:

- do declared fixtures still exist,
- do support-level policies parse,
- do named scenarios point at real fixtures or scenario assets,
- do topology classes agree with environment requirements,
- are paused-time claims compatible with runtime flavor and feature requirements,
- are imported runner/recording claims visibly marked as imported evidence,
- are snapshot normalization rules declared when determinism depends on redaction/sorting,
- and which parts remain manual-review-only?

### `cargo test-surface doctor`
Render human-facing warnings for suspicious situations such as:

- `example_recipe_presented_as_supported_fixture`
- `paused_time_claim_without_current_thread_runtime`
- `paused_time_claim_without_test_util`
- `containerized_peer_required_but_not_declared`
- `portable_recording_presented_as_local_recipe`
- `compile_fail_witness_presented_as_runtime_support`
- `snapshot_redaction_hides_semantic_field`
- `officially_supported_scenario_without_direct_or_imported_witness`
- `external_service_required_but_not_marked`
- `manual_review_required`

`doctor` should be a human-first renderer over captured artifacts, not a magical verifier.

### `cargo test-surface summary`
Render a short receiver-facing note for downstream docs or support runbooks.
A good summary answers:

- which fixtures and fakes are official,
- which seams exist,
- what host capabilities the recommended topologies require,
- what kind of witness backs each scenario,
- and where the recipe still begins with manual review.

### `cargo test-surface diff <old> <new>`
Compare two receipts or packs and classify:

- `support_level_changed`
- `fixture_added`
- `fixture_removed`
- `fake_backend_changed`
- `deterministic_seam_changed`
- `scenario_witness_changed`
- `witness_lineage_changed`
- `environment_requirement_changed`
- `integration_topology_changed`
- `normalization_boundary_changed`
- `manual_review_required`

### `cargo test-surface pack`
Emit one compact `.testsurface.zip` bundle for CI artifacts, release review, downstream support, or maintainer handoff.

## Recommended crate/workspace split

Keep the first implementation modular but not over-factored.
A good starting shape would be:

- `test_surface_model`
  - shared Rust types for packs, receipts, reports, manifests, policies, and diffs
- `test_surface_discovery`
  - import logic for fixture exports, fake backends, scenario assets, and known adapters
- `test_surface_check`
  - policy validation, doctor warnings, topology/requirements consistency, and drift checks
- `test_surface_import`
  - optional import logic for nextest recordings, trybuild suites, and snapshot metadata
- `test_surface_pack`
  - summary rendering, diff writing, markdown output, and zip bundle emission
- `cargo-test-surface`
  - user-facing CLI / cargo subcommand

Optional adapters should stay optional until the core vocabulary is trusted:

- `test_surface_rstest`
- `test_surface_tokio`
- `test_surface_proptest`
- `test_surface_wiremock`
- `test_surface_assert_cmd`
- `test_surface_insta`
- `test_surface_trybuild`
- `test_surface_nextest`
- `test_surface_testcontainers`

## `0.1` artifact set

The archive already had the right center of gravity.
`0.1` should still revolve around:

- `test-surface-pack.toml`
- `fixture-catalog.receipt.json`
- `fake-backend.report.json`
- `scenario-corpus.manifest.json`
- `property-strategy.report.json`
- `deterministic-seam.report.json`
- `snapshot-normalization.report.json`
- `integration-topology.manifest.json`
- `support-level.policy.json`
- `test-environment.requirements.json`
- `scenario-witness.receipt.json`
- `test-support-check.report.json`
- `test-surface-diff.report.json`
- `test-support.summary.md`

This refresh adds one more important review object:

- `witness-lineage.receipt.json` — records whether a scenario claim is backed by a direct run, a compile-fail harness, a portable recording, or some weaker imported/manual source.

That file matters because crate test support gets vague again if the archive records scenarios without recording **where the evidence really came from**.

## Discovery order

A disciplined import order helps prevent fake certainty.

1. **Declared pack facts**
   - `test-surface-pack.toml`
   - maintainer-declared fixture families, support levels, and topology classes
2. **Observed fixture exports**
   - helper modules
   - `rstest` fixtures
   - fake backend constructors
   - CLI test harnesses
3. **Deterministic seams and topology evidence**
   - Tokio paused-time claims
   - temp-state builders
   - mock HTTP / loopback / containerized peers
4. **Scenario witnesses**
   - named corpora
   - example assets
   - snapshot fixtures
   - property strategies
5. **Witness lineage**
   - direct local execution
   - compile-fail harnesses
   - portable recordings / replay imports
   - manual review zones
6. **Environment requirements**
   - Docker
   - loopback network
   - tempdir
   - env mutation
   - external credentials
7. **Manual review zones**
   - anything uncertain or overly inferred

The importer should prefer visible uncertainty over synthesis.

## 2026-03-20 addendum — isolation class and reset posture now need first-class receipts

The previous plan already had support levels, environment requirements, topology classes, witness lineage, and normalization boundaries.
The sharper missing layer now is **isolation honesty**.

A buildable next step should promote two more review objects:

- `isolation-class.receipt.json` — whether a helper or scenario is `per_call_fresh`, `per_test_fresh`, `process_shared`, `externally_shared`, `runner_isolated_only`, or `manual_review_required`;
- `reset-capability.receipt.json` — whether cleanup/reset is `os_cleanup`, `drop_cleanup`, `explicit_reset`, `best_effort_external_cleanup`, `no_reset_support`, or `manual_review_required`.

These objects are worth promoting because the current substrate now makes the difference concrete:

- `cargo test` still runs tests in parallel by default and warns against shared state;
- `std::env::set_var` is unsafe in multi-threaded non-Windows programs;
- nextest's process-per-test model explicitly changes the safety story for environment mutation;
- `wiremock` says `MockServer`s should not be shared between tests;
- `testcontainers` emphasizes self-contained isolated tests with scope-based cleanup;
- `tempfile` distinguishes OS-cleaned files from destructor-dependent directories/files.

### What the crate should provide other people now

1. **Isolation-class truth** — can I treat this fixture as fresh every time, only fresh per test, or only safe because the runner isolates processes?
2. **Runner-specific parallel-safety honesty** — is this safe under shared-process `cargo test`, only under `--test-threads=1`, or only under nextest?
3. **Reset/cleanup truth** — does cleanup come from the OS, from Drop, from an explicit reset API, or from best-effort external teardown?
4. **Contamination warnings** — can a helper mutate global env, current directory, filesystem paths, bound ports, or shared external state in ways that outlive one scenario?
5. **Diffable isolation drift** — did a release silently move a helper from per-test fresh to shared, or from explicit reset to best-effort cleanup?

### First schema pair to keep stable

#### `isolation-class.receipt.json`

A good first schema should let each record say:

- a `fixture_or_scenario` name,
- `isolation_class`,
- `runner_assumption` such as `cargo_test_shared_process`, `cargo_test_serial`, `nextest_process_per_test`, or `manual_review_required`,
- `parallel_posture` such as `parallel_safe`, `serial_only`, `runner_isolated_only`, `parallel_safe_with_unique_resources`, or `manual_review_required`,
- and `hazard_kinds` such as `env_global`, `cwd_global`, `fixed_path`, `fixed_port`, `shared_external_service`, or `manual_review_required`.

#### `reset-capability.receipt.json`

A good first schema should let each record say:

- a `fixture_or_resource` name,
- `reset_class`,
- whether cleanup is `automatic`, `scope_bound`, `explicit`, `best_effort`, or `none`,
- what `cleanup_trigger` applies,
- and any `contamination_window` or `notes` that remain relevant to downstream tests.

### First scenario families worth freezing

1. **Environment mutation is not generically parallel-safe under `cargo test`**
   - shared-process default run,
   - nextest process-per-test contrast,
   - and an explicit runner assumption.

2. **Per-test mock servers are isolated only if not shared**
   - fresh `wiremock::MockServer` per test,
   - explicit warning that sharing the server voids the isolation claim.

3. **Destructor cleanup is not the same as OS cleanup**
   - `tempfile()` versus `TempDir`/`NamedTempFile`,
   - and explicit reset posture when destructors do not run or cleanup is disabled.

### Working rule for future passes

Do **not** let this lane collapse into another generic serial-test helper, more CI plumbing, or another mock crate.
The sharper product boundary is now:

- what test support exists,
- how isolated it really is,
- what runner assumption that claim depends on,
- and how the state becomes clean again.
