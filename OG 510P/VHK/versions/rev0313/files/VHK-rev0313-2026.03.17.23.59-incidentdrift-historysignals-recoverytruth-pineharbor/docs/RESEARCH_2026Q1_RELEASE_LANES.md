# Research notes — release lanes and Linux-native shipping

Why add release lanes after target-route comparison?

Because the ecosystem keeps showing that Linux automation products do not really
ship one universal desktop story:

- AutoKey still presents itself as an X11 automation utility, so its support
  language is already desktop/session scoped rather than blanket Linux parity.
- Espanso's Linux docs still distinguish systemd-managed startup from
  unmanaged/manual startup, which means the release story includes lifecycle,
  not only features.
- Espanso's Wayland docs still call support experimental and note missing
  app-specific configuration support there, which is exactly the kind of caveat
  a release-lane pack should make explicit.
- xremap still treats app-specific remapping and Wayland support as important,
  but its docs/troubleshooting continue to expose desktop-specific GNOME setup
  seams rather than promising one identical path everywhere.
- GlobalShortcuts still requires applications to create a session and bind
  shortcuts into it; that is a release-lane concern, not just a backend detail.
- `portals.conf` still routes portal backends per desktop and config precedence,
  which means backend choice is part of deployment policy.
- freedesktop autostart plus systemd user-manager docs keep reinforcing that
  Linux startup/lifecycle is plural: desktop autostart, user services, manual
  launchers, and helper daemons all coexist.

Product lesson:

VHK should not stop at “these target desktops choose different trigger routes.”
It should also help maintainers say:

- this is the flagship lane,
- these are supported but secondary lanes,
- these need caveats,
- these remain experimental,
- and here is the exact wording we should use publicly.
