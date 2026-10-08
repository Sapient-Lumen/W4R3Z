# File Payload Snapshot Authority Audit — rev0892

## Mission boundary

The sender-side file service must not let caller-controlled executable code run after a durable outbox lease has been minted. The lease is not ordinary data: it owns attempt identity, worker identity, expiry, retry provenance, and the first network-progress cutpoint. Any callback that runs between claim creation and dispatch re-attestation can block indefinitely, re-enter the owner, mutate the live channel, settle or release the claim through another path, or throw after authority has already changed.

The previous API accepted a `std::function` payload source. Runtime tests fenced several hostile callback behaviors, and a later SQLite guard re-attested the claim. That was useful hardening, but it preserved an unnecessarily large trust surface.

## Failed authority sequence

1. Validate the live authenticated channel.
2. Mint a durable outbox claim.
3. Invoke arbitrary caller code to obtain bytes.
4. Try to release the claim if the callback throws.
5. Re-attest the exact claim under a SQLite writer guard.
6. Build the frame.

The guard closed stale-history races, but step 3 still admitted unbounded reentrancy and scheduling while live attempt authority existed. The C++ Core Guidelines CP.22 advises against invoking unknown code while a lock is held because of deadlock and unbounded behavior. An SQLite lease is not literally a C++ mutex, but the same ownership lesson applies more strongly: avoid unknown code while a scarce durable authority is live, even when a later transaction re-proves it.

Primary source: https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#cp22-never-call-unknown-code-while-holding-a-lock-eg-a-callback

## Corrected authority sequence

1. Construct `SyncReplicaFilePayloadSnapshot` before the service call.
2. Move every payload byte into private state.
3. Apply hard cardinality, per-entry byte, aggregate-byte, and platform-addressability budgets.
4. Compute each payload's SHA-256 content identity.
5. Sort by digest, reject duplicate content identities, and compute a domain-separated structural snapshot digest.
6. Validate the live channel and exact folder scope before durable mutation.
7. Construct a bounded `SyncReplicaFileContentInventory` that owns, validates, sorts, and deduplicates the digest set once, then pass that cheap shared-const value into the SQLite claim transaction.
8. Preserve the existing permanent-policy fence: the first ready File operation that exceeds the service's wire or payload policy still blocks before lease mutation.
9. Among policy-compatible operations, claim the first canonical intent whose committed content digest is present in the immutable inventory; absent payloads are skipped without an attempt, worker, lease, retry release, or generation change.
10. Resolve the selected operation by exact content digest and declared size, then return one owned bounded byte copy.
11. On a post-selection size contradiction or copy-allocation failure, exact-release that claim onto local bounded retry timing before propagating the error.
12. Re-attest the exact claim and fresh owned clock under the SQLite writer guard.
13. Perform only reviewed bounded request construction; no payload lookup, caller code, or network I/O runs under the guard.

Unknown code is no longer accepted by the production file-payload API. Copies of the snapshot share `std::shared_ptr<const State>`; the state and entry container are private, so ordinary callers cannot mutate backing bytes after construction. Lookup returns an owned `std::string`, not a borrowed `std::string_view`, so payload bytes cannot outlive their snapshot through a dangling public view. The SQLite owner also no longer accepts a borrowed `span<string_view>` inventory: that first draft left claim selection dependent on caller-managed lifetimes and potentially mutable cross-thread storage. The dedicated inventory value owns its digest strings behind separate `shared_ptr<const State>`, is folder-scoped and hard-capped, and can be copied cheaply across the claim call without repeating full validation.

## Content addressing and its limits

RFC 6920 standardizes ways to identify digital objects with hash outputs and describes checking the binding between a name and returned data. It also makes clear that the hash algorithm and digest value define the content name. AnonSync already commits each canonical file operation to a full lowercase SHA-256 digest and size. The snapshot uses that existing identity for exact local lookup rather than inventing a second payload name.

Primary source: https://www.rfc-editor.org/rfc/rfc6920

FIPS 180-4 specifies SHA-256 as a secure hash algorithm that produces a message digest. The implementation reuses the cube's reviewed SHA-256 primitive. No truncation is used.

Primary source: https://csrc.nist.gov/pubs/fips/180-4/upd1/final

Content identity is not authenticity. The snapshot digest is structural local evidence, not a signature, MAC, membership assertion, or proof of origin. Authentication remains owned by the canonical operation evidence, actor/key policy, and live TLS channel. A hypothetical SHA-256 collision would collapse two payload identities; this revision does not claim formal collision impossibility.

## Availability selection and exact failure ownership

The first callback-retirement draft still claimed in canonical outbox order and only then discovered that a snapshot lacked the selected digest. That unavailable head-of-line object consumed authority before availability was known. That converted ordinary local unavailability into a durable attempt plus exact retry release. With a scheduler that performs only one claim per clock tick, the same absent head-of-line object could repeatedly consume the turn and starve later payloads that were present. This was safe against false delivery but wasteful and liveness-hostile.

rev0892 closes that gap inside the existing `BEGIN IMMEDIATE` claim transaction. The immutable inventory constructor validates and owns lowercase SHA-256 strings, sorts them into strict canonical order, rejects duplicates, and enforces the same 65,536-entry hard ceiling as the payload snapshot before owner authority is approached. The owner then verifies only active state and exact folder scope before acquiring entropy or writer authority, and binary-searches the retained canonical strings only after the candidate passes permanent wire and payload policy. An operation absent from the engaged inventory is not a claim candidate. It receives no attempt number, claim ID, worker identity, deadline, release provenance, or outbox generation. The next canonical available operation may proceed; the causal receiver already has explicit pending-dependency semantics for out-of-order evidence.

The post-claim lookup remains fail-closed. Because selection and lookup use the same immutable snapshot, ordinary absence cannot occur. A committed size that disagrees with the bytes under the selected digest, a hypothetical digest collision, or bounded copy allocation failure can still fail after claim. The service exact-releases that same claim and records local retry provenance. A stale, missing, or already expired claim during that release is a contradiction and is reported rather than silently relabeled as success.

A separate scripted-clock regression proves that a claim can expire after successful snapshot lookup and before guard acquisition. The owner commits the accepted clock evidence, retains the expired exact attempt without fabricated retry-release provenance, and requires a fresh claim ID and attempt number at the deadline.

## Resource and performance audit

The replacement removes callback reentrancy but does not make payload memory free:

- Snapshot construction is O(total bytes + n log n) and owns every byte.
- Each claim transaction binary-searches a canonical immutable digest inventory for each ready policy-compatible candidate; the inventory contains no payload bytes and allocates nothing in the owner. Validation, sorting, deduplication, and digest-string ownership occur once when the inventory is built rather than O(n) again for every retry.
- Each selected request performs one bounded payload copy before acquiring the SQLite writer guard and later moves that copy into the request.
- Aggregate memory remains caller-visible pressure. The default snapshot ceiling is 64 MiB, the default per-payload ceiling is 4 MiB, and the service applies its own tighter wire limit when selecting a claim.
- Reconstructing a snapshot for every attempt would be wasteful. Production callers should retain one immutable snapshot across retries or replace it with a separately reviewed durable content-store snapshot owner.
- The snapshot is process-local and non-durable. A restart still requires reconstruction from a trusted local content store. It does not solve garbage collection, quota fairness, content discovery, or durable cache repair.

The next scalable end state should be a durable, indexed, content-addressed payload store with a value-owned read snapshot or transaction capability. That owner should retain the same no-callback API and exact-release behavior while avoiding whole-working-set memory retention.

## Test and audit refactor

Retiring the callback removed callback-only race injection. Direct owner tests remain responsible for concurrent release, settlement, renewal, trigger mutation, and writer serialization. The service tests now focus on the remaining service-owned frontiers: preclaim channel/scope rejection, immutable source ownership, canonical digest ordering, hard limits, malformed operation rejection, no-attempt selection across an unavailable canonical head, post-selection contradiction release, retry timing, and post-lookup clock expiry. Direct owner tests additionally prove that malformed, duplicate, oversized, moved-from, cross-folder, and non-file-scoped inventories cannot reach claim authority, and that mutating the caller's original digest vector after inventory construction cannot change retained availability.

During this refactor, the old callback test block was found to contain unrelated retry-policy boundary coverage. That coverage had accidentally disappeared. rev0892 restores explicit zero-delay and over-budget constructor tests and verifies that rejection changes no durable sender state.

Four older lexical audits were also corrected. They no longer require retired callback tokens or imply that callback interposition is still a production feature.

## Remaining risks

1. **Allocation failure injection is incomplete.** The post-selection exception path is structurally shared with the compiled size-contradiction release case, but deterministic allocator-fault coverage for the bounded owned payload copy is still absent.
2. **Durable source ownership is missing.** The snapshot is a safe in-memory seam, not the final payload store.
3. **Aggregate budget is not global fairness.** Multiple snapshots can coexist; there is no process-wide, folder-wide, or peer-wide memory governor.
4. **Availability skipping is policy, not terminal rejection.** An absent digest consumes no attempt and permits later available content to proceed, but it does not durably diagnose, dead-letter, expire, or garbage-collect the unavailable intent.
5. **Digest agility is absent.** Canonical operations currently use SHA-256 only. Any future algorithm transition must version operation identity and must not reinterpret old evidence.
6. **Inventory construction still costs O(n log n).** It is paid once per immutable inventory rather than once per claim, but repeatedly rebuilding inventories would remain wasteful.
7. **Lexical audit nonclaim.** Source-order and substring checks cannot prove C++ lifetime semantics, cryptographic security, transaction behavior, exception safety, or runtime progress. Compiler, sanitizer, adversarial runtime, stress, and package verification remain load-bearing.
