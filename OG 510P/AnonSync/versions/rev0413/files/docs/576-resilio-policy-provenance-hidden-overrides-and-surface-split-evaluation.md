# Resilio policy provenance, hidden overrides, and surface-split evaluation

## Why this pass exists

The archive already had pages for destination choice, bind outcome, runtime profile, control-surface grade, and delivery diagnosis.
What it still did not own cleanly enough was one ordinary operator question that sits underneath many of those pages:

- what rule is actually effective here right now
- where did that rule come from
- which stronger or narrower rule is shadowing the obvious UI control
- which surface is truly authoritative for changing it
- what will continue to exist after an edit on one surface
- what stronger sentence would be dishonest because hidden overrides still apply

Current official Resilio docs still make that seam materially real.
They still distinguish ordinary Sync Preferences and Folder Preferences from a deeper Power user preferences plane, and they still say configuration mode can import Advanced Preferences, move storage, set listener/auth/cert material, limit directory pickers, and even disable live WebUI when shares are declared in config.
At the same time, ordinary preference pages still point to power-user flags for behavior that materially changes semantics: LAN rate limiting, Archive retention limits, bind-interface behavior, watcher/notification behavior, placeholder-deletion behavior, conflict-path handling, and more.

That candor is useful.
The problem is that operators can still need article memory to answer one ordinary question:

> which rule is actually winning here, and which surface am I supposed to trust when I change it?

## What current Resilio still gets right

Current official docs still publish several truths worth borrowing.

- **Rule origin is materially real.** Current docs still distinguish Sync Preferences, Folder Preferences, Power user preferences, and configuration-mode ownership rather than pretending all settings are equivalent.
- **Hidden override classes are candidly documented.** Current Power user preferences still expose behaviorally important flags such as `rate_limit_local_peers`, `max_file_size_for_versioning`, `folder_rescan_interval`, `enable_file_system_notifications`, `recreate_placeholders_on_removal`, `fix_conflicting_paths`, `lan_encrypt_data`, and `use_only_bind_interface`.
- **Config mode is openly stronger than ordinary UI in some lanes.** Current configuration-mode docs still say Advanced Preferences can be added there, only Standard folders are supported in config mode, and declared shared folders override previously added folders and disable WebUI.
- **Scope layers are admitted.** Current docs still distinguish global preferences, per-folder preferences, folder defaults, and config-owned settings.
- **Defaults are not hidden from the documentation.** Current docs still show ordinary defaults such as random listening port, loopback-style examples for WebUI, default archive retention, and default per-folder discovery settings, while also documenting deeper override knobs.
- **The current v3 line is still live.** Official docs still show the v3 line through `3.1.2.1076` dated 31/Oct/2025.

That is good candor.
Resilio still admits that behavior does not come from one flat preference sheet.

## Where current Resilio still stays too article-shaped

### 1. Effective rule provenance still depends on memory

The ordinary operator should not have to reconstruct from memory whether current behavior comes from:

- a visible global preference
- a visible folder preference
- a hidden power-user flag
- a folder default that only applied at creation time
- a config-file value that now owns the surface
- a runtime / storage profile switch that changed which settings store is active

Current Resilio still publishes those truths, but it still leaves provenance spread across several articles.

### 2. Edit surfaces are still not honest enough about authority

These are materially different realities:

- a visible UI toggle is authoritative and immediate
- a visible UI toggle is only a local preference layered beneath a stronger config rule
- a folder-level control only affects later folders through defaults, not existing ones
- a config-owned share disables live WebUI and therefore moves future edits elsewhere
- a power-user field changes semantics that the ordinary page still describes in simpler language

Those differences should be first-class product verdicts, not support knowledge.

### 3. Hidden overrides can silently change the meaning of visible actions

Current docs still imply or state behaviors that can surprise an operator unless provenance is surfaced first:

- LAN rate limits can stay off even when global rates look set
- placeholder deletion can be blocked by `recreate_placeholders_on_removal`
- Archive existence and size limits can be changed outside the visible folder flow
- bind-interface forcing can silently narrow connectivity beyond the visible listener story
- disabled file notifications can turn immediate detection into periodic rescans
- disabling conflicting-path handling can turn a repair behavior into a sync stop with unpredictable results

That is useful truth, but it is still not owned by one product page family.

### 4. Config ownership can substitute a different product mode

Current configuration-mode docs still say shared directories declared in config disable WebUI and override folders previously added from WebUI.
That means `change the setting` is not always the right operator sentence.
Sometimes the true sentence is:

- `this seat is now config-owned`
- `this rule is no longer editable from live UI`
- `the visible control is descriptive, not authoritative`

That should be an explicit reviewed state, not a buried support caveat.

## What AnonSync should do instead

AnonSync should make **policy provenance** a first-class reviewed object.

The product should own four page families:

1. **Policy provenance**
   - effective rule
   - rule origin
   - scope
   - shadowing / override chain
   - authoritative edit surface
   - strongest safe sentence and stronger forbidden sentence

2. **Override mutation review**
   - requested change
   - current winning rule
   - losing / shadowed rules that remain present
   - restart / relaunch / config-commit consequences
   - any mode substitution after apply

3. **Hidden override surfacing**
   - risky deep flags affecting visible behavior
   - whether the current surface can edit them
   - why the visible UI would otherwise mislead
   - safer ladder from observation to mutation

4. **Policy provenance receipt**
   - effective rule after apply
   - origin chain after apply
   - surface still authoritative after apply
   - surviving shadow rules and next review point

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that behavior can come from visible preferences, folder-level rules, power-user flags, and config ownership. But it is not worth cloning the way current operators still have to reconstruct from several articles which rule is actually in force, which surface is authoritative, which deeper override is shadowing the visible control, and whether a requested edit is really a preference change or a control-mode substitution.

## New replacement pages added in this revision

- `577` Policy provenance
- `578` Override mutation review
- `579` Hidden override surfacing
- `580` Policy provenance receipt
