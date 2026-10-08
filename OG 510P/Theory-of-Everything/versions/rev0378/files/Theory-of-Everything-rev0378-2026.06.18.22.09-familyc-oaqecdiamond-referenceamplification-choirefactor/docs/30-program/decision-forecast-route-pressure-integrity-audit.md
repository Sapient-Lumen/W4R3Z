# Decision / forecast route-pressure integrity audit — rev0318

## Scope

This audit targets a substantive failure mode in the live cube: decision and forecast surfaces can look well controlled while remaining too weakly connected to route authority. A candidate lane should not survive as prose merely because its decision experiment or prospective forecast was cataloged somewhere else.

`rev0318` therefore makes route-facing decision pressure explicit in the authority graph. This is not a promotion mechanism. It is a rollback and dependency-propagation repair.

## Failure mode found

Before this pass, the authority graph already contained dependency edges that treated discriminator forecasts and decision experiments as controlled artifacts. That was useful but asymmetric: the rows were downstream-controlled, yet the graph did not require those rows to constrain route authority in return.

The practical risk was that future edits could remove, stale, or weaken a forecast or decision-experiment row while the route lane still appeared connected through other support families. That is exactly the archive's recurring vice: a control surface becomes a registry object instead of an executable pressure object.

## Route-facing repair

`rev0318` adds two dependency kinds to the witness vocabulary and source-replayed authority graph:

- `forecast-route-condition`
- `decision-experiment-route-condition`

The graph replay now adds:

- one forecast→route edge for every row in `DISCRIMINATOR-FORECAST-LEDGER.json`; and
- one decision-experiment→route edge for every route listed in `DECISION-EXPERIMENT-LEDGER.json`.

The generated audit `docs/30-program/decision-forecast-route-edge-audit.generated.md` checks that every such ledger row has a graph edge and that every candidate route has at least one route-facing forecast or decision row.

## Previously underpressured lanes repaired

The coverage audit found three route corridors with neither route-facing forecast nor route-facing decision-experiment pressure:

| Route | Repair | Ceiling preserved |
|---|---|---:|
| `R-OQ0057-FAMILYB-THERMO-ENTROPIC` | added `DF-0009-FAMILYB-THERMO-ENTROPIC-LOCAL-LAW-RECOVERY` | `S1` |
| `R-OQ0057-AMPLITUDES-BOOTSTRAP` | added `DF-0010-AMPLITUDES-BOOTSTRAP-CORRIDOR-INVERSION` | `S2` |
| `R-OQ0057-FRAME-QRF-RELATIONAL` | added `DF-0011-QRF-RELATIONAL-PUBLIC-WITNESS-PORTABILITY` | `S2` |

These rows are deliberately phrased as discriminator forecasts and public-record requirements, not as evidence of candidate identity. They make the lanes falsifiable or constraining in public-artifact terms while keeping the old ceilings.

## Source-replay and lint hardening

`tools/sync_generated_surfaces.py` now rebuilds the route-facing decision/forecast edges during authority-graph replay. `tools/lint_archive.py` rejects a package if:

- a forecast row lacks its forecast→route edge;
- a decision experiment route link lacks its decision-experiment→route edge;
- any route row lacks both forecast and decision pressure; or
- the generated decision/forecast edge audit reports drift or failures.

The graph `generated_from` list also includes `DISCRIMINATOR-FORECAST-LEDGER.json` and `DECISION-EXPERIMENT-LEDGER.json`, so the provenance surface now reflects the standalone ledgers that contribute route-pressure edges.

## Measured result

After replay in this revision:

- route rows: `13`
- forecast rows: `11`
- decision experiments: `6`
- route-facing forecast→route edges: `11`
- route-facing decision-experiment→route edges: `7`
- routes lacking both route-facing forecast and decision rows: `0`
- edge/audit failures: `0`

## Non-promotion rule

A route-facing forecast or decision-experiment row can cap, freeze, demote, or reopen route language. It cannot promote a route by itself. Promotion still requires the candidate route row, public-record custody, acquisition protocol, empirical delta, negative controls, observed-sector recovery, promotion gate, and claim-binding controls to allow the stronger wording.

## Followthrough speculation

The cube should continue converting pressure surfaces from passive inventories into source-replayed dependency objects. The useful direction is not more family registries; it is fewer narrative-only escape lanes. A compact future check could ask, for each candidate route, "what public artifact would change our mind, and where does that artifact currently touch the graph?"
