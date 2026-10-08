# Decision proof page: allowed action, blocked stronger action, and uncertainty budget interface spec

## Purpose

After review, the operator still needs one proof page that says:

> what exactly are we allowed to do now, why is that the strongest honest move, and what uncertainty remains too large for a stronger move?

## Proof sections

1. **Proof headline**
2. **Allowed-action proof block**
3. **Threshold-basis block**
4. **Residual-uncertainty block**
5. **Blocked-stronger-action block**
6. **Fallback-and-reopen block**

### 1) Proof headline

Show:

- allowed next verb
- exact scope
- decision grade
- evidence freshness posture
- residual uncertainty class

Supported `decision_grade` values:

- `observe-grade`
- `monitor-grade`
- `bounded-action-grade`
- `escalation-grade`
- `publication-grade`
- `freeze-grade`

### 2) Allowed-action proof block

Required rows:

- action verb
- scope bound
- preconditions satisfied
- safeguards required
- post-action witness required
- maximum sentence that action authorizes later

Hard rule:

An allowed action proof must say what the action **does not** authorize.

### 3) Threshold-basis block

Required rows:

- threshold cleared
- synthesis ids relied on
- decisive packets or witnesses
- decisive contradiction handling
- why the next lower route is insufficient

### 4) Residual-uncertainty block

Required rows:

- open uncertainty items
- why tolerated here
- why not tolerable for stronger route
- downgrade trigger

Hard rule:

If residual uncertainty is tolerated, the page must state whether the choice is robust-to-error or merely time-favored.

### 5) Blocked-stronger-action block

Required rows:

- blocked stronger action
- exact blocker class
- evidence or event needed to clear blocker
- whether the blocker is likely, hard, or impossible to clear

Supported `blocker_clearability` values:

- `cheap-to-clear`
- `moderate-cost`
- `heavy-burden`
- `unlikely-to-clear`
- `structurally-impossible`

### 6) Fallback-and-reopen block

Required rows:

- fallback posture if no further evidence arrives
- automatic reopen triggers
- expiry time for current proof
- next owner on reopen

Hard rule:

Every proof must expire or revalidate on an explicit basis; silent forever-valid decision proofs are not allowed.
