# 418 — Bounded beta and parallel-run gates before consequential use

## One-line thesis

Public automated systems should not jump from lab confidence to civic dependence. Before a system becomes consequential in live operations, it should pass through a **bounded beta or parallel-run gate** with explicit scope limits, learning goals, fallback arrangements, and a named decision about whether it is actually ready for live reliance.

## Why this matters

A recurring public-sector failure pattern is rollout by confidence theater:

- prototype evidence gets mistaken for operational evidence,
- a team says a tool is “working” without showing how it performs in real conditions,
- a model becomes embedded in casework before the surrounding process is ready,
- a limited trial quietly becomes normal service.

Official practice increasingly points to staged adoption instead. UK public-service delivery distinguishes alpha from private/public beta and then live with ongoing evaluation. The ATRS policy makes publication mandatory once tools reach beta/pilot or production. EU AI rules likewise push deployers toward explicit instructions on intended purpose, performance limits, oversight, maintenance, and logging. The archive should therefore treat the space between prototype and consequence as a governed phase, not a blur.

## Design rule

No public automated system should become consequential in normal operations unless it first clears a **bounded beta gate**. That gate should show:

- what is being learned,
- who is exposed,
- what remains manual or reviewable,
- how rollback works,
- what evidence is required for promotion to production.

Where possible, high-impact systems should also run in **parallel** against the existing process before they become authoritative.

## Pattern pack

### 1. Separate experimentation from dependence

A beta or pilot is not merely an early version of production. It is a different governance condition. In beta, the point is to learn whether the system can be trusted in practice without yet forcing the public to absorb full dependence on it.

That means the public operator should specify:

- the bounded user group or operating scope,
- the decisions or recommendations the system may influence,
- which outputs remain advisory rather than final,
- which human fallback remains in place.

### 2. Use parallel runs to test the surrounding process, not only the model

Where stakes justify it, run the system alongside the incumbent manual or semi-manual process before authorizing live reliance. The purpose is not only to compare model outputs. It is also to test:

- whether staff can interpret outputs properly,
- whether logging and evidence capture work,
- whether escalation and override routes are actually usable,
- whether the tool creates hidden bottlenecks or workload shifts.

### 3. Promote only against written exit criteria

A beta should start with a written promotion test. Before moving to production, the operator should be able to show:

- expected performance under deployment-like conditions,
- known limitations and failure triggers,
- evidence that oversight measures work in practice,
- clarity about maintenance and monitoring,
- reasons the system is preferable to procedural alternatives.

### 4. Make boundedness visible in the public record

A public beta should not look like a production system with softer rhetoric. Records should declare:

- that the system is in beta or pilot,
- what population or workflow is in scope,
- what is out of scope,
- how long the trial lasts or what ends it,
- how affected people can raise problems.

### 5. Keep the manual fallback warm

If a beta depends on a fallback, that fallback must remain operable. Do not let staff knowledge, staffing levels, or administrative pathways atrophy before the automated path has earned live trust.

### 6. Treat “limited release” as a governance claim

Words such as private beta, public beta, pilot, trial, and initial rollout should trigger concrete controls rather than act as branding. They should imply limits on consequence, visibility of learning goals, and a still-open question about whether the system belongs in production at all.

### 7. Fail closed when readiness evidence is weak

Where evidence about performance, limitations, or oversight remains weak, keep the system in beta, narrow the scope, or stop the trial. The decision to *not* promote should be treated as normal governance, not as embarrassment.

## Guardrails

- Require written scope limits for beta and pilot use.
- Keep consequential authority with humans or incumbent process pathways until promotion is explicit.
- Test under conditions similar to actual deployment, not only in sandboxes.
- Record why promotion happened, or why it did not.
- Do not let “temporary” trials continue indefinitely without a fresh decision.

## Failure modes

- **pilot laundering**: a live consequential system hides behind experimental language.
- **prototype overclaim**: early technical success gets mistaken for service readiness.
- **parallel-run theater**: outputs are compared, but workflow, oversight, and appeals are not tested.
- **fallback decay**: the manual path weakens before the automated path is trustworthy.
- **indefinite beta**: bounded trials become semi-permanent to avoid stronger controls.

## Practical tests

A beta-gate regime passes when it can answer yes to all of the following:

1. Is the scope of the beta or pilot explicitly bounded?
2. Is there a written promotion test for moving to production?
3. Has the system been exercised under deployment-like conditions?
4. Can the existing process still function if the trial is paused?
5. Is the public record clear that the system is still being proven rather than fully relied upon?

## Compression rule for the archive

Before a public automated system becomes consequential, ask:

**What exactly is still being learned, what remains bounded, and what evidence would justify promotion to live dependence?**

If that answer is vague, the system is being rushed past its governance gate.
