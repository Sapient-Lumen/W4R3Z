# Rev0977 research note

The reader fence follows Linux open-file-description `flock(2)` semantics: duplicated and fork-inherited descriptors share the lease, and the lease is released only after the last such descriptor closes. `unlink(2)` and `rename(2)` do not invalidate already-open file descriptions, which is why namespace mutation requires a separate exact-inode exclusion protocol rather than pathname reasoning alone. These locks remain advisory and require cooperating processes; remote-filesystem behavior remains a qualification boundary.

Primary references:

- https://man7.org/linux/man-pages/man2/flock.2.html
- https://man7.org/linux/man-pages/man2/unlink.2.html
- https://man7.org/linux/man-pages/man2/rename.2.html
