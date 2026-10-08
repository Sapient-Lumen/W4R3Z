# Resilio local mutability ceiling, write barriers, and host-write-lane fragmentation evaluation

## Why this pass exists

The archive already had stronger doctrine for action surfaces, governance planes, seat posture, effect direction, path liveness, service-principal switches, locked-file retries, and storage/presence truth.
What it still lacked was one direct current Resilio evaluation for a narrower but important question:

> can this runtime actually mutate bytes here now, by what grant, through what host/API lane, against what lock model, and what stronger write sentence is still blocked?

Current official Resilio docs still show a useful, living product, but they also still show that one ordinary answer is spread across several article families at once:

- `Locked files`
- `My files don't sync`
- `Sync and SMB file shares`
- `Permissions Sync requires on Android and Amazon Kindle`
- `SD card gimmicks on Android`
- `Synology`
- `Sync Service Troubleshooting on Windows`
- `Power user preferences`

## Current official Resilio evidence that matters here

Current official docs still say all of the following:

- `Locked files` still says another application can block access to files, making transfer impossible, and that Sync cannot identify the locking application for you.
- `Power user preferences` still says `recheck_locked_files_interval` governs later retry of locked files, which means a lock barrier and its re-evaluation policy are separate truths.
- `My files don't sync` still lists multiple non-equivalent local write blockers together: files locked by apps or security tools, destination peer lacking read-write access to files and directory, file-system errors that make Sync abandon syncing, and bad / unmounted drives.
- `Sync and SMB file shares` still says SMB locks resemble local locks, and also warns that a common NAS pattern—Sync touching the files directly while other users access them through SMB—can roll back third-party changes or damage files.
- `Permissions Sync requires on Android and Amazon Kindle` still says Android storage permission is what allows Sync to write received files and apply changes.
- `SD card gimmicks on Android` still says SD-card write access depends on granting root access through the provider API, warns that walking to the SD path through an ordinary picker does not grant that access, and says Sync cannot create a new backup folder on SD card through that lane.
- `Synology` still says the internal `rslsync` user needs explicit read/write permission on the NAS shared folder.
- `Sync Service Troubleshooting on Windows` still says a service running as one user may lack permission to write some folders, that switching to Local System changes the effective storage world, and that old folders then have to be re-added / re-shared.

So current Resilio still contains a real but scattered answer to `can bytes be mutated here now, and if not, is the blocker a lock, missing grant, wrong principal, unsafe host lane, mount trouble, or a colder retry debt?`

## What Resilio still gets right

### 1) It is candid that local write failure has more than one cause

The docs do not pretend that every failure is just `permissions`.
They openly describe app-level locks, OS/API grants, NAS account rights, service-principal mismatch, SMB interaction hazards, and filesystem / mount trouble.
That honesty is valuable.

### 2) It is candid that a visible path is weaker than a writable path

The docs still say that merely seeing a path or choosing a path is not enough on Android SD storage, SMB shares, Windows service accounts, or NAS shares.
That matters.

### 3) It is candid that host lane matters, not just folder identity

The docs still warn that direct local access and SMB access are not one write lane, and that mixing them can damage or roll back data.
That is exactly the sort of operational truth worth borrowing.

## Why this is still a good reason not to clone them

### 1) Current docs still collapse too many barriers into generic sync trouble

An operator still has to merge multiple articles to answer:

- is the byte barrier a lock, a missing OS/API grant, a missing filesystem permission, a wrong service principal, a mount problem, or an unsafe mixed-access lane?
- can the runtime write *anything* here, or only through a different lane?
- is the barrier expected to clear on retry, or does it require a stronger host/world change?

AnonSync should not inherit a contract where `cannot sync` must silently carry all of that.

### 2) Safe host-write lane is still under-modeled

Current Resilio still warns about Sync-on-NAS plus outside-SMB access as a corruption / rollback risk, but that truth is isolated in one article instead of living as a first-class contract object.
A serious sync product should not let `folder is on SMB` impersonate `write lane is safe for concurrent authority`.

### 3) Grant plane and principal plane are still too easy to confuse

Current docs still distribute Android storage grants, SD provider grants, NAS `rslsync` account rights, and Windows service-user rights across separate pages.
That is too much archaeology for such a load-bearing truth.

## What AnonSync should do instead

AnonSync should make **local mutability ceiling** first-class.
Every meaningful local-write sentence needs one stable answer for:

- write grant class
- active principal / actor
- host write lane
- lock barrier state
- filesystem health / mount state
- retry or restart rung
- next strongest safe sentence

The product should never let `connected`, `synced`, `has folder path`, or `permission looks fine` blur into one vague writeability story.

## Hard decisions now locked

1. **Local mutability ceiling is first-class.**
   Every serious write attempt must name whether it is blocked by lock, grant, principal, host lane, filesystem health, or unknown.

2. **Write grant, active principal, and safe host lane are different truths.**
   A runtime may have a path but not a valid grant; it may have a grant but the wrong principal; it may have both and still be in an unsafe mixed-access lane.

3. **Visible path is weaker than writable path.**
   Seeing a folder in UI or on disk must never imply mutation authority.

4. **Retryable lock debt stays visibly weaker than writable-now.**
   `will recheck later` is not the same as `writeable now`.

5. **Unsafe mixed-access lane stays visibly weaker than healthy write authority.**
   If the product knows that the current host lane risks rollback or corruption, it must say so directly.

## What this tranche adds to the archive

This revision adds five more first-class pages:

- **Local-mutability contract sheet**
- **Write-barrier review**
- **Write-authority proof**
- **Mutability-ceiling timeline**
- **Local-mutability lineage receipt**

Together they let AnonSync answer one ordinary operator question without archaeology:

> can this runtime actually mutate bytes here now, what is the real blocker if not, and what stronger write sentence is still blocked?
