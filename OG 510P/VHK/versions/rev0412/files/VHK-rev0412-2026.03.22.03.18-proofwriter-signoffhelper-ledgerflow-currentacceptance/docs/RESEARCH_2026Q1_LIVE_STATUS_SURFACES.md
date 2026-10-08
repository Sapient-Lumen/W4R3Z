# Research 2026Q1: live installed-lane status surfaces

This pass focused on a narrow but practical product question: once VHK has a
reviewed bundle, a native launcher, and optional user-service composition, how
should the installed lane surface *current* health without pretending it has a
full desktop shell of its own?

Patterns borrowed carefully:

- **XDG state vs. packaged docs**
  Live status belongs in `XDG_STATE_HOME` / `~/.local/state`, not in the
  shipped app tree. That keeps the reviewed payload immutable while still
  letting the installed lane cache pinned/recent actions and write a current
  status snapshot.
- **Desktop-entry actions as shortcuts, not architecture**
  Desktop actions are a useful way to expose “open support guide”, “open
  service guide”, or “open live status report” from launchers that support
  them. They are not universal enough to become the only control surface.
- **Best-effort systemd user introspection**
  When VHK expects user units, the native launcher can query
  `systemctl --user show` for those exact unit names and fold the result into a
  live report. That is more Linux-native than inventing a private service-state
  registry, and more honest than pretending every host is systemd-shaped.
- **Learn from launcher ecosystems without copying them blindly**
  Tools like Ulauncher validate the idea that Linux launchers benefit from fast
  shortcuts, extensions, and discoverability surfaces. VHK should borrow the
  “quick access to relevant actions” lesson while keeping its reviewed-bundle
  and service-boundary story explicit.

Resulting product direction:

- keep packaged docs immutable and reviewable
- keep live state under XDG state
- let launcher actions open both packaged guidance and live reports
- let service/session hints stay explicit instead of hidden inside installer
  folklore
