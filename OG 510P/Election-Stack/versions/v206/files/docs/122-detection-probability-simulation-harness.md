# Detection probability simulation harness

**Track:** A (Deployable core)


## Purpose
Quantify how likely you are to detect:
- split-view evidence distribution
- selective unreachability

…given your:
- probe cohort policy
- gossip topology
- measurement cadence

## Approach
Two layers:

### A. Monte Carlo simulation (baseline)
- model cohorts + censorship partitions
- simulate probe outcomes and gossip propagation
- compute detection metrics

### B. Model checking (optional)
- validate simplified models with probabilistic model checking

## Inputs
- `SimulationConfig` (network model, censoring model, cadence)
- `ProbeCohortPlan`

## Outputs
- `SimulationReport` with P(detect ≤ T), MTTD, and sensitivity analyses

## Normative requirements
- **MUST** run simulations ahead of each major election.
- **MUST** publish a summary of detection guarantees (assumptions explicit).

## Artifacts
- `schemas/SimulationConfig.json`
- `schemas/SimulationReport.json`
- `tools/detection_simulator.py`