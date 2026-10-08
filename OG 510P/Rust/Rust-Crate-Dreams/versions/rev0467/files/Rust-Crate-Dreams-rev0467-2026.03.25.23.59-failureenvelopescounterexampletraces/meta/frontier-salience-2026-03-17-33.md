# Frontier salience scan — 2026-03-17 (crate observability surfaces promoted as the operability-support lane)

This pass added a new top-level proposal: **P-0518 Crate Observability Surface Pack Kit**.
It sharpens the archive’s crate-ecosystem frontier by adding a tenth distinct supportiveness lane next to **P-0509** (task-first crate choice), **P-0510** (producer-side capability contracts), **P-0511** (shared interop profiles), **P-0512** (compile-time / early-failure guidance), **P-0513** (runtime handoff/support bundles), **P-0514** (release-to-release upgrade packs), **P-0515** (deprecation/successor off-ramp packs), **P-0516** (configuration/setup scenarios), and **P-0517** (performance envelopes).

## Main judgment

The strongest new cross-cutting contribution here is not:

- another tracing subscriber,
- another OpenTelemetry exporter,
- another schema linter,
- another redaction layer,
- another dashboard,
- or another “one-line telemetry init” facade.

It is the boring crate that can hand other people:

- one **observability pack**,
- one **signal-catalog receipt**,
- one **observability-surface report**,
- one **signal-cost report**,
- one **redaction-boundary report**,
- one **instrumentation-recipe manifest**,
- one **observability-check report**,
- and one **observability diff**.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0035 cargo-build-insights**
3. **P-0469 Cargo Rebuild Explanation Kit**
4. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
5. **P-0514 Crate Upgrade Pack Kit**
6. **P-0516 Crate Configuration Scenario Pack Kit**
7. **P-0517 Crate Performance Envelope Pack Kit**
8. **P-0518 Crate Observability Surface Pack Kit**
9. **P-0512 Crate Guidance Pack Kit**
10. **P-0513 Crate Runtime Handoff Pack Kit**
11. **P-0515 Crate Off-Ramp Pack Kit**
12. **P-0510 Crate Capability Contract & Interop Profile Kit**
13. **P-0511 Crate Interop Profile Pack Kit**
14. **P-0429 rustc_public Analysis Workbench Kit**
15. **P-0490 Cargo Lock Contention Witness Kit**

## Why P-0518 moved up

Fresh official and ecosystem signals line up around six sharper truths:

- The December 2025 vision-doc work explicitly recommends **supportive interfaces from crates**, and emitted telemetry is a real missing support surface for production adopters.
- The 2025 survey says **docs and code** are still the main learning surfaces, so observability support left in ops lore or issue comments remains under-specified.
- Tokio’s tracing docs and the `tracing` / `tracing-subscriber` docs show Rust already has rich structured diagnostics substrate, which means the missing value is not “Rust cannot emit telemetry”.
- OpenTelemetry semantic conventions exist precisely to make names and meanings consistent across codebases and platforms, which makes signal stability a real review surface.
- OpenTelemetry’s logs guidance says structured logs are preferred in production because stable schemas are easier to validate, correlate, and analyze.
- OpenTelemetry Rust still documents traces, metrics, and logs as beta, and its Rust instrumentation-libraries page still highlights a library-boundary fragmentation story rather than a single stable native-integration default.

That means the lane is both:

- **timely** — because the telemetry substrate is mature enough that the next missing value is signal-contract honesty,
- and **distinct** — because the missing value is a crate-authored observability surface above tracing/OTel plumbing and below org-wide telemetry governance.

## What changed in the archive

Added:
- `proposals/crate-observability-surface-pack-kit.md`
- `meta/crate-observability-surface-lanes-2026-03-17.md`
- `meta/frontier-salience-2026-03-17-33.md`
- `fixtures/crate-observability-surface-pack-kit/`
- `entries/2026-03-17-204.md`

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

- task-first crate choice,
- support / interop claims,
- shared ecosystem profiles,
- compile-time guidance,
- runtime handoff,
- upgrade packs,
- off-ramp packs,
- configuration scenarios,
- performance envelopes,
- tracing/OTel plumbing,
- telemetry schema governance,
- and full observability platforms

into one fake “Rust telemetry solved” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://tokio.rs/tokio/topics/tracing
- https://docs.rs/tracing/latest/tracing/
- https://docs.rs/tracing-subscriber/latest/tracing_subscriber/
- https://opentelemetry.io/docs/languages/rust/
- https://opentelemetry.io/docs/languages/rust/libraries/
- https://opentelemetry.io/docs/concepts/semantic-conventions/
- https://opentelemetry.io/docs/concepts/signals/logs/
