# Rev0978 research note

The writer-fenced candidate probe is grounded in open-file-description advisory-lock semantics. Linux `open(2)` distinguishes open file descriptions from descriptors and explains why duplicated or fork-inherited descriptors can keep one lock-bearing file description alive. Linux `flock(2)` and the kernel VFS API document whole-file advisory locks associated with that description and mediated at the inode. POSIX `fcntl` supplies the essential nonclaim: advisory locks constrain only cooperating processes.

Primary references:

- https://man7.org/linux/man-pages/man2/open.2.html
- https://www.kernel.org/doc/man-pages/online/pages/man2/flock.2.html
- https://docs.kernel.org/filesystems/api-summary.html
- https://pubs.opengroup.org/onlinepubs/9699919799/functions/fcntl.html

These interfaces support the global-then-inode lock order and the child-held-descriptor regression. They do not justify mandatory-lock, hostile-writer, copied-buffer, or unqualified network-filesystem claims.
