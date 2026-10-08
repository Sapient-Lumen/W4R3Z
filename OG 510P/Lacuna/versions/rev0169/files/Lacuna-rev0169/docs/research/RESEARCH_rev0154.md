# Research notes — rev0154

## Question

Can a fresh model—especially one that is less capable, less context-sensitive, or unfamiliar with Lacuna—correctly enter a governed campaign from an ordinary request such as “Will you DM?”, and can the same datacube support bounded multi-agent experimentation without relying on invisible author ritual?

Revision 0154 treats that as a research problem rather than merely a documentation problem. A protocol that works only after its inventor supplies the right incantation is not yet a usable experimental substrate.

## Three serious tests

### 1. Is Lacuna a useful gift to Gwern’s retcon-planning project?

Source under discussion: Gwern, “Better Fiction via Retcon Planning,” published 2 June 2026: <https://gwern.net/blog/2026/llm-retcon>

The strongest affirmative answer is narrow and concrete:

> Lacuna makes delayed commitment, plural hidden hypotheses, visible-consequence debt, selective precommitment, context separation, and accepted-state custody executable enough to test without silently laundering narration into canon.

That directly targets several real concerns in the article:

- **Rubber reality:** hidden facts should become harder to rewrite after visible consequences depend on them. Lacuna represents commitments, consequence links, review burden, successor lineage, and forward repair.
- **Mystery fairness:** late adaptation can become evidential cheating. Fair-play seals can bind a selected hidden opening without freezing the entire world.
- **Overfitting every detail:** a dropped cup should not automatically become prophecy. Unknown remains first-class, narration is non-canonical by default, relations do not infer, and the safe proposal template carries no semantic mutations.
- **Plural planning:** hidden state should remain a population rather than one early answer. Candidate worlds, partial assignments, particle attention, and factor custody preserve alternatives explicitly.
- **State-card bottlenecks:** future context should contain only what is needed. Audience/planner projections and source-bound turn packets provide deterministic context slices.
- **Forgetting versus cheating:** speculative rollout prose can be omitted from future model context while accepted custody remains replayable. The system distinguishes context forgetting from history deletion.

The honest negative answer is equally important. Lacuna still does not implement the article’s full generation loop:

- it does not invent or resample candidate worlds;
- it does not roll each world forward;
- it does not score aesthetic quality, agency, payoff, novelty, or coincidence;
- it does not select checkpoints;
- it does not optimize a compressed state card;
- it does not invoke, train, or evaluate an LLM.

So the gift is not “the finished retcon planner.” It is the custody and experimental control substrate that lets a retcon planner be evaluated without granting it unobservable freedom to rewrite its own evidence.

The detailed stage-by-stage analysis is in [`../design/GWERN_GIFT_TEST.md`](../design/GWERN_GIFT_TEST.md).

### 2. Can a 20-year-old player use it with ChatGPT or another LLM?

There are three materially different answers.

#### Conversation-only use

Yes, a capable chat model can begin role-playing immediately after “Will you DM?” It can choose reversible defaults, offer a low-commitment opening scene, and guide the player naturally. But without a local command bridge it cannot truthfully claim that a local Lacuna cube was updated.

That mode is useful, but it is **chat-only play**, not governed custody. The entrance requires the model to say so once rather than interrupting every turn with infrastructure caveats.

#### Human paste bridge

Yes, a player or operator can run `./lacuna model brief`, paste the brief or a fresh turn packet into ChatGPT, save the exact proposal, run commit, and paste back the accepted narration/receipt. This is more manual, but it preserves the authority boundary and works with ordinary chat interfaces.

The player should not need to learn internal terms before play. A setup page can tell the human which command to run; the model brief tells the model exactly what to do next.

#### Connected workspace/host

Yes, when ChatGPT, Codex, Claude Code, Gemini CLI, or another frontier model actually has file/shell access to the project, it can verify, open a source-bound packet, generate a proposal, commit, and present accepted narration. In this mode a one-message start is credible because the host can reach the cube.

The key research result is that **provider name is not the deciding variable**. Actual runtime capability is. ChatGPT Pro without a connected local action remains `chat`; a shell-connected agent is `workspace`; a parent that can create bounded contexts and retain commit authority is `orchestrated`.

### 3. Can different LLM configurations enter legibly and use subagents well?

The entrance must be redundant in the useful sense: machine-readable enough for strong models, explicit enough for literal models, and discoverable through provider-native files.

Revision 0154 supplies:

- a model brief exchange schema;
- Markdown and JSON renderings;
- a root intent router in `AGENTS.md`;
- Codex custom-agent definitions;
- Claude Code project-agent definitions;
- Gemini CLI project-agent definitions;
- ChatGPT Project/custom-GPT instructions and conversation starters; and
- one portable role vocabulary across providers.

The multi-agent hypothesis is not “four agents are wiser than one.” It is:

> Different information and authority boundaries can make failures easier to prevent and diagnose than one monolithic prompt containing hidden hypotheses, prose goals, and exact mutation syntax.

A privileged planner, audience-only narrator, packet-bound proposal builder, and independent verifier have different inputs and outputs. The parent remains the sole committer. This arrangement is useful for fiction and potentially for science, incident analysis, policy work, or any domain where private hypotheses must not leak into a public report.

## Discoverability is a protocol property

Before revision 0154, a turn packet was already a strong execution contract once a host knew to create one. It was not a complete entrance:

- a fresh model might treat the repository as a coding task rather than a game;
- a chat model might imply it had written to the cube when it had no tools;
- a workspace model might not know which campaign to resolve;
- a literal model might copy demonstration placeholders;
- a coordinator might give every subagent the same privileged context;
- a host might present unaccepted proposal prose after a failed commit.

The model brief turns those implicit prerequisites into explicit data. This is analogous to an API having both a valid low-level request format and a discoverable session bootstrap. The second is not cosmetic; it determines whether independent operators can reproduce the system.

## The hyperlegibility principle

A weaker model should not be expected to infer:

- whether “Will you DM?” is session control or an in-world action;
- whether the selected campaign is a library path or cube path;
- whether opening a packet mutates custody;
- whether the exact player wording must be preserved;
- whether an empty operation list is valid;
- whether narration itself is canon;
- whether a stale expected head can be manually repaired;
- where accepted narration appears in a receipt;
- whether a read-only subagent can still see secret files; or
- which role owns the final commit.

Revision 0154 therefore repeats critical invariants across three surfaces:

1. runtime contract fields and validation;
2. portable operator documentation; and
3. provider-native discovery/configuration files.

The repetition is intentional but bounded. Shared runtime helpers prevent semantic drift where duplicated examples would be dangerous.

## Audit findings as research findings

### Executable examples are authority surface

The old turn packet showed fake `replace.me` claim/assertion operations. Those values were visually obvious to a careful human but structurally valid enough for a literal model to return. This exposes a general design rule:

> Any example embedded in an authority-bearing response contract should be safe to execute after the minimum intended edit.

The replacement object is valid narration-only JSON. It teaches restraint by construction.

### Receipt shape must be mechanically true

Documentation referred to `receipt.narration`, but accepted receipts expose `narration` at the top level. A fluent model might compensate; a literal host might fail or fall back to proposal prose. The fix and tests demonstrate another rule:

> Human-readable operator instructions must be checked against real emitted objects, not memory of an intended abstraction.

### Exact input requires fail-closed mechanics

“Use the exact player message” is too weak if the generated command silently accepts empty input or shell-interprets metacharacters. The required `${PLAYER_INPUT:?...}` expansion and execution test convert prose guidance into a host-level guard.

### Verification belongs before readiness

A cube that opens is not necessarily a cube that is fit to continue. The model brief now runs deterministic verification and reports a coarse blocker. It does not dump hidden forensic detail into arbitrary contexts; it tells the operator to inspect the dedicated verifier.

### Role configuration is not secret isolation

Current provider mechanisms differ:

- Claude Code and Gemini CLI project agents can be defined with empty tool sets.
- Codex custom agents can be placed in a read-only sandbox, but read-only does not mean unable to inspect readable workspace files.

Therefore the architecture distinguishes **prompt/context separation** from **hard confidentiality**. Secrets such as unrevealed fair-play openings must remain outside any readable workspace unless the host provides a real isolation boundary.

Current official references are collected in [`../operators/PROVIDER_CONFIGS.md`](../operators/PROVIDER_CONFIGS.md).

## The datacube as an executable context curriculum

The user’s “exact cube we want them to walk through” intuition is significant. A deterministic datacube can define not only state but an experimental sequence of permitted contexts:

```text
seed head
   ↓ exact audience projection
source-bound player input
   ↓ exact planner/audience split
role-specific work products
   ↓ exact proposal grant
acceptance or structured refusal
   ↓ deterministic next head
repeat in a new process or provider
```

This supports controlled comparison across:

- model families;
- model versions;
- chat versus workspace hosts;
- monolithic versus role-split hosts;
- different context budgets;
- different world populations or commitment policies; and
- fiction versus non-fiction task domains.

Because each invocation can reconstruct context from the cube, the experiment need not depend on one model’s conversational memory. External sidecars can retain exact transcript bodies, model/provider/version, token counts, latency, rollouts, and human scores, bound back to cube heads or request digests.

## Scenario capsules

A useful next evaluation artifact is a **scenario capsule** containing:

- one seed cube and known head;
- campaign/player/narrator bindings;
- a scripted sequence of exact player messages;
- role-specific allowed inputs;
- expected acceptance/refusal classes;
- invariants that must remain true;
- optional hidden assessor notes outside model-readable paths;
- model/provider/run metadata templates;
- human rating forms for coherence, agency, restraint, surprise, fairness, and prose; and
- deterministic verification commands.

Scenario capsules could answer questions more rigorously than demonstrations:

- Does the model start correctly from “Will you DM?” without repository confusion?
- Does it preserve exact input and source bindings?
- Does a narrator leak hidden world identifiers or motives?
- Does a proposal builder add unnecessary facts?
- Does a verifier catch stale or grant-widening proposals?
- Does role separation improve leakage and serialization error rates?
- Does retcon planning improve narrative quality relative to a fixed-state or ungoverned baseline?
- Does the same architecture help scientific hypothesis maintenance without overstating evidence?

The cube can make the walk exact. It cannot make subjective scoring objective; those ratings need explicit provenance and inter-rater design.

## Evaluation matrix

A serious comparison should cross at least four axes:

| Axis | Conditions |
|---|---|
| Host | chat-only, human bridge, workspace, orchestrated |
| Context | monolithic, audience/planner split, four-role split |
| Planning | fixed hidden state, ungoverned retcon, Lacuna-governed plural state |
| Model | multiple providers/versions and at least one deliberately weaker model |

Mechanical outcomes should be separated from aesthetic outcomes.

Mechanical measures include:

- successful one-message routing;
- packet identity preservation;
- invalid-operation/refusal rate;
- hidden-context leakage;
- unnecessary semantic mutation rate;
- stale-head recovery;
- reproducible verification;
- exact transcript/digest correspondence; and
- cost/latency/context size.

Human measures include:

- coherence;
- perceived agency;
- surprise without contradiction;
- mystery fairness;
- character continuity;
- meaningful unresolved ambiguity;
- prose quality; and
- whether adaptive reinterpretation feels earned rather than rubbery.

No single score should collapse these categories. In particular, explanatory flexibility and causal agency must remain separate.

## Science-oriented interpretation

The same role split can be recast:

- **planner:** compares competing hypotheses under privileged working material;
- **reporter/narrator:** writes only from disclosed observations;
- **proposal builder:** serializes claims, sources, confidence, unknowns, and requested tests;
- **verifier:** checks provenance and whether conclusions outrun evidence;
- **coordinator:** accepts the mutation.

This may help with reproducible scientific assistance, but Lacuna does not provide theorem proving, calibrated Bayesian inference, causal identification, laboratory instrumentation, or peer review. Its contribution is inspectable custody: which hypotheses existed, which evidence was available to whom, what changed, and what was accepted.

## Provider research snapshot

Revision 0154 uses current public provider mechanisms without pinning model names:

- OpenAI Codex repository instructions and custom subagents: <https://developers.openai.com/codex/guides/agents-md> and <https://developers.openai.com/codex/subagents>
- Claude Code memory and project subagents: <https://code.claude.com/docs/en/memory> and <https://code.claude.com/docs/en/sub-agents>
- Gemini CLI context files and subagents: <https://geminicli.com/docs/cli/gemini-md/> and <https://geminicli.com/docs/core/subagents/>
- ChatGPT Projects and custom GPT guidance: <https://help.openai.com/en/articles/10169521-using-projects-in-chatgpt> and <https://help.openai.com/en/articles/8554397-creating-a-gpt>

These interfaces may change faster than Lacuna’s exchange schemas. Provider files should fail down to the portable `workspace` path rather than becoming authority themselves.

## What revision 0154 establishes

- A fresh model no longer needs to infer the bootstrap ritual.
- A DM utterance is explicitly routable without becoming in-world evidence.
- Capability claims are separated from product branding.
- A conversation-only model has an honest, usable fallback.
- A workspace model receives exact commands and file handoffs.
- An orchestrator receives least-context roles and parent-only commit rules.
- The response template is safe for literal execution.
- Readiness includes deterministic verification and active role checks.
- Exact input is protected by an executable fail-closed guard.
- The accepted narration path matches the actual receipt shape.
- Provider-native configuration is present but explicitly non-authoritative.
- The cube is documented as a possible experimental context curriculum.

## What remains open

- a first-class scenario-capsule schema and runner;
- an action/MCP bridge for ordinary ChatGPT sessions;
- exact transcript sidecar custody and redaction policy;
- model/provider/version/run receipts;
- automatic audience-safe plan scrubbing;
- semantic narration-to-claim extraction and disclosure checking;
- automatic world proposal, rollout, scoring, resampling, and compression;
- hard provider-independent subagent isolation;
- empirical evidence that the four-role split improves outcomes;
- a usability study with players who did not help design Lacuna;
- a direct Gwern-facing demonstration package with short reproducible experiments.

## Working conclusion

Lacuna now has a credible answer to “Can another model actually enter this?” The answer is conditional but operational: yes through a workspace/bridge; yes as explicitly chat-only play without one; and yes with bounded subagents when the provider can enforce or at least respect the handoffs. The next scientific step is not another grand prompt. It is a small set of reproducible scenario capsules that expose the same cube path to several models and measure both mechanical integrity and narrative value.
