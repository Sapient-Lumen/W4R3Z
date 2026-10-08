# Remediation-ladder review page: least-destructive next action and escalation interface spec

## Purpose

The intervention contract sheet summarizes candidate actions.
The **Remediation-ladder review** is the deeper working page where the operator compares them.

It exists because current Resilio material still forces operators to hop among troubleshooting articles in order to infer whether they should:

- wait
- rescan
- restart
- reconnect
- re-add
- relink identity
- change network or service configuration
- gather artifacts
- escalate

AnonSync should make that ladder explicit.

## Core operator question

> given the evidence we have, what is the least-destructive intervention that is actually justified right now, and why are weaker or stronger actions wrong at this moment?

## Fixed page order

1. **Ladder stage strip**
2. **Candidate comparison table**
3. **Rejection reasons panel**
4. **Escalation trigger panel**
5. **Decision outcome strip**

### 1) Ladder stage strip

The page must show the ordered ladder stages explicitly.
Supported stages:

1. `observe-and-bound`
2. `cheap-local-repair`
3. `scoped-rebind`
4. `metadata-rebuild`
5. `identity-or-world-shift`
6. `artifact-and-human-escalation`

Meaning:

- `observe-and-bound` covers wait, cooldown, and manual observation windows
- `cheap-local-repair` covers rescan, restart, temporary cleanup, low-risk path adjustments
- `scoped-rebind` covers reconnecting one folder or repairing one connection path
- `metadata-rebuild` covers re-add or local metadata recreation
- `identity-or-world-shift` covers identity rebuild, service-user change, or runtime-world migration
- `artifact-and-human-escalation` covers log/profiler/dump capture and human support escalation

### 2) Candidate comparison table

Rows are candidate interventions.
Columns must include at least:

- ladder stage
- evidence fit
- urgency fit
- blast radius
- reversibility
- coordination scope
- expected time to signal
- post-action proof burden
- chance of masking root cause
- recommendation verdict

Supported recommendation verdicts:

- `preferred-now`
- `allowed-not-preferred`
- `premature`
- `too-destructive`
- `insufficient`
- `blocked-by-prerequisite`
- `reserve-if-failure`

### 3) Rejection reasons panel

The page must force explicit rejection reasons for both weaker and stronger actions.
Supported reasons must include:

- `symptom-severity-too-high-to-wait`
- `evidence-too-weak-for-destructive-action`
- `restart-would-not-change-relevant-plane`
- `reconnect-too-narrow-for-cohort-symptom`
- `readd-premature-before-connectivity-proof`
- `identity-rebuild-too-destructive`
- `world-shift-creates-unacceptable-fork`
- `artifact-capture-needed-first`
- `support-escalation-premature`
- `support-escalation-now-required`

### 4) Escalation trigger panel

Escalation must not be a vague footer.
Show explicit triggers such as:

- two or more failed local stages
- destructive stage blocked by weak causal evidence
- evidence requires restart-bound artifact capture
- multi-subject coordination cost exceeds local operator authority
- probable known issue with insufficient local workaround
- policy or data-loss risk too high for autonomous action

For each trigger show:

- minimum artifact bundle
- minimum symptom description
- whether repro is still needed
- whether cooldown or additional observation is required before escalation

### 5) Decision outcome strip

Supported outcomes:

- `continue-observing`
- `execute-cheap-local-repair`
- `execute-scoped-rebind`
- `execute-metadata-rebuild`
- `execute-identity-or-world-shift`
- `collect-artifacts-then-reassess`
- `escalate-now`
- `stop-and-contain`

## Comparison heuristics

The page must highlight at least these heuristics:

1. **Least destructive viable action wins.**
2. **Evidence collection is often cheaper than world replacement.**
3. **A fix that only clears the symptom but hides the cause must show that masking risk.**
4. **Actions that fork storage world or abandon metadata require stronger justification than restart or reconnect.**
5. **If the product cannot explain post-action proof, the action is not ready to execute.**

## Hard rules

- no stronger-stage action may win by default just because it sounds decisive
- `worked once before` cannot replace current evidence fit
- operator convenience cannot hide world-fork or data-loss risk
- every chosen action must show what observation would make the next rung necessary if it fails
