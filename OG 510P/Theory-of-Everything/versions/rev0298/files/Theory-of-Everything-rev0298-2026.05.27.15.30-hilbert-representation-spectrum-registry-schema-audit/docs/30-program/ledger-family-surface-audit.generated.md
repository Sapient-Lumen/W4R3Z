# Ledger-family surface/schema audit (generated)

Generated from `LEDGER-FAMILY-REGISTRY.json`. Do not edit directly; run `make index` after changing registered ledger families.

- Registry revision: `rev0298`
- Registered layer families: `38`

| Family | Ledgers present | Schemas present | Summary present | Route fields | Policy |
|---|---:|---:|---:|---:|---|
| `route-state-core` | `3/3` | `3/3` | `1` | `1` | `nonempty-route-fields` |
| `public-record-custody` | `3/3` | `3/3` | `1` | `2` | `nonempty-route-fields` |
| `defeat-rollback-severity` | `3/3` | `3/3` | `1` | `3` | `nonempty-route-fields` |
| `evidence-credit` | `3/3` | `3/3` | `1` | `3` | `nonempty-route-fields` |
| `contrast-update-prior` | `3/3` | `3/3` | `1` | `3` | `cluster-local-plus-wrapper` |
| `measurement-systematics-calibration` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `validity-transport-extrapolation` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `causal-intervention-counterfactual` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `selection-multiplicity-reporting` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `capacity-complexity-generalization` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `semantic-ontology-language` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `social-review-consensus` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `computational-numerical-software` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `formal-proof-assumption-coverage` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `idealization-approximation-limit` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `boundary-initial-sector` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `gauge-constraint-observable` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `regularization-renormalization-matching` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `composition-interface-global` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `unitarity-causality-stability` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `quantization-classical-semiclassical` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `information-entropy-no-go` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `symmetry-anomaly-conservation` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `topology-dimension-signature` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `measure-ensemble-typicality` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `subsystem-algebra-edge-center` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `matter-spectrum-coupling-mass` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `cosmological-background-vacuum-history` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `black-hole-horizon-thermodynamics-evaporation` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `singularity-censorship-hyperbolicity` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `stress-energy-backreaction-conditions` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `classical-gr-recovery` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `state-preparation-detector-decoherence` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `asymptotic-ir-scattering` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `discretization-finite-volume-continuum` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `correlation-operator-bootstrap` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `phase-order-universality` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |
| `hilbert-representation-spectrum` | `3/3` | `3/3` | `1` | `3` | `route-local-plus-wrapper` |

- Missing surface cells: `0`

## Audit rule

Every registered route-support family should expose its ledger files, schemas, generated summary, route fields, open-question gate, and cardinality policy in one place. This audit is intentionally shallow but broad: it catches registry drift before a family can lose a schema, generated mirror, or route-field coverage silently.
