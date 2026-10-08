# Frontier salience snapshot — 2026-03-20 (121)

This pass did **not** open another test runner, serial-only helper, or generic state-isolation crate.
It deepened **P-0523 Crate Test Surface Pack Kit** by making another downstream-testing boundary explicit:

- **a crate can publish fixtures, fakes, deterministic seams, and even replayable witnesses while still leaving users unable to tell whether those surfaces are isolated under the runner they actually use, and whether state really resets afterward.**

## Main judgment

The sharper missing layer is no longer merely “fixture + fake + topology + witness lineage”.
The sharper missing layer is an **isolation-class / reset-capability contract**.

Current Rust testing signals make that specific:

1. Rust's own testing docs still say `cargo test` runs tests in parallel by default and warn against shared state such as files or environment variables.
2. `std::env::set_var` is now unsafe in multi-threaded non-Windows programs, turning environment mutation into an isolation claim instead of a harmless helper detail.
3. nextest explicitly uses process-per-test isolation and separately documents that this safety reasoning does not apply back to `cargo test`.
4. `wiremock` says each `MockServer` is isolated but should not be shared between tests.
5. `testcontainers` emphasizes self-contained isolated integration tests with scope-based cleanup.
6. `tempfile` distinguishes OS cleanup from destructor-dependent cleanup for `TempDir` / `NamedTempFile`.

That means the next worthy move is not another mock crate or CI replay surface.
It is one conservative crate family that can publish:

- **isolation-class truth**,
- **runner-specific parallel-safety truth**,
- **reset-capability truth**,
- and **contamination warnings** when those answers depend on shared-process `cargo test`, nextest, Drop, or external-daemon teardown.

## Why this beat nearby work

The archive already had adjacent lanes for:

- generic test substrate,
- witness lineage and imported evidence,
- deterministic seams,
- topology manifests,
- and environment requirements.

What it still lacked was one compact way to say:

- “this helper is only honest under nextest, not shared-process cargo test,”
- “this mock server is isolated only when each test creates its own instance,”
- and “this temp-state helper cleans up on Drop, which is not the same promise as OS-owned cleanup.”

That is a real receiver-facing product boundary, not another wrapper around existing test tools.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strongest because better crate choice compounds across the rest of the stack.
2. **P-0514 Crate Upgrade Pack Kit** — still unusually strong because release-to-release truth remains broadly under-specified.
3. **P-0523 Crate Test Surface Pack Kit** — materially stronger after this pass because the ecosystem now has enough runner/isolation substrate to make contamination truth explicit instead of folkloric.
4. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because shutdown and timeout aftermath truth remain widely under-served.
5. **P-0017 Trust Lens** — still unusually strong because reviewable trust posture is newly more buildable.
6. **P-0470 Cargo Package Review Kit** — still unusually strong because raw archive authority and extraction truth remain distinct.
7. **P-0036 MSRV Workspace Lab** — still unusually strong because Cargo policy/resolver/lockfile support remains easy to overclaim.
8. **P-0451 Cfg Availability Ledger Kit** — still unusually strong because docs-visible truth remains weaker than usable-support truth.

## What changed in the archive

Added:
- `entries/2026-03-20-301.md`
- `meta/frontier-salience-2026-03-20-121.md`
- `meta/crate-test-surface-isolation-boundaries-2026-03-20.md`
- `fixtures/crate-test-surface-pack-kit/isolation-class.receipt.schema.json`
- `fixtures/crate-test-surface-pack-kit/reset-capability.receipt.schema.json`
- scenario families for runner-specific env mutation safety, per-test mock-server freshness, destructor cleanup posture, and scope-based container cleanup

Updated:
- `README.md`
- `INDEX.md`
- `proposals/crate-test-surface-pack-kit.md`
- `meta/crate-test-surface-product-plan-2026-03-19.md`
- `fixtures/crate-test-surface-pack-kit/README.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`

## Main judgment after the pass

A worthy crate test-surface contribution for Rust should now provide more than supported fixtures, topologies, and scenario witnesses.
It should provide:

- one explicit **isolation-class receipt**,
- one explicit **reset-capability receipt**,
- and one honest way to keep runner assumptions, contamination risk, and cleanup mechanism from masquerading as one general “test support” story.

## Freshness anchors

- Rust book, controlling tests — https://doc.rust-lang.org/book/ch11-02-running-tests.html
- `std::env::set_var` — https://doc.rust-lang.org/std/env/fn.set_var.html
- nextest process-per-test — https://nexte.st/docs/design/why-process-per-test/
- nextest environment variables / safety — https://nexte.st/docs/configuration/env-vars/
- `wiremock::MockServer` — https://docs.rs/wiremock/latest/wiremock/struct.MockServer.html
- `testcontainers` crate docs — https://docs.rs/testcontainers/latest/testcontainers/
- `tempfile` crate docs — https://docs.rs/tempfile/
