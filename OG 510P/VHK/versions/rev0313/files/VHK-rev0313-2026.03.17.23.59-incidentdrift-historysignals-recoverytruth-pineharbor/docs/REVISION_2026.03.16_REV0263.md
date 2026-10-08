# Revision REV0263 — claim witnesses, host drift, and stricter proof discipline

## Summary

This revision extends VHK's recent host-truth / target-fit work into the claim
and audit surfaces. The repo can now say not only what it recommends claiming,
but whether the current machine is actually believable evidence for that claim.

## Implemented

- `gen-claim-pack` now attaches compact current-host review to recommended claim
  rows when live session/host checks are available
- `audit-target-claims` now carries that witness review into audit results and
  summary counts
- strong claims marked as locally `verified` now fail audit when the current
  host clearly drifts from the lane being claimed
- `gen-capability-audit-pack` now surfaces claim posture plus current-host fit
  counts and per-claim witness status
- claim YAML output stays stable and user-editable instead of persisting the
  ephemeral host-review payload

## Why this matters

Linux automation proof is lane-specific. A local run on the wrong desktop can be
valid engineering feedback while still being bad release evidence. VHK now makes
that distinction visible instead of letting maintainers over-trust whatever host
ran the latest docs refresh.

## Validation

- `python -m compileall -q src/vhk`
- focused tests for claim/audit behavior
- regression ring across claim, capability-audit, release-stage, rehearsal,
  dossier, native-install, release-deploy, and setup packs
