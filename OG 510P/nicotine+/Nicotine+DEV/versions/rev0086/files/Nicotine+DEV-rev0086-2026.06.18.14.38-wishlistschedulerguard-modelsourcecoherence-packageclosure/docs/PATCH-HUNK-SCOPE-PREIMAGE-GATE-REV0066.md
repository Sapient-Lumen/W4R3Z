# Patch hunk-scope / preimage binding gate — rev0066

rev0066 continues from rev0065 and adds a hunk-level gate for the exported rev0059 split patch series.

The prior chain already established:

- source-bundle intake and safe extraction;
- Git worktree/ref/commit/tree provenance for the uploaded source bundle;
- selected split patches, roundtrip application, attribution, order permutations, clean-room replay, and contract/tamper controls.

rev0066 fills the review gap between “the patch applies” and “the patch is narrowly scoped.” It parses the twelve rev0059 split patch files and binds every hunk to the original source bytes in the uploaded `Nicotine-source(1).zip` archive.

```text
source bundle SHA256: feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b
source SHA256 status: pass
lanes: 3
bundle patch files: 12
file-scope rows: 15/15 pass
hunk preimage rows: 41/41 pass
marker contract rows: 30/30 pass
negative controls: 4/4 pass
```

## What the gate checks

For each archived lane and each split filing bundle, `tools/probe_rev0066_patch_hunk_scope.py`:

1. reads the patch from `handoff/rev0059/patches/<lane>/`;
2. rejects unsafe or out-of-scope patch paths;
3. checks the touched file set against the bundle-specific contract;
4. reads the original source file directly from the uploaded source ZIP;
5. validates every hunk context/removal line against the original source preimage;
6. rebuilds the patched file in memory;
7. compares the original and patched SHA256 hashes against `data/rev0059_bundle_patch_file_hashes.csv`;
8. verifies required marker lines for the bundle's selected invariant.

## Bundle file-scope contract

```text
U-123:
  pynicotine/downloads.py
  pynicotine/transfers.py

PB-01:
  pynicotine/slskproto.py

SEARCH-RESP-SOURCE-ADMISSION:
  pynicotine/search.py

SEARCH-RESP-PARSER-BUDGET:
  pynicotine/slskmessages.py
```

## Negative controls

rev0066 includes four fail-closed controls:

```text
unsafe-path: rejects parent traversal patch paths
bad-context: rejects corrupted hunk preimage/context
unexpected-file: rejects a patch touching a file outside the bundle contract
missing-marker: rejects a markerless source-admission patch
```

## Decision

No new private packet is promoted in rev0066. The seven strict/front packets remain production-gated against the archived source bundle, with a stronger hunk-level evidence chain. Live-current external filing still requires a fresh current checkout/tarball and current-source seven-gate rerun.
