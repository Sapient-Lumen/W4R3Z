# Input authority: secure attention + HID danger classes

If “who gets the keyboard” is ambiguous, sandboxing collapses.

Two evergreen lessons:
- **HID is power**: a domain that receives real keyboard/mouse input can often *control* or *spy on* the whole session
- **trusted path matters**: users need a way to reach a host-controlled prompt that cannot be faked by an untrusted workload

DeriveBSD should treat *input* as **capability-routed authority**.

## Lessons to steal

### 1) USB input devices are special-danger

Qubes OS is explicit: if you connect a keyboard/mouse to a VM, that VM effectively has control over the system and can sniff input (including passwords).

Reference:
- https://doc.qubes-os.org/en/latest/user/security-in-qubes/device-handling-security.html

See also:
- USB quarantine + removable media workflow: `docs/279-usb-quarantine-and-removable-media-workflow.md`
- Device grants + /dev authority: `docs/278-device-grants-and-devfs-rulesets.md`

### 2) Secure attention sequences create a trusted path

Windows historically recommends requiring **CTRL+ALT+DEL** before logon to ensure the user is talking to a trusted OS path and not a fake prompt.

References:
- Microsoft security policy note: https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/interactive-logon-do-not-require-ctrl-alt-del

## Model

### 1) Host owns raw HID; workloads receive brokered streams

- the host (dom0-equivalent) owns raw HID devices and focus state
- workloads do **not** receive raw USB HID by default
- workloads receive a leased `ui.input.stream` capability via a broker:
  - constrained to foreground/focus
  - constrained to a specific surface/window
  - optionally pointer-only (no keyboard), depending on policy

This aligns with the wider “authority as data” approach: input is routed like any other capability.

### 2) A secure attention key enters “trusted prompt mode”

Reserve a key chord as a **Secure Attention Key (SAK)** (exact chord is a platform decision).
When invoked:

- control is transferred to the host UI stack
- the host enters a visually distinctive *trusted prompt mode* (hard to spoof):
  - unique border/overlay drawn by the host
  - optional hardware indicator (LED) if available
- untrusted workloads are prevented from presenting credential UI that could confuse the user

Use cases:
- login / unlock
- privilege escalation prompts
- signing / key-use confirmation
- high-risk portal approvals

### 3) HID danger classes are explicit inputs to policy

Add a small, stable taxonomy so policy can be opinionated:
- `hid-keyboard`
- `hid-mouse`
- `hid-composite`
- `hid-gamepad`
- `hid-touch`

Default posture:
- never attach `hid-keyboard`/`hid-mouse` to untrusted device domains
- if a workload needs input, provide brokered input streams
- if a user insists on passing raw HID through (e.g., to a Windows VM), require:
  - explicit consent receipts
  - a “this VM can see everything you type” warning
  - an easy escape hatch (SAK to return to host)

This connects directly to device isolation domains (`docs/204`) and portals (`docs/179`).

## Evidence objects

- `ui.input.stream.grant` — leased input stream capability (scope/focus constraints)
- `ui.secure_attention.receipt` — host-issued evidence that SAK was invoked and what trusted action was taken
- `device.profile` — host classification of a device endpoint/controller including HID risk tags (used as policy input)

Schemas:
- `spec/ui.input.stream.grant.schema.json`
- `spec/ui.secure_attention.receipt.schema.json`
- `spec/device.profile.schema.json`

## Open questions

- best SAK chord on laptops with remapped keyboards
- how to prove “trusted prompt mode” is exclusive on multi-monitor / remote desktop
- where to draw the line between “pointer-only input” and “keyboard input” for terminal workloads

See also:
- portal consent receipts: `docs/185-portal-consent-and-audit-receipts.md`
- observability is capability-routed: `docs/192-observability-as-capability.md`
- device domains: `docs/204-device-isolation-domains.md`
- remote desktop input injection (paired with SAK): `docs/208-screencast-and-remote-desktop-portals.md`

Last updated: 2026-03-25r454
