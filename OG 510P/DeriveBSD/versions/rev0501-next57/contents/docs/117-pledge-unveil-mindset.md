# Pledge/unveil as a mindset (derive low-friction sandboxing)

OpenBSD’s pledge/unveil are notable because they are:
- easy to apply broadly
- easy to review
- default to failing closed

References:
- Pledge/Unveil paper (BSDCan 2018). https://www.openbsd.org/papers/BeckPledgeUnveilBSDCan2018.pdf
- OpenBSD pledge(2) man page. https://man.openbsd.org/pledge.2
- OpenBSD unveil(2) man page. https://man.openbsd.org/unveil.2
- SerenityOS: pledge()/unveil() overview and promise vocabulary (nice explainer). https://awesomekling.github.io/pledge-and-unveil-in-SerenityOS/

## DeriveBSD translation (FreeBSD primitives)

FreeBSD doesn’t have pledge/unveil, but it does have strong ingredients:
- Capsicum capability mode (descriptor-oriented security)
- jails (filesystem + namespace containment)
- MAC framework (optional hardening)

DeriveBSD should aim for pledge/unveil’s *ergonomics* by providing:

1) **Profiles**: named capsicum/jail profiles (e.g., `dns-client`, `log-forwarder`, `fetcher`).
2) **Preopened handles**: open required files/sockets before entering capability mode.
3) **Filesystem allowlists by construction**: mount only what is needed into the jail/microVM.
4) **Policy-bound exceptions**: any relaxation is recorded in the policy decision record.

When “exceptions” are required dynamically (after dropping authority), prefer a mediated broker (portal/powerbox) over reintroducing ambient namespaces.
See: `docs/179-portals-and-powerbox.md`.

Pledge/unveil also show a small but important API trick: once you’ve finished describing the sandbox,
you can “lock it in” (e.g., unveil can be disabled after rules are set). That matches DeriveBSD’s
preference for *monotonic tightening* of authority.

## Wrapper posture for large programs (make confinement usable)

Big programs are hard to retrofit with confinement primitives quickly.
A pragmatic pattern is to apply the pledge/unveil mindset at the *launcher*:

- the wrapper declares the promise profile
- it preopens needed handles
- it starts the real program inside the restricted environment

DeriveBSD translation: make the wrapper a normal `derive.unit` with an explicit promise profile and routed capabilities,
so confinement is a review surface even when upstream code isn’t ready.


## Why this matters

- Reviewability: “this process can only touch these resources” is tractable.
- Blast radius diffs become concrete: profile changes are authority changes.

See also: `docs/232-service-promise-profiles.md`.

Promise vocabulary + lint rules: `docs/271-promise-profile-vocabulary-and-lint.md`.

See RFC-0085.

Last updated: 2026-02-27r101
