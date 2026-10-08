from pathlib import Path

root = Path(__file__).resolve().parent

def prepend(path: str, text: str):
    p = root / path
    old = p.read_text(encoding='utf-8')
    p.write_text(text.strip() + '\n\n' + old, encoding='utf-8')

def write(path: str, text: str):
    p = root / path
    p.write_text(text.strip() + '\n', encoding='utf-8')

readme_add = '''## Revision addendum after rev0399 — decision portfolio, prioritization, and dispatch truth

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
'''

status_add = '''## Revision addendum — status shift toward decision portfolios after rev0399

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
'''

resilio_eval_add = '''## Revision addendum — Resilio decision-portfolio, prioritization, dispatch, and starvation evaluation after rev0399

Another current official Resilio pass still supports the same tightened judgment:

- **borrow Resilio's attention signals and troubleshooting candor**
- **do not clone Resilio's cross-case prioritization and dispatch contract**

This time the key evidence cluster is:

- `Sync Main View (Desktop)` still gives operators filters for connected/disconnected shares, search, configurable columns, a 30-day History lane, peer/activity status, and a bell for approval requests or other notifications.
- `How do I perform a search in Sync?` still shows that search exists across folders/files, connected devices, and users.
- `Core warnings` and the `Errors and warnings` / `Errors & Troubleshooting` category pages still cluster many issue families and warning classes as separate attention surfaces.
- `Some internal tasks are taking time to complete` still preserves a real `watch and wait` posture because the product may recover on its own while background work proceeds.
- `Performance overview` still exposes short-window graphs that help an operator notice pressure without becoming a dispatch queue.
- deeper artifact pages like `Collecting debug logs manually`, `Collecting crash reports, mini-dumps and core dumps`, and `Measuring network performance with iperf3` still define heavier investigative rungs that can compete for scarce attention.

So current Resilio still deserves credit for exposing many useful attention signals.
But it still does not own one operator-facing answer to:

> when several candidate decisions are all real enough to matter, which one actually goes now, which one is deliberately held, what preemption is justified, and which watch-only item is quietly aging toward starvation?

That is why this pass again strengthens the non-clone line.
'''

scorecard_add = '''## Addendum after rev0399 — why decision portfolios now sit on the non-clone side

Resilio still earns credit for exposing many useful attention signals.
Those stay on the **borrow** side.

What stays on the **do not clone** side is the portfolio contract:

- current surfaces still show many active things, but not one explicit cross-case prioritization object
- notification presence, warning presence, and activity presence still do too much work as proxy priority
- `watch and wait` items still rely too much on memory and periodic checking rather than an explicit starvation guard
- heavier investigative rungs can compete for attention without one canonical dispatch proof showing why they won or lost

So the line hardens again:

- **borrow attention signals and troubleshooting candor**
- **do not clone a product shape where dispatch order and starvation truth live outside the operator workspace**
'''

clone_veto_add = '''## Addendum after rev0399 — new clone-veto test for decision portfolio truth

A borrowed interface fails the clone test if it can threshold one case honestly but still cannot rank several live candidates without private judgment and memory.
The new veto questions are:

- can the operator see a candidate set rather than only one selected item?
- can the interface separate urgency, blast radius, reversibility, evidence freshness, and starvation risk?
- can an item be action-ready while still losing dispatch honestly?
- can the product show preemption and the displaced work explicitly?
- can watch-only items age toward a visible starvation breach instead of silently disappearing?

If the answer is no, the interface is still cloning Resilio's scattered prioritization shape too closely.
'''

product_add = '''## Product-direction addendum after rev0399 — individual decision truth must roll up into a visible portfolio

AnonSync should not let several threshold-cleared decisions masquerade as a self-ordering queue.
The product direction is now explicit:

- **decision portfolios are first-class**
- **action-readiness, urgency, dispatch priority, and starvation risk remain separate**
- **attention budget is a product truth rather than a private staffing assumption**
- **preemption and hold decisions must preserve the losing work explicitly**
- **every meaningful dispatch needs one receipt preserving why this item won now, what stayed held, and what will reopen the ordering later**

That means future interface work should keep one stable family for:

- cross-case candidate-set shaping
- lane assignment across now / next / later / watch / hold / frozen
- priority-factor comparison and explicit tie-breaking
- starvation and evidence-decay guardrails
- dispatch proofs and preemption records
- durable portfolio receipts for later review, challenge, and capacity planning

The product should never force the operator to turn a pile of live cases into dispatch order purely through inbox motion, memory, and nerve.
'''

sources_add = '''## rev0400 source set — decision portfolios, prioritization, dispatch, and starvation truth

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
'''

write('docs/1540-resilio-decision-portfolio-prioritization-dispatch-and-starvation-fragmentation-evaluation.md', '''# Resilio decision portfolio, prioritization, dispatch, and starvation fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- synthesize several evidence packets into one integrated claim
- turn that claim into one honest decision charter
- separate allowed action from blocked stronger action
- preserve residual uncertainty and escalation posture

What it still lacked was the next ordinary operator answer:

> when several candidate decisions are all real enough to matter, which one actually goes now, which one is deliberately held, and what watch-only item is quietly aging toward starvation?

That is the seam this pass locks.
A product that can threshold one case honestly but cannot prioritize several at once still leaves too much truth in inbox motion, remembered annoyance, and analyst courage.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose many useful attention surfaces, but mostly as separate signals rather than one cross-case dispatch workspace:

- `Sync Main View (Desktop)` still gives the operator filters for connected and disconnected shares, search, configurable columns, a 30-day History lane, visible peer/activity status, and a notification bell for approval requests or other events.
- `How do I perform a search in Sync?` still shows that search spans folders/files, connected devices, and users.
- `Core warnings` still clusters several warning families that may all matter at once.
- `Errors and warnings` and the broader `Errors & Troubleshooting` category still present issue families as separate article groups.
- `Some internal tasks are taking time to complete` still makes `watch and wait` a real posture because background operations may recover without immediate heavy intervention.
- `Performance overview` still exposes 1-minute, 10-minute, and 1-hour graphs that can influence urgency without becoming a dispatch rule.
- deeper artifact pages like `Collecting debug logs manually`, `Collecting crash reports, mini-dumps and core dumps`, and `Measuring network performance with iperf3` still define heavier investigative rungs that can compete for scarce attention.

## What current Resilio still gets right

### 1) It gives the operator many useful attention signals

Notifications, warnings, search, activity state, history, and graphs are all real clues.
That is worth borrowing.

### 2) It preserves that not every live thing deserves the same response

Some issues may self-recover.
Some deserve a watch posture.
Some call for immediate action.
Some justify heavy evidence capture.
That difference matters.

### 3) It keeps the practical surfaces lightweight

Filters, search, history, and warning pages are fast to inspect.
That operational lightness is useful.

## Where current Resilio still fragments the operator answer

### A) Priority still lives mostly in the reader's head

The product and docs show many things that may matter, but still do not compile them into one durable answer about which item wins dispatch right now.

### B) Signal presence is not the same as dispatch order

A lit bell, a warning, a graph spike, or a stalled queue may all feel urgent.
But current Resilio surfaces do not turn those signals into one explicit priority basis that can be reviewed later.

### C) Watch-only work can quietly starve

Resilio does acknowledge that some states can recover on their own.
But the operator still has to remember that a watch item exists, how long it has been waiting, and when patience has become neglect.

### D) Heavy capture can compete with lighter work without one portfolio explanation

Debug logs, crash artifacts, and iperf runs are real work.
Current Resilio pages explain how to perform them, but not one portfolio rule for when they should displace lighter or safer work already waiting.

### E) Preemption is more implicit than explicit

The operator can always change their mind.
But current Resilio surfaces do not preserve one first-class statement of what got displaced and why.

## What AnonSync should borrow

- many useful attention signals
- lightweight scanning surfaces
- candid acknowledgment that some issues deserve monitoring rather than immediate mutation
- practical investigative ladders

## What AnonSync should not clone

AnonSync should not clone a world where the operator must build dispatch order privately from separate warnings, bells, searches, graphs, history, and support articles.
It should not leave the following questions scattered across UI fragments and KB pages:

- which candidate decision goes now?
- which candidate is real but deliberately held?
- what factor actually made one item outrank another?
- what attention budget constrained the choice?
- what watch item is aging toward starvation?
- what exactly was preempted when a hotter case arrived?

## Product requirement extracted from this evaluation

AnonSync should own one stable page family for **decision portfolios**.
That family should make it ordinary to publish:

- candidate set
- priority factors
- explicit attention budget
- lane assignment across now / next / later / watch / hold / frozen
- dispatch winner and displaced work
- starvation guard
- preemption and reevaluation triggers

## Bottom line

Current Resilio still deserves credit for exposing many useful attention signals and practical troubleshooting surfaces.
But it still does not own one operator-facing answer to:

> when several live decisions all matter, what actually goes now, what stays held, and what waiting item is about to be forgotten?

That is why this seam belongs on the non-clone side.
''')

write('docs/1541-decision-portfolio-contract-sheet-page-candidate-set-urgency-lanes-and-attention-budget-interface-spec.md', '''# Decision portfolio contract sheet page: candidate set, urgency lanes, and attention budget interface spec

## Purpose

Once several decision charters are live at the same time, the operator still needs one page that answers:

> what exact candidate set are we prioritizing, what attention budget do we really have, and which lane does each item belong in right now?

## Core decision

AnonSync must expose one first-class **Decision portfolio contract sheet** whenever two or more live decision charters compete for attention, execution, or monitoring.

## Fixed page order

1. **Portfolio header**
2. **Candidate-set card**
3. **Priority-factors card**
4. **Attention-budget card**
5. **Lane-assignment card**
6. **Starvation-guard card**
7. **Dispatch sentence**

### 1) Portfolio header

Show:

- portfolio id
- owning operator or team
- portfolio scope
- current portfolio posture
- total live candidates
- number in `now`
- number in `watch`
- number nearing starvation
- current dispatch winner if one exists

Supported `portfolio_posture` values:

- `portfolio-opened`
- `candidate-scoring-in-progress`
- `lane-mapping-in-progress`
- `dispatch-ready`
- `watch-heavy`
- `capacity-blocked`
- `frozen`
- `superseded`

Hard rule:

The header may not imply healthy control merely because one winner exists.
If three items are starving in `watch`, the header must still show that pressure.

### 2) Candidate-set card

Required rows:

- candidate decision id
- candidate title
- current claim ceiling
- allowed next verb
- current harm if delayed
- current harm if done too early
- affected scope
- dependency or blocker note

Supported `candidate_class` values:

- `bounded-repair`
- `monitoring-posture`
- `supplement-ask`
- `heavy-capture`
- `publication-decision`
- `freeze-or-halt`
- `external-handoff`

Hard rule:

Every candidate must remain visible even if it loses dispatch.
Hidden losers are not allowed.

### 3) Priority-factors card

Required rows:

- urgency
- blast radius
- reversibility
- evidence freshness risk
- watch-starvation risk
- dependency pressure
- operator-cost or burden
- benefit of dispatch now
- cost of not choosing now

Supported `priority_factor_grade` values:

- `low`
- `moderate`
- `high`
- `critical`
- `unknown`

Hard rule:

The card may not collapse all pressure into one synthetic score without still showing factor-by-factor grades.

### 4) Attention-budget card

Required rows:

- available operator budget
- number of safe concurrent actions
- maximum heavy investigations allowed
- watch capacity
- frozen capacity classes
- reevaluation cadence

Supported `attention_budget_class` values:

- `one-major-action-only`
- `many-light-checks-few-actions`
- `watch-only-for-now`
- `heavy-capture-limited`
- `frozen-by-external-dependency`

Hard rule:

Attention budget must be explicit.
The product may not pretend all action-ready items can proceed simultaneously unless the budget says so.

### 5) Lane-assignment card

Render one row per candidate.
Required fields:

- assigned lane
- reason for lane choice
- what would promote it
- what would demote it
- maximum tolerated age in lane

Supported `portfolio_lane` values:

- `now`
- `next`
- `later`
- `watch`
- `hold`
- `frozen`
- `done-or-exited`

Hard rule:

`watch` and `hold` are not synonyms.
`watch` means active observation is still valuable.
`hold` means the portfolio is deliberately not spending attention there yet.

### 6) Starvation-guard card

Required rows:

- candidates nearing starvation
- why they are not already promoted
- maximum allowed silent age
- automatic promotion trigger
- automatic forced-review trigger

Supported `starvation_guard_posture` values:

- `healthy`
- `aging`
- `near-breach`
- `breached`
- `unknown-because-review-missed`

Hard rule:

A portfolio with any `breached` candidate may not describe itself as fully controlled.

### 7) Dispatch sentence

Render exactly two lines:

- **Dispatch now**
- **Most important held-or-watching item and why it is not going now**

Hard rule:

The second line must name one losing item explicitly.
A portfolio without a visible losing item is not telling the truth about prioritization.
''')

write('docs/1542-prioritization-review-page-now-next-later-watch-and-preemption-routes-interface-spec.md', '''# Prioritization review page: now, next, later, watch, and preemption routes interface spec

## Purpose

The contract sheet defines the candidate set.
The operator still needs one review page that compares live lanes side by side and answers:

> which candidate really belongs in `now`, which candidates are safely held, and what exact factor would justify preempting the current winner?

## Review layout

1. **Candidate-comparison strip**
2. **Lane-threshold panel**
3. **Attention-budget panel**
4. **Preemption panel**
5. **Starvation-risk panel**
6. **Tie-break panel**
7. **Review verdict**

### 1) Candidate-comparison strip

Show one card per candidate with:

- current lane
- dispatch eligibility
- dominant urgency factor
- dominant blocker
- reversibility
- scope size
- evidence freshness posture
- starvation age

Hard rule:

Non-selected candidates may not be hidden once a winner is chosen.
The review must show why they lost.

### 2) Lane-threshold panel

For each lane, show:

- why the candidate qualifies for that lane
- what keeps it from a stronger lane
- what would promote it
- what would safely demote it

Supported `lane_failure_class` values:

- `lower-urgency-than-competing-work`
- `dependency-not-ready`
- `budget-exhausted`
- `waiting-for-observation`
- `heavy-burden-not-yet-justified`
- `evidence-too-stale`
- `scope-too-wide-for-now`

Hard rule:

`not selected for now` must name the failure class.
Silence is not explanation.

### 3) Attention-budget panel

Required rows:

- current active slots
- remaining safe slots
- heavy-investigation slots
- monitor slots
- what dispatching this candidate consumes
- what work that would crowd out

Hard rule:

If dispatch consumes the last safe slot, the panel must say which next-best item is displaced.

### 4) Preemption panel

Required rows:

- current winner
- possible preemptor
- evidence or event needed for preemption
- displaced work if preemption occurs
- safe handoff or stop requirement

Supported `preemption_posture` values:

- `no-preemption-basis`
- `preemption-possible`
- `preemption-armed`
- `preemption-fired`
- `preemption-blocked-by-safe-stop`

Hard rule:

Preemption may not be implied only by tone or urgency adjectives.
The displaced work and stop boundary must be explicit.

### 5) Starvation-risk panel

Required rows:

- longest-waiting non-now candidate
- starvation risk grade
- why still not promoted
- earliest forced-review time
- what stronger sentence is lost if it keeps aging

Supported `starvation_risk_grade` values:

- `low`
- `moderate`
- `high`
- `breach-imminent`
- `breached`

Hard rule:

Any candidate at `breach-imminent` or `breached` must appear in the review verdict even if it still loses dispatch.

### 6) Tie-break panel

Required rows:

- nearest competing pair
- shared strengths
- decisive difference
- why that difference matters more right now
- what fact would reverse the tie-break

Hard rule:

When two candidates are close, the decisive difference must be visible.
`Feels worse` is not enough.

### 7) Review verdict

Render:

- dispatched candidate
- why it beats the nearest alternative
- most important held candidate
- preemption trigger if the ordering flips
''')

write('docs/1543-dispatch-proof-page-selected-work-held-work-and-starvation-guard-interface-spec.md', '''# Dispatch proof page: selected work, held work, and starvation guard interface spec

## Purpose

After review, the operator still needs one proof page that says:

> what exactly are we dispatching now, why is that the strongest honest ordering, what losing work remains live, and how will we know if that held work has been neglected too long?

## Proof sections

1. **Proof headline**
2. **Selected-work block**
3. **Priority-basis block**
4. **Held-work block**
5. **Starvation-guard block**
6. **Preemption-and-reopen block**

### 1) Proof headline

Show:

- selected candidate
- lane granted
- dispatch grade
- attention budget consumed
- highest-risk losing candidate

Supported `dispatch_grade` values:

- `dispatch-now-grade`
- `dispatch-next-grade`
- `watch-grade`
- `hold-grade`
- `frozen-grade`

### 2) Selected-work block

Required rows:

- selected candidate id
- exact work authorized now
- why now rather than later
- safe concurrency bound
- witnesses required after dispatch
- maximum claim this dispatch does not authorize

Hard rule:

A dispatch proof must say what the selection does **not** imply about the candidates that lost.

### 3) Priority-basis block

Required rows:

- decisive priority factors
- nearest competing candidate
- decisive tie-break
- budget effect
- whether the choice is robust-to-delay or fragile-to-delay

### 4) Held-work block

Required rows:

- held candidate ids
- current lane for each
- why each lost now
- what would promote each
- what evidence or time event would weaken the current ordering

Hard rule:

Held work cannot be summarized only as `remaining backlog`.
At least the most consequential held item must be described concretely.

### 5) Starvation-guard block

Required rows:

- item with the highest starvation risk
- current age in lane
- allowed remaining age
- forced-review trigger
- what sentence is no longer safe if the breach occurs

Hard rule:

A starvation guard must expire or trigger on an explicit basis; silent indefinite watch is not allowed.

### 6) Preemption-and-reopen block

Required rows:

- current preemption posture
- candidate most likely to preempt
- event or evidence needed to fire preemption
- safe stop or handoff boundary
- next portfolio owner on reopen

Hard rule:

Every dispatch proof must preserve how the ordering can change later without pretending today's winner was eternal truth.
''')

write('docs/1544-decision-portfolio-timeline-page-promotion-deferral-preemption-and-stale-watch-events-interface-spec.md', '''# Decision portfolio timeline page: promotion, deferral, preemption, and stale-watch events interface spec

## Purpose

Portfolio ordering is rarely one moment.
The operator needs a timeline that answers:

> when did a candidate rise, when was it held back, when did another item preempt it, and when did a watch posture turn into neglect?

## Timeline event types

Supported `portfolio_event_type` values:

- `candidate-added`
- `candidate-removed`
- `promoted-to-now`
- `demoted-to-later`
- `entered-watch`
- `hold-imposed`
- `budget-exhausted`
- `dispatch-fired`
- `preemption-armed`
- `preemption-fired`
- `watch-aging`
- `starvation-breach`
- `forced-review-fired`
- `portfolio-frozen`
- `portfolio-reopened`

## Required columns

- event time
- candidate id
- prior lane
- new lane
- triggering factor or evidence
- displaced candidate if any
- attention-budget delta
- stronger sentence gained or lost
- owner after event

## Hard rules

### Promotion and demotion must name the cause

A transition from `watch` to `now`, or from `now` to `hold`, must name the exact evidence, deadline, capacity shift, or competing pressure that changed the lane.

### Preemption must preserve the losing work

If one candidate preempts another, the timeline must show:

- what was displaced
- whether work stopped, handed off, or safely paused
- what stronger sentence the displaced item lost

### Starvation breach must weaken something concrete

A starvation event must say which previous comfort sentence failed.
For example, `safe to keep watching` must become false in a named way.
''')

write('docs/1545-decision-portfolio-lineage-receipt-page-priority-basis-attention-budget-and-blocked-work-interface-spec.md', '''# Decision portfolio lineage receipt page: priority basis, attention budget, and blocked work interface spec

## Purpose

Later operators need one receipt that answers:

> what portfolio choice was made, why did this item win dispatch, what work remained held, and what starvation or preemption risk stayed live at the time?

## Receipt layout

1. **Portfolio identity**
2. **Dispatch basis**
3. **Held-work posture**
4. **Attention budget**
5. **Starvation and preemption risk**
6. **Expiry and reevaluation basis**

### 1) Portfolio identity

Required fields:

- portfolio id
- portfolio scope
- dispatch owner
- receipt issue time
- selected candidate id

### 2) Dispatch basis

Required fields:

- selected lane
- decisive priority factors
- nearest losing candidate
- decisive tie-break
- exact work authorized now

### 3) Held-work posture

Required fields:

- held candidate ids
- highest-risk held candidate
- reason still held
- promotion trigger for that item

### 4) Attention budget

Required fields:

- budget class
- slots consumed
- slots remaining
- displaced work if any

### 5) Starvation and preemption risk

Required fields:

- highest starvation risk grade
- forced-review trigger
- preemption posture
- likely preemptor if known

### 6) Expiry and reevaluation basis

Required fields:

- next portfolio review time or trigger
- stale-basis trigger
- starvation-breach trigger
- successor portfolio id if superseded

## Hard rule

A lineage receipt must preserve the losing work explicitly.
Winning dispatch does not retroactively prove the losing candidates were unimportant.
''')

prepend('README.md', readme_add)
prepend('docs/00-status.md', status_add)
prepend('docs/10-resilio-sync-evaluation.md', resilio_eval_add)
prepend('docs/11-resilio-borrow-line-and-non-clone-scorecard.md', scorecard_add)
prepend('docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md', clone_veto_add)
prepend('docs/20-product-direction.md', product_add)
prepend('docs/sources.md', sources_add)
