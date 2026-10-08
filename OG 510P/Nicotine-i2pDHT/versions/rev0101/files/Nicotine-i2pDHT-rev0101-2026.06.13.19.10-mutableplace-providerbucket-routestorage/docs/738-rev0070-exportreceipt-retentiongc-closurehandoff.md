# rev0070 — exportreceipt-retentiongc-closurehandoff

This revision moves one seam past rev0069's closure seal, retention proof, and redacted audit export.  It treats post-export handling as three independent local permissions:

1. **export receipt** — a redacted export bundle was observed by a local operator/garden/public summary target without raw boundary leakage;
2. **retention GC** — soft working material may be compacted only after required markers and contradiction memory survive;
3. **closure handoff** — a redacted handoff packet may be prepared only when receipt and retention-GC evidence bind to one exact boundary.

The strongest sentence is:

> Redacted export is not handoff; receipt, retention GC, and closure handoff are separate restart-memory boundaries.

No live I2P/SAM transport is added.  This is still a no-network pressure surface for future public-edge and garden/operator audit flows.
