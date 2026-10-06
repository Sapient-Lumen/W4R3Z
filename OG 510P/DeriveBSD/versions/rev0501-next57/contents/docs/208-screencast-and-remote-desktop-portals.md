# ScreenCast + RemoteDesktop portals (screen sharing + remote control) as capability grants

Screen capture and remote control are *high-power crossings*.
If they are ambient (“any app can capture the screen”), sandboxing collapses.

Modern sandboxed desktops treat these as **portal-shaped capability acquisition**:
- a broker mediates a user-visible selection prompt
- the app receives a **scoped stream handle**, not global display access

## Lessons to steal

Remote support composition: `docs/291-remote-assistance-sessions-as-evidence.md`.

Session conventions + remembered permissions: `docs/210-portal-sessions-and-permission-store.md`.

- XDG Desktop Portal **ScreenCast**: apps create a screencast session and select sources (monitor/window/virtual).  
  Reference: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.ScreenCast.html

- XDG Desktop Portal **RemoteDesktop**: apps create remote-desktop sessions with explicit device types (keyboard/pointer/touch).  
  Reference: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.RemoteDesktop.html

- libportal description: a screencast session makes monitor/window content available as a **PipeWire stream**.  
  Reference: https://libportal.org/libportal.html

- PipeWire “portal access control”: portal-mediated clients can be tagged/permissioned specially, and the portal provides the sandbox escape hatch to connect to PipeWire.  
  Reference: https://docs.pipewire.org/page_portal.html

## Model

### 1) Screen sharing is *stream authority*, not “read display memory”

A host-side `derive-screencastd` broker (name placeholder):

- prompts user to select **source(s)** (monitor/window/virtual)
- issues a **leased** `ui.screencast.grant`
- returns a stream handle (e.g., PipeWire remote FD or a DeriveBSD-native stream object)
- enforces constraints:
  - foreground requirement
  - TTL / lease
  - whether audio is included
  - whether cursor is included
  - whether “virtual monitor” is allowed
  - an always-on indicator overlay (non-spoofable)

### 2) Remote control must be explicit, granular, and *paired with input authority*

Remote control is not “screen capture plus magic”.
It is *input injection*, and should reuse the input-authority lane:

- device types must be requested explicitly (keyboard/pointer/touch)
- grants are leased, revocable, and focus-scoped
- entering trusted prompt mode (SAK) must **always** override injected input

See: `docs/207-input-authority-secure-attention-and-hid-risk.md`.

### 3) Bind capture/control to receipts (audit + policy)

For high-assurance channels, treat these as receipted events:
- “screen share started”
- “remote input injection enabled”

Receipts can feed:
- policy gates (e.g., “no screen capture on prod consoles”)
- explainability (why a tool could see/control something)

## Evidence objects

- `ui.screencast.grant` — leased authority to create a screencast session
- `ui.screencast.receipt` — record that a session started (optional policy knob)

- `ui.remotedesktop.grant` — leased authority to create a remote desktop control session
- `ui.remotedesktop.receipt` — record that control was enabled (optional policy knob)

Schemas:
- `spec/ui.screencast.grant.schema.json`, `spec/ui.screencast.receipt.schema.json`
- `spec/ui.remotedesktop.grant.schema.json`, `spec/ui.remotedesktop.receipt.schema.json`

## Integration points

- portals/powerbox: `docs/179-portals-and-powerbox.md`
- intent routing (“share screen” as an intent): `docs/199-intent-routing-and-plumbing.md`
- deterministic redaction (watermarking, metadata stripping): `docs/195-deterministic-redaction-transforms.md`
