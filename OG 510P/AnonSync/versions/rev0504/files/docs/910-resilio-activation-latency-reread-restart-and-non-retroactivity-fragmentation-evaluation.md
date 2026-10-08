# Resilio activation latency, reread/restart, and non-retroactivity fragmentation evaluation

## Why this pass exists

The archive already had broad work on hidden state, change detection, instrumentation activation, and policy provenance.
What it still lacked was one narrower current Resilio pass about an ordinary operator question:

> I changed a rule or knob — when is that actually live, what still waits on restart or reread, and what old state remains untouched even after the new policy becomes active?

Current official Resilio docs are useful here precisely because they are candid.
Today those docs still show that:

- `Ignoring files in Sync (Ignore List)` still says IgnoreList is reread when changed or, if notifications are not arriving, every `folder_rescan_interval`; it still recommends restarting Sync for immediate application; and it still says the rule does not affect files that already synced while already-indexed structure remains passed to peers until disconnect.
- `How soon does synchronization start?` still says file-system notifications are fastest, scheduled folder scan runs every 600 seconds and on Sync start, and setting `folder_rescan_interval` to `0` disables rescans even upon restart.
- `Setting Delay Time For Syncing` still says `FileDelayConfig` lives in the storage folder, is edited as JSON, defaults listed file classes to a 10-second delay, and requires restarting Sync after edits.
- `Collecting debug logs manually` still says debug logging can be enabled through UI or `debug.txt`, that Sync should be restarted to make sure logging is enabled, and that capture should run for at least 15 minutes.
- `Power user preferences` still says `profiler_enabled` requires client restart to activate and still publishes `config_refresh_interval`, `config_save_interval`, and `folder_rescan_interval` as separate timing levers.
- the live v3 line still runs through `3.1.2.1076`.

That is a good reason to keep studying Resilio.
It is also another good reason not to clone the exact interface contract.

## What current Resilio still gets right

### 1) It admits that effect timing is real product meaning

Resilio does not pretend every change is instant.
Current docs still distinguish:
- immediate notification-driven detection
- periodic rescan fallback
- manual rescan
- restart-required toggles
- hidden-file edits
- delayed-shipment policies for actively edited file classes

That honesty is good.

### 2) It admits that `saved` and `effective` are not always the same thing

The docs still say some edits require restart, some wait on reread, and some rely on later background cadence.
That distinction is worth preserving.

### 3) It admits that some changes are not retroactive

The IgnoreList docs still say the rule does not affect files that already synced and that already-indexed structure keeps propagating until disconnect.
That is exactly the kind of limit operators need to see, not infer.

## Why AnonSync still should not clone it

### 1) One ordinary operator question still spans too many pages

To answer `is my change actually live yet?` the operator may still need to combine:

- IgnoreList timing notes
- change-detection / rescan docs
- FileDelayConfig restart ritual
- debug/profiler restart notes
- power-user interval tables
- remembered service/runtime behavior

That is too much archaeology for one ordinary decision.

### 2) Activation class is still too often implicit

Current Resilio docs preserve the facts, but the product contract still makes operators remember whether a control is:
- immediate
- next-reread
- next-rescan
- next-restart
- next-startup
- future-only / non-retroactive

AnonSync should not leave that classification scattered.

### 3) Pending effect is not yet owned strongly enough

A changed hidden file or power-user value can be `saved but not yet honestly live`.
Current Resilio docs still leave too much of that truth in support prose, timing tables, and restart ritual.

### 4) Proof-of-effect and proof-of-save are still too easy to confuse

`edited successfully`, `stored on disk`, `reread by runtime`, `active for future work`, and `retroactively reconciled old material` are not one sentence.
AnonSync should productize those as separate claims.

## Hard decisions now locked for AnonSync

1. **Every meaningful change declares an activation class.** `immediate`, `next-reread`, `next-rescan`, `next-restart`, `next-startup`, `external-proof-needed`, and `future-only` are first-class states.
2. **Saved is never silently upgraded into live.** The product must say when a value is staged only.
3. **Retroactivity is explicit.** A future-only rule never masquerades as having repaired old state.
4. **Pending effect gets its own watch surface.** Operators should be able to inspect what is staged, what is waiting, and what proof is still missing.
5. **Receipts preserve route and proof class.** Later operators must know how a change was introduced, what made it live, and where that claim stops.

## Replacement page family justified by this pass

This pass therefore justifies six more product-owned surfaces:

- **Effect activation contract sheet**
- **Activation latency review**
- **Pending effect watch**
- **Policy effect verification**
- **Activation lineage receipt**
- **Activation expiry / supersession alert**

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still right to admit that some changes become real immediately, some only after reread or restart, and some are future-only rather than retroactive. But it still makes one ordinary operator answer — `did my change merely save, become live, or actually change the world I care about?` — depend on timing notes, restart rituals, hidden-file docs, and rescan lore instead of one stable page family. AnonSync should keep the candor and refuse the archaeology.
