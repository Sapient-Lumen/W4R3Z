# rev0059 patch-layer coherence refactor

rev0059 performs a coherence/refactor pass over the strict/front patch material. The goal is to prevent the selected patch stack from being over-read as one monolithic vulnerability or one inseparable patch.

## Refactor decision

The seven production-gated packets remain intact, but the patch material is now grouped into four filing bundles:

```text
1. U-123 transfer-session identity
2. PB-01 peer primary-election compatibility
3. FileSearchResponse source-admission series
   - SEARCH-RESP-01A
   - SEARCH-RESP-01B-BUDDY
   - SEARCH-RESP-01C-ROOM
4. FileSearchResponse parser-budget series
   - SEARCH-RESP-PARSE-BUDGET-A
   - SEARCH-RESP-PARSE-BUDGET-B
```

## What was separated

```text
patch generation proof
  separated from patch-file roundtrip proof

patch-file roundtrip proof
  separated from fixed-regression attribution

source-admission fixes
  separated from parser-budget fixes even though both touch FileSearchResponse behavior

archived-source proof
  separated from fresh-current checkout proof

public path-traversal/watch rows
  separated from all seven private strict/front packets
```

## Non-claims preserved

rev0059 does not claim that the selected patches are already present in live current upstream. It also does not claim that the public path traversal PRs are private cube findings. Those remain public-watch-only context.

## Result

The cube now has a cleaner handoff path:

```text
claim capsules -> source anchors -> filing-field map -> baseline delta -> combined patch roundtrip -> split patch attribution
```

This gives a reviewer both the high-level packet claims and the low-level patch attribution needed to audit the selected fix shape.
