# Meta 0446 — climate / utility continuity gap audit note

This meta note records the rev0745 repair lane.

- Substantive repair: notes 925 and 926 add the utility-shutoff / medical-baseline / climate-continuity packet.
- Test repair: `metadata/climate_utility_tests.json` adds ten account, medical, assistance, hazard, notice, backup-power, PSPS, reconnection, metrics, and handoff tests.
- Gap-ledger repair: `GAP-009` is now repaired and the stale duplicate health-benefit `GAP-008` next-candidate entry was removed.
- Refactor repair: common test-matrix front-door, H1, and manifest lint checks are registry-driven so new applied cases do not require repeated hardcoding.
