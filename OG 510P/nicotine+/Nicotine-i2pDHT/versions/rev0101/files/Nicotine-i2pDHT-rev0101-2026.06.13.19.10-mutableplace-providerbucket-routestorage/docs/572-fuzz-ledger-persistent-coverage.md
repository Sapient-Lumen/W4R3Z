# Fuzz ledger persistent coverage

`fuzzledger.py` keeps adapter fuzz coverage from being a one-shot artifact.

The ledger signs coverage entries that bind the adapter-fuzz report digest, required/observed mutation digests, generator digest, sequence, previous entry, freshness window, and family/path hints.

It rejects stale entries, replays, rollback, same-sequence forks, previous-link mismatch, report digest drift, coverage digest drift, generator drift, persisted failures, insufficient mutations, and low family/path diversity.

Design guess:

> Fuzz coverage should itself be replayable evidence with drift pressure, not a comment in a test run.
