## Revision addendum — Resilio nested overlap, bridge-host propagation, and seed-horizon fragmentation after rev0314

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync FAQ cluster about sharing a nested child folder separately.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that a child shared inside a parent becomes a second subject with a distinct seed horizon?

> where do those same current docs still show that the ordinary operator answer about `who can seed whom, how child edits can still reach parent-only peers, and who pays the extra work?` depends on special-case documentation instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Is it possible to share a nested folder separately?` article, which still says parent and child must both have `Read & Write` or `Owner`, both must have `Selective Sync` disabled, the overlapping host does extra indexing and rescanning, parent-only peers do not seed child-only peers directly, and child-only changes can still reach parent-only peers through the overlapping host.

This pass therefore raises the non-clone confidence again.
The problem is not that Resilio distinguishes graph truth from path truth.
The problem is that the distinction still lives primarily as FAQ knowledge instead of a first-class overlap topology surface.

## Revision addendum — Resilio resource budget, throttling, and hidden-contention fragmentation after rev0313

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about global send/receive limits, scheduler pause semantics, power-user resource knobs, queue priority, hidden internal work, and memory-scale pressure.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that throughput is governed by multiple independent budgets rather than one generic speed state?

> where do those same current docs still show that the ordinary operator answer about `what is slow, why, and who is paying for that slowdown?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Sync Preferences` article, which still says receiving/sending limits apply to internet traffic by default and require `rate_limit_local_peers` to limit LAN too.
- Resilio's current `Running Sync on schedule` article, which still says scheduled `Paused` sets upload and download rates to zero while zero-sized files, deletions, rescans, and indexing continue and paused peers can still upload to non-paused peers.
- Resilio's current `Power user preferences` article, which still exposes `disk_low_priority`, `disk_worker_per_job`, `worker_threads_count`, `rate_limit_local_peers`, `free_space_warning_threashold`, and related knobs that materially alter resource contention and fairness.
- Resilio's current `File download priority` article, which still says prioritization only applies to the active queue up to 50,000 files, that higher-priority files can suspend lower-priority downloads, that some internal exceptions remain, and that the UI view may not reflect true priority order.
- Resilio's current `Some internal tasks are taking time to complete` article, which still says hidden disk/network work such as block checking, hashing, merging, reading, and writing can consume time and slow visible progress.
- Resilio's current `Out of memory` article, which still says Sync keeps the whole tree and deleted entries in memory/database and may need a remove-and-readd cycle to truly shrink RAM use.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that `performance` is really a multi-budget story
- but current Resilio still answers `what is slow and why?` too diffusely
- AnonSync should therefore prefer first-class resource budgets, budget provenance, starvation warnings, bottleneck proofs, and durable receipts over performance folklore

## Revision addendum — Resilio raw-state cloning, seat duplication, and successor-import gap after rev0312

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about unsupported cloning, storage-folder contents, per-install certificates, and identity replacement.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that copying Sync state is dangerous?

> where do those same current docs still show that the ordinary operator answer about `replacement versus duplicate versus backup` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Cloning Sync` article, which still says cloning a Sync instance by plain copy, drive cloners, or Time Machine style copying is not supported and may create multiple instances that do not transfer to one another and exhibit strange behavior.
- Resilio's current `Sync Storage folder` article, which still says the storage folder keeps current configuration, auxiliary settings files, and shares' database state.
- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says each installation gets a unique digital certificate and fingerprint even when two independent installations use the same identity name.
- Resilio's current `Can I change the name of my Sync identity?` article, which still says identity replacement requires unlinking and generating a new certificate rather than editing one field in place.

The sharper AnonSync reading is therefore not `go ahead and clone state` and not merely `forbid cloning and call it a day`.
It is: raw copied state must never silently count as reviewed continuity; the product needs a first-class reviewed successor-import contract instead.

## Revision addendum — Resilio invocation profile, launch ritual, and runtime-world fragmentation

Current official Resilio docs are still admirably candid that `starting Sync` is not one flat verb: the Windows CLI page still says `/config`, `/webui`, `/storage`, `/noinstall`, `/S`, and `/minimized` materially change startup shape; the Linux guide still says `--storage` chooses where settings, identity, and license live and that without it `.sync` is created in the current directory; that same Linux guide still says `--webui.listen` defaults to `127.0.0.1`, can widen to all interfaces, and can even shut Sync down if pinned to an unavailable interface; the config-mode guide still says a non-default `storage_path` creates settings there and that service config mode works only from service storage; the Windows service troubleshooting guide still says a Local System switch lands in a different storage folder with no old shares visible; and the current v3 update guide still says non-default `/config` or `/storage` launches and Linux binary installs preserve configuration only if relaunched with the same parameters and the same user. That is valuable operational honesty. It is also a strong non-clone signal, because one ordinary operator answer — `what runtime world am I actually starting, where will state live, and what visibility/exposure consequences follow?` — still depends on hopping between CLI help, Linux notes, config-mode instructions, service troubleshooting, and update ritual instead of one owned page family.

The tighter AnonSync response is therefore: treat **invocation profile** as a first-class reviewed object, make quietness separate from stop truth, make storage-root choice explicit world adoption, and require receipts whenever launch materially changes world lineage, visibility, or control exposure.

## Revision addendum — requester proof, human-label collision, and linked-family trust scope after rev0308

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about identity naming, device naming, certificate fingerprints, approval flow, X509 issuance, ACL signing, and linked-device auto-approval widening.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that the requester visible to a human is not the same thing as the proof handle used for trust?

> where do those same current docs still show that the ordinary operator answer about `who exactly am I approving, and how far does that trust travel?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says each installation gets a unique digital certificate and random fingerprint; that two independent instances can share the same identity name while still having different certificates; that fingerprints are used so others know which Sync installation is connecting; and that a remote user can choose to automatically approve all linked devices for future sharing.
- Resilio's current `Link structure and flow` article, which still says the requester sends a public key; the approver is shown the requester's user name and public-key fingerprint; the approver can compare the fingerprint; and only after approval does the owner issue an X509 certificate and sign an ACL entry.
- Resilio's current `Settings on mobile platforms` article, which still exposes identity name, device name, and certificate fingerprint together as the bundle shown to other users.
- Resilio's current `Comprehensive guide to syncing (Desktop-Desktop)` article, which still distinguishes linked-device sharing automation from manual sharing and reinforces that trust/rights travel differently depending on the lane.

## Additional Resilio official sources emphasized in rev0309

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Link structure and flow  
  https://help.resilio.com/hc/en-us/articles/204754739-Link-structure-and-flow

- Settings on mobile platforms  
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- Comprehensive guide to syncing (Desktop-Desktop)  
  https://help.resilio.com/hc/en-us/articles/204754939-Comprehensive-guide-to-syncing-Desktop-Desktop

## Revision addendum — time authority, timestamp provenance, and replay chronology

Another current official Resilio pass sharpens the same conclusion: borrow the candor, do not clone the contract.

The useful Resilio truths are real:
file ordering really does depend on `mtime`; peer clock and timezone really do matter; the ordering basis really is normalized to GMT; skew tolerance really is an explicit budget; visible filesystem timestamps really can diverge from chronology-authoritative database timestamps; and archive restore really can fail to stick because the restored candidate comes back older than current peer state.

The non-clone problem is also real:
one ordinary operator answer — `which timestamp actually governs ordering, replay, and visible truth right now?` — still spans time-difference warnings, onboarding tips, power-user `mtime` settings, and archive-restore instructions.

That means present-day Resilio still externalizes too much meaning into documentation archaeology.
AnonSync should instead own time authority as one page family with temporal authority sheet, clock-skew review, timestamp provenance proof, replay chronology review, and durable receipt continuity.

## Revision addendum — completion horizons, freshness proof, and hidden lag

Another current official Resilio pass sharpens the same conclusion: borrow the candor, do not clone the contract.

The useful Resilio truths are real:
status really is relative to a horizon; a green check really does speak only about connected peers; `X of Y` really does widen the horizon to include offline peers; offline peers really can age out according to policy; hidden background work really can continue under a generic warning; and detection really can lag behind reality because notifications, rescans, and storage class materially matter.

The non-clone problem is also real:
one ordinary operator answer — `is this actually complete and fresh, relative to whom, and with what remaining debt?` — still spans desktop status notes, peer-count semantics, troubleshooting steps, background-task docs, change-detection docs, and old UI-observability lineage.

That means present-day Resilio still externalizes too much meaning into documentation archaeology.
AnonSync should instead own completion/freshness as one page family with completion boundary sheet, claim review, freshness proof, stale peer debt watch, and durable receipt continuity.

## Revision addendum — permission metadata, principal mapping, and apply ceilings

Another current official Resilio pass sharpens the same conclusion: borrow the candor, do not clone the contract.

The useful Resilio truths are real:
permission metadata really is operationally significant; create-time-fixed permission policy really does exist for several current job families; NTFS modes really do differ in semantics; runtime principal really does decide what can be applied; non-native targets really can preserve permission intent without native enforcement; and target-side identity mapping really can be the deciding failure condition.

The non-clone problem is also real:
one ordinary operator answer — `are permissions part of the truth here, and under what exact principal/mapping assumptions does that claim actually hold?` — still spans feature docs, job-class docs, runtime-principal requirements, cross-platform caveats, and troubleshooting pages.

That means present-day Resilio still externalizes too much meaning into documentation archaeology.
AnonSync should instead own permission metadata as one page family with metadata-authority class, permission sync review, principal mapping proof, failure review, and durable receipt continuity.

## Revision addendum — removal verbs, residue planes, and survivor boundaries

Another current official Resilio pass sharpens the same conclusion: borrow the candor, do not clone the contract.

The useful Resilio truths are real:
disconnect really is different from remove; disconnected subjects really can exist without local paths; Selective Sync removal really can clear placeholders from the local file system; `Remove from this device` really is different from placeholder deletion that propagates to peers; linked-identity removal really is narrower than share-global deletion; hiding an offline device really is not unlink; and uninstall really can leave shared folders or `.sync/Archive` behind on desktop while deleting synced material on iOS.

The non-clone problem is also real:
one ordinary operator answer — `what exactly disappears, from where, for whom, and what residue or comeback path survives if I press this remove-like verb?` — still spans disconnect/remove docs, placeholder docs, power-user settings, hidden-device cleanup, uninstall instructions, and platform-specific notes.

That means present-day Resilio still externalizes too much meaning into documentation archaeology.
AnonSync should instead own typed removal as one page family with verb disambiguation, survivor scope, local residue, remote remainder, reconnect risk, comeback risk, and durable receipt continuity.

## Revision addendum — identity linking, certificate takeover, and hidden-device residue

Another current official Resilio pass sharpens the same conclusion: borrow the candor, do not clone the contract.

The useful Resilio truths are real:
identity really is certificate-backed; `My Devices` really is an adoption-style feature rather than raw-key folklore; the direction of an `M`-key link really matters; version-mixed linking can break control-plane expectations; linking two already-running seats can replace a certificate and evict Advanced folders; iOS really can pay a stronger filesystem price; unlink really is local-only; and hidden offline devices really can remain latent members rather than disappearing.

The non-clone problem is also real:
one ordinary operator answer — `what exactly happens if I link or unlink this seat?` — still spans one identity guide, one offline-device cleanup article, and a separate architecture comparison between Standard and Advanced folders.

That means present-day Resilio still externalizes too much meaning into documentation archaeology.
AnonSync should instead own identity merge as one page family with seat lineage, adoption direction, takeover impact, unlink boundary, latent residue truth, and receipt continuity.

## Revision addendum — transfer eligibility, pause truth, and context-gated movement

Another current official Resilio pass sharpens the same conclusion: borrow the candor, do not clone the contract.

The useful Resilio truths are real:
pause is not total stasis; scheduler `Paused` is not identical to full stop; auto-sleep can make the core actually disappear from peer view and later wake; battery saver can force a stop; mobile-data policy and per-share network restriction are real gates; and lowered background priority can change whether work continues.

The non-clone problem is also real:
one ordinary operator answer — `will bytes move now, and if not, what still mutates anyway?` — still spans pause docs, scheduler docs, mobile settings, auto-sleep/battery docs, per-share network docs, and background-priority caveats.

That means present-day Resilio still externalizes too much meaning into documentation archaeology.
AnonSync should instead own transfer eligibility as one page family with lane truth, gate provenance, wake witness, proof ceiling, and receipt continuity.

## Further current clone-veto seam — shared substrate, runtime identity, and write-path boundary truth

Current official Resilio docs are still admirably candid that `folder path` is not one clean semantic class: current `Sync and SMB file shares` docs still say Sync can work with SMB shares only with caveats, requiring full permissions, warning that only `SMB 3.0+` supports notifications, and warning that third-party access outside SMB can damage or roll back files; current `How soon does synchronization start?` docs still say filesystem notifications are the fast path but can be unavailable on storages such as `NFS` and `SMB2` mounted shares, with scheduled scan every `600` seconds as fallback; current `Locked files` docs still say another application can block transfer and that Sync can list blocked files but still cannot identify the locking process; current `Power user preferences` still publish `enable_file_system_notifications` and `recheck_locked_files_interval`; and current `Sync Service Troubleshooting on Windows` docs still say a service cannot see mapped drive letters created at interactive logon, recommends a UNC-style path instead, warns that this loses update notifications so changes are detected on rescan or restart, and says switching the service to `Local System` creates a different storage folder and empty/new Sync state that requires re-adding and re-sharing folders.

That candor is useful.
The current shared-substrate contract is not worth cloning.

Current Resilio still spreads the ordinary answer to `what storage and writer topology do I really have here?` across SMB caveats, notification timing docs, locked-file troubleshooting, power-user tuning, and service-account namespace notes.

AnonSync should therefore keep the candor and replace the page shape with:

- **Storage substrate contract sheet** — one place that classifies the subject as local fs, network share, service-visible UNC, mixed-writer topology, or unknown
- **Shared substrate topology review** — one review surface that states runtime identity, authoritative path namespace, notification floor, and write-lane boundary before apply
- **Lock contention watch** — one watch surface for blocked objects, unknown locker truth, and retry cadence
- **Mixed access boundary warning** — one full-page review for direct-host plus SMB writer collisions, rollback hazard, and safer topology ladders
- **Substrate lineage receipt** — one durable receipt preserving storage class, runtime actor, authoritative path, degradation grade, and forbidden stronger claim

## Further current clone-veto seam — activation latency, proof-of-effect, and non-retroactivity truth

Current official Resilio docs are still admirably candid that `changed` is not one clean semantic class: the active v3 line still runs through `3.1.2.1076`; current `Ignoring files in Sync (Ignore List)` docs still say IgnoreList is reread on change or every `folder_rescan_interval` if notifications are absent, still recommend restart for immediate application, and still say the rule does not affect files that already synced while already-indexed structure remains passed to peers until disconnect; current `How soon does synchronization start?` docs still say scheduled rescan runs every 600 seconds and on Sync start and that `folder_rescan_interval = 0` disables rescans even on restart; current `Setting Delay Time For Syncing` docs still say `FileDelayConfig` is edited in the storage folder as JSON and requires restart; current `Collecting debug logs manually` docs still say debug logging should be followed by restart and at least 15 minutes of collection; current `Power user preferences` still say `profiler_enabled` requires restart and still publish `config_refresh_interval`, `config_save_interval`, and `folder_rescan_interval`.

That candor is useful.
The current activation contract is not worth cloning.

Current Resilio still spreads the ordinary answer to `is my change real yet?` across IgnoreList timing notes, change-detection/rescan docs, hidden storage-file ritual, debug/profiler restart notes, and power-user timing tables.

AnonSync should therefore keep the candor and replace the page shape with:

- **Effect activation contract sheet** — one place that classifies the change as immediate, reread-bound, rescan-bound, restart-bound, startup-bound, external-proof-bound, or future-only
- **Activation latency review** — one review surface that states what becomes true now, later, or never retroactively
- **Pending effect watch** — one watch surface for staged-only, live-unverified, live-proven, stale-proof, and superseded states
- **Policy effect verification** — one verification surface that names witness scope and non-retroactivity honestly
- **Activation lineage receipt** — one durable receipt preserving route, trigger, proof class, residue, and supersession


## Revision addendum — automatic ingress mutation and port-lease truth after rev0293

Another current official Resilio pass still strengthens the same broad conclusion: the product remains useful to study precisely because it is candid that easier directness can require explicit or automatic ingress work. Current official docs still say the listening port handles incoming/outgoing UDP plus incoming TCP, that manual port forwarding should target that same port, that `Use UPnP port mapping` makes Sync send UPnP and NAT-PMP packets to the router automatically, that some printers/scanners/other network equipment may mis-handle those packets and stop processing network requests, that direct peer connection depends on the listening port being opened and forwarded through firewalls/NATs/routers after discovery and before relay fallback, that config mode still exposes an `upnp` field alongside listening-port / proxy / WebUI ownership, and that current speed-troubleshooting guidance still treats direct port mapping as a practical remedy for relay dependence.

That is excellent substance.
The non-clone issue is that too much of the operator-facing meaning still has to be reconstructed from preferences prose, ports/protocols architecture, config notes, and troubleshooting lore.
AnonSync should therefore keep the distinctions and replace the checkbox-shaped contract with ingress-mutation sheets, auto-port-map reviews, mapping-lease watches, router-side-effect warnings, and receipts.

## Revision addendum — artifact-family opacity and epoch-fork truth after rev0287

Another current official Resilio pass still strengthens the same broad conclusion: the product remains useful to study precisely because it is honest about token families and continuity forks.
Current official docs still say only Standard folders use raw keys; key type is materially encoded by the first character; `F` is encrypted custody that cannot decrypt names or content; `M` links devices into one identity family; links carry a temporary key and require an approval flow that culminates in X509 certificate issuance and ACL mutation; and changing a raw key is not distributed automatically, so old-key peers continue syncing among themselves while the changed peer moves to a new epoch.

That is excellent substance.
The non-clone issue is that too much of the operator-facing meaning still has to be inferred from token internals and separate support articles.
AnonSync should therefore keep the semantic distinctions and replace the opaque-token contract with inspected artifact objects, issuance previews, intake reviews, fork warnings, and receipts.


## Revision addendum — priority/residency split, sticky neutral traps, and ghost-risk promise ceilings after rev0286

Current official Resilio docs are still admirably candid that `first in queue`, `visible as placeholder`, `fetchable`, and `safely promised local` are not the same truth: the current `File download priority` article says the feature is available in `3.1.0`, says per-share and global defaults both exist, says shares with manually altered priority stop inheriting later global changes even if later set back to `None`, says only active queued files are prioritized up to a limit, says higher-priority arrivals suspend lower-priority work with internal exceptions, and says single-file sending uses a separate immutable rule once started; current `Synchronization Modes`, `Selective Sync`, and `What Is an RSLS File?` docs still say placeholders are names-only local absence, that fetching a subtree can later auto-download new descendants there, and that `Remove from this device` differs materially from `Remove from all devices`; current `Selective Sync` and `Disconnecting and Removing Folders` docs still warn that removing or disconnecting a selective-sync share removes placeholders from the local filesystem; current `Power user preferences` still publish `folder_defaults.transfer_priority`, `disable_remove_from_all_devices`, and `recreate_placeholders_on_removal`, while also saying one destructive guard is ignored in Linux WebUI; and current `Cannot download files` docs still say some announced items are ghost files that nobody retains in full.

That is real candor.
It still does **not** earn direct interface cloning.

The reason is the next clone-veto rule now applied to another seam:

> one ordinary operator question should have one stable page answer.

Current Resilio still spreads the ordinary residency-promise answer across priority docs, placeholder docs, removal docs, power-user defaults, and warning prose.
So the product idea stays useful while the page contract still fails.

That is why this revision adds five narrower replacement pages:

- `863` Residency intent page
- `864` Residency policy review page
- `865` Residency budget page
- `866` Hydration queue admission page
- `867` Residency promise receipt page

These pages keep the Resilio candor and reject the need to improvise guarantee strength from queue order, default inheritance trivia, placeholder menus, and later warning popups.

## Revision addendum — service/browser control, install-path splits, and destructive-toggle sprawl after rev0285

Current official Resilio docs are still admirably candid that browser control and destructive folder behavior are ordinary operational reality: the live v3 line still runs through `3.1.2.1076`; current `Running Sync as a service on Windows` docs still say Sync can run regardless of logged-in-user state and opens WebUI in the default browser; current `Installing Sync package on Linux` docs still publish manual, repository, and official Docker-image install modes while also separating personal `v3` from Business `v2.8.1`; current `Download Sync` pages still say personal/non-commercial only and warn NAS users not to update Sync Business to `v3`; current `Configuring WebUI` and browser-warning docs still normalize bind choice, self-signed HTTPS, and browser exceptions; current Android interface docs still expose `Use Archive` and `Overwrite changed files` as normal per-share controls.

That is real candor.
It still does **not** earn direct interface cloning.

The reason is the next clone-veto rule now applied to another seam:

> one ordinary operator question should have one stable page answer.

Current Resilio still spreads the ordinary dangerous-control answer across install docs, service docs, product-line docs, WebUI/browser-trust docs, desktop preferences, and mobile share settings.
So the product idea stays useful while the page contract still fails.

That is why this revision adds five narrower replacement pages and component families:

- `857` Danger session capsule
- `858` Trust bootstrap review page
- `859` Salvage export page
- `860` Salvage export receipt page
- `861` Destructive execution ticket page

These pages keep the Resilio candor and reject the need to reconstruct dangerous-control meaning from scattered operational prose.

## Revision addendum — maintenance mutation budgets, suspended continuity, and overwrite folklore after rev0281

Current official Resilio docs are still admirably candid that `safe to look here` and `safe to work here` are not the same thing: the active v3 line still runs through `3.1.2.1076`; current `User Management` docs still say a Read Only peer that modifies files or adds new ones will not propagate those changes and that further synchronization of the changed files will be suspended for that peer; current `Folder Preferences` docs still say `Overwrite any changed files` on Read Only shares will overwrite local changes, including files the operator added, and warn that the option is potentially destructive, while also saying the option is disabled for Read-only folders with Selective Sync ON; current `Encrypted folders` docs still say encrypted backup nodes are Read Only, always have `Overwrite any changed files` activated, and do not allow Selective Sync; current `How to Back up data (Android only)` docs still say backup intentionally preserves copies even after later deletion on the phone and that the desktop side has read-only access so changes do not sync back; current `Sync Interface on iOS devices` docs still say `Remove from this device` disconnects the folder only on that iOS device and removes files there while preserving them on others.

That is real candor.
It still does **not** earn direct interface cloning.

The reason is the next clone-veto rule now applied to another seam:

> one ordinary operator question should have one stable page answer.

Current Resilio still spreads the ordinary maintenance-local-mutation answer across permission docs, folder preferences, encrypted-backup docs, backup docs, and mobile remove semantics.
So the product idea stays useful while the page contract still fails.

That is why this revision adds four narrower replacement pages:

- `837` Maintenance mutation budget page
- `838` Maintenance mutation review page
- `839` Maintenance mutation ledger page
- `840` Maintenance mutation receipt page

These pages keep the Resilio candor and reject the need to improvise mutation fate from several unrelated feature articles.

## Revision addendum — maintenance intent overload, semantic islands, and missing hold-class review after rev0280

Current official Resilio docs are still admirably candid that `maintenance` is not one semantic class: the active v3 line still runs through `3.1.2.1076`; current `How to pause syncing` docs still say pause stops only bits transfer while zero-sized files and deletions still sync and new files are rescanned and indexed; current `Running Sync on schedule` docs still say scheduled `Paused` is only a speed-zero posture, still preserves those residuals, and can still let paused peers upload to non-paused peers while not downloading themselves; current `Is one-way synchronization possible?` docs still say Read Only permission gives one-way sync where changes made in the read-only folder do not sync back; current `How to Back up data (Android only)` docs still say backup intentionally preserves copies and that the desktop side has read-only access so changes do not sync back.

That is real candor.
It still does **not** earn direct interface cloning.

The reason is the next clone-veto rule now applied to another seam:

> one ordinary operator question should have one stable page answer.

Current Resilio still spreads the ordinary maintenance-intent answer across pause docs, scheduler docs, read-only docs, backup docs, and remembered side effects.
So the product idea stays useful while the page contract still fails.

That is why this revision adds four narrower replacement pages:

- `832` Maintenance intent page
- `833` Maintenance semantics review page
- `834` Maintenance transition plan page
- `835` Maintenance contract receipt page

These pages keep the Resilio candor and reject the need to improvise a maintenance contract from several unrelated feature articles.

## Revision addendum — backlog-release cliffs, return caps, and post-quiet order ambiguity after rev0279

Current official Resilio docs are still admirably candid that leaving quiet is not one neutral state change: the active v3 line still runs through `3.1.2.1076`; current `Running Sync on schedule` docs still say empty cells mean full bandwidth available and unchecked upload/download means full bandwidth for that direction, while scheduled `Paused` still leaves specific residual behaviors alive; current `File download priority` docs still say per-share priority and global `folder_defaults.transfer_priority` can both shape order, that manual share priority stops inheriting later global changes even if later set back to `None`, that only up to 50,000 active files are prioritized, that higher-priority arrivals suspend lower-priority work with some internal exceptions, that non-splittable files do not fully obey strict prioritization, and that the visible queue may still appear alphabetical rather than true execution order; current `Power user preferences` still publish `folder_defaults.transfer_priority` as a standing default plane.

That is real candor.
It still does **not** earn direct interface cloning.

The reason is the next clone-veto rule now applied to another seam:

> one ordinary operator question should have one stable page answer.

Current Resilio still spreads the ordinary post-quiet release answer across scheduler prose, priority docs, power-user defaults, and queue caveats.
So the product idea stays useful while the page contract still fails.

That is why this revision adds four narrower replacement pages:

- `827` Backlog release plan page
- `828` Backlog order review page
- `829` Backlog release timeline page
- `830` Backlog release receipt page

These pages keep the Resilio candor and reject the need to infer how the backlog will actually come back to life.

## Revision addendum — local pause, global pause, and quiet-cohort agreement after rev0276

Current official Resilio docs are still admirably candid that pause is partial and origin-bearing: the active v3 line still runs through `3.1.2.1076`; current `How to pause syncing` docs still say pause means only bits download/upload are stopped while zero-sized files and deletions still sync and new files are rescanned and indexed; those same docs still say Global Pause affects all shares on the current device; current `Sync Preferences` docs still present Global Pause / Resume and Scheduler as ordinary local controls; current `Running Sync on schedule` docs still say scheduled `Paused` means upload/download speed are zero while zero-sized files and deletions still sync, new files are rescanned and indexed, and paused peers may still upload to non-paused peers while not downloading themselves; and the still-published historical changelog still records `Sync stopping indexing if folder paused`.

That is real candor.
It still does **not** earn direct interface cloning.

The reason is the next clone-veto rule now applied to another seam:

> one ordinary operator question should have one stable page answer.

Current Resilio still spreads the ordinary quiet-cohort answer across pause how-to, preferences, scheduler prose, and changelog archaeology.
So the product idea stays useful while the page contract still fails.

That is why this revision adds four narrower replacement pages:

- `812` Quiet cohort page
- `813` Quiet agreement review page
- `814` Quiet window request page
- `815` Quiet cohort receipt page

These pages keep the Resilio candor and reject the need to infer whether local pause became shared stillness.
## Revision addendum — dormant return, re-entry, and stale-claim fragmentation after rev0275

Current official Resilio docs are still admirably candid that not every return means ordinary healthy continuity: the active v3 line still runs through `3.1.2.1076`; current `Does Sync work in background?` docs still say shutdown/re-open reindexes folders, gives them a new modification time, and can let offline updates overwrite changes made by peers that stayed online; current `Sync Main View (Desktop)` docs still say offline peers are disconnected from the folder after 7 days; current `Power user preferences` still names `peer_expiration_days` with default `7 (day)`; current `How to clear offline devices? (desktop only)` docs still say hiding an offline device only hides it from view and that it can reappear later if it comes back online; current `"Time difference" error` docs still say clock/timezone drift beyond 600 seconds invalidates chronology and that mobile peers may show empty lists; current `Cannot download files` docs still say some announced items are ghost files that nobody retains in full.

That is not abandonment or product confusion.
It is real operator-oriented candor.

It still does **not** earn direct interface cloning.

The reason is the same clone-veto rule now applied to another seam:

> one ordinary operator question should have one stable page answer.

Current Resilio still spreads the ordinary re-entry answer across background/runtime notes, main-view peer aging, power-user settings, hidden-device cleanup guidance, clock warnings, and ghost-file/source-absence prose.
So the product idea stays strong while the page contract still fails.

That is why this revision adds four narrower replacement pages:

- `807` Re-entry case
- `808` Dormancy timeline
- `809` Stale-return review
- `810` Re-entry receipt

These pages keep the Resilio candor and reject the stale-return reconstruction path.

## Revision addendum — Resilio still names duty ingredients, but not one late-claim object after rev0274

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's opportunity and lateness contracts**

This time the evidence is especially clear around **background/runtime class, wake intervals, notification priority, battery/network gates, watcher fallbacks, and due-time honesty**.

Current official docs still openly distinguish real opportunity facts such as:

- desktop hidden runtime continuing to sync while iOS lacks background synchronization
- Android background work being vulnerable to task killers and notification-priority loss
- Android Auto Sleep waking on a configured interval, 30 minutes by default
- Battery Saver stopping Sync below a chosen charge threshold
- Wi-Fi-only or forbidden-network posture removing the current observation opportunity until policy clears
- watcher exhaustion and UNC/service path classes downgrading discovery to periodic or manual rescan
- the active v3 line still appearing through `3.1.2.1076`

That candor is good.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed into several help articles before the product fully owns these questions:

- when this exact seat will next get a real chance to notice or fetch the change
- whether `late` is premature because the next honest opportunity has not arrived yet
- which prerequisite still matters more than elapsed wall-clock time
- what stronger sentence is still forbidden right now: `stuck`, `ignored`, or `background sync failed`

AnonSync should therefore make **next-observation opportunity** and **late-claim review** first-class product objects.
Every serious missing-update incident should render duty class, unmet prerequisites, next opportunity, due verdict, and safe language before the product treats elapsed time as proof of failure.

## Revision addendum — sidecar benchmarking, capacity isolation, and tuning-cost honesty after rev0269

Another current official Resilio pass sharpens one more reason to **adapt, not clone**.
Current official Resilio docs are still admirably candid that `slow` may require both a live Sync diagnosis and a raw-path isolation experiment: the current `Download/upload speed is very slow` article still names many-small-file overhead, relay use, asymmetrical peers, low-capacity hardware, security software delay, `disk_low_priority`, closed listening ports, predefined hosts, and log escalation; the current `How can I improve data transfer/sync speed?` article still prefers direct connections, same-LAN or VPN paths, predefined hosts, `rate_limit_local_peers false`, `lan_encrypt_data false`, and `disk_low_priority false`; the current `Power user preferences` article still publishes the defaults for `rate_limit_local_peers` and `lan_encrypt_data`; the current `Some internal tasks are taking time to complete` article still says hashing, deduplication, merging, scanning, reading, writing, and transfer are separate hidden operations; `Measuring network performance with iperf3` still says Sync should be shut down completely on both peers during tests and still prescribes forward/reverse TCP and UDP runs; and the current `Resilio Sync 3.0 change log` still shows the active line through `3.1.2.1076`.

That candor is useful.
The non-clone problem is still experiment ownership.
One ordinary operator answer is still scattered across troubleshooting prose, tips, power-user settings, internal-task warnings, and terminal ritual:

> what exact speed question are we isolating, what had to become quiet first, what did the benchmark really prove, and which next tuning change is actually justified?

So this pass promotes four replacement pages:

- **Measurement plan page** — question class, baseline Sync observation, peer-pair scope, quiescence contract, and comparison rules
- **Sidecar benchmark run page** — participant roles, stop/quiet proof, command rows, observed outputs, and validity verdict
- **Performance hypothesis review page** — supported bottleneck hypothesis, candidate interventions, semantic/security cost, and reversible test plan
- **Measurement receipt page** — baseline-versus-benchmark summary, supported bottleneck statement, approved next step, and reopen boundary

The doctrine stays the same:

- **borrow Resilio's practical candor**
- **do not clone its sidecar-benchmark and tuning-folklore contract**

## Revision addendum — instrumentation-posture mutation, restart truth, and baseline-return honesty after rev0268

Another current official Resilio pass sharpens one more reason to **adapt, not clone**.
Current official Resilio docs are still admirably candid that evidence can require changing runtime posture first: the current `Collecting debug logs automatically` and `Collecting debug logs manually` guides still say operators may enable debug logging in settings or via hidden `debug.txt`, should restart Sync to make sure it is enabled, and should gather at least 15 minutes of post-reproduction logs; the current manual guide still says large estates may need larger log size; the current `Increasing Debug Log size` guide still says default rotation is `100 Mbytes`, still says `sync.log` is backed up to `sync.log.old`, still says operators should raise `log_size` to `200` or more and restart, and for older Linux/NAS versions still falls back to editing `settings.dat`; the current `Power user preferences` article still lists `log_size 100 (MB)`, `log_ttl 7 (day)`, and `profiler_enabled false`, and still says `profiler_enabled` writes `profiler.dat`, rotates it every 10 minutes, and requires restart to activate; and the current `Resilio Sync 3.0 change log` still shows the active line through `3.1.2.1076`.

That candor is useful.
The non-clone problem is still posture ownership.
One ordinary operator answer is still scattered across support prose, advanced settings, hidden files, and restart ritual:

> what temporary diagnostic posture is active, how does it differ from baseline, what restart or dwell debt remains, and has the product really returned to normal afterward?

So this pass promotes four replacement pages:

- **Instrumentation plan page** — baseline posture, proposed deltas, capture purpose, and cost/retention budget
- **Instrumentation change review page** — exact changed control or hidden route, restart truth, activation verdict, and side-effect scope
- **Instrumentation restore review page** — return-to-baseline plan, retained residue, deferred cleanup, and reopen triggers
- **Instrumentation posture receipt page** — baseline at start, active deltas during capture, restoration state, and claim ceiling

## Revision addendum — raw-artifact intake, cleanup ritual, and provenance-preserving normalization after rev0267

Another current official Resilio pass sharpens one more reason to **adapt, not clone**.
Current official Resilio docs are still admirably candid that evidence often starts messy: the current `Collecting debug logs manually` guide still names `sync.log` plus rotated zip logs and still varies their location by platform, service account, package mode, and config mode; the current `How to collect logs on NAS manually?` guide still says to copy the whole Sync internal-data folder and then clean it up leaving only `*.log`, `*.log.zip`, and `*.journal`; the current `Collect debug logs on mobiles` guide still uses the `SNC.DBG.LOGS` action and hidden `.synclogs` folder; the current crash/core-dump guides still vary file names and locations across `.dmp`, crash-report folders, and gzipped core dumps; and the current `Resilio Sync 3.0 change log` still shows the active line through `3.1.2.1076`.

That candor is useful.
The non-clone problem is still intake ownership.
One ordinary operator answer is still scattered across support prose and platform ritual:

> what raw material was actually harvested, what class it belongs to, what cleanup changed, and how much provenance survived before packet assembly?

So this pass promotes four replacement pages:

- **Raw evidence intake page** — raw-source identity, witness/platform/path provenance, and artifact-family typing
- **Artifact normalization review page** — keep/prune/extract/rename actions, oversharing warnings, and provenance preservation
- **Packet assembly review page** — normalized members, duplicate/rotation grouping, split posture, and lineage confidence
- **Intake normalization receipt page** — raw-source inventory, normalized outputs, exclusions, and claim ceiling

## Revision addendum — recipient-ask fragmentation, return binding, and follow-up fulfillment honesty after rev0266

Another current official Resilio pass sharpens one more reason to **adapt, not clone**.
Current official Resilio docs are still admirably candid that later asks have real structure: the current `Collecting debug logs automatically` guide still says to indicate which support ticket the logs refer to plus role, timestamp, detailed description, and affected shares/files; the current `Collecting debug logs manually` guide still says to attach logs in reply to the support ticket, upload through the support portal, mention the forum link when redirected from Forums, and ask support for a larger upload link when attachments exceed 20 MB; the current mobile and NAS guides still leave manual return steps visible; and the current `Resilio Sync 3.0 change log` still shows the active line through `3.1.2.1076`.

That candor is useful.
The non-clone problem is still ask ownership.
One ordinary operator answer is still scattered across support prose and portal ritual:

> what exactly did the recipient ask for, how must the answer bind back to the existing case, and what strongest sentence is justified about satisfaction after the return?

So this pass promotes four replacement pages:

- **Recipient ask page** — requested clauses, requester lane, binding token, and satisfiability posture
- **Ask fulfillment review page** — clause coverage, missing members, excess disclosure, and satisfaction sentence
- **Return lane review page** — reply chain, payload fit, size limits, and upload-link preconditions
- **Ask fulfillment receipt page** — ask version, returned members, binding proof, and reopen boundary

## Revision addendum — public-thread/private-packet coupling, companion-case absence, and redaction-boundary honesty after rev0265

Another current official Resilio pass sharpens one more reason to **adapt, not clone**.
Current official Resilio docs are still admirably candid that public discussion and private evidence are not the same audience situation: the current `I still have questions, where can I get answers?` article still sends users toward the forum while also saying they can contact support, with PRO users first to get response and FREE users answered to the extent possible; the current `Collecting debug logs automatically` guide still says the operator should indicate which support ticket the logs refer to, plus peer role, timestamps, detailed description, and affected shares/files; the current `Collecting debug logs manually` guide still says that if the operator was redirected there from Forums they should mention the forum link when sending logs through the support web portal; the current log/crash/dump guides still repeat the Business-only direct-support language for technical support while Sync v3 functionality help is routed toward forum/help-center self-service and payments/licensing toward a web form; and the current `Resilio Sync 3.0 change log` still shows the active line through `3.1.2.1076`.

That candor is useful.
The non-clone problem is still companion-case ownership.
One ordinary operator answer is still scattered across forum posts, support forms, manual references, and private packets:

> what is safe to say publicly, what must stay private, and what durable object proves that these artifacts belong to the same case?

So this pass promotes four replacement pages:

- **Companion case page** — public summary and private packet siblings, audience split, and linkage state
- **Public summary review page** — public-safe claim, repro summary, redaction boundary, and utility verdict
- **Private companion linkage page** — thread/ticket reference, packet purpose, private-only details, and continuity verdict
- **Companion-case receipt page** — public artifact state, private artifact state, linkage proof, and continuation boundary

## Revision addendum — escalation-lane entitlement, destination ambiguity, and response-ceiling honesty after rev0264

Another current official Resilio pass sharpens one more reason to **adapt, not clone**.
Current official Resilio docs are still admirably candid that support/help lanes differ: current `Collecting debug logs automatically`, `Collecting debug logs manually`, and current crash/core-dump guides still say technical support is available exclusively for Resilio Sync Business customers, while Sync v3 functionality questions should go to the community forum and Help Center and payments/licensing should use a web form; the same automatic-log guide still tells the operator to open an in-app `Contact support` form; the current `I still have questions, where can I get answers?` article still says users can also contact support with PRO users first to get response and FREE users answered to the extent possible; the current `Licensing in Resilio Sync 3.0` article still says Business licenses are not compatible with Sync v3 and commercial users should continue using Sync v2 or explore business solutions; and the current `Resilio Sync 3.0 change log` still shows the active line through `3.1.2.1076`.

That candor is useful.
The non-clone problem is still lane ownership.
One ordinary operator answer is still scattered across help-center prose and chrome:

> which route is actually valid for this question and product line, who will receive this package, and what response is honestly plausible after send?

So this pass promotes four replacement pages:

- **Escalation lane page** — available routes, entitlement basis, audience class, and package expectations
- **Escalation review page** — lane comparison, package-fit verdict, privacy/visibility consequences, and redirect triggers
- **Destination confirmation page** — recipient class, package purpose, audience visibility, and follow-up expectation
- **Escalation lane receipt page** — chosen lane, entitlement basis, destination class, delivery state, and reopen boundary


## Revision addendum — evidence-plan absence, artifact-class sprawl, and package opacity after rev0263

Another current official Resilio pass sharpens one more reason to **adapt, not clone**.
Current official Resilio docs are still admirably candid that serious troubleshooting may want different artifact classes: the current `Send info to Support team` section still distributes separate guides for automatic logs, manual logs, mobile logs, crash reports / dumps, NAS dumps, iperf3, and log-size tuning; `Collecting debug logs automatically` still distinguishes Biz-only direct support from Sync v3 self-service, and still keeps manual fallback lanes visible; `Collecting debug logs manually` still names concrete log files and platform-specific storage paths; `Collect debug logs on mobiles` still uses a hidden-folder route and special `SNC.DBG.LOGS` action; `Measuring network performance with iperf3` still says Sync should be shut down on both peers during the test; `Increasing Debug Log size` still documents 100 MB rotation and no mobile adjustment; and the current `Resilio Sync 3.0 change log` still shows the active line through `3.1.2.1076`.

That candor is useful.
The non-clone problem is still package ownership.
One ordinary operator answer is still scattered across support guides:

> what artifact classes does this incident really need, what preconditions made them trustworthy, and what exactly was exported?

So this pass promotes four replacement pages:

- **Evidence plan page** — diagnostic question, requested artifact families, preconditions, and claim budget
- **Artifact capture matrix page** — participant/platform rows, collection route, disruption cost, and return state
- **Evidence manifest page** — actual members, sensitivity findings, completeness verdict, and export readiness
- **Evidence export receipt page** — plan version, manifest version, transport lane, delivery state, and stale boundary

## Revision addendum — incident brief, symptom timestamps, and coordinated capture-run honesty after rev0262

Another current official Resilio pass sharpens one more reason to **adapt, not clone**.
Current official Resilio docs are still admirably candid that raw artifacts need event context: the current `Collecting debug logs automatically` guide still says to reproduce the issue, let Sync collect logs for at least 15 minutes, and write the peer role, timestamp, detailed problem description, and affected shares/files into feedback text; that same guide still says the operator should not close the application/device until log sending is reported done; the current `Collecting debug logs manually` guide still says to describe the issue and mention the forum link if redirected from Forums; the current `My files don't sync` article still routes diagnosis through peers, warnings, history, and queues before heavier capture; and the current `Resilio Sync 3.0 change log` still shows the active line through `3.1.2.1076`.

That candor is useful.
The non-clone problem is still capture-brief ownership.
One ordinary operator answer is still scattered across troubleshooting prose and support guides:

> what exact symptom are we chasing, when did it happen, which subjects and participants define the event, and did this run actually catch it inside a usable evidence window?

So this pass promotes four replacement pages:

- **Incident brief page** — problem statement, time anchors, affected subjects, and reusable short brief
- **Symptom bookmark page** — observed event anchor, time quality, and later capture alignment
- **Coordinated capture run** — participants, steps, dwell floor, and success-window semantics
- **Capture brief receipt** — claimed symptom, actual run outcome, and usable evidence window

## Revision addendum — witness-set scope, peer-role annotation, and completeness honesty after rev0261

Another current official Resilio pass sharpens one more reason to **adapt, not clone**.
Current official Resilio docs are still admirably candid that evidence scope is incident-shaped: the current `Peers aren't connecting` article still says to collect debug logs from two peers that cannot connect; the current `My files don't sync` and `How can I improve data transfer/sync speed?` articles still end with collect-logs-from-all-peers guidance for persistent trouble; the current `Collecting debug logs automatically` guide still asks the operator to explain the role of that peer in the setup, plus timestamps and affected shares/files; the current `Collecting debug logs manually` guide still keeps packet size and upload-route limits visible; and the current `Resilio Sync 3.0 change log` still shows the active line through `3.1.2.1076`.

That candor is useful.
The non-clone problem is still witness ownership.
One ordinary operator answer is still scattered across troubleshooting articles and log guides:

> which peers matter for this incident, what role does each one play, what evidence is owed by each, and when is the witness set complete enough for an honest claim?

So this pass promotes four replacement pages:

- **Incident witness set page** — minimal participant set, role typing, and evidence duty
- **Witness request page** — one participant-specific evidence ask with target window and privacy envelope
- **Witness completeness review** — required returns, missing witnesses, contradiction map, and claim ceiling
- **Witness-set receipt** — participant scope, actual returns, and reopen boundary

## Revision addendum — incident object, investigation continuity, and proof-sufficiency honesty after rev0260

Another current official Resilio pass sharpens one more reason to **adapt, not clone**.
Current official Resilio docs are still admirably candid that diagnosis is multi-surface work: the current `Sync Main View (Desktop)` article still presents History as a separate 30-day activity surface and says `X of Y` opens the peers list; the current `My files don't sync` article still tells operators to click peers counts, click status warnings that often lead to KB explanations, search Sync History, inspect queues from peers lists, and only then work through a long checklist; the current `Locked files` article still says the error row opens a list of locked files but cannot identify the locking application; the current debug-log guides still require enabling debug logging, restarting Sync, collecting at least 15 minutes of logs, and sometimes using manual or fallback send lanes; and the current `Resilio Sync 3.0 change log` still shows the active line through `3.1.2.1076`.

That candor is useful.
The non-clone problem is still investigation ownership.
One ordinary operator answer is still scattered across row clicks, peers lists, history search, queue inspection, and support/log articles:

> what investigation am I in, what have I already checked, which explanation is strongest, what exact proof is still missing, and is heavier capture justified yet?

So this pass promotes four replacement pages:

- **Diagnostic incident page** — durable investigation home, current best explanation, and live alternatives
- **Incident timeline** — one chronology for rows, history, route hops, and interventions
- **Evidence sufficiency review** — what current proof already supports and what heavier capture would actually add
- **Diagnostic conclusion receipt** — winning explanation, rejected alternatives, and reopen boundary

## Revision addendum — warning taxonomy, blast radius, and least-strong repair after rev0258

Another current official Resilio pass sharpens one more reason to **adapt, not clone**.
Current official Resilio docs are still admirably candid that warning rows do not all mean the same thing: the active v3 line still runs through `3.1.2.1076`; current `Core warnings` docs still separate tracker/bootstrap trouble, low space on the default-folder-location disk, failed folder-list / identity sync, and license-management disablement; current `Service files missing` docs still say synchronization for that folder is suspended and that repair may require remove/re-add after Archive check and `.sync` cleanup; current `Some internal tasks are taking time to complete` docs still say the condition may be intermittent and recoverable rather than a hard stall; current `Time difference` docs still say chronology trust is invalidated when peer clocks or timezone settings are wrong and that mobile may show empty lists; and current `Cannot download files` docs still say some announced items may have no remaining full source peers.

That candor is useful.
The non-clone problem is still warning ownership.
One ordinary operator answer is still scattered across warning articles and troubleshooting prose:

> what kind of warning is this, how wide is it, what is the least-strong honest next rung, and what did clearing or acknowledging it actually prove?

So this pass promotes four replacement pages:

- **Warning page** — class, seriousness, scope, and safe sentence
- **Blocker scope** — seat / subject / item / hidden-state blast radius and blocked stronger actions
- **Recovery rung** — least-widening repair ladder and escalation boundary
- **Warning history** — acknowledgement, repair, recurrence, and residue continuity

## Revision addendum — paused label, origin split, and named-state honesty after rev0257

Current official Resilio docs are still admirably candid that `Paused` is not one absolute freeze. The current `How to pause syncing` article still says pause means only bits upload/download are stopped, while zero-sized files and deletions still sync and new files are still rescanned and indexed. The current `Running Sync on schedule` article still says scheduled `Paused` means upload/download speed are zero, yet paused peers can still upload files to non-paused peers while not downloading themselves; that same article still says deletions sync anyway and indexing continues. `Sync Preferences` still keeps Global Pause and Scheduler adjacent as ordinary controls.

That candor is worth borrowing.
The non-clone problem is again page ownership.
Current Resilio still spreads the ordinary operator answer to `what exactly does Paused mean here, and why does it mean something slightly different in another origin?` across a manual pause how-to, scheduler docs, and a preferences page rather than one stable product-owned posture/review/evidence/receipt family.

AnonSync should therefore keep the candor and replace the contract with one explicit named-state family.

## Revision addendum — replay class, piece-shift full resend, and edition-gated stronger delta after rev0256

Current official Resilio docs are still admirably candid that changed-file replay is not one stable truth: the public Sync FAQ still says files are split into pieces from `32 KB` to `2 MB`, that only changed pieces are usually transferred, but that a piece-shifting edit can still force a whole-file resend; the same FAQ still says Sync Business has diff-delta sync for that case. Official Resilio documentation for other job families still says administrators may disable differential sync and intentionally prefer whole-file replay, or keep differential replay enabled and pay the extra local hash/recheck cost instead.

That candor is worth borrowing.
The non-clone problem is again page ownership.
Current Resilio still spreads the ordinary operator answer to `what replay class is active here, how could the next edit narrow it, and what stronger class is unavailable?` across a consumer FAQ, enterprise/job-profile documentation, and workload-tuning guidance rather than one stable product-owned posture/review/evidence/receipt family.

AnonSync should therefore keep the candor and replace the contract with one explicit replay-class family.

## Revision addendum — name-plane reset, outward-artifact freshness, and disconnect residue after rev0255

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about custom share names, local-only UI labels, sharing-time alias insertion, QR regeneration, reset-after-disconnect residue, and local-only folder renames.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that one share can have several simultaneously real names for different audiences?

> where do those same current docs still show that the ordinary operator answer about `which name is actually current here, and is the outward artifact still fresh after rename work?` still depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Setting custom name for sync shares` article, which still says a custom UI name does not rename the folder on disk, does not propagate to linked devices, can be changed while sharing so a different label is inserted into a link or QR, requires QR regeneration after rename, and remains in the UI after disconnect until explicit `Reset`.
- Resilio's current `Can I move or rename a syncing folder?` article, which still says renaming a synced folder affects only the device where it is renamed.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the active v3 line through `3.1.2.1076`.

That is useful candor.
The non-clone problem is workflow ownership.
Current Resilio still lets one ordinary answer about `which name plane is live, which one is residue, and whether the outward artifact is fresh enough to distribute` leak across a tips article, rename guidance, and operator memory.

The archive now owes four more first-class pages:

- **Name posture**
- **Name change review**
- **Artifact label freshness**
- **Name receipt**

These pages are required whenever a share can otherwise hide the difference between local title, disk basename, outward alias, disconnect residue, and stale artifact state.

## Revision addendum — indirection objects, platform split, and target non-transitivity after rev0253

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about soft links, hard links, symbolic links, junction fallout, and `.Conflict` generation.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that a path row can be an indirection object with a materially different fidelity contract than an ordinary file or folder?

> where do those same current docs still show that the ordinary operator answer about `is this object syncing, is its target syncing, or is this just a conflict generator here?` still depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Soft links, hard links and symbolic links` article, which still says Windows does not support these link classes and that they may create `.Conflict` entries, while Unix can synchronize symbolic links as links but not automatically synchronize the target folders.
- Resilio's current `Conflict files in Sync` article, which still names linked junctions as a concrete cause of `.Conflict` files or folders.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the active v3 line through `3.1.2.1076`.

That is useful candor.
The non-clone problem is workflow ownership.
Current Resilio still lets one ordinary answer about `what exactly is syncing here — the indirection object, the target bytes, both, or neither?` leak across a link article and conflict troubleshooting.

The archive now owes four more first-class pages:

- **Indirection posture**
- **Indirection action review**
- **Target transitivity proof**
- **Indirection receipt**

These pages are required whenever an entry that looks file-like or folder-like could otherwise hide platform-dependent object survival, target exclusion, conflict hazard, or graph-widening side effects.

## Revision addendum — identity actions, subject-class fallout, and mobile byte-deletion asymmetry after rev0252

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about identity linking, renaming an identity, uninstall sequencing, subject-class fallout, and platform-specific file deletion.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that identity verbs are not merely account verbs, but can change local subject governance and byte survival differently by class and platform?

> where do those same current docs still show that the ordinary operator answer about `what survives this identity action on this seat?` still depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says linking two already-running installs can make one device lose its certificate, remove Advanced folders from the app, and copy folders from the other instance, while iOS deletes those Advanced folders from the file system because of platform architecture.
- Resilio's current `Can I change the name of my Sync identity?` article, which still says renaming means unlinking and creating a new identity, removes Advanced folders from the instance, preserves Standard folders differently, and keeps folders in the system except on iOS and Windows Phone.
- Resilio's current `How to uninstall Sync?` article, which still says operators should unlink from identity first, then remove remaining Standard shares, and that iOS and Windows Phone uninstall removes synced files from the device.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the active v3 line through `3.1.2.1076`.

That is useful candor.
The non-clone problem is workflow ownership.
Current Resilio still lets one ordinary answer about `is this just identity housekeeping, or am I also dropping subjects and maybe deleting local bytes on this platform?` leak across linking docs, an identity FAQ, and uninstall guidance.

The archive now owes four more first-class pages:

- **Identity-action review**
- **Subject-fate matrix**
- **Preserve-before-identity-action**
- **Identity-action receipt**

These pages are required whenever an identity-looking verb could otherwise be flattened into `unlink`, `rename`, `link`, or `uninstall` without publishing requested verb, subject-class fallout, platform-local byte fate, preserve-first alternatives, and strongest safe sentence.

## Revision addendum — hydration engine, shell/provider lane, and history/collision ceiling after rev0251

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about classic Selective Sync placeholders, shell/context-menu dependencies, recent macOS Selective Sync fixes, and a second official Resilio hydration engine on Windows whose history/conflict guarantees differ from legacy expectations.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `Selective Sync` is not one stable contract but several different hydration engines and local action lanes?

> where do those same current docs still show that the ordinary operator answer about `what exactly can this online-only mode promise here?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Selective Sync` article, which still says Selective Sync can mean placeholder-only arrival, that linked-device defaults can make new files arrive as `.rsl` placeholders, and that removing a Selective Sync share removes placeholders from that device.
- Resilio's current `No Sync icons in the file browser/no Sync-related items in the context menu on Mac/Windows` article, which still says Selective Sync file-browser actions depend on Finder extension health on macOS and on NTFS/alternate-data-stream support plus shell registration on Windows.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line and still records a recent fix for missing context-menu items in Selective Sync shares on macOS.
- Resilio's current `Transparent Selective Sync (TSS) on Windows` article, which still says TSS is a different engine from legacy Selective Sync, is enabled by default there, requires specific Windows/API/path prerequisites, narrows Archive/history behavior on v3.x and older, disables file-edit collision detection there on those older lines, and names co-tenant/runtime risks such as OneDrive on-demand, second-agent use, inherited Cloud API flags, mounted-network-share roots, and some VMware disk modes.

The tighter AnonSync conclusion from this source set is now simple:

> borrow Resilio's candor that partial materialization is a real product contract and that local prerequisites genuinely matter; refuse any interface where one friendly `Selective Sync` label still hides engine kind, lane health, rollback ceiling, conflict ceiling, and co-tenant invalidation risk.

## Further current clone-veto seam — permission-plane mode, reference authority, and inheritance rewrite after rev0250

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **permission-plane posture / permission-plane change review / permission-apply evidence / permission-plane receipt**

Current official Resilio docs still say permission synchronization has distinct modes rather than one behavior; those settings are still applied at job creation for several job families and are not freely mutable later; NTFS still distinguishes `Don't sync Owner`, `Sync full ACL`, and `Re-apply local inherited permissions`; the local re-inheritance mode still exists because partial downloads pass through the service `.sync` directory; compatible permissions can still be preserved on incompatible storage and applied only when the file later lands on NTFS or POSIX substrate; local admin / Local System / root and, over SMB, stronger service-account rights can still be required; a Reference Agent is still recommended or required when pre-seeded RW peers would otherwise merge or scramble permissions; and current pre-seeded guidance still says file permissions can participate in the `needs sync` comparison itself.
That candor is useful.
The non-clone problem is still permission-plane ownership.

Ordinary operators can still be pushed into several official docs before the product fully owns these questions:

- what exact permission mode is active here right now
- whose permission meaning is authoritative if RW peers already disagree
- whether this seat is actually applying permissions, merely preserving them for later, or intentionally re-inheriting locally
- whether the local runtime has enough privilege to justify the claim being made
- whether permission drift is part of sync comparison or only final apply behavior

AnonSync should therefore make **permission-plane posture** and **permission-apply evidence** first-class product objects.
Every serious permission-bearing subject should render mode, authority basis, apply substrate, privilege floor, comparison participation, and receipt language before the product treats `sync permissions` or `preserve ACLs` as self-explanatory.

## Further current clone-veto seam — hidden StreamsList locality, xattr courier stubs, and ignore-boundary split after rev0249

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **attribute-plane posture / attribute-policy change review / attribute-courier evidence / attribute-plane receipt**

Current official Resilio docs still say xattrs and alternate streams sync according to a whitelist stored in hidden `.sync/StreamsList`; that whitelist is still an editable regular text file inside the share; xattrs still cannot be ignored through `IgnoreList`; unsupported filesystems can still force Sync to store metadata in hidden `.sync/Streams` stubs so it can later propagate onward; and disabling xattr syncing can still expose bundle-like macOS objects as ordinary subdirectories.
That candor is useful.
The non-clone problem is still attribute-plane ownership.

Ordinary operators can still be pushed into several help pages before the product fully owns these questions:

- is this seat preserving object meaning natively or only couriering hidden metadata onward
- which channels are in scope because of a visible policy versus a hidden share-local whitelist
- why ordinary exclusion rules do not govern this metadata plane
- whether narrowing metadata carriage is only hidden fidelity loss or visible object-shape change
- what sentence is still allowed afterward: `native fidelity`, `courier-only`, `shape risk`, or `reduced meaning plane`

AnonSync should therefore make **attribute-plane posture** and **attribute-courier evidence** first-class product objects.
Every serious metadata-carriage decision should render policy basis, visible-vs-hidden control locality, native-vs-courier fate, object-shape risk, and receipt language before the product treats xattr carriage as hidden implementation detail.

## Latest addendum — copy-looking trees, hidden control carry, and subject-copy illusion after rev0248

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **copied-tree posture / managed-tree intake review / control-state detachment / copy-like intake receipt**

Current official Resilio docs still say every synced folder gets a hidden `.sync` directory that is critical for synchronization; `.sync/ID` is how Sync recognizes the same share on a device; deleting or corrupting `.sync` suspends sync; two Sync instances touching the same folder or the same external-drive storage can corrupt internal state; raw `Cloning Sync` is unsupported; and trying to add the whole home folder can fail because Sync's own storage folder with a `License` directory sits inside it.
That candor is useful.
The non-clone problem is still copy intuition.

Ordinary operators can still be pushed into several help pages before the product fully owns these questions:

- is this tree only copied payload, or payload plus hidden managed identity
- did controller state come along from this runtime, a sibling runtime, or a foreign world
- is the honest next step same-subject attach, inspect-only, clean branch, detachment, or block
- if hidden state is stripped, which witnesses disappear with it
- what sentence is still allowed afterward: `same managed subject`, `copied payload branch`, `foreign managed carry`, or `blocked pending proof`

AnonSync should therefore make **copy-looking tree posture** and **managed-tree intake** first-class product objects.
Every serious copy/import/restore/reuse action should render payload-versus-control carry, subject-identity basis, hidden-state fate, continuity result, and receipt language before the product treats a folder copy as self-explanatory.

## Latest addendum — local protection, Files-app Recents loss, and copy-return edit boundary after rev0247

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **local protection / protection change review / external edit lane / local protection receipt**

Current official Resilio docs still say iOS `Touch ID & passcode` protection hides files from Files-app `Recents`, iOS outside-app editing imports a copy that must be sent back manually, Sync may not be able to replace the original automatically, local iOS storage remains sandbox-shaped, and Windows Phone passcode recovery can require reinstall with local in-app data loss.
That candor is useful.
The non-clone problem is still workflow ownership.

Ordinary operators can still be pushed into several mobile help articles before the product fully owns these questions:

- what exactly became less visible to the operating system when local protection was enabled
- whether `Open in another app` means live provider editing or only copy-return branch editing
- whether the original can be replaced automatically or whether the operator will see old/new siblings
- whether losing the local secret only blocks access or actually lowers the local recovery ceiling
- what sentence the product is still allowed to say afterward: `protected`, `hidden from Recents`, `copy-return only`, or `reinstall may be required`

AnonSync should therefore make **local protection** and **external edit lane** first-class product objects.
Every serious local-protection toggle and outside-app handoff should render OS-visibility delta, edit-lane class, replacement capability, recovery ceiling, and receipt language before the product treats `protected` or `Edit in...` as self-explanatory.

## Further current clone-veto seam — substrate truth, notify gaps, and mixed-writer hazard

Another current Resilio pass sharpens one more reason to **adapt, not clone**:

- **substrate posture / substrate admission review / mutation-channel evidence / substrate-risk receipt**

Current official Resilio docs still show a useful product, but they also still show that one ordinary answer to `is this connected share actually safe and prompt on this path?` can still depend on:

- whether the path is really local-native or a mounted/networked substrate
- whether filesystem notifications work here or whether detection falls back to scheduled rescans
- whether locks can be diagnosed in-product or only by external tooling and restart
- whether app-edit conflict is being handled by per-type delay tuning instead of one substrate-aware explanation
- whether unmanaged channels can mutate the same bytes outside the share protocol and create corruption or rollback risk

So the tighter non-clone line is:

> borrow Resilio's candor that storage substrate matters, but refuse any product contract where a share can look ordinarily connected while notification gaps, lock uncertainty, or mixed-writer corruption risk are only visible in scattered help pages and advanced knobs.

That yields four more ordinary product-owned pages:

- **Substrate posture**
- **Substrate admission review**
- **Mutation-channel evidence**
- **Substrate-risk receipt**

## Further current clone-veto seam — backup-subject mode bypass, storage-only connected appearance, and subject-kind override

Another current Resilio pass sharpens one more reason to **adapt, not clone**:

- **subject-kind override / arrival-exception review / storage-only arrival posture / subject-kind override receipt**

Current official Resilio docs still show a useful product, but they also still show that one ordinary answer to `does this seat default still apply to this subject?` can still depend on:

- whether linked-device sync modes are being read as the whole arrival contract
- whether mobile backup is a storage-only subject that may still auto-land connected on destination desktops regardless of that mode
- whether a connected-looking row is actually collaborative or only a read-only sink with no destination-to-source writeback
- whether disconnect/reconnect is being used as a posture repair rather than one explicit exception object
- whether later operators can prove that the standing default was bypassed on purpose instead of merely misconfigured

So the tighter non-clone line is:

> borrow Resilio's candor that backup/storage-only subjects are real and that seat defaults can have carve-outs, but refuse any product contract where a subject kind can silently outride the standing arrival default and still present as an ordinary connected share.

That yields four more ordinary product-owned pages:

- **Subject-kind override**
- **Arrival-exception review**
- **Storage-only arrival posture**
- **Subject-kind override receipt**

## Revision addendum — linked-family owner default, self-observer detour, and seat-role proof after rev0244

Another current official Resilio pass still exposes one more page-shaped reason not to clone Resilio wholesale.

Current docs are still candid that personal linked-device convenience and seat-role awkwardness are both real.
They still say all of the following:

- current `Sync Private Identity & Linking My Devices` docs still say once devices are linked, all folders automatically become available on all linked devices and approvals can be handled from any linked device where the folder is active
- current `User Management` docs still say that when data is shared across devices linked to one identity, all of those devices act as Owners
- current `Sync functionality in detail` docs still repeat that linked devices share one common folder list and approval convenience across the linked set
- current `Is one-way synchronization possible?` docs still say Advanced folders do not allow Read Only synchronization across linked devices
- current `How to create a Read Only folder while syncing across linked devices?` docs still say that getting one of your own linked devices into a Read Only posture requires a Standard folder with a Read Only key, disconnecting the already connected folder if needed, manually entering the key, and manually choosing the target location
- current `What's the difference between Standard and Advanced folders?` docs still say Standard and Advanced differ architecturally, that only Advanced supports on-the-fly permission changes and Owner, and that Standard uses keys while Advanced uses PKI/certificates
- the active v3 line still appears through `3.1.2.1076`

That is useful candor.
The non-clone problem is workflow ownership.
Current Resilio still lets one ordinary answer about `what role does this one of my own devices really have, and how do I intentionally narrow it?` leak across linking docs, permission docs, one-way-sync docs, a separate read-only how-to, and folder-class comparison docs.

The archive now owes four more first-class pages:

- **Seat role**
- **Self-narrowing review**
- **Relationship-versus-seat authority**
- **Seat-role receipt**

These pages are required whenever a personal seat role could otherwise be flattened into `linked device`, `Owner`, `Read Only`, or `Standard vs Advanced` without publishing role basis, native-versus-detour narrowing, subject-lineage cost, and safe post-commit language.


## Revision addendum — non-authority local edits, destructive auto-heal, and path-local continuity after rev0243

Another current official Resilio pass still exposes one more page-shaped reason not to clone Resilio wholesale.

Current docs are still candid that `Read Only` is not one simple thing.
They still say all of the following:

- current `User Management` docs still say Read Only peers cannot propagate their edits and that further synchronization of changed files is suspended for that peer unless `Overwrite any changed files` is used
- current `Is one-way synchronization possible?` docs still spell out concrete per-change-class behavior, including rename staying local while the old name is re-downloaded, deleted files being restored, edited files reverting to upstream state, and added files not being synced back
- current `Folder Preferences` docs still say `Overwrite any changed files` is potentially destructive and is disabled for Read-only folders with Selective Sync ON
- current `Folder Types and Management` docs still say local changes on a Read Only folder may cause the peer to stop receiving updates to those files depending on local settings
- current `Encrypted folders` docs still say encrypted peers are Read Only, always have overwrite enabled, and do not offer Selective Sync
- current `User Management`, `Is one-way synchronization possible?`, and `How to create a Read Only folder while syncing across linked devices?` docs still show that linked devices act as Owners, Advanced folders do not offer Read Only across linked devices, and a manual Standard-folder / Read-Only-key / disconnect detour is still required to get a Read Only copy on one of your own devices
- the active v3 line still appears through `3.1.2.1076`

That is useful candor.
The non-clone problem is workflow ownership.
Current Resilio still lets one ordinary answer about `what happens if I edit locally on this non-authority copy?` leak across permission docs, one-way-sync behavior docs, destructive preference text, encrypted-backup docs, and linked-device workaround docs.

The archive now owes four more first-class pages:

- **Non-authority edit posture**
- **Non-authority local-change review**
- **Affected-path continuity**
- **Non-authority edit receipt**

These pages are required whenever a non-authority local copy could otherwise be flattened into one reassuring badge such as `Read Only`, `backup`, or `mirror` without publishing per-change-class fate, future-update continuity, forced-policy limits, and safe post-event language.


## Revision addendum — Archive toggle, replay dependence, and local recovery ceiling after rev0241

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about Archive policy, rename replay through Archive, mobile share-detail controls, retention/access limits, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that `Use Archive` is not just old-version retention, but also part of rename/copy replay behavior and platform-local recovery limits?

> where do those same current docs still show that the ordinary operator answer about `what exactly do I lose if I turn Archive off here?` still depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Folder Preferences` article, which still says Archive stores remotely changed or deleted prior versions and that disabling it also makes remote renames or copies re-download instead of replaying locally.
- Resilio's current `What happens when file is renamed` article, which still says remote rename efficiency depends on Archive because the old name is moved to Archive and later restored under the new name when the hash matches.
- Resilio's current `Using Archive for file versioning and restoring deleted files` article, which still says retention defaults differ by desktop and mobile, Android Archive does not work for SD-card shares, and Archive is not accessible on iOS.
- Resilio's current `Sync interface on Android` and `Sync Interface on iOS devices` articles, which still expose `Use Archive` as a per-share control, with iOS explicitly tying renamed-file processing to Archive and Android limiting Archive to internal phone memory.
- Resilio's current v3 change log, which still shows the live `3.1.2.1076` line.


## Revision addendum — timestamp winner authority, clock confidence, and loser-preservation proof after rev0240

Another current official Resilio pass still exposes one more page-shaped reason not to clone Resilio wholesale.

Current docs are still candid that chronology and loser preservation are real.
They still say all of the following:

- current `Can I connect two pre-populated pre-existing folders?` docs still say that if same files have different hash, the one with latest timestamp will be synced, replacing the file on the remote peer
- current `What if several people make changes to the same file?` docs still say changes normally replay in chronological order, but that the latest file that comes online can take priority even over later online edits, with overwritten versions placed in Archive
- current `Time difference` docs still say Sync decides which file is newer by comparing modification times converted to GMT and that more than 600 seconds of clock or time-zone drift triggers warnings while mobile devices may show empty lists
- current `Using Archive for file versioning and restoring deleted files` docs still say restored files rely on Sync already running, otherwise a later rescan may compare modified times and archive the restored file again as older
- the active v3 line still appears through `3.1.2.1076`

That is useful candor.
The non-clone problem is workflow ownership.
Current Resilio still lets one ordinary answer about `why is this version winning and what happened to the loser?` leak across pre-populated-folder FAQ prose, conflict FAQ prose, time-difference warnings, and Archive restore instructions.

The archive now owes four more first-class pages:

- **Same-path winner review**
- **Decision chronology evidence**
- **Losing-version fate**
- **Divergence-resolution receipt**

These pages are required whenever a same-path winner could otherwise be flattened into `latest timestamp`, `newer`, `restored`, or `overwritten version placed in Archive` without publishing chronology confidence, ranking basis, loser fate, and safe post-commit language.

## Revision addendum — safe reconnect, risky merge, and overloaded `Folder not empty` warnings after rev0239

Another current official Resilio pass still exposes one more page-shaped reason not to clone Resilio wholesale.

Current docs are still candid that non-empty target binds are real.
They still say all of the following:

- current `Folder not empty` docs still say the same warning appears both when adding shared files into an already existing folder and when reconnecting a folder to a location where it synced before
- the same article still warns that files already present in the receiving folder might be deleted or overwritten
- the same article also still says that when reconnecting to the old location the operator should ignore the warning and proceed
- current `Can I connect two pre-populated pre-existing folders?` docs still say click `OK` on the non-empty confirmation and, on linked devices, often route the operator through `Disconnected` posture or disconnect/reconnect ritual before selecting the existing directory
- current `Disconnecting and Removing Folders` docs still say reconnect may propose a different default path, may create a `(1)` sibling, and may again ask the operator to accept `Destination folder is not empty. Add anyway?`
- current manual-location guidance for linked devices still says custom placement is reached by putting the seat into `Disconnected` mode first
- the active v3 line still appears through `3.1.2.1076`

That is useful candor.
The non-clone problem is workflow ownership.
Current Resilio still lets one ordinary answer about `is this old-tree restore or risky merge?` leak across warning prose, reconnect guidance, pre-populated-folder instructions, and seat-mode ritual.

The archive now owes four more first-class pages:

- **Same-lineage reconnect proof**
- **Non-empty target divergence review**
- **Preserve-before-adopt**
- **Reconnect-vs-merge receipt**

These pages are required whenever a non-empty target could otherwise be flattened into one `Folder not empty` / `Add anyway` warning without publishing same-lineage proof, compared classes, preservation options, and safe post-commit language.

## Revision addendum — manual-bind right, default-root scope, and duplicate-suffix fallback after rev0238

Another current Resilio pass now sharpens one more reason to **adapt, not clone**.

Current official Resilio docs still show a product that is fairly candid about arrival-placement reality:

- the current `Synchronization Modes` article still says linked devices use three modes and that the selected device mode shows up under identity settings
- the current `How to manually set the location of the folders synced across linked devices?` article still says when `Selective Sync` or `Synced` are enabled, new folders go into the default folder, and that to choose custom location for later linked-device arrivals the operator should switch that device into `Disconnected`
- the current `Disconnecting and Removing Folders` article still says reconnect may propose a default path different from the original one and may create a `(1)` duplicate folder if the same name already exists
- the same reconnect guidance still says Android may show `Destination folder is not empty. Add anyway?` when reconnecting to the old directory
- the current `Settings on mobile platforms` and `Simple Mode (Android)` articles still say Android default folder / Simple Mode auto-place new shares and add `(1)` on same-name collision
- the current help center now clearly shows a split release history: the dedicated v3 change log is active through `3.1.2.1076`, while the older `Resilio Sync change log` page covers previous versions through `2.8.1.1390`

That is useful candor.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed across several documents before the product fully owns these questions:

- whether the current choice is changing **this share** or the seat's **future arrivals**
- whether the suggested path is merely a default-root hint or a trustworthy continuity proposal
- whether a same-name existing folder is intended continuation, unrelated local material, or duplicate risk
- whether reconnect truly restored continuity or only created a fresh sibling directory
- what exact sentence the product is still allowed to say after a non-empty-target `add anyway` path

That means AnonSync should become **more explicit than Resilio about one-share bind right and duplicate-veto truth**, not less candid than Resilio about default roots and reconnect behavior.

## New page obligations added in this pass

The archive now owes four more first-class pages:

- **Future-arrival defaults**
- **Bind choice review**
- **Existing-folder adoption review**
- **Arrival bind receipt**

These pages are required whenever arrival placement, reconnect, or existing-folder adoption can plausibly be read as stronger continuity than the evidence supports.

## Revision addendum — sync-mode meaning, current-vs-future split, and clear/disconnect return contract after rev0237

Another current Resilio pass now sharpens one more reason to **adapt, not clone**.

Current official Resilio docs still show a product that is fairly candid about mode reality:

- the current `Sync functionality in detail` article still says linked devices expose `Disconnected`, `Selective Sync`, and `Synced` as three different synchronization modes
- the current `Synchronization Modes` and `Sync Preferences` articles still say device-level default connect mode affects how later linked-device arrivals land
- the current `What Is an RSLS File?` article still says placeholder files are zero-byte proxies created by Selective Sync or Connected mode
- the same article still distinguishes `Remove from this device` from `Remove from all devices`
- the current Android and iOS interface articles still say `Clear`/`Clear synced files` revert local files to placeholders when Selective Sync is on
- the current disconnect/reconnect articles still say disconnect preserves the folder in the filesystem, while reconnect may propose a different default path and create a `(1)` duplicate
- the current Android Simple Mode and mobile-settings docs still say new shares can be auto-placed in default folders and collision-suffixed with `(1)`
- the current v3 line still appears active through `3.1.2.1076`

That is useful candor.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed across several documents before the product fully owns these questions:

- whether the visible mode is describing the **current share** or the **seat default for future arrivals**
- whether the current local state is disconnected, names-only, placeholder-backed, or fully materialized
- whether the path is original, reviewed, default-proposed, reconnect-derived, or duplicate-suffixed
- whether `Clear`, `Remove from this device`, and `Disconnect` preserve the same after-state or different return contracts
- what exact sentence the product is still allowed to say about local presence after the action

That means AnonSync should become **more explicit than Resilio about sync-mode meaning and return contract**, not less candid than Resilio about useful mode concepts.

## New page obligations added in this pass

The archive now owes four more first-class pages:

- **Current sync mode**
- **Sync mode change review**
- **Clear-versus-disconnect review**
- **Sync mode receipt**

These pages are required whenever a mode chip, toggle, or mobile share detail can plausibly be read as stronger explanation than it really provides.

## Revision addendum — rule-agreement truth, ignore-ledger shared meaning, and exclusion claim ceilings after rev0236

Another current Resilio pass now sharpens one more reason to **adapt, not clone**.

Current official Resilio docs still show a product that is fairly candid about ignore-rule reality:

- the current IgnoreList article still says excluded files are not indexed and are not counted in the Size column
- the same article still says having the same IgnoreList on all peers is `advisable, but not compulsory`
- the same article still says IgnoreList is case sensitive and that path delimiters differ by OS
- the same article still says ignore rules do not work for files already synced
- the same article still says structural information is still passed until disconnect
- the current troubleshooting page still separately says the Ignore list `must be the same on all peers` so they all agree what shall be skipped
- the current v3 line still appears active through `3.1.2.1076`

That is useful candor.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed across several documents before the product fully owns these questions:

- whether local exclusion is a seat-local accounting rule or a shared cross-peer meaning contract
- whether a rule difference is safe local variance, tolerable ambiguity, or unsafe disagreement
- whether a newly-added rule only narrows future intake or still leaves already-synced residue in scope
- what exact sentence the product is still allowed to say about omitted material, folder size, and peer agreement

That means AnonSync should become **more explicit than Resilio about rule agreement and exclusion claim ceilings**, not less candid than Resilio about ignore mechanics.

## New page obligations added in this pass

The archive now owes four more first-class pages:

- **Rule agreement**
- **Drift-class review**
- **Rule retroactivity**
- **Rule agreement receipt**

These pages are required whenever an exclusion, ignore, or omit rule can plausibly be mistaken for shared peer agreement rather than local seat policy.

## Revision addendum — metric-window truth, row-status overclaim, and timestamp claim ceilings after rev0235

Another current Resilio pass now sharpens one more reason to **adapt, not clone**.

Current official Resilio docs still show a product that is fairly candid about row-metric reality:

- the desktop main view still says green check means files are synced with all **connected** peers
- the same page still says `X of Y peers` means `X` online now while `Y` includes offline peers
- the same page still says offline peers are disconnected from the folder after 7 days by default, with that threshold configurable
- the still-official functionality overview still says mobile folder details show `last synced date`
- the still-official historical change log still says `Last transferred` means the last time files were changed in a folder
- that same change log still records fixes for misleading `Date synced`, peer-list, and receiving-stat accuracy
- the current v3 line still appears active through `3.1.2.1076`

That is useful candor.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed across several documents before the product fully owns these questions:

- whether a row is talking about live presence, remembered inventory, or both
- whether a timestamp means `changed`, `landed`, `seen`, or a historical activity slice
- what exact sentence the product is still allowed to say from that one field
- what deeper page is needed before action, deletion, or escalation

That means AnonSync should become **more explicit than Resilio about metric windows and row claim ceilings**, not less candid than Resilio about what its fields really mean.

## New page obligations added in this pass

The archive now owes four more first-class pages:

- **Windowed metric**
- **Metric interpretation review**
- **Status row proof**
- **Metric receipt**

These pages are required whenever a row, badge, counter, or timestamp can plausibly be read as stronger status proof than it really provides.

## Revision addendum — platform permission provenance, denial fallout, and mobile capability truth after rev0232

Another current Resilio pass now sharpens one more reason to **adapt, not clone**.

Current official Resilio docs still show a product that is fairly candid about platform-permission reality:

- current Android / Kindle permission docs still tie account access to identity-certificate generation plus link/support convenience
- the same docs still tie storage access to writing received files and applying local changes
- the same docs still tie camera access to QR-based device/share connection
- the same docs still tie startup, wake, network, and messaging permissions to autostart, background checking, network participation, and connection-request notifications
- current mobile settings docs still say notification disablement lowers system priority and may stop background work
- current Android battery docs still say Auto-sleep can stop the core so peers no longer see the device online
- current Android/iOS interface docs still show QR scanning, manual key entry, per-share network settings, clear-to-placeholder, archive toggles, and other capability families that can narrow independently
- the current v3 line still appears active through `3.1.2.1076`

That is useful candor.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed across several articles before the product fully owns these questions:

- what exact OS/platform permission is being asked for
- which exact capability family it unlocks or narrows
- what still remains true if it is denied or later revoked
- whether the resulting weakness is camera-only, storage-only, alert-only, background-only, or broader seat failure
- what stronger sentence about the seat the product must now forbid

That means AnonSync should become **more explicit than Resilio about platform permission provenance and denial fallout**, not less candid than Resilio about mobile constraints.

## New page obligations added in this pass

The archive now owes four more first-class pages:

- **Platform permission provenance**
- **Permission consequence review**
- **Permission request proof**
- **Permission state receipt**

These pages are required whenever a seat depends on OS-mediated permission for storage, camera/scan, startup, wake, notification, network, or account-backed capability.

## Revision addendum — control-endpoint attribution, browser target, and runtime watermark after rev0231

Another current Resilio pass now sharpens one more reason to **adapt, not clone**.

Current official Resilio docs still show a product that is fairly candid about control-endpoint reality:

- WebUI defaults differ by host class and install lane: Linux and Windows service use WebUI by default, while workstation app installs can add it via config.
- Listener address and port can be changed in settings or config, and `0.0.0.0` can widen audience from local-only to LAN-visible.
- Linux can run multiple instances, but later instances require manually separated ports, which means same-host browser control is not automatically one-runtime/one-endpoint.
- Storage root and config path define which settings, identity details, and login material are actually in play.
- Windows service install can migrate existing shares or instead open a clean service world in a new browser tab.
- Password-reset guidance still distinguishes deleting settings from config-enforced credentials, with different collateral effects and different continuity implications.
- Browser-warning guidance still distinguishes self-signed endpoint posture, user-provided certificates, click-through exceptions, and HSTS/browser residue.
- The current v3 line still appears active through `3.1.2.1076`.

That is useful candor.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed across several articles before the product fully owns these questions:

- which runtime does this tab or browser endpoint belong to
- what durable state world backs it
- whether this endpoint preserves the same seat or exposes a sibling runtime
- whether the current credential mutation or config edit is targeting the endpoint the operator thinks it is
- whether a warning or missing share roster reflects endpoint mismatch rather than simple auth trouble
- what stronger sentence about endpoint authority the product must forbid

That means AnonSync should become **more explicit than Resilio about control-endpoint attribution and runtime watermarking**, not less candid than Resilio about messy admin reality.

## New page obligations added in this pass

The archive now owes four more first-class pages:

- **Control endpoint attestation**
- **Endpoint switch review**
- **Browser target proof**
- **Control endpoint receipt**

These pages are required whenever a browser/web surface could plausibly point at more than one runtime world, storage root, audience scope, or continuity class.

## Revision addendum — policy provenance, hidden overrides, and surface-split authority after rev0229

Another current Resilio pass now sharpens one more reason to **adapt, not clone**.

Current official docs still show a product that is fairly candid about policy provenance reality:

- ordinary Sync Preferences and Folder Preferences still do not exhaust the real rule set
- current Power user preferences still expose semantically heavy flags for LAN rate limiting, Archive size limits, bind-interface forcing, rescan cadence, file-notification behavior, placeholder-removal semantics, and conflict-path handling
- current configuration-mode docs still allow Advanced Preferences to be carried into config, let config move storage and set control/auth material, and still say declared shared folders override prior WebUI folders and disable WebUI
- current Folder Preferences still describe per-folder relay/tracker/LAN/predefined-host/archive/overwrite behavior, while Sync Preferences still point to deeper flags for LAN-rate behavior
- current docs still distinguish defaults, per-folder rules, folder defaults, power-user flags, and config-owned rules instead of pretending one flat preferences pane explains all behavior
- the current v3 line still appears active through `3.1.2.1076`

That is useful candor.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed across several articles before the product fully owns these questions:

- what rule is actually effective right now
- where that rule came from
- whether the visible control is authoritative or shadowed
- whether the requested edit changes current behavior, future defaults, or product mode itself
- whether a config-owned seat has made the live UI descriptive only

That means AnonSync should become **more explicit than Resilio about policy provenance and override authority**, not less candid than Resilio about layered settings reality.

The archive now adds one more replacement family:

- **Policy provenance**
- **Override mutation review**
- **Hidden override surfacing**
- **Policy provenance receipt**

## Revision addendum — control-surface grade, audience, auth, and transport after rev0228

Another current Resilio pass now sharpens one more reason to **adapt, not clone**.

Current official docs still show a product that is fairly candid about control-surface reality:

- Linux and Windows service installs still default to WebUI on loopback, with LAN reach requiring a listener change.
- Workstation password setup is still optional, while NAS credentials are still compulsory.
- HTTP is still the default transport for WebUI.
- HTTPS still commonly means self-signed certificate warnings unless the operator provides a trusted certificate through config mode.
- Browser-warning docs still distinguish click-through / HSTS residue / durable trusted-cert paths.
- Password-reset docs still distinguish a storage-file deletion path with broader side effects from a config-based credential path with lower collateral impact.
- Config-mode docs still allow password hashes and custom certificates, but can also disable live WebUI if shares are fully config-owned.
- The current v3 line still appears active through `3.1.2.1076`.

That is useful candor.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed across several articles before the product fully owns these questions:

- what grade of control surface is live right now
- who can actually reach it
- whether password protection is the only thing standing between local and LAN exposure
- whether HTTPS is self-signed bootstrap or durable trusted-certificate posture
- whether the current warning is endpoint truth or browser residue
- whether the chosen recovery path preserves broader settings and seat continuity

That means AnonSync should become **more explicit than Resilio about control-surface grade and control hardening**, not less candid than Resilio about messy administration reality.

The archive now adds one more replacement family:

- **Control-surface grade**
- **Exposure/auth mutation review**
- **Certificate posture**
- **Control-surface receipt**

## Revision addendum — recovery horizon, retention decay, and access half-life after rev0222

Current official Resilio docs are still admirably candid that recovery evidence does not have one universal lifetime or one universal access path: the active v3 line still runs through `3.1.2.1076`; current Archive docs still say defaults are 30 days on desktops and 1 day on mobiles, `sync_trash_ttl=0` keeps Archive forever, `max_file_size_for_versioning` can exclude larger files from versioning, Archive reach still differs across desktop, WebUI, Android, and iOS, and Android SD-card shares still lose Archive support; current desktop Main View docs still say History shows general syncing activity for the last 30 days; current `.sync` docs still keep Archive inside hidden control storage; and current uninstall docs still say app removal does not remove archived files automatically.

That is useful truth.
The non-clone problem is that the ordinary operator answer about `how long recovery evidence remains strong`, `which surfaces can still reach it`, `what policy excluded it`, and `what hidden residue survives app removal` still depends on hopping across Archive, History, `.sync`, and uninstall articles instead of one stable product-owned horizon model.

So this revision adds a new non-clone seam:

- **recovery horizon / witness expiry forecast / retention mutation review / recovery horizon receipt**

## Revision addendum — rollback witness locality, recovery host choice, and archive-bearing asymmetry after rev0221

Current official Resilio docs are still admirably candid that rollback evidence is not universally local: the active v3 line still runs through `3.1.2.1076`; current Archive docs still say older or deleted copies move to Archive on *other* peers, only manual restoring is possible, restores should be performed while Sync is running, retention defaults still differ by desktop and mobile, Archive is still inaccessible on iOS, and Archive still does not record which peer changed the file; current rename docs still say Archive is also the mechanism that lets a renamed file be restored under its new name without re-transfer.
That is good product honesty.
The ordinary operator problem is still page shape.
Current Resilio still spreads one everyday recovery-locus answer across Archive docs, rename docs, History UI notes, and runtime timing caveats.
AnonSync should therefore copy the candor and replace the page family with four ordinary surfaces:

- `537` for **Witness locality map**
- `538` for **Recovery host choice**
- `539` for **Archive / History bridge**
- `540` for **Recovery locus receipt**

## Revision addendum — pause, quiescence, and partial-stop truth after rev0220

Current official Resilio docs are still admirably candid that `pause` is not universal stillness: the active v3 line still runs through `3.1.2.1076`; current pause docs still say only bits uploads/downloads are stopped while deletions, zero-sized files, and rescans continue; current scheduler docs still confirm that `Paused` is a partial stop rather than a total freeze; and the still-published historical change log still records that paused-state indexing behavior has been subtle enough to need a fix.
That is good product honesty.
The ordinary operator problem is still page shape.
Current Resilio still spreads one everyday answer across pause docs, scheduler docs, and historical fix archaeology, and those docs still even differ in the exact paused-upload wording.
AnonSync should therefore copy the candor and replace the page family with four ordinary surfaces:

- `532` for **Quiescence review**
- `533` for **Residual activity matrix**
- `534` for **Pause language substitution**
- `535` for **Quiescence receipt**

## Revision addendum — ciphertext custody, decrypt prerequisites, and encrypted-Archive ceilings after rev0211

Current official Resilio docs are still candid that ciphertext-only custody on untrusted devices is a real product pattern: the active v3 line still runs through `3.1.2.1076`; encrypted folders still exist specifically to keep data on an untrusted peer without revealing plaintext; encrypted destinations still must not be casually non-empty; same-lineage encrypted residue can still be re-synced and moved to Archive; encrypted nodes are still read-only, forced-overwrite, and without Selective Sync; onward sharing from those nodes is still encrypted-only; and later recovery still depends on saved RW/RO keys plus intact database continuity, or on an explicit CLI-style decrypt path.
That is good product honesty.
The ordinary operator problem is still page shape.
Current Resilio still spreads one everyday encrypted-node answer across encrypted-folder guidance, read-only behavior notes, ordinary pre-populated connect guidance, and CLI-style recovery instructions.
AnonSync should therefore copy the candor and replace the page family with four ordinary surfaces:

- `487` for **Encrypted target admission**
- `488` for **Ciphertext custody**
- `489` for **Decrypt recovery**
- `490` for **Encrypted Archive limit**

## Revision addendum — volume capability, metadata fidelity, and degraded fallback after rev0210

Current official Resilio docs are still candid that target volumes are not semantically interchangeable: the active v3 line still runs through `3.1.2.1076`; the maintained xattr docs still keep StreamsList as a real whitelist; FAT32 still lacks alt-stream support; fallback stubs in `.sync/Streams` still stand in when metadata cannot be stored natively; Windows shell actions still depend on NTFS support for alternate streams; and old-but-still-official fix history still records CIFS/SMB no-stream weirdness, exFAT attribute trouble, FAT32 noise, and xattr-delivery bugs.
That is good product honesty.
The ordinary operator problem is still page shape.
Current Resilio still spreads one everyday answer across xattr docs, shell-affordance troubleshooting, hidden-sidecar notes, and old changelog archaeology.
AnonSync should therefore copy the candor and replace the page family with four ordinary surfaces:

- `482` for **Volume capability**
- `483` for **Metadata fidelity**
- `484` for **Affordance ceiling**
- `485` for **Volume repair**

## Latest addendum — capability gates, entitlement basis, and missing-control truth after rev0199

Current official Resilio docs still show a practical product line through `3.1.2.1076`, and they still make a serious case for borrowing capability candor rather than hiding it.
They still repeatedly tell the truth that some features differ by line, entitlement, folder class, seat role, and surface.
They also still tell the truth that a seat can inherit capability from an owner, lose it with the owner, or appear licensed yet still narrow in practice when the host role mismatches the entitlement.

What they still do not make easy enough is one ordinary answer to:

- why is this capability present on this seat and missing on that one?
- what exact basis currently makes this seat entitled?
- is this action absent because of version, entitlement, subject class, surface, or seat rights?
- what exactly stopped when this seat lost Pro behavior, and what bytes or history survived?

That is another strong reason to **adapt, not clone**.
AnonSync should copy Resilio's candor about capability gating and live downgrade side effects, but refuse any interface contract where those answers still depend on cross-reading per-feature availability notes, folder-class comparisons, licensing notes, lost-license troubleshooting, and v3 FAQ prose.


## Latest addendum — byte-presence verbs, placeholder scope, and archive replay after rev0192

Current official Resilio docs still show a practical product line through `3.1.2.1076`, and they still make a serious case for borrowing selective materialization, placeholder vocabulary, folder-level disconnect, and retained-history pragmatism.
What they still do not make easy enough is one ordinary answer to:

- what exactly materializes when I fetch this file, subtree, or disconnected subject?
- what exactly disappears only here when I reclaim local space or disconnect this seat?
- when does Delete mean local reclaim versus global delete?
- when does a retained version from history truly replay, and when does it simply fall back into history again?

That is another strong reason to **adapt, not clone**.
AnonSync should copy Resilio's practicality about placeholders and archive honesty, but refuse any interface contract where byte-presence truth still depends on cross-reading synchronization modes, RSLS instructions, disconnect notes, Archive notes, and overwrite FAQs.

## Latest addendum — seat lineage, identity replacement, and reset/rehome impact after rev0191

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **seat lineage / identity replacement / roster residue / reset impact**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer can depend on:

- whether two already-running installs are being linked in a way that causes certificate takeover
- whether a confusing row is actually hidden-but-still-linked, duplicated by one reset path, or merely offline after uninstall
- whether a credential reset preserves identity and preferences or duplicates device rows and resets globals
- whether a service-world or storage-root move is continuity-preserving or really a fresh empty world that needs re-share and reconnect

So the tighter non-clone line is:

> borrow Resilio's certificate-backed seat identity and its honesty about reset side effects, but refuse any product contract where `is this the same seat?`, `what exactly will this reset preserve?`, and `why does this row look duplicated?` still require archaeology across identity, recovery, service, and cleanup article families.

That yields four more ordinary product-owned pages:

- **Seat lineage**
- **Identity replacement**
- **Device roster**
- **Reset impact**

## Latest addendum — pending approval visibility, approver locus, and remembered-trust drift after rev0190

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **pending approval visibility / approver locus / remembered-trust scope**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer can depend on:

- whether the join happened by key, link, QR, or identity-linked automation
- whether the request is still pending because approval is genuinely outstanding, because remembered trust should have auto-approved later, or because the issuer never saw the request at all
- whether the operator is on the specific issuing seat or merely on a linked seat where the subject is present in `Selective Sync` or `Synced`
- whether the relevant truth is published in the share dialog, the pending-folder icon legend, the desktop guide, the identity guide, the link-flow article, or the route troubleshooting page

So the tighter non-clone line is:

> borrow Resilio's identity-backed approvals, fingerprint review, and remembered-trust convenience, but refuse any product contract where `why is this still pending?`, `who may decide it here?`, `what exactly am I approving?`, and `why did I not get prompted this time?` still require archaeology across article families.

That yields four more ordinary product-owned pages:

- **Pending claim**
- **Claim inspection**
- **Approval authority**
- **Approval memory**

# Resilio Sync evaluation (borrow-line and interface-grammar pass)

## Bottom line

Resilio Sync remains a serious reference point.
Current official docs still show:

- an active v3 line through `3.1.2.1076` in late 2025
- WebUI as the default path on Linux and Windows service installs
- practical link/QR/manual share delivery and linking flows
- disconnected / selective / synced mode language that still compresses real operator intent
- advanced-folder permissions and owner-class mutation
- local same-host share workflows
- encrypted folders for ciphertext-only custody on untrusted nodes
- multi-layer troubleshooting for routes, ports, relays, rates, scheduler, and installation
- transport reachability still spans preferences, power-user knobs, manual pins, and troubleshooting pages

So any AnonSync thesis that depends on `Resilio is abandoned`, `Resilio never solved convenience`, or `Resilio only has old desktop-sync ideas` is weak.

The right question is still:

> what current Resilio evidence gives us a good reason not to clone the interface contract, even while borrowing several of its strongest product ideas?

## Sharper conclusion

The answer is now simpler than it was a few revisions ago.

AnonSync should:

- **borrow** several Resilio product ideas more boldly
- **adapt** several useful Resilio workflows into stronger public objects
- **refuse** the exact clone whenever convenience still fuses distinct truths or spreads one everyday answer across too many surfaces

The product ideas worth stealing are real.
The truth-contract boundaries are real too.

## What Resilio still gets right

### 1) Byte-posture language

`Disconnected`, `Selective Sync`, and `Synced` remain some of the cleanest operator-facing names in the category.
They describe real byte posture differences that people actually reason about.

AnonSync should not reject that language merely to sound original.

### 2) Delivery convenience

Resilio is also right that share delivery needs more than one path:

- link/browser convenience
- QR handoff
- manual paste fallback

A serious sync product needs all three.

### 3) Linux and headless practicality

Resilio is right that a browser/local-web control surface is practical for Linux-heavy and service-heavy installs.
AnonSync should preserve that instinct rather than assuming a desktop shell is primary.

### 4) Encrypted intermediary use case

Resilio is right that ciphertext-only custody on a VPS/NAS/borrowed host is a first-class real-world need, not a weird edge case.

### 5) Same-host derivation is real work

Resilio is also right that users do create same-host downstream copies or side roots deliberately.
That family deserves first-class modeling.

## The best current non-clone reasons

### 1) Resilio's convenience often still arrives as fused state

Resilio's mode story is useful, but it still tends to pull several truths together:

- visibility of a share on a seat
- local path adoption
- current byte materialization
- future default posture for later arrivals
- sometimes even authority expectations

AnonSync should keep the useful byte-posture insight while refusing the fused state contract.

### 2) Several useful families still depend on caveat clusters

The local-share family is the strongest example.
Current docs are candid, but the operator still has to remember a cluster of caveats about:

- self-only peer relation
- owner limitations
- permission narrowing rules
- source-child dependence
- reconnect after source reconnect
- remove/re-share for some permission changes

That is a good reason to remodel the behavior as one lineage/continuity object instead of cloning the current family shape.

### 3) Some everyday answers still live across too many surfaces

The strongest examples remain:

- browser warning pages vs control-endpoint trust meaning
- browser-open handoff vs manual typed intake
- ordinary rates vs LAN exceptions vs scheduler vs config mode
- installation vs elevation/network consent vs runtime start vs control reachability

That is not a condemnation of Resilio.
It is simply a good reason not to inherit the exact interface contract.

## The four previously strong non-clone reasons still stand

### 1) Browser trust for local control still broadens into warning ritual

Current official docs still say Linux and service seats use WebUI as the default control path and that a self-signed certificate can trigger browser warnings.
That means browser control trust is still not one explicit product-owned endpoint-trust object.

AnonSync should therefore expose endpoint class, trust grade, exception posture, and certificate upgrade as one reviewed control-trust workflow.

### 2) Browser-open handoff still degrades into OS/browser ritual or generic paste fallback

Current official docs still say opening a link in a browser can fail and that WebUI cannot use that path, with manual paste into `Enter a key or link` used as the workaround.
That means browser-open is still not a fully reliable typed intake lane.

AnonSync should therefore treat deep-link handoff as an accelerator over one canonical typed intake workflow.

### 3) Rate policy still lives across several layers

Current official docs still say rate limits apply to internet traffic by default, not LAN, unless a power-user option changes that, and scheduler behavior adds another surface.
That means the effective answer still spans ordinary preferences, exception toggles, and schedule state.

AnonSync should therefore keep one effective rate-policy ledger that names the winning layer and surviving side effects.

### 4) Install and first-run readiness still fork across trust and startup moments

Current official docs still say SmartScreen warnings may appear because of code-signing trust state, that service or silent-install paths may still leave consent/startup work, and that install completion does not automatically equal ready control reachability.

AnonSync should therefore treat install and first-run as one attested readiness ladder with receipts.

## New sharpened borrow/adapt/reject view

### Borrow directly

AnonSync should copy these product ideas with little embarrassment:

- visible disconnected / selective / full byte posture
- link / QR / manual delivery triad
- browser-first local control on Linux/headless installs
- encrypted intermediary use case
- same-host derivation as a normal workflow

### Adapt instead of clone

AnonSync should preserve the use case but change the contract for:

- linked-device convenience
- advanced-folder authority editing
- local-share continuity
- browser-open intake
- rate and scheduler controls
- encrypted-node family behavior

### Refuse the clone line

AnonSync should not clone:

- one selector silently deciding visibility, adoption, materialization, and future defaults together
- browser certificate ritual as the main expression of endpoint trust
- successful link-open as proof of authoritative intake
- scattered rate truth across preferences, exceptions, schedule, and config surfaces
- `installed` or `service installed` impersonating `trusted, started, and reachable`

## Practical implication for interface work

This revision therefore treats the interface question as inseparable from the Resilio question.
If we are not cloning Resilio, the product needs better everyday page contracts than `we expose more truth somehow`.

That is why this pass adds focused interface specs for:

- share-list rows
- transfer lanes
- history / restore browser
- conflict inbox

Those are exactly the places where Resilio's strengths are worth learning from, but where AnonSync needs a stricter truth contract.

## Result

The archive now has a better answer to both halves of the pressure test.

### Why copy Resilio at all?

Because several of its product ideas are still very good.

### Why not clone it?

Because several of its most operator-important truths still arrive as fused selectors, caveat clusters, or multi-surface reconstruction tasks.

That is a concrete, current, and defensible reason.

## Four current clone-veto seams that still matter

The deeper current answer is not merely that Resilio has a few rough edges.
It is that four important operator questions still do **not** live in one stable product-owned page contract.

### 1) Control trust

Current official docs still show all of the following at once:

- WebUI as the default control path on Linux and Windows service installs
- self-signed certificate warnings when HTTPS is enabled without a custom certificate
- proceed-unsafely and HSTS-clearing rituals as part of the practical support story
- configuration-file certificate replacement as the stronger path

That means the product idea is right — browser/local-web control is useful — while the page contract is still weaker than AnonSync should accept.

### 2) Typed artifact intake

Current official docs still show deep-link/browser-open convenience, but they also still admit that:

- browser/OS handoff can fail
- WebUI cannot consume the direct link path
- manual paste into a generic intake box is the fallback

That means the delivery idea is right, but the canonical typed intake lane is still too implicit.

### 3) Effective rate truth

Current official docs still show that effective bandwidth posture can depend on:

- ordinary send/receive preferences
- the `rate_limit_local_peers` exception
- scheduler windows and the non-obvious activities that still continue under `Paused`
- configuration-mode declarations

That means the product has real capability, but the everyday answer is still reconstructed.

### 4) Install-to-ready bringup

Current official docs still show that the operator may have to reason separately about:

- package trust / OS reputation warnings
- elevation or service-install consent
- firewall or listener exposure state
- runtime start and browser reachability

That means `installed` and `ready` are still too easy to confuse.

## What this means for AnonSync

The correct response is not to sneer at Resilio.
The correct response is to say:

> we will borrow the useful behavior, but every refusal to clone must point at one better replacement page.

That is why this revision adds page contracts for:

- `Control trust`
- `Import artifact`
- `Rate policy`
- `Finish setup`

Those four pages are not decorative extras.
They are the replacement answer that makes the non-clone line respectable.

## Four further current clone-veto seams after the first page tranche

The earlier pass established that control trust, typed intake, effective rate truth, and install readiness still deserved replacement pages.
A further current Resilio reading shows four more seams just as clearly.

### 5) Byte posture versus future-default truth

Current official docs still use `Disconnected`, `Selective Sync`, and `Synced` in a way that is genuinely useful.
But they also still tie those selectors to default-folder behavior, manual connect flow, and later-arrival handling.
That means one strong idea is still carrying several orthogonal truths.

### 6) Encrypted custody versus recovery truth

Current official docs still make encrypted folders a compelling ciphertext-only intermediary pattern.
But they also still require the operator to remember saved keys, preserved database continuity, read-only posture, overwrite semantics, and CLI/offline decrypt paths.
That means the use case is strong while the page contract is still too caveat-shaped.

### 7) Same-host derivation versus lineage continuity

Current official docs still acknowledge same-host local copies as a real workflow.
But they also still explain it through a cluster of special rules about self-only topology, no owner grant, no nested loops, source-child dependence, and manual reattach after source reconnect.
That means the workflow is real while the continuity model is still not one ordinary page.

### 8) Archive usefulness versus safe-eviction truth

Current official docs still make Archive/versioning genuinely useful.
But they also still split the operator answer across hidden paths, UI availability differences, manual restore, timestamp caveats, and a separate History surface for peer authorship.
That means the capability is useful while the safe-eviction / real-recovery answer is still reconstructed.

## What this means for the next page contracts

That is why this revision adds four more replacement pages:

- `273` — Byte posture
- `274` — Encrypted custody
- `275` — Same-host lineage
- `276` — Fetchability

Together with `269` through `272`, the archive now has a stronger answer to `what exactly are we building instead of cloning Resilio?`


## Four further current clone-veto seams after the second-wave page tranche

A further pass on current official docs still leaves four ordinary questions that Resilio answers usefully but not yet with page contracts AnonSync should clone directly.

### 1) Identity linking versus control-plane takeover

Current linking docs still say one already-configured device can lose its certificate and take over another identity when linking two running instances, with Advanced folders removed from the app on the replaced side and harsher filesystem consequences on iOS.
That means `link device` still deserves explicit empty-seat, successor-import, and takeover language.

### 2) Existing-byte intake versus duplicate repair ritual

Current docs still say default-folder arrival plus same-name collision can create indexed duplicate directories, and the repair path often runs through `Disconnect` then `Connect` and manually selecting the intended path.
That is a strong sign that pre-existing-byte intake deserves one typed page rather than remembered sequence.

### 3) Mutable delegation versus hidden ceiling logic

Current docs still say on-the-fly rights changes are Advanced-only, Standard folders need remove/re-add, linked same-identity devices act as Owners, local children cannot receive Owner, and read-only local drift has special suspend/overwrite behavior.
That is useful power, but it still deserves one explicit rights-ceiling page.

### 4) Useful multi-plane naming versus one ambiguous `folder name`

Current docs still say a local custom name may diverge from the disk folder name, not propagate to linked devices, and yet different labels can be inserted into shared links or QR artifacts.
That flexibility is real.
It is also a strong reason to expose one Name planes page instead of one overloaded rename field.

These four seams are the reason this revision adds replacement pages `277` through `280`.


## Fourth-wave current answer after rev0168

A further current-doc pass shows a different kind of non-clone reason than the earlier trust, custody, and join work.
The strongest remaining issue is not that Resilio lacks useful ideas.
It is that several operator-important truths still live in hidden service material or power-user settings.

### 5) Hidden service material is real, but the page contract is too failure-first

Current docs still say every synced folder gets a hidden `.sync` directory, that deleting or moving it breaks synchronization, and that repair may require removing the share, checking Archive, deleting `.sync`, and re-adding the share.
Another current warning doc also says the same family of failure can come from two Sync instances touching the same folder or external drive.

The product instinct is correct: service material exists and matters.
The weak contract is that operators meet the truth mainly through hidden files and later damage.

### 6) Exclusion policy is strong product power, but still hidden as rule file semantics

Current IgnoreList docs still show real power:

- excluded files are not indexed
- excluded files are not counted in share size
- rules are case-sensitive
- defaults exist already
- peers may diverge intentionally and therefore observe different totals

That is a meaningful policy system.
But the ordinary answer still depends on a hidden UTF-8 rule file and remembered wildcard/root-scope syntax.

### 7) Mutation delay is useful, but still surfaced as storage-folder JSON

Current delay docs still show a valuable idea: some file classes should wait briefly before shipping.
They also still place the policy in FileDelayConfig under the storage folder, with direct JSON edits and restart ritual.
That is a fine escape hatch, not a page contract AnonSync should clone.

### 8) Queue priority is a good idea whose public explanation is still incomplete

The current v3.1.0 download-priority docs are honest in a revealing way.
They still say priority may come from per-share settings or a global power-user default, that local manual override stops following later global changes, that only up to 50,000 active files are prioritized, that some suspension exceptions exist, that non-splittable files do not fully obey strict prioritization, and that the UI list may still look alphabetical instead of true execution order.

That is exactly the kind of feature AnonSync should borrow more boldly while refusing the page contract.
The product idea is right.
The visible explanation surface is still too weak.

## Practical consequence for AnonSync

The fourth-wave answer should now be:

- borrow **explicit service material as a public concept**
- borrow **real exclusion policy with accounting consequences**
- borrow **file-class delay windows**
- borrow **queue-order control where it materially changes operator value**
- refuse any contract where those truths live mainly in hidden directories, text syntax, raw JSON, restart ritual, or execution-order exceptions that the visible list cannot explain

Together with `281` through `284`, the archive now has a stronger answer to `what are we building instead of cloning these Resilio seams?`


## Fifth current clone-veto seam that still matters after rev0169

The deeper current answer is now broader than trust/config families.
It is also that four more ordinary operator questions still do **not** live in one stable product-owned page contract.

### 1) Shell acceleration and parity

Current official docs still show all of the following at once:

- WebUI as the only default UI path on Linux-based machines and the default UI path for Windows service installs
- file-browser context actions that depend on Finder / Explorer extensions and filesystem capabilities
- extension-repair ritual on macOS and DLL/registration ritual on Windows
- platform limits such as NTFS-only context-menu availability

That means the convenience is real, but the semantic home of those actions is still too dependent on shell health.

### 2) Local dematerialization versus global destruction

Current official docs still show all of the following at once:

- `.rsls` placeholders as zero-byte names-only representations
- `Remove from this device` as a local byte-posture change
- deleting a placeholder with read-write access as permanent deletion from all peers
- a power-user control for `Remove from all devices` that is ignored in Linux WebUI
- disconnecting a folder removing local placeholder files

That means the convenience is real, but the gesture family still overloads materially different outcomes.

### 3) Restore access parity

Current official docs still show all of the following at once:

- Archive retention by default for 30 days on desktops and 1 day on mobiles
- manual-only restore
- desktop UI opening Archive directly while WebUI/Android rely on hidden `.sync/Archive`
- no Archive access on iOS
- timestamp/index semantics that still require operator interpretation

That means the recovery idea is real, but the restore contract is still too platform-asymmetric.

### 4) Filesystem-shape fidelity

Current official docs still show all of the following at once:

- Windows link-node families as unsupported and conflict-prone
- Unix symbolic links preserved as links while target folders are not implicitly synced
- xattr policy controlled by hidden `StreamsList`
- hidden `.sync/Streams` stubs when metadata cannot be stored natively
- bundle decomposition risk when xattr syncing is disabled

That means the fidelity idea is real, but the ordinary answer still lives across too many specialist surfaces.

## What this means for AnonSync after rev0169

The correct response is again not to sneer at Resilio.
The correct response is to say:

> we will borrow the useful behavior, but the product owes one ordinary page for shell capability, one for byte-action review, one for history access, and one for filesystem-shape audit.

That is the current, concrete, non-clone line.


## Sixth current clone-veto seam that still matters after rev0170

A further current Resilio pass shows a different remaining non-clone reason than the earlier trust, custody, queue, shell, and filesystem passes.
The strongest remaining issue is not raw transport.
It is that two still-ordinary operator questions are answered honestly only by hopping across several separate articles:

1. **who outside this mesh can learn what exact facts, with what plaintext ceiling?**
2. **which exact local state root defines this node right now, and is an existing root safe to attach or clone-risk?**

### 1) Infrastructure visibility is honest, but not one page

Current official docs still show all of the following at once:

- tracker communicates IP addresses, listening ports, and share IDs
- relay passes encrypted traffic without reading or storing plaintext
- link landing pages can count clicks while not receiving the anchor-fragment payload
- update checks, telemetry, and license/account services are separate points of contact
- these services can be narrowed or disabled through settings/config

That is a respectable architectural story.
It is also a strong reason not to clone the current page contract, because the ordinary answer still requires reconstructing one observer matrix from several separate security/help articles.

### 2) Service-role capability ceilings are still FAQ-shaped

Current official docs still show all of the following at once:

- Resilio team cannot see file content
- Resilio neither hosts nor caches ordinary Sync content
- relay cannot examine encrypted transit
- landing-page infrastructure does not see the unique folder-identification payload after `#`
- vendor infrastructure can still affect discovery, relay fallback, update awareness, or telemetry flow

That means the capability ceilings are described, but not through one ordinary service-role page that states what each service can observe, what it can influence, and what it can never do.

### 3) State-root continuity is real, but still support-shaped

Current official docs still show all of the following at once:

- the storage folder contains configuration, auxiliary settings, share database, logs, and identity details
- default storage location changes by OS, service user, package mode, and config mode
- config mode can create a `.sync` storage folder near the binary/current directory if no explicit `storage_path` is given
- switching a Windows service to another principal can create a new storage location and a seemingly empty inventory

That means local-world continuity is very real, but still not one ordinary page.
The operator still has to infer whether they are in the same world, a different default world, or a wrong-root empty branch.

### 4) Clone-safety versus attach/import still does not earn direct cloning

Current official docs still show all of the following at once:

- cloning a Sync instance is unsupported
- a different storage path creates a different settings world
- service storage changes can require re-add / re-share / reconnect work
- standard install is advised instead of copied-state continuity

That is a practical prohibition.
It is not the page contract AnonSync should clone.
AnonSync should instead let the operator review whether an existing root is same-world attach, successor import, stale backup, clean branch, or clone-risk.

## What this means for AnonSync after rev0170

The correct response is again not to sneer at Resilio.
The correct response is to say:

> we will borrow the architectural honesty, but the product now owes one page for infrastructure visibility, one for service role, one for state root, and one for attach-state review.

That is the current, concrete, non-clone line.



## Seventh current clone-veto seam that still matters after rev0171

A further current Resilio pass shows another remaining non-clone reason than the earlier visibility/state-root work.
The strongest remaining issue is that helper policy and background cadence are both reasonably honest, but still reconstructed from too many separate scope layers and support pages.

1. **what helper stack is actually in force for this subject after folder policy, seat policy, proxy posture, cache, and overrides are combined?**
2. **where did helper/bootstrap knowledge come from, and what stale residue still survives after narrowing?**
3. **which helpers does this peer pair really need, and what exact counterfactual would remove that dependence?**
4. **why is this host awake or stale right now, and which cadence loops are responsible?**

### 1) Helper policy is powerful, but still scope-scattered

Current official docs still show all of the following at once:

- folder preferences carry relay, tracker, LAN-search, and predefined-host controls
- those controls are desktop-only
- global proxy posture is configured elsewhere
- LAN-only operation can require both share-preference changes and config/power-user changes
- troubleshooting adds more route truth again through separate network articles

That is real flexibility.
It is also a strong reason not to clone the current page contract, because the ordinary answer still requires rebuilding one helper-policy stack from multiple places.

### 2) Bootstrap/catalog provenance is explicit, but still too article-shaped

Current official docs still show all of the following at once:

- helper bootstrap comes from `config.resilio.com/sync.conf`
- losing that catalog blocks ordinary tracker/relay discovery
- LAN-only narrowing can still require explicit cache clearing on each desktop
- predefined hosts can substitute for broader discovery in some environments

That means the bootstrap story is documented.
It is still not one ordinary page stating which catalog source is active, what cached residue remains, and what private or manual override replaced the default.

### 3) Pairwise helper dependence is reconstructable, but not one page

Current official docs still show all of the following at once:

- direct connection is preferred
- relay is used when direct connection is impossible
- trackers help peers learn addresses and share IDs
- proxies can create asymmetric directness and, if both peers are behind proxies, relay inevitability
- multiple NICs, multicast failure, and blocked listening ports all change what path is possible

That means pairwise dependence is real.
It is not one ordinary page that distinguishes `relay allowed` from `relay inevitable` or names the exact counterfactual needed for directness.

### 4) Host cadence and quiet-host tuning are still support-lore shaped

Current official docs still show all of the following at once:

- filesystem notifications are fastest but can fail on some storage classes or deep trees
- periodic rescan defaults to 600 seconds and can be changed, even to zero
- watcher exhaustion can force the system back to periodic rescan
- NAS quieting guidance recommends stretching rescan/refresh/save cadence and disabling logging
- peer demand can still wake the host despite local quieting changes

That is good operational honesty.
It is not one ordinary host-cadence page.
The operator still has to infer what is keeping the host awake or stale from a mixture of settings and troubleshooting articles.

## What this means for AnonSync after rev0171

The correct response is again not to sneer at Resilio.
The correct response is to say:

> we will borrow the helper flexibility and background-behavior honesty, but the product now owes one page for helper policy, one for bootstrap source, one for pairwise helper dependence, and one for host cadence.

That is the current, concrete, non-clone line.

## Revision addendum — capability gating, alert delivery, and kind chooser after rev0172

Current official Resilio docs still show a useful but scattered truth in another ordinary product seam:

- v3 requires activation, personal-device reuse is permitted for personal non-commercial use, and some older families remain fenced or risky
- v2/v3 preserve synchronization compatibility, but linked devices should all be on v3 to avoid license conflicts, and Sync Business cannot be updated to v3
- desktop, mobile, Android-permission, and Linux docs still split notification/approval-delivery truth across different surfaces
- creation meaning still depends on separate share dialogs, `+` menus, send/backup articles, and kind-specific platform/edition restrictions

That means the product ideas are useful, but the page contracts still do not earn cloning.

AnonSync should therefore add one-page answers for:

- **Capability source** — what this seat can do, where that capability came from, and what remote or expiry dependence remains
- **Compatibility gate** — whether the contemplated mix is safe, sync-only compatible, risky, or blocked
- **Alert delivery** — which carrier could actually deliver the event, which gate could suppress it, and how missed-event recovery works
- **Subject kind chooser** — what `sync`, `backup`, `send`, `ciphertext custody`, and `same-host derivation` really mean before commitment

## Revision addendum — health, repair, and evidence capture after rev0173

Current official Resilio docs still show another useful but scattered truth in an ordinary product seam:

- operators are expected to inspect status rows, peer columns, and warning links and then branch into troubleshooting articles
- locked files, delayed commit windows, SMB/direct mixed access, and weak change detection are all real but still reconstructed from several different docs
- repair guidance is practical but still split across `Database error`, `Service files missing`, `My files don't sync`, and related warnings
- crash and evidence capture still depends on storage-folder discovery, service-account path differences, restart/reproduction ritual, and self-serve support boundaries

That means the product ideas are useful, but the page contracts still do not earn cloning.

AnonSync should therefore add one-page answers for:

- **Issue home** — what family this symptom belongs to, what evidence floor exists, and the first safe action
- **Environment conflict** — whether this is lock pressure, foreign-writer risk, weak notifications, or a mixture
- **Repair plan** — the least-destructive repair ladder with copy-safety proof and environment preconditions
- **Crash capture** — what private evidence exists, what more capture requires, and what later becomes a frozen disclosure packet


## Revision addendum — path continuity, relocation, disconnected presence, and rename explanation after rev0174

Current official Resilio docs still show another useful but scattered truth in an ordinary product seam:

- folder rename is local-only and should not be confused with a stable shared title
- path moves are not all equivalent: cross-volume or cross-partition moves can break ordinary tracking and fall into `Folder not found`
- disconnected folders are still meaningful product objects even though they have no local path
- custom arrival placement still depends on `Disconnected` / `Connect` ritual and default-folder behavior, including `(1)` duplicate cleanup stories
- the same `Folder not empty` warning can mean either a harmless reconnect to the old location or a materially risky merge into unrelated pre-existing bytes
- remote rename/move consequences are honest, but still explained separately through Archive/hash replay rather than one ordinary action-owned page

That means the product ideas are useful, but the page contracts still do not earn cloning.

AnonSync should therefore add one-page answers for:

- **Share path** — where the subject is actually bound here, on what storage/volume facts, and whether in-place relocation is eligible
- **Relocate review** — whether a path change is same-lineage, cross-domain rebind, repair, or continuity-breaking peer reset
- **Disconnected share** — what still exists in pathless presence, what reconnect choices remain, and what wider removal scope would be accepted
- **Rename / move explanation** — what changed locally, what peers are expected to observe, and whether replay depends on retained history or archive state


## Revision addendum — surface parity, external edit, background delivery, and mobile storage after rev0175

Current official Resilio docs still show another useful but scattered truth in an ordinary product seam:

- Linux/WebUI, desktop, Android, and iOS do not expose the same action families, and Resilio is better than average at admitting it
- iOS external-app editing is copy-based and requires explicit save-back into Sync
- Android background delivery is conditional, desktop hidden-window delivery stays active, Linux headless control is WebUI-shaped, and iOS background transfer is unavailable
- Android `Simple Mode` and mobile share settings materially change path choice, visibility, and local-storage behavior
- iOS storage, downloads, shared-link residue, and local clearing semantics still span several distinct pages and surfaces

That means the product ideas are useful, but the page contracts still do not earn cloning.

AnonSync should therefore add one-page answers for:

- **Surface capability** — what this surface can really do now, what it cannot, and why
- **External edit review** — whether another app gets a live bind or a copy, and what save-back contract applies
- **Background delivery** — whether unattended send/receive is continuous, conditional, foreground-only, or blocked
- **Mobile storage** — where bytes live locally, what each cleanup verb removes, and whether the bytes are reacquirable later

## Revision addendum — capture scope, sink choice, landed proof, and source cleanup after rev0176

Current official Resilio docs still show another useful but scattered truth in an ordinary product seam:

- mobile capture and backup are real first-class workflows, not mere renamings of ordinary sync
- Android can back up virtually any reachable data while iOS is limited to Camera Roll because of app-sandbox access ceilings
- linked-device pickers, manual link delivery, Simple Mode defaults, and removable-storage/provider rules all change which sink is actually in the ingest relationship
- backup detail surfaces expose counts, pause/resume, and device lists, but the durable answer to `has this landed enough to delete from the source?` is still reconstructed rather than published
- deleting from the source after backup, pausing ingest, and disconnecting backup all preserve or stop different things, but those consequences still live across several articles

That means the product ideas are useful, but the page contracts still do not earn cloning.

AnonSync should therefore add one-page answers for:

- **Capture source** — what exact source domain is attached, what permission proves it, and what runtime caveat currently narrows it
- **Capture sink chooser** — which sinks participate, by what admission route, and under what storage/path constraints they count
- **Ingest landed proof** — whether a source item is merely discovered, in flight, landed, or safe for source cleanup under policy
- **Source cleanup review** — what source-side delete, pause, and disconnect preserve or stop right now


## Revision addendum — execution principal, permission grants, and blocked-path repair after rev0177

Current official Resilio docs still show another useful but scattered truth in an ordinary product seam:

- runtime principal is real product meaning, not an implementation detail, because Windows service install, Linux packages, NAS packages, and headless macOS all put Sync under different actors
- filesystem authority depends on host-specific grants such as group rw, folder-level grants for package-internal users, or stronger system accounts
- changing runtime principal or storage root can silently move the operator into a different local world with different visible inventory and different recovery obligations
- blocked-path repair is practical but still scattered across host-specific troubleshooting and permission notes rather than one product-owned page

That means the product ideas are useful, but the page contracts still do not earn cloning.

AnonSync should therefore add one-page answers for:

- **Execution principal** — what OS principal is acting now, why it won, and what disk authority it currently holds
- **Filesystem grant** — what exact owner/group/ACL/provider grant makes a path writable and where that proof is weak
- **Principal switch review** — whether a runtime-user or storage-root change stays in the same world or creates a successor world
- **Blocked-path repair** — what exact grant is missing, what rung is safest, and what retest proves recovery


## Fourteenth current clone-veto seam — reachability proof still needs replacement pages

Current official Resilio docs still do a respectable job of admitting that directness depends on real network conditions: configured listening ports, tracker/discovery reachability, relay fallback, LAN multicast/broadcast, manual endpoint pins, proxy posture, and even multiple-NIC conditions. That is good product honesty. It is still not one stable operator contract. The ordinary answers to `what endpoint is actually live`, `why is this peer pair relayed`, `what safe repair rung should I try first`, and `is this manual endpoint trustworthy enough to pin` still depend on hopping between Preferences, Folder Preferences, mobile helper settings, ports/protocols notes, and troubleshooting articles. AnonSync should therefore copy the candor, but replace the page shape with four fixed surfaces: listener endpoint, peer route proof, reachability repair review, and advertised endpoint review.


## Another current non-clone reason: chronology truth still lives across warnings, advanced settings, FAQ prose, and Archive ritual

A further current-doc pass reveals another strong reason not to clone Resilio's interface contract.
The product is actually fairly candid about chronology, but the candid truth still lives in too many different places.

Current official docs still say all of the following:

- the `Time difference` warning appears when a peer's internal clock or time-zone setting is wrong, with Sync comparing file modification time after converting peer times to GMT and allowing only a 600-second difference
- mobile devices can degrade to showing an empty list rather than files under the same invalid-time condition
- `sync_max_time_diff` remains a separate power-user preference with a default of 600 seconds
- `ignore_mtime_assign_errors` can leave the correct timestamp only in the database while the on-disk mtime becomes `current`
- if several people edit the same file, ordinary online chronology can be displaced by the latest file that comes online, so an offline peer can later overwrite a newer online edit, with overwritten versions moved to Archive
- manual Archive restore still depends on Sync already running; otherwise rescan can detect the restored older file and move it to Archive again as older

Those are not mere troubleshooting curiosities.
They describe one public operator truth family that deserves explicit product ownership.

### What to borrow

Borrow the honesty that:

- clock and time-zone validity materially gate transfer safety
- offline return is a different authority rule from clean online chronology
- database truth and filesystem truth can diverge for mtimes
- restore timing changes whether an extracted version becomes live or is archived again

### What not to clone

Do not clone the page contract where the operator must cross-read:

- a warning article for clock validity
- a power-user table for mtime fallback truth
- a FAQ for offline-winner semantics
- an Archive article for restore replay timing

### What AnonSync should replace it with

This revision therefore adds four ordinary replacement pages:

- **Clock authority**
- **Offline replay review**
- **Mtime integrity**
- **Restore replay review**

That is the right response: keep the candor, replace the interface ownership model.


## Semantic tradeoffs and hidden optimization truth after rev0180

Another current no-clone seam is now concrete.
Resilio's official docs are fairly candid that:

- read-only overwrite can be destructive and has class-specific outcomes for edits, renames, deletions, and added files
- placeholder deletion can mean local eviction or global destruction depending on access and verb
- hidden settings can remap placeholder deletion into safety-biased placeholder recreation
- deferred hashing and initial-index policies change when subjects are semantically ready for rename, dedup, and ordinary sync behavior
- some fast transfer paths accept whole-file restart on interruption

That is useful product honesty.
It is also a good reason not to clone the page contract, because one ordinary answer still requires stitching together a FAQ, Folder Preferences, the RSLS article, the power-user table, and the internal-tasks warning page.

The right AnonSync response is therefore:

- borrow the candor
- refuse the toggle-and-article ownership model
- replace it with four ordinary pages: **Read-only divergence**, **Placeholder removal**, **Hash readiness**, and **Transfer method**


## Revision addendum — footprint truth, metric contract, completeness confidence, and hidden residue

This revision pushes the Resilio evaluation further in another quiet but load-bearing place.
Current official docs are still candid that ignored files are not counted in the main `Size` column, placeholders are 0-byte stand-ins, `.sync` / Archive / StreamsList / `.!sync` are real managed byte families, and watcher / rescan / hashing policy can make a view provisional rather than final.
That is all worth borrowing.
What is still not worth cloning is the page contract that leaves the ordinary operator answer spread across IgnoreList, `.sync` internals, RSLS placeholder docs, folder-view columns, and change-detection/power-user articles.

The AnonSync replacement in this revision is four fixed pages:

- `333` for truthful **subject footprint**
- `334` for **metric contract** and drift explanation
- `335` for **completeness confidence**
- `336` for **service residue / clearance review**

The tighter doctrinal answer is:

> a sync product should never make `size`, `present`, `empty`, or `cleared` look self-explanatory when placeholders, exclusions, hidden service bytes, and provisional indexing are all real states.

## Revision addendum — topology, local edges, provider grants, and removable-target continuity

This revision pushes the Resilio evaluation further in another quiet but consequential place.
Current official docs are still candid that nested shares are real but come with seeding asymmetry and duplicated indexing; that same-host local shares are self-only, entitlement-bound, and source-coupled; that provider-backed removable storage needs a real root grant separate from ordinary path browsing; and that missing or returning targets can shift the honest answer between continuity, safe rebind, and dangerous merge.
That is all worth borrowing.
What is still not worth cloning is the page contract that leaves the ordinary operator answer spread across nested-share FAQs, local-share tips, Simple Mode / SD-card peculiarity docs, existing-folder warnings, and move/reconnect articles.

The AnonSync replacement in this revision is four fixed pages:

- `337` for **topology admission**
- `338` for **local edge meaning and entitlement cliffs**
- `339` for **provider grant proof and picker integrity**
- `340` for **removable-target continuity and safe rebind**

The tighter doctrinal answer is:

> a sync product should never make `add here`, `sync locally`, `store on SD`, or `reconnect` look self-explanatory when graph relation, route truth, grant proof, and return continuity are all real states.


## Further current clone-veto seam — share artifact family, requester approval, and mutable grants

Current official Resilio docs are again strong enough that AnonSync has to give a serious answer rather than a vague anti-clone posture.

### What is good and worth borrowing

Resilio is still right that:

- share capability family matters
- approval can be a real requester-review event rather than a decorative prompt
- requester identity evidence deserves visible fingerprints / proofs
- mutable grants and onward-share rights are not identical across every subject kind
- manual carrier flexibility (copy, QR, browser handoff, paste) is valuable in ordinary life

AnonSync should borrow that candor directly.

### What still should not be cloned

The ordinary operator answer is still fragmented.
Current docs still require cross-reading the Share dialog article, Key structure article, Link structure article, User Management article, and mobile sharing guides to answer four basic questions:

1. what exact capability artifact did I issue or import?
2. what approval model comes with that artifact, if any?
3. who is actually asking for access, and why did policy auto-approve or gate them?
4. what part of this grant can I still edit or revoke later, and what already-landed bytes remain outside that future-update boundary?

That means the product idea is good.
The page contract is still too scattered.

### Replacement pages added for this seam

This revision therefore adds four more replacement pages:

- `342` — Share capability
- `343` — Incoming share request
- `344` — Member access
- `345` — Manual claim

The deeper line stays the same:

> borrow Resilio's semantic candor; refuse page contracts that still make one ordinary answer depend on several article families.


## Further current clone-veto seam — subject class, impossible upgrade, linked read-only, and peer-row meaning

Current official Resilio docs are again strong enough that AnonSync has to give a serious answer rather than a vague anti-clone posture.

### What is good and worth borrowing

Resilio is still right that:

- subject class is real semantic structure rather than decoration
- some subject classes truly support richer identity, ownership, and mutable-right semantics than others
- some `upgrades` are actually successor cutovers and should be named that way
- some requested seat exceptions do not fit the current governance family and deserve a more honest separate ritual
- peer-list grouping should reflect what the product can actually prove about identity lineage

AnonSync should borrow that candor directly.

### What still should not be cloned

The ordinary operator answer is still fragmented.
Current docs still require cross-reading the Standard-vs-Advanced article, the Standard→Advanced upgrade how-to, the linked read-only how-to, User Management, and broader linking docs to answer five basic questions:

1. what class of subject is this?
2. what cliffs come with that class?
3. is `upgrade` a same-subject mutation or a successor cutover?
4. is `make this linked seat read-only` really a per-seat exception or a separate lower-governance subject?
5. what are peer rows actually grouping by in this class?

That means the product ideas are good.
The page contracts are still too scattered.

### Replacement pages added for this seam

This revision therefore adds four more replacement pages:

- `347` — Subject class
- `348` — Class upgrade review
- `349` — Linked read-only exception review
- `350` — Peer identity view

The deeper line stays the same:

> borrow Resilio's semantic candor; refuse page contracts that still make one ordinary answer depend on several how-tos and architecture notes.

## Further current clone-veto seam — performance visibility, bottleneck proof, and workload-shaped expectations

Current official Resilio docs are again strong enough that AnonSync has to give a serious answer rather than a vague anti-clone posture.

### What is good and worth borrowing

Resilio is still right that:

- live performance visibility belongs in the product, not just in logs
- per-peer transfer tables with RTT and protocol are useful, not overkill
- disk queue and disk load are real limits and should not be hidden behind `network slow` stories
- route class, peer asymmetry, and file shape materially change honest throughput expectations
- troubleshooting should expose counterfactual repair ideas such as direct path, predefined hosts, or low-priority-disk changes

AnonSync should borrow that candor directly.

### What still should not be cloned

The ordinary operator answer is still fragmented.
Current docs still require cross-reading the Performance Overview article, slow-speed troubleshooting, and preference/power-user notes to answer four basic questions:

1. what exact window and scope does this graph represent?
2. which peer/path is actually constraining progress right now?
3. is disk pressure local to Sync or mostly host-wide?
4. what throughput should I realistically expect from this workload before I start changing knobs?

That means the product ideas are good.
The page contract is still too scattered.

### Replacement pages added for this seam

This revision therefore adds four more replacement pages:

- `352` — Activity metrics
- `353` — Peer connection table
- `354` — Disk pressure
- `355` — Throughput expectation

The deeper line stays the same:

> borrow Resilio's semantic candor; refuse page contracts that still make one ordinary answer depend on charts, troubleshooting prose, and scattered settings memory.


### Diagnostic telemetry and evidence custody addendum

Current official Resilio docs are again strong enough that AnonSync has to give a serious answer rather than a vague anti-clone posture.

#### What is good and worth borrowing

Resilio is still right that:

- anonymous statistics, debug logs, profiler traces, and crash artifacts are different data families
- deeper capture should have an explicit enable step and sometimes a restart gate
- local artifact paths, rotation size, and retention windows are real product facts
- outbound log send is a real transfer with bundle size and completion risk, not a magical support button
- evidence collection guidance should acknowledge mobile-specific and hidden-storage-specific quirks

AnonSync should borrow that candor directly.

#### What still should not be cloned

The ordinary operator answer is still fragmented.
Current docs still require cross-reading the Power user preferences article, debug-log collection guides, mobile log guide, storage-folder article, and crash-report article to answer four basic questions:

1. what operational data classes exist before an incident?
2. what extra capture starts when I enable deeper diagnostics?
3. what exact evidence is leaving the node if I press `send logs`?
4. what artifacts remain locally, where, and for how long?

That means the product ideas are good.
The page contract is still too scattered.

#### Replacement pages added for this seam

This revision therefore adds four more replacement pages:

- `357` — Telemetry consent
- `358` — Profiler capture review
- `359` — Diagnostic send
- `360` — Local evidence retention

The deeper line stays the same:

> borrow Resilio's semantic candor; refuse page contracts that still make one ordinary answer depend on advanced settings tables, support how-tos, and hidden storage folklore.



## Further evaluation after rev0187 — control surfaces are strong ideas with weak page ownership

Another current Resilio pass strengthens the same main conclusion rather than weakening it.

Current official docs still show real product substance:

- a live v3 line with `3.1.2.1076`
- WebUI as the default path on Linux and on Windows service installs
- loopback-by-default listener posture with deliberate widening to LAN
- explicit browser-warning recovery guidance
- explicit password-reset side effects
- explicit browser-link fallback when WebUI cannot consume direct-open intake

That is not abandonment or product confusion.
It is real operator-oriented candor.

It still does **not** earn direct interface cloning.

The reason is the same clone-veto rule now applied to another seam:

> one ordinary operator question should have one stable page answer.

Current Resilio still spreads the ordinary control answer across WebUI setup docs, Linux/service notes, browser-warning recovery, password-reset instructions, installer trust pages, and browser-link troubleshooting.
So the product idea stays strong while the page contract still fails.

That is why this revision adds four narrower replacement pages:

- `362` Control launch
- `363` Control listener
- `364` Browser trust recovery
- `365` Control access recovery

These pages keep the Resilio practicality and reject the scattered explanation path.

## Further evaluation after rev0193 — namespace truth is still real, but still scattered

Another current Resilio pass strengthens the same main conclusion rather than weakening it.

Current official docs still show real product substance:

- a live v3 line with `3.1.2.1076`
- explicit conflict-file causes including case-insensitive collisions, unicode-form differences, prohibited symbols, linked junctions, and even storage/controller faults
- explicit warning not to casually delete `.Conflict` artifacts because they still correspond to real remote data
- explicit unsupported-link guidance on Windows, and explicit symlink-target exclusion guidance on Unix unless the target is added separately
- explicit invalid-name and path-length warnings in troubleshooting guidance
- explicit exposure of path-handling toggles like `fix_conflicting_paths` and `normalize_unicode_paths`

That is not vagueness or abandonment.
It is real operator-oriented candor.

It still does **not** earn direct interface cloning.

The reason is the same clone-veto rule now applied to another seam:

> one ordinary operator question should have one stable page answer.

Current Resilio still spreads the ordinary namespace answer across conflict docs, unsupported-entry docs, invalid-name warnings, move/rename limitations, troubleshooting notes, and power-user settings.
So the product idea stays strong while the page contract still fails.

That is why this revision adds four narrower replacement pages:

- `397` Namespace blockage
- `398` Conflict evidence
- `399` Unsupported entry
- `400` Portability repair

These pages keep the Resilio candor and reject the suffix-and-support reconstruction path.
## Further evaluation after rev0194 — freshness claims are useful, but still article-shaped

Another current Resilio pass strengthens the same main conclusion rather than weakening it.

Current official docs still show real product substance:

- a live v3 line with `3.1.2.1076`
- candid explanation that change detection precedes indexing and delivery rather than magic `instant sync`
- explicit periodic/startup/manual rescan truth
- explicit watcher-exhaustion downgrade truth
- explicit service-path notification-loss truth
- explicit admission that `Some internal tasks are taking time to complete` may still be recoverable background work

That is not abandonment or product confusion.
It is real operator-oriented candor.

It still does **not** earn direct interface cloning.

The reason is the same clone-veto rule now applied to another seam:

> one ordinary operator question should have one stable page answer.

Current Resilio still spreads the ordinary freshness answer across the synchronization-start FAQ, power-user settings, watcher warnings, service troubleshooting, internal-task warnings, and generic no-sync guidance.
So the product idea stays strong while the page contract still fails.

That is why this revision adds four narrower replacement pages:

- `402` Freshness basis
- `403` Detection downgrade
- `404` Rescan review
- `405` Change publication

These pages keep the Resilio candor and reject the FAQ-plus-warning reconstruction path.

## Further evaluation after rev0195 — motion truth is useful, but still article-shaped

Another current Resilio pass strengthens the same main conclusion rather than weakening it.

Current official docs still show real product substance:

- a live v3 line with `3.1.2.1076`
- candid explanation that scheduled `Paused` still allows zero-sized files, deletions, indexing, and some peer-serving behavior
- candid explanation that desktop background, headless Linux, Android task-killer risk, and iOS background absence are materially different runtime stories
- candid explanation that Android Auto Sleep and Battery Saver intentionally change participation posture
- candid explanation that hidden work such as hashing, block checking, local-block copy, compare, read, and write can make Sync look stalled before visible transfer resumes
- candid explanation that slowness can come from relay, many-small-files shape, remote-upload ceiling, disk / hardware limits, or security-software interference
- candid explanation that some unavailable downloads are not waiting at all because no peer still has full source bytes

That is not abandonment or product confusion.
It is real operator-oriented candor.

It still does **not** earn direct interface cloning.

The reason is the same clone-veto rule now applied to another seam:

> one ordinary operator question should have one stable page answer.

Current Resilio still spreads the ordinary motion answer across the schedule article, background/runtime notes, battery/network settings, slow-speed troubleshooting, source-unavailable warnings, and internal-task warnings.
So the product idea stays strong while the page contract still fails.

That is why this revision adds four narrower replacement pages:

- `412` Motion basis
- `413` Quiet window
- `414` Bottleneck cause
- `415` Resume catch-up

These pages keep the Resilio candor and reject the schedule-plus-warning reconstruction path.


## Further non-clone evidence after rev0197 — hidden subject spine and sidecar authority

Another current Resilio pass now tightens the argument in a different ordinary place:

- current docs still openly admit that a subject carries hidden product-owned state inside `.sync`
- current docs still split hidden families across identity, Archive, IgnoreList, StreamsList, and in-flight `.!sync` names
- current docs still make exclusion semantics depend on a hidden text sidecar and xattr carriage depend on a separate hidden whitelist sidecar
- current docs still let duplicate runtimes or unsupported instance cloning corrupt or confuse that hidden state
- current docs still make one repair path effectively `check Archive, delete .sync, remove/re-add`, which is continuity-recreation folklore rather than one product-owned continuity page

So one more strong no-clone reason is now clear:

> Resilio is still worth borrowing for its candor that sync subjects really do have hidden product-owned state, but not for the way ordinary answers about `what is payload`, `what is hidden product state`, `which sidecar is local policy`, `did continuity survive`, and `what hidden bytes are safe to touch` still live across FAQ pages, hidden text files, warning articles, troubleshooting notes, move/rename caveats, and cloning warnings.

AnonSync should therefore expose one visible subject-spine contract, one sidecar-policy page, one spine-integrity page, and one managed-hidden-bytes page instead of relying on hidden folders as the interface.


## Latest addendum — external recipes, command exactness, and postcondition proof after rev0202

Current official Resilio docs still show a practical product line, and they still make a serious case for borrowing procedural candor rather than pretending every repair can be one safe in-product click.
They still openly recommend outside-the-product acts like stopping Sync before `iperf3`, creating `debug.txt` in storage, restarting to make logging take effect, editing or supplying `sync.conf`, clearing HSTS or using a temporary browser bypass, deleting `settings.dat` for one password-reset lane, or rebuilding hidden service state when `.sync` continuity is lost.

What they still do not make easy enough is one ordinary answer to:

- what exact class of step this is
- what exact seat / runtime / path / hidden state it touches
- what had to be stopped or closed first
- what observation only proves the ritual happened
- what product-side reread actually proves success afterward
- whether the result preserved continuity or only recreated workable successor state

That is another strong reason to **adapt, not clone**.
AnonSync should copy Resilio's candor about external recipes and exact steps, but refuse any interface contract where those answers still depend on cross-reading support how-tos, browser-warning pages, config notes, and troubleshooting prose.

### Warning ownership, blast radius, and recovery-rung addendum

Current official Resilio docs still show an active v3 line through `3.1.2.1076`, and they are still candid that warning strings correspond to materially different realities:

- `Core warnings` still separates tracker loss, low space in the default-folder-location disk, failed folder-list / identity sync, and license-management disablement.
- `Some internal tasks are taking time to complete` still says the condition can be recoverable hidden work such as scanning, hashing, block checking, deduplication, merge, transfer, or writing rather than a hard stall.
- the watcher-exhaustion warning still says Sync can lose live notifications and fall back to manual or periodic rescan until the inotify limit is raised and Sync restarted.
- the ghost-file / `Cannot download files` warning still says a peer may have announced bytes that later disappeared into placeholder-only state and now no full source peer has them.
- `Database error` still suspends only the affected subject and still recommends a restart → disconnect/reconnect same destination → re-add ladder.
- `Service files missing` still treats `.sync` loss/corruption as continuity-bearing damage and explicitly says the fix creates a new synchronization instance.
- `Folder not found` and `Folder not empty` still mix same-lineage reconnect, risky merge into pre-existing bytes, and broader peer-reconnect fallout.
- `Time difference` still names clock/timezone invalidation and the 600-second threshold.

That is strong product candor.
What is still not worth cloning is the page contract.
The ordinary operator still has to reconstruct warning meaning across footer strings, share warnings, click-through details, standalone articles, and related-article hops.

AnonSync should therefore expose four fixed public surfaces whenever warning meaning is non-trivial:

1. **Warning page** — exact warning class, honest severity, strongest current claim, and first safe next move
2. **Blocker scope** — seat / subject / item / hidden-state blast radius and unaffected neighbors
3. **Recovery rung** — least-destructive next step, escalation proof, and continuity cost if a broader rung is taken
4. **Warning history** — first seen / last seen / acknowledged / suppressed / cleared-with-proof lineage so dismissal never impersonates repair

So the tighter line for this pass is:

> borrow Resilio's candor that warnings correspond to real degraded states; refuse any product contract where ordinary warning truth still depends on stitching together strings, one-off articles, and troubleshooting prose instead of one stable page family.

## Latest addendum — mobile capture-source, path-class, sink, and reacquire truth after rev0204

Current official Resilio docs still show a practical mobile story, and they still make a serious case for borrowing platform candor rather than pretending a phone is just a small desktop.
They still openly distinguish Camera Backup from ordinary sync, Android folder backup from iOS Camera Roll only, sandboxed iOS storage from Android path classes, Simple Mode fixed defaults from explicit location choice, SD-card root-grant flow from ordinary folder picking, and download-history residue from actual local bytes.

What they still do not make easy enough is one ordinary answer to:

- what exact source class is under review
- what exact path class is writable or only source-readable on this seat
- whether the selected peer is a collaborative peer or a durable-copy sink
- what later local clearing leaves behind as bytes, placeholders, history, or only receipts
- what current prerequsite still governs reacquireability

That is another strong reason to **adapt, not clone**.
AnonSync should copy Resilio's candor about mobile constraints and contracts, but refuse any interface shape where those answers still depend on hopping across Camera Backup, Android Backup, Simple Mode, SD-card, storage-management, file-sharing, and iOS-peculiarity articles.

## Latest addendum — compromised linked seats, narrowest cutoff, and residual authority after rev0205

Current official Resilio docs still show a practical product line, and they still make a serious case for borrowing incident candor rather than pretending a stolen seat is merely an offline row.
They still openly say that an unencrypted stolen linked seat may be able to view, modify, or remove data on other linked devices; that linked seats under one identity act as Owners; that `Disconnect` revokes future updates while leaving already-synchronized files in place; that remote unlink of other linked devices is unavailable; and that the documented response may expand into backup, unlink, storage-folder cleanup, reinstall, identity regeneration, relink, and reshare.

What they still do not make easy enough is one ordinary answer to:

- what exact live authority this suspect seat still carries now
- what exact cutoff can be bought narrowly per subject
- when broader cohort rotation is the honest next step rather than overreaction
- what exact sequence carries trusted survivors forward under a rebuilt epoch
- what already-landed bytes or residual authority still remain after the cutoff

That is another strong reason to **adapt, not clone**.
AnonSync should copy Resilio's candor about incident cost and residual risk, but refuse any interface shape where those answers still depend on hopping across a stolen-device note, identity-linking docs, user-management semantics, licensing behavior, and encrypted-peer guidance.

## Latest addendum — bounded handoff, open redemption, and residue truth after rev0206

Current official Resilio docs still show a practical product line, and they still make a serious case for borrowing candor about convenient file handoff rather than pretending every link is a live shared subject.
They still openly say that `Sharing single file` is a one-time one-way data transfer, that desktop links default to 3 days but may be made never-expiring, that `share_file_ttl` still shapes defaults, that anyone with the link can redeem it, that use count and device bans are unavailable, that changed content invalidates the current handoff and forces a new link, and that recipients may re-share without gaining power to change expiry.

What they still do not make easy enough is one ordinary answer to:

- is this live sync or only a bounded snapshot handoff
- who may redeem it and what ceiling that claim really has
- what exact lane or surface owns the receive path now
- what exact landed result will happen on collision
- what UI clearing, byte deletion, expiry, or stale-content invalidation actually leaves behind

That is another strong reason to **adapt, not clone**.
AnonSync should copy Resilio's candor about bounded handoff limits and residue, but refuse any interface shape where those answers still depend on hopping across the single-file article, Android/iOS sharing notes, receive-path defaults, and power-user history knobs.


## Diagnostic support-lane, log-route, and crash-custody addendum

Current official Resilio docs still make support and diagnostic truth simultaneously candid and scattered.
They still openly separate:

- `send_statistics` anonymous metrics from debug logging and profiler capture
- `log_size`, `log_ttl`, and `profiler_enabled` local-retention behavior
- debug-log activation through Settings/Preferences versus `debug.txt` in storage
- restart-needed capture activation versus already-live capture
- in-product `Contact support` send versus manual attachment / upload fallback
- mobile hidden-log ritual (`SNC.DBG.LOGS`) versus desktop file pickup
- crash report / mini-dump / core-dump collection paths and service-account variance

That is useful evidence.
It is also a strong reason not to clone the current page contract, because the ordinary answer still requires rebuilding one support/disclosure story from several articles.

AnonSync should instead publish four ordinary page families:

- **Support lane** — who can actually receive evidence here, and under what disclosure boundary
- **Log capture window** — what extra capture is active, what restart/hold-time is still required, and what residue is accumulating locally
- **Report send** — what exact packet leaves, by what route, under what size ceiling, with what fallback
- **Crash artifact** — which crash-evidence class exists, where it lives, and what remains local after export


## Revision addendum — space pressure, byte classes, and reclaim proof after rev0208

Another current Resilio pass exposed a storage seam that is too ordinary to remain article-shaped.

Current official docs still openly say that:

- `free_space_warning_threashold` defaults to `1024 MB` and can stop syncing files when the drive tied to the default folder location gets that low
- `disk_min_free_space` and `disk_min_free_space_gb` still offset that floor
- Selective Sync placeholders still materially reduce local byte residency while `Remove from this device` keeps peers intact only if another full source survives
- Archive still retains deleted/older copies for 30 days on desktops and 1 day on mobiles by default, while disabling Archive weakens that protection
- iOS storage still splits App Data from User data and still requires Selective Sync before clearing local files from a sync share
- mobile Cleanup still clears residual files and current debug logs
- storage folders and uninstall paths still preserve configuration, database, logs, dumps, and other managed bytes outside ordinary payload

That candor is useful.
The page shape is still wrong.
One ordinary answer still requires hopping across warnings, power-user settings, Sync-mode docs, Archive docs, mobile storage pages, storage-folder lore, and uninstall notes to answer four questions:

- what exact floor is active here now
- what exact byte classes are consuming local storage
- what safe-first reclaim action exists
- what exactly changed after apply

AnonSync should therefore keep the storage candor and replace the page shape with four ordinary product-owned pages:

- **Space pressure** — active floor, byte contributors, and safest first rung
- **Byte-class inventory** — payload, history, diagnostics, service state, and residue in one stable ledger
- **Reclaim preview** — expected freed bytes, non-effects, and retention cost before commit
- **Reclaim receipt** — observed byte delta, preserved truths, weakened truths, and residue after apply


## Revision addendum — network paths, protocol discipline, and freshness risk after rev0209

Another current Resilio pass exposed a remote-path seam that is too ordinary to remain article-shaped.

Current official docs still openly say that:

- SMB/network shares are a distinct path class with explicit limitations and peculiarities
- Sync and the actual runtime account still both need full permissions to the target folder or delivery can cease
- SMB-mounted paths may lack live notifications unless the stack is SMB 3.0+, and otherwise change discovery falls back to full rescans
- some file storages such as NFS or SMB2 mounted shares are not even supposed to provide working filesystem notifications, so freshness becomes rescan-grade by design
- lock behavior on network shares still depends on the SMB service / daemon implementation and on failure paths such as dropped connections or crashed apps
- mixed direct access plus Samba access on NAS-style setups can still damage files or roll back third-party changes
- Windows service UNC workarounds can still make a path reachable while losing live notifications and relying on rescan or restart instead
- changing service identity to gain access can still move state root and force re-add / re-share / reconnect work

That candor is useful.
The page shape is still wrong.
One ordinary answer still requires hopping across an SMB article, service troubleshooting, generic freshness notes, and release-fix memory to answer four questions:

- what exact path class is this
- which protocol is authoritative for mutation
- how fresh can this location honestly be
- should this remote path be admitted as a subject at all

AnonSync should therefore keep the candor and replace the page shape with four ordinary product-owned pages:

- **Network path class** — local vs mounted vs UNC-under-service plus watcher grade and runtime implications
- **Protocol discipline** — authoritative mutation lane, alternate lanes, and explicit corruption/rollback risk
- **Detection grade** — notification coverage, rescan fallback, restart sensitivity, and freshness ceiling
- **Network subject admission** — permission fitness, lock/daemon caveats, service identity consequences, and admit/reject receipt



## Latest addendum — encrypted-custody workflow ownership after rev0212

A further current Resilio pass shows another remaining non-clone reason than the earlier encrypted-target / ciphertext-capability / decrypt-prerequisite pages.
The strongest remaining issue is not whether Resilio has a real encrypted-custody feature.
It does.
The issue is that the **whole encrypted-custody workflow** is still not owned by one stable operator-facing flow.

Current official docs still openly distinguish useful truths:

- `Encrypted folders` still says the point is to keep an untrusted peer online without plaintext exposure, and still requires manual encrypted-key intake, `Disconnected` posture on linked devices, strict target hygiene, read-only encrypted peers, and preserved key/database continuity for later recovery.
- `Can I connect two pre-populated pre-existing folders?` still documents an ordinary non-empty intake branch with hash comparison, merge, timestamp winner terms, and linked-device reconnect using `Disconnected` as a different kind of path-reuse ritual.
- `Disconnecting and Removing Folders` still says reconnect may propose a different default path and even create a sibling `(1)` directory unless the operator manually retargets.
- `Sync Private Identity & Linking My Devices` still describes linked devices as one identity family where folders become available across the cohort and where the certificate-bearing identity matters materially.

That candor is good.
What is still not worth cloning is the page contract.
The ordinary operator still has to reconstruct one answer to:

- which branch this is
- whether the destination seat posture is appropriate for opaque custody
- whether the target path is being reviewed as ordinary preseed merge or encrypted landing
- whether future recovery was actually prepared rather than merely described
- what proof bundle exists after commit

AnonSync should therefore expose four fixed public surfaces whenever encrypted custody is at stake:

1. **Encrypted custody setup flow** — lane classification, seat-posture review, target admission, consequence preview, and commitment receipt
2. **Encrypted custody seat** — current capability ceiling, recoverability posture, strongest risk, and next review
3. **Recovery material attestation** — saved-key governance, continuity proof, rehearsal status, and effective recovery rung
4. **Encrypted custody dossier** — shareable reviewed facts, redaction boundary, recipient lane, and bundle receipt

So the tighter line for this pass is:

> borrow Resilio's real encrypted-custody capability and its candor about hard ceilings; refuse any product contract where the operator still has to assemble the *whole encrypted-custody workflow* from identity docs, encrypted-folder caveats, reconnect guidance, non-empty-path prompts, and later recovery notes instead of one stable product-owned flow.


## Latest addendum — typed bootstrap artifacts and intake-route ambiguity after rev0213

A further current Resilio pass shows another remaining non-clone reason than the earlier claim-lane, browser-handoff, identity-join, and encrypted-custody pages.
The strongest remaining issue is not whether Resilio supports many bootstrap lanes.
It does.
The issue is that **typed artifact truth and route proof** are still not owned by one stable operator-facing page.

Current official docs still openly distinguish useful truths:

- `Sync Private Identity & Linking My Devices` still uses `M-key` / `Enter a key` for linked-family join and still warns that linking a non-empty running instance can replace a local certificate world and import the other instance's shares.
- `Comprehensive guide to syncing (Desktop-Desktop)` and `Quick guide to syncing` still use link/key/QR for ordinary subject claim and still route desktop manual claim through `Enter key or link`.
- `Encrypted folders` still uses encrypted key plus `Manual connection`, and still makes that lane semantically different because it creates ciphertext-only custody rather than ordinary plaintext-capable membership.
- `Link structure and flow` still says browser links go through a Resilio landing page and then try to hand off into the app.
- `Configuring WebUI` still says clicked-link flows do not work there and manual `Enter a key or link` remains the fallback.

That flexibility is useful.
What is still not worth cloning is the earlier page contract.
The ordinary operator can still be pushed into similar-looking copy/paste/open rituals before the product fully owns:

- what family of artifact was actually imported
- what world it touches
- what it can and cannot do
- which reviewed route should follow
- what durable intake proof remains afterward

AnonSync should therefore expose four fixed public surfaces whenever imported material could mean more than one thing:

1. **Artifact family router** — carrier/family separation, parse confidence, and admissible deeper routes
2. **Typed artifact card** — scope, authority ceiling, freshness, and non-effects
3. **Intake route review** — join vs claim vs encrypted-custody consequence review and safe route switch
4. **Typed intake receipt** — carrier, parse, route, and replay-safe proof

So the tighter line for this pass is:

> borrow Resilio's flexible bootstrap lanes; refuse any product contract where similar manual/key/link surfaces still leave the operator to remember from help articles whether imported material joins an identity family, claims one subject, or creates ciphertext-only custody.


## Latest addendum — destination-world ambiguity, auto-land defaults, and reconnect-target proof after rev0214

Current official Resilio docs are still candid that linked devices have three real synchronization modes; that Disconnected delays bytes and asks where to put the folder; that Selective Sync or Synced can auto-land new arrivals into a default root; that reconnect can draft a different path and create a same-name `(1)` sibling; that pre-populated reuse on linked devices often wants Disconnected posture or disconnect/reconnect ritual; and that encrypted custody on linked devices again wants Disconnected posture plus a fresh empty directory.

That is good product honesty.
But the ordinary operator still has to reconstruct one answer to:

- which destination world is actually in play here
- whether bytes will auto-land or wait unplaced
- whether this is continuity repair or duplicate-branch creation
- whether the current branch allows non-empty reuse at all
- what proof remains after choosing the world

The docs expose those truths across `Synchronization Modes`, linked-device setup, duplicate-folder repair, reconnect guidance, Android location-choice notes, pre-populated-folder advice, and encrypted-folder caveats.
That means current Resilio still leaves too much destination-world truth to article memory.

AnonSync should therefore add one earlier destination-world page family that keeps arrival posture, default root, remembered continuity root, reroute interruption, and special ciphertext-custody branches adjacent before deeper bind/custody pages take over.

The replacement pages for this seam are:

- **Destination world picker** — candidate worlds, bind lanes, blocked worlds, and consequence preview
- **Destination world card** — portable world summary, posture, root history, and strongest warnings
- **Arrival reroute review** — interrupt default auto-land, preserve continuity intent, and compare `leave drafted` vs `reroute`
- **Destination commit receipt** — chosen world, chosen lane, rejected alternatives, and next handoff proof

## Latest addendum — bind-outcome proof after rev0215

Current official Resilio docs are still candid that pre-populated existing-byte binds are real; that matching hashes avoid re-sync, differing content can produce latest-timestamp replacement, and other files merge; that linked-device auto-land can create same-name `(1)` siblings in the default root; that `.sync/ID` still makes same-subject-on-this-seat a distinct collision class; and that encrypted custody still requires a fresh empty target.

That is good product honesty.
But the ordinary operator still has to reconstruct one answer to:

- what semantic branch this target commit will create
- whether this is attach, merge, deliberate fork, or blocked same-subject reuse
- whether a duplicate sibling is being drafted now or only discovered later
- whether the chosen lane is ordinary reuse or empty-only ciphertext custody
- what durable proof remains after choosing the branch

The docs expose those truths across `Can I connect two pre-populated pre-existing folders?`, duplicate-folder troubleshooting, manual-location guidance, same-ID warnings, Share dialog guidance, and encrypted-folder caveats.
That means current Resilio still leaves too much bind-outcome truth to article memory.

AnonSync should therefore add one earlier bind-outcome page family that keeps target-tree evidence, branch verdict, alternatives, and receipt continuity adjacent before deeper merge, reuse, or custody pages take over.

The replacement pages for this seam are:

- **Bind outcome review** — current branch verdict, why it won, and immediate consequence preview
- **Existing tree evidence** — same-ID proof, lineage hints, non-empty shape, and collision classes
- **Branch consequence compare** — attach vs merge vs fork vs blocked alternative review
- **Bind outcome receipt** — chosen branch, strongest evidence, rejected alternatives, and next handoff proof

## Revision addendum — effective seat posture, local mutation, and derivative ceilings after rev0216

Current official Resilio docs are again useful because they remain candid that `connected` is not one semantic state.
The current v3 line still runs through `3.1.2.1076`.
Current official docs also still say all of the following:

- linked devices under one identity act as Owners
- linked-device automation commonly lands folders on all linked seats with broad read-write behavior
- if one linked seat should actually be read-only, the documented path still requires a separate Standard-folder read-only-key ritual with disconnect plus manual reconnect
- ordinary read-only peers do not propagate local edits back, and touched files can enter a suspended state until overwrite or repair resolves them
- encrypted custody peers are read-only, forced-overwrite, and without Selective Sync
- local derived shares inherit only the source ceiling, cannot receive Owner, can narrow when the source narrows, and can disappear with the source

That is strong product honesty.
The ordinary operator problem is still page shape.
Current Resilio still spreads one everyday answer across user management, linked-device guidance, one-way-sync behavior, encrypted folders, and local-share guidance.
AnonSync should therefore copy the candor and replace the page family with four ordinary surfaces:

- `512` for **Effective seat posture**
- `513` for **Local mutation on narrow seat**
- `514` for **Derived rights graph**
- `515` for **Seat posture receipt**

## Revision addendum — seat posture change mechanism, rebind class, and derivative cascade after rev0217

Current official Resilio docs are again useful because they remain candid that not all seat posture changes are one kind of operation.
The current v3 line still runs through `3.1.2.1076`.
Current official docs also still say all of the following:

- Advanced folders support on-the-fly permission changes
- Standard folders do not support on-the-fly permission changes and instead need remove-and-readd with a new key
- linked devices act as Owners by default
- making one linked seat read-only still requires a separate Standard-folder read-only-key ritual with disconnect plus manual reconnect
- local shares cannot receive Owner, cannot change permission through user management, and instead need remove-and-reshare
- source-right narrowing can lower local descendants automatically
- source disconnect can remove local descendants and later reconnect does not restore them automatically

That is strong product honesty.
The ordinary operator problem is still page shape.
Current Resilio still spreads one everyday answer across user management, Standard-vs-Advanced comparison, linked-device guidance, linked read-only workaround guidance, and local-share guidance.
AnonSync should therefore copy the candor and replace the page family with four ordinary surfaces:

- `517` for **Seat posture change review**
- `518` for **Posture transition forecast**
- `519` for **Posture cascade graph**
- `520` for **Seat posture change receipt**


## Revision addendum — visual absence versus actual severance after rev0218

Another current official Resilio pass sharpens one more reason to adapt rather than clone.

Current docs are still candid that:

- `Hide this device` only hides an offline linked seat and does not unlink it
- `Disconnect` affects one device and leaves already-landed bytes in the file system
- `Remove` affects devices linked with one identity yet may still leave the subject on remote devices outside that identity
- `Remove from this device` only reverts local bytes to placeholders
- `Remove from all devices` deletes across peers and archives there
- local unlink exists but remote unlink does not
- severe compromise can still require identity rebuild instead of seat-local severance

That is useful truth.
The non-clone problem is still ownership of the ordinary question `is this actually gone`.
Resilio still leaves operators to reconstruct cosmetic absence, local severance, cohort severance, swarm deletion, and epoch replacement from separate docs.

AnonSync should therefore introduce one dedicated severance family and make disappearance verbs prove their exact scope before commit.


## Revision addendum — post-action claim ceiling and recall overstatement after rev0219

Current official Resilio docs are still admirably candid that common departure and containment actions do **not** all earn the same post-action sentence: the active v3 line still runs through `3.1.2.1076`; current `User Management` docs still say disconnect revokes future updates while already-synchronized files remain; `Disconnecting and Removing Folders` still says disconnect leaves bytes in the local file system and remove from linked devices may still leave remote non-linked retainers; `Synchronization Modes`, `What Is an RSLS File?`, and iOS interface docs still distinguish `Remove from this device` from broader deletion; identity docs still say remote unlink is unavailable; and the stolen-device article still escalates some cases to identity regeneration instead of pretending narrow seat-local verbs fully solved the incident.
That is good product honesty.
The ordinary operator problem is now statement ownership.
Current Resilio still spreads one everyday answer across user-management, disconnect/remove, placeholder, identity-linking, and incident-recovery docs.
AnonSync should therefore copy the candor and replace the page family with four ordinary surfaces:

- `527` for **Action claim review**
- `528` for **Residual claim matrix**
- `529` for **Safe language substitution**
- `530` for **Action statement receipt**


## Revision addendum — cleanup intent, preservation-before-cleanup, and witness survival after rev0223

Current official Resilio docs are still practically honest about cleanup, but they still split one ordinary operator answer across disconnect/remove, Selective Sync, Synchronization Modes, iOS storage, Archive, and uninstall articles. They still distinguish one-device disconnect from linked-device remove; local placeholder reversion from all-peer deletion; Selective-Sync share removal from local placeholder persistence; mobile storage clear from uninstall; and uninstall from hidden archive cleanup. That candor is useful, but the workflow still stays too article-shaped.

So the archive tightens one more non-clone reason: **cleanup should be typed before apply, preservation should be offered before cleanup narrows proof, and the post-cleanup receipt should own the surviving witness and safe sentence.**

New replacement pages in this pass:

- `546` Resilio cleanup intent, witness survival, and preservation-before-cleanup evaluation
- `547` Cleanup intent review
- `548` Witness survival forecast
- `549` Preserve-before-cleanup
- `550` Cleanup outcome receipt


## Revision addendum — hidden witness access, surface visibility, and proof-presentness after rev0224

Current official Resilio docs are still candid that recovery and cleanup witnesses are not equally reachable from every surface. The current v3 line still runs through `3.1.2.1076`. Current official docs also still say all of the following:

- Archive lives in hidden `.sync/Archive`
- desktop Sync UI can open Archive directly, but WebUI and Android still rely on file-browser access to the hidden Archive path
- Archive is not accessible on iOS
- `.sync` is critical service state and should not be moved separately from the shared folder
- uninstall removes the program but not previously shared folders, while hidden Archive may still remain unless the operator removes it manually

That is strong product honesty.
The ordinary operator problem is still surface ownership.
Current Resilio still spreads one everyday answer across Archive, `.sync`, uninstall, and troubleshooting docs.
AnonSync should therefore copy the candor and replace the page family with four ordinary surfaces:

- `552` for **Evidence visibility review**
- `553` for **Hidden witness surfacing**
- `554` for **Surface handoff**
- `555` for **Evidence access receipt**


## Revision addendum — proxy artifacts, visible-entry class, and local-looking action scope after rev0225

Current official Resilio docs are still admirably candid that visible rows are not always ordinary local files: the active v3 line still runs through `3.1.2.1076`; current `What Is an RSLS File?` docs still say `.rsls` entries are zero-byte placeholders representing content without the content itself; the same docs still distinguish `Remove from this device` from all-peer deletion and warn that all peers can end up with placeholders only; and current `Conflict files in Sync` docs still warn that deleting a `.Conflict` file or folder can delete the real corresponding file or folder on a remote peer.
That is good product honesty.
The ordinary operator problem is now artifact-class ownership.
Current Resilio still spreads one everyday answer across placeholder, synchronization-mode, conflict, Archive, and `.sync` docs.
AnonSync should therefore copy the candor and replace the page family with four ordinary surfaces:

- `557` for **Proxy artifact review**
- `558` for **Counterpart map**
- `559` for **Proxy action substitution**
- `560` for **Proxy artifact receipt**


## Revision addendum — subject non-arrival cause, ghost-vs-delay truth, and minimal intervention after rev0226

Current official Resilio docs are still admirably candid that `not here` is not one thing: the active v3 line still runs through `3.1.2.1076`; current `My files don't sync` docs still enumerate IgnoreList exclusion, xattrs limits, local locks, read-only overwrite posture, missing write permissions, encoding/path-length issues, merge failure, filesystem errors, missed notifications, low free space, stuck `.!sync` residue, and clock skew; current `Cannot download files` docs still describe ghost-file states where the tree advertises a subject that no peer now has as full bytes; current watcher-exhaustion docs still say updates may be discovered only after periodic rescan; current `Some internal tasks are taking time to complete` docs still say hidden work can be hashing, merging, scanning, transferring, and writing rather than a hard stall; and current `Service files missing` docs still treat `.sync` loss as continuity-bearing damage that suspends syncing for that folder.
That is good product honesty.
The ordinary operator problem is now subject-level diagnosis ownership.
Current Resilio still spreads one everyday answer across troubleshooting lists, warning articles, lock docs, watcher docs, ghost-file docs, continuity-repair docs, and related-article hops.
AnonSync should therefore copy the candor and replace the page family with four ordinary surfaces:

- `562` for **Subject delivery review**
- `563` for **Absence-cause matrix**
- `564` for **Minimal intervention chooser**
- `565` for **Delivery truth receipt**


## Revision addendum — runtime profile continuity, storage-root lineage, and surface reach after rev0227

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **runtime profile review / storage lineage forecast / runtime switch review / runtime profile receipt**

Current official docs still show a practical product, but they also still show that one ordinary answer to `what actually changed when I switched runtime profile?` can depend on service-install migration choice, service-account changes, storage-root location, config-mode `storage_path`, WebUI listen scope, and uninstall / profile-root cleanup guidance.

That gives AnonSync a cleaner rule: runtime profile is not a hidden implementation detail. The product should own one typed answer for current execution principal, authoritative storage root, continuity verdict, carried-forward shares, and widened or narrowed control surfaces before and after any runtime-envelope change.


## Revision addendum — presence witness grade, hidden-listed peers, and source-proof truth after rev0234

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **presence witness / peer presence review / subject source witness / presence witness receipt**

Current official docs still show a practical product, but they also still show that one ordinary answer to `what is actually present enough here for me to trust this peer row or file row?` can depend on peer-list totals, hidden-offline behavior, green/grey dots, forbidden-network state, pause semantics, sleep policy, source-device online status, and ghost-file warnings.

That gives AnonSync a cleaner rule: presence is not one bit. The product should own one typed answer for listedness, route presence, policy eligibility, and current byte-source sufficiency before it lets any peer row, subject row, or recovery suggestion read as stronger proof than the evidence supports.


## Revision addendum — disappearing safer rungs, edition-shaped action floors, and typed substitution after rev0242

Current official Resilio docs are still admirably candid that not every seat exposes the same severance verbs: the active v3 line still runs through `3.1.2.1076`; current `Disconnecting and Removing Folders` docs still distinguish one-device disconnect from broader remove; current `Selective Sync` docs still tie placeholder-capable posture to feature availability and still warn that removing a Selective-Sync share removes placeholders from the file system on that device; current `Synchronization Modes` and `Folder Types and Management` docs still treat `Disconnected`, `Selective Sync`, and `Synced` as materially different local-byte worlds; and the current desktop Free article still says there is no `Disconnect` button, only `Remove`, explicitly bypassing the disconnect stage because Free offers only `Synced` mode.
That is good product honesty.
The ordinary operator problem is now action-floor ownership.
Current Resilio still spreads one everyday answer across disconnect/remove, Selective Sync, mode, folder-type, and edition-specific help.
AnonSync should therefore copy the candor and replace the page family with four ordinary surfaces:

- `642` for **Action availability**
- `643` for **Severance ladder review**
- `644` for **Capability substitution**
- `645` for **Control-absence receipt**


## Revision addendum — compare-plane mutability, optional property scope, and same-file overclaim after rev0254

Current official Resilio docs are still admirably candid that `needs sync` and `same file` are not one frozen rule: the current pre-seeded guide still says the quick decision uses creation timestamp, modification timestamp, size, and file permissions; the same guide still says creation time can be removed from the equation and that disabling permission sync removes permissions from it; the current file-properties reference still splits properties into synchronized, optionally synchronized, and not synchronized sets by OS/version; current permission docs still say some permission planes are preserved on incompatible storage and only applied later on compatible NTFS or POSIX landings; and current troubleshooting docs still say xattr narrowing can make bundle-like macOS objects sync as ordinary subdirectories.
That is good product honesty.
The ordinary operator problem is now equality-contract ownership.
Current Resilio still spreads one everyday answer across pre-seeded guidance, file-properties tables, permission docs, and troubleshooting notes.
AnonSync should therefore copy the candor and replace the page family with four ordinary surfaces:

- `702` for **Equality posture**
- `703` for **Candidate equivalence review**
- `704` for **Equality evidence**
- `705` for **Equivalence receipt**



## Revision addendum — representative pair, topology slice, and mesh-wide overclaim after rev0270

Current official Resilio docs are still admirably candid that speed evidence comes in different topology scopes: the current `Performance overview` article still exposes per-peer upload/download/RTT/protocol rows; the current slow-speed article still says one slow uploader can reduce other peers' downloads and that more strong uploaders can raise the effective rate; that same article still ends by asking for logs from all peers on stubborn incidents; the current iperf3 guide still measures peer-to-peer network performance between two peers with Sync shut down on both peers; and current folder preferences still make relay/tracker/LAN/predefined-host posture a per-folder, all-peers concern.
That is good product honesty.
The ordinary operator problem is now representativeness-contract ownership.
Current Resilio still spreads one everyday answer across per-peer charts, pairwise benchmarking, route/helper settings, and all-peer escalation.
AnonSync should therefore copy the candor and replace the page family with four ordinary surfaces:

- `782` for **Topology slice**
- `783` for **Representativeness review**
- `784` for **Topology extrapolation**
- `785` for **Topology measurement receipt**


# Resilio change-detection coverage, rescan fallback, and observation-freshness fragmentation evaluation

## Purpose

The archive already had route provenance, representative-pair review, instrumentation posture, and diagnostic receipts.
What it still lacked was one explicit comparison document for another ordinary operator question:

> when the operator asks `how quickly should this change have been noticed, what detection plane was active, and how much blindness or delay was built into that answer?`, where does the product itself own the answer?

Current official Resilio docs are good enough that AnonSync needs a serious answer.
Resilio is not vague about the ingredients.
It documents filesystem notifications, scheduled rescans, manual rescans, watcher exhaustion, notification-hostile storage, IgnoreList reread timing, and power-user rescan tuning.
That candor is worth preserving.

## What Resilio gets right

Resilio is still right that:

- change detection and byte transfer are not the same stage
- filesystem notifications are the fastest detection path when they work
- scheduled rescans are a distinct fallback plane with a different latency profile
- some storage/network shapes are not expected to support notifications reliably
- watcher exhaustion and power-user tuning can materially widen blind windows
- manual rescan is a real operator probe, not merely cosmetic chrome

This is much better than products that pretend every subject is watched continuously and equally.

## What still should not be cloned

The detection-truth contract is still scattered and too support-shaped.
Current official Resilio docs still require the operator to combine at least four article families:

1. **How soon does synchronization start?** for the model of filesystem notifications, scheduled rescans every 600 seconds by default, on-demand rescans, and the fact that `folder_rescan_interval = 0` means no automatic rescan even on restart
2. **Agent run out of system notify watchers** for the Linux watcher-exhaustion warning, the fallback to periodic/manual rescan, and the sysctl-based attempt to raise watcher limits
3. **Ignoring files in Sync (Ignore List)** for the rule that IgnoreList rereads happen on change or, if notifications are not arriving, every `folder_rescan_interval`, with restart recommended for immediate effect
4. **Sync prevents HDD from sleeping on NAS** plus **Power user preferences** for the fact that operators may intentionally widen `folder_rescan_interval` to preserve sleep behavior, while profiler/log/config cadence settings create more runtime posture that affects freshness expectations

That means one ordinary answer is still reconstructed from several places:

- whether this subject is currently under notification-backed observation or rescan-backed observation
- what expected detection latency applies right now
- whether the latency budget was widened intentionally, accidentally, or because the substrate cannot do better
- whether manual rescan is evidence-gathering, a workaround, or the only currently viable detection plane
- what exact sentence is safe about freshness and blindness right now

The substance is useful.
The workflow ownership is still weak.

## Why this matters for AnonSync

AnonSync should not repeat two common mistakes:

1. **continuous-watch overclaim** — treating `connected` or `running` as if every relevant path is being observed in real time
2. **delay-without-ownership** — letting operators discover only after the fact that blindness came from watcher exhaustion, unsupported storage, widened rescan cadence, or a deliberate zero-rescan posture

A serious sync product needs one stable public answer to four different questions:

- **detection-posture truth** — what observation planes were intended and currently active for this subject?
- **coverage truth** — which parts of the subject actually benefit from notifications, and which fall back to rescans or manual probes?
- **freshness truth** — what expected discovery latency and blind-window budget apply right now?
- **intervention truth** — what is the cheapest honest rung: wait, rescan, restore notification capacity, or revise posture?

## Replacement pages in this revision

This revision adds four fixed pages:

- `792` — Detection posture
- `793` — Observation coverage review
- `794` — Change freshness review
- `795` — Change-detection receipt

Together they make detection plane, expected latency, blind-window basis, and strongest safe sentence explicit before AnonSync lets `should have synced already`, `watching normally`, or `just rescan it` become durable incident language.

## Concrete product stance

Borrow from Resilio:

- candid separation of notifications, scheduled rescans, and manual rescans
- candid admission that some storage types and watcher limits break immediate detection
- candid power-user control over rescan cadence and related runtime costs
- candid acknowledgment that detection latency may be widened to preserve storage sleep or reduce pressure

Do not clone from Resilio:

- leaving detection truth split across FAQ prose, warning pages, IgnoreList timing notes, and NAS tuning advice
- letting operators infer freshness from `running` without a declared observation plane
- making manual rescan do triple duty as test, workaround, and hidden detection contract without first-class explanation
- leaving no durable receipt of which latency budget, blind window, and intervention rung applied at the time of judgment

## Evaluation summary

Resilio still deserves credit for not pretending that all file changes are discovered the same way.
But the current product/docs path still leaves a missing object:

> there is no first-class reviewed answer to `what change-detection coverage existed here, how stale could the observation be, and what is the least-strong honest move now?`

AnonSync should therefore make **change-detection coverage** a first-class product object.
Every serious missing-update, stale-view, or delay investigation should publish active detection plane, latency budget, blind-window basis, notification-coverage grade, cheapest honest intervention, strongest allowed sentence, and forbidden stronger sentence before the product treats `delayed`, `stuck`, or `needs rescan` as coherent incident truth.

# Resilio freshness-claim invalidation, posture drift, and revalidation fragmentation evaluation

## Purpose

The archive already had change-detection coverage, blind-window ownership, and freshness claim ceilings.
What it still lacked was the next ordinary operator answer:

> once a freshness judgment exists, what later changes invalidate it, and where does the product itself own that invalidation?

Current official Resilio docs are candid enough that AnonSync needs a sharper answer.
Resilio does not pretend that detection posture is fixed forever.
It separately documents watcher exhaustion, notification-hostile SMB/service paths, NAS sleep-preserving cadence changes, Android auto-sleep, battery-saver stops, forbidden-network posture, manual restarts, and runtime/profile changes.
That candor is worth preserving.

## What Resilio gets right

Resilio is still right that:

- detection quality can materially change after initial setup
- a path family such as SMB or UNC can reduce notification quality relative to local-native storage
- runtime mode changes can alter storage root, service identity, and practical observation behavior
- power-saving posture can widen or even suspend timely discovery
- mobile/network policy can make a share appear connected in one context and fully ineligible in another
- restart and rescan are real revalidation events rather than cosmetic refreshes

This is better than products that act as if one `watching` badge remains authoritative forever.

## What still should not be cloned

The invalidation contract is still scattered and too article-shaped.
Current official Resilio docs still require the operator to combine at least five different article families:

1. **Agent run out of system notify watchers** for the fact that watcher exhaustion can push discovery onto periodic or manual rescans until limits are raised.
2. **Sync Service Troubleshooting on Windows** for the fact that service-style UNC / network-drive setups may not receive update notifications at all, and switching to Local System creates a different storage root and share world.
3. **Sync and SMB file shares** for the fact that SMB notification support depends on SMB 3.0 and that missing notifications mean detection only during full folder rescan.
4. **Sync prevents HDD from sleeping on NAS...** plus **How soon does synchronization start?** for the fact that operators may intentionally widen `folder_rescan_interval` or even set it to zero, directly changing the freshness budget.
5. **Configuring Auto Sleep & Battery Saver (Android)** plus **Setting network interface per share** for the fact that a mobile seat can go offline between wake intervals, stop below battery threshold, or refuse a network entirely so new/updated files are not detected.

That means one ordinary answer is still reconstructed from several places:

- whether a previously issued freshness claim still applies after the host/runtime/path posture changed
- whether the change merely widened the blind window or invalidated the old claim entirely
- whether a prior receipt should be reused, downgraded, or superseded
- what revalidation step is now honest: wait, wake, restart, rescan, restore watchers, or restate the claim ceiling
- what exact sentence is safe right now about the *old* freshness judgment

The substance is useful.
The workflow ownership is still weak.

## Why this matters for AnonSync

AnonSync should not repeat two follow-on mistakes after it already learned to model detection coverage:

1. **receipt immortality** — letting an earlier freshness judgment remain visible as if no later posture drift could weaken it
2. **revalidation folklore** — forcing operators to remember from support prose that SMB, service mode, sleep policy, forbidden network, or watcher exhaustion should reopen the case

A serious sync product now needs one stable public answer to four follow-up questions:

- **invalidation truth** — what changed after the earlier freshness judgment?
- **drift truth** — did the detection posture merely narrow or fundamentally change class?
- **revalidation truth** — what event is strong enough to refresh the claim?
- **receipt truth** — is the old claim still current, downgraded, or superseded?

## Replacement pages in this revision

This revision adds four fixed pages:

- `797` — Freshness invalidator
n- `798` — Freshness revalidation review
- `799` — Posture drift timeline
- `800` — Freshness rollover receipt

Together they make claim expiry, posture drift, and receipt supersession explicit before AnonSync lets `still late`, `still within budget`, or `already checked earlier` become durable language.

## Concrete product stance

Borrow from Resilio:

- candid separation of local-native, SMB/UNC, NAS, service, and mobile power/network postures
- candid admission that runtime changes can alter observation quality and even storage/control world
- candid acknowledgement that sleep/power/network policies create recurring blind windows
- candid use of restart, wake, and rescan as real revalidation events

Do not clone from Resilio:

- leaving invalidation truth split across watcher warnings, service troubleshooting, SMB caveats, NAS sleep advice, and mobile settings articles
- letting an old freshness judgment survive after posture drift without a visible downgrade or supersession
- making operators infer whether a restart or wake meaningfully refreshed the claim
- leaving no durable receipt of what invalidated the prior claim and what newer claim replaced it

## Evaluation summary

Resilio still deserves credit for not pretending that observation posture is eternally stable.
But the current product/docs path still leaves a missing object:

> there is no first-class reviewed answer to `does the earlier freshness judgment still apply after the environment changed, and if not, what replaced it?`

AnonSync should therefore make **freshness-claim invalidation** a first-class product object.
Every serious stale-view, missing-update, or `we already checked this` incident should publish posture drift, invalidator class, revalidation need, supersession state, strongest allowed sentence, and forbidden stronger sentence before the product reuses an earlier freshness receipt as if nothing changed.



## Revision addendum — evaluation after rev0278: borrow residual candor, reject post-quiet folklore

Another current Resilio pass improves the evaluation in one more narrow place.

### Borrow

Keep borrowing these traits:

- admitting that pause leaves specific residual event classes alive instead of pretending that `Paused` means universal stillness
- admitting that scheduled `Paused` can still have asymmetric peer effects rather than flattening everything into one stop bit
- admitting that indexing/share-size growth can continue under paused-looking states
- preserving the uncomfortable but useful truth that visible quiet and semantic quiet are different things

### Refuse to clone

Do not clone these traits:

- making operators remember an old help article just to decide whether a later event fits the allowed residual classes
- letting the first visible movement masquerade as the first real quiet break
- splitting post-quiet event judgment across pause docs, scheduler docs, preferences prose, and changelog folklore
- leaving no durable receipt of whether the earlier quiet claim survived, narrowed, or failed after the event

### Stronger replacement

AnonSync should publish four first-class surfaces instead:

- **Quiet event**
- **Residual allowance review**
- **Quiet challenge ledger**
- **Residual classification receipt**

The governing rule is simple:

> if the product is strong enough to show later motion against a quiet receipt, it must first own whether that motion was declared residue, outside the claim, or the first real break.



## Revision addendum — evaluation after rev0282: borrow rejoin candor, reject restoration folklore

Another current Resilio pass improves the evaluation in one more narrow place.

### Borrow

Keep borrowing these traits:

- admitting that local work on Read Only seats can survive without propagating
- admitting that some healing paths restore source authority destructively rather than merging local work
- admitting that encrypted and backup-oriented seats are preservation lanes with special restore constraints
- admitting that device-local removal or disconnect can preserve bytes elsewhere without proving shared-line restoration

### Refuse to clone

Do not clone these traits:

- making operators infer rejoin class from a pile of permission, backup, encryption, and mobile-help pages
- treating `still exists somewhere` as if it already means `can rejoin the shared line cleanly`
- leaving no stable answer to whether local work should be restored in place, promoted as a successor, preserved only, or abandoned
- leaving no durable receipt of what actually made it back into the shared line versus what merely survived elsewhere

### Stronger replacement

AnonSync should publish four first-class surfaces instead:

- **Maintenance rejoin plan**
- **Maintenance rejoin review**
- **Maintenance rejoin ledger**
- **Maintenance rejoin receipt**

The governing rule is simple:

> if the product is strong enough to say `we can bring this back later`, it must first own whether that means in-place restoration, authority widening, successor promotion, preserve-only survival, or knowing abandonment.

## Revision addendum — evaluation after rev0283: borrow destructive-heal candor, reject overwrite folklore

Another current Resilio pass improves the evaluation in one more narrow place.

### Borrow

Keep borrowing these traits:

- admitting that source-authoritative healing can revert edited contents, restore deleted files, and re-download pre-rename names rather than pretending healing is lossless
- admitting that newly added local files can behave differently from edited existing files under Read Only overwrite healing
- admitting that archive-bearing conditions, retention policy, and device-locality materially change what can still be salvaged
- admitting that encrypted and backup-oriented seats can have harder overwrite postures and weaker ordinary rescue paths

### Refuse to clone

Do not clone these traits:

- making operators infer surrender scope from a pile of one-way-sync, archive, preferences, encryption, and mobile-help pages
- treating `Overwrite changed files` as if it already explains what will be lost or preserved
- leaving no stable answer to whether the current device even bears the older version locally, or whether rescue must come from trash, archive, evidence export, or successor branch
- leaving no durable receipt of what loss was previewed, what salvage was attempted, and what stronger `nothing was lost` sentence remains forbidden

### Stronger replacement

AnonSync should publish four first-class surfaces instead:

- **Maintenance overwrite plan**
- **Maintenance overwrite review**
- **Maintenance overwrite ledger**
- **Maintenance overwrite receipt**

The governing rule is simple:

> if the product is strong enough to offer destructive healing, it must first own the exact surrender scope, salvage ladder, and loss sentence that survive the choice.

## Revision addendum — evaluation after rev0288: borrow permission candor, reject artifact-family policy folklore

Another current Resilio pass improves the evaluation in one more narrow place.

### Borrow

Keep borrowing these traits:

- admitting that read, write, delegate, and revoke are materially different powers
- admitting that linked-own-device seats and externally granted seats are not the same authority plane
- admitting that revocation usually cuts off future updates rather than magically erasing already-held material
- admitting that derivative-local seats can be narrower than their source and can auto-lower when the source is downgraded

### Refuse to clone

Do not clone these traits:

- making operators infer policy from Standard vs Advanced vs linked-device vs local-share family
- treating `change permission` as one universal verb when some cases are live edits and others require reissue or reconnection
- letting `revoke access` sound stronger than `future updates stop while already-synced bytes remain`
- leaving no stable page that says whether a derivative seat can delegate, auto-lowers, or dies with source continuity

### Stronger replacement

AnonSync should publish five first-class surfaces instead:

- **Authority contract**
- **Permission change preview**
- **Delegation boundary review**
- **Revocation impact**
- **Authority policy receipt**

The governing rule is simple:

> if the product is strong enough to say `this seat can read, write, delegate, or is revoked`, it must first own whether that truth comes from live policy, successor issuance, linked-own-seat semantics, or derivative narrowing, and what retained material survives any cutoff.

## Revision addendum — evaluation after rev0289: borrow policy-plane candor, reject provenance folklore

Another current Resilio pass improves the evaluation in one more narrow place.

### Borrow

Keep borrowing these traits:

- admitting that effective settings can genuinely come from different planes such as per-share controls, standing defaults, linked-device defaults, and configuration files
- admitting that some settings affect current subjects while others affect future arrivals or later-created shares
- admitting that configuration-mode startup can be a stronger control plane than casual UI edits
- admitting that platform/runtime caveats can change whether a visible option actually governs behavior from a given surface

### Refuse to clone

Do not clone these traits:

- making the operator merge Folder Preferences, Power user preferences, link-time mode prompts, and configuration-mode notes just to answer `what governs this right now?`
- letting `default` or `None` sound like true inheritance when a sticky local exception may still survive behind the scenes
- hiding config-plane supremacy inside setup prose when configured shares override earlier WebUI ownership
- leaving no durable page that says which plane won, which lower plane lost, and what blast radius a policy edit really has

### Stronger replacement

AnonSync should publish five first-class surfaces instead:

- **Effective policy sheet**
- **Policy change preview**
- **Inheritance return review**
- **Policy drift watch**
- **Policy provenance receipt**

The governing rule is simple:

> if the product is strong enough to show a policy value, it must also own where that value came from, whether it truly inherits, what stronger plane could override it, and which cohort will feel a change.

## Revision addendum — evaluation after rev0290: borrow multi-plane naming candor, reject stale-alias folklore

Another current Resilio pass improves the evaluation in one more narrow place.

### Borrow

Keep borrowing these traits:

- admitting that one sync subject can honestly wear different labels for different audiences
- admitting that local UI alias, on-disk basename, and recipient-facing issuance label are different things
- admitting that a filesystem rename on one seat is local-only rather than a global subject rename
- admitting that some local naming residue can survive continuity changes and therefore matters operationally

### Refuse to clone

Do not clone these traits:

- making the ordinary naming answer depend on separately remembered disk-name behavior, desktop-only UI alias docs, link/QR labeling tricks, and post-disconnect reset lore
- treating an issuance-time recipient label as if it obviously mutates canonical subject identity
- allowing a stale local alias to survive disconnect without visibly downgrading into residue
- leaving no durable preview or receipt that says which naming plane changed and which older labels stayed untouched

### Stronger replacement

AnonSync should publish five first-class surfaces instead:

- **Naming provenance sheet**
- **Name mutation preview**
- **Recipient-label issuance**
- **Alias drift watch**
- **Name lineage receipt**

The governing rule is simple:

> if the product is strong enough to show or change a serious label, it must first own what naming plane that label belongs to, who sees it, whether it is active truth or residue, and which older artifacts still carry older names.

## Revision addendum — evaluation after rev0291: borrow projection candor, reject action-verb folklore

Another current Resilio pass improves the evaluation in one more narrow place.

### Borrow

Keep borrowing these traits:

- admitting that different projections can expose materially different rename powers
- admitting that local UI alias change, filesystem rename, and outward artifact relabel are different mutations
- admitting that mobile and desktop surfaces do not necessarily own the same path semantics
- admitting that recipient-facing labels can be issued without mutating the underlying share name

### Refuse to clone

Do not clone these traits:

- making the ordinary `rename` answer depend on separately remembered desktop tip articles, filesystem FAQs, Android share-detail notes, and sharing-label tricks
- letting the same familiar affordance imply different plane edits without an explicit contract sheet
- relying on projection memory to tell later operators whether a path, alias, canonical title, or outward artifact label changed
- leaving no durable receipt that preserves which projection executed the action and which stronger reading was rejected

### Stronger replacement

AnonSync should publish five first-class surfaces instead:

- **Action verb contract sheet**
- **Rename intent disambiguation**
- **Projection semantic gap review**
- **Cross-projection rename preview**
- **Action lineage receipt**

The governing rule is simple:

> if the product is strong enough to show a rename-like control, it must first own what verb family that control resolves to on this projection, what exact planes it can touch, and what durable receipt will prove the result later.



## Revision addendum — LAN-only proof, helper budgets, and exposure ceilings after rev0292

Current official Resilio docs are still admirably candid that `reachable`, `direct`, `LAN-only`, and `no internet helper in play` are not the same truth: current `Folder Preferences` docs still expose `Use relay server`, `Use tracker server`, `Search LAN`, and `Use predefined hosts`; current `What ports and protocols are used by Sync?` docs still describe a staged route chain from fetching `sync.conf`, to tracker discovery, to direct TCP/UDP on the listening port, to relay fallback, with broadcast/multicast in LAN; current `Can I force Sync to do local network (LAN) syncing only and not sync via the Internet?` docs still say real LAN-only requires disabling tracker and relay in both share and power-user/config settings, enabling multicast, and clearing cached global-IP memory by setting peer expiration to `0`, restarting, and restoring it; current `Power user preferences` still publish `bind_interface`, `use_only_bind_interface`, and `config_refresh_interval`; current `Sync Preferences` still separate listener port, UPnP/NAT-PMP, and proxy posture, including the fact that two proxied peers may only connect via relay; and current `Peers aren't connecting` docs still turn the final route diagnosis into checks across tracker, relay, listening port, multicast, proxy, and multi-NIC posture.

That is real candor.
It still does **not** earn direct interface cloning.

The reason is the next clone-veto rule now applied to another seam:

> one ordinary operator question should have one stable page answer.

Current Resilio still spreads the ordinary `are we truly LAN-only / what exposure did this change permit?` answer across folder preferences, settings, power-user preferences, config steps, and troubleshooting prose.
So the product idea stays useful while the page contract still fails.

That is why this revision adds five narrower replacement pages:

- `899` Reachability contract sheet page
- `900` LAN-scope review page
- `901` Route provenance sheet page
- `902` Exposure budget review page
- `903` Route boundary receipt page

These pages keep the Resilio candor and reject the need to improvise route truth from scattered helper toggles and support instructions.

## Revision addendum — evaluation after rev0295: borrow contested-byte candor, reject repair archaeology

Another current Resilio pass improves the evaluation in one more narrow place.

### Borrow

Keep borrowing these traits:

- admitting that contested bytes can honestly end up blocked, overwritten, preserved side-by-side, or stored in Archive
- admitting that read-only divergence, named conflicts, and offline-writer returns are materially different cases
- admitting that some repair paths depend on runtime posture and restart state rather than just copying bytes around
- admitting that loser versions and local-only extras have real operational fate that should not be hidden

### Refuse to clone

Do not clone these traits:

- making the ordinary repair answer depend on separately remembered conflict-file delete warnings, read-only docs, archive ritual, offline precedence notes, and troubleshooting restart steps
- collapsing blocked intake, parallel survivors, local-only residue, and archive-backed losers into one generic `conflict` story
- leaving no first-class preview of loser fate before a live repair is approved
- letting later operators guess from filenames and history whether a repair actually reconciled the live line or only preserved bytes nearby

### Stronger replacement

AnonSync should publish five first-class surfaces instead:

- **Contested object contract sheet**
- **Repair path review**
- **Survivor set page**
- **Live repair approval**
- **Repair lineage receipt**

The governing rule is simple:

> if the product is strong enough to repair contested bytes, it must first own what is contested, what survives, what move touches the live line, and what stronger reconciliation claim still remains forbidden.

## Further current clone-veto seam — stop proof, hidden runtime, and shutdown fragmentation

Another current official Resilio pass produced a tighter no-clone reason around **stop truth**.
The useful distinctions are real.
The present contract is still too fragmented.

Current official docs still openly distinguish all of the following:

- `Running Sync as a service on Windows` still says Sync can run in the background regardless of logged-in user and can run as `System`, `Local Service`, or current user.
- `Sync interface on Android` still gives `Exit` a separate verb and says it `shuts Sync down correctly`.
- `Does Sync work in background?` still says Android can continue in the background unless killed, while iOS background sync is unavailable; that same article still warns that shutdown and re-open re-index folders and can alter overwrite chronology after offline edits.
- `Settings on mobile platforms` still says disabling Android notifications lowers Sync priority and may force background work to stop.
- `Sync Preferences` still exposes `Start Sync on startup` on desktop.
- `Updating Sync to latest version` and adjacent install/update docs still distinguish app-stop, service-stop, and process-stop according to installation mode.

This is good evidence that Resilio is candid about a real seam.
It is also good evidence that AnonSync should not clone the exact page contract.

To answer one ordinary operator question — **`did I actually stop sync, or did one projection merely disappear while work can still continue or restart?`** — current Resilio still makes the operator combine:

- service/background articles
- mobile-platform background caveats
- an Android-only explicit `Exit` verb
- startup settings
- update/install mode instructions
- shutdown/re-open chronology warnings

AnonSync should keep the distinctions and refuse the archaeology.
That means:

1. **stop becomes a first-class contract object**
2. **projection close/hide never silently equals runtime stop**
3. **drain completion and no-further-publication proof are separate from stop intent**
4. **automatic restart posture is part of stop truth**
5. **restart provenance stays visible because reopen can be chronology-shaping**

That is the reason for this tranche's page family: runtime stop contract sheet, shutdown drain review, runtime stop proof, restart provenance, and runtime stop receipt.


## Revision addendum — birth-time commitments, create-time freezes, and successor-required change after rev0301

Current official Resilio docs are still admirably candid that **not every consequential setting lives on the same mutability plane**.
The current Sync help still says Standard folders cannot be converted into Advanced folders in place and that on-the-fly permission changes are unavailable for Standard folders, requiring remove/re-add with a new key.
The current Active Everywhere docs still say permission-sync settings for Synchronization, Hybrid Work, and File Caching jobs are applied when the job is created and cannot be changed later.
The current Linux cache-server docs still say the selected access and cache paths cannot be changed later after save and that the exposed access path must exist and be empty.
The current migration docs still publish a successor workflow for changing a Sync job into File cache or Hybrid work instead of pretending it is ordinary editing.

This is good evidence that Resilio is candid about a real seam.
It is also good evidence that AnonSync should not clone the exact page contract.

To answer one ordinary operator question — **`can I safely change this later, or is this actually a birth-time commitment?`** — current Resilio still makes the operator combine:

- Standard-versus-Advanced folder docs
- sync-functionality overview prose
- profiles tables
- permission-sync guides
- cache-server setup warnings
- migration instructions

AnonSync should keep the distinctions and refuse the archaeology.
That means:

1. **every consequential field gets a public mutability class**
2. **birth commitments stay visible after creation**
3. **edit and recreate are different verbs**
4. **successor-required change gets one explicit boundary page instead of support folklore**
5. **receipts preserve the rejected stronger sentence that this was merely an in-place edit**

That is the reason for this tranche's page family: mutability contract sheet, birth-commitment review, post-create change preview, recreate boundary, and mutability lineage receipt.


## Further current clone-veto seam — disclosure ceilings, observer classes, and browser-open fragmentation

Another current official Resilio pass produced a tighter no-clone reason around **who can learn what**.
The useful distinctions are real.
The present contract is still too fragmented.

Current official docs still openly distinguish all of the following:

- `Can others see my files? How secure is sharing by Resilio Sync?` still says direct peer transfer, AES-128 in-transit encryption, X.509 authentication, and usage statistics sent in the clear.
- `Can Resilio team see and block/remove any Sync folders?` still says Resilio neither hosts nor caches content, that link-specific information after `#` is not sent from the browser to the server, and that relay cannot examine end-to-end encrypted data.
- `Link structure and flow` still says the landing page can show folder name and size, that the server swaps `https://` to `btsync://`, and that fragment parameters carry folder name, size, folder ID, temporary key, expiration, and client version while not being sent to the server.
- `What ports and protocols are used by Sync?` still says Sync fetches `sync.conf`, sends public/local IPs and share-list participation to tracker infrastructure, and learns peer addresses from that route.
- `Power user preferences` still says `send_statistics` is enabled by default and exports anonymous posture metrics such as OS, version, and active state.

This is good evidence that Resilio is candid about a real seam.
It is also good evidence that AnonSync should not clone the exact page contract.

To answer one ordinary operator question — **`who learned what from this action, by which carrier, and what stronger privacy sentence is still forbidden?`** — current Resilio still makes the operator combine:

- security/privacy FAQ prose
- link-structure docs
- relay docs
- ports/protocol discovery docs
- telemetry settings docs

AnonSync should keep the distinctions and refuse the archaeology.
That means:

1. **disclosure ceiling becomes a first-class contract object**
2. **ciphertext carriage and fact visibility stay separate axes**
3. **carrier, observer, and fact family stay separate modeled objects**
4. **browser-open provenance must say what was local fragment parse versus service-page render**
5. **every serious disclosure path emits a durable receipt with a blocked stronger sentence**

That is the reason for this tranche's page family: disclosure boundary contract sheet, carrier disclosure review, third-party knowledge proof, browser-open boundary, and disclosure lineage receipt.

## Further current clone-veto seam — event evidence retention, attribution gaps, and audit ceilings

Another current official Resilio pass produced a tighter no-clone reason around **what proof survives**.
The useful distinctions are real.
The present contract is still too fragmented.

Current official docs still openly distinguish all of the following:

- `Sync Main View (Desktop)` still says **History** shows general syncing activity for the last **30 days**.
- `Using Archive for file versioning and restoring deleted files.` still says **Archive** does not provide details on which peer made changes and points the operator to **History** for that attribution.
- that same archive article still says archive retention defaults differ by platform: **30 days on desktops** and **1 day on mobiles**.
- `Sync Preferences` still exposes **Show notifications**, which makes notifications a configurable signal plane rather than a durable evidence plane.
- `Sharing files (iOS)` still says transfer history can remain visible even after the downloaded file is removed from the device.
- older changelog/UI lineage still preserves observational aids such as `Date synced`, `Last transferred`, and synchronized notifications.

This is good evidence that Resilio is candid about a real seam.
It is also good evidence that AnonSync should not clone the exact page contract.

To answer one ordinary operator question — **`what durable proof remains of this event, what does it actually prove, and how long until that proof weakens?`** — current Resilio still makes the operator combine:

- main-view / History docs
- Archive docs
- notification settings docs
- transfer-history platform docs
- older changelog notes about convenience evidence surfaces

AnonSync should keep the distinctions and refuse the archaeology.
That means:

1. **evidence family becomes a first-class contract object**
2. **retention horizon becomes visible before expiry weakens the claim**
3. **byte witness and actor witness stay separate unless explicitly joined**
4. **notifications and convenience timestamps stay below durable-proof status unless promoted through review**
5. **every serious event claim emits a durable receipt with the blocked stronger sentence**

That is the reason for this tranche's page family: evidence retention contract sheet, evidence-source join review, attribution gap page, retention horizon watch, and evidence lineage receipt.


## Further current clone-veto seam — hidden control substrate, capsule integrity, and sidecar governance

Another current official Resilio pass produced a tighter no-clone reason around **what inside the synced tree is actually control substrate**.
The useful distinctions are real.
The present contract is still too fragmented.

Current official docs still openly distinguish all of the following:

- `What is '.sync' folder...` still says every shared folder gets a hidden `.sync` system folder, that it is critical for syncing, that it must not be moved separately from the shared folder, and that the same namespace also contains the ID file, IgnoreList, StreamsList, and `.!sync` transfer files.
- `Service files missing / Cannot identify destination folder` still says deleting or corrupting `.sync` suspends synchronization and that adding the same folder to two Sync instances can corrupt internal files and make further sync impossible until the share is removed and re-added.
- `Ignoring files in Sync (Ignore List)` still says IgnoreList is an editable UTF-8 sidecar inside `.sync`, affects indexing / size accounting / future publication, and is not fully retroactive to already-synced structure.
- `Alt Streams and Xattrs in Sync` still says StreamsList is an editable text whitelist and that `.sync/Streams` can hold metadata stubs when a peer cannot store xattrs natively.

This is good evidence that Resilio is candid about a real seam.
It is also good evidence that AnonSync should not clone the exact page contract.

To answer one ordinary operator question — **`what in this folder is user content, what is service capsule, what is editable policy, and what can break if touched or double-owned?`** — current Resilio still makes the operator combine:

- `.sync` FAQ prose
- service-file troubleshooting
- IgnoreList timing notes
- Streams/xattr propagation notes

AnonSync should keep the distinctions and refuse the archaeology.
That means:

1. **control substrate becomes a first-class contract object**
2. **hidden is not an adequate warning channel for fragile service state**
3. **service capsule, editable policy sidecars, metadata residue, and temp transfer artifacts become separate classes**
4. **dual ownership of one local capsule becomes a first-class collision**
5. **every serious substrate mutation emits a durable receipt with a blocked stronger sentence**

That is the reason for this tranche's page family: control substrate contract sheet, system capsule integrity review, twin-runtime collision warning, sidecar governance visibility, and control substrate lineage receipt.

## Revision addendum — live state, persisted state, and boot-authority replay after rev0309

Current official Resilio docs are still admirably candid that `changed now`, `saved durably`, and `will boot back this way` are not the same truth: current `Power user preferences` docs still say `config_save_interval` defaults to **600 seconds** and controls how often settings are saved to storage; current `Sync prevents HDD from sleeping on NAS...` docs still recommend widening `config_save_interval` to values like **18000 seconds** along with refresh/rescan cadence; current `Running Sync in configuration mode` docs still say config-defined shared folders disable WebUI and override folders previously added from WebUI; current `Configuring WebUI` docs still split listener binding authority between config mode and ordinary settings; current `Guide to Linux, and Sync peculiarities` docs still say storage is where Sync keeps settings, identity, and applied license; and current `Sync Service Troubleshooting on Windows` docs still say a service-user switch can create a new storage folder world where prior shares are absent until re-added/re-shared.

Those distinctions are useful.
The present contract is still too fragmented.

To answer one ordinary operator question — **`I changed this; what is true now, what survives restart/crash, and what world will next boot actually reconstruct?`** — current Resilio still makes the operator combine save-cadence docs, NAS sleep advice, config-mode override behavior, storage-home docs, and service-user troubleshooting.

AnonSync should keep the distinctions and refuse the archaeology.
That means:

1. **live-applied, durable-persisted, and boot-authoritative become separate first-class verdicts**
2. **stronger config planes must be visible at the point of edit and at the point of reliance**
3. **storage-home changes become lineage events, not cosmetic service toggles**
4. **risky actions should review persistence class before continuing**
5. **every mutation receipt must preserve the strongest safe restart/crash sentence and the blocked stronger sentence**

That is the reason for this tranche's page family: mutation durability contract sheet, persist-before-risk review, persisted-state proof, boot-authority replay review, and mutation durability receipt.



## Further current clone-veto seam — path identity, canonicalization, and equivalence-class truth

Another current official Resilio pass produced a tighter no-clone reason around **what it means for two filenames to be the same subject identity across a heterogeneous cohort**.
The useful distinctions are real.
The present contract is still too fragmented.

Current official docs still openly distinguish all of the following:

- `Power user preferences` still exposes `normalize_unicode_paths = true` and describes it as normalizing Unicode names into composed/decomposed form.
- `Conflict files in Sync` still says conflicts can arise from case-insensitive peers, decomposed UTF symbols, prohibited filesystem symbols, and linked junctions, and still tells operators to keep the same letter case and encoding across devices.
- `My files don't sync` still says Sync expects UTF-8 naming, still warns about special symbols and path-length limits, and still treats encoding mismatches as a real cause of non-sync.
- `Unsupported asterisk (*)...` still says some invalid trailing-asterisk names may be interpreted as system data and disrupt syncing.
- the current changelog still records fixes for mixed composed/decomposed filename crashes, invalid symbols in Windows paths, and trailing-dot syncing to Windows peers.

This is good evidence that Resilio is candid about a real seam.
It is also good evidence that AnonSync should not clone the exact page contract.

To answer one ordinary operator question — **`are these two paths literally the same, canonically the same, or cohort-unsafe despite looking fine here?`** — current Resilio still makes the operator combine:

- power-user normalization settings
- conflict examples and cleanup guidance
- generic troubleshooting notes about UTF-8 and path length
- special-case invalid-name warnings
- changelog archaeology proving the class is operationally real

AnonSync should keep the distinctions and refuse the archaeology.
That means:

1. **path identity becomes a first-class contract object**
2. **rendered name, raw form, and canonical comparison basis become separate visible truths**
3. **local acceptability does not imply cohort-safe identity**
4. **same-looking/different-byte and different-looking/canonical-collision cases get a dedicated warning family**
5. **every serious path-identity decision emits a durable receipt with the blocked stronger sentence**

That is the reason for this tranche's page family: path identity contract sheet, canonicalization review, equivalence collision warning, path validity preview, and path identity lineage receipt.


## Further current clone-veto seam — special-object fidelity, symbolic-link boundary, and bundle-collapse truth

Another current official Resilio pass produced a tighter no-clone reason around **what it means for a path entry to be an ordinary subject, a preserved reference object, or a metadata-dependent bundle whose semantics may collapse across peers**.
The useful distinctions are real.
The present contract is still too fragmented.

Current official docs still openly distinguish all of the following:

- `Soft links, hard links and symbolic links` still saying Windows does not support junctions, hard links, or symbolic links in Sync and that using them may produce `.Conflict` entries.
- that same article still saying Unix can synchronize the symbolic-link object itself while **not** synchronizing the referenced target unless the target is added separately.
- `Power user preferences` still exposing `ignore_symlinks` and `sync_extended_attributes` as current settings.
- `Alt Streams and Xattrs in Sync` still saying xattrs are synchronized only according to the `.sync/StreamsList` whitelist and that peers that cannot store them natively may create stub data in `.sync/Streams`.
- `My files don't sync` still saying that disabling xattr syncing can make file bundles such as Pages, Keynote, and macOS apps sync as ordinary subdirectories instead.

This is good evidence that Resilio is candid about a real seam.
It is also good evidence that AnonSync should not clone the exact page contract.

To answer one ordinary operator question — **`what object is this really, and what semantics survive across the cohort?`** — current Resilio still makes the operator combine:

- symlink support rules
- power-user suppression/metadata settings
- StreamsList and `.sync/Streams` compatibility behavior
- troubleshooting notes about bundle collapse

AnonSync should keep the distinctions and refuse the archaeology.
That means:

1. **object kind becomes a first-class contract object**
2. **reference preservation and target-follow become separate visible verbs**
3. **bundle fidelity becomes an explicit reviewed ceiling instead of a hidden xattr side effect**
4. **compatibility residue becomes a first-class state rather than quiet implementation detail**
5. **every serious special-object decision emits a durable receipt with the blocked stronger sentence**

That is the reason for this tranche's page family: special object contract sheet, special object intake review, link target boundary, bundle fidelity warning, and special object lineage receipt.
