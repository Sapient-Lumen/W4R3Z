# Wake from amnesia — rev0081

The answer to the GCC question is **yes, but only as a narrow leaf-kernel lane**.

Do not rewrite the DHT in C.  Do not move mutable-head truth, governance, router lifecycle, persistence, or public-edge semantics into native code.  Use GCC C only for tiny pure kernels with Python references, golden vectors, stable ABI contracts, and portable fallbacks.

Current codename: `nativeboundary-gccffi-hotpath`.
