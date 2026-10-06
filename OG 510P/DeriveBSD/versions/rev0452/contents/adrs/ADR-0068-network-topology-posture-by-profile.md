# ADR-0068: Network topology posture by profile

Date: 2026-03-06
Status: Accepted

## Context

DeriveBSD already has the raw ingredients for a coherent networking story:
`docs/322-network-topology-and-firewall-as-derived-operations.md`, `docs/64-networking-modes-mapping.md`,
`docs/281-network-egress-broker-and-consent.md`, and `docs/286-inbound-listen-broker-and-firewall-leases.md` define typed topology artifacts, brokered egress/listening, and the importance of commit-confirmed changes.

What the archive still lacked was a **product-default boundary** for host topology mutation itself.
Without that boundary, the same topology vocabulary drifts into contradictory defaults:

- fleet hosts either permit ad-hoc `ifconfig` / route / `pf` edits or become unusably rigid during incidents,
- workstations either hide risky Wi-Fi/VPN/topology changes behind shell folklore or over-centralize ordinary local networking,
- general-purpose installs cannot tell whether derived networking is preferred or merely aspirational,
- and factory/regulatory images claim sealed production posture while still relying on live, hand-applied topology tweaks.

## Decision

DeriveBSD will treat **network topology posture** as a first-class, profile-shaped default captured in
`spec/examples/product.profiles.json` under `networking` and guarded by `tools/check_product_profiles.py`.

This posture covers the default handling of:

- host link/address/route and `pf`-root mutation outside workload-facing egress/listen brokers,
- whether risky topology changes are activation-first or can occur live,
- whether commit-confirmed rollback is part of the default safety contract,
- and whether maintenance windows / leases / trusted UI are required for stronger host-topology mutation.

The default values are:

- **A / `fleet_host`**: `activation-first-commit-confirmed-maintenance-leased`
- **B / `workstation`**: `trusted-ui-local-first-commit-confirmed`
- **C / `general_os`**: `derived-preferred-explicit-admin-fallback`
- **D / `appliance_factory`**: `sealed-offline-windowed-commit-confirmed`

## Meaning by profile

### A) Secure fleet host (`fleet_host`)

- Host topology is activation-first and policy-derived by default.
- Risky live changes require maintenance leases and commit-confirmed rollback.
- Remote recovery and remote-brick avoidance are part of the baseline contract, not an afterthought.

### B) Secure workstation (`workstation`)

- Ordinary local networking remains humane: Wi-Fi, VPN, and local link changes stay real.
- Riskier topology changes must be trusted-UI-visible and commit-confirmed rather than silent shell folklore.
- The workstation should not surprise the user with hidden exposure-expanding or connectivity-stranding host edits.

### C) General-purpose OS (`general_os`)

- Derived networking is preferred and should emit plans/receipts by default.
- Explicit local-admin fallback remains viable for compatibility and lab workflows.
- C keeps broad usability without silently redefining stricter fleet/workstation/factory posture.

### D) Appliance factory / regulatory (`appliance_factory`)

- Production topology is sealed by default and does not assume ad-hoc live mutation.
- Risky topology changes belong in approved maintenance windows with rollback/confirmation.
- Offline-capable maintenance matters more than convenience shell hotfixes.

## Consequences

### Positive

- The archive now has a stable answer to “how mutable is host networking by default?” across A–D.
- Workstation networking stays humane without turning risky topology edits into ambient shell folklore.
- Factory/regulatory posture now matches the archive’s sealed/maintenance-window claims instead of quietly undermining them.

### Negative / trade-offs

- This adds one more stable profile knob that must remain small and guardrailed.
- Exact health-check sets, confirm-window defaults, and Wi-Fi/VPN UI details remain implementation work.
- General-purpose compatibility remains real, so reviewers still need to resist adapter lanes becoming ambient defaults.

## Non-goals

This ADR does **not** decide:

- the exact network-manager UX for Wi-Fi roaming,
- the exact topology digest algorithm or route canonicalization scheme,
- the exact confirm-window duration or health-check set,
- or the exact backend split between `ifconfig`, `route`, `pfctl`, `netgraph`, `if_bridge`, and future adapters.

Those remain implementation work or future RFC/ADR material.

## Why this shape

The coherence win is not “nobody may touch networking live” and it is not “let shell hotfixes rule.”
It is deciding that:

- A defaults to activation-first, maintenance-leased, commit-confirmed topology mutation,
- B defaults to trusted-UI-visible local networking with rollback for risky host-topology edits,
- C defaults to derived networking while keeping explicit local-admin fallback,
- D defaults to sealed/offline-windowed topology with rollbackable approved mutation.

That is enough to guide future specs and coding without prematurely freezing the network UI stack or topology planner implementation.
