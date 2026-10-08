# Resilio mobile capture-source, path-class, sink, and reacquire truth evaluation

## Why this pass exists

The archive already had:

- ingress verb taxonomy
- subject-kind chooser guidance
- cross-surface parity notes
- mobile storage accounting
- external-edit / save-back review
- warning and recovery-rung pages

Those were necessary, but another current Resilio pass shows a still-missing ordinary seam.
The problem is no longer only `what verb did I press`.
It is now:

- what exact *source class* am I attaching on a mobile seat?
- what exact *path class* is writable, sandboxed, fixed, or source-only on this device?
- what exact *sink contract* am I creating when I choose backup instead of sync?
- after I clear bytes locally, which things are reacquirable, which survive only as history, and which were never meant to sync back?

That is where current official Resilio docs stay useful yet still become too article-shaped.

## What current Resilio still gets right

Current official material is still admirably candid about mobile reality.

Examples the docs still openly describe include:

- **Camera Backup** is not merely a folder toggle; it is a backup flow whose source-side deletions do not delete the storage copy on the chosen desktop/NAS sink.
- **Android backup** can source bytes from almost any reachable Android location, including existing folders and even ExtSD as a *source*, while iOS backup is limited to Camera Roll because iOS apps cannot read outside the application folder.
- **Backup sinks are not collaborative peers in disguise**: the Android backup docs still say the desktop side has read-only access, so its file changes do not sync back and sink-side deletions do not delete the phone copy.
- **Path classes are real**: Simple Mode still forces new shares into `Downloads/Sync` on internal storage, hides root and `ExternalSD`, and turning it off is still required before the operator can choose a location or use SD card.
- **SD-card admission is not ordinary folder-picking**: Sync still needs root-level card permission through the Android document-provider flow, and taking the wrong picker path still fails to grant write access.
- **Some path classes are source-only**: Android 4.4/5.0 ExtSD restrictions still allow backup *from* ExtSD to desktop while not allowing Sync to write the backed-up folder there.
- **Downloads/history are split objects on mobile**: current Android/iOS file-sharing docs still separate `Downloads` from `Shared links`, and deleting a downloaded file can remove the local file while history remains.
- **iOS local storage is explicitly sandboxed**: current storage docs still separate app data, downloaded files, shared files, and synced-share bytes, and clearing local files still depends on Selective Sync.
- **iOS external editing remains copy-based**: the docs still say editing in another app works on a copy that must be sent back, and that putting the updated file back can temporarily create duplicate versions rather than in-place replacement.
- **Android background and battery gates are still explicit**: Auto Sleep and Battery Saver can take the core offline even while the seat still conceptually owns the subject.

That candor matters.
Resilio is not pretending that a phone is just a small desktop.

## Where the current page shape still fails

The ordinary operator answer is still reconstructed across too many mobile-specific articles, configuration notes, and old-but-still-current quirks.

### 1. Source class is still too implicit

Current docs still force the operator to infer whether they are working with:

- a live sync subject
- a capture-only source
- Camera Roll only
- an arbitrary Android folder
- an existing folder on internal storage
- an ExtSD folder that is source-only
- one-off downloaded bytes
- a copied-out iOS working file that is no longer live-bound

That classification is usually implied by which article the operator happened to open, not owned by one stable page family.

### 2. Writable path class is still too scattered

The operator must still piece together whether this device/path is:

- app-sandbox only
- fixed to `Downloads/Sync` because Simple Mode is on
- eligible for explicit location choice only if Simple Mode is off
- writable on SD card only after root-level document-provider permission
- readable as a backup source but not writable as a synced destination
- visible in history but not necessarily still present as bytes

That is too much reconstruction for ordinary mobile work.

### 3. Backup sink truth is still too article-dependent

Current docs often describe backup as if it were obvious, but the actual operator questions still need cross-reading:

- is this sink a live collaborative peer or a storage-only sink?
- do sink-side deletes sync back?
- where will the default backup folder appear?
- can I choose among linked devices now or mail/copy a link to a not-yet-linked sink?
- what remains on each side after disconnect?

Those are contract questions, not help-center trivia.

### 4. Reacquireability and history still blur together

Current docs still make the operator reconstruct whether a removed local file:

- can be re-downloaded from backup
- can be fetched again only if a live source is online
- survives only as a history row
- was merely hidden from the UI
- depends on Selective Sync being enabled before clearance

That is still too many pages for one ordinary trust question.

## What AnonSync should do instead

AnonSync should keep the candor and reject the article sprawl.

The product should split this seam into four page families:

1. **Capture source**
   - what mobile source class is being attached
   - whether the subject is live sync, capture-only, or one-way backup
   - what source-side deletion means later
   - whether edits can ever flow back upstream

2. **Mobile path class**
   - exact storage / path class for this seat
   - writable vs source-only vs sandbox-only vs fixed-default
   - admission prerequisites such as root grant or mode change
   - whether the current chooser is actually picking a location or only granting future authority

3. **Capture sink**
   - which linked or external sink receives durable copies
   - whether the sink is storage-only or collaborative
   - default naming / placement if auto-created
   - disconnect and retention consequences

4. **Mobile reacquire**
   - which locally cleared bytes are reacquirable
   - whether recovery depends on live source, backup history, or surviving download history only
   - what remains as a receipt after bytes are gone
   - what prerequisites such as Selective Sync or keeping Sync open still matter

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that mobile capture, storage, and reacquire truth really are different from desktop truth, but not for the way ordinary answers to `what source class is this`, `what path class is actually writable here`, `what sink contract did I just create`, and `can I clear this now and honestly get it back later` still sprawl across Camera Backup, Android Backup, Simple Mode, SD-card, file-sharing, storage-management, and iOS-peculiarity articles instead of one stable page family.

## New replacement pages added in this revision

- `452` Capture source
- `453` Mobile path class
- `454` Capture sink
- `455` Mobile reacquire
