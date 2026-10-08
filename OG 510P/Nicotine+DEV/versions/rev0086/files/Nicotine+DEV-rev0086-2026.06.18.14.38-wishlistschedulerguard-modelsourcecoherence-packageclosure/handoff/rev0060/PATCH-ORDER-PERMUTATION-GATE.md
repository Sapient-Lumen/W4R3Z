# rev0060 handoff — patch-order permutation gate

This handoff gate is for reviewers applying the rev0059 split filing-bundle patches.

## Input patches

The gate uses the twelve rev0059 bundle patches:

```text
3 archived lanes × 4 filing bundles = 12 patch files
```

Bundles:

```text
U-123
PB-01
SEARCH-RESP-SOURCE-ADMISSION
SEARCH-RESP-PARSER-BUDGET
```

## Order-safety check

For each archived lane, rev0060 applies every possible order of the four bundle patches:

```text
4! = 24 orders per lane
3 lanes × 24 orders = 72 patch-order rows
```

For every order, the five touched source files are hashed and compared to the canonical rev0059 patched-source hashes.

```text
72 patch-order rows: pass
360 final file-hash rows: pass
```

## Regression check

rev0060 also reruns all seven fixed-regression gates on two explicit orders per lane:

```text
canonical order
reverse order
```

```text
3 lanes × 2 orders × 7 packets = 42 regression rows: pass
```

## Reviewer implication

The split bundle patches are order-safe against the uploaded archived source bundle. Reviewers can apply the four bundles in any order for these archived lanes and reach the same final source-file state.

## Boundary

This is archived-source patch-series proof only. A fresh current checkout or current-source tarball with commit identity remains required before live-current external filing.
