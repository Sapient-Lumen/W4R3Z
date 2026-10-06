# RFC-0087: Store/image distribution adapters (casync, CernVM-FS lessons)

Status: Draft

## Summary

Define optional distribution adapters beyond “binary caches”:
- chunked image distribution (casync-like)
- read-only store snapshot distribution (CernVM-FS-like)

References:
- casync: https://github.com/systemd/casync
- CernVM-FS overview: https://cvmfs.readthedocs.io/

## Goals

- Reduce bandwidth and speed up cold starts for fleets.
- Preserve DeriveBSD signature/provenance semantics.

## Design sketch

- Adapter interface:
  - publish(index, chunks) bound to artifact digest
  - fetch missing chunks
  - verify chunks + final digest

See: `docs/119-casync-cvmfs-distribution.md`.
