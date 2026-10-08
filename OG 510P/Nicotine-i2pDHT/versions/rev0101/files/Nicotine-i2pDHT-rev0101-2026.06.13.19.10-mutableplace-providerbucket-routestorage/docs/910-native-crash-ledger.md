# Native crash ledger

The crash ledger treats native crashes, wrong results, loader faults, timeouts, and memory faults as sticky local evidence. A bad native leaf cannot be rediscovered as fresh after restart just because a later selection path looks healthy.

Faults force fallback and quarantine pressure until a later promotion path explicitly carries that history.
