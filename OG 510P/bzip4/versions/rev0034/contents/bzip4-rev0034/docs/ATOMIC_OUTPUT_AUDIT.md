# Atomic output publication audit

`AtomicFileWriter` is the filesystem commit boundary introduced for the rev0021
codec CLI and retained by rev0022. It is intentionally separate from the codec
because a streaming codec can legitimately produce a prefix before a later
block fails.

## Protocol

1. Open the destination's parent directory and retain that descriptor.
2. Create a generically named same-directory temporary with
   `openat(O_CREAT|O_EXCL|O_CLOEXEC)`, mode `0600` by default.
3. Write all sink spans with EINTR-safe, progress-checked loops.
4. `fsync` and close the temporary.
5. Replace the destination with `renameat` through the pinned directory
   descriptor.
6. `fsync` the parent directory and report confirmed durability.

A destructor before rename closes and unlinks only the temporary inode actually
created by this instance. Failed collision candidates are never unlinked. A
failure before rename leaves the destination name untouched. A directory-fsync
failure happens after publication; in that case the new name is visible but
crash durability was not confirmed, so `published()` and `durable()` have
distinct meanings.

Same-directory staging avoids cross-filesystem rename failure and makes the
rename atomic for observers of the destination name. Replacing a destination is
intentional; existing file metadata and permissions are not preserved.

## Regression coverage

Tests prove rollback for an uncommitted writer, a sink exception after four
compression callbacks, and a late CRC failure in the second decoded block after
one successful output callback. In every pre-publication failure, the sentinel
destination is byte-identical and no `.bzip4-tmp-*` files remain. Successful
publication checks byte accounting, one-shot commit, post-commit write guards,
and parent-directory durability.
