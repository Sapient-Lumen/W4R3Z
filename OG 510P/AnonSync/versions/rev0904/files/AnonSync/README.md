# AnonSync rev0904

AnonSync is an **evidence-authorized, crash-consistent, bounded convergence
engine under construction**. Its mission is not ordinary file copying. It turns
exact authorized observations into immutable identity-bearing operations,
preserves them through crashes and pressure, and requires independent replicas
to derive the same active and visible state from equivalent evidence and trust
state.

> Exact history is authority; summaries are acceleration. Projection, counters,
> leases, clocks, retries, receipts, indexes, transport sessions, capabilities,
> filesystem names, and build reports may coordinate or verify work, but none may
> silently acquire more authority than the exact validated evidence and cutpoint
> that created it.

## Rev0904: descriptor-rooted SQLite authority without lock revocation

The selected SQLite path is now carried into one private descriptor-rooted VFS.
Main, rollback-journal, WAL, and SHM names are mediated relative to a retained
deployment directory; anonymous spill, multiply linked family members, named
delete-on-close, VFS substitution, hostile cleanup replacement, and context or
namespace escape fail closed. Every accepted connection proves its exact VFS
object and wrapped live main-file handle before evidence reads or durability
synchronization.

The audit corrected a severe flaw in the first version of that design. It had
retained a second descriptor for the main database inode. Traditional POSIX
record locks are process-associated, and closing any descriptor for the file can
release locks held through SQLite's own descriptor. Rev0904 removes that
auxiliary lifetime. Pre-open inspection for one product authority delegates its
short-lived read to the same bundled Unix VFS before that authority opens its
connection; SQLite can therefore apply its process-wide deferred-close lock
workaround even when another same-inode connection is live. Post-open reads and
syncs use the authority's existing `sqlite3_file` under the connection mutex. A
fork adversary proves a real RESERVED lock survives inspection and VFS teardown.

Mount-namespace identity was also insufficient: a file bind mount can replace a
family member inside the same namespace while preserving `st_dev`. The VFS now
freezes the parent `statx` mount identity and requires each existing family
member to remain on that mount using an allocation-free observer that opens no
lock-bearing inode. The cloudtainer exercised an actual same-namespace bind
mount over the WAL name; VFS access/open rejected it and preserved the foreign
bytes. A second witness bind-mounted the approved main inode onto its own name,
preserving device, inode, and bytes while changing only mount identity; the
public namespace proof rejected that subtler substitution too.

Focused checks pass 25/25 and 90/90; source audits pass 61/61 and 34/34.
Clean GCC 14 and Clang 17 Debug registries each pass 221/221, the focused
ASan/UBSan lane passes 2/2, and a Clang-discovered readiness-publication race in
an inherited-process test now passes 64/64 parallel stress runs. This is still
not hostile-root proof, cross-store atomicity, or a complete
synchronization/anonymity product. See
`SQLITE_DESCRIPTOR_ROOTED_LOCK_AND_MOUNT_FAMILY_AUTHORITY_AUDIT_rev0904.md` and
`REVISION_NOTES_rev0904.md`.

## Rev0901: complete SQLite genesis images and identity-first recovery admission

SQLite store birth no longer exposes an empty or partially initialized selected
main-file pathname. Each role is now created as a private, filename-free,
schema-empty in-memory database; exact deployment binding and complete role
genesis are committed there first. SQLite's serialized main image is then
captured, bounded, sealed, and published at the selected pathname with immutable
create-new/no-replace semantics. The published image is re-opened as an exact
bound bootstrap candidate, reconciled to file-and-parent durability, promoted
from its self-contained rollback image to the operational WAL profile, and
re-attested before use.

`init-resume` now classifies present SQLite candidates before ordinary role
ownership. A rollback-mode image must be a complete SQLite main file with no
`-journal`, `-wal`, or `-shm` sidecar; a WAL candidate may retain its WAL family
but may not carry a rollback journal. Every present store proves exact
record-selected deployment identity on retained handles before any candidate is
promoted, any role state is inspected, or any missing store is created. The
process corpus covers twelve crash/recomposition scenarios, including sealed
rollback-image recovery, contaminated sidecar refusal, and rejection of an
unbound but otherwise valid SQLite main file.

The audit also narrowed detached TLS membership owners to genesis construction:
anonymous images cannot publish membership policy or advance the trusted
anchor. The detached deployment-binding primitive itself now requires a
writable, schema-empty database using MEMORY journaling; an empty SQLite
filename alone is insufficient because anonymous disk-backed temporary
databases also have no exposed filename. A redundant five-second busy timeout
was removed from the private single-connection genesis path.

The clean GCC 14 Debug registry passes **221/221**, the deployment-binding audit
passes **26/26**, and a separate focused ASan/UBSan lane passes **4/4**. The
largest remaining local-authority gap is a descriptor-rooted capability that
binds preflight, open, SQLite sidecars, and owner lifetime to one live deployment
directory; hostile directory-entry replacement remains outside the current
proof. Separate WAL databases are still not atomic as a set, and the bundled
SQLite 3.53.3 should be advanced to the 3.53.4 patch release in an isolated,
fully revalidated dependency revision. See
`ATOMIC_SQLITE_GENESIS_IMAGE_AND_RECOVERY_ADMISSION_AUDIT_rev0901.md` and
`REVISION_NOTES_rev0901.md`.

## Rev0900: durable bootstrap record and exact idempotent resume

Initialization now has explicit authority before the final deployment manifest
exists. Fresh `init` publishes a deterministic hidden bootstrap record before
mutating any selected store. Its payload is the byte-exact canonical future
manifest, still self-bound to the exact final manifest path and existing
self-digest. Record reads are bounded, no-symlink, namespace-checked, and
reconciled to exact file-and-parent durability before they can authorize work.

`init-resume --manifest ABSOLUTE_JSON` uses only that record-selected deployment.
It identity-attests every present store before role-state inspection or missing
creation, and it can fill a partial set only while every present resource and
the files root remain at bootstrap genesis. A complete advanced deployment can
regain a lost final manifest; an advanced partial set cannot be recomposed.
Once the final manifest exists, resume is deliberately identity-only: it refuses
missing stores and cannot initialize schema or reconcile membership under the
name of idempotence.

The audit also corrected an initially weak restart boundary: a visible record or
final manifest after an indeterminate parent-directory sync is now accepted only
after immutable-file reconciliation proves exact bytes and directory durability.
Source audits were refactored around the shared authority frontier, and a stale
bounded-reader allowlist failure was retained as intermediate evidence. The
clean GCC 14 Debug registry passes 221/221, a focused authority lane passes
12/12, nine adversarial resume scenarios pass, and a separate ASan/UBSan focused
lane passes.

The largest remaining bootstrap defect is precise: SQLite main-file birth and
deployment binding are not one durable publication, so a crash between them can
strand an unbound main file. Descriptor-rooted deployment authority,
cross-resource coordination, a forensic bootstrap inspector/quarantine flow,
and the broader supervisor/synchronization/privacy product remain open. See
`CRASH_RECOVERABLE_BOOTSTRAP_RECORD_AND_IDEMPOTENT_RESUME_AUDIT_rev0900.md` and
`REVISION_NOTES_rev0900.md`.

## Rev0899: store-attested common birth and fresh-only bootstrap

The product manifest is no longer the sole witness that a store set belongs
together. Fresh bootstrap now mints a checked 256-bit deployment ID, computes
the exact canonical manifest digest before store creation, and persists that
same identity inside every selected SQLite role and the product payload lease
anchor. A canonical manifest over independently valid stores is therefore not a
committed deployment.

The deployment manifest is version 2 and commits role-specific SQLite
application IDs, required store-internal binding, and fresh-only adoption. Every
SQLite database carries an exact STRICT singleton binding row for deployment,
manifest, role, database path, folder, local actor, application ID, and a
length-framed digest. Replica, file-effect, TLS-membership, and membership-anchor
databases also have distinct header-level application-ID fences. Every normal
open proves the exact opened filename, header, schema, temporary-shadow absence,
singleton row, fields, and digest before constructing the role owner.

Init now preflights the complete selected namespace before its first mutation:
manifest, database main files, and `-journal`/`-wal`/`-shm` sidecars must be
absent, while payload and delivery roots must be empty. The product payload root
uses a v3 identity marker binding deployment ID, manifest digest/path, folder,
actor, and lease protocol; product bootstrap refuses to legitimize pre-existing
payload bytes. This intentionally fails closed rather than adopting rev0898
stores.

The process proof independently recomputes manifest and binding digests and now
covers canonical manifest forgery, same-role and cross-role database swaps,
foreign payload-root substitution, orphan sidecars, and pre-seeded roots, in
addition to clock recovery and real mutual-TLS file delivery/settlement. The
new deployment-binding audit passes 20/20; database-open, bootstrap, and payload
source audits pass 16/16, 19/19, and 33/33. The complete GCC 14 Debug registry
passes 219/219.

Interrupted init can still leave correctly bound but uncommitted resources and
has no inspect/resume/quarantine workflow. Freshness preflight has races against
noncooperating writers, WAL is not atomic across the separate databases, the
unkeyed binding does not resist a hostile local writer, path authority is not
fully descriptor-rooted, and status is not a forensic read-only export. The
product still lacks a bounded supervisor, causal filesystem semantics,
chunking/resume, GC/indexing, at-rest encryption, and an anonymity threat model.
The full audit and primary-source research are in
`STORE_SET_BIRTH_ATTESTATION_AND_FRESH_BOOTSTRAP_AUDIT_rev0899.md`; exact changes
and nonclaims are in `REVISION_NOTES_rev0899.md`.

## Rev0898: explicit store-set bootstrap and manifest-bound operation

The product spine now has one named bootstrap authority. `anonsync_replica
init` validates a complete store set, prepares an immutable deployment-manifest
name, initializes the selected replica, payload, effect, membership, and anchor
owners, and publishes the manifest last. Every normal command requires that
manifest and derives all local paths, folder identity, actor identity, and
payload ceiling from its exact canonical bytes. Raw store-path and local-identity
options can no longer be mixed into status, clock, enqueue, membership, send, or
serve operations.

The manifest has a bounded exact schema, a domain-separated SHA-256 self-digest,
opened-path binding, strict UTF-8 and duplicate-key rejection, exact field and
policy closure, and byte-for-byte canonical re-encoding. Its writer proves both
the 16 KiB read ceiling and its own strict-JSON/UTF-8 contract before any store
is created. Copied, tampered, noncanonical, policy-incompatible, or path-mixed
configuration therefore fails before store access. The manifest is a
last-published operational commit marker and explicitly does not claim that the
individually durable resources form one cross-resource transaction.

Operational SQLite and payload opens are now uniformly existing-only. The
payload store has an explicit, non-defaulted open disposition, so status,
enqueue, and send cannot mint a folder identity marker by pointing at an empty
directory. Only `init` retains creation authority. Every command result names
the exact deployment-manifest digest.

The strict JSON parser was extracted into a small shared leaf so the manifest
and broad runtime codec use one parser without pulling the runtime monolith into
a narrow authority boundary. The process proof now covers bootstrap collision,
path overlap, copied and tampered manifests, detached stores, empty replacement
payload roots, profile mismatches, clock recovery, real mutual TLS, exact file
publication, receipt, and settlement. The complete GCC 14 Debug registry passes
217/217.

The manifest still binds configuration more strongly than common birth. Stores
do not yet persist one shared deployment identifier, and interrupted `init`
needs inspect/resume/quarantine semantics. Ancestor symlink and mount rebinding,
write-capable WAL status observation, a bounded supervisor, causal filesystem
semantics, GC/indexing, at-rest encryption, and a real anonymity threat model
remain open. The full assessment and primary-source research are in
`EXPLICIT_STORE_SET_BOOTSTRAP_AND_MANIFEST_AUTHORITY_AUDIT_rev0898.md`; exact
changes and nonclaims are in `REVISION_NOTES_rev0898.md`.

## Rev0897: explicit clock recovery and fail-closed database targeting

The product spine can now inspect and recover its owned outbox clock without
claiming delivery work. `clock-observe` samples under the replica SQLite
writer lock and publishes only the exact clock cutpoint; a newly detected
rollback, source change, boot change, namespace change, synchronization gap, or
drift violation is returned as durable quarantine state rather than being
hidden behind a work-path exception. `clock-recover` requires the exact current
observation generation and binds one fresh owned observation as the new anchor.
The same exact-CAS update and staged re-attestation path is shared with lease
operations, so the CLI does not mint a second recovery authority.

The database-open boundary was also corrected. Observation, recovery, status,
and send operations no longer carry implicit `SQLITE_OPEN_CREATE`; a mistyped
path fails without creating a main file, WAL, or shared-memory sidecar. File
existence is not treated as authority either: an existing zero-byte placeholder
is refused instead of being initialized, and an existing-only open verifies
that the persistent journal profile is already WAL rather than silently
rewriting a wrong SQLite target before exact schema attestation. SQLite usually
returns a diagnostic connection handle even when open fails, so the product now
keeps that handle in a distinct exception-safe candidate owner, closes it on
every rejection path, proves the successful connection is writable, and only
then adopts it. This removes a severe unwind path in which a failed open could
be misread as a live owned transaction and trigger the process fail-stop
instead of the intended diagnostic exit.

`serve-one` now proves its TLS identity, listener, and both existing membership
authorities before it may create receiver replica or effect stores. The process
proof covers typo/no-create behavior, refusal of pre-existing empty genesis,
byte-preserving rejection of an unrelated DELETE-mode SQLite target through
both observation and bootstrap-capable paths, prevention of the paired-store
creation on that failure, normal failed-open exit, preflight without orphan
bootstrap, healthy clock publication, durable source-change quarantine,
generation-fenced recovery, repeated-recovery rejection, real mutual TLS
delivery, exact receiver publication, and terminal sender settlement. A new
source audit pins every product database call site's explicit creation and
persistent-profile policy.

The largest remaining product gap is still a bounded durable supervisor loop,
but rev0897 changes what that loop can safely build upon: it can distinguish a
clock block from empty work and can invoke an exact recovery transition instead
of relying on manual SQL or process replacement. Bootstrap is not yet a single
atomic store-set operation; `enqueue-file`, `membership-publish`, and receiver
genesis still retain explicit-in-code creation capability. A future `init`
command should make that authority operator-explicit and bind the related store
identities in one durable deployment manifest.

## Rev0896: attested product status surface

The bounded product executable now has a `status` command. It opens the same
owning surfaces as `enqueue-file`, `send-one`, `serve-one`, and
`membership-publish`, restores durable state through those owners, and emits a
flat JSON condition report for the operator-facing cutpoints: causal evidence,
active and visible operations, outbox lease/clock state, retained payloads,
receiver file effects, and anchored TLS membership.

The process proof now observes the sender before delivery, the sender after the
receipt settles, and the receiver after publication. This closes a product gap
without creating a daemon: a one-shot spine can now report whether work is
queued, whether the outbox is settled, whether payload bytes remain retained,
and whether receiver effect and membership anchors agree. The audit/refactor in
`src/anonsync_replica.cpp` keeps status subordinate to durable owners rather
than adding raw schema queries, and factors paired-option validation plus status
summaries into narrow helpers.

This remains a bounded one-command-at-a-time product surface. It does not yet
implement a durable scheduler, peer discovery, causal directories, tombstones,
renames, reachability/GC, chunking, at-rest encryption, or anonymity.

## Rev0895: first bounded product spine

The newer causal replica owners are now invokable without linking the diagnostic
self-test implementation corpus. `anonsync_replica` exposes bounded one-shot
commands to derive a certificate SPKI, publish anchored membership, enqueue a
durable file operation, send one authenticated delivery, or serve one
authenticated delivery. The production sender proves durable payload
availability, completes numeric-address connect and mutual TLS 1.3, verifies the
expected SPKI/actor, and only then may claim SQLite work. Once the guarded
request-prefix frontier is crossed, transport uncertainty leaves the claim live
and ambiguous; only the exact authenticated receipt can settle it.

A registered process test invokes separate sender and receiver processes with
independent databases, durable payload storage, anchored membership, real TCP,
mutual TLS, receiver filesystem publication, and terminal receipt settlement.
It found and corrected fresh-membership bootstrap, request-frame-ceiling, and
container clock-authority composition defects that library-only tests had not
exposed.

`send-one` uses the fail-closed system clock by default. The paired
`--operator-clock-authority-id` and `--operator-clock-uncertainty-ns` options
are an explicit deployment assertion for containers where clock discipline is
owned externally but hidden from the process; they are not measurement or
attestation. Destination parent directories must already exist because causal
directory/tombstone/rename semantics are not yet implemented.

This remains a one-conversation spine, not a daemon. It does not claim
continuous scheduling, discovery, GC/indexing, at-rest encryption, anonymity,
unlinkability, private-interest overlap, endpoint hiding, or traffic-analysis
resistance. The full mission/gap analysis is in
`MISSION_PRODUCT_SPINE_ASSESSMENT_rev0895.md`; sender cutpoints and nonclaims are
in `PRODUCT_SPINE_TLS_CLIENT_AUDIT_rev0895.md`; exact changes are in
`REVISION_NOTES_rev0895.md`.

## Rev0892: independently anchored membership and owned payload availability

Rev0891 made TLS membership an append-only SQLite authority and accepted an
optional caller-retained chain anchor. That still left the rollback witness as
free input to the same API that served membership, without executable crash
ordering or a separately owned persistence path. Rev0892 adds a second SQLite
owner and a coordinator with an explicit two-commit protocol: membership commits
first, no resulting capability escapes, and the independent anchor store must
cover that exact generation/digest cutpoint before a move-only accepted-session
authority can be emitted. Restart reconciliation closes the intentional crash
gap; exact compare-and-swap, append-only transition history, whole-history
reconstruction, and final current-state reproof prevent a stale capability from
being knowingly returned after a concurrent publisher wins.

The accepted TLS server now requires the anchored capability type. Every
terminal result binds the exact membership generation and chain plus the durable
anchor generation, transition sequence, and transition digest. Composition
rejects identical database names and distinct names that resolve to the same
filesystem object, including hard-link aliases. This is a useful accidental-
misconfiguration fence, not proof of separate media or administration. Joint
rollback of both stores, malicious same-process mutation, signed enrollment,
hardware monotonicity, and live revocation remain unclaimed.

Rev0892 also retires the last production outbound file-payload callback.
`SyncReplicaFilePayloadSnapshot` owns bounded content-addressed bytes behind
immutable shared state. A separate `SyncReplicaFileContentInventory` owns,
validates, sorts, deduplicates, and folder-scopes only the available digests.
The SQLite owner receives that value, never borrowed caller views, and selects
the first policy-compatible outbox intent whose content is present inside the
same `BEGIN IMMEDIATE` claim transaction. Missing content is skipped without
creating an attempt, claim ID, lease, retry release, or generation change, so an
unavailable canonical head cannot repeatedly consume claim authority and starve
later available payloads. Post-selection contradictions exact-release the same
claim before failure propagates.

The durable TLS-policy connection/backend implementation was also extracted into
one shared profile used by membership and anchor owners. This removes duplicated
SQLite authority policy while retaining complete schema, exact serialized-handle
generation, transaction, journal, and synchronous-mode re-attestation. Both
owners retain the cube's shared `SqlitePathFamilyGuard`, so ordinary live
main-file rename/replacement, symlink-family drift, and SQLite-reported movement
fail closed before policy authority is returned. This is live process-local
namespace evidence, not storage-media or reboot provenance.

Detailed invariants, failure matrices, research, resource analysis, and
nonclaims are in `TLS_DURABLE_MEMBERSHIP_ANCHOR_AUDIT_rev0892.md`,
`FILE_PAYLOAD_SNAPSHOT_AUTHORITY_AUDIT_rev0892.md`, and
`REVISION_NOTES_rev0892.md`.

## Rev0891: durable membership history and retained TLS context

Rev0890 made post-handshake membership a pure lookup in a canonical immutable
snapshot, but the snapshot itself remained freely constructible configuration.
Rev0891 adds the missing durable source: an append-only SQLite owner binds one
folder/local actor, reconstructs every retained generation, requires exact
compare-and-swap publication under `BEGIN IMMEDIATE`, and emits a move-only
accepted-session capability only from committed state. Every TLS terminal result
now names the exact generation, snapshot digest, prior chain digest, and current
chain digest.

A separately retained `(generation, chain_digest)` anchor detects whole-database
rollback or a fork through that point. The internal chain is deliberately
unkeyed and no external anchor store is claimed. The owner is a complete
O(history + retained entries) correctness oracle, not yet the scalable
production reader.

The database boundary was tightened during audit. Exact schema closure catches
arbitrary-named indexes/triggers attached to authority tables and connection-
local TEMP triggers. A dedicated connection profile disables unsafe schema
execution, extensions, attachments, dirty reads, and ignored CHECK constraints,
and is re-attested inside every transaction. WAL requires `FULL`; rollback
journals require `EXTRA`, without overclaiming the underlying VFS or hardware.

The review also found and fixed a severe ceiling edge: the crossing append could
previously commit beyond a restoration hard limit and brick all later reads.
Admission is now checked against exact retained totals before insertion. Return-
authority allocation also occurs before commit, so allocation failure rolls the
candidate policy back.

The accepted server no longer borrows a raw `SSL_CTX*`. A move-only wrapper
retains the OpenSSL reference with `SSL_CTX_up_ref`/`SSL_CTX_free`; lifetime is
owned while concurrent context mutation remains explicitly unsupported.

Detailed invariants, failure matrices, research, and nonclaims are in
`TLS_DURABLE_MEMBERSHIP_AUTHORITY_AUDIT_rev0891.md`,
`TLS_SERVER_CONTEXT_RETENTION_AUDIT_rev0891.md`, and
`REVISION_NOTES_rev0891.md`.

## Rev0890: immutable membership authority at the live TLS frontier

Rev0889 completed the first accepted TCP/mutual-TLS/file-delivery session but
left the final certificate-key-to-actor decision in a caller-supplied
`std::function`. That callback ran after cryptographic authentication while the
accepted descriptor and `SSL` object were live, immediately before application
authority was minted. A comment requiring stable backing state could not make
arbitrary callback code pure, bounded, or non-reentrant.

Rev0890 replaces that seam with `SyncReplicaTlsMembershipSnapshot`: a validated,
canonical, immutable value for one folder, local actor, positive policy epoch,
and complete exact SPKI-to-actor set. It sorts and deduplicates pins, permits
explicit multi-pin rotation overlap, rejects receiver-device reflection, caps
entry count, and binds the complete set to a domain-separated digest. The server
takes the snapshot by value, checks its service identity before `accept4`, uses
pure exact lookup after verified SPKI derivation, re-proves the accepted socket
before channel construction, and records policy epoch/count/digest in every
terminal result.

Real TLS tests now cover canonical digesting, malformed and duplicate policy,
moved-from misuse, cross-folder/cross-actor pre-accept rejection, valid-certificate
unknown-member rejection, and complete publication/receipt/settlement under the
exact snapshot. Two source audits guard the immutable composition and inventory
every remaining explicit callback boundary. OpenSSL trust callbacks remain part
of the caller-owned handshake configuration; the removed callback is the
separate AnonSync post-handshake membership decision.

The deep analyses are in
`TLS_IMMUTABLE_MEMBERSHIP_SNAPSHOT_AUDIT_rev0890.md` and
`CALLBACK_AUTHORITY_BOUNDARY_AUDIT_rev0890.md`. The next required authority is a
durable, provenance-checked, anti-rollback membership configuration owner that
publishes these snapshots only after commit. Revision scope and nonclaims are in
`REVISION_NOTES_rev0890.md`.

## Rev0889: pre-byte accepted TLS authority and exclusive one-run receiver

Rev0888 completed exact nonblocking request/receipt framing once a caller had
already supplied an authenticated `SSL*`. Two authority gaps remained on either
side of that correctness island. The receiver could consume a complete
application frame before discovering that its selected service had no file-
effect role, and successful one-conversation exchange left the local channel
capability reusable. Outside the exchange, no production C++ owner proved the
listener, atomically accepted a child, bounded the mutual-TLS handshake, or
mapped a verified certificate key to an authorized actor epoch.

Rev0889 closes both seams. `preflight_inbound_channel_or_throw` revalidates the
exact live authenticated channel and receiver effect role before the first
application byte is reserved. The service repeats that preflight at the complete-
frame durable frontier; early admission never becomes a lease over later SQLite
or filesystem authority. `SyncReplicaFileTlsReceiverSession` then freezes exact
request/receipt cutpoints and owns one channel through one run. Move, success,
timeout, peer close, exception, explicit discard, destruction, and replacement
all leave exactly one truthful owner and terminalize the local application
capability. A real TLS fixture queues ciphertext and proves invalid receiver
configuration consumes zero bytes, mutates no durable cutpoint, and emits no
response.

The outer `serve_one_sync_replica_file_delivery_tls_session_or_throw` owner starts
from a move-only capability for one exact Linux listening socket lifetime. It
uses `accept4(SOCK_NONBLOCK | SOCK_CLOEXEC)`, owns the accepted descriptor and
`SSL` object, drives a bounded nonblocking TLS 1.3 mutual-authentication
handshake, derives the verified peer SPKI, requires explicit SPKI-to-actor-epoch
membership, constructs the authenticated channel, and transfers it into exactly
one receiver session. Accept expiry, a silent peer, plaintext on the TLS port,
and a certificate-valid but unmapped peer all terminate before durable receiver
authority. The complete loopback path composes real TCP accept, mutual TLS,
membership, canonical request, SQLite evidence/effect ownership, atomic file
publication, exact receipt, sender settlement, and canonical digest convergence.

Socket policy was refactored rather than duplicated. `FD_CLOEXEC` is a separately
re-proved mutable policy in the generic socket-lifetime leaf, and one absolute-
deadline `poll` owner is shared by accept, handshake, and shutdown. Post-mint
`O_NONBLOCK`/`FD_CLOEXEC` mutation fails before accept. A moved-from listener is
ordinary local misuse and throws before process fail-stop, while an active
capability inherited across a process boundary still fail-stops. Poll wakeups
remain advisory; only the subsequent exact kernel/OpenSSL operation classifies
progress, close, or error.

Transport shutdown remains subordinate to application settlement. Only a
complete local receipt permits the accepted owner to attempt bounded
`close_notify`; timeout or failure cannot erase `ReceiptSent`, and transport
closure never claims that the sender received or durably applied the receipt.
The inner session still does not own raw transport; the outer accepted-session
owner supplies that lifecycle explicitly.

The detailed ownership and failure analyses are in
`TLS_RECEIVER_SESSION_OWNERSHIP_AUDIT_rev0889.md` and
`TLS_ACCEPTED_SESSION_AUTHORITY_AUDIT_rev0889.md`. A separate deep audit found a
major remaining liveness gap: staged and published payloads permanently consume
finite admission budgets, and enough enrolled identities or normal long-lived
churn can still exhaust the folder. The safe reservation/fairness/reclamation
design is in `RECEIVER_STAGING_FAIRNESS_AUDIT_rev0889.md`.

Rev0889 completes a narrow durable isolation slice rather than only telemetry.
Exact schema v3 re-derives and binds actor/device usage, persists per-device
count/byte policy across actor epochs, deterministically applies folder then
device limits, migrates exact v2 under one rollback-tested SQLite transaction,
and keeps device-specific diagnostics receiver-local behind the generic wire
capacity receipt. The review also removes redundant full-payload/canonical and
O(history) public-projection copies from internal mutation paths. See
`FILE_EFFECT_CAPACITY_ACCOUNTING_AUDIT_rev0889.md` and
`FILE_EFFECT_DEVICE_ISOLATION_MIGRATION_AUDIT_rev0889.md`. This does not create a
stable membership principal, total disk quota, fair scheduler, pre-transfer
reservation, or reclamation authority. Revision scope and nonclaims are in
`REVISION_NOTES_rev0889.md`.

## Rev0888: exact first-prefix backpressure and one write state machine

Rev0887 added a receiver-owned conversation from complete authenticated request
through durable idempotent file publication and terminal receipt. One important
transport asymmetry remained: the receipt body was resumable, but its encrypted
8-byte record-length prefix was synchronously driven inside the begin factory.
A genuine nonblocking WANT at that first operation was fail-closed, yet it became
an exception rather than exact typed state.

Rev0888 unifies prefix and body in one heap-stable, move-only
`SyncReplicaTlsRecordWriteContinuation`. The new preparation factory validates
bounds, freezes exact prefix/body bytes, reserves the authenticated stream, and
returns before any `SSL_write_ex`. Each advance performs at most one 64 KiB
operation, retains exact arguments across WANT, accepts partial-write progress,
and exposes prefix completion before any hidden body operation. An untouched
prepared owner releases cleanly; abandonment after any attempted operation,
including a zero-byte WANT, poisons the stream.

The sender's guarded dispatch API remains compatible: it drives only through the
complete prefix while SQLite claim authority is held, commits that cutpoint, and
releases before body backpressure. The receiver uses the pre-prefix owner after
its durable effect decision, so first-prefix WANT is now retained through the
shared absolute-deadline poll loop without holding SQLite authority.

Receiver diagnostics now distinguish no attempted write, attempted zero-byte
prefix WANT, partial prefix, accepted prefix, partial body, and complete local
receipt. A real TLS test saturates the response path after durable publication,
forces first-prefix `WANT_WRITE`, expires the receipt deadline with zero accepted
prefix/body bytes, preserves exactly one visible effect, leaves the sender claim
live, and makes the old application stream unusable.

The retired synchronous prefix helper and stale body-only lexical assumptions
were removed. Exact invariants, failure matrix, OpenSSL retry constraints,
rejected alternatives, and nonclaims are in
`TLS_PREFIX_WRITE_CONTINUATION_AUDIT_rev0888.md`.

The first complete suite also exposed a separate validation race: the SQLite
connection-authority retirement probe could publish ticket one before its worker
started, copy that already-published value into `atomic::wait`, and block until
the external timeout. The worker now advances from completed tickets, and a
deterministic pre-start-ticket regression exercises the former deadlock schedule.
That audit is in
`SQLITE_CONNECTION_AUTHORITY_TEST_SYNCHRONIZATION_AUDIT_rev0888.md`; revision
scope and remaining production gaps are in `REVISION_NOTES_rev0888.md`.

## Rev0887: receiver-owned request, durable effect, and receipt cutpoints

Rev0887 introduced one strict-nonblocking receiver composition owner. It reads a
complete bounded authenticated request, invokes the file-delivery service only
at the complete-frame frontier, preserves the durable idempotent decision, then
re-attests the live channel and emits the exact receipt under an independent
absolute deadline. Malformed requests, abandoned responses, and post-effect
failures destructively discard the application stream rather than allowing the
next record to inherit ambiguous conversation state.

It also froze the exact OpenSSL record-I/O policy observed at authentication so
later option, mode, read-ahead, verification, quiet-shutdown, or shutdown-state
mutation cannot borrow old peer/exporter authority. See
`TLS_RECEIVER_EXCHANGE_CUTPOINT_AUDIT_rev0887.md`,
`TLS_RECORD_IO_POLICY_AUTHORITY_AUDIT_rev0887.md`, and
`REVISION_NOTES_rev0887.md`.

## Rev0886: authentication-time transport anchor and exact resumable writer

Rev0885 proved the exact Linux socket lifetime only when strict record I/O
began. The authenticated `SSL*` itself remained mutable: a caller retaining the
raw handle could replace its BIOs after authentication and let the new
transport inherit peer-SPKI/exporter authority from the old channel. Retaining
only a descriptor proof also missed in-place `BIO_set_fd` mutation.

Rev0886 makes the authentication-time transport part of the channel capability.
The shared state retains both exact read/write BIO objects with `BIO_up_ref` and,
for direct Linux socket BIOs, directional `SOCK_STREAM` lifetime identities.
Every later channel-authority use rechecks BIO pointer, in-place descriptor, and
kernel socket lifetime before trusting session, record, poll-target, delivery-
service, or durable-owner authority.

Retained BIOs are released with `BIO_free_all`, not head-only `BIO_free`. This
matters for the supported caller-managed path where the exact top BIO can own a
filter chain; the final anchor release now destroys the complete detached chain
instead of leaking downstream BIOs. A counted filter-over-socket fixture proves
both objects survive SSL replacement while retained and are later freed exactly
once.

The generic socket leaf is refactored into immutable
`SyncSocketLifetimeIdentity`. `O_NONBLOCK` is mutable readiness policy, not
object identity. Strict mode uses a lifetime–`F_GETFL`–lifetime sandwich; a
blocking direct socket rejected before I/O does not poison caller-managed reuse,
while policy loss after framing progress or pending WANT poisons.

Rev0886 also adds an exact incremental write continuation at the accepted-prefix frontier. The parent continuation kept
only a length promise and accepted caller-owned body bytes later, so a different
same-length frame could cross the durable prefix/body cutpoint. It also poisoned
a healthy nonblocking stream on routine `SSL_ERROR_WANT_READ` or
`SSL_ERROR_WANT_WRITE` because no exact retry capability existed.

`SyncReplicaTlsRecordWriteContinuation` now owns the exact bounded frame in one
heap-stable private state before the prefix can succeed. Each
`advance_or_throw()` issues at most one 64 KiB body request, retains the exact
pointer and length across WANT, exposes a typed advisory readiness target in
strict mode, accepts successful partial-write progress, and releases the
exclusive Write reservation only after the complete body succeeds. Moving the
wrapper cannot relocate pending storage; abandoning it after prefix acceptance
poisons the stream. The one-shot writer and file-dispatch path delegate to this
single state machine.

The compiled TLS 1.3 matrix forces `SSL_set_fd`, in-place `BIO_set_fd`, socket
close/`dup2` ABA, lost `O_NONBLOCK`, same-length caller mutation, pre-WANT and
caller-managed target queries, and two-megabyte nonblocking backpressure through
WANT, wrapper move, bounded resume, and exact peer-byte completion.

The revision now also owns the wait between exact WANT frontiers. One shared
`anonsync_sync_replica_tls_poll` leaf composes both read and write continuations
with an absolute `steady_clock` deadline, target reproof after `EINTR`/`EAGAIN`,
upward-rounded bounded `poll(2)`, a post-wakeup cutpoint check, and at most one
OpenSSL operation per wakeup. `POLLERR`, `POLLHUP`, and `POLLNVAL` remain advisory;
OpenSSL and the continuation own close, truncation, retry, and poison semantics.
A real TLS matrix proves deadline retention, prefix/body separation, clean close,
signal interruption, saturated write retry, bounded write-poll progress, and exact
two-megabyte peer bytes.

The release verifier was also corrected at its own authority boundary. It now
rejects actual `build/`, `build-*`, and `cmake-build-*` directory components while
allowing legitimate evidence basenames such as `build-shape-observation.json`.
An executable CTest policy matrix prevents recurrence of both the false rejection
and the previously accepted real build tree.

This still does not authorize concurrent raw SSL/BIO/fd mutation, prove hidden
transport inside custom/filter BIOs, provide strict non-Linux lifetime evidence,
turn local TLS write completion into peer receipt, or supply the missing bounded
receiver/event-loop/effect owner. Exact final build, sanitizer, stress, audit,
lineage, and package evidence is under `REVISION_EVIDENCE/rev0886/`.

Primary-source constraints, state machines, failure matrices, rejected
alternatives, and deliberate nonclaims:

- `TLS_TRANSPORT_ANCHOR_AUTHORITY_AUDIT_rev0886.md`
- `TLS_INCREMENTAL_WRITE_AUDIT_rev0886.md`
- `TLS_DUPLEX_POLL_AUTHORITY_AUDIT_rev0886.md`

`CLOUDTAINER_BUILD_RETENTION_AUDIT_rev0886.md` records the build-tree
retention failure that exhausted the cloudtainer, the conservative cleanup
boundary, and the quota/expiry policy needed to keep validation viable.

## Rev0885: exact socket-lifetime authority at TLS readiness frontiers

A file-descriptor number is a reusable table slot, not the identity of the
kernel socket that an authenticated TLS session was established over. Rev0884
rechecked that strict TLS BIO descriptors still named nonblocking sockets, but
a close followed by `dup2()` could replace the occupant with another
nonblocking stream socket at the same integer. The old check would pass while a
pending `SSL_read_ex()` retry or a post-prefix body write crossed onto the wrong
transport lifetime.

Rev0885 adds an OpenSSL-independent, opaque
`SyncSocketReadinessIdentity`. On Linux it binds the descriptor number, socket
type, `fstat` device/inode/mode, and a mandatory nonzero `SO_COOKIE`; observation
double-checks stat identity and cookie across the capability capture. Exact
reproof rejects closure, descriptor reuse, object substitution, loss of
`O_NONBLOCK`, non-sockets, and unavailable evidence. Unsupported platforms fail
closed rather than silently accepting a weaker tuple. Only the advisory
descriptor is public, so callers cannot compare a convenient subset or promote
process-local kernel evidence into protocol identity.

The authenticated TLS state now owns one readiness proof beside its exclusive
`Idle/Read/Write` record reservation. A pending WANT retry performs system-call
reproof only, preserving the exact OpenSSL retry frontier. A fresh read step
revalidates the peer/session binding and recaptures the current BIO/socket proof.
The strict writer performs the same live recapture between accepted prefix and
body. `pending_readiness_or_throw()` returns a typed readable/writable poll
target only after WANT, re-proves before disclosure, and the later retry proves
again. A stale target makes the pending operation impossible to resume and
poisons the stream.

The read continuation also caps each public body request at 64 KiB. This bounds
application-requested progress per event-loop step without claiming a bound on
OpenSSL internals or wall-clock time. The socket proof was refactored into its
own small library and runtime test rather than leaving Linux syscalls duplicated
inside the OpenSSL adapter.

The final compiled matrix includes exact descriptor-reuse rejection after WANT,
at poll-target lookup, after successful prefix/body progress, and between the
writer's accepted prefix and body. It also retains the existing TLS 1.3 pin,
exporter, process/thread affinity, stable-buffer retry, close, truncation,
duplex-reservation, and file-dispatch cases. Exact build, test, stress,
sanitizer, audit, projection, lineage, and package evidence is under
`REVISION_EVIDENCE/rev0885/`.

This is still not the production receiver. Raw descriptor mutation must be
serialized by a higher-level owner; `SO_COOKIE` is process-local kernel evidence,
not a cryptographic credential. There is no poll/epoll service, resumable
write-WANT state machine, authenticated accept/connect owner, durable
receive/effect composition in `anonsync_core`, terminal effect receipt,
exactly-once remote execution, or implemented anonymity property. The next
useful slice is one bounded event-loop owner carrying a canonical operation
through receiver SQLite admission, atomic visible effect, authenticated
terminal receipt, and sender settlement.

Primary-source constraints, failure matrix, refactor rationale, adversarial
cases, and deliberate nonclaims: `TLS_SOCKET_LIFETIME_AUTHORITY_AUDIT_rev0885.md`.

## Rev0884: heap-stable incremental TLS receive and duplex ownership

A nonblocking TLS read is not stateless merely because no application byte was
returned. OpenSSL can report `SSL_ERROR_WANT_READ` or `SSL_ERROR_WANT_WRITE` and
require the same read arguments on retry. The previous one-shot reader had no
continuation owner for that frontier; a naïve movable reader with inline prefix
storage could also relocate the buffer that OpenSSL expects to remain exact.

Rev0884 adds a move-only `SyncReplicaTlsRecordReadContinuation` whose private
state lives in one heap allocation. Prefix bytes, body bytes, offsets, limits,
terminal state, reservation, and the authenticated channel owner therefore keep
one stable identity while the public wrapper moves. Each advance performs at
most one `SSL_read_ex`, immediately classifies failure with `SSL_get_error`, and
returns typed progress for ordinary bytes, WANT_READ, WANT_WRITE, complete
frame, or clean pre-frame peer close. WANT does not advance offsets; the next
advance reconstructs the same pointer and length.

The cleanup frontier is explicit. Destruction before any attempted read releases
the reservation cleanly. Abandonment after any attempted read, including WANT,
poisons the channel because the pending operation cannot truthfully be replaced.
A close-notify before any frame byte yields `PeerClosed` and permanently closes
the channel without fabricating a frame. Close after prefix/body progress is
truncation and poisons. Empty and over-limit prefixes fail before body
allocation. Strict mode proves direct socket BIOs and `O_NONBLOCK` at begin and
every retry.

The transport owner is also simplified. A write-only active boolean is replaced
by one duplex `Idle/Read/Write` reservation. Reads, writes, generic record I/O,
and the delivery-authority live verifier cannot re-enter the same `SSL*` while
a continuation owns it. This intentionally gives up concurrent full-duplex use
until AnonSync has a serialized two-direction owner capable of proving it safe.
The legacy one-shot reader delegates to the same incremental state machine and
fails rather than spinning on nonblocking readiness.

The compiled TLS 1.3 matrix covers wrapper moves after prefix and body WANT,
fragmented records, clean and ambiguous abandonment, duplex exclusion,
readiness loss, clean close, truncation, bounds, non-socket descriptors,
foreign-thread fail-stop, and legacy delegation. The exact final build, test,
stress, sanitizer, source-audit, and package results are recorded under
`REVISION_EVIDENCE/rev0884/`.

This is not yet a production receiver. There is no poll/epoll service, bounded
complete-frame queue, authenticated accept/connect owner, durable receive/effect
composition in `anonsync_core`, peer receipt from transport completion, or
exactly-once remote execution. The next valuable step is to place this reader
and the exact first-prefix writer under one bounded event-loop owner and carry a
canonical operation through receiver SQLite/effect authority to a terminal
effect receipt.

Primary OpenSSL research, state machine, failure matrix, audit/refactor, and
deliberate nonclaims: `TLS_INCREMENTAL_RECEIVE_AUDIT_rev0884.md`.

## Rev0883: no-throw continuation affinity and destructor fail-stop

Rev0882 made an unfinished TLS record a move-only, state-owned capability, but
one no-throw path still escaped the authority model. An active continuation
could be moved into another C++ thread and abandoned there. Its destructor
called `poison_noexcept()` and silently changed the shared stream's poison and
reservation flags before any process/thread owner check. Final `SSL_free()` was
fenced, but the first foreign mutation had already occurred.

Rev0883 centralizes the authenticated state's no-throw process/thread proof and
requires it before completion, poison/abandonment, or final SSL release. A
foreign-thread finish, destructor, or move-assignment over an active target now
fails stopped before it can mutate shared TLS state. Same-owner abandonment
still poisons the stream because a complete prefix without its exact body cannot
be reused safely.

The compiled TLS matrix now transfers an active continuation into a foreign
`std::thread` inside an isolated child process. The foreign-thread destructor
must terminate with the exact capability-violation exit code; surviving the
thread join is a test failure. The focused executable reports 75/75 checks. The
structural audit grows to 32 checks and requires the centralized fence,
process-then-thread ordering, mutation ordering, public contract, runtime case,
package surface, and explicit nonclaims.

This review also rejected an unrelated 578-line nonblocking receive prototype
that appeared in a mutable workspace. It failed its first clean compile, changed
public APIs, and supplied no matching runtime matrix. Rev0883 was reconstructed
from the independently verified rev0882 archive instead of granting that branch
authority by presence. The receive direction remains the next major engineering
need, but it should arrive as an explicit event-loop state machine with partial
prefix/body offsets, WANT_READ/WANT_WRITE ownership, backpressure tests, and
clear crash semantics.

OpenSSL's own documentation warns that most objects are not safe for
simultaneous use and that `SSL_free()` may release the SSL object, BIOs, cipher
lists, and session references. This supports the conservative rule that cleanup
is live owner mutation, not bookkeeping exempt from affinity. It does not prove
race freedom. ThreadSanitizer, a receiver loop, resumable WANT-state ownership,
durable body progress, shipped-executable integration, peer receipt, and
exactly-once remote effect are not claimed.

Fresh rev0883 evidence records 192/192 registered tests, 61/61 audit-named
tests, and 5,199/5,199 focused checks in GCC Debug, Clang 17 Release with C++
`-Werror`, and GCC ASan/UBSan with leak detection and bundled SQLite
instrumented. Repeated gates add 5,940/5,940 mixed authority checks and
7,500/7,500 targeted TLS checks. Seventeen selected source audits pass
509/509 checks, including the corrected exact inventory of 15 inherited-process
consumer translation units and 27 spawn sites.

Primary design, online-source audit, failure matrix, rejected-scope record, and
deliberate nonclaims: `TLS_CONTINUATION_AFFINITY_AUDIT_rev0883.md`.

## Rev0882: exact first-prefix authority and exclusive TLS record ownership

Rev0881 returned a canonical file-delivery frame only after re-attesting its
claim under a SQLite writer. The returned C++ value could nevertheless wait in
an ordinary queue while that exact claim expired, was released, was settled, or
was replaced. The generic TLS writer did not know which durable attempt had
once authorized those bytes. This was a real authority gap: historical proof
that a frame was constructible is not live permission to begin that attempt.

Rev0882 adds a narrow composition owner between the file-delivery service and
the authenticated TLS transport. It freezes and reconstructs the bounded
outbound request, frame, and digest outside SQLite; reacquires the exact claim
under `BEGIN IMMEDIATE`; re-proves the live channel and claim-derived request;
then writes only the complete encrypted eight-byte application-record length
prefix while the writer guard excludes competing sender transitions. Once that
prefix has been accepted by OpenSSL, the guard commits and releases before the
potentially large immutable frame body is transferred.

The cutpoint is deliberately truthful. OpenSSL completion is not peer receipt,
receiver admission, durable evidence, filesystem effect, or sender settlement.
A failure before successful prefix return poisons the stream and exact-releases
the claim because no body was supplied through a reusable capability. A commit
or body failure after the prefix leaves the exact claim live and ambiguous;
only a terminal receipt, explicit exact transition, or owned-clock expiry may
retire it.

The TLS writer is now one state machine. `begin_sync_replica_tls_record_write_`
`or_throw()` returns a private, move-only continuation that exclusively owns the
unfinished record. The authenticated SSL owner rejects a second begin, an
ordinary record write, or a record read until the continuation finishes or is
abandoned. Wrong body length, readiness loss, failed live-session reproof, or
abandonment permanently poisons the stream. This corrected a serious defect in
the first rev0882 draft, where exclusivity existed only as caller convention and
a same-thread operation could interleave another record.

The SQLite/TLS composition refuses blocking or opaque BIOs. It requires direct
`BIO_TYPE_SOCKET` read and write BIOs, observable descriptors, successful
`getsockopt(SOL_SOCKET, SO_TYPE)` socket proof, and `O_NONBLOCK` on both
directions immediately before prefix progress and again before body progress.
Descriptor visibility or `O_NONBLOCK` alone is insufficient: a descriptor BIO
can wrap a non-socket object. A readiness contradiction therefore fails before
stream bytes and exact-releases the claim. The generic caller-managed TLS API
remains available outside this database critical-section policy.

A refactor removes two security-sensitive duplicate implementations. Generic
and file delivery now share one exact claim-to-request constructor, including
destination, operation, actor, kind, claim ID, and attempt checks. The one-shot
TLS writer delegates to the same begin/continuation machinery as the composed
path. The new composition remains a separate small library, so the file service
does not absorb OpenSSL and the TLS transport does not absorb SQLite or effect
policy.

Fresh evidence includes one complete 192/192 CTest invocation, the complete
61/61 audit block, 5,198/5,198 focused checks under GCC Debug, Clang 17 Release
`-Werror`, and GCC ASan/UBSan with bundled SQLite instrumented, 5,920/5,920
checks across 100 repeated authority executions, a separate 100-run/7,400-check
TLS cutpoint stress gate, and 505/505 selected lexical audit checks. Lexical
audits remain architecture and package hygiene, not semantic proof.

The largest remaining gap is liveness and restart ownership after prefix
progress. Rev0882 intentionally poisons on `SSL_ERROR_WANT_READ` or
`SSL_ERROR_WANT_WRITE`; it has no event-loop continuation that preserves the
same immutable OpenSSL write arguments, no durable `dispatch_started` state,
and no lease heartbeat while a large body is in flight. The shipped executable
also still does not use the newer causal, file-effect, receipt, and TLS
composition stack. The next valuable milestone is a small replica service with
a real receiver loop and crash injection across prefix, body, receiver commit,
publication, receipt, and settlement frontiers.

Primary design, audit, research, failure matrix, and deliberate nonclaims:
`TLS_FIRST_PREFIX_DISPATCH_AUDIT_rev0882.md`.

## Rev0881: local path capability, exact retry release, and live namespace context

A canonical AnonSync path is global evidence; a destination filesystem's
component ceiling is local effect capability. Rev0880 allowed those two layers
to meet too late. A portable operation whose component exceeded the retained
root's `{NAME_MAX}` could consume payload storage, effect generation, causal
evidence, and repeated sender leases before publication finally failed with
`ENAMETOOLONG`.

Rev0881 moves that proof before effect authority. The file-effect owner first
validates exact operation and payload bytes, then applies a receiver-local
encoded-byte ceiling derived conservatively from the retained root's frozen
`statvfs().f_namemax` and positive `_PC_NAME_MAX` observations. A provably
unrepresentable path returns `DestinationPathBlocked` from an unchanged,
attested transaction. It inserts no effect row, retains no payload, advances no
generation, admits no causal evidence, and touches no namespace entry.

The outer file-delivery protocol explicitly advances to version 2 and adds the
typed `EffectPathBlocked = 9` disposition. Pre-effect denials carry the exact
request and unchanged receiver effect cutpoint, but neither an effect ID nor an
inner causal receipt. Version-1 readers reject the frame version rather than
silently interpreting an outcome they never negotiated.

Validated nonterminal receipts no longer leave a live attempt idle until lease
expiry. The sender releases the exact destination/operation/claim through the
outbox owner's clock and a local, strictly positive, bounded retry policy. The
same transition handles callback, channel-reproof, validation, encoding, or
digest failures after claim minting but before frame escape. Missing, stale, or
expired claim identity fails closed and cannot fabricate release provenance.

Retained directory capability now also freezes the calling thread's live Linux
mount-namespace context. `SyncPosixMountNamespaceAuthority` retains
`/proc/thread-self/ns/mnt`, compares its documented `st_dev`/`st_ino` identity
with a fresh current-thread handle on every proof, and sticky-revokes after any
contradiction. Capture occurs before pathname traversal, so a later
`unshare()`/`setns()` cannot use a descriptor from one namespace as authority in
another.

An audit/refactor consolidated the process-identity and outbox-clock boot-ID
readers into one strict, bounded `sync_system_epoch_identity` leaf. Missing or
permission-hidden procfs evidence is typed at that boundary. The current clock
codec still requires a concrete 36-byte boot UUID, however, so unavailable boot
identity throws before the SQLite owner can durably quarantine it. Likewise,
the arbitrary payload callback is followed by channel reproof but not yet an
exact post-callback outbox-claim attestation. Both gaps are named rather than
hidden.

The file-effect schema remains version 2. Boot UUID and mount ID were
intentionally rejected as mandatory permanent root identity because they are
runtime-ephemeral and would lock an exact database after an ordinary reboot
without an authorized rebind ceremony. Legacy rev0878-rev0880 staged rows whose
names were already impossible are not silently deleted; they require a future
repair protocol.

Primary design and research record:
`FILE_EFFECT_PATH_CAPABILITY_AUDIT_rev0881.md`.

## Rev0880: observed mount-boundary authority and shared resolution owner

Rev0879's descendant fence compared `st_dev`. That blocks another filesystem
but cannot distinguish a same-device bind mount. Rev0880 classifies the actual
running POSIX resolution capability and, on Linux, combines `openat2` with
`RESOLVE_NO_XDEV` and descriptor `statx` mount identity. No kernel version is
used as capability evidence. The exact observed mode is frozen in the retained
root authority, re-proved before use, and carried with every verified duplicated
root descriptor.

The cloudtainer supplies a concrete witness: `/proc` and `/proc/bus` have the
same `st_dev`, but `/proc/bus` is a distinct mount. The focused runtime test
proves that this crossing is rejected when the host exposes either the
`openat2` or `statx` fence. Systems without those observed interfaces retain the
portable device/inode baseline and its explicit same-device-mount nonclaim.

This revision also consolidates the absolute authority, rooted publication, and
legacy absolute publication component loops into one exception-safe POSIX
syscall owner. Domain-specific owner/mode and member-file rules remain in their
callers. A separate audit found and corrected a descriptor leak: when the
post-duplication authority reproof failed, the untransferred duplicate was not
closed.

Mount IDs remain live, runtime-ephemeral evidence and are intentionally absent
from the durable v1 root-attestation digest. A live rebind is detected, but
restart-stable mount-object identity requires a future boot-epoch and authorized
root-rebind protocol. The shipped executable still does not use this newer
effect path.

Primary design and research record:
`MOUNT_BOUNDARY_AUTHORITY_AUDIT_rev0880.md`.

## Rev0879: retained root authority for effect-terminal File publication

Rev0878 composed live authenticated delivery, exact causal projection, bounded
payload staging, immutable publication, and effect-terminal receipts for one File
operation. Its file-effect owner still persisted only normalized root-path text.
A same-path directory replacement between calls could therefore redirect a later
publication into a different tree while the database retained the same spelling.

Rev0879 closes that POSIX boundary. The effect owner now retains one move-only,
process/thread-affine root directory capability, freezes device/inode,
credentials, mode, filesystem and mount observations, persists the canonical
attestation digest in exact file-effect schema version 2, and performs
reconciliation/publication from a duplicated root descriptor plus a strict
canonical relative path. Root replacement revokes a live owner, and restart
against a different root object fails before existing effect authority is
accepted.

The focused path is now:

`live channel authority → exact active-primary cutpoint → bounded staged payload`
`→ retained root capability → descriptor-relative descendant policy → immutable`
`create-new publication → file/directory durability → rooted reconciliation →`
`root-bound effect cutpoint → effect-terminal receipt → sender settlement`

Every descendant parent must remain on the retained root device, be owned by the
retained effective UID, grant owner read/write/search, and deny group/other
write. These checks occur before temporary inode reservation. The absolute-path
and rooted callers share one atomic publication state machine and one restart
reconciliation state machine.

This revision also removes duplicated security machinery: the local JSONL replay
directory class now delegates to the same generic `SyncDirectoryAuthority`.
Automatic migration from path-only file-effect schema v1 is intentionally
refused because old rows contain no evidence of which directory object owned the
prior effects.

This remains a correctness slice, not a complete sync product. The retained-root
path is POSIX-only, does not yet reject same-device bind mounts, has no authorized
root-rebind protocol, and is not used by the shipped executable.

## The central correction: projection authority must survive until effect proof

An earlier composition checked whether an operation was the active visible
primary in one SQLite snapshot, released that snapshot, and then wrote the file.
A second owner could change causal projection between those steps. The receiver
could therefore publish bytes and construct a terminal receipt from a stale
projection decision.

`SyncReplicaSqliteProjectionGuard` closes that check/use gap. It:

- opens `BEGIN IMMEDIATE` on the causal owner;
- fully restores and re-attests exact state;
- requires the exact generation and cutpoint named by the inner evidence receipt;
- requires the exact retained File operation to be Active, the sole visible
  primary, and free of preserved alternates;
- retains the writer-serializing transaction across filesystem materialization,
  effect-owner re-attestation, and canonical receipt construction; and
- commits only after the exact effect receipt bytes and digest exist.

A changed cutpoint returns no authority and produces `ProjectionBlocked`; it is
not silently upgraded to whatever state happens to be current. A runtime test
uses an independent SQLite connection with zero busy timeout to prove that a
competing causal writer is blocked while the guard is live, succeeds after the
guard commits, and cannot make an old cutpoint mint effect authority.

The guard does **not** pretend that SQLite and the filesystem are one
transaction. A rename or fsync can complete before a later exception or process
exit. The effect owner therefore uses immutable no-replace publication and exact
restart reconciliation. A retry may recognize the exact private durable file and
finish the database transition; it never guesses from a syscall return alone.

SQLite documents that `BEGIN IMMEDIATE` starts a write transaction immediately
and may fail with `SQLITE_BUSY` when another writer is active. SQLite permits
multiple readers but only one simultaneous writer. These properties support the
local serialization point; they do not create a transaction across two SQLite
databases and a filesystem.

- https://sqlite.org/lang_transaction.html
- https://sqlite.org/isolation.html

## Payload and lease authority

The file service now requests only `SyncReplicaValueKind::File` work and gives
the owner both the complete delivery model and the maximum payload size before a
lease can be minted. A canonical File whose committed size exceeds the local
wire/effect policy throws inside the preclaim transaction while attempt number,
claim ID, worker, lease, and cutpoint remain unchanged.

This fixes a concrete liveness waste: an oversized operation could previously be
claimed, fail request construction, remain leased until expiry, and repeat the
same impossible cycle.

The payload callback still runs after a valid durable lease exists. A callback,
post-callback channel proof, request validation, encoding, or digest failure now
releases the exact attempt under the sender owner's clock before rethrowing. The
release delay must be positive and within the fixed retry budget, preventing an
idle lease and a caller-configured immediate spin.

This is still an ambient-authority boundary: a payload callback that can also
reach the outbox owner could mutate the claim and then return valid bytes. The
service re-proves channel authority but does not yet hold an exact dispatch guard
or re-attest the claim after arbitrary code. A production payload-store
capability should remove that overlap rather than relying on a loose O(history)
snapshot check.

## Receiver effect ownership

`SyncReplicaFileEffectSqliteOwner` owns a separate database containing exact
canonical operation bytes, exact payload bytes, effect identity, state
generations, aggregate limits, redundant fields, and a complete structural
cutpoint. Every public operation restores and re-attests the full retained set.
It is deliberately an **O(history) correctness oracle**, not a scalable
production index.

The receiver stages exact bytes before causal admission. This prevents an
operation from becoming evidence-terminal when the receiver cannot retain the
payload required for its effect. It also creates an availability obligation:
authenticated but pending or quarantined work can consume staging capacity. The
current aggregate limits do not yet provide per-peer quota, expiry, reclamation,
or dead-letter authority.

For publication, the effect owner classifies the namespace as:

- absent: create one private immutable file;
- exact and directory-synced: reconcile a prior or concurrent successful effect;
- conflicting: preserve the existing entry and return a nonterminal conflict.

Exact means stable bytes, same effective UID, mode 0600, link count one, regular
file type, file synchronization, directory synchronization, and identity
revalidation. File `fsync()` alone does not necessarily persist the directory
entry, so terminal proof includes the containing directory boundary.

- https://man7.org/linux/man-pages/man2/fsync.2.html

## Live channel authority remains load-bearing

Every file-service entry point accepts
`SyncReplicaDeliveryChannelAuthority`, not public
`SyncReplicaDeliveryChannelContext`. The file orchestrator is an explicit friend
of the nonforgeable capability so it can fail closed before staging, claiming,
or settlement without exposing a public “validate” or “mint” API.

The same opaque authority is passed to the nested evidence service. The outbound
path revalidates it after the arbitrary payload callback and before returning
bytes that claim the original channel binding. Production linkage excludes the
deterministic test mint; the test executable alone links that factory.

The inherited TLS adapter requires TLS 1.3, successful peer verification, exact
ALPN, actor/SPKI pinning, a fresh non-resumed session, no early-data attempt, and
an RFC 9266 exporter binding. It owns an OpenSSL reference, is process- and
thread-affine, and permanently poisons record authority after uncertain partial
I/O or invalid framing.

This remains same-process domain separation. It is not a sandbox against
arbitrary code execution, memory corruption, debugger control, or malicious code
already holding the capability.

## Heart of the mission

The mission is a chain of authorities:

1. **Observation authority:** preserve provenance, capability, and uncertainty
   before any physical observation influences identity or liveness.
2. **Canonical identity:** freeze exact operation bytes and derive one immutable
   ID from them.
3. **Exact causality:** name immediate predecessors; summaries may locate work
   but cannot replace parent evidence.
4. **Actor and membership authority:** authenticate actor/key epochs and define
   enrollment, rotation, revocation, recovery, rollback, and old-epoch treatment.
5. **Durable publication:** bind operation bytes, parent edges, projection,
   payload commitment, dispatch ownership, clock evidence, receiver admission,
   visible effects, and receipts to explicit transitions.
6. **Deterministic projection:** retain evidence independently of active and
   visible state so trust and dependency changes can be re-evaluated.
7. **Bounded dissemination:** own CPU, bytes, identities, dependencies, storage,
   time, retries, and wake work under explicit limits.
8. **Receiver effect ownership:** let a terminal receipt mean one exact,
   idempotent, crash-reconciled visible effect—not merely message receipt.
9. **Privacy authority:** state the adversary and observable metadata before
   claiming anonymity, unlinkability, or traffic-analysis resistance.

The compact invariant is:

> Given the same authorized canonical evidence and trust state, replicas must
> derive the same state; no untrusted input, crash cutpoint, duplicate, missing
> dependency, resource claim, stale projection, schema mutation, stale receipt,
> fabricated channel description, reused TLS object, clock movement, retry
> response, namespace race, migration shortcut, or local pressure decision may
> silently gain authority.

## Cross-store boundary and lock order

Rev0878 has three independent durable domains:

1. the sender/receiver causal SQLite owner;
2. the receiver effect SQLite owner; and
3. the receiver filesystem namespace.

The receive path stages in the effect database and releases that transaction,
performs causal admission, then acquires causal projection guard authority before
materializing through the effect owner. The live overlapping order is therefore
**causal database → effect database → filesystem**. Current effect-owner methods
do not call back into the causal owner, so the implementation has no inverse
nested path. Future composition must preserve one declared lock order; adding an
effect-to-causal callback would create deadlock risk.

Holding the causal writer slot across full-history effect restore and file and
directory fsync is conservative and potentially expensive. It is appropriate for
this reference oracle. A production design should authorize a narrower immutable
projection lease or signed projection token, keep the full-history owner as a
differential oracle, and prove that the indexed path derives the same terminal
cutpoints.

## Root identity is retained; live mount context is now fenced

`SyncDirectoryAuthority` opens an absolute root component by component without
following symlinks, retains the terminal descriptor, and re-proves both that
object and the configured path before authority-bearing work. Any observed
identity, mode, credential, filesystem, mount, or mount-namespace contradiction
permanently revokes the live object. The effect owner binds its normalized path
and frozen durable attestation digest into complete database and publication
cutpoints.

Destination parents are opened relative to a duplicated root descriptor. Linux
uses runtime-observed `openat2(RESOLVE_NO_XDEV)` and, when available, `statx`
mount identity to reject same-device mount crossing. Rev0881 additionally
retains `/proc/thread-self/ns/mnt` before traversal and re-proves the current
thread remains in that namespace. Runtime tests cover root replacement, sticky
revocation, restart against a replacement root, shared-writable descendants,
`/proc` versus the same-device `/proc/bus` mount witness, and a mount-namespace
transition when the host permits unprivileged `unshare()`.

The live mount namespace inode and mount ID are deliberately excluded from the
durable root-attestation digest. They are useful runtime evidence but are not
restart-stable storage identity. An explicit operator/device-authorized root
rebind protocol remains absent; changed durable roots and schema-v1 databases
fail closed.

- https://man7.org/linux/man-pages/man7/namespaces.7.html
- https://man7.org/linux/man-pages/man2/openat2.2.html
- https://man7.org/linux/man-pages/man2/statx.2.html

## Audit and refactor work

Rev0879 adds a 31-check retained-root source inventory covering capability shape,
component traversal, frozen policy and digest, sticky reproof, JSONL delegation,
strict relative paths, descendant policy, shared publication/reconciliation,
schema-v2 binding, SQLite cutpoint ordering, adversarial runtime cases, CMake
ownership, and package inventory. It is explicitly **lexical hygiene, not
semantic proof**.

The local JSONL directory authority is now a thin compatibility facade over one
generic owner. This removes a duplicated syscall and revocation state machine
instead of adding a second security boundary. Neighboring atomic-publication and
JSONL audits were updated to follow the new shared verifier/delegation shape
without weakening their runtime expectations.

Rev0881 adds a dedicated file-effect path-capability inventory and updates the
file-delivery, mount-boundary, process-identity, and outbox-clock audits to track
positive bounded retry policy, pre-effect denial, live mount-namespace context,
and the shared boot observer. The refactor removes two divergent procfs readers;
the audit also records the two unsolved composition gaps instead of treating
source vocabulary as proof. The fresh sanitizer lane caught and corrected a
separate CMake policy-list drift: the new epoch test was instrumented for
compilation but initially omitted from sanitizer runtime linking. The dedicated
audit now requires both entries.

The build graph remains wasteful. CMake now contains 79 library declarations,
98 executable declarations, and 193 `add_test` occurrences, yet semantic centers
still include
approximately 15,167 lines in `sync_domain.cpp`, 9,601 in
`sync_domain_selftests.cpp`, 4,529 in `sqlite_replay_ledger.cpp`, and 3,713 in the
causal SQLite owner. The full rebuild spends far more time compiling these older
monoliths than the new authority slice. Target count has outpaced semantic
modularity.

Correction should proceed by authority boundary rather than arbitrary file size:

- split restore/attestation, transition, serialization, and storage ownership;
- generate repetitive target, sanitizer, and test wiring through CMake helpers;
- retain a fast affected-authority gate plus one complete periodic registry;
- measure header and link fanout before choosing cuts; and
- keep the full-history owners stable as differential reference implementations.

`REVISION_EVIDENCE/` already contains more than 4,500 files and roughly 41 MB
before rev0878 evidence. Each new revision therefore keeps compact in-tree
lineage, source delta, audits, summaries, and hashes. A future externally signed,
content-addressed artifact store should hold bulk logs and historical corpora.

## Largest product gap

No production caller in the shipped `anonsync_core` executable uses
`SyncReplicaFileDeliveryService`, the newer causal owner, or the TLS channel.
The current result is a deeply tested correctness island rather than
user-visible synchronization.

The next product milestone should be one narrow executable with:

`configured folder + pinned peer + stable root capability + TLS 1.3 framed`
`transport + bounded request queue + causal/effect owners + one File operation +`
`terminal response + restart injection at every durable frontier`

Only after that path is operable should the project expand to updates,
tombstones, discovery, relays, group membership, compaction, and privacy
mechanisms.

## What remains missing

The most important absent authorities are:

- explicit root epochs/rebinding, schema-v1 migration receipts, and repair of
  legacy locally impossible staged effects;
- ordinary update, rename, tombstone, and deletion effects;
- immutable content-object storage separated from mutable path projection;
- per-peer staging quota, expiry, garbage collection, and dead-letter policy;
- payload-store availability classification and exact post-callback claim
  authority before frame escape;
- durable signed/offline-verifiable receiver effect receipts;
- response journaling across sender crash after transmission;
- membership enrollment, monotonic epochs, rotation, revocation, and recovery;
- durable boot-source-unavailable clock evidence, reconnect/event-loop
  transport, negotiation, jitter, attempt limits, permanent rejection,
  dead-letter authority, and wake scheduling;
- third-party gossip, anti-entropy, causal stability, compaction, and rejoin;
- indexed production owners differentially checked against the O(history)
  oracles;
- an explicit privacy/adversary model; and
- externally trusted signed build provenance.

The name “AnonSync” remains an aspiration. Mutual TLS and payload confidentiality
do not hide endpoints, timing, direction, volume, certificates, or all
application metadata, and therefore do not establish anonymity or unlinkability.

## Evidence and nonclaims

`FILE_EFFECT_PATH_CAPABILITY_AUDIT_rev0881.md` contains the deep defect,
capability split, protocol-v2, retry, namespace, refactor, primary-source
research, rejected-design, and remaining-gap analysis. `RELEASE_GATE.json` and
`REVISION_EVIDENCE/rev0881/` are the authority for compiler, sanitizer, stress,
registry, projection, manifest, and package results.

Rev0881 does not claim use by the shipped executable, normal mutable-file
convergence, deletion, repair of legacy staged poison, restart-stable mount or
boot identity, authorized root migration, Windows path/retained-root parity,
exact post-callback claim authority, durable clock quarantine when boot ID is
unavailable, exactly-once behavior against a privileged or same-UID local
writer, fair hostile-peer staging, independently signed receipts, complete
membership/key lifecycle, complete retry/dead-letter scheduling, nonblocking
transport, production-scale indexed ownership, anti-entropy, compaction,
anonymity, malicious-host defense, full-project
Clang/sanitizer/ThreadSanitizer coverage, externally trusted provenance, or
formal proof.
