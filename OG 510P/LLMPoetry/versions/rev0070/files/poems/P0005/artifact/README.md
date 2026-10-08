# P0005 Bloom-filter artifact — rev0070

- Spec: `poems/P0005/artifact/d001/BLOOM_POEM_SPEC.json`
- Receipt: `poems/P0005/artifact/d001/BLOOM_RECEIPT.json`
- Binary filter: `poems/P0005/artifact/d001/filter.bin`
- Exact ledger: `poems/P0005/artifact/d001/inserted_records.txt`
- Query: `poems/P0005/artifact/d001/query.txt`
- Surface: `poems/P0005/artifact/d001/filter_surface.txt`
- Builder: `tools/build_bloom_false_positive_poem.py`
- Checker: `tools/check_bloom_false_positive_poem.py`

The four-byte filter is not a model of a real case system. It is a closed synthetic construction proving one exact false positive and the distinct inserted owner of each query bit.
