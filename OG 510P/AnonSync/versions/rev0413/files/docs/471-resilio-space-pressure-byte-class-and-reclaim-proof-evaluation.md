# Resilio space pressure, byte classes, and reclaim proof evaluation

## Why this pass exists

The archive already had storage budgets, hidden-state notes, constrained-seat local clear, and abstract reclaim objects.
Those were necessary, but another current Resilio pass still exposes a more ordinary operator seam.
The problem is no longer only `can I free some space locally`.
It is now:

- what exact **space floor** will actually stop progress here?
- what exact **byte classes** are consuming local storage right now?
- what exact **reclaim action** is safe-first rather than secretly weakening history or continuity?
- what exact **proof** do I get afterward that the intended bytes moved and other truths did not?

That is where current official Resilio docs stay candid yet still become too article-shaped.

## What current Resilio still gets right

Current official material is still admirably candid about storage and reclaim reality.

Examples the docs still openly describe include:

- **A concrete stop floor still exists**: the current power-user table still says `free_space_warning_threashold` defaults to `1024 MB` and that if that much space is left on the drive with the default folder location, Sync will warn and stop syncing files.
- **The warning still resolves against a specific drive, not a vague global low-space feeling**: the current core-warning article still says the `Running out of free space in storage location` warning appears when less than 1 GB is left on the disk where the default folder location points.
- **The stop floor is still policy-shaped**: the same power-user table still exposes `disk_min_free_space` and `disk_min_free_space_gb` as offsets to the free-space warning threshold.
- **Selective materialization is still a real local-space tactic**: current synchronization-mode docs still say Selective Sync uses placeholders, takes minimal hard-drive space, and lets `Remove from this device` revert a local full copy to a placeholder while peers remain intact.
- **The docs still warn that local reclaim is not recall-safe by magic**: the same Selective Sync material still says the operator must make sure another peer has a copy before relying on later re-download.
- **History retention is real storage, not folklore**: current Archive docs still say deleted or older copies go to `.sync/Archive`, with default retention of 30 days on desktops and 1 day on mobiles, and that archive access itself differs by platform.
- **Archive policy can weaken or disappear**: current folder-preferences docs still say disabling Archive stops deleted-by-Sync files from being copied there at all.
- **Mobile storage is split into named classes**: the current iOS storage-management page still separates `App Data` from `User data`, and still breaks user data into Downloads, Shared files, and sync shared folders.
- **Some reclaim verbs are posture-gated**: the same iOS storage page still says clearing local files from a sync share requires Selective Sync.
- **Residual and service bytes are explicitly real**: the current mobile-settings page still says Cleanup clears residual files as well as current debug logs.
- **Storage and support residue live outside subject payloads**: the current storage-folder article still says the storage folder keeps configuration, auxiliary settings, shares' database, and logs, while the uninstall guide still says operators may need to remove remaining storage folders manually after uninstall.

That candor matters.
Resilio is not pretending that `space used` is one undifferentiated bucket.

## Where the current page shape still fails

The ordinary operator answer is still reconstructed across too many articles and too many byte classes.

### 1. Pressure truth still leaks across warnings and power-user tables

Current docs are candid that Sync can stop syncing files when space gets too low, and that the stop floor is tied to the default folder location drive.
But the operator still has to combine:

- a warning article
- a power-user table
- hidden offsets like `disk_min_free_space` and `disk_min_free_space_gb`

just to answer one ordinary question:

- what exact floor is active here right now?

That is too much reconstruction for one ordinary pressure verdict.

### 2. Byte classes still sprawl across subject docs, mobile docs, and storage-root lore

Current docs still distribute storage truth across:

- placeholders and materialized files in synchronization-mode docs
- `.sync/Archive` in folder/archive docs
- app data, downloads, and shared files in iOS storage docs
- residual files and current logs in mobile settings
- configuration/database/logs/dumps in storage-folder and uninstall docs

That means the ordinary answer to `where is the space going` is still article-shaped rather than product-shaped.

### 3. Reclaim scope still depends on which surface the operator found first

Current docs still make reclaim semantics depend on whether the operator encountered:

- `Remove from this device`
- deleting a placeholder
- clearing local files on iOS
- mobile `Cleanup`
- Archive retention settings
- uninstall cleanup steps

Those are materially different actions.
The product truth should not depend on which support page the operator remembers.

### 4. Proof of success still collapses into folklore

Current docs still explain how to free bytes, disable Archive, clear files, or manually remove storage folders.
But they still do not provide one public page that answers:

- which byte classes were actually reduced
- which truths were intentionally preserved
- whether retention got weaker
- what residual bytes still remain local afterward

That is still too much folklore for one ordinary `did I reclaim the right thing` decision.

## What AnonSync should do instead

AnonSync should keep the candor and reject the article sprawl.
The product should split this seam into four page families:

1. **Space pressure**
   - active stop floor and active drive/root basis
   - byte-class pressure contributors
   - safe-first actions
   - strongest current non-effect

2. **Byte-class inventory**
   - payload / placeholders / archive / downloads / shared transfers / logs / database / residual files
   - owner and path class
   - reclaimability and retention role
   - continuity risk

3. **Reclaim preview**
   - candidate actions and expected freed bytes
   - non-effects and preserved truths
   - retention or history weakening
   - prerequisite gates and warnings

4. **Reclaim receipt**
   - actual byte delta by class
   - intended vs observed effect
   - preserved / weakened truths
   - remaining residue and next check

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that low-space floors, placeholders, Archive retention, mobile storage classes, and hidden service state all materially change storage truth. But it is not worth cloning the way ordinary answers to `what is consuming space`, `what will stop syncing`, `what can I reclaim safely`, and `what exactly changed afterward` still sprawl across warnings, power-user settings, synchronization-mode docs, Archive docs, mobile storage pages, storage-folder lore, and uninstall cleanup notes instead of one stable page family.

## New replacement pages added in this revision

- `472` Space pressure
- `473` Byte-class inventory
- `474` Reclaim preview
- `475` Reclaim receipt
