# BOOTSTRAPROSE — rev0303: Attempt-bound admission transport seam v1

This is the active construction handoff for `4UR4C10WN-rev0303`. Read it before
changing topology, discovery, admission, transport, custody, replay, receipts,
source, tests, documentation, lineage, or package structure. Historical revision
files are provenance. The maintained present-tense map is listed below.

## Product sentence

> **4UR4C10WN is a portable encrypted private post office that can carry its
> runtime, source, tests, documentation, cryptographic Office state, and an
> embedded I2P router; it accepts explicit human authority, supports
> recipient-absent delivery, survives interrupted work, and reports only what
> retained evidence proves.**

The governing rule remains:

> **Never turn uncertainty into an automatic retry, false success, or broader
> permission.**

The ordinary surface should remain simple. Exact evidence and refusal may be
deep underneath it.

```text
Simple surface
Forensic depth underneath
```

## Governing offline-mail law

The architecture is governed by this ordinary journey:

```text
Alice creates an account.
Alice adds Bob by pasting one Contact string in a dedicated Contacts screen.
Bob is completely offline.
Alice sends by selecting Bob, with no Posthouse or grant setup.
Alice obtains honest signed custody and then goes completely offline.
Bob returns and retrieves/authenticates the Letter without Alice returning.
```

Every participating Office contributes bounded Posthouse capacity and may be an
eligible holder for other Offices by default. Users may choose or exclude
holders, but Routes, Posthouses, service cards, grants, epochs, placement,
receipt thresholds, and poll targets are not ordinary prerequisites. This means
bounded universal eligibility, not broadcasting every Letter to every Office.

The inherited fixed-peer data plane remains necessary but insufficient. Alice
and Bob must independently converge on an overlapping authenticated holder view,
current admission must work across epoch rollover while Bob is absent, and Bob's
discovery must not depend on a receipt stranded with offline Alice. Global
public-stranger Sybil resistance remains a non-claim; it does not block the
known-Contact small network.

Read these before topology work:

```text
docs/SEAMLESS-OFFLINE-TOPOLOGY.md
docs/POSTAL-COMMONS-DEFAULTS.md
bootstrap/README.md
```

The provisional first-network policy remains three selected holder identities,
two required signed custody receipts, 90-day initial custody, conservative
safe-until display, bounded repair/renewal, inspectable seed roots, signed
service gossip, and contribution accounting. Holder identity means a
cryptographic service root; it does not imply distinct machines, operators,
networks, or jurisdictions.

## Maintained present-tense documents

```text
docs/CURRENT-PRODUCT.md
docs/CURRENT-ARCHITECTURE.md
docs/CURRENT-CONSTRUCTION-PLAN.md
docs/CURRENT-THREAT-MODEL.md
docs/DURABLE-WRITER-INVENTORY.md
docs/HUMAN-QUICKSTART.md
docs/SEAMLESS-OFFLINE-TOPOLOGY.md
docs/POSTAL-COMMONS-DEFAULTS.md
bootstrap/README.md
```

rev0303 contract and evidence:

```text
docs/REV0303-ATTEMPT-BOUND-ADMISSION-TRANSPORT-V1.md
docs/REV0303-EVIDENCE.md
docs/REV0303-LOCAL-INTEGRATION-REVIEW.md
```

Retained rev0302 discovery, rev0301 attempt evidence, rev0300 exact-package
durable acceptance, rev0299 mailbox-first admission, rev0298 authenticated
Posthouse view, rev0296 sender recovery, rev0295 reconciliation, rev0294 First
Letter, rev0293 Task / Recovery, and earlier documents remain provenance.

Machine-checked writer contract:

```text
tools/durable_writer_inventory.py
tools/durable_writer_contracts.json
```

The selected writer census is intentionally scoped to the same 15 reviewed
Python modules and 124 sites. It is not a claim that either the rev0300 DMS1
exact-spend transaction or the rev0301 C++ SQLite PAE1 journal is inside that
census. Those boundaries are reviewed and tested separately. rev0302 and
rev0303 add no durable writer. PAT1 publishes only through the existing PAE1
journal. Do not cosmetically widen or relabel the retained contract.

## Exact returned parent

The exact parent is the completed rev0302 host-qualified handoff. Its ZIP,
carrier, external BOOTSTRAP, and complete carried project were checked at intake.
The carrier verified and materialized its source before construction.

```text
Parent archive SHA-256:
f2267751956d1b36a00b1aed4280eebd52054cd3d4bbf09eb887c4b16c91d240

Parent carrier SHA-256:
3bfe7224b14e1d77309b2f94bbdb2423ce528ad83e3ada91fa5f9efb2839cff7

Parent runtime SHA-256:
d55ff9087f9d84c565ff6e0b55504896f7322ac6f873a3bd369167f35933d4af

Parent resource-bundle SHA-256:
22f9100faf6369c700520b9b6e979bf19782143d701c0afe608f7917e0bf788e0

Parent external and embedded BOOTSTRAP SHA-256:
6098a42f4805405272ede18a5724ec23a2650e9f084c5b34fe116f1cc0ce6323

Parent canonical project-tree SHA-256 v2:
77d313d8ade069e2af3a18b7c9c93815ad477b924cc36ef0cb5d43a18b3b2fe5

Parent project: 12,234 files, 1,929 directories including root,
714,373,943 file-content bytes.
```

Every edited parent path must retain its exact bytes and mode beneath
`history/rev0303-parent-preimages/`. Added paths need no invented preimage. No
parent path is removed and no parent file or descendant-directory mode is
intentionally changed. The preimage manifest is verified separately from
complete project comparison.

## Exact two-object package contract

The release ZIP contains exactly these regular files, in this order:

```text
4UR4C10WN          mode 0755
BOOTSTRAPROSE.md   mode 0644
```

No directory entries. The external BOOTSTRAP, embedded project-root BOOTSTRAP,
and `docs/BOOTSTRAPROSE.md` are byte-identical. The carrier verifies its runtime,
bundle, and complete image and materializes its exact carried project. Keep
checksums and final delivery evidence detached to avoid self-hash circularity.
Historical files and the founding ancestor remain carried, not flattened away.

## Retained topology before rev0303

The current layers remain deliberately separate:

```text
PHS1 / PHO1 / PHV1
    dual-authorized service facts, provenance and convergent view

PME1 / PDA1 / PDS1 / PRD1
    Contact-anchored historical candidate replay and current route resolution

PAR1 / PAG1
    exact current package admission request and signed holder decision

PAE1
    one durable request/route authorization, START and response/outcome evidence

PXS1 / DMS1 / FSR1
    exact local durable package acceptance and signed custody evidence
```

Observation is not review. Review is not approval. Admission is not deposit.
Attempt is not custody. Custody is not retrieval, authenticated opening, explicit
ACK, or human reading.

## rev0303 topology decision: transport consumes evidence

rev0303 connects one exact authenticated discovery result and one exact durable
attempt to one bounded transport operation. The adapter does not choose topology:

```text
retained Contact capability
+ package-independent PME1 mailbox-placement epoch
+ recipient-root PDA1 anchor history
+ bounded service-signed PDS1 exact PHV1 snapshots
        ↓ independently rebuild PRD1
one exact current holder and route
        +
canonical PAR1 + one already-durable PAE1 STARTED handle
        ↓ PAT1 move-only one-use binding
one dialer invocation and one ordered byte stream
        ↓
one PAT1 PAR1 frame + one PAT1 PAG1 frame + orderly EOF
        ↓
canonical PAG1 authentication and PAE1 publication only
```

PAT1 has no alternate-holder selector, retry method, fan-out loop, package
writer, custody conversion, renewal, repair, or recipient poll operation.

## Exact discovery and attempt binding

Binding does not trust a caller-provided route assertion. It rebuilds PRD1 from
the complete supplied Contact, placement, anchor, and snapshot evidence at an
explicit evaluation time. It requires:

```text
valid Contact and PME1 mailbox epoch
PAR1 mailbox epoch and quorum equal discovery policy
complete recipient polling and current new-placement authority
no truncated PRD1 diagnostics
one exact poll target matching PAR1:
    stable service identity
    statement fingerprint
    route identity
    storage signing key
    service admission epoch
one PAE1 START naming the same request fingerprint and exact route
START time at or after discovery evaluation
PAE1 deadline within PAR1 expiry
PAE1 response ceiling within PAT1/PAG1 bound
```

The bound result is move-only and one-use. It retains canonical PAR1 bytes, the
private PRD1 plan digest, exact selected holder facts, and the PAE1 START handle.
It contains no second route or callback capable of manufacturing another
attempt.

A PRD1 plan digest is private replay evidence. It is not a public mailbox name,
transport token, holder signature, or custody receipt.

## PAT1 wire boundary

PAT1 carries canonical PAR1 and PAG1 payloads inside one small frame:

```text
4 bytes   ASCII magic "PAT1"
4 bytes   version = 1
4 bytes   frame kind
8 bytes   payload length
32 bytes  SHA-256 of exact payload
N bytes   canonical PAR1 or PAG1
```

The header is exactly 52 bytes. Request and response payloads are each bounded to
4,096 bytes. The reader consumes and validates the header before allocating the
payload. It rejects:

```text
unknown magic, version, or kind
zero or oversized declared length
truncation
payload digest mismatch
wrong one-stream phase
trailing bytes after the one response
noncanonical or unauthenticated PAG1
PAG1 bound to another PAR1
```

PAT1 framing is not service authority. PAR1/PAG1 signatures and exact current
facts remain mandatory.

## One adapter invocation and deadline law

Transport policy is validated before the bound attempt is consumed. This allows
a local policy error to be corrected without losing the one in-memory handle.
The sum of connect and session timeouts may not exceed the remaining durable
PAE1 half-open deadline.

After consumption, the dialer receives one exact route and may be called once.
The stream carries one request frame and one response frame. There is no route
fallback, response callback registry, duplicate callback, or second-use path.

Known outcomes are mapped to PAE1 evidence:

```text
connect timeout or deadline boundary          → TIMED_OUT
connection refusal / unreachable / failure    → DISCONNECTED
write, read, frame, EOF, or PAG1 failure       → DISCONNECTED
exact authenticated admitted PAG1             → RESPONSE_OBSERVED
exact authenticated holder refusal PAG1        → REFUSED
```

`DISCONNECTED` is uncertainty. It is not proof that the holder received nothing.
A network refusal is not an authenticated PAG1 refusal.

Unknown adapter exceptions and process loss leave the durable PAE1 row
`STARTED`. They do not authorize a replacement attempt.

## PAE1 response preflight correction

rev0303 exposes a pure bounded PAG1 validator. `record_response` now validates
the exact owner, request, observation time, response ceiling, canonical bytes,
and signatures before consuming the move-only START handle. PAT1 can therefore
classify malformed response bytes and publish one explicit transport outcome.

The durable publication path repeats validation. SQLite or publication failure
after successful preflight still consumes the handle and remains uncertainty.
This change does not turn response validation into admission capability.

## Process and publication-loss boundaries

The focused fixture exercises:

```text
after consuming START before connect
 after connect before request write
 after request write before response read
 after response read before PAE1 publication
 after PAE1 response COMMIT before ordinary return
```

The first four retain only exact durable `STARTED` evidence. The last retains the
exact committed authenticated response despite caller publication uncertainty.
No boundary creates automatic retry, alternate-holder selection, fan-out,
deposit, or custody authority.

## Local-control qualification and claim ceiling

The focused fixture uses two real IPv4 loopback streams through the existing
narrow `IStreamDialer` / `IByteStream` interfaces:

```text
one admitted PAG1 response
one signed capacity-refusal PAG1 response
```

Scripted streams cover connect timeout/refusal, wrong frame kind, declared
response overflow, trailing bytes, digest damage, PAG1 substitution, PAR1
substitution, discovery-evidence substitution, deadline widening, use after
consumption, and the five loss boundaries.

Loopback success is not public-I2P qualification. rev0303 has no holder-side PAT1
responder, live embedded-I2P admission campaign, route-control proof, capacity
reservation, deposit, custody, recipient polling, retrieval, renewal, repair, or
trusted-clock claim.

## Executable and command boundary

```text
source/include/fourcrown/posthouse_transport.hpp
source/src/posthouse_transport.cpp
```

The active build graph contains 159 native translation units. The command
surface adds exactly two entries:

```text
posthouse-attempt-transport-status   READ_ONLY
posthouse-attempt-transport-lab      TEMPORARY_LOCAL_WRITE
```

The status reports format, bounds, authority separation, and claim ceiling. The
lab creates and removes one owner-local temporary PAE1 SQLite journal and opens
only local IPv4 loopback sockets. It does not open a user Office or embedded
router.

## Focused qualification target

The exact candidate must retain at least:

```text
PAT1 checks                                      41
bound exact attempts                             15
adapter invocations                              14
real local-control loopback connections           2
exact request frames received                     2
authenticated admitted responses                  1
authenticated signed refusals                      1
explicit timeout observations                     2
explicit disconnect observations                  6
malformed or substituted refusals                  9
process-death boundaries                          4
post-COMMIT publication-uncertainty boundaries    1
public-I2P operations                              0
automatic retries or alternate routes              0
fan-out, deposit, or custody actions               0
```

Counts are assertions and observations, not public-network journeys. The final
exact carrier must also retain the PRD1, PAE1, PXS1, PAR1/PAG1, PHV1, DMS1,
Office-control, command-discovery/catalog, First Letter, OPUI, command-split,
selected-writer, BOOTSTRAP, lineage, materialization, and packaging gates
recorded in detached release evidence. Do not turn a selected gate into an
exhaustive CLI, full aggregate self-test, physical-power-loss, trusted-clock,
public-I2P, or portable-release claim.

## Development corrections retained honestly

The first loopback fixture asked the existing LBS1 listener to wait 3,000
milliseconds even though its compiled accept-wait ceiling is 1,000 milliseconds.
LBS1 correctly returned a failed accept. The final fixture uses the existing
bound; no product timeout was widened.

The first statistics assertion expected at least three ordinary response rows,
but the fixture intentionally creates exactly two: the admitted loopback response
and the post-COMMIT/pre-return loss case. The final fixture checks the complete
exact 21-row state distribution. No success is claimed from either failed
intermediate run.

## Next topology gate: holder-side exact admission responder v1

The client half is now narrow enough that the server half can be defined without
letting a listener become deposit or custody authority:

```text
one already-accepted bounded stream
        ↓
one PAT1 ADMISSION_REQUEST frame and canonical PAR1
        + current local PHS1 / storage identity
        + explicit current admission policy and clock
        ↓
one canonical signed PAG1 admission or refusal
        ↓
one PAT1 ADMISSION_RESPONSE frame, then close
```

Required law:

- accept one request frame only and bound it before allocation;
- authenticate the exact Contact/PAR1 request and require exact local current
  service statement, route identity, storage key, admission epoch, rules,
  protocol, limits, and half-open validity;
- decide from explicit local policy and signed request facts;
- sign one canonical PAG1 admission or refusal and write one response;
- retain response-publication uncertainty without inferring client receipt;
- do not reserve quota, spend admission, accept package bytes, write DMS1, issue
  FSR1, retry, select another holder, fan out, or claim custody;
- qualify local-control accepted-stream, overflow, truncation, substitution,
  stale-tip, key/epoch, policy, and process-loss boundaries before live I2P.

After both client and holder seams are exact, qualify one embedded-I2P adapter.
Durable recipient polling intent remains separate and must bind one exact PRD1
digest and bounded campaign rather than becoming an implicit retry engine.

## Build and release truth

The intended artifact in this environment is a strict all-Clang, stripped,
dynamically linked x86-64 GNU/Linux **host-qualified development carrier**. The
pinned static-musl recipe remains source-carried. Do not label this artifact
portable or release-qualified unless the exact final carrier separately proves
the unavailable toolchain and portability gates.

The final evidence must state honestly whether the environment supplied:

```text
Nix executable
musl C++ compiler
static Boost.Program_options archive
```

Current public-I2P operation, trusted-clock qualification, physical-power-loss
durability, operator independence, accessibility/localization, exhaustive CLI,
full aggregate self-test, and cross-environment reproducibility remain separate
campaigns unless detached evidence says otherwise for the exact bytes.

## Reproduction and continuation commands

From the project root:

```bash
make check-repository-inputs
python3 tools/build_host.py --package --jobs 6 --optimization 0
make posthouse-attempt-transport-test
make posthouse-discovery-test
make posthouse-exchange-test
make posthouse-admission-test
make posthouse-storage-test
make posthouse-view-test
./work/releases/host/4UR4C10WN posthouse-attempt-transport-status
./work/releases/host/4UR4C10WN posthouse-attempt-transport-lab
./work/releases/host/4UR4C10WN posthouse-discovery-lab
./work/releases/host/4UR4C10WN posthouse-exchange-lab
./work/releases/host/4UR4C10WN posthouse-admission-lab
./work/releases/host/4UR4C10WN posthouse-storage-lab
./work/releases/host/4UR4C10WN posthouse-view-lab
./work/releases/host/4UR4C10WN mail-store-lab
./work/releases/host/4UR4C10WN office-controls-lab
./work/releases/host/4UR4C10WN command-discovery-lab
./work/releases/host/4UR4C10WN commands
python3 tools/first_letter_test.py --binary ./work/releases/host/4UR4C10WN
python3 tools/office_ui_contract_test.py --binary ./work/releases/host/4UR4C10WN
python3 tools/main_command_split_test.py \
  --binary ./work/releases/host/4UR4C10WN \
  --parent-binary /path/to/rev0302/4UR4C10WN \
  --receipt /tmp/rev0303-main-command-split.json
python3 tools/durable_writer_inventory.py
python3 tools/verify_preimage_manifest.py \
  history/rev0303-parent-preimages/PREIMAGE-MANIFEST.json.md
./work/releases/host/4UR4C10WN verify
./work/releases/host/4UR4C10WN bootstrap-verify BOOTSTRAPROSE.md
./work/releases/host/4UR4C10WN /run
```

When continuing, prefer a stronger topology if retained evidence supports it,
but preserve every authority separation above. Do not let a convenient dialer,
listener, seed, observer, sender receipt, or package-specific result become the
topology by accident.
