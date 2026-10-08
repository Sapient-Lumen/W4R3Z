# Hypothesis adjudication review page: supported, refuted, unresolved, and competing causes interface spec

## Purpose

The incident case sheet names the case and holds the ledger.
This page exists for the harder question:

> given the evidence we now have, which causes are actually supported, which are ruled out, which are only partial explanations, and which still compete honestly?

## Core decision

AnonSync must expose one first-class **Hypothesis adjudication review** whenever a case has more than one active hypothesis, any contradictory evidence, any remediation outcome that changes cause confidence, or any closure proposal stronger than `unknown but stable`.

## Fixed page order

1. **Adjudication header**
2. **Competing causes matrix**
3. **Evidence-to-hypothesis map**
4. **Promotion / refutation decision panel**
5. **Unknowns and next discriminators**
6. **Blocked stronger sentence**

### 1) Adjudication header

Show:

- linked case id
- review owner
- review timestamp
- current favored cause
- current closure ceiling
- number of unresolved branches
- whether contradictory evidence still exists

### 2) Competing causes matrix

Each row is one hypothesis.
Required columns:

- hypothesis label
- cause family
- status before review
- status after review
- confidence movement
- exclusivity class
- reason summary

Supported `status after review` values must include:

- `primary-working-cause`
- `supported-secondary-factor`
- `necessary-precondition-not-root`
- `insufficient-alone`
- `refuted`
- `still-open`
- `superseded-by-combined-cause`

Supported `exclusivity_class` values:

- `exclusive`
- `compatible-with-another`
- `part-of-combined-cause`
- `mutually-blocking`
- `unknown`

Hard rule:

The page must let the operator conclude `more than one thing mattered`.
It may not force every case into one winner-take-all cause.

### 3) Evidence-to-hypothesis map

This map is the heart of the page.
Every evidence item must be tagged as one of:

- `supports`
- `weakly-supports`
- `neutral`
- `weakly-refutes`
- `refutes`
- `complicates`

Additional required fields:

- freshness verdict
- local-vs-global scope
- before-vs-after-remediation timing
- whether the evidence could be artifact residue rather than live truth

### 4) Promotion / refutation decision panel

This panel records each strong move in the reasoning.
Each decision row must show:

- decision id
- hypothesis affected
- movement type
- exact evidence basis
- stronger sentence unlocked
- stronger sentence still blocked
- reviewer signature

Supported `movement_type` values:

- `promote`
- `demote`
- `refute`
- `split`
- `merge`
- `park`
- `reopen`

Hard rule:

`Worked after the fix` cannot by itself promote a cause past `supported-not-exclusive` unless the product also shows why other plausible causes lost.

### 5) Unknowns and next discriminators

The page must always preserve an explicit lane for what is still unknown.
Required fields:

- unknown question
- why it matters
- what evidence would discriminate it
- whether the discriminator is safe, destructive, or external
- due time / next review

Supported discriminator classes:

- `observe-longer`
- `collect-more-artifacts`
- `compare-another-peer`
- `repeat-run`
- `environment-check`
- `support-feedback`
- `unsafe-now`

### 6) Blocked stronger sentence

This section must always contain at least one stronger sentence that remains unearned.
Examples:

- `identity corruption is the best current explanation` is weaker than `identity corruption is the only cause present`
- `watcher exhaustion explains delayed detection` is weaker than `all future delayed-detection risk is removed`
- `ghost-file behavior explains the missing bytes` is weaker than `no similar topology race remains`

## Mandatory interaction rules

- Contradictory evidence must remain visible after the review.
- A closure proposal must link to the exact adjudication decisions that support it.
- The page must preserve whether a favored cause is root cause, contributing factor, or necessary precondition.
- Reopen must send the hypothesis back into the matrix rather than creating invisible history.

## Why this page exists

A troubleshooting article can list possibilities.
A sync product needs to show which possibilities survived contact with actual evidence.
