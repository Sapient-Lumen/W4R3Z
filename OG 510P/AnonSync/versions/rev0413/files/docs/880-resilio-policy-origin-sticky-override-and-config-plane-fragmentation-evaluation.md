# Resilio policy-origin, sticky-override, and config-plane fragmentation evaluation

## Why this pass exists

The archive already had strong work on authority, artifact families, destructive actions, residency, transport, and maintenance semantics.
What it still lacked was one explicit evaluation of a narrower but highly consequential seam:

> when an operator asks `what settings actually govern this subject right now, where did those settings come from, and what will happen if I try to change or reset them?`, how many present-day Resilio planes do they still have to remember?

Current official Resilio docs are still useful because they are candid about real policy sources.
They still openly say that:

- **Folder Preferences** own per-share controls such as Archive, read-only overwrite behavior, relay usage, tracker usage, LAN search, predefined hosts, and file download priority.
- **Power user preferences** publish standing defaults and switches such as `disable_remove_from_all_devices`, and some of those still have platform caveats such as `Ignored in Linux WebUI`.
- **File download priority** now has both a per-share control and a global `folder_defaults.transfer_priority` default, while a share whose priority was manually changed stops inheriting later global changes even if manually set back to `None`.
- **Selective Sync** and **Synchronization Modes** still say mode can be chosen when first connecting, after connection, and when a folder arrives automatically from linked devices.
- **Sync Private Identity & Linking My Devices** still says linked devices auto-receive folders and are prompted with a default folder location plus Disconnected / Selective Sync / Synced posture.
- **Running Sync in configuration mode** still says advanced preferences can be injected through `sync.conf`, that only Standard folders can be set up there, and that if shared folders are specified in configuration then WebUI is disabled and those configured directories override folders previously added from WebUI.

That is good candor.
It is also strong evidence that AnonSync should not clone the exact contract.

## What current Resilio still gets right

### 1) Effective settings really do come from more than one place

Resilio is right that some settings are per-share, some are standing defaults, some are link-time choices, and some are boot-time or configuration-plane choices.
Pretending there is only one policy plane would be dishonest.

### 2) Defaults matter across future arrivals

Resilio is also right that connected-device defaults and folder defaults can affect later arrivals and later created shares.
Those defaults are not cosmetic.

### 3) Config-plane ownership is materially different from casual UI edits

Resilio is right that startup configuration can override previously added folders and even suppress WebUI in some cases.
That is not just another checkbox.
It is a different control plane.

## Why AnonSync still should not clone it

### 1) One ordinary question still leaks across too many policy planes

Current Resilio still makes the ordinary operator answer depend on remembering whether the active setting came from:

- share preferences
- a global power-user default
- a linked-device connect default
- a connect-time choice
- a startup configuration file
- a platform/runtime caveat such as Linux WebUI behavior

Those are real distinctions, but the product should own them in one provenance grammar rather than forcing article archaeology.

### 2) `Return to default` is not honest enough if inheritance does not really rejoin

The current file-priority docs are especially revealing.
A manually changed share priority stops inheriting later global changes even if it is later set back to `None`.
That means `neutral` can still secretly mean `sticky local exception` rather than `rejoined inheritance`.
AnonSync should refuse that ambiguity.

### 3) Config-plane supremacy is still too easy to miss

Current configuration-mode docs still say configured shared directories override folders previously added from WebUI and disable WebUI when the config explicitly defines shared folders.
That is a strong control-plane boundary, but it still mostly lives in setup prose.
A serious product should publish when an effective policy is config-owned and when the UI is no longer the source of truth.

### 4) Blast radius is still hard to inspect before edits

Changing a share preference, changing a standing default, changing a linked-device mode default, and changing a config template do not have the same scope.
Operators deserve a first-class preview of whether they are editing one subject, all inheriting subjects, future arrivals only, or a configuration-owned cohort.

### 5) Drift and exception truth are still too hidden

Once settings can come from several planes, a fleet accumulates exceptions.
Current Resilio reveals pieces of that truth, but the product still does not own a durable `why this share differs from the expected default` page family.
AnonSync should.

## Hard decisions now locked for AnonSync

1. **Every effective policy field carries provenance.** Value alone is never enough.
2. **`Return to default` means rejoin inheritance for real.** It cannot leave a dormant sticky override behind.
3. **Config-plane ownership must stay visible.** A config-owned subject cannot pretend to be UI-owned.
4. **Policy changes preview their plane and blast radius.** Share-local edits, standing-default edits, and config edits are different verbs.
5. **Drift is a first-class object.** Exceptions, legacy overrides, and policy forks get their own review surface and receipt.
6. **Receipts preserve source-of-truth lineage.** Later operators must be able to tell not only what the value became, but also which plane won.

## Replacement page family justified by this pass

This pass therefore justifies five more product-owned surfaces:

- **Effective policy sheet**
- **Policy change preview**
- **Inheritance return review**
- **Policy drift watch**
- **Policy provenance receipt**

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still right that defaults, overrides, per-share settings, linked-device mode choices, and config-plane inputs are genuinely different sources of truth. But it still makes the operator reconstruct effective policy from several planes, and it still tolerates sticky local exceptions that do not clearly return to inheritance. AnonSync should keep the candor and refuse the fragmented policy-origin contract.
