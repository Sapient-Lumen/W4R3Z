# Rejected scope record — rev0883

A mutable, noncanonical workspace acquired an unrelated 578-line incremental
nonblocking receive prototype while the affinity correction was under review.
The prototype changed public continuation APIs and stream reservation semantics
without adding a corresponding runtime matrix. Its first focused GCC build
failed on constructor/signature mismatches, private-state access, and stale call
sites.

The compile log is retained as
`validation/rejected-receive-prototype-compile-failure.log` with SHA-256
`32f2f6df0558c13abc7a61f096819caa2cbb9d1b5c43b4a1d0e92f2a4d26884a`.

No source from that branch is present in rev0883. The final tree was created from
the independently verified rev0882 archive and contains only the reviewed
no-throw affinity correction, exact topology-inventory updates, documentation,
and evidence. This record does not establish who or what created the mutable
branch; it establishes only that presence in a workspace was not accepted as
lineage or implementation authority.
