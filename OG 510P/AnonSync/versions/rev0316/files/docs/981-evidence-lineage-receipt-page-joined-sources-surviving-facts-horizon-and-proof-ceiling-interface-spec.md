# Evidence lineage receipt page — joined sources, surviving facts, horizon, and proof ceiling

## Purpose

Preserve the exact evidence basis that justified a claim at one point in time.

## The receipt must answer

1. which evidence families were consulted
2. which families were joined
3. what each family proved
4. what each family did **not** prove
5. what horizons were in force
6. what strongest safe sentence was emitted
7. what stronger sentence was refused
8. what later invalidators will weaken this receipt

## Required sections

### 1. Receipt header

- receipt id
- subject / incident id
- issuance time
- operator or automation origin
- current class: `event-proof`, `partial-join`, `expiry-watch`, `actor-gap`, `exported-bundle`

### 2. Source family table

Columns:

- family
- source locator
- durability class
- retention horizon at issue time
- facts carried
- facts missing

### 3. Joined-proof summary

Show:

- strongest safe sentence
- blocked stronger sentence
- actor-attribution class
- chronology-authority class
- byte-witness class
- notification/transfer role if any

### 4. Surviving-facts-after-expiry forecast

Show what remains true if each expiring family disappears.

### 5. Invalidators

List conditions such as:

- history expiry reached
- byte witness removed
- source mismatch later discovered
- receipt superseded by stronger or weaker later evidence

### 6. Continuations

Link to:

- evidence retention contract sheet
- join review
- attribution gap page
- retention horizon watch
- external export bundle if created

## Rules

- Receipts may summarize, but may not erase blocked stronger sentences.
- A later stronger receipt must supersede by reference, not rewrite this one.
- A compact receipt card may exist, but the full receipt must preserve horizons and gaps verbatim.
