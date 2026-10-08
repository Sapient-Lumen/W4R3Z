# Release-gate index-surface audit and full-gate recovery

**Track:** Shared / Release gate / Artifact index
**Status:** v855/v856 release-gate coherence repair

## What v855 audits

v855 adds `scripts/report_artifact_index_surface.py` and generated `artifacts/reports/artifact-index-surface-rev0855.*` reports. The audit counts canonical numbered docs, confirms that the generated marker is present, verifies that the artifact-index header is not duplicated, and records whether the release gate is still likely to fail at the first index step.

The audit exists because the old failure mode was simple and wasteful: a release could be otherwise healthy, but maintainers would not learn that until after fixing a collapsed index by hand.

## Correction path

The v855 correction path is intentionally small:

1. Generate `docs/13-artifact-index.md` from the live tree.
2. Check that every canonical numbered doc name is present.
3. Keep the generator in the release-gate inventory so future revisions do not rely on manual index hygiene.
4. Record the audit result in machine-readable JSON and CSV.

## Maintenance boundary

Do not use this audit as a proxy for substance. A generated index can prove coverage of filenames, not quality of the docs. It should be treated as a cheap release-gate guardrail that lets maintainers spend attention on verifier boundaries, source freshness, and live-pilot no-go evidence.
