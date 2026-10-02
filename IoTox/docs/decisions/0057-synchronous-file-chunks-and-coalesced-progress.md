# ADR 0057: Answer file chunks synchronously and coalesce disposable progress

Status: accepted, 2026-08-15.

## Context

c-toxcore 0.2.23 requests outgoing bytes through `tox_file_chunk_request_cb`. Its public header
says the client should answer with `tox_file_send_chunk` in response to that callback. Its
`do_reqchunk_filecb` implementation is stricter in practice: it may request as many as 128 chunks
per file in one iteration and explicitly assumes that the client sends from inside the callback.

IoTox originally converted each request into a required transport event. The Agent event thread
then reopened the transfer state, read the requested bytes, and enqueued a second owner-thread call.
On a genuine source-linked transfer, c-toxcore requested ahead before those deferred calls changed
its connection state. At 74,034 bytes the delayed sends filled its queue and
`tox_file_send_chunk` returned `TOX_ERR_FILE_SEND_CHUNK_SENDQ`. IoTox removed the local sender but
left the receiver waiting.

After synchronous delivery fixed that defect, a four-route experiment exposed a second local
bottleneck. Every successful 1,371-byte request and receive callback caused complete atomic
replacement of global and per-peer transfer directories, a multi-file status replacement, and a
global journal append. That disposable observability work dominated CPU and filesystem writes and
hid route scaling.

## Decision

`ToxTransport::offer_file` may receive one transfer-scoped `FileChunkSource`. The source is
installed on the toxcore owner thread in the same operation that assigns the file number. While
inside a nonterminal chunk-request callback, the transport:

1. reads exactly the requested position and length through that source;
2. calls `tox_file_send_chunk` before returning to c-toxcore;
3. emits a required bookkeeping event that records whether source service was attempted, whether
   the chunk was accepted inline, and the exact typed status;
4. cancels and releases the source immediately if reading or sending fails.

The finite-file source retains the already opened no-follow descriptor and validates type, device,
inode, size, and modification time before and after each positional read. Cancellation, completion,
friend removal, and disconnect release the transport source. The asynchronous manager consumes the
bookkeeping event but never sends an inline-served chunk a second time. Its legacy low-level send
path also cancels on terminal send failure so a receiver is not stranded.

Required transport events remain lossless and the file manager consumes every one. Successful
nonterminal file-progress events are different from semantic history: Agent samples their global
journal and atomic runtime projections at most once per 250 milliseconds. Offers, controls,
terminal indications, manager failures, the in-memory event count, and dropped-event evidence are
not coalesced. The structured `files` operation forces an exact manager snapshot.

## Consequences

- The implementation now follows the provider's callback timing contract and large genuine file
  transfers no longer fail at the former deterministic queue boundary.
- File bytes still never enter journals or FIFOs. Integrity checks remain on every supplied chunk.
- The toxcore owner thread performs bounded local file I/O during the callback. This is intentional:
  c-toxcore's current file chunk is at most 1,371 bytes and requires the response in that turn.
- Runtime progress files are atomic but may be up to 250 milliseconds stale during a healthy
  transfer. They remain disposable projections, not completion or durable truth.
- Four independent Tox routes became measurably faster than multiple files on one Tox connection
  after local projection amplification was removed. This ADR does not standardize a bonded
  transport; route membership, striping, integrity, recovery, and authorization remain a separate
  product protocol gate.

## Evidence

- `tests/test_file_transfer.cpp` transfers multiple chunks while the exact toxcore double rejects
  every `tox_file_send_chunk` call made outside the request callback.
- `docs/evidence/2026-08-15-four-route-lab.tsv` retains the three-trial 1x/2x/4x genuine-provider
  result.
- `docs/research/c-toxcore-0.2.23-four-route-file-lab-rev0015.md` records the defect, bottleneck,
  before/after shakedowns, result interpretation, and remaining experiment gates.
