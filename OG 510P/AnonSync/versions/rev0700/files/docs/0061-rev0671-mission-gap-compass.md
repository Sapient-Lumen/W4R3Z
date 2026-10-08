# Rev0671 — mission gap compass

## Scope of this linked revision

Rev0671 is a deep-read mission and roadmap correction pass. It intentionally makes no C++ source, binary, capability, fixture, or runtime behavior change. The active executable remains:

- `bin/rev0670/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3`

The goal of this revision is to make the next code-bearing move harder to mis-aim. The cube has become technically coherent, but it is still more a set of evidence-bound sync primitives than a sync session that makes two folders converge.

## Heart of the mission

AnonSync is not primarily a ledger product, a proof archive, a relay/idempotency demo, or a generic authorization sidecar. The heart of the mission is:

> Make authorized devices converge on the same intended folder tree without treating a central service as the ordinary source of truth, while preserving enough evidence to recover safely, reject stale or forged work, and expose conflicts honestly.

The product noun is **folder convergence**. The security/durability noun is **evidence-bound local truth**. Put together, the heart is folder convergence under evidence-bound local truth. A successful AnonSync revision should move one of these nouns closer to a working peer-to-peer file synchronization engine.

## What the cube already does well

The rev0651-rev0670 arc corrected the earlier mission drift and built useful C++ sync-domain substrate:

- portable relative path validation and deterministic folder manifests;
- file/tombstone entries, chunk ranges, lineage, entry digests, and publisher-neutral version digests;
- local/remote manifest diff planning and local apply intent planning;
- stale-target guarded file materialization, remote tombstone application, and regular-file conflict-copy preservation;
- receipt-backed staged chunk writes, receipt-gated materialization, staged-transfer inspection, and exact missing-chunk planning;
- request-bound chunk acceptance, individual and batch response envelopes, peer chunk scheduling, peer-bound response acceptance, and peer transfer-round continuation.

The strongest product asset is not any one API. It is the repeated discipline that caller-supplied mutable state is re-derived and checked before bytes are written or local paths are mutated.

## What is missing

The biggest missing piece is not another envelope around one more micro-boundary. The missing piece is a **session loop**.

Rev0670 can safely advance one scheduled peer response into post-write inspection, the next request, the next schedule, or materialization-ready evidence. But there is still no C++ harness that acts like two authorized peers and drives the whole loop:

`scan local folder → exchange manifests → diff → plan local apply → inspect staged transfer → request chunks → schedule peers → build peer responses → accept peer transfer rounds → materialize complete files → apply tombstones/conflicts → rescan and prove convergence`

Without that vertical harness, the cube can keep adding correct small seams while still not demonstrating that AnonSync syncs.

Other missing product parts are now clearer:

1. **Durable sync state:** no persisted manifest/index table, transfer table, peer assignment table, receipt table, mutation state table, retry state, or resumable scheduler state.
2. **Cleanup discipline:** `.part` files and `.chunks` receipt sidecars are not garbage-collected after materialization, conflict promotion, crash recovery, or abandoned transfers.
3. **Peer/folder trust:** peer identity, folder membership, session identity, invite/share keys, revocation, and key rotation are not yet modeled as non-caller-authored authority.
4. **Conflict and deletion semantics:** local tombstone vs remote file, local rename vs remote edit, case/Unicode collisions, tombstone expiry, no-overwrite policy, and persisted conflict metadata remain undefined.
5. **Serialization and protocol surface:** the sync-domain objects are C++ structs and deterministic IDs, but there is no versioned peer message schema or authenticated session transcript.
6. **Privacy and metadata policy:** the product has not decided what peers learn about names, sizes, hashes, mtimes, deleted paths, conflict metadata, device IDs, logs, or retention windows.
7. **Resource governance:** max file size, manifest size, chunk queue size, transfer concurrency, database growth, per-peer caps, backpressure, and denial-of-service boundaries are not yet product rules.
8. **Daemon/runtime integration:** there is no file watcher, discovery, LAN/WAN/NAT behavior, relay mode, mobile/desktop daemon, or operational UX.
9. **Code shape:** sync-domain behavior is concentrated in large files; that is acceptable for the current cube, but it will make protocol/session/persistence work harder if left unresolved too long.
10. **Validation shape:** validators strongly check packaging and phrase evidence. The next validators should also assert end-to-end sync outcomes.

## What should change

The next code-bearing revision should optimize for vertical product proof, not another isolated safety wrapper.

### Change 1 — make the fake peer-session harness the next north star

Build a deterministic C++ fake session that uses the existing primitives exactly as a future daemon would. It should create two fixture roots, scan one or both, compute the manifest diff, plan local apply, request missing chunks, schedule a peer, produce peer-bound responses from the source root, accept those responses through `accept_sync_peer_chunk_response_batch_and_plan_next`, materialize with receipt gating, apply tombstones/conflicts where applicable, and finally rescan to prove convergence.

This harness can be local and fake. It should not add real networking yet. Its job is to force the current primitives into a product loop.

### Change 2 — defer real transport until session semantics exist

LAN discovery, encrypted transport, NAT traversal, relay service, and daemon UX should wait until the fake session proves the sync semantics. Otherwise transport work will freeze the wrong abstractions.

### Change 3 — make persistence the second north star

After the fake session harness, add a minimal SQLite-backed sync state schema for manifests, apply intents, transfer rounds, peer assignments, receipts, mutation terminal states, and cleanup checkpoints. The cube already has SQLite/WAL machinery; it should now be mapped to concrete sync mutations and transfer state.

### Change 4 — turn validators into product validators

Keep package validators, but add a product validator that fails unless a fixture pair converges and the evidence proves how it converged. The validator should inspect outputs like final manifests, staged receipt counts, materialization result, conflict-copy result, and tombstone result.

### Change 5 — promote policy decisions from ceilings into structs

Metadata policy, conflict policy, tombstone retention, case sensitivity, Unicode normalization, and no-overwrite semantics should stop living only in prose. They should become explicit C++ policy structs and test cases.

### Change 6 — keep each revision attached to a sync path

A future change should be rejected if its main subject is only proof material, generic relay authority, or packaging. It should protect or advance a path involving a file, folder, peer, manifest, chunk, commit, tombstone, conflict, or recovery state.

## Recommended next revision

The best next code-bearing revision is:

**Rev0672 — deterministic fake peer-session harness**

Acceptance target:

1. create source and destination fixture roots;
2. scan source into a manifest;
3. diff destination against source;
4. build a `StageRemoteFile` apply intent;
5. inspect an empty staged transfer;
6. build a bounded chunk request;
7. build a peer schedule;
8. synthesize peer-bound response batches from the source bytes;
9. advance one or more peer transfer rounds until `ready_to_materialize`;
10. materialize with `require_chunk_receipts=true`;
11. rescan destination and prove content convergence with the source manifest.

Stretch target: add one remote tombstone and one regular-file conflict-copy preservation case in the same fake session harness, but only if the file-fetch convergence path stays small and deterministic.

## Session operating rule

For this working session, each linked turn should preserve the filename shape:

`Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip`

The linked artifact should have the full filename written out as the link text. One link per turn is enough.

## Honest ceiling after rev0671

Rev0671 does not claim new runtime behavior. The active C++ behavior remains rev0670: peer transfer-round continuation over local deterministic evidence. AnonSync is still not a production peer discovery system, encrypted peer protocol, persisted transfer scheduler, file watcher, daemon, or deployable privacy-preserving distributed sync product. The next useful proof is not more prose; it is a fake peer session that makes folders converge through the current C++ sync-domain boundaries.
