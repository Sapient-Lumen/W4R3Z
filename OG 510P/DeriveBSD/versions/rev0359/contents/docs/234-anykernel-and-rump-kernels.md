# Anykernel + rump kernels: fast kernel-adjacent testing and safer subsystem reuse

Greenfield OS projects usually learn this too late:

- kernel work is hard to test quickly
- untrusted inputs (filesystems, network packets) tend to run in the most privileged place

NetBSD’s **anykernel / rump kernel** architecture is a rare, brilliant idea worth stealing:
run *real kernel subsystems* (filesystems, network stack, drivers) in **userspace** with tight limits and fast iteration.

## What the idea buys us

### 1) Sub-second kernel test loops

Instead of “reboot a VM” cycles, you can:
- spin a minimal kernel instance inside a process
- run unit/integration tests
- fuzz parsers (and feed a continuous fuzz farm)

See also: `docs/274-continuous-fuzzing-farm.md`.

This makes “test-first kernel work” more realistic.

### 2) Safer handling of untrusted inputs

Rump-style deployment patterns include:
- mounting or inspecting untrusted filesystems via a userspace server
- running risky protocol stacks in a compartment

For DeriveBSD, this aligns with our posture:
- compartments/jails/microVMs
- portals for late-bound access
- evidence spine (receipted state transitions)

### 3) A path to reusable components

An “anykernel” framing nudges us toward:
- stable subsystem interfaces
- clear dependency graphs
- smaller privileged cores

## Where DeriveBSD can bake this in (without over-committing)

1) **Kernel CI as a first-class product**
- target: “every subsystem change has a fast test harness”
- output: typed test receipts in the evidence spine

2) **Userspace servers for risky subsystems (optional)**
- untrusted filesystem inspection (“mountless” read-only tooling)
- protocol parsing servers

3) **Fuzzing as policy**
- treat fuzz coverage and crash receipts as build artifacts

## Practical stance

- This is not a v1 requirement.
- But we should design our build + test + evidence interfaces so that **kernel-adjacent components can run outside the kernel** if we decide to.

## References

See: `docs/32-curated-references.md` (rump kernels).

Last updated: 2026-02-25
