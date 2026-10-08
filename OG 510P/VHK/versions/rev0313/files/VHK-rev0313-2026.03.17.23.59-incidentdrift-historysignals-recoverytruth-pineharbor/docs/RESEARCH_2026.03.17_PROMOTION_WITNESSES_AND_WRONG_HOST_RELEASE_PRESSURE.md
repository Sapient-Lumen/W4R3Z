# Research — promotion witnesses and wrong-host release pressure

## Why this matters

A Linux-native automation project does not just need target claims and deployment
packs. It also needs the review surfaces in the middle to say whether the
current workstation is believable proof for the lane being promoted.

That becomes especially important on Wayland, where portal-first claims depend
on desktop family, configured routing, installed backend manifests, live portal
interfaces, and often helper/uinput posture too.

## Lessons from others

- AutoKey still keeps its official support story honest by describing itself as
  Linux/X11, even while Wayland work continues elsewhere.
- AutoKey’s current PR list shows that Wayland support is not one generic box to
  tick: GNOME and KDE are landing through different implementation paths.
- Espanso keeps scope and precedence explicit, including the note that
  app-specific configurations are not yet supported on Wayland.
- xdg-desktop-portal and libei/EIS both describe layered systems rather than one
  universal automation surface.

Product lesson: promotion surfaces should carry evidence posture forward instead
of flattening Linux review back into generic readiness prose.

## Direction added in this revision

`gen-promotion-pack` now consumes the same current-host claim witness posture
that claim/audit surfaces already know.

That adds three things to promotion output when live checks are present:

- a compact current-host claim witness section
- a `current-host-proof-gate`
- explicit backlog/evidence rows when that proof posture is not pass

This keeps a common Linux failure mode visible: the host you used for a refresh
may be useful engineering feedback while still being weak or misleading release
proof for the lane you are trying to promote.

## Immediate follow-through

- core planner/strategy JSON should eventually expose the same witness posture
  directly instead of relying on pack overlays
- release/publish snippets should be able to quote witness posture when repos
  want stricter proof chains
- operator-selected evidence hosts should become first-class once VHK starts
  tracking reviewed flagship environments more explicitly
