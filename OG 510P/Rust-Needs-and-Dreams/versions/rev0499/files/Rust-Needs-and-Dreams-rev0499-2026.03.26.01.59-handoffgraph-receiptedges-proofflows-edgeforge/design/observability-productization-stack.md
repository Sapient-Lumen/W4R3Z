## Execution addendum (rev0454)
For questions about **what the stack should actually ship once “Observability Contract is important” is no longer enough**, route to `design/observability-execution-blueprint-2026Q1.md`.

Interpretation rule:
- this stack still explains composition;
- the new execution blueprint now explains artifact family, proving lanes, and refusal shapes;
- and later revisions should use the stack plus the execution blueprint together rather than widening the stack prose alone.


## Rev0405 addendum — read this as an observability contract, not just a productization stack
This stack is now explicitly promoted as the archive's **Observability Contract** frontier.
Read it as the composition layer above `tracing`, `tracing-subscriber`, `tracing-log`, `metrics`, OpenTelemetry, Tokio Console, Cargo reports, and support/docs artifacts.

Interpretation rule:
- keep **diagnostic identity truth**, **signal/profile truth**, **activation/route truth**, **support/docs truth**, and **consumer handoff truth** visibly separate;
- do not let one exporter choice, one collector config, one dashboard, or one runtime probe silently become the whole observability story;
- and use `design/observability-contract-2026Q1.md` when deciding whether to deepen the production/runtime telemetry band next.

# Design: Observability Productization Stack (Diagnostic Surface + Observability + Runtime Settings + Support Envelope + Release / Incident imports)

## Goal
Turn observability into a **portable productization stack** instead of leaving each Rust project to express its telemetry and runtime-diagnostic contract as a tangle of subscriber layers, exporter environment variables, schema prose, vendor snippets, local Tokio Console setup, and dashboard folklore.

The stack should **not** replace `tracing`, `tracing-subscriber`, OpenTelemetry, Tokio Console, `metrics`, Cargo reports, incident tooling, or backend collectors.
It should make them compose better and make supported observability behavior reviewable.

Read this together with [`design/observability-lane-map.md`](./observability-lane-map.md): the productization layer sits **above** distinct lanes for tracing composition, local formatted diagnostics, legacy-log import, metrics recorders, OpenTelemetry export, runtime diagnostics, and imported machine reports.

## Why this note is needed now
Rust’s current signals say the missing problem is no longer “can Rust emit traces or metrics?”
They say the missing problem is **what a Rust project can honestly claim to emit, correlate, activate, support, and ship**:
- the 2025 State of Rust survey still says debugging remains an active productivity pain, while online docs remain the preferred canonical reference;
- `tracing-subscriber` is explicitly built around composable `Layer`s, which means real Rust observability is already layered rather than singular;
- `metrics` still presents itself as a facade with pluggable implementation choice, which means metrics posture is not automatically unified with tracing posture;
- OpenTelemetry Rust now documents traces, metrics, and logs together, but all three remain **Beta** in the language docs;
- the OpenTelemetry governance/stability proposal explicitly says complexity and lack of stability are barriers to production deployments;
- OpenTelemetry Weaver’s “observability by design” pitch explicitly says telemetry should be treated like a public API with validation and evolution discipline;
- Tokio Console already proves that runtime diagnostics can require their own protocol, subscriber layer, client tooling, and activation flags;
- Cargo’s structured-report work makes machine-readable runtime/build evidence more plausible as an imported lane rather than a side channel.

Together, those signals argue that the missing contribution is **not** another exporter helper, backend-specific bootstrap crate, or tracing convenience wrapper.
It is the **boring portable boundary above the ingredients**.

## Stack layers

### 1) Diagnostic Surface: declared failure and event identity truth
Diagnostic Surface owns the **declared identity layer**:
- stable diagnostic ids or classes;
- event/failure naming posture;
- route/job/task/domain attachment points;
- human-facing versus machine-facing renderings.

This layer answers questions like:
- “What failures or event families are part of the supported surface?”
- “Which names are durable enough for support, alerting, or runbooks?”
- “Which identities should appear in logs, spans, or reports?”

Design rule: **observability must not invent diagnostic identity from formatted strings after the fact**.

### 2) Observability Kit: signal/profile/report/vector truth
Observability Kit owns the **telemetry contract proper**:
- signal classes: traces / logs / metrics / runtime diagnostics;
- schema or semantic-convention subsets;
- required names, attributes, and correlations;
- runtime reports of effective export/config posture;
- validation vectors and packs.

This layer answers questions like:
- “What telemetry does the project claim to emit?”
- “Which fields or semantic conventions are guaranteed?”
- “Which runtime-diagnostic streams are part of the story?”

Design rule: **signal truth must not stay trapped in collector config, dashboard queries, or README examples**.

### 3) Runtime Settings: activation and export truth
Runtime Settings owns the **activation boundary**:
- exporter/backend selection;
- endpoint/auth/secret posture;
- environment and precedence rules;
- sampling, filtering, and redaction settings;
- dev-only versus CI versus production activation;
- runtime-specific gates such as Tokio Console enablement.

This layer answers questions like:
- “Which settings make telemetry actually happen?”
- “What differs between local, CI, and production profiles?”
- “Which parts are safe to expose in reports, and which need redaction?”

Design rule: **observability claims must not silently depend on undocumented env vars, hidden defaults, or local-only runtime flags**.

### 4) Support Envelope + DocProof: supported observability truth
Support Envelope and DocProof together own the **support/docs boundary**:
- support levels per signal/profile;
- stable versus best-effort or experimental lanes;
- checked docs/examples/transcripts for setup and validation;
- runtime-floor, platform, or feature-gate caveats;
- declared non-goals and unsupported profiles.

This layer answers questions like:
- “Is OTLP export really supported, or just shown in an example?”
- “Is Tokio Console a supported dev lane or an optional local trick?”
- “Which signals/profiles are stable enough for downstream consumers?”

Design rule: **one successful local telemetry demo is not a support contract**.

### 5) Release / Incident / Debuggability consumers
The stack matters when real consumers can import it honestly:
- **Release Pipeline** can attach observability packs to a shipped release;
- **Incident / Replay / Debuggability** consumers can start from declared telemetry and diagnostic truth instead of guessing from raw logs;
- **Service / Firmware / Media / Interactive / Agent / CLI** stacks can import observability posture without redefining signal truth;
- **Policy / Trust / Support** consumers can distinguish supported telemetry from experimental or local-only lanes.

Design rule: **consumers import selected observability facts; they do not redefine them into a fake universal health score**.

## What an epic contribution should look like in practice
A worthy contribution here is not “the one true Rust telemetry platform.”
It is a portable boring stack with clear boundaries:

1. **diagnostic identity first**
   - prove stable diagnostic/event identities can be attached before arguing about backends;
2. **signal/profile truth second**
   - prove logs/traces/metrics/runtime streams can be declared and validated as a reviewable subset;
3. **activation truth third**
   - prove exporter/endpoints/sampling/redaction/runtime gates can be attached without leaking secrets or flattening environments;
4. **support/docs truth fourth**
   - prove setup docs, local/CI/prod posture, and experimental lanes can be checked and attached honestly;
5. **consumer imports fifth**
   - prove release, incident, debugger, support, and productization consumers can reuse the same facts.

An eventual aggregate artifact may exist, but it should be a **thin linked pack of imported artifacts**, not a mega-schema that erases diagnostic identity, telemetry truth, activation truth, and support truth.

## Proposed aggregate artifact family
A plausible aggregate lane is:
- `obs-envelope/v0`
  - subject identity, selected profile, imported artifact pointers, and declared observability boundary;
- `obs-activation-report/v0`
  - effective runtime-setting/exporter posture with redaction-aware capture;
- `obs-diff-report/v0`
  - drift between two versions or two profile configurations;
- `obs-product-pack/v0`
  - thin bundle linking:
    - `obs-pack/v0`
    - diagnostic identity attachments
    - settings/export reports
    - support/docs attachments
    - optional release/incident/debug imports

The point is not one new truth engine.
The point is a **reviewable observability-as-product handoff**.

## Ranked first execution lanes
1. **tracing/log bridge lane**
   - best first exporter because many Rust projects already have `tracing`, `tracing-subscriber`, and `tracing-log` in some combination.
2. **OTLP profile lane**
   - proves logs/traces/metrics/schema truth can travel as a declared supported subset rather than collector folklore.
3. **runtime-diagnostic lane**
   - proves Tokio Console or other runtime-specific diagnostics can be attached honestly as capability-gated dev or support lanes.
4. **support and release lane**
   - proves observability can be shipped with docs/support posture instead of disappearing into example snippets.
5. **incident/debug consumer lane**
   - proves downstream tools can import the stack instead of rediscovering it from raw output.

## Non-goals
- a hosted backend or collector distribution;
- a universal quality score for telemetry;
- replacing `tracing`, OpenTelemetry, `metrics`, or Tokio Console;
- pretending traces/logs/metrics/runtime diagnostics are interchangeable;
- flattening signal truth, activation truth, and support truth into one fake “observability enabled” bit.

## Archive implications
- The archive should now treat **Diagnostic Surface + Observability + Runtime Settings + Support Envelope** as a coupled **Observability Productization Stack** in frontier and priority discussions, with Release / Incident / Debuggability as importing consumers and Service / Firmware / Media / Interactive / Agent / CLI as importing productization lanes.
- Future revisions should prefer **diagnostic identity, signal/profile truth, activation truth, support/docs truth, and consumer imports** over another exporter wrapper, dashboard integration, vendor SDK bootstrap, or runtime probe with no product boundary.
- When Service, Firmware, Media, Interactive, Agent, CLI, or Debuggability work cites observability readiness, it should import **diagnostic truth**, **signal truth**, **activation truth**, and **support truth** separately.

## Read this together with
- `gaps/observability-products-telemetry-runtime-diagnostics-and-support-contracts.md`
- `design/diagnostic-surface-kit.md`
- `design/observability-kit.md`
- `design/runtime-settings-kit.md`
- `design/support-envelope-kit.md`
- `design/docproof-kit.md`
- `design/debuggability-stack.md`
- `design/service-productization-stack.md`

## References (signals)
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- tracing-subscriber layers:
  https://docs.rs/tracing-subscriber/latest/tracing_subscriber/layer/index.html
- tracing-log:
  https://docs.rs/tracing-log/latest/tracing_log/
- metrics:
  https://docs.rs/metrics
- OpenTelemetry Rust docs:
  https://opentelemetry.io/docs/languages/rust/
- OpenTelemetry stability proposal:
  https://opentelemetry.io/blog/2025/stability-proposal-announcement/
- OpenTelemetry Weaver:
  https://opentelemetry.io/blog/2025/otel-weaver/
- OpenTelemetry SDK env vars:
  https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/
- Tokio Console:
  https://github.com/tokio-rs/console
- Cargo 1.94 structured reporting:
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- RustSec advisory for `opentelemetry-jaeger`:
  https://rustsec.org/advisories/RUSTSEC-2025-0123.html
