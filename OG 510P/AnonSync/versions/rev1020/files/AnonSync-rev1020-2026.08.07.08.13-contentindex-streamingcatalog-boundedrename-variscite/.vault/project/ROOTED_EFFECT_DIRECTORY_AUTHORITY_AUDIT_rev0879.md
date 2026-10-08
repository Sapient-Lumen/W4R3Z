# AnonSync rev0879 — retained root authority, descriptor-relative effects, and directory-owner refactor

## Executive finding

AnonSync's heart remains **authority accounting under crash, concurrency,
partial trust, duplication, reordering, resource pressure, and ambiguous
response**. The system is not made correct merely because a path is normalized,
a TLS peer was authenticated, a SQLite row committed, or a rename returned
success. Each of those is an observation or transition with a bounded authority
scope. The mission is to preserve that scope end to end so descriptive state can
never silently become causal, filesystem, or settlement authority.

Rev0878 completed a narrow effect-terminal File path but left its most severe
filesystem gap explicit. The concrete risk was a same-path directory replacement:
`SyncReplicaFileEffectSqliteOwner` persisted normalized
root-path text and reopened that pathname during each materialization. The
single-call atomic publisher protected its terminal parent well, but the owner
had no process-lifetime identity for the configured root. A same-path directory
replacement between calls could redirect a later otherwise-valid publication
into a different tree while the database still contained the original spelling.

Rev0879 corrects that boundary on POSIX. The effect owner now mints one retained,
process- and thread-affine `SyncDirectoryAuthority`, freezes kernel-visible root
identity and mutation policy, persists a canonical authority digest in exact
schema version 2, and performs effect reconciliation and publication by walking
relative components from a duplicated retained root descriptor. Replacing the
configured path does not redirect work. It revokes the live capability, and a
restart against a different root identity fails before accepting the existing
database.

The same work also removes a duplicated security state machine. The older local
JSONL directory authority now delegates to the generic owner rather than
maintaining separate traversal, attestation, move, fork, thread, and sticky-
revocation code. One reviewed C++ leaf now owns this class of directory
capability.

The corrected focused path is:

`live authenticated channel capability → exact causal/effect cutpoint → retained`
`root capability → strict canonical relative path → descriptor-relative parent`
`traversal → descendant mutation-policy proof → immutable temp/write/fsync →`
`no-replace rename → directory fsync → rooted exact reconciliation → root-bound`
`effect database cutpoint → terminal receipt`

This remains a correctness slice rather than a shipped synchronization service.

## Mission invariant

> Given the same authorized canonical evidence and trust state, independent
> replicas must derive the same state; no untrusted bytes, pathname spelling,
> missing dependency, stale projection, stale receipt, clock observation,
> duplicate, crash frontier, schema mutation, namespace rebind, mount crossing,
> resource decision, retry response, summary, or migration shortcut may silently
> manufacture authority.

For filesystem effects, the invariant implies several distinct identities:

1. The **configured path spelling** is operator policy and part of the durable
   namespace contract.
2. The **opened root directory object** is the object beneath which one process
   may attempt effects.
3. The **relative operation path** is canonical operation evidence and must not
   be reinterpreted as an absolute or parent-traversing path.
4. The **opened destination parent** is the exact namespace mutation authority
   for one publication attempt.
5. The **published file object and exact bytes** are effect evidence.
6. The **effect database cutpoint** records that evidence only after rooted
   reconciliation, and a terminal receipt is emitted only after a post-mark
   reproof.

A path string cannot substitute for an opened object. An opened object cannot by
itself prove that the configured path still names it. A successful rename cannot
by itself prove directory durability. A durable file cannot by itself prove the
operation remains the authorized active projection. Rev0879 keeps these claims
separate and composes them explicitly.

## Concrete defect in rev0878

Rev0878 normalized `root_path`, persisted that text, and derived a destination as
`root_path / canonical_relative_path` when materializing. Atomic publication
then opened and retained the destination parent for that one call. This protected
against a rebind during the call, but not against a root replacement before the
call began.

A minimal hostile sequence was:

1. construct an effect owner for `/owned/files`;
2. stage exact payload evidence in its SQLite database;
3. rename `/owned/files` to `/owned/displaced`;
4. create a fresh directory at `/owned/files`;
5. invoke `stage()` or `materialize()` again;
6. observe that old code regarded the new object as the configured tree because
   its path text was unchanged.

This is not merely a cosmetic configuration change. The effect publication
digest and complete SQLite cutpoint claimed one namespace root while the actual
mutation could occur beneath another object. The mismatch undermined the meaning
of an effect-terminal receipt.

Lexical containment was not an adequate correction. A normalized destination
would still be lexically beneath the same text after replacement. Re-running
`canonical()` would merely authorize whichever object occupied the path at that
moment. The correction had to retain object identity and make the path/object
relationship a re-proved capability condition.

## Shared `SyncDirectoryAuthority`

### Capability shape

`SyncDirectoryAuthority` is a move-only POSIX capability. At minting it records:

- process incarnation;
- thread incarnation;
- normalized absolute path spelling;
- one retained directory descriptor;
- device and inode;
- owner UID and GID;
- effective UID and GID;
- permission mode;
- filesystem identifier;
- mount flags;
- filesystem `NAME_MAX`; and
- descriptor-relative name limit.

The class is noncopyable so descriptor authority cannot be duplicated by an
ordinary value copy. A deliberate internal friend duplicates the descriptor for
one rooted publication or reconciliation attempt, with root reproof both before
and after duplication. No public raw-descriptor accessor was added.

The object is process-incarnation-bound. Inherited use after `fork()` fail-stops
before the descriptor can authorize filesystem mutation. It is also thread-
incarnation-bound. Throwing APIs reject a foreign thread; `noexcept` accessors
fail-stop rather than returning capability-bearing state from the wrong thread.
Move transfers preserve the original authority identity, and moved-from objects
cannot be reused.

### Initial traversal

Minting requires an absolute path with no lexical `..` component. The
implementation begins at an opened `/` descriptor and processes each path
component separately:

- inspect with `fstatat(..., AT_SYMLINK_NOFOLLOW)`;
- reject symbolic links and non-directories;
- open with `openat()` using `O_DIRECTORY`, `O_CLOEXEC`, and `O_NOFOLLOW` where
  available;
- inspect the opened descriptor with `fstat()`; and
- require the inspected and opened device/inode pair to match.

The terminal descriptor is retained only after the complete traversal. This
avoids the classic check-then-open pathname substitution in which an inspected
component is replaced before the actual open.

The Linux `open(2)` documentation explicitly recommends directory file
descriptors for this class of problem: they avoid races caused by changing path
prefixes, remain stable if the directory is renamed, and pin the underlying
filesystem while held. Those properties explain why the rev0878 path-string
model was insufficient and why rev0879 uses an object capability.

- https://man7.org/linux/man-pages/man2/open.2.html

### Mutation policy

Root authority is minted only when the terminal directory:

- is owned by the current effective UID;
- grants owner read, write, and search permission;
- grants neither group nor other write permission; and
- is not reported on a read-only mount.

This is deliberately narrower than claiming exclusive process ownership. A
second process under the same UID, a privileged process, mutable ancestor
authority, ACLs or security mechanisms not represented by these observations,
and hostile code inside the same process remain outside the proof. The class
comment states those exclusions.

### Reproof and sticky revocation

Every `verify_or_throw()` checks both sides of the authority relation:

1. `fstat()` and filesystem attestation of the retained descriptor must still
   exactly equal the frozen attestation; and
2. component-wise no-symlink traversal of the configured absolute path must
   reach the same exact attestation.

A changed mode that remains superficially safe still fails because the
capability was minted for one frozen observation. A widened group-write bit
fails policy immediately. A renamed/replaced path fails identity. Any failed
reproof permanently sets `revoked_`. Restoring the old path or mode does not
resurrect an object after an interval the process could not observe.

Sticky revocation is important because point-in-time checks cannot prove that no
change-and-restore occurred between calls. Once the process actually observes a
contradiction, continuing would turn incomplete history into authority.

### Durable attestation digest

`sync_directory_attestation_digest_or_throw()` domain-separates and serializes
all frozen scalar observations in big-endian form under
`anonsync-sync-directory-attestation-v1`, then produces SHA-256 hex. The effect
owner stores the path spelling separately and binds both path and authority
digest into its complete cutpoint.

Including effective credentials and mount observations is intentionally strict.
A restart under a different execution identity or changed mount observation does
not silently inherit old effect authority. An explicit future migration or root
rebind protocol can relax that rule only by naming and authenticating the old and
new authorities.

## Refactor: one directory owner instead of two

Before rev0879, the local JSONL replay backend contained its own large directory
capability implementation. It already had valuable behavior: no-symlink
traversal, retained descriptor identity, owner/mode policy, process and thread
affinity, and sticky revocation. The new file-effect root needed nearly the same
boundary.

Copying that implementation would have been expedient and wrong. Every future
fix for mount handling, descriptor flags, process inheritance, or attestation
would need to land identically in two syscall state machines. Divergence would
be likely, and source audits could create a misleading appearance of coverage by
checking two similar vocabularies.

Rev0879 extracts the behavior into `SyncDirectoryAuthority`. The local JSONL
class remains as a thin compatibility facade because its name is part of the
existing internal API. It aliases the generic attestation and delegates open,
path access, verification, raw descriptor access for its namespace friend, and
name-limit access. The wrapper contains no `open`, `openat`, `fstatat`, retained
descriptor, attestation, or revocation state machine.

This is the audit/refactor portion of the revision: it reduces the number of
security boundaries while preserving the older runtime matrix. The JSONL tests
still exercise move behavior, permission drift, path rebinding, symlink denial,
foreign-thread rejection, foreign-thread fail-stop access, fork inheritance
fail-stop, and parent continued use. They now also verify deterministic
attestation hashing and sensitivity to identity change.

## Descriptor-relative immutable effects

### Strict relative-path contract

The rooted atomic APIs accept `SyncDirectoryAuthority` plus one already
canonical relative path. They reject:

- empty paths;
- absolute paths;
- root names or root directories;
- empty components;
- `.` and `..`;
- embedded forward or backward separators;
- NUL bytes; and
- a spelling whose lexical normalization differs from the supplied path.

This validation is intentionally repeated at the composition boundary even
though canonical operations are validated earlier. The rooted publisher is a
separate public C++ boundary and must not assume every future caller preserved
the upstream invariant.

### Root descriptor duplication

The atomic-publication implementation is an explicit friend of the generic
authority through a narrow internal access class. It:

1. re-proves the root;
2. retrieves the private retained descriptor;
3. duplicates it with close-on-exec semantics; and
4. re-proves the root again before returning the duplicate.

The duplicate owns only one attempt. Closing it cannot invalidate the
process-lifetime root owner, and retaining it across a pathname rename cannot
redirect the attempt into a replacement tree.

### Relative parent traversal

Each destination parent component is resolved with `fstatat(...,
AT_SYMLINK_NOFOLLOW)`, `openat(..., O_DIRECTORY | O_NOFOLLOW)`, and an exact
post-open device/inode comparison. No relative component is reopened by
concatenating the configured absolute path.

Every opened descendant directory must also:

- remain on the retained root's `st_dev`;
- be owned by the retained root's effective UID;
- grant owner read/write/search; and
- deny group/other write.

This second policy was found during the rev0879 adversarial pass. A retained root
alone prevented redirection at the root boundary, but a group-writable
intermediate directory still gave another mode class namespace mutation
authority beneath that root. The first implementation would have opened it. The
corrected traversal rejects it before reserving any temporary inode.

At the end of traversal, the root is re-proved. Before temp reservation, before
rename, and after parent-directory synchronization, the terminal relative parent
is re-opened from the root and compared to the retained terminal parent
descriptor. Thus a parent rebind cannot redirect a live attempt.

### One publication state machine

Rev0879 does not create a second atomic-write protocol. The POSIX publication
core now accepts a verifier callback. Both the older absolute-path caller and the
new rooted caller use the same sequence:

1. verify retained parent;
2. inspect final name without following symlinks;
3. create one private unique temporary inode;
4. enforce private owner/mode/link/type invariants;
5. write all exact payload bytes;
6. synchronize the temporary file;
7. revalidate the temporary pathname and inode;
8. revalidate the destination parent;
9. re-inspect the final name;
10. perform atomic create-new/no-replace publication;
11. synchronize the parent directory;
12. revalidate the parent after synchronization; and
13. close retained descriptors.

Typed failure state continues to distinguish not-published, possibly published
with indeterminate directory durability, and directory-synchronized outcomes.
The rooted wrapper reuses that same progress owner and error classification.

### One reconciliation state machine

Restart reconciliation was similarly parameterized rather than copied. From one
retained parent it classifies the final name as absent, conflicting, or exact and
directory-synchronized. Exact requires:

- a non-symlink regular file;
- effective-user ownership;
- mode 0600;
- one link;
- exact expected size and bytes from a frozen descriptor snapshot;
- stable named/opened inode identity;
- file synchronization;
- parent-directory synchronization;
- rooted parent reproof; and
- stable post-sync file and name identity.

A syscall exception after rename is not treated as proof of failure or success.
The owner reconciles exact durable state and only then advances SQLite effect
authority.

## Effect owner schema version 2

The file-effect database exact schema advances from version 1 to schema version
2. The meta row adds a mandatory 64-character `root_authority_digest`. Complete
state restoration requires:

- exact schema SQL and object inventory;
- expected folder ID;
- exact normalized root path;
- exact root authority digest;
- exact configured limits;
- complete operation/payload reconstruction;
- redundant-field agreement;
- effect-set digest agreement; and
- root-bound cutpoint digest agreement.

The publication digest domain becomes
`anonsync-replica-file-effect-publication-v2`; the complete cutpoint domain
becomes `anonsync-replica-file-effect-cutpoint-v2`. Both bind the root authority
digest, and the cutpoint also binds path spelling, limits, generations, complete
stored effects, canonical operation bytes, payload bytes, state, and publication
evidence.

### Why automatic v1 migration is refused

Rev0879 intentionally does not auto-migrate a version-1 effect database. Version
1 recorded only root path text. On opening an old database, the process cannot
prove whether the directory currently occupying that path is the directory under
which prior effects were staged or published. Automatically computing a digest
for the current object would retroactively manufacture evidence that the old
schema never captured.

The exact-schema verifier therefore rejects v1. A future operator-authorized
migration must explicitly identify the old database, prove or reconcile all
published effects beneath a selected root, name the new root authority, and
record a migration receipt. Availability loss is preferable to silently binding
old terminal receipts to an unrelated tree.

## SQLite and filesystem cutpoints

The effect owner verifies the retained root:

- before schema initialization or existing-database acceptance;
- immediately before those transactions commit;
- before and before-commit for snapshots;
- before stage, before stage mutation, and before stage commit;
- before materialization read and its commit;
- during every rooted reconciliation/publication operation;
- before publication-mark mutation;
- before publication-mark commit; and
- in the post-mark terminal file proof.

These checks do not create an atomic transaction between SQLite and the
filesystem. They instead ensure that every durable database transition is made
while the process holds the expected root capability, while immutable
publication plus restart reconciliation handles the unavoidable cross-resource
crash window.

The safe ambiguity cases are:

- file absent, database staged: retry publication;
- exact durable file, database staged: reconcile and mark published;
- exact durable file, database published: return already-published after fresh
  proof;
- conflicting entry, database staged: return nonterminal conflict;
- missing or conflicting entry, database published: fail closed rather than
  emitting a terminal receipt; and
- root/path contradiction at any point: revoke or reject before further
  authority.

## Adversarial runtime evidence

### Live same-path replacement

A runtime test stages one exact effect, renames the configured root away, creates
a fresh directory at the original path, and then invokes the same owner.

The test proves:

- stage rejects before database mutation;
- materialization rejects before replacement-tree publication;
- snapshot rejects after sticky revocation;
- the replacement tree receives neither final bytes nor a temporary publication
  artifact;
- restoring the original directory path does not resurrect the revoked object;
- a freshly constructed owner against the restored exact inode observes the
  unchanged cutpoint; and
- that fresh owner can complete exact publication under the original retained
  root.

### Restart against a replacement root

A separate test stages an effect, destroys the owner, renames the root, creates a
new directory at the same path, and reconstructs the owner against the original
SQLite database. Exact schema restoration detects the root authority digest
mismatch and rejects construction. The replacement tree remains empty. After the
original root is restored, reconstruction observes the same digest and unchanged
cutpoint.

This proves the correction is not merely a live-descriptor property. Root
identity is durable evidence.

### Shared-writable descendant

A third test makes an intermediate destination directory mode 0770. Rooted
materialization rejects the group/other-writable descendant before creating a
temporary or final entry. The effect database remains staged at the same
generation. After restoring mode 0755, a fresh bounded attempt publishes exact
bytes and marks the effect.

The descendant failure does not permanently revoke the root because the root
itself remains valid and no mutation was attempted. This distinguishes a broken
or administratively repairable child path from a contradiction in the retained
root authority.

### Existing capability matrix

The refactored JSONL test remains load-bearing evidence that the shared class:

- is noncopyable and nothrow movable;
- freezes exact identity and policy observations;
- rejects unsafe initial modes and relative/parent-traversing paths;
- sticky-revokes after mode or path contradiction;
- refuses symlink traversal;
- rejects foreign-thread use without revoking valid owner-thread authority;
- fail-stops foreign-thread `noexcept` access; and
- fail-stops fork-inherited use while preserving the parent's capability.

## Online research and design implications

### Directory descriptors are the correct local primitive

The Linux `open(2)` manual notes that directory descriptors can serve as stable
references to directories, avoid races in prefixes that may be renamed, and keep
a filesystem mounted while the descriptor is open. Rev0879 adopts that object-
capability shape instead of repeatedly resolving root text.

- https://man7.org/linux/man-pages/man2/open.2.html

### `openat2()` can close a remaining Linux mount seam

Linux `openat2(2)` provides resolution policy in the kernel. Relevant flags
include:

- `RESOLVE_BENEATH` to prevent escape above a supplied directory;
- `RESOLVE_IN_ROOT` for chroot-like interpretation beneath one descriptor;
- `RESOLVE_NO_SYMLINKS` and `RESOLVE_NO_MAGICLINKS`; and
- `RESOLVE_NO_XDEV` to reject mount-point crossings, including bind mounts.

- https://man7.org/linux/man-pages/man2/openat2.2.html
- https://man7.org/linux/man-pages/man7/path_resolution.7.html

Rev0879's portable POSIX traversal rejects a descendant whose `st_dev` differs
from the retained root. That catches ordinary filesystem crossings, but it does
not detect a same-device bind mount. A bind mount of another location on the same
filesystem can report the same device number. The next Linux-specific hardening
lane should attempt `openat2()` with
`RESOLVE_BENEATH | RESOLVE_NO_SYMLINKS | RESOLVE_NO_MAGICLINKS |
RESOLVE_NO_XDEV`, fail closed for policy errors, and use an explicitly audited
fallback only when the kernel truly lacks the syscall or flag set.

This should be capability detection, not kernel-version inference. Rev0875
already demonstrated why version numbers do not prove optional kernel behavior.

### `statx()` mount IDs can support durable diagnostics

Linux `statx(2)` exposes `STATX_MNT_ID`, and newer kernels expose a unique mount
identifier. Mount IDs can distinguish mount objects even when device IDs match.
They are useful as additional live evidence and diagnostics for a portable
fallback, although a mount ID alone does not replace kernel-enforced resolution
policy and should not be treated as a long-term cross-reboot identity without a
careful epoch model.

- https://man7.org/linux/man-pages/man2/statx.2.html

### Rename is atomic namespace mutation, not complete durability

`rename(2)` supplies atomic namespace replacement/no-replace mechanisms within
its defined filesystem scope, but an application still needs file and directory
synchronization and must handle errors after the namespace transition. Rev0879
retains the existing typed publication-frontier model and exact restart
reconciliation rather than reducing effect authority to one return code.

- https://man7.org/linux/man-pages/man2/rename.2.html
- https://man7.org/linux/man-pages/man2/fsync.2.html

### Kernel path lookup remains a state machine

Linux kernel documentation describes path lookup as component walking with
complex rename, mount, and symlink behavior. That supports the design choice to
centralize traversal in one small capability owner and to prefer kernel-enforced
resolution flags where available rather than scattering lexical checks across
callers.

- https://docs.kernel.org/filesystems/path-lookup.html

## Audit and refactor findings

`tools/audit_sync_effect_root_authority.py` adds a focused lexical hygiene
inventory. It checks the shape and composition of:

- move-only process/thread-affine retained authority;
- component-wise absolute traversal;
- frozen root policy and digest completeness;
- sticky descriptor/path reproof;
- JSONL delegation without a copied syscall state machine;
- strict relative-path validation;
- descriptor-relative descendant traversal and policy;
- one shared publication and reconciliation protocol;
- effect schema v2 and root-bound digest domains;
- root reproof around SQLite mutations and commits;
- adversarial live/restart/descendant runtime cases;
- CMake ownership and CTest registration; and
- rev0879 package-verifier inventory.

The audit labels itself lexical hygiene, not semantic proof. It can detect a
removed token, reordered obvious call, missing file, or accidental duplicate
owner. It cannot prove syscall behavior, race freedom, digest collision
resistance, SQLite semantics, crash recovery, or runtime process topology. The
C++ tests, compiler lanes, sanitizers, restart tests, stress runs, complete CTest
registry, and package verification remain load-bearing.

Neighboring audits were updated rather than weakened. The atomic-publication
audit now understands the verifier callback shared by absolute and rooted
callers. The local JSONL crash audit follows the generic authority source plus
thin wrapper and explicitly checks that the old wrapper no longer owns duplicate
security state.

### Waste corrected

This revision removes a particularly dangerous kind of waste: duplicated
security code whose apparent modularity increases maintenance cost while
reducing confidence. The local JSONL class had a mature capability model; the
file-effect owner needed the same semantics. Extraction creates one place to
improve mount handling, attestation, process topology, and path traversal.

The broader cube still contains extensive lexical audits and large historical
evidence. Those tools should remain hygiene and provenance, not be mistaken for
runtime product behavior. Future revisions should continue replacing copied
state machines with shared typed owners and generated adversarial runtime
matrices.

## Compatibility and migration

- POSIX file-effect databases use exact schema version 2.
- Version-1 file-effect databases are intentionally rejected; there is no silent
  root-identity migration.
- The file-delivery wire protocol remains version 1.
- The causal SQLite schema remains version 5.
- Existing local JSONL source callers retain the compatibility class and
  attestation name.
- The shared directory authority is POSIX-only.
- Windows continues to bind the effect database to normalized path text and a
  path-derived digest, and rooted descriptor-relative APIs are unavailable.
  Rev0879 therefore does not claim Windows parity.

## Known limitations and deliberate nonclaims

### Same-device mount crossing

The descendant `st_dev` policy rejects obvious device crossings but not a
same-device bind mount. Rev0879 does not claim mount-namespace containment.
Linux `openat2(RESOLVE_NO_XDEV)` or carefully interpreted `statx` mount IDs are
the next hardening direction.

### Point-in-time observations

Root and parent reproofs are point-in-time. Another sufficiently authorized
principal can attempt changes between checks. Descriptor-relative operations
prevent those changes from redirecting a retained descriptor into a replacement
tree; later contradictions fail closed. The system cannot prove the absence of
an unobserved change-and-restore interval without stronger external exclusivity.

### Same-UID and privileged actors

POSIX owner and mode checks do not exclude another process under the same UID or
a privileged actor. Rev0879 claims an owner-controlled mutation surface, not
single-process exclusivity or protection from a compromised account.

### ACLs, labels, and network filesystems

The frozen attestation does not model every ACL, Linux security label, remote
filesystem server behavior, cache mode, or platform-specific durability rule.
A production deployment profile must define supported filesystem classes and
prove its assumptions per platform.

### Cross-resource atomicity

The causal database, effect database, and filesystem remain independent durable
domains. Immutable publication and reconciliation make their ambiguity
recoverable; they do not become one transaction.

### Root reconfiguration

There is no operator-authorized root migration or rebind receipt. Changing root
identity currently causes a safe availability failure. A future protocol should
name old/new path and authority digests, reconcile every terminal effect, require
explicit administrative authorization, and publish a durable epoch transition.

### Windows

Windows has no equivalent retained-root implementation in this revision. Its
path-derived digest prevents accidental configuration mismatch but cannot prove
one stable directory object across calls or restart. Terminal-effect parity on
Windows requires a handle-relative design and independently audited directory
durability semantics.

### Scalability

`SyncReplicaFileEffectSqliteOwner` still restores and re-attests complete effect
history on every operation. It is an O(history) correctness oracle and migration
reference, not a production index. Retaining the root capability does not fix
that throughput cost. A future indexed owner should be differentially tested
against this oracle and must preserve the same root-bound cutpoint.

### Product completeness and privacy

Rev0879 does not add a shipped daemon/service entry point, ordinary updates,
deletes, renames, chunked content transfer, quota fairness, complete retry and
dead-letter policy, membership/key lifecycle, anti-entropy, compaction,
independently signed receipts, anonymous transport, unlinkability, or traffic-
analysis resistance. “Anon” remains a mission requirement, not an implemented
privacy claim.

## Recommended next sequence

1. Add a Linux `openat2()` capability path for relative traversal with
   `RESOLVE_BENEATH`, `RESOLVE_NO_SYMLINKS`, `RESOLVE_NO_MAGICLINKS`, and
   `RESOLVE_NO_XDEV`; test exact fallback classification rather than inferring
   support from kernel generation.
2. Add mount-ID observation for diagnostics and adversarial same-device bind-
   mount tests in a privileged CI lane where mount namespaces are available.
3. Define an explicit, signed/authorized root-epoch migration protocol instead
   of weakening schema-v2 restart matching.
4. Move the retained-root effect owner into the first executable replica service
   so this correctness path is no longer only a test/composition island.
5. Add a production indexed effect owner and run generated differential
   scenarios against the full-history oracle.
6. Extend effect semantics one operation at a time—content-addressed update,
   tombstone, then rename—without weakening terminal receipt meaning.
7. Continue reducing duplicate authority owners and treat lexical audits as
   inventories rather than assurance substitutes.

## Bottom line

Rev0879 closes the root-identity defect it inherited from rev0878 and does so by
reducing, not multiplying, filesystem security machinery. The effect owner now
knows which directory object it is authorized to use, proves that the configured
path still names that object, walks destinations from the retained descriptor,
rejects uncontrolled descendants before mutation, persists the identity in its
exact database cutpoint, and fails closed across live and restart-time
replacement.

The remaining mount, platform, exclusivity, scalability, and product gaps are
explicit. That is consistent with AnonSync's mission: uncertainty and missing
evidence must remain visible rather than being converted into convenient
filesystem or receipt authority.
