# AnonSync rev0846

## Mission increment

A process-bound capability is still incomplete when its mutable state, lock,
descriptor, or teardown contract belongs to one exact thread lifetime. A native
thread identifier is only an observation and may be reused after termination.
It cannot authorize a later thread merely because the visible number matches.

Rev0846 extracts a generic, opaque thread-incarnation capability and freezes it
into the local JSONL directory, namespace, and open-file owners. SQLite's
existing same-thread mutex generation now delegates to the same leaf. Throwing
operations reject foreign-thread use before observing or mutating protected
state; `noexcept` move/release/destruction violations fail stopped.

The revision also corrects the capability's post-fork implementation and repairs
an incomplete audit universe. The final TLS cache is raw and trivially
destructible, with no emitted TLS guard or destructor-registration machinery on
the recorded GCC and Clang objects. Fork-related source audits now discover
wrapper consumers independently and compare them with one exact 11-target CMake
inventory.

## Severe defects found and corrected

Rev0845 introduced sticky revocation into owners that remained silent about
thread ownership. Sequential foreign-thread use could violate the descriptor
and lock lifecycle; concurrent use, move, or destruction could race ordinary
C++ fields before any fail-closed policy applied. The new thread proof makes the
single-thread contract executable for these owners. It does not claim to make
racing access legal.

The first generic allocator used a function-local static. A child forked while
another parent thread performed first-use initialization could inherit a stuck
initialization guard whose owner no longer existed. The allocator is now
namespace-scope, constant-initialized, and compile-time required to be an
always-lock-free 64-bit atomic.

The first TLS cache stored the public opaque token directly. Despite `constinit`,
the token's intentional non-trivial destructor caused GCC to emit a guard, TLS
destructor, and `__cxa_thread_atexit`. That runtime path is inappropriate for a
narrow post-fork refresh primitive. The final cache stores only raw, trivially
copyable and trivially destructible process/thread words. GCC 14 and Clang 17
object inspection shows no forbidden TLS runtime symbol.

The inherited-process audits had a separate completeness defect: they checked a
handpicked consumer list, so real users of the shared fork wrapper could be
absent from the audited universe. Rev0846 centralizes the exact linked targets
in CMake and makes the source audits independently discover all wrapper sites.
The final inventory proves 11 consumer translation units, 20 spawn sites, one
centralized raw `fork()`, zero production raw forks, and seven fresh-image
campaigns.

## Delivered

- Added `SyncThreadIncarnation`, an opaque one-word process-local proof for one
  exact C++ thread lifetime.
- Removed integer construction/conversion and made the type
  non-trivially-copyable so ordinary numeric, persisted, wire, or `bit_cast`
  evidence cannot be confused with live authority.
- Added a monotonic lock-free allocator with explicit exhaustion fail-stop.
- Added raw, namespace-scope `constinit thread_local` cache state keyed by the
  current process incarnation; inherited bytes are refreshed after an ordinary
  tracked fork.
- Replaced SQLite's private thread-generation allocator with compatibility
  wrappers over the generic leaf.
- Bound `LocalJsonlReplayDirectoryAuthority`, `LocalJsonlReplayNamespace`, and
  `LocalJsonlReplayOpenFile` to exact process and thread incarnations.
- Made foreign-thread throwing rejection preserve the originating owner,
  revocation state, and exact bytes.
- Made foreign-thread `noexcept` access/release/destruction fail stopped.
- Added a 14-check generic thread corpus, including concurrent and sequential
  uniqueness, post-fork refresh, and a fail-stop death probe.
- Extended directory authority to 26 checks and namespace authority to 64
  checks with foreign-thread adversarial cases.
- Replaced incomplete fork-consumer lists with one exact 11-target CMake
  inventory and independently discovered 20 wrapper sites.
- Added or strengthened source audits for generic thread authority, SQLite
  capability composition, process-incarnation representation consumers, raw
  fork ownership, inherited children, self-exec children, and local JSONL crash
  protocol composition.

## Validation

The exact record is in
`REVISION_EVIDENCE/rev0846/validation/VALIDATION_SUMMARY.json`.

The final active source passed a GCC 14.2 Debug all-target build and final
zero-work Ninja closure, all **143 registered tests** in exact non-overlapping
ranges, and all **41 registered source/architecture audits**.

The focused boundary reports **319 direct checks**: thread incarnation 14,
directory authority 26, namespace 64, backend namespace 30, crash state machine
52, and SQLite connection authority 133. The thread test also passes 100
consecutive registered executions.

Clang 17 with `-Werror` and GCC 14 ASan+UBSan with leak detection each pass the
same **319/319** focused checks. Final GCC and Clang objects contain no TLS guard,
TLS destructor, or `__cxa_thread_atexit` reference for the generic thread leaf.
The sanitizer claim is focused; no ThreadSanitizer or full-project sanitizer is
claimed.

## Scope limits

Thread affinity is not synchronization. Callers must not concurrently access,
move, release, or destroy one owner and expect a token check to repair the C++
object-lifetime or data-race violation. A design that requires shared callers
needs an explicit serialized executor or synchronized owner.

The opaque token is domain separation against accidental evidence confusion,
not protection against hostile code already executing inside the process. The
always-lock-free 64-bit atomic is a deliberate platform constraint. Object-level
TLS evidence covers the recorded GCC/Clang ELF x86-64 toolchains, not every ABI.

Ordinary tracked `fork()` refresh is exercised, but `_Fork()` and process
creation that bypasses the process-incarnation hook remain outside the proof.
The narrow refresh path does not make arbitrary post-fork library re-entry safe
in a multithreaded child.

Rev0846 also does not claim filesystem process exclusivity, arbitrary power-loss
completeness, Windows runtime, distributed convergence, payload
confidentiality, anonymity, metadata hiding, forward secrecy, post-compromise
recovery, hostile-parser isolation, or secure erasure.
