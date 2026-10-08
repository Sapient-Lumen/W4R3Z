# Rev0960 research notes

The implementation was compared with primary operator and platform references:

- Syncthing's explicit database scan operation demonstrates that a
  replacement-class synchronization product benefits from an immediate owner
  scan command. It also highlights AnonSync's remaining lack of folder/subpath
  selection: <https://docs.syncthing.net/rest/db-scan-post.html>
- Linux `unix(7)` documents pathname-socket permissions and `SO_PEERCRED`, while
  warning that socket-file permission behavior is not portable POSIX security:
  <https://man7.org/linux/man-pages/man7/unix.7.html>
- Linux `flock(2)` documents advisory shared/exclusive locks, association with an
  open file description, and network-filesystem caveats:
  <https://man7.org/linux/man-pages/man2/flock.2.html>
- systemd `sd_notify(3)` provides service-state precedent. Rev0960 deliberately
  keeps data-integrity recheck on the owner socket rather than overloading
  configuration reload semantics:
  <https://www.freedesktop.org/software/systemd/man/sd_notify.html>

The resulting product direction is explicit owner control with truthful
acceptance/completion separation, not a new background authority or route-specific
synchronization path.
