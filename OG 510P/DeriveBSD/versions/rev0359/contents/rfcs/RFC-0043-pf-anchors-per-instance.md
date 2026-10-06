# RFC-0043: Per-instance pf anchors + rule digesting

- Status: draft
- Created: 2026-02-23

## Summary
Define deterministic per-instance pf anchor naming, canonical rule generation, and audit logging of pf rules digests.

## Goals
- isolate rulesets per instance (blast radius)
- atomic updates via anchor replacement
- conformance tests for rule output

## References
- pf.conf(5) anchors
- pfctl(8) anchor operations
