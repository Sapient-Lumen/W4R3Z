# Resilio permission-plane, reference-agent, and inheritance-rewrite evaluation

## Why this pass exists

The archive already had strong doctrine for **path writability**, **platform permission prompts**, **xattr/attribute planes**, and **copy-carry hidden state**.
What it still lacked was one direct evaluation for a different but equally sharp question:

> when the product says it will `sync permissions`, what is actually being synchronized, who is authoritative, where do those permissions really apply, and what happens when the local substrate cannot represent them directly?

Current official Resilio docs make this seam much sharper than a simple `preserve ACLs` claim.
They still say all of the following:

- permission synchronization is controlled by job-profile modes, not one universal behavior
- for Synchronization, Hybrid Work, and File Caching jobs, those permission-sync settings are applied when the job is created and cannot be changed later
- NTFS modes still include `Don't sync Owner`, `Sync full ACL`, and `Re-apply local inherited permissions`
- the `Re-apply local inherited permissions` mode exists specifically because partial downloads are written through the service `.sync` directory and would otherwise inherit the wrong local permissions
- NTFS permissions can be preserved on non-NTFS storage and only applied later when the file reaches NTFS storage
- POSIX permissions can likewise be preserved on non-POSIX storage and only applied later when the file reaches a POSIX-compatible filesystem
- syncing NTFS permissions still requires the agent to run as local administrator or Local System, while syncing POSIX permissions requires root
- over SMB, the service account still needs Read, Change permissions, and Take ownership rights for permission sync to work correctly
- for bidirectional pre-seeded folders, current docs still recommend a Reference Agent because otherwise permissions from RW agents can merge into one tree and produce scrambled or randomly assigned ownership
- selecting a Reference Agent still drives an initial synchronization that disables inheritance on the sync root and overwrites local file permissions from the Reference Agent
- current pre-seeded-folder guidance still says file permissions are one of the attributes used to decide whether a file needs synchronization at all, and disabling permission sync can remove permissions from that decision equation

That is substantial operational candor.
It is also a strong reason not to clone the page contract.

## What Resilio gets right

### 1) It admits that `permission sync` is not one thing

Current docs still distinguish:

- identity-bearing ACL carriage
- owner/group propagation
- local re-inheritance instead of remote preservation
- ID-vs-name POSIX application
- deferred application on incompatible storage

That is exactly the kind of honesty sync products often blur away.

### 2) It admits that authority can come from one chosen reference seat

The Reference Agent docs are unusually candid.
They still say permission merge is not semantically neutral and that without a chosen reference seat, RW agents can produce unexpected or scrambled permissions.
That is worth borrowing.

### 3) It admits that privilege floor and substrate matter

Current docs still say local admin / Local System / root may be required, and that SMB permission syncing requires stronger service-account rights.
That makes it clear the permission plane is not just file metadata trivia.

### 4) It admits that permission truth can participate in sync decisions even before bytes move

The pre-seeded guidance still says permissions are part of the quick attribute check that determines whether a file needs syncing.
That means this plane influences divergence detection, not only final decoration.

## Why this is still a good reason not to clone them

The ordinary operator answer is still fragmented.
Current official docs still make one plain question span several article families:

- *what exact permission mode is active here?*
- *is this seat preserving remote authority, re-inheriting locally, or deferring application until a later compatible substrate?*
- *who is the reference authority if pre-seeded RW peers disagree?*
- *does this seat even have enough privilege to apply what the product is claiming?*
- *are permission mismatches participating in `needs sync` decisions right now or not?*

That should not require reading a permission article, a profiles table, a Reference Agent guide, and pre-seeded best-practice notes.

## The tighter AnonSync conclusion

AnonSync should borrow the following from current Resilio more boldly:

- explicit candor that permission carriage is a distinct meaning plane
- explicit candor that the plane has multiple modes rather than one `preserve permissions` checkbox
- explicit candor that some seats only preserve and defer, while others can actually apply
- explicit candor that a reference authority may be needed when RW peers already disagree
- explicit candor that local privilege floor and storage substrate constrain what can honestly be promised

But AnonSync should refuse the exact page contract whenever one ordinary answer still depends on scattered documents.
The product should not let `sync permissions`, `preserve ACLs`, `keep ownership`, or `same access on all peers` stand without one owned surface that states:

- current permission-plane mode
- current reference authority basis
- current application substrate
- current local privilege floor
- whether this plane participates in divergence detection
- strongest safe sentence and stronger forbidden sentence

## Replacement pages added for this seam

This pass therefore adds four more page-shaped obligations:

1. **Permission-plane posture** — what mode is active, where it applies, and what claim ceiling is honest.
2. **Permission-plane change review** — what changes if the operator narrows, widens, localizes, or re-roots permission authority.
3. **Permission-apply evidence** — what proves the reference source, inheritance rewrite, substrate-compatibility, and privilege basis.
4. **Permission-plane receipt** — what later proves the effective mode, apply result, and remaining claim ceiling.

## Bottom line

The tighter no-clone reason is now this:

> Resilio is current evidence that permission carriage, reference authority, inheritance rewrite, and deferred substrate application are real operational truths; it is also current evidence that the ordinary operator answer about `what permission contract is actually in force here?` still leaks across a mode table, a reference-agent guide, pre-seeded advice, and privilege caveats. AnonSync should copy the candor and refuse the scattered contract.
