# Three serious questions about Lacuna

This note answers the three questions that determine whether Lacuna is merely an interesting repository or a useful research artifact and playable system.

1. Does Lacuna answer a real part of Gwern’s retcon-planning argument well enough to be a useful gift?
2. Can an ordinary player—especially someone using ChatGPT rather than a local coding agent—simply say “Will you DM?” and begin?
3. Can different frontier-model hosts, including subagent-capable systems, enter the cube without being expected to infer an unwritten orchestration protocol?

The answers are **yes, with sharply different meanings of yes**. Lacuna is a serious custody substrate and now includes an executable, managed, source-bound retcon-checkpoint adapter. It supports a one-sentence player entrance. It is not a story-generating model, universal ChatGPT filesystem bridge, proof of worker independence, or proof that multi-agent play is better.

## 1. Is this a useful gift to Gwern?

### The strongest honest answer

Lacuna is useful to Gwern **not as an implementation of the entire proposed creative-writing loop, but as an executable answer to its most dangerous systems question**:

> How can hidden state remain revisable without allowing observed reality, exposed consequences, or mystery evidence to become rubber?

Gwern’s June 2, 2026 essay, “Better Fiction via Retcon Planning,” proposes a loop of observed canon, soft hypotheses, checkpoint resampling, candidate selection, compression, and forgetting. It explicitly identifies the main danger as “rubber reality” and says retcon planning needs a commitment budget: observed canon fixed, exposed consequences expensive to revise, unused hidden state cheap. Source: <https://gwern.net/blog/2026/llm-retcon>.

That is exactly the part of the proposal that cannot safely be left to one prompt. A prompt can tell a model to remember canon, preserve clues, and revise only hidden state; it does not create typed custody, stale-head refusal, consequence lineage, replay, or an inspectable distinction between what the player observed and what a planner merely preferred.

Lacuna makes those distinctions executable.

### Mapping the argument to the cube

| Retcon-planning concern | Lacuna answer | Status |
|---|---|---|
| Preserve what the player actually observed | Provenance-bearing assertions, audience visibility, source-bound turn input, accepted narration receipt | Implemented |
| Keep hidden state soft and plural | Candidate worlds, world assignments, commitment levels, particle weights labelled as planner attention rather than truth | Implemented |
| Do not silently canonize a selected explanation | Selection and weight are separate from assertion, anchor, and commitment authority | Implemented |
| Make exposed consequences costly to rewrite | Explicit consequence links, revision-impact reviews, commitment burden, reviewed forward replacement | Implemented |
| Protect mystery evidence from retroactive cheating | Fair-play seals, visibility boundaries, source custody, explicit disclosures | Implemented, with limited witness claims |
| Prevent hidden rationale from leaking into prose | Audience/planner projections plus generated least-context narrator cards | Implemented |
| Walk through exact context over several model calls | Request-scoped turn runs plus managed checkpoint runs with fixed per-role routes, exact self-contained dispatch, ordered accepted/failed invocation custody, deterministic next action, pointer-only recovery, parent review, and exact commit recovery | Implemented in rev0160 |
| Generate several alternative future arcs | Generator card preallocates the exact candidate count and fixes horizon, protected canon/unknowns, risk fields, one explicit rollout beat per horizon turn, and provenance contract | Interface implemented; model quality external |
| Score candidates for coherence, agency, payoff, novelty, coincidence | Provenance-blind judge card fixes dimensions/weights, checks arithmetic and disqualifiers, and applies deterministic winner/tie rule | Interface implemented; validity/calibration external |
| Compress a winning rollout into an optimized checkpoint card | Compressor card enforces winner-only input, exact unknown preservation, byte budget, and narrow hidden-state operations; assembly retains the exact artifact | Mechanically implemented; artistic optimality external |
| Forget rejected rollouts while retaining reproducible experiment custody | Downstream cards omit rejected rollouts while private artifacts retain exact digest custody | Implemented as context omission, not destructive deletion |
| Produce evidence that the method improves fiction | Scenario runner and comparative human study still required | Not implemented |

This is a good division of labor. Generation and aesthetic selection are model/application policy and will change quickly. Custody, authority, provenance, visibility, commitment, and refusal are durable infrastructure concerns.

### What the gift actually gives

A recipient can inspect and run a reference implementation of several claims that otherwise remain easy to hand-wave:

- “Observed canon is fixed” becomes source and assertion custody, not a reminder in a system prompt.
- “Hidden facts become expensive as consequences accrue” becomes an inspectable impact review and explicit repair obligation.
- “Unused hidden state stays cheap” becomes tentative world assignment rather than one silently privileged truth database.
- “A mystery cannot keep changing its culprit after clues are inspected” becomes a separation between hidden hypotheses, disclosed assertions, and optional precommitted secret openings.
- “Compress and forget” becomes an authenticated post-checkpoint narrator capsule plus a fresh continuation context, rather than copying an entire hidden transcript—or leaving the old narrator’s memory intact.
- “The system can run across many model calls” becomes a filesystem state machine whose next owner, complete input artifact, expected schema, and next command are generated by the cube.
- “Compare, score, and compress several explanations” becomes a source-bound generator → provenance-blind judge → compressor → verifier walk with parent-only assembly, review, and commit.

The gift is therefore best described as a **governance substrate and experimental reference implementation for retcon planning**, not “we proved retcon planning works.”

### Does it target real concerns, or adjacent concerns?

It targets the essay’s central caveat directly. The commitment-budget paragraph is not incidental; it determines whether backward reinterpretation produces flexible storytelling or destroys causality and fair play. Lacuna’s strongest mechanisms—commitment levels, consequence custody, revision review, fair-play seals, plural worlds, audience/planner separation—are all responses to that paragraph.

It also targets two implicit engineering problems:

1. **A model cannot reliably distinguish its private hypothesis from public canon merely because both appear in one context window.** Lacuna manufactures asymmetric cards instead of asking a coordinator to redact by intuition.
2. **A checkpoint process needs durable identity across calls.** Packet, task, upstream-return, proposal, and verifier digests prevent accidental cross-turn reuse and edited handoffs.

Those are real prerequisites for a serious experiment. Revision 0159 specified the exact model-facing candidate, judgment, compression, verifier, review, and receipt artifacts. Revision 0160 turns that exchange into one strict resumable run with fixed routes and invocation custody; the workers still supply the creative and evaluative content.

### The remaining experiment

The most valuable next research artifact is a scenario-capsule runner with at least four conditions:

| Condition | Hidden-state policy | Context topology |
|---|---|---|
| Forward-only baseline | One continuing planned world | One model context |
| Prompt-only retcon | Periodic generate/score/compress instructions in prose | One model context |
| Lacuna checkpoint serial | Same source-bound cards, rubric, and commit boundary | One model executes generator → judge → compressor → verifier serially |
| Lacuna checkpoint separated | Same custody and cards | Role-dedicated generator → judge → compressor → verifier contexts; parent commits |

Every condition should receive the same seed, scripted player departures, model family, and evaluation budget. Mechanical measures should be separated from human ratings.

Mechanical measures can include contradiction/refusal counts, stale-artifact detection, hidden-state leakage, unsupported-success assertions, commitment/consequence repair burden, candidate diversity, context size, latency, and cost. Human raters can separately judge coherence, agency, character believability, genre fit, payoff, novelty, coincidence, mystery fairness, and seam visibility.

A successful study may show that some Lacuna machinery is unnecessary, that `pair` beats `full`, or that the custody benefits are real while prose quality remains unchanged. Those are useful results. The system is designed to make such ablations possible rather than assume its own success.

## 2. Can a player just say “Will you DM?”

### The player-level answer

**Yes.** “Will you DM?” is a complete play request. A configured host should route it as session control, begin or resume a campaign, and avoid teaching the player the ledger protocol.

The important distinction is between **starting play** and **durably committing play to a Lacuna cube**.

| Surface | Can begin a scene from one sentence? | Can update the durable cube by itself? |
|---|---:|---:|
| Ordinary ChatGPT chat | Yes | No |
| ChatGPT Project with instructions/files | Yes | No, unless a connected host is provided |
| Custom GPT or ChatGPT app/action connected to a Lacuna host | Yes | Yes |
| Human paste bridge between ChatGPT and the CLI | Yes | Yes, with the human performing the bridge |
| Codex, Claude Code, Gemini CLI, or another shell-capable repository agent | Yes | Yes |

A Project can keep chats, files, and project instructions together, and project memory can support continuity. That still does not mean an uploaded repository is the user’s durable local campaign or that the chat can execute `./lacuna`. OpenAI’s current Projects documentation describes files, project instructions, memory, and connected apps; the local host question remains separate. Source: <https://help.openai.com/en/articles/10169521-projects-in-chatgpt>.

### What ChatGPT should do after the sentence

A properly configured ChatGPT should:

1. recognize play intent rather than answer with installation instructions;
2. say once, only when no bridge exists, “We can play immediately; this chat is not yet committed to a Lacuna cube”;
3. ask at most one bundled preference question if there is no premise at all;
4. otherwise open a reversible, low-commitment situation promptly;
5. treat the player’s wording as an utterance, choice, request, or attempt—not automatic proof of physical success;
6. preserve experienced facts while keeping unused hidden explanations plural;
7. keep JSON, task cards, IDs, stale-head repair, and subagent routing backstage.

The player does not need to know what a claim, world, grant, packet, or receipt is.

### The practical ChatGPT setup

For an ordinary Project or custom GPT:

1. Put `integrations/chatgpt/PROJECT_INSTRUCTIONS.md` in the instruction field.
2. Add `PLAY_WITH_AN_LLM.md`, `docs/operators/CHATGPT.md`, and the relevant campaign material as Project sources.
3. Add the supplied conversation starter: “Will you DM? Start immediately with a low-commitment scene. Do not explain the machinery unless I ask.”
4. Decide whether the session is chat-only, uses a human bridge, or has a connected Lacuna action/app.
5. Let the player speak normally.

This gives a reliable narrative entrance. Governed persistence requires the additional bridge described in `docs/operators/CHATGPT.md`.

### The human bridge is now one resumable run, not a pile of guessed files

The human saves the exact player message, then begins a solo run:

```bash
./lacuna turn run begin .lacuna-play \
  --root .lacuna-runs \
  --player-input-file player-message.txt \
  --director --mode solo --format markdown
```

The generated run directory contains `NEXT.md`. It names one complete input artifact, one expected return schema, and one exact accept command. The human pastes that artifact into ChatGPT, saves ChatGPT’s JSON response, and executes the command. When the run says `ready-to-commit`, the human runs:

```bash
./lacuna turn run commit RUN_PATH --format json
```

Only the passing receipt’s top-level `narration` is treated as having occurred. `ready-to-commit` means the exact proposal passed a local kernel preview; it is still not a commit or head reservation.

This is deliberately usable by someone who does not understand the internal chain. The run itself tells them what is next.

### What “just jump in” cannot honestly mean

It cannot mean that a generic web chat silently edits arbitrary files on a user’s computer. It cannot mean that an uploaded ZIP is a durable campaign host. It cannot mean that a fluent response was committed. It cannot mean that ChatGPT Pro, by subscription label alone, exposes the same project-scoped custom subagent mechanism as Codex.

The correct promise is stronger because it is precise:

> The player can always jump into play. A configured tool-capable or connected host can also jump directly into governed persistence. An unconnected chat can use the same play behavior and later cross the human or application bridge without pretending it already did.

## 3. How should different LLM configurations enter and use subagents?

### Capability first, vendor name second

Lacuna uses three portable profiles:

| Profile | Actual capability | Default topology | Persistence |
|---|---|---|---|
| `chat` | Read pasted material and return text/JSON | Solo model plus human bridge | Human or connected host commits |
| `workspace` | Read repository, run CLI, read/write files | `solo` | Parent model commits |
| `orchestrated` | Workspace capabilities plus bounded role contexts | `auto` → `solo`, `pair`, or `full` | Parent coordinator commits |

A host should downgrade honestly:

```text
connected orchestrated host
        ↓ no subagents
connected single-workspace host
        ↓ no local tools
human paste bridge
        ↓ no bridge desired
chat-only play
```

The protocol does not disappear as capability decreases. Only the degree of automation and isolation changes.

### The cube should not merely suggest “consider using subagents”

Weak orchestration prompts fail because they require the parent to invent all of the following:

- whether this turn deserves one, two, or four role calls;
- which role owns the next step;
- exactly what context that role may see;
- what filename/schema comes back;
- how the next call binds to earlier output;
- who may commit;
- what happens after a refusal.

Rev0157 moved ordinary-turn decisions and the final commit envelope into generated artifacts:

1. `model brief` states the capability contract and provider role aliases.
2. `turn run begin` creates one collision-resistant, request-scoped directory.
3. `run.json` records the selected topology and exact state.
4. `NEXT.md` says who owns the next action, names the complete card, names the required schema, and prints the accept command.
5. `turn run dispatch` can translate the current delegated action into one provider-specific envelope with the exact card digest, alias, return schema, save path, and parent-only accept command.
6. Each task card is the complete prompt envelope for that role.
7. `turn run accept` validates the return and manufactures the next card.
8. Before readiness, the kernel executes the exact proposed mutation in a rolled-back transaction and freezes its IDs, event chain, receipt, and post-state contexts.
9. Only `turn run commit` can persist that envelope. Commit and recovery re-derive authority from the immutable request source rather than trusting the editable preparation.
10. Rerunning commit can recover the exact already-committed change without duplication even after later valid ledger writes, provided the historical request-head prefix and durable event chain still verify exactly.

The generated `NEXT.md` explicitly names current checked-in role aliases:

| Portable role | Codex | Claude Code | Gemini CLI | ChatGPT |
|---|---|---|---|---|
| `lacuna-planner` | `lacuna_planner` | `lacuna-planner` | `lacuna-planner` | role-dedicated planner chat/call |
| `lacuna-narrator` | `lacuna_narrator` | `lacuna-narrator` | `lacuna-narrator` | role-dedicated narrator chat/call |
| `lacuna-proposal-builder` | `lacuna_proposal_builder` | `lacuna-proposal-builder` | `lacuna-proposal-builder` | role-dedicated builder chat/call |
| `lacuna-verifier` | `lacuna_verifier` | `lacuna-verifier` | `lacuna-verifier` | independent verifier chat/call |

This does not force a provider to comply, but it greatly reduces the amount of protocol the coordinator must infer.

Rev0159 applied the same principle to the exact retcon-planning concern by defining the source-bound cards and return chain. Rev0160 makes that chain an authoritative managed walk. `checkpoint run begin` freezes one protected-state boundary and source-backed least-authority grant, binds the exact open cube path, fixes all four provider routes, and writes one audited manifest. `checkpoint run dispatch` then emits the complete current prompt whose identity is a deterministic function of request, role, and ordered upstream digests:

| Checkpoint role | Codex | Claude Code | Gemini CLI | ChatGPT |
|---|---|---|---|---|
| `lacuna-retcon-generator` | `lacuna_retcon_generator` | `lacuna-retcon-generator` | `lacuna-retcon-generator` | generator-only chat/call |
| `lacuna-retcon-judge` | `lacuna_retcon_judge` | `lacuna-retcon-judge` | `lacuna-retcon-judge` | judge-only chat/call |
| `lacuna-retcon-compressor` | `lacuna_retcon_compressor` | `lacuna-retcon-compressor` | `lacuna-retcon-compressor` | compressor-only chat/call |
| `lacuna-retcon-verifier` | `lacuna_retcon_verifier` | `lacuna-retcon-verifier` | `lacuna-retcon-verifier` | verifier-only chat/call |

The managed run does more than suggest delegation. Its single `NEXT.md` names the current role, fixed provider route, complete card, expected schema, and exact parent command. The parent can record a failed invocation without advancing, or accept one exact return and let Lacuna manufacture the next card. This makes subagent use more likely and gives the parent the right tool handoff, but cannot force a product to create subagents or prove that the declared model ran. A one-context fallback remains valid with an explicit no-isolation/no-independence caveat. The normal walk is `docs/operators/CHECKPOINT_RUNS.md`; `docs/operators/CHECKPOINTS.md` documents the lower-level stateless exchange.

### Current provider entrances

- **Codex:** project custom agents can live under `.codex/agents/*.toml`, with project orchestration settings in `.codex/config.toml`; individual agents can be configured read-only. Source: <https://developers.openai.com/codex/subagents>.
- **Claude Code:** project subagents can live under `.claude/agents/`, with frontmatter controlling tools and other behavior. Source: <https://code.claude.com/docs/en/sub-agents>.
- **Gemini CLI:** project custom agents can live under `.gemini/agents/*.md`; tool lists and isolated context loops can constrain role access. Source: <https://geminicli.com/docs/core/subagents/>.
- **ChatGPT:** Projects/custom GPTs are strong instruction and continuity surfaces. Role-separated calls can be performed through dedicated chats, API calls, or a connected app/action, but the host must not claim local execution or hard subagent isolation that the actual surface does not provide.

Provider files are discovery adapters. The generated card is the turn-specific prompt. The packet grant and kernel receipt are the authority boundary.

### Are two agents especially important?

Often, yes—but not because two models are automatically smarter.

The `pair` topology separates the two contexts whose accidental mixing is most dangerous:

1. a privileged planner compares hidden explanations and decides what may become observable;
2. an audience-only narrator writes from the approved observable plan without seeing private rationale, candidate operations, world IDs, or weights.

That split directly addresses hidden-state leakage and rubber-reality narration. It is likely the highest-value multi-agent configuration for ordinary fiction.

`full` adds a proposal builder and verifier. It is appropriate when a turn carries anchor authority, revision/repair pressure, particle reconciliation, confidentiality sensitivity, or when an experiment specifically tests role separation. It is not automatically better; every extra boundary adds cost and another chance for mismatch.

`solo` remains correct for audience-only, trivial, or narration-only turns.

### Why this matters for science

The same topology can separate private hypothesis work from public evidential reporting:

| Fiction role | Scientific analogue |
|---|---|
| Planner | hypothesis generator/comparator with privileged working context |
| Narrator | evidence-facing reporter that states only what observations support |
| Proposal builder | serializer of claims, sources, uncertainty, and unresolved questions |
| Verifier | independent provenance, leakage, authority, and overclaim checker |
| Parent | experiment coordinator or accountable human who accepts the record |

This can support controlled tests of monolithic versus separated reasoning, identical cards across providers, blinded reporting, or removal of privileged hypotheses from an observation-facing worker.

It does not make a panel true. It makes information flow, provenance, and responsibility inspectable.

## Long-run design consequences

The following design principles should shape future cube work:

- **The datacube is an executable context compiler and curriculum.** It should create the exact slice a role needs, retain the join keys and invocation custody, and generate the next allowed step rather than ask the role to search the whole cube.
- **Every multi-call walk needs a durable join key.** Packet, task, and upstream digests should survive separate processes, chats, and providers.
- **The next step should be generated, singular, and testable.** A weaker model should not choose among five vaguely described workflows.
- **Subagents are an information-flow mechanism.** The value is context asymmetry, tool restriction, and independent checking—not agent count.
- **Provider-specific files should remain thin.** They name/discover roles; they should not become a second authority system.
- **Chat-only must remain a first-class downgrade path.** Narrative play should not fail merely because local execution is absent.
- **Connected hosts should expose narrow Lacuna operations.** They should not hand arbitrary mutation tools or secret opening files to the model.
- **Science and fiction should share custody primitives but not evaluation claims.** Provenance and commitment can be common; narrative quality and scientific validity require different external evaluators.

## Acceptance questions for future revisions

A future release should be able to answer yes to all of these:

- Can a fresh tool-capable model see “Will you DM?” and enter play without editing the repository?
- Can an ordinary ChatGPT user start immediately and understand, in one sentence, whether the session is durably connected?
- Can a human bridge follow one generated next action at a time without learning CLI topology?
- Can a subagent-capable parent see an explicit provider role name and complete card rather than infer a prompt?
- Can repeated invocations resume from the run directory alone?
- Does every delegated role lack commit authority?
- Does the narrator receive no privileged planner packet by construction?
- Does a stale, cross-turn, wrong-role, edited, or placeholder artifact fail closed?
- Does the final player-visible text come only from a passing receipt?
- Can a recipient run an exact generator → judge → compressor → verifier checkpoint without inventing prompts or giving workers commit authority?
- Can the recipient clearly distinguish implemented artifact governance from external model quality, independence, and comparative efficacy?

Rev0160 makes the checkpoint question operational for a recipient who knows only how to follow one generated next action. Rev0161 and rev0162 deliver the randomized comparative child and preregistered replicated parent. Rev0163 closes the causal gap by making fresh capsule-bound continuation the role-separated treatment. Rev0164 closes the operator gap by binding that capsule, the exact next player input, optional public history, and one narrow ordinary turn into a single validated dispatch. The next meaningful milestone is a completed multi-provider study with retained null or negative results, masking checks, capsule/context canaries, and provider-conformance evidence—not a broader worker grant.

## Rev0164 resolution: make the bottleneck, next turn, and public continuity non-retconable

1. **Gift to Gwern:** the cube runs an exact four-way comparison that can report a negative result, and the replicated bundle fixes every block, assignment, inclusion rule, and endpoint before outcomes. Optional external retention applies anti-retcon custody to the experiment itself.
2. **Can a daughter just play with ChatGPT?:** yes. “Will you DM?” remains the complete player entrance. Single scenarios and replicated bundles are explicitly backstage, with chat-only, human-bridge, and connected-host routes kept separate from play.
3. **Different LLM and subagent configurations:** serial and role-separated contexts are now causally sharper treatments. Serial keeps one declared context across narration and checkpoint work. Role-separated uses four fresh checkpoint-role contexts, then runs `checkpoint run next-turn` and starts a new narrator segment from one source-bound continuation dispatch. Optional public-history custody follows the same preregistered policy across conditions. A bundle parent gets one exact handoff and return contract at each stage.

The key design move is to stop asking a model to infer either the workflow or the experiment schedule. `run.json.next_action`, parent `bundle.json`, `NEXT.md`, the active driver, exact return template, role aliases, witness gate, block seal, and parent command turn the datacube into a repeated context curriculum across CLI invocations. See [`../operators/SCENARIO_CAPSULES.md`](../operators/SCENARIO_CAPSULES.md) and [`../operators/SCENARIO_BUNDLES.md`](../operators/SCENARIO_BUNDLES.md).


## The fresh-narrator boundary

The parent may remain long-lived because it owns routing, validation, sidecar custody, and commit. The creative narrator is the component that must cross the information bottleneck. After a committed checkpoint, the parent runs `checkpoint run next-turn` with the exact next player input, opens a genuinely fresh narrator context, and supplies only the resulting validated continuation dispatch. Same-chat continuation is still supported for ordinary play and for the persistent-context controls; it must not be described as evidence that compression or forgetting caused the result.

## Rev0165 resolution: test the boundary that product labels cannot prove

The clean retcon experiment cannot rely on “new chat,” “subagent,” or “read-only” as evidence of isolation. Rev0165 preregisters operator-context and filesystem-only canaries for every cell, scans the exact frozen experiment-artifact boundary before blind rating, and carries every clean or leaked result through block sealing and aggregate export. The complete driver remains private coordinator context; nested generator, judge, compressor, verifier, narrator, and rater workers receive only their generated least-context artifacts.

This serves Gwern by turning the context-window objection into a falsifiable protocol outcome, serves a player by leaving the one-sentence DM path untouched, and serves weaker coordinators by giving them one command and one explicit interpretation instead of asking them to improvise a leakage audit. A clean scan still is not a provider attestation or proof of forgetting.

## Rev0165 addendum: complete local history is not an operator adjective

Rev0164 could authenticate every turn the operator named, which was necessary but not enough for a controlled fresh-narrator comparison. Rev0165 separates an explicit list from a complete local claim. In complete mode, the committed checkpoint supplies the cutoff, the ledger supplies every expected durable play-purpose request/proposal for the audience, and retained managed runs supply the exact prose bodies. Any missing or duplicate join refuses. The continuation then says exactly which public-context mode the narrator received.

This matters to Gwern because a compact state card cannot be evaluated fairly when one branch silently loses ordinary public prose. It matters to a daughter because the complexity remains backstage: `PLAY_NOW.md` still reduces the player contract to “Will you DM?” It matters to weaker LLMs because “partial,” “complete,” and “typed-only” are machine fields rather than nuances they must infer from a parent’s wording.
