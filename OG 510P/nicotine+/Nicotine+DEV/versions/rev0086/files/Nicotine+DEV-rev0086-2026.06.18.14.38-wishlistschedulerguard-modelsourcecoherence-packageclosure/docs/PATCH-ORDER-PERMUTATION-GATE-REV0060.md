# rev0060 patch-order permutation gate

## Purpose

rev0059 split the strict/front selected stack into four filing-bundle patches per archived source lane:

```text
U-123
PB-01
SEARCH-RESP-SOURCE-ADMISSION
SEARCH-RESP-PARSER-BUDGET
```

rev0060 checks that this split is not hiding an order dependency. It uses the uploaded `Nicotine-source(1).zip` as the archived source input, applies all 24 possible orders of the four bundle patches for each of the three archived lanes, and compares the resulting source-file hashes against the canonical patched hashes from rev0059.

## Source lanes

```text
github-tag-3.3.10
github-branch-3.3.x
github-branch-master
```

## Patch order matrix

```text
lanes: 3
bundle orders per lane: 24
total patch-order rows: 72
expected result: every order applies cleanly and reaches the same final source-file hashes
```

The final source files checked are:

```text
pynicotine/downloads.py
pynicotine/transfers.py
pynicotine/slskproto.py
pynicotine/search.py
pynicotine/slskmessages.py
```

Result recorded by rev0060:

```text
patch-order permutations: 72/72 pass
permutation final file-hash rows: 360/360 pass
```

## Regression confirmation

After the permutation/hash gate, rev0060 reruns the seven fixed-regression gates on two explicit patch orders per lane:

```text
canonical order:
  U-123 -> PB-01 -> SEARCH-RESP-SOURCE-ADMISSION -> SEARCH-RESP-PARSER-BUDGET

reverse order:
  SEARCH-RESP-PARSER-BUDGET -> SEARCH-RESP-SOURCE-ADMISSION -> PB-01 -> U-123
```

Result recorded by rev0060:

```text
canonical/reverse fixed-regression rows: 42/42 pass
```

That means:

```text
3 lanes × 2 orders × 7 fixed-regression gates = 42 passing regression rows
```

## What this proves

rev0060 proves the archived-source bundle patches are order-safe for reviewer application. The four bundle patches touch separate source-file groups and converge to the same source hashes regardless of the order in which they are applied.

## What this does not prove

rev0060 does not replace:

```text
fresh current checkout/tarball proof
current-source seven-gate rerun
release-branch merge-state review
public PR/milestone overlap review
```

Those remain separate gates before live-current external filing.

## Primary artifacts

```text
data/rev0060_patch_order_permutation_matrix.csv
data/rev0060_patch_order_file_hash_matrix.csv
data/rev0060_patch_order_regression_matrix.csv
data/rev0060_patch_order_summary.csv
evidence/rev0060-patch-order-rerun/
tools/probe_rev0060_patch_order_permutation.py
```
