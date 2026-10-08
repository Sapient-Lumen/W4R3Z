# Intervention approval proof page: chosen action, rollback, and post-action-check interface spec

## Purpose

The **Intervention approval proof** is the durable decision page that justifies why one intervention candidate was chosen and how it will be judged afterward.
It sits between ladder review and actual execution.

## Core operator question

> what exact standard did this intervention satisfy before we took it, and what exact proof will determine whether it helped, partially helped, failed, or merely moved the problem?

## Required sections

### 1) Approval basis

Show:

- intervention id
- linked health object / incident / rollout
- chosen action class
- chosen scope
- chosen operator or authority level
- current urgency
- current strongest safe sentence

### 2) Why this action won

Separate these verdicts explicitly:

- evidence fit
- destructiveness fit
- reversibility fit
- scope fit
- coordination fit
- time-to-signal fit
- post-action-proof clarity

Each must show `pass`, `partial`, `fail`, or `unknown`.

### 3) Rejected alternatives

Show at least:

- strongest weaker candidate rejected and why
- strongest stronger candidate rejected and why
- escalation candidate rejected or required and why

Examples:

- `restart-client` rejected because symptom plane is network route, not local watcher state
- `re-add-folder` rejected because connectivity proof is still weak and data movement risk is unnecessary
- `world-shift` rejected because service-account fork would abandon current storage world prematurely
- `collect-artifacts` required before destructive action

### 4) Execution boundary

This section must state exactly:

- what is allowed to change
- what must not change
- whether restart is included
- whether multiple peers or devices must coordinate
- whether backups, snapshots, or receipts are required first
- what abort condition stops execution midstream

### 5) Rollback or containment class

Supported classes:

- `no-rollback-needed`
- `undo-immediately-if-no-signal`
- `revert-if-symptom-worsens`
- `contain-after-partial-success`
- `cannot-cleanly-rollback`
- `rollback-unknown`

Rules:

- any action that abandons metadata, identity, or storage world must not use a weak rollback label
- `can re-add later` is not sufficient rollback language for a world-fork action

### 6) Post-action check plan

Show:

- first check time
- observation window end
- success predicate
- failure predicate
- partial-success predicate
- stronger sentence still blocked after nominal success

Supported result states:

- `helped-but-cause-unclear`
- `helped-and-cause-supported`
- `no-material-change`
- `worsened`
- `shifted-symptom-plane`
- `artifact-collected-only`

### 7) Escalation-after-failure path

If the action fails or only partially helps, publish the next move explicitly:

- next ladder rung
- extra artifacts required
- cooldown before retry
- who must approve the next rung

## Hard rules

- proof pages must preserve why weaker and stronger actions lost
- execution without a post-action check plan is invalid
- `symptom quieter` must stay weaker than `problem solved`
- any action that changes runtime world must publish `cannot-cleanly-rollback` unless a real clean merge path exists
