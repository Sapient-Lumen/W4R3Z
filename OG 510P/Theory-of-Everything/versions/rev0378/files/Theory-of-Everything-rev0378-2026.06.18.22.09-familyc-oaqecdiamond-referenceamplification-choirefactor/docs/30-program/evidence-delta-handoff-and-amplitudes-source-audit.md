# rev0323 evidence-delta handoff and amplitudes/bootstrap source-role audit

Revision: `rev0323`  
Bundle: `Theory-of-Everything-rev0323-2026.06.04.10.46-amplitudes-evidence-delta-handoff-release-hotpath-audit.zip`

## Risk repaired

The riskiest seam was not a missing registry row. It was one-way pressure accounting. Several empirical-delta rows named evidence units, but the evidence units did not reciprocally expose those delta handles. That made source pressure visible from the delta side while remaining invisible from the evidence-unit side. At the same time, the S0 metadata/provenance wrapper still carried a bundle of route-local empirical-delta IDs, which smeared live route pressure through a generic wrapper.

rev0323 repairs that by:

- adding reciprocal evidence-unit delta handles for the currently declared delta→evidence handoffs,
- removing all empirical-delta IDs from `EU-0014-METADATA-PROVENANCE-WRAPPER`,
- adding an executable `evidence_delta_handoff_policy.py` audit,
- preserving the rule that fresh current amplitudes/bootstrap refs do not enter acquired evidence-unit `source_refs`, and
- keeping the amplitudes/bootstrap lane capped at current `S2`.

## Substantive physics posture

The amplitudes/bootstrap route is still useful as a constraint corridor, not as ontology closure. Current gravity S-matrix work strengthens pressure around crossing-symmetric dispersion relations, graviton-pole handling, subtractions, IR/loop stability, light-state assumptions, and kinematic-domain/numerical robustness. This is route-local pressure because it tests whether candidate inverse or UV-completion claims survive the gravity-specific denominator choices; it is not an acquired observed-sector record and it does not promote the route.

## Refactor outcome

The handoff audit is intentionally small but load-bearing. It forces every empirical delta that declares an evidence-unit handoff to be visible from the evidence unit, while also blocking the metadata wrapper from accumulating route-local pressure. This is control-plane cleanup in service of substance: fewer invisible seams, less source bleed, and a clearer boundary between evidence credit and current source pressure.

No route is promoted.
