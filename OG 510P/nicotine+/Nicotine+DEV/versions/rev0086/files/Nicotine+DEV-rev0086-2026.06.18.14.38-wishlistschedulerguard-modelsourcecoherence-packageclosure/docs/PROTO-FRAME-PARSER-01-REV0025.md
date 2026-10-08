# PROTO-FRAME-PARSER-01 / U-137 + U-175 — rev0025

## Decision

**Verified audited-backlog packet; not promoted to the strict/high-priority document.**

The current-behavior witness passes across all archived source lanes:

```text
github-tag-3.3.10:   13 passed
github-branch-3.3.x: 13 passed
github-branch-master: 13 passed
```

This is real parser/frame hardening debt, but it is not a clean fourth strict report. The practical consequence is malformed-message acceptance/desynchronization and availability/integrity hardening at server, peer, and distributed parser boundaries. It is not code execution, not file disclosure, and not stronger than the existing strict source-binding reports. The 3.3.11 release-candidate notes also overlap the broader parser-hardening theme through maximum uncompressed network-message sizes, so this packet is marked **candidate no direct public match found / public-adjacent generic parser hardening**.

## What was proven

### U-137 — final length-prefixed field truncation

The helper pattern accepts a declared length that extends beyond the actual buffer when the field is final or no later strict read catches the offset. In current source lanes:

```text
SayChatroom final message string:
  declared length = 10
  actual bytes    = 3
  parsed message  = "abc"

FileSearchRequest final search string:
  declared length = 12
  actual bytes    = 6
  parsed term     = "needle"

DistribSearch final search string:
  declared length = 12
  actual bytes    = 5
  parsed term     = "query"

Low-level unpack_bytes helper:
  declared length = 20
  actual bytes    = 3
  returned bytes  = b"abc"
  returned offset = 24, beyond the 7-byte payload
```

In 3.3.10 and 3.3.x, `unpack_string()` / `unpack_bytes()` compute `end = start + length`, slice `message[start:end]`, and return `end`; Python slicing returns only available bytes when `end` exceeds the buffer. In master, the same issue appears through `_offset = start + length`; the returned field uses the available slice and `_offset` can advance beyond the payload.

### U-175 — framed-message sizes smaller than mandatory code fields

For server and peer message frames, the protocol frame is `uint32 length + uint32 code + contents`. A declared `msg_size` smaller than four bytes cannot contain the mandatory code field. Current loops read the code from the outer eight bytes, compute `msg_size_total = msg_size + 4`, and advance by that short total rather than rejecting fail-closed.

Observed current behavior across all lanes:

```text
server msg_size 0 -> connection not closed, 4 bytes remain
server msg_size 1 -> connection not closed, 3 bytes remain
server msg_size 2 -> connection not closed, 2 bytes remain
server msg_size 3 -> connection not closed, 1 byte remains

peer msg_size 0 -> connection not closed, 4 bytes remain
peer msg_size 1 -> connection not closed, 3 bytes remain
peer msg_size 2 -> connection not closed, 2 bytes remain
peer msg_size 3 -> connection not closed, 1 byte remains

distributed msg_size 0 -> connection not closed, 1 byte remains
```

For distributed frames, the mandatory code is one byte, so `msg_size = 0` is the tested too-small value.

## Coherence / fix shape

A good fix should avoid one-off checks scattered into individual messages. The coherent parser invariant is:

```text
1. Validate frame length against its fixed header contract before advancing the buffer.
   - server/peer: msg_size >= 4
   - peer-init/distributed: msg_size >= 1
   - F-message fixed frames: retain the rev0015 fix shape: buffer until 4/8 bytes or close on invalid state.

2. Validate length-prefixed fields before returning content.
   - require start + declared_length <= actual message length;
   - fail the whole message parse on short payload;
   - after parse, require no required field offset has moved beyond the payload.

3. Keep max-size caps separate from minimum-length correctness.
   The 3.3.11-style maximum-message-size hardening is useful but does not by itself reject frames that are too small or internally truncated.

4. Make compatibility explicit.
   Valid empty strings and valid empty byte fields must still parse. The rejected cases are not empty fields; they are declared non-empty fields whose payload bytes are absent.
```

## Public-overlap status

Targeted searches did not find a direct Nicotine+ issue for the exact combined invariant:

```text
"truncated" "unpack_string"                         -> no issue results
"message length" "message code"                     -> no issue results
"MAX_INCOMING_MESSAGE_SIZE"                          -> no issue results
"malformed" "PeerInit"                               -> no useful direct issue result
```

However, public and upstream-adjacent context exists:

- The official protocol docs describe strings/bytes as `uint32 length + payload`, and server messages as `uint32 length + uint32 code + contents`.
- The 3.3.11 RC notes mention maximum uncompressed network-message-size enforcement.
- Several public issues and release-note entries discuss generic crashes, message/network hardening, large result parsing, and connectivity symptoms.

Classification: **candidate no direct public match found / public-adjacent generic parser hardening**.

## Files

```text
maintainer_artifacts/proto-frame-parser-01/test_protocol_frame_and_truncated_field_reproducer.py
evidence/rev0025-proto-frame-parser-pytest-run.txt
evidence/rev0025-proto-frame-parser-probe.jsonl
evidence/rev0025-proto-frame-parser-source-trace.md
evidence/rev0025-web-public-overlap-proto-frame-parser.md
data/rev0025_proto_frame_parser_probe_summary.csv
data/rev0025_proto_frame_parser_probe_summary.json
data/rev0025_public_overlap_proto_frame_parser.csv
data/rev0025_proto_frame_parser_coherence_refactor.csv
```
