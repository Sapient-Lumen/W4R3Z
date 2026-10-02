# BOOTSTRAPROSE — Wake From Amnesia

**Project:** IoTox
**Revision:** rev0004
**Codename:** Wake From Amnesia
**Immediate northstar:** a stronger ratox successor
**Status:** buildable research system; not a production appliance

This is the lone ordinary entrance to the IoTox datacube.

Everything else is deliberately hidden under `.datacube/`. The hiding is not security
and it is not mysticism. It is interface discipline: a future office holder, human or
machine, should wake with no conversational memory, read one object, learn what is
true, learn what is only intended, reproduce the evidence, and then enter the full
working repository without guessing which README won an old argument.

Read this file completely before modifying the project.

This prose is **living operational governance**. The current office holder is not merely
permitted to edit it; the office holder is responsible for rewriting it thoroughly when
reality changes. Preserve decisions and evidence in the datacube, but do not preserve
stale wording out of reverence. Truth outranks continuity of phrasing.

---

## 1. The thing being made

IoTox is a self-owned, peer-to-peer device agent built around Tox.

The immediate product is not Mutorr, not a distributed database, not a vendor cloud,
not a GUI, and not an abstract framework for every overlay network. It is a modern,
small, reliable, inspectable **ratox successor** for physical devices and local programs.

Ratox demonstrated a beautiful idea: complicated encrypted peer networking can feel
like ordinary Unix I/O. IoTox keeps that joy while adding the semantics a device agent
cannot safely omit.

The intended outside should remain obvious:

```text
start the agent
see its Tox address
observe whether it is connected
add a transport peer deliberately
send or receive a framed message
watch events
persist the identity
stop cleanly
script all of it with ordinary local tools
```

The disciplined inside must eventually provide:

```text
one toxcore owner thread
bounded structured local IPC
strict packet framing
explicit authorization independent of Tox friendship
durable commands and results
idempotency, expiry, replay resistance, and cancellation
atomic private state persistence
signed ownership and recovery transitions
safe file transfer and update handling
route policy for native Tox and later Tox-over-Tor / Tox-over-I2P
```

The governing product sentence is:

> From memory, you can reach your devices.

The governing implementation sentence is:

> Make the simple operation truly simple without lying about what occurred.

“Just werx” is not permission to hide ambiguity. It is a demand that the machinery earn
a small interface.

---

## 2. Decisions already made

These are current project decisions, not casual suggestions. Change them only through
an explicit new decision record that states what evidence or product need overcame the
old reasoning.

### 2.1 Tox stays

Tox is the primary network fabric. Sentiment is not sufficient evidence, but it is not
being discarded merely because hard ownership and recovery questions exist. Those
questions exist with every transport.

Tox supplies encrypted peer sessions, long-lived endpoint identities, peer discovery,
NAT traversal, bootstrap discovery, TCP relays, lossless custom packets, and file
transfer. IoTox supplies device identity, ownership, authorization, recovery, command
semantics, and local usability above it.

A Tox key is a transport endpoint. It is not by itself the owner, the authorization
ledger, or permission to actuate hardware.

IoTox intends to contribute useful bootstrap and relay capacity, deployment tooling,
measurements, documentation, and fixes back to the Tox commons. Operating a bootstrap
node or relay must never confer ownership authority over an IoTox device.

### 2.2 Permanent recall is retained

IoTox keeps a fixed Argon2id derivation contract for owner re-entry. A sufficiently
strong generated phrase may be printed, memorized, or both. The same phrase reproduces
the same RecallRoot without stored per-owner metadata.

That property intentionally permits offline password guessing. Therefore phrase
strength is structural, not optional. Human-invented passwords are not acceptable.
RecallRoot-v1 currently specifies eight independently generated words from the pinned
7776-word EFF long list, approximately 103.4 bits under uniform generation, Argon2id
version 19, 65536 KiB, three iterations, four lanes/threads, fixed public salt
`IoToxRecallRoot1`, and 32 output bytes.

The phrase and derived root must never be transmitted. Daily operation should use
domain-separated delegated keys. The exact owner-key hierarchy and live re-entry
handshake remain unfinished.

### 2.3 There is no vendor reassignment key

The IoTox project, company, maintainer, relay operator, bootstrap operator, application
publisher, or update service must not possess a key that can reassign customer devices.

A manufacturer key may attest hardware or sign software. It may not silently replace
the owner.

### 2.4 Authorization is independent of friendship

The authorization ledger is separate from the Tox friend list. It must eventually
express owners, delegated controllers, roles, capabilities, ownership epochs,
temporary grants, revocation, and endpoint bindings.

Adding a Tox friend creates only a transport relationship. The current CLI names this
operation `transport-peer-add` specifically to prevent semantic drift.

No physical actuation command belongs in the trusted product surface until the ledger,
message authentication, durable execution state, expiry, idempotency, and replay rules
exist.

### 2.5 Native Tox comes first

The route taxonomy is intentionally two-dimensional:

```text
transport: Tox
route:     native | Tor-reserved | I2P-reserved
```

This is distinct from possible future direct IoTox transports over Tor or I2P.

The build currently enables only `Tox/native`. `Tox/Tor` and `Tox/I2P` are reserved,
fail closed, and may not silently fall back to native networking. They remain future
research routes through which Tox itself would operate.

### 2.6 Mutorr is preserved, not pursued

The Milehigh Small Circles work remains valuable research. It is not the immediate
northstar and is excluded from the default build and test set.

Its source, tests, fuzz corpus, simulation, and benchmark are retained under
`.datacube/incubator/mutorr/`. Reactivating it requires an explicit office-holder
decision. No core feature may begin depending on it accidentally.

### 2.7 The local core is structured; the façade may be ratox-like

The primary local API is a versioned Unix `SOCK_SEQPACKET` protocol with bounded whole
messages, request IDs, correlated responses, and explicit status codes. The daemon
also publishes private, atomically replaced read-only status files and a metadata-only
event journal.

Future files, FIFOs, or command paths may provide ratox-like ergonomics, but they are a
façade over the structured core. A FIFO write is not automatically a durable,
authorized, exactly-once device command.

### 2.8 C++ is the owned implementation language

IoTox-owned executable, library, test, mock, benchmark, and fuzz implementation is
C++20. External libraries such as c-toxcore and Argon2 may be C, but they remain behind
small exact ABI boundaries.

The project builds with GCC and Clang. Warnings are errors in checked configurations.

---

## 3. Current truth — rev0004

The labels below have strict meanings:

```text
idea                 described only
planned              ordered work with acceptance criteria
compiled             compiler and linker accepted it
unit-verified         direct deterministic tests passed
adapter-verified      boundary passed against an exact test double
binary-verified       separate built processes passed an end-to-end fixture
network-verified      real peers crossed a real or controlled network
route-verified        traffic and leak properties of a route were measured
 target-verified      measured on intended hardware and operating conditions
production            reviewed, supportable, updateable, and accepted for deployment
```

Do not collapse these words into “implemented.”

### 3.1 What exists in code

`iotoxd` is a foreground C++20 device-agent process.

`iotox` is a C++20 same-user local control client.

The daemon currently provides:

- runtime loading of a c-toxcore 0.2.23-compatible shared library;
- one owner thread that exclusively calls the `Tox*` instance;
- official options-accessor style rather than direct options-structure access;
- Tox savedata load, identity preservation, and atomic private save;
- callbacks translated into typed internal events;
- explicit transport-peer acceptance;
- lossless custom-packet transmission and reception;
- strict IoTox application-frame encoding and decoding;
- repeated, strictly parsed bootstrap-node and TCP-relay configuration;
- offline bootstrap retry timing;
- a private Unix `SOCK_SEQPACKET` control socket;
- Linux same-effective-user admission using `SO_PEERCRED`;
- a `0600` socket in owner-controlled `0700` directories;
- bounded control datagrams and correlated request IDs;
- private status files under `runtime/self/`;
- a bounded-rotation event journal that records metadata but not packet bodies;
- clean local shutdown and process restart with the same Tox address.

The control client currently supports:

```text
ping
status
address
stop
transport-peer-add PUBLIC_KEY_HEX
transport-send FRIEND_NUMBER PACKET_HEX
transport-hello FRIEND_NUMBER [TEXT]
```

The low-level transport commands are research and integration tools. They are not an
authorization API and should not become one by convenience.

### 3.2 What has been proven

The default GCC debug build currently has 25 registered C++ unit/integration tests and
seven CTest entries.

The test facility includes an exact loadable C++ toxcore ABI mock. It exercises dynamic
symbol resolution, version checks, Tox creation, callbacks, iteration, bootstrap and
relay calls, peer acceptance, custom-packet echo, savedata, shutdown, and reload.

A separate C++ process-lifecycle test executes the actual `iotoxd` and `iotox` binaries,
uses the shared-library mock, configures a bootstrap node and TCP relay, sends a HELLO
packet, confirms that the event journal excludes payload text, stops the daemon through
the socket, restarts it, and verifies identity continuity.

The local control decoder and the over-Tox frame decoder have Clang libFuzzer targets.
The checked matrix includes GCC debug/release, Clang debug, Clang ASan/UBSan, and GCC
TSan when supported by the container runtime.

### 3.3 What has not been proven

No real c-toxcore binary is bundled in this revision. The cloud container could not
retrieve its source through its ordinary shell network path, so the current transport
claim is **binary-verified against the exact mock**, not real-network-verified.

The following remain unproven or absent:

- building the pinned official c-toxcore 0.2.23 source inside the datacube;
- loading and running that real library here;
- two real Tox peers bootstrapping and connecting;
- NAT traversal, TCP relay, disconnect, reconnect, and long-offline behavior;
- real Tox file transfer;
- public bootstrap-list acquisition, rotation, provenance, and health policy;
- owner keys, delegated keys, and device application identity;
- the authorization ledger and revocation enforcement;
- physical claim and remembered-phrase re-entry transcripts;
- durable command inbox/outbox and execution receipts;
- cancellation and bounded owner-thread command-queue semantics;
- stable peer directories and friend-request workflows;
- ratox-compatible FIFOs or stream surfaces;
- signed firmware/update handling;
- Tor-routed or I2P-routed Tox;
- target-device RAM, CPU, network, flash, power, suspend, and reliability evidence;
- independent security, cryptographic, licensing, or product-safety review.

A successful mock test is valuable evidence about IoTox code. It is not evidence that
the public Tox network, a target NAT, or a battery-powered appliance behaves as hoped.

---

## 4. Wake sequence for an amnesiac office holder

From the extracted archive root:

```sh
# 1. Confirm that this really is the lone entrance.
find . -maxdepth 1 -mindepth 1 -printf '%f\n' | sort

# Expected ordinary name: BOOTSTRAPROSE.md
# Expected hidden names include: .datacube and .gitignore

# 2. Enter the hidden working repository.
cd .datacube

# 3. Read the compact truth and history indexes.
cat REVISION
cat PACKAGE.md
cat CHANGELOG.md
cat MANIFEST.md
cat docs/decisions/README.md
cat docs/governance/office-holder.md
cat docs/open-questions.md

# 4. Reproduce the default build and tests.
cmake --preset gcc-debug
cmake --build --preset gcc-debug
ctest --preset gcc-debug

# 5. Run the detailed registered test list.
./build/gcc-debug/iotox_tests \
  --mock-toxcore ./build/gcc-debug/libtoxcore-iotox-mock.so \
  --mock-argon2 ./build/gcc-debug/libargon2-iotox-mock.so \
  --wordlist third_party/eff_large_wordlist_2016-07-18.txt

# 6. Run every checked compiler/sanitizer lane available in the environment.
./tools/build-matrix.sh

# 7. Verify the retained release artifacts.
./artifacts/run-prebuilt-tests.sh
```

A fast manual daemon exercise with the exact mock:

```sh
cd .datacube
./tools/run-mock-node.sh
```

Or operate the two real binaries directly in separate terminals:

```sh
# Terminal 1
cd .datacube
runtime="$(mktemp -d)/run"
state="${runtime%/run}/state/device.toxsave"
./build/gcc-debug/iotoxd \
  --library ./build/gcc-debug/libtoxcore-iotox-mock.so \
  --runtime "$runtime" \
  --state "$state"

# Terminal 2: use the runtime printed by iotoxd
cd .datacube
./build/gcc-debug/iotox --runtime /absolute/runtime/path ping
./build/gcc-debug/iotox --runtime /absolute/runtime/path status
./build/gcc-debug/iotox --runtime /absolute/runtime/path address
./build/gcc-debug/iotox --runtime /absolute/runtime/path stop
```

For a real c-toxcore library, add one or more endpoints:

```sh
./build/gcc-debug/iotoxd \
  --library /absolute/path/to/libtoxcore.so.2 \
  --bootstrap 'host.example:33445:64_HEX_PUBLIC_KEY' \
  --tcp-relay 'relay.example:443:64_HEX_PUBLIC_KEY'
```

Bracket IPv6 hosts. Endpoint configuration is not a trust grant.

---

## 5. Datacube map

After entering `.datacube/`:

```text
CMakeLists.txt                  default C++ build graph
CMakePresets.json              checked compiler and sanitizer lanes
include/iotox/                  public C++ interfaces
src/                            ratox-successor implementation
  agent.cpp                     daemon orchestration
  control_main.cpp              local `iotox` client
  daemon_main.cpp               `iotoxd`
  local/                        control protocol/socket/runtime tree
  toxcore/                      ABI loader, endpoint parser, owner thread
  protocol/                     over-Tox frame codec
  security/                     RecallRoot research implementation
  state_store.cpp               atomic private persistence
tests/                          C++ unit, integration, process, mock, fuzz tests
incubator/mutorr/               preserved non-default Milehigh research
docs/                           active design, governance, decisions, research
artifacts/                      retained checked binaries and evidence
third_party/                    pinned data and license records
tools/                          matrix, lifecycle, packaging, and checks
```

Git history is the source-history archive. `docs/history/` and `artifacts/history/`
retain important prior prose and delivered evidence where a plain history view is useful.

---

## 6. Repository and governance rules

### 6.1 The lone-entrance invariant

At archive root, `BOOTSTRAPROSE.md` is the only non-hidden entry. The working repository
lives under `.datacube/`. A layout test must fail if another ordinary root entry appears.

Do not create a second visible README, setup script, license file, or convenience link.
Put it in the datacube and teach this entrance how to find it.

### 6.2 BOOTSTRAPROSE minimum content

There is no maximum length. This file may not be reduced below these functional
minimums:

1. what IoTox is and the current northstar;
2. decisions currently in force;
3. exact implementation truth and explicit non-claims;
4. reproducible wake/build/test commands;
5. repository map;
6. office-holder authority and duties;
7. security invariants;
8. immediate ordered work;
9. revision/package naming policy;
10. an amendment note identifying the last substantive update.

Concision and precision are valued. Removing repetition is good. Removing the ability
to resume responsibly is not.

### 6.3 Office-holder authority

The office holder may refactor code, replace architecture, rewrite this prose, supersede
decisions, retire experiments, introduce dependencies, change build systems, or reject
an old dream.

That freedom carries duties:

- distinguish desire from evidence;
- preserve user-made decisions unless explicitly superseded;
- record why a durable choice changed;
- update claim maturity when evidence changes;
- keep default builds reproducible;
- leave failing or unavailable lanes visibly red or unavailable, never cosmetically green;
- do not silently weaken authorization, recovery, route isolation, persistence, or local permissions;
- preserve prior delivered revision archives and their provenance;
- update this entrance before packaging.

The office holder is a steward, not a priest of prior text.

### 6.4 Decision records

Architectural decisions live under `docs/decisions/`. A new record should state:

```text
context
chosen decision
alternatives considered
security and operational consequences
what would justify revisiting it
status: proposed | accepted | superseded | rejected
```

Never rewrite an accepted historical record to make the past look cleaner. Add a
superseding record and update the index.

### 6.5 Evidence records

A revision package should retain:

- compiler and platform versions;
- exact configure/build/test commands;
- unit and integration output;
- process-lifecycle output;
- sanitizer results;
- fuzz-smoke parameters and outcomes;
- binary type and dependency reports;
- checksums;
- explicit external-dependency status;
- known failures and limitations.

A report is evidence only for the binary and environment named in it.

### 6.6 Dependency policy

Pin external source by version and cryptographic digest. Preserve its license and
provenance. Prefer official upstream release artifacts and official headers.

The target c-toxcore line for rev0004 is 0.2.23, released June 3, 2026. That release
fixed a high-severity remote stack-buffer overflow and other defects. Do not substitute
an older system library merely because it links. The runtime adapter must reject an
incompatible version.

Runtime ABI loading is an isolation and testability mechanism. It is not a way to avoid
license or distribution obligations.

### 6.7 Revision archive contract

Every delivered cube increments the four-digit revision and uses the user's
America/New_York local package time:

```text
Project-Name-rev####-YYYY.MM.DD.HH.MM-summary-highlight-codename.zip
```

For this project:

```text
IoTox-rev####-YYYY.MM.DD.HH.MM-lowercase-hyphenated-slug.zip
```

The archive contains one `IoTox/` root. It includes `BOOTSTRAPROSE.md` and the hidden
`.datacube/`, but excludes Git metadata, compiler build trees, temporary identities,
caches, and editor debris. The delivered link text must be the complete filename.

---

## 7. Security invariants

These are minimum guardrails, not a complete threat model.

1. **Tox friend is not IoTox authority.** Transport admission never grants ownership,
   roles, firmware rights, data rights, or actuator capability.
2. **No vendor recovery sovereign.** No project-controlled key may reassign devices.
3. **RecallRoot remains local.** The phrase and root never cross the network or enter
   ordinary command-line history.
4. **Generated phrase strength is mandatory.** Fixed derivation permits offline
   guessing by design.
5. **One toxcore owner thread.** Business logic does not call the `Tox*` instance
   directly.
6. **Explicit route policy.** A requested Tor or I2P route must fail rather than leak
   through native networking.
7. **Local least privilege.** Runtime directories are owner-only; the control socket
   admits only the same effective user in the present Linux implementation.
8. **Bound before allocation.** Every external frame, list, string, object, and queue
   requires size and work limits.
9. **Transport delivery is not execution.** Future device commands need durable
   acceptance and terminal results.
10. **Retry is not repetition.** Hardware-affecting operations require stable IDs and
    idempotency semantics.
11. **Timeout is not cancellation.** The owner-thread queue must gain explicit deadline
    and cancellation state before it carries physical actions.
12. **State replacement is atomic and private.** Power interruption must not casually
    destroy the device's Tox identity.
13. **Status surfaces do not become covert data stores.** The event journal records
    metadata and sizes, not packet bodies or secrets.
14. **Firmware trust is independent of transport.** An authorized Tox session alone
    must never permit arbitrary executable installation.
15. **Mocks are labeled.** Test doubles never count as real-network evidence.

---

## 8. Immediate ordered work

Work from top to bottom unless new evidence changes the order.

### Gate 1 — real c-toxcore in the build

- acquire the official 0.2.23 release artifact;
- verify its published digest and signature where possible;
- retain provenance and license records;
- build it reproducibly with the available GCC/Clang toolchain;
- compile the ABI adapter against official installed headers;
- run the current binary lifecycle against the real shared library;
- retain exact evidence.

Acceptance: `iotoxd` creates, saves, and reloads a real Tox identity without the mock.

### Gate 2 — controlled two-peer native fixture

- provide controlled bootstrap and TCP-relay processes or a reproducible local fixture;
- run two independent IoTox agents;
- establish friendship through an explicit test ceremony;
- exchange HELLO frames in both directions;
- disconnect, reconnect, restart, and preserve identity;
- test relay-only and UDP-enabled paths separately;
- measure time and failure modes.

Acceptance: `Tox/native` becomes network-verified in the named fixture, not merely
adapter-verified.

### Gate 3 — local ratox-successor usability

- define stable runtime path ownership and multi-instance naming;
- materialize peer state without conflating it with authorization;
- expose friend requests safely;
- add a watchable event stream with bounded subscribers and backpressure;
- design the optional FIFO/file façade over the structured control protocol;
- keep every operation scriptable and inspectable;
- test abrupt client exit, daemon crash, stale sockets, full runtime directory, and
  restart.

Acceptance: a small shell script can use the daemon naturally without embedding
c-toxcore, while errors remain correlated and explicit.

### Gate 4 — authorization ledger skeleton

- select application signing primitives and canonical record encoding;
- define stable IoTox device identity separately from route endpoints;
- implement owner, delegated controller, roles, capabilities, epochs, and revocation;
- bind authorization to exact device, operation, expiry, and ownership epoch;
- make transport peer addition incapable of bypassing the ledger;
- fuzz all record decoders.

Acceptance: an unauthorised Tox friend can connect and exchange only the permitted
pre-authorization protocol; it cannot perform a protected operation.

### Gate 5 — durable command semantics

- bounded durable inbox and outbox;
- message IDs and correlation IDs;
- received, started, succeeded, failed, rejected, and expired states;
- explicit cancellation behavior;
- duplicate-result cache;
- clock-skew and boot-epoch rules;
- queue-full and power-loss tests.

Acceptance: retrying a completed command cannot accidentally repeat a physical action.

### Gate 6 — RecallRoot re-entry

- domain-separated owner and delegation keys;
- no-argv phrase entry path;
- fresh challenge transcript bound to device identity and ownership epoch;
- revocation and race rules;
- physical initial claim;
- phrase compromise and owner transition story;
- independent cryptographic review before high-consequence use.

Acceptance: reconstructing from the exact strong phrase can establish a new delegated
controller without revealing the phrase/root and without a vendor service.

### Later gates

- Tox file-transfer manager and signed OTA;
- owner-operated bootstrap/relay packaging and public contribution tooling;
- target-hardware measurements and fault injection;
- leak-tested Tox-over-Tor;
- experimentally validated Tox-over-I2P;
- direct Tor/I2P transports only under separate decisions;
- reconsider Mutorr only after the ratox successor is strong enough to carry it.

---

## 9. Questions the office holder must keep alive

- Does real toxcore's background traffic, memory use, reconnect behavior, and power cost
  fit the first target hardware class?
- Should native, Tor-routed, and I2P-routed Tox share one endpoint identity or use
  separately bound route identities?
- How are bootstrap lists obtained and updated without creating silent vendor control?
- What is the smallest useful ratox-compatible surface that does not pretend FIFO
  delivery equals command completion?
- How should multiple local users or containers be authorized without weakening the
  current same-user boundary?
- What exact semantics apply when a local request times out while its owner-thread
  command has begun?
- What persistent database is small, inspectable, power-loss-safe, and appropriate for
  command/result history?
- Which device classes are safe for this research system, and which require a stronger
  independently audited transport and application stack?
- How will GPL-3.0 c-toxcore distribution obligations affect product packaging and
  source delivery?
- What can IoTox contribute upstream rather than carrying indefinitely as a private
  patch?

Do not answer these questions with aspiration. Design experiments that can make them
smaller.

---

## 10. Definition of a good next revision

A next cube is good when it does at least one difficult thing more truthfully than this
one.

Examples:

- it turns real c-toxcore from unavailable into reproducibly built;
- it turns native transport from mock-binary-verified into real-network-verified;
- it makes the local surface materially more ratox-like without weakening semantics;
- it implements one narrow authorization-ledger slice with hostile tests;
- it discovers and records a reason the current design is wrong;
- it removes code or claims that cannot earn their maintenance cost.

A larger archive, more prose, or a higher test count is not automatically progress.

Before packaging:

```text
[ ] read and update this entire BOOTSTRAPROSE
[ ] update REVISION, version, codename, changelog, package, and manifest
[ ] update decision index and open questions
[ ] build default GCC and Clang lanes
[ ] run all tests and the separate process fixture
[ ] run sanitizer and fuzz smoke lanes available here
[ ] build the optional Mutorr incubator at least once if its files changed
[ ] refresh artifacts, reports, and checksums
[ ] prove the lone-entrance layout
[ ] ensure Git worktree is clean and commit the revision
[ ] create the timestamped archive from a clean staging tree
[ ] extract the archive elsewhere and rerun the retained smoke facility
```

---

## 11. Amendment note

This entrance was created for rev0004 on August 13, 2026.

It records the user's decision to hold Mutorr aside, make the ratox successor the
immediate northstar, keep Tox, retain permanent remembered/printed RecallRoot recovery,
forbid vendor reassignment authority, and require this file to be the lone visible
entrance to the hidden datacube.

rev0004 also records the first executable ratox-successor slice: `iotoxd`, `iotox`, the
structured same-user local socket, private runtime tree, event journal, configurable
bootstrap/relay seam, and a separate real-process lifecycle test over the exact toxcore
ABI mock.
