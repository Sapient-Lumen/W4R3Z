# rev0042 audit/refactor notes

## Audit tightening

`tools/current_scientific_run_audit.py` now checks four source-level defects:

1. GVR oracle truth-membership leakage.
2. Gate compiler duplicate validation branch.
3. Bridge annealing being auxiliary-only.
4. Block-index direct target-score privilege.

`tools/evidence_integrity_audit.py` uses the same source checks and requires current revision artifacts to carry run provenance.

## Refactor scope

The refactor was deliberately narrow:

- No broad registry work.
- No mass historical renaming.
- No current-named carry-forward smoke outputs.
- Only the repaired or rerun lanes emit `REV0042_*` artifacts.

## Storage posture

The historical cube still contains substantial duplicate/carry-forward mass. rev0042 does not solve that by spending the turn on storage bureaucracy. The next storage move should be a thin content-addressed layout for fresh artifacts only.

## Scientific posture

rev0042 should be read as: better falsifier integrity, stronger current provenance, and cleaner blockers. It is not a model or systems promotion.
