# IoTox cloudtainer build report — rev0034

- **Version:** 0.34.0
- **Revision:** rev0034
- **Codename:** I/O Bandwidth Kernel Accounting Citadel
- **Linked outer revision:** rev0021
- **Qualified implementation commit:** `98952abdf016859d24feb93ed121b50ed0007f60`
- **Qualified implementation tree:** `9ba56088df50681a52a2a23f07e012d81a802bf7`

## Result

rev0034 adds one exact-device block-I/O boundary to the existing delegated cgroup-v2 terminal
containment model. Canonical local terminal profiles advance to v5 and can carry a numeric Linux block
device identity plus independent read/write bytes-per-second and operations-per-second ceilings. Host
and profile policy compose monotonically only when both sides name the same device; disagreement fails
before transport or helper execution. Historical profile v1 through v4 bytes remain decodable and
migrate without invented I/O policy.

The host requests and verifies the delegated `io` controller, writes a complete `io.max` device record,
and parses the kernel readback semantically rather than depending on line or key order. Every absent
rate is written explicitly as `max`; every configured finite rate must be positive and no greater than
`INT64_MAX`. Duplicate devices, duplicate keys, malformed spacing, noncanonical integers, incomplete
standard fields, device alias text, and unexpected retained device policy fail closed.

I/O-limited session leaves pin a protected read-only `io.stat` descriptor before task attachment and
require a zero known-counter baseline. After recursive quiescence, and before exact leaf removal,
IoTox parses every device line, requires read/write byte and operation counters, accepts discard
counters only as a complete pair, tolerates well-formed future numeric keys, and accumulates with
unsigned saturation. A read or parse failure yields one explicit incomplete outcome and contributes no
partial counters. Complete cumulative read/write/discard byte and operation totals are projected only
through owner-private runtime status; no path, file, command, peer, profile, terminal, or device label
is retained.

The aggregate admission ledger intentionally remains unchanged. `io.max` is an overcommittable rate
limit, not a reservation of physical storage service. rev0034 therefore does not sum per-session I/O
ceilings into a false capacity claim.

The implementation also repairs retained-evidence construction. The artifact refresher no longer
invokes `ctest -N` after qualification because that show-only command can rewrite
`Testing/Temporary/LastTest.log`. It derives each lane's configured topology from generated CTest files,
requires every expected start, rejects failed or truncated transcripts, distinguishes capability skips
from passes, and includes all eleven configured fuzzers, including terminal protocol and the new
kernel-cgroup parser target.

## Validation summary

- GCC 14.2 Debug warnings-as-errors: 18/18 CTest entries completed; 15 passed, 3 capability-skipped,
  0 failed.
- GCC 14.2 Release warnings-as-errors: 18/18 completed; 15 passed, 3 capability-skipped, 0 failed.
- Clang 17.0 Debug warnings-as-errors: 18/18 completed; 15 passed, 3 capability-skipped, 0 failed.
- Clang 17 ASan+UBSan: 33/33 completed; 30 passed, 3 capability-skipped, 0 failed, with no sanitizer
  diagnostic. The owned registry ran in sixteen deterministic shards.
- GCC 14 ThreadSanitizer: 33/33 completed; 30 passed, 3 capability-skipped, 0 failed, with no race or
  deadlock diagnostic. The owned registry ran in sixteen deterministic shards.
- Host-linked Argon2: 18/18 completed; 15 passed, 3 capability-skipped, 0 failed.
- Mutorr preservation configuration: 20/20 completed; 17 passed, 3 capability-skipped, 0 failed.
- Direct owned C++ registry: 344/344 checks, 0 failures.
- Clang libFuzzer: 11/11 named targets completed 5,000 units each, including the new
  `iotox_terminal_cgroup_fuzzer`; no crash or sanitizer finding was reported.
- Exclusive Agent/session stress: 100/100 distinct fresh process runs passed, after one complete
  344-check registry discovery run.
- Product identity: `IoTox 0.34.0 rev0034`; help exposes the exact device plus four directional I/O
  ceilings.
- Qualified implementation `git diff --check`: pass; key shell scripts pass `bash -n`; the R7 analyzer
  self-test passes.

The three capability skips are independent live memory/PID, CPU, and I/O controller routes. This
construction host exposes those controllers at a higher cgroup level, but the isolated child namespace
does not preactivate them for further descendants. The lifecycle/recovery route is positive. No
positive controller-enforcement result is fabricated from an unavailable delegation.

## Focused proof surface

Profile tests freeze the complete v5 canonical record, exact v1-v4 historical decoding, migration,
strict device syntax, rate bounds, same-device monotone composition, host-only and profile-only
inheritance, and cross-device refusal. CLI tests reject a device without a rate, a rate without a
device, `0:0`, leading-zero aliases, extra separators, values beyond `uint32`, zero rates, overflow,
and malformed rate text.

Nested-key parser tests cover unordered device lines and fields, explicit `max`, accepted future keys,
missing standard fields, duplicate devices and keys, noncanonical spacing and decimals, zero finite
ceilings, overflow, optional discard-pair compatibility, multi-device accumulation, and saturation.
Outcome tests prove one-shot complete/incomplete transport, no partial aggregation, six-field
saturating totals, operation with aggregate ceilings disabled, and private runtime projection.

The capability-aware live I/O oracle, when run under a suitable writable exclusive delegation,
discovers the actual backing device from synchronous attached I/O, verifies semantic `io.max`
retention, performs session I/O, proves quiescent removal, and requires nonzero teardown accounting.
On this host it exits with named skip code 77 before policy mutation because `io` is not preactivated
for child cgroups.

## Research and construction evidence

Construction rechecked the Linux cgroup-v2 `io.max`, `io.stat`, controller-activation, top-down
delegation, and single-writer contracts from official kernel and systemd documentation on
2026-08-19. The applied review is `docs/research/io-bandwidth-kernel-accounting-rev0034.md`; ADR 0085
freezes the policy, composition, parser, enforcement, teardown, accounting, privacy, and nonclaim
boundaries. Revision-owned transcripts, source identities, exit records, source URLs, checksums, and
prebuilt smoke evidence are retained under `artifacts/rev0034/` after artifact refresh.

## Nonclaims

rev0034 does not discover storage topology, provide stable device naming across deployment changes,
control multiple devices in one profile, reserve aggregate physical bandwidth, guarantee throughput,
latency, completion time, queue depth, or fairness, implement I/O weights or cost models, attribute
buffered writeback to a command or file, control network or filesystem traffic independently of block
I/O, continuously sample rates, adapt from PSI, persist per-session outcomes across daemon restart,
protect against root or an equivalent delegated co-writer, qualify a target kernel fleet, establish a
genuine public-Tox two-peer Ratox session, complete physical-host R7 qualification, provide an
independent security audit, or establish production readiness.
