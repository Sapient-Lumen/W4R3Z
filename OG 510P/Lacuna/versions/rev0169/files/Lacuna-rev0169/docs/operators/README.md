# Operator guides

- [`../../PLAY_NOW.md`](../../PLAY_NOW.md) — player-only entrance; no operator vocabulary required.
- [`../../OPERATE_LACUNA.md`](../../OPERATE_LACUNA.md) — shortest capability-first entrance for play, governed operation, and the clean experiment.
- [`ONE_SENTENCE_START.md`](ONE_SENTENCE_START.md) — start or resume play from “Will you DM?” without fictionalizing session control.
- [`FRESH_NARRATOR.md`](FRESH_NARRATOR.md) — join a committed checkpoint to one exact fresh source-bound turn and reset the narrator context.
- [`PUBLIC_HISTORY.md`](PUBLIC_HISTORY.md) — carry exact player-visible prose as an explicit partial list or checkpoint-bound complete durable-turn census.
- [`MODEL_ENTRANCE.md`](MODEL_ENTRANCE.md) — route play, backstage planning, repository, and inspection intent; then choose an honest capability profile.
- [`TURN_RUNS.md`](TURN_RUNS.md) — operate the request-scoped ordinary-turn state machine, self-contained dispatches, pointer recovery, and exact commit.
- [`CHECKPOINT_RUNS.md`](CHECKPOINT_RUNS.md) — operate the managed generator → judge → compressor → verifier checkpoint with fixed provider routes, invocation receipts, exact resume, and commit recovery.
- [`SCENARIO_CAPSULES.md`](SCENARIO_CAPSULES.md) — run one exact four-condition comparison, preserve blinding, configure subagents, collect ratings, and unblind once.
- [`CONTAMINATION_CANARIES.md`](CONTAMINATION_CANARIES.md) — operate and interpret preregistered operator/filesystem canaries without exposing them to blind raters.
- [`SCENARIO_BUNDLES.md`](SCENARIO_BUNDLES.md) — preregister repeated blocks, externally retain the commitment, seal every block blind, and export rater-level data.
- [`CHATGPT.md`](CHATGPT.md) — ordinary chat, Project/custom GPT, human bridge, role context, connected-host, and managed-checkpoint paths.
- [`MULTI_AGENT.md`](MULTI_AGENT.md) — parent/worker authority, least-context cards, provider mixing, and subagent topology for turns and checkpoints.
- [`PROVIDER_CONFIGS.md`](PROVIDER_CONFIGS.md) — Codex, Claude Code, Gemini CLI, ChatGPT, portable mappings, and downgrade rules.
- [`CHECKPOINTS.md`](CHECKPOINTS.md) — the lower-level stateless checkpoint protocol for custom hosts and protocol inspection.

The shortest governed play entrance is:

```bash
./lacuna play start .lacuna-play --bootstrap --profile orchestrated --format markdown
```

Thereafter obey the audited `NEXT.md`, render delegated work with `turn run dispatch`, accept one exact worker object, and let only the parent invoke `turn run commit`.

The normal backstage retcon entrance is:

```bash
./lacuna checkpoint run begin CUBE \
  --root .lacuna-checkpoint-runs \
  --trigger "Compare bounded explanations before the next reveal." \
  --provider chatgpt --format markdown
```

Thereafter obey that run's `NEXT.md`, render the exact current handoff with `checkpoint run dispatch`, record accepted or failed invocations honestly, and let only the parent invoke `checkpoint run commit`. For the clean bottleneck condition, the committed pointer then directs the parent to `checkpoint run next-turn`; give its complete continuation dispatch to a new narrator context and route the returned proposal through the ordinary turn-run accept/commit boundary.

A player never needs checkpoint vocabulary. A parent may be a person, a shell-capable frontier model, or a host program. A worker receives one complete card and returns one JSON object. Neither a provider route nor an invocation receipt proves provider identity, isolation, independence, or model compliance.

## Comparative experiment entrance

```bash
./lacuna scenario template CUBE > scenario-capsule.json
# edit the fixed script/model/budget/rating policy
./lacuna scenario begin CUBE scenario-capsule.json --root .lacuna-scenarios --format markdown
```

Thereafter follow only the audited scenario `NEXT.md`. Give workers only the active cell dispatch and give raters only `70-blind-rating-packet.json`.

## Replicated experiment entrance

```bash
./lacuna scenario bundle template \
  --block CUBE_A CAPSULE_A.json \
  --block CUBE_B CAPSULE_B.json \
  --minimum-witnesses 1 > bundle-plan.json
./lacuna scenario bundle begin bundle-plan.json \
  --root .lacuna-scenario-bundles --format markdown
```

Every child and hidden assignment is published before execution. Follow only the parent `NEXT.md`, seal each fully rated child without unblinding, and call bundle unblind only after all blocks are sealed. The witness gate binds operator-supplied external receipt descriptions; it does not verify a signature, timestamp, or service.
