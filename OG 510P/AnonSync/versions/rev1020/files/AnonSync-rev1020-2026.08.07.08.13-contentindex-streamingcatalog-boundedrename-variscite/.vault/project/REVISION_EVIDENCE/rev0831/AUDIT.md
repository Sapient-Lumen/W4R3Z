# Rev0831 audit — a crash child is a new evidence boundary

## Mission-level finding

AnonSync is an evidence-authorized convergence engine. The same rule applies to
its proof machinery: a crash-test child is not trustworthy merely because
`fork()` returned a PID and the parent later observed an exit code. The child
must start from an explicit process boundary, reconstruct the exact evidence it
is authorized to use, expose no accidental inherited capability, and be owned
until it is reaped.

The focused reset and combined reset/receipt crash-frontier executables violated
that rule. They called `fork()` and then ran ordinary C++, filesystem machinery,
and SQLite-related production choreography directly in the child. In a
multithreaded process, the post-fork image contains one surviving thread plus
copies of mutexes and runtime state that may have been owned by vanished
threads. POSIX permits only async-signal-safe operations before successful
`exec`. SQLite separately warns not to use, or even close through SQLite, a
connection inherited from the parent.

The old corpus usually passed because its fixtures were small and the current
runner happened not to expose the latent state. Passing was not authority for
claiming a sound crash boundary.

## Refactor

Rev0831 adds one Linux test-only process owner:

- `tests/self_exec_test_process.hpp`;
- `tests/self_exec_test_process.cpp`; and
- `tests/self_exec_test_process_test.cpp`.

The owner uses `posix_spawn()` on the canonical `/proc/self/exe` object. It does
not search `PATH` or trust `argv[0]`. A versioned argv instruction is constructed
under explicit count, per-argument, aggregate-argv, and environment byte
budgets. The environment is rebuilt from `LC_ALL=C`, `TZ=UTC`, and a narrow set
of sanitizer/symbolizer variables needed to preserve diagnostics in instrumented
lanes.

A GNU/Linux `posix_spawn_file_actions_addclosefrom_np(..., 3)` action closes all
nonstandard descriptors in the child image. The parent intentionally opens and
observes a non-`CLOEXEC` sentinel before every spawn, so descriptor sanitation
is executable evidence rather than an assumption about an incidentally clean
parent. `closefrom` also avoids the enumerate-then-spawn race that would remain
if a multithreaded parent closed only descriptors seen in `/proc/self/fd`.

Spawn attributes request:

- an empty signal mask;
- default dispositions for every resettable signal; and
- a child-owned process group whose ID is the helper PID.

Every helper begins by independently proving that descriptors 0, 1, and 2 are
open, no descriptor above 2 exists, only allowlisted environment names exist,
locale/timezone evidence is exact, no signal is blocked, and the helper is its
own process-group leader. SQLite and fixture state are opened only after that
boundary check.

## Process authority

`SelfExecTestProcess` is move-only. Exactly one object owns exactly one child
PID. A monotonic bounded wait accepts only a requested normal byte-sized exit
status. Timeout, unexpected `waitpid()` failure, move assignment over an
existing owner, and destructor cleanup all kill the isolated process group and
synchronously reap the leader before authority is cleared.

The executable oracle now proves **11 checks**, including:

- exact helper entry and exact exit;
- move construction without duplicated ownership;
- destructive move assignment that kills/reaps the prior helper before taking
  replacement authority;
- timeout kill/reap;
- destructor kill/reap;
- missing executable denial; and
- oversized argument denial.

The self-exec source audit enforces **28/28** structural obligations so the
runtime behavior cannot silently devolve into a raw post-fork path.

## Exact evidence rebinding

The migrated reset helper accepts one versioned, fixed-shape instruction. After
exec it verifies the process boundary, reopens the fixture, and binds the exact
state and receipt digests selected by the parent before running any fail-stop or
commit-before-report-loss choreography.

The migrated combined crash-frontier helper separately binds:

- normalized absolute fixture root;
- canonical case component;
- expected state digest;
- expected receipt digest;
- request digest; and
- reviewed publication cutpoint index, when present.

Publication cutpoint API names contain underscores, while fixture components
intentionally accept only canonical hyphenated names. The first rebuilt run
caught that mismatch. Rev0831 converts the reviewed cutpoint name to a fixture
component instead of broadening the path grammar.

The existing behavioral oracles remain unchanged in size and meaning:

- reset: **68/68 checks**; and
- combined reset/receipt crash frontier: **462/462 checks**.

## Structural audit result

- self-exec process boundary: **28/28**;
- SQLite reset: **102/102**;
- combined crash frontier: **20/20**;
- reset receipt: **42/42**;
- reset receipt protocol: **29/29**;
- atomic publication: **39/39**;
- aggregate focused source obligations: **260/260**.

## Broader audit

A syntax-aware lexical inventory finds **22 actual raw `fork()` calls in 13 C++
translation units** after this revision. The inventory distinguishes tests that
must observe inherited process-incarnation authority from children that create
all relevant state after fork and should therefore migrate to self-exec.

The most wasteful remaining cluster is five raw-fork children embedded in
`src/sqlite_replay_ledger.cpp`'s production-linked selftest tail. Other high
priority migrations are payload-store crash testing, atomic-publication
cutpoints and contenders, and peer-ingress schema attestation. The allocator
fault worker already execs and should use `posix_spawn` file actions directly.

See `inventory/RAW_FORK_INVENTORY.md` and `.json` for the exact line-level
classification.

## Claim boundary

This is test infrastructure and proof-surface hardening; no production behavior
is claimed to change. `posix_spawn_file_actions_addclosefrom_np` is a GNU/Linux
extension and the runtime corpus is Linux-only. The helper is not a hostile-input
sandbox: it does not set namespaces, seccomp, Landlock, credentials, resource
limits, or a parent-death signal. It proves a narrow child process boundary for
reviewed test instructions.

A clean self-exec boundary does not model arbitrary SQLite VFS faults, torn or
reordered writes, kernel crash, power loss, dishonest storage, or one atomic
transaction spanning SQLite and a receipt file. It also does not prove Windows
behavior, distributed convergence, confidentiality, anonymity, metadata hiding,
key lifecycle, or secure erasure.
