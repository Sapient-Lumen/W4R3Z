# Frontier salience snapshot — 2026-03-17 (38)

This pass promoted a new cross-cutting crate lane:

- **P-0523 Crate Test Surface Pack Kit** — because the archive still had no good receiver-facing artifact for the most ordinary downstream question of all: *how am I supposed to test code that uses this crate?*

## Main judgment

The next worthy crate in the supportiveness frontier was **not** another test runner, mock framework, or container helper.
Those pieces already exist.
The sharper missing layer is the **crate-authored contract** for test support:

- official fixtures,
- fake backends,
- deterministic seams,
- named scenario corpora,
- topology expectations,
- and release-to-release diffs of that support surface.

That move is now better grounded because:

- the Rust vision-doc explicitly argues for more supportive interfaces from crates,
- the 2025 State of Rust survey says docs and code remain the main learning surfaces while debugging is still a real pain,
- Rust’s own docs make unit/integration testing structure explicit,
- Tokio documents paused time and testing helpers for async code,
- and the ecosystem already has strong slices like `rstest`, `proptest`, `wiremock`, `testcontainers`, `assert_cmd`, `tempfile`, and `insta`.

So the gap is no longer “Rust cannot test these things.”
The gap is that crates still rarely publish a **reviewable downstream-testing contract** above that substrate.

## What changed in the archive

Added:
- `proposals/crate-test-surface-pack-kit.md`
- `meta/crate-test-surface-lanes-2026-03-17.md`
- `fixtures/crate-test-surface-pack-kit/`
- `entries/2026-03-17-209.md`

Updated:
- `README.md`
- `INDEX.md`
- `meta/crate-frontier-map-2026-03-16.md`
- `meta/known-existing.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/llm-hygiene.md`

## What this pass deliberately did not do

It did **not** collapse:

- generic test frameworks,
- mock servers,
- property-testing engines,
- snapshot tools,
- containerized integration helpers,
- domain-specific conformance labs,
- and receiver-facing crate test-surface contracts

into one fake “Rust testing solved” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://doc.rust-lang.org/book/ch11-03-test-organization.html
- https://tokio.rs/tokio/topics/testing
- https://docs.rs/tokio-test/latest/tokio_test/
- https://docs.rs/rstest/latest/rstest/attr.fixture.html
- https://docs.rs/proptest/latest/proptest/arbitrary/index.html
- https://docs.rs/wiremock/latest/wiremock/
- https://docs.rs/testcontainers/latest/testcontainers/
- https://docs.rs/assert_cmd/latest/assert_cmd/
- https://docs.rs/tempfile/latest/tempfile/
- https://docs.rs/insta/latest/insta/
