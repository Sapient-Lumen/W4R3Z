# Decrypt recovery page: saved key, database continuity, and CLI witness interface spec

## Purpose

This page answers:

> if the plaintext-capable source fails, what exact recovery rung is still real from this opaque node, and what prerequisites are present or missing right now?

The page exists because recovery from ciphertext custody is not binary.
It depends on saved material, continuity, and the chosen recovery lane.

## Core rule

Every encrypted-custody subject must expose one first-class **Decrypt recovery** page.
That page owns:

- current recovery rung
- saved-material inventory
- database continuity verdict
- allowed recovery lanes
- missing prerequisites
- receipt

## Primary layout

The page always renders the same regions:

1. recovery verdict
2. prerequisite inventory
3. recovery-lane ladder
4. lane-specific execution contract
5. receipt and residual risk

### 1) Recovery verdict

Show:

- verdict label: `live-peer-available`, `saved-materials-ready`, `cli-decrypt-ready`, `partial-prereqs`, `blocked`
- strongest one-line summary
- whether the current best path is remote rehydrate, offline decrypt, or wait
- safest next action

The operator must be able to answer: **what strongest real recovery path exists right now?**

### 2) Prerequisite inventory

Show:

- saved RW key presence
- saved RO key presence if relevant
- database continuity intact / broken / unknown
- encrypted node still attached to the same subject database or not
- encrypted folder path known
- output folder prepared for offline decrypt or not
- strongest missing prerequisite

The operator must be able to answer: **what exact materials do I have, and what continuity survived?**

### 3) Recovery-lane ladder

Render lanes in strength order, for example:

1. `Connect a decrypt-capable RW seat and fetch from the encrypted node`
2. `Use preserved RW key with intact database continuity for remote rehydrate`
3. `Perform reviewed offline/CLI decrypt with required secret, database path, encrypted folder path, and prepared output folder`
4. `Ciphertext exists but key or database continuity is missing`
5. `Blocked: no honest recovery lane proven`

The page must say which rung is currently true and why stronger rungs are not.

### 4) Lane-specific execution contract

For the selected lane, show:

- which secret class is required
- whether the existing encrypted-node database must stay untouched
- whether the action creates plaintext locally or on another seat
- which paths must be supplied exactly
- strongest irreversible or confusing side effect
- explicit non-effects

The operator must be able to answer: **what exactly must I preserve while recovering, and where will plaintext emerge?**

### 5) Receipt and residual risk

After review or execution, emit a receipt preserving:

- current recovery rung
- prerequisites proven present
- prerequisites still missing
- lane chosen or intentionally deferred
- residual risk note

## Honest outputs

This page may conclude:

- `RW secret preserved and node continuity intact · remote rehydrate is believable`
- `Only ciphertext remains · offline decrypt requires explicit CLI-style path proof`
- `Database continuity broken · do not imply ordinary recovery from this node`
- `Output folder not prepared · offline decrypt contract incomplete`

It may not flatten all of these into one generic `Recoverable` badge.

## Rules

### Rule 1 — saved secret is not enough by itself

Do not treat secret possession as equivalent to a complete recovery plan.
Database continuity and path-specific requirements are separate truths.

### Rule 2 — continuity loss must downgrade confidence immediately

If the encrypted folder was removed or the database continuity is broken, the page must narrow the recovery claim instead of keeping optimistic wording.

### Rule 3 — offline decrypt is still product truth

Even if the recovery lane is operationally dense, the product must still model it explicitly rather than pretending it is outside the product's responsibility.

### Rule 4 — plaintext emergence point must be explicit

The operator should know whether plaintext will appear on another trusted seat, locally on the opaque node, or nowhere yet.

## Non-clone reason

Current official Resilio docs still preserve a real recovery story from encrypted custody, but only through saved RW/RO keys, intact database continuity, or an explicit CLI decrypt command that needs secret and path inputs.
That is useful honesty.
What should not be cloned is the way those prerequisites still read like support caveats instead of one stable recovery-ladder page.
