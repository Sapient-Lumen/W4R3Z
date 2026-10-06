# ADR-0065: Kernel mutation posture by profile

Date: 2026-03-06
Status: Accepted

## Context

DeriveBSD already treats kernel mutation as evidence: `docs/318-kernel-tunables-and-sysctls-as-evidence.md`,
`docs/276-kernel-module-policy-and-loading-as-evidence.md`, `docs/429-sysctl-diff-as-drift-surface.md`,
and `docs/230-lockdown-levels-and-securelevel.md` define plans, receipts, drift events, module policy, and lockdown.

What the archive still lacked was a **product-default boundary** for when runtime kernel mutation is ordinary,
when it is a maintenance exception, and when preload + lockdown is the baseline.
Without that boundary, the same sysctl/kmod vocabulary drifts into contradictory defaults:

- fleets quietly tolerate ad-hoc runtime knob edits because “someone had to tune the network”,
- workstations inherit hidden background host mutation from helpers or vendor tools,
- general-purpose installs lose local-admin viability because every risky knob is treated like fleet governance,
- and factory/regulatory systems claim lockdown while still depending on live runtime module/search-path folklore.

## Decision

DeriveBSD will treat **kernel mutation posture** as a first-class, profile-shaped default captured in
`spec/examples/product.profiles.json` under `kernel_mutation` and guarded by `tools/check_product_profiles.py`.

This posture covers the default handling of:

- boot-time tunables (`loader.conf`, `kenv`, similar boot knobs),
- runtime sysctl writes outside activation,
- kernel module loading/search-path mutability,
- and the expected relationship to lockdown/securelevel once activation is complete.

The default values are:

- **A / `fleet_host`**: `activation-first-maintenance-leased`
- **B / `workstation`**: `activation-first-trusted-ui-maintenance`
- **C / `general_os`**: `derived-default-explicit-admin-fallback`
- **D / `appliance_factory`**: `preload-only-lockdown-offline-maintenance`

## Meaning by profile

### A) Secure fleet host (`fleet_host`)

- Boot tunables are generation-bound and reviewable.
- Runtime sysctl mutation outside activation is not ambient host behavior; risky writes require a maintenance lease and receipt.
- Required modules should be preloaded during activation, then the host should raise lockdown so routine runtime load/unload is not a normal operational path.

### B) Secure workstation (`workstation`)

- The host should not grow silent background kernel mutation from desktop helpers, updaters, or support agents.
- Risky sysctl/debug changes and runtime module loads belong to a trusted-UI-visible maintenance path, not invisible background UX.
- Boot tunables remain generation-bound so the user can explain what host posture they actually booted.

### C) General-purpose OS (`general_os`)

- The derive-managed lane remains the default and should emit plans/receipts/diffs for kernel mutation.
- Explicit local-admin fallback remains viable so ordinary local development, driver work, or troubleshooting do not depend on remote maintenance services.
- Stronger lockdown and lease-driven controls remain available, but are explicit choices rather than hidden prerequisites.

### D) Appliance factory / regulatory (`appliance_factory`)

- Production posture is preload-only + lockdown by default: required modules and boot tunables are fixed before steady-state.
- Runtime sysctl/kmod mutation is exceptional and belongs to offline or tightly approved maintenance workflows.
- Live module search-path or convenience runtime loading is out of bounds for the production baseline.

## Consequences

### Positive

- The archive now has a coherent answer to “when is runtime kernel mutation normal?” across A–D.
- Fleet and factory shapes can keep lockdown claims honest without making general-purpose viability impossible.
- Workstation posture now explicitly resists silent host-level kernel mutation under ordinary UI workflows.

### Negative / trade-offs

- This adds one more stable product-profile knob that must remain small and guardrailed.
- Some implementation details remain open: exact sysctl risk classes, exact maintenance lease envelope, and exact commit-confirmed shortlist.
- General-purpose fallback remains a deliberate compromise: it preserves viability but leaves more local-footgun room than A/B/D.

## Non-goals

This ADR does **not** decide:

- exact sysctl key classification taxonomy,
- exact module signer or allowlist format,
- exact securelevel/lockdown backend semantics on every BSD target,
- or exact cadence/retention for drift checks and snapshots.

Those remain implementation work or future RFC/ADR material.

## Why this shape

The coherence win is not “lock everything always.”
It is deciding that:

- A is activation-first with leased maintenance exceptions,
- B is activation-first with trusted-UI maintenance visibility,
- C preserves explicit local-admin fallback,
- D is preload-only + lockdown in production.

That is enough to guide future specs and coding without prematurely freezing the low-level control plane.
