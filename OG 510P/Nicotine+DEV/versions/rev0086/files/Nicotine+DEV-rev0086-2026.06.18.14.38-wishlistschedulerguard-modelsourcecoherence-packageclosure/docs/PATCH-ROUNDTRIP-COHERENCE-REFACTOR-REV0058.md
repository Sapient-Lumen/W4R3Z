# rev0058 — patch roundtrip coherence/refactor

This refactor pass prevents the cube from over-merging several similar-looking evidence layers.

## Refactor result

```text
rev0051 source anchors:
  line/hash source-reading evidence for archived source lanes.

rev0056 baseline-delta replay:
  before/after behavior evidence: current witnesses pass on unpatched source, fixed regressions fail before patch, selected stack passes after patch.

rev0057 patch queue:
  reviewer-facing lane patch files, patch hashes, source-file hashes, and marker audit.

rev0058 patch-file roundtrip:
  proof that the rev0057 patch files, as files, apply to clean uploaded source lanes and preserve all seven fixed-regression gates.

rev0053/rev0054 current-source gates:
  live-current checkout/web-marker context, still separate and still not completed as a filing replacement.
```

## Boundary corrections retained

- The uploaded `Nicotine-source(1).zip` is used as the archived source input.
- The rev0057 patch files are generated for that archived source bundle, not for an unknown future checkout.
- The rev0058 gate proves patch-file applyability plus fixed-regression preservation against the archived lanes.
- The current-upstream filing gate remains separate: a fresh checkout or current tarball with commit identity must still be captured before live-current external filing.
- Public path traversal/watch rows remain public context only and are not part of the seven private strict/front packets.

## Filing-bundle split retained

```text
1. U-123 transfer-session identity
2. PB-01 peer primary-election compatibility
3. FileSearchResponse source admission:
   - SEARCH-RESP-01A
   - SEARCH-RESP-01B-BUDDY
   - SEARCH-RESP-01C-ROOM
4. FileSearchResponse parser budget:
   - SEARCH-RESP-PARSE-BUDGET-A
   - SEARCH-RESP-PARSE-BUDGET-B
```

No new private packet is promoted in rev0058.
