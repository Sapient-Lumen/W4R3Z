# F-CONN-FRAME-01 — fixed-width F-connection partial-frame proof (rev0015)

## Decision

**U-164 is source-confirmed and maintainer-test confirmed, but not promoted to the strict document in rev0015.**

The root is real: the F-connection input path attempts to parse `FileTransferInit` from 4 bytes and `FileOffset` from 8 bytes, then `_process_file_input()` deletes that fixed `idx` amount whenever the helper returns a nonzero `idx`. The helpers return `4` or `8` even when the current `conn.in_buffer` is shorter than the fixed frame size and the parse fails. In a TCP stream, reads can deliver partial bytes, so the correct behavior should be "wait until enough bytes exist" rather than "attempt parse, log failure, and consume what arrived."

## Source-lane result

```text
github-tag-3.3.10: affected; 22 current-behavior tests passed.
github-branch-3.3.x: affected; 22 current-behavior tests passed.
github-branch-master: affected; 22 current-behavior tests passed.
```

## What the rev0015 witness proves

Test file:

```text
maintainer_artifacts/f-conn-frame-01/test_f_connection_fixed_frame_fragment_reproducer.py
```

Current behavior proven across all three lanes:

```text
FileTransferInit:
  - complete 4-byte token frame parses normally;
  - split prefixes of length 1, 2, or 3 are consumed instead of buffered;
  - after the prefix is consumed, the remaining token bytes plus later suffix bytes can be parsed as a different token.

FileOffset:
  - complete 8-byte offset frame parses normally;
  - split prefixes of length 1..7 are consumed instead of buffered;
  - after the prefix is consumed, the remaining offset bytes plus later suffix bytes can be parsed as a different offset and seek target.
```

## Impact boundary

This is **not code execution** and not a standalone confidentiality issue. The practical impact is transfer robustness and peer-driven availability/state confusion at the F-connection framing boundary.

The reason this stays outside the strict document is coherence: in the relevant phases the peer already influences `FileTransferInit` token delivery and `FileOffset` choice, and a malicious peer can already fail or stall its own transfer. U-164 is useful as a regression/hardening item and may support U-123/U-169 transfer-lifecycle testing, but it is not currently a clean fourth strict report.

## Fix shape

A coherent fix should be small and compatibility-preserving:

```text
1. In _process_file_input(), check len(in_buffer) before calling the fixed-width parser.
2. For FileTransferInit, return 0 and keep bytes buffered until len(in_buffer) >= 4.
3. For FileOffset, return 0 and keep bytes buffered until len(in_buffer) >= 8.
4. After the offset is accepted, continue clearing unexpected post-offset input as today.
5. Add tests that feed every split position for FileTransferInit and FileOffset.
6. Keep this separate from token/source-binding fixes such as U-123 and U-169.
```

## Evidence files

```text
evidence/rev0015-fconn-frame-reproducer-run.txt
evidence/rev0015-fconn-frame-probe.jsonl
evidence/rev0015-fconn-frame-source-trace.md
evidence/rev0015-web-public-overlap-fconn-frame.md
data/rev0015_fconn_frame_probe_summary.csv
```
