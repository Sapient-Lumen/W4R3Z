# Wake from amnesia — rev0026

Start here after forgetting the cube:

1. The DHT is still consumer-agnostic and meant to live over I2P eventually.
2. Mutability remains the central hard thing.
3. rev0026 focuses on three ways valid signed things go wrong:
   - a latest head jumps past known history;
   - evidence gets bundled while losing type/scope/conflict pressure;
   - useful refusal starts looking like contribution health.
4. `lineagewindow.py`, `claimbundle.py`, and `workmeter.py` are local deterministic pressure surfaces, not production protocols.
5. `lineagefold.py` audits that the current surface is visible.

Core sentence:

```text
Signed observations need lineage, type, and work-context pressure before they change local behavior.
```
