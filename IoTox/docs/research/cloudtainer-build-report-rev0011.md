# Cloudtainer build report — IoTox rev0011

**Date:** 2026-08-14 America/New_York  
**Revision:** rev0011  
**Version:** 0.11.0  
**Codename:** Ordinary Write  
**Northstar:** one installed C++20 ratox-successor executable  
**Strongest retained evidence:** one literal private per-peer FIFO write crosses signed durable admission, exact toxcore-queue retry, application receipt/result, terminal projection, and process restart against a distinct exact-ABI IoTox peer fixture

## Result

rev0011 turns the ratox inheritance into an executable product path. For every current Tox peer, the
single `iotox` process publishes a private local FIFO:

```text
peers/<64-UPPERCASE-TOX-PUBLIC-KEY>/command
```

A complete ordinary write such as:

```sh
printf '%s\n' device.describe > peers/<PUBLIC_KEY>/command
```

is framed by a bounded C++20 FIFO monitor, parsed as one registered IoTox operation, resolved against
the current peer set, and then submitted to the same signed durable command machinery used by the
structured local client. The FIFO is not a second protocol, second daemon, hidden shell, or competing
queue.

The product surface remains exactly:

```text
bin/iotox
```

Internal libraries, exact provider doubles, tests, fuzzers, and retained research tools remain build
or evidence components. They are not additional installed products.

The strongest honest statement for this revision is:

> The final rev0011 C++20 source has one working ratox-style write entrance for the read-only `device.describe` operation. In the retained separate-process fixture, that write receives a nonzero persistent sender epoch and message id only after signed durable admission, survives an injected c-toxcore `SENDQ` refusal through byte-identical retry, receives remote durable `RECEIVED` and terminal description evidence, and remains inspectable after the one product process stops and restarts.

This is not yet a genuine Tox-network result. The source-linked dependency path reached this
container's DNS boundary before compilation. The complete final-source local matrix did run: GCC,
Clang, AddressSanitizer, UndefinedBehaviorSanitizer, ThreadSanitizer, five bounded libFuzzer targets,
the host-linked Argon2 provider, and the Mutorr preservation lane all completed successfully.

## Product work completed

### A literal ratox-successor write surface

`RuntimeTree` now projects, for each current peer:

```text
command          mode-0600 FIFO; local ingress
command.help     exact supported record grammar and semantics
command-events   bounded disposable admission/rejection journal
```

The v1 grammar is deliberately small:

```text
one printable-ASCII operation name
terminated by LF
body length at most 256 bytes
implemented operation: device.describe
```

A conforming producer can write the entire record plus LF in one write of at most 257 bytes. That is
below the POSIX minimum `PIPE_BUF` of 512 bytes, so cooperating writers can preserve one-record write
atomicity even on an implementation exposing only the minimum.

The reader still treats the FIFO as a byte stream. It does not infer writer identity, trust write
success as admission, or concatenate abandoned fragments forever. Partial and discard states expire;
malformed and oversized input is rejected and later well-formed records can recover framing.

### Filesystem hardening

The monitor requires the expected object to remain a real FIFO in a real same-user peer directory
with private permissions. Before adopting an endpoint it applies:

```text
lstat path checks
O_NOFOLLOW open
fstat descriptor checks
owner and mode checks
path/descriptor device+inode comparison
```

A symlink, wrong owner, permissive mode, regular-file substitution, or path replacement is rejected.
The monitor rescans within a bounded interval, so a repaired FIFO can be adopted without restarting
the product.

The implementation uses a nonblocking reader plus a separate hold-writer descriptor. It does not
rely on Linux's convenient but POSIX-undefined `O_RDWR` FIFO open behavior.

### Durable admission remains the first authoritative fact

A successful `write(2)` means only that bytes entered the kernel FIFO. IoTox advances through
separate observable facts:

```text
record observed
record parsed
record admitted to the signed command store
exact request accepted by toxcore's local send queue
remote IoTox committed RECEIVED
terminal result committed
```

The callback does not allocate a message id and claim success in a disposable projection first. It
asks the existing outgoing command path to reserve and persist the canonical request. Only a
successful reservation produces an admitted event containing the nonzero durable sender epoch and
message id.

Rejected records are explicit and carry no durable identity. `command-events` can help an operator
find what happened, but it is bounded runtime evidence. The signed command store is authoritative.

### Transport- and storage-blind operation execution

The first handler has been moved behind `CommandEngine`. It receives an already decoded request and
an immutable execution context; it does not know whether the operation arrived through a FIFO, Unix
socket, Tox packet, test fixture, or future local adapter, and it does not mutate the command store.

The surrounding agent remains responsible for:

```text
canonical decoding
session and authority admission
durable lifecycle transitions
execution ordering
receipt/result commit
transport delivery and retry
runtime projection
```

Only read-only `device.describe` is executable. No setting, GPIO, actuator, firmware, OTA, shell, or
arbitrary command effect has been admitted.

### Runtime projections have an explicit evidence class

Disposable status, help, ingress-event, and peer-description projections are published with a
private temporary file and atomic rename. They are deliberately not `fsync`-durable and are never an
authority source or command database.

This distinction is now governed explicitly:

```text
signed command store    durable application truth for this research contract
runtime projections     replaceable observation and convenience state
FIFO                    transient byte rendezvous
```

### One-binary process and restart fixture

`tests/test_cli_process.cpp` and `tools/run-mock-node.sh` start the actual `iotox run` process and use
the same `iotox` executable for every operator action. The loadable toxcore fixture is a distinct
IoTox endpoint with its own transport perspective, session nonce, stable Ed25519 principal,
persistent sender epoch, signed proof behavior, durable command records, and audit log.

The retained fixture crosses:

```text
create/load Tox savedata, stable device identity, owner ledger, and command store
accept one peer by public key
HELLO, CAPABILITIES, transcript confirmation, and authority proof
pre-authority durable denial for device.describe
post-authority durable receipt and successful result
literal write of device.describe to the peer command FIFO
nonzero durable admission identity in command-events
injected toxcore SENDQ refusal and exact retry
remote application RECEIVED distinct from terminal result
peer-description projection bound to the authorized stable principal
clean stop
restart from savedata, identity, ledger, and command store
preservation of Tox address, sender epoch, and exact command evidence
```

The process fixture proves the one-binary product wiring and local durability model against the
exact consumed ABI mock. The mock does not implement Tox cryptography, DHT, NAT traversal, public
bootstrap, relay operation, congestion, or hostile-network timing.

## Primary-source research applied

### Ratox

Ratox's history confirms that the FIFO-first interface is not an incidental artifact. The upstream
change titled “Add fifos for incoming requests and remove cmd-parser” moved decisions toward
ordinary external Unix composition. IoTox retains that instinct while refusing to make transient
FIFO bytes the command truth.

Reviewed sources:

```text
https://github.com/pranomostro/ratox
https://raw.githubusercontent.com/pranomostro/ratox/master/ratox.c
https://git.2f30.org/ratox/commit/99b652c0c07c6acf81b6a8cf36a107be76fbe98d.html
```

### FIFO and pipe semantics

Linux and POSIX documents establish the constraints frozen in the adapter:

- a FIFO pathname is a rendezvous for one kernel pipe object, not persistent message storage;
- pipe/FIFO I/O is a byte stream without record boundaries;
- opening a FIFO `O_RDWR` succeeds on Linux but POSIX leaves that behavior undefined;
- a complete write no larger than `PIPE_BUF` is not interleaved with another writer's bytes;
- POSIX requires `PIPE_BUF` to be at least 512 bytes.

Reviewed sources:

```text
https://man7.org/linux/man-pages/man7/fifo.7.html
https://man7.org/linux/man-pages/man7/pipe.7.html
https://pubs.opengroup.org/onlinepubs/9699919799/functions/write.html
```

### c-toxcore 0.2.23

The pinned public contract continues to support the existing owner-thread and packet choices:

- accesses through one `Tox*` require external serialization;
- lossless custom packets are reliable and ordered after local queue acceptance;
- the maximum custom packet size is 1,373 bytes;
- `TOX_ERR_FRIEND_CUSTOM_PACKET_SENDQ` is local send-queue exhaustion, not proof that the remote
  application received or persisted anything;
- public bootstrap, TCP relay, proxy, UDP, and local-discovery options remain separate policy
  controls and therefore require route-specific leak tests.

The 0.2.23 release was published on 2026-06-03 and includes a critical memory-safety correction
identified during manual review. IoTox must keep toxcore pinned, monitored, replaceable behind the
adapter, and independently authorize every consequential application operation.

Reviewed sources:

```text
https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23
https://github.com/TokTok/c-toxcore/security/advisories/GHSA-42vg-9mg3-399f
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox_options.h
```

## Final-source build and verification evidence

The current source tree contains 86 owned C++ source/header files and 40,993 owned C++ lines under
`include/`, `src/`, and `tests/`. The default unit/integration runner registers 98 compiled checks;
the default CTest surface contains eight entries.

Final rev0011 results retained from the exact packaged source:

| Lane or fixture | Retained result |
|---|---|
| GCC 14.2 debug | 8/8 CTest entries passed |
| GCC 14.2 release | 8/8 CTest entries passed |
| Clang 17 debug | 8/8 CTest entries passed |
| Clang 17 AddressSanitizer + UndefinedBehaviorSanitizer | 8/8 CTest entries passed |
| GCC 14.2 ThreadSanitizer | 8/8 CTest entries passed after correcting the startup race it found |
| Five Clang 17 libFuzzer targets | 5,000 units each; 25,000 total; no crash or sanitizer finding |
| GCC 14.2 with system-linked `libargon2.so.1` | 8/8 CTest entries passed |
| Mutorr preservation build | 10/10 CTest entries passed |
| Direct owned unit/integration runner | 98/98 checks passed |
| Separate-process binary lifecycle | passed |
| One-binary mock-node lifecycle initiated through literal FIFO | passed |
| Release install surface | exactly `bin/iotox` |
| Retained checksums and offline prebuilt smoke | passed |

The verifier was split across resumable invocations because individual cloud commands can be
terminated at an execution ceiling. Every final-source lane was nevertheless rebuilt or confirmed
incremental after the last code correction, rerun, and appended to one retained matrix log ending
in `final-source-matrix=pass`. The matrix exit record is zero.

`tools/refresh-retained-artifacts.sh` remains strict by default. It refuses full mode if required
fuzzer or linked-Argon2 artifacts are absent. Its explicit partial mode remains available only to
record an environment limit without inventing green lanes; rev0011 no longer requires that override.

Exact retained paths:

```text
artifacts/reports/validation-summary.txt
artifacts/reports/build-matrix.log
artifacts/reports/build-matrix.exit
artifacts/reports/ctest/
artifacts/reports/fuzzer-smoke.log
artifacts/reports/unit-tests-detail.log
artifacts/reports/binary-process-lifecycle.log
artifacts/reports/mock-node-lifecycle.log
artifacts/reports/install-surface.log
artifacts/reports/prebuilt-smoke.log
artifacts/SHA256SUMS
```

## Defects and governance corrections found during rev0011

Construction and adversarial review changed the implementation rather than merely adding tests:

1. The first tempting FIFO ownership pattern used Linux's `O_RDWR` convenience. Primary-source
   review forced a separate reader and hold-writer design so the contract does not depend on
   POSIX-undefined behavior.
2. A filesystem attacker or accidental process could replace the FIFO with a regular file. The
   path now rejects substitution through type/owner/mode/symlink/inode checks, and a direct test
   requires adoption only after a real private FIFO is restored.
3. A writer can disappear without LF. The parser now expires abandoned partial and discard state
   rather than silently joining unrelated writers into one future command.
4. The existing mock lifecycle originally exercised only the structured local command. It now uses
   the literal per-peer FIFO as the initiating product action and requires the durable identity and
   terminal state from that exact path.
5. Runtime projection publication was at risk of being described with the same durability language
   as the signed journal. ADR 0042 and the implementation now state the narrower contract: private
   atomic replacement, not persistence across sudden power loss.
6. ThreadSanitizer found a real startup race: the event pump could read
   `command_fifo_server_` while the main thread was assigning and constructing that service. Both
   service objects are now fully constructed before the event thread can publish a snapshot, and
   failure cleanup keeps them alive until the event thread has joined. The corrected TSan lane
   passes 8/8 entries.
7. The broad verifier can be interrupted by the cloud execution ceiling after successful lanes.
   Artifact refresh now fails closed by default, supports an explicit partial-evidence mode, and
   never manufactures green results for absent binaries or logs. The final full record was produced
   through resumable exact-source lane execution.
8. The installed help text now names the per-peer FIFO and states that it enters the same signed
   durable command engine, so the one executable documents its literal ratox-successor surface.

## Source-linked standalone attempt

The standalone toolchain pins:

```text
c-toxcore 0.2.23
libsodium 1.0.22
Argon2 reference 20190702
```

The current attempt failed before compilation while fetching the first pinned archive because the
shell could not resolve `download.libsodium.org`. Curl exited with status 6 after its bounded retry.
That log is retained. It is an environment boundary, not a successful official-source build and not
evidence of two genuine Tox peers.

Prepared external gates remain:

```text
tools/build-standalone.sh
tools/verify-standalone.sh
tools/run-real-peer-smoke.sh
```

The eventual CLI run must correct whatever the real provider reveals. It should build official
pinned sources, launch two genuine `iotox` peers, establish friendship and the IoTox transcript,
prove stable principals, write the literal FIFO, cross durable COMMAND/RECEIVED/RESULT, interrupt
and reconnect transport, restart both sides, and exercise a TCP-relay path.

## Current evidence boundary

Established for final rev0011 source in this cloudtainer:

```text
one installed C++20 product executable
GCC debug/release and Clang debug warning-clean builds and default tests
Clang ASan+UBSan and GCC TSan default suites
five bounded parser fuzzers, 25,000 final-source units total
system-linked Argon2 provider lane and Mutorr preservation lane
exact consumed c-toxcore ABI provider boundary
one serialized toxcore owner thread
stable IoTox device identity and RecallRoot-derived authority model
signed authorization ledger
signed bounded durable command store
commit-before-send and commit-before-result order
application RECEIVED distinct from local toxcore queue acceptance
exact duplicate replay and conflicting-key rejection
injected SENDQ recovery
private hardened per-peer command FIFO
literal FIFO-to-durable-command separate-process path
one-binary stop/restart command evidence continuity
private atomic runtime projections
```

Not established here:

```text
source-linked official c-toxcore, libsodium, or pinned source-built Argon2 build
two genuine Tox peers or public network behavior
NAT traversal, TCP relay, Tor, or I2P route
rollback-resistant or encrypted command storage
trusted-clock expiry or cancellation
safe mutable setting, actuator, GPIO, firmware, or OTA effect
physical-power-failure validation on target storage
independent security audit or production readiness
```

## Next executable work

The next revision should keep moving outward from the same durable core rather than creating another
control system:

1. make ordinary peer text/action FIFOs and read journals useful while preserving bounded binary-safe
   structured variants for applications;
2. complete incoming friend-request decision files/FIFOs so an operator can run a node without the
   structured client;
3. expose finite file offer/accept/cancel/send paths through ratox-like private filesystem objects
   backed by the existing transfer manager;
4. continue shrinking `agent.cpp` by extracting outgoing reservation/retry/result coordination and
   incoming admission/replay coordination into typed command-service boundaries;
5. run the full compiler/sanitizer/fuzzer matrix on the eventual CLI and repair final-source defects;
6. build pinned official toxcore and cross the literal FIFO transaction between two genuine nodes
   before admitting any mutable device operation;
7. only after that, design one harmless durable setting with explicit version, idempotency, expiry,
   crash, replay, and rollback semantics.

## Decision

Keep Tox. Keep one product binary. Keep ratox's ordinary Unix feeling. Keep the permanent owner
RecallRoot and the independent authorization ledger. Make the simple surface tell the truth:

```text
ordinary write
bounded parse
signed durable admission
explicit transport state
remote application receipt
terminal result
restart-visible evidence
```

rev0011 is the first revision in which an ordinary filesystem write enters that complete product
path. The FIFO is intentionally ordinary. The admission is not.
