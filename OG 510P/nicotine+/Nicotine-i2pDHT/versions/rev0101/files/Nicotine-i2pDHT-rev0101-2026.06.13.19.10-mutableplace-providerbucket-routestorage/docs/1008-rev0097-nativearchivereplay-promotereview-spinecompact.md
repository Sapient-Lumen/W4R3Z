# rev0097 — nativearchivereplay-promotereview-spinecompact

rev0097 keeps the GCC/native branch narrow. rev0096 archived matching native-shadow evidence while denying promotion; rev0097 tests what happens after restart when that archive is replayed and an operator-style review is requested.

The seam is:

```text
native call archive accepted
+ promotion denial accepted
+ shadow-GC accepted
    ≠ restart replay may grant native load
    ≠ repeated matching shadows may grant promotion
    ≠ fold-spine drift may remain invisible
```

Strong sentence:

```text
Archived native-shadow evidence is only replay memory; promotion review remains held while Python fallback stays authoritative.
```

New surfaces:

- `nativearchivereplay.py` replays rev0096 call-archive / promotion-denial / shadow-GC memory after restart without permitting native load or dispatch.
- `nativepromotereview.py` allows only a held human/operator review marker, not promotion.
- `nativefoldspine.py` was compacted from append-only override drift into one auditable native branch table.
- `nativearchivereplayfold.py` pins the current path through surface ledger, fold map, fold registry, native spine, and rev0096 predecessor history.

Nonclaims remain: no live I2P/SAM transport, no production DHT, no production native ABI/loader/sandbox, no native parser/crypto, no production native dispatch authority, and no Nicotine+ patch.
