# Architecture — rev0157

## Architectural thesis

Revision 0157 makes **readiness executable**.

In rev0156, the request-scoped run could prove that the correct packet, role returns, proposal, verifier result, manifest, and next-action pointer were present and mutually bound. That was strong workflow custody, but `ready-to-commit` still meant “the sidecar chain passed its validators.” The first full kernel execution happened only after the operator invoked commit.

Rev0157 moves the boundary. A run may publish `ready-to-commit` only after the exact final proposal has been normalized, applied through the real mutation engine inside SQLite, projected into its returned contexts, captured as a complete replay envelope, and rolled back. Commit then replays that frozen envelope rather than recomputing a merely equivalent change. If SQLite committed but the sidecar transition did not survive, recovery authenticates the durable change against the historical request-head cube and materializes the missing receipt without appending events again.

The architectural invariant is:

> Sidecar agreement can select what to rehearse; only exact kernel rehearsal can make it ready; only an exact durable replay or authenticated recovery can make it committed.

## Authority planes

| Plane | Owns | Does not own |
|---|---|---|
| Epistemic kernel | Event validity, projections, atomic typed mutation, deterministic verification | Model invocation, prose quality, provider identity |
| Turn contract | Source-bound input, grant, proposal identity, disclosure and scope checks | Workflow scheduling |
| Orchestration | Topology, least-context cards, ordered upstream bindings, advisory verifier | Ledger mutation |
| Turn run v2 | Request-scoped artifact custody, deterministic next action, readiness lifecycle, same-run serialization | World truth, distributed coordination |
| Turn preparation v1 | Exact rolled-back execution envelope at one request head | Head reservation or commitment |
| Turn receipt v3 | Binding from preparation to one durable change plus delivery provenance | Provider attestation or semantic truth |

## Shared mutation engine

`Cube._execute_changeset` is now the single internal execution path for ordinary apply, exact preview, and prepared apply.

It performs the same operations in each mode:

1. validate the strict change-set and expected head;
2. begin an immediate SQLite transaction;
3. prepare each operation under the kernel’s current invariants;
4. append events and update projections;
5. insert the change receipt row;
6. optionally inspect the still-transactional post-state;
7. commit or unconditionally roll back.

`preview_changeset` supplies a frozen timestamp and event IDs and always rolls back. `apply_prepared_changeset` supplies those same values and commits. The shared path removes a class of “preflight accepted a shape that commit interprets differently” drift.

An `after_apply` callback runs before either commit or rollback. Turn preparation uses it to read the exact event chain and build audience/planner contexts from the projected post-state. Prepared commit uses it to compare those artifacts while rollback is still possible.

## Deterministic proposal normalization

A model may omit identifiers for creator operations. Ordinary low-level normalization can still generate fresh IDs, but a turn proposal now supplies its `proposal_id` as an ID-generation seed. Omitted IDs are derived from:

- a domain-separated protocol label;
- proposal ID;
- ID prefix;
- operation index; and
- ID field.

The result is stable across preparation validation, direct commit, and historical recovery. Explicit model-supplied IDs remain authoritative and are still validated normally. Event IDs are not derived; they are collision-resistant values generated once during preparation and frozen into the replay envelope.

## Turn preparation envelope

`43-turn-preparation.json` has schema `lacuna.turn-preparation.v1`. It contains:

- cube, request, proposal, actor, audience, access-mode, and grant bindings;
- canonical proposal and normalized change-set digests;
- normalized operations and generated identifiers;
- one `prepared_at` timestamp;
- ordered event IDs and the complete event rows, including payloads, previous hashes, and event hashes;
- the exact change receipt;
- the resulting ledger head;
- audience context and optional explicitly authorized planner context from the rehearsed post-state; and
- narrow nonclaims.

Preparation construction is two-pass:

1. execute the proposal exactly and roll it back, capturing the envelope;
2. independently validate the envelope by replaying it again and rolling it back.

This catches both kernel refusal and envelope-construction drift before the run manifest publishes readiness.

## Run v2 lifecycle

The stable run layout adds a kernel-owned preparation artifact and lock:

```text
RUN_PATH/
├── 00-player-input.txt
├── 10-turn-packet.json
├── 11-orchestration-plan.json
├── 20-planner-card.json
├── 21-planner-return.json
├── 30-narrator-card.json
├── 31-narrator-return.json
├── 40-proposal-builder-card.json
├── 41-proposal-draft.json
├── 42-turn-proposal.json
├── 43-turn-preparation.json
├── 50-verifier-card.json
├── 51-verifier-return.json
├── 60-turn-receipt.json
├── .run.lock
├── run.json
└── NEXT.md
```

Solo and pair proposals are prepared before the accepting transition is published. In full mode, the candidate remains unprepared until an independently bound verifier return passes. A kernel-invalid proposal therefore never becomes the accepted final proposal in `run.json` and never reaches readiness.

At `ready-to-commit`, `NEXT.md` points to the complete preparation, not merely the proposal. A less capable coordinator sees the exact object that the kernel rehearsed and will replay.

## Exact direct commit

A direct run commit holds the same-run lock and:

1. audits every artifact and deterministic pointer;
2. re-authenticates the preparation by an exact rollback replay;
3. requires the live cube head to equal the request head;
4. applies the frozen change-set, timestamp, and event IDs;
5. before committing, compares the durable payload digest, change receipt, complete event chain, audience context, and optional planner context with the preparation;
6. rolls back on any mismatch;
7. commits only after exact equality;
8. writes a `lacuna.turn-receipt.v3` with `delivery.mode = "direct"`; and
9. advances and re-audits the sidecar.

The database transaction is authoritative. Sidecar publication remains a separate filesystem transition.

## Historical crash recovery

A process can die after SQLite commit and before receipt/manifest persistence. On retry, the run sees that its prepared `proposal_id` already exists and enters recovery rather than reapplication.

`Cube.snapshot_at_head` uses SQLite’s backup API to copy the live cube into memory. It requires an exact changeset boundary, removes later events and changes only from the copy, clears all projections, rebuilds them from the retained event prefix, and verifies that the reconstructed head is exact.

Recovery then:

1. verifies the current live cube;
2. authenticates the preparation by replaying it against the reconstructed request-head cube and rolling back;
3. reads the durable prepared change from the live cube;
4. compares its canonical payload digest, exact change receipt, and complete event chain with the preparation;
5. creates a v3 receipt with `delivery.mode = "recovered"`; and
6. records whether historical reconstruction was required.

No prepared event is appended during recovery. Later valid turns may have advanced the live head; the historical prefix authenticates the original post-state without discarding those later turns.

## Same-run serialization

Every run contains `.run.lock`. Status, accept, and commit open it without following symlinks where supported, require a regular single-linked file with owner-only read/write permissions, and take a nonblocking advisory exclusive lock for the complete transition.

This prevents two cooperative local coordinators from simultaneously advancing one sidecar and closes common symlink/hard-link substitution paths. It is deliberately not described as a distributed lock, a per-cube scheduler, or protection from a hostile account controlling both filesystem and database.

Different runs against one cube are still coordinated by the ledger’s expected-head and change-ID invariants. One may commit; stale peers refuse.

## Audit model

Run audit now recomputes and validates:

- fixed artifact path, media type, schema, role, and digest;
- exact retained input, packet, plan, task cards, ordered role returns, and proposal binding;
- status from topology and artifact presence;
- verifier terminal/pass semantics;
- preparation schema, field set, event hash continuity, proposal/change digests, and exact historical or current-head replay;
- for committed runs, durable change equality and receipt binding;
- deterministic next action and byte-exact `NEXT.md`; and
- lock-file safety.

A preparation whose contexts are edited and rehashed still fails because contexts are regenerated from the projected historical post-state. A preparation with recomputed event hashes still fails because exact event IDs, payloads, receipt, and contexts must all replay together.

## Compatibility and migration

The database remains schema 8 and the event format remains version 1. No cube migration is required.

The lower-level `commit_turn_proposal` Python entrance remains available. It now performs a rollback preparation and exact prepared commit internally, so direct callers inherit the strengthened semantics without adopting run directories.

Turn-run and receipt exchange formats advance to v2 and v3. Historical v1 run artifacts remain historical records; rev0157 does not silently reinterpret them as exact preparations.

## Remaining boundaries

Rev0157 does not claim:

- one transaction across SQLite and sidecar files;
- automatic cleanup of a request event left by a begin-time crash;
- distributed, cross-machine, or hostile-host locking;
- per-cube scheduling across distinct run directories;
- relocatable absolute-path run manifests;
- provider invocation, identity, confidentiality, or signed attestation;
- semantic proof that model prose follows hidden-state restrictions;
- truth, narrative quality, fairness, or successful retcon generation; or
- candidate-world generation, rollout, resampling, scoring, pruning, or selection.

The revision hardens custody at the point where a workflow claim becomes an executable state transition. It does not enlarge the kernel’s epistemic claims.
