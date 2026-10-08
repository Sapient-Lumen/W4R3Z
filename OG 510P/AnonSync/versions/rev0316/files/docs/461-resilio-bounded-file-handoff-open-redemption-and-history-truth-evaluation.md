# Resilio bounded file handoff, open redemption, and history truth evaluation

## Why this pass exists

The archive already had ingress-verb taxonomy, mobile capture/source truth, capability gating, and transfer-lane explanation.
Those were necessary, but another current Resilio pass shows a still-missing ordinary seam.
The problem is no longer only `can bytes move`.
It is now:

- is this thing a **live shared subject** or only a **bounded snapshot handoff**?
- who exactly may **redeem** it, and what claim limits actually exist?
- where exactly will received bytes **land** on each surface class?
- when the operator clears a row or a file later, what **residue** remains as bytes, history, or only an expired claim?

That is where current official Resilio docs stay useful yet still become too article-shaped.

## What current Resilio still gets right

Current official material is still admirably candid about bounded handoff reality.

Examples the docs still openly describe include:

- **Single-file sharing is not live sync**: current docs still say sharing a file is basically a data-transfer operation that may contain one file or a few files at a time.
- **Desktop issuance is flexible**: the current single-file article still says the sender can use `+ -> Share file` or drag-and-drop, multi-select on desktop, and generate a link or QR after rescan and hashing.
- **Expiry is real and explicit**: current docs still say desktop links default to 3 days, can be changed through `share_file_ttl`, may be set to never expire by unchecking expiry, and the max default value allowed is 7.
- **Audience is open-link rather than approver-shaped**: the same article still says everyone who gets the link can download the shared files, and there is no option to restrict number of uses or ban some devices.
- **Desktop receive is path-selectable**: current docs still say the receiving side pastes the link through `Enter a key or link` and picks the files' location.
- **Desktop defaults are configurable**: the same article still says arriving files go to the user's Downloads directory by default and that config-mode / NAS installations use `files_default_path` instead.
- **Mobile is more opinionated**: current Android and iOS articles still say mobile single-file links default to 3 days and currently cannot be changed there.
- **Android receive still lands in one fixed internal inbox**: the Android article still says received files go to `Downloads/SyncDownloads` on internal memory and currently cannot be changed.
- **The handoff is snapshot-like, not continuous**: the single-file article still says this is a one-time one-way file transfer, that changed files invalidate the transfer, and that changed content requires adding the files again and generating a new link.
- **Recipients can fan out further**: the same article still says receivers can share the received files further, but cannot change link expiration date.
- **Name collision handling is concrete**: current docs still say that if the destination already has files with the same name in the selected directory, Sync adds `(1)` to the new ones.
- **Row clearing and byte clearing diverge by surface**: the desktop article still says removing the file from Sync UI does not remove it from device and removing it from device does not remove it from Sync UI, while Android and iOS still split `Downloads` from `Shared links` and treat them differently.
- **History survives some local deletion**: the iOS article still says removing a file from `Downloads` removes it from the device while transfer history still shows it.
- **Transfer residue is still governed by power-user knobs**: current power-user docs still keep `keep_expired_transfer_days` and `keep_expired_transfer_num`, and still note `transfer_job_verify_downloaded_files` for the file-send option.

That candor matters.
Resilio is not pretending a convenient file handoff is the same thing as a live collaborative subject.

## Where the current page shape still fails

The ordinary operator answer is still reconstructed across too many articles and too many surface classes.

### 1. Snapshot-vs-live truth is still article-dependent

The operator still has to reconstruct whether this is:

- a one-shot transfer
- a reusable open-link snapshot
- a changed-content reissue event
- or a real live shared subject

by hopping across single-file docs, mobile sharing notes, and unrelated sync/share articles.

That is too much reconstruction for one ordinary issuance question.

### 2. Claim ceiling is still prose rather than page truth

Current docs are candid that anyone with the link can redeem it, that use count cannot be capped, and that recipients may re-share even though they cannot change expiry.
But that still is not one ordinary page that answers:

- who can redeem this right now
- how open the claim really is
- what the recipient may do after receipt
- what the sender cannot presently constrain

Those are not side notes.
They are the real authority contract of the handoff.

### 3. Landing-path truth is still surface-scattered

Current docs still split receive location truth across:

- desktop Downloads defaults and desktop path choice
- config-mode / NAS `files_default_path`
- Android's fixed `Downloads/SyncDownloads` inbox
- iOS `Downloads` and `Shared links` views

That means the ordinary answer to `where will this land, and who owns that default` is still scattered.

### 4. History and removal residue still hide in platform exceptions

Current docs are candid that clearing a row is not always clearing bytes, that clearing bytes is not always clearing history, and that expired transfers can still remain in UI.
But the product contract still does not provide one public page that answers:

- what survives if I remove this from the UI
- what survives if I remove local bytes
- whether uploadability / downloadability is over or merely hidden
- how long expired rows may remain visible

That is still too much folklore for one ordinary cleanup decision.

## What AnonSync should do instead

AnonSync should keep the candor and reject the article sprawl.
The product should split this seam into four page families:

1. **Bounded handoff**
   - live subject versus bounded snapshot
   - open-link audience ceiling
   - expiry / never-expire contract
   - changed-content invalidation and reissue rule

2. **Redemption lane**
   - how the recipient claims the handoff
   - whether path choice is available on this surface
   - collision handling and resulting landed name
   - recipient re-share ceiling and non-powers

3. **Receive inbox**
   - current default landing root
   - who owns that default on this seat / surface
   - fixed versus configurable receive path
   - byte visibility and local file-manager relationship

4. **Transfer history**
   - UI row versus local bytes versus still-live claim
   - expired-row retention
   - mobile `Downloads` versus `Shared links` residue
   - later cleanup, resend, or reissue consequences

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that single-file send is a bounded one-way handoff, that audience is open-link rather than approver-shaped, that expiry and reissue are real, and that row clearing and byte clearing diverge by surface. But it is not worth cloning the way ordinary answers to `is this live or bounded`, `who may redeem it`, `where will it land`, and `what survives after I clear it` still sprawl across the single-file article, mobile sharing notes, receive-path defaults, and power-user transfer-history settings instead of one stable page family.

## New replacement pages added in this revision

- `462` Bounded handoff
- `463` Redemption lane
- `464` Receive inbox
- `465` Transfer history
