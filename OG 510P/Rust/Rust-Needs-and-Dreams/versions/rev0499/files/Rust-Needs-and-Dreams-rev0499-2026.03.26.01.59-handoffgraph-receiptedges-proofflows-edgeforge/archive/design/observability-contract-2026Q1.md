## Execution addendum (rev0454)
For questions about **what the archive's observability seam should actually ship once “telemetry and runtime diagnostics matter” is no longer enough**, read `design/observability-execution-blueprint-2026Q1.md` immediately after this note.

Interpretation rule:
- the broad observability frontier is unchanged;
- this revision says more explicitly what **Observability Contract** should become in theory and practice;
- **Build-State Evidence** remains the strongest one-project answer overall;
- **Feedback Loop / Debuggability Acceptance** remains the clearest under-ranked day-to-day missing middle;
- **Observability Contract** should now be understood as **reference layer + report/pack command + adapter/import corpus**;
- keep **diagnostic identity**, **signal/profile**, **activation/route**, **runtime-diagnostic capability**, **support/docs**, and **consumer handoff** distinct;
- and future observability syntheses should refuse the tempting wrong shapes first: one exporter route, one dashboard, one runtime probe, or one maturity score.

# Design: Observability Contract 2026Q1

## Goal
Promote the archive's runtime-telemetry substrate from “strong ingredients and good adjacent notes” to a first-class **Observability Contract**: a reviewable boundary for **what a Rust subject emits, how that emission is activated, what is actually supported, and what downstream consumers may conclude**.

This contract should sit:
- **above** raw `tracing` instrumentation, `tracing-subscriber` layer composition, `tracing-log` bridges, `metrics` recorders, OpenTelemetry exporter wiring, and Tokio Console runtime probes;
- **below** incident packs, replay packs, support playbooks, vendor dashboards, and release-policy decisions;
- and **beside** Debuggability, Runtime Settings, and Support Envelope rather than replacing any of them.

The point is not to standardize on one backend.
The point is to stop making service teams, operators, CI, support, and assistants rediscover observability truth from ad hoc subscriber stacks, environment variables, collector snippets, vendor dashboards, and README folklore.

## Why this seam matters now
The case for a first-class observability contract is sharper in 2026 than it was even a year ago:
- The 2025 State of Rust survey says resource usage is still high in the non-trivial-problems list, debugging remains a meaningful pain point, online docs remain the canonical reference, and editors with agentic support are rising. That combination raises the value of machine-readable runtime/diagnostic truth instead of prose-only setup.
- `tracing` continues to define itself as Rust's framework for structured, event-based diagnostics, while `tracing-subscriber` continues to make composition explicit through the `Layer` abstraction.
- `tracing-log` remains a bridge rather than a total replacement, which means real projects still mix logging and tracing lanes.
- `metrics` still presents itself as a facade whose consumer chooses the concrete recorder, which means metrics posture is intentionally plural rather than universally unified.
- OpenTelemetry's Rust docs now document traces, metrics, and logs together, but the current status table still marks all three signals as **Beta** for Rust.
- OpenTelemetry's governance/stability proposal says complexity and lack of stability are impeding production deployments.
- OpenTelemetry Weaver's “observability by design” work argues for semantic-convention validation and versioned telemetry schemas rather than post-hoc dashboard folklore.
- Tokio Console already proves that async runtime diagnostics need their own protocol, wire format, subscriber layer, activation gates, and clients.
- Cargo 1.94 and Cargo's unstable build-analysis/report work make machine-readable diagnostic/report flows more normal inside the Rust toolchain.
- The OpenTelemetry Rust ecosystem itself is clarifying route quality: OTLP is the default exporter in SDK env configuration and the opentelemetry-rust repo recommends OTLP for production scenarios, while `opentelemetry-jaeger` is now explicitly unmaintained.

That combination means the missing contribution is no longer “a nicer tracing helper”.
It is a **portable observability contract** that keeps signal/profile truth, activation truth, support truth, and consumer handoff truth separate.

## References (signals)
- 2025 State of Rust survey: debugging/resource-usage pressure, docs as canonical reference, agentic editors rising.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- `tracing` overview.
  https://docs.rs/tracing
- `tracing-subscriber` Layer abstraction.
  https://docs.rs/tracing-subscriber/latest/tracing_subscriber/layer/index.html
- `tracing-log` compatibility bridge.
  https://docs.rs/tracing-log/latest/tracing_log/
- `metrics` facade overview.
  https://docs.rs/metrics
- OpenTelemetry Rust docs and status table.
  https://opentelemetry.io/docs/languages/rust/
- OpenTelemetry logs concept page (language-status table still lists Rust logs as Beta).
  https://opentelemetry.io/docs/concepts/signals/logs/
- OpenTelemetry stability proposal.
  https://opentelemetry.io/blog/2025/stability-proposal-announcement/
- OpenTelemetry Weaver / observability by design.
  https://opentelemetry.io/blog/2025/otel-weaver/
- General SDK configuration (OTLP defaults).
  https://opentelemetry.io/docs/languages/sdk-configuration/general/
- opentelemetry-rust repo guidance (OTLP recommended for production scenarios).
  https://github.com/open-telemetry/opentelemetry-rust
- Tokio Console wire protocol and console-subscriber layer.
  https://github.com/tokio-rs/console
  https://github.com/tokio-rs/console/blob/main/console-subscriber/README.md
- Cargo 1.94 development cycle.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Cargo unstable build-analysis / `cargo report` docs.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- `opentelemetry-jaeger` unmaintained advisory.
  https://rustsec.org/advisories/RUSTSEC-2025-0123.html

## Working thesis
A worthy contribution here should make it easy to answer all of these without reading source code, collector configs, and dashboards side by side:
1. What **diagnostic identities** are stable enough to rely on: event families, span names, error classes, correlation keys?
2. What **signals and profiles** are actually part of the contract: traces, logs, metrics, runtime diagnostics, and which subsets of names/attributes are guaranteed?
3. What **activation route** is in effect: exporter selection, endpoints, sampling, redaction, dev-versus-prod posture, runtime-specific gates?
4. What is **supported** versus best-effort, experimental, or local-only?
5. What do downstream consumers — release packs, incident kits, support teams, CI, assistants — get to conclude from the observability posture?
6. What changed between releases or runtime profiles without flattening everything into one fake “telemetry health” verdict?

If the design cannot answer those questions, then Rust still lacks the production-facing observability contract layer it needs.

## Contract shape
Read the existing observability substrate as a contract with six visibly separate layers:

### 1) Diagnostic identity truth
What names, classes, and correlations are stable enough to matter:
- span/event/error family names
- durable ids or classes where available
- correlation keys and routing metadata
- source or domain attachment points

### 2) Signal / profile truth
What telemetry exists and what schema slice is promised:
- signal classes: traces / logs / metrics / runtime diagnostics
- semantic-convention profile or narrower schema subset
- required attributes and field names
- allowed aliases, deprecations, and migrations
- validation vectors for CI-scale checking

### 3) Activation / route truth
How the promised telemetry is actually turned on:
- exporter kind and protocol
- environment / code / collector route selection
- endpoints, auth posture, and redaction-aware capture
- sampling, filtering, and retention posture
- runtime-specific gates such as `tokio_unstable`, target filters, or console endpoints

### 4) Support / docs truth
What consumers are entitled to expect:
- supported dev / CI / prod profiles
- stable versus beta / experimental / local-only lanes
- checked docs, examples, and setup transcripts
- declared non-goals and unsupported combinations

### 5) Imported evidence truth
What machine-readable artifacts back the claim:
- lower-layer `obs-pack` or equivalent report bundles
- imported Cargo reports or runtime-diagnostic captures
- drift summaries and schema checks
- warnings for missing fields, unsupported routes, or deprecated exporters

### 6) Consumer handoff truth
How downstream systems are allowed to reuse the contract:
- release attachments
- incident / replay imports
- debugger / support imports
- CI policy inputs
- assistant-facing slices

## What the MVP should look like in theory
A realistic v0 is not “solve observability forever”.
It is:
- one schema family for identity, profile, activation, support, and product-pack composition;
- one `tracing`/`tracing-subscriber` proof;
- one OpenTelemetry/OTLP proof;
- one runtime-diagnostic proof (Tokio Console-style);
- and one consumer handoff proof into release or incident tooling.

Required artifacts:
- `obs-envelope/v0`
- `obs-activation-report/v0`
- `obs-support-report/v0`
- `obs-diff-report/v0`
- `obs-product-pack/v0`

Required rules:
- keep **signal/profile** distinct from **activation**;
- keep **activation** distinct from **support**;
- keep **runtime diagnostics** distinct from general traces/logs/metrics;
- keep **imported evidence** distinct from **consumer conclusions**;
- keep **vendor/backend choice** distinct from **portable observability truth**.

## What the MVP should look like in practice
### Pilot 1 — structured tracing + local formatted diagnostics
Show a Rust service that composes `tracing` with at least two layers: one human-readable local dev layer and one machine-facing export lane.

### Pilot 2 — OTLP-first production path
Show an OTLP-backed path that records the exact activation/export posture and warns when deprecated or unmaintained exporter routes are selected.

### Pilot 3 — runtime diagnostics as a declared capability
Show Tokio Console-style runtime diagnostics as an explicit capability with activation gates and consumer boundaries, not as “just more traces”.

### Pilot 4 — support/docs lane
Bundle checked docs/examples/transcripts so a support consumer can see what is officially supported in dev, CI, and prod.

### Pilot 5 — diff / handoff lane
Show a diff between two releases or runtime profiles that keeps schema drift, exporter drift, and support drift separate.

## Why this should be promoted instead of “just more debugging”
The archive already ranks **Debuggability** high, and that remains correct.
But the next sharpening move here is **not** debugger UX, trait diagnostics, or local repro by itself.

Why this promotion wins now:
- official/product signals are strongest on the gap between telemetry ingredients and supported product truth;
- the archive already has substrate in Diagnostic Surface, Observability, Runtime Settings, Support Envelope, Incident, and Replay notes;
- promoting the observability contract reduces the risk that one backend config, one dashboard, one OTel exporter choice, or one local runtime probe silently defines the whole production story.

So this revision promotes the **runtime telemetry / activation / support** seam, not observability as a hosted platform.

## Ranking impact
This does **not** reorder the archive's top band.
It adds one more explicit Tier A/Tier B bridge beneath the current frontier map:
- Build-State Evidence stays #1 overall.
- Adoption Navigation stays #2 overall.
- Debuggability stays high.
- Safety-Critical Assurance remains the clearest current high-assurance / evidence seam.
- Observability Contract becomes the clearest next **runtime telemetry / support / handoff-shaping** move.

That means it should sit below the broader build/debug/control-plane band, but above another round of backend-specific instrumentation wrappers or dashboard-first tooling.

## What not to build
Do **not** build:
- a hosted observability backend;
- a replacement for `tracing`, OpenTelemetry, `metrics`, or Tokio Console;
- a vendor-specific bootstrap helper pretending to be neutral;
- a universal “telemetry maturity score”;
- or a dashboard-first system that infers support promises from whatever happened to be emitted.

The winning contribution is thinner and more durable:
**publish explicit observability truth, publish activation truth, publish support truth, and hand that off honestly to multiple consumers without flattening the ecosystem into one backend.**
