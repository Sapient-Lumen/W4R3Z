# AnonSync rev0842 deep audit

## Executive verdict

AnonSync's strongest implemented idea remains unusually coherent: **an observation must
become one exact, owned, bounded authority value before it can authorize durable or
externally visible state**. Rev0842 follows that rule through three adjacent persistence
boundaries that still relied on broad live objects or parallel byte construction:

- the local JSONL replay row and its recovery journal;
- the durable SQLite effect-transition hash-chain record; and
- the signed SQLite snapshot manifest.

The revision also audits the file-reading path feeding these boundaries. A bounded byte
count alone was not enough: a FIFO, device, final-component symlink, hard-linked mutable
file, or file changed during the read could still be selected as if it were one stable
regular-file observation. The shared reader now opens first, type-checks the opened
object, reads to EOF under a strict ceiling, and verifies the same object again after the
read. Mutable ledgers and journals use the stronger single-link variant.

This is meaningful progress toward a local integrity and recovery kernel. It is still not
an executable distributed convergence protocol, an anonymity system, or a complete
power-loss proof.

## Heart of the mission

The central engineering law can be stated as:

> Select one namespace object; obtain one exact observation; move all transition-relevant
> fields into one owning value; validate identity, relationships, generations, encodings,
> numeric domains, and resource ceilings there; derive hashes, signatures, durable rows,
> and recovery witnesses only from that value; publish under an explicit durability
> protocol; then recover only into states admitted by the same model.

This law is more important than any particular JSON shape, SQLite table, or report. It
prevents a validator from approving one interpretation while a serializer, hash builder,
or recovery path consumes another.

## Parent defects and waste corrected

### 1. Local JSONL rows had two byte constructions

The rev0841 local backend computed its entry hash from twelve broad arguments, then built
JSON separately with a stream from those same arguments. Reload parsed the JSON and
recomputed the historical hash, but it did not require that the durable row be the exact
canonical encoding production would emit. Delimiter-bearing free text also remained
admissible even though the historical hash tuple is newline-delimited.

Rev0842 introduces `FrozenLocalJsonlReplayEntry`. It owns every row field, validates the
accepted compatibility domain, computes and retains the entry hash, and emits the row.
Load and recovery decode an exact field set, freeze it, verify the recorded hash, and
require byte-for-byte canonical re-encoding. Hash and JSON therefore cannot diverge
without crossing one failing boundary.

The historical hash material remains readable. This revision does **not** relabel it as a
new canonical format. Instead, all delimiter-bearing ASCII controls are rejected, integers
have one locale-free decimal spelling, and the fixed field order makes the accepted
legacy subset injective.

### 2. Batch staging performed real quadratic copying

The parent copied the complete `canonical_lines` vector for every staged row, appended one
line to the copy, then moved the copy back. A batch of N rows therefore performed O(N^2)
string/vector copying before its one durable commit.

The batch owner already has exclusive mutation authority. Rev0842 appends each frozen
canonical line directly during batch staging and publishes the accumulated vector at
commit. Immediate mode retains copy-before-publication semantics because it needs a
candidate complete replacement before the durable protocol begins.

This removes a concrete waste path rather than merely reorganizing files. Immediate mode
still validates and rewrites the full ledger per append; rev0842 does not claim the local
JSONL backend is generally scalable.

### 3. Recovery journal construction was not one frozen publication

The local journal previously validated and streamed individual values in orchestration
code. Rev0842 adds `FrozenLocalJsonlReplayJournal`, with one exact seven-field recovery
witness, fixed format and commit protocol, exact counters, hashes, path budget, and one
bounded JSON encoder. Journal load is exact-field and canonical-encoding checked.

Ledger and journal reads are capped at 64 MiB and 64 KiB respectively. Ledger entry count
is capped at 200,000 and every row has a 64 KiB ceiling. These are local policy ceilings,
not universal protocol maxima.

### 4. Snapshot signatures traversed live JSON

The rev0841 snapshot verifier validated a `Json` payload, later traversed that live tree
again to assemble newline-delimited signing bytes, and later read it again for trust and
snapshot comparisons. The fields had no complete owner or publication-level budgets.
The stream locale had been pinned, so the prior locale defect was not present here, but
the split source of truth remained.

Rev0842 maps the sixteen signature-covered fields once into
`FrozenSqliteSnapshotManifestV2Payload`. The owner validates exact backend constants,
SHA-256 fields, canonical real UTC dates, exact JSON integers, UTF-8/control rules, and
per-field/aggregate budgets. `SqliteSnapshotManifestV2Publication` recomputes the signing
input digest before binding the signature. Trust checks, signature verification, and
snapshot line/head/digest comparisons then consume the frozen fields.

V2 compatibility is deliberately retained. Since its signing bytes are newline-delimited,
rev0842 rejects delimiter-bearing controls before accepting them. A framed vNext remains
preferable for future minting.

### 5. Durable effect-transition material lacked an owner and overflow frontier

The SQLite transition chain previously accepted a long argument list into a helper that
constructed newline-delimited material. Rev0842 introduces
`FrozenEffectTransitionRecord`, used both when appending and when replay-verifying the
chain. It validates all twelve fields, bounds the material at 16 KiB, applies the exact
JSON integer ceiling, and rejects controls in the reason and signer identity.

The transition sequence and prepared sequence are now capped before increment. This
closes a signed `int64_t` overflow frontier that was theoretically reachable through a
corrupt or adversarial durable state even though ordinary databases would never approach
it.

### 6. Bounded reads were duplicated and pathname-oriented

`runner.cpp` carried a local `ifstream` helper that capped bytes but did not make a stable
opened-object claim. Other JSON readers used a generic unbounded path read. Rev0842
removes the runner duplicate and routes bounded documents through
`read_sync_bounded_regular_file_no_symlink_or_throw`.

On POSIX the reader uses nonblocking, no-follow, close-on-exec flags where available;
requires a regular file; enforces the pre-read size ceiling and a one-byte sentinel;
reads through EOF; and checks device, inode, size, link count when requested, and
modification metadata again on the same descriptor. This prevents final-component
symlinks and special files from masquerading as documents and rejects observable mutation
during the read.

The stronger single-link rule is used for mutable local ledgers and journals. It reduces
writable-alias ambiguity but does not prove hostile parent-directory ownership.

## Refactor quality

A shared dependency-light primitive header now owns:

- bounded byte accumulation;
- locale-free integral formatting through `std::to_chars`;
- fixed JSON string escaping and member emission;
- SHA-256, unpadded base64url, UTF-8, control-character, and canonical-UTC checks; and
- named length-framed field emission used by the current effect-intent format.

The existing effect-transition intent publication was reduced from 452 to 259 lines by
using these primitives without changing its v3 wire format. Three focused libraries now
make the new boundaries independently buildable and sanitizable.

The refactor is not a pure file-size win. `src/replay_ledger.cpp` grew from 630 to 1,142
lines because orchestration now includes hardened namespace, load, recovery, and durable
publication checks. The owner/encoder is extracted, but the remaining POSIX and protocol
orchestration should be split by authority rather than allowed to become the next
monolith.

## Audit findings still open

### Directory-entry durability is not a complete state machine

The journal and ledger protocol uses file fsync, temporary write, rename, directory fsync,
and journal unlink. Linux documentation is explicit that fsyncing a file does not by
itself persist its directory entry. The current code has many correct pieces, but rev0842
does not prove every crash cut across journal creation, temporary publication, directory
sync, ledger rename, journal removal, and recovery. In particular, the exact ordering and
recovery interpretation of a newly created journal entry versus the later ledger rename
should be modeled and fault-injected as one protocol.

### `O_NOFOLLOW` protects only the final component

The shared reader rejects a symbolic-link final component. It does not bind every parent
component beneath an already trusted directory descriptor. On Linux, a future namespace
owner should use directory descriptors plus `openat2` resolution constraints such as
`RESOLVE_BENEATH`, `RESOLVE_NO_SYMLINKS`, and `RESOLVE_NO_MAGICLINKS`, with a deliberate
portable fallback. Rev0842 makes no all-component confinement claim.

### Legacy newline formats remain technical debt

The local replay hash, journal compatibility representation, snapshot v2 signing input,
and effect transition record material can be safe on their newly restricted accepted
subsets, but framing is a simpler long-term proof. New minting formats should use named,
length-prefixed fields while retaining explicit legacy readers.

### Local integrity is not distributed convergence

A replica can maintain a perfectly valid local hash chain and still disagree permanently
with another replica. The project still lacks an executable operation algebra covering
concurrent updates, deletes, recreation, rename, duplicate delivery, causal gaps, schema
and key epochs, and coordination requirements.

### Authentication is not anonymity

The code signs and verifies authority evidence but still lacks payload confidentiality,
device membership and key epochs, revocation, forward secrecy, post-compromise recovery,
metadata policy, delivery-service leakage analysis, backup custody, and realistic erasure
claims. “Anon” remains an architectural destination, not an implemented guarantee.

## Where work is still wasteful

- `src/sync_domain.cpp` remains 15,287 lines and 1.12 MB.
- `src/sync_domain_selftests.cpp` remains 9,348 lines and 805 KB.
- `src/sqlite_replay_ledger.cpp` remains 4,527 lines.
- `src/reporting_selftests.cpp` is now 4,773 lines.
- Historical `REVISION_EVIDENCE` is about 24.3 MB and 2,827 files, substantially larger
  than the active first-party implementation.
- Thirty-nine registered lexical/source audits remain. Two had to be updated this
  revision because they encoded an old consumer count and a line-count threshold rather
  than a semantic property.

Lexical audits should be retired when typed APIs, dependency rules, property tests, or a
model oracle enforce the same invariant more directly. Evidence should move toward
content-addressed checkpoint archives rather than recursive inclusion in every ordinary
handoff.

## Recommended architectural direction

Continue the **authority capsule** pattern, but connect the capsules with two executable
models:

1. a local crash-state oracle spanning every SQLite/file/directory/receipt/effect resource;
2. a distributed operation model that defines convergence under replay, reordering,
   partition, concurrency, restart, schema epoch, and key epoch changes.

A likely long-term shape is a ciphertext/content-addressed data plane plus a compact
control plane of authenticated causal operations, object generations, device/key epochs,
revocation facts, and explicit conflict semantics. Local storage mechanisms should
implement that model, not silently define it.

## Validation interpretation

The final GCC 14.2 Debug tree built all targets and reached `ninja: no work to do.` All
136 registered tests passed in eight exact non-overlapping ranges; all 39 registered
source audits are included in that count. The changed leaves and integration paths passed
Clang 17 with `-Werror`. GCC AddressSanitizer plus UndefinedBehaviorSanitizer with leak
detection passed the five extracted leaves.

A full-project sanitizer executable, one uninterrupted 136-test invocation, Release
all-target build, Windows runtime, arbitrary power-loss completeness, distributed
convergence, and privacy properties are not claimed.
