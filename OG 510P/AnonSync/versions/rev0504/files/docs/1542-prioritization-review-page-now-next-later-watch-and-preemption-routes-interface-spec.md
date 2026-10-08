# Prioritization review page: now, next, later, watch, and preemption routes interface spec

## Purpose

The contract sheet defines the candidate set.
The operator still needs one review page that compares live lanes side by side and answers:

> which candidate really belongs in `now`, which candidates are safely held, and what exact factor would justify preempting the current winner?

## Review layout

1. **Candidate-comparison strip**
2. **Lane-threshold panel**
3. **Attention-budget panel**
4. **Preemption panel**
5. **Starvation-risk panel**
6. **Tie-break panel**
7. **Review verdict**

### 1) Candidate-comparison strip

Show one card per candidate with:

- current lane
- dispatch eligibility
- dominant urgency factor
- dominant blocker
- reversibility
- scope size
- evidence freshness posture
- starvation age

Hard rule:

Non-selected candidates may not be hidden once a winner is chosen.
The review must show why they lost.

### 2) Lane-threshold panel

For each lane, show:

- why the candidate qualifies for that lane
- what keeps it from a stronger lane
- what would promote it
- what would safely demote it

Supported `lane_failure_class` values:

- `lower-urgency-than-competing-work`
- `dependency-not-ready`
- `budget-exhausted`
- `waiting-for-observation`
- `heavy-burden-not-yet-justified`
- `evidence-too-stale`
- `scope-too-wide-for-now`

Hard rule:

`not selected for now` must name the failure class.
Silence is not explanation.

### 3) Attention-budget panel

Required rows:

- current active slots
- remaining safe slots
- heavy-investigation slots
- monitor slots
- what dispatching this candidate consumes
- what work that would crowd out

Hard rule:

If dispatch consumes the last safe slot, the panel must say which next-best item is displaced.

### 4) Preemption panel

Required rows:

- current winner
- possible preemptor
- evidence or event needed for preemption
- displaced work if preemption occurs
- safe handoff or stop requirement

Supported `preemption_posture` values:

- `no-preemption-basis`
- `preemption-possible`
- `preemption-armed`
- `preemption-fired`
- `preemption-blocked-by-safe-stop`

Hard rule:

Preemption may not be implied only by tone or urgency adjectives.
The displaced work and stop boundary must be explicit.

### 5) Starvation-risk panel

Required rows:

- longest-waiting non-now candidate
- starvation risk grade
- why still not promoted
- earliest forced-review time
- what stronger sentence is lost if it keeps aging

Supported `starvation_risk_grade` values:

- `low`
- `moderate`
- `high`
- `breach-imminent`
- `breached`

Hard rule:

Any candidate at `breach-imminent` or `breached` must appear in the review verdict even if it still loses dispatch.

### 6) Tie-break panel

Required rows:

- nearest competing pair
- shared strengths
- decisive difference
- why that difference matters more right now
- what fact would reverse the tie-break

Hard rule:

When two candidates are close, the decisive difference must be visible.
`Feels worse` is not enough.

### 7) Review verdict

Render:

- dispatched candidate
- why it beats the nearest alternative
- most important held candidate
- preemption trigger if the ordering flips
