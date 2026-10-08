# Resilio portable-name collision, alias propagation, and move-scope fragmentation evaluation

## Why this seam matters now

Current official Resilio docs still expose a sharp but fragmented naming contract.
They separately say:

- `.Conflict` artifacts can appear when peers disagree only by letter case or encoding, and the operator should not simply delete those conflict files.
- invalid trailing-asterisk names can be misread as system data and disrupt syncing.
- filenames are expected to be UTF-8 and path-length ceilings differ by platform.
- a synced folder rename is local-only, and moving across partitions on Windows or Mac stops being an ordinary move.
- a desktop share can have a custom UI name that does not rename the folder on disk and does not propagate to other peers.
- a file rename can be archive-assisted instead of retransmitted if the old hash is still available.
- symlink support differs materially by platform, and on Unix a synced symlink does not imply its target tree is in scope.

That is valuable candor.
It is also a strong non-clone signal.
The ordinary operator question is not just `why did I get a conflict file?`.
It is:

> what exactly changed here — disk name, UI name, portable artifact label, local mount path, canonical portable rendering, or only a pointer edge — and can every target actually carry that meaning?

Current Resilio material still makes the operator reconstruct that answer from multiple articles instead of one product-owned page family.

## The non-clone reason, tightened

AnonSync should borrow Resilio's willingness to admit that names are not one flat thing.
AnonSync should refuse the present contract shape where the operator must merge:

- conflict repair lore,
- unsupported-name troubleshooting,
- local-only folder rename behavior,
- UI-only custom share naming,
- archive-assisted rename semantics, and
- platform-specific alias-edge limits

to answer one practical question:

> **what name changed, where does it propagate, and what portable canonical form can survive across peers and filesystems?**

So the harder product stance for this pass becomes explicit:

> **AnonSync is not cloning Resilio because the useful distinctions between canonical portable name, local disk name, presented label, artifact alias, local-only move/rename scope, archive-assisted reuse, and alias-edge target scope are real, but the present contract still hides too much meaning across conflict, troubleshooting, naming, move/rename, and symlink articles instead of owning portable-name truth as one stable page family.**

## Product decisions locked by this evaluation

### 1) Path existence is weaker than portable-name admissibility

A name that exists locally may still be inadmissible for the intended audience because of case-fold collisions, encoding drift, invalid symbols, path-budget overflow, reserved-name classes, or alias-edge boundaries.

### 2) Presented names and disk names are different planes

A local subject can simultaneously have:

- a disk basename,
- a local UI title,
- a portable artifact label,
- and a peer-visible canonical name.

Changing one plane must not imply the others changed.

### 3) Local-only move/rename scope must be explicit

If a folder rename changes only the local seat, the interface must say so before commit.
If a move crosses a root or partition boundary and becomes rebind-like rather than move-like, the interface must say so before commit.

### 4) Byte reuse and rename scope are different truths

`Rename` is not one performance class.
The contract must separately state:

- whether the rename is local-only,
- whether peers will observe a new name,
- whether existing bytes will be reused,
- and whether that reuse depends on retention/archive posture.

### 5) Alias edges are not names

Symlink/junction/hardlink behavior is topology, not labeling.
A preserved symlink object is not equivalent to syncing the target tree.
That boundary must be made explicit wherever a rename or portability review could be confused by link-like entries.

## Required AnonSync page family from this pass

This evaluation requires one stable page family:

1. **Portable-name contract sheet**
2. **Canonical-name portability review**
3. **Name-plane propagation review**
4. **Rename-scope and byte-reuse proof**
5. **Portable-name lineage receipt**

The purpose of the family is to let an operator answer, on one path:

- what canonical portable rendering is in play,
- what name planes currently exist,
- which of them the requested mutation touches,
- what target portability class blocks or narrows the change,
- whether byte reuse depends on archive/retention,
- and what stronger sentence was refused.

## What AnonSync should borrow vs refuse

### Borrow from current Resilio

- candor that case/encoding differences can produce real collisions
- candor that invalid names and path limits are operational, not cosmetic
- candor that local folder rename and UI renaming are not the same thing
- candor that archive can make a rename materially cheaper than replay
- candor that alias edges have platform-specific support ceilings

### Refuse from current Resilio

- conflict suffixes as the first serious portability teaching moment
- article archaeology to discover which name plane actually changed
- move/rename language that hides local-only scope until after apply
- alias-edge caveats that remain detached from name and move review
- missing durable receipt for canonicalization, blocked propagation, or rewrite refusal

## Interface consequence

Every serious naming action in AnonSync now needs to answer five questions in public:

1. **What exact canonical portable rendering is proposed?**
2. **Which name plane is being changed?**
3. **Who will observe the change?**
4. **Will the target filesystem and target peers carry it without collision?**
5. **Is byte reuse guaranteed, conditional, or unavailable?**

If the interface cannot answer all five without sending the operator into support prose, it still fails the non-clone bar.

