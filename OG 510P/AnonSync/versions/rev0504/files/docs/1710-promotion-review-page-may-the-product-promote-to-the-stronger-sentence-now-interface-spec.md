# Promotion review page — may the product promote to the stronger sentence now?

## Purpose

This page is the operator workspace for deciding whether a stronger sentence may actually go live.
It exists so the reviewer can test prerequisites, authority, automation rights, override posture, and demotion exposure in one place.

## Required review branches

### Branch 1 — not yet eligible

Use this branch when the lower sentence is real but the stronger sentence should not even enter review yet.
The page must show:

- which prerequisite class is still missing
- whether the blockage is proof, authority, time basis, warning, residue, or policy
- the smallest honest sentence that remains usable meanwhile
- the next event that would make review appropriate

### Branch 2 — manual-review ready

Use this branch when the stronger sentence is eligible for review but may not auto-promote.
The page must show:

- who may make the decision
- why automation is not allowed
- what exact evidence bundle the reviewer is relying on
- what stronger sentence remains blocked even if this promotion is granted

### Branch 3 — auto-promotion gate check

Use this branch when the rule allows automation in principle.
The page must show:

- whether the auto-promotion confidence floor is met
- whether any warnings, residue, or reopen powers still freeze automation
- the exact trigger that would arm automation
- the exact trigger that would immediately disarm it

### Branch 4 — override request

Use this branch when an otherwise-blocked stronger sentence is being requested anyway.
The page must show:

- who is requesting the override
- who may grant it
- which prerequisites remain unsatisfied
- why the override is claimed to be justified
- what debt, probation, expiry, or re-review schedule will survive the override
- which even-stronger acts remain blocked despite the override

### Branch 5 — post-promotion demotion review

Use this branch when a previously promoted stronger sentence may need to be downgraded.
The page must show:

- what sentence had been promoted
- whether it was manual, automatic, or override-based
- what demotion trigger occurred
- whether the earlier lower sentence remains intact
- whether automation is now frozen
- what proof is preserved for audit

### Branch 6 — re-arm after repair

Use this branch when a demoted or denied promotion is being reconsidered after new proof or cleanup.
The page must show:

- what changed since the last denial or demotion
- which missing prerequisites are now satisfied
- whether override residue still survives
- whether the sentence is merely review-ready again or truly auto-armable

## Review invariants

The page must always preserve these invariants:

- earlier lower-sentence truth remains visible when a stronger sentence is blocked
- promotion is typed per stronger sentence, not globally per case
- auto-promotion is never inferred from calm appearance alone
- override must leave a durable scar in the record rather than masquerading as ordinary promotion
- demotion preserves history rather than rewriting the past

## Required reviewer prompts

- what is the smallest honest sentence right now?
- what exact stronger sentence is being considered?
- who is allowed to decide it?
- is automation truly allowed, or only manual review?
- what still blocks the stronger sentence?
- what event would demote it after promotion?

## Forbidden shortcuts

This page must not let the reviewer conclude promotion from shortcuts such as:

- `it has been stable for a while`
- `the system looks quiet`
- `there are no visible warnings`
- `a notification was delivered`
- `similar cases usually promote automatically`

Those phrases may inform judgment.
They may not replace the gate.
