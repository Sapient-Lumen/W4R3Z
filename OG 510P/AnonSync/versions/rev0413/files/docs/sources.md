## rev0412 source set — temporary burst borrow, reserve exception, and payback truth

The most load-bearing source set for this pass was:

- Resilio's current `File download priority` article, which still says higher-priority files suspend lower-priority downloads, that the active prioritized queue is limited, that queue rebuilds may affect performance, and that a manually altered share stops following later global-default priority changes even if later set back to `None`.
- The same article, which still says `folder_defaults.transfer_priority` can apply globally to existing unchanged shares and new shares.
- Resilio's current `How to pause syncing` article, which still says pause is useful when transfer speed is low and you want to prioritize other folders by putting less-needed folders on hold.
- Resilio's current `Sync Preferences` article, which still exposes Global Pause/Resume plus global sending and receiving limits and scheduler controls.
- Resilio's current `Running Sync on schedule` article, which still says paused windows stop ordinary transfer but still allow zero-sized-file sync, deletion propagation, rescanning, indexing, and some onward uploads.
- Resilio's current `How soon does synchronization start?` article, which still says scheduled rescans run every 600 seconds by default and can trigger whole-file rehashing when changes are detected.
- Resilio's current `Some internal tasks are taking time to complete` article, which still says hidden work like block checking, dedup copy, hashing, merging, scanning, reading, transferring, and writing can continue for a long time and may self-recover.
- Resilio's current `Performance overview` article, which still exposes only short-window transfer, RTT, disk-load, and queue-depth evidence.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for useful urgent reprioritization and pressure-shaping ingredients
- but current Resilio still answers `is this extra room lawful temporary borrow, when does that authority expire, and what is owed after it ends?` too diffusely
- AnonSync should therefore prefer explicit burst-borrow contract sheets, authorization reviews, proof pages, timelines, and durable receipts over implied urgency and operator memory

Primary sources:

- File download priority
- How to pause syncing
- Sync Preferences
- Running Sync on schedule
- How soon does synchronization start?
- Some internal tasks are taking time to complete
- Performance overview

## rev0411 source set — allocation-envelope conformance, reserve leakage, and overdraw truth

The most load-bearing source set for this pass was:

- Resilio's current `File download priority` article, which still says higher-priority files suspend lower-priority downloads, the active prioritized queue is limited, queue rebuilds may affect performance, and queue order in the UI may still appear alphabetical.
- Resilio's current `Folder Preferences` article, which still says file download priority can be set in share preferences.
- Resilio's current `Power user preferences` article, which still says `folder_defaults.transfer_priority` exists as a global default for shares that did not break inheritance.
- Resilio's current `Sync Preferences` article, which still exposes global sending and receiving rate limits plus scheduler controls.
- Resilio's current `How to pause syncing` article, which still says pause can be used to prioritize other folders while deletions and rescanning/indexing still continue.
- Resilio's current `How soon does synchronization start?` article, which still says scheduled rescans run every 600 seconds by default and can trigger whole-file rehashing when changes are detected.
- Resilio's current `Some internal tasks are taking time to complete` article, which still says hidden work like block checking, dedup copy, hashing, merging, scanning, reading, transferring, and writing can continue for a long time and may self-recover.
- Resilio's current `Performance overview` article, which still exposes only short-window transfer, RTT, disk-load, and queue-depth evidence.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for useful shaping, limit, and hidden-work ingredients
- but current Resilio still answers `is the active winner still using only the room honestly awarded, or has it leaked into reserve and other claimants' space?` too diffusely
- AnonSync should therefore prefer explicit allocation-envelope contract sheets, conformance reviews, conformance proofs, conformance timelines, and durable conformance receipts over implied fairness and operator memory

Primary sources:

- File download priority
- Folder Preferences
- Power user preferences
- Sync Preferences
- How to pause syncing
- How soon does synchronization start?
- Some internal tasks are taking time to complete
- Performance overview


## rev0410 source set — reservation allocation activation, idle occupancy, and reclaim truth

The most load-bearing source set for this pass was:

- Resilio's current `File download priority` article, which still says higher-priority files suspend lower-priority downloads, that the active prioritized queue is limited, that queue rebuilds may affect performance, and that the queue may still appear alphabetical in the UI.
- Resilio's current `Some internal tasks are taking time to complete` article, which still says background work like block checking, dedup copy, hashing, merging, scanning, reading, transferring, and writing can continue for a long time and may self-recover.
- Resilio's current `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time` article, which still says peers may announce files that later have no downloadable source.
- Resilio's current `Locked files` article, which still says another application can block access and make transfer impossible.
- Resilio's current `Performance overview` article, which still exposes only short-window transfer, RTT, disk-load, and queue-depth evidence.
- Resilio's current `How to pause syncing` article, which still says pause can be used to prioritize other folders by putting less-needed folders on hold.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for useful activation, blocker, and queue-shaping ingredients
- but current Resilio still answers `did the winning claimant actually activate and use the room, or is that room now being idly held while losers keep waiting?` too diffusely
- AnonSync should therefore prefer explicit reservation activation contract sheets, activation reviews, occupancy proofs, occupancy timelines, and durable occupancy receipts over implied activation and operator memory

Primary sources:

- File download priority
- Some internal tasks are taking time to complete
- Cannot download files / These files cannot be downloaded as there are no source peers online for too long time
- Locked files
- Performance overview
- How to pause syncing


## rev0409 source set — reservation contention, preemption, and fairness truth

The most load-bearing source set for this pass was:

- Resilio's current `File download priority` article, which still says priority can be set per share or through a global power-user default, that higher-priority files suspend lower-priority downloads, that queue rebuilds may affect performance, and that the UI queue may still appear alphabetical rather than in actual priority order.
- The same article, which still says a share manually assigned its own priority is no longer affected by later changes to the global default, even if set back to `None` later.
- Resilio's current `How to pause syncing` article, which still says pause can be used to set priority for other folders by putting less-needed folders on hold.
- Resilio's current `Sync Preferences` article, which still exposes global send/receive limits, scheduler controls, and a Global Pause/Resume button that excludes shares already paused individually.
- Resilio's current `Running Sync on schedule` article, which still says paused windows stop ordinary transfer but still allow zero-sized-file sync, deletion propagation, rescanning, indexing, and some onward uploads.
- Resilio's current `Power user preferences` article, which still exposes `folder_defaults.transfer_priority` as a global default whose effect depends on whether a share kept or broke inheritance.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for useful ordering and priority ingredients
- but current Resilio still answers `who wins this contested future room, who loses, what reserve may not be touched, and what fairness guard protects the losers?` too diffusely
- AnonSync should therefore prefer explicit reservation-contention contract sheets, arbitration reviews, verdict proofs, contention timelines, and durable contention receipts over implied winner order and operator memory

Primary sources:

- File download priority
- How to pause syncing
- Sync Preferences
- Running Sync on schedule
- Power user preferences


## rev0408 source set — promise reservation, soft holds, and expiry truth

The most load-bearing source set for this pass was:

- Resilio's current `Sync Preferences` article, which still exposes global sending/receiving limits, a weekly scheduler, and a Global Pause/Resume button that only affects shares not paused individually.
- Resilio's current `Running Sync on schedule` article, which still says paused windows stop ordinary upload/download but still allow zero-sized-file sync, deletion propagation, rescanning, indexing, and even uploads from paused peers to non-paused peers.
- Resilio's current `How to pause syncing` article, which still says ordinary pause leaves deletions and rescanning/indexing alive and that Global Pause excludes shares already paused individually.
- Resilio's current `Performance overview` article, which still exposes only 1-minute, 10-minute, and 1-hour graphs plus per-peer speed, RTT, disk load, and queue depth.
- Resilio's current `How soon does synchronization start?` article, which still says scheduled rescans run every 600 seconds and on start, and that the interval can be changed or set to zero.
- Resilio's current `Some internal tasks are taking time to complete` article, which still says hidden work like checking blocks, dedup copy, hashing, merging, scanning, reading, transferring, and writing can continue without visibly resolving the future-room question.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for useful capacity, pause, and scheduling ingredients
- but current Resilio still answers `is future room genuinely free, softly held, hard-reserved, or silently stolen by stale holds and hidden load?` too diffusely
- AnonSync should therefore prefer explicit promise reservation contract sheets, reservation shaping reviews, reservation proofs, reservation timelines, and durable reservation receipts over implied room ownership and operator memory

Primary sources:

- Sync Preferences
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Running Sync on schedule
  https://help.resilio.com/hc/en-us/articles/210783266-Running-Sync-on-schedule

- How to pause syncing
  https://help.resilio.com/hc/en-us/articles/206217325-How-to-pause-syncing

- Performance overview
  https://help.resilio.com/hc/en-us/articles/360001331930-Performance-overview

- How soon does synchronization start?
  https://help.resilio.com/hc/en-us/articles/204754319-How-soon-does-synchronization-start

- Some internal tasks are taking time to complete
  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete

## rev0407 source set — re-promise authority, credibility budget, and issuance-throttle truth

The most load-bearing source set for this pass was:

- Resilio's current `User Management` article, which still separates `Owner`, `Read-Write`, and `Read Only`, says only Owners may invite new users, and says all devices linked to one identity act as Owners.
- Resilio's current `Sync functionality in detail` article, which still says a folder can be shared and approved from any linked device, that prior approval can be retained for future sharing, and that the operator can instead require approval for every peer.
- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says a remote user can choose to auto-approve all linked devices for future sharing and still warns not to link v2 and v3 devices because license conflicts can lead to lost access to Sync UI and shares configuration.
- Resilio's current `Comprehensive guide to syncing (Desktop-Desktop)` article, which still says linked devices automate folder sharing across the identity with full RW access.
- Resilio's current `Power user preferences` article, which still says older versions may be missing settings or still have deprecated ones.
- Resilio's current `Collecting debug logs manually` article, which still says direct technical support is available only for Sync Business and not Sync v3.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for useful authority ingredients and operational candor
- but current Resilio still answers `after degraded trust or recent breach history, who may publish what class of new promise, for what scope, under what co-sign rule, and on what probation?` too diffusely
- AnonSync should therefore prefer explicit re-promise authority contract sheets, promise issuance reviews, authority proofs, authority timelines, and durable authority receipts over implied trust and operator memory

Primary sources:

- User Management
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- Sync functionality in detail
  https://help.resilio.com/hc/en-us/articles/204754389-Sync-functionality-in-detail

- Sync Private Identity & Linking My Devices
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Comprehensive guide to syncing (Desktop-Desktop)
  https://help.resilio.com/hc/en-us/articles/204754939-Comprehensive-guide-to-syncing-Desktop-Desktop

- Power user preferences
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Collecting debug logs manually
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

## rev0406 source set — breach recovery, make-good, and trust-repair truth

The most load-bearing source set for this pass was:

- Resilio's current `Performance overview` article, which still exposes only 1-minute, 10-minute, and 1-hour real-time graphs plus per-peer speed, latency, and disk queue information.
- Resilio's current `How soon does synchronization start?` article, which still explains immediate filesystem-notification detection, scheduled rescans every 600 seconds and on start, and the fact that `folder_rescan_interval = 0` disables rescans even on restart.
- Resilio's current `Running Sync on schedule` article, which still says paused schedule windows stop ordinary upload/download but do not stop zero-sized-file sync, deletion propagation, or rescanning/indexing.
- Resilio's current `My files don't sync` article, which still routes operators through peers, status warnings, History, queues, restart, re-add, disk checks, and timestamp correction rather than a first-class post-breach duty object.
- Resilio's current `Locked files` article, which still says another application can block access entirely and therefore keep recovery contingent on an external unblocker.
- Resilio's current `Collecting debug logs manually` article, which still says direct technical support is available only for Sync Business and not Sync v3, and still requires enablement, restart, reproduction, and at least 15 minutes of capture.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for useful post-miss recovery ingredients and operational candor
- but current Resilio still answers `what exact obligation survives after the miss, what narrower or substitute remedy is allowed, and when is trust repaired enough for a new promise?` too diffusely
- AnonSync should therefore prefer explicit recovery commitment contract sheets, recovery-shaping reviews, breach recovery proofs, recovery timelines, and durable recovery receipts over follow-up prose and operator memory

Primary sources:

- Performance overview
  https://help.resilio.com/hc/en-us/articles/360001331930-Performance-overview

- How soon does synchronization start?
  https://help.resilio.com/hc/en-us/articles/204754319-How-soon-does-synchronization-start

- Running Sync on schedule
  https://help.resilio.com/hc/en-us/articles/210783266-Running-Sync-on-schedule

- My files don't sync
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Locked files
  https://help.resilio.com/hc/en-us/articles/205504549-Locked-files

- Collecting debug logs manually
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

## rev0405 source set — delivery commitment, renegotiation, and breach truth

The most load-bearing source set for this pass was:

- Resilio's current `Performance overview` article, which still exposes only 1-minute, 10-minute, and 1-hour real-time graphs plus per-peer speed, latency, and disk queue information.
- Resilio's current `How soon does synchronization start?` article, which still explains immediate filesystem-notification detection, scheduled rescans every 600 seconds and on start, and the fact that `folder_rescan_interval = 0` disables rescans even on restart.
- Resilio's current `Running Sync on schedule` article, which still says paused schedule windows stop ordinary upload/download but do not stop zero-sized-file sync, deletion propagation, or rescanning/indexing.
- Resilio's current `Power user preferences` article, which still documents commitment-shaping settings such as `folder_rescan_interval`, `direct_torrent_enabled`, `prioritize_initial_indexing`, `parallel_indexing`, and `recheck_locked_files_interval`.
- Resilio's current `Some internal tasks are taking time to complete` article, which still names hidden operations like checking blocks, deduplication copy, hashing, merging, scanning, reading, writing, and transfer.
- Resilio's current `When a file changes, does Resilio Sync transfer the entire file again, or just the part that's changed?` article, which still says only changed pieces are normally transferred but shifted changes can trigger whole-file re-sync.
- Resilio's current `Locked files` article, which still says another application can block access and make transfer impossible until the condition clears.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for useful delivery-risk ingredients and operational candor
- but current Resilio still answers `is this only a forecast, a target, a conditional promise, a hard commitment, or a breached commitment, and what invalidators govern that sentence?` too diffusely
- AnonSync should therefore prefer explicit delivery commitment contract sheets, commitment-quality reviews, commitment proofs, commitment timelines, and durable commitment receipts over implied promises and operator memory

Primary sources:

- Performance overview
  https://help.resilio.com/hc/en-us/articles/360001331930-Performance-overview

- How soon does synchronization start?
  https://help.resilio.com/hc/en-us/articles/204754319-How-soon-does-synchronization-start

- Running Sync on schedule
  https://help.resilio.com/hc/en-us/articles/210783266-Running-Sync-on-schedule

- Power user preferences
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Some internal tasks are taking time to complete
  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete

- When a file changes, does Resilio Sync transfer the entire file again, or just the part that's changed?
  https://help.resilio.com/hc/en-us/articles/206217095-When-a-file-changes-does-Resilio-Sync-transfer-the-entire-file-again-or-just-the-part-that-s-changed

- Locked files
  https://help.resilio.com/hc/en-us/articles/205504549-Locked-files

## rev0404 source set — finishability, ETA confidence, and forecast truth

The most load-bearing source set for this pass was:

- Resilio's current `Performance overview` article, which still exposes only 1-minute, 10-minute, and 1-hour real-time graphs plus per-peer speed, latency, and disk queue information.
- Resilio's current `How soon does synchronization start?` article, which still explains immediate filesystem-notification detection, scheduled rescans every 600 seconds and on start, and the fact that `folder_rescan_interval = 0` disables rescans even on restart.
- Resilio's current `Running Sync on schedule` article, which still says paused schedule windows stop ordinary upload/download but do not stop zero-sized-file sync, deletion propagation, or rescanning/indexing.
- Resilio's current `Power user preferences` article, which still documents forecast-shaping settings such as `direct_torrent_enabled`, `prioritize_initial_indexing`, `parallel_indexing`, `recheck_locked_files_interval`, and `folder_rescan_interval`.
- Resilio's current `Some internal tasks are taking time to complete` article, which still names hidden operations like checking blocks, deduplication copy, hashing, merging, scanning, reading, writing, and transfer.
- Resilio's current `When a file changes, does Resilio Sync transfer the entire file again, or just the part that's changed?` article, which still says only changed pieces are normally transferred but shifted changes can trigger whole-file re-sync.
- Resilio's current `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time` and `Locked files` articles, which still show blocker classes that can destroy narrow ETA confidence even when work exists.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for useful forecast ingredients and operational candor
- but current Resilio still answers `what honestly remains, is this route finishable, what ETA window survives, and when is no forecast the truthful answer?` too diffusely
- AnonSync should therefore prefer explicit completion forecast contract sheets, forecast-quality reviews, finish-forecast proofs, forecast timelines, and durable forecast receipts over speed extrapolation and operator memory

Primary sources:

- Performance overview
  https://help.resilio.com/hc/en-us/articles/360001331930-Performance-overview

- How soon does synchronization start?
  https://help.resilio.com/hc/en-us/articles/204754319-How-soon-does-synchronization-start

- Running Sync on schedule
  https://help.resilio.com/hc/en-us/articles/210783266-Running-Sync-on-schedule

- Power user preferences
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Some internal tasks are taking time to complete
  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete

- When a file changes, does Resilio Sync transfer the entire file again, or just the part that's changed?
  https://help.resilio.com/hc/en-us/articles/206217095-When-a-file-changes-does-Resilio-Sync-transfer-the-entire-file-again-or-just-the-part-that-s-changed

- Cannot download files / These files cannot be downloaded as there are no source peers online for too long time
  https://help.resilio.com/hc/en-us/articles/360010899719-Cannot-download-files-These-files-cannot-be-downloaded-as-there-are-no-source-peers-online-for-too-long-time

- Locked files
  https://help.resilio.com/hc/en-us/articles/205504549-Locked-files

## rev0403 source set — motion, churn, and net progress truth

The most load-bearing source set for this pass was:

- Resilio's current `Performance overview` article, which still exposes ongoing-activity graphs, short observation windows, per-peer speeds, latency, disk load, and queue depth.
- Resilio's current `Some internal tasks are taking time to complete` article, which still names hidden operations like checking file blocks, copying local blocks for deduplication, hashing, merging folder trees, scanning, reading, and transferring.
- Resilio's current `How soon does synchronization start?` article, which still explains filesystem notifications, default scheduled rescans every 600 seconds and on start, and full-file rehashing when changed files are detected.
- Resilio's current `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time` article, which still explains the ghost-file condition where peers heard about files they later cannot actually fetch.
- Resilio's current `Conflict files in Sync` article, which still shows that movement can create conflict artifacts and cleanup debt instead of a settled result.
- Resilio's current `Locked files` article, which still says another application can block access to files and make transfer impossible.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for useful motion, queue, graph, and troubleshooting witnesses
- but current Resilio still answers `is this live busy work actually shrinking the obligation, or only creating churn and new cleanup debt?` too diffusely
- AnonSync should therefore prefer explicit progress contract sheets, progress-quality reviews, net-progress proofs, progress timelines, and durable progress receipts over activity inference and operator memory

Primary sources:

- Performance overview
  https://help.resilio.com/hc/en-us/articles/360001331930-Performance-overview

- Some internal tasks are taking time to complete
  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete

- How soon does synchronization start?
  https://help.resilio.com/hc/en-us/articles/204754319-How-soon-does-synchronization-start

- Cannot download files / These files cannot be downloaded as there are no source peers online for too long time
  https://help.resilio.com/hc/en-us/articles/360010899719-Cannot-download-files-These-files-cannot-be-downloaded-as-there-are-no-source-peers-online-for-too-long-time

- Conflict files in Sync
  https://help.resilio.com/hc/en-us/articles/204753629-Conflict-files-in-Sync

- Locked files
  https://help.resilio.com/hc/en-us/articles/205504549-Locked-files

## rev0402 source set — work heartbeat, stall, and rescue truth

The most load-bearing source set for this pass was:

- Resilio's current `Sync Main View (Desktop)` article, which still exposes a 30-day History lane, search, peer counts, a notification bell, and status icons including a green check that only means synced with connected peers.
- Resilio's current `My files don't sync` article, which still tells operators to inspect peer connectivity, status warnings, History, and upload/download queues when work appears stuck.
- Resilio's current `Performance overview` article, which still exposes ongoing-activity graphs, short observation windows, per-peer transfer speeds, latency, and disk queue depth.
- Resilio's current `Some internal tasks are taking time to complete` article, which still explains that hidden background work can create temporary apparent inactivity and that Sync may recover on its own.
- Resilio's current `Agent run out of system notify watchers...` article, which still explains that watcher exhaustion can push update discovery onto manual or periodic rescans instead of real-time observation.
- Resilio's current `Resilio Sync change log`, which still records motion-adjacent signals like synchronized notifications, the `Last transferred` column, improved peer-list accuracy, and improved receiving-statistic accuracy.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for useful motion and troubleshooting signals
- but current Resilio still answers `after accepted work goes quiet, is that healthy wait, blocker-bound progress, silent stall, or rescue territory?` too diffusely
- AnonSync should therefore prefer explicit work-heartbeat contract sheets, heartbeat reviews, heartbeat proofs, heartbeat timelines, and durable liveness receipts over status inference and operator memory

Primary sources:

- Sync Main View (Desktop)
  https://help.resilio.com/hc/en-us/articles/204755009-Sync-Main-View-Desktop

- My files don't sync
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Performance overview
  https://help.resilio.com/hc/en-us/articles/360001331930-Performance-overview

- Some internal tasks are taking time to complete
  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete

- Agent run out of system notify watchers. Updated files will be uploaded only after periodic folder rescan
  https://help.resilio.com/hc/en-us/articles/360015593120-Agent-run-out-of-system-notify-watchers-Updated-files-will-be-uploaded-only-after-periodic-folder-rescan

- Resilio Sync change log
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log

## rev0401 source set — dispatch claim, custody, and abandonment truth

The most load-bearing source set for this pass was:

- Resilio's current `Sync Main View (Desktop)` article, which still exposes a bell for approval requests or other notifications plus share and peer surfaces.
- Resilio's current `Comprehensive guide to syncing (Desktop-Desktop)` article, which still says remote adds generate approval requests, synchronization starts after approval unless disabled, and requester details include name, IP address, fingerprint, and approval request receipt date.
- Resilio's current `User Management` article, which still separates Read Only, Read & Write, and Owner permissions, allows on-the-fly permission changes for Advanced folders, and says linked devices under one identity all act as Owners.
- Resilio's current `Sync functionality in detail` article, which still says permissions can change before/during/after sharing, approvals can be handled from any linked device, and previous approvals may remove the need for fresh approval next time unless every-peer approval is required.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for useful identity, approval, and authority candor
- but current Resilio still answers `after dispatch picks the work, who actually has custody of it now, what commitment was accepted, and when does it visibly return to risk if custody fails?` too diffusely
- AnonSync should therefore prefer explicit work claims, claim-acceptance reviews, custody proofs, claim timelines, and durable custody receipts over notification inference and operator memory

Primary sources:

- Sync Main View (Desktop)
  https://help.resilio.com/hc/en-us/articles/204755009-Sync-Main-View-Desktop

- Comprehensive guide to syncing (Desktop-Desktop)
  https://help.resilio.com/hc/en-us/articles/204754939-Comprehensive-guide-to-syncing-Desktop-Desktop

- User Management
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- Sync functionality in detail
  https://help.resilio.com/hc/en-us/articles/204754389-Sync-functionality-in-detail

## rev0400 source set — decision portfolios, prioritization, dispatch, and starvation truth

The most load-bearing source set for this pass was:

- Resilio's current `Sync Main View (Desktop)` article, which still exposes filters for connected/disconnected shares, search, configurable columns, a 30-day History lane, peer/activity status, and notification bell state, giving operators many useful signals but not one portfolio queue.
- Resilio's current `How do I perform a search in Sync?` article, which still shows search across folders/files, connected devices, and users as another attention aid.
- Resilio's current `Core warnings` article, which still clusters multiple warning families that can all compete for operator attention.
- Resilio's current `Errors and warnings` and `Errors & Troubleshooting` category pages, which still present issue families as article groups rather than one dispatch workspace.
- Resilio's current `Some internal tasks are taking time to complete` article, which still makes `watch and wait` a real posture because background work may recover by itself.
- Resilio's current `Performance overview` article, which still exposes short-window troubleshooting graphs that can influence urgency without themselves being a dispatch rule.
- Resilio's current `Collecting debug logs manually`, `Collecting crash reports, mini-dumps and core dumps`, and `Measuring network performance with iperf3` articles, which still define heavier investigative rungs that compete for limited operator attention.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for exposing many useful attention signals
- but current Resilio still answers `when several candidate decisions all matter, which one actually goes now, which one is deliberately held, and what watch item is quietly starving?` too diffusely
- AnonSync should therefore prefer explicit decision portfolios, prioritization reviews, dispatch proofs, portfolio timelines, and durable portfolio receipts over inbox motion and operator memory

Primary sources:

- Sync Main View (Desktop)
  https://help.resilio.com/hc/en-us/articles/204755009-Sync-Main-View-Desktop

- How do I perform a search in Sync?
  https://help.resilio.com/hc/en-us/articles/205457725-How-do-I-perform-a-search-in-Sync

- Core warnings
  https://help.resilio.com/hc/en-us/articles/360001217950-Core-warnings

- Errors and warnings
  https://help.resilio.com/hc/en-us/sections/201112455-Errors-and-warnings

- Errors & Troubleshooting
  https://help.resilio.com/hc/en-us/categories/200410985-Errors-Troubleshooting

- Some internal tasks are taking time to complete
  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete

- Performance overview
  https://help.resilio.com/hc/en-us/articles/360001331930-Performance-overview

- Collecting debug logs manually
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

- Collecting crash reports, mini-dumps and core dumps
  https://help.resilio.com/hc/en-us/articles/206214615-Collecting-crash-reports-mini-dumps-and-core-dumps

- Measuring network performance with iperf3
  https://help.resilio.com/hc/en-us/articles/1500007478562-Measuring-network-performance-with-iperf3

## rev0399 source set — evidence-to-decision thresholds, action charter, and escalation truth

The most load-bearing source set for this pass was:

- Resilio's current `My files don't sync` article, which still routes operators through peers, warnings, History, and queues before branching into different next steps.
- Resilio's current `Some internal tasks are taking time to complete` article, which still makes clear that some degraded states can persist while background work proceeds and may call for waiting or monitoring rather than immediate heavy repair.
- Resilio's current `Peers aren't connecting` article, which still fans one symptom into several materially different troubleshooting routes.
- Resilio's current `Performance overview` article, which still exposes short-window real-time graphs that inform decisions without themselves being one decision object.
- Resilio's current `Errors & Troubleshooting` category page, which still clusters warnings, troubleshooting guides, and support-artifact collection pages as neighboring article families rather than one threshold-and-action workspace.
- Resilio's current `Collecting debug logs automatically` and `Collecting debug logs manually` articles, which still describe heavier evidence-capture escalation without turning that burden into one explicit action threshold.
- Resilio's current `Collecting crash reports, mini-dumps and core dumps` article, which still defines another deeper escalation rung.
- Resilio's current `Measuring network performance with iperf3` article, which still defines a separate network-test rung and requires Sync to be fully shut down during the test.
- Resilio's current support articles, which still say direct technical support is available only for Sync Business and not Sync v3 users.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for exposing useful witness planes and repair ladders
- but current Resilio still answers `what is actually justified next, what stronger action is still blocked, and what uncertainty budget remains too large to spend?` too diffusely
- AnonSync should therefore prefer explicit decision charters, action-threshold reviews, decision proofs, decision timelines, and durable decision receipts over scattered KB reading and analyst intuition

Primary sources:

- My files don't sync
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Some internal tasks are taking time to complete
  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete

- Peers aren't connecting
  https://help.resilio.com/hc/en-us/articles/205450205-Peers-aren-t-connecting

- Performance overview
  https://help.resilio.com/hc/en-us/articles/360001331930-Performance-overview

- Errors & Troubleshooting
  https://help.resilio.com/hc/en-us/categories/200410985-Errors-Troubleshooting

- Collecting debug logs automatically
  https://help.resilio.com/hc/en-us/articles/360019430539-Collecting-debug-logs-automatically

- Collecting debug logs manually
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

- Collecting crash reports, mini-dumps and core dumps
  https://help.resilio.com/hc/en-us/articles/206214615-Collecting-crash-reports-mini-dumps-and-core-dumps

- Measuring network performance with iperf3
  https://help.resilio.com/hc/en-us/articles/1500007478562-Measuring-network-performance-with-iperf3

## rev0398 source set — evidence synthesis, corroboration, contradiction, and integrated-claim truth

The most load-bearing source set for this pass was:

- Resilio's current `Send info to Support team` section page, which still groups mobile logs, iperf3, automatic and manual debug logs, crash reports, and NAS dump flows as separate support articles rather than one synthesis workspace.
- Resilio's current `Collecting debug logs automatically` article, which still requests peer role, timestamps, problem description, and affected shares/files, making one support packet richer but still separate.
- Resilio's current `Collecting debug logs manually` article, which still varies artifact retrieval by desktop, service principal, config-defined `storage_path`, NAS, and Android lane.
- Resilio's current `Collecting crash reports, mini-dumps and core dumps` article, which still introduces another heavier artifact class with its own storage-path logic.
- Resilio's current `Measuring network performance with iperf3` article, which still adds a distinct performance-test artifact that only answers one slice of a case.
- Resilio's current `Performance overview` article, which still exposes 1-minute, 10-minute, and 1-hour real-time troubleshooting graphs on a separate UI surface.
- Resilio's current `Sync Main View (Desktop)` article, which still exposes search, notifications, peer counts, current activity, and a 30-day History lane as another witness surface.
- Resilio's current `Errors & Troubleshooting` category page, which still presents symptom and support materials as separate article families rather than one integrated evidence-adjudication object.
- Resilio's current support articles, which still say direct technical support is available only for Sync Business and not Sync v3 users.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for exposing many useful witness planes
- but current Resilio still answers `which packets are actually independent, which merely duplicate each other, which conflict, and what strongest integrated claim survives all of them together?` too diffusely
- AnonSync should therefore prefer explicit evidence-synthesis sheets, corroboration/conflict reviews, integrated-claim proofs, synthesis timelines, and durable lineage receipts over scattered support instructions and operator memory

Primary sources:

- Send info to Support team
  https://help.resilio.com/hc/en-us/sections/201494276-Send-info-to-Support-team

- Collecting debug logs automatically
  https://help.resilio.com/hc/en-us/articles/360019430539-Collecting-debug-logs-automatically

- Collecting debug logs manually
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

- Collecting crash reports, mini-dumps and core dumps
  https://help.resilio.com/hc/en-us/articles/206214615-Collecting-crash-reports-mini-dumps-and-core-dumps

- Measuring network performance with iperf3
  https://help.resilio.com/hc/en-us/articles/1500007478562-Measuring-network-performance-with-iperf3

- Performance overview
  https://help.resilio.com/hc/en-us/articles/360001331930-Performance-overview

- Sync Main View (Desktop)
  https://help.resilio.com/hc/en-us/articles/204755009-Sync-Main-View-Desktop

- Errors & Troubleshooting
  https://help.resilio.com/hc/en-us/categories/200410985-Errors-Troubleshooting

## rev0397 source set — evidence intake, sufficiency, and supplement-loop truth

The most load-bearing source set for this pass was:

- Resilio's current `Collecting debug logs automatically` article, which still says support text should include ticket reference, peer role, timestamps, problem description, and names of affected shares/files, and still makes `Include logs` an explicit step.
- Resilio's current `Collecting debug logs manually` article, which still requires enablement, restart, reproduction, and at least 15 minutes of post-repro collection, while also capping ordinary attachments at 20 MB and routing larger logs to a different upload path.
- Resilio's current `Increasing Debug Log size` article, which still says logs rotate at `log_size`, that even the retained window can be insufficient, and that larger capture windows may be necessary.
- Resilio's current `Power user preferences` article, which still says today's defaults include `log_size` 100 MB and `log_ttl` 7 days, and still warns that older versions may miss or deprecate settings.
- Resilio's current `Collect debug logs on mobiles` article, which still uses a hidden `.synclogs` folder after a special debug action, making mobile packet form distinct.
- Resilio's current `Where to collect logs on NAS?` article, which still says each NAS has its own local storage for logs and that config may reveal the true storage path.
- Resilio's current `How to collect logs on NAS manually?` article, which still copies the whole internal-data folder first and only later tells the operator to clean it down to the requested files.
- Resilio's current `Collecting crash reports, mini-dumps and core dumps` article, which still introduces heavier artifact classes and platform/service-principal-specific dump locations.
- Resilio's current `Measuring network performance with iperf3` article, which still adds a different support artifact class and requires Sync to be shut down during the test.
- Resilio's current `Send info to Support team` section page, which still groups these articles as a cluster rather than one intake-sufficiency workspace.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for exposing many useful packet-context ingredients
- but current Resilio still answers `is this packet actually sufficient for the named question, what exact gap remains, and what cheapest supplement is really justified?` too diffusely
- AnonSync should therefore prefer explicit intake sheets, sufficiency reviews, supplement proofs, intake timelines, and durable lineage receipts over thread folklore and vague `send more logs` loops

Primary sources:

- Collecting debug logs automatically
  https://help.resilio.com/hc/en-us/articles/360019430539-Collecting-debug-logs-automatically

- Collecting debug logs manually
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

- Increasing Debug Log size
  https://help.resilio.com/hc/en-us/articles/205450145-Increasing-Debug-Log-size

- Power user preferences
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Collect debug logs on mobiles
  https://help.resilio.com/hc/en-us/articles/38269346960531-Collect-debug-logs-on-mobiles

- Where to collect logs on NAS?
  https://help.resilio.com/hc/en-us/articles/205326945-Where-to-collect-logs-on-NAS

- How to collect logs on NAS manually?
  https://help.resilio.com/hc/en-us/articles/208800446-How-to-collect-logs-on-NAS-manually

- Collecting crash reports, mini-dumps and core dumps
  https://help.resilio.com/hc/en-us/articles/206214615-Collecting-crash-reports-mini-dumps-and-core-dumps

- Measuring network performance with iperf3
  https://help.resilio.com/hc/en-us/articles/1500007478562-Measuring-network-performance-with-iperf3

- Send info to Support team
  https://help.resilio.com/hc/en-us/sections/201494276-Send-info-to-Support-team

## rev0396 source set — evidence packet, custody, redaction, and export truth

The most load-bearing source set for this pass was:

- Resilio's current `Collecting debug logs automatically` article, which still routes logs through `Contact support`, requires `Include logs`, says not to close the app or device until sending completes, and asks for peer role, timestamps, and affected shares/files.
- Resilio's current `Collecting debug logs manually` article, which still requires debug enablement, restart, reproduction, and platform-specific log retrieval, including service-principal-specific storage paths and config-defined `storage_path` on Linux.
- Resilio's current `Collect debug logs on mobiles` article, which still uses a distinct hidden `.synclogs` collection path after a special debug action.
- Resilio's current `Where to collect logs on NAS?` article, which still says each NAS has its own local storage for `.sync` state and that config may define the true storage path if the obvious location is wrong.
- Resilio's current `Collecting crash reports, mini-dumps and core dumps` article, which still introduces heavier artifact classes and path variants by operating system and service principal.
- Resilio's current `Collecting core dump on NAS devices` article, which still instructs operators to move dumps into a public folder for download, making export transformation and custody visible.
- Resilio's current `Errors & Troubleshooting` category page, which still groups support-facing evidence instructions as article clusters rather than one packet workspace.
- Resilio's current debug-log and dump articles, which still say direct technical support is available only for Sync Business customers and not for Sync v3 users.
- Resilio's current `Resilio Sync change log`, which still records transport-oriented packet facts such as HTTPS sending for Contact Support dialog and prior inability-to-send-feedback fixes.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for exposing many useful evidence channels
- but current Resilio still answers `what exact evidence packet are we sharing, what got transformed or redacted, which source world produced it, what integrity survives export, and what audience may rely on it?` too diffusely
- AnonSync should therefore prefer explicit evidence-packet sheets, packet-shaping reviews, export proofs, packet timelines, and durable lineage receipts over scattered support instructions and thread memory

Primary sources:

- Collecting debug logs automatically
  https://help.resilio.com/hc/en-us/articles/360019430539-Collecting-debug-logs-automatically

- Collecting debug logs manually
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

- Collect debug logs on mobiles
  https://help.resilio.com/hc/en-us/articles/38269346960531-Collect-debug-logs-on-mobiles

- Where to collect logs on NAS?
  https://help.resilio.com/hc/en-us/articles/205326945-Where-to-collect-logs-on-NAS

- Collecting crash reports, mini-dumps and core dumps
  https://help.resilio.com/hc/en-us/articles/206214615-Collecting-crash-reports-mini-dumps-and-core-dumps

- Collecting core dump on NAS devices
  https://help.resilio.com/hc/en-us/articles/360015557220-Collecting-core-dump-on-NAS-devices

- Errors & Troubleshooting
  https://help.resilio.com/hc/en-us/categories/200410985-Errors-Troubleshooting

- Resilio Sync change log
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log

## rev0395 source set — discriminator acquisition, evidence burden, and question-order truth

The most load-bearing source set for this pass was:

- Resilio's current `Sync Main View (Desktop)` article, which still exposes search, peer counts, statuses, notifications, and a 30-day History lane as cheap observational surfaces.
- Resilio's current `My files don't sync` article, which still tells operators to inspect peers, warnings, History, queues, and escalate to logs if the simpler checks do not resolve the ambiguity.
- Resilio's current `Comprehensive guide to syncing (Desktop-Desktop)` article, which still says absent approval requests can indicate connectivity trouble and still exposes requester name, IP, fingerprint, and request date as verification facts.
- Resilio's current `"Time difference" error` article, which still says UTC time and timezone comparison across peers can distinguish one failure family.
- Resilio's current `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time` article, which still describes a missing-source / ghost-file condition as another discriminator.
- Resilio's current `Some internal tasks are taking time to complete` article, which still says heavy internal work can explain the state and therefore makes observation windows part of evidence planning.
- Resilio's current `Collecting debug logs automatically` article, which still requires enablement, restart, reproduction, a 15-minute post-repro window, and contextual details like peer role, timestamps, and affected shares/files.
- Resilio's current `Collecting debug logs manually` article, which still requires enablement, restart, reproduction, and platform-specific storage-path access.
- Resilio's current `Collecting crash reports, mini-dumps and core dumps` and `Collecting core dump on NAS devices` articles, which still show that some evidence capture is materially more intrusive than ordinary observation.
- Resilio's current `Errors & Troubleshooting` category page, which still organizes issue families as article clusters rather than one burden-aware evidence-priority workspace.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for exposing many useful evidence ingredients
- but current Resilio still answers `which fact should we obtain next, how heavy is that evidence move, what fallback exists, and what stronger sentence stays blocked if we do not capture it?` too diffusely
- AnonSync should therefore prefer explicit discriminator-acquisition sheets, burden reviews, fact-capture proofs, acquisition timelines, and durable lineage receipts over article hopping and support-style evidence macros

Primary sources:

- Sync Main View (Desktop)
  https://help.resilio.com/hc/en-us/articles/204755009-Sync-Main-View-Desktop

- My files don't sync
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Comprehensive guide to syncing (Desktop-Desktop)
  https://help.resilio.com/hc/en-us/articles/204754939-Comprehensive-guide-to-syncing-Desktop-Desktop

- "Time difference" error
  https://help.resilio.com/hc/en-us/articles/204753599--Time-difference-error

- Cannot download files / These files cannot be downloaded as there are no source peers online for too long time
  https://help.resilio.com/hc/en-us/articles/360010899719-Cannot-download-files-These-files-cannot-be-downloaded-as-there-are-no-source-peers-online-for-too-long-time

- Some internal tasks are taking time to complete
  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete

- Collecting debug logs automatically
  https://help.resilio.com/hc/en-us/articles/360019430539-Collecting-debug-logs-automatically

- Collecting debug logs manually
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

- Collecting crash reports, mini-dumps and core dumps
  https://help.resilio.com/hc/en-us/articles/206214615-Collecting-crash-reports-mini-dumps-and-core-dumps

- Collecting core dump on NAS devices
  https://help.resilio.com/hc/en-us/articles/360015557220-Collecting-core-dump-on-NAS-devices

- Errors & Troubleshooting
  https://help.resilio.com/hc/en-us/categories/200410985-Errors-Troubleshooting

## rev0394 source set — doctrine applicability, fact-pattern routing, and distinguishing-question truth

The most load-bearing source set for this pass was:

- Resilio's current `How do I perform a search in Sync?` article, which still says Sync can search folders, shared files, connected devices, and users in UI.
- Resilio's current `Sync Main View (Desktop)` article, which still exposes search, peer counts, statuses, notifications, and a 30-day History lane.
- Resilio's current `My files don't sync` article, which still tells operators to inspect peers, Status warnings, History, and peer queues before selecting a next step.
- Resilio's current `Errors & Troubleshooting` category and `Errors and warnings` section pages, which still organize symptom families mainly as article lists.
- Resilio's current `Peers aren't connecting` article, which still routes one sync-stall symptom family through router, multicast, NIC, firewall, relay, and predefined-host checks.
- Resilio's current `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time` article, which still explains a selective-sync / source-availability ghost-file style condition.
- Resilio's current `"Time difference" error` article, which still explains timestamp and timezone skew as another distinct lookalike route.
- Resilio's current `Database error` article, which still routes toward restart, reconnect, and all-peer re-add.
- Resilio's current `Some internal tasks are taking time to complete` article, which still says the condition may self-recover and may simply reflect heavy processing.
- Resilio's current `Core warnings` article, which still clusters many warning families under one surface.
- Resilio's current `Collecting debug logs manually` article, which still says direct technical support is unavailable for Sync v3 and points users toward forum/Help Center.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for exposing many useful routing breadcrumbs
- but current Resilio still answers `which doctrine actually applies to this fresh fact pattern, which lookalikes remain plausible, and what one more fact would distinguish them best?` too diffusely
- AnonSync should therefore prefer explicit doctrine-applicability sheets, routing reviews, applicability proofs, route-reversal timelines, and durable lineage receipts over article-by-article comparison and support escalation folklore

Primary sources:

- How do I perform a search in Sync?
  https://help.resilio.com/hc/en-us/articles/205457725-How-do-I-perform-a-search-in-Sync

- Sync Main View (Desktop)
  https://help.resilio.com/hc/en-us/articles/204755009-Sync-Main-View-Desktop

- My files don't sync
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Errors & Troubleshooting
  https://help.resilio.com/hc/en-us/categories/200410985-Errors-Troubleshooting

- Errors and warnings
  https://help.resilio.com/hc/en-us/sections/201112455-Errors-and-warnings

- Peers aren't connecting
  https://help.resilio.com/hc/en-us/articles/205450205-Peers-aren-t-connecting

- Cannot download files / These files cannot be downloaded as there are no source peers online for too long time
  https://help.resilio.com/hc/en-us/articles/360010899719-Cannot-download-files-These-files-cannot-be-downloaded-as-there-are-no-source-peers-online-for-too-long-time

- "Time difference" error
  https://help.resilio.com/hc/en-us/articles/204753599--Time-difference-error

- Database error
  https://help.resilio.com/hc/en-us/articles/204753659-Database-error

- Some internal tasks are taking time to complete
  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete

- Core warnings
  https://help.resilio.com/hc/en-us/articles/360001217950-Core-warnings

- Collecting debug logs manually
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

## rev0393 source set — appeal, precedent, and doctrine consistency truth

The most load-bearing source set for this pass was:

- Resilio's current `My files don't sync` article, which still says Status warnings usually link to KB explanations and operators may need to inspect warnings, History, peer state, and queues before choosing a fix.
- Resilio's current `Errors & Troubleshooting` and `Core warnings` section pages, which still organize issue interpretation as clusters of separate warning articles.
- Resilio's current `"Time difference" error` article, which still says bad time or timezone can distort file ordering and even produce empty file lists on mobile.
- Resilio's current `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time` article, which still says a peer may announce files that later no source peer actually holds, creating a ghost-file style condition.
- Resilio's current `Database error` article, which still escalates through restart, reconnect, and all-peer re-add, showing a narrow symptom-specific repair ladder.
- Resilio's current `Service files missing / Cannot identify destination folder` article, which still says the error can come from corrupted internal state or two instances touching the same folder and then routes toward remove-and-add-back repair.
- Resilio's current `Agent run out of system notify watchers` article, which still ties one warning to watcher exhaustion and rescanning semantics.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows warning and status meaning changing by version, including a fixed non-clickable `Can't download file` status and later improved license-warning text.
- Resilio's current `Collecting debug logs manually` and `Collecting crash reports, mini-dumps and core dumps` articles, which still say direct technical support is unavailable for Sync v3 and route users toward the community forum and Help Center.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for exposing many useful doctrine fragments
- but current Resilio still answers `which prior ruling should bind this case, when is it distinguishable, and when was the old guidance overruled or sunset?` too diffusely
- AnonSync should therefore prefer explicit precedent dockets, appeal reviews, precedent proofs, doctrine timelines, and durable lineage receipts over warning-by-warning folklore and changelog archaeology

Primary sources:

- My files don't sync
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Errors & Troubleshooting
  https://help.resilio.com/hc/en-us/categories/200410985-Errors-Troubleshooting

- Core warnings
  https://help.resilio.com/hc/en-us/articles/360001217950-Core-warnings

- "Time difference" error
  https://help.resilio.com/hc/en-us/articles/204753599--Time-difference-error

- Cannot download files / These files cannot be downloaded as there are no source peers online for too long time
  https://help.resilio.com/hc/en-us/articles/360010899719-Cannot-download-files-These-files-cannot-be-downloaded-as-there-are-no-source-peers-online-for-too-long-time

- Database error
  https://help.resilio.com/hc/en-us/articles/204753659-Database-error

- Service files missing / Cannot identify destination folder
  https://help.resilio.com/hc/en-us/articles/205450225-Service-files-missing-Cannot-identify-destination-folder

- Agent run out of system notify watchers. Updated files will be uploaded only after periodic folder rescan
  https://help.resilio.com/hc/en-us/articles/360015593120-Agent-run-out-of-system-notify-watchers-Updated-files-will-be-uploaded-only-after-periodic-folder-rescan

- Resilio Sync 3.0 change log
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Collecting debug logs manually
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

- Collecting crash reports, mini-dumps and core dumps
  https://help.resilio.com/hc/en-us/articles/206214615-Collecting-crash-reports-mini-dumps-and-core-dumps

## rev0392 source set — completion dispute, counterevidence, and rework verdict truth

The most load-bearing source set for this pass was:

- Resilio's current `Sync Main View (Desktop)` article, which still says green check means files are synced with all connected peers, History shows the last 30 days of general syncing activity, and peer counts distinguish online peers from total peers.
- Resilio's current `Comprehensive guide to syncing (Desktop-Desktop)` article, which still says a remote device can remain in `Pending approval`, and if the source side receives no approval request the condition indicates a network-connectivity problem between the devices.
- Resilio's current `User Management` article, which still says permissions can be changed without disrupting synchronization and that disconnect revokes future updates while already synchronized files remain in place.
- Resilio's current `"Time difference" error` article, which still says Sync compares modification times after converting them to GMT and that bad time or timezone can produce warnings and empty file lists on mobile.
- Resilio's current `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time` article, which still says one peer may announce updates while later no source peer actually holds the bytes to provide.
- Resilio's current `Conflict files in Sync` article, which still says multiple versions may try to land into the same file or folder and produce conflict artifacts.
- Resilio's current `Disconnecting and Removing Folders` article, which still says disconnect removes placeholders if Selective Sync was enabled and reconnect may later propose a different path or create a new directory.
- Resilio's current `My files don't sync` article, which still says operators may need to inspect peers, warnings, History, selective-sync state, or even re-add the folder.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for exposing several real witness families that matter when a completion claim is challenged
- but current Resilio still answers `which witness wins, what burden remains unmet, and whether the right result is uphold, narrow, overturn, rework, or reopen?` too diffusely
- AnonSync should therefore prefer explicit completion disputes, counterevidence reviews, verdict proofs, timelines, and durable lineage receipts over improvised `looks green / probably done / maybe retry` folklore

Primary sources:

- Sync Main View (Desktop)
  https://help.resilio.com/hc/en-us/articles/204755009-Sync-Main-View-Desktop

- Comprehensive guide to syncing (Desktop-Desktop)
  https://help.resilio.com/hc/en-us/articles/204754939-Comprehensive-guide-to-syncing-Desktop-Desktop

- User Management
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- "Time difference" error
  https://help.resilio.com/hc/en-us/articles/204753599--Time-difference-error

- Cannot download files / These files cannot be downloaded as there are no source peers online for too long time
  https://help.resilio.com/hc/en-us/articles/360010899719-Cannot-download-files-These-files-cannot-be-downloaded-as-there-are-no-source-peers-online-for-too-long-time

- Conflict files in Sync
  https://help.resilio.com/hc/en-us/articles/204753629-Conflict-files-in-Sync

- Disconnecting and Removing Folders
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- My files don't sync
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

## rev0391 source set — mandate fulfillment, returned evidence, and completion acceptance truth

The most load-bearing source set for this pass was:

- Resilio's current `Comprehensive guide to syncing (Desktop-Desktop)` article, which still says a remote device adding a folder triggers an approval request, sync starts only after approval or disabled approval rules, `Pending approval` without a received request indicates a network issue, and the approver can inspect requester name, IP address, certificate fingerprint, and approval-request receipt date.
- Resilio's current `Sync functionality in detail` article, which still says approval-time permissions can be altered, approvals can be handled from any linked device, and selective-sync surfaces show per-file synchronization progress.
- Resilio's current `Sync Main View (Desktop)` article, which still says the bell lights up for approval requests or other notifications, History shows the last 30 days of general syncing activity, green check means synced with all connected peers, and peer counts distinguish online peers from total peers.
- Resilio's current `User Management` article, which still says permissions can be changed without disrupting synchronization and disconnect revokes future updates while already-synchronized files remain.
- Resilio's current `Resilio Sync change log`, which still records synchronized notifications across devices, a `Last transferred` column, a searchable/sortable History tab, and fixes around accuracy of files sent or received in the peer list.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for exposing several real completion-adjacent witnesses
- but current Resilio still answers `what exact mandate is being claimed as fulfilled, what evidence came back, what part remains incomplete, and who accepted or disputed the return?` too diffusely
- AnonSync should therefore prefer explicit fulfillment attestations, return reviews, completion proofs, timelines, and durable lineage receipts over improvised `done / looks green / probably complete` folklore

Primary sources:

- Comprehensive guide to syncing (Desktop-Desktop)
  https://help.resilio.com/hc/en-us/articles/204754939-Comprehensive-guide-to-syncing-Desktop-Desktop

- Sync functionality in detail
  https://help.resilio.com/hc/en-us/articles/204754389-Sync-functionality-in-detail

- Sync Main View (Desktop)
  https://help.resilio.com/hc/en-us/articles/204755009-Sync-Main-View-Desktop

- User Management
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- Resilio Sync change log
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log

## rev0390 source set — reliance-to-action authority, delegated mandate, and cancellation truth

The most load-bearing source set for this pass was:

- Resilio's current `Sync functionality in detail` article, which still says folder permissions determine what exactly a user can do, lists Read Only / Read & Write / Owner, says permissions can change before, during, or after sharing, and says access can be revoked or altered during approval.
- The same functionality article, which still says linked devices under one private identity all act as Owners and that approval requests can be handled from any linked device.
- Resilio's current `User Management` article, which still says only Owners can invite new users, different peers can receive different permissions, and disconnect revokes future updates while already-synchronized files remain.
- Resilio's current `Sync Share Dialog (Desktop)` article, which still says Advanced folders can be shared only by Owners, Standard folders omit Owner level, and the dialog still carries approval requirement, link expiry, and use-count limit.
- Resilio's current `Comprehensive guide to syncing (Desktop-Desktop)` article, which still says manual sharing requires choosing an access mechanism, permission set, and folder location, may require approval, and allows inspecting requester name, IP address, fingerprint, and approval request receipt date before approving.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for exposing several real authority ingredients
- but current Resilio still answers `who may merely know, who may approve, who may execute, who may re-delegate, and what later cancellation does to work already in motion?` too diffusely
- AnonSync should therefore prefer explicit action mandates, routing reviews, authority proofs, timelines, and durable lineage receipts over improvised permission folklore

Primary sources:

- Sync functionality in detail
  https://help.resilio.com/hc/en-us/articles/204754389-Sync-functionality-in-detail

- User Management
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- Sync Share Dialog (Desktop)
  https://help.resilio.com/hc/en-us/articles/204790709-Sync-Share-Dialog-Desktop

- Comprehensive guide to syncing (Desktop-Desktop)
  https://help.resilio.com/hc/en-us/articles/204754939-Comprehensive-guide-to-syncing-Desktop-Desktop

## rev0389 source set — certification publication, audience reliance, and recall truth

The most load-bearing source set for this pass was:

- Resilio's current `Sync Main View (Desktop)` article, which still says the desktop UI exposes search, filters, customizable columns, a 30-day History lane, and settings/license details.
- Resilio's current `Collecting debug logs automatically` article, which still says debug logging may need to be enabled, Sync restarted, the issue reproduced, and logs collected for at least 15 minutes afterward.
- Resilio's current `Collecting debug logs manually` article, which still says direct technical support is available only for Sync Business customers while Sync v3 users should use the forum / Help Center for functionality questions and a separate web form for payments/licensing.
- The same manual log article, which still says log paths differ across desktop, service principals, Linux current-directory / storage_path worlds, NAS, and Android.
- Resilio's current `Collecting crash reports, mini-dumps and core dumps` article and `Where to collect logs on NAS?` article, which still keep platform-specific artifact capture and support-lane reality visible.
- Resilio's current `Settings on mobile platforms` article, which still separates Support routing from About/build witness on mobile.
- Resilio's current `Running Sync in configuration mode` article, which still says config mode is useful for applying the same settings across many machines and that non-default `storage_path` creates new settings there.
- Resilio's current `Sync Private Identity & Linking My Devices` article, which still warns that linking v2 and v3 devices may create license conflicts and lost UI / share configuration access.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for exposing several real evidence and support-routing ingredients
- but current Resilio still answers `what exact sentence is safe for this audience to rely on, and how do we supersede or recall it later?` too diffusely
- AnonSync should therefore prefer explicit reliance charters, publication reviews, reliance proofs, reliance timelines, and durable lineage receipts over improvised screenshot / log / note packets

Primary sources:

- Sync Main View (Desktop)
  https://help.resilio.com/hc/en-us/articles/204755009-Sync-Main-View-Desktop

- Collecting debug logs automatically
  https://help.resilio.com/hc/en-us/articles/360019430539-Collecting-debug-logs-automatically

- Collecting debug logs manually
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

- Collecting crash reports, mini-dumps and core dumps
  https://help.resilio.com/hc/en-us/articles/206214615-Collecting-crash-reports-mini-dumps-and-core-dumps

- Where to collect logs on NAS?
  https://help.resilio.com/hc/en-us/articles/205326945-Where-to-collect-logs-on-NAS

- Settings on mobile platforms
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- Running Sync in configuration mode
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Sync Private Identity & Linking My Devices
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

## rev0388 source set — estate certification, explicit exclusions, and revocation truth

The most load-bearing source set for this pass was:

- Resilio's current `Sync Main View (Desktop)` article, which still says the main UI offers filters for connected/disconnected shares, search, customizable columns, a 30-day History lane, and statuses where a green check means synced with connected peers; the same article still says peer counts distinguish online from total peers and that peers offline for 7 days get disconnected from the folder.
- Resilio's current `How do I perform a search in Sync?` article, which still says search spans folders, shared files, connected devices, and users in the UI.
- Resilio's current `Folder Types and Management` article, which still says disconnected folders remain visible for future action even though they have no local path and consume no local space.
- The same `Folder Types and Management` article, which still says columns can be shown/hidden and sorted, reinforcing that the product offers inspection aids rather than a durable certificate.
- Resilio's current `Running Sync in configuration mode` article, which still says config mode is helpful for applying the same settings to a number of different machines and that a non-default `storage_path` creates new settings there.
- Resilio's current `Sync Service Troubleshooting on Windows` article, which still says switching the service to `Local System` creates a new storage folder in another directory, after which the old folders are absent until they are re-added / re-shared or reconnected.
- Resilio's current `Settings on mobile platforms` article, which still documents a separate mobile settings lane covering identity, power, and network controls.
- Resilio's current `User Management` article, which still says peer disconnect suspends future updates while already-synchronized files remain in place.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for exposing many raw evidence surfaces an operator would consult before certifying an estate
- but current Resilio still answers `what exact scope is certified, what is excluded, how fresh is the proof, and what revokes the stronger sentence?` too diffusely
- AnonSync should therefore prefer explicit estate certification sheets, shaping reviews, certification proofs, timelines, and durable receipts over informal synthesis across many pages and surfaces

Primary sources:

- Sync Main View (Desktop)
  https://help.resilio.com/hc/en-us/articles/204755009-Sync-Main-View-Desktop

- How do I perform a search in Sync?
  https://help.resilio.com/hc/en-us/articles/205457725-How-do-I-perform-a-search-in-Sync

- Folder Types and Management
  https://help.resilio.com/hc/en-us/articles/204762459-Folder-Types-and-Management

- Running Sync in configuration mode
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Sync Service Troubleshooting on Windows
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

- Settings on mobile platforms
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- User Management
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

## rev0387 source set — return-delta convergence, cohort settlement, and straggler truth

The most load-bearing source set for this pass was:

- Resilio's current `Folders are duplicating with an index (i) in their name.` article, which still says duplicate-path cleanup routes through per-folder disconnect/reconnect and that devices in Selective Sync or Synced mode auto-place arriving folders into the default storage folder unless the device is switched to Disconnected mode.
- Resilio's current `How to manually set the location of the folders synced across linked devices?` article, which still says manual placement requires Disconnected mode plus repeated `Connect`, and that Android still requires disabling Simple mode.
- Resilio's current `Disconnecting and Removing Folders` article, which still says reconnect may propose a different default path and may create a new directory with `(1)` appended.
- Resilio's current `Can I connect two pre-populated pre-existing folders?` article, which still says existing-directory reconciliation is a folder-specific connect workflow and still calls out the need to confirm when the target is not empty.
- Resilio's current `Folder not empty` article, which still warns that files already present in the receiving folder may be deleted or overwritten.
- Resilio's current `Can I move or rename a syncing folder?` article, which still says renaming is local-only and that moving across partitions can require disconnect/reconnect.
- Resilio's current `User Management` article, which still says peer disconnect suspends future updates while already-synchronized files remain.
- Resilio's current `Running Sync in configuration mode` article, which still says configuration mode is helpful when applying the same settings on a number of different machines.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that convergence often requires repeated structural per-folder work and that defaults help future arrivals more than already drifted live subjects
- but current Resilio still answers `how much of this cohort is really settled, which subjects remain outside the stronger sentence, and when is a bounded win all we honestly have?` too diffusely
- AnonSync should therefore prefer explicit convergence campaign sheets, shaping reviews, settlement proofs, convergence timelines, and durable campaign receipts over overloaded `cleanup complete` or `mostly fixed` language

Primary sources:

- Folders are duplicating with an index (i) in their name.  
  https://help.resilio.com/hc/en-us/articles/204753869-Folders-are-duplicating-with-an-index-i-in-their-name

- How to manually set the location of the folders synced across linked devices?  
  https://help.resilio.com/hc/en-us/articles/206216615-How-to-manually-set-the-location-of-the-folders-synced-across-linked-devices

- Disconnecting and Removing Folders  
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- Can I connect two pre-populated pre-existing folders?  
  https://help.resilio.com/hc/en-us/articles/205506569-Can-I-connect-two-pre-populated-pre-existing-folders

- Folder not empty  
  https://help.resilio.com/hc/en-us/articles/204753689-Folder-not-empty

- Can I move or rename a syncing folder?  
  https://help.resilio.com/hc/en-us/articles/205450655-Can-I-move-or-rename-a-syncing-folder

- User Management  
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

## rev0386 source set — return-delta debt, baseline rebind, and honest successor adoption

The most load-bearing source set for this pass was:

- Resilio's current `Disconnecting and Removing Folders` article, which still says reconnect may propose a different default path, create a new directory, append `(1)` when a same-name folder already exists, and remove placeholders on disconnect when Selective Sync was enabled.
- Resilio's current `Folders are duplicating with an index (i) in their name` article, which still says default-mode behavior can auto-place arriving folders into the default storage folder and that switching to Disconnected mode is how the operator regains explicit placement control.
- Resilio's current `How to manually set the location of the folders synced across linked devices?` article, which still says Android Simple mode must be disabled to choose a custom path at connect time.
- Resilio's current `Folder Types and Management` article, which still says disconnected folders have no local path while Selective Sync and Full Sync preserve different local witness shapes.
- Resilio's current `Synchronization Modes` article, which still distinguishes disconnected, selective, and full-sync postures.
- Resilio's current `Can I connect two pre-populated pre-existing folders?` article, which still says existing-directory connect merges trees, skips same-hash files, and resolves same-name different-hash files by latest timestamp.
- Resilio's current `Folder not empty` article, which still warns that adding or reconnecting into a non-empty directory can overwrite or delete already-present files.
- Resilio's current `Can I move or rename a syncing folder?` article, which still says renaming is local-only and moving across partitions can require disconnect/reconnect.
- Resilio's current `User Management` article, which still says peer disconnect leaves already-synchronized bytes in place while future updates remain suspended.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that a changed active state can be operationally real
- but current Resilio still answers `is this temporary debt, the new baseline, or a reopen-worthy mismatch?` too diffusely
- AnonSync should therefore prefer return-delta contracts, delta-aging reviews, parity-debt proofs, return-delta timelines, and return-delta receipts over scattered KB-driven normalization lore

Primary sources:

- Disconnecting and Removing Folders
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- Folders are duplicating with an index (i) in their name
  https://help.resilio.com/hc/en-us/articles/204753869-Folders-are-duplicating-with-an-index-i-in-their-name

- How to manually set the location of the folders synced across linked devices?
  https://help.resilio.com/hc/en-us/articles/206216615-How-to-manually-set-the-location-of-the-folders-synced-across-linked-devices

- Folder Types and Management
  https://help.resilio.com/hc/en-us/articles/204762459-Folder-Types-and-Management

- Synchronization Modes
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- Can I connect two pre-populated pre-existing folders?
  https://help.resilio.com/hc/en-us/articles/205506569-Can-I-connect-two-pre-populated-pre-existing-folders

- Folder not empty
  https://help.resilio.com/hc/en-us/articles/204753689-Folder-not-empty

- Can I move or rename a syncing folder?
  https://help.resilio.com/hc/en-us/articles/205450655-Can-I-move-or-rename-a-syncing-folder

- User Management
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

## rev0385 source set — control re-arm, return-to-protection, and post-bypass reconciliation

The most load-bearing source set for this pass was:

- Resilio's current `How to pause syncing` article, which still says resuming a paused folder is done by repeating the same steps and using `Resume syncing`, proving that some returns are cheap same-surface resumes.
- Resilio's current `Sync Preferences` article, which still says Global Pause/Resume affects only shares that are not paused individually, exposing that return ownership depends on which pause surface owns the state.
- Resilio's current `Disconnecting and Removing Folders` article, which still distinguishes disconnect from remove and still says reconnect may propose a different path, create a new directory, and append `(1)` when a same-name folder already exists.
- Resilio's current `Synchronization Modes` article, which still says disconnected folders have no local path until connect and still distinguishes disconnected, placeholder-only, and full-sync postures.
- Resilio's current `How to manually set the location of the folders synced across linked devices?` article, which still says Disconnected mode enables path choice at connect time and Android Simple mode must be disabled to choose location manually.
- Resilio's current `Can I connect two pre-populated pre-existing folders?` article, which still says same-hash files are not re-synced, same-name different-hash files resolve by latest timestamp, and other files merge into the tree when connecting to an existing directory.
- Resilio's current `Selective Sync` article, which still warns that removing a Selective Sync share removes all placeholders from the local file system.
- Resilio's current `Settings on mobile platforms` article, which still says Android Simple mode controls whether share location can be selected manually and still says the default folder location can receive a `(1)` suffix when a same-name folder already exists.
- Resilio's current `User Management` article, which still says peer disconnect suspends future updates while already-synchronized files remain.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that return paths differ materially
- but current Resilio still answers `did we actually recreate the same protected state, or only restart motion in a changed one?` too diffusely
- AnonSync should therefore prefer return contracts, re-arm readiness reviews, return proofs, reconciliation timelines, and return receipts over scattered KB-driven re-entry lore

Primary sources:

- How to pause syncing
  https://help.resilio.com/hc/en-us/articles/206217325-How-to-pause-syncing

- Sync Preferences
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Disconnecting and Removing Folders
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- Synchronization Modes
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- How to manually set the location of the folders synced across linked devices?
  https://help.resilio.com/hc/en-us/articles/206216615-How-to-manually-set-the-location-of-the-folders-synced-across-linked-devices

- Can I connect two pre-populated pre-existing folders?
  https://help.resilio.com/hc/en-us/articles/205506569-Can-I-connect-two-pre-populated-pre-existing-folders

- Selective Sync
  https://help.resilio.com/hc/en-us/articles/205458095-Selective-Sync

- Settings on mobile platforms
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- User Management
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

## rev0384 source set — control suspension, break-glass, and stop semantics

The most load-bearing source set for this pass was:

- Resilio's current `How to pause syncing` article, which still says pause allows zero-sized files, deletions, and rescans/indexing to continue, proving that `paused` is not equivalent to `nothing changes`.
- Resilio's current `Sync Preferences` article, which still says Global Pause applies only to shares that are not paused individually, exposing scope interaction between stop surfaces.
- Resilio's current `Running Sync on schedule` article, which still says scheduler `Paused` keeps deletions and rescans alive and can still allow uploads to non-paused peers.
- Resilio's current `Disconnecting and Removing Folders` article, which still distinguishes disconnect from remove and says reconnect may propose a different default path and create a new directory.
- Resilio's current `Synchronization Modes` article, which still distinguishes disconnected folders, placeholder-only local removal, and remove-from-all-devices behavior.
- Resilio's current `Setting network interface per share` article, which still says `Stopped. Forbidden network` blocks peer connection and new/update detection for that share.
- Resilio's current `Settings on mobile platforms` article, which still says disabling notifications can lower Sync priority enough that it may stop working in the background, and still exposes mobile-data gating and battery/auto-sleep controls.
- Resilio's current `User Management` article, which still says peer disconnect revokes future updates while preserving already-synchronized files.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for exposing materially different stop semantics instead of pretending all stop states are the same
- but current Resilio still answers `what exactly is suspended, what survives, and what proof restores trust later?` too diffusely
- AnonSync should therefore prefer suspension contracts, bypass reviews, suspension proofs, stop-semantic timelines, and suspension receipts over scattered KB-driven stop lore

Primary sources:

- How to pause syncing
  https://help.resilio.com/hc/en-us/articles/206217325-How-to-pause-syncing

- Sync Preferences
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Running Sync on schedule
  https://help.resilio.com/hc/en-us/articles/210783266-Running-Sync-on-schedule

- Disconnecting and Removing Folders
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- Synchronization Modes
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- Setting network interface per share
  https://help.resilio.com/hc/en-us/articles/360001411244-Setting-network-interface-per-share

- Settings on mobile platforms
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- User Management
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

## rev0383 source set — guardrail attestation, rehearsal, and silent trust decay

The most load-bearing source set for this pass was:

- Resilio's current `Power user preferences` article, which still says the page covers the latest version and older versions may miss or deprecate settings, still marks at least one setting as ignored in Linux WebUI, and still includes restart-bound options like `profiler_enabled`.
- Resilio's current `Folder Preferences` article, which still says folder-level preferences are available on desktop platforms only.
- Resilio's current `Can I force Sync to do local network (LAN) syncing only and not sync via the Internet?` article, which still requires disabling tracker and relay in both share preferences and power-user settings, restarting Sync, and clearing cached peer state on desktops that had already learned an internet route.
- Resilio's current `Running Sync in configuration mode` article, which still says the same settings can be applied across machines, that Advanced Preferences parameters can be added, that a non-default `storage_path` creates new settings there, that config mode can set up only Standard folders, and that config-authored shared folders disable WebUI and override folders previously added from WebUI.
- Resilio's current `Running Sync as a service on Windows` article, which still distinguishes migrated-settings service install from clean installation requiring re-share and reconnect.
- Resilio's current `Sync Service Troubleshooting on Windows` article, which still says switching the service to `Local System` requires restart, creates a new storage folder with no old added folders present, and then requires re-add / re-share or reconnect.
- Resilio's current `Settings on mobile platforms` article, which still shows mobile-specific controls such as battery saver, auto-start, mobile-data gating, notifications affecting background priority, and Android `Simple mode`.
- Resilio's current `Running Sync on schedule` article, which still exposes a weekly scheduler in Sync Preferences -> Advanced and notes version/licensing bounds.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that control truth is version-bound, world-bound, lane-bound, and sometimes restart-bound
- but current Resilio still answers `do we still trust this control right now, and why?` too diffusely
- AnonSync should therefore prefer attestation sheets, witness reviews, rehearsal proofs, decay timelines, and attestation receipts over scattered settings memory

Primary sources:

- Power user preferences
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Folder Preferences
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- Can I force Sync to do local network (LAN) syncing only and not sync via the Internet?
  https://help.resilio.com/hc/en-us/articles/204754349-Can-I-force-Sync-to-do-local-network-LAN-syncing-only-and-not-sync-via-the-Internet

- Running Sync in configuration mode
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Running Sync as a service on Windows
  https://help.resilio.com/hc/en-us/articles/207701296-Running-Sync-as-a-service-on-Windows

- Sync Service Troubleshooting on Windows
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

- Settings on mobile platforms
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- Running Sync on schedule
  https://help.resilio.com/hc/en-us/articles/210783266-Running-Sync-on-schedule

## rev0382 source set — case-to-guardrail promotion, preventive controls, and recurrence watch

The most load-bearing source set for this pass was:

- Resilio's current `Agent run out of system notify watchers` article, which still says watcher exhaustion on Linux can force change discovery to happen only on manual or periodic rescan, and that durable remediation requires writing the watcher limit to `/etc/sysctl.conf` and restarting Sync.
- Resilio's current `Some internal tasks are taking time to complete` article, which still says the condition may be intermittent and self-recovering, so not every case justifies a strong preventive control.
- Resilio's current `Collecting debug logs automatically` article, which still requires enabling debug logging, restarting Sync, reproducing the issue, then waiting at least 15 minutes, making artifact capture a real repeatable runbook.
- Resilio's current `Running Sync on schedule` article, which still exposes a weekly schedule-based bandwidth control in Sync Preferences -> Advanced.
- Resilio's current `Performance overview` article, which still limits built-in live graphs to 1 minute, 10 minute, and 1 hour windows.
- Resilio's current `Power user preferences` article, which still says the page covers the latest version and that older versions may miss or deprecate settings, making some guardrails inherently version-sensitive.
- Resilio's current `Running Sync in configuration mode` article, which still says Sync can apply pre-configured parameters on multiple machines and that Advanced Preferences parameters can also be added.
- Resilio's current `Can I force Sync to do local network (LAN) syncing only and not sync via the Internet?` article, which still requires disabling tracker and relay in both share preferences and power user settings, plus restart, to get the intended constraint.
- Resilio's current `Running Sync as a service on Windows` article, which still distinguishes migrate-settings service install from clean installation and the resulting reconnect / re-share consequences.
- Resilio's current `My files don't sync` article, which still sends the operator through warnings, history, queues, ignore-list consistency, xattr considerations, permissions, rescan/restart, free-space checks, `.!sync` cleanup, time checks, and log collection.
- Resilio's current `Resilio Sync change log`, which still shows statuses, warnings, advanced power-user settings, default ignore-list changes, force-rescan support, memory/error reporting, and other guardrail ingredients arriving piecemeal over time.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for exposing real prevention ingredients and durability details
- but current Resilio still answers `what permanent control did this case justify, what does it really cover, and how will we know if it failed later?` too diffusely
- AnonSync should therefore prefer preventive-control sheets, promotion reviews, activation proofs, recurrence-watch timelines, and durable guardrail receipts over scattered KB-driven operational memory

Primary sources:

- Agent run out of system notify watchers. Updated files will be uploaded only after periodic folder rescan
  https://help.resilio.com/hc/en-us/articles/360015593120-Agent-run-out-of-system-notify-watchers-Updated-files-will-be-uploaded-only-after-periodic-folder-rescan

- Some internal tasks are taking time to complete
  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete

- Collecting debug logs automatically
  https://help.resilio.com/hc/en-us/articles/360019430539-Collecting-debug-logs-automatically

- Running Sync on schedule
  https://help.resilio.com/hc/en-us/articles/210783266-Running-Sync-on-schedule

- Performance overview
  https://help.resilio.com/hc/en-us/articles/360001331930-Performance-overview

- Power user preferences
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Running Sync in configuration mode
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Can I force Sync to do local network (LAN) syncing only and not sync via the Internet?
  https://help.resilio.com/hc/en-us/articles/204754349-Can-I-force-Sync-to-do-local-network-LAN-syncing-only-and-not-sync-via-the-Internet

- Running Sync as a service on Windows
  https://help.resilio.com/hc/en-us/articles/207701296-Running-Sync-as-a-service-on-Windows

- My files don't sync
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Resilio Sync change log
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log

## rev0381 source set — incident case truth, root-cause adjudication, and honest closure

The most load-bearing source set for this pass was:

- Resilio's current `Sync Main View (Desktop)` article, which still says the main UI includes search/filter and a History lane showing general syncing activity for the last 30 days.
- Resilio's current `My files don't sync` article, which still tells the operator to inspect Status warnings, click through to KB explanations, search Sync History, and inspect queue state before choosing among several possible explanations.
- Resilio's current `Errors and warnings` section, which still exposes a broad catalog of separate warning articles.
- Resilio's current `Core warnings` article, which still mixes tracker failure, low storage, and identity/storage corruption under one warning surface and still cites missing `.SyncUser###`, missing `.sync`, and damaged `identity.dat` as examples.
- Resilio's current `Database error` article, which still lists multiple possible causes such as improper shutdown, damaged disk sector, virus, or other software touching the files.
- Resilio's current `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time` article, which still explains a ghost-file race caused by a selective-sync peer retaining only a placeholder.
- Resilio's current `Agent run out of system notify watchers` article, which still ties delayed detection to Linux watcher exhaustion and rescan-only discovery.
- Resilio's current `Service files missing / Cannot identify destination folder` article, which still ties the symptom either to corrupted `.sync` state or to two Sync instances touching the same folder.
- Resilio's current `SE_SM_NO_IDENTITY` and `Error 205` articles, which still point to mobile identity corruption and unlink/new-identity recovery.
- Resilio's current `Some internal tasks are taking time to complete` article, which still says the condition may be intermittent and self-recovering.
- Resilio's current `Peers aren't connecting` article, which still ends in a two-peer debug-log escalation path.
- Resilio's current `Collecting debug logs automatically` article, which still requires timestamps, peer role, and affected shares/files in the report and also says direct technical support is not available for Sync v3 while technical support is available exclusively for Business customers.
- Resilio's current `I still have questions, where can I get answers?` article, which still points users to the forum and support.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for preserving real cause diversity and multiple evidence lanes
- but current Resilio still answers `what do we now believe caused this, how honest is closure, and what should reopen the case?` too diffusely
- AnonSync should therefore prefer incident case sheets, hypothesis reviews, closure proofs, case timelines, and durable case receipts over scattered troubleshooting folklore

Primary sources:

- Sync Main View (Desktop)  
  https://help.resilio.com/hc/en-us/articles/204755009-Sync-Main-View-Desktop

- My files don't sync  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Errors and warnings  
  https://help.resilio.com/hc/en-us/sections/201112455-Errors-and-warnings

- Core warnings  
  https://help.resilio.com/hc/en-us/articles/360001217950-Core-warnings

- Database error  
  https://help.resilio.com/hc/en-us/articles/204753659-Database-error

- Cannot download files / These files cannot be downloaded as there are no source peers online for too long time  
  https://help.resilio.com/hc/en-us/articles/360010899719-Cannot-download-files-These-files-cannot-be-downloaded-as-there-are-no-source-peers-online-for-too-long-time

- Agent run out of system notify watchers. Updated files will be uploaded only after periodic folder rescan  
  https://help.resilio.com/hc/en-us/articles/360015593120-Agent-run-out-of-system-notify-watchers-Updated-files-will-be-uploaded-only-after-periodic-folder-rescan

- Service files missing / Cannot identify destination folder  
  https://help.resilio.com/hc/en-us/articles/205450225-Service-files-missing-Cannot-identify-destination-folder

- SE_SM_NO_IDENTITY  
  https://help.resilio.com/hc/en-us/articles/207337990-SE-SM-NO-IDENTITY

- Error 205  
  https://help.resilio.com/hc/en-us/articles/207337230-Error-205

- Some internal tasks are taking time to complete  
  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete

- Peers aren't connecting  
  https://help.resilio.com/hc/en-us/articles/205450205-Peers-aren-t-connecting

- Collecting debug logs automatically  
  https://help.resilio.com/hc/en-us/articles/360019430539-Collecting-debug-logs-automatically

- I still have questions, where can I get answers?  
  https://help.resilio.com/hc/en-us/articles/206216795-I-still-have-questions-where-can-I-get-answers

## rev0380 source set — remediation run choreography, checkpoints, and safe-abort truth

The most load-bearing source set for this pass was:

- Resilio's current `My files don't sync` article, which still says the operator should inspect peer connectivity, Status warnings, Sync History, and per-share queues before moving to heavier fixes, and still lists restart, re-add, disk check, deletion of stuck `.!sync` files, and time-drift correction as different branches.
- Resilio's current `Database error` article, which still gives a true execution order: restart first, then disconnect/reconnect one peer to the same destination if local, then re-add on all peers if broader.
- Resilio's current `Peers aren't connecting` article, which still splits the run across router/firewall, relay, multicast, NIC, and proxy troubleshooting lanes.
- Resilio's current `Service files missing / Cannot identify destination folder` article, which still requires archive review before deleting `.sync` and re-adding the share.
- Resilio's current `Disconnecting and Removing Folders` article, which still keeps disconnect, reconnect, and remove separate and warns that reconnect may propose a different default path.
- Resilio's current `Sync Service Troubleshooting on Windows` article, which still shows a permission workaround that also requires restart, creates a new service storage world, and then forces re-add / re-share or reconnect of all folders.
- Resilio's current `Running Sync in configuration mode` article, which still ties config placement, service exceptions, and non-default `storage_path` to start semantics and new-world creation.
- Resilio's current `Collecting debug logs automatically` article, which still requires enabling debug logging, restarting Sync, reproducing the issue, and waiting at least 15 minutes for useful logs.
- Resilio's current `Agent run out of system notify watchers` article, which still turns watcher-limit repair into a system change plus Sync restart.
- Resilio's current `How soon does synchronization start?` article, which still says rescan runs every 600 seconds and on start by default, manual rescan exists, and setting `folder_rescan_interval` to zero disables rescans even on restart.
- Resilio's current `Some internal tasks are taking time to complete` article, which still says the condition can be intermittent and self-recovering, preserving a real observe-first branch.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that remediation has ordered steps, real preflight, real waits, and real destructive boundaries
- but current Resilio still answers `how exactly do we perform the chosen fix safely, and where must we stop?` too diffusely
- AnonSync should therefore prefer remediation-run sheets, readiness reviews, checkpoint proofs, run timelines, and durable execution receipts over scattered runbook folklore

Primary sources:

- My files don't sync  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Database error  
  https://help.resilio.com/hc/en-us/articles/204753659-Database-error

- Peers aren't connecting  
  https://help.resilio.com/hc/en-us/articles/205450205-Peers-aren-t-connecting

- Service files missing / Cannot identify destination folder  
  https://help.resilio.com/hc/en-us/articles/205450225-Service-files-missing-Cannot-identify-destination-folder

- Disconnecting and Removing Folders  
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- Sync Service Troubleshooting on Windows  
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Collecting debug logs automatically  
  https://help.resilio.com/hc/en-us/articles/360019430539-Collecting-debug-logs-automatically

- Agent run out of system notify watchers. Updated files will be uploaded only after periodic folder rescan  
  https://help.resilio.com/hc/en-us/articles/360015593120-Agent-run-out-of-system-notify-watchers-Updated-files-will-be-uploaded-only-after-periodic-folder-rescan

- How soon does synchronization start?  
  https://help.resilio.com/hc/en-us/articles/204754319-How-soon-does-synchronization-start

- Some internal tasks are taking time to complete  
  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete

## Revision addendum — official sources emphasized in rev0379

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about remediation actions, intervention cost, world-fork risk, and post-action ambiguity.
The new questions were:

> where do current official docs most clearly show that Resilio already knows restart, reconnect, re-add, relink, service-world change, watcher-limit changes, and artifact capture are materially different intervention classes?

> where do those same current docs still show that the ordinary operator answer about `what is the least-destructive justified next action, and what stronger sentence would it really prove?` depends on many separate articles instead of one stable product-owned intervention workspace?

The most load-bearing source set for this pass was:

- Resilio's current `My files don't sync` article, which still proposes re-add, disk check, restart, free-space action, deletion of stuck `.!sync` files after restart failure, and time-difference correction.
- Resilio's current `Database error` article, which still presents a rough ladder from restart, to reconnect, to re-add on all peers, to debug-log escalation.
- Resilio's current `Peers aren't connecting` article, which still pushes tracker/predefined-host, router/firewall, relay, multicast, routing, and NIC interventions.
- Resilio's current `Service files missing / Cannot identify destination folder` article, which still treats `.sync` as critical state and still allows remediation that removes the share, deletes `.sync`, and adds the share back.
- Resilio's current `Core warnings` article, which still includes identity unlink/recreate and license remove/reapply steps.
- Resilio's current `Agent run out of system notify watchers` article, which still turns a warning into a system-limit change and Sync restart.
- Resilio's current `Folders are duplicating with an index (i)` article, which still uses disconnect/reconnect and default-arrival-mode change as the remedy/prevention pair.
- Resilio's current `Sync Service Troubleshooting on Windows` article, which still shows a permission workaround that can fork the service storage world and require re-add / re-share or reconnect of all folders.
- Resilio's current `Collecting debug logs automatically` article, which still makes artifact capture itself a restart-bound, time-windowed action.
- Resilio's current `Power user preferences` article, which still includes restart-bound `profiler_enabled` and rescan/save/refresh settings that matter to intervention choice.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that different corrective actions have different scope and cost
- but current Resilio still answers `what should we do next, why not something weaker or stronger, and what would count as success?` too diffusely
- AnonSync should therefore prefer explicit intervention sheets, remediation-ladder reviews, approval proofs, remediation timelines, and durable intervention receipts over troubleshooting folklore

Primary sources:

- My files don't sync  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Database error  
  https://help.resilio.com/hc/en-us/articles/204753659-Database-error

- Peers aren't connecting  
  https://help.resilio.com/hc/en-us/articles/205450205-Peers-aren-t-connecting

- Service files missing / Cannot identify destination folder  
  https://help.resilio.com/hc/en-us/articles/205450225-Service-files-missing-Cannot-identify-destination-folder

- Core warnings  
  https://help.resilio.com/hc/en-us/articles/360001217950-Core-warnings

- Agent run out of system notify watchers  
  https://help.resilio.com/hc/en-us/articles/360015593120-Agent-run-out-of-system-notify-watchers-Updated-files-will-be-uploaded-only-after-periodic-folder-rescan

- Folders are duplicating with an index (i) in their name  
  https://help.resilio.com/hc/en-us/articles/204753869-Folders-are-duplicating-with-an-index-i-in-their-name

- Sync Service Troubleshooting on Windows  
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

- Collecting debug logs automatically  
  https://help.resilio.com/hc/en-us/articles/360019430539-Collecting-debug-logs-automatically

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

## Revision addendum — official sources emphasized in rev0378

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about rollout health signals, evidence freshness, troubleshooting planes, and artifact capture.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `live graph`, `warning`, `history event`, `queue clue`, `support artifact`, `known issue`, and `operator narrative` are different evidence classes?

> where do those same current docs still show that the ordinary operator answer about `is this rollout healthy enough to widen right now?` depends on several articles and support flows instead of one stable product-owned health workspace?

The most load-bearing source set for this pass was:

- Resilio's current `Performance overview` article, which still says graphs are real-time views for ongoing activity, limited to 1-minute, 10-minute, and 1-hour windows, and still says disk-load is not necessarily Sync-only load.
- Resilio's current `My files don't sync` article, which still tells operators to inspect peer connectivity, the Status column, Sync History, per-share queues, and then a long list of possible causes.
- Resilio's current `Errors and warnings` section, which still lists many separate warning articles instead of one joined adjudication workspace.
- Resilio's current `Some internal tasks are taking time to complete` article, which still says important work is hidden, warnings can be intermittent and self-recovering, and debug logs may be needed when symptoms do not clear in a timely manner.
- Resilio's current `Collecting debug logs automatically` and `Collecting debug logs manually` articles, which still say direct technical support is available only for Business customers, that Sync v3 lacks direct technical support, that debug logging may require restart before reproduction, and that useful logs may require at least 15 minutes of post-repro collection.
- Resilio's current `Power user preferences` article, which still exposes telemetry/logging/profiler knobs and still says `profiler_enabled` requires restart to activate.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows warning/UI-signal evolution including improved WebUI warning for license-application failure and a fix for a non-clickable `Can't download file` status.
- Resilio's current `Resilio Sync change log`, which still preserves older evidence that performance charts, statuses, and warnings were introduced incrementally and that receiving-performance-stat accuracy needed improvement.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that evidence provenance, freshness, and hidden work matter
- but current Resilio still answers `is this rollout healthy enough to widen, and what kind of evidence are we really leaning on?` too diffusely
- AnonSync should therefore prefer explicit rollout-health sheets, signal-adjudication reviews, promotion-confidence proof pages, health timelines, and durable health receipts over dashboard folklore

Primary sources:

- Performance overview  
  https://help.resilio.com/hc/en-us/articles/360001331930-Performance-overview

- My files don't sync  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Errors and warnings  
  https://help.resilio.com/hc/en-us/sections/201112455-Errors-and-warnings

- Some internal tasks are taking time to complete  
  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete

- Collecting debug logs automatically  
  https://help.resilio.com/hc/en-us/articles/360019430539-Collecting-debug-logs-automatically

- Collecting debug logs manually  
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Resilio Sync change log  
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log

## Revision addendum — official sources emphasized in rev0377

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about staged movement, rollout risk, install-posture-specific upgrades, restart boundaries, and rollback truth.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `compatible`, `eligible`, `updatable`, `restart-required`, `service-migrate`, `clean-install`, `subset-only feature`, and `safe broad rollout` are different truths?

> where do those same current docs still show that the ordinary operator answer about `can we widen this rollout now, what stops it, and what rollback do we have?` depends on several articles instead of one stable product-owned rollout workspace?

The most load-bearing source set for this pass was:

- Resilio's current `FAQ Resilio Sync 3.0.0` article, which still says v2 and v3 preserve synchronization compatibility while linked devices should all update to v3 to avoid license conflicts.
- Resilio's current `Updating installation to Resilio Sync v3` article, which still says Business cannot be updated to v3, still warns that important changes may affect usage and shares configuration, and still varies the procedure by default install, CLI `/config` or `/storage`, service install, and sidecar `sync.conf` posture.
- Resilio's current `Resilio Sync: supported platforms and system requirements` article, which still shows a narrower v3 envelope than v2 in important ways, including no Windows Server support for v3 while v2 still lists it and broader Linux/FreeBSD coverage.
- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says mixed v2/v3 linked devices are highly inadvisable because licenses may conflict and access to UI and shares configuration may be lost while files remain on storage.
- Resilio's current `Selective Sync` article, which still shows feature availability depending on version and entitlement.
- Resilio's current `Power user preferences` article, which still says older versions may be missing settings or have deprecated ones, and still shows at least one field requiring restart to activate.
- Resilio's current `Running Sync as a service on Windows` article, which still distinguishes migrate-settings from clean-install service paths and still requires service restart to apply config-mode use there.
- Resilio's current `Sync Service Troubleshooting on Windows` article, which still says switching service principal to `Local System` creates another storage world with no old folders present and requires re-add / re-share.
- Resilio's current `Resilio Sync change log`, which still preserves rollout-adjacent issue history around license-after-restart, advanced settings not saved after autoupdate, mixed-version issues, startup crashes, and restart regressions.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that compatibility, eligibility, activation, and safe staged rollout are different truths
- but current Resilio still answers `can we broaden this rollout, what stops it, and what rollback do we have?` too diffusely
- AnonSync should therefore prefer explicit rollout sheets, readiness reviews, ring-promotion proof pages, rollout timelines, and durable rollout receipts over rollout folklore

Primary sources:

- FAQ Resilio Sync 3.0.0  
  https://help.resilio.com/hc/en-us/articles/32109883606035-FAQ-Resilio-Sync-3-0-0

- Updating installation to Resilio Sync v3  
  https://help.resilio.com/hc/en-us/articles/31194252837779-Updating-installation-to-Resilio-Sync-v3

- Resilio Sync: supported platforms and system requirements  
  https://help.resilio.com/hc/en-us/articles/205450965-Resilio-Sync-supported-platforms-and-system-requirements

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Selective Sync  
  https://help.resilio.com/hc/en-us/articles/205458095-Selective-Sync

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Running Sync as a service on Windows  
  https://help.resilio.com/hc/en-us/articles/207701296-Running-Sync-as-a-service-on-Windows

- Sync Service Troubleshooting on Windows  
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

- Resilio Sync change log  
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log

## Revision addendum — official sources emphasized in rev0376

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about policy succession, replacement, retirement, rebind-vs-continuity, and teardown.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `deprecated setting`, `remove-readd replacement`, `disconnect`, `identity-wide remove`, `reconnect rebind`, `config-world successor`, `migrated service successor`, `clean-install fork`, `identity regeneration`, and `remove settings` are different lifecycle truths?

> where do those same current docs still show that the ordinary operator answer about `is this really the next policy, what happened to the old one, and what happens to the waivers and out-of-scope subjects?` depends on several articles instead of one stable product-owned lifecycle workspace?

The most load-bearing source set for this pass was:

- Resilio's current `Power user preferences` article, which still says the article covers today's latest Sync version and that older versions may be missing some settings or still have deprecated ones.
- Resilio's current `What's the difference between Standard and Advanced folders?` article, which still says some Standard-folder changes are not on-the-fly and require removing the share and re-adding it with a new key.
- Resilio's current `Disconnecting and Removing Folders` article, which still distinguishes one-device disconnect from identity-wide remove and still says reconnect may propose a different default path and create a new directory unless the operator manually rebinds to the old path.
- Resilio's current `Running Sync in configuration mode` article, which still says config mode helps apply the same settings on multiple machines, only supports Standard folders there, lets non-default `storage_path` create another settings world, and lets config-authored shared folders override WebUI-added folders while disabling WebUI.
- Resilio's current `Running Sync as a service on Windows` article, which still says service installation can migrate existing shares/settings or create a clean installation that requires re-sharing folders.
- Resilio's current `Sync Service Troubleshooting on Windows` article, which still says switching the service to `Local System` creates another service storage world with no old folders present and requires re-add / re-share.
- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says linking already-running devices can replace one certificate and remove Advanced folders from the app on the affected device.
- Resilio's current `Can I change the name of my Sync identity?` article, which still says changing identity name requires unlinking and creating a new identity, after which Advanced folders are removed from the Sync instance while Standard folders remain.
- Resilio's current `How to uninstall Sync?` article, which still says uninstall plus settings removal is a stronger teardown and that service storage roots differ by service account.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that migration, fork, rebind, and teardown are materially different lifecycle truths
- but current Resilio still answers `what replaced what, who really moved, and is the predecessor actually retired yet?` too diffusely
- AnonSync should therefore prefer explicit lifecycle sheets, supersession reviews, promotion/retirement proof pages, family timelines, and durable lifecycle receipts over succession folklore

Primary sources:

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- What's the difference between Standard and Advanced folders?  
  https://help.resilio.com/hc/en-us/articles/204754679-What-s-the-difference-between-Standard-and-Advanced-folders

- Disconnecting and Removing Folders  
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Running Sync as a service on Windows  
  https://help.resilio.com/hc/en-us/articles/207701296-Running-Sync-as-a-service-on-Windows

- Sync Service Troubleshooting on Windows  
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Can I change the name of my Sync identity?  
  https://help.resilio.com/hc/en-us/articles/206163443-Can-I-change-the-name-of-my-Sync-identity

- How to uninstall Sync?  
  https://help.resilio.com/hc/en-us/articles/204775029-How-to-uninstall-Sync

## Revision addendum — official sources emphasized in rev0375

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about unsupported surfaces, ignored fields, local-parallel lanes, applicability limits, world forks, successor gaps, and temporary exception debt.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `desktop-only`, `ignored in Linux WebUI`, `mobile share-local`, `Simple mode capability limit`, `config-only Standard-folder scope`, `config-authored WebUI suppression`, `service clean-install fork`, and `identity replacement` are different truths?

> where do those same current docs still show that the ordinary operator answer about `why isn't this subject really on profile, is that temporary, and when can the exception be removed?` depends on several articles instead of one stable product-owned waiver workspace?

The most load-bearing source set for this pass was:

- Resilio's current `Folder Preferences` article, which still says folder preferences are available on desktop platforms only.
- Resilio's current `Power user preferences` article, which still says `disable_remove_from_all_devices` is ignored in Linux WebUI.
- Resilio's current `Settings on mobile platforms` article, which still distinguishes device-level settings from mobile-local advanced routes and still says Android `Simple mode` changes whether new shares are simply placed in the default directory.
- Resilio's current `Sync interface on Android` article, which still exposes `Advanced-Preferences` as per-folder settings on the share details surface.
- Resilio's current `Running Sync in configuration mode` article, which still says config mode helps apply the same settings on multiple machines, allows advanced preferences in `sync.conf`, limits config-authored shares to Standard folders, lets non-default `storage_path` create another settings world, and disables WebUI while overriding folders previously added from WebUI when shared folders are declared in config.
- Resilio's current `Running Sync as a service on Windows` article, which still says service install can migrate existing shares/settings or create a clean installation that requires re-sharing folders.
- Resilio's current `Sync Service Troubleshooting on Windows` article, which still says changing the service principal to `Local System` can widen access while creating another service storage world with no previous folders present and requiring re-add / re-share.
- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says linking already-running devices can replace one certificate and remove Advanced folders from the app on the device that takes over the new certificate.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that unsupported, ignored, local-only, and successor-gap situations are materially different
- but current Resilio still answers `why is this subject not really on profile, is that temporary, and when can we retire the exception?` too diffusely
- AnonSync should therefore prefer explicit waiver sheets, cohort debt reviews, issuance-proof pages, drift timelines, and durable waiver receipts over exception folklore

Primary sources:

- Folder Preferences  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Settings on mobile platforms  
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- Sync interface on Android  
  https://help.resilio.com/hc/en-us/articles/213500383-Sync-interface-on-Android

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Running Sync as a service on Windows  
  https://help.resilio.com/hc/en-us/articles/207701296-Running-Sync-as-a-service-on-Windows

- Sync Service Troubleshooting on Windows  
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

## Revision addendum — official sources emphasized in rev0374

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about reusable policy, linked-device defaults, per-folder and global defaults, config-authored replication, mobile/share-local lanes, and successor-world forks.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `linked-device default mode`, `default arrival root`, `per-folder policy`, `global advanced default`, `mobile-local share setting`, `config-authored settings replication`, and `service migration vs clean-install fork` are different truths?

> where do those same current docs still show that the ordinary operator answer about `what named policy profile exists, what fields it covers, which subjects are bound to it, and what a revision rollout will actually change` depends on several articles instead of one stable product-owned workspace?

The most load-bearing source set for this pass was:

- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says linked devices make all folders automatically available across the linked family and lets each device choose a synchronization mode for new arrivals.
- Resilio's current `Synchronization Modes` article, which still points the device default to `Preferences -> Identity -> Default connect folder mode`.
- Resilio's current `Sync Preferences` article, which still describes default folder and file locations for new arrivals.
- Resilio's current `Folder Preferences` article, which still exposes per-folder policy such as Archive, overwrite-on-read-only, relay/tracker/LAN/predefined-host discovery, and file download priority.
- Resilio's current `Power user preferences` plus `File download priority` articles, which still show a global advanced default layer and still show manually altered shares detaching from later default changes.
- Resilio's current `Running Sync in configuration mode` article, which still says config mode helps apply the same settings on multiple machines, allows advanced preferences in `sync.conf`, limits config-authored shares to Standard folders, disables WebUI when shared folders are specified there, and lets non-default `storage_path` create another settings world.
- Resilio's current `Running Sync as a service on Windows` article, which still says service installation can migrate existing shares/settings or create a clean installation that requires re-sharing folders.
- Resilio's current `Settings on mobile platforms` and `Sync interface on Android` articles, which still show device-level and share-level advanced preferences as separate local routes.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that reusable policy is spread across real defaults, overrides, device-family lanes, config authorship, and world forks
- but current Resilio still answers `what profile governs this subject, and will the next revision apply here?` too diffusely
- AnonSync should therefore prefer explicit policy-profile sheets, conformance reviews, rollout-proof pages, drift timelines, and durable profile receipts over defaults folklore

Primary sources:

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Synchronization Modes  
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Folder Preferences  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- File download priority  
  https://help.resilio.com/hc/en-us/articles/42328167759251-File-download-priority

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Running Sync as a service on Windows  
  https://help.resilio.com/hc/en-us/articles/207701296-Running-Sync-as-a-service-on-Windows

- Settings on mobile platforms  
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- Sync interface on Android  
  https://help.resilio.com/hc/en-us/articles/213500383-Sync-interface-on-Android

## Revision addendum — official sources emphasized in rev0373

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about baseline anchoring, override lineage, mobile-parallel routes, config/service world drift, search-vs-compare limits, and local-only custom labels.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `visible value`, `inherit`, `manual detach`, `explicit none`, `mobile-local share setting`, `startup config world`, `service fork`, and `local custom name` are different truths?

> where do those same current docs still show that the ordinary operator answer about `do these really match, and what exactly would aligning them change?` depends on several articles instead of one stable product-owned comparison workspace?

The most load-bearing source set for this pass was:

- Resilio's current `File download priority` article, which still says the same conceptual policy can live in share preferences or in the global power-user default, that the default applies to existing unchanged shares and new shares, and that a manually altered share stops following later default changes even if later set back to `None`.
- Resilio's current `Power user preferences` article, which still says `folder_defaults.transfer_priority` is the default for shares whose priority was not altered manually in folder preferences.
- Resilio's current Android and iOS interface articles, which still show per-share advanced preferences as device-local routes distinct from the general settings surface.
- Resilio's current `Running Sync in configuration mode` article, which still says config mode can set up only Standard folders, that non-default storage path creates another settings world, and that config-authored shared folders override folders previously added from WebUI while disabling WebUI.
- Resilio's current `Running Sync as a service on Windows` article, which still says service installation can migrate existing shares/settings or create a clean installation that requires re-sharing folders.
- Resilio's current `Setting custom name for sync shares` article, which still says custom names are local to Sync UI, do not rename the disk folder, do not propagate to other peers, and can remain in the UI after disconnect until reset.
- Resilio's current `How do I perform a search in Sync?` article together with the current change log, which still show useful search improvements for folders, files, devices, users, and power-user settings — improvements that help locate things but still do not produce one explicit equivalence or realignment workspace.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that same-looking settings situations can differ materially by lineage, route, world, and label scope
- but current Resilio still answers `do these really match, and what will alignment actually change?` too diffusely
- AnonSync should therefore prefer explicit baseline sheets, equivalence reviews, realignment proof pages, baseline-drift timelines, and durable lineage receipts over parity folklore

Primary sources:

- File download priority  
  https://help.resilio.com/hc/en-us/articles/42328167759251-File-download-priority

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Sync interface on Android  
  https://help.resilio.com/hc/en-us/articles/213500383-Sync-interface-on-Android

- Sync Interface on iOS devices  
  https://help.resilio.com/hc/en-us/articles/212016726-Sync-Interface-on-iOS-devices

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Running Sync as a service on Windows  
  https://help.resilio.com/hc/en-us/articles/207701296-Running-Sync-as-a-service-on-Windows

- Setting custom name for sync shares  
  https://help.resilio.com/hc/en-us/articles/360011865879-Setting-custom-name-for-sync-shares

- How do I perform a search in Sync?  
  https://help.resilio.com/hc/en-us/articles/205457725-How-do-I-perform-a-search-in-Sync

- Resilio Sync change log  
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log

## Revision addendum — official sources emphasized in rev0372

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about default reach, per-share detachment, explicit-none ambiguity, mobile-parallel settings, startup-owned config, and service-world migration vs clean-install forks.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `default`, `share override`, `explicit none`, `mobile-local parallel value`, `startup config`, and `service-world fork` are different truths?

> where do those same current docs still show that the ordinary operator answer about `who exactly will this setting change reach, who stays detached, and am I looking at inherit or explicit none?` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `File download priority` article, which still says the same conceptual policy can live in share preferences or in the global power-user default, that the global default applies to existing unchanged shares and new shares, and that a manually altered share stops following later global-default changes even if it is later set back to `None`.
- Resilio's current `Sync Preferences`, `Folder Preferences`, and `Power user preferences` articles, which still split one settings family across desktop-global, per-share, and advanced-default surfaces.
- Resilio's current `Settings on mobile platforms` and `Sync interface on Android` articles, which still show mobile-global and mobile per-share advanced routes as separate local lanes.
- Resilio's current `Running Sync in configuration mode` article, which still says advanced preferences can be authored in `sync.conf`, only Standard folders can be configured there, and storage-path choice can create another settings world.
- Resilio's current `Running Sync as a service on Windows` article, which still says service installation can migrate existing shares/settings or create a clean installation that requires re-sharing the necessary folders.
- Resilio's current `Resilio Sync change log`, which still shows useful local improvements such as `search in power user settings`, remembered share-dialog state, and search for folders/users/devices — improvements that help local navigation but still do not produce one explicit pre-commit impact planner.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that default reach and manual detachment are not one thing
- but current Resilio still answers `who will really change, who will remain protected, and what does this visible value actually mean?` too diffusely
- AnonSync should therefore prefer explicit setting-impact sheets, impact-cohort reviews, pre-commit impact proof pages, impact-drift timelines, and durable lineage receipts over blast-radius folklore

Primary sources:

- File download priority  
  https://help.resilio.com/hc/en-us/articles/42328167759251-File-download-priority

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Folder Preferences  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Settings on mobile platforms  
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- Sync interface on Android  
  https://help.resilio.com/hc/en-us/articles/213500383-Sync-interface-on-Android

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Running Sync as a service on Windows  
  https://help.resilio.com/hc/en-us/articles/207701296-Running-Sync-as-a-service-on-Windows

- Resilio Sync change log  
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log

## Revision addendum — official sources emphasized in rev0371

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about settings placement, menu locality, surface asymmetry, advanced-preference search, startup-authored config, service-owned config routes, and WebUI omissions.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `global setting`, `per-folder setting`, `power-user default`, `mobile setting`, `startup config`, `service config`, and `not editable on this surface` are different truths?

> where do those same current docs still show that the ordinary operator answer about `where do I change this, what scope does it touch, and can I even edit it from here?` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Sync Main View (Desktop)` article, which still routes the operator to Sync Preferences, Folder Preferences, Power user preferences, column controls, and share menus instead of one canonical setting-locator object.
- Resilio's current `Sync Preferences` article, which still keeps global update, startup, notifications, default locations, bandwidth, scheduler, listening port, UPnP, proxy, debug logging, and the jump into Power user preferences inside one desktop-only surface.
- Resilio's current `Folder Preferences` article, which still keeps archive, overwrite, relay, tracker, search LAN, predefined hosts, and file download priority in a separate desktop-only per-folder surface.
- Resilio's current `Power user preferences` article, which still exposes a distinct advanced surface and still carries setting-specific activation details such as restart requirements for some items.
- Resilio's current `File download priority` article together with the change log, which still show a cross-surface split between per-share priority and a power-user default, plus the useful but still partial `search in power user settings` improvement.
- Resilio's current `Settings on mobile platforms` and `Sync interface on Android` articles, which still show that identity, network, notifications, advanced settings, and per-share advanced settings live on separate mobile routes rather than one unified setting contract.
- Resilio's current `Running Sync in configuration mode` and `Running Sync as a service on Windows` articles, which still say config-mode and service-mode settings are authored through `sync.conf`, with service-mode requiring the file in the service storage folder and restart.
- Resilio's current `Updating Sync to latest version` article, which still says some actions such as `Check now` are unavailable in WebUI.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that settings do not all live in one place
- but current Resilio still answers `where do I change this, what scope does it govern, and can I actually edit it from here?` too diffusely
- AnonSync should therefore prefer explicit setting-locator sheets, route reviews, context proof pages, change itineraries, and durable lineage receipts over settings-menu folklore

Primary sources:

- Sync Main View (Desktop)  
  https://help.resilio.com/hc/en-us/articles/204755009-Sync-Main-View-Desktop

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Folder Preferences  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- File download priority  
  https://help.resilio.com/hc/en-us/articles/42328167759251-File-download-priority

- Settings on mobile platforms  
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- Sync interface on Android  
  https://help.resilio.com/hc/en-us/articles/213500383-Sync-interface-on-Android

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Running Sync as a service on Windows  
  https://help.resilio.com/hc/en-us/articles/207701296-Running-Sync-as-a-service-on-Windows

- Updating Sync to latest version  
  https://help.resilio.com/hc/en-us/articles/115001130830-Updating-Sync-to-latest-version

- Resilio Sync change log  
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log

## Revision addendum — official sources emphasized in rev0365

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about hot-reread files, restart-gated settings, cold-loaded config, service restarts, and remembered network-state burn-down.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `saved`, `active now`, `re-read on rescan`, `restart required`, and `cold-loaded on startup` are different truths?

> where do those same current docs still show that the ordinary operator answer about `when is this change actually in force, and what stale runtime debt still survives?` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Ignoring files in Sync (Ignore List)` article, which still says IgnoreList is re-read every time it is changed or at folder-rescan intervals, yet still recommends restarting Sync if the operator wants the change applied immediately.
- Resilio's current `Setting Delay Time For Syncing` article, which still says FileDelayConfig should be edited, saved, and then activated by restarting Sync.
- Resilio's current `Collecting debug logs manually` and `Collecting debug logs automatically` articles, which still say debug logging should be enabled and then Sync restarted to make sure the logging state is active.
- Resilio's current `How do I reset my WebUI password?` article, which still says password-reset flows require quitting Sync, changing on-disk state, and restarting before the new credentials become authoritative.
- Resilio's current `Sync Service Troubleshooting on Windows` article, which still says some WebUI listen changes require service restart and that a sync.conf dropped into the service storage folder is loaded automatically by the service on startup.
- Resilio's current `Can I force Sync to do local network (LAN) syncing only and not sync via the Internet?` article, which still says old Internet-learned peer addresses may persist until peer-expiration settings are changed and the client is restarted through a cache-burn sequence.
- Resilio's current Linux/package guidance, which still says some install/update/config-mode changes are adopted on stop/start boundaries rather than hot-applied inside a running process.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that activation timing is not one thing
- but current Resilio still answers `when is this change really in force, and what stale runtime debt remains?` too diffusely
- AnonSync should therefore prefer explicit activation-boundary sheets, restart-debt reviews, applied-state proof pages, activation timelines, and durable lineage receipts over save/restart folklore

Primary sources:

- Ignoring files in Sync (Ignore List)  
  https://help.resilio.com/hc/en-us/articles/205458165-Ignoring-files-in-Sync-Ignore-List

- Setting Delay Time For Syncing  
  https://help.resilio.com/hc/en-us/articles/207491426-Setting-Delay-Time-For-Syncing

- Collecting debug logs manually  
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

- Collecting debug logs automatically  
  https://help.resilio.com/hc/en-us/articles/360019430539-Collecting-debug-logs-automatically

- How do I reset my WebUI password?  
  https://help.resilio.com/hc/en-us/articles/205450295-How-do-I-reset-my-WebUI-password

- Sync Service Troubleshooting on Windows  
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

- Can I force Sync to do local network (LAN) syncing only and not sync via the Internet?  
  https://help.resilio.com/hc/en-us/articles/204754349-Can-I-force-Sync-to-do-local-network-LAN-syncing-only-and-not-sync-via-the-Internet

- Installing Sync package on Linux  
  https://help.resilio.com/hc/en-us/articles/206178924-Installing-Sync-package-on-Linux

## Revision addendum — official sources emphasized in rev0364

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about changed-piece transfer, whole-file resend after piece-shift edits, Archive-gated rename reuse, and the difference between queue priority and byte cost.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `changed data only`, `whole file again`, `rename without retransmit`, and `downloaded first` are different truths?

> where do those same current docs still show that the ordinary operator answer about `how many bytes will actually move, why did this resend in full, and did priority change order or byte cost?` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `When a file changes, does Resilio Sync transfer the entire file again, or just the part that's changed?` article, which still says Sync splits files into pieces from 32KB up to 2MB, normally transfers only changed pieces, but re-syncs the whole file if the edit shifts all pieces, with a stronger diff-delta answer reserved to Sync Business.
- Resilio's current `What happens when file is renamed` article, which still says rename reuse depends on finding the same hash in Archive and that without Archive enabled the bytes will be re-synced again.
- Resilio's current `File download priority` article, which still says priority reorders active downloads by file modification time or size, can suspend lower-priority transfers immediately, but strictly follows prioritization rules only for files split in pieces during transfer.
- That same current priority article, which still says queue rebuilds, the 50k active-file ceiling, and UI ordering mismatches can alter perceived behavior without changing the underlying byte-cost class.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that network movement shape is not one thing
- but current Resilio still answers `how many bytes will move here, why did this resend in full, and what exactly did priority change?` too diffusely
- AnonSync should therefore prefer explicit transfer-cost sheets, resend-geometry reviews, byte-cost proof pages, transfer-shape timelines, and durable lineage receipts over overloaded performance folklore

Primary sources:

- When a file changes, does Resilio Sync transfer the entire file again, or just the part that's changed?  
  https://help.resilio.com/hc/en-us/articles/206217095-When-a-file-changes-does-Resilio-Sync-transfer-the-entire-file-again-or-just-the-part-that-s-changed

- What happens when file is renamed  
  https://help.resilio.com/hc/en-us/articles/209606526-What-happens-when-file-is-renamed

- File download priority  
  https://help.resilio.com/hc/en-us/articles/42328167759251-File-download-priority

## Revision addendum — official sources emphasized in rev0363

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about encrypted-folder rescue preconditions, saved-secret escrow, database continuity, db-path discovery, storage-root variability, and the hard limit between ciphertext retention and actual late decrypt authority.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `encrypted backup exists`, `future rescue is still possible`, `the right secret was saved`, `the right database continuity survived`, and `the recovery lane is still usable` are different truths?

> where do those same current docs still show that the ordinary operator answer about `if the source dies later, is this encrypted backup really salvageable and what action would silently break that?` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Encrypted folders` article, which still says an encrypted backup peer becomes a later rescue source only if RW and RO keys were saved somewhere and the encrypted folder was not removed from Sync so the database remains the same as initially created.
- That same current `Encrypted folders` article, which still says the encrypted node cannot decrypt files itself, recovery can instead happen through reconnecting with the RW key or through a local CLI decrypt lane, and the db path may need to be learned from debug `sync.log` by finding the shareID there.
- Resilio's current `Sync Storage folder` article, which still says the storage directory holds shares' databases and that the storage location varies by operating system, Linux packaging mode, and service account.
- Resilio's current `Disconnecting and Removing Folders` article, which still says disconnect/remove changes Sync participation while folders remain in the filesystem, which is exactly why disk survival is weaker than continuity survival.
- Resilio's current `Using Archive for file versioning and restoring deleted files` article together with `Encrypted folders`, which still shows that ordinary Archive restore and encrypted-node salvage are different ladders and that encrypted peers cannot republish deleted files back from Archive.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that encrypted-backup rescue depends on hidden prerequisites preserved ahead of failure
- but current Resilio still answers `is this backup actually salvageable later, and what action would silently break that option?` too diffusely
- AnonSync should therefore prefer explicit salvage-readiness sheets, continuity-escrow reviews, recovery-precondition proof pages, salvage-viability timelines, and durable lineage receipts over buried disaster-recovery prose

Primary sources:

- Encrypted folders  
  https://help.resilio.com/hc/en-us/articles/207370466-Encrypted-folders

- Sync Storage folder  
  https://help.resilio.com/hc/en-us/articles/206664690-Sync-Storage-folder

- Disconnecting and Removing Folders  
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- Using Archive for file versioning and restoring deleted files.  
  https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files

## Revision addendum — official sources emphasized in rev0361

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about UI/runtime surface asymmetry, WebUI-default environments, desktop-only settings, file-browser fallback, and mobile/background differences.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `feature exists` and `this surface can execute it` are not the same thing?

> where do those same current docs still show that the ordinary operator answer about `can I do this here, can I verify it here, and where does recovery actually live?` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Configuring WebUI` article, which still says WebUI is the default and only option on Linux/NAS and the default UI path on Windows service installs.
- Resilio's current `Folder Preferences` article, which still says folder preferences are available on desktop platforms only.
- Resilio's current `Power user preferences` article, which still says `disable_remove_from_all_devices` is ignored in Linux WebUI.
- Resilio's current `Using Archive for file versioning and restoring deleted files` article, which still says `Open Archive` is a desktop Sync UI action, while WebUI and Android must use the file browser and iOS has no Archive access there.
- Resilio's current `Updating Sync to latest version` article, which still says manual `Check now` is not available in WebUI.
- Resilio's current `Sharing a folder locally` article, which still says local shares are supported only on desktop versions.
- Resilio's current `Does Sync work in background?` and `Sync for iOS Peculiarities` articles, which still say desktop and Android can continue in background while iOS transfer requires the app to be open.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that action availability is surface- and runtime-shaped rather than universal
- but current Resilio still answers `where can I really do this, where can I only witness it, and where does recovery actually live?` too diffusely
- AnonSync should therefore prefer explicit action-surface sheets, surface-locality reviews, action-availability proof pages, surface-shift timelines, and durable lineage receipts over overloaded surface folklore

Primary sources:

- Configuring WebUI  
  https://help.resilio.com/hc/en-us/articles/115001184490-Configuring-WebUI

- Folder Preferences  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Using Archive for file versioning and restoring deleted files.  
  https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files

- Updating Sync to latest version  
  https://help.resilio.com/hc/en-us/articles/115001130830-Updating-Sync-to-latest-version

- Sharing a folder locally  
  https://help.resilio.com/hc/en-us/articles/360011582500-Sharing-a-folder-locally

- Does Sync work in background?  
  https://help.resilio.com/hc/en-us/articles/206816823-Does-Sync-work-in-background

- Sync for iOS Peculiarities  
  https://help.resilio.com/hc/en-us/articles/205506539-Sync-for-iOS-Peculiarities

## Revision addendum — official sources emphasized in rev0358

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about vendor visibility, tracker metadata, relay ciphertext carriage, fragment-local link secrecy, optional telemetry, explicit evidence-send disclosure, and true vendor non-control.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `vendor can see`, `vendor can carry`, `vendor can count`, `vendor can inspect after user send`, and `vendor can intervene` are not the same thing?

> where do those same current docs still show that the ordinary operator answer about `what can Resilio know or do about this share right now?` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Can Resilio team see and block/remove any Sync folders?` article, which still says Resilio neither hosts nor caches content, cannot see link-specific information placed after `#`, cannot generally interfere with decentralized peer-finding, and cannot modify or remove data except through user/peer devices that already hold it.
- Resilio's current `Can others see my files? How secure is sharing by Resilio Sync?` article, which still says the team cannot see user files but still distinguishes tracker metadata, relay carriage, update checks, landing-page counting, license purchase identity, and optional service disabling.
- Resilio's current `What ports and protocols are used by Sync?` article, which still says clients fetch `sync.conf`, then communicate IP addresses, listening port, and share list to trackers so peers can find each other.
- Resilio's current `What is a Relay Server?` article, which still says relay is a distinct fallback carrier and is visibly marked in the peer list.
- Resilio's current `Power user preferences` article, which still says `send_statistics` controls anonymous statistical metrics as a separate disclosure lane.
- Resilio's current `Collecting debug logs manually`, `Collecting debug logs automatically`, and crash/core-dump collection articles, which still say direct technical support is lane-limited and that richer visibility into an installation depends on explicit user capture and send.
- Resilio's current `How to Report Security Vulnerabilities to Resilio, Inc.` article, which still says security disclosure is its own vendor-contact lane.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that service contact, service-visible metadata, ciphertext carriage, explicit evidence send, and absent vendor deletion power are materially different
- but current Resilio still answers `what can the vendor know or do right now?` too diffusely
- AnonSync should therefore prefer explicit vendor-ceiling contracts, service-visible-facts review, intervention-authority proof, disclosure timelines, and durable lineage receipts over security-FAQ folklore

## Additional Resilio official sources emphasized in rev0358

- Can Resilio team see and block/remove any Sync folders?  
  https://help.resilio.com/hc/en-us/articles/205451105-Can-Resilio-team-see-and-block-remove-any-Sync-folders

- Can others see my files? How secure is sharing by Resilio Sync?  
  https://help.resilio.com/hc/en-us/articles/205451025-Can-others-see-my-files-How-secure-is-sharing-by-Resilio-Sync

- What ports and protocols are used by Sync?  
  https://help.resilio.com/hc/en-us/articles/204754759-What-ports-and-protocols-are-used-by-Sync

- What is a Relay Server?  
  https://help.resilio.com/hc/en-us/articles/204754779-What-is-a-Relay-Server

- Power user preferences.  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Collecting debug logs manually.  
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

- Collecting debug logs automatically.  
  https://help.resilio.com/hc/en-us/articles/360019430539-Collecting-debug-logs-automatically

- Collecting crash reports, mini-dumps and core dumps.  
  https://help.resilio.com/hc/en-us/articles/206214615-Collecting-crash-reports-mini-dumps-and-core-dumps

- Collecting core dump on NAS devices.  
  https://help.resilio.com/hc/en-us/articles/360015557220-Collecting-core-dump-on-NAS-devices

- How to Report Security Vulnerabilities to Resilio, Inc.  
  https://help.resilio.com/hc/en-us/articles/360000294599-How-to-Report-Security-Vulnerabilities-to-Resilio-Inc

## Revision addendum — official sources emphasized in rev0348

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about effect provenance, automatic source-heal, inherited local-share cascades, encrypted hard-wiring, manual Archive replay, and touch-based detection induction.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that a visible state can come from very different causes?

> where do those same current docs still show that the ordinary operator answer about `who or what actually caused the state I see now, and did bytes change or did only product notice change?` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `User Management` article, which still says Read Only changes do not propagate, that changed files on a Read Only peer suspend further synchronization for that peer, and that disconnect revokes future updates while leaving already-synced files in place.
- Resilio's current `Is one-way synchronization possible?` article, which still says `Overwrite any changed files` reverts content edits, restores deletions, re-downloads old names after renames, leaves added files local-only and unsynced, and still allows RO peers to serve unmodified bytes.
- Resilio's current `Folder Preferences` article, which still says `Overwrite any changed files` is potentially destructive and unavailable for RO folders with Selective Sync ON.
- Resilio's current `Sharing a folder locally` article, which still says local shares only sync with the parent source, inherit the source permission floor, can automatically downshift when the source seat is narrowed, and for Advanced shares may require remove-and-reshare instead of in-place permission editing.
- Resilio's current `Encrypted folders` article, which still says encrypted nodes are RO, have overwrite-heal always enabled, follow delete state, and cannot republish deleted files back from their own Archive.
- Resilio's current `Using Archive for file versioning and restoring deleted files` article, which still says restore is manual, requires Sync to be running if the older version is to be uploaded to others rather than re-archived later, and does not record in Archive which peer made the change.
- Resilio's current `How to touch files?` article, which still says manual `touch` is a remediation when Sync missed an update because Sync considers a file changed when its modified time or size changes.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that direct publish, source-heal, inheritance, hard-wiring, manual replay, and detection induction are materially different
- but current Resilio still answers `who or what actually caused the state I see now?` too diffusely
- AnonSync should therefore prefer explicit effect-provenance contracts, surprising-state review, state-origin proof, provenance timelines, and durable lineage receipts over result-label folklore

## Additional Resilio official sources emphasized in rev0348

- User Management.  
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- Is one-way synchronization possible?  
  https://help.resilio.com/hc/en-us/articles/204754279-Is-one-way-synchronization-possible

- Folder Preferences.  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- Sharing a folder locally.  
  https://help.resilio.com/hc/en-us/articles/360011582500-Sharing-a-folder-locally

- Encrypted folders.  
  https://help.resilio.com/hc/en-us/articles/207370466-Encrypted-folders

- Using Archive for file versioning and restoring deleted files.  
  https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files

- How to touch files?  
  https://help.resilio.com/hc/en-us/articles/209606046-How-to-touch-files

## Revision addendum — official sources emphasized in rev0347

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about effective seat posture, local-divergence fate on narrow seats, byte-serving by RO peers, linked-device Owner defaults, local-share inherited downshift, and encrypted-node hard-wiring.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `Read Only` is not one flat capability?

> where do those same current docs still show that the ordinary operator answer about `what can this peer really do, what happens to its unauthorized edits, and is this posture direct or inherited?` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `User Management` article, which still says different permissions can be issued to different identities, linked devices all act as Owners, RO edits do not propagate and suspend further sync for the changed file, RW peers publish changes, and Owner adds onward-share and revocation authority.
- Resilio's current `Is one-way synchronization possible?` article, which still says RO peers trigger suspension on changed files, that `Overwrite any changed files` restores deletes, reverts content edits, re-downloads old names after renames, leaves local additions unsynced, and still allows RO peers to transfer unmodified files to newly connected peers.
- Resilio's current `Folder Preferences` article, which still says `Overwrite any changed files` is potentially destructive and unavailable for RO folders with Selective Sync ON.
- Resilio's current `Sharing a folder locally` article, which still says local shares inherit the permission floor of the source, can never receive Owner, automatically downshift if the source seat is narrowed, cannot be changed through user management for Advanced shares, and sync only with the parent source rather than directly with remote peers.
- Resilio's current `Encrypted folders` article, which still says encrypted F-key seats are RO, have overwrite-heal always enabled, do not support Selective Sync, follow delete state, and cannot restore deleted files back from their Archive because they are both RO and delete-following.
- Resilio's current `How to create a Read Only folder while syncing across linked devices?` article, which still says linked devices default to Owner posture and that creating a true RO posture inside that family requires a separate Standard-folder-plus-RO-key path.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that grant label, local-divergence fate, serve-right, and derived posture are materially different
- but current Resilio still answers `what can this peer really do and why did this local edit behave that way?` too diffusely
- AnonSync should therefore prefer explicit effective-seat contracts, narrow-seat mutation review, delegation-and-serve proof, derived-seat review, and durable lineage receipts over permission folklore

## Additional Resilio official sources emphasized in rev0347

- User Management.  
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- Is one-way synchronization possible?  
  https://help.resilio.com/hc/en-us/articles/204754279-Is-one-way-synchronization-possible

- Folder Preferences.  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- Sharing a folder locally.  
  https://help.resilio.com/hc/en-us/articles/360011582500-Sharing-a-folder-locally

- Encrypted folders.  
  https://help.resilio.com/hc/en-us/articles/207370466-Encrypted-folders

- How to create a Read Only folder while syncing across linked devices?  
  https://help.resilio.com/hc/en-us/articles/206216565-How-to-create-a-Read-Only-folder-while-syncing-across-linked-devices

## Revision addendum — official sources emphasized in rev0345

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about disconnected visibility, placeholder-backed namespace, on-demand materialization, ghost files, local-share dependency, and delete-safety rails.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `shown here` is not the same thing as `stored here`?

> where do those same current docs still show that the ordinary operator answer about `what actually exists here right now, and can I really fetch it later?` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Folder Types and Management` article, which still says disconnected folders may be shown while taking no local space and can even lack a folder path, while Selective Sync exposes placeholder-backed visibility rather than full byte residency.
- Resilio's current `Synchronization Modes` article, which still distinguishes disconnected, Selective Sync, and fully synced modes; still says placeholders are used in Selective Sync; still says on-demand fetch requires at least one peer with the file online; and still separates `Remove from this device` from `Remove from all devices`.
- Resilio's current `What Is an RSLS File?` article, which still says `.rsls` placeholder files are 0-byte representations without actual content and explains that materialization fetches the real bytes only on demand.
- Resilio's current `Selective Sync` article, which still says newly arrived files can be presented as placeholders and warns that removing a Selective Sync share removes placeholders from the local filesystem on that device.
- Resilio's current `Disconnecting and Removing Folders` article, which still says disconnect changes sync participation without necessarily deleting local bytes, still notes placeholder removal on disconnect, and still warns that reconnect may propose a new default path.
- Resilio's current `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time.` article, which still describes ghost files where a file was announced into the namespace but no peer actually retains the bytes anymore.
- Resilio's current `Sharing a folder locally` article, which still says local shares only get data from the parent source share and therefore cannot materialize files when the parent has only placeholders.
- Resilio's current `Power user preferences` article, which still exposes `disable_remove_from_all_devices` and `recreate_placeholders_on_removal` as separate safety rails that materially alter destructive authority on placeholder-backed surfaces.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that row visibility, placeholder namespace, byte residency, source guarantee, and delete authority are materially different
- but current Resilio still answers `what actually exists here now, and what would this gesture really destroy?` too diffusely
- AnonSync should therefore prefer explicit presence contracts, residency-mode review, materialization proof, parent-source dependency review, and durable lineage receipts over placeholder folklore

## Additional Resilio official sources emphasized in rev0345

- Folder Types and Management.  
  https://help.resilio.com/hc/en-us/articles/204762459-Folder-Types-and-Management

- Synchronization Modes.  
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- What Is an RSLS File?  
  https://help.resilio.com/hc/en-us/articles/206115384-What-Is-an-RSLS-File

- Selective Sync.  
  https://help.resilio.com/hc/en-us/articles/205458095-Selective-Sync

- Disconnecting and Removing Folders.  
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- Cannot download files / These files cannot be downloaded as there are no source peers online for too long time.  
  https://help.resilio.com/hc/en-us/articles/360010899719-Cannot-download-files-These-files-cannot-be-downloaded-as-there-are-no-source-peers-online-for-too-long-time

- Sharing a folder locally.  
  https://help.resilio.com/hc/en-us/articles/360011582500-Sharing-a-folder-locally

- Power user preferences.  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

## Revision addendum — official sources emphasized in rev0344

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about live change witness, manual touch remediation, writer-delay buffering, locked-file retries, watcher exhaustion, rescan fallback, and database-only timestamp authority.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `changed` and `waiting` are not one flat truth?

> where do those same current docs still show that the ordinary operator answer about `did the product really see this edit, is it intentionally waiting, or is timestamp truth already divorced from the disk view?` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `How to touch files?` article, which still says Sync relies on system notifications for file updates, still treats changed modified time or size as change evidence, and still recommends manual `touch` as explicit remediation when those signals were missed.
- Resilio's current `Setting Delay Time For Syncing` article, which still says file-class delay exists for common Office / Autodesk / Adobe extensions, defaults to 10 seconds, and requires restart after configuration edits.
- Resilio's current `Locked files` article, which still says Sync can list blocked files but still cannot identify which application owns the lock.
- Resilio's current `Power user preferences` article, which still keeps `recheck_locked_files_interval`, `folder_rescan_interval`, and `ignore_mtime_assign_errors` separate and still says the mtime-write-failure fallback can leave the correct timestamp only in the database while disk shows a `current` timestamp.
- Resilio's current `Agent run out of system notify watchers. Updated files will be uploaded only after periodic folder rescan` article, which still says watcher exhaustion downgrades discovery to manual or periodic rescans until the system limit is raised.
- Resilio's current `My files don't sync` article, which still points operators toward restart, touch, locked-file checks, and time-difference checks when observation and movement disagree.
- Resilio's current `Sync and SMB file shares` article, which still says SMB lock behavior can persist oddly depending on the SMB implementation and therefore can change how blocked-file symptoms present.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that live observation, rediscovery, delay-hold, lock blockade, and database-kept time are materially different
- but current Resilio still answers `did the product really see this edit and what exactly is it waiting on now?` too diffusely
- AnonSync should therefore prefer explicit change-witness contracts, writer-pressure review, observation proof, timestamp-authority downgrade review, and durable lineage receipts over detection folklore

## Additional Resilio official sources emphasized in rev0344

- How to touch files.  
  https://help.resilio.com/hc/en-us/articles/209606046-How-to-touch-files

- Setting Delay Time For Syncing.  
  https://help.resilio.com/hc/en-us/articles/207491426-Setting-Delay-Time-For-Syncing

- Locked files.  
  https://help.resilio.com/hc/en-us/articles/205504549-Locked-files

- Power user preferences.  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Agent run out of system notify watchers. Updated files will be uploaded only after periodic folder rescan.  
  https://help.resilio.com/hc/en-us/articles/360015593120-Agent-run-out-of-system-notify-watchers-Updated-files-will-be-uploaded-only-after-periodic-folder-rescan

- My files don't sync.  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Sync and SMB file shares.  
  https://help.resilio.com/hc/en-us/articles/207755736-Sync-and-SMB-file-shares

## Revision addendum — official sources emphasized in rev0343

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about chronology authority, offline-return precedence, time-skew gating, archive-based loser survival, manual touch remediation, and file-class delay mitigation.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `newer` is not one flat truth?

> where do those same current docs still show that the ordinary operator answer about `why did this version win, and what must I prove before an older one is authoritative again?` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `What if several people make changes to the same file?` article, which still says online edits are synchronized chronologically by modification time, but a peer that edited offline and later returns can still outrank later online edits and overwrite them, with overwritten versions placed in Archive.
- Resilio's current `"Time difference" error` article, which still says Sync converts file times to GMT/UTC, still treats more than 600 seconds of peer-time drift as a hard stop for transfer, and still notes that mobile surfaces may show only an empty list under that condition.
- Resilio's current `Using Archive for file versioning and restoring deleted files` article, which still says restoring an older version requires Sync to be running at restore time or the restored file can be considered older again and moved back to Archive on rescan.
- Resilio's current `How to touch files?` article, which still says Sync considers a file changed when its modified time or size changes and still recommends manual `touch`/equivalent to force detection when those signals are missed.
- Resilio's current `Setting Delay Time For Syncing` article, which still says file-class delay exists to reduce edit-time conflicts, defaults to 10 seconds for listed extensions, and requires restart after configuration changes.
- Resilio's current `Power user preferences` article, which still exposes `sync_max_time_diff` and `ignore_mtime_assign_errors` as separate low-level authorities that materially shape chronology trust and mtime interpretation.
- Resilio's current `My files don't sync` article, which still points operators toward time-difference checks, touch/remediation, and queue/history inspection when chronology and observation disagree.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that chronology, time trust, detection sufficiency, and rollback authority are different
- but current Resilio still answers `why did this version win and what must I prove before an older one is authoritative again?` too diffusely
- AnonSync should therefore prefer explicit chronology contracts, concurrent-edit review, time-authority proof, older-byte republish review, and durable lineage receipts over chronology folklore

## Additional Resilio official sources emphasized in rev0343

- What if several people make changes to the same file?  
  https://help.resilio.com/hc/en-us/articles/204754209-What-if-several-people-make-changes-to-the-same-file

- "Time difference" error  
  https://help.resilio.com/hc/en-us/articles/204753599--Time-difference-error

- Using Archive for file versioning and restoring deleted files.  
  https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files

- How to touch files?  
  https://help.resilio.com/hc/en-us/articles/209606046-How-to-touch-files

- Setting Delay Time For Syncing  
  https://help.resilio.com/hc/en-us/articles/207491426-Setting-Delay-Time-For-Syncing

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- My files don't sync  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

## Revision addendum — official sources emphasized in rev0337

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about offer-family asymmetry, approval-bearing versus approval-free carriers, single-file bearer links, browser/WebUI handoff failure, landing defaults, and cleanup residue.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that not every `share` is the same family?

> where do those same current docs still show that the ordinary operator answer about `what did I issue, how open is it, how will it be claimed, where will it land, and what survives cleanup?` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Sync Share Dialog (Desktop)` article, which still says Advanced folders share by link or QR, Standard folders also expose keys, the major difference is the approval mechanism, link approval can target only new peers or all peers, and links can expire after a chosen period.
- Resilio's current `Sharing single file` article, which still says file sharing is basically a data-transfer operation, defaults to 3-day expiry, can be made non-expiring on desktop, is one-time one-way rather than live sync, allows anyone with the link to download without usage-count or device bans, requires reissue after content change, and adds `(1)` on same-name collision.
- Resilio's current `Sync doesn't start when opening Link in browser` article, which still says browser handoff can fail and that manual `+ -> Enter a key or link` is the fallback path.
- Resilio's current `Configuring WebUI` article, which still says clicked links or pasted links in the browser address bar do not work for adding shares in WebUI and that manual entry is required there.
- Resilio's current `Sync Preferences` article, which still says single-file arrival uses a separate default file location on desktop.
- Resilio's current `Sharing files (Android)` article, which still says generated single-file links are 3-day by default on Android, QR is used for receive, files land in `Downloads/SyncDownloads`, UI removal in `Downloads` removes device bytes, and `Shared links` removal is UI-only.
- Resilio's current `Sharing files (iOS)` article, which still says generated single-file links are 3-day by default on iOS, QR is used for receive, downloaded files appear in `Downloads`, deleting them there removes bytes from the device, while transfer history can still remain.
- Resilio's current `Power user preferences` article, which still keeps `keep_expired_transfer_days` and `keep_expired_transfer_num` as separate retention controls for file-send transfers.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that offer family, approval posture, landing path, and cleanup residue are materially different
- but current Resilio still answers `what did I actually hand out and what does cleanup now mean?` too diffusely
- AnonSync should therefore prefer explicit offer-family contracts, bearer-capability review, acceptance-lane review, landing/residue review, and durable lineage receipts over share-verb folklore

## Additional Resilio official sources emphasized in rev0337

- Sync Share Dialog (Desktop).  
  https://help.resilio.com/hc/en-us/articles/204790709-Sync-Share-Dialog-Desktop

- Sharing single file.  
  https://help.resilio.com/hc/en-us/articles/115000401010-Sharing-single-file

- Sync doesn't start when opening Link in browser.  
  https://help.resilio.com/hc/en-us/articles/204753649-Sync-doesn-t-start-when-opening-Link-in-browser

- Configuring WebUI.  
  https://help.resilio.com/hc/en-us/articles/115001184490-Configuring-WebUI

- Sync Preferences.  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Sharing files (Android).  
  https://help.resilio.com/hc/en-us/articles/115000409690-Sharing-files-Android

- Sharing files (iOS).  
  https://help.resilio.com/hc/en-us/articles/115001717390-Sharing-files-iOS

- Power user preferences.  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

## Revision addendum — official sources emphasized in rev0336

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about support-lane entitlement, debug-capture activation, local rotation budgets, profiler traces, crash artifacts, mobile hidden-log rituals, and cleanup residue.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that diagnostics are not one thing?

> where do those same current docs still show that the ordinary operator answer about `what am I collecting now, who can receive it, and what remains local afterward?` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Collecting debug logs manually` article, which still says direct technical support is available only to Resilio Sync Business customers, Sync v3 direct technical support is unavailable, debug logging can be enabled from settings or by `debug.txt`, restart is recommended, at least 15 minutes of collection are needed, logs are `sync.log` plus rotated zip files, storage paths vary by platform and service user, and manual attachments above 20 MB need a larger upload link.
- Resilio's current `Collecting debug logs automatically` article, which still says staffed technical support is Business-only, Sync v3 is self-serve, restart is recommended, 15 minutes of collection after reproduction are needed, and the in-product send path requires `Include logs` / add-on prompts plus time for transfer.
- Resilio's current `Increasing Debug Log size` article, which still says `log_size` defaults to 100 MB, rotates `sync.log` into `sync.log.old`, can keep up to `log_size * 2` locally, and cannot be adjusted on mobile platforms.
- Resilio's current `Power user preferences` article, which still keeps `send_statistics`, `log_size`, `log_ttl`, and `profiler_enabled` separate and still says profiler data is stored as `profiler.dat`, rotated every 10 minutes, and requires restart to activate.
- Resilio's current `Collecting crash reports, mini-dumps and core dumps` article, which still treats crash reports, minidumps, and core dumps as different artifact families with different paths by platform and Windows service user.
- Resilio's current `Collect debug logs on mobiles` article, which still says mobile capture requires debug logging, 15 minutes of collection, `SNC.DBG.LOGS`, and retrieval from hidden `.synclogs` storage.
- Resilio's current `Settings on mobile platforms` article, which still says Android `Cleanup` clears residual files as well as current debug logs and that mobile settings expose `Contact support` separately from general settings.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that diagnostics, support lanes, and cleanup residue are real and different
- but current Resilio still answers `what evidence do I really have and where can it honestly go?` too diffusely
- AnonSync should therefore prefer explicit diagnostic-lane contracts, debug-capture review, crash/profiler custody pages, external-support-lane proof, and durable lineage receipts over support-article ritual

## Additional Resilio official sources emphasized in rev0336

- Collecting debug logs manually.  
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

- Collecting debug logs automatically.  
  https://help.resilio.com/hc/en-us/articles/360019430539-Collecting-debug-logs-automatically

- Increasing Debug Log size.  
  https://help.resilio.com/hc/en-us/articles/205450145-Increasing-Debug-Log-size

- Power user preferences.  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Collecting crash reports, mini-dumps and core dumps.  
  https://help.resilio.com/hc/en-us/articles/206214615-Collecting-crash-reports-mini-dumps-and-core-dumps

- Collect debug logs on mobiles.  
  https://help.resilio.com/hc/en-us/articles/38269346960531-Collect-debug-logs-on-mobiles

- Settings on mobile platforms.  
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

## Revision addendum — official sources emphasized in rev0331

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about Archive provenance, restore authority, retention ceilings, platform visibility, and hidden survivor residue.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `Archive` is not one thing?

> where do those same current docs still show that the ordinary operator answer about `what do these archived bytes prove and can this seat really restore them?` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Using Archive for file versioning and restoring deleted files` article, which still says Archive stores older or deleted copies on other peers when a peer updates or deletes a file; defaults to 30 days on desktops and 1 day on mobiles; is manual-restore only; is not accessible on iOS; does not work on Android shares located on SD cards; depends on Sync still running during restore; and exposes `sync_trash_ttl` plus `max_file_size_for_versioning` as real coverage limits.
- Resilio's current `What is '.sync' folder, and StreamsList, IgnoreList and Archive inside?` article, which still says every synced folder gets a hidden `.sync` folder and that Archive inside it stores old versions of files deleted or modified on other devices.
- Resilio's current `Encrypted folders` article, which still says encrypted nodes have Archive but cannot restore deleted files back into the swarm because they follow deleted authoritative state and are read-only.
- Resilio's current `Power user preferences` article, which still says `sync_trash_ttl` and `max_file_size_for_versioning` are live settings that materially change history retention coverage.
- Resilio's current `Running Sync in configuration mode` article, which still says per-folder `use_sync_trash` is an authored config value.
- Resilio's current `How to uninstall Sync?` article, which still says uninstall does not remove hidden archived files inside `.sync` folders.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that Archive is a real witness-and-salvage object with provenance, retention, and authority cliffs
- but current Resilio still answers `what can I honestly recover from Archive here?` too diffusely
- AnonSync should therefore prefer explicit archive contracts, restore review, retention/visibility review, archive salvage proof, and durable lineage receipts over hidden-history folklore

## Additional Resilio official sources emphasized in rev0331

- Using Archive for file versioning and restoring deleted files.  
  https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files

- What is '.sync' folder, and StreamsList, IgnoreList and Archive inside?  
  https://help.resilio.com/hc/en-us/articles/206217185-What-is-sync-folder-and-StreamsList-IgnoreList-and-Archive-inside

- Encrypted folders  
  https://help.resilio.com/hc/en-us/articles/207370466-Encrypted-folders

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- How to uninstall Sync?  
  https://help.resilio.com/hc/en-us/articles/204775029-How-to-uninstall-Sync

## Revision addendum — official sources emphasized in rev0328

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about pause semantics, scheduler zero-speed windows, Android auto-sleep and battery saver, mobile-data policy, background-priority loss, file-class delay, and queue priority.
The new questions were:

> where do current official docs most clearly show that `paused` is not the same thing as `nothing changes`?

> where do those same current docs still show that the ordinary operator answer about `will this move now, and if not, why not?` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `How to pause syncing` article, which still says pause stops only bits downloads/uploads while zero-sized files, deletions, rescans, and indexing may still proceed.
- Resilio's current `Running Sync on schedule` article, which still says scheduled `Paused` windows zero out upload/download speed but still allow zero-sized files, deletions, rescans, and indexing, and can still allow upload to non-paused peers.
- Resilio's current `Sync Preferences` article, which still exposes separate global pause/resume and scheduler controls instead of one unified eligibility object.
- Resilio's current `Configuring Auto Sleep & Battery Saver (Android)` article, which still says Auto Sleep can turn the core actually off and later wake to check for changes, while Battery Saver can force Sync to stop below a chosen charge threshold.
- Resilio's current `Settings on mobile platforms` article, which still says `Use mobile data` is a device-level gate and that disabling Android notifications can lower background priority enough that Sync may stop working in the background.
- Resilio's current `Setting Delay Time For Syncing` article, which still says selected file classes can be held for delayed publication and only apply after editing a JSON config plus restart.
- Resilio's current `File download priority` article, which still says downloads can be prioritized by size or modification time, lower-priority downloads can be suspended, active queue behavior has limits, and visible queue order may differ from actual priority order.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that movement eligibility, wake cadence, and queue/timing behavior are materially different
- but current Resilio still answers `why is nothing moving right now?` too diffusely
- AnonSync should therefore prefer explicit eligibility contracts, mobility/power review, paused-but-still-mutating explanation, eligibility proof, and durable lineage receipts over pause folklore

## Additional Resilio official sources emphasized in rev0328

- How to pause syncing  
  https://help.resilio.com/hc/en-us/articles/206217325-How-to-pause-syncing

- Running Sync on schedule  
  https://help.resilio.com/hc/en-us/articles/210783266-Running-Sync-on-schedule

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Configuring Auto Sleep & Battery Saver (Android)  
  https://help.resilio.com/hc/en-us/articles/204762699-Configuring-Auto-Sleep-Battery-Saver-Android

- Settings on mobile platforms  
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- Setting Delay Time For Syncing  
  https://help.resilio.com/hc/en-us/articles/207491426-Setting-Delay-Time-For-Syncing

- File download priority  
  https://help.resilio.com/hc/en-us/articles/42328167759251-File-download-priority

## Revision addendum — official sources emphasized in rev0327

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about Selective Sync, RSLS placeholders, hydration scope, local reversion semantics, ghost-file demand failure, and policy-shaped delete behavior.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `visible` is not the same as `has bytes locally`?

> where do those same current docs still show that the ordinary operator answer about `can I fetch this later, what does remove mean, and do any peers still have the bytes?` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Selective Sync` article, which still says the mode can be chosen at connect time, after connect, and as the linked-device default; that if the toggle is on a new connection receives placeholders rather than full contents; that turning Selective Sync on for linked devices makes new files arrive as placeholders while current ones remain as they are; and that removing a Selective Sync share removes its placeholders from the local filesystem.
- Resilio's current `What Is an RSLS File?` article, which still says placeholders are zero-byte stand-ins; that double-click or `Sync to this device` hydrates files; that subtree hydration causes later files added there to auto-download; that `Remove from this device` reverts local copies to placeholders; that delete on a placeholder with write access can remove the file from all peers; and that if all peers revert to placeholders there may be no actual file left anywhere.
- Resilio's current `Synchronization Modes` article, which still says placeholder visibility is not full sync, that fetching requires at least one peer with the real bytes online, and that deleting a previously synced file in Selective Sync reverts it to a placeholder unless a mesh-wide delete action is chosen.
- Resilio's current `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time` article, which still says Selective Sync meshes can advertise files whose source bytes disappear before later fetch, yielding the ghost-file class.
- Resilio's current `Selective Sync (Mobile)` article, which still says mobile placeholder mode represents files with lightweight entries and requires explicit taps to fetch them.
- Resilio's current `Power user preferences` article, which still says policy can disable `Remove from all devices` and can force placeholder recreation on removal.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that placeholder-backed sync has materially different presence classes
- but current Resilio still answers `what do I really have here and what happens if I clear it?` too diffusely
- AnonSync should therefore prefer explicit materialization contracts, hydration review, local residency review, source-byte witness watch, and durable lineage receipts over placeholder folklore

## Additional Resilio official sources emphasized in rev0327

- Selective Sync  
  https://help.resilio.com/hc/en-us/articles/205458095-Selective-Sync

- What Is an RSLS File?  
  https://help.resilio.com/hc/en-us/articles/206115384-What-Is-an-RSLS-File

- Synchronization Modes  
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- Cannot download files / These files cannot be downloaded as there are no source peers online for too long time.  
  https://help.resilio.com/hc/en-us/articles/360010899719-Cannot-download-files-These-files-cannot-be-downloaded-as-there-are-no-source-peers-online-for-too-long-time

- Selective Sync (Mobile)  
  https://help.resilio.com/hc/en-us/articles/206217315-Selective-Sync-Mobile

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

## Revision addendum — official sources emphasized in rev0326

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about maintenance-health warnings, repair ladders, salvage-before-destruction obligations, and the difference between degraded operation and true suspension.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `not syncing` is really several different health classes?

> where do those same current docs still show that the ordinary operator answer about `which repair rung is justified, and what must be salvaged first?` depends on several KB articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Some internal tasks are taking time to complete` article, which still says hidden work may be intermittent and self-recovering rather than a truly stuck runtime, while also naming hashing, tree merge, dedup-copy, scanning, transfer, and disk-write phases.
- Resilio's current `Agent run out of system notify watchers` article, which still says watcher exhaustion degrades change detection into manual or periodic rescans and documents Linux inotify budget changes.
- Resilio's current `Locked files` article, which still says external applications can block transfer, exposes the affected paths, but admits Sync cannot identify the locking application.
- Resilio's current `Database error` article, which still says only the affected folder is suspended and documents a repair ladder from restart to disconnect/reconnect of the same destination to re-add across peers.
- Resilio's current `Service files missing / Cannot identify destination folder` article, which still says `.sync` loss suspends the folder, warns about same-folder/two-instance corruption, and explicitly asks operators to check archive value before deleting `.sync` and recreating the instance.
- Resilio's current `Out of memory` article, which still says Sync keeps the whole tree and deleted operations in memory/database state and that the only way to reduce RAM is destructive remove-and-share-again of the biggest folders.
- Resilio's current `My files don't sync` article, which still fans `not syncing` out into peer disconnect, ignore drift, xattrs, locks, read-only overwrite posture, permissions, encoding/path ceilings, tree-merge limits, filesystem damage, notification loss, free-space pressure, partial files, and time skew.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that maintenance health is multi-class and repair-rung-sensitive
- but current Resilio still answers `what is wrong, what is the least-destructive honest next step, and what must I salvage first?` too diffusely
- AnonSync should therefore prefer explicit health-warning contracts, triage review, repair-rung review, health proof, and durable lineage receipts over warning-row folklore

## Additional Resilio official sources emphasized in rev0326

- Some internal tasks are taking time to complete  
  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete

- Agent run out of system notify watchers. Updated files will be uploaded only after periodic folder rescan  
  https://help.resilio.com/hc/en-us/articles/360015593120-Agent-run-out-of-system-notify-watchers-Updated-files-will-be-uploaded-only-after-periodic-folder-rescan

- Locked files  
  https://help.resilio.com/hc/en-us/articles/205504549-Locked-files

- Database error  
  https://help.resilio.com/hc/en-us/articles/204753659-Database-error

- Service files missing / Cannot identify destination folder  
  https://help.resilio.com/hc/en-us/articles/205450225-Service-files-missing-Cannot-identify-destination-folder

- Out of memory  
  https://help.resilio.com/hc/en-us/articles/209724663-Out-of-memory

- My files don't sync  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

## Revision addendum — official sources emphasized in rev0324

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about portable naming, local-only rename scope, UI-only custom naming, archive-assisted rename reuse, and alias-edge support limits.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `name` is really several different truths?

> where do those same current docs still show that the ordinary operator answer about `what changed, who sees it, and can every target carry it?` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Conflict files in Sync` article, which still says conflicts can arise when names differ only by letter case or encoding, warns not to simply delete `.Conflict` files because they correspond to real remote entries, and frames cleanup around preserving one healthy copy.
- Resilio's current `Unsupported asterisk (*) characters at the end of file/folder names` article, which still says certain trailing-asterisk names are unsupported and can be interpreted as system data, causing errors or sync disruption.
- Resilio's current `My files don't sync` article, which still says Sync expects UTF-8 filenames and lists platform-dependent path-length ceilings.
- Resilio's current `Can I move or rename a syncing folder?` article, which still says renaming a syncing folder affects only the local device and that moves across partitions on Windows or Mac require disconnect/reconnect rather than ordinary move continuity.
- Resilio's current `Setting custom name for sync shares` article, which still says a custom share name changes UI presentation only, does not rename the on-disk folder, and does not propagate to other peers.
- Resilio's current `What happens when file is renamed` article, which still says remote rename reuse depends on Archive because Sync checks for a matching hash there before avoiding retransmission.
- Resilio's current `Soft links, hard links and symbolic links` article, which still says Windows link-like entries are unsupported while on Unix symbolic links can be synced as links without syncing their target folders unless separately added.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that portable-name truth is multi-plane and target-shaped
- but current Resilio still answers `what name changed and can every target actually carry it?` too diffusely
- AnonSync should therefore prefer explicit portable-name contracts, canonical-portability review, name-plane propagation review, rename-scope proof, and durable lineage receipts over conflict/troubleshooting/naming folklore

## Additional Resilio official sources emphasized in rev0324

- Conflict files in Sync  
  https://help.resilio.com/hc/en-us/articles/204753629-Conflict-files-in-Sync

- Unsupported asterisk (*) characters at the end of file/folder names  
  https://help.resilio.com/hc/en-us/articles/206214715-Unsupported-asterisk-characters-at-the-end-of-file-folder-names

- My files don't sync  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Can I move or rename a syncing folder?  
  https://help.resilio.com/hc/en-us/articles/205450655-Can-I-move-or-rename-a-syncing-folder

- Setting custom name for sync shares  
  https://help.resilio.com/hc/en-us/articles/360011865879-Setting-custom-name-for-sync-shares

- What happens when file is renamed  
  https://help.resilio.com/hc/en-us/articles/209606526-What-happens-when-file-is-renamed

- Soft links, hard links and symbolic links  
  https://help.resilio.com/hc/en-us/articles/205504529-Soft-links-hard-links-and-symbolic-links

## Revision addendum — official sources emphasized in rev0323

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about installer trust prompts, host mutation scope, Finder/Explorer shell-extension activation, command-line install distinctions, and uninstall incompleteness.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `installed` is not the same thing as `trusted and host-integrated`?

> where do those same current docs still show that the ordinary operator answer about `are shell affordances live, and is removal actually clean?` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Windows Defender SmartScreen blocks Resilio Sync installer` article, which still says SmartScreen may block installation because a new code-signing certificate lacks enough reputation and may require `Run anyway` or file `Unblock`.
- Resilio's current `How to Silently Install Resilio Sync` article, which still says silent Windows install is not MSI-based, still triggers UAC, and when accepted creates Program Files contents, icons, startup menu items, Explorer context-menu items, and registry entries; and that full silent removal is not possible and may still require manual cleanup and reboot because shell DLLs remain loaded.
- Resilio's current `No Sync icons in the file browser/no Sync-related items in the context menu on Mac/Windows` article, which still says shell surfaces depend on Selective Sync, NTFS on Windows, extension/DLL presence and registration, Finder/Explorer relaunch, explicit Finder-extension enablement, and can conflict with other apps.
- Resilio's current `How to uninstall Sync?` article, which still says uninstall does not delete previously shared folders, that service-storage cleanup differs by runtime principal, and that hidden `.sync/Archive` residue may need manual removal after uninstall.
- Resilio's current `Is there a Command Line Interface (CLI) for Resilio Sync on Windows?` article, which still distinguishes install, no-install, silent start, minimized start, and loopback-only WebUI launch, reinforcing that launch mode and host integration are different truths.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that trust prompts, shell affordances, and uninstall survivors are real host facts
- but current Resilio still answers `is this trusted, integrated, and actually gone?` too diffusely
- AnonSync should therefore prefer explicit host-integration contracts, installer-trust review, shell-activation proof, uninstall-clearance review, and durable receipts over installer/troubleshooting folklore

## Additional Resilio official sources emphasized in rev0323

- Windows Defender SmartScreen blocks Resilio Sync installer  
  https://help.resilio.com/hc/en-us/articles/360014486120-Windows-Defender-SmartScreen-blocks-Resilio-Sync-installer

- How to Silently Install Resilio Sync  
  https://help.resilio.com/hc/en-us/articles/205505969-How-to-Silently-Install-Resilio-Sync

- No Sync icons in the file browser/no Sync-related items in the context menu on Mac/Windows  
  https://help.resilio.com/hc/en-us/articles/206214625-No-Sync-icons-in-the-file-browser-no-Sync-related-items-in-the-context-menu-on-Mac-Windows

- How to uninstall Sync?  
  https://help.resilio.com/hc/en-us/articles/204775029-How-to-uninstall-Sync

- Is there a Command Line Interface (CLI) for Resilio Sync on Windows?  
  https://help.resilio.com/hc/en-us/articles/205506359-Is-there-a-Command-Line-Interface-CLI-for-Resilio-Sync-on-Windows

## Revision addendum — official sources emphasized in rev0321

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about Linux same-host multi-instance support, explicit storage/identity roots, runtime-principal differences, update-path continuity, and destructive same-path collision.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that more than one runtime on one host is possible but not harmless by default?

> where do those same current docs still show that the ordinary operator answer about `what must be distinct, what preserves continuity, and what can corrupt the first instance?` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Guide to Linux, and Sync peculiarities` article, which still says Linux can run multiple instances, that second and later instances require manual port assignment, that `--storage` defines where settings live and otherwise `.sync` storage is created in the current directory, that `--identity` and `--license` also depend on explicit storage rooting, and that `--webui.listen` can widen control audience from loopback to LAN.
- Resilio's current `Running Sync in configuration mode` article, which still says config mode applies pre-configured parameters at start, that a non-default `storage_path` creates new settings there, and that a listening port value of `0` allocates a random port.
- Resilio's current `Installing Sync package on Linux` article, which still says the default service runs under `rslsync` with minimum privileges and separately documents an alternative current-user service mode.
- Resilio's current `Updating installation to Resilio Sync v3` article, which still says non-default `/config` or `/storage` launches must be restarted with the same parameters and the same user to preserve the same storage folder and configuration.
- Resilio's current `Service files missing / Cannot identify destination folder` article, which still says that adding the same folder to Sync A and then Sync B on the same computer, or reusing one external disk as storage for two instances, can corrupt the former instance's internal files and make further synchronization impossible.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that same-host multi-instance runtime is real and that hidden state collisions are dangerous
- but current Resilio still answers `is this second runtime actually safe?` too diffusely
- AnonSync should therefore prefer explicit instance-namespace contracts, second-instance bringup review, same-path collision warnings, external-world handoff review, and durable lineage receipts over Linux-note plus repair folklore

## Additional Resilio official sources emphasized in rev0321

- Guide to Linux, and Sync peculiarities  
  https://help.resilio.com/hc/en-us/articles/204762449-Guide-to-Linux-and-Sync-peculiarities

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Installing Sync package on Linux  
  https://help.resilio.com/hc/en-us/articles/206178924-Installing-Sync-package-on-Linux

- Updating installation to Resilio Sync v3  
  https://help.resilio.com/hc/en-us/articles/31194252837779-Updating-installation-to-Resilio-Sync-v3

- Service files missing / Cannot identify destination folder  
  https://help.resilio.com/hc/en-us/articles/205450225-Service-files-missing-Cannot-identify-destination-folder

## Revision addendum — official sources emphasized in rev0320

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about configuration-mode path admission, root ceilings, picker visibility, config-authored subject sets, and storage worlds.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that not every path on disk is equally admissible as a sync subject?

> where do those same current docs still show that the ordinary operator answer about `can I add this path, why is it missing from the picker, and did config replace my subject set?` depends on configuration commentary instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Running Sync in configuration mode` article, which still says config mode applies pre-configured parameters at program start; that a non-default `storage_path` creates new settings there; that Linux `directory_root_policy` supports `all` and `belowroot`; that `belowroot` denies direct `adddir` attempts within `directory_root` while still allowing descendants; that `dir_whitelist` defines which directories can be used for sync shares and hides others from the folder picker; that config mode can set up only Standard folders, not Advanced; and that config-defined shared folders disable WebUI and override folders previously added from WebUI.
- Resilio's current `Sync Storage folder` article, which still says the storage folder contains current configuration, auxiliary settings files, and shares' database state, and that default desktop storage location changes via config mode.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that directory admission is policy-shaped
- but current Resilio still answers `why can or can't I add this folder?` too diffusely
- AnonSync should therefore prefer explicit directory-admission contracts, root-ceiling review, picker-visibility authority, config-authored roster review, and durable receipts over configuration folklore

## Additional Resilio official sources emphasized in rev0320

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Sync Storage folder  
  https://help.resilio.com/hc/en-us/articles/206664690-Sync-Storage-folder

## Revision addendum — official sources emphasized in rev0319

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about pre-login launch on macOS and headless WebUI control.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that running before login on macOS is a different runtime world rather than mere backgrounding?

> where do those same current docs still show that the ordinary operator answer about `principal, storage home, control audience, file-creation contract, and lost parity` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Launching Sync on Mac without user logged in` article, which still says the ordinary app starts when the user logs in under the current user account; that pre-login launch requires `launchd`, root permissions, and a dedicated `resiliosync` user; that the sample config uses `use_gui: false`, a separate `storage_path`, `listen : 0.0.0.0:8888`, and explicit login/password; that the launchd recipe sets `RunAtLoad`, `KeepAlive`, `UserName`, and `Umask 2`; that future local files inside synced folders must preserve the expected group-write posture or Sync can stop syncing them; and that the recipe adds the placeholder caveat `"enable_placeholders": false`.
- Resilio's current `Configuring WebUI` article, which still says app-install WebUI is configuration-file driven, that `0.0.0.0` widens reach to the LAN, that HTTP is default unless `force_https` is configured, and that clicking a share link in WebUI does not work and must be replaced with manual `Enter a key or link`.
- Resilio's current `Does Sync work in background?` article, which still says ordinary desktop background behavior on macOS can simply mean the minimized app, preserving the contrast between hidden interactive runtime and pre-login headless runtime.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for being candid that pre-login mode is materially different from ordinary background use
- but current Resilio still answers `what exactly changed?` too diffusely
- AnonSync should therefore prefer explicit launch-class contracts, headless-launch review, group-write proof, caveat pages, and durable lineage receipts over setup archaeology

## Additional Resilio official sources emphasized in rev0319

- Launching Sync on Mac without user logged in  
  https://help.resilio.com/hc/en-us/articles/207293730-Launching-Sync-on-Mac-without-user-logged-in

- Configuring WebUI  
  https://help.resilio.com/hc/en-us/articles/115001184490-Configuring-WebUI

- Does Sync work in background?  
  https://help.resilio.com/hc/en-us/articles/206816823-Does-Sync-work-in-background

## Revision addendum — discovery bootstrap authority, fallback envelope, and relay inevitability after rev0317

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about remote bootstrap catalog fetch, tracker/relay discovery lanes, warning semantics, proxy asymmetry, and relay fallback cost.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that connectivity depends on a bootstrap authority and several distinct discovery lanes rather than one generic `network` state?

> where do those same current docs still show that the ordinary operator answer about `who currently defines discovery infrastructure, what fallback remains, and whether relay is inevitable for this pair?` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Peers aren't connecting` article, which still says Sync learns tracker and relay addresses from `config.resilio.com/sync.conf`, that blocked tracker and blocked relay are separate problems, and that predefined hosts are the fallback when tracker use is not possible.
- Resilio's current `What ports and protocols are used by Sync?` article, which still separates bootstrap catalog fetch, tracker contact, direct peer dialing, relay fallback, LAN multicast, and port mapping.
- Resilio's current `Core warnings` article, which still says `No tracker connection` only blocks syncing when relay, LAN broadcasts, or predefined hosts are also unavailable.
- Resilio's current `Sync Preferences` article, which still says proxy servers prohibit incoming connections and that two proxied peers can talk only via relay while one proxied peer can still dial outward directly.
- Resilio's current `What is a Relay Server?` article, which still says relay is used when direct connection is not possible and that relayed transfer is slower than direct transfer.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that discovery is multi-lane and asymmetric
- but current Resilio still answers `what connectivity authority do I actually have right now?` too diffusely
- AnonSync should therefore prefer first-class bootstrap authority, outage review, fallback proof, pairwise reachability review, and durable receipts over connectivity folklore

## Additional Resilio official sources emphasized in rev0318

- Peers aren't connecting  
  https://help.resilio.com/hc/en-us/articles/205450205-Peers-aren-t-connecting

- What ports and protocols are used by Sync?  
  https://help.resilio.com/hc/en-us/articles/204754759-What-ports-and-protocols-are-used-by-Sync

- Core warnings  
  https://help.resilio.com/hc/en-us/articles/360001217950-Core-warnings

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- What is a Relay Server?  
  https://help.resilio.com/hc/en-us/articles/204754779-What-is-a-Relay-Server

## Revision addendum — nested overlap topology, bridge-host propagation, and seed-horizon fragmentation after rev0314

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was Resilio's current official FAQ entry on sharing a nested folder separately.
The new questions were:

> where do current official docs most clearly show that parent/child overlap creates two sync subjects rather than one hierarchy with a narrower audience?

> where do those same docs still show that the ordinary operator answer about direct seeding, carried edits, and duplicate work depends on special-case documentation instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Is it possible to share a nested folder separately?` article, which still says both parent and child must have `Read & Write` or `Owner`, both must have `Selective Sync` disabled, the overlapping host performs extra indexing/rescanning, parent-only peers do not seed child-only peers directly, and child-only changes can still reach parent-only peers through the overlapping host.

That source was enough for this tranche because the product-contract point is already concentrated in one official current document.
The problem is not lack of candor.
The problem is that the truth is still encoded as FAQ knowledge instead of an explicit overlap-topology interface family.

## Revision addendum — resource budget, starvation truth, and bottleneck proof after rev0313

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about global send/receive limits, scheduler pause semantics, power-user resource knobs, download-priority queue behavior, hidden internal work, and memory-scale pressure.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that throughput is governed by multiple independent budgets?

> where do those same current docs still show that the ordinary operator answer about `what is slow, why, and who is paying for that slowdown?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Sync Preferences` article, which still says receiving/sending limits apply to internet traffic by default and require `rate_limit_local_peers` to govern LAN too.
- Resilio's current `Running Sync on schedule` article, which still says scheduled `Paused` zeros upload/download rates while zero-sized files, deletions, rescans, and indexing continue and paused peers can still upload to non-paused peers.
- Resilio's current `Power user preferences` article, which still exposes `disk_low_priority`, `disk_worker_per_job`, `worker_threads_count`, `rate_limit_local_peers`, `free_space_warning_threashold`, and related knobs that materially alter contention and fairness.
- Resilio's current `File download priority` article, which still says prioritization only applies to the active queue up to 50,000 files, can suspend lower-priority downloads, still has internal exceptions, and may not match visible queue ordering.
- Resilio's current `Some internal tasks are taking time to complete` article, which still says hidden read/hash/merge/write work can consume resources and delay visible progress.
- Resilio's current `Out of memory` article, which still says the whole tree and deleted entries remain in memory/database and that true RAM reduction may require removing a large folder from Sync and sharing it again.

## Additional Resilio official sources emphasized in rev0314

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Running Sync on schedule  
  https://help.resilio.com/hc/en-us/articles/210783266-Running-Sync-on-schedule

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- File download priority  
  https://help.resilio.com/hc/en-us/articles/42328167759251-File-download-priority

- Some internal tasks are taking time to complete  
  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete

- Out of memory  
  https://help.resilio.com/hc/en-us/articles/209724663-Out-of-memory

## Revision addendum — raw-state cloning, successor import, and seat rebirth proof after rev0312

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about unsupported cloning, storage-folder contents, per-install certificates, and identity replacement.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that copying Sync state is dangerous?

> where do those same current docs still show that the ordinary operator answer about `replacement versus duplicate versus backup` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Cloning Sync` article, which still says cloning a Sync instance by plain copy, drive cloners, or Time Machine style copying is not supported and may create two or more instances that do not transfer to one another and can show other strange behavior.
- Resilio's current `Sync Storage folder` article, which still says the storage folder keeps current configuration, auxiliary settings files, and shares' database state.
- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says each installation gets a unique digital certificate and fingerprint even when two independent installs share the same identity name.
- Resilio's current `Can I change the name of my Sync identity?` article, which still says changing identity name requires unlinking and creating a new identity so that a new certificate is generated.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for telling operators that copied state is dangerous rather than pretending cloning is ordinary
- but current Resilio still answers `how do I replace a machine safely?` too bluntly
- AnonSync should therefore prefer reviewed successor capsules, explicit state-adoption review, duplicate-seat blocking, and durable activation receipts over opaque clone folklore

## Revision addendum — invocation profile, launch switches, and runtime-world proof after rev0311

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about Windows CLI launch switches, Linux/headless startup arguments, config-mode storage authority, service storage worlds, loopback-vs-LAN WebUI exposure, and update continuity for non-default launches.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that launch flags and startup arguments materially change runtime world, state storage, visibility, and control exposure?

> where do those same current docs still show that the ordinary operator answer about `what world did I just start?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Is there a Command Line Interface (CLI) for Resilio Sync on Windows?` article, which still says `/config`, `/webui`, `/storage`, `/noinstall`, `/S`, and `/minimized` materially change startup behavior.
- Resilio's current `Guide to Linux, and Sync peculiarities` article, which still says `--storage` controls where settings, identity, and license live; that without it `.sync` is created in the current directory; that `--identity` and `--license` also fall back to that storage unless redirected; and that `--webui.listen` defaults to `127.0.0.1`, can widen to all interfaces, and can cause shutdown if pinned to an unavailable interface.
- Resilio's current `Running Sync in configuration mode` article, which still says a non-default `storage_path` creates settings there and that service config mode works only when the config file is placed in the service storage.
- Resilio's current `Sync Service Troubleshooting on Windows` article, which still says switching to Local System yields a different storage folder, an empty-looking roster, and a re-add / re-share burden; and that service WebUI is loopback-only by default unless reconfigured.
- Resilio's current `Updating installation to Resilio Sync v3` article, which still says non-default `/config` or `/storage` launches and Linux binary installs preserve configuration only when relaunched with the same parameters and same user.

## Additional Resilio official sources emphasized in rev0312

- Is there a Command Line Interface (CLI) for Resilio Sync on Windows?  
  https://help.resilio.com/hc/en-us/articles/205506359-Is-there-a-Command-Line-Interface-CLI-for-Resilio-Sync-on-Windows

- Guide to Linux, and Sync peculiarities  
  https://help.resilio.com/hc/en-us/articles/204762449-Guide-to-Linux-and-Sync-peculiarities

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Sync Service Troubleshooting on Windows  
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

- Updating installation to Resilio Sync v3  
  https://help.resilio.com/hc/en-us/articles/31194252837779-Updating-installation-to-Resilio-Sync-v3

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

## Revision addendum — completion horizons, freshness proof, and hidden-lag truth after rev0304

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about desktop status meaning, peer-count semantics, background/internal tasks, change-detection latency, and old but still revealing UI-observability lineage.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `green`, `X of Y peers`, hidden background work, and change-detection timing are materially different ingredients of completion truth?

> where do those same current docs still show that the ordinary operator answer about `is this actually complete and fresh, relative to whom?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Sync Main View (Desktop)` article, which still says a green checkmark means files are synced with all connected peers, and that `X of Y peers` includes offline peers while peers offline for 7 days can be disconnected according to a power-user setting.
- Resilio's current `My files don't sync` article, which still tells operators to inspect peer list, status column, history, and upload/download queue separately when not all files are synced.
- Resilio's current `Some internal tasks are taking time to complete` article, which still says hidden work such as hashing, scanning, merging, block-checking, dedup-copy, reading, and writing can continue and can delay visible completion.
- Resilio's current `How soon does synchronization start?` article, which still says change discovery depends on filesystem notifications, periodic rescan every 600 seconds by default, optional manual rescan, and storage classes where notifications may not work.
- Resilio's current `Power user preferences` article, which still publishes `peer_expiration_days` as the setting that changes when offline peers disappear from the active list.
- The long-running `Resilio Sync change log`, which still records the addition of surrogate columns such as `Last transferred` and fixes around `Date synced`, illustrating that observational hints exist but are not by themselves a proof contract.

## Additional Resilio official sources emphasized in rev0305

- Sync Main View (Desktop)  
  https://help.resilio.com/hc/en-us/articles/204755009-Sync-Main-View-Desktop

- My files don't sync  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Some internal tasks are taking time to complete  
  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete

- How soon does synchronization start?  
  https://help.resilio.com/hc/en-us/articles/204754319-How-soon-does-synchronization-start

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Resilio Sync change log  
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log

## Revision addendum — permission metadata, principal mapping, and apply-ceiling truth after rev0302

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio documentation about file-system permission synchronization, runtime-principal requirements, create-time-fixed permission policy, target identity mapping, and concrete permission-application failures.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that permission metadata is operationally real and not just decorative?

> where do those same current docs still show that the ordinary operator answer about `are permissions actually part of the truth here, and under what assumptions?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Syncing file system permissions` article, which still says Active Everywhere can synchronize NTFS and POSIX permissions; that Synchronization, Hybrid Work, and File Caching jobs fix those settings at creation time; that NTFS mode families differ materially (`Don't sync Owner`, `Sync full ACL`, `Re-apply local inherited permissions`); that Local System / local admin / Domain Admin requirements differ by mode; that non-NTFS targets may preserve NTFS permissions and only apply them later on NTFS storage; that SMB access can require extra rights; and that pre-seeded RW-to-RW merges can scramble ownership without a Reference Agent.
- Resilio's current `Connect Agent cannot set file permission` article, which still says real failures reduce to insufficient NTFS privileges or missing same-ID / same-name target mappings for POSIX application.
- Resilio's current `Synchronization Job` and `Hybrid Work Job` pages, which still keep permission-bearing profile choice in creation-time workflow rather than framing it as a trivial late toggle.

## Additional Resilio official sources emphasized in rev0303

- Syncing file system permissions  
  https://www.resilio.com/documentation/content/advanced-configuration/agents/syncing_file_system_permissions/

- Connect Agent cannot set file permission: not enough privileges or a new permission is incorrect  
  https://www.resilio.com/documentation/content/troubleshooting/error-messages/connect_agent_cannot_set_file_permission__not_enough_privileges_or_a_new_permission_is_incorrect/

- Synchronization Job  
  https://www.resilio.com/documentation/content/jobs/synchronization_job/

- Hybrid Work Job  
  https://www.resilio.com/documentation/content/jobs/hybrid_work_job/

## Revision addendum — removal verbs, placeholder deletion, hidden-device cleanup, and uninstall residue after rev0300

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about disconnecting and removing folders, disconnected-folder semantics, selective-sync placeholder removal, `Remove from this device` vs delete-for-all behavior, power-user removal guards, hidden offline devices, iOS remove-from-device semantics, and uninstall residue.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `remove` is not one thing?

> where do those same current docs still show that the ordinary operator answer about `what disappears, for whom, and what survives?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Disconnecting and Removing Folders` article, which still says disconnect affects one device, can leave the folder in the file system, removes Selective Sync placeholders locally, and reconnect can default to a different path and create an indexed sibling directory unless manually rebound.
- Resilio's current `Folder Types and Management` article, which still says disconnected folders have no local path and removing a disconnected folder removes it from linked devices.
- Resilio's current `Selective Sync` article, which still warns that removing a Selective Sync share removes all placeholders from the local file system on that device.
- Resilio's current `What Is an RSLS File?` article, which still says `Remove from this device` reverts a file or subfolder to a placeholder locally, while deleting a placeholder with Read & Write access can remove it permanently from all peers.
- Resilio's current `Power user preferences` article, which still publishes `disable_remove_from_all_devices` and `recreate_placeholders_on_removal`, and still notes that the former is ignored in Linux WebUI.
- Resilio's current `How to clear offline devices?` article, which still says hiding only removes a device from view and it can reappear if it returns online.
- Resilio's current `Sync Interface on iOS devices` article, which still says `Remove from this device` disconnects the folder only on that iOS device and removes files from that device while preserving others.
- Resilio's current `How to uninstall Sync?` article, which still says uninstall is not subject deletion, desktop uninstall can leave shared folders and `.sync/Archive` behind, and iOS uninstallation removes synced files from the device.

## Additional Resilio official sources emphasized in rev0301

- Disconnecting and Removing Folders  
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- Folder Types and Management  
  https://help.resilio.com/hc/en-us/articles/204762459-Folder-Types-and-Management

- Selective Sync  
  https://help.resilio.com/hc/en-us/articles/205458095-Selective-Sync

- What Is an RSLS File?  
  https://help.resilio.com/hc/en-us/articles/206115384-What-Is-an-RSLS-File

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- How to clear offline devices? (desktop only)  
  https://help.resilio.com/hc/en-us/articles/204762439-How-to-clear-offline-devices-desktop-only

- Sync Interface on iOS devices  
  https://help.resilio.com/hc/en-us/articles/212016726-Sync-Interface-on-iOS-devices

- How to uninstall Sync?  
  https://help.resilio.com/hc/en-us/articles/204775029-How-to-uninstall-Sync

## Revision addendum — transfer eligibility, pause semantics, and context-gating work after rev0298

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about pause semantics, scheduler zero-speed windows, auto-sleep/battery gating, device-level mobile-data rules, per-share forbidden-network rules, and background-priority caveats.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `paused`, `sleeping`, `battery stopped`, `forbidden network`, and `Wi‑Fi only waiting` are materially different transfer-eligibility truths?

> where do those same current docs still show that the ordinary operator answer about `will bytes move now, and if not, what still mutates anyway?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `How to pause syncing` article, which still says pause stops only bit transfers while zero-sized files and deletions still sync and new files are still rescanned and indexed.
- Resilio's current `Running Sync on schedule` article, which still says scheduler `Paused` sets upload/download speed to zero but zero-sized files and deletions still sync, paused peers may still upload to non-paused peers, and rescans/indexing still continue.
- Resilio's current `Configuring Auto Sleep & Battery Saver (Android)` article, which still says Auto Sleep turns the core off when idle, peers then do not see the device online, Sync wakes periodically to check for changes, and Battery Saver can force Sync to stop below a threshold.
- Resilio's current `Settings on mobile platforms` article, which still says `Use mobile data` is a device-level gate and disabling Android notifications may stop background work by lowering system priority.
- Resilio's current `Setting network interface per share` article, which still says a share can become `Stopped. Forbidden network`, in which state it will not connect to peers and new or updated files will not be detected.
- Resilio's current `Sync Preferences` article, which still exposes global pause, scheduler, and bandwidth limits as separate settings planes.
- Resilio's current `Power user preferences` article, which still publishes `free_space_warning_threashold` as another stop-syncing gate in the same operational universe.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0299

- How to pause syncing  
  https://help.resilio.com/hc/en-us/articles/206217325-How-to-pause-syncing

- Running Sync on schedule  
  https://help.resilio.com/hc/en-us/articles/210783266-Running-Sync-on-schedule

- Configuring Auto Sleep & Battery Saver (Android)  
  https://help.resilio.com/hc/en-us/articles/204762699-Configuring-Auto-Sleep-Battery-Saver-Android

- Settings on mobile platforms  
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- Setting network interface per share  
  https://help.resilio.com/hc/en-us/articles/360001411244-Setting-network-interface-per-share

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — activation latency and proof-of-effect work after rev0294

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about IgnoreList reread timing, scheduled and manual rescans, sidecar/config restart rituals, debug/profiler activation, and future-only versus retroactive effect boundaries.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that a changed rule or knob may become real immediately, after reread, after rescan, after restart, or only for future work?

> where do those same current docs still show that the ordinary operator answer about `did this merely save, become live, or actually change the world I care about?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Ignoring files in Sync (Ignore List)` article, which still says IgnoreList is reread on change or every `folder_rescan_interval` if notifications are absent, recommends restart for immediate application, and says the rule does not affect files that already synced while already-indexed structure remains passed to peers until disconnect.
- Resilio's current `How soon does synchronization start?` article, which still says filesystem notifications are fastest, scheduled rescan runs every 600 seconds and on Sync start, manual rescan exists, and `folder_rescan_interval = 0` disables rescans even upon restart.
- Resilio's current `Setting Delay Time For Syncing` article, which still places `FileDelayConfig` in the storage folder, still requires JSON edits there, still defaults listed file types to a 10-second delay, and still requires restarting Sync.
- Resilio's current `Collecting debug logs manually` article, which still says debug logging can be enabled via UI or `debug.txt`, that restart is needed to make sure it is enabled, and that capture should run for at least 15 minutes.
- Resilio's current `Power user preferences` article, which still says `profiler_enabled` requires restart and still publishes `folder_rescan_interval`, `config_refresh_interval`, and `config_save_interval` as separate timing levers.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0295

- Ignoring files in Sync (Ignore List)  
  https://help.resilio.com/hc/en-us/articles/205458165-Ignoring-files-in-Sync-Ignore-List

- How soon does synchronization start?  
  https://help.resilio.com/hc/en-us/articles/204754319-How-soon-does-synchronization-start

- Setting Delay Time For Syncing  
  https://help.resilio.com/hc/en-us/articles/207491426-Setting-Delay-Time-For-Syncing

- Collecting debug logs manually  
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — automatic ingress mutation and port-lease work after rev0293

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about listening-port semantics, UPnP/NAT-PMP auto-mapping, manual forwarding expectations, config-plane `upnp` ownership, and direct-path troubleshooting advice.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that directness can require explicit or automatic ingress work at the network edge?

> where do those same current docs still show that the ordinary operator answer about `did I just request router mutation, what inbound audience widened, and do I actually know whether the mapping is live or gone?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Sync Preferences` article, which still says the listening port is used for incoming/outgoing UDP and incoming TCP, that manual forwarding should target that same port, that `Use UPnP port mapping` makes Sync send UPnP and NAT-PMP packets to the router, and that some printers/scanners/other network equipment may mis-handle those packets and stop processing network requests.
- Resilio's current `What ports and protocols are used by Sync?` article, which still says direct connection depends on the listening port being opened and forwarded through firewalls, NATs, and routers after discovery and before relay fallback.
- Resilio's current `Running Sync in configuration mode` article, which still publishes the `upnp` field and keeps it adjacent to listening-port, proxy, WebUI, and shared-folder ownership in the startup config plane.
- Resilio's current `Download/upload speed is very slow` article, which still treats open listening port and direct port mapping as practical remedies for relay dependence.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0294

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- What ports and protocols are used by Sync?  
  https://help.resilio.com/hc/en-us/articles/204754759-What-ports-and-protocols-are-used-by-Sync

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Download/upload speed is very slow  
  https://help.resilio.com/hc/en-us/articles/205450195-Download-upload-speed-is-very-slow

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — artifact-family opacity and epoch-fork work after rev0287

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about raw key families, temporary-key links, approval/certificate flow, identity-link `M` keys, share-dialog expiry/use budgets, and key-change epoch forks.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that links, keys, ciphertext-custody artifacts, and linked-identity artifacts are materially different authority objects?

> where do those same current docs still show that the ordinary operator answer about `what exactly is this token and what fork happens if I rotate it?` depends on token internals and several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Key structure and flow` article, which still says only Standard folders use raw keys, that the first character determines materially different key types (`A`, `B`, `D`, `E`, `F`, `M`), that `F` is ciphertext-only custody, that `M` is an identity-link key, and that key changes are not distributed automatically so old-key peers continue syncing together after one peer changes key.
- Resilio's current `Link structure and flow` article, which still says the browser landing page is a carrier shell, that meaningful parameters live after `#`, that links contain a temporary key, that the claimant sends a locally generated public key, and that approval generates an X509 certificate plus signed ACL entry before access becomes live.
- Resilio's current `Sync Share Dialog (Desktop)` article, which still says keys and links differ materially because keys do not use the approval mechanism and still publishes expiry and use-budget settings during issuance.
- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says devices linked with one identity use an `M`-key path, that taking the M-key from one device can transfer identity name, fingerprint, and configured shares to another, and that linking two already-running devices can replace one certificate and remove Advanced folders from the app.
- Resilio's current `Sharing a folder locally` article, which still says local shares are neither full peers nor ordinary onward shares, that they inherit ceilings from the source share, and that some permission changes require remove-and-reshare rather than in-place mutation.

## Additional Resilio official sources emphasized in rev0288

- Key structure and flow  
  https://help.resilio.com/hc/en-us/articles/206767810-Key-structure-and-flow

- Link structure and flow  
  https://help.resilio.com/hc/en-us/articles/204754739-Link-structure-and-flow

- Sync Share Dialog (Desktop)  
  https://help.resilio.com/hc/en-us/articles/204790709-Sync-Share-Dialog-Desktop

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Sharing a folder locally  
  https://help.resilio.com/hc/en-us/articles/360011582500-Sharing-a-folder-locally

## Revision addendum — priority/residency fragmentation and guarantee-class interface work after rev0286

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about the new `File download priority` feature in `3.1.0`, sticky manual priority override behavior, Selective Sync and `.rsls` placeholder semantics, selective-share removal behavior, power-user defaults and destructive guardrails, and current ghost/no-source warnings.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that queue order, local presence, future-descendant hydration, and surviving full-copy witnesses are different truths?

> where do those same current docs still show that the ordinary operator answer about `will this become local, stay local, and how strong is that promise?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `File download priority` article, which says the feature is available in Sync `3.1.0`, allows per-share and global defaults, freezes later global inheritance for shares whose priority was manually altered, limits prioritization to the active queue, suspends lower-priority transfers for higher-priority arrivals with internal exceptions, and treats single-file sending differently.
- Resilio's current `Power user preferences` article, which still publishes `folder_defaults.transfer_priority`, `disable_remove_from_all_devices`, and `recreate_placeholders_on_removal`, and still says the first destructive-action guard is ignored in Linux WebUI.
- Resilio's current `Synchronization Modes` article, which still says placeholders represent non-local content, that syncing a subtree can later auto-download new descendants there, and that `Remove from this device` differs materially from `Remove from all devices`.
- Resilio's current `Selective Sync` article, which still says turning Selective Sync ON for a first connection yields placeholder information only, that linked-device defaults affect future arrivals, and warns that removing the Selective Sync share removes placeholders from the local filesystem.
- Resilio's current `What Is an RSLS File?` article, which still says placeholders are 0-byte files, that subfolder fetch can auto-download later descendants, and that placeholder reversion requires another full copy to still exist somewhere.
- Resilio's current `Disconnecting and Removing Folders` article, which still says disconnecting a selective-sync folder removes placeholders from that device and reconnect may propose a different default path.
- Resilio's current `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time` article, which still says some announced files are ghost files that no peer retains in full anymore.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line and records the introduction of file download priority in `3.1.0`.

## Additional Resilio official sources emphasized in rev0287

- File download priority  
  https://help.resilio.com/hc/en-us/articles/42328167759251-File-download-priority

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Synchronization Modes  
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- Selective Sync  
  https://help.resilio.com/hc/en-us/articles/205458095-Selective-Sync

- What Is an RSLS File?  
  https://help.resilio.com/hc/en-us/articles/206115384-What-Is-an-RSLS-File

- Disconnecting and Removing Folders  
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- Cannot download files / These files cannot be downloaded as there are no source peers online for too long time  
  https://help.resilio.com/hc/en-us/articles/360010899719-Cannot-download-files-These-files-cannot-be-downloaded-as-there-are-no-source-peers-online-for-too-long-time

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — dangerous service/browser control, trust bootstrap, and pre-destructive preservation after rev0285

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync and Resilio site pages about Windows service/WebUI control, Linux install modes and version compatibility, the current Sync download warnings, WebUI/browser-trust bootstrap, and Android per-share destructive controls.
The new questions were:

> where do current official Resilio materials most clearly show that browser/service control is real but the dangerous-control contract is still split across install, service, product-line, and browser-warning pages?

> where do those same current docs still show that `export first` and `overwrite later` are still too close to remembered operator ritual and too far from one owned workflow grammar?

The most load-bearing source set for this pass was:

- Resilio's current `Running Sync as a service on Windows`, which still says Sync can run as a service regardless of whether a user is logged in and that setup opens WebUI in the default browser.
- Resilio's current `Installing Sync package on Linux`, which still publishes manual, repository, and official Docker-image install paths and still separates personal `v3` from Business `v2.8.1` compatibility.
- Resilio's current `Download Sync` page, which still says Sync is for personal non-commercial use and warns NAS users not to update current Sync Business installations to `v3` because configured-share access will be lost.
- Resilio's current `Configuring WebUI` and `Browser warning "Your connection is not private"` articles, which still normalize listener binding, optional password posture, self-signed HTTPS, and browser-exception bootstrap.
- Resilio's current `Sync interface on Android`, which still exposes `Use Archive`, `Overwrite changed files`, relay, tracker, LAN search, and host overrides as ordinary per-share controls.

## Additional Resilio official sources emphasized in rev0286

- Running Sync as a service on Windows  
  https://help.resilio.com/hc/en-us/articles/207701296-Running-Sync-as-a-service-on-Windows

- Installing Sync package on Linux  
  https://help.resilio.com/hc/en-us/articles/206178924-Installing-Sync-package-on-Linux

- Download Sync  
  https://www.resilio.com/sync/download/

- Configuring WebUI  
  https://help.resilio.com/hc/en-us/articles/115001184490-Configuring-WebUI

- Browser warning "Your connection is not private"  
  https://help.resilio.com/hc/en-us/articles/4404757430291-Browser-warning-Your-connection-is-not-private

- Sync interface on Android  
  https://help.resilio.com/hc/en-us/articles/213500383-Sync-interface-on-Android

## Revision addendum — product-line split, local-web reality, trust bootstrap, and destructive contract review after rev0284

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync and Resilio site pages about the live v3 personal line, the still-supported v2.8 Business line, unsupported Business-to-v3 upgrades, Linux/WebUI defaults, self-signed browser trust warnings, and the current destructive-heal path.
The new questions were:

> where do current official Resilio materials most clearly show that the useful candor is real, but the present-day operator contract is split across product lines and bootstrap notes rather than one owned interface grammar?

> where do those same current docs still show that `overwrite changed files` is too close to settings and too far from a first-class reviewed destructive operation?

The most load-bearing source set for this pass was:

- Resilio's current `Resilio Sync 3.0 change log`, which currently runs through `3.1.2.1076 (31/Oct/2025)`.
- Resilio's current `Resilio Sync: supported platforms and system requirements`, which still presents both a `Sync v3` section and a `Sync v2` section in the same support article.
- Resilio's current `Download Sync` page, which says Sync is for personal non-commercial purposes and warns NAS users not to update current Sync Business installations to Sync v3 because access to configured shares will be lost.
- Resilio's current `New Opportunities Ahead as Sync Business Transitions` page, which says no new Sync Business trials or purchases are offered, that existing licenses remain supported, and that `2.8` is the final upgrade available in the account portal for Sync Business.
- Resilio's current `Important before updating to Resilio Sync 3.0.0` and `Updating installation to Resilio Sync v3` pages, which both say Sync Business cannot be updated to v3.
- Resilio's current `Configuring WebUI`, `Running Sync in configuration mode`, and `Browser warning "Your connection is not private"` articles, which together show local web/service operation, listener binding, and self-signed browser-trust exception paths.
- Resilio's current `Is one-way synchronization possible?`, `Folder Preferences`, `Using Archive for file versioning and restoring deleted files`, `Encrypted folders`, `Power user preferences`, `Sync Interface on iOS devices`, and `Sync interface on Android` pages, which still spread one destructive-heal answer across several surfaces.

## Additional Resilio official sources emphasized in rev0285

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Resilio Sync: supported platforms and system requirements  
  https://help.resilio.com/hc/en-us/articles/205450965-Resilio-Sync-supported-platforms-and-system-requirements

- Download Sync  
  https://www.resilio.com/sync/download/

- New Opportunities Ahead as Sync Business Transitions  
  https://www.resilio.com/sync-business/

- Important before updating to Resilio Sync 3.0.0  
  https://help.resilio.com/hc/en-us/articles/31193941051795-Important-before-updating-to-Resilio-Sync-3-0-0

- Updating installation to Resilio Sync v3  
  https://help.resilio.com/hc/en-us/articles/31194252837779-Updating-installation-to-Resilio-Sync-v3

- Configuring WebUI  
  https://help.resilio.com/hc/en-us/articles/115001184490-Configuring-WebUI

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Browser warning "Your connection is not private"  
  https://help.resilio.com/hc/en-us/articles/4404757430291-Browser-warning-Your-connection-is-not-private

- Is one-way synchronization possible?  
  https://help.resilio.com/hc/en-us/articles/204754279-Is-one-way-synchronization-possible

- Folder Preferences  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- Using Archive for file versioning and restoring deleted files  
  https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files

- Encrypted folders  
  https://help.resilio.com/hc/en-us/articles/207370466-Encrypted-folders

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Sync Interface on iOS devices  
  https://help.resilio.com/hc/en-us/articles/212016726-Sync-Interface-on-iOS-devices

- Sync interface on Android  
  https://help.resilio.com/hc/en-us/articles/213500383-Sync-interface-on-Android

## Revision addendum — maintenance mutation-budget and overwrite-fate review after rev0281

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about Read Only mutation suspension, `Overwrite any changed files`, encrypted-backup hardwiring, Android backup preservation semantics, iOS remove-from-device semantics, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that `read only`, `backup`, and other maintenance-like postures do **not** imply one clean `safe local work` contract?

> where do those same current docs still show that the ordinary operator answer about `if I edit here during the hold, what later fate does that work have?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `User Management` article, which still says a Read Only peer that modifies files or adds new ones will not propagate those changes and that further synchronization of the changed files will be suspended for that peer.
- Resilio's current `Folder Preferences` article, which still says `Overwrite any changed files` on Read Only shares will overwrite local changes, including files the operator added, warns that it is potentially destructive to the operator's data, and says the option is disabled for Read-only folders with Selective Sync ON.
- Resilio's current `Encrypted folders` article, which still says encrypted backup nodes are Read Only, always have `Overwrite any changed files` activated, and do not allow Selective Sync.
- Resilio's current `How to Back up data (Android only)` article, which still says backup intentionally preserves copies even after later deletion on the phone and that the desktop side has read-only access so changes do not sync back.
- Resilio's current `Sync Interface on iOS devices` article, which still says `Remove from this device` disconnects the folder only on that iOS device and removes its files there while preserving them on others.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0282

- User Management  
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- Folder Preferences  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- Encrypted folders  
  https://help.resilio.com/hc/en-us/articles/207370466-Encrypted-folders

- How to Back up data (Android only)  
  https://help.resilio.com/hc/en-us/articles/204762339-How-to-Back-up-data-Android-only

- Sync Interface on iOS devices  
  https://help.resilio.com/hc/en-us/articles/212016726-Sync-Interface-on-iOS-devices

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — maintenance intent overload and semantic-island review after rev0280

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about manual pause, scheduled `Paused`, one-way/read-only sync, Android backup preservation semantics, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that `pause`, `scheduled Paused`, `read only`, and `backup` are materially different motion contracts rather than one maintenance class?

> where do those same current docs still show that the ordinary operator answer about `what kind of hold do I actually need, and what still moves under it?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `How to pause syncing` article, which still says pause stops only bits transfer while zero-sized files and deletions still sync and new files are rescanned and indexed.
- Resilio's current `Running Sync on schedule` article, which still says scheduled `Paused` is only a speed-zero posture, still preserves those residuals, and can still let paused peers upload to non-paused peers while not downloading themselves.
- Resilio's current `Is one-way synchronization possible?` article, which still says Read Only permission gives one-way sync where changes made in the read-only folder do not sync back.
- Resilio's current `How to Back up data (Android only)` article, which still says backup intentionally preserves copies and that the desktop side has read-only access so changes do not sync back.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0281

- How to pause syncing  
  https://help.resilio.com/hc/en-us/articles/206217325-How-to-pause-syncing

- Running Sync on schedule  
  https://help.resilio.com/hc/en-us/articles/210783266-Running-Sync-on-schedule

- Is one-way synchronization possible?  
  https://help.resilio.com/hc/en-us/articles/204754279-Is-one-way-synchronization-possible

- How to Back up data (Android only)  
  https://help.resilio.com/hc/en-us/articles/204762339-How-to-Back-up-data-Android-only

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — re-entry cases, dormancy truth, and stale-return safety after rev0275

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about hidden offline devices, peer-expiration aging, shutdown/re-open chronology effects, clock-invalid returns, ghost announcements, and the maintained v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that not every comeback is an ordinary healthy return?

> where do those same current docs still show that the ordinary operator answer about `what exactly returned after dormancy, and how trustworthy is that return?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Does Sync work in background?` article, which still says shutdown/re-open reindexes folders, gives them a new modification time, and can let offline updates overwrite changes made by peers that remained online.
- Resilio's current `Sync Main View (Desktop)` article, which still says offline peers are disconnected from the folder after 7 days.
- Resilio's current `Power user preferences` article, which still names `peer_expiration_days` with default `7 (day)`.
- Resilio's current `How to clear offline devices? (desktop only)` article, which still says hiding an offline device only hides it from view and that it will reappear if it later goes online.
- Resilio's current `"Time difference" error` article, which still says time / timezone drift beyond 600 seconds invalidates chronology and that mobile peers may show empty lists.
- Resilio's current `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time` article, which still says some announced files are ghost files that nobody has anymore.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.
- Resilio's still-published historical `Resilio Sync change log`, which still records reconnect-after-long-offline and reconnected-peer download fixes, reinforcing that stale-return semantics have long been a real product seam.

## Additional Resilio official sources emphasized in rev0276

- Does Sync work in background?  
  https://help.resilio.com/hc/en-us/articles/206816823-Does-Sync-work-in-background

- Sync Main View (Desktop)  
  https://help.resilio.com/hc/en-us/articles/204755009-Sync-Main-View-Desktop

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- How to clear offline devices? (desktop only)  
  https://help.resilio.com/hc/en-us/articles/204762439-How-to-clear-offline-devices-desktop-only

- "Time difference" error  
  https://help.resilio.com/hc/en-us/articles/204753599--Time-difference-error

- Cannot download files / These files cannot be downloaded as there are no source peers online for too long time  
  https://help.resilio.com/hc/en-us/articles/360010899719-Cannot-download-files-These-files-cannot-be-downloaded-as-there-are-no-source-peers-online-for-too-long-time

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Resilio Sync change log  
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log

## Revision addendum — route posture, effective path, and route-provenance fragmentation after rev0271

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about discovery helpers, effective path classes, relay fallback, current route witnesses, and the active v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that tracker, LAN search, predefined hosts, direct transport, and relay are different route ingredients?

> where do those same current docs still show that the ordinary operator answer about `what route did this incident actually take, over what window, and did it match policy?` still depends on toggles, current chrome, and troubleshooting prose instead of one stable product-owned object?

The most load-bearing source set for this pass was:

- Resilio's current `What ports and protocols are used by Sync?` article, which still separates sync.conf discovery, tracker communication, direct TCP/UDP attempts, relay fallback, and LAN multicast.
- Resilio's current `What is a Relay Server?` article, which still says relay is a fallback, still says it impacts syncing speed, and still ties relay use to a peer-list icon.
- Resilio's current `Folder Preferences` article, which still makes relay, tracker, LAN search, and predefined hosts per-folder helper posture.
- Resilio's current `Performance overview` article, which still exposes a live peer-connection protocol row alongside upload/download/RTT.
- Resilio's current `Peers aren't connecting` article, which still names blocked tracker, blocked relay, blocked listening port, and multiple NIC routing as distinct causes.
- Resilio's current `Download/upload speed is very slow` article, which still calls out relay penalty and still recommends direct-port mapping, port forwarding, and predefined hosts.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

Reference URLs:

- https://help.resilio.com/hc/en-us/articles/204754759-What-ports-and-protocols-are-used-by-Sync
- https://help.resilio.com/hc/en-us/articles/204754779-What-is-a-Relay-Server
- https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences
- https://help.resilio.com/hc/en-us/articles/360001331930-Performance-overview
- https://help.resilio.com/hc/en-us/articles/205450205-Peers-aren-t-connecting
- https://help.resilio.com/hc/en-us/articles/205450195-Download-upload-speed-is-very-slow
- https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — representative pair, topology coverage, and mesh-wide claim ceilings after rev0270

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about per-peer performance tables, asymmetric uploader effects, pairwise iperf benchmarking, per-folder helper policy, all-peer speed escalation, and the maintained v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that one pair, one uploader cohort, and one share-wide incident are different performance scopes?

> where do those same current docs still show that the ordinary operator answer about `does this pairwise result really generalize?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Performance overview` article, which still exposes a details table of peer connections with upload/download speed, RTT, and protocol for each connected peer.
- Resilio's current `Download/upload speed is very slow` article, which still says one slow uploader can reduce other peers' download speed, that more high-upload peers can raise the effective rate, and that persistent cases should escalate to logs from all peers.
- Resilio's current `Measuring network performance with iperf3` guide, which still prescribes a benchmark between two peers and still requires Sync to be shut down completely on both peers during the tests.
- Resilio's current `Folder Preferences` article, which still says relay/tracker/LAN/predefined-host posture is configured per folder and that predefined hosts should be used on all peers in constrained environments.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the maintained v3 line through `3.1.2.1076`.

## Additional Resilio official sources emphasized in rev0271

- Performance overview  
  https://help.resilio.com/hc/en-us/articles/360001331930-Performance-overview

- Download/upload speed is very slow  
  https://help.resilio.com/hc/en-us/articles/205450195-Download-upload-speed-is-very-slow

- Measuring network performance with iperf3  
  https://help.resilio.com/hc/en-us/articles/1500007478562-Measuring-network-performance-with-iperf3

- Folder Preferences  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — sidecar benchmarking, capacity isolation, and tuning-cost honesty after rev0269

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about slow-speed causes, direct-versus-relayed paths, rate-limit and LAN-encryption settings, hidden internal-task overhead, external iperf3 benchmarking, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that raw network capacity, route class, workload shape, and hidden Sync work are different performance truths?

> where do those same current docs still show that the ordinary operator answer about `is the network really the limiter, what had to be quiet first, and which tuning change is justified next` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Download/upload speed is very slow` article, which still names many-small-file workload, relay usage, asymmetrical peers, low-capacity hardware, security software delay, `disk_low_priority`, closed listening ports, predefined hosts, and all-peer log escalation.
- Resilio's current `How can I improve data transfer/sync speed?` article, which still prefers direct connections, same-LAN or VPN paths, predefined hosts, `rate_limit_local_peers false`, `lan_encrypt_data false`, and `disk_low_priority false`.
- Resilio's current `Power user preferences` article, which still publishes defaults for `rate_limit_local_peers` and `lan_encrypt_data` and keeps those tuning names concrete.
- Resilio's current `Some internal tasks are taking time to complete` article, which still says hashing, deduplication, merging, scanning, reading, writing, and transfer are separate hidden operations with distinct disk/CPU implications.
- Resilio's current `Measuring network performance with iperf3` guide, which still says Sync should be shut down completely on both peers during tests and still prescribes sequential forward/reverse TCP and UDP commands.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0270

- Download/upload speed is very slow  
  https://help.resilio.com/hc/en-us/articles/205450195-Download-upload-speed-is-very-slow

- How can I improve data transfer/sync speed?  
  https://help.resilio.com/hc/en-us/articles/204762319-How-can-I-improve-data-transfer-sync-speed

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Some internal tasks are taking time to complete  
  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete

- Measuring network performance with iperf3  
  https://help.resilio.com/hc/en-us/articles/1500007478562-Measuring-network-performance-with-iperf3

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — instrumentation posture, restart truth, and baseline-return honesty after rev0268

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about enabling debug logging, hidden-file activation, restart requirements, minimum dwell, log-size inflation, profiler activation, retention defaults, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that evidence often requires changing runtime posture first rather than merely exporting artifacts later?

> where do those same current docs still show that the ordinary operator answer about `what posture changed, when it became active, and whether baseline was restored` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Collecting debug logs automatically` guide, which still says operators may enable debug logging in settings or via hidden `debug.txt`, should restart Sync to ensure logging is enabled, should collect at least 15 minutes after reproduction, and should not close the app/device until sending is done.
- Resilio's current `Collecting debug logs manually` guide, which still repeats the enable-and-restart ritual, still says large estates may need increased log size, and still names concrete log files and platform-specific storage paths.
- Resilio's current `Increasing Debug Log size` guide, which still says rotation defaults are `100 Mbytes`, that `sync.log` is backed up to `sync.log.old`, that operators should raise `log_size` to `200` or more and restart, and that older Linux/NAS versions may still require editing `settings.dat` without `kill -9` shutdown.
- Resilio's current `Power user preferences` article, which still lists `log_size 100 (MB)`, `log_ttl 7 (day)`, and `profiler_enabled false`, and still says profiler data is stored in `profiler.dat`, rotates every 10 minutes, and requires restart to activate.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0269

- Collecting debug logs automatically  
  https://help.resilio.com/hc/en-us/articles/360019430539-Collecting-debug-logs-automatically

- Collecting debug logs manually  
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

- Increasing Debug Log size  
  https://help.resilio.com/hc/en-us/articles/205450145-Increasing-Debug-Log-size

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — raw-artifact intake, cleanup ritual, and provenance-preserving normalization after rev0267

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about raw log filenames, path heterogeneity, hidden mobile harvests, NAS whole-folder copy/cleanup, crash/core-dump file shapes, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that evidence first appears as heterogeneous raw artifacts rather than one clean packet?

> where do those same current docs still show that the ordinary operator answer about `what raw material did I actually harvest and what changed during cleanup?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Collecting debug logs manually` guide, which still names `sync.log` and `sync.log.<some number>.zip`, still varies storage roots by platform/service/config mode, and still ends in portal upload plus forum-link / size-cap ritual.
- Resilio's current `How to collect logs on NAS manually?` guide, which still says to copy the whole Sync internal-data folder from the NAS, then clean it up leaving only `*.log`, `*.log.zip`, and `*.journal`, then pack and send.
- Resilio's current `Collect debug logs on mobiles` guide, which still routes raw harvest through `SNC.DBG.LOGS` and the hidden `.synclogs` folder.
- Resilio's current `Collecting crash reports, mini-dumps and core dumps` guide, which still spreads crash materials across platform-specific paths, filenames, and gzipped-core rituals.
- Resilio's current `Collecting core dump on NAS devices` guide, which still says to move the produced dump into a shared/public folder so it can be downloaded through the NAS WebUI before send.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0268

- Collecting debug logs manually  
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

- How to collect logs on NAS manually?  
  https://help.resilio.com/hc/en-us/articles/208800446-How-to-collect-logs-on-NAS-manually

- Collect debug logs on mobiles  
  https://help.resilio.com/hc/en-us/articles/38269346960531-Collect-debug-logs-on-mobiles

- Collecting crash reports, mini-dumps and core dumps  
  https://help.resilio.com/hc/en-us/articles/206214615-Collecting-crash-reports-mini-dumps-and-core-dumps

- Collecting core dump on NAS devices  
  https://help.resilio.com/hc/en-us/articles/360015557220-Collecting-core-dump-on-NAS-devices

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Sources addendum — rev0266 companion cases, audience splits, and public/private continuity

The most load-bearing source set for this pass was another current official Resilio cluster around forum/help routing, support contact language, log-submission instructions, and the active v3 line.

- Resilio's current `I still have questions, where can I get answers?` article, which still sends users to the forum while also saying they can contact support, with PRO users first to get response and FREE users answered to the extent possible.
- Resilio's current `Collecting debug logs automatically` article, which still says technical support is available exclusively for Resilio Sync Business customers, still routes Sync v3 functionality questions toward forum/help-center self-service and payments/licensing toward a web form, and still asks the operator to state which support ticket the logs refer to plus peer role, timestamp, detailed description, and affected shares/files.
- Resilio's current `Collecting debug logs manually` article, which still says that if the operator was redirected there from Forums they should mention the forum link when sending logs through the support web portal.
- Resilio's current `Collecting crash reports, mini-dumps and core dumps` and `Collecting core dump on NAS devices` articles, which still repeat the same Business-only direct-support versus Sync v3 self-serve split.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the active v3 line through `3.1.2.1076`.

Reference URLs:

- https://help.resilio.com/hc/en-us/articles/206216795-I-still-have-questions-where-can-I-get-answers
- https://help.resilio.com/hc/en-us/articles/360019430539-Collecting-debug-logs-automatically
- https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually
- https://help.resilio.com/hc/en-us/articles/206214615-Collecting-crash-reports-mini-dumps-and-core-dumps
- https://help.resilio.com/hc/en-us/articles/360015557220-Collecting-core-dump-on-NAS-devices
- https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Sources addendum — rev0265 escalation-lane entitlement, destination ambiguity, and response-expectation ceilings

The most load-bearing source set for this pass was another current official Resilio cluster around technical-support entitlement, in-app send surfaces, forum/help-center routing, billing/licensing web-form routing, product-line incompatibility, and the active version line.

- Resilio's current `Collecting debug logs automatically` article, which still says technical support is available exclusively for Resilio Sync Business customers, that Sync v3 functionality questions should go to the community forum and Help Center, that payments/licensing questions should use a web form, and that the in-product path still goes through `Preferences (Settings) > Support > Contact support`.
- Resilio's current `Collecting debug logs manually` article, which still repeats the same Business-only technical-support language, Sync v3 self-serve guidance, and payments/licensing web-form routing.
- Resilio's current `Collecting crash reports, mini-dumps and core dumps` and `Collecting core dump on NAS devices` articles, which still repeat the same lane split while sending operators through OS-specific artifact collection steps.
- Resilio's current `I still have questions, where can I get answers?` article, which still says users can look through the forum and also contact support, with PRO users first to get response and FREE users answered to the extent possible.
- Resilio's current `Licensing in Resilio Sync 3.0` article, which still says Business licenses are not compatible with Sync v3 and that commercial users should continue using Sync v2 or explore business solutions.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the active v3 line through `3.1.2.1076`, including license-application UI work and the earlier fix for a non-clickable `Can't download file` status.

Reference URLs:

- https://help.resilio.com/hc/en-us/articles/360019430539-Collecting-debug-logs-automatically
- https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually
- https://help.resilio.com/hc/en-us/articles/206214615-Collecting-crash-reports-mini-dumps-and-core-dumps
- https://help.resilio.com/hc/en-us/articles/360015557220-Collecting-core-dump-on-NAS-devices
- https://help.resilio.com/hc/en-us/articles/206216795-I-still-have-questions-where-can-I-get-answers
- https://help.resilio.com/hc/en-us/articles/31116248751123-Licensing-in-Resilio-Sync-3-0
- https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Sources addendum — rev0264 artifact-class sprawl, capture-route fragmentation, and package opacity

The most load-bearing source set for this pass was another current official Resilio cluster around support-bound evidence classes, route-specific capture steps, package preconditions, and the active v3 line.

- Resilio's current `Send info to Support team` section, which still groups separate guides for mobile logs, iperf3, automatic logs, manual logs, crash reports / dumps, NAS core dumps, and log-size tuning.
- Resilio's current `Collecting debug logs automatically` guide, which still says technical support is available exclusively for Business customers, still directs Sync v3 users to forum / Help Center self-service for functionality help, still asks operators to keep the app/device open until sending is done, and still routes desktops/NAS to manual fallback if send fails.
- Resilio's current `Collecting debug logs manually` guide, which still names `sync.log` and rotated zipped log files and still lists platform- and service-specific storage paths.
- Resilio's current `Collect debug logs on mobiles` guide, which still says to use `SNC.DBG.LOGS` and pull logs from hidden `.synclogs`.
- Resilio's current `Collecting crash reports, mini-dumps and core dumps` guide, which still splits artifact type and collection route by operating system.
- Resilio's current `Measuring network performance with iperf3` guide, which still says Sync should be shut down completely on both peers during testing.
- Resilio's current `Increasing Debug Log size` guide, which still says logs rotate at `100 Mbytes` by default, keep `sync.log` plus `sync.log.old`, may still be insufficient at `200 Mb`, and cannot be adjusted on mobile platforms.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the active v3 line through `3.1.2.1076`.

Reference URLs:

- https://help.resilio.com/hc/en-us/sections/201494276-Send-info-to-Support-team
- https://help.resilio.com/hc/en-us/articles/360019430539-Collecting-debug-logs-automatically
- https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually
- https://help.resilio.com/hc/en-us/articles/38269346960531-Collect-debug-logs-on-mobiles
- https://help.resilio.com/hc/en-us/articles/206214615-Collecting-crash-reports-mini-dumps-and-core-dumps
- https://help.resilio.com/hc/en-us/articles/1500007478562-Measuring-network-performance-with-iperf3
- https://help.resilio.com/hc/en-us/articles/205450145-Increasing-Debug-Log-size
- https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — incident brief, timestamps, and coordinated capture-run context after rev0262

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about freeform support narrative, symptom timestamps, reproduction dwell, send-completion ritual, and the active v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that logs need role, timestamp, subject, and reproduction context?

> where do those same current docs still show that the ordinary operator answer about `what symptom are we chasing and did this run really catch it?` still depends on prose and ritual instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Collecting debug logs automatically` guide, which still says to reproduce the issue, let Sync collect logs for at least 15 minutes, include peer role / timestamp / detailed description / affected share or file names in feedback text, and keep the application or device open until sending is done.
- Resilio's current `Collecting debug logs manually` guide, which still says to describe the issue, mention the forum link when redirected from Forums, and respect packet-size / upload-route constraints.
- Resilio's current `My files don't sync` article, which still routes operators through peers, warnings, history search, and queue checks before heavier capture.
- Resilio's current `Peers aren't connecting` article, which still implies a specific failing pair and ends the unresolved path with logs from two peers that cannot connect.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0263

- Collecting debug logs automatically  
  https://help.resilio.com/hc/en-us/articles/360019430539-Collecting-debug-logs-automatically

- Collecting debug logs manually  
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

- My files don't sync  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Peers aren't connecting  
  https://help.resilio.com/hc/en-us/articles/205450205-Peers-aren-t-connecting

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — witness-set scope, peer-role annotation, and multi-peer evidence completeness after rev0261

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about pairwise connectivity troubleshooting, all-peer log asks for persistent sync/speed problems, participant-role annotation inside feedback, and the active v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that different incidents need different witness counts and role context?

> where do those same current docs still show that the ordinary operator answer about `which peers matter for this case, what role each plays, and when the witness set is complete enough` still depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Peers aren't connecting` article, which still says persistent pairwise connection trouble should be escalated with debug logs from two peers that cannot connect.
- Resilio's current `My files don't sync` article, which still says that if the listed checks do not help, operators should collect logs from all peers and send them to support.
- Resilio's current `How can I improve data transfer/sync speed?` article, which still ends the persistent-speed path with collect logs from all peers.
- Resilio's current `Collecting debug logs automatically` guide, which still says the feedback text should include the role of that peer in the setup, the timestamp for the observed problem, and the affected share/file names.
- Resilio's current `Collecting debug logs manually` guide, which still keeps packet-level upload and size-limit constraints visible rather than one reviewed witness object.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0262

- Peers aren't connecting  
  https://help.resilio.com/hc/en-us/articles/205450205-Peers-aren-t-connecting

- My files don't sync  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- How can I improve data transfer/sync speed?  
  https://help.resilio.com/hc/en-us/articles/204762319-How-can-I-improve-data-transfer-sync-speed

- Collecting debug logs automatically  
  https://help.resilio.com/hc/en-us/articles/360019430539-Collecting-debug-logs-automatically

- Collecting debug logs manually  
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Sources addendum — rev0260 incident object, history search, and diagnostic continuity

The most load-bearing source set for this pass was another current official Resilio cluster around main-view row semantics, troubleshooting route archaeology, item-level locked-file detail, debug-log capture ritual, and the active version line.

- Resilio's current `Sync Main View (Desktop)` article, which still says statuses show current activity, that `X of Y` opens the peers list, and that History is a distinct 30-day activity surface.
- Resilio's current `My files don't sync` article, which still tells operators to click peers counts, click status warnings that often lead to KB explanations, search Sync History, inspect queues from peers lists, and only later collect logs from all peers.
- Resilio's current `Locked files` article, which still says the error row opens a list of locked files while also saying Sync cannot identify which application locked them.
- Resilio's current `Collecting debug logs manually` article, which still says direct technical support is only for Resilio Sync Business customers, Sync v3 users are directed toward forum/help-center self-service, debug logging may require restart, logs should be collected for at least 15 minutes, and attachment ceilings or manual routes can matter.
- Resilio's current `Collecting debug logs automatically` article, which still says debug logging must be enabled, restart can be required, log send is a separate support action, and fallback to manual collection exists if automatic send fails.
- Resilio's current `Peers aren't connecting` and `Download/upload speed is very slow` articles, which still say unresolved cases should end in collecting debug logs from the relevant peers.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line and records that `Can't download file` had to be fixed to be clickable.

Reference URLs:

- https://help.resilio.com/hc/en-us/articles/204755009-Sync-Main-View-Desktop
- https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync
- https://help.resilio.com/hc/en-us/articles/205504549-Locked-files
- https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually
- https://help.resilio.com/hc/en-us/articles/360019430539-Collecting-debug-logs-automatically
- https://help.resilio.com/hc/en-us/articles/205450205-Peers-aren-t-connecting
- https://help.resilio.com/hc/en-us/articles/205450195-Download-upload-speed-is-very-slow
- https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Sources addendum — rev0259 warning taxonomy, blocker scope, and least-strong repair

The most load-bearing source set for this pass was another current official Resilio cluster around core warnings, continuity-damage warnings, chronology-invalid warnings, ghost-source warnings, recoverable hidden-work warnings, and the active version line.

- Resilio's current `Core warnings` article, which still separates tracker/bootstrap trouble, low space on the default-folder-location disk, failed folder-list / identity sync, and license-management disablement.
- Resilio's current `Service files missing / Cannot identify destination folder` article, which still says synchronization for that folder is suspended and that one repair path is remove/re-add after checking Archive and deleting `.sync`.
- Resilio's current `Some internal tasks are taking time to complete` article, which still says the condition can be intermittent and recoverable rather than a hard stall.
- Resilio's current `Time difference` article, which still says chronology trust is invalidated when peer clocks or timezone settings are wrong and that mobile devices may show empty lists.
- Resilio's current `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time` article, which still says some announced items can remain without any full source peer.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the active v3 line through `3.1.2.1076`.

Reference URLs:

- https://help.resilio.com/hc/en-us/articles/360001217950-Core-warnings
- https://help.resilio.com/hc/en-us/articles/205450225-Service-files-missing-Cannot-identify-destination-folder
- https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete
- https://help.resilio.com/hc/en-us/articles/204753599--Time-difference-error
- https://help.resilio.com/hc/en-us/articles/360010899719-Cannot-download-files-These-files-cannot-be-downloaded-as-there-are-no-source-peers-online-for-too-long-time
- https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Sources addendum — rev0258 paused-label origin split and named-state honesty

The most load-bearing source set for this pass was another current official Resilio cluster around manual pause, scheduled pause, global pause placement, and the active version line.

- Resilio's current `How to pause syncing` article, which still says pause stops only bits upload/download, while zero-sized files and deletions still sync and new files are still rescanned and indexed.
- Resilio's current `Running Sync on schedule` article, which still says scheduled `Paused` means upload/download speed are zero, yet paused peers can still upload to other non-paused peers, while deletions still sync and indexing continues.
- Resilio's current `Sync Preferences` article, which still presents Global Pause/Resume and Scheduler as ordinary nearby controls.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the active v3 line through `3.1.2.1076`.

Reference URLs:

- https://help.resilio.com/hc/en-us/articles/206217325-How-to-pause-syncing
- https://help.resilio.com/hc/en-us/articles/210783266-Running-Sync-on-schedule
- https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences
- https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Sources addendum — rev0257 replay class, piece-shift fallback, and differential-sync ceilings

The most load-bearing source set for this pass was another current official Resilio cluster around changed-file replay class, piece-shifting full resend, stronger diff-delta language, and policy-bearing differential-sync choices.

- Resilio's current `When a file changes, does Resilio Sync transfer the entire file again, or just the part that's changed?` article, which still says files are split into pieces from `32 KB` to `2 MB`, that only changed pieces are usually transferred, that piece-shifting edits can still force a whole-file resend, and that Sync Business has diff-delta sync for that case.
- Resilio's current official documentation page `Synchronizing pre-seeded folder`, which still says the `Disable differential sync` parameter chooses between whole-file sync and changed-piece replay once a file needs syncing, and that hash-availability policy materially changes replay behavior.
- Resilio's current official documentation page `Advanced custom parameters`, which still says hashing/differential parameters are coupled and that weak hash availability can make changed-file replay depend on which agent actually has hashes.
- Resilio's current official best-practice pages for VDI / profile-style workloads, which still say slower disks may justify full-file replay while faster disks may justify changed-piece replay and stronger local recheck.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the active v3 line through `3.1.2.1076`.

Reference URLs:

- https://help.resilio.com/hc/en-us/articles/206217095-When-a-file-changes-does-Resilio-Sync-transfer-the-entire-file-again-or-just-the-part-that-s-changed
- https://www.resilio.com/documentation/content/advanced-configuration/best-practices/synchronizing_pre-seeded_folder/
- https://www.resilio.com/documentation/content/advanced-configuration/profiles-and-configuration-parameters/advanced_custom_parameters/
- https://www.resilio.com/documentation/content/advanced-configuration/best-practices/best_practices_for_synchronizing_fslogix_and_vdi_profiles/
- https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Sources addendum — rev0256 name-plane reset, stale outward labels, and residue after disconnect

The most load-bearing source set for this pass was another current official Resilio cluster around custom share names, rename-local-only path behavior, and the active version line.

- Resilio's current `Setting custom name for sync shares` article, which still says a custom UI name does not rename the folder on disk, does not propagate to linked devices, can be changed while sharing so a different label is inserted into a link or QR, requires QR regeneration after rename, and remains in the UI after disconnect until explicit `Reset`.
- Resilio's current `Can I move or rename a syncing folder?` article, which still says renaming a synced folder affects only the device where it is renamed.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the active v3 line through `3.1.2.1076`.

Reference URLs:

- https://help.resilio.com/hc/en-us/articles/360011865879-Setting-custom-name-for-sync-shares
- https://help.resilio.com/hc/en-us/articles/205450655-Can-I-move-or-rename-a-syncing-folder
- https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — indirection objects, target non-transitivity, and conflict fallout after rev0253

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about symbolic links, hard links, directory junctions, unsupported-entry consequences, and `.Conflict` fallout.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that a normal-looking path row may be an indirection object with a materially different fidelity contract?

> where do those same current docs still show that the ordinary operator answer about `is this object syncing, is its target syncing, or is this a conflict generator here?` still depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Soft links, hard links and symbolic links` article, which still says Windows does not support these classes and that `.Conflict` fallout may result, while Unix can synchronize symbolic links as links but not automatically synchronize the target folders.
- Resilio's current `Conflict files in Sync` article, which still names linked junctions as a direct cause of `.Conflict` artifacts.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the active v3 line through `3.1.2.1076`.

## Additional Resilio official sources emphasized in rev0254

- Soft links, hard links and symbolic links
  https://help.resilio.com/hc/en-us/articles/205504529-Soft-links-hard-links-and-symbolic-links

- Conflict files in Sync
  https://help.resilio.com/hc/en-us/articles/204753629-Conflict-files-in-Sync

- Resilio Sync 3.0 change log
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — identity actions, subject-class fallout, and mobile byte deletion after rev0252

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about identity linking, renaming an identity, uninstall sequencing, and platform-specific local-byte fate.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that identity verbs can change local subject governance and byte survival differently by class and platform?

> where do those same current docs still show that the ordinary operator answer about `what survives this identity action on this seat?` still depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says linking two already-running installs can make one device lose its certificate, remove Advanced folders from the app, copy folders from the other instance, and on iOS delete those Advanced folders from the file system.
- Resilio's current `Can I change the name of my Sync identity?` article, which still says renaming requires unlinking and creating a new identity, removes Advanced folders from the instance, leaves Standard folders in the instance, and keeps folders in the system except on iOS and Windows Phone.
- Resilio's current `How to uninstall Sync?` article, which still says operators should unlink from identity first, then remove remaining Standard shares, and that uninstall on iOS and Windows Phone removes synced files from the device.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the active v3 line through `3.1.2.1076`.

## Additional Resilio official sources emphasized in rev0253

- Sync Private Identity & Linking My Devices
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Can I change the name of my Sync identity?
  https://help.resilio.com/hc/en-us/articles/206163443-Can-I-change-the-name-of-my-Sync-identity

- How to uninstall Sync?
  https://help.resilio.com/hc/en-us/articles/204775029-How-to-uninstall-Sync

- Resilio Sync 3.0 change log
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — hydration-engine split, shell/provider lane truth, and history/collision ceiling after rev0251

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio docs about classic Selective Sync placeholders, shell/context-menu dependencies, a recent Selective Sync macOS fix in the live v3 line, and the newer Windows transparent/cloud-file hydration engine whose guarantees differ from legacy expectations.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `Selective Sync` is not one stable contract but several different hydration engines and local action lanes?

> where do those same current docs still show that the ordinary operator answer about `what exactly can this online-only mode promise here?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Selective Sync` article, which still says Selective Sync can mean placeholder-only arrival and that removing a Selective Sync share removes placeholders from that device.
- Resilio's current `No Sync icons in the file browser/no Sync-related items in the context menu on Mac/Windows` article, which still says file-browser actions depend on Finder extension health on macOS and on NTFS/alternate-data-stream support plus shell registration on Windows.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line and records a recent fix for missing context-menu items in Selective Sync shares on macOS.
- Resilio's current `Transparent Selective Sync (TSS) on Windows` article, which still says TSS is a different engine from legacy Selective Sync, requires specific Windows/API/path prerequisites, narrows Archive/version-history behavior and collision detection on older lines, and names several local co-tenant/runtime conflicts.

## Additional Resilio official sources emphasized in rev0251

- Selective Sync
  https://help.resilio.com/hc/en-us/articles/205458095-Selective-Sync

- No Sync icons in the file browser/no Sync-related items in the context menu on Mac/Windows
  https://help.resilio.com/hc/en-us/articles/206214625-No-Sync-icons-in-the-file-browser-no-Sync-related-items-in-the-context-menu-on-Mac-Windows

- Resilio Sync 3.0 change log
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Transparent Selective Sync (TSS) on Windows
  https://www.resilio.com/documentation/content/advanced-configuration/agents/transparent_selective_sync_windows/

## Revision addendum — hidden StreamsList locality, xattr courier stubs, and ignore-boundary split after rev0249

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about xattr / alternate-stream whitelisting, hidden `StreamsList` policy locality, `IgnoreList` non-applicability, `.sync/Streams` fallback stubs, bundle-shape consequences, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that metadata carriage can be selective, hidden, and platform-constrained at the same time?

> where do those same current docs still show that the ordinary operator answer about `is this seat preserving object meaning natively, merely relaying it, or silently narrowing it?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Alt Streams and Xattrs in Sync` article, which still says xattrs sync only according to a whitelist in hidden `.sync/StreamsList`, that the file is editable, that unlisted xattrs are ignored, that `IgnoreList` does not control xattrs, and that unsupported targets may use hidden `.sync/Streams` stubs.
- Resilio's current `What is '.sync' folder, and StreamsList, IgnoreList and Archive inside?` article, which still says `.sync` is critical and that service-state families like `StreamsList` live there.
- Resilio's current `Ignoring files in Sync (Ignore List)` article, which still says IgnoreList is a separate hidden rule file and that peer differences are allowed.
- Resilio's current troubleshooting / shell-behavior notes already reflected in the archive, which still tie disabled xattr syncing to bundle-shape exposure on macOS.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0250

- Alt Streams and Xattrs in Sync
  https://help.resilio.com/hc/en-us/articles/204754729-Alt-Streams-and-Xattrs-in-Sync

- What is '.sync' folder, and StreamsList, IgnoreList and Archive inside?
  https://help.resilio.com/hc/en-us/articles/206217185-What-is-sync-folder-and-StreamsList-IgnoreList-and-Archive-inside

- Ignoring files in Sync (Ignore List)
  https://help.resilio.com/hc/en-us/articles/205458165-Ignoring-files-in-Sync-Ignore-List

- Resilio Sync 3.0 change log
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — copied-tree identity carry, hidden control state, and unsupported clone after rev0249

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about hidden `.sync` state, same-ID recognition, service-file failure, unsupported cloning, storage-root contamination, and whole-tree add failure.
The new questions were:

> where do current official docs most clearly show that a folder can look like ordinary bytes while still carrying live sync identity and controller state?

> where do those same current docs still show that the ordinary operator answer about `is this copied payload or still the same managed subject?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `What is '.sync' folder, and StreamsList, IgnoreList and Archive inside?` article, which still says `.sync` is critical, contains the ID and service files, and should not be moved separately from the folder.
- Resilio's current `Selected folder is already added to Sync` article, which still says Sync recognizes a share by `.sync/ID` and therefore the same ID cannot be added twice on one device.
- Resilio's current `Service files missing / Cannot identify destination folder` article, which still says deleting or corrupting `.sync` suspends sync, that the error may also appear when two Sync instances touch the same folder or external-drive storage, and that repair can still require checking Archive, deleting `.sync`, and re-adding the share.
- Resilio's current `Cloning Sync` article, which still says raw cloning of a Sync instance is unsupported.
- Resilio's current `Cannot add folder. It contains a folder that is already syncing.` article, which still says whole-home-folder add attempts can fail because Sync's own storage folder with a `License` directory sits inside the tree.
- Resilio's current `Sync Storage folder` article, which still says configuration, database, and support material live in the storage folder and that its location changes by runtime profile.

## Additional Resilio official sources emphasized in rev0249

- What is '.sync' folder, and StreamsList, IgnoreList and Archive inside?
  https://help.resilio.com/hc/en-us/articles/206217185-What-is-sync-folder-and-StreamsList-IgnoreList-and-Archive-inside

- Selected folder is already added to Sync
  https://help.resilio.com/hc/en-us/articles/209316526-Selected-folder-is-already-added-to-Sync

- Service files missing / Cannot identify destination folder
  https://help.resilio.com/hc/en-us/articles/205450225-Service-files-missing-Cannot-identify-destination-folder

- Cloning Sync
  https://help.resilio.com/hc/en-us/articles/360018421940-Cloning-Sync

- Cannot add folder. It contains a folder that is already syncing.
  https://help.resilio.com/hc/en-us/articles/360000053399-Cannot-add-folder-It-contains-a-folder-that-is-already-syncing

- Sync Storage folder
  https://help.resilio.com/hc/en-us/articles/206664690-Sync-Storage-folder

## Revision addendum — substrate truth, notify gaps, and mixed-writer hazard after rev0246

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about SMB/network-mounted shares, filesystem notification limits, lock diagnosis boundaries, edit-delay tuning, substrate-shaped advanced knobs, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that a mounted or networked path may still be a materially worse sync substrate even if the share looks ordinary in the main UI?

> where do those same current docs still show that the ordinary operator answer about `is this connected share safe and prompt on this path?` still depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Sync and SMB file shares` article, which still says SMB shares work with limitations, that notifications may require SMB 3.0 on both client and server, that lock behavior depends on the SMB implementation, and that third-party access outside Samba can damage files or roll back changes.
- Resilio's current `How soon does synchronization start?` article, which still says filesystem notifications are the fastest path but do not work for some storages such as NFS or SMB2 mounted shares, with scheduled rescans every 600 seconds by default as the fallback.
- Resilio's current `Locked files` article, which still says another application may block access, that Sync cannot tell which application locked the file, and that operators may need external tooling and restart to recover.
- Resilio's current `Setting Delay Time For Syncing` article, which still says per-file-type delay may be needed when editing and syncing the same file at once to avoid conflicts between Office and Sync.
- Resilio's current `Power user preferences` article, which still exposes substrate-shaped controls such as `disk_worker_pool_size` for high-latency CIFS/network shares, `enable_file_system_notifications`, and `recheck_locked_files_interval`.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0247

- Sync and SMB file shares
  https://help.resilio.com/hc/en-us/articles/207755736-Sync-and-SMB-file-shares

- How soon does synchronization start?
  https://help.resilio.com/hc/en-us/articles/204754319-How-soon-does-synchronization-start

- Locked files
  https://help.resilio.com/hc/en-us/articles/205504549-Locked-files

- Setting Delay Time For Syncing
  https://help.resilio.com/hc/en-us/articles/207491426-Setting-Delay-Time-For-Syncing

- Power user preferences
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Resilio Sync 3.0 change log
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — backup-subject mode bypass, storage-only connected appearance, and subject-kind override after rev0245

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about linked-device sync modes, camera backup, Android backup asymmetry, pre-populated reconnect workflow, linked-family arrival convenience, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that backup/storage-only subjects are real and not merely ordinary sync with a friendlier label?

> where do those same current docs still show that the ordinary operator answer about `does this seat default still apply to this subject?` still depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Synchronization Modes` article, which still says linked devices can be set to `Disconnected`, `Selective Sync`, or `Synced` to control how much data is moved to each device.
- Resilio's current `How to use Camera Backup (all mobiles)?` article, which still says backup folders are for storage purposes only, create `1.4` folders with Read Only keys, auto-create a backup folder on the destination desktop, and preserve already-present pictures on both devices when backup is disconnected.
- Resilio's current `How to Back up data (Android only)` article, which still says desktop has Read-only access to the backup share, destination-side changes do not sync back, and destination-side deletions do not delete the phone copy.
- Resilio's current `Can I connect two pre-populated pre-existing folders?` article, which still says that when using mobile's backup with linked devices the share will always appear connected on destination desktops regardless of the syncing mode and must be disconnected/reconnected.
- Resilio's current `Sync Private Identity & Linking My Devices` and `Sync functionality in detail` articles, which still say linked devices share one common folder list and linked-device arrival convenience is part of the model.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the active v3 line through `3.1.2.1076`.

## Additional Resilio official sources emphasized in rev0246

- Synchronization Modes
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- How to use Camera Backup (all mobiles)?
  https://help.resilio.com/hc/en-us/articles/205506809-How-to-use-Camera-Backup-all-mobiles

- How to Back up data (Android only)
  https://help.resilio.com/hc/en-us/articles/204762339-How-to-Back-up-data-Android-only

- Can I connect two pre-populated pre-existing folders?
  https://help.resilio.com/hc/en-us/articles/205506569-Can-I-connect-two-pre-populated-pre-existing-folders

- Sync Private Identity & Linking My Devices
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Sync functionality in detail
  https://help.resilio.com/hc/en-us/articles/204754389-Sync-functionality-in-detail

- Resilio Sync 3.0 change log
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — linked-family owner default, self-observer detour, and seat-role proof after rev0244

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about linked devices, owner default, one-way synchronization limits, read-only workarounds for your own devices, folder-class architecture, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that linked-family convenience is useful while also defaulting all linked devices to owner-grade authority?

> where do those same current docs still show that the ordinary operator answer about `what role does this one of my own devices really have, and how do I intentionally narrow it?` still depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says linked devices automatically share folder visibility, that approvals can be issued from any linked device where the folder is active, and that all folders become available across the linked set.
- Resilio's current `User Management` article, which still says that when you share data across your own devices linked to one identity all of those devices act as Owners.
- Resilio's current `Sync functionality in detail` article, which still repeats shared folder-list visibility and approval convenience across the linked family.
- Resilio's current `Is one-way synchronization possible?` article, which still says Advanced folders do not allow Read Only synchronization across linked devices.
- Resilio's current `How to create a Read Only folder while syncing across linked devices?` article, which still says the workaround uses a Standard folder with a Read Only key, disconnects an already connected folder if needed, and then manually binds the narrower copy.
- Resilio's current `What's the difference between Standard and Advanced folders?` article, which still says Standard and Advanced differ architecturally, only Advanced supports on-the-fly permission changes and Owner, and Standard uses keys while Advanced uses PKI/certificates.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the active v3 line through `3.1.2.1076`.

## Additional Resilio official sources emphasized in rev0245

- Sync Private Identity & Linking My Devices
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- User Management
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- Sync functionality in detail
  https://help.resilio.com/hc/en-us/articles/204754389-Sync-functionality-in-detail

- Is one-way synchronization possible?
  https://help.resilio.com/hc/en-us/articles/204754279-Is-one-way-synchronization-possible

- How to create a Read Only folder while syncing across linked devices?
  https://help.resilio.com/hc/en-us/articles/206216565-How-to-create-a-Read-Only-folder-while-syncing-across-linked-devices

- What's the difference between Standard and Advanced folders?
  https://help.resilio.com/hc/en-us/articles/204754679-What-s-the-difference-between-Standard-and-Advanced-folders

- Resilio Sync 3.0 change log
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — non-authority local edits, destructive auto-heal, and path-local continuity after rev0243

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about Read Only permission behavior, one-way synchronization details, destructive overwrite policy, encrypted-peer constraints, mobile share-detail controls, linked-device ownership semantics, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that non-authority local edits can freeze continuity, auto-heal destructively, or leave local-only residue rather than one simple `read only` story?

> where do those same current docs still show that the ordinary operator answer about `what happens if I edit locally on this non-authority copy?` still depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `User Management` article, which still says Read Only peers cannot propagate local edits and that further synchronization of changed files is suspended unless `Overwrite any changed files` is used.
- Resilio's current `Is one-way synchronization possible?` article, which still spells out per-change-class behavior for rename, delete, edit, and add when overwrite policy is in play.
- Resilio's current `Folder Preferences` article, which still says overwrite is potentially destructive and is disabled for Read-only folders with Selective Sync ON.
- Resilio's current `Folder Types and Management` article, which still says local changes on Read Only folders can stop future updates depending on local settings.
- Resilio's current `Encrypted folders` article, which still says encrypted peers are Read Only, always have overwrite enabled, and do not offer Selective Sync.
- Resilio's current `Sync interface on Android` and `Sync Interface on iOS devices` articles, which still expose overwrite behavior as a per-share control on mobile surfaces.
- Resilio's current `How to create a Read Only folder while syncing across linked devices?` article together with `User Management` and `Is one-way synchronization possible?`, which still show that linked devices act as Owners, Advanced folders do not offer Read Only across linked devices, and a manual Standard-folder / Read-Only-key / disconnect route is still required for that outcome.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0244

- User Management
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- Is one-way synchronization possible?
  https://help.resilio.com/hc/en-us/articles/204754279-Is-one-way-synchronization-possible

- Folder Preferences
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- Folder Types and Management
  https://help.resilio.com/hc/en-us/articles/204762459-Folder-Types-and-Management

- Encrypted folders
  https://help.resilio.com/hc/en-us/articles/207370466-Encrypted-folders

- Sync interface on Android
  https://help.resilio.com/hc/en-us/articles/213500383-Sync-interface-on-Android

- Sync Interface on iOS devices
  https://help.resilio.com/hc/en-us/articles/212016726-Sync-Interface-on-iOS-devices

- How to create a Read Only folder while syncing across linked devices?
  https://help.resilio.com/hc/en-us/articles/206216565-How-to-create-a-Read-Only-folder-while-syncing-across-linked-devices

- Resilio Sync 3.0 change log
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — Archive toggle, replay dependence, and local recovery ceiling after rev0241

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about Archive policy, rename replay through Archive, mobile share-detail controls, retention/access limits, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that `Use Archive` is not just old-version retention, but also part of rename/copy replay behavior and seat-local recovery power?

> where do those same current docs still show that the ordinary operator answer about `what exactly do I lose if I turn Archive off here?` still depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Folder Preferences` article, which still says Archive stores remotely changed or deleted prior versions and that disabling it also makes remote renames or copies re-download instead of replaying locally.
- Resilio's current `What happens when file is renamed` article, which still says remote rename efficiency depends on Archive because the old name is moved to Archive and later restored under the new name when the hash matches.
- Resilio's current `Using Archive for file versioning and restoring deleted files` article, which still says retention defaults differ by desktop and mobile, Android Archive does not work for SD-card shares, and Archive is not accessible on iOS.
- Resilio's current `Sync interface on Android` and `Sync Interface on iOS devices` articles, which still expose `Use Archive` as a per-share control, with iOS explicitly saying renamed files are processed through Archive and Android limiting Archive to internal phone memory.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0242

- Resilio Sync 3.0 change log
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Folder Preferences
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- What happens when file is renamed
  https://help.resilio.com/hc/en-us/articles/209606526-What-happens-when-file-is-renamed

- Using Archive for file versioning and restoring deleted files.
  https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files

- Sync interface on Android
  https://help.resilio.com/hc/en-us/articles/213500383-Sync-interface-on-Android

- Sync Interface on iOS devices
  https://help.resilio.com/hc/en-us/articles/212016726-Sync-Interface-on-iOS-devices

## Revision addendum — timestamp winner authority, clock confidence, and loser-preservation proof after rev0240

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about pre-populated same-path divergence, chronology trust, offline-return priority, Archive restore timing, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that winner choice often rides on timestamp ordering, offline-return rules, and Archive preservation rather than one abstract `conflict resolved` story?

> where do those same current docs still show that the ordinary operator answer about `why is this version winning, how trustworthy is that ranking, and where did the loser go?` still depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Can I connect two pre-populated pre-existing folders?` article, which still says same-hash files are not re-synced, differing-content same-path files let the latest timestamp win, and the operator still clicks `OK` on a non-empty-folder confirmation.
- Resilio's current `What if several people make changes to the same file?` article, which still says online edits usually replay in chronological order but an offline peer returning later can still take priority, with overwritten versions moved to Archive.
- Resilio's current `Time difference` article, which still says Sync decides which file is newer by comparing modification times converted to GMT, that more than 600 seconds of drift triggers warnings, and that mobile devices may show empty lists.
- Resilio's current `Using Archive for file versioning and restoring deleted files` article, which still says restoring while Sync is not running can cause the restored older file to be archived again on rescan, and that Archive itself does not tell you which peer made the change.
- Resilio's current v3 change log, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0241

- Can I connect two pre-populated pre-existing folders?
  https://help.resilio.com/hc/en-us/articles/205506569-Can-I-connect-two-pre-populated-pre-existing-folders

- What if several people make changes to the same file?
  https://help.resilio.com/hc/en-us/articles/204754209-What-if-several-people-make-changes-to-the-same-file

- "Time difference" error
  https://help.resilio.com/hc/en-us/articles/204753599--Time-difference-error

- Using Archive for file versioning and restoring deleted files.
  https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files

- Resilio Sync 3.0 change log
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — safe reconnect, risky merge, and overloaded `Folder not empty` warnings after rev0239

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about `Folder not empty`, pre-populated pre-existing folders, reconnect path proposals, `Add anyway` prompts, manual location choice on linked devices, and the active v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that both safe reconnect and risky merge are real non-empty-target cases?

> where do those same current docs still show that the ordinary operator answer about `am I restoring the old tree or merging into a risky existing one?` still depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Folder not empty` article, which still says the same warning appears both when adding shared files into an already existing folder and when reconnecting a folder to a location where it synced before; still warns that existing files in the receiving folder might be deleted or overwritten; and still says to ignore the warning and proceed when reconnecting to the old location.
- Resilio's current `Can I connect two pre-populated pre-existing folders?` article, which still says click `OK` on the non-empty confirmation and, on linked devices, often use `Disconnected` posture or disconnect/reconnect ritual before selecting the existing directory.
- Resilio's current `Disconnecting and Removing Folders` article, which still says reconnect may propose a different default path, may create a `(1)` sibling, and may again ask Android to accept `Destination folder is not empty. Add anyway?`
- Resilio's current `How to manually set the location of the folders synced across linked devices?` article, which still says custom placement for linked-device arrivals is reached by putting the seat into `Disconnected` mode first.
- Resilio's current `Synchronization Modes` article, which still anchors the linked-device `Disconnected` / `Selective Sync` / `Synced` posture used in the surrounding path ritual.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the active v3 line through `3.1.2.1076`.

## Additional Resilio official sources emphasized in rev0240

- Folder not empty
  https://help.resilio.com/hc/en-us/articles/204753689-Folder-not-empty

- Can I connect two pre-populated pre-existing folders?
  https://help.resilio.com/hc/en-us/articles/205506569-Can-I-connect-two-pre-populated-pre-existing-folders

- Disconnecting and Removing Folders
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- How to manually set the location of the folders synced across linked devices?
  https://help.resilio.com/hc/en-us/articles/206216615-How-to-manually-set-the-location-of-the-folders-synced-across-linked-devices

- Synchronization Modes
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- Resilio Sync 3.0 change log
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — current default-root policy, reconnect path, and duplicate-suffix fallback after rev0238

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about linked-device default connect mode, manual location choice for incoming shares, reconnect path proposals, default-folder / Simple Mode auto-placement, duplicate-name `(1)` fallback, and the current split v2/v3 release-history pages.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that future-arrival defaults, default roots, reconnects, and existing local directories materially shape path placement?

> where do those same current docs still show that the ordinary operator answer about `how do I safely place this one share?` still depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Synchronization Modes` article, which still says linked devices use `Disconnected`, `Selective Sync`, and `Synced`, and still ties device-level mode to future linked-device arrivals.
- Resilio's current `How to manually set the location of the folders synced across linked devices?` article, which still says `Selective Sync` and `Synced` put new folders into the default folder and that the operator should switch the device to `Disconnected` to choose custom location for later arrivals.
- Resilio's current `Disconnecting and Removing Folders` article, which still says reconnect may propose a default path different from the original one, may create a `(1)` duplicate, and may ask Android to `Add anyway` for a non-empty target.
- Resilio's current `Settings on mobile platforms` and `Simple Mode (Android)` articles, which still say default folder / Simple Mode auto-place new Android shares and add `(1)` on same-name collision.
- Resilio's current `Resilio Sync 3.0 change log` and `supported platforms and system requirements` pages, which still show the active v3 line through `3.1.2.1076`.
- Resilio's older `Resilio Sync change log` page, which now functions as the previous-versions history and still tops out at `2.8.1.1390`.

## Additional Resilio official sources emphasized in rev0239

- Resilio Sync 3.0 change log
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Resilio Sync: supported platforms and system requirements
  https://help.resilio.com/hc/en-us/articles/205450965-Resilio-Sync-supported-platforms-and-system-requirements

- Synchronization Modes
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- How to manually set the location of the folders synced across linked devices?
  https://help.resilio.com/hc/en-us/articles/206216615-How-to-manually-set-the-location-of-the-folders-synced-across-linked-devices

- Disconnecting and Removing Folders
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- Settings on mobile platforms
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- Simple Mode (Android)
  https://help.resilio.com/hc/en-us/articles/205458155-Simple-Mode-Android

- Resilio Sync change log
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log

## Revision addendum — current-share posture, future-default meaning, and clear/disconnect return contract after rev0237

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about synchronization modes, placeholder files, linked-device defaults, mobile share details, disconnect/reconnect behavior, default-folder placement, duplicate-path fallback, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that `Disconnected`, `Selective Sync`, and `Synced` are useful but overloaded operator concepts?

> where do those same current docs still show that the ordinary operator answer about `what does this mode mean now`, `what does it imply for future arrivals`, and `what exactly survives clear or disconnect` still depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Sync functionality in detail` article, which still says linked devices expose `Disconnected`, `Selective Sync`, and `Synced` as three modes and ties Selective Sync to placeholder-based on-demand access.
- Resilio's current `Synchronization Modes` and `Sync Preferences` articles, which still say device-level default connect mode and default folder path govern how later linked-device arrivals land.
- Resilio's current `What Is an RSLS File?` article, which still says placeholders are zero-byte proxies created by Selective Sync or Connected mode and distinguishes `Remove from this device` from `Remove from all devices`.
- Resilio's current Android and iOS interface articles, which still say `Clear` or `Clear synced files` revert local files to placeholders and still expose `Disconnect`/`Remove from this device` as separate actions.
- Resilio's current `Disconnecting and Removing Folders`, `How to manually set the location of the folders synced across linked devices`, `Folders are duplicating with an index (i) in their name`, `Settings on mobile platforms`, and `Simple Mode (Android)` articles, which still say disconnect preserves the folder, reconnect may propose a different path, default placement can create `(1)` duplicates, and mobile default-folder policy can silently choose arrival paths.
- Resilio's current v3 change log, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0238

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Sync functionality in detail  
  https://help.resilio.com/hc/en-us/articles/204754389-Sync-functionality-in-detail

- Synchronization Modes  
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- What Is an RSLS File?  
  https://help.resilio.com/hc/en-us/articles/206115384-What-Is-an-RSLS-File

- Sync interface on Android  
  https://help.resilio.com/hc/en-us/articles/213500383-Sync-interface-on-Android

- Sync Interface on iOS devices  
  https://help.resilio.com/hc/en-us/articles/212016726-Sync-Interface-on-iOS-devices

- Disconnecting and Removing Folders  
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- How to manually set the location of the folders synced across linked devices  
  https://help.resilio.com/hc/en-us/articles/206216615-How-to-manually-set-the-location-of-the-folders-synced-across-linked-devices

- Folders are duplicating with an index (i) in their name.  
  https://help.resilio.com/hc/en-us/articles/204753869-Folders-are-duplicating-with-an-index-i-in-their-name

- Settings on mobile platforms  
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- Simple Mode (Android)  
  https://help.resilio.com/hc/en-us/articles/205458155-Simple-Mode-Android

## Revision addendum — rule-agreement truth, ignore-ledger shared meaning, and exclusion claim ceilings after rev0236

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about IgnoreList semantics, troubleshooting language about peer agreement, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that ignore rules affect indexing, accounting, case/path matching, and retroactivity in real ways?

> where do those same current docs still show that the ordinary operator answer about `do these peers actually mean the same thing by ignored?` still depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Ignoring files in Sync (Ignore List)` article, which still says excluded files are not indexed and not counted in the Size column, still calls matching lists `advisable, but not compulsory`, still says IgnoreList is case sensitive, still notes OS-specific path delimiters, and still says rules do not affect already-synced files while structural information is still passed until disconnect.
- Resilio's current `My files don't sync` article, which still says the Ignore list must be the same on all peers so they all agree on what shall be skipped.
- Resilio's current v3 change log, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0237

- Ignoring files in Sync (Ignore List)
  https://help.resilio.com/hc/en-us/articles/205458165-Ignoring-files-in-Sync-Ignore-List

- My files don't sync
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Resilio Sync 3.0 change log
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — metric-window truth, status-row overclaim, and timestamp claim ceilings after rev0235

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about the desktop main view, mobile/details surfaces, still-official historical change-log semantics for row columns, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that counters and timestamps speak about different windows rather than one generic `status now` truth?

> where do those same current docs still show that the ordinary operator answer about `what does this row really prove` still depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Sync Main View (Desktop)` article, which still says green check means synced with all connected peers, still defines `X of Y peers` as online-now vs total-including-offline, and still says offline peers are disconnected from the folder after 7 days by default.
- Resilio's still-official `Sync functionality in detail` article, which still says mobile folder details show size, number of files, and `last synced date`.
- Resilio's still-official older change log, which still says the optional `Last transferred` column means the last time files were changed in a folder, and still records fixes for misleading `Date synced`, peer-list, and receiving-stat accuracy.
- Resilio's current v3 change log, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0236

- Sync Main View (Desktop)
  https://help.resilio.com/hc/en-us/articles/204755009-Sync-Main-View-Desktop

- Sync functionality in detail
  https://help.resilio.com/hc/en-us/articles/204754389-Sync-functionality-in-detail

- Resilio Sync change log
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log

- Resilio Sync 3.0 change log
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — mobile network eligibility, forbidden-network stoppage, and sleep-vs-policy truth after rev0233

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about mobile settings, per-share allowed-network rules, Android share interface affordances, Android auto-sleep / battery saver, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that a share can be present on the seat yet policy-ineligible on the current network?

> where do those same current docs still show that the ordinary operator answer about `is this blocked by seat policy, share policy, or sleeping core`, `does detection still happen`, and `what future condition will wake this back up` still depends on hopping across several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Settings on mobile platforms` article, which still says `Use mobile data` controls whether Sync transfers when only mobile data is available, and still separates network, notifications, and battery-related behavior on mobile.
- Resilio's current `Setting network interface per share` article, which still defines `Any network`, `Wi‑Fi only`, and `Custom`, and still says `Stopped. Forbidden network` means peers will not connect for that share and new or updated files will not be detected.
- Resilio's current `Sync interface on Android` article, which still exposes `Allowed network` in share details.
- Resilio's current `Configuring Auto Sleep & Battery Saver (Android)` article, which still says the core can stop so peers no longer see the device online, and that wake intervals control when checks resume.
- Resilio's current v3 change log, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0234

- Settings on mobile platforms  
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- Setting network interface per share  
  https://help.resilio.com/hc/en-us/articles/360001411244-Setting-network-interface-per-share

- Sync interface on Android  
  https://help.resilio.com/hc/en-us/articles/213500383-Sync-interface-on-Android

- Configuring Auto Sleep & Battery Saver (Android)  
  https://help.resilio.com/hc/en-us/articles/204762699-Configuring-Auto-Sleep-Battery-Saver-Android

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — control-endpoint attribution, browser target, and runtime watermark after rev0231

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about WebUI defaults, Linux multi-instance launches, storage-root and config-path ownership, Windows service install/migrate behavior, password-reset collateral effects, browser warning handling, and the current v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that a browser/admin endpoint is not automatically one stable runtime world?

> where do those same current docs still show that the ordinary operator answer about `which runtime am I controlling right now` still depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current v3 change log, which still shows the live `3.1.2.1076` line.
- `Configuring WebUI`, which still distinguishes host-class defaults, config-owned listener changes, LAN widening via `0.0.0.0`, optional workstation password, self-signed HTTPS, and manual browser-link fallback in WebUI.
- `Guide to Linux, and Sync peculiarities`, which still says Linux has no GUI, can run multiple instances, requires manually separated ports for later instances, can define storage explicitly, and can shut down immediately if forced to bind WebUI to an unavailable interface.
- `Running Sync as a service on Windows`, which still distinguishes migrated versus clean service install and says the service opens WebUI in a new browser tab.
- `Running Sync in configuration mode`, which still says non-default `storage_path` creates settings there, service config mode must use the service storage, and storage path holds settings / logs / identity details.
- `Is there a Command Line Interface (CLI) for Resilio Sync on Windows?`, which still documents `/config` and `/noinstall` as launch-time namespace selectors.
- `How do I reset my WebUI password?`, which still distinguishes deleting settings files from config-enforced credentials, including duplication/default-reset collateral on one path and lower collateral on the other.
- `Browser warning "Your connection is not private"`, which still distinguishes self-signed HTTPS posture, temporary click-through, HSTS/browser residue, and user-provided certificates.

## Additional Resilio official sources emphasized in rev0232

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Configuring WebUI  
  https://help.resilio.com/hc/en-us/articles/115001184490-Configuring-WebUI

- Guide to Linux, and Sync peculiarities  
  https://help.resilio.com/hc/en-us/articles/204762449-Guide-to-Linux-and-Sync-peculiarities

- Running Sync as a service on Windows  
  https://help.resilio.com/hc/en-us/articles/207701296-Running-Sync-as-a-service-on-Windows

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Is there a Command Line Interface (CLI) for Resilio Sync on Windows?  
  https://help.resilio.com/hc/en-us/articles/205506359-Is-there-a-Command-Line-Interface-CLI-for-Resilio-Sync-on-Windows

- How do I reset my WebUI password?  
  https://help.resilio.com/hc/en-us/articles/205450295-How-do-I-reset-my-WebUI-password

- Browser warning "Your connection is not private"  
  https://help.resilio.com/hc/en-us/articles/4404757430291-Browser-warning-Your-connection-is-not-private

## Revision addendum — same-host instance namespace, sibling runtime identity, and overlap admission after rev0230

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about Linux multiple instances, CLI/config storage roots, Windows service-account storage divergence, v3 upgrade preservation rules, and overlap-driven `Service files missing` repair.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that same-host runtimes are materially distinct namespaces rather than one flat `device`?

> where do those same current docs still show that the ordinary operator answer about `am I reopening the same seat`, `which storage root is authoritative`, and `is this attach safe or overlap-corrupting` still depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current v3 change log, which still shows the live `3.1.2.1076` line.
- `Guide to Linux, and Sync peculiarities`, which still says Linux can run multiple instances, that later instances need manual port assignment, that storage defaults to a local `.sync` directory if not specified, and that web UI bind choices can also affect liveness.
- `Is there a Command Line Interface (CLI) for Resilio Sync on Windows?`, which still documents `/config`, `/storage`, `/noinstall`, and other launch-time namespace-defining switches.
- `Running Sync in configuration mode`, which still says `storage_path` creates settings there, config-mode service launches must use the service storage, and config mode supports only Standard folders.
- `Running Sync as a service on Windows`, `Sync Storage folder`, and `Sync Service Troubleshooting on Windows`, which still show that service account choice changes the active storage root and can surface a new empty share roster that then requires re-add / reconnect work.
- `Updating installation to Resilio Sync v3`, which still says non-default `/config` or `/storage` users should relaunch with the same parameters and the same user to preserve configuration.
- `Service files missing / Cannot identify destination folder` and `What is '.sync' folder...`, which still say continuity-bearing hidden state is critical and that two instances on the same computer (or external storage reused by two instances) can corrupt it.
- `Selected folder is already added to Sync`, which still says a device cannot host two folders with the same `.sync/ID` at once.

## Additional Resilio official sources emphasized in rev0231

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Guide to Linux, and Sync peculiarities  
  https://help.resilio.com/hc/en-us/articles/204762449-Guide-to-Linux-and-Sync-peculiarities

- Is there a Command Line Interface (CLI) for Resilio Sync on Windows?  
  https://help.resilio.com/hc/en-us/articles/205506359-Is-there-a-Command-Line-Interface-CLI-for-Resilio-Sync-on-Windows

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Running Sync as a service on Windows  
  https://help.resilio.com/hc/en-us/articles/207701296-Running-Sync-as-a-service-on-Windows

- Sync Storage folder  
  https://help.resilio.com/hc/en-us/articles/206664690-Sync-Storage-folder

- Sync Service Troubleshooting on Windows  
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

- Updating installation to Resilio Sync v3  
  https://help.resilio.com/hc/en-us/articles/31194252837779-Updating-installation-to-Resilio-Sync-v3

- Service files missing / Cannot identify destination folder  
  https://help.resilio.com/hc/en-us/articles/205450225-Service-files-missing-Cannot-identify-destination-folder

- What is '.sync' folder, and StreamsList, IgnoreList and Archive inside  
  https://help.resilio.com/hc/en-us/articles/206217185-What-is-sync-folder-and-StreamsList-IgnoreList-and-Archive-inside

- Selected folder is already added to Sync  
  https://help.resilio.com/hc/en-us/articles/209316526-Selected-folder-is-already-added-to-Sync

## Revision addendum — policy provenance, hidden overrides, and surface-split authority after rev0229

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about visible preferences, folder-level preferences, power-user overrides, and configuration-mode ownership.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that the real rule plane is layered rather than flat?

> where do those same current docs still show that the ordinary operator answer about `what rule is actually winning`, `which surface owns it`, and `whether this control is descriptive or authoritative` still depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current v3 change log, which still shows the live `3.1.2.1076` line.
- Resilio's current `Sync Preferences` article, which still shows visible global settings and still points to power-user preferences for semantically important LAN-rate behavior.
- Resilio's current `Folder Preferences` article, which still shows per-folder archive / overwrite / relay / tracker / LAN / predefined-host behavior.
- Resilio's current `Power user preferences` article, which still documents semantically heavy deep flags such as bind-interface forcing, Archive limits, watcher / notification behavior, placeholder-removal behavior, conflict-path handling, and LAN encryption.
- Resilio's current `Running Sync in configuration mode` article, which still says Advanced Preferences can be added to config, shared folders in config override prior WebUI folders, shared folders in config disable WebUI, and config mode supports only Standard folders.

## Additional Resilio official sources emphasized in rev0230

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Folder Preferences  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

## Revision addendum — control-surface grade, audience, auth, transport, and trust posture after rev0228

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about WebUI default listener scope, password policy differences, HTTP/HTTPS posture, self-signed certificate handling, config-mode control ownership, password-reset side effects, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that control surfaces have materially different grades?

> where do those same current docs still show that the ordinary operator answer about `who can reach this`, `what actually protects it`, `what warning is browser residue versus endpoint truth`, and `which recovery path preserves broader state` still depends on hopping across several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current v3 change log, which still shows the live `3.1.2.1076` line.
- Resilio's current `Configuring WebUI` article, which still states the default loopback listener, optional workstation password, compulsory NAS password, session-cookie lifetime, HTTP default, HTTPS / self-signed posture, and browser-link intake caveat.
- Resilio's current `Guide to Linux, and Sync peculiarities` article, which still states loopback-only default for security, LAN reach via `0.0.0.0`, optional password on Linux, and bind-loss shutdown risk when forcing a specific interface.
- Resilio's current `Browser warning "Your connection is not private"` article, which still distinguishes self-signed cert warning, click-through, HSTS-clearing / `thisisunsafe`, and custom trusted certificate in config mode.
- Resilio's current `How do I reset my WebUI password?` article, which still distinguishes storage-file deletion with preference reset and device duplication from config-file credential recovery with lower collateral impact.
- Resilio's current `Running Sync in configuration mode` article, which still documents password hashes, custom certificate material, config-owned storage roots, and disabling WebUI when shared folders are declared in config.

## Additional Resilio official sources emphasized in rev0229

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Configuring WebUI  
  https://help.resilio.com/hc/en-us/articles/115001184490-Configuring-WebUI

- Guide to Linux, and Sync peculiarities  
  https://help.resilio.com/hc/en-us/articles/204762449-Guide-to-Linux-and-Sync-peculiarities

- Browser warning "Your connection is not private"  
  https://help.resilio.com/hc/en-us/articles/4404757430291-Browser-warning-Your-connection-is-not-private

- How do I reset my WebUI password?  
  https://help.resilio.com/hc/en-us/articles/205450295-How-do-I-reset-my-WebUI-password

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

## Revision addendum — recovery horizon, retention decay, and access half-life after rev0222

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about Archive retention defaults, size-based versioning ceilings, platform access differences, desktop History window, hidden `.sync` storage, uninstall residue, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that recovery evidence has different lifetimes and different reach depending on seat, platform, and policy?

> where do those same current docs still show that the ordinary operator answer about `how long recovery evidence remains usable`, `what surface can still reach it`, `what policy excluded it`, and `what residue survives app removal` still depends on hopping across several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current v3 change log, which still shows the live `3.1.2.1076` line.
- Resilio's current `Using Archive for file versioning and restoring deleted files` article, which still gives the default Archive horizons, configurable TTL, size ceiling, mobile / iOS / Android SD-card caveats, and manual restore mechanics.
- Resilio's current `Sync Main View (Desktop)` article, which still says History shows general syncing activity for the last 30 days.
- Resilio's current `What is '.sync' folder, and StreamsList, IgnoreList and ...` article, which still places Archive inside the hidden `.sync` control folder.
- Resilio's current `How to uninstall Sync?` article, which still says uninstall does not remove archived files automatically and manual hidden-folder cleanup is needed.

## Additional Resilio official sources emphasized in rev0223

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Using Archive for file versioning and restoring deleted files  
  https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files

- Sync Main View (Desktop)  
  https://help.resilio.com/hc/en-us/articles/204755009-Sync-Main-View-Desktop

- What is '.sync' folder, and StreamsList, IgnoreList and ...  
  https://help.resilio.com/hc/en-us/articles/206217185-What-is-sync-folder-and-StreamsList-IgnoreList-and-Archive-inside

- How to uninstall Sync?  
  https://help.resilio.com/hc/en-us/articles/204775029-How-to-uninstall-Sync

## Revision addendum — rollback witness locality, archive-bearing asymmetry, and recovery host choice after rev0221

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about Archive placement, manual restoring, runtime replay caveats, rename handling through Archive, History visibility, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that previous-version witnesses are not kept everywhere equally?

> where do those same current docs still show that the ordinary operator answer about `which seat has the bytes`, `which seat should perform the restore`, `what proof still comes from History`, and `what surface can reach the witness` still depends on hopping across several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current v3 change log, which still shows the live `3.1.2.1076` line.
- Resilio's current `Using Archive for file versioning and restoring deleted files` article, which still says prior versions land on other peers, restore is manual, runtime liveness matters, retention defaults differ by platform, iOS lacks Archive access, and Archive does not identify the acting peer.
- Resilio's current `What happens when file is renamed` article, which still says Archive is used on remote peers to move the old name aside and restore it under the new name without re-transfer when the hash matches.
- Resilio's current `Sync Main View (Desktop)` article, which still says History shows general syncing activity for the last 30 days and therefore still acts as the operator-facing event lane that complements Archive.

## Additional Resilio official sources emphasized in rev0222

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Using Archive for file versioning and restoring deleted files  
  https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files

- What happens when file is renamed  
  https://help.resilio.com/hc/en-us/articles/209606526-What-happens-when-file-is-renamed

- Sync Main View (Desktop)  
  https://help.resilio.com/hc/en-us/articles/204755009-Sync-Main-View-Desktop

## Revision addendum — pause, scheduler, and partial-stop truth after rev0220

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about pause semantics, scheduler semantics, and the still-published fix history around paused-state indexing.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that `pause` is only a partial stop?

> where do those same current docs still show that the ordinary operator answer about `what actually stopped`, `what is still alive`, and `is this safe for maintenance-grade quiet?` still depends on hopping across several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current v3 change log, which still shows the live `3.1.2.1076` line.
- Resilio's current `How to pause syncing` article, which still says pause stops only bits uploads/downloads while deletions, zero-sized files, and rescans continue.
- Resilio's current `Running Sync on schedule` article, which still treats `Paused` as a partial stop rather than a universal freeze and still describes residual paused-peer behavior in a way operators may need to reconcile with the ordinary pause article.
- Resilio's still-published historical change log, which still records a fix for paused-state indexing behavior.

## Additional Resilio official sources emphasized in rev0221

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- How to pause syncing  
  https://help.resilio.com/hc/en-us/articles/206217325-How-to-pause-syncing

- Running Sync on schedule  
  https://help.resilio.com/hc/en-us/articles/210783266-Running-Sync-on-schedule

- Resilio Sync change log  
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log

## Revision addendum — seat posture change mechanism, rebind class, and derivative cascades

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about live permission edits, Standard-folder mutation limits, linked-seat read-only workaround, local-share derivative rules, and the active v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that posture changes are not all the same kind of operation?

> where do those same current docs still show that the ordinary operator answer about `can I change this live?`, `is this really a rebind?`, `what descendants will auto-narrow or disappear?`, and `is this request blocked by class?` still depends on hopping across several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current v3 change log, which still shows the live `3.1.2.1076` line.
- Resilio's current `User Management` article, which still says live permission changes are available only for Advanced folders, linked devices act as Owners, and disconnect stops future updates but not already-landed files.
- Resilio's current `What's the difference between Standard and Advanced folders?` article, which still says Standard folders do not support on-the-fly permission changes and need removal plus re-add with a new key.
- Resilio's current `How to create a Read Only folder while syncing across linked devices?` article, which still documents the disconnect-plus-manual-rebind ritual for narrowing one linked seat to read-only.
- Resilio's current `Sharing a folder locally` article, which still says local shares cannot receive Owner, cannot change access through user management, must be removed and re-shared to change permission, narrow automatically with the source, and do not reconnect automatically after source removal.

## Additional Resilio official sources emphasized in rev0218

- Resilio Sync 3.0 change log
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- User Management
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- What's the difference between Standard and Advanced folders?
  https://help.resilio.com/hc/en-us/articles/204754679-What-s-the-difference-between-Standard-and-Advanced-folders

- How to create a Read Only folder while syncing across linked devices?
  https://help.resilio.com/hc/en-us/articles/206216565-How-to-create-a-Read-Only-folder-while-syncing-across-linked-devices

- Sharing a folder locally
  https://help.resilio.com/hc/en-us/articles/360011582500-Sharing-a-folder-locally

## Revision addendum — ciphertext custody, encrypted target admission, and recovery prerequisites

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about encrypted folders on untrusted machines, ordinary pre-populated folder connection, read-only overwrite semantics, and the active v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid about ciphertext-only custody and its hard ceilings?

> where do those same current docs still show that the ordinary operator answer about `is this target safe?`, `can this node ever produce plaintext?`, `what exact materials must survive for later recovery?`, and `why can't encrypted Archive replay a deleted file from here?` still depends on hopping across several docs instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current v3 change log, which still shows the live `3.1.2.1076` line.
- Resilio's current `Encrypted folders` article, which still frames opaque custody on untrusted hosts as a real pattern, still requires a freshly created directory, still warns about same-F-key residue moving into Archive, still keeps encrypted nodes read-only and non-selective, still limits onward share to encrypted format, and still makes recovery depend on saved RW/RO keys plus database continuity or an explicit CLI decrypt lane.
- Resilio's current `Is one-way synchronization possible?` article, which still explains the real semantics of read-only peers and `Overwrite any changed files`.
- Resilio's current `Can I connect two pre-populated pre-existing folders?` article, which still helps show how different ordinary pre-populated admission is from encrypted-target admission.

## Additional Resilio official sources emphasized in rev0212

- Resilio Sync 3.0 change log
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Encrypted folders
  https://help.resilio.com/hc/en-us/articles/207370466-Encrypted-folders

- Is one-way synchronization possible?
  https://help.resilio.com/hc/en-us/articles/204754279-Is-one-way-synchronization-possible

- Can I connect two pre-populated pre-existing folders?
  https://help.resilio.com/hc/en-us/articles/205506569-Can-I-connect-two-pre-populated-pre-existing-folders

## Revision addendum — volume capability, metadata fidelity, affordance ceilings, and degraded repair

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about alternate streams and xattrs, shell/context-menu prerequisites, hidden sidecars in `.sync`, and the still-published fix history around FAT32, exFAT, CIFS/SMB, and xattr delivery.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid about target-volume capability and metadata fallback?

> where do those same current docs still show that the ordinary operator answer about `what can this target really carry?`, `is metadata native or stub-backed?`, `why is this action absent?`, and `should I migrate or reformat this subject?` still depends on hopping across several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current v3 change log, which still shows the live `3.1.2.1076` line and still records a 3.0.3 fix for missing Selective Sync context-menu items on macOS.
- Resilio's current `Alt Streams and Xattrs in Sync` article, which still keeps StreamsList as a real whitelist, still names FAT32 / Linux / macOS limits, still explains `.sync/Streams` fallback stubs, and still says IgnoreList does not control xattr carriage.
- Resilio's current `No Sync icons in the file browser...` article, which still says Windows context-menu items appear only on NTFS because that filesystem supports alternate data streams, and still treats extension registration as a separate prerequisite.
- Resilio's current `.sync folder` article, which still names StreamsList and `.!sync` as product-owned hidden state rather than hand-waving them away.
- Resilio's still-published historical change log, which still records concrete filesystem-edge fixes and failures such as FAT32 log flooding, exFAT attribute trouble, CIFS/SMB no-stream weirdness, and xattr-delivery problems on Linux.

## Additional Resilio official sources emphasized in rev0211

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Alt Streams and Xattrs in Sync  
  https://help.resilio.com/hc/en-us/articles/204754729-Alt-Streams-and-Xattrs-in-Sync

- No Sync icons in the file browser/no Sync-related items in the context menu on Mac/Windows  
  https://help.resilio.com/hc/en-us/articles/206214625-No-Sync-icons-in-the-file-browser-no-Sync-related-items-in-the-context-menu-on-Mac-Windows

- What is '.sync' folder, and StreamsList, IgnoreList and Archive inside?  
  https://help.resilio.com/hc/en-us/articles/206217185-What-is-sync-folder-and-StreamsList-IgnoreList-and-Archive-inside

- Resilio Sync change log  
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log

## Revision addendum — publication readiness, authoring delay, touch repair, and inbound priority

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about change detection, periodic rescans, delay-time policy, locked files, manual `touch` repair, and the newer file-download-priority feature.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid about why `sync now` may really mean `detect`, `wait`, `unlock`, `nudge freshness`, or `queue differently`?

> where do those same current docs still show that the ordinary operator answer about `is this ready`, `why is this waiting`, `should I touch this`, and `why is this not first` still depends on hopping across several docs instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current v3 change log, which still shows the live `3.1.2.1076` line and records the introduction of file download priority in `3.1.0.1073`.
- Resilio's current `How soon does synchronization start?` FAQ, which still explains filesystem notifications, default 600-second rescans, zero-rescan behavior, and manual rescan.
- Resilio's current `Setting Delay Time For Syncing` article, which still places file-class delay policy in `FileDelayConfig` in the storage folder and still requires restart.
- Resilio's current `How to touch files?` article, which still openly recommends manual mtime nudges when mtime or size did not change or were not noticed.
- Resilio's current `Locked files` article, which still shows clickable locked-file status but still leaves application attribution and recovery partly manual.
- Resilio's current `File download priority` page, which still explains per-share and global priority, sticky manual override behavior, 50k active-queue limits, suspension exceptions, non-splittable-transfer limits, and visible-vs-actual order mismatch.
- Resilio's current power-user and watcher-warning docs, which still connect rescan cadence, low-level defaults, and degraded detection coverage.

## Additional Resilio official sources emphasized in rev0202

- Resilio Sync 3.0 change log
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- How soon does synchronization start?
  https://help.resilio.com/hc/en-us/articles/204754319-How-soon-does-synchronization-start

- Setting Delay Time For Syncing
  https://help.resilio.com/hc/en-us/articles/207491426-Setting-Delay-Time-For-Syncing

- How to touch files?
  https://help.resilio.com/hc/en-us/articles/209606046-How-to-touch-files

- Locked files
  https://help.resilio.com/hc/en-us/articles/205504549-Locked-files

- File download priority
  https://help.resilio.com/hc/en-us/articles/42328167759251-File-download-priority

- Power user preferences
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Agent run out of system notify watchers. Updated files will be uploaded only after periodic folder rescan
  https://help.resilio.com/hc/en-us/articles/360015593120-Agent-run-out-of-system-notify-watchers-Updated-files-will-be-uploaded-only-after-periodic-folder-rescan

## Revision addendum — capability availability, entitlement provenance, and Pro-function loss

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about repeated feature-availability notes, folder-class capability splits, local-share entitlement cliffs, Business owner/seat provenance, lost-license recovery, and v3 licensing FAQ guidance.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid about feature gating and entitlement provenance?

> where do those same current docs still show that the ordinary operator answer about `can I do this here?`, `why do I have this right?`, `why is this control absent?`, and `what just stopped working?` still depends on hopping across several feature pages and support notes instead of one stable product-owned page?

The most load-bearing source set for this pass was:

- Resilio's current Selective Sync, My Devices, User Management, and single-file-sharing docs, which still repeat explicit `Feature availability depending on version` notes for v2 licensed builds versus v3.
- Resilio's current Standard-versus-Advanced comparison, which still ties capability ceilings to subject family rather than just seat entitlement.
- Resilio's current local-share docs, which still say the feature is desktop-only, Pro-only, and stops working when trial or license posture is lost.
- Resilio's current license-application and seat-sharing docs, which still distinguish Home / Family from Business owner and shared-seat behavior and still warn that applying the key elsewhere can steal owner status.
- Resilio's current Business-expiry, lost-license, and unsupported-server warning docs, which still show that capability loss can propagate, seats can revert to Free, and some host-role mismatches still narrow effective behavior even when a key was applied.
- Resilio's current v3 FAQ, which still ties non-commercial use, personal-device reuse, family-sharing limits, and Business non-upgrade boundaries into the effective entitlement story.

## Additional Resilio official sources emphasized in rev0200

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Selective Sync  
  https://help.resilio.com/hc/en-us/articles/205458095-Selective-Sync

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- User Management  
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- Sharing single file  
  https://help.resilio.com/hc/en-us/articles/115000401010-Sharing-single-file

- What's the difference between Standard and Advanced folders?  
  https://help.resilio.com/hc/en-us/articles/204754679-What-s-the-difference-between-Standard-and-Advanced-folders

- Sharing a folder locally  
  https://help.resilio.com/hc/en-us/articles/360011582500-Sharing-a-folder-locally

- How to apply license key and share license seats  
  https://help.resilio.com/hc/en-us/articles/204762369-How-to-apply-license-key-and-share-license-seats

- What happens when Sync Business trial or license expires?  
  https://help.resilio.com/hc/en-us/articles/206216825-What-happens-when-Sync-Business-trial-or-license-expires

- My device has lost the license and Sync has reverted to the Free version. How can I return the Pro functionality?  
  https://help.resilio.com/hc/en-us/articles/204753499-My-device-has-lost-the-license-and-Sync-has-reverted-to-the-Free-version-How-can-I-return-the-Pro-functionality

- "Your Sync Business license doesn't support Windows Server or Linux (x86 or x64)."  
  https://help.resilio.com/hc/en-us/articles/115000651390--Your-Sync-Business-license-doesn-t-support-Windows-Server-or-Linux-x86-or-x64

- FAQ Resilio Sync 3.0.0  
  https://help.resilio.com/hc/en-us/articles/32109883606035-FAQ-Resilio-Sync-3-0-0

## Revision addendum — placeholder materialization, local reclaim, delete scope, and archive replay

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about synchronization modes, Selective Sync, placeholders, disconnect behavior, Archive retention, and overwrite / replay caveats.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid about selective materialization, local reclaim, and retained-history pragmatism?

> where do those same current docs still show that the ordinary operator answer about `what will this fetch do?`, `is this local reclaim or global delete?`, and `will this restore replay or re-archive?` still depends on hopping across several guides and FAQs instead of one stable product-owned page?

The most load-bearing source set for this pass was:

- Resilio's current synchronization-mode and Selective Sync docs, which still distinguish disconnected, placeholder-first, and fully-synced postures and still say subtree fetch affects future descendants.
- Resilio's current RSLS / placeholder docs, which still say `Remove from this device` reverts locally while deleting a placeholder with Read & Write access removes it from all peers.
- Resilio's current disconnect docs, which still say disconnect is one-device-only, keeps the folder in the file system, but removes placeholder files on selective-sync subjects.
- Resilio's current Archive docs, which still say restore is manual, retention is time-bounded, and replay can fail back into Archive if runtime timing is wrong.
- Resilio's current overwrite and pre-populated-folder docs, which still say latest online return / latest timestamp can overwrite peer work and place the overwritten version in Archive.

## Additional Resilio official sources emphasized in rev0193

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Synchronization Modes  
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- Selective Sync  
  https://help.resilio.com/hc/en-us/articles/205458095-Selective-Sync

- What Is an RSLS File?  
  https://help.resilio.com/hc/en-us/articles/206115384-What-Is-an-RSLS-File

- Disconnecting and Removing Folders  
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- Using Archive for file versioning and restoring deleted files.  
  https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files

- What if several people make changes to the same file?  
  https://help.resilio.com/hc/en-us/articles/204754209-What-if-several-people-make-changes-to-the-same-file

- Can I connect two pre-populated pre-existing folders?  
  https://help.resilio.com/hc/en-us/articles/205506569-Can-I-connect-two-pre-populated-pre-existing-folders

## Revision addendum — seat lineage, destructive linking, duplicate rows, and reset/rehome boundaries

This revision intentionally leaned on another small cluster of current official Resilio docs because they expose a different class of non-clone reason than the earlier approval and grant-lifecycle passes.
The new questions were:

> where do current official docs prove that **seat identity** is still certificate-bearing and that linking two already-running installs can become destructive certificate takeover rather than harmless relationship creation?

> where do current docs show that **hidden offline rows** are not the same thing as unlink or retirement, and that roster residue can legitimately return later?

> what current evidence most clearly shows that **credential recovery** and **service-world reset / rehome** still have materially different preservation fallout, including duplicate rows, reset preferences, and empty-world re-share work?

> where do current docs prove that **mobile identity repair** still requires local unlink/recreate rather than clean successor continuity?

The most load-bearing source set for this pass was the maintained v3 line together with docs on private identity and linking, hiding offline devices, WebUI password reset, Windows service install and troubleshooting, uninstall cleanup, and Android identity corruption repair.

### Additional Resilio official sources emphasized in rev0192

- Resilio Sync 3.0 change log
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Sync Private Identity & Linking My Devices
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- How to clear offline devices? (desktop only)
  https://help.resilio.com/hc/en-us/articles/204762439-How-to-clear-offline-devices-desktop-only

- How do I reset my WebUI password?
  https://help.resilio.com/hc/en-us/articles/205450295-How-do-I-reset-my-WebUI-password

- Running Sync as a service on Windows
  https://help.resilio.com/hc/en-us/articles/207701296-Running-Sync-as-a-service-on-Windows

- Sync Service Troubleshooting on Windows
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

- How to uninstall Sync?
  https://help.resilio.com/hc/en-us/articles/204775029-How-to-uninstall-Sync

- Error 205
  https://help.resilio.com/hc/en-us/articles/207337230-Error-205

## Revision addendum — pending approval, approver locus, and remembered-trust scope

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about approval prompts, pending-folder behavior, approver eligibility across linked seats, request inspection, remembered certificates, and route failures that masquerade as missing approvals.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid about approval flows, request proof, and remembered-trust convenience?

> where do those same current docs still show that the ordinary operator answer about `why is this pending?`, `who may approve it?`, `what exactly am I trusting?`, and `why did I not get a fresh prompt?` still depends on hopping across guides, link-flow articles, folder-type notes, identity docs, and connectivity notes instead of one stable product-owned page?

The most load-bearing source set for this pass was:

- Resilio's current v3 changelog, which still shows an active Sync v3 line through `3.1.2.1076`.
- Resilio's current sharing and desktop-guide docs, which still say links and keys are different approval lanes, pending approval can mean the requester is waiting while the issuer sees nothing due to network connectivity, and identity details can be inspected before approval.
- Resilio's current identity and functionality docs, which still say approvals can be granted from any linked seat where the subject is in `Selective Sync` or `Synced`, that earlier approvals can be remembered, and that security options can force reprompting.
- Resilio's current folder-type and link-flow docs, which still say previously approved peers may auto-connect later and that approval itself is a certificate / ACL event tied to a concrete claimant identity and fingerprint.

## Additional Resilio official sources emphasized in rev0191

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Sync functionality in detail  
  https://help.resilio.com/hc/en-us/articles/204754389-Sync-functionality-in-detail

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Comprehensive guide to syncing (Desktop-Desktop)  
  https://help.resilio.com/hc/en-us/articles/204754939-Comprehensive-guide-to-syncing-Desktop-Desktop

- Sync Share Dialog (Desktop)  
  https://help.resilio.com/hc/en-us/articles/204790709-Sync-Share-Dialog-Desktop

- Folder Types and Management  
  https://help.resilio.com/hc/en-us/articles/204762459-Folder-Types-and-Management

- Link structure and flow  
  https://help.resilio.com/hc/en-us/articles/204754739-Link-structure-and-flow

- What ports and protocols are used by Sync?  
  https://help.resilio.com/hc/en-us/articles/204754759-What-ports-and-protocols-are-used-by-Sync

## Revision addendum — linked identity, folder-family authority cliffs, and claim-lane governance

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about linked-device automation, owner-like behavior across linked seats, Standard-vs-Advanced authority cliffs, key-vs-link approval differences, and the documented workaround for linked-seat read-only.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid about linked-seat convenience, class-dependent authority, and carrier-dependent approval behavior?

> where do those same current docs still show that the ordinary operator answer about `what authority will this seat gain?`, `what future scope am I creating?`, `may this seat re-share?`, and `are these lanes truly equivalent?` still depends on hopping across identity guides, share dialogs, Standard-vs-Advanced docs, and exception how-tos instead of one stable product-owned page?

The most load-bearing source set for this pass was:

- Resilio's current desktop-to-desktop and identity docs, which still show that linked devices auto-receive folders and act as Owners across one identity.
- Resilio's current user-management and Standard-vs-Advanced docs, which still show that only Owners can share Advanced folders while Standard folders permit broader onward sharing under different ceilings.
- Resilio's current share-dialog docs, which still distinguish keys from links because keys do not use the approval mechanism while links can carry approval, expiry, and use budgets.
- Resilio's current one-way-sync docs, which still show that some expected per-seat narrowing for linked devices is not an in-place toggle and instead requires a different family plus manual claim path.

## Additional Resilio official sources emphasized in rev0189

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Comprehensive guide to syncing (Desktop-Desktop)  
  https://help.resilio.com/hc/en-us/articles/204754939-Comprehensive-guide-to-syncing-Desktop-Desktop

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- User Management  
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- Sync Share Dialog (Desktop)  
  https://help.resilio.com/hc/en-us/articles/204790709-Sync-Share-Dialog-Desktop

- What's the difference between Standard and Advanced folders  
  https://help.resilio.com/hc/en-us/articles/204754679-What-s-the-difference-between-Standard-and-Advanced-folders

- Is one-way synchronization possible?  
  https://help.resilio.com/hc/en-us/articles/204754279-Is-one-way-synchronization-possible

## Revision addendum — current-surface capability, browser-app handoff, and missing-action diagnosis

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about share dialogs, browser-open link flow, WebUI exceptions, browser/app handoff failures, browser compatibility, and ad-block interference.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid about browser-first control, multi-carrier sharing, and the fact that some fast paths depend on browser or surface cooperation?

> where do those same current docs still show that the ordinary operator answer about `can I do this here?`, `what exactly failed?`, and `am I still continuing the same reviewed work after switching channels?` still depends on hopping across guides, share dialogs, browser prompts, WebUI exceptions, and troubleshooting notes instead of one stable product-owned page?

The most load-bearing source set for this pass was:

- Resilio's current WebUI, Linux, and Windows-service docs, which still show browser/local-web as ordinary control on Linux-heavy and service-heavy seats, with loopback defaults unless deliberately widened.
- Resilio's current desktop sharing and desktop-to-desktop guide docs, which still show link / QR / e-mail / clipboard sharing, browser-open launch prompts, and manual `Enter key or link` fallback.
- Resilio's current browser-link troubleshooting doc, which still says direct browser opening is impossible when Sync is accessed through WebUI.
- Resilio's current `There's no Share button in Web UI…` troubleshooting doc, which still says missing affordances can be caused by browser incompatibility, ad-block interference, or legitimate role limits rather than policy alone.
- Resilio's current v3 changelog, which still shows the product line is active enough that these seams are current design evidence rather than abandoned-history trivia.

## Additional Resilio official sources emphasized in rev0188

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Configuring WebUI  
  https://help.resilio.com/hc/en-us/articles/115001184490-Configuring-WebUI

- Running Sync as a service on Windows  
  https://help.resilio.com/hc/en-us/articles/207701296-Running-Sync-as-a-service-on-Windows

- Sync Service Troubleshooting on Windows  
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

- Guide to Linux, and Sync peculiarities  
  https://help.resilio.com/hc/en-us/articles/204762449-Guide-to-Linux-and-Sync-peculiarities

- Comprehensive guide to syncing (Desktop-Desktop)  
  https://help.resilio.com/hc/en-us/articles/204754939-Comprehensive-guide-to-syncing-Desktop-Desktop

- Sync Share Dialog (Desktop)  
  https://help.resilio.com/hc/en-us/articles/204790709-Sync-Share-Dialog-Desktop

- Sync doesn't start when opening Link in browser  
  https://help.resilio.com/hc/en-us/articles/204753649-Sync-doesn-t-start-when-opening-Link-in-browser

- There’s no Share button in Web UI…  
  https://help.resilio.com/hc/en-us/articles/204753699-There-s-no-Share-button-in-Web-UI

## Revision addendum — topology, local edges, provider grants, and removable-target continuity

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about nested shares, same-host local sharing, removable/provider-backed storage grants, and returning targets.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid about graph shape, self-routed local edges, storage-provider grants, and disappearing/returning targets?

> where do those same current docs still show that the ordinary operator answer about `what topology did I just create?`, `who actually seeds this target?`, `did I really grant this medium/provider?`, and `did continuity survive the target's disappearance?` still depends on hopping across several FAQs, tips, peculiarity articles, and warning pages instead of one stable product-owned page?

The most load-bearing source set for this pass was:

- Resilio's current nested-share, pre-populated-folder, duplicate-bind, and folder-not-empty docs, which still distinguish disjoint reuse from child-share overlap and conflicting existing binds.
- Resilio's current local-share docs, which still say same-host edges are desktop-only, entitlement-bound, self-only, source-coupled, non-recursive, and not propagated to linked devices.
- Resilio's current Android Simple Mode and SD-card docs, which still distinguish provider-root grant from actual folder choice and still show how convenience mode changes the available topology and storage targets.
- Resilio's current move/reconnect and SMB/network docs, which still show that weakly bound or returning targets can differ materially in notification quality, continuity confidence, and safe rebind truth.

## Additional Resilio official sources emphasized in rev0182

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Is it possible to share a nested folder separately?  
  https://help.resilio.com/hc/en-us/articles/205506159-Is-it-possible-to-share-a-nested-folder-separately

- Can I connect two pre-populated pre-existing folders?  
  https://help.resilio.com/hc/en-us/articles/205506569-Can-I-connect-two-pre-populated-pre-existing-folders

- Selected folder is already added to Sync  
  https://help.resilio.com/hc/en-us/articles/209316526-Selected-folder-is-already-added-to-Sync

- Sharing a folder locally  
  https://help.resilio.com/hc/en-us/articles/360011582500-Sharing-a-folder-locally

- Simple Mode (Android)  
  https://help.resilio.com/hc/en-us/articles/205458155-Simple-Mode-Android

- SD card gimmicks on Android  
  https://help.resilio.com/hc/en-us/articles/209643433-SD-card-gimmicks-on-Android

- Folder not empty  
  https://help.resilio.com/hc/en-us/articles/204753689-Folder-not-empty

- Can I move or rename a syncing folder?  
  https://help.resilio.com/hc/en-us/articles/205450655-Can-I-move-or-rename-a-syncing-folder

- Sync and SMB file shares  
  https://help.resilio.com/hc/en-us/articles/207755736-Sync-and-SMB-file-shares

# Source notes through rev0186

## Revision addendum — semantic tradeoffs, destructive convenience, and hidden optimization truth

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about read-only overwrite behavior, placeholder removal, deferred hashing / preseed readiness, and transfer-method tradeoffs.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid about destructive convenience and hidden optimization costs?

> where do those same current docs still show that the ordinary operator answer about `what will be overwritten?`, `what will be deleted?`, `what is not semantically ready yet?`, and `what interruption cost did I just accept?` still depends on hopping across FAQs, preferences, power-user tables, RSLS/how-to pages, and warning articles rather than one stable page?

The most load-bearing source set for this pass was:

- Resilio's current read-only / one-way sync, user-management, and folder-preferences docs, which still say local changes on read-only seats can suspend synchronization, that `Overwrite any changed files` can be destructive, and that the precise fate of renamed, deleted, edited, and added files differs by class.
- Resilio's current RSLS / Selective Sync docs, which still distinguish local revert-to-placeholder from remove-from-all-devices and still warn that placeholder-only meshes can leave no actual bytes anywhere.
- Resilio's current power-user preferences and internal-tasks docs, which still expose `lazy_indexing`, `prioritize_initial_indexing`, `direct_torrent_enabled`, and `recreate_placeholders_on_removal`, and still explain that hash/check/merge/copy work materially changes visible behavior without necessarily meaning the product is stuck.

## Additional Resilio official sources emphasized in rev0180

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Folder Preferences  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- Is one-way synchronization possible?  
  https://help.resilio.com/hc/en-us/articles/204754279-Is-one-way-synchronization-possible

- What Is an RSLS File?  
  https://help.resilio.com/hc/en-us/articles/206115384-What-Is-an-RSLS-File

- Selective Sync  
  https://help.resilio.com/hc/en-us/articles/205458095-Selective-Sync

- Some internal tasks are taking time to complete  
  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete

- My files don't sync  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

## Revision addendum — execution principal, permission grant, and host authority

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about service accounts, package users, storage roots, filesystem permissions, and blocked-path repair.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid about which runtime user or service account is acting on disk?

> where do those same current docs still show that the ordinary operator answer about `who is touching these bytes?`, `what exact grant makes this path writable?`, `does switching host mode create a different local world?`, and `what repair rung is safest?` still depends on hopping across several host-specific articles instead of one stable product-owned page?

The most load-bearing source set for this pass was:

- Resilio's current Windows service install and troubleshooting docs, which still say the service can run as the current user or Local System, that switching to Local System can widen folder reach, and that such a switch can also move Sync into a different storage-root world that looks empty until folders are re-added and reconnected.
- Resilio's current Linux package and Linux-peculiarities docs, which still say the default service runs as `rslsync`, that current-user service is an alternative, and that storage defaults can follow either package defaults or the current working directory unless storage is pinned explicitly.
- Resilio's current storage-folder and Synology docs, which still show that runtime principal changes where identity/settings/logs live and that package-internal users need explicit folder grants.
- Resilio's current headless macOS and generic troubleshooting docs, which still warn that group-rw continuity matters and that the runtime user must have read-write access to both files and directories.

## Additional Resilio official sources emphasized in rev0177

- Running Sync as a service on Windows  
  https://help.resilio.com/hc/en-us/articles/207701296-Running-Sync-as-a-service-on-Windows

- Sync Service Troubleshooting on Windows  
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

- Installing Sync package on Linux  
  https://help.resilio.com/hc/en-us/articles/206178924-Installing-Sync-package-on-Linux

- Guide to Linux, and Sync peculiarities  
  https://help.resilio.com/hc/en-us/articles/204762449-Guide-to-Linux-and-Sync-peculiarities

- Sync Storage folder  
  https://help.resilio.com/hc/en-us/articles/206664690-Sync-Storage-folder

- Synology  
  https://help.resilio.com/hc/en-us/articles/206664850-Synology

- Launching Sync on Mac without user logged in  
  https://help.resilio.com/hc/en-us/articles/207293730-Launching-Sync-on-Mac-without-user-logged-in

- My files don't sync  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

# Source notes through rev0177

## Revision addendum — capture scope, sink choice, landed proof, and source cleanup

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about camera backup, Android backup, mobile intake constraints, and storage/runtime ceilings.
The new questions were:

> where do current official docs most clearly show that Resilio still has genuinely useful capture-only ingest behavior rather than only generic sync?

> where do those same current docs still show that the ordinary operator answer about `what exact source is attached?`, `which sink counts?`, `has this really landed?`, and `can I delete from the source now?` still depends on hopping across several mobile and backup articles instead of one stable page?

The most load-bearing source set for this pass was:

- Resilio's current Camera Backup and Android backup docs, which still say source-side deletion can leave landed sink copies intact, linked-device or link-based sink selection is part of the flow, iOS is Camera-Roll-only, and Android backup can span broader reachable data.
- Resilio's current mobile-intake and Simple Mode docs, which still say Android path choice can require disabling Simple Mode before QR intake and that Simple Mode forces default internal roots and `(1)` duplicate creation.
- Resilio's current mobile storage/runtime docs, which still say background behavior and local-storage semantics differ materially by platform and affect the practical truth of capture ingest.

## Additional Resilio official sources emphasized in rev0176

- How to use Camera Backup (all mobiles)?
  https://help.resilio.com/hc/en-us/articles/205506809-How-to-use-Camera-Backup-all-mobiles

- How to Back up data (Android only)
  https://help.resilio.com/hc/en-us/articles/204762339-How-to-Back-up-data-Android-only

- Syncing between a desktop computer and a mobile device
  https://help.resilio.com/hc/en-us/articles/205451165-Syncing-between-a-desktop-computer-and-a-mobile-device

- Simple Mode (Android)
  https://help.resilio.com/hc/en-us/articles/205458155-Simple-Mode-Android

- Settings on mobile platforms
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- Storage Management on iOS
  https://help.resilio.com/hc/en-us/articles/115001726304-Storage-Management-on-iOS

- Sync Interface on Android
  https://help.resilio.com/hc/en-us/articles/213500383-Sync-interface-on-Android

- Sync Interface on iOS devices
  https://help.resilio.com/hc/en-us/articles/212016726-Sync-Interface-on-iOS-devices

# Source notes through rev0176

## Revision addendum — path continuity, relocation, disconnected presence, and rename explanation

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about path locality, relocation limits, pathless disconnected presence, duplicate/default-path ritual, and rename replay behavior.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly honest about local-only rename, cross-volume breakage, pathless known-subject presence, and remote rename replay?

> where do those same current docs still show that the ordinary operator answer about `where is this bound?`, `can I move it safely?`, `what still exists when disconnected?`, and `what will peers observe if I rename this here?` still depends on hopping across several FAQs and troubleshooting pages instead of one stable product-owned page?

The most load-bearing source set for this pass was:

- Resilio's current move/rename and folder-not-found docs, which still distinguish same-drive from cross-drive behavior, mark mobile as non-relocatable, and admit that heavier repair can sever prior peer relationships.
- Resilio's current disconnected-folder and manual-location docs, which still make pathless presence real while tying custom arrival placement to `Disconnected` and later `Connect`.
- Resilio's current duplicate-folder and folder-not-empty docs, which still show that default-path arrivals and non-empty-target reconnects can range from harmless to dangerous while sharing too much UI ritual.
- Resilio's current rename/Archive explanation, which still truthfully describes remote replay via retained bytes but keeps that explanation away from the move/rename action itself.

## Additional Resilio official sources emphasized in rev0174

- Can I move or rename a syncing folder?  
  https://help.resilio.com/hc/en-us/articles/205450655-Can-I-move-or-rename-a-syncing-folder

- Folder not found / Can't open the destination folder  
  https://help.resilio.com/hc/en-us/articles/205450255-Folder-not-found-Can-t-open-the-destination-folder

- Folder Types and Management  
  https://help.resilio.com/hc/en-us/articles/204762459-Folder-Types-and-Management

- Disconnecting and Removing Folders  
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- How to manually set the location of the folders synced across linked devices?  
  https://help.resilio.com/hc/en-us/articles/206216615-How-to-manually-set-the-location-of-the-folders-synced-across-linked-devices

- Folders are duplicating with an index (i) in their name.  
  https://help.resilio.com/hc/en-us/articles/204753869-Folders-are-duplicating-with-an-index-i-in-their-name

- Folder not empty  
  https://help.resilio.com/hc/en-us/articles/204753689-Folder-not-empty

- What happens when file is renamed  
  https://help.resilio.com/hc/en-us/articles/209606526-What-happens-when-file-is-renamed

## Revision addendum — capability provenance, compatibility gates, alert delivery, and kind choice

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about right-to-run, version-family compatibility, notification delivery, and subject-kind creation.
The new questions were:

> where do current official docs most clearly show that Resilio still has real product substance around activation, platform candor, alerting, and multiple creation families?

> where do those same current docs still show that the ordinary operator answer depends on licensing pages, FAQ pages, update guides, platform settings, permission docs, and separate sharing/backup articles rather than one stable product-owned page?

The most load-bearing source set for this pass was:

- Resilio's current licensing, FAQ, and update docs, which still say v3 requires activation, personal-device reuse is allowed for personal non-commercial use, linked v2/v3 identities are risky, Sync Business cannot update to v3, and update safety can depend on preserving the same storage/config/user context.
- Resilio's current desktop/mobile/Android/Linux notification-related docs, which still split alert-delivery truth across desktop preferences, mobile settings, Android permissions, and Linux UI-only caveats.
- Resilio's current sharing/send/backup/local-share docs, which still expose useful creation families while spreading the meaning across different menus, platform articles, TTL rules, and capability gates.

## Additional Resilio official sources emphasized in rev0172

- Licensing in Resilio Sync 3.0  
  https://help.resilio.com/hc/en-us/articles/31116248751123-Licensing-in-Resilio-Sync-3-0

- FAQ Resilio Sync 3.0.0  
  https://help.resilio.com/hc/en-us/articles/32109883606035-FAQ-Resilio-Sync-3-0-0

- Updating installation to Resilio Sync v3  
  https://help.resilio.com/hc/en-us/articles/31194252837779-Updating-installation-to-Resilio-Sync-v3

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Settings on mobile platforms  
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- Permissions Sync requires on Android and Amazon Kindle  
  https://help.resilio.com/hc/en-us/articles/205451065-Permissions-Sync-requires-on-Android-and-Amazon-Kindle

- Guide to Linux, and Sync peculiarities  
  https://help.resilio.com/hc/en-us/articles/204762449-Guide-to-Linux-and-Sync-peculiarities

- Sync Share Dialog (Desktop)  
  https://help.resilio.com/hc/en-us/articles/204790709-Sync-Share-Dialog-Desktop

- Sharing single file  
  https://help.resilio.com/hc/en-us/articles/115000401010-Sharing-single-file

- Sharing files (Android)  
  https://help.resilio.com/hc/en-us/articles/115000409690-Sharing-files-Android

- How to use Camera Backup (all mobiles)?  
  https://help.resilio.com/hc/en-us/articles/205506809-How-to-use-Camera-Backup-all-mobiles

- How to Back up data (Android only)  
  https://help.resilio.com/hc/en-us/articles/204762339-How-to-Back-up-data-Android-only

- Sharing a folder locally  
  https://help.resilio.com/hc/en-us/articles/360011582500-Sharing-a-folder-locally

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was a quieter cluster of current official Resilio Sync docs about outside-service visibility and local state-root continuity.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly honest about what tracker, relay, landing-page, update, and telemetry/account infrastructure can and cannot learn?

> where do those same current docs still show that the ordinary operator answer about `who can see what?` and `which local world am I in?` still depends on hopping across security FAQs, ports/config notes, storage-folder lists, config-mode instructions, and identity/troubleshooting articles rather than one stable page?

The most load-bearing source set for this pass was:

- Resilio's current security/privacy docs, which still say the product is cloudless in the ordinary file-storage sense, that the vendor cannot see file contents, that tracker learns IP/port/share-ID facts, that relay passes encrypted traffic without plaintext access, and that landing-page handling intentionally keeps the unique folder-identification payload after `#` out of the server request path.
- Resilio's current ports/protocols, key-flow, and warning docs, which still spell out tracker/discovery facts, LAN/predefined-host publication behavior, and how tracker outage or identity damage actually manifests.
- Resilio's current power-user docs, which still expose separate settings for statistics, tracker use, relay use, known hosts, and refresh intervals rather than one ordinary observer matrix.
- Resilio's current storage-folder, config-mode, identity, and warning docs, which still make clear that storage location, runtime profile, and service principal define a real local state world — but still require the operator to reconstruct that world from multiple articles.

## Additional Resilio official sources emphasized in rev0171

- Can others see my files? How secure is sharing by Resilio Sync?  
  https://help.resilio.com/hc/en-us/articles/205451025-Can-others-see-my-files-How-secure-is-sharing-by-Resilio-Sync

- What is a Relay Server?  
  https://help.resilio.com/hc/en-us/articles/204754779-What-is-a-Relay-Server

- What ports and protocols are used by Sync?  
  https://help.resilio.com/hc/en-us/articles/204754759-What-ports-and-protocols-are-used-by-Sync

- Key structure and flow  
  https://help.resilio.com/hc/en-us/articles/206767810-Key-structure-and-flow

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Sync Storage folder  
  https://help.resilio.com/hc/en-us/articles/206664690-Sync-Storage-folder

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Can I change the name of my Sync identity?  
  https://help.resilio.com/hc/en-us/articles/206163443-Can-I-change-the-name-of-my-Sync-identity

- Core warnings  
  https://help.resilio.com/hc/en-us/articles/360001217950-Core-warnings

## Revision addendum — observer boundaries, service ceilings, and local-world continuity

This revision intentionally leaned on a sixth-wave cluster of current Resilio docs.
The new question was:

> after the archive already had stronger answers for trust, intake, rate truth, byte posture, custody, restore, shell parity, and filesystem-shape fidelity, what current official Resilio pages still most clearly show that AnonSync needs more ordinary replacement pages instead of another direct clone?

The answer came from four families:

- **Infrastructure visibility** — useful honesty about trackers, relays, landing pages, updates, and telemetry, but still too article-scattered
- **Service-role ceilings** — useful statements about what vendor-run services cannot do, but still too FAQ-shaped for ordinary disablement review
- **State-root continuity** — useful storage/config honesty, but still too dependent on path lists, service-principal shifts, and troubleshooting notes
- **Attach/import boundaries** — useful refusal to bless cloning, but still too blunt to classify same-world attach, successor import, stale backup, or clone-risk copies

# Source notes through rev0169

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was a second cluster of current official Resilio Sync docs.
The new questions were:

> where do current official docs most clearly show that Resilio still has excellent product ideas around byte posture, encrypted custody, same-host derivation, and Archive/versioning?

> where do those same current docs still show that the everyday operator answer depends on fused mode selectors, key/database caveats, local-share exception clusters, or restore folklore rather than one stable page?

The most load-bearing source set for this pass was:

- Resilio's current Synchronization Modes, linked-device, preferences, and manual-location docs, which still show useful byte-posture language while tying it to default folder and manual-connect behavior.
- Resilio's current Encrypted folders doc, which still shows ciphertext-only untrusted-node custody while also requiring saved keys, preserved database continuity, and special restore/decrypt conditions.
- Resilio's current Sharing a folder locally doc, which still shows same-host derivation as a real workflow while documenting source-child dependence, rights ceilings, loop rules, and manual reattach behavior.
- Resilio's current Archive doc, which still shows useful versioning/recovery while also requiring manual restore, hidden paths or UI variance, timestamp caveats, and separate History lookup for peer authorship.

## Additional Resilio official sources emphasized in rev0166

- Synchronization Modes  
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- How to manually set the location of the folders synced across linked devices?  
  https://help.resilio.com/hc/en-us/articles/206216615-How-to-manually-set-the-location-of-the-folders-synced-across-linked-devices

- Encrypted folders  
  https://help.resilio.com/hc/en-us/articles/207370466-Encrypted-folders

- Sharing a folder locally  
  https://help.resilio.com/hc/en-us/articles/360011582500-Sharing-a-folder-locally

- Using Archive for file versioning and restoring deleted files.  
  https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files

## Revision addendum — byte posture, encrypted custody, same-host lineage, and fetchability

This revision intentionally leaned on a second wave of current Resilio docs.
The new question was:

> after the archive already had better answers for control trust, typed intake, effective rate truth, and install readiness, what current official Resilio pages still show the strongest need for more replacement pages rather than a direct clone?

The answer came from four families:

- **Synchronization modes / linked-device defaults** — useful posture language, but still too fused
- **Encrypted folders** — valuable ciphertext custody, but still too caveat-shaped on recovery
- **Sharing a folder locally** — valuable same-host workflow, but still too exception-shaped on continuity
- **Archive/versioning** — valuable recovery aid, but still too reconstructive on real fetchability and safe eviction

# Source notes through rev0164

This revision again leaned on the uploaded comparison archives, but the outside evidence that most directly mattered this time was a small official Gmail/GitHub pairing showing that thread chronology and current operative review state are not the same object.
The new questions were:

> where do current official docs most clearly show that one threaded lane may preserve raw chronology while still needing a separate current-state interpretation?

> what current evidence most clearly separates `latest reply in the lane` from `current operative head that still governs action`?

The most load-bearing source set for this pass was:

- Gmail's current conversation-view docs, which say replies are grouped together in conversations with the latest email at the bottom of the conversation thread.
- GitHub's current pull-request review docs, which say reviews can `Comment`, `Approve`, or `Request changes`, that reviews appear in the conversation timeline and merge box, and that reviews can be re-requested after significant changes.
- GitHub's current protected-branches docs, which say approving reviews can be dismissed as stale when the diff changes, and that `Request changes` can block merge until approval or dismissal.

Those current platform truths reinforced the new AnonSync rule that `newest imported reply` and `current operative reply head` must remain different answers.

## Additional official sources emphasized in rev0163

- Group emails into conversations - Gmail Help  
  https://support.google.com/mail/answer/5900

- About pull request reviews - GitHub Docs  
  https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews

- About protected branches - GitHub Docs  
  https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches

- Commenting on a pull request - GitHub Docs  
  https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/commenting-on-a-pull-request

- REST API endpoints for pull request review comments - GitHub Docs  
  https://docs.github.com/en/rest/pulls/comments

- About pull request reviews - GitHub Docs  
  https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews

## Comparative datacubes emphasized in rev0163

- `Goldenrule-rev0323-2026.03.19.19.18-lineageheadregister-citationheadwarnings(1).zip`
- `Anonymity-rev0425-2026.03.20.01.07-seriesumbrellarefactorrootnarrowingnorelease.zip`
- `pyCausalWeave-rev0075-2026.03.19.21.31-taskagentreviewrequestsplittruth.zip`

## Revision addendum — reply-series heads, supersession, and contradiction warnings

This revision intentionally leaned on one comparison-archive cluster and one small cluster of current official Gmail/GitHub docs.
The new question was:

> once imported reply truth can already classify object exactness, represented scope, human-proof, semantic stance, and referent coverage, what compact surface says which reply is currently operative now when several replies have accumulated in the same lane?

The most useful comparison pressure this time came from:

- **Goldenrule** — especially its lineage-head / citation-head / warning-surface pressure, which reinforced that latest chronology and current claim-ready head are different answers
- **Anonymity** — especially its series-umbrella / queue visibility pressure, which reinforced that moving families need one compact currentness surface rather than scattered reconstruction
- **pyCausalWeave** — which reinforced that raw request/review arrival order and current live gate truth should remain separate objects

## Comparative datacubes emphasized in rev0162

- `Goldenrule-rev0323-2026.03.19.19.18-lineageheadregister-citationheadwarnings(1).zip`
- `DeriveBSD-rev0323-2026.03.20.01.25-organizationuserscopeexact.zip`
- `pyCausalWeave-rev0075-2026.03.19.21.31-taskagentreviewrequestsplittruth.zip`

## Revision addendum — referent slice, quote scope, and request coverage

This revision intentionally leaned on one comparison-archive cluster and one small cluster of current official GitHub review-comment docs.
The new question was:

> once imported reply truth can already say what exact object was acknowledged, who that reply can speak for, whether any human replied, and what that reply meant, what stops one quoted paragraph or one line-range comment from silently inheriting whole-packet acceptance meaning?

The most useful comparison pressure this time came from:

- **Goldenrule** — especially its citation-head / head-warning pressure, which reinforced that quoted or cited sub-surfaces should not silently inherit whole-document meaning
- **DeriveBSD** — which reinforced that exact scope and exact target claims should stay visible rather than collapse into fuzzy near-matches
- **pyCausalWeave** — which reinforced that one review/request object often still needs a split between current object identity and the narrower slice that a reply actually addressed

## Additional official sources emphasized in rev0161

- About pull request reviews - GitHub Docs  
  https://docs.github.com/articles/about-pull-request-reviews

- REST API endpoints for pull request reviews - GitHub Docs  
  https://docs.github.com/en/rest/pulls/reviews

- Merge request reviews - GitLab Docs  
  https://docs.gitlab.com/user/project/merge_requests/reviews/

## Comparative datacubes emphasized in rev0161

- `Anonymity-rev0425-2026.03.20.01.07-seriesumbrellarefactorrootnarrowingnorelease.zip`
- `pyCausalWeave-rev0075-2026.03.19.21.31-taskagentreviewrequestsplittruth.zip`
- `DeriveBSD-rev0323-2026.03.20.01.25-organizationuserscopeexact.zip`

## Revision addendum — reply stance, conditionality, and smallest follow-up

This revision intentionally leaned on one comparison-archive cluster and one small cluster of current official review-platform docs.
The new question was:

> once imported reply truth can already say what exact object was acknowledged, who that reply can speak for, and whether any human replied, what stops every human reply from silently inheriting acceptance meaning?

The most useful comparison pressure this time came from:

- **Anonymity** — especially its response-menu / smallest-sufficient-handoff pattern, which cleanly made follow-up class an explicit owned object instead of prose drift
- **pyCausalWeave** — which reinforced that review/request/follow-through truth should not collapse into one overloaded status word
- **DeriveBSD** — which reinforced that exact scope and exact outcome should stay visible rather than being smoothed into generic success

## Revision addendum — acknowledgment authorship, automation, and human-proof

- the previous rev0160 authorship pass remains intact and now acts as a companion seam rather than the terminal imported-reply answer
- this rev0161 pass builds on it by separating `human replied` from `human accepted`

## Additional official sources emphasized in rev0159

- About shared mailboxes in Microsoft 365  
  https://learn.microsoft.com/en-us/microsoft-365/admin/email/about-shared-mailboxes?view=o365-worldwide

- Shared mailboxes in Exchange Online  
  https://learn.microsoft.com/en-us/exchange/collaboration-exo/shared-mailboxes

- Create distribution lists - Microsoft 365 admin  
  https://learn.microsoft.com/en-us/microsoft-365/admin/setup/create-distribution-lists?view=o365-worldwide

- Set who can view, post & moderate - Google Groups Help  
  https://support.google.com/groups/answer/2464975

- Set permissions for managing members and content - Google Workspace Learning Center  
  https://support.google.com/a/users/answer/9886284

- Set organization-wide policies for using groups - Google Workspace Help  
  https://support.google.com/a/answer/167097

## Comparative datacubes emphasized in rev0159

- `DeriveBSD-rev0323-2026.03.20.01.25-organizationuserscopeexact.zip`
- `pyCausalWeave-rev0075-2026.03.19.21.31-taskagentreviewrequestsplittruth.zip`

## Revision addendum — reviewed recipient targets, stale retargets, and explicit reissue

This revision intentionally leaned on one comparison-archive pattern and one small cluster of current GitHub docs.
The new question was:

> once a reviewed packet, offer issue, or refresh note was prepared for one explicit recipient or target, what stops that older reviewed intent from silently following a different recipient, wider audience, or new destination later?

The most useful comparison pressure this time came from:

- **pyCausalWeave** — especially its target-scoped retarget-guard work, which cleanly separated object continuity from target continuity
- **DeriveBSD** — which reinforced that exact scope and exact target claims should stay visible rather than collapse into fuzzy near-matches

The current GitHub docs reinforced the same law from a different domain: changing the base branch of a pull request can make comments outdated, required approving reviews can be dismissed as stale when the merge base changes, and fresh review can be re-requested after substantial changes.
That reinforced the AnonSync decision that earlier reviewed intent should not silently follow a materially different current target.

### Comparative datacubes emphasized in rev0155

- `pyCausalWeave-rev0075-2026.03.19.21.31-taskagentreviewrequestsplittruth.zip`
- `DeriveBSD-rev0323-2026.03.20.01.25-organizationuserscopeexact.zip`

### Current web/platform sources emphasized in rev0155

- GitHub Docs: Changing the base branch of a pull request
  https://docs.github.com/articles/changing-the-base-branch-of-a-pull-request

- GitHub Docs: Requesting a pull request review
  https://docs.github.com/articles/requesting-a-pull-request-review

- GitHub Docs: About protected branches
  https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches

## Revision addendum — artifact carryforward, delta ledgers, and refresh notices

This revision intentionally leaned on two comparison-archive patterns and one small piece of current web-platform guidance.
The new question was:

> once one artifact family already has an older disclosed or previously-current shareable head, what compact surface says whether that older artifact still stands, what changed in the newer one, and whether a terse refresh note is honest or a full reopen is required?

The most useful comparison pressure this time came from:

- **Anonymity** — the packet-carryforward / delta-ledger / visible-refresh-notice split for reused outward-facing packets under successor maintenance
- **EvidenceVault** — the distinction between stable public surface, queue state, and immutable release snapshot, which reinforced that current public artifact and current public explanation are not the same object

A small current web-platform analogy helped too: modern HTTP validators such as **ETag** and **Last-Modified** are good at proving whether a representation changed or appears unchanged, but they are not human semantic change summaries by themselves.
That reinforced the AnonSync decision not to confuse hash/version drift with one honest recipient-safe refresh explanation.

### Comparative datacubes emphasized in rev0152

- `Anonymity-rev0425-2026.03.20.01.07-seriesumbrellarefactorrootnarrowingnorelease.zip`
- `EvidenceVault-rev0484-2026.03.20.01.36-publishedqueueexecutionfrozenpublicsurface.zip`

### Current web/platform sources emphasized in rev0152

- MDN: ETag header
  https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/ETag

- MDN: Last-Modified header
  https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Last-Modified

## Revision addendum — browser trust, handoff fallback, effective rate policy, and install readiness

This revision intentionally leaned on another small cluster of current official Resilio docs because they expose a different class of non-clone reason than the earlier trust-memory and repair passes.
The new questions were:

> where do current official docs prove that **browser trust for local control** still broadens into unsafe proceed, HSTS clearing, or config-file certificate replacement instead of one endpoint-trust contract?

> where do current docs show that **browser-open handoff** can still fail because of browser, OS-association, or WebUI-surface limits and then fall back to generic manual paste?

> what current evidence most clearly shows that **rate policy** still lives across ordinary preferences, power-user LAN exceptions, scheduler notes, and configuration mode?

> where do current docs prove that **installation** still splits package trust, UAC/firewall consent, and runtime startup into different moments rather than one readiness receipt?

The most load-bearing source set for this pass was the maintained v3 line together with docs on WebUI configuration, browser warnings, browser-open failure, Sync preferences, scheduling, silent install, and SmartScreen.

### Additional Resilio official sources emphasized in rev0144

- Configuring WebUI  
  https://help.resilio.com/hc/en-us/articles/115001184490-Configuring-WebUI

- Browser warning "Your connection is not private"  
  https://help.resilio.com/hc/en-us/articles/4404757430291-Browser-warning-Your-connection-is-not-private

- Sync doesn't start when opening Link in browser  
  https://help.resilio.com/hc/en-us/articles/204753649-Sync-doesn-t-start-when-opening-Link-in-browser

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Running Sync on schedule  
  https://help.resilio.com/hc/en-us/articles/210783266-Running-Sync-on-schedule

- How to Silently Install Resilio Sync  
  https://help.resilio.com/hc/en-us/articles/205505969-How-to-Silently-Install-Resilio-Sync

- Windows Defender SmartScreen blocks Resilio Sync installer  
  https://help.resilio.com/hc/en-us/articles/360014486120-Windows-Defender-SmartScreen-blocks-Resilio-Sync-installer

## Revision addendum — trust memory, absence scope, credential recovery, and repair ladders

This revision intentionally leaned on another small cluster of current official Resilio docs because they expose a different class of non-clone reason than the earlier attention, entitlement, and upgrade passes.
The new questions were:

> where do current official docs prove that **approval** can still widen into remembered future trust instead of staying a one-time decision?

> where do current docs show that **disconnected, hidden, offline, and removed** still carry different return and removal semantics even when the list rows look similarly absent?

> what current evidence most clearly shows that **WebUI credential recovery** can still cause duplicate-seat visibility or unrelated settings reset depending on which ritual is used?

> where do current docs prove that **repair** still broadens from restart to reconnect to re-add through troubleshooting prose rather than one typed escalation ladder?

The most load-bearing source set for this pass was the maintained v3 line together with docs on linking and future approval, folder types and disconnected rows, disconnect/remove scope, hidden offline devices, WebUI password reset, locked files, stuck-sync troubleshooting, and database-error repair.

### Additional Resilio official sources emphasized in rev0143

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Folder Types and Management  
  https://help.resilio.com/hc/en-us/articles/204762459-Folder-Types-and-Management

- Disconnecting and Removing Folders  
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- How to clear offline devices? (desktop only)  
  https://help.resilio.com/hc/en-us/articles/204762439-How-to-clear-offline-devices-desktop-only

- How do I reset my WebUI password?  
  https://help.resilio.com/hc/en-us/articles/205450295-How-do-I-reset-my-WebUI-password

- Locked files  
  https://help.resilio.com/hc/en-us/articles/205504549-Locked-files

- My files don't sync  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Database error  
  https://help.resilio.com/hc/en-us/articles/204753659-Database-error

## Revision addendum — listener survivability, instance namespaces, capability-owner jumps, and typed headless intake

This revision intentionally leaned on another small cluster of current official Resilio docs because they expose a different class of non-clone reason than the earlier route, restore, and service-world passes.
The new questions were:

> where do current official docs prove that **control exposure** can still be widened in ways that make the process depend on one fragile interface rather than one survivable control boundary?

> where do current docs show that **same-host multi-instance operation** still depends on manual namespace discipline instead of one reviewed separation contract?

> what current evidence most clearly shows that **capability ownership** can still jump seats and starve another seat as an activation side effect rather than a reviewed entitlement transfer?

> where do current docs prove that **headless intake** still routes materially different artifact classes through one generic entry verb?

The most load-bearing source set for this pass was the maintained v3 line together with docs on Linux peculiarities, Windows service troubleshooting, same-host service-file corruption, headless license application, license-owner transfer, and stolen-device reactivation behavior.

### Additional Resilio official sources emphasized in rev0140

- Guide to Linux, and Sync peculiarities  
  https://help.resilio.com/hc/en-us/articles/204762449-Guide-to-Linux-and-Sync-peculiarities

- Sync Service Troubleshooting on Windows  
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

- Service files missing / Cannot identify destination folder  
  https://help.resilio.com/hc/en-us/articles/205450225-Service-files-missing-Cannot-identify-destination-folder

- How to apply license key and share license seats  
  https://help.resilio.com/hc/en-us/articles/204762369-How-to-apply-license-key-and-share-license-seats

- Can I change the device which acts as the license owner?  
  https://help.resilio.com/hc/en-us/articles/204753479-Can-I-change-the-device-which-acts-as-the-license-owner

- If your device is stolen  
  https://help.resilio.com/hc/en-us/articles/204644049-If-your-device-is-stolen

# Source notes through rev0139

This revision again leaned on current official Resilio sources, but with fresh attention on four sharper questions:

> if a modern sync product is still useful and maintained, what current evidence gives us a **compromise-response** reason not to clone its interface contract?

> what current documentation most clearly proves that some restore and versioning truth still lives in **hidden archive ritual plus separate history lookup** rather than one recovery workflow?

> where do current official docs most clearly show that **presence and membership truth** still blur offline aging, cosmetic hiding, and actual retirement or revocation?

> how do current docs about **single-file sharing** prove that bounded snapshot delivery is still semantically different from a live shared subject even when the UI makes it feel similar?

The most load-bearing source set this time was the v3 change log together with docs on linking, unlinking limitations, clearing offline devices, stolen-device response, sync main view peer counts, archive/version restore, share dialog, link structure/flow, synchronization modes, user management, folder preferences, power-user defaults, configuration mode, WebUI, reconnect/path placement, route narrowing, selected-folder collision, same-machine local sharing, Standard-vs-Advanced differences, move/rename limits, service-seat troubleshooting, and single-file sharing.

# Sources

This revision intentionally relied on a small set of load-bearing sources checked on 2026-03-19.
The newest pass especially reused the current official docs that reveal the semantic split most clearly: maintained v3 releases, landing-page-to-app handoff, linked-device identity takeover, inability to remotely unlink devices, device-wide synchronization modes, per-share versus global transfer-priority inheritance, WebUI-as-default on Linux/service installs, route narrowing across several settings layers plus cache-clear ritual, hidden share identity via `.sync/ID`, local-share same-machine caveats, non-upgradeable Standard folders, move/rehome limits by root/platform, service-account storage-root drift, stolen-device response through unlink/regenerate/reinstall/reshare, hidden-archive/manual restore, cosmetic offline-device hiding, peer-count offline aging, and one-time file-transfer caveats.

## Resilio official

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- How to clear offline devices? (desktop only)  
  https://help.resilio.com/hc/en-us/articles/204762439-How-to-clear-offline-devices-desktop-only

- If your device is stolen  
  https://help.resilio.com/hc/en-us/articles/204644049-If-your-device-is-stolen

- Sync Main View (Desktop)  
  https://help.resilio.com/hc/en-us/articles/204755009-Sync-Main-View-Desktop

- Synchronization Modes  
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- Sync functionality in detail  
  https://help.resilio.com/hc/en-us/articles/204754389-Sync-functionality-in-detail

- Sync Share Dialog (Desktop)  
  https://help.resilio.com/hc/en-us/articles/204790709-Sync-Share-Dialog-Desktop

- Sharing single file  
  https://help.resilio.com/hc/en-us/articles/115000401010-Sharing-single-file

- User Management  
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- What's the difference between Standard and Advanced folders?  
  https://help.resilio.com/hc/en-us/articles/204754679-What-s-the-difference-between-Standard-and-Advanced-folders

- How do I upgrade my Standard (1.4, or classic) folders to Advanced (2.x) folders?  
  https://help.resilio.com/hc/en-us/articles/206216575-How-do-I-upgrade-my-Standard-1-4-or-classic-folders-to-Advanced-2-x-folders

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Folder Preferences  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- File download priority  
  https://help.resilio.com/hc/en-us/articles/42328167759251-File-download-priority

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Configuring WebUI  
  https://help.resilio.com/hc/en-us/articles/115001184490-Configuring-WebUI

- There's no Share button in Web UI…  
  https://help.resilio.com/hc/en-us/articles/204753699-There-s-no-Share-button-in-Web-UI

- Disconnecting and Removing Folders  
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- How to manually set the location of the folders synced across linked devices?  
  https://help.resilio.com/hc/en-us/articles/206216615-How-to-manually-set-the-location-of-the-folders-synced-across-linked-devices

- Link structure and flow  
  https://help.resilio.com/hc/en-us/articles/204754739-Link-structure-and-flow

- What ports and protocols are used by Sync?  
  https://help.resilio.com/hc/en-us/articles/204754759-What-ports-and-protocols-are-used-by-Sync

- Can I force Sync to do local network (LAN) syncing only and not sync via the Internet?  
  https://help.resilio.com/hc/en-us/articles/204754349-Can-I-force-Sync-to-do-local-network-LAN-syncing-only-and-not-sync-via-the-Internet

- Selected folder is already added to Sync  
  https://help.resilio.com/hc/en-us/articles/209316526-Selected-folder-is-already-added-to-Sync

- Sharing a folder locally  
  https://help.resilio.com/hc/en-us/articles/360011582500-Sharing-a-folder-locally

- Can I connect two pre-populated pre-existing folders?  
  https://help.resilio.com/hc/en-us/articles/205506569-Can-I-connect-two-pre-populated-pre-existing-folders

- Using Archive for file versioning and restoring deleted files.  
  https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files

- Can I move or rename a syncing folder?  
  https://help.resilio.com/hc/en-us/articles/205450655-Can-I-move-or-rename-a-syncing-folder

- Folder not found / Can't open the destination folder  
  https://help.resilio.com/hc/en-us/articles/205450255-Folder-not-found-Can-t-open-the-destination-folder

- Sync Service Troubleshooting on Windows  
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows
## Revision addendum — hidden service state, warning-tier targets, subtree graphs, and one-way truth

This revision intentionally leaned on another small cluster of current official Resilio docs because they expose a different class of non-clone reason than the earlier offer/route/restore passes.
The new questions were:

> if current sync products still feel tempting to clone, where do their official docs show that **hidden service state** is still part of the practical operator contract?

> where do current docs prove that **warning-tier targets** still need a durable semantic contract rather than a one-time warning?

> what current evidence most clearly shows that **nested subtree sharing** is a graph mutation with propagation and seeding caveats, not an ordinary share action?

> how do current docs prove that **read-only** still overloads write denial, local repair, and relay/seeding truth?

The most load-bearing source set for this pass was the maintained v3 line together with docs on hidden `.sync` service state, `IgnoreList`, `StreamsList`, cloning, service-file corruption, SMB behavior, symlink behavior, nested subtree sharing, and one-way synchronization.

### Additional Resilio official sources emphasized in rev0129

- Cloning Sync  
  https://help.resilio.com/hc/en-us/articles/360018421940-Cloning-Sync

- Service files missing / Cannot identify destination folder  
  https://help.resilio.com/hc/en-us/articles/205450225-Service-files-missing-Cannot-identify-destination-folder

- Ignoring files in Sync (Ignore List)  
  https://help.resilio.com/hc/en-us/articles/205458165-Ignoring-files-in-Sync-Ignore-List

- Alt Streams and Xattrs in Sync  
  https://help.resilio.com/hc/en-us/articles/204754729-Alt-Streams-and-Xattrs-in-Sync

- What is '.sync' folder, and StreamsList, IgnoreList and Archive inside?  
  https://help.resilio.com/hc/en-us/articles/206217185-What-is-sync-folder-and-StreamsList-IgnoreList-and-Archive-inside

- Soft links, hard links and symbolic links  
  https://help.resilio.com/hc/en-us/articles/205504529-Soft-links-hard-links-and-symbolic-links

- Sync and SMB file shares  
  https://help.resilio.com/hc/en-us/articles/207755736-Sync-and-SMB-file-shares

- Is it possible to share a nested folder separately?  
  https://help.resilio.com/hc/en-us/articles/205506159-Is-it-possible-to-share-a-nested-folder-separately

- Is one-way synchronization possible?  
  https://help.resilio.com/hc/en-us/articles/204754279-Is-one-way-synchronization-possible

## Revision addendum — name portability, name planes, rename cost, and placeholder no-byte risk

This revision intentionally leaned on another small cluster of current official Resilio docs because they expose a different class of non-clone reason than the earlier hidden-state and restore passes.
The new questions were:

> where do current official docs prove that **name portability truth** still leaks through conflict suffixes and troubleshooting lore rather than one typed portability review?

> where do current docs show that **presentation names, disk names, and portable-artifact labels** can diverge without one clear public model?

> what current evidence most clearly shows that a familiar `rename` can still hide **archive-assisted continuity versus real byte replay**?

> where do current docs prove that placeholder-heavy flows can still leave operators with **names but no bytes** unless witness truth is shown explicitly?

The most load-bearing source set for this pass was the maintained v3 line together with docs on conflict files, rename behavior, custom share names, selective-sync placeholder files, disconnect/reconnect, synchronization modes, power-user guardrails, and troubleshooting for UTF-8/path-length failures.

### Additional Resilio official sources emphasized in rev0130

- Conflict files in Sync  
  https://help.resilio.com/hc/en-us/articles/204753629-Conflict-files-in-Sync

- What happens when file is renamed  
  https://help.resilio.com/hc/en-us/articles/209606526-What-happens-when-file-is-renamed

- What Is an RSLS File?  
  https://help.resilio.com/hc/en-us/articles/206115384-What-Is-an-RSLS-File

- Can I move or rename a syncing folder?  
  https://help.resilio.com/hc/en-us/articles/205450655-Can-I-move-or-rename-a-syncing-folder

- Setting custom name for sync shares  
  https://help.resilio.com/hc/en-us/articles/360011865879-Setting-custom-name-for-sync-shares

- My files don't sync  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

## Revision addendum — opaque replicas, watch coverage, ghost-state, and service-root separation

This revision intentionally leaned on another small cluster of current official Resilio docs because they expose a different class of non-clone reason than the earlier naming, restore, and topology passes.
The new questions were:

> where do current official docs prove that **ciphertext-only custody** is still a real operational class with its own target-hygiene and recovery ceilings, not just a normal read-only share?

> where do current docs show that **change-detection truth** still depends on watcher coverage, target class, and rescan settings rather than one stable runtime contract?

> what current evidence most clearly shows that a file can remain **announced in the namespace without any online byte witness** and still require ritual repair or careful waiting?

> how do current docs prove that **service-root placement** can still collide with broad-tree syncing and should therefore be surfaced before bind?

The most load-bearing source set for this pass was the maintained v3 line together with docs on encrypted folders, key structure, start-of-sync detection, watcher exhaustion, ghost-file warnings, storage-root placement, and broad home-folder admission failure.

### Additional Resilio official sources emphasized in rev0131

- Encrypted folders  
  https://help.resilio.com/hc/en-us/articles/207370466-Encrypted-folders

- Key structure and flow  
  https://help.resilio.com/hc/en-us/articles/206767810-Key-structure-and-flow

- How soon does synchronization start?  
  https://help.resilio.com/hc/en-us/articles/204754319-How-soon-does-synchronization-start

- Agent run out of system notify watchers. Updated files will be uploaded only after periodic folder rescan  
  https://help.resilio.com/hc/en-us/articles/360015593120-Agent-run-out-of-system-notify-watchers-Updated-files-will-be-uploaded-only-after-periodic-folder-rescan

- Cannot download files / These files cannot be downloaded as there are no source peers online for too long time.  
  https://help.resilio.com/hc/en-us/articles/360010899719-Cannot-download-files-These-files-cannot-be-downloaded-as-there-are-no-source-peers-online-for-too-long-time

- Sync Storage folder  
  https://help.resilio.com/hc/en-us/articles/206664690-Sync-Storage-folder

- Cannot add folder. It contains a folder that is already syncing.  
  https://help.resilio.com/hc/en-us/articles/360000053399-Cannot-add-folder-It-contains-a-folder-that-is-already-syncing

- Core warnings  
  https://help.resilio.com/hc/en-us/articles/360001217950-Core-warnings

## Revision addendum — clock trust, quiescent commit, alias edges, and pause truth

This revision intentionally leaned on another small cluster of current official Resilio docs because they expose a different class of non-clone reason than the earlier opaque-custody, naming, and restore passes.
The new questions were:

> where do current official docs prove that **chronology trust** still depends on peer clock and timezone correctness rather than one visible confidence model?

> where do current docs show that **active-writer safety** still leaks through hidden delay tuning, restart requirements, and generic lock warnings instead of one public quiescence contract?

> what current evidence most clearly shows that **link-like filesystem edges** still fork semantics by platform and boundary instead of one typed admission review?

> where do current docs prove that `**pause**` still hides a signal matrix, allowing some mutation classes through while the interface sounds absolute?

The most load-bearing source set for this pass was the maintained v3 line together with docs on Invalid Time, locked files, delay tuning, power-user retry configuration, link-node support ceilings, manual pause, scheduler pause, and sync preferences.

### Additional Resilio official sources emphasized in rev0132

- "Time difference" error  
  https://help.resilio.com/hc/en-us/articles/204753599--Time-difference-error

- Locked files  
  https://help.resilio.com/hc/en-us/articles/205504549-Locked-files

- Setting Delay Time For Syncing  
  https://help.resilio.com/hc/en-us/articles/207491426-Setting-Delay-Time-For-Syncing

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Soft links, hard links and symbolic links  
  https://help.resilio.com/hc/en-us/articles/205504529-Soft-links-hard-links-and-symbolic-links

- How to pause syncing  
  https://help.resilio.com/hc/en-us/articles/206217325-How-to-pause-syncing

- Running Sync on schedule  
  https://help.resilio.com/hc/en-us/articles/210783266-Running-Sync-on-schedule

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

## Revision addendum — rule ledgers, metadata channels, staged finality, and capture-only ingest

This revision intentionally leaned on another small cluster of current official Resilio docs because they expose a different class of non-clone reason than the earlier clock, topology, restore, and route passes.
The new questions were:

> where do current official docs prove that **ignore policy** still lives in hidden sidecars and can still drift into silent disagreement about what should sync?

> where do current docs show that **metadata fidelity** still depends on hidden whitelists and service stubs rather than one visible contract?

> what current evidence most clearly shows that **partial transfer finality** still leaks through hidden `.!sync` artifacts and cleanup ritual?

> where do current docs prove that **capture-only backup** is still useful enough to matter but still special-cased through runtime caveats and legacy folder class meaning?

The most load-bearing source set for this pass was the maintained v3 line together with docs on IgnoreList, `.sync` contents, alternate streams and xattrs, partial-download troubleshooting, camera backup, Android backup, and iOS/mobile peculiarities.

### Additional Resilio official sources emphasized in rev0133

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Ignoring files in Sync (Ignore List)  
  https://help.resilio.com/hc/en-us/articles/205458165-Ignoring-files-in-Sync-Ignore-List

- My files don't sync  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- What is '.sync' folder, and StreamsList, IgnoreList and Archive inside?  
  https://help.resilio.com/hc/en-us/articles/206217185-What-is-sync-folder-and-StreamsList-IgnoreList-and-Archive-inside

- Alt Streams and Xattrs in Sync  
  https://help.resilio.com/hc/en-us/articles/204754729-Alt-Streams-and-Xattrs-in-Sync

- How to use Camera Backup (all mobiles)?  
  https://help.resilio.com/hc/en-us/articles/205506809-How-to-use-Camera-Backup-all-mobiles

- How to Back up data (Android only)  
  https://help.resilio.com/hc/en-us/articles/204762339-How-to-Back-up-data-Android-only

- Sync for iOS Peculiarities  
  https://help.resilio.com/hc/en-us/articles/205506539-Sync-for-iOS-Peculiarities

## Revision addendum — hidden work, reuse proof, repair ladders, and departure truth

This revision intentionally leaned on another small cluster of current official Resilio docs because they expose a different class of non-clone reason than the earlier rule-ledger, metadata, and staged-transfer passes.
The new questions were:

> where do current official docs prove that **important work is still hidden behind one generic busy warning** rather than one visible phase model?

> where do current docs show that **local reuse and pre-seeded acceptance** still need stronger public proof about hashing, local-block reuse, and whole-file fallback?

> what current evidence most clearly shows that **integrity repair** still falls back to reconnect, remove, and re-add ritual even when the damaged layer differs?

> where do current docs prove that **disconnect / remove / placeholder eviction** still hide materially different local and shared consequences?

The most load-bearing source set for this pass was the maintained v3 line together with docs on internal tasks, changed-piece behavior, power-user optimization defaults, database error repair, service-files-missing repair, no-sync troubleshooting, selective sync, synchronization modes, and disconnect/remove semantics.

### Additional Resilio official sources emphasized in rev0134

- Some internal tasks are taking time to complete  
  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete

- When a file changes, does Resilio Sync transfer the entire file again, or just the part that's changed?  
  https://help.resilio.com/hc/en-us/articles/206217095-When-a-file-changes-does-Resilio-Sync-transfer-the-entire-file-again-or-just-the-part-that-s-changed

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Database error  
  https://help.resilio.com/hc/en-us/articles/204753659-Database-error

- Service files missing / Cannot identify destination folder  
  https://help.resilio.com/hc/en-us/articles/205450225-Service-files-missing-Cannot-identify-destination-folder

- My files don't sync  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Disconnecting and Removing Folders  
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- Selective Sync  
  https://help.resilio.com/hc/en-us/articles/205458095-Selective-Sync

- Synchronization Modes  
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

## Revision addendum — storage truth, identity-root salvage, host custody, and compatibility gates

This revision intentionally leaned on another small cluster of current official Resilio docs because they expose a different class of non-clone reason than the earlier work-ledger, repair, and departure passes.
The new questions were:

> where do current official docs prove that **storage pressure** is still described through default-root warnings and hidden thresholds rather than one filesystem-scoped pressure ledger?

> where do current docs show that **identity-root failure** still lives in hidden storage artifacts and salvage/reset ritual rather than one explicit control-plane health workflow?

> what current evidence most clearly shows that **same-host dual-instance ownership** can still corrupt hidden service state unless custody is classified before bind?

> how do current docs prove that **linking across cohorts or non-empty control planes** is still closer to a migration/takeover problem than to a harmless convenience join?

The most load-bearing source set for this pass was the maintained v3 line together with docs on core warnings, power-user preferences, default folder location semantics, `SE_SM_NO_IDENTITY`, service-files-missing repair, same-host dual-instance corruption, mixed-version linking guidance, certificate/share takeover on linking, and Windows service/runtime principal troubleshooting.

### Additional Resilio official sources emphasized in rev0135

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Resilio Sync change log  
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log

- Core warnings  
  https://help.resilio.com/hc/en-us/articles/360001217950-Core-warnings

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- SE_SM_NO_IDENTITY  
  https://help.resilio.com/hc/en-us/articles/207337990-SE-SM-NO-IDENTITY

- Service files missing / Cannot identify destination folder  
  https://help.resilio.com/hc/en-us/articles/205450225-Service-files-missing-Cannot-identify-destination-folder

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Sync Service Troubleshooting on Windows  
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

## Revision addendum — constrained seats, roundtrip editing, shell dependence, and resume precedence

This revision intentionally leaned on another small cluster of current official Resilio docs because they expose a different class of non-clone reason than the earlier storage, identity, and repair passes.
The new questions were:

> where do current official docs prove that **constrained-seat acceptance** still hides storage class, path consent, and degraded promises behind mode toggles and provider ritual rather than one bind review?

> where do current docs show that **external editing** on some seats is still a copy-out / copy-back workflow rather than an in-place shared-object mutation?

> what current evidence most clearly shows that **shell actions** still depend on posture, extension health, and filesystem class instead of one stable capability surface?

> how do current docs prove that **background gaps and late-return offline edits** still carry precedence semantics that deserve quarantine rather than silent application?

The most load-bearing source set for this pass was the maintained v3 line together with docs on Android Simple Mode, QR/mobile intake, Android file receipt paths, SD-card/provider access, iOS storage sandbox and copy-return editing, shell integration on macOS/Windows, background support by platform, and offline-edit precedence.

### Additional Resilio official sources emphasized in rev0136

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Simple Mode (Android)  
  https://help.resilio.com/hc/en-us/articles/205458155-Simple-Mode-Android

- Syncing between a desktop computer and a mobile device  
  https://help.resilio.com/hc/en-us/articles/205451165-Syncing-between-a-desktop-computer-and-a-mobile-device

- Sharing files (Android)  
  https://help.resilio.com/hc/en-us/articles/115000409690-Sharing-files-Android

- Storage Management on iOS  
  https://help.resilio.com/hc/en-us/articles/115001726304-Storage-Management-on-iOS

- SD card gimmicks on Android  
  https://help.resilio.com/hc/en-us/articles/209643433-SD-card-gimmicks-on-Android

- Sync for iOS Peculiarities  
  https://help.resilio.com/hc/en-us/articles/205506539-Sync-for-iOS-Peculiarities

- How to edit a document stored in Sync? (iOS)  
  https://help.resilio.com/hc/en-us/articles/204762379-How-to-edit-a-document-stored-in-Sync-iOS

- No Sync icons in the file browser/no Sync-related items in the context menu on Mac/Windows  
  https://help.resilio.com/hc/en-us/articles/206214625-No-Sync-icons-in-the-file-browser-no-Sync-related-items-in-the-context-menu-on-Mac-Windows

- Does Sync work in background?  
  https://help.resilio.com/hc/en-us/articles/206816823-Does-Sync-work-in-background

- What if several people make changes to the same file?  
  https://help.resilio.com/hc/en-us/articles/204754209-What-if-several-people-make-changes-to-the-same-file

## Revision addendum — power cadence, transfer rows, ingress verbs, and reclaim scope

This revision intentionally leaned on another small cluster of current official Resilio docs because they expose a different class of non-clone reason than the earlier seat, shell, and resume passes.
The new questions were:

> where do current official docs prove that **power-saving policy** still changes whether a seat is actually visible and participating, not just how much battery it uses?

> what current documentation most clearly proves that **file-send history rows** still diverge from live offer state and from bytes on disk?

> where do current official docs show that **mobile ingress verbs** still mix live collaboration, adopted folders, bounded sends, and capture-style backup under one adjacent menu family?

> how do current docs prove that **local cleanup and reclaim** still depend on surface and posture rather than one explicit scope matrix?

The most load-bearing source set for this pass was the maintained v3 change log together with docs on Android Auto Sleep/Battery Saver, mobile sharing on Android and iOS, storage management on iOS, Sync interface on Android, mobile initiation, Android backup, and power-user transfer retention preferences.

### Additional Resilio official sources emphasized in rev0137

- Configuring Auto Sleep & Battery Saver (Android)  
  https://help.resilio.com/hc/en-us/articles/204762699-Configuring-Auto-Sleep-Battery-Saver-Android

- Sharing files (Android)  
  https://help.resilio.com/hc/en-us/articles/115000409690-Sharing-files-Android

- Sharing files (iOS)  
  https://help.resilio.com/hc/en-us/articles/115001717390-Sharing-files-iOS

- Storage Management on iOS  
  https://help.resilio.com/hc/en-us/articles/115001726304-Storage-Management-on-iOS

- Sync interface on Android  
  https://help.resilio.com/hc/en-us/articles/213500383-Sync-interface-on-Android

- Initiate sharing on mobile platforms  
  https://help.resilio.com/hc/en-us/articles/207370636-Initiate-sharing-on-mobile-platforms

- How to Back up data (Android only)  
  https://help.resilio.com/hc/en-us/articles/204762339-How-to-Back-up-data-Android-only

## Revision addendum — service promotion, remote-path honesty, declaration branching, and closure truth

This revision intentionally leaned on another small cluster of current official Resilio docs because they expose a different class of non-clone reason than the earlier power, reclaim, and mobile-seat passes.
The new questions were:

> where do current official docs prove that **service promotion** still branches between same-node continuity and clean background world creation rather than a simple `run in background` toggle?

> what current documentation most clearly proves that **a reachable path** can still lose strong local-change detection and fall back to rescan or restart ritual?

> where do current official docs show that **declarative configuration** still narrows capability and can override or disable the ordinary live control surface?

> how do current docs prove that **uninstall/offboard** still mixes peer departure, storage cleanup, hidden share-local residue, and platform-forced copy loss rather than one explicit closure plan?

The most load-bearing source set for this pass was the maintained v3 change log together with docs on Windows service install and troubleshooting, configuration mode, storage folder paths, watcher-budget exhaustion, and uninstall guidance.

### Additional Resilio official sources emphasized in rev0138

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Running Sync as a service on Windows  
  https://help.resilio.com/hc/en-us/articles/207701296-Running-Sync-as-a-service-on-Windows

- Sync Service Troubleshooting on Windows  
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Sync Storage folder  
  https://help.resilio.com/hc/en-us/articles/206664690-Sync-Storage-folder

- Agent run out of system notify watchers. Updated files will be uploaded only after periodic folder rescan  
  https://help.resilio.com/hc/en-us/articles/360015593120-Agent-run-out-of-system-notify-watchers-Updated-files-will-be-uploaded-only-after-periodic-folder-rescan

- How to uninstall Sync?  
  https://help.resilio.com/hc/en-us/articles/204775029-How-to-uninstall-Sync

## Revision addendum — bootstrap authority, proxy asymmetry, memory relief, and self-seat narrowing

This revision intentionally leaned on another small cluster of current official Resilio docs because they expose a different class of non-clone reason than the earlier service, route, and restore passes.
The new questions were:

> where do current official docs prove that **discovery bootstrap authority** still lives in a fetched remote catalog and support-page reachability checks rather than one rendered dependency object?

> where do current docs show that **proxy posture** still changes directness asymmetrically and can make relay inevitable for some peer pairs?

> what current evidence most clearly shows that **memory relief** still broadens too quickly into remove-and-readd ritual with database loss?

> how do current docs prove that **narrowing one linked self-owned seat** still falls back to disconnect-plus-read-only-key ritual instead of one in-place rights edit?

The most load-bearing source set for this pass was the maintained v3 line together with docs on tracker/bootstrap failures, proxy behavior in preferences, linked-device ownership, read-only creation across linked devices, and out-of-memory guidance.

### Additional Resilio official sources emphasized in rev0139

- Peers aren't connecting  
  https://help.resilio.com/hc/en-us/articles/205450205-Peers-aren-t-connecting

- Cannot connect to trackers  
  https://help.resilio.com/hc/en-us/articles/210587126-Cannot-connect-to-trackers

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Out of memory  
  https://help.resilio.com/hc/en-us/articles/209724663-Out-of-memory

- User Management  
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- How to create a Read Only folder while syncing across linked devices?  
  https://help.resilio.com/hc/en-us/articles/206216565-How-to-create-a-Read-Only-folder-while-syncing-across-linked-devices

## Revision addendum — identity relabel, title overrides, route explanation, and global search

This revision intentionally leaned on another small cluster of current official Resilio docs because they expose a different class of non-clone reason than the earlier service, seat, and route-budget passes.
The new questions were:

> where do current official docs prove that **identity rename** still behaves like authority replacement rather than label correction?

> what current documentation most clearly proves that **share title** can diverge across disk name, UI override, and one-off outgoing artifact label?

> where do current official docs show that **route/performance truth** still requires crossing relay docs, speed advice, and performance graphs?

> how do current docs prove that **search** still depends on the pane or platform you happen to be in?

The most load-bearing source set for this pass was the maintained v3 line together with docs on identity-name changes, custom share names, performance overview, direct-vs-relayed speed guidance, relay behavior, ports/protocols, main-view/peer/license/iOS search, and move/rename behavior.

### Additional Resilio official sources emphasized in rev0141

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Can I change the name of my Sync identity?  
  https://help.resilio.com/hc/en-us/articles/206163443-Can-I-change-the-name-of-my-Sync-identity

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Setting custom name for sync shares  
  https://help.resilio.com/hc/en-us/articles/360011865879-Setting-custom-name-for-sync-shares

- Can I move or rename a syncing folder?  
  https://help.resilio.com/hc/en-us/articles/205450655-Can-I-move-or-rename-a-syncing-folder

- Performance overview  
  https://help.resilio.com/hc/en-us/articles/360001331930-Performance-overview

- How can I improve data transfer/sync speed?  
  https://help.resilio.com/hc/en-us/articles/204762319-How-can-I-improve-data-transfer-sync-speed

- What is a Relay Server?  
  https://help.resilio.com/hc/en-us/articles/204754779-What-is-a-Relay-Server

- What ports and protocols are used by Sync?  
  https://help.resilio.com/hc/en-us/articles/204754759-What-ports-and-protocols-are-used-by-Sync

- How do I perform a search in Sync?  
  https://help.resilio.com/hc/en-us/articles/205457725-How-do-I-perform-a-search-in-Sync

- Does Sync work in background?  
  https://help.resilio.com/hc/en-us/articles/206816823-Does-Sync-work-in-background

## Revision addendum — attention delivery, entitlement cliffs, upgrade visibility, and self-serve diagnostics

This revision intentionally leaned on another small cluster of current official Resilio docs because they expose a different class of non-clone reason than the earlier rename, route, and intake passes.
The new questions were:

> where do current official docs prove that **attention delivery** still depends on surface and platform quirks rather than one product-native delivery grade?

> where do current docs show that **entitlement expiry** still has operational fallout for real workflows rather than just billing meaning?

> what current evidence most clearly shows that **upgrade visibility** still differs by surface, especially between desktop and WebUI/headless usage?

> where do current docs prove that **diagnostics and support** still rely on hidden log paths, restart ritual, and support-boundary lore rather than one export workflow?

The most load-bearing source set for this pass was the maintained v3 line together with docs on desktop preferences, main-view attention affordances, Linux peculiarities, mobile notification/background behavior, Business-trial/license expiry, local shares, update checks and rollout caveats, manual debug-log collection, and power-user log/profiler settings.

### Additional Resilio official sources emphasized in rev0142

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Sync Main View (Desktop)  
  https://help.resilio.com/hc/en-us/articles/204755009-Sync-Main-View-Desktop

- Guide to Linux, and Sync peculiarities  
  https://help.resilio.com/hc/en-us/articles/204762449-Guide-to-Linux-and-Sync-peculiarities

- Settings on mobile platforms  
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- What happens when Sync Business trial or license expires?  
  https://help.resilio.com/hc/en-us/articles/206216825-What-happens-when-Sync-Business-trial-or-license-expires

- Sharing a folder locally  
  https://help.resilio.com/hc/en-us/articles/360011582500-Sharing-a-folder-locally

- Updating Sync to latest version  
  https://help.resilio.com/hc/en-us/articles/115001130830-Updating-Sync-to-latest-version

- Collecting debug logs manually  
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

## Revision addendum — comparative datacube influences in rev0145

This revision was not driven only by public Resilio evidence.
It also deliberately cross-read the uploaded comparison archives to see whether any non-AnonSync patterns were strong enough to deserve import.

The most direct comparative influences were:

- **DelayBasin rev0093** — for the argument that several simultaneously eligible explanations should preserve a compact tie set, arbitration witness, fallback surface, and abstention budget instead of forcing one silent winner
- **SlopOS rev0545** — for the argument that visible facts need authorship buckets before confidence or policy layers can be interpreted honestly
- **DeriveBSD rev0323** — for the lane-exactness pressure that once a surface claims a scope or authority class, adjacent fields should not quietly contradict that claim
- **Hyperepo rev0242** — for the insistence that browser history behavior, push-versus-replace decisions, and back-forward continuity deserve first-class specification
- **Micromax rev0401** — for the insistence that miss surfaces preserve the initiating action and target class instead of collapsing into generic failure copy
- **The Election Stack rev0524** — for the discipline that transient message delivery must never become the sole durable source of controlling meaning

These are comparative design influences, not implementation dependencies.
They were used to tighten AnonSync's own interface laws, not to widen its scope.

## Revision addendum — diagnostics, packet freeze, and outside-step follow-up in rev0146

This revision again used both comparative datacube reading and current public source review, but the scope stayed narrow on purpose.
The question was not `what other big subsystem should AnonSync absorb?`
The real question was:

> what evidence proves that the existing diagnostics/support lane still hides too much meaning about **when capture is active**, **when evidence becomes disclosure**, and **when the next honest step lives outside the product and must later be rejoined**?

### Comparative datacube influences emphasized in rev0146

The most direct comparative influences were:

- **DeriveBSD rev0323** — for the pressure to make support and follow-up lanes timeline-first, scope-exact, and safe-open rather than generic request buckets
- **Radical-Governance rev0416** — for the discipline that private logs, restricted backstage review, and portable outward packets should remain distinct objects with clear audience boundaries
- **EvidenceVault rev0484** — for the insistence that anything leaving the local truth boundary needs a frozen public surface rather than a mutable live view
- **Anonymity rev0425** — for the reminder that `no release` and narrow outward publication are real healthy outcomes, not merely incomplete workflows
- **pyCausalWeave rev0075** — for the argument that external blockers and stale follow-ups need typed request/return objects rather than disappearing into notes or chat memory

These are comparative design influences, not implementation dependencies.
They were used to sharpen AnonSync's existing diagnostics/support seam, not to widen the product.

### Additional official Resilio sources emphasized in rev0146

The most relevant current official sources for this pass were the maintained support docs around logs, crash dumps, and manual escalation ritual:

- Collecting debug logs manually  
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

- Settings on mobile platforms  
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- Sync v3 automatic logs collection  
  https://help.resilio.com/hc/en-us/articles/115001172124-Sync-v3-automatic-logs-collection

- How to increase log size in Sync  
  https://help.resilio.com/hc/en-us/articles/207548995-How-to-increase-log-size-in-Sync

- Crash dumps  
  https://help.resilio.com/hc/en-us/articles/360001335340-Crash-dumps

The value of these sources is not that AnonSync should clone their exact support procedures.
The value is that they still expose a familiar sync-product failure mode: support truth is distributed across hidden paths, restarts, manual bundle collection, mobile extraction steps, optional higher log volume, and separate crash-dump retrieval instead of one product-native evidence / freeze / disclose / follow-up grammar.

## Revision addendum — reapproval triggers and current-head registers in rev0147

This pass again used both comparative datacube reading and a small current public-source check, but the scope stayed narrow on purpose.
The question was not `what new subsystem should AnonSync absorb?`
The real question was:

> what evidence proves that remembered approval should reopen on basis drift, and that retained shareable artifacts need one compact current-head register instead of lineage folklore?

### Comparative datacube influences emphasized in rev0147

The most direct comparative influences were:

- **Goldenrule rev0323** — for the compact lineage-head register idea that distinguishes latest operational tip from a stricter citation-ready or freeze-ready head and preserves warnings when the answer is not unique
- **EvidenceVault rev0484** — for the discipline of keeping a tiny `Current documents` surface rather than forcing inheritors to reconstruct what is current from the whole retained archive
- **Radical-Governance rev0416** — for the argument that approvals are perishable, should reopen after material change, and should face periodic reapproval even without an explicit trigger report

These are comparative design influences, not implementation dependencies.
They were used to tighten AnonSync's existing remembered-trust and retained-artifact seams, not to widen the product.

### Additional current public source emphasized in rev0147

The most relevant current public source for this pass was the OpenSSH manual behavior around changed host identity: when a host key changes, `ssh` warns and disables password authentication rather than quietly inheriting prior trust.
That is useful here not because AnonSync should mimic OpenSSH UX exactly, but because it reinforces the underlying design law that remembered trust should become guarded or reopened when a key trust basis changes rather than drifting forward silently.

- OpenBSD `ssh(1)` manual — changed host identification warning / stricter behavior  
  https://man.openbsd.org/ssh.1

## Revision addendum — approval roster versus live request truth in rev0148

This revision was driven by one narrow comparative question rather than broad new public-web research:

> where do the comparison archives and current platform docs most clearly show that **reviewer / approver presence is not the same thing as a current live request**, and that later changes need **explicit rerequest** instead of quiet continuity?

The most direct comparative influence was:

- **pyCausalWeave rev0075** — for the pressure that reviewer-roster continuity, active review request, completed review, and later rerequest after head drift should remain separate truths rather than one flattened reviewer state

The most relevant current platform sources for this pass were:

- GitHub Docs — About pull request reviews
  https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews

- GitLab Docs — Merge request reviews
  https://docs.gitlab.com/user/project/merge_requests/reviews/

Their value here is not that AnonSync should mimic pull-request UX.
Their value is that they reinforce one reusable coordination law: systems can keep reviewer / approver continuity visible while still requiring an explicit current request and an explicit rerequest after later changes.

## Revision addendum — frozen guidance basis and fetch-boundary truth in rev0149

This revision was driven by one narrow comparative question rather than a broad new subsystem sweep:

> where do the comparison archives and current official troubleshooting surfaces most clearly show that a **live source locator** is not the same thing as an exact **frozen review basis**, and that later drift must not silently rewrite what local translation was grounded on?

The most direct comparative influences were:

- **TriKEM rev0260** — for the fail-closed discipline that reviewed authority host, successful fetch posture, exact reviewed bytes, and downstream imported claims are separate gates rather than one `trusted source` answer
- **EvidenceVault rev0484** — for the discipline that working candidates, ready-to-publish material, and frozen public surface are different objects and that current public meaning should point at the frozen surface rather than the mutable working tree
- **Radical-Governance rev0416** — for the pressure to keep restricted/private material, outward packets, and public-facing summaries as different surfaces with different audiences and different drift obligations

These are comparative design influences, not implementation dependencies.

The most relevant current official Resilio sources for this pass were the maintained troubleshooting and settings pages that still route operators through live help-center articles for enabling debug logs, enlarging log size, changing power-user settings, and even manually extracting NAS logs over SSH/SCP:

- Collecting debug logs manually  
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Increasing Debug Log size  
  https://help.resilio.com/hc/en-us/articles/205450145-Increasing-Debug-Log-size

- How to collect logs on NAS manually?  
  https://help.resilio.com/hc/en-us/articles/208800446-How-to-collect-logs-on-NAS-manually

- Errors & Troubleshooting  
  https://help.resilio.com/hc/en-us/categories/200410985-Errors-Troubleshooting

Their value here is not that AnonSync should clone those exact procedures.
Their value is that they reinforce one reusable product law: when troubleshooting depends on mutable live pages, hidden storage paths, copied commands, or platform-specific extraction instructions, the product should preserve the exact fetched copy and exact reviewed excerpts that local translation actually relied on instead of pretending one live link is the entire stable basis.

## Revision addendum — status bridge and follow-through claim truth in rev0150

This revision again used both comparative datacube reading and current public source review, but the scope stayed narrow on purpose.
The question was not `what other subsystem should AnonSync absorb?`
The real question was:

> what evidence proves that AnonSync still needs one lighter everyday status-proof scale before a full dossier, and one stricter middle seam where partial outside progress is not yet a whole-fix claim?

### Comparative datacube influences emphasized in rev0150

The most direct comparative influences were:

- **VHK rev0348** — for the insistence that a product should expose one lighter installed/runtime status bridge before support escalates to a fuller dossier, and that `ready`, `not ready`, `unavailable`, and `error` remain different operator truths
- **Rust-Crate-Dreams rev0277** — for the follow-through coverage pressure that a machine-observed source fix may still leave manifest/docs/feature follow-through unfinished, which translated cleanly into AnonSync's outside-step and repair lanes
- **Rust-Needs-and-Dreams rev0302** — for the larger execution-evidence posture that run/request/effect truth should stay machine-readable and reviewable instead of dissolving into one vague success state
- **pyCausalWeave rev0075** — for the continuing pressure that traceability is strongest when compact claims point back to explicit supporting rows instead of ambient confidence

These are comparative design influences, not implementation dependencies.

### Current official Linux/service-manager sources most relevant to this pass

The most relevant current official sources for this pass were the systemd / logind manuals that distinguish human-oriented `status` output from machine-readable `show` properties and that preserve condition and result fields as first-class runtime facts:

- systemctl(1)  
  https://www.freedesktop.org/software/systemd/man/systemctl.html

- org.freedesktop.systemd1(5)  
  https://man7.org/linux/man-pages/man5/org.freedesktop.systemd1.5.html

- loginctl(1)  
  https://man7.org/linux/man-pages/man1/loginctl.1.html

Their value here is not that AnonSync should clone systemd UX.
Their value is that they reinforce two reusable product laws:

1. one lighter machine-readable status bridge can answer many everyday operator questions before a full dossier is necessary
2. request/start/result/condition/effect facts should remain distinct long enough that later follow-through and claim strength can be stated honestly

## Revision addendum — outbound channel execution and delivery-claim truth in rev0151

This revision again used both comparative datacube reading and current public-source review, but the scope stayed narrow on purpose.
The question was not `should AnonSync become a messaging or delivery-tracking system?`
The real question was:

> what evidence proves that a frozen artifact, a local outbound channel completion, and a real recipient-side receipt are different truths that deserve different labels and different claim ceilings?

### Comparative datacube influences emphasized in rev0151

The most direct comparative influences were:

- **EvidenceVault rev0484** — for the discipline that a queued or candidate outward artifact, an executed release/publication event, and the frozen public surface snapshot are different objects that should point to one another instead of collapsing into one vague `published` state
- **The-Election-Stack rev0524** — for the continuing pressure that transient visible completion should not become the only durable home of meaning once the operator later asks what actually happened
- **Hyperepo rev0242** and **Micromax rev0401** — for the broader browser-local pressure that transport and navigation gestures must preserve what they really witnessed rather than letting UI convenience flatten history

These are comparative design influences, not implementation dependencies.

### Current official browser-platform sources most relevant to this pass

The most relevant current sources for this pass were MDN's current Clipboard and Web Share documentation:

- Clipboard `writeText()` — resolves once the system clipboard has been updated
  https://developer.mozilla.org/en-US/docs/Web/API/Clipboard/writeText

- Web Share API — `navigator.share()` resolves if the data was successfully sent to a share target and requires transient activation
  https://developer.mozilla.org/en-US/docs/Web/API/Web_Share_API

- `Navigator.share()` platform note — on Windows the promise resolves when the share popup launches, while on Android it resolves once the data has successfully been passed to the share target
  https://developer.mozilla.org/en-US/docs/Web/API/Navigator/share

Their value here is not that AnonSync should clone browser API vocabulary directly.
Their value is that they reinforce one reusable product law:

1. different outbound channels complete at different semantic moments
2. the product should publish the strongest delivery label that the current witness actually supports
3. later stronger witness import should raise the claim ceiling explicitly rather than quietly rewriting earlier channel history

## Revision addendum — startup owner, duplicate-launch risk, and drift truth in rev0153

This revision again used both comparative datacube reading and current public-source review, but the scope stayed narrow on purpose.
The question was not `should AnonSync become a generic init-manager?`
The real question was:

> what evidence proves that install readiness, service continuity, current runtime health, and actual startup ownership are different truths that deserve different objects and different receipts?

### Comparative datacube influences emphasized in rev0153

The most direct comparative influences were:

- **VHK rev0348** — for the pressure that installed startup truth needs one compact owner answer, not just runtime health plus scattered service-manager clues
- **DeriveBSD rev0323** — for the broader evidence posture that configuration, execution, and operational reality should produce receipts rather than ambient assumptions
- **GlassTTY rev0123** — for the continuing support-truth discipline that claims should stay lane-specific and evidence-bearing instead of collapsing into one vague supported/working label

These are comparative design influences, not implementation dependencies.

### Current official startup / service-manager sources most relevant to this pass

The most relevant current sources for this pass were current systemctl, XDG autostart, and systemd XDG-autostart documentation:

- systemctl(1) — `is-enabled` distinguishes states such as `static`, `indirect`, `generated`, `transient`, and `disabled`, which means startup ownership is not one simple boolean
  https://man7.org/linux/man-pages/man1/systemctl.1.html

- Desktop Application Autostart Specification — `Hidden=true` means the entry must be ignored and `TryExec` means an entry must not autostart if the target executable is not available
  https://specifications.freedesktop.org/autostart/0.5/

- systemd-xdg-autostart-generator — XDG autostart entries may themselves become generated systemd user services in desktops that opt into that model
  https://www.freedesktop.org/software/systemd/man/systemd-xdg-autostart-generator.html

Their value here is not that AnonSync should clone systemd or desktop-environment UX.
Their value is that they reinforce one reusable product law:

1. startup ownership can exist in several different classes at once
2. conditional or generated startup lanes do not mean the same thing as ordinary explicit enablement
3. healthy current runtime is not enough to prove safe automatic return later
4. the product should publish the strongest startup-owner verdict that current host evidence actually supports

## Revision addendum — reviewed-action basis guard and stale-attempt truth in rev0154

This revision again used both comparative datacube reading and current official-source review, but the scope stayed narrow on purpose.
The question was not `should AnonSync become a generic workflow engine?`
The real question was:

> what evidence proves that a reviewed draft, queue-worthy action, or apply-ready click should remain scoped to the exact basis it was reviewed against, and that later drift should surface stale-attempt / reissue instead of silent inheritance or silent disappearance?

### Comparative datacube influences emphasized in rev0154

The most direct comparative influences were:

- **pyCausalWeave rev0075** — for the explicit pressure that approval, merge-request, and queue-entry truths remain head-scoped and should surface rerequest / requeue when that head drifts
- **Goldenrule rev0323** — for the continuing pressure that compact head registers and publication contracts should keep current-head truth explicit enough that later outward actions do not rely on ambient `latest` folklore
- **EvidenceVault rev0484** — for the discipline that working candidate material, queued/publish intent, and frozen public surface are different objects and that later outward acts should point to explicit frozen/current objects instead of vague currentness

These are comparative design influences, not implementation dependencies.

### Current official platform sources most relevant to this pass

The most relevant current sources for this pass were GitHub's current GraphQL input-object docs and GitLab's current merge / approval / status-check docs that all preserve explicit current-head compare-and-set semantics:

- GitHub GraphQL input objects — `expectedHeadOid` appears on pull-request auto-merge enablement, queue entry, and branch-update mutations
  https://docs.github.com/en/graphql/reference/input-objects

- GitLab merge request approvals API — the `sha` parameter ensures approval of the current HEAD commit SHA and returns `409 Conflict` on mismatch
  https://docs.gitlab.com/api/merge_request_approvals/

- GitLab merge request API — merge-request resources publish current diff/head SHA information and use SHA-sensitive operations for merge-time safety
  https://docs.gitlab.com/api/merge_requests/

- GitLab external status checks — stale responses against non-current HEAD return `409 Conflict`
  https://docs.gitlab.com/user/project/merge_requests/status_checks/

Their value here is not that AnonSync should clone pull-request UX.
Their value is that they reinforce one reusable product law:

1. reviewed or requested actions can be compare-and-set against an expected current basis
2. stale attempts should fail closed with explicit repair instead of silently inheriting newer state
3. queued, approved, and ready states are only honest while the basis they refer to is still the one that is current

## Revision addendum — disclosure register and current outward-surface truth in rev0156

This revision again used both comparative datacube reading and current public-source review, but the scope stayed narrow on purpose.
The question was not `should AnonSync become a generic release manager or messaging product?`
The real question was:

> what evidence proves that a newer frozen head, a queued outward issue, an executed issue event, and the current outward surface are different truths that deserve different objects and different receipts?

### Comparative datacube influences emphasized in rev0156

The most direct comparative influences were:

- **EvidenceVault rev0484** — for the discipline that candidate queue state, executed publication, and stable public surface are different objects that should point to one another instead of collapsing into one vague `published` state
- **Goldenrule rev0323** — for the continuing pressure that head registers and outward-facing summaries should keep `current` explicit instead of relying on ambient latestness
- **The-Election-Stack rev0524** — for the pressure that transient completion cues should not become the only durable home of outward-state truth once the operator later asks what is actually in force

These are comparative design influences, not implementation dependencies.

### Current official platform sources most relevant to this pass

The most relevant current sources for this pass were GitHub's current release-management docs:

- Managing releases in a repository — release creation starts as `Draft a new release`, and GitHub recommends creating immutable releases as drafts, attaching assets, then publishing
  https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository

- Releases REST API — `Get the latest release` returns the latest **published** full release and explicitly excludes draft releases
  https://docs.github.com/en/rest/releases/releases

- About releases — releases are deployable packaged iterations with their own release dates and assets, distinct from the underlying tag date
  https://docs.github.com/repositories/releasing-projects-on-github/about-releases

Their value here is not that AnonSync should clone GitHub release UX.
Their value is that they reinforce one reusable product law:

1. draft/candidate state is not the same as published/outward current state
2. an executed publish/issue event should be its own durable object
3. `latest outwardly in force` may lag behind `newest prepared thing` until that issue event actually occurs
4. later delivery or adoption evidence can remain separate from the outward-surface transition itself

## Revision addendum — Resilio borrow line and interface grammar after rev0164

This revision intentionally leaned on a narrower set of current official Resilio docs than some earlier passes.
The questions were:

> which current official Resilio pages most clearly prove that the product is still alive and worth learning from?

> which current pages most clearly show where we should **borrow the product idea** but **refuse the exact truth contract**?

The most load-bearing official source cluster for this pass was:

- the current v3 change log, which still shows active 2025 releases and UI work
- WebUI configuration and browser-warning docs, which keep browser-first local control practical while still externalizing endpoint trust into browser ritual
- browser-open failure docs, which still preserve manual paste as the durable fallback
- sync preferences and scheduler docs, which still spread effective rate truth across several layers
- folder-types, synchronization-modes, user-management, local-share, and encrypted-folder docs, which together show both how much Resilio got right and how many caveat clusters still surround local adoption, authority, same-host derivation, and ciphertext-only custody

### Additional official Resilio sources emphasized in rev0164

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Configuring WebUI  
  https://help.resilio.com/hc/en-us/articles/115001184490-Configuring-WebUI

- Browser warning "Your connection is not private"  
  https://help.resilio.com/hc/en-us/articles/4404757430291-Browser-warning-Your-connection-is-not-private

- Sync doesn't start when opening Link in browser  
  https://help.resilio.com/hc/en-us/articles/204753649-Sync-doesn-t-start-when-opening-Link-in-browser

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Running Sync on schedule  
  https://help.resilio.com/hc/en-us/articles/210783266-Running-Sync-on-schedule

- Folder Types and Management  
  https://help.resilio.com/hc/en-us/articles/204762459-Folder-Types-and-Management

- Synchronization Modes  
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- User Management  
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- Sharing a folder locally  
  https://help.resilio.com/hc/en-us/articles/360011582500-Sharing-a-folder-locally

- Encrypted folders  
  https://help.resilio.com/hc/en-us/articles/207370466-Encrypted-folders

- Windows Defender SmartScreen blocks Resilio Sync installer  
  https://help.resilio.com/hc/en-us/articles/360014486120-Windows-Defender-SmartScreen-blocks-Resilio-Sync-installer

## Revision addendum — current Resilio pages emphasized in rev0165

This revision intentionally stayed close to current official Resilio Sync pages because the task was not just to admire or criticize the product in general.
It was to decide where current evidence still does and does not earn interface cloning.

The most load-bearing official pages for this pass were:

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Configuring WebUI  
  https://help.resilio.com/hc/en-us/articles/115001184490-Configuring-WebUI

- Running Sync as a service on Windows  
  https://help.resilio.com/hc/en-us/articles/207701296-Running-Sync-as-a-service-on-Windows

- Browser warning "Your connection is not private"  
  https://help.resilio.com/hc/en-us/articles/4404757430291-Browser-warning-Your-connection-is-not-private

- How do I reset my WebUI password?  
  https://help.resilio.com/hc/en-us/articles/205450295-How-do-I-reset-my-WebUI-password

- Sync doesn't start when opening Link in browser  
  https://help.resilio.com/hc/en-us/articles/204753649-Sync-doesn-t-start-when-opening-Link-in-browser

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Running Sync on schedule  
  https://help.resilio.com/hc/en-us/articles/210783266-Running-Sync-on-schedule

- Synchronization Modes  
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- Encrypted folders  
  https://help.resilio.com/hc/en-us/articles/207370466-Encrypted-folders

- Sharing a folder locally  
  https://help.resilio.com/hc/en-us/articles/360011582500-Sharing-a-folder-locally

- Disconnecting and Removing Folders  
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

The practical synthesis for rev0165 was:

- Resilio still clearly earns borrowing for byte posture, delivery convenience, encrypted custody, same-host derivation, and Linux/browser practicality.
- Resilio still does **not** clearly earn direct page cloning for control trust, typed intake, effective rate truth, or install-to-ready bringup.
- Therefore the archive should answer those seams with replacement pages, not just critique.

## Revision addendum — current Resilio pages emphasized in rev0167

This revision intentionally leaned on current official Resilio pages that most clearly expose the remaining tension between good convenience and weak page boundaries.

The most load-bearing official pages for this pass were:

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Updating installation to Resilio Sync v3  
  https://help.resilio.com/hc/en-us/articles/31194252837779-Updating-installation-to-Resilio-Sync-v3

- FAQ Resilio Sync 3.0.0  
  https://help.resilio.com/hc/en-us/articles/32109883606035-FAQ-Resilio-Sync-3-0-0

- Can I connect two pre-populated pre-existing folders?  
  https://help.resilio.com/hc/en-us/articles/205506569-Can-I-connect-two-pre-populated-pre-existing-folders

- How to manually set the location of the folders synced across linked devices?  
  https://help.resilio.com/hc/en-us/articles/206216615-How-to-manually-set-the-location-of-the-folders-synced-across-linked-devices

- Folders are duplicating with an index (i) in their name.  
  https://help.resilio.com/hc/en-us/articles/204753869-Folders-are-duplicating-with-an-index-i-in-their-name

- User Management  
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- What's the difference between Standard and Advanced folders?  
  https://help.resilio.com/hc/en-us/articles/204754679-What-s-the-difference-between-Standard-and-Advanced-folders

- Sync functionality in detail  
  https://help.resilio.com/hc/en-us/articles/204754389-Sync-functionality-in-detail

- Setting custom name for sync shares  
  https://help.resilio.com/hc/en-us/articles/360011865879-Setting-custom-name-for-sync-shares

The practical synthesis for rev0167 was:

- Resilio still clearly earns borrowing for own-device linking convenience, pre-existing-byte reuse, mutable delegation, and flexible labeling.
- Resilio still does **not** clearly earn direct page cloning for identity joins, non-empty target intake, rights ceilings, or naming-scope truth.
- Therefore the archive should answer those seams with replacement pages, not just critique.

## Revision addendum — current Resilio pages emphasized in rev0168

This revision intentionally leaned on another tight cluster of current official Resilio pages because they expose one more non-clone pattern clearly:
strong operator ideas still sometimes live behind hidden service material, hidden rule files, storage-folder JSON, or partially authoritative list surfaces.

The most load-bearing official pages for this pass were:

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- What is '.sync' folder, and StreamsList, IgnoreList and Archive inside?  
  https://help.resilio.com/hc/en-us/articles/206217185-What-is-sync-folder-and-StreamsList-IgnoreList-and-Archive-inside

- Service files missing / Cannot identify destination folder  
  https://help.resilio.com/hc/en-us/articles/205450225-Service-files-missing-Cannot-identify-destination-folder

- Ignoring files in Sync (Ignore List)  
  https://help.resilio.com/hc/en-us/articles/205458165-Ignoring-files-in-Sync-Ignore-List

- Setting Delay Time For Syncing  
  https://help.resilio.com/hc/en-us/articles/207491426-Setting-Delay-Time-For-Syncing

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- File download priority  
  https://help.resilio.com/hc/en-us/articles/42328167759251-File-download-priority

- Folder Preferences  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- How to touch files?  
  https://help.resilio.com/hc/en-us/articles/209606046-How-to-touch-files

- Core warnings  
  https://help.resilio.com/hc/en-us/articles/360001217950-Core-warnings

The practical synthesis for rev0168 was:

- Resilio still clearly earns borrowing for explicit service material, exclusion policy, file-class delay windows, and queue prioritization.
- Resilio still does **not** clearly earn direct page cloning for hidden service-bundle integrity, hidden rule syntax, restart-bound timing knobs, or visible-vs-actual queue truth.
- Therefore the archive should answer those seams with replacement pages, not just critique.

## Revision addendum — current Resilio pages emphasized in rev0169

This revision intentionally leaned on another tight cluster of current official Resilio pages because they expose one more non-clone pattern clearly:
strong operator ideas still sometimes live behind shell-extension dependence, overloaded placeholder gestures, platform-asymmetric restore access, and fragmented filesystem-shape caveats.

The most load-bearing official pages for this pass were:

- Configuring WebUI  
  https://help.resilio.com/hc/en-us/articles/115001184490-Configuring-WebUI

- No Sync icons in the file browser/no Sync-related items in the context menu on Mac/Windows  
  https://help.resilio.com/hc/en-us/articles/206214625-No-Sync-icons-in-the-file-browser-no-Sync-related-items-in-the-context-menu-on-Mac-Windows

- What Is an RSLS File?  
  https://help.resilio.com/hc/en-us/articles/206115384-What-Is-an-RSLS-File

- Synchronization Modes  
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Disconnecting and Removing Folders  
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- Using Archive for file versioning and restoring deleted files.  
  https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files

- Soft links, hard links and symbolic links  
  https://help.resilio.com/hc/en-us/articles/205504529-Soft-links-hard-links-and-symbolic-links

- Alt Streams and Xattrs in Sync  
  https://help.resilio.com/hc/en-us/articles/204754729-Alt-Streams-and-Xattrs-in-Sync

- My files don't sync  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

The practical synthesis for rev0169 was:

- Resilio still clearly earns borrowing for on-demand bytes, shell accelerators, retained history, and fidelity-aware treatment of links and metadata.
- Resilio still does **not** clearly earn direct page cloning for shell-dependent action parity, overloaded placeholder/delete gestures, restore access parity, or filesystem-shape truth.
- Therefore the archive should answer those seams with replacement pages, not just critique.

## Revision addendum — current Resilio pages emphasized in rev0170

This revision intentionally leaned on another compact cluster of current official Resilio docs because they expose a quieter but still important class of non-clone reason.
The new questions were:

> where do current official docs most clearly spell out **which outside infrastructure can learn which facts**, and where do they still require the operator to reconstruct one privacy/observer answer from several separate pages?

> where do current official docs most clearly show that **local state root continuity** is real, path-dependent, profile-dependent, and unsafe to treat as a generic app clone?

The most useful current source cluster this time was:

- `Can others see my files? How secure is sharing by Resilio Sync?`
- `Can Resilio team see and block/remove any Sync folders?`
- `What is a Relay Server?`
- `What ports and protocols are used by Sync?`
- `Link structure and flow`
- `Sync Storage folder`
- `Running Sync in configuration mode`
- `Cloning Sync`
- `Sync Service Troubleshooting on Windows`

### Current official Resilio pages emphasized in rev0170

- Can others see my files? How secure is sharing by Resilio Sync?  
  https://help.resilio.com/hc/en-us/articles/205451025-Can-others-see-my-files-How-secure-is-sharing-by-Resilio-Sync

- Can Resilio team see and block/remove any Sync folders?  
  https://help.resilio.com/hc/en-us/articles/205451105-Can-Resilio-team-see-and-block-remove-any-Sync-folders

- What is a Relay Server?  
  https://help.resilio.com/hc/en-us/articles/204754779-What-is-a-Relay-Server

- What ports and protocols are used by Sync?  
  https://help.resilio.com/hc/en-us/articles/204754759-What-ports-and-protocols-are-used-by-Sync

- Link structure and flow  
  https://help.resilio.com/hc/en-us/articles/204754739-Link-structure-and-flow

- Sync Storage folder  
  https://help.resilio.com/hc/en-us/articles/206664690-Sync-Storage-folder

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Cloning Sync  
  https://help.resilio.com/hc/en-us/articles/360018421940-Cloning-Sync

- Sync Service Troubleshooting on Windows  
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

The practical synthesis for rev0170 was:

- Resilio is admirably explicit that tracker sees addresses/ports/share IDs, relay carries encrypted traffic, landing pages can count clicks without receiving the anchor-fragment payload, and telemetry/update/account services are distinct infrastructure contacts
- Resilio is also admirably explicit that ordinary content stays on user devices and that the vendor cannot simply remove user folder content
- but the operator still has to reconstruct those truths from several separate pages rather than one stable infrastructure-visibility or service-role page
- the same pattern holds locally: storage roots are documented, config mode can create a new implicit `.sync` world, service-user changes can produce a different storage root and an apparently empty inventory, and plain cloning is unsupported
- that is a strong reason for AnonSync to borrow the honesty while replacing the page contracts with explicit **Infrastructure visibility**, **Service role**, **State root**, and **Attach state** pages

## Revision addendum — current Resilio pages emphasized in rev0171

This revision intentionally leaned on another compact cluster of current official Resilio docs because they expose a different but still important class of non-clone reason.
The new questions were:

> where do current official docs most clearly show that **helper policy is real but still split across folder scope, global scope, config scope, and troubleshooting scope**?

> where do current official docs most clearly show that **bootstrap/catalog provenance and cached route residue are operationally real**, especially when narrowing toward LAN-only or manual-host-only behavior?

> where do current official docs most clearly show that **background cadence** — notifications, periodic rescans, helper refresh, settings saves, and logging — still determines whether a host feels fresh, stale, awake, or quiet?

The most useful current source cluster this time was:

- `Folder Preferences`
- `Sync Preferences`
- `Running Sync in configuration mode`
- `Can I force Sync to do local network (LAN) syncing only and not sync via the Internet?`
- `Peers aren't connecting`
- `Cannot connect to trackers`
- `What ports and protocols are used by Sync?`
- `What is a Relay Server?`
- `How soon does synchronization start?`
- `Agent run out of system notify watchers. Updated files will be uploaded only after periodic folder rescan`
- `Sync prevents HDD from sleeping on NAS...`
- `Power user preferences`

### Current official Resilio pages emphasized in rev0171

- Folder Preferences  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Can I force Sync to do local network (LAN) syncing only and not sync via the Internet?  
  https://help.resilio.com/hc/en-us/articles/204754349-Can-I-force-Sync-to-do-local-network-LAN-syncing-only-and-not-sync-via-the-Internet

- Peers aren't connecting  
  https://help.resilio.com/hc/en-us/articles/205450205-Peers-aren-t-connecting

- Cannot connect to trackers  
  https://help.resilio.com/hc/en-us/articles/210587126-Cannot-connect-to-trackers

- What ports and protocols are used by Sync?  
  https://help.resilio.com/hc/en-us/articles/204754759-What-ports-and-protocols-are-used-by-Sync

- What is a Relay Server?  
  https://help.resilio.com/hc/en-us/articles/204754779-What-is-a-Relay-Server

- How soon does synchronization start?  
  https://help.resilio.com/hc/en-us/articles/204754319-How-soon-does-synchronization-start

- Agent run out of system notify watchers. Updated files will be uploaded only after periodic folder rescan  
  https://help.resilio.com/hc/en-us/articles/360015593120-Agent-run-out-of-system-notify-watchers-Updated-files-will-be-uploaded-only-after-periodic-folder-rescan

- Sync prevents HDD from sleeping on NAS...  
  https://help.resilio.com/hc/en-us/articles/205449995-Sync-prevents-HDD-from-sleeping-on-NAS

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

The practical synthesis for rev0171 was:

- Resilio still clearly earns borrowing for real helper control: subject-level tracker/relay/LAN/predefined-host policy, explicit proxy limits, and candid bootstrap/tracker/relay troubleshooting
- Resilio also still clearly earns borrowing for operational honesty around notifications, periodic rescans, watcher exhaustion, and the fact that logging/refresh/save cadence can keep a NAS awake
- but the operator still has to reconstruct the effective helper story from folder preferences, global preferences, configuration mode, LAN-only recipes, and failure articles rather than one stable helper-policy page
- and the operator still has to reconstruct the wakefulness/freshness story from change-detection docs, watcher warnings, power-user keys, and NAS troubleshooting rather than one stable host-cadence page
- that is a strong reason for AnonSync to borrow the flexibility and honesty while replacing the page contracts with explicit **Helper policy**, **Bootstrap source**, **Helper dependence**, and **Host cadence** pages

## Revision addendum — health, repair, and crash-capture page contracts after rev0173

This revision intentionally leaned on another compact cluster of current official Resilio docs because they expose a different class of non-clone reason than the earlier capability, helper, and lineage passes.
The new questions were:

> where do current official docs prove that **issue classification** still begins in warning rows and article hops rather than one stable page?

> where do current official docs show that **environment conflict** still mixes lock pressure, delay windows, weak notifications, and unsafe foreign-writer topology across several pages?

> what current documentation most clearly proves that **repair sequencing** is practical but still scattered across restart / reconnect / re-add / delete-hidden-state ladders rather than one product-owned repair page?

> where do current official docs show that **crash/evidence capture** still depends on hidden storage roots, service-account path differences, restart/reproduction ritual, and self-serve support boundaries?

The most load-bearing source set for this pass was the maintained v3 line together with docs on status-driven troubleshooting, locked files, delay tuning, SMB file shares, database error repair, service-files-missing repair, storage-folder paths, debug-log collection, log-size guidance, and crash/core-dump collection.

### Additional Resilio official sources emphasized in rev0173

- My files don't sync  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Some internal tasks are taking time to complete  
  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete

- Locked files  
  https://help.resilio.com/hc/en-us/articles/205504549-Locked-files

- Setting Delay Time For Syncing  
  https://help.resilio.com/hc/en-us/articles/207491426-Setting-Delay-Time-For-Syncing

- Sync and SMB file shares  
  https://help.resilio.com/hc/en-us/articles/207755736-Sync-and-SMB-file-shares

- How soon does synchronization start?  
  https://help.resilio.com/hc/en-us/articles/204754319-How-soon-does-synchronization-start

- Database error  
  https://help.resilio.com/hc/en-us/articles/204753659-Database-error

- Service files missing / Cannot identify destination folder  
  https://help.resilio.com/hc/en-us/articles/205450225-Service-files-missing-Cannot-identify-destination-folder

- Sync Storage folder  
  https://help.resilio.com/hc/en-us/articles/206664690-Sync-Storage-folder

- Collecting debug logs manually  
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

- Collecting crash reports, mini-dumps and core dumps  
  https://help.resilio.com/hc/en-us/articles/206214615-Collecting-crash-reports-mini-dumps-and-core-dumps

- Increasing Debug Log size  
  https://help.resilio.com/hc/en-us/articles/205450145-Increasing-Debug-Log-size

The practical synthesis for rev0173 was:

- Resilio is helpfully candid that warnings often point at real issue families rather than a fake all-purpose `sync error`
- Resilio is also candid that local locks, editor delay windows, SMB/direct mixed access, and weak notifications are real environment conflicts that change what is safe
- Resilio still offers practical repair ladders for database and service-material damage, but the operator must reconstruct the least-destructive order from several pages
- crash and evidence capture are real and documented, but they still begin in hidden storage/service paths, restart ritual, and self-serve support instructions rather than one ordinary product-owned page
- that is a strong reason for AnonSync to borrow the candor and pragmatism while replacing the page contracts with explicit **Issue home**, **Environment conflict**, **Repair plan**, and **Crash capture** pages

## Revision addendum — surface parity, external edit, background delivery, and mobile storage after rev0175

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about platform asymmetry, copy-based external editing, background delivery limits, and mobile storage semantics.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly honest about different surface capabilities across desktop, Linux/WebUI, Android, and iOS?

> where do those same current docs still show that the ordinary operator answer about `can I do this here?`, `am I editing a live object or a copy?`, `will this keep syncing in the background?`, and `what exactly does clear/remove free locally?` still depends on several platform articles instead of one stable product-owned page?

The most load-bearing source set for this pass was:

- Resilio's current Linux/WebUI notes, which still say Linux has no OS integration, no tray icon, no notifications outside Sync UI, and ordinary sharing/license entry flows through `Enter a key or link`.
- Resilio's current Android/iOS interface pages, which still expose materially different share-detail verbs, network controls, and local cleanup behavior.
- Resilio's current iOS peculiarity and edit guides, which still say external-app editing is copy-based and that deletions from iOS may simply un-sync locally.
- Resilio's current background, auto-sleep, battery-saver, simple-mode, and network-interface notes, which still spread unattended-freshness truth across several mobile/platform articles.
- Resilio's current iOS storage and sharing pages, which still split sandbox storage, downloads, shared-link residue, and local cleanup/history semantics across multiple surfaces.

## Additional Resilio official sources emphasized in rev0175

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Guide to Linux, and Sync peculiarities  
  https://help.resilio.com/hc/en-us/articles/204762449-Guide-to-Linux-and-Sync-peculiarities

- Does Sync work in background?  
  https://help.resilio.com/hc/en-us/articles/206816823-Does-Sync-work-in-background

- Sync interface on Android  
  https://help.resilio.com/hc/en-us/articles/213500383-Sync-interface-on-Android

- Sync Interface on iOS devices  
  https://help.resilio.com/hc/en-us/articles/212016726-Sync-Interface-on-iOS-devices

- Sync for iOS Peculiarities  
  https://help.resilio.com/hc/en-us/articles/205506539-Sync-for-iOS-Peculiarities

- How to edit a document stored in Sync? (iOS)  
  https://help.resilio.com/hc/en-us/articles/204762379-How-to-edit-a-document-stored-in-Sync-iOS

- Storage Management on iOS  
  https://help.resilio.com/hc/en-us/articles/115001726304-Storage-Management-on-iOS

- Sharing files (iOS)  
  https://help.resilio.com/hc/en-us/articles/115001717390-Sharing-files-iOS

- Configuring Auto Sleep & Battery Saver (Android)  
  https://help.resilio.com/hc/en-us/articles/204762699-Configuring-Auto-Sleep-Battery-Saver-Android

- Simple Mode (Android)  
  https://help.resilio.com/hc/en-us/articles/205458155-Simple-Mode-Android

- Selective Sync (Mobile)  
  https://help.resilio.com/hc/en-us/articles/206217315-Selective-Sync-Mobile

- Setting network interface per share  
  https://help.resilio.com/hc/en-us/articles/360001411244-Setting-network-interface-per-share

- Syncing between a desktop computer and a mobile device  
  https://help.resilio.com/hc/en-us/articles/205451165-Syncing-between-a-desktop-computer-and-a-mobile-device

# Source notes through rev0181

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was a transport-and-reachability cluster of current official Resilio Sync docs.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid about listening ports, direct-versus-relay behavior, helper toggles, proxies, and manual endpoint pins?

> where do those same docs still show that the ordinary operator answer about `what endpoint is live?`, `what route really won?`, `what safe repair rung should I try first?`, and `which endpoint claim is trustworthy enough to pin?` still depends on hopping across Preferences, Folder Preferences, mobile helper settings, ports/protocols notes, and troubleshooting articles rather than one stable page?

The most load-bearing source set for this pass was:

- Resilio's current Preferences and power-user docs, which still make listening port, UPnP/NAT-PMP, proxy posture, bind-interface, and external-port facts real but split them across ordinary and advanced settings.
- Resilio's current Folder Preferences and mobile interface docs, which still expose relay, tracker, LAN discovery, and predefined-host controls on multiple surfaces.
- Resilio's current ports/protocols and security docs, which still spell out tracker publication, relay fallback, LAN multicast/broadcast, and manual/direct endpoint expectations.
- Resilio's current troubleshooting docs, which still explain bootstrap catalog failure, blocked tracker access, blocked listening ports, blocked relay access, multicast/VPN/subnet issues, multiple-NIC issues, and proxy constraints — but as support ladders rather than a first-class product page.

## Additional Resilio official sources emphasized in rev0178

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Folder Preferences  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- What ports and protocols are used by Sync?  
  https://help.resilio.com/hc/en-us/articles/204754759-What-ports-and-protocols-are-used-by-Sync

- Peers aren't connecting  
  https://help.resilio.com/hc/en-us/articles/205450205-Peers-aren-t-connecting

- Download/upload speed is very slow  
  https://help.resilio.com/hc/en-us/articles/205450195-Download-upload-speed-is-very-slow

- Can others see my files? How secure is sharing by Resilio Sync?  
  https://help.resilio.com/hc/en-us/articles/205451025-Can-others-see-my-files-How-secure-is-sharing-by-Resilio-Sync

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Sync interface on Android  
  https://help.resilio.com/hc/en-us/articles/213500383-Sync-interface-on-Android

- Sync Interface on iOS devices  
  https://help.resilio.com/hc/en-us/articles/212016726-Sync-Interface-on-iOS-devices

## Revision addendum — chronology authority, offline replay, mtime fallback, and restore timing

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about chronology trust and replay behavior.
The new questions were:

> where do current official docs most clearly show that Resilio is actually quite candid about clock validity, surprising offline-winner semantics, timestamp-fidelity fallback, and restore timing?

> where do those same current docs still show that the ordinary operator answer depends on crossing warning articles, advanced preference tables, conflict FAQ prose, and Archive instructions rather than one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Time difference` warning article, which still says peer times are compared in GMT, the allowed difference is 600 seconds, invalid time-zone settings are a common cause, and mobile devices may show an empty list under the same condition.
- Resilio's current power-user preference table, which still exposes `sync_max_time_diff` and `ignore_mtime_assign_errors`, explicitly noting that the correct timestamp may remain only in the database while on-disk mtime becomes `current`.
- Resilio's current same-file-change FAQ, which still says an offline peer returning later can override later online edits and send the overwritten versions into Archive.
- Resilio's current Archive restore article, which still says restore is manual only, WebUI/Android rely on hidden `.sync/Archive`, iOS cannot access Archive, and restoring while Sync is not running can cause the restored older file to be archived again on rescan.

## Additional Resilio official sources emphasized in rev0179

- "Time difference" error
  https://help.resilio.com/hc/en-us/articles/204753599--Time-difference-error

- Power user preferences
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- What if several people make changes to the same file?
  https://help.resilio.com/hc/en-us/articles/204754209-What-if-several-people-make-changes-to-the-same-file

- Using Archive for file versioning and restoring deleted files.
  https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files

## Revision addendum — accounting truth, subject footprint, completeness confidence, and hidden residue

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about byte accounting, hidden service state, sparse placeholders, and provisional completeness.
The new questions were:

> where do current official docs most clearly show that Resilio is actually candid about ignored bytes not counting, placeholders being 0-byte stand-ins, hidden `.sync` / Archive / StreamsList / `.!sync` material being real, and rescans / hashing making some answers provisional?

> where do those same docs still show that the ordinary operator answer to `how much is really here?`, `what counts?`, `is this view complete yet?`, and `what hidden bytes remain?` still depends on hopping across IgnoreList, `.sync` internals, RSLS placeholders, folder-view columns, and change-detection / power-user articles rather than one stable page family?

The most load-bearing source set for this pass was:

- Resilio's current IgnoreList article, which still says ignored files are not indexed and not counted in the `Size` column, that rules are case-sensitive, and that post-add IgnoreList edits still leave structural knowledge in the database and passed to peers until disconnect.
- Resilio's current `.sync` article, which still says `.sync` is critical and houses Archive, IgnoreList, StreamsList, and in-flight `.!sync` files.
- Resilio's current RSLS placeholder article, which still says placeholders are 0-byte stand-ins, warns that all peers can end up with placeholders only if every full copy is removed, and distinguishes local revert-to-placeholder from global delete.
- Resilio's current change-detection and power-user articles, which still say watcher quality varies by storage, rescans default to 600 seconds, rescans can be disabled entirely, and advanced settings like `lazy_indexing`, `parallel_indexing`, `folder_rescan_interval`, `max_file_size_for_versioning`, and `free_space_warning_threashold` affect what the product knows and reports.
- Resilio's current folder-view article, which still shows `size` and related columns as optional surface-level numbers without one integrated accounting-contract page.

## Additional Resilio official sources emphasized in rev0181

- Ignoring files in Sync (Ignore List)
  https://help.resilio.com/hc/en-us/articles/205458165-Ignoring-files-in-Sync-Ignore-List

- What is '.sync' folder, and StreamsList, IgnoreList and Archive inside?
  https://help.resilio.com/hc/en-us/articles/206217185-What-is-sync-folder-and-StreamsList-IgnoreList-and-Archive-inside

- What Is an RSLS File?
  https://help.resilio.com/hc/en-us/articles/206115384-What-Is-an-RSLS-File

- How soon does synchronization start?
  https://help.resilio.com/hc/en-us/articles/204754319-How-soon-does-synchronization-start

- Power user preferences
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Folder Types and Management
  https://help.resilio.com/hc/en-us/articles/204762459-Folder-Types-and-Management

## Revision addendum — share artifacts, requester approval, mutable grants, and manual claim semantics

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about share capability artifacts, approval flow, mutable grants, and manual claim/import semantics.
The new questions were:

> where do current official docs most clearly show that Resilio still has real product substance around keys versus links, requester approval, mutable grants, and mobile/desktop carrier flexibility?

> where do those same current docs still show that the ordinary operator answer about `what exact artifact is this?`, `what approval lane comes with it?`, `who is asking?`, and `what still changes later?` still depends on hopping across several article families instead of one stable product-owned page?

The most load-bearing source set for this pass was:

- Resilio's current Share Dialog docs, which still distinguish Advanced-folder links/QR from Standard-folder keys, still bind approval/security/expiry/use-count to particular artifact families, and still make `Only new peers` versus `All peers` part of the governance story.
- Resilio's current Key structure and Link structure docs, which still make raw key type part of the capability itself while describing approval-capable link redemption as a real requester event with public key, fingerprint, certificate, and ACL consequences.
- Resilio's current User Management docs, which still say mutable rights are available only for Advanced folders and that disconnect revokes future updates while leaving already landed bytes in place.
- Resilio's current mobile sharing docs, which still say mobile issuance routes through `send the key or link`, keeping carrier flexibility real while still leaving approval and claim semantics easy to over-compress.

## Additional Resilio official sources emphasized in rev0183

- Sync Share Dialog (Desktop)  
  https://help.resilio.com/hc/en-us/articles/204790709-Sync-Share-Dialog-Desktop

- Key structure and flow  
  https://help.resilio.com/hc/en-us/articles/206767810-Key-structure-and-flow

- Link structure and flow  
  https://help.resilio.com/hc/en-us/articles/204754739-Link-structure-and-flow

- User Management  
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- Comprehensive guide to syncing (Desktop-Desktop)  
  https://help.resilio.com/hc/en-us/articles/204754939-Comprehensive-guide-to-syncing-Desktop-Desktop

- Initiate sharing on mobile platforms  
  https://help.resilio.com/hc/en-us/articles/207370636-Initiate-sharing-on-mobile-platforms

- Syncing between a desktop computer and a mobile device  
  https://help.resilio.com/hc/en-us/articles/205451165-Syncing-between-a-desktop-computer-and-a-mobile-device

## Revision addendum — subject-class cliffs, impossible upgrade, linked read-only ritual, and peer-row meaning

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about Standard-vs-Advanced class differences, impossible in-place upgrade, linked-device read-only workaround ritual, and class-dependent peer-list grouping.
The new questions were:

> where do current official docs most clearly show that Resilio still has real product substance around subject-class differences and is honest that those differences change ownership, mutation, and peer-list meaning?

> where do those same current docs still show that the ordinary operator answer about `what class is this?`, `is upgrade actually a cutover?`, `is linked read-only a true exception or a separate subject?`, and `what are these rows rows of?` still depends on hopping across several article families instead of one stable product-owned page?

The most load-bearing source set for this pass was:

- Resilio's current Standard-vs-Advanced article, which still says Standard uses randomly generated keys while Advanced uses PKI/certificates, only Advanced supports on-the-fly permission changes and Owner semantics, Standard peers can share the key they have without the same bounded owner model, Standard peer lists show devices separately where Advanced can group descendants beneath one user identity, and Standard cannot be converted in place to Advanced.
- Resilio's current Standard→Advanced upgrade how-to, which still says there is no upgrade path in place and the operator must disconnect/remove the Standard folder on all peers and add it back as Advanced.
- Resilio's current linked read-only how-to, which still says all linked devices act as Owners and that making one linked device read-only requires using a Standard folder with a Read Only key, disconnecting the existing folder if needed, entering the key manually, and choosing a location.
- Resilio's current User Management and linking docs, which still reinforce that all linked same-identity devices act as Owners and that richer grouping and mutable-grant behavior follow from the stronger class/identity model rather than from a generic folder toggle.

## Additional Resilio official sources emphasized in rev0184

- What's the difference between Standard and Advanced folders?  
  https://help.resilio.com/hc/en-us/articles/204754679-What-s-the-difference-between-Standard-and-Advanced-folders

- How do I upgrade my Standard (1.4, or classic) folders to Advanced (2.x) folders?  
  https://help.resilio.com/hc/en-us/articles/206216575-How-do-I-upgrade-my-Standard-1-4-or-classic-folders-to-Advanced-2-x-folders

- How to create a Read Only folder while syncing across linked devices?  
  https://help.resilio.com/hc/en-us/articles/206216565-How-to-create-a-Read-Only-folder-while-syncing-across-linked-devices

- User Management  
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

## Revision addendum — performance observability, bottleneck proof, and workload-shaped expectations

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about live performance graphs, peer-level route/RTT tables, disk queue/load visibility, and slow-speed troubleshooting.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid about live performance evidence rather than hiding it?

> where do those same current docs still show that the ordinary operator answer about `what is slow?`, `which path is the bottleneck?`, `is disk the limiter?`, and `what speed should I honestly expect here?` still depends on hopping across charts, troubleshooting prose, and scattered settings rather than one stable product-owned page?

The most load-bearing source set for this pass was:

- Resilio's current Performance Overview article, which still says live graphs are available, that windows can be 1 minute / 10 minutes / 1 hour, that the peer table shows upload/download rate, RTT, and protocol, and that disk load may reflect host-wide pressure rather than Sync alone.
- Resilio's current slow-speed troubleshooting article, which still says many small files, relay usage, asymmetric peers, low-capacity hardware, security software, low-priority disk settings, closed listening ports, predefined hosts, and ISP throttling all materially change the honest throughput story.
- Resilio's current sync-speed-improvement guidance, which still prefers direct connections, LAN-locality, and predefined hosts over vague `try again` optimism.

## Additional Resilio official sources emphasized in rev0185

- Performance overview  
  https://help.resilio.com/hc/en-us/articles/360001331930-Performance-overview

- Download/upload speed is very slow  
  https://help.resilio.com/hc/en-us/articles/205450195-Download-upload-speed-is-very-slow

- How can I improve data transfer/sync speed?  
  https://help.resilio.com/hc/en-us/articles/204762319-How-can-I-improve-data-transfer-sync-speed

## Revision addendum — diagnostic telemetry, profiler capture, and evidence custody

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about anonymous statistics, debug-log collection, profiler traces, storage roots, hidden mobile log artifacts, and outbound support sends.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid about what operational evidence exists and how it is captured?

> where do those same current docs still show that the ordinary operator answer about `what is already observed?`, `what extra capture did I just enable?`, `what exact bundle is leaving the node?`, and `what evidence remains locally afterwards?` still depends on hopping across a settings table, several log-collection articles, and hidden storage conventions rather than one stable product-owned page?

The most load-bearing source set for this pass was:

- Resilio's current Power user preferences article, which still says `send_statistics` collects anonymous metrics like OS and Sync version, `log_size` and `log_ttl` bound debug-log retention, and `profiler_enabled` stores `profiler.dat` in the storage folder and requires restart.
- Resilio's current automatic log-collection article, which still says debug logging can be enabled in UI or by a `debug.txt` file containing `FFFFFFFF`, requires restart for confidence, asks for at least 15 minutes of reproduction, and sends logs through a real feedback flow with an `Include logs` choice.
- Resilio's current mobile log-collection article, which still routes Android/mobile evidence collection through the special `SNC.DBG.LOGS` intake string and hidden `.synclogs` storage.
- Resilio's current storage-folder and crash-report articles, which still list concrete hidden storage roots and dump locations by platform and service account.

## Additional Resilio official sources emphasized in rev0186

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Collecting debug logs automatically  
  https://help.resilio.com/hc/en-us/articles/360019430539-Collecting-debug-logs-automatically

- Collect debug logs on mobiles  
  https://help.resilio.com/hc/en-us/articles/38269346960531-Collect-debug-logs-on-mobiles

- Increasing Debug Log size  
  https://help.resilio.com/hc/en-us/articles/205450145-Increasing-Debug-Log-size

- Sync Storage folder  
  https://help.resilio.com/hc/en-us/articles/206664690-Sync-Storage-folder

- Collecting crash reports, mini-dumps and core dumps  
  https://help.resilio.com/hc/en-us/articles/206214615-Collecting-crash-reports-mini-dumps-and-core-dumps

## Revision addendum — control surface bootstrap, exposure, and recovery

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about browser-first WebUI control, loopback-vs-LAN exposure, browser-warning recovery, password-reset side effects, installer trust gates, and browser-open link fallback.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid about how browser/local-web control works?

> where do those same current docs still show that the ordinary operator answer about `what surface is this?`, `who can reach it?`, `why does the browser distrust it?`, and `how do I recover access without collateral damage?` still depends on hopping across setup docs, troubleshooting notes, browser-warning pages, and reset rituals instead of one stable product-owned page?

The most load-bearing source set for this pass was:

- Resilio's current v3 changelog and Get Started tree, which still show an active v3 line through `3.1.2.1076`.
- Resilio's current WebUI and Linux/service docs, which still say browser/local-web control is the default path on Linux and Windows service installs, that loopback is the default listener posture, and that widening to LAN is a deliberate move.
- Resilio's current browser-warning and SmartScreen docs, which still show that local control trust and install trust can fail in ordinary browser/OS ways that the product should explain explicitly.
- Resilio's current WebUI password-reset and browser-link troubleshooting docs, which still distinguish side-effectful reset paths from safer ones and still admit that direct browser-open intake does not work from WebUI.

## Additional Resilio official sources emphasized in rev0187

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Get started with Sync  
  https://help.resilio.com/hc/en-us/categories/200140177-Get-started-with-Sync

- Configuring WebUI  
  https://help.resilio.com/hc/en-us/articles/115001184490-Configuring-WebUI

- Guide to Linux, and Sync peculiarities  
  https://help.resilio.com/hc/en-us/articles/204762449-Guide-to-Linux-and-Sync-peculiarities

- Running Sync as a service on Windows  
  https://help.resilio.com/hc/en-us/articles/207701296-Running-Sync-as-a-service-on-Windows

- Sync Service Troubleshooting on Windows  
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

- Browser warning "Your connection is not private"  
  https://help.resilio.com/hc/en-us/articles/4404757430291-Browser-warning-Your-connection-is-not-private

- How do I reset my WebUI password?  
  https://help.resilio.com/hc/en-us/articles/205450295-How-do-I-reset-my-WebUI-password

- Sync doesn't start when opening Link in browser  
  https://help.resilio.com/hc/en-us/articles/204753649-Sync-doesn-t-start-when-opening-Link-in-browser

- Windows Defender SmartScreen blocks Resilio Sync installer  
  https://help.resilio.com/hc/en-us/articles/360014486120-Windows-Defender-SmartScreen-blocks-Resilio-Sync-installer

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Sync Storage folder  
  https://help.resilio.com/hc/en-us/articles/206664690-Sync-Storage-folder

## Revision addendum — grant lifecycle, revoke residue, and successor-grant epochs

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about share-dialog security controls, mutable rights, Standard-vs-Advanced class fences, key/link flow, local-share caveats, and disconnect / reconnect behavior.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid about mutable rights, link safety controls, and revocation residue?

> where do those same current docs still show that the ordinary operator answer about `can I edit this in place?`, `which artifacts are still live?`, `what descendants inherit this change?`, and `when is this really a successor epoch?` still depends on hopping across several article families rather than one stable product-owned page?

The most load-bearing source set for this pass was:

- Resilio's current v3 changelog, which still shows an active Sync v3 line through `3.1.2.1076`.
- Resilio's current Share Dialog article, which still says Advanced folders use link/QR, Standard folders also expose raw keys, approval can be `Only new peers` or `All peers`, and links can carry expiry and use limits.
- Resilio's current User Management and Sync functionality articles, which still say Advanced-folder rights can be changed on the fly, Owner controls onward sharing, and `Disconnect` revokes future updates while already synchronized files remain.
- Resilio's current Standard-vs-Advanced article, which still says Standard folders cannot do on-the-fly permission changes and instead require remove-and-readd with a new key.
- Resilio's current local-share article, which still says Advanced local-share permissions cannot be changed through user management, must be removed and re-shared to change, and source-right downgrades cascade while source disconnect/removal does not automatically restore the derivative.
- Resilio's current key-flow and link-flow articles, which still show that key change does not propagate automatically, old-key peers continue syncing together, and link claim is a real identity / certificate flow rather than a cosmetic URL open.

## Additional Resilio official sources emphasized in rev0190

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Sync Share Dialog (Desktop)  
  https://help.resilio.com/hc/en-us/articles/204790709-Sync-Share-Dialog-Desktop

- User Management  
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- Sync functionality in detail  
  https://help.resilio.com/hc/en-us/articles/204754389-Sync-functionality-in-detail

- What's the difference between Standard and Advanced folders?  
  https://help.resilio.com/hc/en-us/articles/204754679-What-s-the-difference-between-Standard-and-Advanced-folders

- Sharing a folder locally  
  https://help.resilio.com/hc/en-us/articles/360011582500-Sharing-a-folder-locally

- Disconnecting and Removing Folders  
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- Key structure and flow  
  https://help.resilio.com/hc/en-us/articles/206767810-Key-structure-and-flow

- Link structure and flow  
  https://help.resilio.com/hc/en-us/articles/204754739-Link-structure-and-flow

## Revision addendum — namespace blockage, conflict meaning, unsupported entries, and portability repair

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about conflict-file causes, unsupported links, invalid-name edge cases, path-length / encoding troubleshooting, move/rename limits, and power-user path-conflict toggles.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid about namespace portability, unsupported entry classes, and conflict danger?

> where do those same current docs still show that the ordinary operator answer about `why is this path family blocked?`, `what exactly does this conflict artifact correspond to?`, and `what safe repair scope applies?` still depends on hopping across conflict docs, unsupported-entry docs, invalid-name warnings, troubleshooting lists, and power-user settings instead of one stable product-owned page?

The most load-bearing source set for this pass was:

- Resilio's current v3 changelog, which still shows an active Sync v3 line through `3.1.2.1076` and even recent clickable-error / context-menu fixes.
- Resilio's current conflict-file doc, which still lists case-insensitive collisions, unicode-form differences, prohibited symbols, linked junctions, and device/controller issues, and still warns not to casually delete `.Conflict` artifacts.
- Resilio's current soft/hard/symbolic-link doc, which still says Windows link classes are unsupported and may create `.Conflict` fallout, while Unix symlink targets are not synchronized unless separately added.
- Resilio's current troubleshooting docs, which still point to UTF-8 expectations, path-length ceilings, filesystem errors, stalled merge limits, and clickable status-row guidance.
- Resilio's current unsupported-asterisk warning, which still says some names may be interpreted as system data and disrupt syncing.
- Resilio's current power-user preferences doc, which still exposes `fix_conflicting_paths` and `normalize_unicode_paths`, confirming that path handling remains a real semantic layer.

## Additional Resilio official sources emphasized in rev0194

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Conflict files in Sync  
  https://help.resilio.com/hc/en-us/articles/204753629-Conflict-files-in-Sync

- Soft links, hard links and symbolic links  
  https://help.resilio.com/hc/en-us/articles/205504529-Soft-links-hard-links-and-symbolic-links

- Unsupported asterisk (*) characters at the end of file/folder names  
  https://help.resilio.com/hc/en-us/articles/206214715-Unsupported-asterisk-characters-at-the-end-of-file-folder-names

- My files don't sync  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Can I move or rename a syncing folder?  
  https://help.resilio.com/hc/en-us/articles/205450655-Can-I-move-or-rename-a-syncing-folder

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences
## Revision addendum — freshness claims, detection downgrade, and rescan ritual after rev0194

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about change-detection basis, scheduled and manual rescans, watcher exhaustion, Windows-service notification downgrade, internal task phases, and generic no-sync diagnosis.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid about notifications, rescans, and the fact that slow internal work can still be healthy rather than stuck?

> where do those same current docs still show that the ordinary operator answer about `is this actually fresh yet?`, `what degraded detection?`, `what exactly will rescan improve?`, and `where is this changed file in the publication chain?` still depends on hopping across FAQs, warning pages, service caveats, power-user settings, and generic troubleshooting notes instead of one stable product-owned page?

The most load-bearing source set for this pass was:

- Resilio's current v3 changelog, which still shows an active Sync v3 line through `3.1.2.1076`.
- Resilio's current synchronization-start FAQ, which still says detection precedes indexing/delivery, that notifications are fastest when they work, that periodic scan runs every 600 seconds and on Sync start, that rescan can be set to zero, and that manual rescan is ordinary UI.
- Resilio's current power-user preference table, which still exposes `folder_rescan_interval`, `parallel_indexing`, `enable_file_system_notifications`, and `recheck_locked_files_interval` as direct freshness-shaping controls.
- Resilio's current watcher-exhaustion warning, which still says Linux watcher exhaustion forces discovery into manual or periodic rescan until limits are raised and Sync restarted.
- Resilio's current Windows service troubleshooting doc, which still says UNC-style workaround for service-invisible mapped drives loses system file-update notifications and falls back to rescan or restart.
- Resilio's current internal-tasks warning and generic `My files don't sync` guide, which still split the changed-file story across scan/merge/transfer/write phases, status/history/queue checks, and restart/`touch` ritual when notifications are weak.

## Additional Resilio official sources emphasized in rev0195

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- How soon does synchronization start?  
  https://help.resilio.com/hc/en-us/articles/204754319-How-soon-does-synchronization-start

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Agent run out of system notify watchers. Updated files will be uploaded only after periodic folder rescan  
  https://help.resilio.com/hc/en-us/articles/360015593120-Agent-run-out-of-system-notify-watchers-Updated-files-will-be-uploaded-only-after-periodic-folder-rescan

- Sync Service Troubleshooting on Windows  
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

- Some internal tasks are taking time to complete  
  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete

- My files don't sync  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync
## Revision addendum — discovery basis, relay fallback, and observer-delta truth after rev0195

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about discovery lanes, tracker/relay prerequisites, peer-route fallback, observer disclosure, protocol overlap, and route residue after tightening.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid about tracker, LAN discovery, predefined hosts, relay fallback, and the fact that route tightening may still leave remembered public endpoint residue?

> where do those same current docs still show that the ordinary operator answer about `how are these peers finding each other?`, `who currently learns what?`, `why is this pair relayed?`, and `what is the least-widening repair?` still depends on hopping across key flow, ports/protocols, settings, privacy prose, LAN-only ritual, and troubleshooting notes instead of one stable product-owned page?

The most load-bearing source set for this pass was:

- Resilio's current v3 changelog, which still shows an active Sync v3 line through `3.1.2.1076`.
- Resilio's current key-flow article, which still says tracker learns ShareID plus local/public endpoint facts, LAN discovery multicasts ShareID plus `IP:port`, and predefined hosts receive share identity and peer IP when contacted.
- Resilio's current ports/protocols article, which still says Sync first fetches `sync.conf` to learn tracker and relay addresses and then requires listening-port reachability for direct connection.
- Resilio's current relay article and folder preferences article, which still say direct is preferred, relay is fallback, relay can slow sync, tracker helps automatic discovery, and predefined hosts remain a real path in high-security networks.
- Resilio's current privacy/security article, which still names tracker and relay as concrete points of contact with Resilio infrastructure and says tracker learns share ID plus endpoint data.
- Resilio's current `Peers aren't connecting`, slow-speed, and LAN-only articles, which still split route diagnosis across blocked tracker, blocked listener, blocked relay, multicast limits, proxy involvement, port mapping, known-host fallback, and remembered public-endpoint residue.
- Resilio's current power-user preference table, which still exposes `folder_defaults.use_tracker`, `folder_defaults.use_relay`, `folder_defaults.known_hosts`, `tracker_protocols`, `tunnel_protocols`, and LAN discovery mode as live route-shaping controls.

## Additional Resilio official sources emphasized in rev0196

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Key structure and flow  
  https://help.resilio.com/hc/en-us/articles/206767810-Key-structure-and-flow

- What ports and protocols are used by Sync?  
  https://help.resilio.com/hc/en-us/articles/204754759-What-ports-and-protocols-are-used-by-Sync

- What is a Relay Server?  
  https://help.resilio.com/hc/en-us/articles/204754779-What-is-a-Relay-Server

- Folder Preferences  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- Peers aren't connecting  
  https://help.resilio.com/hc/en-us/articles/205450205-Peers-aren-t-connecting

- Can others see my files? How secure is sharing by Resilio Sync?  
  https://help.resilio.com/hc/en-us/articles/205451025-Can-others-see-my-files-How-secure-is-sharing-by-Resilio-Sync

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Can I force Sync to do local network (LAN) syncing only and not sync via the Internet?  
  https://help.resilio.com/hc/en-us/articles/204754349-Can-I-force-Sync-to-do-local-network-LAN-syncing-only-and-not-sync-via-the-Internet

- Download/upload speed is very slow  
  https://help.resilio.com/hc/en-us/articles/205450195-Download-upload-speed-is-very-slow

## Revision addendum — quiet posture, hidden work, and catch-up truth after rev0196

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about scheduled quiet windows, background/runtime limits, battery/network gates, hidden internal work, source-unavailable warnings, and slow-transfer causes.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid about partial pauses, runtime absence, hidden work, source absence, and practical bottleneck families?

> where do those same current docs still show that the ordinary operator answer about `why is nothing moving?`, `what still propagates while quiet?`, `what is actually slow?`, and `what will resume really change?` still depends on hopping across schedule docs, background/runtime notes, mobile settings, troubleshooting articles, and warnings instead of one stable product-owned page?

The most load-bearing source set for this pass was:

- Resilio's current v3 changelog, which still shows an active Sync v3 line through `3.1.2.1076`.
- Resilio's current `Running Sync on schedule` article, which still says `Paused` zeroes upload/download speed while zero-sized files, deletions, indexing, and some peer-serving behavior survive.
- Resilio's current `Does Sync work in background?` article, which still distinguishes desktop background continuity, headless Linux, Android runtime-killer risk, and unavailable background sync on iOS.
- Resilio's current `Configuring Auto Sleep & Battery Saver (Android)` and `Settings on mobile platforms` articles, which still show intentional offline intervals, wake cadence, charge-threshold stops, and network-based share stoppage.
- Resilio's current `Some internal tasks are taking time to complete` article, which still names hashing, block checking, local-block copy, compare, read, and write as real hidden work that may later recover.
- Resilio's current `Download/upload speed is very slow` article, which still names relay, many-small-files workload, remote-upload asymmetry, low-capacity networking gear, security software, and disk-priority settings as real bottleneck families.
- Resilio's current `Cannot download files ... no source peers online for too long time` and `Will my devices still sync when switched off?` articles, which still make source-presence truth explicit rather than pretending Sync is cloud-backed.

## Additional Resilio official sources emphasized in rev0197

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Running Sync on schedule  
  https://help.resilio.com/hc/en-us/articles/210783266-Running-Sync-on-schedule

- Does Sync work in background?  
  https://help.resilio.com/hc/en-us/articles/206816823-Does-Sync-work-in-background

- Configuring Auto Sleep & Battery Saver (Android)  
  https://help.resilio.com/hc/en-us/articles/204762699-Configuring-Auto-Sleep-Battery-Saver-Android

- Settings on mobile platforms  
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- Setting network interface per share  
  https://help.resilio.com/hc/en-us/articles/360001411244-Setting-network-interface-per-share

- Some internal tasks are taking time to complete  
  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete

- Download/upload speed is very slow  
  https://help.resilio.com/hc/en-us/articles/205450195-Download-upload-speed-is-very-slow

- Cannot download files / These files cannot be downloaded as there are no source peers online for too long time  
  https://help.resilio.com/hc/en-us/articles/360010899719-Cannot-download-files-These-files-cannot-be-downloaded-as-there-are-no-source-peers-online-for-too-long-time

- Will my devices still sync when switched off?  
  https://help.resilio.com/hc/en-us/articles/204754199-Will-my-devices-still-sync-when-switched-off

## Revision addendum — hidden subject spine, sidecar policy, and continuity-bearing service state

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about the `.sync` folder, IgnoreList, StreamsList, service-file loss, move/rename limits, troubleshooting for stuck partials and ignore disagreement, and the unsupported cloning warning.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that a sync subject has hidden product-owned state, local text sidecars, xattr-carriage sidecars, and continuity-bearing identifiers?

> where do those same current docs still show that the ordinary operator answer about `what is product-owned here?`, `which sidecar controls this behavior?`, `did continuity survive?`, and `what hidden bytes are safe to touch?` still depends on hopping across several FAQs, sidecar docs, warning pages, troubleshooting notes, and caveat articles instead of one stable product-owned page?

The most load-bearing source set for this pass was:

- Resilio's current v3 changelog, which still shows the product line is active enough that these seams are current design evidence rather than abandoned-history trivia.
- Resilio's current `.sync` FAQ, which still says every subject gets a hidden service folder containing ID, IgnoreList, StreamsList, Archive, and in-flight `.!sync` names.
- Resilio's current `Service files missing` warning, which still says `.sync` loss suspends sync and that duplicate runtimes touching the same subject can corrupt the internal files.
- Resilio's current IgnoreList doc and `My files don't sync` troubleshooting doc, which still show that ignore policy is a hidden text sidecar, that excluded files are not indexed or counted, and that peer disagreement over ignore behavior can itself explain divergence.
- Resilio's current xattr / StreamsList doc, which still says metadata carriage uses a separate whitelist sidecar and can fall back to stub files in `.sync/Streams`.
- Resilio's current move/rename FAQ and `Cloning Sync` warning, which still show that continuity-preserving moves are limited and naive instance cloning is unsupported.

## Additional Resilio official sources emphasized in rev0198

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- What is '.sync' folder, and StreamsList, IgnoreList and Archive inside?  
  https://help.resilio.com/hc/en-us/articles/206217185-What-is-sync-folder-and-StreamsList-IgnoreList-and-Archive-inside

- Ignoring files in Sync (Ignore List)  
  https://help.resilio.com/hc/en-us/articles/205458165-Ignoring-files-in-Sync-Ignore-List

- Alt Streams and Xattrs in Sync  
  https://help.resilio.com/hc/en-us/articles/204754729-Alt-Streams-and-Xattrs-in-Sync

- Service files missing / Cannot identify destination folder  
  https://help.resilio.com/hc/en-us/articles/205450225-Service-files-missing-Cannot-identify-destination-folder

- My files don't sync  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Can I move or rename a syncing folder?  
  https://help.resilio.com/hc/en-us/articles/205450655-Can-I-move-or-rename-a-syncing-folder

- Cloning Sync  
  https://help.resilio.com/hc/en-us/articles/360018421940-Cloning-Sync

## Revision addendum — install eligibility, linked cohorts, and cutover honesty after rev0198

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about system requirements, v3 update limits, Business-vs-v3 boundaries, mixed-version linked devices, Linux package lanes, and NAS install warnings.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid about host-role support, usage-class boundaries, mixed-cohort risk, and unsupported update fallout?

> where do those same current docs still show that the ordinary operator answer about `may this seat run this line?`, `may this cohort mix versions?`, `what survives this cutover?`, and `who owns updates for this lane?` still depends on hopping across system requirements, update instructions, FAQ prose, install guides, and identity-linking warnings instead of one stable product-owned page?

The most load-bearing source set for this pass was:

- Resilio's current v3 changelog, which still shows an active Sync v3 line through `3.1.2.1076`.
- Resilio's current supported-platforms article, which still says v3 is not supported on Windows Server and narrows v3 architecture availability relative to v2.
- Resilio's current `Updating installation to Resilio Sync v3` article, which still says Business cannot be updated and that some unsupported crossings may leave files intact while losing share configuration.
- Resilio's current Sync v3 FAQ, which still says Business installations, including those on personal Windows Server, cannot be updated to v3 while support continues on Business licenses.
- Resilio's current Linux package guide and NAS install pages, which still repeat edition/usage compatibility warnings and show install-lane-specific package families.
- Resilio's current `Sync Private Identity & Linking My Devices` article, which still warns that mixing v2 and v3 inside one linked constellation can conflict on licensing and cost UI/share-configuration access.

## Additional Resilio official sources emphasized in rev0199

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Resilio Sync: supported platforms and system requirements  
  https://help.resilio.com/hc/en-us/articles/205450965-Resilio-Sync-supported-platforms-and-system-requirements

- Updating installation to Resilio Sync v3  
  https://help.resilio.com/hc/en-us/articles/31194252837779-Updating-installation-to-Resilio-Sync-v3

- FAQ Resilio Sync 3.0.0  
  https://help.resilio.com/hc/en-us/articles/32109883606035-FAQ-Resilio-Sync-3-0-0

- Installing Sync package on Linux  
  https://help.resilio.com/hc/en-us/articles/206178924-Installing-Sync-package-on-Linux

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Synology  
  https://help.resilio.com/hc/en-us/articles/206664850-Synology

- QNAP  
  https://help.resilio.com/hc/en-us/articles/206178964-QNAP

## Additional Resilio official sources emphasized in rev0200

The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid about hidden advanced settings, config-mode precedence, restart boundaries, and resource-bias side effects?

> where do those same current docs still show that the ordinary operator answer about `what hidden policy is active`, `what visible controls it shadows`, `what requires restart or peer-memory clearance`, and `what cost this runtime bias buys` still depends on hopping across advanced tables, config snippets, folder preferences, and special-case help articles instead of one stable product-owned page?

The most load-bearing source set for this pass was:

- Resilio's current v3 changelog, which still shows an active Sync v3 line through `3.1.2.1076`.
- Resilio's current **Power user preferences** article, which still says it covers today's latest Sync version and still exposes destructive guardrails, peer-retention settings, route/discovery defaults, restart-bearing toggles, and runtime-bias controls in one low-level table.
- Resilio's current **Running Sync in configuration mode** article, which still says advanced preferences can be added to `sync.conf` and that declaring shared folders in config disables WebUI and overrides folders previously added from WebUI.
- Resilio's current **Can I force Sync to do local network (LAN) syncing only and not sync via the Internet?** article, which still requires a mix of share-preference edits, power-user settings, and temporary peer-expiration zeroing plus restart to clear cached public endpoints.
- Resilio's current **Folder Preferences** article, which still splits route/discovery controls across ordinary folder settings while leaving other load-bearing behavior in advanced tables.

## Additional Resilio official sources emphasized in rev0201

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Can I force Sync to do local network (LAN) syncing only and not sync via the Internet?  
  https://help.resilio.com/hc/en-us/articles/204754349-Can-I-force-Sync-to-do-local-network-LAN-syncing-only-and-not-sync-via-the-Internet

- Folder Preferences  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

## Revision addendum — external recipes, copied commands, and postcondition proof

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about external repair rituals, copied commands, browser-trust workarounds, config-mode precedence, password-reset side effects, and hidden service-state loss.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid about outside-the-product steps and exact commands?

> where do those same current docs still show that the ordinary operator answer about `what this step is`, `what it touches`, `what had to stop first`, and `what proves success afterward` still depends on hopping across several docs instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current v3 changelog, which still shows an active Sync v3 line through `3.1.2.1076`.
- Resilio's current **Measuring network performance with iperf3** article, which still requires Sync to be shut down completely on both peers and still publishes explicit client/server commands.
- Resilio's current **Collecting debug logs manually** article, which still allows debug activation via settings or `debug.txt`, still requires restart to ensure logging is enabled, and still asks for at least 15 minutes of collection.
- Resilio's current **Browser warning "Your connection is not private"** article, which still permits temporary browser bypass, HSTS cleanup, or supplying a trusted cert through config mode.
- Resilio's current **Running Sync in configuration mode** article, which still says config-defined shared folders disable WebUI and override folders previously added there, and still exposes WebUI credentials / HTTPS / certificate fields in config.
- Resilio's current **Configuring WebUI** article, which still treats WebUI as the default path on Linux and Windows service installs and still says clicking share links in the browser does not work for WebUI.
- Resilio's current **How do I reset my WebUI password?** article, which still presents a `settings.dat` deletion lane and a config-mode lane that avoids duplicate-device rows and preference reset.
- Resilio's current **Service files missing / Cannot identify destination folder** article, which still treats `.sync` loss/corruption as continuity-bearing state loss and suggests remove/re-add style repair.

## Additional Resilio official sources emphasized in rev0203

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Measuring network performance with iperf3  
  https://help.resilio.com/hc/en-us/articles/1500007478562-Measuring-network-performance-with-iperf3

- Collecting debug logs manually  
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

- Browser warning "Your connection is not private"  
  https://help.resilio.com/hc/en-us/articles/4404757430291-Browser-warning-Your-connection-is-not-private

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Configuring WebUI  
  https://help.resilio.com/hc/en-us/articles/115001184490-Configuring-WebUI

- How do I reset my WebUI password?  
  https://help.resilio.com/hc/en-us/articles/205450295-How-do-I-reset-my-WebUI-password

- Service files missing / Cannot identify destination folder  
  https://help.resilio.com/hc/en-us/articles/205450225-Service-files-missing-Cannot-identify-destination-folder

## Revision addendum — warning taxonomy, scope blast radius, and recovery-rung truth

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about core warnings, hidden-work backlog, watcher exhaustion, ghost-file warnings, continuity-bearing hidden-state loss, chronology failure, and merge/path prompts.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that warnings correspond to materially different degraded states?

> where do those same current docs still show that the ordinary operator answer about `what kind of warning is this`, `how wide is it`, `what exact next rung is safest`, and `what did acknowledgement really change` still depends on hopping across warning strings, one-off warning articles, troubleshooting prose, and a few hidden toggles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current v3 changelog, which still shows an active Sync v3 line through `3.1.2.1076`.
- Resilio's current **Errors and warnings** section, which still keeps a distinct family of warning articles rather than pretending all errors are one generic problem.
- Resilio's current **Core warnings** article, which still separates tracker loss, low-space-on-default-folder disk, folder-list/identity failure, and license-management disablement.
- Resilio's current **Some internal tasks are taking time to complete** article, which still says the condition can mean scanning, hashing, block checking, deduplication, merge, transfer, or writing and may recover on its own.
- Resilio's current **Agent run out of system notify watchers** article, which still says notification coverage can degrade into rescan-only discovery until the watcher limit is raised and Sync restarted.
- Resilio's current **Cannot download files / These files cannot be downloaded as there are no source peers online for too long time** article, which still explains ghost-file state, per-warning filename detail, `Ignore All`, and a disable-warning path through power-user settings.
- Resilio's current **Database error** article, which still suspends only the affected subject and still recommends a restart → disconnect/reconnect same destination → re-add ladder.
- Resilio's current **Service files missing / Cannot identify destination folder** article, which still treats `.sync` loss/corruption as continuity-bearing state loss and still says the proposed fix creates a new synchronization instance.
- Resilio's current **Folder not found / Can't open the destination folder** article, which still distinguishes restore / point-to-new-location / re-add-and-reconnect fallout.
- Resilio's current **Folder not empty** article, which still says the same prompt can mean either risky overwrite/delete of pre-existing bytes or harmless reconnect to a location that already synced before.
- Resilio's current **Time difference** article, which still explains the per-peer clock/timezone problem and the 600-second threshold.

## Additional Resilio official sources emphasized in rev0204

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Errors and warnings  
  https://help.resilio.com/hc/en-us/sections/201112455-Errors-and-warnings

- Core warnings  
  https://help.resilio.com/hc/en-us/articles/360001217950-Core-warnings

- Some internal tasks are taking time to complete  
  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete

- Agent run out of system notify watchers. Updated files will be uploaded only after periodic folder rescan  
  https://help.resilio.com/hc/en-us/articles/360015593120-Agent-run-out-of-system-notify-watchers-Updated-files-will-be-uploaded-only-after-periodic-folder-rescan

- Cannot download files / These files cannot be downloaded as there are no source peers online for too long time.  
  https://help.resilio.com/hc/en-us/articles/360010899719-Cannot-download-files-These-files-cannot-be-downloaded-as-there-are-no-source-peers-online-for-too-long-time

- Database error  
  https://help.resilio.com/hc/en-us/articles/204753659-Database-error

- Service files missing / Cannot identify destination folder  
  https://help.resilio.com/hc/en-us/articles/205450225-Service-files-missing-Cannot-identify-destination-folder

- Folder not found / Can't open the destination folder  
  https://help.resilio.com/hc/en-us/articles/205450255-Folder-not-found-Can-t-open-the-destination-folder

- Folder not empty  
  https://help.resilio.com/hc/en-us/articles/204753689-Folder-not-empty

- "Time difference" error  
  https://help.resilio.com/hc/en-us/articles/204753599--Time-difference-error

## Revision addendum — mobile capture-source, path-class, sink, and reacquire truth

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about mobile backup sources, Simple Mode, SD-card authority, iOS sandbox storage, one-off downloads, copied-out iOS editing, and mobile runtime gating.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that mobile source kind, storage class, sink authority, and reacquireability really are different from desktop truth?

> where do those same current docs still show that the ordinary operator answer about `what source class is this`, `what path class is actually writable`, `what sink contract did I just create`, and `can I clear this now and honestly get it back later` still depends on hopping across several platform articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current v3 changelog, which still shows an active Sync v3 line through `3.1.2.1076` and still preserves release notes relevant to current mobile surface behavior.
- Resilio's current **How to use Camera Backup (all mobiles)?** article, which still says source-side deletion preserves the sink copy, linked-device selection is part of backup routing, disconnect preserves already-landed pictures, and default sink naming differs by platform.
- Resilio's current **How to Back up data (Android only)** article, which still says Android backup can source virtually any data, desktop has read-only access to the share, linked-device backup is first-class, and ExtSD can be a backup source while not being writable as a synced destination under Android restrictions.
- Resilio's current **Simple Mode (Android)** article, which still says new shares default into `Downloads/Sync` on internal storage, hides root and `ExternalSD`, and must be disabled for explicit location choice.
- Resilio's current **SD card gimmicks on Android** article, which still says SD-card use needs a root-level document-provider grant and distinguishes granting card authority from later choosing the share location.
- Resilio's current **Storage Management on iOS** article, which still says iOS keeps files in Sync's sandbox, separates App Data from User data, and distinguishes Downloads, Shared files, and synced-share bytes.
- Resilio's current **Sharing files (Android)** and **Sharing files (iOS)** articles, which still separate `Downloads` from `Shared links`, keep file-history residue after local removal, and publish fixed/default download-store behavior.
- Resilio's current **How to edit a document stored in Sync? (iOS)** and **Sync for iOS Peculiarities** articles, which still explain copied-out editing, manual save-back, duplicate-risk, no global delete on iOS local delete, and lack of background transfer.
- Resilio's current **Configuring Auto Sleep & Battery Saver (Android)** article, which still says the core can go offline and wake periodically, materially affecting later reacquire timing.

## Additional Resilio official sources emphasized in rev0205

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- How to use Camera Backup (all mobiles)?  
  https://help.resilio.com/hc/en-us/articles/205506809-How-to-use-Camera-Backup-all-mobiles

- How to Back up data (Android only)  
  https://help.resilio.com/hc/en-us/articles/204762339-How-to-Back-up-data-Android-only

- Simple Mode (Android)  
  https://help.resilio.com/hc/en-us/articles/205458155-Simple-Mode-Android

- SD card gimmicks on Android  
  https://help.resilio.com/hc/en-us/articles/209643433-SD-card-gimmicks-on-Android

- Storage Management on iOS  
  https://help.resilio.com/hc/en-us/articles/115001726304-Storage-Management-on-iOS

- Sharing files (Android)  
  https://help.resilio.com/hc/en-us/articles/115000409690-Sharing-files-Android

- Sharing files (iOS)  
  https://help.resilio.com/hc/en-us/articles/115001717390-Sharing-files-iOS

- Selective Sync (Mobile)  
  https://help.resilio.com/hc/en-us/articles/206217315-Selective-Sync-Mobile

- How to edit a document stored in Sync? (iOS)  
  https://help.resilio.com/hc/en-us/articles/204762379-How-to-edit-a-document-stored-in-Sync-iOS

- Sync for iOS Peculiarities  
  https://help.resilio.com/hc/en-us/articles/205506539-Sync-for-iOS-Peculiarities

- Sync interface on Android  
  https://help.resilio.com/hc/en-us/articles/213500383-Sync-interface-on-Android

- Syncing between a desktop computer and a mobile device  
  https://help.resilio.com/hc/en-us/articles/205451165-Syncing-between-a-desktop-computer-and-a-mobile-device

- Setting network interface per share  
  https://help.resilio.com/hc/en-us/articles/360001411244-Setting-network-interface-per-share

- Configuring Auto Sleep & Battery Saver (Android)  
  https://help.resilio.com/hc/en-us/articles/204762699-Configuring-Auto-Sleep-Battery-Saver-Android

## Latest addendum question after rev0205

> where do current official Resilio docs still show that the ordinary operator answer about `what can this suspect seat still do`, `what is the narrowest believable cutoff`, `when is whole-identity rotation required`, and `what residual authority still remains afterward` still depends on hopping across several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current v3 changelog, which still shows an active Sync v3 line through `3.1.2.1076`.
- Resilio's current **If your device is stolen** article, which still says disk encryption changes immediate risk, unencrypted stolen linked seats may view/modify/remove data on other linked devices, and the documented response may broaden into backup, unlink, storage-folder cleanup, reinstall, identity regeneration, relink, and reshare.
- Resilio's current **Sync Private Identity & Linking My Devices** article, which still says linked devices share one identity, that all folders are visible across linked devices, that remote unlink of other devices is unavailable, and that linking already-running installs can cause one device to lose its old certificate and Advanced folders.
- Resilio's current **User Management** article, which still says linked devices under one identity act as Owners, and that `Disconnect` revokes future updates while leaving already-synchronized files in place.
- Resilio's current **Encrypted folders** article, which still preserves the product's separate untrusted-storage pattern and therefore sharpens the contrast with a stolen linked owner seat.

## Additional Resilio official sources emphasized in rev0206

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- If your device is stolen  
  https://help.resilio.com/hc/en-us/articles/204644049-If-your-device-is-stolen

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- User Management  
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- Encrypted folders  
  https://help.resilio.com/hc/en-us/articles/207370466-Encrypted-folders

## Latest addendum question after rev0206

> where do current official Resilio docs still show that the ordinary operator answer about `is this live or bounded`, `who may redeem it`, `where will it land`, and `what survives after I clear it or let it expire` still depends on hopping across several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current v3 changelog, which still shows an active Sync v3 line through `3.1.2.1076`.
- Resilio's current **Sharing single file** article, which still says file send is a one-time one-way transfer, that desktop expiry defaults to 3 days but may be made never-expiring, that `share_file_ttl` shapes defaults, that anyone with the link can download, that use count and device bans do not exist, that changed content requires reissue, that recipients may re-share without changing expiry, and that same-name collisions land as `(1)` variants.
- Resilio's current **Sharing files (Android)** article, which still says mobile single-file expiry is fixed at 3 days there, that receives land in `Downloads/SyncDownloads` on internal memory, that this currently cannot be changed, that `Downloads` cleanup removes device bytes, and that `Shared links` removal is UI-only.
- Resilio's current **Sharing files (iOS)** article, which still says mobile single-file expiry is fixed at 3 days there, that receives arrive by QR lane, that local deletion from `Downloads` removes device bytes while transfer history still remains visible, and that `Shared links` removal is UI-only.
- Resilio's current **Power user preferences** article, which still preserves `share_file_ttl`, `transfer_job_verify_downloaded_files`, `keep_expired_transfer_days`, and `keep_expired_transfer_num` as separate hidden knobs for file-send defaults and row retention.

## Additional Resilio official sources emphasized in rev0207

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Sharing single file  
  https://help.resilio.com/hc/en-us/articles/115000401010-Sharing-single-file

- Sharing files (Android)  
  https://help.resilio.com/hc/en-us/articles/115000409690-Sharing-files-Android

- Sharing files (iOS)  
  https://help.resilio.com/hc/en-us/articles/115001717390-Sharing-files-iOS

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

## Latest addendum question after rev0207

> where do current official Resilio docs still show that the ordinary operator answer about `who can actually receive diagnostics here`, `what capture is active`, `how does the packet leave`, and `what crash or log residue remains afterward` still depends on hopping across several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current v3 changelog, which still shows an active Sync v3 line through `3.1.2.1076`.
- Resilio's current **Power user preferences** article, which still says the current table covers today's latest Sync version and still exposes `send_statistics`, `log_size`, `log_ttl`, and `profiler_enabled`, including profiler storage in `profiler.dat`, 10-minute rotation, and restart requirement.
- Resilio's current **Collecting debug logs manually** article, which still says debug logging can be enabled through UI or `debug.txt`, still requires restart to ensure activation, still asks for at least 15 minutes of collection, and still documents log paths, service-account storage differences, and the 20 MB attachment ceiling.
- Resilio's current **Collecting debug logs automatically** article, which still distinguishes Business support from Sync v3 self-serve, still uses the in-product `Contact support` lane, and still says the app must remain open until sending completes.
- Resilio's current **Collect debug logs on mobiles** article, which still uses the `SNC.DBG.LOGS` ritual and hidden `.synclogs` path.
- Resilio's current **Collecting crash reports, mini-dumps and core dumps** article, which still separates crash reports, mini dumps, and core dumps by OS and service-user path.
- Resilio's current **Collecting core dump on NAS devices** article, which still requires SSH, graceful stop, `ulimit -c unlimited`, terminal restart, and manual move/download of the dump.

## Additional Resilio official sources emphasized in rev0208

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Collecting debug logs manually  
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

- Collecting debug logs automatically  
  https://help.resilio.com/hc/en-us/articles/360019430539-Collecting-debug-logs-automatically

- Collect debug logs on mobiles  
  https://help.resilio.com/hc/en-us/articles/38269346960531-Collect-debug-logs-on-mobiles

- Collecting crash reports, mini-dumps and core dumps  
  https://help.resilio.com/hc/en-us/articles/206214615-Collecting-crash-reports-mini-dumps-and-core-dumps

- Collecting core dump on NAS devices  
  https://help.resilio.com/hc/en-us/articles/360015557220-Collecting-core-dump-on-NAS-devices

## Revision addendum — space pressure, byte classes, and reclaim proof

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about free-space warnings, storage thresholds, Selective Sync placeholders, Archive retention, mobile storage accounting, cleanup residue, storage-folder scope, and uninstall leftovers.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid about stop floors, storage classes, and reclaim consequences?

> where do those same current docs still show that the ordinary operator answer about `what is consuming space`, `what will stop syncing`, `what can I reclaim safely`, and `what exactly changed afterward` still depends on hopping across warnings, power-user settings, Sync-mode docs, Archive docs, mobile storage pages, and cleanup notes instead of one stable product-owned page?

The most load-bearing source set for this pass was:

- Resilio's current power-user table, which still publishes `free_space_warning_threashold`, `disk_min_free_space`, and `disk_min_free_space_gb` and still says Sync can warn and stop syncing files at the configured floor.
- Resilio's current core-warning article, which still ties the free-space warning to the disk where the default folder location points.
- Resilio's current synchronization-mode docs, which still distinguish placeholders from materialized files and still describe `Remove from this device` as local placeholder reversion.
- Resilio's current Archive and folder-preferences docs, which still publish retention defaults and still show that disabling Archive weakens retained-delete behavior.
- Resilio's current iOS storage and mobile-settings docs, which still split storage into app data, user data, downloads, shared files, and residual/debug cleanup classes.
- Resilio's current storage-folder and uninstall docs, which still show that configuration, database, logs, dumps, and other non-payload bytes live in separate storage roots and may require deliberate manual cleanup.

## Additional Resilio official sources emphasized in rev0209

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Core warnings  
  https://help.resilio.com/hc/en-us/articles/360001217950-Core-warnings

- Synchronization Modes  
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- Folder Preferences  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- Using Archive for file versioning and restoring deleted files.  
  https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files

- Storage Management on iOS  
  https://help.resilio.com/hc/en-us/articles/115001726304-Storage-Management-on-iOS

- Settings on mobile platforms  
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- Sync Storage folder  
  https://help.resilio.com/hc/en-us/articles/206664690-Sync-Storage-folder

- How to uninstall Sync?  
  https://help.resilio.com/hc/en-us/articles/204775029-How-to-uninstall-Sync

## Revision addendum — network paths, protocol discipline, and freshness risk

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about SMB shares, notification loss on mounted paths, service-mode UNC workarounds, permission/runtime identity consequences, and the current v3 release line.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid about network-path limits, mixed access, and degraded freshness?

> where do those same current docs still show that the ordinary operator answer about `what path class is this`, `which protocol is authoritative`, `how fresh can this location ever be`, and `should this remote path be admitted at all` still depends on hopping across multiple articles instead of one stable product-owned page?

The most load-bearing source set for this pass was:

- Resilio's current SMB article, which still says SMB shares are supported with limitations, still requires full permissions, still limits live notifications to SMB 3.0+, and still warns that mixed direct-plus-Samba access can damage or roll back files.
- Resilio's current Windows service troubleshooting article, which still says mapped drives are unavailable to the service, still recommends UNC entry as a workaround, and still warns that this workaround loses file-update notifications and falls back to rescan or restart.
- Resilio's current change-detection article, which still says some storages such as NFS or SMB2 mounted shares are not even supposed to provide working filesystem notifications and still documents the default 600-second rescan cadence.
- Resilio's current v3 change log, which still shows the active line through `3.1.2.1076`, confirming that these path truths still matter in current product shape rather than abandoned legacy docs.

## Additional Resilio official sources emphasized in rev0210

- Sync and SMB file shares
  https://help.resilio.com/hc/en-us/articles/207755736-Sync-and-SMB-file-shares

- Sync Service Troubleshooting on Windows
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

- How soon does synchronization start?
  https://help.resilio.com/hc/en-us/articles/204754319-How-soon-does-synchronization-start

- Resilio Sync 3.0 change log
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — encrypted-custody workflow ownership after rev0212

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another small cluster of current official Resilio Sync docs about encrypted folders, linked-device identity behavior, pre-populated folder connection, reconnect/default-path drift, and the current v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is still genuinely good at encrypted custody as a product capability?

> where do those same current docs still show that the operator must reconstruct the *whole encrypted-custody workflow* across several articles instead of one product-owned flow?

The most load-bearing source set for this pass was:

- Resilio's current `Encrypted folders` article, which still states the untrusted-peer purpose, manual encrypted-key lane, linked-seat `Disconnected` requirement, strict target-hygiene rule, encrypted-node capability ceilings, saved-key/database continuity prerequisites, CLI decrypt lane, and encrypted-Archive restore ceiling.
- Resilio's current `Can I connect two pre-populated pre-existing folders?` article, which still documents a different non-empty-target branch with hash/merge/winner semantics and a distinct linked-device reconnect ritual.
- Resilio's current `Disconnecting and Removing Folders` article, which still says reconnect may propose a different default path and create a sibling `(1)` directory unless the operator manually retargets.
- Resilio's current `Sync Private Identity & Linking My Devices` article, which still makes linked-device identity, certificate-bearing seat identity, and cross-device availability part of the effective branch logic.
- Resilio's current v3 change log, which still shows the line as active through `3.1.2.1076` and therefore confirms this branch structure is not ancient fossil behavior.

## Additional Resilio official sources emphasized in rev0213

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Encrypted folders  
  https://help.resilio.com/hc/en-us/articles/207370466-Encrypted-folders

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Can I connect two pre-populated pre-existing folders?  
  https://help.resilio.com/hc/en-us/articles/205506569-Can-I-connect-two-pre-populated-pre-existing-folders

- Disconnecting and Removing Folders  
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- Important before updating to Resilio Sync 3.0.0  
  https://help.resilio.com/hc/en-us/articles/31193941051795-Important-before-updating-to-Resilio-Sync-3-0-0

- Updating installation to Resilio Sync v3  
  https://help.resilio.com/hc/en-us/articles/31194252837779-Updating-installation-to-Resilio-Sync-v3

## Revision addendum — typed bootstrap artifacts and intake-route proof

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about linking by `M-key`, ordinary link/key/QR subject claim, encrypted-key manual connection, browser landing pages, and WebUI fallback.
The new questions were:

> where do current official docs most clearly show that Resilio is still genuinely flexible about how bootstrap artifacts arrive?

> where do those same current docs still show that the operator must reconstruct from several articles what family of artifact was actually imported and which reviewed route should follow?

The most load-bearing source set for this pass was:

- Resilio's current `Sync Private Identity & Linking My Devices` article, which still documents `M-key` / `Enter a key`, whole-family linked-device availability, and takeover risk when linking into a non-empty running instance.
- Resilio's current `Comprehensive guide to syncing (Desktop-Desktop)` and `Quick guide to syncing`, which still document ordinary subject claim via link/key/QR and manual `Enter key or link` fallback.
- Resilio's current `Encrypted folders` article, which still documents encrypted-key `Manual connection` and the fact that this lane creates ciphertext-only custody rather than ordinary plaintext-capable membership.
- Resilio's current `Link structure and flow` article, which still says browser links go through a Resilio landing page and then try to hand off into the app.
- Resilio's current `Configuring WebUI` article, which still says clicked-link flows do not work there and manual typed entry remains necessary.
- Resilio's current v3 change log, which still shows the line as active through `3.1.2.1076`, confirming these route shapes still matter in current product shape rather than abandoned lore.

## Additional Resilio official sources emphasized in rev0214

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Comprehensive guide to syncing (Desktop-Desktop)  
  https://help.resilio.com/hc/en-us/articles/204754939-Comprehensive-guide-to-syncing-Desktop-Desktop

- Quick guide to syncing  
  https://help.resilio.com/hc/en-us/articles/205506699-Quick-guide-to-syncing

- Encrypted folders  
  https://help.resilio.com/hc/en-us/articles/207370466-Encrypted-folders

- Link structure and flow  
  https://help.resilio.com/hc/en-us/articles/204754739-Link-structure-and-flow

- Configuring WebUI  
  https://help.resilio.com/hc/en-us/articles/115001184490-Configuring-WebUI

## Revision addendum — destination-world proof after rev0214

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about linked-device synchronization modes, linked-device setup defaults, duplicate-folder fallback, manual location choice, reconnect behavior, pre-populated-folder reuse, and encrypted-folder landing rules.
The new questions were:

> where do current official docs most clearly show that Resilio genuinely supports several distinct destination-world branches rather than one generic folder connect?

> where do those same current docs still show that the ordinary operator answer about `where will this land`, `is this the right world`, and `did reconnect preserve continuity or draft a duplicate branch` still depends on hopping across several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current synchronization-mode docs, which still define `Disconnected`, `Selective Sync`, and `Synced` as materially different arrival postures and still say Disconnected asks where to put the folder later.
- Resilio's current linked-device docs, which still say linking suggests a default folder location and a synchronization mode.
- Resilio's current duplicate-folder and manual-location docs, which still say Selective Sync or Synced auto-land new folders into the default storage root and that disabling Android `Simple mode` enables manual location choice.
- Resilio's current reconnect docs, which still say reconnect can propose a different default path and create a `(1)` sibling unless the operator retargets manually.
- Resilio's current pre-populated-folder docs, which still say linked-device reuse often wants Disconnected posture or disconnect/reconnect ritual.
- Resilio's current encrypted-folder docs, which still say linked-device encrypted custody again wants `Disconnected` posture and a fresh empty directory.

## Additional Resilio official sources emphasized in rev0214

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Synchronization Modes  
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Folders are duplicating with an index (i) in their name.  
  https://help.resilio.com/hc/en-us/articles/204753869-Folders-are-duplicating-with-an-index-i-in-their-name

- How to manually set the location of the folders synced across linked devices?  
  https://help.resilio.com/hc/en-us/articles/206216615-How-to-manually-set-the-location-of-the-folders-synced-across-linked-devices

- Disconnecting and Removing Folders  
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- Can I connect two pre-populated pre-existing folders?  
  https://help.resilio.com/hc/en-us/articles/205506569-Can-I-connect-two-pre-populated-pre-existing-folders

- Encrypted folders  
  https://help.resilio.com/hc/en-us/articles/207370466-Encrypted-folders

## Revision addendum — bind-outcome proof after rev0215

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about pre-populated folder connection, duplicate same-name auto-land, manual location choice, same-ID collision, encrypted-folder target rules, and the current v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio genuinely supports attaching existing bytes instead of always forcing a fresh empty target?

> where do those same current docs still show that the ordinary operator answer about `what semantic branch will this target commit create` still depends on hopping across several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Can I connect two pre-populated pre-existing folders?` article, which still says identical hashes are not re-synced, differing content can yield latest-timestamp replacement, other files merge into the folder tree, and linked devices often want `Disconnected` posture or disconnect/reconnect ritual before reusing an existing directory.
- Resilio's current duplicate-folder and manual-location docs, which still say linked devices in `Selective Sync` or `Synced` auto-land new folders into the default root and can create a same-name `(1)` sibling unless the operator switches to `Disconnected` and chooses the intended location manually.
- Resilio's current `Selected folder is already added to Sync` warning article, which still says `.sync/ID` identifies a share and distinguishes same-subject-on-this-seat collision from ordinary non-empty reuse.
- Resilio's current `Encrypted folders` article, which still says encrypted targets should be fresh empty directories and therefore prove that not every target chooser represents the same branch class.
- Resilio's current `Sync Share Dialog (Desktop)` and `Comprehensive guide to syncing (Desktop-Desktop)` pages, which still show that key/link claim can intentionally point at an existing directory and still treat non-empty confirmation as one small local prompt.
- Resilio's current v3 change log, which still shows the line as active through `3.1.2.1076`, confirming that this branch structure is current product behavior rather than abandoned lore.

## Additional Resilio official sources emphasized in rev0216

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Can I connect two pre-populated pre-existing folders?  
  https://help.resilio.com/hc/en-us/articles/205506569-Can-I-connect-two-pre-populated-pre-existing-folders

- Folders are duplicating with an index (i) in their name.  
  https://help.resilio.com/hc/en-us/articles/204753869-Folders-are-duplicating-with-an-index-i-in-their-name

- How to manually set the location of the folders synced across linked devices?  
  https://help.resilio.com/hc/en-us/articles/206216615-How-to-manually-set-the-location-of-the-folders-synced-across-linked-devices

- Selected folder is already added to Sync  
  https://help.resilio.com/hc/en-us/articles/209316526-Selected-folder-is-already-added-to-Sync

- Encrypted folders  
  https://help.resilio.com/hc/en-us/articles/207370466-Encrypted-folders

- Sync Share Dialog (Desktop)  
  https://help.resilio.com/hc/en-us/articles/204790709-Sync-Share-Dialog-Desktop

- Comprehensive guide to syncing (Desktop-Desktop)  
  https://help.resilio.com/hc/en-us/articles/204754939-Comprehensive-guide-to-syncing-Desktop-Desktop

## Revision addendum — effective seat posture proof after rev0216

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about linked-device owner defaults, one-way/read-only behavior, encrypted-folder capability ceilings, local-share inheritance, and the current v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio genuinely has several materially different effective seat postures rather than one generic `connected` state?

> where do those same current docs still show that the ordinary operator answer about `what can this seat actually do right now` still depends on hopping across several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `User Management` article, which still says linked devices under one identity act as Owners, read-only peers do not propagate local changes, and disconnect revokes only future updates.
- Resilio's current `Sync functionality in detail` and `Comprehensive guide to syncing (Desktop-Desktop)`, which still say linked-device automation makes folders broadly available across your own seats.
- Resilio's current `How to create a Read Only folder while syncing across linked devices?` article, which still documents the disconnect-plus-RO-key workaround for one linked seat.
- Resilio's current `Is one-way synchronization possible?` article, which still documents suspension and overwrite behavior for local mutations on read-only peers.
- Resilio's current `Encrypted folders` article, which still says encrypted peers are read-only, forced-overwrite, and without Selective Sync.
- Resilio's current `Sharing a folder locally` article, which still says local derivatives cannot receive Owner, inherit source ceilings, narrow automatically when the source narrows, and disappear when the source is removed or disconnected.
- Resilio's current v3 change log, which still shows the line as active through `3.1.2.1076`, confirming that these posture distinctions are current product behavior rather than abandoned lore.

## Additional Resilio official sources emphasized in rev0217

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- User Management  
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- Sync functionality in detail  
  https://help.resilio.com/hc/en-us/articles/204754389-Sync-functionality-in-detail

- Comprehensive guide to syncing (Desktop-Desktop)  
  https://help.resilio.com/hc/en-us/articles/204754939-Comprehensive-guide-to-syncing-Desktop-Desktop

- How to create a Read Only folder while syncing across linked devices?  
  https://help.resilio.com/hc/en-us/articles/206216565-How-to-create-a-Read-Only-folder-while-syncing-across-linked-devices

- Is one-way synchronization possible?  
  https://help.resilio.com/hc/en-us/articles/204754279-Is-one-way-synchronization-possible

- Encrypted folders  
  https://help.resilio.com/hc/en-us/articles/207370466-Encrypted-folders

- Sharing a folder locally  
  https://help.resilio.com/hc/en-us/articles/360011582500-Sharing-a-folder-locally

## Revision addendum — visual absence, severance scope, and residual return

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about hidden offline devices, disconnect versus remove, placeholder-local versus peer-wide deletion, identity unlink limits, and stolen-device recovery.

The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that `hide`, `disconnect`, `remove`, `remove from this device`, `remove from all devices`, `unlink`, and `rotate` are not the same severance claim?

> where do those same current docs still show that the ordinary operator answer about `is this actually gone`, `who can still bring it back`, `what bytes remain outside recall`, and `when is broader rotation still required` still depends on hopping across several docs instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `How to clear offline devices?` article, which still says hiding an offline device only removes list clutter, does not unlink it, and the row reappears if that device comes back online.
- Resilio's current `Disconnecting and Removing Folders` article, which still says disconnect affects one device, remove affects linked devices under one identity, and non-linked remote retainers may still keep the folder.
- Resilio's current `Synchronization Modes` and `What Is an RSLS File?` docs, which still distinguish `Remove from this device` from `Remove from all devices`.
- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says unlink is local and remote unlink is unavailable.
- Resilio's current `If your device is stolen` article, which still escalates serious linked-seat compromise to share removal, identity regeneration, relink, and reshare.
- Resilio's current v3 change log, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0219

- Resilio Sync 3.0 change log
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- How to clear offline devices? (desktop only)
  https://help.resilio.com/hc/en-us/articles/204762439-How-to-clear-offline-devices-desktop-only

- Disconnecting and Removing Folders
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- Synchronization Modes
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- What Is an RSLS File?
  https://help.resilio.com/hc/en-us/articles/206115384-What-Is-an-RSLS-File

- Sync Private Identity & Linking My Devices
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- If your device is stolen
  https://help.resilio.com/hc/en-us/articles/204644049-If-your-device-is-stolen

## Revision addendum — post-action claim ceiling and recall overstatement

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about future-update revocation, disconnect vs remove, placeholder-local vs wider deletion, local-only unlink, incident rotation, and the live v3 line.

The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that common actions earn different post-action truth ceilings?

> where do those same current docs still show that the ordinary operator answer about `what am I allowed to say now?` still depends on hopping across several docs instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `User Management` article, which still says disconnect revokes future updates while already-synchronized files remain.
- Resilio's current `Disconnecting and Removing Folders` article, which still says disconnect leaves local bytes, while remove from linked devices may still leave remote non-linked retainers.
- Resilio's current `Synchronization Modes`, `What Is an RSLS File?`, and iOS interface docs, which still distinguish local placeholder eviction from broader deletion and still keep archive consequences visible.
- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says remote unlink is unavailable.
- Resilio's current `If your device is stolen` article, which still escalates some incidents to identity regeneration, relink, and reshare instead of pretending narrower actions completed containment.
- Resilio's current v3 change log, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0220

- Resilio Sync 3.0 change log
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- User Management
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- Disconnecting and Removing Folders
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- Synchronization Modes
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- What Is an RSLS File?
  https://help.resilio.com/hc/en-us/articles/206115384-What-Is-an-RSLS-File

- Sync Interface on iOS devices
  https://help.resilio.com/hc/en-us/articles/212016726-Sync-Interface-on-iOS-devices

- Sync Private Identity & Linking My Devices
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- If your device is stolen
  https://help.resilio.com/hc/en-us/articles/204644049-If-your-device-is-stolen

## Revision addendum — cleanup intent and witness survival

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about disconnect/remove scope, placeholder-local versus all-peer deletion, mobile storage clearing, hidden archive survival, uninstall semantics, and the still-live v3 line.

The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that cleanup verbs are materially different?

> where do those same current docs still show that the ordinary operator answer about `what kind of cleanup this is`, `what witness should be preserved first`, `what survives afterward`, and `what sentence is safe now` still depends on hopping across several docs instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Disconnecting and Removing Folders` article, which still says disconnect affects one device, remove affects linked devices, folders can remain in the filesystem, and non-linked remote retainers may still keep the share.
- Resilio's current `Synchronization Modes` article, which still says `Remove from this device` reverts a local copy to a placeholder while `Remove from all devices` deletes across peers and archives the file there.
- Resilio's current `Selective Sync` article, which still warns that removing a Selective Sync share removes placeholders from the local filesystem.
- Resilio's current `Storage Management on iOS` article, which still separates app data from user data and still says local copies from sync shares can be cleared only when Selective Sync is enabled.
- Resilio's current `How to uninstall Sync?` article, which still says uninstall does not delete previously shared folders or hidden archived files automatically on desktop platforms, while iOS uninstall removes local synced files because of platform architecture.
- Resilio's current v3 change log, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0224

- Resilio Sync 3.0 change log
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Disconnecting and Removing Folders
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- Synchronization Modes
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- Selective Sync
  https://help.resilio.com/hc/en-us/articles/205458095-Selective-Sync

- Storage Management on iOS
  https://help.resilio.com/hc/en-us/articles/115001726304-Storage-Management-on-iOS

- How to uninstall Sync?
  https://help.resilio.com/hc/en-us/articles/204775029-How-to-uninstall-Sync

## Revision addendum — hidden witness access and surface visibility

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about hidden Archive location, surface-specific Archive access, critical `.sync` service state, uninstall residue, and the still-live v3 line.

The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that proof can exist yet still be hidden or inaccessible from the current surface?

> where do those same current docs still show that the ordinary operator answer about `does the witness still exist`, `can I inspect it here`, `is it only hidden`, and `what better surface should I switch to` still depends on hopping across several docs instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Using Archive for file versioning and restoring deleted files` article, which still says Archive is opened directly from desktop Sync UI, that Android and WebUI rely on file-browser access to hidden `.sync/Archive`, and that Archive is not accessible on iOS.
- Resilio's current `What is '.sync' folder, and StreamsList, IgnoreList and Archive inside?` article, which still says `.sync` is hidden by default, critical for syncing, and unsafe to move separately from the shared folder.
- Resilio's current `How to uninstall Sync?` article, which still says desktop uninstall removes the program but not previously shared folders and may still leave hidden Archive material unless removed manually.
- Resilio's current v3 change log, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0225

- Resilio Sync 3.0 change log
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Using Archive for file versioning and restoring deleted files.
  https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files

- What is '.sync' folder, and StreamsList, IgnoreList and Archive inside?
  https://help.resilio.com/hc/en-us/articles/206217185-What-is-sync-folder-and-StreamsList-IgnoreList-and-Archive-inside

- How to uninstall Sync?
  https://help.resilio.com/hc/en-us/articles/204775029-How-to-uninstall-Sync

## Revision addendum — proxy artifacts and local-looking action scope

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about placeholder files, placeholder deletion semantics, last-full-copy risk, conflict derivatives, and the still-live v3 line.

The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that visible filesystem rows are not always ordinary local files?

> where do those same current docs still show that the ordinary operator answer about `what this row really is`, `what subject it stands for`, and `what delete or move would actually do` still depends on hopping across several docs instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `What Is an RSLS File?` article, which still says `.rsls` entries are zero-byte placeholders, distinguishes `Remove from this device` from broader deletion, and warns that all peers can end up with placeholders only.
- Resilio's current `Conflict files in Sync` article, which still says `.Conflict` rows correspond to real remote material and should not simply be deleted.
- Resilio's current `Synchronization Modes` article, which still reinforces placeholder behavior and local-removal versus all-peer-removal distinctions.
- Resilio's current v3 change log, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0226

- Resilio Sync 3.0 change log
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- What Is an RSLS File?
  https://help.resilio.com/hc/en-us/articles/206115384-What-Is-an-RSLS-File

- Synchronization Modes
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- Conflict files in Sync
  https://help.resilio.com/hc/en-us/articles/204753629-Conflict-files-in-Sync

## Revision addendum — subject non-arrival diagnosis and least-strong intervention

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about missing files, ghost subjects, locked files, watcher exhaustion, hidden background work, continuity breaks, and the still-live v3 line.

The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that `not here` can mean policy exclusion, local blockage, hidden work, route weakness, ghost state, or continuity damage?

> where do those same current docs still show that the ordinary operator answer about `which absent-state class applies` and `what least-strong move is justified` still depends on hopping across several docs instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `My files don't sync` article, which still enumerates IgnoreList exclusion, xattrs limits, local locks, read-only overwrite posture, missing write permissions, encoding/path-length issues, merge failure, filesystem errors, missed notifications, low free space, stuck `.!sync` residue, and clock skew.
- Resilio's current `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time` article, which still describes ghost-file states where a subject remains advertised in the tree even though no peer now has the bytes.
- Resilio's current `Locked files` article, which still says the product can show which files are locked but cannot identify the locking application.
- Resilio's current watcher-exhaustion article, which still says live notification loss pushes discovery onto manual or periodic rescan.
- Resilio's current `Some internal tasks are taking time to complete` article, which still says hashing, merge, scanning, block checks, transfer, and writing may explain delay without proving a hard stall.
- Resilio's current `Service files missing / Cannot identify destination folder` article, which still treats `.sync` loss as continuity-bearing damage that suspends syncing for that folder.
- Resilio's current v3 change log, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0227

- Resilio Sync 3.0 change log
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- My files don't sync
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Cannot download files / These files cannot be downloaded as there are no source peers online for too long time.
  https://help.resilio.com/hc/en-us/articles/360010899719-Cannot-download-files-These-files-cannot-be-downloaded-as-there-are-no-source-peers-online-for-too-long-time

- Locked files
  https://help.resilio.com/hc/en-us/articles/205504549-Locked-files

- Agent run out of system notify watchers. Updated files will be uploaded only after periodic folder rescan
  https://help.resilio.com/hc/en-us/articles/360015593120-Agent-run-out-of-system-notify-watchers-Updated-files-will-be-uploaded-only-after-periodic-folder-rescan

- Some internal tasks are taking time to complete
  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete

- Service files missing / Cannot identify destination folder
  https://help.resilio.com/hc/en-us/articles/205450225-Service-files-missing-Cannot-identify-destination-folder

## Revision addendum — runtime profile continuity, storage-lineage, and surface reach after rev0227

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about Windows service installation, service troubleshooting, storage-folder placement, config-mode storage roots, Linux runtime flags, uninstall residue, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that runtime profile is materially real rather than a cosmetic launch choice?

> where do those same current docs still show that the ordinary operator answer about `which runtime profile is active`, `which storage root is authoritative`, `whether shares and identity carried over`, and `what surfaces widened or narrowed` still depends on hopping across several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Running Sync as a service on Windows` article, which still distinguishes migrate-settings from clean installation and still says a clean install requires re-share / reconnect work.
- Resilio's current `Sync Service Troubleshooting on Windows` article, which still says Local System can create a new storage root, present `SYSTEM`, show no old shares, require re-add / reconnect, narrow file-update observation, and default WebUI to localhost without config changes.
- Resilio's current `Sync Storage folder` article, which still says settings, configuration, databases, logs, and identity details live in profile-specific storage roots.
- Resilio's current `Running Sync in configuration mode` article, which still says `storage_path` creates new settings there and that config mode supports only Standard folders.
- Resilio's current `Guide to Linux, and Sync peculiarities` article, which still treats WebUI listen scope and storage path as runtime-shaping flags and still warns that binding to an unavailable interface can shut Sync down.
- Resilio's current `How to uninstall Sync?` article, which still distinguishes unlinking identity, removing shares, and manually deleting service/profile roots.
- Resilio's current v3 change log, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0228

- Running Sync as a service on Windows  
  https://help.resilio.com/hc/en-us/articles/207701296-Running-Sync-as-a-service-on-Windows

- Sync Service Troubleshooting on Windows  
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

- Sync Storage folder  
  https://help.resilio.com/hc/en-us/articles/206664690-Sync-Storage-folder

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Guide to Linux, and Sync peculiarities  
  https://help.resilio.com/hc/en-us/articles/204762449-Guide-to-Linux-and-Sync-peculiarities

- How to uninstall Sync?  
  https://help.resilio.com/hc/en-us/articles/204775029-How-to-uninstall-Sync

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — platform permission provenance, denial fallout, and mobile capability truth after rev0232

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about Android / Kindle permissions, mobile settings, mobile interface affordances, battery / auto-sleep behavior, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that platform permissions unlock materially different powers rather than one generic `mobile access` blob?

> where do those same current docs still show that the ordinary operator answer about `why is the app asking for this`, `what remains true if I refuse it`, and `is this camera-only, storage-only, alerts-only, startup-only, or background-only` still depends on hopping across several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current v3 change log, which still shows the live `3.1.2.1076` line.
- Resilio's current `Permissions Sync requires on Android and Amazon Kindle` article, which still ties account, storage, camera, Wi-Fi/network, startup, wake, and messaging permissions to concrete product powers.
- Resilio's current `Settings on mobile platforms` article, which still ties notification disablement to lower system priority and possible background stoppage, and still exposes Auto-start / Battery saver / Auto-sleep as first-class mobile behaviors.
- Resilio's current `Sync interface on Android` and `Sync Interface on iOS devices` articles, which still show QR scan, manual key entry, per-share network controls, archive toggles, and placeholder-clearing actions as separate mobile capabilities.
- Resilio's current `Configuring Auto Sleep & Battery Saver (Android)` article, which still says the core can stop and peers no longer see the device online.

## Additional Resilio official sources emphasized in rev0233

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Permissions Sync requires on Android and Amazon Kindle  
  https://help.resilio.com/hc/en-us/articles/205451065-Permissions-Sync-requires-on-Android-and-Amazon-Kindle

- Settings on mobile platforms  
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- Sync interface on Android  
  https://help.resilio.com/hc/en-us/articles/213500383-Sync-interface-on-Android

- Sync Interface on iOS devices  
  https://help.resilio.com/hc/en-us/articles/212016726-Sync-Interface-on-iOS-devices

- Configuring Auto Sleep & Battery Saver (Android)  
  https://help.resilio.com/hc/en-us/articles/204762699-Configuring-Auto-Sleep-Battery-Saver-Android

## Revision addendum — presence witness grade, hidden-listed peers, and source-proof truth after rev0234

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about peer-list totals, linked-device dots and modes, hidden offline devices, no-source warnings, mobile network stoppage, auto-sleep, pause semantics, switched-off devices, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that `listed`, `online`, `eligible`, and `has a current source` are materially different truths rather than one `present` bit?

> where do those same current docs still show that the ordinary operator answer about `what is actually present enough here for me to trust this row or subject?` still depends on hopping across several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Sync Main View (Desktop)` article, which still says `X of Y peers` means `X` online now and `Y` total including offline, and still says offline peers disconnect after 7 days by default.
- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says linked devices show green/grey dots for online/offline and display selected sync modes.
- Resilio's current `How to clear offline devices?` article, which still says clearing only hides a device from view and does not unlink it, and that it reappears if it comes back online.
- Resilio's current `Setting network interface per share`, `Settings on mobile platforms`, and `Configuring Auto Sleep & Battery Saver (Android)` articles, which still say visible shares can be forbidden-network or sleep-blocked rather than route-broken.
- Resilio's current `How to pause syncing` article, which still says pause stops payload movement but not every non-payload effect.
- Resilio's current `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time` article, which still describes ghost-file states where subjects are announced but nobody currently has the bytes.
- Resilio's current `Will my devices still sync when switched off?` article, which still says a source device must actually be online for syncing to work.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0235

- Sync Main View (Desktop)  
  https://help.resilio.com/hc/en-us/articles/204755009-Sync-Main-View-Desktop

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- How to clear offline devices? (desktop only)  
  https://help.resilio.com/hc/en-us/articles/204762439-How-to-clear-offline-devices-desktop-only

- Setting network interface per share  
  https://help.resilio.com/hc/en-us/articles/360001411244-Setting-network-interface-per-share

- Settings on mobile platforms  
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- Configuring Auto Sleep & Battery Saver (Android)  
  https://help.resilio.com/hc/en-us/articles/204762699-Configuring-Auto-Sleep-Battery-Saver-Android

- How to pause syncing  
  https://help.resilio.com/hc/en-us/articles/206217325-How-to-pause-syncing

- Cannot download files / These files cannot be downloaded as there are no source peers online for too long time.  
  https://help.resilio.com/hc/en-us/articles/360010899719-Cannot-download-files-These-files-cannot-be-downloaded-as-there-are-no-source-peers-online-for-too-long-time

- Will my devices still sync when switched off?  
  https://help.resilio.com/hc/en-us/articles/204754199-Will-my-devices-still-sync-when-switched-off

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Additional Resilio official sources emphasized in rev0243

- Disconnecting and Removing Folders  
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- Selective Sync  
  https://help.resilio.com/hc/en-us/articles/205458095-Selective-Sync

- Synchronization Modes  
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- Folder Types and Management  
  https://help.resilio.com/hc/en-us/articles/204762459-Folder-Types-and-Management

- I'm using Sync Free and there is no "Disconnect” button in the folder menu...  
  https://help.resilio.com/hc/en-us/articles/205504569-I-m-using-Sync-Free-and-there-is-no-Disconnect-button-in-the-folder-menu

## Revision addendum — local protection, Files-app Recents loss, and copy-return editing after rev0248

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about mobile passcode protection, iOS Files-app visibility, sandbox storage, outside-app copy-return editing, and Windows Phone local recovery limits.
The new questions were:

> where do current official docs most clearly show that `protect this app` also changes OS visibility and recovery ceiling rather than just adding a local lock?

> where do those same current docs still show that the ordinary operator answer about `what exactly happens if I open this file in another app?` still depends on a settings page, peculiarities page, and edit tutorial instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Settings on mobile platforms` article, which still says iOS `Touch ID & passcode` hides files from Files-app `Recents`, and still says forgotten Windows Phone passcodes force reinstall with local in-app data loss.
- Resilio's current `How to edit a document stored in Sync? (iOS)` article, which still says iOS editing requires importing into another app, then manually putting the modified document back, and still says automatic replacement may fail leaving old/new versions side by side.
- Resilio's current `Sync for iOS Peculiarities` article, which still says `Open In...` copies a file to another app, that edits there do not affect the Sync copy until sent back, and that deleting on iOS merely un-syncs locally.
- Resilio's current `Storage Management on iOS` article, which still says Sync keeps files in its sandbox, separates app data from user data, and only allows local-copy clearing when Selective Sync is enabled.
- Resilio's current `Sync for Windows Phone Peculiarities` article, which still says files opened in another app are copied, changes there do not affect the Sync-stored file until sent back, and deleting on the phone does not delete on other peers.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0248

- Settings on mobile platforms  
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- How to edit a document stored in Sync? (iOS)  
  https://help.resilio.com/hc/en-us/articles/204762379-How-to-edit-a-document-stored-in-Sync-iOS

- Sync for iOS Peculiarities  
  https://help.resilio.com/hc/en-us/articles/205506539-Sync-for-iOS-Peculiarities

- Storage Management on iOS  
  https://help.resilio.com/hc/en-us/articles/115001726304-Storage-Management-on-iOS

- Sync for Windows Phone Peculiarities  
  https://help.resilio.com/hc/en-us/articles/205506559-Sync-for-Windows-Phone-Peculiarities

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — permission-plane mode, reference authority, and inheritance rewrite after rev0250

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio docs about permission-sync modes, Reference Agent authority, local re-inheritance, substrate-delayed apply, privilege floor, and pre-seeded comparison behavior.
The new questions were:

> where do current official docs most clearly show that `sync permissions` is not one behavior but a family of materially different contracts?

> where do those same current docs still show that the ordinary operator answer about `what permission contract is actually in force here?` still depends on hopping across several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Syncing file system permissions` article, which still says permission sync has distinct NTFS/POSIX modes, that `Re-apply local inherited permissions` exists because partial downloads are staged through the service `.sync` directory, that permissions can be preserved on incompatible storage and only applied later on compatible substrate, and that local admin / Local System / root and stronger SMB service-account rights can be required.
- Resilio's current `Profiles` article, which still says the permission-sync mode is a job-profile parameter and that for Synchronization, Hybrid Work, and File Caching jobs these settings are applied when the job is created and cannot be changed later.
- Resilio's current `Reference Agent` article, which still says pre-seeded RW peers can otherwise merge or scramble permissions, that selecting a Reference Agent drives an initial synchronization that disables inheritance on the sync root and overwrites local permissions from the Reference Agent, and that changing/removing that reference has real continuity consequences.
- Resilio's current `Synchronizing pre-seeded folder` article, which still says file permissions participate in the attribute check that decides whether a file needs synchronization, and that disabling permission sync can remove permissions from that equation.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0251

- Syncing file system permissions  
  https://www.resilio.com/documentation/content/advanced-configuration/agents/syncing_file_system_permissions/

- Profiles  
  https://www.resilio.com/documentation/content/advanced-configuration/profiles-and-configuration-parameters/profiles/

- Reference Agent  
  https://www.resilio.com/documentation/content/advanced-configuration/mc-and-jobs/reference_agent/

- Synchronizing pre-seeded folder  
  https://www.resilio.com/documentation/content/advanced-configuration/best-practices/synchronizing_pre-seeded_folder/

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — compare-plane mutability and same-file claim ceilings after rev0255

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio / Active Everywhere docs about pre-seeded compare rules, file-property scope, permission-plane participation, and mixed-system metadata narrowing.
The new questions were:

> where do current official docs most clearly show that `same file` and `needs sync` are not one eternal rule but a mutable comparison contract?

> where do those same current docs still show that the ordinary operator answer about `what counts as the same object here?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Synchronizing pre-seeded folder` guide, which still says the quick `needs sync` decision uses creation timestamp, modification timestamp, size, and file permissions; still says creation time can be removed from the equation; and still says disabling permission sync removes permissions from the equation.
- Resilio's current `File properties being synchronized and not` reference, which still splits properties by operating system into synchronized, optionally synchronized, and not synchronized families, including execute bits, alternate streams, xattrs, Finder labels/comments, and creation-time/version caveats.
- Resilio's current `Syncing file system permissions` guide, which still says permission-sync modes are real job-profile choices, can be fixed at job creation for major job families, and may preserve permissions on incompatible storage for later application rather than native parity now.
- Resilio's current `My files don't sync` troubleshooting article, which still says xattr/stream narrowing on mixed systems can cause bundle-like macOS objects to sync as ordinary subdirectories.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0255

- Synchronizing pre-seeded folder  
  https://www.resilio.com/documentation/content/advanced-configuration/best-practices/synchronizing_pre-seeded_folder/

- File properties being synchronized and not  
  https://www.resilio.com/documentation/content/reference-information/file_properties_being_synchronized_and_not/

- Syncing file system permissions  
  https://www.resilio.com/documentation/content/advanced-configuration/agents/syncing_file_system_permissions/

- My files don't sync  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — status drill-in, KB handoff, and route fragmentation after rev0259

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about main-view row semantics, troubleshooting click paths, item-level locked-file detail, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that rows, peers lists, history, queue, and item slices are different diagnostic objects?

> where do those same current docs still show that the ordinary operator answer about `what should I open next from this failing row, and what will that route actually prove?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Sync Main View (Desktop)` article, which still says statuses show current activity, that green check means files are synced with all connected peers, that `X of Y` opens the peers list, and that History is a distinct 30-day activity surface.
- Resilio's current `My files don't sync` article, which still tells operators to click the peers count, click status warnings that often lead to KB explanations, inspect Sync History, and open peers lists to inspect upload/download queues.
- Resilio's current `Locked files` article, which still says the error message is clickable and opens the list of locked files, while also saying Sync still cannot identify which application locked them.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line and records that `Can't download file` had to be fixed to be clickable.

## Additional Resilio official sources emphasized in rev0260

- Sync Main View (Desktop)  
  https://help.resilio.com/hc/en-us/articles/204755009-Sync-Main-View-Desktop

- My files don't sync  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Locked files  
  https://help.resilio.com/hc/en-us/articles/205504549-Locked-files

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — change-detection coverage and freshness after rev0272

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about filesystem notifications, scheduled rescans, watcher exhaustion, IgnoreList reread timing, and NAS sleep-preserving cadence changes.
The new questions were:

> where do current official docs most clearly show that `noticed` is not one invariant background promise but a posture that can be notification-backed, rescan-backed, or effectively manual?

> where do those same current docs still show that the ordinary operator answer about `is this actually late yet?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `How soon does synchronization start?` FAQ, which still says filesystem notifications are the fastest path, still says scheduled rescans run every 600 seconds by default and on Sync start, still says `folder_rescan_interval` can change that cadence, and still says setting it to zero disables rescans even on restart.
- Resilio's current `Agent run out of system notify watchers` warning article, which still says watcher exhaustion means Sync will only learn about changes by periodic or manual rescans until watcher limits are raised.
- Resilio's current `Ignoring files in Sync (Ignore List)` article, which still says IgnoreList is reread on change or every `folder_rescan_interval` if notifications are not coming, and still recommends restart for immediate application.
- Resilio's current `Sync prevents HDD from sleeping on NAS...` article, which still recommends substantially widening `folder_rescan_interval`, `config_refresh_interval`, and `config_save_interval` to preserve sleep behavior.
- Resilio's current `Power user preferences` reference, which still documents the relevant advanced settings family and profiler/log/config cadence controls.
- Resilio's current `Resilio Sync change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0273

- How soon does synchronization start?  
  https://help.resilio.com/hc/en-us/articles/204754319-How-soon-does-synchronization-start

- Agent run out of system notify watchers. Updated files will be uploaded only after periodic folder rescan  
  https://help.resilio.com/hc/en-us/articles/360015593120-Agent-run-out-of-system-notify-watchers-Updated-files-will-be-uploaded-only-after-periodic-folder-rescan

- Ignoring files in Sync (Ignore List)  
  https://help.resilio.com/hc/en-us/articles/205458165-Ignoring-files-in-Sync-Ignore-List

- Sync prevents HDD from sleeping on NAS...  
  https://help.resilio.com/hc/en-us/articles/205449995-Sync-prevents-HDD-from-sleeping-on-NAS

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Resilio Sync change log  
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log

## Revision addendum — freshness-claim invalidation and revalidation after rev0273

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about watcher exhaustion, SMB/UNC notification loss, service-profile changes, NAS sleep-preserving cadence changes, Android auto-sleep, battery-saver stops, forbidden-network posture, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that an earlier `should have been noticed already` judgment can become stale because the observation posture changed later?

> where do those same current docs still show that the ordinary operator answer about `does the old freshness claim still apply?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Agent run out of system notify watchers` warning article, which still says watcher exhaustion pushes discovery onto periodic or manual rescans until limits are raised.
- Resilio's current `Sync Service Troubleshooting on Windows` article, which still says network-drive / UNC service setups may lose notifications and that switching to Local System creates a different storage root and share world.
- Resilio's current `Sync and SMB file shares` article, which still says missing SMB notifications reduce discovery to full folder rescan.
- Resilio's current `How soon does synchronization start?` FAQ, which still says default scheduled rescans are 600 seconds, that `folder_rescan_interval` can widen or remove that cadence, and that setting it to zero disables rescans even on restart.
- Resilio's current `Sync prevents HDD from sleeping on NAS...` article, which still recommends widening rescan / refresh / save intervals to preserve NAS sleep.
- Resilio's current `Configuring Auto Sleep & Battery Saver (Android)` article, which still says the mobile core can go offline between wake intervals and can be forced to stop below a battery threshold.
- Resilio's current `Setting network interface per share` article, which still says forbidden-network posture prevents peers from connecting and new or updated files from being detected.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0274

- Agent run out of system notify watchers. Updated files will be uploaded only after periodic folder rescan  
  https://help.resilio.com/hc/en-us/articles/360015593120-Agent-run-out-of-system-notify-watchers-Updated-files-will-be-uploaded-only-after-periodic-folder-rescan

- Sync Service Troubleshooting on Windows  
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

- Sync and SMB file shares  
  https://help.resilio.com/hc/en-us/articles/207755736-Sync-and-SMB-file-shares

- How soon does synchronization start?  
  https://help.resilio.com/hc/en-us/articles/204754319-How-soon-does-synchronization-start

- Sync prevents HDD from sleeping on NAS...  
  https://help.resilio.com/hc/en-us/articles/205449995-Sync-prevents-HDD-from-sleeping-on-NAS

- Configuring Auto Sleep & Battery Saver (Android)  
  https://help.resilio.com/hc/en-us/articles/204762699-Configuring-Auto-Sleep-Battery-Saver-Android

- Setting network interface per share  
  https://help.resilio.com/hc/en-us/articles/360001411244-Setting-network-interface-per-share

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — next-observation opportunity and late-claim honesty after rev0274

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about background/runtime class, Android wake intervals and battery stops, notification-priority loss, mobile network gating, watcher-exhaustion fallback, service / UNC notification loss, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that different seats earn different next honest chances to notice, publish, or fetch changes?

> where do those same current docs still show that the ordinary operator answer about `is this actually late yet?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Does Sync work in background?` article, which still says desktop hidden runtime stays active, Android can work in background but task killers can stop it, and iOS background synchronization is unavailable.
- Resilio's current `Configuring Auto Sleep & Battery Saver (Android)` article, which still says Android may hibernate between wake intervals, wake on a configured interval that is 30 minutes by default, and stop below a battery threshold.
- Resilio's current `Settings on mobile platforms` article, which still says disabling Android notifications can lower Sync's priority so it may stop working in the background and still keeps mobile-data / Wi-Fi policy in a separate settings surface.
- Resilio's current `How soon does synchronization start?` article plus `Power user preferences`, which still keep periodic rescans as the fallback observation path when notifications are missing or weakened.
- Resilio's current `Agent run out of system notify watchers` article, which still says watcher exhaustion downgrades discovery to periodic or manual rescans.
- Resilio's current `Sync Service Troubleshooting on Windows` article, which still says service-style UNC setups may lose file-update notifications and therefore shift observation onto rescan or restart.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0275

- Does Sync work in background?  
  https://help.resilio.com/hc/en-us/articles/206816823-Does-Sync-work-in-background

- Configuring Auto Sleep & Battery Saver (Android)  
  https://help.resilio.com/hc/en-us/articles/204762699-Configuring-Auto-Sleep-Battery-Saver-Android

- Settings on mobile platforms  
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- How soon does synchronization start?  
  https://help.resilio.com/hc/en-us/articles/204754319-How-soon-does-synchronization-start

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Agent run out of system notify watchers. Updated files will be uploaded only after periodic folder rescan  
  https://help.resilio.com/hc/en-us/articles/360015593120-Agent-run-out-of-system-notify-watchers-Updated-files-will-be-uploaded-only-after-periodic-folder-rescan

- Sync Service Troubleshooting on Windows  
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — quiet cohorts and counterpart agreement after rev0276

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about manual pause, Global Pause, scheduler `Paused`, local-control scope, counterpart asymmetry, ongoing delete/indexing behavior, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that pause controls are still mainly **local** controls rather than reviewed shared quiet agreements?

> where do those same current docs still show that the ordinary operator answer about `is the cohort actually quiet enough for this job?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `How to pause syncing` article, which still says pause stops only bits download/upload while zero-sized files and deletions still sync, new files are rescanned and indexed, and Global Pause affects all shares on the current device.
- Resilio's current `Sync Preferences` article, which still presents Global Pause / Resume and Scheduler as ordinary local controls.
- Resilio's current `Running Sync on schedule` article, which still says scheduled `Paused` means upload/download speed are zero while zero-sized files and deletions still sync, new files are rescanned and indexed, and paused peers may still upload to non-paused peers while not downloading themselves.
- Resilio's still-published historical `Resilio Sync change log`, which still records `Sync stopping indexing if folder paused`.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0277

- How to pause syncing  
  https://help.resilio.com/hc/en-us/articles/206217325-How-to-pause-syncing

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Running Sync on schedule  
  https://help.resilio.com/hc/en-us/articles/210783266-Running-Sync-on-schedule

- Resilio Sync change log  
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — quiet-break provenance and resume-authority review after rev0277

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about manual pause/resume, local Global Pause / Resume, scheduler clock boundaries, startup/runtime reactivation, hidden background activity, historical paused-state subtlety, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that reactivation may come from **manual**, **scheduled**, **startup**, or **background** causes rather than one clean shared `resume` object?

> where do those same current docs still show that the ordinary operator answer about `who broke the quiet claim, by what authority, and was that expected?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `How to pause syncing` article, which still says pause stops only bits download/upload while zero-sized files and deletions still sync, new files are rescanned and indexed, and resume is performed by repeating the same local steps.
- Resilio's current `Running Sync on schedule` article, which still says empty cells allow full bandwidth while `Paused` is only a speed-zero local state with residual delete/indexing behavior and asymmetric peer behavior.
- Resilio's current `Sync Preferences` article, which still places Start Sync on startup, Global Pause / Resume, and Scheduler together as ordinary local controls.
- Resilio's current `Does Sync work in background?` article, which still says desktop hidden runtime remains active, Linux can run headlessly, and Android can keep working in background unless the platform/runtime stops it.
- Resilio's still-published historical `Resilio Sync change log`, which still records `Sync stopping indexing if folder paused`.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0278

- How to pause syncing  
  https://help.resilio.com/hc/en-us/articles/206217325-How-to-pause-syncing

- Running Sync on schedule  
  https://help.resilio.com/hc/en-us/articles/210783266-Running-Sync-on-schedule

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Does Sync work in background?  
  https://help.resilio.com/hc/en-us/articles/206816823-Does-Sync-work-in-background

- Resilio Sync change log  
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — allowed residuals and quiet-challenge classification after rev0278

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about manual pause, scheduled `Paused`, surviving delete/control/indexing behavior, paused-peer upload asymmetry, historical paused-state subtlety, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that specific kinds of motion can still happen during `pause` or scheduled `Paused`?

> where do those same current docs still show that the ordinary operator answer about `did this event actually break the quiet claim, or was it expected residue?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `How to pause syncing` article, which still says pause stops only bits download/upload while zero-sized files still sync, deletions still sync, and new files are still rescanned and indexed so share size can increase on paused peers.
- Resilio's current `Running Sync on schedule` article, which still says scheduled `Paused` leaves those same residuals alive and can still let paused peers upload to other non-paused peers while not downloading themselves.
- Resilio's current `Sync Preferences` article, which still presents Global Pause / Resume and Scheduler as ordinary local controls rather than a later challenge-classification object.
- Resilio's still-published historical `Resilio Sync change log`, which still records `Sync stopping indexing if folder paused`.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0279

- How to pause syncing  
  https://help.resilio.com/hc/en-us/articles/206217325-How-to-pause-syncing

- Running Sync on schedule  
  https://help.resilio.com/hc/en-us/articles/210783266-Running-Sync-on-schedule

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Resilio Sync change log  
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — backlog release shape and post-quiet order after rev0279

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about scheduled quiet-window expiry, full-bandwidth return, file download priority, global transfer-priority defaults, queue caps, preemption exceptions, visible-vs-actual queue order, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that leaving quiet can snap back to full bandwidth while backlog order is only partly described by visible queue chrome?

> where do those same current docs still show that the ordinary operator answer about `what resumes first, at what cap, and how bursty will catch-up be?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Running Sync on schedule` article, which still says empty cells mean full bandwidth available, unchecked upload or download means full bandwidth for that direction, and scheduled `Paused` still preserves certain residual behaviors.
- Resilio's current `File download priority` article, which still says per-share priority and global `folder_defaults.transfer_priority` can both shape order, manual share priority stops inheriting later global changes even if later set back to `None`, only up to 50,000 active files are prioritized, higher-priority arrivals suspend lower-priority work with some internal exceptions, non-splittable files do not fully obey strict prioritization, and the visible UI queue may still appear alphabetical rather than actual execution order.
- Resilio's current `Power user preferences` article, which still publishes `folder_defaults.transfer_priority` as a standing default plane.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0280

- Running Sync on schedule  
  https://help.resilio.com/hc/en-us/articles/210783266-Running-Sync-on-schedule

- File download priority  
  https://help.resilio.com/hc/en-us/articles/42328167759251-File-download-priority

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — maintenance rejoin and shared-line restoration after rev0282

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about Read Only suspension, overwrite healing, encrypted-backup restore limits, storage-oriented backup lanes, device-local disconnect semantics, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that local work under a narrow or backup-like posture can survive with several materially different later restoration paths?

> where do those same current docs still show that the ordinary operator answer about `how can this work rejoin the shared line now?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `User Management` article, which still says Read Only changes do not propagate and further synchronization of the changed files is suspended for that peer.
- Resilio's current `Is one-way synchronization possible?` article, which still says overwrite healing can restore deleted files, re-download old names after renames, revert edited contents to the most recent RW version, and keep newly added files local instead of syncing them.
- Resilio's current `Folder Preferences` article, which still says `Overwrite any changed files` is potentially destructive and disabled for Read-only folders with Selective Sync ON.
- Resilio's current `Encrypted folders` article, which still says encrypted backup nodes are Read Only, always have overwrite enabled, need saved keys plus preserved database continuity or local decrypt flow for restoration, and cannot simply restore encrypted-archive files back into the swarm.
- Resilio's current `How to use Camera Backup (all mobiles)?` article, which still says backup folders are storage-oriented Read Only folders and disconnect leaves already-present files on both ends.
- Resilio's current `Sync Interface on iOS devices` article, which still says `Remove from this device` disconnects only on that device and preserves files on others.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0283

- User Management  
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- Is one-way synchronization possible?  
  https://help.resilio.com/hc/en-us/articles/204754279-Is-one-way-synchronization-possible

- Folder Preferences  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- Encrypted folders  
  https://help.resilio.com/hc/en-us/articles/207370466-Encrypted-folders

- How to use Camera Backup (all mobiles)?  
  https://help.resilio.com/hc/en-us/articles/205506809-How-to-use-Camera-Backup-all-mobiles

- Sync Interface on iOS devices  
  https://help.resilio.com/hc/en-us/articles/212016726-Sync-Interface-on-iOS-devices

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — destructive-heal preview and loss-waiver truth after rev0283

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about Read Only overwrite healing, Archive/device-locality rules, archive-retention defaults, encrypted-backup hardwiring, mobile overwrite/archive toggles, configuration-mode defaults, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that `overwrite changed files` is not a self-contained truth because change class, archive-bearing locality, and retention policy all affect what is actually lost?

> where do those same current docs still show that the ordinary operator answer about `what exactly will be surrendered now, and what can I still salvage first?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Is one-way synchronization possible?` article, which still says Read Only overwrite healing re-downloads old names after renames, restores deleted files, reverts edited contents to the most recent RW version, and leaves newly added files local rather than syncing them.
- Resilio's current `Folder Preferences` article, which still says `Overwrite any changed files` is potentially destructive, while Archive stores remotely caused changed or deleted files in `.sync/Archive` for 30 days by default and disabling Archive removes that safety copy and changes rename/copy behavior.
- Resilio's current `Using Archive for file versioning and restoring deleted files` article, which still says a device's Archive receives prior versions only when the file was modified by another peer and that local deletions are usually recovered from local trash instead.
- Resilio's current `Encrypted folders` article, which still says encrypted backup nodes are Read Only, always have overwrite enabled, and can move same-key preexisting encrypted files into Archive with extra space cost.
- Resilio's current `Power user preferences` article, which still publishes `overwrite_changes false` and `sync_trash_ttl 30 (day)` as standing defaults shaping destructive-heal posture.
- Resilio's current `Sync interface on Android` and `Sync Interface on iOS devices` articles, which still expose separate Archive and overwrite toggles on mobile.
- Resilio's current `Running Sync in configuration mode` article, which still documents `"overwrite changes": "true"` as restoring modified files to original version for read-only configuration-mode setups.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0284

- Is one-way synchronization possible?  
  https://help.resilio.com/hc/en-us/articles/204754279-Is-one-way-synchronization-possible

- Folder Preferences  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- Using Archive for file versioning and restoring deleted files.  
  https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files

- Encrypted folders  
  https://help.resilio.com/hc/en-us/articles/207370466-Encrypted-folders

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Sync interface on Android  
  https://help.resilio.com/hc/en-us/articles/213500383-Sync-interface-on-Android

- Sync Interface on iOS devices  
  https://help.resilio.com/hc/en-us/articles/212016726-Sync-Interface-on-iOS-devices

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — authority policy, delegation boundary, and revocation residue after rev0288

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about Standard-vs-Advanced permission semantics, Owner delegation, linked-device ownership, read-only breakage and overwrite-heal posture, derivative-local share narrowing, and revocation residue.
The new questions were:

> where do current official docs most clearly show that `who can do what here?` is still answered differently depending on folder family, identity family, and derivative-local class?

> where do those same current docs still show that `change permission`, `revoke`, and `share onward` are not one stable operator grammar today because some paths are live policy edits and others are remove-and-reissue or local-derivative caveats?

The most load-bearing source set for this pass was:

- Resilio's current `Sync functionality in detail` article, which still says Owner can share, change permissions, and revoke access, and that linked devices under one identity can approve from any linked device.
- Resilio's current `User Management` article, which still says linked devices under one identity act as Owners, that Read Only changes do not propagate and suspend further sync for changed files on that peer, and that disconnect cuts off future updates while already-synchronized files remain.
- Resilio's current `What's the difference between Standard and Advanced folders?` article, which still says Standard folders have no Owner concept, any peer can share the key it has, and permission changes there require removing and re-adding with a new key.
- Resilio's current `Sync Share Dialog (Desktop)` article, which still says only Owners can share Advanced folders, while Standard folders have no Owner level and keys do not use the approval mechanism.
- Resilio's current `How to create a Read Only folder while syncing across linked devices?` article, which still says linked-device sync makes all linked devices Owners and that achieving read-only there requires using a Standard-folder Read Only key instead.
- Resilio's current `Is one-way synchronization possible?` article, which still says Advanced folders do not support read-only synchronization across linked devices and that Read Only changes can stop synchronization for changed files unless overwrite-heal is enabled.
- Resilio's current `Sharing a folder locally` article, which still says local derivatives cannot receive Owner, cannot exceed source permissions, may need re-sharing to change access, auto-lower when the source seat is downgraded, and disappear when the source is removed or disconnected.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0289

- Sync functionality in detail  
  https://help.resilio.com/hc/en-us/articles/204754389-Sync-functionality-in-detail

- User Management  
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- What's the difference between Standard and Advanced folders?  
  https://help.resilio.com/hc/en-us/articles/204754679-What-s-the-difference-between-Standard-and-Advanced-folders

- Sync Share Dialog (Desktop)  
  https://help.resilio.com/hc/en-us/articles/204790709-Sync-Share-Dialog-Desktop

- How to create a Read Only folder while syncing across linked devices?  
  https://help.resilio.com/hc/en-us/articles/206216565-How-to-create-a-Read-Only-folder-while-syncing-across-linked-devices

- Is one-way synchronization possible?  
  https://help.resilio.com/hc/en-us/articles/204754279-Is-one-way-synchronization-possible

- Sharing a folder locally  
  https://help.resilio.com/hc/en-us/articles/360011582500-Sharing-a-folder-locally

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

## Revision addendum — policy provenance, sticky override, and config-plane ownership after rev0289

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about per-share Folder Preferences, Power user defaults, file-priority inheritance behavior, linked-device mode defaults, and configuration-mode ownership.
The new questions were:

> where do current official docs most clearly show that `what policy is in force right now?` is still answered across several control planes rather than one stable product-owned surface?

> where do those same current docs still show that `return to default` and `who owns this setting?` are not one stable operator grammar today because standing defaults, local overrides, linked-device defaults, and config-plane declarations can all compete?

The most load-bearing source set for this pass was:

- Resilio's current `Folder Preferences` article, which still publishes per-share controls for Archive, overwrite, relay, tracker, LAN search, predefined hosts, and file download priority.
- Resilio's current `Power user preferences` article, which still publishes standing defaults and switches such as `disable_remove_from_all_devices`, and still notes platform caveats like `Ignored in Linux WebUI`.
- Resilio's current `File download priority` article, which still says `folder_defaults.transfer_priority` can affect existing and new shares while a share whose priority was manually changed stops inheriting later global changes even if set back to `None`.
- Resilio's current `Selective Sync` article, which still says sync mode can be chosen at first connect, after connect, and when a folder is automatically added from linked devices.
- Resilio's current `Synchronization Modes` and `Sync Private Identity & Linking My Devices` articles, which still spread mode/default-path truth across linked-device defaults, current-subject modes, and future automatic arrivals.
- Resilio's current `Running Sync in configuration mode` article, which still says advanced preferences can be injected through config, that only Standard folders can be set up there, and that configured shared folders override previously added WebUI folders while disabling WebUI for that case.

## Additional Resilio official sources emphasized in rev0290

- Folder Preferences  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- File download priority  
  https://help.resilio.com/hc/en-us/articles/42328167759251-File-download-priority

- Selective Sync  
  https://help.resilio.com/hc/en-us/articles/205458095-Selective-Sync

- Synchronization Modes  
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

## Revision addendum — naming provenance, issued recipient labels, and stale alias residue after rev0290

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another small cluster of current official Resilio Sync docs about custom share names, local-only folder rename behavior, identity/device naming, and share-path/location semantics.
The new questions were:

> where do current official docs most clearly show that `what is this called?` is still answered across several separate naming planes rather than one stable product-owned surface?

> where do those same current docs still show that issuance-time recipient labels and stale post-disconnect aliases are materially different from canonical subject rename?

The most load-bearing source set for this pass was:

- Resilio's current `Setting custom name for sync shares` article, which still says Sync UI names normally mirror folder names on disk, that desktop custom names can diverge from disk names, that custom names do not propagate to linked devices, that different labels can be inserted into links or QR codes during sharing while the underlying share name stays unchanged, and that a custom name can remain in the UI after disconnect until explicit `Reset`.
- Resilio's current `Can I move or rename a syncing folder?` article, which still says renaming a syncing folder affects only the local device and does not update other devices.
- Resilio's current `Can I change the name of my Sync identity?` and `Sync Private Identity & Linking My Devices` articles, which still reinforce that seat/identity naming is a different plane again from subject naming, and that identity-name change is not a simple relabel but an unlink/new-certificate event.
- Resilio's current `Settings on mobile platforms` and `Sync interface on Android` articles, which still distinguish identity name from device name on mobile surfaces.

## Additional Resilio official sources emphasized in rev0291

- Setting custom name for sync shares  
  https://help.resilio.com/hc/en-us/articles/360011865879-Setting-custom-name-for-sync-shares

- Can I move or rename a syncing folder?  
  https://help.resilio.com/hc/en-us/articles/205450655-Can-I-move-or-rename-a-syncing-folder

- Can I change the name of my Sync identity?  
  https://help.resilio.com/hc/en-us/articles/206163443-Can-I-change-the-name-of-my-Sync-identity

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Settings on mobile platforms  
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- Sync interface on Android  
  https://help.resilio.com/hc/en-us/articles/213500383-Sync-interface-on-Android

## Revision addendum — projection rename semantics and action-verb fragmentation after rev0291

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another small cluster of current official Resilio Sync docs about desktop custom naming, filesystem rename semantics, Android share rename behavior, iOS share rename wording, and outward artifact labeling.
The new questions were:

> where do current official docs most clearly show that `rename` is still not one stable operator verb today because different projections touch different naming planes?

> where do those same current docs still show that later operators would need projection memory, not just changed text, to know what a familiar-looking rename control actually did?

The most load-bearing source set for this pass was:

- Resilio's current `Setting custom name for sync shares` article, which still says desktop custom names are applied only in Sync UI, do not rename the folder on disk, do not propagate to other peers or linked devices, and can also be changed during sharing so a different label is inserted into a link or QR while the underlying share name remains unchanged.
- Resilio's current `Can I move or rename a syncing folder?` article, which still says filesystem rename affects only the local device and that mobile platforms do not support moving sync shares.
- Resilio's current `Sync interface on Android` article, which still says the share-name pencil renames both in Sync and in the filesystem.
- Resilio's current `Sync Interface on iOS devices` article, which still says the share-name pencil lets you rename the share, while being less explicit than Android about the exact plane effect.

## Additional Resilio official sources emphasized in rev0292

- Setting custom name for sync shares  
  https://help.resilio.com/hc/en-us/articles/360011865879-Setting-custom-name-for-sync-shares

- Can I move or rename a syncing folder?  
  https://help.resilio.com/hc/en-us/articles/205450655-Can-I-move-or-rename-a-syncing-folder

- Sync interface on Android  
  https://help.resilio.com/hc/en-us/articles/213500383-Sync-interface-on-Android

- Sync Interface on iOS devices  
  https://help.resilio.com/hc/en-us/articles/212016726-Sync-Interface-on-iOS-devices

## Revision addendum — LAN-only truth, helper budgets, and exposure ceilings after rev0292

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another small cluster of current official Resilio Sync docs about share-level helper toggles, direct-vs-relay route stages, LAN-only instructions, listener/proxy behavior, bind-interface controls, and connectivity troubleshooting.
The new questions were:

> where do current official docs most clearly show that `LAN-only` is still stronger than a couple of toggles?

> where do those same current docs still show that one ordinary route answer is spread across share preferences, settings, power-user knobs, config steps, and troubleshooting pages?

The most load-bearing source set for this pass was:

- Resilio's current `Folder Preferences` article, which still exposes `Use relay server`, `Use tracker server`, `Search LAN`, and `Use predefined hosts`, and explains that predefined hosts depend on peer listening-port knowledge and can replace tracker/LAN discovery in high-security networks.
- Resilio's current `What ports and protocols are used by Sync?` article, which still describes the staged route chain of discovering tracker/relay addresses via `sync.conf`, talking to tracker, attempting direct TCP/UDP on the listening port, falling back to relay, and using broadcast/multicast on LAN.
- Resilio's current `Can I force Sync to do local network (LAN) syncing only and not sync via the Internet?` article, which still says real LAN-only requires disabling tracker and relay in both share and power-user/config settings, enabling multicast, and clearing cached global-IP memory by setting peer expiration to `0`, restarting, and restoring it.
- Resilio's current `Power user preferences` article, which still publishes route-shaping knobs such as `config_refresh_interval`, `bind_interface`, and `use_only_bind_interface`.
- Resilio's current `Sync Preferences` article, which still keeps listener port, UPnP/NAT-PMP mapping, and proxy behavior in a separate settings surface and notes that two proxied peers may end up communicating only via relay.
- Resilio's current `Peers aren't connecting` article, which still sends the operator through tracker, relay, listening-port ingress, multicast availability, proxy posture, and multiple-NIC troubleshooting.

## Additional Resilio official sources emphasized in rev0293

- Folder Preferences  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- What ports and protocols are used by Sync?  
  https://help.resilio.com/hc/en-us/articles/204754759-What-ports-and-protocols-are-used-by-Sync

- Can I force Sync to do local network (LAN) syncing only and not sync via the Internet?  
  https://help.resilio.com/hc/en-us/articles/204754349-Can-I-force-Sync-to-do-local-network-LAN-syncing-only-and-not-sync-via-the-Internet

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Peers aren't connecting  
  https://help.resilio.com/hc/en-us/articles/205450205-Peers-aren-t-connecting

- Setting network interface per share  
  https://help.resilio.com/hc/en-us/articles/360001411244-Setting-network-interface-per-share

## Revision addendum — contested repair, read-only suspension, and archive ritual after rev0295

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another small cluster of current official Resilio Sync docs about conflict-file delete risk, Read Only divergence and overwrite behavior, offline-writer precedence, manual Archive replay, and troubleshooting repair steps.
The new questions were:

> where do current official docs most clearly show that `what repair path is safe for this contested item?` is still answered across several separate behavioral families rather than one stable product-owned surface?

> where do those same current docs still show that loser fate, survivor classes, restart/runtime posture, and remote counterpart risk are all real product meaning that should be owned together?

The most load-bearing source set for this pass was:

- Resilio's current `Conflict files in Sync` article, which still warns not to just delete a `.Conflict` item because it corresponds to a real remote counterpart and still explains how these conflicts can arise from case, encoding, invalid symbols, junctions, and storage/controller problems.
- Resilio's current `User Management` article, which still says Read Only local changes do not propagate and further synchronization of the changed files is suspended for that peer.
- Resilio's current `Is one-way synchronization possible?` article, which still spells out the exact per-class outcomes when `Overwrite any changed files` is enabled on a Read Only peer.
- Resilio's current `What if several people make changes to the same file?` article, which still says a returning offline edit can outrank later online edits and that overwritten versions land in Archive.
- Resilio's current `Using Archive for file versioning and restoring deleted files` article, which still says restoring is manual, runtime must be active if replay is intended, Archive lacks per-peer authorship detail, and old versions are retained asymmetrically across peers.
- Resilio's current `My files don't sync` article, which still points operators with locally changed Read Only files to enabling overwrite and restarting Sync on that peer.

## Additional Resilio official sources emphasized in rev0296

- Conflict files in Sync  
  https://help.resilio.com/hc/en-us/articles/204753629-Conflict-files-in-Sync

- User Management  
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- Is one-way synchronization possible?  
  https://help.resilio.com/hc/en-us/articles/204754279-Is-one-way-synchronization-possible

- What if several people make changes to the same file?  
  https://help.resilio.com/hc/en-us/articles/204754209-What-if-several-people-make-changes-to-the-same-file

- Using Archive for file versioning and restoring deleted files.  
  https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files

- My files don't sync  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

## Revision addendum — shared substrate, service namespace, and lock-contention truth after rev0296

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync pages about SMB-share caveats, notification loss on shared/networked paths, locked files, power-user lock/detection posture, and Windows service namespace differences.
The new questions were:

> where do current official Resilio materials most clearly show that storage substrate, runtime identity, and writer topology materially change the sync contract?

> where do those same current docs still show that `authoritative path` and `safe write lane` remain too fragmented to clone directly?

The most load-bearing source set for this pass was:

- Resilio's current `Sync and SMB file shares`, which still says full permissions are required, only `SMB 3.0+` supports notifications, stranded locks can remain after network/app failure, and simple Samba setups can damage or roll back files when third-party apps touch the same data outside SMB.
- Resilio's current `How soon does synchronization start?`, which still says filesystem notifications can be unavailable on storages such as `NFS` and `SMB2` mounted shares, with scheduled rescans every `600` seconds as fallback.
- Resilio's current `Locked files`, which still says blocked files can be listed in UI but the locking application cannot be identified by Sync itself.
- Resilio's current `Power user preferences`, which still publishes `enable_file_system_notifications` and `recheck_locked_files_interval`.
- Resilio's current `Sync Service Troubleshooting on Windows`, which still says mapped drive letters are invisible to the service, recommends UNC-style entry instead, warns that this loses update notifications, and says switching to `Local System` changes the storage folder / state world and requires re-adding and re-sharing folders.

## Additional Resilio official sources emphasized in rev0297

- Sync and SMB file shares  
  https://help.resilio.com/hc/en-us/articles/207755736-Sync-and-SMB-file-shares

- How soon does synchronization start?  
  https://help.resilio.com/hc/en-us/articles/204754319-How-soon-does-synchronization-start

- Locked files  
  https://help.resilio.com/hc/en-us/articles/205504549-Locked-files

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Sync Service Troubleshooting on Windows  
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

## Revision addendum — stop truth, background runtime, and restart-boundary work after rev0297

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about Windows service continuity, Android's explicit `Exit`, platform-specific background execution, startup revival, mobile notification priority, and install/update stop rituals.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `closed`, `backgrounded`, `service-running`, `exit`, `start-on-boot`, and `re-opened` are materially different runtime truths?

> where do those same current docs still show that the ordinary operator answer about `did I really stop it?` depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Running Sync as a service on Windows` article, which still says Sync can run in the background regardless of logged-in user and can run as `System`, `Local Service`, or current user.
- Resilio's current `Sync interface on Android` article, which still gives `Exit` its own action and still says it `shuts Sync down correctly`.
- Resilio's current `Does Sync work in background?` article, which still says Android can work in the background unless killed, that iOS background synchronization is unavailable, and that shutdown and re-open re-index folders and can alter overwrite chronology after offline edits.
- Resilio's current `Settings on mobile platforms` article, which still says disabling Android notifications lowers Sync priority and may force background work to stop.
- Resilio's current `Sync Preferences` article, which still exposes `Start Sync on startup` on desktop.
- Resilio's current `Updating Sync to latest version` article, together with adjacent install/update materials, which still distinguishes app, service, and process stop posture according to install mode.

## Additional Resilio official sources emphasized in rev0298

- Running Sync as a service on Windows  
  https://help.resilio.com/hc/en-us/articles/207701296-Running-Sync-as-a-service-on-Windows

- Sync interface on Android  
  https://help.resilio.com/hc/en-us/articles/213500383-Sync-interface-on-Android

- Does Sync work in background?  
  https://help.resilio.com/hc/en-us/articles/206816823-Does-Sync-work-in-background

- Settings on mobile platforms  
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Updating Sync to latest version  
  https://help.resilio.com/hc/en-us/articles/115001130830-Updating-Sync-to-latest-version

## Revision addendum — identity-link, certificate-takeover, and latent-device work after rev0299

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about digital certificates, linked-device identity, M-key directionality, mixed-version linking risk, certificate takeover when linking already-running seats, Advanced-folder eviction, iOS filesystem deletion risk, local-only unlink, hidden offline-device residue, and the architecture split between Standard and Advanced folders.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `link device` is really a seat-adoption operation with certificate and folder consequences?

> where do those same current docs still show that the ordinary operator answer about `what exactly happens if I link or hide/unlink this seat?` depends on several pages instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says each installation gets a digital certificate, warns against linking v2 and v3 devices under one identity, says the direction of the `M` key matters because the adopting seat takes the source seat's identity name, fingerprint, and configured shares, warns that linking two already-running seats can replace one certificate and remove Advanced folders from the app, notes the stronger iOS filesystem deletion risk, and states that unlink is local-only because other devices cannot be remotely unlinked.
- Resilio's current `How to clear offline devices?` article, which still says clearing only hides an offline linked device rather than unlinking it and that the device reappears if it comes back online.
- Resilio's current `What's the difference between Standard and Advanced folders?` article, which still says linked-device identity and certificate-aware peer grouping belong to the Advanced/PKI model rather than generic key-only sharing.

## Additional Resilio official sources emphasized in rev0300

- Sync Private Identity & Linking My Devices
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- How to clear offline devices? (desktop only)
  https://help.resilio.com/hc/en-us/articles/204762439-How-to-clear-offline-devices-desktop-only

- What's the difference between Standard and Advanced folders?
  https://help.resilio.com/hc/en-us/articles/204754679-What-s-the-difference-between-Standard-and-Advanced-folders

## Revision addendum — birth-time commitments, create-time freezes, and recreate-boundary work after rev0301

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio docs about Standard-versus-Advanced conversion cliffs, Standard-folder permission-mutation limits, create-time-fixed permission-sync modes, cache-server path freezes, mount-point remount/index consequences, and successor-style job migration.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that some important settings are really birth-time commitments rather than ordinary live edits?

> where do those same current docs still show that the ordinary operator answer about `can I change this later or not?` depends on several pages instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `What's the difference between Standard and Advanced folders?` article, which still says Standard folders cannot be converted into Advanced folders in place and that on-the-fly permission changes are unavailable for Standard folders, requiring remove/re-add with a new key.
- Resilio's current `Profiles` and `Syncing file system permissions` docs, which still say permission-sync settings for Synchronization, Hybrid Work, and File Caching jobs are applied when the job is created and cannot be changed later.
- Resilio's current `Configuring Linux OS cache servers` guide, which still says the selected access and cache paths cannot be changed later after the job is saved, that the exposed path must exist and be empty, and that changing mount point later retriggers initial indexing while reusing cached bytes as a pre-seeded scenario.
- Resilio's current `Migrate Sync jobs to File cache or Hybrid work jobs` guide, which still publishes a real successor / migration workflow rather than pretending the change is just an in-place edit.

## Additional Resilio official sources emphasized in rev0302

- What's the difference between Standard and Advanced folders?
  https://help.resilio.com/hc/en-us/articles/204754679-What-s-the-difference-between-Standard-and-Advanced-folders

- Profiles
  https://www.resilio.com/documentation/content/advanced-configuration/profiles-and-configuration-parameters/profiles/

- Syncing file system permissions
  https://www.resilio.com/documentation/content/advanced-configuration/agents/syncing_file_system_permissions/

- Configuring Linux OS cache servers
  https://www.resilio.com/documentation/content/agents/configuring_linux_os_cache_servers/

- Migrate Sync jobs to File cache or Hybrid work jobs
  https://www.resilio.com/documentation/content/jobs/migrate_sync_jobs_to_file_cache_or_hybrid_work_jobs/

## Revision addendum — disclosure ceilings, link-fragment locality, and telemetry defaults after rev0303

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about security/privacy claims, link fragment locality, landing-page preview behavior, relay blindness, tracker/config discovery, and default telemetry export.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that peers, browser/service infrastructure, trackers, relays, and telemetry recipients are different observer classes?

> where do those same current docs still show that the ordinary operator answer about `who learned what from this action?` depends on several pages instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Can others see my files? How secure is sharing by Resilio Sync?` article, which still says direct peer transfer, AES-128 in-transit encryption, X.509 authentication, and usage statistics sent in the clear.
- Resilio's current `Can Resilio team see and block/remove any Sync folders?` article, which still says Resilio neither hosts nor caches content, that link-specific information after `#` is not sent from the browser to the server, and that relay cannot examine encrypted payload.
- Resilio's current `Link structure and flow` article, which still says the landing page can show folder name and size, that the server swaps `https://` to `btsync://`, and that fragment parameters carry folder name, size, folder ID, temporary key, expiration, and client version while remaining outside the server-requested URL.
- Resilio's current `What ports and protocols are used by Sync?` article, which still says Sync downloads `sync.conf`, communicates public/local IP addresses and share-list participation to tracker infrastructure, and learns peer addresses from that discovery route.
- Resilio's current `What is a Relay Server?` article, which still says relay carries files only as unreadable encrypted traffic and does not store them.
- Resilio's current `Power user preferences` article, which still says `send_statistics` defaults to `true` and exports anonymous runtime posture metrics such as OS, version, and active state.

## Additional Resilio official sources emphasized in rev0304

- Can others see my files? How secure is sharing by Resilio Sync?
  https://help.resilio.com/hc/en-us/articles/205451025-Can-others-see-my-files-How-secure-is-sharing-by-Resilio-Sync

- Can Resilio team see and block/remove any Sync folders?
  https://help.resilio.com/hc/en-us/articles/205451105-Can-Resilio-team-see-and-block-remove-any-Sync-folders

- Link structure and flow
  https://help.resilio.com/hc/en-us/articles/204754739-Link-structure-and-flow

- What ports and protocols are used by Sync?
  https://help.resilio.com/hc/en-us/articles/204754759-What-ports-and-protocols-are-used-by-Sync

- What is a Relay Server?
  https://help.resilio.com/hc/en-us/articles/204754779-What-is-a-Relay-Server

- Power user preferences
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

## Revision addendum — event evidence retention, history windows, and audit ceilings after rev0305

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about History retention, Archive attribution limits, notification posture, transfer-history persistence, and convenience timestamp lineage.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that event evidence comes in different families with different retention and proof ceilings?

> where do those same current docs still show that the ordinary operator answer about `what proof survives, what does it still prove, and for how long?` depends on several pages instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Sync Main View (Desktop)` article, which still says History shows general syncing activity for the last 30 days.
- Resilio's current `Using Archive for file versioning and restoring deleted files.` article, which still says Archive does not itself provide peer-change attribution, points the operator to History for that, and publishes different default archive retention on desktops versus mobiles.
- Resilio's current `Sync Preferences` article, which still exposes `Show notifications` as a configurable signal surface.
- Resilio's current `Sharing files (iOS)` article, which still says transfer history can remain visible after the downloaded file is removed from the device.
- Resilio's older-but-still-relevant `Resilio Sync change log`, which still documents `Date synced`, `Last transferred`, and synchronized notifications as useful observability features without turning them into a unified evidence contract.

## Additional Resilio official sources emphasized in rev0306

- Sync Main View (Desktop)
  https://help.resilio.com/hc/en-us/articles/204755009-Sync-Main-View-Desktop

- Using Archive for file versioning and restoring deleted files.
  https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files

- Sync Preferences
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Sharing files (iOS)
  https://help.resilio.com/hc/en-us/articles/115001717390-Sharing-files-iOS

- Resilio Sync change log
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log

## Revision addendum — time authority, timestamp provenance, and replay chronology after rev0306

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about time-difference handling, peer clock and timezone dependence, skew-budget settings, database-only `mtime` fallback, and archive replay behavior.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that chronology depends on real clock trust and real `mtime` authority?

> where do those same current docs still show that the ordinary operator answer about `which timestamp actually governs ordering, replay, and visible truth?` depends on several pages instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `"Time difference" error` article, which still says Sync decides which file is newer by comparing files' modification time after converting to GMT, and that wrong time or timezone beyond the allowed threshold produces warnings and empty file lists on mobile.
- Resilio's current `Power user preferences` article, which still says `sync_max_time_diff` defaults to 600 seconds and that `ignore_mtime_assign_errors` can preserve the correct `mtime` only in the database while disk `mtime` becomes current timestamp.
- Resilio's current `Using Archive for file versioning and restoring deleted files.` article, which still says restored files carry older modified time than other peers and can be moved back to Archive if Sync is not running during restore.
- Resilio's current `Comprehensive guide to syncing (Desktop-Desktop)` article, which still says Sync relies on each device's internal clock and that wrong time or timezone causes `Excessive time difference` behavior.
- Resilio's current `Syncing between a desktop computer and a mobile device` article, which still repeats the same internal-clock dependency for cross-device flows.

## Additional Resilio official sources emphasized in rev0307

- "Time difference" error
  https://help.resilio.com/hc/en-us/articles/204753599--Time-difference-error

- Power user preferences
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Using Archive for file versioning and restoring deleted files.
  https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files

- Comprehensive guide to syncing (Desktop-Desktop)
  https://help.resilio.com/hc/en-us/articles/204754939-Comprehensive-guide-to-syncing-Desktop-Desktop

- Syncing between a desktop computer and a mobile device
  https://help.resilio.com/hc/en-us/articles/205451165-Syncing-between-a-desktop-computer-and-a-mobile-device

## Revision addendum — hidden control substrate, service capsule integrity, and sidecar governance after rev0307

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about hidden `.sync` state, service-file suspension, same-folder dual-instance corruption, IgnoreList behavior, StreamsList metadata propagation, and temporary transfer artifacts.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that a synced folder contains multiple classes of hidden control substrate rather than only user bytes?

> where do those same current docs still show that the ordinary operator answer about `what hidden thing is safe to edit, dangerous to delete, or unsafe to double-own?` depends on several pages instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `What is '.sync' folder, and StreamsList, IgnoreList and Archive inside?` article, which still says every shared folder gets a hidden `.sync` system folder, that it is critical, must not be moved separately, and that the namespace also contains ID, IgnoreList, StreamsList, and `.!sync` transfer files.
- Resilio's current `Service files missing / Cannot identify destination folder` article, which still says deleting or corrupting `.sync` suspends synchronization and that adding one folder to two Sync instances can corrupt internal files and make further sync impossible.
- Resilio's current `Ignoring files in Sync (Ignore List)` article, which still says IgnoreList is an editable UTF-8 sidecar inside `.sync`, affects indexing and size accounting, is not fully retroactive to already-synced structure, and is reread on change or rescan.
- Resilio's current `Alt Streams and Xattrs in Sync` article, which still says StreamsList is an editable text whitelist and that `.sync/Streams` can hold xattr stub files when some peers cannot store metadata natively.

## Additional Resilio official sources emphasized in rev0308

- What is '.sync' folder, and StreamsList, IgnoreList and Archive inside?
  https://help.resilio.com/hc/en-us/articles/206217185-What-is-sync-folder-and-StreamsList-IgnoreList-and-Archive-inside

- Service files missing / Cannot identify destination folder
  https://help.resilio.com/hc/en-us/articles/205450225-Service-files-missing-Cannot-identify-destination-folder

- Ignoring files in Sync (Ignore List)
  https://help.resilio.com/hc/en-us/articles/205458165-Ignoring-files-in-Sync-Ignore-List

- Alt Streams and Xattrs in Sync
  https://help.resilio.com/hc/en-us/articles/204754729-Alt-Streams-and-Xattrs-in-Sync

## Revision addendum — mutation durability, config-plane replay, and storage-world truth after rev0309

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about save cadence, NAS sleep tuning, configuration mode, WebUI authority split, storage-home location, and service-user world changes.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that live runtime state, persisted storage state, and next-boot authoritative state are materially different?

> where do those same current docs still show that the ordinary operator answer about `did my change really stick, and in what world?` depends on several pages instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Power user preferences` article, which still says `config_save_interval` defaults to `600` seconds and controls how often settings are saved to storage.
- Resilio's current `Sync prevents HDD from sleeping on NAS...` article, which still recommends widening `config_save_interval` — for example to `18000` seconds — together with refresh/rescan cadence.
- Resilio's current `Running Sync in configuration mode` article, which still says config-defined shared folders disable WebUI and override folders previously added from WebUI.
- Resilio's current `Configuring WebUI` article, which still splits listener authority between configuration mode and ordinary interactive settings.
- Resilio's current `Guide to Linux, and Sync peculiarities` article, which still says the storage directory keeps settings, identity, and applied license.
- Resilio's current `Sync Service Troubleshooting on Windows` article, which still says a service-user change can create a different storage folder world where prior folders must be re-added/re-shared.

## Additional Resilio official sources emphasized in rev0310

- Power user preferences
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Sync prevents HDD from sleeping on NAS...
  https://help.resilio.com/hc/en-us/articles/205449995-Sync-prevents-HDD-from-sleeping-on-NAS

- Running Sync in configuration mode
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Configuring WebUI
  https://help.resilio.com/hc/en-us/articles/115001184490-Configuring-WebUI

- Guide to Linux, and Sync peculiarities
  https://help.resilio.com/hc/en-us/articles/204762449-Guide-to-Linux-and-Sync-peculiarities

- Sync Service Troubleshooting on Windows
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

## Revision addendum — path identity, canonicalization, and equivalence-class truth after rev0310

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about Unicode normalization, filename conflict causes, UTF-8 and path portability, invalid path-name edge cases, and bugfix history proving that these classes are operationally real.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that path identity is not simply `whatever the local filesystem accepted`?

> where do those same current docs still show that the ordinary operator answer about `same name, different raw form, collision, rewrite, or reject?` depends on several pages instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Power user preferences` article, which still exposes `normalize_unicode_paths = true` and describes it as normalizing Unicode names into composed/decomposed form.
- Resilio's current `Conflict files in Sync` article, which still says conflicts can arise from case-insensitive peers, decomposed UTF symbols, prohibited symbols, and linked junctions, and still says operators should keep the same letter case and encoding across devices.
- Resilio's current `My files don't sync` article, which still says Sync expects UTF-8 naming, still flags special-symbol/encoding trouble, and still warns about path-length limits.
- Resilio's current `Unsupported asterisk (*) characters at the end of file/folder names` article, which still says some invalid trailing-asterisk names may be interpreted as system data and disrupt syncing.
- Resilio's current changelog, which still records fixes for crashes caused by mixed composed/decomposed symbols in filenames, invalid symbols in Windows paths, and trailing-dot syncing to Windows peers.

## Additional Resilio official sources emphasized in rev0311

- Power user preferences
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Conflict files in Sync
  https://help.resilio.com/hc/en-us/articles/204753629-Conflict-files-in-Sync

- My files don't sync
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Unsupported asterisk (*) characters at the end of file/folder names
  https://help.resilio.com/hc/en-us/articles/206214715-Unsupported-asterisk-characters-at-the-end-of-file-folder-names

- Resilio Sync change log
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log

## Revision addendum — special-object fidelity, symbolic-link boundary, and bundle-collapse truth after rev0315

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about symbolic-link support asymmetry, power-user symlink/xattr toggles, StreamsList-based metadata preservation, compatibility stub behavior, and troubleshooting notes about bundle collapse when xattr syncing is disabled.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that an object can be a preserved reference, an unsupported link class, a metadata-bearing bundle, or a degraded plain directory depending on platform and settings?

> where do those same current docs still show that the ordinary operator answer about `what is this object really, and what fidelity survives?` depends on several pages instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Soft links, hard links and symbolic links` article, which still says Windows does not support these link classes in Sync while Unix can synchronize a symbolic link object without synchronizing the referenced target.
- Resilio's current `Alt Streams and Xattrs in Sync` article, which still says xattrs are synchronized only according to hidden `.sync/StreamsList` and that peers unable to store them natively may create stub data in `.sync/Streams`.
- Resilio's current `Power user preferences` article, which still exposes `ignore_symlinks` and `sync_extended_attributes` as current operator-tunable settings.
- Resilio's current `My files don't sync` article, which still says disabling xattr syncing can make file bundles such as Pages, Keynote, and macOS apps sync as ordinary subdirectories.

## Additional Resilio official sources emphasized in rev0316

- Soft links, hard links and symbolic links
  https://help.resilio.com/hc/en-us/articles/205504529-Soft-links-hard-links-and-symbolic-links

- Alt Streams and Xattrs in Sync
  https://help.resilio.com/hc/en-us/articles/204754729-Alt-Streams-and-Xattrs-in-Sync

- Power user preferences
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- My files don't sync
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

## Revision addendum — service promotion, principal switch, and service-world continuity after rev0316

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about service install branching, service-user identity, mapped-drive loss, UNC fallback, service-storage authority, loopback-vs-LAN WebUI scope, and uninstall-visible service storage roots.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `run as service` is not one flat backgrounding verb but a continuity-bearing cutover?

> where do those same current docs still show that the ordinary operator answer about `did I keep the same seat or start a different service world?` depends on several pages instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Running Sync as a service on Windows` article, which still says service install can either migrate the existing Sync shares or perform a clean installation, and still says the service can run as current user, Local Service, or Local System.
- Resilio's current `Sync Service Troubleshooting on Windows` article, which still says mapped drive letters are unavailable to services because interactive logon did not occur, still says the UNC workaround loses immediate notifications and falls back to rescan or restart, and still says switching to Local System opens a different service storage world with no old shares visible until re-add / re-share / reconnect.
- Resilio's current `Running Sync in configuration mode` article, which still says service config mode works only by putting `sync.conf` in the service storage folder.
- Resilio's current `Sync Preferences` article together with the same troubleshooting article, which still preserve the split between listener/posture settings and service restart / audience truth.
- Resilio's current `How to uninstall Sync?` article, which still publishes distinct service storage roots for local-user, LocalService, and LocalSystem service seats.

## Additional Resilio official sources emphasized in rev0317

- Running Sync as a service on Windows
  https://help.resilio.com/hc/en-us/articles/207701296-Running-Sync-as-a-service-on-Windows

- Sync Service Troubleshooting on Windows
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

- Running Sync in configuration mode
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Sync Preferences
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- How to uninstall Sync?
  https://help.resilio.com/hc/en-us/articles/204775029-How-to-uninstall-Sync

## Revision addendum — ingress mutation, port lease, and router-side-effect truth after rev0321

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about listening-port semantics, manual forwarding dependence, automatic UPnP/NAT-PMP router requests, router-side fragility, direct-vs-relay connectivity, and slow-speed repair advice.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `better direct connectivity` can also mean off-host router mutation and a widened candidate inbound audience?

> where do those same current docs still show that the ordinary operator answer about `local listener change, mapping attempt, visible lease, outside reachability, or actual direct proof?` depends on several pages instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Sync Preferences` article, which still says the listening port covers incoming TCP plus incoming/outgoing UDP, still says it is random on installation unless changed, still says manual NAT forwarding must target that port, and still says `Use UPnP port mapping` sends UPnP and NAT-PMP packets to the router while warning that some printers, scanners, and other equipment may mishandle UPnP.
- Resilio's current `Running Sync in configuration mode` article, which still exposes the same automatic mapping choice and still says listening port `0` allocates a random port.
- Resilio's current `What ports and protocols are used by Sync?` article, which still distinguishes tracker traffic, direct peer traffic, relay fallback, LAN discovery, and automatic port-mapping traffic.
- Resilio's current `Peers aren't connecting` article, which still says opening the listening port in routers and firewalls can matter for direct connection and that relay remains relevant when direct connection is not possible.
- Resilio's current `Download/upload speed is very slow` article, which still repeats the importance of UPnP/manual port-forward posture for directness and speed.

## Additional Resilio official sources emphasized in rev0322

- Sync Preferences
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Running Sync in configuration mode
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- What ports and protocols are used by Sync?
  https://help.resilio.com/hc/en-us/articles/204754759-What-ports-and-protocols-are-used-by-Sync

- Peers aren't connecting
  https://help.resilio.com/hc/en-us/articles/205450205-Peers-aren-t-connecting

- Download/upload speed is very slow
  https://help.resilio.com/hc/en-us/articles/205450195-Download-upload-speed-is-very-slow

- Resilio Sync change log
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log

## Additional Resilio official sources emphasized in rev0323

- Windows Defender SmartScreen blocks Resilio Sync installer
  https://help.resilio.com/hc/en-us/articles/360014486120-Windows-Defender-SmartScreen-blocks-Resilio-Sync-installer

- How to Silently Install Resilio Sync
  https://help.resilio.com/hc/en-us/articles/205505969-How-to-Silently-Install-Resilio-Sync

- No Sync icons in the file browser/no Sync-related items in the context menu on Mac/Windows
  https://help.resilio.com/hc/en-us/articles/206214625-No-Sync-icons-in-the-file-browser-no-Sync-related-items-in-the-context-menu-on-Mac-Windows

- How to uninstall Sync?
  https://help.resilio.com/hc/en-us/articles/204775029-How-to-uninstall-Sync

## Revision addendum — self-edge derivation, source-coupled lifecycle, and entitlement cliffs after rev0324

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about same-computer local sharing, self-only peer posture, no tracker/relay/LAN discovery for that derivative lane, loop bans, inherited-rights ceilings, source-coupled removal and manual reattach, placeholder-limited byte promises, and license-sensitive continuity.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `sync local folders` is not ordinary sharing but a self-edge topology with its own rights and lifecycle ceiling?

> where do those same current docs still show that the ordinary operator answer about `what exactly did I create, what tears it down, and why did it stop?` is still too convenience-shaped to clone directly?

The most load-bearing source set for this pass was:

- Resilio's current `Sharing a folder locally` article, which still says the feature is desktop-only and Pro-only, still says the derivative is connected to exactly one peer `self`, still removes tracker/relay/LAN discovery from the derivative preferences, still bans parent/subdirectory loop shapes, still caps derivative rights below the source and forbids `Owner`, still says Advanced-share rights changes may require remove-and-re-share, still says source-right downgrades flow down, still says source disconnect/removal removes the derivative and source return does not automatically restore it, still says derivative Selective Sync may diverge while byte availability remains source-limited, and still says expiry or license removal stops the derivative.
- Resilio's current `Resilio Sync change log`, which still preserves local same-computer syncing as its own feature introduction rather than a mere restatement of ordinary sharing.

## Additional Resilio official sources emphasized in rev0325

- Sharing a folder locally
  https://help.resilio.com/hc/en-us/articles/360011582500-Sharing-a-folder-locally

- Resilio Sync change log
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log


## Revision addendum — stop proof, hidden runtime, and restart provenance after rev0325

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about service/background runtime classes, Android explicit exit, iOS foreground-only limits, notification-linked Android background priority, startup re-entry, update/relaunch distinctions, and restart-caused chronology risk.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `close`, `exit`, `stop service`, and `will start again later` are not the same operational truth?

> where do those same current docs still show that the ordinary operator answer about `did I really stop it, what can still continue, and what brought it back?` is still too fragmented to clone directly?

The most load-bearing source set for this pass was:

- Resilio's current `Running Sync as a service on Windows` article, which still says service mode runs regardless of logged-in user and can run as `System`, `Local Service`, or current user.
- Resilio's current `Does Sync work in background?` article, which still says desktop can keep running when UI is hidden, Android can work in the background unless killed, iOS background sync is unavailable, and shutdown/re-open causes folder re-indexing and can alter overwrite chronology after offline edits.
- Resilio's current `Sync interface on Android` article, which still says `Exit` `shuts Sync down correctly`.
- Resilio's current `Settings on mobile platforms` article, which still says disabling Android notifications lowers Sync priority and may force background work to stop.
- Resilio's current `Sync Preferences` article, which still exposes `Start Sync on startup` for Mac and Windows as a future boot re-entry setting.
- Resilio's current `Updating installation to Resilio Sync v3` article, which still distinguishes process stop / service stop by installation mode and still says Linux relaunch should use the same command line parameters and same user to preserve continuity.

## Additional Resilio official sources emphasized in rev0326

- Running Sync as a service on Windows
  https://help.resilio.com/hc/en-us/articles/207701296-Running-Sync-as-a-service-on-Windows

- Does Sync work in background?
  https://help.resilio.com/hc/en-us/articles/206816823-Does-Sync-work-in-background

- Sync interface on Android
  https://help.resilio.com/hc/en-us/articles/213500383-Sync-interface-on-Android

- Settings on mobile platforms
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- Sync Preferences
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Updating installation to Resilio Sync v3
  https://help.resilio.com/hc/en-us/articles/31194252837779-Updating-installation-to-Resilio-Sync-v3

- Resilio Sync change log
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log


## Revision addendum — path liveness, remount witness, and rebind ceiling after rev0329

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about missing-path warnings, same-drive move tracking, reconnect path drift, removable-root ambiguity, and same-computer external targeting.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `path missing`, `moved`, `remounted`, `reconnect to old directory`, and `use this external drive` are not the same continuity truth?

> where do those same current docs still show that the ordinary operator answer about `did this subject move, disappear, return, or become a new bind?` still depends on several pages instead of one stable product-owned family?

The most load-bearing source set for this pass was:

- Resilio's current `Folder not found / Can't open the destination folder` article, which still says the warning can mean deletion or moving the folder to another HDD / logical partition, and still distinguishes restore-from-trash, point-to-correct-location, and remove-and-add-again as materially different remedies.
- Resilio's current `Can I move or rename a syncing folder?` article, which still says rename is local-only, still limits Windows/macOS move tracking to the same logical drive, still limits Linux to moves inside the sync parent folder, and still says mobile platforms do not support moving sync shares.
- Resilio's current `Disconnecting and Removing Folders` article, which still says reconnect may propose a default path different from the original, may create a same-name `(1)` sibling, and still requires manual path correction plus `Destination folder is not empty. Add anyway?` if the operator wants the old directory back.
- Resilio's current `Can I use Resilio Sync to backup from an internal drive to an externally connected USB drive?` article, which still routes same-computer internal→external work through local sharing rather than ordinary two-seat repair.
- Resilio's current `My files don't sync` article, which still separately reminds the operator to verify that all drives are mounted properly when filesystem reachability is in doubt.

## Additional Resilio official sources emphasized in rev0330

- Folder not found / Can't open the destination folder  
  https://help.resilio.com/hc/en-us/articles/205450255-Folder-not-found-Can-t-open-the-destination-folder

- Can I move or rename a syncing folder?  
  https://help.resilio.com/hc/en-us/articles/205450655-Can-I-move-or-rename-a-syncing-folder

- Disconnecting and Removing Folders  
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- Can I use Resilio Sync to backup from an internal drive to an externally connected USB drive?  
  https://help.resilio.com/hc/en-us/articles/205506299-Can-I-use-Resilio-Sync-to-backup-from-an-internal-drive-to-an-externally-connected-USB-drive

- My files don't sync  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync


## Revision addendum — non-authority convergence, empty-target purge, and forced source-heal after rev0330

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about read-only divergence, destructive overwrite posture, encrypted-seat hardwire, and empty-target unknown-file deletion.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that ordinary RO, overwrite-heal RO, encrypted RO, and purge-capable RO are not the same convergence truth?

> where do those same current docs still show that the ordinary operator answer about `what happens to my local divergence here?` still depends on several pages instead of one stable product-owned family?

The most load-bearing source set for this pass was:

- Resilio's current `Folder Types and Management` article, which still says Read Only seats cannot send additions / deletions / edits and may stop receiving updates to locally changed files.
- Resilio's current `Sync Share Dialog (Desktop)` article, which still says Read Only peers can make changes locally but none of those changes sync outward.
- Resilio's current `Folder Preferences` article, which still says `Overwrite any changed files` is potentially destructive and is disabled for Read-only folders with Selective Sync ON.
- Resilio's current `Encrypted folders` article, which still says encrypted peers are Read Only, always have overwrite-heal active, do not support Selective Sync, and should not use a non-empty target because preexisting files are ignored while same-key encrypted files may be re-synced and archived.
- Resilio's current `Power user preferences` article, which still publishes `overwrite_changes`, `folder_defaults.delete_unknown_files`, and `sync_ro_delete_unknown_file`, including the warning that the last one works for an empty RO target and is not optimized for pre-seeded folders.

## Additional Resilio official sources emphasized in rev0331

- Folder Types and Management  
  https://help.resilio.com/hc/en-us/articles/204762459-Folder-Types-and-Management

- Sync Share Dialog (Desktop)  
  https://help.resilio.com/hc/en-us/articles/204790709-Sync-Share-Dialog-Desktop

- Folder Preferences  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- Encrypted folders  
  https://help.resilio.com/hc/en-us/articles/207370466-Encrypted-folders

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

## Revision addendum — identity graph adoption, certificate takeover, and containment reset after rev0332

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about identity linking, certificate takeover, linked-device arrival defaults, containment reset, and identity-coupled licensing.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `link device` is a graph-level action with direction, certificate takeover, default arrival posture, and containment blast radius?

> where do those same current docs still show that the ordinary operator answer about `what survives if I link this seat into that identity now, and what is the honest recovery move if trust fails?` still depends on several pages instead of one stable product-owned family?

The most load-bearing source set for this pass was:

- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says each installation has its own certificate/fingerprint, linking is directional, one side can take over the other's identity and shares, all linked devices see all folders, unlink is local-only, and hiding an offline device is not unlinking.
- Resilio's current `Synchronization Modes` article, which still says linked-device arrivals default into `Disconnected`, `Selective Sync`, or `Synced`, while the source side begins from the effective full-data / owner lane.
- Resilio's current `How to manually set the location of the folders synced across linked devices?` article, which still says `Disconnected` is the branch for manual target-path authorship.
- Resilio's current `How to create a Read Only folder while syncing across linked devices?` article, which still says linked-device arrivals default to Owner and that a true RO outcome requires leaving that lane and manually using a Standard-folder RO key.
- Resilio's current `Can I change the name of my Sync identity?` article, which still says name change requires unlinking and generating a new certificate.
- Resilio's current `If your device is stolen` article, which still says honest containment for a compromised linked seat can require unlink, storage cleanup, reinstall, new identity, relink, and reshare.
- Resilio's current `How to apply license key and share license seats` article, which still says Business license ownership belongs to one identity and can be stolen by directly applying the license to another identity.
- Resilio's current `How to clear offline devices? (desktop only)` article, which still says hiding an offline device only removes clutter and the device can reappear later without having been unlinked.

## Additional Resilio official sources emphasized in rev0333

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Synchronization Modes  
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- How to manually set the location of the folders synced across linked devices?  
  https://help.resilio.com/hc/en-us/articles/206216615-How-to-manually-set-the-location-of-the-folders-synced-across-linked-devices

- How to create a Read Only folder while syncing across linked devices?  
  https://help.resilio.com/hc/en-us/articles/206216565-How-to-create-a-Read-Only-folder-while-syncing-across-linked-devices

- Can I change the name of my Sync identity?  
  https://help.resilio.com/hc/en-us/articles/206163443-Can-I-change-the-name-of-my-Sync-identity

- If your device is stolen  
  https://help.resilio.com/hc/en-us/articles/204644049-If-your-device-is-stolen

- How to apply license key and share license seats  
  https://help.resilio.com/hc/en-us/articles/204762369-How-to-apply-license-key-and-share-license-seats

- How to clear offline devices? (desktop only)  
  https://help.resilio.com/hc/en-us/articles/204762439-How-to-clear-offline-devices-desktop-only


## Revision addendum — entitlement topology, owner transfer, and line-split migration after rev0333

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about commercial seat topology, owner transfer, borrower dependence, and v2/v3 line-family compatibility.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `owner identity`, `borrowed seat`, `linked seat collapse`, `owner-steal by direct apply`, and `v2/v3 linked-cohort conflict` are not the same truth?

> where do those same current docs still show that the ordinary operator answer about `who really owns this entitlement graph, who is only borrowing from it, and can this cohort cross the line split safely?` still depends on several pages instead of one stable product-owned family?

The most load-bearing source set for this pass was:

- Resilio's current `Sync Business licensing and managing license seats in Resilio Sync v2` article, which still says one seat maps to one unique identity, linked devices under one identity collapse into one counted seat, there can be only one License Owner, and applying the key on another identity makes that identity the new owner.
- Resilio's current `How to apply license key and share license seats` article, which still says linked devices under the owner inherit Pro automatically, non-linked identities borrow seats only through owner approval, reclaim remains owner-controlled, and removing the Business license from the owner does not remove it from License Users.
- Resilio's current `What happens when Sync Business trial or license expires?` article, which still says borrowed seats expire with the owner.
- Resilio's current `Sync Private Identity & Linking My Devices` article, which still warns that linked mixed-version v2/v3 devices may conflict on the applied license and can lose access to UI and share configuration.
- Resilio's current `FAQ Resilio Sync 3.0.0`, `Licensing in Resilio Sync 3.0`, `Important before updating to Resilio Sync 3.0.0`, and `Updating installation to Resilio Sync v3` articles, which still say Business cannot go to v3, linked devices should all move together to avoid license conflicts, and unsupported Business upgrades can lose configured shares while leaving files intact on disk.

## Additional Resilio official sources emphasized in rev0334

- Sync Business licensing and managing license seats in Resilio Sync v2  
  https://help.resilio.com/hc/en-us/articles/360013238759-Sync-Business-licensing-and-managing-license-seats-in-Resilio-Sync-v2

- How to apply license key and share license seats  
  https://help.resilio.com/hc/en-us/articles/204762369-How-to-apply-license-key-and-share-license-seats

- What happens when Sync Business trial or license expires?  
  https://help.resilio.com/hc/en-us/articles/206216825-What-happens-when-Sync-Business-trial-or-license-expires

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- FAQ Resilio Sync 3.0.0  
  https://help.resilio.com/hc/en-us/articles/32109883606035-FAQ-Resilio-Sync-3-0-0

- Licensing in Resilio Sync 3.0  
  https://help.resilio.com/hc/en-us/articles/31116248751123-Licensing-in-Resilio-Sync-3-0

- Important before updating to Resilio Sync 3.0.0  
  https://help.resilio.com/hc/en-us/articles/31193941051795-Important-before-updating-to-Resilio-Sync-3-0-0

- Updating installation to Resilio Sync v3  
  https://help.resilio.com/hc/en-us/articles/31194252837779-Updating-installation-to-Resilio-Sync-v3

## Additional Resilio official sources emphasized in rev0335

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about subject architecture families, governance primitives, delegation lanes, linked-device exceptions, and family-conversion ceilings.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `Standard`, `Advanced`, linked owner-default arrival, and encrypted derivative subjects are not one architecture?

> where do those same current docs still show that the ordinary operator answer about `what governance family am I choosing here, who can later re-share it, and can I migrate without teardown?` still depends on several pages instead of one stable product-owned family?

The most load-bearing source set for this pass was:

- Resilio's current `What's the difference between Standard and Advanced folders?` article, which still says Standard uses keys while Advanced uses certificates, only Advanced has Owner and on-the-fly permission changes, Standard peer lists do not understand one linked user as one certificate-bearing person, only Owners can share Advanced folders, and Standard cannot be converted in place to Advanced.
- Resilio's current `Key structure and flow` article, which still says only Standard folders use keys and still exposes separate RW, RO, encrypted-capable, encrypted-readback, encrypted-only, and identity-linking key classes.
- Resilio's current `Sync Share Dialog (Desktop)` and `User Management` articles, which still say Standard has no Owner level, Standard peers can re-share onward with the key class they hold, only Owners can share Advanced folders, and linked devices under one identity all act as Owners.
- Resilio's current `How to create a Read Only folder while syncing across linked devices?` and `Is one-way synchronization possible?` articles, which still say a real RO linked-device result requires leaving the linked lane and creating a manual Standard-folder RO-key exception.
- Resilio's current `Encrypted folders` article, which still says encrypted nodes are a separate derivative lane with manual encrypted-key attach, no decryption, no Selective Sync, and hardwired read-only / overwrite-heal behavior.
- Resilio's current `Running Sync in configuration mode` article, which still says config mode can author Standard folders only, not Advanced.

- What's the difference between Standard and Advanced folders?  
  https://help.resilio.com/hc/en-us/articles/204754679-What-s-the-difference-between-Standard-and-Advanced-folders

- Key structure and flow  
  https://help.resilio.com/hc/en-us/articles/206767810-Key-structure-and-flow

- Sync Share Dialog (Desktop)  
  https://help.resilio.com/hc/en-us/articles/204790709-Sync-Share-Dialog-Desktop

- User Management  
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- How to create a Read Only folder while syncing across linked devices?  
  https://help.resilio.com/hc/en-us/articles/206216565-How-to-create-a-Read-Only-folder-while-syncing-across-linked-devices

- Is one-way synchronization possible?  
  https://help.resilio.com/hc/en-us/articles/204754279-Is-one-way-synchronization-possible

- Encrypted folders  
  https://help.resilio.com/hc/en-us/articles/207370466-Encrypted-folders

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

## Additional Resilio official sources emphasized in rev0338

This revision leaned on another current official Resilio Sync cluster about transport negotiation, overlap truth, interface binding, proxy asymmetry, and relay survival.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `configured protocols`, `shared common protocols`, `configured ciphers`, `shared common ciphers`, `preferred interface`, and `hard cutoff` are not the same truth?

> where do those same current docs still show that the ordinary operator answer about `what tunnel classes are actually still possible here?` still depends on several pages instead of one stable product-owned family?

The most load-bearing source set for this pass was:

- Resilio's current `What ports and protocols are used by Sync?` article, which still describes config fetch, tracker, direct TCP/UDP over the listening port, relay fallback, LAN multicast/broadcast discovery, and separate router-facing UPnP/NAT-PMP packets.
- Resilio's current `Power user preferences` article, which still says `tunnel_protocols` and `tunnel_ciphers` require some common overlap to connect, `bind_interface` may switch to the next active interface, `use_only_bind_interface` can block connection attempts when the chosen interface is absent, and `lan_encrypt_data` forces LAN encryption.
- Resilio's current `Sync Preferences` article, which still says proxies prohibit incoming connections and that two peers behind proxies can talk only via relay.
- Resilio's current `Peers aren't connecting` article, which still says tracker reach, listening-port reach, relay reach, and multiple-NIC routing materially affect the tunnel that survives.
- Resilio's current `What is a Relay Server?` article, which still says relay is the fallback when direct connection is not possible and that it slows syncing relative to direct.

- What ports and protocols are used by Sync?  
  https://help.resilio.com/hc/en-us/articles/204754759-What-ports-and-protocols-are-used-by-Sync

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Peers aren't connecting  
  https://help.resilio.com/hc/en-us/articles/205450205-Peers-aren-t-connecting

- What is a Relay Server?  
  https://help.resilio.com/hc/en-us/articles/204754779-What-is-a-Relay-Server


## Additional Resilio official sources emphasized in rev0339

This revision leaned on another current official Resilio Sync cluster about nested parent/child subjects, overlap admission, same-ID boundaries, selective-sync ceilings, and reconnect-to-existing paths.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `nested share`, `visible through parent`, `seeds the child`, `contains an existing syncing interior`, and `reconnect to existing bytes` are not the same truth?

> where do those same current docs still show that the ordinary operator answer about `can I safely admit this overlap and what topology does it really create?` still depends on several pages instead of one stable product-owned family?

The most load-bearing source set for this pass was:

- Resilio's current `Is it possible to share a nested folder separately?` article, which still says both parent and child need RW/Owner, both are treated as separate sync folders, parent-only peers do not seed child-only peers, both sides must have Selective Sync disabled, the child subtree is indexed/rescanned twice, and child-share changes can still reach parent-share peers through the overlap.
- Resilio's current `Selective Sync` article, which still says Selective Sync is a materialized placeholder posture rather than full local bytes, making it a meaningful eligibility boundary for nested admission.
- Resilio's current `Selected folder is already added to Sync` article, which still says a device can have only one folder with the same `.sync/ID` and distinguishes same-path reuse from same-key / different-path collision.
- Resilio's current `Cannot add folder. It contains a folder that is already syncing.` article, which still says a larger home-folder claim can fail because the home folder already contains Sync's storage-folder license directory.
- Resilio's current `Can I connect two pre-populated pre-existing folders?` article, which still says attaching an existing populated path is a reconnect/confirmation lane rather than a fresh empty-path bind.
- Resilio's current change log, which still preserves the separate ceiling that a nested folder cannot be added in Selective Sync mode.

- Is it possible to share a nested folder separately?  
  https://help.resilio.com/hc/en-us/articles/205506159-Is-it-possible-to-share-a-nested-folder-separately

- Selective Sync  
  https://help.resilio.com/hc/en-us/articles/205458095-Selective-Sync

- Selected folder is already added to Sync  
  https://help.resilio.com/hc/en-us/articles/209316526-Selected-folder-is-already-added-to-Sync

- Cannot add folder. It contains a folder that is already syncing.  
  https://help.resilio.com/hc/en-us/articles/360000053399-Cannot-add-folder-It-contains-a-folder-that-is-already-syncing

- Can I connect two pre-populated pre-existing folders?  
  https://help.resilio.com/hc/en-us/articles/205506569-Can-I-connect-two-pre-populated-pre-existing-folders

- Resilio Sync change log  
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log


## rev0340 note — interface affinity, multi-NIC ambiguity, and service all-NIC audience

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio docs about named interface preference, multi-NIC troubleshooting, current performance witnesses, and still-published interface-related change-log history.

The most load-bearing sources for this pass were:

- Resilio's current `Power user preferences` article, which still says `bind_interface` names one interface, `use_only_bind_interface` turns disappearance into a hard connection cutoff, and if the defined interface is unavailable Sync will switch to the next active interface.
- Resilio's current `Peers aren't connecting` article, which still names multiple NICs as a real cause of connection trouble and suggests switching to another NIC in LAN cases.
- Resilio's current `Performance overview` article, which still exposes only current peer-table witnesses such as upload/download, RTT, and protocol.
- Resilio's still-published change log, which still preserves `Allow to select NIC for data transfer instead of binding to all interfaces`, `Fix Sync showing "No Network" when only bridge interface is available on OS X`, and `Allow Sync to listen all NICs when installed as service`.

Primary sources:

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Peers aren't connecting  
  https://help.resilio.com/hc/en-us/articles/205450205-Peers-aren-t-connecting

- Performance overview  
  https://help.resilio.com/hc/en-us/articles/360001331930-Performance-overview

- Resilio Sync change log  
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log



## rev0341 note — byte-plan certainty, hash witness, and reuse-vs-redownload ceilings

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio docs about changed-piece transfer, local dedup reuse, pre-seeded hashing, archive-backed rename reuse, and stuck partial-transfer residue.

The most load-bearing sources for this pass were:

- Resilio's current `When a file changes, does Resilio Sync transfer the entire file again, or just the part that's changed?` article, which still says only changed pieces are transferred in the ordinary case, while piece shifts can still force whole-file resend and Business has a separate diff-delta feature.
- Resilio's current `Some internal tasks are taking time to complete` article, which still says Sync separately checks file blocks, copies local file blocks for deduplication, hashes files, hashes local files for pre-seeded folders on receiving peers apart from read-only peers, and writes deduplicated pieces to disk.
- Resilio's current `What happens when file is renamed` article, which still says the receiving peer checks Archive for same-hash bytes and can reuse them under the new name instead of re-transmitting the bytes.
- Resilio's current `My files don't sync` article, which still says partially downloaded `.!sync` residue can remain in `.sync`, and if syncing does not resume after restart the operator may need to delete those temp files and restart again.

Primary sources:

- When a file changes, does Resilio Sync transfer the entire file again, or just the part that's changed?  
  https://help.resilio.com/hc/en-us/articles/206217095-When-a-file-changes-does-Resilio-Sync-transfer-the-entire-file-again-or-just-the-part-that-s-changed

- Some internal tasks are taking time to complete  
  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete

- What happens when file is renamed  
  https://help.resilio.com/hc/en-us/articles/209606526-What-happens-when-file-is-renamed

- My files don't sync  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync



## rev0342 note — queue-governance provenance, active-window ceilings, and visible-order mismatch

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio docs about the new file-download-priority feature, its power-user default, per-share overrides, active-queue ceilings, suspension behavior, and UI-order mismatch.

The most load-bearing sources for this pass were:

- Resilio's current `File download priority` article, which still says the feature is available in `3.1.0`, priority can be set by file size or modification time, global defaults can apply to still-inheriting existing shares and to new shares including single-file sharing, only the active 50,000-file queue is prioritized, suspension has internal exceptions, non-splittable files weaken strict preemption, and the UI queue may still appear alphabetical rather than in actual priority order.
- Resilio's current `Power user preferences` article, which still enumerates `folder_defaults.transfer_priority` and its values (`None`, smaller first, larger first, older first, newer first).
- Resilio's current `Folder Preferences` article, which still surfaces the per-share file-download-priority control.

Primary sources:

- File download priority  
  https://help.resilio.com/hc/en-us/articles/42328167759251-File-download-priority

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Folder Preferences  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences


## Revision addendum — official sources emphasized in rev0354

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about pause semantics, scheduler zero-rate windows, sleep / battery stops, LAN-exempt limits, and per-share network restrictions.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `paused`, `offline`, `limited`, `sleeping`, and `forbidden network` are not the same truth?

> where do those same current docs still show that the ordinary operator answer about `what this node is actually willing to do right now` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Sync Preferences` article, which still says there is a global pause/resume control, explicit sending/receiving rate limits, and a scheduler, while also stating that bandwidth limits apply to Internet connections by default rather than LAN.
- Resilio's current `Power user preferences` article, which still exposes `rate_limit_local_peers` and other low-level switches needed to make visible transfer caps truthful in LAN.
- Resilio's current `How to pause syncing` article, which still says pause leaves zero-sized files, deletions, and rescanning/indexing alive.
- Resilio's current `Running Sync on schedule` article, which still says scheduler `Paused` has its own semantics and again preserves deletions and indexing while describing upload/download effects separately.
- Resilio's current `Configuring Auto Sleep & Battery Saver (Android)` article, which still says Auto Sleep turns the core off, hides the device from connected peers, and wakes on a configured interval, while Battery Saver can force Sync to stop below a charge floor.
- Resilio's current `Setting network interface per share` article, which still says shares can be Any network, Wi‑Fi only, or Custom, and that a prohibited network yields `Stopped. Forbidden network` where the peer is not connected and new/updated files are not detected.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that pause, throttle, sleep cadence, battery stop, network prohibition, indexing, and delete propagation are materially different
- but current Resilio still answers `what is this node willing to do right now, what work continues anyway, and what gate is responsible?` too diffusely
- AnonSync should therefore prefer explicit activity-posture sheets, pause-semantics review, work-willingness proof, duty-cycle timelines, and durable lineage receipts over overloaded status folklore



## Revision addendum — official sources emphasized in rev0357

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about disconnected visibility without local path or space, placeholder-only Selective Sync presence, ignored-subject exclusion from `Size`, hidden Archive retention, storage-folder debug/profiler residue, remote storage telemetry, and low-space warnings tied to the default folder location.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `visible`, `counted in Size`, `occupies bytes`, `can still fetch later`, and `can still grow in hidden storage` are not the same truth?

> where do those same current docs still show that the ordinary operator answer about `what is really consuming disk here, and what budget gate will stop sync first?` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Folder Types and Management` article, which still says disconnected folders take no local space and may not even have a folder path, while Selective Sync takes minimal space and shows placeholder-backed contents.
- Resilio's current `Synchronization Modes` and `What Is an RSLS File?` articles, which still say Selective Sync placeholders represent files without their content and are 0-byte or minimal-space stand-ins.
- Resilio's current `Ignoring files in Sync (Ignore List)` article, which still says ignored subjects are not indexed and not counted in the `Size` column.
- Resilio's current `Using Archive for file versioning and restoring deleted files` article, which still says old or deleted copies go into hidden `.sync/Archive`, that retention can be adjusted including effectively forever, and that operators should mind available disk storage space.
- Resilio's current `Power user preferences` article, which still says the free-space warning threshold watches the drive with the default folder location and stops syncing files there, while also documenting rotated logs and `profiler.dat` under the storage folder.
- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says a linked device in `Sync All` mode can expose storage status remotely.
- Resilio's current change log, which still preserves the product fact that mobile/iOS storage-used viewing and clearing became an explicit operator surface.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that placeholder visibility, counted size, hidden Archive retention, service-storage residue, and watched low-space budgets are materially different
- but current Resilio still answers `what is actually consuming bytes, what is counted, and what low-space gate is really armed?` too diffusely
- AnonSync should therefore prefer explicit storage-accounting sheets, footprint reviews, budget-gate proof pages, occupancy-drift timelines, and durable lineage receipts over overloaded size folklore

Primary sources:

- Folder Types and Management  
  https://help.resilio.com/hc/en-us/articles/204762459-Folder-Types-and-Management

- Synchronization Modes  
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- What Is an RSLS File?  
  https://help.resilio.com/hc/en-us/articles/206115384-What-Is-an-RSLS-File

- Ignoring files in Sync (Ignore List)  
  https://help.resilio.com/hc/en-us/articles/205458165-Ignoring-files-in-Sync-Ignore-List

- Using Archive for file versioning and restoring deleted files.  
  https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Resilio Sync change log  
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log


## Revision addendum — official sources emphasized in rev0359

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about identity certificates, linked-device approvals, grouped peer-list rendering, Standard-vs-Advanced participant granularity, and separately editable device labels.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that a visible participant row can mean a grouped identity, a linked-device family, or a single device seat depending on folder family and surface?

> where do those same current docs still show that the ordinary operator answer about `who exactly did I approve or count?` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says identities are certificate-based, fingerprints are used for later connections, linked devices share folders automatically, and a remote user can choose to approve all linked devices for future sharing after approving one of them.
- Resilio's current `What's the difference between Standard and Advanced folders` article, which still says Advanced folders can reflect user identity and group linked devices under one user entry, while Standard folders do not reflect user identity in the peer list and instead show each linked device as a separate entity.
- Resilio's current `Sync functionality in detail` article, which still says peers and devices are grouped in the Peer List and that search can target folders, users, and devices.
- Resilio's current `Settings on mobile platforms` article, which still says other users are shown the identity name, device name, and certificate fingerprint, and that the device name can be edited.
- Resilio's current `Can I change the name of my Sync identity?` article, which still says changing identity name requires unlinking and creating a new identity, regenerating the certificate rather than merely changing display text.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that identity, certificate, linked-family grouping, device seats, and friendly labels are materially different
- but current Resilio still answers `who exactly is this row or count about, and what unit did I actually approve?` too diffusely
- AnonSync should therefore prefer explicit participant-unit sheets, peer-row granularity reviews, authority proof pages, participant timelines, and durable lineage receipts over overloaded peer folklore

Primary sources:

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- What's the difference between Standard and Advanced folders  
  https://help.resilio.com/hc/en-us/articles/204754679-What-s-the-difference-between-Standard-and-Advanced-folders

- Sync functionality in detail  
  https://help.resilio.com/hc/en-us/articles/204754389-Sync-functionality-in-detail

- Settings on mobile platforms  
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- Can I change the name of my Sync identity?  
  https://help.resilio.com/hc/en-us/articles/206163443-Can-I-change-the-name-of-my-Sync-identity

## Revision addendum — official sources emphasized in rev0360

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about filename normalization, case-collision behavior, path-length ceilings, invalid-name rules, and symbolic-link projection.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that a visible pathname, a canonical byte-level identity, and a safe cohort-wide arrival outcome are not the same thing?

> where do those same current docs still show that the ordinary operator answer about `will this path survive intact, be rewritten, conflict, or block?` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Conflict files in Sync` article, which still says case-insensitive targets can produce `.Conflict` files, decomposed UTF symbols can collide even when humans see the same glyph, prohibited filesystem symbols can be rewritten on Windows, and linked junctions can contribute to conflict behavior.
- Resilio's current `My files don't sync` article, which still says Sync expects UTF-8 filenames, mixed-system encoding can break syncing, and path or filename length can exceed platform ceilings.
- Resilio's current `Unsupported asterisk (*) characters at the end of file/folder names` article, which still says some trailing-asterisk names without extensions are invalid and may be interpreted as system data.
- Resilio's current `Soft links, hard links and symbolic links` article, which still says Windows link classes are unsupported while UNIX can sync symbolic-link objects without automatically syncing target folders.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that case, normalization, symbol rules, path ceilings, and link-object handling are materially different
- but current Resilio still answers `will this pathname survive intact, and what exactly will arrive on the other side?` too diffusely
- AnonSync should therefore prefer explicit path-projection sheets, path-equivalence reviews, projection-capability proof pages, filesystem-dialect timelines, and durable lineage receipts over overloaded filename folklore

Primary sources:

- Conflict files in Sync  
  https://help.resilio.com/hc/en-us/articles/204753629-Conflict-files-in-Sync

- My files don't sync  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Unsupported asterisk (*) characters at the end of file/folder names  
  https://help.resilio.com/hc/en-us/articles/206214715-Unsupported-asterisk-characters-at-the-end-of-file-folder-names

- Soft links, hard links and symbolic links  
  https://help.resilio.com/hc/en-us/articles/205504529-Soft-links-hard-links-and-symbolic-links

## Revision addendum — official sources emphasized in rev0362

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about approval quantifiers, linked-device carry, peer-count semantics, source sufficiency, self-only local shares, and linked-family removal limits.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `one`, `any`, `all`, `self only`, `all linked devices`, and `all connected peers` are different truths?

> where do those same current docs still show that the ordinary operator answer about `who exactly is this claim about, and how many counterparts are enough?` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Sync Share Dialog (Desktop)` article, which still says links can require approval from only new peers or from all peers per folder.
- Resilio's current `Sync functionality in detail` article, which still says any linked device can approve a folder connection.
- Resilio's current `Sync Main View (Desktop)` article, which still says `X of Y peers` means online peers out of the total including offline peers.
- Resilio's current `Synchronization Modes` article, which still says disconnected folders can connect whenever any peer in the swarm is online while Selective Sync fetch requires at least one peer that has the files online.
- Resilio's current `Sharing a folder locally` article, which still says a local share is connected only to `self`, only pulls from the parent share, and does not sync with remote peers directly even though the peer count can grow.
- Resilio's current `Disconnecting and Removing Folders` article, which still says removal from linked devices does not prove disappearance from nonlinked remote devices.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that counterpart quantifiers and sufficiency thresholds matter
- but current Resilio still answers `who exactly is this claim about, and how many counterparts are enough?` too diffusely
- AnonSync should therefore prefer explicit quantifier sheets, audience-scope reviews, sufficiency-proof pages, quantifier-drift timelines, and durable lineage receipts over overloaded plural nouns

Primary sources:

- Sync Share Dialog (Desktop)  
  https://help.resilio.com/hc/en-us/articles/204790709-Sync-Share-Dialog-Desktop

- Sync functionality in detail  
  https://help.resilio.com/hc/en-us/articles/204754389-Sync-functionality-in-detail

- Sync Main View (Desktop)  
  https://help.resilio.com/hc/en-us/articles/204755009-Sync-Main-View-Desktop

- Synchronization Modes  
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- Sharing a folder locally  
  https://help.resilio.com/hc/en-us/articles/360011582500-Sharing-a-folder-locally

- Disconnecting and Removing Folders  
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

## Revision addendum — official sources emphasized in rev0366

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about identity naming, device labels, share-path naming, desktop aliases, invite-inserted labels, and backup-folder naming.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that `identity name`, `device name`, `folder name`, `share alias`, and `link label` are different truths?

> where do those same current docs still show that the ordinary operator answer about `what exactly did I rename, where will the label show up, and did authority change?` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Can I change the name of my Sync identity?` article, which still says identity naming participates in certificate creation and cannot be changed in place.
- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says peers recognize a connecting installation by name plus fingerprint.
- Resilio's current `Setting custom name for sync shares` article, which still says a custom share name is local UI only, does not rename the disk folder, does not propagate to peers or linked devices, and can be varied per generated link or QR.
- Resilio's current `Can I move or rename a syncing folder?` article, which still says a local filesystem rename affects only that device.
- Resilio's current Android / iOS interface docs and mobile settings docs, which still say username, fingerprint, and device name are shown together while device-name change remains separate from identity regeneration.
- Resilio's current `How to use Camera Backup (all mobiles)?` article, which still says default backup-folder naming depends on device class and uses the device name on iOS.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that naming planes and label propagation matter
- but current Resilio still answers `what exactly did I rename, and who will see that new text?` too diffusely
- AnonSync should therefore prefer explicit name-plane sheets, alias reviews, authority-proof pages, label-drift timelines, and durable lineage receipts over overloaded `rename` verbs

Primary sources:

- Can I change the name of my Sync identity?  
  https://help.resilio.com/hc/en-us/articles/206163443-Can-I-change-the-name-of-my-Sync-identity

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Setting custom name for sync shares  
  https://help.resilio.com/hc/en-us/articles/360011865879-Setting-custom-name-for-sync-shares

- Can I move or rename a syncing folder?  
  https://help.resilio.com/hc/en-us/articles/205450655-Can-I-move-or-rename-a-syncing-folder

- Settings on mobile platforms  
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- Sync interface on Android  
  https://help.resilio.com/hc/en-us/articles/213500383-Sync-interface-on-Android

- Sync Interface on iOS devices  
  https://help.resilio.com/hc/en-us/articles/212016726-Sync-Interface-on-iOS-devices

- How to use Camera Backup (all mobiles)?  
  https://help.resilio.com/hc/en-us/articles/205506809-How-to-use-Camera-Backup-all-mobiles


## Revision addendum — official sources emphasized in rev0367

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about **direction of effect**, not just visibility or presence.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that bidirectional sync, read-only replication, storage-only backup, and encrypted custody are different directional lanes?

> where do those same current docs still show that the ordinary operator answer about `which side can publish, delete back, restore back, or only retain` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Synchronization Modes` article, which still says Synced mode synchronizes all content and propagates additions, deletions, and changes across connected peers.
- Resilio's current `Folder Types and Management` article, which still says Read Only means you may not send changes, additions, or deletions to the rest of the swarm and that Encrypted folders are backup-oriented.
- Resilio's current `Folder Preferences` article, which still says remote RW changes and deletions propagate to other peers and that `Overwrite any changed files` for Read Only folders can destructively replace local divergence.
- Resilio's current `How to Back up data (Android only)` article, which still says mobile backup preserves desktop copies after mobile deletion and preserves phone copies after desktop deletion because the desktop has Read-only access.
- Resilio's current `How to use Camera Backup (all mobiles)?` article, which still says camera backup is for storage purposes only, uses Read Only keys, and leaves already-present pictures on both sides after disconnect.
- Resilio's current `Encrypted folders` article, which still says encrypted nodes are Read Only, can re-share only in encrypted form, and cannot restore deleted files back from their own Archive to the live source.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that directionality is more than one label
- but current Resilio still answers `which side can actually publish, delete back, restore back, or only hold bytes?` too diffusely
- AnonSync should therefore prefer explicit effect-direction sheets, flow-direction reviews, reverse-lane proofs, effect-direction timelines, and durable lineage receipts over overloaded mode icons or posture names

Primary sources:

- Synchronization Modes  
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- Folder Types and Management  
  https://help.resilio.com/hc/en-us/articles/204762459-Folder-Types-and-Management

- Folder Preferences  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- How to Back up data (Android only)  
  https://help.resilio.com/hc/en-us/articles/204762339-How-to-Back-up-data-Android-only

- How to use Camera Backup (all mobiles)?  
  https://help.resilio.com/hc/en-us/articles/205506809-How-to-use-Camera-Backup-all-mobiles

- Encrypted folders  
  https://help.resilio.com/hc/en-us/articles/207370466-Encrypted-folders



## Revision addendum — official sources emphasized in rev0368

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another current official Resilio Sync cluster about **governance plane truth**, not just action locality.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that desktop folder prefs, power-user settings, startup config, service storage, CLI switches, and mobile settings are different governance planes?

> where do those same current docs still show that the ordinary operator answer about `who owns this value, what overrode what, and does this subject still inherit the default?` depends on several articles instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Folder Preferences` article, which still says folder preferences are available on desktop platforms only.
- Resilio's current `Power user preferences` article, which still says some advanced settings are ignored in Linux WebUI.
- Resilio's current `File download priority` article, which still says a global default may apply to existing and new shares but a manually set share no longer follows later global changes, even if later set back to `None`.
- Resilio's current `Running Sync in configuration mode` article, which still says config can include advanced parameters, can create only Standard folders, and that config-authored shared folders disable WebUI and override folders previously added from WebUI.
- Resilio's current `Sync Service Troubleshooting on Windows` article, which still says service storage location and service principal changes can move the effective world and that some WebUI changes require service restart.
- Resilio's current `Settings on mobile platforms` article, which still shows a narrower mobile settings surface than the richer desktop-only folder and advanced preference planes.
- Resilio's current `Is there a Command Line Interface (CLI) for Resilio Sync on Windows?` article, which still says CLI switches can force config mode, storage path, and loopback-only WebUI behavior.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that governance is split across several planes
- but current Resilio still answers `who owns this value, what overrode what, and does this subject still inherit the default?` too diffusely
- AnonSync should therefore prefer explicit governance-plane sheets, policy-authorship reviews, mutation-authority proofs, governance timelines, and durable lineage receipts over overloaded `Preferences` or `Advanced` language

Primary sources:

- Folder Preferences  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- File download priority  
  https://help.resilio.com/hc/en-us/articles/42328167759251-File-download-priority

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Sync Service Troubleshooting on Windows  
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

- Settings on mobile platforms  
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- Is there a Command Line Interface (CLI) for Resilio Sync on Windows?  
  https://help.resilio.com/hc/en-us/articles/205506359-Is-there-a-Command-Line-Interface-CLI-for-Resilio-Sync-on-Windows


## rev0369 source set — local mutability ceiling, write barriers, and host-write-lane truth

The most load-bearing source set for this pass was:

- Resilio's current `Locked files` article, which still says another application can block access to files, making transfer impossible, and that Sync cannot identify the locking app for you.
- Resilio's current `Power user preferences` article, which still says `recheck_locked_files_interval` governs later retry of locked files.
- Resilio's current `My files don't sync` article, which still lists locked/protected files, missing RW access, filesystem errors, and missing mounts as different common causes.
- Resilio's current `Sync and SMB file shares` article, which still says SMB locks can persist and that mixed direct-local plus SMB access can roll back or damage files.
- Resilio's current `Permissions Sync requires on Android and Amazon Kindle` article, which still says Android storage permission allows Sync to write received files and apply changes.
- Resilio's current `SD card gimmicks on Android` article, which still says SD-card write access depends on granting root access through the provider API, warns that walking to the path through the ordinary picker does not grant it, and says Sync cannot create a new backup folder on SD card through that lane.
- Resilio's current `Synology` article, which still says the internal `rslsync` user needs explicit Read/Write rights on the NAS shared folder.
- Resilio's current `Sync Service Troubleshooting on Windows` article, which still says a service user may lack permission to write desired folders, that Local System changes the storage world, and that old folders then have to be re-added / re-shared.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that local writeability has several distinct barriers
- but current Resilio still answers `can this runtime actually mutate bytes here now, and what exact barrier is stronger if not?` too diffusely
- AnonSync should therefore prefer explicit local-mutability sheets, write-barrier reviews, write-authority proofs, mutability timelines, and durable lineage receipts over overloaded `cannot sync` or `permissions` language

Primary sources:

- Locked files  
  https://help.resilio.com/hc/en-us/articles/205504549-Locked-files

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- My files don't sync  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Sync and SMB file shares  
  https://help.resilio.com/hc/en-us/articles/207755736-Sync-and-SMB-file-shares

- Permissions Sync requires on Android and Amazon Kindle  
  https://help.resilio.com/hc/en-us/articles/205451065-Permissions-Sync-requires-on-Android-and-Amazon-Kindle

- SD card gimmicks on Android  
  https://help.resilio.com/hc/en-us/articles/209643433-SD-card-gimmicks-on-Android

- Synology  
  https://help.resilio.com/hc/en-us/articles/206664850-Synology

- Sync Service Troubleshooting on Windows  
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

## rev0370 source set — entitlement provenance, license topology, and feature-afterlife truth

The most load-bearing source set for this pass was:

- Resilio's current `Licensing in Resilio Sync 3.0` article, which still says legacy Home Pro and Family Pro continue to work in v3, while Sync Business licenses are not compatible with v3 and commercial users should stay on v2 or move to other business offerings.
- Resilio's current `FAQ Resilio Sync 3.0.0` article, which still says v3 functionality is fully available for non-commercial use, but activation still needs a license; the site-issued v3 license is associated with the given person and cannot be shared; legacy Home Pro remains personal-use only; and legacy Family Pro can be used by up to five family members.
- Resilio's current `Important before updating to Resilio Sync 3.0.0` and `Updating installation to Resilio Sync v3` articles, which still say Free-to-v3 upgrades get only a short trial before registration/activation are needed and that Business installations, including personal Windows Server business installs, should not update to v3.
- Resilio's current `How to apply license key and share license seats` article, which still says Home/Free keys can be applied to several devices, Family Pro uses the same key across family devices, Business can be applied only to one owner identity, linked devices of the owner inherit automatically, other identities need shared seats, and reapplying the Business key elsewhere steals ownership.
- Resilio's current `What happens when Sync Business trial or license expires?` article, which still says Business expiry removes Pro features and shared seats expire on the same date.
- Resilio's current `Sharing a folder locally` article, which still says local shares are a Pro feature and stop working when the trial/license expires or the license is removed.
- Resilio's current `"Your Sync Business license doesn't support Windows Server or Linux (x86 or x64)."` article, which still says the license may apply on Server OS but sharing files/folders and linking devices stop without the Server-support qualifier.
- Resilio's current `My device has lost the license and Sync has reverted to the Free version...` article, which still says Business ownership can move if the key is applied elsewhere and a seat can disappear through reclaim or over-sharing.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that entitlement source, topology, legitimacy, and feature-afterlife are different truths
- but current Resilio still answers `why is this feature available here, who granted it, and what happens when that entitlement changes?` too diffusely
- AnonSync should therefore prefer explicit entitlement sheets, license-topology reviews, feature-entitlement proofs, entitlement timelines, and durable lineage receipts over overloaded `licensed`, `Pro`, or `free` language

Primary sources:

- Licensing in Resilio Sync 3.0  
  https://help.resilio.com/hc/en-us/articles/31116248751123-Licensing-in-Resilio-Sync-3-0

- FAQ Resilio Sync 3.0.0  
  https://help.resilio.com/hc/en-us/articles/32109883606035-FAQ-Resilio-Sync-3-0-0

- Important before updating to Resilio Sync 3.0.0  
  https://help.resilio.com/hc/en-us/articles/31193941051795-Important-before-updating-to-Resilio-Sync-3-0-0

- Updating installation to Resilio Sync v3  
  https://help.resilio.com/hc/en-us/articles/31194252837779-Updating-installation-to-Resilio-Sync-v3

- How to apply license key and share license seats  
  https://help.resilio.com/hc/en-us/articles/204762369-How-to-apply-license-key-and-share-license-seats

- What happens when Sync Business trial or license expires?  
  https://help.resilio.com/hc/en-us/articles/206216825-What-happens-when-Sync-Business-trial-or-license-expires

- What is the difference between Sync Home Pro and Sync Family Pro?  
  https://help.resilio.com/hc/en-us/articles/360002187599-What-is-the-difference-between-Sync-Home-Pro-and-Sync-Family-Pro

- Sharing a folder locally  
  https://help.resilio.com/hc/en-us/articles/360011582500-Sharing-a-folder-locally

- "Your Sync Business license doesn't support Windows Server or Linux (x86 or x64)."  
  https://help.resilio.com/hc/en-us/articles/115000651390--Your-Sync-Business-license-doesn-t-support-Windows-Server-or-Linux-x86-or-x64

- My device has lost the license and Sync has reverted to the Free version. How can I return the Pro functionality?  
  https://help.resilio.com/hc/en-us/articles/204753499-My-device-has-lost-the-license-and-Sync-has-reverted-to-the-Free-version-How-can-I-return-the-Pro-functionality


## rev0408 source set — promise capacity, concurrency, and overcommitment truth

The most load-bearing source set for this pass was:

- Resilio's current `Performance overview` article, which still says Sync exposes 1-minute, 10-minute, and 1-hour real-time graphs, per-peer upload/download speed, RTT, and disk queue depth.
- Resilio's current `Sync Preferences` article, which still says sending/receiving rates can be limited globally and that the scheduler can pause or limit speed on selected day-hour windows.
- Resilio's current `Running Sync on schedule` article, which still says `Paused` stops ordinary upload/download but still allows zero-sized file sync, deletions, rescanning/indexing, and some uploads to non-paused peers.
- Resilio's current `How soon does synchronization start?` article, which still says rescans run every 600 seconds by default and that detected changes may trigger whole-file rehashing.
- Resilio's current `Some internal tasks are taking time to complete` article, which still says hidden work includes block checking, dedup copying, hashing, merging, scanning, reading, transferring, and writing.
- Resilio's current `Power user preferences` article, which still says disk priority, per-job disk threading, indexing threads, and config save/refresh cadence can alter runtime contention and differ by version.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for admitting that real capacity has several ingredients
- but current Resilio still answers `do we honestly have room for one more promise, and what stronger promise is blocked if not?` too diffusely
- AnonSync should therefore prefer explicit commitment-capacity sheets, promise-load reviews, capacity proofs, capacity timelines, and durable lineage receipts over overloaded graph, queue, or scheduler language

Primary sources:

- Performance overview  
  https://help.resilio.com/hc/en-us/articles/360001331930-Performance-overview

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Running Sync on schedule  
  https://help.resilio.com/hc/en-us/articles/210783266-Running-Sync-on-schedule

- How soon does synchronization start?  
  https://help.resilio.com/hc/en-us/articles/204754319-How-soon-does-synchronization-start

- Some internal tasks are taking time to complete  
  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences
