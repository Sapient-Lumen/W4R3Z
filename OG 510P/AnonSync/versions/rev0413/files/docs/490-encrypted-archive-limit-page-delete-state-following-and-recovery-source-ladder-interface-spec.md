# Encrypted Archive limit page: delete-state following and recovery-source ladder interface spec

## Purpose

This page answers:

> what does encrypted Archive on this node really prove, why can it not replay a deleted file back into the live subject from here, and what higher recovery sources still remain?

The page exists because `Archive exists` is not the same truth as `Archive can restore the file from this node`.

## Core rule

Every encrypted-custody subject with retained history must expose one first-class **Encrypted Archive limit** page.
That page owns:

- what encrypted history exists
- replay ceiling from this node
- delete-state-following explanation
- higher recovery ladder
- receipt

## Primary layout

The page always renders the same regions:

1. archive verdict
2. why replay is blocked here
3. alternative recovery-source ladder
4. safe actions and non-actions
5. receipt and proof links

### 1) Archive verdict

Show:

- whether encrypted Archive evidence exists here
- whether candidate bytes are still locally present
- whether those bytes are plaintext-readable here: yes/no
- strongest honest one-line answer
- safest next action

The operator must be able to answer: **what does this Archive actually buy me from this node?**

### 2) Why replay is blocked here

Show the blocking reasons separately:

- read-only barrier
- delete-state-following because overwrite guardrail is forced
- no ordinary plaintext authority on this node
- strongest direct non-effect

The operator must be able to answer: **why exactly can't this node push the deleted file back into the live subject?**

### 3) Alternative recovery-source ladder

List higher recovery sources in honest priority order, for example:

1. `Restore from recycle bin or ordinary undo on the source seat`
2. `Restore from Archive on another connected read-write seat`
3. `Fetch still-present ciphertext through a decrypt-capable RW recovery lane`
4. `Inspect encrypted history only; live replay not yet proven`
5. `Blocked: no stronger source currently available`

The page must say which rung is currently available.

### 4) Safe actions and non-actions

Show actions such as:

- `Open Decrypt recovery`
- `Locate another RW history source`
- `Export encrypted evidence receipt`
- `Preserve this node untouched`

Also show explicit non-actions such as:

- `Do not imply Restore to live share from this node`
- `Do not imply plaintext inspection here`

### 5) Receipt and proof links

Emit a receipt preserving:

- encrypted Archive presence
- replay ceiling from this node
- alternative recovery rung chosen
- proof links to **Ciphertext custody** and **Decrypt recovery**

## Honest outputs

This page may conclude:

- `Encrypted Archive present · evidence exists, but this node cannot replay deletion back into the live subject`
- `History exists only as ciphertext witness here`
- `Use RW-peer Archive or another recovery source instead`
- `No stronger recovery source currently proven`

It may not flatten these into one generic `Restore available` outcome.

## Rules

### Rule 1 — history presence and replay authority are separate

Archive presence is valuable, but it is not equivalent to current replay authority.

### Rule 2 — the blocking reason must be operator-readable

If the node follows delete state and is read-only, the page should say so plainly rather than hide behind generic `cannot restore` wording.

### Rule 3 — alternative ladders must be explicit

If stronger recovery sources exist elsewhere, the page must name them in order instead of making the operator rediscover them from separate articles.

### Rule 4 — evidence can matter even when replay is blocked

The page should preserve the value of encrypted history as evidence or future input without pretending it is a live restore surface today.

## Non-clone reason

Current official Resilio docs are admirably blunt that encrypted Archive on the opaque node cannot restore a deleted file back into the live share because the node is read-only and follows the delete state.
That truth should be copied.
What should not be copied is the way the operator still has to learn it from article caveats instead of one stable page explaining the ceiling and the higher recovery ladder.
