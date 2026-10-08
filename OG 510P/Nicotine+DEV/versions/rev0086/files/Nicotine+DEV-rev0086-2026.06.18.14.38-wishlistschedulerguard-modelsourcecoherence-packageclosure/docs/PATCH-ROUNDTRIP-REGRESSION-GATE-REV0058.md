# rev0058 — patch-file roundtrip regression gate

rev0058 continues from rev0057 and does **not** promote a new private packet. The purpose of this revision is to close a reviewer-facing gap between two existing proof layers:

```text
rev0056: selected helper stack passes fixed regressions after patching clean uploaded source lanes
rev0057: lane-specific selected-stack patch files are generated and hash/marker checked
rev0058: those patch files themselves are applied to clean uploaded source lanes and the fixed regressions are rerun
```

The uploaded source bundle remains the explicit archived-source input:

```text
Nicotine-source(1).zip SHA256: feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b
source lanes: github-tag-3.3.10, github-branch-3.3.x, github-branch-master
source embedded in compact cube zip: no
```

## Patch-file roundtrip

For each lane, rev0058 starts from a clean extraction of the uploaded source bundle and uses the rev0057 patch file:

```text
handoff/rev0057/patches/github-tag-3.3.10/strict-front-selected-stack-rev0057.patch
handoff/rev0057/patches/github-branch-3.3.x/strict-front-selected-stack-rev0057.patch
handoff/rev0057/patches/github-branch-master/strict-front-selected-stack-rev0057.patch
```

The roundtrip gate records four patch stages per lane:

```text
forward dry-run before apply
forward apply
reverse dry-run after apply
second forward dry-run rejected after apply
```

Results:

```text
patch apply roundtrip rows: 12/12 pass
patched source-file hash rows: 15/15 pass
fixed-regression rows after patch-file apply: 21/21 pass
```

## Fixed-regression rerun after applying patch files

The seven strict/front fixed-regression gates were rerun on the patch-file-applied lanes:

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

Raw outputs are stored in:

```text
evidence/rev0058-patch-roundtrip-rerun/
```

Machine-readable matrices are stored in:

```text
data/rev0058_patch_roundtrip_apply_matrix.csv/json
data/rev0058_patch_roundtrip_file_hashes.csv/json
data/rev0058_patch_roundtrip_fixed_regression_matrix.csv/json
data/rev0058_patch_roundtrip_summary.csv/json
```

The helper is:

```bash
python tools/probe_rev0058_patch_roundtrip_gate.py --source-zip /path/to/Nicotine-source.zip --run-tests --lane github-branch-master
```

The recorded full matrix was assembled from three lane-specific helper runs. This keeps the proof lane-local while avoiding all-in-one wrapper timeouts in the execution environment.

## Status after rev0058

```text
strict report-candidates: 7
production-gated maintainer packets: 7
production-ready disclosure texts in cube: 7
new private packets in rev0058: 0
source bundle used: yes
rev0057 patch files reused: 3
patch-file roundtrip fixed-regression rows: 21/21 pass
fresh current checkout for live external filing: still separate/pending
```

Boundary retained: rev0058 is archived-source patch-file proof against the uploaded source bundle. It does not replace a fresh current checkout/tarball and current-source seven-gate rerun before live-current external filing.
