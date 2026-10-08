# Safe-extractor negative-control runtime refactor

**Track:** Shared / Release engineering / Safe extraction
**Status:** v857 executable release-gate refactor
**Scope:** `scripts/check_release_safe_extractor.py`, `artifacts/reports/release-safe-extractor-runtime-refactor-rev0857.*`

## What changed

`check_release_safe_extractor.py` used to build and repeatedly extract a full release ZIP while testing extractor safety. That was substantively correct but wasteful: the checked behavior is the extractor bridge, not the size of the cube.

v857 replaces the full-cube negative-control carrier with a tiny canonical release ZIP containing `MANIFEST.sha256`, `VERSION`, `README.md`, and one nested docs member. The probe still exercises the same important boundaries:

```text
verify before extraction
extract from the verifier byte snapshot
reject bad ZIPs before writing
reject ambiguous ZIP input paths
reject non-empty outputs unless --clean is explicit
reject output symlinks and symlinked ancestry
reject lexical output traversal/current/empty components
preserve canonical directory and file modes
fail closed on member-directory, temp-root, and output-parent swap probes
```

## Why this is risk-first

The one-command release gate is only useful if it reaches substantive verifier, source, packaging, and manifest checks. A negative-control test that repeatedly packages/extracts thousands of files can become a local denial-of-service failure mode even when the underlying extractor is healthy.

The refactor keeps the extractor contract executable while avoiding repeated full-cube packaging/extraction inside the smoke test. Full final release ZIP verification, safe extraction, and extracted-tree manifest verification still run against the real packaged archive before a release is linked.

## Boundary

This is release-engineering hardening only. It does not prove production signer authority, publication governance, current voter instruction, certification, legal reliance, or live-pilot readiness.
