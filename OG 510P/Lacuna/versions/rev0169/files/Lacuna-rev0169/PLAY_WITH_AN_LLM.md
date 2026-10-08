# Play Lacuna with an LLM

A player should be able to say **“Will you DM?”** and begin. The player does not manage packets, schemas, task cards, agents, hashes, or commits. The host does.

Players can stop here and use [`PLAY_NOW.md`](PLAY_NOW.md). Researchers evaluating the retcon-planning claim can start with [`FOR_GWERN.md`](FOR_GWERN.md).

The shortest shell-capable entrance is:

```bash
./lacuna play start .lacuna-play \
  --bootstrap \
  --profile orchestrated \
  --format markdown
```

The command treats the default sentence as `session-control`, safely creates or selects a campaign, opens one resumable turn run, and prints the audited next action. It does not invoke a model or claim that narration has happened.

Players can use [`PLAY_NOW.md`](PLAY_NOW.md). Read [`OPERATE_LACUNA.md`](OPERATE_LACUNA.md) for the shortest capability-first operator entrance and [`docs/operators/ONE_SENTENCE_START.md`](docs/operators/ONE_SENTENCE_START.md) for the complete one-page play procedure.

## Pick the path from capabilities

| Host surface | Begins from one sentence | Durably updates a cube without a human bridge | Recommended path |
|---|---:|---:|---|
| Ordinary ChatGPT or another conversation-only model | Yes | No | Chat-only play |
| Project/custom instructions and uploaded files only | Yes | No | Chat-only or human bridge |
| ChatGPT connected to a Lacuna Action/App/API host | Yes | Yes | Narrow connected-host run API |
| Codex or another shell-capable workspace model | Yes | Yes | `play start`, then `NEXT.md` |
| Claude Code, Gemini CLI, or another subagent-capable host | Yes | Yes | Orchestrated run plus provider dispatch |
| Human operating the CLI while an LLM supplies returns | Yes | Yes | Human paste bridge |

Choose by actual shell, storage, connector, and worker capabilities—not by subscription or product name.

An uploaded repository can teach a model the rules. It does not by itself grant access to the user’s durable local campaign.

## What the player experiences

After “Will you DM?”, the configured host should:

1. route the sentence as session control rather than an in-world deed;
2. reuse the selected campaign or create a reversible low-commitment default when explicitly allowed;
3. begin promptly instead of teaching the protocol;
4. ask at most one bundled preference question when no premise or preference exists;
5. treat later player wording as an utterance, choice, request, or attempt—not automatic proof of success;
6. preserve experienced facts while keeping unused hidden explanations plural; and
7. show narration only after a durable host receives a passing commit receipt.

The player never needs to choose a world ID, schema, topology, role, or recovery command.

## The run loop

After `play start`, copy the run path and read:

```bash
cat RUN_PATH/NEXT.md
```

For a delegated stage, generate a self-contained handoff:

```bash
./lacuna turn run dispatch RUN_PATH \
  --provider chatgpt \
  --format markdown
```

Use `codex`, `claude-code`, `gemini-cli`, or `portable` for another route. The dispatch embeds the complete exact task card; a chat worker does not need local file access and should not infer omitted context.

Save the worker’s one exact JSON object and advance:

```bash
./lacuna turn run accept RUN_PATH MODEL_RETURN.json --format markdown
```

Repeat until the parent-owned commit action appears:

```bash
./lacuna turn run commit RUN_PATH --format json
```

Only a passing `60-turn-receipt.json` makes its top-level narration player-visible.

## One model or several

`auto` is a deterministic routing policy, not a claim that more agents are always better.

| Mode | Context walk | Best default use |
|---|---|---|
| `solo` | parent proposal | Conversation-only bridge, trivial turn, or constrained host |
| `pair` | planner → audience-only narrator → parent proposal | Ordinary director turn |
| `full` | planner → narrator → proposal builder → verifier | Anchor, revision, repair, conflict, or debt-sensitive turn |

The important boundary is information flow, not agent count. The narrator receives audience context plus approved observable beats, not planner context, hidden-world weights, private rationale, candidate operations, or unrevealed openings.

A provider with native subagents can invoke each generated dispatch in a bounded worker. A provider without them can use separate role-dedicated conversations or serialize the work in one parent, while being honest that this is weaker isolation. The parent alone accepts artifacts and commits.

## Backstage checkpoint: hidden explanations without rubber reality

The player does not ask for or operate a checkpoint. Between audience-facing turns, a connected parent may decide that several hidden explanations should be compared before one becomes expensive to revise. It opens one managed run, which freezes a separate `lacuna.turn-request.v4` checkpoint, fixed per-role provider routes, exact resume state, and ordered invocation custody before walking four exact role cards:

```text
generator: several distinct explanations + exact bounded rollout beats
    → judge: provenance-stripped candidate view + fixed rubric
    → compressor: selected candidate only + bounded state card
    → verifier: proposal-visible anti-rubber-reality review
    → parent: raw-chain validation, kernel rehearsal, commit/recovery
```

The cube does not merely say “consider alternatives.” It preallocates the exact candidate slots, preallocates one beat per requested rollout turn, removes generator provenance from the judge view, checks every weighted score, selects deterministically, and refuses operations that would publish hidden state, erase an unknown, reweight worlds from aesthetics, or harden a latent assignment.

Start the managed path with:

```bash
./lacuna checkpoint run begin CUBE \
  --root .lacuna-checkpoint-runs \
  --trigger "Compare bounded explanations before the next reveal." \
  --provider chatgpt --format markdown
```

Then follow only the checkpoint run's `NEXT.md`, render `checkpoint run dispatch`, save one exact JSON return, and invoke the generated `accept` command. A failed provider or worker attempt can be recorded without advancing. A tool-capable ChatGPT or native-subagent host can use four role contexts. A human can paste each generated dispatch into separate chats. One model can execute the cards serially when no workers exist, but the host must not call that independent judging.

After a committed checkpoint, the clean information-bottleneck condition adds a fifth boundary: run `checkpoint run next-turn` with the exact next player input, create a new narrator context, and give it the complete generated continuation dispatch. The dispatch binds the authenticated compact state to one audience-only solo turn and its exact proposal template. Optional public-history custody can carry exact player-visible prose without carrying rejected futures. Prefer `history complete CHECKPOINT_RUN --run-root TURN_RUNS` for a ledger-censused completeness claim; use `history build` only for an explicit possibly partial list. Continuing in the old context remains a valid serial control but cannot demonstrate forgetting. The complete procedure is [`docs/operators/CHECKPOINT_RUNS.md`](docs/operators/CHECKPOINT_RUNS.md), [`docs/operators/FRESH_NARRATOR.md`](docs/operators/FRESH_NARRATOR.md), and [`docs/operators/PUBLIC_HISTORY.md`](docs/operators/PUBLIC_HISTORY.md); the stateless substrate is [`docs/operators/CHECKPOINTS.md`](docs/operators/CHECKPOINTS.md).

## Ordinary ChatGPT

Add [`integrations/chatgpt/PROJECT_INSTRUCTIONS.md`](integrations/chatgpt/PROJECT_INSTRUCTIONS.md) to a Project or custom GPT. A player can then simply ask for a DM.

Without a connected host, ChatGPT should say once:

> We can play immediately; this chat is not yet committed to a Lacuna cube.

Then it begins. It must not claim that project files, an uploaded ZIP, or a subscription changed a local campaign.

For durable play, use the human bridge in [`docs/operators/CHATGPT.md`](docs/operators/CHATGPT.md), a shell-capable host, or a narrow connected integration. For role-separated work, paste the output of `turn run dispatch --provider chatgpt`; do not invent a prompt from a path-only pointer. For the clean post-checkpoint condition, use a new non-project-shared narrator context where practical and record whether Custom Instructions, memory, or linked conversation state were active.

## Research comparison is not part of play

A player never needs a scenario capsule or bundle. Those commands are for an experiment owner comparing DM configurations after the ordinary one-sentence entrance already works. A `scenario bundle` preregisters several exact four-condition blocks, optionally requires externally retained commitment receipts, keeps each completed block blind, and unblinds all blocks together. A shell-capable parent, connected ChatGPT host, or human bridge follows the bundle's generated `NEXT.md`; individual workers receive only the active child driver or rating form. Each child also preregisters operator-only and filesystem-only contamination canaries and freezes one private scan before blind rating; the complete driver and canary bodies must not be forwarded to nested role workers or raters. See [`docs/operators/SCENARIO_BUNDLES.md`](docs/operators/SCENARIO_BUNDLES.md) and [`docs/operators/CONTAMINATION_CANARIES.md`](docs/operators/CONTAMINATION_CANARIES.md).

## What the datacube is doing

The cube does not ask a model to remember every distinction in prose. It manufactures the exact context walk:

```text
exact input + typed kind
        ↓
source-bound packet and authority grant
        ↓
deterministic topology
        ↓
least-context task card embedded in a dispatch
        ↓
exact role return bound by digest
        ↓
parent proposal and optional verifier
        ↓
exact rollback kernel preparation
        ↓
durable commit receipt
        ↓ checkpoint boundary when used
fresh continuation dispatch → new narrator context → exact ordinary turn proposal
```

That same pattern can support fiction, simulations, and scientific workflows where private hypotheses, public observations, model suggestions, and accepted records must remain distinct. Lacuna supplies custody and context manufacture; it does not prove the worker reasoned correctly.

## What success proves

A fluent scene proves that a model produced text. A self-contained dispatch proves that the host rendered one complete role input. A passing run audit proves local artifact and topology consistency. A verifier `pass` remains advisory. A passing receipt proves that the kernel accepted the exact prepared proposal at the expected historical boundary.

None of those alone proves narrative quality, provider identity, hard context isolation, objective truth, or mystery fairness.

Continue with [`docs/operators/FRESH_NARRATOR.md`](docs/operators/FRESH_NARRATOR.md), [`docs/operators/PUBLIC_HISTORY.md`](docs/operators/PUBLIC_HISTORY.md), [`docs/design/THREE_SERIOUS_QUESTIONS.md`](docs/design/THREE_SERIOUS_QUESTIONS.md), [`docs/operators/TURN_RUNS.md`](docs/operators/TURN_RUNS.md), [`docs/operators/CHECKPOINT_RUNS.md`](docs/operators/CHECKPOINT_RUNS.md), and [`docs/operators/MULTI_AGENT.md`](docs/operators/MULTI_AGENT.md).
