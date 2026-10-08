# GCC FFI contract

The GCC path is a C ABI contract, not a permission to smuggle protocol state into C.

Minimum guardrails:

- Symbol prefix: `i2pdht_`.
- Explicit ABI version symbol.
- Fixed-width integer types.
- No heap ownership transfer across the boundary.
- No callbacks into Python.
- No global mutation.
- No untrusted network bytes for early native leaves.
- Python reference implementation must remain.
- Golden vectors must compare native and Python behavior.
- Portable Python fallback must exist.
- Endianness vectors must exist.

Native parser work is held, not accepted.  C parsers for untrusted bytes are a rich source of memory-safety mistakes.  If a native parser ever enters the cube, it needs differential fuzzing, sanitizer profiles, corpus shrinking, and a serious memory-safe-native comparison.
