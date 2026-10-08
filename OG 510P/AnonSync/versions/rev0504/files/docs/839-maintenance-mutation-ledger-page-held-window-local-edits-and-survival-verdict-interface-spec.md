# Maintenance mutation ledger page — held window, local edits, and survival verdict interface spec

## Purpose

Once a maintenance window is live, the product should not make operators remember later whether local work happened, which files were touched, and which of those edits were in-budget or doomed.
This page exists to stop `I think I only looked around` folklore.

## Core decision

AnonSync must expose one first-class **Maintenance mutation ledger** page whenever any local mutation attempt occurs under an active maintenance contract, narrow-rights seat, preservation node, or backup-like posture.

The page exists to answer five things in one place:

1. what local mutation attempts occurred during the held window
2. which attempts were in-budget versus out-of-budget
3. which attempts survived, suspended continuity, or were overwritten
4. which attempts still need repair or export follow-up
5. what later sentence is still safe to use about the window

## Fixed page order

1. **Ledger verdict**
2. **Window and mutation timeline**
3. **Per-path survival verdicts**
4. **Repair / export follow-up**
5. **Actions and receipts**

### 1) Ledger verdict

Show:

- `maintenance_mutation_ledger_page_id`
- scope
- active maintenance contract reference
- held-window start and end or `still-open`
- aggregate verdict (`no-local-mutations`, `all-in-budget`, `mixed`, `continuity-suspended`, `overwritten-work`, `unknown`)
- strongest honest summary

The operator must be able to answer:

> what happened locally during this maintenance window overall?

### 2) Window and mutation timeline

Show events in order:

- hold entered
- local mutation attempted
- local mutation completed or blocked
- later overwrite or repair event
- export / branch save event
- contract exit or supersession

Each event row must show:

- actor or seat if known
- action class
- affected path or scope slice
- immediate verdict
- successor event if any

### 3) Per-path survival verdicts

For each affected path or cluster show:

- last local mutation class
- current survival state (`survived`, `local-only`, `suspended`, `overwritten`, `exported-elsewhere`, `unknown`)
- continuity status now
- whether evidence or notes were also affected
- strongest safe per-path sentence

This section is the stable answer to:

> which local work is still real here, and which work lost continuity or got replaced?

### 4) Repair / export follow-up

Show open obligations such as:

- `export surviving scratch now`
- `repair suspended continuity`
- `confirm overwrite was intentional`
- `promote side branch back under review`
- `reopen maintenance claim ceiling`

Each obligation must state:

- why it remains open
- what proof would close it
- whether any stronger sentence is blocked until closure

### 5) Actions and receipts

Actions may include:

- `Acknowledge ledger`
- `Open repair lane`
- `Open export lane`
- `Supersede with mutation receipt`
- `Reopen maintenance contract`
- `Cancel`

Receipts must record the held window, mutation attempts, per-path survival verdicts, and remaining follow-up.

## Public object

### Maintenance mutation ledger page

Fields:

- `maintenance_mutation_ledger_page_id`
- `scope_ref`
- `maintenance_contract_ref`
- `window_start`
- `window_end`
- `mutation_event_rows[]`
- `path_survival_rows[]`
- `followup_rows[]`
- `aggregate_verdict`
- `strongest_safe_sentence`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. scope
2. aggregate verdict
3. strongest surviving risk
4. blocked stronger sentence
5. next action

Example:

```text
Evidence backup seat     mixed     two edited files would be overwritten by later heal     cannot claim safe local work without export     Open export lane
```

## Non-goals

This page does **not** replace the maintenance contract itself.
It records only the local **mutation history and survival verdicts** inside that contract's window.
