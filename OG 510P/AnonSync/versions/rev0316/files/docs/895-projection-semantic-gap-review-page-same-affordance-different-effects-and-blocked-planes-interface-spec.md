# Projection semantic gap review page: same affordance, different effects, and blocked planes interface spec

## Purpose

Some controls look equivalent across projections even when they are not.
This page exists for the higher-risk moment:

> the operator is about to reuse a familiar-looking control on a different projection, but the effect is not guaranteed to be the same.

## Core decision

Whenever the same-looking affordance has materially different plane effects across projections, AnonSync must open one first-class **Projection semantic gap review**.

The page owns:

- familiar affordance family
- current projection effect
- remembered comparison projection effect
- semantic gap class
- safest continuation or refusal

## Fixed page order

1. affordance family and current projection
2. comparison projection card
3. semantic gap table
4. safest continuation verdict
5. projection-aware receipt promise

### 1) Affordance family and current projection

Show:

- visible affordance family (`pencil rename`, `rename menu`, `share-label edit`, `other`)
- current projection
- current resolved verb family
- strongest safe sentence

### 2) Comparison projection card

This card is mandatory when the operator arrived here from memory, docs, or a prior receipt from another projection.
Show:

- comparison projection
- remembered or prior verb family there
- whether the current projection is stronger, narrower, or just different

### 3) Semantic gap table

Minimum columns:

- plane
- current projection effect
- comparison projection effect
- mismatch class (`none`, `narrower`, `broader`, `different-plane`, `unknown`)
- risk if operator assumes sameness

### 4) Safest continuation verdict

Possible outcomes:

- `safe to continue here`
- `safe only after explicit plane confirmation`
- `switch projection before apply`
- `stop; this projection cannot honor the intended verb honestly`

### 5) Projection-aware receipt promise

Before apply, state what the receipt will preserve:

- executing projection
- resolved verb family
- changed planes
- untouched planes
- rejected stronger reading

## Rules

### Rule 1 — familiar icons do not imply shared semantics

Visual reuse across projections is never enough evidence that the same plane will change.

### Rule 2 — the semantic gap must be named plainly

`Different here` is not enough; the page must say whether the current projection is narrower, broader, or aimed at a different plane.

### Rule 3 — switching projection is a first-class outcome

The correct answer may be `do this elsewhere` rather than forcing the act from the wrong surface.

## Acceptance criteria

A later operator can:

- tell why the familiar control could not be trusted blindly here
- tell how current and comparison projections differ
- tell whether the action was continued, rerouted, or blocked
- tell what stronger mistaken reading was rejected
