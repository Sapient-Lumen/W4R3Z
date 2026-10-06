# Host hardening profile (v1 baseline)

Define named profiles so security posture is explainable and not a “toggle soup”.

## Profiles (idea)
- baseline: sane defaults
- locked: tighter mutation and networking posture
- forensic: adds auditing and stricter logging

Inspiration:
- Bottlerocket minimizes host mutation by routing settings through an API (rather than “ssh and change things”). https://github.com/bottlerocket-os/bottlerocket

## Key levers
- Secure Boot-compatible generation binding (`docs/51-secure-boot-integration.md`)
- Jail sandbox defaults (`docs/45-build-sandbox-jails.md`)
- Capsicum/Casper confinement for daemons (`docs/49-capsicum-casper-hardening.md`)
- pf deny-by-default networking (`docs/26-virtual-networking-pf.md`)

## “Break-glass” posture (avoid normalizing mutation)

To keep the default posture immutable, prefer:
- an *ephemeral* debug environment (service jail or microVM) that can be launched, used, and destroyed
- an audited “break-glass” workflow that emits evidence objects and is policy-gated

This reduces the incentive to keep permanent SSH-style mutation paths around.

See RFC-0031 and ADR-0011.
Last updated: 2026-02-23
