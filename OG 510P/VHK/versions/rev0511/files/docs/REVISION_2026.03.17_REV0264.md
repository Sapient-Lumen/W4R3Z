# Revision REV0264 — promotion witnesses and wrong-host proof gates

## Summary

This revision extends VHK's claim-witness discipline into the promotion pack.
Promotion review can now see whether the current machine is believable evidence
for the stronger Linux lanes the repo wants to promote.

## Implemented

- `gen-promotion-pack` now accepts live host/session evidence and computes a
  compact current-host claim witness review
- promotion output now carries a `current-host-proof-gate` when that witness
  posture is visible
- promotion backlog/evidence gain explicit wrong-host-proof follow-up items
- promotion docs/fixups now show host proof drift instead of leaving it only in
  claim/audit output
- refresh script now includes `gen-claim-pack` so promotion review can refresh
  the same proof surfaces it depends on

## Why this matters

Linux promotion pressure often arrives before support claims are edited. If the
project already knows a workstation is poor proof for a stronger target lane,
promotion review should say so early instead of letting the wrong host become
release folklore.

## Validation

- `python -m compileall -q src/vhk`
- focused tests for promotion, claim, and capability-audit packs
- regression ring across route-selection and later-stage pack suites
