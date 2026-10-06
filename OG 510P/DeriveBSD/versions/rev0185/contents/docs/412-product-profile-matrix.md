# Product profile matrix (A–D)

> Generated from `spec/examples/product.profiles.json`. Do not hand-edit; run `python3 tools/gen_product_profile_matrix.py --write`.

**Tier:** A (Core meta-doc)  
**Profiles:** A, B, C, D  
**Pillars:** reproducibility, isolation, supply-chain, operability

## Defaults snapshot

| Profile | Default posture (selected knobs) |
|---|---|
| A — A) Secure fleet host (`fleet_host`) | `backups=replication-lane`, `evidence=always-on`, `firmware_updates=policy-gated`, `interactive_ui=off-by-default`, `networking=policy-derived`, `platform_provenance=measured-and-receipted`, `runtime=microvm-first`, `updates=health-gated` |
| B — B) Secure workstation (`workstation`) | `backups=exports-or-replication`, `evidence=exportable`, `firmware_updates=interactive-consent`, `interactive_ui=on`, `platform_provenance=exportable`, `portable_homes=on`, `runtime=appvm-or-microvm`, `updates=health-gated` |
| C — C) General-purpose OS (`general_os`) | `backups=user-choice`, `compat=bounded-adapters`, `devshells=first-class`, `firmware_updates=user-choice`, `platform_provenance=user-choice`, `runtime=jails-first-with-microvm-lanes`, `updates=transactional` |
| D — D) Appliance factory / regulatory (`appliance_factory`) | `backups=replication-and-restore-drills`, `evidence=bundled-and-redacted`, `firmware_updates=offline-staged`, `platform_provenance=measured-and-retained`, `runtime=sealed-workload-images`, `telemetry=minimal`, `updates=offline-bundles` |

## Required invariants

### A — A) Secure fleet host (`fleet_host`)
- Atomic activation + rollback
- Receipts/evidence for privileged ops
- Remote recovery story (break-glass, logged)
- Strong supply-chain verification by default

### B — B) Secure workstation (`workstation`)
- Clear trusted UI boundary / secure attention path
- Portal-mediated file/clipboard/device flows
- Data-at-rest protection appropriate for lost-device threat model
- Explainers for 'why does this app have access?'

### C — C) General-purpose OS (`general_os`)
- Derive pipeline remains the primary interface
- Adapters remain killable and tiered
- Explainability of system state remains intact

### D — D) Appliance factory / regulatory (`appliance_factory`)
- Airgap-friendly update and provenance workflow
- Long-term rebuildability / source availability plan
- Strict admission gates and stable audit evidence exports
- Deterministic retention / evidence redaction controls

## Forbidden by default

### A — A) Secure fleet host (`fleet_host`)
- Desktop session on host
- Unreceipted mutable config
- Opaque binary update channels

### B — B) Secure workstation (`workstation`)
- Implicit ambient authority across apps
- Direct device passthrough without policy + receipts

### C — C) General-purpose OS (`general_os`)
- Forked 'classic' configuration pathways that bypass the derive pipeline

### D — D) Appliance factory / regulatory (`appliance_factory`)
- Network-dependent updates without mirror-kit fallback
- Undocumented debug backdoors

## Notes

- Profiles are compilation targets for defaults and gates; they are not forks.
- Letter aliases A–D are defined in `spec/product.profile_aliases.json` (tools normalize to canonical ids).
- Features should declare **Tier** and applicable **Profiles** in their doc metadata.
