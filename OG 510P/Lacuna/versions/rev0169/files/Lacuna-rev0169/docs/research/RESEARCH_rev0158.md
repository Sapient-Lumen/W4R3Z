# Research — rev0158

## Research question

Can a typed datacube make retcon planning and long-running model play more reproducible by manufacturing the exact contexts, authorities, and acceptance boundaries through which different models walk?

Revision 0158 does not answer the aesthetic part empirically. It reduces several confounds that would otherwise make the experiment hard to interpret.

## Question 1 — is Lacuna a useful gift for Gwern’s retcon-planning questions?

The strongest claim is narrower than “this solves retcon planning.” Lacuna implements governance for the essay’s commitment-budget and rubber-reality concerns:

- exact observed/reported/believed provenance rather than one flat canon summary;
- plural hidden candidate worlds and first-class unknowns;
- monotone commitment and explicit revision-impact review;
- authored consequence custody and forward repair rather than silent transfer;
- audience/planner projection separation;
- selective precommitment receipts for mystery promises;
- source-bound turns, stale-head refusal, exact rollback preparation, replay, and recovery.

The missing experimental host still needs checkpoint policy, candidate generation, rollout, scoring, selection, and compression. Therefore the gift is best understood as an executable control condition and custody substrate around the proposed planner.

A useful comparison should hold model family, token budget, transcript, and generation policy constant while varying:

1. forward-only hidden state;
2. prompt-only retcon planning;
3. Lacuna solo custody;
4. Lacuna pair custody with planner/narrator separation; and
5. Lacuna full custody with builder/verifier stages.

Mechanical outcomes should be separated from human ratings. Lacuna can measure stale or cross-turn refusal, hidden-context leakage through structured artifacts, unsupported-success custody, commitment/consequence burden, repair lineage, exact context bytes/digests, event replay, latency, and topology. Human raters must still judge coherence, agency, character, genre, payoff, novelty, coincidence, and enjoyment.

## Question 2 — can a 20-year-old player simply ask ChatGPT to DM?

At the player-experience layer, yes. A conversational model can begin a scene from “Will you DM?” without requiring schema knowledge.

At the persistence layer, capability matters:

| Host surface | Begin play | Persist to local Lacuna without another bridge |
|---|---:|---:|
| ordinary ChatGPT conversation | yes | no |
| Project/custom instructions with uploaded files | yes | no, unless connected tools exist |
| human bridge to the CLI | yes | yes |
| connected Action/App/API host | yes | yes |
| shell-capable workspace agent | yes | yes |

The correct conversation-only disclosure is one sentence: play can start immediately, but it is not yet committed to a Lacuna cube. The model should then open a reversible, low-commitment situation rather than making the player administer the ledger.

For a connected or workspace host, rev0158 gives the literal command:

```bash
./lacuna play start .lacuna-play --bootstrap --profile orchestrated --format markdown
```

This converts the exact invitation into typed session control, safely resolves a campaign, and emits one run/next action. The first worker handoff can then be rendered for ChatGPT with the complete card embedded:

```bash
./lacuna turn run dispatch RUN_PATH --provider chatgpt --format markdown
```

This is a testable improvement over “upload the repository and hope the model infers the procedure.”

## Question 3 — how should weaker or differently tooled models enter?

The portable unit is not a provider feature. It is one exact delegated-stage envelope:

```text
role + complete card + input kind + digest + return schema
+ forbidden actions + parent-only next command + nonclaims
```

Codex, Claude Code, Gemini CLI, ChatGPT, an API worker, a local model, or a human can all consume that unit. Native agent definitions can improve discovery, but they are not required for correctness.

This creates several experimental configurations:

### Monolithic parent

One context receives the packet and builds the final proposal. Cheapest and easiest, but hidden and audience context share one model state.

### Planner/narrator pair

The planner sees private hypotheses; the narrator sees only audience context plus an approved observable plan. The parent serializes a safe proposal. This is the default auto topology for an ordinary director session-control start.

### Full four-role chain

Planner, audience-only narrator, proposal builder, and independent verifier each receive a digest-bound card. This spends more calls to isolate information and check binding, not to create a majority vote.

### Two-agent scientific/reporting pattern

A private hypothesis worker may compare explanations while a report worker receives only publishable evidence and approved conclusions. The parent binds source provenance and accepts only a typed public report proposal. This uses the same information-asymmetry principle without claiming that narrative-specific policies automatically transfer to science.

The core ablation is therefore not simply “one model versus many.” It is:

- shared conversational context versus manufactured least-context cards;
- path-only delegation versus embedded exact dispatch;
- implicit intent classification versus typed input;
- coordinator prose versus schema-bound one-object returns;
- sidecar agreement versus executable kernel preparation.

## The datacube as a repeated context walk

A cube can prescribe the exact context sequence across multiple turns and even multiple CLI/model invocations:

1. start from one verified head;
2. issue exact text with a typed kind;
3. generate a packet and deterministic topology;
4. manufacture a role-specific card;
5. bind the worker return to the packet/upstream digest;
6. manufacture the next card without relying on conversation memory;
7. rehearse the final proposal in the real kernel;
8. commit or refuse at the expected head; and
9. derive the next audience/planner projections from the ledger.

This permits matched provider and topology comparisons in which every host receives the same semantic input boundary. It does not control provider-internal memory, hidden system prompts, sampling, or tool enforcement; those must be recorded as external experimental provenance.

## Suggested scenario capsule

A future capsule should include:

- seed cube and exact verified head;
- campaign metadata and typed player-input sequence;
- checkpoint triggers;
- topology/provider configuration;
- exact dispatch/card digests and model/version metadata;
- expected acceptance/refusal classes, not expected prose;
- external transcript and rollout digests;
- mechanical metrics;
- blind human-rating form; and
- nonclaims about evaluator subjectivity and provider attestation.

Useful adversarial families remain off-script departure, mystery culprit pressure, incidental-detail overfitting, contradictory player success, consequence burden, stale concurrency, context leakage, and cross-turn handoff contamination. Rev0158 adds session-control misrouting, missing-filesystem handoff, linked-member substitution, oversized sidecar, and pointer-repair cases.

## Hypotheses rather than conclusions

H1. Explicit input typing reduces accidental fictionalization of session-management text.

H2. Embedded dispatches improve successful one-object completion for remote and weaker coordinators relative to path-only instructions.

H3. Planner/narrator separation reduces structured hidden-state leakage relative to a monolithic context, though it may increase cost or reduce prose quality.

H4. A full verifier stage catches more binding and leakage defects than pair mode, but may not justify its latency for ordinary turns.

H5. Exact preparation and historical recovery reduce false “ready” and duplicate-retry failures independently of model quality.

H6. Typed commitment/consequence custody improves continuity under retcon pressure, but may overconstrain adaptive fiction if policy sets commitment too aggressively.

None of these hypotheses is reported as confirmed in this release.

## Immediate next experiment

Build one small external runner that invokes the same model family under solo and pair conditions for a ten-turn off-script mystery capsule. Retain exact dispatches and returns, score structured leakage/refusal/repair mechanically, and obtain blind human ratings for coherence, agency, and seam visibility. That experiment would test the new context-compiler boundary without first requiring the entire candidate-rollout-scoring architecture.
