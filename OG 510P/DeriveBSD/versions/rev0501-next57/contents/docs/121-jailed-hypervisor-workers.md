# Jailed hypervisor workers (bhyve-in-jail) (optional, v1)

DeriveBSD treats runtime components as hostile-by-default (microVMs, builders, even the hypervisor process).
One underused BSD-native defense-in-depth move is to run the **bhyve worker process inside a jail**, so a compromise of the VMM process has **less ambient authority**.

## What the platform supports

- FreeBSD added explicit support for bhyve inside jails (`security.jail.vmm_allowed`).
  - FreeBSD 12.0 release notes: `security.jail.vmm_allowed` enables `bhyve(8)` use within `jail(8)`.
    - https://www.freebsd.org/releases/12.0R/relnotes/
- The FreeBSD Handbook documents the *practical* devfs considerations for running bhyve in a jail (shared tap/nmdm namespaces, devfs rules).
  - https://docs.freebsd.org/en/books/handbook/virtualization/
- `jail(8)` explicitly warns that devfs exposure determines whether jail isolation is meaningful.
  - https://man.freebsd.org/jail

## DeriveBSD mapping

### Split the VMM into a “worker compartment”

- `derive-vmmd` (host control plane) remains small and policy-bound.
- It spawns **bhyve worker jails** that:
  - have a narrow filesystem view (only required binaries, ideally read-only)
  - get only the device nodes they need (devfs ruleset)
  - have network either disabled or explicitly vnet-scoped

### Policy hooks

Policy can require, per target kind:
- `runtime.hypervisor.jailed = true`
- minimum host hardening profile
- explicit devfs allowlist
- explicit network mode

### Evidence (“explainability”)

Every launch should record:
- whether bhyve ran in a jail
- the jail params (in normalized form)
- the devfs ruleset id/hash

This makes “limit authority” measurable, not aspirational.

## Reality checks

- This feature is *optional* in v1: it is powerful but easy to misconfigure.
- DeriveBSD should ship conformance tests for:
  - `security.jail.vmm_allowed` present + enabled
  - minimal devfs exposure
  - tap/nmdm naming collision avoidance (documented in the Handbook)

Also note that regressions can happen: there are reports/bugs where bhyve-in-jail behavior changed across releases.
Example bug thread:
- https://bugs.freebsd.org/bugzilla/show_bug.cgi?id=273557

Last updated: 2026-02-23
