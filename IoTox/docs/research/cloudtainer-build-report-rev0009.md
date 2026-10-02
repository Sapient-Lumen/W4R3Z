# Cloudtainer build report — IoTox rev0009

**Date:** 2026-08-14 America/New_York  
**Revision:** rev0009  
**Version:** 0.9.0  
**Codename:** Sovereign Ledger  
**Northstar:** one installed C++20 ratox-successor executable  
**Strongest evidence:** compiled, unit-tested, exact-mock-ABI-tested, process-tested,
sanitizer-tested, bounded-fuzz-smoke-tested

## Result

rev0009 crosses IoTox's first application-authority boundary. A confirmed Tox session can now
carry a fresh directional challenge, a stable Ed25519 principal proof bound to that exact
online-epoch transcript, a decision against an independently signed local authority ledger, and
one harmless capability-gated machine operation.

The product surface remains one installed executable:

```text
bin/iotox
```

The process fixture exercises that executable both as the foreground agent and as its local
operator. Libraries, exact ABI mocks, test programs, fuzzers, and Mutorr preservation programs
remain internal build/evidence components; they do not become additional installed product
commands.

The strongest honest statement for this revision is:

> The owned C++ product path verifies a distinct signed exact-mock peer, denies a command before
> authority proof, admits the same read-only operation afterward, correlates and validates its
> result, retries byte-identical records after injected local toxcore queue pressure, projects
> the result through the ratox-style runtime tree, and preserves Tox, device, and authority
> identity across restart.

This is not a genuine-Tox-network claim. Official c-toxcore and pinned libsodium source could
not be downloaded in this container, and no public bootstrap, NAT, relay, Tor, or I2P path ran.

## Product work completed

### Stable IoTox device identity

IoTox now owns a persistent Ed25519 device principal that is deliberately separate from the Tox
route identity. The identity file contains a fixed-format random seed and derived public key,
uses private permissions, rejects malformed or mismatched material, and is written atomically.
The public key is re-derived during load instead of trusting duplicated serialized bytes.

This separation lets later route identities rotate without silently changing the application
identity or ownership constitution of the device.

### RecallRoot owner principal

The permanent RecallRoot-v1 phrase contract now feeds an explicit domain-separated owner-signing
seed. The phrase, root, owner seed, and signing secret remain in the short-lived local client
ceremony; the running agent receives signed authority records rather than the remembered secret.

The fixed derivation is intentionally reproducible. It therefore permits offline guessing, so
generated phrase entropy is part of the security contract rather than an optional recommendation.
No vendor recovery or reassignment key was added.

### Signed authority ledger v1

rev0009 adds a deterministic local constitution with:

```text
fixed 16-byte ledger header
fixed 256-byte Ed25519-signed records
stable device binding
strict sequence and previous-record digest chaining
ownership epoch field
bootstrap, grant, and revoke actions
roles with fixed capability ceilings
issuer possession and delegation checks
owner-only owner grant/revoke rules
implicit owner-demotion rejection
last-active-owner protection
bounded replay
private no-symlink loading
atomic complete-file replacement and directory fsync
```

The current format deliberately requires zero validity-time fields because trusted-clock policy
has not been designed. It has no rollback-resistant external witness and does not claim to solve
filesystem rollback or phrase compromise.

The loader reads and verifies into private temporary state, then commits the complete replayed
snapshot under its mutex. This avoids holding the ledger lock across blocking file I/O and keeps
observers from seeing a partially loaded constitution.

### Transcript-bound directional authority

After mutual HELLO/CAPABILITIES confirmation, each endpoint independently acts as verifier and
claimant.

The verifier sends a canonical challenge binding:

```text
its stable device principal
its current ownership epoch
its current ledger sequence and tail digest
the exact confirmed-session transcript digest
a fresh nonzero challenge nonce
```

The claimant returns a canonical Ed25519 proof binding all of those values plus its stable
principal and the challenge message ID. The verifier then checks the signature and consults its
own current ledger for role and capability state. The peer does not self-assert its powers.

Authority is directional. One side may prove an accepted principal while the reverse direction
remains unproven. A stable device principal can answer automatically without exporting its
secret. Recalled-owner or delegated-controller proof remains an explicit local ceremony.

`proof-sent` means only that toxcore accepted the local packet into its queue. It is not a remote
verification receipt. The exact mock independently verifies the proof for evidence, but protocol
v1 has no proof-acknowledgement message.

### First capability-gated operation

The first machine operation is intentionally read-only:

```text
device.describe
required capability: read.telemetry
```

The request uses a fixed eight-byte canonical body. Its correlated result has a fixed header and
a fixed 64-byte device description carrying:

```text
semantic version
revision number
negotiated protocol
stable device principal
implemented feature mask
offered operation mask
```

A successful result is accepted only when its correlation is reserved, its protocol equals the
confirmed session, and its principal equals the verifier device named by the peer's accepted
authority challenge. An exact duplicate is idempotent; a changed second result for the same
correlation becomes conflict.

The current reservation/result registry is bounded and process-local. It is suitable only for a
harmless idempotent query. It is not durable command execution and must not be connected to an
actuator.

### Ratox-successor operator surface

The one binary now exposes authority and the first operation while retaining the structured
local control socket as the authoritative write path. Representative commands include:

```text
iotox identity
iotox authority
iotox principals
iotox authority-challenge FRIEND
iotox authority-proof FRIEND
iotox authority-session FRIEND
iotox device-describe FRIEND
iotox peer-description FRIEND
```

The private runtime tree projects stable identity, ledger state, principals, peer sessions,
directional authority state, protocol journals, and the accepted peer description under a
public-key-first peer directory. The files are an observation façade over structured state, not
the authority database itself.

## Exact one-binary fixture

`tools/run-mock-node.sh` starts the actual `iotox run` process and uses the same executable for
all local operations. Its loadable toxcore ABI mock is a distinct counterparty with its own Tox
perspective, session nonce, stable Ed25519 device principal, authority challenge, proof, and
device description.

The final fixture completed this path:

```text
create Tox identity, stable device identity, and owner authority ledger
accept a transport peer by public key
inject one local SENDQ failure for HELLO
retry the exact frozen HELLO
inject one local SENDQ failure for CAPABILITIES
retry the exact frozen confirmation
confirm the transcript in both directions
inject one local SENDQ failure for AUTHORITY_CHALLENGE
retry the exact frozen challenge
receive the peer challenge
inject one local SENDQ failure for AUTHORITY_PROOF
retry the exact frozen signed proof
observe peer command denial before its proof is accepted
verify the peer proof against the current signed ledger
replay the exact peer command and return a successful device description
replay the exact request/result without changing the outcome
reserve a local device.describe request
inject one local SENDQ failure and retry the exact request
receive, correlate, bind, and project the peer description
stop cleanly
restart from savedata, stable identity, and authority ledger
prove all three identities remain continuous
```

The fixture watchdog was raised because RecallRoot Argon2 work can legitimately exceed the old
10-second test budget under constrained or instrumented execution. It also stopped expecting an
obsolete manually submitted device proof after the agent acquired automatic stable-device proof.
The runtime description projection is polled explicitly because a structured control reply and
its filesystem observation are adjacent operations, not one cross-interface transaction.

## Upstream research applied

Primary-source review on 2026-08-14 retained c-toxcore 0.2.23 as the current pinned target and
libsodium 1.0.22 as the current pinned signing/hash dependency.

The implementation and build plan were checked against:

```text
https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox_options.h
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/CMakeLists.txt
https://github.com/jedisct1/libsodium/releases/tag/1.0.22-RELEASE
https://doc.libsodium.org/public-key_cryptography/public-key_signatures
https://doc.libsodium.org/hashing/generic_hashing
https://git.2f30.org/ratox/file/ratox.c.html
```

Applied conclusions remain narrow:

- c-toxcore lossless custom packets provide reliable ordered packet transport after local queue
  acceptance; they do not provide IoTox authority, application receipts, idempotency, or durable
  execution;
- `TOX_ERR_FRIEND_CUSTOM_PACKET_SENDQ` is local queue pressure, so retry may reuse the exact
  frozen record but must not invent another logical request;
- the 1,373-byte reliable-packet ceiling leaves 1,332 bytes after the IoTox outer frame;
- one `Tox*` remains serialized by one owner thread;
- c-toxcore options expose controls relevant to later proxy/TCP-only experiments, but toggling
  those controls does not prove Tox/Tor or Tox/I2P;
- Ed25519 detached signatures and BLAKE2b generic hashing are appropriate narrow primitives for
  the current canonical records, but the application protocol and key hierarchy remain IoTox's
  responsibility;
- ratox's Unix simplicity remains the interface inheritance; its friendship/FIFO semantics are
  not adopted as the authorization or durability model.

The detailed source facts and IoTox inferences are retained in the rev0009 research notes and
ADRs. Current c-toxcore still presents itself as experimental and not independently formally
audited, so source pinning, rapid patching, application signatures, bounded parsers, sandboxing,
and explicit evidence levels remain product requirements.

## Verification executed

The final owned source was built with warnings as errors in the normal compiler lanes.

```text
GCC 14.2 debug                       build pass; CTest 8/8
GCC 14.2 release                     build pass; CTest 8/8
Clang 17 debug                       build pass; CTest 8/8
Clang 17 ASan + UBSan                build pass; CTest 8/8
GCC 14 ThreadSanitizer               build pass; CTest 8/8
system-linked Argon2 provider        build pass; CTest 8/8
Mutorr preservation configuration   build pass; CTest 10/10
owned unit/integration executable    81 checks; 0 failures
one-binary exact-mock lifecycle      pass
installed executable count           1 (`bin/iotox`)
lone-entrance layout                  pass
```

Five Clang libFuzzer targets each ran 5,000 units without a reported crash:

```text
iotox_frame_fuzzer
iotox_session_fuzzer
iotox_local_control_fuzzer
iotox_command_fuzzer
iotox_authority_fuzzer
```

Some long build lanes were resumed after the execution window interrupted Ninja; every reported
lane was then completed and its full CTest suite rerun. The retained logs preserve those
interruptions instead of rewriting history.

A focused Clang static-analysis pass originally reported blocking ledger reads under a critical
section. The loader was refactored to read/replay privately and commit under lock; the focused
analysis then completed without diagnostics. Broader static analysis is not part of the claimed
matrix, and one expensive authority-session analysis exceeded its bounded tool window.

Sanitizer and fuzzer success applies only to executed paths and generated inputs. It is not proof
of memory safety, race freedom, cryptographic correctness, parser completeness, or production
fitness.

## Product-shaped dependency attempt

`tools/build-standalone.sh` was executed. It stopped before any source-linked compilation because
shell DNS could not resolve the first pinned archive host:

```text
curl: (6) Could not resolve host: download.libsodium.org
```

The attempted archive contract remains pinned:

```text
libsodium 1.0.22
sha256 adbdd8f16149e81ac6078a03aca6fc03b592b89ef7b5ed83841c086191be3349

c-toxcore 0.2.23
sha256 b0349f4829d3d1699a77e199850f870f48d376e2baaf2c69d27b28571c498cfe
```

Consequently, this cloudtainer did not execute:

```text
official source-linked libsodium
source-linked c-toxcore
fully source-linked one-binary product
two genuine Tox peers
public bootstrap, NAT, TCP-relay, disconnect/reconnect, or finite-file network behavior
```

The build and peer-smoke facilities remain prepared for a networked command line. The failed
fetch is retained as a failed lane, not promoted into a build claim.

## Defects found while constructing rev0009

The facility exposed and corrected these material issues:

```text
stale explicit-claimant policy blocked automatic stable-device proof
duplicate CLI dispatch remained after an interrupted edit stream
an unsigned synthetic peer fixture could not prove authority semantics
an unmatched-result report held locks in an unsafe order
CLI and runtime projection could observe adjacent immutable snapshots at different moments
a process assertion treated proof-sent as remote proof processing
the fixture watchdog was too short for Argon2 under constrained execution
the fixture expected an obsolete manual device proof after automatic proof existed
one embedded 7,776-word literal exceeded Clang's strict string-literal limit
ledger loading held its mutex across blocking file reads
```

Corrections preserved or strengthened the contracts:

- the exact mock became a distinct signed peer;
- both authority directions are implemented and checked;
- the CLI returns and publishes one immutable operation snapshot;
- asynchronous filesystem observation is polled instead of assumed atomic with control replies;
- `proof-sent` remains honestly local;
- watchdogs accommodate real password-hardening work without hiding a hang;
- the word list is split into bounded literals and reassembled without changing bytes;
- ledger load/replay is private until one locked commit.

No assertion was removed merely to obtain green output.

## What rev0009 proves

Within this container and exact-mock model, rev0009 proves that the owned C++ code can:

```text
maintain one public product executable
keep toxcore behind one owner-thread boundary
preserve Tox, application-device, and authority identity across restart
reconstruct the fixed owner principal from RecallRoot-v1
prepare, sign, append, persist, reload, and deterministically replay authority records
reject malformed, tampered, unauthorized, over-capability, and owner-breaking records
confirm a canonical Tox online-epoch transcript
bind a stable principal proof to that transcript and current local ledger head
distinguish friendship, session readiness, proof, capability, enqueue, and operation result
reject device.describe before proof and admit it afterward
correlate and bind a successful description to the already challenged peer
retry exact frozen packets after modeled local SENDQ pressure
project useful ratox-style read surfaces without making them constitutional state
```

## What rev0009 does not prove

It does not prove:

```text
that current IoTox source compiles against the official c-toxcore/libsodium archives
that two real Tox peers establish or preserve the protocol sequence
that Tox succeeds through representative NATs or TCP relays
that Tox/Tor or Tox/I2P can be made functional and leak-free
that principal proof has a remote acknowledgement
that commands survive process death, disk failure, reconnect, or lost acknowledgements
that retries cannot duplicate a future physical effect
that clock-based expiry is safe on devices with bad time
that the ledger detects rollback or phrase compromise
that plaintext identity seeds are adequate for an appliance
that any actuator, firmware, or safety-critical operation is authorized safely
that the product is audited, hardened, target-tested, or production-ready
```

The next internal construction remains the durable command/result state machine and store. The
next external gate remains the pinned source-linked build followed by two genuine native Tox
peers.
