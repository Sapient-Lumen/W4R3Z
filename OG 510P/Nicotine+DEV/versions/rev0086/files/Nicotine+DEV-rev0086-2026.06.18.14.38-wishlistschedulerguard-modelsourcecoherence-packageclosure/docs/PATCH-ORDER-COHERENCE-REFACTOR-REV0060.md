# rev0060 patch-order coherence refactor

## Refactor decision

rev0060 adds a new evidence layer named **patch-order permutation proof**. This layer is intentionally separate from the earlier strict/front gates.

## Separation table

| Layer | Role | rev0060 decision |
| --- | --- | --- |
| rev0056 baseline-delta replay | Proves before/after behavior on uploaded archived source | retained; not duplicated |
| rev0057 combined patch queue | Produces lane-specific selected-stack patches | retained; not treated as order proof |
| rev0058 patch-file roundtrip | Proves combined patch files apply/reverse correctly | retained; not split-bundle order proof |
| rev0059 patch-layer attribution | Proves each packet is carried by its intended bundle, not another bundle | retained; not a permutation proof |
| rev0060 patch-order permutation | Proves the four split bundle patches commute as a reviewer-facing series | added |
| rev0051 source anchors | Line-level archived source evidence | retained; not patch application evidence |
| rev0054 current-web markers | Web-visible marker snapshot | retained; not source checkout proof |
| public path watch rows | Public PR/path traversal tracking | retained as public-overlap only |
| fresh-current checkout proof | Required for live-current filing | still pending/separate |

## Filing bundle boundary

The filing bundles remain:

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

rev0060 does not split or merge any production-gated packet. It only audits whether the patch bundles can be applied in arbitrary order against the uploaded archived source lanes.

## Audit result

```text
new private packets: 0
production-gated maintainer packets retained: 7
patch-order permutations: 72/72 pass
permutation final file-hash rows: 360/360 pass
canonical/reverse fixed-regression rows: 42/42 pass
```

## Next queue boundary

The highest-priority remaining gate is unchanged:

```text
fresh current checkout or current-source tarball with commit identity
```

Only after that source identity is available should the seven fixed-regression gates be rerun and classified as current-upstream-ready, native-fixed, superseded-equivalent, or retired.
