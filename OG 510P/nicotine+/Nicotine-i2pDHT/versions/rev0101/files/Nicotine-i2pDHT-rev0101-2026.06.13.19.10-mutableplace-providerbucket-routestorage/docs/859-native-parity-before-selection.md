# Native parity before selection

Native parity is now a first-class gate.

The parity guard accepts only these safe outcomes:

- native missing, Python fallback selected;
- native present and every parity vector matches the Python reference;
- native mismatch/exception quarantined, Python fallback selected.

It rejects the dangerous implied outcome:

```text
native compiled -> native is trusted
```

The parity vectors are deterministic and cover left-wins, right-wins, equality, early-byte differences, late-byte differences, all-zero edges, all-ff edges, and generated mixed cases.  This is not a proof of correctness.  It is a cheap, repeatable boundary that catches drift before the leaf can influence routing order.

The Python reference remains mandatory.  If a future profile claims native is required, missing native becomes a launch quarantine rather than a silent fallback.
