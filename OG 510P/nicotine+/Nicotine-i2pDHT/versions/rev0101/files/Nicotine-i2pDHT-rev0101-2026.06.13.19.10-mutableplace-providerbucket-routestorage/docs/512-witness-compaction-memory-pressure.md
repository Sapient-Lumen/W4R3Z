# Witness compaction memory pressure

Witness/audit memory can become a denial-of-service surface if kept forever, and a safety bug if compacted casually.

`witnesscompact.py` therefore treats compaction as protocol work. Soft observations may expire or fall out of a byte budget. Hard negatives and active redress evidence cannot silently disappear.

The current hard-negative classes include stale public records, payload mismatch, redress gaps, and explicit hard-negative evidence. Same-sequence conflicts quarantine the compaction result instead of letting the newest-looking item win.
