# Write-authority proof page — who can actually mutate bytes here now?

## Proof goal

This page proves the strongest truthful local-write sentence the product can currently make.

The proof target is one of:

- `this runtime can mutate bytes here now`
- `this runtime can mutate bytes here now, but only through a constrained lane`
- `this runtime cannot mutate bytes here now`
- `mutability remains unknown`

## Proof ladder

### Rung 1 — path witness

Evidence that the subject path exists or is selectable.
This is weak and never enough.

### Rung 2 — grant witness

Evidence that the active principal or provider grant allows writes to the subject.
Examples:

- OS/storage permission granted
- provider-root grant granted
- NAS internal user has RW rights
- service principal has folder access

Still weaker than live writeability.

### Rung 3 — no-current-lock witness

Evidence that the requested subject is not currently blocked by another app or lock model.
Still weaker than safe lane.

### Rung 4 — host-lane safety witness

Evidence that the write lane is not one the product already knows is unsafe for concurrent authority.
This is what stops `technically writable` from impersonating `operationally safe`.

### Rung 5 — live mutation witness

Evidence that the runtime actually completed or can complete the requested mutation now on the subject, in the current world, through the current lane.
Only here may the product say:

> `writeable now`

## Mandatory proof fields

- active actor / principal
- write grant class
- current barrier class
- lane safety class
- best completed witness
- missing stronger proof

## Strong-sentence rules

### Allowed stronger sentences

- `writeable now`
- `writeable now through provider lane`
- `writeable after lock clears`
- `writeable only after principal/world switch`
- `path exists but write authority is not proven`
- `unsafe mixed lane blocks stronger health sentence`

### Forbidden stronger sentences without proof

Do not say:

- `folder is healthy` if the host lane is known unsafe
- `grant is enough` without a lane and lock witness
- `service runtime can continue previous subject` without continuity proof
- `SD path is writable` without provider-grant proof

## Receipt excerpt

Every proof page must emit a condensed receipt block with:

- proof rung reached
- blocker class
- lane class
- actor / principal
- blocked stronger sentence
