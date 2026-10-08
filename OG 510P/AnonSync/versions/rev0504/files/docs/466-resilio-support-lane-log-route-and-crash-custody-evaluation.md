# Resilio support lane, log route, and crash custody evaluation

## Why this pass exists

The archive already had diagnostics, evidence custody, external guidance intake, and export/redaction surfaces.
Those were necessary, but another current Resilio pass still exposes a more ordinary operator seam.
The problem is no longer only `how do I gather evidence`.
It is now:

- what exact **support lane** is even real for this product line?
- what exact **capture depth** is active right now, and what extra local residue did that create?
- by what exact **route** will evidence leave this seat?
- what exact **crash artifacts** still remain on disk afterward?

That is where current official Resilio docs stay candid yet still become too article-shaped.

## What current Resilio still gets right

Current official material is still admirably candid about support and diagnostics reality.

Examples the docs still openly describe include:

- **Support lane entitlement is not magical**: current log guides still say direct technical support is available only for Resilio Sync Business customers, while Sync v3 users are pointed toward the community forum and Help Center for functionality questions.
- **Anonymous metrics are distinct from heavier diagnostics**: the current power-user table still keeps `send_statistics` separate from debug logging and profiler capture, and still describes it as anonymous OS/version/activity metrics rather than raw user content.
- **Debug logging is a real state change**: current guides still say debug logging can be enabled in Settings/Preferences or via a `debug.txt` file containing `FFFFFFFF` in the storage folder.
- **Restart is still operationally meaningful**: the same guides still say the operator should restart Sync to make sure debug logging is actually enabled, and the power-user table still says `profiler_enabled` requires client restart.
- **Retention and local footprint are real**: the power-user table still publishes `log_size`, `log_ttl`, and `profiler_enabled`, and still says profiler data is stored as `profiler.dat` in the storage folder and rotated every 10 minutes.
- **Capture windows are real, not instantaneous**: manual, automatic, and mobile debug-log guides still say to let Sync collect logs for at least 15 minutes.
- **Automatic send and manual send are different lanes**: one current guide still sends logs through `Preferences/Settings -> Support -> Contact support` with an `Include logs` flow, while another still explains manual collection, attachment, and upload.
- **Attachment ceilings still matter**: the manual log guide still says only 20 MB attachments are allowed and that larger logs may need a separate upload link.
- **Mobile export has its own hidden ritual**: the mobile debug guide still says the operator must enter `SNC.DBG.LOGS`, then retrieve logs from hidden `.synclogs` storage.
- **Crash artifacts are distinct from debug logs**: the crash-collection guide still separates crash reports, mini dumps, and core dumps, and still gives different storage paths by platform and by Windows service user.
- **NAS core dump collection is explicit outside-the-product work**: the NAS dump guide still says to SSH in, stop Sync gracefully, run `ulimit -c unlimited`, start Sync from the same terminal, wait for a crash, and then move/download the dump.

That candor matters.
Resilio is not pretending that all `send to support` actions are the same thing.

## Where the current page shape still fails

The ordinary operator answer is still reconstructed across too many articles and too many route classes.

### 1. Support entitlement still hides in troubleshooting prose

The operator still has to reconstruct whether they are in:

- self-serve forum/help-center mode
- staffed support mode
- an in-product send lane
- a manual attachment/upload lane

by hopping across log guides and support-section pages.

That is too much reconstruction for one ordinary `who can receive this` question.

### 2. Capture depth still leaks across toggles and helper rituals

Current docs are candid that anonymous stats, debug logging, profiler capture, and crash dumps are not the same thing.
But that still is not one ordinary page that answers:

- what exact collection family is active now
- what restart boundary still remains
- what files are being written locally
- what hold time is still required before send is meaningful

Those are not side notes.
They are the real depth contract.

### 3. Report-send truth is still route-scattered

Current docs still split send truth across:

- in-product `Contact support`
- manual email attachment
- mobile hidden-log extraction
- larger-file upload-link fallback
- NAS / SSH-only crash-capture workflows

That means the ordinary answer to `how does this leave, and what can fail here` is still scattered.

### 4. Crash custody still lives in platform-specific rituals

Current docs are candid that crash artifacts may sit in different directories by OS or service account, and that collection on NAS can require terminal work.
But the product contract still does not provide one public page that answers:

- which crash artifact classes exist here
- where they currently live
- what has already been exported
- what still remains local after export

That is still too much folklore for one ordinary failure-response decision.

## What AnonSync should do instead

AnonSync should keep the candor and reject the article sprawl.
The product should split this seam into four page families:

1. **Support lane**
   - self-serve versus staffed vendor lane
   - private versus public disclosure boundary
   - entitlement proof and current lane limit
   - next admissible disclosure route

2. **Log capture window**
   - capture family (metrics / debug / profiler / crash)
   - activation path and restart requirement
   - hold-time sufficiency
   - local residue and retention

3. **Report send**
   - packet membership and send lane
   - attachment ceiling / fallback upload route
   - route-specific blockers and completion proof
   - what exactly left the machine

4. **Crash artifact**
   - crash-report / minidump / core-dump class
   - current local path and owner/runtime scope
   - export route and sensitivity
   - post-export residue and cleanup proof

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that support and diagnostics have real lane, restart, retention, and crash-custody consequences. But it is not worth cloning the way ordinary answers to `what am I collecting now`, `who can actually receive it`, `how does it leave`, and `what remains local afterward` still sprawl across the power-user table, manual/automatic/mobile log guides, and crash/core-dump articles instead of one stable page family.

## New replacement pages added in this revision

- `467` Support lane
- `468` Log capture window
- `469` Report send
- `470` Crash artifact
