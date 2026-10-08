# Forecast-to-update discipline

## Purpose

A forecast is not an empirical delta. A simulation, Fisher forecast, design sensitivity, mission science case, or benchmark target can be extremely valuable because it defines what future records should discriminate. It should not be scored as acquired route evidence.

## Four states

| State | Description | Archive effect |
|---|---|---|
| forecast-public | design, simulation, or sensitivity target is public | creates or sharpens a decision-experiment row |
| protocol-public | measurement protocol and controls are public | may improve acquisition readiness |
| record-public | acquired data / likelihood / benchmark artifact is public | may create empirical delta if controls survive |
| update-public | route field change is declared and linted | may alter score, blocker, or state within ceiling |

## Rule

Every future empirical claim should say which state it occupies. `DECISION-EXPERIMENT-LEDGER.json` owns forecast-to-record outcome classes. `EMPIRICAL-DELTA-LEDGER.json` owns actual route-field changes. `CANDIDATE-ROUTE-STATE-LEDGER.json` owns current route state.

## Current consequence

LISA, CMB-S4, constrained GIE, and other forecast-rich corridors are now represented as decision experiments unless or until a public record with controls exists. This keeps planning value visible without letting planning value become evidence value.
