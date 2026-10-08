# Atomic replace loses xattrs, ACLs, and timestamps

Simulates a crate that correctly uses an atomic replacement helper but overclaims that the destination file identity is otherwise unchanged.

Why this matters:
- `atomic-write-file` documents that replacing a file via a temporary file can lose metadata from the original file.
- The docs explicitly call out missing preservation support for timestamps, ACLs, Linux extended attributes (xattrs), and SELinux contexts.
- A persistence-surface crate should therefore publish **identity retention** explicitly instead of flattening replacement into “same file, just newer bytes”.

What this scenario should force:
- an `identity-retention.report` with per-metadata-class truth
- a summary that distinguishes safe replacement from identity preservation
- a doctor warning such as `metadata_retention_overclaimed`
