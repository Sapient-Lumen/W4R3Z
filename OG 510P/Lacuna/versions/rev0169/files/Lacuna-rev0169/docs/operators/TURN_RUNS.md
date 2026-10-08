# Request-scoped turn runs

A turn run is a private sidecar state machine for one exact player or session-control message. It retains the complete handoff chain across separate model calls and CLI invocations while keeping ledger mutation with the parent and kernel.

`run.json` is authoritative. `NEXT.md` is a deterministic, recoverable pointer.

## Start from one sentence

```bash
./lacuna play start .lacuna-play \
  --bootstrap \
  --profile orchestrated \
  --format markdown
```

The default exact input is `Will you DM?` with `input.kind = session-control`.

For an ordinary in-play message:

```bash
printf '%s' 'I listen beneath the floorboards.' > player-message.txt

./lacuna turn run begin .lacuna-play \
  --root .lacuna-runs \
  --player-input-file player-message.txt \
  --input-kind play-turn \
  --director --mode auto --format markdown
```

Use `--input-kind session-control` for start, resume, pause, mode change, or other out-of-fiction management text. The kind is validated and retained before any mutation.

## Directory contract

The run directory is created with owner-only access and a collision-resistant name.

| File | Purpose |
|---|---|
| `00-player-input.txt` | Exact UTF-8 input retained outside the event ledger |
| `10-turn-packet.json` | Source-bound request-v2/v3 packet, contexts, grant, and safe proposal template |
| `11-orchestration-plan.json` | Deterministic topology decision |
| `20-planner-card.json` / `21-planner-return.json` | Privileged planning handoff |
| `30-narrator-card.json` / `31-narrator-return.json` | Audience-only narration handoff |
| `40-proposal-builder-card.json` | Full-mode serializer envelope |
| `41-proposal-draft.json` | Safe parent proposal draft for solo/pair |
| `42-turn-proposal.json` | Exact accepted proposal candidate |
| `43-turn-preparation.json` | Rolled-back exact kernel execution envelope |
| `50-verifier-card.json` / `51-verifier-return.json` | Full-mode independent check |
| `60-turn-receipt.json` | Direct or authenticated recovered receipt |
| `.run.lock` | Owner-only cooperative same-run lock |
| `run.json` | Strict `lacuna.turn-run.v2` manifest and artifact digests |
| `NEXT.md` | Human/model pointer deterministically rendered from `run.json` |

Only files referenced by the strict manifest and required by the exact topology have authority. An unreferenced interrupted-write remnant does not advance the run.

## State machine

```text
solo:
  awaiting-solo-proposal
      → exact kernel rollback preparation
      → ready-to-commit
      → committed

pair:
  awaiting-planner
      → awaiting-narrator
      → awaiting-pair-proposal
      → exact kernel rollback preparation
      → ready-to-commit
      → committed

full:
  awaiting-planner
      → awaiting-narrator
      → awaiting-proposal-builder
      → awaiting-verifier
      → verifier-refused (terminal)
        or exact kernel rollback preparation
      → ready-to-commit
      → committed
```

A structurally well-formed but kernel-invalid proposal does not become ready. Preparation occurs before the final sidecar transition is published.

## Follow one pointer

```bash
cat RUN_PATH/NEXT.md
```

The pointer names:

- one owner;
- one complete input artifact;
- one required schema;
- one exact parent command;
- one player-visibility rule.

Do not choose a stage because another file exists. Do not edit IDs or digests. Do not summarize a card into a homemade prompt.

## Self-contained worker dispatch

For a delegated owner:

```bash
./lacuna turn run dispatch RUN_PATH \
  --provider portable|codex|claude-code|gemini-cli|chatgpt \
  --format markdown
```

The returned `lacuna.agent-dispatch.v1` embeds the exact card in `input_document` and repeats its digest, role, schema, authority, and return contract. This lets a chat worker operate without local filesystem access.

The worker returns one JSON object only. The parent saves it and runs:

```bash
./lacuna turn run accept RUN_PATH MODEL_RETURN.json --format markdown
```

A delegated worker cannot accept its own return or commit.

## Exact-input boundary

Prefer `--player-input-file` or standard input for newlines, shell metacharacters, and transcript-sensitive text. The packet binds exact UTF-8 content by SHA-256. The cube stores its digest and provenance rather than the transcript body.

JSON artifact digests use Lacuna canonical JSON: key order and whitespace are irrelevant; values and list order are authoritative.

Request v3 carries `input.kind`. Legacy v2 packets remain accepted and default to `play-turn` for compatibility.

## Exact preparation

At readiness, `43-turn-preparation.json` is the complete replay envelope. It contains the normalized proposal and operations, deterministic generated operation IDs, frozen time and event IDs, full event hash chain, change receipt, resulting head, and projected returned contexts.

Preparation is produced by applying the exact change through the real mutation engine inside SQLite and rolling the transaction back. It is then independently replayed and rolled back again for validation.

This proves local executable consistency at one request head. It does not commit, reserve the head, attest a provider, prove truth, or prove narrative quality.

## Exact direct commit

`turn run commit` holds the same-run lock and:

1. audits the complete sidecar chain and pointer;
2. re-authenticates the preparation by exact rollback replay;
3. requires the live cube head to equal the prepared request head when the change is absent;
4. applies the frozen timestamp, event IDs, operations, and payload;
5. compares the still-transactional receipt, full event chain, and projected contexts with preparation;
6. rolls back on any mismatch;
7. commits only after exact equality;
8. writes `60-turn-receipt.json`; and
9. transitions and re-audits the sidecar.

Only the receipt’s top-level `narration` is player-visible.

## Commit crash recovery

SQLite and the sidecar filesystem are separate durability domains. A process may commit the cube and die before writing the receipt or manifest transition.

On retry, commit checks whether the prepared proposal ID is already durable.

- When absent, it performs direct exact replay.
- When present, it verifies the live cube, reconstructs the exact request-head ledger prefix in an isolated in-memory database, authenticates the preparation there, compares the durable payload, receipt, and complete event chain, and materializes a recovered receipt without appending events again.

Later valid turns may already have advanced the live head. Historical reconstruction authenticates the original boundary without deleting or rewriting those later turns. Recovery records delivery provenance; it is not provider attestation.

## Deterministic pointer recovery

`NEXT.md` contains no independent authority. If it is missing, edited, or replaced by a link:

```bash
./lacuna turn run recover RUN_PATH --format markdown
```

The command:

1. acquires `.run.lock`;
2. audits every authoritative member while deliberately ignoring the pointer;
3. refuses on any authoritative inconsistency;
4. atomically writes the deterministic pointer; and
5. performs a full audit including the new pointer.

It does not reconstruct a packet, task card, role return, proposal, preparation, manifest, or receipt.

## Sidecar member integrity

Every authoritative member and `NEXT.md` read goes through an authenticated file descriptor. The reader refuses:

- symlinks;
- hard-linked files;
- non-regular files;
- members larger than the fixed read limit;
- path-to-descriptor identity mismatch;
- and detected size, metadata, or pathname substitution during the read.

This closes common accidental and cooperative-host link-substitution failures. It is not a hostile same-user security boundary; a process with equivalent authority can still bypass the CLI or attack between operations.

## Same-run concurrency

`status`, `recover`, `dispatch`, `accept`, and `commit` audit under an owner-only regular `.run.lock` where relevant; state-changing operations hold a nonblocking advisory exclusive lock across the transition. Concurrent cooperating coordinators receive a structured busy refusal.

The lock is per run and same host. It is not a distributed lease, per-cube scheduler, or transaction spanning SQLite and the filesystem. Different runs against one cube remain coordinated by expected-head and change-ID invariants.

## Audit refusals

A run refuses when, among other cases:

- a member is missing, linked, oversized, edited, relabelled, or digest-inconsistent;
- manifest paths, fixed metadata, topology, status, or next action differ from deterministic expectations;
- retained input and packet body differ;
- a return belongs to another packet, task, or upstream chain;
- a proposal changes source-bound identity or exceeds its grant;
- narration retains the fail-closed placeholder;
- a full run lacks a passing verifier;
- the kernel cannot apply or exactly replay the proposal;
- a prepared event, receipt, context, or payload differs;
- a durable change with the same ID has different custody;
- or `NEXT.md` is not the exact rendering of `run.json`.

Do not repair an integrity refusal by editing hashes. Correct the source process or begin a fresh request.

## Recovery table

| Condition | Correct action |
|---|---|
| Malformed or cross-turn worker return | Discard it; reissue the current complete dispatch |
| Kernel-invalid final proposal | Correct it while the run remains at the prior parent proposal stage |
| `verifier-refused` | Do not commit; begin a fresh run from retained input |
| Head advanced before the DB commit | Begin a fresh source-bound request; readiness was not a reservation |
| Matching DB commit survived sidecar crash | Re-run commit; authenticated recovery is automatic |
| Same change ID differs from preparation | Refuse and investigate |
| Only `NEXT.md` is damaged | Run explicit pointer recovery |
| An authoritative member is damaged | Recovery refuses; do not invent replacement custody |
| Run directory moved | Absolute paths no longer match; retain the original location |
| `begin` died before manifest completion | Inspect the immutable request source, then begin a fresh run |

## Privacy boundary

A run can contain exact player text, privileged planner context, model notes, a complete proposal, and prepared post-state contexts. Protect it according to its most privileged member.

Owner-only filesystem modes are not encryption or provider isolation. Keep credentials and unrevealed fair-play openings outside all model-readable run directories unless the host supplies a stronger boundary.

## What the proofs mean

A passing audit proves internal consistency under the current local verifier: exact artifact identities and digests, topology, bindings, preparation replay, historical reconstruction where needed, and durable equality for committed runs.

It does not prove model identity, semantic correctness, hard isolation, truth, fairness, or prose quality.
