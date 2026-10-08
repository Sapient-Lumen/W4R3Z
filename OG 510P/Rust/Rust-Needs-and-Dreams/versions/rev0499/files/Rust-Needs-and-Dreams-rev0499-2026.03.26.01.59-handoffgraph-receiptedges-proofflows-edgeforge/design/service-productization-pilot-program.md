# Design: Service Productization Pilot Program (Service Surface + Runtime Settings + Observability + Async Reliability + Background Work + Support Envelope)

## Goal
Turn the **Service Productization Stack** from a plausible synthesis into a ranked execution program that can prove real value quickly: route truth, settings truth, runtime evidence, async/work reliability, and honest support claims before the ecosystem tries to promise a “complete Rust service platform” in the abstract.

## Why this needs a pilot layer
The archive already had strong individual designs for services, config, telemetry, async reliability, jobs, and support claims. What it did not yet state clearly enough is:
- which service-productization lane should be proven first;
- when route and settings truth are sufficient versus when telemetry or replay are needed;
- when async lifecycle evidence is ordinary service-operability work versus deeper incident/replay work;
- when background jobs and workflows deserve first-class contracts instead of “internal implementation detail” status;
- and when docs/support claims are credible enough for users, operators, and release consumers.

Without this layer, the archive risks two opposite failures:
1. **framework theater** — people mistake one pleasant web framework or app template for a solved production-service substrate;
2. **operability theater** — projects accumulate tracing, config crates, cron jobs, and README promises without one reviewable contract tying them together.

## Design principles
1. **Start with the cheapest trustworthy service lane.** Route and settings truth should come before platform fantasies.
2. **Escalation must be explicit.** Pilots should say when they stop at HTTP/config/docs, when they add telemetry, and when they escalate into replay/incident territory.
3. **Out-of-band work is first-class.** Jobs and workflows are not “miscellaneous service internals”.
4. **Support docs are consumers, not the source of truth.** docs.rs, READMEs, and runbooks should import pilot artifacts.
5. **Negative and partial results matter.** “Unsupported on this runtime floor” or “job contract incomplete” is a useful pilot outcome.
6. **Do not bless one framework too early.** The stack should stay portable across `axum`, `actix-web`, `poem`, `tower`, and adjacent ecosystems.

## Pilot artifact family
### 1) `service-lane-brief/v0`
Explains why a particular service-productization lane is worth piloting now:
- lane id and summary
- target subject and operator/developer user story
- likely escalation path
- why current framework/docs folklore is insufficient
- concrete ecosystem proving ground (for example `axum` + `tower-http`, `config`, Tokio/tracing, or `apalis`)

### 2) `service-escalation-policy/v0`
Declares the intended handoff order:
- route/settings stop conditions
- telemetry escalation conditions
- async/background-work escalation conditions
- support/release/policy consumer conditions
- replay/incident escalation conditions

### 3) `service-correlation-budget/v0`
Defines what evidence links are required:
- route ids ↔ checked exchanges
- route/settings ↔ telemetry fields and runtime ids
- route/settings ↔ job/workflow triggers
- runtime evidence ↔ support/docs claims
- incident/replay packs ↔ prior service artifacts

### 4) `service-readiness-scorecard/v0`
Decides whether a pilot is credible:
- are the lane boundaries explicit?
- are unsupported areas visible?
- can at least one downstream consumer import the results?
- should the lane be `promote`, `pilot`, `watch`, or `defer`?

### 5) `service-pilot-pack/v0`
Bundle for publication and reuse:
- lane brief
- escalation policy
- correlation budget
- selected service/settings/obs/async/work/support artifacts
- readiness scorecard
- consumer summary

## Concrete first proving grounds
- **`axum` + `tower-http` request/config pilot** for route, middleware, and checked exchange truth without pretending router code alone is the product.
- **Tokio + `tracing` / `tracing-opentelemetry` runtime-correlation pilot** for spans, logs, and correlation ids that point back to declared service identities.
- **`config`-backed layered-settings pilot** for defaults, environment/file/source precedence, and checked examples.
- **`apalis`-backed background-work pilot** for official job identity, retries, monitoring, and graceful-drain posture without burying work semantics inside a service README.
- **docs.rs / `doc_cfg` support pilot** for checked docs/support truth instead of assuming one CI build or one local run proves deployment support.

## Ranked first pilots

### 1) Request-surface + settings lane
**Why first**
- It is the cheapest lane that still creates real productization value.
- The 2024 survey says Rust is already popular for server backends, web/networking services, and cloud technologies.
- Many teams can benefit from route truth and configuration truth before they need deeper reliability or incident machinery.

**What must be explicit**
- stable route ids and support levels
- checked exchange examples
- stable setting ids, source precedence, defaults, and secret posture
- docs/import links for operators and users

**Success bar**
A service can publish a reviewable request/config contract that users, CI, and docs can all consume.

### 2) Telemetry + runtime-correlation lane
**Why second**
- The 2025 survey keeps debugging and resource usage in the pain set.
- Once route/settings truth exists, telemetry can become an explainable import instead of a bag of spans.

**What must be explicit**
- telemetry profile and exporter posture
- required signal names/fields
- route/request/job correlation ids
- redaction and environment posture
- unsupported runtime-diagnostic lanes

**Success bar**
A service can show what runtime evidence it emits and how it connects back to declared service behavior.

### 3) Graceful shutdown + background-work lane
**Why third**
- The 2026 flagship themes keep async actively evolving.
- Real services nearly always have worker tasks, schedulers, or workflows that ordinary route contracts do not cover.

**What must be explicit**
- shutdown/cancellation semantics
- worker/task ownership
- job/workflow identities and trigger maps
- retry/idempotency posture
- what is exact versus best-effort during recovery

**Success bar**
A service can explain how it stops, drains, retries, and resumes out-of-band work without hand-wavy runbook prose.

### 4) Support-envelope + docs truth lane
**Why fourth**
- docs.rs target changes and the `doc_cfg` push make support/availability truth more salient.
- Many service support problems are really hidden target/runtime-floor/docs mismatches.

**What must be explicit**
- runtime floors and target assumptions
- docs.rs / cfg / target coverage posture
- checked docs/examples/transcripts
- source-build versus release-artifact support differences
- unsupported platform or deployment claims

**Success bar**
Users and operators can tell which deployments are officially supported and what the docs actually prove.

### 5) Release / policy / incident consumer lane
**Why fifth**
- Once earlier pilots exist, service evidence can drive real governance and release decisions.
- This is how productization becomes ecosystem infrastructure rather than local engineering taste.

**What must be explicit**
- which artifacts are required for release review
- which policy checks consume which service truths
- freshness/expiry posture
- incident escalation prerequisites
- what remains advisory rather than gating

**Success bar**
A release or deployment decision can import service evidence without flattening it into one fake green check.

## Pilots to defer
These matter later, but are weaker opening bets:
- **one batteries-included Rust service mega-framework** — too likely to hide real lane boundaries;
- **a hosted service platform/dashboard** — too heavy before portable artifacts mature;
- **universal platform templates** — useful as consumers later, but premature as the canonical source;
- **policy-first service gating** — too brittle before route/settings/obs/support artifacts are stable.

## Immediate archive consequences
Read this file together with:
- [`design/service-productization-stack.md`](./service-productization-stack.md)
- [`design/service-surface-kit.md`](./service-surface-kit.md)
- [`design/runtime-settings-kit.md`](./runtime-settings-kit.md)
- [`design/observability-kit.md`](./observability-kit.md)
- [`design/async-reliability-stack.md`](./async-reliability-stack.md)
- [`design/background-work-kit.md`](./background-work-kit.md)
- [`design/support-envelope-kit.md`](./support-envelope-kit.md)
- [`design/docproof-kit.md`](./docproof-kit.md)
- [`design/policy-kit.md`](./policy-kit.md)
- [`design/release-pipeline-kit.md`](./release-pipeline-kit.md)

The archive should now prefer:
- **an explicit epic path** for service-productization work via [`proposals/epic-service-productization-stack.md`](../proposals/epic-service-productization-stack.md),
- **request/config-first pilots** before platform-scale ambitions,
- **explicit escalation policies** instead of improvised “add tracing and hope” handoffs,
- **portable background-work modeling** instead of burying jobs inside service internals,
- **docs/support truth** instead of README optimism,
- and **consumer imports** over prose-only service readiness claims.

## What should wait
Do **not** start with:
- a universal service control plane,
- a full platform-as-a-product pitch,
- one generated mega-schema for routes/config/telemetry/jobs/support,
- or a fake aggregate “service maturity” score.

Those may become overlays or consumers later.
They are not the missing substrate.
