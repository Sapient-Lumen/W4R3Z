# pledge/unveil-style promises and Derive promise profiles

OpenBSD’s `pledge(2)` and `unveil(2)` are an unusually successful security API because they are:
- small
- understandable
- incremental (tighten after startup)
- reviewable in code

DeriveBSD already has **promise profiles** as data-first sandbox declarations.
A greenfield advantage is to *map these worlds* so the ecosystem gets an ergonomic on-ramp.

## References

- pledge(2): https://man.openbsd.org/pledge.2
- unveil(2): https://man.openbsd.org/unveil.2

## Goal

Let developers think in “pledge-ish” terms while the system enforces:
- Capsicum capability mode + rights
- preopen maps
- network broker policies
- UAPI surface gates

See: `docs/232-service-promise-profiles.md`, `docs/294-oblivious-sandboxing-launchers.md`.

## Mapping concept

Introduce an optional **profile frontend**:

- input: `pledge_style.promises` + `unveil_style.paths`
- output: canonical `sandbox.profile` with:
  - preopen map
  - syscall/UAPI allowlist
  - broker requirements (egress/listen)
  - “no ambient DNS” discipline

This is explicitly a *compiler*, not a second sandbox system.

## Example mapping (sketch)

### pledge-ish intent

- “This service only reads config, writes logs, and makes HTTPS requests.”

### Derived Derive profile

- filesystem: read-only for `/etc/derive/*`, write for `/var/log/<svc>`
- network: require `net.egress` grants for `tcp:443` and DNS mediation if hostname-based
- UAPI: only the minimal syscall/IOCTL families required

## Why this matters for ecosystem health

A capability-first OS lives or dies on how easy it is to do the right thing.
If we ship:

- a small “promise vocabulary”
- good defaults
- observation mode (learned profiles)

…then third-party software can become least-authority without everyone becoming a sandbox expert.

See:
- learned profiles: `docs/326-learned-promise-profiles-and-observation-mode.md`
- vocabulary + lint: `docs/271-promise-profile-vocabulary-and-lint.md`
