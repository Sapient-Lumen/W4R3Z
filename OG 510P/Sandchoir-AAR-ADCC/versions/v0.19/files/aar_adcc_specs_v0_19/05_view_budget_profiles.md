# 05 — View Budget Profiles (v0.19)

Budgets are enforced by AAR and tuned by the Bandwidth Adapter.

## Default section caps (items)
- MANDATORY: 6
- HOT: 6
- DELTA: 8
- ROLE: 6
- DISCOVERY: 1
- RANDOM: 1
Total typical: 20–28 items max.

## Emergency shrink (bandwidth collapse)
- MANDATORY: 4
- HOT: 4
- DELTA: 4
- ROLE: 2
- DISCOVERY: 0
- RANDOM: 0

## Role presets
- Integrator: +2 HOT, +2 DELTA
- Skeptic: +2 HOT (claims/CE), +1 DISCOVERY
- Tester: +2 DELTA (evidence/tests), +1 HOT (failures)
- Compiler: +2 ROLE (intent/clarify), -2 HOT

## Zoom policy (P2)
Agents may request `ZOOM=<ID>` once per slice.
AAR returns:
- compact item + immediate neighbors (refs) within a small cap.

## Exploration defaults
- Normal: DISCOVERY=1, RANDOM=0
- Consensus collapse: DISCOVERY=1, RANDOM=1
- Bandwidth collapse: DISCOVERY=0, RANDOM=0
