# Host adapter, stat, watcher, and handoff cards

Shell surfaces for host compatibility should show adapter reality without implying extra authority.

A host-adapter card should show:

- provider type and current policy epoch;
- sandbox fit;
- authority-bearing handle, if any;
- whether the mount is a projection, import/export membrane, or hydrated placeholder surface;
- whether host-side state is advisory, current, stale, or receipt-only.

Stat and inode cards must avoid phrases like "this inode is the object" or "metadata proves access." They should say "legacy projection" and link to the backing ViewFS handle or explicitly say no live handle is present.

Watcher cards must distinguish notification from authority. A changed-file event may say that a compatible host observer saw a change, but opening or acting on that object still needs a live handle and current policy.

External-app handoff cards must distinguish one-shot portal/export approval from persistent grant. The receiver, redaction profile, target handle, and receipt should be visible, and the card should never claim that the external app now owns durable ViewFS authority unless a separate delegation says so.
