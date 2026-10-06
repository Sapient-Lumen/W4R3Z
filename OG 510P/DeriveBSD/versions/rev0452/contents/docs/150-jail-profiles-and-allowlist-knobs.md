# Jail profiles and allowlist knobs (blast-radius-by-default)

DeriveBSD relies on jails for build sandboxes, fetchers, and some control-plane helpers.
FreeBSD jails have a large set of **opt-in** capabilities (the `allow.*` family) and related knobs.
DeriveBSD should:

- define **named jail profiles** (builder, fetcher, hypervisor-worker, etc.)
- derive their exact knobs from policy
- treat the profile as an evidence-bearing artifact (`jail.profile.json`) bound to the generation

## Prior art

FreeBSD documents jail parameters and the security implications of enabling optional features such as raw sockets.

## DeriveBSD shape

### Baseline stance

- deny-by-default for `allow.*`
- `exec.clean=1` (clean environment)
- `mount.devfs=1` + devfs ruleset that exposes only required device nodes
- explicit resource budgets (`rctl`/`cpuset`) for hostile-builder containment

### Example profiles (sketch)

**builder**
- no raw sockets
- no module loading
- no mount permissions
- no VNET by default
- devfs: minimal (null, zero, random, urandom, tty, etc.)

**fetcher**
- minimal filesystem view
- network permitted only via derived pf/FIB egress plan
- no raw sockets

**hypervisor-worker**
- VMM-related devices exposed via devfs ruleset
- no write access outside its runtime directory
- pf/FIB + capability routing manifests constrain egress and authority

### Evidence objects

- `jail.profile.json` (JCS-hashable)
  - profile name
  - jail parameters (allowlist)
  - devfs ruleset id + content digest
  - network posture (pf anchor ids + FIB id)
  - resource budgets

## Why this matters for DeriveBSD

This is a cheap, high-leverage safety rail:

- reduces default blast radius
- makes privilege changes obvious (profile diffs)
- gives `derive explain` concrete answers about *ambient authority*

See also:
- `docs/49-capsicum-casper-hardening.md`
- `docs/143-resource-controls-rctl-racct-cpuset.md`
- `docs/144-routing-isolation-fibs-setfib.md`
- `docs/325-rootless-jails-and-unprivileged-compartments.md`
