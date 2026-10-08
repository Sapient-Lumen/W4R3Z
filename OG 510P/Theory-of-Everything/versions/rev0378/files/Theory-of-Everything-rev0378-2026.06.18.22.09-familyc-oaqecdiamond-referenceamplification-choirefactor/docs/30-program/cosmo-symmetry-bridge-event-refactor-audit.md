# rev0349 — Cosmology, symmetry, and bridge event refactor audit

## Purpose

This revision targets the next high-risk source-bearing seam after the route/matter normalization wave: cosmology/vacuum/thermal rows, Lorentz/CPT rows, horizon and QFT recovery rows, and decision/forecast/delta bridge rows that still carried old `revXXXX_*note` fields. The aim is substantive leakage control, not registry expansion.

## What changed

- Retired 107 old per-revision note fields from eleven ledgers: `VACUUM-ENERGY-LEDGER.json`, `THERMAL-HISTORY-LEDGER.json`, `CPT-DISCRETE-SYMMETRY-LEDGER.json`, `HORIZON-STRUCTURE-LEDGER.json`, `GAUGE-SYMMETRY-LEDGER.json`, `UNITARITY-CHECK-LEDGER.json`, `SCATTERING-OBSERVABLE-LEDGER.json`, `QUANTIZATION-MAP-LEDGER.json`, `EMPIRICAL-DELTA-LEDGER.json`, `DISCRIMINATOR-FORECAST-LEDGER.json`, and `DECISION-EXPERIMENT-LEDGER.json`.
- Added 112 typed `source_role_events` to preserve denominator-only, metadata-wrapper-forbidden, and route-local handoff semantics.
- Added 4 decision `authority_ceiling_events` for former `rev0327_nested_ceiling_note` fields so nested outcome ceilings are not disguised as source-role custody.
- Extended `FRONTIER-SOURCE-FRESHNESS-ASSERTIONS.json` with dark-sector and Lorentz/CPT snapshot receipts checked on `2026-06-09`.

## Semantic correction

Decision nested outcome ceilings are not source records. They now use `authority_ceiling_events` with `ceiling_event_type: nested_outcome_ceiling_normalization`, `outcome_promotion_ceilings`, and an explicit replacement of `rev0327_nested_ceiling_note`. This keeps spend authority separate from public-record source role.

## Freshness receipts added

Dark-sector receipts cover LZ light dark matter / solar CEvNS, XENONnT ionization-only light dark matter, KATRIN sterile-neutrino search, and ADMX 1.1--1.3 GHz axion search records. Lorentz/CPT receipts cover the 2026 SME Data Tables edition, hydrogen/antihydrogen or molecular-ion spectroscopy/theory rows, GRB photon-propagation Lorentz-invariance tests, and charm CPT bounds. These receipts are denominator or freshness custody only.

## Executable controls added

`tools/lint_archive.py` now requires typed event coverage when the migrated ref families appear on their normalized rows:

- dark-sector refs on vacuum or thermal rows require `retained_on_denominator_row_only` events;
- String/M and cosmology staging refs on vacuum/thermal rows require denominator events;
- Lorentz/CPT refs on CPT/discrete-symmetry rows require denominator events;
- horizon classical-GR and Family-B thermodynamic horizon refs require denominator events;
- QM/QFT precision refs on gauge, unitarity, scattering, and quantization rows require denominator events, while metadata wrappers must not carry them as direct `source_refs`;
- decision, forecast, and empirical-delta bridge refs require `route_local_handoff_only` events;
- decision `authority_ceiling_events` must be rev0349-normalized, replace `rev0327_nested_ceiling_note`, and carry valid S-level outcome ceilings.

## Non-promotion boundary

No route score, authority state, promotion ceiling, observed-sector obligation, empirical-delta handle, forecast handle, decision-experiment outcome, or acquired-support source row is promoted by this revision. The changes make existing denominator and handoff semantics executable.

## Remaining risk

After this pass, 79 old `revXXXX_*note` fields remain across smaller ledgers. The next useful cleanup should target only notes that carry source-role, protocol/acquisition, measurement, systematic, calibration, severity, credit, or authority semantics with an executable lint payoff. Do not migrate notes merely for neatness.
