## Revision addendum — status shift toward temporary burst borrow and payback after rev0412

The next seam after explicit allocation-envelope conformance is now explicit:

- the archive can already say which claimant won, whether that claimant activated, whether use stayed inside the awarded room, and when use drifted into overdraw, reserve breach, or claimant bleed
- it still needed to own the harder post-conformance truth of whether some extra-room use is a typed temporary exception, who authorized it, when it expires, what harm it causes, and what payback is owed before ordinary entitlement can be claimed again
- current Resilio docs reinforce that gap because priority raises, pause/scheduler asymmetries, rate limits, rescans, hidden work, and short-window performance still do not compile into one first-class burst-borrow verdict

This pass turns that gap into a first-class product object: **the burst-borrow exception case**.

What is newly true in the archive:

- **unauthorized overdraw is weaker than typed temporary exception truth**
- **authorized temporary borrow, expired borrow, unauthorized overdraw, and unpaid payback are separate public truths**
- **urgent exception authority can now exist without silently becoming new baseline entitlement**
- **reserve harm and harmed-claimant consequence can now survive the end of the burst as explicit payback duty instead of being washed away by later lower usage**
- **renewal, denial, throttle-back, reclaim, and reopened contention can now begin from one typed exception verdict instead of operator improvisation**

What remains intentionally true:

- envelope conformance still matters
- protected reserve still matters
- claimant harm still matters
- priority, pause, scheduler, rescans, and hidden work still matter
- but none of those may substitute for one explicit answer about whether extra-room use is lawfully borrowed, still valid, and honestly repaid

## Revision addendum — status shift toward allocation-envelope conformance after rev0411

The next seam after explicit allocation activation is now explicit:

- the archive can already say which claimant won, whether that claimant activated, whether the claimant is productively consuming room, and when reclaim should begin after idle holding
- it still needed to own the harder post-activation truth of whether the active winner is staying inside the room actually awarded or is bleeding into protected reserve or other claimants' space while still looking `busy`
- current Resilio docs reinforce that gap because priority rules, per-share overrides, global rate limits, scheduler windows, rescans, hidden work, and short-window performance still do not compile into one first-class envelope-conformance verdict

This pass turns that gap into a first-class product object: **the allocation-envelope conformance case**.

What is newly true in the archive:

- **activated occupancy is weaker than envelope-conforming occupancy**
- **within-envelope, edge-of-envelope, ordinary overdraw, protected-reserve breach, and cross-claim bleed are separate public truths**
- **temporary emergency borrow can exist without silently becoming ordinary entitlement**
- **losers and neighboring claimants can now carry explicit consequence when a winner exceeds its award instead of hiding behind generic load pressure**
- **correction, downgrade, reclaim, and reopened contention can now begin from one typed conformance verdict instead of post hoc operator interpretation**

What remains intentionally true:

- activation still matters
- productive occupancy still matters
- priority, rate limits, scheduler, rescans, and hidden work still matter
- but none of those may substitute for one explicit answer about whether active use is still honoring the award envelope


## Revision addendum — status shift toward allocation activation after rev0410

The next seam after explicit reservation contention is now explicit:

- the archive can already say which claimant won, who lost, what reserve stayed protected, and what fairness guard applied
- it still needed to own the harder post-verdict truth of whether the winner actually activated the awarded room or only sat on it while others kept waiting
- current Resilio docs reinforce that gap because priority, internal tasks, missing sources, locks, pause controls, and short-window graphs still do not compile into one first-class activation verdict

This pass turns that gap into a first-class product object: **the allocation activation case**.

What is newly true in the archive:

- **award is weaker than activated occupancy**
- **awarded-not-started, activated-consuming, activated-no-net-progress, idle-held, downgraded, and reclaimed are separate public truths**
- **losing-claimant starvation can resume after the winner is chosen if the winner fails the activation window**
- **emergency and reserve-borrow awards receive stricter activation and reclaim treatment**
- **reclaim is a typed event, not a silent timeout**

What remains intentionally true:

- winning arbitration still matters
- protected reserve still matters
- queue motion, internal work, or blocker noise still matter
- but none of those may substitute for one explicit answer about whether the winner is actually using the room


## Revision addendum — status shift toward reservation contention after rev0409

The next seam after explicit promise reservation is now explicit:

- the archive can already say whether future room exists and whether some of that room is softly or firmly spoken for
- it still needed to own the harder truth where several claimants compete for the same room and the operator must know who wins, what reserve may not be touched, who gets split or deferred, and when repeated losses become starvation instead of harmless waiting

This pass turns that gap into a first-class product object: **the reservation contention case**.

What is newly true in the archive:

- the product can now say that contested room exists without pretending that one claimant has already won it
- `winning claimant`, `split allocation`, `preempted claimant`, `deferred claimant`, `denied claimant`, and `protected reserve preserved` can now stay visibly different instead of collapsing into vague `priority handled`
- manual overrides, pauses, and higher-priority queue motion can now influence the verdict without silently becoming doctrine
- losing claimants can now carry explicit starvation protection, release triggers, and blocked stronger sentences instead of fading into operator memory
- later operators can now see the claimant set, the winner basis, the reserve rule applied, the losers preserved, and the exact stronger promise that stayed blocked because contested room went elsewhere

New docs in this tranche:

- `1600-resilio-promise-reservation-contention-preemption-and-fairness-fragmentation-evaluation.md`
- `1601-reservation-contention-contract-sheet-page-contested-room-claimants-and-protected-reserve-interface-spec.md`
- `1602-contention-arbitration-review-page-allocate-split-preempt-defer-and-deny-routes-interface-spec.md`
- `1603-reservation-verdict-proof-page-winning-claim-preemption-basis-and-starvation-guard-interface-spec.md`
- `1604-reservation-contention-timeline-page-claim-collision-escalation-preemption-and-release-events-interface-spec.md`
- `1605-reservation-contention-lineage-receipt-page-allocation-basis-preemption-class-and-blocked-stronger-sentences-interface-spec.md`


## Revision addendum — status shift toward promise reservation after rev0408

The next seam after explicit promise capacity is now explicit:

- the archive can already say who is allowed to promise again and whether honest headroom still exists
- it still needed to own the harder truth where the operator must know whether any of that room is already softly held, who owns the hold, what expires it, what reserve remains truly free, and when a stale hold becomes visible risk instead of hidden folklore

This pass turns that gap into a first-class product object: **the promise reservation**.

What is newly true in the archive:

- the product can now say that capacity exists while still preserving that some or all of that future room is already reserved
- `soft hold`, `hard reservation`, `option without guarantee`, `protected reserve`, `released`, `expired`, and `reclaimed` can now stay visibly different instead of collapsing into vague `we probably still have room`
- future work that is not yet a published promise can now still consume named reservation budget instead of silently stealing from later commitments
- ghost holds and stale tentative reservations can now surface as first-class risk instead of hiding inside operator memory or inbox custom
- later operators can now see who opened the hold, what scope it covered, what had to happen before it could become a real promise, when it expired or renewed, and what stronger promise stayed blocked while the room was spoken for

New docs in this tranche:

- `1594-resilio-promise-reservation-soft-hold-and-expiry-fragmentation-evaluation.md`
- `1595-promise-reservation-contract-sheet-page-soft-hold-owner-expiry-and-reserve-boundary-interface-spec.md`
- `1596-reservation-shaping-review-page-soft-hold-hard-reservation-option-and-release-routes-interface-spec.md`
- `1597-promise-reservation-proof-page-reserved-scope-expiry-window-and-ghost-hold-guard-interface-spec.md`
- `1598-promise-reservation-timeline-page-hold-open-renew-release-expire-and-reclaim-events-interface-spec.md`
- `1599-promise-reservation-lineage-receipt-page-hold-basis-expiry-and-blocked-stronger-sentences-interface-spec.md`

The newest hardening move is important:

- **capacity is weaker than reservation truth**
- **soft hold, hard reservation, protected reserve, and expired hold are different truths**
- **ghost reservations must become visible risk instead of hidden capacity theft**

## Revision addendum — status shift toward re-promise authority after rev0406

The next seam after breach recovery and trust repair is now explicit:

- the archive can already say what failed, what survived, what narrower make-good is allowed, and whether trust is partly or fully repaired
- it still needed to own the harder truth where the operator must know who may publish a new promise, how strong that promise may be, whether scope must narrow, whether co-sign is required, and when authority stays blocked even after some recovery success

This pass turns that gap into a first-class product object: **the re-promise authority**.

What is newly true in the archive:

- the product can now say that trust repair happened while still preserving that promise authority remains capped, probationary, or blocked
- `fully-authorized`, `co-sign-required`, `narrowed-scope-only`, `target-only`, `checkpoint-only`, and `blocked` can now stay visibly different instead of collapsing into generic regained trust
- repeated failures can now consume a first-class credibility budget instead of being flattened by one acceptable recovery
- restored authority can now remain narrower than the old authority, with explicit audience, scope, and promise-class caps
- later operators can now see why authority narrowed, what widened it again, what stronger sentence remains blocked, and who must approve the next broader promise

New docs in this tranche:

- `1582-resilio-repromise-authority-credibility-budget-and-issuance-throttle-fragmentation-evaluation.md`
- `1583-repromise-authority-contract-sheet-page-trust-state-authority-class-and-approval-requirements-interface-spec.md`
- `1584-promise-issuance-review-page-autonomy-co-sign-required-throttled-and-blocked-routes-interface-spec.md`
- `1585-repromise-authority-proof-page-eligibility-window-credibility-budget-and-scope-cap-interface-spec.md`
- `1586-promise-authority-timeline-page-breach-downgrade-probation-restoration-and-suspension-events-interface-spec.md`
- `1587-promise-authority-lineage-receipt-page-authority-basis-scope-cap-and-restoration-gate-interface-spec.md`

The newest hardening move is important:

- **trust repair is weaker than restored promise authority**
- **authority class, promise-class cap, scope cap, and co-sign rule are different truths**
- **one repaired breach may still leave future promise authority on probation**

## Revision addendum — status shift toward breach recovery after rev0405

The next seam after explicit delivery commitment and breach truth is now explicit:

- the archive can already say what was promised, under what invalidators, and when miss or breach actually opened
- it still needed to own the harder truth where the operator must know what obligation survives after the miss, whether the original full scope still governs, what narrower or substitute make-good is allowed, and when a new promise becomes truthful again

This pass turns that gap into a first-class product object: **the recovery commitment**.

What is newly true in the archive:

- the product can now say that a commitment breached while still preserving a surviving obligation instead of collapsing everything into generic recovery language
- `full make-good`, `partial make-good`, `substitute make-good`, `diagnostic checkpoint only`, and `trust-repair only` can now stay visibly different instead of collapsing into generic follow-up work
- reduced or abandoned scope can now stay explicit inside the recovery object instead of being silently normalized by time or effort
- `motion restored`, `scope restored`, `trust repaired`, and `re-promise eligible` can now stay visibly different instead of letting resumed activity impersonate renewed commitment authority
- later operators can now see what failed, what still owed scope survived, what remedy class was published, whether parity was restored, when trust requalification began, and whether a fresh promise was ever legitimately reopened

New docs in this tranche:

- `1576-resilio-breach-recovery-make-good-and-trust-repair-fragmentation-evaluation.md`
- `1577-recovery-commitment-contract-sheet-page-breach-class-make-good-scope-and-repromise-gate-interface-spec.md`
- `1578-recovery-shaping-review-page-remedy-class-restored-scope-and-trust-requalification-routes-interface-spec.md`
- `1579-breach-recovery-proof-page-recovery-window-surviving-obligation-and-repromise-boundary-interface-spec.md`
- `1580-breach-recovery-timeline-page-breach-open-remedy-published-scope-restored-and-trust-repaired-events-interface-spec.md`
- `1581-breach-recovery-lineage-receipt-page-breach-class-remedy-scope-and-repromise-readiness-interface-spec.md`

The newest hardening move is important:

- **breach is weaker than recovery duty resolution**
- **surviving obligation, make-good class, and trust-repair status are different truths**
- **resumed motion is still weaker than re-promise eligible**

## Revision addendum — status shift toward delivery commitment after rev0404

The next seam after finishability and ETA confidence is now explicit:

- the archive can already say what remains, whether the route is honestly finishable, and how wide the ETA window should be
- it still needed to own the harder truth where the operator must know whether anyone has actually promised delivery, under what conditions that promise survives, when renegotiation is mandatory, and when the line has crossed from slip into breach

This pass turns that gap into a first-class product object: **the delivery commitment**.

What is newly true in the archive:

- the product can now say that work is forecastable while still not yet promised
- `aspiration`, `target`, `conditional commitment`, `hard commitment`, `withdrawn commitment`, and `breach open` can now stay visibly different instead of collapsing into generic deadline talk
- invalidators, renegotiation triggers, miss boundaries, and breach boundaries can now be carried with the promise instead of being reconstructed later from context
- the strongest surviving sentence can now degrade explicitly when confidence burns down, instead of leaving downstream readers to infer whether the original promise still governs
- later operators can now see what was promised, who relied on it, what conditions could void it, when the window widened, when renegotiation opened, and what weaker sentence survived miss or breach

New docs in this tranche:

- `1570-resilio-deadline-commitment-renegotiation-and-breach-fragmentation-evaluation.md`
- `1571-delivery-commitment-contract-sheet-page-forecast-basis-promise-conditions-and-breach-boundary-interface-spec.md`
- `1572-commitment-quality-review-page-promise-readiness-voiding-conditions-and-renegotiation-routes-interface-spec.md`
- `1573-delivery-commitment-proof-page-promise-window-risk-budget-and-surviving-sentence-interface-spec.md`
- `1574-delivery-commitment-timeline-page-promise-made-tightened-renegotiated-and-breached-events-interface-spec.md`
- `1575-delivery-commitment-lineage-receipt-page-promise-basis-voiding-conditions-and-breach-class-interface-spec.md`

The newest hardening move is important:

- **finish forecast is weaker than commitment**
- **aspiration, target, conditional commitment, and hard commitment are different truths**
- **miss, renegotiation, withdrawal, and breach must stay explicit instead of being flattened into generic slip language**

## Revision addendum — status shift toward finishability and ETA confidence after rev0403

The next seam after motion-versus-progress is now explicit:

- the archive can already say whether live work is buying real net progress
- it still needed to own the harder truth where the operator must know what remains, whether the current route is honestly finishable, how wide the ETA window must stay, and when no honest forecast exists yet

This pass turns that gap into a first-class product object: **the completion forecast**.

What is newly true in the archive:

- the product can now say that work is advancing while still not yet supporting a narrow ETA
- `finishable now if motion holds`, `finishable with known delays`, `finishable after prerequisite`, `finishable only after reroute`, `finishability uncertain`, and `no honest forecast` can now stay visibly different instead of collapsing into generic optimism
- remaining work can now be preserved separately from observed speed, so throughput stops pretending to be finishability
- schedule pauses, rescans, hidden preprocessing, source absence, and restart-from-start risk can now widen forecast confidence explicitly instead of hiding behind transfer graphs
- later operators can now see what remained, why the estimate widened or tightened, when a forecast slipped or was withdrawn, and what weaker sentence survived a no-forecast posture

New docs in this tranche:

- `1564-resilio-finish-forecast-remaining-work-and-eta-confidence-fragmentation-evaluation.md`
- `1565-completion-forecast-contract-sheet-page-remaining-obligation-finishability-and-confidence-interface-spec.md`
- `1566-forecast-quality-review-page-finishability-eta-window-and-deadline-risk-routes-interface-spec.md`
- `1567-finish-forecast-proof-page-eta-window-finishability-grade-and-claim-ceiling-interface-spec.md`
- `1568-completion-forecast-timeline-page-estimate-tightening-slip-and-no-forecast-events-interface-spec.md`
- `1569-completion-forecast-lineage-receipt-page-forecast-basis-finishability-grade-and-blocked-stronger-sentences-interface-spec.md`

The newest hardening move is important:

- **net progress is weaker than finish forecast**
- **finishability, ETA window, deadline confidence, and no-honest-forecast are different truths**
- **hidden preprocessing, pause windows, discovery lag, and interruption/rework risk must count against forecast confidence**

## Revision addendum — status shift toward net progress after rev0402

The next seam after work heartbeat is now explicit:

- the archive can already say who owns a live work item and whether that item still has a heartbeat
- it still needed to own the harder truth where the operator must know whether visible motion is actually reducing the obligation or merely spending time on retries, rescans, hashing, merges, blocked transfers, or conflict-producing churn

This pass turns that gap into a first-class product object: **work progress quality**.

What is newly true in the archive:

- the product can now say that work is alive while still not yet making confirmed net progress
- `motion seen`, `net progress proved`, `churn present but advancing`, `churn dominant`, `new debt created`, and `no-net-gain` can now stay visibly different instead of collapsing into generic progress language
- last observed motion can now be preserved separately from last confirmed net advance, so busy time stops pretending to be obligation reduction
- tolerated churn can now be typed and budgeted rather than treated as folklore
- reroute and rescue can now activate because motion stopped buying progress, not only because all motion stopped
- later operators can now see when the obligation last truly shrank, what churn budget was consumed, when a no-net-gain watch opened, who owned reroute, and what weaker sentence survived an active-but-unproductive route

New docs in this tranche:

- `1558-resilio-motion-progress-churn-and-net-advance-fragmentation-evaluation.md`
- `1559-work-progress-contract-sheet-page-obligation-reduction-churn-signals-and-net-advance-interface-spec.md`
- `1560-progress-quality-review-page-meaningful-advance-retry-churn-and-no-net-gain-routes-interface-spec.md`
- `1561-net-progress-proof-page-obligation-reduction-churn-budget-and-claim-ceiling-interface-spec.md`
- `1562-work-progress-timeline-page-advance-retry-loop-churn-burst-and-net-gain-events-interface-spec.md`
- `1563-work-progress-lineage-receipt-page-progress-basis-churn-status-and-blocked-stronger-sentences-interface-spec.md`

The newest hardening move is important:

- **motion is weaker than meaningful advance**
- **hashing, rescanning, merging, retrying, and queue motion can be real without yet being net progress**
- **alive work may still cross a no-net-gain boundary that forces reroute or rescue**

## Revision addendum — status shift toward work heartbeat after rev0401

The next seam after work claim custody is now explicit:

- the archive can already say who accepted custody of dispatched work and when that claim expires
- it still needed to own the harder truth where the operator must know whether that custody is actually alive, merely waiting safely, blocker-bound, silently stalled, or already in rescue territory

This pass turns that gap into a first-class product object: **the work heartbeat**.

What is newly true in the archive:

- the product can now say that work is accepted while still not yet showing live progress
- `healthy motion`, `healthy wait`, `blocked wait`, `heartbeat overdue`, `silent stall`, and `rescue active` can now stay visibly different instead of collapsing into generic in-progress language
- last observed motion can now be preserved separately from the next required heartbeat, so quiet windows stop pretending to be proof of progress
- nudge, rescue, and reclaim can now be typed consequences of liveness failure instead of ad hoc follow-up habits
- later operators can now see when motion was last observed, what quiet window was allowed, when the stall boundary was crossed, who owns rescue, and what weaker sentence survived a stale claim

New docs in this tranche:

- `1552-resilio-work-heartbeat-stall-and-rescue-fragmentation-evaluation.md`
- `1553-work-heartbeat-contract-sheet-page-claimed-work-expected-motion-and-stall-boundary-interface-spec.md`
- `1554-progress-review-page-heartbeat-evidence-healthy-wait-blocker-and-stall-routes-interface-spec.md`
- `1555-execution-heartbeat-proof-page-motion-basis-silence-window-and-rescue-route-interface-spec.md`
- `1556-work-heartbeat-timeline-page-claim-start-progress-nudge-stall-and-rescue-events-interface-spec.md`
- `1557-work-heartbeat-lineage-receipt-page-heartbeat-status-stall-boundary-and-rescue-owner-interface-spec.md`

The newest hardening move is important:

- **accepted custody is weaker than verified progress**
- **healthy wait, blocker-bound wait, silence window, and silent stall are different truths**
- **quiet time may be allowed, but quiet time is never allowed to impersonate live progress**

## Revision addendum — status shift toward work claim custody after rev0400

The next seam after cross-case decision portfolios is now explicit:

- the archive can already say what work item should go now
- it still needed to own the harder truth where the operator must know whether that work is actually claimed, by whom, for how long, and under what reclaim rule if custody fails

This pass turns that gap into a first-class product object: **the work claim**.

What is newly true in the archive:

- the product can now say that an item won dispatch while still not yet being owned
- `selected`, `notified`, `acknowledged`, `accepted`, `started`, `re-delegated`, `expired`, and `reclaimed` can now stay visibly different instead of collapsing into generic assignment language
- commitment windows can now say whether acknowledgement alone is enough or whether actual start is required
- silence can now age into visible expiry and reclaim instead of being mistaken for quiet progress
- later operators can now see who took custody, when that claim expires, what residual duty survived handoff, and what risk re-entered the portfolio when custody failed

New docs in this tranche:

- `1546-resilio-dispatch-claim-custody-and-abandonment-fragmentation-evaluation.md`
- `1547-work-claim-contract-sheet-page-dispatched-item-assignee-commitment-window-and-reclaim-rules-interface-spec.md`
- `1548-claim-acceptance-review-page-inform-request-accept-redelegate-and-decline-routes-interface-spec.md`
- `1549-execution-custody-proof-page-assignee-claim-expiry-and-safe-unclaim-interface-spec.md`
- `1550-work-claim-timeline-page-dispatch-claim-redelegate-expiry-and-reclaim-events-interface-spec.md`
- `1551-work-claim-lineage-receipt-page-custody-basis-commitment-window-and-abandonment-guard-interface-spec.md`

The newest hardening move is important:

- **winning dispatch is weaker than accepted custody**
- **notification and generic authority do not prove ownership of the work**
- **silence is never success; expired work must fall back into visible risk**

## Revision addendum — status shift toward decision portfolios after rev0399

The next seam after individual evidence-to-decision thresholds is now explicit:

- the archive can already say what one synthesized body of evidence is enough to do
- it still needed to own the harder cross-case truth where several decisions are all real enough to matter at once and the operator must choose what gets attention now

This pass turns that gap into a first-class product object: **the decision portfolio**.

What is newly true in the archive:

- the product can now say that a candidate is action-ready while still not being the one that should go first
- `now`, `next`, `later`, `watch`, `hold`, and `frozen` can now stay visibly different instead of collapsing into generic queue noise
- watch-only and deferred items can now age toward starvation instead of disappearing from truth once something else wins dispatch
- explicit attention budget can now limit what gets worked without pretending the non-selected items stopped mattering
- later operators can now see why one candidate was dispatched, which competing work stayed held, what preemption occurred, and what starvation guard still protected the losing items

New docs in this tranche:

- `1540-resilio-decision-portfolio-prioritization-dispatch-and-starvation-fragmentation-evaluation.md`
- `1541-decision-portfolio-contract-sheet-page-candidate-set-urgency-lanes-and-attention-budget-interface-spec.md`
- `1542-prioritization-review-page-now-next-later-watch-and-preemption-routes-interface-spec.md`
- `1543-dispatch-proof-page-selected-work-held-work-and-starvation-guard-interface-spec.md`
- `1544-decision-portfolio-timeline-page-promotion-deferral-preemption-and-stale-watch-events-interface-spec.md`
- `1545-decision-portfolio-lineage-receipt-page-priority-basis-attention-budget-and-blocked-work-interface-spec.md`

The newest hardening move is important:

- **action-ready is not self-prioritizing**
- **urgency, blast radius, reversibility, evidence freshness, and watch-starvation risk are not interchangeable**
- **held work must stay visible as deliberate debt, not vanish behind the item that won dispatch**

## Revision addendum — status shift toward evidence-to-decision thresholds after rev0398

The next seam after packet synthesis and integrated-claim truth is now explicit:

- the archive can already say what a merged body of evidence supports
- it still needed to own the harder truth where the operator must decide **what that support is actually enough to do**

This pass turns that gap into a first-class product object: **the decision charter**.

What is newly true in the archive:

- operators can now distinguish a sentence that is strong enough to publish from a sentence that is strong enough only to monitor on
- evidence can now clear one action threshold while still failing a stronger one
- `wait`, `monitor`, `ask one more thing`, `apply bounded action`, and `escalate` can now stay visibly different instead of collapsing into generic momentum
- explicit `no decision yet` can now be honest product state rather than private analyst hesitation
- later operators can now see what threshold was cleared, what uncertainty budget remained, what stronger action stayed blocked, and what next fact or event would reopen the choice

New docs in this tranche:

- `1534-resilio-evidence-to-decision-threshold-action-and-escalation-fragmentation-evaluation.md`
- `1535-decision-charter-contract-sheet-page-target-action-threshold-and-residual-uncertainty-interface-spec.md`
- `1536-action-threshold-review-page-claim-ceiling-act-monitor-ask-and-escalate-routes-interface-spec.md`
- `1537-decision-proof-page-allowed-action-blocked-stronger-action-and-uncertainty-budget-interface-spec.md`
- `1538-decision-timeline-page-threshold-crossing-deferral-escalation-and-reopen-events-interface-spec.md`
- `1539-decision-lineage-receipt-page-action-basis-threshold-posture-and-blocked-stronger-sentences-interface-spec.md`

The newest hardening move is important:

- **a merged claim is not self-executing**
- **claim ceiling, action threshold, and uncertainty budget are not interchangeable**
- **the same evidence can justify `monitor` while still failing `mutate`, or justify `escalate` while still failing `conclude`**

## Revision addendum — status shift toward evidence synthesis and integrated-claim truth after rev0397

The next seam after packet intake and supplement-loop truth is now explicit:

- the archive can already say whether one packet is received, opened, validated, fit for the named question, and strong enough for a bounded claim
- it still needed to own the harder truth where **several packets now exist at once** and the operator must decide whether they actually strengthen, merely repeat, or actively undermine one another

This pass turns that gap into a first-class product object: **evidence synthesis truth**.

What is newly true in the archive:

- operators can now compile several packets and witness surfaces into one explicit synthesis set rather than a vague `we looked at logs and graphs` story
- duplicate support and independent corroboration can now stay visibly separate instead of being counted together
- contradictions can now stay alive as first-class blockers even when many weaker packets appear to align
- the strongest safe integrated sentence can now remain explicitly smaller than the most optimistic reading of any one packet
- later operators can now see which packets were relied on, which were superseded, which were discounted, which conflicts remained unresolved, and exactly why the merged claim ceiling stopped where it did

New docs in this tranche:

- `1528-resilio-evidence-synthesis-corroboration-contradiction-and-integrated-claim-fragmentation-evaluation.md`
- `1529-evidence-synthesis-contract-sheet-page-target-question-packet-set-and-weighted-basis-interface-spec.md`
- `1530-corroboration-and-conflict-review-page-independent-support-duplicates-and-unresolved-mismatch-interface-spec.md`
- `1531-integrated-claim-proof-page-merged-basis-open-conflicts-and-ceiling-interface-spec.md`
- `1532-evidence-synthesis-timeline-page-arrival-supersession-corroboration-conflict-and-claim-shift-events-interface-spec.md`
- `1533-evidence-synthesis-lineage-receipt-page-packet-set-weighted-basis-and-blocked-stronger-sentences-interface-spec.md`

The newest hardening move is important:

- **multiple packets do not average into truth**
- **duplicate support, independent corroboration, and contradiction are not interchangeable**
- **one unresolved conflict can keep the stronger sentence blocked even when the packet count looks impressive**

## Revision addendum — status shift toward evidence intake, sufficiency, and supplement-loop truth after rev0396

The next seam after packet custody and export truth is now explicit:

- the archive can already say what packet form was exported, what got redacted, who held custody, and whether the packet was sent, received, opened, validated, and usable
- it still needed to own the harder truth where a recipient must decide *whether that packet is actually sufficient for the live question*, what exact gap still blocks the stronger sentence, and what smallest supplement request is really justified

This pass turns that gap into a first-class product object: **evidence intake truth**.

What is newly true in the archive:

- received packets can now be judged against explicit **target questions** rather than vague `looks helpful` intuition
- the product can now separate `received`, `opened`, `validated`, `fit`, `bounded decision-grade`, and `decision-grade with reservations`
- window fitness, scope fit, version fit, and world fit can now weaken a packet even when the files technically open
- supplement requests can now name the exact gap they target and the stronger sentence they would unlock
- every intake can now preserve a durable fallback sentence for the case where no supplement ever arrives or freshness later expires

New docs in this tranche:

- `1522-resilio-evidence-intake-sufficiency-and-supplement-loop-fragmentation-evaluation.md`
- `1523-evidence-intake-contract-sheet-page-target-claim-packet-fit-and-open-gaps-interface-spec.md`
- `1524-intake-sufficiency-review-page-open-validate-fit-grade-and-cheapest-supplement-interface-spec.md`
- `1525-supplement-request-proof-page-gap-target-cheapest-ask-and-new-ceiling-interface-spec.md`
- `1526-evidence-intake-timeline-page-arrival-validation-supplement-and-expiry-events-interface-spec.md`
- `1527-evidence-intake-lineage-receipt-page-sufficiency-grade-gap-status-and-fallback-claim-interface-spec.md`

The newest hardening move is important:

- **received, opened, validated, fit, and decision-grade are not the same state**
- **a packet is sufficient only for a named target question, never generically**
- **`send more logs` is invalid unless it is the named cheapest useful supplement**

## Revision addendum — status shift toward evidence packet, custody, and export truth after rev0395

The next seam after burden-aware fact acquisition is now explicit:

- the archive can already say which missing fact matters, which evidence channel is cheapest, what burden rung applies, and what stronger sentence stays blocked if heavier capture is declined
- it still needed to own the harder truth where evidence has been captured and must now be *shaped, redacted, exported, validated, and handed to an audience* without lying about what was lost in the process

This pass turns that gap into a first-class product object: **evidence packet truth**.

What is newly true in the archive:

- captured facts and artifacts can now compile into explicit packet objects rather than vague `sent logs` folklore
- operators can now separate `raw capture`, `derived digest`, `redacted packet`, `narrative summary`, and `audience-facing minimum share`
- export state can now stay visibly split across `sent`, `received`, `opened`, `validated`, and `usable`
- redaction and transformation now publish their diagnostic cost instead of hiding behind `privacy-safe` wording
- later operators can now see which storage world or runtime lane produced the packet, how it was transformed, who held custody, and what stronger evidentiary sentence the packet still cannot support

New docs in this tranche:

- `1516-resilio-evidence-packet-custody-redaction-and-export-fragmentation-evaluation.md`
- `1517-evidence-packet-contract-sheet-page-source-artifacts-redaction-class-and-audience-envelope-interface-spec.md`
- `1518-packet-shaping-review-page-raw-derived-redacted-and-minimum-sufficient-share-interface-spec.md`
- `1519-evidence-export-proof-page-sent-received-opened-validated-and-usable-interface-spec.md`
- `1520-evidence-packet-timeline-page-capture-redaction-export-recall-and-supersession-events-interface-spec.md`
- `1521-evidence-packet-lineage-receipt-page-custody-redaction-integrity-and-audience-boundary-interface-spec.md`

The newest hardening move is important:

- **raw capture, redacted packet, and narrative summary are not interchangeable**
- **minimum-sufficient sharing is allowed, but every redaction must publish what it weakens**
- **a packet exported successfully is still weaker than one the audience actually validated and could use**

## Revision addendum — status shift toward discriminator acquisition, evidence burden, and question-order truth after rev0394

The next seam after doctrine applicability is now explicit:

- the archive can already say which doctrines are plausible, which routes look similar, and what one more fact would distinguish them fastest
- it still needed to own the harder truth where the operator must decide *which evidence move is worth making now*, how heavy it is, what fallback exists, and what stronger sentence remains blocked if the best capture never happens

This pass turns that gap into a first-class product object: **discriminator acquisition**.

What is newly true in the archive:

- missing facts can now be ranked by **decision value** instead of treated as interchangeable curiosities
- cheap observational checks, multi-peer checks, restart-bound logs, and heavy artifacts can now be compared in one workspace
- the product can now publish an explicit **burden ladder** and intrusion budget before approving heavier capture
- unavailable channels and declined heavy capture can now weaken the safe sentence explicitly instead of vanishing into free text
- each returned ask can now produce a durable proof showing what ambiguity it actually collapsed, what route changed, and what stronger sentence is still blocked

New docs in this tranche:

- `1510-resilio-discriminator-evidence-acquisition-burden-and-question-order-fragmentation-evaluation.md`
- `1511-discriminator-acquisition-contract-sheet-page-open-gaps-question-value-and-burden-interface-spec.md`
- `1512-discriminator-collection-review-page-cheapest-highest-signal-next-fact-and-intrusion-budget-interface-spec.md`
- `1513-fact-capture-proof-page-question-answered-evidence-quality-and-route-update-interface-spec.md`
- `1514-discriminator-acquisition-timeline-page-ask-skip-fail-escalate-and-burden-shift-events-interface-spec.md`
- `1515-discriminator-acquisition-lineage-receipt-page-discriminator-evidence-quality-burden-and-blocked-stronger-sentences-interface-spec.md`

The newest hardening move is important:

- **the next best distinguishing question is not enough; the product must own how to get the answer**
- **decision value, burden rung, and intrusion cost remain separate truths**
- **declined or unavailable capture channels must weaken the claim explicitly rather than disappearing**

## Revision addendum — status shift toward doctrine applicability and fact-pattern routing truth after rev0393

The next seam after appeal and precedent is now explicit:

- the archive can already say what doctrine exists, how strong it is, when it was narrowed, and how it may be overruled
- it still needed to own the harder truth where a *new* case arrives and the operator must decide whether a precedent really applies, whether the case is only symptom-similar, which missing fact still matters most, and what question would collapse the ambiguity fastest

This pass turns that gap into a first-class product object: **doctrine applicability routing**.

What is newly true in the archive:

- new cases can now compile into explicit candidate precedents rather than fuzzy `looks like before` memory
- operators can now separate `symptom match`, `fact-pattern match`, `world match`, and `governing-doctrine match`
- lookalike warnings can now be reviewed together with explicit disqualifiers instead of one article at a time
- the product can now publish the **next best distinguishing question** when evidence is not yet sufficient to route safely
- route reversals are now durable events instead of embarrassing folklore after more facts arrive

New docs in this tranche:

- `1504-resilio-doctrine-applicability-fact-pattern-routing-and-distinguishing-question-fragmentation-evaluation.md`
- `1505-doctrine-applicability-contract-sheet-page-case-facts-candidate-precedents-and-missing-discriminators-interface-spec.md`
- `1506-fact-pattern-routing-review-page-symptom-lookalikes-disqualifiers-and-next-best-question-interface-spec.md`
- `1507-applicability-proof-page-governing-doctrine-distinction-gaps-and-safe-next-claim-interface-spec.md`
- `1508-applicability-timeline-page-facts-learned-candidates-promoted-and-route-reversal-events-interface-spec.md`
- `1509-applicability-lineage-receipt-page-fact-pattern-governing-doctrine-open-gaps-and-blocked-stronger-sentences-interface-spec.md`

The newest hardening move is important:

- **published doctrine is not self-applying**
- **the next best distinguishing question is part of the product**
- **similar symptom families do not get to collapse into one route without fact-pattern proof**

## Revision addendum — status shift toward appeal, precedent, and doctrine consistency truth after rev0392

The next seam after challenged completion is now explicit:

- the archive can already say how a completion claim is challenged, what counterevidence was attached, and what verdict or rework came out
- it still needed to own the harder truth where operators ask whether this verdict should guide the *next* similar case, whether an older ruling still binds, and when a newer fix or world mismatch makes the older ruling only persuasive or even superseded

This pass turns that gap into a first-class product object: **the precedent docket**.

What is newly true in the archive:

- dispute verdicts can now be promoted, or refused promotion, into explicit doctrine with published binding weight
- operators can now distinguish `binding`, `presumptive`, `persuasive`, `informative-only`, and `superseded` precedent instead of treating all past cases as equal folklore
- version drift, world mismatch, and later fixes can now narrow or sunset an old ruling without pretending it never mattered
- appeals can now explicitly ask to uphold, distinguish, narrow, overrule, or create new doctrine instead of reopening the same argument in free text
- downstream handoff now preserves doctrine weight, scope window, overrule path, and the next forbidden overclaim

New docs in this tranche:

- `1498-resilio-appeal-precedent-and-doctrine-fragmentation-evaluation.md`
- `1499-precedent-docket-contract-sheet-page-source-ruling-analogy-and-binding-weight-interface-spec.md`
- `1500-appeal-and-distinguish-review-page-binding-persuasive-overruled-and-version-scoped-doctrine-interface-spec.md`
- `1501-precedent-proof-page-doctrine-adopted-exception-allowed-and-overrule-path-interface-spec.md`
- `1502-precedent-timeline-page-ruling-appeal-overrule-sunset-and-version-drift-events-interface-spec.md`
- `1503-precedent-lineage-receipt-page-binding-weight-scope-version-window-and-overrule-boundary-interface-spec.md`

The newest hardening move is important:

- **a verdict is not yet doctrine merely because it happened once**
- **binding weight must be published explicitly**
- **version drift and overrule paths stay first-class instead of being buried in changelog archaeology**

## Revision addendum — status shift toward contested completion, counterevidence, and rework verdict truth after rev0391

The next seam after returned work and acceptance is now explicit:

- the archive can already say when a delegate claimed completion and when a reviewer accepted, partially accepted, or left residual duty visible
- it still needed to own the harder truth where that accepted or pending return is later challenged by a requester, downstream witness, or contradictory state and therefore needs one adjudication object instead of a fresh folklore thread

This pass turns that gap into a first-class product object: **the completion dispute**.

What is newly true in the archive:

- a challenged completion claim can now freeze or narrow the stronger sentence without erasing the original claim
- counterevidence can now be attached as typed witness families instead of free-text dissatisfaction
- contradictory witness planes can now be prioritized explicitly rather than left to dashboard vibes
- verdicts can now uphold, weaken, narrow, split, overturn, or spawn rework without hiding what acceptance residue still survives
- dispute handoff now preserves burden-of-proof state, surviving acceptance residue, appeal boundary, and the next forbidden overclaim

New docs in this tranche:

- `1492-resilio-completion-dispute-counterevidence-and-rework-fragmentation-evaluation.md`
- `1493-completion-dispute-contract-sheet-page-claim-counterclaim-witness-and-burden-interface-spec.md`
- `1494-counterevidence-adjudication-review-page-green-state-history-gap-and-scope-mismatch-interface-spec.md`
- `1495-dispute-verdict-proof-page-uphold-overturn-partial-overturn-and-rework-interface-spec.md`
- `1496-completion-dispute-timeline-page-challenge-escalation-verdict-and-reopen-events-interface-spec.md`
- `1497-completion-dispute-lineage-receipt-page-verdict-burden-surviving-duty-and-appeal-boundary-interface-spec.md`

The newest hardening move is important:

- **accepted completion is weaker than adjudicated uncontested completion**
- **counterevidence must stay typed and prioritized**
- **rework and narrowed residue must remain explicit after verdict**

## Revision addendum — fulfillment attestation, returned evidence, and completion acceptance truth after rev0390

This tranche locks the next seam around **fulfillment attestation truth**.
The key decisions now made explicit in the archive are:

- **issued work, attempted work, effect observed, accepted completion, and closed obligation are different truths**
- **self-claimed completion is weaker than reviewer-accepted completion, and reviewer-accepted completion is weaker than no-residual-duty closure**
- **green status, history entries, notification clears, and peer-state changes are witnesses, not automatic acceptance**
- **partial completion, disputed evidence, side-effected completion, and bounded acceptance are first-class outcomes rather than awkward exceptions**
- **every serious delegated-work sentence now needs one receipt that preserves source mandate, claimed completion class, reviewer verdict, acceptance rung, residual duty, reopen posture, and the blocked stronger sentence**

New docs added in this tranche:

- `1486-resilio-mandate-fulfillment-attestation-evidence-and-acceptance-fragmentation-evaluation.md`
- `1487-fulfillment-attestation-contract-sheet-page-mandate-step-evidence-and-completion-class-interface-spec.md`
- `1488-execution-return-review-page-attempted-partial-complete-disputed-and-needs-acceptance-interface-spec.md`
- `1489-completion-acceptance-proof-page-finished-accepted-reopened-and-surviving-obligations-interface-spec.md`
- `1490-fulfillment-timeline-page-claim-review-acceptance-rejection-and-rework-events-interface-spec.md`
- `1491-fulfillment-lineage-receipt-page-completion-class-acceptance-state-and-residual-duty-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `done` can no longer hide whether the work was merely attempted, partially evidenced, accepted only for bounded scope, or actually closed with no meaningful residual duty
- returned evidence now stays visibly weaker than requester acceptance, so a status badge or green peer state cannot impersonate fulfillment truth
- partial or disputed returns now stay first-class instead of collapsing into chat-thread folklore
- later operators can open one receipt and see what was asked, what came back, what was accepted, what still remains, and which stronger completion sentence the product refused to make

## Revision addendum — reliance-to-action authority, delegated mandate, and cancellation truth after rev0389

This tranche locks the next seam around **action-authority truth**.
The key decisions now made explicit in the archive are:

- **reliance and action authority are separate first-class objects**
- **`inform`, `watch`, `approve`, `execute`, `escalate`, and `re-delegate` remain separate routes**
- **a role label like `owner` or `operator` is weaker than an explicit authority class and action set**
- **every serious mandate now needs explicit scope, exclusions, preconditions, expiry, and cancellation behavior**
- **every serious issued instruction now gets one receipt that preserves who was empowered, what they were allowed or required to do, what they were forbidden to do, when the authority died, and what weaker sentence survived after recall**

New docs added in this tranche:

- `1480-resilio-reliance-to-action-authority-delegation-and-recall-fragmentation-evaluation.md`
- `1481-action-mandate-contract-sheet-page-authority-scope-duties-and-expiry-interface-spec.md`
- `1482-mandate-shaping-review-page-inform-observe-decide-execute-and-escalate-routing-interface-spec.md`
- `1483-action-authority-proof-page-issued-mandate-acceptance-execution-and-revocation-interface-spec.md`
- `1484-mandate-timeline-page-issue-acknowledgement-execution-supersession-and-cancel-events-interface-spec.md`
- `1485-mandate-lineage-receipt-page-authority-scope-duty-state-and-recall-boundary-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `received the packet` can no longer hide whether the recipient may actually act
- authority now stays bounded by scope, world, prerequisites, and freshness instead of by vague seniority or convenience
- cancellation and supersession now explicitly tell downstream actors whether to stop immediately, finish a bounded safe-close, or escalate
- later operators can open one receipt and see what action authority existed, who accepted it, what happened, and what became unsafe to assume later

## Revision addendum — certification publication, audience reliance, and recall truth after rev0388

This tranche locks the next seam around **publication-for-reliance truth**.
The key decisions now made explicit in the archive are:

- **reliance charter is a first-class contract object rather than a side effect of an existing certificate**
- **audience class, safe claim envelope, attached evidence, freshness, supersession, and recall remain separate truths**
- **`sent` is weaker than `received`, `received` is weaker than `understood`, and `understood` is weaker than `delegated custody accepted`**
- **live-linked packets remain visibly stronger than detached snapshots or forwarded stale copies**
- **every serious published claim now needs one receipt that preserves who it was for, what exact sentence it allowed, what exclusions traveled with it, when it staled, and what event recalled or superseded it**

New docs added in this tranche:

- `1474-resilio-certification-publication-audience-reliance-and-recall-fragmentation-evaluation.md`
- `1475-reliance-charter-contract-sheet-page-audience-claim-envelope-and-recall-channel-interface-spec.md`
- `1476-certification-publication-review-page-operator-exec-audit-and-successor-handoff-variants-interface-spec.md`
- `1477-reliance-proof-page-published-claims-obligations-and-supersession-interface-spec.md`
- `1478-reliance-timeline-page-publication-acknowledgement-supersession-and-recall-events-interface-spec.md`
- `1479-reliance-lineage-receipt-page-audience-envelope-freshness-and-recall-boundary-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `we certified it` can no longer hide who is actually allowed to rely on which sentence
- audience downgrades now stay visibly separate from source truth so executive, audit, partner, and successor-operator packets cannot silently widen or flatten claims
- stale screenshots, forwarded exports, and detached snapshots now stay visibly weaker than live-linked packets
- supersession and recall now become first-class lifecycle events instead of buried follow-up chatter
- later operators can open one receipt and see what was published, to whom, with what ceiling, and what weaker sentence old packet holders may still retain unless recall is confirmed

## Status addendum — estate certification seam opened after rev0387

The archive now covers another clean operator seam:

- it already knew how to settle many parity debts through bounded convergence campaigns
- it now also knows how to issue an explicit **estate certification** with exact scope, exclusions, freshness, and revocation triggers

This means the spine can now say all of the following without cheating:

- `cleanup campaigns succeeded for these subjects`
- `this broader certificate is still blocked by these exclusions`
- `this bounded certificate is fresh through this horizon`
- `this event will revoke the stronger sentence automatically`

The newest hardening move is important:

- **campaign closure is weaker than certification**
- **bounded certification is allowed, but universal certification must be earned explicitly**
- **freshness and revocation are now built into the confidence object itself**

## Revision addendum — status shift toward return-delta convergence and cohort settlement after rev0386

The next seam after explicit parity debt is now explicit:

- the archive can already say when one changed active state is tolerated debt, successor candidate, or reopen-worthy
- it still needed to own the harder multi-subject truth where many such states are being judged together and therefore need one campaign, one claim ceiling, and one honest story about stragglers

This pass turns that gap into a first-class product object: **the convergence campaign**.

What is newly true in the archive:

- many tolerated deltas can now be shaped as one settlement effort without hiding subject-level routing
- every subject in a settlement wave now gets an explicit route: exact restore, promote successor, keep temporary, split out, or reopen
- partial success can now publish a bounded stronger sentence without overclaiming across uncovered subjects
- stragglers now remain visible as blockers, not statistical noise
- campaign handoff now preserves settled scope, carried-forward debt, and the next blocked stronger sentence

New docs in this tranche:

- `1462-resilio-return-delta-convergence-cohort-settlement-and-straggler-truth-evaluation.md`
- `1463-convergence-campaign-contract-sheet-page-debt-cohort-target-end-state-and-safety-fences-interface-spec.md`
- `1464-convergence-shaping-review-page-restore-promote-split-and-reopen-routing-interface-spec.md`
- `1465-convergence-proof-page-wave-progress-settlement-class-and-claim-upgrade-interface-spec.md`
- `1466-convergence-timeline-page-wave-entry-reconciliation-settlement-and-straggler-events-interface-spec.md`
- `1467-convergence-lineage-receipt-page-cohort-settlement-coverage-and-blocked-stronger-sentences-interface-spec.md`

### Why this pass matters

The archive now has a cleaner answer to another very common operator failure mode:

> a team cleaned up most of a messy field of changed-but-working states, then gradually started talking as if the whole baseline was back even though a few drifted survivors, reopen-worthy subjects, or successor-only exceptions were still doing all the real blocking work.

That ambiguity is now explicitly disallowed.

## Revision addendum — status shift toward return-delta debt, baseline rebind, and honest successor adoption after rev0385

The next seam after return-to-protection is now explicit:

- the archive can already tell whether activity came back and whether the same protected state returned
- it still needed to own the harder middle where the current state is active and acceptable, but not yet exact parity with the old baseline

This pass turns that middle into a first-class product object: **accepted return-delta debt**.

What is newly true in the archive:

- changed-but-working returns now remain visible as debt until exact restore, successor promotion, or reopen
- tolerated deltas now require explicit owner, expiry, rereview cadence, and blocked stronger sentence
- a successor baseline now requires deliberate promotion rather than silent normalization through time or frequent use
- exact restore, successor promotion, claim narrowing, and reopen now form one decision ladder instead of out-of-band operator folklore
- handoff now preserves the next forbidden overclaim: `still syncing` may not silently round up to `same protected state`

New docs in this tranche:

- `1456-resilio-return-delta-debt-baseline-rebind-and-reopen-fragmentation-evaluation.md`
- `1457-return-delta-contract-sheet-page-accepted-successor-delta-expiry-and-owner-interface-spec.md`
- `1458-delta-aging-review-page-restore-exact-promote-successor-or-reopen-interface-spec.md`
- `1459-parity-debt-proof-page-temporary-accepted-delta-baseline-rebind-and-claim-ceiling-interface-spec.md`
- `1460-return-delta-timeline-page-accepted-drift-expiry-promotion-and-reopen-events-interface-spec.md`
- `1461-return-delta-lineage-receipt-page-parity-debt-owner-expiry-and-blocked-stronger-sentences-interface-spec.md`

### Why this pass matters

The archive now has a cleaner answer to a very common operator failure mode:

> a system came back in a changed state, kept working, and everyone gradually started treating that changed state as the intended baseline without ever deciding whether it was debt, successor, or latent failure.

That ambiguity is now explicitly disallowed.

## Revision addendum — control re-arm, return-to-protection, and post-bypass reconciliation after rev0384

This pass locks the next seam after control suspension: **control re-arm / return-to-protection / post-bypass reconciliation**.
The archive already knew how to suspend a control truthfully and preserve what survives during the bypass.
What it still lacked was one ordinary operator answer to:

> when activity comes back, did we actually recreate the same protected state, what structural delta remains, and what proof is still required before the stronger sentence returns?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on current re-entry fragmentation across resume, reconnect, disconnected-mode connect, existing-directory merge, placeholder behavior, path defaults, Android Simple mode, and permission restoration
- five new **interface specs** for return contract, re-arm readiness review, return proof, post-bypass reconciliation timeline, and return lineage receipt
- five hard product decisions:
  - **`resumed`, `reconnected`, `reattached`, `merged`, and `requalified` remain separate states**
  - **every return must publish structural deltas, not just motion resumed**
  - **exact restoration and accepted-successor return are separate truths**
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

> `when activity comes back, are we back to the same protected state or only moving again in a changed one?`

## Revision addendum — control suspension, break-glass, and stop semantics after rev0383

This pass locks the next seam after control attestation: **control suspension / break-glass / truth-preserving stop semantics**.
The archive already knew how to attest a live control and withdraw trust when drift appears.
What it still lacked was one ordinary operator answer to:

> if we temporarily stop or weaken a control, what exactly stops, what explicitly continues, when does it resume, and what proof is required before the stronger trust sentence can come back?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on current stop-semantic fragmentation across pause, scheduler pause, disconnect/remove, synchronization modes, per-share network gates, mobile/system-mediated stops, and peer revocation
- five new **interface specs** for suspension contract, bypass review, suspension proof, stop-semantic timeline, and suspension-lineage receipt
- five hard product decisions:
  - **`paused`, `stopped`, `disconnected`, `detached`, and `revoked` remain separate states**
  - **every active bypass must publish surviving effects, not just requested effects**
  - **resume availability and trust restoration are separate truths**
  - **overstayed bypasses automatically worsen posture even without a visible incident**
  - **temporary suspension must preserve the next forbidden overclaim**

New docs in this tranche:

- `1444-resilio-control-suspension-break-glass-and-stop-semantic-fragmentation-evaluation.md`
- `1445-control-suspension-contract-sheet-page-requested-effect-surviving-effects-and-resume-class-interface-spec.md`
- `1446-bypass-review-page-pause-disconnect-network-gate-and-claim-downgrade-interface-spec.md`
- `1447-suspension-proof-page-approved-bypass-surviving-propagation-and-rearm-conditions-interface-spec.md`
- `1448-stop-semantic-timeline-page-pause-entry-auto-resume-detach-and-trust-restoration-interface-spec.md`
- `1449-suspension-lineage-receipt-page-active-bypass-surviving-effects-and-next-rearm-proof-interface-spec.md`

### Why this pass matters

The previous tranche answered `why do we still trust this control?`
This tranche answers the next harder question:

> `if we suspend it on purpose, what is still happening, and what must be re-proved before the old claim is safe again?`

## Revision addendum — guardrail attestation, rehearsal, and silent trust decay after rev0382

This pass locks the next seam after case-to-guardrail promotion: **control trust after activation**.
The archive already knew how to promote a control, activate it, and watch for recurrence.
What it still lacked was one explicit answer to:

> what proves this control is still trustworthy right now, what witness is strong enough, and what event silently withdraws that trust before the next painful repeat?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on why current control trust still fragments across power-user settings, folder preferences, config mode, service mode, mobile settings, scheduler, LAN-only instructions, restart requirements, and world-fork notes rather than one durable attestation workflow
- five new **interface specs** for control attestation contract sheet, attestation review, rehearsal proof, control-decay timeline, and attestation-lineage receipt
- a tighter non-clone line based on current official Resilio evidence that a careful operator can configure real controls, but still has to reconstruct `do we still trust this control now, and why?` from separate surfaces and KB memory
- five hard product decisions:
  - **configured, active, and trusted remain separate states**
  - **every meaningful control must publish at least one witness stronger than `visible setting value`**
  - **passive quiet windows may renew freshness but may not by themselves earn a stronger preventive sentence**
  - **missed attestation, version drift, world forks, ignored settings, and prerequisite loss can withdraw trust without a visible incident**
  - **some controls require rehearsal or paired-surface attestation instead of waiting for a real repeat**

New docs in this tranche:

- `1438-resilio-control-attestation-rehearsal-and-silent-decay-fragmentation-evaluation.md`
- `1439-control-attestation-contract-sheet-page-mechanism-prerequisite-and-witness-class-interface-spec.md`
- `1440-attestation-review-page-live-check-synthetic-drill-passive-witness-and-claim-ceiling-interface-spec.md`
- `1441-control-rehearsal-proof-page-drill-scope-observed-barrier-and-stale-trust-withdrawal-interface-spec.md`
- `1442-control-decay-timeline-page-version-drift-world-fork-missed-check-and-trust-loss-interface-spec.md`
- `1443-control-attestation-lineage-receipt-page-latest-proof-mechanism-and-blocked-stronger-sentences-interface-spec.md`

### Why this pass matters

The previous tranche answered `what durable guardrail came out of the case?`
This tranche answers the next harder question:

> `why do we still trust that guardrail today, and what exact event makes the old trust unsafe to reuse?`

## Revision addendum — case-to-guardrail promotion, preventive controls, and recurrence watch after rev0381

This pass locks the next seam after honest case closure: **case-to-guardrail promotion**.
The archive already knew how to choose a fix, run it safely, and close the case honestly.
What it still lacked was one explicit answer to:

> what durable control, watch, or capture-on-repeat runbook did this case teach us to create, and what stronger prevention claim is still blocked?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on why current preventive ingredients still live across watcher-limit KBs, scheduler/settings pages, power-user preferences, config mode, service setup, live graphs, and changelog memory rather than one durable case-to-control workflow
- five new **interface specs** for preventive control contract sheet, control promotion review, control activation proof, recurrence watch timeline, and control-lineage receipt
- a tighter non-clone line based on current official Resilio evidence that a careful operator can find many real guardrail ingredients, but still has to reconstruct `what did we permanently change because of this case, what does it cover, and how will we know if it escaped?` from separate surfaces
- five hard product decisions:
  - **every non-trivial closed case must end in a typed guardrail verdict**
  - **preventive, detective, containment, and capture-only classes remain non-collapsible**
  - **every active control publishes scope, prerequisites, and at least one anti-claim**
  - **quiet windows, near misses, early detections, contained repeats, and strongly prevented repeats remain separate evidence rungs**
  - **drift and same-cause escapes automatically downgrade the strongest safe preventive sentence**

New docs in this tranche:

- `1432-resilio-case-promotion-preventive-control-and-recurrence-watch-fragmentation-evaluation.md`
- `1433-preventive-control-contract-sheet-page-source-case-hazard-signature-and-coverage-scope-interface-spec.md`
- `1434-control-promotion-review-page-prevent-detect-mitigate-watch-and-no-control-verdict-interface-spec.md`
- `1435-control-activation-proof-page-rollout-owner-rereview-and-does-not-protect-interface-spec.md`
- `1436-recurrence-watch-timeline-page-near-miss-repeat-prevented-event-and-control-drift-interface-spec.md`
- `1437-control-lineage-receipt-page-case-origin-coverage-class-and-blocked-stronger-sentences-interface-spec.md`

### Why this pass matters

The previous tranche answered `what do we now believe and what would reopen the case?`
This tranche answers the next harder question:

> `what durable structure prevents this from degrading into folklore, and how honest are we about what it still does not prevent?`

## Revision addendum — incident case truth, root-cause adjudication, and honest closure after rev0380

This pass locks the next seam after remediation execution: **case reasoning and closure truth**.
The archive already knew how to choose and run a corrective action.
What it still lacked was one explicit answer to:

> after the run, what do we now believe caused the problem, what did we rule out, what remains unknown, how honest is closure, and what exact event should reopen the case later?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on why current cause reasoning and closure still live across warnings, history, queues, logs, and support/forum escalation rather than one durable case object
- five new **interface specs** for incident case contract sheet, hypothesis adjudication review, case closure proof, incident case timeline, and case-lineage receipt
- a tighter non-clone line based on current official Resilio evidence that the ordinary operator task `decide what we now believe and whether this case is honestly closed` still depends on many separate articles and artifacts
- five hard product decisions:
  - **every material degradation becomes a first-class incident case object**
  - **supported, refuted, unresolved, and combined causes stay separate**
  - **closure classes remain typed and non-collapsible**
  - **residual risk and reopen triggers stay explicit even after apparent recovery**
  - **support artifacts can inform the case but cannot replace adjudication**

New docs in this tranche:

- `1426-resilio-root-cause-adjudication-case-closure-and-reopen-criteria-fragmentation-evaluation.md`
- `1427-incident-case-contract-sheet-page-symptom-cluster-hypotheses-and-target-sentence-interface-spec.md`
- `1428-hypothesis-adjudication-review-page-supported-refuted-unresolved-and-competing-causes-interface-spec.md`
- `1429-case-closure-proof-page-resolved-mitigated-unresolved-reopen-triggers-and-residual-risk-interface-spec.md`
- `1430-incident-case-timeline-page-symptom-branch-elimination-cause-promotion-and-reopen-events-interface-spec.md`
- `1431-case-lineage-receipt-page-cause-status-residual-risk-and-blocked-stronger-sentences-interface-spec.md`

### Why this pass matters

The previous tranche answered `how do we execute the chosen repair safely?`
This tranche answers the next harder question:

> `what do we now believe, what closure class is honest, and what exactly would force a reopen?`

Current official Resilio material is useful here because it does preserve real cause diversity, but still too diffusely for a clone.
The clearest current cluster is:

- `Sync Main View (Desktop)` still exposes 30-day History and search/filter
- `My files don't sync` still routes the operator through warning, history, and queue evidence
- `Errors and warnings` / `Core warnings` still spread one visible trouble surface across many distinct warning/cause articles
- `Database error`, `Cannot download files ...`, `Agent run out of system notify watchers`, `Service files missing`, `SE_SM_NO_IDENTITY`, and `Error 205` still show materially different cause families
- `Some internal tasks are taking time to complete` still blocks premature over-closure with a self-recovery branch
- `Collecting debug logs automatically` still asks for timestamps, peer role, and affected shares/files while also narrowing direct support availability for Sync v3

## Revision addendum — remediation run choreography, checkpoints, and safe abort after rev0379

This pass locks the next seam after typed intervention selection: **remediation execution**.
The archive already knew how to choose the least-destructive justified next action.
What it still lacked was one explicit answer to:

> once the action is chosen, how do we execute it safely, in what order, with what preflight checks, with what witness checkpoints, and at what point do we stop instead of compounding damage or ambiguity?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on execution choreography scattered across restart, reconnect, re-add, service-world, config-world, watcher-limit, and artifact-capture docs
- five new **interface specs** for remediation-run contract sheet, execution-readiness review, checkpointed-run proof, remediation-run timeline, and execution-lineage receipt
- a tighter non-clone line based on current official Resilio evidence that the ordinary operator task `perform the chosen fix safely and know when to stop` still depends on many separate articles
- five hard product decisions:
  - **every material multi-step intervention becomes a first-class remediation run object**
  - **preflight gates, quiet points, and destructive boundaries are explicit**
  - **checkpoint evidence governs safe-continue versus safe-abort**
  - **archive/path/world-fork risks block destructive progress until cleared**
  - **handoff preserves next allowed and next forbidden action explicitly**

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

Current official Resilio material is useful here precisely because it is candid about ordered repairs, but still too scattered for a clone.
The clearest current cluster is:

- `My files don't sync` still front-loads peer/warning/history/queue inspection
- `Database error` still publishes restart → reconnect → all-peer re-add ordering
- `Service files missing / Cannot identify destination folder` still requires archive review before `.sync` deletion and re-add
- `Disconnecting and Removing Folders` still distinguishes disconnect, reconnect, and remove with different path implications
- `Sync Service Troubleshooting on Windows` still shows permission repair that also creates a new service world and demands restart plus re-add / reconnect
- `Running Sync in configuration mode` still ties config placement and `storage_path` to start semantics and world creation
- `Collecting debug logs automatically` still makes evidence capture a timed run with restart and reproduce steps
- `Agent run out of system notify watchers` still ends in restart after changing the system limit
- `How soon does synchronization start?` still makes post-fix proof depend on rescan posture
- `Some internal tasks are taking time to complete` still leaves room for self-recovery instead of immediate escalation

## Revision addendum — intervention ladder, chosen-action proof, and post-action truth after rev0378

This pass locks the next seam after typed rollout-health evidence: **intervention selection**.
The archive already knew how to define rollout health, grade confidence, and decide whether promotion should widen or hold.
What it still lacked was one explicit answer to:

> once the product judges health as ambiguous, degraded, blocked, or risky, what exact intervention should happen next, how destructive is it, and what proof would distinguish symptom relief from real repair?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on remediation advice scattered across restart, reconnect, re-add, service-world, identity, watcher-limit, and support-artifact docs
- five new **interface specs** for intervention contract sheet, remediation-ladder review, intervention approval proof, remediation timeline, and intervention receipt
- a tighter non-clone line based on current official Resilio evidence that the ordinary operator task `choose the least-destructive justified next intervention` still depends on many separate troubleshooting articles
- five hard product decisions:
  - **every material corrective action becomes a first-class intervention object**
  - **least-destructive viable action wins**
  - **observe / wait and artifact capture are typed actions**
  - **reversibility, blast radius, and post-action proof ceiling stay separate**
  - **symptom disappearance remains weaker than root-cause removal**

New docs in this tranche:

- `1414-resilio-intervention-selection-remediation-ladder-and-post-action-proof-fragmentation-evaluation.md`
- `1415-intervention-contract-sheet-page-candidate-action-risk-and-success-claim-interface-spec.md`
- `1416-remediation-ladder-review-page-least-destructive-next-action-and-escalation-interface-spec.md`
- `1417-intervention-approval-proof-page-chosen-action-rollback-and-post-action-check-interface-spec.md`
- `1418-remediation-event-timeline-page-attempt-result-cooldown-and-escalation-interface-spec.md`
- `1419-intervention-lineage-receipt-page-action-basis-reversibility-and-outcome-ceiling-interface-spec.md`

### Why this pass matters

The previous tranche answered `is the rollout healthy enough to widen?`
This tranche answers the next harder question:

> `if not, or if the health picture is still ambiguous, what should we actually do next — and what proof would make that action count as success rather than mere activity?`

Current official Resilio material is useful here precisely because it is candid that many different intervention types exist, but still too scattered for a clone.
The clearest current cluster is:

- `My files don't sync` still suggests re-add, disk check, restart, free-space action, deletion of stuck `.!sync` files, and time-difference correction
- `Database error` still presents a rough ladder from restart, to reconnect, to re-add on all peers, to debug-log escalation
- `Peers aren't connecting` still pushes operators into tracker, predefined-host, firewall, routing, multicast, and NIC actions
- `Service files missing / Cannot identify destination folder` still says remediation can require removing the share, deleting `.sync`, and adding the share back
- `Core warnings` still includes identity and license interventions
- `Agent run out of system notify watchers` still turns a warning into system-limit change plus restart
- `Sync Service Troubleshooting on Windows` still includes a permission workaround that can fork the service storage world and require re-add / re-share of all folders
- `Collecting debug logs automatically` still makes artifact capture itself an action with restart and observation costs

## Revision addendum — rollout health, signal adjudication, and promotion confidence after rev0377

This pass locks the next seam after typed rollout: **rollout health evidence**.
The archive already knew how to define rings, gates, stop conditions, and rollback class.
What it still lacked was one explicit answer to:

> once a rollout is live, what evidence actually justifies widening it, holding it, freezing it, or rolling it back?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on real-time graphs, warnings, history, hidden background work, log/profiler artifacts, and evidence freshness
- five new **interface specs** for rollout-health contract sheet, signal-adjudication review, promotion-confidence proof, health-event timeline, and rollout-health receipt
- a tighter non-clone line based on current official Resilio evidence about ongoing-only performance graphs, multi-plane troubleshooting, hidden work that can self-recover, restart-bound log collection, and warning/stat signal evolution in the change logs
- five hard product decisions:
  - **every serious rollout gets a first-class health object**
  - **signal classes are explicit and typed**
  - **promotion confidence is graded**
  - **evidence freshness is published before promotion widens**
  - **support artifacts cannot silently become durable product truth**

New docs in this tranche:

- `1408-resilio-rollout-health-signal-adjudication-and-evidence-freshness-fragmentation-evaluation.md`
- `1409-rollout-health-contract-sheet-page-signal-classes-evidence-window-and-promotion-readiness-interface-spec.md`
- `1410-signal-adjudication-review-page-warnings-history-graphs-logs-and-human-escalation-interface-spec.md`
- `1411-promotion-confidence-proof-page-greenhold-redstop-and-evidence-freshness-interface-spec.md`
- `1412-rollout-health-event-timeline-page-warning-flap-recovery-escalation-and-sentence-change-interface-spec.md`
- `1413-rollout-health-lineage-receipt-page-signal-basis-confidence-grade-and-blocked-stronger-sentences-interface-spec.md`

### Why this pass matters

The previous tranche answered `are we allowed to widen this rollout in principle?`
This tranche answers the next harder question:

> `given the evidence we have right now, are we actually healthy enough to widen it, or are we mistaking narrow, stale, or weak signals for durable promotion truth?`

Current official Resilio material is useful here precisely because it is candid about multiple evidence planes, but still too scattered for a clone.
The clearest current cluster is:

- current performance docs still expose only short-window real-time graphs and remind the operator that some host-load metrics are not Sync-only
- current troubleshooting docs still require hopping among peers, status warnings, history, queues, and long cause lists
- current warning docs still separate many warning families into distinct KB articles
- current `Some internal tasks...` docs still admit hidden work, intermittent recovery, and escalation-to-logs when symptoms persist
- current log docs still admit evidence collection has prerequisites, restart cost, and limited support lanes for v3
- current power-user docs still publish profiler/logging controls with their own activation debt
- current change logs still preserve that health surfaces and warning accuracy have evolved over time

## Revision addendum — policy rollout rings, readiness gates, and safe promotion after rev0376

This pass locks the next seam after typed policy lifecycle: **policy rollout**.
The archive already knew how to define predecessors, successors, waivers, and retirement posture.
What it still lacked was one explicit answer to:

> once a successor policy exists, how do we move it through canary, pilot, and broad rings without confusing compatibility, eligibility, publication, and safe promotion?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on staged rollout risk, upgrade-lane fragmentation, install-posture-specific update paths, restart debt, and rollback truth
- five new **interface specs** for rollout contract sheet, readiness review, ring-promotion proof, rollout-event timeline, and rollout receipt
- a tighter non-clone line based on current official Resilio evidence about v2/v3 compatibility versus linked-major conflict, Business/v3 limits, platform-envelope splits, feature availability by version/entitlement, default/service/CLI/config update-path differences, restart-required settings, and service clean-install or storage-world forks
- five hard product decisions:
  - **every policy successor rollout is a first-class rollout object**
  - **ring membership is explicit and typed**
  - **promotion is gate-based**
  - **stop conditions can freeze broader rollout automatically**
  - **rollback class is declared before promotion**

New docs in this tranche:

- `1402-resilio-policy-rollout-rings-readiness-gates-and-rollback-window-fragmentation-evaluation.md`
- `1403-policy-rollout-contract-sheet-page-successor-target-rings-readiness-gates-and-stop-conditions-interface-spec.md`
- `1404-rollout-readiness-review-page-version-floor-waiver-debt-restart-cost-and-world-eligibility-interface-spec.md`
- `1405-ring-promotion-proof-page-canary-pilot-broad-freeze-auto-stop-and-rollback-class-interface-spec.md`
- `1406-rollout-event-timeline-page-stage-entry-promotion-freeze-stop-rollback-and-reopen-events-interface-spec.md`
- `1407-policy-rollout-lineage-receipt-page-revision-ring-gate-stop-basis-and-blocked-stronger-sentences-interface-spec.md`

### Why this pass matters

The previous tranche answered `what policy succeeds what and who is still on the old one?`
This tranche answers the next harder question:

> `are we actually ready to widen the successor rollout, or are we still mistaking a successful canary, byte compatibility, or subset-only feature safety for true broad-readiness?`

Current official Resilio material is useful here precisely because it is candid about movement constraints, but still too scattered for a clone.
The clearest current cluster is:

- current FAQ docs still separate sync compatibility from mixed-major linked-family safety
- current v3 update docs still separate supported personal upgrades from Business-held no-go lanes and still make the upgrade procedure depend on installation posture
- current platform docs still publish different v2/v3 envelopes that affect who can move at all
- current feature docs still publish version and entitlement gates
- current power-user docs still publish version drift and restart-required activation for some fields
- current service docs still publish migrate-vs-clean-install and restart-bound config branches
- current change-log history still shows that restart, autoupdate persistence, and license-application timing are real rollout-adjacent failure sources

## Revision addendum — policy lifecycle, supersession, and safe retirement after rev0375

This pass locks the next seam after typed waivers: **policy family lifecycle**.
The archive already knew how to define profile truth and explain divergence.
What it still lacked was one explicit answer to:

> when a newer policy arrives, what exact relation does it have to the old one, who really moves, what happens to waivers, and when is the predecessor actually retired rather than merely deprecated?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on supersession, successor worlds, migration-vs-fork, and retirement evidence debt
- five new **interface specs** for lifecycle contract sheet, supersession review, promotion/retirement proof, family timeline, and lifecycle receipt
- a tighter non-clone line based on current official Resilio evidence about deprecated settings, Standard-folder remove/re-add replacement, disconnect vs remove vs reconnect, config-world forks, migrated-vs-clean service successors, Local System storage-world replacement, identity regeneration, and settings teardown
- four hard product decisions:
  - **every governed profile belongs to a policy family and every family change gets a typed successor relation**
  - **retirement is a first-class state rather than silent deletion**
  - **waivers never auto-carry silently across supersession**
  - **subjects stay explicitly classified as on-current, on-deprecated, grandfathered, blocked-from-successor, orphaned, or retired-with-no-successor**

New docs in this tranche:

- `1396-resilio-policy-supersession-retirement-and-successor-world-fragmentation-evaluation.md`
- `1397-policy-lifecycle-contract-sheet-page-predecessor-successor-relation-and-retirement-scope-interface-spec.md`
- `1398-supersession-review-page-cohort-adoption-waiver-carryforward-and-orphan-risk-interface-spec.md`
- `1399-promotion-and-retirement-proof-page-successor-cutover-coverage-and-blocked-subjects-interface-spec.md`
- `1400-policy-family-timeline-page-promotion-deprecation-split-merge-rollback-and-sunset-events-interface-spec.md`
- `1401-policy-lifecycle-lineage-receipt-page-predecessor-successor-status-and-blocked-stronger-sentences-interface-spec.md`

## Current status

The archive now has a clearer settings-governance staircase:

- find the canonical setting
- prove who a change touches
- compare subjects to a baseline
- bind subjects to named profiles
- explain why nonconforming subjects are excluded or waived
- prove when a newer policy truly succeeds, branches, rolls back, or retires an older one

That last rung is what this revision adds.
It means later operators no longer need to remember whether a `new policy` story is really a revision bump, service-world fork, config-world successor, identity reset, grandfathered predecessor, or a true retirement event.
The receipt family now carries that burden directly.

## Revision addendum — policy-waiver pack, exception class, and expiry review after rev0374

This pass locks the next seam after named policy profiles: **typed policy waivers and exception debt**.
The archive already knew how to name a profile and compare conformance.
What it still lacked was one explicit product answer to:

> this subject is not cleanly on profile — is that unsupported, ignored, local-only, mid-migration, or intentionally waived, and when must we revisit that judgment?

This revision adds that answer.
It contributes:

- one new **Resilio evaluation** focused on policy-waiver, applicability, and expiry fragmentation
- five new **interface specs** for waiver contract sheet, waiver cohort review, waiver issuance proof, waiver drift timeline, and waiver lineage receipt
- a tighter non-clone line based on current official Resilio evidence about desktop-only surfaces, Linux-WebUI ignored advanced fields, mobile share-local routes, Android Simple-mode capability limits, config-only Standard-folder scope, config-authored WebUI suppression, storage/world forks, service migration vs clean-install forks, and identity replacement side effects
- three hard product decisions:
  - **every material profile divergence becomes either a typed waiver or a hard non-support verdict**
  - **waiver classes stay explicit — unsupported world, unsupported surface, ignored runtime, local-parallel lane, missing prerequisite, migration gap, and hard out-of-policy are not one thing**
  - **waivers expire by default, require owners and removal conditions, and do not count as clean conformance**

New docs in this tranche:

- `1390-resilio-policy-waiver-class-exception-expiry-and-applicability-fragmentation-evaluation.md`
- `1391-policy-waiver-contract-sheet-page-exception-scope-prerequisite-gap-and-expiry-interface-spec.md`
- `1392-waiver-cohort-review-page-unsupported-worlds-ignored-fields-device-local-lanes-and-debt-class-interface-spec.md`
- `1393-waiver-issuance-proof-page-approve-timebox-recheck-and-rollout-blocking-interface-spec.md`
- `1394-waiver-drift-timeline-page-prerequisite-met-expiry-renewal-and-unplanned-coverage-loss-interface-spec.md`
- `1395-waiver-lineage-receipt-page-profile-gap-expiry-review-duty-and-blocked-stronger-sentences-interface-spec.md`

## Current status

The archive now has a clearer and tighter settings-governance staircase:

- find the canonical setting
- prove who a change touches
- compare subjects to a baseline
- bind subjects to named profiles
- explain why nonconforming subjects are excluded, degraded, blocked, or timeboxed

That last rung is what this revision adds.
It means later operators no longer need to remember whether a nonconforming subject was `really unsupported`, `temporarily waived`, `ignored by runtime`, `local-only`, or just never rechecked after a fork.
The receipt family now carries that burden directly.

## Revision addendum — policy-profile pack, binding class, and conformance rollout after rev0373

This tranche locks the next seam around **reusable policy profile truth**.
The key decisions now made explicit in the archive are:

- **every reusable defaults bundle must be a first-class versioned policy-profile object rather than a remembered cluster of global, per-share, config, and mobile settings**
- **`live-inherit`, `field-pin`, `frozen-snapshot`, `branched-profile`, and `unbound` are different binding truths**
- **field coverage is explicit, so nearby settings can no longer quietly ride along under `the usual defaults` language**
- **profile scope is world-aware, so config-authored worlds, service forks, mobile-local lanes, and interactive desktop lanes remain separate until explicitly joined**
- **profile revision rollout is compare-first, mutate-second, and `same current values` is weaker than `will adopt future revisions`**
- **every serious profile inspection or rollout now needs one receipt that preserves profile id, revision, field coverage, binding class, conformance grade, and blocked stronger sentence**

New docs added in this tranche:

- `1384-resilio-policy-profile-pack-binding-revision-and-conformance-fragmentation-evaluation.md`
- `1385-policy-profile-contract-sheet-page-profile-signature-field-coverage-and-binding-class-interface-spec.md`
- `1386-profile-conformance-review-page-live-bindings-field-pins-frozen-copies-and-unbound-subjects-interface-spec.md`
- `1387-profile-attach-and-rollout-proof-page-target-cohort-adoption-mode-and-revision-safety-interface-spec.md`
- `1388-profile-drift-timeline-page-revision-bump-field-pin-freeze-branch-and-rejoin-events-interface-spec.md`
- `1389-profile-lineage-receipt-page-profile-signature-binding-class-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `our defaults profile` can no longer hide whether the product is talking about linked-device arrival posture, per-folder behavior, advanced defaults, config-authored replication, or a mobile-local share lane
- profile membership now has binding classes, so value coincidence can no longer impersonate live inheritance
- future profile revisions now publish which subjects will adopt them, which will stay pinned, which are frozen snapshots, and which belong to another branch or world
- batch profile rollout can no longer quietly bind unsupported worlds or erase intentional pins
- later operators can open one receipt and see what profile revision was in force, what field coverage actually existed, what class of binding was proven, what rollout happened or was blocked, and which stronger `on profile` sentence the product refused to make

## Revision addendum — setting-baseline anchor, equivalence grade, and safe realignment after rev0372

This tranche locks the next seam around **settings baseline and equivalence truth**.
The key decisions now made explicit in the archive are:

- **every serious settings comparison must compile to a normalized governance signature rather than relying on display label plus visible value**
- **`same label`, `same visible value`, `same effective value now`, `same governance state`, and `same baseline conformance` are different truths**
- **local custom share names are navigational aids, not reliable anchors for parity claims**
- **realignment is compare-first, mutate-second, and `restore inheritance` is a different action from merely matching the currently displayed value**
- **mobile-local lanes, startup-config worlds, migrated service worlds, and clean-install service forks remain separate comparison domains until explicitly joined**
- **every serious settings comparison now needs one receipt that preserves canonical anchor, normalized signature, equality grade, safe realignment action, and the blocked stronger sentence**

New docs added in this tranche:

- `1378-resilio-setting-baseline-anchor-equivalence-grade-and-realignment-fragmentation-evaluation.md`
- `1379-setting-baseline-contract-sheet-page-anchor-subject-signature-and-equivalence-grade-interface-spec.md`
- `1380-equivalence-review-page-visible-match-effective-match-governance-match-and-false-friends-interface-spec.md`
- `1381-realignment-proof-page-align-keep-detached-split-branch-and-reanchor-subjects-interface-spec.md`
- `1382-baseline-drift-timeline-page-default-shift-local-rename-override-world-fork-and-rejoin-events-interface-spec.md`
- `1383-baseline-lineage-receipt-page-anchor-signature-equivalence-grade-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `same value` can no longer hide whether the subject is inheriting, explicitly detached, mobile-local, config-authored, or living in another service world
- comparison now has grades, so superficial sameness can no longer impersonate governance equivalence or baseline conformance
- local UI aliases can no longer masquerade as canonical subject anchors during audits or bulk alignment
- `align to baseline` now publishes whether it changes value only, governance state, world scope, or subject anchoring assumptions
- later operators can open one receipt and see what baseline was used, what subject was really under review, what grade of sameness was proven, and which stronger parity sentence the product refused to make

## Revision addendum — setting-impact cohort, detached overrides, and inherit-vs-explicit-none truth after rev0371

This tranche locks the next seam around **settings impact truth**.
The key decisions now made explicit in the archive are:

- **every meaningful settings mutation must compile to an explicit target cohort before commit**
- **`inherit` and explicit `none/off` are different truths and must never share one ambiguous control state**
- **`same visible value` is weaker than `same inheritance state`**
- **detached exceptions stay visible at default-change time instead of being discovered later by surprise**
- **service worlds, startup worlds, mobile-local lanes, and interactive desktop worlds are separate until explicitly joined**
- **every serious settings mutation now needs one receipt that preserves included cohort, excluded cohort, inherit-vs-explicit verdict, activation rung, and the blocked stronger sentence**

New docs added in this tranche:

- `1372-resilio-setting-impact-cohort-detached-overrides-and-inheritance-reset-fragmentation-evaluation.md`
- `1373-setting-impact-contract-sheet-page-target-cohort-detached-overrides-and-inherit-vs-explicit-none-interface-spec.md`
- `1374-impact-cohort-review-page-global-default-share-override-mobile-parallel-and-service-world-branches-interface-spec.md`
- `1375-precommit-impact-proof-page-subjects-that-will-change-stay-detached-or-require-reattach-interface-spec.md`
- `1376-impact-drift-timeline-page-default-shift-override-creation-explicit-none-reattach-and-world-fork-events-interface-spec.md`
- `1377-impact-lineage-receipt-page-target-cohort-detached-exceptions-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `change default` can no longer hide which subjects will actually adopt the new value
- a share that currently displays `None` can no longer impersonate either `inherit` or `explicit none` without a separate verdict
- reattach is now its own action rather than a side effect of visible-value coincidence
- service migration, clean-install service, config-world edits, and mobile-parallel settings can no longer masquerade as one universal cohort
- later operators can open one receipt and see which subjects were in scope, which were protected exceptions, what inheritance state the focused subject was in, and what stronger blast-radius sentence the product refused to make

## Revision addendum — setting-surface discoverability, route locality, and interface locator truth after rev0370

This tranche locks the next seam around **setting-surface discoverability truth**.
The key decisions now made explicit in the archive are:

- **every meaningful setting is a first-class object with one canonical identity rather than a loose label scattered across menus and config files**
- **scope, visibility, editability, authority, and activation are different truths**
- **`I can see this value here` is weaker than `I can edit it here`, and `I can edit it here` is weaker than `this surface wins`**
- **search and deep-linking now compile to a setting object instead of just opening whatever menu seemed nearby**
- **every serious settings sentence now needs one receipt that preserves query, canonical setting, scope, edit route, authority winner, activation rung, and the blocked stronger sentence**

New docs added in this tranche:

- `1366-resilio-setting-surface-discoverability-route-and-context-fragmentation-evaluation.md`
- `1367-setting-locator-contract-sheet-page-canonical-setting-scope-and-edit-route-interface-spec.md`
- `1368-setting-route-review-page-desktop-folder-mobile-config-and-service-branches-interface-spec.md`
- `1369-setting-context-proof-page-visible-vs-editable-vs-authoritative-here-interface-spec.md`
- `1370-setting-change-itinerary-page-query-route-edit-activation-and-verification-events-interface-spec.md`
- `1371-setting-lineage-receipt-page-query-route-scope-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `open settings` can no longer hide whether the needed change lives in global desktop preferences, per-folder preferences, power-user defaults, mobile settings, startup config, or a service-owned route
- same-looking labels across surfaces can no longer impersonate one shared authority without an explicit route and scope object
- search now becomes semantic rather than menu-local: it finds the setting object, not just the nearest UI string
- witness-only surfaces now stay visibly weaker than mutation-authority surfaces, so `I saw the value in WebUI` cannot overclaim `I can change it there`
- later operators can open one receipt and see what query was resolved, what surface won, what scope it governed, how activation worked, and which stronger settings sentence the product refused to make

## Revision addendum — activation boundary, restart debt, and cold-apply truth after rev0364

This tranche locks the next seam around **activation-boundary truth**.
The key decisions now made explicit in the archive are:

- **activation rung is a first-class contract object rather than a side effect of vague `saved`, `applied`, or `restart if needed` language**
- **live-now, next-rescan, next-local-restart, next-service-restart, next-cohort-restart, and successor-cutover activation are different truths**
- **`saved` is weaker than `active in runtime`, and `restart recommended` is weaker than `restart is the first honest activation rung`**
- **`config present on disk` is weaker than `the active process has adopted it`, and `restart completed` is weaker than `old cached world debt is actually burned down`**
- **every serious setting, repair, or mode-change claim now needs one receipt that preserves mutation locus, activation rung, residual old-world debt, witness class, and the blocked stronger sentence**

New docs added in this tranche:

- `1330-resilio-activation-boundary-restart-debt-and-cold-apply-fragmentation-evaluation.md`
- `1331-activation-boundary-contract-sheet-page-live-apply-rescan-restart-and-cutover-rungs-interface-spec.md`
- `1332-restart-debt-review-page-ignorelist-filedelay-debug-logging-webui-and-lan-cache-branches-interface-spec.md`
- `1333-applied-state-proof-page-live-now-next-rescan-next-restart-and-service-restart-evidence-interface-spec.md`
- `1334-activation-timeline-page-config-edit-rescan-restart-cache-burn-and-cutover-events-interface-spec.md`
- `1335-activation-boundary-lineage-receipt-page-change-basis-activation-rung-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `saved` can no longer hide whether a change is active immediately, only after rescanning, only after a local restart, or only after a service/successor restart
- restart advice now stays visibly separate from activation truth instead of letting `recommend restart` masquerade as `runtime already matches disk`
- cold-loaded config, hot-reread files, and cache-burn sequences now publish different activation rungs instead of collapsing into one `applied` sentence
- later operators can open one receipt and see where the mutation landed, what event actually activated it, what stale runtime debt still remained, and which stronger immediacy sentence the product still refused to make

## Revision addendum — transfer-cost truth, resend geometry, and splittability ceiling after rev0363

This tranche locks the next seam around **transfer-cost truth**.
The key decisions now made explicit in the archive are:

- **transfer cost is a first-class contract object rather than a side effect of `sync only changed data` language**
- **piecewise delta, whole-file resend, archive-hit rename reuse, queue priority, and splittability ceiling are different truths**
- **`higher priority` is weaker than `lower byte cost`, and `suspended` is weaker than `cancelled`**
- **`same bytes under a new pathname` is weaker than `rename reuse is actually proven on this cohort`**
- **every serious movement claim now needs one receipt that preserves byte-cost basis, reuse path, splittability class, queue order, and the blocked stronger sentence**

New docs added in this tranche:

- `1324-resilio-transfer-cost-resend-geometry-and-splittability-ceiling-fragmentation-evaluation.md`
- `1325-transfer-cost-contract-sheet-page-splittability-reuse-basis-and-order-vs-byte-cost-interface-spec.md`
- `1326-resend-geometry-review-page-piece-shift-rename-reuse-and-archive-gate-interface-spec.md`
- `1327-byte-cost-proof-page-piecewise-delta-full-resend-and-priority-evidence-interface-spec.md`
- `1328-transfer-shape-timeline-page-queue-preemption-archive-hit-and-whole-file-fallback-events-interface-spec.md`
- `1329-transfer-cost-lineage-receipt-page-byte-cost-basis-reuse-path-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `syncs only changed data` can no longer hide whether the current case is piecewise delta, a whole-file resend after geometry shift, or a rename that only avoids retransmission because Archive supplied the bytes locally
- queue controls now stay visibly separate from byte-cost claims instead of letting `higher priority` impersonate `less network movement`
- splittability is now first-class, so strict priority guarantees cannot silently overextend onto nonsplittable transfer lanes
- rename review now publishes the Archive gate instead of implying that same-content arrivals always avoid retransmission
- later operators can open one receipt and see why bytes moved the way they did here, what was merely reordered, what actually avoided retransmit, and which stronger efficiency sentence the product still refused to make

## Revision addendum — salvage readiness, continuity escrow, and late-decrypt authority after rev0362

This tranche locks the next seam around **salvage readiness truth**.
The key decisions now made explicit in the archive are:

- **salvage readiness is a first-class contract object rather than a vague side effect of `backup` language**
- **ciphertext presence, secret escrow, database continuity, locator readiness, and actual recovery lane are different truths**
- **`encrypted copy exists` is weaker than `future salvage remains possible`, and `future salvage remains possible` is weaker than `the recovery lane is fully proven now`**
- **same-looking folder path is weaker than same database continuity, and same encrypted key is weaker than saved RW decryption authority**
- **every serious encrypted-backup or disaster-recovery sentence now needs one receipt that preserves escrow basis, continuity proof, locator proof, salvage floor, and the blocked stronger sentence**

New docs added in this tranche:

- `1318-resilio-salvage-readiness-escrow-continuity-and-late-decrypt-fragmentation-evaluation.md`
- `1319-salvage-readiness-contract-sheet-page-secret-escrow-database-continuity-and-recovery-lane-interface-spec.md`
- `1320-continuity-escrow-review-page-remove-readd-database-rebind-and-latent-salvage-loss-interface-spec.md`
- `1321-recovery-precondition-proof-page-rw-key-db-path-encrypted-node-and-stronger-claim-barrier-interface-spec.md`
- `1322-salvage-viability-timeline-page-key-retention-folder-removal-log-loss-and-source-failure-events-interface-spec.md`
- `1323-salvage-readiness-lineage-receipt-page-escrow-basis-continuity-proof-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `backup` can no longer hide the difference between ciphertext retention and actually provable future rescue
- encrypted disaster recovery now surfaces hidden preconditions before failure day instead of burying them in support prose
- remove / re-add / storage-root changes now warn when they silently sever salvage continuity even if bytes still look present
- later operators can open one receipt and see what secret escrow survived, whether continuity still holds, which recovery lane is real, and which stronger rescue sentence the product refused to make

## Revision addendum — claim quantifier, audience truth, and sufficiency-scope honesty after rev0361

This tranche locks the next seam around **claim quantifier truth**.
The key decisions now made explicit in the archive are:

- **claim quantifier is a first-class contract object rather than a side effect of plural nouns and peer counters**
- **self-only, any-source, all-connected, all-linked, all-remote-known, all-ever-approved, and historical-roster claims are different truths**
- **`one peer online` is weaker than `one source peer with the needed bytes online`, and `removed from linked devices` is weaker than `removed from every remote holder`**
- **`approved before` is weaker than `approved under this folder's current approval rule`**
- **every serious availability, approval, removal, or count sentence now needs one receipt that preserves subject set, audience set, sufficiency rule, horizon, evidence basis, and the blocked stronger sentence**

New docs added in this tranche:

- `1312-resilio-claim-quantifier-audience-and-sufficiency-fragmentation-evaluation.md`
- `1313-quantifier-contract-sheet-page-subject-set-audience-set-and-sufficiency-rule-interface-spec.md`
- `1314-audience-scope-review-page-self-only-linked-family-remote-peers-and-ever-approved-branches-interface-spec.md`
- `1315-sufficiency-proof-page-any-source-all-connected-all-linked-and-no-stronger-claim-interface-spec.md`
- `1316-quantifier-drift-timeline-page-approval-memory-roster-decay-and-source-loss-events-interface-spec.md`
- `1317-quantifier-lineage-receipt-page-claim-subject-sufficiency-basis-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `shared`, `approved`, `available`, and `removed` can no longer hide who exactly the claim is about
- a peer count can no longer masquerade as byte-holder sufficiency, approval scope, or trust scope
- `self`-derived local copies now stay visibly weaker than independent remote holders even when the row count grows
- later operators can open one receipt and see what subject set the sentence targeted, what threshold made it true, and which stronger quantifier sentence the product refused to make

## Revision addendum — action surface, witness locality, and recovery-scope truth after rev0360

This tranche locks the next seam around **action-surface truth**.
The key decisions now made explicit in the archive are:

- **execution surface, witness surface, and recovery surface are first-class contract objects rather than side effects of buttons or platform folklore**
- **desktop app, WebUI, mobile app, file browser / shell, service manager, config file, and browser/OS handoff are different locality classes**
- **`available somewhere in product` is weaker than `available on this current surface`, and `available on this current surface` is weaker than `recoverable on this current surface`**
- **out-of-band recovery is weaker than same-surface recovery even when it is the strongest honest path**
- **every serious action request now needs one receipt that preserves requested verb family, execution surface, witness surface, recovery surface, fallback class, semantic loss boundary, and the blocked stronger sentence**

New docs added in this tranche:

- `1306-resilio-action-surface-execution-witness-and-recovery-locality-fragmentation-evaluation.md`
- `1307-action-surface-contract-sheet-page-execution-surface-witness-surface-and-recovery-scope-interface-spec.md`
- `1308-surface-locality-review-page-desktop-webui-mobile-file-browser-and-os-handoff-branches-interface-spec.md`
- `1309-action-availability-proof-page-here-vs-elsewhere-vs-out-of-band-surface-capability-interface-spec.md`
- `1310-surface-shift-timeline-page-runtime-platform-and-fallback-lane-events-interface-spec.md`
- `1311-action-surface-lineage-receipt-page-requested-verb-active-surface-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `feature exists` can no longer hide whether the current surface can execute it, only inspect it, or only recover it out of band
- WebUI-default and service/headless seats now keep execution truth adjacent to recovery truth instead of making the operator infer both from missing affordances
- desktop-only, Android-only, iOS-open-app-only, and Linux-WebUI-ignored exceptions now stay visibly separate from generic `supported` language
- file-browser / shell / service-manager steps now publish their semantic loss instead of masquerading as same-surface recovery
- later operators can open one receipt and see where the action truly lived, where it could be witnessed, what fallback changed the lane, and which stronger same-surface sentence the product refused to make

## Revision addendum — participant-unit truth, grouped-row granularity, and approval-scope honesty after rev0358

This tranche locks the next seam around **participant-unit truth**.
The key decisions now made explicit in the archive are:

- **participant unit is a first-class contract object rather than a side effect of `peer`, `user`, `device`, or `participant` language**
- **human-facing identity, certificate-bearing authority unit, linked-device family, individual device seat, grouped user row, visible device row, and historical roster memory are different truths**
- **`peer count` is weaker than `device-seat count`, `device-seat count` is weaker than `authority-unit count`, and `authority-unit count` is weaker than `permission-bearing participant count`**
- **device-name match is weaker than certificate continuity, and grouped-row continuity is weaker than approval-memory continuity**
- **every serious count, approval, permission, or disconnect sentence now needs one receipt that preserves participant-unit class, count basis, authority basis, regroup risk, and the blocked stronger sentence**

New docs added in this tranche:

- `1294-resilio-participant-unit-identity-device-and-peer-row-granularity-fragmentation-evaluation.md`
- `1295-participant-unit-contract-sheet-page-identity-family-device-seat-and-row-basis-interface-spec.md`
- `1296-peer-row-granularity-review-page-user-group-device-entry-and-count-truth-interface-spec.md`
- `1297-participant-authority-proof-page-certificate-fingerprint-device-label-and-approval-memory-basis-interface-spec.md`
- `1298-participant-granularity-timeline-page-link-regroup-rename-and-identity-regeneration-events-interface-spec.md`
- `1299-participant-unit-lineage-receipt-page-count-basis-authority-unit-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `peer` can no longer hide whether the product is speaking about a grouped identity, one device seat, a certificate-bearing authority unit, or merely a visible row
- participant counts now publish their unit basis instead of pretending that rows, devices, and approved authorities are the same thing
- approval language now stays attached to certificate continuity and family scope instead of drifting down to row labels or friendly names
- device rename and identity regeneration now stay visibly different because one is presentational drift while the other is authority replacement
- later operators can open one receipt and see what exactly was counted, approved, edited, or disconnected, what regrouping assumptions were in play, and which stronger participant sentence the product refused to make

## Revision addendum — vendor ceiling, service-visible facts, and intervention-boundary truth after rev0357

This tranche locks the next seam around **vendor knowledge and intervention ceiling truth**.
The key decisions now made explicit in the archive are:

- **vendor ceiling is a first-class contract object rather than a side effect of `private`, `cloudless`, or `support` language**
- **tracker-visible metadata, relay ciphertext carriage, link-fragment opacity, landing-page counting, optional telemetry, explicit evidence-send, and direct vendor mutation authority are different truths**
- **`vendor cannot see files` is weaker than `no metadata left the device`, and `no metadata left the device` is weaker than `vendor has no meaningful service contact at all`**
- **`support can inspect sent logs` is weaker than `support can intervene in the live mesh`, and `vendor can run services` is weaker than `vendor can delete user-held copies`**
- **every serious privacy, takedown, or support-language claim now needs one receipt that preserves service-contact basis, disclosure widening, intervention boundary, and the blocked stronger sentence**

New docs added in this tranche:

- `1288-resilio-vendor-knowledge-intervention-and-service-contact-ceiling-fragmentation-evaluation.md`
- `1289-vendor-ceiling-contract-sheet-page-service-visible-facts-and-intervention-boundary-interface-spec.md`
- `1290-service-visible-facts-review-page-tracker-relay-landing-telemetry-and-support-send-interface-spec.md`
- `1291-intervention-authority-proof-page-link-fragment-local-control-and-vendor-noncontrol-interface-spec.md`
- `1292-vendor-contact-timeline-page-service-contact-disclosure-widening-and-evidence-send-events-interface-spec.md`
- `1293-vendor-ceiling-lineage-receipt-page-service-contact-disclosure-basis-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `private` can no longer hide whether tracker metadata, relay carriage, landing-page counting, telemetry, or user-sent diagnostics widened outside visibility
- vendor-side non-control is now explicit instead of implied by `P2P` marketing language
- support/send flows now keep evidence visibility adjacent to the still-absent power to revoke or delete already-held peer copies
- landing-page opacity for `#` fragments now stays attached to broader service-contact truth instead of pretending to settle the entire privacy story
- later operators can open one receipt and see what outside services were involved, what they could learn, what the vendor still could not do, and which stronger privacy or takedown sentence the product refused to make

## Revision addendum — admission instrument, approval memory, and credential afterlife after rev0354

This tranche locks the next seam around **admission instrument truth**.
The key decisions now made explicit in the archive are:

- **admission instrument is a first-class contract object rather than a side effect of `share`, `invite`, `link`, or `join`**
- **linked-identity automatic arrival, manual key admission, manual link admission, QR rendering, approval memory, certificate issuance, and key-lineage split are different truths**
- **`shared` is weaker than `join path exists`, `join path exists` is weaker than `durable credential issued`, and `durable credential issued` is weaker than `currently non-revoked`**
- **link expiry is weaker than access revocation, and local key rotation is weaker than cohort-wide migration**
- **every serious admission event now needs one receipt that preserves admission basis, gate class, issuance witness, afterlife limits, and the blocked stronger sentence**

New docs added in this tranche:

- `1270-resilio-admission-instrument-approval-memory-and-credential-afterlife-fragmentation-evaluation.md`
- `1271-admission-instrument-contract-sheet-page-key-link-qr-approval-and-certificate-basis-interface-spec.md`
- `1272-join-review-page-approval-requirement-link-expiry-use-count-and-existing-peer-memory-interface-spec.md`
- `1273-grant-issuance-proof-page-temporary-key-fingerprint-certificate-and-acl-basis-interface-spec.md`
- `1274-credential-afterlife-timeline-page-link-expiry-key-rotation-approval-memory-and-old-cohort-split-interface-spec.md`
- `1275-admission-instrument-lineage-receipt-page-join-basis-credential-class-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `share this` can no longer hide whether the operator sent a durable key, an expiring link, or only a QR rendering of one of those
- join review now surfaces approval bypass, remembered approval scope, time expiry, and use exhaustion before the operator learns them from surprising arrivals or failures
- grant proof now separates invitation receipt, request arrival, fingerprint review, certificate issuance, ACL install, and actual transfer eligibility instead of flattening them into `approved`
- key change review now keeps old-lineage survival adjacent to new-lineage issuance instead of implying that one peer rotation migrated the cohort
- later operators can open one receipt and see what admission path existed, when durable access was actually minted, what survived expiry or rotation, and which stronger sentence the product still refused to make

## Revision addendum — cohort census, live-set truth, and historical-roster semantics after rev0351

This tranche locks the next seam around **cohort census and participant-count truth**.
The key decisions now made explicit in the archive are:

- **cohort census is a first-class contract object rather than a side effect of one `X of Y peers` badge**
- **live-reachable set, historical roster, visible rows, source-capable subset, authority-capable subset, and self-derived local branches are different truths**
- **`online` is weaker than `source-capable`, and `source-capable` is weaker than `independent redundancy`**
- **hidden-for-declutter is weaker than removed, and disconnected gray row is weaker than severed membership absence**
- **every serious participant-count claim now needs one receipt that preserves counting basis, live/source split, independence class, residue rows, and the blocked stronger sentence**

New docs added in this tranche:

- `1252-resilio-cohort-census-live-set-historical-roster-and-source-capability-fragmentation-evaluation.md`
- `1253-cohort-census-contract-sheet-page-live-set-historical-roster-source-subset-and-row-visibility-interface-spec.md`
- `1254-roster-membership-review-page-ever-seen-online-disconnected-hidden-and-self-derived-branches-interface-spec.md`
- `1255-live-capability-proof-page-online-source-capable-authority-capable-and-serve-eligible-evidence-interface-spec.md`
- `1256-cohort-drift-timeline-page-live-count-history-expiry-hide-and-reentry-triggers-interface-spec.md`
- `1257-cohort-census-lineage-receipt-page-live-set-roster-basis-and-capability-ceiling-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `3 of 7 peers` can no longer hide whether the `7` are live, merely ever-seen, disconnected gray rows, hidden devices, or self-derived local fanout
- roster review now keeps auto-returning hidden rows adjacent to the live set instead of letting declutter masquerade as severance
- source-coverage review now separates `reachable`, `source-capable`, and `independent resilience` instead of deriving all three from one count
- local-share fanout can no longer silently inflate redundancy claims
- later operators can open one receipt and see what the cohort count actually meant here, who could really help now, what rows were only history or visibility residue, and which stronger resilience sentence the product still refused to make

## Revision addendum — detachment, revocation, roster residue, and installation afterlife after rev0350

This tranche locks the next seam around **detachment and revocation truth**.
The key decisions now made explicit in the archive are:

- **detachment and revocation are first-class contract objects rather than scattered button labels**
- **hide-record, disconnect-local, revoke-selected-peer, remove-linked-family, unlink-seat, and uninstall-runtime are different truths**
- **future-update cutoff is weaker than byte retraction, and byte retraction is weaker than ecosystem disappearance**
- **roster cleanup is weaker than trust severance, and trust severance is weaker than remote survivor absence**
- **every serious detachment action needs one receipt that preserves authority basis, propagation boundary, byte/roster/storage residue, reappearance triggers, and the blocked stronger sentence**

New docs added in this tranche:

- `1246-resilio-detachment-revocation-roster-residue-and-visibility-fragmentation-evaluation.md`
- `1247-detachment-and-revocation-contract-sheet-page-action-class-authority-scope-and-residue-interface-spec.md`
- `1248-offline-roster-visibility-review-page-hide-clear-reappear-and-observation-ceiling-interface-spec.md`
- `1249-access-revocation-proof-page-disconnect-unlink-remove-and-future-update-boundary-interface-spec.md`
- `1250-installation-clearance-review-page-uninstall-storage-residue-and-peer-record-afterlife-interface-spec.md`
- `1251-detachment-lineage-receipt-page-action-authority-residue-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `hide`, `disconnect`, `remove`, `unlink`, and `uninstall` can no longer hide the difference between decluttering, revocation, and real severance
- roster review now surfaces when a record can reappear without a new grant instead of pretending that visual absence proves relationship absence
- revocation review now publishes the boundary between future-flow cutoff and already-landed bytes that remain outside the action
- uninstall review now keeps program removal, storage residue, archive residue, and stale peer records adjacent instead of scattering them across host and support prose
- later operators can open one receipt and see who acted, what boundary the action actually touched, what survived, and which stronger cleanup sentence the product still refused to make

## Revision addendum — reachability provenance, discovery route, and infrastructure exposure truth after rev0349

This tranche locks the next seam around **reachability provenance and transport-exposure truth**.
The key decisions now made explicit in the archive are:

- **reachability provenance is a first-class product state rather than a side effect of `connected`, `offline`, or `relay` badges**
- **discovery basis, current transport route, infrastructure exposure, and policy allowance are different truths**
- **tracker introduction, LAN discovery, predefined-host dialout, mixed discovery, and no-current-witness are different origin classes**
- **direct route is weaker than privacy isolation proof, and relay encryption is weaker than no-third-party carriage**
- **every serious connectivity event now needs one receipt that preserves discovery basis, route witness, service-contact exposure, fallback ladder, and the blocked stronger sentence**

New docs added in this tranche:

- `1240-resilio-reachability-provenance-discovery-route-relay-fallback-and-infrastructure-exposure-fragmentation-evaluation.md`
- `1241-reachability-provenance-contract-sheet-page-discovery-basis-current-route-and-service-contact-exposure-interface-spec.md`
- `1242-discovery-path-review-page-tracker-lan-predefined-host-and-no-bootstrap-branches-interface-spec.md`
- `1243-transport-route-proof-page-direct-lan-direct-wan-relay-and-route-switch-evidence-interface-spec.md`
- `1244-service-contact-exposure-review-page-bootstrap-tracker-relay-and-link-landing-disclosure-interface-spec.md`
- `1245-reachability-lineage-receipt-page-discovery-basis-route-witness-and-exposure-ceiling-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `connected` can no longer hide whether peers were introduced by tracker, LAN discovery, or predefined hosts
- `relay` can no longer hide the difference between encrypted third-party carriage and true peer-direct transport
- privacy review now keeps config bootstrap, tracker metadata disclosure, relay carriage, and link-landing indirection adjacent instead of scattering them across security and troubleshooting prose
- route switches now publish whether the system merely allowed direct transport or actually proved a direct lane at this moment
- later operators can open one receipt and see how peers were found, how bytes were routed, what outside infrastructure was contacted, and what stronger sentence was still blocked

## Revision addendum — operator attestation, certainty override, and destructive assumption truth after rev0348

This tranche locks the next seam around **operator attestation and reviewed human certainty**.
The key decisions now made explicit in the archive are:

- **operator attestation is first-class product state rather than a side effect of `Ignore`, `Proceed`, `OK`, `touch`, or `recreate` advice**
- **warning dismissal, local-newest assertion, same-tree reconnect assertion, archive-reviewed destructive approval, and risky merge acceptance are different assertion classes**
- **human evidence basis, missing machine proof, blast radius, and expiry must be published together**
- **visibility change is weaker than world truth, and reviewed necessity is weaker than preserved continuity proof**
- **every serious human-certainty event now needs one receipt that preserves assertion class, evidence reviewed, expiry basis, blast radius, and the blocked stronger sentence**

New docs added in this tranche:

- `1234-resilio-operator-attestation-certainty-override-ignore-proceed-and-destructive-assumption-fragmentation-evaluation.md`
- `1235-operator-attestation-contract-sheet-page-assertion-class-evidence-basis-blast-radius-and-expiry-interface-spec.md`
- `1236-local-truth-assertion-review-page-ghost-warning-reconnect-same-path-and-prepopulated-tree-branches-interface-spec.md`
- `1237-destructive-assumption-proof-page-archive-reviewed-overwrite-risk-and-successor-epoch-commit-interface-spec.md`
- `1238-attestation-expiry-timeline-page-peer-return-rescan-new-evidence-and-reopen-triggers-interface-spec.md`
- `1239-operator-attestation-lineage-receipt-page-assertion-basis-scope-expiry-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `Ignore All` can no longer hide whether the operator only changed visibility or supplied a stronger claim about world absence
- `touch these files if you are certain` can no longer hide which certainty was supplied, what evidence backed it, and when that certainty expires
- `just proceed` on reconnect or pre-populated targets can no longer hide whether the branch is same-tree reconnect or overwrite-capable risky merge
- `make sure Archive has nothing important` can no longer stay private human memory before destructive recreate
- later operators can open one receipt and see what the human asserted here, why the product accepted that assertion, what remained unproved, and what stronger sentence was still blocked

## Revision addendum — effect provenance, surprising-state origin, and detection-induction truth after rev0347

This tranche locks the next seam around **effect provenance and state-origin truth**.
The key decisions now made explicit in the archive are:

- **effect provenance is first-class product state rather than a side effect of whatever result happens to be visible now**
- **result class and origin class are different truths**
- **direct publish, derived cascade, automatic source-heal, encrypted hard-wire, manual archive replay, and detection induction are separate origin classes**
- **detection induction is weaker than content authorship, and restored/reverted is weaker than manual recovery proof**
- **every serious surprising-state event now needs one receipt that preserves result class, origin class, actor basis, mechanism class, and the blocked stronger sentence**

New docs added in this tranche:

- `1228-resilio-effect-provenance-auto-heal-inheritance-archive-replay-and-touch-fragmentation-evaluation.md`
- `1229-effect-provenance-contract-sheet-page-result-class-origin-class-actor-basis-and-mechanism-interface-spec.md`
- `1230-surprising-state-review-page-remote-write-local-touch-auto-heal-and-manual-replay-branches-interface-spec.md`
- `1231-state-origin-proof-page-direct-publish-derived-cascade-hard-wire-and-manual-replay-evidence-interface-spec.md`
- `1232-effect-provenance-timeline-page-result-branch-switches-and-reopen-triggers-interface-spec.md`
- `1233-effect-provenance-lineage-receipt-page-origin-class-actor-basis-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `updated` can no longer hide whether the state came from direct publish, a source-heal, a derived cascade, a hard-wired seat rule, manual replay, or only re-detection after touch / mtime induction
- `reverted` and `restored` can no longer hide whether the cause was automatic runtime behavior or explicit operator replay
- parent-source inheritance and encrypted-seat hard-wiring now stay adjacent to surprising-state explanation instead of hiding in setup caveats
- detection-induction acts now stay separate from fresh-content authorship instead of being guessed from later visibility alone
- later operators can open one receipt and see what result was judged, what origin class won, who or what supplied that effect, and what stronger sentence was still blocked

## Revision addendum — effective seat posture, writeback authority, serve-right, and derived-seat truth after rev0346

This tranche locks the next seam around **effective seat posture and local-divergence fate**.
The key decisions now made explicit in the archive are:

- **grant label is first-class but insufficient; effective seat posture is the real contract object**
- **writeback authority, onward-share authority, byte-serve eligibility, and local-divergence fate are different truths**
- **`Read Only` is weaker than `cannot publish mutations`, and `cannot publish mutations` is weaker than `cannot contribute bytes`**
- **derived posture is first-class state: direct grant, linked-family default, local-share inheritance, encrypted hard-wire, or unresolved derivation**
- **every serious narrow-seat or posture dispute now needs one receipt that preserves grant label, derivation basis, local-change fate, serve ceiling, and the blocked stronger sentence**

New docs added in this tranche:

- `1222-resilio-effective-seat-posture-writeback-heal-serve-and-derivation-fragmentation-evaluation.md`
- `1223-effective-seat-posture-contract-sheet-page-grant-label-writeback-authority-serve-right-and-local-change-fate-interface-spec.md`
- `1224-narrow-seat-mutation-review-page-suspension-auto-heal-local-only-additions-and-selective-sync-ceiling-interface-spec.md`
- `1225-delegation-and-serve-proof-page-onward-share-authority-unmodified-byte-serving-and-peer-cascade-ceiling-interface-spec.md`
- `1226-derived-seat-review-page-linked-owner-default-local-share-inheritance-encrypted-hardwire-and-reshare-boundary-interface-spec.md`
- `1227-effective-seat-posture-lineage-receipt-page-derived-basis-local-change-fate-and-serve-ceiling-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `read only` can no longer hide whether local edits suspend, auto-heal, or survive as unsynced local-only residue
- `owner` can no longer hide whether the posture was directly granted or merely inherited from one linked identity family
- byte-serving can now stay distinct from writeback authority instead of being guessed from the permission label
- local-share inheritance and encrypted-node hard-wiring now stay adjacent to capability claims instead of hiding in separate setup articles
- later operators can open one receipt and see what this seat really could do, how a local change would fare, why the posture existed, and what stronger sentence was still blocked

## Revision addendum — subject scope, ignore divergence, namespace role, and unsupported-name ceiling after rev0345

This tranche locks the next seam around **subject scope and namespace-role truth**.
The key decisions now made explicit in the archive are:

- **subject scope is first-class per-peer product state rather than a side effect of file visibility and troubleshooting**
- **ordinary user subject, peer-excluded subject, UI-hidden subject, service-critical artifact, metadata-sidecar artifact, transfer-temp residue, and invalid-name-blocked subject are different namespace roles**
- **visible is weaker than indexed, indexed is weaker than counted, and counted is weaker than replicated**
- **`ignored now` is weaker than `never announced`, and `never announced` is weaker than `purged from every peer view`**
- **every serious exclusion or odd-pathname event now needs one receipt that preserves namespace role, peer-scope basis, retroactivity class, manipulation safety, and the blocked stronger sentence**

New docs added in this tranche:

- `1216-resilio-subject-scope-ignore-divergence-namespace-role-and-unsupported-name-fragmentation-evaluation.md`
- `1217-subject-scope-contract-sheet-page-visibility-indexing-counting-and-namespace-role-interface-spec.md`
- `1218-ignore-divergence-review-page-peer-local-rules-retroactivity-and-size-mismatch-interface-spec.md`
- `1219-namespace-role-review-page-hidden-service-artifacts-streams-and-temp-residue-interface-spec.md`
- `1220-scope-proof-page-visible-indexed-counted-replicated-and-exclusion-basis-interface-spec.md`
- `1221-subject-scope-lineage-receipt-page-peer-scope-namespace-role-and-exclusion-basis-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `ignored` can no longer hide whether the pathname is peer-excluded, service-owned, temp residue, metadata-sidecar state, or invalid-name-blocked
- `hidden` can no longer hide whether the path is merely absent from the UI or actually out of scope
- share-size mismatches can now stay adjacent to peer-local ignore divergence instead of hiding in docs footnotes
- `.sync`, `Streams`, and `.!sync` objects now publish namespace role and delete safety before operators damage them out of guesswork
- later operators can open one receipt and see what role the pathname had here, whether exclusion was retroactive or local only, what safety ceiling applied, and what stronger sentence was still blocked

## Revision addendum — change witness, writer pressure, observation debt, and timestamp-authority downgrade after rev0343

This tranche locks the next seam around **change evidence and publication honesty**.
The key decisions now made explicit in the archive are:

- **change witness is first-class product state rather than a side effect of notifications, rescans, and support rituals**
- **live watcher observation, rescan rediscovery, manual touch induction, quiescence hold, lock blockade, and database-only timestamp authority are different truths**
- **waiting is weaker than quiescence hold, quiescence hold is different from lock blockade, and both are different from observation uncertainty**
- **disk-visible mtime is weaker than authoritative product time, and authoritative product time is weaker than chronology certainty**
- **every serious detection or publication-delay event now needs one receipt that preserves witness class, hold/block basis, timestamp authority, and the blocked stronger sentence**

New docs added in this tranche:

- `1204-resilio-change-witness-lock-blockade-watcher-exhaustion-and-mtime-write-downgrade-fragmentation-evaluation.md`
- `1205-change-witness-contract-sheet-page-live-event-rescan-discovery-quiescence-hold-and-timestamp-authority-interface-spec.md`
- `1206-writer-pressure-review-page-delay-profile-lock-blockade-recheck-cadence-and-safe-publish-threshold-interface-spec.md`
- `1207-observation-proof-page-watcher-health-rescan-debt-manual-touch-and-change-seen-confidence-interface-spec.md`
- `1208-timestamp-authority-downgrade-review-page-disk-mtime-write-failure-database-truth-and-row-honesty-interface-spec.md`
- `1209-change-witness-lineage-receipt-page-detection-basis-hold-block-class-and-timestamp-authority-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `updated` can no longer hide whether the product saw the edit live, rediscovered it later, or only noticed it after manual induction
- `waiting` can no longer hide whether the product is intentionally buffering a writer, blocked by a lock, or simply missing observation certainty
- disk `Date modified` can no longer masquerade as the whole truth when authoritative timestamp state may already have diverged
- watcher exhaustion, rescan debt, delay profiles, and lock retries now stay adjacent to change claims instead of hiding in warnings and troubleshooting pages
- later operators can open one receipt and see how the change was observed, why publication waited, what time basis was in force, and what stronger sentence was still blocked

## Revision addendum — modification-time authority, offline winner, time-skew gate, and archive republish after rev0342

This tranche locks the next seam around **mutation chronology and rollback truth**.
The key decisions now made explicit in the archive are:

- **mutation chronology is first-class product state rather than a side effect of mtimes and archive folders**
- **online sequence, offline-return winner, time-skew refusal, manual touch remediation, and archive-based republish are different truths**
- **clock trust is weaker than time-authority proof, and time-authority proof is weaker than winner certainty**
- **archive presence is weaker than rollback authority, and rollback authority is weaker than convergence proof**
- **every serious conflict or rollback action now needs one receipt that preserves winner basis, time-certainty class, loser survivor map, and the blocked stronger sentence**

New docs added in this tranche:

- `1198-resilio-modification-time-authority-offline-winner-time-skew-gate-and-archive-republish-fragmentation-evaluation.md`
- `1199-mutation-chronology-contract-sheet-page-online-order-offline-winner-and-time-basis-interface-spec.md`
- `1200-concurrent-edit-review-page-online-sequence-offline-return-delay-mitigation-and-loser-placement-interface-spec.md`
- `1201-time-authority-proof-page-clock-zone-gmt-window-and-mtime-certainty-interface-spec.md`
- `1202-older-byte-republish-review-page-archive-restore-runtime-witness-and-touch-remediation-interface-spec.md`
- `1203-mutation-chronology-lineage-receipt-page-winner-basis-time-certainty-and-loser-survivor-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `newer` can no longer hide whether the verdict came from live chronology, offline-return precedence, repaired time authority, or a manual republish act
- time-skew gating, mtime trust, database fallback, and manual touch now stay adjacent to chronology claims instead of hiding in separate troubleshooting or preference pages
- archive restore can no longer masquerade as a completed rollback without runtime witness and republish proof
- future conflict mitigation now stays adjacent to conflict explanation instead of living as isolated tips prose
- later operators can open one receipt and see why this version won, how trustworthy the time basis was, where the losing bytes survived, and what stronger rollback sentence was still blocked

## Revision addendum — offer family, bearer capability, acceptance lane, and landing residue after rev0336

This tranche locks the next seam around **offer-family truth**.
The key decisions now made explicit in the archive are:

- **offer family is first-class product state rather than a cosmetic choice among link, key, QR, and send-file verbs**
- **approval posture, bearer openness, expiry authority, and usage-ceiling absence are different truths**
- **claim lane is weaker than claim success, and landing truth is weaker than cleanup proof**
- **desktop default landing, mobile fixed inboxes, collision suffixes, and row-vs-byte residue are separate contracts rather than afterthoughts**
- **every serious issuance or claim now needs one receipt that preserves artifact family, openness posture, acceptance lane, landing result, survivor boundary, and the blocked stronger sentence**

New docs added in this tranche:

- `1162-resilio-offer-family-bearer-capability-acceptance-lane-and-landing-residue-fragmentation-evaluation.md`
- `1163-offer-family-contract-sheet-page-key-link-qr-file-send-and-claim-governance-interface-spec.md`
- `1164-bearer-capability-review-page-approval-absence-expiry-usage-ceiling-and-fanout-interface-spec.md`
- `1165-acceptance-lane-review-page-browser-handoff-manual-paste-qr-and-webui-fallback-interface-spec.md`
- `1166-landing-residue-review-page-default-destination-collision-suffix-and-ui-byte-divergence-interface-spec.md`
- `1167-offer-family-lineage-receipt-page-artifact-family-claim-lane-and-landing-survivor-boundary-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `Share` can no longer hide whether the artifact is an approval-capable folder link, an approval-free key, or a bounded file-transfer offer
- `anyone with the link` can no longer masquerade as approval, privacy, or usage-bounded safety
- browser handoff, manual paste, QR claim, and WebUI manual entry can no longer collapse into one intake story
- destination defaults, `(1)` suffix collisions, and cleanup residue now stay adjacent to the claim instead of hiding in later troubleshooting
- later operators can open one receipt and see what was issued, how open it was, how it was claimed, where it landed, and what cleanup did not prove

## Revision addendum — diagnostic lane, self-serve support boundary, and evidence residue after rev0335

This tranche locks the next seam around **diagnostic-lane truth**.
The key decisions now made explicit in the archive are:

- **diagnostic lane is first-class product state rather than an advanced-settings afterthought**
- **anonymous metrics, debug capture, profiler traces, crash artifacts, staffed support, self-serve guidance, and cleanup residue are different truths**
- **capture family, outbound send, and cleanup closure are separate boundaries**
- **restart and hold-time are reviewed sufficiency gates rather than friendly tips**
- **every serious diagnostic act needs one receipt that preserves capture family, support lane, send route, residue boundary, and the blocked stronger sentence**

New docs added in this tranche:

- `1156-resilio-diagnostic-lane-activation-self-serve-support-and-evidence-residue-fragmentation-evaluation.md`
- `1157-diagnostic-lane-contract-sheet-page-capture-family-support-lane-and-residue-ceiling-interface-spec.md`
- `1158-debug-capture-review-page-activation-restart-window-and-log-rotation-cost-interface-spec.md`
- `1159-crash-and-profiler-custody-page-artifact-class-locality-and-send-lane-interface-spec.md`
- `1160-external-support-lane-proof-page-business-support-self-serve-redaction-and-send-readiness-interface-spec.md`
- `1161-diagnostic-lane-lineage-receipt-page-capture-family-send-path-and-residue-boundary-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `Enable debug logging` can no longer hide the difference between anonymous metrics, debug logs, profiler traces, and crash artifacts
- support entitlement now publishes the difference between staffed vendor lanes, self-serve/community lanes, and billing/licensing forms instead of implying one generic `Contact support` outcome
- sufficiency now stays attached to restart and hold-time, not just to the existence of a send button
- later operators can open one receipt and see what was collected, who could receive it, and what local residue remained after send or cleanup

## Revision addendum — entitlement topology, owner transfer, and line-split migration after rev0333

This tranche locks the next seam around **commercial entitlement topology and line-family truth**.
The key decisions now made explicit in the archive are:

- **licensed, linked-under-owner, borrowed-seat, family-shared, and non-commercial self-activation are different entitlement topologies**
- **owner transfer is a governance mutation, not a harmless `apply key` action**
- **borrowed seats publish dependency on owner approval, owner expiry, and reclaim authority instead of pretending to be self-owned**
- **byte compatibility is weaker than linked-cohort migration safety, and linked-cohort migration safety is weaker than line-supported upgrade**
- **every serious entitlement mutation needs one receipt that preserves owner identity, seat class, line family, survivor boundary, and blocked stronger sentence**

New docs added in this tranche:

- `1144-resilio-entitlement-topology-owner-transfer-seat-loan-and-line-split-fragmentation-evaluation.md`
- `1145-entitlement-topology-contract-sheet-page-owner-user-linked-identity-and-line-compatibility-interface-spec.md`
- `1146-license-owner-transfer-review-page-direct-apply-theft-linked-owner-and-seat-survivor-interface-spec.md`
- `1147-seat-loan-and-reclaim-review-page-unique-identity-budget-approval-and-owner-expiry-cascade-interface-spec.md`
- `1148-line-split-migration-watch-page-v2-v3-linked-cohort-conflict-and-business-block-interface-spec.md`
- `1149-entitlement-topology-lineage-receipt-page-owner-seat-class-line-family-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `licensed` no longer stands in for owner topology, borrower dependence, or upgrade safety
- direct key application that can move Business ownership can no longer masquerade as ordinary activation
- counted budget now stays visibly tied to unique identity vs device count before approval or reclaim
- v2↔v3 byte compatibility can no longer overclaim safe linked-cohort migration
- later operators can open one receipt and see who owned the entitlement graph, who was borrowing, what line family mattered, and why stronger safety language was blocked

## Revision addendum — archive witness, restore authority, and retention survivor map after rev0331

This tranche locks the next seam around **archive witness and restore-authority truth**.
The key decisions now made explicit in the archive are:

- **archived-byte witness is weaker than restore authority, and restore authority is weaker than backup-class safety**
- **remote-change provenance, local-trash expectation, manual resurrection, retention TTL, version-size ceiling, and platform visibility are different classes rather than one `Archive` feature**
- **runtime-live restore is stronger than copied-bytes-on-disk, and copied-bytes-on-disk is stronger than authoritative republish**
- **encrypted-seat archive visibility is weaker than recoverability because bytes may be present while publication authority is absent**
- **every serious archive action needs one receipt that preserves provenance, authority class, retention/visibility limits, survivor map, and blocked stronger sentence**

New docs added in this tranche:

- `1132-resilio-archive-witness-restore-authority-and-retention-survivor-fragmentation-evaluation.md`
- `1133-archive-contract-sheet-page-version-witness-restore-authority-and-retention-class-interface-spec.md`
- `1134-archive-restore-review-page-manual-resurrection-runtime-witness-and-source-authority-interface-spec.md`
- `1135-archive-retention-and-platform-visibility-page-ttl-size-cap-mobile-visibility-and-sd-card-boundary-interface-spec.md`
- `1136-archive-salvage-proof-page-remote-change-origin-encrypted-seat-limit-and-survivor-map-interface-spec.md`
- `1137-archive-lineage-receipt-page-version-origin-restore-authority-retention-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `found in Archive` no longer stands in for recoverable, publishable, or durable
- restore now separates manual byte resurrection, runtime witness, and authority to republish
- retention and visibility cliffs now stay adjacent to recovery claims instead of hiding in preferences or platform caveats
- encrypted/archive-bearing seats now publish their recovery ceiling before operators over-trust them
- later operators can open one receipt and see what archived bytes proved, what they did not prove, and why stronger backup/recovery language was blocked

## Revision addendum — path liveness, remount witness, and rebind ceiling after rev0329

This tranche locks the next seam around **path liveness and rebind-class truth**.
The key decisions now made explicit in the archive are:

- **path liveness is weaker than subject continuity, and subject continuity is weaker than peer-continuity preservation**
- **same-root move, cross-root rehome, returned removable root, self-edge external targeting, and fresh bind are different classes rather than one `fix path` action**
- **path spelling is weaker than root witness, and root witness is weaker than same-subject proof**
- **reconnect suggestion is weaker than safe rebind, and safe rebind is weaker than zero-reconnect-cost continuity**
- **every serious missing-path event needs one receipt that preserves loss-cause hypothesis, returned-root witness, repair rung, reconnect cost, and blocked stronger sentence**

New docs added in this tranche:

- `1120-resilio-path-liveness-remount-witness-and-rebind-ceiling-fragmentation-evaluation.md`
- `1121-path-liveness-contract-sheet-page-live-bind-missing-root-and-rebind-class-interface-spec.md`
- `1122-missing-path-review-page-moved-deleted-remounted-and-trash-return-branches-interface-spec.md`
- `1123-remount-and-external-media-review-page-removable-root-witness-drive-class-and-safe-resume-interface-spec.md`
- `1124-rebind-proof-page-same-subject-old-root-new-root-and-reconnect-cost-interface-spec.md`
- `1125-path-liveness-lineage-receipt-page-loss-cause-root-return-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `path missing` no longer stands in for delete, move, remount, or fresh bind
- reconnect proposals and `(1)` sibling creation can no longer masquerade as continuity proof
- returned removable roots now publish witness strength before resume
- same-computer internal→external targeting now stays visibly separate from ordinary rehome language
- later operators can open one receipt and see why a repaired path was treated as same subject, fresh bind, or derivative instead of reverse-engineering the branch from support rituals

## Revision addendum — transfer eligibility, pause semantics, and context gating after rev0328

This tranche locks the next seam around **transfer eligibility and context-gated movement truth**.
The key decisions now made explicit in the archive are:

- **transfer eligibility is a first-class contract object**
- **payload movement, local detection, deletion propagation, zero-byte propagation, indexing, peer visibility, publish delay, and queue precedence are different lanes or modifiers**
- **pause, scheduled-zero, auto-sleep, battery stop, mobile-data block, delay-held, and priority-deferred are typed states rather than one badge family**
- **policy gates and context gates remain separate, and `eligible` is weaker than `immediate`, while `immediate` is weaker than `first in queue`**
- **every serious eligibility mutation needs one receipt that preserves gates, lane truth, timing modifiers, wake trigger, and blocked stronger sentence**

New docs added in this tranche:

- `1114-resilio-transfer-eligibility-pause-schedule-and-context-gating-fragmentation-evaluation.md`
- `1115-transfer-eligibility-contract-sheet-page-policy-context-and-lane-truth-interface-spec.md`
- `1116-mobility-and-power-budget-review-page-mobile-data-network-battery-priority-and-schedule-delta-interface-spec.md`
- `1117-paused-but-still-mutating-page-delete-propagation-indexing-and-visibility-truth-interface-spec.md`
- `1118-transfer-eligibility-proof-page-current-gate-basis-next-wake-and-why-not-moving-interface-spec.md`
- `1119-eligibility-boundary-receipt-page-policy-context-proof-and-resume-trigger-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `paused` is no longer allowed to hide whether deletions, zero-byte markers, rescans, or indexing still happen
- transfer policy, current context, wake cadence, and queue/timing modifiers now live in one eligibility family instead of scattered settings pages
- `not moving now` now separates `blocked`, `sleeping`, `waiting for context`, `delay-held`, and `deprioritized in queue`
- later operators can open one receipt and see why bytes were not moving, what still mutated anyway, and what event would change the answer

## Revision addendum — placeholder materialization, pin truth, and source-byte witness after rev0327

This tranche locks the next seam around **placeholder materialization and source-byte witness truth**.
The key decisions now made explicit in the archive are:

- **visible placeholder, hydrated local copy, pinned residency, subtree future-arrival commitment, and fully-synced share are different materialization classes**
- **remove-from-device, revert-to-placeholder, remove-share, and delete-everywhere are different intents with different survivor maps**
- **placeholder visibility is weaker than source-byte witness, and source-byte witness is weaker than offline guarantee**
- **ghost-file risk must be surfaced as a first-class watch state rather than a late fetch surprise**
- **every serious materialization action needs one receipt that preserves class, local bytes, source witness, future-arrival commitment, and blocked stronger sentence**

New docs added in this tranche:

- `1108-resilio-placeholder-materialization-pin-truth-and-source-byte-witness-fragmentation-evaluation.md`
- `1109-materialization-contract-sheet-page-placeholder-hydrated-pinned-and-byte-witness-interface-spec.md`
- `1110-hydration-review-page-single-file-subtree-future-arrivals-and-fetch-ceiling-interface-spec.md`
- `1111-local-residency-review-page-remove-from-device-remove-from-all-and-placeholder-survivor-interface-spec.md`
- `1112-source-byte-witness-watch-page-ghost-file-risk-offline-guarantee-and-materialization-debt-interface-spec.md`
- `1113-materialization-lineage-receipt-page-visible-entry-local-bytes-and-source-witness-boundary-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `I can see it` is no longer allowed to collapse placeholder visibility, local bytes, or future offline readiness
- hydration now separates one-time fetch, ongoing local residency, and subtree future-arrival commitment
- local cleanup and mesh-wide deletion now publish separate survivor maps before commit
- ghost-file risk now sits adjacent to materialization review instead of living as troubleshooting folklore
- later operators can open one receipt and see what was visible, what bytes were local, who still witnessed source bytes, and what stronger availability sentence was blocked

## Revision addendum — maintenance health, repair rung, and salvage boundary after rev0326

This tranche locks the next seam around **maintenance health and repair rung truth**.
The key decisions now made explicit in the archive are:

- **busy work, degraded detection, blocked transfer, suspended subject, and destructive-rebuild recommendation are different health verdicts**
- **restart, reconnect-same-destination, re-add, sidecar recreation, and peer-wide re-share are different repair rungs**
- **archive/history review, partial-download residue, and evidence capture must appear before destructive repair steps**
- **warning cleared is weaker than health proven, and resumed transfer is weaker than restored live observation**
- **every serious health action needs one receipt that preserves warning basis, chosen repair rung, survivor/loss boundary, and the blocked stronger sentence**

New docs added in this tranche:

- `1102-resilio-maintenance-health-warning-repair-rung-and-salvage-boundary-fragmentation-evaluation.md`
- `1103-health-warning-contract-sheet-page-pressure-lock-spine-and-repair-class-interface-spec.md`
- `1104-health-triage-review-page-busy-recovering-rescan-only-suspended-and-corrupt-verdict-interface-spec.md`
- `1105-repair-rung-review-page-restart-reconnect-readd-and-salvage-boundary-interface-spec.md`
- `1106-health-proof-page-recovered-degraded-rescan-only-and-support-escalation-ceiling-interface-spec.md`
- `1107-health-lineage-receipt-page-warning-basis-repair-rung-and-state-loss-boundary-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `not syncing` is no longer allowed to collapse slowdown, degraded detection, lock contention, folder suspension, and destructive rebuild into one vague symptom
- repair flows now publish rung strength, survivor map, and salvage duty before letting the operator cross a state-loss boundary
- health proof now separates `warning gone`, `transfer resumed`, `live observation restored`, and `escalate with evidence`
- later operators can open one receipt and see why a destructive or non-destructive rung was chosen and what stronger `fixed` sentence was still blocked

## Revision addendum — self-edge derivation, source-coupled lifecycle, and entitlement cliffs after rev0324

This tranche locks the next seam around **same-host self-edge derivation**.
The key decisions now made explicit in the archive are:

- **same-host self-edge is its own topology class, not just another share or another path**
- **self-only route posture and discovery-bypassed semantics are different truths from ordinary peer connectivity**
- **rights inheritance is a ceiling below the source, not delegated equality**
- **source disconnect/remove, source return, placeholder scarcity, and license expiry are first-class continuity facts for the derivative**
- **every self-edge action needs one receipt that preserves topology verdict, rights ceiling, source-coupled teardown, byte-witness posture, and suspension boundary**

New docs added in this tranche:

- `1090-resilio-self-edge-local-derivation-loop-rights-and-license-cliff-evaluation.md`
- `1091-self-edge-derivation-contract-sheet-page-source-self-peer-loop-ceiling-and-lifecycle-coupling-interface-spec.md`
- `1092-self-edge-topology-review-page-parent-child-loop-ban-and-fanout-boundary-interface-spec.md`
- `1093-derived-rights-and-lifecycle-review-page-owner-ceiling-source-downgrade-and-reattach-requirement-interface-spec.md`
- `1094-self-edge-materialization-and-entitlement-watch-page-placeholder-dependence-discovery-bypass-and-license-cliff-interface-spec.md`
- `1095-self-edge-lineage-receipt-page-source-target-self-peer-and-suspension-boundary-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `sync local folders` is no longer allowed to hide self-edge topology, route class, or loop risk
- derivative rights now publish ceiling, downgrade cascade, and re-share boundaries instead of sounding like ordinary share editing
- source return can no longer impersonate derivative auto-heal when manual reattach is still required
- independent Selective Sync controls can no longer overclaim independent byte availability
- later operators can open one receipt and see why a derivative existed, why it stopped, and what proof would justify restoring it

## Revision addendum — portable-name truth, canonical collision, and name-plane propagation after rev0323

This tranche locks the next seam around **portable-name truth and propagation scope**.
The key decisions now made explicit in the archive are:

- **path existence is weaker than portable-name admissibility**
- **canonical portable name, disk basename, presented title, artifact label, and peer-visible alias are different name planes**
- **local-only rename scope must be explicit before commit**
- **byte reuse and rename scope are different truths**
- **every serious naming action needs one receipt that preserves canonicalization delta, plane delta, scope/byte-reuse delta, and the blocked stronger sentence**

New docs added in this tranche:

- `1084-resilio-portable-name-collision-alias-propagation-and-move-scope-fragmentation-evaluation.md`
- `1085-portable-name-contract-sheet-page-canonical-collision-alias-planes-and-propagation-scope-interface-spec.md`
- `1086-canonical-name-portability-review-page-case-encoding-invalid-symbol-and-path-budget-interface-spec.md`
- `1087-name-plane-propagation-review-page-disk-name-ui-label-offer-alias-and-local-only-rename-interface-spec.md`
- `1088-rename-scope-and-byte-reuse-proof-page-local-path-move-archive-assisted-remote-reuse-and-symlink-boundary-interface-spec.md`
- `1089-portable-name-lineage-receipt-page-canonicalization-alias-plane-delta-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `name` now decomposes into canonical portability, plane, audience, and byte-reuse scope
- case/encoding/path-limit failures become reviewed portability classes instead of conflict-file archaeology
- local-only disk rename and cosmetic title change can no longer masquerade as the same action
- alias-edge boundary warnings now sit adjacent to move/rename proof instead of support folklore
- later operators can open one receipt and see what portable rendering was adopted, who saw the change, and what stronger propagation sentence was blocked

## Revision addendum — host integration, signer trust, shell activation, and uninstall clearance after rev0322

This tranche locks the next seam around **host integration and clearance truth**.
The key decisions now made explicit in the archive are:

- **host integration is not the same as program presence**
- **signer trust, OS consent, shell-surface activation, and uninstall clearance are different truths**
- **successful installer launch is weaker than accepted host mutation, and accepted host mutation is weaker than proven shell-surface activation**
- **program removal is weaker than clearance, and clearance is weaker than subject-data erasure**
- **every host-integration change needs a receipt that preserves trust prompts crossed, shell surfaces touched, survivors left behind, and the blocked stronger sentence**

New docs added in this tranche:

- `1078-resilio-host-integration-signer-trust-shell-activation-and-uninstall-clearance-fragmentation-evaluation.md`
- `1079-host-integration-contract-sheet-page-installer-trust-os-consent-shell-surfaces-and-clearance-state-interface-spec.md`
- `1080-installer-trust-review-page-codesign-reputation-uac-consent-and-host-mutation-scope-interface-spec.md`
- `1081-shell-surface-activation-proof-page-finder-explorer-extension-state-filesystem-eligibility-and-registration-truth-interface-spec.md`
- `1082-uninstall-clearance-review-page-program-removal-settings-residue-shell-release-and-shared-data-survivor-interface-spec.md`
- `1083-host-integration-lineage-receipt-page-trust-prompts-shell-surface-state-and-clearance-ceiling-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `installed` now decomposes into signer trust, OS consent, host mutation scope, and shell proof state
- Finder/Explorer affordances are reviewed as host-activation proof instead of support folklore
- `uninstall` is no longer allowed to hide the difference between binary removal, settings clearance, shell-hook release, and data/archive survivors
- later operators can open one receipt and see which trust prompts were crossed and which stronger removal or integration sentence was blocked

## Revision addendum — automatic ingress mutation, port lease, and router side-effects after rev0321

This tranche locks the next seam around **automatic ingress mutation and port-lease truth**.
The key decisions now made explicit in the archive are:

- **automatic port mapping is router mutation, not a harmless performance toggle**
- **local listener choice and externally reachable lease are different truths**
- **fixed-vs-random listening port is continuity-bearing whenever forwarding or known-host guidance depends on it**
- **mapping success is weaker than directness proof, and both are weaker than stable ingress continuity**
- **every ingress-widening action needs a receipt with attempted mutation, requested audience, proof ceiling, and blocked stronger sentence**

New docs added in this tranche:

- `1072-resilio-automatic-ingress-mutation-port-lease-and-router-side-effect-fragmentation-evaluation.md`
- `1073-ingress-exposure-contract-sheet-page-listening-port-map-authority-and-lease-truth-interface-spec.md`
- `1074-port-mapping-review-page-random-vs-fixed-port-upnp-lease-and-manual-forward-mismatch-interface-spec.md`
- `1075-router-side-effect-warning-page-upnp-nat-pmp-device-fragility-and-rollback-boundary-interface-spec.md`
- `1076-directness-proof-page-open-listener-mapped-ingress-and-relay-fallback-ceiling-interface-spec.md`
- `1077-ingress-lineage-receipt-page-listener-continuity-mutation-attempt-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `open direct connectivity` now decomposes into listener choice, router mutation authority, audience widening, and proof ceiling
- random port assignment is no longer allowed to hide inside convenience language when external rules depend on it
- directness proof is now modeled as a ladder rather than a single green state
- later operators can open one receipt and see whether the runtime merely changed a local listener or also requested off-host ingress mutation

## Revision addendum — same-host multi-instance namespace, path ownership, and external-world handoff after rev0320

This tranche locks the next seam around **same-host multi-instance bringup**.
The key decisions now made explicit in the archive are:

- **same-host multi-instance is a namespace contract, not a power-user convenience**
- **listener separation, storage-root separation, principal continuity, and subject-path ownership are different truths**
- **same-path claim on one host is exclusive until migrate / reattach / branch review says otherwise**
- **external or removable storage reuse across runtimes is an ownership handoff rather than a raw add-folder shortcut**
- **every blocked overlap needs a receipt that preserves the blocked stronger sentence**

New docs added in this tranche:

- `1066-resilio-same-host-multi-instance-port-namespace-storage-world-and-claim-collision-evaluation.md`
- `1067-instance-namespace-contract-sheet-page-runtime-identity-listener-storage-and-claim-ceiling-interface-spec.md`
- `1068-second-instance-bringup-review-page-port-separation-storage-root-identity-and-ui-audience-interface-spec.md`
- `1069-same-path-claim-collision-warning-page-hidden-state-corruption-and-branch-vs-reattach-interface-spec.md`
- `1070-shared-external-storage-review-page-removable-world-reuse-and-safe-ownership-handoff-interface-spec.md`
- `1071-instance-lineage-receipt-page-runtime-namespace-storage-root-subject-ownership-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- a second runtime is reviewed as a namespace with listener, storage, identity, and audience facts
- successful process start does not imply safe subject ownership
- removable media with continuity-bearing state cannot be reused without a typed handoff review
- later operators can open one receipt and see why `run both` or `reuse this path` was refused

## Revision addendum — directory admission, root ceiling, picker authority, and config-authored roster after rev0319

This tranche locks the next seam around **directory admission authority**.
The key decisions now made explicit in the archive are:

- **path existence is not path admissibility**
- **root ceiling and picker visibility are different truths**
- **config-authored subject import is roster-authority replacement**
- **subject-class support belongs in admission review, not in setup footnotes**
- **every denial needs a blocking-authority receipt**

New docs added in this tranche:

- `1060-resilio-directory-admission-root-ceiling-whitelist-and-config-authorship-fragmentation-evaluation.md`
- `1061-directory-admission-contract-sheet-page-path-admissibility-root-ceiling-and-authorship-basis-interface-spec.md`
- `1062-root-ceiling-review-page-directory-root-policy-descendant-only-creation-and-direct-root-denial-interface-spec.md`
- `1063-picker-visibility-authority-page-allowlisted-browse-surfaces-hidden-paths-and-direct-entry-boundary-interface-spec.md`
- `1064-config-authored-subject-set-review-page-standard-only-folders-webui-suppression-and-roster-replacement-interface-spec.md`
- `1065-directory-admission-lineage-receipt-page-requested-path-verdict-blocking-authority-and-roster-authorship-delta-interface-spec.md`

What this tranche contributes to the larger doctrine:

- add-folder flows must compile into a reviewed authority object, not a raw picker
- browse surfaces must admit when they are filtered and when they are merely incomplete
- config-owned subject rosters must declare authorship replacement and mutation-surface narrowing before apply
- later operators must be able to read one receipt and know whether a path failed because of root ceiling, visibility authority, subject class, or roster authorship

## Latest addendum — pre-login launch class, group-write contract, and headless audience after rev0318

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **pre-login runtime contract sheet / headless launch review / group-write discipline proof / pre-login mode caveat page / pre-login lineage receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `what exactly changed when I made Sync run before login on a Mac?` depends on combining several articles:

- the current Mac pre-login article still says ordinary app start is tied to user login under the current user, while pre-login launch requires `launchd`, root permissions, and a dedicated runtime user
- that same article still flips `use_gui` to `false`, moves storage into the dedicated user's home, binds WebUI to `0.0.0.0:8888`, and uses `RunAtLoad`, `KeepAlive`, and `Umask 2`
- that same article still warns that new local files inside synced folders must preserve the reviewed group-write posture or Sync can stop syncing them
- that same article still adds a placeholder/selective-sync caveat through `"enable_placeholders": false`
- current WebUI docs still say app-install WebUI is config-driven, HTTP by default unless `force_https` is set, and that clicking a share link in WebUI does not work and must be replaced by manual `Enter a key or link`
- current background-behavior docs still say ordinary macOS background use can simply be the minimized app, which is materially different from pre-login launchd mode

So the tighter non-clone line is:

> borrow Resilio's candor that pre-login runtime, principal choice, storage home, file-creation discipline, control audience, and handler parity are materially different truths — but refuse any product contract where `run before login` still makes the operator merge setup recipe prose, WebUI notes, and background docs to know what world now exists.

That yields five more ordinary product-owned pages:

- **Pre-login runtime contract sheet**
- **Headless launch review**
- **Group-write discipline proof**
- **Pre-login mode caveat page**
- **Pre-login lineage receipt**

## Latest addendum — discovery bootstrap authority, fallback envelope, and relay inevitability after rev0317

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **bootstrap authority contract sheet / bootstrap outage review / egress-only reachability review / discovery fallback proof / bootstrap lineage receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `who currently defines discovery infrastructure, what fallback envelope remains, and for which peer pairs is relay inevitable?` depends on combining several articles:

- connectivity troubleshooting still saying Sync learns tracker and relay addresses from `config.resilio.com/sync.conf`
- ports/protocols docs still splitting the path across catalog fetch, tracker, direct peer dialing, relay, LAN multicast, and port mapping
- core warnings still saying `No tracker connection` only blocks sync if relay, LAN broadcasts, or predefined hosts are also unavailable
- preferences docs still saying proxies prohibit incoming connections and that two proxied peers can talk only via relay, while one proxied peer can still dial outward directly
- relay docs still saying relayed transfer is slower than direct transfer

So the tighter non-clone line is:

> borrow Resilio's candor that bootstrap authority, tracker/relay/LAN/manual lanes, cached continuity, and proxy asymmetry are materially different truths — but refuse any product contract where the operator still has to merge warning pages, preferences prose, troubleshooting, and architecture notes to know what discovery authority exists and whether relay is already inevitable.

That yields five more ordinary product-owned pages:

- **Bootstrap authority contract sheet**
- **Bootstrap outage review**
- **Egress-only reachability review**
- **Discovery fallback proof**
- **Bootstrap lineage receipt**

## Latest addendum — service promotion, principal switch, and service-world continuity after rev0316

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **service promotion contract sheet / principal switch review / service world preview / service cutover proof / service lineage receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `did I really background the same seat, or did I open a different principal/world and lose continuity?` can depend on:

- service-install docs still offering **migrate settings** versus **clean installation**
- those same docs still allowing the service to run as **current user**, **Local Service**, or **Local System**
- service-troubleshooting docs still saying mapped drive letters are unavailable to services because interactive logon did not occur
- those same troubleshooting docs still saying the UNC workaround loses immediate notifications so discovery falls back to **rescan** or **restart**
- the same article still saying a switch to **Local System** can show an empty-looking world because the service opened a different storage folder and now needs **re-add / re-share / reconnect**
- config-mode docs still saying service config only works from the **service storage folder**
- troubleshooting docs still saying service WebUI is **127.0.0.1** by default unless changed and restarted
- uninstall docs still publishing different service storage roots for local-user, LocalService, and LocalSystem service seats

So the tighter non-clone line is:

> borrow Resilio's candor that service install mode, principal choice, storage root, mapped-path reach, notification grade, and listener scope are materially different truths — but refuse any product contract where `run as service` still makes the operator merge install, troubleshooting, config, preference, and uninstall articles to know whether the same seat actually survived.

That yields five more ordinary product-owned pages:

- **Service promotion contract sheet**
- **Principal switch review**
- **Service world preview**
- **Service cutover proof**
- **Service lineage receipt**

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


## Revision addendum — stop proof, hidden runtime, and restart provenance after rev0325

This tranche locks the next seam around **runtime stop truth**.
The key decisions now made explicit in the archive are:

- **projection close, runtime stop, service stop, and future boot re-entry are different truths**
- **stop intent is weaker than drain completion, and drain completion is weaker than no-further-publication proof**
- **platform class matters because desktop hidden runtime, Windows service, Android exit, and iOS foreground-only runtime do not share one shutdown contract**
- **restart provenance is continuity-bearing because reopen / relaunch can change indexing and chronology claims**
- **every serious stop-adjacent action needs one receipt that preserves stop scope, proof rung, residuals, re-entry posture, and the blocked stronger sentence**

New docs added in this tranche:

- `1096-resilio-stop-proof-hidden-runtime-and-restart-provenance-fragmentation-evaluation.md`
- `1097-runtime-stop-contract-sheet-page-projection-runtime-boot-reentry-and-platform-class-interface-spec.md`
- `1098-shutdown-drain-review-page-stop-intent-residual-work-and-no-further-publication-proof-interface-spec.md`
- `1099-runtime-stop-proof-page-visible-state-service-state-and-platform-background-ceiling-interface-spec.md`
- `1100-restart-provenance-page-stop-source-reentry-trigger-and-chronology-risk-interface-spec.md`
- `1101-runtime-stop-lineage-receipt-page-stop-scope-proof-rung-and-reentry-posture-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `close` can no longer hide the difference between surface disappearance, runtime persistence, and supervisor-managed return
- stop UX now has an explicit proof ladder instead of one binary success story
- startup toggles now publish future re-entry truth rather than pretending to prove present stop
- later operators can open one receipt and see both what was stopped and what brought it back


## Revision addendum — non-authority convergence, empty-target purge, and forced source-heal after rev0330

This tranche locks the next seam around **non-authority convergence truth**.
The key decisions now made explicit in the archive are:

- **non-authority convergence is a first-class contract object rather than an accidental consequence of permissions**
- **seat class, posture origin, and runtime proof are different truths**
- **heal posture is weaker than survivor truth, because edits/deletes may heal while additions still remain local-only**
- **empty-target purge is a stronger destructive class than overwrite-heal and must never hide behind a default**
- **every serious non-authority action needs one receipt that preserves posture origin, purge/heal scope, survivor boundary, and the blocked stronger sentence**

New docs added in this tranche:

- `1126-resilio-non-authority-convergence-empty-target-purge-and-forced-source-heal-fragmentation-evaluation.md`
- `1127-non-authority-convergence-contract-sheet-page-seat-role-heal-posture-and-survivor-truth-interface-spec.md`
- `1128-read-only-divergence-review-page-suspension-heal-and-local-survivor-fate-interface-spec.md`
- `1129-empty-target-purge-review-page-delete-unknown-posture-bootstrap-assumption-and-preseeded-risk-interface-spec.md`
- `1130-forced-source-heal-proof-page-encrypted-hardwire-defaults-and-runtime-proof-ceiling-interface-spec.md`
- `1131-non-authority-convergence-lineage-receipt-page-seat-class-posture-origin-and-survivor-boundary-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `read only` can no longer hide the difference between suspension, overwrite-heal, local-only survivors, and purge-capable bootstrap
- inherited defaults and encrypted-seat hardwire now publish origin truth instead of pretending every destructive posture was consciously chosen now
- reuse of an allegedly empty target now gets a real destructive-review page instead of a buried power-user footnote
- later operators can open one receipt and see why a seat healed edits, preserved additions, or refused a stronger sentence about safe cleanup

## Revision addendum — identity graph adoption, certificate takeover, and containment reset after rev0332

This tranche locks the next seam around **identity-graph adoption truth**.
The key decisions now made explicit in the archive are:

- **linking devices is graph adoption, not neutral pairing**
- **certificate survival, display-name change, and share-roster replacement are different truths**
- **future auto-arrival mode, path authorship, and owner-default authority are different parts of linked-graph membership**
- **hide offline, unlink local, regenerate identity, and relicense are different containment classes**
- **every serious identity-graph action needs one receipt that preserves direction, survivor map, entitlement coupling, containment class, and the blocked stronger sentence**

New docs added in this tranche:

- `1138-resilio-identity-graph-adoption-certificate-takeover-and-containment-reset-fragmentation-evaluation.md`
- `1139-identity-graph-adoption-contract-sheet-page-certificate-graph-direction-and-entitlement-coupling-interface-spec.md`
- `1140-certificate-takeover-review-page-directionality-shares-replacement-and-storage-survivor-interface-spec.md`
- `1141-linked-graph-default-arrival-page-owner-posture-disconnected-mode-and-manual-ro-exception-interface-spec.md`
- `1142-identity-containment-reset-proof-page-compromised-seat-blast-radius-and-regeneration-interface-spec.md`
- `1143-identity-lineage-receipt-page-graph-direction-certificate-survivor-and-containment-class-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `link device` can no longer hide who adopts whom or which certificate survives
- linked-graph membership now publishes default arrival posture and owner-default rights instead of hiding them in `My Devices` folklore
- read-only exceptions now visibly branch out of the linked-device lane instead of pretending owner-default arrival can somehow become RO later
- compromised-seat response now has an explicit ladder from hide to unlink to full identity reset instead of one vague `disconnect the bad device` story

## Revision addendum — subject architecture family, governance domain, and migration ceiling after rev0334

This tranche locks the next seam around **subject architecture family truth**.
The key decisions now made explicit in the archive are:

- **subject architecture is governance, not cosmetics**
- **key-domain Standard, certificate-domain Advanced, and encrypted-derivative backup subjects are different families**
- **write power, re-share power, permission-mutation power, and encrypted seeding power are different truths**
- **linked owner-default arrival stays visibly separate from manual Standard-key exceptions**
- **architecture migration is a reviewed ceiling because in-place conversion, remove-and-readd replacement, and config-only family support are not the same reality**
- **every architecture-affecting action needs one receipt that preserves family, authority lane, exception class, migration verdict, and the blocked stronger sentence**

New docs added in this tranche:

- `1150-resilio-subject-architecture-family-key-domain-certificate-domain-and-encrypted-derivative-fragmentation-evaluation.md`
- `1151-subject-architecture-contract-sheet-page-governance-domain-authority-lane-and-upgrade-ceiling-interface-spec.md`
- `1152-governance-domain-review-page-standard-key-advanced-certificate-and-encrypted-derivative-branch-interface-spec.md`
- `1153-authority-and-reshare-review-page-owner-nonowner-linked-lane-and-manual-ro-exception-interface-spec.md`
- `1154-architecture-migration-watch-page-remove-readd-convert-ceiling-config-mode-and-linked-view-identity-interface-spec.md`
- `1155-subject-architecture-lineage-receipt-page-governance-domain-authority-lane-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `folder type` can no longer hide the difference between key governance, certificate governance, and encrypted derivative behavior
- linked-device defaults now publish when the only honest RO outcome requires leaving the linked lane and using a Standard-key exception
- upgrade promises now visibly branch between in-place change, remove-and-readd, derivative branch, and unsupported automation path instead of being implied by UI similarity
- later operators can open one receipt and see which governance primitive, delegation lane, and migration ceiling actually governed the chosen subject

## Revision addendum — transport profile, protocol overlap, cipher overlap, and bind residue after rev0337

This tranche locks the next seam around **transport profile truth**.
The key decisions now made explicit in the archive are:

- **transport profile is a first-class compiled object rather than a scattered bag of advanced toggles**
- **configured protocol set, effective common protocol overlap, configured cipher set, and effective common cipher overlap are different truths**
- **interface preference is weaker than bind witness, and bind witness is weaker than hard cutoff**
- **proxy-constrained egress, relay fallback, direct listener reach, and LAN discovery remain different route classes even for the same share**
- **every transport-affecting action needs one receipt that preserves overlap truth, bind residue, and the blocked stronger sentence**

New docs added in this tranche:

- `1168-resilio-transport-profile-protocol-overlap-cipher-overlap-and-bind-residue-fragmentation-evaluation.md`
- `1169-transport-profile-contract-sheet-page-route-class-protocol-set-cipher-set-and-bind-authority-interface-spec.md`
- `1170-protocol-overlap-review-page-direct-relay-lan-tracker-and-no-common-lane-interface-spec.md`
- `1171-bind-witness-review-page-interface-pinning-fallback-switch-and-use-only-cutoff-interface-spec.md`
- `1172-transport-hardening-review-page-lan-encryption-cipher-overlap-and-performance-side-effect-interface-spec.md`
- `1173-transport-profile-lineage-receipt-page-protocol-cipher-bind-witness-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `advanced network settings` can no longer hide the difference between configured protocol lists and the overlap a peer pair still actually shares
- interface pinning now publishes whether the runtime will fall forward or stop instead of pretending `bind` means confinement by itself
- hardening knobs now expose compatibility and side-effect cost before apply instead of after surprise route loss or slowdown
- later operators can open one receipt and see what tunnel classes survived, what overlap was actually proven, and which stronger sentence the product refused to say


## Revision addendum — overlapping-subject topology, seed-gap truth, and selective-sync admission ceilings after rev0338

This tranche locks the next seam around **overlapping-subject topology truth**.
The key decisions now made explicit in the archive are:

- **overlapping parent/child subjects are a first-class topology object rather than a convenience shortcut**
- **shared subtree visibility, seed authority, and shadow propagation are different truths**
- **selective materialization is weaker than overlap eligibility, because nested admission can require fully materialized subjects on both sides**
- **larger-root claims can be blocked by service-owned or license-bearing interior material even when the operator did not create that interior on purpose**
- **every serious overlap-affecting action needs one receipt that preserves claim class, seed-gap truth, dual-index cost, and the blocked stronger sentence**

New docs added in this tranche:

- `1174-resilio-overlapping-subject-topology-nested-share-shadow-seeding-and-selective-sync-ceiling-fragmentation-evaluation.md`
- `1175-overlapping-subject-contract-sheet-page-parent-child-topology-seed-lane-and-index-cost-interface-spec.md`
- `1176-nested-share-topology-review-page-parent-child-rights-shadow-propagation-and-seed-gap-interface-spec.md`
- `1177-overlap-admission-review-page-selective-sync-ceiling-home-root-conflict-and-existing-id-boundary-interface-spec.md`
- `1178-overlapping-subject-proof-page-shared-subtree-dual-indexing-and-propagation-residue-interface-spec.md`
- `1179-overlapping-subject-lineage-receipt-page-parent-child-claim-class-seed-gap-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `nested share` can no longer hide the difference between overlapping subjects, one unified subject illusion, and direct seed authority
- selective-sync state now publishes topology eligibility instead of pretending materialization mode is just a storage preference
- larger-root admission now surfaces service-interior and same-ID boundary conflicts before the operator learns them from add-folder errors
- later operators can open one receipt and see which overlap was admitted, what seed gap survived, and which stronger claim the product refused to make


## Revision addendum — interface affinity, multi-NIC ambiguity, and service all-NIC audience after rev0339

This tranche locks the next seam around **interface-affinity truth**.
The key decisions now made explicit in the archive are:

- **interface affinity is a first-class contract object rather than an advanced footnote**
- **requested NIC, effective NIC, listener audience, and fallback class are different truths**
- **a named interface preference is weaker than a bind witness, and a bind witness is weaker than a continuity claim**
- **service/runtime-class changes must review interface audience explicitly instead of laundering them through startup language**
- **every serious interface-affinity action needs one receipt that preserves requested NIC, effective witness, fallback class, audience delta, and the blocked stronger sentence**

New docs added in this tranche:

- `1180-resilio-interface-affinity-multi-nic-fallforward-and-service-all-nics-fragmentation-evaluation.md`
- `1181-interface-affinity-contract-sheet-page-requested-nic-effective-nic-and-fallback-class-interface-spec.md`
- `1182-multi-nic-review-page-announced-addresses-bind-preference-and-same-lan-ambiguity-interface-spec.md`
- `1183-interface-fallback-proof-page-bind-witness-next-active-switch-and-bridge-only-startup-boundary-interface-spec.md`
- `1184-service-nic-audience-review-page-all-nics-listener-class-and-exposure-delta-interface-spec.md`
- `1185-interface-affinity-lineage-receipt-page-requested-nic-effective-witness-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `choose interface` can no longer hide the difference between preference, effective witness, and hard cutoff
- multi-NIC troubleshooting now publishes interface contention explicitly instead of pretending the host has one obvious network identity
- service/runtime changes now surface network-audience widening before the operator learns it from side effects
- later operators can open one receipt and see what NIC was requested, what NIC was actually observed, and which stronger sentence the product refused to make



## Revision addendum — byte-plan certainty, hash witness, and reuse-vs-redownload ceilings after rev0340

This tranche locks the next seam around **byte-plan certainty**.
The key decisions now made explicit in the archive are:

- **byte-plan certainty is a first-class contract object rather than a speed hint**
- **piece-delta transfer, local block reuse, archive-assisted rename reuse, pre-seeded byte match, and full redownload are different truths**
- **hashing is weaker than byte witness, and byte witness is weaker than `no re-download required`**
- **partial local residue is weaker than resumability proof, and resumability proof is weaker than survivor safety**
- **every serious byte-plan action needs one receipt that preserves reuse basis, witness grade, fallback-to-redownload class, and the blocked stronger sentence**

New docs added in this tranche:

- `1186-resilio-byte-plan-certainty-hash-witness-dedup-reuse-and-partial-transfer-fragmentation-evaluation.md`
- `1187-byte-plan-contract-sheet-page-reuse-basis-hash-witness-and-redownload-ceiling-interface-spec.md`
- `1188-hash-and-preseed-review-page-local-byte-candidates-dedup-search-and-archive-dependency-interface-spec.md`
- `1189-reuse-basis-review-page-piece-delta-local-copy-rename-reuse-and-full-redownload-branch-interface-spec.md`
- `1190-partial-transfer-survivor-proof-page-resume-witness-cleanup-boundary-and-leftover-residue-interface-spec.md`
- `1191-byte-plan-lineage-receipt-page-reuse-basis-witness-grade-and-redownload-fallback-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `won't re-download` can no longer hide the difference between changed-piece transfer, local block reuse, archive-backed rename reuse, pre-seeded byte match, and ordinary full transfer
- hashing now publishes whether the system is still only evaluating local candidates or has actually proven reusable bytes
- partial residue now surfaces the difference between `bytes exist`, `resume seems plausible`, `resume is proven`, and `cleanup discards progress`
- later operators can open one receipt and see what cheaper path was relied on, what witness grade supported it, and which stronger sentence the product refused to make



## Revision addendum — queue-governance provenance, active-window ceilings, and visible-order mismatch after rev0341

This tranche locks the next seam around **queue-governance provenance**.
The key decisions now made explicit in the archive are:

- **queue-governance provenance is a first-class contract object rather than an advanced preference detail**
- **global default, per-share override, sticky former-manual override, active-window order, and visible list order are different truths**
- **`None` is weaker than `inherits current default`, and `inherits current default` is weaker than `will move first`**
- **priority policy is weaker than active admission, and active admission is weaker than uninterrupted completion**
- **every serious queue-order action needs one receipt that preserves policy origin, active-window scope, exception ceiling, and the blocked stronger sentence**

New docs added in this tranche:

- `1192-resilio-download-priority-policy-provenance-active-window-and-visible-order-fragmentation-evaluation.md`
- `1193-queue-governance-contract-sheet-page-policy-origin-active-window-and-visible-order-interface-spec.md`
- `1194-priority-origin-review-page-global-default-sticky-none-and-single-file-spillover-interface-spec.md`
- `1195-active-window-proof-page-50000-file-ceiling-suspension-exceptions-and-queue-rebuild-interface-spec.md`
- `1196-visible-order-mismatch-page-ui-alphabetical-order-non-splittable-files-and-overclaim-barrier-interface-spec.md`
- `1197-queue-governance-lineage-receipt-page-policy-origin-window-scope-and-visible-order-trust-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `priority` can no longer hide the difference between policy origin, active admission, and visible list order
- `None` now publishes whether the subject still inherits the live global default or is carrying sticky former-manual local state
- queue review now surfaces the active 50,000-file window and documented exception classes before the operator infers too much from backlog size or on-screen order
- later operators can open one receipt and see what policy origin governed the queue, what active scope it actually covered, and which stronger sentence the product refused to make


## Revision addendum — investigation evidence, support-lane truth, and capture survivorship after rev0355

This tranche locks the next seam around **investigation evidence**.
The key decisions now made explicit in the archive are:

- **support lane, capture posture, artifact class, and survivorship are different truths**
- **`debug enabled` is weaker than `logging witnessed active during the incident`, and that is weaker than `the needed evidence survived rotation or cleanup`**
- **live runtime evidence, post-crash residue, and runtime-stopped benchmark evidence are different diagnostic classes**
- **local export is weaker than proven escalation lane, and proven escalation lane is weaker than promised human review**
- **every serious troubleshooting action needs one receipt that preserves support lane, capture basis, survivorship risk, sharing posture, and the blocked stronger sentence**

New docs added in this tranche:

- `1276-resilio-investigation-evidence-bundle-support-lane-and-capture-posture-fragmentation-evaluation.md`
- `1277-investigation-evidence-contract-sheet-page-support-lane-capture-posture-and-artifact-classes-interface-spec.md`
- `1278-evidence-capture-review-page-live-repro-log-window-redaction-and-safe-freeze-boundary-interface-spec.md`
- `1279-support-lane-proof-page-self-serve-business-support-and-escalation-eligibility-interface-spec.md`
- `1280-evidence-retention-timeline-page-log-rotation-repro-window-and-postmortem-artifact-survival-interface-spec.md`
- `1281-investigation-evidence-lineage-receipt-page-support-lane-capture-basis-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `send logs` can no longer hide the difference between export capability, receiver class, and actual support entitlement
- capture UX now surfaces the difference between requested logging, witnessed active logging, sufficient repro window, and surviving evidence
- stopped-runtime network benchmarking now stays visibly separate from live-runtime fault observation
- later operators can open one receipt and see what evidence class was collected, who could actually receive it, and which stronger diagnostic sentence the product refused to make


## Revision addendum — storage accounting, occupancy budget, and hidden growth after rev0356

This tranche locks the next seam around **storage-accounting truth**.
The key decisions now made explicit in the archive are:

- **visible namespace, placeholder weight, materialized working bytes, hidden Archive bytes, and service-storage bytes are different truths**
- **reported `Size` is weaker than counted-scope truth, and counted-scope truth is weaker than full proven footprint**
- **cleanup of working bytes is weaker than total footprint reclamation**
- **a low-space warning is weaker than `the whole product is out of space` unless the watched budget basis is explicit**
- **every serious storage sentence needs one receipt that preserves counted scope, occupancy class, budget basis, hidden-growth risks, and the blocked stronger sentence**

New docs added in this tranche:

- `1282-resilio-storage-accounting-occupancy-budget-and-hidden-growth-fragmentation-evaluation.md`
- `1283-storage-accounting-contract-sheet-page-visible-size-placeholder-weight-and-hidden-growth-interface-spec.md`
- `1284-footprint-review-page-counted-bytes-placeholders-archive-and-service-storage-interface-spec.md`
- `1285-space-stop-proof-page-budget-gate-default-location-and-actual-occupancy-interface-spec.md`
- `1286-occupancy-drift-timeline-page-materialization-archive-rotation-and-clear-storage-events-interface-spec.md`
- `1287-storage-accounting-lineage-receipt-page-footprint-basis-growth-risks-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `size` can no longer hide the difference between counted sync subjects and the full local footprint
- `takes no space` can no longer hide the difference between namespace-only visibility, placeholders, working bytes, Archive growth, and service storage
- storage cleanup now surfaces exactly which occupancy classes changed and which remained
- later operators can open one receipt and see what was counted, what actually occupied bytes, what hidden growth survived, and which stronger storage sentence the product refused to make

## Revision addendum — pathname dialect, filesystem projection, and loss-boundary honesty after rev0359

This tranche locks the next seam around **pathname projection truth**.
The key decisions now made explicit in the archive are:

- **visible pathname, canonical identity, normalization class, case behavior, symbol projection, length ceiling, object-kind projection, and loss boundary are different truths**
- **`same path` is weaker than `same canonical identity`, and `same canonical identity` is weaker than `same safe arrival outcome`**
- **`link synced` is weaker than `link target coverage survives`**
- **human-equal glyphs are weaker than proven cohort-stable pathname identity**
- **every serious add / rename / rebind action needs one receipt that preserves filesystem dialect, projection outcome, loss boundary, evidence basis, and the blocked stronger sentence**

New docs added in this tranche:

- `1300-resilio-pathname-dialect-case-unicode-length-and-link-projection-fragmentation-evaluation.md`
- `1301-path-projection-contract-sheet-page-case-normalization-symbol-length-and-object-kind-interface-spec.md`
- `1302-path-equivalence-review-page-casefold-unicode-rewrite-and-merge-risk-interface-spec.md`
- `1303-projection-capability-proof-page-filename-encoding-length-symbol-and-link-support-basis-interface-spec.md`
- `1304-filesystem-dialect-timeline-page-arrival-rewrite-conflict-and-rebind-events-interface-spec.md`
- `1305-path-projection-lineage-receipt-page-dialect-basis-projection-loss-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `filename` can no longer hide the difference between human-facing glyphs, canonical identity, and cohort-stable projection
- rename review now surfaces case collapse, normalization drift, symbol rewrite, length ceilings, and link-kind mismatch before the operator overclaims safety
- `unsupported` can no longer hide whether the failure mode is rewrite, conflict, hard block, or link-only projection
- later operators can open one receipt and see which filesystem dialects were in play, what actually happened to the pathname, what loss boundary was accepted, and which stronger sentence the product refused to make

## Revision addendum — name planes, alias drift, and label-authority boundaries after rev0365

This tranche locks the next seam around **name-plane truth**.
The key decisions now made explicit in the archive are:

- **name plane is a first-class contract object rather than a side effect of `rename`, `identity`, `device`, `share`, or `folder` language**
- **identity handle, device handle, filesystem subject name, local UI alias, invitation label, and derived default folder name are different truths**
- **`renamed in UI` is weaker than `renamed on disk`, `renamed on disk` is weaker than `renamed on every peer`, and `changed device label` is weaker than `changed identity / certificate lineage`**
- **same displayed text is weaker than same authority continuity, and a new invite label is weaker than a persistent share rename**
- **every serious naming event now needs one receipt that preserves plane family, authority consequence, propagation scope, reset path, and the blocked stronger sentence**

New docs added in this tranche:

- `1336-resilio-name-plane-identity-device-share-and-link-label-fragmentation-evaluation.md`
- `1337-name-plane-contract-sheet-page-identity-device-path-alias-and-invitation-label-interface-spec.md`
- `1338-local-vs-remote-alias-review-page-disk-name-ui-alias-link-label-and-device-label-interface-spec.md`
- `1339-name-authority-proof-page-presentation-vs-certificate-lineage-and-propagation-basis-interface-spec.md`
- `1340-label-drift-timeline-page-local-rename-invite-regeneration-disconnect-persistence-and-identity-reset-interface-spec.md`
- `1341-name-plane-lineage-receipt-page-plane-family-propagation-scope-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `name` can no longer hide whether the product is speaking about a certificate-bearing identity, a device label, a filesystem subject, a local alias, or an invite-only label
- renaming now keeps authority consequences adjacent to text changes instead of letting presentation drift impersonate identity continuity
- invite generation now stays visibly different from persistent alias mutation because generated labels can diverge per recipient without changing the share itself
- disconnect persistence now stays visible because an old local alias surviving in UI is weaker than a live shared connection
- later operators can open one receipt and see what naming plane changed, what remained unchanged, who could observe the new text, what reset path exists, and which stronger naming sentence the product refused to make


## Revision addendum — effect direction, reverse-lane truth, and flow-role honesty after rev0366

This tranche locks the next seam around **effect-direction truth**.
The key decisions now made explicit in the archive are:

- **materialization mode and effect direction are different truths**
- **authoring lane, delete lane, serve lane, onward-reshare lane, reverse-recovery lane, and disconnect survivor class are different truths**
- **`full local copy` is weaker than `can publish`**
- **`can serve` is weaker than `can restore the world from here`**
- **`Read Only` is weaker than a real directional contract because ordinary read-only replication, storage-only backup, and opaque encrypted custody still have different reverse-effect ceilings**

New docs added in this tranche:

- `1342-resilio-effect-direction-bidirectional-backup-and-reverse-lane-fragmentation-evaluation.md`
- `1343-effect-direction-contract-sheet-page-authoring-delete-serve-and-recovery-lanes-interface-spec.md`
- `1344-flow-direction-review-page-bidirectional-storage-only-backup-and-opaque-custody-interface-spec.md`
- `1345-reverse-lane-proof-page-which-side-can-publish-delete-restore-and-reshare-interface-spec.md`
- `1346-effect-direction-timeline-page-enable-backup-disconnect-delete-and-recovery-events-interface-spec.md`
- `1347-effect-direction-lineage-receipt-page-lane-basis-reverse-effects-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `connected` can no longer hide whether this seat is truly collaborative, inbound-only, storage-only, or opaque custody
- delete review now keeps source-following, local survivor behavior, and reverse-delete ceilings visible instead of burying them in product folklore
- recovery review now keeps `can help recovery elsewhere` visibly weaker than `can republish recovery from here`
- later operators can open one receipt and see which directional lane governed the seat, what reverse effects were blocked, what survived disconnect, and which stronger sentence the product refused to make



## Revision addendum — governance plane, override authorship, and control-surface honesty after rev0367

This tranche locks the next seam around **governance-plane truth**.
The key decisions now made explicit in the archive are:

- **governance plane is a first-class contract object rather than a footnote of `Preferences`, `Advanced`, `Config`, `Service`, or `Mobile` wording**
- **authorship plane, witness surface, scope, override precedence, inheritance state, and activation boundary are different truths**
- **`same shown value` is weaker than `same governance lineage`**
- **`saved in a colder plane` is weaker than `already active winner`**
- **every serious policy or settings sentence now needs one receipt that preserves winning plane, losing planes, inheritance state, activation boundary, witness surface, and the blocked stronger sentence**

New docs added in this tranche:

- `1348-resilio-governance-plane-ui-poweruser-config-and-service-override-fragmentation-evaluation.md`
- `1349-governance-plane-contract-sheet-page-ui-poweruser-config-service-and-override-basis-interface-spec.md`
- `1350-policy-authorship-review-page-global-default-share-override-and-manual-detach-interface-spec.md`
- `1351-mutation-authority-proof-page-which-surface-can-set-see-and-override-this-value-interface-spec.md`
- `1352-governance-plane-timeline-page-default-adoption-manual-override-restart-and-service-world-events-interface-spec.md`
- `1353-governance-plane-lineage-receipt-page-authorship-plane-override-basis-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `setting exists` can no longer hide the difference between a live same-surface preference, a manual subject override, a power-user default, a startup-config takeover, or a service-owned world
- neutral-looking values can no longer silently impersonate restored inheritance after a manual detachment
- mobile and WebUI witnessing now stay visibly weaker than true authorship when a colder or desktop-only plane still owns the value
- later operators can open one receipt and see which plane won, what lost, what inheritance state survived, what activation boundary applied, and which stronger governance sentence the product refused to make


## Revision addendum — local mutability ceiling, write-barrier truth, and host-lane honesty after rev0368

This tranche locks the next seam around **local mutability ceiling**.
The key decisions now made explicit in the archive are:

- **local mutability ceiling is a first-class contract object rather than a side effect of `locked`, `permissions`, `service`, `SD card`, or `SMB` wording**
- **write grant, active principal, host write lane, lock barrier, filesystem health, and retry rung are different truths**
- **`path visible` is weaker than `path writable`, `path writable` is weaker than `safe host lane`, and `will retry later` is weaker than `writeable now`**
- **every serious local-write sentence now needs one receipt that preserves actor, grant class, lane class, strongest blocker, retry rung, continuity consequence, and the blocked stronger sentence**

New docs added in this tranche:

- `1354-resilio-local-mutability-ceiling-lock-permission-and-host-write-lane-fragmentation-evaluation.md`
- `1355-local-mutability-contract-sheet-page-write-grant-lock-barrier-and-host-lane-interface-spec.md`
- `1356-write-barrier-review-page-locks-permissions-api-grants-and-unsafe-host-paths-interface-spec.md`
- `1357-write-authority-proof-page-who-can-actually-mutate-bytes-here-now-interface-spec.md`
- `1358-mutability-ceiling-timeline-page-grant-loss-lock-release-remount-and-principal-switch-events-interface-spec.md`
- `1359-local-mutability-lineage-receipt-page-write-basis-blockers-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `cannot sync` can no longer hide whether the real barrier is a lock, a missing OS/API grant, a wrong service/NAS principal, an unsafe mixed SMB/direct lane, or filesystem / mount trouble
- host-lane safety now stays visibly separate from ordinary writeability so a technically writable but rollback-prone setup cannot impersonate healthy authority
- provider-grant surfaces now stay visibly different from classic filesystem permissions because selecting a path is weaker than gaining the write API lane
- later operators can open one receipt and see who the actor was, what write lane governed the attempt, what the strongest blocker really was, what retry or world change was required, and which stronger write sentence the product refused to make

## Revision addendum — entitlement provenance, license topology, and feature-afterlife truth after rev0369

This tranche locks the next seam around **entitlement provenance truth**.
The key decisions now made explicit in the archive are:

- **entitlement provenance is a first-class contract object rather than a side effect of `licensed`, `Pro`, `free`, `trial`, or `available` language**
- **site-issued v3 non-commercial activation, legacy Home Pro, legacy Family Pro, Business owner identity, linked-device inheritance, shared-seat delegation, trial state, and wrong-support posture are different truths**
- **`activated` is weaker than `legitimate for this usage lane`, and `legitimate for this usage lane` is weaker than `durable independent entitlement`**
- **feature-afterlife is first-class: some features survive as ordinary sync, some fall on owner loss, some fall on seat reclaim, some fall on expiry, and some are blocked by missing server-support posture**
- **every serious feature or upgrade sentence now needs one receipt that preserves entitlement source, grant topology, usage-lane verdict, feature-afterlife class, and the blocked stronger sentence**

New docs added in this tranche:

- `1360-resilio-entitlement-provenance-license-topology-and-feature-afterlife-fragmentation-evaluation.md`
- `1361-entitlement-provenance-contract-sheet-page-license-source-usage-lane-and-feature-afterlife-interface-spec.md`
- `1362-license-topology-review-page-owner-seat-family-lane-and-revocation-authority-interface-spec.md`
- `1363-feature-entitlement-proof-page-why-this-capability-is-allowed-here-now-interface-spec.md`
- `1364-entitlement-afterlife-timeline-page-activation-expiry-reclaim-and-lane-shift-events-interface-spec.md`
- `1365-entitlement-lineage-receipt-page-source-topology-afterlife-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `licensed` can no longer hide whether a feature is running on site-issued non-commercial activation, legacy personal licensing, family pack scope, business owner topology, linked inheritance, or a reclaimable seat
- feature availability now stays visibly separate from usage-lane legitimacy, so `active now` no longer impersonates `permitted for this commercial / non-commercial / server posture`
- local shares, business sharing/linking, and other feature cliffs now keep their entitlement dependency attached instead of falling into generic `Pro feature` folklore
- owner takeover, seat reclaim, expiry fan-out, and wrong-support posture now stay visibly separate from simple local key presence
- later operators can open one receipt and see why a feature existed here, who could revoke it, what cliff would happen next, and which stronger entitlement sentence the product refused to make


## Revision addendum — promise capacity, concurrency, and overcommitment truth after rev0408

This tranche locks the next seam around **promise capacity**.
The key decisions now made explicit in the archive are:

- **promise capacity is a first-class contract object rather than a side effect of graphs, rates, scheduler windows, and queue motion**
- **restored authority, admitted promise load, reserve headroom, and overcommitment risk are different truths**
- **visible motion is weaker than spare commitment room**
- **background work and discovery lag can consume real future budget even when throughput looks acceptable**
- **every serious promise-admission sentence now needs one receipt that preserves admitted load, headroom class, reserve posture, strongest blocked stronger sentence, and next release trigger**

New docs added in this tranche:

- `1588-resilio-promise-capacity-concurrency-and-overcommitment-fragmentation-evaluation.md`
- `1589-commitment-capacity-contract-sheet-page-issuer-budget-concurrent-promises-and-reserve-headroom-interface-spec.md`
- `1590-promise-load-review-page-admit-defer-throttle-and-capacity-reservation-routes-interface-spec.md`
- `1591-commitment-capacity-proof-page-load-envelope-headroom-and-overcommitment-guard-interface-spec.md`
- `1592-promise-capacity-timeline-page-budget-consumed-restored-throttled-and-overcommit-events-interface-spec.md`
- `1593-commitment-capacity-lineage-receipt-page-load-basis-headroom-class-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `allowed to promise again` can no longer hide whether there is actually room for another promise now
- scheduler pauses, rescans, hashing, merges, queue pressure, and throttles can no longer silently impersonate spare commitment headroom
- reserve policy now stays visibly separate from raw throughput so `fast enough right now` no longer impersonates `safe to admit more obligation`
- later operators can open one receipt and see what load was already admitted, what reserve remained protected, what headroom class was honest, what stronger promise was blocked, and what next event could release capacity
