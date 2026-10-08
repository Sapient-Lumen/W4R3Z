# Lacuna

**An epistemic ledger for worlds that have not finished becoming true.**

New here?

- **Play:** [`PLAY_NOW.md`](PLAY_NOW.md)
- **Evaluate the retcon-planning gift:** [`FOR_GWERN.md`](FOR_GWERN.md)
- **Operate the repository:** [`OPERATE_LACUNA.md`](OPERATE_LACUNA.md)

Lacuna is a dependency-free Python/SQLite custody kernel for adaptive fiction, tabletop-like campaigns, mysteries, simulations, and model-hosted interactive worlds. It keeps observation, testimony, belief, hidden-world hypothesis, constraint, commitment, consequence, and unknown state distinct. Several explanations may remain live at once; a planner preference never becomes canon by accident.

Rev0169 (`rev0169`) is the send-ready polish pass for the test harness and release license. It keeps the three-door gift surface (`PLAY_NOW.md`, `FOR_GWERN.md`, and `OPERATE_LACUNA.md`) at the top of the archive, replaces blocking close-time SQLite WAL truncation with non-blocking passive checkpoint cleanup, makes unedited scenario templates fail closed, adds a top-level MIT license, and documents a bounded module/method acceptance runner so recipient testing reports a clear pass/fail/timeout module or method instead of hanging ambiguously.

The current artifact retains the full experimental custody stack: fresh post-checkpoint narration through a source-bound continuation dispatch, complete-versus-partial public-history labeling, preregistered operator/filesystem canaries with whole-retained-tree scans, replicated bundle seals, post-primary-rating method-identifiability assessments, parent-opened child unblind gates, spreadsheet-safe rater exports, and `artifact check` for clean-extraction audits. These mechanisms add falsification pressure and source custody; they do not prove provider memory erasure, filesystem denial, semantic completeness, narrative quality, or causal efficacy.

Lacuna still does not call a model, write plot, choose a winning world, parse prose entailment, train itself, or package itself. A human or LLM proposes. The cube validates, records, projects, or refuses.

## Governing distinctions

> Unknown is not false. A report is not an observation. A belief is not world truth. A selected world is not canon. Proximity is not causality. Commitment is not confidence. A valid seal is not truth. Narration is presentation, not automatic mutation.

A **claim** is neutral proposition content. An **assertion** records an agent’s stance, source, perspective, standing, visibility, and interval. A **candidate world** is one partial hidden-world hypothesis. An **anchor** is an assertion whose contradiction is no longer acceptable. A **constraint** rejects incompatible explicit state without filling missing truth. A **commitment** governs how an assignment may change. A **consequence link** records an authored dependency. A **consequence repair** records reviewed predecessor→successor replacement custody. A **fair-play seal** binds one external opening to an earlier salted digest without making it canon. An **open question** preserves a deliberate lacuna.

## Start with a campaign

```bash
cd Lacuna-rev0169

./lacuna campaign create /tmp/lacuna-stories lantern-room \
  --title "The Lantern Room" \
  --summary "A bell, a broken cup, and several surviving explanations."

./lacuna campaign list /tmp/lacuna-stories
./lacuna campaign show /tmp/lacuna-stories
./lacuna status /tmp/lacuna-stories
```

The first campaign is selected automatically. Ordinary cube commands accept either a bare cube or a campaign library whose active campaign is selected.

## Start play from one sentence

```bash
./lacuna play start /tmp/lacuna-stories \
  --profile orchestrated \
  --player-input 'Will you DM?' \
  --format markdown
```

From an absent or empty default path, add `--bootstrap`:

```bash
./lacuna play start .lacuna-play --bootstrap --profile orchestrated --format markdown
```

The command classifies the exact sentence as `session-control`, opens a request-scoped run, and prints its audited next action. It does not invoke a model or narrate. Use `--profile workspace` for one shell-capable parent and `--profile chat` for a human bridge. Ordinary ChatGPT can begin chat-only play immediately, but durable persistence requires a connected host or human-operated CLI. See `PLAY_WITH_AN_LLM.md` and `docs/operators/ONE_SENTENCE_START.md`.

A read-only capability brief remains available:

```bash
./lacuna model brief /tmp/lacuna-stories --profile orchestrated --format markdown
```

## Take one governed turn

Preserve exact player text and begin a request-scoped run:

```bash
printf '%s' 'I listen beneath the floorboards.' > /tmp/player-message.txt

./lacuna turn run begin /tmp/lacuna-stories \
  --root /tmp/lacuna-runs \
  --player-input-file /tmp/player-message.txt \
  --director --mode auto --format markdown
```

The command prints a collision-resistant run path. From then on, read exactly one pointer:

```bash
cat RUN_PATH/NEXT.md
```

It names the sole next owner, complete input artifact, expected return schema, player-visibility rule, and exact parent command. For a delegated stage, render a complete provider handoff:

```bash
./lacuna turn run dispatch RUN_PATH --provider chatgpt --format markdown
```

The dispatch embeds the exact generated card as `input_document`; use `codex`, `claude-code`, `gemini-cli`, or `portable` for another route. Give the worker that complete handoff, save its one exact JSON object, and advance:

```bash
./lacuna turn run accept RUN_PATH MODEL_RETURN.json --format markdown
```

Repeat until `NEXT.md` names commit:

```bash
./lacuna turn run commit RUN_PATH --format json
```

Only an accepted `60-turn-receipt.json` proves mutation. Present its top-level `narration` field; never present merely proposed, verified, or ready-to-commit narration as having happened.

At `ready-to-commit`, `43-turn-preparation.json` is the complete replay envelope. Readiness means the exact kernel path succeeded and was rolled back; it is not a head reservation. A retry after a database/sidecar crash either commits nothing twice or recovers a receipt bound to the already-durable event chain.

`auto` selects `solo`, `pair`, or `full` from packet-visible policy. The ordinary director path is planner → audience-only narrator → parent proposal. Full mode adds a packet-bound proposal builder and independent fail-closed verifier. A narration-only proposal with empty operations is valid.

The lower-level `turn packet`, `turn plan`, `turn card`, and `turn commit` commands remain available as the inspectable protocol substrate and for custom hosts. The turn-run interface is the normal entrance because it retains and audits the complete handoff chain. See `docs/operators/TURN_RUNS.md` and `docs/operators/MULTI_AGENT.md`.

## Compare hidden explanations at a governed checkpoint

A checkpoint is backstage planning, not a player command. Open a managed run when several latent explanations fit and a reveal, payoff, or causal commitment is approaching:

```bash
./lacuna checkpoint run begin /tmp/lacuna-stories \
  --root /tmp/lacuna-checkpoint-runs \
  --trigger "Compare bounded explanations before the next reveal." \
  --candidate-count 4 \
  --rollout-horizon-turns 4 \
  --provider chatgpt \
  --format markdown
```

Copy the printed run path. Thereafter read only its audited pointer:

```bash
cat RUN_PATH/NEXT.md
./lacuna checkpoint run dispatch RUN_PATH --format markdown
```

The dispatch embeds the complete exact current role card. Give it to one role-dedicated context, save one JSON object, and invoke the generated `checkpoint run accept` command. A timeout, transport error, malformed output, interruption, or worker refusal can be recorded with `checkpoint run record-failure` without advancing. Repeat through generator → provenance-blind judge → winner-only compressor → verifier. At `ready-to-commit`, only the parent runs:

```bash
./lacuna checkpoint run commit RUN_PATH --format json
```

For the clean information-bottleneck condition, move narration to a new context through one source-bound continuation command:

```bash
./lacuna checkpoint run next-turn RUN_PATH \
  --player-input-file next-player-input.txt \
  --provider chatgpt \
  --format markdown
```

The command authenticates the checkpoint, requires the cube still at its accepted head, opens one audience-only solo turn, and emits a self-contained fresh-narrator dispatch. The worker returns one exact turn proposal; the parent uses the printed ordinary-turn accept command and commits through the existing turn-run boundary. For the strongest local prose-coverage claim, first run `lacuna history complete CHECKPOINT_RUN --run-root TURN_RUNS` and pass the result with `--public-history`; use `history build` only when an explicitly partial ordered list is the intended treatment. A serial same-context continuation remains a valid control and usability path, but it does not test whether the compressed state card is sufficient. See `docs/operators/FRESH_NARRATOR.md` and `docs/operators/PUBLIC_HISTORY.md`.

Every generator template has exactly the requested candidate slots and every candidate has exactly one ordered beat per rollout turn. All four provider routes are fixed at run creation and may be heterogeneous. The run retains exact invocation custody, but provider names and model metadata are host declarations—not attestations of identity, isolation, or independence. Detailed rollouts remain noncanon and are not written into active cube state.

A player still only needs to say **“Will you DM?”**; checkpoint vocabulary stays backstage. See `docs/operators/CHECKPOINT_RUNS.md`. `docs/operators/CHECKPOINTS.md` documents the lower-level stateless protocol for custom hosts.

## Test the retcon mechanism instead of assuming it works

Bind an editable experiment capsule to one verified seed:

```bash
./lacuna scenario template /tmp/lacuna-stories > /tmp/scenario-capsule.json
```

Replace the scripted off-plan action and declare one exact model/sampling/budget policy, then begin:

```bash
./lacuna scenario begin /tmp/lacuna-stories /tmp/scenario-capsule.json \
  --root /tmp/lacuna-scenarios --format markdown
```

The run privately commits a randomized four-condition assignment and creates exact seed clones. Thereafter follow only `RUN_PATH/NEXT.md`:

```bash
./lacuna scenario dispatch RUN_PATH --format markdown
./lacuna scenario record RUN_PATH CELL_RETURN.json --format markdown
```

Repeat through four opaque cells. On the final accepted cell, Lacuna freezes `65-PRIVATE-contamination-scan.json` before creating the blind packet. Inspect it privately with `./lacuna scenario contamination RUN_PATH`; do not show canary tokens or findings to blind raters. Give raters only `70-blind-rating-packet.json`, create one fixed form per rater with `scenario rating-template`, record complete ratings, then run `scenario unblind` once. Leakage findings are retained rather than used for cherry-picked reruns. Provider/context/cost fields are host declarations, a clean exact-token scan is not proof of isolation, structured blinding is not semantic anonymity, and one block is not a causal result. See `docs/operators/CONTAMINATION_CANARIES.md` and `docs/operators/SCENARIO_CAPSULES.md`.

For a preregistered replicated study, build every block before execution:

```bash
./lacuna scenario bundle template \
  --block /tmp/lacuna-stories /tmp/scenario-capsule.json \
  --block /tmp/lacuna-stories /tmp/scenario-capsule.json \
  --minimum-witnesses 1 > /tmp/bundle-plan.json

./lacuna scenario bundle begin /tmp/bundle-plan.json \
  --root /tmp/lacuna-scenario-bundles --format markdown
```

Retain `30-public-commitment.json` externally, satisfy any witness gate, then follow only the bundle `NEXT.md`. Each block is fully rated and sealed without unblinding; only after all scheduled blocks are sealed does `scenario bundle unblind` publish the complete rater-level report. See `docs/operators/SCENARIO_BUNDLES.md`.

## Govern a hidden-world premise

Create a claim and world, then assign a tentative hypothesis:

```bash
./lacuna world-assign /tmp/lacuna-stories \
  --assignment-id asn_passage \
  --world-id wld_case \
  --claim-id clm_secret_passage \
  --truth true \
  --commitment tentative \
  --commitment-basis planning \
  --rationale "Current hidden-world hypothesis."
```

Raise commitment one boundary at a time:

```bash
./lacuna commitment-raise /tmp/lacuna-stories asn_passage soft \
  --basis authored \
  --rationale "The next scene now depends on this premise."
```

Record an explicit downstream dependency:

```bash
./lacuna consequence-link /tmp/lacuna-stories \
  asn_passage question qst_where_draft_enters motivates \
  --severity material \
  --rationale "This question exists because the passage hypothesis was adopted."
```

## Revise without retcon amnesia

First request a current-head review:

```bash
./lacuna revision-impact /tmp/lacuna-stories asn_passage > /tmp/impact.json
```

Inspect blockers, burden components, ambient exposure, and explicit consequences. Then submit the exact `impact_sha256`:

```bash
./lacuna world-revise /tmp/lacuna-stories asn_passage false \
  --assignment-id asn_passage_rev2 \
  --expected-impact-sha256 DIGEST_FROM_IMPACT \
  --reason "The surviving evidence favors a ventilation shaft instead." \
  --commitment tentative \
  --commitment-basis planning
```

A separately committed intervening event makes the review stale. Reviewed operations in one atomic change-set share its base head, allowing a narration source and reviewed mutation to commit together while still detecting relevant in-transaction state changes. Hard commitment or a binding consequence blocks in-place revision. Notice/material consequences remain visible repair obligations after an endpoint ends.

See `docs/protocols/REVISION_IMPACT.md`, `COMMITMENT_GOVERNANCE.md`, and `CONSEQUENCE_LINKS.md`.

## Repair a consequence without erasing its past

Request a review of the active predecessor:

```bash
./lacuna consequence-repair-review /tmp/lacuna-stories csq_old > /tmp/repair.json
./lacuna consequence-repair-frontier /tmp/lacuna-stories
```

Then author one complete successor using the returned `repair_review_sha256`:

```bash
./lacuna consequence-replace /tmp/lacuna-stories \
  csq_old asn_passage_rev2 question qst_where_draft_enters motivates \
  --consequence-id csq_new \
  --repair-id cpr_old_to_new \
  --severity material \
  --rationale "The revised passage premise now motivates the live question." \
  --expected-repair-sha256 DIGEST_FROM_REVIEW \
  --reason "Replace dependency custody after premise revision."
```

Inspect both historical links and the identified repair relation:

```bash
./lacuna consequences /tmp/lacuna-stories --include-retired
./lacuna consequence-repairs /tmp/lacuna-stories
```

See `docs/protocols/CONSEQUENCE_REPAIR.md`.

## Precommit selected secrets without freezing the world

Prepare an opening outside the cube:

```bash
cat > /tmp/culprit.json <<'JSON'
{"culprit_id":"character.ada","method":"glass key"}
JSON

./lacuna seal prepare /tmp/lacuna-stories /tmp/culprit.json \
  --seal-id seal.case-culprit > /tmp/seal-opening.json
```

Publish only its salted digest and retain the returned receipt:

```bash
./lacuna seal create /tmp/lacuna-stories /tmp/seal-opening.json \
  --label "Authored culprit" --purpose mystery > /tmp/seal-created.json
./lacuna seal receipt /tmp/lacuna-stories seal.case-culprit > /tmp/seal-receipt.json
```

Later, verify and reveal the exact opening:

```bash
./lacuna seal verify /tmp/lacuna-stories /tmp/seal-opening.json
./lacuna seal reveal /tmp/lacuna-stories /tmp/seal-opening.json \
  --reason "The investigation reached the authored resolution."
```

The payload and 256-bit nonce are absent from the cube before reveal. Creation and reveal must be separate committed change-sets. `receipt_sha256` covers a stable origin core and does not change at reveal; retain or externally anchor it if fork resistance matters. A passing seal proves byte continuity only—not truth, authorship, uniqueness, trusted time, clue sufficiency, or fair-play quality. Seal lifecycle operations are host-only and unavailable to ordinary audience or director model turns.

See `docs/protocols/FAIR_PLAY_SEALS.md` and `docs/protocols/INTERACTION_SURFACES.md`.

## Keep several explanations alive

Worlds may branch, disagree, receive weights, be selected for one planning pass, or be pruned. Selection is not canonization. Pairwise relations and open-world cardinality constraints reject impossible explicit combinations without manufacturing closure.

```bash
./lacuna cardinality-add /tmp/lacuna-stories \
  --constraint-id crd.single-culprit \
  --label "Exactly one culprit" \
  --claim-id clm_ada --claim-id clm_basil --claim-id clm_cora \
  --min-true 1 --max-true 1 \
  --rationale "The authored mystery has one culprit."
```

`Ada=true` does not create `Basil=false`; two explicit falsehoods do not create the final truth. Lacuna refuses only a partial valuation that no unresolved completion can satisfy.

## Reweight without collapsing the world bank

Inspect the complete live/selected population and issue a review for one active evidence assertion:

```bash
./lacuna particle-bank /tmp/lacuna-stories
./lacuna particle-update-review /tmp/lacuna-stories ast_red_dust > /tmp/particle-review.json
```

Then assess every required world exactly once using the returned digest:

```bash
./lacuna particle-update /tmp/lacuna-stories ast_red_dust \
  --expected-bank-sha256 DIGEST_FROM_REVIEW \
  --assessment wld_river=0.8 \
  --assessment wld_road=0.2 \
  --reason "The threshold dust favors the river-route hypothesis."

./lacuna particle-updates /tmp/lacuna-stories
```

The update implements normalized `prior × likelihood` planning weights over the complete eligible population. Likelihoods are authored quantities, not calibrated probabilities. One assertion may act as one factor only. If that assertion is later superseded, Lacuna preserves the historical update and reports reweighting debt rather than silently rewriting the vector. ESS, entropy, maximum mass, valuation duplicates, and likelihood divergence are diagnostics—not truth, diversity, or quality certificates.

A world-scoped director cannot mutate the global bank; an unscoped director may submit a reviewed update through the turn contract. See `docs/protocols/PARTICLE_BANK.md`.

## Reconcile withdrawn evidence without rewriting history

Inspect the current factor epoch and projected repair:

```bash
./lacuna particle-reconciliation-review /tmp/lacuna-stories \
  > /tmp/reconciliation-review.json
```

When the review is ready, submit its exact digest:

```bash
./lacuna particle-reconcile /tmp/lacuna-stories \
  --reconciliation-id prc.red-dust-withdrawal \
  --expected-reconciliation-sha256 DIGEST_FROM_REVIEW \
  --reason "Replay active factors and exclude superseded evidence."

./lacuna particle-reconciliations /tmp/lacuna-stories
```

Reconciliation starts from the immutable prior stored by the first update in the latest structurally coherent epoch. It replays every active factor once, records ended factors as excluded history, and normalizes with max-shifted log arithmetic. Structural changes to world membership, valuation, custody, status, or authored prior begin a new epoch rather than carrying old assessments forward. The result changes weights only and appends `particle.reconciled`; no earlier update is edited.

The review, factor dispositions, world arithmetic, and reconciliation history are available only to unscoped planner authority. See `docs/protocols/FACTOR_LEDGER_RECONCILIATION.md` and `docs/research/RESEARCH_rev0169.md`.

## Ask why a record exists

```bash
./lacuna explain /tmp/lacuna-stories ast_seen_cup
./lacuna explain /tmp/lacuna-stories ast_seen_cup --agent-id player
```

Planner explanations include full custody and structural links. Perspective explanations are a separate visibility-safe projection: privileged record kinds, hidden dependency IDs, raw event payloads, change IDs, source locators, and invisible ancestry are omitted.

## What rev0169 contains

- Rev0169 test-harness repair: close-time SQLite WAL cleanup now uses a bounded passive checkpoint instead of a truncating checkpoint that can block behind another fixture, subprocess, or reader connection.
- Rev0169 scenario safety: generated scenario capsules must have their placeholder player inputs and model-policy placeholders replaced before `scenario begin` or bundle planning will proceed.
- Rev0169 release clarity: the archive has a top-level MIT `LICENSE`, current revision records, and a bounded module/method `tools/run_acceptance.py` runner for recipient testing.
- All rev0167 method-identifiability custody: primary blind ratings freeze before method guesses, correctness is joined only during unblinding, bundle block seals bind masking artifacts, and bundle-staged child unblinding is parent-gated.
- All rev0166 send-ready release surfaces: `PLAY_NOW.md` for a player, `FOR_GWERN.md` for the research claim and shortest appraisal path, and `OPERATE_LACUNA.md` for the parent/operator.
- `artifact check`, a read-only extracted-release doctor that verifies the manifest, exact member set on request, version/revision/root coherence, Python syntax, JSON/TOML parsing, and relative Markdown links without writing bytecode into the release.
- `checkpoint run next-turn`, `checkpoint run narrator-capsule`, `history build`, and `history complete`, giving the clean post-checkpoint condition an explicit fresh-narrator handoff and honest partial-versus-complete public prose custody.
- `lacuna.public-history.v2`, `lacuna.public-history-view.v2`, and `lacuna.checkpoint-continuation-dispatch.v2`, distinguishing `typed-only`, `bound-public-history`, and `complete-bound-public-history` context modes.
- `lacuna.scenario-contamination-plan.v1` and `lacuna.scenario-contamination-scan.v1`, with one operator-only and one filesystem-only exact canary per opaque cell and complete retained-tree scanning of regular-file bodies and relative pathnames before blind rating.
- Scenario run/report v3, bundle v2, block-seal v3, and bundle-report v3 custody, preserving rater-level primary ratings, method guesses, confidence, recognition/familiarity, cue text, correctness after unblind, and spreadsheet-safe CSV export.
- Scenario bundle preregistration, public commitments, optional witness gates, one-active-block execution, seal-all-before-any-unblind custody, partial unblind recovery, and all-block aggregate exports.
- Shared durable request/narration-source custody, sidecar descriptor authentication, incremental scanning, exact rollback preparation, historical commit recovery, and parent-only accept/recover/commit/presentation authority.
- A release-surface regression test that requires the README opening to name the current revision and forbids the stale rev0166/rev0165 public blurb that motivated this polish pass.
- Database schema 8 and event schema 1 unchanged.
- Current architecture, research, decisions, audit, threat, operator, schema, and acceptance records under `docs/`.

Python 3.11+ is required. There are no third-party runtime dependencies. The bundled `./lacuna` launcher starts Python with `-S` and disables bytecode writes, preventing ambient site-packages/`sitecustomize` hooks from entering the executable boundary and keeping read-only artifact checks from dirtying a clean extraction.

For first-contact acceptance, run the send-facing smoke suite. It covers the artifact audit, release-surface documents, and the generated-scenario-template gate in fresh subprocesses:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 tools/run_acceptance.py --timeout 60
```

For the expanded deterministic suite, still without the intentionally heavy integration/E2E/schema gates:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 tools/run_acceptance.py --all-modules --timeout 60
```

In short wall-clock windows, run the expanded suite in shards:

```bash
for shard in 1/8 2/8 3/8 4/8 5/8 6/8 7/8 8/8; do
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 tools/run_acceptance.py --all-modules --timeout 60 --shard "$shard"
done
```

For exhaustive opt-in verification, including checkpoint/sidecar integration tests, scenario/bundle lifecycle tests, launcher subprocess E2E tests, and optional Draft 2020-12 schema checks, install the schema test extra and run finer bounded shards with `--all`:

```bash
python3 -m pip install -e '.[test]'
for shard in $(seq 1 32); do
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 tools/run_acceptance.py --all --timeout 90 --shard "${shard}/32"
done
```

The recipient-facing acceptance path is `tools/run_acceptance.py`. Plain monolithic `unittest discover` is left for local development only; in constrained shells prefer the smoke command, the explicit expanded `--all-modules` walk, or the opt-in `--all` shards above so failures name a module or method instead of looking like a hang.

## Core commands

```text
campaign init/create/list/select/show/path
play start
model brief
history build/complete
checkpoint run begin/status/dispatch/accept/record-failure/recover/commit/narrator-capsule/next-turn/continuation
scenario template/begin/status/recover/dispatch/record/contamination/rating-template/rate/unblind
scenario bundle template/begin/status/recover/commitment/witness-template/witness/dispatch/record/rating-template/rate/seal/unblind/export
checkpoint begin/card/dispatch/assemble/review/commit (lower-level stateless protocol)
turn run begin/status/dispatch/accept/recover/commit; lower-level packet/plan/card/commit
seal prepare/create/list/receipt/verify/reveal/void
init / migrate        create a cube or migrate schema 1/2/3/4/5/6/7 to schema 8
status / head         inspect identity, counts, versions, and ledger head
apply                 apply one atomic JSON change-set
verify / rebuild      verify custody or replay projections from events
snapshot              export current semantic state
claims / relations    inspect propositions and pairwise constraints
cardinalities         inspect bounded claim groups
canon / unknowns      inspect anchors, consensus, and deliberate lacunae
worlds / world        inspect candidate worlds and assignments
particle-bank / particle-update-review / particle-update / particle-updates
particle-reconciliation-review / particle-reconcile / particle-reconciliations
revision-impact       produce a head-bound assignment revision review
consequences          inspect explicit dependency lifecycle
consequence-repair-review / consequence-repair-frontier / consequence-replace / consequence-repairs
perspective / context emit access-scoped epistemic projections
seal                  operate host-custodied fair-play commitments
conflicts / evidence  inspect tensions and evidence links
explain               trace origin, dependencies, and dependents
```

Mutation commands include `claim-add`, `relation-add`, `cardinality-add`, `assert`, `world-add`, `world-assign`, `world-revise`, `commitment-raise`, `consequence-link`, `consequence-replace`, host-only seal operations, complete-bank particle updates and reconciliations, evidence operations, and question operations. Run `./lacuna COMMAND --help` for exact arguments.

## Migration and integrity

```bash
./lacuna migrate /path/to/cube-or-selected-library
./lacuna verify /path/to/cube-or-selected-library
```

Migration updates physical projections and records step digests outside the story event stream. It does not rewrite old events or change the ledger head. Event schema remains 1.

The hash chain detects mutation when checked by the current verifier. It is not a digital signature or remote transparency log. Campaign metadata, transcript bodies, and unrevealed seal openings are outside the story ledger. A burden score, custody explanation, constraint witness, consequence link, or valid seal does not prove truth, causality, fairness, authorship, or artistic quality. See `docs/THREAT_MODEL.md`.

## Project map

```text
PLAY_NOW.md                    player-only entrance: say “Will you DM?” and begin
OPERATE_LACUNA.md              shortest capability-first operator/experiment entrance
lacuna                         executable launcher
src/lacuna/                    standard-library kernel and adapters
tests/                         invariant and executable end-to-end tests
schemas/                       strict exchange-format JSON Schemas
examples/                      multi-world and turn-contract fixtures
docs/protocols/                stable human/model operating contracts
docs/operators/                model-host entrances and provider handoffs
integrations/chatgpt/           Project/custom-GPT instructions and starters
docs/architecture/             current architecture
docs/research/                 source-backed design research
docs/audits/                   findings and repairs
REVISION.json                  lineage and revision receipt
MANIFEST.sha256                member-level archive integrity
```

Read `START_HERE.md`, then `docs/README.md`.
