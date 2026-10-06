# RFC-0051: Deterministic image building (mtree/makefs/mkimg)

- Status: draft
- Created: 2026-02-23

## Summary
Standardize the DeriveBSD image build pipeline using mtree → makefs → mkimg for deterministic microVM disk artifacts.

## Goals
- reproducible image creation from manifests
- policy-governed determinism knobs
- audit-friendly mapping and digests

## References
- mtree(8), makefs(8), mkimg(1)
- FreeBSD release tooling (release(7))
