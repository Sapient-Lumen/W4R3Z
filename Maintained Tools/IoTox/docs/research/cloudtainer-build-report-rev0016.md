# Cloudtainer build report — IoTox rev0016

**Revision:** rev0016
**Version:** 0.16.0
**Codename:** Guarded Authority
**Final-source verification date:** 2026-08-16, America/New_York
**Public product executable:** `iotox`
**Owned implementation language:** C++20
**Pinned c-toxcore target:** 0.2.23

## 1. Executive result

rev0016 closes Ratox prerequisite R2 with an explicit, signed authority-ledger v2 migration. It does
not reinterpret any v1 byte or silently widen any v1 principal. The durable v1 capability mask stays
`0x7f`; v2 adds bit 7, `interactive.terminal`, under a new `0xff` mask. The source-level name
`kAllCapabilities` intentionally retains its v1 meaning so recompilation alone cannot grant terminal
authority.

A v1 ledger reaches v2 through one exact `migrate-v2` record. That record is encoded and signed in a
separate v2 domain, extends the exact v1 tail, is self-signed by an active owner, and preserves the
owner's exact v1 capabilities. Terminal authority can appear only in a later signed v2 grant. Role
ceilings, parsing, rendering, record validation, delegation, ownership transition, and capability
sessions are all format-aware.

The ledger now has a separate 192-byte private rollback guard. It records one committed exact head
and, during atomic replacement, one pending exact head. Startup accepts the committed state, the
completed pending state, or the precise interrupted pre-replace state and rejects unrelated ledger
rollback, deletion, or fork. This is a local consistency guard, not a claim that coordinated
replacement of both ledger and guard is impossible.

Capability-session feature bit 24, `authorization-ledger-v2`, binds the ledger format into challenge,
proof, and confirmed-session state. A v2 proof is unavailable unless both peers negotiated that bit;
a transcript or payload-format downgrade fails closed. Local and remote RecallRoot signing clients
verify the exact daemon-prepared action, format, role, capability set, principals, sequence policy,
and time fields before releasing a signature.

The terminal service itself remains disabled. Feature bit 23 is still unset, and rev0016 adds no PTY,
shell/profile adapter, or remote terminal dispatch.

## 2. Final verification

The exact executable source passed the clean maintained matrix:

```text
171/171 compiled owned C++ checks through the fixture-aware CTest registry
8/8 CTest entries under GCC debug
8/8 CTest entries under strict GCC -O3 release
8/8 CTest entries under Clang debug
8/8 CTest entries under Clang AddressSanitizer + UndefinedBehaviorSanitizer
8/8 CTest entries under GCC ThreadSanitizer
8/8 CTest entries with host-linked Argon2
10/10 CTest entries in the Mutorr preservation configuration
7 Clang libFuzzer targets x 5,000 units = 35,000 sanitizer-backed executions
```

The matrix finished with `final-source-matrix=pass`. No fuzzer emitted a crash artifact. The seven
fuzzers cover the outer frame, session payload, local control packet, durable command codecs,
authority record/session formats, Ratox frame, and complete interactive-session/quota-directory
state. The authority corpus includes a valid v2 migration record and v2 challenge/proof seeds.

The dedicated Agent/session harness then rediscovered the linked registry index and exercised the
full mock-toxcore Agent/session case 100 times. All 100 runs passed at discovered shard 1/171. Its
retained transcript is accepted only when every numbered run appears once, the target test passes,
and the final summary is exact.

During clean Clang validation, the authority CLI process fixture exposed a real harness race: a
command that correctly rejected its arguments could exit before the parent wrote the RecallRoot
phrase, causing the parent test process to receive `SIGPIPE`. Both process helpers now preload their
small bounded stdin payload into an empty pipe before spawn/fork and require it to fit the discovered
`PIPE_BUF`. Repeated focused Clang runs and the complete clean matrix passed afterward. Product
signal behavior was not weakened to hide the defect.

## 3. Compiler and source environment

```text
Kernel:  Linux 6.18.35 x86_64 GNU/Linux
CMake:   3.31.6
Ninja:   1.12.1
GCC:     g++ (Debian 14.2.0-19) 14.2.0
Clang:   17.0.0
```

Warnings are errors in the maintained lanes. The final owned `include/`, `src/`, and `tests/` C/C++
surface contains:

```text
105 implementation/header/test files
60,446 lines
171 registered owned C++ checks
```

Including the preserved Mutorr incubator yields 117 C/C++ files and 61,982 lines. Mutorr remains
buildable but is not linked into the default product and did not determine the authority design.

## 4. Source-linked standalone result

The exact pinned archives were verified before extraction:

```text
c-toxcore 0.2.23  b0349f4829d3d1699a77e199850f870f48d376e2baaf2c69d27b28571c498cfe
cmp 52bfcfa17d2e    4abfd641dd5ccba04b6e0ced04a79755fa70709290b3ba15dbd4b4a2de345ed0
libsodium 1.0.22   adbdd8f16149e81ac6078a03aca6fc03b592b89ef7b5ed83841c086191be3349
Argon2 20190702    daf972a89577f8772602bf2eb38b6a3dd3d922bf5724d45e7f9589b5e830442c
```

The source-linked build compiled c-toxcore, libsodium, and Argon2 into the `iotox` executable and
passed `tools/verify-standalone.sh` with
`standalone-linked-toxcore-libsodium-argon2=pass`. The resulting Linux x86-64 binary still uses the
host C/C++ runtime and loader; it is not claimed to be universally portable.

The first invocation requested source-input packaging while the tracked development worktree was
intentionally dirty. The packager rejected that state after the executable had already built and
verified. This was the expected fail-closed outcome. Exact source-input packaging is performed only
from the clean final commit; the datacube distribution manifest and checksums are authoritative for
the files actually included.

No public DHT bootstrap, NAT traversal, TCP relay qualification, genuine remote peer, or two-host
terminal session was exercised by this standalone build.

## 5. Research contract applied

Primary material reviewed for this revision includes:

```text
https://www.rfc-editor.org/rfc/rfc9052
https://www.rfc-editor.org/rfc/rfc8949
https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23
https://doc.libsodium.org/installation
https://github.com/P-H-C/phc-winner-argon2/releases/tag/20190702
https://owasp.org/www-project-internet-of-things/
```

RFC 9052's explicit signature context and protected semantic inputs reinforced the decision to use
independent v1/v2 signature and digest domains and to verify the exact prepared mutation before
signing. RFC 8949's deterministic-encoding requirements reinforced the existing fixed canonical
record approach; IoTox does not claim that its proprietary fixed records are COSE or CBOR objects.
The current c-toxcore v0.2.23 release and its security-fix history reinforce keeping provider input
bounded, version-pinned, and independently verified. Upstream facts guide local requirements but do
not prove IoTox correct.

The detailed applied review is retained in:

```text
docs/research/authority-v2-terminal-capability-migration-rev0016.md
docs/decisions/0063-explicit-signed-authority-ledger-v2-migration.md
docs/protocol-authority-v2.md
```

## 6. Construction details

### Non-widening migration

The v2 migration is a distinct action, not an overloaded grant or a header rewrite. Replay accepts a
mixed history consisting of v1 records, exactly one v2 migration record, then only v2 records. The
ledger header must agree with the format derived from the signed history. A migration has the next
sequence in the current ownership epoch, extends the exact prior digest, names the owner as both
issuer and subject, and carries exactly the old owner capability set.

`all` remains the seven-bit v1 set. `all-v2` is an explicit eight-bit spelling and is rejected on a
v1 ledger. An owner may activate the new terminal bit only through a later v2 grant; all other grants
remain bounded by the issuer's capabilities and the fixed role ceiling. Ownership transition
preserves the nominated successor's exact rights instead of recomputing them from a newer mask.

### Rollback guard and durable replacement

The signed ledger remains the authority history. The guard is a separate private regular file with a
fixed header and fixed committed/pending head slots. Each head binds initialized state, ledger
format, ownership epoch, sequence, record count, and tail digest. Append first publishes a pending
transition, atomically replaces the ledger, then commits the new head. Startup reconciles only the
precise states produced by interruption around that sequence.

Both files use bounded reads, no-follow opens, running-user ownership checks, and private-mode
checks. A missing guard may be adopted only for an empty/v1 state allowed by the migration policy; a
v2 ledger cannot silently recreate lost rollback state. The design does not claim monotonic hardware,
remote witnesses, or resistance to an attacker who can replace both files coherently.

### Session and delegation binding

Authority challenges, proofs, and session snapshots carry `AuthorityLedgerFormat`. V2 encodings use
separate markers and signature domains. The negotiated feature set is transcript-bound, so receiving
a v2 proof without shared bit 24 is a protocol error. Remote mutation preparation and confirmation
carry exact ledger heads, reject stale successors, and treat only byte-identical duplicates as
idempotent completion.

The control protocol advances to minor 22 and adds the explicit remote migration operation. Local
and remote RecallRoot ceremonies derive the expected owner public key, decode the prepared body,
compare every security-relevant field with the requested operation, sign only that body, and avoid
echoing the recovery phrase. Process tests include a hostile fixture that substitutes a terminal
grant for a migration body and prove that no append/signature request follows.

## 7. Honest boundary and next work

rev0016 proves a local, compiler-clean, sanitizer-clean, fuzzed authority-ledger v2 construction and
source-linked Linux build. It does not prove compromise resistance for the host filesystem, secure
time, hardware-backed anti-rollback, multi-writer shared storage, network availability, or terminal
service safety. Time windows remain part of the signed record contract but do not manufacture a
trusted clock.

The strongest supportable claim is:

> IoTox rev0016 has an explicit, signed, non-widening authority-ledger v2 migration; an opt-in
> terminal capability; format-bound capability sessions; exact remote/local signing ceremonies; and
> a two-head local rollback guard with tested interrupted-replacement recovery. The remote terminal
> service is still not enabled.

The next independent Ratox prerequisite is R3: a local PTY/profile adapter with privilege separation,
process lifecycle fencing, terminal-byte non-logging, bounded I/O, and an explicit threat review.
Only after R3 should the Agent connect negotiated v2 authority to the already completed R1 session
engine. Feature bit 23, remote advertisement, reconnect qualification, and two-host genuine-network
evidence remain later gates.
