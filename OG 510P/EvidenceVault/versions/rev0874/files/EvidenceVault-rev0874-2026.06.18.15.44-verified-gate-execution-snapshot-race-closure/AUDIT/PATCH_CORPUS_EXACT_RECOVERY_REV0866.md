# Patch-corpus exact recovery and live coverage refactor — rev0866

## Result

rev0866 recovered **81 previously missing canonical files (546,423 bytes)** from byte-complete new-side streams already present in the historical patch corpus. Every recovered file matches both the indexed byte count and SHA-256 in `INDEX/files.csv`. The set includes **12 source payloads (13,568 bytes)**.

Canonical exact coverage moves from **19 to 100 files** and from **4,338,844 to 4,885,267 bytes**. Missing indexed paths fall from **4,550 to 4469**. Exact canonical source paths rise from **1 to 13**.

## Recovery boundary

The recovery engine accepts only a contiguous new-side stream beginning at line 1 and only after its size and SHA-256 exactly match the canonical index. It does not infer omitted context, patch together partial hunks, or overwrite later-revision bytes. Five exact baseline candidates are present at paths that now contain later overlay revisions; those paths were deliberately left untouched.

Operator writes are permitted only into a separate tree with the identical canonical index. Symlink traversal, overlap with the tool bundle, and non-matching existing targets are rejected. Writes use a no-clobber atomic publication step and are verified afterward.

## Gate refactor

`scripts/canonical_coverage.py` is now the shared live coverage engine. `scripts/overlay_gate.py` recomputes coverage before either listing or running checks and rejects any stale or inflated `PATCH_BUNDLE_MANIFEST.json` profile. The gate no longer merely repeats declared representation counts.

## Command-surface audit

The canonical `Makefile` contains 47 unique lexical references to `scripts/*.py` or `scripts/*.sh`; **42 are absent**. None of those missing command-surface files was recoverable from the exact patch-body set. `make gate` therefore remains the wrong entrypoint for this partial overlay; use:

```bash
python3 scripts/overlay_gate.py
```

## Remaining risk

Rights closure remains the highest publication risk. The recovered `RIGHTS/NOTICE.draft` and other historical rights files are canonical evidence payloads, **not** active grants. The cube still lacks an owner-approved root license or notice, 4469 indexed files remain absent, 17 same-path files remain revision-divergent, and the 17 selected StreamFold payloads remain missing.

The machine-readable audit contains every recovered path, hash, origin, coverage delta, skipped divergence, and missing Makefile reference.
