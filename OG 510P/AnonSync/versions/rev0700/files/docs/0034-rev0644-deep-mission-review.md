# rev0644 deep mission review — corrected by rev0650

## Rev0650 correction

The rev0644 review was directionally useful about trust boundaries, replay, idempotency, and recovery, but it drew the wrong product conclusion. AnonSync is not a generic authorization/effect sidecar. **AnonSync is the C++ peer-to-peer file synchronization product.**

Treat the rev0644 findings as substrate lessons for sync: peer identity must not be caller-authored, file/sync-operation identity must be unambiguous, duplicate messages must not duplicate mutations, and restart/restore must not invent success.

## Corrected heart of the mission

The durable mission is AnonSync itself: a Resilio Sync-style C++ engine that keeps authorized devices converged on a shared folder.

A production AnonSync path needs four layers bound together:

1. **Sync interpretation:** paths, metadata, manifests, chunk hashes, tombstones, and conflict lineage map to one unambiguous meaning across peers.
2. **Peer/folder authority:** device identity, folder membership, key material, policy, and clock/trust context come from the right trust domains.
3. **Idempotent sync mutation:** retries, duplicate peer messages, restarts, partial transfers, and restore converge on one file version, tombstone, transfer, or conflict record.
4. **Recovery and reconciliation:** synced, pending, partial, applied, deleted, conflicted, failed, and unknown states remain distinguishable after interruption.

The code already contains useful machinery for those properties: normalized cases, claim and contract binding, JWT/event replay identities, idempotency keys, SQLite ledger chains, outbox rows, leases, signed terminal transitions, snapshot/restore verification, and a service-shaped ingress path. The correction is that these are not the product. They are the future sync mutation ledger and evidence substrate.

## What had gone severely wrong in the substrate

### 1. “Authenticated” identity was caller-authored

Through rev0643, `authenticated_context` lived inside caller-controlled JSON. The sender signed its own assertion of principal and authenticator. For sync, the equivalent bug would be allowing a peer message to declare its own trusted device/folder identity. Rev0644 separated typed trusted context from attacker-controlled request data; future sync peer sessions must keep that rule.

### 2. The public library API allowed policy construction

The old public config object exposed mutable security fields. A library caller could disable sender verification or substitute trust material. For sync, share policy, folder membership, peer trust roots, and transfer policy must come from authenticated operator/share state, not arbitrary caller-authored fields.

### 3. A valid nonce could be consumed without a reservation

The replay cache committed before profile authorization and ledger append, in a different SQLite file. A later failure burned the nonce while no durable reservation existed. For sync, the analogous failure would burn a peer message or transfer id while no manifest/commit/transfer state was durable. Replay and the sync mutation ledger must share one authoritative transaction or an explicit recovery protocol.

### 4. Undefined behavior existed in a shared decoder

The Base64url decoder shifted a signed `int` across arbitrarily long input. Because shared codecs will also serve peer/session and manifest paths, parser and cryptographic primitives must be hardened before they protect sync protocol inputs.

### 5. Historical validation sometimes proved self-consistency, not meaning

Rev0618 persisted an empty `contract_digest_sha256` in accepted rows while its chain and tests passed. Rev0631 also left newline-concatenated security tuples ambiguous. For sync, hash chains and counters are not evidence unless they bind the exact file, chunk, peer, folder, tombstone, and conflict semantics they claim to bind.

### 6. Claims outran retention semantics

The prior nonce wording implied uniqueness without a horizon. A sync product must define retention for tombstones, peer message ids, manifest histories, chunk availability, conflict records, and deleted data. Local retained rows are not global sync truth.

### 7. Durability settings and permission changes were requested but not always proven

Rev0644 verified WAL and `synchronous=FULL`, applied busy timeouts and SQLite limits, and failed closed when private permissions could not be established. Future sync file application must be equally explicit about temp paths, fsync, atomic rename, partial chunks, symlinks, and unsafe path handling.

## Corrected missing architecture

### A. Sync-domain model

The cube needs first-class C++ types for device, folder/share, file id, normalized relative path, metadata policy, manifest entry, chunk id/range, tombstone, version lineage, conflict record, and transfer reservation.

### B. Local index and manifest store

A deterministic fixture scanner should safely walk a directory, reject unsafe paths according to policy, chunk files, compute stable hashes, and persist local manifest/index state.

### C. Manifest diff and sync planner

Given local and remote manifests, the engine should produce explicit actions: need chunk, offer chunk, commit file version, apply tombstone, preserve conflict, or no-op.

### D. Authenticated peer session harness

Before real networking, a fake C++ peer harness should exchange device/folder identity, manifest summaries, chunk availability, and transfer requests. Peer identity must be constructed by the session adapter, not request body JSON.

### E. Sync mutation ledger

The existing admission/replay/outbox/relay machinery should be mapped to concrete sync operations. Start with one operation, then prove retry/crash/restart behavior.

### F. Transfer and file-apply protocol

Chunk receipt needs temp-file discipline, partial-state persistence, hash verification, resume, cleanup, fsync, atomic replace, and protection against symlink/path traversal families.

### G. Conflict, deletion, and retention policy

The engine must decide how divergent edits, renames, case-folding collisions, tombstone expiry, restore, peer-offline windows, and metadata differences behave.

### H. Privacy and metadata model

AnonSync may not be anonymous in the strict sense, but it is a sync product and therefore must define what peers learn: file names, sizes, hashes, mtimes, folder ids, device ids, logs, tombstones, and conflict metadata.

## Corrected roadmap

### P0

1. Add sync-domain structs/schemas in C++.
2. Build a deterministic local folder scanner and manifest/chunk index over fixtures.
3. Implement manifest diff planning.
4. Add a fake authenticated peer session for manifest exchange.
5. Bind one concrete sync action to the existing SQLite/WAL reservation ledger.

### P1

1. Add resumable chunk transfer state and safe file application.
2. Define conflict and tombstone retention semantics.
3. Add peer/share trust, invite, revocation, and rotation rules.
4. Add resource limits and telemetry for manifest size, chunk queues, database growth, and transfer concurrency.

### P2

1. Split monolithic C++ files by sync trust domain.
2. Replace Boolean-manifest growth with versioned sync schemas and claim-to-test maps.
3. Rename deterministic fuzz launchers as selftests, then add real coverage-guided fuzzing for peer messages, path normalization, manifests, and chunk tables.
4. Add SBOM, signed provenance, and reproducible/hermetic build instructions.

## Speculation, corrected

- **Likely product shape:** AnonSync should become a small C++ P2P sync daemon/library with deterministic core logic, not a generic authorization sidecar.
- **Likely development failure:** locally provable evidence features were easier to add than file/peer/chunk behavior, so the cube became evidence-rich and sync-poor.
- **Best use of the cloudtainer:** keep revisions compact, but each new security claim must attach to a sync path: peer message, manifest, chunk transfer, file commit, tombstone, or conflict.
- **Naming:** keep AnonSync. The name is the product; the architecture must now earn it.
