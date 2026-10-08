# AnonSync rev0815 revision notes

## Mission-level result

Rev0815 turns the next layer of SQLite transaction-stack exception composition
into an executable proof surface. The project already owned savepoint identity,
LIFO closure, outer-transaction generation, callback generation, process/thread
incarnation, and retained connection lifetime. This revision asks the harder
question: what remains true when a boundary is denied after an earlier effect,
the caller catches the exception, and then retries or attempts an outer commit?

The concrete production correction removes an application-level allocation
window between the two SQLite effects that implement rollback of a savepoint.
SQLite defines `ROLLBACK TO` as a rewind that leaves the named mark live;
`RELEASE` erases that mark. Rev0814 constructed the RELEASE SQL, diagnostic
label, and a copied callback-permit name after the rollback branch. A C++
allocation failure could therefore interrupt one logical close after the rewind
but before the release attempt. Rev0815 precomputes the complete close plan
before the first effect and borrows the already-stable generated name during the
synchronous authorizer call.

This is a latent split-boundary exception window, not evidence of observed data
loss. SQLite errors can still occur at either SQLite boundary, and those errors
remain deliberately retryable while the exact typed mark is live.

## Exact lineage

The source parent is
`AnonSync-rev0814-2026.07.17.06.21-savepointstack-resetatomic-forkproof-ownershipaudit.zip`
with SHA-256
`cb94168d4115afc9c9b90c5281fe85185c19754ef928452d651688d6e12c3212`.
The exact parent ZIP passes 25/25 package checks and its canonical extracted
`AnonSync/` root passes 21/21. No build output, reconstructed approximation, or
unsealed intermediate was used as source.

## Parent finding

A source-shape reproduction against the exact parent records all five conditions
that created the latent window:

- the live savepoint callback permit owned a copied `std::string` name;
- `SavepointPermitScope` accepted that name by value;
- rollback SQL was built inline;
- release SQL was built inline after the rollback branch; and
- the release diagnostic label was also built inline after the rollback branch.

The reproduction is retained as
`REVISION_EVIDENCE/rev0815/defect_reproduction/parent-allocation-window-reproduction.json`.
It does not claim that a naturally occurring allocator failure was observed.

## Production correction

`ConnectionAuthorityState::savepoint_permit_name` is now a non-owning
`std::string_view`. The view exists only during one synchronous
`sqlite3_exec()` call while the serialized connection mutex is retained, and it
borrows the stable generated name held by the savepoint boundary proof. Permit
revocation clears the view.

A new `FencedSavepointClosePlan` owns the rollback SQL, release SQL, rollback
label, and release label. The complete plan is built after use-time authority
validation and authorizer-ownership probing but before `ROLLBACK TO` or
`RELEASE` executes. The fenced close path then consumes only those prebuilt
objects. Consequently, application C++ allocation is no longer part of the
rewind-to-release interval.

The unfenced compatibility lane remains explicitly observation-based and is not
represented as an exact authority proof.

## Independent exception-composition model

The new 541-line
`tests/sqlite_transaction_exception_composition_test.cpp` maintains its own
transaction/savepoint stack model and differentially checks it against an
in-memory SQLite database. It does not import or mirror the production owner's
private stack state.

A one-shot authorizer cutpoint denies each reviewed boundary in turn. The 37
checks cover denied savepoint begin, denied release, denied rollback-to,
successful rewind followed by denied release, nested LIFO recovery, denied outer
commit, denied outer rollback, caught failures, exact-mark retention, retry, and
outer-commit refusal while an inner mark remains.

The critical partial-effect trace proves the intended retry contract:
`ROLLBACK TO` succeeds, `RELEASE` is denied, the data is rewound while the mark
remains, later work is added, and retrying rollback rewinds that later work
before releasing the same exact mark.

## Audit and refactor result

A new CTest-registered source audit passes 43/43. It binds the production
preallocation ordering, borrowed permit lifetime, CMake registration, sanitizer
participation, seven armed policy cut traces, independent model shape, broad
stack-audit integration, and package-verifier proof surface.

The existing transaction-stack audit was expanded and now passes 86/86. It
hashes the new model, rejects regression to an allocating callback-permit name,
requires close-plan construction before the first SQLite close effect, and
continues to inventory centralized transaction-stack ownership.

The package verifier now requires the reviewed connection owner, transaction
owner, composition model, and both source audits, so a sealed cube cannot retain
CMake references while omitting the proof implementation.

## Source delta and repository shape

Six active files changed: 918 inserted and 10 removed lines. No bundled
third-party source changed. The active implementation projection contains 156
files and 15,614,059 bytes with digest
`2f4433dd281c096dccf58bfc292c2a71c9e39700f2d40743b3c50162f3cb69bf`.

Key final sizes are 1,666 lines in the SQLite connection-authority owner, 358 in
the transaction/savepoint RAII owner, 541 in the independent composition model,
266 in its focused audit, 526 in the broader transaction-stack audit, and 15,371
in `sync_domain.cpp`.

## Validation

- Complete dependency-aware Debug all-target build from the turn's initially
  empty Ninja tree: passed. Changed sources and all affected dependencies were
  rebuilt; a final no-work invocation confirmed closure. Because command-window
  interruptions caused the same tree to be resumed, this is not described as a
  single uninterrupted fresh-build timing result.
- Complete CTest invocation after the final active-source changes: 90/90 in
  31.35 seconds.
- Connection-authority corpus: 133/133.
- Independent exception-composition model: 37/37.
- Focused model/owner/audit CTest lane: 4/4.
- Composition stress: 500 iterations, 18,500 checks, all passed.
- Focused ASan/UBSan: ten repeated owner-plus-model iterations, 1,700 checks,
  all passed.

The sanitizer lane instrumented the changed C++ owner and model in Debug mode.
The exact bundled SQLite object was intentionally reused uninstrumented after an
attempt to rebuild the amalgamation exceeded a command window. Leak detection
was disabled. No bundled-SQLite or full-application sanitizer claim is made.

## Research consequences and next work

SQLite's documented stack semantics support the retry model: `ROLLBACK TO`
rewinds but preserves the mark, while `RELEASE` removes it. SQLite also documents
that selected errors may automatically roll back an outer transaction, so
`sqlite3_get_autocommit()` remains necessary after failure but is only an
observation, not identity evidence.

The next high-value local experiment is an Nth-allocation failure worker that
installs a SQLite allocator overlay before initialization and walks every
allocation cut through begin, rollback-to, release, commit, and rollback. It
should run as a one-shot process because allocator configuration is global and
startup-sensitive. That model should then be paired with a VFS crash-cut oracle
covering journal/WAL writes and AnonSync sidecar/publication artifacts.

The broader unproved mission boundaries remain: executable distributed
convergence algebra; crash consistency spanning SQLite and filesystem effects;
disposable hostile-database interpretation; payload confidentiality; metadata
leakage; device/key enrollment, rotation, revocation, and recovery; forward
secrecy; and post-compromise recovery.
