# Control promotion review page: prevent, detect, mitigate, watch, and no-control verdict interface spec

## Purpose

The contract sheet names the candidate guardrail.
This page answers the harder product question:

> does this case actually justify a preventive control, only a watch, only a capture-on-repeat runbook, or no reusable control at all?

## Core decision

AnonSync must expose one first-class **Control promotion review** before any closed case can claim it has been turned into operational learning.

## Fixed page order

1. **Promotion header**
2. **Candidate verdict matrix**
3. **Evidence and repeatability review**
4. **Scope-fit and cost review**
5. **Escape and false-positive review**
6. **Decision sentence**

### 1) Promotion header

Show:

- linked case id
- proposed control id
- proposer
- reviewer
- review date
- source closure class
- current repeat pressure
- requested verdict

Supported `requested_verdict` values:

- `promote-preventive-control`
- `promote-detective-watch`
- `promote-containment-control`
- `promote-capture-on-repeat`
- `record-non-preventable`
- `record-accepted-risk`

### 2) Candidate verdict matrix

Each verdict row must show:

- what sentence it would unlock
- evidence required
- repeat shape required
- rollout burden
- operator burden
- escape risk
- reason it won or lost

Hard rule:

`we changed something after the case` is never enough to win `promote-preventive-control`.

### 3) Evidence and repeatability review

Required questions:

- was the favored cause sufficiently supported
- has the hazard repeated before
- would the same control have changed the past outcome
- is the mechanism stable across versions / worlds / lanes
- is the control only local, or truly reusable
- do we have enough evidence to distinguish prevention from early detection

Supported `repeatability_verdict` values:

- `reusable-same-cause`
- `reusable-same-symptom-only`
- `world-bound-only`
- `single-case-insufficient`
- `pattern-known-but-mechanism-uncertain`

### 4) Scope-fit and cost review

Publish explicit rows for:

- scope of benefit
- scope of collateral cost
- restart or downtime cost
- policy/profile fit
- config/service/world divergence risk
- training burden
- maintenance burden
- expiry / rereview trigger

Hard rule:

A control that is expensive, world-fragile, or restart-heavy may still win, but the page must make that burden visible before approval.

### 5) Escape and false-positive review

Each candidate must answer:

- what repeats would escape the control
- what lookalikes it may wrongly classify
- what near misses it would catch
- what evidence would prove the control failed
- what evidence would prove only the watch succeeded

Supported `escape_class` values:

- `same-cause-escape`
- `different-cause-same-symptom`
- `world-out-of-scope`
- `version-drift`
- `operator-bypass`
- `insufficient-signal`

### 6) Decision sentence

The page ends with one required sentence in this shape:

> `From case <id>, we are promoting <control/watching/no-control verdict> for hazard <signature> across <scope>, because <basis>, while still blocked from claiming <stronger preventive sentence>.`

Hard rule:

Every losing verdict must preserve a short reason, so that `why not preventive?` does not disappear into memory.
