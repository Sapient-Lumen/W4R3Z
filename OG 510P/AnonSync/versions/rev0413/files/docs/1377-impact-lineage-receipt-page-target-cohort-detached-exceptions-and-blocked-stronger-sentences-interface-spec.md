# Impact-lineage receipt page — target cohort, detached exceptions, and blocked stronger sentences

## Purpose

This receipt gives one durable line-item answer to:

> what setting mutation was proposed or committed, what exact cohort it reached, what detached or parallel subjects stayed out of scope, whether the focused subject was inheriting or explicit, and what stronger blast-radius sentence the product refused to make?

## Receipt fields

### Mutation block

- canonical setting id
- operator intent
- mutation class
- current route / surface

### Cohort block

- included cohort
- excluded cohort
- detached exception count
- future-subject inheritance rule

### Inheritance block

- focused subject state: `inherits`, `explicit override`, `explicit none`, `matching by coincidence`, `unknown`
- proof rung reached for that verdict
- whether reattach is required

### World / activation block

- world identity
- activation rung
- whether current receipt is world-local only
- strongest missing witness

### Strong-sentence block

- strongest allowed impact sentence
- blocked stronger sentence
- exact reason blocked

## Copy rules

- Prefer `changes inheriting cohort only` over `applies to all`.
- Prefer `explicit none` over `default cleared` when the subject remains detached.
- Prefer `reattach required` over `already following default again` unless inheritance proof exists.
- Prefer `different world` over generic `not included` when service/config fork is the reason.

## Example final sentence pattern

> `This mutation changes <cohort>; <exceptions> remain outside scope, the focused subject is <inheritance verdict>, and stronger sentence <all / back to default / active everywhere> was blocked by <missing proof>.`