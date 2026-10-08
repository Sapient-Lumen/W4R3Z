# Resilio publication-readiness, authoring-delay, and touch-repair evaluation

## What current official docs still make clear

Another current Resilio pass again strengthens the main archive conclusion rather than weakening it.

Current official docs still show real product substance:

- a live v3 line with `3.1.2.1076`
- a current FAQ answer that still says changes start syncing immediately **only after** detection, indexing, and delivery can begin
- explicit detection truth that filesystem notifications are the fastest path, while scheduled rescans still default to every 600 seconds and on Sync start
- explicit degraded-detection truth that the rescan interval can be changed, including all the way to `0`, which disables rescans even on restart
- explicit authoring-safety truth that certain file classes can be delayed before shipment, with a default 10-second delay for listed file types such as Office, AutoDesk, and Adobe documents
- explicit storage/config truth that the delay policy still lives in `FileDelayConfig` in the storage folder and still requires editing JSON and restarting Sync
- explicit lock-conflict truth that the product will mark files as locked, let the operator open the affected-file list, but still cannot name the application holding the lock
- explicit manual-repair truth that a file may need to be manually `touched` when mtime or size did not change or were not noticed
- explicit inbound-priority truth that current v3 supports per-share download priority by modification time or size, plus a global default in power-user preferences
- explicit precedence truth that a share with manually set transfer priority stops inheriting future global priority changes even if the operator later sets the share back to `None`
- explicit queue-behavior truth that higher-priority files can suspend lower-priority downloads, but only inside the active queue window and with internal exceptions
- explicit UI-truth mismatch that the current interface may still list files alphabetically rather than in actual priority order

That is not weak product thinking.
It is useful operational truth.

## What still should not be cloned

The ordinary operator answer is still fragmented.
Current docs still require hopping across the FAQ, delay-time article, touch-file how-to, locked-files warning, file-download-priority page, power-user table, and watcher / rescan notes to answer four basic questions:

1. **Is this changed file actually ready to publish right now, or still waiting on detection, delay, or a lock?**
2. **Which delay policy is active for this file class, where did it come from, and when will the hold end?**
3. **Is `touch` actually the right repair here, or would it only fake freshness and create chronology risk?**
4. **Why is this inbound file not going first, and which policy or queue exception is currently in charge?**

Resilio still has strong ideas here.
It still does **not** earn direct interface cloning.

The reason is the same clone-veto rule applied to another seam:

> one ordinary operator question should have one stable page answer.

Current Resilio still spreads publication-readiness truth across a FAQ, a troubleshooting article, a how-to, a new priority feature page, and power-user notes.
So the product idea stays strong while the page contract still fails.

## Why this matters for AnonSync

AnonSync should borrow five important habits directly:

- **say openly when `sync now` is really gated by detection coverage, authoring delay, or a lock rather than transport**
- **say openly which file-class delay policy currently applies and whether it is inherited, local, or temporary**
- **say openly when a manual repair such as `touch` would advance chronology and therefore needs proof and review**
- **say openly when inbound priority is inherited, overridden, queue-limited, or partially defeated by transfer class**
- **say openly when the visible list order is not the authoritative execution order**

But AnonSync should refuse five weaker habits:

- learning publication readiness from several unrelated support articles
- learning delay policy by editing a storage-folder JSON file before understanding current truth
- learning whether `touch` is appropriate only from a shell-command how-to
- learning queue exceptions only after a supposedly urgent file does not move first
- learning visible-vs-actual order mismatch only from footnotes

## Replacement pages added for this seam

This revision therefore adds four narrower replacement pages:

- `437` — Publication readiness
- `438` — Authoring delay
- `439` — Touch repair
- `440` — Inbound priority

These pages keep the Resilio candor and reject the fragmented how-to-first operator reconstruction path.

## Sharper non-clone line after this pass

The archive now has one tighter sentence for this seam:

> borrow Resilio's candor that detection coverage, authoring delay, lock conflicts, manual mtime repair, and inbound urgency are real operational truths; refuse any interface contract where `is this ready yet`, `why is this waiting`, `is touch actually correct`, and `why is this not first` still depend on a FAQ, a how-to, and a troubleshooting article instead of one stable page family.
