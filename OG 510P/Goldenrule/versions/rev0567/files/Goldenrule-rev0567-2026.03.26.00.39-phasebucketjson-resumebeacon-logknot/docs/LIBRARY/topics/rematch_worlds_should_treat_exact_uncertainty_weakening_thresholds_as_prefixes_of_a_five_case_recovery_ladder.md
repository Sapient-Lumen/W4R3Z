# Rematch worlds should treat exact uncertainty weakening thresholds as prefixes of a five-case recovery ladder

## Claim
Once the archive already exposes the exact weakening breakpoints `{7, 11, 12, 17, 23}`, future inheritors should read them as a serial five-case recovery ladder, not as an arbitrary scalar frontier.

## Why
- the base saved-state resolver has exactly `5` optional weakening cases in the default matrix,
- each breakpoint restores exactly **one** previously deferred base weakening case,
- the recovery order is exact and prefix-closed: `18@0.84`, then `2@0.95`, then `13@0.84`, then `8@0.84`, then `2@0.84`,
- so the threshold menu is mechanically audit-able: picking a larger threshold is exactly choosing to recover one more concrete base weakening case.

## Current archive consequence
- the archive now carries a weakening-recovery ladder that names every withheld base weakening case and the smallest threshold that restores it,
- the six named weakening regimes can therefore be understood as recovered-case counts `{0,1,2,3,4,5}` as well as semantic policy bands,
- any future menu edit that adds, removes, merges, or reorders breakpoints is now visibly a change to the recovered case set rather than a harmless renaming.

## Operational rule
1. list which concrete deferred base weakening cases you are willing to restore,
2. choose the smallest threshold whose recovery ladder prefix contains exactly those cases,
3. treat any new breakpoint insertion or recovery-order swap as a policy change requiring explicit review,
4. do not describe the threshold as “more permissive” without also naming the newly recovered case.

## Pointers
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_recovery_ladder_snapshot_20260308.md`
- `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_recovery_ladder.py`
