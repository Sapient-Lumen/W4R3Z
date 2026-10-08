# One-sentence play start

For the shortest player, parent, and clean-experiment routes, start with [`../../OPERATE_LACUNA.md`](../../OPERATE_LACUNA.md).

A player may begin with one sentence:

> Will you DM?

That sentence is **session control**. It asks the host to begin or resume play; it is not dialogue spoken by a character and it does not assert that anything happened inside the fiction.

## The shortest durable entrance

From a shell-capable workspace at the repository root:

```bash
./lacuna play start .lacuna-play \
  --bootstrap \
  --profile orchestrated \
  --format markdown
```

With no explicit `--player-input`, the command retains the exact default text `Will you DM?`. It safely initializes an empty `.lacuna-play/` library when `--bootstrap` is present, creates or selects one campaign, opens a request-scoped run, classifies the input as `session-control`, and prints the first audited next action.

It does **not** invoke a model, narrate a scene, or commit a turn.

Use an existing campaign without bootstrap:

```bash
./lacuna play start PATH_TO_CUBE_OR_LIBRARY \
  --profile orchestrated \
  --player-input 'Will you DM?' \
  --format markdown
```

For exact multiline session text, use `--player-input-file` or standard input.

## What the parent does next

Copy the emitted run path and inspect one pointer:

```bash
cat RUN_PATH/NEXT.md
```

When the owner is a delegated role, render a complete provider-neutral or provider-specific handoff:

```bash
./lacuna turn run dispatch RUN_PATH \
  --provider chatgpt \
  --format markdown
```

Other supported route labels are `portable`, `codex`, `claude-code`, and `gemini-cli`.

The dispatch is self-contained. It embeds the exact generated task card in `input_document`, names the role and provider alias, states the required return schema, supplies the save path and parent accept command, and repeats the worker’s non-authority. A chat worker does not need local access to the run directory.

The worker returns one JSON object only. The parent saves those exact bytes and runs the generated command:

```bash
./lacuna turn run accept RUN_PATH MODEL_RETURN.json --format markdown
```

Repeat `NEXT.md` → `dispatch` → worker JSON → `accept` for delegated stages. Parent-owned stages are completed by the parent from the named complete artifact. At readiness:

```bash
./lacuna turn run commit RUN_PATH --format json
```

Only the top-level `narration` in a passing `60-turn-receipt.json` may be presented as having happened.

## What ordinary ChatGPT can do

A conversation-only ChatGPT can begin a playable scene immediately. It should say once, when no connected host or human bridge exists:

> We can play immediately; this chat is not yet committed to a Lacuna cube.

Then it should DM normally, keep the protocol backstage, preserve experienced facts, and keep unused hidden explanations revisable.

A Project, custom instructions, uploaded ZIP, or subscription tier can improve instruction-following and continuity. Those features do not by themselves prove access to a durable local cube. Governed persistence requires one of:

- a connected host exposing the narrow run operations;
- a shell-capable workspace agent;
- or a human moving exact dispatches and returns between ChatGPT and the CLI.

## Human bridge in four operations

For an ordinary ChatGPT conversation plus a local terminal:

```bash
./lacuna play start .lacuna-play --bootstrap --profile chat --format markdown
./lacuna turn run dispatch RUN_PATH --provider chatgpt --format markdown
./lacuna turn run accept RUN_PATH chatgpt-return.json --format markdown
./lacuna turn run commit RUN_PATH --format json
```

The second and third operations repeat until `NEXT.md` names commit. Use `solo` behavior for the smallest bridge, or an orchestrated run with fresh role-dedicated conversations for planner, narrator, builder, and verifier stages.

## Capability table

| Surface | Starts from one sentence | Persists to a cube without a human bridge | Correct route |
|---|---:|---:|---|
| Ordinary chat model | Yes | No | Chat-only play |
| Project/custom instructions plus files | Yes | No, absent a connected host | Chat-only or human bridge |
| Connected ChatGPT Action/App/API host | Yes | Yes | Narrow run API |
| Codex or another shell-capable workspace model | Yes | Yes | `play start`, then follow `NEXT.md` |
| Claude Code / Gemini CLI with role workers | Yes | Yes | Provider dispatch plus parent-only accept/commit |
| Human terminal plus any capable LLM | Yes | Yes | Paste bridge |

Choose a profile from actual capabilities, not product branding.

## Why the typed input matters

`lacuna.turn-request.v3` carries `input.kind` as either:

- `session-control` — start, resume, pause, change mode, or otherwise manage play; or
- `play-turn` — an utterance, choice, request, or attempt made within the active play exchange.

The host decides the kind before mutation. The kernel validates it and records it in source custody. This prevents a weak coordinator from turning “Will you DM?” into fictional dialogue or an in-world event merely because the same text field carries both kinds of input.

Legacy v2 packets remain readable and default to `play-turn`; they do not gain retroactive session-control meaning.

## Failure and repair

A missing, stale, malformed, cross-turn, or wrong-schema worker return is discarded and the current complete dispatch is reissued. Do not repair IDs or hashes by hand.

`NEXT.md` is a deterministic convenience pointer, not authority. When it is missing, edited, or replaced by a link, first audit and repair only that pointer:

```bash
./lacuna turn run recover RUN_PATH --format markdown
```

Recovery refuses if `run.json` or any authoritative retained artifact is missing, changed, relabelled, oversized, linked, or digest-inconsistent. It never reconstructs an authoritative model return.

## Host instruction in one paragraph

Treat `Will you DM?` as session control; resolve or safely bootstrap one campaign; open exactly one request-scoped run; follow only its audited `NEXT.md`; render a self-contained dispatch for each delegated role; give that worker only the embedded complete card; save one exact schema-valid JSON return; keep accept and commit authority in the parent; and present narration only from a passing commit receipt.

That paragraph is the portable entrance. The generated artifacts are the executable details.
