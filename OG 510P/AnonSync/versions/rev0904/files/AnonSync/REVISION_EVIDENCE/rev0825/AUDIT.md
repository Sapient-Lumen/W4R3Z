# Rev0825 audit

## Boundary selected

Rev0825 reviews the transition between an already authorized SQLite reset and
its externally visible receipt. The invariant is:

> One durable reset event has one canonical document. Publishing that immutable
> evidence may create one previously absent name, but may never destroy or
> replace an object owned by another actor. Early observations may deny work;
> only an atomic no-replace transition authorizes publication under races.

## Severe parent defects

Receipt v3 mixed event evidence with attempt-local observations. Its bytes
changed between `Committed` and `AlreadyCommitted`, between connection owner
generations, and after legitimate later writes toggled
`state_advanced_after_commit`. The database transition was idempotent, but its
supposedly durable evidence was not canonical.

The reset CLI also used the ordinary replace-existing report publisher. Alias
checks prevented direct damage to the ledger family and request, but did not
protect an unrelated regular destination created after preflight. A successful
rename could erase that object even though it carried no reset authority.

## Corrected authority flow

The command now parses and exactly validates the digest-pinned request, rejects
ledger/request aliases, renders the entire canonical receipt, and performs a
non-mutating create-new preflight before reset. The receipt bytes are fixed
before destructive authority is consumed.

The reset owner then either commits the exact transition or recovers the prior
commit. Only afterward does the CLI invoke immutable publication. The publisher
reopens and revalidates the parent chain, reserves a private unique temp inode,
writes and syncs the complete payload, revalidates temp and parent identity,
checks the final entry, closes the writer, then executes an atomic no-replace
rename relative to the same pinned directory descriptor. The directory is
synced and parent identity is rechecked after publication.

Preflight is deliberately not called a reservation. A competitor can create the
name after it. Linux `RENAME_NOREPLACE` is the decisive authority, and failure
preserves the competitor. Unsupported POSIX platforms fail closed rather than
emulating create-new as check-then-rename.

## Refactor ownership

Canonical reset documents moved from `runner.cpp` into the focused
`anonsync_sqlite_replay_ledger_reset_documents` library. The durable serializer
has exactly two semantic inputs: validated request semantics and exact request
bytes digest. The state report remains distinct because connection generation is
legitimate observation metadata but not durable-event identity.

The CMake graph excludes the documents owner from the aggregate core glob,
links it in one direction, and rejects focused-test regressions into core. The
release verifier now requires the owner, focused test, and source audit.

## Executable and structural proof

- documents byte contract: 18/18;
- atomic publication runtime corpus: 38/38;
- caught/crash/race publication cutpoints: 149/149;
- reset owner: 67/67;
- CLI reset/recovery/occupied-name/symlink oracle: 380/380;
- atomic publication audit: 34/34;
- reset audit: 99/99;
- receipt/publication audit: 36/36;
- load-authority audit: 28/28.

The race oracle places a distinct regular file at the final name after the last
pre-publication name check. Create-new publication fails, reports the exact
pre-publication outcome and possible temp residue, and preserves both inode and
bytes. Separate cases prove an already occupied regular file and symlink deny
before reset, while exact recovery to a different fresh name emits byte-identical
receipt bytes without deleting post-reset work.

## Broader audit observations

The raw variadic `syscall` route used during initial implementation was unsafe
and unnecessary; the final Linux owner calls the typed libc `renameat2`
interface. No raw `syscall(` remains in the publication owner.

This cloud filesystem returned `EEXIST` when a no-replace rename targeted a name
that had just been retired. The protocol does not infer portability from that
behavior and does not rely on name reuse. Recovery explicitly requires a
genuinely distinct absent destination.

The documents extraction removes security-significant JSON construction from a
large CLI file, but `runner.cpp` and the publication owner remain sizeable.
Further extraction should follow invariant ownership, not arbitrary line-count
splits.

## Validation integrity

The exact rev0824 archive and extracted parent pass their own verifier. The
active-source patch applies cleanly to that parent and reproduces all 188 current
active files byte-for-byte. GCC 14 built every target, and a final dependency
closure reported no work. All 109 CTest entries passed across three disjoint
index ranges after final source changes. A single uninterrupted run is not
claimed because longer commands hit the cloud execution ceiling.

Focused GCC ASan/UBSan and Clang 17 warning-as-error graphs each pass the three
new runtime boundaries. The sanitizer claim excludes the full project and
bundled SQLite.

## Explicit limits

No-replace publication prevents replacement at the final transition; it does
not isolate the directory from a hostile same-UID actor before or after that
point. A failed attempt can leave a reported writer-owned temp artifact. The
current tests model process exits and injected exceptions at application
frontiers, not every SQLite VFS, filesystem, kernel, storage-controller, or
power-loss cut. Windows was not executed. Distributed convergence, payload
confidentiality, anonymity, metadata hiding, key lifecycle, and secure erasure
remain outside this revision's proved surface.
