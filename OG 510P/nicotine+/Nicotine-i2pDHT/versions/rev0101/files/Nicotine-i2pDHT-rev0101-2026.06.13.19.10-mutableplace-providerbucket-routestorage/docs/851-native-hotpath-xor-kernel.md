# Native hotpath XOR kernel

The first native candidate is deliberately small: compare two node IDs by XOR distance to a pivot.

Why this kernel:

- It is deterministic.
- It is side-effect-free.
- It does not allocate.
- It does not parse untrusted protocol frames.
- It has a Python reference.
- It is a real DHT hotpath.

Files:

- `src/i2p_dht_lab/nativehotpaths.py` — Python reference and source locator.
- `native/gcc/xor_distance.c` — optional GCC C leaf kernel.
- `tests/test_rev0081_nativeboundary_gccffi_hotpath.py` — compiles and compares when GCC is present.

The C code is not a production performance claim.  It is a seam test: can the cube carry native kernels without letting native code become the protocol authority?
