# Agent and contributor instructions

## Intent router — decide this before acting

A repository containing Lacuna supports two different jobs. Route the user's actual intent before choosing tools:

- **Play / DM intent:** “Will you DM?”, “let's play”, “continue the campaign”, character actions, and ordinary table talk mean operate a campaign. Do not edit Lacuna source merely because the workspace contains code.
- **Backstage checkpoint intent:** “compare hidden explanations”, “run a retcon checkpoint”, or “sample alternatives before the reveal” means operate a managed `./lacuna checkpoint run ...` against a campaign. This is private planning, not player-facing narration and not ordinary source work.
- **Comparative-research intent:** “test Lacuna,” “run the four conditions,” “replicate the Gwern experiment,” “preregister blocks,” or “witness the assignment” means operate `./lacuna scenario ...` or `./lacuna scenario bundle ...`. This is experiment-owner custody, not ordinary play and not a request to claim that Lacuna works.
- **Repository intent:** audit, refactor, test, document, package, or implement Lacuna means work on the project. Do not mutate a campaign merely because one is present.
- **Inspection intent:** explain, list, verify, or diagnose means use read-only commands unless the user explicitly authorizes a turn or mutation.

A session-control sentence such as “Will you DM?” selects play mode. It is not evidence that any in-world physical event succeeded.

### Tool-capable play route

1. Use the cube or campaign library named by the user. Otherwise use `.lacuna-play/`.
2. On an unmistakable play request, prefer the typed one-command entrance:

   ```bash
   ./lacuna play start .lacuna-play --bootstrap --profile orchestrated --format markdown
   ```

   Use `--profile workspace` when bounded workers are unavailable and `--profile chat` for a human bridge. `--bootstrap` is safe only for an absent or empty play path; the command refuses a foreign nonempty path.
3. The default exact input is `Will you DM?` with `input.kind = session-control`. For later in-fiction messages use `./lacuna turn run begin --input-kind play-turn` and preserve exact bytes with `--player-input-file`.
4. After every transition read only `RUN_PATH/NEXT.md`. Obey its one owner, complete input, schema, visibility rule, and parent command.
5. For a delegated stage, render a self-contained handoff:

   ```bash
   ./lacuna turn run dispatch RUN_PATH --provider portable --format markdown
   ```

   Select `codex`, `claude-code`, `gemini-cli`, or `chatgpt` from actual host capabilities. The dispatch embeds the complete task card; do not invent a prompt or assume the worker can open the local path.
6. Give the worker only that complete dispatch, save exactly one JSON object, and advance with `./lacuna turn run accept`. The worker never accepts its own response, edits the sidecar, or commits.
7. Parent-owned proposal stages remain with the parent. A narration-only proposal with empty operations is valid; add typed custody only when justified and granted.
8. When the run is ready, the parent runs `./lacuna turn run commit`. Present only the accepted receipt’s top-level `narration` field; a planner return, proposal, verifier pass, or preparation is not player-visible fact.
9. When only `NEXT.md` is missing or damaged, use `turn run recover`; it repairs only the deterministic pointer after authoritative audit. Never hand-edit hashes or reconstruct authoritative artifacts.

For provider-native roles, use `lacuna_planner`, `lacuna_narrator`, `lacuna_proposal_builder`, and `lacuna_verifier` in Codex; use `lacuna-planner`, `lacuna-narrator`, `lacuna-proposal-builder`, and `lacuna-verifier` in Claude Code and Gemini CLI. The generated dispatch and card control the per-turn task.

### Tool-capable checkpoint route

1. Open a checkpoint only against the campaign the user authorized, and only for backstage planning. Do not reinterpret a player's in-fiction sentence as checkpoint consent.
2. Start one managed source-bound run:

   ```bash
   ./lacuna checkpoint run begin CUBE \
     --root .lacuna-checkpoint-runs \
     --trigger "Compare bounded explanations." \
     --provider portable --format markdown
   ```

   The command binds the exact open cube path, freezes a `lacuna.turn-request.v4` with purpose `checkpoint`, fixes all four provider routes, creates an owner-only sidecar, and emits one audited next action.
3. After every transition read only `RUN_PATH/NEXT.md`. Do not infer the stage from filenames or conversation memory.
4. At a delegated stage render `./lacuna checkpoint run dispatch RUN_PATH --format markdown`. The dispatch embeds the exact complete role card, fixed provider alias, already-sized return template, accept command, and failure-record command.
5. Route that envelope to exactly one named role. Use `lacuna_retcon_generator`, `lacuna_retcon_judge`, `lacuna_retcon_compressor`, and `lacuna_retcon_verifier` in Codex; use `lacuna-retcon-generator`, `lacuna-retcon-judge`, `lacuna-retcon-compressor`, and `lacuna-retcon-verifier` in Claude Code and Gemini CLI. ChatGPT may use role-dedicated conversations or agents.
6. Give the worker only the complete dispatch and accept exactly one JSON object with `checkpoint run accept`. Record timeout, provider, transport, invalid-output, refusal, or interruption attempts with `checkpoint run record-failure`; a failed attempt does not advance. A worker never accepts, assembles, reviews, commits, recovers, edits another return, or presents hidden state.
7. The judge receives a provenance-stripped canonical candidate view, not proof of semantic anonymity. The compressor receives only the deterministic winner. The verifier checks proposal-visible consistency; the parent revalidates the raw chain and kernel preparation.
8. At `ready-to-commit`, only the parent runs `checkpoint run commit`. Present only an accepted receipt's top-level narration. Candidates, rollout beats, scores, state cards, invocation receipts, and planner context remain private and noncanon.
9. For the clean information-bottleneck condition, follow the committed pointer to `checkpoint run next-turn`, preserve the exact next player input, create a new narrator context, and give it only the generated continuation dispatch. When prose continuity is required, prefer `history complete CHECKPOINT_RUN --run-root TURN_RUNS`; use `history build` only for an explicitly partial list. A serial same-context continuation is valid play/control behavior but is not a forgetting test.
10. If only `NEXT.md` is damaged, use `checkpoint run recover`; it repairs only that derived pointer after full authoritative audit. Retrying commit may authenticate an exact already-durable transition, including after later valid head advancement, without duplicate events.
11. Provider routes, context IDs, capsule digests, and invocation receipts are host declarations, not vendor attestations of model identity, isolation, timing, tool denial, or independence.

The normal operator contract is `docs/operators/CHECKPOINT_RUNS.md`; `docs/operators/CHECKPOINTS.md` documents the lower-level stateless protocol for custom hosts.

### Conversation-only play route

A chat model without local tools may start a playable scene immediately, but must label it once as **chat-only and not yet committed to Lacuna**. Use the human paste bridge in `docs/operators/CHATGPT.md` for governed persistence. Never imply that files or the cube changed without a passing receipt.

Lacuna is a custody kernel, not a storyteller. Changes should make epistemic distinctions more explicit, replayable, inspectable, and safely accessible.

## Non-negotiable doctrine

- Unknown is not false.
- A claim is not an assertion.
- A report is not an observation.
- A belief is not world truth.
- A selected candidate world is not canon.
- A normalized particle weight is planner attention, not truth or calibrated probability.
- One evidence assertion is one multiplicative factor; superseded current-epoch factors create visible debt until explicit reconciliation.
- Reweighting and reconciliation are not resampling, pruning, selection, or canonization.
- Reconciliation repairs derived weights from immutable reasons; it never edits the original update.
- A constraint rejects; it does not silently infer.
- Ambient exposure is not causality.
- A consequence link is authored custody, not discovered physics.
- Consequence repair is forward replacement with lineage, not rollback or automatic transfer.
- Commitment is mutation policy, not confidence.
- A fair-play seal proves one opening matches one earlier digest; it does not prove truth, authorship, uniqueness, trusted time, or fairness.
- Unrevealed seal openings remain outside the cube and ordinary model-turn authority.
- Changing world-assignment truth creates a successor; it never overwrites history.
- Narration is presentation; only accepted typed operations mutate state.
- A checkpoint candidate, rollout beat, aesthetic score, selected explanation, compressed state card, or narrator capsule is noncanon planning/context custody unless and until an allowed typed operation is accepted.
- A valid narrator capsule proves exact local artifact identity, not provider forgetting or semantic sufficiency.
- Player wording proves an utterance or attempt, not physical success.
- Audience and planner projections remain structurally separate.
- A custody explanation, burden score, or deterministic witness is not a proof of truth or fairness.
- Database migration never silently rewrites old events and must preserve the ledger head.
- Refusal is a successful outcome when an invariant would be violated.

## Scope discipline

The runtime may own:

- immutable event custody and atomic receipts;
- typed claims, assertions, sources, perspectives, worlds, and questions;
- pairwise/set-level compatibility validation;
- governed commitment and revision custody;
- explicit consequence graphs, digest-bound repair, and lineage diagnostics;
- complete-population particle reviews, single-use evidence reweighting, factor/debt diagnostics, and log-space factor-ledger reconciliation;
- host-custodied fair-play digest, reveal, receipt, and verification lifecycle;
- deterministic projections, verification, and rebuild;
- campaign selection metadata;
- source-bound turn normalization;
- access-scoped context and explanations;
- deterministic post-checkpoint narrator-capsule manufacture;
- explicit migrations and exchange schemas.

Keep these outside the kernel unless a later revision makes a compelling boundary argument:

- LLM vendor integrations and invocation;
- prose generation and dramatic scoring;
- automatic checkpoint triggering and semantic claims that a score measures truth or quality;
- automatic logical closure presented as stored truth;
- narrative particle proposal, search, resampling, rejuvenation, and selection policy;
- transcript hosting and chat UI;
- training or self-improvement loops;
- compiler/toolchain discovery;
- release packaging and deployment;
- cloud orchestration and long-running autonomy;
- general UI frameworks.

A campaign is an entrance, not a truth layer. A turn adapter is a protocol boundary, not a storyteller. A solver or planner must expose derivation/search custody rather than silently upgrading inference into fact.

## Change protocol

1. Add or update a behavioral test first when changing an invariant.
2. Represent semantic mutation as an event plus deterministic projection.
3. Refuse malformed, stale, cyclic, conflicting, or unauthorized operations before appending any event.
4. Never reuse `assign_world` as a hidden revision path.
5. Bind high-impact revision to an atomic base-head impact review.
6. Keep ambient exposure distinct from explicit consequence edges.
7. Do not delete or auto-transfer consequence debt; use reviewed replacement or explicit retirement and preserve lifecycle custody.
8. Validate replacement against active endpoints and the post-replacement graph.
9. Keep seal payloads and nonces out of events, projections, contexts, and receipts until an explicit later reveal.
10. Hash only immutable origin fields in externally anchorable receipt cores.
11. Keep secret-custody operations out of ordinary audience and director model grants.
12. Require complete eligible populations for global reweighting and reconciliation, and keep factor single-use/refusal atomic.
13. Preserve historical factor updates; reconciliation must use an immutable epoch baseline, explicit included/excluded dispositions, and a new event.
14. Treat structural world changes as factor-epoch boundaries unless a future explicit portability review authorizes otherwise.
15. Keep reweighting, reconciliation, factor correction, proposal, resampling, pruning, selection, commitment, and canonization as separate powers.
16. Emit structured refusals with deterministic witnesses where possible.
17. Document migrations. Keep database schema and event schema versioning separate.
18. Keep runtime dependencies at zero until one removes more risk than it adds.
19. Keep perspective and planner contexts structurally separate, including links, weights, factor history, reconciliation state, and diagnostic side channels.
20. Preserve exact transcript bytes outside the cube when replay matters.
21. Register scalar/list turn references centrally and refuse forward aliases before mutation.
22. Update version, changelog, current architecture/research/audit/decision/acceptance records, `REVISION.json`, manifest, and artifact filename.

## Review questions

Before accepting a feature, ask:

- Does this distinguish epistemic categories or blur them?
- Is this semantic custody, or application policy pretending to be infrastructure?
- Does it constrain state or silently infer state?
- Is a numeric output clearly labelled with what it does not measure?
- Does a global particle operation cover the complete eligible denominator?
- Can the same evidence be counted twice, directly or through an equivalent assertion family?
- What happens when an applied evidence assertion is superseded?
- Which factor epoch owns the assessment, and is its baseline reconstructable?
- Does reconciliation preserve excluded reasons, complete population, and independent replay arithmetic?
- Are correlated or derivative assertions being multiplied as though independent?
- Can projections be rebuilt exactly from events?
- What happens under concurrent writers and stale review receipts?
- What is visible to each perspective through records, links, IDs, diagnostics, and omission?
- What remains unknown afterward?
- What precisely causes refusal, and is the witness deterministic?
- Can a newly authored rule or dependency invalidate existing state atomically?
- What happens to downstream custody when an endpoint ends?
- Does a proposed repair preserve history without pretending equivalence?
- What provenance exists, and what does it fail to prove?
- Does a cryptographic-looking artifact carry explicit nonclaims and a stable external anchor point?
- Could a model, perspective, receipt, log, or rebuild path expose an unrevealed opening?
- What claim does the verifier explicitly not make?

## Comparative scenario and bundle protocol (rev0165)

When asked whether Lacuna's retcon mechanism works, do not answer from architecture alone. Use one `scenario` for an inspectable block or one `scenario bundle` for a preregistered replicated study.

### One block

1. `scenario template` binds one editable capsule to the exact verified seed.
2. The owner fixes script, model/sampling policy, budgets, rubric, and rater count before `scenario begin`.
3. `scenario begin` creates four exact hidden-assignment clones for forward-only, prompt-only-retcon, Lacuna serial, and Lacuna role-separated conditions.
4. Follow only the audited `NEXT.md`; at most one opaque cell is active.
5. Give a cell worker only the generated driver/role card, never the private assignment or sibling cells.
6. Use a fresh provider session per cell and honest declared context IDs. Forward-only, prompt-only-retcon, and Lacuna-serial use one persistent context for the complete cell.
7. For Lacuna role-separated, explicitly create fresh pairwise-distinct checkpoint workers, commit the checkpoint, run `checkpoint run next-turn`, and use a new dispatch-bound narrator context for the next story segment.
8. Record every accepted and failed attempt, bind it to the exact script step, and retain every accepted ordinary turn in the player-visible transcript. The first post-checkpoint narrator attempt must name the checkpoint ID and exact capsule digest.
9. Keep the complete driver and its operator-only canary with the private cell coordinator; nested role workers and raters receive only generated least-context artifacts. Do not open the filesystem-only canary merely to inspect it.
10. After all cells freeze, require the exact private contamination scan before the blind packet. Preserve same-cell/cross-cell matches; never discard or rerun a cell because the scan is inconvenient.
11. Give raters only `70-blind-rating-packet.json`. Do not unblind before the fixed complete rating count.

### Replicated bundle

1. Build one plan with every `CUBE CAPSULE` block before observing any result. Do not append or replace blocks later.
2. Require one comparable rating contract; record story, model, and replicate differences as explicit strata.
3. `scenario bundle begin` precreates every child, hidden assignment, and exact seed clone and publishes one public commitment.
4. When the plan requires external receipts, retain that commitment outside the host and record the exact receipt descriptions before any child advances.
5. Read only the bundle `NEXT.md`. It names one owner, one complete input, one expected schema, one blind/nonblind boundary, and one exact parent command.
6. For a subagent-capable host, explicitly create the named fresh worker context and give it only the emitted complete dispatch. A worker never accepts, seals, recovers, unblinds, browses siblings, or mutates the parent. Role-separated cells also require a fresh narrator after every checkpoint, using only the complete dispatch emitted by `checkpoint run next-turn`.
7. Preserve every completed, refused, and failed cell. Reused declared contexts or non-null invocation IDs across blocks, persistent-control context drift, and missing/reused post-checkpoint narrator contexts are refused.
8. Before rating, authenticate each child's frozen contamination scan. Block seals must bind its digest/status/count; do not omit a detected leak or create a replacement block.
9. After all fixed ratings for one block, run `scenario bundle seal`; never call child unblind directly.
10. Unblind only after every scheduled block is sealed. Retry the same bundle command after interruption; do not sample replacement assignments.
11. Analyze the rater-level JSON under a separately declared statistical model. The bundle itself emits no winner, significance, or causal claim.

Codex workers are defined in `.codex/agents/`; Claude Code workers in `.claude/agents/`; Gemini-oriented workers in `.gemini/agents/`. ChatGPT may use role-dedicated chats/calls or a connected tool; without one, use the human bridge. The parent/coordinator alone owns filesystem access, transition commands, acceptance, deterministic review, commit/recovery, witness recording, sealing, unblinding, and player presentation.

Keep Lacuna-derived cube outcomes, host-declared provider/context/capsule metrics, external-receipt descriptions, and human judgments separate. Never claim provider identity, independent memory, semantic blindness, trusted randomness/time, forgetting, or efficacy merely because the retained artifacts are internally consistent.
