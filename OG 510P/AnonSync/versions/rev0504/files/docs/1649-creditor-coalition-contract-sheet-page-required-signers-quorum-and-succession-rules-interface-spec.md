# Creditor coalition contract sheet page — required signers, quorum, and succession rules

## Purpose

This page is the canonical object for the question:

> for this creditor or creditor slice, whose signatures count, how many are required for each action, what counts as quorum, and how does successor authority replace or inherit a predecessor's role?

It exists so the archive never has to smuggle closure sufficiency through `someone important signed`, `an Owner approved it`, or `nobody objected in time`.

## Primary questions the page must answer

1. Is final closure single-signer, countersigned, quorum-based, unanimous, or adjudicated?
2. Which signer classes count for each action?
3. Which actions can proceed with fewer signatures than final release?
4. What happens when a required signer exits, is replaced, or is unreachable?
5. Which stronger closure sentences remain blocked because the coalition rule is not yet satisfied?

## Required fields

### A. Source-case block

- source creditor authority contract sheet
- source creditor claim contract sheet
- source restoration, probation, or burst-debt case if present
- current creditor verification posture
- strongest blocked sentence before coalition analysis
- current future-burst posture

### B. Coalition-rule block

- coalition model (`single-signer`, `countersigned`, `quorum`, `unanimous`, `adjudicated`, `hybrid`)
- signer universe definition
- minimum signer count for payment acknowledgment
- minimum signer count for partial settlement
- minimum signer count for final waiver
- minimum signer count for probation lift
- minimum signer count for reopen or closure challenge
- whether abstention can count
- whether silence can count
- whether timeout can count
- exact stronger sentence allowed only after full coalition satisfaction

### C. Signer-roster block

For each signer or seat the page must show:

- signer seat name or role label
- current occupant or `vacant`
- signer class (`principal`, `delegate`, `role-holder`, `reserve-guardian`, `policy-seat`, `adjudicator`, `observer`)
- seat status (`active`, `pending`, `vacant`, `suspended`, `revoked`, `challenged`)
- whether this seat is mandatory, optional, substitute, or advisory
- whether this seat may sign alone for any action
- whether this seat only counts with a countersigner

### D. Successor-and-vacancy block

- successor rule (`automatic-by-role`, `manual-reappointment`, `principal-reconfirmation`, `policy-rollover`, `none`)
- whether predecessor signature survives seat turnover
- whether successor may ratify earlier unsigned or partially signed actions
- whether vacancy pauses all action or only stronger actions
- maximum temporary vacancy horizon before adjudication or freeze escalation

### E. Conflict-and-dominance block

- how disagreement is represented (`freeze`, `majority`, `principal-overrides`, `adjudicator-decides`, `policy-ordering`, `other`)
- whether a lower action may proceed while higher action freezes
- whether one signer can veto partial settlement
- whether one signer can veto final waiver
- exact evidence required to resolve conflict

### F. Consequence block

- actions currently unlocked
- actions currently blocked
- weakest true sentence now
- strongest sentence now earned
- next missing signer, seat fill, or adjudication needed
- whether restoration or future-burst release stays frozen because coalition sufficiency is incomplete

## Required badges

- `single-signer-sufficient`
- `countersign-required`
- `quorum-not-met`
- `unanimity-not-met`
- `vacant-required-seat`
- `successor-not-ratified`
- `conflict-freeze-active`
- `partial-action-allowed`
- `final-release-blocked`
- `adjudication-required`

Badges must stack rather than collapse.
For example, `partial-action-allowed` may coexist with `vacant-required-seat` and `final-release-blocked`.

## Hard rules

- finality thresholds must be typed per action, not inferred globally
- silence counts only when the coalition rule explicitly says so
- successor rules must be explicit; role rename or seat reassignment alone is not enough
- coalition sufficiency must be recomputed after revocation, turnover, challenge, or seat vacancy
- blocked stronger sentences must remain visible even when weaker actions can still proceed

## Stronger-sentence guard

This page may say `ops and finance both required for final waiver; ops alone may acknowledge reserve receipt`.
It may not say `creditor fully released` until the final-waiver coalition rule is genuinely satisfied.
