# Integrated claim proof page: merged basis, open conflicts, and ceiling interface spec

## Purpose

The operator needs one proof page that turns a multi-packet reading into one durable answer:

> what exact integrated claim is justified, by what weighted basis, and how far does that claim stop because of unresolved conflict or missing independence?

## Core decision

AnonSync must expose one first-class **Integrated claim proof** whenever a synthesis set produces any nontrivial merged sentence that others may rely on.

## Fixed page order

1. **Proof header**
2. **Integrated-claim card**
3. **Weighted-basis card**
4. **Conflict-ceiling card**
5. **Alternative-interpretation card**
6. **Reliance-envelope card**
7. **Proof sentence**

### 1) Proof header

Show:

- proof id
- synthesis source id
- proof owner
- issuance time
- current proof posture
- current strongest safe integrated sentence
- strongest blocked sentence

Supported `proof_posture` values:

- `draft`
- `bounded-proof-issued`
- `reservation-heavy-proof-issued`
- `proof-recalled`
- `proof-superseded`
- `proof-expired`

### 2) Integrated-claim card

Required rows:

- exact integrated sentence
- target question answered
- scope answered
- worlds covered
- worlds excluded
- time window covered

Supported `integrated_claim_grade` values:

- `weak-pattern-only`
- `bounded-supported`
- `strongly-corroborated`
- `conflict-capped`
- `temporary-synthesis-only`

Hard rule:

A `strongly-corroborated` claim must include at least two active source clusters labeled `independent-corroboration`.

### 3) Weighted-basis card

Render the active basis in descending decisional weight.
Required fields per row:

- source id
- source role in proof
- source weight explanation
- freshness posture
- relation status to other top-weight sources

Supported `source_role_in_proof` values:

- `lead-basis`
- `corroborating-basis`
- `context-basis`
- `conflict-shadow`
- `discounted-reference`

Hard rule:

The page must explain why the top-weight source outranks any more numerous lower-weight cluster.

### 4) Conflict-ceiling card

Required rows:

- unresolved conflict ids
- what each conflict blocks
- fallback sentence that remains safe
- recall or downgrade trigger

Hard rule:

If the proof remains conflict-capped, the blocked stronger sentence must be displayed in the same visual block as the issued sentence.

### 5) Alternative-interpretation card

Show the strongest live alternatives that were not fully eliminated.
Required rows:

- alternative interpretation
- why still live
- what evidence weighs against it
- what evidence would kill it

Hard rule:

Alternative interpretations may not be omitted merely because one integrated claim is favored.

### 6) Reliance-envelope card

Required rows:

- who may rely on this proof
- what decisions it can support
- what decisions it cannot support
- freshness horizon
- supersession trigger

Hard rule:

A proof issued for one question may not silently authorize a broader policy or certification claim.

### 7) Proof sentence

Render exactly three lines:

- **Issued integrated claim**
- **Why this merged basis is enough for that sentence**
- **What stronger sentence is still blocked and by what unresolved conflict or missing independence**
