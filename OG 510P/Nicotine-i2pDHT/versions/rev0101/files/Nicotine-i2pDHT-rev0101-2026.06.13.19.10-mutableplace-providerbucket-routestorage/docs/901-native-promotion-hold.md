# Native promotion hold

Promotion from fallback back to native is intentionally harder than first selection.

`nativepromotion.py` joins selection, fallback journal, quarantine report, and corpus report. It accepts promotion only when fresh native selection exists and when prior fallback/quarantine memory is explicitly preserved. It rejects digest drift, replay, rollback, same-sequence forks, previous-link mismatch, low diversity, active quarantine, stale corpus, and dropped fallback/quarantine memory.

The purpose is to avoid the most common native optimization trap: a fixed-looking artifact silently erases the evidence that made native unsafe yesterday.
