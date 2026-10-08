# ABI guard load boundary

The ABI guard treats the compiled artifact as a local claim.

A native library must match:

- expected ABI version;
- required symbol names;
- source digest;
- compiler flag digest;
- object digest;
- bounded maximum input size;
- available Python fallback.

Any mismatch quarantines the native artifact and keeps the Python fallback path available.  No fallback means no native-required profile.

This intentionally keeps the ABI tiny.  The leaf currently exposes only the XOR comparator and ABI-version function from `native/gcc/xor_distance.c`.  There is no cross-boundary allocation, no callbacks, no parser surface, and no authority over protocol truth.
