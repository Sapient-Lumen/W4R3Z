# Evidence access receipt page — visible now, hidden still there, and next best surface

## Purpose

Produce a durable post-review receipt that captures the difference between:

- evidence visible now
- evidence known to exist but still hidden
- evidence believed to exist only on another seat
- evidence unavailable on the current surface

## Receipt fields

### Identity
- receipt id
- subject / lineage
- current seat
- current surface
- timestamp

### Visibility summary
- visible-now witness classes
- hidden-but-openable-here classes
- route-required classes
- unavailable-here classes

### Strongest safe sentence
One narrow sentence the operator may reuse safely.

Examples:

- `Archive witness is inspectable from this desktop seat.`
- `Archive witness exists but this surface requires file-browser access to inspect it.`
- `Recovery witness is not inspectable on this iOS surface.`

### Forbidden overclaims
Examples:

- `recoverable here`
- `no witness exists`
- `fully gone`
- `safe to delete hidden state`

### Next-best surface
If needed, show:

- target seat or tool
- reason
- expected gain
- whether current proof survives if handoff is deferred

### Residual warnings
- hidden `.sync` is critical state
- authorship may still need History even when Archive is visible
- uninstall residue may outlive the app
- hidden is not equivalent to safe removal

## Entry points

This receipt must be reachable from:

- recovery pages
- cleanup pages
- uninstall pages
- severance / claim-ceiling pages
- diagnostics / export workflows

## Success condition

A future reader should be able to tell, without reopening several docs or re-running scans, what evidence was actually inspectable from the reviewed surface and what still required another route.
