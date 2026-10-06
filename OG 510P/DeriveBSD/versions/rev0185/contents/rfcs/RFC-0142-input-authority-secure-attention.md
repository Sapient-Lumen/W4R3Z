# RFC-0142: Input authority (secure attention + HID risk classes)

Status: **Draft**  
Last updated: 2026-02-24

## Problem

If untrusted workloads can receive raw keyboard/mouse, they can:
- capture passwords and secrets
- inject input to control other workloads

Users also need a **trusted path** to enter credentials and confirm sensitive actions.

## Proposal

Add an optional input-authority lane:

- host retains exclusive ownership of raw HID by default
- workloads receive brokered, leased input streams (focus/surface constrained)
- reserve a Secure Attention Key (SAK) to enter host-controlled “trusted prompt mode”
- introduce a small HID danger-class taxonomy that policy can treat as high-risk

## Spec objects

- `ui.input.stream.grant`
- `ui.secure_attention.receipt`
- `device.profile` (device classification evidence; used as policy input)

See: `docs/207-input-authority-secure-attention-and-hid-risk.md`.

## Prior art

- Qubes warns that connecting USB input devices to a VM gives that VM effective control and allows input sniffing.
  https://doc.qubes-os.org/en/latest/user/security-in-qubes/device-handling-security.html

- Windows secure logon recommends CTRL+ALT+DEL for a trusted path.
  https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/interactive-logon-do-not-require-ctrl-alt-del

## Open questions

- best SAK chord across different keyboard layouts and remote consoles
- how to represent focus constraints for non-GUI/TTY workflows
- UX for “pass raw HID through to a VM” with honest warnings and escape hatches
