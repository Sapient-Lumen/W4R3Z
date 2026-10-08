# rev0796 audit

## Finding: unsigned WAL state crossed a signed main-file boundary

The manifest and restore paths hashed `read_file(snapshot_path)`, then opened
that pathname with SQLite. A sibling `-wal` was outside the digest but inside
SQLite's logical database view. The preserved parent reproducer left the main
file digest unchanged, wrote a valid outbox mutation only to WAL, and rev0792
restored the unsigned `inflight` state.

This was a boundary-ownership error, not merely a missing filename check. Hash,
schema verification, prefix continuity, and `sqlite3_backup` each observed a
different moment or representation of the path.

## Correction

`SealedSqliteSnapshot` is now the sole production owner for untrusted snapshot
capture. It rejects journal sidecars; securely opens one single-linked regular
main file; copies and hashes exact bytes into a private 0700 directory; re-hashes
the private file before promotion; caps the copy at one GiB; pins the selected
SQLite VFS; and exposes only an immutable, read-only SQLite open over the staged
inode. Manifest digest verification, logical verification, prefix continuity,
and restore backup all consume that same process-local seal.

The existing path-family guard gained retained-parent read-only open and
sidecar-absence checks and was extracted from the core monolith into its own
library.

## Audit refactor

The legacy persistence inventory previously scanned immutable historical
evidence and still allowlisted the pre-rev0790 projection decoder. It now scans
only active source roots, strips comments and literals before matching,
distinguishes test fixtures from production, permits raw scalar extraction only
inside `sqlite_exact_value.cpp`, and runs as a fail-closed CTest gate.

## Deterministic checks

Twelve authority and architecture audits passed. The snapshot-seal source audit
has 37 checks covering single-owner construction, sidecar rejection, source and
staged-byte digest identity, byte budget, immutable URI flags, explicit/pinned
VFS use, live VFS pointer attestation, manifest and restore call-site reuse,
untrusted SQLite configuration, focused-link independence, and absence of old
raw snapshot opens.

## Remaining exposure

The seal bounds input bytes but not all SQLite CPU, page, row, allocation, or
wall-time work. Private staging temporarily duplicates plaintext snapshot bytes.
The process and superuser remain trusted. Crash-cut recovery, replay-evidence
provenance, formal convergence, and an end-to-end privacy model remain outside
this revision.
