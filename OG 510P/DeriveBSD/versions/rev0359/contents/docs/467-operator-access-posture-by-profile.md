# Operator-access posture by profile

**Tier:** C (Optional lane)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate  

DeriveBSD already has an operator-session lane.
What this doc decides is narrower and more important for coherence:
**what is the default posture for human administrative access in each product shape?**

This is intentionally **not** an access-broker implementation doc.
It is a product-default decision.

See also:
- ADR: `adrs/ADR-0057-operator-access-posture-by-profile.md`
- operator sessions / SSH certs: `docs/311-operator-access-leases-and-ssh-certs.md`
- terminal session recording: `docs/292-terminal-session-recording-as-evidence.md`
- recording/detail/export defaults for that lane: `docs/617-operator-access-recording-detail-and-export-posture-by-profile.md`
- breakglass: `docs/236-breakglass-and-recovery-mode.md`
- product profiles: `docs/411-product-profiles-as-compilation-target.md`

## Why this needs a hard decision

Every system that avoids deciding operator access ends up deciding it anyway through drift:

- static `authorized_keys` files become the real access policy,
- workstation remote admin quietly becomes always-on SSH or agent caching,
- factory/regulated images inherit vendor maintenance keys,
- and nobody can answer whether login, elevation, recording, and breakglass are one lane or four.

DeriveBSD already says authority should be leased, receipted, and reviewable.
Administrative access is too important to leave as an undocumented exception.
So we fix the **product-default human admin posture** now while leaving exact broker, CA, recording backend, and shell-profile details open.

## Product-shape defaults

| Profile | `operator_access` default | Practical meaning |
|---|---|---|
| A (`fleet_host`) | `brokered-jit-cert-role-shell-escalation-separate` | Fleet admin uses brokered short-lived certs; role shells/restricted commands are preferred; escalation is separate from login. |
| B (`workstation`) | `local-user-presence-preferred-jit-remote-admin-exceptional` | Local secure-attention/user-presence admin is the default; remote shell admin is exceptional and must be leased/JIT if it exists. |
| C (`general_os`) | `local-admin-default-jit-remote-preferred-explicit-static-key-adapter` | Classic local admin stays compatible; Derive-managed remote admin prefers JIT/leased access; static keys remain explicit adapter territory only. |
| D (`appliance_factory`) | `maintenance-window-jit-cert-quorum-no-standing-admin-keys` | Production/factory admin stays maintenance-window-shaped, JIT, and strongly approved; shipped standing admin keys are forbidden by default. |

These values live in `spec/examples/product.profiles.json` and are guarded by `tools/check_product_profiles.py`.

## Cross-profile invariants

Regardless of profile:

- standing operator/admin SSH keys and permanent bastion access are not the preferred default
- login is distinct from escalation
- operator sessions emit typed evidence even when full TTY recording is not enabled
- breakglass remains an explicit exceptional lane, not the ambient default
- remote admin authority, when it exists, lands in certificates / leases / durable policy rather than silent standing credentials

## What this fixes by profile

### A) Secure fleet host (`fleet_host`)

Default: `brokered-jit-cert-role-shell-escalation-separate`

- Fleet hosts keep operator access brokered, short-lived, and revocable.
- Role shells or forced commands should be preferred over "everyone lands in a full shell and figures it out later."
- Escalation remains a separate reviewable lane.

### B) Secure workstation (`workstation`)

Default: `local-user-presence-preferred-jit-remote-admin-exceptional`

- Secure-attention / local user presence is the normal authority model for workstation admin.
- Remote shell admin is exceptional and should not become the invisible default behind the trusted UI.
- Remote assistance remains the user-facing support lane; operator shell admin is a different, narrower authority.

### C) General-purpose OS (`general_os`)

Default: `local-admin-default-jit-remote-preferred-explicit-static-key-adapter`

- Compatibility keeps classic local admin viable.
- Derive-managed remote admin should still prefer JIT/leased access.
- Static key and classic bastion patterns can exist only as explicit adapters, not as the archive’s preferred operational truth.

### D) Appliance factory / regulatory (`appliance_factory`)

Default: `maintenance-window-jit-cert-quorum-no-standing-admin-keys`

- Maintenance/operator access should be shaped by maintenance windows, not ambient shipped credentials.
- Standing vendor/admin keys are forbidden by default in shipped or factory images.
- Stronger approvals and explicit breakglass posture remain part of the baseline for sensitive production maintenance lanes.

## What this does *not* decide

Still open:

- exact role-shell / forced-command vocabulary
- recording/detail/export defaults now live in `docs/617-operator-access-recording-detail-and-export-posture-by-profile.md`; only finer role/class and retention details remain
- offline or partitioned operation when the broker/CA is unreachable
- workstation local-elevation UX details and secure-attention hooks
- renewal, revoke, and session-survival semantics under network partitions

That work stays implementation-level.
This doc only fixes the product-default boundary so the archive can keep converging without drifting.

## Design cue from current systems

A few ecosystem lessons are stable:

- OpenSSH certificates make short-lived, principal-scoped SSH access boring enough to be the default instead of an aspirational security project.
- doas-style local elevation keeps "login" and "privileged command" separate with a small, explicit rules surface.
- session-recording systems keep proving that recording/storage/retention are a separate governance problem from mere session admission.

DeriveBSD should steal the lesson, not the standing-key folklore.

Last updated: 2026-03-21r347
