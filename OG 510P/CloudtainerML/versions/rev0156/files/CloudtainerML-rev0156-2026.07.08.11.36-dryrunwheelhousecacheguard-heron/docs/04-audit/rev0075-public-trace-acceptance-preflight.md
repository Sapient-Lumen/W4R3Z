# rev0075 — Public trace acceptance preflight

rev0075 addresses the next risky blocker after the capture kit: accepting an external trace safely. A future public/pretrained Q/K/V bundle must be finite, shape-compatible, provenance-attested, and native-replay-compatible before it can become current evidence.

The revision adds adversarial fixtures for:

- good non-public Q/K/V bundles;
- public flag without manifest;
- manifest hash mismatch;
- public-looking metadata with local/tiny red flags;
- score/value bundles that can be evaluated but cannot enter native Q/K/V replay;
- non-finite Q/K/V arrays;
- mismatched Q/K/V shapes.

The gate is patched to reject non-finite arrays and Q/K/V shape mismatches before selector evaluation. All preflight fixtures remain non-public and non-promotional.
