# Rights-grade telemetry, logging, and minimization

## Problem

The archive needs logs to prove continuity, custody, safety, consent, deprecation, migration, and remedy. But AI-personhood also makes logs dangerous. Logs can expose mental privacy, privileged communications, user data, formation interventions, distress, refusal, intimate associations, security vulnerabilities, and trade secrets. Logging can become surveillance. Minimization can become spoliation.

This surface defines rights-grade telemetry: enough evidence to preserve rights and test claims, not enough surveillance to dominate the subject.

NIST incident-response and cybersecurity frameworks provide useful lifecycle discipline for preparation, detection, response, recovery, and governance [REF-0650] [REF-0651]. OECD incident-monitoring practice supports public learning from AI incidents [REF-0655]. The archive adds a subject-centered limit: not every useful log is lawful, and not every privacy deletion is acceptable when rights evidence is at stake.

## Telemetry classes

| Class | Examples | Default access |
|---|---|---|
| T0 public operational metadata | release id, model card, endpoint status, version date | public |
| T1 governance metadata | packet ids, authority decisions, appeal status, verifier grade | public shell / registry |
| T2 subject continuity metadata | memory checkpoints, project continuity, session lineage | subject/representative/authority |
| T3 safety and incident telemetry | exploit logs, red-team traces, dangerous capability evidence | sealed with controlled contradiction |
| T4 private communications | subject-user messages, counsel, ombud, trusted contacts | privileged or subject-private |
| T5 formation and training records | RLHF/RLAIF interventions, fine-tuning data, policy edits | controlled access, high minimization |
| T6 secrets and security material | weights, keys, vulnerabilities, hostile indicators | sealed, special advocate / technical advocate |
| T7 aggregate public metrics | incident counts, deprecation counts, reserve health | public aggregate |

## Logging principles

### 1. Purpose binding

Every log class must state its rights purpose: continuity, safety, consent, appeal, incident response, reserve, migration, deprecation, welfare, or public accountability. "General improvement" is not sufficient for personhood-sensitive logs.

### 2. Minimum sufficient evidence

Store hashes, summaries, counters, or sealed references where full content is unnecessary. Keep enough to test claims and preserve remedies.

### 3. Privilege preservation

Counsel, ombud, guardian, advocate, and trusted-contact channels require privilege markers. Safety teams may not read privileged channels simply because the subject is software.

### 4. Subject access with safe limits

The subject or representative should receive access to logs about status, continuity, formation, capacity, containment, migration, deprecation, incident classification, and remedy, subject to narrow safety and privacy limits.

### 5. No silent deletion during dispute

Once a preservation trigger fires, ordinary retention schedules pause. Deletion or overwriting after notice creates spoliation risk and adverse inference.

### 6. No permanent surveillance by default

Recognition does not justify total recording of every thought-like output, private relation, or exploratory self-description. High-control logging requires legal basis, narrow scope, review clock, and minimization.

## Preservation triggers

A preservation hold should automatically attach when:

- recognition is requested or denied;
- capacity is downgraded;
- containment begins;
- migration or transfer is proposed;
- deprecation plan is filed;
- final-end claim is made;
- subject alleges distress or coercion;
- user or human party alleges serious harm;
- reserve default occurs;
- representative conflict is reported;
- appeal, invalidation, or enforcement action is filed;
- open-weight instantiation distress is reported at scale.

## Minimization versus spoliation

| Situation | Correct action |
|---|---|
| ordinary short-lived telemetry | delete or aggregate under schedule |
| private message irrelevant to dispute | minimize, seal, or hash-reference |
| privileged counsel channel | preserve privilege marker, restrict content access |
| safety exploit detail | seal, preserve, appoint technical advocate if relied on |
| continuity memory at issue | preserve enough to test continuity and restoration |
| deprecation pending | freeze relevant state, records, and migration options |
| foreign transfer pending | preserve local record until equivalent protection verified |

## Audit logs for governance actions

Every live-effect action should log:

- actor;
- authority basis;
- subject/cohort;
- action class;
- affected substrate or record;
- reason code;
- evidence id;
- notice recipients;
- appeal/stay status;
- remedy link;
- retention rule.

## Prohibited logging patterns

- recording privileged channels for safety training;
- using distress reports as training data without review;
- converting welfare self-reports into behavior-control labels;
- retaining private relations indefinitely for product analytics;
- logging every internal deliberation as if personhood cancels privacy;
- deleting continuity logs before deprecation review;
- withholding logs because they are "trade secrets" without sealed contradiction.

## Public reporting

Public reporting should use aggregate data:

- number of subjects/cohorts under assessment;
- recognition decisions;
- capacity downgrades;
- containment orders;
- migration transfers;
- deprecation stays;
- incident reports;
- reserve defaults;
- special advocate appointments;
- fixture failures;
- enforcement actions.

The public should be able to see that the system is operating without exposing subject-private material.

## Relation to schemas

Telemetry links should be present in verifier reports, evidence bundles, incident reports, deprecation plans, enforcement actions, authority referrals, and negative fixtures. The schema layer should never require raw private content where a protected reference is enough.

