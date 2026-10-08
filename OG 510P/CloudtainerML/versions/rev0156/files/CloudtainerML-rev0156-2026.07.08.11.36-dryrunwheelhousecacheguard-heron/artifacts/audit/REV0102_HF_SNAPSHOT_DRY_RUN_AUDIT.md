# HF snapshot dry-run audit — REV0102

Status: `skipped`  
Promotion allowed: `false`

Dry run attempted: `false`  
Known planned size GB: `0.0`

## Blockers

- none

## Warnings

- none

## Interpretation

This is a bandwidth/time safety valve. If `ALLOW_DOWNLOAD=1` is set, the gate should prove repo/revision reachability with `dry_run=True` before attempting to materialize the full snapshot.
