# Crate test-surface product plan — 2026-03-17

This note exists to keep **P-0523 Crate Test Surface Pack Kit** disciplined.
The archive already decided that the missing value is a **receiver-facing fixture / fake-backend / deterministic-seam / scenario-topology contract**.
This pass answers a narrower question:

> If somebody actually started building **P-0523** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps crate authors publish one reviewable answer to:

- which fixtures, builders, fake backends, and helper modules are actually part of the crate’s intended support surface,
- which test scenarios are representative enough to rely on,
- which seams exist for time, randomness, filesystem, network, environment, and process state,
- which topologies are intentionally supported for downstream tests,
- what host capabilities those topologies require,
- and what changed between releases.

It should **not** try to become a new test runner, mock framework, property-testing engine, snapshot system, or container orchestration tool.
Those are adjacent imports, not the product.

## What the crate should provide other people

For downstream users, release reviewers, and support engineers, the crate should provide:

1. **One compact downstream-testing contract** instead of folklore split across helper modules, README snippets, examples, and issue comments.
2. **A support-level policy** so teams can tell `officially_supported` apart from `best_effort_example`, `experimental`, or `manual_review_required`.
3. **A fixture catalog** so official builders, temp-state helpers, fake transports, transcript replayers, loopback harnesses, and test-only APIs are discoverable in one place.
4. **A deterministic-seam inventory** so users know whether time, randomness, environment variables, filesystem state, sockets, and process interaction can be controlled without patching internals.
5. **A scenario witness receipt** that ties named scenarios to real fixtures, seams, and topologies instead of vague prose like “we test retries”.
6. **An environment-requirements profile** so maintainers can state whether a scenario needs Docker, loopback networking, tempdir access, env mutation, clock pause, or a real external service.
7. **A short human summary** that can be pasted into downstream testing guides, support templates, and release notes.
8. **A release diff** that makes hidden losses of test support loud.

For maintainers, the crate should provide:

1. a small pack file that is cheap to review,
2. explicit `manual_review_required` escape hatches instead of fake certainty,
3. a way to import existing helpers from `rstest`, Tokio, `wiremock`, `assert_cmd`, `tempfile`, `insta`, `proptest`, and `testcontainers`,
4. one place to declare whether a mock recipe is only an example or a real supported contract,
5. and a CI gate for “this release silently narrowed our test-support surface”.

## Recommended `0.1` command surface

### `cargo test-surface init`
Create a starter `test-surface-pack.toml` by importing obvious candidates from:

- maintainer-declared fixture modules,
- helper functions and fake backends,
- known async seams such as Tokio paused time,
- named example or docs scenarios when the maintainer opts in,
- and selected adapters for `rstest`, `wiremock`, `assert_cmd`, `tempfile`, and `insta`.

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
- and imported evidence.

`capture` should work on imported artifacts too.
It must not require that every declared scenario executes in the same invocation.

### `cargo test-surface check`
Run the local validation pass:

- do declared fixtures still exist,
- do support-level policies parse,
- do named scenarios point at real fixtures or scenario assets,
- do topology classes agree with environment requirements,
- are “paused time” claims compatible with the runtime flavor,
- are fake backends and snapshot normalization rules still declared,
- and which parts remain manual-review-only?

### `cargo test-surface doctor`
Render human-facing warnings for suspicious situations such as:

- `example_recipe_presented_as_supported_fixture`
- `paused_time_claim_without_current_thread_runtime`
- `containerized_peer_required_but_not_declared`
- `snapshot_redaction_hides_semantic_field`
- `officially_supported_scenario_without_witness`
- `external_service_required_but_not_marked`
- `manual_review_required`

`doctor` should be a human-first renderer over captured artifacts, not a magical verifier.

### `cargo test-surface summary`
Render a short receiver-facing note for downstream docs or support runbooks.
A good summary answers:

- which fixtures and fakes are official,
- which seams exist,
- what host capabilities the recommended topologies require,
- and what kinds of scenarios the maintainer considers representative.

### `cargo test-surface diff <old> <new>`
Compare two receipts or packs and classify:

- `support_level_changed`
- `fixture_added`
- `fixture_removed`
- `fake_backend_changed`
- `deterministic_seam_changed`
- `scenario_witness_changed`
- `environment_requirement_changed`
- `integration_topology_changed`
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
- `test-support-check.report.json`
- `test-surface-diff.report.json`
- `test-support.summary.md`

This pass adds three more important artifacts:

- `support-level.policy.json` — what `officially_supported`, `best_effort_example`, `experimental`, `manual_review_required`, and `unknown` mean and what minimum evidence each class expects.
- `test-environment.requirements.json` — which host capabilities a scenario or topology assumes, such as Docker, loopback networking, tempdir access, env mutation, paused time, or real external credentials.
- `scenario-witness.receipt.json` — the declared or observed mapping from named scenarios to the fixtures, seams, assets, and topologies that actually witness them.

Those files matter because crate test support gets vague again if the archive only records fixtures and topologies but not:

- whether a recipe is truly supported,
- what host capabilities are required to execute it,
- and whether named scenarios are actually backed by runnable support artifacts.

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
5. **Environment requirements**
   - Docker
   - loopback network
   - tempdir
   - env mutation
   - external credentials
6. **Manual review zones**
   - anything uncertain or overly inferred

The importer should prefer visible uncertainty over synthesis.

## Support-level policy

The first implementation should treat **support levels as first-class review objects** and keep them separate from fixture kind or topology class.

### What should count as support levels in `0.1`

- `officially_supported`
- `best_effort_example`
- `experimental`
- `manual_review_required`
- `unknown`

### What should *not* be encoded as support levels in `0.1`

- “there is an example in the repo, therefore it is official”
- “the community usually uses wiremock, therefore the crate supports wiremock”
- “a container recipe exists in CI, therefore downstream users should depend on Docker”
- “snapshot tests happen to exist, therefore snapshot output is a stable support surface”

The support-level policy should be versioned and diffable.
If a maintainer cannot explain why a fixture or scenario is `officially_supported`, it should fall back to `best_effort_example` or `manual_review_required`.

## Environment-requirements policy

The first implementation should treat **host capabilities** as explicit review material.
A good `0.1` should model:

- `none`
- `tempdir_access`
- `env_mutation`
- `loopback_network`
- `docker_daemon`
- `paused_time_runtime`
- `real_external_service`
- `manual_review_required`

with optional notes such as:

- `credential_source`
- `cleanup_required`
- `ci_friendly`
- `parallel_safe`
- `platform_scope`

The crate should not pretend that all integration topologies are equally cheap or reproducible.
That distinction is exactly why the environment-requirements artifact needs to exist.

## Scenario-witness policy

The first implementation should treat **named scenarios** as explicit witnessed claims, not vague aspiration.

A good `0.1` should model:

- `fixture_refs`
- `seam_refs`
- `topology_refs`
- `asset_refs`
- `support_level`
- `witness_status`

with `witness_status` values such as:

- `observed`
- `declared_only`
- `sample_only`
- `manual_review_required`

The crate should allow a maintainer to say “we publish a retry scenario corpus, but only the mock transport and loopback witnesses are official” or “Docker is only required for wire-compat scenarios”.
That is more honest than a flat “we test retries”.

## Thin-slice scenario families that should ship with the archive

1. **Paused time claimed, but background work is still unowned**
   - Catch crates that claim deterministic timeout testing while spawned tasks or runtime flavor choices make that claim weaker than advertised.
2. **Mock HTTP recipe exists, but the official fake transport is different**
   - Distinguish a supported crate-authored fake backend from a community wiremock recipe.
3. **Containerized peer is optional for most tests but required for wire compatibility**
   - Keep “local fast tests” and “real peer fidelity” separate rather than pretending one topology covers both.

## What should wait until later

Save for `0.2+`:

- deep automatic fixture discovery across arbitrary macro-heavy test suites,
- broad execution orchestration across all declared scenarios,
- hosted dashboards,
- golden-output review UI,
- domain-specific conformance packs,
- and ambitious inference of support levels from CI alone.

The strongest first version is **small, explicit, diffable, and honest about uncertainty**.
