# Research — rev0159

## Research question

Can a typed datacube turn retcon planning from an attractive prompt pattern into a reproducible experiment in which canon, hypotheses, rollouts, selection, compression, authority, and acceptance remain distinguishable across many model calls?

Revision 0159 implements the exchange and custody adapter. It does not report that the adapter improves fiction.

## Why this addresses Gwern’s actual concern

Gwern’s June 2, 2026 essay “Better Fiction via Retcon Planning” proposes preserving observed canon, maintaining soft hidden hypotheses, sampling explanations, rolling them forward, scoring them, compressing the winner, and forgetting detailed future plot. Its central failure mode is rubber reality: backward adaptation becomes cheating when observations, clues, or exposed consequences are rewritten as cheaply as unused hidden state.

Lacuna directly governs that boundary:

- observed/reported/believed propositions retain typed source and perspective;
- hidden worlds and unknowns remain plural;
- commitment is mutation policy rather than confidence;
- assignment changes create successors instead of overwrites;
- visible consequences create explicit repair debt;
- fair-play secrets can be digest-precommitted;
- audience and planner contexts are structurally different;
- accepted mutations are source-bound, stale-head checked, replayable, and recoverable.

Rev0159 adds the missing experimental walk around those mechanisms: exact candidate cardinality, exact forward beats, provenance-blind judging, deterministic score custody, winner-only compression, narrow checkpoint operations, advisory verification, kernel rehearsal, and exact commit/recovery.

The useful gift claim is therefore narrow and falsifiable: Lacuna makes several forms of silent cheating and artifact drift detectable while supplying a common substrate on which retcon-planning conditions can be compared.

## Player and ChatGPT question

A player can simply say “Will you DM?” The host-level answer depends on capabilities:

| Surface | Start a scene | Persist into a local Lacuna cube |
|---|---:|---:|
| ordinary ChatGPT conversation | yes | no |
| ChatGPT Project/custom instructions only | yes | no, absent connected tools |
| human paste bridge | yes | yes |
| connected app/action/API host | yes | yes |
| shell-capable workspace agent | yes | yes |

The correct chat-only disclosure is brief: play can begin now, but it is not yet committed to Lacuna. A tool-capable host uses `play start` for the one-sentence entrance and follows the generated run pointer. The player does not administer the checkpoint loop; checkpoints are backstage parent work triggered by an explicit host/user planning decision.

For ChatGPT Pro or another frontier host with role-separated calls, the exact checkpoint cards can be delivered serially or to dedicated contexts. The system should state which mode actually occurred. A serial execution is valid custody but not evidence of independent judging.

## Why exact cardinality matters for less capable models

A frontier coordinator may infer that “four candidates over six turns” means four objects, each with six ordered beats. A weaker or smaller model may return three candidates, summarize the whole horizon in one paragraph, omit a score slot, or invent identity fields after the fact.

Rev0159 turns those hidden expectations into a concrete curriculum:

- output templates contain all candidate IDs;
- every rollout array contains one placeholder per horizon turn;
- every judge score slot is preallocated;
- the complete card identifies the one object to return;
- the dispatch identifies the exact role, provider alias, save path, and parent next command;
- validators recompute identities and cardinality instead of repairing them.

This is the “datacube as executable context compiler” idea: the cube does not merely store facts; it manufactures the exact bounded context and return shape through which a role should walk.

## Multi-agent hypotheses

Two agents are most valuable when they create an information boundary, not merely more tokens.

For ordinary play, the strongest split remains privileged planner versus audience-only narrator. For checkpoints, the highest-value boundaries are:

1. generator versus provenance-blind judge, reducing direct self-selection;
2. judge versus winner-only compressor, preventing rejected futures from contaminating the bottleneck; and
3. workers versus parent, preserving exact assembly and kernel authority.

A four-worker topology may outperform serial execution, but it may also add latency, mismatch, and provider memory leakage. Rev0159 makes both conditions consume the same semantic cards so the topology itself can be ablated.

## Scientific analogue

The same pattern can separate hypothesis work from evidence-facing reporting:

| Fiction checkpoint role | Scientific analogue |
|---|---|
| generator | proposes multiple explanatory models and prospective consequences |
| provenance-blind judge | evaluates fixed criteria without declared author identity |
| compressor | writes a bounded working-model update and preserved uncertainties |
| verifier | checks visible provenance, scope, unresolved questions, and overclaim |
| parent | owns experimental design, full comparison custody, and record acceptance |

This does not make a panel scientifically correct. It makes information flow and responsibility inspectable, and it permits tests of monolithic versus separated reasoning under identical artifacts.

## Proposed comparative scenario capsule

Use at least four matched conditions:

1. **forward-only baseline:** one continuing hidden plan;
2. **prompt-only retcon:** generate/score/compress instructions in one context without Lacuna custody;
3. **Lacuna serial:** the same model executes exact checkpoint cards in sequence;
4. **Lacuna separated:** role-dedicated generator, judge, compressor, and verifier contexts with parent-only acceptance.

Each capsule should contain:

- one seed cube and verified head;
- exact scripted player inputs and checkpoint triggers;
- policy, rubric, model family, token/cost budget, and randomization plan;
- exact cards, dispatches, returns, digests, declared provider/model/version, timing, and retry lineage;
- expected mechanical acceptance/refusal classes rather than expected prose;
- blind human-rating forms and randomized condition labels; and
- explicit nonclaims about provider attestation and evaluator objectivity.

Scenario families should include off-script departure, mystery culprit pressure, incidental-detail overfitting, contradictory claimed success, accumulated consequence burden, stale concurrency, confidentiality, and cross-checkpoint artifact contamination.

## Measures

### Mechanically available

- protected-canon mutation attempts and refusal classes;
- exact candidate/rollout cardinality;
- unknown preservation;
- score arithmetic and deterministic selection agreement;
- compression size and operation-surface compliance;
- hidden-context fields present or absent from structured artifacts;
- stale/cross-request/edited artifact refusal;
- consequence and commitment burden before/after accepted revisions;
- exact event replay and recovery agreement;
- latency, invocation count, token/cost metadata supplied by the host; and
- serial versus separated topology.

### Necessarily external

- coherence, agency, character believability, genre fit, payoff, novelty, coincidence, mystery fairness, seam visibility, and enjoyment;
- whether a rollout was actually predictive rather than plausible-sounding;
- whether candidates covered the important explanatory modes;
- whether the rubric matches player values; and
- whether provider contexts were truly independent.

## Hypotheses, not results

H1. Exact cardinality-explicit cards reduce malformed and silently incomplete model returns relative to prose-only instructions.

H2. Provenance-blind judging reduces declared-author bias but does not eliminate semantic or shared-context bias.

H3. Winner-only compression reduces rejected-future leakage into later narration relative to a monolithic prompt.

H4. Parent-side deterministic selection and kernel review reduce winner substitution, stale mutation, and duplicate-retry failures independently of prose quality.

H5. Role-separated checkpoints improve mystery restraint and continuity under off-script pressure, but may cost more and sometimes reduce stylistic coherence.

H6. Lacuna’s commitment/consequence substrate produces more visible repair work than prompt-only retconning; that burden may be either valuable honesty or excessive rigidity depending on policy.

None is confirmed by this release.

## Immediate next experiment

Build one ten-turn off-script mystery capsule and run all four conditions with the same model family. Force one major departure, one tempting culprit switch after disclosed clues, and one reversal with several visible consequences. Retain exact checkpoint artifacts, measure structured leakage/refusal/repair, and obtain blind ratings for coherence, agency, mystery fairness, and seam visibility. This is now the highest-leverage next step; broader worker authority is not.
