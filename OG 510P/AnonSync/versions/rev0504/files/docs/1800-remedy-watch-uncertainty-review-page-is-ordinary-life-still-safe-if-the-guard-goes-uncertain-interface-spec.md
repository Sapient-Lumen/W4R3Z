# Remedy-watch-uncertainty review page — is ordinary life still safe if the guard goes uncertain?

## Purpose

This page is the operator's adjudication surface for whether a discharged case remains safe once the guard's evidence or signal path weakens.
It exists so the operator can answer one typed question instead of reconstructing uncertainty posture from quiet notifications, rescan fallbacks, and support workflows.

## Primary review question

`If this case's guard becomes uncertain, does the product still keep ordinary life honest within the allowed uncertainty budget and fail-safe policy?`

## Required review panes

### 1. Uncertainty-trigger pane

Show:

- freshness lapse triggers
- signal-path degradation triggers
- notification-loss triggers
- rescan-only detection triggers
- restart-required detection triggers
- currently tripped uncertainty triggers

### 2. Budget pane

Show:

- configured uncertainty budget
- current uncertainty age
- grace still remaining
- over-budget verdict for named cohort
- over-budget verdict for required cohort

### 3. Fail-safe pane

Show:

- automatic fail-safe policy
- automatic narrowing or re-fence scope
- execution status
- manual fail-safe obligations still open
- strongest fail-safe sentence ceiling

### 4. Residual ordinary-life pane

Show:

- ordinary-lane permissions still live
- admissions still live
- resharing surfaces still live
- required-cohort exposure after fail-safe
- final uncertainty verdict ceiling

## Required review outcomes

The page must support outcomes such as:

- `uncertainty absent; fail-safe armed`
- `named-lane uncertainty only; stronger ordinary-life sentence survives for required cohort`
- `required-cohort uncertainty inside grace budget`
- `required-cohort uncertainty over budget; auto-fail-safe pending`
- `auto-fail-safe executed; ordinary life narrowed but not fully revoked`
- `manual re-fence required before honest ordinary-life continuation`
- `uncertainty resolved by fresh proof`
- `ordinary-life claim no longer honest`

## Review discipline

The review must forbid these shortcuts:

- recent probe equals uncertainty handled forever
- quiet UI equals uncertainty absent
- rescan fallback equals same guard strength as live notification path
- fail-safe configured equals fail-safe executed
- narrowed permissions equals full re-fence
- one lane regained proof equals required-cohort uncertainty cleared
