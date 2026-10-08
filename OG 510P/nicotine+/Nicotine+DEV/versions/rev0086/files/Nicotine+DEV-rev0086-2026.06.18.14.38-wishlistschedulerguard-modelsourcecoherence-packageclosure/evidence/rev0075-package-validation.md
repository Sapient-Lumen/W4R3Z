# rev0075 package validation

## Pre-manifest gate

```text
status: pass
coherence checks: 32/32 pass
required paths: 41 present
compiled rev0075 Python files: 14
compile failures: 0
forbidden paths: 0
symlinks: 0
payload files excluding this record, its JSON, and manifest: 3012
payload bytes on the same basis: 145145732
```

The preflight intentionally records `manifest: not-yet-generated`. After this record is written, `tools/build_rev0075_manifest.py` hashes every package file except the manifest itself. The same fail-closed audit is then run against the root and against a clean extraction of the final ZIP.

The gate rejects missing current-authority documents, ledger drift, test/source-matrix drift, archive-hash drift, inconsistent duplicate accounting, Python compile failures, embedded upstream source, source ZIPs, Git metadata, caches, symlinks, and incomplete or mismatched manifest rows.
