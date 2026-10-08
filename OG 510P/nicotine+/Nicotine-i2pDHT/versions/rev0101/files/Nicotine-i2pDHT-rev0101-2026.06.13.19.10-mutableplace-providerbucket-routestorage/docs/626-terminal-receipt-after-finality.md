# Terminal receipt after finality

`terminalreceipt.py` adds a signed receipt after finality and prune guard both accept terminal state.

A finality marker alone is not enough to let later cleanup, compaction, or live side-effect code claim terminal authority. The terminal receipt binds finality digest, accepted marker digest, prune-guard digest, prune plan digest, exact request boundary, family/path diversity, sequence, previous receipt, and validity window.

This is another local memory seam: terminality is easier to audit later when it has a small typed receipt rather than relying on a remembered pile of reports.
