# Rev0689 — mission reclaim compass

## Scope of this linked revision

Rev0689 is a deep-read mission and roadmap correction pass. It intentionally makes no C++ source, binary, capability, fixture, or runtime behavior change. The active executable remains:

- `bin/rev0688/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3`

This revision exists because rev0688 added the right row shape but not yet the right worker lifecycle. The new `sync_session_resume_transfer_workorders` table is the correct next seam, but its current use still claims and completes rows in one fake-peer executor transaction. That is audit evidence; it is not yet daemon-grade scheduling.

## Heart of the mission

AnonSync is not primarily a ledger product, proof archive, scheduler demo, or generic authorization sidecar. The heart of the mission is:

> Make authorized devices converge on the same intended folder tree without treating a central service as the ordinary source of truth, while preserving enough evidence to recover safely, reject stale or forged work, and expose conflicts honestly.

The heart can be compressed to: **folder convergence under evidence-bound local truth**.

That phrase has two hard requirements:

1. **Folder convergence:** source/destination truth must be proven by live filesystem and manifest evidence, not by successful function calls alone.
2. **Evidence-bound local truth:** every mutation needs durable, replay-safe, peer/folder/session-scoped evidence that explains why it was allowed and how it can be recovered after interruption.

Rev0688 is mission-aligned because it turns invisible transfer work into durable worker-owned rows. Rev0689's correction is that the row must become a lifecycle, not just a receipt attached to a successful fake-peer pass.

## What the cube already does well

The current cube has recovered from the earlier mission drift. The rev0650 correction named the product as C++ peer-to-peer folder synchronization. The rev0651–rev0670 arc built sync-domain objects and a peer transfer-round path. Rev0671 identified the need for a vertical fake session. Rev0672–rev0688 then built that vertical proof and a restart stack around it.

The strongest current chain is:

`source scan → destination scan → manifest diff → local apply plan → staged inspection → chunk request → peer schedule → peer-bound response batch → peer transfer-round continuation → receipt-gated materialization → committed staging cleanup → destination rescan → content convergence → SQLite session checkpoint → manifest chunk-row persistence → read-only checkpoint verification → exact chunk receipt coverage guard → source filesystem probe → destination filesystem probe → staging cleanup probe → DB-bound terminal staging repair sweeper → read-only resume action plan router → MaterializeStagedFile resume executor → CleanupCommittedStaging resume executor → ResumeTransfer work-order planner → fake-peer ResumeTransfer executor → bounded resume-cycle drain executor → durable worker-owned resume transfer workorder rows`

The repeated discipline is the asset: caller-supplied mutable state is re-derived and checked before bytes are written or local paths are mutated.

## What is missing

The main missing piece is now a **crash-surviving worker boundary**.

Rev0688 rows store worker id, lease id, lease epoch, peer/session/request/schedule/execution keys, staging path, source manifest chunk evidence, and state. But there are only two states, `claimed` and `completed`, and the public executor claims a row immediately before writing the chunk, then completes it immediately after receipt-backed verification. A crash between those points is representable in the table shape but not yet intentionally executable as product behavior.

Concrete missing pieces:

1. **Separate claim API:** no public mutating function persists `claimed` rows and returns before writing bytes.
2. **Owned-claim executor:** no executor consumes only pre-existing rows owned by the current worker/lease.
3. **Lease time policy:** no `claimed_at`, `lease_expires_at`, monotonic epoch/clock policy, retry window, attempt count, or expiration rule.
4. **Reclaim/abandon/quarantine:** no state transition differentiates live claims, expired claims, stolen claims, retryable claims, abandoned claims, and suspicious claims.
5. **Peer response attachment:** no production peer response path can yet prove that bytes correspond to an already claimed workorder row.
6. **Overwrite replay evidence:** existing-target replacement replay still lacks durable pre-mutation evidence.
7. **Tombstone/conflict replay:** deletes and conflict-copy preservation are product nouns, but they are not yet restart-drained through the same cycle discipline as file fetch.
8. **Trust and privacy material:** folder membership, device identity, invite/share-key epochs, revocation, metadata minimization, and retention policy are not yet concrete product structs.
9. **Resource governance:** staged writes lack explicit disk budgets, chunk budgets, cancellation, retry caps, and per-peer backpressure rules.
10. **Review shape:** `sync_domain.cpp` and the selftest corpus are now large enough that future scheduler and transport changes will be harder to audit unless split by trust domain.

## What should change

### Change 1 — make `claimed` a real product boundary

The next code-bearing revision should introduce a first-class transfer workorder claim function. It should load the same checkpoint/action/transfer-planner evidence as rev0688, insert or preserve durable `claimed` rows, and stop. It should not read source bytes, write staged bytes, write receipt sidecars, or mark rows completed.

Acceptance target:

1. create an interrupted fake-session checkpoint with missing staged chunks;
2. call the claim function;
3. prove `sync_session_resume_transfer_workorders` contains `claimed` rows with request, peer request, schedule, execution, peer, worker, lease, source chunk, apply intent, and staging evidence;
4. prove staged files and receipt rows are still absent or unchanged;
5. restart/reopen SQLite and prove the same rows remain claim-owned.

### Change 2 — execute only owned claimed rows

The next executor should consume rows that already exist. It should reject work unless row ownership and evidence match the current session, worker, lease, peer, manifest chunk, apply intent, source action, request keys, and staging path. It can still use a fake source root in the test harness, but its precondition should be a claimed row rather than a recomputed local plan.

Acceptance target:

1. execute rows claimed in a prior phase;
2. verify source chunk bytes against manifest rows;
3. write staged bytes and receipt files;
4. upsert receipt rows;
5. update exactly one matching row from `claimed` to `completed` per chunk;
6. reject mismatched worker id, lease id, execution key, stale manifest chunk, or staging path.

### Change 3 — define reclaim before transport

Add explicit state and policy before attaching real networking. A minimum shape is:

- `claimed`
- `completed`
- `expired` or derived expired view
- `reclaimed`
- `abandoned`
- `quarantined`

The exact schema can differ, but the behavior must not erase evidence. Reclaim should be a new row transition, not a silent overwrite of another worker's claim.

### Change 4 — bind peer responses to claims

Only after claim/execute/reclaim works locally should real peer response acceptance attach to the workorder table. Production peer bytes should satisfy an existing claimed row; they should not cause new scheduler work to appear implicitly.

### Change 5 — promote policy nouns into C++

Conflict policy, tombstone retention, overwrite preflight, metadata privacy, folder membership, device identity, and peer authority should become structs and tests. They should stop living only in ceilings and roadmap prose.

## What should stop

Stop adding another generic proof boundary unless it protects a sync path involving a folder, file, manifest, chunk, peer, claim, receipt, materialization, tombstone, conflict, or recovery state.

Stop describing rows as scheduler-ready if they can only be created and completed inside one executor call.

Stop moving toward production transport until a row can survive interruption in `claimed` and be recovered without recomputing invisible work.

## Recommended next code-bearing revision

**Rev0690 — split resume transfer claim from execution**

Recommended public surface:

- `claim_sync_session_checkpoint_resume_transfer_workorders`
- `execute_claimed_sync_session_checkpoint_resume_transfer_workorders`
- result counters for rows planned, newly claimed, already claimed, executed, completed, rejected, and left pending

Recommended validator assertions:

1. a claim-only run creates durable `claimed` rows but no staged bytes or receipt rows;
2. a second claim-only run is idempotent;
3. an execute-owned run writes chunks and marks rows `completed`;
4. mismatched worker/lease execution is rejected;
5. a crash-simulated reopen sees claimed rows before execution;
6. the existing resume cycle can be adapted to call claim then execute without losing strict final convergence.

## Session operating rule

For this working session, each linked turn should preserve the filename shape:

`Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip`

The linked artifact should have the full filename written out as the link text. One link per turn is enough.

## Honest ceiling after rev0689

Rev0689 does not claim new runtime behavior. The active C++ behavior remains rev0688: fake-peer transfer work is represented as completed worker-owned durable rows. AnonSync is still not a production peer discovery system, encrypted peer protocol, persisted multi-worker scheduler, file watcher, daemon, UI, invite/share-key authority, or deployable privacy-preserving distributed sync product. The next useful proof is not more prose; it is splitting transfer workorder claim from execution and proving an interrupted claimed row can be recovered honestly.
