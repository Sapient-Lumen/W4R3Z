# 178. Remediation triage, severity, service objectives, corrective action, escalation, and closure governance

## Purpose

Rev0171 made post-release observation harder to launder. Rev0172 adds the next missing layer: observation can detect a signal, but a signal is not remediation. A feedback item, anomaly, failed query, broken reference, public-overclaim, or downstream-reliance notice still needs triage, severity assignment, local service objectives, corrective-action ownership, escalation boundaries, and closure evidence.

The new rule is: **detection is not disposition**. A detected problem cannot be treated as fixed merely because it appears in a ledger, and a local objective cannot be upgraded into a public SLA.

## New local artifacts

Rev0172 adds six root artifacts:

- `REMEDIATION_TRIAGE_POLICY.yml`
- `SEVERITY_CLASSIFICATION_MATRIX.yml`
- `SERVICE_OBJECTIVE_LEDGER.yml`
- `CORRECTIVE_ACTION_REGISTER.yml`
- `COMMUNICATION_ESCALATION_LEDGER.yml`
- `CLOSURE_VERIFICATION_LEDGER.yml`

and the checker:

- `tools/check_remediation_closure.py`

It also adds the runbook:

- `RUNBOOKS/remediation-triage-corrective-action-closure-review-v1.md`

These artifacts create local remediation accountability only. They do not create a public helpdesk, service-level agreement, emergency-response duty, legal notification process, external incident commander, or proof that every defect has been found.

## Control-stack placement

Rev0172 follows post-release observability. The intended sequence is now:

1. Observe or receive a signal from validator health, query regression, feedback intake, reliance notice, drift/anomaly check, audit sample, exercise drill, or public-language review.
2. Open or update a triage row with a severity class and evidence source.
3. Apply local objective pressure: first-review target, repair target, escalation target, or explicit deferral boundary.
4. Record corrective action, owner role, verification artifact, and forbidden shortcut.
5. Record communication/escalation boundary without implying public notification duty.
6. Close only with evidence, or keep open with an explicit residual-risk or deferral state.

## Key distinctions

### Triage is not repair

`REMEDIATION_TRIAGE_POLICY.yml` records how signals are routed. It does not prove that any signal has been repaired.

### Severity is not panic

`SEVERITY_CLASSIFICATION_MATRIX.yml` creates local severity classes. It does not import emergency, legal, cybersecurity, medical, or public-safety severity duties.

### Service objectives are not SLAs

`SERVICE_OBJECTIVE_LEDGER.yml` records local review and repair objectives for archive stewardship. It does not promise public response times, uptime, customer support, or enforceable service levels.

### Corrective action is not verified closure

`CORRECTIVE_ACTION_REGISTER.yml` records proposed and completed local corrective actions. A corrective action remains insufficient until closure evidence is checked.

### Escalation is not public notification

`COMMUNICATION_ESCALATION_LEDGER.yml` records local escalation paths. It does not create a public notice channel, legal notice duty, customer alerting path, or recall process.

### Closure is not disappearance

`CLOSURE_VERIFICATION_LEDGER.yml` records closure evidence and residual debt. A closed row may still carry public-use restrictions, historical limitations, or downstream reliance debt.

## Required local checks

Rev0172 requires:

- a remediation triage policy with resolving source artifacts;
- a severity matrix with explicit blocking and non-blocking classes;
- service objectives with `public_sla_active: false`;
- corrective actions with verification artifacts;
- communication/escalation rows with `public_notification_duty: false`;
- closure rows with evidence artifacts and residual-debt declarations;
- query coverage for `remediation`, `severity`, `objectives`, `corrective`, `escalation`, and `closure`;
- fixture coverage for broken triage artifact, invalid severity reference, public SLA activation, missing corrective-action evidence, public-notification duty activation, and closure-without-evidence.

## Forbidden shortcuts

Rev0172 blocks the following shortcuts:

- "observed" -> "remediated";
- "triaged" -> "closed";
- "severity assigned" -> "legal incident classified";
- "objective declared" -> "SLA active";
- "corrective action listed" -> "verified closure";
- "escalation path recorded" -> "public notification duty accepted";
- "closure row exists" -> "downstream reliance corrected".

## Public-use boundary

The rev0173 package may be described as a locally validated research/governance package with explicit remediation triage, severity, local-objective, corrective-action, escalation-boundary, and closure-evidence artifacts. It may not be described as publicly supported, SLA-backed, externally remediated, independently audited, legally incident-ready, source-current, or operationally deployable.
