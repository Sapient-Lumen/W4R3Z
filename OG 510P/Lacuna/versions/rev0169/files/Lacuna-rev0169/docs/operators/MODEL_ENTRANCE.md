# Portable model entrance

A fresh model should not have to infer whether the user wants to play, edit the repository, inspect a cube, or authorize mutation. It should not have to reconstruct orchestration from scattered prose or assume local access to a path it cannot open.

Lacuna exposes four generated entrances:

1. `play start` turns one exact session-control sentence into a governed run;
2. `model brief` explains capabilities, readiness, routing, and authority without mutation;
3. `turn run dispatch` turns the current delegated stage into one self-contained worker envelope.
4. `checkpoint run begin/dispatch/accept` turns a backstage planning request into one managed generator → judge → compressor → verifier run with fixed provider routes, invocation custody, and exact resume; after commit, `checkpoint run next-turn` opens one narrow ordinary turn and emits the complete clean-continuation dispatch.

## First classify intent

| Intent | Examples | Correct route |
|---|---|---|
| Play | “Will you DM?”, “continue”, character speech/action | Operate a campaign |
| Backstage checkpoint | “compare hidden explanations”, “run a retcon checkpoint” | Open a managed checkpoint run; keep it private |
| Repository work | audit, refactor, test, document, package | Work on source |
| Inspection | explain, show, verify, diagnose | Prefer read-only commands |
| Mutation authority | explicit request plus a capable host | Use packet/run/commit boundaries |

“Will you DM?” is session control. It asks the host to start or resume; it does not establish a fictional event.

## Direct play entrance

```bash
./lacuna play start REFERENCE \
  --profile chat|workspace|orchestrated \
  --format markdown
```

Add `--bootstrap` only when the reference is absent or empty and safe campaign initialization is intended. Lacuna refuses to overlay play state onto a foreign nonempty path.

With no explicit player input, the exact text is `Will you DM?`. `play start` emits `lacuna.play-start.v1`, opens a turn-request-v3 packet with `input.kind = session-control`, and reports the next action. It does not invoke a model or narrate.

Read `ONE_SENTENCE_START.md` for the complete path.

## Read-only brief

```bash
./lacuna model brief REFERENCE \
  --profile chat|workspace|orchestrated \
  --format markdown|json
```

`REFERENCE` may be a cube or a campaign library with one selected campaign. The brief resolves and verifies the cube, checks role readiness, names provider aliases, and states exact run/receipt behavior without changing the head.

Use it operationally; do not merely summarize it to the user.

## Profiles describe capabilities

### `chat`

Assumes only pasted text and returned text/JSON. It does not assume shell access, durable storage, connectors, subagents, or background execution.

The model may begin chat-only play. Governed persistence requires a human bridge or connected host.

### `workspace`

Assumes one parent can read and write files and execute the CLI. It does not assume bounded subagents. Default to `solo` unless the host can preserve role boundaries by separate contexts.

### `orchestrated`

Assumes one parent can execute the CLI and can route exact cards to bounded workers or role-dedicated contexts. `auto` selects `solo`, `pair`, or `full` from packet-visible policy. The parent keeps accept and commit authority.

A profile is an operational claim by the host, not a provider identity proof.

## Typed input protocol

Turn request v3 contains:

```json
{"input": {"kind": "session-control"}}
```

or:

```json
{"input": {"kind": "play-turn"}}
```

The exact text remains separately retained and digest-bound. The kind is validated before mutation and copied into source custody, the packet, role instructions, and dispatch.

Legacy request v2 remains accepted and defaults to `play-turn`. Compatibility does not infer session control retroactively.

Checkpoint openings emit `lacuna.turn-request.v4` with `request_purpose: "checkpoint"` and a source-bound checkpoint grant. Ordinary play still uses the play purpose. The explicit purpose, not prose heuristics, selects the authority profile.

## Delegated-stage entrance

When `NEXT.md` names a worker:

```bash
./lacuna turn run dispatch RUN_PATH \
  --provider portable|codex|claude-code|gemini-cli|chatgpt \
  --format markdown|json
```

The strict `lacuna.agent-dispatch.v1` envelope includes:

- run and stage identity;
- provider route and role alias;
- typed input kind;
- artifact path, digest, media type, schema, and role;
- the complete exact card as `input_document`;
- one required return schema and formatting rule;
- save path and parent accept command;
- worker authority and prohibitions;
- parent-only actions and nonclaims.

The worker performs the role from `input_document`. It does not ask for the local path, read unrelated artifacts, edit the sidecar, accept its own response, or commit.

Embedding the card fixes a practical entrance failure: a chat context can receive the exact task even when the local artifact path is meaningless to it. It does not prove that the worker obeyed the card.

## Checkpoint-stage entrance

Open one managed run. The source cube path is resolved and bound to the exact open `Cube` used to freeze the request; provider routes are fixed before any worker return exists:

```bash
./lacuna checkpoint run begin CUBE \
  --root .lacuna-checkpoint-runs \
  --trigger "Compare bounded explanations." \
  --provider chatgpt \
  --format markdown
```

When its `NEXT.md` names a worker:

```bash
./lacuna checkpoint run dispatch RUN_PATH --format markdown
```

The strict `lacuna.checkpoint-run-agent-dispatch.v1` embeds the exact current card, fixed route and alias, return schema, staging path, accept command, failure-record command, authority boundary, and nonclaims. Generator templates contain exactly the policy candidate count and exactly one ordered rollout beat per horizon turn. Judge templates contain exactly one complete score slot per canonical candidate ID. Weaker models fill concrete slots rather than infer protocol cardinality from prose.

The parent saves one exact JSON return and invokes `checkpoint run accept`, or records an honest failed attempt without advancing. The run manufactures the next card, validates the full upstream chain, and retains an ordered `lacuna.checkpoint-invocation-receipt.v1`. At the end only the parent may invoke `checkpoint run commit`. A committed run's deterministic next action may then open `checkpoint run next-turn`; the clean treatment gives its complete `lacuna.checkpoint-continuation-dispatch.v2` to a new narrator context. Optional `lacuna.public-history.v2` custody can be bound when exact earlier prose is required. Prefer checkpoint-bound `history complete` for a durable-turn completeness claim; `history build` is explicitly partial.

The lower-level `checkpoint begin/card/dispatch/assemble/review/commit` commands remain available for custom hosts that deliberately own their own state machine. See [`CHECKPOINT_RUNS.md`](CHECKPOINT_RUNS.md) and [`CHECKPOINTS.md`](CHECKPOINTS.md).

## Run pointer and recovery

`run.json` is authoritative. `NEXT.md` is a deterministic rendering for humans and models.

After each transition, read only the current pointer. Do not choose a stage because another file exists.

When only an ordinary-turn pointer is missing or damaged:

```bash
./lacuna turn run recover RUN_PATH --format markdown
```

For a managed checkpoint pointer:

```bash
./lacuna checkpoint run recover RUN_PATH --format markdown
```

Each command audits all authoritative members using secure descriptor reads, rewrites only `NEXT.md`, and re-audits. Any authoritative inconsistency refuses.

## Presentation rule

A generated scene, planner return, proposal, verifier pass, and exact preparation are not player-visible facts. Only a passing turn receipt binds narration to the durable accepted change.

## Minimal instruction for a fresh parent

Treat play-start language as session control; resolve one campaign; choose ordinary play or a private managed checkpoint; open one run; follow only its audited pointer; generate one complete dispatch for each delegated stage; give the worker only the embedded card; save one exact return or record one honest failure; keep accept and commit authority; present only receipt narration; and, when testing the compression bottleneck, run `checkpoint run next-turn` with the exact next player input and give its complete continuation dispatch to a new narrator context rather than the orchestration conversation.
