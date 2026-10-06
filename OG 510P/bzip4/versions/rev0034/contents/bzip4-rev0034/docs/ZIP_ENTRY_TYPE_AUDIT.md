# ZIP entry-type audit — rev0030

Central `version made by`, external attributes, DOS directory bits, and the
trailing-slash marker are used to classify regular files, directories, symbolic
links, special POSIX files, and unclassified entries. Host identifiers 3 (Unix)
and 19 (OS X) are treated as POSIX mode carriers.

An explicit POSIX directory must have a trailing slash. An explicit
non-directory must not. The DOS directory bit may not contradict an explicit
POSIX non-directory; without POSIX type bits it must still agree with the name
marker.

Default policy rejects symlinks, special files, and type mismatches through
separate switches. A report-only override keeps the issue and counters; it does
not authorize extraction.

Schema `bzip4.zip-preflight.v6` retains all v4 type counters and adds ZIP64 and
central-retention telemetry. The 18 representative archives contain 15,707
explicit regular files, 298 directories, and 4,672 unclassified entries, with
zero symlinks, special files, or type mismatches. Unclassified is not treated as
regular because many valid producers omit explicit type bits.

Preflight does not decompress symlink payloads, resolve targets, create
filesystem objects, or enforce a destination capability. Extraction remains a
separate policy boundary.
