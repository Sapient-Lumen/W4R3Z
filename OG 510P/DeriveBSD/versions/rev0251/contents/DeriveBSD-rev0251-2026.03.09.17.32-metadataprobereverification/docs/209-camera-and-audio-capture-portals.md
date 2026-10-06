# Camera + audio capture portals (AV devices) as capability grants

Camera and microphone access are *high-signal exfil channels*.
A greenfield OS should make AV capture:
- **explicit** (no ambient device nodes)
- **brokered** (user-visible consent and device choice)
- **leased and revocable** (no “forever mic”) 

## Lessons to steal

Session conventions + remembered permissions: `docs/210-portal-sessions-and-permission-store.md`.

- XDG Desktop Portal **Camera**: on-demand camera access mediated by a portal.  
  Reference: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Camera.html

- libportal notes that camera access can be mediated via PipeWire remotes (portal → PipeWire connection pattern).  
  Reference: https://libportal.org/libportal.html

- PipeWire is designed with a security model aimed at containerized applications and supports Flatpak use cases.  
  Reference: https://pipewire.org/

- Microphone/audio capture is notably *still messy* in the Linux portal ecosystem:
  - there is an open request for a microphone portal analogous to camera  
    Reference: https://github.com/flatpak/xdg-desktop-portal/issues/615
  - and an “Audio portal” discussion proposing a portal like Camera but for audio devices  
    Reference: https://github.com/flatpak/xdg-desktop-portal/issues/1129
  - Mozilla notes there is no microphone portal yet when trying to integrate with portals  
    Reference: https://bugzilla.mozilla.org/show_bug.cgi?id=1726218

DeriveBSD can bake in an audio capture portal early (while staying compatible with PipeWire-like broker patterns).

## Model

### 1) AV capture is a brokered stream grant

A host-side `derive-mediad` broker (name placeholder):

- mediates access to:
  - camera devices
  - microphone devices
- issues leased grants with constraints:
  - device selection (explicit device id or “default”)
  - purpose (e.g., video-call vs recording) as a policy input
  - TTL / revocation
  - foreground requirement
  - mandatory capture indicator

### 2) Unify the *stream transport* story

Prefer a single “media stream transport” story for:
- camera
- microphone
- screencast audio

Concrete designs can use:
- PipeWire-style remotes (FD handoff) as an interop option
- a DeriveBSD-native stream object over the ocap RPC substrate

See:
- screencast portal lane: `docs/208-screencast-and-remote-desktop-portals.md`
- object-capability RPC: `docs/183-object-capability-rpc.md`

### 3) Receipts + redaction hooks

- capture grants should be receipted for high-assurance environments
- optionally bind a redaction transform digest:
  - metadata stripping for artifacts
  - watermark requirements

See: `docs/195-deterministic-redaction-transforms.md`.

## Evidence objects

- `ui.camera.grant`, `ui.camera.receipt`
- `ui.audio.capture.grant`, `ui.audio.capture.receipt`

Schemas:
- `spec/ui.camera.grant.schema.json`, `spec/ui.camera.receipt.schema.json`
- `spec/ui.audio.capture.grant.schema.json`, `spec/ui.audio.capture.receipt.schema.json`

## Integration points

- portals/powerbox: `docs/179-portals-and-powerbox.md`
- device isolation domains (driver VMs): `docs/204-device-isolation-domains.md`
- network egress mediation (for WebRTC-style call stacks): `docs/201-network-egress-as-capability.md`
