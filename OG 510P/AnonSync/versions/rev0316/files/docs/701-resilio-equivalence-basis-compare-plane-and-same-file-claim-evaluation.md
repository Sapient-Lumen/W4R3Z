# Resilio equivalence-basis, compare-plane, and same-file-claim evaluation

## Why this pass exists

The archive already had strong doctrine for pre-seeded reuse, timestamp authority, permission planes, metadata carriage, and portability.
What it still lacked was one direct evaluation for a sharper seam:

> when the product says `already synced`, `same file`, `up to date`, or `needs sync`, which properties are actually in the comparison contract right now, and which have been silently removed, deferred, or narrowed?

Current official Resilio docs make this seam much sharper than a generic `fast sync` story.
Across current pre-seeded guidance, file-properties reference, permission docs, and troubleshooting notes they still say all of the following:

- for pre-seeded folders, the Agent decides whether a file needs syncing by looking at four attributes: creation timestamp, modification timestamp, size, and file permissions
- that same current guide still says the creation timestamp can be removed from the equation with a profile parameter
- it also still says disabling NTFS or POSIX permission synchronization can remove file permissions from the equation
- current file-properties docs still say the synchronized / optionally synchronized / not synchronized properties differ by operating system and version, including content, name, modification time, creation time, execute permission, bundle xattr, Finder labels/comments, alternate streams, and POSIX/NTFS permission planes
- current permission docs still say permission-sync mode is a real job-profile choice and, for Synchronization / Hybrid Work / File Caching jobs, is fixed when the job is created
- those same permission docs still say permissions may be preserved on incompatible storage and only applied later on compatible NTFS or POSIX storage
- current `My files don't sync` guidance still says xattrs can fail to sync across mixed systems and that disabling them can cause bundle-like macOS objects to sync as ordinary subdirectories
- the current Sync v3 help-center line still runs through `3.1.2.1076`

That is very useful candor.
It is also a strong reason not to clone the page contract.

## What Resilio gets right

### 1) It admits that sameness is not one bit

Current docs do not pretend one universal comparison rule exists.
They still show that `needs sync` can depend on a quick attribute gate, later hash proof, permission-mode policy, and metadata-plane policy.
That honesty is worth borrowing.

### 2) It admits that the compare plane can change

Current docs still say creation time can be taken out of the equation and permission sync can remove permissions from it.
That means the product is not just comparing files; it is comparing them under a mutable policy basis.

### 3) It admits that some properties are carried, some are optional, and some are not synchronized at all

The file-properties reference is especially useful because it refuses to flatten all file properties into a vague `metadata` bucket.
It still distinguishes hard guarantees, optional planes, and non-synchronized properties by OS family.

### 4) It admits that a seat may carry a property plane without applying it natively

Current permission docs still say permissions can be preserved on incompatible storage and only applied later when a compatible substrate is reached.
That matters because `same access` and `same file` are not the same sentence.

## Why this is still a strong reason not to clone them

The ordinary operator answer is still too fragmented.
Current official docs still make one plain question span several article families:

- what properties currently decide `needs sync` for this subject?
- which of those properties are merely compared quickly versus fully proven later by hashing?
- which properties are actually synchronized to all seats, which are optional, and which are only preserved for later application?
- when the product says `same file`, does it mean content-equal, compare-plane equal, or merely quiet under the current attribute gate?
- what changed in that answer when a policy toggle removed creation time, permissions, or xattr carriage from the effective contract?

That should not require reading pre-seeded guidance, file-properties reference, permission docs, and troubleshooting notes together.

## The tighter AnonSync conclusion

AnonSync should borrow the following from current Resilio more boldly:

- explicit candor that equality and `needs sync` are policy-bearing judgments rather than eternal facts
- explicit candor that the compare plane differs by platform, subject profile, and enabled property planes
- explicit candor that some seats preserve later-apply properties without being able to prove native parity right now
- explicit candor that bundle/object fidelity can narrow when optional metadata planes are removed

But AnonSync should refuse the exact page contract whenever one ordinary answer still depends on several documents.
The product should not let `same file`, `already synced`, `up to date`, or `nothing to do` stand without one owned surface that states:

- effective comparison basis now
- optional planes currently in or out of the equation
- proof strength reached so far
- later-apply versus native-apply ceiling
- strongest safe sentence and stronger forbidden sentence

## Replacement pages added for this seam

This pass therefore adds four more page-shaped obligations:

1. **Equality posture** — what properties currently define the effective sameness contract for this subject and seat.
2. **Candidate equivalence review** — how two candidate objects compare, which mismatches matter, and what stronger proof is still required.
3. **Equality evidence** — what proof classes have actually been established across quick attributes, hashes, and optional planes.
4. **Equivalence receipt** — what the product concluded, which properties were in scope, and what stronger claim remained unsupported.

## Bottom line

The tighter no-clone reason is now this:

> Resilio is current evidence that compare planes, property carriage, and `needs sync` decisions are real product semantics; it is also current evidence that the ordinary operator answer about `what counts as the same file here?` still leaks across pre-seeded guidance, property tables, permission modes, and troubleshooting notes. AnonSync should copy the candor and refuse the scattered equality contract.
