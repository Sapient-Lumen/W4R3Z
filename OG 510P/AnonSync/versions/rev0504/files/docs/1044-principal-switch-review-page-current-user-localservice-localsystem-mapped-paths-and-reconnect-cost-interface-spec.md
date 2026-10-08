# Principal switch review page — current user, LocalService, LocalSystem, mapped paths, and reconnect cost

## Purpose

Review the exact consequences of changing which principal owns the service runtime.

This page exists to answer:

- `what path classes become reachable or unreachable under the new principal?`
- `what mapped-drive or UNC caveats appear?`
- `does principal widening change storage-world continuity?`
- `what immediate reconnect or re-share cost follows if the old roster will not carry forward?`
- `what sentence about successful migration is blocked even if the new principal can now read the path?`

## Inputs

- source principal
- target principal
- known subject paths and path classes
- storage-root mapping for source and target
- notification-capability findings
- reconnect obligations if continuity is not preserved

## Layout

### A. Principal delta verdict strip

Fields:

- source principal
- target principal
- path reach delta
- storage-world delta
- reconnect cost verdict
- strongest safe sentence

Example verdicts:

- `Current user → current-user service: same principal class; storage continuity likely`
- `Current user → Local System: wider filesystem reach, different service storage world`
- `Current user → Local Service: review path access and continuity before apply`
- `Mapped-drive subject present: service cannot rely on drive-letter continuity`

### B. Path-class matrix

Rows must at minimum cover:

- local user-profile path
- mapped drive letter
- UNC / SMB path
- another user's folder
- removable or externally mounted path if present

Columns:

- source accessibility
- target accessibility
- notification grade
- rescan dependence
- safe next step

### C. Storage-world delta card

Must show:

- source storage root
- target service storage root
- whether roots are the same, migrated, different, or unknown
- whether roster carry-forward is expected
- whether empty state is benign, suspicious, or proof of a different world

### D. Reconnect cost card

For each affected subject, show:

- carry-forward class (`preserved`, `needs-reconnect`, `needs-reshare`, `blocked`, `unknown`)
- operator work estimate class (`none`, `light`, `moderate`, `heavy`)
- why that class applies

### E. Safer alternatives card

Must offer reviewed alternatives such as:

- `keep service under current user`
- `stay interactive; do not promote yet`
- `switch path from mapped drive to UNC and accept observation downgrade`
- `start clean service branch intentionally`

## Required interactions

- `Mark mapped-drive risk reviewed`
- `Accept observation downgrade`
- `Return to cutover contract sheet`
- `Continue to service world preview`

## Guardrails

- Never let wider path reach read as proven continuity.
- Never hide mapped-drive loss behind a generic permissions error.
- Never let UNC fallback hide notification downgrade.
- Never suppress reconnect cost just because the runtime starts successfully.

## Output

A principal-switch review that makes path reach, continuity loss, observation downgrade, and reconnect cost explicit before the operator commits to the new service owner.
