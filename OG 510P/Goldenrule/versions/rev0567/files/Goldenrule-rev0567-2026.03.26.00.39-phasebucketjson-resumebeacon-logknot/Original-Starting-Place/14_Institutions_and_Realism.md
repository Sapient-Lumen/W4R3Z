# Institutions & Realism Modules

Golden Rule behavior in the wild is not only a property of individual policy;
it is also a property of **institutions** (reputation, exit, arbitration, norms).

This document defines modular institutions that WorldSpecs can toggle.

## 14.1 Partner choice (markets) module
Motivation: cooperation may be stabilized by the ability to switch partners; partner choice can create market-like dynamics.

World fields:
- `exit_allowed`: bool
- `exit_cost`: numeric
- `rematch_policy`: random | assortative | reputation_based
- `identity_persistence`: stable | pseudonymous | resettable

Key tests:
- “reputation laundering” when identity can reset,
- “too-sticky relationships” when exit is expensive,
- “market thinness”: few alternatives creates exploitation pressure.

## 14.2 Reputation & standing module
Reputation norms can penalize unjustified harm while permitting justified punishment.

World fields:
- `observer_model`: public | private | mixed
- `update_norm`: image_scoring | standing | custom
- `error_rates`: observation/gossip noise
- `audit_events`: probability of truth revelation

Key tests:
- cooperation under private/noisy info,
- justified defection without reputation collapse,
- misclassification cascades (“innocent becomes bad by rumor”).

## 14.3 Apology / repentance / clarification module
Apologies are strategic signals and can be faked; they often function by shifting beliefs about future behavior.

World fields:
- `signal_types`: apology, explain, commit, request_repair
- `signal_costs`: per type
- `signal_noise`: loss/misread
- `verification`: optional (audits, escrow)

Key tests:
- fake apology adversaries,
- guilt/contrition dynamics when apology has a cost,
- reintegration rules: how quickly reputation recovers after sustained cooperation.

## 14.4 Arbitration / mediation module
Third-party dispute resolution can prevent retaliation spirals.

World fields:
- `arbitration_available`: bool
- `arbitration_cost`: numeric
- `resolution_power`: weak (recommend) | strong (enforce)

Key tests:
- arbitration reduces mutual defection under high noise?
- moral hazard: do agents outsource trust and stop learning?

## 14.5 Jubilee / reset module (memory and forgiveness at scale)
Memory reset can be:
- time-based,
- repentance-triggered,
- institutionally imposed.

Key tests:
- jubilee prevents permanent caste systems,
- but can enable cyclical exploitation without enforcement.

## 14.6 Power snowball module (compounding advantage)
To model “centralization of power”:
- allow actions to affect a persistent `capital` state,
- capital amplifies future payoffs or enforcement power.

World fields:
- `capital_update_rules`
- `leverage_function`
- `redistribution_rules` (optional)

Key tests:
- prevent runaway domination without collapsing welfare,
- detect “soft extortion” via leverage accumulation.

## 14.7 Realism without losing epistemic control
Rules for adding realism:
- every added mechanism MUST come with axiom probes and failure traces,
- every mechanism MUST be switchable and versioned,
- begin with small-state models (FSM/belief) before adding neural policies.

## 14.8 Practical note: using off-the-shelf engines
Phase 1 (fast):
- implement IPD + modules in Rust core.

Phase 2 (broader games):
- integrate OpenSpiel (many games; fast core + Python bindings) and/or PettingZoo (standard MARL API).
- keep the same Scorecard + Probe framework to avoid definition drift.
