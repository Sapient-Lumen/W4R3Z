# Store tree serialization and digests (NAR lessons, Derive “DAR” sketch)

DeriveBSD needs a **canonical, streamable encoding** for filesystem trees to:
- compute stable content digests
- replicate artifacts across caches
- verify artifacts without trusting the transport

Nix’s NAR format exists for similar reasons:
- it elides metadata Nix doesn’t consider meaningful for identity (e.g., timestamps) and uses a deterministic representation for store paths.

References in `docs/32-curated-references.md`.

## DeriveBSD target: “DAR” (Derive ARchive) concept

A Derive tree encoding should be:
- **canonical** (one encoding for one tree)
- **streamable** (hashable while streaming)
- **policy-aware** (what metadata is identity vs non-identity)

### Encoding units (conceptual)
- header: { version, hash_alg, feature_flags }
- entries (sorted by path):
  - type: file/dir/symlink/dev/…
  - mode bits (policy-controlled subset)
  - uid/gid mapping (policy-controlled)
  - file flags / ACL / xattrs (optional tiers)
  - content: raw bytes (or chunk references)
  - for symlink: target string

### Metadata tiers
Policy chooses what contributes to identity:
- Tier 0: path, type, bytes, exec-bit only
- Tier 1: full mode bits + normalized uid/gid
- Tier 2: xattrs/ACLs/flags (explicit allowlist)

### Chunking
Optional: chunk large files into fixed or content-defined chunks:
- enables dedup
- supports partial fetch
- attestation can cover chunk map

## Relationship to mtree
- `mtree(8)` is ideal as the *manifest view* of a tree, and can be used to generate/verify a DAR tree description.
- `makefs(8)` can build images from a directory or mtree manifest; DAR can be an intermediate for deterministic staging.

## Non-goals (v1)
- perfect “support everything” metadata semantics from day one
- silently including OS-specific metadata in identity without policy

See RFC-0054 and ADR-0024.

Last updated: 2026-02-23
