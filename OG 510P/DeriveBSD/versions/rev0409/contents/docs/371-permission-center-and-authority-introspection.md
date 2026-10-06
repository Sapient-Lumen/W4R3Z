# Permission center + authority introspection (keep dynamic grants from turning into permanent mystery)

Portals and brokers prevent ambient authority, but they introduce a new failure mode:
**permissions become scattered, sticky, and hard to reason about**.

DeriveBSD already has the raw ingredients:
- grants and receipts (network/device/crypto/debug)
- a consent ledger (`docs/369-consent-ledgers-and-permission-review-ui.md`)
- authority graphs (`docs/366-capability-graphs-and-authority-diff-surfaces.md`)
- flow receipts (`spec/net.flow.receipt.schema.json`)
- introspection trees (Inspect-style): `docs/372-inspect-style-structured-introspection.md`

This doc proposes the “ecosystem feature” that makes those primitives usable:

> a single, queryable **permission center** that answers “who can do what, and why?”

## Prior art worth stealing

- Android “auto-reset permissions for unused apps” (permissions expire if unused):
  https://developer.android.com/about/versions/11/privacy/permissions

- Apple App Privacy Report (domain-level network transparency for apps):
  https://support.apple.com/en-us/102188

- Firefox permission manager (central store of user-granted exceptions):
  https://firefox-source-docs.mozilla.org/permissions/manager.html

- Qubes qrexec policy management (cross-domain calls are policy + files you can diff):
  https://doc.qubes-os.org/en/latest/user/advanced-topics/rpc-policy.html

## The DeriveBSD target

Two frontends to the same substrate:

- **CLI**: `derive perms …` (JSON-first, scriptable)
- **GUI**: “Permission Center” (human browsing, review, revoke)

Both should be able to answer:

- What authority does this unit/app have *right now*? (leases)
- What authority can it acquire dynamically? (portals)
- What has it actually used recently? (receipts, privacy-safe summaries)
- What changed since last week? (authority diff + consent ledger)

### A minimal data model

- **Active leases** (timeboxed by default):
  - `net.egress.grant`, `net.listen.grant`, `device.attach.grant`, debug/trace leases, crypto op leases

- **Persistent grants** (explicitly sticky):
  - file bookmarks, portal permission-store entries, policy exceptions

- **Usage evidence** (privacy-budgeted):
  - flow receipts (network domains + counts), device-use receipts, crypto op receipts

- **Justification**:
  - the consent prompt text + the requesting component identity + the policy decision record id

## UX rules (keep it from becoming a junk drawer)

1) **Everything has a TTL** by default.
   - A persistent grant must be explicitly converted from a lease.

2) **Auto-expire unused grants** is a first-class knob.
   - Borrow the Android lesson: permissions that are never used should not be eternal.

3) **Every grant is explainable**.
   - “why does X have Y?” must link to:
     - the consent receipt
     - the policy decision record (if any)
     - the authority graph edge

4) **Review is diff-first**.
   - the permission center should always have a “since last update” view.

5) **Revoke is safe and reversible**.
   - revocation should prefer:
     - lease expiry
     - indirection pointers
     - “soft fail” fallbacks (feature unavailable)

## CLI sketches

- `derive perms list --unit <id> --json`
- `derive perms diff --since 7d --json`
- `derive perms revoke <grant_id> --reason "…"`
- `derive perms expire-unused --older-than 90d --dry-run`
- `derive perms privacy-report --unit <id> --window 7d --json`

The “privacy report” output is a Derive-flavored equivalent of App Privacy Report:
- domains contacted (from flow receipts)
- sensors/devices used (from device receipts)
- exports performed (from export receipts)

## Where this plugs in

- Consent ledger: `docs/369-consent-ledgers-and-permission-review-ui.md`
- Consent UX contract: `docs/256-consent-ux-contract.md`
- Authority budgets + drift alarms: `docs/298-authority-budgets-and-permission-drift-alarms.md`
- Inspect-style introspection snapshots: `docs/372-inspect-style-structured-introspection.md`
- Network egress broker + flow receipts: `docs/281-network-egress-broker-and-consent.md`
- Device grants + devfs views: `docs/278-device-grants-and-devfs-rulesets.md`, `docs/323-devfs-views-plans-and-receipts.md`
- Export policies + receipts: `docs/251-export-policies-and-support-bundle-portal.md`

Last updated: 2026-02-27r105
