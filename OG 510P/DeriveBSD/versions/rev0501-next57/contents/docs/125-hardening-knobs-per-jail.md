# Per-jail hardening knobs (HardenedBSD secadm mindset)

DeriveBSD’s security posture improves when “hardening” stops being a pile of ad-hoc sysctls and becomes a **policy result**.

HardenedBSD offers a useful inspiration: expose exploit-mitigation knobs and apply them *per jail* (scoped compartments), rather than as global toggles.

References:
- HardenedBSD “easy feature comparison” (ASLR, SEGVGUARD, W^X, etc.): https://hardenedbsd.org/content/easy-feature-comparison
- HardenedBSD `secadm` README (per-jail rules; toggling ASLR/SEGVGUARD/mprotect(exec)): https://hardenedbsd.org/sites/default/files/README.txt
- `secadm` repo notes (MAC module hooks exec; per-jail rules): https://github.com/HardenedBSD/secadm

## DeriveBSD mapping

### Make hardening declarative

Add a policy-visible object:
- `hardening.profile` (e.g. `minimal`, `server`, `locked-down`)
- `hardening.knobs` (fine-grained, allowlisted)

### Scope it to compartments

Apply hardening to:
- build jails
- bhyve worker jails
- service jails

This aligns with “treat builders hostile” and “limit authority.”

### Record it as evidence

Every build/run decision should record:
- selected profile
- effective knobs
- enforcement mechanism (sysctl/MAC module/etc)

## Why this is “greenfield-worthy”

Older OSes struggle because hardening is:
- global
- undocumented
- changed by hand

DeriveBSD can instead treat it as:
**policy input → policy decision → audited enforcement**.

Last updated: 2026-02-23
