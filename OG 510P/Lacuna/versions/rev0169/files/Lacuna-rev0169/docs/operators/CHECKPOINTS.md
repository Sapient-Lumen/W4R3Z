# Lower-level source-bound retcon checkpoint protocol

This is the inspectable exchange protocol between Lacuna's custody kernel and the generate–roll out–judge–compress pattern discussed in Gwern's [“Better Fiction via Retcon Planning”](https://gwern.net/blog/2026/llm-retcon).

**Normal operators should use [`CHECKPOINT_RUNS.md`](CHECKPOINT_RUNS.md).** The managed path wraps these same schemas and kernel operations in an audited run directory with fixed provider routes, invocation receipts, exact stage topology, one generated next action, pointer-only recovery, and retry-safe commit/recovery. The commands on this page remain the protocol substrate for custom hosts, experiments, and manual inspection.

A checkpoint is **not** an ordinary play turn and it is **not** freeform multi-agent brainstorming. It is a finite artifact walk:

```text
parent opens exact request
  -> generator returns candidates
  -> provenance-blind judge returns scores + deterministic winner
  -> compressor returns one bounded state card + narrow proposal body
  -> parent assembles exact proposal and custody source
  -> verifier returns advisory pass/refuse
  -> kernel review prepares and rolls back exact mutation
  -> parent commits or exactly recovers it
```

The parent may be a person, a tool-capable ChatGPT/Codex session, another frontier model, or a small host program. Workers never commit. Lacuna manufactures complete least-context cards; it does not call model vendors or prove that a host created isolated subagents.

## The two entrances people should not confuse

| Human intent | Correct entrance | Result |
|---|---|---|
| “Will you DM?” / continue play | `./lacuna play start ...` or `./lacuna turn run begin ...` | Starts or resumes an audience-facing turn. |
| “Pause and compare hidden explanations” | `./lacuna checkpoint run begin ...` | Opens one resumable source-bound planning run. |

A fresh ChatGPT should not make the player learn checkpoint vocabulary. It should start play. The parent can open a checkpoint later when hidden causal structure is thin, a reveal is approaching, alternatives are collapsing too early, or a bounded planning comparison would be useful.

## What the checkpoint protocol actually enforces

The checkpoint request contains:

- one immutable `lacuna.turn-request.v4` with `request_purpose: "checkpoint"`;
- one source-bound `lacuna.turn-grant.v2` with profile `checkpoint`;
- the exact expected cube head and turn-packet digest;
- a deterministic protected-state projection;
- the exact set of existing unknown IDs;
- the candidate count, rollout horizon, compression budget, operation budget, score dimensions, weights, and selection rule;
- exactly one generated candidate slot per declared candidate and exactly one ordered rollout beat per declared horizon turn;
- a machine-readable four-role workflow and provider aliases.

The checkpoint grant is deliberately narrower than a director grant. It may create or revise tentative hidden hypothesis records, but it cannot:

- publish an assertion as an observation;
- close an existing unknown;
- select, prune, or reweight worlds;
- treat aesthetic score as evidence;
- raise a hidden assignment above `soft`;
- open or operate fair-play seals;
- write an arbitrary source supplied by a worker.

Assembly, not the compressor, prepends the exact selection-custody source. That source binds digests of the request, candidates, judgment, protected state, selected candidate, and compressed state card.

## What it does not enforce

A passing checkpoint does not prove:

- that the candidates are imaginative, independent, or good;
- that separate provider calls were made;
- that one model did not recognize its own prose;
- that the judge is unbiased or calibrated;
- that the selected explanation is true;
- that the method improves fiction;
- that a provider honored context isolation merely because a card requested it.

`blind_review: true` has one exact meaning: generator provenance and generation notes are removed from the judge card, and candidates are sorted by candidate ID. It is **provenance-blind**, not semantically anonymous, randomized, or cryptographically independent.

## The lower-level stateless operator walk

This path has no `run.json`, no `NEXT.md`, no fixed per-role provider routes, no invocation receipts, and no built-in resume state. The custom host owns those duties.

Set a private artifact directory. Keep every file; later artifacts bind earlier files by digest.

```bash
CUBE=/path/to/cube-or-selected-library
RUN=/path/to/private/checkpoint-$(date +%Y%m%d-%H%M%S)
mkdir -p "$RUN"
```

### 1. Freeze the request and protected state

```bash
./lacuna checkpoint begin "$CUBE" \
  --trigger "Several hidden explanations fit; compare them before the next reveal." \
  --candidate-count 4 \
  --rollout-horizon-turns 4 \
  --compression-max-chars 6000 \
  --max-operations 32 \
  > "$RUN/00-request.json"
```

Do not edit `00-request.json`. If the cube head changes before review, the checkpoint is stale and must be reopened.

### 2. Manufacture and dispatch the generator card

```bash
./lacuna checkpoint card "$RUN/00-request.json" \
  --role lacuna-retcon-generator \
  > "$RUN/10-generator-card.json"

./lacuna checkpoint dispatch "$RUN/10-generator-card.json" \
  --provider chatgpt --format markdown \
  > "$RUN/11-generator-dispatch.md"
```

Give one worker the **complete dispatch/card unchanged**. Save its one JSON response exactly as:

```text
20-candidates.json    # lacuna.checkpoint-candidates.v1
```

The generator sees privileged planner context. Its output template already contains exactly the declared candidate count and exactly one ordered rollout beat per declared horizon turn, so a worker does not have to infer array cardinality. Candidates and rollout beats remain advisory and noncanon.

### 3. Manufacture and dispatch the judge card

```bash
./lacuna checkpoint card "$RUN/00-request.json" \
  --role lacuna-retcon-judge \
  --candidates "$RUN/20-candidates.json" \
  > "$RUN/30-judge-card.json"

./lacuna checkpoint dispatch "$RUN/30-judge-card.json" \
  --provider chatgpt --format markdown \
  > "$RUN/31-judge-dispatch.md"
```

Save the exact response as:

```text
40-judgment.json      # lacuna.checkpoint-judgment.v1
```

The judge card contains one complete score slot for every canonicalized candidate ID. The judge must score every candidate on every declared dimension. Weighted scores are checked mechanically. The winner is the highest-scoring eligible candidate; a tie goes to the lexicographically smallest candidate ID. The judge cannot pick a lower-scoring favorite in prose.

### 4. Manufacture and dispatch the compressor card

```bash
./lacuna checkpoint card "$RUN/00-request.json" \
  --role lacuna-retcon-compressor \
  --candidates "$RUN/20-candidates.json" \
  --judgment "$RUN/40-judgment.json" \
  > "$RUN/50-compressor-card.json"

./lacuna checkpoint dispatch "$RUN/50-compressor-card.json" \
  --provider chatgpt --format markdown \
  > "$RUN/51-compressor-dispatch.md"
```

Save the response as:

```text
60-compression.json   # lacuna.checkpoint-compression.v1
```

The compressor receives only the selected candidate, protected state, judgment, packet identity template, and narrow operation list. It cannot silently blend rejected candidates. Empty operations are valid when the useful result is only a compact planning card.

### 5. Assemble the proposal in the parent

```bash
./lacuna checkpoint assemble \
  "$RUN/00-request.json" \
  "$RUN/20-candidates.json" \
  "$RUN/40-judgment.json" \
  "$RUN/60-compression.json" \
  > "$RUN/70-proposal.json"
```

Assembly validates the entire digest chain, retains the exact compressor artifact, recomputes selection evidence, prepends the custody source, and emits a packet-bound turn proposal. A worker does not perform this step.

### 6. Manufacture and dispatch the verifier card

```bash
./lacuna checkpoint card "$RUN/00-request.json" \
  --role lacuna-retcon-verifier \
  --proposal "$RUN/70-proposal.json" \
  > "$RUN/80-verifier-card.json"

./lacuna checkpoint dispatch "$RUN/80-verifier-card.json" \
  --provider chatgpt --format markdown \
  > "$RUN/81-verifier-dispatch.md"
```

Save the response as:

```text
90-verifier.json      # lacuna.checkpoint-verifier-return.v1
```

The verifier begins at `refuse`. A claimed pass is valid only when every required check is true, no blocking finding remains, and the recommended action is `commit`. Its verdict is advisory; it has no write authority.

### 7. Run kernel review without mutation

```bash
./lacuna checkpoint review "$CUBE" \
  "$RUN/00-request.json" \
  "$RUN/20-candidates.json" \
  "$RUN/40-judgment.json" \
  "$RUN/70-proposal.json" \
  "$RUN/90-verifier.json" \
  > "$RUN/100-review.json"
```

Review performs the ordinary turn kernel's full preparation inside a transaction, freezes the exact event envelope and post-state digests, then rolls back. `mechanical_status: "pass"` is readiness, not commitment and not a head reservation.

### 8. Commit once, or recover the exact already-committed change

```bash
./lacuna checkpoint commit "$CUBE" \
  "$RUN/00-request.json" \
  "$RUN/20-candidates.json" \
  "$RUN/40-judgment.json" \
  "$RUN/70-proposal.json" \
  "$RUN/90-verifier.json" \
  "$RUN/100-review.json" \
  > "$RUN/110-receipt.json"
```

Only `overall_status: "accepted"` proves the checkpoint reached the cube. Retrying the exact command can recover the exact receipt without duplicate events. If later valid changes have advanced the live head, recovery verifies the historical request-head prefix and exact durable checkpoint event chain before reconstructing the receipt. Changed input, forged ledger history, changed grant, or changed preparation refuses.

Present only the accepted receipt's top-level `narration` to the player. Do not expose candidate files, judgment, state card, or planner context.

The lower-level stateless path does not manufacture a fresh-narrator capsule. A custom host using this surface must compile an equivalent winner-only continuation artifact and start a new narrator context itself. Normal operators should use the managed run and `checkpoint run next-turn`, which authenticates the complete retained chain, opens one exact audience-only ordinary turn, and emits the complete fresh-narrator dispatch. `checkpoint run narrator-capsule` remains the lower-level checkpoint-only artifact.

## Role matrix

| Role | Receives | Returns | Must not do |
|---|---|---|---|
| `lacuna-retcon-generator` | Policy, protected state, privileged planner context | `lacuna.checkpoint-candidates.v1` | Select winner, mutate cube, narrate to player |
| `lacuna-retcon-judge` | Policy, protected state, provenance-stripped sorted candidate view | `lacuna.checkpoint-judgment.v1` | Use provider preference, edit candidates, commit |
| `lacuna-retcon-compressor` | Selected candidate, judgment, protected state, narrow grant | `lacuna.checkpoint-compression.v1` | Add source, close unknowns, harden/select/reweight worlds |
| `lacuna-retcon-verifier` | Exact request and assembled proposal | `lacuna.checkpoint-verifier-return.v1` | Rewrite proposal, claim kernel acceptance, commit |

All cards are `lacuna.checkpoint-task-card.v1`. Their task IDs are deterministic functions of request digest, role, and ordered upstream digest chain. Validation recomputes that identity, enforces the role-specific upstream order, and binds the output template to the exact task, checkpoint, and request.

## Provider names

Use one provider value with `checkpoint dispatch`:

| Host | `--provider` | Bundled role aliases |
|---|---|---|
| Portable/manual | `portable` | canonical hyphenated names |
| Codex | `codex` | underscore custom-agent names |
| Claude Code | `claude-code` | hyphenated subagent names |
| Gemini CLI | `gemini-cli` | hyphenated subagent names |
| ChatGPT / human bridge | `chatgpt` | explicit ChatGPT role labels |

Provider aliases are routing metadata. They do not attest which model ran, which tools it had, or whether contexts were isolated.
Each dispatch is revalidated by exact recomputation from its embedded task card and provider route; this detects envelope drift, but it still does not attest who executed it.

## ChatGPT: what a 20-year-old player should be able to do

### Just play in an ordinary chat

She can say **“Will you DM?”** and play immediately. The supplied ChatGPT instructions tell the model to start a scene, ask at most one bundled premise question when genuinely necessary, keep Lacuna internals backstage, and say once when the session is chat-only rather than durably committed.

No CLI ritual should be required from the player.

### Use a real cube through a human bridge

A person with the files runs the parent commands above, uploads or pastes only the generated dispatch to the appropriate ChatGPT conversation, saves the exact JSON response, and advances to the next command. Separate conversations are useful role-dedicated contexts, but they are not automatically a confidentiality proof.

For ordinary turns, use `docs/operators/CHATGPT.md`. For this four-stage checkpoint, use this document.

### Use a connected/tool-capable ChatGPT parent

A parent that truly has shell/filesystem access can run the same commands itself. The request's `workflow.host_directive` tells a capable parent to delegate each exact card to a role-dedicated context. The cube can therefore make subagent use more likely and make the required handoff unambiguous, but it cannot force a product to expose or use a subagent API.

The parent should:

1. retain every exact artifact in a private directory;
2. ask one role context to consume one complete card;
3. accept only one JSON root object;
4. run the next Lacuna validator before trusting it;
5. reserve assemble, review, commit, and player presentation for itself.

When subagents are unavailable, the parent may execute cards serially in one context. It must not describe that fallback as independent judging or context isolation.

## Recommended topology by capability

| Capability | Topology | Honest claim |
|---|---|---|
| One conversation, no tools | Chat-only play; no governed checkpoint commit | Playable fiction, no durable cube mutation |
| Human plus several chats | Human parent; four role-dedicated chats | Exact artifact separation, not cryptographic isolation |
| One tool-capable frontier context | Parent executes cards serially | Full validation and custody, weak independence |
| Parent plus subagents | Four role contexts; parent owns transitions | Best bundled topology; isolation depends on host |
| Multiple model families | Generator, judge, compressor, verifier may use different providers | Stronger procedural diversity, still not proof of independence or quality |

Do not automatically assume “more agents” means better output. The important invariant is that each role receives the exact minimum artifact and cannot acquire parent authority from its prompt.

## Why the datacube matters beyond fiction

The useful general pattern is not “four agents.” It is **request-bound context manufacture**:

- freeze an exact state projection;
- assign a narrow role and authority surface;
- bind all handoffs by canonical digest;
- require a typed return;
- validate before manufacturing the next context;
- retain provenance and explicit nonclaims;
- reserve mutation for one parent/kernel boundary.

That pattern can support scientific proposal–critic–compressor–verifier workflows, model comparisons, or long-running investigations. A future adapter should define new task/output schemas rather than pretending the fiction score rubric is a scientific truth metric. Lacuna's cube can carry the exact context across turns and CLI invocations; it should not erase domain-specific epistemology by treating every workflow as retcon planning.

## Refusal and recovery guide

- **Bad task ID or upstream digest:** discard the worker artifact and regenerate the card from retained exact upstream files.
- **Wrong schema or prose around JSON:** ask the worker to return only the card's exact root JSON object; do not manually repair hidden identities.
- **Candidate count or unknown set mismatch:** rerun the generator card. Do not delete inconvenient unknowns.
- **Judgment selection mismatch:** rerun the judge. Selection is deterministic after eligibility and scores.
- **Compression exceeds budget or uses forbidden operations:** rerun the compressor with the same card.
- **Verifier refuses:** inspect findings, then reopen or rerun the appropriate upstream stage. Never flip the status by hand.
- **Stale head at review:** retain the old run for audit and begin a new checkpoint against the current cube.
- **Commit response lost:** retry the exact commit command with the exact files. Recovery can authenticate the exact historical commit even after later valid writes; it refuses rather than blessing a look-alike.

## Retention checklist

Retain at least:

```text
00-request.json
10-generator-card.json
20-candidates.json
30-judge-card.json
40-judgment.json
50-compressor-card.json
60-compression.json
70-proposal.json
80-verifier-card.json
90-verifier.json
100-review.json
110-receipt.json
```

Dispatch Markdown is useful operational evidence but the JSON cards and returns are the digest-bearing artifacts. Keep the directory private: generator, compressor, proposal, and review artifacts may contain hidden campaign state.
