# Incident case contract sheet page: symptom cluster, hypotheses, and target sentence interface spec

## Purpose

The archive already had pages for intervention choice and remediation execution.
What it still lacked was one ordinary page for the next operator question:

> what exact case are we working, what symptoms belong to it, what hypotheses are on the table, and what sentence are we trying to earn before we dare call it closed?

Current official Resilio docs make this seam concrete because they already force operators to pivot among warnings, history, queues, logs, support notes, and article-specific explanations.
The missing piece is the one durable case object that joins those strands without overclaiming certainty.

## Core decision

AnonSync must expose one first-class **Incident case contract sheet** whenever:

- a symptom survives beyond a trivial local observation window
- more than one plausible cause exists
- any remediation run has started or been considered
- any support or forum escalation artifact is created
- recurrence or reopen becomes a serious possibility

The sheet exists to answer ten things in one place:

1. what symptom cluster defines the case
2. what subject scope is affected
3. what evidence families are currently in play
4. what hypotheses are being considered
5. what confidence floor the operator is currently willing to state
6. what strongest target sentence the case is trying to unlock
7. what weaker sentence is already safe
8. who owns the case and its next review
9. what remediation runs or support artifacts are attached
10. what closure class is still impossible to claim

## Fixed page order

1. **Case header**
2. **Symptom cluster card**
3. **Evidence inventory**
4. **Hypothesis ledger**
5. **Target sentence and confidence floor**
6. **Residual risk teaser**

### 1) Case header

Show at minimum:

- `case_id`
- case title
- created time
- active owner
- severity
- current phase
- linked rollout / intervention / remediation-run ids
- latest update time

Supported `current_phase` values must include:

- `triage`
- `evidence-gathering`
- `hypothesis-review`
- `remediation-active`
- `awaiting-observation`
- `awaiting-escalation`
- `closure-review`
- `closed`
- `reopened`

### 2) Symptom cluster card

Publish explicit rows for:

- primary visible symptom
- secondary symptoms
- first observed time
- latest observed time
- affected subjects
- affected worlds / lanes
- recurrence posture
- user-visible impact

Supported `recurrence_posture` values:

- `first-known-occurrence`
- `seen-before-same-shape`
- `seen-before-not-proven-same-cause`
- `recurring-known-cause`
- `reopen-of-prior-case`

Hard rule:

Similar visible symptoms may share a cluster only when the product can say whether the join is based on topology, identity, timing, warning code, or operator judgment.

### 3) Evidence inventory

Each row is one evidence object.
Required columns:

- `evidence_id`
- evidence class
- captured time
- freshness window
- source surface
- subject scope
- summary
- confidence contribution
- stale / superseded marker

Supported `evidence_class` values must include:

- `warning-or-status`
- `history-event`
- `queue-or-peer-view`
- `live-metric`
- `filesystem-or-path-check`
- `runtime-or-service-state`
- `artifact-log`
- `operator-note`
- `support-or-forum-reply`

Hard rule:

Evidence may support a hypothesis, refute a hypothesis, or remain neutral, but the page must never force one evidentiary direction when the operator has not made that claim.

### 4) Hypothesis ledger

Each row is one current hypothesis.
Required columns:

- `hypothesis_id`
- label
- cause family
- current status
- supporting evidence ids
- refuting evidence ids
- expected next discriminator
- owner

Supported `cause_family` values must include:

- `topology-or-peer-state`
- `path-or-filesystem-state`
- `identity-or-certificate-state`
- `internal-metadata-or-database-state`
- `runtime-or-resource-pressure`
- `permission-or-principal-mismatch`
- `config-or-world-divergence`
- `external-environment`
- `unknown`

Supported `current_status` values:

- `candidate`
- `favored`
- `supported-not-exclusive`
- `primary-working-cause`
- `refuted`
- `parked`
- `merged-into-another`

### 5) Target sentence and confidence floor

Show three stacked sentences:

- **safe now**
- **target to earn**
- **still blocked**

Example:

- safe now: `sync resumed after reconnect`
- target to earn: `sync resumed because tracker reachability was restored`
- still blocked: `all affected peers are stable and no recurrence remains likely`

Also show:

- current confidence floor
- what new evidence would raise it
- what new evidence would collapse it

Supported `confidence_floor` values:

- `weak-observation`
- `plausible`
- `supported`
- `strong-but-not-exclusive`
- `best-current-explanation`

### 6) Residual risk teaser

Before closure review, the contract sheet must already preview:

- known residual risk class
- current reopen trigger count
- time-to-next-review
- strongest statement forbidden at this moment

Supported `residual_risk_class` values:

- `none-proven`
- `low-known`
- `moderate-known`
- `high-known`
- `unknown`

## Mandatory interaction rules

- The page must not auto-collapse all losing hypotheses into `wrong`; some may remain unresolved.
- The page must not let a remediation run auto-promote a cause to `primary-working-cause` without explicit adjudication.
- The page must preserve contradictory evidence rather than silently pruning it.
- The page must show when two cases were merged and what sentence became weaker or stronger because of the merge.

## Why this page exists

The operator should not have to reconstruct a case from warnings, KB pages, queue screenshots, log bundles, and memory.
The product should own the case object directly.
