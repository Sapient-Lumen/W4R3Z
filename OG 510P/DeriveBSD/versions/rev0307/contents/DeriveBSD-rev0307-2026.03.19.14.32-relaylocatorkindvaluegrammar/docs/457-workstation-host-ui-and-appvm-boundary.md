# Workstation host UI and AppVM boundary

**Tier:** B (Cross-cutting product-shape decision)
**Profiles:** B
**Pillars:** isolation, operability
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace

Profile **B** only stays coherent if the archive answers one uncomfortable question clearly:

> does the workstation host run general apps directly, or does it remain a trusted UI/control plane while apps live in compartments?

This doc makes the smallest durable decision that keeps **B** viable without weakening **A** or **D**.

## Decision (v0 posture)

For profile **B**:

- the **host** is the trusted UI and broker control plane,
- general interactive apps are **AppVM-first**,
- and host↔app sharing is **portal-mediated and receipted**.

This is an accepted boundary, not a sketch. See `adrs/ADR-0047-workstation-host-ui-and-appvm-boundary.md`.

## What the host is allowed to be

The host may run a deliberately small trusted set:

- compositor / trusted shell / window-origin markers
- secure-attention / unlock / approval surfaces
- portal brokers and session managers
- settings / updates / recovery / support tooling
- device, network, identity, and secret mediation services

These are host responsibilities because they define the trust boundary or own privileged host state.

## What the host is **not** by default

The host is **not** the default execution surface for arbitrary user-facing apps such as:

- browsers
- mail/chat clients
- office/document viewers
- media players
- general developer GUI tools

Those should execute inside derived AppVMs and use portals/brokers for access.

This avoids the common failure mode where the system has nice isolation primitives on paper, but daily life happens on the host “for convenience.”

## Why AppVM-first is the right default for B

This boundary keeps the product shapes coherent:

- **A (fleet host):** keeps a small control-plane threat model.
- **B (workstation):** gets real per-app isolation without inventing ad-hoc file/device sharing.
- **C (general OS):** may still offer broader host execution via bounded adapters, but that is not the workstation default.
- **D (appliance/regulatory):** avoids inheriting host-side desktop sprawl.

The safe path becomes the normal path: app isolation first, host mediation second.

## Required crossing rules

### Files and data movement

Use portals/brokers for:

- open/save/import/export
- clipboard and drag&drop
- printing
- screenshots / screencast / remote desktop
- camera / microphone / location

The host should hand apps narrowed handles/streams/tokens, not ambient namespaces. clipboard/file-transfer broker UX should make the ordinary workstation floor explicit: no ambient shared clipboard, explicit export/import, and future bounded drag/drop only if it stays reviewable rather than becoming another ambient shared state path. URI opening should likewise stay compartment-preserving: `http` / `https` goes to a designated browsing compartment, `mailto` goes to a designated communications compartment, and `file://` does not bypass explicit file authority lanes. The chooser/default-app layer for that routing should stay on trusted host-managed role slots instead of arbitrary handler discovery or first-open default rewrites from untrusted context, the remembered role/default state for those slots should live in typed `intent.role.binding` objects rather than package-manager or desktop-entry folklore, trusted settings changes to that state should review through `intent.role.binding.diff` instead of ad-hoc settings deltas, those remembered-role mutations should emit `intent.role.binding.event` so the event journal/support bundles can answer when the change happened, and the ordinary interactive workstation lane should prove approval through the constrained `intent.role.binding` consent profiles instead of treating trusted settings UI as ambient write authority. When the same remembered-role family is mutated non-interactively by reconcile/import/admin policy, the durable event should join back to `policy.decision` through `policy_decision_digest` instead of pretending a workstation prompt happened. When that non-interactive path specifically came from support/import/recovery, the same event should also carry `import_receipt_digest` so the exact typed import receipt stays queryable. Across both lanes, the actual apply rule is compare-and-swap against the current binding digest: reviewed diffs that go stale must leave `write-denied` evidence with `reason_code = precondition-failed` and `observed_binding` instead of silently rebasing.

See: `docs/179-portals-and-powerbox.md`, `docs/205-data-transfer-portals-clipboard-and-dnd.md`, `docs/208-screencast-and-remote-desktop-portals.md`, `docs/538-workstation-cross-domain-datatransfer-floor.md`, `docs/539-workstation-intent-routed-uri-opening-floor.md`, `docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md`, `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md`, `docs/542-role-binding-diff-as-review-surface.md`, `docs/544-role-binding-consent-lane-for-interactive-workstation-mutations.md`, `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`, `docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md`, `docs/547-role-binding-support-import-join-via-content-import-receipt.md`, `docs/548-role-binding-authority-lanes-not-invocation-surfaces.md`.

### Input and trusted prompts

The host owns raw HID, focus, and the secure-attention path.
AppVMs should receive brokered input streams, not raw keyboard/mouse devices by default.
High-risk prompts (unlock, signing, consent, elevation) must route through a host-controlled trusted path.

See: `docs/207-input-authority-secure-attention-and-hid-risk.md`.

### Devices

Direct device passthrough is exceptional, not normal workstation plumbing.
USB and removable-media flows should prefer quarantine/device domains and typed grants/receipts over ambient `/dev` exposure.

See: `docs/204-device-isolation-domains.md`, `docs/278-device-grants-and-devfs-rulesets.md`, `docs/279-usb-quarantine-and-removable-media-workflow.md`.

### Display composition and acceleration

The trusted host should own composition, window-origin markers, focus policy, and trusted prompts.
AppVMs should cross into that host-controlled display plane through remoted GUI rather than joining a shared host display server.
`docs/537-workstation-remoted-session-surface-boundary.md` now fixes the baseline as a **remoted session surface** first; seamless host-native per-window integration is intentionally deferred.
The baseline accepts software-rendered or simple 2D guest output as acceptable workstation behavior; raw host X11/DRM/render-node access and direct guest GPU passthrough are not.
Using small-role or single-app AppVMs is the preferred ergonomics answer at this stage.

See: `docs/536-workstation-display-composition-and-gpu-boundary.md`, `docs/537-workstation-remoted-session-surface-boundary.md`.

## What remains intentionally undecided

This boundary is crisp, but it is **not** a complete desktop implementation plan.
Still-open implementation questions include:

- the exact remoting transport and damage/copy model for the session surface,
- audio/video backend details,
- IME/accessibility behavior across the boundary,
- whether a future bounded accelerated lane is worth the complexity,
- whether a future seamless per-window lane is worth standardizing,
- whether any role vocabulary beyond `browsing` / `communications` is worth standardizing,
- and whether some tightly bounded host-side developer/admin tools deserve an adapter lane.

Those are future RFC/ADR topics.

## Product-profile wiring

Profile **B** should summarize this boundary in a small, stable way:

- `runtime=appvm-first-with-host-ui-control-plane`
- forbidden by default: host execution of general-purpose apps outside the trusted host UI / broker set

This is intentionally **not** a second policy language.
It is a compact compilation-target default that keeps reviews, docs, and future tooling aligned.

## Related docs

- `docs/268-desktop-appvms-and-portalized-apps.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/411-product-profiles-as-compilation-target.md`
- `docs/412-product-profile-matrix.md`
- `docs/179-portals-and-powerbox.md`
- `docs/207-input-authority-secure-attention-and-hid-risk.md`
- `docs/536-workstation-display-composition-and-gpu-boundary.md`

Last updated: 2026-03-18r278
