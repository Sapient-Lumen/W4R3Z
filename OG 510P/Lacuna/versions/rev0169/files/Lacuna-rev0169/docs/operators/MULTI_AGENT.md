# Multi-agent and least-context operation

Lacuna uses multiple roles to create asymmetric information boundaries, not because more agents are presumed to be wiser.

The parent owns the request, sidecar transitions, proposal acceptance, exact preparation, commit, and player presentation. Workers return bounded data only.

## Topologies

| Mode | Walk | Intended use |
|---|---|---|
| `solo` | parent proposal | Simple turn, weak host, or ordinary ChatGPT bridge |
| `pair` | planner → audience-only narrator → parent proposal | Ordinary director turn |
| `full` | planner → narrator → proposal builder → verifier | High-impact state work or an evaluation ablation |

`auto` chooses deterministically from packet-visible policy. It is not a global claim that the chosen number of agents is optimal.

Retcon checkpoints use a separate fixed planning topology:

| Role | Least context | Output |
|---|---|---|
| generator | protected state + planner context + policy | exact candidate set with bounded rollout beats |
| judge | provenance-stripped, canonicalized candidates + rubric | complete scores + deterministic winner |
| compressor | selected candidate only + protected state + narrow grant | bounded state card + proposal body |
| verifier | exact request + assembled proposal | advisory pass/refuse |

The parent alone validates the raw chain, assembles custody, runs the kernel, commits, recovers, and presents narration. In a managed checkpoint run, all four provider routes are fixed at begin time and every accepted or failed attempt receives one ordered host-declared invocation receipt. For the clean information-bottleneck condition, a fifth context boundary follows commit: `checkpoint run next-turn` emits one source-bound dispatch and a new narrator receives only that complete dispatch. This topology tests distinct failure modes; it does not imply that more agents are intrinsically wiser.

## Why planner and narrator separate

The planner may need hidden candidate worlds, commitment and consequence state, private rationale, and possible operations. The narrator should receive only:

- audience-safe current context;
- exact session/play input;
- an approved observable beat plan;
- style and return constraints.

The narrator card omits planner context, hidden weights, private notes, candidate operations, and unrevealed openings. This reduces leakage pressure and makes the intended boundary inspectable.

A monolithic model can still ignore or reconstruct hidden information from prior memory. Even four fresh checkpoint workers do not help when the continuing narrator remains in the contaminated parent conversation. Use `checkpoint run next-turn` and route its complete dispatch to a new narrator context for the clean condition. Hard isolation remains a host responsibility.

## Generated dispatch instead of prompt guessing

At each delegated stage:

```bash
./lacuna turn run dispatch RUN_PATH --provider PROVIDER --format markdown
```

The dispatch embeds exactly one `lacuna.turn-task-card.v1` as `input_document`, names the provider alias, and gives one return contract. It instructs the worker to perform the role rather than summarize the handoff.

The worker may read and reason from that card and return its structured refusal when needed. It may not inspect unrelated run artifacts, edit the sidecar, accept its own result, commit, or present proposed narration as fact.

The parent saves the exact return and runs the generated command.

For a managed retcon checkpoint, omit a provider override because the role route is already frozen in `run.json`:

```bash
./lacuna checkpoint run dispatch RUN_PATH --format markdown
```

The dispatch embeds one `lacuna.checkpoint-task-card.v1`, one provider-specific role alias, the exact save/accept command, and a failure-record command. A native-subagent parent should hand that dispatch—not the full cube and not a prose summary—to one bounded context. A human bridge can paste the same envelope into a fresh chat.

## Digest-bound context walk

Later cards bind to the packet and exact accepted upstream artifacts:

```text
packet
  └─ planner card → planner return
       └─ narrator card → narrator return
            └─ builder card → proposal
                 └─ verifier card → verifier return
                      └─ exact kernel preparation → receipt
```

A return from another turn, an edited upstream object, a valid object from the wrong stage, or a relabelled artifact refuses. The coordinator must not “fix” identity fields by copying values from the current packet.

Checkpoint cards use the same principle with a separate digest chain:

```text
request
  └─ generator card → candidates with exact rollout beats
       └─ provenance-blind judge card → judgment
            └─ compressor card → compression
                 └─ parent assembly → proposal
                      └─ verifier card → advisory return
                           └─ parent kernel review → receipt
                                └─ next-turn → continuation dispatch → fresh narrator context
```

A managed run additionally binds each role card to an ordered invocation sequence:

```text
failed attempt(s) → one accepted output receipt → next exact card
```

Each receipt fixes the role, configured provider route, provider alias, card digest, deterministic dispatch digest, expected output schema, host-declared model metadata, and either the accepted output digest or a failure class. It does not prove which model actually ran or that contexts were isolated.

The judge does not receive generator provenance or generation notes. That is provenance blinding, not semantic anonymity. The verifier receives proposal-visible material; the parent, not the verifier, recomputes the raw scores and deterministic selection.

## Parent-only authority

Only the parent may:

- choose ordinary-turn topology and, at checkpoint begin, freeze all per-role provider routes;
- invoke a worker;
- save and accept a return or record a failed attempt;
- add justified typed custody to a safe draft;
- decide whether to abandon a refused run;
- invoke commit or recovery;
- open and route the post-commit source-bound continuation turn;
- and present accepted receipt narration.

Provider routing and subagent identity are not authority grants.

## Native subagent parent pattern

A parent with native subagents should treat `NEXT.md` as the scheduling decision and the generated dispatch as the complete worker prompt:

1. Audit the run and render the current dispatch.
2. Spawn exactly one worker for the named role; do not ask it to choose the next role.
3. Give it only the dispatch and no mutation tools unless the host requires a transport tool.
4. Require one JSON object matching the named schema.
5. Return to the parent, save the exact object, and invoke `accept`; on transport or worker failure, invoke `record-failure`.
6. Re-read the newly generated `NEXT.md` rather than relying on conversation memory.
7. After checkpoint commit in the clean condition, run `checkpoint run next-turn` with the next exact player input and spawn a new narrator context that receives only the generated continuation dispatch.

Parallel generation can be useful in a future experiment, but the current managed checkpoint contract has one generator output containing the complete candidate set. Spawning several unsynchronized generators and merging their prose outside the schema would lose exact candidate cardinality and custody. A custom host can instead define an experimental aggregation layer above the current request, while leaving parent acceptance and the kernel unchanged.

## When extra roles help

Pair mode is valuable when private planning information could contaminate public narration. Full mode may help when a proposal’s serialization and independent checking are meaningful separate failure modes, especially around anchors, revision, consequence repair, conflicts, or broad writes.

Extra roles also add cost and coordination surfaces. Evaluate:

- solo versus pair versus full;
- native subagent versus separate-chat execution;
- generated dispatch versus prose-only delegation;
- same-model versus cross-model roles;
- context size, latency, cost, refusal rate, leakage, and final quality.

A weaker model may benefit more from a complete narrow card than from a long global instruction. A stronger model may still benefit because the boundary becomes reproducible and auditable.

## Scientific configuration

The same pattern can be configured as:

```text
hypothesis planner (private candidate space)
    → blinded report writer (public evidence only)
    → claim serializer (typed proposed record)
    → independent checker
    → parent acceptance authority
```

The analogy does not validate scientific claims. It preserves the distinction between hypothesis, observation, report, proposal, verification, and accepted record while giving each model only the intended slice.

## Isolation boundary

Checked-in agent definitions, empty tool lists, read-only workspaces, fresh chats, separate API calls, and capsule digests are useful controls. A Project with shared memory is not a clean isolation boundary; a fresh chat can still inherit Custom Instructions. None is cryptographic proof that a provider erased memory, denied every tool, or prevented covert leakage.

Protect the run directory according to its most privileged artifact. Never place credentials or unrevealed fair-play openings in a worker-readable directory without a stronger host boundary.

## Scenario capsules: subagent topology is now a treatment

Rev0161 introduced, rev0162 made replicable, rev0163 added the narrator reset, and rev0164 binds that reset to the exact next ordinary turn. Both `lacuna-serial` and `lacuna-role-separated` use the same four checkpoint role contracts and model policy. Serial declares one persistent context for the complete cell. Role-separated declares four fresh pairwise-distinct checkpoint contexts, then requires a fresh dispatch-bound narrator after each completed checkpoint. The narrator remains in that new context until the next checkpoint. Cross-cell and cross-block declared-context reuse is refused.

A capable parent should explicitly ask for the named subagent; do not rely on the model to infer that delegation is desirable. Give the worker only the active generated card, with no repository/run browsing and no transition tools. After a completed role-separated checkpoint, run `checkpoint run next-turn` and give the next narrator only its complete continuation dispatch; the embedded capsule digest remains the experiment join key. The parent retains exact output capture, failure recording, assembly, kernel review, accept/commit recovery, continuation routing, transcript presentation, rating custody, and unblinding.

This is an information-boundary experiment, not a claim that multiple agents are inherently better or independent. A replicated study should preregister every block and seal all children before unblinding; see [`SCENARIO_CAPSULES.md`](SCENARIO_CAPSULES.md) and [`SCENARIO_BUNDLES.md`](SCENARIO_BUNDLES.md).

## Canary boundary in comparative runs

The scenario driver is a coordinator envelope and intentionally contains a cell-specific operator-only canary. It may be supplied to one isolated cell coordinator, including a persistent-control coordinator, but must not be forwarded wholesale to nested checkpoint roles or the fresh narrator. The filesystem-only canary body is never a worker input. The frozen scan tests exact retained-output leakage across cells and scopes; it does not turn native subagents into a cryptographic isolation boundary.
