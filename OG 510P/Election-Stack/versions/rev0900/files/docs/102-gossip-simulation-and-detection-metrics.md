# Gossip simulation and detection metrics

**Track:** A (Deployable core)


## Why quantify
Gossip is not magic: a powerful attacker can delay or partition messages. You need quantified confidence:
- How likely is it that a split view is detected within X minutes?

## Key parameters
- N monitors/witnesses participating
- Peer graph degree (how many others each monitor gossips with)
- Gossip interval (seconds)
- Partition model (regional/ASN split, targeted censorship)
- Adversary strategy (delay, selective drop, equivocation)

## Core metrics
- **Detection probability** by time T: P(detect ≤ T)
- **Mean time to detection** (MTTD)
- **Worst-case undetected window** under stated assumptions
- **Bandwidth cost** per participant
- **False divergence rate** (benign mismatches)

## Minimal simulation approach
Start with Monte Carlo:
- model participants, message schedules, adversary drops
- record first time a monitor sees incompatible digests

## Formal verification (optional)
Use probabilistic model checking to validate simplified models and compare with simulations.

## Normative requirements
- **MUST** publish the parameter choices (N, interval, peer degree) as part of governance.
- **MUST** run quarterly simulations under updated threat assumptions.
- **MUST** treat a failed detection SLO as an incident requiring remediation.

## Artifacts
- `schemas/SimulationConfig.json`
- `schemas/SimulationReport.json`
- `tools/detection_simulator.py`