from pathlib import Path

root = Path(__file__).resolve().parent

def prepend(path: str, text: str):
    p = root / path
    old = p.read_text(encoding='utf-8')
    p.write_text(text.strip() + '\n\n' + old, encoding='utf-8')

def write(path: str, text: str):
    p = root / path
    p.write_text(text.strip() + '\n', encoding='utf-8')

readme_add = '''## Revision addendum after rev0398 — evidence-to-decision thresholds, action charter, and escalation truth

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
'''

status_add = '''## Revision addendum — status shift toward evidence-to-decision thresholds after rev0398

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
'''

resilio_eval_add = '''## Revision addendum — Resilio evidence-to-decision threshold, action, and escalation evaluation after rev0398

Another current official Resilio pass still supports the same tightened judgment:

- **borrow Resilio's evidence diversity and troubleshooting candor**
- **do not clone Resilio's evidence-to-decision and action-threshold contract**

This time the key evidence cluster is:

- `My files don't sync` still tells operators to inspect peers, status warnings, History, and queue state before branching into repair steps.
- `Some internal tasks are taking time to complete` still describes background work that may simply need time, making `wait` or `monitor` a real route rather than indecision.
- `Peers aren't connecting` still branches operators into networking, firewall, proxy, relay, multicast, and predefined-host troubleshooting rather than one unified decision ladder.
- `Performance overview` still exposes short-window graphs useful for troubleshooting, but not a decision threshold or action charter.
- `Errors & Troubleshooting` still presents warnings, self-help guides, and support-artifact articles as neighboring article families rather than one threshold-and-decision workspace.
- `Collecting debug logs automatically`, `Collecting debug logs manually`, `Collecting crash reports, mini-dumps and core dumps`, and `Measuring network performance with iperf3` still describe heavier evidence gathering and escalation rungs, but not one operator-facing answer about when those rungs are actually justified.
- current support articles still say direct technical support is only for Sync Business and not Sync v3, which makes operator-side threshold judgment even more important.

So current Resilio still deserves credit for exposing many useful witness planes and repair ladders.
But it still does not own one operator-facing answer to:

> given the synthesized evidence we have right now, what threshold is actually cleared, which verb is justified next, what stronger verb stays blocked, and what uncertainty budget remains too large to spend?

That is why this pass again strengthens the non-clone line.
'''

scorecard_add = '''## Addendum after rev0398 — why evidence-to-decision thresholds now sit on the non-clone side

Resilio still earns credit for exposing useful witness planes and practical troubleshooting routes.
Those stay on the **borrow** side.

What stays on the **do not clone** side is the decision contract:

- current docs still make the operator decide informally whether the right next verb is wait, monitor, ask, repair, or escalate
- evidence surfaces and repair ladders still live on different pages with no canonical threshold object joining them
- heavy-capture routes still explain *how* to gather more evidence more clearly than *when* that burden is justified
- article reading still does too much of the work of turning synthesized evidence into an action boundary

So the line hardens again:

- **borrow witness diversity and troubleshooting candor**
- **do not clone a product shape where evidence-to-decision thresholds live outside the operator workspace**
'''

clone_veto_add = '''## Addendum after rev0398 — new clone-veto test for evidence-to-decision truth

A borrowed interface fails the clone test if it can merge evidence into one sentence but still cannot tell the operator what that sentence is actually good enough to do.
The new veto questions are:

- can the operator distinguish claim ceiling from action threshold?
- can the interface say `monitor only` or `ask one more thing` without pretending a stronger action is ready?
- can the interface publish an explicit uncertainty budget and the next fact that would spend it wisely?
- can escalation be justified as a threshold-crossing event rather than just analyst frustration?
- can the interface preserve one durable receipt showing allowed action, blocked stronger action, and reopen triggers?

If the answer is no, the interface is still cloning Resilio's scattered decision-threshold shape too closely.
'''

product_add = '''## Product-direction addendum after rev0398 — synthesized evidence must terminate in an explicit decision charter

AnonSync should not let an integrated claim masquerade as an automatic action.
The product direction is now explicit:

- **evidence-to-decision thresholding is first-class**
- **claim ceiling, action threshold, and uncertainty budget remain separate**
- **the same evidence can justify different verbs at different risk levels**
- **`no decision yet` is legitimate product state when the threshold is not met**
- **every meaningful choice needs one receipt preserving allowed action, blocked stronger action, fallback posture, and reopen triggers**

That means future interface work should keep one stable family for:

- decision-charter shaping from synthesized evidence
- action-threshold review across act / monitor / ask / defer / escalate routes
- uncertainty-budget publication and spend discipline
- allowed-action proof and blocked-stronger-action explanation
- threshold drift when new evidence arrives or old evidence stales out
- durable decision receipts for later disputes, escalation, and doctrine work

The product should never force the operator to turn a synthesized packet set into action purely through memory, chat, and personal courage.
'''

sources_add = '''## rev0399 source set — evidence-to-decision thresholds, action charter, and escalation truth

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
'''

write('docs/1534-resilio-evidence-to-decision-threshold-action-and-escalation-fragmentation-evaluation.md', '''# Resilio evidence-to-decision threshold, action, and escalation fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- intake packets honestly
- request the cheapest useful supplement
- synthesize several witness planes into one bounded integrated claim
- preserve conflict, contradiction, and synthesis ceiling

What it still lacked was the next ordinary operator answer:

> given the synthesized evidence we actually have right now, what is that enough to do, what stronger action is still blocked, and should the next move be act, monitor, ask, defer, or escalate?

That is the seam this pass locks.
A product that can merge evidence but cannot turn it into a thresholded decision still leaves too much truth in analyst courage, improvised escalation, and support folklore.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose many useful witness planes and troubleshooting rungs, but mostly as separate surfaces rather than one decision-threshold workspace:

- `My files don't sync` still tells operators to inspect peers, status warnings, History, and upload/download queues, and then fan out into different possible next steps.
- `Some internal tasks are taking time to complete` still explains that some states can simply reflect background work, which makes `wait` or `monitor` a real route rather than a failure to decide.
- `Peers aren't connecting` still breaks one symptom into several materially different branches around multicast, firewall, routing, proxy, relay, and predefined hosts.
- `Performance overview` still exposes 1-minute, 10-minute, and 1-hour graphs that inform judgment but do not themselves declare what threshold is cleared.
- `Errors & Troubleshooting` still clusters warnings, self-help guides, and support-artifact pages as separate article families.
- `Collecting debug logs automatically` and `Collecting debug logs manually` still define a heavier evidence-capture burden, including enablement, restart, reproduction, and post-repro wait time.
- `Collecting crash reports, mini-dumps and core dumps` still defines a deeper escalation rung.
- `Measuring network performance with iperf3` still adds another specialized evidence rung and requires Sync to be completely shut down during the test.
- support articles still say direct technical support is available only for Sync Business and not Sync v3, which increases the importance of operator-side threshold judgment.

## What current Resilio still gets right

### 1) It admits that not every symptom needs the same next move

Some issues point toward waiting, some toward configuration checks, some toward network diagnosis, and some toward deep capture.
That is worth borrowing.

### 2) It preserves burden differences between rungs

Looking at warnings is cheaper than restarting with debug logging.
An iperf3 run is different from a history check.
A core dump is much heavier than a queue glance.
That honesty matters.

### 3) It keeps troubleshooting practical

The articles are not abstract.
They tell operators real next moves.
That practical candor is valuable.

## Where current Resilio still fragments the operator answer

### A) Threshold truth still lives in the reader's head

The operator can usually find relevant pages, but still must decide privately whether the current evidence is enough to:

- wait and observe
- ask one more discriminating question
- perform a bounded repair
- escalate for deeper artifacts
- publish a conclusion

The docs give ingredients and ladders, but not one explicit threshold object.

### B) Claim strength and action readiness are not compiled together

A graph can be suggestive.
A warning can be actionable.
A log can be rich but stale.
A support artifact can be costly but still inconclusive.
Current Resilio surfaces do not compile those facts into one sentence about what action is justified now.

### C) `no decision yet` is not owned as a product state

The docs can imply patience or deeper investigation, but the product shape still pushes the operator to infer whether unresolved uncertainty is acceptable or disqualifying.

### D) Escalation burden is described more clearly than escalation justification

Resilio explains how to gather logs, dumps, and tests.
It is less explicit about when those rungs are proportionate given the actual uncertainty left.

## What AnonSync should borrow

- typed troubleshooting ladders
- practical next-step candor
- burden honesty across light and heavy evidence rungs
- separate witness surfaces rather than one vague health badge

## What AnonSync should not clone

AnonSync should not clone a world where the operator must translate synthesized evidence into action mainly through private judgment.
It should not leave the following questions scattered across warnings, articles, and support instructions:

- what threshold is actually cleared?
- what action verb is justified now?
- what stronger verb stays blocked and why?
- what uncertainty budget remains too large to spend?
- what next fact or event would most efficiently change the threshold?

## Product requirement extracted from this evaluation

AnonSync should own one stable page family for **decision charters**.
That family should make it ordinary to publish:

- target decision
- evidence basis used
- current claim ceiling
- action threshold cleared
- uncertainty budget remaining
- allowed next verb
- blocked stronger verb
- reopen trigger and escalation trigger

## Bottom line

Current Resilio still deserves credit for exposing useful evidence planes and real troubleshooting ladders.
But it still does not own one operator-facing answer to:

> given the synthesized evidence we have right now, what is it actually enough to do?

That is why this seam belongs on the non-clone side.
''')

write('docs/1535-decision-charter-contract-sheet-page-target-action-threshold-and-residual-uncertainty-interface-spec.md', '''# Decision charter contract sheet page: target action threshold and residual uncertainty interface spec

## Purpose

Once evidence has been synthesized, the operator still needs one page that answers:

> what exact decision are we trying to make, what action threshold is in play, and how much unresolved uncertainty is still allowed before a stronger action becomes dishonest?

## Core decision

AnonSync must expose one first-class **Decision charter contract sheet** whenever synthesized evidence is being used to justify a repair, wait posture, escalation, external statement, certification move, or doctrinal application.

## Fixed page order

1. **Decision header**
2. **Target-decision card**
3. **Threshold-ladder card**
4. **Evidence-basis card**
5. **Residual-uncertainty card**
6. **Allowed-action card**
7. **Blocked-stronger-action card**
8. **Decision sentence**

### 1) Decision header

Show:

- decision charter id
- parent case or synthesis id
- decision owner
- current decision posture
- current claim ceiling
- highest cleared threshold
- allowed next verb
- strongest blocked verb
- reopen trigger count

Supported `decision_posture` values:

- `charter-opened`
- `threshold-mapping-in-progress`
- `uncertainty-budget-drafted`
- `bounded-action-ready`
- `monitor-only-ready`
- `ask-before-action`
- `escalation-ready`
- `decision-blocked`
- `superseded`

Hard rule:

The header may not describe a charter as `action-ready` unless at least one threshold has been marked `cleared` and at least one stronger threshold has either been tested or explicitly marked out of scope.

### 2) Target-decision card

Required rows:

- target decision question
- target action being considered
- harm if action is delayed
- harm if action is premature
- governing scope
- excluded scopes

Supported `decision_target_class` values:

- `bounded-repair`
- `wait-and-monitor`
- `ask-for-one-more-fact`
- `heavy-capture-escalation`
- `publish-conclusion`
- `publish-warning-only`
- `halt-or-freeze`
- `external-handoff`

Hard rule:

One decision charter answers one named decision.
It may mention adjacent choices, but cannot quietly decide them too.

### 3) Threshold-ladder card

Render one row per candidate threshold.
Required fields:

- threshold name
- required basis class
- current threshold state
- why cleared or not cleared
- next cheapest upgrade path

Supported `threshold_name` values:

- `observe-only`
- `monitor-with-watch`
- `bounded-local-action`
- `cohort-action`
- `heavy-capture-escalation`
- `publish-claim`
- `close-case`

Supported `threshold_state` values:

- `cleared`
- `not-cleared`
- `blocked-by-conflict`
- `blocked-by-world-mismatch`
- `blocked-by-staleness`
- `deferred`
- `not-attempted`

Hard rule:

A higher threshold may not be implied from a lower one.
`monitor-with-watch` does not imply `bounded-local-action`.
`bounded-local-action` does not imply `publish-claim`.

### 4) Evidence-basis card

Required rows:

- active synthesis id
- packet classes relied on
- known contradictory packets
- freshness posture
- missing high-value source classes
- weighting note

Hard rule:

The decision page may not hide a contradiction that the synthesis page still marks unresolved.

### 5) Residual-uncertainty card

Required rows:

- uncertainty budget class
- concrete open questions
- acceptable uncertainty for this threshold
- uncertainty already consumed
- uncertainty that still blocks stronger action

Supported `uncertainty_budget_class` values:

- `minimal`
- `bounded-and-explicit`
- `moderate-but-tolerable`
- `too-large-to-spend`
- `unknown-because-world-fit-failed`

Hard rule:

`too-large-to-spend` must automatically block any row above `ask-for-one-more-fact`, `monitor-with-watch`, or `heavy-capture-escalation`.

### 6) Allowed-action card

Required rows:

- allowed next verb
- exact scope of permission
- safeguards required
- witness required after action
- expiry or rereview time

Supported `allowed_next_verb` values:

- `wait`
- `monitor`
- `ask`
- `apply-bounded-action`
- `escalate-capture`
- `freeze-or-halt`
- `publish-bounded-claim`
- `handoff-with-warning`

Hard rule:

Exactly one primary next verb must be named.
Secondary verbs can appear as contingencies only.

### 7) Blocked-stronger-action card

Required rows:

- strongest blocked verb
- what evidence gap blocks it
- what contradiction blocks it
- what cheaper path could unblock it
- safe fallback if never unblocked

Hard rule:

The blocked stronger action must be visible even when the allowed next verb looks obvious.

### 8) Decision sentence

Render exactly two lines:

- **Allowed action now**
- **Strongest blocked stronger action and why**

Hard rule:

If the primary next verb is `wait` or `monitor`, the second line must state what future event would re-open the charter automatically.
''')

write('docs/1536-action-threshold-review-page-claim-ceiling-act-monitor-ask-and-escalate-routes-interface-spec.md', '''# Action-threshold review page: claim ceiling, act, monitor, ask, and escalate routes interface spec

## Purpose

The contract sheet defines the target decision.
The operator still needs one review page that compares live routes side by side and answers:

> is the right next move to act, monitor, ask, defer, or escalate, and what exact evidence difference makes that route stronger than the others right now?

## Review layout

1. **Route-comparison strip**
2. **Claim-ceiling panel**
3. **Threshold-crossing panel**
4. **Uncertainty-spend panel**
5. **Cheapest-upgrade panel**
6. **Decision pressure panel**
7. **Review verdict**

### 1) Route-comparison strip

Show one card for each route:

- `wait`
- `monitor`
- `ask`
- `bounded-action`
- `heavy-escalation`
- `publish`
- `halt`

Each card must show:

- current eligibility
- key supporting basis
- key blocker
- reversibility
- risk of acting too early
- risk of waiting too long

Hard rule:

The interface may not hide non-selected routes entirely.
It must show why they lost.

### 2) Claim-ceiling panel

Required rows:

- strongest safe sentence
- strongest sentence needed for each route
- routes supported only by weaker sentences
- routes blocked by unresolved contradiction

Hard rule:

A route cannot be marked `eligible` if its required sentence is above the current claim ceiling.

### 3) Threshold-crossing panel

For each route, show:

- threshold status
- what evidence cleared it
- what evidence failed it
- whether failure is reversible or structural

Supported `threshold_failure_class` values:

- `missing-fact`
- `stale-basis`
- `world-mismatch`
- `conflict-unresolved`
- `cost-disproportionate`
- `scope-too-wide`

### 4) Uncertainty-spend panel

Required rows:

- uncertainty still open
- whether this route tolerates that uncertainty
- what harm follows if uncertainty is wrong
- whether the route increases or decreases future certainty

Hard rule:

The review must publish when a route is chosen *despite* open uncertainty, not just when the route waits for certainty.

### 5) Cheapest-upgrade panel

Required rows:

- next cheapest fact that would upgrade the current route
- next cheapest fact that would downgrade the current route
- next cheapest artifact or observation that would unlock the blocked stronger route

Hard rule:

`collect more logs` is invalid unless named as the cheapest upgrade relative to all other currently available asks.

### 6) Decision pressure panel

Required rows:

- time pressure
- safety pressure
- operational pressure
- evidence decay pressure
- cost of continued indecision

Supported `decision_pressure_posture` values:

- `low-and-patient`
- `watch-closely`
- `time-sensitive`
- `harm-rising`
- `freeze-first`

Hard rule:

High pressure may justify a lower-certainty route, but the review must publish that trade explicitly.

### 7) Review verdict

Render:

- selected route
- why it beats the nearest alternative
- what stronger route stays blocked
- what event reopens route comparison
''')

write('docs/1537-decision-proof-page-allowed-action-blocked-stronger-action-and-uncertainty-budget-interface-spec.md', '''# Decision proof page: allowed action, blocked stronger action, and uncertainty budget interface spec

## Purpose

After review, the operator still needs one proof page that says:

> what exactly are we allowed to do now, why is that the strongest honest move, and what uncertainty remains too large for a stronger move?

## Proof sections

1. **Proof headline**
2. **Allowed-action proof block**
3. **Threshold-basis block**
4. **Residual-uncertainty block**
5. **Blocked-stronger-action block**
6. **Fallback-and-reopen block**

### 1) Proof headline

Show:

- allowed next verb
- exact scope
- decision grade
- evidence freshness posture
- residual uncertainty class

Supported `decision_grade` values:

- `observe-grade`
- `monitor-grade`
- `bounded-action-grade`
- `escalation-grade`
- `publication-grade`
- `freeze-grade`

### 2) Allowed-action proof block

Required rows:

- action verb
- scope bound
- preconditions satisfied
- safeguards required
- post-action witness required
- maximum sentence that action authorizes later

Hard rule:

An allowed action proof must say what the action **does not** authorize.

### 3) Threshold-basis block

Required rows:

- threshold cleared
- synthesis ids relied on
- decisive packets or witnesses
- decisive contradiction handling
- why the next lower route is insufficient

### 4) Residual-uncertainty block

Required rows:

- open uncertainty items
- why tolerated here
- why not tolerable for stronger route
- downgrade trigger

Hard rule:

If residual uncertainty is tolerated, the page must state whether the choice is robust-to-error or merely time-favored.

### 5) Blocked-stronger-action block

Required rows:

- blocked stronger action
- exact blocker class
- evidence or event needed to clear blocker
- whether the blocker is likely, hard, or impossible to clear

Supported `blocker_clearability` values:

- `cheap-to-clear`
- `moderate-cost`
- `heavy-burden`
- `unlikely-to-clear`
- `structurally-impossible`

### 6) Fallback-and-reopen block

Required rows:

- fallback posture if no further evidence arrives
- automatic reopen triggers
- expiry time for current proof
- next owner on reopen

Hard rule:

Every proof must expire or revalidate on an explicit basis; silent forever-valid decision proofs are not allowed.
''')

write('docs/1538-decision-timeline-page-threshold-crossing-deferral-escalation-and-reopen-events-interface-spec.md', '''# Decision timeline page: threshold crossing, deferral, escalation, and reopen events interface spec

## Purpose

A decision is rarely one moment.
The operator needs a timeline that answers:

> when did the threshold actually change, when was action deferred, when did escalation become justified, and when did the earlier proof lose force?

## Timeline event types

Supported `decision_event_type` values:

- `threshold-opened`
- `threshold-cleared`
- `threshold-failed`
- `decision-deferred`
- `monitor-posture-entered`
- `action-authorized`
- `action-blocked`
- `escalation-justified`
- `escalation-declined`
- `proof-expired`
- `proof-revalidated`
- `reopen-trigger-fired`
- `fallback-invoked`

## Required columns

- event time
- prior route
- new route
- evidence delta causing the shift
- uncertainty delta
- stronger sentence gained or lost
- owner after event

## Hard rules

### Threshold shifts must name the cause

A transition from `monitor` to `bounded-action`, or from `bounded-action` to `escalation`, must name the packet, fact, timeout, conflict, or external event that changed the route.

### Deferral is not absence

If the decision is intentionally deferred, the timeline must show:

- why deferred
- what watch is active
- what event will end the deferral

### Reopen must weaken something concrete

A reopen event must say which previously allowed action or stronger sentence lost force.
''')

write('docs/1539-decision-lineage-receipt-page-action-basis-threshold-posture-and-blocked-stronger-sentences-interface-spec.md', '''# Decision lineage receipt page: action basis, threshold posture, and blocked stronger sentences interface spec

## Purpose

Later operators need one receipt that answers:

> what was the decision, what threshold was actually cleared, what stronger move stayed blocked, and why did the archive treat that choice as honest at the time?

## Receipt layout

1. **Decision identity**
2. **Action basis**
3. **Threshold posture**
4. **Residual uncertainty**
5. **Blocked stronger sentence**
6. **Expiry and reopen basis**

### 1) Decision identity

Required fields:

- decision charter id
- parent synthesis id
- affected scope
- decision owner
- receipt issue time

### 2) Action basis

Required fields:

- allowed next verb
- exact scope
- decisive basis sources
- safeguards attached
- post-action witness required

### 3) Threshold posture

Required fields:

- highest cleared threshold
- nearest blocked threshold
- threshold failure class if blocked
- decision pressure posture

### 4) Residual uncertainty

Required fields:

- uncertainty budget class
- key open questions
- tolerated-vs-not-tolerated split

### 5) Blocked stronger sentence

Render exactly one line:

- **Strongest blocked stronger sentence and why**

### 6) Expiry and reopen basis

Required fields:

- expiry trigger
- automatic reopen triggers
- fallback if no new evidence arrives
- successor decision id if superseded

## Hard rule

A lineage receipt must preserve the weaker surviving truth even after the chosen action completes.
Completing the action does not retroactively prove the stronger blocked sentence.
''')

prepend('README.md', readme_add)
prepend('docs/00-status.md', status_add)
prepend('docs/10-resilio-sync-evaluation.md', resilio_eval_add)
prepend('docs/11-resilio-borrow-line-and-non-clone-scorecard.md', scorecard_add)
prepend('docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md', clone_veto_add)
prepend('docs/20-product-direction.md', product_add)
prepend('docs/sources.md', sources_add)
