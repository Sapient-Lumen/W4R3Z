# rev0787 connection authority audit

## Scope

Target: `src/sync_domain.cpp`

The audit distinguishes requested configuration from observed runtime evidence. It fails if the target
regresses to a raw `sqlite3_open_v2` call, if the wrapper stops pinning/observing VFS state, if access mode
is not observed, or if the busy-handler guard becomes movable/copyable.

## Deliberately unresolved

- Existing direct `sqlite3_busy_handler` uses outside the new guard are not mechanically rewritten. Their
  callback contexts must be migrated together with the operation mutex and owner-generation token.
- `SQLITE_FCNTL_VFSNAME` reports a stack; wrappers/shims are accepted only when the pinned VFS appears as an
  exact slash-delimited component.
- In-memory databases have no backing file for the file-control probe and are explicitly classified rather
  than accidentally treated as verified disk VFS evidence.

## Waste finding

The repository continues to retain historical audit/evidence trees inside every handoff ZIP. This makes
archives larger and static searches noisier. rev0787 keeps lineage evidence for compatibility but records
first-party metrics separately and excludes build products. A later packaging-only revision should move
old evidence into a content-addressed external ledger while preserving signed digests in the cube.
