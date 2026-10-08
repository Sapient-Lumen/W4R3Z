# Cooperation Benchmark Card — Toy IPD fresh-partner transfer benchmark

- id: `cooperation-benchmark-card-example-toy-ipd-fresh-partner-transfer`
- result_kind: `comparative`
- schema_version: `1`
- notes: Use explicit not applicable strings rather than omission so future inheritors can distinguish absent fields from intentionally inapplicable ones.

## Comparison license

- **headline comparison licensed**: cold-start fresh-partner transfer within one scripted-bot counterpart class under no-chat full-information repeated IPD conditions
- **headline comparison not licensed without further justification**: generic more-cooperative-than-humans or more-cooperative-across-counterpart-classes claim

## Lane contract

- **counterpart class and mix rule**: single counterpart class: scripted repeated-game bots; no cross-class pooling
- **counterpart class x novelty axis coverage**: same counterpart class only; fresh partner identities sampled from one fixed scripted registry
- **cold start familiarized coadaptive status**: cold start only; no practice rounds; no adaptive warm-up
- **same partner continuation vs fresh partner transfer**: headline score uses fresh-partner transfer only; same-partner continuation not pooled into headline
- **role seat assignment and side switch policy**: symmetric simultaneous-move task; side-switch not applicable
- **information visibility and asymmetry regime**: full payoff and full action observability after each round; no hidden private facts
- **communication schedule and channel rights**: not applicable: no free-form or templated communication channel
- **interaction language translation localization and pooling rule**: not applicable: no natural-language interaction in the scored lane
- **interaction horizon stopping rule and termination knowledge**: fixed 50-round episodes; horizon known to both sides in advance
- **intervention rights delegation policy and final action authority**: fully autonomous evaluated agent; no human override, veto, or delegation split
- **process aware vs outcome only interpretation**: outcome-first score with trace retention for audit; no process-aware headline metric
- **human lane type proxy provenance and real human escalation status**: not applicable: no human or human-proxy partner lane
- **counterpart disclosure blinding and participant belief protocol**: not applicable: no real-human participants
- **participant pool provenance country mix eligibility and repeat exposure policy**: not applicable: no real-human participants
- **material payoff matrix stake mapping and comprehension protocol**: not applicable: no real-human participants

## Score construction

- **scored unit unit of analysis**: episode-level cooperation rate per evaluated-agent x partner pairing
- **pooling weighting censoring rule**: equal weight per partner; no censoring of completed episodes
- **primary estimand**: mean episode-level cooperation rate difference between evaluated agent and fixed baseline policy across the sampled fresh-partner set

## Metric governance

- **primary endpoint governing metric**: episode-level cooperation rate difference on the fresh-partner lane
- **auxiliary guardrail metrics**: joint payoff, exploitation rate against always-defect probes, and termination-free completion rate
- **composite normalization rule**: none; headline uses a single governing endpoint
- **multiplicity metric selection policy**: primary endpoint fixed before scoring; auxiliary metrics reported descriptively and do not replace the headline

## Uncertainty and dependence

- **dependence clustering structure**: rounds clustered within episode and episodes clustered within partner policy
- **inference or resampling unit**: partner-policy cluster bootstrap
- **primary uncertainty summary**: 95% bootstrap confidence interval on the primary estimand

## Variant selection

- **variant family**: single frozen agent wrapper for the scored run
- **selection tuning rule**: no prompt or wrapper retuning after benchmark outcomes
- **search budget**: one scored wrapper; no best-of-many selection
- **test touch policy**: benchmark suite untouched during wrapper selection

## Evaluated subject

- **evaluated subject provenance**: local policy snapshot toy-agent-v1
- **serving stack execution substrate**: repo-local Python execution only; no provider endpoint
- **evaluation window snapshot date**: snapshot dated 2026-03-19
- **update drift posture**: fully pinned local snapshot for this report

## Environment and knowledge

- **tool capability catalog and access policy**: game-engine actions only; no retrieval, web, filesystem writes, or external tools
- **external environment state snapshot posture**: fully frozen simulated environment
- **knowledge base retrieval corpus provenance and snapshot**: not applicable: no retrieval corpus or external KB
- **reset refresh mutability policy**: environment reset between episodes; no state carryover across partner pairings

## Execution budget

- **turn action tool call budget**: one action per round for 50 rounds; no external tool calls
- **context history retention policy**: full within-episode history retained; no cross-episode memory
- **token compute latency budget**: not applicable: structured policy actions rather than language generation
- **limit hit handling truncation stop rule**: episode ends at fixed horizon; no timeout-based truncation

## Scenario sampling

- **scenario world template family**: single fixed IPD world specification
- **sampling randomization rule**: fresh partner policies drawn without replacement from one fixed registry slice
- **seed set reroll stopping policy**: single published seed bundle; no reroll-until-good policy
- **release posture holdout exposure**: fully public fixed suite

## Failure handling

- **raw attempt denominator**: all launched evaluated-agent x partner episodes
- **scored denominator**: identical to raw denominator because invalid episodes count as failures
- **failure invalid output taxonomy**: invalid action token, engine exception, or missing action within deadline
- **retry repair rule and budget**: no retry and no manual repair for scored episodes
- **exclusion scoring rule**: failed episodes remain in denominator and receive zero cooperation credit

## Adjudication

- **judge rater provenance**: not applicable: no human or LLM judge in the primary endpoint
- **rubric scoring protocol**: deterministic rules-based scorer from the environment logs
- **adjudication debias rule**: not applicable: no free-text judged comparison
- **calibration escalation policy**: not applicable: no judge escalation path
