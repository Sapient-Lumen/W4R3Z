# Driver safety tiering (Rust-first, user-mode by default, isolate legacy)

The highest-impact reliability/security bugs in commodity OSes come from **drivers**:
- huge, stateful code
- constant parser surface (device protocols)
- often written in C
- historically “in-kernel or bust”

DeriveBSD’s greenfield advantage is to *tier* drivers so that **risk is an explicit choice**.

## Prior art worth stealing

- Fuchsia: drivers are **user-space components** under a driver framework (DFv2).  
  https://fuchsia.dev/fuchsia-src/concepts/drivers  
  https://fuchsia.dev/fuchsia-src/concepts/drivers/driver_framework
- Windows: UMDF runs many device drivers in **user mode** to isolate kernel impact.  
  https://learn.microsoft.com/en-us/windows-hardware/drivers/wdf/overview-of-the-umdf
- Rust in kernels: make “memory safety by default” possible for new code.  
  https://docs.kernel.org/rust/index.html  
  https://rust-for-linux.com/
- Userspace filesystems (NetBSD puffs): a concrete example of pulling a huge driver surface out of kernel space.  
  https://www.netbsd.org/docs/puffs/

## The tier model (explicit, lintable)

Define a required attribute on every driver:

- **Tier 0 — Kernel core only**  
  Minimal plumbing: bus discovery, DMA primitives, interrupt routing, safe transfer rings.  
  *Goal:* tiny, reviewable, fuzzable.

- **Tier 1 — In-kernel safe-language driver**  
  Allowed for latency-sensitive drivers *if* written in a memory-safe subset (Rust-first).  
  *Goal:* reduce exploitability for code that must live in kernel.

- **Tier 2 — User-mode driver component (default)**  
  Driver runs as a component with explicit capabilities:
  - device handle
  - DMA-bounded buffers (if allowed)
  - logging/metrics (budgeted)
  - firmware fetch channel (if allowed)
  *Goal:* driver crash ≠ kernel crash; supervision tree can restart drivers.

- **Tier 3 — Driver domain / microVM**  
  Legacy or high-risk drivers run inside an isolated domain (microVM / jail / compartment) with:
  - a narrow para-device interface
  - strict IO + network egress controls
  - strong crash containment
  *Goal:* “we needed this blob” doesn’t poison the host.

## Contracts: drivers must have “small crossings”

Drivers are “parser surfaces”. Make that explicit:

- every driver has a **contract digest** for the host-facing API
- every driver has a **fuzz harness** for its protocol boundary
- every driver binds to devices through a **registry + manifest** (no magic probing)

Tie into:
- `docs/140-capability-routing-manifests.md`
- `docs/297-component-descriptors-and-compiled-runtime-manifests.md`
- `docs/355-rump-kernels-and-userspace-driver-testing.md`
- `docs/274-continuous-fuzzing-farm.md`

## Operational posture

- Drivers participate in supervision (restart budgets, escalation).  
  See: `docs/349-supervision-trees-and-restart-strategies.md`
- Driver restarts produce **receipts** (so flapping is evidence, not vibes).
- Upgrades follow the same **slot/rollback discipline** as everything else.  
  See: `docs/359-slot-based-updates-and-boot-assessment-lessons.md`

## What we bake in now

- Tooling expects Tier 2 by default.
- The “device capability” is first-class in cap routing.
- The build/test pipeline has a dedicated “driver CI lane”:
  - userspace harness
  - rump-kernel harness where applicable
  - protocol fuzzing
  - hermetic integration tests (realm-style)

## Open questions

- What’s our minimal “para-device” ABI for Tier 3 domains?
- Do we want an explicit driver ABI promise (like “stable for N releases”)?
- How do we represent DMA authority as a capability with measurable risk?

## Related docs

- `docs/172-device-backend-isolation-bhyve.md`
- `docs/361-safe-crossing-apis-and-boundary-bugs-lessons-from-tock.md`
- `docs/68-resource-profiles-rctl-cpuset.md`
