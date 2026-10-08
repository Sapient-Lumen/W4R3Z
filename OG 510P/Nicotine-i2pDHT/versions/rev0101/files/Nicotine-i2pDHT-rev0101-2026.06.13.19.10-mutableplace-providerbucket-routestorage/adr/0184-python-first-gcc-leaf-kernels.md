# ADR 0184 — Python-first GCC leaf kernels

Decision: keep the DHT semantics Python-first and allow GCC-compiled C only for narrow leaf kernels with a stable ABI, Python reference, golden vectors, bounded inputs, no heap ownership transfer, and a portable fallback.

Rejected: rewriting mutable-head acceptance, governance, SAM/router orchestration, persistence, public-edge semantics, or untrusted-byte parsing in C at this stage.

Rationale: native leaf kernels can be useful for routing hotpaths and set-reconciliation adapters, but semantic authority in C would slow design, reduce auditability, and add memory-safety risk before the protocol has settled.
