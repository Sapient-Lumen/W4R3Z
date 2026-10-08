# Native shadow-GC

`nativeshadowgc.py` allows soft compaction of bulky shadow vectors without deleting the evidence that matters.

The accepted path may shrink soft vector count, but it must preserve:

- call archive memory,
- promotion denial memory,
- call ledger memory,
- Python route memory,
- Python oracle memory,
- fallback memory,
- tombstone memory,
- quarantine memory,
- crash memory,
- a compact summary marker.

The rule is: GC can reduce storage pressure, but it cannot make native promotion look clean by forgetting why it was denied.
