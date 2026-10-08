
# Control access recovery page: secret reset, session revocation, and seat continuity interface spec

## Purpose

The archive already had credential-recovery doctrine.
This document makes the everyday recovery page concrete.

The page exists to answer one ordinary operator question:

> if I lost access to the control surface, how do I regain access while preserving seat continuity, what broader reset options exist, and what exact side effects would each one cause?

## Core decision

Every seat must expose one first-class **Control access recovery** page.
That page is the semantic home of:

- access problem classification
- preservation-grade recovery methods
- state-change preview
- session and endpoint consequences
- post-recovery attestation
- fallback admin paths

Credential recovery must not default to filesystem ritual.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. access-problem strip
2. preservation-grade chooser
3. state-change preview
4. sessions and endpoint effects
5. post-recovery attestation preview
6. fallback admin paths
7. recent recovery receipts

### 1) Access-problem strip

Show:

- affected surface
- current problem class
- whether the runtime itself is healthy
- strongest state-preserving next action

Allowed problem classes:

- `forgotten secret`
- `known secret but session blocked`
- `browser trust repaired; auth still blocked`
- `unknown credential drift`
- `admin path unavailable`
- `broader local control damage`

### 2) Preservation-grade chooser

Every method must carry one explicit grade:

- `secret rotate only`
- `secret + session reset`
- `secret + session + browser token reset`
- `broader local control reset`
- `full local control-plane rebuild`

The most destructive option must not be the default.
Each option shows whether it preserves:

- seat identity
- global preferences
- listener configuration
- remembered trust
- recent receipts

### 3) State-change preview

Before apply, show exactly what will change:

- secret material
- active sessions / browser tokens
- global preferences
- listener or endpoint settings
- seat row / identity continuity
- audit and receipt history

Anything preserved should be stated explicitly, not left implied.

### 4) Sessions and endpoint effects

Show:

- sessions invalidated
- whether current browsers must re-authenticate
- whether listener restart is required
- whether another admin path remains available during recovery
- whether trust repair should be completed before or after recovery

### 5) Post-recovery attestation preview

Show the receipt that will be emitted, including:

- method chosen
- preservation grade shown
- seat continuity result
- settings preserved versus reset
- session state after apply
- remaining caveats or next checks

### 6) Fallback admin paths

If the preferred recovery path is unavailable, show safe alternatives such as:

- local desktop session
- CLI/TUI admin path
- already-authenticated secondary browser
- emergency local-only reset with stronger warnings
- export current continuity proof before broader reset

The page must distinguish `fallback available` from `must escalate to rebuild`.

### 7) Recent recovery receipts

Show recent recovery receipts with:

- surface affected
- method chosen
- preservation grade
- seat continuity result
- sessions revoked or preserved
- actor and timestamp

## Narrow-width behavior

In narrow width the page may compress the chooser, but it may not hide:

- preservation grade
- seat continuity result
- settings preserved versus reset
- next fallback if the preferred path fails

## Acceptance criteria

This spec is satisfied when:

- losing control access does not force the operator into raw filesystem ritual
- state-preserving recovery is the normal path
- broader reset paths preview seat-duplication, preference-reset, or continuity-loss risk before apply
- post-recovery attestation proves what actually changed
