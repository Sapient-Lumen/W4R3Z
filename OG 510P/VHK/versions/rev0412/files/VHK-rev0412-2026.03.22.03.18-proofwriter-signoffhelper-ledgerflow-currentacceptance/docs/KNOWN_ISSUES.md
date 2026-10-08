# Known issues and platform caveats

VHK targets i3/X11 first, but includes best-effort sway/Wayland helpers.
On Wayland, *global* input automation and screen capture are constrained by
compositor security choices. This document collects practical caveats that
regularly show up when building a desktop macro runner.

## Wayland input injection is intentionally constrained

Wayland generally does **not** expose the same global "send keys/mouse anywhere"
surface that X11 tooling like `xdotool` relies on. This means:

- some workflows require compositor-specific helpers
- some key combinations may not be deliverable to all clients
- background / unfocused automation is far less reliable

If you are doing serious automation on Wayland, plan to:

- prefer window-manager / compositor APIs where possible (sway IPC, etc.)
- treat input injection tooling as "best-effort" and test on your target compositor

References:

- ArchWiki: Wayland security + limitations: https://wiki.archlinux.org/title/Wayland

## RemoteDesktop portal / libei is promising but still uneven

The cross-desktop “approved” direction for remote control on Wayland is the
XDG Desktop Portal **RemoteDesktop** API + **libei/EIS**.

However, in practice:

- Some portal backends do not implement RemoteDesktop at all (e.g. Hyprland portal backends have tracked this gap).
- Even when implemented, session lifetimes and permission UX can be surprising.
- Clients have reported EIS devices being removed on screen blanking and needing reconnect logic.

References:

- Portal interface docs: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.RemoteDesktop.html
- Hyprland portal backend issue: https://github.com/hyprwm/xdg-desktop-portal-hyprland/issues/252
- wlroots portal libei discussion: https://github.com/emersion/xdg-desktop-portal-wlr/issues/323
- input-leap EIS device removal report: https://github.com/input-leap/input-leap/issues/1699
- GNOME 48-era automation discussion (local tools prompting “remote interaction”): https://www.semicomplete.com/blog/xdotool-and-exploring-wayland-fragmentation/

## `ydotool` requires `/dev/uinput` access

VHK can use `ydotool` as a Wayland pointer backend. `ydotoold` typically needs
access to `/dev/uinput`, which often implies **root permissions** or carefully
configured device permissions.

Common failure modes:

- `ydotoold` started as root creates a socket only accessible to root
- distro packages may ship a *user* service, but `/dev/uinput` still requires
  elevated permissions

Mitigations (distro-dependent):

- run `ydotoold` as a system service and set the socket permissions/group
- configure udev rules so members of a dedicated group can access `/dev/uinput`
- some distros load the `uinput` kernel module lazily; if `/dev/uinput` never appears, add a modules-load entry (e.g. `/etc/modules-load.d/uinput.conf`)
- recent `systemd-udevd` versions may ignore udev rules referencing a *non-system* group; ensure your `uinput` group is a system group (gid < 1000) if you use GROUP="uinput"
- this became more visible with newer systemd releases (e.g. systemd **258**) where udev may log `Group '...' is not a system group, ignoring` and skip applying your GROUP/OWNER rules
- on some distros `/dev/uinput` is created *lazily* when the `uinput` module loads; if permissions are set by a udev rule, you may need to ensure the module loads early (e.g. `/etc/modules-load.d/uinput.conf`) to avoid a circular permission problem

Avoid "quick fixes" like setting the ydotool binary `setuid root` unless you
fully understand the security implications.

References:

- ydotool daemon/service/socket pain points: https://bugzilla.redhat.com/show_bug.cgi?id=2250692
- ydotool runtime notes + systemd discussions: https://github.com/ReimuNotMoe/ydotool/issues/42
- Arch Linux bug: ydotool uinput permission errors (FS#79391): https://bugs.archlinux.org/task/79391
- ydotool issue: socket permissions too restricted (#73): https://github.com/ReimuNotMoe/ydotool/issues/73
- systemd 258 udev group policy discussion (Arch forum): https://bbs.archlinux.org/viewtopic.php?id=308380
- systemd issue: udev ignores non-system users/groups in rules (#39056): https://github.com/systemd/systemd/issues/39056


## `ydotool mousemove --absolute` can be buggy (multi-monitor + scaling)

Several users have reported that `ydotool mousemove --absolute X Y` can behave
unexpectedly depending on compositor + monitor configuration:

- Some setups appear to ignore the coordinates and always jump to the upper-left.
- Others report a "half-resolution" effect where (10,10) becomes (20,20).

VHK ships a pragmatic workaround by default:

- For absolute moves, it first does `mousemove --absolute 0 0`, then moves
  **relatively** by (X,Y). This mirrors workarounds used by other automation
  scripts.
- If your cursor movement is scaled, set `VHK_YDOTOOL_PIXEL_SCALE` (eg `0.5`
  when the cursor moves twice as far).
- If your setup has a working absolute mode and you want to force it, set
  `VHK_YDOTOOL_ABSOLUTE_METHOD=native`.

References:

- ydotool issue: absolute mode always goes to upper-left (#250): https://github.com/ReimuNotMoe/ydotool/issues/250
- ydotool issue: half-resolution / double movement (#158): https://github.com/ReimuNotMoe/ydotool/issues/158
- TotoBotKey notes (absolute workaround + scaling + multi-monitor caveats): https://pypi.org/project/TotoBotKey/


## `dotool` is a practical uinput alternative (especially on GNOME)

`dotool` is another uinput-based injector that works in X11/Wayland/TTY.
It reads commands from stdin. For hotkey-driven automation, `dotoold` + `dotoolc`
keeps virtual devices alive to avoid a per-invocation startup delay.

Notes:

- Like ydotool, dotool needs `/dev/uinput` permissions.
- For long-running holds (keydown/keyup, click-and-drag), prefer the daemon/client
  mode (`dotoold` + `dotoolc`).
- VHK can generate a starter user service with `vhk gen-dotoold-service`.
## `keyd` command actions run as the keyd service user (often root)

If you export hotkeys to `keyd` using `vhk gen-keyd-config`, remember that keyd
typically runs as **root**. Its `command(...)` action inherits root's environment,
which may not have access to user-session services (Wayland portals,
notification daemons, etc.).

Mitigation patterns:

- use a wrapper script that re-enters your user session environment
- use `vhk gen-keyd-config --command-prefix ...` to inject that wrapper/prefix

See docs/KEYD.md.

## `wtype` can be compositor + XWayland sensitive

VHK can use `wtype` for Wayland keyboard injection. Some compositors have had
regressions or limitations where `wtype` works for native Wayland clients but
not for XWayland apps (or vice versa).

If typing appears to do nothing:

- confirm the target window is focused
- confirm your compositor supports virtual keyboards the way `wtype` expects
- test the same command on both a Wayland-native app and an XWayland app

If `wtype` fails with `Compositor does not support the virtual keyboard protocol`,
VHK will automatically fall back to `ydotool` when present (Wayland), but note
that `ydotool key` operates on **Linux keycodes** rather than symbolic names.

References:

- Example compositor regression affecting XWayland: https://github.com/labwc/labwc/issues/1796
- AskUbuntu discussion (GNOME/Mutter lacks virtual-keyboard): https://askubuntu.com/questions/1524311/is-there-wtype-like-tool-that-works-with-gnome-on-wayland
- Unix.SE report (GNOME 48 / libei note): https://unix.stackexchange.com/questions/800680/after-upgrading-to-debian-13-gnome-shell-48-4-most-wayland-automation-and-scree

## Screenshot and region selection toolchains vary

## GNOME/KDE: "wlroots" tools may not work

Many Wayland helper tools in the ecosystem assume **wlroots** protocols (for example:
- screen capture via `wlr-screencopy-unstable-v1` (used by `grim`)
- region overlays via `zwlr_layer_shell_v1` (used by `slurp`)
- input via the `virtual-keyboard` protocol (used by `wtype`)

On compositors that do not expose those protocols (notably GNOME/Mutter, and some KDE setups),
you may see errors like:
- `compositor doesn't support wlr-screencopy-unstable-v1` (screenshots)
- `compositor doesn't support zwlr_layer_shell_v1` (region selection)
- `Compositor does not support the virtual keyboard protocol` (typing)

Mitigations:
- prefer compositor-native tooling (e.g. GNOME/KDE screenshot utilities) or a **portal-based** flow via `xdg-desktop-portal` when available
- treat global input and capture on Wayland as best-effort; test on your target desktop environment

References:
- wtype protocol support issue: https://github.com/atx/wtype/issues/45
- AskUbuntu discussion of Mutter + wtype: https://askubuntu.com/questions/1524311/is-there-wtype-like-tool-that-works-with-gnome-on-wayland
- Example report: grim/slurp/wtype failures on GNOME: https://unix.stackexchange.com/questions/800680/after-upgrading-to-debian-13-gnome-shell-48-4-most-wayland-automation-and-scree
- ArchWiki: screen capture tooling + portals: https://wiki.archlinux.org/title/Screen_capture

### New: best-effort non-wlroots screenshot helpers

VHK's default Wayland screenshot backend is still **grim** (wlroots).

However, on desktops where `grim` cannot work (e.g. GNOME/Mutter without
`wlr-screencopy-unstable-v1`), you may have better luck with desktop-native
helpers:

- **KDE Plasma:** `spectacle --background --fullscreen --output out.png`
  (and interactive selection via `--region`).
- **GNOME:** `gnome-screenshot -f out.png` (and interactive selection via
  `--area`). Note: some GNOME installs no longer ship `gnome-screenshot` by
  default; you may need to install it explicitly.

VHK now uses these tools as a **best-effort fallback** for full-screen capture
when running on Wayland and `grim` is not available, and also uses them for
interactive asset capture (`vhk capture-needle`, `vhk capture-baseline`) when
`slurp`/`slop` are unavailable.

References:
- gnome-screenshot options (`--area`, `-f`): https://man.archlinux.org/man/extra/gnome-screenshot/gnome-screenshot.1.en
- spectacle background mode + output flags: https://manpages.ubuntu.com/manpages/jammy/man1/spectacle.1.html
- Why portals exist for screenshots on Wayland: https://github.com/python-pillow/Pillow/issues/6392
- XDG Desktop Portal overview: https://wiki.archlinux.org/title/XDG_Desktop_Portal


VHK prefers:

- screenshots: `grim` (Wayland), `maim`/`scrot`/ImageMagick fallbacks (X11)
- region selection: `slurp` (Wayland), `slop` (X11)

If screen capture fails on Wayland:

- verify your compositor supports the wlroots `screencopy` protocol (`grim`)
- consider a portal-based flow (`xdg-desktop-portal`) when you need desktop-wide
  capture under stricter compositors

### Portal troubleshooting: "No such interface org.freedesktop.portal.Screenshot"

If you attempt portal-based screenshotting (e.g. via `vhk portal-screenshot`) and
see errors like:

- `No such interface "org.freedesktop.portal.Screenshot" on object at path /org/freedesktop/portal/desktop`

it usually means your active portal backend does not implement the Screenshot
interface. This can happen if:

- you have `xdg-desktop-portal` installed but no matching backend (gtk/kde/wlr)
- your backend is present but missing the Screenshot portal in that release
- `portals.conf` points to a backend that doesn't provide Screenshot

Mitigations:

- Ensure you have a backend that matches your desktop (e.g. `xdg-desktop-portal-gtk`
  for many GTK-based desktops, `xdg-desktop-portal-kde` for Plasma, or
  `xdg-desktop-portal-wlr` for wlroots).
- On some systems you may need to configure or override `portals.conf` to select
  the correct backend for your session.

References:

- ArchWiki overview + backend selection notes: https://wiki.archlinux.org/title/XDG_Desktop_Portal
- Example wlroots backend issue report: https://github.com/emersion/xdg-desktop-portal-wlr/issues/246

References:

- ArchWiki: screen capture tooling examples (grim/slurp, etc.): https://wiki.archlinux.org/title/Screen_capture

## sway socket discovery in non-interactive contexts

For sway, the socket path is normally in `SWAYSOCK` (and sometimes `I3SOCK` for
compatibility). In scripts started outside the graphical session (systemd/cron),
those environment variables may be missing.

VHK attempts multiple discovery paths, but long-running background jobs should
explicitly pass through a correct `SWAYSOCK` when possible.

References:

- sway IPC man page (SWAYSOCK/I3SOCK and `sway --get-socketpath`): https://man.archlinux.org/man/sway-ipc.7.en
- Historical issue: `--get-socketpath` behavior when `SWAYSOCK` is unset: https://github.com/swaywm/sway/issues/2639

## Hyprland: comma syntax and JSON probing

Hyprland binds are **comma-separated** and *trailing commas matter*. A stray comma
can become part of the argument (e.g. `firefox,`), and the bind will silently fail.

For active-window checks and scripting, `hyprctl` supports JSON output via the
`-j` flag (for example: `hyprctl -j activewindow`).

For event-driven automation (focus/workspace watchers), Hyprland exposes a
separate **socket2** event stream at:

- `$XDG_RUNTIME_DIR/hypr/$HYPRLAND_INSTANCE_SIGNATURE/.socket2.sock`

The stream is newline-delimited and uses the form `EVENT>>DATA\n`.

Note: Hyprland documents that its control socket (`.socket.sock`) is evaluated
synchronously and warns that unclosed connections can freeze Hyprland until a
timeout—so prefer short-lived control connections and use socket2 for long-lived
event listeners.

References:

- Hyprland wiki: binds comma syntax and release flag: https://wiki.hypr.land/Configuring/Binds/
- Hyprland wiki: hyprctl flags (`-j` JSON output): https://wiki.hypr.land/Configuring/Using-hyprctl/
- Hyprland wiki: IPC sockets + socket2 event format: https://wiki.hypr.land/IPC/

## systemd user services and WM sessions

### graphical-session.target may not activate

Some i3/sway setups start the compositor outside systemd user session targets.
In those cases, `graphical-session.target` may remain inactive, and units that
use `WantedBy=graphical-session.target` will not start.

Workarounds:
- install under `default.target` (VHK’s `gen-systemd-watcher` defaults to this)
- or add proper systemd integration for your session (display manager / wrapper)

### Missing environment (WAYLAND_DISPLAY / DISPLAY)

If a user service runs before the session’s environment variables are imported,
it might not see `DISPLAY`/`WAYLAND_DISPLAY`/`XDG_RUNTIME_DIR`.

Depending on your session, you may need to call:

```bash
systemctl --user import-environment DISPLAY WAYLAND_DISPLAY XDG_RUNTIME_DIR
```

near the end of your WM startup.

## X11: window geometry vs decorations (CoordMode window/client)

On X11, tools disagree on whether reported window geometry includes decorations
(titlebar, borders) or invisible "shadows"/padding.

VHK's X11 active-window geometry fallback uses:

- `xdotool getwindowgeometry --shell` (or `xwininfo`) for a best-effort outer rect
- `_NET_FRAME_EXTENTS` when available to approximate the client/content rectangle
- `_GTK_FRAME_EXTENTS` as a secondary fallback on some GTK environments

If your `CoordMode mode=client` clicks appear offset:

- run `vhk window-spy` and compare `geometry.rect` vs `geometry.client`
- verify `_NET_FRAME_EXTENTS` exists: `xprop -id <win> _NET_FRAME_EXTENTS`
- if the numbers look wrong, treat client-rect translation as best-effort and
  prefer visual targeting (ImageSearch/PixelSearch) over window-relative clicks

References:

- xdotool `getwindowgeometry` docs: https://man.archlinux.org/man/xdotool.1.en
- _NET_FRAME_EXTENTS definition: https://man.archlinux.org/man/extra/perl-x11-protocol-other/X11%3A%3AProtocol%3A%3AWM.3pm.en
- xdotool geometry mismatch report: https://github.com/jordansissel/xdotool/issues/176
- _GTK_FRAME_EXTENTS explanation: https://erwin.co/what-are-_gtk_frame_extents-and-how-does-gnome-window-sizing-work/
