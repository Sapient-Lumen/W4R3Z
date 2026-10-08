# Feature-entitlement proof page — why is this capability allowed here now?

## Proof goal

This page proves the strongest truthful entitlement sentence the product can currently make.

The proof target is one of:

- `this capability is legitimately entitled here now`
- `this capability is active here now, but only through a revocable topology`
- `this capability is active here now, but legitimacy for this lane is not proven`
- `this capability is not currently entitled here`
- `entitlement remains unknown`

## Proof ladder

### Rung 1 — activation witness

Evidence that a key, site-issued license, or trial is presently applied.
This is weak and never enough.

### Rung 2 — source witness

Evidence that identifies the entitlement source.
Examples:

- site-issued v3 non-commercial activation
- legacy Home Pro key
- legacy Family Pro key
- Business owner identity
- shared business seat

Still weaker than legitimacy.

### Rung 3 — topology witness

Evidence that shows how the current node inherits or holds the entitlement.
Examples:

- owner identity matches this node
- linked device under owner
- seat explicitly shared to this participant
- family member within scope

Still weaker than lane legitimacy and feature-afterlife.

### Rung 4 — lane/scope witness

Evidence that the current usage lane and platform/support posture match what the entitlement permits.
This is what stops `active now` from impersonating `legitimate for this use`.

### Rung 5 — feature-afterlife witness

Evidence that the specific feature still survives the current entitlement topology and has no stronger hidden cliff.
Only here may the product say:

> `legitimately entitled now`

## Mandatory proof fields

- subject capability
- entitlement source
- grant topology
- usage lane verdict
- feature-afterlife class
- best completed witness
- missing stronger proof

## Strong-sentence rules

### Allowed stronger sentences

- `legitimately entitled now`
- `active now through revocable seat`
- `active now but wrong support posture blocks stronger sentence`
- `trial active; durable entitlement not proven`
- `license applied but feature-afterlife cliff remains`

### Forbidden stronger sentences without proof

Do not say:

- `licensed for this use` without a lane witness
- `durable access` when owner or seat topology can still revoke it
- `server-capable` when the support qualifier is missing
- `this feature will survive expiry` without feature-specific afterlife proof

## Receipt excerpt

Every proof page must emit a condensed receipt block with:

- proof rung reached
- entitlement source
- topology class
- usage-lane verdict
- blocked stronger sentence
