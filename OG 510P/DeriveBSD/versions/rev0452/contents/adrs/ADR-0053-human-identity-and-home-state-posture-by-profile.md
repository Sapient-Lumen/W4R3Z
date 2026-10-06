# ADR-0053: Human identity and home-state posture by profile

- **Status:** Accepted
- **Date:** 2026-03-06

## Context

DeriveBSD already has the ingredients for a good **human identity + user-state** story:
`docs/269-portable-home-areas-and-user-records.md` frames a portable, signed `home.area` + `user.record`, and `docs/270-appvm-storage-private-volatile-and-home-areas.md` keeps AppVM persistence explicit.

What the archive still lacked was the **product-shape default**.
Without that, the archive drifts into incompatible assumptions:

- A quietly grows “just give the operator a normal always-mounted home” folklore on fleet hosts,
- B forgets that whole-home mounts into general AppVMs collapse isolation,
- C cannot tell whether classic host accounts are acceptable compatibility or design failure,
- D risks mixing maintenance identities with production workload state.

We do **not** need to solve every backend, unlock source, or user-record field here.
We do need a stable, checkable answer to:

- whether portable homes are the default,
- when home state should unlock and relock,
- whether whole-home mounts into AppVMs are normal or exceptional,
- and whether production images should carry human home state at all.

## Decision

We define human identity / home-state posture as a **profile-shaped default** and thread it into `spec/examples/product.profiles.json` under a stable `home_identity` knob.

### A) `fleet_host`

Default posture: `host-operator-accounts-no-portable-home-default`

- Fleet hosts may have operator accounts for break-glass or maintenance, but portable homes are not the baseline.
- Human state is not part of ordinary workload-host posture.
- Any operator home-like state should remain login-bounded and separately governed from workload state.

### B) `workstation`

Default posture: `portable-home-preferred-login-mounted-no-whole-home-appvm-default`

- Human-facing workstations prefer a portable, encrypted home area with a bound identity record.
- Home state should unlock on user login and be able to relock/unmount on logout or explicit lock.
- General interactive AppVMs do **not** receive the whole portable home by default; sharing stays portal/file-grant shaped.
- If a whole-home mount into an AppVM exists at all, it is an explicit, leased exceptional path.

### C) `general_os`

Default posture: `host-accounts-default-portable-home-optional`

- Broad compatibility keeps classic host accounts as the default.
- Portable homes remain a first-class option for roaming/encrypted user-state workflows.
- Compatibility is allowed, but it should not silently redefine B’s tighter default.

### D) `appliance_factory`

Default posture: `no-human-homes-in-production-maintenance-identities-separate`

- Production/manufacturing images do not assume portable human home areas.
- Maintenance/operator identities are separate from production workload state.
- If human user-state exists at all, it belongs in maintenance stations or explicit servicing workflows, not the production image baseline.

## Consequences

- Product profiles now carry a stable `home_identity` default.
- The old workstation-only `portable_homes` knob is removed to reduce ambiguity; the archive should have one uniform vocabulary for this boundary.
- `tools/check_product_profiles.py` must enforce this boundary so the archive cannot silently drift back toward always-mounted homes or whole-home AppVM sharing by default.
- Open questions narrow to implementation detail: user-record schema compatibility, group/per-machine exceptions, TPM/policy-authorize unlock evolution, whole-home exceptional-lease UX, and backup/export/import semantics.

## Non-goals

- Choosing one mandatory home-storage backend for all deployments.
- Designing the full login manager/session manager stack.
- Solving every roaming, backup, or per-machine identity edge case in this ADR.
