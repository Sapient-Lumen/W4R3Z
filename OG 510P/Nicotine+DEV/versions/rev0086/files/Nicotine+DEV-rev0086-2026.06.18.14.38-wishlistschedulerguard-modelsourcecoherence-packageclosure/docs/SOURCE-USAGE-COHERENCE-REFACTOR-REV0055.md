# Source-usage coherence refactor — rev0055

rev0055 audits and refactors the latest handoff language around source usage.

## Refactor result

The cube now distinguishes four evidence classes:

```text
1. Uploaded archived source bundle
   - file: Nicotine-source(1).zip
   - used for source anchors, archived marker scans, and extracted-lane selected-stack reruns

2. Archived source anchors
   - rev0051 line/hash anchors
   - now explicitly rerun against the uploaded source zip in rev0055

3. Current web marker snapshot
   - rev0054 public raw-file marker triage
   - useful but not a substitute for tests or source bundle validation

4. Fresh current checkout
   - still required before filing against live upstream
   - must include commit/hash/date and current-source seven-gate rerun
```

## Corrected ambiguity

Previous latest summaries emphasized that a current checkout could not be completed in the container. That remains true for live-current filing, but it should not obscure that the uploaded source bundle is present and usable. rev0055 makes the source-bundle use explicit and adds rerun evidence that depends on it.

## Files to use going forward

```text
docs/SOURCE-BUNDLE-USAGE-GATE-REV0055.md
data/rev0055_source_bundle_usage_gate.csv
data/rev0055_source_bundle_stack_rerun_matrix.csv
tools/probe_rev0055_source_bundle_usage_gate.py
```
