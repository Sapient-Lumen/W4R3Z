# Source-bundle usage gate — rev0055

This revision responds to the source-use correction: the uploaded `Nicotine-source(1).zip` is now treated explicitly as the archived-source input for the cube.

## Decision

The uploaded source bundle **is used**. It is not embedded in the compact cube zip, but rev0055 records it as an external input and verifies the strict/front evidence against it.

```text
source zip: Nicotine-source(1).zip
source SHA256: feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b
zip entries: 3551
source root: Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z
lanes: github-branch-3.3.x, github-branch-master, github-tag-3.3.10
```

## What was corrected

rev0053/rev0054 correctly kept a separate blocker for a fresh current upstream checkout, but their latest summaries could read as if the uploaded source bundle was not being used. That was too ambiguous.

rev0055 separates the concepts:

```text
uploaded source bundle: used as the archived-source baseline and regression source
fresh current checkout: still required only before filing against live/current upstream
web marker snapshot: supplementary triage only, not a replacement for source or tests
```

## Evidence added

```text
evidence/rev0055-source-anchor-helper-rerun.json
  - rev0051 source-anchor helper rerun against /mnt/data/Nicotine-source(1).zip
  - status: pass
  - anchor rows: 126

evidence/rev0055-current-upstream-gate-sourcezip-rerun.json
  - rev0053 source-zip marker scan rerun against /mnt/data/Nicotine-source(1).zip
  - status: pass
  - marker rows: 21
  - selected markers present: 0
  - selected markers missing: 54

evidence/rev0055-strict-stack-sourcebundle-rerun-matrix.txt/json
  - rev0046 integrated selected patch stack rerun on extracted source lanes
  - gates: 21/21 pass
```

## Strict stack rerun summary

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

## Boundary retained

The source bundle is an archived rev0003 upstream-source bundle. It proves the archived source baseline and supports the selected patch-stack rerun. It does **not** replace a fresh current checkout/tarball when the filing target is live upstream head.

No new private packet is promoted in rev0055.
