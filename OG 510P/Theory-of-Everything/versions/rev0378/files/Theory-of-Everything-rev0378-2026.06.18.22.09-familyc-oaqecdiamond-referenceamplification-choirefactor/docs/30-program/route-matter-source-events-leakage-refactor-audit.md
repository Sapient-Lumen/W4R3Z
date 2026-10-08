# rev0348 route-head and matter-sector source-role event refactor audit

## Why this was the risky next move

`rev0347` normalized evidence-unit exclusions and selected observed-sector rows, but the route head and matter/precision ledgers still carried large clusters of per-revision source-role note fields. That was risky because those rows are close to the human narrative path: stale or duplicated `revXXXX_*note` keys can look like live support, even when their intended meaning is denominator pressure, metadata exclusion, or route-local handoff only.

This pass keeps the scientific state unchanged and moves the remaining high-count source-role burden semantics into executable `source_role_events`.

## Refactor summary

The pass retires the following ad hoc note fields from the selected source-bearing ledgers:

| Surface | Row-level `revXXXX_*note` fields retired | Top-level `revXXXX_*note` fields retired | Typed events added |
| --- | ---: | ---: | ---: |
| `CANDIDATE-ROUTE-STATE-LEDGER.json` | 59 | 0 | 85 row events |
| `PARTICLE-SPECTRUM-LEDGER.json` | 29 | 1 | 43 row events + 1 top-level event |
| `MASS-HIERARCHY-LEDGER.json` | 28 | 1 | 42 row events + 1 top-level event |
| `INTERACTION-COUPLING-LEDGER.json` | 28 | 1 | 42 row events + 1 top-level event |
| `COSMOLOGICAL-BACKGROUND-LEDGER.json` | 22 | 0 | 22 row events |
| `LORENTZ-COVARIANCE-LEDGER.json` | 18 | 0 | 18 row events |
| `MICROCAUSALITY-LOCALITY-LEDGER.json` | 18 | 0 | 18 row events |
| **Total** | **202** | **3** | **270 row events + 3 top-level events** |

## Source-role semantics preserved

The new events use the existing small role vocabulary rather than creating another route registry:

- `denominator_pressure` for public records retained only as burden-setting constraints.
- `metadata_wrapper` for explicit wrapper exclusions.
- `route_local_handoff_only` as the source-ref disposition for route-head mirrors that must not become acquired route support.
- `retained_on_denominator_row_only` for matter, QCD, electroweak/flavor/neutrino, cosmology, Lorentz/CPT, and QM/QFT public records that stay on denominator rows.
- `forbidden_on_metadata_wrapper` for public refs that may be named only as exclusions on metadata wrapper rows.

No route score, promotion ceiling, authority state, observed-sector obligation, empirical-delta handle, forecast handle, or decision-experiment handle is promoted by this migration.

## Executable hardening

`tools/lint_archive.py` now treats the normalized route-head and matter/precision ledgers as event-normalized surfaces. It rejects:

- regrowth of row-level or top-level `revXXXX_*note` keys in the normalized ledgers;
- malformed, duplicate, or unknown-role `source_role_events`;
- bibliography refs in events that are not known `REF-*` handles;
- missing route-local handoff events for route rows carrying observed-sector empirical-delta pressure;
- route-local events whose disposition is not `route_local_handoff_only`;
- matter-sector denominator refs missing from non-wrapper source rows;
- matter/QCD/electroweak refs appearing directly in metadata-wrapper `source_refs`;
- missing forbidden-wrapper events for matter-sector metadata wrappers;
- missing retained-denominator event coverage for cosmology, Lorentz/CPT, QM/QFT, and microcausality rows.

The route/matter policy scripts were also corrected so typed route-local handoff events are not falsely reported as source leakage. That was a real policy bug: once route-head events named the public refs explicitly, older whole-file scanners interpreted the event payload as misplaced source custody. The repaired policy keeps row-level source leakage prohibited while allowing typed handoff events that are separately linted.

## Freshness receipts added

`FRONTIER-SOURCE-FRESHNESS-ASSERTIONS.json` now carries per-source snapshot receipts for the matter, QCD, and electroweak/flavor/neutrino public-record groups. These receipts record `checked_at`, `public_status`, `source_role`, and `no_promotion_disposition` for:

- PDG / Muon g-2 / KATRIN / CMS-Higgs matter-sector custody;
- FLAG / precision QCD coupling / CMS strong-coupling-running custody;
- CMS W mass / CKMfitter / HFLAV / NuFIT / LHCb Z mass / JUNO neutrino-oscillation custody.

The receipts are deliberately non-promotional. They make freshness explicit without converting current public records into candidate-native matter derivations, QCD derivations, electroweak/flavor derivations, neutrino-mass mechanisms, or route support.

## Remaining risk

The highest-count route and matter clusters are now normalized, but several lower-count ledgers still contain old note keys. The next useful cleanup should focus on generated-audit compression and the remaining event migrations in vacuum-energy, thermal-history, decision-experiment, CPT/discrete-symmetry, empirical-delta, discriminator-forecast, horizon-structure, gauge-symmetry, unitarity, scattering, and quantization surfaces. Those should be migrated only where they remove real leakage or reading risk, not merely because a registry can be made.
