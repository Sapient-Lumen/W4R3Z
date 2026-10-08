# Resilio clock, chronology, and mtime-authority evaluation

## Why this pass matters

Current official Resilio Sync docs are unusually candid about chronology.
They still say all of the following:

- peer clock or time-zone skew beyond the allowed window blocks transfer and raises a visible warning
- mobile devices can degrade all the way to an empty file list under the same condition
- the allowed clock-difference window is still a separate power-user preference rather than one ordinary product page
- if Sync cannot write file modification time on disk, a power-user fallback can keep the correct timestamp only in the database while the on-disk mtime becomes `current`
- ordinary multi-writer resolution still privileges the latest file that comes online, even if another peer made a later online edit chronologically
- manual Archive restore still depends on Sync already running; otherwise an extracted older version can be archived again on rescan as `older`

These are not minor support notes.
They describe one load-bearing truth family: **chronology authority**.

Resilio still has good product substance here.
It is honest that clocks matter, that offline return can trump later online edits, that restore is timing-sensitive, and that some timestamp truth can live in the database instead of on disk.

But that honesty is still spread across:

- the `Time difference` warning page
- the power-user preferences table
- the file-conflict FAQ
- the Archive restore article

That is a concrete reason not to clone the page contract.

## What Resilio gets right

### 1) It admits chronology is an operational dependency

Current official docs still say Sync compares file modification time after converting peer times to GMT and raises a warning when actual peer time difference exceeds the allowed 600-second window.
That is useful honesty.
Many products bury this completely.

### 2) It admits offline return is not the same thing as clean chronology

Current official docs still say an offline peer that later returns can override a later online edit, with overwritten versions landing in Archive.
That is again useful honesty.
It is better than pretending chronological modification time alone always wins.

### 3) It admits restore depends on runtime timing

Current official docs still say a restored file taken from Archive should be restored while Sync is running, because otherwise rescan can compare mtimes and archive the restored file again as older.
That is painful, but at least true.

### 4) It admits on-disk timestamp fidelity can fail

Current official docs still say a power-user preference can stop repeated mtime-write attempts and keep the correct timestamp only in the database, with the on-disk mtime left as the current timestamp.
That is a real operator truth, not a cosmetic detail.

## Why we still should not clone it

The core problem is not lack of truth.
The core problem is **where the truth lives**.

Resilio still makes the operator reconstruct one ordinary answer from several separate article families:

- *are peer clocks trustworthy enough to compare chronology at all?*
- *if an offline editor returns, what exactly wins and what gets preserved?*
- *is the timestamp shown by the filesystem the real authority, or only the database knows the correct answer?*
- *if I restore a file version now, will it stay restored, replay outward, or get archived again on rescan?*

Those should not be support-article questions.
They should be ordinary product pages.

## The AnonSync borrow line

Borrow from current Resilio:

- explicit clock-validity warnings
- explicit allowed-difference policy
- explicit acknowledgement that offline return can outrank later online edits
- explicit acknowledgement that restore timing affects replay outcome
- explicit acknowledgement that database truth and on-disk truth can diverge

Adapt into AnonSync:

- one first-class page for **clock authority**
- one first-class page for **offline replay review**
- one first-class page for **mtime integrity**
- one first-class page for **restore replay review**

Refuse to clone from Resilio:

- warning-page-only ownership of chronology trust
- power-user-table-only ownership of mtime-fallback truth
- FAQ-only ownership of offline-winner semantics
- Archive-article-only ownership of restore replay timing

## Resulting interface obligations for this revision

This revision therefore adds four replacement page contracts:

1. `325-clock-authority-page-peer-time-validity-and-chronology-confidence-interface-spec.md`
2. `326-offline-replay-review-page-timeline-authority-and-overwrite-risk-interface-spec.md`
3. `327-mtime-integrity-page-disk-write-failure-database-fallback-and-surface-truth-interface-spec.md`
4. `328-restore-replay-review-page-archive-extraction-rescan-risk-and-live-propagation-interface-spec.md`

These pages make one ordinary promise explicit:

> An operator should never have to stitch together chronology truth from a warning banner, a hidden advanced preference, a conflict FAQ, and a restore article before touching real bytes.
