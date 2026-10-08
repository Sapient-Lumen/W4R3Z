# Resilio semantic tradeoffs and hidden optimization evaluation

## Why this pass matters

Current official Resilio Sync docs are unusually candid about several semantic tradeoffs that many products hide.
They still say all of the following:

- read-only peers suspend synchronization for files they changed locally unless `Overwrite any changed files` is enabled
- that overwrite option is potentially destructive, restores deleted files, re-downloads the old name after a rename, and leaves added files in place without syncing them
- the same overwrite option is disabled for read-only folders with Selective Sync ON
- placeholder deletion can mean `revert locally to placeholder` or `remove permanently from all peers`, depending on access class and action path
- a power-user preference can prevent placeholder deletion from propagating destruction by recreating placeholders on removal
- `lazy_indexing` can defer hashing until requested, which means a remote placeholder rename will not rename the source peer's file accordingly
- `prioritize_initial_indexing` can intentionally delay syncing on pre-seeded folders until peers finish rescanning
- `direct_torrent_enabled` speeds some small transfers by not breaking files into pieces, but interrupted transfers then restart from the beginning

These are not cosmetic support notes.
They describe one load-bearing truth family: **semantic tradeoff visibility**.

Resilio still has good product substance here.
It is honest that convenience can be destructive, that placeholder actions are not all the same, that some semantic operations need hashing/readiness before they behave well, and that some transfer fastpaths accept worse interruption behavior.

But that honesty is still spread across:

- the read-only / one-way sync FAQ
- Folder Preferences
- the RSLS / placeholder article
- the power-user preferences table
- the internal-tasks warning page

That is a concrete reason not to clone the page contract.

## What Resilio gets right

### 1) It admits read-only is not semantically trivial

Current docs still say a read-only peer can make local changes, that changed files can stop syncing for that peer, and that `Overwrite any changed files` can restore deleted content, re-download renamed content under the old name, and revert edited content.
That is useful honesty.

### 2) It admits placeholder removal is a meaning fork

Current docs still distinguish local revert-to-placeholder from remove-from-all-devices and explicitly warn that deleting a placeholder with read-write access can remove it permanently from all peers.
That is again useful honesty.

### 3) It admits readiness work changes visible behavior

Current docs still say background tasks include block checking, hashing, merge, scan, dedup copy, and read/write work, and that some power-user preferences intentionally defer hashing or hold back syncing on pre-seeded folders until rescans complete.
That is real operator truth.

### 4) It admits some speed paths worsen interruption recovery

Current docs still say `direct_torrent_enabled` can speed small-file transfer by avoiding pieces, but an interrupted transfer then restarts from the beginning.
That is the sort of tradeoff products often hide completely.

## Why we still should not clone it

The core problem is not lack of truth.
The core problem is **where the truth lives**.

Resilio still makes the operator reconstruct one ordinary answer from several separate article families:

- *if this read-only seat drifts locally, what exactly gets suspended, restored, or preserved?*
- *if I delete this placeholder here, is that a local eviction or global destruction?*
- *is this subject actually ready for rename/dedup/semantic operations yet, or is hashing still deferred?*
- *did I just opt into a faster transfer method that will restart from zero if interrupted?*

Those should not be support-article questions.
They should be ordinary product pages.

## The AnonSync borrow line

Borrow from current Resilio:

- explicit candor that read-only overwrite policy can be destructive
- explicit distinction between local placeholder eviction and all-devices delete
- explicit acknowledgement that hashing/readiness gates can delay semantic correctness and visible progress
- explicit acknowledgement that some fast transfer paths sacrifice resume behavior

Adapt into AnonSync:

- one first-class page for **read-only divergence policy**
- one first-class page for **placeholder removal semantics**
- one first-class page for **hash readiness**
- one first-class page for **transfer method**

Refuse to clone from Resilio:

- FAQ-only ownership of read-only overwrite truth
- file-browser-gesture-plus-power-user-toggle ownership of placeholder destruction guardrails
- warning-page-plus-advanced-setting ownership of deferred readiness
- toggle-only ownership of transfer fastpath versus resume sacrifice

## Resulting interface obligations for this revision

This revision therefore adds four replacement page contracts:

1. `329-read-only-divergence-page-suspension-overwrite-and-added-file-fate-interface-spec.md`
2. `330-placeholder-removal-page-local-evict-global-delete-and-guardrail-policy-interface-spec.md`
3. `331-hash-readiness-page-deferred-indexing-placeholder-rename-and-preseed-gate-interface-spec.md`
4. `332-transfer-method-page-piecewise-resume-direct-fastpath-and-interruption-cost-interface-spec.md`

These pages make one ordinary promise explicit:

> An operator should never have to stitch together semantic tradeoff truth from a FAQ, a folder preference, a hidden power-user toggle, a file-browser gesture, and a background-task warning before touching real bytes.
