# Release safe-extractor gate surface audit

**Track:** Shared / Release engineering / Audit
**Status:** v857 generated-audit companion
**Scope:** `artifacts/reports/release-safe-extractor-runtime-refactor-rev0857.json`

## Result

v857 treats the safe extractor as a high-risk release bridge: verifier acceptance must happen before writes, writes must come from the verifier's byte snapshot, and the post-extraction tree must match `MANIFEST.sha256` before publication.

The audit records the runtime and semantic surface of the refactored gate. Its purpose is to stop the release gate from burning time on repeated full-cube extraction while still proving the failure modes that matter.

## Secondary size-budget cleanup

While finishing v857, the size gate exposed another release-control waste path: track-header CSV reports repeated every numbered doc even though the JSON and Markdown summaries already carry total counts. The CSV surface now carries actionable failure rows only, which keeps `scripts/check_tracks.py` auditable without spending release size budget on duplicate success rows.

## Maintainer rule

Use the small synthetic carrier for extractor negative controls. Use the real release ZIP for the final artifact checks:

```text
scripts/verify_release_zip.py <release.zip>
scripts/extract_release_zip.py <release.zip> <safe-output-dir>
scripts/verify_manifest.py <safe-output-dir>
```

Boundary: this audit is not a production deployment assertion, independent validation, legal advice, certification, current voter instruction, or live-pilot authorization.
