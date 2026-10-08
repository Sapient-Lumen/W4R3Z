# Resource budget lineage receipt page — budget precedence, fairness, and starvation risk

## Purpose

Emit a durable receipt for any meaningful resource-budget decision or diagnosed bottleneck.

This page exists to answer later:

- `what budget or proof did we rely on at that moment?`
- `which plane won precedence?`
- `what fairness or starvation warnings were active?`
- `what stronger sentence was explicitly blocked?`

## Required receipt fields

### 1. Receipt header

Must show:

- receipt id
- timestamp
- subject / runtime scope
- originating action (`budget edit`, `schedule apply`, `priority change`, `pressure proof`, `starvation review`, `other`)

### 2. Winning-plane summary

Must show:

- winning budget plane
- losing / shadowed planes
- affected lanes
- activation basis
- restart or context conditions if any

### 3. Fairness / starvation summary

Must show:

- whether preemption is allowed
- whether queue cap risk was present
- whether visible order matched execution order
- whether low-priority work was already suspended

### 4. Claim ceiling summary

Must show:

- strongest safe sentence
- blocked stronger sentence
- confidence level
- invalidators

### 5. After-effects summary

Must show:

- who may slow down
- which shares or peers remain uncapped
- what follow-up proof or watch was opened

## Minimum interactions

The page must expose actions to:

- copy receipt id
- open originating review or proof
- compare against latest budget state
- export receipt bundle