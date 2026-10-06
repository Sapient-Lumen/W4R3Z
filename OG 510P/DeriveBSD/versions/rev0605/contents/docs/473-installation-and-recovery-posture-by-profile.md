# Installation-and-recovery posture by profile

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** operability, reproducibility, isolation  
**Patterns:** Plan→Apply→Receipt, Registry→Diff→Gate  

DeriveBSD already knows how to model install and recovery as **derived operations**.
What this doc decides is narrower and more important for coherence:
**what is the default installation/recovery posture in each product shape?**

This is intentionally **not** an installer-stack doc.
It is a product-default decision.

See also:
- ADR: `adrs/ADR-0063-installation-and-recovery-posture-by-profile.md`
- install/recovery lane: `docs/309-installation-and-recovery-as-derived-operations.md`
- disk mutation lane: `docs/310-disk-layout-plans-and-receipts.md`
- derived recovery images: `docs/360-derived-recovery-images-and-minimal-userspace.md`
- breakglass recording/detail/export posture: `docs/618-breakglass-recording-detail-and-export-posture-by-profile.md`
- destructive reprovision evidence/detail/export posture: `docs/619-destructive-reprovision-evidence-detail-and-export-posture-by-profile.md`
- product profiles: `docs/411-product-profiles-as-compilation-target.md`

## Why this needs a hard decision

Install/recovery posture eventually gets decided one way or another.
If the archive avoids deciding it, real systems drift toward:

- remote fleet reprovisioning that can hit the wrong disk because device identity never became mandatory,
- workstation reinstall flows that bury destructive action under “next, next, next”,
- general-purpose compatibility paths that quietly become the authority model,
- factory/reset workflows that live in shell history instead of signed bundles and retained receipts.

DeriveBSD already says disk mutation, key posture, and recovery authority must be planned and explainable.
That only becomes coherent if the archive fixes the **default authority model for install and recovery** instead of leaving it to installer folklore.

## Product-shape defaults

| Profile | `installation_recovery` default | Practical meaning |
|---|---|---|
| A (`fleet_host`) | `target-bound-additive-breakglass` | Reprovisioning is idempotent and target-device-bound; additive create/grow is routine, destructive disk mutation is breakglass/maintenance shaped. |
| B (`workstation`) | `guided-consent-encrypted-default` | Install/recovery is trusted-UI-guided, destructive edits require explicit disk confirmation, and encrypted-root posture is the baseline. |
| C (`general_os`) | `guided-choice-explicit-destructive` | Derive-guided and bounded compatibility/classic installer paths may coexist, but destructive repartitioning remains explicit and reviewable. |
| D (`appliance_factory`) | `target-bound-offline-resettable` | Production/factory installs are target-bound and offline-capable by default; destructive reprovisioning belongs to signed reset bundles/markers with retained receipts. |

These values live in `spec/examples/product.profiles.json` and are guarded by `tools/check_product_profiles.py`.
The narrower destructive reset/reseed authority default now lives in the separate `destructive_reprovision` profile knob and contract doc: `docs/483-destructive-reprovisioning-and-reset-authority.md`.

## Cross-profile invariants

Regardless of profile:

- install and recovery media stay derived, signed, and policy-bound rather than mutable live-CD folklore
- target-device selection must be explainable enough to answer “which disk did we intend to touch?” after the fact
- additive create/grow is the ordinary path; shrink/reformat/erase requires stronger intent than routine provisioning
- encrypted-root posture belongs to product policy, not last-minute installer improvisation
- recovery availability matters because a secure system that cannot be repaired safely will still be repaired unsafely

## What this fixes by profile

### A) Secure fleet host (`fleet_host`)

Default: `target-bound-additive-breakglass`

- Remote or console-driven reprovisioning should be safe to retry because the plan binds to device identity and ordinary mutation stays additive.
- Destructive disk edits belong in breakglass or maintenance policy rather than the happy path.
- Recovery/install carriers may vary (virtual media, on-disk recovery slot, verified mirror), but they must stay signed and ready.

### B) Secure workstation (`workstation`)

Default: `guided-consent-encrypted-default`

- The person holding the laptop should see clear disk identity and destructive intent before the system wipes or repartitions anything.
- Encrypted-root posture is the baseline for ordinary private user state; recovery cannot quietly solve UX by baking secrets into images.
- A local verified recovery path should remain available because “find another machine and rebuild rescue media” is not a humane default.

### C) General-purpose OS (`general_os`)

Default: `guided-choice-explicit-destructive`

- General-purpose installs keep room for compatibility/classic installer adapters without making them the secret product truth.
- Encryption remains preferred, but explicit fallback is allowed when hardware, portability, or compatibility demands it.
- Destructive disk operations must stay visible and named instead of hiding behind one-click convenience.

### D) Appliance factory / regulatory (`appliance_factory`)

Default: `target-bound-offline-resettable`

- Factory/regulatory installs assume target-device identity, approved offline carriers, and retained receipts as the normal story.
- Production reset or reprovision belongs to signed reset bundles/markers and review-heavy station workflows, not bench lore.
- Recovery must remain available without live upstream reachability because regulated/offline claims collapse otherwise.

## What this does *not* decide

Still open:

- exact disk-layout frontend or TUI/GUI installer stack
- exact recovery-image packaging (EFI payload, ISO, boot environment, etc.)
- exact trusted-UI copy and education flow on B
- exact carrier / transport shape for `reset.authorization` on each platform
- exact remote virtual-media / BMC adapter behavior for A/D

That work stays implementation-level.
This doc only fixes the product-default boundary so the archive can keep converging without drifting.

## Design cue from current systems

A few lessons are stable:

- additive repartitioning is safer as the routine path than “installer can do anything all the time”
- recovery images work better when they are treated as durable product artifacts, not emergency improvisation
- text-mode or ramdisk installers can still be excellent when device selection and destructive intent are made explicit
- factory/reset paths must be governed capabilities, not shell-history folklore

DeriveBSD should steal those lessons while keeping frontends and transport helpers replaceable.

Last updated: 2026-03-21r350
