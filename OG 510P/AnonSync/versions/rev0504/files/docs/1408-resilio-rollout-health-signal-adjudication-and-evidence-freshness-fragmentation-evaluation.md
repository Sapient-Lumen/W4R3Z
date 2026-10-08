# Resilio rollout health, signal adjudication, and evidence-freshness fragmentation evaluation

## Why this pass exists

The archive already had stronger doctrine for:

- policy profiles
- typed waivers and exception debt
- policy supersession and retirement
- rollout rings, readiness gates, stop conditions, and rollback class

What it still lacked was one explicit answer to the next ordinary operator question:

> the rollout exists and rings are defined — but do we actually have enough trustworthy, fresh, and adjudicated evidence to widen promotion, or are we reading too much into one graph, one warning, one anecdote, or one support bundle?

Current official Resilio material is useful here, but it still spreads the answer across several evidence planes:

- `Performance overview`
- `My files don't sync`
- `Errors and warnings`
- `Some internal tasks are taking time to complete`
- `Collecting debug logs automatically`
- `Collecting debug logs manually`
- `Power user preferences`
- `Resilio Sync 3.0 change log`
- `Resilio Sync change log`

## Current official Resilio evidence that matters here

Current official docs still show all of the following:

- `Performance overview` still says the graphs are **real-time** views for **ongoing activity**, with windows of **1 minute, 10 minutes, or 1 hour**, and that the disk-load chart is not necessarily Sync-only load.
- The same performance doc still says network details show peer upload/download speed, round-trip time, and protocol, which is useful signal but still only one surface.
- `My files don't sync` still tells operators to inspect several different planes: peer connectivity, the Status column, Sync History, the per-share peer queue, and then a long list of possible causes.
- `Errors and warnings` still presents many separate KB articles rather than one joined health adjudication workspace.
- `Some internal tasks are taking time to complete` still says important work is hidden and not visible to the user, that the warning may be intermittent and self-recovering, and that support plus debug logs may be needed when it does not clear in a timely manner.
- `Collecting debug logs automatically` still says direct technical support is available only for Business customers; for Sync v3 direct support is not available, users are directed to the community forum and Help Center; debug logging must be enabled and then restarted before reproduction, and operators are told to let logs collect for at least 15 minutes after the issue reproduces.
- `Power user preferences` still exposes `send_statistics`, `log_size`, `log_ttl`, and `profiler_enabled`, with `profiler_enabled` still requiring restart to activate.
- `Resilio Sync 3.0 change log` still shows warning- and UI-signal evolution, including improved WebUI warning for license application failure and fixes for a previously non-clickable `Can't download file` error status.
- `Resilio Sync change log` still preserves older evidence that performance charts, statuses, and warnings were introduced incrementally and that accuracy of receiving performance statistics has needed improvement.

So current Resilio still clearly admits real health-evidence truths:

- a graph is useful but time-window-bounded
- a warning can be real while still being transient
- a status string can exist before it is reliable or clickable enough to diagnose well
- hidden background work can explain surface symptoms
- log-based evidence has setup cost, freshness cost, and restart cost
- support evidence, UI evidence, historical known-issue evidence, and operator narrative are different evidence classes
- not every symptom deserves immediate promotion freeze, and not every green graph justifies broadening a rollout

But those truths do not yet become one first-class operator-facing **rollout health / signal adjudication / promotion-confidence object**.

## What Resilio still gets right

### 1) It exposes multiple useful signal planes

Graphs, warnings, history, peer queues, and logs are all legitimate evidence.
That is better than pretending one health badge is enough.

### 2) It admits that some evidence is hidden, delayed, or transient

The `Some internal tasks...` article is especially valuable because it says the user is not seeing all background work and that a visible warning can still self-clear.
That is exactly the kind of nuance a serious product should preserve.

### 3) It admits that evidence collection itself has cost and prerequisites

Restart-required profiling and debug logging are important truths.
Evidence is not free.

### 4) It keeps improving warnings and stats rather than pretending they were always authoritative

The change logs are useful because they preserve that stats accuracy and warning usability have changed over time.
That makes confidence-bounded interpretation more honest.

## Where current Resilio still fragments the operator answer

### A) Health evidence exists, but not as one adjudicated object

An operator can gather health clues from:

- real-time charts
- peer tables
- status warnings
- sync history
- peer queues
- warning KB pages
- debug logs
- profiler traces
- changelog-known issues

But current docs do not yield one canonical object with:

- evidence window
- freshness grade
- signal classes
- adjudicated severity
- likely cause confidence
- promotion consequence
- blocked stronger sentence

### B) Signal provenance is mixed, but not normalized

Some evidence is live UI telemetry.
Some is historical KB guidance.
Some is support-artifact capture.
Some is changelog prior.
Some is operator testimony.

Current Resilio makes all of those available in pieces, but does not normalize them into one operator-facing provenance ladder.

### C) There is no first-class promotion-confidence review

Before widening a rollout, an operator may need to know all of these:

- are current warnings transient or structural?
- is the graph window wide enough to trust?
- is the signal Sync-caused or host-caused?
- did we actually collect fresh logs after reproduction?
- is this symptom already a known version issue?
- does the evidence justify hold, freeze, rollback, or proceed-with-guard?

Current Resilio docs answer those pieces across performance docs, troubleshooting pages, support articles, and changelog archaeology.

### D) Escalation artifacts are too easy to confuse with durable product truth

A debug log bundle, profiler file, or support note is useful, but it is not the same as a stable operator verdict.
Current docs teach how to collect artifacts, but not how to compile them into one durable promotion-health judgment.

### E) Sentence discipline is still too easy to overstate

Without one health object, `rollout looks fine` can accidentally hide that:

- only a 10-minute graph window was checked
- warnings are currently suppressed but logs were never recollected after restart
- the symptom is host-load-related rather than rollout-related
- there is only forum-era anecdotal evidence, not cohort evidence
- a known issue prior still blocks a stronger sentence

## Hard product decisions now locked for AnonSync

### 1) Every serious rollout gets a first-class health object

The product must preserve:

- rollout id
- evidence window
- freshness grade
- signal inventory
- adjudicated symptom classes
- likely-cause classes
- promotion consequence
- strongest safe sentence
- blocked stronger sentence

### 2) Signal classes are explicit and typed

Supported signal classes must include at least:

- `live-metric`
- `warning-or-status`
- `history-event`
- `queue-observation`
- `support-artifact`
- `known-issue-prior`
- `operator-note`
- `unknown`

### 3) Promotion confidence is graded, not implied

Supported promotion-confidence classes must include at least:

- `green-promotable`
- `guarded-promotable`
- `hold-pending-more-evidence`
- `freeze-now`
- `rollback-now`
- `unknown`

### 4) Evidence freshness must be published before promotion widens

A promotion-health review must say whether the evidence is:

- `live-current`
- `recent-enough`
- `stale-but-still-informative`
- `too-stale-for-promotion`
- `unknown`

### 5) Support artifacts cannot silently become durable product truth

Logs, profiler traces, and support narratives must be joined into an adjudication step before they can justify green, hold, freeze, or rollback.

### 6) Host-load and product-regression stories must stay separate until proved joined

The product must preserve the difference between:

- Sync-caused degradation
- host-caused degradation
- mixed causality
- unproven causality

### 7) Stronger rollout-health sentences must stay blocked explicitly

The product must be able to say:

- `rollout is healthy enough for canary expansion` while blocking `healthy enough for broad rollout`
- `no structural blocker observed in this window` while blocking `no meaningful regressions remain`
- `symptom recovered` while blocking `root cause resolved`
