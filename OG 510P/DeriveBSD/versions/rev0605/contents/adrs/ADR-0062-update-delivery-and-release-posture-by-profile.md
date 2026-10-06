# ADR-0062: Update-delivery and release posture by profile

- **Status:** Accepted
- **Date:** 2026-03-06

## Context

DeriveBSD already has substantial update machinery on paper:
`docs/61-channel-metadata-tuf-inspired.md` defines signed channel metadata,
`docs/112-health-gated-updates.md` makes post-boot health a first-class success criterion,
`docs/177-fleet-coordinated-rollouts.md` and `docs/258-staged-rollouts-and-cohorts.md` define receipted rollout control,
`docs/138-offline-signed-update-bundles.md` and `docs/273-airgap-mirror-kits-and-sneakernet-updates.md` define offline carriers,
and `docs/403-swhid-fallback-and-long-term-source-availability.md` captures the rebuildability side of the lane.

What the archive still lacked was the **product-shape default** for update delivery and release finalization.
Without that, incompatible stories quietly coexist:

- **A** may claim fleet-safe updates while drifting toward opaque always-on host updaters or ad-hoc rollout controllers.
- **B** may discover updates safely but still spring surprise apply/reboot behavior on the human holding the device.
- **C** cannot tell whether a central coordinator, health-gate stack, or mirror-kit workflow is required just to remain viable.
- **D** may claim regulated/offline posture while still making production success depend on live channels instead of approved bundles and quarantine→promote workflows.

We do **not** need to choose one update agent, one GUI, one graph server, or one mirror-kit container here.
We do need a stable, checkable answer to:

- which product shapes are health-gated by default vs merely transactional,
- where staged rollout / assignment is the natural operational story,
- where trusted-UI-mediated scheduling and reboot finalization matter,
- where offline bundles and mirror kits are the default delivery authority,
- and how the archive separates **bytes authenticity** from **offer/assignment/finalization** decisions.

## Decision

We define update delivery as a **profile-shaped default** and keep it threaded through `spec/examples/product.profiles.json` under the stable `updates` knob.

Cross-profile guardrail:
- signed channel metadata and rollback/freshness protections remain authoritative for bytes,
- offer/assignment/finalization decisions stay separately explainable and receipted rather than hidden in one opaque updater,
- `staged` or `applied` is never treated as `healthy` success without the profile-appropriate commit signal,
- offline carriers are only carriers; local verification and quarantine→promote remain the trust boundary,
- and weaker compatibility lanes in C must not silently redefine stricter A/B/D defaults.

### A) `fleet_host`

Default posture: `health-gated`

- Fleet hosts treat updates as policy-derived rollout operations.
- Cohorts, maintenance windows, reboot coordination, and post-boot health gates are normal rather than optional ornamentation.
- Director-like explicit assignment may exist, but it narrows delivery/offer authority; it does not replace signed channel metadata as byte authority.

### B) `workstation`

Default posture: `health-gated`

- Workstations may discover or even stage updates in the background, but apply/finalization must stay trusted-UI-visible and deferrable.
- Reboot and rollback consequences should be understandable to a non-expert user.
- Silent unattended host-generation apply/reboot is out of bounds as the workstation baseline.

### C) `general_os`

Default posture: `transactional`

- General-purpose installs keep atomic switch/rollback as the baseline update story.
- Health gates, rollout graphs, assignment services, and offline bundle lanes remain available, but they are optional Derive lanes rather than hidden prerequisites for viability.
- Central coordinators and compatibility update tools stay adapter-shaped or explicitly chosen.

### D) `appliance_factory`

Default posture: `offline-bundles`

- Factory/regulatory shapes default to approved offline bundles or mirror kits with quarantine→promote import.
- Production success should not depend on live upstream channel reachability.
- Controlled windows, retained receipts, and local approval policy are the expected update path, with online channels serving staging and preparation rather than production trust.

## Consequences

- Product profiles now treat `updates` as a stable compilation-target surface instead of a loose implementation detail.
- `tools/check_product_profiles.py` must enforce this boundary so the archive cannot drift back toward surprise workstation reboots, coordinator-dependent general-OS viability, opaque fleet updater folklore, or online-only factory delivery paths.
- Risk item 5 narrows from “what is the default strategy?” to implementation detail: exact key-rotation ergonomics, long-term source-retention policy depth, concrete mirror-kit/bundle envelopes, and local scheduling UX.

## Non-goals

- Choosing one in-tree update agent, graph protocol backend, or GUI surface.
- Freezing the exact reboot policy language or maintenance-window syntax here.
- Defining the full source-retention and archival budget for every deployment.
- Eliminating explicit compatibility adapters for classic update tooling on day 0.
