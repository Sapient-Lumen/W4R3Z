# ABI compatibility lanes: Linux emulation vs microVMs (Linuxulator / WSL lessons)

**Tier:** E (Adapter)  
**Profiles:** A, B, C  
**Pillars:** isolation, supply-chain, operability
**Patterns:** Adapter→Shadow→Replace, Registry→Diff→Gate  

DeriveBSD is hypervisor-centric, so the **default** path for “run Linux stuff” should be:

- **Linux-in-a-microVM** (real Linux kernel, real syscalls, strong isolation)

However, BSD ecosystems also have a second path that can be *surprisingly useful* when constrained and treated honestly:

- **Linux ABI compatibility layers** (FreeBSD “Linuxulator”-style syscall translation)

This doc defines a **bounded, optional adapter lane** for ABI compatibility, and why it must never become ambient.

References:
- FreeBSD Handbook: Linux Binary Compatibility (Linuxulator): https://docs.freebsd.org/en/books/handbook/linuxemu/
- FreeBSD `linux(4)` man page (Linux ABI module): https://man.freebsd.org/cgi/man.cgi?linux%284%29=
- FreeBSD Wiki: Linuxulator status/notes: https://wiki.freebsd.org/Linuxulator
- Microsoft: Comparing WSL 1 and WSL 2 (compat layer vs real kernel): https://learn.microsoft.com/en-us/windows/wsl/compare-versions
- Ubuntu docs: Compare WSL versions (same core distinction): https://documentation.ubuntu.com/wsl/latest/explanation/compare-wsl-versions/
- gVisor overview (userspace “application kernel”): https://gvisor.dev/docs/

## A. Lesson: compatibility layers accrete “kernel surface” risk

The WSL 1 → WSL 2 shift is the cleanest public demonstration of the trade:
- **WSL 1**: a compatibility layer translating syscalls
- **WSL 2**: a lightweight VM running a real Linux kernel

As syscall coverage expectations grew, a real kernel became the pragmatic answer.
That maps directly to DeriveBSD:

- if you need “it behaves like Linux”, prefer **Linux microVMs**.

## B. v0 stance (DeriveBSD)

### 1) Default: Linux microVMs
- full syscall compatibility
- clean security boundary
- compatible with DeriveBSD’s “artifact target framework” (`docs/73-artifact-target-framework.md`)

### 2) Optional: ABI translation adapter (Linuxulator-shaped)
Allow a Linux ABI translation lane only when:
- the workload fits a narrow profile (CLI tools, small utilities, constrained servers)
- performance/latency or footprint make microVMs undesirable
- policy explicitly opts in

This lane is treated as an **adapter** under the “strangler discipline” (`docs/402-adapter-lanes-and-strangler-discipline.md`):

- Adapter → Shadow → Replace

In practice, this means:
- you can *start* with translation to get ecosystem reach
- but the long-term goal is either native DeriveBSD builds or Linux-in-microVM

## C. How to keep ABI translation honest

### 1) Make it a separate runtime kind
ABI translation workloads must be labeled and routed differently:
- distinct unit kind (e.g., `linux-abi.unit`) and distinct launch tool
- distinct default policy profile (more restrictive than a native jail)

### 2) Treat syscall coverage as a contract surface
Compatibility layers fail by a thousand papercuts.
DeriveBSD should make coverage reviewable:
- model “supported Linux syscall/ioctl families” as a **surface registry** (see `docs/379-surface-registry-pattern.md`)
- emit diffs when coverage expands (new surface = new risk)

### 3) Fuzz it like a kernel boundary
Syscall translation is effectively a boundary parser.
If DeriveBSD ever ships this lane, wire it into the existing fuzz discipline:
- align translation handlers with **UAPI fuzz descriptors** (`docs/406-uapi-fuzz-descriptors-and-conformance.md`)
- treat coverage growth as “new UAPI surface” (promotion gates can require fuzz evidence)

### 4) Keep a hard escape hatch: “upgrade to microVM”
If a workload hits an unsupported feature (namespaces/cgroups-ish behaviors, ioctls, exotic epoll semantics):
- the operator UX must make “run this as a Linux microVM” the obvious upgrade.

## D. Security posture

Translation layers create a large and subtle attack surface.
Minimum safeguards:
- never run the translation machinery in the same privilege domain as the host control plane
- prefer running it inside a *dedicated compartment* with strong budgets (rctl/cpuset) and tight promise profiles
- tie observability/debug authority to leases (`docs/192-observability-as-capability.md`, `docs/311-operator-access-leases-and-ssh-certs.md`)

## E. Why include the lane at all?

Because it’s a rare “unpopular but practical” trick:
- FreeBSD’s Linuxulator lets some ecosystems run valuable third-party binaries without a full VM
- WSL 1 shows translation can be an excellent UX in the narrow zone where it works

But the meta-lesson is stronger:

> ABI translation must be an **explicit adapter lane**, never a silent foundation.

Last updated: 2026-02-27r119
