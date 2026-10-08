## Revision addendum after rev0412 — temporary burst borrow, reserve exception, and payback truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **temporary out-of-envelope use that may be lawful for a while without becoming ordinary entitlement**.
It does eight things in one tranche:

1. Continues the archive after rev0412 with a new page family centered on what happens *after* the product can detect overdraw but *before* it should collapse all extra-room use into either `fine` or `breach`.
2. Tightens the non-clone line again: borrow Resilio's candor that per-share and global priority, pause, scheduler, rate limits, rescans, and hidden internal work really do let operators favor urgent work temporarily; refuse any contract where the operator still has to reconstruct `was this extra room a valid burst exception, when does it expire, what did it cost others, and what is owed afterward` from scattered surfaces.
3. Adds one new **Resilio evaluation** document focused on why current temporary-borrow truth is still too fragmented to clone even though the ingredients are useful.
4. Adds five new **interface specs** for burst borrow contract sheet, burst authorization review, burst borrow proof, burst exception timeline, and burst borrow lineage receipt.
5. Makes one hard product decision explicit: **unauthorized overdraw is weaker than typed temporary exception truth.**
6. Makes another hard product decision explicit: **authorized temporary borrow, expired borrow, unauthorized overdraw, and unpaid payback are different public truths.**
7. Makes a third hard product decision explicit: **temporary urgent borrow can exist without silently becoming new ordinary entitlement.**
8. Packages the result as another continuation archive whose new tranche makes the `ordinary award / borrowed room / authority basis / expiry / harmed-claimant consequence / payback / restoration proof / receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1618-resilio-temporary-envelope-exception-burst-borrow-and-restitution-fragmentation-evaluation.md`
- `1619-burst-borrow-contract-sheet-page-exception-scope-expiry-harmed-claimants-and-payback-basis-interface-spec.md`
- `1620-burst-authorization-review-page-sanctioned-overdraw-reserve-borrow-throttle-back-and-denial-routes-interface-spec.md`
- `1621-burst-borrow-proof-page-exception-authority-live-consumption-payback-and-restoration-basis-interface-spec.md`
- `1622-burst-exception-timeline-page-authorize-borrow-renew-expire-payback-and-restored-normal-entitlement-events-interface-spec.md`
- `1623-burst-borrow-lineage-receipt-page-exception-room-payback-state-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's urgent reprioritization and shaping ingredients**
- **do not clone Resilio's temporary-borrow and payback contract**

This time the reason is especially clear around **priority changes that suspend lower-priority downloads, global defaults that stop applying once a share is manually altered, pause and scheduler lanes that can favor one folder while other file-system effects keep running, rescans and hidden work that keep consuming room, and short-window performance telemetry that still does not answer whether extra room was lawfully borrowed or just silently taken**.
Current official materials simultaneously show that:

- current `File download priority` docs still say higher-priority files suspend lower-priority downloads, the active prioritized queue is limited, and queue rebuilds may affect performance
- the same docs still say `folder_defaults.transfer_priority` can apply globally but manually altered shares stop following later global changes even if set back to `None`
- current `How to pause syncing` docs still say pause is useful when transfer speed is low and you want to prioritize other folders by putting less-needed folders on hold
- current `Sync Preferences` docs still expose Global Pause plus global sending and receiving limits and scheduler controls
- current `Running Sync on schedule` docs still say paused windows stop ordinary upload/download but still allow zero-sized-file sync, deletion propagation, rescanning, indexing, and some onward uploads
- current `How soon does synchronization start?` docs still say scheduled rescans run every 600 seconds by default and can trigger whole-file rehashing
- current `Some internal tasks are taking time to complete` docs still say hidden work like block checking, dedup copy, hashing, merging, scanning, reading, transferring, and writing can continue for a long time and may self-recover
- current `Performance overview` docs still expose only short-window transfer, RTT, disk-load, and queue-depth evidence

That candor is useful.
The temporary-borrow contract is the problem.
AnonSync should not clone a world where the operator still has to translate `priority raised`, `others paused`, `global rate changed`, `urgent claimant still active`, and `hidden work continuing` into one stable answer about whether extra room is being used under a valid short-lived exception, whether that exception expired, and what reserve or claimant payback is now owed.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because temporary extra-room use is a real contract with separate truths for ordinary award, borrowed room, authority basis, expiry, harmed-claimant consequence, payback, and restored entitlement, but the present contract still scatters the answer to `is this lawful temporary borrow or just silent overdraw, and what is owed when it ends?` across several KB articles and UI surfaces instead of owning it as one stable page family.**

## Revision addendum after rev0411 — allocation-envelope conformance, protected-reserve leakage, and overdraw truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **active winners that may no longer be honoring the room they were actually awarded**.
It does eight things in one tranche:

1. Continues the archive after rev0411 with a new page family centered on what happens *after* a winner activates but *before* the product should pretend that active use is still inside the awarded envelope.
2. Tightens the non-clone line again: borrow Resilio's candor that priority rules, per-share overrides, global rate limits, scheduler windows, rescans, hidden internal work, and short-window performance graphs all shape real consumption; refuse any contract where the operator still has to reconstruct `is the winner inside the award, leaning on the edge, borrowing reserve, or leaking into someone else's room` from scattered surfaces.
3. Adds one new **Resilio evaluation** document focused on why current envelope-conformance truth is still too fragmented to clone even though the ingredients are useful.
4. Adds five new **interface specs** for allocation envelope contract sheet, envelope conformance review, allocation envelope proof, allocation envelope timeline, and allocation envelope lineage receipt.
5. Makes one hard product decision explicit: **activated occupancy is weaker than envelope-conforming occupancy.**
6. Makes another hard product decision explicit: **within-envelope, edge-of-envelope, ordinary overdraw, protected-reserve breach, and cross-claim bleed are different public truths.**
7. Makes a third hard product decision explicit: **temporary emergency borrow may justify a narrow exception but may not silently normalize overdraw, reserve leakage, or claimant harm.**
8. Packages the result as another continuation archive whose new tranche makes the `award limit / current consumption class / reserve impact / claimant impact / corrective route / conformance proof / receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1612-resilio-allocation-envelope-conformance-protected-reserve-leakage-and-overdraw-fragmentation-evaluation.md`
- `1613-allocation-envelope-contract-sheet-page-awarded-room-limit-borrowed-reserve-and-conformance-basis-interface-spec.md`
- `1614-envelope-conformance-review-page-in-bounds-overdraw-protected-reserve-breach-and-corrective-routes-interface-spec.md`
- `1615-allocation-envelope-proof-page-occupancy-within-award-overdraw-class-and-corrective-basis-interface-spec.md`
- `1616-allocation-envelope-timeline-page-award-activation-overdraw-correction-and-restored-conformance-events-interface-spec.md`
- `1617-allocation-envelope-lineage-receipt-page-awarded-room-conformance-class-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's shaping and pressure candor**
- **do not clone Resilio's envelope-conformance contract**

This time the reason is especially clear around **per-share and global priority rules, global send/receive limits, pause/scheduler asymmetries, rescans and hidden internal work, and short-window performance telemetry that all influence real room consumption without one durable answer to whether active use is still inside the room actually awarded**.
Current official materials simultaneously show that:

- current `File download priority` docs still say higher-priority files suspend lower-priority downloads, the active prioritized queue is limited, and queue rebuilds may affect performance
- current `Folder Preferences` docs still say file download priority can be set per share
- current `Power user preferences` docs still say `folder_defaults.transfer_priority` exists as a global default for shares that did not break inheritance
- current `Sync Preferences` docs still expose global sending/receiving limits and scheduler controls
- current `How to pause syncing` docs still say pause can be used to prioritize other folders while deletions and rescanning/indexing still continue
- current `How soon does synchronization start?` docs still say scheduled rescans run every 600 seconds by default and can trigger whole-file rehashing
- current `Some internal tasks are taking time to complete` docs still say hidden work like checking blocks, dedup copy, hashing, merging, scanning, reading, transferring, and writing can continue for a long time and may self-recover
- current `Performance overview` docs still expose only short-window transfer, RTT, disk-load, and queue-depth evidence

That candor is useful.
The envelope-conformance contract is the problem.
AnonSync should not clone a world where the operator still has to translate `winner active`, `queue moving`, `priority raised`, `global rate changed`, `paused neighbors`, `rescans running`, and `hidden work continuing` into one stable answer about whether the winner is honestly staying inside the room it was awarded or quietly bleeding into protected reserve and other claimants' space.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because activated occupancy is a real contract with separate truths for awarded room, current consumption class, reserve borrowing, reserve breach, claimant impact, corrective throttle, reclaim, and restored conformance, but the present contract still scatters the answer to `is the active winner still inside the room it honestly owns?` across several KB articles and UI surfaces instead of owning it as one stable page family.**


## Revision addendum after rev0410 — reservation activation, idle occupancy, and reclaim truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **awarded room that may not actually activate**.
It does eight things in one tranche:

1. Continues the archive after rev0410 with a new page family centered on what happens *after* contested room already has a winner but *before* the product should pretend that the winner is honestly using that room.
2. Tightens the non-clone line again: borrow Resilio's candor that priority, queue limits, hidden internal tasks, missing source peers, locked files, pause controls, and short-window performance graphs all matter; refuse any contract where the operator still has to reconstruct `did the winner actually activate, is the winner just churning, is the room being idly held, and when do the losers deserve reclaim?` from scattered surfaces.
3. Adds one new **Resilio evaluation** document focused on why current allocation-activation truth is still too fragmented to clone even though the ingredients are useful.
4. Adds five new **interface specs** for reservation activation contract sheet, allocation activation review, reservation occupancy proof, allocation occupancy timeline, and allocation occupancy lineage receipt.
5. Makes one hard product decision explicit: **allocation verdict is weaker than activated occupancy.**
6. Makes another hard product decision explicit: **awarded-not-started, activated-consuming, activated-no-net-progress, idle-held, downgraded, and reclaimed are different public truths.**
7. Makes a third hard product decision explicit: **losing-claimant starvation resumes when a winner fails its activation window, especially after emergency or protected-reserve borrowing.**
8. Packages the result as another continuation archive whose new tranche makes the `winner basis / activation window / idle age / blocker class / reclaim trigger / loser blockage / occupancy receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1606-resilio-reservation-allocation-activation-idle-occupancy-and-reclaim-fragmentation-evaluation.md`
- `1607-reservation-activation-contract-sheet-page-winning-claim-occupancy-and-activation-window-interface-spec.md`
- `1608-allocation-activation-review-page-activate-downgrade-reclaim-and-reopen-contention-routes-interface-spec.md`
- `1609-reservation-occupancy-proof-page-activated-room-idle-winner-and-reclaim-basis-interface-spec.md`
- `1610-allocation-occupancy-timeline-page-verdict-activation-idle-drift-and-reclaim-events-interface-spec.md`
- `1611-allocation-occupancy-lineage-receipt-page-winning-room-activation-state-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's activation and blocker candor**
- **do not clone Resilio's allocation-occupancy and reclaim contract**

This time the reason is especially clear around **higher-priority downloads suspending lower-priority ones, hidden internal tasks, missing-source-peer failures, locked-file blockers, short-window performance graphs, and pause controls that can all shape whether a winner really consumes awarded room without one durable activation verdict**.
Current official materials simultaneously show that:

- current `File download priority` docs still say higher-priority files suspend lower-priority downloads and that the active prioritized queue is limited
- the same docs still say queue rebuilds can affect performance and the queue may still appear alphabetical in the UI
- current `Some internal tasks are taking time to complete` docs still say block checking, dedup copy, hashing, merging, scanning, reading, transferring, and writing can continue for a long time and may self-recover
- current `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time` docs still say peers may announce files that later have no downloadable source
- current `Locked files` docs still say another application can block access and make transfer impossible
- current `Performance overview` docs still expose only short-window transfer, RTT, disk-load, and queue-depth evidence
- current `How to pause syncing` docs still say pause can be used to prioritize other folders by putting less-needed folders on hold

That candor is useful.
The allocation-activation contract is the problem.
AnonSync should not clone a world where the operator still has to translate `winner selected`, `queue moving`, `internal tasks running`, `locked`, `no source`, and `paused for something else` into one stable answer about whether awarded room is truly activated, idly held, or ready to be reclaimed for the people still waiting.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because winning contested room is a real contract with separate truths for award, activation, productive occupancy, idle hold, blocker class, reclaim trigger, and loser blockage, but the present contract still scatters the answer to `did the winner really take and use the room, or should the room go back for reclaim?` across several KB articles and UI surfaces instead of owning it as one stable page family.**


## Revision addendum after rev0409 — reservation contention, preemption, and fairness truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **reservation arbitration truth**.
It does eight things in one tranche:

1. Continues the archive after rev0409 with a new page family centered on what happens when several valid-looking claimants compete for the same future room.
2. Tightens the non-clone line again: borrow Resilio's candor that file-priority rules, per-share overrides, global defaults, pause controls, scheduler lanes, and queue suspension all shape who effectively goes first; refuse any contract where the operator still has to reconstruct `who wins this contested room, what reserve may not be touched, and who is being starved or preempted` from scattered surfaces.
3. Adds one new **Resilio evaluation** document focused on why current contention truth is still too fragmented to clone even though the ingredients are useful.
4. Adds five new **interface specs** for reservation contention contract sheet, contention arbitration review, reservation verdict proof, reservation contention timeline, and reservation contention lineage receipt.
5. Makes one hard product decision explicit: **reservation truth is weaker than reservation-allocation truth under contention.**
6. Makes another hard product decision explicit: **winning claimant, protected reserve, split allocation, defer, deny, and preempted claimant are different public truths.**
7. Makes a third hard product decision explicit: **manual override and emergency pause may influence allocation but may not masquerade as doctrine, fairness, or protected-reserve policy.**
8. Packages the result as another continuation archive whose new tranche makes the `claimant set / protected reserve / arbitration route / winner basis / loser preservation / starvation guard / contention receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1600-resilio-promise-reservation-contention-preemption-and-fairness-fragmentation-evaluation.md`
- `1601-reservation-contention-contract-sheet-page-contested-room-claimants-and-protected-reserve-interface-spec.md`
- `1602-contention-arbitration-review-page-allocate-split-preempt-defer-and-deny-routes-interface-spec.md`
- `1603-reservation-verdict-proof-page-winning-claim-preemption-basis-and-starvation-guard-interface-spec.md`
- `1604-reservation-contention-timeline-page-claim-collision-escalation-preemption-and-release-events-interface-spec.md`
- `1605-reservation-contention-lineage-receipt-page-allocation-basis-preemption-class-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's reservation-arbitration contract**

This time the reason is especially clear around **per-share download priority, global default priority, queue suspension for higher-priority files, pause-as-ad-hoc-priority, scheduler lanes, and override detachment that all influence who effectively goes first without one durable allocation verdict**.
Current official materials simultaneously show that:

- current `File download priority` docs still say download priority can be set per share or by global power-user default
- the same docs still say higher-priority files suspend lower-priority downloads, queue rebuilds can affect performance, and the UI queue may still appear alphabetical rather than in true priority order
- the same docs still say a share manually given its own priority is no longer affected by later changes to the global default, even if manually set back to `None`
- current `How to pause syncing` docs still say pause can be used to set priority for other folders by putting less-needed folders on hold
- current `Sync Preferences` docs still say Global Pause excludes shares already paused individually while global send/receive limits and scheduler lanes still shape throughput
- current `Running Sync on schedule` docs still say paused windows stop ordinary transfer but still allow deletions, rescanning, indexing, and some onward uploads
- current `Power user preferences` docs still say `folder_defaults.transfer_priority` exists as a global default whose effect depends on whether a share kept or broke inheritance

That candor is useful.
The reservation-arbitration contract is the problem.
AnonSync should not clone a world where the operator still has to translate `higher priority`, `paused for now`, `global default`, `manual override`, `queue suspended`, and `still alphabetical in UI` into one stable answer about who wins contested future room, what reserve may not be touched, who is starved, and what stronger promise stays blocked.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because reservation contention is a real contract with separate truths for claimant class, protected reserve, arbitration route, preemption basis, fairness guard, and blocked stronger sentences, but the present contract still scatters the answer to `who wins this room and what do the losers honestly get next?` across several KB articles and UI surfaces instead of owning it as one stable page family.**


## Revision addendum after rev0408 — promise reservation, soft holds, and expiry truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **promise reservation truth**.
It does eight things in one tranche:

1. Continues the archive after rev0408 with a new page family centered on what happens *after* an issuer is allowed to promise and *even after* some honest headroom exists but *before* that future room should be treated as safely spoken for.
2. Tightens the non-clone line again: borrow Resilio's candor that throughput windows, scheduler pauses, global/individual pause semantics, rescans, hidden preprocessing, and rate limits all shape real future room; refuse any contract where the operator still has to reconstruct `is this room already softly held, who owns that hold, when does it expire, and what stronger promise is blocked by ghost reservations?` from scattered surfaces.
3. Adds one new **Resilio evaluation** document focused on why current reservation truth is still too fragmented to clone even though the ingredients are useful.
4. Adds five new **interface specs** for promise reservation contract sheet, reservation shaping review, reservation proof, reservation timeline, and reservation lineage receipt.
5. Makes one hard product decision explicit: **available promise capacity is weaker than explicit reservation truth.**
6. Makes another hard product decision explicit: **soft hold, hard reservation, protected reserve, provisional option, and expired hold are different public truths.**
7. Makes a third hard product decision explicit: **ghost reservations and stale holds must consume visible risk instead of silently stealing future honesty.**
8. Packages the result as another continuation archive whose new tranche makes the `reservation basis / hold owner / expiry / release trigger / reserve boundary / blocked stronger promise / reservation receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1594-resilio-promise-reservation-soft-hold-and-expiry-fragmentation-evaluation.md`
- `1595-promise-reservation-contract-sheet-page-soft-hold-owner-expiry-and-reserve-boundary-interface-spec.md`
- `1596-reservation-shaping-review-page-soft-hold-hard-reservation-option-and-release-routes-interface-spec.md`
- `1597-promise-reservation-proof-page-reserved-scope-expiry-window-and-ghost-hold-guard-interface-spec.md`
- `1598-promise-reservation-timeline-page-hold-open-renew-release-expire-and-reclaim-events-interface-spec.md`
- `1599-promise-reservation-lineage-receipt-page-hold-basis-expiry-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's load-shaping ingredients and operational candor**
- **do not clone Resilio's promise-reservation and soft-hold contract**

## Revision addendum after rev0406 — re-promise authority, credibility budget, and issuance-throttle truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **who may promise again after degraded trust**.
It does eight things in one tranche:

1. Continues the archive after rev0406 with a new page family centered on what happens *after* recovery begins or even after some trust has been repaired but *before* the product should let anyone publish a fresh promise at the old strength.
2. Tightens the non-clone line again: borrow Resilio's candor that permissions, approvals, linked identities, mixed-version risk, version-scoped settings, and support tier all shape real operational authority; refuse any contract where the operator still has to reconstruct `who may publish what class of new promise, for what scope, under what co-sign rule, with what probation or outright block?` from scattered surfaces.
3. Adds one new **Resilio evaluation** document focused on why current promise-authority truth is still too fragmented to clone even though the ingredients are useful.
4. Adds five new **interface specs** for re-promise authority contract sheet, promise issuance review, re-promise authority proof, authority timeline, and authority lineage receipt.
5. Makes one hard product decision explicit: **trust repair is weaker than restored promise authority.**
6. Makes another hard product decision explicit: **autonomous authority, co-sign-required authority, scope-capped authority, target-only authority, and blocked authority are different public truths.**
7. Makes a third hard product decision explicit: **credibility budget is first-class and repeated misses must degrade authority explicitly instead of being normalized by one decent recovery.**
8. Packages the result as another continuation archive whose new tranche makes the `authority basis / credibility budget / promise-class cap / scope cap / co-sign rule / probation / restoration gate / authority receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1582-resilio-repromise-authority-credibility-budget-and-issuance-throttle-fragmentation-evaluation.md`
- `1583-repromise-authority-contract-sheet-page-trust-state-authority-class-and-approval-requirements-interface-spec.md`
- `1584-promise-issuance-review-page-autonomy-co-sign-required-throttled-and-blocked-routes-interface-spec.md`
- `1585-repromise-authority-proof-page-eligibility-window-credibility-budget-and-scope-cap-interface-spec.md`
- `1586-promise-authority-timeline-page-breach-downgrade-probation-restoration-and-suspension-events-interface-spec.md`
- `1587-promise-authority-lineage-receipt-page-authority-basis-scope-cap-and-restoration-gate-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's authority ingredients and operational candor**
- **do not clone Resilio's re-promise authority and issuance-throttle contract**

## Revision addendum after rev0405 — breach recovery, make-good, and trust-repair truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **post-breach recovery truth**.
It does eight things in one tranche:

1. Continues the archive after rev0405 with a new page family centered on what happens *after* a deadline was actually missed or breached and *before* a new promise should be allowed again.
2. Tightens the non-clone line again: borrow Resilio's candor that short performance windows, rescans, scheduler pauses, troubleshooting ladders, external locks, and log-capture escalation all shape post-miss recovery; refuse any contract where the operator still has to reconstruct `what is now owed, what original scope survived, what narrower remedy is allowed, and when trust is repaired enough for a new promise?` from scattered surfaces.
3. Adds one new **Resilio evaluation** document focused on why current recovery truth is still too fragmented to clone even though the ingredients are useful.
4. Adds five new **interface specs** for recovery commitment contract sheet, recovery-shaping review, breach recovery proof, recovery timeline, and recovery lineage receipt.
5. Makes one hard product decision explicit: **breach is weaker than recovery duty resolution.**
6. Makes another hard product decision explicit: **original promise, surviving obligation, make-good scope, and trust-repair status are different public truths.**
7. Makes a third hard product decision explicit: **motion restored is still weaker than re-promise eligible.**
8. Packages the result as another continuation archive whose new tranche makes the `breach basis / surviving obligation / make-good class / reduced-or-substitute scope / trust repair / re-promise gate / recovery receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1576-resilio-breach-recovery-make-good-and-trust-repair-fragmentation-evaluation.md`
- `1577-recovery-commitment-contract-sheet-page-breach-class-make-good-scope-and-repromise-gate-interface-spec.md`
- `1578-recovery-shaping-review-page-remedy-class-restored-scope-and-trust-requalification-routes-interface-spec.md`
- `1579-breach-recovery-proof-page-recovery-window-surviving-obligation-and-repromise-boundary-interface-spec.md`
- `1580-breach-recovery-timeline-page-breach-open-remedy-published-scope-restored-and-trust-repaired-events-interface-spec.md`
- `1581-breach-recovery-lineage-receipt-page-breach-class-remedy-scope-and-repromise-readiness-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's post-miss recovery ingredients and operational candor**
- **do not clone Resilio's breach-recovery and trust-repair contract**

## Revision addendum after rev0404 — deadline commitment, renegotiation, and breach truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **delivery-commitment truth**.
It does eight things in one tranche:

1. Continues the archive after rev0404 with a new page family centered on what happens *after* the product has an honest finish forecast but *before* that forecast should be treated as a real promise.
2. Tightens the non-clone line again: borrow Resilio's candor that short-window graphs, rescans, pause windows, hidden preprocessing, lock/source blockers, and restart-from-start risk all shape delivery confidence; refuse any contract where the operator still has to reconstruct `was this only a forecast, a target, a conditional promise, a hard commitment, or a breach?` from scattered surfaces.
3. Adds one new **Resilio evaluation** document focused on why current commitment truth is still too fragmented to clone even though the ingredients are useful.
4. Adds five new **interface specs** for delivery commitment contract sheet, commitment-quality review, commitment proof, commitment timeline, and commitment lineage receipt.
5. Makes one hard product decision explicit: **finish forecast is weaker than commitment.**
6. Makes another hard product decision explicit: **aspiration, target, conditional commitment, and hard commitment are different public truths.**
7. Makes a third hard product decision explicit: **invalidators, renegotiation triggers, miss, withdrawal, and breach must stay explicit instead of dissolving into vague `slipped` language.**
8. Packages the result as another continuation archive whose new tranche makes the `forecast basis / promise class / invalidators / breach boundary / surviving sentence / commitment receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1570-resilio-deadline-commitment-renegotiation-and-breach-fragmentation-evaluation.md`
- `1571-delivery-commitment-contract-sheet-page-forecast-basis-promise-conditions-and-breach-boundary-interface-spec.md`
- `1572-commitment-quality-review-page-promise-readiness-voiding-conditions-and-renegotiation-routes-interface-spec.md`
- `1573-delivery-commitment-proof-page-promise-window-risk-budget-and-surviving-sentence-interface-spec.md`
- `1574-delivery-commitment-timeline-page-promise-made-tightened-renegotiated-and-breached-events-interface-spec.md`
- `1575-delivery-commitment-lineage-receipt-page-promise-basis-voiding-conditions-and-breach-class-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's delivery-risk ingredients and operational candor**
- **do not clone Resilio's commitment, renegotiation, and breach contract**

## Revision addendum after rev0403 — finishability, ETA confidence, and forecast truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **completion-forecast truth**.
It does eight things in one tranche:

1. Continues the archive after rev0403 with a new page family centered on what happens *after* work has proved some real net progress but *before* the operator can honestly claim when it will finish.
2. Tightens the non-clone line again: borrow Resilio's candor that short-window graphs, rescans, schedule pauses, preprocessing, changed-piece transfer, whole-file re-sync risk, and locked or missing-source blockers are all forecast ingredients; refuse any contract where the operator still has to reconstruct `is this work honestly finishable soon, later, only after a checkpoint, or not forecastable yet?` from scattered metrics and settings.
3. Adds one new **Resilio evaluation** document focused on why current forecast truth is still too fragmented to clone even though the ingredients are useful.
4. Adds five new **interface specs** for completion forecast contract sheet, forecast-quality review, finish forecast proof, forecast timeline, and forecast lineage receipt.
5. Makes one hard product decision explicit: **net progress is weaker than finish forecast.**
6. Makes another hard product decision explicit: **finishability, ETA window, deadline confidence, and no-honest-forecast are different public truths.**
7. Makes a third hard product decision explicit: **hidden preprocessing, discovery lag, pause windows, and interruption/rework risk must count against forecast confidence instead of hiding behind throughput optimism.**
8. Packages the result as another continuation archive whose new tranche makes the `remaining obligation / finishability grade / ETA window / confidence-and-risk / deadline posture / forecast receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1564-resilio-finish-forecast-remaining-work-and-eta-confidence-fragmentation-evaluation.md`
- `1565-completion-forecast-contract-sheet-page-remaining-obligation-finishability-and-confidence-interface-spec.md`
- `1566-forecast-quality-review-page-finishability-eta-window-and-deadline-risk-routes-interface-spec.md`
- `1567-finish-forecast-proof-page-eta-window-finishability-grade-and-claim-ceiling-interface-spec.md`
- `1568-completion-forecast-timeline-page-estimate-tightening-slip-and-no-forecast-events-interface-spec.md`
- `1569-completion-forecast-lineage-receipt-page-forecast-basis-finishability-grade-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's forecast ingredients and operational candor**
- **do not clone Resilio's finishability and ETA-confidence contract**

## Revision addendum after rev0402 — net progress, churn, and no-net-gain truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **motion-versus-progress truth**.
It does eight things in one tranche:

1. Continues the archive after rev0402 with a new page family centered on what happens *after* work is alive and moving but *before* the operator can honestly say that the motion is buying real progress.
2. Tightens the non-clone line again: borrow Resilio's candor that graphs, queues, scans, hashes, merges, locked-file warnings, ghost-file warnings, and conflict warnings are all useful witnesses; refuse any contract where the operator still has to reconstruct `is this motion actually reducing the obligation, or only generating churn and new cleanup debt?` from scattered troubleshooting surfaces.
3. Adds one new **Resilio evaluation** document focused on why current progress-quality truth is still too fragmented to clone even though the motion signals are useful.
4. Adds five new **interface specs** for work progress contract sheet, progress-quality review, net-progress proof, progress timeline, and progress lineage receipt.
5. Makes one hard product decision explicit: **motion is weaker than meaningful advance.**
6. Makes another hard product decision explicit: **hashing, rescanning, merging, retrying, and queue motion may stay visible without being allowed to impersonate net progress.**
7. Makes a third hard product decision explicit: **a live heartbeat can still cross into no-net-gain churn, and that boundary must trigger an explicit reroute or rescue consequence.**
8. Packages the result as another continuation archive whose new tranche makes the `outstanding obligation / meaningful advance / churn budget / no-net-gain boundary / reroute owner / progress receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1558-resilio-motion-progress-churn-and-net-advance-fragmentation-evaluation.md`
- `1559-work-progress-contract-sheet-page-obligation-reduction-churn-signals-and-net-advance-interface-spec.md`
- `1560-progress-quality-review-page-meaningful-advance-retry-churn-and-no-net-gain-routes-interface-spec.md`
- `1561-net-progress-proof-page-obligation-reduction-churn-budget-and-claim-ceiling-interface-spec.md`
- `1562-work-progress-timeline-page-advance-retry-loop-churn-burst-and-net-gain-events-interface-spec.md`
- `1563-work-progress-lineage-receipt-page-progress-basis-churn-status-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's motion and troubleshooting signals**
- **do not clone Resilio's motion-as-progress and no-net-gain contract**

## Revision addendum after rev0401 — work heartbeat, stall, and rescue truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **claimed-work liveness truth**.
It does eight things in one tranche:

1. Continues the archive after rev0401 with a new page family centered on what happens *after* work has been dispatched and accepted but *before* the operator can honestly say that custody is still alive and progressing.
2. Tightens the non-clone line again: borrow Resilio's candor that status icons, peer counts, history, queues, performance graphs, watcher warnings, and internal-task warnings are useful motion signals; refuse any contract where the operator still has to reconstruct `is this accepted work actually moving, merely waiting healthily, blocked, silently stalled, or already in need of rescue?` from scattered status surfaces.
3. Adds one new **Resilio evaluation** document focused on why current work-progress truth is still too fragmented to clone even though the motion signals are useful.
4. Adds five new **interface specs** for work heartbeat contract sheet, heartbeat review, execution heartbeat proof, heartbeat timeline, and heartbeat lineage receipt.
5. Makes one hard product decision explicit: **accepted custody is weaker than verified progress.**
6. Makes another hard product decision explicit: **healthy wait, blocker-bound wait, silence window, and silent stall are different public truths.**
7. Makes a third hard product decision explicit: **last observed motion and next required heartbeat must stay separate, so quiet time never silently impersonates progress.**
8. Packages the result as another continuation archive whose new tranche makes the `claimed work / expected motion / allowed quiet window / heartbeat evidence / stall boundary / rescue route / liveness receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1552-resilio-work-heartbeat-stall-and-rescue-fragmentation-evaluation.md`
- `1553-work-heartbeat-contract-sheet-page-claimed-work-expected-motion-and-stall-boundary-interface-spec.md`
- `1554-progress-review-page-heartbeat-evidence-healthy-wait-blocker-and-stall-routes-interface-spec.md`
- `1555-execution-heartbeat-proof-page-motion-basis-silence-window-and-rescue-route-interface-spec.md`
- `1556-work-heartbeat-timeline-page-claim-start-progress-nudge-stall-and-rescue-events-interface-spec.md`
- `1557-work-heartbeat-lineage-receipt-page-heartbeat-status-stall-boundary-and-rescue-owner-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's motion and troubleshooting signals**
- **do not clone Resilio's claimed-work heartbeat and stall contract**

## Revision addendum after rev0400 — work claim, execution custody, and abandonment truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **dispatch-to-custody truth**.
It does eight things in one tranche:

1. Continues the archive after rev0400 with a new page family centered on what happens *after* a portfolio has selected the work that should go now but *before* the operator can honestly say that the work is actually owned.
2. Tightens the non-clone line again: borrow Resilio's candor that approval requests, requester identity details, permission levels, owner rights, linked-device approval flexibility, and notifications are all useful authority ingredients; refuse any contract where the operator still has to reconstruct `who actually claimed the dispatched work, what commitment window they accepted, when silence becomes abandonment, and how the work visibly returns if custody fails?` from scattered approval and permission surfaces.
3. Adds one new **Resilio evaluation** document focused on why current dispatch-to-custody truth is still too fragmented to clone even though the identity/authority ingredients are useful.
4. Adds five new **interface specs** for work claim contract sheet, claim acceptance review, execution custody proof, work claim timeline, and work claim lineage receipt.
5. Makes one hard product decision explicit: **winning dispatch is weaker than accepted custody.**
6. Makes another hard product decision explicit: **selected, notified, acknowledged, accepted, started, re-delegated, expired, and reclaimed are different public truths.**
7. Makes a third hard product decision explicit: **silence is never success; unclaimed or expired work must fall back into visible risk instead of disappearing behind a stale assignment.**
8. Packages the result as another continuation archive whose new tranche makes the `dispatch winner / requested custodian / commitment window / re-delegation boundary / expiry / reclaim / abandonment guard / custody receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1546-resilio-dispatch-claim-custody-and-abandonment-fragmentation-evaluation.md`
- `1547-work-claim-contract-sheet-page-dispatched-item-assignee-commitment-window-and-reclaim-rules-interface-spec.md`
- `1548-claim-acceptance-review-page-inform-request-accept-redelegate-and-decline-routes-interface-spec.md`
- `1549-execution-custody-proof-page-assignee-claim-expiry-and-safe-unclaim-interface-spec.md`
- `1550-work-claim-timeline-page-dispatch-claim-redelegate-expiry-and-reclaim-events-interface-spec.md`
- `1551-work-claim-lineage-receipt-page-custody-basis-commitment-window-and-abandonment-guard-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's identity, approval, and authority candor**
- **do not clone Resilio's dispatch-to-custody and abandonment contract**

## Revision addendum after rev0399 — decision portfolio, prioritization, and dispatch truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **cross-case decision portfolio truth**.
It does eight things in one tranche:

1. Continues the archive after rev0399 with a new page family centered on what happens *after* individual decisions become threshold-clear enough to matter but *before* the operator can honestly treat them as self-prioritizing.
2. Tightens the non-clone line again: borrow Resilio's candor that main-view filters, peer counts, notifications, warnings, history, and performance graphs are all useful attention signals; refuse any contract where the operator still has to reconstruct `which ready item goes now, which can safely wait, which watch-only item is quietly starving, and what preemption is justified?` from scattered surfaces.
3. Adds one new **Resilio evaluation** document focused on why current prioritization truth is still too fragmented to clone even though the signals are useful.
4. Adds five new **interface specs** for decision portfolio contract sheet, prioritization review, dispatch proof, portfolio timeline, and portfolio lineage receipt.
5. Makes one hard product decision explicit: **action-ready is not self-prioritizing.**
6. Makes another hard product decision explicit: **urgency, blast radius, reversibility, evidence freshness, and watch-starvation risk are different public truths.**
7. Makes a third hard product decision explicit: **a held or watch-only item must stay visible as deliberate debt, not disappear behind the item that won dispatch.**
8. Packages the result as another continuation archive whose new tranche makes the `candidate set / priority basis / attention budget / lane assignment / preemption / starvation guard / dispatch proof` seam explicit in the reading order and page family.

New docs in this tranche:

- `1540-resilio-decision-portfolio-prioritization-dispatch-and-starvation-fragmentation-evaluation.md`
- `1541-decision-portfolio-contract-sheet-page-candidate-set-urgency-lanes-and-attention-budget-interface-spec.md`
- `1542-prioritization-review-page-now-next-later-watch-and-preemption-routes-interface-spec.md`
- `1543-dispatch-proof-page-selected-work-held-work-and-starvation-guard-interface-spec.md`
- `1544-decision-portfolio-timeline-page-promotion-deferral-preemption-and-stale-watch-events-interface-spec.md`
- `1545-decision-portfolio-lineage-receipt-page-priority-basis-attention-budget-and-blocked-work-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's attention signals and troubleshooting candor**
- **do not clone Resilio's cross-case prioritization and dispatch contract**

## Revision addendum after rev0398 — evidence-to-decision thresholds, action charter, and escalation truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **evidence-to-decision truth**.
It does eight things in one tranche:

1. Continues the archive after rev0398 with a new page family centered on what happens *after* evidence has been synthesized but *before* the operator is allowed to act, publish, or escalate as though the answer were self-executing.
2. Tightens the non-clone line again: borrow Resilio's candor that warnings, history, peer state, graphs, logs, dumps, iperf runs, and troubleshooting ladders all matter; refuse any contract where the operator still has to reconstruct `what decision threshold is actually cleared, what stronger action is still blocked, and is the right next verb act, monitor, ask, defer, or escalate?` from scattered KB pages and support articles.
3. Adds one new **Resilio evaluation** document focused on why current decision-threshold truth is still too fragmented to clone even though the inputs are useful.
4. Adds five new **interface specs** for decision charter contract sheet, action-threshold review, decision proof, decision timeline, and decision lineage receipt.
5. Makes one hard product decision explicit: **a merged claim is not self-executing.**
6. Makes another hard product decision explicit: **claim ceiling, action threshold, and uncertainty budget are different public truths.**
7. Makes a third hard product decision explicit: **the same evidence can justify `monitor` while still failing `mutate`, or justify `escalate` while still failing `conclude`.**
8. Packages the result as another continuation archive whose new tranche makes the `synthesis / threshold / uncertainty budget / allowed action / blocked stronger action / escalation route` seam explicit in the reading order and page family.

New docs in this tranche:

- `1534-resilio-evidence-to-decision-threshold-action-and-escalation-fragmentation-evaluation.md`
- `1535-decision-charter-contract-sheet-page-target-action-threshold-and-residual-uncertainty-interface-spec.md`
- `1536-action-threshold-review-page-claim-ceiling-act-monitor-ask-and-escalate-routes-interface-spec.md`
- `1537-decision-proof-page-allowed-action-blocked-stronger-action-and-uncertainty-budget-interface-spec.md`
- `1538-decision-timeline-page-threshold-crossing-deferral-escalation-and-reopen-events-interface-spec.md`
- `1539-decision-lineage-receipt-page-action-basis-threshold-posture-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's evidence diversity and troubleshooting candor**
- **do not clone Resilio's evidence-to-decision and action-threshold contract**

## Revision addendum after rev0397 — evidence synthesis, corroboration, contradiction, and integrated-claim truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **evidence synthesis truth**.
It does eight things in one tranche:

1. Continues the archive after rev0397 with a new page family centered on what happens *after* packets have been received and intake-tested but *before* the operator is allowed to speak in one merged sentence.
2. Tightens the non-clone line again: borrow Resilio's candor that graphs, peer/state surfaces, history, notifications, logs, dumps, mobile captures, NAS artifacts, and iperf runs can all matter; refuse any contract where the operator still has to reconstruct `which packets are genuinely independent, which merely duplicate one another, which conflict, and what strongest integrated sentence survives all of them together?` from scattered support pages and UI fragments.
3. Adds one new **Resilio evaluation** document focused on why current evidence-synthesis truth is still too fragmented to clone even though the source artifacts are useful.
4. Adds five new **interface specs** for evidence synthesis contract sheet, corroboration/conflict review, integrated-claim proof, synthesis timeline, and synthesis lineage receipt.
5. Makes one hard product decision explicit: **multiple packets do not average into truth.**
6. Makes another hard product decision explicit: **duplicate support, independent corroboration, and contradiction stay separate.**
7. Makes a third hard product decision explicit: **one unresolved conflict can keep the stronger sentence blocked even when many weaker packets point the same way.**
8. Packages the result as another continuation archive whose new tranche makes the `packet set / independence / corroboration / contradiction / synthesis ceiling / unresolved conflict` seam explicit in the reading order and page family.

New docs in this tranche:

- `1528-resilio-evidence-synthesis-corroboration-contradiction-and-integrated-claim-fragmentation-evaluation.md`
- `1529-evidence-synthesis-contract-sheet-page-target-question-packet-set-and-weighted-basis-interface-spec.md`
- `1530-corroboration-and-conflict-review-page-independent-support-duplicates-and-unresolved-mismatch-interface-spec.md`
- `1531-integrated-claim-proof-page-merged-basis-open-conflicts-and-ceiling-interface-spec.md`
- `1532-evidence-synthesis-timeline-page-arrival-supersession-corroboration-conflict-and-claim-shift-events-interface-spec.md`
- `1533-evidence-synthesis-lineage-receipt-page-packet-set-weighted-basis-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's artifact diversity and troubleshooting candor**
- **do not clone Resilio's evidence-synthesis and integrated-claim contract**

## Revision addendum after rev0396 — evidence intake, sufficiency, and supplement-loop truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **evidence intake truth**.
It does eight things in one tranche:

1. Continues the archive after rev0396 with a new page family centered on what happens *after* an evidence packet has been exported and received but *before* the recipient is allowed to treat it as decision-grade.
2. Tightens the non-clone line again: borrow Resilio's candor that timestamps, peer roles, share names, reproduction windows, attachment limits, log rotation, dump classes, mobile hidden-log paths, NAS-local storage, and alternate channels all matter; refuse any contract where the recipient still has to reconstruct `is this packet decision-grade, what exact gap remains, and what cheapest supplement would raise the ceiling most?` from scattered support instructions.
3. Adds one new **Resilio evaluation** document focused on why current evidence-intake truth is still too fragmented to clone even though the capture/export ingredients are useful.
4. Adds five new **interface specs** for evidence intake contract sheet, intake sufficiency review, supplement request proof, intake timeline, and intake lineage receipt.
5. Makes one hard product decision explicit: **received, opened, validated, fit, and decision-grade are different states.**
6. Makes another hard product decision explicit: **a packet is sufficient only for a named target question, never in the abstract.**
7. Makes a third hard product decision explicit: **`send more logs` is not an acceptable supplement request unless it is the named cheapest useful ask.**
8. Packages the result as another continuation archive whose new tranche makes the `target question / packet fit / window fitness / open gaps / supplement loop / fallback claim` seam explicit in the reading order and page family.

New docs in this tranche:

- `1522-resilio-evidence-intake-sufficiency-and-supplement-loop-fragmentation-evaluation.md`
- `1523-evidence-intake-contract-sheet-page-target-claim-packet-fit-and-open-gaps-interface-spec.md`
- `1524-intake-sufficiency-review-page-open-validate-fit-grade-and-cheapest-supplement-interface-spec.md`
- `1525-supplement-request-proof-page-gap-target-cheapest-ask-and-new-ceiling-interface-spec.md`
- `1526-evidence-intake-timeline-page-arrival-validation-supplement-and-expiry-events-interface-spec.md`
- `1527-evidence-intake-lineage-receipt-page-sufficiency-grade-gap-status-and-fallback-claim-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's evidence-context candor and support-packet realism**
- **do not clone Resilio's evidence-intake and sufficiency contract**

## Revision addendum after rev0395 — evidence packet, custody, redaction, and export truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **evidence packet truth**.
It does eight things in one tranche:

1. Continues the archive after rev0395 with a new page family centered on what happens *after* a fact or artifact has been captured but *before* others are expected to rely on it.
2. Tightens the non-clone line again: borrow Resilio's candor that logs, dumps, mobile captures, NAS captures, feedback uploads, service-path variants, and support-routing details are all real evidence ingredients; refuse any contract where the operator still has to reconstruct `what exact artifact form are we sharing, what was redacted or transformed, which storage world produced it, and what integrity ceiling survives the export channel?` from scattered support pages.
3. Adds one new **Resilio evaluation** document focused on why current evidence-packet truth is still too fragmented to clone even though the capture instructions are useful.
4. Adds five new **interface specs** for evidence packet contract sheet, packet-shaping review, export proof, packet timeline, and packet lineage receipt.
5. Makes one hard product decision explicit: **raw capture, derived digest, redacted packet, and narrative summary are different objects.**
6. Makes another hard product decision explicit: **sent, received, opened, validated, and usable remain separate truths.**
7. Makes a third hard product decision explicit: **minimum-sufficient sharing is first-class, but every redaction or transformation must publish the diagnostic power it weakens.**
8. Packages the result as another continuation archive whose new tranche makes the `source artifact / redaction class / audience envelope / export integrity / recall boundary` seam explicit in the reading order and page family.

New docs in this tranche:

- `1516-resilio-evidence-packet-custody-redaction-and-export-fragmentation-evaluation.md`
- `1517-evidence-packet-contract-sheet-page-source-artifacts-redaction-class-and-audience-envelope-interface-spec.md`
- `1518-packet-shaping-review-page-raw-derived-redacted-and-minimum-sufficient-share-interface-spec.md`
- `1519-evidence-export-proof-page-sent-received-opened-validated-and-usable-interface-spec.md`
- `1520-evidence-packet-timeline-page-capture-redaction-export-recall-and-supersession-events-interface-spec.md`
- `1521-evidence-packet-lineage-receipt-page-custody-redaction-integrity-and-audience-boundary-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's evidence-capture candor and channel honesty**
- **do not clone Resilio's evidence-packet and custody contract**

## Revision addendum after rev0394 — discriminator acquisition, evidence burden, and question-order truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **discriminator acquisition**.
It does eight things in one tranche:

1. Continues the archive after rev0394 with a new page family centered on what happens *after* candidate doctrines and lookalikes are known but the decisive fact still has to be obtained.
2. Tightens the non-clone line again: borrow Resilio's candor that peer state, warnings, history, time checks, approval details, queue inspection, logs, and crash artifacts are all real evidence channels; refuse any contract where the operator still has to reconstruct `which fact is worth getting next, how much burden it costs, and whether heavier capture is actually justified yet` from scattered pages and support lore.
3. Adds one new **Resilio evaluation** document focused on why current evidence-acquisition truth is still too fragmented to clone even though the ingredients are useful.
4. Adds five new **interface specs** for discriminator acquisition contract sheet, evidence-priority review, fact-capture proof, acquisition timeline, and acquisition lineage receipt.
5. Makes one hard product decision explicit: **missing facts are not equal, and the cheapest highest-discriminator fact should usually win first.**
6. Makes another hard product decision explicit: **decision value, burden rung, and intrusion cost remain separate truths.**
7. Makes a third hard product decision explicit: **unavailable capture channels and declined heavy capture must weaken the safe sentence explicitly instead of disappearing into chat residue.**
8. Packages the result as another continuation archive whose new tranche makes the `candidate ask / burden ladder / fallback path / capture proof / blocked stronger sentence` seam explicit in the reading order and page family.

New docs in this tranche:

- `1510-resilio-discriminator-evidence-acquisition-burden-and-question-order-fragmentation-evaluation.md`
- `1511-discriminator-acquisition-contract-sheet-page-open-gaps-question-value-and-burden-interface-spec.md`
- `1512-discriminator-collection-review-page-cheapest-highest-signal-next-fact-and-intrusion-budget-interface-spec.md`
- `1513-fact-capture-proof-page-question-answered-evidence-quality-and-route-update-interface-spec.md`
- `1514-discriminator-acquisition-timeline-page-ask-skip-fail-escalate-and-burden-shift-events-interface-spec.md`
- `1515-discriminator-acquisition-lineage-receipt-page-discriminator-evidence-quality-burden-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's observational breadcrumbs and evidence candor**
- **do not clone Resilio's question-order and evidence-burden contract**

## Revision addendum after rev0393 — doctrine applicability, fact-pattern routing, and distinguishing-question truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **doctrine applicability**.
It does eight things in one tranche:

1. Continues the archive after rev0393 with a new page family centered on what happens when a fresh case arrives and the operator must decide *which precedent, if any, really governs it*.
2. Tightens the non-clone line again: borrow Resilio's candor that search, warning pages, troubleshooting pages, peer/status/history surfaces, and support/log breadcrumbs all help; refuse any contract where the operator still has to reconstruct `which doctrine applies to this fact pattern, which lookalikes are still plausible, and what one more fact would collapse the ambiguity fastest?` from scattered articles and memory.
3. Adds one new **Resilio evaluation** document focused on why current doctrine-application truth is still too fragmented to clone even though the warning articles and search affordances are useful.
4. Adds five new **interface specs** for doctrine applicability contract sheet, fact-pattern routing review, applicability proof, applicability timeline, and applicability lineage receipt.
5. Makes one hard product decision explicit: **published doctrine is not self-applying.**
6. Makes another hard product decision explicit: **symptom match, fact-pattern match, world match, and governing-doctrine match remain separate truths.**
7. Makes a third hard product decision explicit: **the next best distinguishing question is part of the operator product, not a support-artifact afterthought.**
8. Packages the result as another continuation archive whose new tranche makes the `candidate precedent / missing discriminator / route reversal / applicability receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1504-resilio-doctrine-applicability-fact-pattern-routing-and-distinguishing-question-fragmentation-evaluation.md`
- `1505-doctrine-applicability-contract-sheet-page-case-facts-candidate-precedents-and-missing-discriminators-interface-spec.md`
- `1506-fact-pattern-routing-review-page-symptom-lookalikes-disqualifiers-and-next-best-question-interface-spec.md`
- `1507-applicability-proof-page-governing-doctrine-distinction-gaps-and-safe-next-claim-interface-spec.md`
- `1508-applicability-timeline-page-facts-learned-candidates-promoted-and-route-reversal-events-interface-spec.md`
- `1509-applicability-lineage-receipt-page-fact-pattern-governing-doctrine-open-gaps-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's symptom catalog, search affordances, and troubleshooting candor**
- **do not clone Resilio's doctrine-application contract**

## Revision addendum after rev0392 — appeal, precedent, and doctrine consistency truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **appeal and precedent**.
It does eight things in one tranche:

1. Continues the archive after rev0392 with a new page family centered on what happens *after* a dispute verdict when the operator needs consistency across similar cases.
2. Tightens the non-clone line again: borrow Resilio's candor that warnings, KB explanations, troubleshooting trees, changelog fixes, and support/forum routing all carry real doctrine fragments; refuse any contract where the operator still has to reconstruct `which prior ruling should bind this case, when is it distinguishable, and when did a later version or fix overrule the old guidance?` from scattered articles and memory.
3. Adds one new **Resilio evaluation** document focused on why current precedent truth is still too fragmented to clone even though the symptom-specific guidance is useful.
4. Adds five new **interface specs** for precedent docket contract sheet, appeal-and-distinguish review, precedent proof, precedent timeline, and precedent lineage receipt.
5. Makes one hard product decision explicit: **a verdict is not yet doctrine merely because it happened once.**
6. Makes another hard product decision explicit: **binding, presumptive, persuasive, informative-only, and superseded guidance remain separate truths.**
7. Makes a third hard product decision explicit: **version drift, world mismatch, and later fixes can weaken old rulings without erasing their historical value.**
8. Packages the result as another continuation archive whose new tranche makes the `appeal / precedent / distinguish / overrule / sunset / doctrine receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1498-resilio-appeal-precedent-and-doctrine-fragmentation-evaluation.md`
- `1499-precedent-docket-contract-sheet-page-source-ruling-analogy-and-binding-weight-interface-spec.md`
- `1500-appeal-and-distinguish-review-page-binding-persuasive-overruled-and-version-scoped-doctrine-interface-spec.md`
- `1501-precedent-proof-page-doctrine-adopted-exception-allowed-and-overrule-path-interface-spec.md`
- `1502-precedent-timeline-page-ruling-appeal-overrule-sunset-and-version-drift-events-interface-spec.md`
- `1503-precedent-lineage-receipt-page-binding-weight-scope-version-window-and-overrule-boundary-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's symptom candor and version honesty**
- **do not clone Resilio's precedent contract**

## Revision addendum after rev0391 — completion dispute, counterevidence, and rework verdict truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **contested completion**.
It does eight things in one tranche:

1. Continues the archive after rev0391 with a new page family centered on what happens when a completion claim is challenged.
2. Tightens the non-clone line again: borrow Resilio's candor that green-check state, approval state, peer counts, history, disconnect aftermath, time-skew warnings, no-source-peer warnings, and file-conflict artifacts are all real witnesses; refuse any contract where the operator still has to reconstruct `which witness wins, what burden remains unmet, and whether the right result is uphold, narrow, overturn, or rework` from scattered pages and troubleshooting folklore.
3. Adds one new **Resilio evaluation** document focused on why current dispute truth is still too fragmented to clone even though the witness ingredients are useful.
4. Adds five new **interface specs** for completion dispute contract sheet, counterevidence adjudication review, dispute verdict proof, completion dispute timeline, and completion dispute lineage receipt.
5. Makes one hard product decision explicit: **accepted completion can still be challenged, and the challenge must freeze or narrow the stronger sentence visibly.**
6. Makes another hard product decision explicit: **green state, history activity, claimed completion, accepted completion, and adjudicated completion remain separate truths.**
7. Makes a third hard product decision explicit: **counterevidence must be typed, prioritized, and tied to a burden of proof; it may not dissolve into a generic `seems wrong` note.**
8. Packages the result as another continuation archive whose new tranche makes the `challenge / counterevidence / witness priority / verdict / rework / appeal` seam explicit in the reading order and page family.

New docs in this tranche:

- `1492-resilio-completion-dispute-counterevidence-and-rework-fragmentation-evaluation.md`
- `1493-completion-dispute-contract-sheet-page-claim-counterclaim-witness-and-burden-interface-spec.md`
- `1494-counterevidence-adjudication-review-page-green-state-history-gap-and-scope-mismatch-interface-spec.md`
- `1495-dispute-verdict-proof-page-uphold-overturn-partial-overturn-and-rework-interface-spec.md`
- `1496-completion-dispute-timeline-page-challenge-escalation-verdict-and-reopen-events-interface-spec.md`
- `1497-completion-dispute-lineage-receipt-page-verdict-burden-surviving-duty-and-appeal-boundary-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's witness candor**
- **do not clone Resilio's completion-dispute contract**

## Revision addendum after rev0390 — mandate fulfillment, returned evidence, and completion acceptance truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **fulfillment attestation**.
It does eight things in one tranche:

1. Continues the archive after rev0390 with a new page family centered on what comes back after authority was delegated.
2. Tightens the non-clone line again: borrow Resilio's candor that approval requests, requester fingerprints, notification bells, peer-list counts, history, green-check state, permission mutation, linked-device approval flexibility, and peer disconnect consequences are all real witnesses; refuse any contract where the operator still has to reconstruct `what exactly was claimed as done, what evidence came back, what part remains incomplete, and who actually accepted the return` from scattered surfaces.
3. Adds one new **Resilio evaluation** document focused on why current fulfillment truth is still too fragmented to clone even though the ingredients are useful.
4. Adds five new **interface specs** for fulfillment attestation contract sheet, execution return review, completion acceptance proof, fulfillment timeline, and fulfillment lineage receipt.
5. Makes one hard product decision explicit: **issued work is not fulfilled merely because the assignee says `done`.**
6. Makes another hard product decision explicit: **attempted, effect-observed, complete-self-claimed, accepted, and closed remain separate truths.**
7. Makes a third hard product decision explicit: **residual obligations survive accepted completion when the accepted scope is bounded, temporary, or side-effected.**
8. Packages the result as another continuation archive whose new tranche makes the `mandate / return / evidence / acceptance / residual-duty` seam explicit in the reading order and page family.

New docs in this tranche:

- `1486-resilio-mandate-fulfillment-attestation-evidence-and-acceptance-fragmentation-evaluation.md`
- `1487-fulfillment-attestation-contract-sheet-page-mandate-step-evidence-and-completion-class-interface-spec.md`
- `1488-execution-return-review-page-attempted-partial-complete-disputed-and-needs-acceptance-interface-spec.md`
- `1489-completion-acceptance-proof-page-finished-accepted-reopened-and-surviving-obligations-interface-spec.md`
- `1490-fulfillment-timeline-page-claim-review-acceptance-rejection-and-rework-events-interface-spec.md`
- `1491-fulfillment-lineage-receipt-page-completion-class-acceptance-state-and-residual-duty-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's witness candor**
- **do not clone Resilio's completion-acceptance contract**

## Revision addendum after rev0389 — reliance-to-action authority, delegated mandate, and cancellation truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **reliance versus action authority**.
It does eight things in one tranche:

1. Continues the archive after rev0389 with a new page family centered on how a received packet becomes, or does not become, downstream authority.
2. Tightens the non-clone line again: borrow Resilio's candor that permissions, invitation rights, approval checkpoints, requester fingerprints, folder-type differences, link expiry, use-count limits, revoke/disconnect, and linked-identity owner expansion are all real authority ingredients; refuse any contract where the operator still has to reconstruct `who may merely know, who may decide, who may execute, who may re-delegate, and how stale instructions die` from several separate pages and gestures.
3. Adds one new **Resilio evaluation** document focused on why current reliance-to-action truth is still too fragmented to clone even though the authority ingredients are useful.
4. Adds five new **interface specs** for action mandate contract sheet, mandate shaping review, action authority proof, mandate timeline, and mandate lineage receipt.
5. Makes one hard product decision explicit: **a reliance packet is not a work order.**
6. Makes another hard product decision explicit: **observe, approve, execute, escalate, and re-delegate remain separate truths.**
7. Makes a third hard product decision explicit: **queued or in-flight work must publish how supersession or cancellation changes what is still safe to do.**
8. Packages the result as another continuation archive whose new tranche makes the `authority / action-set / scope / expiry / cancellation / receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1480-resilio-reliance-to-action-authority-delegation-and-recall-fragmentation-evaluation.md`
- `1481-action-mandate-contract-sheet-page-authority-scope-duties-and-expiry-interface-spec.md`
- `1482-mandate-shaping-review-page-inform-observe-decide-execute-and-escalate-routing-interface-spec.md`
- `1483-action-authority-proof-page-issued-mandate-acceptance-execution-and-revocation-interface-spec.md`
- `1484-mandate-timeline-page-issue-acknowledgement-execution-supersession-and-cancel-events-interface-spec.md`
- `1485-mandate-lineage-receipt-page-authority-scope-duty-state-and-recall-boundary-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's reliance-to-action contract**

## Revision addendum after rev0388 — certification publication, audience reliance, and recall truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **publication for reliance**.
It does eight things in one tranche:

1. Continues the archive after rev0388 with a new page family centered on who may safely act on a certification.
2. Tightens the non-clone line again: borrow Resilio's candor that UI state, history, build/version surfaces, debug logs, crash artifacts, support/forum lanes, mobile support, NAS log paths, config worlds, and mixed-version/device-world warnings are different evidence ingredients; refuse any contract where the operator still has to reconstruct `what exact sentence is safe for this audience to rely on, and how do we supersede or recall it later?` from several pages and ad hoc packets.
3. Adds one new **Resilio evaluation** document focused on why current publication and audience-reliance truth is still too fragmented to clone even though the evidence ingredients are useful.
4. Adds five new **interface specs** for reliance charter contract sheet, publication review, reliance proof, reliance timeline, and reliance lineage receipt.
5. Makes one hard product decision explicit: **a certificate is not self-executing; it becomes operational only through an audience-specific reliance charter.**
6. Makes another hard product decision explicit: **delivery, receipt, understanding, delegated custody, supersession, and recall are different public truths.**
7. Makes a third hard product decision explicit: **a stale forwarded snapshot is weaker than a live-linked packet, and `sent` is weaker than `safe to rely on`.**
8. Packages the result as another continuation archive whose new tranche makes the `audience / claim-envelope / publication-review / reliance-proof / recall-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1474-resilio-certification-publication-audience-reliance-and-recall-fragmentation-evaluation.md`
- `1475-reliance-charter-contract-sheet-page-audience-claim-envelope-and-recall-channel-interface-spec.md`
- `1476-certification-publication-review-page-operator-exec-audit-and-successor-handoff-variants-interface-spec.md`
- `1477-reliance-proof-page-published-claims-obligations-and-supersession-interface-spec.md`
- `1478-reliance-timeline-page-publication-acknowledgement-supersession-and-recall-events-interface-spec.md`
- `1479-reliance-lineage-receipt-page-audience-envelope-freshness-and-recall-boundary-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's publication-for-reliance contract**

This time the reason is especially clear around **UI summary state, 30-day history, version/about witness, debug-log capture rituals, crash/core-dump collection, support-lane splits, mobile support surfaces, config-world attribution, and mixed-version handoff warnings**.
Current official materials simultaneously show that:

- current `Sync Main View (Desktop)` docs still say the UI exposes filters, search, columns, a 30-day History lane, and settings/license details
- current `Collecting debug logs automatically` docs still say debug capture may require enablement, restart, and at least 15 minutes of post-repro collection
- current `Collecting debug logs manually` docs still say Business customers have direct technical support while Sync v3 users are pushed toward the forum / Help Center plus a separate payments/licensing form
- the same manual log docs still say artifact locations vary across desktop, service principals, Linux storage paths, NAS, and Android
- current `Collecting crash reports, mini-dumps and core dumps` and `Where to collect logs on NAS?` docs still preserve platform-specific evidence lanes
- current `Settings on mobile platforms` docs still separate Support links from About/build witness on mobile
- current `Running Sync in configuration mode` docs still say config can apply the same settings on many machines while non-default `storage_path` creates a new settings world
- current `Sync Private Identity & Linking My Devices` docs still warn against linking v2 and v3 devices because of license/application conflicts and lost UI / share configuration access

That candor is useful.
The publication-for-reliance contract is the problem.
AnonSync should not clone a world where the operator still has to translate `dashboard looks green`, `history looks quiet`, `here are the logs`, `here is the build`, `forum vs support`, and `this came from that machine/world` into one stable answer about audience, safe sentence, exclusions, freshness, supersession, recall channel, and blocked stronger sentence by stitching together several pages and ad hoc packets.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because publication is a real contract with separate truths for audience, claim envelope, evidence payload, freshness, supersession, and recall, but the present contract still scatters the answer to `what exact sentence is safe for this audience to rely on, and how do we retract or supersede it later?` across several KB articles and improvised evidence packets instead of owning it as one stable page family.**

## Revision addendum — estate certification, explicit exclusions, and revocation truth after rev0387

This pass locks the next seam after convergence campaigns and bounded settlement truth: **how to certify that a meaningful estate is back in bounds without turning campaign closure into a false universal green badge**.
The archive already knew how to settle many changed returns honestly.
What it still lacked was one explicit answer to:

> after the cleanup waves, what exact scope can we now certify, what remains explicitly outside that certificate, how fresh is the proof, and what event revokes the stronger sentence later?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on why current estate confidence still fragments across folders view, search, history, disconnected-folder visibility, configuration mode, service-world forks, mobile settings, and permission/disconnect state instead of one durable certification object
- five new **interface specs** for estate certification contract sheet, certification shaping review, certification proof, certification timeline, and certification lineage receipt
- a tighter non-clone line based on current official Resilio evidence that operators can inspect many useful surfaces today but still have to synthesize estate certification manually
- five hard product decisions:
  - **campaign success does not automatically mint estate certification**
  - **every certificate must publish exact scope and explicit exclusions**
  - **bounded certification is a legitimate truth and should stay bounded**
  - **freshness and revocation are part of the certificate, not later footnotes**
  - **the stronger sentence must shrink or die when scope changes, evidence stales, or a world fork appears**

New docs in this tranche:

- `1468-resilio-estate-certification-scope-exclusion-and-freshness-fragmentation-evaluation.md`
- `1469-estate-certification-contract-sheet-page-scope-exclusions-and-freshness-target-interface-spec.md`
- `1470-estate-certification-shaping-review-page-covered-bounded-excluded-and-blocking-scope-interface-spec.md`
- `1471-estate-certification-proof-page-certified-scope-freshness-and-revocation-triggers-interface-spec.md`
- `1472-estate-certification-timeline-page-scope-change-freshness-renewal-and-revocation-events-interface-spec.md`
- `1473-estate-certification-lineage-receipt-page-certified-scope-exclusions-and-revocation-boundary-interface-spec.md`

### Why this pass matters

The previous tranche answered `how to settle many parity debts without lying about stragglers`.
This tranche answers the next harder question:

> `after those campaigns, what exact estate scope can we now honestly certify as back in bounds, what remains outside that certificate, and when does that confidence silently expire or revoke?`

Current official Resilio material is useful here because it already proves that certification work is real, but still fragmented:

- the desktop main view still offers filters, search, columns, peer counts, and a 30-day History lane
- green check still means synced with connected peers, which is useful but narrower than estate-wide truth
- disconnected folders can still remain visible with no local path
- search still spans folders, shared files, connected devices, and users
- configuration mode can still apply the same settings to many machines while also allowing a non-default `storage_path` to create a different settings world
- switching the Windows service to `Local System` can still create a new storage world with no old folders present until they are re-added or reconnected
- mobile settings still live on their own lane with separate operating controls
- peer disconnect can still leave old bytes present while future updates are suspended

That candor is worth borrowing.
The contract shape is not.
AnonSync should not clone a world where an operator still has to reconstruct estate certification from many useful but separate surfaces.

## Revision addendum — return-delta convergence, cohort settlement, and straggler truth after rev0386

This pass locks the next seam after return-delta debt and baseline rebind: **how to settle many changed-but-working states as a group without silently promoting drift or hiding the subjects that still block the stronger sentence**.
The archive already knew how to make one tolerated mismatch explicit.
What it still lacked was one explicit answer to:

> once many return deltas exist at once, how do we shape a settlement wave, route each subject honestly, publish stragglers, and upgrade claims only for the scope actually proved?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on why current convergence truth still fragments across per-folder disconnect/reconnect, default-mode placement, manual path choice, existing-directory merge, folder-not-empty risk, local-only rename/move constraints, peer-right drift, and config-mode parameter distribution instead of one durable convergence campaign object
- five new **interface specs** for convergence campaign contract sheet, convergence shaping review, convergence proof, convergence timeline, and convergence lineage receipt
- a tighter non-clone line based on current official Resilio evidence that multi-subject settlement today is real work but still lives mostly as repeated per-share memory and one-off routing rather than one operator-facing settlement truth
- five hard product decisions:
  - **many tolerated deltas become a first-class convergence campaign once they are being judged as one success story**
  - **every subject in the campaign must route explicitly to exact restore, successor promotion, temporary keep, split-out, or reopen**
  - **partial success may upgrade claims only for the scope actually settled**
  - **stragglers remain first-class objects and cannot be averaged away**
  - **cohort success is a proof-and-scope statement, not a vibes statement**

New docs in this tranche:

- `1462-resilio-return-delta-convergence-cohort-settlement-and-straggler-truth-evaluation.md`
- `1463-convergence-campaign-contract-sheet-page-debt-cohort-target-end-state-and-safety-fences-interface-spec.md`
- `1464-convergence-shaping-review-page-restore-promote-split-and-reopen-routing-interface-spec.md`
- `1465-convergence-proof-page-wave-progress-settlement-class-and-claim-upgrade-interface-spec.md`
- `1466-convergence-timeline-page-wave-entry-reconciliation-settlement-and-straggler-events-interface-spec.md`
- `1467-convergence-lineage-receipt-page-cohort-settlement-coverage-and-blocked-stronger-sentences-interface-spec.md`

### Why this pass matters

The previous tranche answered `when one changed active state is debt, successor, or reopen-worthy`.
This tranche answers the next harder question:

> `when there are many such states, how do we settle them together without lying about coverage, hiding stragglers, or silently rounding a bounded win up to family-wide success?`

Current official Resilio material is useful here because it already proves that convergence is real, but still fragmented:

- duplicate `(1)` folders are still fixed through per-folder disconnect/reconnect and manual repointing
- Disconnected mode and Android Simple mode still govern whether custom placement is possible for future arrivals
- existing-directory connection still routes through folder-specific merge and non-empty-folder confirmation
- reconnect can still create new paths and structural forks
- move/rename rules can still stay local or require disconnect/reconnect
- peer disconnect can still leave bytes present while future-update rights diverge
- configuration mode can still apply settings across multiple machines without becoming a settlement campaign for already drifted live subjects

That candor is worth borrowing.
The contract shape is not.
AnonSync should not clone a world where the operator still has to reconstruct cohort settlement truth out of repeated folder mechanics and memory.

## Revision addendum — return-delta debt, baseline rebind, and honest successor adoption after rev0385

This pass locks the next seam after control re-arm and return-to-protection: **what to do when the system comes back in a changed-but-working state that is operationally acceptable for a while but not yet the same protected state as before**.
The archive already knew how to suspend controls, bring them back, and keep motion restoration separate from trust restoration.
What it still lacked was one explicit answer to:

> when a changed return keeps working, is that state temporary debt, a deliberate successor baseline, or an unresolved mismatch that must reopen later?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on why current post-return truth still fragments across reconnect path changes, duplicate `(1)` folders, mode/default-location behavior, existing-directory merges, folder-not-empty risks, local-only renames, move/reconnect boundaries, and peer-rights drift instead of one durable return-delta contract
- five new **interface specs** for return-delta contract sheet, delta-aging review, parity-debt proof, return-delta timeline, and return-delta lineage receipt
- a tighter non-clone line based on current official Resilio evidence that a state can be visibly active and still differ materially from the old intended home, mode, witness, or rights posture
- five hard product decisions:
  - **a changed-but-working return becomes explicit parity debt unless it is deliberately promoted**
  - **temporary accepted delta and successor baseline are separate truths**
  - **every tolerated mismatch requires owner, expiry, and rereview cadence**
  - **time and usage alone may not silently promote a changed state to the new baseline**
  - **`still syncing` is weaker than `same protected state` and must stay weaker until proof or promotion says otherwise**

New docs in this tranche:

- `1456-resilio-return-delta-debt-baseline-rebind-and-reopen-fragmentation-evaluation.md`
- `1457-return-delta-contract-sheet-page-accepted-successor-delta-expiry-and-owner-interface-spec.md`
- `1458-delta-aging-review-page-restore-exact-promote-successor-or-reopen-interface-spec.md`
- `1459-parity-debt-proof-page-temporary-accepted-delta-baseline-rebind-and-claim-ceiling-interface-spec.md`
- `1460-return-delta-timeline-page-accepted-drift-expiry-promotion-and-reopen-events-interface-spec.md`
- `1461-return-delta-lineage-receipt-page-parity-debt-owner-expiry-and-blocked-stronger-sentences-interface-spec.md`

### Why this pass matters

The previous tranche answered `did we actually bring protection back, and what structural delta still remains?`
This tranche answers the next harder question:

> `if we keep operating in that changed state, when does it become a debt with an owner and expiry, when can it honestly become the new baseline, and when must it reopen instead of being normalized?`

Current official Resilio material is useful here because it already proves that changed-but-working returns are real:

- reconnect may propose a different default path, create a new directory, and append `(1)` when a same-name folder already exists
- Selective Sync or Synced default-mode behavior can auto-place arriving folders into the default storage location until the operator switches the device into Disconnected mode for manual placement
- disabling Android Simple mode changes whether custom path choice is available at connect time
- disconnected folders have no local path while Selective Sync and Full Sync preserve different local witness shapes
- existing-directory connect merges trees and resolves same-name different-hash files by latest timestamp
- reconnecting to or adding into a non-empty folder can overwrite or delete already-present files
- renaming a syncing folder is local-only while moving across partitions can require disconnect/reconnect
- peer disconnect can leave bytes in place while future updates remain suspended

That candor is worth borrowing.
The contract shape is not.
AnonSync should not clone a world where the operator still has to infer, from scattered KB pages, whether a changed return is temporary debt, an intentional successor, or a problem that should reopen.

## Revision addendum — control re-arm, return-to-protection, and post-bypass reconciliation after rev0384

This pass locks the next seam after control suspension and break-glass: **how protection actually comes back after a bypass ends, and how we distinguish motion restored from the same protected state restored**.
The archive already knew how to attest a control, suspend it truthfully, and preserve what still survives while it is weakened.
What it still lacked was one explicit answer to:

> after we unpause, reconnect, reattach, or restore permissions, are we truly back to the same protected state, what structural deltas remain, and what proof is still required before the stronger sentence returns?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on why current re-entry truth still fragments across resume, reconnect, disconnected-mode connect, existing-directory merge, placeholder behavior, path defaults, Android Simple mode, and permission restoration instead of one durable return-to-protection contract
- five new **interface specs** for return-to-protection contract sheet, re-arm readiness review, return proof, post-bypass reconciliation timeline, and return-to-protection lineage receipt
- a tighter non-clone line based on current official Resilio evidence that several current `come back` verbs are materially different but still do not become one operator-facing answer to `did we actually recreate the same protected state or only restart activity in a changed one?`
- five hard product decisions:
  - **`resumed`, `reconnected`, `reattached`, `merged`, and `requalified` remain separate states**
  - **every return must publish structural deltas, not just the fact that motion resumed**
  - **same-path restoration and accepted-successor return are separate truths**
  - **connect-to-existing-directory and new-path reconnect are reconciliation events, not simple resumes**
  - **the strongest pre-bypass sentence stays blocked until requalification closes the remaining delta**

New docs in this tranche:

- `1450-resilio-control-rearm-return-to-protection-and-post-bypass-reconciliation-fragmentation-evaluation.md`
- `1451-return-to-protection-contract-sheet-page-intended-restoration-structural-delta-and-return-class-interface-spec.md`
- `1452-rearm-readiness-review-page-path-mode-peer-and-placeholder-reconciliation-interface-spec.md`
- `1453-return-to-protection-proof-page-resume-reconnect-rebind-and-requalification-interface-spec.md`
- `1454-post-bypass-reconciliation-timeline-page-resume-path-fork-merge-and-trust-return-events-interface-spec.md`
- `1455-return-to-protection-lineage-receipt-page-rearm-class-residual-delta-and-blocked-stronger-sentences-interface-spec.md`

### Why this pass matters

The previous tranche answered `what still survives while the control is bypassed?`
This tranche answers the next harder question:

> `when activity comes back, are we really back to the same protected state, or did we return through a path/mode/topology change that still blocks the stronger claim?`

Current official Resilio material is useful here because it already proves that re-entry is not one thing:

- `How to pause syncing` still says resume is just repeating the same action, which is a cheap same-surface return
- `Sync Preferences` still says Global Pause/Resume applies only to shares not already paused individually, exposing re-entry ownership by surface
- `Disconnecting and Removing Folders` still says reconnect may propose a different default path, may create a new directory, and may append `(1)` if a same-name folder exists
- `Synchronization Modes` still says disconnected folders have no local path until connect, while Selective Sync returns placeholder-only posture instead of full local bytes
- `How to manually set the location of the folders synced across linked devices?` still says Disconnected mode enables path choice at connect time, while Android Simple mode must be disabled to choose location manually
- `Can I connect two pre-populated pre-existing folders?` still says connecting to an existing directory merges trees, skips same-hash files, and resolves same-name different-hash files by latest timestamp
- `Selective Sync` still warns that removing a Selective Sync share removes all placeholders from the local file system
- `User Management` still says peer disconnect suspends future updates while already-synchronized files remain

That candor is useful.
The contract shape is the problem.
AnonSync should not clone a world where several return-like states exist but the product still cannot answer in one place:

- whether the return reused the same path or silently forked it
- whether the return recreated full local witness state or only placeholder posture
- whether the return merged into an existing directory and therefore changed proof obligations
- whether permission or future-update rights actually match the old state
- whether motion resumed, protection resumed, or a weaker successor state was merely accepted

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because return-to-protection is a real contract with separate truths for motion restoration, path/topology/permission parity, merge-versus-resume behavior, accepted structural delta, and trust requalification, but the present contract still scatters the answer across resume guides, disconnect/reconnect notes, synchronization modes, path-choice articles, and merge workflows instead of owning it as one stable page family.**

## Revision addendum — control suspension, break-glass, and truth-preserving stop semantics after rev0383

This pass locks the next seam after control trust and attestation: **how a trusted control is intentionally suspended, narrowed, or bypassed without lying about what is still happening underneath**.
The archive already knew how to promote a control, attest it, rehearse it, and withdraw trust on drift.
What it still lacked was one explicit answer to:

> if we have to stop or weaken this protection for a while, what exactly stops, what still continues, when does it resume, and what must be re-proved before we can safely overclaim protection again?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on why current stop semantics still fragment across pause, scheduler pause, disconnect/remove, synchronization modes, per-share network gates, mobile/system-mediated stops, and peer revocation instead of one durable suspension contract
- five new **interface specs** for control suspension contract sheet, bypass review, suspension proof, stop-semantic timeline, and suspension-lineage receipt
- a tighter non-clone line based on current official Resilio evidence that several current `stop` verbs are materially different but still do not become one operator-facing answer to `what is actually suspended, what survives, and what restores trust later?`
- five hard product decisions:
  - **`paused`, `stopped`, `disconnected`, `detached`, and `revoked` remain separate states**
  - **every active bypass must publish surviving effects, not just requested effects**
  - **resume availability and trust restoration are separate truths**
  - **overstayed bypasses automatically worsen posture even without a visible incident**
  - **temporary control suspension must preserve the next forbidden overclaim**

New docs in this tranche:

- `1444-resilio-control-suspension-break-glass-and-stop-semantic-fragmentation-evaluation.md`
- `1445-control-suspension-contract-sheet-page-requested-effect-surviving-effects-and-resume-class-interface-spec.md`
- `1446-bypass-review-page-pause-disconnect-network-gate-and-claim-downgrade-interface-spec.md`
- `1447-suspension-proof-page-approved-bypass-surviving-propagation-and-rearm-conditions-interface-spec.md`
- `1448-stop-semantic-timeline-page-pause-entry-auto-resume-detach-and-trust-restoration-interface-spec.md`
- `1449-suspension-lineage-receipt-page-active-bypass-surviving-effects-and-next-rearm-proof-interface-spec.md`

### Why this pass matters

The previous tranche answered `why do we still trust this guardrail now?`
This tranche answers the next harder question:

> `when we intentionally weaken or suspend the guardrail for a while, what exactly is still happening, and what evidence is required before full trust can be said to have returned?`

Current official Resilio material is useful here because it already proves that stop semantics differ materially:

- `How to pause syncing` still says pause lets zero-sized files sync, deletions sync, and rescans/indexing continue
- `Sync Preferences` still says Global Pause affects only shares that are not paused individually
- `Running Sync on schedule` still says scheduled `Paused` keeps deletions and rescans alive and can still allow uploads to non-paused peers
- `Disconnecting and Removing Folders` still distinguishes disconnect from remove and says reconnect may propose a different default path
- `Synchronization Modes` still distinguishes disconnected state, placeholder-only local removal, and remove-from-all-devices behavior
- `Setting network interface per share` still says `Stopped. Forbidden network` blocks peer connection and new/update detection for that share
- `Settings on mobile platforms` still says some system/lane settings can force background stop behavior
- `User Management` still says peer disconnect suspends future updates while keeping already-synced files

That candor is useful.
The contract shape is the problem.
AnonSync should not clone a world where several stop-like states exist but the product still cannot answer in one place:

- what exact effect was requested
- what exact effect actually survives underneath
- whether the stop auto-resumes, requires reconnect, or requires re-add
- whether the bypass narrowed coverage, detached topology, or revoked peer relationship
- what stronger sentence stays blocked even after visible activity resumes

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because stop semantics are a real contract with separate truths for requested suppression, surviving propagation, scope, expiry, auto-resume, reconnect cost, and trust restoration, but the present contract still scatters the answer across pause pages, scheduler rules, disconnect/remove guides, network-gate notes, mobile background settings, and peer-permission routes instead of owning it as one stable page family.**

## Revision addendum — guardrail attestation, rehearsal, and silent trust decay after rev0382

This pass locks the next seam after case-to-guardrail promotion: **why an active guardrail is still trusted later, especially when no fresh incident has happened yet**.
The archive already knew how to promote a control, activate it, and watch for recurrence.
What it still lacked was one explicit answer to:

> what proves this control is still real right now, what kind of witness is strong enough, and what event silently withdraws that trust before the next painful repeat?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on why current control truth still fragments across power-user settings, folder preferences, config mode, service mode, mobile settings, scheduler, LAN-only instructions, restart requirements, and world-fork notes rather than one durable attestation workflow
- five new **interface specs** for control attestation contract sheet, attestation review, rehearsal proof, control-decay timeline, and attestation-lineage receipt
- a tighter non-clone line based on current official Resilio evidence that a careful operator can configure many real controls, but still has to reconstruct `do we still trust this control now, and why?` from scattered surfaces and KB memory
- five hard product decisions:
  - **configured, active, and trusted remain separate states**
  - **every meaningful control must publish at least one witness stronger than `visible setting value`**
  - **passive quiet windows may renew freshness but may not magically upgrade a control into stronger prevention**
  - **missed attestation, version drift, world forks, ignored settings, and prerequisite loss can withdraw trust even without a visible incident**
  - **some controls require synthetic rehearsal or paired-surface attestation instead of waiting for a real repeat**

New docs in this tranche:

- `1438-resilio-control-attestation-rehearsal-and-silent-decay-fragmentation-evaluation.md`
- `1439-control-attestation-contract-sheet-page-mechanism-prerequisite-and-witness-class-interface-spec.md`
- `1440-attestation-review-page-live-check-synthetic-drill-passive-witness-and-claim-ceiling-interface-spec.md`
- `1441-control-rehearsal-proof-page-drill-scope-observed-barrier-and-stale-trust-withdrawal-interface-spec.md`
- `1442-control-decay-timeline-page-version-drift-world-fork-missed-check-and-trust-loss-interface-spec.md`
- `1443-control-attestation-lineage-receipt-page-latest-proof-mechanism-and-blocked-stronger-sentences-interface-spec.md`

### Why this pass matters

The previous tranche answered `what durable guardrail did the case teach us to create?`
This tranche answers the next harder question:

> `why do we still trust that guardrail now, and what exact event makes that trust stale or false before the next big escape teaches us the hard way?`

Current official Resilio material is useful here because it already proves that control truth is often multi-surface, version-sensitive, world-sensitive, and restart-sensitive:

- `Power user preferences` still says the page is for the latest version, warns older versions may miss or deprecate settings, marks at least one setting as ignored in Linux WebUI, and still has restart-bound options
- `Folder Preferences` still says the page is desktop-only
- the LAN-only article still requires changes in both share preferences and power-user settings plus restart, and even documents cached peer-state cleanup when internet paths were learned earlier
- `Running Sync in configuration mode` still says the same settings can be applied across machines, but also says a non-default `storage_path` creates a new settings world, config mode can set up only Standard folders, and config-authored shared folders disable WebUI and override prior WebUI folders
- `Running Sync as a service on Windows` still distinguishes migrated settings from clean-install service worlds
- `Sync Service Troubleshooting on Windows` still says switching to `Local System` requires restart and creates a new storage folder with no old added folders present
- `Settings on mobile platforms` still shows separate mobile-only controls and Android `Simple mode`
- `Running Sync on schedule` still exposes a version/licensing-bound scheduler in Sync Preferences -> Advanced

That candor is useful.
The contract shape is the problem.
AnonSync should not clone a world where a control can be visible, named, and even apparently active, yet the product still cannot answer in one place:

- what last proved the control is still trustworthy
- whether that proof is fresh or stale
- whether a synthetic drill is required
- whether a version change or world fork silently withdrew the old claim
- what stronger sentence is still blocked even after the latest proof

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because control trust is a real contract with separate truths for mechanism, prerequisites, witness class, proof freshness, rehearsal duty, decay pressure, and trust withdrawal, but the present contract still scatters the answer to `do we still trust this control right now, and why?` across settings pages, config/service notes, mobile-vs-desktop lanes, and KB memory instead of owning it as one stable page family.**

## Revision addendum — case-to-guardrail promotion, preventive controls, and recurrence watch after rev0381

This pass locks the next seam after honest case closure: **what durable control or watch do we promote from the case so the result becomes operational truth instead of folklore?**
The archive already knew how to choose a fix, run it safely, and close the case honestly.
What it still lacked was one explicit answer to:

> what permanent guardrail, watch, or capture-on-repeat runbook did this case teach us to create, what exact hazard is it for, and what stronger prevention claim is still blocked?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on why current prevention ingredients still live across watcher-limit KBs, scheduler/settings pages, power-user preferences, config mode, service setup, live graphs, and changelog memory rather than one durable case-to-control workflow
- five new **interface specs** for preventive control contract sheet, control promotion review, control activation proof, recurrence watch timeline, and control-lineage receipt
- a tighter non-clone line based on current official Resilio evidence that a careful operator can discover many real guardrail ingredients but still has to reconstruct `what did we permanently change because of this case, what does it cover, and how will we know if it escaped?` from several separate surfaces
- five hard product decisions:
  - **every non-trivial closed case must end in a typed guardrail verdict: preventive control, detective watch, containment control, capture-on-repeat runbook, non-preventable, or accepted risk**
  - **prevent, detect, contain, and merely explain remain separate control classes**
  - **every active control must publish coverage, prerequisites, and at least one explicit anti-claim**
  - **quiet windows, near misses, repeats caught early, repeats contained, and repeats truly prevented remain separate evidence rungs**
  - **version drift, world forks, and same-cause escapes automatically downgrade the strongest safe preventive sentence**

New docs in this tranche:

- `1432-resilio-case-promotion-preventive-control-and-recurrence-watch-fragmentation-evaluation.md`
- `1433-preventive-control-contract-sheet-page-source-case-hazard-signature-and-coverage-scope-interface-spec.md`
- `1434-control-promotion-review-page-prevent-detect-mitigate-watch-and-no-control-verdict-interface-spec.md`
- `1435-control-activation-proof-page-rollout-owner-rereview-and-does-not-protect-interface-spec.md`
- `1436-recurrence-watch-timeline-page-near-miss-repeat-prevented-event-and-control-drift-interface-spec.md`
- `1437-control-lineage-receipt-page-case-origin-coverage-class-and-blocked-stronger-sentences-interface-spec.md`

### Why this pass matters

The previous tranche answered `what do we now believe, and is closure honest?`
This tranche answers the next harder question:

> `what will stop us from relearning the same case the hard way, and how honest are we about what that new guardrail does not prevent?`

Current official Resilio material is useful here because it already contains real prevention ingredients, but still diffusely for a clone.
The clearest current cluster is:

- `Agent run out of system notify watchers` still distinguishes temporary vs persistent environment tuning and still requires restart after the persistent `sysctl.conf` path
- `Some internal tasks are taking time to complete` still blocks premature `fix everything` reactions by admitting self-recovery and background work
- `Collecting debug logs automatically` still makes artifact capture a real repeatable runbook with enablement, restart, reproduction, and post-repro wait steps
- `Running Sync on schedule`, `Power user preferences`, `Running Sync in configuration mode`, and the LAN-only article still expose real guardrail ingredients, but across different settings worlds and apply requirements
- `Running Sync as a service on Windows` still preserves world forks through migrate-vs-clean service installation
- `Performance overview` still keeps live observation short-windowed rather than turning it into durable recurrence truth
- the current change log still shows these guardrail ingredients arriving piecemeal across warnings, power-user settings, force-rescan support, ignore-list changes, memory/error reporting, and other fixes

That candor is useful.
The contract shape is the problem.
AnonSync should not clone a world where a team can troubleshoot carefully and even change the right setting, yet still lacks one durable answer to:

- which case justified this control
- whether it prevents, detects, contains, or only guides
- what worlds and versions it really covers
- what it explicitly does not protect
- what evidence would prove the control escaped later

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because post-case learning is a real contract with separate truths for hazard signature, protection class, scope, prerequisites, anti-claims, effectiveness watch, and escape accounting, but the present contract still scatters the answer to `what did we permanently change because of this case, what does it truly cover, and how would we know it failed?` across KB articles, settings surfaces, and changelog memory instead of owning it as one stable page family.**

## Revision addendum — incident case truth, root-cause adjudication, and honest closure after rev0380

This pass locks the next seam after remediation execution: **case reasoning and closure truth**.
The archive already knew how to choose and run a corrective action.
What it still lacked was one explicit answer to:

> after the run, what do we now believe caused the problem, what did we rule out, what remains unknown, how honest is closure, and what exact event should reopen the case later?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on why current cause reasoning and closure still live across warnings, history, queues, logs, and support/forum escalation rather than one durable case object
- five new **interface specs** for an incident case contract sheet, hypothesis adjudication review, case closure proof, incident case timeline, and case-lineage receipt
- a tighter non-clone line based on current official Resilio evidence that even careful operators still have to reconstruct `what we now believe the cause is` from many separate articles and artifacts
- five hard product decisions:
  - **every material degradation becomes a first-class incident case object**
  - **supported, refuted, unresolved, and combined causes stay separate**
  - **closure classes remain typed: resolved, mitigated, workaround, self-recovered, unknown-but-stable, unresolved, reopened**
  - **residual risk and reopen triggers stay explicit even after the symptom clears**
  - **support artifacts and forum replies can inform a case but cannot replace adjudication**

New docs in this tranche:

- `1426-resilio-root-cause-adjudication-case-closure-and-reopen-criteria-fragmentation-evaluation.md`
- `1427-incident-case-contract-sheet-page-symptom-cluster-hypotheses-and-target-sentence-interface-spec.md`
- `1428-hypothesis-adjudication-review-page-supported-refuted-unresolved-and-competing-causes-interface-spec.md`
- `1429-case-closure-proof-page-resolved-mitigated-unresolved-reopen-triggers-and-residual-risk-interface-spec.md`
- `1430-incident-case-timeline-page-symptom-branch-elimination-cause-promotion-and-reopen-events-interface-spec.md`
- `1431-case-lineage-receipt-page-cause-status-residual-risk-and-blocked-stronger-sentences-interface-spec.md`

### Why this pass matters

The previous tranche answered `how do we perform the chosen fix safely?`
This tranche answers the next harder question:

> `what do we now believe, how honest is closure, and what exact thing would force us to reopen the case later?`

Current official Resilio material is useful here precisely because it does preserve real diagnostic diversity, but still too diffusely for a clone.
The clearest current cluster is:

- `Sync Main View (Desktop)` still gives History for the last 30 days and search/filter in the main surface
- `My files don't sync` still pushes the operator through warnings, history, and queue state, with warning entries linking to KB explanations
- `Errors and warnings` and `Core warnings` still fan one visible problem family out into many distinct warning articles and cause families
- `Database error` still admits several plausible causes rather than one deterministic explanation
- `Cannot download files ... no source peers online for too long time` still documents a real ghost-file/topology race explanation
- `Agent run out of system notify watchers` still explains one delay symptom through Linux watcher exhaustion and rescan-only discovery
- `Service files missing / Cannot identify destination folder` still ties the symptom either to corrupted `.sync` state or two Sync instances touching the same folder
- `SE_SM_NO_IDENTITY` and `Error 205` still point to mobile identity corruption on different paths
- `Some internal tasks are taking time to complete` still preserves a true self-recovery branch
- `Peers aren't connecting` still ends in a two-peer debug-log escalation path
- `Collecting debug logs automatically` still requires timestamps, affected shares/files, and peer role in the support narrative, while also stating that direct technical support is not available for Sync v3

All of that is exactly why this revision turns case reasoning into a product seam instead of leaving it as troubleshooting folklore.

## Revision addendum — remediation run choreography, checkpoints, and safe abort after rev0379

This pass locks the next seam after typed intervention selection: **remediation execution**.
The archive already knew how to choose the least-destructive justified next action.
What it still lacked was one explicit answer to:

> once the action is chosen, how do we execute it safely, in what order, with what preflight checks, with what witness checkpoints, and at what point do we stop instead of compounding damage or ambiguity?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on why current execution choreography is still scattered across restart/reconnect/re-add/service/config/log-capture/watcher-limit/docs rather than owned as one run object
- five new **interface specs** for a remediation-run contract sheet, execution-readiness review, checkpointed-run proof, remediation-run timeline, and execution-lineage receipt
- a tighter non-clone line based on current official Resilio evidence that even careful operators still have to reconstruct `how exactly do we perform the chosen fix safely?` from many separate articles
- five hard product decisions:
  - **every material multi-step intervention becomes a first-class remediation run object**
  - **preflight gates, quiet points, and destructive boundaries are explicit rather than side notes**
  - **checkpoint evidence governs safe-continue versus safe-abort after each critical step**
  - **archive/path/world-fork risks block destructive progress until cleared**
  - **handoff and partial completion preserve the next allowed and next forbidden action explicitly**

New docs in this tranche:

- `1420-resilio-intervention-execution-choreography-prerequisite-checkpoints-and-abort-boundary-fragmentation-evaluation.md`
- `1421-remediation-run-contract-sheet-page-step-graph-prerequisites-quiet-point-and-abort-boundary-interface-spec.md`
- `1422-execution-readiness-review-page-preflight-archive-risk-observer-coverage-and-concurrency-freeze-interface-spec.md`
- `1423-checkpointed-run-proof-page-step-completion-witnesses-safe-continue-and-safe-abort-interface-spec.md`
- `1424-remediation-run-event-timeline-page-preflight-freeze-execute-verify-cooldown-abort-and-handoff-events-interface-spec.md`
- `1425-execution-lineage-receipt-page-run-graph-checkpoints-abort-path-and-proof-ceiling-interface-spec.md`

### Why this pass matters

The previous tranche answered `what should we do next?`
This tranche answers the next harder question:

> `how do we execute that chosen action safely enough that later operators can tell whether we actually did the right thing, stopped at the right boundary, and preserved the strongest truthful sentence?`

Current official Resilio material is useful here precisely because it is candid about step ordering, but still too scattered for a clone.
The clearest current cluster is:

- current `My files don't sync` docs still require peer/warning/history/queue inspection before many fixes
- current `Database error` docs still publish a real order: restart, then reconnect, then all-peer re-add
- current `Service files missing / Cannot identify destination folder` docs still require archive review before deleting `.sync` and re-adding
- current `Disconnecting and Removing Folders` docs still preserve that disconnect, reconnect, and remove are different verbs with different destination/path consequences
- current `Sync Service Troubleshooting on Windows` docs still show a permission workaround that also creates a new service storage world, requires restart, and then re-add / re-share or reconnect of all folders
- current `Running Sync in configuration mode` docs still distinguish config placement, start semantics, service exceptions, and `storage_path` world creation
- current `Collecting debug logs automatically` docs still make witness capture itself a run with enable, restart, reproduce, and timed observation steps
- current `Agent run out of system notify watchers` docs still require system-limit change plus restart
- current `How soon does synchronization start?` docs still change what post-fix proof means because rescan cadence and even restart-triggered rescans may be disabled
- current `Some internal tasks are taking time to complete` docs still preserve a legitimate `observe first` branch when symptoms may self-recover

## Revision addendum — rev0379 intervention ladder, least-destructive-next-action, and post-action proof

This pass locks the next seam after rollout-health evidence: **intervention selection / remediation ladder / post-action proof**.
The archive already knew how to decide whether a rollout was healthy enough to widen.
What it still lacked was one explicit product answer to:

> now that we know something is wrong, ambiguous, or blocked, what exact intervention should we take next, how risky is it, what evidence justifies it, and what proof would tell us whether it truly helped?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on scattered remediation advice across restart, rescan, reconnect, re-add, relink, world-shift, watcher-limit, service-account, and artifact-capture flows
- five new **interface specs** for intervention contract sheet, remediation-ladder review, intervention approval proof, remediation timeline, and intervention-lineage receipt
- a tighter non-clone line based on current official Resilio evidence that the ordinary operator task `choose the least-destructive justified next action` still depends on many separate troubleshooting articles rather than one canonical intervention workspace
- five hard product decisions:
  - **every material corrective action becomes a first-class intervention object**
  - **least-destructive viable action wins over more dramatic action**
  - **wait/observe and artifact capture are real intervention classes, not absences of action**
  - **reversibility, blast radius, and proof ceiling stay separate**
  - **symptom disappearance must stay weaker than root-cause removal**

New docs in this tranche:

- `1414-resilio-intervention-selection-remediation-ladder-and-post-action-proof-fragmentation-evaluation.md`
- `1415-intervention-contract-sheet-page-candidate-action-risk-and-success-claim-interface-spec.md`
- `1416-remediation-ladder-review-page-least-destructive-next-action-and-escalation-interface-spec.md`
- `1417-intervention-approval-proof-page-chosen-action-rollback-and-post-action-check-interface-spec.md`
- `1418-remediation-event-timeline-page-attempt-result-cooldown-and-escalation-interface-spec.md`
- `1419-intervention-lineage-receipt-page-action-basis-reversibility-and-outcome-ceiling-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's remediation contract**

This time the reason is especially clear around **action choice, destructiveness, reversibility, and post-action proof**.
Current official materials simultaneously show that:

- restart, reconnect, re-add, relink, `.sync` deletion, watcher-limit changes, service-account changes, and log/profiler capture are all real interventions with very different cost
- some interventions are local while others fork runtime or storage worlds
- some actions require restart before they even become active
- support-artifact capture is part of the intervention ladder rather than outside it
- current Resilio still leaves the operator to reconstruct `what is the least-destructive justified next action, and what stronger sentence would it actually prove?` from many separate articles

That is good enough to borrow the distinctions, but not good enough to clone the contract shape.

## Revision addendum — rev0378 promotion evidence, signal adjudication, and health-freshness truth

This pass locks the next seam after rollout rings and stop conditions: **rollout health / signal adjudication / evidence freshness / promotion confidence**.
The archive already knew how to define a rollout, set gates, and declare stop conditions.
What it still lacked was one explicit product answer to:

> given the evidence we have right now, is this rollout actually healthy enough to widen, or are we overreading a graph, a warning, a stale artifact, or a support anecdote?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on real-time graphs, warnings, history, queue clues, hidden background work, debug/profiler artifacts, and health-evidence freshness
- five new **interface specs** for rollout-health contract sheet, signal-adjudication review, promotion-confidence proof, health-event timeline, and rollout-health lineage receipt
- a tighter non-clone line based on current official Resilio evidence about ongoing-only performance graphs, multi-surface troubleshooting (Peers/Status/History/queue), hidden background work that may self-recover, restart-bound profiling/log collection, v3 support limitations, and changelog evidence that warning/stat accuracy has evolved over time
- five hard product decisions:
  - **every serious rollout gets a first-class health object**
  - **signal classes are explicit and typed**
  - **promotion confidence is graded, not implied from one surface**
  - **evidence freshness is published before promotion widens**
  - **support artifacts cannot silently become durable product truth**

New docs in this tranche:

- `1408-resilio-rollout-health-signal-adjudication-and-evidence-freshness-fragmentation-evaluation.md`
- `1409-rollout-health-contract-sheet-page-signal-classes-evidence-window-and-promotion-readiness-interface-spec.md`
- `1410-signal-adjudication-review-page-warnings-history-graphs-logs-and-human-escalation-interface-spec.md`
- `1411-promotion-confidence-proof-page-greenhold-redstop-and-evidence-freshness-interface-spec.md`
- `1412-rollout-health-event-timeline-page-warning-flap-recovery-escalation-and-sentence-change-interface-spec.md`
- `1413-rollout-health-lineage-receipt-page-signal-basis-confidence-grade-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's rollout-health contract**

This time the reason is especially clear around **health evidence, signal provenance, and promotion confidence**.
Current official materials simultaneously show that:

- current `Performance overview` docs still say the graphs are real-time views for ongoing activity, with 1-minute, 10-minute, and 1-hour windows, and that disk-load is not necessarily Sync-only load
- current `My files don't sync` docs still tell operators to inspect several planes — peers, Status warnings, Sync History, and per-share queues — before they can even form a first diagnosis
- current `Some internal tasks are taking time to complete` docs still say important work is hidden from the user, warnings may be intermittent and self-recovering, and logs may still be needed if they do not clear in time
- current log-collection docs still say v3 has no direct technical support, artifacts must often be gathered manually or after enabling debug logging and restarting, and useful evidence may require at least 15 minutes of post-repro collection
- current power-user docs still show that telemetry/profiler/log controls are settings with their own freshness and activation debt
- current change logs still preserve that performance statistics, statuses, and warning usability have needed improvement over time

That candor is useful.
The health contract is the problem.
AnonSync should not clone a world where the operator still has to translate `graph looks okay`, `warning appeared`, `history shows errors`, `logs were captured`, `support is limited`, and `this might be a known issue` into one stable answer about confidence grade, promotion consequence, freshness, causal strength, and blocked stronger sentence by stitching together several KB articles.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because rollout health is a real contract with separate truths for evidence window, signal class, freshness, adjudication, confidence grade, and promotion consequence — but the present contract still scatters the answer to `is this rollout healthy enough to widen right now?` across several KB articles and support flows instead of owning it as one stable page family.**

## Revision addendum — rev0377 policy rollout rings, readiness gates, and safe promotion

This pass locks the next seam after policy lifecycle and supersession: **policy rollout / ring promotion / stop condition / rollback truth**.
The archive already knew how to define a successor policy and explain who should move in principle.
What it still lacked was one explicit product answer to:

> now that a successor exists, how exactly do we ship it across a real cohort — in stages, with canary/pilot/broad ring truth, explicit readiness gates, stop conditions, and predeclared rollback class — without letting publication masquerade as successful rollout?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on mixed-major rollout risk, install-posture-specific upgrades, version/feature lane gates, restart-bound activation, service migrate-vs-clean-install branches, and rollback truth
- five new **interface specs** for rollout contract sheet, readiness review, ring-promotion proof, rollout-event timeline, and rollout lineage receipt
- a tighter non-clone line based on current official Resilio evidence about v2/v3 compatibility versus linked-family conflict, Business/v3 non-upgradability, narrower v3 platform envelope, feature availability by version/entitlement, install-posture-specific update steps, restart-required settings, service restart/config branches, Local System storage-world replacement, and historical change-log evidence that rollout state can be derailed by restart and autoupdate edges
- five hard product decisions:
  - **every policy successor rollout is a first-class rollout object, not a boolean publish**
  - **ring membership is explicit and typed (`canary`, `pilot`, `broad`, `holdback`, `frozen`, `rollback`)**
  - **promotion is gate-based, not hope-based**
  - **armed stop conditions can freeze broader promotion automatically**
  - **rollback class is declared before promotion and preserved in receipts**

New docs in this tranche:

- `1402-resilio-policy-rollout-rings-readiness-gates-and-rollback-window-fragmentation-evaluation.md`
- `1403-policy-rollout-contract-sheet-page-successor-target-rings-readiness-gates-and-stop-conditions-interface-spec.md`
- `1404-rollout-readiness-review-page-version-floor-waiver-debt-restart-cost-and-world-eligibility-interface-spec.md`
- `1405-ring-promotion-proof-page-canary-pilot-broad-freeze-auto-stop-and-rollback-class-interface-spec.md`
- `1406-rollout-event-timeline-page-stage-entry-promotion-freeze-stop-rollback-and-reopen-events-interface-spec.md`
- `1407-policy-rollout-lineage-receipt-page-revision-ring-gate-stop-basis-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's rollout contract**

This time the reason is especially clear around **compatibility versus safe staged rollout**.
Current official materials simultaneously show that:

- current `FAQ Resilio Sync 3.0.0` docs still say v2 and v3 preserve synchronization compatibility while linked devices should all be updated to v3 to avoid license conflicts
- current `Updating installation to Resilio Sync v3` docs still say Business cannot be updated to v3, warn that important changes may affect usage and shares configuration, and make the procedure depend on whether the install is default, service-based, CLI `/config` or `/storage`, or sidecar `sync.conf`
- current supported-platform docs still show a narrower v3 platform envelope than v2 in important ways, including no Windows Server support for v3 while v2 still lists it
- current `Selective Sync` docs still publish feature availability by version and entitlement, proving that one rollout claim can be safe for a subset and unsafe cohort-wide
- current `Power user preferences` docs still say older versions may miss settings or have deprecated ones, while at least one field still requires restart to activate
- current service docs still say install choices and principal changes can create migrate-vs-clean-install forks and even another storage world requiring re-add / re-share
- current change-log history still shows repeated rollout-adjacent failures involving restart, autoupdate persistence, license-after-restart, startup crashes, and mixed-version edges

That candor is useful.
The rollout contract is the problem.
AnonSync should not clone a world where the operator still has to translate `compatible`, `supported`, `updatable`, `restart required`, `clean install`, `hold this Business lane`, `subset-only feature`, and `mixed-major linked risk` into one stable answer about ring membership, readiness, stop conditions, rollback class, and blocked stronger sentence by stitching together several KB articles.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because policy rollout is a real contract with separate truths for publication state, ring state, readiness gates, stop conditions, rollback class, and claim ceiling — but the present contract still scatters the answer to `are we actually ready to broaden this rollout?` across several KB articles instead of owning it as one stable page family.**

## Revision addendum — rev0376 policy lifecycle, supersession, and safe retirement

This pass locks the next seam after policy profiles and typed waivers: **policy lifecycle / successor relation / retirement truth**.
The archive already knew how to define a profile, measure conformance, and explain exceptions.
What it still lacked was one explicit product answer to:

> when a new policy appears, is it actually the next revision, a partial successor, a world-specific successor, a split, a merge, a rollback, or a retirement with no safe successor — and what happens to subjects and waivers still living under the old one?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on supersession, retirement, successor worlds, rebind-vs-continuity, and lifecycle evidence debt
- five new **interface specs** for policy-lifecycle contract sheet, supersession review, promotion-and-retirement proof, policy-family timeline, and policy-lifecycle lineage receipt
- a tighter non-clone line based on current official Resilio evidence about deprecated or version-specific settings, Standard-folder remove/re-add replacement, disconnect vs remove vs reconnect rebind, config-authored successor worlds, service migrate-vs-clean-install forks, Local System storage-world replacement, identity regeneration, and storage/settings teardown
- four hard product decisions:
  - **every governed profile belongs to a policy family and every family change gets a typed successor relation**
  - **retirement is a first-class state, not silent deletion**
  - **waivers never auto-carry silently across supersession**
  - **subject posture after supersession stays explicit: on-current, on-deprecated, grandfathered, blocked-from-successor, orphaned, or retired-with-no-successor**

New docs in this tranche:

- `1396-resilio-policy-supersession-retirement-and-successor-world-fragmentation-evaluation.md`
- `1397-policy-lifecycle-contract-sheet-page-predecessor-successor-relation-and-retirement-scope-interface-spec.md`
- `1398-supersession-review-page-cohort-adoption-waiver-carryforward-and-orphan-risk-interface-spec.md`
- `1399-promotion-and-retirement-proof-page-successor-cutover-coverage-and-blocked-subjects-interface-spec.md`
- `1400-policy-family-timeline-page-promotion-deprecation-split-merge-rollback-and-sunset-events-interface-spec.md`
- `1401-policy-lifecycle-lineage-receipt-page-predecessor-successor-status-and-blocked-stronger-sentences-interface-spec.md`

## Revision addendum — policy-waiver pack, exception class, and expiry review after rev0374

This revision continues directly from `rev0374` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **desktop-only folder preferences, Linux-WebUI-ignored advanced settings, mobile device settings versus Android share-local advanced preferences, Android Simple-mode capability limits, config-mode replication for the same settings on multiple machines, config-only Standard-folder limits, config-authored WebUI suppression and folder override, storage-path world forks, service migration vs clean-install forks, and service-principal world changes**.
2. Tightens the non-clone line again: borrow Resilio's candor that `supported world`, `supported surface`, `ignored field`, `local-parallel lane`, `missing prerequisite`, `migration gap`, `clean-install fork`, and `temporary waiver` are different truths; refuse any contract where the operator still has to reconstruct `why isn't this subject really on profile, is that temporary, and when can the exception be removed?` from several surfaces and articles.
3. Adds one new **Resilio evaluation** document focused on why present-day policy-waiver and applicability reasoning are still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for a policy-waiver contract sheet, waiver cohort review, waiver issuance proof, waiver drift timeline, and waiver lineage receipt.
5. Makes one hard product decision explicit: **every material profile divergence must become either a typed waiver object or a hard non-support verdict.**
6. Makes another hard product decision explicit: **`unsupported-world`, `unsupported-surface`, `ignored-by-runtime`, `local-parallel-lane`, `missing-prerequisite`, `migration-gap`, and `hard-out-of-policy` are different truths and must not collapse into one generic `exception`.**
7. Makes a third hard product decision explicit: **waivers expire by default, open-ended exceptions need stronger approval and ownership, and waived subjects do not count as clean conformance.**
8. Packages the result as another continuation archive whose new tranche makes the `policy-waiver / debt-class / expiry-review / rollout-blocking / waiver-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1390-resilio-policy-waiver-class-exception-expiry-and-applicability-fragmentation-evaluation.md`
- `1391-policy-waiver-contract-sheet-page-exception-scope-prerequisite-gap-and-expiry-interface-spec.md`
- `1392-waiver-cohort-review-page-unsupported-worlds-ignored-fields-device-local-lanes-and-debt-class-interface-spec.md`
- `1393-waiver-issuance-proof-page-approve-timebox-recheck-and-rollout-blocking-interface-spec.md`
- `1394-waiver-drift-timeline-page-prerequisite-met-expiry-renewal-and-unplanned-coverage-loss-interface-spec.md`
- `1395-waiver-lineage-receipt-page-profile-gap-expiry-review-duty-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's profile-exception contract**

This time the reason is especially clear around **desktop-only preference surfaces, Linux-WebUI ignored advanced fields, Android share-local advanced lanes, Simple-mode capability limits, config-only Standard-folder scope, WebUI suppression by config-authored shares, storage/world forks, and service migration vs clean-install gaps**.
Current official materials simultaneously show that:

- current `Folder Preferences` docs still say per-folder preferences are desktop-only
- current `Power user preferences` docs still say at least one advanced field is ignored in Linux WebUI
- current `Settings on mobile platforms` and `Sync interface on Android` docs still keep device settings and per-share advanced preferences on separate local routes, while Android `Simple mode` still changes whether a share location can be chosen manually
- current `Running Sync in configuration mode` docs still say config mode is useful for applying the same settings on multiple machines, still limit config-authored shares to Standard folders, still allow advanced preferences in `sync.conf`, still let non-default `storage_path` create a new settings world, and still disable WebUI plus override previously WebUI-added folders when shared folders are declared in config
- current `Running Sync as a service on Windows` and `Sync Service Troubleshooting on Windows` docs still say service install can migrate existing settings or create a clean-install fork, and still say principal changes such as `Local System` can widen access while creating another service storage world that requires re-add / re-share
- current `Sync Private Identity & Linking My Devices` docs still say linking already-running devices can replace one certificate and remove Advanced folders from the app on the device that takes over the new certificate

That candor is useful.
The waiver contract is the problem.
AnonSync should not clone a world where the operator still has to translate `desktop-only`, `ignored in Linux WebUI`, `mobile local`, `Simple mode`, `config replica`, `clean install`, `service fork`, and `identity replacement` into one stable answer about exception class, affected fields, expiry, owner, removal condition, rollout consequence, and blocked stronger sentence by stitching together several KB articles.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because profile exceptions are a real contract with separate truths for exception class, applicability scope, removal condition, expiry, owner, and rollout consequence — but the present contract still scatters the answer to `why isn't this subject really on profile, is that temporary, and when can the exception be removed?` across several KB articles instead of owning it as one stable page family.**

## Revision addendum — policy-profile pack, binding class, and conformance rollout after rev0373

This revision continues directly from `rev0373` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **linked-device auto-availability, device default connect mode, default arrival roots, per-folder preferences, global power-user defaults, config-mode replication for the same settings on multiple machines, config-only standard-folder limits, storage-path world forks, service migration vs clean-install forks, and mobile/share-local preference routes**.
2. Tightens the non-clone line again: borrow Resilio's candor that `linked-family default mode`, `default arrival root`, `per-share policy`, `global advanced default`, `mobile-local share lane`, `config-authored fleet replication`, `storage-path world fork`, and `service successor world` are different truths; refuse any contract where the operator still has to reconstruct `what named policy profile exists, what exact fields it covers, which subjects are truly bound to it, and what the next profile revision will actually change` from several surfaces and articles.
3. Adds one new **Resilio evaluation** document focused on why present-day policy-profile and conformance reasoning are still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for a policy-profile contract sheet, profile conformance review, profile attach-and-rollout proof, profile drift timeline, and profile lineage receipt.
5. Makes one hard product decision explicit: **every reusable defaults bundle must be a first-class versioned policy-profile object with explicit field coverage, subject scope, and world scope.**
6. Makes another hard product decision explicit: **binding classes are real — `live-inherit`, `field-pin`, `frozen-snapshot`, `branched-profile`, and `unbound` are different truths.**
7. Makes a third hard product decision explicit: **profile revision rollout is compare-first, mutate-second, and `same current values` must stay visibly weaker than `will adopt future profile revisions`.**
8. Packages the result as another continuation archive whose new tranche makes the `policy-profile / binding-class / conformance-review / rollout-proof / profile-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1384-resilio-policy-profile-pack-binding-revision-and-conformance-fragmentation-evaluation.md`
- `1385-policy-profile-contract-sheet-page-profile-signature-field-coverage-and-binding-class-interface-spec.md`
- `1386-profile-conformance-review-page-live-bindings-field-pins-frozen-copies-and-unbound-subjects-interface-spec.md`
- `1387-profile-attach-and-rollout-proof-page-target-cohort-adoption-mode-and-revision-safety-interface-spec.md`
- `1388-profile-drift-timeline-page-revision-bump-field-pin-freeze-branch-and-rejoin-events-interface-spec.md`
- `1389-profile-lineage-receipt-page-profile-signature-binding-class-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's profile-shaped settings contract**

This time the reason is especially clear around **linked-family defaults, per-device arrival posture, per-folder policy, global advanced defaults, config-mode replication, storage/world forks, and mobile/share-local lanes**.
Current official materials simultaneously show that:

- current `Sync Private Identity & Linking My Devices` and `Synchronization Modes` docs still describe automatic linked-device availability plus per-device default connect behavior
- current `Sync Preferences` docs still describe default arrival roots for new folders and single-file landings
- current `Folder Preferences`, `Power user preferences`, and `File download priority` docs still distribute one reusable policy family across per-folder, advanced-default, and manually detached lanes
- current Android and mobile settings docs still keep device-level and share-level advanced preferences in separate local routes
- current `Running Sync in configuration mode` docs still say config mode is useful for applying the same settings on multiple machines, still allow advanced preferences in `sync.conf`, still limit config-authored shares to Standard folders, still disable WebUI when shared folders are specified there, and still let non-default storage create another settings world
- current `Running Sync as a service on Windows` docs still say service installation can preserve continuity by migration or create a clean-install fork that requires re-sharing folders

That candor is useful.
The profile contract is the problem.
AnonSync should not clone a world where the operator still has to translate `default mode`, `same settings`, `folder preference`, `advanced default`, `config replica`, `mobile share setting`, and `migrated service copy` into one stable answer about canonical profile id, field coverage, binding class, conformance grade, revision adoption, and blocked stronger sentence by stitching together several KB articles.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because reusable policy is a real contract with separate truths for profile identity, field coverage, binding class, world scope, revision adoption, and conformance — but the present contract still scatters the answer to `what profile governs this subject, and what exactly will the next profile revision change?` across several KB articles instead of owning it as one stable page family.**

## Revision addendum — setting-baseline anchor, equivalence grade, and safe realignment after rev0372

This revision continues directly from `rev0372` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **file-download-priority default/override behavior, power-user defaults, ordinary UI search, power-user-search convenience, mobile per-share advanced preferences, configuration-mode storage/world authorship, service migration vs clean-install forks, and local-only custom share names**.
2. Tightens the non-clone line again: borrow Resilio's candor that `visible value`, `manual detach`, `inherit`, `explicit none`, `mobile-local parallel setting`, `startup-owned config world`, `service fork`, and `local custom label` are different truths; refuse any contract where the operator still has to reconstruct `do these actually match, what baseline am I comparing against, and am I aligning value only or governance too?` from several articles and surfaces.
3. Adds one new **Resilio evaluation** document focused on why present-day setting-baseline and equivalence reasoning are still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for a setting-baseline contract sheet, equivalence review, realignment proof, baseline-drift timeline, and baseline-lineage receipt.
5. Makes one hard product decision explicit: **every serious settings comparison must compile to a normalized governance signature rather than relying on label plus visible value alone.**
6. Makes another hard product decision explicit: **equality has grades — `same label`, `same visible value`, `same effective value now`, `same governance state`, and `same baseline conformance` are different truths.**
7. Makes a third hard product decision explicit: **realignment is compare-first, mutate-second, and `restore inheritance` must remain visibly different from `match the current displayed value`.**
8. Packages the result as another continuation archive whose new tranche makes the `baseline-anchor / equivalence-grade / false-friend / realignment-proof / baseline-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1378-resilio-setting-baseline-anchor-equivalence-grade-and-realignment-fragmentation-evaluation.md`
- `1379-setting-baseline-contract-sheet-page-anchor-subject-signature-and-equivalence-grade-interface-spec.md`
- `1380-equivalence-review-page-visible-match-effective-match-governance-match-and-false-friends-interface-spec.md`
- `1381-realignment-proof-page-align-keep-detached-split-branch-and-reanchor-subjects-interface-spec.md`
- `1382-baseline-drift-timeline-page-default-shift-local-rename-override-world-fork-and-rejoin-events-interface-spec.md`
- `1383-baseline-lineage-receipt-page-anchor-signature-equivalence-grade-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's settings-comparison contract**

This time the reason is especially clear around **same-looking values with different override lineage, mobile-parallel settings, config/service world forks, search-vs-compare, and local-only subject labels**.
Current official materials simultaneously show that:

- current `File download priority` and `Power user preferences` docs still say the same conceptual policy can live in share preferences or in a global default, and still say manually altered shares stop following later global-default changes even if later set back to `None`
- current Android and iOS interface docs still keep per-share advanced preferences on device-local routes alongside general settings
- current `Running Sync in configuration mode` docs still say config mode can set up only Standard folders, that non-default storage creates another settings world, and that config-authored shared folders override folders previously added from WebUI while disabling WebUI
- current `Running Sync as a service on Windows` docs still say service installation can preserve continuity by migration or create a clean-install fork that requires re-sharing folders
- current `Setting custom name for sync shares` docs still say local custom names are only UI labels, do not rename the folder on disk, do not propagate to other peers, and can survive disconnect until reset
- current search docs and change log still show useful local search improvements, but not one canonical settings-equivalence workspace

That candor is useful.
The comparison contract is the problem.
AnonSync should not clone a world where the operator still has to translate `same label`, `same value`, `same share`, `same default`, `same route`, and `same world` into one stable answer about canonical anchor, governance signature, equality grade, safe realignment action, and blocked stronger sentence by stitching together several KB articles.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because settings comparison is a real contract with separate truths for anchor identity, visible value, governance lineage, world scope, and baseline conformance, but the present contract still scatters the answer to `do these actually match, and what exactly would aligning them change?` across several KB articles instead of owning it as one stable page family.**

## Revision addendum — setting-impact cohort, detached overrides, and inherit-vs-explicit-none truth after rev0371

This revision continues directly from `rev0371` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **desktop global preferences, per-share folder preferences, power-user defaults, file-download-priority override behavior, mobile settings and per-share advanced routes, configuration-mode authorship, service migration vs clean-install forks, and historical UI convenience additions in the change log**.
2. Tightens the non-clone line again: borrow Resilio's candor that `default`, `share override`, `explicit none`, `mobile-local parallel value`, `startup-owned config`, `service-world fork`, and `clean-install world` are different truths; refuse any contract where the operator still has to reconstruct `who exactly will this change reach, who stays detached, and does this mean inherit or explicit none?` from several articles and surfaces.
3. Adds one new **Resilio evaluation** document focused on why present-day settings-impact and override-cohort reasoning are still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for a setting-impact contract sheet, impact-cohort review, pre-commit impact proof, impact-drift timeline, and impact-lineage receipt.
5. Makes one hard product decision explicit: **every meaningful settings mutation must compile to an explicit target cohort before commit.**
6. Makes another hard product decision explicit: **`inherit` is a first-class state and must never be represented by the same control state as explicit `none/off`.**
7. Makes a third hard product decision explicit: **a subject whose visible value matches the default by coincidence must not be allowed to impersonate a reattached inheriting subject.**
8. Packages the result as another continuation archive whose new tranche makes the `setting-impact / detached-exception / reattach / world-fork` seam explicit in the reading order and page family.

New docs in this tranche:

- `1372-resilio-setting-impact-cohort-detached-overrides-and-inheritance-reset-fragmentation-evaluation.md`
- `1373-setting-impact-contract-sheet-page-target-cohort-detached-overrides-and-inherit-vs-explicit-none-interface-spec.md`
- `1374-impact-cohort-review-page-global-default-share-override-mobile-parallel-and-service-world-branches-interface-spec.md`
- `1375-precommit-impact-proof-page-subjects-that-will-change-stay-detached-or-require-reattach-interface-spec.md`
- `1376-impact-drift-timeline-page-default-shift-override-creation-explicit-none-reattach-and-world-fork-events-interface-spec.md`
- `1377-impact-lineage-receipt-page-target-cohort-detached-exceptions-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's settings-impact contract**

This time the reason is especially clear around **default reach, detached shares, explicit-none ambiguity, mobile-parallel routes, and service/config world forks**.
Current official materials simultaneously show that:

- current `File download priority` docs still distinguish a global default from a per-share manual choice and still say a manually altered share no longer follows later default changes even if set back to `None`
- current `Sync Preferences`, `Folder Preferences`, and `Power user preferences` docs still distribute one conceptual setting family across desktop-global, per-share, and advanced-default surfaces
- current mobile docs still keep device-level settings and per-share advanced settings in separate local lanes
- current config-mode and service docs still show that startup-owned config and service-world choices can govern a different world or a forked successor world
- the current change log still shows useful local improvements such as `search in power user settings` and remembered share-dialog state, but not one explicit pre-commit impact planner

So the next AnonSync obligation is now clear:

> **a setting locator is not enough; every serious settings mutation must also publish one reviewed answer to `who changes, who stays out, and what exact inheritance state am I looking at?`**

## Revision addendum — setting-surface discoverability, route locality, and interface locator truth after rev0370

This revision continues directly from `rev0370` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **desktop Sync Preferences, desktop Folder Preferences, Power user preferences, Android settings and per-share advanced settings, configuration-mode `sync.conf`, service-only config placement, and WebUI omissions**.
2. Tightens the non-clone line again: borrow Resilio's candor that `global setting`, `per-share setting`, `power-user default`, `mobile setting`, `startup-authored config`, `service-owned config`, and `visible but not editable here` are different truths; refuse any contract where the operator still has to reconstruct `where do I change this, at what scope, on which surface, and what exactly will this edit touch?` from several articles.
3. Adds one new **Resilio evaluation** document focused on why present-day settings-surface discoverability is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for a setting-locator contract sheet, setting-route review, setting-context proof, setting-change itinerary, and setting-lineage receipt.
5. Makes one hard product decision explicit: **every meaningful setting is a first-class object with one canonical identity rather than a loose label scattered across menus, help pages, and config files.**
6. Makes another hard product decision explicit: **visibility, editability, authority, scope, and activation are separate truths.**
7. Makes a third hard product decision explicit: **`I can see this setting here` is weaker than `I can edit it here`, and `I can edit it here` is weaker than `this surface is the winning authority for this value`.**
8. Packages the result as another continuation archive whose new tranche makes the `setting-locator / route-review / context-proof / change-itinerary / setting-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1366-resilio-setting-surface-discoverability-route-and-context-fragmentation-evaluation.md`
- `1367-setting-locator-contract-sheet-page-canonical-setting-scope-and-edit-route-interface-spec.md`
- `1368-setting-route-review-page-desktop-folder-mobile-config-and-service-branches-interface-spec.md`
- `1369-setting-context-proof-page-visible-vs-editable-vs-authoritative-here-interface-spec.md`
- `1370-setting-change-itinerary-page-query-route-edit-activation-and-verification-events-interface-spec.md`
- `1371-setting-lineage-receipt-page-query-route-scope-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's settings-surface contract**

This time the reason is especially clear around **desktop-vs-folder-vs-power-user placement, mobile-vs-desktop asymmetry, config-mode startup authorship, and service-only edit routes**.
Current official materials simultaneously show that:

- current `Sync Main View (Desktop)` docs still point the operator outward to Sync Preferences, Folder Preferences, Power user preferences, search/filter controls, and right-click share menus rather than answering one canonical `where does this setting live?`
- current `Sync Preferences` docs still put global update, startup, notifications, default path, scheduler, network, proxy, debug logging, and the jump into Power user preferences in one desktop-only surface
- current `Folder Preferences` docs still keep per-folder archive, relay, tracker, LAN, predefined hosts, and file download priority in a separate desktop-only surface
- current `Power user preferences` docs still expose a distinct advanced settings surface, and some entries there still carry their own restart/activation caveats
- the current change log still advertises `Added search in power user settings`, which is useful but still only improves one sub-surface rather than compiling one product-owned answer about setting identity and route
- current `Settings on mobile platforms` and `Sync interface on Android` docs still put identity, network, notifications, advanced settings, and per-share advanced preferences on separate mobile routes
- current `Running Sync in configuration mode` and `Running Sync as a service on Windows` docs still say config-mode and service-mode settings are authored through `sync.conf`, with service config requiring placement in the service storage folder and restart
- current `Updating Sync to latest version` docs still say some actions such as `Check now` are unavailable in WebUI

That candor is useful.
The settings-surface contract is the problem.
AnonSync should not clone a world where the operator still has to translate `settings`, `folder preferences`, `advanced`, `mobile`, `config`, `service`, and `not in WebUI` into one stable answer about canonical setting identity, scope, edit surface, witness-only surfaces, authority winner, and blocked stronger sentence by stitching together several KB articles.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because setting discoverability is a real contract with separate truths for scope, edit route, witness surface, authority winner, and activation boundary, but the present contract still scatters the answer to `where do I change this, here or elsewhere, and what exactly will this edit govern?` across several KB articles instead of owning it as one stable page family.**

## Revision addendum — activation boundary, restart debt, and cold-apply truth after rev0364

This revision continues directly from `rev0364` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **hot-reread IgnoreList behavior, FileDelayConfig restart requirement, debug-logging restart verification, WebUI credential reset/reload, service WebUI listen changes, LAN-only cache burn-down, and startup-loaded config/service modes**.
2. Tightens the non-clone line again: borrow Resilio's candor that `saved`, `re-read`, `restart recommended`, `service restart required`, `loaded on startup`, and `old cache still active` are different truths; refuse any contract where the operator still has to reconstruct `when is this change actually in force, and what stale runtime debt still survives?` from several articles.
3. Adds one new **Resilio evaluation** document focused on why present-day activation-boundary truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for activation-boundary contract sheet, restart-debt review, applied-state proof, activation timeline, and activation-boundary lineage receipt.
5. Makes one hard product decision explicit: **activation rung is a first-class contract object rather than an afterthought hidden behind `saved` or `restart if needed`.**
6. Makes another hard product decision explicit: **live-now, next-rescan, next-local-restart, next-service-restart, next-cohort-restart, and successor-cutover are separate truths.**
7. Makes a third hard product decision explicit: **`saved` is weaker than `active in runtime`, and `restart completed` is weaker than `old-world cache debt is truly burned down`.**
8. Packages the result as another continuation archive whose new tranche makes the `activation-boundary-contract / restart-debt-review / applied-state-proof / activation-timeline / activation-boundary-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1330-resilio-activation-boundary-restart-debt-and-cold-apply-fragmentation-evaluation.md`
- `1331-activation-boundary-contract-sheet-page-live-apply-rescan-restart-and-cutover-rungs-interface-spec.md`
- `1332-restart-debt-review-page-ignorelist-filedelay-debug-logging-webui-and-lan-cache-branches-interface-spec.md`
- `1333-applied-state-proof-page-live-now-next-rescan-next-restart-and-service-restart-evidence-interface-spec.md`
- `1334-activation-timeline-page-config-edit-rescan-restart-cache-burn-and-cutover-events-interface-spec.md`
- `1335-activation-boundary-lineage-receipt-page-change-basis-activation-rung-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's activation-boundary contract**

This time the reason is especially clear around **hot-reread files, restart-gated changes, service-specific restart requirements, and cached old-world debt that survives a settings edit**.
Current official materials simultaneously show that:

- current `Ignoring files in Sync (Ignore List)` docs still say IgnoreList is re-read when changed or on rescan, yet still recommend a restart if the operator wants the change applied immediately
- current `Setting Delay Time For Syncing` docs still say FileDelayConfig edits require saving the file and restarting Sync
- current debug-log collection docs still say the operator should turn on debug logging and then restart Sync to make sure the logging state is actually active
- current `How do I reset my WebUI password?` docs still say credential-reset flows require quitting Sync, changing files, and restarting before the new state becomes authoritative
- current `Sync Service Troubleshooting on Windows` docs still say some WebUI listen changes require service restart and that service-mode config files are loaded automatically by the service at startup
- current `Can I force Sync to do local network (LAN) syncing only and not sync via the Internet?` docs still say old Internet-learned peer addresses can survive until cache-expiration settings are changed and the client is restarted through a specific burn-down sequence

That candor is useful.
The activation-boundary contract is the problem.
AnonSync should not clone a world where the operator still has to translate `I saved the file`, `I changed the setting`, `restart recommended`, `service restart`, `config mode`, and `old route still used` into one stable answer about mutation locus, activation rung, stale runtime debt, witness grade, and blocked stronger sentence by stitching together several KB articles.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because activation is a real contract with separate truths for live-now adoption, rescan adoption, restart-gated adoption, service-specific cold-load, and cache-burn debt, but the present contract still scatters the answer to `when is this change really in force, and what stale runtime debt still remains?` across several KB articles instead of owning it as one stable page family.**

## Revision addendum — transfer-cost truth, resend geometry, and splittability ceiling after rev0363

This revision continues directly from `rev0363` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **piecewise delta transfer, whole-file resend after piece shift, archive-assisted rename reuse, splittable-vs-nonsplittable priority behavior, and queue preemption under download priority**.
2. Tightens the non-clone line again: borrow Resilio's candor that `changed data only`, `whole file again`, `renamed without retransmit`, and `downloaded first` are different truths; refuse any contract where the operator still has to reconstruct `how many bytes will actually move here, why did this file resend in full, and did priority change order or network cost?` from several articles.
3. Adds one new **Resilio evaluation** document focused on why present-day transfer-cost truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for transfer-cost contract sheet, resend-geometry review, byte-cost proof, transfer-shape timeline, and transfer-cost lineage receipt.
5. Makes one hard product decision explicit: **transfer cost is a first-class contract object rather than an optimistic side effect of `syncs only changed data` marketing language.**
6. Makes another hard product decision explicit: **piecewise delta, whole-file resend, archive-hit rename reuse, queue priority, and splittability ceiling are separate truths.**
7. Makes a third hard product decision explicit: **`higher priority` is weaker than `lower byte cost`, and `same bytes under a new pathname` is weaker than `rename reuse is actually proven on this cohort`.**
8. Packages the result as another continuation archive whose new tranche makes the `transfer-cost-contract / resend-geometry-review / byte-cost-proof / transfer-shape-timeline / transfer-cost-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1324-resilio-transfer-cost-resend-geometry-and-splittability-ceiling-fragmentation-evaluation.md`
- `1325-transfer-cost-contract-sheet-page-splittability-reuse-basis-and-order-vs-byte-cost-interface-spec.md`
- `1326-resend-geometry-review-page-piece-shift-rename-reuse-and-archive-gate-interface-spec.md`
- `1327-byte-cost-proof-page-piecewise-delta-full-resend-and-priority-evidence-interface-spec.md`
- `1328-transfer-shape-timeline-page-queue-preemption-archive-hit-and-whole-file-fallback-events-interface-spec.md`
- `1329-transfer-cost-lineage-receipt-page-byte-cost-basis-reuse-path-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's transfer-cost contract**

This time the reason is especially clear around **piecewise delta transfer, full resend after piece-shift edits, archive-assisted rename reuse, and splittable-only priority guarantees**.
Current official materials simultaneously show that:

- current `When a file changes, does Resilio Sync transfer the entire file again, or just the part that's changed?` docs still say Sync splits files into pieces from 32KB up to 2MB, usually sends only changed pieces, but will re-sync the whole file if the edit shifts all pieces
- those same current docs still say the stronger `avoid whole-file resend even after shift` sentence belongs to the separate Sync Business diff-delta lane rather than the ordinary baseline
- current `What happens when file is renamed` docs still say rename reuse depends on the remote peer finding the same hash in Archive and that without Archive enabled the file will be re-synced again
- current `File download priority` docs still say priority can reorder the active queue by mtime or size, can suspend lower-priority downloads immediately, but strictly follows the prioritization rules only for files that are split in pieces during transfer
- those same current priority docs still say queue rebuilds and the 50k active-file ceiling can change performance independently of the actual byte cost of any one file

That candor is useful.
The transfer-cost contract is the problem.
AnonSync should not clone a world where the operator still has to translate `sync only changed data`, `rename`, `priority`, `suspended`, `large file`, and `archive` into one stable answer about byte-cost class, reuse basis, splittability class, queue order, and blocked stronger sentence by stitching together several KB articles.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because transfer cost is a real contract with separate truths for byte-cost class, rename-reuse basis, splittability ceiling, and queue order, but the present contract still scatters the answer to `how many bytes will actually move, why did this resend in full, and did priority change only order or also cost?` across several KB articles instead of owning it as one stable page family.**

## Revision addendum — salvage readiness, continuity escrow, and late-decrypt authority after rev0362

This revision continues directly from `rev0362` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **encrypted-folder rescue preconditions, saved RW/RO key escrow, database continuity on encrypted nodes, local CLI decrypt, db-path discovery through logs, storage-root variability, and the limits of encrypted Archive restore**.
2. Tightens the non-clone line again: borrow Resilio's candor that ciphertext presence, secret escrow, database continuity, and actual recovery lane are different truths; refuse any contract where the operator still has to reconstruct `if the source dies later, is this encrypted backup actually salvageable, and what present-day action would silently break that future option?` from several articles.
3. Adds one new **Resilio evaluation** document focused on why present-day salvage-readiness truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for salvage-readiness contract sheet, continuity-escrow review, recovery-precondition proof, salvage-viability timeline, and salvage-readiness lineage receipt.
5. Makes one hard product decision explicit: **salvage readiness is a first-class contract object rather than a soft promise implied by `backup` language.**
6. Makes another hard product decision explicit: **ciphertext presence, secret escrow, database continuity, locator readiness, and actual recovery lane are separate truths.**
7. Makes a third hard product decision explicit: **same-looking folder path is weaker than same database continuity, and same encrypted capability is weaker than saved RW decryption authority.**
8. Packages the result as another continuation archive whose new tranche makes the `salvage-readiness-contract / continuity-escrow-review / recovery-precondition-proof / salvage-viability-timeline / salvage-readiness-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1318-resilio-salvage-readiness-escrow-continuity-and-late-decrypt-fragmentation-evaluation.md`
- `1319-salvage-readiness-contract-sheet-page-secret-escrow-database-continuity-and-recovery-lane-interface-spec.md`
- `1320-continuity-escrow-review-page-remove-readd-database-rebind-and-latent-salvage-loss-interface-spec.md`
- `1321-recovery-precondition-proof-page-rw-key-db-path-encrypted-node-and-stronger-claim-barrier-interface-spec.md`
- `1322-salvage-viability-timeline-page-key-retention-folder-removal-log-loss-and-source-failure-events-interface-spec.md`
- `1323-salvage-readiness-lineage-receipt-page-escrow-basis-continuity-proof-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's salvage-readiness contract**

This time the reason is especially clear around **encrypted backup preconditions, saved-secret escrow, database continuity, db-path discovery, and the gap between ciphertext retention and late decrypt authority**.
Current official materials simultaneously show that:

- current `Encrypted folders` docs still say an encrypted backup peer can only become a later rescue source if RW and RO keys were saved somewhere and the encrypted folder was not removed from Sync so the database remains the same as initially created
- those same current docs still say the encrypted node cannot decrypt files itself, so recovery depends on either reconnecting with the RW key from a safe workstation or using a local CLI decrypt path
- those same current docs still say CLI decrypt needs the RW secret plus the database path, and that the database name may need to be learned from debug logs by finding the shareID in `sync.log`
- current `Sync Storage folder` docs still say the storage directory holds shares' databases and that its location materially changes by OS, Linux package posture, and service account
- current `Disconnecting and Removing Folders` docs still say folder removal/disconnect changes Sync state while filesystem bytes can remain, which is exactly why `still on disk` is weaker than `continuity still survives`
- current `Encrypted folders` and `Using Archive for file versioning and restoring deleted files` docs together still show that encrypted-node salvage is a different ladder from ordinary Archive restore, because encrypted peers are read-only and auto-follow source delete state

That candor is useful.
The salvage-readiness contract is the problem.
AnonSync should not clone a world where the operator still has to translate `encrypted backup`, `have the key`, `folder still exists`, `can decrypt`, `can restore later`, and `archive still has it` into one stable answer about escrow basis, continuity proof, locator proof, recovery lane, and blocked stronger sentence by stitching together several KB articles.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because encrypted-backup rescue is a real contract with separate truths for secret escrow, database continuity, locator readiness, and actual late-decrypt lane, but the present contract still scatters the answer to `if the source dies later, is this backup really salvageable and what action would silently break that?` across several KB articles instead of owning it as one stable page family.**

## Revision addendum — claim quantifier, audience truth, and sufficiency-scope honesty after rev0361

This revision continues directly from `rev0361` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **approval quantifiers (`only new peers` vs `all peers`), linked-device approval carry, `X of Y peers` counting, disconnected-vs-selective sufficiency rules, local-share `self` topology, and remove-vs-linked-family-vs-nonlinked-remote boundaries**.
2. Tightens the non-clone line again: borrow Resilio's candor that `one`, `any`, `all`, `self only`, `all linked devices`, and `all connected peers` are different truths; refuse any contract where the operator still has to reconstruct `who exactly is this claim about, and how many counterparts are sufficient for it to be true?` from several articles.
3. Adds one new **Resilio evaluation** document focused on why present-day quantifier truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for quantifier contract sheet, audience-scope review, sufficiency proof, quantifier-drift timeline, and quantifier lineage receipt.
5. Makes one hard product decision explicit: **claim quantifier is a first-class contract object.**
6. Makes another hard product decision explicit: **self-only, any-source, all-connected, all-linked, all-remote-known, and all-ever-approved are different public truths.**
7. Makes a third hard product decision explicit: **`one peer online` is weaker than `one source peer with the needed bytes online`, and `removed from linked devices` is weaker than `removed from every remote holder`.**
8. Packages the result as another continuation archive whose new tranche makes the `quantifier-contract / audience-scope-review / sufficiency-proof / quantifier-drift-timeline / quantifier-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1312-resilio-claim-quantifier-audience-and-sufficiency-fragmentation-evaluation.md`
- `1313-quantifier-contract-sheet-page-subject-set-audience-set-and-sufficiency-rule-interface-spec.md`
- `1314-audience-scope-review-page-self-only-linked-family-remote-peers-and-ever-approved-branches-interface-spec.md`
- `1315-sufficiency-proof-page-any-source-all-connected-all-linked-and-no-stronger-claim-interface-spec.md`
- `1316-quantifier-drift-timeline-page-approval-memory-roster-decay-and-source-loss-events-interface-spec.md`
- `1317-quantifier-lineage-receipt-page-claim-subject-sufficiency-basis-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's quantifier contract**

This time the reason is especially clear around **approval scope, linked-device carry, local-share self-topology, peer-count semantics, selective-sync source sufficiency, and linked-family removal limits**.
Current official materials simultaneously show that:

- current `Sync Share Dialog (Desktop)` docs still say links can require approval from only new peers or from all peers per folder
- current `Sync functionality in detail` docs still say any linked device can approve a folder connection
- current `Sync Main View (Desktop)` docs still say `X of Y peers` means online peers out of the total including offline peers
- current `Synchronization Modes` docs still say disconnected folders can connect later when any peer in the swarm is online, while Selective Sync fetch requires at least one peer that has the files online
- current `Sharing a folder locally` docs still say a local share connects only to `self`, only pulls from the parenting share, and does not sync with remote peers directly even though the peer count can grow
- current `Disconnecting and Removing Folders` docs still say removing a folder from linked devices does not prove it disappeared from remote devices not linked to your identity

That candor is useful.
The quantifier contract is the problem.
AnonSync should not clone a world where the operator still has to translate `peer`, `peers`, `all`, `only new`, `all linked devices`, `self`, `connected peers`, and `at least one source` into one stable answer about subject set, audience set, sufficiency rule, and blocked stronger sentence by stitching together several KB articles.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because counterpart quantifiers are a real contract with separate truths for subject set, audience set, sufficiency threshold, and horizon, but the present contract still scatters the answer to `who is this about, and how many counterparts are enough for this sentence to be true?` across several KB articles instead of owning it as one stable page family.**

## Revision addendum — action surface truth, witness locality, and recovery-scope honesty after rev0360

This revision continues directly from `rev0360` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **WebUI-default runtimes, desktop-only folder settings, Linux WebUI exceptions, desktop-vs-WebUI Archive handling, WebUI update-check gaps, desktop-only local shares, and Android/iOS/background asymmetry**.
2. Tightens the non-clone line again: borrow Resilio's candor that execution surface, witness surface, recovery surface, and out-of-band fallback are different truths; refuse any contract where the operator still has to reconstruct `can I do this here, where can I really verify it, and where does recovery actually live?` from several articles.
3. Adds one new **Resilio evaluation** document focused on why present-day action-surface truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for action-surface contract sheet, surface-locality review, action-availability proof, surface-shift timeline, and action-surface lineage receipt.
5. Makes one hard product decision explicit: **execution surface, witness surface, and recovery surface are separate first-class truths.**
6. Makes another hard product decision explicit: **`available in product` is weaker than `available on this current surface`, and `available on this current surface` is weaker than `recoverable on this current surface`.**
7. Makes a third hard product decision explicit: **out-of-band filesystem / shell / service-manager recovery is weaker than same-surface recovery, even when it is the strongest honest path.**
8. Packages the result as another continuation archive whose new tranche makes the `action-surface-contract / surface-locality-review / action-availability-proof / surface-shift-timeline / action-surface-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1306-resilio-action-surface-execution-witness-and-recovery-locality-fragmentation-evaluation.md`
- `1307-action-surface-contract-sheet-page-execution-surface-witness-surface-and-recovery-scope-interface-spec.md`
- `1308-surface-locality-review-page-desktop-webui-mobile-file-browser-and-os-handoff-branches-interface-spec.md`
- `1309-action-availability-proof-page-here-vs-elsewhere-vs-out-of-band-surface-capability-interface-spec.md`
- `1310-surface-shift-timeline-page-runtime-platform-and-fallback-lane-events-interface-spec.md`
- `1311-action-surface-lineage-receipt-page-requested-verb-active-surface-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's action-surface contract**

This time the reason is especially clear around **WebUI-default Linux/service runtimes, desktop-only folder preferences and local shares, Linux WebUI exceptions, Archive access asymmetry, WebUI update-check omissions, and iOS-open-app-only transfer posture**.
Current official materials simultaneously show that:

- current `Configuring WebUI` docs still say WebUI is the default and only option on Linux/NAS and the default UI path on Windows when Sync is installed as a service
- current `Folder Preferences` docs still say folder preferences are available on desktop platforms only
- current `Power user preferences` docs still say `disable_remove_from_all_devices` is ignored in Linux WebUI
- current `Using Archive for file versioning and restoring deleted files` docs still say `Open Archive` is a desktop Sync UI action, while WebUI and Android use the file browser and iOS has no Archive access there
- current `Updating Sync to latest version` docs still say manual `Check now` is not available in the WebUI
- current `Sharing a folder locally` docs still say local shares are supported only on desktop versions
- current `Does Sync work in background?` and `Sync for iOS Peculiarities` docs still say desktop and Android can continue work in background while iOS transfer requires the app to be open

That candor is useful.
The action-surface contract is the problem.
AnonSync should not clone a world where the operator still has to translate `available`, `not here`, `open in browser`, `use file browser`, `desktop only`, `WebUI only`, and `mobile works differently` into execution surface, witness surface, recovery surface, and semantic loss boundary by stitching together several KB articles.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because action locality is a real contract with separate truths for execution, witnessing, recovery, and out-of-band fallback, but the present contract still scatters the answer to `can I do this here, can I verify it here, and where does recovery actually live?` across several KB articles instead of owning it as one stable page family.**

## Revision addendum — participant-unit truth, grouped-row granularity, and approval-scope honesty after rev0358

This revision continues directly from `rev0358` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **certificate-bearing identities, linked-device families, grouped user rows, Standard-vs-Advanced peer-list granularity, editable device labels, and approval memory that can carry across linked devices**.
2. Tightens the non-clone line again: borrow Resilio's candor that identity, certificate, linked family, device seat, grouped row, and friendly label are different truths; refuse any contract where the operator still has to reconstruct `who exactly is this row about, what unit did I approve, and what does this count really count?` from several articles.
3. Adds one new **Resilio evaluation** document focused on why present-day participant truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for participant-unit contract sheet, peer-row granularity review, participant-authority proof, participant-granularity timeline, and participant-unit lineage receipt.
5. Makes one hard product decision explicit: **participant unit is a first-class contract object.**
6. Makes another hard product decision explicit: **row count, device-seat count, authority-unit count, and permission-bearing participant count are separate truths.**
7. Makes a third hard product decision explicit: **device-name match is weaker than certificate continuity, and grouped-row continuity is weaker than approval-memory continuity.**
8. Packages the result as another continuation archive whose new tranche makes the `participant-unit-contract / peer-row-granularity-review / participant-authority-proof / participant-granularity-timeline / participant-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1294-resilio-participant-unit-identity-device-and-peer-row-granularity-fragmentation-evaluation.md`
- `1295-participant-unit-contract-sheet-page-identity-family-device-seat-and-row-basis-interface-spec.md`
- `1296-peer-row-granularity-review-page-user-group-device-entry-and-count-truth-interface-spec.md`
- `1297-participant-authority-proof-page-certificate-fingerprint-device-label-and-approval-memory-basis-interface-spec.md`
- `1298-participant-granularity-timeline-page-link-regroup-rename-and-identity-regeneration-events-interface-spec.md`
- `1299-participant-unit-lineage-receipt-page-count-basis-authority-unit-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's participant contract**

This time the reason is especially clear around **certificate identity, linked-device approval carryover, Advanced grouped-user rows, Standard device-only rows, editable device names, and identity regeneration that is really certificate replacement rather than cosmetic relabeling**.


## Revision addendum — admission instrument, approval memory, and credential-afterlife truth after rev0354

This revision continues directly from `rev0354` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **linked-identity automatic sharing, manual sharing via key/link/QR, approval modes, time- and use-limited links, link temporary-key flow, certificate issuance after approval, and non-propagating key rotation**.
2. Tightens the non-clone line again: borrow Resilio's candor that admission basis, transport wrapper, approval gate, durable credential issuance, and post-issuance afterlife are different truths; refuse any contract where the operator still has to reconstruct `what was actually sent, when access became durable, and what survives expiry or key change?` from several articles.
3. Adds one new **Resilio evaluation** document focused on why present-day admission truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for admission-instrument contract sheet, join review, grant-issuance proof, credential-afterlife timeline, and admission-instrument lineage receipt.
5. Makes one hard product decision explicit: **wrapper, admission gate, and durable credential are separate truths.**
6. Makes another hard product decision explicit: **QR is a representation wrapper, not its own authority class.**
7. Makes a third hard product decision explicit: **link expiry is weaker than access revocation, and local key rotation is weaker than cohort-wide migration.**
8. Packages the result as another continuation archive whose new tranche makes the `admission-instrument-contract / join-review / grant-issuance-proof / credential-afterlife-timeline / admission-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1270-resilio-admission-instrument-approval-memory-and-credential-afterlife-fragmentation-evaluation.md`
- `1271-admission-instrument-contract-sheet-page-key-link-qr-approval-and-certificate-basis-interface-spec.md`
- `1272-join-review-page-approval-requirement-link-expiry-use-count-and-existing-peer-memory-interface-spec.md`
- `1273-grant-issuance-proof-page-temporary-key-fingerprint-certificate-and-acl-basis-interface-spec.md`
- `1274-credential-afterlife-timeline-page-link-expiry-key-rotation-approval-memory-and-old-cohort-split-interface-spec.md`
- `1275-admission-instrument-lineage-receipt-page-join-basis-credential-class-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's admission contract**

This time the reason is especially clear around **manual keys vs links, approval memory, expiring/use-limited links, link temporary-key flow, certificate issuance, and key-rotation afterlife**.
Current official materials simultaneously show that:

- current `Comprehensive guide to syncing` docs still separate linked-identity automatic sharing from manual sharing via key/link/QR
- current `Sync Share Dialog (Desktop)` docs still say Standard-folder keys differ from links specifically by approval mechanism, that links may require no approval, only-new-peer approval, or all-peer-per-folder approval, and that links can be limited by time or number of uses
- current `Link structure and flow` docs still say links carry a temporary key and expiration, that the link payload is after the `#` fragment and not sent to Resilio server, and that durable access requires request, fingerprint review, X509 certificate issuance, and ACL signing
- current `Key structure and flow` docs still say changing the key on one peer does not distribute automatically; old-key peers continue syncing with each other and stop syncing with the changed peer
- current `Sync Share Dialog (Desktop)` and `Comprehensive guide to syncing` docs still treat QR as a sharing means / wrapper for mobile use rather than a separate authority class

That candor is useful.
The admission contract is the problem.
AnonSync should not clone a world where the operator still has to translate `share`, `key`, `link`, `QR`, `approval`, `expired invite`, and `changed key` into admission basis, gate class, durable credential issuance, remembered-trust scope, invite afterlife, and lineage split by stitching together several KB articles.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because admission is a real contract with separate truths for automatic identity arrival, manual key/link transport, approval memory, certificate issuance, and credential afterlife, but the present contract still scatters the answer to `what was actually sent, when access became durable, and what survives expiry or key change?` across several KB articles instead of owning it as one stable page family.**

## Revision addendum — mixed-version capability floor, platform gating, and feature-ceiling truth after rev0352

This revision continues directly from `rev0352` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **v2/v3 byte compatibility, linked-family mixed-major license conflict risk, platform-envelope differences between v2 and v3, Selective Sync feature gating, and Business/NAS installs that must remain on v2**.
2. Tightens the non-clone line again: borrow Resilio's candor that wire compatibility, identity-linked safety, platform support, feature entitlement, and upgrade lane are different truths; refuse any contract where the operator still has to reconstruct `what can this whole cohort safely claim, which member sets the floor, and what upgrade is actually forbidden rather than merely delayed?` from several articles.
3. Adds one new **Resilio evaluation** document focused on why present-day mixed-version capability truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for capability-floor contract sheet, version interlock review, feature envelope proof, capability-floor timeline, and capability-floor lineage receipt.
5. Makes one hard product decision explicit: **byte compatibility is weaker than capability compatibility.**
6. Makes another hard product decision explicit: **linked-family mixed-major risk is first-class state rather than a footnote under generic compatibility.**
7. Makes a third hard product decision explicit: **product lane and platform class can permanently cap the cohort even when newer peers exist.**
8. Packages the result as another continuation archive whose new tranche makes the `capability-floor-contract / version-interlock-review / feature-envelope-proof / capability-floor-timeline / capability-floor-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1258-resilio-mixed-version-capability-floor-platform-gating-and-license-conflict-fragmentation-evaluation.md`
- `1259-capability-floor-contract-sheet-page-cohort-version-floor-platform-gate-and-feature-ceiling-interface-spec.md`
- `1260-version-interlock-review-page-linked-family-mixed-major-risk-and-upgrade-boundary-interface-spec.md`
- `1261-feature-envelope-proof-page-feature-gates-seat-type-platform-class-and-cohort-floor-interface-spec.md`
- `1262-capability-floor-timeline-page-upgrade-drift-unsupported-nodes-and-floor-change-events-interface-spec.md`
- `1263-capability-floor-lineage-receipt-page-cohort-floor-blocked-feature-and-remediation-basis-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's mixed-version capability contract**

This time the reason is especially clear around **v2/v3 wire compatibility, mixed-major linked-family risk, narrower v3 platform support, feature gating by version/license, and Business/NAS lanes that must stay on v2**.
Current official materials simultaneously show that:

- current `FAQ Resilio Sync 3.0.0` docs still say v2 and v3 preserve synchronization compatibility, but devices linked with one identity should all be updated to v3 to avoid license conflicts
- current `Sync Private Identity & Linking My Devices` docs still say it is highly advisable not to link devices where v2 and v3 are mixed because licenses can conflict and lead to lost access to Sync UI and shares configuration, even though files on storage are not affected
- current `Supported platforms and system requirements` docs still say v3 is not supported on Windows Server while v2 still lists Windows Server support; those same docs also still show a wider v2 platform envelope including FreeBSD and wider CPU coverage
- current `Selective Sync` docs still say the feature is fully available in v3, while in v2 it is available only in licensed editions
- current Linux and NAS installation docs still say Sync Business must remain on v2, the latest available Business lane is 2.8.1, and installing v3 over a Business installation is unsupported and can lose access to configured shares until reinstall

That candor is useful.
The capability-floor contract is the problem.
AnonSync should not clone a world where the operator still has to translate `compatible`, `linked devices`, `supported platform`, `licensed feature`, and `Business must stay on v2` into byte-compatibility grade, admin-safety ceiling, platform floor, feature envelope, and forbidden upgrade lane by stitching together several FAQ, identity, platform, feature, and install pages.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because mixed-version truth is a real contract with separate truths for wire compatibility, linked-family safety, platform eligibility, feature entitlement, and upgrade lane, but the present contract still scatters the answer to `what can this whole cohort safely claim, which member sets the floor, and what upgrade is actually forbidden rather than merely delayed?` across several KB articles instead of owning it as one explicit capability-floor page family.**

## Revision addendum — effective seat posture, writeback authority, serve-right, and derived-seat truth after rev0346

This revision continues directly from `rev0346` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **Read Only vs Read & Write vs Owner posture, file suspension on RO edits, `Overwrite any changed files` behavior by action type, RO byte-serving, linked-device Owner defaults, local-share inheritance/downshift, and encrypted-node hard-wired observer posture**.
2. Tightens the non-clone line again: borrow Resilio's candor that grant label, local divergence fate, byte-serving, onward sharing, and derived posture are different truths; refuse any contract where the operator still has to reconstruct `what can this peer really do, what happens to its unauthorized edits, and is this posture direct or inherited?` from several articles.
3. Adds one new **Resilio evaluation** document focused on why present-day effective-seat truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for effective-seat-posture contract sheet, narrow-seat mutation review, delegation-and-serve proof, derived-seat review, and effective-seat-posture lineage receipt.
5. Makes one hard product decision explicit: **grant label is insufficient on its own; effective seat posture is the real contract object.**
6. Makes another hard product decision explicit: **writeback authority, onward-share authority, byte-serve eligibility, and local-divergence fate are separate truths.**
7. Makes a third hard product decision explicit: **derived posture is first-class state — direct grant, linked-family default, local-share inheritance, encrypted hard-wire, or unresolved derivation.**
8. Packages the result as another continuation archive whose new tranche makes the `effective-seat-posture / narrow-seat-mutation-review / delegation-and-serve-proof / derived-seat-review / seat-posture-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1222-resilio-effective-seat-posture-writeback-heal-serve-and-derivation-fragmentation-evaluation.md`
- `1223-effective-seat-posture-contract-sheet-page-grant-label-writeback-authority-serve-right-and-local-change-fate-interface-spec.md`
- `1224-narrow-seat-mutation-review-page-suspension-auto-heal-local-only-additions-and-selective-sync-ceiling-interface-spec.md`
- `1225-delegation-and-serve-proof-page-onward-share-authority-unmodified-byte-serving-and-peer-cascade-ceiling-interface-spec.md`
- `1226-derived-seat-review-page-linked-owner-default-local-share-inheritance-encrypted-hardwire-and-reshare-boundary-interface-spec.md`
- `1227-effective-seat-posture-lineage-receipt-page-derived-basis-local-change-fate-and-serve-ceiling-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's effective-seat contract**

This time the reason is especially clear around **RO edit suspension, optional destructive auto-heal, local-only additions, RO byte-serving, linked-device Owner defaults, local-share inherited downshift, and encrypted-node hard-wiring**.
Current official materials simultaneously show that:

- current `User Management` docs still say permissions can differ by identity, linked devices all act as Owners, RO edits do not propagate and can suspend further sync for the changed file, RW peers publish mutations, and Owner additionally grants onward share and revoke authority
- current `Is one-way synchronization possible?` docs still say RO rename, delete, and content edit can be auto-healed back from RW source when `Overwrite any changed files` is enabled, while local adds remain present but unsynced; those same docs still say RO peers may nevertheless transfer unmodified files to newly connected peers
- current `Folder Preferences` docs still say `Overwrite any changed files` is potentially destructive and is disabled for RO folders with Selective Sync ON
- current `Sharing a folder locally` docs still say local shares inherit the permission floor of the source, can never receive Owner, automatically downshift if the source seat is narrowed, and may require remove-and-reshare for access-level changes
- current `Encrypted folders` docs still say encrypted F-key seats are hard-wired RO, have overwrite-heal always on, do not support Selective Sync, follow delete state, and cannot republish deleted files back from their Archive
- current `How to create a Read Only folder while syncing across linked devices?` docs still say linked devices default to Owner posture, so a true RO seat inside one linked family requires breaking out into a separate Standard-folder-plus-RO-key path

That candor is useful.
The effective-seat contract is the problem.
AnonSync should not clone a world where the operator still has to translate `Read Only`, `Owner`, `Overwrite changed files`, `local share`, `encrypted backup`, and `linked device` into writeback authority, local divergence fate, serve-right, delegation ceiling, and derivation class by stitching together several KB articles.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because seat posture is a real contract with separate truths for direct grant, derived posture, writeback authority, serve-right, onward-share authority, and local-divergence fate, but the present contract still scatters the answer to `what can this peer really do, what happens to its unauthorized edits, and is this posture direct or inherited?` across several KB articles instead of owning it as one stable page family.**

## Revision addendum — subject scope, ignore divergence, namespace role, and unsupported-name ceiling after rev0345

This revision continues directly from `rev0345` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **IgnoreList scope exclusion, peer-local rule divergence, post-scan retroactivity limits, hidden-dotfile UI policy, `.sync` service-state criticality, `.!sync` temporary residue, `StreamsList` / xattr sidecar behavior, and unsupported trailing-asterisk names**.
2. Tightens the non-clone line again: borrow Resilio's candor that subject scope, UI-hidden state, service artifacts, metadata sidecars, transfer-temp residue, and invalid-name blocks are different truths; refuse any contract where the operator still has to reconstruct `why is this pathname absent, invisible, uncounted, or unsafe to touch?` from several articles.
3. Adds one new **Resilio evaluation** document focused on why present-day scope/exclusion truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for subject-scope contract sheet, ignore-divergence review, namespace-role review, scope proof, and subject-scope lineage receipt.
5. Makes one hard product decision explicit: **subject scope is first-class per-peer product state rather than a side effect of file visibility and troubleshooting.**
6. Makes another hard product decision explicit: **ordinary user subjects, peer-excluded subjects, UI-hidden subjects, service artifacts, metadata sidecars, transfer-temp residues, and invalid-name blocks are separate namespace roles.**
7. Makes a third hard product decision explicit: **visible is weaker than indexed, indexed is weaker than counted, counted is weaker than replicated, and `ignored now` is weaker than `never announced`.**
8. Packages the result as another continuation archive whose new tranche makes the `subject-scope-contract / ignore-divergence-review / namespace-role-review / scope-proof / subject-scope-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1216-resilio-subject-scope-ignore-divergence-namespace-role-and-unsupported-name-fragmentation-evaluation.md`
- `1217-subject-scope-contract-sheet-page-visibility-indexing-counting-and-namespace-role-interface-spec.md`
- `1218-ignore-divergence-review-page-peer-local-rules-retroactivity-and-size-mismatch-interface-spec.md`
- `1219-namespace-role-review-page-hidden-service-artifacts-streams-and-temp-residue-interface-spec.md`
- `1220-scope-proof-page-visible-indexed-counted-replicated-and-exclusion-basis-interface-spec.md`
- `1221-subject-scope-lineage-receipt-page-peer-scope-namespace-role-and-exclusion-basis-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's scope/exclusion contract**

This time the reason is especially clear around **IgnoreList-based exclusion, case-sensitive and OS-delimited rule syntax, post-scan retroactivity limits, hidden-dotfile UI policy, `.sync` service criticality, `.!sync` temporary transfer residue, Streams/xattr sidecar fallbacks, and unsupported trailing-asterisk names**.
Current official materials simultaneously show that:

- current `Ignoring files in Sync (Ignore List)` docs still say ignored files are not indexed and not counted in `Size`, that default rules already exclude system or temp files, that matching IgnoreLists across peers are advisable but not compulsory, and that IgnoreList is case-sensitive
- those same current `IgnoreList` docs still say the list will not work with files that have already been synced, that later-edited IgnoreLists can leave folder structure already stored in the database and passed to other peers, and that Sync re-reads IgnoreList on change or at `folder_rescan_interval`
- current `What is '.sync' folder, and StreamsList, IgnoreList and Archive inside?` docs still say `.sync` is hidden critical service state, that deleting it causes `Service files missing`, and that `.!sync` files are in-progress downloads rather than finished user content
- current `Service files missing / Cannot identify destination folder` docs still say corrupting `.sync` suspends synchronization and may require removing and re-adding the share
- current `Alt Streams and Xattrs in Sync` docs still say xattrs cannot be ignored by IgnoreList, are governed by `StreamsList`, and may fall back into `.sync/Streams` stub files when a filesystem cannot store them directly
- current mobile settings docs still say dot-prefixed hidden files are not shown in Sync UI by default on those surfaces
- current `Unsupported asterisk (*) characters at the end of file/folder names` docs still say such names are not supported and may be interpreted as system data, causing program errors or disruption of syncing
- current `My files don't sync` docs still collapse unsupported names, encoding issues, long paths, permission problems, stuck `.!sync` residues, time drift, and storage/filesystem faults into one troubleshooting lane

That candor is useful.
The scope contract is the problem.
AnonSync should not clone a world where the operator still has to translate `ignored`, `hidden`, `.sync`, `.!sync`, `Streams`, `not shown`, and `not syncing` into per-peer scope membership, namespace role, count participation, divergence class, and delete safety by stitching together several KB articles.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because subject scope and namespace role are real contracts with separate truths for UI visibility, indexing, counting, peer-local exclusion, service ownership, metadata sidecars, temp transfer residue, and invalid-name ceilings, but the present contract still scatters the answer to `why is this pathname absent, invisible, uncounted, or unsafe to touch?` across several KB articles instead of owning it as one stable page family.**

## Revision addendum — presence, materialization, source guarantee, and ghost fetch after rev0344

This revision continues directly from `rev0344` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **disconnected rows without local paths, Selective Sync placeholders, Connected-mode demand fetch, remove-from-device vs remove-from-all semantics, placeholder removal on disconnect, ghost files with no remaining source peer, local-share dependency on parent materialization, and delete-safety toggles for placeholder surfaces**.
2. Tightens the non-clone line again: borrow Resilio's candor that row visibility, path binding, placeholder namespace, byte residency, source guarantee, and delete authority are different truths; refuse any contract where the operator still has to reconstruct `what actually exists here right now, and can I really fetch it later?` from several articles.
3. Adds one new **Resilio evaluation** document focused on why present-day presence/materialization truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for presence contract sheet, residency-mode review, materialization proof, parent-source dependency review, and presence lineage receipt.
5. Makes one hard product decision explicit: **presence is first-class product state rather than a cosmetic side effect of sync mode and placeholder mechanics**.
6. Makes another hard product decision explicit: **row-only visibility, bound path, placeholder namespace, local byte residency, and source guarantee are separate truths**.
7. Makes a third hard product decision explicit: **visible name is weaker than local path, local path is weaker than local bytes, and local bytes are weaker than durable future fetchability**.
8. Packages the result as another continuation archive whose new tranche makes the `presence-contract / residency-mode-review / materialization-proof / parent-source-dependency-review / presence-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1210-resilio-presence-materialization-source-guarantee-and-ghost-fetch-fragmentation-evaluation.md`
- `1211-presence-contract-sheet-page-row-path-placeholder-byte-and-source-guarantee-interface-spec.md`
- `1212-residency-mode-review-page-disconnected-selective-synced-and-remove-semantics-interface-spec.md`
- `1213-materialization-proof-page-placeholder-backing-peer-ghost-fetch-and-delete-safety-interface-spec.md`
- `1214-parent-source-dependency-review-page-local-share-placeholder-inheritance-and-reconnect-survivor-interface-spec.md`
- `1215-presence-lineage-receipt-page-row-path-byte-and-source-guarantee-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's presence/materialization contract**

This time the reason is especially clear around **disconnected folders with no bound path, 0-byte placeholders, on-demand fetch dependence on live source peers, `Remove from this device` versus `Remove from all devices`, placeholder removal during disconnect, ghost files with no surviving byte source, local-share dependence on parent materialization, and power-user placeholder delete safety rails**.
Current official materials simultaneously show that:

- current `Folder Types and Management` and `Synchronization Modes` docs still say disconnected folders can be shown for future action while taking no space and, in one current description, not even having a folder path associated with them
- current `What Is an RSLS File?`, `Selective Sync`, and `Synchronization Modes` docs still say placeholders are 0-byte representations of names/file types rather than actual data and that on-demand materialization requires a peer that still has the file online
- current `Synchronization Modes` docs still separate `Remove from this device` from `Remove from all devices`, while warning that reverting to placeholder is safe only if another peer still has the file
- current `Disconnecting and Removing Folders` and `Selective Sync` docs still say disconnect/removal can remove placeholders from the local filesystem and that reconnect can propose a new default path unless corrected manually
- current `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time.` docs still describe ghost files where metadata was announced but no peer actually retains the bytes anymore
- current `Sharing a folder locally` docs still say local shares only get data from the parent source share and therefore cannot materialize files if the parent has only placeholders
- current `Power user preferences` docs still expose `disable_remove_from_all_devices` and `recreate_placeholders_on_removal` as separate safety rails that materially change what delete gestures can mean on placeholder-backed surfaces

That candor is useful.
The presence contract is the problem.
AnonSync should not clone a world where the operator still has to translate `available`, `connected`, `.rsls`, `remove from this device`, `remove from all devices`, and `no source peers online` into row visibility, path binding, byte residency, fetch guarantee, and delete blast radius by stitching together several guide, warning, and preference pages.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because visible presence is a real contract with separate truths for row visibility, path binding, placeholder namespace, byte residency, source guarantee, and gesture authority, but the present contract still scatters the answer to `what actually exists here right now, and can I really fetch it later?` across several KB articles instead of owning it as one stable page family.**

## Revision addendum — modification-time authority, offline winner, time-skew gate, and archive republish after rev0342

This revision continues directly from `rev0342` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **same-file concurrent edits, offline-return winner precedence, UTC-normalized time authority, 600-second skew gating, archive-based loser survival, runtime-dependent republish, manual touch remediation, and file-class delay mitigation**.
2. Tightens the non-clone line again: borrow Resilio's candor that chronology class, clock trust, detection sufficiency, archive survival, and republish authority are different truths; refuse any contract where the operator still has to reconstruct `why did this version win, how trustworthy was the time basis, and what must happen before an older version is authoritative again?` from several articles.
3. Adds one new **Resilio evaluation** document focused on why present-day chronology and rollback truth are still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for mutation chronology contract sheet, concurrent edit review, time authority proof, older-byte republish review, and mutation chronology lineage receipt.
5. Makes one hard product decision explicit: **mutation chronology is first-class product state rather than a side effect of mtimes and archive folders**.
6. Makes another hard product decision explicit: **online order, offline-return winner, time-skew refusal, detection remediation, and archive-based republish are separate truths**.
7. Makes a third hard product decision explicit: **clock correctness is weaker than time-authority proof, and archive presence is weaker than rollback authority**.
8. Packages the result as another continuation archive whose new tranche makes the `chronology-contract / concurrent-edit-review / time-authority-proof / older-byte-republish-review / chronology-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1198-resilio-modification-time-authority-offline-winner-time-skew-gate-and-archive-republish-fragmentation-evaluation.md`
- `1199-mutation-chronology-contract-sheet-page-online-order-offline-winner-and-time-basis-interface-spec.md`
- `1200-concurrent-edit-review-page-online-sequence-offline-return-delay-mitigation-and-loser-placement-interface-spec.md`
- `1201-time-authority-proof-page-clock-zone-gmt-window-and-mtime-certainty-interface-spec.md`
- `1202-older-byte-republish-review-page-archive-restore-runtime-witness-and-touch-remediation-interface-spec.md`
- `1203-mutation-chronology-lineage-receipt-page-winner-basis-time-certainty-and-loser-survivor-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's chronology/rollback contract**

This time the reason is especially clear around **online chronological order, offline-return winner precedence, UTC-normalized mtime trust, 600-second time-skew blocking, archive loser survival, runtime-dependent republish, manual touch remediation, and file-class delay**.
Current official materials simultaneously show that:

- current `What if several people make changes to the same file?` docs still say online edits are processed chronologically by modification time, yet an offline-edited returning peer can still outrank later online edits and overwrite them, with overwritten versions placed in Archive
- current `"Time difference" error` docs still say Sync converts file times to GMT/UTC, blocks transfer when peer time drift exceeds the allowed 600-second window, and can degrade mobile surfaces into an empty-list symptom under that same condition
- current `Using Archive for file versioning and restoring deleted files` docs still say restoring an older file requires Sync to be running at restore time or the older version can be compared as stale and moved back to Archive again on rescan
- current `How to touch files?` docs still say Sync treats a file as changed when its modified time or size changes, so manual `touch` is an explicit remediation path when change detection is weak
- current `Setting Delay Time For Syncing` docs still say file-class delay exists to reduce edit-time conflicts, defaults to 10 seconds for listed file types, and requires restart after config edits
- current `Power user preferences` docs still keep `sync_max_time_diff` and `ignore_mtime_assign_errors` as separate low-level authorities rather than one owned chronology surface

That candor is useful.
The chronology contract is the problem.
AnonSync should not clone a world where the operator still has to translate `newer`, `conflict`, `invalid time`, `touch the file`, `restore from Archive`, and `set delay for this extension` into chronology class, time-authority grade, loser survivor map, and rollback proof by stitching together several FAQ, warning, and tips articles.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because winner choice and rollback authority are real contracts with separate truths for chronology class, clock trust, detection sufficiency, loser survival, and republish proof, but the present contract still scatters the answer to `why did this version win, how trustworthy was the time basis, and what must happen before an older version becomes authoritative again?` across several KB articles instead of owning it as one stable page family.**

## Revision addendum — offer family, bearer capability, acceptance lane, and landing residue after rev0336

This revision continues directly from `rev0336` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **folder links vs keys, approval asymmetry, single-file bearer links, browser handoff failure, WebUI manual paste fallback, desktop default file location, mobile fixed receive lanes, and row-vs-byte residue**.
2. Tightens the non-clone line again: borrow Resilio's candor that offer family, approval model, bearer openness, claim lane, destination authority, and cleanup residue are different truths; refuse any contract where the operator still has to reconstruct `what did I issue, how open is it, how will it be claimed, where will it land, and what survives afterward?` from several articles.
3. Adds one new **Resilio evaluation** document focused on why present-day offer-family truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for offer family contract sheet, bearer capability review, acceptance lane review, landing and residue review, and offer-family lineage receipt.
5. Makes one hard product decision explicit: **offer family is first-class product state rather than a cosmetic choice between link, key, QR, or send-file verbs**.
6. Makes another hard product decision explicit: **approval posture, bearer openness, and usage-ceiling absence are separate truths**.
7. Makes a third hard product decision explicit: **claim lane is weaker than claim success, and landing truth is weaker than cleanup truth**.
8. Packages the result as another continuation archive whose new tranche makes the `offer-family-contract / bearer-capability-review / acceptance-lane-review / landing-residue-review / offer-family-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1162-resilio-offer-family-bearer-capability-acceptance-lane-and-landing-residue-fragmentation-evaluation.md`
- `1163-offer-family-contract-sheet-page-key-link-qr-file-send-and-claim-governance-interface-spec.md`
- `1164-bearer-capability-review-page-approval-absence-expiry-usage-ceiling-and-fanout-interface-spec.md`
- `1165-acceptance-lane-review-page-browser-handoff-manual-paste-qr-and-webui-fallback-interface-spec.md`
- `1166-landing-residue-review-page-default-destination-collision-suffix-and-ui-byte-divergence-interface-spec.md`
- `1167-offer-family-lineage-receipt-page-artifact-family-claim-lane-and-landing-survivor-boundary-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's offer-family contract**

This time the reason is especially clear around **approval-capable folder links, approval-free keys, single-file bearer links, browser/WebUI handoff gaps, default landing paths, mobile fixed inboxes, collision suffixes, and row-vs-byte residue**.
Current official materials simultaneously show that:

- current `Sync Share Dialog (Desktop)` docs still say Advanced folders share by link or QR with permission choices, while Standard folders also expose keys and the major difference is the approval mechanism
- those same current docs still say link issuance can require approval for only new peers or for all peers and can attach an expiration period after which new peers must get a new link
- current `Sharing single file` docs still say file sharing is basically a data-transfer operation, defaults to 3-day expiry, may be made non-expiring on desktop, is one-time one-way rather than live sync, and lets anyone with the link download without usage-count restriction or device bans
- those same single-file docs still say changed content requires reissue, recipients may re-share received files further, and same-name landings create `(1)` suffixes
- current `Sync doesn't start when opening Link in browser` and `Configuring WebUI` docs still say browser handoff can fail and WebUI cannot claim clicked links directly, forcing manual `+ -> Enter a key or link`
- current `Sync Preferences` docs still keep single-file arrival under a separate default file location on desktop
- current `Sharing files (Android)` and `Sharing files (iOS)` docs still say mobile single-file links are 3-day by default, use QR receive, and split transfer-list cleanup from landed-byte cleanup differently by surface

That candor is useful.
The offer-family contract is the problem.
AnonSync should not clone a world where the operator still has to translate `Share`, `Copy key`, `Copy link`, `Scan QR`, `Open link`, `Enter a key or link`, and `remove from list` into offer family, openness, claim-lane proof, landing authority, and survivor boundary by stitching together several guide, preference, and troubleshooting articles.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because issuance and claim are real contracts with separate truths for offer family, approval posture, bearer openness, claim lane, landing authority, and residue boundary, but the present contract still scatters the answer to `what did I issue, how open is it, how will it be claimed, where will it land, and what survives cleanup?` across several KB articles instead of owning it as one stable page family.**

## Revision addendum — diagnostic lane, self-serve support boundary, and evidence residue after rev0335

This revision continues directly from `rev0335` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **Business-only direct technical support, Sync v3 self-serve guidance, debug-log activation and restart, 15-minute capture windows, log-rotation budgets, profiler traces, crash artifacts, mobile hidden-log rituals, and cleanup residue**.
2. Tightens the non-clone line again: borrow Resilio's candor that anonymous metrics, debug logs, profiler traces, crash dumps, staffed support, self-serve guidance, and cleanup residue are different truths; refuse any contract where the operator still has to reconstruct `what am I collecting now, who can actually receive it, and what still remains local afterward?` from several articles.
3. Adds one new **Resilio evaluation** document focused on why present-day diagnostic-lane truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for diagnostic lane contract sheet, debug capture review, crash/profiler custody page, external support lane proof, and diagnostic-lane lineage receipt.
5. Makes one hard product decision explicit: **diagnostic lane is first-class product state rather than an advanced-settings afterthought**.
6. Makes another hard product decision explicit: **capture family, support lane, send route, and cleanup residue are separate truths**.
7. Makes a third hard product decision explicit: **restart and hold-time are reviewed sufficiency boundaries, not friendly suggestions**.
8. Packages the result as another continuation archive whose new tranche makes the `diagnostic-contract / debug-capture-review / crash-profiler-custody / support-lane-proof / diagnostic-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1156-resilio-diagnostic-lane-activation-self-serve-support-and-evidence-residue-fragmentation-evaluation.md`
- `1157-diagnostic-lane-contract-sheet-page-capture-family-support-lane-and-residue-ceiling-interface-spec.md`
- `1158-debug-capture-review-page-activation-restart-window-and-log-rotation-cost-interface-spec.md`
- `1159-crash-and-profiler-custody-page-artifact-class-locality-and-send-lane-interface-spec.md`
- `1160-external-support-lane-proof-page-business-support-self-serve-redaction-and-send-readiness-interface-spec.md`
- `1161-diagnostic-lane-lineage-receipt-page-capture-family-send-path-and-residue-boundary-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's diagnostic-lane contract**

This time the reason is especially clear around **business-only direct support, Sync v3 self-serve guidance, restart-gated debug capture, 15-minute sufficiency windows, log rotation, profiler traces, crash-artifact locality, mobile hidden-log rituals, and cleanup residue**.
Current official materials simultaneously show that:

- current `Collecting debug logs manually` and `Collecting debug logs automatically` guides still say direct technical support is available only for Resilio Sync Business customers, while Sync v3 users are directed toward the community forum and Help Center
- those same current guides still say debug logging can be enabled from Preferences/Settings or by creating `debug.txt` with `FFFFFFFF` in the storage folder, still recommend restart to make sure logging is enabled, and still require at least 15 minutes of collection after reproduction
- current `Collecting debug logs manually` docs still say logs are `sync.log` plus rotated zip files, still name platform- and service-user-specific storage paths, and still cap manual attachments at 20 MB before a larger upload link is needed
- current `Increasing Debug Log size` docs still say `log_size` defaults to 100 MB, rotates `sync.log` into `sync.log.old`, can retain up to `log_size * 2` locally, and cannot be adjusted on mobile platforms
- current `Power user preferences` docs still keep `send_statistics`, `log_ttl`, and `profiler_enabled` separate, and still say profiler data is stored as `profiler.dat`, rotated every 10 minutes, and requires restart to activate
- current `Collecting crash reports, mini-dumps and core dumps` docs still split crash reports, minidumps, and core dumps into distinct artifact classes with different paths by platform and Windows service user
- current `Collect debug logs on mobiles` and `Settings on mobile platforms` docs still say mobile capture has a hidden `SNC.DBG.LOGS` flow, hidden `.synclogs` storage, and a separate cleanup action that clears residual files and current debug logs

That candor is useful.
The diagnostic-lane contract is the problem.
AnonSync should not clone a world where the operator still has to translate `debug logging`, `profiler`, `send logs`, `contact support`, `cleanup`, and `crash dump` into capture family, support entitlement, sufficiency window, local residue, and outbound disclosure route by stitching together several troubleshooting and settings articles.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because diagnostics are a real contract with separate truths for capture family, support lane, sufficiency boundary, outbound route, and cleanup residue, but the present contract still scatters the answer to `what am I collecting now, who can receive it, and what remains local afterward?` across several KB articles instead of owning it as one stable page family.**

## Revision addendum — entitlement topology, owner transfer, seat loan, and line-split migration after rev0333

This revision continues directly from `rev0333` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **Business license owner identity, linked-device seat collapse, seat sharing and reclaim, owner-steal by direct key apply, owner-expiry cascade, v2/v3 linked-cohort conflicts, and the Business→v3 hard block**.
2. Tightens the non-clone line again: borrow Resilio's candor that owner identity, borrowed seats, linked-seat counting, and line-family compatibility are different truths; refuse any contract where the operator still has to reconstruct `who really owns this entitlement graph, who is borrowing from it, and can this cohort cross the v2/v3 line safely?` from several articles.
3. Adds one new **Resilio evaluation** document focused on why present-day entitlement-topology and line-family truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for entitlement topology contract sheet, owner transfer review, seat loan/reclaim review, line-split migration watch, and entitlement-topology lineage receipt.
5. Makes one hard product decision explicit: **licensed, linked-under-owner, borrowed-seat, family-shared, and non-commercial self-activation are different entitlement topologies**.
6. Makes another hard product decision explicit: **owner transfer is a governance mutation, not a harmless `apply key` action, and borrowed seats must publish their dependency graph**.
7. Makes a third hard product decision explicit: **byte compatibility is weaker than linked-cohort migration safety, and linked-cohort migration safety is weaker than line-supported upgrade**.
8. Packages the result as another continuation archive whose new tranche makes the `topology-contract / owner-transfer-review / seat-loan-review / line-split-watch / entitlement-topology-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1144-resilio-entitlement-topology-owner-transfer-seat-loan-and-line-split-fragmentation-evaluation.md`
- `1145-entitlement-topology-contract-sheet-page-owner-user-linked-identity-and-line-compatibility-interface-spec.md`
- `1146-license-owner-transfer-review-page-direct-apply-theft-linked-owner-and-seat-survivor-interface-spec.md`
- `1147-seat-loan-and-reclaim-review-page-unique-identity-budget-approval-and-owner-expiry-cascade-interface-spec.md`
- `1148-line-split-migration-watch-page-v2-v3-linked-cohort-conflict-and-business-block-interface-spec.md`
- `1149-entitlement-topology-lineage-receipt-page-owner-seat-class-line-family-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's entitlement-topology and line-migration contract**

This time the reason is especially clear around **single Business owner identity, linked-device seat collapse, shared-seat borrowing, owner-steal by direct key apply, owner-expiry cascade, linked v2/v3 license conflicts, and the Business→v3 hard block**.
Current official materials simultaneously show that:

- current `Sync Business licensing and managing license seats in Resilio Sync v2` docs still say one license seat maps to one unique identity, all devices linked with one identity consume one seat, only one License Owner exists, and that applying the key to another identity makes that new identity the owner
- current `How to apply license key and share license seats` docs still say linked devices under the owner inherit Pro automatically, unlinked identities can borrow seats through approval, reclaim is owner-controlled, and removing the Business license from the owner does not remove it from License Users
- current `What happens when Sync Business trial or license expires?` docs still say shared seats expire when the owner expires
- current `Sync Private Identity & Linking My Devices` docs still warn that linked mixed-version v2/v3 devices may conflict on the applied license and can lose access to UI and share configuration
- current `FAQ Resilio Sync 3.0.0`, `Licensing in Resilio Sync 3.0`, and `Updating installation to Resilio Sync v3` docs still say Business cannot be updated to v3, linked devices should all be updated together to avoid license conflicts, and unsupported Business upgrades can lose configured shares while leaving files on disk intact
- current v3 FAQ/licensing docs still split personal, family, and non-commercial licensing into different usage claims rather than one flat `Pro` story

That candor is useful.
The entitlement-topology contract is the problem.
AnonSync should not clone a world where the operator still has to translate `licensed`, `borrowed seat`, `owner`, `linked device`, and `compatible with v3` into owner graph, counted identity, borrower dependency, line-family safety, and survivor boundary by stitching together licensing, identity, and upgrade pages.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because entitlement is a real topology contract with separate truths for owner identity, borrowed seats, linked-seat counting, line-family compatibility, and migration blast radius, but the present contract still scatters the answer to `who owns this entitlement graph, who is merely borrowing from it, and can this cohort actually cross the v2/v3 line safely?` across several KB articles instead of owning it as one stable page family.**

## Revision addendum — archive witness, restore authority, and retention survivor map after rev0331

This revision continues directly from `rev0331` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **Archive provenance, manual restore, runtime-live restore requirements, retention TTL, max-file-size versioning ceiling, platform visibility gaps, encrypted-seat restore limits, config-authored archive enablement, and uninstall survivor residue**.
2. Tightens the non-clone line again: borrow Resilio's candor that archived bytes, restore authority, retention, and platform visibility are different truths; refuse any contract where the operator still has to reconstruct `what do these archived bytes prove and can this seat really restore them?` from several articles.
3. Adds one new **Resilio evaluation** document focused on why present-day archive/recovery-adjacent truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for archive contract sheet, archive restore review, archive retention/visibility page, archive salvage proof, and archive lineage receipt.
5. Makes one hard product decision explicit: **archive witness is weaker than backup, and restore authority is separate from archived-byte presence**.
6. Makes another hard product decision explicit: **manual resurrection is a reviewed act whose outcome depends on runtime witness, timestamp ordering, and seat authority**.
7. Makes a third hard product decision explicit: **retention TTL, version-size ceiling, platform visibility, encrypted-seat cliffs, and uninstall residue are first-class product state rather than footnotes**.
8. Packages the result as another continuation archive whose new tranche makes the `archive-contract / restore-review / retention-visibility / salvage-proof / archive-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1132-resilio-archive-witness-restore-authority-and-retention-survivor-fragmentation-evaluation.md`
- `1133-archive-contract-sheet-page-version-witness-restore-authority-and-retention-class-interface-spec.md`
- `1134-archive-restore-review-page-manual-resurrection-runtime-witness-and-source-authority-interface-spec.md`
- `1135-archive-retention-and-platform-visibility-page-ttl-size-cap-mobile-visibility-and-sd-card-boundary-interface-spec.md`
- `1136-archive-salvage-proof-page-remote-change-origin-encrypted-seat-limit-and-survivor-map-interface-spec.md`
- `1137-archive-lineage-receipt-page-version-origin-restore-authority-retention-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's archive/recovery-adjacent contract**

This time the reason is especially clear around **remote-change provenance, manual-only restore, runtime-live restore dependence, TTL and size ceilings, platform visibility gaps, encrypted-seat inability to republish restored bytes, and uninstall survivor residue**.
Current official materials simultaneously show that:

- current `Using Archive for file versioning and restoring deleted files` docs still say Archive receives older or deleted copies on other peers when a peer updates or deletes a file, keeps them by default for 30 days on desktops and 1 day on mobiles, requires manual restore only, exposes Archive differently by platform, and depends on Sync still running so restored files are not immediately archived again as older
- the same docs still say Archive can be turned on or off per folder, `sync_trash_ttl = 0` means never auto-delete, and `max_file_size_for_versioning` can exclude large files from version history altogether
- current `.sync` docs still say Archive is hidden under each synced folder and stores old versions of files deleted or modified on other devices
- current `Encrypted folders` docs still say encrypted nodes have Archive yet cannot restore deleted files back into the swarm because they follow deleted authoritative state and are read-only
- current config-mode docs still say per-folder `use_sync_trash` is a real authored setting
- current uninstall docs still say removing the app does not remove hidden `.sync/Archive` residue

That candor is useful.
The archive contract is the problem.
AnonSync should not clone a world where the operator still has to translate `I found it in Archive` into provenance, restore authority, retention horizon, and cleanup residue by stitching together versioning, sidecar, encrypted-seat, config, and uninstall pages.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because Archive is a real witness-and-salvage contract with separate truths for remote-change provenance, restore authority, runtime restore conditions, retention ceilings, platform visibility, and survivor residue, but the present contract still scatters the answer to `what do these archived bytes prove and can this seat really restore them?` across several KB articles instead of owning it as one stable page family.**

## Revision addendum — path liveness, remount witness, and rebind ceiling after rev0329

This revision continues directly from `rev0329` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **missing-path warnings, same-drive move tracking, cross-root breakage, reconnect path drift, removable-root return, and same-computer internal→external targeting**.
2. Tightens the non-clone line again: borrow Resilio's candor that `path missing`, `same-root move`, `cross-root rehome`, `returned external root`, and `fresh bind` are different truths; refuse any contract where the operator still has to reconstruct `did this subject die, move, remount, or become a new bind?` from several FAQs and warning pages.
3. Adds one new **Resilio evaluation** document focused on why present-day path-liveness truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for path liveness contract sheet, missing-path review, remount/external-media review, rebind proof, and path-liveness lineage receipt.
5. Makes one hard product decision explicit: **path liveness is weaker than subject continuity, and subject continuity is weaker than peer-continuity preservation**.
6. Makes another hard product decision explicit: **same-root move, cross-root rehome, returned removable root, self-edge external targeting, and fresh bind are different classes rather than one `fix path` action**.
7. Makes a third hard product decision explicit: **path spelling is weaker than root witness, and root witness is weaker than same-subject proof**.
8. Packages the result as another continuation archive whose new tranche makes the `path-liveness-contract / missing-path-review / remount-review / rebind-proof / path-liveness-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1120-resilio-path-liveness-remount-witness-and-rebind-ceiling-fragmentation-evaluation.md`
- `1121-path-liveness-contract-sheet-page-live-bind-missing-root-and-rebind-class-interface-spec.md`
- `1122-missing-path-review-page-moved-deleted-remounted-and-trash-return-branches-interface-spec.md`
- `1123-remount-and-external-media-review-page-removable-root-witness-drive-class-and-safe-resume-interface-spec.md`
- `1124-rebind-proof-page-same-subject-old-root-new-root-and-reconnect-cost-interface-spec.md`
- `1125-path-liveness-lineage-receipt-page-loss-cause-root-return-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's path-liveness contract**

This time the reason is especially clear around **missing-path warnings, same-drive move tracking, cross-root breakage, reconnect path drift, returned removable roots, and same-computer external targeting**.
Current official materials simultaneously show that:

- current `Folder not found / Can't open the destination folder` docs still say the warning can mean deletion or moving the folder to another HDD / logical partition, and still distinguish restore-from-trash, point-to-correct-location, and remove-and-add-again as different remedies
- current `Can I move or rename a syncing folder?` docs still say rename is local-only, still limit Windows/macOS tracking to moves within the same drive, still limit Linux to moves inside the sync parent folder, and still say mobile platforms do not support moving sync shares
- current `Disconnecting and Removing Folders` docs still say reconnect may propose a different default path, may create a same-name `(1)` sibling, and still require manual path correction plus `Destination folder is not empty. Add anyway?` to get the old directory back
- current `Can I use Resilio Sync to backup from an internal drive to an externally connected USB drive?` docs still route same-computer internal→external work through local sharing rather than ordinary two-seat path repair
- current `My files don't sync` docs still separately remind the operator to verify that drives are mounted properly when filesystem reachability is in doubt

That candor is useful.
The path-liveness contract is the problem.
AnonSync should not clone a world where the operator still has to translate `missing`, `moved`, `returned`, `reconnect`, and `use this external drive` into continuity class, remount witness, rebind cost, and subject-vs-derivative truth by stitching together several setup and troubleshooting pages.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because path liveness is a real contract with separate truths for path reachability, root witness, subject continuity, peer continuity, and external-target intent, but the present contract still scatters the answer to `did this subject move, disappear, remount, or become a new bind?` across several KB articles instead of owning it as one stable page family.**

## Revision addendum — transfer eligibility, pause semantics, and context gating after rev0328

This revision continues directly from `rev0328` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **pause semantics, weekly scheduler zero-speed windows, Android auto-sleep and battery saver, mobile-data policy, background-priority loss through notification disabling, file-class publish delay, and download-queue priority**.
2. Tightens the non-clone line again: borrow Resilio's candor that `paused`, `sleeping`, `battery stopped`, `Wi‑Fi-only waiting`, `delay-held`, and `priority-deferred` are different truths; refuse any contract where the operator still has to reconstruct `will bytes move now, and what still mutates anyway?` from several articles.
3. Adds one new **Resilio evaluation** document focused on why present-day transfer-eligibility truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for transfer eligibility contract sheet, mobility and power budget review, paused-but-still-mutating page, transfer eligibility proof, and eligibility boundary receipt.
5. Makes one hard product decision explicit: **transfer eligibility is a first-class contract object, and pause/offline/sleep/battery stop/scheduled zero/delay-held/priority-deferred are typed states rather than one badge family**.
6. Makes another hard product decision explicit: **bit movement, local detection, deletion propagation, zero-byte propagation, indexing, peer visibility, publish delay, and queue precedence are separate lanes or modifiers**.
7. Makes a third hard product decision explicit: **policy gates and context gates remain separate, and eligibility is different from immediacy and queue precedence**.
8. Packages the result as another continuation archive whose new tranche makes the `eligibility-contract / mobility-budget-review / paused-but-still-mutating / eligibility-proof / eligibility-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1114-resilio-transfer-eligibility-pause-schedule-and-context-gating-fragmentation-evaluation.md`
- `1115-transfer-eligibility-contract-sheet-page-policy-context-and-lane-truth-interface-spec.md`
- `1116-mobility-and-power-budget-review-page-mobile-data-network-battery-priority-and-schedule-delta-interface-spec.md`
- `1117-paused-but-still-mutating-page-delete-propagation-indexing-and-visibility-truth-interface-spec.md`
- `1118-transfer-eligibility-proof-page-current-gate-basis-next-wake-and-why-not-moving-interface-spec.md`
- `1119-eligibility-boundary-receipt-page-policy-context-proof-and-resume-trigger-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's transfer-eligibility contract**

This time the reason is especially clear around **pause semantics, scheduler zero windows, auto-sleep wake cadence, battery stop thresholds, mobile-data policy, background-priority loss, publish delay, and queue-priority suspension**.
Current official materials simultaneously show that:

- current `How to pause syncing` docs still say pause stops bits movement while zero-sized files, deletions, rescans, and indexing can still proceed
- current `Running Sync on schedule` docs still say scheduled `Paused` windows zero out upload/download speed but still allow zero-sized files, deletions, rescans, indexing, and in some cases upload to non-paused peers
- current `Sync Preferences` docs still expose separate global pause/resume and scheduler controls rather than one unified eligibility object
- current `Configuring Auto Sleep & Battery Saver (Android)` docs still say Auto Sleep can turn the core actually off and later wake to check for changes, while Battery Saver can force a stop below the chosen threshold
- current `Settings on mobile platforms` docs still say mobile data is a device-level gate and that disabling Android notifications can lower background priority enough that Sync may stop working in the background
- current `Setting Delay Time For Syncing` docs still say some file classes can be held for delayed publication, which means eligible is not the same thing as immediate
- current `File download priority` docs still say queued downloads can be reordered, lower-priority downloads can be suspended, and visible queue ordering may differ from the actual priority order

That candor is useful.
The transfer-eligibility contract is the problem.
AnonSync should not clone a world where the operator still has to translate `paused`, `waiting`, `sleeping`, `not moving`, and `moving later` into policy gates, context gates, mutation lanes, wake triggers, and queue/timing modifiers by stitching together several setup and support pages.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because transfer eligibility is a real contract with separate truths for payload movement, local detection, deletion propagation, peer visibility, wake cadence, publish delay, and queue priority, but the present contract still scatters the answer to `will this move now, and if not, why not?` across several KB articles instead of owning it as one stable page family.**

## Revision addendum — placeholder materialization, pin truth, and source-byte witness after rev0327

This revision continues directly from `rev0327` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **Selective Sync mode selection, `.rsls` placeholders as zero-byte visible entries, single-file and subtree hydration, future auto-download after subtree hydration, local reversion to placeholders, mesh-wide delete semantics, ghost-file warnings, and power-user switches that reshape delete behavior**.
2. Tightens the non-clone line again: borrow Resilio's candor that placeholders, hydrated bytes, subtree future-arrival behavior, and source-byte witness are different truths; refuse any contract where the operator still has to infer offline safety and delete scope from several setup and warning pages.
3. Adds one new **Resilio evaluation** document focused on why present-day placeholder/materialization truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for materialization contract sheet, hydration review, local residency review, source-byte witness watch, and materialization lineage receipt.
5. Makes one hard product decision explicit: **visible placeholder, hydrated local copy, pinned local residency, subtree future-arrival commitment, and fully-synced share are different materialization classes**.
6. Makes another hard product decision explicit: **remove-from-device, revert-to-placeholder, remove-share, and delete-everywhere are different intents with different survivor maps and rights ceilings**.
7. Makes a third hard product decision explicit: **placeholder visibility is weaker than source-byte witness, and source-byte witness is weaker than offline guarantee**.
8. Packages the result as another continuation archive whose new tranche makes the `materialization-contract / hydration-review / local-residency-review / byte-witness-watch / lineage-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1108-resilio-placeholder-materialization-pin-truth-and-source-byte-witness-fragmentation-evaluation.md`
- `1109-materialization-contract-sheet-page-placeholder-hydrated-pinned-and-byte-witness-interface-spec.md`
- `1110-hydration-review-page-single-file-subtree-future-arrivals-and-fetch-ceiling-interface-spec.md`
- `1111-local-residency-review-page-remove-from-device-remove-from-all-and-placeholder-survivor-interface-spec.md`
- `1112-source-byte-witness-watch-page-ghost-file-risk-offline-guarantee-and-materialization-debt-interface-spec.md`
- `1113-materialization-lineage-receipt-page-visible-entry-local-bytes-and-source-witness-boundary-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's placeholder/materialization contract**

This time the reason is especially clear around **zero-byte placeholders, single-file vs subtree hydration, future auto-download beneath hydrated subtrees, local reversion vs delete-everywhere, ghost-file demand failure, and power-user mutation gates**.
Current official materials simultaneously show that:

- current `Selective Sync` docs still say the mode can be chosen at connect time, after connect, and as the default for linked-device arrivals, and that new files can arrive as placeholders while current ones remain full
- current `What Is an RSLS File?` docs still say placeholders are zero-byte stand-ins, that subtree hydration changes future-arrival behavior, that `Remove from this device` is local-only, and that if all peers revert to placeholders there may be no actual file left anywhere
- current `Synchronization Modes` docs still say visible placeholders are not full files, that demand fetch requires a peer with the real bytes online, and that delete behavior differs from local placeholder reversion
- current `Cannot download files / There are no source peers online for too long time` docs still preserve the ghost-file class where an advertised file later has no byte-bearing source left
- current `Power user preferences` docs still say policy can disable `Remove from all devices` or force placeholder recreation on removal

That candor is useful.
The materialization contract is the problem.
AnonSync should not clone a world where the operator still has to translate `I can see it`, `I opened it once`, `I want it kept here`, and `I can get it later` into actual materialization classes and witness boundaries by stitching together setup, placeholder, warning, and preference pages.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because placeholder-backed sync is a real contract with separate classes for visible metadata, local bytes, ongoing local residency, subtree future-arrival commitment, and source-byte witness, but the present contract still scatters offline-safety and delete-scope truth across several KB articles instead of owning them as one stable page family.**

## Revision addendum — maintenance health, repair rung, and salvage boundary after rev0326

This revision continues directly from `rev0326` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **hidden background work that is not necessarily stuck, watcher exhaustion that downgrades change detection into rescans, external lock contention, folder-scoped database suspension, `.sync` spine loss, memory-driven destructive rebuild guidance, and generic `my files don't sync` troubleshooting that still fans out into distinct causes and remedies**.
2. Tightens the non-clone line again: borrow Resilio's candor that health warnings have very different severity classes; refuse any contract where the operator still has to infer whether the safe next step is `wait`, `restart`, `reconnect`, `re-add`, `delete .sync`, or `share again` by reading several troubleshooting articles.
3. Adds one new **Resilio evaluation** document focused on why present-day maintenance-health truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for health warning contract sheet, health triage review, repair rung review, health proof, and health lineage receipt.
5. Makes one hard product decision explicit: **busy work, degraded detection, blocked transfer, suspended subject, and destructive-rebuild recommendation are different health verdicts and must not collapse into one generic `not syncing` state**.
6. Makes another hard product decision explicit: **restart, reconnect-same-destination, re-add, sidecar recreation, and peer-wide re-share are distinct repair rungs with different survivor and destruction boundaries**.
7. Makes a third hard product decision explicit: **archive/history review, partial-download residue, and evidence capture must appear before destructive repair steps rather than after the operator has already crossed the state-loss boundary**.
8. Packages the result as another continuation archive whose new tranche makes the `health-warning-contract / triage-review / repair-rung-review / health-proof / lineage-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1102-resilio-maintenance-health-warning-repair-rung-and-salvage-boundary-fragmentation-evaluation.md`
- `1103-health-warning-contract-sheet-page-pressure-lock-spine-and-repair-class-interface-spec.md`
- `1104-health-triage-review-page-busy-recovering-rescan-only-suspended-and-corrupt-verdict-interface-spec.md`
- `1105-repair-rung-review-page-restart-reconnect-readd-and-salvage-boundary-interface-spec.md`
- `1106-health-proof-page-recovered-degraded-rescan-only-and-support-escalation-ceiling-interface-spec.md`
- `1107-health-lineage-receipt-page-warning-basis-repair-rung-and-state-loss-boundary-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's maintenance-health contract**

This time the reason is especially clear around **hidden background work, watcher-budget exhaustion, external locks, folder-scoped suspension, `.sync` spine loss, memory-driven destructive rebuild, and explicit salvage-before-repair obligations**.
Current official materials simultaneously show that:

- current `Some internal tasks are taking time to complete` docs still say the runtime may be busy and recover on its own rather than truly stuck
- current watcher-exhaustion docs still say Sync can degrade into manual/periodic-rescan discovery rather than live notify
- current `Locked files` docs still say another application may be blocking transfer while Sync cannot identify the locker for you
- current `Database error` docs still suspend only the affected folder and climb a repair ladder from restart to reconnect to re-add
- current `Service files missing` docs still suspend the folder, explicitly warn about same-folder/two-instance corruption, and require archive review before deleting `.sync`
- current `Out of memory` docs still say historical/deleted state remains in the database and that the only way to reduce RAM is destructive remove-and-share-again of the biggest folders
- current `My files don't sync` docs still scatter many distinct causes across ignore drift, xattrs, locks, overwrite posture, permissions, encoding/path ceilings, tree-merge limits, filesystem failure, notification loss, free-space pressure, partial files, and time skew

That candor is useful.
The maintenance-health contract is the problem.
AnonSync should not clone a world where the operator still has to translate a symptom like `not syncing` into severity, repair rung, salvage duty, and proof ceiling by stitching together warnings and troubleshooting pages.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because maintenance health is a real contract with separate classes for busy-but-recovering work, rescan-only degraded detection, external block, folder-scoped suspension, sidecar/spine loss, and memory-driven destructive rebuild, but the present contract still scatters the repair ladder and salvage duty across several KB articles instead of owning them as one stable page family.**

## Revision addendum — self-edge derivation, source-coupled lifecycle, and entitlement cliffs after rev0324

This revision continues directly from `rev0324` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **desktop-only local sharing, self-only peer topology, no tracker/relay/LAN discovery for the derivative lane, parent/child loop bans, inherited-rights ceilings, source-driven downgrade, source-coupled removal, manual reattach after source return, placeholder-limited byte promises, and Pro-license cliffs**.
2. Tightens the non-clone line again: borrow Resilio's candor that same-host derivation is real; refuse any contract where the operator still has to expand `sync local folders` into a self-edge topology, a rights ceiling, a lifecycle dependency, and a license-sensitive continuity story.
3. Adds one new **Resilio evaluation** document focused on why present-day self-edge derivation is still too convenience-shaped to clone even though the distinctions are useful.
4. Adds five new **interface specs** for self-edge derivation contract sheet, self-edge topology review, derived-rights and lifecycle review, self-edge materialization and entitlement watch, and self-edge lineage receipt.
5. Makes one hard product decision explicit: **same-host self-edge is its own topology class, not just another share or another path**.
6. Makes another hard product decision explicit: **rights inheritance is a ceiling below the source and must never sound like derivative equality or delegated ownership**.
7. Makes a third hard product decision explicit: **source removal, source return, placeholder scarcity, and license expiry are first-class continuity facts for the derivative rather than hidden footnotes**.
8. Packages the result as another continuation archive whose new tranche makes the `self-edge-contract / topology-review / rights-lifecycle-review / materialization-entitlement-watch / lineage-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1090-resilio-self-edge-local-derivation-loop-rights-and-license-cliff-evaluation.md`
- `1091-self-edge-derivation-contract-sheet-page-source-self-peer-loop-ceiling-and-lifecycle-coupling-interface-spec.md`
- `1092-self-edge-topology-review-page-parent-child-loop-ban-and-fanout-boundary-interface-spec.md`
- `1093-derived-rights-and-lifecycle-review-page-owner-ceiling-source-downgrade-and-reattach-requirement-interface-spec.md`
- `1094-self-edge-materialization-and-entitlement-watch-page-placeholder-dependence-discovery-bypass-and-license-cliff-interface-spec.md`
- `1095-self-edge-lineage-receipt-page-source-target-self-peer-and-suspension-boundary-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's self-edge derivation contract**

This time the reason is especially clear around **self-only peer topology, loop bans, inherited-rights ceilings, source-coupled removal/reattach, placeholder-limited byte promises, and license cliffs**.
Current official materials simultaneously show that:

- current `Sharing a folder locally` docs still say the derivative is desktop-only, self-only, and not an ordinary remote-peer lane
- the same docs still remove standard tracker/relay/LAN discovery semantics from the derivative preferences
- the same docs still ban parent/subdirectory loop shapes
- the same docs still cap derivative rights below the source, forbid `Owner`, and can require remove-and-re-share to change access on Advanced shares
- the same docs still say source-right downgrades flow down, source removal tears the derivative down, and source return still requires manual derivative reattachment
- the same docs still say derivative Selective Sync policy can diverge while byte availability still depends on what the source actually has
- the same docs still say expiry or license removal can make the derivative unavailable and stop syncing

That candor is useful.
The self-edge contract is the problem.
AnonSync should not clone a world where the operator still reaches the feature through `Sync local folders` convenience language and then has to remember topology, rights, lifecycle, byte, and entitlement cliffs from caveats.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because same-host self-edge derivation is a real topology with self-only reachability, inherited-rights ceilings, loop bans, source-coupled deletion/reattach behavior, placeholder-limited byte promises, and license cliffs, but the present contract still compresses that meaning into a convenience-first action instead of owning it as one stable page family.**

## Revision addendum — portable-name truth, canonical collision, and name-plane propagation after rev0323

This revision continues directly from `rev0323` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **case/encoding conflict artifacts, invalid trailing-name forms, UTF-8/path-length expectations, local-only folder rename, custom UI naming, archive-assisted rename reuse, and symlink target-boundary limits**.
2. Tightens the non-clone line again: borrow Resilio's candor that names, labels, moves, and alias edges are materially different; refuse any contract where the operator still has to reconstruct `what name changed, who will see it, and can every target actually carry it?` from several articles.
3. Adds one new **Resilio evaluation** document focused on why present-day portable-name truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for portable-name contract sheet, canonical-name portability review, name-plane propagation review, rename-scope and byte-reuse proof, and portable-name lineage receipt.
5. Makes one hard product decision explicit: **path existence is weaker than portable-name admissibility**.
6. Makes another hard product decision explicit: **canonical portable name, disk basename, presented title, artifact label, and peer-visible alias are separate public planes**.
7. Makes a third hard product decision explicit: **rename scope and byte reuse are separate truths, and alias-edge target boundaries must stay explicit wherever rename meaning could be overclaimed**.
8. Packages the result as another continuation archive whose new tranche makes the `portable-name-contract / canonical-portability-review / name-plane-propagation / rename-scope-proof / lineage-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1084-resilio-portable-name-collision-alias-propagation-and-move-scope-fragmentation-evaluation.md`
- `1085-portable-name-contract-sheet-page-canonical-collision-alias-planes-and-propagation-scope-interface-spec.md`
- `1086-canonical-name-portability-review-page-case-encoding-invalid-symbol-and-path-budget-interface-spec.md`
- `1087-name-plane-propagation-review-page-disk-name-ui-label-offer-alias-and-local-only-rename-interface-spec.md`
- `1088-rename-scope-and-byte-reuse-proof-page-local-path-move-archive-assisted-remote-reuse-and-symlink-boundary-interface-spec.md`
- `1089-portable-name-lineage-receipt-page-canonicalization-alias-plane-delta-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's portable-name contract**

This time the reason is especially clear around **case/encoding conflict artifacts, invalid trailing-name forms, UTF-8 and path-length expectations, local-only folder rename, custom UI naming, archive-assisted rename reuse, and symlink target-boundary limits**.
Current official materials simultaneously show that:

- current conflict docs still say case/encoding disagreement can create conflict artifacts that must not be cleaned up naively
- current troubleshooting docs still treat invalid names, UTF-8 expectations, and path limits as real sync boundaries
- current naming docs still separate UI custom naming from on-disk rename and peer propagation
- current move/rename docs still separate local-only folder rename from cross-partition rebind-like behavior
- current rename internals docs still make cheap remote reuse depend on retention/archive state
- current symlink docs still separate preserving a link object from syncing its target tree

That candor is useful.
The naming contract is the problem.
AnonSync should not clone a world where the operator still needs conflict repair lore, troubleshooting notes, share-naming notes, rename/move caveats, and symlink caveats to know what changed, whether it propagates, whether the target can carry it, or whether byte reuse is actually available.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful distinctions between canonical portable name, local disk name, presented label, artifact alias, local-only move/rename scope, archive-assisted reuse, and alias-edge target scope are real, but the present contract still hides too much meaning across conflict, troubleshooting, naming, move/rename, and symlink articles instead of owning portable-name truth as one stable page family.**

## Revision addendum — host integration, signer trust, shell activation, and uninstall clearance after rev0322

This revision continues directly from `rev0322` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **SmartScreen signer reputation, silent-install UAC consent, host-wide install artifacts, Finder/Explorer shell-surface activation, NTFS/selective prerequisites, shell-registration repair, CLI install-vs-launch distinctions, and uninstall survivors such as shared folders, service storage, and hidden archives**.
2. Tightens the non-clone line again: borrow Resilio's candor that install trust, host mutation, shell activation, and uninstall residue are materially different; refuse any contract where the operator still has to reconstruct `trusted`, `integrated`, and `gone` from separate setup, troubleshooting, and uninstall articles.
3. Adds one new **Resilio evaluation** document focused on why present-day host-integration truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for host integration contract sheet, installer trust review, shell-surface activation proof, uninstall clearance review, and host-integration lineage receipt.
5. Makes one hard product decision explicit: **host integration is not the same as app presence**.
6. Makes another hard product decision explicit: **signer trust, OS consent, shell-surface activation, and uninstall clearance are separate truths and must never collapse into `installed` or `removed`**.
7. Makes a third hard product decision explicit: **program removal is weaker than clearance, and clearance is weaker than subject-data erasure or archive elimination**.
8. Packages the result as another continuation archive whose new tranche makes the `installer-trust / host-mutation-scope / shell-proof / clearance-review / lineage-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1078-resilio-host-integration-signer-trust-shell-activation-and-uninstall-clearance-fragmentation-evaluation.md`
- `1079-host-integration-contract-sheet-page-installer-trust-os-consent-shell-surfaces-and-clearance-state-interface-spec.md`
- `1080-installer-trust-review-page-codesign-reputation-uac-consent-and-host-mutation-scope-interface-spec.md`
- `1081-shell-surface-activation-proof-page-finder-explorer-extension-state-filesystem-eligibility-and-registration-truth-interface-spec.md`
- `1082-uninstall-clearance-review-page-program-removal-settings-residue-shell-release-and-shared-data-survivor-interface-spec.md`
- `1083-host-integration-lineage-receipt-page-trust-prompts-shell-surface-state-and-clearance-ceiling-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's host-integration contract**

This time the reason is especially clear around **SmartScreen signer reputation, silent-install UAC consent, Finder/Explorer shell-surface activation, NTFS/selective prerequisites, shell-registration repair, and uninstall survivors**.
Current official materials simultaneously show that:

- SmartScreen reputation can block installation of a newly signed package
- silent install still crosses UAC and mutates concrete host surfaces
- host shell affordances depend on real eligibility and registration gates
- uninstall can still leave shared folders, archives, service state, registry/preferences, or pinned shell hooks behind
- launch mode and install mode are not the same contract

That candor is useful.
The host-integration contract is the problem.
AnonSync should not clone a world where the operator still needs installer notes, shell troubleshooting, CLI switch lore, and uninstall articles to know whether a package is trusted enough to install, whether shell affordances are truly active, or whether removal actually cleared the host footprint.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful distinctions between signer trust, OS consent, host mutation scope, shell-surface activation, uninstall clearance, and shared-data/archive survivors are real, but the present contract still hides too much meaning across SmartScreen, silent-install, shell-troubleshooting, CLI, and uninstall pages instead of owning host integration as one stable page family.**

## Revision addendum — same-host multi-instance namespace, path ownership, and external-world handoff after rev0320

This revision continues directly from `rev0320` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **Linux same-host multi-instance support, manual port assignment for later instances, default-versus-explicit storage roots, runtime principal differences, update-time same-user/same-parameter continuity, and destructive same-path double-claim on one host or one external disk**.
2. Tightens the non-clone line again: borrow Resilio's candor that `you can run more than one instance` is real; refuse any contract where the operator still has to reconstruct `what must be distinct, what can still collide, and when does a second bind become corruption?` from Linux guide notes, config/storage commentary, update ritual, and a later repair article.
3. Adds one new **Resilio evaluation** document focused on why present-day same-host multi-instance truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for instance namespace contract sheet, second-instance bringup review, same-path claim collision warning, shared external-storage review, and instance lineage receipt.
5. Makes one hard product decision explicit: **same-host multi-instance bringup is a namespace contract, not a power-user convenience**.
6. Makes another hard product decision explicit: **listener separation, storage-root separation, principal continuity, and subject-path ownership are separate truths and must never collapse into `another process`**.
7. Makes a third hard product decision explicit: **reusing removable/external storage across runtimes is an ownership handoff that requires resume / successor / branch / inspect review rather than a raw add-folder path**.
8. Packages the result as another continuation archive whose new tranche makes the `instance-namespace / second-bringup / same-path-collision / external-world-handoff / lineage-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1066-resilio-same-host-multi-instance-port-namespace-storage-world-and-claim-collision-evaluation.md`
- `1067-instance-namespace-contract-sheet-page-runtime-identity-listener-storage-and-claim-ceiling-interface-spec.md`
- `1068-second-instance-bringup-review-page-port-separation-storage-root-identity-and-ui-audience-interface-spec.md`
- `1069-same-path-claim-collision-warning-page-hidden-state-corruption-and-branch-vs-reattach-interface-spec.md`
- `1070-shared-external-storage-review-page-removable-world-reuse-and-safe-ownership-handoff-interface-spec.md`
- `1071-instance-lineage-receipt-page-runtime-namespace-storage-root-subject-ownership-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's same-host multi-instance contract**

This time the reason is especially clear around **Linux multiple-instance support, manual port assignment, default working-directory storage, explicit `--storage` / `--identity` worlds, same-user continuity on update, service-user versus current-user runtime, and `.sync` corruption when two runtimes claim the same folder or one external disk is reused across instances**.
Current official materials simultaneously show that:

- the current `Guide to Linux, and Sync peculiarities` article still says Linux can run multiple instances but the second and later ones require manual port assignment
- that same article still says `--storage` defines where settings live and otherwise `.sync` storage is created in the current directory, while `--identity` and `--license` also depend on explicit storage rooting
- the current `Running Sync in configuration mode` article still says a non-default `storage_path` creates new settings there and a listening-port value of `0` allocates a random port
- the current `Installing Sync package on Linux` article still distinguishes the default `rslsync` service user from an alternative current-user service mode, with different continuity and permission implications
- the current `Updating installation to Resilio Sync v3` article still says non-default `/config` or `/storage` launches must restart with the same parameters and the same user to preserve the same storage folder and configuration
- the current `Service files missing` article still says that adding the same folder to Sync A and then Sync B on the same computer, or reusing one external disk as storage for two instances, can corrupt the former instance's internal files and make further synchronization impossible

That candor is useful.
The multi-instance contract is the problem.
AnonSync should not clone a world where the operator still needs Linux-note memory plus a later repair article to know whether they created a distinct runtime namespace, accidentally opened a new storage world, or destructively double-claimed a continuity-bearing path.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful distinctions between runtime namespace, listener ownership, storage world, runtime principal, subject-path ownership, and removable-world handoff are real, but the present contract still hides too much meaning across Linux notes, config/storage commentary, update ritual, and repair guidance instead of owning same-host multi-instance bringup as one stable page family.**

## Revision addendum — directory admission, root ceiling, picker authority, and config-authored roster after rev0319

This revision continues directly from `rev0319` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **configuration-mode path admission, `directory_root_policy`, `dir_whitelist`, storage-path world selection, Standard-only config subjects, and config-authored roster override / WebUI suppression**.
2. Tightens the non-clone line again: borrow Resilio's candor that not every visible or existing path is equally admissible; refuse any contract where the operator still has to reconstruct `can I add this folder, who is filtering the picker, and did config just replace my subject set?` from sample-config commentary and storage notes.
3. Adds one new **Resilio evaluation** document focused on why present-day directory-admission truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for directory admission contract sheet, root-ceiling review, picker visibility authority, config-authored subject-set review, and directory-admission lineage receipt.
5. Makes one hard product decision explicit: **path existence is not path admissibility**.
6. Makes another hard product decision explicit: **root ceiling and picker visibility are separate truths and must never collapse into one browse result**.
7. Makes a third hard product decision explicit: **config-authored subject import is roster-authority replacement, not startup convenience**.
8. Packages the result as another continuation archive whose new tranche makes the `admission-authority / root-ceiling / picker-visibility / config-authored-roster / denial-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1060-resilio-directory-admission-root-ceiling-whitelist-and-config-authorship-fragmentation-evaluation.md`
- `1061-directory-admission-contract-sheet-page-path-admissibility-root-ceiling-and-authorship-basis-interface-spec.md`
- `1062-root-ceiling-review-page-directory-root-policy-descendant-only-creation-and-direct-root-denial-interface-spec.md`
- `1063-picker-visibility-authority-page-allowlisted-browse-surfaces-hidden-paths-and-direct-entry-boundary-interface-spec.md`
- `1064-config-authored-subject-set-review-page-standard-only-folders-webui-suppression-and-roster-replacement-interface-spec.md`
- `1065-directory-admission-lineage-receipt-page-requested-path-verdict-blocking-authority-and-roster-authorship-delta-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's directory-admission contract**

This time the reason is especially clear around **configuration-mode path admission, `directory_root_policy`, `dir_whitelist`, Standard-only config subjects, config-authored roster override, and storage-path world selection**.
Current official materials simultaneously show that:

- the current `Running Sync in configuration mode` article still says config mode applies pre-configured settings at start and is useful for applying the same settings on a number of machines
- that same article still says a non-default `storage_path` creates new settings there instead of the default location
- that same article still says Linux `directory_root_policy` supports `all` versus `belowroot`, and `belowroot` denies attempts to use `adddir` directly within `directory_root` while allowing subdirectories
- that same article still says `dir_whitelist` defines which directories can be used to store sync shares and that others will not be visible in the folder picker
- that same article still says config mode can set up only Standard folders, not Advanced
- that same article still says if shared folders are set in config, WebUI is disabled and the configured shared directories override folders previously added from WebUI
- the current `Sync Storage folder` article still says the storage folder keeps current configuration, auxiliary settings files, and shares' database state, and that desktop default location changes through config mode

That candor is useful.
The admission contract is the problem.
AnonSync should not clone a world where the operator still needs config-file lore to know whether a path is admissible, whether the picker is filtered, whether direct-root creation is denied, or whether the active subject roster is still theirs to mutate.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful distinctions between path existence, path admissibility, root ceiling, picker visibility, subject class, and roster authorship are real, but the present contract still hides too much meaning inside configuration commentary instead of owning directory admission as one stable page family.**

## Revision addendum — pre-login launchd, group-write contract, and headless audience after rev0318

This revision continues directly from `rev0318` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **macOS pre-login launch via launchd, dedicated runtime user, root-owned boot orchestration, `use_gui: false`, LAN-exposed WebUI, `Umask 2` group-write discipline, placeholder caveats, and browser/manual intake losses**.
2. Tightens the non-clone line again: borrow Resilio's candor that `run before login` is materially different; refuse any contract where the operator still has to reconstruct `what world did I create, who owns it, what file-creation contract now applies, and what desktop affordances did I lose?` from recipe prose and adjacent WebUI docs.
3. Adds one new **Resilio evaluation** document focused on why present-day pre-login/headless truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for pre-login runtime contract sheet, headless launch review, group-write discipline proof, pre-login mode caveat page, and pre-login lineage receipt.
5. Makes one hard product decision explicit: **pre-login startup is a world-class change, not a startup checkbox**.
6. Makes another hard product decision explicit: **file-creation discipline under the chosen principal/umask is first-class runtime truth rather than setup folklore**.
7. Makes a third hard product decision explicit: **headless control audience and session-affordance loss must be reviewed separately from mere launch timing**.
8. Packages the result as another continuation archive whose new tranche makes the `prelogin-launch / dedicated-principal / group-write-contract / headless-control / caveat-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1054-resilio-prelogin-launchd-principal-groupwrite-and-headless-webui-fragmentation-evaluation.md`
- `1055-prelogin-runtime-contract-sheet-page-session-boundary-launch-class-and-principal-world-interface-spec.md`
- `1056-headless-launch-review-page-launchd-user-storage-home-webui-audience-and-delay-interface-spec.md`
- `1057-group-write-discipline-proof-page-umask-delivery-ownership-and-sync-stop-risk-interface-spec.md`
- `1058-prelogin-mode-caveat-page-placeholders-link-handoff-and-session-losses-interface-spec.md`
- `1059-prelogin-lineage-receipt-page-launch-class-principal-webui-exposure-and-posix-contract-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's pre-login/headless-runtime contract**

This time the reason is especially clear around **macOS launchd pre-login setup, a dedicated runtime user, root-owned orchestration, `use_gui: false`, LAN-exposed WebUI, `Umask 2` group-write discipline, placeholder caveats, and browser/manual intake losses**.
Current official materials simultaneously show that:

- the current `Launching Sync on Mac without user logged in` article still says ordinary app start happens at user login under the current account, while pre-login launch requires `launchd`, a new user, and root permissions
- that same article still uses a config with `use_gui: false`, a separate `storage_path`, `listen : 0.0.0.0:8888`, explicit login/password, `RunAtLoad`, `KeepAlive`, `UserName`, and `Umask 2`
- that same article still warns that newly created files inside synced folders must preserve the reviewed group-write posture or Sync can stop syncing those files
- that same article still adds a selective-sync caveat by telling the operator to set `"enable_placeholders": false`
- the current `Configuring WebUI` article still says app-install WebUI is config-file driven, that `0.0.0.0` widens reach to the LAN, that HTTP is default unless `force_https` is configured, and that link-click intake in WebUI does not work and must be re-entered manually
- the current `Does Sync work in background?` article still says ordinary macOS background behavior can simply mean the minimized app, which is a materially different runtime shape from pre-login launchd mode

That candor is useful.
The launch contract is the problem.
AnonSync should not clone a world where the operator still needs recipe memory and POSIX intuition to know whether `run before login` preserved the same world, created a new principal-owned storage home, widened control exposure, required a new file-creation discipline, or dropped ordinary handler parity.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful distinctions between interactive background use, pre-login headless runtime, runtime principal, storage home, WebUI audience, and file-creation discipline are real, but the present contract still hides too much meaning across one setup recipe plus adjacent WebUI/background docs instead of owning pre-login runtime as one stable page family.**

## Revision addendum — discovery bootstrap authority, fallback envelope, and relay inevitability after rev0317

This revision continues directly from `rev0317` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **bootstrap catalog fetch, tracker/relay address authority, predefined-host fallback, `No tracker connection` semantics, proxy asymmetry, and relay dependence**.
2. Tightens the non-clone line again: borrow Resilio's candor that connectivity is lane-shaped; refuse any contract where the operator still has to reconstruct `who currently defines discovery infrastructure, what fallback remains, and whether relay is already inevitable` from several articles.
3. Adds one new **Resilio evaluation** document focused on why present-day discovery-bootstrap truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for bootstrap authority contract sheet, bootstrap outage review, egress-only reachability review, discovery fallback proof, and bootstrap lineage receipt.
5. Makes one hard product decision explicit: **bootstrap authority is first-class state, not hidden support lore**.
6. Makes another hard product decision explicit: **fallback envelope must be explicit rather than inferred from one warning string**.
7. Makes a third hard product decision explicit: **pairwise relay inevitability is computed and shown before the operator learns it from poor throughput**.
8. Packages the result as another continuation archive whose new tranche makes the `bootstrap-authority / fallback-envelope / egress-only-posture / relay-inevitability / durable-receipt` seam explicit in the reading order and page family.

## Revision addendum — service promotion, principal switch, and service-world continuity

This revision continues directly from `rev0316` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **service install migrate-vs-clean branching, current-user vs Local Service vs Local System runtime ownership, mapped-drive invisibility, UNC fallback notification loss, service-storage config authority, and loopback-only WebUI default**.
2. Tightens the non-clone line again: borrow Resilio's candor that service cutover is materially real; refuse any contract where the operator still has to reconstruct `did I keep the same seat or start a different service world?` from install, troubleshooting, config, preferences, and uninstall prose.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio service-promotion truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: service promotion contract sheet, principal switch review, service world preview, service cutover proof, and service lineage receipt.
5. Makes one hard product decision explicit: **service promotion is a continuity-bearing cutover, not a backgrounding checkbox**.
6. Makes another hard product decision explicit: **principal change is a world switch unless storage-world continuity is proven**.
7. Makes a third hard product decision explicit: **path reach, observation grade, and control exposure are separate truths from continuity and must be reviewed separately**.
8. Packages the result as another continuation archive whose new tranche makes the `migrate / clean-branch / principal-switch / service-world / cutover-proof` seam explicit in the reading order and page family.

New docs in this tranche:

- `1042-resilio-service-promotion-principal-switch-and-service-world-fragmentation-evaluation.md`
- `1043-service-promotion-contract-sheet-page-interactive-seat-service-seat-principal-and-continuity-class-interface-spec.md`
- `1044-principal-switch-review-page-current-user-localservice-localsystem-mapped-paths-and-reconnect-cost-interface-spec.md`
- `1045-service-world-preview-page-storage-root-empty-state-attribution-and-observation-grade-interface-spec.md`
- `1046-service-cutover-proof-page-migrated-roster-webui-audience-and-post-restart-observation-truth-interface-spec.md`
- `1047-service-lineage-receipt-page-source-runtime-target-principal-storage-world-and-reconnect-obligations-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's service-promotion contract**

This time the reason is especially clear around **installer-time migrate-vs-clean branching, principal-specific service storage roots, mapped-drive loss, UNC fallback notification downgrade, loopback-only default WebUI exposure, and cutovers that can widen path reach while still opening a different storage world**.
Current official materials simultaneously show that:

- the current `Running Sync as a service on Windows` article still offers **migrate settings** versus **clean installation**, and still says migrated installs should surface the old shares afterward
- the current `Sync Service Troubleshooting on Windows` article still says mapped drive letters are unavailable to services because interactive logon did not occur
- that same article still says the UNC workaround loses immediate file-update notifications and pushes discovery to **rescan** or **restart**
- that same article still says switching to **Local System** can expose an empty-looking world because a different service storage folder is now active and old folders must be **re-add / re-share / reconnect**ed
- the current `Running Sync in configuration mode` article still says service config mode works only by placing `sync.conf` in the **service storage**
- the current troubleshooting docs still say service WebUI is **127.0.0.1** by default without config and must be changed and restarted for broader reach
- the current uninstall docs still publish different service storage roots for local-user, LocalService, and LocalSystem service seats

That candor is useful.
The service cutover contract is the problem.
AnonSync should not clone a world where the operator still needs article memory to know whether `running as service` preserved the same seat, widened path access but downgraded observation, opened a different principal-owned storage world, or quietly created a clean branch that now needs reconnect work.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful distinctions between migrate-vs-clean install, runtime principal, mapped-path reach, notification grade, service storage, and WebUI audience are real, but the present contract still hides too much meaning across install instructions, troubleshooting notes, config-mode docs, preferences, and uninstall guidance instead of owning service cutover as one stable page family.**

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

## Latest addendum — automatic ingress mutation, port lease, and router side-effects after rev0321

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **ingress exposure contract sheet / port-mapping review / router side-effect warning / directness proof / ingress lineage receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `did I just change a local port preference, or did I ask my network to open ingress toward this runtime?` depends on combining several pages:

- current `Sync Preferences` docs still say the listening port covers incoming TCP plus incoming and outgoing UDP, is random on install unless changed, and that manual NAT forwarding must target that port
- those same docs still say `Use UPnP port mapping` sends UPnP and NAT-PMP packets to the router and still warn that some printers, scanners, and other equipment can mishandle UPnP and stop processing requests
- current `Running Sync in configuration mode` docs still expose the same router-mapping choice and still say port `0` allocates a random port
- current `What ports and protocols are used by Sync?` docs still split tracker, direct peer traffic, relay fallback, LAN discovery, and automatic port-mapping traffic into different lanes
- current `Peers aren't connecting` and `Download/upload speed is very slow` docs still say that directness may require opening the listening port on routers and firewalls, while relay remains the fallback if direct connection is not possible
- the current changelog still records fixes for UPnP behavior and listening-port persistence, which helps confirm this class is operationally real rather than theoretical

So the tighter non-clone line is:

> borrow Resilio's candor that the listening port, router mutation, manual forwarding, and relay fallback are materially different truths — but refuse any product contract where `help me connect directly` still makes the operator merge preferences, config notes, troubleshooting, speed tips, and changelog archaeology to know whether an external audience was merely requested, visibly leased, or actually proven.

That yields five more ordinary product-owned pages:

- **Ingress exposure contract sheet**
- **Port-mapping review**
- **Router side-effect warning**
- **Directness proof**
- **Ingress lineage receipt**


## Latest addendum — stop proof, hidden runtime, and restart provenance after rev0325

Another current official Resilio pass now sharpens one more reason to **adapt, not clone**:

- **runtime stop contract sheet / shutdown drain review / runtime stop proof / restart provenance page / runtime stop lineage receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `did I really stop Sync, or did I only dismiss one surface while runtime or future boot re-entry still exists?` depends on combining several pages:

- current `Running Sync as a service on Windows` docs still say service mode can run regardless of logged-in user and under `System`, `Local Service`, or current user
- current `Does Sync work in background?` docs still say desktop can keep running when hidden, Android can run in background unless killed, iOS cannot sync in background, and shutdown/re-open can trigger re-indexing that affects overwrite chronology after offline edits
- current `Sync interface on Android` docs still expose a stronger explicit `Exit` verb that `shuts Sync down correctly`
- current `Settings on mobile platforms` docs still say disabling Android notifications lowers Sync priority and may force background work to stop
- current `Sync Preferences` docs still expose `Start Sync on startup` as a future boot re-entry choice rather than present stop proof
- current update/install guides still distinguish process stop, service stop, and relaunch with the same parameters and same user to preserve continuity

So the tighter non-clone line is:

> borrow Resilio's candor that hidden runtime, service runtime, Android exit, iOS foreground-only limits, startup re-entry, and restart chronology are materially different truths — but refuse any product contract where `close`, `stop`, and `won't come back` still make the operator merge service docs, mobile docs, settings, and update instructions to know what actually happened.

That yields five more ordinary product-owned pages:

- **Runtime stop contract sheet**
- **Shutdown drain review**
- **Runtime stop proof**
- **Restart provenance page**
- **Runtime stop lineage receipt**


## Latest addendum — non-authority convergence, empty-target purge, and forced source-heal after rev0330

Another current official Resilio pass now sharpens one more reason to **adapt, not clone**:

- **non-authority convergence contract sheet / read-only divergence review / empty-target purge review / forced source-heal proof / non-authority convergence lineage receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `what happens to local divergence on a seat that is not allowed to author shared truth here?` depends on combining several pages:

- current `Folder Types and Management` docs still say Read Only seats cannot send additions, deletions, or edits and may stop receiving updates to locally changed files
- current `Sync Share Dialog (Desktop)` docs still say Read Only peers can make changes locally, but none of those changes sync outward
- current `Folder Preferences` docs still say `Overwrite any changed files` is potentially destructive and disabled for Read-only folders with Selective Sync ON
- current `Encrypted folders` docs still say encrypted peers are Read Only, always have overwrite-heal active, and do not support Selective Sync
- current `Power user preferences` docs still publish `overwrite_changes`, `folder_defaults.delete_unknown_files`, and `sync_ro_delete_unknown_file`, including the warning that the last one works for an empty RO target and is not optimized for pre-seeded folders

So the tighter non-clone line is:

> borrow Resilio's candor that non-authority seats can suspend, auto-heal, preserve local-only survivors, or even purge unknown files under hidden posture — but refuse any product contract where `what exactly happens to my local divergence here?` still makes the operator merge permission docs, folder preferences, encrypted-seat caveats, and power-user tables to understand whether edits heal, additions strand locally, or an allegedly empty target may be destructively cleaned.

That yields five more ordinary product-owned pages:

- **Non-authority convergence contract sheet**
- **Read-only divergence review**
- **Empty-target purge review**
- **Forced source-heal proof**
- **Non-authority convergence lineage receipt**

## Latest addendum — identity graph adoption, certificate takeover, and containment reset after rev0332

Another current official Resilio pass now sharpens one more reason to **adapt, not clone**:

- **identity-graph adoption contract sheet / certificate takeover review / linked-graph default arrival and rights page / identity containment reset proof / identity lineage receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `if I link this device into that identity now, what survives, what gets replaced, and what is the honest containment move if one seat becomes untrusted?` depends on combining several pages:

- current `Sync Private Identity & Linking My Devices` docs still say linking is directional, one side can take over the other's certificate/fingerprint/share roster, all linked devices see all folders, unlink is local-only, and hiding an offline device is not unlinking
- the same current identity docs still warn against v2↔v3 linking because license/UI/share configuration can conflict
- current `Synchronization Modes` docs still say linked-device arrivals default into `Disconnected`, `Selective Sync`, or `Synced`, while the source side effectively begins with full data / owner posture
- current `How to manually set the location of the folders synced across linked devices?` docs still say `Disconnected` is the branch for manual target-path authorship
- current `How to create a Read Only folder while syncing across linked devices?` docs still say linked-device arrival defaults to Owner and that a real RO outcome requires leaving the linked-device lane and manually using a Standard-folder RO key
- current `Can I change the name of my Sync identity?` and `If your device is stolen` docs still say identity rename / compromise response can require unlink, new certificate generation, storage cleanup, relink, and reshare
- current `How to apply license key and share license seats` docs still say Business license ownership belongs to one identity and can be stolen by directly applying the license to another identity

So the tighter non-clone line is:

> borrow Resilio's candor that identity linking is a graph-level act with certificate direction, automatic arrival posture, owner-default rights, containment blast radius, and license-owner coupling — but refuse any product contract where `Link device` still makes the operator merge identity docs, mode docs, RO workaround docs, rename guidance, stolen-device containment, and licensing notes to know what graph is being adopted and what honest reset remains if trust fails.

That yields five more ordinary product-owned pages:

- **Identity-graph adoption contract sheet**
- **Certificate takeover review**
- **Linked-graph default arrival and rights page**
- **Identity containment reset proof**
- **Identity lineage receipt**

## Latest addendum — subject architecture family, key-domain vs certificate-domain governance, and encrypted-derivative lanes after rev0334

Another current official Resilio pass now sharpens one more reason to **adapt, not clone**:

- **subject architecture contract sheet / governance-domain review / authority and re-share review / architecture migration watch / subject architecture lineage receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `what architecture am I actually choosing here, who can re-share or re-authorize later, and can I migrate without tearing the subject down?` depends on combining several pages:

- current `What's the difference between Standard and Advanced folders?` docs still say Standard uses keys while Advanced uses certificates, only Advanced has Owner and on-the-fly permission changes, Standard peer lists do not understand one linked user as one identity, only Owners can share Advanced folders, and Standard cannot be converted in place to Advanced
- current `Key structure and flow` docs still say only Standard folders use keys and still expose architecture-bearing key classes for RW, RO, encrypted-capable, encrypted readback, encrypted-only, and identity linking
- current `Sync Share Dialog (Desktop)` and `User Management` docs still say Standard has no Owner level, Standard peers can re-share onward with the key class they possess, only Owners can share Advanced folders, and linked devices under one identity all act as Owners
- current `How to create a Read Only folder while syncing across linked devices?` and `Is one-way synchronization possible?` docs still say a true RO linked-device outcome requires leaving the linked lane and manually using a Standard-folder RO key
- current `Encrypted folders` docs still say encrypted nodes are a separate backup-like derivative lane: manual encrypted-key attach, `Disconnected` escape hatch for linked devices, no decryption, no Selective Sync, and hardwired read-only / overwrite-heal posture
- current `Running Sync in configuration mode` docs still say config mode can author Standard folders only, not Advanced

So the tighter non-clone line is:

> borrow Resilio's candor that key-based Standard subjects, certificate-based Advanced subjects, linked owner-lane arrivals, and encrypted derivative subjects are materially different governance systems — but refuse any product contract where `what architecture am I choosing here, what power does it confer or give up later, and can I migrate without teardown?` still makes the operator merge comparison charts, key docs, sharing docs, linked-device caveats, encrypted-folder caveats, and config-mode notes.

That yields five more ordinary product-owned pages:

- **Subject architecture contract sheet**
- **Governance-domain review**
- **Authority and re-share review**
- **Architecture migration watch**
- **Subject architecture lineage receipt**

## Latest addendum — transport profile, protocol overlap, cipher overlap, and bind residue after rev0337

Another current official Resilio pass now sharpens one more reason to **adapt, not clone**:

- **transport profile contract sheet / protocol overlap review / bind witness review / transport hardening review / transport profile lineage receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `what tunnel classes can these peers still use, what crypto overlap do they still share, and what happens if the preferred interface disappears?` depends on combining several pages:

- current `What ports and protocols are used by Sync?` docs still describe a staged transport story: config fetch, tracker, direct TCP/UDP over the listening port, relay fallback, and LAN multicast/broadcast discovery
- current `Power user preferences` docs still publish `tunnel_protocols` and `tunnel_ciphers`, each explicitly saying peers need some common overlap to connect
- the same current power-user docs still say `bind_interface` can fall forward to the next active interface unless `use_only_bind_interface` is also enforced, and `lan_encrypt_data` forces LAN encryption
- current `Sync Preferences` docs still say proxies prohibit incoming connections and that if both peers are behind proxies they can talk only via relay
- current `Peers aren't connecting` and `What is a Relay Server?` docs still say tracker reach, listening-port reach, multiple-NIC routing, and relay fallback materially change the actual tunnel that survives

So the tighter non-clone line is:

> borrow Resilio's candor that route lane, common protocol overlap, common cipher overlap, bind fallback, proxy asymmetry, and relay survival are different truths — but refuse any product contract where `what transport lane is actually possible here, and will this interface pin really constrain traffic?` still makes the operator merge ports/protocols guidance, power-user tables, proxy notes, and troubleshooting prose.

That yields five more ordinary product-owned pages:

- **Transport profile contract sheet**
- **Protocol overlap review**
- **Bind witness review**
- **Transport hardening review**
- **Transport profile lineage receipt**


## Latest addendum — overlapping-subject topology, nested-share seed gaps, and selective-sync admission ceilings after rev0338

Another current official Resilio pass now sharpens one more reason to **adapt, not clone**:

- **overlapping-subject contract sheet / nested-share topology review / overlap admission review / overlapping-subject proof / overlapping-subject lineage receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `what happens if I admit a child share inside a parent share, or try to expand a larger root around an existing subject?` depends on combining several pages:

- current `Is it possible to share a nested folder separately?` docs still say nested sharing is allowed only with limitations: both parent and child need `Read & Write` or `Owner`, both are treated as separate sync folders, parent-only peers do **not** seed child-only peers, and both parent and child must have `Selective Sync` disabled
- that same current nested-share doc still says the overlap has side effects: the child subtree is indexed and rescanned twice, and child-share changes can still flow outward to parent-share peers through the parent subtree
- current `Selected folder is already added to Sync` docs still say a device can only have one folder with the same `.sync/ID`, and they distinguish same-path reuse from same-key↔different-path collisions
- current `Cannot add folder. It contains a folder that is already syncing.` docs still say a larger home-folder claim can fail because the home folder already contains Sync's storage-folder license material
- current `Can I connect two pre-populated pre-existing folders?` docs still say reusing an existing populated path is a reconnect/confirmation workflow rather than a clean empty-path admission
- the change log still preserves the separate ceiling that a nested folder cannot be added in Selective Sync mode

So the tighter non-clone line is:

> borrow Resilio's candor that overlapping parent/child subjects, seed gaps, selective-sync exclusion, same-ID boundaries, service-interior conflicts, and reconnect-to-existing are materially different truths — but refuse any product contract where `can I safely admit this overlap, who can seed whom, and what extra cost or shadow propagation am I accepting?` still makes the operator merge a nested-share FAQ, selective-sync docs, collision errors, home-folder warnings, reconnect prose, and changelog notes.

That yields five more ordinary product-owned pages:

- **Overlapping-subject contract sheet**
- **Nested-share topology review**
- **Overlap admission review**
- **Overlapping-subject proof**
- **Overlapping-subject lineage receipt**


## Latest addendum — interface affinity, multi-NIC ambiguity, and service all-NIC audience after rev0339

Another current official Resilio pass now sharpens one more reason to **adapt, not clone**:

- **interface-affinity contract sheet / multi-NIC review / interface-fallback proof / service NIC-audience review / interface-affinity lineage receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `did this really stay on the interface I intended, and did a runtime-class change widen my audience?` depends on combining several pages:

- current `Power user preferences` docs still say `bind_interface` names an interface, but if that interface is unavailable Sync will switch to the **next active interface** unless `use_only_bind_interface` is enabled
- current `Peers aren't connecting` docs still treat multiple NICs as a first-class cause and even suggest switching to another NIC in LAN cases
- current `Performance overview` docs still expose only current peer-table witnesses like upload/download, RTT, and protocol, which are useful but weaker than continuity proof
- the still-published official change log still preserves materially relevant network truth: `Allow to select NIC for data transfer instead of binding to all interfaces`, `Fix Sync showing "No Network" when only bridge interface is available on OS X`, and `Allow Sync to listen all NICs when installed as service`

So the tighter non-clone line is:

> borrow Resilio's candor that requested NIC, effective NIC, fall-forward, bridge-only startup, multi-NIC routing, and service all-NIC audience are different truths — but refuse any product contract where `did this really stay on the interface I meant, and did service/runtime changes widen who could hear me?` still makes the operator merge power-user settings, troubleshooting prose, performance rows, and changelog archaeology.

That yields five more ordinary product-owned pages:

- **Interface-affinity contract sheet**
- **Multi-NIC review**
- **Interface-fallback proof**
- **Service NIC-audience review**
- **Interface-affinity lineage receipt**


## Latest addendum — byte-plan certainty, hash witness, and reuse-vs-redownload ceilings after rev0340

Another current official Resilio pass now sharpens one more reason to **adapt, not clone**:

- **byte-plan contract sheet / hash-and-preseed review / reuse-basis review / partial-transfer survivor proof / byte-plan lineage receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `why does this claim it should not re-download, what witness actually supports that, and what survives if resume fails?` depends on combining several pages:

- current `When a file changes, does Resilio Sync transfer the entire file again, or just the part that's changed?` docs still say only changed pieces are transferred in the ordinary case, while piece shifts can still force whole-file resend and Business has a separate diff-delta feature
- current `Some internal tasks are taking time to complete` docs still say Sync does distinct hidden work: checking file blocks, copying local file blocks for deduplication, hashing files, hashing local files for pre-seeded folders on receiving peers apart from read-only peers, and writing deduplicated file pieces to disk
- those same current troubleshooting docs still say local block copy may avoid re-download but can increase disk usage while it does so
- current `What happens when file is renamed` docs still say rename reuse depends on Archive: the receiver checks Archive for a file with the same hash and, if found, restores it under the new name instead of re-transmitting the bytes
- current `My files don't sync` docs still say partially downloaded `.!sync` residue can remain in `.sync`, and if resume does not continue after restart the operator may need to delete the temp files and restart again

So the tighter non-clone line is:

> borrow Resilio's candor that changed-piece transfer, local dedup reuse, archive-assisted rename reuse, pre-seeded hashing, and stuck partial residue are different truths — but refuse any product contract where `why does this claim it should not re-download, what witness actually supports that, and what survives if resume fails?` still makes the operator merge a transfer FAQ, hidden-task troubleshooting, rename/archive behavior, and partial-download cleanup prose.

That yields five more ordinary product-owned pages:

- **Byte-plan contract sheet**
- **Hash-and-preseed review**
- **Reuse-basis review**
- **Partial-transfer survivor proof**
- **Byte-plan lineage receipt**


## Latest addendum — queue-governance provenance, active-window ceilings, and visible-order mismatch after rev0341

Another current official Resilio pass now sharpens one more reason to **adapt, not clone**:

- **queue-governance contract sheet / priority-origin review / active-window proof / visible-order mismatch page / queue-governance lineage receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `why is this prioritized, what scope does that actually cover, and does the queue I see prove the queue the scheduler is using?` depends on combining several pages:

- current `File download priority` docs still say the feature is available in Sync `3.1.0`, can prioritize by size or modification time, defaults to `None`, and applies only to the active queue up to a limit of **50,000** active files
- that same current priority doc still says a global `folder_defaults.transfer_priority` automatically applies to all still-inheriting shares and to new shares including single-file sharing
- that same current priority doc still says once a share's priority has been manually changed, later global changes stop applying to it **even if the share is later manually set back to `None`**
- current `Power user preferences` docs still enumerate the global default values (`None`, smaller first, larger first, older first, newer first)
- current `Folder Preferences` docs still surface the per-share priority control
- current `File download priority` docs still say lower-priority work can be suspended for a higher-priority file, but internal exceptions remain, non-splittable files do not strictly follow the same cancellation behavior, and the UI queue may still appear alphabetical rather than in actual priority order

So the tighter non-clone line is:

> borrow Resilio's candor that global defaults, per-share overrides, sticky former-manual overrides, active-window scope, exception-bearing suspensions, and visible-order mismatch are materially different truths — but refuse any product contract where `why is this prioritized, what scope does that actually cover, and does the queue I see prove the queue the scheduler is using?` still makes the operator merge a feature article, power-user defaults, and folder-preference surfaces.

That yields five more ordinary product-owned pages:

- **Queue-governance contract sheet**
- **Priority-origin review**
- **Active-window proof**
- **Visible-order mismatch page**
- **Queue-governance lineage receipt**


## Latest addendum — investigation evidence, support-lane truth, and capture survivorship after rev0355

Another current official Resilio pass now sharpens one more reason to **adapt, not clone**:

- **investigation-evidence contract sheet / evidence-capture review / support-lane proof / evidence-retention timeline / investigation-evidence lineage receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `what evidence can I capture now, who can actually receive it, and what stronger diagnostic claim does it justify?` depends on combining several pages:

- current `Collecting debug logs manually` and `Collecting debug logs automatically` docs still say debug logging must be enabled before reproduction, Sync should be restarted so the posture is real, and enough time should be allowed after reproduction for the logs to become useful
- current `Increasing Debug Log size` docs still say logs rotate at a bounded size, so `logging enabled` is weaker than `the needed evidence survived`
- current `Collecting crash reports, mini-dumps and core dumps` docs still separate logs from crash artifacts and change the storage path when Sync runs as a service under another account
- current `Where to collect logs on NAS?` and mobile settings/debug articles still show vendor-specific and platform-specific evidence paths plus cleanup behavior that can erase current logs
- current `Measuring network performance with iperf3` docs still require Sync to be shut down for that benchmark, so comparative transport evidence is different from live runtime evidence
- those same troubleshooting articles still say direct technical support is only for Business customers, while Sync v3 otherwise routes functionality help toward the forum and Help Center

So the tighter non-clone line is:

> borrow Resilio's candor that support lane, live debug capture, rotated-log survival, crash residue, mobile export, NAS storage paths, and stopped-runtime benchmarks are different truths — but refuse any product contract where `what evidence can I capture now, who can actually receive it, and what diagnostic sentence does it justify?` still makes the operator merge half a dozen troubleshooting pages.

That yields five more ordinary product-owned pages:

- **Investigation-evidence contract sheet**
- **Evidence-capture review**
- **Support-lane proof**
- **Evidence-retention timeline**
- **Investigation-evidence lineage receipt**

## Latest addendum — pathname dialect, filesystem projection, and loss-boundary honesty after rev0359

Another current official Resilio pass now sharpens one more reason to **adapt, not clone**:

- **path-projection contract sheet / path-equivalence review / projection-capability proof / filesystem-dialect timeline / path-projection lineage receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `will this pathname survive intact, be rewritten, conflict, or block as it crosses this cohort?` depends on combining several pages:

- current `Conflict files in Sync` docs still say case-insensitive targets can turn case-only distinctions into `.Conflict` outcomes, decomposed UTF symbols can collide despite human-equal appearance, prohibited symbols can be rewritten on Windows, and linked junctions can be part of conflict behavior
- current `My files don't sync` docs still say Sync expects UTF-8 filenames, mixed-system encoding can break syncing, and path / filename length can exceed platform ceilings
- current `Unsupported asterisk (*) characters at the end of file/folder names` docs still say some trailing-asterisk names without extensions are invalid and may be interpreted as system data
- current `Soft links, hard links and symbolic links` docs still say Windows link classes are unsupported, while UNIX can sync a symbolic-link object without automatically syncing its target folder

So the tighter non-clone line is:

> borrow Resilio's candor that case behavior, Unicode normalization, prohibited symbols, length ceilings, and link-object handling are materially different truths — but refuse any product contract where `will this pathname survive intact, and what exactly will arrive?` still makes the operator merge conflict guidance, troubleshooting prose, invalid-name notes, and link-object docs.

That yields five more ordinary product-owned pages:

- **Path-projection contract sheet**
- **Path-equivalence review**
- **Projection-capability proof**
- **Filesystem-dialect timeline**
- **Path-projection lineage receipt**

## Revision addendum — name planes, alias drift, and label-authority boundaries after rev0365

This revision continues directly from `rev0365` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **identity naming, device naming, share-path naming, desktop custom aliases, invite-specific labels, and backup-folder default naming**.
2. Tightens the non-clone line again: borrow Resilio's candor that `identity name`, `device name`, `folder name`, `share alias`, and `link label` are different truths; refuse any contract where the operator still has to reconstruct `what exactly did I rename, where will that label show up, and did I change authority or only presentation?` from several articles.
3. Adds one new **Resilio evaluation** document focused on why current naming-plane truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for name-plane contract sheet, local-vs-remote alias review, name-authority proof, label-drift timeline, and name-plane lineage receipt.
5. Makes one hard product decision explicit: **name plane is a first-class contract object.**
6. Makes another hard product decision explicit: **identity handle, device handle, filesystem subject name, local UI alias, invitation label, and derived default folder name are different public truths.**
7. Makes a third hard product decision explicit: **`renamed in UI` is weaker than `renamed on disk`, and `changed device label` is weaker than `changed identity / certificate lineage`.**
8. Packages the result as another continuation archive whose new tranche makes the `name-plane-contract / alias-review / authority-proof / label-drift-timeline / name-plane-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1336-resilio-name-plane-identity-device-share-and-link-label-fragmentation-evaluation.md`
- `1337-name-plane-contract-sheet-page-identity-device-path-alias-and-invitation-label-interface-spec.md`
- `1338-local-vs-remote-alias-review-page-disk-name-ui-alias-link-label-and-device-label-interface-spec.md`
- `1339-name-authority-proof-page-presentation-vs-certificate-lineage-and-propagation-basis-interface-spec.md`
- `1340-label-drift-timeline-page-local-rename-invite-regeneration-disconnect-persistence-and-identity-reset-interface-spec.md`
- `1341-name-plane-lineage-receipt-page-plane-family-propagation-scope-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's naming-plane contract**

This time the reason is especially clear around **identity names, device labels, share path names, local desktop aliases, invite-inserted labels, and derived backup-folder naming**.
Current official materials simultaneously show that:

- current `Can I change the name of my Sync identity?` docs still say the identity name participates in certificate creation and cannot be changed in place; changing it requires unlinking and generating a new identity
- current `Sync Private Identity & Linking My Devices` docs still say the name plus fingerprint are what other peers use to recognize the connecting installation
- current `Setting custom name for sync shares` docs still say a desktop custom share name changes only local UI, does not rename the folder on disk, and does not propagate to peers or linked devices
- those same current custom-name docs still say a generated link or QR can carry a different inserted name without changing the persistent share alias itself
- current `Can I move or rename a syncing folder?` docs still say a folder renamed in the file browser only changes on that device and other devices do not adopt the new name automatically
- current Android and iOS interface docs still say identity views expose username, fingerprint, and device name together, and Android still exposes a device-name change separately from identity unlink
- current `How to use Camera Backup (all mobiles)?` docs still say default backup-folder naming depends on device class and, on iOS, includes the device name

That candor is useful.
The naming-plane contract is the problem.
AnonSync should not clone a world where the operator still has to translate `identity`, `device`, `folder`, `share`, `link label`, and `backup folder name` into one stable answer about plane family, authority consequence, propagation scope, persistence class, and blocked stronger sentence by stitching together several KB articles.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because names are a real contract with separate truths for identity lineage, device presentation, filesystem subject naming, local aliasing, invitation labeling, and derived default naming, but the present contract still scatters the answer to `what exactly did I rename, where will the new label appear, and did I change authority or only presentation?` across several KB articles instead of owning it as one stable page family.**


## Revision addendum — effect direction, reverse-lane truth, and flow-role honesty after rev0366

This revision continues directly from `rev0366` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **bidirectional sync, read-only replication, storage-only mobile backup, camera-backup disconnect survivor behavior, and encrypted custody / reverse-recovery limits**.
2. Tightens the non-clone line again: borrow Resilio's candor that `Synced`, `Read Only`, `backup`, and `encrypted` are different lanes; refuse any contract where the operator still has to reconstruct `which side can publish, delete back, restore back, or only retain` from several articles.
3. Adds one new **Resilio evaluation** document focused on why current directionality truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for effect-direction contract sheet, flow-direction review, reverse-lane proof, effect-direction timeline, and effect-direction lineage receipt.
5. Makes one hard product decision explicit: **effect direction is a first-class contract object.**
6. Makes another hard product decision explicit: **authoring lane, delete lane, serve lane, onward-reshare lane, reverse-recovery lane, and disconnect survivor class are different public truths.**
7. Makes a third hard product decision explicit: **`full local copy` is weaker than `can publish`, and `can serve` is weaker than `can recover the world from here`.**
8. Packages the result as another continuation archive whose new tranche makes the `effect-direction / flow-review / reverse-lane-proof / direction-timeline / direction-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1342-resilio-effect-direction-bidirectional-backup-and-reverse-lane-fragmentation-evaluation.md`
- `1343-effect-direction-contract-sheet-page-authoring-delete-serve-and-recovery-lanes-interface-spec.md`
- `1344-flow-direction-review-page-bidirectional-storage-only-backup-and-opaque-custody-interface-spec.md`
- `1345-reverse-lane-proof-page-which-side-can-publish-delete-restore-and-reshare-interface-spec.md`
- `1346-effect-direction-timeline-page-enable-backup-disconnect-delete-and-recovery-events-interface-spec.md`
- `1347-effect-direction-lineage-receipt-page-lane-basis-reverse-effects-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's directionality contract**

This time the reason is especially clear around **bidirectional sync, ordinary read-only replication, storage-only backup, camera-backup disconnect survivor behavior, and encrypted custody / recovery ceilings**.
Current official materials simultaneously show that:

- current `Synchronization Modes` and `Folder Types and Management` docs still say full sync is the ordinary bidirectional lane and that Read Only blocks sending changes, additions, or deletions to the swarm
- current `Folder Preferences` docs still say remote RW changes and deletions propagate across peers and that `Overwrite any changed files` can destructively replace local divergence in Read Only folders
- current `How to Back up data (Android only)` docs still say backup preserves desktop copies after phone deletion and preserves phone copies after desktop deletion because the desktop is read-only
- current `How to use Camera Backup (all mobiles)?` docs still say camera backup is for storage purposes only, uses Read Only keys, and leaves already-present pictures on both sides after disconnect
- current `Encrypted folders` docs still say encrypted nodes are Read Only, can re-share only in encrypted form, and cannot restore deleted files back from their own Archive into the live source

That candor is useful.
The directionality contract is the problem.
AnonSync should not clone a world where the operator still has to translate `connected`, `full sync`, `read only`, `backup`, and `encrypted` into one stable answer about authorship, delete direction, serve eligibility, reverse recovery, disconnect survivors, and blocked stronger sentences by stitching together several KB articles.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because directionality is a real contract with separate truths for authorship, delete propagation, storage-only retention, serve eligibility, onward re-share, and reverse recovery, but the present contract still scatters the answer to `which side can actually publish, delete back, restore back, or only hold bytes?` across several KB articles instead of owning it as one stable page family.**


## Revision addendum after rev0367 — governance plane, override authorship, and control-surface honesty

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **governance plane truth**.
It does eight things in one tranche:

1. Continues the archive after rev0367 with a new page family centered on where values actually live and who truly owns them.
2. Tightens the non-clone line again: borrow Resilio's candor that desktop folder prefs, power-user settings, startup config, service storage, CLI switches, and mobile settings are different realities; refuse any contract where the operator still has to reconstruct `who owns this value, what overrode what, and does this subject still inherit the default?` from several articles.
3. Adds one new **Resilio evaluation** document focused on why current governance-plane truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for governance-plane contract sheet, policy-authorship review, mutation-authority proof, governance-plane timeline, and governance-plane lineage receipt.
5. Makes one hard product decision explicit: **governance plane is a first-class contract object.**
6. Makes another hard product decision explicit: **authorship plane, witness surface, scope, precedence, inheritance state, and activation boundary are different public truths.**
7. Makes a third hard product decision explicit: **`same shown value` is weaker than `same governance lineage`, and `saved in a colder plane` is weaker than `already active winner`.**
8. Packages the result as another continuation archive whose new tranche makes the `governance-plane / authorship-review / mutation-authority-proof / governance-timeline / governance-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1348-resilio-governance-plane-ui-poweruser-config-and-service-override-fragmentation-evaluation.md`
- `1349-governance-plane-contract-sheet-page-ui-poweruser-config-service-and-override-basis-interface-spec.md`
- `1350-policy-authorship-review-page-global-default-share-override-and-manual-detach-interface-spec.md`
- `1351-mutation-authority-proof-page-which-surface-can-set-see-and-override-this-value-interface-spec.md`
- `1352-governance-plane-timeline-page-default-adoption-manual-override-restart-and-service-world-events-interface-spec.md`
- `1353-governance-plane-lineage-receipt-page-authorship-plane-override-basis-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's governance contract**

This time the reason is especially clear around **desktop-only folder preferences, power-user defaults, manual per-share detachment from global defaults, config-authored folder takeover, service-storage world changes, and surface-limited mobile settings**.
Current official materials simultaneously show that:

- current `Folder Preferences` docs still say the per-folder preference surface is desktop-only
- current `Power user preferences` docs still expose advanced settings and admit that some are ignored in Linux WebUI
- current `File download priority` docs still say a manual share-level priority can sever later inheritance from the global power-user default, even when the share is later set back to `None`
- current `Running Sync in configuration mode` docs still say config-authored shared folders disable WebUI and override folders previously added from WebUI, while config mode can create only Standard folders
- current `Sync Service Troubleshooting on Windows` docs still say service storage location and service principal changes can create a new effective world with no previous folders present and require re-add / re-share
- current `Settings on mobile platforms` docs still show a narrower mobile control plane than the richer desktop-only folder and advanced preference surfaces

That candor is useful.
The governance contract is the problem.
AnonSync should not clone a world where the operator still has to translate `Preferences`, `Advanced`, `Power user`, `sync.conf`, `Service`, `CLI`, and `Mobile settings` into one stable answer about authorship plane, witness surface, inheritance state, override precedence, activation boundary, and blocked stronger sentences by stitching together several KB articles.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because governance is a real contract with separate truths for authorship plane, witness surface, scope, override precedence, inheritance state, and activation boundary, but the present contract still scatters the answer to `who really owns this value right now, what overrode what, and does this subject still inherit the default?` across several KB articles instead of owning it as one stable page family.**


## Revision addendum after rev0368 — local mutability ceiling, write-barrier truth, and host-lane honesty

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **local mutability ceiling**.
It does eight things in one tranche:

1. Continues the archive after rev0368 with a new page family centered on whether a runtime can actually mutate bytes at a local subject now.
2. Tightens the non-clone line again: borrow Resilio's candor that locks, missing RW grants, provider/API grants, service / NAS principals, SMB lane safety, and filesystem trouble are different realities; refuse any contract where the operator still has to reconstruct `can bytes really be mutated here now, and what exact barrier is stronger if not?` from several articles.
3. Adds one new **Resilio evaluation** document focused on why current local-write truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for local-mutability contract sheet, write-barrier review, write-authority proof, mutability timeline, and local-mutability lineage receipt.
5. Makes one hard product decision explicit: **local mutability ceiling is a first-class contract object.**
6. Makes another hard product decision explicit: **write grant, active principal, host write lane, lock barrier, filesystem health, and retry rung are different public truths.**
7. Makes a third hard product decision explicit: **`path visible` is weaker than `path writable`, `path writable` is weaker than `safe host lane`, and `will retry later` is weaker than `writeable now`.**
8. Packages the result as another continuation archive whose new tranche makes the `local-mutability / barrier-review / write-authority-proof / mutability-timeline / mutability-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1354-resilio-local-mutability-ceiling-lock-permission-and-host-write-lane-fragmentation-evaluation.md`
- `1355-local-mutability-contract-sheet-page-write-grant-lock-barrier-and-host-lane-interface-spec.md`
- `1356-write-barrier-review-page-locks-permissions-api-grants-and-unsafe-host-paths-interface-spec.md`
- `1357-write-authority-proof-page-who-can-actually-mutate-bytes-here-now-interface-spec.md`
- `1358-mutability-ceiling-timeline-page-grant-loss-lock-release-remount-and-principal-switch-events-interface-spec.md`
- `1359-local-mutability-lineage-receipt-page-write-basis-blockers-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's local-writeability contract**

This time the reason is especially clear around **locked files, missing RW grants, Android storage and SD-card provider access, NAS internal-user rights, Windows service principals, SMB mixed-access hazards, and filesystem / mount trouble**.
Current official materials simultaneously show that:

- current `Locked files` docs still say another application can block file access and that Sync cannot identify the locking app for you
- current `Power user preferences` docs still say later lock retry is its own adjustable policy via `recheck_locked_files_interval`
- current `My files don't sync` docs still separate locked files, missing RW access, filesystem errors, and mount trouble as different causes
- current `Sync and SMB file shares` docs still warn that mixed direct-local plus SMB access can roll back or damage files
- current `Permissions Sync requires on Android and Amazon Kindle` docs still say Android storage permission is what lets Sync write received files and apply changes
- current `SD card gimmicks on Android` docs still say SD-card write access depends on the provider API lane and that ordinary picker navigation does not grant it
- current `Synology` docs still say the internal `rslsync` user needs explicit Read/Write rights on the NAS share
- current `Sync Service Troubleshooting on Windows` docs still say switching service principal can widen access while also creating a new storage world that requires re-add / re-share

That candor is useful.
The local-write contract is the problem.
AnonSync should not clone a world where the operator still has to translate `locked`, `no permission`, `service`, `SD card`, `SMB`, and `filesystem trouble` into one stable answer about grant class, actor / principal, host write lane, strongest blocker, retry rung, and continuity consequence by stitching together several KB articles.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because local mutability is a real contract with separate truths for write grant, active principal, host write lane, lock barrier, filesystem health, retry rung, and continuity consequence, but the present contract still scatters the answer to `can this runtime actually mutate bytes here now, and what exact barrier is stronger if not?` across several KB articles instead of owning it as one stable page family.**

## Revision addendum after rev0369 — entitlement provenance, license topology, and feature-afterlife truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **entitlement provenance**.
It does eight things in one tranche:

1. Continues the archive after rev0369 with a new page family centered on why a capability is available here at all.
2. Tightens the non-clone line again: borrow Resilio's candor that site-issued v3 activation, legacy Home Pro / Family Pro, Business owner topology, linked-device inheritance, shared seats, wrong-support posture, and feature-specific entitlement cliffs are different realities; refuse any contract where the operator still has to reconstruct `why is this feature available here, who granted that right, and what happens when that entitlement changes?` from several articles.
3. Adds one new **Resilio evaluation** document focused on why current entitlement truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for entitlement-provenance contract sheet, license-topology review, feature-entitlement proof, entitlement-afterlife timeline, and entitlement lineage receipt.
5. Makes one hard product decision explicit: **entitlement provenance is a first-class contract object.**
6. Makes another hard product decision explicit: **entitlement source, usage-lane legitimacy, grant topology, revocation authority, and feature-afterlife are different public truths.**
7. Makes a third hard product decision explicit: **`activated` is weaker than `legitimate for this usage lane`, and `legitimate for this usage lane` is weaker than `durable independent entitlement`.**
8. Packages the result as another continuation archive whose new tranche makes the `entitlement-source / topology-review / entitlement-proof / afterlife-timeline / entitlement-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1360-resilio-entitlement-provenance-license-topology-and-feature-afterlife-fragmentation-evaluation.md`
- `1361-entitlement-provenance-contract-sheet-page-license-source-usage-lane-and-feature-afterlife-interface-spec.md`
- `1362-license-topology-review-page-owner-seat-family-lane-and-revocation-authority-interface-spec.md`
- `1363-feature-entitlement-proof-page-why-this-capability-is-allowed-here-now-interface-spec.md`
- `1364-entitlement-afterlife-timeline-page-activation-expiry-reclaim-and-lane-shift-events-interface-spec.md`
- `1365-entitlement-lineage-receipt-page-source-topology-afterlife-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's entitlement contract**

This time the reason is especially clear around **v3 non-commercial activation, legacy personal licensing, family-pack scope, owner-centered Business topology, shared-seat revocability, server-support qualifiers, expiry fan-out, and feature-specific entitlement cliffs**.
Current official materials simultaneously show that:

- current `Licensing in Resilio Sync 3.0` docs still say legacy Home Pro / Family Pro continue in v3 while Business cannot move to v3
- current `FAQ Resilio Sync 3.0.0` docs still say v3 is fully available for non-commercial use but still needs activation and that the new site-issued license is personal and non-shareable
- current `Updating installation to Resilio Sync v3` docs still say former Free installs only get a short trial before registration and activation are required
- current `How to apply license key and share license seats` docs still say Business is owner-centered, linked devices inherit automatically, other identities depend on shared seats, and ownership can move if the key is re-applied elsewhere
- current `What happens when Sync Business trial or license expires?` docs still say owner and shared seats lose Pro features on expiry
- current `Sharing a folder locally` docs still say local shares stop working when entitlement is lost
- current `Your Sync Business license doesn't support Windows Server or Linux` docs still say the key may apply while sharing/linking stop without the right server-support qualifier
- current `My device has lost the license...` docs still say seat loss can happen through owner movement, reclaim, or over-sharing

That candor is useful.
The entitlement contract is the problem.
AnonSync should not clone a world where the operator still has to translate `licensed`, `Pro`, `free`, `trial`, `Business`, `Family`, and `available` into one stable answer about source, topology, lane legitimacy, revocation authority, feature-afterlife, and blocked stronger sentences by stitching together several KB articles.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because entitlement is a real contract with separate truths for source, topology, lane legitimacy, revocation authority, and feature-afterlife, but the present contract still scatters the answer to `why is this capability available here, who granted that right, and what happens when that entitlement changes?` across several KB articles instead of owning it as one stable page family.**


## Revision addendum after rev0408 — promise capacity, concurrency, and overcommitment truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **promise capacity**.
It does eight things in one tranche:

1. Continues the archive after rev0408 with a new page family centered on whether another promise honestly fits at all.
2. Tightens the non-clone line again: borrow Resilio's candor that graphs, queue depth, rate limits, scheduler windows, rescans, hidden preprocessing, and power-user throttles all shape real capacity; refuse any contract where the operator still has to reconstruct `do we actually have room for one more promise?` from several unrelated surfaces.
3. Adds one new **Resilio evaluation** document focused on why current capacity truth is still too fragmented to clone even though the ingredients are useful.
4. Adds five new **interface specs** for commitment-capacity contract sheet, promise-load review, commitment-capacity proof, promise-capacity timeline, and commitment-capacity lineage receipt.
5. Makes one hard product decision explicit: **restored promise authority is weaker than available promise capacity.**
6. Makes another hard product decision explicit: **concurrent promise load, reserve headroom, protected capacity, and overcommitment risk are different public truths.**
7. Makes a third hard product decision explicit: **background work, discovery lag, and hidden processing consume real future budget even when visible throughput looks acceptable.**
8. Packages the result as another continuation archive whose new tranche makes the `capacity-sheet / load-review / capacity-proof / capacity-timeline / capacity-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1588-resilio-promise-capacity-concurrency-and-overcommitment-fragmentation-evaluation.md`
- `1589-commitment-capacity-contract-sheet-page-issuer-budget-concurrent-promises-and-reserve-headroom-interface-spec.md`
- `1590-promise-load-review-page-admit-defer-throttle-and-capacity-reservation-routes-interface-spec.md`
- `1591-commitment-capacity-proof-page-load-envelope-headroom-and-overcommitment-guard-interface-spec.md`
- `1592-promise-capacity-timeline-page-budget-consumed-restored-throttled-and-overcommit-events-interface-spec.md`
- `1593-commitment-capacity-lineage-receipt-page-load-basis-headroom-class-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's promise-capacity contract**

This time the reason is especially clear around **short-window performance graphs, queue depth, scheduler pauses, background hashing/merging/scanning work, periodic rescans, and power-user throttles that all shape real delivery headroom**.
Current official materials simultaneously show that:

- current `Performance overview` docs still say Sync exposes 1-minute, 10-minute, and 1-hour graphs, per-peer rates, RTT, and disk queue depth
- current `Sync Preferences` docs still say global sending/receiving rates can be limited and a scheduler can pause or throttle by day-hour windows
- current `Running Sync on schedule` docs still say paused windows still allow zero-sized file sync, deletions, rescanning, indexing, and some onward uploads
- current `How soon does synchronization start?` docs still say rescans run every 600 seconds by default and can trigger whole-file rehashing
- current `Some internal tasks are taking time to complete` docs still say hidden work includes block checks, dedup copies, hashing, tree merges, scans, reads, transfers, and writes
- current `Power user preferences` docs still say disk, indexing, save cadence, refresh cadence, and per-job disk threading can all alter runtime contention and differ by version

That candor is useful.
The promise-capacity contract is the problem.
AnonSync should not clone a world where the operator still has to translate `looks busy`, `looks fast`, `paused`, `limited`, `still scanning`, and `hidden merge work` into one stable answer about admitted promise load, reserve headroom, protected capacity, overcommitment risk, and strongest blocked stronger sentence by stitching together several KB articles.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because promise capacity is a real contract with separate truths for admitted load, reserve headroom, protected capacity, background-work burden, and overcommitment risk, but the present contract still scatters the answer to `do we honestly have room for one more promise, and what stronger promise is blocked if not?` across several KB articles and UI surfaces instead of owning it as one stable page family.**
