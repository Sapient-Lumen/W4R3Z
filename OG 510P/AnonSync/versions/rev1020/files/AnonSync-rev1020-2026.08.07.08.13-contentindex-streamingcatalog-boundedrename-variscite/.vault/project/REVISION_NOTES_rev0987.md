# AnonSync rev0987 revision notes

## Selective synchronization

Rev0987 advances reconciliation to protocol generation 4 and adds one durable
bounded selective-sync policy per configured folder. The policy contains one
default plus at most 1,024 canonical longest-component-prefix rules and at most
48 KiB of rule path bytes.

The owner can inspect or replace it while the service is stopped:

```text
anonsync_sync selective-sync-status --manifest ABSOLUTE_JSON
anonsync_sync selective-sync-set --manifest ABSOLUTE_JSON \
  --default materialize|metadata_only \
  [--rule MODE=CANONICAL_PATH ...]
```

Metadata-only file operations retain causal evidence but omit payload transfer
and rooted publication. A later genuine expansion uses ordinary reconciliation
to obtain the missing payload and ordinary folder convergence to publish it.

## Rooted dematerialization

A newly excluded file that is already rooted can now be removed safely. The
effect requires an exact unchanged catalog predecessor, current metadata-only
policy, matching rooted descriptor, current sole-visible causal target, and an
independently verified immutable private copy retained through the unlink.
Immediately before unlink, the visible name is atomically displaced and that
exact private inode is hashed again in full under a stable POSIX observation.
Failed byte or observation proof restores the displaced object when possible.
Changed, untracked, conflicted, or only-copy paths are preserved and reported as
unresolved. No tombstone is minted. Dematerialization also obeys the existing
bounded remote-operation frontier and resumes through its durable cursor.

The private payload is deliberately retained, so this reclaims synchronized-root
space rather than total AnonSync storage. The conservative first implementation
also performs a second complete file read at the private unlink cutpoint. A crash
in the narrow post-displacement window may leave a reserved private recovery
artifact; the bytes are preserved, but automatic residue recovery is future
work. Quota-aware payload collection remains future work.

## Expansion fence and successor rehydration

The durable absence fence now opens only when a policy change materializes at
least one path previously treated as metadata-only. Pure narrowing no longer
blocks deletion repair across the rest of a large tree. An already-active fence
is retained until an ordinary complete remote sweep settles it.

While that exact fence is active, a reselected absent path may materialize the
cataloged operation or a current causal successor learned while excluded. A
focused regression proves materialize, dematerialize, remote successor,
reselect, acquire, and publish through the ordinary engines.

## Audit/refactor

Policy expansion is decided exactly from the finite union of rule boundaries
and the default region without walking the namespace or allocating a merged
container. An exhaustive focused oracle compares all 486 policies over a nested
boundary basis pairwise. Ordinary mode lookup and directory pruning allocate no
memory.

The first allocation-free pruning refactor lower-bounded on `directory` rather
than the virtual `directory/` key. A legal sibling such as `a-archive` could
therefore sort before `a/keep` and hide the deeper include. The final comparator
uses the virtual slash-suffixed key without allocating it, and an adversarial
regression binds that ordering.

Prepared local files, direct remote apply, and historical restore now carry or
re-prove the exact selection generation and digest before rooted publication, so
stale in-flight work cannot rematerialize a path after narrowing.

A clean sanitizer graph exposed a release-surface defect: the selective-policy
test compiled instrumented dependencies but was omitted from the final-link
sanitizer inventory. CMake now applies both compile and link sanitizers to
that executable, and the selective-sync source audit binds both lists. The
atomic-publication audit was also refactored to inspect the shared private
conditional-removal owner, exclude only that exact owner from the generic
no-unlink rule, and require both public wrappers to delegate to it.

## Product direction

The first target remains Linux/headless synchronization of multi-terabyte media
trees with mandatory delta transfer and selective synchronization. Rev0986
implemented fixed-block delta; rev0987 implements the first selective-sync
vertical slice. The next product edge is measured scale qualification and a
content-defined or multi-level delta generation for insertion-heavy large files,
followed by rename/move identity, directory semantics, quota/ENOSPC handling,
and an operator-usable conflict workflow.

Android remains desirable but unclaimed. Credentials remain operator-owned and
outside backup authority. Retention remains best effort and conservative when
continuity is uncertain.

## Limitations

This revision provides no filesystem placeholders, automatic private-payload
eviction, destructive garbage collection, Android adapter, identity-preserving
rename/move, empty directories, complete portable metadata, or polished conflict
UI. The explicit production path and payload identity ceilings still require
measurement against the owner's real high-path-count media tree.

## Validation

Exact rev0987 source passed a fresh GCC 14.2 Debug complete graph (540/540 configured build edges), 265/265 documentation-independent tests plus the finalized selective-sync and structural audits for complete 267/267 registered-test accounting, and an independent 43/43 GCC product replay. Focused GCC proofs passed 26 selective-policy, 18/18 conditional-unlink-authority, 644 payload-store, 4,861 reconciliation-protocol, 106 reconciliation-service, 518 folder-owner, 2,043 TLS-transport, and 110 sync-once checks. Source audits passed 52/52 selective-sync, 43/43 atomic-publication, 42/42 fixed-block-delta, and 420/420 structural payload-store authority checks. A fresh Clang 17 Debug product graph completed 251/251 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 43/43 product tests passed in bounded exact-source invocations with leak detection and halt-on-error. Focused sanitizer proofs passed the same 26, 18, 644, 4,861, 106, 518, 2,043, and 110 checks; the folder-owner proof peaked at 1,649,884 KiB RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0986 parent SHA-256 matched 00eca1b35b4072365aac651717506a4d02f6ea9593124151c18af99de0d8c3c3 and passed 41/41 wrapper-aware package checks. The binary-aware patch reconstructed all 31/31 changed active files and the complete 591-file projection byte-for-byte and by mode. The final active implementation projection contains 591 files / 27,507,720 bytes with SHA-256 307fe1ce3827c871ffe3dfdc3f9c4ac477fbad1b205dfb6ef986ac3fccd2f59f. The final wrapper directory and ZIP remain publication-gated on the exact manifest, package verification, CRC integrity, canonical paths, absence of symlinks, and clean-extraction path/byte/type/mode equality.

## Archive

AnonSync-rev0987-2026.08.04.03.36-selectivepolicy-rooteddematerialization-expansionfence-dioptase.zip
