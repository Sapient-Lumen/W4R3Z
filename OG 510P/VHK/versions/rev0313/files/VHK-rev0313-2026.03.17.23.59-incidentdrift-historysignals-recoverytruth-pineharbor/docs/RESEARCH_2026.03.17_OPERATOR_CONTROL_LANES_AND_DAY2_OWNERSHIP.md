# Research — operator control lanes and day-2 ownership

Recent upstream Linux automation docs keep reinforcing a simple lesson: the shipped surface and the operated surface are not always the same thing.

- Espanso exposes explicit `status`, `restart`, `service start`, `service stop`, `service register`, and `service unregister` flows, which means text expansion is not only a config package but also a managed service surface.
- keyd documents explicit install/start/reload/log loops (`systemctl enable --now keyd`, `keyd reload`, `journalctl -eu keyd`), which means low-latency remap lanes need an operator-control story, not just generated configs.
- Portal surfaces such as GlobalShortcuts and RemoteDesktop are session objects with create/start/bind/rebind behavior, while Background adds background/autostart permission as a separate lifecycle surface.
- InputCapture further separates `enabled` from `active`, showing that portal/session control is not the same thing as immediate runtime ownership.

VHK should therefore model a third truth alongside shipping lane and startup route: operator control lane.
