# Safe crossing APIs and boundary bugs (Tock lessons for typed OS surfaces)

DeriveBSD’s core design principle is “crossings are contracts.”
That applies to userland brokers and portals — but the kernel boundary matters too.

Tock (a Rust-based embedded OS) is useful as a negative/positive lesson:

- **positive:** keep kernel interfaces simple and non-blocking; force long-running work to be async
- **negative:** even “memory-safe” kernels can have dangerous boundary assumptions at syscall edges

## What to steal

### 1) Keep boundary calls small and synchronous

A simple rule: boundary crossings should not block indefinitely.
If a call might take time, the interface should:

- register interest (subscribe)
- grant a buffer (allow)
- trigger work (command)
- deliver completion later

DeriveBSD implication: prefer request/receipt patterns over giant “do everything” syscalls.

### 2) Treat syscall surfaces like any other contract

Even if DeriveBSD keeps a traditional BSD syscall ABI, we can still:

- define a typed *contract catalog* for privileged interfaces
- hash/digest the catalog into runtime manifests
- require conformance tests (see WIT lane) for any new privileged boundary

### 3) Design for boundary auditing

Boundary bugs are where “the type system ends.”
DeriveBSD should lean on:

- strict copyin/copyout conventions
- fuzzing harnesses (rump kernel testing lane)
- receipts for privileged operations that cross trust boundaries

## Where this plugs in

- Contracts + digests: `docs/183-object-capability-rpc.md`, `docs/356-wasm-component-model-and-wit-contracts.md`
- Kernel subsystem testing: `docs/355-rump-kernels-and-userspace-driver-testing.md`
- Continuous fuzzing farm: `docs/274-continuous-fuzzing-farm.md`

## References

- Tock syscall model documentation:
  https://book.tockos.org/doc/syscalls
- Weisblat thesis on syscall-boundary memory safety in Tock (boundary vulnerability case study):
  https://www.ll.mit.edu/sites/default/files/publication/doc/improving-security-system-call-boundary-type-safe-weisblat-thesis-weisblat.pdf

Last updated: 2026-02-27r101
