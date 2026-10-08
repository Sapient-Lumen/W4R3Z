# Research — rev0160

## Research question

Does turning the rev0159 source-bound checkpoint exchange into a strict managed run make Lacuna materially more useful as a gift, a ChatGPT-compatible game substrate, and a multi-provider/subagent research instrument—without pretending that host-side custody proves model quality or independence?

## Result in this revision

Operationally, yes.

Rev0159 answered “what exact objects should exist?” Rev0160 answers “how can a recipient traverse them correctly over several invocations?” One run now fixes source/cube identity and all provider routes, emits one complete current-stage dispatch, records accepted and failed attempts, manufactures each next card only after validation, makes refusal terminal, audits/rebuilds the entire chain, and commits or exactly recovers through the existing kernel.

This closes an important gap in the gift claim. The protocol no longer depends on the author remembering the ritual. It still does not answer whether the generated candidates, scores, compression, or prose are good.

## Question 1 — does this target Gwern’s real concerns?

The core target remains the “rubber reality”/commitment-budget problem: observed canon must be fixed, exposed consequences expensive to change, and unused hidden state cheap. Lacuna already supplied typed observations, plural worlds, commitments, consequence/revision custody, fair-play seals, audience/planner separation, and exact accepted mutation.

The managed run adds the experimental control surface needed to test those claims honestly:

- one exact source head and protected-state boundary;
- exact candidate and rollout cardinality;
- provenance-stripped judge context;
- deterministic score arithmetic and winner rule;
- winner-only compression;
- proposal-visible advisory verification;
- parent-only kernel review;
- fixed provider assignments;
- ordered attempt/output custody; and
- exact resume and commit recovery.

That is directly useful to the argument because a retcon-planning study that cannot reconstruct which context, model route, output, and accepted state belonged to each checkpoint is vulnerable to post-hoc substitution.

The remaining gap is empirical. Rev0160 does not show that retcon planning improves coherence, agency, payoff, novelty, mystery fairness, or enjoyment.

## Question 2 — can a ChatGPT user just begin?

At the player layer, yes: “Will you DM?” remains sufficient. The host should recognize session control, open a low-commitment scene, and keep protocol details backstage.

At the durable cube layer, capability still matters:

| Surface | Immediate play | Durable Lacuna mutation | Managed checkpoint role |
|---|---:|---:|---:|
| ordinary ChatGPT chat | yes | no | yes, through pasted self-contained dispatch |
| ChatGPT Project/custom GPT without host bridge | yes | no | yes, with a human parent bridge |
| connected ChatGPT app/action/agent host | yes | yes | yes, host advances managed run |
| Codex/Claude Code/Gemini CLI/workspace agent | yes | yes | yes, parent can call CLI and optionally subagents |

The key usability change is that a human bridge no longer needs to understand the whole checkpoint topology. It can repeat:

```text
read NEXT.md
render dispatch
paste one complete card
save one JSON object
accept or record failure
repeat
commit only when ready
```

The dispatch embeds the full task card, so ChatGPT need not access local files or infer missing context. This is a stronger, more honest answer than saying a Project upload somehow gives web ChatGPT a local persistent process.

## Question 3 — do configurations and subagents become hyperlegible?

Yes at the host-contract level. A managed run fixes a complete heterogeneous route map before execution. For example:

```text
generator  = ChatGPT
judge      = Codex
compressor = Claude Code
verifier   = Gemini CLI
```

At each state the cube names the exact provider route and provider-specific alias. A capable parent can map that to a native subagent; a less capable parent can open a fresh chat/API call; a serial fallback can use one context. The artifact path is identical across those configurations.

This supports a clean experimental distinction:

- **same artifact protocol, serial context** tests the checkpoint procedure without isolation;
- **same artifact protocol, role-separated contexts** tests information asymmetry and independent process boundaries;
- **same artifact protocol, mixed model families** tests procedural diversity;
- **same source capsule, prompt-only control** tests whether custody itself changes failure modes.

The receipts do not prove that the configured provider ran. They make the parent’s retained declaration and exact accepted output inspectable.

## Why two agents may matter

For ordinary play, the highest-value split remains privileged planner versus audience-only narrator: it prevents hidden rationale from leaking into prose by construction.

For checkpoints, generator versus judge is the analogous split. The judge receives candidate content but not declared generator provenance or notes. This can reduce direct self-preference and lets a study vary model family independently. It does not guarantee anonymity: style, structure, shared provider memory, or collusion can reveal origin.

A compressor adds a different asymmetry: it receives only the deterministic winner, preventing rejected future arcs from entering the compressed state through ordinary context carryover. A verifier adds proposal-visible adversarial checking but cannot independently reproduce hidden winner selection. The parent remains the only actor with the full chain.

Thus, “more agents” is not the hypothesis. The testable intervention is **manufactured context asymmetry plus fixed authority**.

## The datacube as repeated context curriculum

Rev0160 makes the “exact cube we want them to walk through” idea literal. The cube can control a multi-invocation curriculum:

1. freeze one source head, player trigger, grant, and protected state;
2. issue an exact generator card with preallocated candidate/rollout slots;
3. retain the return and manufacture a canonical provenance-blind judge card;
4. retain deterministic selection and manufacture a winner-only compressor card;
5. assemble the narrow proposal and manufacture a proposal-visible verifier card;
6. run the real kernel under rollback;
7. commit or authenticate the exact durable result;
8. reconstruct the next step from disk in a later process.

This structure is useful beyond fiction. Scientific hypothesis work could give a generator privileged hypotheses, a judge blinded candidate reports, a compressor a selected compact model, and a public reporter only evidence-facing material. The kernel would still govern provenance and authority, not scientific truth.

## Mechanical outcomes now measurable

The managed layer adds measurements that were previously external bookkeeping:

- route assignment per role;
- attempted and accepted invocation count per role;
- failure classes and retry count;
- exact card and dispatch digests;
- exact accepted output digest;
- malformed/wrong-stage/cross-run/relabelled/missing-custody refusals;
- status progression and terminal refusal;
- pointer damage/recovery;
- direct versus recovered commit delivery;
- duplicate-event absence after retry; and
- host-declared model/version/ID/timing/duration.

Existing Lacuna measures remain available: contradictions, stale-head refusal, commitment and consequence burden, repair debt, unknown preservation, audience/planner leakage, event replay, and projection verification.

## Measurements still external

- candidate diversity and missing explanatory modes;
- faithful forward simulation;
- coherence, agency, character believability, genre fit, payoff, novelty, coincidence, mystery fairness, seam visibility, and enjoyment;
- token counts, billing, latency accuracy, provider logs, and tool use unless independently supplied;
- semantic anonymity and worker independence;
- whether hidden state should have been compressed or kept plural; and
- whether checkpoint timing was appropriate.

These should remain separate from ledger truth and from mechanically passing schemas.

## Comparative scenario-capsule design

The next research artifact should package a fixed seed cube and scripted departures under at least four conditions:

| Condition | Checkpoint policy | Context topology |
|---|---|---|
| forward-only | none; one continuing plan | one context |
| prompt-only retcon | same generate/score/compress prose instructions | one context, no managed custody |
| Lacuna serial | same source cards/rubric/commit boundary | one context executes all roles |
| Lacuna separated | same source cards/rubric/commit boundary | role-dedicated contexts; parent commits |

A mixed-provider separated condition can be added after same-family comparisons.

Each capsule should contain:

- seed artifact and verified head;
- exact player inputs and checkpoint triggers;
- policy parameters and randomized condition label;
- fixed model family/version declaration and sampling budget;
- managed run archive or equivalent control artifacts;
- expected mechanical refusal/acceptance classes;
- external token/cost/latency records;
- blind human-rating forms; and
- analysis code that never treats aesthetic scores as probabilities or canon.

Suggested scenarios remain: off-script departure, culprit-switch pressure after disclosed clues, incidental-detail overfitting, contradictory player success claims, consequence-heavy reversal, concurrency/staleness, hidden-context leakage, and cross-run handoff contamination.

## Hypotheses, not findings

H1. A single generated next action reduces operator and weaker-model protocol errors relative to the stateless guide.

H2. Cardinality-sized cards plus exact accept validation reduce malformed or silently incomplete returns across providers.

H3. Fixed mixed-provider routes and invocation custody improve reproducibility of comparative runs, even though they do not attest provider execution.

H4. Role-separated generator/judge contexts reduce declared-author preference relative to serial self-judging, but semantic fingerprints remain.

H5. Winner-only compression reduces rejected-future leakage relative to a monolithic checkpoint prompt.

H6. Managed exact recovery reduces duplicate or stale writes independently of story quality.

H7. The additional custody may improve honesty and debuggability while adding latency/cost and sometimes reducing stylistic coherence.

None is confirmed by this release.

## Development performance observation

During audit, repeated committed-run validation duplicated exact preparation work. Splitting public full-chain receipt validation from a package-internal already-validated-chain helper reduced representative fixture times for commit, committed audit, and idempotent retry. This supports practical iteration, but it is not a benchmark across machines or real provider latency.

## Immediate next experiment

Build one ten-turn off-script mystery capsule. Use the same model family and budget for prompt-only, Lacuna serial, and Lacuna separated conditions; force one major departure, one tempting culprit switch after exposed clues, and one reversal with visible consequences. Retain managed runs and exact invocation declarations, blind the human-rating labels, and report mechanical custody outcomes separately from aesthetic ratings.

That experiment—not broader worker authority—is the next evidence-bearing step.
