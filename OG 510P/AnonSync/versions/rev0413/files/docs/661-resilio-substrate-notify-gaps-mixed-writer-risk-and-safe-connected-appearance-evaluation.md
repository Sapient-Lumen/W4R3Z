# Resilio substrate notify gaps, mixed-writer risk, and safe connected-appearance evaluation

## Why this pass exists

The archive already had stronger doctrine for seat role, subject-kind override, non-authority edits, reconnect meaning, and winner proof.
What it still lacked was one direct current Resilio evaluation for a narrower but important question:

> when a share looks ordinary and connected, does the product also publish whether the underlying storage substrate is safe enough for ordinary connected language, or does the operator have to learn later that change detection is degraded, locks are implementation-defined, or mixed-writer access can corrupt bytes?

Current official Resilio docs still show a useful, living product, but they also still show that one ordinary answer is spread across several article families at once:

- `Sync and SMB file shares`
- `How soon does synchronization start?`
- `Locked files`
- `Setting Delay Time For Syncing`
- `Power user preferences`
- `Resilio Sync 3.0 change log`

## Current official Resilio evidence that matters here

Current official docs still show an active v3 line through `3.1.2.1076`.
They also still say all of the following:

- `Sync and SMB file shares` still says SMB shares work but must be used carefully, that file-update notifications may be unavailable unless both client and server support SMB 3.0, that lock behavior depends on the SMB service implementation, and that third-party access to Samba-shared files outside Samba can damage files or roll back changes.
- The same SMB article still calls out a favorite setup — syncing between NASes while other users access the same data over SMB — as one that can lead to lost or corrupted files when Sync accesses the files outside SMB protocol.
- `How soon does synchronization start?` still says filesystem notifications are the fastest path, but that for some storages they are not supposed to work at all, including NFS or SMB2 mounted shares and deeply nested folders on Windows; it also still says the fallback scheduled scan runs every 600 seconds by default.
- `Locked files` still says another application may block file access, that Sync cannot tell which application locked the file, and that operators may need separate tooling and a restart to recover.
- `Setting Delay Time For Syncing` still says operators may need per-file-type delay tuning to prevent Office and Sync from running into conflict when a file is being edited and synced at the same time.
- `Power user preferences` still says there are substrate-shaped controls such as `disk_worker_pool_size` for high-latency CIFS/network shares, `enable_file_system_notifications`, and `recheck_locked_files_interval` for locked-file retry behavior.

So current Resilio still contains a real but scattered answer to `is this a normal connected share on a trustworthy substrate, or a degraded substrate that needs different language, review, and repair expectations?`

## What Resilio still gets right

### 1) It is candid that storage substrate matters

The docs do not pretend all paths are equally good just because they are mounted.
They openly say SMB needs care, notifications may not work, lock behavior depends on the server, and some mixed-writer setups can corrupt data.
That honesty is valuable.

### 2) It still admits that timing and conflict are partly substrate-shaped

The docs openly say Sync may rely on rescans when notifications do not work and may need edit-delay tuning when apps and Sync are both touching the same file.
That candor matters.

### 3) It still admits that diagnosis may exceed the product boundary

The docs do not hide that Sync cannot identify the locking application and may require external tooling to do so.
That is awkward, but honest.

## Why this is still a good reason not to clone them

### 1) Connected appearance can still outrun substrate truth

Current docs still allow a share row to look ordinary while the real contract may be:

- notifications may be absent
- updates may only be discovered on scheduled rescan
- lock recovery may depend on external tools
- mixed-writer topology may be unsafe enough to corrupt or roll back bytes

AnonSync should not inherit a model where substrate capability only becomes visible after the operator leaves the share surface.

### 2) Safe connected language still depends on several scattered caveats

Current Resilio still leaves one ordinary sentence — `this share is safely live here` — dependent on reading an SMB warning article, a detection-timing article, a locked-files article, and advanced tuning notes together.
A serious sync product should own that sentence on the share itself.

### 3) Mixed-writer danger is still more like support prose than first-class policy

The SMB docs are candid that certain NAS + SMB + out-of-band writer setups can lose or corrupt files.
But that danger is still not expressed as a native substrate policy object with a review, severity, and durable receipt.
That means the operator still has to remember infrastructure folklore rather than product truth.

### 4) Repair meaning is still under-owned

Current docs still force the operator to reconstruct whether the right next step is:

- accept slower scheduled detection
- change retry timing for locked files
- introduce edit delay for specific file classes
- stop mixed-writer access entirely
- migrate the share to a safer substrate

That is not one ordinary support question.
It is one missing interface family.

## The tighter AnonSync conclusion

AnonSync should borrow the following from Resilio more boldly:

- candid admission that mounted storage is not the same thing as safe sync substrate
- candid admission that detection confidence and lock behavior can degrade by storage class
- candid admission that some mixed-writer topologies are unsafe, not merely slower

But AnonSync should refuse the exact page contract whenever one ordinary answer still depends on:

- storage-protocol caveat pages
- detection-timing fallback notes
- separate lock-diagnosis help
- app-specific delay-tuning tips
- advanced knobs that reveal substrate truth more clearly than the share surface does

## The replacement pages this evaluation justifies

This pass therefore makes four page-shaped obligations concrete:

1. **Substrate posture** — what storage substrate is this share running on, and what honest connected sentence does that permit?
2. **Substrate admission review** — should this share be allowed, degraded, quarantined, or blocked on this substrate and topology?
3. **Mutation-channel evidence** — how are changes being detected, what lock risk exists, and are there unsafe out-of-band writers?
4. **Substrate-risk receipt** — what substrate facts, warnings, and claim ceiling were in force when the operator proceeded?

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still good evidence that substrate-specific truth matters, but it is also current evidence that one ordinary question — `is this connected share actually safe and prompt on this storage path?` — can still require SMB caveats, detection-fallback notes, lock-diagnosis help, and app-conflict tuning just to learn that the substrate may be degraded or unsafe. AnonSync should copy the candor and refuse the ordinary-row / hidden-substrate contract.
