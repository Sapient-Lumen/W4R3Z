
## Rev0405 framing
This gap is now explicitly promoted as an **observability contract** gap, not merely “better telemetry setup”.
The missing contribution is the portable boundary between:
- **what a subject emits**,
- **how that emission is activated**,
- **what is actually supported**,
- and **what downstream consumers may conclude**.

# Gap: observability products still lack one honest product boundary

Rust has serious observability ingredients, but it still lacks a **portable productization layer for observability as a product surface**.

Today, teams assemble the truth from separate pieces:
- `tracing` spans and events;
- `tracing-subscriber` layer stacks;
- `tracing-log` compatibility bridges;
- `metrics` facade recorders and exporters;
- OpenTelemetry traces / metrics / logs and exporter setup;
- runtime-specific diagnostics such as Tokio Console;
- config/env sampling/exporter settings;
- redaction rules, docs, and runbooks hidden in README prose or deployment notes.

Those are all real surfaces, but the ecosystem still tends to collapse them into one vague claim:
> “we have tracing and metrics wired up, so observability is covered.”

That is no longer honest enough.

## Why this now matters more
Several current signals make the missing seam clearer than it used to be:

- The 2025 State of Rust survey still puts debugging in the active productivity-pain set, while also saying online docs remain the preferred canonical reference. That means observability and its support/docs posture are part of what users and operators really consume.
- `tracing-subscriber` is explicitly built around composable `Layer`s, and `tracing-log` explicitly treats `log` compatibility as a bridge rather than a total replacement. That means Rust observability already has multiple signal and bridge lanes in play.
- The OpenTelemetry Rust docs now document traces, metrics, and logs together, but all three are still marked **Beta** in the Rust language docs.
- The OpenTelemetry governance/stability proposal explicitly says project complexity and lack of stability are creating barriers to production deployments.
- OpenTelemetry Weaver’s “observability by design” pitch explicitly argues that telemetry should be treated like a versioned public API with validation and schema discipline.
- Tokio Console already proves that runtime/task diagnostics are useful enough to warrant their own protocol, subscriber layer, and activation requirements (`tokio_unstable`, target filters, separate client tooling).
- Cargo is actively adding structured machine-readable report flows (`cargo report timings`, `rebuild`, `sessions`), which makes attachable diagnostic/runtime evidence more realistic inside Rust tooling.
- The metrics ecosystem remains intentionally separate enough that `metrics` still presents itself as a facade rather than pretending one telemetry API owns everything.

Taken together, the missing problem is no longer “can Rust emit telemetry at all?”
The missing problem is:

**what can a Rust project honestly claim to emit, correlate, activate, validate, document, and support as an observability product surface?**

## What is missing
The ecosystem needs a portable layer that keeps these truths distinct but composable:

1. **Failure and event identity truth**
   - stable diagnostic ids or classes
   - route/job/task/span/event naming posture
   - correlation keys and boundary ids

2. **Signal/profile truth**
   - which traces / logs / metrics / runtime streams exist
   - semantic-convention or schema subset
   - required attributes and field names
   - validation vectors and drift reports

3. **Activation truth**
   - exporter/backend/profile selection
   - endpoint/auth/secret posture
   - sampling, filtering, redaction, and environment-specific config
   - runtime-specific activation such as Tokio Console or dev-only probes

4. **Support + docs truth**
   - what signals are supported in dev, CI, prod
   - what is stable versus best-effort or experimental
   - which docs/examples/transcripts are checked
   - what remains partial, gated, or unsupported

5. **Release / incident / consumer import truth**
   - what release attachment or pack corresponds to a shipped build
   - what incident, replay, debugger, or support systems may conclude
   - what remains advisory versus gating

## What this should not become
This should **not** become:
- a hosted observability vendor SDK in disguise;
- a prettier dashboard for one backend;
- a universal metrics/tracing facade that erases real differences;
- another exporter bake-off;
- a giant “telemetry maturity” score;
- or a replacement for `tracing`, OpenTelemetry, Tokio Console, `metrics`, or backend collectors.

The missing contribution is a **reviewable observability-as-product boundary** above the point tools.

## What a worthy contribution would look like
A real contribution here would define a thin artifact family and workflow that can:
- import `obs-pack` evidence, diagnostic identity, runtime-setting/exporter posture, and support/docs evidence;
- produce one honest observability-facing pack for release review and downstream consumption;
- diff two releases or two runtime profiles without flattening signal truth, activation truth, and support truth into one score;
- let tools answer questions like:
  - “what telemetry and runtime diagnostics does this project actually support?”
  - “which attributes/names are promises versus incidental output?”
  - “what changed in exporter/sampling/redaction/runtime activation?”
  - “is Tokio Console/dev runtime telemetry part of support or only a local debugging lane?”
  - “what exactly shipped, and what observability profile belonged to that release?”

## Likely shape of the solution
The strongest path is an explicit **Observability Productization Stack** that composes:
- **Diagnostic Surface Kit** for stable failure/event identity;
- **Observability Kit** for signal/profile/report/vector truth;
- **Runtime Settings Kit** for activation/exporter/secret/redaction posture;
- **Support Envelope + DocProof** for docs/support/runtime-floor truth;
- imports into **Release Pipeline**, **Debuggability Stack**, **Incident/Replay**, and productization stacks such as Service, Firmware, Media, Interactive, Agent, and CLI.

This would finally let the ecosystem talk about observability as a **supported product surface** rather than a pile of tracing layers, env vars, exporter defaults, and ops folklore.

## Why this belongs in the archive now
The archive already had a strong lower-layer Observability Kit.
What it did **not** have yet was the explicit synthesis saying that the next worthy contribution is likely **not** another tracing bridge, exporter wrapper, vendor bootstrap, or runtime probe.
It is the layer that joins those tools into one honest contract for what projects actually emit and support.

## References (signals)
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- tracing:
  https://docs.rs/tracing
- tracing-subscriber:
  https://docs.rs/tracing-subscriber
- tracing-log:
  https://docs.rs/tracing-log/latest/tracing_log/
- metrics:
  https://docs.rs/metrics
- OpenTelemetry Rust docs:
  https://opentelemetry.io/docs/languages/rust/
- OpenTelemetry stability proposal:
  https://opentelemetry.io/blog/2025/stability-proposal-announcement/
- OpenTelemetry Weaver / observability by design:
  https://opentelemetry.io/blog/2025/otel-weaver/
- OpenTelemetry SDK env/exporter selection:
  https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/
- Tokio Console:
  https://github.com/tokio-rs/console
- Cargo 1.94 development cycle:
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- opentelemetry-jaeger advisory:
  https://rustsec.org/advisories/RUSTSEC-2025-0123.html
