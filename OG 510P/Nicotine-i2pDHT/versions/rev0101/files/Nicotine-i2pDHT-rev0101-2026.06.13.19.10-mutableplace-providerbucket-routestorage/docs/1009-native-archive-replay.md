# Native archive replay

`nativearchivereplay.py` makes rev0096 archive memory restart-visible. The accepted path requires the call archive, promotion denial, and shadow-GC reports to agree at one exact boundary.

It rejects native call execution, native result authority, digest drift, replay, rollback, same-sequence forks, previous-link mismatches, low diversity, and any drop of Python fallback / tombstone / quarantine / crash memory.

Replay is deliberately not load permission.
