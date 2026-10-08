# Computational reproducibility and artifact replay discipline

`OQ-0071` controls code, workflow, container, benchmark, simulation, solver, proof-assistant, and generated-artifact language.

A route may use computational support language only when `COMPUTATIONAL-REPRODUCIBILITY-LEDGER.json` declares the support-bearing artifact, execution environment, dependency lock, randomness/seed rule, replay command, independent reproduction expectation, maximum authority effect, and rollback handles.

## Stop rule

Runnable code, a container image, a notebook, a workflow file, a proof replay, or a generated summary is not itself candidate evidence. It becomes spendable only as a route-local evidence object under the route state, public-record carrier, acquisition protocol, evidence-credit, contrast/update, measurement/systematics, validity/transport, causal/counterfactual, selection/multiplicity, capacity/generalization, semantic/ontology, social-authority, and rollback ledgers.

## Required denominator fields

A computational row must answer all of these before the archive can say that a computation is replayable:

| Field | Meaning | Failure mode blocked |
|---|---|---|
| `artifact_object` | What exact script, proof, model, notebook, workflow, solver, container, or generated file carries the result? | treating surrounding prose as the replay object |
| `input_record` | Which public carrier, dataset, proof source, benchmark, catalog, or simulator distribution is consumed? | changing inputs while claiming same result |
| `execution_environment` | What platform, runtime, dependency, hardware, container, service, or build context was used? | environment drift |
| `replay_command` | What command or procedure should reproduce the artifact-local output? | runnable-in-principle laundering |
| `randomness_rule` | Which seeds, stochastic procedures, nondeterministic schedulers, or sampling choices are fixed or varied? | seed and scheduler cherry-picking |
| `expected_output_equivalence` | What counts as same: bitwise equality, tolerance-bounded equality, same posterior class, same proof obligation, or same qualitative decision? | moving the output target after replay |
| `independent_replay_expectation` | What independent party, implementation, or environment should be able to reproduce the result? | author-local replay only |
| `maximum_authority_effect` | What wording is allowed even if replay succeeds? | replay-to-promotion laundering |
| `rollback_rule_ids` | Which rule fires if replay fails? | silent failure retention |

## Authority ceilings

Computational replay has a ceiling lower than candidate evidence unless the non-computational ledgers also clear their debts:

| Replay result | Maximum direct authority effect |
|---|---|
| artifact unavailable | no computational support |
| artifact available but unreplayed | custody / inspection cue only |
| author-local replay | workflow plausibility only |
| independent same-environment replay | artifact-local reproducibility |
| independent cross-environment replay | stronger artifact-local reproducibility plus portability pressure |
| independent reimplementation | possible evidence-unit strengthening, still route-local |
| adversarial replay with negative controls | severe-test input if other ledgers permit |

Even the strongest replay does not itself establish public-record closure, causal mechanism, observed-sector recovery, candidate-native observability, or ToE identity.

## Non-promotion rule

Computational reproducibility can preserve, cap, freeze, or roll back support. It cannot promote a route, close `OQ-0057`, or convert custody replay into physical evidence.
