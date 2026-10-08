# Temporal lineage receipt page — time authority, ordering basis, and blocked stronger sentences

## Purpose

Create a durable artifact for later operators so they do not need to remember power-user settings, clock incidents, or restore caveats to know what time-based claim was actually justified at action time.

## Receipt sections

### 1. Action summary

Show:

- action kind
- subject
- acting seat
- completed at

### 2. Time basis at action time

Show:

- ordering basis trusted then
- skew budget
- confidence class
- whether ledger-only `mtime` authority was involved

### 3. Timestamp provenance snapshot

Show:

- disk-visible timestamp snapshot
- ledger timestamp snapshot
- divergence verdict

### 4. Outcome sentence

Examples:

- `Replay completed under guarded chronology; ledger mtime remained authoritative.`
- `Freshness claim accepted only for trusted peers within drift budget.`
- `Disk-visible mtime was not proof of winning chronology.`

### 5. Blocked stronger sentence

Examples:

- `Do not read filesystem timestamp alone as swarm truth.`
- `Do not infer restored candidate will stay winner after later peer return.`
- `Do not infer all peers were within chronology budget.`

### 6. Invalidators

Show:

- later peer return
- time-source degradation
- rescan after offline restore
- loss of ledger proof

## Required fields

- receipt identifier
- action identifier
- ordering basis
- skew budget
- confidence class
- disk vs ledger divergence snapshot
- strongest safe sentence
- stronger rejected sentence
- invalidators

## Interaction rules

- Exported receipts must remain readable without the live system.
- Copying a receipt snippet should preserve the blocked stronger sentence by default.
- Receipts should be linkable from replay, completion, evidence, and repair flows.
