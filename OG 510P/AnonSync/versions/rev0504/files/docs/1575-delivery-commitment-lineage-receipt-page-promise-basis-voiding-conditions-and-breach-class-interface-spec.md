# Delivery commitment lineage receipt page: promise basis, voiding conditions, and breach class interface spec

## Purpose

This receipt is the durable artifact that later operators, reviewers, and downstream audiences use to understand exactly what was promised, why it was publishable, what could void it, and what survived after slip or breach.

## Required receipt blocks

### 1) Identity block

Show:

- commitment id
- linked forecast id
- linked deliverable id
- audience id
- owner id
- receipt generation time

### 2) Promise basis block

Show:

- commitment class
- published promise window
- forecast basis used
- finishability grade at publication
- confidence grade at publication
- strongest supporting fact

### 3) Voiding conditions block

Show:

- named invalidators
- named renegotiation triggers
- whether route change voids the promise
- whether restart-from-zero risk was absorbed or excluded
- whether hidden preprocessing was absorbed or excluded

### 4) Breach boundary block

Show:

- tolerated slip rule
- miss rule
- breach rule
- who may declare breach
- whether audience re-acceptance is needed after downgrade

### 5) Surviving sentence block

Show:

- strongest sentence if conditions held
- strongest sentence after widening only
- strongest sentence after miss
- strongest sentence after breach
- current surviving sentence now

### 6) Lineage block

Show:

- all promise-class changes
- all renegotiation events
- all breach events
- replacement commitment id if any
- receipt invalidators still open

## Hard rules

- The receipt must make `forecast`, `target`, `conditional commitment`, and `hard commitment` visibly non-interchangeable.
- The receipt must preserve earlier stronger promises even after later downgrade.
- The receipt may never say only `late` when `breach` was the actual published boundary.
- The receipt must preserve the weaker surviving sentence instead of pretending the old promise still governs.
