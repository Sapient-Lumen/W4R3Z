# Intervention-lineage receipt page: action basis, reversibility, and outcome ceiling interface spec

## Purpose

The **Intervention-lineage receipt** is the durable receipt produced after any material intervention or explicit decision to continue observing.

It exists to prevent later operators from having to guess:

- what action was actually taken
- why that action was chosen
- what it touched
- how reversible it really was
- what sentence it legitimately proved
- what stronger claim remained blocked

## Required fields

### 1) Identity block

Show:

- `intervention_receipt_id`
- intervention id
- linked incident / health / rollout id
- action class
- scope touched
- execution time window
- executing authority

### 2) Basis block

Show:

- current problem sentence before action
- evidence basis summary
- ladder rung
- chosen-action reason
- weaker action rejection summary
- stronger action rejection summary

### 3) Risk block

Show:

- blast radius class
- reversibility class
- restart involvement
- coordination scope
- world-fork risk
- data-loss risk

### 4) Outcome block

Supported outcome classes:

- `observe-only-completed`
- `symptom-cleared`
- `partial-relief`
- `no-material-change`
- `worsened`
- `artifact-captured`
- `escalated`
- `rolled-back`
- `world-shifted`

For each outcome show:

- observation window used
- outcome sentence
- strongest safe sentence now allowed
- stronger sentence still blocked

### 5) Next-step block

Show explicitly:

- no further action
- continue observation
- retry same rung after cooldown
- advance one rung
- escalate
- contain and stop

## Mandatory receipt language rules

- `worked` is forbidden without an outcome class and safe sentence
- `fixed` is forbidden unless the receipt can support root-cause removal rather than symptom disappearance alone
- `reversible` is forbidden unless the receipt names the actual revert path
- `temporary recovery` and `durable recovery` must stay separate

## Example blocked-stronger-sentence patterns

- `Connectivity resumed after port/routing repair` still weaker than `all peer-path instability causes removed`.
- `Sync resumed after restart` still weaker than `watcher delivery and background scan behavior are now reliable`.
- `Folder re-added and metadata rebuilt` still weaker than `original corruption root cause identified`.
- `Service now writes successfully as Local System` still weaker than `previous service world preserved without re-share cost`.

## Hard rules

- every material intervention must produce a receipt even when the chosen action was `wait-and-observe`
- receipts must preserve both what the action changed and what it did not prove
- world-fork actions must preserve the discontinuity plainly
