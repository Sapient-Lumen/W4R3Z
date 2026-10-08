# Start here

Choose one door; everything else is reference material:

- **Player:** [`PLAY_NOW.md`](PLAY_NOW.md) — say “Will you DM?” and begin.
- **Gwern or another researcher:** [`FOR_GWERN.md`](FOR_GWERN.md) — the claim, nonclaims, and shortest experiment path.
- **Human or model operator:** [`OPERATE_LACUNA.md`](OPERATE_LACUNA.md) — capability-first commands, recovery, fresh continuation, and experiment controls.

Lacuna rev0169 is an epistemic-world custody kernel with a player-only entrance, managed source-bound retcon checkpoints, a checkpoint-bound complete public-history census, exact four-condition scenario runs, preregistered replicated bundles, post-primary-rating method-identifiability assessment, parent-gated bundle child unblinding, and a send-ready test-harness, license, and scenario-template polish pass.

## One-sentence model

**Store what happened, who says and believes what, which hidden worlds remain possible, what explicitly depends on what, how expensive revision is, which selected secrets were provably bound earlier, and why planning attention moved among surviving worlds—without pretending those categories are one canon paragraph.**

## Player entrance

Open [`PLAY_NOW.md`](PLAY_NOW.md), say “Will you DM?”, and speak or act normally. Everything below is operator material.

## Say “Will you DM?”

For a shell-capable host, this is the complete start:

```bash
rm -rf /tmp/lacuna-play /tmp/lacuna-runs
./lacuna play start /tmp/lacuna-play \
  --root /tmp/lacuna-runs \
  --bootstrap \
  --profile orchestrated \
  --format markdown
```

With no `--player-input`, the retained text is exactly `Will you DM?`. The new packet uses `lacuna.turn-request.v3` and records `input.kind = session-control`. The command creates or selects one campaign, opens one run, and prints its first audited next action. It does not invoke a model or narrate.

Copy the run path and inspect one pointer:

```bash
RUN_PATH=$(find /tmp/lacuna-runs -mindepth 1 -maxdepth 1 -type d | head -n 1)
cat "$RUN_PATH/NEXT.md"
```

For the delegated planner stage, render a self-contained handoff:

```bash
./lacuna turn run dispatch "$RUN_PATH" \
  --provider chatgpt \
  --format markdown \
  > /tmp/lacuna-planner-handoff.md
```

The handoff embeds the exact task card as `input_document`. A chat worker need not open the local file path. A Codex, Claude Code, Gemini CLI, or portable route receives the same contract under a provider-specific alias.

Save the worker’s exact one-object JSON return and run the accept command printed in the dispatch. Repeat until the parent owns commit. Only the final receipt narration may be presented.

Ordinary ChatGPT without a connected host can begin a scene immediately, but should state once that the chat is not yet committed to a Lacuna cube. Use `integrations/chatgpt/PROJECT_INSTRUCTIONS.md` and the human bridge in `docs/operators/CHATGPT.md`.

## Pause backstage for a managed retcon checkpoint

Do not ask the player to run this. A tool-capable parent may open it between turns when several hidden explanations fit and commitment pressure is rising:

```bash
rm -rf /tmp/lacuna-checkpoint-runs
./lacuna checkpoint run begin /tmp/lacuna-play \
  --root /tmp/lacuna-checkpoint-runs \
  --trigger "Compare bounded explanations before the next reveal." \
  --candidate-count 4 \
  --rollout-horizon-turns 4 \
  --provider chatgpt \
  --format markdown
```

The run freezes a `lacuna.turn-request.v4` checkpoint packet, binds the exact source cube path, fixes provider routes for generator, judge, compressor, and verifier, creates `run.json`, and prints one audited next action. Copy the run path and follow only its pointer:

```bash
CHECKPOINT_RUN=$(find /tmp/lacuna-checkpoint-runs -mindepth 1 -maxdepth 1 -type d | head -n 1)
cat "$CHECKPOINT_RUN/NEXT.md"
./lacuna checkpoint run dispatch "$CHECKPOINT_RUN" --format markdown
```

Give the complete dispatch to the named worker. Save exactly one JSON object and run the generated `checkpoint run accept` command. The templates contain the exact candidate count, one ordered future beat per horizon turn, and one score slot per canonical candidate. Accepted and failed attempts are retained as ordered host-declared invocation receipts. At `ready-to-commit`, only the parent runs `checkpoint run commit`.

For a clean test of compression and forgetting, do not continue in the same narrator context. After commit and when the next player input arrives:

```bash
./lacuna checkpoint run next-turn "$CHECKPOINT_RUN" \
  --player-input-file /tmp/next-player-input.txt \
  --provider chatgpt \
  --format markdown
```

The command opens one audience-only solo turn at the checkpoint head and emits one exact `lacuna.checkpoint-continuation-dispatch.v2`. Give that whole dispatch to a new narrator context, save its single proposal object, and use the printed ordinary-turn accept command. For a complete local durable-turn claim, first run `lacuna history complete CHECKPOINT_RUN --run-root TURN_RUNS` and add `--public-history public-history.json`; `history build` remains the explicitly partial-list path. Same-context continuation remains a useful control and play path, but it is experimentally confounded. Read `docs/operators/FRESH_NARRATOR.md` and `docs/operators/PUBLIC_HISTORY.md`.

Read `docs/operators/CHECKPOINT_RUNS.md` for the complete ChatGPT/Codex/Claude/Gemini and human-bridge walk. `docs/operators/CHECKPOINTS.md` is the lower-level stateless protocol for custom hosts.

## Run the acceptance path

```bash
./lacuna artifact check --strict-members --format markdown
./lacuna turn run status "$RUN_PATH" --format markdown
./lacuna turn run recover "$RUN_PATH" --format markdown
./lacuna verify /tmp/lacuna-play
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 tools/run_acceptance.py --timeout 60
```

Expected properties:

1. Safe bootstrap occurs only on an absent or empty path.
2. The first campaign is selected and resolves to a verified cube.
3. Exact input and `session-control` kind are retained before any fictional mutation.
4. `auto` selects the deterministic topology from packet-visible policy.
5. `run.json` strictly binds run, cube, request, proposal, expected head, packet digest, artifact set, status, and next action.
6. `NEXT.md` names one owner and prints the provider-dispatch command for delegated stages.
7. `lacuna.agent-dispatch.v1` embeds the exact task card, role, input kind, return schema, parent command, and non-authority.
8. The audience-only narrator card is manufactured without planner context or private rationale.
9. A final proposal cannot become ready until its exact normalized change succeeds through the real kernel and is rolled back.
10. Commit replays the frozen envelope exactly; a matching post-commit crash can be authenticated without duplicate events, even after later valid turns advance the live head.
11. Linked, oversized, changed, relabelled, cross-turn, or wrong-stage sidecar members refuse.
12. `turn run recover` can replace only deterministic `NEXT.md`; it never invents authoritative custody.
13. Managed checkpoint state, exact source-path binding, fixed heterogeneous provider routes, accepted/failed invocation custody, stage topology, pointer recovery, verifier refusal, receipt authentication, and later-head commit recovery are exercised end to end.
14. Committed checkpoints compile deterministic narrator capsules that exclude rejected futures; `checkpoint run next-turn` binds one capsule to the exact next input and ordinary turn, and scenario treatments enforce persistent-context controls versus fresh dispatch-bound continuation.
15. Scenario checkpoints require a following scripted ordinary turn, so every tested checkpoint has an observable continuation.
16. A committed checkpoint can open one exact fresh source-bound continuation turn and emit a single validated dispatch; invalid public-history custody fails before the turn is created.
17. `lacuna.public-history.v2` authenticates exact player input and accepted narration. `history build` labels an explicit run list as `not-claimed`; `history complete` binds a `complete-before-checkpoint` ledger census to one committed checkpoint and refuses missing, duplicate, or mismatched managed-run prose. `lacuna.public-history-view.v2` removes parent-side IDs, hashes, and event positions before narrator delivery.
18. Scenario runs preregister operator-only and filesystem-only exact canaries before execution, freeze and authenticate a scan before blind rating, retain leak-detected blocks instead of rerunning them, and bind each scan into replicated block seals.
19. The acceptance suite and current revision records are under `docs/acceptance/ACCEPTANCE_rev0169.json`.

## Try governed evidence reweighting

After creating at least two live candidate worlds and one active evidence assertion, review the complete bank:

```bash
./lacuna particle-bank /tmp/lacuna-play
./lacuna particle-update-review /tmp/lacuna-play ast_example \
  > /tmp/particle-review.json
```

Use the returned `expected_bank_sha256` and assess every listed world exactly once:

```bash
./lacuna particle-update /tmp/lacuna-play ast_example \
  --expected-bank-sha256 DIGEST \
  --assessment world.one=0.75 \
  --assessment world.two=0.25 \
  --reason "Recorded evidence changes planning attention."
```

The update changes weights only. It does not select, prune, resample, revise, disclose, or canonize a world. The evidence assertion is a single-use multiplicative factor. If it is later superseded, `particle-bank` reports reweighting debt instead of silently repairing history.

## Try factor-ledger reconciliation

After an applied evidence assertion is superseded, inspect the complete current-epoch replay:

```bash
./lacuna particle-reconciliation-review /tmp/lacuna-play \
  > /tmp/reconciliation-review.json
```

Use the returned `expected_reconciliation_sha256` exactly once:

```bash
./lacuna particle-reconcile /tmp/lacuna-play \
  --reconciliation-id prc.example \
  --expected-reconciliation-sha256 DIGEST \
  --reason "Exclude withdrawn evidence and replay every active factor."
./lacuna particle-reconciliations /tmp/lacuna-play
```

The old update remains immutable. The reconciliation records the epoch baseline, every included and excluded factor, complete per-world log-space arithmetic, and the repaired vector. World mutation starts a new factor epoch instead of silently reusing stale likelihoods. Audience and world-scoped director contexts cannot see or authorize this global operation.

## Run the comparison that can falsify Lacuna

This is backstage research, not a player command:

```bash
./lacuna scenario template /tmp/lacuna-play > /tmp/capsule.json
# edit the exact script and one fixed model/sampling/budget/rating policy
./lacuna scenario begin /tmp/lacuna-play /tmp/capsule.json \
  --root /tmp/lacuna-scenarios --format markdown
```

Follow the run's `NEXT.md`. Dispatch one opaque cell, execute it under the preregistered context boundary, record one exact return, and repeat. After the fourth cell, inspect the private exact-token result with `./lacuna scenario contamination RUN_PATH --format markdown`; do not disclose it to raters. Give raters only `70-blind-rating-packet.json`; never give them the assignment, drivers, canary sources, or scan. See [`docs/operators/CONTAMINATION_CANARIES.md`](docs/operators/CONTAMINATION_CANARIES.md) and [`docs/operators/SCENARIO_CAPSULES.md`](docs/operators/SCENARIO_CAPSULES.md).

For replication, fix the entire roster before observing any result:

```bash
./lacuna scenario bundle template \
  --block /tmp/lacuna-play /tmp/capsule.json \
  --block /tmp/lacuna-play /tmp/capsule.json \
  --minimum-witnesses 1 > /tmp/bundle-plan.json
./lacuna scenario bundle begin /tmp/bundle-plan.json \
  --root /tmp/lacuna-scenario-bundles --format markdown
```

Externally retain the public commitment, record the required witness receipt descriptions, and then obey only the bundle `NEXT.md`. Seal each complete block without unblinding it. The final unblind is allowed only after every block is sealed. See [`docs/operators/SCENARIO_BUNDLES.md`](docs/operators/SCENARIO_BUNDLES.md).

## Try governed revision

After creating a claim, world, and assignment, run:

```bash
./lacuna revision-impact /tmp/lacuna-play asn_example > /tmp/impact.json
```

Read `impact_sha256`, blockers, burden, ambient footprint, and explicit consequences. Apply the successor only with that exact digest:

```bash
./lacuna world-revise /tmp/lacuna-play asn_example false \
  --assignment-id asn_example_rev2 \
  --expected-impact-sha256 DIGEST \
  --reason "Documented correction of the current hypothesis."
```

The predecessor remains in assignment history. Any separately committed intervening event makes the digest stale; reviewed operations in one atomic change-set use its shared base head. A hard commitment or binding consequence blocks revision. Softer consequence links survive as repair debt and can now be replaced through a reviewed atomic lineage event.

## Try consequence repair

```bash
./lacuna consequence-repair-frontier /tmp/lacuna-play
./lacuna consequence-repair-review /tmp/lacuna-play csq_example > /tmp/repair.json
./lacuna consequence-replace /tmp/lacuna-play \
  csq_example asn_example_rev2 question qst_example motivates \
  --severity material \
  --rationale "Reviewed successor dependency." \
  --expected-repair-sha256 DIGEST \
  --reason "Replace obsolete consequence custody."
```

Replacement preserves the old link, creates a new one, and records a separate repair identity at one event sequence. It refuses inactive endpoints, no-op replacements, duplicate active edges, stale reviews, and post-repair cycles.

## Try a fair-play seal

Prepare a secret opening without writing it to the cube:

```bash
printf '%s\n' '{"culprit_id":"character.ada"}' > /tmp/culprit.json
./lacuna seal prepare /tmp/lacuna-play /tmp/culprit.json \
  --seal-id seal.case-culprit > /tmp/opening.json
```

Publish only the digest, then export a retainable receipt:

```bash
./lacuna seal create /tmp/lacuna-play /tmp/opening.json \
  --purpose mystery --label "Case culprit"
./lacuna seal receipt /tmp/lacuna-play seal.case-culprit > /tmp/receipt.json
```

Keep `/tmp/opening.json` outside the cube. Retain or externally anchor `receipt_sha256`. Later:

```bash
./lacuna seal verify /tmp/lacuna-play /tmp/opening.json
./lacuna seal reveal /tmp/lacuna-play /tmp/opening.json \
  --reason "The authored solution was reached."
```

The seal proves exact-opening continuity only. It does not make the payload true, establish a trusted timestamp, prove uniqueness, or certify mystery fairness. Seal lifecycle operations are host-only and absent from ordinary model turns.

## Recommended host pattern

```text
exact player input retained outside the event ledger
   |
turn run begin
   |-- source-bound packet + immutable grant
   |-- deterministic solo / pair / full plan
   |-- first safe draft or digest-bound role card
   v
run.json + NEXT.md
   |-- one owner
   |-- one complete input artifact
   |-- one required schema
   |-- one exact next command
   v
parent and optional bounded roles return exact JSON
   |
turn run accept audits and manufactures the next stage
   |
turn run commit asks the kernel to accept atomically
   |
accepted receipt -> present top-level narration
```

The same executable works as a human CLI, subprocess tool, direct Python library, or future narrow Action/App/MCP adapter. Provider instructions and orchestration policy live outside the custody kernel; the source-bound grant, expected head, validation, and atomic receipt remain the enforcement boundary. Lower-level packet/plan/card commands remain inspectable. The bundled launcher uses Python `-S` so ambient site packages do not enter the runtime boundary.

## Read in this order

1. `PLAY_NOW.md`
2. `OPERATE_LACUNA.md`
3. `PLAY_WITH_AN_LLM.md`
4. `docs/operators/ONE_SENTENCE_START.md`
5. `docs/operators/FRESH_NARRATOR.md`
6. `docs/operators/PUBLIC_HISTORY.md`
7. `docs/design/THREE_SERIOUS_QUESTIONS.md`
8. `docs/NORTHSTAR.md`
9. `docs/design/GWERN_GIFT_TEST.md`
10. `docs/operators/MODEL_ENTRANCE.md`
11. `docs/operators/TURN_RUNS.md`
12. `docs/operators/CHATGPT.md`
13. `docs/operators/MULTI_AGENT.md`
14. `docs/operators/CHECKPOINT_RUNS.md`
15. `docs/operators/SCENARIO_CAPSULES.md`
16. `docs/operators/CONTAMINATION_CANARIES.md`
17. `docs/operators/SCENARIO_BUNDLES.md`
18. `docs/operators/CHECKPOINTS.md`
19. `docs/architecture/ARCHITECTURE_rev0169.md`
20. `docs/protocols/TURN_CONTRACT.md`
21. `docs/protocols/CONTEXT_ACCESS.md`
22. `docs/protocols/INTERACTION_SURFACES.md`
23. `docs/protocols/FACTOR_LEDGER_RECONCILIATION.md`
24. `docs/protocols/PARTICLE_BANK.md`
25. `docs/protocols/FAIR_PLAY_SEALS.md`
26. `docs/protocols/CONSEQUENCE_REPAIR.md`
27. `docs/design/BEYOND_RETCON_PLANNING.md`
28. `docs/research/RESEARCH_rev0169.md`
29. `docs/audits/AUDIT_rev0169.md`
30. `docs/audits/DIRECT_UPLOAD_FEEDBACK_AUDIT_rev0163.md`

## Sharp boundaries

- Unknown remains unknown.
- A selected candidate world is not global truth.
- A reconciled particle bank is repaired planner attention, not objective posterior truth.
- Ambient exposure is not causality.
- Commitment is mutation policy, not confidence.
- A burden score is not a probability or fairness certificate.
- A consequence link is authored custody, not discovered physics.
- A consequence replacement is forward repair, not rollback or proof of equivalence.
- A fair-play seal is byte continuity, not truth, authorship, uniqueness, trusted time, or narrative fairness.
- Narration is presentation; accepted typed operations mutate state.
- Perspective context and planner context never share one widened object.
- The cube does not call an LLM or retain transcript bodies.
- Provider instruction files guide behavior but do not grant authority; only a source-bound write grant and accepted commit mutate state.
- A turn run, checkpoint run, invocation receipt, orchestration plan, task card, or verifier pass is a sidecar artifact—not a story-ledger event or provider attestation.
- Digest continuity proves exact artifact binding, not model compliance or semantic truth.
- A chat-only game is not a committed Lacuna campaign.
- A fresh-narrator capsule or continuation dispatch is private context custody, not canon, provider attestation, or proof of forgetting.
- A public-history artifact proves exact custody only for the committed runs explicitly supplied; it does not prove transcript completeness or semantic entailment.
- A scenario bundle is experiment custody, not a player requirement, statistical conclusion, provider attestation, or proof of independent subagents.
