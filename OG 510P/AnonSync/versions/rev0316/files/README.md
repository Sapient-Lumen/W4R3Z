## Revision addendum — nested overlap topology, bridge hosts, and carried-edit truth

This revision continues directly from `rev0314` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **sharing a nested child folder separately, separate-subject treatment, bridge-host propagation, disabled Selective Sync, and duplicate indexing/rescan cost**.
2. Tightens the non-clone line again: borrow Resilio's candor that parent/child overlap creates a real sync graph; refuse any contract where the operator still has to infer `who can seed whom, how child edits can travel, and who pays the extra work` from an FAQ and hierarchy intuition.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio nested-overlap truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: overlapping subject contract sheet, overlap topology review, independent seed horizon, overlap load warning, and overlap lineage receipt.
5. Makes one hard product decision explicit: **overlap is a first-class topology object rather than a side effect of path containment**.
6. Makes another hard product decision explicit: **bridge hosts must be named whenever they can carry child edits into the parent audience**.
7. Makes a third hard product decision explicit: **nested overlap is blocked by default unless duplicate indexing/rescan cost and carried-edit consequences are reviewed**.
8. Integrates these decisions back into the comparison spine so later revisions inherit a stable non-clone line on parent/child overlap.

New docs in this tranche:

- `1030-resilio-nested-share-overlap-topology-and-seed-fragmentation-evaluation.md`
- `1031-overlapping-subject-contract-sheet-page-parent-child-boundary-seed-horizon-and-indexing-load-interface-spec.md`
- `1032-overlap-topology-review-page-parent-share-child-share-carried-edits-and-blocked-assumptions-interface-spec.md`
- `1033-independent-seed-horizon-page-parent-only-peer-child-only-peer-and-bridge-host-truth-interface-spec.md`
- `1034-overlap-load-warning-page-double-indexing-rescan-cost-and-selective-sync-incompatibility-interface-spec.md`
- `1035-overlap-lineage-receipt-page-subject-boundaries-bridge-paths-and-blocked-stronger-sentences-interface-spec.md`

## Revision addendum — resource budget, starvation truth, and bottleneck proof

This revision continues directly from `rev0313` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **global send/receive rates, scheduler pause semantics, power-user resource knobs, download-priority queue behavior, hidden internal tasks, and memory-scale warnings**.
2. Tightens the non-clone line again: borrow Resilio's candor that throughput is governed by multiple real budgets; refuse any contract where the operator still has to reconstruct `what is slow, why, and who is paying for that slowdown?` from settings pages, queue docs, and troubleshooting articles.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio resource-budget truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: resource budget contract sheet, resource budget review, starvation and suspension warning, resource pressure proof, and resource budget lineage receipt.
5. Makes one hard product decision explicit: **resource budget becomes a first-class contract object rather than a generic performance summary**.
6. Makes another hard product decision explicit: **budget lanes stay separate — WAN, LAN, disk, CPU/indexing, memory, and free-space are not one slider**.
7. Makes a third hard product decision explicit: **starvation risk and queue-preemption truth must be inspectable, not inferred from a friendly visible list order**.
8. Packages the result as another continuation archive whose new tranche makes the `resource-budget / precedence / starvation-warning / bottleneck-proof / durable-receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present resource-budget contract**

This time the reason is especially clear around **global WAN rate limits that do not automatically apply to LAN, scheduled `Paused` windows that still permit some mutations, power-user settings that materially alter disk/CPU/fairness behavior, priority queues with caps and hidden exceptions, and memory pressure that remains structural rather than cosmetic**.
Current official materials simultaneously show that:

- the current `Sync Preferences` article still says receiving/sending limits apply to internet traffic by default and need `rate_limit_local_peers` for LAN.
- the current scheduler article still says `Paused` zeros upload/download rates while zero-sized files, deletions, rescans, and indexing still proceed.
- the current `Power user preferences` article still exposes `disk_low_priority`, `disk_worker_per_job`, `worker_threads_count`, `rate_limit_local_peers`, and `free_space_warning_threashold` as real resource-governing settings.
- the current `File download priority` article still says prioritization only governs the active queue, has a 50k-file cap, can suspend lower-priority work, still has internal exceptions, and may not be reflected by visible queue order.
- the current `Out of memory` article still says the whole tree and deleted state live in memory/database and that shrinking memory use may require removing a large share and re-adding it.
- the current `Some internal tasks are taking time to complete` article still says hidden read/hash/merge/write work can be the real cause of slow progress.

That candor is useful.
The resource contract is the problem.
AnonSync should not clone a world where the operator still needs article memory to know whether the bottleneck is policy, preemption, queue saturation, disk pressure, memory scale, or hidden internal work.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful distinctions between bandwidth limits, scheduler pauses, queue priority, hidden work, and memory pressure are real, but the present contract still hides too much meaning across preferences, power-user settings, queue docs, and troubleshooting prose instead of owning resource budget as one stable page family.**

## Revision addendum — raw-state clone boundary, reviewed successor capsules, and seat rebirth proof

This revision continues directly from `rev0312` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **unsupported Sync cloning, storage-folder contents, per-install certificate identity, and identity replacement via unlink/regenerate**.
2. Tightens the non-clone line again: borrow Resilio's blunt honesty that opaque app-state or disk-image cloning is dangerous; refuse any contract where the operator still has to reconstruct `is this a safe replacement, a stale backup, or a dangerous duplicate seat?` from cloning warnings plus scattered storage and identity docs.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio successor/restore/cloning truth is still too blunt to clone even though the warning itself is useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: successor capsule contract sheet, state adoption review, duplicate seat collision warning, successor activation proof, and state lineage receipt.
5. Makes one hard product decision explicit: **raw state cloning is never the normal continuity path**.
6. Makes another hard product decision explicit: **replacement-seat carry-forward must use a reviewed successor artifact rather than opaque copied state**.
7. Makes a third hard product decision explicit: **seat rebirth and subject carry-forward are separate truths and must be receipted separately**.
8. Packages the result as another continuation archive whose new tranche makes the `raw-clone / cold-successor / stale-backup / duplicate-seat / reborn-seat-proof` seam explicit in the reading order and page family.

## Revision addendum — invocation profile, launch truth, and runtime-world proof

This revision continues directly from `rev0311` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **Windows CLI launch switches, Linux/headless launch args, config-mode storage authority, service storage worlds, loopback-vs-LAN WebUI exposure, and update continuity for non-default launches**.
2. Tightens the non-clone line again: borrow Resilio's candor that launch flags and storage roots materially change runtime truth; refuse any contract where the operator still has to reconstruct `what world am I actually starting?` from CLI help, Linux notes, config-mode notes, service troubleshooting, and update instructions.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio invocation-profile truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: invocation profile contract sheet, launch review, quiet-runtime proof, launch world preview, and invocation lineage receipt.
5. Makes one hard product decision explicit: **launch intent becomes a first-class reviewed object whenever it can change world lineage, visibility truth, or control exposure**.
6. Makes another hard product decision explicit: **quietness, backgrounding, and browser-open control are separate truths from state-root continuity**.
7. Makes a third hard product decision explicit: **storage-root selection is state adoption, not a cosmetic convenience knob**.
8. Packages the result as another continuation archive whose new tranche makes the `invocation-profile / world-lineage / quiet-runtime-proof / launch-world-preview / durable-receipt` seam explicit in the reading order and page family.

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


## Revision addendum — time authority, timestamp provenance, and replay chronology

This revision continues directly from `rev0306` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **time-difference handling, GMT-based file ordering, skew-budget settings, database-only mtime fallback, archive-restore chronology, and internal-clock dependence across desktop/mobile guides**.
2. Tightens the non-clone line again: borrow Resilio's candor that chronology really depends on time and `mtime`; refuse any contract where the operator still has to reconstruct `which timestamp actually governs right now?` from warnings, power-user settings, and archive notes.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio time-authority truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: temporal authority contract sheet, clock-skew/time-authority review, timestamp provenance proof, replay chronology review, and temporal lineage receipt.
5. Makes one hard product decision explicit: **filesystem-visible time and chronology-authoritative time are separate truths when assignment or clock trust degrades**.
6. Makes another hard product decision explicit: **archive replay is chronology-sensitive and cannot masquerade as simple file copy**.
7. Makes a third hard product decision explicit: **skew budget, timezone fault, and ledger-only fallback are first-class operator facts**.
8. Packages the result as another continuation archive whose new tranche makes the `time-authority / disk-vs-ledger-mtime / skew-review / replay-chronology / durable-receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present time-authority contract**

This time the reason is especially clear around **GMT-normalized mtime ordering, 600-second skew budgets, database-only authoritative mtime, and archive restore candidates that can be re-archived if replay timing is wrong**.
Current official materials simultaneously show that:

- the `Time difference` article still says Sync decides which file is newer by comparing **files modification time**, converting it to **GMT**, and warning once peer time difference exceeds the allowed threshold.
- the current `Power user preferences` table still says `sync_max_time_diff` defaults to **600 seconds** and that if `ignore_mtime_assign_errors` is used after mtime assignment failures, Sync can keep the **correct mtime only in the database** while the visible disk timestamp becomes **current time**.
- the current `Using Archive for file versioning and restoring deleted files` article still says restored files come back with an **older modified timestamp** than that on other peers, and that restoring while Sync is not running can cause the file to be re-detected later and moved back to Archive as older.
- the current desktop and mobile sync guides still remind operators that Sync relies on the **internal clock** of each device and that wrong time or timezone causes `Excessive time difference` behavior.

That candor is useful.
The time-authority contract is the problem.
AnonSync should not clone a world where the operator still has to remember whether `modified on disk`, `authoritative in the database`, `restored from Archive`, and `peer clock looks okay` are all the same temporal truth.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful timestamp and chronology distinctions are real, but the present contract still hides too much meaning inside time-difference warnings, power-user mtime settings, archive-restore notes, and onboarding tips instead of owning time authority as one stable page family.**

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

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful completion/freshness distinctions are real, but the present contract still hides too much meaning inside status UI notes, troubleshooting pages, background-task docs, detection-latency docs, and old changelog lineage instead of owning completion truth as one stable page family.**

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

1. Re-checks another current official Resilio cluster around **file-system permission synchronization, NTFS/POSIX mode families, create-time-fixed permission policy in Synchronization / Hybrid Work / File Caching jobs, runtime-principal requirements, target identity mapping, pre-seeded ownership ambiguity, and explicit permission-application error codes**.
2. Tightens the non-clone line again: borrow Resilio's candor that permission metadata is operationally real; refuse any contract where the operator still has to reconstruct permission truth from job-profile tables, runtime-principal lore, cross-platform caveats, and troubleshooting pages.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio permission-metadata truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: metadata authority contract sheet, permission sync review, principal mapping proof, permission failure review, and metadata lineage receipt.
5. Makes one hard product decision explicit: **byte truth and metadata truth are separate axes** rather than one silent `healthy` state.
6. Makes another hard product decision explicit: **runtime principal and target identity mapping are part of the permission contract** rather than hidden prerequisites.
7. Makes a third hard product decision explicit: **cross-platform preservation, native apply, local inheritance rewrite, and bytes-only continuation are different postures that require different receipts**.
8. Packages the result as another continuation archive whose new tranche makes the `metadata-authority / principal-proof / mapping-ceiling / permission-failure / durable-receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present permission-metadata contract**

This time the reason is especially clear around **create-time-fixed permission policy, NTFS mode families, Local System vs Domain Admin requirements, cross-platform preservation without native application, and concrete target identity-mapping failures**.
Current official materials simultaneously show that:

- `Syncing file system permissions` still says Resilio Active Everywhere can synchronize Standard and Special NTFS permissions as well as POSIX.1 permissions; that Synchronization, Hybrid Work, and File Caching jobs lock those permission-sync settings at creation time; that NTFS permission modes differ materially (`Don't sync Owner`, `Sync full ACL`, `Re-apply local inherited permissions`); that full-owner application can require same-domain operation plus Domain Admin while lighter NTFS permission syncing still needs Local System; that non-NTFS targets may preserve NTFS permissions and apply them only later when files land on NTFS storage; and that pre-seeded RW-to-RW merges can scramble ownership without a Reference Agent.
- `Connect Agent cannot set file permission` still says concrete failures reduce to missing privileges for NTFS application or missing same-ID / same-name user-group mappings for POSIX application.
- Current Synchronization and Hybrid Work job docs still show permission-affecting profile selection and per-agent posture as part of job creation rather than one late repair toggle.

That candor is useful.
The permission-metadata contract is the problem.
AnonSync should not clone a world where the operator still has to remember whether `permission sync on` means fully applied now, preserved for later, rewritten to local inheritance, or blocked by runtime principal and target mapping.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful permission-metadata distinctions are real, but the present contract still hides too much meaning inside feature docs, job-class docs, runtime-principal requirements, and troubleshooting pages instead of owning metadata truth as one stable page family.**

## Revision addendum — removal verbs, residue planes, and non-final disappearance

This revision continues directly from `rev0300` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **disconnecting folders, reconnect path drift, linked-device removal, disconnected-folder scope, selective-sync placeholder removal, `Remove from this device`, placeholder deletion that can propagate globally, power-user removal guards, hidden offline devices, and uninstall residue**.
2. Tightens the non-clone line again: borrow Resilio's candor that `remove` is not one thing; refuse any contract where the operator still has to reconstruct whether a remove-like verb changes the seat roster, the subject registry, local bytes, global bytes, or only visibility.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio removal truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: removal contract sheet, removal intent disambiguation, device-local eviction boundary, identity-wide removal and remote remainder review, and removal lineage receipt.
5. Makes one hard product decision explicit: **remove-like verbs are typed operations**. `disconnect`, `remove from this device`, `remove from linked seats`, `delete for reachable peers`, `hide`, `unlink`, and `uninstall` are not styling variants.
6. Makes another hard product decision explicit: **residue truth is part of the action contract**. A remove preview must show what survives locally, remotely, and latently.
7. Makes a third hard product decision explicit: **reconnect and comeback risk belong inside removal workflows**. Default-path drift, sibling-branch creation, hidden-seat reappearance, and uninstall residue are not aftercare footnotes.
8. Packages the result as another continuation archive whose new tranche makes the `typed-removal / residue-plane / comeback-risk / remote-remainder / durable-receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present removal contract**

This time the reason is especially clear around **disconnect vs remove, local placeholder reversion vs global placeholder deletion, linked-identity scope vs outside peers, hide-vs-unlink, and uninstall residue**.
Current official materials simultaneously show that:

- `Disconnecting and Removing Folders` still says disconnect affects one device, can leave the folder in the file system, removes placeholders if Selective Sync was enabled, and later reconnect may propose a different default path that can create a new `(1)` directory unless the operator manually rebinds the old path.
- The same article still says removing a folder from linked devices stops showing it on devices linked to that identity, but the folder can still remain on remote devices outside that linked identity.
- `Folder Types and Management` still says disconnected folders may have no local path at all and that removing a disconnected folder removes it from all linked devices.
- `Selective Sync` still warns that removing a Selective Sync share removes all placeholders from the local file system.
- `What Is an RSLS File?` still says `Remove from this device` reverts a file or subfolder to a placeholder locally, while deleting a placeholder with Read & Write access can remove it from all peers.
- `Power user preferences` still says `disable_remove_from_all_devices` can hide that destructive path for Selective Sync shares, but the same preference is ignored in Linux WebUI; it also still exposes `recreate_placeholders_on_removal`, proving that local placeholder behavior is separately configurable.
- `How to clear offline devices?` still says hiding a device only removes it from view and it can reappear later.
- `How to uninstall Sync?` still says uninstall is not subject deletion, desktop uninstall can leave ordinary shared folders and `.sync/Archive` behind, and iOS removes synced files from the device on uninstall.

That candor is useful.
The removal contract is the problem.
AnonSync should not clone a world where the operator still has to remember whether `remove` means detaching a subject here, deleting bytes for everyone, hiding a seat from view, or merely uninstalling the runtime while residue survives.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful removal distinctions are real, but the present contract still hides too much meaning inside disconnect docs, placeholder docs, hidden-device cleanup, uninstall instructions, and power-user notes instead of owning typed removal as one stable page family.**

## New documents in rev0301

- `946` Resilio removal verb taxonomy and residue-plane fragmentation evaluation
- `947` Removal contract sheet page
- `948` Removal intent disambiguation page
- `949` Device-local eviction boundary page
- `950` Identity-wide removal and remote remainder review page
- `951` Removal lineage receipt page

## Revision addendum — identity linking, certificate takeover, and unlink-boundary clarity

This revision continues directly from `rev0299` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **Sync Private Identity / My Devices**, certificate generation, M-key-driven linking, version-mixed identity conflicts, certificate takeover when linking already-running devices, Advanced-folder eviction, iOS filesystem deletion risk, local-only unlink, and hidden-offline-device residue.
2. Tightens the non-clone line again: borrow Resilio's candor that linking devices is not just a friendly pairing flow; refuse any contract where the operator still has to reconstruct seat adoption, certificate replacement, folder fate, and residue from one getting-started page plus a separate offline-device article.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio identity-link / device-adoption truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: identity merge contract sheet, identity adoption review, certificate takeover impact page, unlink and hidden-device boundary page, and identity merge receipt.
5. Makes one hard product decision explicit: **identity linking is a first-class adoption contract**. `scan QR`, `paste key`, `pair device`, `take over certificate`, and `inherit all configured shares` are not interchangeable answers.
6. Makes another hard product decision explicit: **seat lineage and subject lineage remain separate truths**. A seat can adopt another identity without that being a casual subject-level reconnect.
7. Makes a third hard product decision explicit: **hide is not unlink and offline residue is not revocation**. If a dormant linked device can reappear and resume ordinary continuity, the product must say so plainly.
8. Packages the result as another continuation archive whose new tranche makes the `seat adoption / certificate takeover / folder fate / unlink boundary / latent residue / durable receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present identity-link contract**

This time the reason is especially clear around **version-mixed linking, certificate takeover, Advanced-folder eviction, iOS deletion risk, local-only unlink, and hidden offline-device residue**.
Current official materials simultaneously show that:

- `Sync Private Identity & Linking My Devices` still says every installation gets its own digital certificate, linked devices inherit all folders automatically, and if device2 links to device1 using device1's `M` key then device2 takes device1's identity name, fingerprint, and configured shares.
- The same current article still warns not to link v2 and v3 devices under one identity because license and share configuration can conflict badly enough to lose UI/share access.
- The same current article still warns that linking two devices which are already running Sync can cause one to lose its certificate, remove all Advanced folders from the app on the adopting device, and on iOS remove those Advanced folders from the filesystem as well.
- The same current article still says you cannot remotely unlink other devices.
- `How to clear offline devices?` still says clearing only hides a device; it does not unlink it, and the device reappears if it ever comes back online.
- `What's the difference between Standard and Advanced folders?` still says `My Devices` and certificate-aware peer identity are features of Advanced/PKI-style folders rather than the generic raw-key model.

That candor is useful.
The identity-link contract is the problem.
AnonSync should not clone a world where the operator still has to remember whether a `link device` action is really seat adoption, certificate replacement, share inheritance, subject eviction, or merely a cosmetic list entry.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful seat-adoption truths are real, but the present contract still hides too much meaning inside an identity guide, an offline-device cleanup article, and architecture notes instead of owning identity merge as one stable page family.**

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

## Revision addendum — activation latency, proof-of-effect, and non-retroactivity truth

This revision continues directly from `rev0294` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **IgnoreList reread timing, scheduled and manual rescans, restart-required FileDelayConfig edits, debug/profiler activation, and power-user timing controls**.
2. Tightens the non-clone line again: borrow Resilio's candor that some changes become real immediately, some only after reread or restart, and some are future-only; refuse any contract where the operator still has to reconstruct that from support articles and hidden-file ritual.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio activation truth is still too fragmented to clone even though the underlying distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: effect activation contract sheet, activation latency review, pending effect watch, policy effect verification, and activation lineage receipt.
5. Makes one hard product decision explicit: **saved-state, live-state, and proven-effect are different first-class truths**.
6. Makes another hard product decision explicit: **every meaningful change declares its activation class**. `immediate`, `next-reread`, `next-rescan`, `next-restart`, `next-startup`, `external-proof-needed`, and `future-only` are not support-only lore.
7. Makes a third hard product decision explicit: **retroactivity is explicit**. A future-only rule never silently masquerades as having repaired historical material.
8. Packages the result as another continuation archive whose new tranche makes the `saved / staged / live / proven / future-only / superseded` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present activation contract**

This time the reason is especially clear around **reread timing, rescans, restart gates, and non-retroactive rule effect**.
Current official materials simultaneously show that:

- `Ignoring files in Sync (Ignore List)` still says IgnoreList is reread on change or every `folder_rescan_interval` when notifications are absent, still recommends restart for immediate application, and still says it does not affect files that already synced.
- the same current IgnoreList article still says already-indexed directory structure continues to be stored and passed to peers until disconnect.
- `How soon does synchronization start?` still says scheduled rescan runs every 600 seconds and on Sync start, and that `folder_rescan_interval = 0` disables rescans even upon restart.
- `Setting Delay Time For Syncing` still says `FileDelayConfig` lives in the storage folder, is edited as JSON, defaults listed file classes to a 10-second delay, and requires restart after edits.
- `Collecting debug logs manually` still says debug logging should be followed by restart to make sure it is enabled and that collection should run for at least 15 minutes.
- `Power user preferences` still says `profiler_enabled` requires restart to activate, while separately publishing `folder_rescan_interval`, `config_refresh_interval`, and `config_save_interval`.
- the live v3 line still runs through `3.1.2.1076`.

That candor is useful.
The activation contract is the problem.
AnonSync should not clone a world where the operator still has to remember whether a change is immediate, reread-bound, rescan-bound, restart-bound, or future-only — and where `saved`, `live`, and `historically corrected` are too easy to confuse.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful timing truths are real, but the present activation contract still hides too much meaning inside hidden-file edits, restart rituals, rescan cadence, and non-retroactivity notes instead of owning effect timing as one stable page family.**

## New documents in rev0295

- `910` Resilio activation latency, reread/restart, and non-retroactivity fragmentation evaluation
- `911` Effect activation contract sheet page
- `912` Activation latency review page
- `913` Pending effect watch page
- `914` Policy effect verification page
- `915` Activation lineage receipt page


## Revision addendum — automatic ingress mutation, router-side-effect warnings, and port-lease truth

This revision continues directly from `rev0293` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **listening-port semantics, UPnP/NAT-PMP auto-mapping, manual forwarding expectations, configuration-mode ownership, and direct-path troubleshooting advice**.
2. Tightens the non-clone line again: borrow Resilio's candor that easier directness can require explicit or automatic ingress work; refuse any contract where the operator still has to reconstruct router mutation and mapping truth from preferences prose, architecture pages, and troubleshooting notes.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio automatic-ingress truth is still too fragmented to clone even though the underlying distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: ingress mutation contract sheet, auto port-map review, mapping lease watch, router-side-effect warning, and ingress mutation receipt.
5. Makes one hard product decision explicit: **automatic port mapping is a reviewed network-edge mutation, not a convenience toggle**.
6. Makes another hard product decision explicit: **lease truth belongs to the product**. `enabled`, `requested`, `observed`, `stale`, and `cleared` are different first-class states.
7. Makes a third hard product decision explicit: **router-side collateral risk stays adjacent to apply**. Infrastructure-facing caution is not buried in a support note.
8. Packages the result as another continuation archive whose new tranche makes the `auto-map request / port basis / widened audience / lease freshness / accepted infrastructure risk / durable receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present automatic-ingress contract**

This time the reason is especially clear around **UPnP/NAT-PMP mapping, listening-port truth, and router-side collateral effects**.
Current official materials simultaneously show that:

- `Sync Preferences` still says the listening port is used for incoming/outgoing UDP and incoming TCP, that manual forwarding should target that same port, and that `Use UPnP port mapping` makes Sync send UPnP and NAT-PMP packets to the router automatically.
- the same article still warns that some printers, scanners, and other network equipment may mis-handle those UPnP packets and stop processing network requests.
- `What ports and protocols are used by Sync?` still says direct connection depends on the listening port being opened and forwarded through firewalls, NATs, and routers after discovery and before relay fallback.
- `Running Sync in configuration mode` still keeps the `upnp` field, listening port, proxy, WebUI, and shared-folder ownership in one startup-owned config plane.
- `Download/upload speed is very slow` still treats open listening port and direct port mapping as practical remedies for relay dependence.

That candor is useful.
The automatic-ingress contract is the problem.
AnonSync should not clone a world where the operator still has to reconstruct, from several pages and router folklore, whether a local-looking checkbox requested network-edge mutation, what inbound audience widened, whether the mapping is only allowed or actually observed, and what collateral network risk was accepted.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful truths are real, but the present automatic-ingress contract still hides too much network-edge mutation meaning inside preferences prose, config notes, and troubleshooting lore instead of owning port-mapping truth as one stable page family.**

## New documents in rev0294

- `904` Resilio auto-ingress mutation, router-side-effect, and port-lease fragmentation evaluation
- `905` Ingress mutation contract sheet page
- `906` Auto port-map review page
- `907` Mapping lease watch page
- `908` Router-side-effect warning page
- `909` Ingress mutation receipt page

## Revision addendum — projection-stable rename verbs, plane-explicit actions, and cross-projection receipts

This revision continues directly from `rev0291` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **desktop custom share names, local filesystem rename, Android share rename behavior, iOS share rename wording, and outward link/QR relabeling**.
2. Tightens the non-clone line again: borrow Resilio's candor that different projections can expose different rename powers; refuse any contract where the operator still has to know which client they are standing in to know what `rename` means.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio action-verb semantics are still too projection-dependent to clone even though the underlying distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: action verb contract sheet, rename intent disambiguation, projection semantic gap review, cross-projection rename preview, and action lineage receipt.
5. Makes one hard product decision explicit: **button labels are not enough**. Every serious rename-like action resolves to a typed verb family before apply.
6. Makes another hard product decision explicit: **projection may narrow capability, but may not silently change semantics**. A familiar pencil icon cannot carry hidden plane drift.
7. Makes a third hard product decision explicit: **receipts preserve projection witness**. Later operators must not need device-memory folklore to interpret what changed.
8. Packages the result as another continuation archive whose new tranche makes the `same-looking control / different plane effect / projection witness / durable receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present action-verb contract**

This time the reason is especially clear around **projection-dependent rename semantics**.
Current official materials simultaneously show that:

- `Setting custom name for sync shares` still says a desktop custom name is applied only in Sync UI, does not rename the folder on disk, and does not propagate to other peers or linked devices.
- the same article still says a different outward label can be inserted into a link or QR during sharing while the underlying share name remains unchanged.
- `Can I move or rename a syncing folder?` still says filesystem rename affects only the local device.
- `Sync interface on Android` still says the share-name pencil renames both in Sync and in the filesystem.
- `Sync Interface on iOS devices` still says the share-name pencil lets you rename the share, while leaving the exact plane effect less explicit than Android.

That candor is useful.
The action-verb contract is the problem.
AnonSync should not clone a world where the operator still has to remember which projection owns local alias rename, filesystem rename, canonical retitle, or outward artifact relabel before trusting what a familiar-looking `rename` control will do.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful distinctions are real, but the present-day action contract still hides too much plane meaning inside projection-specific rename affordances and support-article memory instead of owning rename semantics as one stable page family.**

## New documents in rev0292

- `892` Resilio projection rename semantic split and action-verb fragmentation evaluation
- `893` Action verb contract sheet page
- `894` Rename intent disambiguation page
- `895` Projection semantic gap review page
- `896` Cross-projection rename preview page
- `897` Action lineage receipt page

## Revision addendum — name provenance, recipient-label issuance, and stale-alias residue

This revision continues directly from `rev0290` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **desktop-only custom share names, local-only disk renames, issuance-time link/QR labels, and alias residue that survives disconnect until explicit reset**.
2. Tightens the non-clone line again: borrow Resilio's candor that one sync subject can honestly wear several names for several audiences; refuse any contract where the operator still has to reconstruct current naming truth from local basename, local alias, issued-artifact label, and stale residue.
3. Adds one new **Resilio evaluation** document focused on why the present-day Resilio naming answer is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: naming provenance sheet, name mutation preview, recipient-label issuance, alias drift watch, and name lineage receipt.
5. Makes one hard product decision explicit: **every visible serious label carries plane and audience provenance**. A naked label is not enough.
6. Makes another hard product decision explicit: **issuance-time recipient labels are first-class artifacts**. They are never treated as silent canonical subject renames.
7. Makes a third hard product decision explicit: **disconnect leaves residue, not truth**. A surviving local alias after continuity break must badge itself as stale or residue.
8. Packages the result as another continuation archive whose new tranche makes the `current render / rename preview / recipient-facing label / stale alias / naming receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present naming contract**

This time the reason is especially clear around **desktop custom names, local-only path renames, link/QR label insertion, and disconnect residue**.
Current official materials simultaneously show that:

- `Setting custom name for sync shares` still says Sync UI names normally mirror folder names on disk, while desktop custom names can diverge from disk names.
- the same article still says a custom UI name does not rename the folder on disk, does not propagate to linked devices, and can still be changed during sharing so a different label is inserted into a link or QR code.
- the same article still says disconnecting such a share can leave the custom name in the UI until explicit `Reset`.
- `Can I move or rename a syncing folder?` still says renaming a syncing folder affects only the local device and does not update other devices.

That candor is useful.
The naming contract is the problem.
AnonSync should not clone a world where the operator still has to reconstruct, from several tips and FAQs, whether a visible label is canonical subject identity, local alias, disk basename, outward-artifact label, or stale residue surviving past disconnect.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful truths are real, but the present-day naming contract still hides too much audience and provenance meaning inside local UI aliases, share-view issuance tricks, filesystem rename behavior, and stale post-disconnect residue instead of owning naming truth as one stable page family.**

## New documents in rev0291

- `886` Resilio name provenance, recipient-label issuance, and alias-residue fragmentation evaluation
- `887` Naming provenance sheet page
- `888` Name mutation preview page
- `889` Recipient-label issuance page
- `890` Alias drift watch page
- `891` Name lineage receipt page

## Revision addendum — effective policy provenance, sticky-override refusal, and config-plane ownership

This revision continues directly from `rev0289` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **per-share Folder Preferences, Power user standing defaults, file-priority inheritance behavior, linked-device default connect modes, and configuration-mode ownership / override semantics**.
2. Tightens the non-clone line again: borrow Resilio's candor that effective policy can come from several real planes; refuse any contract where the operator still has to reconstruct current truth from share preferences, defaults, config files, and sticky exceptions.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio policy-origin truth is still too fragmented to clone even though the underlying distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: effective policy sheet, policy change preview, inheritance return review, policy drift watch, and policy provenance receipt.
5. Makes one hard product decision explicit: **every effective policy field carries provenance**. A resolved value without origin is not enough.
6. Makes another hard product decision explicit: **`return to default` must really rejoin inheritance**. AnonSync will not keep a hidden sticky override behind a neutral label.
7. Makes a third hard product decision explicit: **config-plane ownership stays visible**. A config-owned subject cannot pretend to be UI-owned truth.
8. Packages the result as another continuation archive whose new tranche makes the `effective policy / origin plane / drift / true rejoin` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present policy-origin contract**

This time the reason is especially clear around **per-share preferences, standing defaults, link-time modes, and configuration-plane ownership**.
Current official materials simultaneously show that:

- `Folder Preferences` still owns per-share controls such as Archive, read-only overwrite behavior, relay, tracker, LAN search, predefined hosts, and file download priority.
- `Power user preferences` still publishes standing defaults and switches such as `disable_remove_from_all_devices`, including platform caveats like `Ignored in Linux WebUI`.
- `File download priority` still says a global `folder_defaults.transfer_priority` can apply to existing and new shares, while a share with a manually changed priority stops inheriting later global changes even if manually set back to `None`.
- `Selective Sync`, `Synchronization Modes`, and `Sync Private Identity & Linking My Devices` still spread mode truth across connect-time choice, post-connect change, and linked-device defaults.
- `Running Sync in configuration mode` still says advanced preferences can be injected through config, that only Standard folders can be set up there, and that configured shared folders override previously added WebUI folders while disabling WebUI for that case.

That candor is useful.
The policy-origin contract is the problem.
AnonSync should not clone a world where the operator still has to reconstruct, from several planes and caveats, whether a field is inherited, locally overridden, config-owned, future-only, or merely pretending to have returned to default.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful truths are real, but the present-day policy contract still hides too much source-of-truth meaning inside separate preference planes, startup configuration, and sticky exceptions instead of owning effective policy as one stable page family.**

## New documents in rev0290

- `880` Resilio policy-origin, sticky-override, and config-plane fragmentation evaluation
- `881` Effective policy sheet page
- `882` Policy change preview page
- `883` Inheritance return review page
- `884` Policy drift watch page
- `885` Policy provenance receipt page

## Revision addendum — authority policy, delegation boundaries, and retained-material revocation truth

This revision continues directly from `rev0288` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **Standard vs Advanced folder permissions, Owner vs non-Owner delegation, linked-device Owner semantics, on-the-fly vs reissue-based permission change, one-way sync breakage, and local-share narrowing / auto-lowering rules**.
2. Tightens the non-clone line again: borrow Resilio's candor that read, write, delegate, revoke, and derivative-local narrowing are materially different truths; refuse any contract where the operator still has to reconstruct those truths from folder family, identity family, and share caveats.
3. Adds one new **Resilio evaluation** document focused on why the present-day Resilio permission / delegation / revocation answer is still too fragmented to clone even though the underlying truths are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: authority contract, permission change preview, delegation boundary review, revocation impact, and authority policy receipt.
5. Makes one hard product decision explicit: **authority policy is a first-class object**. The operator should not have to infer the live contract from artifact family alone.
6. Makes another hard product decision explicit: **live mutation and reissue are different verbs**. The product must say whether a requested permission change edits an existing policy or requires successor issuance / reconnection.
7. Makes a third hard product decision explicit: **revocation always publishes retained-material truth**. `Future updates stop` and `already-held bytes remain` must stay adjacent.
8. Packages the result as another continuation archive whose new tranche makes the `grant class / delegation boundary / revocation residue` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present permission contract**

This time the reason is especially clear around **Standard vs Advanced folder semantics, linked-device ownership, revocation residue, and local-derivative narrowing**.
Current official materials simultaneously show that:

- `Sync functionality in detail` and `User Management` still say `Owner` can share, change permissions, and revoke access, while revoking cuts off future updates but does not remove already synchronized files.
- `What's the difference between Standard and Advanced folders?` still says Standard folders do not have an Owner concept, any peer can share the key it has, and changing permissions is not on-the-fly there because the share must be removed and re-added with a new key.
- `How to create a Read Only folder while syncing across linked devices?` and `Is one-way synchronization possible?` still say linked devices under one identity act as Owners, so achieving a read-only linked-device posture requires stepping out of the linked-device grammar and using a Standard-folder key instead.
- `Sharing a folder locally` still says a local derivative cannot receive Owner, cannot exceed source permissions, may need re-sharing to change access, and auto-lowers if the source seat is downgraded.

That candor is useful.
The policy contract is the problem.
AnonSync should not clone a world where the operator still has to reconstruct, from several docs and share families, whether a seat may delegate, whether a permission change is live or requires reissue, what revocation actually leaves behind, and whether a local derivative is merely narrower or already orphaned.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful truths are real, but the present-day permission contract still hides too much governance inside folder-family distinctions, linked-seat exceptions, and derivative-share caveats instead of owning authority policy as one stable page family.**

## New documents in rev0289

- `874` Resilio permission family, delegation, and revocation fragmentation evaluation
- `875` Authority contract page
- `876` Permission change preview page
- `877` Delegation boundary review page
- `878` Revocation impact page
- `879` Authority policy receipt page

## Revision addendum — artifact-family inspection, token-opacity refusal, and epoch-fork warning

This revision continues directly from `rev0287` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **raw key families, approval-bearing web links, temporary-key link flow, identity-link `M` keys, share-dialog expiry/use budgets, and key-change epoch fork behavior**.
2. Tightens the non-clone line again: borrow Resilio's candor that keys, links, encrypted-custody artifacts, and seat-link artifacts are materially different; refuse any contract where too much authority meaning still lives inside opaque tokens and support prose.
3. Adds one new **Resilio evaluation** document focused on why present-day token-family truth and key-rotation fork truth are still too scattered and too opaque to clone directly.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: capability artifact, issuance preview, incoming artifact intake, artifact rotation / fork warning, and artifact issuance receipt.
5. Makes one hard product decision explicit: **artifact family must be inspectable before use**. A pasted token is never the only explanation of rights.
6. Makes another hard product decision explicit: **seat-link artifacts and subject-access artifacts never share one flattened grammar**. `join my device family` and `join this subject` are different contracts.
7. Makes a third hard product decision explicit: **rotation is an epoch event**. Replacing a live artifact must preview surviving old cohorts, successor issuance, and retirement order.
8. Packages the result as another continuation archive whose new tranche makes the `artifact family / intake semantics / successor fork` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's opaque artifact contract**

This time the reason is especially clear around **raw key families, temporary-key links, certificate-backed approval, and key-change fork behavior**.
Current official materials simultaneously show that:

- `Key structure and flow` still says only Standard folders use raw keys, that the first key character encodes materially different types (`A`, `B`, `D`, `E`, `F`, `M`), that `F` is ciphertext-only custody, and that `M` is an identity-link artifact.
- the same current article still says key change is not distributed automatically and that old-key peers keep syncing with each other after one peer changes key.
- `Link structure and flow` still says share links carry a temporary key in the hash fragment, that the browser landing page is only a carrier shell, that the claimant sends a locally generated public key, and that approval mints an X509 certificate plus ACL entry before access becomes live.
- `Sync Share Dialog (Desktop)` still says links and keys differ materially because keys do not use the approval mechanism, and still keeps expiry and use-budget semantics inside the issuance flow.
- `Sync Private Identity & Linking My Devices` still says an `M`-key path can take over another device's identity, fingerprint, and configured shares, which proves that a seat-link artifact is not just another folder invite.

That candor is useful.
The operator contract is still too opaque.
AnonSync should not clone a world where the operator still has to infer from token prefixes, browser wrappers, and separate support notes whether the thing in hand is a bearer-style raw key, an approval-bearing invite, a seat-link artifact, a ciphertext-custody capability, or a successor artifact that will fork continuity.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful truths are real, but the present-day artifact contract still hides too much governance inside opaque tokens and still treats rotation/fork truth too much like implementation detail instead of one owned workflow.**

## New documents in rev0288

- `868` Resilio artifact family, token opacity, and epoch fork evaluation
- `869` Capability artifact page
- `870` Issuance preview page
- `871` Incoming artifact intake page
- `872` Artifact rotation / fork warning page
- `873` Artifact issuance receipt page


## Revision addendum — residency intent, sticky priority overrides, and queue-vs-guarantee truth

This revision continues directly from `rev0286` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **file download priority in Sync 3.1.0, global-vs-share priority defaults, sticky manual override behavior, Selective Sync / `.rsls` placeholder semantics, placeholder-removal semantics, Linux-WebUI guard mismatches, and ghost/no-source warnings**.
2. Tightens the non-clone line again: borrow Resilio's candor that queue order, placeholders, later-arrival behavior, and source availability are real operator truths; refuse any contract where the ordinary question `will this actually become local, stay local, and with what guarantee?` still depends on several help pages and surface exceptions.
3. Adds one new **Resilio evaluation** document focused on why the present-day Resilio priority/residency contract is still too fragmented to clone even though the underlying product truths are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: residency intent, residency policy review, residency budget, hydration queue admission, and residency promise receipt.
5. Makes one hard product decision explicit: **priority is never itself a residency promise**. `go first` and `guaranteed local` are different objects.
6. Makes another hard product decision explicit: **neutral/default means inherit again**. Returning a subject to neutral may not preserve a sticky hidden local override.
7. Makes a third hard product decision explicit: **residency promises must publish a guarantee class** — at minimum `preview-only`, `queued-best-effort`, `guaranteed-local-now`, or `guaranteed-local-for-future-descendants`.
8. Packages the result as another continuation archive whose new tranche makes the `priority / residency guarantee / ghost-risk` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present priority/residency contract**

This time the reason is especially clear around **download priority, placeholder semantics, and source-availability risk**.
Current official materials simultaneously show that:

- `File download priority` is now a first-class feature in Sync `3.1.0`, with both share-local and global defaults, active-queue limits, suspension behavior, internal exceptions, queue rebuilds, and a separate rule for single-file sending.
- the same article says a share with manually altered priority stops inheriting later global changes **even if later set back to `None`**.
- `Synchronization Modes`, `Selective Sync`, and `What Is an RSLS File?` still say placeholders are names-only byte absence, that syncing a subtree can opt later descendants into local download, and that `Remove from this device` versus `Remove from all devices` are materially different actions.
- `Selective Sync` and `Disconnecting and Removing Folders` still warn that removing or disconnecting a selective-sync share removes placeholders from the filesystem on that device.
- `Power user preferences` still publish both `folder_defaults.transfer_priority` and guardrail switches such as `disable_remove_from_all_devices` and `recreate_placeholders_on_removal`, while also saying at least one destructive guard is ignored in Linux WebUI.
- `Cannot download files / ... no source peers online` still says some announced items are ghost files that nobody retains in full anymore.

That candor is useful.
The promise contract is the problem.
AnonSync should not clone a world where the operator still has to reconstruct, from several docs and settings, whether a subject is merely visible, merely queued, likely to hydrate, guaranteed to become local, guaranteed to remain local for later descendants, or already doomed by lack of a surviving full-copy witness.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful truths are real, but the present-day operator contract still splits queue order, inheritance behavior, placeholder semantics, destructive-remove meaning, and no-source risk across several pages instead of owning them as one residency grammar.**

## New documents in rev0287

- `862` Resilio priority, residency, and placeholder-promise fragmentation evaluation
- `863` Residency intent page
- `864` Residency policy review page
- `865` Residency budget page
- `866` Hydration queue admission page
- `867` Residency promise receipt page


## Revision addendum — trust-bootstrap blocks, rescue-first export, and one-shot destructive execution

This revision continues directly from `rev0285` and does nine concrete things:

1. Re-checks another current official Resilio cluster around **Windows service/browser control, Linux install modes and product-line compatibility, public Sync download warnings, WebUI/browser-trust bootstrap, and Android per-share destructive toggles**.
2. Tightens the non-clone line again: borrow Resilio's candor that browser/service control is real, install path and product line matter, and destructive controls appear on multiple surfaces; refuse any contract where operators must still splice install notes, browser-warning folklore, and per-surface overwrite toggles into one mental model.
3. Adds one new **Resilio evaluation** document focused on how current official materials still scatter the ordinary dangerous-control answer across install, service, product-line, browser-trust, desktop, and mobile surfaces.
4. Adds five new **interface specs** for the missing workflow-owned surfaces in this pass: danger session capsule, trust bootstrap review, salvage export, salvage export receipt, and destructive execution ticket.
5. Makes one hard product decision explicit: **bootstrap trust exception is never sufficient for destructive commit**. It may permit observation and review; it does not unlock destructive approval or destructive execution.
6. Makes another hard product decision explicit: **`Approve after export` must become a first-class export object and receipt**, not an implied promise that the operator remembers later.
7. Makes a third hard product decision explicit: **destructive approval is never sticky remembered consent**. It compiles into a freshness-bound, scope-bound, one-shot execution ticket.
8. Refreshes the core doctrine documents actually touched in this pass — README, status, evaluation, borrow-line scorecard, clone-veto, product direction, interface rules, pattern language, architecture decisions, roadmap, sources, and the new page family — so the tranche is integrated rather than floating.
9. Packages the result as another continuation archive whose new tranche makes the `trust unlock / rescue-first export / one-shot destructive ticket` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's dangerous-control contract**

This time the evidence is especially clear around **service/browser control, Linux install/product-line compatibility, public non-commercial warnings, browser-trust bootstrap, and mobile per-share destructive toggles**.

Current official docs still openly distinguish real operator facts such as:

- `Running Sync as a service on Windows` still saying Sync can run as a background service regardless of logged-in user state and opens WebUI in the default browser
- `Installing Sync package on Linux` still publishing manual, repository, and official Docker-image install paths while also separating personal `v3` from Business `v2.8.1`
- `Download Sync` still saying Sync is for personal non-commercial use and warning NAS users not to update current Sync Business installations to `v3` because configured-share access will be lost
- `Configuring WebUI` and browser-warning docs still making binding, password posture, self-signed HTTPS, and browser exceptions ordinary operational facts
- Android interface docs still exposing `Use Archive`, `Overwrite changed files`, relay, tracker, LAN search, and host overrides as normal per-share controls

That candor is good.
The non-clone problem is still dangerous-control ownership.
Ordinary operators can still be pushed into several docs before the product fully owns these questions:

- which runtime and product line this control surface actually belongs to
- whether current browser trust is durable enough for destructive action or still only bootstrap trust
- what exact residue can be preserved before destructive approval
- whether final destructive approval still binds to the same endpoint, trust grade, loss basis, and salvage basis right now

AnonSync should therefore make **danger-session context, trust-bootstrap review, rescue-first export, and one-shot destructive execution** first-class product objects.
Every serious destructive repair, source-authoritative reset, encrypted-custody surrender, or overwrite approval should keep runtime/trust identity visible, support salvage export as an explicit object, and require a freshness-bound execution ticket before commit.

## New documents in rev0286

- `856` Resilio service/browser and destructive-toggle fragmentation evaluation
- `857` Danger session capsule and persistent review-context component family
- `858` Trust bootstrap review page
- `859` Salvage export page
- `860` Salvage export receipt page
- `861` Destructive execution ticket page


## Revision addendum — rev0285: Resilio product-line split, destructive review shell, and local-web danger contract

This revision continues directly from `rev0284` and does eight concrete things:

1. Re-checks current official Resilio Sync material around the **live v3 line, the still-supported v2.8 Business line, unsupported Business-to-v3 upgrade paths, Linux/WebUI bringup, self-signed browser trust warnings, and the current destructive-heal pages**.
2. Tightens the non-clone line again: borrow Resilio's candor that local-web/service operation is real, that read-only overwrite is destructive, and that product-line boundaries must be spoken plainly; refuse any contract where destructive decisions or upgrade boundaries still require cross-reading product-line notices, install guides, and help-center prose.
3. Adds one new **Resilio evaluation** document focused on why the present-day Resilio picture strengthens the `adapt, not clone` judgment: the useful candor is still there, but it now sits inside a more visibly split product story (`Sync v3 personal`, `Sync Business v2.8`, `Active Everywhere` for new business buyers).
4. Adds four new **interface specs** for the workflow-owned surfaces this pass was still missing: destructive review shell, loss-class matrix and salvage-ladder components, destructive approval barrier, and local-web danger-surface exposure contract.
5. Makes one hard product decision explicit: **destructive actions are never preference toggles in AnonSync**. They are reviewed, scoped, receipted operations with a proof-adjacent loss matrix and salvage ladder.
6. Makes another hard product decision explicit: **local web is first-class, but danger actions must carry endpoint identity, auth posture, listener scope, and seat capability on the same page**. The product may support trust bootstrap; it may not normalize vague browser-exception folklore as the control contract.
7. Refreshes the core doctrine documents actually touched in this pass — README, status, scorecard, clone-veto, product direction, interface rules, pattern language, architecture decisions, roadmap, sources, and the new page family — so the tranche is integrated rather than floating.
8. Packages the result as another continuation archive whose new tranche makes the `Resilio split / destructive review shell / local-web danger contract` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present product contract**

This time the reason is even stronger because the current official picture is now clearly split across product lines as well as feature pages.
Current official materials simultaneously show that:

- Resilio Sync v3 is the live personal-use line and the 3.0 change log currently runs through `3.1.2.1076`
- current support/platform docs still list `Sync v3` platforms while also keeping separate `Sync v2` support sections
- current Resilio pages say Sync Business customers should stay on `v2.8`, that `v3` is not the supported upgrade path for Business, and that attempting that path can lose configured-share access
- current Linux/WebUI docs still treat local web and configuration mode as ordinary reality, including listener binding and service-style operation
- current browser-warning docs still normalize a self-signed-certificate trust exception path for WebUI
- current destructive-heal docs still spread one operator answer across one-way sync, folder preferences, archive behavior, encrypted folders, power-user defaults, mobile surfaces, and configuration-mode prose

That candor is useful.
The split contract is the problem.
AnonSync should not clone a world where the operator must piece together:

- whether they are in the personal-v3 line, the business-v2 line, or the enterprise-active-everywhere lane
- whether a local-web/browser warning is merely expected bootstrap, an endpoint-exposure problem, or a real trust downgrade
- whether `overwrite changed files` is an ordinary per-folder preference or a destructive reviewed decision with a live salvage envelope

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful truths are real, but the present-day operator contract is still split across product lines, upgrade warnings, local-web bootstrap notes, and destructive-heal help prose rather than owned as one reviewed interface grammar.**

## Legacy revision notes preserved below

## Revision addendum — rev0284: destructive heal preview, salvage ladders, and loss-waiver truth

This revision continues directly from `rev0283` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **Read Only overwrite healing, archive-bearing conditions, archive-retention defaults, encrypted-backup hardwiring, mobile overwrite toggles, configuration-mode defaults, and the active v3 line**.
2. Sharpens the non-clone line again: borrow Resilio's candor that source-authoritative healing can be destructive and that archive/salvage conditions matter, while refusing any product contract where operators still have to reconstruct exact local loss and remaining salvage from several help articles.
3. Adds one new **Resilio evaluation** document focused on how current official docs still spread one ordinary operator answer about `before I let source-authoritative healing proceed, what exact local work will be overwritten, what salvage still exists, and what loss am I knowingly waiving?` across several features and help surfaces.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: maintenance overwrite plan, maintenance overwrite review, maintenance overwrite ledger, and maintenance overwrite receipt.
5. Extends the doctrine so every serious read-only heal, backup-seat reset, encrypted-custody surrender, source-authoritative repair, and destructive rejoin attempt now publishes **candidate loss classes, archive-bearing status, salvage ladder, waiver boundary, strongest safe sentence, and reopen conditions** before the product treats `overwrite changed files` as self-explanatory.
6. Refreshes the core doctrine documents actually touched in this pass — README, status, evaluation, borrow-line scorecard, clone-veto tests, product direction, roadmap, sources, and the new page family — so the tranche is integrated rather than floating.
7. Packages the result as another continuation archive whose new tranche makes the `destructive heal preview / salvage review / surrender ledger / loss receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's destructive-heal contract**

This time the evidence is especially clear around **Read Only overwrite healing, archive-bearing asymmetry, archive-retention policy, encrypted backup hardwiring, mobile overwrite toggles, and config-mode defaults**.

Current official docs still openly distinguish real destructive-heal facts such as:

- `Is one-way synchronization possible?` still saying that on Read Only shares overwrite healing can re-download the older name after a rename, restore a deleted file, revert edited content to the most recent RW version, and keep newly added files local rather than syncing them
- `Folder Preferences` still saying `Overwrite any changed files` is potentially destructive, while also saying Archive stores remotely caused changed or deleted files in `.sync/Archive` for 30 days by default and that disabling Archive stops that safety copy and makes remote rename/copy fall back to re-download
- `Using Archive for file versioning and restoring deleted files` still saying a device's Archive receives an old file version only when the file was modified by another peer, while locally deleted files are usually recovered from the local trash / recycling bin instead
- `Encrypted folders` still saying encrypted backup nodes are Read Only, always have overwrite activated, cannot decrypt locally in ordinary operation, and may move same-key preexisting encrypted files into Archive with extra space cost
- `Power user preferences` still publishing `overwrite_changes false` as the default and `sync_trash_ttl 30 (day)` as the standing archive-age parameter
- mobile interface docs still exposing both `Use Archive` and `Overwrite changed files` / `Overwrite any changed files` as separate knobs on Android and iOS
- the current 3.0 change log still showing the maintained line through `3.1.2.1076`

That candor is good.
The non-clone problem is still destructive-heal ownership.
Ordinary operators can still be pushed into several help articles before the product fully owns these questions:

- which exact local change classes are about to be surrendered if source-authoritative healing proceeds
- whether any archive, trash, evidence export, or successor branch salvage path still exists before overwrite
- whether the current device even bears the older version locally or only some other peer's archive does
- whether disabling Archive, using an encrypted custody seat, or changing overwrite defaults has already weakened the rescue ladder
- what strongest sentence remains safe afterward, and what stronger `nothing was lost` sentence is still forbidden

AnonSync should therefore make **destructive-heal preview and salvage review** first-class product objects.
Every serious read-only heal, backup-seat reset, encrypted custody surrender, source-authoritative repair, and destructive rejoin attempt should render candidate loss classes, archive-bearing status, salvage ladder, waiver boundary, strongest safe sentence, and reopen conditions before the product treats `Overwrite changed files` as routine.

## Legacy revision notes preserved below

## Revision addendum — rev0283: maintenance rejoin, shared-line restoration, and successor-boundary truth

This revision continues directly from `rev0282` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **Read Only suspension, `Overwrite any changed files`, encrypted-backup restore limits, storage-oriented backup folders, device-local removal/disconnect preservation semantics, and the active v3 line**.
2. Sharpens the non-clone line again: borrow Resilio's candor that local work under narrow or backup-like maintenance postures can survive with several later fates, while refusing any product contract where operators still have to guess how that work can rejoin the shared line later.
3. Adds one new **Resilio evaluation** document focused on how current official docs still spread one ordinary operator answer about `after local work happened during a hold, what exact path can bring it back into the shared line now?` across several features and help surfaces.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: maintenance rejoin plan, maintenance rejoin review, maintenance rejoin ledger, and maintenance rejoin receipt.
5. Extends the doctrine so every serious evidence hold, read-only inspection window, backup-like endpoint, encrypted custody seat, and repair sandbox now publishes **rejoin path, authority-change needs, promotion requirement, overwrite barrier, strongest safe sentence, and successor boundary** before the product treats `we can bring it back later` as implied.
6. Refreshes the core doctrine documents actually touched in this pass — README, status, evaluation, borrow-line scorecard, clone-veto tests, product direction, roadmap, sources, and the new page family — so the tranche is integrated rather than floating.
7. Packages the result as another continuation archive whose new tranche makes the `maintenance rejoin / restoration class / successor lane / abandonment boundary` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's maintenance rejoin contract**

This time the evidence is especially clear around **Read Only suspension, optional but destructive overwrite healing, encrypted backup's preserve-and-restore asymmetry, storage-oriented backup lanes, and device-local removal that preserves bytes without restoring shared-line continuity**.

Current official docs still openly distinguish real maintenance-rejoin facts such as:

- `User Management` still saying Read Only peers that modify files or add new ones do not propagate those changes and that further synchronization of the changed files will be suspended for that peer
- `Is one-way synchronization possible?` still saying the same thing operationally, while also saying `Overwrite any changed files` can restore deleted files, re-download the old name after a rename, revert edited contents to the most recent version from a RW peer, and keep newly added files local rather than syncing them
- `Folder Preferences` still saying `Overwrite any changed files` is potentially destructive and disabled for Read-only folders with Selective Sync ON
- `Encrypted folders` still saying encrypted backup nodes are Read Only, always have overwrite activated, cannot decrypt locally, and rely on saved keys plus preserved database continuity or special local decrypt flow for restoration
- that same current encrypted-folder article still saying encrypted-archive restoration cannot simply upload the restored file back because the node is read-only and follows deleted state
- `How to use Camera Backup (all mobiles)?` still saying backup folders are storage-oriented Read Only folders and that disconnecting backup leaves already-present files on both mobile and desktop
- `Sync Interface on iOS devices` still saying `Remove from this device` disconnects the folder only on that device, removes local files there, and preserves them on others
- the current 3.0 change log still showing the maintained line through `3.1.2.1076`

That candor is good.
The non-clone problem is still maintenance rejoin ownership.
Ordinary operators can still be pushed into several help articles before the product fully owns these questions:

- whether the held local work can rejoin in place, only after widening rights, only as a successor branch, or not at all
- whether source-authoritative healing will overwrite the local work before any rejoin claim is honest
- whether added files, edited files, renamed files, and backup-preserved copies have different restoration paths
- when `preserved somewhere` is a real success and when it is only a weaker evidence or backup sentence
- what strongest sentence remains safe afterward, and what stronger `restored cleanly` sentence is still forbidden

AnonSync should therefore make **maintenance rejoin planning and shared-line restoration review** first-class product objects.
Every serious evidence hold, read-only inspection window, backup-like endpoint, encrypted custody seat, and repair sandbox should render rejoin path, authority change needs, promotion or successor requirement, overwrite barrier, strongest safe sentence, and successor boundary before the product treats later restoration as obvious.

## Legacy revision notes preserved below

## Revision addendum — rev0282: maintenance mutation budgets, suspended continuity, and overwrite-proof local work

This revision continues directly from `rev0281` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **Read Only mutation fate, `Overwrite any changed files`, encrypted-backup hardwiring, mobile backup preservation semantics, remove-from-device behavior, and the active v3 line**.
2. Sharpens the non-clone line again: borrow Resilio's candor that narrow or backup-like seats can still accept local changes with very different later fates, while refusing any product contract where operators still have to remember which local edits survive, suspend continuity, or get overwritten.
3. Adds one new **Resilio evaluation** document focused on how current official docs still spread one ordinary operator answer about `while this hold is active, what local work is safe here and what later fate will that work have?` across several features and help surfaces.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: maintenance mutation budget, maintenance mutation review, maintenance mutation ledger, and maintenance mutation receipt.
5. Extends the doctrine so every serious read-only inspection window, preservation node, backup-like endpoint, evidence hold, and repair sandbox now publishes **allowed local work, continuity fate, overwrite risk, escape hatch, strongest safe sentence, and reopen boundary** before the product treats `safe to edit here` as implied.
6. Refreshes the core doctrine documents actually touched in this pass — README, status, evaluation, borrow-line scorecard, clone-veto tests, product direction, roadmap, sources, and the new page family — so the tranche is integrated rather than floating.
7. Packages the result as another continuation archive whose new tranche makes the `maintenance mutation budget / mutation review / mutation ledger / mutation receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's maintenance-local mutation contract**

This time the evidence is especially clear around **read-only local-change suspension, potentially destructive `Overwrite any changed files`, encrypted backup's hardwired overwrite posture, Android backup's preservation semantics, and iOS remove-from-device asymmetry**.

Current official docs still openly distinguish real maintenance-local mutation facts such as:

- `User Management` still saying Read Only peers that modify files or add new ones do not propagate those changes and that further synchronization of the changed files will be suspended for that peer
- `Folder Preferences` still saying `Overwrite any changed files` on Read Only shares will overwrite local changes, including files the operator added, and warning that this option is potentially destructive to the operator's data
- that same current article still saying the overwrite option is disabled for Read-only folders with Selective Sync ON
- `Encrypted folders` still saying encrypted backup nodes are Read Only, always have `Overwrite any changed files` activated, and do not allow Selective Sync
- `How to Back up data (Android only)` still saying backup intentionally preserves copies even after later deletion on the phone and that the desktop side has read-only access so changes do not sync back
- `Sync Interface on iOS devices` still saying `Remove from this device` disconnects the folder only on that iOS device, removes files there, and preserves them on others
- the current 3.0 change log still showing the maintained line through `3.1.2.1076`

That candor is good.
The non-clone problem is still maintenance-local mutation ownership.
Ordinary operators can still be pushed into several help articles before the product fully owns these questions:

- whether editing here is actually in budget or only feels harmless because the seat is `read only` or `backup-like`
- whether local edits will survive in place, strand themselves, suspend future continuity, or be overwritten later
- whether newly added files behave differently from edits to existing files in this posture
- what cheaper escape hatch exists before any local work begins
- what strongest sentence remains safe afterward, and what stronger `safe local work` sentence is still forbidden

AnonSync should therefore make **maintenance mutation budget and mutation-fate review** first-class product objects.
Every serious evidence hold, read-only inspection window, preservation node, backup-like endpoint, and repair sandbox should render allowed local work, continuity fate, overwrite risk, export or branch escape hatch, strongest safe sentence, and reopen boundary before the product treats local editing as obviously safe.

## Legacy revision notes preserved below

## Revision addendum — rev0281: maintenance intent, hold-class semantics, and non-overloaded quiet contracts

This revision continues directly from `rev0280` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **manual pause, scheduled `Paused`, one-way/read-only sync, Android backup semantics, and the active v3 line**.
2. Sharpens the non-clone line again: borrow Resilio's candor that different controls imply different motion contracts, while refusing any product contract where operators still have to remember which feature means transfer silence, writeback quiet, preservation, or destructive-safety.
3. Adds one new **Resilio evaluation** document focused on how current official docs still spread one ordinary operator answer about `what kind of maintenance hold do I actually need, and what still moves under it?` across several features and help surfaces.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: maintenance intent, maintenance semantics review, maintenance transition plan, and maintenance contract receipt.
5. Extends the doctrine so every serious upgrade window, evidence capture, migration cut, destructive repair, and staged catch-up now publishes **requested hold class, achieved semantics, allowed residuals, counterpart requirements, strongest safe sentence, and reopen boundary** before the product treats `paused` or `backup` as enough.
6. Refreshes the core doctrine documents actually touched in this pass — README, status, evaluation, borrow-line scorecard, clone-veto tests, product direction, roadmap, interface spec, sources, and the new page family — so the tranche is integrated rather than floating.
7. Packages the result as another continuation archive whose new tranche makes the `maintenance intent / semantics matrix / transition plan / contract receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's overloaded quiet-and-maintenance contract**

This time the evidence is especially clear around **partial pause, scheduled speed-zero with surviving residuals, one-way read-only semantics, Android backup preservation semantics, and the absence of one product-owned maintenance intent chooser**.

Current official docs still openly distinguish real maintenance-semantics facts such as:

- `How to pause syncing` still saying pause stops only bits transfer while zero-sized files and deletions still sync and new files are still rescanned and indexed
- `Running Sync on schedule` still saying scheduled `Paused` is only a speed-zero posture, still preserves those residuals, and can still let paused peers upload to non-paused peers while not downloading themselves
- `Is one-way synchronization possible?` still saying Read Only permission gives one-way sync where changes made in the read-only folder do not sync back
- `How to Back up data (Android only)` still saying backup intentionally preserves copies and that the desktop side has read-only access so changes do not sync back
- the current 3.0 change log still showing the maintained line through `3.1.2.1076`

That candor is good.
The non-clone problem is still maintenance-intent ownership.
Ordinary operators can still be pushed into several help articles before the product fully owns these questions:

- whether the goal is transfer silence, writeback quiet, delete freeze, preserve-only posture, or a stronger maintenance hold
- which kinds of motion remain intentionally allowed under the chosen control
- whether the maintenance sentence is local only or needs counterpart match before it is honest
- whether the chosen control should drain in-flight work, cut over immediately, or wait for acknowledgement
- what strongest sentence remains safe now, and what stronger `frozen` or `nothing can change` sentence is still forbidden

AnonSync should therefore make **maintenance intent and maintenance semantics review** first-class product objects.
Every serious upgrade window, evidence capture, migration cut, destructive repair, and staged backlog release should render requested hold class, achieved semantics, allowed residuals, counterpart requirements, strongest safe sentence, and reopen boundary before the product treats `paused`, `read only`, or `backup` as sufficient language.

## Legacy revision notes preserved below

## Revision addendum — rev0280: backlog release shape, cap-return cliffs, and post-quiet order truth

This revision continues directly from `rev0279` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **scheduled quiet-window expiry, full-bandwidth return, per-share and default download priority, active-queue caps, preemption rules, queue rebuild churn, visible-vs-actual order mismatch, and the active v3 line**.
2. Sharpens the non-clone line again: borrow Resilio's candor that quiet expiry and backlog release are not neutral, while refusing any contract where operators still have to splice schedule prose, priority docs, caps, and queue exceptions just to predict the post-quiet blast.
3. Adds one new **Resilio evaluation** document focused on how current official docs still spread one ordinary operator answer about `when quiet ends, what resumes first, at what cap, and how bursty will catch-up be?` across several settings and help surfaces.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: backlog release plan, backlog order review, backlog release timeline, and backlog release receipt.
5. Extends the doctrine so every serious quiet-window expiry, maintenance exit, and deferred catch-up now publishes **return cap, release-shape verdict, authoritative order, exceptions, flood risk, and reopen boundary** before the product treats resumed motion as predictable.
6. Refreshes the core doctrine documents actually touched in this pass — README, status, evaluation, borrow-line scorecard, clone-veto tests, product direction, roadmap, sources, and the new page family — so the tranche is integrated rather than floating.
7. Packages the result as another continuation archive whose new tranche makes the `quiet expiry / cap return / backlog release order / flood-risk` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's post-quiet backlog-release contract**

This time the evidence is especially clear around **empty-schedule-cell full-bandwidth return, partial paused-state asymmetry, priority inheritance and override freeze, 50k active-queue limits, preemption exceptions, queue rebuild churn, and visible-vs-actual order mismatch**.

Current official docs still openly distinguish real post-quiet release facts such as:

- `Running Sync on schedule` still saying empty cells mean Sync can work at full bandwidth available, unchecked upload or download means full bandwidth for that direction, and scheduled `Paused` still allows certain residual behaviors
- `File download priority` still saying per-share priority and global `folder_defaults.transfer_priority` can both shape download order, while manually set share priority stops inheriting later global changes even if the operator later sets the share back to `None`
- that same priority article still saying only the active queue is prioritized up to 50,000 files, higher-priority arrivals suspend lower-priority work, some internal exceptions remain, non-splittable files do not fully obey strict prioritization, and the visible UI queue may still appear alphabetical rather than true execution order
- `Power user preferences` still publishing `folder_defaults.transfer_priority` as a standing default plane rather than a reviewed catch-up release object
- the current 3.0 change log still showing the maintained line through `3.1.2.1076`

That candor is good.
The non-clone problem is still release-shape ownership.
Ordinary operators can still be pushed into several help articles before the product fully owns these questions:

- whether quiet expiry returns to full bandwidth immediately or to some narrower cap
- which backlog class will actually move first once transfer lanes reopen
- whether the visible queue order is authoritative enough to trust during catch-up
- whether queue rebuild or transfer-class exceptions make a seemingly neat priority promise false in the current moment
- what strongest sentence remains safe now, and what stronger `resume will clear the backlog cleanly` sentence is still forbidden

AnonSync should therefore make **backlog release planning and post-quiet order review** first-class product objects.
Every serious maintenance exit, quiet-window expiry, and deferred-catch-up situation should render release trigger, return cap, authoritative order, queue exceptions, flood-risk verdict, and reopen boundary before the product treats resumed motion as understood.

## Legacy revision notes preserved below


## Revision addendum — rev0279: allowed residuals, quiet challenges, and break-vs-expected judgment

This revision continues directly from `rev0278` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **manual pause, scheduled `Paused`, surviving delete/control/indexing behavior, asymmetric paused-peer upload behavior, historical paused-state subtlety, and the active v3 line**.
2. Sharpens the non-clone line again: borrow Resilio's candor that some motion survives pause, while refusing any contract where operators still have to remember that matrix later just to decide whether a new event actually disproved the quiet claim.
3. Adds one new **Resilio evaluation** document focused on how current official docs still spread one ordinary operator answer about `this event happened during quiet — was that expected residue or a real break?` across several local-control articles.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: quiet event, residual allowance review, quiet challenge ledger, and residual classification receipt.
5. Extends the doctrine so every serious maintenance / evidence / migration window now publishes **challenged quiet receipt, observed event, allowance-fit verdict, surviving sentence, and reopen boundary** before the product treats post-quiet motion as understood.
6. Refreshes the core doctrine documents actually touched in this pass — README, status, evaluation, borrow-line scorecard, clone-veto tests, product direction, roadmap, sources, and the new page family — so the tranche is integrated rather than floating.
7. Packages the result as another continuation archive whose new tranche makes the `allowed residue / quiet challenge / first real break` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's post-quiet event-classification contract**

This time the evidence is especially clear around **delete propagation, zero-byte/control-shaped events, indexing/share-size growth, scheduled paused-peer upload asymmetry, and the absence of one product-owned event classifier**.

Current official docs still openly distinguish real post-quiet event facts such as:

- `How to pause syncing` still saying pause stops only bits download/upload while zero-sized files and deletions still sync and new files are still rescanned and indexed so share size can increase on paused peers
- `Running Sync on schedule` still saying scheduled `Paused` means upload/download speed are zero while zero-sized files and deletions still sync, new files are rescanned and indexed, and paused peers may still upload to non-paused peers while not downloading themselves
- `Sync Preferences` still presenting Global Pause / Resume and Scheduler as ordinary local controls rather than as a reviewed object that later classifies challenge events
- the still-published historical change log still recording `Sync stopping indexing if folder paused`
- the current 3.0 change log still showing the maintained line through `3.1.2.1076`

That candor is good.
The non-clone problem is still post-quiet workflow ownership.
Ordinary operators can still be pushed into several help articles before the product fully owns these questions:

- whether a later delete, share-size jump, queue change, or upload row was actually expected under the earlier quiet receipt
- whether the event belonged to the covered cohort/scope or only looked adjacent to it
- whether the first visible movement was really the first break or only allowed residual noise
- what sentence remains safe now, and what stronger sentence became forbidden the moment the event was classified
- what durable receipt proves whether the earlier quiet claim survived, narrowed, or failed

AnonSync should therefore make **allowed-residual classification and quiet-challenge review** a first-class product object.
Every serious maintenance window, evidence capture, migration cut, or destructive repair should render challenged quiet receipt, observed event, allowance-fit verdict, surviving sentence, and reopen boundary before the product treats post-quiet motion as understood.

## Legacy revision notes preserved below

## Revision addendum — rev0278: quiet-break provenance, resume authority, and post-quiet claim safety

This revision continues directly from `rev0277` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **manual resume, Global Resume, scheduler clock boundaries, Start Sync on startup, hidden/background runtime, historical paused-state subtlety, and the active v3 line**.
2. Sharpens the non-clone line again: borrow Resilio's candor that reactivation can come from several honest sources, while refusing any contract where operators still have to infer whether quiet ended by manual choice, clock expiry, background continuation, or uncovered-seat reality.
3. Adds one new **Resilio evaluation** document focused on how current official docs still spread one ordinary operator answer about `who broke the quiet claim, by what authority, and was that break expected?` across several local-control articles.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: quiet break, resume authority review, quiet break timeline, and quiet break receipt.
5. Extends the doctrine so every serious maintenance / evidence / migration window now publishes **prior quiet basis, breaking seat, authority verdict, quiet tenure, strongest surviving sentence, and successor boundary** before the product treats reactivation as understood.
6. Refreshes the core doctrine documents actually touched in this pass — README, clone-veto tests, roadmap, sources, evaluation, and the new page family — so the tranche is integrated rather than floating.
7. Packages the result as another continuation archive whose new tranche makes the `quiet claim / first break event / resume authority / successor claim` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's resume and quiet-break contract**

This time the evidence is especially clear around **local resume, scheduler boundaries, background runtime, startup-based reactivation, and the absence of one product-owned quiet-break object**.

Current official docs still openly distinguish real post-quiet facts such as:

- `How to pause syncing` still saying pause stops only bits download/upload while zero-sized files and deletions still sync, new files are still rescanned and indexed, and resuming is done by repeating the same local steps
- that same article still saying Global Pause / Resume lives on the current device window rather than as a reviewed shared maintenance object
- `Running Sync on schedule` still saying empty cells mean full bandwidth and `Paused` is only a speed-zero local state whose delete/indexing residuals remain alive
- `Sync Preferences` still placing Start Sync on startup, Global Pause / Resume, and Scheduler together as ordinary local controls
- `Does Sync work in background?` still saying desktop hidden runtime stays active, Linux can run headlessly, and Android may still keep working in background unless platform/runtime conditions stop it
- the still-published historical change log still recording `Sync stopping indexing if folder paused`
- the current 3.0 change log still showing the maintained line through `3.1.2.1076`

That candor is good.
The non-clone problem is still post-quiet workflow ownership.
Ordinary operators can still be pushed into several help articles before the product fully owns these questions:

- which exact event first weakened or ended the prior quiet claim
- which seat it came from and whether that seat was actually inside the prior covered cohort
- whether the break was expected because the declared window expired or surprising because a seat resumed early
- how long the prior quiet claim actually held before it weakened
- what sentence remains safe now, and what successor claim would be needed to regain stronger language

AnonSync should therefore make **quiet-break provenance and resume-authority review** a first-class product object.
Every serious maintenance window, evidence capture, migration cut, or destructive repair should render prior quiet basis, first break event, authority verdict, quiet tenure, surviving sentence, and successor boundary before the product treats reactivation as understood.

## Legacy revision notes preserved below

## Revision addendum — rev0277: quiet cohorts, counterpart agreement, and local-vs-shared stillness

This revision continues directly from `rev0276` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **manual pause, Global Pause, scheduler `Paused`, counterpart asymmetry, ongoing delete/indexing behavior, and the active v3 line**.
2. Sharpens the non-clone line again: borrow Resilio's candor that pause is partial and origin-bearing, while refusing any contract where operators still have to infer whether only one seat got quieter or the seats that matter actually matched a shared quiet window.
3. Adds one new **Resilio evaluation** document focused on how current official docs still spread one ordinary operator answer about `did we establish quiet where this job actually needed it?` across several local-control articles.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: quiet cohort, quiet agreement review, quiet window request, and quiet cohort receipt.
5. Extends the doctrine so every serious maintenance / evidence / migration window now publishes **target cohort, matched seats, uncovered seats, residual movers, strongest safe sentence, and reopen boundary** before the product treats local pause as shared stillness.
6. Refreshes the core doctrine documents actually touched in this pass — README, status, evaluation, borrow-line scorecard, clone-veto tests, product direction, architecture decisions, roadmap, sources, and the new page family — so the tranche is integrated rather than floating.
7. Packages the result as another continuation archive whose new tranche makes the `local pause / shared quiet agreement / uncovered residual mover` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's local-pause and shared-quiet contract**

This time the evidence is especially clear around **manual pause, local Global Pause, scheduled quiet windows, and the absence of one product-owned cohort-coverage object**.

Current official docs still openly distinguish real quiet-window facts such as:

- `How to pause syncing` still saying pause stops only bits download/upload while zero-sized files and deletions still sync and new files are still rescanned and indexed
- that same article still saying Global Pause affects all shares on the current device, which is a local control rather than a reviewed counterpart agreement
- `Sync Preferences` still describing Global Pause / Resume and Scheduler as ordinary local controls in the same preferences surface
- `Running Sync on schedule` still saying scheduled `Paused` means upload/download speed are zero, while zero-sized files and deletions still sync, new files are rescanned and indexed, and paused peers may still upload to non-paused peers while not downloading themselves
- the current 3.0 change log still showing the maintained line through `3.1.2.1076`
- the still-published historical change log still recording `Sync stopping indexing if folder paused`

That candor is good.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed into several help articles before the product fully owns these questions:

- did only **this** seat become quieter, or did the seats that matter actually match the requested stillness
- which still-relevant seats remain able to publish bytes, propagate deletes, or rescan local changes
- whether the safe sentence is `quiet here`, `quiet across covered seats`, or `not yet quiet enough`
- what counterpart proof is still missing before a maintenance/evidence/migration claim becomes honest
- what event would reopen the quiet claim after it was issued

AnonSync should therefore make **quiet cohort agreement** a first-class product object.
Every serious maintenance window, evidence capture, migration cut, or destructive repair should render target cohort, matched seats, uncovered seats, residual movers, safe language, and reopen conditions before the product treats local pause as shared stillness.

## Legacy revision notes preserved below

## Revision addendum — rev0276: re-entry cases, dormancy truth, and stale-return safety

This revision continues directly from `rev0275` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **hidden-but-not-unlinked offline devices, peer-expiration aging, shutdown/re-open re-indexing, offline edits outranking later online work, time-difference invalidation, ghost announcements, and the active v3 line**.
2. Sharpens the non-clone line again: borrow Resilio's candor that not every comeback is an ordinary healthy return, while refusing any contract where operators still have to merge background notes, peer-list aging, hidden-device behavior, clock warnings, and no-source warnings before deciding whether `back` is even a safe word.
3. Adds one new **Resilio evaluation** document focused on how current official docs still spread one ordinary operator answer about `what exactly came back after dormancy, and how trustworthy is that return?` across several articles.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: re-entry case, dormancy timeline, stale-return review, and re-entry receipt.
5. Extends the doctrine so every serious stale return now publishes **dormancy facts, return class, chronology confidence, source-reality verdict, strongest safe sentence, and reopen boundary** before the product treats the state as ordinary again.
6. Refreshes the core doctrine documents actually touched in this pass — README, status, evaluation, borrow-line scorecard, clone-veto tests, product direction, architecture decisions, roadmap, open questions, sources, and the new page family — so the tranche is integrated rather than floating.
7. Packages the result as another continuation archive whose new tranche makes the `re-entry case / dormancy timeline / stale-return review / re-entry receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's stale-return and re-entry contract**

This time the evidence is especially clear around **restart-shaped chronology risk, hidden-offline return, peer-expiration aging, clock-invalid comeback, and ghost announcements with no remaining full source**.

Current official docs still openly distinguish real stale-return facts such as:

- `Does Sync work in background?` still saying shutdown and re-open re-index folders, assign a new modification time, and can let offline updates overwrite changes made by peers that remained online
- `Sync Main View (Desktop)` still saying offline peers remain counted for a while and are disconnected from the folder after 7 days
- `Power user preferences` still naming `peer_expiration_days` with a default of 7 days
- `How to clear offline devices? (desktop only)` still saying hidden offline devices are only hidden, not unlinked, and can reappear later if they come back online
- `"Time difference" error` still saying time / timezone drift beyond 600 seconds invalidates chronology and can leave mobile peers showing empty lists
- `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time` still saying some announced files are really ghost files that nobody has anymore
- the active v3 line still appearing through `3.1.2.1076`

That candor is good.
The non-clone problem is still re-entry ownership.
Ordinary operators can still be pushed into several help articles before the product fully owns these questions:

- what exact kind of thing returned: a healthy participant, a hidden device, an aged-out peer, or only a stale announcement
- whether chronology trust survived dormancy well enough for ordinary `latest` language
- whether live full source bytes are actually back or only the announcement is
- what cheapest honest move follows now: trust, quarantine, repair clocks, or verify source
- what stronger sentence is still forbidden: `everything is normal again`, `this is definitely latest`, or `the file will arrive now`

AnonSync should therefore make **re-entry after dormancy** a first-class product object.
Every serious long-offline return, hidden-device reappearance, clock-invalid comeback, or ghost-announcement aftermath should render dormancy facts, return class, chronology confidence, source-reality verdict, safe language, and reopen conditions before the product treats the state as ordinary again.

## Legacy revision notes preserved below

## Revision addendum — rev0275: next-observation opportunity, duty windows, and late-claim honesty

This revision continues directly from `rev0274` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **desktop hidden runtime, Android background survival, Android auto-sleep wake intervals, battery-saver stops, mobile notification priority, Wi-Fi/network gating, watcher fallback, service/UNC notification loss, and the active v3 line**.
2. Sharpens the non-clone line again: borrow Resilio's candor that seats earn different next chances to notice or act, but refuse any contract where operators still have to merge wake rules, battery/network policy, watcher warnings, and rescan cadence before deciding whether `late` is even honest.
3. Adds one new **Resilio evaluation** document focused on how current Resilio still spreads one ordinary operator answer about `when is this seat actually due next?` across several unrelated help articles.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: next observation opportunity, late-claim review, duty-cycle timeline, and observation-opportunity receipt.
5. Extends the doctrine so every serious delay surface now publishes **duty class, unmet prerequisites, next opportunity, due verdict, stronger rejected sentence, and reopen boundary** before the product treats elapsed time as evidence of failure.
6. Refreshes the status/evaluation/product-direction/interface/report/sources documents so the new tranche is integrated rather than bolted on.
7. Packages the result as another continuation archive whose new tranche makes the `not yet due` versus `actually late` seam explicit in the reading order and the page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's lateness contracts**

This time the evidence is especially clear around **duty class, wake windows, notification/background survivability, and next-opportunity truth**.

Current official docs still openly distinguish real timing facts such as:

- `Does Sync work in background?` still saying desktop hidden runtime stays active, Android can work in background but task killers can stop it, and iOS background synchronization is unavailable
- `Configuring Auto Sleep & Battery Saver (Android)` still saying Android may hibernate between wake intervals and wake every configured period, 30 minutes by default, while Battery Saver can stop Sync below a chosen threshold
- `Settings on mobile platforms` still saying disabling Android notifications can lower Sync's priority so it may stop working in the background, and still keeping Wi-Fi/mobile-data policy in a separate network settings area
- `How soon does synchronization start?`, `Power user preferences`, and the watcher/service articles still preserving rescan-backed and notification-degraded opportunity classes
- the active v3 line still appearing through `3.1.2.1076`

That candor is good.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed into several help articles before the product fully owns these questions:

- when this seat is actually next due to notice or act
- whether `late` is premature because the relevant wake/rescan/opportunity has not arrived yet
- which prerequisite matters more than wall-clock time right now
- what stronger sentence is still forbidden: `ignored`, `stuck`, or `background sync failed`

AnonSync should therefore make **next-observation opportunity** and **late-claim review** first-class product objects.
Every serious missing-update incident should render duty class, unmet prerequisites, next opportunity, due verdict, safe language, and reopen conditions before the product treats elapsed time as proof of failure.

## Legacy revision notes preserved below

# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0275`
- Timestamp: `2026.03.22.05.53` (America/New_York)
- Codename: `opportunitydutytruthledger`

## What changed in this revision

This revision continues directly from `rev0273` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **watcher exhaustion, SMB / UNC notification loss, service-profile changes, NAS sleep-preserving cadence widening, Android auto-sleep and battery-saver stops, forbidden-network posture, and the active v3 line**.
2. Sharpens the non-clone line again: borrow Resilio's candor that observation posture can drift after an incident starts, while refusing any contract where old freshness claims linger as if runtime, path, power, or network changes did not matter.
3. Adds one new **Resilio evaluation** document focused on how current official docs still spread one ordinary operator answer about `does the earlier freshness judgment still apply after the environment changed?` across watcher, service, SMB, NAS, mobile, and settings articles.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: freshness invalidator, freshness revalidation review, posture drift timeline, and freshness rollover receipt.
5. Extends the doctrine so every serious reused freshness or lateness claim now publishes **prior receipt, invalidator class, drift impact, new proof threshold, supersession boundary, and strongest safe sentence** before the product treats `already checked` or `still late` as durable incident truth.
6. Refreshes the core doctrine documents actually touched in this pass — README, status, evaluation, borrow-line scorecard, clone-veto tests, product direction, architecture decisions, roadmap, open questions, sources, and the new page family — so the tranche is integrated rather than floating.
7. Packages the result as another continuation archive whose new tranche makes the `freshness invalidator / freshness revalidation review / posture drift timeline / freshness rollover receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's freshness-claim invalidation and revalidation contract**

This time the evidence is especially clear around **`Agent run out of system notify watchers` still saying watcher exhaustion pushes discovery onto periodic or manual rescans; `Sync Service Troubleshooting on Windows` still saying UNC/network-drive service setups may not receive update notifications and that switching to Local System creates a different storage root and share world; `Sync and SMB file shares` still saying missing SMB notifications reduce discovery to full folder rescans; `Sync prevents HDD from sleeping on NAS...` plus `How soon does synchronization start?` still letting operators widen or disable rescan cadence entirely; `Configuring Auto Sleep & Battery Saver (Android)` still saying the mobile core can go offline between wake intervals or stop below battery threshold; `Setting network interface per share` still saying forbidden-network posture prevents peers from connecting and new or updated files from being detected; and the maintained v3 line still running through `3.1.2.1076`**.

That candor is good.
The non-clone problem is still freshness-receipt ownership.
Ordinary operators can still be pushed into several help articles before the product fully owns these questions:

- whether an earlier freshness judgment is still current after runtime, path, power, or network posture changed
- whether the change only weakened the claim or expired it entirely
- what event is strong enough to revalidate the claim under the new posture
- where the boundary lies between the old receipt and the new one
- what exact sentence is still safe to say right now about the old finding

AnonSync should therefore make **freshness-claim invalidation** a first-class product object.
Every serious stale-view, missing-update, or `we already checked this` investigation should render prior receipt, invalidator class, drift impact, new proof threshold, supersession boundary, strongest safe sentence, and forbidden stronger sentence before the product treats a past freshness claim as still authoritative.

## Legacy revision notes preserved below

# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0273`
- Timestamp: `2026.03.22.03.47` (America/New_York)
- Codename: `detectioncoveragefreshnessledger`

## What changed in this revision

This revision continues directly from `rev0272` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **filesystem notifications, default 600-second scheduled rescans, manual rescans, watcher exhaustion, IgnoreList reread timing, NAS sleep-preserving cadence changes, and the active v3 line**.
2. Sharpens the non-clone line again: borrow Resilio's candor that immediate detection, periodic discovery, and manual probing are different truths, while refusing any contract where freshness and blindness still have to be inferred from FAQ prose, warning articles, and power-user tuning notes.
3. Adds one new **Resilio evaluation** document focused on how current official docs still spread one ordinary operator answer about `how quickly should this change have been noticed, and what blind window applied?` across FAQ, warning, IgnoreList, and NAS/power-user guidance.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: detection posture, observation coverage review, change freshness review, and change-detection receipt.
5. Extends the doctrine so every serious missing-update or stale-view conclusion now publishes **active detection plane, notification-coverage grade, expected latency budget, blind-window basis, cheapest honest intervention, and strongest safe sentence** before the product treats `stuck`, `late`, or `needs rescan` as durable incident truth.
6. Refreshes the core doctrine documents actually touched in this pass — README, status, evaluation, borrow-line scorecard, architecture decisions, roadmap, open questions, sources, and the new page family — so the tranche is integrated rather than floating.
7. Packages the result as another continuation archive whose new tranche makes the `detection posture / observation coverage review / change freshness review / change-detection receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's change-detection and freshness contract**

This time the evidence is especially clear around **`How soon does synchronization start?` still distinguishing filesystem notifications, default scheduled rescans every 600 seconds, manual rescans, and the fact that `folder_rescan_interval = 0` means no automatic rescan even on restart; `Agent run out of system notify watchers` still saying Linux watcher exhaustion pushes discovery onto periodic or manual rescans; `Ignoring files in Sync (Ignore List)` still saying IgnoreList rereads happen on change or every `folder_rescan_interval` when notifications are not arriving, with restart recommended for immediate effect; `Sync prevents HDD from sleeping on NAS...` still recommending much larger rescan / refresh / save intervals to preserve sleep; and the maintained v3 line still running through `3.1.2.1076`**.

That candor is good.
The non-clone problem is still change-detection ownership.
Ordinary operators can still be pushed into several help articles before the product fully owns these questions:

- whether this subject was actually under timely notification-backed observation
- what detection latency budget was active right now
- whether blindness came from substrate limits, watcher exhaustion, or an intentional power-saving posture
- what manual rescan proves here, and what it does not prove
- what exact sentence is still safe to say about freshness right now

AnonSync should therefore make **change-detection coverage** a first-class product object.
Every serious missing-update, stale-view, or `why has this not appeared yet?` investigation should render active detection plane, latency budget, blind-window basis, coverage grade, cheapest honest intervention, strongest safe sentence, and forbidden stronger sentence before the product treats `delayed`, `stuck`, or `needs rescan` as coherent incident language.

## Legacy revision notes preserved below

# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0272`
- Timestamp: `2026.03.22.03.31` (America/New_York)
- Codename: `routeprovenancetruthledger`

## What changed in this revision

This revision continues directly from `rev0271` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **tracker/relay/LAN/predefined-host posture, direct-versus-relayed route truth, peer-list relay icons, protocol rows, routing/NIC caveats, and the active v3 line**.
2. Sharpens the non-clone line again: borrow Resilio's candor that discovery helpers, effective path, and fallback behavior are different truths, while refusing any contract where the operator still has to infer route provenance from one live icon, one live protocol row, and several help articles.
3. Adds one new **Resilio evaluation** document focused on how current official docs still spread one ordinary operator answer about `what route did this incident actually use, over what window, and did that match policy?` across route architecture, folder settings, performance tables, and troubleshooting prose.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: route posture, route evidence, route divergence review, and route provenance receipt.
5. Extends the doctrine so every serious connectivity or speed-route conclusion now publishes **desired helper posture, desired transport contract, allowed fallback ladder, observed route class, evidence window, route-switch status, mismatch verdict, and strongest safe sentence** before the product treats `direct` or `relay` as durable incident truth.
6. Refreshes the core doctrine documents actually touched in this pass — README, status, borrow-line scorecard, product direction, roadmap, critical open questions, sources, and the update scaffold — so the new tranche is integrated rather than floating.
7. Packages the result as another continuation archive whose new tranche makes the `route posture / route evidence / route divergence review / route provenance receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's route-provenance contract**

This time the evidence is especially clear around **`What ports and protocols are used by Sync?` still separating config-file discovery, tracker communication, direct TCP/UDP attempts, relay fallback, and LAN multicast; `What is a Relay Server?` still explaining that relay is a fallback and still tying relay use to a peer-list icon; `Folder Preferences` still making relay, tracker, LAN search, and predefined hosts per-folder helper posture; `Performance overview` still showing a current peer-table protocol row; `Peers aren't connecting` still naming blocked tracker, blocked relay, blocked listening port, and multi-NIC routing as distinct causes; `Download/upload speed is very slow` still calling out relay penalty and direct-port mapping; and the maintained v3 line still running through `3.1.2.1076`**.

That candor is good.
The non-clone problem is still route-truth ownership.
Ordinary operators can still be pushed into several help articles before the product fully owns these questions:

- what helper posture was intended for this subject?
- what route was actually observed for the relevant pair or cohort?
- whether that route statement covers one glance, one stable window, or the whole incident
- whether the route matched policy or only succeeded through fallback
- what exact sentence is still safe to say about route provenance right now

AnonSync should therefore make **route provenance** a first-class product object.
Every serious connectivity or speed investigation should render desired helper posture, observed path class, witness basis, evidence window, route-switch status, mismatch verdict, strongest safe sentence, and forbidden stronger sentence before the product treats `direct`, `relay`, or `tracker issue` as coherent incident language.

## Legacy revision notes preserved below

# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0271`
- Timestamp: `2026.03.22.03.03` (America/New_York)
- Codename: `representativepairtruthledger`

## What changed in this revision

This revision continues directly from `rev0270` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **per-peer performance tables, asymmetric uploader effects, pairwise iperf benchmarking, per-folder helper policy, all-peer speed escalation, and the active v3 line**.
2. Sharpens the non-clone line again: borrow Resilio's candor that one peer pair, one uploader cohort, and one share-wide incident are different topology claims, while refusing any contract where the operator still has to decide from folklore whether a neat pairwise result really generalizes.
3. Adds one new **Resilio evaluation** document focused on how current official docs still spread one ordinary operator answer about `does this measured pair really stand in for the rest of the mesh?` across performance overview, slow-speed guidance, helper-policy settings, iperf instructions, and all-peer escalation.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: topology slice, representativeness review, topology extrapolation, and topology measurement receipt.
5. Extends the doctrine so every serious pairwise performance conclusion now publishes **covered peer set, direction coverage, route coverage, representative-pair verdict, generalization ceiling, counterexample seats, and reopen boundary** before the product treats one measured pair as mesh truth.
6. Refreshes the core doctrine documents actually touched in this pass — README, status, evaluation, borrow-line scorecard, clone-veto tests, architecture decisions, roadmap, sources, and the update scaffold — so the new tranche is integrated rather than floating.
7. Packages the result as another continuation archive whose new tranche makes the `topology slice / representativeness review / topology extrapolation / topology measurement receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's representative-pair and mesh-wide overclaim contract**

This time the evidence is especially clear around **`Performance overview` still exposing per-peer upload/download/RTT/protocol rows; `Download/upload speed is very slow` still saying one slow uploader can depress other peers and that more strong uploaders can raise the effective download rate while also escalating persistent cases to logs from all peers; `Measuring network performance with iperf3` still prescribing a pairwise benchmark with Sync shut down on both peers; `Folder Preferences` still making relay/tracker/LAN/predefined-host posture a per-folder, all-peers concern; and the maintained v3 line still running through `3.1.2.1076`**.

That candor is good.
The non-clone problem is still topology-claim ownership.
Ordinary operators can still be pushed into several help articles before the product fully owns these questions:

- does this result cover one pair, one uploader cohort, one route segment, or the whole incident?
- which peers or directions remain plausible counterexamples?
- when is a pair only illustrative rather than representative?
- what exact sentence is still safe to say about the wider mesh right now?

AnonSync should therefore make **representative-pair judgment** a first-class product object.
Every serious performance investigation should render covered peer set, flow-role map, direction and route coverage, representative-pair verdict, generalization ceiling, counterexample seats, and forbidden stronger sentence before the product treats one neat pairwise result as system truth.

## Legacy revision notes preserved below

# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0269`
- Timestamp: `2026.03.22.02.07` (America/New_York)
- Codename: `captureposturetruthledger`

## What changed in this revision

This revision continues directly from `rev0268` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **temporary diagnostic posture changes, hidden enablement routes, restart gates, log-buffer inflation, profiler activation, retention defaults, and the active v3 line**.
2. Sharpens the non-clone line again: borrow Resilio's candor that good evidence may require changing runtime posture first, while refusing any contract where the operator still has to remember those temporary deltas from support prose, advanced settings, hidden files, and restart ritual.
3. Adds one new **Resilio evaluation** document focused on how current official docs still spread one ordinary operator answer about `what diagnostic posture changed, when it actually became active, what it cost, and whether baseline was restored` across several support articles and power-user settings.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: instrumentation plan, instrumentation change review, instrumentation restore review, and instrumentation posture receipt.
5. Extends the doctrine so every serious evidence flow now publishes **baseline posture, active diagnostic deltas, activation route, restart truth, residue/retention state, and restoration status** before the product treats `diagnostics enabled` as intelligible.
6. Refreshes the core doctrine documents actually touched in this pass — README, status, evaluation, borrow-line scorecard, clone-veto tests, product direction, interface pattern language, architecture decisions, roadmap, critical open questions, and sources — so the new tranche is integrated rather than floating.
7. Packages the result as another continuation archive whose new tranche makes the `instrumentation plan / instrumentation change review / instrumentation restore review / instrumentation posture receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's instrumentation-posture contract**

This time the evidence is especially clear around **`Collecting debug logs automatically` and `Collecting debug logs manually` still saying operators may enable debug logging in settings or via hidden `debug.txt` and should restart Sync to ensure it is enabled, then reproduce and collect at least 15 minutes of logs; `Collecting debug logs manually` still suggesting larger log size for large-file estates; `Increasing Debug Log size` still saying default rotation is `100 Mbytes`, that `sync.log` is backed up to `sync.log.old`, that operators should raise `log_size` to `200` or more and restart, and that older Linux/NAS versions may still require editing `settings.dat`; `Power user preferences` still listing `log_size 100 (MB)`, `log_ttl 7 (day)`, and `profiler_enabled false`, and still saying `profiler_enabled` writes `profiler.dat`, rotates it every 10 minutes, and requires restart to activate; and the live v3 line still appearing through `3.1.2.1076`.**

Current official docs still openly distinguish real facts such as:

- evidence quality can depend on temporary runtime posture changes before any packet exists
- hidden-file, advanced-setting, and visible-toggle activation routes are not the same thing
- restart and dwell truth matter for whether a capture is trustworthy
- retention, rotation, and local residue are consequences of instrumentation posture, not just export details
- the live Sync v3 line still appears through `3.1.2.1076`

That candor is good.
The non-clone problem is still posture ownership.
Ordinary operators can still be pushed into several articles before the product fully owns these questions:

- what exact diagnostic deltas differ from baseline right now
- whether those deltas are staged, active, or still awaiting restart
- what storage/retention/privacy cost the deltas introduce
- whether the capture window actually ran under the intended posture
- whether the product has returned to baseline or merely stopped talking about diagnostics

AnonSync should therefore make **instrumentation plan** and **instrumentation restore review** first-class product objects.
Every serious evidence handoff should render baseline posture, activation route, restart truth, retention/residue, and restoration status before the product treats `turned diagnostics on` as coherent case handling.

## Legacy revision notes preserved below

# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0268`
- Timestamp: `2026.03.22.01.43` (America/New_York)
- Codename: `intakeartifactprovenanceledger`

## What changed in this revision

This revision continues directly from `rev0267` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **raw artifact locations, hidden-folder harvests, NAS whole-folder copy/cleanup, dump relocation, filename heterogeneity, and the active v3 line**.
2. Sharpens the non-clone line again: borrow Resilio's candor that evidence starts messy and platform-specific, while refusing any contract where the operator still has to scavenge, prune, rename, move, and repack raw artifacts without one durable intake object that preserves provenance.
3. Adds one new **Resilio evaluation** document focused on how current official docs still spread one ordinary operator answer about `what raw material was actually harvested, what class it belongs to, and what cleanup changed before packet assembly` across several support articles and platform rituals.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: raw evidence intake, artifact normalization review, packet assembly review, and intake normalization receipt.
5. Extends the doctrine so every serious evidence flow now publishes **raw-source identity, witness/platform/path provenance, cleanup transforms, duplicate/rotation handling, split decisions, and lineage claim ceiling** before the product treats `logs packed and sent` as intelligible.
6. Refreshes the core doctrine documents actually touched in this pass — README, status, evaluation, borrow-line scorecard, clone-veto tests, product direction, roadmap, critical open questions, and sources — so the new tranche is integrated rather than floating.
7. Packages the result as another continuation archive whose new tranche makes the `raw evidence intake / artifact normalization review / packet assembly review / intake normalization receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's raw-artifact intake contract**

This time the evidence is especially clear around **`Collecting debug logs manually` still naming `sync.log` plus rotated zip logs and varying storage roots by platform/service/config mode; `How to collect logs on NAS manually?` still telling the operator to copy the whole Sync internal-data folder and then clean it up leaving only `*.log`, `*.log.zip`, and `*.journal`; `Collect debug logs on mobiles` still routing harvest through `SNC.DBG.LOGS` and the hidden `.synclogs` folder; crash/core-dump guides still spreading file shapes and paths across `.dmp`, crash-report folders, and gzipped core dumps; and the live v3 line still appearing through `3.1.2.1076`.**

Current official docs still openly distinguish real facts such as:

- raw evidence members genuinely begin in heterogeneous paths and filename shapes
- some flows first produce an overscoped folder and only later a narrowed evidence subset
- moving, pruning, extracting, zipping, or repacking artifacts changes the evidentiary story
- packet assembly is different from raw harvest and different again from export
- the live Sync v3 line still appears through `3.1.2.1076`

That candor is good.
The non-clone problem is still intake ownership.
Ordinary operators can still be pushed into several articles before the product fully owns these questions:

- what raw sources were actually harvested before cleanup began
- what witness/platform/path provenance each source carries
- what should be kept, pruned, grouped as rotations, or held as contradiction witnesses
- what cleanup changed a source into a normalized member
- what lineage ceiling still limits the packet even after successful assembly

AnonSync should therefore make **raw evidence intake** and **artifact normalization review** first-class product objects.
Every serious evidence handoff should render source provenance, transform history, duplicate/rotation handling, split posture, and lineage ceiling before the product treats `collected the logs` as coherent case handling.

## Legacy revision notes preserved below

# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0267`
- Timestamp: `2026.03.22.01.24` (America/New_York)
- Codename: `requestreturntruthledger`

## What changed in this revision

This revision continues directly from `rev0266` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **follow-up asks, return binding, reply-chain expectations, attachment caps, upload-link escalation, and the active v3 line**.
2. Sharpens the non-clone line again: borrow Resilio's candor that later asks really do change the operator's obligations, while refusing any contract where the operator still has to reconstruct `what was asked for`, `how to bind the answer back`, and `what still remains open` from ticket prose, portal ritual, and memory.
3. Adds one new **Resilio evaluation** document focused on how current official docs still spread one ordinary operator answer about `what exactly the recipient asked for, what return lane can carry it, and whether this return fully satisfies the ask` across support articles and channel-specific instructions.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: recipient ask, ask fulfillment review, return lane review, and ask fulfillment receipt.
5. Extends the doctrine so every serious follow-up request now publishes **request clauses, binding token, lane viability, satisfaction ceiling, extra-disclosure warnings, and durable return proof** before the product treats `replied with logs` as understanding.
6. Refreshes the core doctrine documents actually touched in this pass — README, status, evaluation, borrow-line scorecard, clone-veto tests, product direction, interface pattern language, architecture decisions, and report language — so the new tranche is integrated rather than floating.
7. Packages the result as another continuation archive whose new tranche makes the `recipient ask / ask fulfillment review / return lane review / ask fulfillment receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's recipient-ask contract**

This time the evidence is especially clear around **`Collecting debug logs automatically` still telling the operator to indicate which support ticket the logs refer to, plus role, timestamps, detailed description, and affected shares/files; `Collecting debug logs manually` still saying to attach logs in reply to the support ticket, upload logs through the support web portal, mention the forum link if redirected from Forums, and ask support for a bigger upload link if attachments exceed 20 MB; mobile and NAS collection guides still ending in awkward manual-return steps; and the live v3 line still appearing through `3.1.2.1076`.**

Current official docs still openly distinguish real facts such as:

- a later recipient ask is different from the original send
- binding tokens such as ticket numbers and forum links really do matter
- return lanes have practical size and format limits
- sending *something* back is different from satisfying the ask
- the live Sync v3 line still appears through `3.1.2.1076`

That candor is good.
The non-clone problem is still ask ownership.
Ordinary operators can still be pushed into several articles before the product fully owns these questions:

- what exact clauses the recipient asked for
- what binding token or reply chain must carry the answer back
- whether the current packet covers the ask or widens disclosure unnecessarily
- whether the lane can actually carry the packet or needs an upload-link pre-step
- what later receipt proves which ask version was answered and what remained open

AnonSync should therefore make **recipient ask** and **ask fulfillment review** first-class product objects.
Every serious follow-up request should render request clauses, binding token, payload-fit truth, satisfaction ceiling, and reopen language before the product treats `replied with logs` as coherent case handling.

## Legacy revision notes preserved below

# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0266`
- Timestamp: `2026.03.22.01.03` (America/New_York)
- Codename: `companionthreadtruthledger`

## What changed in this revision

This revision continues directly from `rev0265` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **forum/help routing, support-contact language, public-thread/private-packet coupling, manual cross-references, and the active v3 line**.
2. Sharpens the non-clone line again: borrow Resilio's candor that public discussion and private evidence are different audience situations, while refusing any contract where the operator still has to tie forum links, ticket numbers, and support prose together by hand just to keep one case coherent.
3. Adds one new **Resilio evaluation** document focused on how current official docs still spread one ordinary operator answer about `what can be said publicly, what must stay private, and how those artifacts are proven to belong to the same case` across help-center articles and send surfaces.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: companion case, public summary review, private companion linkage, and companion-case receipt.
5. Extends the doctrine so every split-audience help flow now publishes **public-safe minimum claim, private-only detail boundary, companion linkage basis, continuation lane, and durable split-audience receipt** before the product treats `posted on forum` plus `sent logs` as coherent case handling.
6. Refreshes the core doctrine documents actually touched in this pass — README, status, evaluation, borrow-line scorecard, clone-veto tests, product direction, interface grammar, operator workbench, interface pattern language, architecture decisions, report language, roadmap, critical open questions, and sources — so the new tranche is integrated rather than floating.
7. Packages the result as another continuation archive whose new tranche makes the `companion case / public summary review / private companion linkage / companion-case receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's cross-lane companion-case contract**

This time the evidence is especially clear around **`I still have questions, where can I get answers?` still sending users toward the forum while also saying they can contact support with PRO users first to get response and FREE users answered to the extent possible; `Collecting debug logs automatically` still telling the operator to indicate which support ticket the logs refer to plus role, timestamp, detailed description, and affected shares/files; `Collecting debug logs manually` still saying that if the operator was redirected there from Forums they should mention the forum link when sending logs through the support web portal; the log/crash/dump guides still repeating the Business-only direct-support versus Sync v3 self-serve split; and the live v3 line still appearing through `3.1.2.1076`.**

Current official docs still openly distinguish real facts such as:

- public/community discussion and private evidence packets are not the same audience situation
- contextual references such as ticket numbers and forum links really do matter for continuity
- a case can legitimately need both a public-safe summary and a private packet
- posting a summary is different from delivering private evidence and different again from proving the two belong to the same case
- the live Sync v3 line still appears through `3.1.2.1076`

That candor is good.
The non-clone problem is still companion-case ownership.
Ordinary operators can still be pushed into several articles before the product fully owns these questions:

- what minimum useful claim is safe to state publicly
- what details must stay private-only
- how the public summary and private packet are durably linked
- what continuation belongs in the public lane, the private lane, or both
- what later receipt proves which side of the companion case exists, which is missing, and what was intentionally withheld

AnonSync should therefore make **companion case** and **public summary review** first-class product objects.
Every serious split-audience help flow should render public-safe claim, redaction boundary, companion linkage, continuation lane, and split-audience receipt language before the product treats `forum post` plus `logs sent` as coherent case handling.

## Legacy revision notes preserved below

# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0265`
- Timestamp: `2026.03.22.00.46` (America/New_York)
- Codename: `escalationlanetruthledger`

## What changed in this revision

This revision continues directly from `rev0264` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **support-lane entitlement, destination ambiguity, business-vs-v3 routing, forum/web-form/ticket split, and the active v3 line**.
2. Sharpens the non-clone line again: borrow Resilio's candor that audience and entitlement matter, while refusing any contract where the operator still has to reconcile `Contact support`, Biz-only technical-support language, forum/help-center self-service, billing/licensing web forms, and vague response expectations from several articles.
3. Adds one new **Resilio evaluation** document focused on how current official docs still spread one ordinary operator answer about `who should receive this package, why this lane is valid, what audience will see it, and what response is actually plausible` across help-center articles and surface chrome.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: escalation lane, escalation review, destination confirmation, and escalation lane receipt.
5. Extends the doctrine so every serious outward help/handoff attempt now publishes **available lanes, entitlement basis, audience class, package-fit verdict, destination visibility, and response ceiling** before the product treats an upload or form submission as a meaningful escalation act.
6. Refreshes the core doctrine documents actually touched in this pass — README, status, evaluation, borrow-line scorecard, clone-veto tests, product direction, architecture decisions, diagnostic-evidence doctrine, critical open questions, and sources — so the new tranche is integrated rather than floating.
7. Packages the result as another continuation archive whose new tranche makes the `escalation lane / route review / destination confirmation / lane receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's escalation-lane contract**

This time the evidence is especially clear around **current log/crash/dump guides still saying technical support is available exclusively for Business customers while Sync v3 functionality questions should go through forum/help-center self-service and payments/licensing should use a web form; the same automatic-log guide still telling the operator to open an in-app `Contact support` form; `I still have questions, where can I get answers?` still saying users can also contact support with PRO users first to get response and FREE users answered to the extent possible; `Licensing in Resilio Sync 3.0` still saying Business licenses are not compatible with Sync v3 and commercial users should continue using Sync v2 or explore business solutions; and the live v3 line still appearing through `3.1.2.1076`.**

Current official docs still openly distinguish real facts such as:

- support/help lanes differ by product line and question class
- billing/licensing questions are not the same lane as functionality troubleshooting
- audience matters: public/community, private support, billing desk, peer, and local-only are not interchangeable
- upload/send success is different from route validity and different again from any owed answer
- the live Sync v3 line still appears through `3.1.2.1076`

That candor is good.
The non-clone problem is still lane ownership.
Ordinary operators can still be pushed into several articles before the product fully owns these questions:

- which route is actually valid for this question and product line
- who the audience really is for this package
- whether the current package shape fits that destination
- what privacy and visibility posture follows from the chosen lane
- what response expectation is honest instead of wishful
- what later receipt proves why this lane was chosen and when it should be reopened or redirected

AnonSync should therefore make **escalation lane** and **destination confirmation** first-class product objects.
Every serious outward help or handoff attempt should render entitlement basis, lane comparison, audience visibility, package-fit verdict, and response-ceiling language before the product treats `submit`, `post`, or `contact support` as understanding.

## Legacy revision notes preserved below

# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0264`
- Timestamp: `2026.03.22.00.33` (America/New_York)
- Codename: `packagemeaningmanifestledger`

## What changed in this revision

This revision continues directly from `rev0263` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **artifact-class sprawl, package opacity, platform-specific capture routes, transport preconditions, and the active v3 line**.
2. Sharpens the non-clone line again: borrow Resilio's candor that different incidents need different artifact families and that collection has real preconditions, while refusing any contract where the operator still has to assemble the package story from separate support articles and hidden file paths.
3. Adds one new **Resilio evaluation** document focused on how current official docs still spread one ordinary operator answer about `what evidence classes are in this package, why are they here, what preconditions were needed, and what exactly was exported` across troubleshooting articles and support guides.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: evidence plan, artifact capture matrix, evidence manifest review, and evidence export receipt.
5. Extends the doctrine so every serious escalation now publishes **question-to-artifact mapping, platform-specific preconditions, manifest membership, package sensitivity, completeness ceiling, and export-lane receipt** before the product treats `logs sent` or `files attached` as understanding.
6. Refreshes the core doctrine documents actually touched in this pass — README, evaluation, borrow-line scorecard, clone-veto tests, product direction, roadmap, operator workbench, interface pattern language, architecture decisions, diagnostic-evidence doctrine, critical open questions, and sources — so the new tranche is integrated rather than floating.
7. Packages the result as another continuation archive whose new tranche makes the `evidence plan / capture matrix / manifest / export receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's package-assembly contract**

This time the evidence is especially clear around **the current `Send info to Support team` section still distributing separate guides for automatic logs, manual logs, mobile logs, crash reports / dumps, NAS dumps, iperf3, and log-size tuning; `Collecting debug logs automatically` still saying Biz customers get direct support while Sync v3 users are pushed toward forum/help-center self-service, keep-the-device-open send ritual, and manual fallback for desktops/NAS; `Collecting debug logs manually` still naming artifact files and platform storage paths; `Increasing Debug Log size` still documenting 100 MB rotation with `.old`, possible insufficiency, and no mobile adjustment; and the live v3 line still appearing through `3.1.2.1076`.**

Current official docs still openly distinguish real facts such as:

- different questions can require different artifact families
- some artifact families have platform-specific capture routes and hidden storage paths
- some artifact classes require disruptive preconditions such as shutting Sync down or waiting for a crash
- transport completion is different from package meaning
- the live Sync v3 line still appears through `3.1.2.1076`

That candor is good.
The non-clone problem is still package ownership.
Ordinary operators can still be pushed into several docs before the product fully owns these questions:

- what exact question each requested artifact class is meant to answer
- which preconditions were required to make this package meaningful
- what files or measurements are actually inside the package
- what sensitivity and completeness ceiling this manifest carries
- what later receipt proves what was exported, by which lane, and with what stale boundary

AnonSync should therefore make **evidence plan** and **evidence manifest review** first-class product objects.
Every serious escalation should render artifact rationale, platform preconditions, manifest membership, sensitivity findings, completeness verdict, and export receipt language before the product treats packet existence as case understanding.

## Legacy revision notes preserved below

# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0263`
- Timestamp: `2026.03.22.00.24` (America/New_York)
- Codename: `timeanchorsignalledger`

## What changed in this revision

This revision continues directly from `rev0262` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **freeform support narrative, symptom timestamps, affected share/file naming, reproduction dwell, send-completion ritual, and the active v3 line**.
2. Sharpens the non-clone line again: borrow Resilio's candor that artifacts need event context and that capture must surround an actual symptom, while refusing any contract where the operator still has to type the case brief into support prose and remember whether the reproduction run actually caught the target event inside a usable evidence window.
3. Adds one new **Resilio evaluation** document focused on how current official docs still spread one ordinary operator answer about `what exact symptom are we chasing, when did it happen, what subjects are implicated, and did this capture run really catch it?` across troubleshooting pages and log guides.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: incident brief, symptom bookmark, coordinated capture run, and capture brief receipt.
5. Extends the doctrine so every serious multi-step evidence attempt now publishes **problem statement, time-anchor quality, affected-subject scope, coordinated run semantics, usable evidence window, and stale/reopen boundary** before the product treats a packet as self-explanatory.
6. Refreshes the core doctrine documents actually touched in this pass — README, status, evaluation, borrow-line scorecard, clone-veto tests, product direction, interface grammar, operator workbench, interface pattern language, architecture decisions, roadmap, diagnostic-evidence doctrine, critical open questions, and sources — so the new tranche is integrated rather than floating.
7. Packages the result as another continuation archive whose new tranche makes the `incident brief / symptom bookmark / coordinated run / usable evidence window` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's capture-brief contract**

This time the evidence is especially clear around **`Collecting debug logs automatically` still asking for reproduction, at least 15 minutes of collection, feedback text naming peer role, timestamps, detailed description, and affected shares/files, the same guide still warning not to close the application/device until sending is done, `Collecting debug logs manually` still asking the operator to describe the issue and mention the forum link when redirected, and the live v3 line still appearing through `3.1.2.1076`**.

Current official docs still openly distinguish real facts such as:

- artifacts need event context to be interpretable
- reproduction is different from activation and different again from successful send
- symptom timestamps and affected subjects are meaningful evidence anchors
- a pairwise incident still implies a specific failing event even when the product does not preserve the brief as a first-class object
- the live Sync v3 line still appears through `3.1.2.1076`

That candor is good.
The non-clone problem is still capture-brief ownership.
Ordinary operators can still be pushed into several docs before the product fully owns these questions:

- what exact symptom this evidence packet is supposed to explain
- which timestamp or event window later pages should inherit
- which shares/files truly belong in the brief
- whether the coordinated run actually caught the target symptom
- what later receipt proves the evidence window is usable rather than merely collected

AnonSync should therefore make **incident brief** and **coordinated capture run** first-class product objects.
Every serious evidence attempt should render problem statement, time-anchor quality, affected-subject scope, run semantics, evidence-window strength, and receipt language before the product treats support text or packet existence as understanding.

## Legacy revision notes preserved below

# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0262`
- Timestamp: `2026.03.22.00.11` (America/New_York)
- Codename: `witnessscopepeerledger`

## What changed in this revision

This revision continues directly from `rev0261` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **pairwise-vs-all-peer evidence asks, peer-role annotation inside log submissions, manual-vs-automatic witness return routes, and the active v3 line**.
2. Sharpens the non-clone line again: borrow Resilio's candor that different incidents need different witness counts, while refusing any contract where the operator still has to infer `who owes evidence`, narrate peer role in prose, and remember whether `two peers`, `all peers`, or a narrower sampled set was actually enough.
3. Adds one new **Resilio evaluation** document focused on how current official docs still spread one ordinary operator answer about `which peers matter for this case, what role each plays, and when the witness set is complete enough` across troubleshooting articles and log-collection guides.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: incident witness set, witness request, witness completeness review, and witness-set receipt.
5. Extends the doctrine so every multi-peer diagnostic now publishes **minimal participant set, role typing, evidence duty, witness completeness, and claim ceiling** before the product treats a packet as representative.
6. Refreshes the core doctrine documents actually touched in this pass — README, status, evaluation, product direction, interface grammar, interface flows, operator workbench, architecture decisions, roadmap, diagnostic-evidence doctrine, escalation doctrine, critical open questions, and sources — so the new tranche is integrated rather than floating.
7. Packages the result as another continuation archive whose new tranche makes the `incident / witness set / participant ask / completeness / receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's witness-scope contract**

This time the evidence is especially clear around **`Peers aren't connecting` still asking for logs from two peers, `My files don't sync` and the speed-improvement article still asking for logs from all peers, the automatic-log guide still asking the operator to describe the role of that peer in the setup plus timestamps and affected shares/files, and the live v3 line still appearing through `3.1.2.1076`**.

Current official docs still openly distinguish real facts such as:

- some incidents are pairwise while others are share-wide
- peer role is meaningful evidence, not optional prose decoration
- returned artifacts need witness metadata such as timestamps and affected subjects
- witness completeness is different from mere packet existence
- the live Sync v3 line still appears through `3.1.2.1076`

That candor is good.
The non-clone problem is still witness ownership.
Ordinary operators can still be pushed into several docs before the product fully owns these questions:

- which peers actually matter for this incident
- what role each peer plays in the current explanation
- what evidence is owed by each participant
- whether the current witness set is complete enough for the claim being made
- what later receipt proves which witnesses were requested, returned, or missing

AnonSync should therefore make **incident witness set** and **witness completeness review** first-class product objects.
Every serious multi-peer diagnostic should render participant scope, role typing, evidence duty, completeness verdict, safe-language ceiling, and receipt language before the product treats a log packet as representative or asks an operator to narrate topology from memory.

## Legacy revision notes preserved below

# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0261`
- Timestamp: `2026.03.22.00.06` (America/New_York)
- Codename: `casefiletruthledger`

## What changed in this revision

This revision continues directly from `rev0260` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **main-view row semantics, troubleshooting route archaeology, item-level locked-file detail, debug-log capture ritual, and the active v3 line**.
2. Sharpens the non-clone line again: borrow Resilio's candor that diagnosis really does span rows, peers, history, queues, item lists, and heavier evidence capture, while refusing any contract where the operator still has to remember the investigation as a mental story.
3. Adds one new **Resilio evaluation** document focused on how current official docs still scatter one ordinary operator answer about `what case am I in, what have I already checked, what is still missing, and is heavier capture justified yet?` across row clicks, history search, peer/queue checks, and log guides.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: diagnostic incident page, incident timeline, evidence sufficiency review, and diagnostic conclusion receipt.
5. Extends the doctrine so every serious diagnostic now publishes **entry point, current best explanation, live alternatives, braided chronology, proof-sufficiency verdict, and durable conclusion memory** before the product treats investigation as folklore.
6. Refreshes the core doctrine documents actually touched in this pass — README, status, evaluation, borrow-line scorecard, clone-veto tests, product direction, operator workbench, interface pattern language, architecture decisions, roadmap, critical open questions, and sources — so the new tranche is integrated rather than floating.
7. Packages the result as another continuation archive whose new tranche makes the `incident home / braided timeline / sufficiency review / conclusion receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's investigation contract**

This time the evidence is especially clear around **the main view still splitting rows, peers counts, and 30-day history into distinct surfaces; `My files don't sync` still instructing operators to hop across peers, status, history, queue, and later all-peer log collection; `Locked files` still opening affected files while admitting it cannot identify the locker; automatic and manual debug-log guides still imposing restart, time-window, and route rituals; and the live v3 line still appearing through `3.1.2.1076`**.

Current official docs still openly distinguish real facts such as:

- diagnosis is genuinely multi-surface
- item-level detail is different from row meaning
- heavier evidence capture has real time and support-lane consequences
- clickability itself remains part of the operator contract
- the live Sync v3 line still appears through `3.1.2.1076`

That candor is good.
The non-clone problem is still investigation ownership.
Ordinary operators can still be pushed across several surfaces before the product fully owns these questions:

- what investigation this is
- what has already been checked
- which explanation currently leads
- what exact proof is still missing
- whether heavier capture is really justified now
- what conclusion should survive handoff or later reopening

AnonSync should therefore make **diagnostic incident** and **evidence sufficiency** first-class product objects.
Every serious diagnostic should render entry point, current best explanation, live alternatives, chronology, proof budget, and conclusion receipt language before the product treats investigation as memory or support ritual.

## Legacy revision notes preserved below

# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0260`
- Timestamp: `2026.03.21.23.55` (America/New_York)
- Codename: `drillrouteproofledger`

## What changed in this revision

This revision continues directly from `rev0259` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **status-click drill-in, KB-linked warning explanation, peers/history/queue detours, per-warning affected-item lists, and the active v3 line**.
2. Sharpens the non-clone line again: borrow Resilio's candor that rows should be clickable and diagnostic, while refusing any contract where the operator still has to hop from status row to KB article to peers list to history to queue before the product itself owns the current answer.
3. Adds one new **Resilio evaluation** document focused on how current official docs still spread one ordinary operator answer about `what exactly should I open next from this failing row, and what will that click actually prove?` across main-view docs, troubleshooting prose, item-specific warning pages, and changelog notes.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: status drilldown, diagnostic router, affected items, and diagnostic route receipt.
5. Extends the doctrine so every serious status token now publishes **local explanation, subject scope, affected-item slice, best-next routes, and a durable route receipt** before the product treats a click as self-explanatory or ejects the operator into external help.
6. Refreshes the core doctrine documents actually touched in this pass — README, status, evaluation, borrow-line scorecard, clone-veto tests, product direction, operator workbench, interface pattern language, architecture decisions, roadmap, critical open questions, and sources — so the new tranche is integrated rather than floating.
7. Packages the result as another continuation archive whose new tranche makes the `status row / owned explanation / route choice / affected-item proof` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's diagnostic route contract**

This time the evidence is especially clear around **the main view still defining status and peers rows, troubleshooting still telling operators to click status rows that often lead to KB explanations, `Locked files` still opening a file list but not identifying the locker, and the live v3 line still recording that `Can't download file` had to be fixed to be clickable at all**.

Current official docs still openly distinguish real facts such as:

- some rows are meant to be clicked for more detail
- peers count, history, queue, and warning item lists are materially different diagnostic surfaces
- item-level detail is sometimes separate from the warning meaning itself
- clickability itself can be part of the operator contract
- the live Sync v3 line still appears through `3.1.2.1076`

That candor is good.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed across several surfaces before the product fully owns these questions:

- what this current row is actually proving
- whether the next click opens local proof, item-level detail, or external prose
- which diagnostic route is strongest for the current subject
- which concrete files/items are implicated right now
- what later receipt proves which route was taken and which conclusion was actually earned

AnonSync should therefore make **status drilldown** and **diagnostic router** first-class product objects.
Every serious status token should render local explanation, scope, affected-item slice, best-next route, claim ceiling, and route receipt language before the product treats a row click as mere decoration or troubleshooting folklore.

## Legacy revision notes preserved below
# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0259`
- Timestamp: `2026.03.21.23.18` (America/New_York)
- Codename: `warningblastladderproof`

## What changed in this revision

This revision continues directly from `rev0258` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **core warnings, service-file continuity damage, chronology-invalid warnings, no-source warnings, recoverable hidden-work warnings, and the active v3 line**.
2. Sharpens the non-clone line again: borrow Resilio's candor that warnings are typed and materially different, while refusing any contract where operators still reconstruct `what kind of warning is this, how wide is it, what is the least-strong safe next rung, and what did acknowledgement actually change` from several articles.
3. Adds one new **Resilio evaluation** document focused on how current official docs still spread one ordinary operator answer about warning meaning and repair strength across core-warning rows, one-off warning pages, and troubleshooting prose.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: warning page, blocker scope, recovery rung, and warning history.
5. Extends the doctrine so every serious warning now publishes **class, blast radius, strongest safe sentence, least-strong next rung, acknowledgement semantics, and recurrence/residue memory** before commitment.
6. Refreshes the core doctrine documents actually touched in this pass — README, status, evaluation, borrow-line scorecard, product direction, roadmap, critical open questions, and sources — so the new tranche is integrated rather than floating.
7. Packages the result as another continuation archive whose new tranche makes the `warning class / blast radius / least-strong repair / acknowledgement residue` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's warning contract**

This time the evidence is especially clear around **Core warnings that still separate infrastructure, storage, identity-sync, and license-management conditions; `Service files missing` docs that still suspend synchronization for the folder; `Some internal tasks...` docs that still say the condition may be recoverable hidden work rather than a hard stall; `Time difference` docs that still invalidate chronology trust; and `Cannot download files` docs that still name no-source ghost states**.

Current official docs still openly distinguish real facts such as:

- not every warning is the same class of truth
- blast radius can be item-local, subject-local, seat-local, or continuity-bearing hidden-state damage
- the least-strong safe next rung differs by warning class
- acknowledgement is weaker than repair
- the live Sync v3 line still appears through `3.1.2.1076`

That candor is good.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed into several docs before the product fully owns these questions:

- what kind of warning this is
- how wide the current blocker really is
- what the least-strong honest next move should be
- what stronger move would widen or destroy more state
- what later history proves whether the condition self-cleared, was merely acknowledged, or was actually repaired

AnonSync should therefore make **warning page** and **recovery rung** first-class product objects.
Every serious warning should render class, scope, safe wording boundary, least-strong next rung, acknowledgement semantics, recurrence memory, and receipt/history language before the product treats a banner as self-explanatory.

## Legacy revision notes preserved below

# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0258`
- Timestamp: `2026.03.21.22.47` (America/New_York)
- Codename: `pausedoriginmatrixtruth`

## What changed in this revision

This revision continues directly from `rev0257` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **manual pause, scheduled `Paused`, global pause placement, delete-through/indexing-through behavior, and origin-dependent outbound semantics under the same visible word**.
2. Sharpens the non-clone line again: borrow Resilio's candor that pause is selective and origin-bearing, while refusing any contract where the same visible token such as `Paused` can quietly mean different live signal matrices depending on origin.
3. Adds one new **Resilio evaluation** document focused on how current official docs still spread one ordinary operator answer about `what exactly does this state word mean here?` across pause how-to, scheduler docs, and preferences.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: state token posture, state token change review, state token evidence, and state token receipt.
5. Extends the interface/workbench doctrine so every serious visible state word now publishes **origin, full signal matrix, live exceptions, semantic-stability verdict, and strongest safe sentence** before commit.
6. Refreshes the core doctrine documents actually touched in this pass — README, status, evaluation, borrow-line scorecard, clone-veto tests, product direction, interface grammar, architecture decisions, and sources — so the new tranche is integrated rather than floating.
7. Packages the result as another continuation archive whose new tranche makes the `visible word / origin / signal matrix / wording honesty` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's named-state contract**

This time the evidence is especially clear around **manual pause docs that still say pause only stops bit upload/download while deletions and indexing continue, scheduler docs that still use the same word `Paused` but let paused peers upload to non-paused peers, and preferences that still keep Global Pause and Scheduler adjacent as ordinary controls**.

Current official docs still openly distinguish real facts such as:

- `Paused` is not the same answer as `fully frozen`
- delete propagation and indexing can remain alive under pause
- scheduler-origin pause can still have different documented outbound semantics than manual pause
- the visible word alone is weaker than the true signal matrix
- the live Sync v3 line still appears through `3.1.2.1076`

That candor is good.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed into several docs before the product fully owns these questions:

- what exact signal matrix this state word means right now
- whether the same visible word means something different under another origin
- which exceptions remain alive under the token
- what stronger sentence the product refuses to say because it would overstate the truth
- what later receipt proves the visible token and matrix that were actually in force

AnonSync should therefore make **state token posture** and **state token change review** first-class product objects.
Every serious visible state word should render origin, active matrix, live exceptions, semantic-stability verdict, safe wording boundary, and receipt language before the product treats `Paused`, `Connected`, or any other calm badge as self-explanatory.

## Legacy revision notes preserved below

# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0257`
- Timestamp: `2026.03.21.22.26` (America/New_York)
- Codename: `replayclassshiftceiling`

## What changed in this revision

This revision continues directly from `rev0256` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **piecewise replay, piece-shift whole-file fallback, Business-only stronger diff-delta language in the public FAQ, and enterprise/job-profile policy that can intentionally choose full resend over local differential recheck**.
2. Sharpens the non-clone line again: borrow Resilio's candor that replay cost is workload-shaped and policy-bearing, while refusing any contract where operators still reconstruct `what replay class is active here, when will edits trigger whole resend, and which stronger replay lane is unavailable` from FAQ pages and enterprise tuning docs.
3. Adds one new **Resilio evaluation** document focused on how current official docs still spread one ordinary operator answer about `how expensive will the next changed-file replay actually be?` across Sync FAQ material and official Resilio documentation.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: replay class posture, replay cost review, replay evidence, and replay receipt.
5. Extends the interface/workbench doctrine so every serious changed-file replay claim now publishes **current replay class, fallback/full-resend ceiling, edit-shape risk, hash basis, stronger unavailable class, and strongest safe sentence** before commit.
6. Refreshes the core doctrine documents actually touched in this pass — README, status, evaluation, borrow-line scorecard, clone-veto tests, product direction, pattern language, architecture decisions, roadmap, critical open questions, and sources — so the new tranche is integrated rather than floating.
7. Packages the result as another continuation archive whose new tranche makes the `incremental claim / piece-shift fallback / differential lane / replay-cost review` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's mutable replay-class contract**

This time the evidence is especially clear around **public Sync FAQ language that usually only changed pieces are transferred, but that piece-shifting edits can still force a whole-file resend; Business-only stronger diff-delta language for that case; and official Resilio documentation that still lets administrators intentionally choose full resend or changed-piece replay depending on hash policy, storage cost, and workload shape**.

Current official docs still openly distinguish real facts such as:

- `changed parts only` is not the same truth as `diff-delta replay survives piece shifts`
- piecewise replay can still collapse to whole-file resend when edit shape shifts later blocks
- replay class can be weakened intentionally to save local CPU/disk work
- stronger replay may be edition-, runtime-, or policy-gated rather than universally available
- the live Sync v3 line still appears through `3.1.2.1076`

That candor is good.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed into several docs before the product fully owns these questions:

- what replay class is active for this subject right now
- whether the current promise survives prefix-insert or other piece-shifting edits
- whether replay is limited by edit shape, missing hashes, disabled differential policy, or product tier
- what stronger replay class exists but is unavailable here
- what later receipt proves the class that was actually in force when the policy was committed

AnonSync should therefore make **replay class posture** and **replay cost review** first-class product objects.
Every serious replay-affecting change should render current class, fallback ceiling, edit-shape risk, hash basis, unavailable stronger class, and receipt language before the product treats `incremental`, `delta`, or `optimize transfer` as self-explanatory.

## Legacy revision notes preserved below

# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0255`
- Timestamp: `2026.03.21.21.43` (America/New_York)
- Codename: `equivalencebasismutabletruth`

## What changed in this revision

This revision continues directly from `rev0254` and does seven concrete things:

1. Re-checks another current official Resilio / Active Everywhere cluster around **pre-seeded compare rules, mutable `needs sync` equations, file-property scope, optional metadata/permission planes, and later-apply parity on incompatible storage**.
2. Sharpens the non-clone line again: borrow Resilio's candor that `same file` and `needs sync` are policy-bearing judgments, while refusing any contract where ordinary equality meaning leaks across pre-seed guidance, property tables, permission docs, and troubleshooting notes.
3. Adds one new **Resilio evaluation** document focused on how current official docs still spread one ordinary operator answer about `what counts as the same file here?` across several page families.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: equality posture, candidate equivalence review, equality evidence, and equivalence receipt.
5. Extends the interface/workbench doctrine so every serious sameness claim now publishes **effective compare plane, proof class, optional planes in/out of scope, later-apply ceilings, and strongest safe sentence** before commit.
6. Refreshes the core doctrine documents actually touched in this pass — README, status, evaluation, borrow-line scorecard, clone-veto tests, roadmap, critical open questions, and sources — so the new tranche is integrated rather than floating.
7. Packages the result as another continuation archive whose new tranche makes the `same file / needs sync / compare plane / proof ceiling` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's mutable equality contract**

This time the evidence is especially clear around **pre-seeded folders using creation time, modification time, size, and permissions as the quick `needs sync` equation; current docs also saying creation time or permission planes can be removed from that equation; property carriage still varying by platform and version; and permissions still being preservable on incompatible storage for later application rather than native parity now**.

Current official docs still openly distinguish real facts such as:

- `same enough to stay quiet` and `fully parity-proven` still being different realities
- optional planes like permissions, xattrs/streams, and platform-local decorations still not sharing one universal fate
- some seats still being able to carry later-apply meaning without honestly claiming native parity now
- bundle/object fidelity still narrowing when optional metadata planes are removed
- the live Sync v3 line still appearing through `3.1.2.1076`

That candor is good.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed into several docs before the product fully owns these questions:

- what exact properties currently define `same file` for this subject
- whether quietness came from quick-attribute agreement, full content proof, or only a narrowed compare plane
- which optional planes are in scope, disabled, or merely preserved for later compatible landing
- whether this seat can honestly claim native parity or only content parity plus deferred side planes
- what later receipt proves the compare basis that was actually used

AnonSync should therefore make **equality posture** and **candidate equivalence review** first-class product objects.
Every serious sameness claim should render effective compare plane, proof class, optional-plane status, later-apply ceiling, and receipt language before the product treats `same`, `up to date`, or `nothing to do` as self-explanatory.

## Legacy revision notes preserved below

# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0254`
- Timestamp: `2026.03.21.23.59` (America/New_York)
- Codename: `indirectiontargetceiling`

## What changed in this revision

This revision continues directly from `rev0253` and does seven concrete things:

1. Re-checks another current official Resilio Sync cluster around **soft links, hard links, symbolic links, junction-driven `.Conflict` fallout, platform split, and target non-transitivity**.
2. Sharpens the non-clone line again: borrow Resilio's candor that indirection objects are real and dangerous, while refusing any contract where an ordinary file-or-folder row hides whether the object itself survives, whether target bytes are included, and whether conflicts are expected on this seat family.
3. Adds one new **Resilio evaluation** document focused on how current Resilio still spreads one ordinary operator answer about `is this entry itself syncing, is its target syncing, or is this just a conflict generator here?` across link docs, conflict docs, and troubleshooting folklore.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: indirection posture, indirection action review, target transitivity proof, and indirection receipt.
5. Extends the interface/workbench doctrine so every serious alias-edge object now publishes **entry kind, platform lane, object fate, target scope, transitivity verdict, conflict hazard, and strongest safe sentence** before commit.
6. Refreshes status-bearing doctrine documents — status, evaluation, scorecard, clone-veto tests, product direction, roadmap, open questions, daemon API, sources, and README — so the new tranche is integrated rather than bolted on.
7. Packages the result as another continuation archive whose new tranche makes the `entry object / target bytes / platform split / conflict hazard` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's indirection-object contract**

This time the evidence is especially clear around **Windows treating soft links, hard links, junctions, and symbolic links as unsupported and conflict-prone, Unix preserving symbolic links while excluding target folders unless separately added, and conflict guidance still naming linked junctions as a direct conflict cause**.

Current official docs still openly distinguish real facts such as:

- Windows still not supporting soft links, junctions, hard links, or symbolic links in Sync, with `.Conflict` fallout still called out for each affected entry
- Unix still being able to synchronize symbolic links as links while target folders are still not synchronized unless added separately
- current conflict guidance still naming linked junctions as a concrete cause of `.Conflict` files or folders
- the live Sync v3 line still appearing through `3.1.2.1076`

That candor is good.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed into several help pages before the product fully owns these questions:

- whether this row is an ordinary file/folder or an indirection object with a different fidelity contract
- whether the entry object itself survives, is flattened, is blocked, or is conflict-prone on this seat family
- whether target bytes are included now, excluded entirely, or require explicit separate admission
- whether following the target would widen the sync graph beyond what the current share already means
- what later receipt can prove the exact entry-kind and target-transitivity verdict that was applied

AnonSync should therefore make **indirection posture** and **target transitivity proof** first-class product objects.
Every serious alias-edge path should render entry kind, platform lane, object fate, target scope, transitivity verdict, conflict hazard, safe substitution ladder, and receipt language before the product treats the row as just another ordinary file or folder.

## Legacy revision notes preserved below

# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0253`
- Timestamp: `2026.03.21.21.13` (America/New_York)
- Codename: `identityfatesurvivalcliff`

## What changed in this revision

This revision continues directly from `rev0252` and does seven concrete things:

1. Re-checks another current official Resilio Sync cluster around **identity-linking certificate takeover, identity renaming by unlink/recreate, uninstall guidance, subject-class fallout, and platform-specific byte deletion on iOS / Windows Phone**.
2. Sharpens the non-clone line again: borrow Resilio's candor that identity actions have real local consequences, while refusing any contract where an account-looking verb such as `unlink`, `rename identity`, `link running installs`, or `uninstall` quietly changes subject governance and byte survival by class and platform.
3. Adds one new **Resilio evaluation** document focused on how current Resilio still spreads one ordinary operator answer about `what survives this identity action on this seat?` across linking guidance, identity FAQ, uninstall guidance, and mobile-platform caveats.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: identity-action review, subject-fate matrix, preserve-before-identity-action, and identity-action receipt.
5. Extends the interface/workbench doctrine so every serious identity-changing action now publishes **requested verb, affected subject classes, app-removal effect, local-byte survival by platform, preserve-first alternatives, and strongest safe sentence** before commit.
6. Refreshes status-bearing doctrine documents — status, evaluation, scorecard, clone-veto tests, product direction, roadmap, open questions, sources, and README — so the new tranche is integrated rather than bolted on.
7. Packages the result as another continuation archive whose new tranche makes the `identity verb / subject fate / mobile deletion asymmetry` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's account-looking identity-action contract**

This time the evidence is especially clear around **linking two already-running installs, renaming identity only by unlinking and creating a new certificate, uninstall guidance that clears Advanced then Standard in sequence, and platform-specific file deletion on iOS / Windows Phone**.

Current official docs still openly distinguish real facts such as:

- linking two already-running Sync installs still causing one device to lose its certificate, remove Advanced folders from the app, and copy folders from the other instance
- iOS still deleting those Advanced folders from the file system when that certificate takeover happens
- changing identity name still requiring unlink + new identity creation, still removing Advanced folders from the instance, and still preserving Standard folders differently
- that preservation sentence still having a mobile carve-out: folders remain in the system except on iOS and Windows Phone
- uninstall guidance still telling operators to unlink from identity first, then remove remaining Standard shares, while desktop uninstall generally leaves previously shared folders in the file system
- iOS and Windows Phone uninstall still removing synced files from the device because of platform architecture
- the live Sync v3 line still appearing through `3.1.2.1076`

That candor is good.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed into several help pages before the product fully owns these questions:

- is this verb only changing identity or also evicting some subject classes from app governance
- which local bytes survive, and which are deleted because of platform architecture
- whether `Advanced`, `Standard`, and already-landed local files are surviving differently on this seat
- whether the safe next move is `unlink`, `rename`, `relink`, `export first`, `branch first`, or `do not proceed here`
- what later receipt can prove about the exact fate of each local subject after the action

AnonSync should therefore make **identity-action review** and **subject-fate matrix** first-class product objects.
Every serious identity-changing action should render requested verb, affected subject classes, app-removal effect, local-byte survival by platform, preserve-first alternatives, and receipt language before the product treats identity work as mere account housekeeping.

## Legacy revision notes preserved below

## Legacy revision notes preserved below

# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0251`
- Timestamp: `2026.03.21.20.50` (America/New_York)
- Codename: `permissionreferenceceiling`

## What changed in this revision

This revision continues directly from `rev0250` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **permission-sync modes, Reference Agent authority, inheritance rewrite, privilege floor, substrate-delayed apply, and the active official lines**.
2. Sharpens the non-clone line again: borrow Resilio's candor that file-permission meaning is real and operationally sharp, while refusing any contract where `sync permissions` collapses mode, authority, privilege, and apply substrate into one checkbox.
3. Adds one new **Resilio evaluation** document focused on how current official docs still spread one ordinary operator answer about `what permission contract is actually in force here?` across a mode page, profiles table, Reference Agent guide, and pre-seeded best-practice notes.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: permission-plane posture, permission-plane change review, permission-apply evidence, and permission-plane receipt.
5. Extends the interface/workbench doctrine so every serious permission-bearing subject now publishes **mode, authority basis, apply substrate, privilege floor, compare participation, and strongest safe sentence** before commit.
6. Refreshes status-bearing doctrine documents — status, evaluation, scorecard, clone-veto tests, product direction, interface, architecture, open questions, sources, and README — so the new tranche is integrated rather than bolted on.
7. Packages the result as another continuation archive whose new tranche makes the `permission mode / reference authority / local re-inheritance` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's permission-plane contract**

This time the evidence is especially clear around **permission-sync modes, Reference Agent authority, local re-inheritance, delayed apply on incompatible storage, and privilege-floor truth**.

Current official docs still openly distinguish real facts such as:

- permission synchronization still having distinct modes rather than one behavior
- `Re-apply local inherited permissions` still existing because partial downloads pass through the service `.sync` directory
- NTFS or POSIX permissions still being preservable on incompatible storage and only applied when the file later lands on compatible substrate
- local admin / Local System / root, and over SMB stronger service-account rights, still being part of the real contract
- pre-seeded RW peers still needing one explicit Reference Agent to avoid merged or scrambled permission authority
- file permissions still being part of the quick `needs sync` comparison unless the plane is explicitly removed from that equation

That candor is good.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed into several official docs before the product fully owns these questions:

- what exact permission mode is active here right now
- whose permission meaning is authoritative if peers already disagree
- whether this seat is really applying that plane, only carrying it onward, or intentionally rewriting it through local inheritance
- whether the runtime has enough privilege to justify the claim being made
- whether permission drift participates in synchronization decisions or only final apply behavior

AnonSync should therefore make **permission-plane posture** and **permission-apply evidence** first-class product objects.
Every serious permission-bearing subject should render mode, authority basis, apply substrate, privilege floor, comparison participation, and receipt language before the product treats `sync permissions` or `preserve ACLs` as self-explanatory.

## Legacy revision notes preserved below

# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0250`
- Timestamp: `2026.03.21.21.34` (America/New_York)
- Codename: `courierstubpolicysplit`

## What changed in this revision

This revision continues directly from `rev0249` and does seven concrete things:

1. Re-checks another current official Resilio Sync cluster around **xattr / alternate-stream whitelisting, hidden `StreamsList` policy locality, `IgnoreList` non-applicability, fallback stubs in `.sync/Streams`, and the active v3 line**.
2. Sharpens the non-clone line again: borrow Resilio's candor that metadata carriage can be real, selective, and platform-constrained, while refusing any contract where object meaning rides on a hidden share-local whitelist and unsupported seats silently become courier seats with hidden residue.
3. Adds one new **Resilio evaluation** document focused on how current Resilio still spreads one ordinary operator answer about `is this seat preserving object meaning natively, merely relaying it, or silently narrowing it?` across xattr docs, `.sync` internals, IgnoreList docs, and troubleshooting caveats.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: attribute-plane posture, attribute-policy change review, attribute-courier evidence, and attribute-plane receipt.
5. Extends the interface/workbench doctrine so every serious metadata-carriage decision now publishes **policy basis, visible-vs-hidden control locality, native-vs-courier fate, object-shape risk, and strongest safe sentence** before commit.
6. Refreshes status-bearing doctrine documents — status, evaluation, scorecard, clone-veto tests, product direction, interface, roadmap, open questions, sources, and README — so the new tranche is integrated rather than bolted on.
7. Packages the result as another continuation archive whose new tranche makes the `hidden whitelist / courier stub / ignore-boundary` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's hidden attribute-plane contract**

This time the evidence is especially clear around **hidden `StreamsList` whitelists, xattrs bypassing `IgnoreList`, fallback stubs in `.sync/Streams`, and bundle-shape consequences when metadata carriage narrows**.

Current official docs still openly distinguish real facts such as:

- xattrs still syncing only according to a whitelist stored in hidden `.sync/StreamsList`
- the whitelist still being an editable regular text file inside the share
- xattrs still not being governable through `IgnoreList`
- unsupported filesystems still causing Sync to store stream/xattr information in hidden `.sync/Streams` stubs so it can later propagate onward
- disabling xattr syncing still being able to expose bundle-like macOS objects as ordinary subdirectories
- the active v3 line still appearing through `3.1.2.1076`

That candor is good.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed into several help pages before the product fully owns these questions:

- is this seat a native preserver of object meaning or only a courier carrying hidden sidecars onward
- which metadata channels are in scope because of visible product policy versus because of a hidden share-local text file
- why normal exclusion policy does not govern this attribute plane
- whether changing the policy merely narrows hidden fidelity or actually changes visible object shape
- what sentence the product is still allowed to say afterward: `native fidelity`, `courier-only`, `shape risk`, or `reduced meaning plane`

AnonSync should therefore make **attribute-plane posture** and **attribute-courier evidence** first-class product objects.
Every serious metadata-carriage decision should render policy basis, visible-vs-hidden control locality, native-vs-courier fate, object-shape risk, and receipt language before the product treats xattr carriage as hidden implementation detail.

## Legacy revision notes preserved below

# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0242`
- Timestamp: `2026.03.21.19.46` (America/New_York)
- Codename: `archivetogglereplayceiling`

## What changed in this revision

This revision continues directly from `rev0241` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **Archive enable/disable policy, rename/copy replay dependence, per-surface archive controls, retention/access limits, and the active v3 line**.
2. Sharpens the non-clone line again: borrow Resilio's candor that Archive is not just for old versions but also part of rename/copy byte-reuse, while refusing any contract where a simple `Use Archive` toggle quietly changes recovery ceiling and replay cost at the same time.
3. Adds one new **Resilio evaluation** document focused on how current Resilio still spreads one ordinary operator answer about `what exactly do I lose if I turn Archive off here?` across folder preferences, mobile share details, Archive restore docs, and rename replay docs.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: retention/replay dependence, archive-policy change review, local recovery ceiling, and archive-policy receipt.
5. Extends the interface/workbench doctrine so any retention-bearing toggle now publishes **retained-byte effect, remote rename/copy replay effect, seat-local access limits, and strongest safe sentence** before commit.
6. Refreshes status-bearing doctrine documents — status, evaluation, scorecard, clone-veto tests, product direction, interface, roadmap, and sources — so the new tranche is integrated rather than bolted on.
7. Packages the result as another continuation archive whose new tranche makes the `archive toggle` seam explicit in the reading order and the page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's retention/replay contract**

This time the evidence is especially clear around **Archive enable/disable policy, rename/copy replay dependence, mobile access limits, and local recovery ceilings**.

Current official docs still openly distinguish real facts such as:

- `Folder Preferences` still saying Archive stores remotely changed or deleted prior versions by default, and that disabling it also causes remote renames or copies to be re-downloaded instead of being replayed locally
- `What happens when file is renamed` still saying remote rename efficiency depends on Archive because the old name is moved to Archive and restored under the new name when the hash matches
- `Using Archive for file versioning and restoring deleted files` still saying retention defaults differ by desktop and mobile, Android archive support is limited on SD-card shares, and Archive is not accessible on iOS
- current Android and iOS share-detail docs still exposing `Use Archive` as a per-share control, with iOS explicitly saying renamed files are processed through Archive and Android limiting Archive for shares on internal phone memory
- the active v3 line still appears through `3.1.2.1076`

That candor is good.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed into several help articles before the product fully owns these questions:

- does turning Archive off only reduce retained-history time, or also remove cheap rename/copy replay help
- which seats can still hold recovery bytes after this change, and for how long
- whether this seat can even access Archive locally on the current platform/path class
- what stronger sentence is still allowed afterward: `history shortened`, `local rollback reduced`, `rename replay weakened`, or `remote copies will now re-download`

AnonSync should therefore make **retention/replay dependence** and **local recovery ceiling** first-class product objects.
Every serious archive-bearing toggle should render retained-byte effect, remote replay effect, surface/path limits, and receipt language before the product treats `Use Archive` as a harmless preference.

## Legacy revision notes preserved below

This revision continues directly from `rev0240` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **pre-populated same-path divergence, `latest timestamp` replacement, offline-return overwrite priority, peer clock/time-zone validity, Archive restore timing, and the active v3 line**.
2. Sharpens the non-clone line again: borrow Resilio's candor that chronology, offline return, and loser preservation are real operational truths, but refuse any contract where timestamp order silently becomes winner authority.
3. Adds one new **Resilio evaluation** document focused on how current Resilio still spreads one ordinary operator answer about `why is this version winning, and what happens to the loser?` across pre-populated-folder FAQ prose, conflict FAQ prose, time-difference warnings, and Archive restore instructions.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: same-path winner review, decision chronology evidence, losing-version fate, and divergence-resolution receipt.
5. Extends the interface/workbench doctrine so every serious same-path divergence now publishes **winner basis, chronology confidence, timestamp-source strength, loser-preservation shape, and durable claim ceiling** before the product treats `latest timestamp`, `newer`, or `restored` as sufficient explanation.
6. Refreshes status-bearing doctrine documents — status, evaluation, scorecard, clone-veto tests, product direction, interface, roadmap, and sources — so the new tranche is integrated rather than bolted on.
7. Packages the result as another continuation archive whose new tranche makes the `timestamp winner` seam explicit in the reading order and the page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's winner contracts**

This time the evidence is especially clear around **same-path divergence, timestamp-only winner rules, clock confidence, and loser-preservation proof**.

Current official docs still openly distinguish real chronology facts such as:

- `Can I connect two pre-populated pre-existing folders?` still saying that when same files have different hashes, the one with the latest timestamp is synced and replaces the file on the remote peer
- `What if several people make changes to the same file?` still saying online edits normally replay in chronological order, but an offline peer that comes back online can still take priority over later online edits, with overwritten versions placed in Archive
- `Time difference` still saying Sync decides which file is newer by comparing modification times converted to GMT, and that more than 600 seconds of drift or bad time-zone configuration triggers warnings while mobile devices may show empty lists
- `Using Archive for file versioning and restoring deleted files` still saying restored files depend on Sync already running, otherwise a later rescan can compare modified times and move the restored file back into Archive as older
- the active v3 line still appears through `3.1.2.1076`

That candor is good.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed into several help articles before the product fully owns these questions:

- why one same-path candidate is winning right now
- whether the winner basis is strong authority, guarded timestamp order, or offline-return rule
- whether clock and time-zone posture make chronology trustworthy enough for overwrite
- where the losing version actually survives, for how long, and how recoverable it remains
- what exact sentence the product is still allowed to say afterward: `winner applied`, `guarded timestamp winner applied`, `loser preserved`, or only `manual settlement still advised`

AnonSync should therefore make **same-path winner review** and **losing-version fate** first-class product objects.
Every serious same-path divergence should render winner basis, chronology confidence, timestamp-source strength, loser-preservation shape, and receipt language before the product treats `latest timestamp wins`, `newer`, or `restored` as sufficient explanation.

## Legacy revision notes preserved below

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's page contracts**

This time the evidence is especially clear around **rule-agreement truth, ignore-ledger shared meaning, and exclusion claim ceilings**.

Current official docs still openly distinguish real ignore-policy facts such as:

- IgnoreList living in hidden `.sync`, with excluded files not indexed and not counted in the Size column
- matching IgnoreLists across peers being described as `advisable, but not compulsory` on the IgnoreList page
- the troubleshooting page separately saying the Ignore list `must be the same on all peers` so they all agree on what shall be skipped
- IgnoreList being case sensitive and path delimiters differing by operating system
- ignore filters not retroactively affecting files already synced
- structural information still being passed until disconnect even when an item is ignored

That candor is good.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed into several help articles before the product fully owns these questions:

- whether this rule difference is harmless local preference or unsafe peer disagreement
- whether `ignored here` means `ignored everywhere` or only `not indexed on this seat`
- whether the rule only affects future intake or requires a deeper reclassify / disconnect decision
- what sentence the product is still allowed to say about omitted material, share size, and cross-peer agreement

AnonSync should therefore make **rule agreement and exclusion claim ceiling** first-class product objects.
Every serious ignore/exclude surface should render rule provenance, ledger equivalence, retroactivity class, structural residue, strongest safe sentence, and stronger forbidden sentence before the product treats local exclusion as shared system truth.

## Legacy revision notes preserved below

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's page contracts**

This time the evidence is especially clear around **presence witness grade, hidden-listed peer truth, and subject source witness truth**.

Current official docs still openly distinguish real presence-adjacent facts such as:

- `X of Y peers` where `X` is online now and `Y` includes peers that have merely been connected before
- linked-device green/grey dots and sync modes that describe connection and posture, not byte-source sufficiency
- `Hide this device` clearing an offline device from view without unlinking it, and the hidden device reappearing if it comes back online
- `Stopped. Forbidden network` where a visible share is present but not allowed to connect or detect changes on the current network
- Android Auto-sleep or Battery Saver taking the core offline so peers do not see the device online
- ghost-file situations where a subject is still announced in the tree even though no peer currently has the full bytes
- switched-off devices not syncing because a source device must be online for syncing to work

That candor is good.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed into several help articles before the product fully owns these questions:

- is this peer only historically listed, or actually online now
- is it online but ineligible because of pause, forbidden network, or sleep state
- does any currently present peer still have the full bytes for this subject
- is this a ghost announcement, a placeholder-only swarm, or merely delayed transfer
- what exact sentence the product is still allowed to say about presence right now

AnonSync should therefore make **presence witness grade** a first-class product object.
Every serious peer list, absent-file review, source-availability warning, and mobile participation surface should render listedness, route-presence, eligibility, source witness, and strongest safe language before commit or escalation.


## Latest addendum — mutation durability, boot-authority replay, and storage-world truth after rev0309

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's page contracts**

This time the evidence is especially clear around **live state, persisted state, config-owned boot authority, and storage-home world shifts**.

Current official docs still openly distinguish real operational facts such as:

- `Power user preferences` still saying **`config_save_interval` defaults to 600 seconds** and controls how often settings are saved to storage.
- `Sync prevents HDD from sleeping on NAS...` still recommending that operators widen **`config_save_interval`** — even to **18000 seconds** — together with other intervals to preserve drive sleep.
- `Running Sync in configuration mode` still saying config-defined shared folders **disable WebUI** and **override** folders previously added from WebUI.
- `Configuring WebUI` still splitting listener settings between **config-file authority** and ordinary interactive settings depending on mode.
- `Guide to Linux, and Sync peculiarities` still saying the **storage** directory is where Sync keeps **settings, identity, and applied license**.
- `Sync Service Troubleshooting on Windows` still saying a service-user switch can create a **different storage folder world** where old folders are absent until re-added/re-shared.

That candor is good.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed into several help articles before the product fully owns these questions:

- whether a change is merely true in the current runtime or durably persisted
- what next boot will really replay
- whether a stronger config plane outranks the interactive value on screen
- whether a service/principal/storage-home switch creates a different state world rather than continuing the same one
- what exact sentence the product is still allowed to say about crash/restart survival

AnonSync should therefore make **mutation durability and boot-authority replay** first-class product objects.
Every serious policy, listener, trust, exposure, and destructive flow should render live verdict, persisted verdict, boot-authoritative verdict, storage-home provenance, strongest safe sentence, and stronger forbidden sentence before the product treats `changed in settings` as if it already meant `durably true`.


## Latest addendum — mutation durability, boot-authority replay, and storage-world truth after rev0309

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's page contracts**

This time the evidence is especially clear around **live state, persisted state, config-owned boot authority, and storage-home world shifts**.

Current official docs still openly distinguish real operational facts such as:

- `Power user preferences` still saying **`config_save_interval` defaults to 600 seconds** and controls how often settings are saved to storage.
- `Sync prevents HDD from sleeping on NAS...` still recommending that operators widen **`config_save_interval`** — even to **18000 seconds** — together with other intervals to preserve drive sleep.
- `Running Sync in configuration mode` still saying config-defined shared folders **disable WebUI** and **override** folders previously added from WebUI.
- `Configuring WebUI` still splitting listener settings between **config-file authority** and ordinary interactive settings depending on mode.
- `Guide to Linux, and Sync peculiarities` still saying the **storage** directory is where Sync keeps **settings, identity, and applied license**.
- `Sync Service Troubleshooting on Windows` still saying a service-user switch can create a **different storage folder world** where old folders are absent until re-added/re-shared.

That candor is good.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed into several help articles before the product fully owns these questions:

- whether a change is merely true in the current runtime or durably persisted
- what next boot will really replay
- whether a stronger config plane outranks the interactive value on screen
- whether a service/principal/storage-home switch creates a different state world rather than continuing the same one
- what exact sentence the product is still allowed to say about crash/restart survival

AnonSync should therefore make **mutation durability and boot-authority replay** first-class product objects.
Every serious policy, listener, trust, exposure, and destructive flow should render live verdict, persisted verdict, boot-authoritative verdict, storage-home provenance, strongest safe sentence, and stronger forbidden sentence before the product treats `changed in settings` as if it already meant `durably true`.


## Latest addendum — mutation durability, boot-authority replay, and storage-world truth after rev0309

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's page contracts**

This time the evidence is especially clear around **live state, persisted state, config-owned boot authority, and storage-home world shifts**.

Current official docs still openly distinguish real operational facts such as:

- `Power user preferences` still saying **`config_save_interval` defaults to 600 seconds** and controls how often settings are saved to storage.
- `Sync prevents HDD from sleeping on NAS...` still recommending that operators widen **`config_save_interval`** — even to **18000 seconds** — together with other intervals to preserve drive sleep.
- `Running Sync in configuration mode` still saying config-defined shared folders **disable WebUI** and **override** folders previously added from WebUI.
- `Configuring WebUI` still splitting listener settings between **config-file authority** and ordinary interactive settings depending on mode.
- `Guide to Linux, and Sync peculiarities` still saying the **storage** directory is where Sync keeps **settings, identity, and applied license**.
- `Sync Service Troubleshooting on Windows` still saying a service-user switch can create a **different storage folder world** where old folders are absent until re-added/re-shared.

That candor is good.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed into several help articles before the product fully owns these questions:

- whether a change is merely true in the current runtime or durably persisted
- what next boot will really replay
- whether a stronger config plane outranks the interactive value on screen
- whether a service/principal/storage-home switch creates a different state world rather than continuing the same one
- what exact sentence the product is still allowed to say about crash/restart survival

AnonSync should therefore make **mutation durability and boot-authority replay** first-class product objects.
Every serious policy, listener, trust, exposure, and destructive flow should render live verdict, persisted verdict, boot-authoritative verdict, storage-home provenance, strongest safe sentence, and stronger forbidden sentence before the product treats `changed in settings` as if it already meant `durably true`.



## Latest addendum — special-object fidelity, symbolic-link boundary, and bundle-collapse truth after rev0315

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's page contracts**

This time the evidence is especially clear around **special filesystem objects, reference preservation, xattr-dependent bundle fidelity, and compatibility residue**.

Current official docs still openly distinguish real operational facts such as:

- `Soft links, hard links and symbolic links` still saying Windows does **not** support junctions, hard links, or symbolic links in Sync and that using them may produce `.Conflict` entries.
- that same article still saying Unix can synchronize the symbolic-link object itself, but the referenced target folder is **not** synchronized unless it is added separately.
- `Power user preferences` still exposing **`ignore_symlinks`** and **`sync_extended_attributes`** as current operator-tunable settings.
- `Alt Streams and Xattrs in Sync` still saying xattrs sync only by whitelist through hidden `.sync/StreamsList` and that peers unable to store them natively may create stub data in `.sync/Streams`.
- `My files don't sync` still saying disabling xattr syncing can make file bundles such as Pages, Keynote, and macOS apps sync as plain subdirectories instead.

That candor is good.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed into several help articles before the product fully owns these questions:

- whether an object is being preserved as a **reference** or merely as ordinary bytes
- whether the referenced **target** is included, excluded, or needs its own separate subject
- whether bundle semantics depend on metadata lanes the current cohort cannot fully apply
- whether compatibility residue such as `.sync/Streams` is expected and what it means
- what exact sentence the product is still allowed to say about object fidelity across the cohort

AnonSync should therefore make **special-object fidelity** first-class product structure.
Every serious intake, publish, restore, or portability flow should render object kind, reference-vs-target boundary, metadata dependency, compatibility residue, strongest safe sentence, and stronger forbidden sentence before the product treats `synced object` as if it already meant `ordinary preserved subject with stable semantics everywhere`.
