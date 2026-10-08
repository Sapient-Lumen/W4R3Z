# AnonSync rev0880: mount-boundary authority and shared POSIX resolution audit

## Executive finding

AnonSync's receiver effect path is trying to prove a narrow statement:

> An exact authorized File operation may materialize only beneath the exact live
> root capability that owns the effect cutpoint, and every pathname component
> used to reach the destination must remain inside the root's authorized mount
> and mutation policy.

Rev0879 made the root a retained descriptor rather than reusable path text, but
its descendant fence was based on `st_dev`. That was necessary and portable,
but not sufficient. Linux bind mounts and other mount attachments can expose a
new mount boundary backed by the same filesystem device. An attacker or
misconfigured supervisor able to alter the mount namespace could therefore put
a same-`st_dev` mount below the authorized root. The descendant ownership and
mode checks could all pass even though pathname resolution had crossed into a
separately attached mount object.

This is not theoretical on the validation host. `/proc` and `/proc/bus` report
the same `st_dev`, while `/proc/bus` is a distinct mount. The rev0879 device
comparison cannot distinguish that boundary.

Rev0880 adds a live, capability-classified Linux mount fence:

* `openat2(2)` with `RESOLVE_NO_XDEV` rejects a component when kernel pathname
  resolution would cross a mount point, including a bind mount;
* `statx(2)` mount identity independently checks the opened descriptor and can
  detect a same-device crossing after open;
* `STATX_MNT_ID_UNIQUE` is preferred when the running kernel actually returns
  it, while the older `STATX_MNT_ID` remains a valid live observation;
* the exact observed capability is frozen in `SyncDirectoryAuthority` and
  re-proved before later use;
* non-Linux or genuinely unavailable kernels retain the portable `st_dev` /
  `st_ino` baseline and its explicit same-device-mount nonclaim; and
* no kernel version is used as evidence that a syscall, flag, mount ID, header,
  seccomp profile, or namespace view is available.

The same revision removes three subtly different component-traversal state
machines by placing `fstatat`/no-follow inspection, `openat2` or `openat`,
post-open `fstat`, identity comparison, bounded race retry, and mount comparison
under one POSIX syscall owner. It also fixes a descriptor leak in the atomic
publication adapter when the authority's post-duplication reproof throws.

## Heart of the mission

AnonSync is an authority-accounting engine. Its heart is not transport and not
file copying. Exact authorized evidence must own every transition from
observation to visible effect:

1. exact canonical bytes own operation identity;
2. exact predecessor evidence owns causality;
3. exact trust and dependency state own projection;
4. an exact outbox claim owns one transport attempt;
5. an authenticated live channel owns interpretation of frame bytes;
6. exact staged payload bytes own materialization;
7. a retained filesystem capability owns pathname resolution and publication;
8. a terminal effect cutpoint owns the receipt that can settle the sender; and
9. summaries, paths, indexes, clocks, mount IDs, sessions, and reports remain
   evidence or acceleration, never substitute authority.

Mount handling belongs in that chain because a pathname component is not merely
text. Linux pathname lookup may transition from one mounted object to another.
If that transition is not part of the authorized effect policy, accepting it
silently lets mutable environment state redirect exact operation authority.

## Parent defect: `st_dev` is not mount identity

Rev0879's rooted atomic publication performs component-wise no-follow traversal
and checks each opened directory against the retained root's device, owner, and
mode. This blocks a different filesystem device, a symlink, a foreign owner, or
a group/other-writable descendant. It does not block a same-device mount.

A bind mount attaches an existing directory tree at another mount point. The
underlying files retain their device and inode identities. A distinct mount
object can therefore have the same `st_dev` as its parent. Device identity is a
filesystem identity observation, not a mount-transition proof.

On this cloudtainer:

```text
/proc      st_dev=28
/proc/bus  st_dev=28
```

Yet `/proc/bus` is a separate mount attachment. This gives a deterministic,
unprivileged runtime witness for the exact class of boundary rev0879 could not
see. The container lacks `CAP_SYS_ADMIN`, so the test does not manufacture a
private bind mount and does not claim privileged namespace coverage. It uses the
host-provided mount only when the witness and a strong observed capability are
both present.

## Linux authority primitives

### `openat2` as a resolution-time fence

Linux `openat2(2)` extends `openat(2)` with an explicit resolution policy. The
kernel documentation states that `RESOLVE_NO_XDEV` disallows mount-point
crossings, including bind mounts. `RESOLVE_BENEATH` prevents resolution outside
the supplied directory, and `RESOLVE_NO_SYMLINKS` rejects symbolic links in all
components. `RESOLVE_NO_MAGICLINKS` is retained explicitly even though current
Linux semantics imply it under `RESOLVE_NO_SYMLINKS`.

Rev0880 opens one already-separated component at a time with:

```text
O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW
RESOLVE_BENEATH | RESOLVE_NO_MAGICLINKS |
RESOLVE_NO_SYMLINKS | RESOLVE_NO_XDEV
```

`EXDEV` becomes an explicit retained-root mount-boundary violation. `ELOOP`
remains an explicit symlink violation. Linux may return `EAGAIN` when it cannot
prove a `RESOLVE_BENEATH` constraint safely in the presence of a rename or mount
race. The helper retries that result only eight times, then fails. It never
turns an unbounded adversarial race into unbounded CPU authority.

A successful probe of `openat2` against `.` proves that this running process can
invoke the syscall with the complete requested policy. It does not prove that
all future pathnames are safe. Every component is still opened under the policy,
and the returned descriptor is independently compared with the pre-open
no-follow identity.

Primary source:

* https://man7.org/linux/man-pages/man2/openat2.2.html

### `statx` as descriptor mount evidence

`statx(2)` can return `stx_mnt_id` for an opened descriptor through
`AT_EMPTY_PATH`. Rev0880 requests both `STATX_MNT_ID` and, when the build headers
expose it, `STATX_MNT_ID_UNIQUE`. It trusts only fields whose bits the running
kernel places in `stx_mask`.

The older `STATX_MNT_ID` is unique for the mount namespace but can be reused
after unmount. `STATX_MNT_ID_UNIQUE`, introduced later, supplies the kernel's
extended mount ID and is not reused for the lifetime of the system. Rev0880
prefers the unique form when it is actually returned; it records the identity
kind as well as the numeric value so an old and extended ID cannot compare equal
by accident.

The root's mount identity is captured once when the live authority is minted.
Every descendant descriptor opened under rooted publication is compared against
that retained mount identity. This provides an independent post-open fence when
`statx` is available, including systems where `openat2` is unavailable.

Primary source:

* https://man7.org/linux/man-pages/man2/statx.2.html

### Path-lookup races remain an explicit concern

The Linux VFS uses mount and rename synchronization during pathname lookup, but
userspace must still treat path resolution as a concurrent state machine. The
shared helper therefore retains the rev0879 before/open/after identity check in
addition to the new kernel policy. A pre-open `fstatat(...,
AT_SYMLINK_NOFOLLOW)` proves the named component's observed type and identity;
the opened descriptor's `fstat` must match it exactly. A component changed
between observations fails rather than silently adopting the newer object.

Primary source:

* https://docs.kernel.org/filesystems/path-lookup.html

## Capability classification, not version inference

Rev0874 demonstrated why kernel-version inference is unacceptable: the running
version appeared new enough for a time-namespace interface, but the container's
configuration and procfs view did not expose it. Rev0880 follows the correction
from rev0875.

The resolution capability is a closed live observation:

* `portable-device-identity-v1`;
* `linux-statx-mount-id-v1`;
* `linux-openat2-no-xdev-v1`; or
* `linux-openat2-no-xdev-statx-mount-id-v1`.

Only an actual successful syscall and required returned mask mint a Linux
capability. `ENOSYS` is the explicit unavailable result. A successful `statx`
that omits mount-ID mask bits is also unavailable. `EINVAL`, `EPERM`, `EIO`, and
other unexpected results are not silently reinterpreted as an older safe
platform; they are fatal to capability minting. This is conservative: a
seccomp profile that returns `EPERM` can reduce liveness even when the portable
fallback would be possible. The current policy deliberately refuses to confuse
"kernel does not implement this interface" with "the process policy or calling
contract is contradictory." A future typed capability observation could model
policy-denied support separately if deployments require graceful downgrade.

The capability is frozen in the live root authority. Every reproof probes again
and requires exact equality. A running authority cannot silently lose
`openat2`, gain a differently interpreted `statx` identity, or downgrade to
`st_dev` after a sandbox transition.

## Why mount ID is not in the durable root-attestation digest

The root's structural attestation digest remains version 1 and includes device,
inode, credentials, permission mode, filesystem identity, mount flags, name
limits, and path-name limit. It intentionally excludes the live resolution
capability and mount ID.

That exclusion is necessary for the current restart contract:

* mount IDs are runtime and namespace observations;
* the older ID can be reused after unmount;
* even the extended unique ID is scoped to one running system lifetime;
* kernel capability can differ after reboot, container replacement, header
  change, seccomp change, or deployment migration; and
* placing ephemeral values in the existing SQLite root digest would make an
  ordinary reboot indistinguishable from an unauthorized root change.

This is also a real limitation, not a free compatibility choice. A live owner
will detect a root path rebound to a different mount object. After process or
machine restart, a bind mount of the exact same underlying directory can have
the same durable structural attestation but a new mount ID. Rev0880 does not
claim durable mount-object identity across restart.

A stronger future protocol should persist a typed runtime binding such as
`boot-id + STATX_MNT_ID_UNIQUE`, distinguish same-boot restart from new-boot
restart, and require an explicit root-rebind transition when the runtime epoch
changes. That transition must be authorized by exact prior root state and must
not rewrite historical effect receipts. Merely adding the current mount ID to
an unversioned digest would create an availability failure and an ambiguous
migration, not durable authority.

## Shared POSIX component-resolution owner

Before this revision, three component loops independently implemented variants
of the same security boundary:

1. absolute traversal in `SyncDirectoryAuthority`;
2. descriptor-relative descendant traversal in rooted atomic publication; and
3. absolute parent traversal in legacy atomic publication.

Each loop had its own flags, error wording, symlink checks, identity comparison,
close behavior, and future mount-policy insertion point. This duplication was
already costly: hardening only the rooted path would leave root reproof and the
legacy absolute path on subtly different race semantics.

Rev0880 introduces:

* `src/sync_posix_directory_resolution.hpp`; and
* `src/sync_posix_directory_resolution.cpp`.

The leaf owns:

* filesystem-root descriptor acquisition;
* component spelling validation;
* `fstatat(..., AT_SYMLINK_NOFOLLOW)` preinspection;
* symlink and non-directory rejection;
* `openat2` policy selection or portable `openat` fallback;
* bounded `EAGAIN` retry;
* close-on-exec setup;
* post-open `fstat` and exact device/inode comparison;
* `statx` mount identity capture and comparison; and
* exception-safe ownership of every intermediate descriptor.

Callers retain policy that belongs to their domain. Rooted publication still
checks effective-user ownership, owner read/write/search, and group/other write
bits. Absolute compatibility traversal still permits mount crossings. The leaf
therefore centralizes syscall semantics without collapsing distinct authority
contracts into one permissive helper.

### Remaining traversal inventory

A source inventory still finds direct `openat`/`fstatat` use in:

* `src/persistence/local_jsonl_replay_namespace.cpp`; and
* `src/sqlite_path_security.cpp`.

Those are not hidden copies of the refactored directory-component loop.
`local_jsonl_replay_namespace.cpp` opens named regular members, lock files, and
journal pairs under an already authorized directory and binds filename-to-file
identity. `sqlite_path_security.cpp` additionally creates missing parent
components and owns SQLite-family member and lock-file rules. Moving them into a
directory-only helper without first extracting their creation/member contracts
would erase important distinctions.

They remain candidates for a later two-layer refactor:

1. a shared no-follow directory-component resolver; and
2. separate regular-member/create policies for JSONL and SQLite.

The current revision stops where semantics stop matching.

## Descriptor leak corrected

The atomic publication adapter must duplicate the retained root descriptor and
then re-prove the authority after duplication. This post-duplication proof
closes the interval in which the path or retained observations could change
around `dup`.

Rev0879 transferred ownership of the duplicate only after that proof. If the
proof threw, no RAII owner had yet acquired the descriptor. Every rejected
traversal could therefore leak one descriptor. Repeated contradictions could
turn a correctness rejection into process-wide descriptor exhaustion.

Rev0880 closes the duplicate in the catch path before rethrowing. The ordering is
now:

```text
verify authority
→ duplicate descriptor with close-on-exec
→ verify authority again
→ on failure, close duplicate and rethrow
→ on success, transfer descriptor + frozen mount capability to caller
```

This is a contained resource-ownership fix, but it matters to authority:
resource exhaustion must not become an attacker-controlled side effect of
asking the system to reject stale evidence.

## Runtime evidence

The focused C++ test covers a deterministic classifier matrix and live syscall
behavior:

* successful `openat2` classification;
* `ENOSYS` explicit unavailability;
* fatal `EINVAL`, `EPERM`, and `EIO` classifications;
* successful `statx` with required mount-ID mask;
* successful `statx` without the mask as unavailable;
* `ENOSYS` unavailability and unexpected failure;
* canonical capability naming;
* mount-identity capture and repeated identity-kind/value stability;
* ordinary same-mount directory traversal;
* symlink rejection;
* `..` rejection;
* capability transfer through move-only `SyncDirectoryAuthority` ownership;
* live authority reproof; and
* rejection of `/proc/bus` when the host supplies the same-`st_dev` mount witness.

The existing atomic publication test remains the regression oracle for both
rooted and absolute callers after the traversal refactor. The root-authority,
local-JSONL, thread-incarnation, file-effect, and complete CTest lanes remain
required before packaging.

The source audit is intentionally lexical hygiene. It checks that the reviewed
ownership and test surfaces remain wired, but it cannot prove kernel behavior,
control flow, race freedom, or absence of undefined behavior. Runtime tests,
sanitizers, compiler warnings, and package verification remain separate gates.

## Speculation and next corrections

### 1. Durable boot-epoch root binding

Persist a typed boot observation together with `STATX_MNT_ID_UNIQUE` when
available. On restart in the same boot, require exact mount identity. Across a
new boot, require an explicit root-rebind state transition that checks durable
structural attestation, operator policy, and the previous complete effect
cutpoint. Do not mutate historical receipt identity.

Linux exposes a boot ID through procfs on common deployments, but any design
must classify actual observability rather than infer it from Linux version.
Containers may virtualize or hide that source.

### 2. Explicit mount allowlists

Some deployments may intentionally store effects on child mounts. A boolean
`NO_XDEV` policy cannot express that. A future policy could bind an ordered set
of authorized mount capabilities to path prefixes. On Linux, extended mount IDs
could name the live set; on restart, the set would require an epoch transition.
The default should remain no crossing.

### 3. Richer new mount API observations

Current Linux exposes newer mount-introspection calls including `statmount(2)`
and `listmount(2)`. They may eventually provide mount attributes, namespace
identity, propagation, and peer-group observations useful for diagnosing why a
root changed. `open_tree(2)` can clone or obtain a mount object and
`move_mount(2)` can attach it. These interfaces are newer, privilege-sensitive,
and not a reason to weaken the current descriptor fence.

Primary sources:

* https://man7.org/linux/man-pages/man2/statmount.2.html
* https://man7.org/linux/man-pages/man2/listmount.2.html
* https://man7.org/linux/man-pages/man2/open_tree.2.html
* https://man7.org/linux/man-pages/man2/move_mount.2.html
* https://man7.org/linux/man-pages/man7/mount_namespaces.7.html

### 4. Fault-injected descriptor ownership

The leak fix is structurally small but deserves a deterministic injected-failure
seam. A future test-only syscall adapter could force the second authority proof
to fail after a successful duplication and compare `/proc/self/fd` counts before
and after thousands of attempts. That adapter should not become a production
virtual syscall abstraction unless it also preserves exact errno and ownership
semantics.

### 5. Indexed production owner

The largest architectural gap remains unchanged: the new causal, channel,
effect, and filesystem authorities are correctness islands and are not the
shipped executable's main path. Further micro-hardening can become wasteful if
it does not lead to one runnable replica service. The next product milestone
should compose the existing owners into one executable endpoint while retaining
the O(history) owners as differential, repair, and migration oracles.

## Severe and wasteful patterns found

### Corrected: same-device mount crossing

Severity: high for deployments where the mount namespace can change beneath the
service. Rev0879's wording already disclosed this nonclaim. Rev0880 closes it
when either `openat2` no-cross-mount resolution or `statx` mount identity is
observably available.

### Corrected: post-duplication descriptor leak

Severity: medium, potentially high under repeated adversarial contradictions.
The failure path now closes the untransferred descriptor.

### Corrected: three directory-component state machines

Severity: maintenance and assurance waste. One security correction previously
required synchronized edits across three loops. The shared leaf now owns the
common syscall protocol.

### Not corrected: exact same-root bind replacement across restart

Severity depends on the local threat model. Live replacement is detected;
restart-stable mount-object identity is not claimed. A boot-epoch/root-rebind
protocol is required.

### Not corrected: privilege and same-UID exclusivity

A process with `CAP_SYS_ADMIN`, a same-UID process able to mutate authorized
directories, or a fully compromised process can exceed this proof. The retained
root is domain authority within the process, not an OS sandbox.

### Not corrected: service integration

The most serious delivery waste remains the gap between heavily tested owners
and the shipped `anonsync_core` path. Rev0880 should be treated as completion of
one filesystem boundary needed by that service, not as a substitute for
integration.

## Compatibility

* File-effect SQLite exact schema remains version 2.
* Causal SQLite remains schema version 5.
* File-delivery wire protocol remains version 1.
* Directory-attestation digest remains `anonsync-sync-directory-attestation-v1`.
* POSIX systems without observed Linux support retain portable behavior.
* Windows behavior is unchanged and receives no mount-ID parity claim.
* No automatic root-rebind or schema migration is introduced.

## Deliberate nonclaims

Rev0880 does not claim:

* mount-namespace containment;
* protection from `CAP_SYS_ADMIN`, root, or arbitrary in-process code;
* same-UID process exclusivity;
* restart-stable mount-object identity;
* rejection of same-device mounts on the portable fallback;
* an authorized root-rebind or boot-epoch migration protocol;
* Windows retained-root or mount-boundary parity;
* formal verification of VFS races;
* cross-database/filesystem atomicity;
* a shipped production replica service;
* production-scale incremental indexing;
* update, rename, deletion, or tombstone effects;
* complete retry, dead-letter, quota, compaction, membership, or key lifecycle;
* anonymity, unlinkability, endpoint hiding, or traffic-analysis resistance; or
* externally trusted signed provenance.

The revision claims a narrower result: when the running POSIX environment
observably supplies the Linux primitives, descriptor-relative rooted File
publication rejects same-device mount crossings and re-proves the exact live
capability; all callers share one exception-safe component-resolution owner.
