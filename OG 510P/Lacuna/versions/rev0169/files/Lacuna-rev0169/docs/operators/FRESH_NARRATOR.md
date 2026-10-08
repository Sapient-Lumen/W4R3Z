# Fresh narrator continuation

The retcon-planning loop is incomplete if the model that continues the story still remembers every rejected candidate and rollout. Lacuna therefore joins an authenticated committed checkpoint to a newly opened, source-bound ordinary turn and emits one least-context fresh-narrator dispatch.

## Normal path: one command

After a managed checkpoint commits, its generated `NEXT.md` points to:

```bash
./lacuna checkpoint run next-turn CHECKPOINT_RUN_PATH \
  --player-input-file next-player-input.txt \
  --provider chatgpt \
  --format markdown
```

This command fails closed unless the checkpoint is committed and the cube is still at the checkpoint's accepted head. It then opens exactly one ordinary turn with these constraints:

- `input.kind = play-turn`;
- audience-only packet, with no director/planner context;
- `solo` topology;
- no anchor authority; and
- exact player input retained and digest-bound before narration.

It returns `lacuna.checkpoint-continuation-dispatch.v2`. The dispatch contains one complete `input_document` and one exact `lacuna.turn-proposal.v2` template. The dedicated worker role is `lacuna-fresh-narrator` (Codex alias `lacuna_fresh_narrator`).

The worker returns one root JSON object only. Save it to `return_contract.save_path`, run the printed `turn run accept` command, and then follow that ordinary turn run's `NEXT.md` through exact preparation and parent-only commit. Only the accepted turn receipt narration becomes player-visible.

## Capture and recovery boundary

`next-turn` creates the ordinary source request and run before it prints the dispatch. Capture its output and preferably supply a dedicated `--root` for the continuation segment. If the process completed but the printed handoff was lost, do **not** rerun `next-turn`: the first request has already advanced the cube, so the live-head guard will correctly refuse a second creation attempt.

Instead, locate the fresh `awaiting-solo-proposal` turn under the chosen root, audit it with `turn run status`, and regenerate the same handoff through:

```bash
./lacuna checkpoint run continuation \
  CHECKPOINT_RUN_PATH FRESH_TURN_RUN_PATH \
  --provider chatgpt \
  --format markdown
```

Do not delete the first turn, edit its packet, or rebase the checkpoint capsule. SQLite, the sidecar filesystem, and terminal delivery are separate durability domains; the bridge recovers exact retained custody rather than pretending they are one transaction.

## What the fresh narrator receives

The single dispatch binds:

- committed checkpoint run, request, proposal, compression, and receipt identities;
- exact selected-state-card and post-checkpoint audience-context digests;
- accepted previous checkpoint narration;
- typed audience-safe context;
- retained and omitted elements;
- preserved unknown IDs;
- forbidden contradictions and next pressures;
- exact next player input;
- exact ordinary turn packet and proposal identity; and
- optional digest-bound public history.

It excludes by construction:

- raw candidates and rejected rollout beats;
- judge scores and rationale;
- generator or worker provenance;
- verifier findings;
- parent orchestration history;
- unrelated run artifacts; and
- mutation, acceptance, recovery, or commit authority.

The input instructs the narrator to treat the state card as private soft planning guidance, not observed truth, and to treat player wording as an attempt until narration establishes an outcome.

## Preserve prose-only public continuity

Typed audience context is mechanically governed but may be sparse when earlier turns were narration-only. For the strongest local coverage claim, compile history from the committed checkpoint boundary and the retained ordinary-turn roots:

```bash
./lacuna history complete CHECKPOINT_RUN_PATH \
  --run-root TURN_RUNS \
  --format json > public-history.json
```

The ledger supplies the complete expected pre-checkpoint turn census; retained managed runs supply the exact player input and accepted narration. Missing transcript custody, direct/stateless turns without matching managed runs, duplicates, and run/ledger mismatches refuse. The parent retains `lacuna.public-history.v2`; the worker sees only `lacuna.public-history-view.v2` with `coverage_mode = complete-before-checkpoint` and `completeness = complete`.

When selective context is deliberate, `lacuna history build RUN_001 ...` remains available. It produces `coverage_mode = explicit-run-list` and `completeness = not-claimed`. The continuation dispatch exposes that distinction rather than calling a selected list complete.

Then bind either artifact:

```bash
./lacuna checkpoint run next-turn CHECKPOINT_RUN_PATH \
  --player-input-file next-player-input.txt \
  --public-history public-history.json \
  --provider chatgpt \
  --format markdown
```

Invalid history refuses before the continuation turn is opened. Complete coverage is limited to durable Lacuna play-purpose turns for the audience before that checkpoint; it cannot census uncommitted external chat. See [`PUBLIC_HISTORY.md`](PUBLIC_HISTORY.md).

## Lower-level paths

When a parent has already opened the exact fresh solo turn, bind it explicitly:

```bash
./lacuna checkpoint run continuation \
  CHECKPOINT_RUN_PATH TURN_RUN_PATH \
  --provider portable \
  --format markdown
```

The bridge requires the turn to be fresh, audience-only, `solo`, `play-turn`, no-anchor, and source-bound at the checkpoint's accepted head. A director turn, stale turn, already-advanced turn, different cube/audience, session-control request, or uncommitted checkpoint refuses.

To retain or inspect the reusable checkpoint-only capsule without opening a turn:

```bash
./lacuna checkpoint run narrator-capsule CHECKPOINT_RUN_PATH \
  --format json > fresh-narrator-capsule.json
```

`lacuna.checkpoint-narrator-capsule.v1` remains a private deterministic host artifact. The continuation dispatch authenticates and embeds its relevant content while adding the next ordinary turn's exact authority boundary.

## Why one dispatch matters

Rev0163 could compile a winner-only capsule, but an operator still had to combine that capsule with the next player input and independently open a turn. Rev0164 closed that authority seam. That left room for a weak coordinator to omit the input, widen the turn, reuse a director packet, or hand the narrator a freeform prompt that was not bound to the eventual proposal.

The rev0165 dispatch contract preserves that closed seam while making history coverage machine-readable: checkpoint output, compact state, public context, optional transcript history, exact player input, exact proposal template, save path, and parent accept command are one validated object.

## Scenario treatment

For the `lacuna-role-separated` condition:

- every checkpoint role uses a fresh, pairwise-distinct declared context;
- a committed checkpoint ends the current narrator segment;
- `checkpoint run next-turn` creates the first turn of a new segment;
- that first narrator invocation records the preceding checkpoint and capsule digest;
- optional public history follows the same preregistered coverage policy in every condition; and
- later turns may remain in the new narrator context until the next checkpoint.

`forward-only`, `prompt-only-retcon`, and `lacuna-serial` remain persistent-context controls. Context IDs and freshness remain host declarations. Lacuna verifies internal topology and artifact binding, not provider memory erasure.

## Product surfaces

A clean condition can use a new API request with no previous conversation link, a fresh role chat, or a native subagent with a card-only workspace. Projects, temporary chats, custom instructions, subagent filesystems, and provider retention can all change the true boundary. Record actual settings and use random private canaries as falsification pressure.

A canary appearing downstream is evidence of leakage. Its absence is not proof of isolation.

## State-card retention warning

The ledger binds the state-card digest. The full text remains in the committed checkpoint sidecar unless essential content was also encoded through typed operations. Preserve the sidecar or a private exact export. A digest cannot reconstruct a lost state card.

## Nonclaims

A passing continuation dispatch proves exact local linkage between one committed checkpoint, one compact state, an optional authenticated v2 parent history plus its coverage-labelled least-context public view, and one fresh source-bound ordinary turn. It does not prove:

- provider/model identity or genuine fresh memory;
- absence of tools, shared files, logs, or side channels;
- completeness of supplied public history;
- semantic fidelity of the narrator's prose;
- artistic sufficiency of the compressed state card; or
- that retcon planning improves fiction.
