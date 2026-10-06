# Service promise profiles (pledge/unveil ergonomics for FreeBSD primitives)

DeriveBSD already has strong sandbox ingredients (jails, Capsicum, MAC, portals), but **ergonomics** decide whether they get used.

This doc proposes a *single reviewable surface*—a **promise profile**—that compiles into:
- jail profile + mounts (what paths exist at all)
- devfs ruleset + device grants (what device nodes exist at all)
- Capsicum/Casper policy (what can be done with already-open handles)
- portal needs (what must be brokered interactively)
- optional MAC knobs (defense-in-depth)

The goal is *OpenBSD pledge/unveil-style* “easy to apply everywhere” **without** requiring pledge/unveil in the kernel.

## What a promise profile is

A **promise profile** is a small, typed, versioned artifact:
- **named** (stable id like `profile:fetcher@1`)
- **diff-friendly** (authority changes are obvious)
- **monotonic** (can tighten further; loosening requires policy decision record)
- **compilable** (no runtime interpretation in hot paths)

It is the bridge between:
- human intent (“this service is a DNS+HTTP fetcher and nothing else”)
- machine enforcement (jail view + capsicum rights + portals)

## Making least-authority practical: observe → propose → review

Hand-authoring perfect profiles is unrealistic.
DeriveBSD should ship a first-class **observation mode** that runs a unit, records its access attempts, and emits a *candidate profile patch* for review.

See: `docs/326-learned-promise-profiles-and-observation-mode.md`.

## Shape (high level)

Schema + example: `spec/sandbox.profile.schema.json`, `spec/examples/sandbox.profile.json`.

Promise vocabulary + lint rules: `docs/271-promise-profile-vocabulary-and-lint.md`.

A profile should be able to express (at minimum):

1) **Filesystem visibility** (unveil-like)
- the OS view is *constructed*: mount only what’s needed
- allowlist paths with simple `r/rw/rx` semantics

2) **Network intent**
- no ambient networking
- use the **network egress capability** lane where possible (policy decides egress grants)
- use the **listen broker** lane for inbound exposure (policy decides what ports may be opened)

3) **Handle rights (Capsicum)**
- restrict operations on already-open fds (read/write/ioctl/seek/etc)
- prefer “preopen then cap_enter” discipline

4) **Brokered exceptions (portals)**
- if the service truly needs late-bound access, it must go through a broker

5) **Runtime invariants**
- “lock” the profile once applied (monotonic tightening)
- optional “must run under verified-exec” requirement (see docs/233)

## Where promise profiles plug in

### A) Service supervision (svcdb)

- Each service entry can optionally reference a promise profile digest.
- The svcdb compiler checks:
  - the profile exists
  - declared dependencies imply required promises (lint)
  - portals requested match profile allowances

### B) Build sandboxing

Build profiles are just promise profiles:
- a builder profile can forbid network by default
- impurities become explicit profile changes (and thus show up in diffs)

### C) MicroVM/service-jail templates

A template microVM/jail can declare:
- the profile
- the mount plan
- the capset

So a microVM becomes “profile + rootfs + policy outputs”.

## Minimal policy rules (so this doesn’t become a mess)

- **Profile edits are authority edits** → require a policy decision record.
- Profiles are **small and curated**: add new promises only when several programs need them.
- Profiles must compile to deterministic enforcement.

## Related docs

- Pledge/unveil mindset: `docs/117-pledge-unveil-mindset.md`
- Jail profiles: `docs/150-jail-profiles-and-allowlist-knobs.md`
- Capsicum/Casper hardening: `docs/49-capsicum-casper-hardening.md`
- Portals/powerbox: `docs/179-portals-and-powerbox.md`
- Network egress broker: `docs/281-network-egress-broker-and-consent.md`
- Inbound listen broker: `docs/286-inbound-listen-broker-and-firewall-leases.md`
- Capability routing + lint/viz: `docs/189-capability-graph-lint-and-viz.md`
- Lint reports as artifacts: `docs/237-lint-reports-and-contract-testing.md`
- Process contracts + service ownership: `docs/235-process-contracts-and-service-ownership.md`

See RFC-0166.

Last updated: 2026-02-25
