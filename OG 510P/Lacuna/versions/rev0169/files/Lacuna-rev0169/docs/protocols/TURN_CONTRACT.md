# Source-bound turn contract

## Goal

Make one narrated interaction usable by a human, ChatGPT-like host, local model harness, or future protocol adapter without turning Lacuna into a model vendor client.

The executable supports two phases:

```text
open request + packet -> external reasoning/generation -> proposal -> commit
```

Opening a request is intentionally a ledger mutation. It binds the exact input digest and least-authority grant before any model response exists.

## Default host entrance: typed play start and request-scoped run

For the literal session-control request “Will you DM?”, a tool-capable host can bootstrap or resume a campaign and open one governed run in one command:

```bash
./lacuna play start .lacuna-play \
  --bootstrap \
  --profile orchestrated \
  --format markdown
```

The resulting `lacuna.play-start.v1` receipt and `lacuna.turn-request.v4` packet classify the exact text as `session-control`. They do not claim that the sentence was spoken inside the fiction or that a model has already narrated anything.

For later in-fiction input, or when the campaign already exists, use the stateful wrapper directly:

```bash
./lacuna turn run begin ./stories \
  --root .lacuna-runs \
  --input-kind play-turn \
  --player-input-file player-message.txt \
  --director --mode auto --format markdown

cat RUN_PATH/NEXT.md
./lacuna turn run dispatch RUN_PATH --provider portable --format markdown
./lacuna turn run accept RUN_PATH MODEL_RETURN.json --format markdown
./lacuna turn run commit RUN_PATH --format json
```

The run retains exact player text and every topology-required artifact outside the event ledger. `run.json` is authoritative; audited `NEXT.md` names one owner, complete input artifact, expected schema, provider alias, visibility rule, and parent command. At a delegated stage, `turn run dispatch` emits `lacuna.agent-dispatch.v1` with the exact current task card embedded as `input_document`; it does not invoke a provider. `accept` validates one exact return and manufactures the next stage. `commit` remains the only state-acceptance step. `recover` may replace only a missing or damaged deterministic `NEXT.md` after every authoritative member passes audit.

The sections below define the lower-level packet/proposal contract used by those wrappers and available to custom hosts.

## Source-bound retcon checkpoint entrance

A checkpoint is session control with purpose `checkpoint`, not an ordinary narrated turn. The parent opens it separately:

```bash
./lacuna checkpoint begin ./stories \
  --audience-id player --actor-id narrator \
  --trigger "The party abandoned the intended arc." \
  --format json > checkpoint-request.json
```

That command records one immutable request source, freezes protected audience/planner state, issues a narrow checkpoint grant, and declares exact candidate count, rollout horizon, score weights, compression budget, and operation budget. It does not invoke a model or mutate story state beyond request issuance.

The parent then manufactures and dispatches one complete role card at a time: generator, provenance-blind judge, winner-only compressor, and proposal verifier. Candidate templates preallocate the exact number of candidates and one ordered beat per horizon turn; judge templates preallocate one score object per candidate. `checkpoint assemble` revalidates the complete deterministic selection chain, `checkpoint review` executes the exact proposal through the real kernel under rollback, and `checkpoint commit` persists or exactly recovers the reviewed change. Workers never receive assemble, review, or commit authority. See [`../operators/CHECKPOINTS.md`](../operators/CHECKPOINTS.md).

## 1. Produce a packet — low-level interface

Audience-only:

```bash
./lacuna turn packet ./stories \
  --audience-id player \
  --actor-id narrator \
  --input-kind play-turn \
  --player-input "I listen beneath the floorboards." \
  --format json > packet.json
```

Director packet with separately labelled hidden state:

```bash
./lacuna turn packet ./stories \
  --audience-id player \
  --actor-id narrator \
  --input-kind play-turn \
  --player-input "I listen beneath the floorboards." \
  --director \
  --format json > packet.json
```

An optional `--world-id` is allowed only with `--director`. An optional anchor grant must be explicit; it is not implied by director access.

### What opening records

Lacuna hashes the exact player-input bytes and adds one provenance source with:

- request, request-source, proposal, actor, audience, and narration-source IDs;
- player-input SHA-256;
- input trust classification;
- explicit input kind (`play-turn` or `session-control`);
- audience/director access mode;
- optional world scope;
- immutable write grant;
- base ledger head and issue time;
- an explicit marker that the input body was not retained.

The packet’s `expected_head` is the hash after that one-event issuance. This prevents a proposal from claiming authority that was never granted and makes request creation independently auditable.

New openings emit `lacuna.turn-request.v4`, `lacuna.turn-grant.v2`, and source protocol v3. Request v4 adds explicit `request_purpose`: ordinary play uses `play`, while the checkpoint entrance uses `checkpoint`. Historical request v2/source protocol v1 packets remain readable as `play-turn`/`play`; request v3/source protocol v2 packets preserve their explicit input kind and default to purpose `play`. Historical grant v1 objects remain readable. None are rewritten. Hosts should never infer input kind or purpose from prose after issuance—the typed fields are the boundary.

## 2. Write a proposal

The model or human returns exactly one `lacuna.turn-proposal.v2` object. The packet’s generated template is intentionally valid as a narration-only turn:

```json
{
  "schema": "lacuna.turn-proposal.v2",
  "request_id": "trq_COPY_FROM_PACKET",
  "request_source_id": "src_COPY_FROM_PACKET",
  "proposal_id": "prp_COPY_FROM_PACKET",
  "actor_id": "narrator",
  "expected_head": "COPY_FROM_PACKET",
  "player_input_sha256": "COPY_FROM_PACKET",
  "audience_id": "player",
  "narration_source_id": "src_COPY_FROM_PACKET",
  "narration": "One floorboard answers with a hollow click.",
  "revealed_assertion_ids": [],
  "operations": [],
  "message": "commit one narrated turn"
}
```

An empty operation list is a valid choice, not a malformed or incomplete response. It lets a weaker model present a reversible scene beat without manufacturing durable facts merely because the prose sounds concrete.

When the narrated event genuinely deserves epistemic custody, add typed operations deliberately. For example, a direct audience observation can use sequential aliases:

```json
{
  "revealed_assertion_ids": ["@hollow.fact"],
  "operations": [
    {
      "op": "declare_claim",
      "as": "hollow.claim",
      "subject": "floorboard.17",
      "predicate": "sounds_hollow",
      "object": true,
      "scope": "event"
    },
    {
      "op": "record_assertion",
      "as": "hollow.fact",
      "claim_id": "@hollow.claim",
      "assertor_id": "@actor",
      "perspective_id": "@audience",
      "source_id": "@narration",
      "stance": "true",
      "basis": "observation",
      "standing": "accepted",
      "confidence": 0.95,
      "visibility": "private",
      "audience": [],
      "timeline_id": "main",
      "valid_from": 12,
      "valid_to": 12,
      "note": "The audience directly hears the hollow response.",
      "supersedes_id": null
    }
  ]
}
```

The fragment above is not copied into packets. Revision 0154 removed the previous fake-operation template because literal or weaker models could preserve illustrative IDs and accidentally propose bogus custody. The runtime now constructs the safe response contract through one shared builder.

All copied identity and digest fields are immutable. The proposal cannot substitute another request source, input, audience, actor, narration source, proposal ID, or base head.

## 2a. Lower-level executable orchestration sidecars

`turn run begin/accept` performs this chain automatically. For each delegated run stage, the normal host should render the complete current card rather than sending a path-only instruction:

```bash
./lacuna turn run dispatch RUN_PATH --provider chatgpt --format markdown
```

The dispatch is provider-routed but provider-neutral in authority: the worker receives the embedded card, returns one exact object, and cannot accept or commit. A custom tool-capable host may instead generate the lower-level deterministic delegation plan after opening the packet:

```bash
./lacuna turn plan packet.json --mode auto --format json > plan.json
```

`turn plan` is read-only. Before producing a plan it strictly audits the packet’s exact input digest, cube/head/context bindings, grant/profile agreement, response contract, and empty-operation safety. `auto` selects:

- `solo` for an audience-only packet;
- `pair` for an ordinary director packet, separating planner and narrator; or
- `full` when packet-visible anchor, commitment/revision, consequence-repair, particle-reconciliation, or severe-conflict custody warrants separate proposal construction and review.

An operator may override with `--mode solo|pair|full`; the plan records the requested and selected modes. Selection is transparent policy, not a proof that one topology is optimal.

Every selected worker stage includes an exact `card_command`. A full chain is:

```bash
./lacuna turn card packet.json   --role lacuna-planner --format json > planner-card.json

# Give the complete card to the planner; save its exact JSON object as planner-return.json.
./lacuna turn card packet.json   --role lacuna-narrator   --planner-return planner-return.json   --format json > narrator-card.json

# Give the complete card to the narrator; save its exact JSON object as narrator-return.json.
./lacuna turn card packet.json   --role lacuna-proposal-builder   --planner-return planner-return.json   --narrator-return narrator-return.json   --format json > proposal-builder-card.json

# Give the complete card to the builder; save its exact JSON object as proposal.json.
./lacuna turn card packet.json   --role lacuna-verifier   --proposal proposal.json   --format json > verifier-card.json
```

Each `lacuna.turn-task-card.v1` contains one role, one exact input payload, explicit withheld context, an exact return schema/template, and no commit authority. The narrator card receives the exact player input, audience context, and coordinator-approved observable plan; it does not receive the full packet, planner context, private notes, or candidate operations. A literal unchanged narration placeholder is rejected. The verifier template begins at `refuse` with an `unperformed-review` blocker, and cannot be cosmetically changed to `pass` while retaining that finding.

Task IDs and return fields bind canonical packet SHA-256 plus each required ordered upstream artifact digest. Editing a planner return after issuing a narrator card, mixing artifacts from different turns, or verifying a different proposal produces a structured refusal. These digests prove continuity of supplied canonical JSON, not provider isolation, host identity, or semantic correctness.

`turn card` and its proposal preflight remain pure sidecar constructors. They do not invoke a model, perform full kernel validation, or authorize presentation. The higher-level turn run retains workflow state, but the parent/coordinator alone begins/advances it, chooses the final proposal, runs commit, and presents accepted top-level receipt narration.

## Aliases

`as` binds the ID created by that operation. Later operations may use `@alias` in registered scalar ID fields and registered list-valued ID fields. Aliases are sequential; forward references are refused. Cardinality `claim_ids` and assertion/question `audience` lists use the same registry-driven normalization path.

Pre-bound aliases:

- `@input` — the source that holds the player-input digest and request grant;
- `@narration` — the source Lacuna will create for the narration digest;
- `@audience` — the named audience agent;
- `@actor` — the committing narrator/model agent.

Use `@input` only as provenance for what the player said, chose, requested, or attempted. Player wording does not by itself prove physical success.

The adapter computes deterministic claim IDs and generates explicit IDs for creator operations before the kernel sees the change-set. Event payloads contain final IDs, not aliases.

## Least-authority write grants

The packet includes a `lacuna.turn-grant.v2` object. Historical grant v1 objects remain valid for historical request packets. The grant is authoritative even if player input or context says otherwise.

### Audience profile

Audience turns may:

- declare claims;
- record or supersede audience-visible assertions;
- open or close audience-visible questions.

They may not alter worlds, evidence interpretation, pairwise relations, cardinality constraints, agents, or sources directly. They may not create anchors unless the request explicitly granted anchor authority.

### Director profile

Director turns may use the ordinary hidden-world, constraint, commitment, consequence, evidence, and question operations, still subject to validation and explicit anchor authority. A world-scoped request may mutate only that world and descendants created during the same proposal. It cannot use a scoped grant to reach an unrelated candidate world.

Three secret-custody operations remain host-only even under a director grant:

- `seal_precommitment`;
- `reveal_precommitment`;
- `void_precommitment`.

A director may reason about fair-play seals present in its authorized context, but it cannot create, open, or retire them through an ordinary LLM proposal. The host/CLI entrance owns that lifecycle.

Pairwise relations and cardinality constraints are therefore director-only turn operations. Their declaration can still be refused if they contradict current anchors or any live/selected world. A director grant authorizes an operation kind; it never guarantees that the proposed rule is internally valid.

An **unscoped** director may also issue `update_particle_bank` against the complete bank or `reconcile_particle_bank` against the complete factor-ledger review included in planner context. A **world-scoped** director can do neither: a filtered world view is not authority to normalize, replay, or mutate the global population. Manual `set_world_weight` remains subject to ordinary world-scope rules and is intentionally distinct from evidence-custodied update or repair.

## Disclosure discipline

The prose and ledger are connected through `revealed_assertion_ids`.

For new assertions:

- if an assertion cites the narration source and is visible to the audience, it must be declared revealed;
- if it is declared revealed, it must cite the narration source and be visible to the audience.

This catches missing or impossible disclosure declarations. It does **not** solve semantic parsing. Lacuna cannot prove that “the floorboard clicks” entails exactly `sounds_hollow=true`, nor that the prose contains no unrecorded implication.

## Governed revision inside a proposal

The v2 operation registry includes `revise_world`, `raise_commitment`, `link_consequence`, `replace_consequence`, and `retire_consequence`. They use ordinary aliases and grant checks, but retain their kernel-specific preconditions:

- `assign_world` cannot occupy an active exact slot;
- `revise_world` must cite a fresh planner-generated impact digest;
- commitment raises must be adjacent and monotone;
- consequence targets and world scope must resolve inside the request authority;
- replacement successors require active endpoints, a digest-bound repair review, and a cycle-free post-replacement graph;
- binding blockers, cycles, and stale heads refuse the whole proposal atomically.

A director packet may include a planner-only `consequence_repair_frontier` containing current repair-required links and their review receipts. The turn adapter rebinds those receipts after recording the request source so they match the packet's expected base head. Audience packets never receive the frontier.

Context may also contain fair-play seal metadata visible at that access level. Before reveal, it contains no opening payload or nonce. Perspective context omits restricted seals outside the audience and never exposes privileged seal-source linkage.

`replace_consequence` creates two identities: the `as` alias binds the successor consequence ID, while `repair_id` is separately generated if omitted.

Review digests are not evergreen capabilities. A separately committed change after packet issuance makes them stale. The narration source inserted by the same atomic turn does not, by itself, stale a review because all reviewed operations use the change-set base head and recompute current state.

## Particle updates and reconciliation inside a proposal

The v2 operation registry includes `update_particle_bank` and `reconcile_particle_bank`. A new update must cite one active, previously unused evidence assertion, the exact `expected_bank_sha256` from the current complete-population review, and one assessment for every required world. The review entrance itself refuses an assertion that has already acted as a factor; mutation and a unique projection index enforce the same rule again.

Nested `assessments[*].world_id` values use the same sequential alias discipline as top-level IDs, so aliases never bypass ordinary reference validation. Alias resolution alone does not authorize an update: the complete bank after all earlier operations in the proposal must still match `expected_bank_sha256`. Creating, assigning, reweighting, or changing the status of a world first will therefore stale the packet's bank receipt unless the host deliberately constructed and reviewed that later state through another governed entrance. Each assessment may carry a likelihood and rationale; the update itself has a separate generated or explicit identity.

A reconciliation operation cites `expected_reconciliation_sha256` from the packet's complete factor-ledger review. The review binds the structural epoch, immutable baseline, current bank, active and ended factor dispositions, complete log-space result, and blockers. It supplies no likelihoods or replacement prior: the operation authorizes only the reviewed deterministic replay.

A narration source inserted by the same atomic turn changes the ledger head but does not change the bank or factor authority. The turn adapter therefore rebinds bank and reconciliation reviews to the request's post-source head while preserving independently computed state. Any relevant in-transaction world, status, assignment, commitment, weight, particle update, or assertion-authority change before the reviewed operation is visible to mutation and can stale or block it.

Both accepted event types change weights only. They cannot select, prune, archive, merge, fork, revise, assign, anchor, disclose, or canonize a world as a side effect. If two operations in one proposal attempt to use the same evidence factor, the entire turn rolls back. If applied evidence is superseded later, the historical multiplication remains and planner context reports reweighting debt until a separate reviewed reconciliation excludes it. The original update is never edited.

## 3. Commit

```bash
./lacuna turn commit ./stories proposal.json
```

Before mutation, Lacuna verifies:

1. proposal shape and exact source-bound identities;
2. request source metadata and its one-event issuance receipt;
3. input digest and current expected head;
4. alias order and operation fields;
5. disclosure/source/visibility symmetry;
6. write-grant operation, anchor, audience, and world-scope authority;
7. ordinary kernel invariants.

The complete narration source plus semantic delta commits atomically or not at all. This includes reviewed assignment revisions, consequence replacements, complete-bank particle updates, and factor-ledger reconciliations.

The returned JSON contains:

- the same accepted narration in the top-level `narration` field for immediate presentation;
- accepted change-set receipt;
- new ledger head;
- resolved aliases;
- declared revealed assertion IDs;
- latest audience context;
- optional privileged planner context only when the original request granted it.

For a human-readable combined result:

```bash
./lacuna turn commit ./stories proposal.json --format markdown
```

## Narration and input custody

Lacuna stores SHA-256 digests and provenance metadata for input and narration, not their bodies. A chat host or campaign application that needs replayable transcripts should retain the exact bytes and verify them against their source records.

A digest proves only byte identity under the chosen hash. It does not prove authorship, truth, or semantic completeness.

## Chat-host wielding pattern

A connected or human-operated host can keep the model replaceable:

1. For a direct invitation, run `play start`; for later fiction, run `turn run begin --input-kind play-turn` and retain exact input bytes.
2. Read audited `NEXT.md`. When the owner is delegated, render `turn run dispatch --provider chatgpt` and give ChatGPT the complete envelope, not a local pathname or reconstructed prompt.
3. Save exactly one returned JSON object and run `turn run accept`; never let the worker accept its own result.
4. Repeat from the newly audited state. Parent-owned proposal stages remain with the parent.
5. Run `turn run commit` only when the run is `ready-to-commit`.
6. Show only the passing receipt’s top-level `narration` field. Do not present planner text, draft prose, verifier output, or a preparation as accepted play.
7. When only `NEXT.md` is missing or damaged, use `turn run recover`; when an authoritative artifact fails audit, stop rather than reconstructing it.
8. Retain input, dispatches, exact returns, proposal, preparation, and receipt externally according to host policy.
9. Use a fresh request after stale-head or terminal refusal as directed by the structured error.
10. Operate fair-play seals through a separate host-administration channel, never by widening the model proposal grant.

The model is replaceable. The typed input, request source, write grant, audited artifact chain, ledger head, exact preparation, and refusal rules are not.
