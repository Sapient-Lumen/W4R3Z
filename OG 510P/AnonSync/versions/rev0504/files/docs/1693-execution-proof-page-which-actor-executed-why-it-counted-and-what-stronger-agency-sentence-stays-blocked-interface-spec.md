# Execution proof page — which actor executed, why it counted, and what stronger agency sentence stays blocked

## Purpose

This page is the durable proof object for the strongest honest execution sentence earned by a given act version.
It exists so later operators can see not merely that something happened, but who carried it out, why that actor class counted, what supervision applied, and what stronger execution sentence remained blocked.

## Sentences this page may support

- `the named principal executed the reversible act after fresh confirmation`
- `a delegate executed within a narrow authority lane while final waiver release stayed blocked`
- `a supervised agent prepared and routed the package, but a human performed the irreversible commit`
- `a linked device carried the notification and preserved continuity, but it was not counted as the executing actor`
- `automatic execution ran within a previously approved low-risk lane, while stronger autopilot use remained blocked for final settlement`

## Mandatory proof blocks

### A. Act-and-execution block

- source act identifier
- source version identifier
- exact effect that was attempted or executed
- highest execution sentence honestly earned
- strongest blocked stronger sentence
- exact reason the earned sentence stops where it does

### B. Actor-and-capacity block

- actor identity used
- whether the actor was a human principal, delegate, linked identity surrogate, device custodian, supervised agent, autopilot, or adjudicator
- whether that actor kind is sufficient for the exact typed effect
- whether substitution was expressly authorized
- strongest blocked stronger sentence if actor proof remains incomplete

### C. Freshness-and-trigger block

- whether standing mandate existed
- whether execute-now confirmation was required
- whether execute-now confirmation was obtained
- whether correction, recall, or supersession reset the mandate
- whether replay or stale-trigger risk was checked
- exact reason remembered trust was accepted or rejected for execution

### D. Supervision block

- whether human preview occurred
- whether dual control occurred
- whether agent execution was supervised
- whether rollback or abort remained available
- whether later challenge can reopen execution validity

### E. Audit block

- execution event bundle identifiers
- pre-execution approval identifiers
- supervision / countersign identifiers
- dispute / reopen / supersession identifiers
- next event that could strengthen or weaken the proof

## Required badges

- `execution-attempted`
- `execution-complete`
- `principal-executed`
- `delegate-executed`
- `agent-executed`
- `autopilot-executed`
- `fresh-trigger-obtained`
- `supervision-proven`
- `actor-kind-under-challenge`
- `stronger-autopilot-sentence-blocked`

Badges must stack instead of collapsing meaning.
For example, `execution-complete`, `agent-executed`, and `supervision-proven` may coexist with `stronger-autopilot-sentence-blocked`, while `delegate-executed` may coexist with `actor-kind-under-challenge` if authority is later disputed.

## Proof obligations

- prove assent separately from execution
- prove actor kind separately from actor identity convenience
- prove supervision separately from raw event completion
- preserve whether a fresh execute-now trigger was required and obtained
- preserve why the product refused a stronger `autopilot was fully authorized` sentence
- preserve which lower-risk lane counted even when a stronger irreversible lane stayed blocked

## Stronger-sentence guard

This page may say `the delegate executed the reversible hold-release under dual control, a supervised agent carried the transport step, and final autonomous settlement remained blocked because fresh principal-specific execute-now authorization was still required for the irreversible release`.
It may not say `the system was fully authorized to execute the settlement automatically` unless that stronger sentence was actually earned.
