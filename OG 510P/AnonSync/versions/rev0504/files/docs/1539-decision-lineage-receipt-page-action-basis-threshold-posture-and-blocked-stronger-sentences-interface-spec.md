# Decision lineage receipt page: action basis, threshold posture, and blocked stronger sentences interface spec

## Purpose

Later operators need one receipt that answers:

> what was the decision, what threshold was actually cleared, what stronger move stayed blocked, and why did the archive treat that choice as honest at the time?

## Receipt layout

1. **Decision identity**
2. **Action basis**
3. **Threshold posture**
4. **Residual uncertainty**
5. **Blocked stronger sentence**
6. **Expiry and reopen basis**

### 1) Decision identity

Required fields:

- decision charter id
- parent synthesis id
- affected scope
- decision owner
- receipt issue time

### 2) Action basis

Required fields:

- allowed next verb
- exact scope
- decisive basis sources
- safeguards attached
- post-action witness required

### 3) Threshold posture

Required fields:

- highest cleared threshold
- nearest blocked threshold
- threshold failure class if blocked
- decision pressure posture

### 4) Residual uncertainty

Required fields:

- uncertainty budget class
- key open questions
- tolerated-vs-not-tolerated split

### 5) Blocked stronger sentence

Render exactly one line:

- **Strongest blocked stronger sentence and why**

### 6) Expiry and reopen basis

Required fields:

- expiry trigger
- automatic reopen triggers
- fallback if no new evidence arrives
- successor decision id if superseded

## Hard rule

A lineage receipt must preserve the weaker surviving truth even after the chosen action completes.
Completing the action does not retroactively prove the stronger blocked sentence.
