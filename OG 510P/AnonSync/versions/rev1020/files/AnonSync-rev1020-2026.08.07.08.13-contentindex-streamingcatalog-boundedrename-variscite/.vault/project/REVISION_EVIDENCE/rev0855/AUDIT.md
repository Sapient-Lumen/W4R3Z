# Rev0855 audit

## Scope

This revision audited the SQLite scoped-mutation authority introduced in
rev0854, with emphasis on type authority, invalid policy representations,
process/thread teardown, NOMUTEX compatibility, callback-slot mutation, and the
accuracy of the structural inventory itself.

## Primary findings

### One type represented incompatible authorities

`SyncSqliteDatabaseMutexGuard` carried an enum policy that selected either a
strict serialized connection or an absent-mutex compatibility lane. The same
type exposed exact-database `authorizes()`, mutex identity, and `release()`. Even
though runtime checks attempted to keep the NOMUTEX path nonauthorizing, the
API surface made authority separation conventional rather than structural.

The enum check rejected only exact equality with `RequireSerialized`; every
other underlying representation was treated as permissive. A corrupted or
cast value therefore selected a weaker policy.

**Correction:** remove the enum, make the guard strictly FULLMUTEX-only, and
represent the raw busy-timeout compatibility path with a separate owner that
has no authority or transfer API.

### Null mutex suppressed lifetime validation

The old destructor returned immediately when `mutex_ == nullptr`. That is the
normal state of the NOMUTEX compatibility lane and the post-`release()` state
of the strict guard. Process and exact-thread checks were placed after that
return, allowing foreign-thread or inherited-process destruction to bypass the
capability violation boundary.

**Correction:** both scoped owners call one shared process-then-thread validator
before examining mutex state. Runtime child-process tests prove the NOMUTEX and
post-transfer cases fail stopped.

### Structural inventory counted prose as code

The busy-handler audit matched `sqlite3_busy_timeout(` before removing line
comments. A documentation comment could be counted as a production API call,
inflating the inventory and making harmless prose changes look like authority
changes.

**Correction:** strip `//` comments before function-call matching. The sole
direct production call is now accurately reported in `sync_sqlite_support.cpp`.

## Resulting authority split

`SyncSqliteDatabaseMutexGuard`:

- requires a non-null serialized/FULLMUTEX connection;
- owns one recursive connection-mutex entry;
- is process- and exact-thread-bound before and after transfer;
- authorizes only the exact `sqlite3*` while it owns the entry; and
- may transfer the entry only through its one-way `release()` operation.

`SyncSqliteBusyTimeoutMutationGuard`:

- is used only by the raw busy-timeout gateway;
- enters the recursive connection mutex when SQLite supplies one;
- admits an absent mutex only under the caller's external single-user contract;
- remains process- and exact-thread-bound even with no mutex; and
- exposes no callback authorization, mutex identity, or transfer operation.

Compile-time concepts and structural audits prevent the narrow owner from
satisfying retained-callback witness interfaces.

## Validation result

- full GCC Debug all-target graph completed;
- immediate final rebuild: zero actions;
- registered tests: **148/148**;
- registered audits: **43/43**;
- focused GCC Debug: **461/461**;
- focused Clang 17 `-Werror`: **461/461**;
- focused GCC ASan+UBSan with leak detection: **461/461**;
- repeatability: **600/600** executable runs, **46,100** aggregate checks;
- focused structural checks: **316/316**;
- parent package verification: **26/26 ZIP**, **22/22 directory**; and
- exact source patch replay: **283/283 active files**.

## Residual risks

The raw busy-timeout overload still accepts a borrowed `sqlite3*`; no guard can
prove that external code obeys SQLite's single-user NOMUTEX contract or refrains
from concurrent close. Foreign code can bypass all reviewed callback-slot
owners by calling SQLite C APIs directly.

The split improves local authority correctness but does not advance the missing
distributed operation algebra, deterministic convergence oracle, privacy or key
protocol, hostile-input worker isolation, or secure erasure story.
