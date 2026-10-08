# Cube audit report — Rev0289

Record count: 153
Required axes: 23
Families: 13
Remedy profiles: 153
Case contracts: 82

## Audit/refactor focus

Rev0289 audits the route-to-case layer. Rev0288 could prove that route records and remedy profiles existed, but it did not prove that golden cases remained executable answer obligations. This pass adds a separate case-contract layer and checks that expected routes, flags, raw axes, remedy profiles, sources, and must-not answers stay synchronized.

## Repairs

- Added `family`-preserving case contracts for every golden case.
- Normalized invalid raw case-axis values (`state`, `enforcement`, `crypto_user`, `correction`) into cube vocabulary or added the missing vocabulary where it belonged (`refund_reissue`).
- Replaced generic expected flags with route-backed flags and preserved prior values as `legacy_expected_flags` where changed.
- Added a release-integrity route and calibration ladder for case-contract failures.
- Added `tools/audit_case_contracts.py` and wired it into the release path.
