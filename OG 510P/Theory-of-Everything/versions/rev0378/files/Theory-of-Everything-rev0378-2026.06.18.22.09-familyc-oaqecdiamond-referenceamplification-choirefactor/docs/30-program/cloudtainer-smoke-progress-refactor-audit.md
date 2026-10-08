# Cloudtainer smoke progress refactor audit

Revision: `rev0365`

## Scope

This audit handles the rev0364 replay-risk finding: the archive's direct checks were healthy, but aggregate lint/smoke execution could look stalled in a small cloudtainer.

## Implemented change

- Added `tools/run_lint_steps.py` as the canonical `make lint` runner.
- `make lint` now emits named step start/OK/fail lines with elapsed seconds.
- Package smoke now checks the provenance sidecars and candidate-docket audit in the extracted tree before mutation replay, schema validation, archive lint, and deterministic rebuild.
- Package smoke now prints elapsed time per subprocess, so a slow step is visible as a slow step rather than an ambiguous hang.
- Source-role negative replay now builds temporary mutation trees as real directories with symlinked read-only files, then materializes private copies before writes. This avoids repeated full-tree copies without risking hard-link mutation of the source archive.

## Step boundary

The timed lint runner keeps the same semantic checks but makes them observable:

1. clean transients;
2. check release provenance sidecars;
3. check candidate-native docket duplication audit;
4. run source-role negative replay;
5. run registered JSON Schema validation;
6. run archive lint.

## Why this is not bureaucracy

The change shortens failure localization. If a future revision breaks packaging, the operator should know whether the failure is generated-sidecar drift, archive invariants, source-role mutation replay, schema contracts, or deterministic rebuild. That is a concrete cloudtainer-cost reduction.

## Non-promotion boundary

This refactor changes replay ergonomics only. It does not alter route state, evidence credit, forecast realization, public-record credit, observed-sector recovery, or current-head scientific authority.
