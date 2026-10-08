# Decision portfolio lineage receipt page: priority basis, attention budget, and blocked work interface spec

## Purpose

Later operators need one receipt that answers:

> what portfolio choice was made, why did this item win dispatch, what work remained held, and what starvation or preemption risk stayed live at the time?

## Receipt layout

1. **Portfolio identity**
2. **Dispatch basis**
3. **Held-work posture**
4. **Attention budget**
5. **Starvation and preemption risk**
6. **Expiry and reevaluation basis**

### 1) Portfolio identity

Required fields:

- portfolio id
- portfolio scope
- dispatch owner
- receipt issue time
- selected candidate id

### 2) Dispatch basis

Required fields:

- selected lane
- decisive priority factors
- nearest losing candidate
- decisive tie-break
- exact work authorized now

### 3) Held-work posture

Required fields:

- held candidate ids
- highest-risk held candidate
- reason still held
- promotion trigger for that item

### 4) Attention budget

Required fields:

- budget class
- slots consumed
- slots remaining
- displaced work if any

### 5) Starvation and preemption risk

Required fields:

- highest starvation risk grade
- forced-review trigger
- preemption posture
- likely preemptor if known

### 6) Expiry and reevaluation basis

Required fields:

- next portfolio review time or trigger
- stale-basis trigger
- starvation-breach trigger
- successor portfolio id if superseded

## Hard rule

A lineage receipt must preserve the losing work explicitly.
Winning dispatch does not retroactively prove the losing candidates were unimportant.
