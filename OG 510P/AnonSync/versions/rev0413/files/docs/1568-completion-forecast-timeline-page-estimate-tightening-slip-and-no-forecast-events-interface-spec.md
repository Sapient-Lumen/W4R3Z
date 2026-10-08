# Completion forecast timeline page: estimate tightening, slip, and no-forecast events interface spec

## Purpose

Forecast quality changes over time.
The timeline page must answer:

> when did remaining work first become measurable, when did finishability become believable, when did the ETA window tighten or widen, and when did the product decide that no honest forecast remained?

## Core timeline rule

AnonSync must treat forecast changes as first-class events, not as stray comments inside progress or rescue history.

## Fixed event order

1. **Remaining-work-shaped event**
2. **First-finishability event**
3. **First-ETA-window or no-ETA event**
4. **Estimate-tightening or estimate-widening event**
5. **Slip / checkpoint-miss / no-forecast event**
6. **Requalification or close event**

### 1) Remaining-work-shaped event

Record:

- when remaining work first became explicit
- which basis established it
- whether the basis was direct or inferred
- who accepted it

### 2) First-finishability event

Record:

- first finishability grade
- strongest basis for it
- blockers still open at that time

### 3) First-ETA-window or no-ETA event

Record one of:

- first broad ETA window
- first bounded ETA window
- first checkpoint-based ETA window
- first `no honest ETA` verdict

### 4) Estimate-tightening or estimate-widening event

Record whenever:

- remaining-work basis improved or weakened
- schedule gates changed
- representative speed changed materially
- hidden preparation was discovered
- interruption or restart risk widened the window

### 5) Slip / checkpoint-miss / no-forecast event

Record whenever:

- a published window was missed
- a checkpoint-critical date passed
- a live blocker invalidated the estimate
- the product downgraded to `no honest forecast`

### 6) Requalification or close event

Record whenever:

- fresh evidence restored forecast confidence
- a reroute produced a new estimate
- the work finished and the final forecast posture closed

Hard rule:

Forecast history may not rewrite missed windows out of existence.
A slipped or withdrawn estimate remains part of lineage.
