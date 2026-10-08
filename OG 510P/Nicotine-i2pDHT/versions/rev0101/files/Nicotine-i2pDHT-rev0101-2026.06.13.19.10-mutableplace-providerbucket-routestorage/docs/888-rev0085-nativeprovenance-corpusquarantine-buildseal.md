# rev0085 — nativeprovenance-corpusquarantine-buildseal

rev0085 continues the GCC/native line without turning it into a rewrite.

The new risk-first boundary is: a native artifact is not safe because parser hold, sanitizer plan, budget, runtime, or dispatch passed somewhere else. Native code must now pass three more local gates:

- `nativeprovenance.py`: source audit + sanitizer + native budget + compiler/object/artifact digests + builder/path diversity.
- `nativecorpus.py`: deterministic differential corpus against the Python XOR oracle.
- `nativequarantine.py`: sticky quarantine memory when provenance or corpus fails, so restart cannot rediscover a bad artifact as fresh.
- `nativeprovenancefold.py`: current revision audit preserving rev0084 `nativebudgetfold` predecessor history.

The strongest sentence:

```text
A native artifact is not safe because it compiled, passed parity once, or survived dispatch; build provenance, differential corpus, and quarantine memory must agree while Python remains the oracle.
```

Nonclaim: this is still a no-network design/prototype cube. No live I2P/SAM transport, no production native ABI, no native parser/crypto, and no production DHT.
