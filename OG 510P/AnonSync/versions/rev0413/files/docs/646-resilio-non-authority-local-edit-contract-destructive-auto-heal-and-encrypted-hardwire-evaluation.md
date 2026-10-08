# Resilio non-authority local-edit contract, destructive auto-heal, and encrypted hardwire evaluation

## Why this pass exists

The archive already had strong doctrine for authority, local material, severance, and recovery.
What it still lacked was one direct current Resilio evaluation for another ordinary seam:

> when this seat is not the authority for a shared subject, what exactly happens if local edits occur here — do updates freeze, do remote bytes overwrite the edit, do some local additions survive unsynced, and is that contract even available in the same way across modes and peer types?

Current official Resilio docs still show a useful, living product, but they also still show that one everyday answer still leaks across several different article families at once:

- `User Management`
- `Is one-way synchronization possible?`
- `Folder Preferences`
- `Folder Types and Management`
- `Encrypted folders`
- `Sync interface on Android` / `Sync Interface on iOS devices`
- `How to create a Read Only folder while syncing across linked devices?`

## Current official Resilio evidence that matters here

Current official docs still show an active v3 line through `3.1.2.1076`.
They also still say all of the following:

- `User Management` still says Read Only peers cannot propagate their edits and that further synchronization of files changed by a Read Only peer is suspended for that peer unless `Overwrite any changed files` is used.
- `Is one-way synchronization possible?` still spells out per-change-class behavior: with overwrite enabled, renamed files remain while the old name is re-downloaded, deleted files are restored, edited files revert to the most recent version from a RW peer, and added files are not synced back.
- `Folder Preferences` still says `Overwrite any changed files` is potentially destructive, includes locally added files, and is disabled for Read-only folders with Selective Sync ON.
- `Folder Types and Management` still says Read Only folders may allow local changes depending on local settings, but that such changes can stop the user from receiving later updates to those files.
- `Encrypted folders` still says encrypted backup peers are always Read Only, always have overwrite enabled, and do not allow Selective Sync.
- `Sync interface on Android` and `Sync Interface on iOS devices` still expose overwrite as a per-share control on mobile surfaces rather than a deeper contract page.
- `User Management`, `Is one-way synchronization possible?`, and `How to create a Read Only folder while syncing across linked devices?` still make clear that linked devices under one identity act as Owners, that Advanced folders do not offer Read Only across linked devices, and that creating a Read Only copy on one of your own devices still routes through a Standard-folder/manual-key/disconnect workflow.

So current Resilio still contains a real but scattered answer to `what kind of local edit freedom do I actually have here, and what happens to future updates if I use it?`

## What Resilio still gets right

### 1) It is candid that non-authority local edits are not one simple thing

The docs do not pretend that `Read Only` automatically means `immutable local copy`.
They admit suspension, overwrite, and special encrypted behavior.
That honesty matters.

### 2) It still publishes concrete per-change-class effects

Rename, delete, edit, and add do not all behave the same way.
Resilio's docs still say so explicitly.
That is valuable operator candor.

### 3) It still admits that some postures hardwire the policy

Encrypted peers forcing overwrite and forbidding Selective Sync is real product truth.
The docs do not hide it.

## Why this is still a good reason not to clone them

### 1) One `Read Only` badge still hides several incompatible local-edit contracts

Current docs still require the operator to reconstruct whether this share means:

- local edits freeze future updates for changed paths
- local edits are destructively auto-healed
- local additions remain as unsynced residue
- Selective Sync forbids the overwrite option
- encrypted posture forces overwrite and forbids Selective Sync

AnonSync should not inherit a single badge that carries all of that.

### 2) Destructive auto-heal still looks like an ordinary preference

Current docs are candid that `Overwrite any changed files` is destructive.
But the contract still arrives as a checkbox in per-folder preferences and mobile share details, not as a first-class review of what local edits will lose.
A serious sync product should not let destructive reversion masquerade as routine tuning.

### 3) Non-authority posture and identity posture are still mixed awkwardly

Current docs still say linked devices act as Owners, and that creating a Read Only copy on one of your own devices routes through Standard-folder/manual-key/disconnect ritual.
That means the product still lacks one clean operator-owned sentence for `this device is intentionally non-authoritative for this subject`.

### 4) Future-update continuity is still path-local but not surfaced that way

Some paths freeze, some revert, some survive local-only, and some policies cannot be toggled in some modes.
Current Resilio still makes the operator stitch that truth together from permission docs, one-way-sync docs, preferences, and encrypted-backup docs.

## The tighter AnonSync conclusion

AnonSync should borrow the following from Resilio more boldly:

- candid admission that non-authority local edit behavior is a real policy surface
- explicit per-change-class outcomes rather than one vague `read only` sentence
- explicit publication of hardwired posture limits such as encrypted/opaque backup roles

But AnonSync should refuse the exact page contract whenever one ordinary answer still depends on:

- permission folklore
- hidden per-path suspension
- destructive auto-heal disguised as a preference toggle
- identity-level owner semantics being worked around by manual Read Only detours

## The replacement pages this evaluation justifies

This pass therefore makes four page-shaped obligations concrete:

1. **Non-authority edit posture** — what local changes are allowed here, and what is their fate?
2. **Non-authority local-change review** — before a local edit or policy change, what freezes, reverts, survives locally, or must be diverted elsewhere?
3. **Affected-path continuity** — after divergence or auto-heal, which paths still receive updates, which are frozen, and why?
4. **Non-authority edit receipt** — what policy was in force, what local changes occurred or were reviewed, and what is the strongest honest sentence now?

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still good evidence that non-authority local edits need explicit policy, but it is also current evidence that one `Read Only` story can still require archaeology across permission pages, one-way-sync details, destructive preference text, encrypted exceptions, and linked-device workarounds. AnonSync should copy the candor and refuse the overloaded read-only contract.
