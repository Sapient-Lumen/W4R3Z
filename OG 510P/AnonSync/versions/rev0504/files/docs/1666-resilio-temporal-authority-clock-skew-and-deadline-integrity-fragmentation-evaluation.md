# Resilio temporal-authority, clock-skew, and deadline-integrity fragmentation evaluation

## Claim

Current official Resilio docs are still admirably candid that `file modification time`, `peer clock`, `timezone`, `approval receipt time`, `history ordering`, and `placeholder mtime` are not one flat thing.
That candor is useful.
It is also exactly why AnonSync should not clone the present contract.

The missing product object is now sharper than enactment effectivity:

> after the product knows **which typed act executed and when it should become effective**, it still needs one first-class answer to **whether the clocks and timestamp bases are trusted enough for notice deadlines, cooling windows, expiry, and reopen timing to mean what the UI says they mean**.

Current Resilio materials still do not provide one typed time-authority object for:

- trusted vs untrusted local clocks
- timezone-corrected but still stale peers
- file mtime versus action execution time
- approval-request receipt time versus notice-completion time
- cooling timers whose basis becomes suspect after clock correction
- effective timestamps that should degrade when time integrity is lost
- manually adjudicated temporal overrides after skew, offline gaps, or backdated state

Instead, the operator still has to translate warnings, internal-clock caveats, GMT normalization, and scattered timestamp behavior into deadline meaning.

## What current official docs still say

Current official docs still jointly show all of the following:

- `"Time difference" error` still says Sync compares file modification times, converts them to GMT, also converts peers' local time plus timezone to GMT, and warns once time difference exceeds 600 seconds.
- `Comprehensive guide to syncing (Desktop-Desktop)` still says Sync relies on each device's internal clock while syncing and updating files, and warns that wrong time or timezone can trigger the excessive-time-difference condition.
- `Syncing between a desktop computer and a mobile device` still repeats that correct device time and timezone are crucial while syncing and updating files.
- `Resilio Sync change log` still says placeholders keep the same modification time as real files and later also says placeholders keep mtime up to date as on real files.
- `Sync Main View (Desktop)` still says History shows general syncing activity for only the last 30 days, which is useful trace but not a durable deadline-proof object.

This is strong operational candor.
It is not a first-class time-authority contract.

## Why this still fragments the decisive answer

One ordinary fairness answer still requires stitching together several docs and surfaces:

- whether the clock basis for a cooling or expiry timer is trustworthy
- whether a file-ordering timestamp is being reused as if it were an act-effectivity timestamp
- whether a peer's timezone correction fixed the problem before or after a deadline allegedly elapsed
- whether a placeholder-preserved mtime should be trusted as temporal evidence or only as file-state continuity
- whether a later clock correction should reopen a supposedly complete cooling or notice window
- whether short-history visibility leaves a temporal proof gap even when the UI looks orderly

That means current official materials can help answer `why did Sync complain about time?`, `why does file ordering look wrong?`, or `why do placeholders preserve mtimes?`
They still do not directly answer `is this notice deadline, cooling window, expiry, or reopen timer trustworthy enough to support an irreversible fairness sentence right now?`

That gap is exactly where AnonSync should refuse cloning.

## Hard replacement line for AnonSync

AnonSync should borrow the useful ingredients:

- explicit skew warnings
- clear UTC normalization language
- visible distinction between internal clocks and file mtimes
- preservation of file-state mtimes where operationally useful
- operator-visible acknowledgement that bad clocks can break ordering

But AnonSync should replace the page contract with a first-class **time authority and deadline integrity** object where each typed act has its own:

- authoritative time basis
- skew budget
- trusted and degraded clock classes
- timer-start rule
- deadline-validity rule
- clock-correction aftermath
- adjudicated temporal override route

## Product decision tightened here

The new design line is:

- **observed timestamp is weaker than trusted deadline basis**
- **local clock time, normalized UTC time, file mtime, receipt time, notice-completion time, cooling-start time, and effective time are separate public truths**
- **time-skew warnings must degrade deadline strength instead of merely decorating the UI**
- **irreversible acts may not silently mature on an untrusted clock basis**
- **clock correction or late temporal evidence may reopen supposedly completed cooling, expiry, or contest sentences**

## Consequence for the non-clone score

Resilio still belongs on the borrow side for time-skew candor, UTC normalization, and operational timestamp honesty.
Resilio remains on the non-clone side for the fairness-critical deadline contract.

The reason is now precise:

> current Resilio docs still expose internal-clock dependence, timezone correction, GMT normalization, placeholder mtime preservation, and short-window history as separate operational facts rather than one typed time-authority object for `trusted`, `degraded`, `suspect`, `corrected`, and `adjudicated` deadline states, so the operator still has to reconstruct whether a timer is trustworthy from scattered traces instead of one owned interface family.
