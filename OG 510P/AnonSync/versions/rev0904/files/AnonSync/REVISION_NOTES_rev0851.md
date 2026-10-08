# AnonSync rev0851

## Mission increment

AnonSync's implemented heart is to turn an observation into the narrowest
process-, thread-, connection-, generation-, lifetime-, policy-, and
resource-bound capability that may authorize one deterministic recoverable
transition. A raw C callback argument is therefore not ordinary plumbing. It is
address-based authority whose referent must remain owned for exactly the period
SQLite may call it, including prepare-time recompilation paths.

Rev0851 applies that rule to the application policy context behind the SQLite
authorizer bridge.

## Severe defect corrected

Rev0850 made the bridge's `ConnectionAuthorityState*` lifetime explicit, but the
public installation overload still accepted an arbitrary non-null `void*`
policy context. SQLite retained the bridge and could invoke it during prepare or
reprepare long after the installing call returned. The connection authority had
no ownership reference to the external object and no way to distinguish live,
expired, stack, moved, or foreign-process storage. A caller could therefore
create a fully generation-bound authorizer whose policy dereferenced dangling
memory.

The same raw context also made retirement order unreviewable. Replacing or
revoking a policy could run user cleanup while SQLite's connection mutex was
held, inviting reentrancy, deadlock, or unbounded application work inside a
low-level critical section.

## Delivered

- Added separately linked `SyncSqliteOwnedAuthorizerPolicy`.
- Coupled one policy callback with an optional `std::shared_ptr<void>` lifetime
  reference while retaining a context-free policy mode.
- Made the owner noncopyable, non-move-assignable, process-incarnation-bound,
  and source-first validating on movement.
- Made inherited-process inspection, invocation, movement, swapping, and
  destruction fail stopped before touching a copied shared-pointer control
  block.
- Kept the compatibility raw installation overload only for `nullptr` context;
  non-null raw contexts are rejected with a directed API error.
- Published new connection state policy-empty so SQLite client-data allocation
  or destructor hazards cannot run application context cleanup.
- On replacement, transferred the old policy into a retirement escrow declared
  outside the mutex guard. Reverse local destruction leaves SQLite's mutex
  before releasing the old context or custom deleter.
- On revocation and typed close, disabled the authorizer, detached its retained
  claim, moved policy into the outer escrow, cleared connection client data,
  left the mutex, and only then released application storage.
- Strengthened state destruction to fail stopped while either the authorizer
  owner or policy owner remains live.
- Added custom-deleter probes using `sqlite3_mutex_try()` from a separate worker
  thread; replacement and revocation both observe `SQLITE_OK`, proving cleanup
  occurs after the connection mutex is released.
- Added 20 focused owner checks and expanded integrated connection authority to
  153 checks.
- Expanded the existing authorizer audit to 35 composed checks rather than
  creating another overlapping audit.
- Corrected the new test after the complete registry exposed a second raw
  `fork()` site. The test now uses the centralized inherited-process harness;
  the exact inventory is again one raw-fork translation unit, 13 inherited
  consumers, 23 wrapper spawn sites, and 30 total process-test sites.
- Made the new owner header, source, and test mandatory in release packages from
  rev0851 onward without invalidating the sealed rev0850 parent.

## Validation

The final active source passes:

- a complete GCC 14.2 C++20 Debug all-target build using Unix Makefiles;
- a final dependency-closure build with zero compile or link commands;
- all **148/148** registered tests in six exact non-overlapping ranges;
- all **43/43** registered structural audits;
- **982/982** direct focused GCC checks;
- Clang 17 `-Werror` focused build and **982/982** runtime checks;
- GCC 14 ASan+UBSan with leak detection and **982/982** focused checks;
- **250/250** repeated focused executions;
- **356/356** focused structural checks;
- sealed rev0850 parent ZIP verification at **26/26** and directory verification
  at **22/22**; and
- exact source-patch replay across **276/276** active files with no missing,
  extra, byte-count, or SHA-256 mismatch.

Exact commands, logs, audit payloads, lineage, source delta, scope, and active
projection are under `REVISION_EVIDENCE/rev0851/`.

## Scope limits

The type-erased owner proves lifetime, not that the callback casts the context
to the correct type. Mutable shared policy state remains responsible for its own
synchronization. Constructing a new owner after `fork()` binds that owner to the
child, but cannot prove that a supplied `shared_ptr` control block was not
created in the parent. Application code should construct and own callback state
before threads and process topology become ambiguous, or re-create it after a
fresh image.

SQLite exposes no getter for the installed authorizer. Named lifetime claims and
nonce probes prove reviewed installation/acquisition boundaries, while arbitrary
foreign raw replacement between probes remains constrained by source inventory.
The close path assumes the exact typed connection owner has quiesced ordinary
users; general concurrent teardown race freedom is not claimed.

No claim is made for ThreadSanitizer, full-project sanitizer coverage,
sanitation of bundled SQLite, Release-mode all-target behavior, Windows runtime
behavior, arbitrary power-loss cutpoints, hostile-input worker isolation,
distributed convergence, payload confidentiality, anonymity, metadata hiding,
forward secrecy, post-compromise recovery, or secure erasure.
