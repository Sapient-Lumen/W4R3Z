## Revision addendum — nested overlap topology, bridge hosts, and carried-edit truth

This revision continues directly from `rev0314` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **sharing a nested child folder separately, bridge-host propagation, disabled Selective Sync, and duplicate indexing/rescan cost**.
2. Tightens the non-clone line again: borrow Resilio's candor that parent/child overlap creates a real graph; refuse any contract where the operator still has to infer `who can seed whom and how child edits travel` from an FAQ and filesystem hierarchy alone.
3. Adds one new **Resilio evaluation** document focused on why present-day nested-overlap truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for overlapping subject contract sheet, overlap topology review, independent seed horizon, overlap load warning, and overlap lineage receipt.
5. Makes one hard product decision explicit: **overlap is a first-class topology object**.
6. Makes another hard product decision explicit: **bridge hosts are explicit whenever they can carry edits between audiences**.
7. Makes a third hard product decision explicit: **nested overlap is blocked by default unless cost and carried-edit consequences are reviewed**.
8. Integrates the work back into the comparison spine.

## Revision addendum — resource budget, starvation truth, and bottleneck proof

This revision continues directly from `rev0313` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **global send/receive rates, scheduler pause semantics, power-user resource knobs, queue priority behavior, hidden internal work, and RAM-scale warnings**.
2. Tightens the non-clone line again: borrow Resilio's candor that slowdown has many real causes; refuse any contract where the operator still has to reconstruct `what is slow, why, and who is paying?` from five different articles.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio resource-budget truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: resource budget contract sheet, resource budget review, starvation and suspension warning, resource pressure proof, and resource budget lineage receipt.
5. Makes one hard product decision explicit: **resource budget is a first-class contract object**.
6. Makes another hard product decision explicit: **budget lanes stay separate — WAN, LAN, disk, CPU/indexing, memory, and free-space are not one `performance` bar**.
7. Makes a third hard product decision explicit: **starvation and queue-preemption truth must be inspectable rather than hidden behind list order or `paused` folklore**.
8. Packages the result as another continuation archive whose new tranche makes the `resource-budget / precedence / starvation / bottleneck-proof / durable-receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present resource-budget contract**

This time the reason is especially clear around **internet-only default rate limits, schedule pauses that still allow some mutation, power-user knobs that materially change resource fairness, queue priority with caps and exceptions, and memory pressure that reflects structural tree size rather than transient noise**.
Current official Resilio docs still leave the operator reconstructing one ordinary answer — `what is constraining throughput right now, and who is being starved?` — from preferences, power-user settings, queue docs, and troubleshooting pages rather than one owned contract.
That is exactly where AnonSync should diverge.

## Revision addendum — raw-state clone boundary, cold successor import, and seat rebirth proof

This revision continues directly from `rev0312` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **unsupported cloning, storage-folder contents, per-install digital certificates, and identity replacement by unlink/new certificate generation**.
2. Tightens the non-clone line again: borrow Resilio's candor that copied Sync state is dangerous; refuse any contract where the operator still has to reconstruct `is this safe replacement or unsafe duplicate?` from scattered cloning/storage/identity docs.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio clone/successor truth is still too blunt to clone even though the warning itself is valuable.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: successor capsule contract sheet, state adoption review, duplicate seat collision warning, successor activation proof, and state lineage receipt.
5. Makes one hard product decision explicit: **raw state cloning is never the normal continuity path**.
6. Makes another hard product decision explicit: **replacement must pass through reviewed successor import or be blocked/inspection-only**.
7. Makes a third hard product decision explicit: **seat rebirth and subject carry-forward are separate truths**.
8. Packages the result as another continuation archive whose new tranche makes the `raw-clone / successor-capsule / duplicate-seat / stale-backup / reborn-seat-proof` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's blunt honesty**
- **do not clone Resilio's present clone/successor contract**

This time the reason is especially clear around **the still-current `Cloning Sync` warning, the still-current statement that the storage folder contains configuration and shares database state, and the still-current identity docs that say each installation gets a unique digital certificate**.
Current Resilio still tells the truth that copied state is dangerous.
What it still does not give the operator is one owned page family for `cold successor import` versus `stale backup` versus `concurrent duplicate seat`.

That is exactly where AnonSync should diverge.

## Revision addendum — invocation profile, launch switches, and runtime-world proof

This revision continues directly from `rev0311` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **Windows launch switches, Linux/headless launch args, config-owned storage roots, service storage worlds, loopback-vs-LAN control exposure, and update continuity for non-default launches**.
2. Tightens the non-clone line again: borrow Resilio's candor that launch is not one flat verb; refuse any contract where the operator still has to reconstruct `what world am I actually starting, and what control/exposure does that imply?` from several admin articles.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio invocation-profile truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: invocation profile contract sheet, launch review, quiet-runtime proof, launch world preview, and invocation lineage receipt.
5. Makes one hard product decision explicit: **launch intent becomes a first-class reviewed object whenever it can change world lineage, visibility truth, or control exposure**.
6. Makes another hard product decision explicit: **hidden/minimized/service/headless are projection postures, not reliable substitutes for stop or same-world claims**.
7. Makes a third hard product decision explicit: **storage-root choice is state adoption and world selection, not a cosmetic convenience**.
8. Packages the result as another continuation archive whose new tranche makes the `invocation-profile / launch-review / quiet-runtime-proof / launch-world-preview / durable-receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present invocation contract**

This time the reason is especially clear around **Windows CLI flags that materially change storage, visibility, or listener scope; Linux defaults that can create a `.sync` world in the current directory; config-mode rules that can create settings in a non-default `storage_path`; service-account shifts that surface a different storage world; and update instructions that preserve continuity only if the operator relaunches with the same parameters and same user**.
Current official materials simultaneously show that:

- the current Windows CLI article still says `/config`, `/webui`, `/storage`, `/noinstall`, `/S`, and `/minimized` materially change how Sync starts.
- the current Linux guide still says `--storage` controls where settings, identity, and license live; without it a `.sync` folder is created in the current directory; `--identity` and `--license` also fall back to that storage unless explicitly redirected; and `--webui.listen` can widen control exposure or even cause shutdown if pinned to an unavailable interface.
- the current config-mode guide still says a non-default `storage_path` creates settings there and that service config mode works only from the service storage.
- the current Windows service troubleshooting guide still says switching to Local System yields a different storage folder and an empty-looking roster that must be re-added and re-shared.
- the current v3 update guide still says non-default `/config` or `/storage` launches must be restarted with the same parameters, and Linux binary installs must be relaunched with the same parameters and the same user to preserve configuration.

That candor is useful.
The invocation contract is the problem.
AnonSync should not clone a world where `start`, `silent`, `minimized`, `service`, `headless`, `browser-open`, and `use this storage root` still require article memory to know whether they preserve the same runtime world.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful distinctions between launch intent, world lineage, quietness, and control exposure are real, but the present contract still hides too much meaning across CLI help, Linux notes, config-mode instructions, service troubleshooting, and update ritual instead of owning invocation profile as one stable page family.**

## Revision addendum — path identity, canonicalization, and equivalence-class truth

This revision continues directly from `rev0310` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **Unicode normalization, case posture, invalid-symbol rules, conflict examples, UTF-8 expectations, and path-name bugfix history**.
2. Tightens the non-clone line again: borrow Resilio's candor that path identity is not just whatever one local filesystem accepts; refuse any contract where the operator still has to reconstruct `are these two names the same thing, a collision, or a peer-specific rewrite?` from several help pages and changelog notes.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio path-identity truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: path identity contract sheet, canonicalization review, equivalence collision warning, path validity preview, and path identity lineage receipt.
5. Makes one hard product decision explicit: **path identity becomes a first-class contract object rather than a side effect of conflict recovery**.
6. Makes another hard product decision explicit: **rendered name, raw form, and canonical comparison basis are separate truths**.
7. Makes a third hard product decision explicit: **local acceptability never by itself proves cohort-safe identity or portable rename semantics**.
8. Packages the result as another continuation archive whose new tranche makes the `path-identity / canonical-basis / equivalence-collision / portability-preview / durable-receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present path-identity contract**

This time the reason is especially clear around **hidden Unicode normalization policy, case-sensitive versus case-insensitive peers, same-looking composed/decomposed names, invalid-symbol and trailing-form portability, and bugfix history that proves these are not merely theoretical edge cases**.
Current official materials simultaneously show that:

- the current `Power user preferences` article still exposes `normalize_unicode_paths = true` and describes it as normalizing Unicode filenames into composed/decomposed form.
- the current `Conflict files in Sync` article still says conflicts can arise from case-insensitive peers, decomposed UTF symbols, prohibited filesystem symbols, and linked junctions, and still says operators should keep the same letter case and encoding across devices.
- the current `My files don't sync` article still says Sync expects UTF-8 naming, still flags special-symbol/encoding trouble, and still warns about path-length limits.
- the current `Unsupported asterisk (*)...` article still says one invalid trailing-asterisk family can be interpreted as system data and disrupt syncing.
- the current changelog still records fixes for crashes caused by mixed composed/decomposed symbols in filenames, invalid symbols in Windows paths, and trailing-dot syncing to Windows peers.

That candor is useful.
The path-identity contract is the problem.
AnonSync should not clone a world where the operator still has to remember whether a visible filename, a raw codepoint form, a canonicalized comparison form, and a peer-rewritten path all answer the same equality question.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful path-identity distinctions are real, but the present contract still hides too much meaning across power-user settings, conflict guidance, troubleshooting notes, invalid-name warnings, and changelog archaeology instead of owning path identity as one stable page family.**

## Revision addendum — requester proof, human-label collision, and linked-family trust scope

This revision continues directly from `rev0308` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **identity names, device labels, certificate fingerprints, approval flow, X509 issuance, ACL signing, and linked-device auto-approval widening**.
2. Tightens the non-clone line again: borrow Resilio's candor that names, devices, fingerprints, and linked families are materially different; refuse any contract where the operator still has to reconstruct `who exactly am I approving, and how far does that trust travel?` from several help pages.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio requester-proof truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: requester identity contract sheet, requester collision review, proof handle page, trust expansion review, and requester lineage receipt.
5. Makes one hard product decision explicit: **human-readable labels are hints, not trust handles**.
6. Makes another hard product decision explicit: **approval memory binds to the reviewed requester handle bundle, not to a remembered display name**.
7. Makes a third hard product decision explicit: **linked-family widening is a second decision, not a silent consequence of approving one requester**.
8. Packages the result as another continuation archive whose new tranche makes the `requester-proof / label-collision / proof-handle / family-expansion / durable-receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present requester-identity contract**

This time the reason is especially clear around **same-name different-certificate requesters, approval surfaces that show both user name and public-key fingerprint, and a trust-memory model that can widen to all linked devices**.
Current official materials simultaneously show that:

- the current `Sync Private Identity & Linking My Devices` article still says every installation gets a unique digital certificate and random fingerprint, that even two independent instances with the same identity name still have different certificates, and that a remote user can choose to automatically approve all linked devices for future sharing.
- the current `Link structure and flow` article still says the approval flow shows the requester's user name and public-key fingerprint, that the approver can compare the fingerprint, and that only after approval does the owner issue an X509 certificate and sign an ACL entry for the requester.
- the current `Settings on mobile platforms` article still exposes identity name, device name, and certificate fingerprint together as part of what other users recognize.

That candor is useful.
The requester-proof contract is the problem.
AnonSync should not clone a world where the operator still has to remember whether a human name, a device label, a fingerprint, and a linked family all answer the same trust question.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful distinctions between labels, devices, proof handles, and linked families are real, but the present contract still hides too much meaning across identity docs, link-flow prose, and settings pages instead of owning requester proof as one stable page family.**

## Revision addendum — hidden control substrate, service capsule integrity, and sidecar governance

This revision continues directly from `rev0307` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **hidden `.sync` service state, ID-file criticality, user-editable IgnoreList and StreamsList sidecars, xattr stub propagation, temporary `.!sync` artifacts, and same-folder dual-instance corruption**.
2. Tightens the non-clone line again: borrow Resilio's candor that a synced folder is not just user bytes; refuse any contract where the operator still has to reconstruct `what in this namespace is content, policy, capsule, or fragile residue?` from FAQ and troubleshooting pages.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio control-substrate truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: control substrate contract sheet, system capsule integrity review, twin-runtime collision warning, sidecar governance visibility, and control substrate lineage receipt.
5. Makes one hard product decision explicit: **hiddenness is not an adequate warning channel for service-critical control substrate**.
6. Makes another hard product decision explicit: **service capsule, editable policy sidecars, compatibility residue, and temporary transfer artifacts are different classes**.
7. Makes a third hard product decision explicit: **dual ownership of one local control capsule is a first-class collision, not a support footnote**.
8. Packages the result as another continuation archive whose new tranche makes the `hidden-control-substrate / capsule-integrity / sidecar-governance / twin-runtime-collision / durable-receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present hidden-control-substrate contract**

This time the reason is especially clear around **critical hidden `.sync` state, movable-versus-non-movable capsule boundaries, user-editable IgnoreList and StreamsList sidecars, metadata stub propagation inside `.sync/Streams`, temporary `.!sync` transfer files, and same-folder dual-instance corruption/suspension risk**.
Current official materials simultaneously show that:

- the current `What is '.sync' folder...` article still says every shared folder gets a hidden `.sync` system folder, that it is critical for syncing, that it must not be moved separately from the shared folder, and that the namespace also contains ID, IgnoreList, StreamsList, and `.!sync` transfer files.
- the current `Service files missing / Cannot identify destination folder` article still says deleting or corrupting `.sync` suspends synchronization and that adding the same folder to two Sync instances can corrupt the former instance's internal files and make further sync impossible until the share is re-added.
- the current `Ignoring files in Sync (Ignore List)` article still says IgnoreList is an editable UTF-8 sidecar inside `.sync`, affects indexing and size accounting, is not retroactive to already-synced structure, and is reread on change or rescan.
- the current `Alt Streams and Xattrs in Sync` article still says StreamsList is a regular editable text whitelist, and that when a peer cannot store xattrs natively, Sync may create stub files under `.sync/Streams` so metadata can continue propagating.

That candor is useful.
The control-substrate contract is the problem.
AnonSync should not clone a world where the operator still has to remember whether `hidden`, `.sync`, `IgnoreList`, `StreamsList`, `.!sync`, and `Streams` are all the same kind of object.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful hidden-control distinctions are real, but the present contract still hides too much meaning inside FAQ pages, troubleshooting notes, IgnoreList timing docs, and xattr propagation docs instead of owning control substrate as one stable page family.**


## Revision addendum — time authority, timestamp provenance, and replay chronology truth

This revision continues directly from `rev0306` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **GMT-based file ordering, time-difference warnings, skew-budget settings, database-only mtime fallback, archive replay, and internal-clock dependence**.
2. Tightens the non-clone line again: borrow Resilio's candor that chronology really depends on time and `mtime`; refuse any contract where the operator still has to reconstruct `which timestamp actually governs?` from several help pages.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio time-authority truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: temporal authority contract sheet, clock-skew/time-authority review, timestamp provenance proof, replay chronology review, and temporal lineage receipt.
5. Makes one hard product decision explicit: **disk-visible `mtime` and chronology-authoritative `mtime` are separate truths when assignment fails or trust degrades**.
6. Makes another hard product decision explicit: **archive replay is chronology-sensitive and must preview re-archive / overwrite risk before apply**.
7. Makes a third hard product decision explicit: **skew budget, timezone fault, and ledger-only fallback are first-class operator facts**.
8. Packages the result as another continuation archive whose new tranche makes the `time-authority / disk-vs-ledger-mtime / skew-review / replay-chronology / durable-receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present time-authority contract**

This time the reason is especially clear around **GMT-normalized file ordering, 600-second skew budgets, database-only authoritative mtime, and archive restore candidates that can be re-archived if replay timing is wrong**.
Current official materials simultaneously show that:

- `Time difference` still says Sync decides which file is newer by comparing **files modification time**, converting it to **GMT**, and warning when peer time difference exceeds the allowed window.
- `Power user preferences` still says `sync_max_time_diff` defaults to **600 seconds** and that `ignore_mtime_assign_errors` can keep the **correct mtime only in the database** while disk `mtime` becomes **current timestamp**.
- `Using Archive for file versioning and restoring deleted files.` still says restored files carry an **older modified timestamp** than other peers and that replay can fail if Sync is not running during restore.
- the desktop and mobile syncing guides still say Sync relies on each device's **internal clock** and that wrong time or timezone causes `Excessive time difference` behavior.

That candor is useful.
The time-authority contract is the problem.
AnonSync should not clone a world where `modified on disk`, `authoritative in ledger`, `restored from archive`, and `clock looks okay` still read like one truth.

## New documents in rev0307

- `982` Resilio time authority, disk-vs-database timestamp, and replay-chronology evaluation
- `983` Temporal authority contract sheet page
- `984` Clock-skew and time-authority review page
- `985` Timestamp provenance proof page
- `986` Replay chronology review page
- `987` Temporal lineage receipt page

## Revision addendum — completion horizons, freshness proof, and hidden-lag truth

This revision continues directly from `rev0304` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **desktop status meaning, peer counts, offline-peer expiry, troubleshooting guidance, hidden background operations, detection latency, and observational surrogate columns such as last-transferred/date-synced**.
2. Tightens the non-clone line again: borrow Resilio's candor that green state is relative and that background work is real; refuse any contract where the operator still has to reconstruct `complete relative to whom, and with what freshness debt?` from several UI/help pages.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio completion/freshness truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: completion boundary contract sheet, completion claim review, freshness proof, stale peer debt watch, and completion lineage receipt.
5. Makes one hard product decision explicit: **completion is always horizon-scoped** rather than global by implication.
6. Makes another hard product decision explicit: **freshness is not inferred from a green check, quiet transfer, or last-transferred alone**.
7. Makes a third hard product decision explicit: **offline debt, peer aging, detection lag, and hidden internal work are first-class truth objects**.
8. Packages the result as another continuation archive whose new tranche makes the `completion-horizon / freshness-proof / stale-peer-debt / hidden-lag / durable-receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present completion/freshness contract**

This time the reason is especially clear around **green-check relativity, X-of-Y peer horizon, peer expiration, queue/history troubleshooting, hidden background work, and detection-latency truth**.
Current official materials simultaneously show that:

- `Sync Main View (Desktop)` still says the green checkmark means files are synced with **all connected peers**, not all known or intended peers, and still says `X of Y peers` includes offline peers while peers offline for 7 days can be disconnected through a power-user setting.
- `My files don't sync` still tells operators to inspect the peer list, status warnings, history, and upload/download queue separately when not all files are synced.
- `Some internal tasks are taking time to complete` still says important background work such as hashing, scanning, merging, reading, writing, and block checking can continue out of sight and may slow or postpone visible completion.
- `How soon does synchronization start?` still says change discovery depends on filesystem notifications, rescans every 600 seconds by default, and optional manual rescan, with notifications absent or degraded on some storage classes.
- the current change-log lineage still shows observational aids such as `Date synced` and `Last transferred`, which are useful but still weaker than one owned proof contract.

That candor is useful.
The completion/freshness contract is the problem.
AnonSync should not clone a world where the operator still has to remember whether `green`, `X of Y`, `last transferred`, `history quiet`, and `queue empty` together imply `done`.

## New documents in rev0305

- `970` Resilio completion, freshness, peer horizon, and hidden-lag fragmentation evaluation
- `971` Completion boundary contract sheet page
- `972` Completion claim review page
- `973` Freshness proof page
- `974` Stale peer debt watch page
- `975` Completion lineage receipt page

## Revision addendum — disclosure ceilings, observer classes, and browser-open truth

This revision continues directly from `rev0303` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **security/privacy claims, browser landing-page behavior, link-fragment locality, relay blindness, tracker/config discovery, and default telemetry export**.
2. Tightens the non-clone line again: borrow Resilio's candor that peers, relays, trackers, browser handlers, and telemetry recipients are materially different observer classes; refuse any contract where the operator still has to reconstruct `who learned what?` from several FAQs and settings pages.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio disclosure truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: disclosure boundary contract sheet, carrier disclosure review, third-party knowledge proof, browser-open boundary, and disclosure lineage receipt.
5. Makes one hard product decision explicit: **disclosure ceiling is a first-class contract object** rather than a marketing adjective.
6. Makes another hard product decision explicit: **ciphertext carriage and fact visibility stay separate axes** rather than collapsing into one `secure` badge.
7. Makes a third hard product decision explicit: **carrier, observer, and fact family are separate modeled objects**, so the product must publish the blocked stronger privacy sentence instead of letting operators over-infer.
8. Packages the result as another continuation archive whose new tranche makes the `disclosure-ceiling / observer-class / browser-open-boundary / local-fragment-proof / durable-receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present privacy/disclosure contract**

This time the reason is especially clear around **cloudless-but-not-zero-disclosure posture, link-fragment locality, landing-page preview behavior, relay blindness, tracker-visible route facts, and telemetry defaults**.
Current official materials simultaneously show that:

- `Can others see my files? How secure is sharing by Resilio Sync?` still says peer data is directly transferred and AES-128 encrypted in transit, that X.509 certificates are used for mutual authentication, and that Resilio collects usage statistics sent in the clear.
- `Can Resilio team see and block/remove any Sync folders?` still says Resilio neither hosts nor caches content, does not distribute links, that link-specific information after `#` is not sent from the browser to the server, and that relay cannot examine encrypted data flowing through it.
- `Link structure and flow` still says the landing page can show folder name and size, that the server replaces `https://` with `btsync://`, and that fragment parameters can contain folder name, size, folder ID, temporary key, expiration, and client version while remaining outside the server-requested URL.
- `What ports and protocols are used by Sync?` still says Sync fetches `sync.conf`, communicates public and local IP addresses plus share lists to tracker infrastructure, and learns peer addresses from that path.
- `Power user preferences` still says `send_statistics` defaults to `true` and exports anonymous statistical metrics such as OS, Sync version, and whether Sync is active.

That candor is useful.
The disclosure contract is the problem.
AnonSync should not clone a world where the operator still has to remember whether `direct`, `relay`, `landing page`, `tracker`, and `telemetry` imply the same or different knowledge ceilings.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful disclosure distinctions are real, but the present contract still hides too much meaning inside security FAQ pages, link-structure docs, relay docs, ports/protocol docs, and telemetry settings instead of owning disclosure truth as one stable page family.**

## Revision addendum — permission metadata, principal mapping, and apply-ceiling truth

This revision continues directly from `rev0302` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **file-system permission synchronization, NTFS/POSIX mode families, create-time-fixed permission policy, runtime-principal requirements, target identity mapping, pre-seeded ownership ambiguity, and concrete permission-application failures**.
2. Tightens the non-clone line again: borrow Resilio's candor that permission metadata is operationally real; refuse any contract where the operator still has to reconstruct permission truth from profile tables, service-account lore, cross-platform caveats, and troubleshooting pages.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio permission-metadata truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: metadata authority contract sheet, permission sync review, principal mapping proof, permission failure review, and metadata lineage receipt.
5. Makes one hard product decision explicit: **byte truth and metadata truth are separate axes**.
6. Makes another hard product decision explicit: **runtime principal and target identity mapping are part of the permission contract**.
7. Makes a third hard product decision explicit: **preserve-only, native apply, local inheritance rewrite, and bytes-only continuation are distinct postures with distinct claim ceilings**.
8. Packages the result as another continuation archive whose new tranche makes the `metadata-authority / principal-proof / mapping-ceiling / permission-failure / durable-receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present permission-metadata contract**

This time the reason is especially clear around **create-time-fixed permission policy, NTFS mode families, Local System vs Domain Admin requirements, cross-platform preservation without native application, and concrete target identity-mapping failures**.
Current official materials simultaneously show that:

- `Syncing file system permissions` still says Resilio Active Everywhere can synchronize NTFS and POSIX permissions, that several job families fix those settings at creation time, that NTFS mode selection materially changes semantics, that Local System / local admin / Domain Admin requirements differ by mode, that non-native targets may only preserve permission intent, and that pre-seeded RW merges can scramble ownership without a Reference Agent.
- `Connect Agent cannot set file permission` still says real failures reduce to insufficient NTFS privileges or missing same-ID / same-name target mappings for POSIX.
- Current job docs still keep permission-bearing profile choice in the creation flow rather than one generic late toggle.

That candor is useful.
The permission-metadata contract is the problem.
AnonSync should not clone a world where `sync permissions` still hides whether the honest answer is `fully applied`, `apply-with-conditions`, `preserve-only`, `rewrite locally`, or `blocked`.

## New documents in rev0303

- `958` Resilio permission metadata authority and principal-mapping fragmentation evaluation
- `959` Metadata authority contract sheet page
- `960` Permission sync review page
- `961` Principal mapping proof page
- `962` Permission failure review page
- `963` Metadata lineage receipt page

## Revision addendum — removal verbs, residue planes, and comeback-risk truth

This revision continues directly from `rev0300` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **disconnect, reconnect path drift, linked-device removal, disconnected-folder scope, placeholder-local revert, placeholder-global delete, power-user removal guards, hidden offline devices, and uninstall residue**.
2. Tightens the non-clone line again: borrow Resilio's candor that removal is multi-plane; refuse any contract where the operator still has to reconstruct which plane changed from scattered support prose.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio removal truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: removal contract sheet, removal intent disambiguation, device-local eviction boundary, identity-wide removal and remote remainder review, and removal lineage receipt.
5. Makes one hard product decision explicit: **remove-like verbs are typed operations** rather than one overloaded red affordance.
6. Makes another hard product decision explicit: **residue and survivors are part of the contract**.
7. Makes a third hard product decision explicit: **reconnect and comeback risk must preview before apply**.
8. Packages the result as another continuation archive whose new tranche makes the `typed-removal / survivor-boundary / residue-truth / comeback-risk / durable-receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present removal contract**

This time the reason is especially clear around **disconnect vs remove, placeholder-local vs placeholder-global delete, linked-identity scope vs outside peers, hide-vs-unlink, and uninstall residue**.
Current official materials simultaneously show that:

- `Disconnecting and Removing Folders` still says disconnect affects one device, while remove affects devices linked to the same identity and may still leave remote non-linked devices untouched.
- The same article still says reconnect can default to a different path and create a new indexed folder unless manually rebound.
- `Folder Types and Management` still says disconnected folders have no local path and removing them clears them from linked devices.
- `Selective Sync` still warns that removing a Selective Sync share removes placeholders from the local file system.
- `What Is an RSLS File?` still says `Remove from this device` is local placeholder reversion while deleting a placeholder with write authority can remove it from all peers.
- `Power user preferences` still publishes `disable_remove_from_all_devices` and `recreate_placeholders_on_removal`, proving that destructive remove and local placeholder behavior are separate policy levers.
- `How to clear offline devices?` still says hiding only hides and later reappearance is possible.
- `How to uninstall Sync?` still says uninstall can leave folders and `.sync/Archive` behind on desktop while removing synced files from iOS devices.

That candor is useful.
The removal contract is the problem.
AnonSync should not clone a world where the operator still has to remember which `remove` verb changed which plane.

## New documents in rev0301

- `946` Resilio removal verb taxonomy and residue-plane fragmentation evaluation
- `947` Removal contract sheet page
- `948` Removal intent disambiguation page
- `949` Device-local eviction boundary page
- `950` Identity-wide removal and remote remainder review page
- `951` Removal lineage receipt page

## Revision addendum — identity linking, certificate takeover, and unlink-boundary truth

This revision continues directly from `rev0299` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **identity certificates, M-key linking, all-folder inheritance, version-mixed linking risk, certificate takeover, Advanced-folder eviction, iOS delete risk, local-only unlink, and hidden offline devices**.
2. Tightens the non-clone line again: borrow Resilio's candor that seat linking is not ordinary low-risk pairing; refuse any contract where the operator still has to reconstruct seat adoption and folder fate from support prose.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio identity-link / seat-adoption truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: identity merge contract sheet, identity adoption review, certificate takeover impact page, unlink and hidden-device boundary page, and identity merge receipt.
5. Makes one hard product decision explicit: **identity linking is a reviewed seat-adoption operation** rather than a casual pairing affordance.
6. Makes another hard product decision explicit: **certificate takeover, share inheritance, and folder eviction must preview separately** rather than hiding behind one `Link device` action.
7. Makes a third hard product decision explicit: **hide is not unlink and offline residue is not revocation**.
8. Packages the result as another continuation archive whose new tranche makes the `seat-adoption / takeover / unlink boundary / latent residue / durable receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present identity-link contract**

This time the reason is especially clear around **version-mixed linking, certificate takeover, Advanced-folder eviction, iOS deletion risk, local-only unlink, and hidden offline-device residue**.
Current official materials simultaneously show that:

- `Sync Private Identity & Linking My Devices` still says identity linking can cause one device to adopt another device's identity name, fingerprint, and configured shares.
- The same article still warns against linking v2 and v3 devices because license/share configuration can conflict.
- The same article still warns that linking two already-running devices can cause one to lose its certificate, remove Advanced folders from the app, and on iOS remove them from the filesystem too.
- The same article still says you cannot remotely unlink other devices.
- `How to clear offline devices?` still says clear only hides a device and it can reappear if it comes back online.
- `What's the difference between Standard and Advanced folders?` still ties certificate-aware identity and `My Devices` semantics to Advanced folders.

That candor is useful.
The identity-link contract is the problem.
AnonSync should not clone a world where the operator still has to remember whether `link` means pairing, adoption, certificate replacement, or latent linked-device residue.

## New documents in rev0300

- `940` Resilio identity linking, certificate takeover, and seat-merge fragmentation evaluation
- `941` Identity merge contract sheet page
- `942` Identity adoption review page
- `943` Certificate takeover impact page
- `944` Unlink and hidden-device boundary page
- `945` Identity merge receipt page

## Revision addendum — transfer eligibility, pause truth, and context-gated movement clarity

This revision continues directly from `rev0298` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **pause semantics, scheduler zero windows, auto-sleep, battery saver, mobile-data policy, per-share forbidden-network rules, and background-priority side effects**.
2. Tightens the non-clone line again: borrow Resilio's candor that `paused`, `sleeping`, `forbidden network`, `battery stopped`, `Wi‑Fi only waiting`, and `global pause` are materially different truths; refuse any contract where the operator still has to reconstruct them from several help pages and settings planes.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio transfer-eligibility truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: transfer eligibility contract sheet, mobility and power budget review, paused-but-still-mutating page, transfer eligibility proof, and eligibility boundary receipt.
5. Makes one hard product decision explicit: **transfer eligibility is a first-class contract object**. `can move payload now`, `can still detect/index`, `sleeping`, `context-blocked`, and `runtime-stopped` are not interchangeable answers.
6. Makes another hard product decision explicit: **lane truth stays separate**. Payload movement, deletion propagation, zero-byte/structural publication, local detection, indexing, and peer visibility are different lanes and cannot be flattened into one `Paused` badge.
7. Makes a third hard product decision explicit: **policy gate and context gate remain separate truths**. `Wi‑Fi only` is not the same as `currently on cellular`; `custom network` is not the same as `currently forbidden network`; `battery policy` is not the same as `below threshold now`.
8. Packages the result as another continuation archive whose new tranche makes the `eligibility / gates / surviving mutation lanes / wake witness / proof ceiling / durable receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present transfer-eligibility contract**

This time the reason is especially clear around **pause semantics, scheduler zero-speed windows, auto-sleep, battery gating, mobile-data policy, and forbidden-network behavior**.
Current official materials simultaneously show that:

- `How to pause syncing` still says pause stops only bit transfers while zero-sized files and deletions still sync and new files are still rescanned and indexed.
- `Running Sync on schedule` still says scheduler `Paused` means download and upload speed are zero, but zero-sized files and deletions still sync, paused peers may still upload to non-paused peers, and rescans/indexing still continue.
- `Configuring Auto Sleep & Battery Saver (Android)` still says Auto Sleep can turn the core actually off when idle and wake periodically to check for changes, while Battery Saver can force Sync to stop below a chosen charge threshold.
- `Settings on mobile platforms` still says `Use mobile data` is a device-level gate and that disabling Android notifications lowers Sync priority enough that background work may stop.
- `Setting network interface per share` still says a share can be `Stopped. Forbidden network`, meaning it will not connect to peers for that share and new or updated files will not be detected.
- `Sync Preferences` still exposes global pause, scheduler, and bandwidth limits as separate settings planes.

That candor is useful.
The transfer-eligibility contract is the problem.
AnonSync should not clone a world where the operator still has to remember whether `paused` means `fully inert`, `payload blocked but indexing alive`, `sleeping until next wake`, `blocked by current network`, or `battery policy just forced the runtime down`.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful eligibility truths are real, but the present contract still hides too much meaning inside pause docs, scheduler docs, mobile settings, and power/network caveats instead of owning transfer eligibility as one stable page family.**

## New documents in rev0299

- `934` Resilio transfer eligibility, pause/schedule semantics, and context-gating fragmentation evaluation
- `935` Transfer eligibility contract sheet page
- `936` Mobility and power budget review page
- `937` Paused-but-still-mutating page
- `938` Transfer eligibility proof page
- `939` Eligibility boundary receipt page

## Revision addendum — stop truth, drain proof, and restart-boundary clarity

This revision continues directly from `rev0297` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **background/runtime continuity, Windows service execution, Android's explicit `Exit`, startup-on-boot posture, mobile background caveats, and stop-before-update / reopen chronology**.
2. Tightens the non-clone line again: borrow Resilio's candor that `closed`, `backgrounded`, `running as a service`, `start on boot`, and `exit` are materially different runtime truths; refuse any contract where the operator still has to reconstruct that from platform notes, settings, and update docs.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio stop/projection/runtime truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: runtime stop contract sheet, shutdown drain review, runtime stop proof, restart provenance page, and runtime stop receipt.
5. Makes one hard product decision explicit: **stop is a first-class contract object**. `close window`, `hide tray`, `background`, `service keeps running`, `pause`, and `full stop` are not interchangeable answers.
6. Makes another hard product decision explicit: **projection disappearance never equals runtime stop**. If bytes may still move, index, or publish, the product must say so plainly.
7. Makes a third hard product decision explicit: **saved stop intent, live runtime state, drain completion, and proven no-further-publication are separate truths**. The operator should not have to infer them from process folklore.
8. Packages the result as another continuation archive whose new tranche makes the `projection / runtime / drain / proof / restart-boundary / durable receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present stop/runtime contract**

This time the reason is especially clear around **service-background continuity, mobile background differences, explicit exit semantics, startup revival, and reopen chronology risk**.
Current official materials simultaneously show that:

- `Running Sync as a service on Windows` still says Sync can run automatically in the background regardless of whether a user is logged in, can run as `System`, `Local Service`, or current user, and can therefore keep syncing even when the ordinary interactive surface is gone.
- `Sync interface on Android` still gives `Exit` its own explicit verb and says it `shuts Sync down correctly`, which means ordinary navigation away from the surface is not the same thing as a true stop.
- `Does Sync work in background?` still says Android may keep working in the background unless killed by task killers or memory optimizers, while iOS background synchronization is unavailable; the same article also still says shutting down and reopening re-indexes folders and can change overwrite chronology after offline edits.
- `Settings on mobile platforms` still says disabling Android notifications lowers Sync's priority in the system and may force it to stop working in the background.
- `Sync Preferences` still exposes `Start Sync on startup`, so stop truth is not just about the current moment but also about automatic runtime revival at next boot.
- `Updating Sync to latest version` and related install/update docs still distinguish stopping the app, service, or process according to install mode rather than presenting one universal `quit` story.

That candor is useful.
The stop/runtime contract is the problem.
AnonSync should not clone a world where the operator still has to remember whether closing a surface, losing a notification, rebooting, hiding a tray icon, or leaving a service installed means bytes may still move.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful runtime truths are real, but the present contract still hides too much meaning inside service docs, mobile background caveats, startup settings, and update instructions instead of owning stop truth as one stable page family.**

## New documents in rev0298

- `928` Resilio stop proof, hidden runtime, and shutdown fragmentation evaluation
- `929` Runtime stop contract sheet page
- `930` Shutdown drain review page
- `931` Runtime stop proof page
- `932` Restart provenance page
- `933` Runtime stop receipt page

## Revision addendum — shared substrate, lock contention, and write-path boundary truth

This revision continues directly from `rev0296` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **SMB-share caveats, missing notifications on shared/networked paths, lock contention, Windows service namespace differences, mapped-drive invisibility, and power-user lock/detection settings**.
2. Tightens the non-clone line again: borrow Resilio's candor that storage substrate, runtime identity, and notification quality materially change the sync contract; refuse any contract where the operator still has to reconstruct that from SMB warnings, service troubleshooting, lock articles, and power-user timing tables.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio shared-storage truth is still too fragmented to clone even though the underlying distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: storage substrate contract sheet, shared substrate topology review, lock contention watch, mixed access boundary warning, and substrate lineage receipt.
5. Makes one hard product decision explicit: **storage substrate is a first-class contract object**. `local fs`, `network share`, `service-visible UNC`, and `mixed writer topology` are not one generic `folder` answer.
6. Makes another hard product decision explicit: **one synced subject gets one authoritative write-path contract**. Direct-on-host writers and SMB-mediated writers do not silently share one safe sentence.
7. Makes a third hard product decision explicit: **runtime identity and notification floor are public truths**. Service account, path namespace, event-vs-rescan detection, and lock-recheck cadence are not hidden implementation trivia.
8. Packages the result as another continuation archive whose new tranche makes the `storage class / runtime actor / authoritative path / contention grade / write-lane boundary / durable receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present shared-substrate contract**

This time the reason is especially clear around **SMB caveats, service namespace drift, lock contention, and mixed direct-plus-Samba writers**.
Current official materials simultaneously show that:

- `Sync and SMB file shares` still says Sync can work with SMB shares, but only with caveats: full permissions are required, only `SMB 3.0+` supports file-update notifications, stranded locks can remain after network/app failure, and simple Samba setups can damage or roll back files if third-party apps touch the same data outside SMB.
- `How soon does synchronization start?` still says filesystem notifications are the fast path, but some storages are not expected to support them correctly, explicitly including `NFS` and `SMB2` mounted shares, with scheduled scan every `600` seconds as fallback.
- `Locked files` still says another application can block Sync from transferring data, that the UI can list the blocked files, but that Sync still cannot identify which application holds the lock.
- `Power user preferences` still publishes both `enable_file_system_notifications` and `recheck_locked_files_interval`, keeping detection strength and lock retry posture as real tunable parts of the contract.
- `Sync Service Troubleshooting on Windows` still says mapped drive letters do not exist for the service because they are created on interactive logon, recommends UNC-style entry instead, warns that this loses update notifications so changes are discovered only on rescan or restart, and says switching the service to `Local System` creates a different storage folder / empty state that requires re-adding and re-sharing folders.

That candor is useful.
The shared-substrate contract is the problem.
AnonSync should not clone a world where the operator still has to remember whether the trustworthy path is the interactive alias, the service-visible UNC path, the host-local path that bypasses SMB semantics, or the lane that silently degraded change detection to rescans.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful substrate truths are real, but the present contract still hides too much meaning inside SMB caveats, service troubleshooting, lock articles, and power-user settings instead of owning storage topology as one stable page family.**

## New documents in rev0297

- `922` Resilio shared substrate, lock contention, and path-namespace fragmentation evaluation
- `923` Storage substrate contract sheet page
- `924` Shared substrate topology review page
- `925` Lock contention watch page
- `926` Mixed access boundary warning page
- `927` Substrate lineage receipt page


## Revision addendum — contested repair, blocked intake, and survivor-set truth

This revision continues directly from `rev0295` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **conflict-file delete risk, read-only suspension, `Overwrite any changed files`, offline-writer precedence, manual archive restore, and restart-needed repair paths**.
2. Tightens the non-clone line again: borrow Resilio's candor that contested files really can be blocked, overwritten, restored, or preserved in parallel; refuse any contract where the operator still has to reconstruct the safe repair path from six help-center articles and a pile of side effects.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio contested-file repair truth is still too fragmented to clone even though the underlying distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: contested object contract sheet, repair path review, survivor set page, live repair approval, and repair lineage receipt.
5. Makes one hard product decision explicit: **contest is a first-class object**. `blocked`, `parallel-survivor`, `overwrite-candidate`, `local-only residue`, and `archived loser` are not one generic `conflict` badge.
6. Makes another hard product decision explicit: **repair preview owns loser fate before apply**. The operator must know what stays live, what survives side-by-side, what falls to archive, and what remains local-only.
7. Makes a third hard product decision explicit: **live repair is its own approval barrier**. Restoring, overwriting, or resuming contested bytes into the live line is not a casual row action.
8. Packages the result as another continuation archive whose new tranche makes the `contest basis / chosen repair path / survivor set / live mutation scope / durable receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present contested-repair contract**

This time the reason is especially clear around **read-only suspension, offline-writer precedence, archive replay, and conflict-file delete risk**.
Current official materials simultaneously show that:

- `Conflict files in Sync` still says `.Conflict` items can come from case, encoding, invalid-symbol, link, or controller issues, and still warns not to just delete a `.Conflict` item because it corresponds to the real file or folder on a remote peer.
- `User Management` still says that if a Read Only peer modifies or adds files, those changes do not propagate and further synchronization of the changed files is suspended for that peer unless overwrite behavior is used.
- `Is one-way synchronization possible?` still spells out the per-class fate when `Overwrite any changed files` is enabled: renamed files stay while the old name is re-downloaded, deleted files are restored, edited files revert to the most recent RW version, and added files remain local-only and unsynced.
- `What if several people make changes to the same file?` still says an offline edit that comes back online can outrank later online edits, and that overwritten versions are placed in Archive.
- `Using Archive for file versioning and restoring deleted files` still says only manual restoring is possible, Sync must be running while restoring if you want replay rather than re-archiving, Archive does not record which peer made the change, and old versions arrive on other peers rather than the peer that made the change.
- `My files don't sync` still says that when a destination Read Only peer has changed files locally, the repair step is to enable `Overwrite any changed` on that RO peer and restart Sync there.

That candor is useful.
The contested-repair contract is the problem.
AnonSync should not clone a world where the operator still has to remember whether the safe move is to keep a parallel survivor, enable overwrite, restore from Archive while runtime is live, or avoid deleting a named conflict twin.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful contested-file truths are real, but the present repair contract still hides too much meaning inside conflict naming, read-only caveats, archive ritual, restart steps, and chronology notes instead of owning contested repair as one stable page family.**

## New documents in rev0296

- `916` Resilio contested repair, read-only suspension, offline precedence, and archive ritual fragmentation evaluation
- `917` Contested object contract sheet page
- `918` Repair path review page
- `919` Survivor set page
- `920` Live repair approval page
- `921` Repair lineage receipt page

## Latest addendum — activation latency, proof-of-effect, and non-retroactivity truth after rev0294

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **one ordinary `I changed it` answer still depends too much on separate planes such as change notifications, periodic rescan cadence, manual rescan, restart-required toggles, hidden storage files, and power-user timing defaults**
- **`saved`, `runtime reread`, `live for future work`, and `historically corrected` are still real different truths, but current Resilio mostly leaves the operator to reconstruct that classification**
- **non-retroactivity is documented, but it still too often lives as an article caveat rather than as one owned review boundary**
- **pending effect is still easy to over-read as success when the real truth is only `staged`, `waiting on trigger`, or `proof missing`**

Hard decisions made in this tranche:

1. **Saved-state, live-state, and proven-effect are different first-class truths.**
2. **Every meaningful change declares an activation class.** `immediate`, `next-reread`, `next-rescan`, `next-restart`, `next-startup`, `external-proof-needed`, and `future-only` are public product state.
3. **Retroactivity is explicit.** A future-only rule never silently impersonates historical correction.
4. **Pending effect gets its own watch surface.** Operators should be able to inspect what is merely staged, what is live, and what proof has gone stale.
5. **Receipts preserve route and proof class.** Later operators must know how a change entered, what made it live, and where the claim stops.

That yields five more ordinary product-owned pages:

- **Effect activation contract sheet page**
- **Activation latency review page**
- **Pending effect watch page**
- **Policy effect verification page**
- **Activation lineage receipt page**

This tranche closes a real gap between the earlier detection / hidden-state / instrumentation work and the ordinary operator question `did this change merely save, actually become live, or truly change the world I care about yet?`


## Latest addendum — automatic ingress mutation, router-side-effect warnings, and port-lease truth after rev0293

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **automatic direct-connect assistance still depends too much on separate planes such as listening-port settings, UPnP/NAT-PMP requests, manual forwarding expectations, config-mode ownership, and speed-troubleshooting advice**
- **a local-looking `Use UPnP port mapping` control is still really a network-edge mutation request with audience-widening implications**
- **current Resilio docs are candid that some network equipment can mis-handle those packets, but that collateral warning still mostly lives as preferences prose instead of one owned workflow**
- **mapping truth is still too easy to over-read as `enabled` rather than `requested`, `observed`, `stale`, or `cleared`**

Hard decisions made in this tranche:

1. **Automatic port mapping is a reviewed network-edge mutation.** AnonSync will not present it as a harmless convenience toggle.
2. **Lease truth belongs to the product.** `enabled`, `requested`, `observed`, `stale`, and `cleared` are different first-class states.
3. **Ingress widening and helper dependence stay separate.** Direct inbound reach is not flattened into generic reachability.
4. **Router-side collateral risk stays adjacent to apply.** Infrastructure-facing caution is never buried in support prose.
5. **Ingress receipts preserve claim ceiling.** Later operators must know not only that directness improved, but whether that improvement depended on router mutation and how fresh the proof was.

That yields five more ordinary product-owned pages:

- **Ingress mutation contract sheet page**
- **Auto port-map review page**
- **Mapping lease watch page**
- **Router-side-effect warning page**
- **Ingress mutation receipt page**

This tranche closes a real gap between earlier route / exposure work and the ordinary operator question `did I just ask the network edge to open me up, what audience widened, and do I actually know whether that mapping is live or gone?`

## Latest addendum — name provenance, recipient-label issuance, and stale-alias residue after rev0290

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **one visible `name` answer still depends too much on separate planes such as disk basename, desktop-only custom UI alias, issuance-time link/QR label, and stale alias residue after disconnect**
- **issuance-time recipient labels still behave like artifact-local naming rather than canonical subject rename, but current Resilio mostly leaves that truth in tip-style prose**
- **disconnect can still leave a custom alias behind in the UI until explicit reset, which means residue can impersonate current truth unless the product names it honestly**

Hard decisions made in this tranche:

1. **Every visible serious label carries plane and audience provenance.** A naked label is not enough.
2. **Issuance-time recipient labels are first-class artifacts.** They never silently mutate canonical subject history.
3. **Disconnect leaves residue, not truth.** A surviving local alias after continuity break must declare itself stale or residue.
4. **Name mutation preview is explicit.** Canonical retitle, local alias edit, disk rename, and recipient-label issuance are different verbs.
5. **Naming receipts preserve untouched planes.** Later operators must know not only what changed, but what definitely did not.

That yields five more ordinary product-owned pages:

- **Naming provenance sheet page**
- **Name mutation preview page**
- **Recipient-label issuance page**
- **Alias drift watch page**
- **Name lineage receipt page**

This tranche closes a real gap between the earlier general name-plane doctrine and the ordinary operator question `what is this actually called right now, to whom, and which older labels are still out there after I rename or disconnect things?`

## Latest addendum — effective policy provenance, sticky overrides, and config-plane ownership after rev0289

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **effective policy answers still depend too much on separate planes such as per-share preferences, standing defaults, linked-device defaults, and startup configuration**
- **`return to default` can still fail to mean true rejoin, because current Resilio documents at least one sticky override behavior that stops inheriting later changes even after appearing neutral again**
- **config-plane ownership is real but still too easy to miss when configured shares override earlier WebUI additions and suppress that UI path**

Hard decisions made in this tranche:

1. **Every effective policy field carries provenance.** AnonSync never shows resolved value without origin plane.
2. **`Return to default` means true inheritance rejoin.** AnonSync will not preserve a hidden dormant override behind a neutral label.
3. **Config-plane ownership stays visible.** A config-owned subject cannot pretend that the current UI is the source of truth.
4. **Policy edits preview plane and blast radius.** Share-local change, cohort-default change, future-arrivals default change, and config change are different verbs.
5. **Drift is a first-class object.** Exceptions, legacy overrides, and policy forks get their own review surface and durable receipt.

That yields five more ordinary product-owned pages:

- **Effective policy sheet page**
- **Policy change preview page**
- **Inheritance return review page**
- **Policy drift watch page**
- **Policy provenance receipt page**

This tranche closes a real gap between earlier residency / authority work and the ordinary operator question `what is actually governing this thing right now, who set it, and did my reset really put it back under the parent rule?`.

## Latest addendum — authority policy, delegation boundaries, and retained-material revocation truth after rev0288

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **permission answers still depend too much on folder family, identity family, and derivative-share class**
- **changing authority is still sometimes a live policy edit and sometimes a reissue / reconnect event, and current Resilio makes the operator remember which is which**
- **revocation still mostly means future-update cutoff plus retained local bytes, not clean erasure**

Hard decisions made in this tranche:

1. **Authority policy is a first-class object.** AnonSync never makes the operator infer the live contract from artifact family alone.
2. **Live mutation and reissue are different verbs.** A permission change preview must say whether the result comes from editing policy, issuing a successor, reconnecting, or merely lowering a derivative.
3. **Revocation always publishes retained-material truth.** `Future updates stop` and `already-held bytes remain` stay adjacent.
4. **Own-seat linkage and granted external rights stay separate.** `Add my own seat` is never flattened into `grant another principal authority`.
5. **Derivative seats can only narrow, never silently widen.** Local or downstream derivatives must publish source ceiling, current floor, and auto-lowering triggers.

That yields five more ordinary product-owned pages:

- **Authority contract page**
- **Permission change preview page**
- **Delegation boundary review page**
- **Revocation impact page**
- **Authority policy receipt page**

This tranche closes a real gap between the earlier artifact/intake work and the ordinary question `what authority is really live here right now, how can it change, and what still remains after I cut it off?`.

## Latest addendum — artifact-family truth, intake inspection, and epoch-fork warning after rev0287

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **current Resilio still treats artifact family as real semantics, which is good**
- **too much of that meaning still lives inside opaque tokens, browser wrappers, and article archaeology, which is not good enough to clone**
- **key rotation still behaves like epoch fork truth, not a harmless refresh**

Hard decisions made in this tranche:

1. **Artifact family must be inspectable before use.** A token is never its own explanation.
2. **Seat-link and subject-access artifacts stay separate.** AnonSync never flattens `join this seat family` into `join this subject`.
3. **Carrier never owns semantics.** QR, browser-open, paste, and local handoff are delivery lanes; the inspected artifact object owns the meaning.
4. **Rotation is an epoch event.** Successor issuance must preview surviving old cohorts and retirement order.
5. **Issuance and intake both emit receipts.** Later operators should not need token folklore to reconstruct what was issued or accepted.

That yields five more ordinary product-owned pages:

- **Capability artifact page**
- **Issuance preview page**
- **Incoming artifact intake page**
- **Artifact rotation / fork warning page**
- **Artifact issuance receipt page**

This tranche closes a real gap between earlier join/approval doctrine and the actual authority object that crosses the wire.


## Latest addendum — priority semantics, residency promises, and ghost-risk truth after rev0286

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **queue order and local-presence promise are still different truths in current Resilio**
- **manual `priority` override still freezes inheritance in a surprising way instead of returning cleanly to default semantics**
- **placeholder visibility, subtree auto-hydration, remove semantics, and no-source ghost risk still have to be reconstructed from several pages**

Hard decisions made in this tranche:

1. **Priority is never a residency guarantee.** `First in queue` and `will definitely be local` are different product objects.
2. **Neutral means inherit again.** AnonSync does not preserve a sticky hidden local priority contract after the operator returns to the neutral/default state.
3. **Residency promises get typed guarantee classes.** At minimum: `preview-only`, `queued-best-effort`, `guaranteed-local-now`, and `guaranteed-local-for-future-descendants`.
4. **Queue admission must publish source-witness truth.** A pending hydration cannot sound strong when the product already knows the full-copy witness is singular, offline, or absent.
5. **Receipts must preserve the promise ceiling.** A receipt may prove that a subject was queued, budgeted, or guaranteed; it may not let later operators confuse those classes.

That yields five more ordinary product-owned pages:

- **Residency intent page**
- **Residency policy review page**
- **Residency budget page**
- **Hydration queue admission page**
- **Residency promise receipt page**


## Latest addendum — trust bootstrap, rescue-first export, and one-shot destructive execution after rev0285

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **dangerous browser/service control still sprawls across install docs, WebUI docs, browser-warning docs, and per-surface settings**
- **`Approve after export` is not honest enough unless export itself becomes a first-class reviewed object and receipt**
- **destructive approval should never survive as sticky remembered browser consent**

Hard decisions made in this tranche:

1. **Bootstrap trust exception never unlocks destructive commit.** Observation and review may continue; destructive approval and execution stay blocked.
2. **Dangerous workflows keep one persistent context capsule.** Endpoint, acting seat, trust grade, basis freshness, at-risk counts, and best rescue rung must travel together.
3. **Pre-destructive preservation gets its own page and receipt.** `Export residue` is a real salvage object, not an afterthought.
4. **Final destructive authority becomes a one-shot execution ticket.** Endpoint drift, trust drift, seat drift, loss-row drift, or salvage invalidation expires it.
5. **Receipts must preserve the difference between side survival and same-line recovery.** Exported residue proves preservation, not full restoration.

That yields five more ordinary product-owned pages and component families:

- **Danger session capsule and persistent review-context rail**
- **Trust bootstrap review page**
- **Salvage export page**
- **Salvage export receipt page**
- **Destructive execution ticket page**


## Latest addendum — Resilio product-line split, destructive review shells, and local-web danger truth after rev0284

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **the current official Resilio operator contract is split not just by feature, but by product line**
- **destructive actions still live too close to preferences and too far from reviewed loss/salvage objects**
- **local web is real and worth borrowing, but danger actions still need a stronger trust-and-scope contract than WebUI folklore**

Hard decisions made in this tranche:

1. **AnonSync stays local-web-first.** Linux/service/WebUI reality is not a side surface; it is a primary projection.
2. **AnonSync will not clone Resilio's product-line split as the primary conceptual model.** Personal, business, and enterprise capability differences may exist, but the operator-facing semantics for destructive review, custody, and receipts must remain one grammar.
3. **Every destructive heal, source-authoritative reset, or overwrite approval goes through a reviewed barrier.** No ordinary preference toggle, advanced setting, or row-menu shortcut may stand in for that barrier.
4. **Every danger surface must carry endpoint identity, auth posture, listener scope, acting seat, capability, loss classes, salvage ladder, and claim ceiling on one page family.**
5. **Browser-trust exceptions are bootstrap details, not the control contract.** AnonSync may support trust bootstrap, but it must not teach `just proceed anyway` as the durable mental model for authority-bearing control.

## Latest addendum — maintenance mutation budgets, suspended continuity, and overwrite-proof local work after rev0281

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **maintenance mutation budget / maintenance mutation review / maintenance mutation ledger / maintenance mutation receipt**

Current official Resilio docs still admit that a narrow or backup-like seat is not one clean `safe local work` class: `User Management` still says a Read Only peer that modifies files or adds new ones will not propagate those changes and that further synchronization of the changed files will be suspended for that peer; `Folder Preferences` still says `Overwrite any changed files` on Read Only shares overwrites local changes, including files the operator added, and warns that the option is potentially destructive, while also saying the option is disabled for Read-only folders with Selective Sync ON; `Encrypted folders` still says encrypted backup nodes are Read Only, always have `Overwrite any changed files` activated, and do not allow Selective Sync; `How to Back up data (Android only)` still says backup intentionally preserves copies even after later deletion on the phone and that the desktop side has read-only access so changes do not sync back; `Sync Interface on iOS devices` still says `Remove from this device` disconnects only on that iOS device and removes files there while preserving them on others; and the live v3 line still runs through `3.1.2.1076`.

So the tighter non-clone line is:

> borrow Resilio's candor that maintenance-local work can survive, suspend, strand itself, or be overwritten depending on posture, but refuse any product contract where the operator still has to remember those fates from several docs before touching the files.

That yields four more ordinary product-owned pages:

- **Maintenance mutation budget page**
- **Maintenance mutation review page**
- **Maintenance mutation ledger page**
- **Maintenance mutation receipt page**

## Latest addendum — maintenance intent, hold-class semantics, and non-overloaded quiet contracts after rev0280

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **maintenance intent / maintenance semantics review / maintenance transition plan / maintenance contract receipt**

Current official Resilio docs still admit that `slow down or stop for a while` is not one clean semantic class: `How to pause syncing` still says pause stops only bits transfer while zero-sized files and deletions still sync and new files are rescanned and indexed; `Running Sync on schedule` still says scheduled `Paused` is only a speed-zero posture, still preserves those residuals, and can still let paused peers upload to non-paused peers while not downloading themselves; `Is one-way synchronization possible?` still says Read Only permission gives one-way sync where changes made in the read-only folder do not sync back; `How to Back up data (Android only)` still says backup intentionally preserves copies and that the desktop side has read-only access so changes do not sync back; and the live v3 line still runs through `3.1.2.1076`.

So the tighter non-clone line is:

> borrow Resilio's candor that pause, speed-zero schedule, read-only sync, and backup are different motion contracts, but refuse any product contract where the operator still has to remember which feature means transfer silence, preservation, writeback quiet, or destructive-safety.

That yields four more ordinary product-owned pages:

- **Maintenance intent page**
- **Maintenance semantics review page**
- **Maintenance transition plan page**
- **Maintenance contract receipt page**

## Latest addendum — backlog release shape, cap-return cliffs, and post-quiet order truth after rev0279

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **backlog release plan / backlog order review / backlog release timeline / backlog release receipt**

Current official Resilio docs still admit that leaving quiet is not one clean `resume`: `Running Sync on schedule` still says empty cells mean full bandwidth available, unchecked upload or download means full bandwidth for that direction, and scheduled `Paused` still keeps certain residual behaviors alive; `File download priority` still says per-share and global priority can both shape order, that manual share priority stops inheriting later global changes even if later set back to `None`, that only up to 50,000 active files are prioritized, that higher-priority arrivals suspend lower-priority work with some internal exceptions, that non-splittable files do not fully obey strict prioritization, and that the visible UI queue may still look alphabetical rather than actual execution order; `Power user preferences` still publishes `folder_defaults.transfer_priority`; and the live v3 line still runs through `3.1.2.1076`.

So the tighter non-clone line is:

> borrow Resilio's candor that quiet expiry, cap return, and queue ordering are different truths, but refuse any product contract where the operator still has to splice schedule prose, priority rules, queue caps, and visible-list caveats just to predict the post-quiet catch-up blast.

That yields four more ordinary product-owned pages:

- **Backlog release plan page**
- **Backlog order review page**
- **Backlog release timeline page**
- **Backlog release receipt page**


## Latest addendum — allowed residuals, quiet challenges, and break-vs-expected classification after rev0278

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **quiet event / residual allowance review / quiet challenge ledger / residual classification receipt**

Current official Resilio docs still admit that `pause` and scheduled `Paused` do not end all motion: `How to pause syncing` still says zero-sized files and deletions still sync and new files are rescanned and indexed so share size increases; `Running Sync on schedule` still says scheduled `Paused` leaves those same residuals alive and can still let paused peers upload to non-paused peers while not downloading themselves; `Sync Preferences` still presents Global Pause / Resume and Scheduler as ordinary local controls rather than a later challenge-classification object; the still-published historical change log still records `Sync stopping indexing if folder paused`; and the live v3 line still runs through `3.1.2.1076`.

So the tighter non-clone line is:

> borrow Resilio's candor that specific motion can survive `pause`, but refuse any product contract where the operator still has to remember that residual matrix later just to decide whether a new event actually disproved the quiet claim.

That yields four more ordinary product-owned pages:

- **Quiet event page**
- **Residual allowance review page**
- **Quiet challenge ledger page**
- **Residual classification receipt page**

## Latest addendum — quiet cohorts, counterpart agreement, and local-vs-shared stillness after rev0276

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **quiet cohort page / quiet agreement review / quiet window request / quiet cohort receipt**

Current official Resilio docs still admit that pause controls are useful yet overwhelmingly local: `How to pause syncing` still says pause stops only bits download/upload while zero-sized files and deletions still sync and new files are still rescanned and indexed; that same article still says Global Pause affects all shares on the current device; `Sync Preferences` still presents Global Pause / Resume and Scheduler as ordinary neighboring local controls; `Running Sync on schedule` still says scheduled `Paused` means upload/download speed are zero while zero-sized files and deletions still sync, new files are rescanned and indexed, and paused peers may still upload to non-paused peers while not downloading themselves; the still-published historical change log still records `Sync stopping indexing if folder paused`; and the live v3 line still runs through `3.1.2.1076`.

So the tighter non-clone line is:

> borrow Resilio's candor that pause is partial and origin-bearing, but refuse any product contract where the operator still has to infer whether only one seat got quieter or the seats that matter actually matched a shared quiet window.

That yields four more ordinary product-owned pages:

- **Quiet cohort page**
- **Quiet agreement review page**
- **Quiet window request page**
- **Quiet cohort receipt page**

## Latest addendum — re-entry cases, dormancy truth, and stale-return safety after rev0275

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **re-entry case / dormancy timeline / stale-return review / re-entry receipt**

Current official Resilio docs still admit that not every comeback means ordinary healthy sync: `Does Sync work in background?` still says shutdown/re-open re-indexes folders and gives them a new modification time, and that offline updates can overwrite changes made by peers that remained online; `Sync Main View (Desktop)` still says offline peers are disconnected from the folder after 7 days; `Power user preferences` still names `peer_expiration_days` with default `7 (day)`; `How to clear offline devices? (desktop only)` still says hiding an offline device does not unlink it and that it will reappear if it later goes online; `"Time difference" error` still says chronology trust fails past 600 seconds and that mobile peers may show empty lists; `Cannot download files` still says some announced files are ghost files that nobody has anymore; and the live v3 line still runs through `3.1.2.1076`.
So the tighter non-clone line is:

> borrow Resilio's candor that stale return, hidden reappearance, expired-peer comeback, clock-invalid return, and ghost-announcement aftermath are different truths, but refuse any product contract where the operator still has to merge background notes, peer-aging settings, hidden-device behavior, clock warnings, and source-unavailable prose before deciding what exactly came back and how trustworthy it is.

That yields four more ordinary product-owned pages:

- **Re-entry case page**
- **Dormancy timeline page**
- **Stale-return review page**
- **Re-entry receipt page**

## Latest addendum — next-observation opportunity, duty windows, and late-claim honesty after rev0274

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **next observation opportunity / late-claim review / duty-cycle timeline / observation opportunity receipt**

Current official Resilio docs still admit that not every seat is supposed to notice changes continuously: `Does Sync work in background?` still says desktop hidden runtime remains active, Android can work in background but task killers can stop it, and iOS background synchronization is unavailable; `Configuring Auto Sleep & Battery Saver (Android)` still says Android may hibernate between wake intervals and wake every configured period, 30 minutes by default, while Battery Saver can stop Sync below a chosen threshold; `Settings on mobile platforms` still says Wi-Fi-only policy constrains transfer, and disabling Android notifications can lower Sync's priority so it may stop working in the background; `How soon does synchronization start?` and `Power user preferences` still keep periodic rescans as the fallback observation path; `Agent run out of system notify watchers` still says watcher exhaustion downgrades discovery to periodic or manual rescans; `Sync Service Troubleshooting on Windows` still says service-style UNC setups may lose file-update notifications; and the live v3 line still runs through `3.1.2.1076`.
So the tighter non-clone line is:

> borrow Resilio's candor that different seats earn different next chances to notice or act, but refuse any product contract where the operator still has to merge background rules, wake intervals, battery/network gates, watcher warnings, and rescan cadence before deciding whether `late` is even an honest word.

That yields four more ordinary product-owned pages:

- **Next observation opportunity page**
- **Late-claim review page**
- **Duty-cycle timeline page**
- **Observation opportunity receipt page**

## Latest addendum — route provenance, desired-vs-observed path truth, and switch-history honesty after rev0271

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **route posture / route evidence / route divergence review / route provenance receipt**

Current official Resilio docs still admit that helper posture and effective path are different truths: the current `What ports and protocols are used by Sync?` article still separates sync.conf discovery, tracker communication, direct TCP/UDP attempts, relay fallback, and LAN multicast; the current `What is a Relay Server?` article still says relay is a fallback and still ties relay use to a peer-list icon; the current `Folder Preferences` article still makes relay, tracker, LAN search, and predefined hosts per-folder posture; the current `Performance overview` article still exposes a protocol row in the peer-connection table; `Peers aren't connecting` still names blocked tracker, blocked relay, blocked listening port, and multiple NIC routing as distinct failure causes; `Download/upload speed is very slow` still says relay use can impair speed and still recommends direct-port mapping; and the live v3 line still runs through `3.1.2.1076`.
So the tighter non-clone line is:

> borrow Resilio's candor that discovery helpers, current path, and fallback causes are different route truths, but refuse any product contract where the operator still has to infer route provenance from a few toggles, one current icon, one current protocol row, and several help articles instead of reading one durable reviewed object.

That yields four more ordinary product-owned pages:

- **Route posture page**
- **Route evidence page**
- **Route divergence review page**
- **Route provenance receipt page**

## Latest addendum — capacity-isolation experiments, sidecar benchmarking, and tuning-cost truth after rev0269

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **measurement plan / sidecar benchmark run / performance hypothesis review / measurement receipt**

Current official Resilio docs still admit that raw network capacity and live Sync throughput are not the same thing: the current `Download/upload speed is very slow` article still names many-small-file workload, relay usage, asymmetrical peers, low-capacity hardware, security software delay, `disk_low_priority`, closed ports, predefined hosts, and all-peer log escalation; the current `How can I improve data transfer/sync speed?` article still prefers direct connections, same-LAN or VPN paths, predefined hosts, `rate_limit_local_peers false`, `lan_encrypt_data false`, and `disk_low_priority false`; the current `Power user preferences` article still publishes defaults for `rate_limit_local_peers` and `lan_encrypt_data`; the current `Some internal tasks are taking time to complete` article still says hashing, deduplication, merging, scanning, reading, writing, and transfer are distinct hidden operations; `Measuring network performance with iperf3` still says Sync should be shut down completely on both peers during the tests and still prescribes sequential forward/reverse TCP and UDP rows; and the live v3 line still runs through `3.1.2.1076`.
So the tighter non-clone line is:

> borrow Resilio's candor that route class, workload shape, hidden internal work, and raw path capacity are different performance truths, but refuse any product contract where the operator still has to stop Sync, run an external benchmark, and mentally splice the result back into troubleshooting prose and power-user settings instead of reading one durable experiment object.

That yields four more ordinary product-owned pages:

- **Measurement plan page**
- **Sidecar benchmark run page**
- **Performance hypothesis review page**
- **Measurement receipt page**

## Latest addendum — instrumentation posture, restart truth, and baseline return after rev0268

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **instrumentation plan / instrumentation change review / instrumentation restore review / instrumentation posture receipt**

Current official Resilio docs still admit that evidence often starts with runtime posture changes: the current `Collecting debug logs automatically` and `Collecting debug logs manually` guides still say operators may enable debug logging in settings or by creating `debug.txt` with `FFFFFFFF`, then restart Sync to ensure logging is enabled and collect at least 15 minutes after reproduction; the current `Collecting debug logs manually` guide still says operators with many files should consider increasing log size; the current `Increasing Debug Log size` guide still says default rotation is `100 Mbytes`, that `sync.log` is backed up to `sync.log.old`, that operators should raise `log_size` to `200` or more and restart, and that older Linux/NAS versions may still require editing `settings.dat`; the current `Power user preferences` article still lists `log_size 100 (MB)`, `log_ttl 7 (day)`, and `profiler_enabled false`, and still says `profiler_enabled` writes `profiler.dat`, rotates every 10 minutes, and requires restart to activate; and the live v3 line still runs through `3.1.2.1076`.
So the tighter non-clone line is:

> borrow Resilio's candor that good evidence may require temporary posture changes, but refuse any product contract where the operator still has to remember those deltas from support prose, advanced settings, hidden files, and restart ritual instead of reading one durable object with baseline, active delta, and restoration truth.

That yields four more ordinary product-owned pages:

- **Instrumentation plan page**
- **Instrumentation change review page**
- **Instrumentation restore review page**
- **Instrumentation posture receipt page**

## Latest addendum — raw-artifact intake, normalization lineage, and packet-assembly truth after rev0267

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **raw evidence intake / artifact normalization review / packet assembly review / intake normalization receipt**

Current official Resilio docs still admit that raw evidence arrives in heterogeneous shapes: the current `Collecting debug logs manually` guide still names `sync.log` and rotated zip logs and still varies the storage root by platform, service account, package mode, and config mode; the current `How to collect logs on NAS manually?` guide still tells the operator to copy the whole Sync internal-data folder and then clean it up, leaving only `*.log`, `*.log.zip`, and `*.journal`; the current `Collect debug logs on mobiles` guide still routes harvest through `SNC.DBG.LOGS` and the hidden `.synclogs` folder; current crash/core-dump guides still spread dump shapes and paths across `.dmp`, crash-report folders, and gzipped cores; and the live v3 line still runs through `3.1.2.1076`.
So the tighter non-clone line is:

> borrow Resilio's candor that raw evidence is path-specific and messy, but refuse any product contract where the operator still has to scavenge, prune, rename, move, and repack those artifacts by hand without one durable intake object that preserves provenance from raw harvest to reviewed packet.

That yields four more ordinary product-owned pages:

- **Raw evidence intake page**
- **Artifact normalization review page**
- **Packet assembly review page**
- **Intake normalization receipt page**

## Latest addendum — recipient asks, return binding, and fulfillment truth after rev0266

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **recipient ask / ask fulfillment review / return lane review / ask fulfillment receipt**

Current official Resilio docs still admit that follow-up asks change what the operator now owes: the current `Collecting debug logs automatically` guide still says to indicate which support ticket the logs refer to plus role, timestamp, detailed description, and affected shares/files; the current `Collecting debug logs manually` guide still says to attach logs in reply to the support ticket, upload through the support portal, mention the forum link when redirected from Forums, and ask support for a larger upload link if attachments exceed 20 MB; current mobile and NAS collection guides still end in awkward manual return steps; and the live v3 line still runs through `3.1.2.1076`.
So the tighter non-clone line is:

> borrow Resilio's candor that follow-up asks have binding tokens, lane limits, and artifact-specific return shapes, but refuse any product contract where the operator still has to reconstruct `what was asked for`, `how to bind the answer back`, and `what still remains open` from ticket prose, forum links, and portal ritual.

That yields four more ordinary product-owned pages:

- **Recipient ask page**
- **Ask fulfillment review page**
- **Return lane review page**
- **Ask fulfillment receipt page**

## Latest addendum — companion cases, audience splits, and public/private continuity after rev0265

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **companion case / public summary review / private companion linkage / companion-case receipt**

Current official Resilio docs still admit that discussion and evidence do not always belong in the same lane: `I still have questions, where can I get answers?` still sends users toward the forum while also saying they can contact support, with PRO users first to get response and FREE users answered to the extent possible; the current automatic-log guide still tells the operator to indicate in feedback text which support ticket the logs refer to plus role, timestamp, detailed description, and affected shares/files; the current manual-log guide still says that if the operator was redirected there from Forums they should mention the forum link when sending logs through the support web portal; and the live v3 line still runs through `3.1.2.1076`.
So the tighter non-clone line is:

> borrow Resilio's candor that public discussion, private evidence, and other support routes are different audience situations, but refuse any product contract where the operator still has to tie forum links, ticket numbers, and private packets together by hand instead of reopening one durable companion-case object.

That yields four more ordinary product-owned pages:

- **Companion case page**
- **Public summary review page**
- **Private companion linkage page**
- **Companion-case receipt page**

## Latest addendum — escalation lanes, destination truth, and response-ceiling honesty after rev0264

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **escalation lane / escalation review / destination confirmation / escalation lane receipt**

Current official Resilio docs still admit that route, entitlement, and audience differ: current log/crash/dump guides still say technical support is available exclusively for Resilio Sync Business customers, while Sync v3 functionality questions should go to the community forum and Help Center and payments/licensing should use a web form; the current automatic-log guide still tells the operator to use an in-app `Contact support` form; `I still have questions, where can I get answers?` still says users can also contact support and that PRO users are first to get response while FREE users may be answered to the extent possible; `Licensing in Resilio Sync 3.0` still says Business licenses are not compatible with Sync v3 and commercial users should continue using Sync v2 or explore business solutions; and the live v3 line still runs through `3.1.2.1076`.
So the tighter non-clone line is:

> borrow Resilio's candor that support lanes, entitlement, and audience really differ, but refuse any product contract where the operator still has to reconcile forum/help-center self-service, Biz-only technical-support language, billing web forms, and in-product `Contact support` affordances without one product-owned lane contract.

That yields four more ordinary product-owned pages:

- **Escalation lane page**
- **Escalation review page**
- **Destination confirmation page**
- **Escalation lane receipt page**

## Latest addendum — incident brief, symptom bookmarks, and coordinated capture runs after rev0262

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **incident brief / symptom bookmark / coordinated capture run / capture brief receipt**

Current official Resilio docs still admit that artifacts need event context: the current `Collecting debug logs automatically` guide still says to reproduce the issue, let Sync collect logs for at least 15 minutes, and explain in feedback text the peer role, problem timestamp, detailed description, and affected shares/files; that same guide still says not to close the application/device until sending is confirmed complete; the current `Collecting debug logs manually` guide still says to describe the issue and mention the forum link when redirected from Forums; and the live v3 line still runs through `3.1.2.1076`.
So the tighter non-clone line is:

> borrow Resilio's candor that logs need event context and a real capture window, but refuse any product contract where the operator still has to type the case brief into prose and remember whether the reproduction run actually caught the target symptom inside a usable evidence window.

That yields four more ordinary product-owned pages:

- **Incident brief page**
- **Symptom bookmark page**
- **Coordinated capture run**
- **Capture brief receipt**

## Latest addendum — witness-set scope, peer-role annotation, and evidence completeness after rev0261

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **incident witness set / witness request / witness completeness review / witness-set receipt**

Current official Resilio docs still admit that evidence scope changes by incident class: the current `Peers aren't connecting` article still asks for logs from two peers that cannot connect; the current `My files don't sync` and `How can I improve data transfer/sync speed?` articles still say to collect logs from all peers if the issue persists; the current `Collecting debug logs automatically` guide still says the feedback text should explain that peer's role in the setup plus problem timestamps and affected shares/files; and the live v3 line still runs through `3.1.2.1076`.
So the tighter non-clone line is:

> borrow Resilio's candor that different incidents need different witness counts, but refuse any product contract where the operator still has to infer who owes evidence, narrate peer role in prose, and remember whether `two peers`, `all peers`, or a narrower witness sample was actually enough for this case.

That yields four more ordinary product-owned pages:

- **Incident witness set page**
- **Witness request page**
- **Witness completeness review**
- **Witness-set receipt**

## Latest addendum — incident-object absence, history search, and conclusion continuity after rev0260

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **diagnostic incident page / incident timeline / evidence sufficiency review / diagnostic conclusion receipt**

Current official Resilio docs still admit that diagnosis spans several surfaces: the current desktop main-view article still says History is its own 30-day activity lane and that `X of Y` opens peers; the current `My files don't sync` article still tells operators to click peers counts, click status warnings that often jump to KB explanations, search Sync History, open peers lists to inspect queues, and only later collect logs from all peers; the current `Locked files` article still says the row opens affected files but cannot identify the locking application; current debug-log guides still require enabled debug logging, restart, and at least 15 minutes of collection; and the live v3 line still runs through `3.1.2.1076`.
So the tighter non-clone line is:

> borrow Resilio's candor that diagnosis really does span rows, peers, history, queues, item lists, and heavier evidence capture, but refuse any product contract where the operator still has to remember the investigation as a mental story instead of reopening one durable case object that preserves what has been checked, what remains missing, and what conclusion is actually justified.

That yields four more ordinary product-owned pages:

- **Diagnostic incident page**
- **Incident timeline**
- **Evidence sufficiency review**
- **Diagnostic conclusion receipt**

## Latest addendum — status drill-in, KB handoff, and route-owned diagnosis after rev0259

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **status drilldown / diagnostic router / affected items / diagnostic route receipt**

Current official Resilio docs still say the desktop main view has status rows, peers counts, and 30-day history, but the ordinary troubleshooting path still spreads the next move across several separate surfaces. The current `My files don't sync` article still tells operators to click the `X of Y peers` link, click status warnings that often lead to KB explanations, inspect Sync History, open peers lists to inspect queued transfers, and only then work through a long checklist. The current `Locked files` article still says the error row opens a file list and lets you click to the file path, but also says Sync still cannot identify which application locked the files. The current v3 change log still records that `Can't download file` had to be fixed to be clickable at all.
So the tighter non-clone line is:

> borrow Resilio's candor that serious rows should be clickable and informative, but refuse any product contract where operators still reconstruct `what this row proves, what click should come next, whether that click opens meaning or affected items, and which route produced the final answer` by hopping across UI rows, help-center prose, history, peer lists, and queue views.

That yields four more ordinary product-owned pages:

- **Status drilldown**
- **Diagnostic router**
- **Affected items**
- **Diagnostic route receipt**

## Latest addendum — warning taxonomy, blocker scope, and least-strong repair after rev0258

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **warning page / blocker scope / recovery rung / warning history**

Current official Resilio docs are actually fairly candid that warnings are not one thing. The current `Core warnings` article still separates tracker/bootstrap trouble, low space on the default-folder-location disk, failed folder-list / identity sync, and license-management disablement. The current `Service files missing` article still says synchronization for that folder is suspended. The current `Some internal tasks are taking time to complete` article still says the condition can be intermittent and recoverable rather than a hard stall. The current `Time difference` article still says chronology trust is invalidated and mobile devices may show empty lists. The current `Cannot download files` article still says a tree may advertise files that no peer now holds as full bytes.
So the tighter non-clone line is:

> borrow Resilio's candor that warning classes differ, but refuse any product contract where operators still reconstruct `what kind of warning is this, how wide is it, what is the least-strong safe next rung, and what did acknowledgement really change` from one-off articles and troubleshooting lore.

That yields four more ordinary product-owned pages:

- **Warning page**
- **Blocker scope**
- **Recovery rung**
- **Warning history**

## Latest addendum — paused-label origin split and named-state matrix honesty after rev0257

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **state token posture / state token change review / state token evidence / state token receipt**

Current official Resilio docs still reuse the visible word `Paused` across manual pause, global pause, and scheduler surfaces, but the documented matrix is not one stable thing. The current `How to pause syncing` article still says pause stops only bits upload/download, while zero-sized files and deletions still sync and new files are still rescanned and indexed. The current `Running Sync on schedule` article still says scheduled `Paused` means upload/download speed are zero, yet a paused peer may still upload to non-paused peers while not downloading itself; that same article still says deletions sync anyway and indexing continues. `Sync Preferences` still presents Global Pause and Scheduler as ordinary nearby controls.
So the tighter non-clone line is:

> borrow Resilio's candor that pause is selective and origin-bearing, but refuse any product contract where one visible state word like `Paused` still hides origin-dependent signal matrices, delete-through, and indexing-through behavior.

That yields four more ordinary product-owned pages:

- **State token posture**
- **State token change review**
- **State token evidence**
- **State token receipt**

## Latest addendum — replay class, piece-shift fallback, and differential-lane ceiling after rev0256

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **replay class posture / replay cost review / replay evidence / replay receipt**

Current official Resilio docs still say files are split into pieces from `32 KB` to `2 MB`, that usually only changed pieces are transferred, but that if edits shift all pieces the whole file is re-synced; the same current FAQ still says Sync Business has diff-delta sync for that shifted-file case. Separate official Resilio documentation still says administrators may intentionally disable differential sync so the whole file is replayed, or keep it on and pay the local hash/recheck cost to send only changed pieces.
So the tighter non-clone line is:

> borrow Resilio's candor that replay cost is workload-shaped and policy-bearing, but refuse any product contract where operators still reconstruct `what replay class is active here, when edits will collapse to whole resend, and what stronger lane is unavailable` from FAQ prose and enterprise tuning pages.

That yields four more ordinary product-owned pages:

- **Replay class posture**
- **Replay cost review**
- **Replay evidence**
- **Replay receipt**

## Latest addendum — name-plane reset, stale outward labels, and residue-after-disconnect after rev0255

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **name posture / name change review / artifact label freshness / name receipt**

Current official Resilio docs still say a desktop share can have a custom UI name that does not rename the folder on disk and does not propagate to linked devices; the same current article still says a different custom name can be inserted while generating a sharing link or QR code; that sharing-time label still does not become the durable share name in preferences; QR output still needs regeneration after a label change; disconnect still preserves the custom UI name until explicit `Reset`; and current move/rename guidance still says renaming the synced folder affects only the local device.
So the tighter non-clone line is:

> borrow Resilio's candor that several name planes are real and useful, but refuse any product contract where operators still reconstruct `which name is local residue, which one is outward, and whether the visible artifact is stale under a later rename` from tips pages and memory.

That yields four more ordinary product-owned pages:

- **Name posture**
- **Name change review**
- **Artifact label freshness**
- **Name receipt**

## Latest addendum — mutable equality basis and same-file claim ceilings after rev0255

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **equality posture / candidate equivalence review / equality evidence / equivalence receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `what counts as the same file here?` can depend on:

- the pre-seeded quick equation still using creation timestamp, modification timestamp, size, and file permissions
- creation time still being removable from the equation by policy
- permission sync still being removable from the equation by policy
- the current file-properties reference still splitting properties into synchronized, optionally synchronized, and not synchronized by platform and version
- permission docs still allowing later application on compatible storage instead of native parity on the current seat
- troubleshooting docs still warning that xattr/stream narrowing can change bundle/object shape on mixed systems

So the tighter non-clone line is:

> borrow Resilio's candor that equality and `needs sync` are real, mutable product semantics, but refuse any product contract where `same file`, `up to date`, or `nothing to do` still require operators to reconstruct the effective compare plane from several documents.

That yields four more ordinary product-owned pages:

- **Equality posture**
- **Candidate equivalence review**
- **Equality evidence**
- **Equivalence receipt**


## Latest addendum — indirection objects, target non-transitivity, and junction-driven conflict fallout after rev0253

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **indirection posture / indirection action review / target transitivity proof / indirection receipt**

Current official Resilio docs still say Windows does not support soft links, hard links, symbolic links, or junctions in Sync and that using such links may lead to `.Conflict` files for each affected entry. Separate current docs still say Unix can synchronize symbolic links as links while target folders are not synchronized unless separately added. Separate current conflict guidance still names files or folders located in linked junctions as a direct cause of `.Conflict` artifacts.
That candor is useful.
The non-clone problem is still indirection ownership.

Ordinary operators can still be pushed into several official docs before the product fully owns these questions:

- whether the row is an ordinary file/folder or an indirection object
- whether the entry object itself is preserved, flattened, blocked, or likely to create conflict residue on this seat family
- whether target bytes are in scope now, out of scope now, or require separate admission
- whether following the target widens the graph beyond the current share contract
- what later receipt can prove the applied fidelity and transitivity verdict

AnonSync should therefore make **indirection posture** and **target transitivity proof** first-class product objects.
Every serious alias-edge path should render entry kind, platform lane, object fate, target scope, transitivity verdict, conflict hazard, safe substitution ladder, and receipt language before the product treats the row as just another ordinary file or folder.

## Latest addendum — identity-action verbs, subject-class fallout, and mobile byte-deletion asymmetry after rev0252

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **identity-action review / subject-fate matrix / preserve-before-identity-action / identity-action receipt**

Current official Resilio docs still say linking two already-running installs can make one device lose its certificate, remove Advanced folders from the app, and copy folders from the other instance; the same current linking docs still say iOS deletes those Advanced folders from the file system because of platform architecture. Separate current docs still say changing identity name requires unlinking and creating a new identity, removes Advanced folders from the instance, keeps Standard folders differently, and preserves folders in the system only excepting iOS and Windows Phone. Separate current uninstall guidance still says to unlink from identity first, then remove the remaining Standard shares, while uninstall on iOS and Windows Phone removes synced files from the device.
That candor is useful.
The non-clone problem is still identity-action ownership.

Ordinary operators can still be pushed into several official docs before the product fully owns these questions:

- whether an account-looking verb is also evicting some local subject classes from app governance
- whether local bytes stay on disk, disappear from the app only, or are deleted because of platform architecture
- whether Advanced and Standard subjects are surviving differently on this seat
- whether the safest next move is `unlink now`, `preserve first`, `branch first`, or `use another seat`
- what later receipt can prove about the fate of each local subject after the action

AnonSync should therefore make **identity-action review** and **subject-fate matrix** first-class product objects.
Every serious identity-changing action should render requested verb, affected subject classes, app-removal effect, local-byte survival by platform, preserve-first alternatives, and receipt language before the product treats identity work as mere account housekeeping.

## Latest addendum — hydration-engine split, shell/provider lane truth, and history/collision ceilings after rev0251

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **hydration-engine posture / hydration-mode change review / hydration evidence / hydration receipt**

Current official Resilio docs still say Selective Sync can mean classic `.rsl` placeholder arrival with later on-demand fetch, that removing a Selective Sync share removes placeholders from that device, that file-browser actions still depend on OS/file-system integration, and that the live Sync v3 line recently fixed missing context-menu items in Selective Sync shares on macOS. Separate current official Windows cloud-file docs still say Transparent Selective Sync is a different engine from legacy Selective Sync, that it requires specific Windows/API/path prerequisites, that v3.x and older do not retain ordinary file versions for TSS folders and only archive remote deletions there, that file-edit collision detection does not work there on those older lines, and that other local worlds such as OneDrive on-demand, a second agent, inherited Cloud API flags, or some VMware disk modes can distort or break the expected contract.
That candor is useful.
The non-clone problem is still hydration ownership.

Ordinary operators can still be pushed into several official docs before the product fully owns these questions:

- which hydration engine is actually active here
- which local actions are available because of daemon policy versus shell/provider integration health
- whether retained history is full, delete-only, narrowed, or absent for this engine/path
- whether file-edit collision detection still works here
- whether the current path is merely awkward or actually ineligible
- whether another provider/runtime is just present or actively invalidating the contract

AnonSync should therefore make **hydration-engine posture** and **hydration evidence** first-class product objects.
Every serious partial-materialization subject should render engine kind, lane health, eligibility basis, history guarantee, collision guarantee, co-tenant ceilings, and receipt language before the product treats `Selective Sync` or `online only` as self-explanatory.

## Latest addendum — permission-plane mode, reference authority, and inheritance rewrite after rev0250

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

## Latest addendum — hidden StreamsList locality, xattr courier stubs, and ignore-boundary split after rev0249

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

Current official Resilio docs still say every synced folder gets a hidden `.sync` directory that is critical for synchronization; `.sync/ID` is how Sync recognizes the same share on a device; deleting or corrupting `.sync` suspends sync; two Sync instances touching the same folder or the same external-drive storage can corrupt internal state; raw `Cloning Sync` is unsupported; and a current home-folder warning still says Sync's own storage folder with a `License` directory can contaminate whole-tree add attempts.
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

Current official Resilio docs still show a useful product, but they also still show that one ordinary answer to `what exactly changes if I protect this app or open this file in another app?` can still depend on:

- whether local protection hides the files from OS `Recents` / Files-app surfacing on iOS
- whether forgetting the local secret can create a reinstall-and-local-loss recovery cliff on a mobile family
- whether opening in another app is live provider editing or only copy-return / branch creation
- whether the platform can replace the original automatically or leaves old and new versions side by side
- whether local clearing, local-only data risk, and sandbox-shaped storage constraints live on a separate storage page

So the tighter non-clone line is:

> borrow Resilio's candor that mobile app protection, outside-app editing, and local recovery ceilings are real contracts, but refuse any product contract where a privacy toggle and an `Open in...` affordance still hide OS-visibility loss, copy-return edit semantics, duplicate-return risk, and reinstall-level recovery cliffs.

That yields four more ordinary product-owned pages:

- **Local protection**
- **Protection change review**
- **External edit lane**
- **Local protection receipt**

## Latest addendum — substrate truth, notify gaps, and mixed-writer hazard after rev0246

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **substrate posture / substrate admission review / mutation-channel evidence / substrate-risk receipt**

Current official Resilio docs still show a useful product, but they also still show that one ordinary answer to `is this connected share actually safe and prompt on this path?` can still depend on:

- whether the path is really local-native or a mounted/networked substrate
- whether file notifications work here or whether detection only falls back to scheduled rescans
- whether locks can be diagnosed in-product or only by external tooling and restart ritual
- whether the same bytes are being touched through unmanaged channels outside the share protocol
- whether the truthful sentence is `ordinary connected`, `degraded but usable`, or `unsafe mixed-writer topology`

So the tighter non-clone line is:

> borrow Resilio's candor that storage substrate matters, but refuse any product contract where a share can look ordinarily connected while notification gaps, lock uncertainty, or mixed-writer corruption risk are only visible in scattered help pages and advanced knobs.

That yields four more ordinary product-owned pages:

- **Substrate posture**
- **Substrate admission review**
- **Mutation-channel evidence**
- **Substrate-risk receipt**

## Latest addendum — backup-subject mode bypass, storage-only connected appearance, and subject-kind override after rev0245

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **subject-kind override / arrival-exception review / storage-only arrival posture / subject-kind override receipt**

Current official Resilio docs still show a useful product, but they also still show that one ordinary answer to `does this seat default still apply to this subject?` can still depend on:

- whether `Disconnected` / `Selective Sync` / `Synced` is being read as a universal linked-device arrival rule
- whether mobile backup is a storage-only subject that quietly outrides that default on destination desktops
- whether a connected-looking destination row is actually collaborative or only a read-only storage sink
- whether the desktop may write back at all or merely hold durable copies
- whether later operators must disconnect/reconnect just to restore the posture they thought the seat default already promised

So the tighter non-clone line is:

> borrow Resilio's candor that backup/storage-only subjects are real and that seat defaults can have carve-outs, but refuse any product contract where a subject kind can silently bypass the standing arrival mode and still look like an ordinary connected collaborative share.

That yields four more ordinary product-owned pages:

- **Subject-kind override**
- **Arrival-exception review**
- **Storage-only arrival posture**
- **Subject-kind override receipt**

## Latest addendum — linked-family owner default, self-observer detour, and seat-role proof after rev0244

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **seat role / self-narrowing review / relationship-versus-seat authority / seat-role receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `how do I make one of my own devices intentionally less authoritative than the rest?` can still depend on:

- whether linked-family membership silently gives the seat owner-grade power
- whether the narrower request can exist natively or only through Standard-folder substitution
- whether a Read Only key, disconnect step, and manual bind are standing in for one real seat-role change
- whether later operators are looking at the same subject lineage or a workaround copy that only serves the same material purpose
- whether the strongest safe sentence is `native observer seat`, `derived narrow seat`, or only `detour receive-only copy`

So the tighter non-clone line is:

> borrow Resilio's candor that linked-family convenience is useful and that one of your own devices may still need a narrower role, but refuse any product contract where linked devices default to `Owner` and a self-observer request still has to detour through Standard-folder substitution, Read Only keys, disconnect/manual bind ritual, and later archaeology about what the seat really is.

That yields four more ordinary product-owned pages:

- **Seat role**
- **Self-narrowing review**
- **Relationship-versus-seat authority**
- **Seat-role receipt**


## Latest addendum — non-authority local edits, destructive auto-heal, and path-local continuity after rev0243

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **non-authority edit posture / non-authority local-change review / affected-path continuity / non-authority edit receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `what happens if I edit locally on a non-authority copy?` can still depend on:

- whether this seat is merely forbidden to publish upstream or whether local edits also freeze future updates for touched paths
- whether `Overwrite any changed files` is off, optional, enabled, or forced by posture
- whether Selective Sync disables the overwrite option on a Read Only share
- whether encrypted/backup posture forces overwrite and forbids Selective Sync entirely
- whether local additions remain as unsynced residue while edits, deletes, or renames behave differently
- whether linked-device ownership semantics force a manual Read Only detour instead of one native seat-level non-authority posture

So the tighter non-clone line is:

> borrow Resilio's candor that non-authority local edits are a real policy surface, but refuse any product contract where one `Read Only` badge still has to cover frozen paths, destructive auto-heal, local-only residue, mode-specific option disappearance, and encrypted hardwiring.

That yields four more ordinary product-owned pages:

- **Non-authority edit posture**
- **Non-authority local-change review**
- **Affected-path continuity**
- **Non-authority edit receipt**


## Latest addendum — Archive toggle, replay dependence, and local recovery ceiling after rev0241

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **retention/replay dependence / archive-policy change review / local recovery ceiling / archive-policy receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `what exactly do I lose if I turn Archive off here?` can still depend on:

- whether `Use Archive` is being read as simple retention policy or as the thing that also preserves cheap rename/copy replay
- whether the current seat or surface can even access Archive locally on this platform/path class
- whether Android internal-memory limits or iOS no-access ceilings make local recovery weaker than the toggle name suggests
- whether some other seat still carries the real rollback witness after this local policy change
- whether later language should honestly say `retention shortened`, `local recovery narrowed`, or `remote rename/copy now re-download here`

So the tighter non-clone line is:

> borrow Resilio's candor that Archive affects both rollback and replay, but refuse any product contract where `Use Archive` still reads like a harmless preference while recovery locality, replay cost, and surface ceilings remain spread across several help pages.

That yields four more ordinary product-owned pages:

- **Retention/replay dependence**
- **Archive-policy change review**
- **Local recovery ceiling**
- **Archive-policy receipt**


## Latest addendum — timestamp-only winner rules, clock confidence, and loser-preservation proof after rev0240

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **same-path winner review / decision chronology evidence / losing-version fate / divergence-resolution receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `why is this version winning, and what happens to the loser?` can still depend on:

- whether same-path divergence came from pre-populated-folder comparison, offline return, ordinary live conflict, or Archive restore replay
- whether the current ranking is a strong content/authority verdict or only a `latest timestamp` / `latest file that comes online` rule
- whether peer clocks and time zones are trustworthy enough for chronology-sensitive overwrite at all
- whether the losing version survives in Archive, a branch, an export, or nowhere easy to inspect
- whether later `restored`, `newest`, or `winner` language is stronger than the proof that actually existed

So the tighter non-clone line is:

> borrow Resilio's candor that chronology, offline-return priority, and loser preservation are real, but refuse any product contract where timestamp order silently becomes winner authority and loser fate stays half-hidden in Archive folklore.

That yields four more ordinary product-owned pages:

- **Same-path winner review**
- **Decision chronology evidence**
- **Losing-version fate**
- **Divergence-resolution receipt**

## Latest addendum — safe reconnect, risky merge, and overloaded `Folder not empty` warnings after rev0239

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **same-lineage reconnect proof / non-empty target divergence review / preserve-before-adopt / reconnect-vs-merge receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `am I restoring the old tree or merging into a risky existing one?` can still depend on:

- whether the non-empty target is the actual remembered path or only a convenient same-name folder
- whether `Folder not empty` means harmless reconnect to a previously synced location or a materially risky merge into existing bytes
- whether Resilio is about to compare identical/local-only/remote-only/divergent material or only ask for generic confirmation
- whether local material that might be deleted or overwritten should first be preserved or copied aside
- whether later `connected` language really proves old-tree restoration or only reviewed guarded merge

So the tighter non-clone line is:

> borrow Resilio's candor that reconnect and pre-populated reuse are real, but refuse any product contract where the same `Folder not empty` / `Add anyway` warning still has to stand for both safe same-lineage reconnect and risky merge into existing bytes.

That yields four more ordinary product-owned pages:

- **Same-lineage reconnect proof**
- **Non-empty target divergence review**
- **Preserve-before-adopt**
- **Reconnect-vs-merge receipt**

## Latest addendum — manual-bind right, default-root scope, and duplicate-veto after rev0238

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **future-arrival defaults / bind choice review / existing-folder adoption review / arrival bind receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `how do I safely place this one incoming or reconnecting share?` can still depend on:

- whether the seat-wide linked-device default connect mode is being used as a proxy for one-share placement rights
- whether Android Simple Mode or default-folder policy is quietly auto-placing new shares and adding `(1)` on same-name collision
- whether reconnect is proposing the original path or a default path that may create a sibling duplicate
- whether an existing non-empty target is being adopted intentionally or only waved through with `Add anyway`
- whether choosing a custom location for one share forces an operator to mutate whole-seat posture first

So the tighter non-clone line is:

> borrow Resilio's candor that defaults, suggested roots, reconnects, and existing local material are real, but refuse any product contract where one-share bind safety still depends on changing whole-device mode or accepting duplicate-suffix folklore.

That yields four more ordinary product-owned pages:

- **Future-arrival defaults**
- **Bind choice review**
- **Existing-folder adoption review**
- **Arrival bind receipt**

## Latest addendum — current-share posture, future-default meaning, and clear/disconnect return contract after rev0237

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **current sync mode / sync mode change review / clear-versus-disconnect review / sync mode receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `what does this mode actually mean on this seat?` can depend on:

- whether the current statement is about one already-present share or about the seat's **future default connect mode**
- whether the current subject has names only, placeholders, or full local bytes
- whether `Clear` is a local placeholder reversion while `Disconnect` preserves filesystem material and changes the return path
- whether reconnect will propose the original path or a default path that can create a `(1)` duplicate
- whether Simple Mode or default-folder settings are quietly choosing the path basis for new arrivals

So the tighter non-clone line is:

> borrow Resilio's candor that sync modes are useful operator concepts, but refuse any product contract where one mode chip still has to carry current-share posture, future-arrival default, byte materialization, path basis, and return contract at once.

That yields four more ordinary product-owned pages:

- **Current sync mode**
- **Sync mode change review**
- **Clear-versus-disconnect review**
- **Sync mode receipt**

## Latest addendum — rule-agreement truth and ignore-ledger shared meaning after rev0236

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **rule agreement / drift-class review / rule retroactivity / rule agreement receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `do these peers actually mean the same thing by ignored?` can depend on:

- whether matching IgnoreLists are merely `advisable` or actually required for shared agreement
- whether the rule is only local indexing/accounting or a shared exclusion contract
- whether path/case semantics differ by operating system
- whether the rule affects only future intake rather than already-synced material
- whether structural information is still carried until disconnect even when payloads are ignored

So the tighter non-clone line is:

> borrow Resilio's candor that ignore rules have real indexing, accounting, and retroactivity semantics, but refuse any product contract where operators still have to infer whether rule drift is harmless local variance or unsafe shared-meaning disagreement.

That yields four more ordinary product-owned pages:

- **Rule agreement**
- **Drift-class review**
- **Rule retroactivity**
- **Rule agreement receipt**

## Latest addendum — metric-window truth and row-status overclaim after rev0235

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **windowed metric / metric interpretation review / status row proof / metric receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `what does this row actually prove right now?` can depend on:

- whether a green check is only about all **connected** peers
- whether `X of Y peers` is mixing live peers with historically known peers
- whether an offline-aging threshold has already changed participation semantics
- whether a mobile timestamp is `last synced date`
- whether another column is really `last files changed`
- whether older accuracy fixes reveal that some fields are informative but not self-explanatory proof

So the tighter non-clone line is:

> borrow Resilio's candor that counters and timestamps speak about materially different windows, but refuse any product contract where those windows still require article-hopping before a row can be trusted for action.

That yields four more ordinary product-owned pages:

- **Windowed metric**
- **Metric interpretation review**
- **Status row proof**
- **Metric receipt**

## Latest addendum — presence witness grade and source-proof truth after rev0234

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **presence witness / peer presence review / subject source witness / presence witness receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `what is actually present enough here for me to trust this peer row or file row?` can depend on:

- whether `X of Y peers` is showing live peers or merely historical total peers
- whether a peer was hidden from view rather than unlinked
- whether an online dot is only proving connection while forbidden-network, pause, or sleep policy still narrows participation
- whether any currently present peer still has full bytes for the subject
- whether the current row is only a ghost announcement waiting for an offline source that may never return

So the tighter non-clone line is:

> borrow Resilio's candor that listedness, connection, eligibility, and current source-proof are materially different truths, but refuse any product contract where those still require hopping across peer-list, identity, mobile, pause, and troubleshooting docs.

That yields four more ordinary product-owned pages:

- **Presence witness**
- **Peer presence review**
- **Subject source witness**
- **Presence witness receipt**


## Latest addendum — network eligibility truth and forbidden-network stoppage after rev0233

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **network eligibility / forbidden-network review / network policy delta / network eligibility receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `is this share actually allowed to detect or transfer on the network I am on right now?` can depend on:

- whether global mobile-data policy allows participation on cellular at all
- whether this share is narrowed further to `Wi‑Fi only` or one current network
- whether `Stopped. Forbidden network` means more than slow transfer and still suspends peer connection plus detection
- whether the whole core is asleep under Auto-sleep or Battery Saver rather than route-broken
- whether charging state or later wake cadence will change when participation resumes

So the tighter non-clone line is:

> borrow Resilio's candor that visible shares can be policy-ineligible on the current network, but refuse any product contract where `eligible now`, `blocked by seat policy`, `blocked by share policy`, and `sleeping between wake checks` still require hopping across mobile settings, share-network, interface, and battery-policy docs.

That yields four more ordinary product-owned pages:

- **Network eligibility**
- **Forbidden-network review**
- **Network policy delta**
- **Network eligibility receipt**


## Scope of this revision

This revision is an in-place continuation of `rev0232`, driven by the current request and the now-current archive state:

- continue researching rather than merely polishing
- evaluate Resilio Sync again rather than relying on stale paraphrase
- make every `do not clone` decision point point to a better replacement page
- keep writing concrete interface contracts where the archive still has page-shape gaps
- keep staying narrow: prefer ordinary operator authority and lifecycle surfaces over broad product sprawl
- in this pass specifically, force a cleaner answer for **why a constrained/mobile seat is asking for a platform permission at all**
- in this pass specifically, force a cleaner answer for **what exact capability floor remains if that permission is denied, deferred, revoked, or only partially present**
- in this pass specifically, force a cleaner answer for **which failures are camera-only, storage-only, alerts-only, startup-only, or background-policy-only rather than generic seat breakage**

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

This revision adds one new evaluation and four new interface page specs:

- `591-resilio-platform-permission-provenance-and-capability-fragmentation-evaluation.md`
- `592-platform-permission-provenance-page-family-capability-and-safe-language-interface-spec.md`
- `593-permission-consequence-review-page-grant-denial-revocation-and-fallback-interface-spec.md`
- `594-permission-request-proof-page-trigger-origin-os-dialog-and-feature-boundary-interface-spec.md`
- `595-permission-state-receipt-page-grant-basis-capability-floor-and-aftermath-interface-spec.md`

It also updates the archive-wide doctrine in:

- `README.md`
- `docs/10-resilio-sync-evaluation.md`
- `docs/11-resilio-borrow-line-and-non-clone-scorecard.md`
- `docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md`
- `docs/20-product-direction.md`
- `docs/30-interface-spec.md`
- `docs/38-operator-workbench-interface-spec.md`
- `docs/39-interface-pattern-language.md`
- `docs/40-architecture-decisions.md`
- `docs/50-roadmap.md`
- `docs/sources.md`

## Scope of this revision

This revision is an in-place continuation of `rev0231`, driven by the current request and the now-current archive state:

- continue researching rather than merely polishing
- evaluate Resilio Sync again rather than relying on stale paraphrase
- make every `do not clone` decision point point to a better replacement page
- keep writing concrete interface contracts where the archive still has page-shape gaps
- keep staying narrow: prefer ordinary operator authority and lifecycle surfaces over broad product sprawl
- in this pass specifically, force a cleaner answer for **which runtime a live browser/control endpoint actually belongs to**
- in this pass specifically, force a cleaner answer for **what runtime watermark, storage lineage, and audience/auth grade the product can prove from that endpoint**
- in this pass specifically, force a cleaner answer for **when endpoint recovery or relaunch is actually a control-world switch rather than the same surface continuing**

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

This revision adds one new evaluation and four new interface page specs:

- `586-resilio-control-endpoint-attribution-browser-target-and-runtime-watermark-evaluation.md`
- `587-control-endpoint-attestation-page-runtime-watermark-audience-and-storage-lineage-interface-spec.md`
- `588-endpoint-switch-review-page-port-listener-profile-and-browser-rebind-interface-spec.md`
- `589-browser-target-proof-page-tab-origin-handler-path-and-runtime-match-interface-spec.md`
- `590-control-endpoint-receipt-page-runtime-watermark-endpoint-grade-and-safe-language-interface-spec.md`

It also updates the archive-wide doctrine in:

- `README.md`
- `docs/10-resilio-sync-evaluation.md`
- `docs/11-resilio-borrow-line-and-non-clone-scorecard.md`
- `docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md`
- `docs/20-product-direction.md`
- `docs/30-interface-spec.md`
- `docs/38-operator-workbench-interface-spec.md`
- `docs/39-interface-pattern-language.md`
- `docs/40-architecture-decisions.md`
- `docs/50-roadmap.md`
- `docs/sources.md`

## Scope of this revision

This revision is an in-place continuation of `rev0229`, driven by the current request and the now-current archive state:

- continue researching rather than merely polishing
- evaluate Resilio Sync again rather than relying on stale paraphrase
- make every `do not clone` decision point point to a better replacement page
- keep writing concrete interface contracts where the archive still has page-shape gaps
- keep staying narrow: prefer ordinary operator authority and lifecycle surfaces over broad product sprawl
- in this pass specifically, force a cleaner answer for **what rule is actually effective here right now**
- in this pass specifically, force a cleaner answer for **where that rule came from and which surface truly owns it**
- in this pass specifically, force a cleaner answer for **when a visible control is descriptive only because a deeper override or config-owned rule is winning**

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

This revision adds one new evaluation and four new interface page specs:

- `576-resilio-policy-provenance-hidden-overrides-and-surface-split-evaluation.md`
- `577-policy-provenance-page-effective-rule-origin-override-and-edit-path-interface-spec.md`
- `578-override-mutation-review-page-ui-power-config-and-scope-collision-interface-spec.md`
- `579-hidden-override-surfacing-page-risky-defaults-shadow-rules-and-disablement-interface-spec.md`
- `580-policy-provenance-receipt-page-effective-rule-origin-scope-and-residue-interface-spec.md`

It also updates the archive-wide doctrine in:

- `README.md`
- `docs/10-resilio-sync-evaluation.md`
- `docs/11-resilio-borrow-line-and-non-clone-scorecard.md`
- `docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md`
- `docs/20-product-direction.md`
- `docs/30-interface-spec.md`
- `docs/38-operator-workbench-interface-spec.md`
- `docs/39-interface-pattern-language.md`
- `docs/40-architecture-decisions.md`
- `docs/50-roadmap.md`
- `docs/sources.md`

## Scope of this revision

This revision is an in-place continuation of `rev0228`, driven by the current request and the now-current archive state:

- continue researching rather than merely polishing
- evaluate Resilio Sync again rather than relying on stale paraphrase
- make every `do not clone` decision point point to a better replacement page
- keep writing concrete interface contracts where the archive still has page-shape gaps
- keep staying narrow: prefer ordinary operator authority and lifecycle surfaces over broad product sprawl
- in this pass specifically, force a cleaner answer for **what grade of control surface is actually live right now**
- in this pass specifically, force a cleaner answer for **how audience, auth, transport, and certificate posture combine into one honest sentence**
- in this pass specifically, force a cleaner answer for **which control hardening or recovery path changes grade with what collateral cost**

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

This revision adds one new evaluation and four new interface page specs:

- `571-resilio-control-surface-grade-audience-auth-and-transport-fragmentation-evaluation.md`
- `572-control-surface-grade-page-audience-auth-transport-and-fallback-interface-spec.md`
- `573-exposure-auth-mutation-review-page-loopback-lan-http-https-and-mode-shift-interface-spec.md`
- `574-certificate-posture-page-endpoint-origin-warning-class-and-durable-fix-interface-spec.md`
- `575-control-surface-receipt-page-audience-auth-grade-transport-and-recovery-path-interface-spec.md`

It also updates the archive-wide doctrine in:

- `README.md`
- `docs/10-resilio-sync-evaluation.md`
- `docs/11-resilio-borrow-line-and-non-clone-scorecard.md`
- `docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md`
- `docs/20-product-direction.md`
- `docs/30-interface-spec.md`
- `docs/38-operator-workbench-interface-spec.md`
- `docs/39-interface-pattern-language.md`
- `docs/40-architecture-decisions.md`
- `docs/50-roadmap.md`
- `docs/sources.md`

## Tighter answer reached in this pass

The archive now has another sharper reason to **learn from Resilio without cloning it**:

- borrow Resilio's candor that listener scope, workstation-vs-NAS password floor, transport choice, certificate trust class, and password-reset path materially change the effective control surface
- refuse the product contract where operators still have to infer whether control is local-only, LAN-reachable, passwordless, self-signed, trusted, browser-residue-blocked, or carrying collateral reset side effects
- replace that refusal with one control-surface grade page, one exposure/auth mutation review page, one certificate posture page, and one durable control-surface receipt

## Latest addendum — control-surface grade, audience, auth, and transport after rev0228

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **control-surface grade / exposure-auth mutation review / certificate posture / control-surface receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `what grade of control surface is this, really?` can depend on:

- WebUI docs still saying Linux and Windows service installs default to loopback WebUI and LAN reach requires widening the listen address
- WebUI docs still saying workstation passwords are optional while NAS credentials are compulsory and browser cookies last only for the session
- WebUI docs still saying HTTP remains the default transport and HTTPS requires configuration
- browser-warning docs still treating self-signed HTTPS, click-through, HSTS-clearing, and own-certificate config as distinct states
- password-reset docs still distinguishing settings-file deletion with broader side effects from config-file credential recovery with lower collateral impact
- config-mode docs still allowing password hashes, trusted cert paths, and even disabling live WebUI when shares are declared in config
- the v3 change log still showing the line as active through `3.1.2.1076`

So the tighter non-clone line is:

> borrow Resilio's candor that control surfaces have real audience, auth, transport, and recovery grades, but refuse any product contract where `who can reach this`, `what actually protects it`, `which warning is browser residue versus endpoint truth`, and `which recovery path changes grade with what collateral cost` still require hopping across several help articles.

That yields four more ordinary product-owned pages:

- **Control-surface grade**
- **Exposure/auth mutation review**
- **Certificate posture**
- **Control-surface receipt**

## Scope of this revision

This revision is an in-place continuation of `rev0227`, driven by the current request and the now-current archive state:

- continue researching rather than merely polishing
- evaluate Resilio Sync again rather than relying on stale paraphrase
- make every `do not clone` decision point point to a better replacement page
- keep writing concrete interface contracts where the archive still has page-shape gaps
- keep staying narrow: prefer ordinary operator authority and lifecycle surfaces over broad product sprawl
- in this pass specifically, force a cleaner answer for **which runtime profile is actually in charge**
- in this pass specifically, force a cleaner answer for **whether a runtime/profile switch preserved the same storage-root lineage**
- in this pass specifically, force a cleaner answer for **which control and observation surfaces widened or narrowed as a side effect**

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

This revision adds one new evaluation and four new interface page specs:

- `566-resilio-runtime-profile-locus-storage-lineage-and-surface-reach-fragmentation-evaluation.md`
- `567-runtime-profile-review-page-execution-principal-storage-root-and-surface-reach-interface-spec.md`
- `568-storage-lineage-forecast-page-profile-switch-share-carryover-and-identity-surface-interface-spec.md`
- `569-runtime-switch-review-page-migrate-clean-install-webui-scope-and-observation-loss-interface-spec.md`
- `570-runtime-profile-receipt-page-executing-principal-storage-root-surface-reach-and-followup-interface-spec.md`

It also updates the archive-wide doctrine in:

- `README.md`
- `docs/10-resilio-sync-evaluation.md`
- `docs/11-resilio-borrow-line-and-non-clone-scorecard.md`
- `docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md`
- `docs/20-product-direction.md`
- `docs/30-interface-spec.md`
- `docs/38-operator-workbench-interface-spec.md`
- `docs/39-interface-pattern-language.md`
- `docs/40-architecture-decisions.md`
- `docs/50-roadmap.md`
- `docs/sources.md`

## Tighter answer reached in this pass

The archive now has another sharper reason to **learn from Resilio without cloning it**:

- borrow Resilio's candor that runtime profile, service account, storage root, and control reach are materially different operating loci
- refuse the product contract where operators still have to infer whether they preserved the same seat, moved to a fresh runtime profile, widened control reach, or narrowed observation quality
- replace that refusal with one runtime-profile review page, one storage-lineage forecast page, one runtime-switch review page, and one durable runtime-profile receipt

## Latest addendum — runtime profile continuity, storage-root lineage, and surface reach after rev0227

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **runtime profile review / storage lineage forecast / runtime switch review / runtime profile receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `what actually changed when I switched runtime profile?` can depend on:

- service install docs still distinguishing migrate-settings from clean installation
- service troubleshooting docs still saying a Local System switch can create a new storage root, surface `SYSTEM`, show no old shares, and require re-add / reconnect work
- storage-folder docs still saying settings, databases, logs, and identity details live in profile-specific storage roots
- config-mode docs still allowing a new `storage_path` root and limiting config mode to Standard folders
- Linux docs still treating WebUI listen address as a real reachability and shutdown risk boundary
- uninstall docs still distinguishing unlinking, share removal, and manual profile-root deletion
- the v3 change log still showing the line as active through `3.1.2.1076`

So the tighter non-clone line is:

> borrow Resilio's candor that runtime profile is materially real, but refuse any product contract where `which profile is in charge`, `which storage root is authoritative`, `whether shares and identity carried forward`, and `which surfaces widened or narrowed` still require hopping across several docs.

That yields four more ordinary product-owned pages:

- **Runtime profile review**
- **Storage lineage forecast**
- **Runtime switch review**
- **Runtime profile receipt**

## Scope of this revision

This revision is an in-place continuation of `rev0223`, driven by the current request and the now-current archive state:

- continue researching rather than merely polishing
- evaluate Resilio Sync again rather than relying on stale paraphrase
- make every `do not clone` decision point point to a better replacement page
- keep writing concrete interface contracts where the archive still has page-shape gaps
- keep staying narrow: prefer ordinary operator authority and lifecycle surfaces over broad product sprawl
- in this pass specifically, force a cleaner answer for **what kind of cleanup is actually being requested**
- in this pass specifically, force a cleaner answer for **which witnesses should be preserved before cleanup**
- in this pass specifically, force a cleaner answer for **what evidence survives cleanup and what claim that outcome earns**

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

This revision adds one new evaluation and four new interface page specs:

- `546-resilio-cleanup-intent-and-witness-survival-fragmentation-evaluation.md`
- `547-cleanup-intent-review-page-local-reclaim-detach-uninstall-and-preserve-first-interface-spec.md`
- `548-witness-survival-forecast-page-local-bytes-history-and-hidden-residue-after-cleanup-interface-spec.md`
- `549-preserve-before-cleanup-page-export-pin-and-proof-floor-interface-spec.md`
- `550-cleanup-outcome-receipt-page-freed-scope-surviving-witness-and-strongest-safe-claim-interface-spec.md`

It also updates the archive-wide doctrine in:

- `README.md`
- `docs/10-resilio-sync-evaluation.md`
- `docs/11-resilio-borrow-line-and-non-clone-scorecard.md`
- `docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md`
- `docs/20-product-direction.md`
- `docs/30-interface-spec.md`
- `docs/38-operator-workbench-interface-spec.md`
- `docs/39-interface-pattern-language.md`
- `docs/40-architecture-decisions.md`
- `docs/50-roadmap.md`
- `docs/sources.md`

## Tighter answer reached in this pass

The archive now has another sharper reason to **learn from Resilio without cloning it**:

- borrow Resilio's candor that cleanup verbs, local reclaim, linked removal, and uninstall are materially different
- refuse the product contract where operators still have to infer whether cleanup should preserve evidence first and what witness survives afterward
- replace that refusal with one cleanup-intent review page, one witness-survival forecast page, one preserve-before-cleanup page, and one durable cleanup-outcome receipt

## Latest addendum — cleanup intent and witness survival after rev0223

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **cleanup intent review / witness survival forecast / preserve-before-cleanup / cleanup outcome receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `what kind of cleanup is this, and what proof survives it?` can depend on:

- disconnect/remove docs still distinguishing one-device detach from linked-device removal
- synchronization-mode docs still distinguishing local placeholder reversion from all-peer deletion and archive placement
- Selective Sync docs still warning that removing the share drops placeholders from the local filesystem
- iOS storage-management docs still separating app data from user data and allowing local-copy clearing only on Selective Sync shares
- uninstall docs still saying app removal does not delete previously shared folders or hidden archived files automatically on desktop platforms, while iOS uninstall removes local synced files because of platform architecture
- the v3 change log still showing the line as active through `3.1.2.1076`

So the tighter non-clone line is:

> borrow Resilio's candor that cleanup verbs are materially different, but refuse any product contract where `what cleanup family this is`, `what should be preserved first`, `what survives afterward`, and `what sentence the result actually earns` still require hopping across several help articles.

That yields four more ordinary product-owned pages:

- **Cleanup intent review**
- **Witness survival forecast**
- **Preserve-before-cleanup**
- **Cleanup outcome receipt**

## Scope of this revision

This revision is an in-place continuation of `rev0222`, driven by the current request and the now-current archive state:

- continue researching rather than merely polishing
- evaluate Resilio Sync again rather than relying on stale paraphrase
- make every `do not clone` decision point point to a better replacement page
- keep writing concrete interface contracts where the archive still has page-shape gaps
- keep staying narrow: prefer ordinary operator authority and lifecycle surfaces over broad product sprawl
- in this pass specifically, force a cleaner answer for **how long recovery evidence stays strong**
- in this pass specifically, force a cleaner answer for **which surfaces can still reach the evidence before it decays**
- in this pass specifically, force a cleaner answer for **what retention or cleanup changes narrow later recovery truth**

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

This revision adds one new evaluation and four new interface page specs:

- `541-resilio-recovery-horizon-retention-and-surface-decay-evaluation.md`
- `542-recovery-horizon-page-byte-event-access-half-life-interface-spec.md`
- `543-witness-expiry-forecast-page-retention-floor-and-platform-loss-interface-spec.md`
- `544-retention-mutation-review-page-policy-change-evidence-survival-and-space-cost-interface-spec.md`
- `545-recovery-horizon-receipt-page-available-until-proof-floor-and-expiry-risks-interface-spec.md`

It also updates the archive-wide doctrine in:

- `README.md`
- `docs/10-resilio-sync-evaluation.md`
- `docs/11-resilio-borrow-line-and-non-clone-scorecard.md`
- `docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md`
- `docs/20-product-direction.md`
- `docs/30-interface-spec.md`
- `docs/32-interface-flows.md`
- `docs/38-operator-workbench-interface-spec.md`
- `docs/39-interface-pattern-language.md`
- `docs/40-architecture-decisions.md`
- `docs/50-roadmap.md`
- `docs/sources.md`

## Tighter answer reached in this pass

The archive now has another sharper reason to **learn from Resilio without cloning it**:

- borrow Resilio's candor that recovery evidence has real time, size, platform, and cleanup limits
- refuse the product contract where operators still have to infer byte horizon, event horizon, access reach, and hidden residue from separate help articles
- replace that refusal with one recovery-horizon page, one witness-expiry forecast page, one retention-mutation review page, and one durable recovery-horizon receipt

## Latest addendum — recovery horizon and evidence half-life after rev0222

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **recovery horizon / witness expiry forecast / retention mutation review / recovery horizon receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `how long is this recoverable and from where?` can depend on:

- Archive docs still saying defaults are 30 days on desktops and 1 day on mobiles
- those same docs still saying version capture can be excluded by `max_file_size_for_versioning`
- platform reach still differing across desktop, WebUI, Android, Android SD-card shares, and iOS
- desktop Main View still treating History as a 30-day event lane
- `.sync` docs still placing Archive in hidden control storage
- uninstall docs still saying app removal does not remove archived files automatically

So the tighter non-clone line is:

> borrow Resilio's candor that recovery evidence has a real half-life and real access cliffs, but refuse any product contract where `how long it lasts`, `which surface can still reach it`, `what policy excluded it`, and `what residue survives app removal` still require hopping across several docs.

That yields four more ordinary product-owned pages:

- **Recovery horizon**
- **Witness expiry forecast**
- **Retention mutation review**
- **Recovery horizon receipt**

## Scope of this revision

This revision is an in-place continuation of `rev0221`, driven by the current request and the now-current archive state:

- continue researching rather than merely polishing
- evaluate Resilio Sync again rather than relying on stale paraphrase
- make every `do not clone` decision point point to a better replacement page
- keep writing concrete interface contracts where the archive still has page-shape gaps
- keep staying narrow: prefer ordinary operator authority and lifecycle surfaces over broad product sprawl
- in this pass specifically, force a cleaner answer for **where prior-version witnesses actually live**
- in this pass specifically, force a cleaner answer for **which seat should perform recovery work**
- in this pass specifically, force a cleaner answer for **which recovery facts come from Archive versus History**

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

This revision adds one new evaluation and four new interface page specs:

- `536-resilio-rollback-witness-locality-and-archive-bearing-asymmetry-evaluation.md`
- `537-witness-locality-map-page-prior-version-holders-retention-and-access-limits-interface-spec.md`
- `538-recovery-host-choice-page-witness-seat-runtime-liveness-and-replay-locus-interface-spec.md`
- `539-archive-history-bridge-page-candidate-bytes-authorship-join-and-gap-labels-interface-spec.md`
- `540-recovery-locus-receipt-page-witness-seat-restore-shape-and-proof-limits-interface-spec.md`

It also updates the archive-wide doctrine in:

- `README.md`
- `docs/10-resilio-sync-evaluation.md`
- `docs/11-resilio-borrow-line-and-non-clone-scorecard.md`
- `docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md`
- `docs/20-product-direction.md`
- `docs/30-interface-spec.md`
- `docs/32-interface-flows.md`
- `docs/38-operator-workbench-interface-spec.md`
- `docs/39-interface-pattern-language.md`
- `docs/40-architecture-decisions.md`
- `docs/50-roadmap.md`
- `docs/sources.md`

## Tighter answer reached in this pass

The archive now has another sharper reason to **learn from Resilio without cloning it**:

- borrow Resilio's candor that prior-version witnesses are peer-local, asymmetric, and runtime-sensitive
- refuse the product contract where operators still have to infer which seat actually holds the old bytes and which seat should perform the recovery
- replace that refusal with one witness-locality map page, one recovery-host choice page, one archive/history bridge page, and one durable recovery-locus receipt

## Latest addendum — rollback witness locality after rev0221

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **witness locality map / recovery host choice / archive-history bridge / recovery locus receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `where does the recoverable prior version actually live?` can depend on:

- Archive docs still saying prior versions land on *other* peers, not the mutating peer
- Archive docs still saying restore is manual and runtime-sensitive
- rename docs still relying on Archive to avoid re-transfer under the new name
- desktop main-view docs still making History the 30-day event lane while Archive lacks actor attribution
- platform reach still differing across desktop, WebUI, Android, and iOS

So the tighter non-clone line is:

> borrow Resilio's candor that recovery witnesses are local to particular peers and that Archive is useful but incomplete, but refuse any product contract where `which seat has the bytes`, `which seat should perform the restore`, `what proof still comes from History`, and `what stronger sentence is forbidden` still require hopping across several docs.

That yields four more ordinary product-owned pages:

- **Witness locality map**
- **Recovery host choice**
- **Archive / History bridge**
- **Recovery locus receipt**

## Scope of this revision

This revision is an in-place continuation of `rev0220`, driven by the current request and the now-current archive state:

- continue researching rather than merely polishing
- evaluate Resilio Sync again rather than relying on stale paraphrase
- make every `do not clone` decision point point to a better replacement page
- keep writing concrete interface contracts where the archive still has page-shape gaps
- keep staying narrow: prefer ordinary operator authority and lifecycle surfaces over broad product sprawl
- in this pass specifically, force a cleaner answer for **what `pause` actually stops**
- in this pass specifically, force a cleaner answer for **what still remains live during a paused state**
- in this pass specifically, force a cleaner answer for **what stronger action is needed when the operator really wants maintenance-grade quiet**

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

This revision adds one new evaluation and four new interface page specs:

- `531-resilio-pause-quiescence-ambiguity-and-partial-stop-truth-evaluation.md`
- `532-quiescence-review-page-phase-stop-residual-activity-and-safe-alternative-interface-spec.md`
- `533-residual-activity-matrix-page-transfer-detect-delete-and-readiness-lanes-interface-spec.md`
- `534-pause-language-substitution-page-freeze-stop-and-quiesce-claim-rewrite-interface-spec.md`
- `535-quiescence-receipt-page-requested-stop-effective-scope-and-residual-flow-interface-spec.md`

It also updates the archive-wide doctrine in:

- `README.md`
- `docs/10-resilio-sync-evaluation.md`
- `docs/11-resilio-borrow-line-and-non-clone-scorecard.md`
- `docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md`
- `docs/20-product-direction.md`
- `docs/30-interface-spec.md`
- `docs/32-interface-flows.md`
- `docs/38-operator-workbench-interface-spec.md`
- `docs/39-interface-pattern-language.md`
- `docs/40-architecture-decisions.md`
- `docs/50-roadmap.md`
- `docs/sources.md`

## Tighter answer reached in this pass

The archive now has another sharper reason to **learn from Resilio without cloning it**:

- borrow Resilio's candor that `pause` is a partial stop rather than a magical freeze
- refuse the product contract where operators still have to infer that stop vector from help prose or reconcile differing official pause-language details
- replace that refusal with one quiescence-review page, one residual-activity matrix page, one pause-language substitution page, and one durable quiescence receipt

## Latest addendum — pause, quiescence, and partial-stop truth after rev0220

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **quiescence review / residual activity matrix / pause language substitution / quiescence receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `what does pause actually stop here?` can depend on:

- the current pause docs still saying pause stops only bits uploads/downloads
- those same docs still saying deletions, zero-sized files, and rescans continue
- scheduler docs still confirming partial-stop behavior rather than total stillness
- scheduler docs describing paused-peer upload behavior differently from the ordinary pause article
- older-but-still-official changelog history showing paused-state indexing semantics have been subtle enough to break and need fixes

So the tighter non-clone line is:

> borrow Resilio's candor that `pause` is weaker than ordinary-language `freeze`, but refuse any product contract where `what actually stopped`, `what still lives`, `what sentence is safe`, and `what stronger action is needed for maintenance-grade quiet` still require cross-reading pause, scheduler, and changelog material.

That yields four more ordinary product-owned pages:

- **Quiescence review**
- **Residual activity matrix**
- **Pause language substitution**
- **Quiescence receipt**

## Scope of this revision

This revision is an in-place continuation of `rev0219`, driven by the current request and the now-current archive state:

- continue researching rather than merely polishing
- evaluate Resilio Sync again rather than relying on stale paraphrase
- make every `do not clone` decision point point to a better replacement page
- keep writing concrete interface contracts where the archive still has page-shape gaps
- keep staying narrow: prefer ordinary operator authority and lifecycle surfaces over broad product sprawl
- in this pass specifically, force a cleaner answer for **what sentence an action actually earns**
- in this pass specifically, force a cleaner answer for **which stronger post-action claims must be forbidden**
- in this pass specifically, force a cleaner answer for **what residual proof blocks a stronger sentence**

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

This revision adds one new evaluation and four new interface page specs:

- `526-resilio-post-action-claim-ceiling-and-recall-overstatement-evaluation.md`
- `527-action-claim-review-page-requested-verb-effective-claim-and-forbidden-overstatement-interface-spec.md`
- `528-residual-claim-matrix-page-local-linked-external-and-history-proof-interface-spec.md`
- `529-safe-language-substitution-page-operator-verb-rewrite-and-audience-fit-interface-spec.md`
- `530-action-statement-receipt-page-effective-claim-residual-scope-and-forbidden-phrases-interface-spec.md`

It also updates the archive-wide doctrine in:

- `README.md`
- `docs/10-resilio-sync-evaluation.md`
- `docs/11-resilio-borrow-line-and-non-clone-scorecard.md`
- `docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md`
- `docs/20-product-direction.md`
- `docs/30-interface-spec.md`
- `docs/38-operator-workbench-interface-spec.md`
- `docs/39-interface-pattern-language.md`
- `docs/40-architecture-decisions.md`
- `docs/50-roadmap.md`
- `docs/sources.md`

## Tighter answer reached in this pass

The archive now has another sharper reason to **learn from Resilio without cloning it**:

- borrow Resilio's candor that disconnect, revoke, remove, unlink, local eviction, global delete, and incident rotation earn different truth ceilings
- refuse the product contract where operators still infer the safe post-action sentence by cross-reading several help articles
- replace that refusal with one action-claim review page, one residual-claim matrix page, one safe-language substitution page, and one durable action-statement receipt

## Latest addendum — post-action claim ceiling after rev0219

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **action claim review / residual claim matrix / safe language substitution / action statement receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `what am I allowed to say now?` can depend on:

- whether `Disconnect` only revoked future updates while landed files remain
- whether folder disconnect only severed one seat while local bytes remain on disk
- whether linked-cohort remove still leaves non-linked remote retainers possible
- whether `Remove from this device` was only local eviction to placeholders
- whether `Remove from all devices` still leaves archive / retention consequences
- whether unlink was only local because remote unlink is unavailable
- whether incident response still requires broader rotation before `contained` is an honest sentence

So the tighter non-clone line is:

> borrow Resilio's candor that common actions earn different truth ceilings, but refuse any product contract where `what sentence did this action earn`, `what stronger sentence is still unsupported`, `what residue blocks it`, and `what stronger action would be needed` still require hopping across user-management, disconnect/remove, placeholder, identity, and incident-recovery docs.

That yields four more ordinary product-owned pages:

- **Action claim review**
- **Residual claim matrix**
- **Safe language substitution**
- **Action statement receipt**


## Latest addendum — hidden witness access and surface visibility after rev0224

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **evidence visibility review / hidden witness surfacing / surface handoff / evidence access receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `can I actually inspect the recovery witness from where I am standing?` can depend on:

- Archive living in hidden `.sync/Archive`
- desktop UI open paths versus file-browser open paths not being the same thing
- WebUI and Android still depending on file-browser access to hidden Archive
- iOS not exposing Archive access
- hidden `.sync` being critical state rather than disposable clutter
- uninstall removing the program while hidden witness can still remain on disk

So the tighter non-clone line is:

> borrow Resilio's candor that witnesses can exist, remain hidden, and survive cleanup, but refuse any product contract where `exists somewhere`, `inspectable here`, `inspectable only via another surface`, and `unavailable on this surface` still require hopping across Archive, .sync, uninstall, and platform caveat docs.

That yields four more ordinary product-owned pages:

- **Evidence visibility review**
- **Hidden witness surfacing**
- **Surface handoff**
- **Evidence access receipt**


## Latest addendum — proxy artifacts and local-looking action scope after rev0225

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **proxy artifact review / counterpart map / proxy action substitution / proxy artifact receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `what kind of thing is this visible row and what would delete actually do here?` can depend on:

- whether `.rsls` means placeholder proxy rather than full local bytes
- whether `Remove from this device` is only local eviction while all-peer deletion is broader
- whether a placeholder delete with read-write access removes the file from all peers
- whether a `.Conflict` row is a harmless duplicate or a dangerous correspondent to real remote material
- whether hidden `.sync` is witness or service state rather than user content

So the tighter non-clone line is:

> borrow Resilio's candor that visible filesystem rows are not always ordinary local files, but refuse any product contract where `what artifact class is this`, `what canonical subject does it stand for`, and `what local-looking verb really means here` still require hopping across placeholder, synchronization-mode, conflict, Archive, and service-state docs.

That yields four more ordinary product-owned pages:

- **Proxy artifact review**
- **Counterpart map**
- **Proxy action substitution**
- **Proxy artifact receipt**


## Latest addendum — subject non-arrival cause and least-destructive intervention after rev0226

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **subject delivery review / absence-cause matrix / minimal intervention chooser / delivery truth receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `why is this subject not here or not advancing right now?` can depend on:

- whether IgnoreList or metadata policy intentionally excluded it
- whether locks, missing write permission, or read-only divergence are blocking it locally
- whether path / encoding / length limits make it unportable rather than merely slow
- whether the product is still hashing, merging, scanning, or writing rather than actually stuck
- whether watchers are exhausted and discovery has fallen back to periodic rescan
- whether the tree still advertises a ghost subject that no peer now has as bytes
- whether same-lineage continuity is broken because service files are missing

So the tighter non-clone line is:

> borrow Resilio's candor that `not here` can mean many different things, but refuse any product contract where `which absent-state class applies`, `what evidence supports it`, and `what least-strong move is justified` still require hopping across troubleshooting lists, warning articles, and repair folklore.

That yields four more ordinary product-owned pages:

- **Subject delivery review**
- **Absence-cause matrix**
- **Minimal intervention chooser**
- **Delivery truth receipt**


## Latest addendum — disappearing safer rungs, edition-shaped action floors, and typed substitution after rev0242

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **action availability / severance ladder review / capability substitution / control-absence receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `why can't I do the gentler thing here?` can depend on:

- `Disconnecting and Removing Folders` still distinguishing one-device disconnect from broader remove
- `Selective Sync` still being a capability-bearing posture rather than a cosmetic toggle
- `Synchronization Modes` and `Folder Types and Management` still making `Disconnected`, `Selective Sync`, and `Synced` materially different action worlds
- the current desktop Free article still saying there is no `Disconnect` button and only `Remove` is available, explicitly bypassing the disconnect stage because Free exposes only `Synced`

So the tighter non-clone line is:

> borrow Resilio's candor that gentler and stronger severance rungs are different, but refuse any product contract where a missing safer rung, the basis for its absence, and the least-strong substitute still require hopping across mode docs, feature-availability notes, and troubleshooting-style edition articles.

That yields four more ordinary product-owned pages:

- **Action availability**
- **Severance ladder review**
- **Capability substitution**
- **Control-absence receipt**


## Latest addendum — representative-pair judgment, topology-slice ownership, and mesh-wide claim ceilings after rev0270

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **topology slice / representativeness review / topology extrapolation / topology measurement receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `does this pairwise result really explain the rest of the incident?` can depend on:

- `Performance overview` still exposing a table of peer connections with upload, download, RTT, and protocol for each connected peer
- `Download/upload speed is very slow` still saying one slow uploader can drag other peers and that more strong uploaders can raise the effective download rate
- that same slow-speed article still escalating persistent cases to logs from all peers
- `Measuring network performance with iperf3` still prescribing a benchmark between two peers with Sync shut down on both peers during the test
- `Folder Preferences` still making relay/tracker/LAN/predefined-host posture a per-folder setting that should be used on all peers when constraining discovery paths

So the tighter non-clone line is:

> borrow Resilio's candor that pairwise, cohort-wide, and share-wide performance truths differ, but refuse any product contract where whether one measured pair is actually representative still requires hopping across charts, troubleshooting prose, helper settings, and support escalation rituals.

That yields four more ordinary product-owned pages:

- **Topology slice**
- **Representativeness review**
- **Topology extrapolation**
- **Topology measurement receipt**


## Latest addendum — change-detection coverage, blind-window ownership, and freshness claim ceilings after rev0272

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **detection posture / observation coverage review / change freshness review / change-detection receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `why has this not been noticed yet, and is that actually late?` can depend on:

- `How soon does synchronization start?` still separating filesystem notifications, scheduled rescans, and on-demand rescans, with default scheduled rescans every 600 seconds
- that same FAQ still saying `folder_rescan_interval = 0` disables automatic rescans even on restart
- `Agent run out of system notify watchers` still saying watcher exhaustion can move discovery onto periodic or manual rescans
- `Ignoring files in Sync (Ignore List)` still saying IgnoreList rereads rely on change notifications or else every `folder_rescan_interval`, with restart recommended for immediate effect
- `Sync prevents HDD from sleeping on NAS...` still recommending much larger rescan and refresh intervals to preserve NAS sleep

So the tighter non-clone line is:

> borrow Resilio's candor that change discovery can be notification-backed, rescan-backed, or effectively manual, but refuse any product contract where the active detection plane, blind window, and freshness claim ceiling still require hopping across FAQs, warning pages, and power-user tuning advice.

That yields four more ordinary product-owned pages:

- **Detection posture**
- **Observation coverage review**
- **Change freshness review**
- **Change-detection receipt**

## Latest addendum — freshness-claim invalidation, posture drift, and receipt supersession after rev0273

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **freshness invalidator / freshness revalidation review / posture drift timeline / freshness rollover receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `does our earlier freshness judgment still apply after the environment changed?` can depend on:

- `Agent run out of system notify watchers` still saying watcher exhaustion can move discovery onto periodic or manual rescans until limits are raised
- `Sync Service Troubleshooting on Windows` still saying service-style network-drive / UNC use may lose notifications and that switching to Local System creates a different storage root and apparent share world
- `Sync and SMB file shares` still saying missing SMB notifications mean detection only during full folder rescan
- `Sync prevents HDD from sleeping on NAS...` still recommending much larger rescan / refresh / save intervals, while `How soon does synchronization start?` still says `folder_rescan_interval = 0` disables rescans even on restart
- `Configuring Auto Sleep & Battery Saver (Android)` still saying the mobile core can go offline between wake intervals or stop below a battery threshold
- `Setting network interface per share` still saying forbidden-network posture prevents peers from connecting and new or updated files from being detected

So the tighter non-clone line is:

> borrow Resilio's candor that observation posture can drift materially after an incident begins, but refuse any product contract where whether an old freshness receipt is still current still requires hopping across watcher warnings, service/SMB caveats, NAS cadence advice, and mobile power/network docs.

That yields four more ordinary product-owned pages:

- **Freshness invalidator**
- **Freshness revalidation review**
- **Posture drift timeline**
- **Freshness rollover receipt**


## Latest addendum — maintenance rejoin, shared-line restoration, and successor boundaries after rev0282

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **maintenance rejoin plan / maintenance rejoin review / maintenance rejoin ledger / maintenance rejoin receipt**

Current official Resilio docs still admit that narrow-seat local work can survive in materially different restoration classes: `User Management` still says Read Only changes do not propagate and suspend future sync for the touched files; `Is one-way synchronization possible?` still says overwrite healing can restore deleted files, re-download pre-rename names, revert edited contents, and keep newly added files local rather than syncing them; `Folder Preferences` still says overwrite is potentially destructive and disabled for Read-only folders with Selective Sync ON; `Encrypted folders` still says encrypted backup nodes are Read Only, always overwrite, need saved keys plus preserved database continuity or special local decrypt flow for restoration, and cannot simply restore encrypted-archive files back into the swarm; `How to use Camera Backup (all mobiles)?` still says backup folders are storage-oriented Read Only folders and disconnect leaves already-present files on both ends; `Sync Interface on iOS devices` still says `Remove from this device` preserves copies elsewhere while removing the device-local copy; and the live v3 line still runs through `3.1.2.1076`.
So the tighter non-clone line is:

> borrow Resilio's candor that local work under a narrow posture can survive with several later fates, but refuse any product contract where the operator still has to infer from permissions, overwrite, encryption, backup, and device-local disconnect docs whether that work can rejoin the shared line, only become a successor, or never rejoin honestly at all.

That yields four more ordinary product-owned pages:

- **Maintenance rejoin plan page**
- **Maintenance rejoin review page**
- **Maintenance rejoin ledger page**
- **Maintenance rejoin receipt page**

## Latest addendum — destructive-heal preview, salvage ladders, and loss-waiver ownership after rev0283

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **maintenance overwrite plan / maintenance overwrite review / maintenance overwrite ledger / maintenance overwrite receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `if I let source-authoritative healing proceed right now, what exact local work will be destroyed, what salvage remains, and what loss am I waiving?` can depend on:

- `Is one-way synchronization possible?` still separating the fate of renamed, deleted, edited, and newly added files under Read Only overwrite healing
- `Folder Preferences` still saying overwrite is potentially destructive, while Archive stores remotely caused changed/deleted files in `.sync/Archive` for 30 days by default and disabling Archive removes that safety copy and makes remote rename/copy fall back to re-download
- `Using Archive for file versioning and restoring deleted files` still saying a device's Archive receives prior versions only when the file was modified by another peer, while locally deleted files usually live in local trash instead
- `Encrypted folders` still saying encrypted backup nodes are Read Only, always overwrite, and can move same-key preexisting encrypted files into Archive with extra space cost
- `Power user preferences` still publishing `overwrite_changes` and `sync_trash_ttl` as standing defaults that shape the damage and salvage ladder
- mobile interface docs still exposing separate `Use Archive` and overwrite toggles on Android and iOS

So the tighter non-clone line is:

> borrow Resilio's candor that source-authoritative healing can destroy local work and that salvage depends on archive-bearing conditions, but refuse any product contract where exact surrender scope and remaining rescue options still require hopping across one-way-sync, archive, preferences, encryption, and mobile-help prose.

That yields four more ordinary product-owned pages:

- **Maintenance overwrite plan page**
- **Maintenance overwrite review page**
- **Maintenance overwrite ledger page**
- **Maintenance overwrite receipt page**

## Latest addendum — projection-stable rename verbs and cross-projection action receipts after rev0291

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **action verb contract / rename intent disambiguation / projection semantic gap review / cross-projection rename preview / action lineage receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `what exactly will this rename control change from here?` can depend on:

- `Setting custom name for sync shares` still saying desktop custom name is UI-only, does not rename the folder on disk, and does not propagate to other peers or linked devices
- that same article still saying outward link/QR labels can be changed while the underlying share name remains unchanged
- `Can I move or rename a syncing folder?` still saying filesystem rename affects only the local device
- `Sync interface on Android` still saying the share-name pencil renames both in Sync and in the filesystem
- `Sync Interface on iOS devices` still saying the share-name pencil lets you rename the share, while being less explicit than Android about the exact plane effect

So the tighter non-clone line is:

> borrow Resilio's candor that different projections can expose different rename powers, but refuse any product contract where the operator still has to remember which client they are standing in to know what a familiar-looking `rename` control will do.

That yields five more ordinary product-owned pages:

- **Action verb contract sheet**
- **Rename intent disambiguation**
- **Projection semantic gap review**
- **Cross-projection rename preview**
- **Action lineage receipt**



## Latest addendum — LAN-only proof, helper cutoff, and route-boundary receipts after rev0292

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **reachability contract sheet / LAN-scope review / route provenance sheet / exposure budget review / route boundary receipt**

Current official Resilio docs still admit that route posture has several materially different truth planes: `Folder Preferences` still splits tracker, relay, Search LAN, and predefined hosts; `What ports and protocols are used by Sync?` still describes discovery and transfer as a staged sequence with direct and relay branches; `Can I force Sync to do local network (LAN) syncing only and not sync via the Internet?` still says true LAN-only needs both helper cutoff and public-route-cache cleanup; `Sync Preferences` still keeps listening port, UPnP, and proxy posture in a separate surface; `Power user preferences` still keeps bind-interface and refresh knobs in yet another surface; and `Peers aren't connecting` still turns the final route answer into a troubleshooting climb through tracker, relay, listener, multicast, proxy, and multiple-NIC possibilities.

So the tighter non-clone line is:

> borrow Resilio's candor that route truth is multi-stage and evidence-bearing, but refuse any product contract where one ordinary answer to `is this really LAN-only / what wider reach did I just allow?` still requires hopping across share preferences, settings, power-user knobs, config, and troubleshooting pages.

That yields five more ordinary product-owned pages:

- **Reachability contract sheet**
- **LAN-scope review**
- **Route provenance sheet**
- **Exposure budget review**
- **Route boundary receipt**


## Latest addendum — mutability classes, birth commitments, and recreate-boundary receipts after rev0301

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **mutability contract sheet / birth-commitment review / post-create change preview / recreate-boundary page / mutability lineage receipt**

Current official docs still admit that editability is not one truth plane: current Sync help still says Standard folders cannot become Advanced in place and Standard permission changes can require remove/re-add; current Active Everywhere docs still say permission-sync settings for Synchronization, Hybrid Work, and File Caching jobs are applied when the job is created and cannot be changed later; current Linux cache-server docs still say selected access and cache paths cannot be changed later after save; and current migration docs still publish a real successor workflow for turning Sync jobs into File cache or Hybrid work jobs.

So the tighter non-clone line is:

> borrow Resilio's candor that some choices really are birth-time commitments, but refuse any product contract where one ordinary answer to `can I change this later or not?` still requires hopping across folder-class docs, profiles tables, cache-server setup pages, and migration guides.

That yields five more ordinary product-owned pages:

- **Mutability contract sheet**
- **Birth-commitment review**
- **Post-create change preview**
- **Recreate-boundary page**
- **Mutability lineage receipt**

## Latest addendum — event evidence retention, attribution gaps, and audit-ceiling receipts after rev0305

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **evidence retention contract sheet / evidence-source join review / attribution gap page / retention horizon watch / evidence lineage receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `what durable proof remains of what happened, who did it, and for how long?` can depend on:

- desktop main-view docs still making **History** the 30-day event lane
- archive docs still saying **Archive** lacks actor attribution and points the operator back to **History**
- those same archive docs still publishing different default retention on desktop versus mobile
- sync-preferences docs still treating notifications as a toggled signal surface rather than a durable receipt system
- iOS file-sharing docs still letting transfer history outlive local file removal in at least one flow
- historic changelog/UI lineage still exposing `Date synced`, `Last transferred`, and synchronized notifications as helpful but weaker evidence surfaces

So the tighter non-clone line is:

> borrow Resilio's candor that evidence comes in different families with different retention and proof ceilings, but refuse any product contract where `who changed this`, `what proof survives`, `how long it survives`, and `what stronger sentence is forbidden` still require hopping across History, Archive, notifications, transfer-history quirks, and old UI notes.

That yields five more ordinary product-owned pages:

- **Evidence retention contract sheet**
- **Evidence-source join review**
- **Attribution gap page**
- **Retention horizon watch**
- **Evidence lineage receipt**

## Latest addendum — mutation durability, persistence ceilings, and boot-authority receipts after rev0309

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **mutation durability contract sheet / persist-before-risk review / persisted-state proof / boot-authority replay review / mutation durability receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `I changed this — what is true now, what survives crash, and what will next boot actually replay?` can depend on:

- power-user docs still making **`config_save_interval`** the cadence at which settings are saved to storage
- NAS sleep docs still recommending much wider save cadence, directly stretching the potential gap between live state and durable persistence
- config-mode docs still saying config-defined folders can **disable WebUI** and **override** previously interactive folders
- WebUI docs still splitting listener authority between config-owned and interactive planes
- Linux/storage docs still saying settings, identity, and license live in the **storage** directory
- Windows service troubleshooting still saying a service-user change can create a **different storage world** where prior folders and remembered state do not simply appear

So the tighter non-clone line is:

> borrow Resilio's candor that live runtime truth, persisted storage truth, and boot-authoritative config truth are materially different — but refuse any product contract where `changed in the UI`, `survives restart`, `wins on next boot`, and `belongs to the same state world` still require hopping across save-cadence docs, config-mode docs, storage docs, and service troubleshooting pages.

That yields five more ordinary product-owned pages:

- **Mutation durability contract sheet**
- **Persist-before-risk review**
- **Persisted-state proof**
- **Boot-authority replay review**
- **Mutation durability receipt**



## Latest addendum — object-kind fidelity, link-target boundary, and bundle-collapse receipts after rev0315

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **special object contract sheet / special object intake review / link target boundary / bundle fidelity warning / special object lineage receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `what is this thing really, and what fidelity survives across the cohort?` can depend on:

- symlink/junction support docs that differ sharply between Windows and Unix
- power-user settings that can ignore symlinks or disable extended-attribute syncing
- StreamsList/xattr docs that explain whitelist-based metadata preservation and `.sync/Streams` residue
- troubleshooting notes that explain why some metadata-dependent bundles degrade into ordinary subdirectories

So the tighter non-clone line is:

> borrow Resilio's candor that object kind, reference preservation, metadata fidelity, and compatibility residue are materially different — but refuse any product contract where `sync this object` still hides whether the object is a preserved reference, an excluded target, a stub-backed metadata case, or a collapsed plain directory.

That yields five more ordinary product-owned pages:

- **Special object contract sheet**
- **Special object intake review**
- **Link target boundary**
- **Bundle fidelity warning**
- **Special object lineage receipt**
