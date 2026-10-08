# Display geometry on Wayland

Automation often needs a reliable answer to:

> “What is the size of the virtual desktop coordinate space?”

On X11, this is straightforward (`xrandr --query`). On Wayland, there is no
single cross-DE API, and some automation backends accept *normalized* pointer
coordinates (e.g. dotool’s `mouseto` uses 0..1).

VHK therefore implements **best-effort probes** for screen geometry.

## What VHK uses (preference order)

1. **Hyprland**: `hyprctl -j monitors` → union of monitor rects.
2. **sway/i3**: i3 IPC `get_outputs` → union of active output rects.
3. **wlroots compositors (generic)**: `wlr-randr --json` (or plain `wlr-randr`)
   → union of per-output `Position:` + current-mode sizes.
4. **GNOME/Mutter**: DBus `org.gnome.Mutter.DisplayConfig.GetCurrentState`
   (queried via `gdbus`). The interface describes physical monitors, their
   available modes (including an `is-current` flag), and logical monitor layout
   (x/y, scale, transform).
5. **KDE Plasma**: `kscreen-doctor --outputs` → parse `Geometry: x,y WxH` lines.
   This is what many KDE users rely on for Wayland display scripting.

If none of these succeed, VHK will raise a helpful error telling you which tool
to install for your environment.


## wlroots details (wlr-randr)

On wlroots-based compositors (sway, river, labwc, wayfire, etc.), `wlr-randr`
can query the output layout via the *wlr-output-management* protocol.

Newer releases support JSON output:

```bash
wlr-randr --json
```

Older releases print a human-readable format containing `Enabled:`, `Modes:`,
`Position:`, `Transform:`, and `Scale:` fields. VHK parses both.

### Scale interpretation

VHK defaults to interpreting the **virtual desktop** in *logical/layout*
coordinates by dividing the current mode dimensions by the output scale.

If your compositor/tooling reports sizes in raw pixel units, override with:

```bash
VHK_WLR_RANDR_SIZE_MODE=physical
```

### Services / cron caveat

`wlr-randr` needs a valid Wayland environment (notably `XDG_RUNTIME_DIR` and a
Wayland display). If you run VHK or wlr-randr from a system service or cron,
prefer **systemd user services** or explicitly export the required variables.

## GNOME details (Mutter DisplayConfig)

The DisplayConfig interface returns:

- **Monitors**: `(connector, vendor, product, serial)` plus a list of **modes**
  where each mode includes `width`, `height`, and properties like `is-current`.
- **Logical monitors**: `x`, `y`, `scale`, `transform`, and the monitor IDs that
  are part of that logical group.

VHK picks the `is-current` mode to get physical dimensions, then applies the
logical monitor scale (and transform rotation) to compute a bounding box.

To inspect this yourself:

```bash
gdbus call --session \
  --dest org.gnome.Mutter.DisplayConfig \
  --object-path /org/gnome/Mutter/DisplayConfig \
  --method org.gnome.Mutter.DisplayConfig.GetCurrentState
```

Example output is a large one-liner, but it contains mode tuples like
`('1360x768@59.960', 1360, 768, ..., {'is-current': <true>})` and logical monitor
tuples like `(0, 0, 1.0, uint32 0, true, [('eDP-1-1', ...)], @a{sv} {})`.

## KDE details (kscreen-doctor)

On Plasma, `kscreen-doctor --outputs` prints a readable summary that includes
per-output geometry lines (e.g. `Geometry: 0,0 2560x1440`).

```bash
kscreen-doctor --outputs
```

VHK parses the geometry lines and computes the union rectangle.

## Caveat: scaling vs screenshot pixels

Wayland compositors may present a “logical” coordinate space that differs from
physical pixel dimensions when fractional scaling is enabled.

VHK’s vision steps operate on screenshot pixels, while some input injection paths
may act in logical coordinates. In practice, VHK’s geometry probe uses the
logical-monitor scale reported by the compositor and is therefore *closer* to
the pointer coordinate space, but there can still be edge cases when mixing
backends.

If you see consistent offset/scale errors, consider:

- forcing a different pointer backend (`VHK_POINTER_BACKEND=ydotool` vs `dotool`)
- using compositor-native bindings for pointer movement when available
