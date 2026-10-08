# ChatGPT operation

## Can a player just say “Will you DM?”

**Yes.** It is a complete request to begin or resume play. It is session control, not character dialogue and not proof that an in-world event occurred.

What happens backstage depends on the actual host:

| Surface | Begins from one sentence | Persists to a durable Lacuna cube by itself |
|---|---:|---:|
| Ordinary ChatGPT conversation | Yes | No |
| Project/custom instructions with files | Yes | No, absent a connected host |
| Connected Action/App/API host | Yes | Yes |
| Human paste bridge | Yes | Yes, with the human operating custody |
| Codex or another shell-capable workspace host | Yes | Yes |

A Project can group chats, files, custom instructions, memory, and supported tools. An uploaded ZIP or subscription tier does not by itself prove access to the user’s durable local campaign or authority to execute `./lacuna`.

Official product references are recorded here because capabilities change:

- Projects: <https://help.openai.com/en/articles/10169521-projects-in-chatgpt>
- GPT capabilities, Apps, and Actions: <https://help.openai.com/en/articles/8554407-gpts-in-chatgpt>
- Creating and configuring GPTs: <https://help.openai.com/en/articles/8554397-creating-and-editing-gpts>
- ChatGPT agent: <https://help.openai.com/en/articles/11752874-chatgpt-agent>
- Temporary Chat: <https://help.openai.com/en/articles/8914046-temporary-chat-faq>
- API conversation state: <https://developers.openai.com/api/docs/guides/conversation-state>
- Workspace agents where available: <https://help.openai.com/en/articles/20001143-chatgpt-workspace-agents-for-enterprise-and-business>
- Codex subagents: <https://developers.openai.com/codex/subagents>

Choose the path from capabilities visible in the current surface. For a clean context-bottleneck experiment, treat Project memory, enabled Custom Instructions, linked API conversation state, and shared readable workspaces as explicit experimental variables rather than assuming the product label isolates them.

## Path A — immediate chat-only play

Put `integrations/chatgpt/PROJECT_INSTRUCTIONS.md` in the Project or custom-GPT instruction field. Add `PLAY_WITH_AN_LLM.md` and this guide as references when useful.

When no connected host or current dispatch exists, ChatGPT says once:

> We can play immediately; this chat is not yet committed to a Lacuna cube.

Then it begins a reversible, low-commitment scene. It should not repeat the disclaimer every turn, expose ledger vocabulary, or claim that local files changed.

The player speaks and acts normally. ChatGPT preserves experienced facts, keeps unused hidden explanations plural, and treats attempted actions as attempts until the fiction establishes an outcome.

## Path B — one-command local start

A human or shell-capable parent starts the governed session:

```bash
./lacuna play start .lacuna-play \
  --bootstrap \
  --profile chat \
  --format markdown
```

Without `--player-input`, the retained sentence is exactly `Will you DM?` and its type is `session-control`.

The command creates or selects the campaign and opens the run. It does not call ChatGPT. Copy the printed run path and follow `NEXT.md`.

## Path C — the human paste bridge

This is the smallest durable path for ordinary ChatGPT.

### Delegated stage

Render a complete ChatGPT handoff:

```bash
./lacuna turn run dispatch RUN_PATH \
  --provider chatgpt \
  --format markdown \
  > chatgpt-handoff.md
```

Paste the complete handoff into ChatGPT. It contains the exact generated task card as `input_document`, so ChatGPT does not need to open the local path named for audit custody.

Ask ChatGPT to perform the named role and return exactly one JSON object. Do not ask it to summarize the envelope. Save the exact object without prose or code fences:

```bash
./lacuna turn run accept RUN_PATH chatgpt-return.json --format markdown
```

Read the new `NEXT.md`. Repeat dispatch and accept for each delegated stage.

### Parent-owned stage

When `NEXT.md` names `parent-coordinator`, the human or connected host reads the named complete artifact, performs the stated review/serialization action, and runs the printed command. The worker never accepts its own return.

### Commit

When status is `ready-to-commit`:

```bash
./lacuna turn run commit RUN_PATH --format json
```

Only after this succeeds may the host present the top-level `narration` from `RUN_PATH/60-turn-receipt.json`.

A malformed, wrong-schema, wrong-turn, placeholder, stale, or digest-inconsistent response is refused. Reissue the current complete dispatch; do not repair IDs or hashes manually.

## Path D — ChatGPT as one bounded role

An orchestrated run may use fresh or role-dedicated ChatGPT contexts for:

- planner;
- audience-only narrator;
- proposal builder;
- verifier.

Generate a fresh dispatch for each stage. Do not paste the planner card or planner return into the narrator context. The narrator dispatch is manufactured from audience context plus approved observable beats and omits private world hypotheses, weights, candidate operations, and rationale.

Separate chats or API calls provide distinct contexts. They are not automatically provider-attested confidentiality boundaries. Describe the isolation honestly.

The parent alone may:

- choose the worker and transport;
- save and accept the exact return;
- review readiness;
- commit the frozen preparation; and
- present receipt narration.

## Path E — managed backstage retcon checkpoint

The player still only says what they do. A connected or human parent may privately open a checkpoint between turns when several hidden explanations fit and a reveal or payoff is approaching. Use the managed run, not the stateless command walk:

```bash
./lacuna checkpoint run begin CUBE \
  --root .lacuna-checkpoint-runs \
  --trigger "Compare bounded explanations before the next reveal." \
  --provider chatgpt \
  --format markdown
```

Copy the printed run path. At every worker stage:

```bash
./lacuna checkpoint run dispatch RUN_PATH --format markdown \
  > chatgpt-checkpoint-handoff.md
```

Paste the whole handoff into one role-dedicated conversation or agent. It embeds the exact current card and the already-sized return template. ChatGPT returns exactly one JSON object. Save it unchanged and run the accept command printed inside the handoff:

```bash
./lacuna checkpoint run accept RUN_PATH RUN_PATH/MODEL_RETURN.json \
  --model HONEST_MODEL_NAME \
  --model-version OPTIONAL_VERSION \
  --invocation-id OPTIONAL_CALL_ID \
  --format markdown
```

Then read the newly generated `NEXT.md`. The managed state order is generator → provenance-blind judge → winner-only compressor → proposal-visible verifier → parent commit. All candidate slots, rollout beats, and judge score slots are preallocated. The parent does not ask ChatGPT to infer the workflow or remember which file comes next.

A timeout, provider error, malformed return, refusal, or interrupted attempt can be recorded without advancing:

```bash
./lacuna checkpoint run record-failure RUN_PATH \
  --failure-class invalid-output \
  --failure-message "The response contained prose around the JSON." \
  --model HONEST_MODEL_NAME
```

Use separate chats, ChatGPT workspace agents, or native subagents when available and useful, but describe the boundary honestly. A configured provider route and host-declared invocation receipt are not provider attestations of identity, isolation, tool denial, or independence. One conversation may execute roles serially; that remains a valid transport but is not independent judging.

At `ready-to-commit`, only the parent runs:

```bash
./lacuna checkpoint run commit RUN_PATH --format json
```

For the clean forgetting condition, wait for the next exact player input and compile one source-bound continuation handoff:

```bash
./lacuna checkpoint run next-turn RUN_PATH \
  --player-input-file next-player-input.txt \
  --provider chatgpt \
  --format markdown > fresh-narrator-handoff.md
```

Open a new narrator context and paste the whole handoff. It already embeds the authenticated compact state, typed audience context, exact player input, exact proposal template, save path, and parent accept command. ChatGPT returns one JSON proposal only. The parent saves it, runs the printed ordinary-turn accept command, and follows that turn run through commit.

When earlier prose is needed for continuity, the parent should prefer `lacuna history complete CHECKPOINT_RUN --run-root TURN_RUNS` and add `--public-history public-history.json`; use `history build` only for an explicitly partial ordered list. Do not place the narrator in a Project whose memory can reference worker or parent chats. Temporary Chat reduces personalization-memory carryover but still follows enabled Custom Instructions; disable or record them. A new API request should omit linked conversation/previous-response state when the treatment requires a fresh supplied context. These controls reduce carryover; they do not attest provider forgetting.

Candidates, scores, rejected futures, state cards, reviews, and invocation records remain backstage. See [`CHECKPOINT_RUNS.md`](CHECKPOINT_RUNS.md), [`FRESH_NARRATOR.md`](FRESH_NARRATOR.md), and [`PUBLIC_HISTORY.md`](PUBLIC_HISTORY.md). The stateless protocol in [`CHECKPOINTS.md`](CHECKPOINTS.md) is for custom hosts that intentionally own the state machine.

## Path F — connected-host target

A narrow ChatGPT Action/App/API host should expose operations equivalent to:

1. `play start` or `turn run begin` from exact input bytes and an explicit input kind/profile;
2. audited run status and deterministic next action;
3. self-contained dispatch rendering for the current delegated stage;
4. exact artifact acceptance;
5. pointer-only recovery;
6. exact commit or authenticated receipt recovery.

A connected host may also expose the managed checkpoint surface: `checkpoint run begin/status/dispatch/accept/record-failure/recover/commit/narrator-capsule/next-turn/continuation`. It should keep `run.json` authoritative, expose only the current complete dispatch to a role worker, and retain provider/model invocation metadata as host declarations. Role workers must not receive arbitrary shell, accept, review, recovery, or mutation endpoints.

It may expose read-only campaign selection, model brief rendering, verification, and receipt inspection. It should not expose arbitrary mutation commands to a role worker. Unrevealed fair-play openings stay outside the integration.

At minimum, retain:

- exact input bytes, digest, and kind;
- run, cube, request, packet, proposal, and expected-head identity;
- complete dispatch delivered to each worker;
- exact returned JSON and digest;
- ordered accepted and failed checkpoint invocation receipts;
- structured refusals;
- preparation and accepted receipt;
- fresh-narrator capsule and continuation-dispatch bytes/digests plus the context/settings declaration used for continuation;
- optional public-history bytes/digest and its declared coverage policy.

Provider, model, timing, and token metadata may be recorded as host-supplied invocation custody. Do not call it provider attestation without an actual attestation mechanism.

## Pointer recovery

`NEXT.md` is derived, not authoritative. When it is missing, edited, or link-substituted:

```bash
./lacuna turn run recover RUN_PATH --format markdown
```

Recovery first audits every authoritative member. It replaces only `NEXT.md`; it refuses to invent or repair a packet, card, return, proposal, preparation, manifest, invocation receipt, or commit receipt. For a managed checkpoint run use:

```bash
./lacuna checkpoint run recover RUN_PATH --format markdown
```

## What the player should experience

The protocol remains backstage. The player says what they do; the DM responds. Ask a setup question only when a missing preference genuinely blocks play. Do not ask the player to author JSON, manage files, choose worlds, resolve stale heads, or understand the agent topology.

## Comparative scenarios with ChatGPT

The player still says “Will you DM?” and plays. A scenario capsule is a backstage experiment-owner workflow.

Without shell/filesystem access, a person runs `scenario dispatch`, pastes the complete active driver or generated role card into a fresh ChatGPT conversation, saves the exact JSON return, and runs `scenario record`. Separate conversations can support the role-separated treatment; after each completed checkpoint, rev0164 requires the parent to run `checkpoint run next-turn` and give its complete continuation dispatch to a new narrator conversation. Fresh-chat/context IDs remain host declarations rather than proof of independent memory.

A connected ChatGPT parent may operate the CLI and any agent tools it actually has. It should explicitly delegate the named role, provide only the generated least-context card, and retain all transition authority itself. Give blind raters only `70-blind-rating-packet.json`. See [`SCENARIO_CAPSULES.md`](SCENARIO_CAPSULES.md).

### Replicated scenario bundles

For a preregistered multi-block study, the player-facing entrance is still exactly the same: the participant can simply say “Will you DM?” The bundle is backstage research custody, not something the player must understand.

The experiment owner first builds one bundle plan containing every seed/capsule pair, fixes the rating contract and inclusion rule, and publishes the complete child tree before accepting any condition result. When a witness threshold is configured, the parent must collect the required external receipt before dispatching the first child. Thereafter ChatGPT should follow only the parent bundle's `NEXT.md`, use an explicitly fresh worker context for every condition and blind-rating invocation, use a fresh dispatch-bound narrator inside each role-separated cell after every checkpoint, seal every block, and refuse to unblind any child until all scheduled blocks are sealed. A connected parent may use native subagents when available, but it must give each one only the generated dispatch/card and retain all accept, audit, recovery, seal, and unblind authority itself.

Without a connected filesystem tool, a human bridge can execute the same protocol by copying each complete generated dispatch into a fresh ChatGPT conversation and recording the exact JSON return. See [`SCENARIO_BUNDLES.md`](SCENARIO_BUNDLES.md).

## Comparative-run contamination canaries

In a scenario cell, the complete driver is private coordinator context, not a prompt to paste into every role chat. It deliberately contains an operator-only canary and identifies a separate filesystem-only canary by path/digest. Give generator, judge, compressor, verifier, fresh narrator, and blind rater only their generated role artifact. Once all cells are frozen, run `lacuna scenario contamination RUN --format markdown` before rating. Preserve detected matches; a clean scan is not proof that ChatGPT memory, Project context, Custom Instructions, or linked conversation state was absent.
