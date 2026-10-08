# Recovery host choice page: witness seat, runtime liveness, and replay locus interface spec

## Purpose

This page answers one ordinary operator question:

> now that I know where the witness bytes live, which host should perform the recovery work, and will the chosen recovery shape actually stick?

The page exists because `recover this file` still collapses several materially different operations:

- export bytes for inspection from the witness seat
- restore locally on the witness seat only
- replay back into live shared state from a suitable host
- nominate a different host because the current host cannot safely complete the replay

## Core decision

Every non-trivial rollback workflow must compile to one first-class **Recovery host choice** page.
That page owns:

- chosen witness seat
- requested recovery shape
- daemon/watch liveness prerequisites
- replay locus and expected propagation
- re-archive / chronology rejection risk
- strongest next safe action

The product must not let `open archive`, `copy out file`, and `make this live again everywhere` blur together.

## Primary layout

The page always renders the same regions in the same order:

1. recovery strip
2. witness-host card
3. requested-recovery-shape card
4. runtime-liveness card
5. replay-locus card
6. safer-alternative card
7. recovery receipts

### 1) Recovery strip

Show:

- subject path
- selected candidate witness seat
- requested recovery shape (`export`, `inspect-local`, `replace-live-local`, `replay-sharewide`, `side-by-side`) 
- verdict (`safe-now`, `guarded`, `host-switch-needed`, `history-join-needed`, `blocked`)
- one next honest action

### 2) Witness-host card

Show:

- chosen witness seat and why it was chosen
- whether it actually holds the bytes or only coordinates another seat
- surface/channel used for recovery
- whether this host is plaintext-capable, ciphertext-only, or metadata-only
- whether the current acting seat is remote-controlling, directly operating, or merely nominating the host

### 3) Requested-recovery-shape card

Show:

- whether the operator intends export, local inspection, local replacement, or share-visible replay
- whether the requested shape changes shared state or only local state
- whether the requested shape is honest from this host class
- what stronger or weaker shapes are available from the same host

### 4) Runtime-liveness card

Show:

- whether the engine / daemon must be running now on the witness host
- whether watch state is fresh enough for replay to be recognized as the intended winner
- whether delayed rescan would likely demote the restored file back into archive/history
- whether peer reachability matters now for the requested shape

This card should answer `will recovery from this host actually behave as intended at runtime?`

### 5) Replay-locus card

Show:

- where the restored bytes will first become live
- whether propagation is expected, guarded, or intentionally absent
- whether chronology or newer peer state is likely to reject the replay
- whether the chosen action is best understood as export, inspection, replacement, or distributed mutation

This card should answer `where does the recovery become real, and for whom?`

### 6) Safer-alternative card

Show only the strongest honest alternative when the request is too strong, for example:

- `Export from witness seat, do not replay yet`
- `Switch to desktop host for live recovery`
- `Join History before making actor claims`
- `Wait for daemon/watch freshness`
- `Recover side-by-side for comparison first`
- `Cancel because no safe replay locus exists`

## Non-negotiable rules

### Rule 1 — host choice must precede replay

The operator may not commit a distributed restore before the product states which host is actually performing it.

### Rule 2 — runtime liveness must remain first-class

If replay depends on the engine actively running and observing the change now, that is a precondition, not a buried support note.

### Rule 3 — export and replay are different product verbs

A witness-host action that merely copies bytes out must not inherit the language of share-wide recovery.

## Honest outputs

The page may conclude:

- `This host can export and inspect the candidate, but live replay should run from a desktop witness seat with active watch state.`
- `Recovery from the selected witness host is safe now because the engine is running and the requested action is side-by-side local restore only.`
- `The chosen host has the bytes but not the surface needed for live replay; switch hosts or downgrade the request to export.`
