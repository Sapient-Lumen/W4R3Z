# AnonSync rev0837 — opened-object bounded read

Rev0837 corrects the shared heartbeat/recovery file reader. The rev0836 helper
trusted its first file size, could accept a concurrently growing prefix as a
complete document, and could block in `open()` on a raced FIFO before type
validation. Its Windows path precheck and later path reopen were also separate
observations.

The revision extracts one dependency-free compiled leaf, makes the opened
object the authority, reads through EOF with a one-byte ceiling sentinel,
rechecks identity and mutation metadata, rejects final symlink/reparse objects
and embedded NUL paths, and preserves exact cleanup/error precedence. Both
production callers now use the same header-owned contract; the giant domain
unit loses 55 lines and the CLI loses its forward declaration.

Validation: exact rev0836 parent verification, exact source-patch replay over
220 active files, 127/127 registered tests, 21/21 structural checks, 740/740
repeated focused checks, Clang 17 37/37, GCC ASan/UBSan 37/37 with leak detection
disabled, and a zero-work final dependency closure. See
`REVISION_EVIDENCE/rev0837/` for exact witnesses, logs, limits, and inventory.
