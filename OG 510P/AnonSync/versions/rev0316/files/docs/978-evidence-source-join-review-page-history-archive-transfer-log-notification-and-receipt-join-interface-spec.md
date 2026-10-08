# Evidence-source join review page — history, archive, transfer log, notification, and receipt join

## Purpose

Answer one ordinary question before the operator overclaims:

> if I join these evidence surfaces, what stronger statement becomes honest, what still remains missing, and what mismatch or expiry risk am I accepting?

## When this page appears

Open this page whenever the operator tries to:

- attribute a mutation to a specific seat or actor
- promote byte recoverability into incident blame or chronology certainty
- use a notification or transfer-history surface as durable proof
- export an incident summary or recovery receipt

## Layout

The page always renders the same order:

1. incident strip
2. selected-source list
3. join result card
4. mismatch and expiry card
5. action ladder
6. evidence-join receipts

### 1) Incident strip

Show:

- subject or incident label
- current verdict: `join-strengthens-proof`, `join-still-partial`, `join-blocked`, `join-expiry-risk`
- one next honest action

### 2) Selected-source list

Each chosen source shows:

- family badge
- source timestamp
- retention horizon
- facts carried
- facts not carried
- confidence grade

### 3) Join result card

This card publishes:

- strongest newly honest sentence after the join
- still-blocked stronger sentence
- whether actor attribution is now complete, partial, or still absent
- whether chronology is authoritative or guarded
- whether byte recoverability is confirmed or inferred only

### 4) Mismatch and expiry card

This card publishes:

- timestamp-range mismatches across sources
- subject-identity mismatch or ambiguity
- actor-name mismatch or alias ambiguity
- sources already expired or near expiry
- whether the join is stable enough for export or only for local review

### 5) Action ladder

Show actions such as:

- `Export bounded incident summary`
- `Create durable receipt now`
- `Keep as local partial explanation only`
- `Escalate before history expiry`
- `Do not join; evidence families are mismatched`

### 6) Evidence-join receipts

Receipts preserve:

- families joined
- resulting strongest safe sentence
- blocked stronger sentence
- expiry horizons in force at join time
- later invalidators

## Rules

### Rule 1 — joins must raise or lower proof explicitly

A join is not cosmetic. The page must say whether it actually strengthened the claim.

### Rule 2 — missing actor proof stays visible

Byte witness plus transfer occurrence still may not name the actor. The page must say so.

### Rule 3 — near-expiry evidence must be called out before export

If the strongest safe sentence depends on evidence about to disappear, the page must warn before completion.
