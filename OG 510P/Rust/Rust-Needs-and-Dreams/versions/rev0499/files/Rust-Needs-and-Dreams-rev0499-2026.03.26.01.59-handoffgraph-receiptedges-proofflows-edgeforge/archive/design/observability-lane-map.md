# Design: Observability Lane Map (formatted diagnostics, tracing composition, log bridges, metrics facades, OpenTelemetry export, runtime diagnostics, and machine-report imports)

## Goal
Make the archive more precise about **what kind of observability claim is actually being made**.

Rust observability is strong, but the ecosystem still talks too often as if one phrase — “observability support” — names one coherent thing.
It does not.
A local `tracing_subscriber::fmt` layer printing human-readable events, a reloadable `EnvFilter` stack, a `tracing-log` bridge that absorbs `log` records, a `metrics` facade with its own recorder layers, an OTLP-facing OpenTelemetry pipeline, a Tokio-console runtime-diagnostics server, and imported Cargo machine reports are **different but connected** lanes.

The worthy contribution here is therefore not another exporter helper, backend bootstrap crate, or “one true telemetry stack”.
It is a **portable lane map and evidence boundary** that lets tools say which observability lane they are using, which semantics actually attach to it, where adapters are lossy, and which downstream consumers may reuse the claim honestly.

Read this together with:
- [`design/observability-kit.md`](./observability-kit.md)
- [`design/observability-productization-stack.md`](./observability-productization-stack.md)
- [`design/observability-productization-pilot-program.md`](./observability-productization-pilot-program.md)
- [`design/diagnostic-surface-kit.md`](./diagnostic-surface-kit.md)
- [`design/runtime-settings-kit.md`](./runtime-settings-kit.md)
- [`proposals/epic-observability-kit.md`](../proposals/epic-observability-kit.md)

## Why this note is needed now
The live Rust and OpenTelemetry signals line up around one conclusion: Rust needs a better **observability-surface contract**, not just more instrumentation glue.

- `tracing` still defines itself as a scoped, structured logging and diagnostics system for collecting structured, event-based diagnostic information, and it still explains that traditional log messages become hard to interpret in async systems like Tokio.
  https://docs.rs/tracing/latest/src/tracing/lib.rs.html
- `tracing-subscriber` still centers on the composable `Layer` abstraction rather than one fixed subscriber. Its `fmt` lane is explicitly about logging formatted representations of tracing events, `EnvFilter` is explicitly a `Layer`/`Filter`, and `reload::Layer` exists because runtime reconfiguration is its own surface.
  https://docs.rs/tracing-subscriber/latest/tracing_subscriber/layer/index.html
  https://docs.rs/tracing-subscriber/latest/tracing_subscriber/fmt/struct.Layer.html
  https://docs.rs/tracing-subscriber/latest/tracing_subscriber/filter/struct.EnvFilter.html
  https://docs.rs/tracing-subscriber/latest/tracing_subscriber/reload/struct.Layer.html
- `tracing-log` and `SubscriberInitExt` prove that legacy `log` compatibility is its own explicit lane. The docs still say `LogTracer` converts `log::Record`s into `tracing::Event`s, and `SubscriberInitExt` says enabling the `tracing-log` feature will also initialize a `log` compatibility layer.
  https://docs.rs/tracing-log/latest/tracing_log/
  https://docs.rs/tracing-subscriber/latest/tracing_subscriber/util/trait.SubscriberInitExt.html
- `metrics` remains a separate facade world. Its docs still define a single metrics API abstracting over the implementation choice, and `metrics-util` still defines recorder `layers`/`Stack` separately from the tracing-subscriber story.
  https://docs.rs/metrics
  https://docs.rs/metrics-util/latest/metrics_util/layers/index.html
- OpenTelemetry Rust still documents traces, metrics, and logs together, but the language docs still mark all three as **Beta**; the repository still recommends OTLP exporters for production scenarios; `opentelemetry-appender-tracing` explicitly converts `tracing` events into OpenTelemetry `LogRecords` and attaches trace context; and the OpenTelemetry governance side now says complexity and lack of stability are impeding production deployments while Weaver argues for observability-by-design through semantic-convention discipline.
  https://opentelemetry.io/docs/languages/rust/
  https://github.com/open-telemetry/opentelemetry-rust
  https://docs.rs/opentelemetry-appender-tracing
  https://opentelemetry.io/blog/2025/stability-proposal-announcement/
  https://opentelemetry.io/blog/2025/otel-weaver/
- Tokio Console still proves that runtime diagnostics are not just “more logs”. The `console-subscriber` README describes a dedicated `Layer`, a gRPC server, specific Tokio instrumentation requirements, and an explicit `tokio_unstable` gate.
  https://github.com/tokio-rs/console/blob/main/console-subscriber/README.md
- Cargo 1.94 now has an explicit structured-logging workstream. That is a strong signal that imported machine-readable reports belong in the observability conversation, but as **imports**, not as proof that build/runtime telemetry is unified.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- The RustSec advisory for `opentelemetry-jaeger` being unmaintained is another practical reason to keep exporter/profile lanes visible instead of flattening everything into “OpenTelemetry enabled”.
  https://rustsec.org/advisories/RUSTSEC-2025-0123.html

## The lane map

### Lane 1 — Structured tracing / subscriber-composition lane
**What it is**
- Core `tracing` spans/events plus layered subscriber composition.
- Registry, filters, span context, per-layer behavior, and runtime reconfiguration.

**Why it matters**
- This is the in-process semantic spine many Rust applications actually build on.
- It is where context propagation, filtering boundaries, and subscriber ordering become public behavior.

**What the archive should preserve**
- span/event identity posture,
- layer composition order,
- filter placement,
- reloadability,
- and whether the lane is human-only, machine-oriented, or both.

**What it should not pretend**
- that a tracing pipeline is already an exporter contract,
- that `fmt`, OTLP, and runtime diagnostics are interchangeable sinks,
- or that one subscriber stack generalizes across all Rust telemetry lanes.

### Lane 2 — Local formatted-diagnostics lane
**What it is**
- Human-readable terminal/file output using `fmt`, env filtering, and local-development ergonomics.
- Includes span-event formatting choices, local verbosity control, and rotation/writer posture when recorded.

**Why it matters**
- This is often the first lane users actually see.
- It is valuable even when no vendor-neutral export, metrics backend, or runtime console exists.

**What the archive should preserve**
- formatting mode,
- writer/sink posture,
- env-filter/default-filter behavior,
- local-dev versus shipped-support status,
- and whether runtime reconfiguration exists.

**What it should not pretend**
- that pretty local logs prove machine-readable telemetry,
- that formatted output preserves the full semantics of spans/events,
- or that a terminal-oriented lane is enough for release/support claims.

### Lane 3 — Legacy-log bridge lane
**What it is**
- `log`-ecosystem compatibility through `tracing-log`, subscriber init, or adjacent bridge layers.
- Importing dependency-emitted `log::Record`s into the tracing tree or other downstream consumers.

**Why it matters**
- Real Rust applications often depend on crates that still emit `log` records.
- Bridge posture changes initialization order, conflict rules, and what correlation is even possible.

**What the archive should preserve**
- whether the bridge is enabled,
- who owns logger initialization,
- lossiness of imported fields,
- initialization failure/conflict behavior,
- and whether the imported records enter the trace tree or only a flat output lane.

**What it should not pretend**
- that `log` and `tracing` are one native surface,
- that imported records gain full span semantics automatically,
- or that bridge activation is a minor implementation detail.

### Lane 4 — Metrics facade / recorder lane
**What it is**
- `metrics` macros, recorder selection, recorder-layer stacks, and metrics-only export or aggregation paths.

**Why it matters**
- The Rust metrics story is still materially distinct from the tracing-subscriber story.
- Units, histogram behavior, recorder installs, and export backends belong to this lane even when traces/logs also exist.

**What the archive should preserve**
- metrics facade versus direct backend API,
- recorder identity,
- layer stack,
- unit/name/profile choices,
- and whether correlation to traces/logs is native, bridged, or absent.

**What it should not pretend**
- that “OpenTelemetry supports metrics” makes the metrics facade irrelevant,
- that counter/gauge/histogram semantics are recoverable from general logs,
- or that a metrics lane proves full observability coherence.

### Lane 5 — OpenTelemetry export / semantic-profile lane
**What it is**
- Traces, metrics, and logs exported through OpenTelemetry APIs/SDKs and OTLP-oriented pipelines.
- Semantic-convention subsets, resource attributes, correlation policy, and backend/exporter profile.

**Why it matters**
- This is the main vendor-neutral machine-telemetry lane Rust teams reach for in production.
- It is also the lane where upstream stability, semantic-convention drift, and exporter choice are most visible.

**What the archive should preserve**
- signal set (traces/logs/metrics),
- Beta/stability posture,
- exporter profile (especially OTLP-first versus legacy exporters),
- semantic-convention/profile subset,
- resource attributes,
- and bridging choices such as `tracing-opentelemetry` or `opentelemetry-appender-tracing`.

**What it should not pretend**
- that all OpenTelemetry signals in Rust are equally mature,
- that traces/logs/metrics automatically share the same schema subset,
- or that a backend/exporter example proves a portable product boundary.

### Lane 6 — Runtime-diagnostic lane
**What it is**
- Runtime-specific task/resource diagnostics such as Tokio Console instrumentation.
- Dedicated protocol/server/client behavior, runtime-specific compile flags, and specialized async visibility.

**Why it matters**
- This lane captures things general traces/logs/metrics often do not: task state, wakeups, resource contention, and scheduler-facing runtime internals.
- It is extremely useful, but it is not the same claim as “production telemetry is configured”.

**What the archive should preserve**
- runtime family,
- required feature flags / cfg gates,
- server/client protocol posture,
- dev/CI/prod support level,
- and relation to the ordinary tracing/export pipeline.

**What it should not pretend**
- that runtime diagnostics are a transparent extension of logging,
- that Tokio-console support is backend-neutral,
- or that a local debugging lane is silently part of the shipped support contract.

### Lane 7 — Imported machine-report lane
**What it is**
- Structured Cargo or tool reports imported into observability-facing workflows.
- Build timings, structured logging, sessions, and other machine-readable reports attached as bounded evidence.

**Why it matters**
- Build/development telemetry increasingly matters to Rust users, and Cargo is growing the surfaces for it.
- But imported machine reports are still not the source of truth for application/runtime telemetry.

**What the archive should preserve**
- report producer,
- import boundary,
- freshness and scope,
- whether the report is runtime, build, or local-dev evidence,
- and what downstream correlation claims are actually supported.

**What it should not pretend**
- that Cargo reports are the same thing as service telemetry,
- that imported build evidence proves runtime observability,
- or that every machine-readable report belongs in the same pack by default.

## Adapter rules
A lane map becomes useful only if it names **lossy boundaries**.
The archive should therefore treat these as first-class adapter classes:

1. **tracing core ↔ local formatted diagnostics**
   - loses machine-schema completeness and often narrows the correlation surface to what the formatter renders.
2. **`log` records ↔ tracing events**
   - gains trace-tree placement but may still lose structure and initialization neutrality.
3. **metrics facade ↔ OpenTelemetry metrics export**
   - may lose recorder-specific behavior, naming/unit assumptions, or histogram/detail posture.
4. **tracing events ↔ OpenTelemetry logs/traces**
   - requires an explicit bridge choice and changes how events, spans, and correlation ids are represented.
5. **runtime diagnostics ↔ general telemetry**
   - loses task/resource-specific semantics unless the runtime lane is preserved as a separate capability.
6. **machine reports ↔ observability packs**
   - imports evidence with a distinct producer, freshness horizon, and scope; it does not magically become runtime telemetry.

## What should change elsewhere in the archive
- **Observability Kit** should remain the base artifact family, but it should now cite this lane map as the rule for what must stay separate.
- **Observability Productization Stack** should continue to couple Diagnostic Surface + Observability + Runtime Settings + Support Envelope, but it should stop flattening local output, export profiles, runtime diagnostics, and imported reports into one readiness claim.
- **Runtime Settings Kit** should own exporter/endpoints/filtering/redaction activation without re-owning metrics semantics or runtime-diagnostic protocol claims.
- **Debuggability Stack**, **Incident Kit**, **Replay Kit**, and **Service Productization Stack** should import selected observability lanes rather than narrating one hidden telemetry story of their own.
- **Cargo report / build-state work** should stay an imported evidence lane instead of becoming the implicit observability substrate.

## Strategic conclusion
The archive should now treat **Observability Kit** as a sharper frontier seam than it was before:
- lane maps should keep **tracing composition**, **formatted local diagnostics**, **legacy log bridges**, **metrics facades**, **OpenTelemetry export**, **runtime diagnostics**, and **imported machine reports** distinct;
- pilot programs should prove those lanes separately before speaking about “Rust observability support” in general;
- downstream consumers should import only the lane facts they can honestly reuse.

The worthy contribution here is therefore a thin `cargo obs` / `obs-pack/v0` layer whose lane profiles, activation reports, vector reports, and consumer handoffs make observability behavior reviewable without forcing one universal telemetry stack.
