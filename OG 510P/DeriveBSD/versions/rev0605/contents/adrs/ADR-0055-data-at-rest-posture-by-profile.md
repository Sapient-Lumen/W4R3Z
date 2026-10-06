# ADR-0055: Data-at-rest posture by profile

- **Status:** Accepted
- **Date:** 2026-03-06

## Context

DeriveBSD already has the ingredients for a credible **data-at-rest** lane:
`docs/409-zfs-encryption-and-key-management.md` makes ZFS-native encryption and key-use evidence explicit,
`docs/250-breakglass-and-recovery-workflows.md` frames emergency/unattended recovery authority,
`docs/272-sealed-secrets-attested-unsealing.md` narrows TPM-sealed unlock evolution,
and `docs/463-human-identity-and-home-state-posture-by-profile.md` already fixes that workstation home data should unlock with the human rather than ambient whole-system convenience.

What the archive still lacked was the **product-shape default**.
Without that, deployments drift into incompatible assumptions:

- A quietly normalizes raw file-backed auto-unlock or image-baked key material for unattended fleets.
- B keeps a lost-device threat model on paper but still leaves daily user state unlocked at boot.
- C cannot tell whether encryption is Derive guidance or just another optional footnote.
- D risks shipping production/factory images whose unlock story depends on hidden convenience secrets instead of explicit maintenance/quorum lanes.

We do **not** need to freeze one unlock backend or one ZFS layout here.
We do need a stable, checkable answer to:

- which product shapes treat **state encryption** as the default rather than an option,
- which shapes allow unattended unlock and under what authority model,
- whether login-bounded human data is the default for workstations,
- and whether raw file/URL key locations are first-class defaults or merely compatibility adapters.

## Decision

We define data-at-rest posture as a **profile-shaped default** and thread it into `spec/examples/product.profiles.json` under the stable `data_at_rest` knob.

Cross-profile guardrail:
- ZFS-native encryption is the preferred substrate for mutable/user-secret datasets.
- Raw file-backed or direct URL-backed unlock (`keylocation=file://...` or `http(s)://...`) is **not** a first-class Derive default unlock lane. If such mechanisms exist for compatibility, they are adapter-shaped, exceptional, and receipted rather than ambient or image-baked.

### A) `fleet_host`

Default posture: `encrypted-state-attested-or-brokered-unlock`

- Fleet hosts encrypt mutable state by default.
- Unattended bring-up may use attested local unlock or brokered/break-glass recovery, but not image-baked static key files.
- Boot convenience is allowed only through explicit policy/evidence lanes.

### B) `workstation`

Default posture: `lost-device-default-login-bound-user-state`

- Workstations assume a lost/stolen-device threat model.
- Ordinary human data should unlock with the human (login/session/presence path), not silently at boot.
- Small pre-login/device-available state may exist, but it is the exception lane, not the default place for private user data.

### C) `general_os`

Default posture: `encrypted-preferred-explicit-compatibility-fallback`

- Broad compatibility keeps the archive from mandating one encryption UX for every install.
- Encryption should still be the preferred and easy path.
- Compatibility fallbacks stay explicit; they must not silently redefine workstation or factory defaults.

### D) `appliance_factory`

Default posture: `encrypted-production-state-attested-or-quorum-maintenance-unlock`

- Production/factory/regulatory shapes encrypt production state by default.
- Unattended production boot may rely on attested local policy; maintenance/recovery unlock should be explicitly authorized, receipted, and often quorum-shaped.
- Shipping static unlock files or hidden convenience secrets in product/factory images is out of bounds.

## Consequences

- Product profiles now carry a stable `data_at_rest` default.
- `tools/check_product_profiles.py` must enforce this boundary so the archive cannot silently drift back toward image-baked unlock keys, always-unlocked workstation state, or hidden production convenience secrets.
- Open questions narrow to implementation detail: exact dataset partitioning, boot-vs-state split, metadata leakage budgets, unlock evolution rules, and break-glass vs ordinary recovery UX.

## Non-goals

- Choosing one mandatory unlock backend for all profiles.
- Freezing exact ZFS dataset topology, bootloader layout, or TPM policy format in this ADR.
- Standardizing every re-key or disk migration workflow here.
