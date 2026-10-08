# Rev0954 audit summary

Rev0954 removes a restart-scale defect on the shipping payload-store path. A new
process previously rehashed every retained payload byte even when every immutable
payload and its private rooted observation were unchanged. The new fixed-width,
checksum-sealed verification checkpoint binds the exact store identity marker and
the canonical eleven-field POSIX observation for every digest-named payload.
Fresh processes still enumerate, rooted-open, stat, capacity-check, and pathname-
reprove the complete namespace; they hash every missing, stale, changed, malformed,
or identity-mismatched record. `ReadOnlyInspect` remains byte-cold and ignores all
acceleration.

Checkpoint refresh is best-effort and non-authoritative. Ordinary shared scans
return their proved snapshot before trying a fresh exclusive mutation lease and a
second complete metadata reproof. Mutation batches and successful receiver
publication may checkpoint an exact post-publication set. Torn or stale records
fail closed, staged residues are recognized and repaired under the existing
mutation authority, and transient capacity accounting reserves the checkpoint's
real fixed-width geometry rather than an unbounded estimate.

The refactor splits binary parsing into an independently tested leaf and
centralizes `stat` conversion so marker, payload, process-cache, and durable-
checkpoint observations cannot drift field by field. Runtime tests cover restart
reuse, stale inode replacement, identity rebind, pre-bootstrap forgery, malformed
and overgrown records, post-rename metadata, capacity pressure, owner/thread
fences, staged-prefix observation, and same-process repair. Process and durable
reuse are reported separately through the shipping folder/service diagnostics.

Reconstruction over the exact sealed parent also caught an older branch that had
removed rev0953's final equality check between the pass-published remote fairness
cursor and the durable terminal cursor. Rev0954 restores that predicate, its
compiled scheduling-only movement regression, and its structural guard. A fresh
Clang build exposed a second integration defect: the new instrumented leaf test
was absent from the explicit sanitizer final-link inventory. The CMake authority
and lexical audit now bind both compile and link closure.

A late one-entry-per-pass integrity-scrub experiment was rejected. Entry count is
not an I/O bound when one payload may be multiple gigabytes, and a process-local
cursor can repeat the same prefix after every restart. Rev0954 therefore makes no
permanent-corruption-detection claim. A future scrub owner must combine byte and
entry budgets, durable continuation/epoch state, and explicit quarantine or
failure semantics. The checkpoint checksum is not a MAC, history remains append-
only, and retention, restore, reachability pins, garbage collection, changed-file
block reuse, cross-platform qualification, and the first named Resilio uninstall
workload remain open.

The source structural audit passes 87/87 checks. It is a regression tripwire, not
a semantic, cryptographic, filesystem, concurrency, crash, or hostile-writer
proof. See `DURABLE_PAYLOAD_VERIFICATION_CHECKPOINT_AUDIT_rev0954.md`.
