# Rev0805 implementation and architecture audit

## Scope

This audit read the complete rev0804 source tree, built the C++ project with the
bundled SQLite, enumerated CLI and CTest surfaces, executed omitted diagnostics,
traced their failures, inspected link and compile graphs, measured repository
concentration, ran strict compiler lanes, attempted a full sanitizer build, and
reviewed current primary research relevant to SQLite hardening, crash testing,
replicated convergence, group key management, and Linux process containment.

The audit distinguishes three classes of statement:

- **proved in rev0805**: backed by source, executable tests, or package checks;
- **audit finding**: backed by repository inspection but not a formal proof; and
- **speculation/roadmap**: a proposed design direction, not implemented behavior.

## Executive findings

| Severity | Finding | Rev0805 action |
|---|---|---|
| Critical proof gap | 11 of 38 advertised selftests were absent from CTest; 2 failed | fixed; 38/38 registered; 80/80 CTest |
| High test-boundary defect | hostile fixtures used a production-FK connection and could no longer manufacture corruption | fixed with explicit separate hostile/offline connection |
| High build/API waste | runtime library and runtime header carried selftest machinery | split into one-way test library and explicit selftest API |
| High architecture debt | 24,531-line domain TU blocks practical full instrumentation in this container | documented; next extraction target identified |
| High missing proof | no executable distributed convergence algebra | roadmap P0 |
| High missing proof | no exhaustive crash-cut/domain-state oracle | roadmap P0 |
| High containment gap | hostile SQLite interpretation is in-process | roadmap P0 worker |
| High product-claim gap | anonymity/confidentiality/key lifecycle are not demonstrated | roadmap P0 threat model |
| Medium migration debt | 751 lexical raw SQLite calls across source | inventory and typed migration recommended |
| Medium history debt | 284 revision tokens and 55 needle comments in active files | move archaeology to evidence manifests |

## Finding A — false-green selftest gate

### Parent evidence

The parent CLI help exposed 38 distinct `--selftest-*` flags. CMake registered
27 of those flags. The complete registered suite passed 67/67. Direct execution
of the 11 omitted flags produced nine successes and two exit-code-2 failures.
The preserved outputs are under `defect_reproduction/`.

### Root cause

There was no single machine-enforced source of truth between the diagnostic
surface and CTest. New or legacy CLI flags could exist without a corresponding
`add_test()`, so a green CTest run did not imply a green public diagnostic
surface.

### Correction

- register every omitted flag with CTest;
- give each diagnostic an explicit timeout;
- run `audit_selftest_registration.py` as CTest;
- compare binary help output with CMake in both directions; and
- fail on an empty help-derived set, missing registration, or unadvertised
  registration.

### Current proof

- advertised selftests: 38
- registered selftests: 38
- missing: 0
- unadvertised registrations: 0
- complete CTest: 80/80

## Finding B — adversarial fixture authority drift

### Parent evidence

The SQLite hardening and crash-corpus tests attempted direct `UPDATE` mutations
of `ledger_entries.entry_hash`. A production connection now enforces foreign
keys, so SQLite rejected the mutation with `FOREIGN KEY constraint failed`.
The tests stopped before they could verify production behavior against the
intended inconsistent artifact.

### Security interpretation

The correct response was not to disable foreign keys in production or to ignore
the return code. The fixture needed an explicit authority to manufacture a state
that production code must reject. Test mutation and production verification are
different roles and should use different connections.

### Correction

`selftest_sqlite_hostile_exec()` opens a separate read/write connection,
disables foreign-key enforcement only on that connection, verifies the pragma
state through exact scalar extraction, executes the mutation, and closes the
connection. Production verification opens/uses its normal hardened path.

### Current proof

- hardening diagnostic: 12/12
- crash-corpus diagnostic: 15/15
- both diagnostics: 10 consecutive repeated passes
- production foreign-key enforcement: unchanged

## Finding C — runtime library included test support

### Parent evidence

`src/reporting_selftests.cpp` was in `ANONSYNC_CORE_SOURCES`. It included the
small production JSON report implementation plus thousands of lines of
corpora, fixtures, subprocess helpers, test cryptography, and diagnostic entry
points. A representative runtime consumer exposed 56,278 first-party lines and
4,559 lines from this file.

### Correction

- move `report_json()` to `src/reporting.cpp`;
- remove `reporting_selftests.cpp` from the runtime source list;
- add `anonsync_selftests_lib` with a one-way dependency on the runtime library;
- link the CLI and deterministic diagnostic wrappers to the selftest library;
- keep normal runtime tests/consumers on the runtime library; and
- configure-fail if the selftest source reappears in the core list.

### Current proof

The same representative consumer exposes 51,809 first-party lines, includes
`reporting.cpp`, and does not include `reporting_selftests.cpp`. The reduction is
4,469 lines / 7.94%.

## Finding D — runtime header included diagnostics

### Parent evidence

`include/anonsync_core.hpp` declared 39 selftest entry points. One had neither a
definition nor a caller.

### Correction

- add `include/anonsync_selftest_api.hpp`;
- move the 38 real entry declarations and diagnostic helpers there;
- remove all selftest declarations from the runtime header;
- remove the stale undefined declaration; and
- make wrapper binaries include only the test API.

### Current proof

The separation audit passes 8/8. Runtime header selftest declarations: 0.
Selftest API declarations: 38. Definitions: 38.

## Repository concentration and migration observations

These are audit findings, not proofs of incorrect runtime behavior:

- `src/sync_domain.cpp`: 24,531 lines; selftest tail begins at line 15,811;
- `src/sqlite_replay_ledger.cpp`: 5,312 lines; selftest tail begins at line
  4,405;
- `src/reporting_selftests.cpp`: 4,475 lines, now test-only;
- `include/anonsync_core.hpp`: 3,455 lines / 168,102 bytes;
- raw `sqlite3_*(` lexical calls in source: 751 across 27 files;
- active revision-token occurrences: 284;
- revision-needle comment lines: 55; and
- local transport source contains Unix socketpair and IPv4 loopback mechanisms,
  not a demonstrated production remote transport.

The lexical cryptography search found authentication/signature components
(HMAC-SHA256 and RS256) but did not establish a payload-encryption, ratchet,
group-epoch, or metadata-hiding protocol. This is sufficient to mark privacy as
unproved, not sufficient to prove no such capability could exist outside the
reviewed source.

## Validation matrix

| Lane | Scope | Result |
|---|---|---|
| Parent package verifier | exact uploaded rev0804 ZIP | 25/25 |
| GCC Debug `-Werror` | complete project | build passed |
| CTest | complete registered rev0805 suite | 80/80 |
| Selftest registration audit | CLI help vs CMake | 38/38 |
| Runtime/test separation audit | source/API/CMake | 8/8 |
| Repetition | hardening + crash corpus, 10 iterations | all passed |
| Clang strict | final changed objects | passed |
| GCC O3 | final changed objects | passed |
| Mixed ASan/UBSan | CLI + selftest objects instrumented; runtime uninstrumented | 3 diagnostics passed |
| Full ASan/UBSan attempt | all first-party objects except domain TU compiled | not claimed |

## Deliberate non-claims

Rev0805 does not claim:

- a full-core sanitizer pass;
- leak detection;
- a complete optimized Release build;
- optimized bundled SQLite coverage;
- exhaustive crash consistency;
- formal or model-checked distributed convergence;
- production remote transport;
- payload confidentiality, anonymity, or metadata privacy;
- forward secrecy or post-compromise recovery; or
- complete typed-lifetime coverage of all SQLite calls.

## Recommended next correction

The highest-return next C++ change is to extract the 8,721-line deterministic
selftest tail from `sync_domain.cpp` into `anonsync_selftests_lib`, preserving
all behavior and adding a build-graph guard. In parallel, begin the independent
convergence reference model. The extraction makes sanitizer/model iterations
cheaper; the model prevents further accumulation of convergence mechanisms
without a convergence contract.
