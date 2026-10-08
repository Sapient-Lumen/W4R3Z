# VHK revision 0258 — portal manifest inventory, routing diagnostics, and backend reality checks

This revision tightens one of the trickiest Linux-native seams in VHK: **Wayland portal backend discovery**.

The repo already probed live XDG Desktop Portal frontend interfaces (`Screenshot`, `ScreenCast`, `RemoteDesktop`, `InputCapture`, `GlobalShortcuts`) and parsed `portals.conf`. That was useful, but incomplete. It could tell you that an interface was missing without being able to answer:

- is a matching backend actually installed?
- is the backend present but excluded by `.portal` `UseIn` rules for the current desktop?
- does `portals.conf` reference a backend id that is not present on disk?
- are alternative wlroots backends (for example `luminous`) installed but not yet routed?

## What changed

### 1) `vhk doctor` now inventories installed `.portal` backend manifests

New probe surface:

- `xdg_portal_backend_manifests`

It scans the standard XDG data roots for `xdg-desktop-portal/portals/*.portal` files and records:

- backend id (filename stem)
- manifest path
- D-Bus name
- advertised `org.freedesktop.impl.portal.*` interfaces
- `UseIn` desktop rules
- whether the backend is usable on the current `XDG_CURRENT_DESKTOP`
- parse failures / malformed manifest warnings

### 2) capability-matrix portal backends now have a real fallback path

`build_doctor_capability_matrix()` used to derive portal backend names only from `portals.conf`.

It now:

- prefers explicit `portals.conf` routing when present
- otherwise falls back to installed manifest-advertised backends for that interface
- prefers backends whose `UseIn` rules match the current desktop

This makes the matrix more honest on hosts that have portal backends installed but do not ship a visible `portals.conf`, or where the user has not written one yet.

### 3) doctor advice now explains *why* a portal interface is missing

When a live portal interface is absent, VHK can now add more specific hints:

- “a backend advertising this interface exists, but its `UseIn` rules do not match the current desktop”
- “installed manifests advertising this interface include …”
- “`portals.conf` references backend ids that were not discovered in installed `.portal` manifests”
- “some installed `.portal` manifests could not be parsed”

That moves VHK closer to the kind of host-reality diagnostics Linux-native automation needs.

## Why this matters for VisualHotKey specifically

VHK is trying to be honest about Linux automation instead of flattening everything into “Wayland supported / not supported”. Portal routing is exactly the kind of seam where that honesty matters:

- screenshot support may come from one backend
- screencast support from another
- global shortcuts may only exist on some desktops
- RemoteDesktop / InputCapture may exist only on a subset of backends and sessions
- user-space diagnosis often depends on `XDG_CURRENT_DESKTOP`, activation environment, and packaging choices outside the macro repo itself

Manifest-aware doctor output gives VHK a better foundation for future:

- readiness packs
- host contract packs
- setup/install advice
- environment-diff planning

## Tests added

New coverage in `tests/test_doctor_cli.py`:

- manifest discovery and capability fallback coverage for `gtk`, `wlr`, and `luminous`
- advice coverage for desktop-mismatch (`UseIn`) and missing configured backend ids

Broader regression checks run for:

- `tests/test_doctor_cli.py`
- `tests/test_portal.py`
- `tests/test_global_shortcuts_portal.py`
- `tests/test_plan_project_cli.py`
- `tests/test_validate_cli.py`

## Follow-up work

The next logical extension is to thread the same manifest inventory into:

- host-contract artifacts
- readiness/session-fit packs
- setup docs/scripts
- environment comparison output

so VHK can compare **configured**, **installed**, and **live** portal state in one review surface.
