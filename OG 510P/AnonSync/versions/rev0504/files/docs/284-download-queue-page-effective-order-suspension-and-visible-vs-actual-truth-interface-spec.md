# Download queue page: effective order, suspension, and visible-vs-actual truth interface spec

## Purpose

`53`, `266`, and the transfer-lane work already treat throughput and queueing as public behavior.
This document makes `which file goes first, and why` one stable page.

The page exists to answer one ordinary operator question:

> what is the effective download order right now, why are some files ahead of others, and when visible order differs from actual execution which answer is authoritative?

## Core decision

Every subject with non-trivial inbound transfer ordering must render one first-class **Download queue** page.
That page is the semantic home of:

- effective priority policy and its source
- active queue and current execution order
- suspension / preemption reasons
- policy exceptions and hard limits
- receipts for priority mutation

The page must not let alphabetical browse order or generic transfer progress substitute for actual queue truth.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. queue verdict strip
2. effective-priority policy card
3. active execution lane
4. suspension and exception card
5. source-of-truth comparison card
6. action matrix
7. receipts and retired priority decisions

### 1) Queue verdict strip

The strip shows:

- subject or transfer scope
- one queue verdict
- one priority-source verdict
- one next-honest-action button

Allowed queue verdicts:

- `natural order active`
- `priority order active`
- `priority partially constrained`
- `queue rebuild in progress`
- `visible order differs from actual order`

Allowed priority-source verdicts:

- `no priority policy`
- `inherited default`
- `subject override`
- `temporary review override`

### 2) Effective-priority policy card

Show:

- priority basis (`none`, `mtime-desc`, `mtime-asc`, `size-desc`, `size-asc`, or future allowed basis)
- policy origin
- whether the subject still inherits future global changes
- active queue window limit
- whether current transfer class can fully obey priority policy

The page must make `inherited default` visibly different from `local override frozen in time`.

### 3) Active execution lane

Show ordered rows for active and near-active downloads with:

- path or artifact ref
- current execution rank
- visible browse rank if different
- reason for current rank
- splittable / non-splittable class
- bytes remaining
- whether it preempted or was preempted

### 4) Suspension and exception card

Show:

- files suspended due to higher priority arrival
- non-splittable transfers that continue despite later higher-priority rows
- queue rebuild triggers such as errors or changed file properties
- internal caps or limits that truncate strict prioritization

The page should answer `why didn't the obvious file go first?` directly.

### 5) Source-of-truth comparison card

If any visible list differs from execution order, show:

- authoritative execution order source
- surfaces currently showing non-authoritative order
- reason for the mismatch
- whether the mismatch is cosmetic only or decision-relevant

### 6) Action matrix

Render ordered actions such as:

- `Keep inherited priority`
- `Pin subject to explicit priority`
- `Return subject to natural order`
- `Temporarily expedite selected files`
- `Escalate to transfer review`

Each row shows:

- scope touched
- whether it changes execution immediately
- whether it breaks inheritance
- reversibility
- expected receipt

### 7) Receipts and retired priority decisions

Show recent queue-policy receipts with:

- actor
- old and new policy
- scope
- whether inheritance was broken or restored
- affected active rows count
- follow-up advice if queue rebuild is expected

## Narrow-width behavior

In narrow width the page may stack cards, but it may not hide:

- whether priority order is active
- the authoritative execution order
- visible-vs-actual mismatch truth
- exceptions preventing strict priority

## Acceptance criteria

This spec is satisfied when:

- operators can tell from one page what the effective queue order actually is
- inherited defaults and frozen local overrides are visibly different
- suspension and exception behavior is typed rather than folklore
- alphabetical or browse ordering cannot masquerade as authoritative execution order
- any priority mutation leaves a durable receipt naming whether inheritance changed
