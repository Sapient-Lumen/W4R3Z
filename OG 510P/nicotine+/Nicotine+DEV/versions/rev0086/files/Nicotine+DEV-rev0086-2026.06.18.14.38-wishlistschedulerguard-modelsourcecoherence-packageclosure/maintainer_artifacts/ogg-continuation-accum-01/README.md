# OGG-CONTINUATION-ACCUM-01 maintainer artifact

Current-behavior witness for **U-124**.

Run against a source checkout with:

```bash
NICOTINE_SOURCE=/path/to/nicotine-plus pytest -q test_ogg_continuation_accumulation_reproducer.py
```

The test builds compact Ogg streams where one packet spans multiple pages. Each continuation page uses 255 lacing entries of 255 bytes, so the packet is not yielded until a later lacing value below 255 appears.

The assertions intentionally pass on the archived source lanes. A hardened share-scanner metadata parser should apply a local byte/page budget before assembling a very large continued Ogg packet into one bytes/bytearray object.
