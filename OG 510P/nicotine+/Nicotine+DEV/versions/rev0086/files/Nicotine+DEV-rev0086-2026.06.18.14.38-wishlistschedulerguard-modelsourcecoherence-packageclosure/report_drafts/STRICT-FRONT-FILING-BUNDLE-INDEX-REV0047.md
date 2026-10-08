# Strict/front filing bundle index — rev0047

This index supersedes the rev0045 flat filing index and should be used with the rev0046 integrated stack matrix.

## Recommended order

```text
1. U-123 transfer-session identity
2. PB-01 peer primary-election compatibility
3. FileSearchResponse source-admission series
4. FileSearchResponse parser-budget series
```

## Bundle 1 — transfer-session identity

```text
Packet: U-123
Report: report_drafts/U123-PRODUCTION-READY-MAINTAINER-REPORT-REV0037.md
Patch:  report_drafts/U123-SELECTED-PATCH-REV0037.diff
Regression: maintainer_artifacts/u123/test_downloads_duplicate_transfer_token_collision_rejection_regression.py
Evidence: evidence/rev0037-u123-collision-rejection-rerun.txt
Integrated evidence: evidence/rev0046-strict-bundle-integrated-rerun-matrix.txt
```

## Bundle 2 — peer primary-election compatibility

```text
Packet: PB-01
Report: report_drafts/PB01-PRODUCTION-READY-MAINTAINER-REPORT-REV0038.md
Patch:  report_drafts/PB01-SELECTED-PATCH-REV0038.diff
Regression: maintainer_artifacts/pb01/test_peer_connection_primary_election_fixed_regression.py
Evidence: evidence/rev0038-pb01-fixed-regression-rerun.txt
Integrated evidence: evidence/rev0046-strict-bundle-integrated-rerun-matrix.txt
```

## Bundle 3 — FileSearchResponse source admission

```text
Packets:
  SEARCH-RESP-01A
  SEARCH-RESP-01B-BUDDY
  SEARCH-RESP-01C-ROOM

Current stacked patch set:
  report_drafts/SEARCH-RESP-01C-ROOM-SELECTED-PATCH-REV0043-3.3.10.diff
  report_drafts/SEARCH-RESP-01C-ROOM-SELECTED-PATCH-REV0043-3.3.x.diff
  report_drafts/SEARCH-RESP-01C-ROOM-SELECTED-PATCH-REV0043-master.diff
```

The rev0043 patch stacks the rev0039 user guard and rev0040 buddy snapshot guard.

## Bundle 4 — FileSearchResponse parser budgets

```text
Packets:
  SEARCH-RESP-PARSE-BUDGET-A
  SEARCH-RESP-PARSE-BUDGET-B

Current stacked patch set:
  report_drafts/SEARCH-RESP-PARSE-BUDGET-B-SELECTED-PATCH-REV0042-3.3.10.diff
  report_drafts/SEARCH-RESP-PARSE-BUDGET-B-SELECTED-PATCH-REV0042-3.3.x.diff
  report_drafts/SEARCH-RESP-PARSE-BUDGET-B-SELECTED-PATCH-REV0042-master.diff
```

Keep this parser-budget series separate from source admission. It touches `pynicotine/slskmessages.py`, not the search-mode admission policy in `pynicotine/search.py`.
