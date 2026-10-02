# Cloudtainer build report — IoTox rev0013

**Revision:** rev0013  
**Version:** 0.13.0  
**Codename:** Ordinary Cargo  
**Office date:** 2026-08-14, America/New_York  
**Immediate northstar:** one-binary modern ratox successor  
**Primary external dependency target:** c-toxcore 0.2.23  

## 1. Executive finding

rev0013 advances the executable ratox-successor surface rather than only adding proof machinery.
The single public product binary, `iotox`, now gives each projected peer three finite-file lanes in
addition to the message, action, and durable-command lanes established earlier:

```text
file-send       absolute source path
file-receive    provider file number + TAB + absolute destination path
file-control    provider file number + TAB + pause|resume|cancel
```

The FIFOs carry bounded control records. They never carry file bytes. The existing C++ file-transfer
manager owns toxcore file numbers, file ids, requested chunks, temporary receive files, atomic
publication, cancellation, and two-sided pause truth. The runtime tree projects current transfer
state under `peers/<tox-public-key>/files/` and preserves bounded human evidence in `file-events`.

The final rev0013 source completed the project-owned clean build matrix:

```text
GCC 14.2 debug                         8/8 CTest entries
GCC 14.2 release                       8/8 CTest entries
Clang 17 debug                         8/8 CTest entries
Clang 17 ASan + UBSan                  8/8 CTest entries
GCC 14.2 ThreadSanitizer               8/8 CTest entries
GCC 14.2 linked to host Argon2         8/8 CTest entries
Mutorr preservation configuration     10/10 CTest entries
Clang 17 libFuzzer                     5 targets × 5,000 runs
registered C++ checks                  110
```

The one-binary process fixture, exact consumed-ABI toxcore provider, filesystem surface, restart
continuity, and repeated owner-thread/session path are exercised locally. Genuine Tox bootstrap,
DHT, NAT traversal, relay interoperability, public-network file transfer, Tox/Tor, and Tox/I2P are
not proved here.

The pinned standalone builder was attempted after the final owned-source matrix. It stopped before
compilation because this shell could not resolve `download.libsodium.org`. That is retained as an
external dependency/network failure, not represented as a toxcore build result.

## 2. Product construction in this revision

### 2.1 One product, one executable

The installed product contract remains one executable named `iotox`. The same binary acts as:

- long-running device agent;
- local Unix client;
- status and evidence reader;
- peer-admission operator;
- RecallRoot generator and verifier;
- message, action, command, and finite-file operator.

Static libraries, exact ABI provider doubles, process fixtures, test runners, fuzzers, and Mutorr
incubator programs exist only inside build or evidence configurations. They are not additional
installed products.

### 2.2 Six ordinary peer-local write lanes

A projected peer now has:

```text
message         live normal Tox text
message-action  live action Tox text
action          compatibility name for message-action
command         durable IoTox command admission
file-send       finite local source-file admission
file-receive    finite local receive-destination admission
file-control    finite live-transfer control
```

The file names are intentionally ordinary. Their semantics are not casual:

- a successful `write(2)` to a FIFO proves only kernel admission;
- a parsed record may still be rejected by IoTox;
- a toxcore call may still fail;
- a remote peer may disconnect;
- a receive may be admitted but not complete;
- a completed object may still be hostile content;
- no received file gains execution, installation, firmware, or authorization authority.

`file-events` and the typed live transfer projection carry semantic evidence. This preserves
ratox's useful “write a name to a file” experience without turning the FIFO into a false transfer
receipt.

### 2.3 Finite-file send

`file-send` accepts one LF-terminated byte-line record containing an absolute local source path.
IoTox opens the source as a regular file before asking toxcore to advertise it. The opened descriptor
is retained so later chunk requests refer to the admitted object rather than reopening a mutable
path on every callback.

The user-visible basename is offered as file metadata. It is not trusted as a destination path on
the receiving side.

A successful local admission means:

```text
source opened and validated
provider file-send call accepted
direction and provider file number recorded
transfer projected
semantic event appended
```

It does not mean that a peer accepted, received, verified, or safely used the bytes.

### 2.4 Finite-file receive

Incoming toxcore file offers remain paused. `file-receive` accepts:

```text
<provider file number><TAB><absolute destination path><LF>
```

The manager opens a private temporary file in the destination directory and only then asks toxcore
to resume the incoming transfer. A successfully admitted receive record is frozen as evidence even
if a tiny transfer completes and disappears from the live table before the local reply is encoded.

Completion requires the provider's terminal zero-length chunk callback after the exact requested
bytes have been written. The temporary file is synchronized and atomically renamed onto the chosen
destination. Incomplete or failed transfers do not publish a partial destination under the final
name.

This is local publication discipline, not content trust. The application above IoTox must still
validate type, digest, signature, version, target hardware, and policy before using sensitive data.

### 2.5 Control and two-sided pause

`file-control` accepts:

```text
<provider file number><TAB>pause<LF>
<provider file number><TAB>resume<LF>
<provider file number><TAB>cancel<LF>
```

The manager records local pause and peer pause independently. A transfer is runnable only when both
sides are resumed. A peer-originated control callback is not fabricated from a successful local
`tox_file_control()` call.

This distinction follows the reviewed c-toxcore 0.2.23 contract. The local API reports whether the
local control request was accepted. The receive-control callback reports only a control message
received from the remote friend. Collapsing those into one bit would let a local resume erase a
peer pause or let a test provider invent remote evidence.

### 2.6 Live handles and bounded evidence

A toxcore file number is scoped to one friend, one direction-sensitive live transfer context, and
may be reused after terminal cleanup. IoTox therefore does not treat it as durable object identity.
The 32-byte file id is projected when available as stronger transfer identity evidence, but
rev0013 does not yet use it to resume transfers across process restart.

Terminal transfers leave the live projection. Human events remain in a bounded journal. High-rate
chunk callbacks are not copied into every peer's human journal; typed state and bounded low-level
transport evidence preserve observability without allowing routine file traffic to grow an
unbounded text log.

## 3. Exact source and ABI research applied

The implementation was checked against the tagged c-toxcore 0.2.23 public header and related source,
ratox's file surface, and Toxic's maintained transfer code. The operative findings are recorded in:

```text
docs/research/c-toxcore-0.2.23-ratox-finite-file-control-rev0013.md
docs/decisions/0046-ratox-file-fifos-name-finite-local-files.md
docs/decisions/0047-file-control-tracks-two-sided-pause.md
```

The findings that directly constrain code are:

1. Calls involving one `Tox*` must be serialized. IoTox keeps one owner thread.
2. An incoming file offer begins paused from the receiver's perspective.
3. Local and peer pause are independent and both sides must resume.
4. Successful local file control does not cause the remote-control callback locally.
5. File numbers are friend-scoped live handles and may be reused.
6. File ids are the available cross-session transfer identifiers.
7. The sender must return exactly the requested chunk unless cancellation or terminal semantics
   apply.
8. A zero-length terminal chunk signals completion at the callback boundary.
9. ratox's simplicity is worth preserving, but a path/FIFO operation must not be confused with
   durable transfer truth.

No web source or static review is promoted to runtime interoperability evidence. Those sources tell
us what program to attempt. The exact provider and tests tell us what owned code currently does.
Only a real toxcore build and genuine peers can close the external gate.

## 4. Defects exposed and corrected during construction

### 4.1 The mock echoed local control as a fake peer callback

The inherited exact provider returned successful local file-control calls and then invoked the
registered receive-control callback as though the peer had sent the same control. That violated the
reviewed callback direction and would have hidden an incorrect one-bit pause model.

The provider now changes local provider state without manufacturing remote evidence. Tests inject
peer control separately when they need to exercise the callback path.

### 4.2 `file-control` required TAB while its FIFO policy rejected TAB

The grammar deliberately uses TAB to keep paths byte-preserving and avoid shell-style tokenization.
The first runtime-tree integration attempt configured the control FIFO with a printable-text policy
that rejected TAB before parsing. The binary process fixture exposed the contradiction.

The lane now uses the bounded byte-line policy. The semantic parser, not a generic printable filter,
owns the exact `number<TAB>action` grammar.

### 4.3 A successful receive resume could race immediate completion

A tiny transfer can complete in the provider iteration immediately after the local resume succeeds.
If the manager looked up only the live transfer after the call returned, it could report “not found”
even though admission and completion both succeeded.

The manager now returns a frozen admitted snapshot once the provider accepted resume. Terminal
cleanup may remove the live projection afterward, but it cannot retroactively turn successful
admission into failure.

### 4.4 Version truth found one stale process assertion

After the source was promoted to `0.13.0/rev0013`, the process test still expected `revision=12` in
one status projection. The compiled identity gate failed. The assertion now checks revision 13 and
the complete suite proves the current version rather than merely naming it in prose.

### 4.5 Build execution limits were not converted into false product failures

Earlier development invocations were interrupted by the cloud command boundary while Ninja was
still compiling. The final evidence run used the project wrapper and completed all required lanes
with its lock, clean build directories, warnings-as-errors policy, and unchanged sanitizer flags.
The retained final matrix records the completed run and its zero exit marker.

## 5. Verification detail

### 5.1 Compilers and configurations

The final wrapper identified:

```text
GNU C/C++ 14.2.0
Clang C/C++ 17.0.0
```

Every normal configuration used C++20 and warnings as errors. The sanitizer configurations retained
their normal project flags:

```text
Clang: AddressSanitizer + UndefinedBehaviorSanitizer, halt on error
GCC:   ThreadSanitizer, halt on error
```

The matrix also built and tested a configuration linked to the host `libargon2.so.1`, independently
of the runtime-loaded exact test provider.

### 5.2 Default CTest entries

Each normal lane ran eight entries:

```text
iotox.unit-and-integration
iotox.binary-process-lifecycle
iotox.client-version
iotox.client-help
iotox.bootstrap-seeds
iotox.recall-generate
iotox.client-absent-daemon
iotox.lone-entrance-layout
```

The Mutorr preservation configuration added its research cube demonstration and benchmark smoke,
for 10/10 passing entries. This does not make Mutorr part of the immediate product northstar.

### 5.3 Registered C++ checks

The final unit/integration registry contains 110 C++ checks. File-related coverage includes:

- exact consumed file ABI types and symbols;
- outgoing source admission;
- incoming offer projection without premature activation;
- private receive staging and atomic publication;
- exact chunk request handling;
- independent local and peer pause;
- pause, resume, and cancel control parsing;
- terminal cleanup and reusable live handles;
- runtime-tree FIFO ownership, modes, and help text;
- process-level ordinary writes through all three file FIFOs;
- one binary crossing CLI, local IPC, Agent, owner thread, exact provider, callback, and evidence
  projection.

### 5.4 Fuzz smoke

The final Clang 17 libFuzzer smoke ran 5,000 units for each target:

```text
iotox_frame_fuzzer
iotox_session_fuzzer
iotox_local_control_fuzzer
iotox_command_fuzzer
iotox_authority_fuzzer
```

No crash, sanitizer termination, or retained artifact was reported. The run copies reviewed seed
corpora into build-local mutable corpora first; it never rewrites source seeds.

The smoke is a regression gate, not a security proof. It does not cover toxcore's implementation or
real network scheduling.

### 5.5 Repeated Agent/session path

`tools/agent-session-stress.sh` first requires one complete passing direct registry, discovers the
principal ratox-successor Agent integration shard from that linked output, and executes the shard 100
times in fresh test processes. That shard proves the callback-owned online epoch, deliberate first HELLO queue pressure, exact
retry, transcript confirmation, authority binding, ordinary message/action/command/file traffic,
restart state, and orderly shutdown against the exact provider. Each repetition must independently
pass; the retained log contains exactly 100 `run=NNN PASS` records and a zero exit marker.

### 5.6 Retained artifact discipline

The artifact refresher requires, rather than merely describes:

- zero matrix exit status;
- `final-source-matrix=pass` in the complete log;
- all compiler/sanitizer `LastTest.log` files;
- all five fuzzer executables and the final fuzz log;
- linked-Argon2 binary and tests;
- Mutorr preservation tests;
- exactly 100 passing Agent repetitions;
- debug and release product binaries;
- exact provider and process-test binaries.

It then reruns the direct tests from copied binaries, the binary process fixture, the one-binary
mock-node lifecycle, release installation, checksum verification, and offline prebuilt smoke before
writing a new `SHA256SUMS`.

## 6. Standalone and genuine-Tox status

The intended standalone build uses pinned official source archives:

```text
libsodium 1.0.22
Argon2 20190702
c-toxcore 0.2.23
```

The final attempt exited with curl status 6 while fetching the first archive because the shell could
not resolve `download.libsodium.org`. Therefore the following remain unexecuted in this environment:

```text
official source-linked libsodium
official source-linked c-toxcore
fully source-linked one-binary product
two genuine Tox peers
public bootstrap and DHT
NAT traversal
TCP relay path
real text receipts
real finite-file callbacks
Tox over Tor
Tox over I2P
```

The exact dynamic provider remains valuable because it tests the consumed ABI boundary and lets the
owned C++ program move forward. It is not a substitute for the external gate.

## 7. Security and operational boundaries retained

rev0013 does not weaken the accepted ownership model:

- Tox friendship is transport admission, not ownership or actuator authority.
- RecallRoot remains a permanent, reproducible owner root under the frozen Argon2id derivation
  contract.
- Offline phrase guessing is structurally possible; generated phrase strength is mandatory.
- IoTox has no vendor reassignment key.
- The signed local authorization ledger owns roles, capabilities, epochs, and revocation.
- Application commands require transcript-bound authority above Tox transport identity.
- Received files are untrusted bytes.
- A local path is a mutable name, not identity and not authority.
- Same-UID local writers remain inside the present trust boundary; stronger multi-user isolation is
  not claimed.
- Transfer recovery across disconnect or restart is not implemented.
- Tox/Tor and Tox/I2P remain reserved and fail closed.

## 8. What rev0013 establishes

The strongest honest statement is:

> IoTox rev0013 is a compiled one-binary C++20 ratox-successor foundation whose owned process and
> filesystem path can admit finite local file sends and receives, track exact toxcore-style chunks,
> publish completed destinations atomically, expose pause/resume/cancel through ordinary peer-local
> FIFOs, and preserve two-sided control truth against an exact consumed-ABI provider.

It does not establish:

> that the source-linked product builds in this shell, that two genuine Tox peers interoperate, or
> that any reserved privacy route works.

## 9. Immediate continuation

The next code should deepen the ratox successor rather than broaden into Mutorr or direct overlay
transports. In order:

1. Build the pinned official providers on a networked CLI and compile the linked `iotox` product.
2. Run two genuine peers through controlled bootstrap/relay infrastructure.
3. Drive literal normal/action text and receipts through the existing surface.
4. Drive finite file offer, admission, chunks, two-sided pause, cancellation, completion, and
   checksum comparison through real toxcore.
5. Correct every ABI, callback, timing, shutdown, and persistence mismatch revealed by that run.
6. Add explicit friend lifecycle operations and durable peer metadata without making friendship an
   authority grant.
7. Design transfer recovery around file ids and persisted application metadata only after real
   provider behavior is measured.
8. Preserve one public executable and the ordinary filesystem surface throughout.

The product should continue to feel simple because the hard distinctions are implemented inside it,
not because the distinctions are omitted.

## 10. Retention closure

After the final source, office record, and reproducible stress tool were frozen, the strict artifact
refresher completed in `full` mode. It reran the copied direct and process binaries, the no-build
one-binary mock lifecycle, and release installation. The resulting current evidence states:

```text
registered C++ checks                 110 passed
normal compiler/sanitizer lanes       8/8 each
Mutorr preservation                   10/10
Agent/session fresh-process stress    100/100
public installed executables          1
retained evidence mode                full
offline prebuilt smoke                 pass
SHA256SUMS verification                pass
```

The final archive must still be extracted and rechecked as an object in its own right. Retained
checksums prove the files named by the evidence set; they do not prove the omitted real-network
claims.

