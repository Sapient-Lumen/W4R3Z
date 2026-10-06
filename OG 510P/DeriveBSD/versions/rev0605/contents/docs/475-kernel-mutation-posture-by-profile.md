# Kernel mutation posture by profile

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability, reproducibility  
**Patterns:** Plan→Apply→Receipt, Registry→Diff→Gate  

DeriveBSD already has kernel-mutation building blocks.
What this doc decides is narrower and more important for coherence:
**what is the default posture for boot tunables, runtime sysctl writes, module loading, and lockdown in each product shape?**

This is intentionally **not** a full backend spec for securelevel, sysctl taxonomy, or module signature format.
It is a product-default decision.

See also:
- ADR: `adrs/ADR-0065-kernel-mutation-posture-by-profile.md`
- sysctls as evidence: `docs/318-kernel-tunables-and-sysctls-as-evidence.md`
- kernel modules as evidence: `docs/276-kernel-module-policy-and-loading-as-evidence.md`
- lockdown posture: `docs/230-lockdown-levels-and-securelevel.md`
- sysctl diffs: `docs/429-sysctl-diff-as-drift-surface.md`
- product profiles: `docs/411-product-profiles-as-compilation-target.md`

## Why this needs a hard decision

The archive already says kernel mutation should be planned, receipted, and explainable.
Without a profile-shaped default, that principle still drifts in practice:

- fleet hosts end up with “temporary” runtime sysctl edits that quietly become the real baseline,
- workstation host state gets mutated by background helpers or support tools,
- general-purpose systems lose viability if every kernel change assumes a fleet-style maintenance service,
- and factory/regulatory images claim lockdown while still relying on runtime module-search-path folklore.

Kernel mutation is too security-relevant to leave as implied local custom.
The archive needs a stable default for **when runtime kernel mutation is normal, exceptional, or out of bounds**.

## Scope of this knob

`kernel_mutation` covers the default handling of:

- boot-time tunables and `kenv`-like knobs
- runtime sysctl writes outside activation
- kernel module load/unload posture and module-search-path mutability
- the expected relationship to securelevel/lockdown after activation

It does **not** decide every backend detail of key classification, signer format, or lease transport.

## Product-shape defaults

| Profile | `kernel_mutation` default | Practical meaning |
|---|---|---|
| A (`fleet_host`) | `activation-first-maintenance-leased` | Boot tunables are generation-bound; runtime sysctl mutation is maintenance-shaped and receipted; kmods are preload-first and routine runtime load/unload is not the fleet baseline. |
| B (`workstation`) | `activation-first-trusted-ui-maintenance` | Host kernel mutation should not happen silently in the background; risky sysctl/debug changes and runtime kmod loads require trusted-UI-visible maintenance or consented admin workflow. |
| C (`general_os`) | `derived-default-explicit-admin-fallback` | Derive-managed plans/receipts remain the default, but explicit local-admin fallback stays viable; stronger leases/lockdown are optional lanes, not hidden prerequisites. |
| D (`appliance_factory`) | `preload-only-lockdown-offline-maintenance` | Production posture is preload-only plus lockdown; runtime sysctl/kmod mutation is exceptional and belongs to offline or tightly approved maintenance workflows. |

These values live in `spec/examples/product.profiles.json` and are guarded by `tools/check_product_profiles.py`.

## Cross-profile invariants

Regardless of profile:

- boot-time tunables belong in the generation closure, not in ad-hoc mutable host files
- runtime sysctl mutation should be plan/receipt/event-shaped, never invisible folklore
- module loading is privileged code admission and should be explained by policy/plan/receipt, not by “the kernel found something on disk”
- lockdown claims are only credible if required runtime mutation has already been modeled and completed
- drift surfaces (`sysctl.diff`, `kmod.policy.diff`, snapshots/events) are part of the operator story, not afterthought diagnostics

## What this fixes by profile

### A) Secure fleet host (`fleet_host`)

Default: `activation-first-maintenance-leased`

- Fleet hosts should not normalize ad-hoc runtime kernel mutation as part of steady-state operations.
- Runtime sysctl writes outside activation are maintenance exceptions with receipts, not ambient service authority.
- Preload-first module posture keeps lockdown meaningful once health gates pass.

### B) Secure workstation (`workstation`)

Default: `activation-first-trusted-ui-maintenance`

- The host should not mutate kernel posture silently in the background while the user thinks they are just using apps.
- Risky sysctl/debug changes and runtime module loads should surface in trusted UI maintenance workflows.
- Workstation safety is not just about app isolation; it also means the host kernel does not become a hidden mutable substrate.

### C) General-purpose OS (`general_os`)

Default: `derived-default-explicit-admin-fallback`

- General-purpose viability requires that a competent local admin can still do driver work, troubleshooting, or compatibility changes without a fleet control plane.
- The derived lane remains the preferred and explainable path, but the archive should not pretend C is viable if every kernel mutation needs central ceremony.
- The fallback remains explicit and reviewable rather than ambient service mutability.

### D) Appliance factory / regulatory (`appliance_factory`)

Default: `preload-only-lockdown-offline-maintenance`

- Production claims about fixed posture and regulatory evidence become incoherent if runtime kernel mutation is ordinary.
- Required modules and tunables should be fixed before steady-state, then lockdown should make that claim real.
- Exceptional runtime mutation belongs to offline or strongly approved maintenance workflows with receipts.

## What this does **not** decide yet

This doc does **not** freeze:

- the exact sysctl risk taxonomy
- the exact list of commit-confirmed knobs
- the exact module signature or signer policy format
- the exact lockdown implementation across FreeBSD/other BSD targets
- the exact drift-check cadence or snapshot retention budget

Those remain implementation details or future RFC/ADR material.

## Why this is worth locking now

This decision collapses a recurring ambiguity without inventing a new subsystem:

- A gets activation-first fleet discipline with maintenance-shaped exceptions,
- B explicitly rejects silent host-kernel mutation in ordinary desktop life,
- C keeps local-admin viability honest,
- D gets a real preload+lockdown production baseline.

That is enough to guide future specs and coding while keeping low-level control details open.

## Design cue from current systems

A few ecosystem lessons are stable:

- FreeBSD and OpenBSD securelevel/lockdown primitives are useful because they turn post-boot privilege into something the kernel can still refuse
- sysctl remains a privileged mutable interface, which means it needs explicit budget and receipts if we want explainable systems
- kernel module search-path and runtime loader behavior are policy surfaces, not implementation trivia
- production/regulated environments only really have “lockdown” if required mutation happens before the lock is raised

DeriveBSD should steal those lessons while keeping the transport and backend replaceable.

Last updated: 2026-03-06r204
