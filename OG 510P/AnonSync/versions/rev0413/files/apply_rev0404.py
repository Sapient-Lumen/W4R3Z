from pathlib import Path

root = Path(__file__).resolve().parent

def prepend(path: str, text: str):
    p = root / path
    old = p.read_text(encoding='utf-8')
    p.write_text(text.strip() + '\n\n' + old, encoding='utf-8')

def write(path: str, text: str):
    p = root / path
    p.write_text(text.strip() + '\n', encoding='utf-8')

# New docs for rev0404
write('docs/1564-resilio-finish-forecast-remaining-work-and-eta-confidence-fragmentation-evaluation.md', """
# Resilio finish forecast, remaining work, and ETA-confidence fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- prove that work was alive
- separate motion from net progress
- show churn and no-net-gain boundaries
- trigger reroute or rescue when busy work stopped buying real reduction of the obligation

What it still lacked was the next ordinary operator answer:

> given the current progress truth, what can we now honestly forecast about finishing, how much obligation remains, and how believable is any ETA or deadline claim?

That is the seam this pass locks.
A product that can say work is truly advancing but still cannot say whether it is finishable soon, later, or not honestly forecastable yet still leaves too much truth trapped in graph watching and ad hoc optimism.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose several real **forecast ingredients**, but mostly as separate operational surfaces rather than one operator-facing forecast contract:

- `Performance overview` still exposes only short real-time windows — 1 minute, 10 minutes, and 1 hour — with per-peer speed, latency, and disk queue detail.
- `How soon does synchronization start?` still says change discovery may be immediate through filesystem notifications, or delayed until scheduled rescan every 600 seconds and on start, and that `folder_rescan_interval = 0` disables rescans even on restart.
- `Running Sync on schedule` still says paused hours stop ordinary upload/download but do not stop zero-sized-file sync, deletion propagation, and rescanning/indexing.
- `Power user preferences` still lists forecast-shaping settings such as `direct_torrent_enabled`, `prioritize_initial_indexing`, `parallel_indexing`, `recheck_locked_files_interval`, and `folder_rescan_interval`, each capable of changing how quickly visible work can actually finish.
- `Some internal tasks are taking time to complete` still says hidden work like checking blocks, deduplication copy, hashing, merging, scanning, reading, and writing can consume time without yet proving that final obligation is near completion.
- `When a file changes, does Resilio Sync transfer the entire file again, or just the part that's changed?` still says only changed pieces are normally transferred, but if pieces shift then the whole file is re-synced unless a Business-only delta feature applies.
- `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time` still shows that peers can be told work exists and only later discover that no source can actually provide the bytes.
- `Locked files` still shows that the work can remain pending because another application has blocked access entirely.

## What current Resilio still gets right

### 1) It exposes many of the variables that distort any naive ETA

Short-window speeds, disk load, queue depth, rescans, schedule pauses, and hidden preprocessing are all real forecast ingredients.
That candor is worth borrowing.

### 2) It admits that discovery time and transfer time are different phases

The rescan article and scheduler article both make clear that bytes are not the whole story.
A system may still be detecting, indexing, or waiting for its next allowed transfer window.

### 3) It names several conditions that can collapse forecast confidence

Locked files, ghost-file conditions, and whole-file re-sync after shifted changes all teach the same lesson:
a visible trend line is still weaker than a reliable finish forecast.

## Where current Resilio still fragments the operator answer

### A) Performance windows are still observation tools, not a finish contract

Current graphs can show what happened over 1 minute, 10 minutes, or 1 hour.
They still do not compile one explicit answer to what remains, whether the obligation is finishable under current conditions, or how wide the honest ETA window should be.

### B) Delay sources still sit on different surfaces

Scheduler pauses, rescan cadence, initial indexing delay, locked-file recheck intervals, and hidden preprocessing each affect finish time.
But current product/docs still make the operator collect those sources mentally rather than receiving one normalized forecast object.

### C) Partial-transfer efficiency and restart-from-start risk still coexist without one truth surface

Resilio help usefully says changed pieces are usually transferred, yet also says shifted changes can force whole-file re-sync and `direct_torrent_enabled` can restart a small file from the beginning after interruption.
That means optimistic byte-based ETA can be honestly wrong unless risk is published.

### D) The product still does not own `no honest forecast yet`

Current docs give many reasons forecast confidence may be weak.
But they still do not render one first-class answer that says the work is real, progress exists, and yet no narrow ETA claim is currently justified.

## Resulting product decision

AnonSync should borrow Resilio's candor that forecast depends on speed, delay windows, rescans, schedule rules, preprocessing, and availability failures.
It should **not** clone the contract where the operator still has to infer finishability and ETA confidence from scattered metrics, warnings, and advanced settings.

AnonSync should instead expose:

- one first-class **completion forecast contract sheet**
- one **forecast-quality review**
- one **finish forecast proof** page
- one **forecast timeline**
- one durable **forecast lineage receipt**

## Hard decisions locked by this pass

- **net progress is weaker than finish forecast**
- **finishability, ETA window, deadline confidence, and no-honest-forecast stay separate**
- **hidden preprocessing, schedule pauses, discovery lag, and retry risk must count against forecast confidence**
- **the product may honestly say `no narrow ETA` even while work is real and advancing**
- **forecast receipts must preserve remaining-obligation basis, finishability grade, ETA window, risk basis, and blocked stronger sentence**
""")

write('docs/1565-completion-forecast-contract-sheet-page-remaining-obligation-finishability-and-confidence-interface-spec.md', """
# Completion forecast contract sheet page: remaining obligation, finishability, and confidence interface spec

## Purpose

Once net progress exists, the operator still needs one page that answers:

> what exactly remains, is the work finishable under current conditions, what ETA window is currently honest, and what conditions make the estimate stronger or weaker?

## Core decision

AnonSync must expose one first-class **Completion forecast contract sheet** whenever a work item has proved net progress, partial net progress, churn-dominant progress with some remaining path, reroute after no-net-gain, or any live request for time-to-finish, deadline posture, or finishability.

## Fixed page order

1. **Forecast header**
2. **Remaining-obligation card**
3. **Finishability card**
4. **ETA-window card**
5. **Confidence-and-risk card**
6. **Forecast sentence**

### 1) Forecast header

Show:

- forecast id
- linked progress id
- linked heartbeat id
- linked claim id
- current forecast posture
- current custodian
- remaining-obligation unit
- current finishability grade
- current ETA-window status
- current deadline posture if any
- forecast owner

Supported `forecast_posture` values:

- `drafted-from-progress`
- `remaining-work-shaped`
- `finishability-provisional`
- `eta-window-published`
- `deadline-risk-open`
- `forecast-held-wide`
- `no-honest-forecast`
- `reroute-before-forecast`
- `requalified-after-shift`
- `closed`

Hard rule:

The header may not imply a trustworthy ETA merely because net progress exists.
Net progress is still weaker than a finish forecast.

### 2) Remaining-obligation card

Required rows:

- named obligation still open
- current remaining-work basis
- unit of remaining work
- whether the remaining basis is direct or inferred
- known completed fraction if publishable
- hidden preparation still outstanding
- known external wait still outstanding
- current smallest finishable subgoal

Hard rules:

- `remaining work` must not silently equal `bytes left` unless the contract says bytes are the real obligation unit.
- Hidden preparation such as rescan, hash, merge, approval, wake, or lock release must remain visible when it affects completion.

### 3) Finishability card

Required rows:

- current finishability grade
- strongest basis for that grade
- hardest blocker to finishing
- whether finish is possible under current route
- whether finish needs new evidence or only elapsed work
- whether the route is deadline-compatible

Supported `finishability_grade` values:

- `finishable-now-if-motion-holds`
- `finishable-with-known-delays`
- `finishable-after-prerequisite`
- `finishable-only-after-reroute`
- `finishability-uncertain`
- `not-honestly-finishable-under-current-route`

Hard rule:

`finishable-now-if-motion-holds` requires both a remaining-work basis and no known blocking prerequisite stronger than elapsed time.

### 4) ETA-window card

Required rows:

- current ETA claim class
- earliest honest finish time
- latest honest finish time
- whether the window is local-time or relative-duration based
- main factors widening the window
- next condition that would narrow the window most

Supported `eta_claim_class` values:

- `no-eta-claimed`
- `wide-window-only`
- `bounded-window`
- `checkpoint-based-window`
- `deadline-miss-risk-window`
- `narrow-window-blocked`

Hard rules:

- A single point ETA is disallowed.
- `bounded-window` requires an explicit lower and upper bound.
- `checkpoint-based-window` must name the checkpoint that divides the estimate.

### 5) Confidence-and-risk card

Required rows:

- current confidence grade
- strongest support for confidence
- strongest reason confidence is capped
- whether the estimate depends on hidden work
- whether schedule gates or pause windows apply
- whether source availability risk is live
- whether restart-from-start or whole-file-rework risk is live
- whether locked-resource risk is live

Supported `forecast_confidence_grade` values:

- `high-for-current-window`
- `moderate`
- `fragile`
- `too-fragile-for-eta`

Hard rule:

If any live risk can invalidate the current window without a new external event being noticed quickly, confidence may not exceed `moderate`.

### 6) Forecast sentence

Render:

- strongest allowed finishability sentence
- strongest allowed ETA sentence
- strongest blocked stronger sentence

Examples:

- `Net progress is real, but only a wide finish window is honest because scheduled pauses and hidden merge work still dominate the remaining path.`
- `Current route is finishable after lock release; no honest ETA exists until access to the blocked files returns.`
- `Work appears likely to finish within the current window if source availability and rescan posture do not change, but a tighter claim is blocked.`
""")

write('docs/1566-forecast-quality-review-page-finishability-eta-window-and-deadline-risk-routes-interface-spec.md', """
# Forecast quality review page: finishability, ETA window, and deadline-risk routes interface spec

## Purpose

The contract sheet defines what remains and what would count as an honest forecast.
The review page must decide:

> based on current evidence, can this work be finished under the current route, what ETA window is still justified, and is the operator dealing with healthy uncertainty, fragile forecasting, or no honest forecast at all?

## Core review rule

AnonSync must separate **remaining-work evidence**, **finishability evidence**, **ETA evidence**, **deadline evidence**, and **forecast fragility**.
No review may collapse those into one optimistic progress label.

## Fixed page order

1. **Review banner**
2. **Remaining-work review**
3. **Finishability review**
4. **ETA-window review**
5. **Deadline and slip review**
6. **Blocked stronger sentence**

### 1) Review banner

Show:

- current review verdict
- current finishability grade
- ETA claim class
- confidence grade
- active deadline posture if any
- current forecast owner

Supported `review_verdict` values:

- `forecast-supported`
- `wide-forecast-only`
- `checkpoint-forecast-only`
- `finishable-no-eta`
- `deadline-risk-rising`
- `forecast-broken-reroute-needed`
- `no-honest-forecast`

Hard rule:

`forecast-supported` is disallowed unless both remaining-work basis and finishability basis are fresh enough for the requested decision horizon.

### 2) Remaining-work review

Required rows:

- strongest current basis for what remains
- whether remaining work is directly observed or inferred
- whether hidden preparation is already included
- whether remaining work is shrinking monotonically
- whether new debt is still appearing
- reviewer who accepted the remaining-work basis

Route rules:

- If remaining-work basis is stale or scope-mismatched, route to `no-honest-forecast`.
- If remaining work depends on a known checkpoint not yet cleared, route to `checkpoint-forecast-only`.

### 3) Finishability review

Required rows:

- strongest basis that finishing is possible
- strongest basis that finishing is blocked
- whether current route can complete without mutation
- whether source, lock, approval, or wake dependency is unresolved
- whether reroute would change forecast materially

Route rules:

- `finishable-no-eta` is valid when the route still looks viable but elapsed-time forecasting is too fragile.
- `forecast-broken-reroute-needed` is required when current route no longer honestly supports finishing.

### 4) ETA-window review

Required rows:

- strongest current ETA basis
- whether the basis is throughput, checkpoint, or policy-window driven
- whether recent net progress is representative or merely bursty
- whether scheduled pauses or rescan windows widen the estimate
- whether recent interruption risk is live

Route rules:

- Throughput-only ETA may not stand if hidden work or schedule gates dominate.
- `wide-forecast-only` is required if only a broad window survives honest review.
- `no-honest-forecast` is required when lower/upper bounds would be theatrical rather than evidenced.

### 5) Deadline and slip review

Required rows:

- named deadline if any
- current deadline posture
- strongest basis for on-time or late risk
- first reason the estimate could slip
- next condition that would restore confidence most

Supported `deadline_posture` values:

- `no-deadline-bound`
- `comfortably-inside-window`
- `inside-but-fragile`
- `checkpoint-critical`
- `likely-slip`
- `deadline-miss-probable`
- `deadline-claim-blocked`

Hard rule:

Deadline posture may not exceed the strength of the ETA claim class.
A weak ETA cannot support a strong on-time claim.

### 6) Blocked stronger sentence

Render:

- strongest allowed forecast sentence
- strongest blocked stronger forecast sentence
- missing fact or event that would unlock the stronger sentence

Examples:

- `Work is finishable with known delays, but a bounded ETA is blocked by the next rescan and lock recheck windows.`
- `A broad completion window is honest, but an on-time deadline claim is blocked by schedule pauses and source-availability fragility.`
- `Net progress is real, yet no honest ETA survives because remaining work is still changing as conflict debt appears.`
""")

write('docs/1567-finish-forecast-proof-page-eta-window-finishability-grade-and-claim-ceiling-interface-spec.md', """
# Finish forecast proof page: ETA window, finishability grade, and claim ceiling interface spec

## Purpose

After forecast review, the product needs one durable proof page that answers:

> what is the strongest finish claim we can still make, what proves the remaining work and finishability posture, what ETA window survives honest scrutiny, and what stronger sentence is still blocked?

## Core decision

AnonSync must expose one first-class **Finish forecast proof** page for every work item that has entered forecast review, deadline review, no-honest-forecast territory, reroute-after-forecast, or external publication of finish expectations.

## Fixed page order

1. **Forecast verdict banner**
2. **Remaining-work basis card**
3. **Finishability basis card**
4. **ETA-window card**
5. **Forecast fragility card**
6. **Blocked stronger claim card**

### 1) Forecast verdict banner

Show:

- current forecast verdict
- current finishability grade
- strongest allowed finish sentence
- strongest allowed ETA sentence
- current confidence grade
- deadline posture if any
- forecast owner

Supported `forecast_verdict` values:

- `finishable-with-bounded-window`
- `finishable-with-wide-window`
- `finishable-after-checkpoint`
- `finishable-no-honest-eta`
- `deadline-risk-material`
- `forecast-broken-reroute-needed`
- `no-honest-forecast-proved`

Hard rule:

A verdict may not claim any ETA window unless both the remaining-work basis and the window-widening factors are explicitly published.

### 2) Remaining-work basis card

Required rows:

- strongest current remaining-work basis
- freshness of that basis
- whether it is direct or inferred
- hidden preparation still outstanding
- external dependency still outstanding
- reviewer who accepted the basis

### 3) Finishability basis card

Required rows:

- strongest basis that work can finish
- strongest live blocker against finish
- whether current route is sufficient
- whether reroute would reset or preserve the estimate
- smallest claimed finish scope

### 4) ETA-window card

Required rows:

- ETA claim class
- earliest honest finish
- latest honest finish
- time basis for the lower bound
- time basis for the upper bound
- checkpoint dependencies if any
- publication audience if already shared

### 5) Forecast fragility card

Required rows:

- confidence grade
- leading fragility source
- whether recent speed is representative
- whether schedule/pause windows widen the estimate
- whether hidden preprocessing widens the estimate
- whether interruption restart risk widens the estimate
- whether source absence or lock risk blocks tighter claims

### 6) Blocked stronger claim card

Required rows:

- strongest blocked stronger finish sentence
- strongest blocked stronger ETA sentence
- missing event or fact that would unlock each one
- whether the stronger claim is impossible or merely premature

Examples:

- `Current evidence supports a broad finish window, but not a narrow ETA, because schedule pauses and rescan-triggered discovery still dominate.`
- `Work remains finishable after the locked-file barrier clears, but any time-bound finish claim is blocked until access returns.`
- `A bounded window survives for the current scope only; a whole-estate finish claim remains blocked by unresolved ghost-file risk.`
""")

write('docs/1568-completion-forecast-timeline-page-estimate-tightening-slip-and-no-forecast-events-interface-spec.md', """
# Completion forecast timeline page: estimate tightening, slip, and no-forecast events interface spec

## Purpose

Forecast quality changes over time.
The timeline page must answer:

> when did remaining work first become measurable, when did finishability become believable, when did the ETA window tighten or widen, and when did the product decide that no honest forecast remained?

## Core timeline rule

AnonSync must treat forecast changes as first-class events, not as stray comments inside progress or rescue history.

## Fixed event order

1. **Remaining-work-shaped event**
2. **First-finishability event**
3. **First-ETA-window or no-ETA event**
4. **Estimate-tightening or estimate-widening event**
5. **Slip / checkpoint-miss / no-forecast event**
6. **Requalification or close event**

### 1) Remaining-work-shaped event

Record:

- when remaining work first became explicit
- which basis established it
- whether the basis was direct or inferred
- who accepted it

### 2) First-finishability event

Record:

- first finishability grade
- strongest basis for it
- blockers still open at that time

### 3) First-ETA-window or no-ETA event

Record one of:

- first broad ETA window
- first bounded ETA window
- first checkpoint-based ETA window
- first `no honest ETA` verdict

### 4) Estimate-tightening or estimate-widening event

Record whenever:

- remaining-work basis improved or weakened
- schedule gates changed
- representative speed changed materially
- hidden preparation was discovered
- interruption or restart risk widened the window

### 5) Slip / checkpoint-miss / no-forecast event

Record whenever:

- a published window was missed
- a checkpoint-critical date passed
- a live blocker invalidated the estimate
- the product downgraded to `no honest forecast`

### 6) Requalification or close event

Record whenever:

- fresh evidence restored forecast confidence
- a reroute produced a new estimate
- the work finished and the final forecast posture closed

Hard rule:

Forecast history may not rewrite missed windows out of existence.
A slipped or withdrawn estimate remains part of lineage.
""")

write('docs/1569-completion-forecast-lineage-receipt-page-forecast-basis-finishability-grade-and-blocked-stronger-sentences-interface-spec.md', """
# Completion forecast lineage receipt page: forecast basis, finishability grade, and blocked stronger sentences interface spec

## Purpose

Later operators need one durable receipt that says:

> what finish forecast was actually published, what remaining-work basis and finishability grade supported it, what ETA window survived honest review, and what stronger sentence stayed blocked at the time?

## Required receipt fields

- receipt id
- linked forecast id
- linked progress id
- linked work id
- linked claim id
- publication time
- forecast owner
- remaining-obligation basis summary
- finishability grade
- ETA claim class
- confidence grade
- deadline posture if any
- leading fragility source
- strongest allowed finish sentence
- strongest allowed ETA sentence
- strongest blocked stronger sentence
- next condition that would narrow the estimate most

## Supported receipt states

- `forecast-published`
- `forecast-revised`
- `forecast-widened`
- `forecast-withdrawn`
- `no-honest-forecast-published`
- `forecast-closed-on-completion`

## Hard rules

- A receipt may not publish a point ETA.
- A receipt may not claim a bounded window without both lower and upper bound.
- If `no-honest-forecast-published` is the state, the receipt must still preserve what weaker sentence survived.
- If a forecast is widened or withdrawn later, the earlier receipt remains visible in lineage.

## Example strongest sentences

Allowed:

- `The current route is finishable with a broad window, but a tighter ETA remains blocked by scheduled pauses and hidden preprocessing.`
- `Work is progressing and appears finishable after the next checkpoint, yet no narrow forecast is currently honest.`

Blocked:

- `Completion by 14:00 is assured.`
- `Current transfer speed implies a reliable finish time.`
- `Because progress exists, the deadline will be met.`
""")

prepend('README.md', """
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
""")

prepend('docs/00-status.md', """
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
""")

prepend('docs/10-resilio-sync-evaluation.md', """
## Revision addendum — Resilio finish-forecast and ETA-confidence evaluation after rev0403

Another current official Resilio pass still supports the same tightened judgment:

- **borrow Resilio's forecast ingredients and candor**
- **do not clone Resilio's finishability and ETA-confidence contract**

This time the key evidence cluster is:

- `Performance overview` still gives operators short real-time windows — 1 minute, 10 minutes, and 1 hour — with per-peer speeds, latency, disk load, and queue depth, which are useful observations but not a finish contract.
- `How soon does synchronization start?` still says detection can be immediate through filesystem notifications or delayed until scheduled rescan every 600 seconds and on start, and that `folder_rescan_interval = 0` disables rescans even on restart.
- `Running Sync on schedule` still says paused hours stop ordinary upload/download but do not stop zero-sized-file sync, deletion propagation, and rescanning/indexing.
- `Power user preferences` still exposes forecast-shaping settings such as `direct_torrent_enabled`, `prioritize_initial_indexing`, `parallel_indexing`, `recheck_locked_files_interval`, and `folder_rescan_interval`.
- `Some internal tasks are taking time to complete` still says hidden work like checking blocks, deduplication copy, hashing, merging, scanning, reading, and writing can consume time without yet proving final completion is near.
- `When a file changes, does Resilio Sync transfer the entire file again, or just the part that's changed?` still says only changed pieces are normally transferred, but shifted changes can force a whole-file re-sync unless Business-only delta applies.
- `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time` and `Locked files` still show blocker classes that can destroy narrow ETA confidence even while activity or prior progress exists.

So current Resilio still deserves credit for exposing many honest forecast ingredients.
But it still does not own one operator-facing answer to:

> given current progress truth, what honestly remains, is this route finishable, what ETA window survives review, and when is `no honest forecast yet` the right sentence?

That is why this pass again strengthens the non-clone line.
""")

prepend('docs/11-resilio-borrow-line-and-non-clone-scorecard.md', """
## Addendum after rev0403 — why finishability and ETA confidence now sit on the non-clone side

Resilio still earns credit for exposing many useful forecast ingredients.
Those stay on the **borrow** side.

What stays on the **do not clone** side is the forecast contract:

- current surfaces still show short-window motion and throughput, but not one explicit finishability object
- rescans, scheduler pauses, preprocessing, restart-from-start risk, and blocker recheck windows still have to be mentally integrated by the operator
- partial-transfer efficiency and whole-file-rework risk still coexist without one forecast-confidence surface
- `no honest forecast yet` still has to be inferred rather than rendered as a first-class product truth

So the line hardens again:

- **borrow forecast ingredients and operational candor**
- **do not clone a product shape where finishability and ETA-confidence truth live outside the operator workspace**
""")

prepend('docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md', """
## Addendum after rev0403 — new clone-veto test for finishability and ETA truth

A borrowed interface fails the clone test if it can show that work is progressing yet still cannot tell the operator what honest finish claim survives.
The new veto questions are:

- can the operator distinguish remaining work from recent speed?
- can the interface separate finishability grade from ETA window and from deadline posture?
- can the product publish `no honest forecast yet` without pretending failure or inventing a theatrical ETA?
- can schedule pauses, rescans, hidden preprocessing, lock/source risk, and restart-from-start risk visibly widen the estimate?
- can a slipped or withdrawn forecast stay in lineage instead of being overwritten by the latest hopeful number?

If the answer is no, the interface is still cloning Resilio's scattered forecast shape too closely.
""")

prepend('docs/20-product-direction.md', """
## Product-direction addendum after rev0403 — net progress must graduate into honest finish forecast

AnonSync should not let real progress masquerade as a reliable finish estimate.
The product direction is now explicit:

- **completion forecast is first-class**
- **remaining work, finishability, ETA window, confidence grade, and deadline posture remain separate**
- **no-honest-forecast is a valid product truth rather than an operator embarrassment**
- **hidden preprocessing, discovery lag, schedule pauses, and interruption/rework risk must widen forecast confidence explicitly**
- **every meaningful forecast needs one receipt preserving remaining-work basis, finishability grade, ETA class, fragility source, and blocked stronger sentence**

That means future interface work should keep one stable family for:

- shaping remaining work from proved progress
- evaluating finishability under the current route
- publishing broad, bounded, or checkpoint-based ETA windows
- downgrading honestly to no forecast when evidence is too fragile
- recording slip, widening, withdrawal, and requalification events
- durable forecast receipts for later staffing, publication, and deadline review

The product should never force the operator to infer finishability from throughput graphs, short observation windows, or wishful trend extrapolation alone.
""")

prepend('docs/sources.md', """
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
""")
