# Rev0996 audit — framed raw-tail recovery and bounded authority reads

## Why this was the next risk

Rev0995 removed repeated document construction from ordinary save, then left one
measured question rather than authorizing a storage rewrite by taste: does the
bounded JSON/base64 recovery record create user-relevant memory pressure at the
same payload sizes where recovery matters most?

It does. A 16 MiB immutable payload already owned by the editor became a
22,370,271-byte record, while the old checkpoint path peaked at 72,706,910 bytes
of additional CPython-traced allocation and the old load path peaked at
95,077,911 bytes. The problem was not durable checkpointing itself. It was
turning arbitrary bytes into base64 text, embedding that text in a Python JSON
object, encoding the complete JSON value, and later reversing the whole stack.

This was severe because it sat inside the trust-critical interrupted-save path.
A safety feature that multiplies the largest live save object can become the
reason a stressed save fails.

## Severe and wasteful findings corrected

### Recovery serialization multiplied one already-owned payload

The v1 record embedded payload bytes as a base64 string inside canonical JSON.
For a large record, checkpointing could simultaneously own the source payload,
base64 bytes, an ASCII string, JSON text, and the final encoded record. Loading
could own the record bytes, decoded JSON/string graph, encoded base64 text, and
new payload bytes.

The 16 MiB reproduction made that geometry visible before any format choice:

- record size: 22,370,271 bytes, or 1.333372 times the payload;
- checkpoint median traced peak: 72,706,910 bytes beyond the pre-existing source;
- load median traced peak: 95,077,911 bytes; and
- exact round trip remained correct, so the waste was representation, not a
  semantic bug.

### Immediate commit reread the checkpoint it had just constructed

The default save sequence writes a recovery checkpoint and then commits the
same intended bytes. Before this revision, `commit_checkpoint()` reopened,
parsed, base64-decoded, and rehashed the full record even though the same
`RecoveryJournal` instance had just constructed and durably published it.
That second payload object was not an independent authority witness; it was a
costly reconstruction of facts already held in memory.

### Metadata-only operations loaded recovery text

Recovery listing, status inspection, residue discovery, permission repair, and
restart-time commit need verified record authority and payload identity. They do
not need a Python `bytes` object containing the recovery text. The old reader had
one shape, so every operation materialized and then discarded the payload.

### The first fast-path witness had a publication race

The initial optimization recorded the pathname's inode signature after the
checkpoint was published. A byte-identical replacement in the narrow interval
between atomic publication and signature capture could therefore inherit the
in-memory authority intended for the fsynced temporary inode.

The audit reproduced that race at both handoff points. The correction binds the
witness first to the exact private temporary inode that was written and fsynced,
then verifies that the atomically published pathname still names that inode. A
second complete signature check after the outer publication hook closes the next
handoff. Any replacement refuses the shortcut and leaves the record available
for normal validation; it never earns commit authority.

## Landing

### Versioned single-file frame

New checkpoints use `micromax.recovery.v2` with one small frame:

```text
21-byte magic: MICROMAX-RECOVERY NUL 0x02 CR LF
4-byte unsigned big-endian header length
canonical UTF-8 JSON header
exact raw payload tail
```

The header carries target/buffer authority, creation time, base and commit
fingerprints, payload kind, bounded metadata, raw-tail size, and payload SHA-256.
A domain-separated SHA-256 covers the canonical header body. The raw tail is
checked independently against the payload digest. Exact file size must equal
magic plus length field plus header plus declared payload; truncation and
trailing bytes fail closed.

The deterministic filename and historical `.recovery.json` suffix remain. The
suffix is now imperfect, but changing it would create parallel inventory and
migration semantics for no product gain. The magic and schema, not the suffix,
select the parser.

### No joined record on the production writer

The private atomic writer now accepts bounded byte parts and writes each part to
one mode-0600 temporary file. It flushes and fsyncs the file, atomically replaces
the deterministic entry, syncs the directory when the host supports that
operation, and returns the exact published signature. The normal path never
joins header and payload into another complete bytes object.

The historical injected `journal_writer(Path, bytes)` test seam still joins the
parts because its callback contract accepts one bytes object. That is explicit
compatibility debt, not the product default.

### Authority and payload are separate reader products

The v2 reader now has two deliberate paths:

- `load()` and `payload()` validate the frame and materialize the exact payload
  because returning recovery text requires it;
- inventory, `inspect()`, residue discovery, permission continuation, and
  restart-time `commit_checkpoint()` parse the small header and hash the raw
  tail in bounded 1 MiB blocks, returning payload-free authority.

Legacy v1 JSON/base64 records remain readable. Because v1 places base64 inside a
single JSON value, its compatibility parser still performs the old full decode.
New records gain the bounded authority path without pretending the legacy layout
can stream cheaply.

### Inode-bound immediate commit

A successful default checkpoint retains only small authority metadata plus the
exact final file signature. It never retains a second payload. Immediate commit
may reuse that authority only while a no-follow reopen produces the same device,
inode, size, timestamps, mode, owner, and link count. Any drift discards the
witness and invokes full bounded record validation before the document writer is
allowed to run.

The witness is an in-process optimization, not a lock, signature, or hostile
filesystem attestation. Restart and cross-instance operation use the durable
record. Unkeyed SHA-256 detects accidental corruption; it does not authenticate
against an actor able to rewrite the private journal and recompute its hashes.

## Measurement

The permanent artifact is
`.artifacts/rev0996-framed-recovery-record.json`. It compares the exact retired
canonical JSON/base64 construction with the product v2 path over one 16 MiB
immutable payload for three local samples.

| Operation | v1 JSON/base64 traced peak | v2 framed traced peak |
| --- | ---: | ---: |
| checkpoint | 72,706,910 bytes | 19,561 bytes |
| explicit payload load | 95,077,911 bytes | 16,791,015 bytes |
| verified authority inspection | n/a | 2,109,340 bytes |
| restart-time verified commit | n/a | 2,109,386 bytes |
| same-instance checkpoint then commit | n/a | 2,106,468 bytes |

The v2 record is 16,777,982 bytes, 24.999% smaller than v1 and only about 766
bytes above the payload. The controlled comparison reports a 99.973% reduction
in checkpoint traced peak and an 82.340% reduction in explicit-load traced peak.
Median local elapsed time moved from about 0.278 seconds to 0.056 seconds for
checkpoint and from about 0.199 seconds to 0.017 seconds for payload load.

These numbers are attribution witnesses, not portable benchmarks. `tracemalloc`
starts after the immutable source payload exists and does not measure RSS,
allocator arenas, native buffers, kernel page cache, filesystem latency, or
power-loss behavior. The approximately 2.11 MiB authority peak reflects bounded
read blocks and target fingerprinting, not a total process-memory ceiling.

## Online comparison and design pressure

Research was used to validate the narrow shape rather than import a database or
serialization framework:

- RFC 4648 defines base64 in 24-bit input groups represented by four encoded
  characters. The measured near-4/3 record expansion is therefore inherent to
  the old text representation, not a Python accident.
  https://www.rfc-editor.org/rfc/rfc4648
- Python's JSON encoder produces text and its documentation explicitly notes that
  JSON is not a framed protocol. A small explicit length-prefixed header avoids
  pretending arbitrary raw bytes belong inside one JSON document.
  https://docs.python.org/3/library/json.html
- Python `struct` defines `>` as big-endian with standard sizes and no native
  alignment. The four-byte length field is therefore host-independent.
  https://docs.python.org/3/library/struct.html
- Python `hashlib` specifies that repeated `update()` calls are equivalent to
  hashing concatenated input. Header domain separation and bounded raw-tail
  hashing need no complete concatenation.
  https://docs.python.org/3/library/hashlib.html
- Python binary I/O accepts bytes-like objects, supporting part writes and
  bounded reads without converting the payload to text.
  https://docs.python.org/3/library/io.html
- Python documents successful `os.replace()` as an atomic rename on POSIX. This
  supports the existing publish step but does not replace file and directory
  synchronization evidence or broaden the claim to every filesystem/storage
  stack.
  https://docs.python.org/3/library/os.html#os.replace
- SQLite's atomic-commit account treats a well-formed, present journal as
  recovery authority and distinguishes validation/ownership from replay. The
  useful lesson is conservative classification before mutation—not that
  Micromax needs SQLite's lock manager, page format, or transaction machinery.
  https://www.sqlite.org/atomiccommit.html

## What remains missing and what should happen next

The largest project-level gap remains publication truth: signed/hermetic release
evidence and explicit filesystem, terminal, Windows, and broader platform
receipts are still incomplete.

Within recovery, v2 retires the reproduced memory cliff but does not make every
operation free:

- explicit `load()` must allocate one exact payload object;
- authority-only operations still read and hash the raw tail to reject
  corruption before exposing trusted metadata;
- legacy v1 records retain full JSON/base64 decode cost until naturally replaced
  or dismissed;
- the injected single-bytes writer seam still joins the complete v2 record;
- default inventory validates records sequentially under record-byte and target-
  comparison budgets, but a directory containing many maximum-size records can
  still consume substantial I/O;
- SHA-256 is corruption evidence, not keyed authenticity;
- cross-instance writers are not coordinated by a journal lock; pathname/inode
  drift fails closed, but this is not a hostile multi-process transaction claim;
  and
- the same atomic replace/fsync protocol still needs real Windows and filesystem
  receipts before broader durability language is justified.

The most plausible future optimization is header-only inventory with an explicit
"payload not yet verified" state or a sidecar index, but that would weaken the
current rule that listed candidates are fully integrity-checked. It should not be
added unless large real recovery directories make sequential hashing visibly
slow. Likewise, changing the suffix, migrating legacy records eagerly, adding a
watcher, or importing a generic journal framework would create more lifecycle
surface than product value today.

After release evidence, the next measured product pressures remain the delayed
query-replace planning source and O(number-of-lines) pointer generations. The
new recovery frame should be left alone unless a concrete crash/restart journey
contradicts its current bounded behavior.
