# Setting-context proof page — visible vs editable vs authoritative here

## Proof goal

This page proves the strongest truthful setting sentence the product can currently make.

The proof target is one of:

- `this setting is editable here now`
- `this setting is visible here, but edited elsewhere`
- `this route can author only a local/share override`
- `this route is not the winning authority`
- `setting context remains unknown`

## Proof ladder

### Rung 1 — discovery witness

Evidence that the query or alias matched a real canonical setting object.
This is weak and never enough.

### Rung 2 — route witness

Evidence that the product knows a concrete surface and path for the setting.
Still weaker than scope and authority.

### Rung 3 — scope witness

Evidence that the product knows what subject set the edit will govern:
global, share-local, device-local, startup-world, or service-world.

### Rung 4 — authority witness

Evidence that the product knows whether this route is the winner, an override, or only a witness.
Only here may the product safely say:

> `editable here with known scope`

### Rung 5 — activation witness

Evidence that the product knows what event makes the edit active.
Only here may the product safely say:

> `editable here now and activation path is known`

## Mandatory proof fields

- canonical setting id
- matched aliases
- current surface
- winning surface
- scope verdict
- best completed witness
- missing stronger proof

## Strong-sentence rules

### Allowed stronger sentences

- `editable here now`
- `visible here, edited elsewhere`
- `this route creates a share-local override`
- `startup config owns this value`
- `service route required`
- `current surface is witness-only`

### Forbidden stronger sentences without proof

Do not say:

- `change it in settings` without a route witness
- `global change` without a scope witness
- `this menu owns the value` without an authority witness
- `change is in effect` without an activation witness
- `same value everywhere` without sameness proof

## Receipt excerpt

Every proof page must emit a condensed receipt block with:

- proof rung reached
- canonical setting id
- winning surface
- scope verdict
- blocked stronger sentence
