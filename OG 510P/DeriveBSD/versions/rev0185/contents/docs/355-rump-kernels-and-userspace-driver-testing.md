# Rump kernels and userspace driver testing (NetBSD lesson)

A persistent OS problem: **drivers are hard to test** because kernel-mode debugging is expensive
and CI/fuzzing for kernel subsystems is slow.

NetBSD’s *rump kernel* work is a powerful (and under-copied) idea: run *unmodified kernel code*
(filesystems, network stacks, drivers) **in userspace** for development, testing, and fuzzing.

References:
- “Kernel Development in Userspace — The Rump Approach” (BSDCan 2009): https://www.bsdcan.org/2009/schedule/attachments/104_rumpdevel.pdf
- “The rump kernel: a tool for driver development …” (AsiaBSDCon 2015): https://www.netbsd.org/gallery/presentations/justin/2015_AsiaBSDCon/justincormack-abc2015.pdf
- “Rump File Systems: Kernel Code Reborn” (USENIX 2009): https://www.usenix.org/event/usenix09/tech/full_papers/kantee/kantee.pdf

## What DeriveBSD should steal

### 1) A “userspace kernel harness” lane

DeriveBSD should treat “kernel-facing code” as eligible for a **userspace harness** mode:

- compile target: `kernel.subsystem` (fs/net/driver/module)
- harness runtime: `rumpish-runner` (userspace process or microVM)
- result artifacts: `kernel.test.receipt`, `kernel.fuzz.receipt`

This is not a mandate for the whole kernel. It’s a *tooling lane* that enables fast feedback.

### 2) Tight integration with evidence lanes

Userspace harness runs should emit the same kind of receipts DeriveBSD already likes:
- exact artifact digests under test
- corpus + seed digests (for fuzzing)
- minimized reproducers
- traces/snapshots only on failure (budgeted)

This makes kernel reliability and fuzzing **policy-gateable** without inventing a second universe.

### 3) Why this matters for a hypervisor-centric OS

DeriveBSD already assumes microVMs are cheap.

A practical pattern:
- run harnessed subsystems as userspace processes for developer iteration
- run them in microVMs for isolation-in-testing
- promote only with receipts

### 4) A driver “test seam” contract

If a driver is launched via a broker, the broker boundary is an ideal test seam:
- fake hardware capability providers
- recorded I/O transcripts for deterministic replay
- fault injection knobs modeled as explicit capabilities

That keeps driver tests aligned with the same **capability routing** model as production.

## Bake-in-now ecosystem payoff

- kernel and driver CI becomes **fast** and **reproducible**
- fuzzing gets dramatically cheaper (more cycles, better coverage)
- driver bring-up becomes less heroic
- “this kernel change is safe” becomes a *receipted claim*, not a vibe
