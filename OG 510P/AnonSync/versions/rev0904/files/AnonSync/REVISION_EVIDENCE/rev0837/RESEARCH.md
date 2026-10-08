# Research notes — AnonSync rev0837

## Nonblocking open is part of type-safe observation

POSIX specifies special FIFO behavior for `O_NONBLOCK`: opening a FIFO for read
only succeeds without waiting for a writer. That matters before type inspection;
without it, a pathname raced from a regular file to a FIFO can block inside
`open()` and never reach `fstat()`. Linux documents that `O_NONBLOCK` generally
has no effect on regular-file I/O, so it closes this FIFO-open hole without
proving an overall read deadline.

Sources:

- https://pubs.opengroup.org/onlinepubs/9799919799/functions/open.html
- https://man7.org/linux/man-pages/man2/open.2.html

## Final-component denial is not a complete path policy

Linux `O_NOFOLLOW` rejects a symbolic link only when it is the trailing path
component. `openat2()` can apply resolution policy across the complete walk;
`RESOLVE_BENEATH`, `RESOLVE_NO_SYMLINKS`, and `RESOLVE_NO_MAGICLINKS` are the
relevant primitives for a future descriptor-anchored trust root.

Source:

- https://man7.org/linux/man-pages/man2/openat2.2.html

## Descriptor metadata is an observation, not a snapshot primitive

`fstat()` reports metadata for the exact open descriptor, avoiding a second
pathname lookup. Comparing device/inode, size, mtime, and ctime before and after
materially improves rejection of concurrent replacement and mutation. It does
not freeze file contents or prevent a sufficiently privileged writer from
restoring metadata. Linux `statx()` offers richer metadata, including mount ID
and optionally change/version information on supporting filesystems, but feature
availability and semantics must be tested rather than assumed.

Sources:

- https://man7.org/linux/man-pages/man3/fstat.3p.html
- https://man7.org/linux/man-pages/man2/statx.2.html

## Windows opened-object ownership

`CreateFileW` with `FILE_FLAG_OPEN_REPARSE_POINT` opens the reparse point itself
instead of blindly following it. `GetFileInformationByHandle` and `ReadFile`
then keep inspection and bytes bound to one handle. Microsoft notes that the
64-bit file index in `BY_HANDLE_FILE_INFORMATION` is not guaranteed unique on
ReFS; `FILE_ID_INFO` exposes a 128-bit identifier for cross-handle identity work.
The current revision compares the same handle before and after, so this is a
future portability boundary rather than a demonstrated rev0837 defect.

Sources:

- https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew
- https://learn.microsoft.com/en-us/windows/win32/fileio/reparse-points-and-file-operations
- https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfileinformationbyhandle
- https://learn.microsoft.com/en-us/windows/win32/api/fileapi/ns-fileapi-by_handle_file_information
- https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_id_info
- https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-readfile
- https://learn.microsoft.com/en-us/windows/win32/fileio/testing-for-the-end-of-a-file
- https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-closehandle

## Design inference

The meaningful capability is not “a path passed validation.” It is “this opened
object produced these complete bytes under this ceiling, type, identity, and
change evidence.” That shape should recur across AnonSync: bind policy to the
resource capability actually consumed, prove completion rather than accepting a
prefix, and consume cleanup ownership exactly once.
