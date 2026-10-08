# Crate diagnosis-surface lanes — 2026-03-17

This note keeps one specific crate lane from dissolving into vague “better debugging / observability / support tooling” language.

## The lane this file is defending

The missing lane is:

- **receiver-facing crate diagnosis-surface contracts** — official symptom catalogs, self-check manifests, signal maps, remediation classes, safe support-capture guidance, and release-to-release diffs.

The sharp question is:

> “When this crate stalls, floods, or behaves strangely, what symptoms does it officially recognize, what should I inspect first, and what bundle should I capture before escalating?”

## What it is not

### 1. Not compile-time guidance or failure-path support

**P-0512** is about diagnostics and recovery guidance around failure paths.
**P-0525** is about steady-state or runtime-near troubleshooting surfaces that may exist even when nothing crashed.

### 2. Not runtime failure handoff bundles

**P-0513** is about panic/failure handoff bundles and redacted runtime context.
**P-0525** is about recognized symptoms, self-checks, signal maps, and troubleshooting bundles even outside a crash path.

### 3. Not observability-surface contracts

**P-0518** is about which telemetry exists, how stable it is, what it costs, and how sensitive it is.
**P-0525** imports those signals into a receiver-facing symptom-to-action contract.

### 4. Not debuggability posture or symbol/visualizer support

**P-0486** is about debuginfo, visualizers, symbol sidecars, and debugger readiness.
**P-0525** is about what symptoms to diagnose and which checks or captures are officially supported.

### 5. Not downstream test-surface contracts

**P-0523** is about fixtures, fakes, deterministic seams, and scenario corpora for downstream tests.
**P-0525** is about troubleshooting support in live or quasi-live conditions.

### 6. Not official example / quickstart support

**P-0524** is about the smallest supported path to first success.
**P-0525** is about the smallest supported path to first diagnosis once the happy path no longer holds.

### 7. Not a full incident-management or support platform

A dashboard, hosted support portal, or incident-management product can aggregate evidence and coordinate people.
**P-0525** is narrower: it exists to make crate-authored troubleshooting support explicit, reviewable, and diffable.

## Working rule for future passes

When a pass proposes another crate in this neighborhood, it must state explicitly whether the missing value is primarily about:

1. **failure-path / compile-time guidance**,
2. **runtime failure handoff**,
3. **observability signal contracts**,
4. **debugger / symbol / visualizer posture**,
5. **receiver-facing diagnosis-surface contracts**,
6. **downstream testing support**,
7. or a **full incident/support platform**.

Do **not** let the archive quietly collapse telemetry emission, debugger readiness, issue templates, crash bundles, symptom catalogs, and hosted support systems into one fake debugging-support lane.

Future passes in this area should also name at least **two adjacent lanes considered but not promoted**, so archive memory retains the boundary instead of restating it later from scratch.
