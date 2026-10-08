# 877. Numbered-doc track-header gate and generated-index invariant

**Track:** Shared (Release engineering and gate reliability)
**Status:** rev0856 release-gate repair

## Problem fixed

The next concrete one-command gate failure after the artifact-index repair was `scripts/check_tracks.py`. Recent numbered docs and the generated `docs/13-artifact-index.md` can be release-critical, but if they lack a valid `**Track:**` header the gate stops before it reaches verifier, source, packaging, and manifest checks.

That is a real maintenance failure, not a cosmetic one. Track headers are the archive's low-tech routing layer. Losing them makes the cube harder to triage and lets generated docs drift outside the same release controls as hand-written docs.

## rev0856 change

rev0856 repairs the recent numbered-doc track headers, keeps `docs/13-artifact-index.md` inside the generated header invariant, and adds `scripts/report_track_header_surface.py` so the problem is visible as a small audit artifact instead of only as a long release-gate failure.

Generated reports:

```text
artifacts/reports/track-header-surface-rev0856.json
artifacts/reports/track-header-surface-rev0856.json
artifacts/reports/track-header-surface-audit-rev0856.md
```

## Boundary

This is a release-navigation and gate-reliability repair only. It does not change verifier cryptographic semantics, signer authority, source freshness, current voter instruction, certification, legal reliance, or live-pilot readiness.
