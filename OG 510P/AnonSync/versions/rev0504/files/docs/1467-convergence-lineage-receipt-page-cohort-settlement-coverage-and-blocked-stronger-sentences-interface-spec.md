# Convergence lineage receipt page: cohort settlement, coverage, and blocked stronger sentences interface spec

## Purpose

After a settlement wave ends, the next operator still needs one durable receipt that says what really got settled, what scope the stronger sentence now covers, and which stragglers still keep the broader claim blocked.

## Receipt contract

This receipt is the handoff object for campaign truth.
It is not a worklog.
It is a statement of settled scope, residual debt, and remaining honesty limits.

## Fixed page order

1. **Receipt header**
2. **Covered-scope card**
3. **Settlement-class card**
4. **Residual-straggler card**
5. **Claim-ceiling card**
6. **Handoff sentence**

### 1) Receipt header

Show:

- campaign id
- wave id
- receipt time
- owner at close
- settlement outcome
- coverage summary

### 2) Covered-scope card

Required rows:

- included subjects
- settled subjects
- excluded subjects
- reopened subjects
- proof freshness horizon
- next mandatory rereview

### 3) Settlement-class card

Required rows:

- final settlement class
- exact restore count
- successor promotion count
- temporary debt carried forward count
- bounded subset description

### 4) Residual-straggler card

Required rows:

- straggler ids
- why each remains outside the stronger sentence
- owner
- expiry
- next action

### 5) Claim-ceiling card

Required rows:

- strongest safe sentence now
- exact scope of that sentence
- next blocked stronger sentence
- what would unlock it
- automatic downgrade trigger

Hard rule:

The receipt must state the broader blocked sentence even when the bounded scope outcome is good.

### 6) Handoff sentence

Format:

> `This receipt proves [final settlement class] for [exact scope of that sentence]. It remains unsafe to say [next blocked stronger sentence] because [straggler ids / missing proof] remain outside the settled scope.`

## Explicit anti-goals

Do not:

- turn a bounded win into a universal claim
- omit reopened or carried-forward subjects
- hide temporary debt behind a generic closed status
- issue a receipt with no rereview horizon when stragglers still exist

## Why this page exists

Because the archive should never again need a detective to determine whether a cleanup campaign really settled the cohort or merely improved the average.
