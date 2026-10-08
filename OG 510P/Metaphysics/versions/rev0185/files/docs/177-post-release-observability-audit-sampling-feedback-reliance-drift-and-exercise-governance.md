# 177. Post-release observability, audit sampling, feedback intake, reliance, drift, and exercise governance

## Purpose

Rev0170 made local release execution and attestation language harder to launder. Rev0171 adds the next missing layer: a package may pass its local release gates and still remain weak after release if there is no observable surface for misuse, no audit sampling rule, no feedback intake boundary, no downstream reliance ledger, no drift/anomaly register, and no exercise practice for rollback or incident response.

The added rule is simple: **release is not observation**. A passed gate does not mean that public misunderstanding, silent downstream dependence, stale claims, broken query affordances, or operational misuse will be noticed.

## New local artifacts

Rev0171 adds six root artifacts:

- `OBSERVABILITY_MONITORING_PLAN.yml`
- `AUDIT_SAMPLING_PLAN.yml`
- `FEEDBACK_INTAKE_LEDGER.yml`
- `DOWNSTREAM_RELIANCE_LEDGER.yml`
- `DRIFT_ANOMALY_LEDGER.yml`
- `EXERCISE_INCIDENT_DRILL_LEDGER.yml`

and the checker:

- `tools/check_observability_feedback.py`

These artifacts do not create public monitoring, a service desk, a public issue tracker, a legal duty to respond, or operational deployment permission. They create a local post-release accountability surface only.

## Control-stack placement

Rev0171 follows the rev0170 reproducibility/attestation boundary. The intended sequence is now:

1. Validate package structure, schema-required fields, references, status vocabulary, query regression, invariants, traceability, claim/evidence, release gates, reproducibility/attestation boundary, and fixture corpus.
2. Record the local build, unsigned attestation boundary, custody ledger, execution log, rollback/retraction plan, and public-release packet.
3. Apply post-release observation pressure: monitoring signals, audit samples, feedback channels, reliance rows, drift checks, anomaly dispositions, and exercise/drill evidence.
4. Block any wording that converts local observation planning into public monitoring, incident-response duty, customer-support duty, service-level commitment, domain authority, or operational readiness.

## Key distinctions

### Observability is not public monitoring

`OBSERVABILITY_MONITORING_PLAN.yml` records local signals that a steward can inspect. It does not claim telemetry, public uptime monitoring, alerting infrastructure, user analytics, privacy instrumentation, or continuous supervision.

### Audit sampling is not exhaustive review

`AUDIT_SAMPLING_PLAN.yml` records representative sampling pressure over governed artifacts. It does not prove that every claim, cross-reference, query, or source is correct.

### Feedback intake is not a support channel

`FEEDBACK_INTAKE_LEDGER.yml` distinguishes local feedback memory from a public support obligation. A feedback channel may be documented as inactive, local, or manually reviewed, but not represented as a guaranteed public response path.

### Reliance tracking is not downstream control

`DOWNSTREAM_RELIANCE_LEDGER.yml` records known or declared reliance states. It does not prove that downstream copies, citations, forks, or summaries have been found, recalled, or corrected.

### Drift and anomaly rows are not automatic correction

`DRIFT_ANOMALY_LEDGER.yml` records local drift checks and anomaly dispositions. It does not claim continuous drift detection, source watching, model monitoring, or automatic remediation.

### Exercises are not real incidents

`EXERCISE_INCIDENT_DRILL_LEDGER.yml` records tabletop or local drill evidence. It does not prove real-world incident performance, legal response capacity, or public recall ability.

## Required local checks

Rev0171 requires:

- at least one observability signal with resolving source artifacts;
- at least one audit sample with resolving target artifacts;
- explicit feedback-channel boundary state;
- explicit downstream-reliance boundary state;
- drift/anomaly checks with no unbounded blocking anomaly;
- at least one exercise/drill row with resolving artifacts;
- query coverage for `observability`, `audit`, `feedback`, `reliance`, `drift`, and `drills`;
- fixture coverage for broken observability, audit, feedback, reliance, and drift cases.

## Forbidden shortcuts

Rev0171 blocks the following shortcuts:

- "validated" -> "observed after release";
- "feedback ledger exists" -> "public issue tracker active";
- "drift check row exists" -> "continuous monitoring active";
- "exercise drill passed" -> "incident response proven";
- "reliance ledger exists" -> "downstream reliance controlled";
- "audit sample passed" -> "all claims are correct".

## Public-use boundary

The rev0171 package may be described as a locally validated research/governance package with explicit post-release observability and feedback-boundary artifacts. It may not be described as source-current, operationally monitored, publicly maintained, customer-supported, independently audited, legally attested, or deployment-ready.
