# Capability mode + dynamic linking (avoid reintroducing ambient authority)

Capsicum is easiest when a process can pre-open everything it needs, then drop ambient authority via `cap_enter(2)`.

Dynamic linking complicates this:
- the runtime linker needs to open shared libraries
- `dlopen(3)` is a common pattern (plugins, NSS, crypto engines)
- once in capability mode, path-based opens are no longer available

If DeriveBSD doesn’t define a clean pattern, teams tend to “just keep ambient filesystem access” for convenience.

This doc collects a **tight, repeatable** pattern to keep capability mode viable.

References:
- “Towards oblivious sandboxing with Capsicum” (dynamic linking in capability mode pain points): https://papers.freebsd.org/2017/vbsdcon/anderson-Towards_Oblivious_SandBoxing.files/anderson-Towards_Oblivious_SandBoxing.pdf
- capsicum(4): https://man.freebsd.org/cgi/man.cgi?query=capsicum&sektion=4
- libcasper(3): https://man.freebsd.org/cgi/man.cgi?query=libcasper&sektion=3

## Recommended DeriveBSD pattern (v0)

### 1) Treat required DSOs as explicit dependencies

For DeriveBSD-managed daemons, the set of required libraries should be captured as:
- a build-time closure fact (already in the store)
- optionally, a **link capsule** manifest listing DSOs needed at process start

This keeps “what must be openable” diffable.

### 2) Enter capability mode only after initial linking completes

Practical rule:

> Do *all* dynamic linking and setup, then `cap_enter(2)` and never return.

This implies:
- avoid late `dlopen()` where possible
- or make late loads go through a brokered handle path (below)

### 3) For unavoidable `dlopen()`, use a brokered-open pattern

If a process must load a plugin after entering capability mode:

- move the “open library bytes” operation to a tiny **helper** that retains limited ambient authority
- helper opens the file *by policy*, returns an FD/handle
- the capability-mode process consumes the FD (not a path)

This maps naturally onto:
- **Casper services** (capability-mode friendly)
- DeriveBSD **portals/powerbox** for dynamic grants

See: `docs/179-portals-and-powerbox.md`.

### 4) Prefer static linking for the smallest TCB daemons

For the highest-privilege daemons (policy engine, signer interface, installer), static linking can be a net win:
- fewer moving parts
- fewer late-link surprises

It should remain a *choice*, not a mandate.

## Engineering guidance

- **Fail closed**: if a daemon tries to `dlopen()` a path after `cap_enter`, it should fail, and the failure should be surfaced clearly.
- **Make the exception explicit**: any portal/broker use should emit an evidence object referencing a policy decision.
- **Keep brokers small**: the helper/portal should not become a general “open any file” escape hatch.

Pointers:
- Capsicum/Casper hardening plan: `docs/49-capsicum-casper-hardening.md`
- Process topology / role separation: `docs/96-process-topology.md`

Candidate RFC: **Capability-mode dynamic linking + brokered plugin opens**.

Last updated: 2026-02-24
