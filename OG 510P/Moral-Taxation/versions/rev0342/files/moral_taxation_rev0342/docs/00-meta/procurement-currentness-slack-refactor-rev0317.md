# Procurement currentness and slack refactor — rev0317

Rev0317 focused on the thinnest remaining risk after rev0316: procurement was barely positive on compactness and still used volatile procurement/defense sources without source-currentness claims.

## What changed

- Compressed all five `public_procurement_industrial_policy` calibration ladders into priority gates while keeping route-specific option scans, defaults, and the three required capsules.
- Added `S673`, a GAO 2026 sustainment-cost report, to the defense procurement route so lifecycle operating-and-support cost growth is not hidden behind acquisition-stage cost growth alone.
- Added source-currentness refs and claims for the procurement subsidy route (`S512`, `S513`, `S514`) and defense procurement route (`S610`, `S611`, `S612`, `S613`, `S673`).
- Added `tools/audit_procurement_risk.py` to keep procurement memo slack below 18000 bytes and prevent the new currentness refs from being dropped.
- Refactored `tools/check_archive.py` so archive-structure checks no longer re-run the deep audit subprocess suite after `make audit`; this removes a validation-timeout/waste pattern in the cloudtainer.

## Byte outcome

| Metric | rev0316 | rev0317 |
|---|---:|---:|
| `procurement_route_memo_total_bytes_after` | 19663 | 17623 |
| `procurement_route_memo_bytes_saved` | 959 | 2999 |

## Substantive correction

Defense procurement now has an explicit lifecycle-cost gate. That matters because cost-overrun routing is incomplete if it only watches development and acquisition cost while ignoring sustainment growth after deployment.
