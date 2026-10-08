# Resilio download-priority policy provenance, active-window ceiling, and visible-order fragmentation evaluation

## Why this pass exists

The archive already had strong doctrine for transfer eligibility, resource contention, queue pressure, and byte-plan certainty.
What it still lacked was one direct current Resilio pass about a narrower operator question:

> when the product says `this is prioritized`, what truth actually exists: a global default, a per-share override, a sticky ex-share override, an active-window sort, a UI-only ordering illusion, or only a best-effort queue preference with exceptions?

Current official Resilio docs are unusually useful here because they are candid about the real mechanics while still leaving the operator to reconstruct them across the new `File download priority` article, `Folder Preferences`, and `Power user preferences`.

Today those docs still show that:

- download priority is available in Sync `3.1.0`.
- a share can prioritize by file size or modification time, while the default is `None`.
- a global `folder_defaults.transfer_priority` can automatically apply to existing shares whose priority has not been altered manually, and also to new shares including single-file sharing.
- once a share's priority has been changed manually, later global changes stop applying to it even if the share is later manually set back to `None`.
- only the active download queue is prioritized, with a limit of 50,000 active files.
- higher-priority arrivals can suspend lower-priority downloads, but there are internal exceptions.
- active downloads can be suspended immediately even when almost complete.
- queue rebuilds can happen when file properties or errors change and can affect performance.
- non-splittable files do not strictly follow the same cancellation logic.
- the UI queue may still appear alphabetical rather than in effective priority order.

That is a strong operator-truth corpus.
It is also a strong reason not to clone the exact page contract.

## What current Resilio still gets right

### 1) It admits that priority origin matters

The current docs do not pretend every queue preference comes from one place.
They explicitly distinguish per-share configuration from global defaults.
That is worth keeping.

### 2) It admits that `None` does not always mean `back to inherited`

The current docs are candid that once a share has been manually changed, later global default changes no longer affect it even if the share is manually set back to `None`.
That distinction is materially useful.

### 3) It admits that prioritized order is only about the active window

The current docs still say only the active queue is prioritized and that there is a 50,000-file cap.
That is much better than a flat promise that the whole backlog is globally ordered.

### 4) It admits that visible order can diverge from effective order

The current docs still say the queue shown in the UI may appear alphabetical rather than in actual priority order.
That candor is valuable because it keeps visible listing separate from scheduling truth.

## Why AnonSync still should not clone it

### 1) Policy provenance is still too easy to lose

The operator still has to reconstruct whether the current order comes from a global default, a per-share override, or a now-sticky former manual override.
AnonSync should not let `priority: none` hide which of those is actually true.

### 2) The active-window ceiling is still too easy to forget

The current docs still leave the operator to remember that only the active queue is prioritized and that waiting files above the cap are outside the current preference effect.
AnonSync should make that ceiling explicit.

### 3) Suspension and exception behavior are still too easy to overstate

`Higher priority` is not the same as `everything lower stops immediately under all circumstances`.
Internal exceptions and non-splittable-file behavior remain real.
AnonSync should publish those ceilings where the operator makes the choice.

### 4) UI order is still too easy to mistake for scheduler proof

If the queue surface remains alphabetical while the actual scheduler uses priority rules, then the visible list is not proof of effective order.
AnonSync should not let the operator infer scheduling truth from a convenience list.

## Hard decisions now locked for AnonSync

1. **Queue-governance provenance is a first-class contract object, not an advanced preference detail.**
2. **Global default, per-share override, sticky former-manual override, active-window order, and visible list order are separate truths.**
3. **`None` is weaker than `inherits current default`, and `inherits current default` is weaker than `will move first`.**
4. **Priority policy is weaker than active admission, and active admission is weaker than uninterrupted completion.**
5. **Every serious queue-order action needs one receipt that preserves policy origin, active-window scope, exception ceiling, and the blocked stronger sentence.**

## Replacement page family justified by this pass

This pass therefore justifies five more product-owned surfaces:

- **Queue-governance contract sheet**
- **Priority-origin review**
- **Active-window proof**
- **Visible-order mismatch page**
- **Queue-governance lineage receipt**

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still right that priority origin, sticky manual override, active-window ceilings, suspension behavior, and visible-order mismatch are materially different truths. But it still makes one ordinary operator answer — `why is this prioritized, what scope does that actually cover, and does the queue I see prove the queue the scheduler is using?` — depend on several pages instead of one stable product-owned family. AnonSync should keep the candor and refuse the fragmentation.
