# rev0096 — callarchive-promotedeny-shadowgc

rev0096 stays on the GCC/native branch but refuses to let matching native shadow evidence become live authority.

The new seam is:

```text
native shadow settlement accepted
+ held native admission accepted
+ Python-route call ledger accepted
    ≠ restart-sticky call archive
    ≠ native promotion permission
    ≠ safe shadow evidence cleanup
```

The strongest sentence for this revision:

```text
A matching native shadow result is not a promotion path; it is archiveable evidence only while Python fallback, promotion denial, and hard native-fault memory survive cleanup.
```

New surfaces:

- `nativecallarchive.py` archives the Python-route call ledger.
- `nativepromotiondeny.py` records denial of native promotion even after repeated matching shadow evidence.
- `nativeshadowgc.py` permits only soft shadow-vector compaction that preserves denial/fallback/hard-negative memory.
- `nativearchivefold.py` pins rev0096 through the fold/audit path.

Nonclaims remain: no live I2P/SAM transport, no production DHT, no production native ABI/loader/sandbox, no native parser/crypto, no native dispatch authority, and no Nicotine+ patch.
