# Design: Debuggability Pilot Program (Diagnostic Surface + Observability + Debugger Experience)

## Goal
Turn the **Debuggability Stack** from a plausible synthesis into a ranked execution program that can prove real value quickly: stable failure identities, trustworthy runtime correlation, honest debugger tuple claims, and durable repro handoffs before the ecosystem tries to promise “stellar debugging” in the abstract.

## Why this needs a pilot layer
The archive already has separate designs for diagnostics, observability, and debugger support. What it did not yet state clearly enough is:
- which debuggability lane should be proven first;
- when a failure should stop at diagnostics versus escalate to telemetry or a debugger;
- when runtime-side async inspection counts as side-channel help rather than native debugger support;
- when a debugger claim is credible enough for support or compatibility docs;
- and when replay / incident lanes are genuinely justified.

Without this layer, the archive risks two opposite failures:
1. **debugger theater** — projects casually claim “debugging works” after checking one IDE path or one debugger tuple;
2. **telemetry theater** — projects ship logs/traces/console hooks but still cannot explain what failure happened or what a maintainer should do next.

## Design principles
1. **Start with the cheapest trustworthy lane.** Many problems should terminate at checked diagnostics before escalating.
2. **Escalation must be explicit.** A pilot should say why it moved from diagnostics to telemetry, from telemetry to debugger, or from debugger to replay.
3. **Tuple truth beats brand claims.** Debugger evidence must stay tied to concrete tuples.
4. **Correlation is not causation.** Logs/traces/debugger observations can point to a problem without claiming they fully explain it.
5. **Support docs are consumers, not the source of truth.** Support/import layers should read pilot artifacts.
6. **Negative and partial results matter.** “unsupported on this tuple” is a useful pilot outcome.

## Pilot artifact family
### 1) `debug-lane-brief/v0`
Explains why a particular debuggability lane is worth piloting now:
- lane id and summary
- target subject and user story
- likely escalation path
- why current folklore is insufficient

### 2) `debug-escalation-policy/v0`
Declares the intended handoff order:
- diagnostic-only stop conditions
- telemetry escalation conditions
- debugger escalation conditions
- replay/incident escalation conditions
- required artifacts at each step

### 3) `debug-correlation-budget/v0`
Defines what evidence links are required:
- diagnostic ids ↔ fixtures/examples
- diagnostic ids ↔ logs/traces/runtime signals
- runtime signals ↔ debugger or async-inspection subjects
- repro packs ↔ prior diagnostics/telemetry/debugger reports

### 4) `debug-readiness-scorecard/v0`
Decides whether a pilot is credible:
- is the lane actually useful?
- are claims explicit enough for consumers?
- are unsupported areas visible?
- should the lane be `promote`, `pilot`, `watch`, or `defer`?

### 5) `debug-pilot-pack/v0`
Bundle for publication and reuse:
- lane brief
- escalation policy
- correlation budget
- selected diagnostic / telemetry / debugger artifacts
- readiness scorecard
- consumer summary

## Ranked first pilots

### 1) Failure-identity lane
**Why first**
- The 2025 survey says many users actually find compiler error explanations useful, which is a strong signal that clear diagnostic surfaces are not optional garnish.
- Many debugging sessions should end here if the failure surface is stable, documented, and reviewable.
- This is the cheapest place to improve daily Rust experience without waiting for debugger parity.

**What must be explicit**
- stable diagnostic ids or explicit `none`
- checked CLI/JSON/HTTP examples
- help/docs metadata
- redaction posture
- the threshold for escalating beyond diagnostics

**Success bar**
A project can publish a checked failure surface and show when a user should move on to telemetry or debugger tooling instead of guessing.

### 2) Debugger tuple-truth lane
**Why second**
- The 2026 debugging survey is explicit that debugger quality varies across families, versions, and operating systems.
- The archive already has a good debugger kit; what it needed was a clearer place in the larger debugging story.

**What must be explicit**
- debugger family/version + OS + target + toolchain tuple
- visualizer coverage
- async-inspection posture
- expression-evaluation posture
- `supported` / `partial` / `watch` / `unsupported` outcomes

**Success bar**
A project can publish honest debugger capability claims that support docs and issue templates can reuse.

### 3) Runtime-correlation lane
**Why third**
- Many operational failures need logs/traces/runtime metadata before native stepping is practical.
- Cargo and adjacent tooling are making machine-readable reports more available, which makes correlation more realistic and less folkloric.

**What must be explicit**
- telemetry profile and exporter/runtime config
- required signal names/fields
- correlation with diagnostic ids or request/span/task ids
- what is local-dev only versus CI or production-safe
- unsupported or intentionally omitted signals

**Success bar**
A service or binary can show which runtime evidence is expected, how it links to failure identities, and what privacy or configuration tradeoffs apply.

### 4) Repro / replay handoff lane
**Why fourth**
- Not every problem needs replay, but the hard ones often do.
- This lane proves that replay or incident workflows can import prior debug evidence instead of starting from scratch.

**What must be explicit**
- the failure identity that triggered escalation
- the telemetry/debugger artifacts already attached
- what replay or repro subject is now being captured
- exact vs best-effort posture
- where the handoff stopped being ordinary debug work and became deeper reliability work

**Success bar**
A hard bug can move from failure report to replay/repro pack without losing its earlier diagnostic and observability context.

### 5) Support / compatibility consumer lane
**Why fifth**
- Once earlier pilots exist, support envelopes and compatibility claims can import them.
- This is how debugging improvements become ecosystem infrastructure instead of local engineering practice.

**What must be explicit**
- which claims are safe for docs/release/support pages
- freshness/expiry posture
- which tuples or profiles the claim actually covers
- which gaps remain watch-only or unsupported

**Success bar**
Support and compatibility docs can cite debuggability evidence without collapsing it into one universal support badge.

## Pilots to defer
These matter later, but are weaker opening bets:
- **one universal debugger runtime/adapter layer** — too likely to hide real tuple differences;
- **full replay-first debugging platforms** — too heavy before ordinary evidence lanes are mature;
- **observability mega-schemas** — likely to obscure the narrow profiles real users can review;
- **AI-first debugging copilots** — useful consumers later, but the stack should not make them canonical.

## Immediate archive consequences
Read this file together with:
- [`design/debuggability-stack.md`](./debuggability-stack.md)
- [`proposals/epic-debuggability-stack.md`](../proposals/epic-debuggability-stack.md)
- [`design/diagnostic-surface-kit.md`](./diagnostic-surface-kit.md)
- [`design/observability-kit.md`](./observability-kit.md)
- [`design/debugger-experience-kit.md`](./debugger-experience-kit.md)
- [`design/debugger-pilot-program.md`](./debugger-pilot-program.md)
- [`design/replay-kit.md`](./replay-kit.md)
- [`design/incident-kit.md`](./incident-kit.md)
- [`design/async-reliability-stack.md`](./async-reliability-stack.md)

The archive should now prefer:
- **diagnostic-first debugging improvements** before expensive tuple labs,
- **explicit escalation policies** instead of improvised handoffs,
- **correlation budgets** instead of vague “we have tracing/debugger support” claims,
- and **consumer imports** over prose-only support claims.

## What should wait
Do **not** start with:
- one giant debugger support matrix for the whole ecosystem,
- a hosted debugging SaaS,
- a plan to replace existing error crates or telemetry crates,
- or a fake aggregate “debuggability score.”

Those may become consumers or overlays later.
They are not the missing substrate.
