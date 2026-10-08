# Rev0995 audit — one-payload save, exact clean baseline, and complete huge-line journey

## Why this was the next risk

Rev0994 repaired live-growth `fastdirty` policy but left a concrete unanswered
question: after the editor avoids per-edit full-document hashing, does the complete
very-long-line loop still contain a user-visible cliff, and does save throw away
the benefit by rebuilding the same generation several times?

The complete loop was exercised before choosing a new representation. On one
8,000,000-character logical line the permanent journey covers viewport projection,
literal search, cursor movement, insertion, Undo, Redo, interrupted-save recovery
checkpointing, and save. The journey remains exact. The largest avoidable cost was
not movement or history and did not justify a rope, piece tree, gap buffer, or
segmented-line migration. It was ordinary save preparation.

That ordering matters to the mission. Micromax is trying to build a calm editor
whose safety work remains affordable. A durable checkpoint is valuable; making a
normal save transiently own several equivalent complete documents is not.

## Severe and wasteful findings

### An ordinary save rebuilt one generation three times

Before this revision, a dirty Unix/UTF-8 save with no text cleanup:

1. joined the line vector into `before_text`;
2. encoded one commit payload;
3. encoded the same text again for the recovery payload;
4. snapshotted the complete undo manager;
5. joined the document again in `_snapshot_buffer_state()` even though rollback
   could not be needed without a cleanup mutation; and
6. joined and encoded the document again in `mark_clean()` when `fastdirty` made
   the current generation signature unknown.

The recovery record also computed SHA-256 separately for payload and commit even
when both names referred to identical bytes. With `rmtrailingws=true`, its old
no-op path eagerly built a complete trimmed line list and joined it merely to prove
nothing changed.

These were not independent safety witnesses. They were repeated materializations
of one already-owned generation.

### Cleanup rollback began too late

The save path marked cleanup as applied only after `Buffer.set_text()`, cursor
normalization, state capture, and undo recording completed. An exception during
the first mutation itself could therefore leave normalized text in memory while
the disk write had not begun and the original undo state had not been restored.

The correction starts rollback authority immediately before the first cleanup
mutation. Any failure during mutation, cursor normalization, undo recording,
checkpoint commit, or writing restores the exact pre-save text, sidecars, dirty
state, `fastdirty`, version, generation signatures, and undo-manager snapshot.

### The first lazy whitespace draft still copied its prefix twice

The initial refactor waited for the first changed line before allocating a
normalized vector, but used `source_lines[:index]` inside a list comprehension.
For a late change that transiently copied all prefix pointers and then copied them
again into the real result. The audit removed that slice: the normalized vector is
now the only prefix container.

## Landing

### One canonical payload for the ordinary path

After strict encoding succeeds, a Unix/UTF-8 payload with no cleanup is exact
proof of three facts at once:

- the bytes intended for disk;
- the exact pre-write recovery text; and
- the canonical LF-joined current buffer generation used by dirty tracking.

The editor now passes the same immutable `bytes` object through checkpoint,
commit, writer, and clean-baseline hashing. `RecoveryJournal._bytes()` preserves
an existing `bytes` identity, and `checkpoint()` reuses the payload SHA-256 for
the commit fingerprint when the commit aliases the payload.

The optimization is deliberately excluded when proof does not hold:

- DOS output has CRLF bytes while the live buffer remains LF;
- non-UTF-8 encodings do not match the buffer's canonical UTF-8 signature; and
- save cleanup must retain exact pre-normalization recovery text while committing
  normalized output.

Those lanes keep distinct payloads and the existing exact buffer-signature path.

### Clean baselines consume already-owned bytes

`Buffer.mark_clean(current_utf8=...)` can adopt the hash of an already-owned
strict canonical UTF-8 payload instead of joining and encoding the buffer again.
Without that proof it retains the old behavior and computes the live signature.
Randomized Unicode differential coverage confirms the byte-derived signature
matches the existing text-derived BLAKE2b signature.

### Snapshots exist only around a possible mutation

Undo-manager and full buffer-state snapshots are now created only when save
normalization actually changes editor text. Both before and after history states
reuse text values already materialized for encoding, so cleanup remains one
undoable edit without extra complete-document joins. A no-op
`rmtrailingws=true` scan allocates neither a full line copy nor a joined result.

## Complete huge-line evidence

The permanent artifact is `.artifacts/rev0995-single-payload-save.json`.
Its 8,000,000-character journey found the needle in a projected soft-wrapped
viewport, found the exact source coordinate with literal search, moved right and
left, inserted `!`, restored `NEEDLE` with Undo, restored `!NEEDLE` with Redo,
and saved exact bytes through a recovery checkpoint.

The final save used:

- one `get_text()` call;
- zero `_current_signature()` calls;
- zero undo-manager snapshots;
- zero complete buffer-state snapshots;
- one byte object shared by recovery and commit; and
- one exact clean signature derived from that payload.

Local stage times were approximately 0.0373 seconds for literal search and
0.0132 seconds for save; viewport projection, movement, edit, Undo, and Redo were
below 0.003 seconds each in this cloudtainer run. These are attribution witnesses,
not portable latency guarantees.

The controlled preparation comparison reduced complete `get_text()`
materializations from three to one, median local elapsed time by 29.021%, and
CPython `tracemalloc` peak from 40,197,979 to 16,000,893 bytes, a 60.195%
reduction. Source construction, allocator arenas, native memory, RSS, filesystem
latency, and cross-platform behavior are outside that claim.

The recovery witness also shows the remaining amplification honestly: a
2,000,000-byte payload becomes a 2,667,418-byte canonical JSON record because the
bounded journal base64-encodes binary content. Payload identity is hashed once;
the second SHA-256 belongs to record integrity.

## Online comparison

Research was used to test the direction rather than import an architecture:

- Python's `hashlib` contract accepts bytes-like input and defines repeated
  updates as hashing the concatenation. BLAKE2b is guaranteed in supported
  Python builds, so hashing the already-owned canonical payload is equivalent to
  the existing text-chunk path for valid UTF-8.
  https://docs.python.org/3/library/hashlib.html
- Python's codec registry canonicalizes aliases such as `UTF8`, supporting the
  narrow `encoding == "utf-8"` proof after lookup rather than an ad hoc spelling
  list.
  https://docs.python.org/3/library/codecs.html
- Python's base64 encoder returns encoded bytes, and the JSON documentation warns
  that untrusted JSON may consume substantial CPU and memory. This supports
  keeping the journal bounded and names base64-plus-JSON materialization as the
  next save-memory residual rather than pretending this revision made recovery
  streaming.
  https://docs.python.org/3/library/base64.html
  https://docs.python.org/3/library/json.html
- micro documents visible `fastdirty`, file format, encoding, EOF-newline, and
  backup behavior. Its policy comparison reinforces Micromax's current choice:
  keep a reversible conservative dirty mode, but do not make safety features pay
  repeated full-document work when one exact payload already exists.
  https://github.com/micro-editor/micro/blob/master/runtime/help/options.md
- VS Code's text-buffer reimplementation describes moving away from a line-array
  representation only after reproduced speed and memory pressure. Micromax's
  complete huge-line evidence does not yet show the same need: the remaining
  operation is one unavoidable immutable payload plus recovery serialization,
  not broad editor-loop failure.
  https://code.visualstudio.com/blogs/2018/03/23/text-buffer-reimplementation

## What remains missing

The highest project-level gap is still publication truth: signed/hermetic release
evidence and explicit filesystem, terminal, Windows, and broader platform
receipts remain incomplete.

Inside save/recovery, the next plausible pressure is the journal's bounded but
non-streaming base64 and canonical-JSON construction. It can own the payload,
encoded expansion, JSON text, and final record near the same time. A streaming or
binary record format should be considered only after a larger recovery journey
shows user-visible peak memory or latency, because changing the durable format
has compatibility and corruption-handling cost.

Other residuals remain unchanged:

- delayed query-replace owns one complete immutable planning source;
- aggregate history copies O(number of lines) pointer vectors for changed
  buffers;
- one huge changed logical line still constructs one immutable result string;
- the exact threshold-crossing generation still computes one complete signature;
- cross-instance recovery attention is event-refreshed rather than watched; and
- `tracemalloc` and logical `undobytes` do not bound total object/native/RSS cost.

A speculative concurrency concern also remains: save is synchronous and the
product has no supported concurrent buffer mutation during a writer call. If a
future host introduces asynchronous writes or re-entrant save callbacks, payload
ownership must be bound to an explicit buffer generation before clean state can
be adopted. Do not add that machinery until such an owner exists, but do not
reuse the current synchronous assumption silently in an asynchronous design.

## Decision

Keep the line-list representation. The complete huge-line loop is now exercised,
and the corrected ordinary save owns one canonical payload rather than several
equivalent complete generations. The next revision should finish release/platform
evidence or reproduce recovery-serialization pressure; it should not create a
text engine, watcher, cache registry, or new durable format by anticipation.
