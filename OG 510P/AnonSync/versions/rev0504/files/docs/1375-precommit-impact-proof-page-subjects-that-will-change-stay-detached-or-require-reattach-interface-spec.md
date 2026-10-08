# Pre-commit impact proof page — subjects that will change, stay detached, or require reattach

## Proof goal

This page proves the strongest truthful impact sentence the product can make **before** the operator commits the mutation.

The proof target is one of:

- `this will change exactly these subjects`
- `this changes only the focused subject`
- `this changes the default but detached subjects stay unchanged`
- `this edits only a future/startup/service world`
- `impact cohort remains partially unknown`

## Proof ladder

### Rung 1 — canonical-setting proof

The product knows which setting object is being changed.
This is necessary but weak.

### Rung 2 — route proof

The product knows the exact mutation route and surface.
Still weaker than impact.

### Rung 3 — cohort-membership proof

The product knows which subject classes the route governs:
focused share, inheriting shares, future shares, current device, service world, or startup world.
Only now may the product say `this is more than a local edit`.

### Rung 4 — exception proof

The product knows which subjects stay detached or remain parallel.
Only now may the product safely say:

> `this changes 24 subjects and leaves 3 detached subjects unchanged`

### Rung 5 — inheritance-state proof

The product knows whether `inherit`, `explicit none`, and `matching-by-coincidence` differ for the focused subject.
Only now may the product safely say:

> `this subject is reattached` or `this subject remains explicitly set to none`

### Rung 6 — activation proof

The product knows when the proved cohort will actually adopt the change.
Only now may the product safely say:

> `these exact subjects will change after restart / rescan / cutover`

## Mandatory proof fields

- canonical setting id
- mutation class
- current surface
- cohort proved included
- cohort proved excluded
- inherit-vs-explicit verdict
- highest completed rung
- missing stronger proof

## Strong-sentence rules

### Allowed stronger sentences

- `this changes only this share`
- `this changes all inheriting shares in the current world`
- `detached shares remain unchanged`
- `this subject is explicitly set to none`
- `reattach is required before later defaults can reach this subject`
- `this edits next-startup state only`

### Forbidden stronger sentences without proof

Do not say:

- `apply to all` without exception proof
- `back to default` without inheritance-state proof
- `same as global` without proving inheritance rather than coincidence
- `everyone will get this` without current-world proof
- `done` without activation proof

## Receipt excerpt

Every proof page must emit a condensed receipt block with:

- proof rung reached
- included cohort ceiling
- excluded cohort ceiling
- inherit-vs-explicit verdict
- blocked stronger sentence