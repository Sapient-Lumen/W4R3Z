# AnonSync rev0806 — domain seam, fixture bridge, and diagnostic build isolation

## Lineage

Rev0806 is derived from the complete uploaded archive
`AnonSync-rev0805-2026.07.16.15.34-falsegreen-hostileforge-selftestsplit-proofsurface.zip`,
SHA-256 `425f17c3bf5e93b230dff213a5acb030b45dfdf3bde1f3179f8fe138ce1a742c`.
The exact parent ZIP passes **25/25** checks in its packaged verifier and contains
43 source C++ implementation files, 31 production headers, and 28 test C++
files. No build product or recovered object tree was used as source lineage.

## Heart of the mission

AnonSync is an **evidence-authorized convergence engine**:

> Make every replicated state transition carry enough owner-verified evidence
> to remain safe under concurrency, replay, crash, compromise, and partial
> failure; reject invalid authority before unrelated valid state is destroyed;
> then prove the authorized transitions converge.

A successful syscall, callback, query, signature, PID comparison, pointer
lookup, returned row, database open, or commit is an observation. It becomes
authority only when the invariant owner verifies the exact bytes, identity,
process incarnation, owner generation, lifetime, policy, relationship, schema,
resource budget, and durability evidence required for that transition.

Rev0806 applies this rule to source ownership: sharing a translation unit is not
an architectural authorization for diagnostics to depend on arbitrary private
runtime machinery, and a passing diagnostic is not a reason to make every
runtime consumer compile its corpus.

## Severe architecture cost in the parent

After rev0805's reporting/selftest split, `src/sync_domain.cpp` remained 24,531
lines. The definition of `run_sync_domain_model_selftest()` began at line
15,811, leaving an 8,721-line tail containing deterministic convergence cases,
filesystem fixtures, hostile databases, recovery workflows, subprocess/lock
scenarios, and direct fixture construction.

Consequences:

1. every normal consumer of `anonsync_core_lib` parsed and compiled the corpus;
2. focused reporting wrappers inherited the domain corpus through the aggregate
   selftest library even though they did not call it;
3. the corpus silently borrowed anonymous-namespace helpers from runtime code;
4. test-only SQLite backup/review helpers lived in the runtime unit; and
5. this 24,531-line object was the sole first-party compile barrier in rev0805's
   attempted full-core sanitizer lane.

The code was functionally valuable. Its ownership and compilation boundary were
wrong.

## Refactor: one diagnostic owner, one explicit private seam

Rev0806 creates:

- `src/sync_domain_selftests.cpp` — the extracted deterministic domain corpus;
- `src/sync_domain_test_access.hpp` — a private, non-installed fixture seam; and
- `tools/audit_sync_domain_selftest_separation.py` — an executable ownership
  audit registered with CTest.

The runtime translation unit now has zero definitions of
`run_sync_domain_model_selftest()` and is 15,840 lines. The diagnostic unit is
8,905 lines. The extra lines are explicit includes, local diagnostic helpers,
checked conversions, and fixture code that was previously hidden by shared-TU
proximity.

### Private fixture bridge

Ten operations needed exact runtime-compatible artifact construction. Rather
than publish them in `include/` or duplicate protocol material, rev0806 exposes a
narrow source-private namespace:

```text
anonsync::sync_domain_test_access
```

Every entry ends in `_for_fixture`. The bridge covers exact staging paths,
receipt paths/material, content/chunk hashing, convergence comparison, staged
chunk and atomic receipt writes, and daemon-owner-lock fixture acquisition. The
bridge header is included by exactly two files: the runtime implementation that
defines the wrappers and the diagnostic implementation that calls them.

The bridge is deliberately a compromise, not a claim of ideal final design. It
keeps the corpus byte-compatible while making borrowed authority visible and
auditable. A future extraction of the underlying invariant owner may replace
these wrappers with a smaller internal production component. Public runtime
headers contain no bridge declaration.

### Test-only helpers left runtime entirely

`sqlite_backup_file_or_throw()` and
`sqlite_sidecar_review_event_metrics_for_session_or_throw()` existed only to
construct or inspect diagnostic fixtures. They now live in the diagnostic
translation unit and are absent from runtime code.

## Build graph correction

The single rev0805 test library is split into two static diagnostic owners and
one interface aggregate:

```text
anonsync_reporting_selftests_lib   -> anonsync_core_lib
anonsync_sync_domain_selftests_lib -> anonsync_core_lib
anonsync_selftests_lib (INTERFACE) -> both diagnostic owners
```

`anonsync_core` links the aggregate. The three deterministic fuzz-named
reporting wrappers link only `anonsync_reporting_selftests_lib`. This matters:
a target should not compile an 8,905-line model merely because another
diagnostic target uses it.

CMake iterates every declared selftest source and configure-fails if any appears
in `ANONSYNC_CORE_SOURCES`. The dependency direction remains diagnostics to
runtime; runtime never links a selftest support target.

### Measured consumer graphs

Representative normal runtime target:

| Metric | Rev0805 | Rev0806 |
|---|---:|---:|
| First-party translation units | 42 | 42 |
| First-party lines | 51,809 | 43,118 |
| Domain diagnostic lines | embedded in core | 0 |

Reduction: **8,691 lines / 16.78%**.

Focused reporting wrapper (`anonsync_fuzz_json_codec`):

| Metric | Rev0805 | Rev0806 |
|---|---:|---:|
| First-party translation units | 43 | 43 |
| First-party lines | 55,392 | 46,701 |
| Reporting diagnostics | included | included |
| Domain diagnostics | embedded in core | excluded |

Reduction: **8,691 lines / 15.69%**.

## Compile-cost evidence and its tradeoff

Direct sequential GCC 14 object compiles using the same Debug-equivalent flags
measured:

| Unit | Lines | Wall | Peak RSS | Object bytes |
|---|---:|---:|---:|---:|
| Rev0805 combined domain | 24,531 | 16.54 s | 1,014,224 KiB | 12,889,776 |
| Rev0806 runtime domain | 15,840 | 11.43 s | 690,412 KiB | 10,425,424 |
| Rev0806 diagnostic domain | 8,905 | 10.90 s | 716,164 KiB | 5,720,872 |

For normal runtime consumers, the dominant compile is 30.89% faster in this
sample, uses 31.93% less peak memory, and emits a 19.12% smaller object. The
largest split job uses 29.39% less peak memory than the parent monolith.

There is an honest cost: serially compiling both split units took 22.33 seconds,
35.01% longer than compiling the parent monolith. Header parsing and template
work are repeated. The revision therefore claims lower ordinary-consumer cost,
lower per-job memory, correct ownership, and independent scheduling—not lower
total diagnostic compile work.

### Compiler trace: where the next seam actually is

Clang 17 `-ftime-trace` profiles were captured for both final units. The runtime
compile's `ExecuteCompiler` event was 8.01 seconds; the diagnostic unit's was
5.01 seconds. Trace events overlap and are not additive wall-time accounting,
so they are used only to rank future work.

The largest named runtime parse events cluster around checkpoint control-plane
functions: operator status (74.6 ms), scheduler execution (63.2 ms), scheduler
planning (62.7 ms), fake-peer session execution (61.3 ms), and the daemon loop
(53.0 ms). This is stronger evidence for a future checkpoint scheduler/operator/
daemon invariant owner than another arbitrary file-length cut.

The extracted diagnostic remains structurally concentrated: the single
`run_sync_domain_model_selftest()` function accounted for a 755.0 ms parse
event, a 910.9 ms function-optimization event, and a 297.1 ms code-generation
event. Its next refactor should split scenario-owned functions while preserving
one public entry point and one aggregate result.

## Strict-compiler corrections found during extraction

Clang 17 with `-Wconversion -Wsign-conversion -Wshadow -Werror` exposed eight
inherited signedness hazards that the parent warning set did not reject.

Corrections:

- byte-classification loops iterate `char` and explicitly convert each element
  to `unsigned char` before ctype or portable-byte policy checks; and
- unsigned fixture values pass through a checked helper before conversion to
  the signed integer type used by CLI argument construction.

Both changed units now pass the strict Clang lane and GCC 14
`-O3 -DNDEBUG -Werror` syntax/optimization analysis.

## Machine-enforced boundary

The new sync-domain audit passes **13/13** and verifies:

1. no domain-model selftest definition remains in runtime;
2. exactly one definition exists in the diagnostic unit;
3. CMake gives the diagnostic source one named support owner and excludes it
   from the core source set;
4. every diagnostic source is guarded against core reabsorption;
5. dependency direction is diagnostic support to runtime;
6. focused reporting wrappers do not inherit the domain corpus;
7. the fixture bridge is source-private and has exactly two include users;
8. public runtime headers expose no fixture authority;
9. bridge declaration and definition sets match;
10. all bridge entry names explicitly say `_for_fixture`;
11. test-only SQLite fixture helpers are absent from runtime;
12. the production unit is materially below the parent boundary; and
13. diagnostic calls qualify the fixture namespace explicitly.

The broader runtime/selftest audit now passes **9/9**. CLI help and CTest remain
in exact **38/38** selftest parity.

## Validation

### Required debug gate

- GCC 14.2.0
- C++20
- Debug
- bundled SQLite 3.53.3
- `-Wall -Wextra -Wpedantic -Werror`
- complete current final build graph passed and is up to date
- a separate final from-scratch attempt was interrupted by shared-container
  contention after 29/127 steps; it is not represented as a pass
- full CTest: **81/81 passed**
- domain-model diagnostic: **588/588 checks**

### Sanitizer scope

Rev0805 could compile every first-party ASan/UBSan object except the combined
`sync_domain.cpp`. In rev0806, the 15,840-line production domain unit compiles to
an instrumented 34,403,560-byte object with ASan and UBSan references. This
clears the exact production compile barrier identified in the parent.

A complete instrumented executable is not claimed. Reconfigured full-build and
direct diagnostic-object attempts did not finish within bounded command windows
in the shared 4 GiB/no-swap cloudtainer while unrelated large compiler jobs were
also active. The diagnostic object, final link, runtime execution, and leak
detection therefore remain unproved. The logs are preserved rather than
converted into a false-green sanitizer claim.

## Deep audit: what still matters most

### 1. Extract an invariant owner, not just another tail

The remaining runtime domain file is still 15,840 lines. Its next production
split should follow the trace-backed checkpoint scheduler/operator/daemon
control plane, with a narrow internal API, explicit transaction and lease
authority, focused tests that do not link the entire core, generated adversarial
cases, and graph evidence.

### 2. Turn the 588-case corpus into an executable convergence oracle

The corpus is broad, but breadth is not a convergence algebra. Durable
operations still need explicit classification as commutative/order-sensitive,
idempotent/single-use, monotone/retracting, causally independent/dependent, and
epoch-compatible/barriered. A compact independent model should generate
permutations and differential-check the C++ implementation.

### 3. Build a crash-cut/domain-state oracle

SQLite's integrity and transaction outcome are only part of AnonSync's durable
state. The oracle must jointly classify database, WAL/journal, receipts,
sidecars, checkpoints, staging files, renames, and externally visible effects
after every injected cut.

### 4. Reduce raw SQLite interpretation surface

The source tree now contains 747 lexical raw SQLite calls: 590 in runtime source
and 157 in the two diagnostic owners. A machine-readable migration ledger should
classify new calls and drive high-risk row interpretation, lifetime, callback,
and transaction boundaries toward typed owners.

### 5. Keep privacy claims separate from authentication

Nothing in this structural revision changes the prior conclusion: the reviewed
code demonstrates substantial authentication/replay/persistence work, not a
complete payload-encryption, metadata-hiding, anonymity, forward-secrecy, or
post-compromise-recovery protocol. The product name must not substitute for a
threat and leakage model.

## Sealed evidence

`REVISION_EVIDENCE/rev0806/` contains exact lineage, source delta, machine
audits, parent/current build graphs, compile measurements, full CTest output,
strict compiler logs, sanitizer attempt limits, repository metrics, online
research, the active implementation projection, and package verification
inputs.
