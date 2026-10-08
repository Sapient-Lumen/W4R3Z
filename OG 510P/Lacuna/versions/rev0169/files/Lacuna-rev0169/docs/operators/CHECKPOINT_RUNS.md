# Managed retcon checkpoint runs

Use this path for normal operation. It turns the lower-level checkpoint protocol into one audited, resumable directory with one exact next action.

A managed run does **not** call an LLM. It freezes the current checkpoint request, manufactures the least-context card for the current role, records the configured provider route, validates each returned JSON object, records host-declared invocation custody, manufactures the next card, runs the real kernel review, and commits or exactly recovers the one reviewed transition.

The player never needs to see this protocol.

## The shortest complete walk

Open one private run:

```bash
CUBE=/path/to/cube-or-selected-library
./lacuna checkpoint run begin "$CUBE" \
  --root .lacuna-checkpoint-runs \
  --trigger "Several hidden explanations fit; compare them before the next reveal." \
  --candidate-count 4 \
  --rollout-horizon-turns 4 \
  --compression-max-chars 6000 \
  --max-operations 32 \
  --provider chatgpt \
  --format markdown
```

Copy the printed run path. From then on, `RUN_PATH/NEXT.md` names exactly one owner and one action:

```bash
cat RUN_PATH/NEXT.md
```

At a delegated stage, render the complete worker handoff:

```bash
./lacuna checkpoint run dispatch RUN_PATH --format markdown \
  > checkpoint-handoff.md
```

Give that whole handoff to exactly one role-dedicated model context. It embeds the exact card, cardinality-sized return template, provider alias, authority boundary, and required return schema. The worker does not need filesystem access and should return exactly one JSON object—no prose or code fence.

Save the object as `RUN_PATH/MODEL_RETURN.json`, then run the accept command printed in the handoff. Its general form is:

```bash
./lacuna checkpoint run accept RUN_PATH RUN_PATH/MODEL_RETURN.json \
  --model HONEST_MODEL_NAME \
  --model-version OPTIONAL_VERSION \
  --invocation-id OPTIONAL_PROVIDER_CALL_ID \
  --format markdown
```

Read the newly generated `NEXT.md` and repeat. The normal role order is:

```text
awaiting-generator
  -> awaiting-judge
  -> awaiting-compressor
  -> awaiting-verifier
  -> ready-to-commit
  -> committed
```

When the run reaches `ready-to-commit`:

```bash
./lacuna checkpoint run commit RUN_PATH --format json
```

Only an accepted checkpoint receipt proves that the selected narrow transition reached the cube. Present only the receipt's top-level `narration` when it is appropriate to continue play. Candidates, rollout futures, scores, state cards, reviews, and invocation records stay backstage.

The committed `NEXT.md` then points to the clean continuation entrance when the next player input is available:

```bash
./lacuna checkpoint run next-turn RUN_PATH \
  --player-input-file next-player-input.txt \
  --provider chatgpt \
  --format markdown
```

The command opens one audience-only solo turn at the accepted checkpoint head and emits one complete fresh-narrator dispatch. Give that dispatch to a new narrator context, save its exact proposal object, and run the ordinary-turn accept command embedded in the dispatch. This is required by the role-separated experimental treatment; same-context continuation remains a valid serial control.

## What begin changes

`checkpoint run begin` resolves the supplied cube path and the already-open `Cube` root to the same exact location, verifies the cube, and manufactures the source-bound request plus generator card before creating the sidecar directory. Ordinary policy or request validation failure therefore leaves no run-shaped directory. The request event is custody for the exact trigger, expected head, grant, protected-state projection, and packet digest. It is not a fictional reveal and does not commit any candidate hidden world.

The run directory itself is a private host sidecar, created with owner-only permissions where the platform supports them. An actual process interruption or filesystem failure during publication can still leave an incomplete unreferenced directory; such a directory is not a valid run and must not be repaired by hand. The sidecar is outside the event ledger and may contain privileged future material.

## Mix model providers by role

A run freezes four provider routes at creation. Use one default or override any role:

```bash
./lacuna checkpoint run begin "$CUBE" \
  --root .lacuna-checkpoint-runs \
  --trigger "Compare bounded causal explanations." \
  --provider portable \
  --generator-provider chatgpt \
  --judge-provider codex \
  --compressor-provider claude-code \
  --verifier-provider gemini-cli \
  --format markdown
```

Supported route labels are `portable`, `codex`, `claude-code`, `gemini-cli`, and `chatgpt`. The route determines the role alias shown in `NEXT.md` and the dispatch. It does not invoke, authenticate, isolate, or attest that provider.

A useful heterogeneous configuration is:

| Role | Typical reason for separation | Receives |
|---|---|---|
| generator | broaden hypothesis search | protected state, policy, privileged planner context |
| judge | reduce direct generator self-preference | provenance-stripped, ID-sorted candidates and exact scoring rubric |
| compressor | prevent rejected futures from leaking downstream | selected candidate, judgment, protected unknowns, narrow grant |
| verifier | add a proposal-visible adversarial check | exact request and parent-assembled proposal |

Different model families can add procedural diversity. They still do not prove statistical independence, semantic anonymity, calibration, or better fiction.

## ChatGPT without shell access: the human bridge

A person can operate the parent while ChatGPT performs one bounded role. For the clean condition, use fresh role chats and a separate fresh narrator chat after commit:

1. The person runs `checkpoint run begin` and then `checkpoint run dispatch`.
2. The person pastes the complete handoff into a fresh or role-dedicated ChatGPT conversation.
3. ChatGPT returns one JSON object.
4. The person saves it unchanged and runs the printed `checkpoint run accept` command.
5. The person repeats until `ready-to-commit`, then runs `checkpoint run commit`.
6. When the next player input arrives, the person runs `checkpoint run next-turn` and pastes its complete continuation dispatch into a new narrator context.
7. The person saves the returned proposal unchanged, runs the dispatch's ordinary-turn accept command, follows that turn run's `NEXT.md`, and commits only from the parent.

The same conversation may execute roles serially when convenience matters more than separation. In that case, do not describe the judge or verifier as independent and do not call the continuing narrator a forgetting test. Fresh conversations reduce accidental context carryover but are not provider-signed confidentiality proofs. A shared-memory Project is operationally convenient and experimentally confounded for the clean condition.

A 20-year-old player still only needs to say “Will you DM?” The bridge is a backstage operator workflow, not a player ritual. See [`CHATGPT.md`](CHATGPT.md) for the ordinary play entrance.

## Tool-capable parent and native subagents

`NEXT.md` is deliberately written as an orchestration instruction. At each delegated state it names:

- the sole current role;
- the configured provider route and provider-specific role/context alias;
- the exact card path and required output schema;
- a command that renders a self-contained handoff; and
- the rule that the parent alone accepts, reviews, commits, recovers, and presents.

A parent with native subagents should create or invoke **one** context for the named role, provide only the generated dispatch, disable unnecessary tools, collect one JSON object, and return to the parent boundary. A host without native subagents can use a fresh chat, API call, or serial execution while preserving the same card boundary.

Lacuna can make the intended subagent call and context slice explicit. It cannot force a product to expose subagents, choose a model, deny tools, erase memory, or prove that the worker followed the handoff.

## Record a failed invocation without advancing

A timeout, provider error, transport failure, invalid output, worker refusal, or interruption should not be disguised as a successful role return:

```bash
./lacuna checkpoint run record-failure RUN_PATH \
  --failure-class timeout \
  --failure-message "No complete JSON object arrived." \
  --model HONEST_MODEL_NAME \
  --model-version OPTIONAL_VERSION \
  --invocation-id OPTIONAL_PROVIDER_CALL_ID
```

Accepted failure classes are:

```text
provider-error
timeout
transport-error
invalid-output
worker-refusal
interrupted
other
```

The run remains at the same role. The next attempt number increments. Only a validated accepted output advances.

## Invocation custody: what is actually retained

For every accepted or failed attempt, the parent writes one ordered `lacuna.checkpoint-invocation-receipt.v1` containing:

- run, checkpoint, sequence, attempt, and role;
- frozen provider route and provider-specific agent/context name;
- exact card and deterministic dispatch digests;
- required output schema;
- host-declared model, optional version, optional invocation ID, and optional timing/duration;
- accepted output path/digest/schema, or a failure class and message; and
- explicit nonclaims.

These receipts establish the sidecar's retained custody under Lacuna's canonical JSON rules. They are **host declarations**, not provider-signed model identity, billing, token-usage, tool-denial, isolation, or timing attestations.

Every retained role output requires exactly one accepted invocation receipt. Failed attempts may precede it. Invocation roles must appear in stage order, and no later attempt may follow an accepted return for the same role. A run retains at most 1,000 invocation receipts; an additional attempt refuses before writing a receipt or changing `run.json`.

## Exact state and files

`run.json` is authoritative. It binds the run and cube identity, exact checkpoint request, fixed provider routes, exact artifact topology, invocation receipt sequence, state, and deterministic next action.

The fixed files are:

```text
00-trigger.txt
10-checkpoint-request.json
20-generator-card.json
21-candidates.json
30-judge-card.json
31-judgment.json
40-compressor-card.json
41-compression.json
50-checkpoint-proposal.json
60-verifier-card.json
61-verifier-return.json
70-checkpoint-review.json
80-checkpoint-receipt.json
invocation-NNNN-ROLE.json
run.json
NEXT.md
.run.lock
```

Only the files appropriate to the current state are referenced by `run.json`. Every referenced JSON artifact has fixed path, media type, schema, role, and canonical digest metadata. Audit reconstructs every downstream card and proposal from the retained upstream chain rather than trusting file names alone.

## Status, audit, and pointer recovery

Strictly audit the complete run:

```bash
./lacuna checkpoint run status RUN_PATH --format markdown
```

`NEXT.md` is derived and replaceable. If it is missing, stale, edited, or link-substituted, repair only that pointer:

```bash
./lacuna checkpoint run recover RUN_PATH --format markdown
```

Recovery first audits every authoritative member and then rewrites `NEXT.md`. It never invents or repairs a request, card, model return, proposal, review, invocation record, manifest, or receipt.

A verifier refusal produces terminal state `verifier-refused`. Do not flip it by editing JSON. Retain the run for audit, correct the process or proposal, and begin a fresh checkpoint.


## Fresh narrator after commit

The generator/judge/compressor/verifier boundary does not erase the continuing narrator's conversation history. The normal post-commit transition is therefore:

```bash
./lacuna checkpoint run next-turn RUN_PATH \
  --player-input-file next-player-input.txt \
  --provider portable \
  --format markdown
```

The command:

1. locks and audits the complete committed checkpoint;
2. authenticates the request, proposal, compression, receipt, and winner-only narrator capsule;
3. requires the live cube head to equal the checkpoint's accepted post-commit head;
4. opens exactly one fresh ordinary `play-turn` run with audience-only context, `solo` topology, and no anchor grant;
5. binds the exact player input and ordinary proposal template; and
6. emits `lacuna.checkpoint-continuation-dispatch.v2` for `lacuna-fresh-narrator`.

The worker receives one input document and returns one exact `lacuna.turn-proposal.v2`. It cannot accept, recover, commit, inspect unrelated artifacts, or present narration as durable. The parent saves the object, runs the printed ordinary-turn accept command, and follows that turn run through exact preparation and commit.

When exact prose continuity is needed, prefer `lacuna history complete RUN_PATH --run-root TURN_RUNS` and pass `--public-history`. The immutable ledger supplies the expected pre-checkpoint turn census and retained managed runs supply exact prose; missing or duplicate custody refuses. Use `lacuna history build ...` only for an explicitly partial run list. Both modes are checked against cube, audience, canonical digests, immutable event order, and checkpoint chronology before the continuation turn is created. See [`PUBLIC_HISTORY.md`](PUBLIC_HISTORY.md).

Two lower-level surfaces remain:

- `checkpoint run continuation CHECKPOINT_RUN TURN_RUN` binds an already-open qualifying fresh turn;
- `checkpoint run narrator-capsule` emits only the reusable authenticated checkpoint capsule.

This is context manufacture, not remote attestation. A host can still leak extra information, a provider can retain state, an explicit-run-list public history may be incomplete; complete mode is still limited to durable Lacuna turns and excludes external chat, and a schema-valid state card can be artistically insufficient. See [`FRESH_NARRATOR.md`](FRESH_NARRATOR.md).

## Commit crash and later-head recovery

SQLite mutation and sidecar replacement are not one distributed transaction. A process can commit the exact checkpoint and crash before writing `80-checkpoint-receipt.json` or updating `run.json`.

Retry:

```bash
./lacuna checkpoint run commit RUN_PATH --format json
```

The parent validates the complete retained chain. If the exact proposal is already durable, it reconstructs an authenticated receipt instead of appending duplicate events. This also works after later valid ledger changes advance the live head: recovery verifies the historical request-head prefix and exact durable event chain. A look-alike change, forged prefix, changed preparation, or stale uncommitted proposal refuses.

## Sidecar safety and concurrency boundary

Managed checkpoint runs reuse the same hardened sidecar boundary as ordinary turn runs:

- descriptor-bound reads;
- refusal of symlinks, hard links, nonregular files, oversized members, and detected path substitution;
- canonical digest and fixed metadata checks;
- one nonblocking owner-only `.run.lock` across each complete state transition; and
- atomic file replacement for authoritative JSON and the derived pointer.

This is cooperative same-host coordination. It is not a hostile-same-user sandbox, distributed lock, encrypted vault, remote attestation system, or atomic transaction across the filesystem and SQLite.

## Retention, upgrades, and privacy

Treat the directory according to its most privileged artifact. It can contain rejected future arcs, protected unknowns, private planner context, the only full copy of the selected state-card body, and exact model returns. Lacuna supplies no built-in encryption, remote archive, redaction, expiry, or secure deletion.

The current run schema binds the exact Lacuna project version. Finish, deliberately retain, or export active runs before upgrading; there is no checkpoint-run migration command yet.

After acceptance, `MODEL_RETURN.json` is merely the operator's staging file. The accepted canonical object is already retained under its fixed role filename. Deleting the staging file does not redact the managed run.

## Lower-level protocol

The stateless commands remain available for experiments and custom hosts:

```text
checkpoint begin
checkpoint card
checkpoint dispatch
checkpoint assemble
checkpoint review
checkpoint commit
```

They expose the same checkpoint schemas and kernel boundary without `run.json`, `NEXT.md`, invocation receipts, fixed provider routes, or managed resume semantics. See [`CHECKPOINTS.md`](CHECKPOINTS.md). New human and model operators should start with the managed path unless they specifically need to own the artifact state machine themselves.
