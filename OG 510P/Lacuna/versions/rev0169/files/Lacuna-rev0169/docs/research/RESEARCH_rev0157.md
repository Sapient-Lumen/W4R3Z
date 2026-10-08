# Research — rev0157

## Research question

What changes when a model-facing datacube does not merely tell an agent what should happen next, but supplies an exact, replayable kernel execution that has already succeeded under rollback?

Revision 0157 treats this as both an engineering and experimental question. The engineering result is turn preparation, exact replay, historical recovery, and same-run locking. The research value is a cleaner distinction among:

- a model’s proposed continuation;
- an orchestration chain’s internally consistent continuation;
- a kernel-executable continuation at one exact world-state head; and
- a durably accepted continuation with replayable custody.

## Relevance to Gwern’s retcon-planning concerns

Lacuna remains a governance substrate, not a completed retcon generator. Its contribution to the argument is to make several otherwise vague controls executable:

1. **Commitment budget.** Candidate facts can remain hypotheses until explicit assignments, anchors, commitments, consequences, or disclosures make revision costly.
2. **Path dependence.** The ledger records what was known, believed, selected, weighted, revised, repaired, or revealed at each point instead of laundering history into one current synopsis.
3. **Rubber reality.** A selected world does not become canon, narration does not mutate state by itself, and audience-visible claims require typed custody.
4. **Checkpoint reproducibility.** A turn is bound to exact player input, request head, grants, role slices, proposal, prepared event chain, and receipt.
5. **Falsifiability.** Monolithic, role-separated, and kernel-governed hosts can be compared from the same cube and exact request sequence.

Rev0157 strengthens the fifth point. An experimental condition can no longer count a sidecar-valid but kernel-invalid continuation as “ready.” The prepared post-state, including contexts visible to the next turn, is reproducible.

## Exact preparation as an experimental object

A `lacuna.turn-preparation.v1` file can support controlled measurements that a proposal alone cannot:

- whether two providers produce proposals that normalize to the same typed operations;
- whether a weaker coordinator can follow the prepared replay path without inventing IDs or flags;
- whether projected audience context is stable under independent replay;
- whether a later host can detect a forged or contaminated sidecar;
- whether crash recovery preserves event count and custody;
- how often proposals pass structural preflight but fail real kernel semantics; and
- where latency/cost is spent: planning, narration, verification, preparation, or commit.

The preparation should not be shown to an audience-only narrator. It is a parent/kernel audit artifact and may contain privileged state.

## Hyperlegibility hypothesis

The user’s concern that “what feels natural to a frontier model is not natural to every model” suggests a concrete hypothesis:

> Models with lower instruction-following or tool-planning capability will complete more correct turns when every stage exposes one complete input, one exact schema, one generated command, and one already-rehearsed commit envelope than when they receive an equivalent prose workflow.

A useful ablation has five conditions:

1. prose instructions only;
2. packet plus prose role label;
3. digest-bound task cards;
4. task cards plus `run.json`/`NEXT.md`;
5. the rev0157 run plus exact kernel preparation.

Measure wrong-stage output, invented identifier rate, schema conformance, hidden-state leakage, kernel refusal rate, recovery correctness, calls, latency, tokens, and human intervention.

## Two-agent and multi-agent hypothesis

The most important split remains planner versus audience-only narrator, not “more agents are smarter.” It encodes an information-flow boundary:

- planner sees competing hidden worlds, commitments, repair debt, weights, and private hypothesis state;
- narrator sees only audience context and an approved observable plan;
- proposal builder serializes typed custody without inheriting arbitrary planning discretion;
- verifier receives the exact candidate and bindings but no commit authority;
- parent accepts artifacts and invokes the kernel.

Rev0157 adds a further separation: the kernel itself becomes an independent executable checker before readiness. This is useful even when all model roles are one provider or one base model.

For science, the analogous split is private hypothesis generation versus evidence-facing reporting, followed by provenance serialization, independent overclaim checking, and exact data-record commit. The method improves inspectability, not truth by consensus.

## Datacube as context curriculum

The cube can define an exact multi-invocation walk:

1. bind player/observer input at head H;
2. manufacture role-specific views and task cards;
3. retain exact outputs and ordered digest joins;
4. normalize the accepted proposal deterministically;
5. execute it under rollback to produce head H′ and next contexts;
6. commit exactly or recover the same event chain;
7. begin the next invocation from the verified durable projection.

This creates a context curriculum whose transitions are executable rather than conversational. It can be used for fiction, incident response, intelligence analysis, scientific hypothesis management, or any setting where private working hypotheses and public reports should not collapse into one prompt.

## Recovery as a custody experiment

Post-commit recovery is a useful adversarial fixture:

- interrupt after SQLite commit;
- optionally append unrelated later turns;
- retry from the old run directory;
- require no new prepared events;
- reconstruct the original request-head prefix;
- reject any modified prepared context even if all local sidecar digests are recomputed; and
- produce a receipt that identifies recovered delivery.

This tests whether the system’s authority is really in the durable ledger or merely in the coordinator’s current files.

## Proposed Gwern gift evaluation

A serious gift should include an experiment, not only an architecture. Use matched scenario capsules with identical initial cube, player sequence, model/version/settings, and evaluation forms across:

1. ordinary rolling-context generation;
2. prompt-only retcon planning;
3. Lacuna solo with source-bound typed commit;
4. Lacuna pair with planner/narrator information separation;
5. Lacuna full with proposal builder, verifier, and exact preparation.

Mechanical outcomes:

- contradictions and unauthorized revisions;
- hidden canary leakage;
- unsupported success assertions;
- commitment and consequence repair burden;
- live-world diversity and premature collapse;
- structural-preflight versus kernel-preparation failure rate;
- stale/cross-turn/tampered artifact refusal;
- exact replay and crash recovery success;
- role context size; and
- total latency/cost.

Blind human outcomes:

- coherence;
- agency;
- character continuity;
- payoff/setup quality;
- novelty;
- contrivance;
- mystery fairness;
- visible retcon seams; and
- overall preference.

The experiment should preserve complete external provider provenance but must not call a local digest a provider attestation.

## Negative results that would matter

Lacuna’s hypothesis would be weakened if:

- exact custody reduces contradictions but substantially damages agency or prose quality;
- pair/full separation leaks as often as a monolithic prompt;
- preparation rarely catches errors beyond structural preflight;
- weaker models cannot follow generated cards/pointers despite hyperlegibility;
- historical recovery is too expensive for realistic cubes;
- hosts work around typed custody by overusing narration-only turns; or
- raters prefer rubber reality even when they can identify its inconsistencies.

These are useful outcomes, not reasons to avoid evaluation.

## Next research instruments

1. Scenario capsules with frozen seed cubes and exact player-input sequences.
2. Provider invocation sidecars recording model/version/settings/tool grants/timing/cost without claiming attestation.
3. Automated hidden-state canaries and overclaim detectors.
4. Per-stage token/context measurements across model capability tiers.
5. Connected ChatGPT/API host exposing only begin/status/accept/commit.
6. Per-cube scheduling experiments across concurrent distinct runs.
7. Large-cube benchmarks for historical snapshot/rebuild cost.
8. External blind-rating harness for narrative and scientific-report conditions.

## Nonclaims

Rev0157 does not show that Lacuna produces better stories, discovers true hypotheses, eliminates retcons, or solves Gwern’s full planning problem. It makes one previously ambiguous boundary—workflow readiness versus executable readiness—precise enough to operate, attack, and measure.
