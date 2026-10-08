# Wayland support (sway, etc.)

VHK started as an **i3 + X11** automation tool, but the ecosystem around
Wayland has converged on a small set of reliable CLI building blocks. VHK uses
those when `settings.desktop_backend: wayland` (or when auto-detection sees a
Wayland session).

## Detection and overrides

Resolution order:

1. `settings.desktop_backend` in `project.yaml` (`auto|x11|wayland`)
2. `VHK_BACKEND` environment variable (`auto|x11|wayland`)
3. Heuristics: `XDG_SESSION_TYPE=wayland`, or any present `WAYLAND_DISPLAY` (even if `DISPLAY` is also set via XWayland)

## Tooling by feature

### Screenshots

- X11: `maim` (preferred) or ImageMagick `import`
- Wayland: `grim` with optional `-g "<x>,<y> <w>x<h>"` region capture

`grim` is the standard Wayland-native screenshot tool. Its region format matches
`slurp` output, making them easy to combine. Note that grim's `-g` geometry is in
*layout coordinates*, while its output image can be scaled via `-s <factor>`.
By default grim uses the *highest output scale*, which can cause captured image
pixels to be larger than the coordinate space used by input backends.

To keep automation coordinates consistent, VHK defaults to running grim with:

- `-s 1` (so one image pixel corresponds to one layout-coordinate pixel)

Override with:

- `VHK_GRIM_SCALE=auto` to omit `-s` and use grim's default behavior
- `VHK_GRIM_SCALE=<float>` to force a specific scale factor

VHK's Doctor performs a real temporary capture instead of assuming that a found
`grim` binary is automatically usable, because some compositors still lack the
screencopy protocol grim expects.

Note: `grim` (and `slurp`) are **wlroots-first**. On GNOME/Mutter and some KDE
setups, the required protocols may be missing; prefer a portal-based flow
(`xdg-desktop-portal`) or compositor-native screenshot utilities in those
environments.

#### XDG Desktop Portal (opt-in)

Wayland *intentionally* restricts silent, programmatic screen capture on many
desktops. The cross-DE mechanism intended for sandboxed apps is the
**XDG Desktop Portal** `org.freedesktop.portal.Screenshot` API.

VHK does **not** use the portal by default during automated runs (it is usually
interactive). However:

- `vhk portal-screenshot` will request a portal screenshot and print the returned
  `file://...` URI (or copy it to `--out`).
- `vhk portal-pick-color` will use the portal color-picker and print a hex color.
- You can explicitly force the screenshot backend for debugging with:

  ```bash
  VHK_SCREENSHOT_BACKEND=portal vhk doctor
  ```

Portal limitations:
- region capture is not part of the API (capture-fullscreen + crop is the usual workaround)
- the portal chooses where the screenshot is saved and returns a URI
- the first call commonly triggers a permission prompt

See the upstream portal documentation for method signatures and options.

### Region selection

- X11: `slop` (select rectangle)
- Wayland: `slurp` (select rectangle)

`slurp`'s default output format is `%x,%y %wx%h` (e.g. `10,20 300x400`).

### Clipboard

- X11: `xclip` or `xsel`
- Wayland: `wl-copy` / `wl-paste` from `wl-clipboard`

### Input

- X11: `xdotool`
- Wayland keyboard:
  - `wtype` (Wayland virtual keyboard protocol; compositor-dependent)
  - `dotool` / `dotoolc` (uinput; works on X11/Wayland/TTY; needs /dev/uinput)
  - `ydotool` (uinput; needs `ydotoold` daemon + /dev/uinput)
- Wayland mouse/pointer:
  - `dotool` / `dotoolc` (supports clicks + wheel; VHK translates pixel coords to `mouseto` 0..1 using virtual screen geometry probes)
  - `ydotool` (uinput; useful fallback, but some setups report flaky absolute movement)

Notes:

- `wtype` depends on the Wayland *virtual keyboard* protocol. Some compositors
  (notably GNOME/Mutter) do not support it, so `wtype` can fail with
  "Compositor does not support the virtual keyboard protocol".
  When VHK sees that specific failure it will fall back to uinput-based tools
  when present (preferring `dotoolc`, then `dotool`, then `ydotool`). In
  addition, VHK now prefers uinput helpers by default in GNOME-like sessions
  so users don't hit the failure path unnecessarily.
- `ydotool` is split into a client + daemon. Socket paths vary across distros
  and service layouts; VHK now tries both `$XDG_RUNTIME_DIR/.ydotool_socket` and
  `/tmp/.ydotool_socket` (or respects `YDOTOOL_SOCKET` if set).
- On Hyprland, VHK can use `hyprctl dispatch movecursor x y` for **absolute**
  pointer movement (no uinput required for the move itself). Clicking still
  needs a separate backend (`ydotool`/`dotool`).
 - On KDE Wayland, VHK can use `kdotool` (when installed) for best-effort
   cursor position and active-window metadata. `kdotool` does **not** inject
   input; it complements `dotool`/`ydotool`.

Display geometry note:

- On Wayland, “virtual screen size” is compositor-specific. VHK’s geometry
  probe now supports Hyprland (`hyprctl`), sway/i3 IPC, generic wlroots layouts
  via `wlr-randr` (when available), GNOME (`gdbus` + Mutter DisplayConfig), and
  KDE (`kscreen-doctor --outputs`). See
  `docs/DISPLAY_GEOMETRY.md` for details.
- Environment overrides:
  - `VHK_WLR_RANDR_SIZE_MODE=logical|physical` to control how `wlr-randr` scale is interpreted
  - `VHK_INPUT_BACKEND=...` to force both keyboard + pointer backends
  - `VHK_KEYBOARD_BACKEND=...` or `VHK_POINTER_BACKEND=...` for finer control
  - values: `auto|xdotool|wtype|ydotool|dotool|dotoolc|xvkbd`

Future direction:

- The Wayland ecosystem is converging on **libei/EIS** for standardized emulated
  input across compositors. VHK does not speak libei yet, but this is the most
  promising path for cross-DE input injection without compositor-specific hacks.

  See `docs/LIBEI_EIS_AND_PORTALS.md` for a roadmap-style note.
### Active window geometry (CoordMode / window-spy)

Some features (notably `CoordMode mode=window|client` and `vhk window-spy`) need
active-window geometry.

- On **i3/sway**, VHK queries the IPC tree for `rect` and `window_rect`.
- On **Hyprland**, VHK uses `hyprctl activewindow -j` for `at`/`size`.
- On **KDE (KWin)**, VHK uses `kdotool getactivewindow ...` when `kdotool` is installed.
- On **generic X11 sessions**, VHK falls back to EWMH/X11 tooling:
  - active window id via `xprop -root _NET_ACTIVE_WINDOW` (or `xdotool getactivewindow`)
  - geometry via `xdotool getwindowgeometry --shell` (or `xwininfo -id ...`)
  - best-effort client rect via `_NET_FRAME_EXTENTS` (and `_GTK_FRAME_EXTENTS` as a fallback)

On Wayland desktops outside sway/Hyprland, there is no stable cross-DE API for
window geometry. In those environments, `CoordMode mode=window|client` may fail
until a compositor-specific backend exists.

## i3 IPC on Wayland

If you're on sway, the IPC protocol is i3-compatible and the socket path is
exported in `SWAYSOCK` (and often `I3SOCK` for compatibility). VHK's socket
discovery checks both.

## Mixed XWayland sessions

On many Wayland desktops, both `WAYLAND_DISPLAY` and `DISPLAY` are present because XWayland is available for legacy apps. VHK now treats `WAYLAND_DISPLAY` as authoritative by default so helper selection does not accidentally fall back to X11-only tooling.

Recent xdotool releases have tightened this further by explicitly rejecting Wayland/XWayland sessions instead of failing mysteriously, so this bias is now the safer default. If you intentionally want X11 behavior, override with `VHK_BACKEND=x11` or `settings.desktop_backend: x11`.


## Doctor / diagnostics notes

- `vhk doctor` now surfaces `NO_AT_BRIDGE` and a best-effort AT-SPI bus probe so
  Wayland sessions do not silently lose accessibility targeting.
- the same Doctor also verifies i3/sway IPC reachability separately from session detection, so stale `I3SOCK`/`SWAYSOCK` values are easier to spot.
- `ydotool` being installed is not enough by itself; the daemon and `/dev/uinput`
  permissions still matter. The Doctor now keeps those helpers visible so future
  remediation can be more explicit.
- The emergency `x11vnc -clear_keys` recovery command is intentionally treated as
  X11-only; mixed XWayland sessions should still default to Wayland helper choice
  unless the user explicitly forces `VHK_BACKEND=x11`.
- Screenshot diagnostics now distinguish "binary exists" from "capture actually
  works" so Wayland support failures show up early instead of during the first
  image-search/OCR run.
- Portal diagnostics now probe `Screenshot`, `ScreenCast`, `RemoteDesktop`,
  `InputCapture`, and `GlobalShortcuts` separately, then summarize the result as
  a capability matrix instead of a single yes/no "Wayland supported" answer.
- Doctor also inspects `portals.conf` search results so backend routing (for
  example `gtk` vs `gnome` vs `kde`) is less opaque during troubleshooting.
- Doctor now inventories installed `.portal` backend manifests too, so it can
  distinguish "portal interface missing because no backend is installed" from
  "backend exists but its `UseIn` desktop match excludes the current session"
  and from "`portals.conf` references a backend id that is not installed".
- Host-contract and readiness packs now carry that same portal route contract
  forward, so deployment review can compare configured routing, installed
  backends, and live D-Bus interfaces without dropping back into ad-hoc host
  inspection.

### Global hotkeys (Wayland)

On Wayland, traditional X11-style global key grabs are not available. The
cross-DE approach is the **GlobalShortcuts portal**:

- Interface: `org.freedesktop.portal.GlobalShortcuts`
- Typical flow: CreateSession → BindShortcuts (interactive) → listen for
  Activated/Deactivated signals

VHK provides an experimental helper:

```bash
vhk portal-hotkeys /path/to/project --bus-event hotkey
```

Pair it with a `dispatch: true` bus watcher (see `docs/BUS_EVENTS.md`).

Reality check: portal backend support is uneven. Many wlroots setups rely on `xdg-desktop-portal-wlr`, which currently implements Screenshot/ScreenCast only, and some GNOME setups report `BindShortcuts` as unimplemented. Keep compositor-native triggers (Hyprland custom events) and bus-based hotkey daemons (sxhkd on X11) as first-class fallbacks.

The practical takeaway for VHK is that a Wayland session may have excellent screen capture and still have no generic hotkey or input-capture path. Treat each subsystem independently in project guidance and diagnostics.

## Deployment-facing Wayland truth

VHK now keeps portal-route review visible beyond `vhk doctor` and host/readiness
packs. `gen-setup-pack`, `gen-native-install-pack`, `gen-service-compose-pack`,
`gen-release-deploy-pack`, `gen-release-stage-pack`, `gen-host-rehearsal-pack`,
and `gen-host-dossier-pack` all carry a compact host/deployment-truth summary
forward when live checks are requested.

That matters on modern Wayland hosts because one desktop can simultaneously have:

- configured routing that points at a backend id
- installed `.portal` manifests that may or may not match `UseIn` for the
  current desktop
- live frontend portal interfaces that are still missing or degraded on D-Bus

Keeping those truths visible in deployment, staging, rehearsal, and support docs
is a better Linux-native posture than flattening everything back into package
lists or a generic "Wayland supported" claim.

VHK now also carries a small **target-fit** contract through native install,
release deploy/stage, rehearsal, and dossier output. That lets the repo keep
both truths in view at once: what this host can do right now, and how that host
compares with one declared flagship lane such as GNOME Wayland, KDE Wayland,
wlroots Wayland, or an X11 fallback. On Linux that distinction matters; a host
can be healthy for itself while still drifting from the lane you intend to
ship.


## Claim-proof discipline on Wayland

One more Linux-native lesson follows from all of the above: the machine you run
review commands on is not automatically valid proof for the lane you want to
ship. A healthy sway or Hyprland host can still be the wrong witness for a
GNOME/KDE portal-first claim, and a GNOME host with degraded portal routing is
not strong proof for a polished GlobalShortcuts/RemoteDesktop story either.

VHK now carries a compact current-host claim review in claim/audit surfaces so
operators can see whether the local machine is aligned, degraded, drifted, or
neutral for the target being claimed. That is a better Linux-native posture
than treating any successful local run as universal Wayland evidence.

That witness posture now also feeds `plan-project`, which now surfaces
`planner_target_claims`, `planner_claim_witness`, and current `host_truth` /
`portal_route_contract` directly in core planner output so wrong-host proof is
visible before maintainers ever touch claim YAML. It also still feeds
`gen-promotion-pack`, which adds a `current-host-proof-gate` plus
backlog/evidence entries when the current host is weak or misleading proof for
the stronger Linux lane story the repo wants to promote.

## Explicit evidence lanes on Wayland

Wayland support questions are often lane-specific rather than universal: GNOME
Wayland, KDE Wayland, sway/wlroots, Hyprland, and X11 fallback all differ in
portal routing, helper posture, and input semantics. Because of that, VHK now
lets maintainers pin one explicit reviewed lane with `--evidence-lane
<profile-id>` in planner/claim/promotion/audit flows.

That matters because a healthy wlroots host can still be weak evidence for a
GNOME Wayland portal-first story, and a GNOME host with degraded
GlobalShortcuts/RemoteDesktop routing is still weak proof for a polished KDE or
wlroots lane. The point of the new evidence-lane contract is not to create more
claims; it is to keep proof boundaries visible when Linux lanes diverge.
