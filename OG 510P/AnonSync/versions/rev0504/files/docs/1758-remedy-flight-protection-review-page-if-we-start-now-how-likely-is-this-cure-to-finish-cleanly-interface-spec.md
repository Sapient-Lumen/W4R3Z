# Remedy-flight-protection review page — if we start now, how likely is this cure to finish cleanly?

## Decision question

This page answers one operational question:

**If the case starts its cure now, is it protected strongly enough to finish cleanly for the required cohort inside the promised window, or are we still relying on luck, manual babysitting, or fragile runtime conditions?**

## Review sections

### 1) Startability versus finish protection

The review must begin by comparing the already-proven runway with the stronger finish-protection claim actually available now.
It must show:

- what cure work can start immediately
- what makes the start interruptible or protected
- what stronger finish sentence is still blocked
- whether manual babysitting is part of the honest story

### 2) Preemption and scheduler exposure

The page must separate:

- configured priority
- active queue position
- higher-priority arrival risk
- queue rebuild sensitivity
- scheduler-open window coverage
- pause exposure and intentional suspension rights

### 3) Runtime fragility map

The review must show whether forward progress is materially protected, including:

- hidden internal-task pressure
- watcher-loss or rediscovery lag
- source continuity through finish
- temporary-write continuity
- restart survivability
- `.sync` and service-metadata integrity

### 4) Cohort-specific finish exposure

The page must model which cohorts are likely to finish and which remain fragile.
It must separate:

- named pilot cohort
- currently connected cohort
- required cohort
- offline-but-required cohort
- cohorts depending on fragile or single-source lanes

### 5) Highest honest sentence

The page must always conclude with one highest honest sentence from this family:

- `cure start requested`
- `cure started but interruptible`
- `cure in-flight protected for named cohort`
- `cure in-flight protected for required cohort`
- `cure preempted or requeued`
- `cure stalled by hidden work or discovery lag`
- `cure aborted by source loss`
- `finish-protection collapsed`

It must also name the blocked stronger sentence and why it remains blocked.

## Review invariants

- the review never lets runway readiness impersonate finish protection
- the review never lets current byte motion impersonate bounded interruption risk
- the review never lets source-online-at-start impersonate source continuity through finish
- the review always names the exact blocker that prevents the stronger finish sentence
