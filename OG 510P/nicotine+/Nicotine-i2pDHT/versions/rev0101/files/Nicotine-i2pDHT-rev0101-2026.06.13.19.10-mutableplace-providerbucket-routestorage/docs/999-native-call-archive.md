# Native call archive

`nativecallarchive.py` turns rev0095's Python-route call ledger into restart-sticky archive evidence.

It accepts only if:

- the upstream call ledger accepted,
- the route remains `python_fallback`,
- no native call was executed,
- no native result was selected,
- Python result authority is preserved,
- admission, settlement, fault-seal, fallback, oracle, tombstone, quarantine, and crash memory survive.

It quarantines digest drift, replay, rollback, same-sequence forks, previous-link mismatch, low diversity, native route drift, native authority claims, and memory drops.
