# Research notes — rev0156

## Research question

Can Lacuna serve simultaneously as:

1. a useful experimental gift addressing the central governance problem in Gwern’s retcon-planning proposal;
2. a playable system that an ordinary adult can enter by saying “Will you DM?” to ChatGPT or another model; and
3. a hyperlegible cross-provider datacube walk in which weaker models and subagents receive enough exact context to act correctly without being granted mutation authority?

Revision 0156 treats these as one research program. The common problem is not raw model intelligence. It is whether the host makes state, authority, context, and the next action explicit enough that model capability can be spent on planning and narration rather than reverse-engineering a protocol.

## Relation to “Better Fiction via Retcon Planning”

Gwern’s “Better Fiction via Retcon Planning,” dated June 2, 2026, proposes a loop of observed canon, soft hidden hypotheses, future rollout, selection, checkpoint compression, and forgetting. The essay’s central warning is “rubber reality”: hidden facts may remain cheap to revise, but observed canon and exposed consequences must become expensive. It therefore calls for a commitment budget.

Primary source: <https://gwern.net/blog/2026/llm-retcon>.

Lacuna does not yet implement the whole generative loop. It implements the part most likely to fail if represented only as prompt advice:

- observed reports, assertions, sources, and disclosures have typed custody;
- hidden hypotheses can remain plural candidate worlds;
- attention weights do not silently become truth;
- commitment is distinct from confidence;
- consequences create explicit revision burden and forward-repair obligations;
- fair-play openings can be precommitted without freezing an entire world;
- audience and planner projections differ structurally;
- each turn is source/head/grant bound and can refuse stale or unsupported mutation.

This makes Lacuna a governance substrate and reference implementation for the essay’s commitment-budget problem. It is a useful gift precisely if it is presented as that—not as completed evidence that retcon planning improves fiction.

## Gift test

A serious gift should let the recipient do more than read claims. It should support four activities.

### Inspect

The recipient can inspect exact event, projection, turn, commitment, consequence, seal, particle, and context-firewall semantics. They can see what is invariant and what is deliberately external.

### Run

The recipient can create a campaign, begin one exact request-scoped turn, delegate role cards across providers or conversations, and attempt a kernel commit. The happy path and refusal path are executable.

### Falsify

The system exposes ablations rather than assuming more machinery is always better: solo versus pair versus full, prompt-only versus generated cards, one context versus role-specific contexts, and Lacuna-governed versus forward-only or prompt-only retcon baselines.

### Extend

Candidate generation, rollout, scoring, checkpoint optimization, and experimental hosting can be added outside the kernel without weakening the custody boundary.

A gift that merely says “use multiple agents and remember canon” would not meet this test. Revision 0156’s run protocol materially improves runnability and falsifiability.

## What changed in the model entrance

Revision 0155 manufactured exact task cards but still left workflow custody in the coordinator’s memory and documentation. That is too much hidden inference for a literal or less capable model:

- Which request is current?
- Which return has already been accepted?
- Which role owns the next step?
- Which of several JSON files is complete input?
- Which schema should be returned?
- What exact command advances the chain?
- Has an edited pointer or valid-but-wrong-stage artifact been substituted?

Revision 0156 stores the answers in one request-scoped directory and recomputes them during every audit. `NEXT.md` is not a loose checklist; it is a deterministic view of the strict manifest and artifact topology.

The research hypothesis is that **hyperlegibility disproportionately helps models below the frontier**. A strong model may reconstruct a missing chain. A weaker model is more likely to summarize, improvise a schema, reuse stale context, or act as the wrong role. Reducing those choices should improve protocol conformance without requiring a stronger model.

## One-sentence play entrance

“Will you DM?” is sufficient player intent. The host should not require a player to know Lacuna vocabulary or choose an execution profile.

The research distinction is between narrative start and durable state transition:

| Surface | Immediate play | Durable Lacuna mutation |
|---|---:|---:|
| Ordinary ChatGPT conversation | Yes | No |
| ChatGPT Project with files/instructions | Yes | No, absent a bridge |
| Human ChatGPT/CLI paste bridge | Yes | Yes |
| Connected ChatGPT Action/App/API host | Yes | Yes |
| Codex/Claude Code/Gemini CLI repository host | Yes | Yes |

OpenAI’s Projects documentation currently describes project files, project instructions, memory, and connected apps; those features should not be conflated with arbitrary durable access to a user’s local Lacuna campaign. Source: <https://help.openai.com/en/articles/10169521-projects-in-chatgpt>.

The one-time chat-only disclosure is intentionally small: “We can play immediately; this chat is not yet committed to a Lacuna cube.” After that, the model should play rather than repeatedly expose implementation details.

## ChatGPT research paths

### Conversation-only DM

This tests whether Lacuna’s behavioral doctrine improves play even without persistence: player actions are attempts rather than automatic successes, experienced facts remain fixed, and unused explanations remain plural. It should not claim that the cube changed.

### Human paste bridge

A human begins a `solo` run, pastes the complete packet into ChatGPT, saves the exact proposal JSON, accepts it, and commits only after the run says it is ready. This is deliberately low-tech but scientifically useful because the artifact chain remains reproducible.

### Role-dedicated contexts

Separate ChatGPT conversations or API calls can act as planner, narrator, builder, and verifier. This is useful context separation, though not a provider-attested confidentiality boundary. The generated task card—not a remembered role description—is the per-turn prompt.

### Connected host

A narrow host exposing begin/status/accept/commit equivalents is the preferred future ChatGPT integration. It should expose deterministic artifacts rather than arbitrary filesystem or mutation access. This makes the interface auditable and keeps commit with the parent host.

## Provider and subagent hypotheses

Official current references used for the checked-in adapters:

- Codex custom subagents: <https://developers.openai.com/codex/subagents>
- Codex `AGENTS.md`: <https://developers.openai.com/codex/guides/agents-md>
- Claude Code subagents: <https://code.claude.com/docs/en/sub-agents>
- Claude Code instruction memory/imports: <https://code.claude.com/docs/en/memory>
- Gemini CLI subagents: <https://geminicli.com/docs/core/subagents/>
- Gemini CLI context files: <https://geminicli.com/docs/cli/gemini-md/>

Provider syntax can drift. The portable schema and run state must remain usable when a native adapter is unavailable.

### H1 — Generated dispatch beats “remember to delegate”

A root instruction saying “use subagents when helpful” leaves role choice and context construction implicit. A deterministic next action naming the role alias, complete card, expected schema, and accept command should produce higher conformance and fewer context leaks.

### H2 — Pair captures most information-asymmetry benefit

Planner → audience-only narrator may remove the largest leakage channel while avoiding builder/verifier latency. Pair should be the strongest default challenger to a monolithic model.

### H3 — Full helps most at high-impact custody boundaries

A separate serializer and fail-closed verifier should matter more when operations create or revise durable assertions, anchors, consequences, disclosures, or commitments than for narration-only turns.

### H4 — Agent count is not the causal variable

Several agents sharing the same complete privileged context may provide little benefit. The important intervention is manufactured context asymmetry, exact contracts, and parent-only authority.

### H5 — A verifier is useful only when it can refuse

A verifier prompted to be agreeable is cosmetic. A fail-closed template, independent context, explicit checks, and a closed run after refusal are necessary for a meaningful ablation.

### H6 — Exact sidecar state improves cross-model replay

A later model invocation should be able to resume correctly from `RUN_PATH` without chat memory. Cross-turn return substitution, upstream edits, wrong-stage schemas, and pointer tampering should fail deterministically.

## Two-agent and multi-agent configurations

Two agents are not universally required. They are especially valuable where the desired output should not contain the reasoning used to choose it.

### Fiction

A planner can see candidate worlds, commitment burden, and private risks. A narrator can see only the approved observable plan and audience projection. This reduces accidental canonization and hidden-state leakage.

### Science and analysis

A hypothesis worker can inspect private candidate explanations, provenance, and uncertainty. A report worker can receive only evidence approved for public communication. A verifier can check citation/provenance binding and unsupported certainty without being allowed to mutate the evidence ledger.

The analogy is structural, not a claim that narrative and scientific truth are identical. In both cases, separation helps prevent “internal working hypothesis” from becoming “publicly asserted conclusion” merely because one model wrote both in one context.

## Proposed four-condition experiment

Use the same scenario capsules, model family, token/cost budget, and scripted player departures in four conditions:

1. **Forward-only baseline:** one continuing planned world in one context.
2. **Prompt-only retcon:** periodic backward reinterpretation under prose instructions in one context.
3. **Lacuna pair:** plural hidden state with planner → audience-only narrator and governed commit.
4. **Lacuna full:** planner → narrator → proposal builder → verifier with the same custody kernel.

Randomize condition order where practical. Preserve exact prompts, outputs, model/version settings, run artifacts, refusals, latency, and cost. Do not let evaluators see condition labels.

### Mechanical measures

Lacuna or the host can measure:

- invalid or stale artifact refusal;
- wrong-stage/schema return rate;
- hidden-state canary leakage;
- unsupported physical-success assertions;
- contradiction and revision attempts;
- commitment/consequence repair burden;
- number and diversity of retained candidate worlds;
- context bytes/tokens per role;
- run completion rate;
- latency, calls, and cost;
- whether the final receipt can be replayed from exact custody.

These measures do not substitute for narrative quality.

### Human measures

Blind raters should separately score:

- coherence;
- player agency;
- character consistency;
- genre fit;
- payoff and setup quality;
- novelty;
- coincidence/contrivance;
- mystery fairness;
- visibility of retcon seams;
- overall preference.

Inter-rater agreement and uncertainty should be reported. A result in which custody improves but prose quality does not is still informative.

## Adversarial conformance study

A smaller study should target the entrance itself across model tiers and providers.

Give each model one of:

- prose-only instructions;
- packet + prose role name;
- generated task card;
- task card + audited run `NEXT.md`.

Inject controlled hazards:

- stale prior-turn return;
- edited upstream artifact;
- valid JSON for the wrong stage;
- unchanged placeholder;
- misleading hand-edited `NEXT.md`;
- provider alias mismatch;
- a request to commit from a worker role.

Measure correct refusal, exact schema conformance, unintended prose, invented identifiers, context leakage, and successful completion. This directly tests the user’s concern that what feels natural to a frontier model is not natural to every model.

## Audit-derived lessons

### Documentation can be an executable defect

The prior ChatGPT bridge instructed operators to use `--player-input-file`, but the CLI did not implement it. The prose described a safer boundary that did not exist. Treating model-facing docs as code surfaced and repaired the mismatch.

### “One complete input” must be literal

An instruction that names a packet and a proposal draft while pointing to only one file still requires inference. Revision 0156 makes the named path sufficient for the current action.

### Valid JSON can still be the wrong action

Schema validity alone cannot protect a stateful chain. The expected stage, packet, role, ordered upstream digests, proposal identity, and artifact metadata must agree.

### A human-readable pointer is an attack surface

A weaker model may obey `NEXT.md` even when `run.json` is correct. The pointer must therefore be derived and audited, not merely advisory text that can drift independently.

### Privacy defaults matter

Automatically returning planner context in every receipt would turn a least-context design into a routine leakage path. Privileged receipt context is now explicit opt-in.

### Subagents are orchestration tools, not authorities

The cube should prompt the parent to use a bounded role and hand it the right card. It should not let the role choose its own scope, mutate the cube, or infer that provider isolation has been proven.

## Next research instruments

The highest-value additions after rev0156 are:

1. a narrow connected host implementing the four run operations for ChatGPT/API use;
2. invocation-custody sidecars recording provider/model/version/settings/timing without calling them attestations;
3. same-run locking and explicit begin/commit crash recovery;
4. scenario capsules and a reproducible four-condition runner;
5. automated leakage and protocol-conformance fixtures across model tiers;
6. candidate-world proposal/rollout modules that remain separate from commitment and canonization.

Revision 0156 does not answer the empirical quality question. It makes that question substantially easier to ask without confusing model fluency with state custody.
