# Preventive control contract sheet page: source case, hazard signature, and coverage scope interface spec

## Purpose

After the archive learned to close cases honestly, it still needed one ordinary page for the next operator question:

> what durable control or watch did this case teach us to create, what exact hazard shape is it for, and what scope does it really cover?

## Core decision

AnonSync must expose one first-class **Preventive control contract sheet** whenever a non-trivial case is promoted into a reusable guardrail, watch, or capture-on-repeat runbook.

The page exists to answer ten things in one place:

1. which case or cases justify the control
2. what exact hazard signature the control is about
3. whether the control is preventive, detective, containment, or capture-only
4. what subjects and worlds are in scope
5. what prerequisites must already be true
6. what activation method is intended
7. what success sentence the team hopes to earn
8. what stronger sentence is still blocked
9. who owns rereview and drift response
10. what the control explicitly does **not** protect against

## Fixed page order

1. **Control header**
2. **Source-case basis card**
3. **Hazard signature card**
4. **Coverage scope card**
5. **Mechanism and prerequisites card**
6. **Claim ceiling and anti-claims**

### 1) Control header

Show at minimum:

- `control_id`
- control title
- control class
- owner
- created time
- latest revision
- current posture
- linked source case ids
- linked policy / rollout ids

Supported `control_class` values must include:

- `preventive`
- `detective-watch`
- `containment`
- `capture-on-repeat`
- `operator-guidance-only`
- `accepted-risk-marker`

Supported `current_posture` values must include:

- `draft`
- `reviewing`
- `approved-not-activated`
- `activating`
- `active`
- `watching-effectiveness`
- `expired`
- `superseded`
- `retired`

### 2) Source-case basis card

Publish explicit rows for:

- source case id
- source symptom cluster
- favored cause or hazard family
- closure class of the source case
- confidence floor inherited from the source case
- why promotion is justified
- why one-off local guidance is not enough

Hard rule:

A case with `unknown-but-stable` closure may still justify a detective watch or capture-on-repeat control, but must not by itself justify a strong preventive claim.

### 3) Hazard signature card

Each control must name a reusable **hazard signature**.
Required fields:

- visible symptom family
- underlying cause family
- triggering preconditions
- excluded lookalikes
- severity if repeated
- expected repeat horizon
- whether human action is part of the hazard

Supported `cause_family` values must include:

- `environment-capacity`
- `runtime-state-corruption`
- `identity-or-metadata`
- `topology-or-discovery`
- `permissions-or-locking`
- `path-or-filesystem-compatibility`
- `operator-procedure-gap`
- `version-or-world-fragmentation`
- `unknown-pattern-watch`

Hard rule:

The hazard signature must separate `same visible symptom` from `same cause family`.
A control may scope itself to one or both, but cannot blur them.

### 4) Coverage scope card

Required rows:

- subject class covered
- world / lane coverage
- platform coverage
- version floor and ceiling
- entitlement assumptions
- explicit exclusions
- rollout target size
- restart or cold-apply requirement

Supported `scope_strength` values:

- `single-subject`
- `cohort`
- `policy-profile-bound`
- `world-wide`
- `advisory-only`

### 5) Mechanism and prerequisites card

Each control must publish:

- mechanism description
- activation surface
- preconditions
- dependencies
- failure modes
- reversibility class
- expected side effects
- proof inputs required after activation

Supported `activation_surface` values must include:

- `setting-change`
- `policy-profile`
- `config-managed`
- `service-or-runtime-posture`
- `environment-tuning`
- `monitoring-rule`
- `capture-runbook`
- `operator-training-or-checklist`

### 6) Claim ceiling and anti-claims

The page must show three separate sentences:

- `safe strongest claim now`
- `blocked stronger claim`
- `explicit anti-claim`

Examples of valid anti-claims:

- `does not prevent the hazard outside Linux worlds`
- `does not prevent repeats caused by manual service-world forks`
- `detects recurrence earlier but does not stop the root cause`
- `reduces blast radius only after restart-bound activation`

Hard rule:

Every active control must publish at least one explicit anti-claim.
