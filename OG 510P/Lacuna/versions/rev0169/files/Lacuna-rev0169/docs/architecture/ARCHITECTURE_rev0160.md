# Architecture — rev0160

## Purpose

Revision 0160 turns rev0159’s source-bound retcon checkpoint exchange into one governed **managed checkpoint run**. The new layer solves operational continuity: it fixes provider routes, retains accepted and failed invocation custody, generates one exact next action, reconstructs the full artifact chain on every transition, and makes commit retry/recovery explicit.

It does not add a model client or a second commit engine. External workers still generate and evaluate speculative objects. Lacuna controls context manufacture, object validation, authority, state progression, rollback review, and durable acceptance.

The database remains schema 8. Immutable event envelopes remain schema 1. New contracts are exchange/sidecar schemas only.

## System layers

```text
player-facing play
    │
    ├─ play start / turn run v2
    │      └─ ordinary planner/narrator/builder/verifier custody
    │
    └─ parent decides backstage comparison is warranted
           │
           └─ checkpoint run v1 (private host sidecar)
                  │
                  ├─ fixed source request + protected state
                  ├─ fixed role/provider routes
                  ├─ exact cards and accepted outputs
                  ├─ ordered accepted/failed invocation receipts
                  ├─ deterministic run.json.next_action / NEXT.md
                  └─ parent-only proposal, review, commit/recovery
                               │
                               └─ existing turn preparation/receipt path
                                            │
                                            └─ event ledger + projections
```

The managed run is intentionally outside the immutable story ledger. Candidate futures, scores, model declarations, and rejected attempts are experiment/host custody. Only the narrow reviewed turn mutation and narration source can become durable story state.

## State machine

```text
awaiting-generator
    -- accepted candidates --> awaiting-judge
    -- failed attempt ------> awaiting-generator

awaiting-judge
    -- accepted judgment ---> awaiting-compressor
    -- failed attempt ------> awaiting-judge

awaiting-compressor
    -- accepted compression -> parent assembles proposal
                            -> awaiting-verifier
    -- failed attempt ------> awaiting-compressor

awaiting-verifier
    -- accepted refusal ----> verifier-refused (terminal)
    -- accepted pass -------> parent kernel review
                            -> ready-to-commit
    -- failed attempt ------> awaiting-verifier

ready-to-commit
    -- direct commit -------> committed
    -- exact durable match -> committed (recovered)

committed
    -- retry ---------------> same authenticated receipt
```

No worker transition can skip a stage. No failure advances. No accepted invocation may be followed by another attempt for the same role. A terminal refusal is never edited into readiness.

## Fixed sidecar topology

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
invocation-NNNN-generator|judge|compressor|verifier.json
run.json
NEXT.md
.run.lock
```

`run.json` is authoritative. For every status, an exact set of artifact keys must be present and all other fixed keys must remain null. Each referenced artifact has fixed path, media type, schema, role, and canonical digest. Unreferenced files are not authority.

`NEXT.md` is a deterministic rendering of `run.json.next_action`. It may be regenerated only after the manifest and every authoritative member pass audit.

## Managed manifest

`lacuna.checkpoint-run.v1` binds:

- project version, run ID/path, creation/update metadata, and original reference;
- canonical resolved cube path and cube ID;
- current status;
- complete provider route map for all four roles;
- checkpoint ID, expected head, trigger digest, request digest, and source turn-packet digest;
- all fixed artifact references;
- ordered invocation receipt references;
- one deterministic next action; and
- a fixed trust-boundary/nonclaim list.

The manifest is strict to the creating project version. It does not attempt cross-version run interpretation or path relocation.

## Source and path binding

Begin receives both an open `Cube` and a resolved path. It resolves `cube.root` and the supplied path with `strict=True` and requires equality before any run directory exists. It verifies the cube, builds the source-bound checkpoint request, and manufactures the first generator card before sidecar publication.

This prevents ordinary validation failures and caller path confusion from producing a plausible run. It does not create a hostile same-user filesystem boundary.

## Provider routes and dispatch

The four routes are fixed at begin:

```text
lacuna-retcon-generator  -> provider
lacuna-retcon-judge      -> provider
lacuna-retcon-compressor -> provider
lacuna-retcon-verifier   -> provider
```

A route can be `portable`, `codex`, `claude-code`, `gemini-cli`, or `chatgpt`. Different roles may use different providers. Empty or incomplete maps refuse.

`lacuna.checkpoint-run-agent-dispatch.v1` is recomputed from the current retained task card and fixed route. It includes:

- run, checkpoint, status, task, role, route, and provider alias;
- exact card digest and complete embedded card;
- exact output schema, staging path, and parent accept command;
- parent failure-record command;
- worker instructions and authority split; and
- explicit nonclaims.

The dispatch is self-contained so a remote chat need not see the filesystem. It is transport description, not invocation or attestation.

## Invocation custody

Each attempt produces one `lacuna.checkpoint-invocation-receipt.v1` with:

```text
run/checkpoint/sequence/attempt/role
fixed provider route + agent alias
card SHA-256
recomputed dispatch SHA-256
expected output schema
host-declared model/version/invocation/timing
accepted output reference OR failure class/message
recorded time
fixed declaration and nonclaims
```

Audit requires stage-order monotonicity, contiguous sequence numbers, per-role attempt numbering, no attempt after acceptance, and exactly one accepted receipt for every retained role output. A failed receipt has no output reference and never changes the stage. The manifest/schema ceiling is 1,000 receipts; capacity is checked before the next receipt is written so limit refusal cannot strand an invalid 1,001-entry manifest.

These records make retained host behavior inspectable. They do not prove which provider ran or whether calls were omitted.

## Full-chain reconstruction

Every audit reconstructs rather than trusts downstream artifacts:

1. validate manifest, routes, identity, topology, and fixed nonclaims;
2. read trigger and validate the exact checkpoint request;
3. rebuild and compare the generator card;
4. validate candidates, then rebuild and compare the judge card;
5. validate judgment, then rebuild and compare the compressor card;
6. validate compression, reassemble and compare the parent proposal;
7. rebuild and compare the verifier card;
8. validate verifier return and status semantics;
9. open the bound cube and validate the parent kernel review;
10. when committed, authenticate the checkpoint receipt against the durable change;
11. audit every invocation receipt against exact cards, dispatches, routes, and retained outputs;
12. recompute `next_action` and compare `NEXT.md` byte-for-byte.

Canonical JSON digests bind object semantics, not whitespace or key order. The trigger text is byte/text-bound through its own SHA-256.

## Authority matrix

| Actor | May do | May not do |
|---|---|---|
| generator | return exact bounded candidates | judge, compress, assemble, review, commit, present |
| judge | score provenance-stripped candidates under fixed rubric | change candidates, assemble, commit, present |
| compressor | return winner-only state card, narration, narrow operations | see rejected futures, choose a new winner, commit |
| verifier | return proposal-visible pass/refuse advice | recompute hidden selection independently, review kernel state, commit |
| parent/coordinator | route cards, record failures, accept outputs, assemble, review, commit/recover, present accepted narration | claim vendor attestation or bypass kernel acceptance |
| kernel | validate typed authority, prepare under rollback, commit/recover exact event chain | generate prose, choose aesthetics, invoke providers |

Provider aliases never grant parent authority to a worker.

## Review, receipt, and performance boundary

A passing verifier causes the parent to call the existing checkpoint review. Review revalidates the complete candidate/judgment/proposal chain and runs the real turn mutation under rollback. `ready-to-commit` therefore means exact preparation succeeded at the request head; it is not commitment or a reservation.

The public `validate_checkpoint_commit_receipt` remains a full-chain API. Managed audit and commit, after independently validating the full chain, use a package-internal receipt-document validator to avoid repeating the expensive exact preparation a second time. The helper never accepts an unvalidated request/proposal/review chain and still authenticates the durable event/receipt relationship.

## Crash and recovery matrix

| Failure point | Authoritative result | Recovery |
|---|---|---|
| validation before run publication | no run directory | correct input and retry begin |
| interruption during sidecar publication | possible incomplete orphan | no automatic repair/indexing; inspect/remove under host policy |
| output/receipt/card written before manifest | old manifest remains authority; leftover file ignored | retry current transition after audit |
| manifest written but `NEXT.md` missing/stale | authoritative state advanced | `checkpoint run recover` rewrites pointer only |
| SQLite commit succeeds before receipt/manifest publication | durable change exists, run still ready | retry commit; authenticate and publish recovered receipt |
| later valid writes advance cube head after checkpoint commit | durable historical checkpoint remains | reconstruct request-head prefix and authenticate exact event chain; no duplicate events |
| stale uncommitted proposal meets later head | no matching durable change | refuse; begin a fresh source-bound checkpoint |

Filesystem and SQLite are separate durability domains. Recovery verifies exact identity; it is not a best-effort merge.

## Shared sidecar boundary

`src/lacuna/sidecars.py` is now the common implementation for turn and checkpoint runs:

- canonical JSON digesting;
- bounded descriptor-based reads;
- UTF-8 JSON/text parsing;
- symlink, hardlink, nonregular, oversize, and detected substitution refusal;
- strict directory resolution;
- owner-only single-link lock authentication;
- nonblocking cooperative locking; and
- shell-command quoting.

The lock serializes cooperative transitions within one run. Stale-head checks remain the cross-run/cube mutation guard. There is no distributed lease or hostile-account protection.

## CLI and host surfaces

```text
checkpoint run begin
checkpoint run status
checkpoint run recover
checkpoint run dispatch
checkpoint run accept
checkpoint run record-failure
checkpoint run commit
```

The lower-level `checkpoint begin/card/dispatch/assemble/review/commit` surface remains available for custom hosts and experiments. It uses the same exchange objects and kernel path but has no authoritative managed state or invocation receipts.

## Unchanged foundations

Rev0160 does not change:

- database schema 8 or event schema 1;
- turn request v4 / grant v2 source semantics;
- candidate, judgment, compression, proposal, verifier, review, or commit-receipt v1 semantics;
- ordinary turn-run v2 and turn-preparation/receipt contracts;
- commitment, consequence, particle, factor, fair-play, access, or projection semantics; or
- the principle that model artifacts are advisory until parent/kernel acceptance.

## Explicit nonclaims

The architecture does not prove model identity, provider execution, tool denial, context isolation, independent judging, rollout quality, rubric validity, artistic optimality, fair sampling, or narrative improvement. It adds exact host-side custody and reproducible refusal boundaries around those external activities.
