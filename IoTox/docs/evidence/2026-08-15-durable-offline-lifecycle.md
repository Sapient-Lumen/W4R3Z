# Durable offline command lifecycle evidence — 2026-08-15

Classification: shareable founding-host qualification report. The retained logs contain build and
test output only. Process fixtures used private temporary directories and destroyed their Tox
savedata, device keys, authority ledgers, command stores, runtime trees, and FIFO/socket state.

## Inputs

```text
implementation-source-commit=447f4fcc9602dda5fae1becec1af26c97d8fd84a
dependencies-lock-sha256=fa7b36c0f2de857ed35cb63967ab29fcdd6fa874ae5c4c0efe572f0195930e86
standalone-binary-sha256=cb448346b8f58d3f25d8305a61955029bb7879fd1beee080790988056203b5ca
final-matrix-log-sha256=2aee852e52bdd12d44f2db7abe15f2ec282d165275d863317498b969052ad80e
fuzzer-log-sha256=9932bd59ae7f54649d56b268576a74529a91df1c05fa4c1802dc6e73af40f4fc
coverage-xml-sha256=20a0567e06a3fea860557a769203e2147271d936c569883c66b61f6d57a3216b
agent-stress-log-sha256=a2e1dc1ef58d3c1f2ab3c0bd7d07bd46833ff4d5c0220af872612a26db3517d5
gcc=15.3.0
clang=21.1.8
provider=c-toxcore-0.2.23 pinned source for the standalone; exact ABI double for process tests
```

The Clang 21 wrapper was selected because it uses the same glibc 2.42 generation as the available
bare-metal provider libraries. An older Clang 17 wrapper produced glibc 2.39 executables that could
not load those host libraries; that rejected lane was an environment/toolchain mismatch, not a
green or failed IoTox source result.

## Frozen lifecycle and storage gates

The maintained 137-check C++ registry proves:

- `IOTXCMD3` signs the complete header and sorted record body, rejects malformed or foreign state,
  and persists independent request, receipt, and result delivery schedules;
- a correctly signed private v2 snapshot strictly decodes and atomically migrates to v3 before
  transport starts, while a configured size refusal leaves every byte of the original v2 file
  unchanged;
- insertion, update, cancellation, clock checkpoint, quota, configured-size, and persistence
  failures leave the prior in-memory and on-disk generation authoritative;
- only fully delivered terminal history is prunable; unfinished global, peer/direction record, and
  peer/direction canonical-byte limits fail explicitly and are revalidated on open;
- the one-second admission delay permits cancellation only while an outgoing request is reserved
  with zero committed attempts; any possibly peer-visible attempt irrevocably closes that path;
- high, normal, and low priority order is deterministic, while exact exponential backoff and stable
  jitter preserve a monotonic signed next-attempt deadline across ordinary and forced replay;
- clock high-water checkpoints are signed and monotonic, rollback tolerance is boundary-tested,
  and attempt scheduling uses a steady process clock rather than following live wall-clock jumps;
- trusted expiry before an attempt becomes `expired`, expiry after an attempt becomes
  `timed-out-unconfirmed`, and one exact authenticated late result may resolve the retained uncertain
  timeout without reopening cancellation or unattempted expiry;
- shutdown closes durable admission and retry starts before ingress and transport teardown; and
- clock scheduling and rollback checks read the high-water scalar under the store lock instead of
  copying a potentially 8 MiB full snapshot for each record serviced.

Exact registry summaries after the final matrix were:

```text
tests=137 selected=137 shard=0/1 failures=0
tests=150 selected=150 shard=0/1 failures=0
```

The second line includes the preserved 13-check Mutorr incubator.

## Separate-process offline gate

`iotox.binary-process-lifecycle` starts the actual daemon and uses the same binary as its local
client. The final fixture proved:

- online high-priority admission exposes the persisted cancellation window and cancels at zero
  attempts;
- TTL admission fails closed when wall-clock trust was not explicitly enabled;
- a deliberately restored but disconnected friendship admits a key-bound current-version read,
  remains `reserved` with zero transport attempts beyond the ordinary delay, survives process
  restart, and cancels safely;
- an explicitly trusted 500 ms TTL on that offline friendship settles as unattempted `expired`
  rather than fabricating delivery or a peer result;
- injected toxcore `SENDQ` pressure retains and retries the exact frozen request bytes; and
- command records and runtime projections reconstruct across orderly stop and restart.

The fixture uses the exact consumed c-toxcore ABI double so offline state and error timing are
deterministic. It does not turn the mock into genuine-network evidence.

## Complete qualification

The clean final source matrix ended with `final-source-matrix=pass`:

```text
GCC 15.3 Debug warnings-as-errors                 8/8 CTest entries
GCC 15.3 Release warnings-as-errors               8/8 CTest entries
Clang 21.1 Debug warnings-as-errors                8/8 CTest entries
Clang 21.1 ASan+UBSan, leak/error halting          8/8 CTest entries
GCC 15.3 TSan, race/deadlock halting               8/8 CTest entries
GCC 15.3 linked system Argon2                      8/8 CTest entries
GCC 15.3 Mutorr preservation                     10/10 CTest entries
frame/session/local-control/command/authority fuzz 5,000 executions each
```

The clean coverage build passed all eight CTest entries and the enforced 70% line floor:

```text
lines=70.6% (13,337/18,889)
functions=87.6% (1,183/1,351)
branches=39.3% (12,562/31,949)
```

The exclusive fresh-process Agent/session stress audit passed 100/100 consecutive runs at
`shard=1/137`. The pinned standalone verifier passed and found no shared runtime dependency on
c-toxcore, libsodium, or Argon2. A second incremental construction of the unchanged source produced
the identical standalone binary SHA-256 recorded above.

## Review findings resolved before the source commit

The qualification review corrected five subtle boundaries before the final matrix:

- incoming terminal records are retained until both locally owned artifacts have entered the local
  Tox queue;
- a live rollback check is anchored to monotonic elapsed time, not only signed startup history;
- explicit duplicate replay cannot move a signed retry deadline backward;
- size-refused migration is tested against the complete exact original v2 file; and
- retained uncertain timeouts can accept one exact late authenticated result without making every
  locally terminal state mutable.

The final performance pass also removed per-record full-snapshot copies from the clock hot path.
The optimized tree, rather than the earlier diagnostic tree, produced every result in the complete
qualification section.

## Claim boundary

This closes M5 for the current read-only `device.describe` and `system.summary` operation set on the
official IoTox tool. It establishes bounded durable offline admission, restart replay, scheduling,
expiry uncertainty, cancellation-before-start, quota, persistence-failure, and shutdown behavior
against deterministic process/provider fixtures.

It does not establish a mutable or physical effect, remote cancellation after an attempt, secure
time, rollback-resistant storage, encrypted command metadata, power-cut/flash-wear fitness,
controlled packet-loss behavior, a new genuine-network result for M5, production readiness, or
cross-client compatibility. Existing retained genuine-peer normal-native and TCP-only reports
remain the narrower network evidence for the protocol and authority layers.
