# Rev0987 implementation and audit record

## Product slice

Rev0987 adds one bounded durable selective-sync policy per configured folder.
The policy has one default mode, at most 1,024 canonical longest-component-prefix
rules, and at most 48 KiB of rule-path bytes. Metadata-only file operations keep
causal evidence while omitting payload transfer and rooted publication. A later
materialization expansion uses the existing reconciliation and convergence
engines to acquire and publish the current file.

A newly excluded regular file may be dematerialized only after the catalog
predecessor, current sole-visible target, exact selection generation/digest,
rooted file bytes and POSIX observation, and an independently retained private
payload descriptor all remain valid. The visible name is atomically displaced
with `RENAME_NOREPLACE`; that exact private inode is opened no-follow, rehashed
in full, re-proved, and only the private name is unlinked. Changed, untracked,
conflicted, and only-copy paths remain rooted and unresolved. No tombstone is
created. Work is bounded by the existing durable remote-effect cursor.

## Adjacent audit and refactor

The allocation-free descendant lookup originally lower-bounded on `directory`
instead of the virtual key `directory/`; a legal sibling such as `a-archive`
could hide a deeper `a/keep` inclusion. The retained comparator performs the
virtual-key comparison without allocating, and an exhaustive 486-policy
pairwise oracle checks the expansion classifier against direct path semantics.

A clean sanitizer graph exposed a build-boundary defect: the new selective-policy
test compiled instrumented dependencies but was omitted from the sanitizer
final-link inventory. CMake now applies both compile and link sanitizer flags,
and the selective-sync audit binds both inventories.

The atomic-publication source audit had also become stale after conditional
removal was centralized. It now isolates the shared private implementation,
excludes only that exact owner from the generic no-unlink rule, positively
requires both public wrappers to delegate to it, and verifies that the owner
unlinks only the private displaced name.

## Deliberate limitations

This is not placeholder sync, automatic private-payload eviction, quota policy,
or garbage collection. Dematerialization reclaims the synchronized-root copy but
retains the immutable private payload. The conservative first implementation
hashes the rooted file once during convergence and again after private
displacement; memory remains bounded, but very large-file narrowing pays two
complete reads. A crash between displacement and restoration/unlink can leave a
reserved private recovery artifact; bytes remain preserved, but automatic
residue recovery is future work.

The multi-terabyte workflow still requires a real high-path-count soak and
measured RSS, disk amplification, ENOSPC, initial-sync, and catch-up behavior.
Fixed-block delta remains vulnerable to insertion-driven boundary shifts.
Android remains a portability target, not a supported authority model.
