# Native unload quarantine boundary

Native unload is not cleanup. It is a local protocol marker that decides whether a loaded GCC leaf is still resident, unloaded to Python fallback, or quarantined after a fault.

rev0088 tests these guesses:

- clean native leaves may remain loaded only while Python fallback remains available;
- fault pressure forces unload-to-fallback and artifact quarantine;
- keeping native loaded after a wrong result, timeout, memory fault, or crash is a quarantine event;
- preserving fallback/quarantine memory is mandatory after a fault;
- replay, rollback, same-sequence fork, previous-link mismatch, digest drift, and low family/path diversity all block unload authority.

The active code is `src/i2p_dht_lab/nativeunload.py`.
