# Atomic permission repair and process-bound private-temp leases (rev0963)

## Executive judgment

Rev0962 made abrupt save-process death observable. That evidence exposed two
unfinished states with direct user cost:

1. after an atomic replacement, the correct document bytes could be visible at
   the intentionally private staging mode (`0600`), while restart treated the
   matching bytes as complete and retired the only recovery witness; and
2. hard death could strand exact unsaved bytes in private checkpoint or document
   temps, but Micromax had no safe way to distinguish a dead creator from a live
   process—especially on a shared container volume where the same numeric PID
   can exist in another PID namespace.

Rev0963 closes those paths with executable transactions rather than a general
cleanup registry. Atomic writes now declare their final permission intent before
the recovery checkpoint. Restart offers one narrow, fd-bound permission repair,
and private temp names carry a versioned save lease plus enough Linux process
identity to make explicit cleanup fail closed.

## What had gone severely wrong

### Matching bytes were mistaken for a completed permission transaction

The recovery journal compared the target bytes with the intended commit. When
they matched, the target was classified `already persisted`; ordinary recovery
could dismiss the record. That is insufficient for the atomic writer introduced
in rev0962: it publishes the new inode while it is still `0600`, restores the
intended mode, synchronizes the inode, and then synchronizes the directory. A
process death after replacement or `chmod` can therefore leave correct bytes
without proof that the complete permission/durability sequence finished.

The dangerous case was not data corruption. It was loss of the witness needed to
finish or honestly refuse the remaining transition. A document intended to be
`0640` could stay unexpectedly owner-only forever, while an intended `0600`
document could look complete even though its replacement namespace had never
been re-synchronized.

### PID-only cleanup is not authority

A numeric PID can be reused after a process exits. In containers, the same PID
can also name unrelated processes in different PID namespaces. Age thresholds
have the same defect: a slow or suspended writer does not become deletable merely
because a clock advanced. Broad glob cleanup would eventually delete live
private work.

The cleanup proof therefore has to bind a temp to one save transaction and one
process instance, and it must degrade to `unknown`, not `stale`, whenever the
host cannot establish that identity.

### The mode probe still had avoidable residue and cleanup did duplicate work

To preserve default ACL/umask effects without mutating process-wide umask, a new
atomic target needs an empty `0666` probe. The rev0962 POSIX path unlinked it
immediately after opening, but a small open-to-unlink death window remained.
Also, timeout cleanup scanned a parent once for the nominal symlink name and
again for its concrete target name even when both lived in the same directory.
Neither problem justified more doctrine; both were small code fixes.

## Implemented transaction

### 1. Permission intent is pinned before checkpoint publication

`plan_atomic_write()` resolves the nominal and concrete target authority before
the journal record is published. The immutable plan records:

- requested and concrete write paths;
- whether a final-component symlink was followed;
- preserve-permission policy;
- whether an existing mode was preserved;
- the exact intended final mode; and
- containing-directory device/inode identity.

The plan itself runs through the existing bounded worker boundary when the
editor has a filesystem timeout. The writer consumes the plan verbatim and
refuses parent replacement, symlink retargeting, option drift, or invalid mode
metadata before creating a payload temp.

The journal stores a versioned `atomic-private-temp-mode-v1` contract, the
private staging mode, intended final mode, save lease, and pinned parent
identity. The contract is opt-in and validated before durable publication, so a
partial or malformed record cannot silently acquire repair authority.

### 2. `recovermode` is a narrow verified continuation, not generic `chmod`

When target bytes match a retained atomic commit, `recoveries` now distinguishes:

- permission repair required (`0600` to the intended mode);
- permission synchronization pending (the mode already equals the intended
  mode, including intended `0600`); and
- permission conflict (bytes match, but authority or mode is outside the
  recorded transaction).

`recover` no longer retires such a witness. The explicit interactive command
`recovermode [#N|ID]`:

1. opens the recorded parent directory without following a replacement path and
   verifies its device/inode identity;
2. opens the target relative to that descriptor with final-component no-follow;
3. requires the exact committed bytes, a regular file, current effective-user
   ownership, one hard link, the recorded inode, and either the private or
   intended mode;
4. revalidates the named inode and mode immediately before `fchmod`;
5. applies the intended mode only when needed;
6. synchronizes the inode, then the pinned containing directory;
7. re-reads and revalidates bytes, inode, name, and mode; and only then
8. retires the recovery record.

If directory synchronization is unavailable, the mode may already be correct,
but the journal remains for an idempotent later retry. An intended final mode of
`0600` uses the same sync-and-retire path; equality is not treated as proof that
the transaction completed.

### 3. Private temps carry v3 process identity and a save lease

A v3 temp name includes:

- a 128-bit random save lease shared by the checkpoint and document writer;
- a compact boot identity;
- a compact PID-namespace identity;
- creator PID;
- creator `/proc/<pid>/stat` start tick; and
- an independent random filename token.

The PID namespace is taken from the canonical `/proc/<pid>/ns/pid` link text
(`pid:[N]`) when available, with the documented namespace-handle device/inode as
a fallback. This cloudtainer synthesizes unstable `stat` inode values for those
handles but preserves stable link text, so preferring the documented link value
is necessary for the current process to classify as active here.

A creator is `stale` only when all identity fields are reliable in the current
PID namespace and the tuple can be disproved—for example, the boot differs, the
PID is absent, or the PID now has a different start tick. Cross-namespace,
permission-denied, malformed, legacy-v2, or unavailable evidence is `unknown`
and cannot authorize cleanup.

### 4. Cleanup is bounded, visible, explicit, and revalidated

`recovertemps` lists a bounded metadata-only inventory. It does not open temp
payloads.

- Parseable checkpoint temps in the private recovery directory can be listed
  even when death occurred before journal publication.
- Document temps are listed only when a valid journal record supplies the exact
  save lease and the still-matching parent device/inode authority.
- Active and unknown creators remain visible but are never cleanup eligible.
- Directory entry, row, record-count, and record-byte limits are reported rather
  than hidden.

`recoverclean [#N|ID]` removes one selected row only after reopening the parent
without following it and rechecking parent identity, exact filename grammar,
lease, process identity, file device/inode, size, mtime, mode, regular-file type,
owner, link count, and stale-owner proof. The unlink is descriptor-relative and
the directory is synchronized where supported. A changed or disappeared row is
refused.

The bounded write parent now removes only temps carrying both the killed worker
PID and the exact save lease. Cleanup authority no longer depends on basename,
so nominal and concrete targets in the same parent require one scan instead of
two.

### 5. Empty mode probes prefer unnamed inodes

On Linux/filesystems supporting `O_TMPFILE`, default-mode discovery now uses an
unnamed regular inode that is unreachable by pathname and vanishes at descriptor
close. Permission, capacity, and I/O failures still propagate. Only documented
capability-absence errors fall back to the empty named probe, which POSIX unlinks
while still open.

The workspace filesystem in this cloudtainer rejected `O_TMPFILE`, so actual
runtime here exercised the conservative fallback. The new branch is covered by
deterministic unit tests rather than being claimed as live-filesystem evidence.

## Audit/refactor findings

- Permission repair originally checked the named inode before the fault/concurrency
  boundary but did not require the observed mode there. It now checks both before
  and immediately after the boundary, directly before `fchmod`; an injected
  external `chmod` is refused and the journal remains.
- The first implementation treated intended mode `0600` as already resolved. It
  now synchronizes file and directory and retires only after the same final
  verification used for other intended modes.
- Timeout cleanup carried an unused basename argument and deduplicated on
  `(parent, basename)`, causing redundant full-directory scans. It now
  deduplicates parents and matches only process plus lease authority.
- Process identity accepted arbitrary 16-character strings as reliable. Tokens
  now require lowercase hexadecimal grammar, and temp construction rejects a
  nonpositive PID.
- The portable empty mode probe remains payload-free. On POSIX it is unlinked
  before `fstat`; when supported, `O_TMPFILE` removes even the small named-open
  window.
- The generated `ed.save` resource contract initially failed after planning
  was inserted because `mxaudit` matched one exact source wrapping. The audit now
  follows the effective write timeout through a local alias into both
  `plan_atomic_write_bounded` and `write_file_bytes`, and checks semantic docstring
  fragments rather than physical lines.

## Online research used

Primary operating-system documentation informed the implementation:

- Linux `open(2)` documents `O_TMPFILE` as an unnamed regular inode, automatic
  deletion at last close, mode handling like `O_CREAT`, filesystem support
  requirements, and capability-absence errors:
  https://man7.org/linux/man-pages/man2/open.2.html
- Linux `namespaces(7)` documents `/proc/<pid>/ns`, stable namespace handles,
  matching device/inode identity, canonical `type:[inode]` link text, and the
  permanence of a process's PID-namespace membership:
  https://man7.org/linux/man-pages/man7/namespaces.7.html
- Linux procfs documentation describes per-process directories and PID reuse:
  https://docs.kernel.org/filesystems/proc.html
- `proc_pid_stat(5)` defines field 22 (`starttime`) used to distinguish process
  instances sharing a numeric PID:
  https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html
- The kernel sysctl documentation defines the per-boot random `boot_id` source:
  https://docs.kernel.org/admin-guide/sysctl/kernel.html
- `fsync(2)` documents that synchronizing a file alone does not necessarily
  synchronize the directory entry containing it:
  https://man7.org/linux/man-pages/man2/fsync.2.html
- `rename(2)` documents atomic name replacement semantics, which are necessary
  but separate from persistence completion:
  https://man7.org/linux/man-pages/man2/rename.2.html

## Honest limits

- This is conservative Linux/POSIX process-identity logic, not a portable
  cross-host garbage collector. Without reliable `/proc` boot, namespace, PID,
  and start-time evidence, cleanup remains unavailable.
- A document temp from a save whose journal checkpoint never published cannot be
  correlated later by lease and parent authority. It remains private residue for
  manual filesystem administration; Micromax does not broaden its scan to guess.
- The named mode-probe fallback can still leave an **empty** ordinary-mode file
  if the process dies in the tiny interval between open and unlink. It never
  contains document bytes. `O_TMPFILE` removes that window only where supported.
- POSIX provides no compare-and-swap `chmod`. The implementation narrows and
  tests the revalidation boundary, but a hostile concurrent directory owner can
  still race after the last check. This is an application trust boundary, not an
  operating-system sandbox against an adversarial peer with the same filesystem
  authority.
- Deleting an already-unlinked temp cannot be rolled back if the following
  directory sync fails. The outcome reports the sync witness honestly.
- Process-death tests do not prove sudden-power-loss, controller-cache, remote
  filesystem, Windows, or all-mount-option behavior.
- Direct writes remain non-atomic across death after truncate; exact recovery
  text remains the mitigation.

## Next highest-leverage work

The specific crash-residue and permission-repair blockers are now executable.
The next product-risk choices are to pin real `micromax.screen.v1` consumers and
visual budgets so taste work cannot drift behind internal models, and to derive
tests, wheel, archive, and provenance from one declared source snapshot. Further
save work should be driven by new process/power-loss evidence rather than by a
larger recovery registry.
