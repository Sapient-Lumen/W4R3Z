# Remedy-watch-health review page — is this post-discharge guard still credible right now?

## Purpose

This page is the operator's adjudication surface for whether a discharged case's relapse guard is still credible enough to justify stronger ordinary-life sentences.
It exists so the operator can answer one typed question instead of reconstructing credibility from quiet surfaces, warnings, and ad hoc logs.

## Primary review question

`Is this discharged case's relapse guard still credible right now, for the required cohort, inside the allowed freshness and response-budget envelope?`

## Required review panes

### 1. Coverage pane

Show:

- required guarded cohort
- actually probed cohort
- actually drilled cohort
- named lanes still unproven
- platform blind spots still live
- runtime blind spots still live

### 2. Freshness pane

Show:

- last successful canary probe
- probe age versus allowed ceiling
- last successful end-to-end drill
- drill age versus allowed ceiling
- next forced reprobe time
- next forced redrill time

### 3. Response-budget pane

Show:

- configured maximum response budget
- last measured response budget
- worst recent response budget
- budget verdict for named cohort
- budget verdict for required cohort

### 4. Evidence-strength pane

Show:

- notification basis strength
- history basis strength
- logging basis strength
- stale-surface risk
- watch-health verdict ceiling

## Required review outcomes

The page must support outcomes such as:

- `guard configured but unproven`
- `named-cohort probe current, required-cohort proof blocked`
- `probe current but drill stale`
- `probe and drill current but response budget exceeded`
- `guard credible for required cohort`
- `guard credible only with declared blind spots`
- `guard not credible enough for continued ordinary-life sentence`

## Review discipline

The review must forbid these shortcuts:

- quiet bell equals healthy guard
- no visible warning equals recent successful probe
- debug logging available equals credibility proven
- one platform pass equals required-cohort pass
- eventual re-fence equals inside-budget re-fence
