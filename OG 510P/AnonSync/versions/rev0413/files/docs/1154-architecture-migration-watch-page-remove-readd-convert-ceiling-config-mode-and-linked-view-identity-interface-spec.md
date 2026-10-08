# Architecture migration watch page: remove-readd convert ceiling, config-mode support, and linked-view identity interface spec

## Purpose

This page exists for the moment an operator tries to move a subject across architecture families or assumes an automation lane can author every family equally.
It answers one ordinary question:

> is this an in-place architecture change, a remove-and-readd subject replacement, a linked-lane exception branch, or a configuration-authoring ceiling that should stop us before we promise too much?

## When this page must appear

Trigger this page for:

- Standard → Advanced aspirations
- any claim that an existing subject can simply be upgraded in place
- creation of an encrypted branch from an existing readable subject
- attempts to author Advanced through config mode
- any plan that combines linked auto-arrival with later manual Standard-key exceptions

## Fixed page order

1. migration intent header
2. convert ceiling card
3. automation and config card
4. linked-view and peer-identity card
5. risk and ceiling card
6. receipt/export rail

### 1) Migration intent header

Show:

- current family / requested family
- migration verdict (`same-family tweak`, `remove-and-readd family swap`, `derivative branch`, `unsupported`, `unknown`)
- strongest safe sentence
- stronger rejected sentence

### 2) Convert ceiling card

Render rows for:

- in-place conversion support
- required teardown/re-add support
- app subject continuity
- byte survivor class
- re-share / permission debt after migration

### 3) Automation and config card

Show:

- whether config mode can author this family
- whether config output is trapped in the Standard family
- whether manual UI or manual connection is required for this branch
- whether encryption branch requires `Disconnected` plus later key entry

### 4) Linked-view and peer-identity card

Show the reviewed distinction between:

- Standard device-level peer list
- Advanced certificate-level user grouping
- linked owner-default arrival behavior
- manual exceptions that will appear separately rather than as native linked subjects

### 5) Risk and ceiling card

Possible warnings:

- `Standard cannot be converted in place to Advanced`
- `config mode supports Standard only`
- `RO linked outcome requires a manual Standard-key exception`
- `encrypted derivative cannot stand in for readable participation`
- `changing architecture can alter peer-identity visibility and delegation model, not just permissions`

### 6) Receipt/export rail

Offer:

- `Emit subject architecture lineage receipt`
- `Open governance-domain review`
- `Open authority and re-share review`

## Rules

### Rule 1 — migration must not be framed as preference editing when it is subject replacement

The page must publish teardown/re-add when that is the honest reality.

### Rule 2 — automation ceilings must stay explicit

`configurable` and `operationally possible with manual side-steps` are not the same claim.

### Rule 3 — identity visibility changes count as architecture consequences

Switching families can change whether peers are seen as bare devices or certificate-grouped users; that must not be hidden.
