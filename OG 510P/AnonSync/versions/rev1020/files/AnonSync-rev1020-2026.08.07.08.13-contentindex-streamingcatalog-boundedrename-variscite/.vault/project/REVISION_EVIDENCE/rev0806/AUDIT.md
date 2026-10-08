# Rev0806 implementation and architecture audit

## Scope

This audit begins from the exact verifier-clean rev0805 archive. It inspects the
complete CMake/source/test graph, extracts and normalizes the embedded domain
selftest body, compiles the affected C++ under strict GCC and Clang lanes,
executes the complete CTest gate, queries target dependencies, measures direct
object compile cost, records Clang time traces, attempts sanitizer builds within
the cloudtainer budget, inventories remaining source concentration, and reviews
primary sources relevant to target ownership, compiler profiling, SQLite crash
testing, and replicated convergence.

Statements are classified as:

- **proved in rev0806**: backed by source, an executable audit/test, or a sealed
  package check;
- **measured**: backed by a preserved command result but sensitive to this
  cloudtainer; or
- **roadmap/speculation**: a proposed direction, not implemented behavior.

## Executive findings

| Severity | Finding | Rev0806 action |
|---|---|---|
| High build/ownership defect | An 8,721-line deterministic corpus remained in every runtime consumer | extracted into its own source-owning diagnostic target |
| High graph leakage | Three focused reporting wrappers inherited unrelated domain diagnostics | split reporting and domain diagnostic static owners; wrappers link reporting only |
| Medium hidden authority | The corpus borrowed anonymous runtime helpers by translation-unit proximity | introduced a ten-operation private `_for_fixture` bridge with exact two-user audit |
| Medium runtime pollution | SQLite backup and review-metric fixture helpers lived in runtime | moved entirely into diagnostic source |
| Medium conversion risk | Strict Clang found eight inherited signedness hazards | three byte conversions and five checked CLI conversions corrected |
| High residual concentration | Runtime domain remains 15,840 lines; corpus remains one 8,905-line function-bearing unit | trace-backed next seams documented; not falsely claimed solved |

## Proved implementation results

### Runtime versus diagnostic ownership

- `src/sync_domain.cpp`: 24,531 parent lines to 15,840 final lines.
- `src/sync_domain_selftests.cpp`: 8,905 lines and the sole definition of
  `run_sync_domain_model_selftest()`.
- Runtime public headers contain no fixture bridge declaration.
- `src/sync_domain_test_access.hpp` is included by exactly the runtime defining
  unit and the domain diagnostic unit.
- Ten bridge declarations and definitions match exactly, and every operation
  ends in `_for_fixture`.
- Test-only SQLite backup and sidecar-review metrics helpers are absent from
  runtime.
- The extracted public diagnostic still reports **588 passed / 0 failed**.

The normalized extraction proof reverses only explicit bridge qualification.
After that normalization, the function body has two change hunks: five unsigned
fixture values now use checked conversion before a signed CLI boundary. No other
behavioral body delta is hidden by the move.

### CMake target graph

The final graph is:

```text
anonsync_reporting_selftests_lib   -> anonsync_core_lib
anonsync_sync_domain_selftests_lib -> anonsync_core_lib
anonsync_selftests_lib (INTERFACE) -> both source-owning diagnostic targets
```

The CLI links the interface aggregate. The three deterministic reporting
wrappers link only `anonsync_reporting_selftests_lib`. CMake iterates all
selftest source variables and rejects any diagnostic source added to the core
source set.

The focused boundary audit passes **13/13**. The broader runtime/selftest audit
passes **9/9**. CLI help and CTest registration remain in exact **38/38** parity.

### Complete executable gate

- GCC 14.2.0, C++20, Debug-equivalent project flags, bundled SQLite 3.53.3.
- Complete current final build graph is up to date.
- Full CTest: **81/81 passed**.
- Domain model: **588/588 checks**.
- Strict changed-unit Clang 17 lane:
  `-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror`.
- Changed-unit GCC 14 optimized syntax lane:
  `-O3 -DNDEBUG -Wall -Wextra -Wpedantic -Werror`.

A separate final from-scratch run was interrupted after 29/127 steps by severe
shared-container contention. It is preserved as an attempt, not represented as
a second clean-build pass. The complete current graph was produced from a clean
intermediate configure/build followed by final reconfigure/relink; a final
`cmake --build` reports no work, and all 81 tests pass against those outputs.

## Measured compile and dependency economics

### Ordinary runtime consumer

`anonsync_sqlite_runtime_payload_store_test` retains 42 first-party translation
units but falls from 51,809 to 43,118 first-party lines: **8,691 lines / 16.78%**
removed from its graph.

### Focused reporting wrapper

`anonsync_fuzz_json_codec` retains 43 first-party translation units but falls
from 55,392 to 46,701 lines: **8,691 lines / 15.69%** removed. The query confirms
that it includes reporting diagnostics and excludes domain diagnostics.

### Direct object compilation

| Unit | Lines | Wall | Peak RSS | Object bytes |
|---|---:|---:|---:|---:|
| Rev0805 combined domain | 24,531 | 16.54 s | 1,014,224 KiB | 12,889,776 |
| Rev0806 runtime domain | 15,840 | 11.43 s | 690,412 KiB | 10,425,424 |
| Rev0806 diagnostic domain | 8,905 | 10.90 s | 716,164 KiB | 5,720,872 |

For ordinary runtime consumers, the measured dominant object compile is 30.89%
faster and uses 31.93% less peak memory. Compiling both final objects serially
took 22.33 seconds, 35.01% more than the parent monolith. This revision therefore
claims lower ordinary-consumer cost, smaller individual compiler jobs,
independent scheduling, and correct ownership—not lower total diagnostic work.

### Clang time trace

The runtime `ExecuteCompiler` event was 8.01 seconds and the diagnostic event
5.01 seconds. Events overlap and are not additive. Named runtime parse hot spots
cluster around checkpoint operator status, scheduler planning/execution,
fake-peer execution, and the daemon loop. The diagnostic's single public model
function accounted for a 755.0 ms parse event, a 910.9 ms function-optimization
event, and a 297.1 ms code-generation event.

This evidence argues for a future checkpoint scheduler/operator/daemon invariant
owner in production and scenario-owned functions inside the diagnostic corpus.

## Sanitizer result and limit

The 15,840-line production domain unit now compiles to a 34,403,560-byte object
with ASan/UBSan instrumentation references. This clears the exact production
unit that blocked the parent attempt.

No complete instrumented executable, diagnostic-object sanitizer compile,
runtime sanitizer test, or leak-detection pass is claimed. Bounded attempts did
not finish under the shared 4 GiB/no-swap environment while unrelated large
compiler work was active. Logs and remaining Ninja step counts are preserved.

## Remaining architecture debt

### 1. Convergence is broad-tested but not algebraically specified

The 588-case diagnostic is substantial, yet durable operations still need an
explicit classification: commutative versus order-sensitive, idempotent versus
single-use, monotone versus retracting, causally independent versus dependent,
and epoch-compatible versus barriered. An independent small model should
generate reorder, duplicate, retry, partition, restart, concurrent update/delete,
and epoch-change traces, then differential-check C++.

### 2. Crash testing needs a domain-state oracle

SQLite's transaction result is only one artifact. Recovery classification must
span database/WAL/journal state, receipts, sidecars, checkpoints, staged bytes,
renames, directory durability, and externally published effects after every
injected cut. SQLite's alternative-VFS and power-loss test strategy is the right
mechanical inspiration, but AnonSync needs a higher-level oracle.

### 3. Runtime source remains concentrated

- `src/sync_domain.cpp`: 15,840 lines.
- `src/sqlite_replay_ledger.cpp`: 5,312 lines, including a 908-line selftest tail
  beginning at line 4,405.
- `include/anonsync_core.hpp`: 3,455 lines / 168,102 bytes.
- Runtime source: 590 lexical `sqlite3_*` call sites across 23 files.

The 908-line ledger diagnostic tail is the next low-risk ownership extraction.
The trace-backed checkpoint scheduler/operator/daemon cluster is the more
important production decomposition.

### 4. Privacy claims remain unproved

This revision changes build ownership, not cryptographic product properties.
The reviewed code still does not demonstrate a complete payload-encryption,
metadata-hiding, anonymity, forward-secrecy, group-epoch, revocation, recovery,
or post-compromise-security protocol. Authentication and replay defense must
not be presented as confidentiality or anonymity.

## Primary-source research

The preserved research note uses CMake's official documentation for interface
and transitive target semantics, Clang's official `-ftime-trace` documentation,
SQLite's own power-loss testing description, and the delta-CRDT paper. Research
supports the roadmap; it is not represented as implemented behavior.
