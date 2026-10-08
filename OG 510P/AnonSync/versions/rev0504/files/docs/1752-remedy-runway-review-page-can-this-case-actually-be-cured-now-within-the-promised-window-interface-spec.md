# Remedy-runway review page — can this case actually be cured now within the promised window?

## Decision question

This page answers one operational question:

**Can the case actually execute a cure now, for the required cohort, inside the promised window, or are we still relying on optimistic preservation plus operator hope?**

## Review sections

### 1) Requested cure versus executable cure

The review must begin by comparing the requested cure objective with the executable cure lane actually available now.
It must show:

- what exact repair action is required
- which objects and sources that action depends on
- which parts are presently source-ready
- which parts remain placeholder-only or offline-dependent

### 2) Source readiness map

The page must separate:

- source known to exist
- source online now
- source expected but offline
- placeholder-only visibility
- ghost or no-source risk
- sources whose freshness or authority is stale

### 3) Capacity and contention map

The review must show whether the cure lane is materially executable, including:

- active priority class
- competing workload and preemption rights
- scheduler-open versus scheduler-closed windows
- upload and download headroom
- temporary write amplification needs
- internal-task congestion
- discovery lag caused by watcher limits or rescan fallback

### 4) Cohort coverage

The review must model which cohorts can actually be cured now.
It must separate:

- named pilot cohort
- connected cohort
- required cohort
- offline-but-required cohort
- cohorts needing manual preparation or manual approval before repair can start

### 5) Highest honest sentence

The page must always conclude with one highest honest sentence from this family:

- `cure requested only`
- `cure runnable with manual preparation`
- `cure runway partial`
- `cure runway ready for named cohort`
- `cure runway ready for required cohort`
- `cure runway blocked by source absence`
- `cure runway degraded by headroom or queue risk`
- `cure runway missed or expired`

It must also name the blocked stronger sentence and why it remains blocked.

## Review invariants

- the review never lets preserved bytes impersonate online source readiness
- the review never lets configured priority impersonate real response-window sufficiency
- the review never lets temporary calm impersonate runway stability if queue, rescan, or headroom risk remains
- the review always names the exact blocker that prevents the stronger cure sentence
