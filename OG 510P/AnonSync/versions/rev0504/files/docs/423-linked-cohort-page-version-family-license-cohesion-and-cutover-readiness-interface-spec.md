# Linked cohort page — version family, license cohesion, and cutover readiness interface spec

## Purpose

The archive already had constellation, approval, and seat-lineage guidance.
What it still lacked was one ordinary page for the simpler question:

> may these linked seats keep acting as one cohort right now, or is version/family skew already turning identity convenience into control-risk and configuration-risk?

Current official Resilio docs make this seam concrete.
They still warn against linking devices where v2 and v3 are mixed because applied-license conflicts can cost UI access and share configuration.
That is useful truth.
It should not remain tucked inside identity guidance.

## Core decision

AnonSync must expose one first-class **Linked cohort** page for every identity cohort or intentionally related seat family.

The page exists to answer five things in one place:

1. which seats belong to the cohort
2. whether the cohort is uniform enough for safe shared identity behavior
3. what skew class currently exists
4. which seats must move together before any risky boundary is crossed
5. whether the cohort is ready for the proposed cutover

## Fixed page order

1. **Cohort uniformity verdict**
2. **Seat membership and current lines**
3. **Skew consequences**
4. **Cutover readiness**
5. **Safe next actions**

### 1) Cohort uniformity verdict

Show:

- `linked_cohort_page_id`
- cohort scope
- current `cohort_verdict` (`uniform`, `uniform-with-exceptions`, `mixed-version`, `mixed-family`, `mixed-license-state`, `cutover-in-progress`, `unknown`)
- strongest honest summary
- last cohort scan time

The operator must be able to answer:

> is this cohort safe to treat as one identity domain right now?

### 2) Seat membership and current lines

Show one row per seat:

- seat label
- installed line / family
- release posture
- license / entitlement posture
- last seen
- cutover inclusion requirement

The page must distinguish `offline but same family` from `present and risky skew`.

### 3) Skew consequences

Show the strongest consequences currently in play:

- UI access risk
- share-configuration risk
- approval or linking risk
- support-boundary risk
- unknown-state risk if some seats are missing

This section must say what can still safely continue and what must stop until the cohort is uniform.

### 4) Cutover readiness

Show:

- proposed target line
- seats already compatible
- seats that must move first
- seats that must not move yet
- whether staged cutover is safe or deceptive

The page must answer:

> can I move one seat now, or must this cohort move together?

### 5) Safe next actions

Actions may include:

- `Review cohort skew`
- `Create cohort cutover plan`
- `Hold linking changes`
- `Open install target for seat`
- `Mark seat intentionally separate`

Each action must preview whether it reduces or widens cohort ambiguity.

## Public object

### Linked cohort page

Fields:

- `linked_cohort_page_id`
- `cohort_ref`
- `seat_rows[]`
- `cohort_verdict`
- `skew_findings[]`
- `cutover_readiness`
- `must_move_together_refs[]`
- `safe_next_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. cohort
2. uniformity verdict
3. strongest skew
4. cutover readiness
5. next safest action

Example:

```text
Family identity A     mixed-version     v2/v3 license-conflict risk     move-together required     Create cohort cutover plan
```

## Non-goals

This page does **not** replace per-seat install eligibility or package selection.
It proves only **whether related seats can honestly continue as one cohort across this boundary**.
