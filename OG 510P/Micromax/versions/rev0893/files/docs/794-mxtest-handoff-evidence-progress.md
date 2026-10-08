# Rev0835 — carried aggregate evidence and selected-test progress

Rev0835 closes a practical handoff gap in the aggregate evidence lane.

## Problem

The mxtest evidence path had become increasingly resume-safe, but the revision zip still excluded `.artifacts/` wholesale. That meant a partial `.artifacts/mxtest-all*.json` manifest could verify locally, yet disappear from the linked handoff archive. The next session had to start the aggregate run from scratch unless the same cloudtainer filesystem happened to survive.

The manifest summary also over-emphasized chunk counts. A chunk can be partial while still containing many passed file or node-id spans, so humans had to inspect nested JSON to know how many selected tests were already represented by passed evidence.

## Change

`tools/mkrevzip.py` now carries only stable aggregate evidence manifests:

- `.artifacts/mxtest-all.json`
- `.artifacts/mxtest-all-64.json`

Scratch plans, probes, caches, and revision-specific temporary manifests remain excluded. This keeps archives small while letting the recommended aggregate lane travel with the zip.

`tools/mxtest.py` now records and verifies selected-test progress:

- `test_status_counts`
- `passed_selected`
- `remaining_selected`

Manifest summaries and `--verify-current` now print a `test progress:` line so the next session can see useful progress immediately.

## Audit notes

A bounded rev0835 aggregate probe reached 160 selected tests with no failures before the `--max-new-tests` cap stopped the run. The probe also exposed the archive gap above: the manifest was useful, but would not have been shipped by the previous packaging policy.

## Validation

Focused validation covered the mxtest accounting path, mkrevzip artifact allowlist, context, and the current aggregate smoke. A full aggregate pass is still not claimed.
