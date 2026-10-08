# Structural audit — rev0375

## Highest-risk issue corrected

The cube had a plausible custodian-routing defect. Rev0374 split the 11:00 Columbiana results event from the 17:30 FEMA/IPAWS event, but the Ohio side still risked being treated as a subordinate branch of the FEMA Region 3 route. That is too brittle because Ohio is in FEMA Region 5 while Pennsylvania and West Virginia sit in FEMA Region 3.

Rev0375 adds a separate Region 5/Ohio/Columbiana acquisition lane and marks the older combined Ohio/Columbiana rev0374 packet as superseded for specificity purposes, not invalid.

## Audit/refactor result

- New route/custodian split table: `cube/bvps-fema-region-split-audit-rev0375.csv`.
- New official-findings watchlist: `cube/bvps-official-findings-watchlist-rev0375.csv`.
- New request specificity and proofcut crosswalk tables.
- New forward-work capsule and manifest.
- New validation report retention plan: historical validation reports are not deleted, but future work should operate from the current report plus archived history rather than scanning every root/cube mirror.

## Still open by design

The package does not contain the actual FEMA preliminary findings, the 11:00 Columbiana results packet, the ANS/IPAWS disposition, the EOF repair/retest packet, or any adjudicated response packet. All readiness conclusions remain blocked.
