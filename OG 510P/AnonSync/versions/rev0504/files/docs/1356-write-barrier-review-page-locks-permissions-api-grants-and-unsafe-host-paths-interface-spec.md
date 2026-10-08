# Write-barrier review page — locks, permissions, API grants, and unsafe host paths

## Review question

> which specific barrier is preventing safe local mutation, and what kind of intervention actually clears it?

## Barrier classes that must stay separate

### 1) App / OS lock barrier

Use when a file is blocked by another application, security software, encryption software, or a host-level lock.
Required fields:

- locked subject set
- whether lock owner is known or unknown
- next retry rung
- whether lock is single-file, subtree-wide, or unknown

This barrier is **retryable debt**, not permission failure.

### 2) Filesystem permission barrier

Use when the runtime principal lacks read/write access to the file or directory.
Required fields:

- active principal
- missing rights class
- whether file and directory rights both fail
- whether principal switch or ACL change is needed

This barrier is **grant/principal failure**, not merely a temporary lock.

### 3) Provider/API grant barrier

Use when mutation must pass through a provider grant surface (for example Android SD-card root grant), and path navigation alone did not grant the right API capability.
Required fields:

- required provider grant
- whether root or subtree grant is required
- whether the current selection path actually used the provider lane
- whether create-new-folder is blocked even when write access exists for existing folders

This barrier is **API-lane failure**, not classic POSIX/NTFS permissions.

### 4) Host-lane safety barrier

Use when bytes may technically be writable, but the current mixed-access pattern is known to risk rollback or corruption.
Required fields:

- lane pair in conflict
- unsafe consequence class
- safe replacement lane
- whether the current setup should be declared unfit for concurrent authority

This barrier is **unsafe authority topology**, not simple access denial.

### 5) Filesystem health / mount barrier

Use when file-system errors, missing mounts, or bad drive state make Sync abandon syncing or invalidate the path.
Required fields:

- mount / drive health class
- whether the subject still exists at the same host path
- whether fs-repair or remount is required
- whether continuity proof survives after repair

### 6) Service-world / principal boundary barrier

Use when the runtime changes principal or storage world and the new actor can write, but only after subject continuity is re-established.
Required fields:

- old runtime world
- new runtime world
- principal delta
- continuity consequence: `same-subject`, `readd-required`, `reshare-required`, `unknown`

## Review output sentence

The page must end with one sentence in this shape:

> `Current write ceiling is <barrier class>; stronger sentence <writeable-now / safe-lane / same-world continuity> is blocked because <missing proof>.`

## Things the page must refuse to say

- `permissions issue` when the barrier is actually a lock or provider grant failure
- `folder is writable` when the lane is known unsafe
- `service fix solved it` when a world shift broke continuity and folders must be re-added
- `same path means same authority` when provider grant or principal changed
