# libei/EIS + XDG RemoteDesktop portal (future Wayland input path)

Wayland intentionally removed the universal, compositor-agnostic “inject input”
APIs that many X11 automation tools rely on (e.g. XTEST).

As a result, most practical automation stacks today use one of:

- compositor-specific protocols (e.g. a “virtual keyboard” protocol)
- uinput-based injection (e.g. dotool/ydotool), which works broadly but requires
  `/dev/uinput` permission

A longer-term cross-desktop path is emerging around **libei** (Emulated Input)
and the **XDG Desktop Portal RemoteDesktop** API.

## What the portal provides

The RemoteDesktop portal provides an API for applications to request permission
for remote control. A key method is:

- `org.freedesktop.portal.RemoteDesktop.ConnectToEIS`

This returns a file descriptor for an EIS (Emulated Input Server) connection.
Clients can then use **libei** to send keystrokes/mouse events over that fd.

Portal docs (interface v2):

- https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.RemoteDesktop.html

The design goal is:

- permission and policy are handled by the portal
- once approved, the client speaks to the compositor directly via EIS

## Where this is in practice

Support varies by desktop and portal backend:

- GNOME has been adding EIS plumbing for the portal and remote desktop stack.
- wlroots portal backends have discussed libei support, but it may not be
  universally present.
- some compositor-specific portal backends may not implement the RemoteDesktop
  interface at all.

Recent ecosystem issues to track:

- wlroots portal backend libei discussion: https://github.com/emersion/xdg-desktop-portal-wlr/issues/323
- Hyprland portal backend lacking RemoteDesktop: https://github.com/hyprwm/xdg-desktop-portal-hyprland/issues/252
- libei devices being removed on screen blanking (real client impact): https://github.com/input-leap/input-leap/issues/1699

Practical note: some environments (e.g. GNOME 48-era stacks) can surface confusing
permission prompts like “Allow remote interaction” even for local tools that inject
input via compositor pathways.

## VHK direction

VHK does not currently speak libei from Python.

However, this file exists as a roadmap because a future VHK backend could:

1. start a RemoteDesktop portal session (interactive permission prompt)
2. call `ConnectToEIS` to get an EIS fd
3. use a small helper binary (or bindings) to emit EIS input events

This would provide a compositor-approved input injection path without requiring
uinput permissions.

### Practical caveats

- Portal UX is usually interactive and may not support “permanent allow”.
- The EIS fd can be invalidated; the helper should handle reconnects.
- “Capture input” and “emulate input” are separate problems; RemoteDesktop is
  focused on emulation.
