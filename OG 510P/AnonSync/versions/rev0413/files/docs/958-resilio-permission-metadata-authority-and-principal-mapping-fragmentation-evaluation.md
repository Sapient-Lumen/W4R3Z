# Resilio permission metadata authority, principal mapping, and apply-ceiling fragmentation evaluation

## Why this seam matters

The archive already has strong doctrine for **birth commitments**, **policy provenance**, **shared substrate truth**, **runtime identity**, and **repair ladders**.
What it still lacked was one direct evaluation for another ordinary operator question:

> when the product says it is synchronizing permissions too, what exactly is part of subject truth, under which runtime principal and identity-mapping assumptions, and when is the honest answer only `preserved`, `best effort`, or `cannot be applied here`?

Current official Resilio documentation makes this seam sharper than a generic `ACLs are hard` disclaimer.
Across the current Active Everywhere documentation they still say all of the following:

- permission synchronization is a real first-class feature, including Standard and Special NTFS permissions as well as POSIX.1 permissions
- for Synchronization, Hybrid Work, and File Caching jobs, the permission-sync settings are applied when the Job is created and cannot be changed later
- NTFS permission synchronization has materially different modes, including `Don't sync Owner`, `Sync full ACL`, and `Re-apply local inherited permissions`
- the runtime principal matters: synchronizing NTFS permissions requires Local System or a local administrator, while full-owner application requires Domain Admin in same-domain cases
- cross-platform compatibility matters: systems that cannot apply the replicated permission structure should not be grouped casually, and non-NTFS targets may only preserve NTFS permissions until the file later reaches NTFS storage
- pre-seeded read-write to read-write synchronization can scramble ownership unless a Reference Agent is chosen
- concrete troubleshooting guidance still says permission-sync failures can reduce to `not enough privileges` or missing user/group identity mapping on the target

That is useful candor.
It is also a good reason not to clone the page contract.

## What Resilio gets right

### 1) It treats permission metadata as real, not decorative

Current docs do not pretend that byte transfer alone is the whole subject.
They are explicit that ownership, ACLs, and POSIX permissions can matter enough to configure and troubleshoot directly.

### 2) It admits that metadata truth has a different ceiling than byte truth

A file can arrive while permission truth remains conditional.
Some targets can preserve metadata without applying it immediately.
Some principals can carry one mode but not another.
That is a valuable distinction.

### 3) It admits that principal and namespace assumptions matter

The same nominal `sync permissions` choice can require:

- Local System
- local administrator
- Domain Admin
- same-domain reachability
- same user or group ID / name on the target
- a deliberate Reference Agent for pre-seeded bi-directional merges

Those are real operator constraints.

## Why AnonSync still should not clone it

One ordinary operator question is still fragmented:

> are permissions actually part of the truth for this subject here, and what exactly would have to be true on this runtime and this target for that promise to hold?

In current Resilio, that answer can still depend on hopping across:

- the permission-sync feature article
- job-creation pages
- job-profile settings
- troubleshooting errors
- runtime principal guidance
- storage / cross-platform caveats

That is too much archaeology for a question that can decide whether a cutover is safe.

## Hard decisions for AnonSync

1. **Byte truth and metadata truth are separate axes.** `File arrived` must not silently imply `permissions matched`.
2. **Permission metadata gets a first-class authority class.** The product must say whether the current posture is `apply-and-enforce`, `preserve-for-later-application`, `local-inherit-rewrite`, `bytes-only`, or `blocked`.
3. **Runtime principal is part of the contract.** Service account, domain posture, and mapping compatibility must be visible before apply.
4. **Cross-platform preservation and local application are different verbs.** Preserving NTFS ACL intent on a non-NTFS path is not the same claim as applying it there.
5. **Permission failures get a real review surface.** The operator should not have to infer from one error code whether the safe fix is principal change, identity mapping repair, policy downgrade, or bytes-only continuation.
6. **Receipts preserve metadata ceiling.** Later audits must still show whether permission truth was fully applied, only preserved, rewritten to local inheritance, or deliberately omitted.

## Interface family implied by this evaluation

This pass therefore adds five more page-shaped obligations:

1. **Metadata authority contract sheet**
2. **Permission sync review**
3. **Principal mapping proof**
4. **Permission failure review**
5. **Metadata lineage receipt**

## Bottom line

The tighter no-clone reason is now this:

> current Resilio docs are good evidence that permission metadata is operationally real and that runtime principal / identity mapping materially change what can honestly be promised; they are also good evidence that the ordinary operator answer about `are permissions part of truth here or not?` still leaks across several documents instead of one stable product-owned contract.
