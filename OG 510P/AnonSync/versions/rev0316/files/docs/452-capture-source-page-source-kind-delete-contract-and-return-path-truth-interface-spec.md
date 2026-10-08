# Capture source page: source kind, delete contract, and return-path truth interface spec

## Purpose

This page answers:

> what exact mobile source am I attaching here, and what will later deletion or editing on that source mean?

The page exists because `Add Backup`, `Camera Backup`, `Create folder`, `Scan QR`, and `Send file` are not the same contract.

## Core rule

Every mobile-origin subject or flow must expose one first-class **Capture source** page before apply.
That page owns:

- source kind
- source location class
- mutability direction
- source-side delete contract
- return-path truth

## Primary layout

The page always renders the same regions:

1. source verdict
2. source-kind card
3. delete / return contract card
4. path witness card
5. next review and receipt

### 1) Source verdict

Show:

- source label
- source kind verdict: `live-sync`, `capture-only`, `camera-roll-backup`, `android-folder-backup`, `one-off-transfer`, `copied-out-working-file`, `unknown`
- strongest honest operator summary
- one next honest action

### 2) Source-kind card

Show:

- exact origin class
- whether bytes will continue to update automatically
- whether downstream edits ever flow back
- whether the subject is continuous, capture-only, or bounded

The operator must be able to answer: **what kind of mobile source is this really?**

### 3) Delete / return contract card

Show:

- what source-side deletion does after landing
- whether sink-side deletion ever returns upstream
- whether edited bytes must be re-imported manually
- whether duplicate or parallel versions are expected during save-back

The operator must be able to answer: **what later delete or edit means here?**

### 4) Path witness card

Show:

- current source path or source authority witness
- whether the app has direct read access, delegated provider access, or only sandbox-local access
- whether this chooser is selecting bytes, selecting authority, or both

The operator must be able to answer: **what exact source am I reading from, and by what authority?**

### 5) Next review and receipt

Show links to:

- Mobile path class
- Capture sink
- Mobile reacquire

After apply, emit a receipt that preserves:

- source kind
- source authority witness
- delete contract summary
- return-path summary

## Honest outputs

This page may conclude:

- `camera-roll backup with no sink-to-source delete propagation`
- `android folder backup from custom path`
- `source-only external card backup`
- `copied-out iOS working file requiring manual save-back`
- `live sync subject rather than capture-only backup`
- `one-off transfer with no return path`

It may not collapse these into one generic `mobile share` verdict.

## Rules

### Rule 1 — source kind must be named before bytes move

The page must not rely on menu placement or a plus-menu label to convey subject kind.

### Rule 2 — source-side deletion must stay adjacent to source kind

Operators should not discover later that deleting on the phone preserved the sink copy, or that deleting on the sink could not affect the source.

### Rule 3 — return path must be explicit

If edits require manual re-import, save-back, or replacement rather than live sync, the page must say so directly.

## Acceptance test

This page is good enough when a cautious operator can answer all of the following without leaving it:

- what exact source class is under review
- whether this is live sync, capture-only backup, or one-off transfer
- what deletion on the phone will mean later
- whether sink-side edits or deletes can propagate back
- whether changed bytes must be returned manually
