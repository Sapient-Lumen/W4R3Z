# Reverse-lane proof page — which side can publish, delete, restore, and re-share

## Purpose

This page answers one ordinary question with evidence rather than assumption:

> which side can actually send effects back the other way from here, and which reverse lanes are blocked even though bytes are present?

## When this page appears

Show this proof page whenever the operator asks to confirm:

- whether local edits can publish outward
- whether local deletes can affect the source
- whether local restore can republish to other peers
- whether local custody can be re-shared in plaintext or only in a narrower form
- whether local bytes are merely retained evidence rather than active authority

## Proof ladder

Rank evidence from strongest to weakest:

1. explicit lane contract from this subject type
2. live reviewed capability witness on this seat
3. reviewed delete-direction contract
4. reviewed recovery-lane prerequisite proof
5. historical anecdote or operator memory

The page must never let a weaker rung outrank a stronger one.

## Fixed page order

1. reverse-lane verdict  
2. capability table  
3. blocked reverse paths  
4. prerequisite ledger  
5. strongest safe sentence  
6. reopening conditions

### 1) Reverse-lane verdict

Show separate verdicts for:

- outbound edit publication
- outbound delete publication
- reverse restore publication
- onward re-share publication

Each verdict must be one of:

- `proven allowed`
- `allowed only with additional reviewed prerequisites`
- `blocked by lane`
- `unknown`

### 2) Capability table

Rows:

- publish changed bytes outward
- publish delete outward
- republish restored bytes outward
- serve unchanged bytes outward
- re-share plaintext outward
- re-share only transformed / encrypted form outward

Columns:

- `current verdict`
- `basis`
- `missing proof`
- `best next proof`

### 3) Blocked reverse paths

List each blocked path explicitly, for example:

- `local restore cannot republish because seat is inbound-only`
- `local Archive cannot reverse source delete because source-delete-following is active`
- `local custody can re-share only in encrypted form`

### 4) Prerequisite ledger

For any conditional reverse lane, show the exact prerequisites, such as:

- saved secret or credential
- continuity of the same database / lineage
- live writable counterpart online
- reviewed runtime witness

### 5) Strongest safe sentence

Show two sentences:

- strongest safe sentence
- stronger blocked sentence

Example:

- safe: `This seat can retain and serve bytes, but cannot republish restored bytes back into the live subject.`
- blocked: `This seat can fully recover the subject on its own.`

### 6) Reopening conditions

Show what must change for a stronger reverse-lane sentence to become honest.

## Copy rules

- Never let `has bytes` imply `can restore world`.
- Never let `can serve` imply `can publish edits`.
- Never let `can re-share` omit the form class of the re-share.
- Always separate `blocked by lane` from `unknown because proof is missing`.
