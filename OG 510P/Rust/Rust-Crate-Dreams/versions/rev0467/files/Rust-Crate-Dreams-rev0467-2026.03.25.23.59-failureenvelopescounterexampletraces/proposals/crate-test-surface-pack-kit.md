---
id: P-0523
title: Crate Test Surface Pack Kit — fixture catalogs, fake-backend receipts, scenario corpora, and test-support diffs for library authors
status: idea
domains: [crates, dx, testing, fixtures, mocks, property-testing, integration-testing, supportiveness]
last_reviewed: 2026-03-20
evidence:
  - https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - https://doc.rust-lang.org/book/ch11-03-test-organization.html
  - https://doc.rust-lang.org/cargo/guide/tests.html
  - https://doc.rust-lang.org/cargo/reference/cargo-targets.html
  - https://tokio.rs/tokio/topics/testing
  - https://docs.rs/tokio-test/latest/tokio_test/
  - https://docs.rs/rstest/latest/rstest/attr.fixture.html
  - https://docs.rs/proptest/latest/proptest/arbitrary/index.html
  - https://docs.rs/wiremock/latest/wiremock/
  - https://docs.rs/testcontainers/latest/testcontainers/
  - https://docs.rs/assert_cmd/latest/assert_cmd/
  - https://docs.rs/tempfile/latest/tempfile/
  - https://docs.rs/insta/latest/insta/
  - https://docs.rs/trybuild/latest/trybuild/
  - https://nexte.st/docs/features/record-replay/
  - https://nexte.st/docs/design/why-process-per-test/
  - https://nexte.st/docs/configuration/env-vars/
  - https://doc.rust-lang.org/std/env/fn.set_var.html
  - https://nexte.st/docs/features/record-replay-rerun/portable-recordings/
  - https://docs.rs/assert_cmd/latest/assert_cmd/cargo/
  - https://docs.rs/wiremock/latest/wiremock/struct.MockServer.html
  - https://rust.testcontainers.org/system_requirements/docker/
  - https://docs.rs/tokio/latest/tokio/time/fn.pause.html
  - https://docs.rs/tokio/latest/tokio/attr.test.html
  - https://insta.rs/docs/redactions/
---

# Problem

The archive now has much better receiver-facing lanes for:

- choosing crates,
- understanding support claims,
- fitting interop profiles,
- getting compile-time guidance,
- handling runtime failure handoff,
- upgrading,
- leaving a crate,
- choosing setup scenarios,
- reasoning about performance posture,
- understanding observability surfaces,
- reviewing authority / determinism posture,
- reviewing lifecycle / shutdown behavior,
- reviewing resource / saturation posture,
- and reviewing persistence / durability posture.

It still lacks a good answer to a different but extremely common downstream question:

> “If I depend on this crate, what official fixtures, fakes, test builders, scenario corpora, and deterministic harnesses does it actually hand me so I can test *my* code without reverse-engineering its internals?”

That gap matters because today’s Rust testing substrate is real but scattered.

The December 2025 Rust vision-doc work explicitly recommends more **supportive interfaces from crates**.
The 2025 State of Rust survey says docs and code remain the main learning surfaces while debugging still remains a real productivity problem.
Rust’s own testing docs split the world into unit and integration tests, Tokio documents paused time and mock I/O for async tests, `rstest` provides fixture injection, `proptest` provides canonical strategies, `wiremock` covers HTTP mocking, `testcontainers` covers isolated integration environments, `assert_cmd` covers CLI assertions, `tempfile` covers throwaway filesystem state, `trybuild` covers compile-fail / diagnostic contracts, `cargo-nextest` now covers record/replay and portable recordings, and `insta` covers snapshot workflows and redactions.

But today that substrate still does **not** give maintainers one boring workflow for questions like:

- which test surfaces are officially supported versus “examples only”,
- whether the crate publishes stable test fixtures/builders or asks every downstream to hand-roll them,
- whether fake backends, paused clocks, mock I/O, temp-state builders, and transcript replayers are available,
- which scenario corpora are representative and which are illustrative only,
- whether property-testing strategies or snapshot normalizers are published,
- what integration environments are intentionally supported (pure in-process, ephemeral files, mock HTTP, containerized peer, external service),
- what kind of witness actually backs a scenario claim (direct run, compile-fail harness, imported portable recording, or manual review),
- and how the test-support surface changed across releases.

The worthy crate is therefore **not** another generic test runner, **not** another mock server, **not** another snapshot tool, and **not** another property-testing engine.
It is a **Crate Test Surface Pack Kit**: a crate that helps maintainers author, verify, diff, and export the receiver-facing testing support contract their crate gives other people.

# Main judgment

A worthy crate here should provide a receiver-facing answer to:

1. **What officially supported test surfaces exist for this crate?**
2. **Which fixtures/builders/fakes are public support contracts versus incidental examples?**
3. **What deterministic seams exist for time, filesystem, network, randomness, process state, and external services?**
4. **Which scenario corpora and example topologies are representative enough to rely on?**
5. **Which property strategies or snapshot normalizers exist for user-facing types and protocols?**
6. **What integration environments are intentionally supported for downstream tests?**
7. **What kind of witness lineage backs each scenario claim?**
8. **How did that test-support surface change across releases?**

That is more valuable than leaving users to reconstruct testing guidance from README snippets, examples folders, ad hoc helper modules, and issue threads.

## 2026-03-20 isolation / reset refinement

One more ordinary bluff is still available on top of the current testing substrate:

> a crate can publish fixtures, fake backends, and scenario witnesses, yet still leave downstream users unable to tell whether those surfaces are truly isolated per test, safe under shared-process parallel execution, or cleanly reset after use.

Current official and de facto standard surfaces make that sharper now than it used to be:

- `cargo test` still runs many tests in parallel threads inside the same test binary by default, and Rust's own book warns that tests must not depend on shared state such as files or environment variables;
- `std::env::set_var` is now unsafe outside single-threaded programs on non-Windows platforms, which makes “this helper mutates environment variables” an isolation claim, not just a convenience note;
- nextest's process-per-test model makes some environment-mutation workflows materially safer than shared-process `cargo test`, but nextest explicitly says this reasoning does **not** transfer back to `cargo test`;
- `wiremock` documents that each `MockServer` is isolated and should not be shared across tests;
- `testcontainers` documents self-contained, isolated integration tests with scope-based container cleanup;
- and `tempfile` distinguishes OS-cleaned temp files from `TempDir` / `NamedTempFile` cleanup that depends on destructors running.

That means the sharper missing crate layer is no longer only **fixture / fake / topology / witness** support.
It is also **isolation honesty**.

This pass therefore promotes two more first-class review objects for **P-0523**:

- `isolation-class.receipt.json` — whether a fixture or scenario is `per_call_fresh`, `per_test_fresh`, `process_shared`, `externally_shared`, `runner_isolated_only`, or `manual_review_required`, plus which runner assumptions make that statement true;
- `reset-capability.receipt.json` — whether cleanup/reset is `os_cleanup`, `drop_cleanup`, `explicit_reset`, `best_effort_external_cleanup`, `no_reset_support`, or `manual_review_required`.

A worthy crate here should now help other people answer not just “what test helpers exist?” but also:

- **can these tests run in parallel under `cargo test` without cross-test contamination?**
- **does this recipe only become safe under nextest's process-per-test model?**
- **is cleanup automatic because the OS owns it, because Drop owns it, because an explicit reset API exists, or only because a best-effort external teardown usually succeeds?**

# What it provides

- `test-surface-pack.toml` — versioned declaration of supported fixture families, fake backends, deterministic seams, integration topologies, and scenario corpora.
- `fixture-catalog.receipt.json` — observed receipt for exported test builders, temp-state constructors, fake services, mock traits, and helper modules.
- `fake-backend.report.json` — explicit classification such as `in_memory`, `record_replay`, `protocol_mock`, `ephemeral_fs`, `containerized_peer`, `loopback_server`, or `manual_review_required`.
- `scenario-corpus.manifest.json` — named scenario set with scope such as `happy_path`, `retry`, `timeout`, `backpressure`, `upgrade`, `crash_recovery`, `format_edge_case`, or `manual_review_required`.
- `property-strategy.report.json` — published property generators / shrinking posture for important user-facing types and workflows.
- `deterministic-seam.report.json` — explicit seam classifications for clock, randomness, filesystem, network, environment, and process isolation.
- `snapshot-normalization.report.json` — what unstable fields or ordering are normalized for snapshot tests, and what remains intentionally raw.
- `integration-topology.manifest.json` — supported topology classes such as `in_process_only`, `ephemeral_local_state`, `mock_http`, `real_socket_loopback`, `containerized_dependency`, `external_service_required`, or `manual_review_required`.
- `test-support-check.report.json` — verifies published fixtures and scenarios still build and still match declared support claims.
- `support-level.policy.json` — explicit meaning of `officially_supported`, `best_effort_example`, `experimental`, and `manual_review_required`.
- `test-environment.requirements.json` — host-capability requirements such as tempdir access, loopback network, Docker, paused time, or real external credentials.
- `scenario-witness.receipt.json` — ties named scenarios to the fixtures, seams, assets, and topologies that actually witness them.
- `witness-lineage.receipt.json` — records whether a witness came from a direct local run, compile-fail harness, portable replay artifact, or manual-review-only source.
- `isolation-class.receipt.json` — records whether a fixture/scenario is fresh per call, fresh per test, process-shared, externally shared, or only safe under a runner-specific isolation model.
- `reset-capability.receipt.json` — records whether cleanup/reset comes from the OS, Drop, explicit reset APIs, best-effort external teardown, or not at all.
- `test-surface-diff.report.json` — compares two releases and classifies `fixture_added`, `fixture_removed`, `fake_backend_changed`, `scenario_corpus_changed`, `property_strategy_changed`, `deterministic_seam_changed`, `integration_topology_changed`, `environment_requirement_changed`, `support_level_changed`, `witness_lineage_changed`, `isolation_class_changed`, `reset_capability_changed`, and `manual_review_required`.
- `test-support.summary.md` — short human-facing explanation of how downstream users should test code that depends on the crate.
- `cargo test-surface check` — run support fixtures and verify receipts against the pack.
- `cargo test-surface diff <old> <new>` — show how test-support promises changed.
- `cargo test-surface summary` — render a concise downstream testing guide.

# What the crate should provide other people

1. **A receiver-facing test-support contract** above examples folders, README snippets, and folklore.
2. **A fixture catalog** so teams can see the officially supported test builders, fake backends, temp-state helpers, and transcript replayers in one place.
3. **Deterministic seams** so downstream code can test clocks, retries, backoff, temp files, sockets, randomness, and process interaction without invasive patching.
4. **Scenario corpora** so common success/failure shapes stop being re-authored from scratch for every dependent crate.
5. **Property and snapshot support** so users know whether the crate publishes canonical generators, shrinkers, and normalization rules for complex outputs.
6. **Topology guidance** so people know whether they should test with pure in-process fakes, loopback servers, ephemeral files, containers, or real external services.
7. **Witness-lineage honesty** so users can tell “maintainer-supported local recipe” apart from compile-fail coverage or replayed CI evidence.
8. **Normalization-boundary honesty** so snapshot determinism helpers do not silently become semantic proof.
9. **Isolation-class truth** so teams can tell per-test freshness apart from shared-process helpers, externally shared peers, or nextest-only safety.
10. **Reset/cleanup truth** so destructor-based cleanup, OS cleanup, explicit reset APIs, and best-effort external teardown stop masquerading as the same thing.
11. **A diffable test surface** so release reviewers can spot when support for a fake backend or scenario family silently disappeared.
12. **Importable vocabulary** for docs portals, pathfinder tools, release review bots, and downstream integration guides.

# Persona / who it’s for

- library authors whose crates are used in larger applications and need better downstream testing support
- SDK/client maintainers who should publish official fake transports and scenario corpora
- runtime/framework maintainers who want pauseable time, temp-state builders, and loopback or in-memory adapters to be reviewable support artifacts
- downstream application teams trying to make integration tests deterministic and maintainable
- docs/tool authors who want stable testing artifacts instead of prose scraping

# Users & user stories

- **HTTP client maintainer**: “Publish one official fake transport, one wiremock recipe, and one retry/backoff scenario corpus so users stop guessing how to test failure modes.”
- **Database crate maintainer**: “Tell users whether they should test against an in-memory backend, tempdir-backed store, containerized peer, or real external server.”
- **CLI crate maintainer**: “Ship a binary-test recipe, temp-state fixture, snapshot normalization rules, and exit-code scenario corpus.”
- **Async service framework maintainer**: “Declare whether time can be paused, what mock I/O surface exists, and which shutdown or timeout scenarios are officially supported.”
- **Downstream integrator**: “Diff two releases and see whether the official fake backend changed or a key scenario corpus was dropped.”

# Prior art (and why it’s insufficient)

- Rust’s test organization docs distinguish unit and integration tests.
- Tokio documents paused time for async tests and offers dedicated testing helpers via `tokio-test`.
- `rstest` publishes reusable fixtures.
- `proptest` publishes `Arbitrary` / `Strategy` substrate for generated cases.
- `wiremock` publishes HTTP mocking for black-box tests.
- `testcontainers` publishes isolated containerized integration environments.
- `assert_cmd` helps test binaries.
- `tempfile` covers ephemeral filesystem state.
- `insta` covers snapshot testing and redactions/sorted redactions for stability.
- `trybuild` covers compile-fail and diagnostic testing.
- `cargo-nextest` now covers record/replay and portable recordings for exported run evidence.

What remains missing is a **crate-authored testing support contract workflow** above those pieces:

- author one per-crate test-support pack,
- classify which fixtures/fakes are stable support surfaces,
- freeze deterministic seams and topology expectations,
- verify representative scenarios still work,
- and diff that support surface across releases.

# Design principles

1. **Receiver-facing first** — optimize for downstream users of a crate, not only its maintainers.
2. **Support-claim honesty** — distinguish `officially_supported`, `best_effort_example`, and `manual_review_required`.
3. **Determinism over vibes** — if a crate claims pauseable time, fake transports, or isolated state, that should be checkable.
4. **Topology explicitness** — do not smuggle “requires Docker” or “needs real network” into tiny footnotes.
5. **Scenario-first** — publish named scenario corpora rather than vague “we test retries”.
6. **Small diffable artifacts** — make testing support reviewable release to release.
7. **Plural test styles** — unit, integration, property, snapshot, and replay styles can coexist.
8. **No forced framework monoculture** — support importing existing fixtures from `rstest`, `proptest`, `wiremock`, `testcontainers`, and custom helpers.

# Proposed architecture

## 1. Core model

### Pack file
`test-surface-pack.toml`

Sections:
- `crate`
- `fixture_family`
- `fake_backend`
- `deterministic_seam`
- `scenario_corpus`
- `integration_topology`
- `property_support`
- `snapshot_support`
- `notes`

### Receipts and reports
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
- `witness-lineage.receipt.json`
- `test-support-check.report.json`
- `test-surface-diff.report.json`

## 2. Capture layer

The crate should let maintainers record:
- exported test helpers,
- fake implementations or adapters,
- deterministic seams and knobs,
- example scenario bundles,
- supported integration environments,
- witness lineage from direct runs or imported evidence,
- normalization boundaries for stable snapshots,
- and release-to-release changes.

## 3. Verification layer

`cargo test-surface check` should verify:
- helper modules or features still exist,
- sample fixtures still compile,
- fake backends still satisfy declared capabilities,
- representative scenarios still run,
- property strategies still generate key types,
- and snapshot normalization rules still apply as declared.

## 4. Diff layer

`cargo test-surface diff` should classify:
- fixture added/removed,
- fake backend strengthened/weakened,
- deterministic seam added/removed,
- scenario corpus broadened/narrowed,
- topology requirement changed,
- property strategy changed,
- snapshot normalization changed,
- and manual-review-required deltas.

# Example artifact vocabulary

```toml
schema_version = "0.1"
crate = "example-sdk"

[[fixture_family]]
name = "temp_state_builder"
stability = "officially_supported"
kind = "ephemeral_fs"

[[fake_backend]]
name = "mock_transport"
class = "protocol_mock"
network = "not_required"

[[deterministic_seam]]
name = "clock"
class = "pauseable_time"

[[scenario_corpus]]
name = "retry_backoff"
coverage = ["timeout", "503", "eventual_success"]

[[integration_topology]]
name = "dockerized_peer"
class = "containerized_dependency"
required_for = ["wire_compat"]
```

# Thin-slice implementation plan

## 0.1
- schema + CLI that validates `test-surface-pack.toml`
- fixture catalog receipt
- fake-backend report
- integration-topology manifest
- diff tool for added/removed fixture families

## 0.2
- deterministic seam report
- scenario corpus manifest
- test-support summary renderer
- first import adapters for `rstest` fixture exports and `tokio::time` paused-time claims

## 0.3
- property-strategy report
- snapshot-normalization report
- import adapters for `proptest`, `wiremock`, `assert_cmd`, `tempfile`, and `insta`

## 0.4
- integration helpers for `testcontainers`
- richer capability classes for loopback versus external-service-required topologies
- release-to-release compatibility checks and stronger diff classification

# Package shape

- `testsurface-core` — core schemas, model types, validation.
- `testsurface-fixture` — fixture catalog helpers.
- `testsurface-determinism` — pauseable clock / temp-state / deterministic seam vocabulary.
- `testsurface-http` — fake backend and mock HTTP helpers.
- `testsurface-prop` — property support adapters.
- `testsurface-snapshot` — snapshot normalization helpers.
- `cargo-test-surface` — CLI.

## Feature flags
- `serde`
- `std`
- `tokio`
- `proptest`
- `wiremock`
- `testcontainers`
- `insta`
- `diff`

# Compatibility story

- Must work with declared-by-maintainer facts first; automatic inference is optional support, not the only path.
- Should import existing fixture/test helpers when possible instead of forcing a new test DSL.
- Should remain neutral about test frameworks and runtimes.
- Should integrate with authority/lifecycle/resource/persistence packs without collapsing into them.
- Should stay useful for pure library crates, async service crates, CLI crates, SDKs, parsers, and storage adapters.

# Conformance & fixtures

The crate should ship fixture families that exercise both declared and observed truth:

1. **HTTP/SDK client**
   - mock transport,
   - wiremock recipe,
   - retry/backoff corpus,
   - paused-time or fake-clock seam.

2. **CLI / local tool**
   - `assert_cmd` recipe,
   - tempdir-backed state,
   - snapshot normalization,
   - exit-code and stderr scenario corpus.

3. **Async protocol / runtime adapter**
   - mock I/O,
   - paused time,
   - loopback topology,
   - timeout/shutdown scenario corpus.

4. **Persistence-facing crate**
   - temp-state builder,
   - in-memory backend if present,
   - upgrade/recovery scenario corpus,
   - property strategy for key serialized types.

# Why this could be epic

Because it scales across an absurd range of crates while making a very ordinary and painful question boring:

> “How am I actually supposed to test code that uses this crate?”

If Rust wants supportive crate interfaces, test support is one of the least glamorous and highest-leverage places to cash that out.
A good crate here would not replace Rust’s testing ecosystem.
It would make crates publish a **reviewable testing contract** on top of it.
