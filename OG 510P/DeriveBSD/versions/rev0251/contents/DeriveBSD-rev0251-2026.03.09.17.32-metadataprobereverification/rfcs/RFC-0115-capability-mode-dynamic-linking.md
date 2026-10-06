# RFC-0115: Capability mode + dynamic linking strategy

Status: **draft**

## Problem

Capsicum capability mode is an attractive primitive for reducing ambient authority in DeriveBSD daemons.

Dynamic linking complicates Capsicum adoption:
- the runtime linker must open libraries
- many programs use `dlopen()` after startup
- capability mode removes path-based opens

Without a defined pattern, teams tend to keep ambient filesystem access “just in case”, undermining the model.

## Goals

1) Provide a repeatable, low-friction pattern that keeps capability mode viable.
2) Keep required dynamic dependencies explicit and diffable.
3) Offer a sanctioned pattern for late plugin loads without broad escape hatches.

## Non-goals

- Mandating static linking for all programs.
- Inventing a new ELF linker/loader.

## Prior art

- Capsicum experience reports and “oblivious sandboxing” work describing dynamic linking pain points.

References:
- Towards oblivious sandboxing (slides): https://papers.freebsd.org/2017/vbsdcon/anderson-Towards_Oblivious_SandBoxing.files/anderson-Towards_Oblivious_SandBoxing.pdf
- capsicum(4): https://man.freebsd.org/cgi/man.cgi?query=capsicum&sektion=4
- libcasper(3): https://man.freebsd.org/cgi/man.cgi?query=libcasper&sektion=3

## Proposed patterns

### Pattern A: “link-then-cap” (default)

For DeriveBSD-managed daemons:

1) do all initialization and runtime linking before entering capability mode
2) `cap_enter(2)` once initialization completes
3) never perform path-based opens after entering capability mode

This is simple and should be the v1 default.

### Pattern B: Brokered plugin open (for unavoidable dlopen)

If a program must load plugin bytes after entering capability mode:

- delegate the path open to a tiny helper/broker that retains minimal ambient authority
- helper returns a file descriptor (or equivalent) to the capability-mode process
- the broker decision is evaluated by policy and recorded as evidence

This reuses the portal/powerbox abstraction:
- RFC-0114 (portals)

### Pattern C: Static-link “small TCB” daemons (optional)

For the most privileged daemons (policy engine, signer interface, installer), static linking may simplify the threat surface.
This is a per-daemon decision.

## “Link capsule” (optional ergonomics)

Define an optional build output that records the DSOs required at process start.
The activation/launcher can then:
- ensure those DSOs are present in the expected closure
- pre-open them (when useful)
- fail early if the runtime link set is unexpected

This improves explainability (“why did this daemon need these libraries?”) without requiring new kernel features.

## Integration points

- Capsicum/Casper hardening plan: `docs/49-capsicum-casper-hardening.md`
- Portals/powerbox: RFC-0114 and `docs/179-portals-and-powerbox.md`

## Open questions

- Do we standardize a link capsule schema (JSON) or treat it as an internal build artifact?
- Which daemons must be capability-mode in v1 vs “best effort”?
