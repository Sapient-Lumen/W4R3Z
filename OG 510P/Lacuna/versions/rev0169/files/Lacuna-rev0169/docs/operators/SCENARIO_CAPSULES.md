# Comparative scenario capsules

A scenario capsule is Lacuna's executable answer to a difficult question: **does governed retcon planning actually help, compared with simpler ways of continuing the same story?**

It does not assume that the answer is yes. It manufactures four exact seed clones, commits a hidden condition assignment, accepts one condition at a time, freezes player-visible transcripts, emits a structurally blind rating packet, freezes the fixed number of complete primary ratings, then records post-rating method-identifiability assessments before condition identity can be revealed.

The four fixed conditions are:

| Condition | What it tests | Context and continuation topology |
|---|---|---|
| `forward-only` | Continue from prior state without retrospective hidden-state revision | no checkpoint; one persistent context for the complete cell |
| `prompt-only-retcon` | Let one ordinary model call generate, select, and compress a retrospective explanation | one monolithic checkpoint call; one persistent context for the complete cell |
| `lacuna-serial` | Use Lacuna's generator, judge, compressor, and verifier contracts without manufactured context independence | four ordered checkpoint roles and narration in one persistent context for the complete cell |
| `lacuna-role-separated` | Test manufactured context asymmetry plus the compressed-state bottleneck | four fresh pairwise-distinct checkpoint roles; a fresh continuation-dispatch narrator after each completed checkpoint |

This is an experiment sidecar, not story canon. A cell cube is a disposable exact clone. Nothing in a cell changes the seed cube.

## What this can answer

One completed four-cell block can expose concrete differences in:

- continuity, agency, character stability, genre fit, payoff, novelty, coincidence restraint, mystery fairness, and visible replanning seams;
- whether a condition reached a verified final cube state;
- event-count deltas and frozen final heads;
- host-declared invocation count, failures, latency, tokens, and cost when those values are available; and
- operational failures such as refusals, invalid output, budget exhaustion, or context-topology violations; and
- exact operator-context or filesystem-canary appearances in retained same-cell or cross-cell experiment artifacts.

It cannot establish a general causal result from one block. Replicate the capsule with independently assigned runs, multiple seeds, multiple models, and raters before drawing broad conclusions. Provider identity, model version, context isolation, token usage, timing, and cost are declarations unless a provider independently attests them.

## One complete CLI lifecycle

### 1. Bind a template to one verified seed

```bash
./lacuna scenario template CUBE > scenario-capsule.json
```

The template is already bound to the seed cube ID and head. Edit only the experimental content and policy fields. In particular, replace the placeholder player action and model declaration.

```json
{
  "script": [
    {
      "step_id": "step.off-script-1",
      "player_input": "I abandon the planned meeting and follow the courier into the rain.",
      "checkpoint_after": true,
      "checkpoint_trigger": "Reconsider latent causes without changing observed facts, exposed consequences, or hard commitments.",
      "tags": ["off-script-departure"]
    },
    {
      "step_id": "step.post-checkpoint-1",
      "player_input": "I ask the courier why the station clock is running backward.",
      "checkpoint_after": false,
      "checkpoint_trigger": null,
      "tags": ["post-checkpoint-continuation"]
    }
  ],
  "model_policy": {
    "provider": "portable",
    "model_family": "one-declared-family",
    "model": "one-exact-model-name",
    "model_version": null,
    "sampling_policy": "Use the same temperature, reasoning effort, tool policy, and output budget in all cells.",
    "sampling_seed": null,
    "same_model_required": true
  }
}
```

Keep all four condition names and their order unchanged. Fix the script, model policy, budgets, rubric, and rater count before beginning. The capsule becomes immutable experiment custody after publication. Every checkpoint must be followed by at least one scripted ordinary turn; a checkpoint on the final step refuses because it would produce no observable post-checkpoint continuation.

### 2. Begin the private run

```bash
./lacuna scenario begin CUBE scenario-capsule.json \
  --root .lacuna-scenarios \
  --format markdown
```

Begin performs these operations before the authoritative run path appears:

1. resolve the open cube and supplied path to the same exact directory;
2. verify the seed cube and exact capsule boundary;
3. take one semantic snapshot digest and event count;
4. generate a private randomization seed and deterministic four-condition permutation;
5. create four SQLite backup clones with the same cube ID, head, event count, and semantic snapshot;
6. manufacture every condition-specific private cell-coordinator driver and return template;
7. preregister one operator-only and one filesystem-only exact contamination canary per opaque cell;
8. place each filesystem token only in its unrelated private cell file; and
9. publish the complete owner-only directory with one same-filesystem rename.

`20-PRIVATE-assignment.json` reveals the condition mapping. Do not give it, a private driver, or the run directory to a blind rater.

### 3. Dispatch exactly one opaque cell

```bash
./lacuna scenario dispatch RUN_PATH --format markdown > cell-handoff.md
```

Only one cell can be active. The dispatch is a **private cell-coordinator driver**. It names an opaque cell label and includes the exact cube path, script, model policy, budget, condition contract, return template, and preregistered contamination controls.

Give the driver only to the isolated context or human acting as that cell's coordinator, never to a blind rater. The operator-only token is intentionally visible at this boundary. For nested planner, judge, compressor, verifier, or fresh-narrator calls, transmit only the exact generated role dispatch—not the complete scenario driver. A context that can browse sibling cells can contaminate the comparison. The experiment owner remains responsible for invoking providers, keeping contexts separate, saving exact outputs, and operating Lacuna commands.

### 4. Execute the condition in a fresh provider session

For every cell:

- create a fresh conversation, API conversation state, Codex thread, Claude Code parent session, or equivalent provider context;
- do not reuse a declared `context_id` from another cell;
- process script steps in order;
- record every accepted and failed attempt in exact sequence;
- bind every attempt to its `script_step_id`;
- retain one accepted `lacuna-narrator` call for each transcript step;
- obey the condition-specific checkpoint and continuation topology;
- keep all invocations in one declared persistent context for the first three conditions;
- for `lacuna-role-separated`, keep one narrator context per story segment, use fresh pairwise-distinct checkpoint-role contexts, run `checkpoint run next-turn`, give the next narrator only its complete dispatch, and bind that first subsequent attempt to its checkpoint ID and embedded capsule SHA-256; and
- never let a worker commit, recover, or mutate another cell.

The return is one `lacuna.scenario-cell-return.v1` object. Checkpoint invocations in managed conditions retain one `managed_checkpoint_id`; the first post-checkpoint narrator in the role-separated condition retains `continuation_checkpoint_id` plus `continuation_capsule_sha256`. These values and context IDs are host declarations whose topology Lacuna checks; they are not provider signatures or proof that only the capsule was supplied.

### 5. Record the exact return

```bash
./lacuna scenario record RUN_PATH CELL_RETURN.json --format markdown
```

Record is fail-closed. It validates identity, schema, transcript prefix, script-step binding, role order, model policy, persistent/fresh continuation topology, checkpoint/capsule linkage, fixed budgets, cross-cell context separation, duplicate invocation IDs, and the current cell cube. It then freezes a return artifact and a Lacuna-derived cell receipt.

A rejected return does not advance the manifest. Correct the external artifact and try again; do not edit retained run artifacts.

Repeat dispatch → execute → record until all four cells are frozen.

### 6. Inspect the preregistered contamination scan privately

When the fourth cell is recorded, Lacuna first freezes `65-PRIVATE-contamination-scan.json`. It scans every retained regular-file body and relative pathname beneath the frozen cell trees—including cloned SQLite state, sidecars, and cooperative locks—for unexpected exact copies of each cell's operator-only and filesystem-only token. Inspect the authenticated result:

```bash
./lacuna scenario contamination RUN_PATH --format markdown
```

A finding is retained as `same-cell-leak` or `cross-cell-leak`; it does not discard, repair, or rerun the condition. A clean result means only that those exact tokens were absent from the scanned artifacts. It does not prove fresh provider memory, filesystem denial, semantic isolation, or absence of paraphrased leakage.

Do not give the plan, source tokens, or scan findings to blind raters. Read [`CONTAMINATION_CANARIES.md`](CONTAMINATION_CANARIES.md) for the full boundary and recovery rules.

### 7. Give only the blind packet to raters

Only after the scan is frozen does Lacuna emit:

```text
70-blind-rating-packet.json
```

This packet contains opaque labels, transcripts, transcript digests, and the fixed rubric. It omits structured condition identity, private drivers, invocation records, cube state, and the assignment. Semantic blinding is not guaranteed: prose style or a failure may reveal a method.

Create one exact rating form per rater:

```bash
./lacuna scenario rating-template RUN_PATH \
  --rater-id rater.alex > rating-alex.json
```

The rater fills every integer score, assigns every preference rank exactly once, and may add comments. Then the owner records it:

```bash
./lacuna scenario rate RUN_PATH rating-alex.json --format markdown
```

The run will not unblind after primary ratings alone. Once the capsule's fixed `rater_count` has been reached with unique rater IDs, collect the matching post-rating method-identifiability forms:

### 8. Unblind once

```bash
./lacuna scenario unblind RUN_PATH --format markdown
```

The deterministic report joins condition assignments, frozen transcript and return digests, the exact pre-rating contamination scan, Lacuna-derived mechanical outcomes, host-declared execution totals, authored rating sums/counts, and method-identifiability summaries. These evidence classes remain separate. Leak-detected cells remain included.

## ChatGPT: can a player just say “Will you DM?”

Yes—for play. A 20-year-old player should not need to know scenario capsules, checkpoints, subagents, or the CLI. In an ordinary ChatGPT conversation she can say **“Will you DM?”** and the model should start play under the supplied project instructions. Without a connected filesystem/tool host, that session is chat-only and is not durable Lacuna custody.

A comparative scenario is different. It is a backstage operator workflow. ChatGPT can perform a bounded worker role when a person or connected parent gives it the complete generated dispatch and later records its exact JSON return. Ordinary chat alone cannot prove fresh contexts, clone a cube, retain private assignment custody, or run kernel verification.

Use these entry points:

- player-facing start: [`../../PLAY_WITH_AN_LLM.md`](../../PLAY_WITH_AN_LLM.md);
- ordinary ChatGPT bridge: [`CHATGPT.md`](CHATGPT.md);
- managed ordinary turns: [`TURN_RUNS.md`](TURN_RUNS.md);
- managed retcon roles: [`CHECKPOINT_RUNS.md`](CHECKPOINT_RUNS.md);
- preregistered leakage controls: [`CONTAMINATION_CANARIES.md`](CONTAMINATION_CANARIES.md);
- comparative experiment: this document.

## Continuation is part of the treatment

The `lacuna-role-separated` condition is not satisfied merely by using four differently named workers. The continuing narrator is the model whose memory matters after compression. After every completed managed checkpoint, wait for the next scripted player input and run:

```bash
./lacuna checkpoint run next-turn CHECKPOINT_RUN_PATH \
  --player-input-file next-player-input.txt \
  --provider portable \
  --format markdown
```

The next narrator call must use a declared context that has not appeared earlier in the cell and receive only that complete continuation dispatch. Every attempt for that first turn names the preceding managed checkpoint ID and the dispatch's capsule digest. Later ordinary turns stay in that narrator context until the next checkpoint and leave continuation fields null. A preregistered public-history policy, when used, must be equivalent across all four conditions.

The three controls use one persistent context for the whole cell. This is intentionally stricter than merely allowing any convenient host topology: the experiment needs context persistence versus context reset to be an explicit treatment difference. See [`FRESH_NARRATOR.md`](FRESH_NARRATOR.md).

## Native subagents and the parent/worker split

The cube can make delegation much more likely by emitting a complete role card, exact return schema, forbidden context, fixed provider alias, and parent command. It cannot force a host product to expose a subagent API or prove that a fresh context was used.

The safe topology is:

```text
experiment owner / parent coordinator
    ├─ owns run directory and private assignment
    ├─ opens one opaque cell
    ├─ owns ordinary-turn and checkpoint state transitions
    ├─ gives each worker only its generated dispatch/card
    ├─ records exact returns and failures
    ├─ runs deterministic review/commit/recovery
    └─ presents only player-visible narration

role worker / subagent / fresh chat
    ├─ receives one complete least-context card
    ├─ has no need to inspect the repository or run directory
    ├─ returns one schema-bound JSON object
    └─ cannot accept, commit, recover, unblind, or present by authority
```

### Codex

Codex supports explicit subagent orchestration and only spawns a subagent when asked. The repository includes role definitions under `.codex/agents/` and fixes `max_depth = 1` so workers cannot create another authority layer. A parent should explicitly invoke the named Lacuna role and paste only the generated card. See the official Codex subagent documentation: <https://developers.openai.com/codex/subagents>.

### Claude Code

Claude Code custom subagents run in separate context windows with their own prompts and tool permissions. Lacuna definitions under `.claude/agents/` deny tools and require one exact JSON return. See: <https://docs.anthropic.com/en/docs/claude-code/sub-agents>.

### Gemini coding agents

Lacuna includes equivalent local role definitions under `.gemini/agents/`. Product surfaces and subagent syntax can change; treat the generated card and schema as portable authority, and treat native context separation as a host capability rather than a Lacuna guarantee.

### ChatGPT without a subagent control surface

Use separate fresh conversations as a human bridge, or execute roles serially in one conversation and declare that topology honestly. Do not label a serial fallback “independent” or “role-separated.” For the actual role-separated cell, use four fresh role chats and then a fifth fresh narrator chat after commit; give that narrator only the generated continuation dispatch. Do not use a shared-memory Project as the clean isolation boundary. A connected parent may instead route exact cards to whatever agent tools it actually has.

## Why two agents can matter

The strongest reason is not that “more agents are smarter.” It is **information separation**. A judge that sees provider identity, generation rationale, or a preferred answer can rationalize a selection. A verifier that helped compose a proposal can rubber-stamp its own work. A continuing narrator that remembers rejected futures can defeat the compression test even when all four checkpoint workers were fresh. A role-separated setup therefore manufactures worker slices **and** a fresh dispatch-bound continuation, making contamination auditable through declared context, checkpoint, and capsule identities.

This matters for fiction and science for the same structural reason: private hypothesis generation, blind comparison, compact retained state, and independent checking should not silently collapse into one self-confirming conversation.

Still, two nominal agents can share weights, system memory, tools, or hidden provider state. Role separation is an experimental condition and a custody claim—not proof of epistemic independence.

## Replication protocol

A single scenario remains the smallest inspectable comparison block. For a study worth sharing, use the parent protocol in [`SCENARIO_BUNDLES.md`](SCENARIO_BUNDLES.md):

1. predeclare every capsule and seed block;
2. use several stories and off-script actions;
3. record story/model/replicate strata explicitly;
4. require one comparable rating contract;
5. publish all children and hidden assignments before execution;
6. externally retain the public commitment when discard resistance matters;
7. preserve every completed, refused, and failed cell;
8. seal each fully rated block without unblinding it;
9. unblind only after all scheduled blocks are sealed; and
10. analyze the rater-level export under a separately declared ordinal/statistical model.

Rev0163 retains rev0162's preregistration, fixed schedule, optional witness gate, all-child publication, seal-before-unblind discipline, exact resume, and rater-level export while making continuation mode and capsule-bound narrator reset part of every child contract. It still does not calculate inferential statistics, prove rater/provider independence, or verify an external signature or timestamp.

## Recovery and refusal

`run.json` is authoritative; `NEXT.md` is a deterministic pointer. If only `NEXT.md` is missing or stale:

```bash
./lacuna scenario recover RUN_PATH --format markdown
```

Recovery refuses when an authoritative artifact, digest, clone state, condition mapping, context custody declaration, rating, or report no longer reconstructs exactly. It does not rewrite evidence to make a broken run pass.

## Trust boundary

The scenario runner proves much less—and more useful—than a magical experiment oracle:

- it proves local artifact consistency under Lacuna's schemas and canonical digests;
- it proves the accepted clone state passed Lacuna verification at the frozen boundary;
- it detects edits, persistent-context drift, missing or reused post-checkpoint narrator contexts, inconsistent checkpoint/capsule declarations, cross-cell declared context reuse, duplicate declared invocation IDs, premature cell mutation, and early unblinding within the retained run;
- it does not prove honest host randomization, absence of discarded unpublished runs, provider identity, fresh memory, hidden-prompt equality, human blindness, model compliance, or causal efficacy;
- same-filesystem directory publication prevents a normal reader from seeing an incrementally constructed authoritative run, but is not a distributed transaction or hostile-host boundary; and
- story-ledger mutation and sidecar publication remain separate durability domains.
