# rev0023 — rangesketch / admissionwall / namespacefold

Codename: `rangesketch-admissionwall-namespacefold`.

This revision pushes on three hard boundaries before live I2P/SAM transport exists:

1. **Range-sketch anti-entropy**: compact signed regional summaries request repair without becoming truth.
2. **Admission wall**: valid-looking requests still need budget/family/namespace admission before expensive handler work.
3. **Namespace registry**: a consumer-agnostic DHT needs mutable validator policy rather than one hard-coded application schema.

The audit/refactor lane adds `namespacefold.py`, updates the active surface ledger, and makes the current revision's namespace/admission/range surfaces visible from the docs index and evidence scripts.

Strongest sentence:

```text
A record can be parse-safe, signature-valid, and still not admitted into local work.
```

Nonclaims remain unchanged: no live SAM/I2P transport, no production DHT, no production namespace governance, no global reputation, no Sybil/anonymity guarantee, no private retrieval guarantee, and no Nicotine+ patch.
