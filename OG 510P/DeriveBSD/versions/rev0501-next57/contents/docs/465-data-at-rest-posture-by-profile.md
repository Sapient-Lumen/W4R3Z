# Data-at-rest posture by profile

**Tier:** C (Optional lane)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability, supply-chain  
**Patterns:** Plan→Apply→Receipt, Broker→Lease→Receipt  

DeriveBSD already has a credible **data-at-rest** lane.
What this doc decides is narrower and more important for coherence:
**what is the default encryption + unlock posture for each product shape?**

This is intentionally **not** a backend-choice doc.
It is a product-default decision.

See also:
- ADR: `adrs/ADR-0055-data-at-rest-posture-by-profile.md`
- ZFS encryption lanes: `docs/409-zfs-encryption-and-key-management.md`
- break-glass / recovery authority: `docs/250-breakglass-and-recovery-workflows.md`
- sealed unlock evolution: `docs/272-sealed-secrets-attested-unsealing.md`
- human home-state posture: `docs/463-human-identity-and-home-state-posture-by-profile.md`
- product profiles: `docs/411-product-profiles-as-compilation-target.md`

## Why this needs a hard decision

Every serious system eventually answers the same uncomfortable questions:

- what data is encrypted by default, and what is allowed to remain available before login?
- which product shapes may boot unattended, and by what authority lane?
- are raw file keys or direct URL key locations treated as normal convenience, or as compatibility exceptions?
- does a workstation really honor a lost-device threat model, or only claim to?

If the archive leaves this as “we’ll decide later,” real systems drift toward:

- raw file-backed auto-unlock on fleet hosts,
- daily user state unlocked at boot on workstations,
- compatibility-mode installs swallowing the secure path,
- or factory images that ship hidden recovery secrets nobody wants to document.

So we decide the **default encryption + unlock authority model** now while leaving exact dataset topology, TPM policy shape, and UX details open.

## Product-shape defaults

| Profile | `data_at_rest` default | Practical meaning |
|---|---|---|
| A (`fleet_host`) | `encrypted-state-attested-or-brokered-unlock` | Mutable state is encrypted by default; unattended bring-up must use attested local or brokered recovery lanes, not image-baked file keys. |
| B (`workstation`) | `lost-device-default-login-bound-user-state` | Private user/home state is encrypted by default and should unlock with the human, not ambient boot convenience. |
| C (`general_os`) | `encrypted-preferred-explicit-compatibility-fallback` | Encryption is preferred and easy, but broad-compat installs may choose an explicit fallback. |
| D (`appliance_factory`) | `encrypted-production-state-attested-or-quorum-maintenance-unlock` | Production/factory state is encrypted by default; maintenance/recovery unlock is explicit, receipted, and often quorum-shaped. |

These values live in `spec/examples/product.profiles.json` and are guarded by `tools/check_product_profiles.py`.

## Cross-profile invariants

Regardless of profile:

- mutable/user-secret state should prefer ZFS-native encryption rather than ad-hoc wrapper scripts
- unlock operations must remain receipted and explainable
- raw file-backed or direct URL-backed key locations are not first-class Derive defaults
- ordinary recovery should not depend on secrets baked into images or hidden in support bundles
- re-key / recovery / break-glass workflows must stay separate from ambient day-to-day convenience

## What this fixes by profile

### A) Secure fleet host (`fleet_host`)

Default: `encrypted-state-attested-or-brokered-unlock`

- Fleet hosts are replaceable, but their mutable state still deserves encryption by default.
- Unattended boot is compatible with this profile only through attested local unlock or brokered recovery policy.
- Static host-local file keys may exist as explicit adapters for special environments, but they are not the Derive default.

### B) Secure workstation (`workstation`)

Default: `lost-device-default-login-bound-user-state`

- Workstations assume device theft/loss is normal enough to design for.
- Ordinary user/home data should unlock on login/session/presence, not just because the machine booted.
- Small pre-login state may still exist for boot/login plumbing, but private human data belongs in the login-bounded lane.

### C) General-purpose OS (`general_os`)

Default: `encrypted-preferred-explicit-compatibility-fallback`

- General-purpose viability keeps the compatibility door open.
- The secure path should still be obvious and easy.
- If encryption is relaxed for compatibility, that relaxation should be explicit and reviewable rather than silently inherited from convenience defaults.

### D) Appliance factory / regulatory (`appliance_factory`)

Default: `encrypted-production-state-attested-or-quorum-maintenance-unlock`

- Production/factory/regulatory state is encrypted by default.
- Maintenance or recovery unlock should be explicitly authorized, receipted, and often quorum-shaped rather than hidden inside shipped images.
- Production images should not carry convenience unlock secrets that quietly become permanent dependencies.

## What this does *not* decide

Still open:

- exact dataset split between boot-critical / pre-login / login-bounded / production state
- TPM-policy vs broker-policy expression details
- metadata-leakage budgets and boot-partition posture
- exact re-key cadence / migration workflow / operator UX
- how break-glass remote unlock should differ from normal unattended policy in receipts and controls

That work stays implementation-level.
This doc only fixes the product-default boundary so the archive can keep converging without drifting.

## Design cue from current systems

Three current-system lessons matter here:

- OpenZFS exposes encryption as a dataset-creation choice, tracks loaded-key state explicitly, and supports multiple key locations — which is powerful, but also exactly why DeriveBSD should distinguish “possible in ZFS” from “wise as a product default.”
- Android’s file-based encryption model explicitly splits credential-encrypted and device-encrypted storage, which is a strong cue that workstation/private human data should unlock with the human whenever possible rather than merely at boot.
- systemd-homed treats activated homes as mountable identity-bearing objects and compares user-record copies at activation time, reinforcing the idea that human state activation should be explicit and bounded rather than ambient.

DeriveBSD should steal the lesson, not the surrounding convenience folklore.

Last updated: 2026-03-06r194
