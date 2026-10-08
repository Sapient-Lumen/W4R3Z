# Risk register rev0081

- Native C parser risk: held, not accepted.
- Hand-rolled C cryptography risk: quarantined.
- FFI heap ownership risk: quarantined.
- No Python fallback risk: quarantined.
- Native code becoming semantic authority: rejected by policy.
- Toolchain packaging drift: held behind ABI contract and fallback.
- False performance confidence: documented as seam test, not benchmark proof.
