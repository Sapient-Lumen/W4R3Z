# rev0081 — nativeboundary-gccffi-hotpath

Question answered: should this DHT be written with GCC instead of Python in part?

Yes, **in part**, but the part should be narrow.  GCC should compile leaf kernels, not own the protocol.  Python should remain the place where mutable-head acceptance, garden policy, subjective governance, routing/admission decisions, SAM/router orchestration, persistence semantics, and wake-from-amnesia audit behavior are designed.

The native boundary should start with boring pure kernels:

- XOR-distance comparison and candidate ordering.
- Range-sketch/hash-combine helpers after Python reference tests exist.
- Set-reconciliation adapters behind a strict seam.
- Bulk hashing only by binding vetted libraries or extremely small leaf wrappers.

The first GCC artifact in this cube is intentionally tiny: `native/gcc/xor_distance.c`.  It exposes `i2pdht_abi_version` and `i2pdht_xor_compare`, and tests compile it into a shared library before comparing it against the Python reference.

The policy sentence:

> Write the DHT in Python until semantics stop moving; compile only deterministic, side-effect-free, no-heap-transfer leaf kernels through a stable C ABI with Python fallbacks.

Nonclaims remain: no production DHT, no production FFI package, no live I2P/SAM transport, no production native parser, no production crypto implementation, no Sybil/anonymity guarantee, and no Nicotine+ patch.
