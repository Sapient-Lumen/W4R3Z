# Remote assistance sessions as evidence (screen share + control without backdoors)

Remote support is inevitable.
If the OS doesn’t provide a blessed path, people invent shadow paths (permanent agents, ad-hoc SSH tunnels, “just install this remote tool”),
and the security posture collapses.

DeriveBSD should treat remote assistance as a **high-power capability lane**:
scoped, timeboxed, visible, revocable, and recorded as evidence.

This doc defines the lane itself.
The product-shape default for A–D now lives in `docs/461-remote-assistance-posture-by-profile.md`.

## Goals

- **No stealth**: remote view/control must be user-visible (indicator) and consent-gated.
- **Scoped authority**: “view only” vs “control keyboard/mouse” vs “file transfer” are separate scopes.
- **Leased + revocable**: assistance is a timeboxed lease that can be revoked immediately.
- **Prefer outbound**: where possible, sessions should be established as *user-initiated outbound connections* (avoid opening inbound listeners).
- **Bundle-friendly**: a remote session yields a single typed evidence object (`support.session`) that points at receipts, artifacts, and exports.

## Model

### 1) A support broker owns the dangerous pieces

A host component (`derive-supportd`) acts like a portal/broker:

- creates a `portal.session`
- requests `consent.request` (and optionally quorum approvals for high-risk scopes)
- issues scoped grants (ScreenCast / RemoteDesktop / data-transfer) and records receipts
- optionally enables **terminal session recording** for the duration (see `docs/292-terminal-session-recording-as-evidence.md`)
- registers leases with the lease registry so global revoke works (`docs/249-lease-registry-and-cross-lane-revocation.md`)

### 2) Capability surfaces used (existing lanes)

Remote assistance should be composed from existing, audited lanes:

- Screen sharing: `ui.screencast.grant` + `ui.screencast.receipt` (`docs/208-screencast-and-remote-desktop-portals.md`)
- Remote control: `ui.remotedesktop.grant` + `ui.remotedesktop.receipt` (same doc)
- Clipboard / file transfer: `ui.datatransfer.grant` + `ui.datatransfer.receipt` (`docs/205-data-transfer-portals-clipboard-and-dnd.md`)
- Sharing artifacts out of the system: `export.policy` + `export.receipt` (`docs/251-export-policies-and-support-bundle-portal.md`)
- Networking is never ambient: if a helper connection is needed, it should flow through the inbound/outbound broker lanes (`docs/281-network-egress-broker-and-consent.md`, `docs/286-inbound-listen-broker-and-firewall-leases.md`). If support needs a temporary relay-backed service handoff, it now also compiles to a support-peer publish session with `authority.trigger = support-session` and `authority.support_session_digest` rather than a freestanding support URL.

### 3) “Secure attention” for taking control

For “control keyboard/mouse”, DeriveBSD should require a secure-attention transition before control becomes active
(so malware cannot silently hand your session to a remote party).

See: `docs/207-input-authority-secure-attention-and-hid-risk.md`, `spec/ui.secure_attention.receipt.schema.json`.

## Evidence

A remote assistance session should produce:

- `support.session`: the session envelope (participants, scope, time bounds, and pointers to other evidence)
- consent receipts (and optionally quorum approvals)
- portal/session records
- UI grants/receipts and any network leases
- optional recordings (TTY + screencast) and their redaction/export receipts

This makes it easy to include remote assistance in incident bundles (`docs/216-incident-snapshots-and-support-bundles.md`)
and to prove what happened during an assistance event.

See: `spec/support.session.schema.json`, `spec/examples/support.session.json`.

## Non-goals

- We are not building a SaaS remote support product.
- We do not aim to tunnel arbitrary inbound connectivity around the networking brokers.

Last updated: 2026-03-19r299
