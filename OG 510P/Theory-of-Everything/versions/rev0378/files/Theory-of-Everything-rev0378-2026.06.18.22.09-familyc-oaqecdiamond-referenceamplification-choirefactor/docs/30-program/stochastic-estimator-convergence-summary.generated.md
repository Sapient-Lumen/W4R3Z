# Stochastic sampling / estimator variance / convergence summary (generated)

Generated from `STOCHASTIC-SAMPLER-LEDGER.json`, `ESTIMATOR-VARIANCE-LEDGER.json`, and `CONVERGENCE-DIAGNOSTIC-LEDGER.json`. Do not edit directly; run `make index` after changing executable ledgers.

- Revision: `rev0378`
- Stochastic-sampler rows: `14`
- Estimator-variance rows: `14`
- Convergence-diagnostic rows: `14`
- Route rows: `13`
- S4/S5 routes: `0`

## Stochastic-sampler class counts

- `metadata/provenance nonphysical sampler wrapper`: `1`
- `route-local stochastic sampler / Monte Carlo denominator`: `13`

## Estimator-variance class counts

- `metadata/provenance nonphysical estimator wrapper`: `1`
- `route-local estimator bias/variance denominator`: `13`

## Convergence-diagnostic class counts

- `metadata/provenance nonphysical convergence wrapper`: `1`
- `route-local convergence / mixing / stopping diagnostic denominator`: `13`

## Route handle counts

| Route | Samplers | Estimators | Diagnostics |
|---|---:|---:|---:|
| `R-OQ0057-FAMILYC-EW-CODE` | `2` | `2` | `2` |
| `R-OQ0057-FAMILYC-LEARNED-INVERSE` | `2` | `2` | `2` |
| `R-OQ0057-FAMILYB-THERMO-ENTROPIC` | `2` | `2` | `2` |
| `R-OQ0057-STRINGM-ATLAS` | `2` | `2` | `2` |
| `R-OQ0057-ASYMPTOTIC-SAFETY` | `2` | `2` | `2` |
| `R-OQ0057-CAUSAL-SET` | `2` | `2` | `2` |
| `R-OQ0057-AMPLITUDES-BOOTSTRAP` | `2` | `2` | `2` |
| `R-OQ0057-LAB-GIE-BMV` | `2` | `2` | `2` |
| `R-OQ0057-GW-STRONGFIELD-GR` | `2` | `2` | `2` |
| `R-OQ0057-FRAME-QRF-RELATIONAL` | `2` | `2` | `2` |
| `R-OQ0057-LAB-GRAVITON-COUNTING` | `2` | `2` | `2` |
| `R-OQ0057-COSMO-DARK-ENERGY-BAO` | `2` | `2` | `2` |
| `R-OQ0057-PRIMORDIAL-TENSOR-BMODES` | `2` | `2` | `2` |

## Non-promotion rule

Stochastic-sampler, estimator-variance, and convergence-diagnostic rows make Monte Carlo, MCMC, nested-sampling, HMC, bootstrap, posterior/evidence, effective-sample-size, R-hat, convergence, and finite-sample precision language auditable. They can cap, freeze, demote, or roll back support, but they do not promote a route beyond route-state, likelihood/prior, measurement, selection/multiplicity, public-record, observed-sector, and residual-control ledgers.

