from pathlib import Path

root = Path(__file__).resolve().parent

def prepend(path: str, text: str):
    p = root / path
    original = p.read_text()
    p.write_text(text.rstrip() + "\n\n" + original)

def write(path: str, text: str):
    p = root / path
    p.write_text(text.rstrip() + "\n")

readme_add = '''## Revision addendum after rev0393 — doctrine applicability, fact-pattern routing, and distinguishing-question truth

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
'''

status_add = '''## Revision addendum — status shift toward doctrine applicability and fact-pattern routing truth after rev0393

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
'''

resilio_eval_add = '''## Revision addendum — Resilio doctrine applicability, fact-pattern routing, and distinguishing-question evaluation after rev0393

Another current official Resilio pass still supports the same tightened judgment:

- **borrow Resilio's symptom catalog, search affordances, and troubleshooting candor**
- **do not clone Resilio's doctrine-application contract**

This time the key evidence cluster is:

- `How do I perform a search in Sync?` still says Sync search can find folders and shared files, connected devices, and users, but it remains literal search rather than a doctrine-applicability workspace
- `Sync Main View (Desktop)` still exposes peer counts, statuses, notifications, search, and History, which are real routing breadcrumbs
- `My files don't sync` still tells operators to inspect peers, Status warnings, History, and peer queues before choosing a next step
- `Errors & Troubleshooting` and `Errors and warnings` still organize symptom families as article lists rather than one fact-pattern router
- `Peers aren't connecting`, `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time`, `"Time difference" error`, `Database error`, and `Some internal tasks are taking time to complete` still each describe plausible but overlapping interpretations of `sync is not proceeding as expected`
- `Core warnings` still packs very different warning families into one article set, which is useful but still leaves doctrine application to the operator
- `Collecting debug logs manually` still says direct technical support is unavailable for Sync v3 and routes users toward forum/Help Center when local article comparison is not enough

So current Resilio still deserves credit for exposing many useful routing breadcrumbs.
But it still does not own one operator-facing answer to:

> given the facts we have now, which doctrine actually governs this case, which lookalike routes remain plausible, and what one more fact would distinguish them most efficiently?

That is why this pass again strengthens the non-clone line.
'''

scorecard_add = '''## Addendum after rev0393 — why doctrine applicability now sits on the non-clone side

Resilio still earns credit for search, warning surfaces, and symptom-specific troubleshooting.
Those stay on the **borrow** side.

What stays on the **do not clone** side is the route-selection contract:

- a new case still has to be compared against several warning pages and troubleshooting trees manually
- search still helps *find* candidate pages but does not publish applicability weight
- peer/status/history clues still require operator synthesis rather than one fact-pattern router
- support/forum routing still becomes the fallback when doctrine application is ambiguous

So the line hardens again:

- **borrow search, warning candor, and symptom breadcrumbs**
- **do not clone a product shape where applicability and the next best distinguishing question live outside the operator workspace**
'''

clone_veto_add = '''## Addendum after rev0393 — new clone-veto test for doctrine applicability

A borrowed interface fails the clone test if it can publish precedent but not apply it cleanly.
The new veto questions are:

- can the operator compare multiple candidate precedents against one fresh fact pattern in one workspace?
- can the operator separate symptom similarity from governing-doctrine fit?
- can the interface publish explicit disqualifiers and unresolved differentiators?
- can the product name the **next best distinguishing question** instead of dumping the operator into article search?
- can later facts visibly reverse the route without erasing the earlier ambiguity?

If the answer is no, the interface is still cloning Resilio's scattered doctrine-application shape too closely.
'''

product_add = '''## Product-direction addendum after rev0393 — doctrine is not self-applying

AnonSync should not let published doctrine masquerade as automatic diagnosis.
The product direction is now explicit:

- **doctrine applicability is first-class**
- **symptom match, fact-pattern match, world match, and governing-doctrine match remain separate**
- **the next best distinguishing question is a product obligation**
- **route reversals become durable timeline events**
- **every meaningful applicability sentence needs one receipt preserving candidate precedents, open gaps, and blocked overclaims**

That means future interface work should keep one stable family for:

- case intake against candidate precedents
- lookalike-route comparison
- discriminating-question selection
- governing-doctrine proof or temporary hold
- durable applicability receipts for later operators

The product should never force the operator to infer applicability by manually comparing warning pages, history hints, and remembered forum threads alone.
'''

sources_add = '''## rev0394 source set — doctrine applicability, fact-pattern routing, and distinguishing-question truth

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
'''

write('docs/1504-resilio-doctrine-applicability-fact-pattern-routing-and-distinguishing-question-fragmentation-evaluation.md', '''# Resilio doctrine applicability, fact-pattern routing, and distinguishing-question fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- resolve a contested completion claim
- promote a ruling into precedent
- distinguish or overrule doctrine later

What it still lacked was the next ordinary operator answer:

> given this fresh case, which doctrine actually governs it, which lookalike routes remain plausible, and what one more fact would collapse the ambiguity fastest?

That is the seam this pass locks.
Published doctrine is not self-applying.
Search is not the same as applicability.
Warning titles are not the same as fact-pattern matches.
A useful operator product must help route the case, not merely list possible articles.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose many useful routing breadcrumbs, but mostly as separate pages and surfaces:

- `How do I perform a search in Sync?` still says Sync can search folders and shared files, connected devices, and users in UI.
- `Sync Main View (Desktop)` still exposes search, peer counts, statuses, notifications, and a 30-day History lane.
- `My files don't sync` still tells operators to inspect peers, Status warnings, History, and peer queues before choosing a next step.
- `Errors & Troubleshooting` and `Errors and warnings` still organize symptom families mainly as article lists.
- `Peers aren't connecting` still routes one family through multicast, NIC, router, firewall, relay, and predefined-host checks.
- `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time` still describes a selective-sync / source-availability ghost-file style route.
- `"Time difference" error` still describes timestamp/timezone skew as another distinct route.
- `Database error` still escalates through restart, reconnect, and all-peer re-add.
- `Some internal tasks are taking time to complete` still says the issue may self-recover and may merely reflect temporary load.
- `Core warnings` still clusters many unrelated warning families under one surface.
- `Collecting debug logs manually` still says direct technical support is unavailable for Sync v3 and routes users toward forum/Help Center.

## What current Resilio still gets right

### 1) It preserves many real routing breadcrumbs

Resilio does not leave the operator completely blind.
Search, warning links, peer counts, history, and queue inspection are real breadcrumbs.
That is worth borrowing.

### 2) It keeps different symptom families distinct

Connectivity, ghost-file/source absence, time skew, database corruption, and temporary internal backlog are not flattened into one pseudo-cause.
That honesty matters.

### 3) It makes escalation visible

When local interpretation is not enough, Resilio does say when logs or deeper troubleshooting are needed.
That is better than an opaque failure.

## Where current Resilio still fragments the operator answer

### A) Search finds pages, but does not publish applicability weight

Literal search can help the operator find relevant folders, files, devices, users, or pages.
What it still does not do is answer whether one doctrine actually governs the current case better than the lookalikes.

### B) Symptom families still require manual article comparison

`My files don't sync` is an umbrella symptom.
So are some warning and history surfaces.
Current Resilio still leaves the operator to compare several candidate warning articles and troubleshooting trees manually.

### C) The next best distinguishing question is not first-class

A strong operator product should tell the operator what one more fact would most reduce ambiguity:

- are peers connected or not?
- is the clock wrong?
- is there a source peer for the missing bytes?
- is the problem local database state?
- is the system simply under temporary heavy load?

Current Resilio offers the ingredients, but not a canonical ranked discriminator object.

### D) Route reversals are still mostly informal

An operator can first suspect connectivity, then later discover time skew or ghost-file conditions.
What current Resilio still does not give is one durable route-reversal record that preserves why the earlier route looked plausible and what fact overturned it.

## Hard product decision unlocked by this pass

AnonSync should not let doctrine application live in article search, warning memory, or support escalation folklore.
It should compile every serious fresh case into a first-class **doctrine applicability** object that separately expresses:

- observed symptom family
- material facts already known
- candidate precedents
- disqualifiers already present
- unresolved differentiators
- next best distinguishing question
- currently governing doctrine if any
- strongest blocked sentence while ambiguity remains

## Replacement line for AnonSync

Borrow from Resilio:

- search affordances that expose useful breadcrumbs
- symptom-specific warning pages that keep problem families distinct
- explicit troubleshooting hints about peers, history, warnings, and queues

Do not clone from Resilio:

- any workflow where search results masquerade as doctrine application
- any contract where the operator must compare warning pages manually to decide which route applies
- any interface where the next best distinguishing question is not product-owned
- any product shape where route reversals vanish into support folklore instead of becoming durable doctrine-application history

AnonSync should instead ship explicit pages for:

- doctrine applicability contract sheet
- fact-pattern routing review
- applicability proof
- applicability timeline
- applicability lineage receipt
''')

write('docs/1505-doctrine-applicability-contract-sheet-page-case-facts-candidate-precedents-and-missing-discriminators-interface-spec.md', '''# Doctrine applicability contract sheet page: case facts, candidate precedents, and missing discriminators interface spec

## Purpose

After the archive learned how to publish doctrine, it still needed one ordinary page for the next operator question:

> this new case resembles several older ones — which doctrine candidates are live, which facts already disqualify some of them, and what fact is still missing before we can safely route it?

## Core decision

AnonSync must expose one first-class **Doctrine applicability contract sheet** whenever a fresh case, warning cluster, or routed escalation is being matched against existing doctrine.

## Fixed page order

1. **Applicability header**
2. **Observed-facts card**
3. **Candidate-precedents card**
4. **Disqualifiers and gaps card**
5. **Next-best-question card**
6. **Temporary routing stance card**
7. **Decision sentence**

### 1) Applicability header

Show:

- applicability sheet id
- source case id
- current operator owner
- intake time
- current ambiguity class
- current strongest safe sentence
- current unsafe overclaim

Supported `ambiguity_class` values:

- `single-clear-route`
- `few-live-lookalikes`
- `many-live-lookalikes`
- `insufficient-facts`
- `evidence-contradiction`
- `route-reversal-pending`

Hard rule:

A new case may not jump directly from symptom text to governing doctrine without first naming the ambiguity posture.

### 2) Observed-facts card

Required rows:

- primary symptom summary
- known environment/world facts
- known peer/connectivity facts
- known time/state facts
- known history or warning facts
- known operator actions already attempted

Hard rule:

The page must separate **observed facts** from **inferred cause**.
Facts are the substrate for routing; doctrine fit cannot be built on blurred speculation.

### 3) Candidate-precedents card

For each candidate doctrine, show:

- doctrine id
- why it was surfaced
- fit class
- strongest safe claim if this candidate wins
- strongest disqualifying fact already present
- additional fact needed to confirm or reject it

Supported `fit_class` values:

- `governing-if-confirmed`
- `strong-lookalike`
- `possible-but-weak`
- `currently-disqualified`
- `historically-related-only`

Hard rule:

The sheet must support more than one candidate precedent at once.
The operator should not have to flip between doctrine receipts to compare fit.

### 4) Disqualifiers and gaps card

Required rows:

- facts that rule out candidates already
- facts that weaken but do not eliminate candidates
- facts still missing
- facts that would collapse the ambiguity fastest
- contradictions between current witnesses

Hard rule:

A missing fact is not the same as an adverse fact.
The page must keep uncertainty separate from disqualification.

### 5) Next-best-question card

Required rows:

- next best distinguishing question
- why this question has the highest decision value
- evidence channel needed to answer it
- who may answer it
- fallback question if unavailable

Hard rule:

The product must publish one ranked next question whenever routing remains ambiguous.
`Read more docs` is not an acceptable substitute.

### 6) Temporary routing stance card

Supported `temporary_routing_stance` values:

- `apply-governing-doctrine-now`
- `treat-as-provisional-lookalike`
- `hold-for-next-fact`
- `route-to-fact-capture`
- `route-to-human-adjudication`
- `route-reversal-under-review`

Required rows:

- temporary routing stance
- what action is allowed under that stance
- what action is blocked under that stance
- what stronger sentence remains blocked
- expiry or rereview boundary

Hard rule:

Temporary stance must bound action.
Ambiguous routing may not silently authorize the same actions as a confirmed governing doctrine.

### 7) Decision sentence

Render one sentence only:

- `Given current facts, this case is [temporary_routing_stance] with [ambiguity_class]; leading candidate doctrine is [candidate] and the next best distinguishing question is [question].`

## Required interactions

- **Add observed fact**
- **Attach candidate precedent**
- **Disqualify candidate**
- **Promote question to primary discriminator**
- **Shift temporary routing stance**

## Failure state

If no candidate doctrine exists yet, show:

- `No doctrine candidate surfaced yet. This case remains unclassified and requires fresh fact-pattern work before any doctrine claim is safe.`
''')

write('docs/1506-fact-pattern-routing-review-page-symptom-lookalikes-disqualifiers-and-next-best-question-interface-spec.md', '''# Fact-pattern routing review page: symptom lookalikes, disqualifiers, and next best question interface spec

## Purpose

After the archive learned how to stage candidate doctrine, it still needed one ordinary workspace for the next harder question:

> among these lookalike routes, which one actually deserves to govern this case, which ones are still alive only because we lack one fact, and what question should we ask next instead of guessing?

## Core decision

AnonSync must expose one first-class **Fact-pattern routing review** page whenever multiple lookalike doctrines or warning families are still plausibly competing for the same case.

## Fixed page order

1. **Review header**
2. **Lookalike-stack card**
3. **Discriminator matrix card**
4. **Evidence-channel card**
5. **Route-reversal risk card**
6. **Proposed governing route card**
7. **Decision sentence**

### 1) Review header

Show:

- routing review id
- active case id
- number of live lookalike routes
- review owner
- current routing risk
- strongest currently safe sentence

Supported `routing_risk` values:

- `low-misroute-risk`
- `moderate-misroute-risk`
- `high-misroute-risk`
- `unknown-routing-risk`

### 2) Lookalike-stack card

For each active lookalike route, show:

- route name
- doctrine or article family behind it
- strongest fact supporting it
- strongest fact against it
- current fit class
- harm if misapplied

Hard rule:

The page must support simultaneous review of several lookalike routes.
Operators should not have to compare them serially in memory.

### 3) Discriminator matrix card

Required rows:

- key distinguishing facts by route
- facts already known
- facts still unknown
- facts contradicted by current witnesses
- cheapest reliable discriminator
- highest-value discriminator

Hard rule:

The matrix must show which routes are separated by which facts.
A review is incomplete if it only lists routes without the factual splits between them.

### 4) Evidence-channel card

Required rows:

- evidence channels available now
- evidence channels unavailable now
- latency/cost to obtain each channel
- witness reliability concerns
- who must be involved for each channel

Hard rule:

The next best question is inseparable from where the answer can actually come from.
A perfect discriminator that cannot be observed now is weaker than a good discriminator that can.

### 5) Route-reversal risk card

Required rows:

- why the leading route might still be wrong
- what new fact would reverse the route
- what damage an early misroute would cause
- whether interim-hold action is required
- what action can still proceed safely across all live routes

Hard rule:

If a route reversal would materially change action, the page must publish that risk before any stronger routing claim.

### 6) Proposed governing route card

Supported `proposed_route_verdict` values:

- `route-now-governing`
- `route-now-provisional`
- `hold-for-primary-discriminator`
- `route-to-dual-path-containment`
- `escalate-for-adjudication`
- `declare-no-current-governing-route`

Required rows:

- proposed route verdict
- governing route if any
- explicit routes ruled out
- explicit routes still alive
- next question if not final
- strongest blocked sentence if not final

Hard rule:

A provisional route must preserve which alternatives are still alive.
The interface may not present provisional routing as settled doctrine.

### 7) Decision sentence

Render one sentence only:

- `Routing review currently [proposed_route_verdict]; leading route is [route], live alternatives are [routes], and the next best distinguishing question is [question].`

## Required interactions

- **Raise new lookalike route**
- **Mark route disqualified**
- **Promote discriminator**
- **Switch to dual-path containment**
- **Escalate for adjudication**

## Failure state

If the case still has no reliable discriminator, show:

- `No reliable discriminator yet. Only cross-route-safe actions may proceed.`
''')

write('docs/1507-applicability-proof-page-governing-doctrine-distinction-gaps-and-safe-next-claim-interface-spec.md', '''# Applicability proof page: governing doctrine, distinction gaps, and safe next claim interface spec

## Purpose

After the archive learned how to compare lookalike routes, it still needed one proof page that answers:

> what doctrine currently governs this case, what facts earned that routing, what uncertainty remains, and what stronger sentence is still blocked until more is learned?

## Core decision

AnonSync must expose one first-class **Applicability proof** page whenever a case is materially routed into governing doctrine, provisional doctrine, or an explicit no-current-governing-route state.

## Fixed page order

1. **Routing summary card**
2. **Fact-pattern proof card**
3. **Competing-route disposition card**
4. **Open-gap card**
5. **Safe-next-claim card**
6. **Decision sentence**

### 1) Routing summary card

Required rows:

- current governing route or doctrine
- routing class
- case owner
- adoption time
- current status

Supported `routing_class` values:

- `confirmed-governing-doctrine`
- `provisional-governing-doctrine`
- `cross-route-safe-containment-only`
- `human-adjudication-required`
- `no-current-governing-doctrine`

### 2) Fact-pattern proof card

Required rows:

- key facts that justify the route
- key facts that would have supported rejected routes
- strongest missing fact if any
- witness contradictions if any
- why the current route is still safer than alternatives

Hard rule:

Applicability proof must prove the route against the alternatives, not merely restate the selected doctrine.

### 3) Competing-route disposition card

For each competing route, show:

- route name
- disposition
- decisive fact or lack of fact
- whether it can re-open later
- what evidence would revive it

Supported `route_disposition` values:

- `ruled-out`
- `suppressed-pending-fact`
- `still-live-but-weaker`
- `kept-as-reopen-candidate`
- `promoted-to-co-governing-risk`

Hard rule:

Rejected routes must not disappear.
The proof must preserve why they lost and how they could return.

### 4) Open-gap card

Required rows:

- unresolved factual gap
- impact of that gap on action
- rereview trigger
- expiry for provisional confidence
- stronger claim blocked by the gap

Hard rule:

Open gaps must weaken the claim ceiling explicitly.
A proof with unresolved gaps may not present itself as fully settled.

### 5) Safe-next-claim card

Required rows:

- strongest currently safe routing sentence
- strongest blocked overclaim
- actions safe under current routing
- actions forbidden until gap closure
- evidence that would unlock the stronger claim

Hard rule:

The proof must speak in claim ceilings, not vibes.

### 6) Decision sentence

Render one sentence only:

- `Current applicability is [routing_class]; governing doctrine is [route], justified by [fact basis], with [open gap] still blocking [stronger claim].`

## Required interactions

- **Confirm governing doctrine**
- **Downgrade to provisional**
- **Preserve reopen candidate**
- **Record blocked stronger claim**
- **Trigger rereview**

## Failure state

If no doctrine currently governs, show:

- `No governing doctrine proved yet. Only cross-route-safe containment or fact-capture actions are justified.`
''')

write('docs/1508-applicability-timeline-page-facts-learned-candidates-promoted-and-route-reversal-events-interface-spec.md', '''# Applicability timeline page: facts learned, candidates promoted, and route reversal events interface spec

## Purpose

After the archive learned how to prove doctrine applicability, it still needed one chronology page for operators asking:

> how did this case move from symptom intake to a governing doctrine, and which later fact reversed or strengthened the route?

## Core decision

AnonSync must expose one first-class **Applicability timeline** page for every materially routed case whose doctrine fit evolved over time.

## Required event families

- intake symptom recorded
- candidate precedent surfaced
- candidate precedent disqualified
- primary discriminator chosen
- new fact learned
- evidence contradiction attached
- provisional route declared
- governing doctrine confirmed
- route reversed
- cross-route-safe containment entered
- human adjudication requested
- applicability rereview triggered

## Event-row schema

Each row must show:

- timestamp
- event family
- current leading route before event
- current leading route after event
- fact added or removed
- doctrine weight delta if any
- newly allowed claim
- newly blocked claim
- who caused the change

## Hard rules

### 1) Route reversal is a first-class event

If the leading route changes, the timeline must preserve both the old and new route plus the fact that forced the reversal.

### 2) Facts must precede stronger claims

A stronger doctrine-applicability sentence must not appear before the fact event that justified it.

### 3) Rejected routes remain historical truth

The timeline must preserve what routes were plausible earlier, even after they are disqualified.
That history matters for later doctrine refinement.

## Empty state

If the case never moved beyond obvious single-route intake, show:

- `No extended applicability timeline yet. Intake facts were sufficient for direct routing without live lookalike competition.`
''')

write('docs/1509-applicability-lineage-receipt-page-fact-pattern-governing-doctrine-open-gaps-and-blocked-stronger-sentences-interface-spec.md', '''# Applicability lineage receipt page: fact pattern, governing doctrine, open gaps, and blocked stronger sentences interface spec

## Purpose

After the archive learned how to track routing history, it still needed one final handoff page that answers:

> what doctrine currently governs this case, which facts made that routing safe, what gaps remain, and what stronger sentence is still blocked if another operator picks this up later?

## Core decision

AnonSync must expose one first-class **Applicability lineage receipt** whenever a routed case is handed off, paused, escalated, or used to justify bounded next action.

## Fixed page order

1. **Receipt header**
2. **Current fact-pattern card**
3. **Governing-doctrine card**
4. **Open-gap and rival-route card**
5. **Claim-ceiling card**
6. **Blocked-stronger-sentence card**

### 1) Receipt header

Show:

- applicability receipt id
- case id
- current routing owner
- publication time
- latest rereview time
- current routing class

### 2) Current fact-pattern card

Required rows:

- primary symptom family
- decisive observed facts
- worlds/lanes relevant
- already-attempted actions
- current witness contradictions if any

### 3) Governing-doctrine card

Required rows:

- governing doctrine id or `none yet`
- routing class
- why this doctrine currently wins
- doctrine weight used
- next rereview trigger

### 4) Open-gap and rival-route card

Required rows:

- open factual gap
- rival routes still alive
- rival routes ruled out
- fact that would most likely reopen routing
- cross-route-safe action set if any

### 5) Claim-ceiling card

Required rows:

- strongest currently safe routing sentence
- action authority justified by that sentence
- weaker sentence if the route downgrades
- expiry or freshness boundary

### 6) Blocked-stronger-sentence card

Required rows:

- strongest blocked overclaim
- exact fact needed to unlock it
- who can supply that fact
- what evidence would collapse the current route instead

## Hard rule

An applicability receipt must let a later operator answer four questions immediately:

- what facts do we really know?
- what doctrine currently governs, if any?
- what rival routes are still alive?
- what stronger sentence is still blocked?

If any of those are missing, the receipt is incomplete.

## Empty state

If routing is still unclassified, show:

- `No applicability receipt yet: the case has not reached a stable routing stance.`
''')

prepend('README.md', readme_add)
prepend('docs/00-status.md', status_add)
prepend('docs/10-resilio-sync-evaluation.md', resilio_eval_add)
prepend('docs/11-resilio-borrow-line-and-non-clone-scorecard.md', scorecard_add)
prepend('docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md', clone_veto_add)
prepend('docs/20-product-direction.md', product_add)
prepend('docs/sources.md', sources_add)
