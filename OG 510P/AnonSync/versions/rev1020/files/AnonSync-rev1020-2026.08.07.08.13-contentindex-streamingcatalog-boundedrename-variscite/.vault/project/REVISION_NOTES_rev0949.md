# AnonSync rev0949 revision notes

## Mission

AnonSync exists to replace Resilio Sync in one named real workflow with a
practical C++ folder-synchronization product. Direct TCP, Tor, and I2P are
routes into the same authenticated synchronization semantics. This revision
strengthens the retained shipping folder observer, owner, service configuration,
and diagnostics; it does not add another daemon or sync engine.

## Primary correction: one field represented two different capacities

Before rev0949, `maximum_entries` bounded every object classified by the rooted
walker: directories, regular files, symbolic links, unsupported objects, and
reserved internal artifacts. Rev0946 then correctly constrained that same field
to the 100,000-entry catalog and payload-store production boundary. The result
was a composition error in the opposite direction from rev0946's original
payload-store defect: objects that never become cataloged file rows or payload
identities consumed durable file capacity anyway.

A tree containing 100,000 regular files and ordinary directory structure could
therefore be rejected even though the catalog and payload owners could represent
all of its current files. Increasing the old field would have widened a service
configuration beyond the actual durable owners. Keeping it at 100,000 made
namespace shape, not synchronizable file count, determine whether the contract
was usable.

Rev0949 introduces two explicit limits:

- `maximum_entries` bounds all classified namespace objects and defaults to
  262,144;
- `maximum_regular_files` bounds current synchronizable regular files and
  defaults to the 100,000 production catalog/payload capacity.

Both are independently validated in the observer. Every classified object
spends the namespace allowance. A regular file additionally spends the file
allowance immediately after descriptor-relative classification and before
resume filtering or scheduling-frontier decisions. Counting the replayed prefix
and the first frontier candidate is intentional: a durable cursor cannot make a
folder containing too many files appear admissible merely by splitting it into
segments.

The folder owner now validates `maximum_regular_files`, rather than all namespace
entries, against the actual catalog and payload-store capacities. The internal
4,096-path segment frontier must not exceed the whole-folder regular-file limit.
Compile-time production assertions bind the ordinary 100,000 regular-file and
remote-path ceilings to the durable owners while allowing a larger namespace
work ceiling.

The field is carried end to end through:

- the linked service JSON parser and production composition check;
- `anonsync_sync` and `anonsync_folder` CLI overrides;
- identity/share create, provision, link, and join setup surfaces;
- persisted provisioning output and `check-config`;
- convergence reports and test fixtures.

A process test proves that `maximum_entries = 100001` is accepted with the
default 100,000 regular-file contract. `maximum_regular_files = 100001` is
rejected through the real `check-config` path before service owners mutate. A
folder-owner fixture separately proves that two files plus one directory fit a
three-entry/two-file contract, while lowering only the entry limit rejects the
pass without changing the catalog.

## Audit correction: avoid a complete speculative idle pass before a bounded pass

Rev0948 removed duplicate whole-tree path vectors from the idle fast path, but
the optimization could still violate the intended work shape. It attempted a
complete read-only proof first. Only after the walker reached the 4,096-path
segment frontier did the owner fall back to the durable continuation path. For
a known-large unchanged catalog, one service turn could therefore perform a
whole speculative replica projection and rooted prefix before doing the bounded
authoritative segment.

Rev0949 checks total retained catalog mappings before taking the speculative
replica snapshot, counting file rows, or entering the idle traversal. A catalog
larger than the path segment frontier goes directly to durable segmented work.
The gate counts all mappings, not only current `File` rows, because tombstones
are retained history and the idle proof must inspect their path state too. A
restart-backed test first proves bounded continuation for five unchanged files
with a two-path frontier, then deletes all five, publishes five tombstones, and
proves the tombstone-heavy catalog also bypasses the idle fast path while an
authoritative epoch completes without mutation.

This is not an attempt to make deletion authority incremental. Completed-epoch
absence adjudication remains deliberate whole-catalog work. The correction only
prevents a speculative optimization from duplicating that scale of work before
the bounded authoritative path.

## Diagnostic refactor: exact traversal stop reasons

A traversal segment now reports one of four states:

- `not_started`;
- `end_of_namespace`;
- `aggregate_file_byte_frontier`;
- `regular_file_count_frontier`.

The observer assigns the outcome only after the descriptor-rooted walker has
unwound, rebound every opened directory, and reverified the retained root. The
folder owner carries it into pass reports, and both diagnostic CLIs serialize it.
The value explains scheduling behavior; it is not persisted authority and cannot
substitute for the authenticated epoch journal or completion proof.

## Exact nonclaims and next scale owner

The new 262,144 default is not a huge-tree guarantee. It truthfully separates
namespace work from file storage, but shape-dependent costs remain:

- `read_sorted_components_or_throw` still retains and sorts every immediate
  basename in one directory before processing children;
- every continuation segment starts at the root and re-enumerates and `lstat`s
  its skipped prefix;
- a watcher remains an accelerator, not completeness authority;
- completed-epoch absence adjudication still examines retained catalog history;
- current catalog and payload stores retain historical identities, so 100,000
  current files provide no guaranteed edit/delete churn headroom;
- a 262,144-object namespace can still be too small for some valid shapes with
  100,000 regular files; operators must measure the first target workload.

The next structural correction should be a crash-consistent exact metadata and
subtree index that can resume near the durable cursor, identify changed subtrees,
and support incremental absence candidates. The rooted complete scanner should
remain the rebuild and rotating-scrub oracle. A durable payload index, explicit
version retention and restore, safe garbage collection, changed-block transfer,
rename/directory semantics, multi-share ownership, cross-platform behavior, and
live Tor/I2P qualification remain product work.

## Research

Current Syncthing documentation describes a persisted index database containing
file metadata and block hashes, filesystem notifications that trigger scans, and
continued periodic rescans. Its syncing documentation also describes local block
reuse. These are useful precedents for retaining AnonSync's watcher/full-scan
division while replacing repeated complete metadata work with durable indexes;
they do not establish equivalent behavior or performance here.

The Linux `scandir(3)` and `readdir(3)` manuals reinforce a narrower systems
observation. `scandir` allocates an entry array and sorts it, while `readdir`
returns entries incrementally and warns that directory offsets are opaque. A
future indexed walker cannot safely persist a raw `d_off` as a portable durable
cursor. AnonSync's current component-path cursor is semantically safer, but its
per-directory full basename buffering remains a measurable memory cost.

Sources consulted 2026-07-30:

- https://docs.syncthing.net/users/config.html
- https://docs.syncthing.net/users/syncing.html
- https://man7.org/linux/man-pages/man3/scandir.3.html
- https://man7.org/linux/man-pages/man3/readdir.3.html

## Validation

The frozen rev0949 source passed:

- the complete configured GCC 14.2 Debug target graph;
- every one of 254 registered GCC tests across bounded completed evidence
  shards;
- 35/35 GCC product tests in 25.75 seconds;
- 70/70 focused observer checks;
- 250 focused folder-scan-owner checks;
- the real service configuration/status process path, including acceptance of
  100,001 namespace entries and rejection of 100,001 regular files;
- the 59/59 payload/folder structural audit;
- a fresh Clang 17 Debug ASan/UBSan product graph, 222/222 build steps;
- 35/35 Clang product tests in seven completed fresh serial shards, 86.78
  cumulative real test seconds, with leak detection and no sanitizer diagnostic.

The lexical structural audit is hygiene evidence only. Runtime tests and direct
source review carry the filesystem, capacity, restart, and transaction claims.
