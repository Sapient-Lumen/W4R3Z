# Affected items page — file slice, cause cluster, and safe-next-step interface spec

## Purpose

Give one concrete page for the item-level question:

- which exact files/items are implicated right now
- what grouped cause slice they belong to
- what evidence is local versus inferred
- which safe next step applies to each group

This page exists so the product never collapses `N files affected` into a vague count without a durable, navigable slice.

## Inputs

- parent status/warning/queue token
- subject identifier
- affected item rows
- item-level evidence per row
- cause cluster labels
- current availability/location data if relevant
- safe next action per cluster
- stronger forbidden sentence per cluster
- navigation affordances (`open path`, `copy path`, `inspect peer`, `inspect history`, `other`)

## Primary questions this page must answer

1. Which concrete items are implicated now?
2. Are they all in one cause cluster or several?
3. What is locally proved per item?
4. Which actions are safe at item level?
5. What stronger root-cause sentence is still unsupported?

## Layout

### A. Slice summary strip

Fields:

- affected-item count
- cluster count
- dominant cluster
- whether the list is complete or partial
- safest next action

### B. Cluster cards

Each cluster should show:

- cluster label (`locked`, `no source`, `path issue`, `permission blocked`, `mixed`, `unknown`)
- item count
- local evidence summary
- strongest safe cluster sentence
- stronger forbidden sentence
- best next action

### C. Item table

Columns:

- item/path label
- current item verdict
- evidence freshness
- cluster
- safe action
- details

Optional secondary columns:

- source/target peer if relevant
- last attempt
- current availability

### D. Item detail pane

For one selected item, show:

- exact item identifier/path
- current proved issue
- current unknowns
- adjacent routes that can strengthen the answer
- safe action ladder

### E. Non-inference block

Three lines:

- **what this page proves**
- **what it does not prove**
- **what route would be needed for stronger attribution**

## Required interactions

- `Open item path`
- `Copy item identifier`
- `Open route evidence for this item`
- `Open history for this item`
- `Return to status drilldown`
- `Issue diagnostic route receipt`

## Guardrails

- Never show an affected-item count without a route to the concrete slice when the slice is known.
- Never claim exact root cause per item if only cluster-level evidence exists.
- Never mix complete and partial lists without labeling that boundary.
- Never route out to the filesystem and lose the selected item context.
- Never let one cluster's safe action masquerade as universal for every item.

## Output

A concrete, grouped, navigable affected-items slice that keeps item evidence and action safety adjacent.
