# AnonSync rev0840 deep audit

## Heart of the mission

AnonSync is an evidence-authorized convergence engine. A successful operation or parsed
value is only an observation. The invariant owner must bind the exact identity,
incarnation, generation, policy, relationship, bytes, namespace object, resource budget,
and durability evidence needed by a transition. For serialized evidence, this implies a
stronger rule: **the exact owning value that passes validation must be the value from
which every emitted byte is derived**.

Rev0840 applies that rule to the daemon heartbeat publication boundary.

## Severe parent findings

### Validation and emission did not share one source value

The rev0839 encoder accepted the broad daemon options and result objects. It copied an
authority-bearing document, validated that copy, then serialized lifecycle, lease, and
progress fields directly from the broad result. The output therefore had two sources of
truth. The problem was not a demonstrated race in the current call site; it was an API
that made schema drift, accidental field leakage, and validation/emission mismatch easy
as the broad domain model evolved.

### Locale could corrupt the wire grammar

C++ streams use the process-global locale in effect at construction unless explicitly
imbued. A custom numeric grouping facet made rev0839 emit integers such as `7_000` and
`100_000`. RFC 8259's number grammar has no grouping separator. The preserved parent
witness fails Python's strict parser. Any embedding host or future locale initialization
could therefore turn a syntactically successful heartbeat write into unreadable bytes.

### The writer could publish what its reader rejects

The reader is bounded at 64 KiB, but rev0839's writer had no matching bound. The parent
reproduction uses a 70,000-byte reason and emits 73,146 bytes. A successful atomic
publication could thus create a document the same binary refuses to load, converting an
oversize diagnostic into lifecycle ambiguity.

## C++ correction

`SyncDaemonHeartbeatPublication` owns four small values: the typed authority document,
service-lifecycle observations, lease observations, and progress observations. The codec
accepts only a `const` publication. It validates all exact-number and lifecycle
relationships on that same value, then emits all bytes from that value.

`make_sync_daemon_heartbeat_publication_or_throw` is the sole broad-model adapter. It
copies the 3 used option fields and all 61 serialized result fields into an owning
snapshot. A focused mutation test changes the original options/result after adaptation
and proves that encoded output remains the frozen snapshot.

The writer and reader share `kSyncDaemonHeartbeatMaximumJsonBytes`. Serialization pins
`std::locale::classic()` before any numeric insertion and rejects output over the shared
ceiling before filesystem publication. V1 remains readable legacy evidence but cannot be
minted by the current encoder.

The in-memory `Json` value moved from `anonsync_core_internal.hpp` to
`include/anonsync_json_value.hpp`. The codec now depends on that leaf and process
observation, not crypto, SQLite, or the broad public domain model. A separate adapter
library depends on the codec and core types; the reverse dependency is forbidden.

## Refactor and build-graph result

The heartbeat document source's preprocessed surface fell by 41,377 lines (33.59%) and
1,426,486 bytes (39.55%). Its focused test fell by 53,701 lines (43.65%) and 1,772,437
bytes (49.28%). The mapping-heavy adapter is isolated in 133 source lines, and the JSON
value owner is a 63-line include leaf.

A 46-check audit proves broad-type absence from the codec, exact snapshot use,
locale pinning, shared size ownership, one adapter mapping per field, focused target
ownership, no core back-edge, and sanitizer compile/link parity. All 46 pass. The
neighboring process-observation audit passes 27/27 after being taught the new owner.

## Broader audit finding

A lexical inventory found 58 production `std::ostringstream` constructions and only two
explicit classic-locale imbues. Not every stream is machine-readable, and blindly
imbuing diagnostics would not prove anything. But reporting, replay journals, signed
intent construction, operator JSON, and other listed hotspots should be classified and
placed under explicit locale/canonicalization contracts. This is systemic debt, not a
claim that all 56 remaining streams are defective.

## Cloudtainer correction

An abandoned temporary workspace left a watchdog process that terminated commands whose
arguments mentioned the authoritative rev0840 build path. Two CTest attempts therefore
ended with signal 15 despite the tests preceding the cut passing. The stale process group
was identified by its exact command line and killed. Those partial runs are excluded.
The final result is counted only from nine complete, exact, non-overlapping ranges over
one immutable GCC Debug build, followed by a no-work dependency-closure build.

## Evidence

- Parent package: directory **21/21**, ZIP **25/25**.
- Active source patch replay: **PASS**, 233 files, zero mismatches.
- Active source delta: **13 files**, **1,231 insertions**, **378 deletions**.
- Heartbeat document: **58/58**.
- Publication adapter: **8/8**.
- Domain integration: **602/602**.
- Focused stress: **1,000 process executions**.
- Heartbeat source audit: **46/46**.
- Process identity neighbor audit: **27/27**.
- Clang 17 `-Werror`: **4/4**.
- GCC 14 ASan+UBSan with leak detection: **2/2**.
- Complete CTest inventory: **132/132**, including **39/39** registered audits.

## What remains missing

The heartbeat is not authenticated and is not a hard failure detector. The size ceiling
needs per-field budgets and an explicit failure-report channel. Other machine
serializers need locale and deterministic-byte classification. The broad core header and
15,287-line domain translation unit remain expensive. No full-project sanitizer or
Release build is claimed.

The larger mission remains open: executable convergence semantics, cross-resource
crash-cut completeness, disposable hostile-input workers, payload confidentiality,
anonymity and metadata-leakage analysis, device/key lifecycle, forward secrecy,
post-compromise recovery, and secure erasure.
