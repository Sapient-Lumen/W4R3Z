# Remote assistance posture by profile

**Tier:** C (Optional lane)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Plan→Apply→Receipt, Registry→Diff→Gate  

DeriveBSD already has a strong *capability-lane* design for remote assistance.
What this doc decides is narrower and more important for coherence:
**what is the default remote-assistance posture for each product shape?**

This is intentionally **not** a protocol decision.
It is a product-default decision.

See also:
- ADR: `adrs/ADR-0051-remote-assistance-posture-by-profile.md`
- capability lane: `docs/291-remote-assistance-sessions-as-evidence.md`
- recordings: `docs/292-terminal-session-recording-as-evidence.md`
- consent substrate: `docs/256-consent-ux-contract.md`

## Why this needs a hard decision

Every system eventually needs support.
If the archive leaves remote assistance as “we’ll figure that out later”, real deployments grow shadow paths:

- always-on remote agents,
- ad-hoc tunnels,
- silent screen sharing,
- permanent exceptions that never land in policy,
- or unrecorded operator sessions during incidents.

That breaks all four product shapes in different ways.
So we decide the **default authority model** now, while leaving transport and implementation details open.

## Product-shape defaults

### A) Secure fleet host (`fleet_host`)

Default: `brokered-tty-console-recorded-no-gui-control`

- Fleet hosts are not a desktop-remoting surface.
- The blessed support path is brokered TTY / serial / console assistance.
- If a remote transport is needed, it should be outbound-initiated or otherwise policy-derived.
- Recording/evidence is on by default for the support path.
- General-purpose remote GUI control of the host is not part of the default product story.

### B) Secure workstation (`workstation`)

Default: `visible-user-mediated-view-or-control-with-lease`

- View-only and remote-control sessions are allowed.
- Sessions must be visible in the trusted UI with a clear indicator and immediate revoke path.
- Remote control requires secure attention before control becomes active.
- Clipboard and file transfer remain separate grants.
- Persistent remembers/restores are not ambient authority; effective authority must still land in a lease or durable policy object with revoke.

### C) General-purpose OS (`general_os`)

Default: `brokered-explicit-lease-no-ambient-agent`

- A brokered support path exists for both operator-style and desktop-ish use cases.
- The archive still prefers explicit start + lease + revoke over permanently enabled helpers.
- Legacy or developer workflows may use adapters, but they stay explicit, killable, and reviewable.

### D) Appliance factory / regulatory (`appliance_factory`)

Default: `disabled-by-default-maintenance-only-recorded`

- Production images do not expose ambient remote-support authority by default.
- Remote assistance belongs to maintenance windows, attended support stations, or dedicated support images.
- Recording and retained evidence are the default.
- Interactive prompts are not the authority model for production/evidence lanes.

## Cross-profile invariants

Regardless of profile:

- no stealth remote view/control
- no ambient permanent remote-support agent in the trusted plane
- support authority is leased, revocable, and receipted
- network transport must still respect ingress/egress posture
- file transfer/export remains a separate authority lane

## What this does *not* decide

Still open:

- exact relay/protocol choice
- session-recording detail defaults (output-only vs input+output, retention, redaction/export)
- which high-risk scopes require quorum by default
- how maintenance-window enablement is represented in product D artifacts

That work stays implementation-level.
This doc only fixes the product-default boundary so the archive can make progress without drifting.

Last updated: 2026-03-06r190
