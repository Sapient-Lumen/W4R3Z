# Frontier-source freshness audit (generated)

Generated from `FRONTIER-SOURCE-FRESHNESS-ASSERTIONS.json` and the named executable ledgers. Do not edit directly; run `make index` after changing frontier source assertions or source-carrying rows.

- Assertion revision: `rev0378`
- Assertion schema version: `1.8`
- Freshness assertions: `33`
- Required source-carrying rows checked: `556`
- Typed source-role event rows replayed: `556`
- Typed source-role event replay failures: `0`
- Watchlist zero-placement refs checked: `2`
- Watchlist route-bearing placements: `0`
- Freshness failures: `0`

## Source-role counts

- `acquired_support`: `3`
- `denominator_pressure`: `26`
- `forecast_runway`: `3`
- `operational_status`: `1`

## Replay modes

| Mode | Assertions |
|---|---:|
| `one_role_typed_replay` | `29` |
| `row_refs_only` | `0` |
| `row_scoped_mixed_role_replay` | `3` |
| `zero_placement_watchlist` | `1` |

## Assertion summary

| Assertion | Replay mode | Source role | Checked at | Public status | Frontier source | Freshness state | Receipts | Required rows | Event rows | Watchlist refs | Watchlist placements | Failed rows |
|---|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|
| `FSF-0001-GWTC5-CORE-CUSTODY` | `one-role-typed` | `acquired_support` | `2026-06-04` | Public release object is used as custody/replay/constraint input as of the assertion date; support spending remains capped by the owning route rows. | GWTC-5.0 | `current-as-of-2026-06-04-web-audit` | `0` | `12` | `12` | `0` | `0` | `0` |
| `FSF-0002-DESI-DR2-CORE-CUSTODY` | `one-role-typed` | `acquired_support` | `2026-06-04` | Public release object is used as custody/replay/constraint input as of the assertion date; support spending remains capped by the owning route rows. | DESI DR2 cosmology chains and data products | `current-as-of-2026-06-04-web-audit` | `0` | `13` | `13` | `0` | `0` | `0` |
| `FSF-0003-EUCLID-CERN-WATCHLIST-BOUNDARY` | `zero-placement-watchlist` | `forecast_runway` | `2026-06-10` | Watchlist-only group: Euclid Q1 and CERN accelerator schedule are public timing/custody sources; neither is a route-bearing evidence row in this revision. | Euclid Q1 and CERN accelerator schedule | `current-as-of-2026-06-10-web-audit` | `2` | `0` | `0` | `2` | `0` | `0` |
| `FSF-0004-CMBS4-SHUTDOWN-CLOSEOUT-CUSTODY` | `one-role-typed` | `operational_status` | `2026-06-04` | Public source object is mission/project/status or closeout custody as of the assertion date. | CMB-S4 shutdown / closeout archive custody | `current-as-of-2026-06-04-web-audit` | `0` | `11` | `11` | `0` | `0` | `0` |
| `FSF-0005-LISA-CONSTRUCTION-PROTOTYPE-RUNWAY` | `one-role-typed` | `forecast_runway` | `2026-06-04` | Public source object is schedule, release-timing, or future-instrument runway custody as of the assertion date. | LISA adoption / construction / NASA prototype-hardware runway | `current-as-of-2026-06-04-web-audit` | `0` | `4` | `4` | `0` | `0` | `0` |
| `FSF-0007-SPT3G-BMODE-ACQUIRED-PUBLIC-PRESSURE` | `one-role-typed` | `acquired_support` | `2026-06-04` | Public release object is used as custody/replay/constraint input as of the assertion date; support spending remains capped by the owning route rows. | SPT-3G two-year B-mode bandpowers and likelihood products | `current-as-of-2026-06-04-web-audit` | `0` | `11` | `11` | `0` | `0` | `0` |
| `FSF-0008-GIE-BMV-INFERENCE-SPLIT` | `one-role-typed` | `denominator_pressure` | `2026-06-04` | Public source object is used as burden-setting constraint pressure as of the assertion date; it is not candidate-native evidence. | GIE/BMV realization and inference-split literature | `current-as-of-2026-06-04-web-audit` | `0` | `6` | `6` | `0` | `0` | `0` |
| `FSF-0009-FAMILYC-SUBREGION-STATE-PORTABILITY` | `one-role-typed` | `denominator_pressure` | `2026-06-04` | Public source object is used as burden-setting constraint pressure as of the assertion date; it is not candidate-native evidence. | FamilyC gravitating-region/subregion-state theory-pressure references | `current-as-of-2026-06-04-web-audit` | `0` | `3` | `3` | `0` | `0` | `0` |
| `FSF-0010-GRAVITON-COUNTING-SOURCE-PARTITION` | `one-role-typed` | `denominator_pressure` | `2026-06-04` | Public source object is used as burden-setting constraint pressure as of the assertion date; it is not candidate-native evidence. | single-graviton and graviton-counting route-local source partition | `current-as-of-2026-06-04-web-audit` | `0` | `11` | `11` | `0` | `0` | `0` |
| `FSF-0011-DESI-DR2-EXTENDED-DE-COMBINATION-PRESSURE` | `one-role-typed` | `denominator_pressure` | `2026-06-04` | Public source object is used as burden-setting constraint pressure as of the assertion date; it is not candidate-native evidence. | DESI DR2 extended dark-energy combination pressure | `current-as-of-2026-06-04-web-audit` | `0` | `6` | `6` | `0` | `0` | `0` |
| `FSF-0012-AMPLITUDES-GRAVITY-IR-POSITIVITY-PRESSURE` | `one-role-typed` | `denominator_pressure` | `2026-06-04` | Public source object is used as burden-setting constraint pressure as of the assertion date; it is not candidate-native evidence. | amplitudes/bootstrap gravitational EFT graviton-pole, IR-loop, and positivity pressure | `current-as-of-2026-06-04-web-audit` | `0` | `8` | `8` | `0` | `0` | `0` |
| `FSF-0013-ASYMPTOTIC-SAFETY-LORENTZIAN-OBSERVABLE-PRESSURE` | `one-role-typed` | `denominator_pressure` | `2026-06-04` | Public source object is used as burden-setting constraint pressure as of the assertion date; it is not candidate-native evidence. | asymptotic-safety Lorentzian-observable, form-factor, GLOB, and swampland compatibility pressure | `current-as-of-2026-06-04-web-audit` | `0` | `16` | `16` | `0` | `0` | `0` |
| `FSF-0014-FAMILYC-LEARNED-INVERSE-OOD-PRESSURE` | `one-role-typed` | `denominator_pressure` | `2026-06-04` | Public source object is used as burden-setting constraint pressure as of the assertion date; it is not candidate-native evidence. | learned-inverse holographic reconstruction, PINN/SciML failure-mode, and uncertainty-calibration pressure | `current-as-of-2026-06-04-web-audit` | `0` | `14` | `14` | `0` | `0` | `0` |
| `FSF-0015-FAMILYB-THERMO-RELATIVE-ENTROPY-SCOPE` | `one-role-typed` | `denominator_pressure` | `2026-06-04` | Public source object is used as burden-setting constraint pressure as of the assertion date; it is not candidate-native evidence. | FamilyB relative-entropy, semiclassical spacetime thermodynamics, non-Riemannian, non-extensive horizon-entropy, and nonequilibrium entropy-production pressure | `current-as-of-2026-06-04-web-audit` | `0` | `7` | `7` | `0` | `0` | `0` |
| `FSF-0016-CAUSAL-SET-CONTINUUM-HORIZON-QSG-PRESSURE` | `one-role-typed` | `denominator_pressure` | `2026-06-04` | Public source object is used as burden-setting constraint pressure as of the assertion date; it is not candidate-native evidence. | causal-set QSG computability, continuum-emergence, interacting-QFT correlator, horizon-molecule entropy, and discrete-horizon diagnostic pressure | `current-as-of-2026-06-04-web-audit` | `0` | `12` | `12` | `0` | `0` | `0` |
| `FSF-0017-STRINGM-OBSERVED-SECTOR-ATLAS-PRESSURE` | `one-role-typed` | `denominator_pressure` | `2026-06-04` | Public source object is used as burden-setting constraint pressure as of the assertion date; it is not candidate-native evidence. | String/M finite-region flux-vacuum atlas, Landau-Ginzburg stabilization, and DESI/de Sitter swampland pressure | `current-as-of-2026-06-04-web-audit` | `0` | `19` | `19` | `0` | `0` | `0` |
| `FSF-0018-GW-GR-TEST-SEMANTICS-S2-BOUNDARY` | `one-role-typed` | `denominator_pressure` | `2026-06-04` | Public source object is used as burden-setting constraint pressure as of the assertion date; it is not candidate-native evidence. | GW public GR-test and black-hole-spectroscopy semantics | `current-as-of-2026-06-04-web-audit` | `0` | `10` | `10` | `0` | `0` | `0` |
| `FSF-0019-QRF-FRAME-TRANSPORT-LARGE-GAUGE-PRESSURE` | `one-role-typed` | `denominator_pressure` | `2026-06-04` | Public source object is used as burden-setting constraint pressure as of the assertion date; it is not candidate-native evidence. | QRF frame-transport, crossed-product observer-dependence, and large-gauge/boundary-corner semantics | `current-as-of-2026-06-04-web-audit` | `0` | `11` | `11` | `0` | `0` | `0` |
| `FSF-0020-FAMILYB-NONEQUILIBRIUM-HORIZON-CALIBRATION` | `one-role-typed` | `denominator_pressure` | `2026-06-04` | Public source object is used as burden-setting constraint pressure as of the assertion date; it is not candidate-native evidence. | FamilyB nonequilibrium entropy-production and non-extensive/topological horizon-entropy calibration pressure | `current-as-of-2026-06-04-web-audit` | `0` | `10` | `10` | `0` | `0` | `0` |
| `FSF-0021-CMB-BMODE-SUCCESSOR-CAUSAL-SOURCE-PRESSURE` | `one-role-typed` | `forecast_runway` | `2026-06-05` | Public source object is schedule, release-timing, or future-instrument runway custody as of the assertion date. | Primordial B-mode successor forecasts, LiteBIRD mission runway, and causal-source B-mode ambiguity pressure | `current-as-of-2026-06-05-web-audit` | `0` | `8` | `8` | `0` | `0` | `0` |
| `FSF-0022-COSMO-DESI-LYA-EUCLID-SOURCE-STAGING` | `row-scoped-mixed-role` | `denominator_pressure` | `2026-06-10` | Mixed public-record group: DESI DR2 cosmology chains/posteriors are public custody; Lyman-alpha and interpretation-caveat records are denominator pressure; Euclid release timing is future-runway custody. | DESI DR2 public chains, Lyman-alpha / interpretation pressure, String/M DESI-portal caveat, and Euclid release-timeline runway | `current-as-of-2026-06-10-web-audit` | `5` | `11` | `19` | `0` | `0` | `0` |
| `FSF-0023-FAMILYC-FINITE-N-QEC-ISLAND-SOURCE-ROLE` | `one-role-typed` | `denominator_pressure` | `2026-06-05` | Public source object is used as burden-setting constraint pressure as of the assertion date; it is not candidate-native evidence. | FamilyC finite-N/interior-QEC, modular-Krylov island-area, and massless-island source-role pressure | `current-as-of-2026-06-05-web-audit` | `0` | `11` | `11` | `0` | `0` | `0` |
| `FSF-0024-LAB-GIE-PROTOCOL-NOISE-CLASSICAL-SPLIT` | `one-role-typed` | `denominator_pressure` | `2026-06-05` | Public source object is used as burden-setting constraint pressure as of the assertion date; it is not candidate-native evidence. | Lab GIE/BMV constrained-dynamics, shielding/stability, thermal-noise, and classical/nonlocal inference-split pressure | `current-as-of-2026-06-05-web-audit` | `0` | `13` | `13` | `0` | `0` | `0` |
| `FSF-0025-OBSERVED-SECTOR-MATTER-FRONTIER-SOURCE-ROLE` | `one-role-typed` | `denominator_pressure` | `2026-06-09` | Public source objects were rechecked for rev0348 and remain burden-setting denominator pressure, not candidate-native evidence. | Observed-sector matter, Higgs/electroweak coupling, muon precision, and neutrino-mass public constraint custody | `current-as-of-2026-06-09-web-audit` | `4` | `43` | `43` | `0` | `0` | `0` |
| `FSF-0026-CLASSICAL-GR-OBSERVED-SECTOR-SOURCE-ROLE` | `one-role-typed` | `denominator_pressure` | `2026-06-09` | Classical-GR observed-sector public records were snapshotted in this rev0347 pass and remain denominator pressure only across horizon-scale imaging, S2/Galactic-center orbital tests, and cosmological full-shape/growth constraints. | Classical-GR observed-sector public constraint custody across horizon-scale imaging, Galactic-center stellar orbits, and large-scale growth/full-shape gravity | `current-as-of-2026-06-09-web-audit` | `4` | `32` | `32` | `0` | `0` | `0` |
| `FSF-0027-DARK-SECTOR-CONSTRAINT-SOURCE-ROLE` | `one-role-typed` | `denominator_pressure` | `2026-06-09` | Public source object is used as burden-setting constraint pressure as of the assertion date; it is not candidate-native evidence. | Direct dark-matter, light-DM, sterile-neutrino, and axion-search constraint custody | `current-as-of-2026-06-09-web-audit` | `4` | `42` | `42` | `0` | `0` | `0` |
| `FSF-0028-QM-QFT-GAUGE-OBSERVED-SECTOR-SOURCE-ROLE` | `one-role-typed` | `denominator_pressure` | `2026-06-09` | QM/QFT/gauge public denominator records were snapshotted in this rev0347 pass and remain unit/constants/QED precision pressure only. | QM/QFT/gauge observed-sector constants and precision lepton magnetic-moment custody | `current-as-of-2026-06-09-web-audit` | `2` | `46` | `46` | `0` | `0` | `0` |
| `FSF-0029-QCD-HADRONIC-OBSERVED-SECTOR-SOURCE-ROLE` | `one-role-typed` | `denominator_pressure` | `2026-06-09` | Public source objects were rechecked for rev0348 and remain burden-setting denominator pressure, not candidate-native evidence. | QCD/hadronic observed-sector denominator custody: lattice-QCD averages, alpha_s, jet/PDF running, quark masses, and nonperturbative-to-perturbative matching | `current-as-of-2026-06-09-web-audit` | `3` | `47` | `47` | `0` | `0` | `0` |
| `FSF-0030-LORENTZ-CPT-SME-SOURCE-ROLE` | `one-role-typed` | `denominator_pressure` | `2026-06-09` | Public source object is used as burden-setting constraint pressure as of the assertion date; it is not candidate-native evidence. | Lorentz/CPT/SME current public constraint corpus | `current-as-of-2026-06-09-web-audit` | `5` | `46` | `46` | `0` | `0` | `0` |
| `FSF-0031-ELECTROWEAK-FLAVOR-NEUTRINO-SOURCE-ROLE` | `one-role-typed` | `denominator_pressure` | `2026-06-09` | Public source objects were rechecked for rev0348 and remain burden-setting denominator pressure, not candidate-native evidence. | Electroweak precision, flavor/CKM, and neutrino observed-sector public constraint custody | `current-as-of-2026-06-09-web-audit` | `6` | `47` | `47` | `0` | `0` | `0` |
| `FSF-0032-EQUIVALENCE-FIFTH-FORCE-WEAKFIELD-SOURCE-ROLE` | `one-role-typed` | `denominator_pressure` | `2026-06-09` | Equivalence-principle, fifth-force, clock/redshift, and weak-field public records were snapshotted in the rev0346/rev0347 typed-source-role passes and remain denominator pressure or operational status only. | Equivalence-principle, inverse-square/fifth-force, quantum-free-fall, clock/redshift, and torsion-balance public constraint custody | `current-as-of-2026-06-09-web-audit` | `5` | `17` | `17` | `0` | `0` | `0` |
| `FSF-0033-ACT-DR6-CMB-COSMOLOGY-DENOMINATOR` | `row-scoped-mixed-role` | `denominator_pressure` | `2026-06-13` | public ACT DR6 data/paper/derived-product locators identified; rev0363 retains compact inventory-control JSON for REF-0729 ACT DR6.02 public products and REF-0731 ACT DR6 lensing-likelihood identity, while REF-0730 remains paper/likelihood locator-only and no bulky payload checksums are vendored | ACT DR6 public CMB maps, spectra, likelihoods, chains, and derived/lensing products | `current-as-of-2026-06-13-inventory-control-audit` | `3` | `5` | `5` | `0` | `0` | `0` |
| `FSF-0034-PTA-NANOGRAV-GWB-DENOMINATOR` | `row-scoped-mixed-role` | `denominator_pressure` | `2026-06-13` | public NANOGrav official summary and primary paper identified; public-data row now pins exact Zenodo v2.1.0 timing-data identity and records upstream md5 inventory for related public analysis products while bulky payloads remain external | NANOGrav 15-year PTA nanohertz stochastic gravitational-wave-background public evidence and data products | `current-as-of-2026-06-13-web-audit` | `3` | `4` | `4` | `0` | `0` | `0` |

## Failure details

None.

## Typed event replay rule

For assertions that declare `typed_event_replay_policy` or row-scoped `typed_event_replay_policies`, the evaluator now checks not only row-level `source_refs`, but also the covering `source_role_events` disposition and credit cap. Row-scoped policies are used when one freshness assertion mixes acquired support custody, denominator pressure, and future runway timing. This prevents a fresh public source from surviving as a bare row ref after its custody, denominator, handoff, exclusion, runway, or metadata-wrapper boundary event is removed.

## Source-role receipt rule

Every frontier-source assertion now carries `source_role`, `checked_at`, `public_status`, and `no_promotion_disposition`. Optional per-source snapshot receipts are validated when present. The allowed roles are `acquired_support`, `denominator_pressure`, `forecast_runway`, `operational_status`, and `metadata_wrapper`.
Assertions that declare `watchlist_zero_route_placement_policy` also replay against the source-custody isolation evaluator and must have zero route-bearing placements for the named watchlist refs.

## Compression note

The evaluator still checks every required source-carrying row. The generated artifact intentionally retains assertion summaries and failure details rather than a row-by-row PASS table, keeping the control plane smaller while preserving failure visibility.

## Non-promotion rule

A current public release ref can repair custody, replay, calibration, systematics, and likelihood freshness, but it cannot promote a route by freshness alone.

## Why this exists

Volatile public sources are high-value and high-risk: a current catalog, likelihood chain, or schedule can silently supersede the object named in an older row. This audit is intentionally narrow: it checks only the rows that currently spend public frontier-source language, and it treats watchlist-only sources as custody/timing pressure rather than evidence.
