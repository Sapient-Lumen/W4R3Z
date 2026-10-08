# AnonSync rev0840

## Mission increment

An outward evidence document must be authorized as one exact value: freeze it, validate
that value, serialize that value under invariant byte rules, and reject it before
publication when the local reader cannot consume it.

## Delivered

- One owning `SyncDaemonHeartbeatPublication` containing the authority document and all
  lifecycle, lease, and progress observations.
- One narrow adapter from the broad daemon options/result model into the publication.
- Exact adapter coverage for 3 option fields and 61 result fields.
- Codec API and implementation with no broad daemon model access.
- Validation and emission from the same immutable publication reference.
- Shared 65,536-byte writer/reader bound with pre-publication rejection.
- Locale-independent JSON integer formatting via `std::locale::classic()`.
- Dependency-light `anonsync_json_value.hpp` extracted from the runtime internal header.
- Separate codec and adapter static-library owners with one-way CMake dependencies.
- Focused adapter snapshot test, custom-locale regression, oversize regression, and v1
  minting fence.
- Expanded 46-check source/build-graph audit, including mapping parity for every emitted
  broad-model field and sanitizer compile/link parity.
- Neighboring process-identity audit updated for the new publication owner.
- A repository-level locale-sensitive stream inventory for future corrections.

## Parent defects reproduced

1. A custom global grouping locale made rev0839 emit `7_000`, `100_000`, and similar
   tokens. Python's strict JSON parser rejects the preserved witness at line 6.
2. A 70,000-byte reason made rev0839 emit 73,146 bytes, 7,610 bytes beyond its own
   bounded reader's 65,536-byte ceiling.
3. The rev0839 codec accepted broad orchestration state, validated one derived subset,
   and later read the broad state again while emitting observations.

## Validation

- CTest: **132/132** in nine exact non-overlapping shards.
- Registered audit tests: **39/39**.
- Heartbeat document: **58/58**.
- Publication adapter: **8/8**.
- Domain integration: **602/602**.
- Focused stress: **1,000 process executions**.
- Heartbeat source audit: **46/46**.
- Process identity neighbor audit: **27/27**.
- Clang 17 `-Werror`: **4/4** focused tests/audits.
- GCC 14 ASan+UBSan, leak detection enabled: **2/2** focused executables.
- Source patch replay: **PASS** across 233 active files.
- Parent: directory **21/21**, ZIP **25/25**.

## Measured dependency reduction

| Translation unit | rev0839 preprocessed lines | rev0840 lines | Reduction |
|---|---:|---:|---:|
| Heartbeat document source | 123,196 | 81,819 | 33.59% |
| Heartbeat document test | 123,029 | 69,328 | 43.65% |
| New publication adapter source | — | 40,884 | split owner |
| New publication adapter test | — | 52,659 | split owner |

## Important interpretation

The publication is a frozen serialization capability, not authenticated authority. An
attacker able to replace the heartbeat file can still forge it for denial of service.
Durable owner-generation checks and exact process observation remain independent gates.

The 64 KiB rejection is deliberately fail-closed. It avoids publishing evidence that
the project itself cannot read, but an operational policy still needs bounded diagnostic
fields and a separate failure-report path so an oversize reason does not silently reduce
service visibility.

## Scope limits

No complete canonical-JSON implementation is claimed; only the heartbeat's numeric
format is locale-independent and its fixed member order remains implementation-defined.
No full-project sanitizer, Release build, arbitrary failure-cut completeness, Windows
runtime result, authenticated heartbeat, convergence proof, confidentiality, anonymity,
metadata hiding, hostile-worker isolation, or secure erasure is claimed.

## Handoff

See `REVISION_EVIDENCE/rev0840/AUDIT.md`, `RESEARCH.md`, `NEXT_WORK.md`, and
`validation/VALIDATION_SUMMARY.json`.
