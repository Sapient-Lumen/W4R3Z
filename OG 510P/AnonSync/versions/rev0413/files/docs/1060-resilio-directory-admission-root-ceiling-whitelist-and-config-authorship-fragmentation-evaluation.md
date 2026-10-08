# Resilio directory-admission, root-ceiling, whitelist, and config-authorship fragmentation evaluation

## Why this pass exists

The archive already had launch authority, storage worlds, service promotion, bootstrap authority, overlap topology, and hidden control substrate.
What it still did not own cleanly enough was one narrower but very ordinary operator seam:

> when a user tries to add or create a synced directory, who decides which paths are admissible at all, what root ceiling applies, what the picker is even allowed to reveal, and when does config authorship replace operator authorship?

Current official Resilio docs still make that seam materially real.
They still say all of the following at once:

- running Sync in configuration mode applies a pre-configured parameter set at program start and is intended for repeating the same settings on multiple machines
- if a non-default `storage_path` is set in config, new settings are created there instead of the default location
- `directory_root_policy` on Linux changes how `directory_root` may be used for `getdir` and `adddir`, and `belowroot` explicitly denies attempts to use `adddir` to create directories directly within the root itself
- `dir_whitelist` defines which directories may be used to store sync shares and says other directories will not be visible in the folder picker
- if shared folders are set in the config file, WebUI is disabled and the shared directories in config override folders previously added from WebUI
- config mode can create only Standard folders, not Advanced
- the storage folder is itself a separate authority-bearing world because it contains current configuration, auxiliary settings files, and shares' database state

That is good candor.
It is also a strong reason not to clone the present contract.
One ordinary operator answer — `can I add this folder, who is blocking me, and did admin-supplied config already replace my own set?` — still depends on combining:

- configuration-mode setup prose
- configuration-file field descriptions
- storage-folder notes
- WebUI disable/override caveats embedded inside the sample-config overview

AnonSync should keep the distinctions and refuse the archaeology.

## Hard product decisions locked by this pass

1. **Directory admission is first-class policy state.** Path existence on disk is not enough; the product must say whether the path is admissible.
2. **Root ceiling and picker visibility are separate truths.** A path can be under the allowed root yet still hidden by picker policy, and a visible candidate can still fail a create-time ceiling.
3. **Config-authored subject sets are explicit authorship changes.** A preloaded folder set that overrides prior UI-added subjects is not a convenience import; it is authority replacement.
4. **Creation authority and nomination authority stay distinct.** `belowroot` is not the same thing as `no access`; it is a specific denial of direct creation at the root level while still allowing work below it.
5. **Receipts must preserve the blocking authority.** Every denial or replacement must remember whether config policy, picker whitelist, root ceiling, subject-class restriction, or storage-world change caused it.

## What current Resilio still gets right

Current official docs still publish several truths worth borrowing.

- **Admission can be policy-shaped.** The current config-mode article still exposes `directory_root_policy` and `dir_whitelist` instead of pretending every browsable path is equally admissible.
- **Root creation ceiling is explicit.** The same article still distinguishes `all` from `belowroot`, and says `belowroot` denies `adddir` attempts directly inside `directory_root` while still accepting subdirectories.
- **Picker visibility is admitted as authority, not just UI polish.** The same article still says non-whitelisted directories will not be visible in the folder picker.
- **Config authorship is admitted as stronger than WebUI authorship.** The same article still says config-defined shared folders disable WebUI and override folders previously added from WebUI.
- **Storage world is candidly separate.** The current storage-folder article still says the storage folder keeps configuration, auxiliary settings, and share database state, and that config mode changes the default location on desktop.

That is useful product honesty.
Resilio does not pretend that folder choice is one flat browse action.

## Where current Resilio still stays too article-shaped

### 1. Admission authority still hides inside sample-config commentary

The ordinary operator should not have to inspect a config-file overview to learn that path admission and path visibility may already be constrained before any add-folder flow begins.
Yet that is still roughly how present-day Resilio explains it.

### 2. Root ceiling and picker whitelist still collapse in practice

Current official docs do name both `directory_root_policy` and `dir_whitelist`.
But they do not render one operator-owned answer such as:

- visible and admissible
- admissible but not picker-visible
- picker-visible but create-denied at root ceiling
- config-authored only; operator add blocked
- standard-folder-only admission; advanced subject class unavailable
- denied because the current storage world is not the governing one

AnonSync should not clone a product where that answer remains a reconstruction.

### 3. Config-authored folder sets still feel like startup trivia instead of authority replacement

Current docs are admirably blunt that config-defined shared folders disable WebUI and override folders previously added from WebUI.
But the operator still has to infer the real product meaning:

- who authored the active subject set
- what earlier operator-authored set was displaced
- whether the UI is intentionally absent versus broken
- whether edits must now happen in config rather than in the picker

That is too weak for an ordinary interface.

### 4. Subject-class restriction remains tucked into setup prose

Current docs say config mode can only set up Standard folders, not Advanced.
That is not a footnote.
It means path admission is also shaped by subject class.
AnonSync should make that visible when it matters.

### 5. Denials still do not own authority lineage

A failed add-folder attempt may really be about root ceiling, whitelist, config-authorship, subject-class restriction, or storage-world mismatch.
Present-day Resilio still spreads that answer across setup prose and support memory rather than one durable receipt.

## The tighter non-clone decision

Borrow Resilio's candor that path admission is policy-shaped, that root ceiling and picker visibility are real, that config-authored folders can override prior WebUI state, and that storage world matters.
Do **not** clone a product contract where operators still have to merge config-mode prose, sample-config comments, and storage-folder notes to answer whether a path is admissible, visible, creatable, and operator-authored.

## What AnonSync should do instead

AnonSync should treat **directory admission authority** as one first-class reviewed family.
Every serious add-folder, create-folder, path retarget, bootstrap-config import, or managed-seat enrollment should answer five things in one place:

1. **admission authority** — who governs admissible paths for this seat right now
2. **root ceiling** — where creation or nomination may occur and where it may not
3. **picker visibility authority** — which paths are intentionally hidden from browse surfaces and why
4. **subject authorship** — whether the active subject roster is operator-authored, policy-authored, imported, or replaced
5. **safe language** — what the product may and may not say about `you can add any folder`, `browse all locations`, and `your existing subjects are still yours to edit`

## New page obligations from this pass

The archive now needs five more workflow-owned pages:

- **Directory admission contract sheet**
- **Root-ceiling review**
- **Picker visibility authority page**
- **Config-authored subject-set review**
- **Directory-admission lineage receipt**

Those pages should sit beside storage-world, launch-class, and control-substrate pages — not underneath setup notes alone.
