# Human identity and home-state posture by profile

**Tier:** C (Optional lane)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Registry→Diff→Gate  

DeriveBSD already has a credible **portable home / user record** lane.
What this doc decides is narrower and more important for coherence:
**what is the default human identity + home-state posture for each product shape?**

This is intentionally **not** a backend choice.
It is a product-default decision.

See also:
- ADR: `adrs/ADR-0053-human-identity-and-home-state-posture-by-profile.md`
- portable homes: `docs/269-portable-home-areas-and-user-records.md`
- AppVM storage contract: `docs/270-appvm-storage-private-volatile-and-home-areas.md`
- TPM/policy unlock evolution: `docs/272-sealed-secrets-attested-unsealing.md`
- desktop stance: `docs/457-workstation-host-ui-and-appvm-boundary.md`

## Why this needs a hard decision

Every serious OS ends up answering the same uncomfortable questions:

- is the user account mainly *host config* or a portable identity object?
- when is home state mounted and unlocked?
- can general apps see the user’s whole home, or only specific exports?
- does a fleet or factory image carry human home state at all?

If the archive leaves this as “we’ll decide later,” real systems drift toward:

- always-mounted homes that admins or host-side processes can browse at rest,
- AppVMs that quietly receive the whole home because it is convenient,
- compatibility exceptions that swallow the workstation boundary,
- or production images that mix maintenance identities with product state.

So we decide the **default authority model** now, while leaving backend and receipt details open.

## Product-shape defaults

### A) Secure fleet host (`fleet_host`)

Default: `host-operator-accounts-no-portable-home-default`

- Fleet hosts may have operator accounts for break-glass or maintenance.
- Portable homes are not the normal fleet-host baseline.
- Human state should remain separately governed from workload state and login-bounded when present.

### B) Secure workstation (`workstation`)

Default: `portable-home-preferred-login-mounted-no-whole-home-appvm-default`

- Workstations prefer a portable, encrypted home area with a bound identity record.
- Home state should unlock on login and be able to relock/unmount on logout or explicit lock.
- General interactive AppVMs do **not** get the whole portable home by default.
- File/dir access should remain portal/file-grant shaped; whole-home mounts are exceptional, leased, and receipted if they exist at all.

### C) General-purpose OS (`general_os`)

Default: `host-accounts-default-portable-home-optional`

- Classic host accounts remain the compatibility/default path.
- Portable homes stay first-class for people who want roaming encrypted user state.
- Compatibility is allowed, but it should not silently redefine B’s tighter home-state boundary.

### D) Appliance factory / regulatory (`appliance_factory`)

Default: `no-human-homes-in-production-maintenance-identities-separate`

- Production/manufacturing images do not assume portable human home areas.
- Maintenance identities are separate from production workload state.
- If human user-state exists, it belongs in maintenance stations or explicit servicing workflows, not the production-image default.

## Cross-profile invariants

Regardless of profile:

- human identity is a governed object, not just an ambient side effect of host `/etc/passwd`
- unlocked home state should be bounded to a session, login, or explicit approval rather than “everything mounted forever”
- whole-home sharing into less-trusted app compartments is exceptional, not the baseline
- attach/unlock/lock/export operations should be receipted
- compatibility paths may exist, but they stay explicit and reviewable

## What this does *not* decide

Still open:

- the canonical `user.record` schema vs adapter surface
- exact login/unlock manager integration
- TPM/policy-authorize defaults for home unlock evolution
- how group membership and per-machine exceptions compose with portability
- how whole-home exceptional leases, project mounts, and backup/export semantics should look in detail

That work stays implementation-level.
This doc only fixes the product-default boundary so the archive can keep converging without drifting.

## Design cue from current systems

Two current-system lessons matter here:

- systemd’s Home Directories model treats a human account as a portable home object that carries both user data and a signed user record, and mounts it when active rather than assuming a permanently ambient home.
- Android’s file-based encryption model explicitly separates credential-encrypted storage from device-encrypted storage and says files should live in credential-encrypted storage whenever possible, which is a strong cue that ordinary human data should unlock with the human rather than at boot.

DeriveBSD should steal the lesson, not the Linux/Android plumbing.

Last updated: 2026-03-06r192
