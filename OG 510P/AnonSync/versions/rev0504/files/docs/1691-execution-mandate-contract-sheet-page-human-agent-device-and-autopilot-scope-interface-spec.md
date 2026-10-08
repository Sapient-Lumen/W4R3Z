# Execution-mandate contract sheet page — human, delegate, device, agent, and autopilot scope

## Purpose

This page is the canonical declaration of what kind of actor may actually carry out a typed act.
It exists so the product can stop pretending that `assented`, `owner`, `linked device`, `notification received`, and `execution-authorized` are the same truth.

The page must answer:

> for this act version, who may execute it, through what actor class, under what supervision, with what freshness requirement, and what stronger execution sentence remains blocked?

## Mandatory executor classes

At minimum the page must expose these classes separately:

- named human principal only
- named delegate may execute
- linked-identity substitute allowed
- linked-identity substitute forbidden
- device-only execution forbidden
- supervised agent execution allowed
- unsupervised autopilot allowed
- countersigned execution required
- adjudicator-triggered execution only
- execute-now reconfirmation required

The implementation may add more classes, but it may not collapse them into one generic `authorized` state.

## Mandatory blocks

### A. Act-and-version block

- source act identifier
- source version identifier
- exact effect to be executed
- exact execution class required for this version
- exact reason this execution class is required

### B. Executor-and-capacity block

- named executor or executor cohort
- whether the allowed executor is a human principal, delegated representative, linked identity, device custodian, agent, autopilot, or adjudicator
- whether owner status is relevant
- whether identity or device substitution is allowed for this exact act
- strongest blocked stronger sentence if actor kind remains under-proved

### C. Supervision-and-dual-control block

- whether human-in-the-loop is required
- whether dual control or countersign execution is required
- whether pre-execution preview is mandatory
- whether agent execution requires named supervisor
- whether unsupervised autopilot is ever allowed for this row
- exact reason the product refuses stronger autonomous execution

### D. Freshness-and-replay block

- whether standing mandate exists
- whether a fresh execute-now confirmation is required
- whether prior assent may be reused for execution
- whether corrections, recalls, or supersession reset the mandate
- what replay protections apply
- what expires the mandate

### E. Effect-and-rollback block

- which typed effects may be executed under the current mandate
- which stronger irreversible effects remain blocked
- whether rollback, pause, or manual interruption is required
- whether execution may start automatically but finish only after human release
- what happens if the acting capacity is later challenged

## Required comparisons

The page must keep these comparisons explicit:

- `assented` vs `execution-mandated`
- `human principal` vs `delegate`
- `delegate` vs `supervised agent`
- `supervised agent` vs `unsupervised autopilot`
- `standing mandate` vs `fresh execute-now confirmation`

## Required badges

- `assented-not-yet-execution-mandated`
- `human-only`
- `delegate-allowed`
- `linked-identity-substitute-used`
- `device-only-blocked`
- `supervised-agent-allowed`
- `autopilot-blocked`
- `execute-now-confirmation-required`
- `dual-control-required`
- `execution-claim-blocked`

## Failure modes the page must prevent

- treating assent as proof that anyone may now execute
- treating owner status as proof of fairness-grade execution authority
- treating linked-device convenience as proof of named-human execution authorization
- letting old assent or remembered trust silently authorize a new irreversible execution
- hiding when automation is allowed only for reversible or low-risk effects

## Stronger-sentence guard

The page may say `the principal assented to provisional settlement terms, a named delegate may prepare execution, but unsupervised autopilot remains blocked and fresh execute-now confirmation is still required for final waiver release`.
It may not say `the system is authorized to carry this out automatically` until that stronger sentence is actually earned.
