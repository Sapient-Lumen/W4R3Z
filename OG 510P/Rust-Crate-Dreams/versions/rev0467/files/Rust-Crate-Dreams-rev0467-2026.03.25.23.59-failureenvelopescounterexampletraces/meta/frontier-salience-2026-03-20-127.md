# Frontier salience snapshot — 2026-03-20 (127)

This pass did **not** promote another subscriber/exporter, another org-wide telemetry platform, or another profiling/backend lane.
It deepened **P-0518 crate-observability-surface-pack-kit** by making a more boring and more reusable boundary explicit:

- **a crate can truthfully document signals and routes while still leaving other teams unable to tell whether those routes are lossy, sampled, periodically aggregated, or dependent on clean shutdown / `force_flush`.**

## Main judgment

The sharper missing layer is no longer merely “which signals exist and where do they go?”.
The sharper missing layer is a **delivery-posture / completeness-class contract** above signal catalogs, activation recipes, bridge routes, and redaction rules.

Current observability substrate makes that specific:

1. Tokio’s tracing docs still frame `tracing` as structured event-based diagnostics substrate, not as a delivery-guarantee model.
2. `tracing_appender::non_blocking` still defaults to lossy buffering, exposes dropped-line counters, and relies on `WorkerGuard` for clean exit flushing.
3. `SdkTracerProvider` and `SdkLoggerProvider` still expose explicit `force_flush` / shutdown semantics for remaining buffered telemetry.
4. OpenTelemetry sampling docs are explicit that sampled-versus-not-sampled is literally the difference between processed/exported and not processed/exported.
5. OpenTelemetry metrics docs still describe measurements as aggregated in memory and exported periodically.
6. The OpenTelemetry Rust library-instrumentation docs still keep the library/app boundary real, which means crate authors need a better way to say what delivery/completeness story they are actually shipping.

That means the next worthy move is not another exporter or queue.
It is one conservative crate family that can publish:

- **delivery-posture truth**,
- **completeness-class truth**,
- plus the already-needed signal / activation / route / schema / sensitivity surfaces.

## Why this beat nearby work

The archive already had adjacent lanes for:

- telemetry plumbing,
- profiling and memory observability,
- diagnosis support,
- performance envelopes,
- and org/backend governance.

What it still lacked was one compact way to say:

- “this log route is real, but lossy under pressure,”
- “this trace route is official, but sampled,”
- “this metric route is official, but aggregated-window rather than per-event,”
- and “this exit path needs `WorkerGuard` or `force_flush` before another team should call it complete.”

That is a real receiver-facing product boundary, not just another telemetry tool.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still strongest because better crate choice compounds across the rest of the stack.
2. **P-0514 Crate Upgrade Pack Kit** — still unusually strong because release-to-release truth remains broadly under-specified.
3. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because shutdown and timeout aftermath truth remain broad pain points.
4. **P-0523 Crate Test Surface Pack Kit** — still unusually strong because downstream test-support truth remains under-served.
5. **P-0518 Crate Observability Surface Pack Kit** — materially stronger after this pass because route truth now looks incomplete without delivery/completeness truth.
6. **P-0474 cargo-config-layer-receipt-kit** — still strong because Cargo config is now a real operational support surface.
7. **P-0124 schema-compatibility-workbench-kit** — still unusually strong because schema engines exist but one shared review contract above them still does not.
8. **P-0017 Trust Lens** — still unusually strong because reviewable dependency-trust posture is newly more buildable.
9. **P-0037 secrets-kit** — stronger after its contract pass, but still slightly narrower than the cross-project observability gap.
10. **P-0121 ffi-boundary-conformance-kit** — still important and sharper, but should remain boundary-contract-first.

## What changed in the archive

Added:
- `entries/2026-03-20-307.md`
- `meta/frontier-salience-2026-03-20-127.md`
- `meta/crate-observability-surface-product-plan-2026-03-20.md`
- `meta/crate-observability-surface-delivery-boundaries-2026-03-20.md`
- `fixtures/crate-observability-surface-pack-kit/delivery-posture.receipt.schema.json`
- `fixtures/crate-observability-surface-pack-kit/completeness-class.report.schema.json`
- scenario families for lossy nonblocking logs, batch-export flush dependence, and periodic metrics

Updated:
- `README.md`
- `INDEX.md`
- `proposals/crate-observability-surface-pack-kit.md`
- `fixtures/crate-observability-surface-pack-kit/README.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`

## Main judgment after the pass

A worthy observability-support contribution for Rust should now provide more than signal/activation/route/schema/redaction artifacts.
It should also provide:

- one explicit **delivery-posture receipt**,
- one explicit **completeness-class report**,
- and one honest separation between **route existence** and **what another team may rely on from that route**.

## Freshness anchors

- Tokio tracing topic — https://tokio.rs/tokio/topics/tracing
- `tracing-appender` nonblocking docs — https://docs.rs/tracing-appender/latest/tracing_appender/non_blocking/
- `WorkerGuard` docs — https://docs.rs/tracing-appender/latest/tracing_appender/non_blocking/struct.WorkerGuard.html
- `ErrorCounter` docs — https://docs.rs/tracing-appender/latest/tracing_appender/non_blocking/struct.ErrorCounter.html
- `SdkTracerProvider` docs — https://docs.rs/opentelemetry_sdk/latest/opentelemetry_sdk/trace/struct.SdkTracerProvider.html
- `SdkLoggerProvider` docs — https://docs.rs/opentelemetry_sdk/latest/opentelemetry_sdk/logs/struct.SdkLoggerProvider.html
- OpenTelemetry sampling docs — https://opentelemetry.io/docs/concepts/sampling/
- `opentelemetry` metrics docs — https://docs.rs/opentelemetry/latest/opentelemetry/
- `tracing-opentelemetry` metrics layer docs — https://docs.rs/tracing-opentelemetry/latest/tracing_opentelemetry/struct.MetricsLayer.html
- `opentelemetry-appender-tracing` docs — https://docs.rs/opentelemetry-appender-tracing/latest/opentelemetry_appender_tracing/
- OpenTelemetry Rust instrumentation libraries docs — https://opentelemetry.io/docs/languages/rust/libraries/
