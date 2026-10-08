# Capability substitution page — requested outcome, missing control, and least-strong alternative interface spec

## Purpose

This page answers one ordinary question:

> the exact control I wanted is unavailable here, so what substitute preserves my intent best, what gets worse, and what stronger mistakes should I avoid?

The page exists because substitution is a product decision, not a user guess.

## Core decision

Whenever the requested action is unavailable but one or more substitutes exist, the product must open one first-class **Capability substitution** page.

The page is outcome-shaped.
It explains how closely each substitute matches the original intent.

## Fixed page order

1. original intent and missing control
2. substitute candidates
3. intent-match matrix
4. harm delta and blocked shortcuts
5. commit review
6. substitution receipt

### 1) Original intent and missing control

Show:

- original requested outcome in user language
- exact missing control
- current basis for absence
- whether the missing control exists elsewhere

The operator should be able to answer: **what did I ask for, and what exact thing is missing?**

### 2) Substitute candidates

List candidates such as:

- nearest same-scope substitute
- nearest stronger substitute
- defer / change-posture / change-surface route
- no-op / wait route if safer than substitution

### 3) Intent-match matrix

For each substitute, show:

- scope match
- byte-retention match
- reversibility match
- authority match
- complexity cost
- strongest new harm introduced

Use a small vocabulary such as:

- `near-match`
- `broader-than-requested`
- `narrower-than-requested`
- `different-kind`
- `unsafe-without-extra-review`

### 4) Harm delta and blocked shortcuts

This section must publish:

- what gets worse relative to the requested control
- what proof is lost or preserved
- what later recovery work becomes harder
- which tempting stronger shortcut is explicitly blocked or discouraged

### 5) Commit review

This section publishes:

- substitute chosen
- exact sentence earned afterward
- stronger sentence still unsupported
- return path to the original requested control if the basis for absence changes

### 6) Substitution receipt

The receipt preserves:

- original requested outcome
- missing control and its basis
- substitute options shown
- substitute selected
- harm delta acknowledged
- post-action claim ceiling

## Main surface

A compact **Capability substitution** card should show:

- requested action chip
- missing-control chip
- best substitute chip
- harm-delta chip
- primary action: `Review substitute`

## Acceptance criteria

A user can:

- see that substitution is happening at all
- compare substitutes against the original intent
- identify the least-strong workable substitute
- understand what gets worse if they proceed
- prove later that a substitute, not the original control, was committed
