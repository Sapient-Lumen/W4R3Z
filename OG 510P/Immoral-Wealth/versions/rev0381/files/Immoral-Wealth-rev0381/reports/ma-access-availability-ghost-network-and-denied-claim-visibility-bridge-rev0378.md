---
revision_current: rev0378
generated_at: 2026-06-18T20:46:00Z
title: MA access availability, ghost-network, and denied-claim visibility bridge
status: not_certified_current
---

# MA access availability, ghost-network, and denied-claim visibility bridge — rev0378

Rev0378 moves the Medicare Advantage branch from denial/appeal/clinical-correctness alone to the missing access and visibility layer.

## Substantive finding

A Medicare Advantage row cannot pass if it proves that a service was covered, denied, appealed, or later restored while leaving three things invisible: whether an in-network provider was actually available, whether the provider directory listed inactive or non-serving providers, and whether MA encounter data can definitively identify payment denials.

## Concrete changes

- Added sources S609-S614.
- Added eight noncertifying locator-bound evidence records, including two new `contradicts` records.
- Added thirty-four mechanical association rows: scoreboard, memo, bridge, and evidence-debt links.
- Added a row contract for HSD/ACC network adequacy, MPF/API/provider-directory state, active provider and appointment availability, behavioral-health access, access complaints/failed ZIP or specialty markers, definitive denied-claim status, payment/service restoration, clinical correctness, and subgroup denominator.
- Refactored older MA bridge audit scripts so they resolve their latest active bridge/workbench instead of failing merely because the current revision advanced.

## Certification status

The case remains **not certified current**. The required next object is one current contract/service/provider/request/payment row that joins access availability, directory accuracy, definitive denied-claim visibility, clinical correctness, and remedy restoration.
