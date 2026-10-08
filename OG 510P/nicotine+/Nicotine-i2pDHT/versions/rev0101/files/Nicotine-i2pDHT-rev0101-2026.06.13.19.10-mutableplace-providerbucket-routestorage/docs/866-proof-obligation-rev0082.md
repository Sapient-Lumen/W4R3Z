# Proof obligation — rev0082

rev0082 proof obligations:

- Missing native artifact selects Python fallback rather than crashing or inventing native success.
- A fake native mismatch is quarantined while Python remains usable.
- A fake native exception is quarantined while Python remains usable.
- The real GCC XOR leaf, when compilable, matches the Python reference vectors.
- ABI/version/symbol/source/flag/object/input-limit drift quarantines the native artifact.
- Native-required profiles cannot launch when native parity or ABI is missing.
- Fold/audit surfaces include the new native parity path and preserve rev0081 predecessor history.
