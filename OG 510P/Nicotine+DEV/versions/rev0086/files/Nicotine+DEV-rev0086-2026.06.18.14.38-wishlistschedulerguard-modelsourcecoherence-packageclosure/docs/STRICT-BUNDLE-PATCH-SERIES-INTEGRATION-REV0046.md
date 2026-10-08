# STRICT-BUNDLE patch-series integration — rev0046

## Decision

rev0046 keeps all seven strict/front packets production-gated and does not open a new packet. The revision converts rev0045's filing index into an integrated patch-series gate.

## Why this revision exists

Earlier revisions proved each packet in isolation. That is enough for packet-level evidence, but not enough for a maintainer handoff. The search-response work in particular has intentional stacking:

```text
SEARCH-RESP-01A -> SEARCH-RESP-01B-BUDDY -> SEARCH-RESP-01C-ROOM
SEARCH-RESP-PARSE-BUDGET-A -> SEARCH-RESP-PARSE-BUDGET-B
```

rev0046 therefore applies the latest selected stack once per lane and reruns all seven fixed-behavior regressions against the same patched checkout.

## Source lanes

```text
github-tag-3.3.10
github-branch-3.3.x
github-branch-master
```

Source bundle used:

```text
Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z
```

## Applied stack

```text
1. U-123 selected transfer-session identity patch
2. PB-01 selected primary-election patch from rev0038
3. SEARCH-RESP source-set selected patch from rev0043
4. SEARCH-RESP parser-budget selected patch from rev0042
```

The rev0043 source-set patch is intentionally the patch-of-record for SEARCH-RESP-01A, SEARCH-RESP-01B-BUDDY, and SEARCH-RESP-01C-ROOM. The rev0042 parser-budget patch is intentionally the patch-of-record for both SEARCH-RESP-PARSE-BUDGET-A and SEARCH-RESP-PARSE-BUDGET-B.

## Result matrix

```text
github-tag-3.3.10:
  U-123: OK
  PB-01: 11 passed
  SEARCH-RESP-01A: 7 passed
  SEARCH-RESP-01B-BUDDY: 8 passed
  SEARCH-RESP-01C-ROOM: 8 passed
  SEARCH-RESP-PARSE-BUDGET-A: 4 passed
  SEARCH-RESP-PARSE-BUDGET-B: 4 passed

github-branch-3.3.x:
  U-123: OK
  PB-01: 11 passed
  SEARCH-RESP-01A: 7 passed
  SEARCH-RESP-01B-BUDDY: 8 passed
  SEARCH-RESP-01C-ROOM: 8 passed
  SEARCH-RESP-PARSE-BUDGET-A: 4 passed
  SEARCH-RESP-PARSE-BUDGET-B: 4 passed

github-branch-master:
  U-123: OK
  PB-01: 11 passed
  SEARCH-RESP-01A: 7 passed
  SEARCH-RESP-01B-BUDDY: 8 passed
  SEARCH-RESP-01C-ROOM: 8 passed
  SEARCH-RESP-PARSE-BUDGET-A: 4 passed
  SEARCH-RESP-PARSE-BUDGET-B: 4 passed
```

Full command output is in `evidence/rev0046-strict-bundle-integrated-rerun-matrix.txt`.

## Status after rev0046

```text
strict report-candidates: 7
production-gated maintainer packets: 7
production-ready disclosure texts in cube: 7
integrated selected-patch stack: pass
new packets promoted: 0
```
