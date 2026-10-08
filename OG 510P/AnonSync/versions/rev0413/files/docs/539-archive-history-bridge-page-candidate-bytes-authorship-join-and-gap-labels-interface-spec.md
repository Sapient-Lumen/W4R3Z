# Archive / History bridge page: candidate bytes, authorship join, and gap labels interface spec

## Purpose

This page answers one ordinary operator question:

> I found recoverable bytes, but who changed the file, why does this candidate exist, and how much of that answer comes from archive evidence versus separate history evidence?

The page exists because recovery proof often has two halves:

- **byte witness** — a candidate prior version exists somewhere
- **event witness** — a separate history trail explains who changed what and when

Those halves should be joined deliberately, not blurred.

## Core decision

Every serious recovery system must own one first-class **Archive / History bridge** page.
That page owns:

- candidate byte identity
- archive-origin facts
- history-origin facts
- joined authorship / chronology claims
- explicit proof gaps and forbidden overstatements

The operator must not have to remember that archive bytes are real but actor attribution still lives elsewhere.

## Page layout

The page always renders the same regions in the same order:

1. joined-evidence strip
2. byte-witness card
3. event-witness card
4. join-confidence card
5. forbidden-claim card
6. next-action card
7. evidence receipts

### 1) Joined-evidence strip

Show:

- subject path
- selected candidate
- byte witness class
- event witness class
- join verdict (`joined`, `partial-join`, `bytes-only`, `history-only`, `contradicted`)
- strongest safe sentence

### 2) Byte-witness card

Show:

- where the candidate bytes were preserved
- capture reason if known (`remote-update`, `remote-delete`, `rename-continuity`, `manual-preserve`, `unknown`)
- preserved-at time
- whether the candidate is directly recoverable
- whether the witness source is opaque about actor identity

### 3) Event-witness card

Show:

- history entries that plausibly explain the candidate
- actor / seat identity when known
- chronology confidence
- retention or completeness limits on the history lane
- whether the event witness is same-path, inferred, or only adjacent

### 4) Join-confidence card

Show:

- whether the byte witness and event witness match exactly, plausibly, weakly, or not at all
- what facts are safe to say (`candidate exists`, `likely replaced by seat X`, `actor unknown`, `delete observed but prior bytes absent`)
- what proof remains missing

### 5) Forbidden-claim card

Show explicit sentences the product refuses to let the operator overstate, for example:

- `This archive candidate proves who changed the file.`
- `The mutating seat still has the previous version.`
- `This restore is the exact version user X created.`
- `This history row means the bytes are still recoverable.`

### 6) Next-action card

Show only the strongest honest next action:

- `Recover bytes without actor claim`
- `Use joined proof in receipt`
- `Inspect competing history rows`
- `Export evidence only`
- `Cancel actor statement; bytes and events do not join strongly enough`

## Non-negotiable rules

### Rule 1 — archive evidence and history evidence must remain typed

The product may join them, but it may not erase which facts came from which source.

### Rule 2 — byte recoverability does not imply actor attribution

Recovered bytes may be strong while authorship remains partial or unknown.

### Rule 3 — history events do not imply bytes still exist

An event witness with no current byte witness must stay evidence-only.

## Honest outputs

The page may conclude:

- `A recoverable candidate exists, but actor attribution is only partial; use recovery language, not blame language.`
- `History and archive line up strongly enough to say the prior version was displaced by seat B yesterday, and the bytes remain recoverable on seat C.`
- `The event trail is strong, but no prior bytes remain; inspection may continue, recovery may not.`
