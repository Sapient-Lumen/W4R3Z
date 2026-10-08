# Resilio time authority, disk-vs-database timestamp truth, and replay-chronology evaluation

## Decision for AnonSync

Borrow Resilio's candor that timestamp truth is operationally real.
Do **not** clone the present Resilio contract for file ordering, wall-clock trust, `mtime` authority, or archive replay.

## Why this pass matters

Current official Resilio materials still make one ordinary operator question — `which timestamp actually governs ordering, replay, and visible freshness right now?` — depend on several separate pages instead of one owned interface family.

The useful truths are real:

- Resilio's current `Time difference` article still says Sync decides which file is newer by comparing **files modification time**, converting it to **GMT**, and warning once actual peer time difference exceeds the allowed window.
- the current power-user table still publishes `sync_max_time_diff = 600 sec`, making ordering trust explicitly budgeted rather than absolute.
- that same current table still publishes `ignore_mtime_assign_errors`, and still says that when Sync fails to write a file's `mtime` on disk it can keep the **correct mtime only in the database** while the filesystem timestamp becomes **current time**.
- the current archive-restore article still says restored files come back with an **older modified timestamp** than other peers, and that restoring while Sync is not running can cause the candidate to be detected later and moved back to Archive as older.
- the current desktop and mobile sync guides still remind operators that Sync relies on the **internal clock** of each device and that wrong time or timezone causes `Excessive time difference` behavior.

## The non-clone problem

Those truths are useful.
The page shape is not.

Present-day Resilio still externalizes too much meaning into documentation archaeology:

- wall-clock trust and file ordering live in a time-difference article
- the allowed skew budget and the database-only `mtime` escape hatch live in power-user settings
- replay behavior for restored candidates lives in archive instructions
- device-time dependence is repeated in onboarding guides rather than owned as steady-state authority truth

So one ordinary operator answer still requires reconstructing:

1. the **active ordering basis**
2. the **skew budget** currently being trusted
3. whether **disk-visible time** still matches the product's chronology ledger
4. whether replaying a retained candidate will stick, be outranked, or be re-archived
5. the **strongest safe sentence** the product may still say afterward

## AnonSync product stance

AnonSync should instead own temporal authority as one page family:

- a **Temporal authority contract sheet** that states ordering basis, skew budget, disk-vs-ledger timestamp truth, and proof ceiling
- a **Clock-skew and time-authority review** that previews which peers or seats are degrading chronology trust and what is held as a result
- a **Timestamp provenance proof** page that says plainly when visible filesystem `mtime` no longer matches ledger truth
- a **Replay chronology review** that previews whether a retained candidate will win, lose, or bounce back into retention
- a **Temporal lineage receipt** that preserves which time basis was trusted, what stronger sentence stayed blocked, and what invalidators would weaken the claim later

## Hard decisions now locked

1. Wall-clock trust and file-ordering trust are first-class objects.
2. Filesystem-visible `mtime` and product chronology ledger are separate truths when assignment can fail.
3. Archive replay is chronology-sensitive and must not masquerade as simple file copy.
4. Skew budgets, timezone faults, and ledger-only fallback are reviewable operator facts, not support lore.
5. Durable receipts preserve the trusted time basis and the blocked stronger reading.
