# Research 2026Q1: stateful native launchers

Why this pass mattered:

- the native install lane already had a credible reviewed-bundle story, but the installed launcher still assumed `$0` pointed at the real app tree even when the install flow exposed it through a symlink in `~/.local/bin`
- launcher quick actions were also frozen at generation time, which made them useful as a review surface but weak as an installed product surface

What we borrowed from current Linux conventions:

- XDG state is the right home for launcher-specific recent/pinned entry state because it is restart-persistent user state, not portable project data and not disposable cache
- desktop-entry actions are a good fit for quicklists/jumplists, but they are static file metadata; refreshing the installed desktop file from live launcher state is more honest than pretending those actions are magically dynamic
- launcher quick actions should stay additive. Some launchers surface them prominently, and some hide them unless the user or launcher mode explicitly asks for them

How that changed VHK:

- the generated native launcher now resolves its real app root through the installed symlink path before locating the reviewed bundle or embedded runtime
- the installed lane now keeps recent/pinned entry state under XDG state and can regenerate its installed desktop entry from that state
- the installed lane still works without those quick actions; the main launcher command remains the primary product entrypoint
