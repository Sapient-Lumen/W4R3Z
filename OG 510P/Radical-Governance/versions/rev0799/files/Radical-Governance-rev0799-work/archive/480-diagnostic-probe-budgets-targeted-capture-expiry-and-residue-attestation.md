# 480 — Diagnostic probe budgets, targeted capture, expiry, and residue attestation

## One-line thesis

When consequential public-AI systems escalate from ordinary monitoring into deeper diagnostic capture, they should do so through a named probe plan with explicit scope, minimization, approval, expiry, export posture, and residue attestation, so incident response and troubleshooting do not quietly become open-ended surveillance or permanent debug residue.

## Why this matters

The archive already covers monitoring honesty, privileged access, record schedules, redaction gateways, serious incidents, repair ladders, and portable evidence packets. What it still lacked was a sharper boundary between **ordinary operational evidence** and **deeper diagnostic capture**.

That boundary matters because many public harms are born in the exception path. A team enables verbose logs, session capture, prompt replay, screen recording, or expanded trace export to debug a complaint, outage, fairness anomaly, or supplier issue. The extra collection is justified for the moment, but nobody names its scope, who approved it, what is excluded, how long it may run, whether the outputs can leave the institution, or what must be removed when the incident closes.

The result is familiar: a temporary diagnostic mode becomes the new normal, extra sensitive material lingers after the incident, and later reviewers cannot say whether the expanded capture was necessary, proportionate, or still active.

## Pattern pack

### 1. Separate ordinary monitoring from diagnostic probes

The archive should distinguish:

- normal steady-state logging and monitoring,
- bounded probe activation,
- promoted incident capture,
- and exported forensic or review bundles.

Those are different authority states, not one generic telemetry setting.

### 2. Require a named probe plan before deeper capture begins

Any diagnostic step that materially increases collection depth, sensitivity, retention, cost, or exposure should open a named probe plan stating:

- the uncertainty or incident question it answers,
- the evidence classes to be collected,
- the classes explicitly excluded,
- the expected performance or privacy cost,
- the approving role,
- and the stop condition or expiry time.

### 3. Budget the probe

Probe plans should carry budgets such as:

- time window,
- event-rate or sample-rate limit,
- subject or case scope,
- buffer size or retention window,
- exportability level,
- and who can read or promote the results.

The point is not zero diagnostics. It is preventing invisible expansion.

### 4. Prefer targeted and ring-buffered capture over ambient escalation

When possible, diagnostic capture should prefer bounded mechanisms such as:

- per-case or per-route capture,
- ring buffers promoted on incident,
- targeted join expansion,
- or short-lived enhanced traces,

instead of turning on broad persistent debug collection for whole populations or whole services.

### 5. Separate local-only capture from exportable material

A probe should say whether the results:

- stay local to the operating team,
- enter a protected incident bundle,
- become part of a review or appeal packet,
- or may be sent to a supplier, auditor, or regulator under defined rules.

Diagnostic scope is not only about what is captured; it is also about where the capture may travel.

### 6. Attest to expiry and residue removal

When the probe ends, preserve a compact attestation stating:

- whether capture actually stopped,
- what residual artifacts remain,
- what was deleted or downgraded,
- what was retained under hold or incident rules,
- and who verified the end state.

Otherwise temporary diagnostics silently become permanent infrastructure.

### 7. Treat probe overuse as governance signal

Repeated need for exceptional capture should be measured as evidence that ordinary observability, dispute packets, operator tooling, or supplier transparency are inadequate.

The goal is not to normalize ever-deeper probes. The goal is to make exceptional capture less necessary over time.

## Guardrails

- Do not hide deep capture behind one vague debug toggle.
- Do not expand collection without naming what is excluded as well as what is included.
- Do not let temporary diagnostic modes outlive their stop condition by inertia.
- Do not export probe artifacts beyond their declared disclosure posture.
- Do not treat leftover diagnostic residue as harmless merely because the incident is over.

## Failure modes

- **debug-forever drift**: temporary verbose capture quietly becomes steady-state practice.
- **probe-without-boundary**: teams collect more without naming subject scope, retention, or approver.
- **silent export creep**: locally justified diagnostics later travel to suppliers or external reviewers without fresh review.
- **residue amnesia**: everyone remembers the incident, but nobody can say what extra traces are still sitting around afterward.
- **exception dependency**: the service repeatedly needs emergency probes because ordinary evidence surfaces are too weak.

## Practical tests

A diagnostic-probe discipline passes when it can answer yes to all of the following:

1. Can the archive distinguish ordinary monitoring from deeper diagnostic capture?
2. Does each material probe have a named plan with purpose, scope, exclusions, approver, and expiry?
3. Are time, rate, subject, retention, and export posture budgeted explicitly?
4. Can the institution show whether a probe stayed local, entered an incident bundle, or left the institution?
5. Is there an end-state attestation showing what stopped, what remains, and why?

## Compression rule for the archive

If a consequential service can say **we turned on more diagnostics** but cannot also say **why, for whom, for how long, with what limits, and what residue remained afterward**, then it is still letting **incident troubleshooting impersonate ungoverned collection**.
