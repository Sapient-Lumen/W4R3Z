# Dispatch proof page: selected work, held work, and starvation guard interface spec

## Purpose

After review, the operator still needs one proof page that says:

> what exactly are we dispatching now, why is that the strongest honest ordering, what losing work remains live, and how will we know if that held work has been neglected too long?

## Proof sections

1. **Proof headline**
2. **Selected-work block**
3. **Priority-basis block**
4. **Held-work block**
5. **Starvation-guard block**
6. **Preemption-and-reopen block**

### 1) Proof headline

Show:

- selected candidate
- lane granted
- dispatch grade
- attention budget consumed
- highest-risk losing candidate

Supported `dispatch_grade` values:

- `dispatch-now-grade`
- `dispatch-next-grade`
- `watch-grade`
- `hold-grade`
- `frozen-grade`

### 2) Selected-work block

Required rows:

- selected candidate id
- exact work authorized now
- why now rather than later
- safe concurrency bound
- witnesses required after dispatch
- maximum claim this dispatch does not authorize

Hard rule:

A dispatch proof must say what the selection does **not** imply about the candidates that lost.

### 3) Priority-basis block

Required rows:

- decisive priority factors
- nearest competing candidate
- decisive tie-break
- budget effect
- whether the choice is robust-to-delay or fragile-to-delay

### 4) Held-work block

Required rows:

- held candidate ids
- current lane for each
- why each lost now
- what would promote each
- what evidence or time event would weaken the current ordering

Hard rule:

Held work cannot be summarized only as `remaining backlog`.
At least the most consequential held item must be described concretely.

### 5) Starvation-guard block

Required rows:

- item with the highest starvation risk
- current age in lane
- allowed remaining age
- forced-review trigger
- what sentence is no longer safe if the breach occurs

Hard rule:

A starvation guard must expire or trigger on an explicit basis; silent indefinite watch is not allowed.

### 6) Preemption-and-reopen block

Required rows:

- current preemption posture
- candidate most likely to preempt
- event or evidence needed to fire preemption
- safe stop or handoff boundary
- next portfolio owner on reopen

Hard rule:

Every dispatch proof must preserve how the ordering can change later without pretending today's winner was eternal truth.
