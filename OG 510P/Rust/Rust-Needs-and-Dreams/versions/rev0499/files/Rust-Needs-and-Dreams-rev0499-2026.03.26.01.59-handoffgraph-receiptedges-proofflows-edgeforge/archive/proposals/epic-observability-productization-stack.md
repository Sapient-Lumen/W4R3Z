## Execution addendum (rev0454)
This proposal now sits beneath an explicit seam-local execution answer.
Read `design/observability-execution-blueprint-2026Q1.md` before widening this epic further so the proposal stays anchored to identity/profile/activation/runtime-capability/support/handoff truth rather than drifting toward one backend, one dashboard, or one maturity score.


## Rev0405 promotion note
This proposal now sits under the explicit **Observability Contract** frontier.
Treat it as the clearest next **runtime telemetry / support / handoff-shaping** move rather than another exporter wrapper, backend bootstrap, or dashboard integration.

# Epic proposal: Observability Productization Stack

## Problem
Rust projects increasingly have logs, spans, metrics, runtime probes, and exporter setup, but they still lack one honest way to review observability as a **supported product surface**.

Today, maintainers, operators, support teams, and downstream tools often reconstruct that truth from:
- subscriber-layer code;
- env-var conventions;
- collector snippets;
- dashboard assumptions;
- local Tokio Console setup;
- and README prose.

That is enough to demo observability.
It is not enough to ship or support it.

## Proposal
Build a thin composition layer above existing archive pieces:
- **Diagnostic Surface Kit**
- **Observability Kit**
- **Runtime Settings Kit**
- **Support Envelope + DocProof**
- optional imports into **Release Pipeline**, **Debuggability Stack**, **Incident/Replay**, and domain productization stacks

The result should be an **Observability Productization Stack** that can describe:
- what telemetry and runtime diagnostics exist;
- what names/attributes/correlations are promised;
- how exporters/sampling/redaction/runtime gates are activated;
- what is supported versus best-effort or experimental;
- and what release/incident/debug consumers may conclude.

## Candidate artifact family
- `obs-envelope/v0`
- `obs-activation-report/v0`
- `obs-diff-report/v0`
- `obs-product-pack/v0`

These should remain **thin linked artifacts**, not a new mega-schema.

## Reference CLI shape
- `cargo obs product export`
  - emit `obs-envelope/v0` for one selected subject/profile
- `cargo obs product activate`
  - emit `obs-activation-report/v0` from imported settings/runtime evidence
- `cargo obs product diff --against <ref|version|profile>`
  - emit `obs-diff-report/v0`
- `cargo obs product pack`
  - produce `obs-product-pack/v0`
- `cargo obs product verify-pack <path>`
  - verify schema versions, checksums, redaction rules, and imported-attachment integrity

This should stay a **thin composition layer**.
It should not replace the lower-layer kits.

## What `obs-product-pack/v0` should contain
- `manifest.json`
- `obs-envelope.json`
- `obs-activation-report.json`
- optional `obs-diff-report.json`
- imported `obs-pack` pointer or embedded attachment
- imported diagnostic identity attachments
- imported runtime-settings/exporter reports
- imported support/docs attachments
- checksums, provenance, and generator identity
- optional release/debug/incident import pointers

## Design principles
- **Observability is a product surface, not just backend plumbing.**
- **Thin imports over new truth engines.**
- **Diagnostic identity, signal truth, activation truth, and support truth remain distinct.**
- **Runtime diagnostics are capability-gated, not assumed.**
- **Release and incident consumers import the stack; they do not redefine it.**
- **Diff observability drift, not only collector config text.**

## Early implementation order
1. tracing/log identity lane
2. OTLP/schema/profile lane
3. runtime-diagnostic lane
4. support/docs + release lane
5. debugger/incident/domain consumer imports

## Non-goals
- a hosted observability backend;
- a universal telemetry vendor SDK;
- replacing `tracing`, OpenTelemetry, `metrics`, or Tokio Console;
- a single observability health score;
- making release or policy decisions inside the pack itself.

## Success bar
This becomes worthy when a maintainer, operator, or downstream tool can answer:
- what telemetry and runtime diagnostics this subject supports;
- what names/fields/profiles are actually promised;
- what exporter/sampling/redaction/runtime activation belongs to that promise;
- what docs/setup/support claims were checked;
- and what changed between versions or profiles as an observability product,

without scraping config files, dashboards, and repo folklore.

## Read this with
- `gaps/observability-products-telemetry-runtime-diagnostics-and-support-contracts.md`
- `design/observability-productization-stack.md`
- `design/observability-productization-pilot-program.md`
- `design/observability-kit.md`
- `design/diagnostic-surface-kit.md`
- `design/runtime-settings-kit.md`
- `design/support-envelope-kit.md`
