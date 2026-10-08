# Rev0811 audit: sticky owner memory and destructive reset authority

## Scope

This review followed the checkpoint owner generation from public API options,
through orchestration, pure policy, SQLite row interpretation, recipient write
transactions, filesystem-effect reservations, checkpoint-root replacement,
operator recovery workflow, direct repair entry points, CLI construction, and
the focused/full test graphs.

The audit compared the exact extracted rev0810 parent against the rev0811 source
and treated the rev0810 fallback sketch as untrusted design input because it was
not part of production CMake or CTest.

## Severe findings

### A. Rev0810 was labeled as a release without being integrated or sealed

Severity: release integrity.

The parent archive has one top-level directory named after the long archive
filename rather than `AnonSync/`. The embedded release gate and README still
identify rev0809. The primary `MANIFEST.sha256` omits the four rev0810 fallback
files. The sticky-owner code is a 26-line standalone reference implementation
outside production source, runtime linkage, and CTest.

The current verifier records:

- parent ZIP, unpinned: 7/17 checks;
- parent ZIP, expected rev0810: 7/18 checks;
- extracted parent directory, unpinned: 19/20 checks;
- extracted parent directory, expected rev0810: 19/21 checks.

Rev0811 does not conceal or reinterpret those results. It binds the exact parent
archive hash, records all four verifier reports, derives the source patch from
the exact extraction, integrates the invariant into production C++, and emits a
canonical `AnonSync/` release root with current revision metadata.

### B. Releasing an owner reopened capability-free mutation

Severity: authority laundering.

The prior recipient policy required exact capability while an owner row was
held, but accepted empty capability after the row became `released`. A caller
could therefore activate ownership, release, and continue mutation as if no
owner had ever existed.

Correction: a separate durable owner-mode row records that the session crossed
the owner boundary. Release preserves `owner-required`, advances its timestamp,
and leaves the latest generation unchanged. Empty capability is rejected after
release; a database-minted successor is required.

### C. Checkpoint-root reset cascaded away ownership history

Severity: generation rollback / authority laundering.

The owner row is a child of `sync_session_checkpoints` with `ON DELETE CASCADE`.
The domain directly deleted the root during checkpoint replacement. The cascade
removed the only generation evidence, allowing a replacement root to appear
never owned and allowing a later acquisition to restart at generation 1.

Correction: `sync_session_checkpoint_owner_modes` has no foreign key to the
checkpoint root. It survives the real cascade and stores the latest generation.
A post-reset successor receives exactly `latest + 1`.

### D. Operator repair had no successor authority

Severity: integration bypass pressure.

Once sticky mode was correctly enforced, the recovery workflow and standalone
repair CLI failed because they mutated after release without acquiring a
successor. The unsafe response would have been to add another unowned exception.

Correction: the database mints a scoped internal repair-owner lease. The exact
capability is passed to repair recipients and explicitly retired. Workflow,
direct repair, and CLI tests prove acquisition, propagation, exact use, and
release.

### E. Destructive root deletion had the wrong invariant owner

Severity: future bypass risk.

The raw `DELETE FROM sync_session_checkpoints` lived in `sync_domain.cpp`, far
from the focused recipient boundary. Authorization could be preflighted or
omitted independently of the destructive statement.

Correction: root deletion now exists in one focused implementation. It requires
a private `CheckpointRootResetPermit` issued after recipient verification in
the exact typed write transaction. The permit is non-default-constructible,
noncopyable, nonmovable, single-use, and bound to the transaction-generation
lease, database handle, session, mode snapshot, and reset epoch. The source
audit rejects direct root-delete SQL in the domain.

## Refactor performed

The refactor is an ownership correction rather than a cosmetic file split:

```text
sync_domain.cpp
  owns orchestration and one typed transaction
      |
      v
sync_checkpoint_owner_fence.cpp
  owns durable mode interpretation, capability verification,
  generation mint/release, reset permit, root delete, and proof reload
      |
      v
sync_checkpoint_owner_fence_policy.cpp
  owns pure state-transition decisions
```

The domain supplies the exact `SyncSqliteTransactionAuthority`; it cannot
construct a reset permit. The recipient boundary stores only a weak
transaction-generation lease, so the permit fails closed after commit,
rollback, guard destruction, handle reuse, process change, thread-incarnation
change, or transaction-generation supersession.

The direct checkpoint-root delete has one source owner. The repair authority
lifecycle is represented by a scoped internal type rather than repeated tuples
or reconstructed lock IDs. The public mutation options now carry the exact
capability and explicit observation epoch.

## Proof surface

The focused source audit expanded from 25 to 38 checks. It verifies:

- capability geometry and recipient propagation;
- pure policy dependency direction;
- sticky mode outside the root cascade;
- release preserving sticky ownership;
- private, nontransferable, single-use reset permit shape;
- exact typed transaction binding;
- a single root-delete owner;
- typed RAII replacement ordering;
- no forgeable production administrative-disable API;
- durable generation mint and compare-and-replace;
- exact post-write proof reload;
- scoped operator repair acquisition and retirement;
- recipient checks for every discovered mutation family;
- write reservation across filesystem effects;
- adversarial focused tests, full-domain lifecycle tests, CTest registration,
  no-core focused linkage, and sanitizer graph coverage.

Behavioral evidence:

- policy: 39/39;
- SQLite: 39/39, including a real foreign-key cascade and successor mint;
- domain: 594/594;
- complete CTest: 86/86;
- ten repeated focused pairs: 780 assertions;
- strict GCC/Clang compile: 8/8;
- focused ASan/UBSan: 2/2 binaries, 78/78 checks.

## Review of failure ordering

The destructive path now orders authority as follows:

1. enter an immediate typed write transaction;
2. prove the exact transaction-generation authority;
3. load/backfill mode and owner evidence on that SQLite snapshot;
4. authorize the exact capability and observation epoch;
5. issue a private reset permit containing the reviewed durable snapshot;
6. delete the root, allowing the owner-child cascade;
7. compare-and-replace the independent mode timestamp;
8. reload exact mode evidence;
9. repopulate the checkpoint root and related rows;
10. commit the same typed transaction.

Any exception before commit rolls back both root deletion and mode update.

## Remaining high-risk gaps

### Exact sticky-mode schema identity

`CREATE TABLE IF NOT EXISTS` creates the reviewed definition on a new database,
but does not prove the identity of a preexisting object. Runtime row decoding
and pure policy checks reject many malformed substitutions, yet the table SQL,
column storage geometry, constraints, and absence of unexpected triggers are
not independently attested. The project already contains a reusable schema SQL
canonicalizer and exact-attestation patterns in the peer-ingress boundary. The
next revision should extract/reuse that narrow facility and pin this table
before interpreting it as authority.

### Administrative disable is a modeled state, not a complete protocol

The pure policy recognizes a canonical-shaped disable evidence ID and permits
empty capability in that state. Production exposes no transition that writes
it, which prevents accidental API disable in this revision. A future transition
must verify real administrative authorization, bind the prior generation and
policy epoch, append an audit record, define reactivation rules, and survive
crash/replay. A prefix plus digest shape is not itself authorization.

### Cooperative time

Observation, lease, release, and reset epochs remain caller supplied. Geometry,
regression, expiry, overflow, and SQLite signed-integer bounds are checked, but
there is no trusted clock or distributed lease oracle.

### Local serialization only

`BEGIN IMMEDIATE` and recipient-side verification serialize compliant users of
the same SQLite database/VFS. They do not establish consensus across devices or
independent stores and do not defend against an actor that can arbitrarily
rewrite the database.

### Database/filesystem crash atomicity

Holding the writer reservation across a filesystem effect prevents compliant
takeover interleaving, but SQLite commit and file write/rename/sync are not one
atomic crash boundary. A crash-cut oracle remains required.

### Retention

Sticky mode intentionally outlives checkpoint roots. This preserves safety but
also preserves session ownership history. A deliberate retention, archival,
and administrative retirement policy is required before unbounded production
operation.

### Mission-level missing work

No executable convergence algebra, exhaustive crash-cut oracle, remote protocol
proof, anonymity design, payload encryption protocol, metadata leakage model,
forward secrecy, post-compromise recovery, or complete key lifecycle is claimed.
