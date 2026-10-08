# Decision-experiment ledger

## Purpose

`DECISION-EXPERIMENT-LEDGER.json` is the executable bridge between route posture and possible public records. `CANDIDATE-ROUTE-STATE-LEDGER.json` says where a route stands now; `EMPIRICAL-DELTA-LEDGER.json` says what a new source or record changes; the decision-experiment ledger says what future or benchmarked outcomes would be allowed to change.

This prevents a common failure mode: a field result is announced, the archive calls it exciting, and the claim silently climbs from constraint to identification without recording the target quotient, negative controls, residual cap, or rollback handle.

## Required distinction

A decision experiment has three separable roles:

| Role | Meaning | Promotion risk |
|---|---|---|
| forecast | a design or sensitivity study says what could be measured | treating reach as acquired evidence |
| record | a public artifact is produced and can be challenged | treating record acquisition as candidate identity |
| route update | a denominator field, control, blocker, cap, or state actually changes | treating any improvement as global closure |

The ledger forces those roles apart.

## Current decision classes

- direct GIE / BMV-style entanglement and mediator tests;
- indirect GIE precursor and constrained-dynamics feasibility tests;
- strong-field gravitational-wave deviation / polarization tests;
- DESI-style late-time expansion and dark-energy dynamics records;
- CMB primordial-tensor / B-mode forecast-to-outcome records;
- Family-C reconstruction benchmarks with public replay and negative controls.

## Non-promotion rule

No decision-experiment outcome automatically promotes a route. A clean positive outcome can at most spend the `promotion_ceiling` named in the row, and it must still preserve the row's `residual_cap`, `public_record_carrier_ids`, and `acquisition_protocol_ids`. In the current archive, no decision experiment has an `S4` or `S5` automatic effect.

## Generated readout

`docs/30-program/decision-experiment-summary.generated.md` is produced by `make index`. It is descriptive only and cannot serve as route evidence.

## Carrier / protocol fields

Decision rows now name `public_record_carrier_ids` and `acquisition_protocol_ids`. This prevents a possible outcome from being counted as acquired evidence merely because a forecast, paper, or public portal exists.
