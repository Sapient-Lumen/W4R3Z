# CHERI: capability hardware and a memory-safety lane (optional)

DeriveBSD is already “capability-first” at the *authority* layer (Capsicum, object-capability RPC, portals).
CHERI extends that idea into the *memory model*: pointers become **unforgeable, bounds-checked capabilities**, enabling fine-grained memory safety and scalable compartmentalization.

Because DeriveBSD is BSD-native, we can treat **CheriBSD/Morello/CHERI-RISC-V** as a realistic *optional* lane rather than a research curiosity.

## Why this is a greenfield opportunity

Older ecosystems try to bolt memory safety onto decades of C ABI expectations.
A greenfield system can:

- keep a conventional amd64 lane while
- making a **CHERI lane** first-class: builds, ports policy, and compatibility expectations are explicit.

The key is to avoid “half adopting” CHERI.
Treat it like other optional lanes (unikernel, proofs, live-patching): **opt-in, policy-defined, receipted**.

## Stance

- **Default:** DeriveBSD runs on conventional architectures, with memory safety coming from:
  - isolation (jails/microVMs),
  - safer languages in privileged code (Rust tiering),
  - parser/UAPI registries + fuzz gates.

- **Optional CHERI lane:** a *separate platform target* (e.g., Morello or CHERI-RISC-V) where the base set is built with CHERI-enabled toolchains.

## Design sketch

### 1) CHERI is an explicit platform constraint

Add a platform attribute to system specs/locks so it is impossible to “accidentally” mix:

- `platform.cpu = amd64 | aarch64 | morello | cheri-riscv64 | ...`
- `platform.abi = conventional | hybrid | purecap`

This becomes part of:
- closure proofs,
- artifact identity,
- update channel metadata.

### 2) ABI reality: embrace *hybrid → purecap* as an intentional migration story

CHERI ecosystems tend to distinguish:
- **hybrid**: mixes conventional and capability pointers (interop-focused)
- **purecap**: capability pointers everywhere (safety-focused)

DeriveBSD should not pretend this is transparent.
The lane should be explicit about:
- which userlands are supported (base, a “cheri-ports set”),
- where compat shims exist,
- which services are required to be memory-safe.

### 3) Compartmentalization becomes cheaper and more ergonomic

CHERI’s strongest system-level win is not only “no OOB writes”, but that **compartments get real enforcement with low overhead**.
This complements DeriveBSD’s existing posture:

- service jails/microVMs shrink ambient authority,
- CHERI shrinks intra-process blast radius.

### 4) Driver safety story

CHERI does not remove the need for driver tiering.
But it improves the “in-kernel must exist” case:

- in-kernel tiers can be:
  - Rust-first, **and/or**
  - CHERI-enforced, with more credible mitigation against memory corruption.

See: `docs/363-driver-safety-tiering-rust-and-user-mode.md`.

## Artifacts / evidence hooks (keep it reviewable)

- **Platform lane receipt:** every build artifact records whether it is conventional/hybrid/purecap.
- **Porting receipts:** ports that required CHERI-specific patches produce a small “delta receipt” (what changed and why).
- **Boundary receipts:** if CHERI is used for compartmentalization, map compartments into `authority.graph` so the extra guarantees remain visible.

## Risks / non-goals

- CHERI is not a “flip a switch” memory-safety fairy.
- Don’t force the lane onto all users.
- Don’t invent a bespoke CHERI porting ecosystem: interop with existing CheriBSD work where possible.

## References

- Cambridge CTSRD CHERI project overview:
  - https://www.cl.cam.ac.uk/research/security/ctsrd/cheri/
- FreeBSD Foundation: CHERI/Morello context for FreeBSD ecosystems:
  - https://freebsdfoundation.org/blog/freebsd-for-research-cheri-morello/
- FreeBSD status report: CheriBSD (FreeBSD for CHERI-enabled platforms):
  - https://www.freebsd.org/status/report-2022-10-2022-12/cheribsd/

Last updated: 2026-02-27r110
