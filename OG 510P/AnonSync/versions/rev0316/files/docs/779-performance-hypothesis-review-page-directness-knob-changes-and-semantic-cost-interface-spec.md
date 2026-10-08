# Performance hypothesis review page — directness, knob changes, and semantic cost interface spec

## Purpose

A benchmark result does not directly tell the operator which change to make.
It only narrows the hypothesis space.
Current Resilio docs still connect slow-speed causes, direct-path advice, LAN/VPN suggestions, power-user settings, and sidecar benchmarking across several articles.
AnonSync should turn that into one explicit review object.

## Core decision

Every performance intervention after a measurement run must be reviewed as a **hypothesis with upside, cost, and revert plan**, not as folklore.

The page must answer:

1. what the current dominant bottleneck hypothesis is
2. which interventions are actually supported by the evidence
3. what semantic, security, or operational cost each intervention carries
4. which intervention is the smallest honest next move
5. which tempting changes are specifically rejected

## Required sections

1. **Current best hypothesis**
2. **Supported intervention candidates**
3. **Cost / semantics review**
4. **Reversible test plan**
5. **Rejected folklore**

## 1) Current best hypothesis

State the strongest supported explanation, such as:

- `relay/directness is dominant`
- `raw network ceiling is low`
- `Sync workload overhead is dominant over network`
- `disk or security-filter contention is dominant`
- `source-peer asymmetry remains unresolved`
- `evidence still insufficient`

This section must also show the comparison basis that earned the hypothesis.

## 2) Supported intervention candidates

For each candidate change, show:

- change name
- target bottleneck family
- evidence basis
- expected upside band
- whether it is local, pairwise, share-scoped, or baseline-scoped

Examples might include:

- improve direct reachability / port mapping
- prefer same-LAN/VPN path
- set predefined hosts
- remove unintended rate limits
- review LAN encryption posture
- change disk-priority posture
- wait for a stronger source peer
- do nothing because the current ceiling is already honest for this workload

## 3) Cost / semantics review

Every candidate must publish its cost class, for example:

- security cost
- policy / topology cost
- operator labor
- restart or interruption cost
- broader blast radius
- reversibility quality

The page must never present `disable encryption`, `force LAN only`, or other topology/security-affecting changes as pure speed wins.

## 4) Reversible test plan

For candidates that proceed, show:

- exact hypothesis sentence
- scope of change
- success metric
- dwell / observation window
- revert trigger
- receipt that will prove the change was or was not worth keeping

## 5) Rejected folklore

Explicitly record tempting but unsupported moves, such as:

- changing several knobs at once
- promoting a benchmark result to a global claim without witness scope
- disabling protections without a measured upside case
- blaming the network when internal-task or disk evidence says otherwise

## Compact rendering obligations

Any compact suggestion card must still preserve:

- dominant hypothesis
- best next intervention
- major cost class
- reason stronger or riskier changes are withheld

## Anti-clone rule

Do not clone troubleshooting flows that leap from `slow` to `try these settings`.
AnonSync should only propose performance changes after an explicit hypothesis review that preserves evidence basis, side effects, reversibility, and the smallest honest next step.
