# Crash-recoverable bootstrap record and idempotent resume audit — rev0900

## Executive conclusion

AnonSync's heart is **durable bounded causal convergence in which authority is
explicit, evidence-bound, recoverable, and never fabricated by observation**.
The product is not merely a file copier and it is not yet an anonymity system.
Its central discipline is that a path, file, row, summary, process, retry, or
operator assertion must not become authority merely because it exists. Exact
validated history and durable cutpoints authorize transitions; derived state is
only an accelerator or report.

Rev0899 made a newly initialized store set prove one common deployment birth,
but its fail-closed interruption behavior was not yet recoverable. A crash after
one or more stores had been created, but before the final deployment manifest
was published, left a set of correctly bound resources with no durable object
that explicitly authorized completing that exact configuration. Re-running
fresh `init` correctly refused to adopt them, but the only safe operational
answer was manual forensic work or abandonment. That was a real mission gap:
authority was explicit after commit, but the pre-commit transition itself was
not durably named.

Rev0900 adds one immutable bootstrap record before store mutation and one
bounded `init-resume` command. The record's payload is not a second configuration
language. It is the **byte-exact canonical future deployment manifest**, still
self-bound to the exact final manifest pathname and self-digested under the
existing manifest grammar. Its deterministic hidden sibling name is derived
from a domain-separated SHA-256 of that canonical final path. Recovery therefore
selects a deployment from exact durable evidence, never from nearby filenames,
store presence, or a guessed configuration.

The implementation is deliberately narrower than a general transaction or
repair engine. It can complete a record-selected partial store set only while
all present resources remain at bootstrap genesis. If no selected store is
missing, an operationally advanced but complete deployment may republish a lost
final manifest from the exact record. Once the final manifest exists,
`init-resume` is identity-only and cannot create a missing store, initialize role
schema, or reconcile the membership pair. Those constraints preserve the
meaning of the final manifest as the commit cutpoint rather than turning resume
into an unbounded repair authority.

## What changed

### One exact pre-commit authority

`src/sync_replica_bootstrap_record.{hpp,cpp}` owns the record boundary. For final
manifest path `P`, the record is a fixed-length hidden sibling:

```
.anonsync-replica-bootstrap-<sha256(domain || canonical P)>.json
```

The domain is `anonsync:replica-bootstrap-record-path:v1\n`. Fixed-length naming
avoids inheriting an operator-controlled manifest basename length. Namespace
validation proves that the derived file cannot alias the final manifest, any
selected SQLite main file, its `-journal`, `-wal`, or `-shm` sidecar, or reside
inside either mutable content root.

Creation uses immutable create-new publication, private mode, file
synchronization, atomic no-replace namespace publication, and parent-directory
synchronization. Readback is bounded to the deployment-manifest ceiling,
refuses symbolic links, strictly decodes the bytes against the expected final
pathname, revalidates the record namespace, and reconciles the exact file plus
parent-directory durability before returning authority.

The exact-byte deployment-manifest decoder was extracted from the pathname
reader. This is intentionally one parser and one canonical encoder: the durable
record can live at a staging pathname while its bytes remain bound to the final
commit pathname. Copied records fail because the embedded `manifest_path` does
not bind the caller-selected final filename; edited records fail canonical
re-encoding and self-digest checks.

### Record-first fresh initialization

Fresh `init` still has no adoption semantics. It first proves the final manifest
and deterministic record absent, every selected SQLite main and sidecar absent,
and mutable roots empty. It prepares a move-only final-manifest publication
capability, which retains destination authority but creates no temporary or
final entry. The record is then the first durable mutation. Only after its exact
readback may store creation begin.

After record publication, the namespace is inventoried again. If a resource
appeared between the original preflight and that observation, fresh `init`
refuses and directs the operator to `init-resume`; it does not reinterpret the
racing resource as part of the deployment. Newly created stores are checked at
genesis, the complete set is identity-attested, role state is inspected, the
membership pair is reconciled, the record is re-read unchanged, and only then is
the prepared final manifest published.

### Exact-record-selected `init-resume`

`init-resume --manifest ABSOLUTE_JSON` takes no raw store, root, actor, folder,
or capacity options. The deterministic record and its canonical bytes select
every value. Recovery is split into ordered phases:

1. Inventory all selected main files, sidecars, payload identity, and files-root
   state. A sidecar without its main database is an explicit refusal, not an
   empty slot.
2. Identity-attest every present SQLite main and payload store against the
   record-selected deployment before any role owner may initialize or migrate
   schema elsewhere.
3. Inspect present role state and classify whether all present resources and
   the files root remain at bootstrap genesis.
4. If any selected store is missing, refuse unless every present resource is at
   genesis. Otherwise create only the missing resources.
5. Attest the complete store set, re-read the record unchanged, and publish the
   exact final manifest.

The identity-first ordering is a security boundary. For example, when the
replica database is missing but a later effect database has been replaced with
a foreign one, resume rejects that foreign binding before it can create the
earlier missing database. This prevents partial recomposition from acquiring
more authority merely because creation order happens to encounter an empty slot
first.

### Committed replay is identity-only

A final manifest changes the permissible behavior. The committed branch first
requires byte identity between final manifest and record, strict decoding of the
final file, and exact file-plus-parent durability reconciliation. It then
requires that every selected store exists and proves the record-selected
identity. It does **not** traverse role-owner constructors or membership
reconciliation.

This split corrected a subtle audit finding. The earlier implementation refused
to create a missing committed store, but still constructed every role owner and
could therefore initialize or migrate schema, create WAL state, or reconcile
membership while calling the operation idempotent. The final implementation
keeps committed replay at the identity boundary and leaves ordinary operational
commands responsible for later role-state work.

## Crash and cutpoint analysis

The behavior at each relevant cutpoint is now explicit:

| Cutpoint | Durable observation after restart | Authorized result |
|---|---|---|
| Before record publication | No record, no committed manifest | Fresh `init` may begin after full freshness proof. |
| Record durable, no stores | Exact future manifest is known | `init-resume` may create all selected stores. |
| Some exact-bound stores at genesis | Record plus partial genesis set | Resume may create only the missing stores. |
| Present foreign, copied, tampered, or wrong-role store | Record conflicts with present identity | Refuse before creating any missing store. |
| Present state advanced and another store missing | Partial deployment has operational history | Refuse recomposition; no final manifest is published. |
| Complete exact-bound set advanced, final manifest absent | No store is missing and record remains exact | Republish the lost final manifest without erasing state. |
| Final manifest exists and a store is missing | Commit marker names an incomplete set | Refuse; committed resume never mints replacement authority. |
| Record or final entry visible after indeterminate directory sync | Exact bytes may be visible but durable namespace state was uncertain | Reconcile exact file and parent directory before accepting it. |
| SQLite main file exists but deployment binding was not durably completed | Main-file birth cannot prove record-selected identity | Refuse; this remains a known stranded cutpoint. |

The last row is the largest remaining bootstrap defect. SQLite main-file
creation and the first binding transaction are separate durable steps. A crash
between them can leave an unbound main file which neither fresh initialization
nor exact resume may safely adopt. Correcting that requires an atomic database
birth protocol, likely by constructing and closing a fully bound database under
a writer-owned temporary name and publishing it with a no-replace rename, plus
careful proof that SQLite has left no live sidecar state. That is materially
larger than accepting an empty file or teaching resume to infer ownership, both
of which would violate the mission.

## Audit and refactor findings

### Durability acceptance was initially too weak

The first record reader bounded, decoded, and identity-checked a visible record
but did not upgrade an indeterminate prior directory-sync outcome before using
it as recovery authority. A crash could therefore leave the record visible
while the namespace durability of that entry remained uncertain. The final
reader now invokes immutable-file reconciliation and returns only the
`ExactAndDirectorySynced` outcome. The same reconciliation was added to
committed final-manifest replay.

This distinction matters because “the bytes can be opened now” is an
observation, not proof that the create-new cutpoint survived the preceding
failure domain. Rev0900 makes the restart path complete the durability proof
before granting authority.

### Authority audits had become layout-coupled

Several lexical audits assumed all creation statements lived directly inside
`command_init`. Extracting a shared creation frontier and adding `init-resume`
made those inventories fail even though runtime authority had become narrower.
The audits were refactored to pin the real graph instead: one shared missing-store
creator, exact record selection, identity-before-state ordering, genesis-gated
partial creation, committed identity-only replay, and no raw creation surface in
normal commands.

The broad suite then exposed one more stale closed inventory. The bounded-file
reader audit correctly noticed the new bootstrap-record consumer but had not
listed it. The test was not suppressed; the allowlist was updated to name that
consumer and the current product reads. The failed intermediate run is retained
as release evidence, followed by the passing 221-test run.

### Build provenance waste was corrected, not hidden

A recovered incremental cache pointed at a different workspace path. Reusing it
would have produced weak source/build provenance and misleading dependency
closure. Rev0900 discarded that cache and used an explicitly configured GCC 14
Debug tree. Focused targets were built first; the remaining broad graph still
required 313 Ninja actions and three command-ceiling invocations, while the full
221-test registry completed in 19.35 seconds.

The asymmetry remains wasteful. The likely correction sequence is:

1. publish a documented product/authority fast lane;
2. measure header fan-out and incremental invalidation;
3. add a measured compiler launcher such as `ccache` or `sccache` when available;
4. only then experiment with target-scoped unity builds, never global unity that
   can conceal include, macro, or ODR defects.

### Sanitizer lane

A clean separate GCC 14 Debug AddressSanitizer/UndefinedBehaviorSanitizer build
compiled the manifest, record, binding, and product executable closure across
119 actions. Three compiled authority tests and all nine resume process
scenarios passed with leak detection and halt-on-first-error enabled. This is a
focused memory/UB check, not a ThreadSanitizer claim or a full sanitized
registry.

## Adversarial evidence

The process corpus drives only the shipped executable and proves nine distinct
scenarios:

1. fresh record/final/stdout byte identity, private mode, and committed
   idempotence;
2. recovery of a lost final manifest for an advanced but complete sender;
3. recreation of a missing genesis payload identity;
4. recreation of a missing genesis receiver database;
5. foreign later-role binding rejected before an earlier missing database is
   created;
6. advanced partial deployment refused;
7. committed deployment with a missing store refused;
8. orphan SQLite sidecar refused;
9. copied record rejected by final-path binding.

The compiled record test additionally proves deterministic fixed-length naming,
exact canonical byte round-trip, private mode, duplicate create-new refusal,
copy rejection, tamper rejection, and namespace collision refusal. The manifest
test proves the direct decoder preserves size, canonicalization, digest, and
final-path constraints.

## Online research and architectural implications

Primary SQLite documentation treats `-journal`, `-wal`, and `-shm` files as
members of database recovery and live WAL state, not disposable clutter. It
also documents that the super-journal providing multi-database atomicity is a
rollback-journal mechanism and that WAL transactions are atomic per database,
not across multiple database files. This supports both orphan-sidecar refusal
and the nonclaim of cross-store atomicity.

SQLite's corruption guidance emphasizes that rogue writers, stale handles,
multiple library copies, renamed/unlinked live databases, and inconsistent
sidecar handling can defeat SQLite's own protections. AnonSync must therefore
keep its store-set authority and local-writer threat model distinct from
SQLite's transactional guarantees.

Linux `openat2(2)` provides `RESOLVE_BENEATH`, `RESOLVE_IN_ROOT`,
`RESOLVE_NO_SYMLINKS`, `RESOLVE_NO_MAGICLINKS`, and related constraints. A future
Linux deployment-root capability can use those semantics to reduce ancestor
rebinding and traversal races. Portable implementations still require reviewed
component walks and explicit platform nonclaims.

SQLite 3.53.4 was released on 2026-07-24 and fixes issues present in 3.53.0
through 3.53.3. Rev0900 retains the already reviewed bundled 3.53.3 pin; it does
not smuggle a dependency refresh into an authority revision. A dedicated update
should import official bytes, verify the published source ID and SHA3-256,
update local SHA-256 pins, and rerun SQLite crash, backup/restore, process, and
full registry lanes.

Primary sources:

- https://sqlite.org/tempfiles.html
- https://sqlite.org/wal.html
- https://sqlite.org/lang_attach.html
- https://sqlite.org/atomiccommit.html
- https://www.sqlite.org/howtocorrupt.html
- https://man7.org/linux/man-pages/man2/openat2.2.html
- https://sqlite.org/releaselog/3_53_4.html

## What remains missing

The new record closes one pre-commit authority gap; it does not make the product
complete. Highest-priority remaining work is:

1. **Atomic database birth and binding.** Eliminate the stranded unbound-main
   cutpoint without adopting path presence as identity.
2. **Bootstrap inspection and quarantine.** Add a read-only report that
   classifies exact record, manifest, database-family, root, binding, genesis,
   and residue state without running role constructors; add explicit quarantine
   or operator-directed abort policy rather than automatic deletion.
3. **Temporary-publication residue ownership.** Atomic publication reports
   possible temp residue after some failures but has no bounded inventory and
   quarantine workflow for deployment bootstrap.
4. **Descriptor-rooted deployment authority.** Replace a bag of absolute paths
   with one retained root capability and portable relative resource names.
5. **Cross-resource transition protocol.** WAL does not provide atomicity across
   the replica, effect, membership, anchor, payload, and final-file resources.
6. **Hostile local-writer model.** The current unkeyed bindings detect accidental
   corruption and recomposition, not a same-UID or privileged writer able to
   rewrite all resources. External signing or hardware-rooted keys would be
   needed for that claim.
7. **Forensic status.** `status` still enters write-capable WAL owner surfaces;
   it is not a side-effect-free evidence export.
8. **Product completion.** A bounded durable supervisor, peer discovery,
   backoff, causal directory/tombstone/rename semantics, chunking and transfer
   resume, reachability/GC, indexing, at-rest encryption, and an explicit
   anonymity/privacy threat model remain absent.

A practical next sequence is atomic database birth, then read-only bootstrap
inspection/quarantine, then one descriptor-rooted deployment capability. Only
once those authority foundations are stable should the product add a durable
supervisor that repeatedly invokes existing bounded transitions.

## Validation

- Explicit GCC 14.2.0 Debug build; bundled SQLite 3.53.3 and OpenSSL 3.5.5.
- Broad build completed after 313 remaining Ninja actions; final closure:
  `ninja: no work to do.`
- Full registered suite: 221/221 in 19.35 seconds with 8 workers.
- Focused product/authority lane: 12/12.
- Resume process proof: 9/9 scenarios, direct and registered.
- Bootstrap authority audit: 24/24.
- Database-open policy audit: 17/17.
- Deployment-binding audit: 23/23.
- Bounded regular-file consumer audit: 23/23.
- Payload-store audit: 33/33.
- Release path-policy selftest: 14/14.
- Focused GCC 14 ASan/UBSan authority and process lane passed.
- Changed-text whitespace/newline audit and Python bytecode compilation passed.
- `clang-format` was unavailable and is not claimed.

These tests and lexical audits are executable tripwires, not formal proof of
power-loss behavior on every filesystem, freedom from noncooperating-writer
races, cross-resource atomicity, hostile local-writer resistance, or anonymity.
