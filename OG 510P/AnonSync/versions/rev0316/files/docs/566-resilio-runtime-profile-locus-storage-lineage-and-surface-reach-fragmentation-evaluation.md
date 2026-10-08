# Resilio runtime profile, storage-root lineage, and surface-reach fragmentation evaluation

## Why this pass exists

The archive already had strong pages for seat posture, posture change, severance, witness locality, cleanup, proxy artifacts, and subject non-arrival.
What it still did not own cleanly enough was one operator question that appears whenever the runtime envelope changes:

- am I still operating the same seat or did I just move to a different runtime locus
- did the storage root stay the same or did the product silently begin reading a different one
- did my shares really migrate, or am I now looking at a fresh profile that merely lives on the same machine
- did control reach, shell affordances, or observation behavior widen or narrow as a side effect
- is this a harmless launch-mode tweak, or a real continuity boundary

Current official Resilio docs still make that seam very real.
They are candid that Windows service mode can run as current user, Local Service, or Local System; that converting to service can either migrate settings or perform a clean installation; that switching a service to Local System can create a new storage folder, show a new welcome flow, surface `SYSTEM` as the default identity name, and require re-add / re-share / reconnect work; that config mode can create a new settings root when `storage_path` changes and only supports Standard folders; that Linux / CLI runtime can move storage and widen WebUI listening scope; and that uninstall guidance still distinguishes unlinking identity, removing shares, and manually deleting per-profile storage roots.

That honesty is useful.
The problem is that the operator still has to reconstruct one ordinary answer from several articles:

> what changed about the effective operating seat when I switched runtime profile, service account, storage path, or control reach?

## What current Resilio still gets right

Current official docs still publish several operational truths worth borrowing.

- **Runtime profile is materially real.** Current service docs still say service mode can run as System, Local Service, or current user and that this changes how the product runs and where it is reachable.
- **Migration versus clean install is named.** Current service-install docs still distinguish `migrate settings and uninstall existing client` from `clean installation`, and they still say the clean path requires re-share and reconnect work.
- **Storage-root shifts are admitted explicitly.** Current storage-folder docs still say settings, databases, identity details, and logs live in the storage folder and that storage locations differ across desktop, service, Local Service, Local System, and config-mode profiles.
- **Service-account switching can produce a fresh control plane.** Current troubleshooting docs still say a Local System switch can create a new storage root, show no old shares, present `SYSTEM` as the default identity name, and require re-add and reconnect.
- **Surface reach is a real policy.** Current troubleshooting and Linux docs still say WebUI defaults to `127.0.0.1`, that reaching LAN clients requires widening the listen address, and that binding to a specific unavailable interface can shut Sync down.
- **Observation quality can narrow.** Current troubleshooting docs still say the Local System workaround loses file-update system notifications and falls back to rescan or restart discovery.
- **Teardown still leaves lineage residue questions.** Current uninstall docs still say unlinking identity and removing shares are optional but affect whether the peer continues to appear offline elsewhere, and storage roots must still be removed separately.
- **The current v3 line is still live.** Official docs still show the v3 line through `3.1.2.1076` dated 31/Oct/2025.

That is strong candor.
Resilio is still willing to admit that runtime profile is not just decoration.

## Where current Resilio still stays too article-shaped

### 1. Runtime locus truth still depends on admin-memory stitching

The ordinary operator should not need to reconstruct from memory whether a given runtime change means:

- `same seat, same root`
- `same seat, migrated root`
- `new root, fresh runtime profile`
- `service principal widened but observation narrowed`
- `control reach widened to LAN`
- `shell / notification affordances changed`
- `identity surface replaced or newly generated`
- `manual re-share / reconnect required`

Current Resilio still tells those truths, but still makes the operator stitch them together from install, troubleshooting, storage, config, Linux, and uninstall pages.

### 2. Profile switch and seat continuity still blur together

These are materially different realities:

- the same seat moved with migrated settings
- the same host now runs a second fresh runtime profile
- the same machine now exposes a broader WebUI surface
- the service principal gained filesystem reach but lost some observation fidelity
- the storage path changed and therefore the operative identity / database set changed

Those distinctions should be first-class product verdicts, not things inferred after opening an unexpectedly empty UI.

### 3. Surface consequences are still too side-note shaped

The operator should not learn only after the switch that:

- the UI is now localhost-only unless reconfigured
- the UI is now LAN-reachable
- shell or notification behavior differs under the new runtime account
- Advanced folders are unavailable in config mode
- the apparent seat label changed because a different runtime profile is now in charge

### 4. Teardown, replacement, and ghost residue still lack one continuity sentence

Unlinking, uninstalling, removing the service, deleting storage roots, and leaving them in place are not the same thing.
Yet the product still does not own one stable answer to:

- what runtime profile remains visible elsewhere
- which offline rows are expected residue versus live seats
- which storage root still holds logs / identity / databases
- whether this was retirement, replacement, or merely shutdown

## What AnonSync should do instead

AnonSync should make **runtime profile continuity** a first-class reviewed object.

The product should own four page families:

1. **Runtime profile review**
   - current execution principal
   - current storage root and profile lineage
   - current identity surface and seat continuity verdict
   - current control / observation surface reach

2. **Storage lineage forecast**
   - requested runtime/profile switch
   - whether shares, databases, and identity are expected to carry forward
   - whether a fresh profile will appear instead
   - what follow-up re-share / reconnect / retire work will be required

3. **Runtime switch review**
   - requested switch versus effective switch
   - migrate versus clean-install choice
   - WebUI reach delta
   - shell / notification / capability delta
   - safe language substitution before apply

4. **Runtime profile receipt**
   - executing principal after apply
   - storage root after apply
   - profile lineage verdict
   - carried-forward versus fresh shares
   - control-surface reach and next obligations

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that service mode, service account, config storage path, and control reach materially change the effective operating locus. But it is not worth cloning the way current operators still have to reconstruct, from several help articles, whether they preserved the same seat, moved to a fresh storage root, lost or widened control surfaces, or now owe manual re-share / reconnect work.

## New replacement pages added in this revision

- `567` Runtime profile review
- `568` Storage lineage forecast
- `569` Runtime switch review
- `570` Runtime profile receipt
