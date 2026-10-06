# RFC-0054: Store tree serialization (“DAR”) and digests

- Status: draft
- Created: 2026-02-23

## Summary
Define a canonical, streamable encoding for filesystem trees to compute stable digests and enable cache replication and verification.

## Goals
- canonical encoding
- policy-controlled metadata identity tiers
- optional chunking for large blobs

## References
- Nix NAR (`nix-store --dump`) as a lesson
- mtree(8), makefs(8)
