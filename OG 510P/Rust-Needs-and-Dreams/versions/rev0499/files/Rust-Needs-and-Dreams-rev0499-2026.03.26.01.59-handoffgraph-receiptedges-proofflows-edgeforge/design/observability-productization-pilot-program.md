# Design: Observability Productization Pilot Program (Diagnostic Surface + Observability + Runtime Settings + Support Envelope)

## Goal
Turn the **Observability Productization Stack** from a plausible synthesis into a ranked execution program that can prove real value quickly: stable failure identity, reviewable signal subsets, explicit activation/export posture, honest support claims, and downstream release/incident/debug consumers.

Read this together with [`design/observability-lane-map.md`](./observability-lane-map.md): every pilot should now name which lanes it covers and which lanes remain explicitly out of scope.

## Why this needs a pilot layer
The archive already had a strong lower-layer Observability Kit.
What it did not yet state clearly enough is:
- which observability-productization lane should be proven first;
- when signal/profile truth is enough versus when runtime diagnostics or release attachments are needed;
- when runtime-specific diagnostics belong in the official support story versus a local debugging lane;
- when env/exporter defaults are acceptable versus when explicit activation reports are required;
- and when incident/debug/release consumers are justified rather than premature.

Without this layer, the archive risks two opposite failures:
1. **telemetry theater** — projects emit logs, spans, and metrics but cannot state what is actually promised;
2. **platform theater** — people mistake one backend integration or collector template for a solved observability substrate.

## Design principles
1. **Start with the cheapest trustworthy identity and signal lane.** Name and validate what exists before promising fleet-scale control planes.
2. **Activation must be explicit.** Exporters, endpoints, sampling, redaction, and runtime-specific gates should not hide in env-var folklore.
3. **Runtime diagnostics are first-class but capability-gated.** Tokio Console-style lanes matter without becoming the universal default.
4. **Support docs are consumers, not the source of truth.** Docs should import checked artifacts.
5. **Negative and partial results matter.** “metrics lane incomplete” or “Tokio Console dev-only” is a useful outcome.
6. **Do not bless one backend too early.** OTLP-first is sensible, but the stack should stay portable above vendor selection.

## Pilot artifact family
### 1) `obs-lane-brief/v0`
Explains why a particular observability-productization lane is worth piloting now:
- lane id and summary
- target subject and operator/developer user story
- likely escalation path
- why existing telemetry/config folklore is insufficient

### 2) `obs-escalation-policy/v0`
Declares the intended handoff order:
- diagnostic-identity stop conditions
- signal/profile validation conditions
- activation/export escalation conditions
- runtime-diagnostic escalation conditions
- support/release/incident/debug consumer conditions

### 3) `obs-correlation-budget/v0`
Defines what evidence links are required:
- diagnostic ids ↔ logs/spans/metrics
- service/job/task/resource ids ↔ telemetry fields
- runtime settings ↔ effective exporter/sampling/redaction posture
- runtime diagnostics ↔ general telemetry lanes
- release/support/incident consumers ↔ earlier observability artifacts

### 4) `obs-readiness-scorecard/v0`
Decides whether a pilot is credible:
- are lane boundaries explicit?
- are unsupported areas visible?
- can at least one downstream consumer import the results?
- should the lane be `promote`, `pilot`, `watch`, or `defer`?

### 5) `obs-product-pack/v0`
Bundle for publication and reuse:
- lane brief
- escalation policy
- correlation budget
- selected diagnostic / obs / settings / support artifacts
- readiness scorecard
- consumer summary

## Ranked first pilots

### 1) Tracing/log identity lane
**Why first**
- It is the cheapest lane that still creates real productization value.
- Many Rust projects already have `tracing`, `tracing-subscriber`, and sometimes `tracing-log`.
- Stable diagnostic/event identity is the prerequisite for later support, alerting, and incident consumers.

**What must be explicit**
- stable event/diagnostic ids or classes
- subscriber-layer posture
- `log` ↔ `tracing` bridge stance
- human vs machine output differences

**Success bar**
A project can publish a reviewable log/trace identity contract that docs, CI, and support can all consume.

### 2) OTLP + schema/profile lane
**Why second**
- OpenTelemetry Rust now documents all three major signals together, but all remain Beta.
- The OpenTelemetry project itself is emphasizing stability, release hygiene, and “observability by design”.

**What must be explicit**
- chosen semantic-convention/profile subset
- required signal names and attributes
- OTLP/exporter posture
- validation vectors and drift checks
- unmaintained or deprecated exporter warnings where relevant

**Success bar**
A project can show what telemetry subset it supports and validate that promise in CI.

### 3) Runtime-diagnostic lane
**Why third**
- Tokio Console already proves the value of task/runtime diagnostics, but its activation requirements mean it cannot be treated as silent default behavior.
- This is where many teams currently blur “local debugging tool” and “supported runtime evidence”.

**What must be explicit**
- whether runtime diagnostics are dev-only, CI-only, or supportable in production
- activation gates (`tokio_unstable`, tracing targets, extra endpoints)
- protocol/client posture
- relation to general traces/logs/metrics

**Success bar**
A project can describe runtime diagnostics as an honest supported capability instead of a hidden local trick.

### 4) Support-envelope + release lane
**Why fourth**
- The 2025 Rust survey says docs remain canonical.
- Observability behavior is now something operators and downstream consumers expect to read and trust, not reconstruct from code.

**What must be explicit**
- support levels per signal/profile
- checked docs/examples/setup transcripts
- release attachment of observability packs
- supported vs best-effort vs experimental lanes
- unsupported platform/runtime/profile claims

**Success bar**
Users and operators can tell what observability behavior shipped with a release and what the docs actually prove.

### 5) Incident / debugger / product consumer lane
**Why fifth**
- Once earlier pilots exist, observability evidence can drive real debugging and release work instead of remaining local engineering taste.
- This is how the stack becomes ecosystem infrastructure.

**What must be explicit**
- which artifacts are required for incident or debugger handoff
- which stacks import which observability truths
- freshness/expiry posture
- what remains advisory rather than gating

**Success bar**
A downstream consumer can import observability evidence without flattening it into one fake green check.

## Pilots to defer
These matter later, but are weaker opening bets:
- **one hosted Rust observability platform** — too likely to hide real portability and support boundaries;
- **one universal telemetry facade replacing existing crates** — too likely to erase real lane differences;
- **policy-first gating of telemetry quality** — too brittle before identity/profile/support artifacts stabilize;
- **a mega-schema for every signal/backend/dashboard/query** — too broad before narrow reviewable subsets mature.

## Immediate archive consequences
Read this file together with:
- `design/observability-productization-stack.md`
- `design/diagnostic-surface-kit.md`
- `design/observability-kit.md`
- `design/runtime-settings-kit.md`
- `design/support-envelope-kit.md`
- `design/docproof-kit.md`
- `design/debuggability-stack.md`
- `design/service-productization-stack.md`

The archive should now prefer:
- **identity-first and profile-first pilots** before backend/platform ambition,
- **explicit activation reports** instead of env-var folklore,
- **runtime-diagnostic honesty** instead of silently treating local tools as supported product surfaces,
- **support/docs truth** instead of README optimism,
- and **consumer imports** over prose-only observability-readiness claims.

## What should wait
Do **not** start with:
- a vendor-specific dashboard suite,
- a full collector distribution,
- one generated mega-schema for all telemetry/runtime/profile/setup questions,
- or a fake aggregate “observability maturity” score.

Those may become overlays or consumers later.
They are not the missing substrate.
