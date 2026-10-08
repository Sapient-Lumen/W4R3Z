# WorldSpec & WorldSuites (Possible Worlds)

## 3.1 Why “worlds”
A single tournament setting is a “spherical chicken in a vacuum.” The engine MUST evaluate across a **suite** of contexts.

A `WorldSpec` is a complete description of:
- game payoffs,
- information structure,
- noise/ambiguity,
- termination,
- interaction topology,
- optional institutions.

WorldSuites are curated sets of WorldSpecs.

## 3.2 WorldSpec schema (YAML/JSON)
Required fields:
- `id`: stable identifier
- `game`: reference to `GameSpec` (e.g., IPD)
- `payoff`: payoff matrix or distribution family
- `noise`: `NoiseModelSpec`
- `observation`: what each agent observes (actions, signals, partial)
- `termination`: `TerminationRuleSpec`
- `topology`: well-mixed, graph, schedule, or partner-choice market
- `institution`: optional enforcement/communication/reset/reputation
- `seed`: base RNG seed (world-level)

### NoiseModelSpec
Support:
1) **Implementation noise**: intended action flips with prob p.
2) **Observation noise**: observe opponent action incorrectly.
3) **Bursty noise**: Markov process with “storm” states.
4) **Asymmetric noise**: different agents have different p.
5) **Miscommunication**: signals lost/misread.

### TerminationRuleSpec
Support:
- fixed length N,
- geometric termination with continuation probability δ,
- stopping based on events (e.g., bankruptcy, collapse),
- “exit-triggered” termination (when an agent leaves a match).

## 3.3 Information and observation: intention is underdetermined
WorldSpec MUST distinguish:
- intended action (agent output),
- executed action (post-noise),
- observed action (what the other agent sees).

A world MAY include:
- **public observers** (third-party reputation),
- **private records** (each agent sees different evidence),
- **audit events** (rare reveals of true executed action).

This enables testing “duty/intention” under uncertainty.

## 3.4 Partner choice / exit as first-class topology
Many real interactions include the option to leave and choose new partners.

WorldSpec SHOULD support a `partner_choice` topology:
- agents can **stay**, **leave**, or **seek** new partners at checkpoints,
- matching may follow a market rule (random, preference-based, reputation-based),
- leaving may have costs (lost future benefit, reputation impact, switching cost).

This is a major “neglected environment” in many IPD-style tournaments.

## 3.5 Reputation & standing institutions
WorldSpec MAY include a `reputation` institution:
- each agent has a reputation record visible to others (public) or partially private,
- reputation updates follow a norm (image-scoring-like, standing-like, etc.),
- norms can treat “justified defection” differently from “unjustified defection.”

Include error/noise in reputational information.

## 3.6 Apology / clarification / commitment channels
WorldSpec MAY include a `signal_channel`:
- messages/signals have costs (optional) and noise (loss/misread),
- signals can encode apology, clarification, commitment, request-for-repair.

Signals are not assumed truthful. Worlds MUST allow “fake apology” opponents.

## 3.7 Jubilee / memory reset as a first-class mechanism
Model explicitly:
- periodic reset opportunities,
- conditional reset triggered by repentance signals,
- asymmetric reset (one side resets, other doesn’t),
- costs/benefits of reset.

Jubilee is treated as a world-level institution; strategies decide whether to participate.

## 3.8 Seeds and determinism
Each run MUST define:
- global seed,
- per-world seed,
- per-match seed,
- per-noise-stream seed.

All seeds MUST be recorded in artifacts.

## 3.9 WorldSuite types
- `core`: canonical baselines (low noise, standard payoffs)
- `noise_grace`: high noise, bursty noise, asymmetric observation
- `exploitation`: extortion-rich adversary schedule
- `repair`: structured miscoordination + recovery challenges
- `partner_choice`: exit + switching costs + market matching
- `reputation`: observer norms, private/public standing, audit events
- `restoration`: apology/repentance opportunities and reintegration rules
- `power_snowball`: multiparty / compounding advantage
- `institutional`: arbitration, memory reset, communication rules

## 3.10 Holdout worlds
MUST maintain a `holdout` suite never used in search/training, only for evaluation and promotion.

## 3.11 World generator (adversarial)
A `WorldFuzzer` SHOULD generate new worlds that maximize:
- candidate failure under scorecard constraints,
- overfitting signals (performance collapse outside training suite),
- brittleness to non-stationarity (e.g., noise storms, payoff shocks).
