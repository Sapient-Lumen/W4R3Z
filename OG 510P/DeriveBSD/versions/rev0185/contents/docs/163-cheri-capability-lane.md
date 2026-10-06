# CHERI capability lane (optional): hardware-enforced memory safety + compartmentation

CHERI (Capability Hardware Enhanced RISC Instructions) extends CPU architectures with *capabilities* that can provide fine-grained memory protection and scalable compartmentalization.
CheriBSD is a FreeBSD-derived OS that experiments with CHERI and runs on Arm Morello and CHERI-RISC-V.

DeriveBSD is FreeBSD-first, but we can keep an **optional CHERI lane** as a *security accelerator* for specific components and workloads.

This is **not** a portability hedge. It is a **BSD-native hardening option**: when CHERI-capable hardware/software stacks are available, DeriveBSD should be able to take advantage.

## Why this matters for DeriveBSD

DeriveBSD’s stated default posture is:
- treat builders hostile
- minimize TCB
- limit authority and make it reviewable

CHERI can reduce the blast radius of memory safety failures and enable tighter compartment boundaries for high-risk components.

## Where CHERI fits

### 1) Control-plane hardening lane
For high-risk long-lived processes (e.g., cache verification, policy evaluation helpers, key-handling helpers), a CHERI build can be a meaningful hardening option.

Derive integration points:
- allow selecting an **`abi_profile: cheri-purecap`** (or similar) for a target
- record this choice in the Plan digest and in the “capability routing” outputs

### 2) MicroVM workloads
Treat “CHERI guest images” as a workload target lane:
- microVM bundle + guest OS may be CheriBSD
- policy can require CHERI for particularly sensitive workloads

### 3) DevShell isolation option
For “untrusted repo” workflows, a microVM-backed DevShell could optionally use a CheriBSD guest image.
This helps test CHERI readiness while delivering real user value.

## Evidence and explainability

If CHERI is selected:
- record `abi_profile` in the Plan and artifact metadata
- attach a small “cheri lane” evidence object:
  - target triple/ABI mode
  - compiler toolchain identity
  - capsule id

`derive explain` should answer:
- “is this component CHERI-hardened?”
- “what ABI mode?”
- “what toolchain built it?”

## Non-goals

- Requiring CHERI hardware for DeriveBSD.
- Claiming CHERI magically makes components safe; it changes the failure surface.

## References

- CheriBSD project overview: https://www.cheribsd.org/
- CHERI overview (Cambridge CTSRD): https://www.cl.cam.ac.uk/research/security/ctsrd/cheri/
- CHERI temporal safety (CheriBSD runtime revocation notes): https://ctsrd-cheri.github.io/cheribsd-getting-started/features/temporal.html
- CHERIvoke paper (temporal safety via revocation sweeps): https://www.cl.cam.ac.uk/research/security/ctsrd/pdfs/201910micro-cheri-temporal-safety.pdf
- FreeBSD Foundation note on CHERI/CheriBSD work (context): https://freebsdfoundation.org/blog/enhancing-memory-safety-in-programming-insights-from-the-freebsd-vendor-summit/

See also: `docs/140-capability-routing-manifests.md`.

Last updated: 2026-02-25
