from pathlib import Path

root = Path('/mnt/data/work_rev0276')
docs = root / 'docs'

new_docs = {
    '806-resilio-dormant-return-reentry-and-stale-claim-fragmentation-evaluation.md': '''# Resilio dormant-return, re-entry, and stale-claim fragmentation evaluation

## Purpose

The archive already had freshness invalidation, next-observation opportunity, source-witness work, chronology-confidence review, and resume catch-up.
What it still lacked was the next ordinary operator answer:

> this seat or subject came back after dormancy; is this an ordinary healthy return, a chronology-risky re-entry, a hidden roster reappearance, or a stale announcement that still is not safely trustworthy?

Current official Resilio docs are candid enough that AnonSync needs a tighter answer.
Resilio does not pretend all returns mean the same thing.
It separately documents hidden-but-still-linked offline devices, offline peer expiration, restart/reopen re-indexing, offline edits that can overwrite later online work, clock/timezone invalidation, and ghost announcements that no peer still has as full bytes.
That candor is worth preserving.

## What Resilio gets right

Resilio is still right that:

- a device that was hidden from the roster is not necessarily unlinked forever and can reappear when it comes back online
- a peer row that aged out of the ordinary list after 7 days is a different truth from a seat that never existed
- shutting down and later reopening can be a chronology-shaping event rather than a cosmetic resume
- offline local edits can outrank or overwrite changes made by peers that stayed online if chronology trust is weak
- invalid clocks or timezones make stale-return interpretation unsafe and can even leave mobile peers showing empty file lists
- some returning demand is only a ghost announcement because the subject was advertised earlier but no peer now retains full source bytes

This is better than products that flatten every comeback into one green `online again` story.

## What still should not be cloned

The re-entry contract is still scattered and too article-shaped.
Current official Resilio docs still require the operator to combine at least six different article families:

1. **Does Sync work in background?** for the fact that shutdown/re-open reindexes folders, gives them a new modification time, and can let offline edits overwrite changes made by peers that remained online.
2. **Sync Main View (Desktop)** for the fact that offline peers remain counted for a while and then are disconnected from the folder after 7 days.
3. **Power user preferences** for the fact that the offline-peer aging rule is actually a tunable `peer_expiration_days` setting whose default is 7 days.
4. **How to clear offline devices? (desktop only)** for the fact that clearing an offline device only hides it from view and it can reappear later without being unlinked.
5. **"Time difference" error** for the fact that chronology trust fails once peer time or timezone drift exceeds 600 seconds and that mobile peers may then show empty lists.
6. **Cannot download files / There are no source peers online for too long time** for the fact that some announced files are actually stale ghosts that nobody still has in full.

Historical changelog notes make the seam look even more like a durable contract issue rather than a one-off typo:

- historical published fixes still include reconnect-after-long-offline breakage and inability to download from a reconnected peer in some cases
- the maintained v3 line still runs through `3.1.2.1076`

That means one ordinary answer is still reconstructed from several places:

- whether the returning seat is merely visible again or actually trustworthy again
- whether dormancy changed chronology confidence enough to block ordinary `latest` language
- whether the returning seat still has full source bytes for the announced subjects
- whether the safest move is observe, quarantine, repair time, verify source reality, or widen review
- what exact sentence is safe right now: `ordinary wake`, `stale return under review`, `clock-invalid re-entry`, or `announcement persists but source is gone`

The substance is useful.
The workflow ownership is still weak.

## Why this matters for AnonSync

AnonSync should not repeat three follow-on mistakes after it already learned to model freshness budgets and late-claim gates:

1. **false normality** — treating a returning seat as ordinary healthy participation before dormancy, clock trust, and source reality are checked
2. **false disappearance** — treating a hidden or aged-out roster entry as gone forever when it may simply reappear later
3. **false freshness** — treating old announcements or offline edits as ordinary current truth when chronology or source reality has changed

A serious sync product now needs one stable public answer to four follow-up questions:

- **dormancy truth** — how long was this seat or subject effectively absent, hidden, or uncertain?
- **re-entry truth** — what exact kind of return is this?
- **continuity truth** — what chronology and source claims are still safe after the return?
- **action truth** — is the cheapest honest move to trust, quarantine, repair clocks, verify source, or escalate?

## Replacement pages in this revision

This revision adds four fixed pages:

- `807` — Re-entry case page
- `808` — Dormancy timeline page
- `809` — Stale-return review page
- `810` — Re-entry receipt

Together they make `what exactly came back, and how trustworthy is that return?` explicit before AnonSync lets `online again`, `latest`, or `should catch up now` become durable language.

## Concrete product stance

Borrow from Resilio:

- candid separation of hidden-offline, aged-out, re-opened, clock-invalid, and ghost-announcement situations
- candid admission that dormancy can change chronology trust rather than merely delay transfer
- candid use of roster aging, clock validity, and source-bytes reality as real facts rather than cosmetic badges
- candid preservation of the possibility that a hidden device may still come back later

Do not clone from Resilio:

- leaving stale-return meaning split across background, main-view, identity, clock-error, and source-unavailable articles
- letting `online again` or `peer visible` masquerade as `safe to trust again`
- making operators infer whether a return is harmless, stale, dangerous, or merely incomplete
- leaving no durable receipt of dormancy facts, chronology confidence, source reality, and reopen conditions

## Evaluation summary

Resilio still deserves credit for naming the ingredients of a stale return.
But the current product/docs path still leaves a missing object:

> there is no first-class reviewed answer to `this thing came back after dormancy; what exactly returned, what stayed uncertain, and what stronger sentence is still forbidden?`

AnonSync should therefore make **re-entry after dormancy** a first-class product object.
Every serious long-offline return, hidden-device reappearance, clock-invalid comeback, or ghost-announcement aftermath should publish dormancy facts, return class, chronology confidence, source-reality verdict, strongest allowed sentence, and forbidden stronger sentence before the product treats the state as ordinary again.
''',
    '807-re-entry-case-page-dormancy-class-roster-return-and-safe-language-interface-spec.md': '''# Re-entry case page — dormancy class, roster return, and safe-language interface spec

## Purpose

The archive already had freshness invalidation, next-observation opportunity, chronology-confidence review, and source-witness work.
What it still lacked was one fixed page for the operator question:

> this seat or subject is back after being absent or uncertain; what exact kind of return is this, and how much ordinary trust has it really earned yet?

AnonSync should therefore model the answer as a first-class **re-entry case page**.
The product must never force the operator to merge peer-list memory, hidden-device behavior, clock warnings, source-unavailable errors, and dormancy folklore before deciding whether `back` is even a safe word.

## Core decision

Every serious stale return must publish one reviewed re-entry object before stronger normality language is allowed.
The page must preserve six truths:

1. seat / subject under review
2. dormancy class and interval
3. current roster-return class
4. chronology confidence after return
5. source-reality verdict after return
6. strongest allowed sentence right now

## Fixed review order

1. **Current re-entry verdict**
2. **Dormancy facts**
3. **Return class and roster state**
4. **Chronology and source reality**
5. **Safe action ladder**
6. **Claim ceiling**

## 1) Current re-entry verdict

Show:

- seat / subject scope
- current re-entry class
- strongest current summary
- whether this is ordinary wake, stale return, hidden reappearance, aged-out rejoin, clock-invalid return, or ghost-announcement aftermath

Required re-entry classes:

- `ordinary-wake`
- `hidden-reappearance`
- `aged-out-peer-return`
- `long-offline-return`
- `clock-invalid-return`
- `ghost-announcement-return`
- `mixed`
- `unknown`

## 2) Dormancy facts

Publish explicitly:

- last good witness before dormancy
- first known dormancy anchor
- covered dormancy interval or uncertainty band
- whether the seat was merely hidden, actually absent, expired from roster, or unknown
- whether local edits or announcements may have accumulated during dormancy

## 3) Return class and roster state

Show these separately:

- current roster state (`listed`, `hidden`, `reappeared`, `expired-then-returned`, `not-listed`, `unknown`)
- current runtime state (`awake`, `foreground-only`, `interval-based`, `stopped`, `unknown`)
- current peer visibility witness
- whether this return proves linkage continuity, only visibility continuity, or neither

The operator must be able to answer:

> what exactly came back here: an ordinary participant, a hidden roster entry, or only a weak visible hint?

## 4) Chronology and source reality

This section is mandatory.
It must publish:

- chronology confidence (`high`, `guarded`, `low`, `blocked`)
- whether time / timezone is valid enough for normal ordering
- whether local offline edits exist or are plausible
- whether live full source bytes still exist for the affected subject
- whether the return is contaminated by stale announcements or ghost items

## 5) Safe action ladder

Examples:

- trust as ordinary wake
- keep under re-entry observation
- verify clocks / timezone first
- verify full source peers first
- quarantine local precedence claims
- reopen source-witness review
- escalate to divergence / chronology review

Each action must preview the resulting trust delta and non-effects.

## 6) Claim ceiling

Required verdicts:

- `ordinary participation restored`
- `returned but chronology guarded`
- `returned but source reality incomplete`
- `visible again but linkage continuity weak`
- `unsafe to normalize yet`
- `cannot judge yet`

This verdict is mandatory.

## Compact rendering obligations

Any compact card for re-entry must still preserve:

- re-entry class
- dormancy interval label
- chronology confidence
- source-reality verdict
- safest next action

## Anti-clone rule

Do not clone workflows where the operator still has to read several support articles before the product can answer `this thing came back, but only with guarded trust`.

## Receipt consequence

Every dormancy timeline, stale-return review, and re-entry receipt must link back to the exact re-entry class and claim ceiling that carried the judgment.
''',
    '808-dormancy-timeline-page-last-good-witness-hide-expiry-and-return-context-interface-spec.md': '''# Dormancy timeline page — last-good witness, hide/expiry, and return-context interface spec

## Purpose

The archive already had duty-cycle timelines and posture-drift timelines.
What it still lacked was one timeline for the narrower question:

> what exactly happened between the last trustworthy sighting and the current return, and which events made the return weaker or stronger?

AnonSync should therefore expose a first-class **dormancy timeline page** whenever a seat, peer, or subject comes back after meaningful absence or stale uncertainty.

## Core decision

A stale return must be explainable as a short evidence ladder, not as remembered folklore.
The timeline must preserve five truths:

1. last good witness before dormancy
2. dormancy anchors and uncertainty band
3. hide / roster expiry / visibility change events
4. return and recovery events
5. current interpretation of the covered interval

## Fixed review order

1. **Last good witness**
2. **Dormancy interval**
3. **Visibility and roster changes**
4. **Return-context events**
5. **Current interpretation**

## 1) Last good witness

Show the last reviewed trustworthy state before dormancy:

- timestamp or range
- witness class
- what it proved
- what it did *not* prove beyond that point

## 2) Dormancy interval

Publish:

- first absent / uncertain anchor
- interval end or current return anchor
- uncertainty band width
- whether the seat was hidden, expired, stopped, asleep, foreground-only, clock-invalid, or unknown during this interval

## 3) Visibility and roster changes

Record events such as:

- hidden from roster
- reappeared in roster
- peer expired from list
- peer returned after expiry
- runtime stopped / resumed
- clock warning opened / cleared

Each event row must say whether it changed only visibility, only trust, or both.

## 4) Return-context events

Record relevant return-side anchors such as:

- app restart or reopen
- foreground resume
- next wake interval
- allowed network return
- source-peer return
- ghost-announcement detection
- manual clock repair

## 5) Current interpretation

The page must end with one explicit summary:

- `ordinary wake with short dormancy`
- `long-offline return with guarded chronology`
- `hidden roster reappearance`
- `aged-out peer returned`
- `clock-invalid interval blocks normalization`
- `announcement survives but source reality is broken`
- `mixed / unresolved`

## Public object

### Dormancy timeline page

Fields:

- `dormancy_timeline_page_id`
- `scope_ref`
- `last_good_witness_ref`
- `dormancy_interval`
- `visibility_change_rows[]`
- `return_context_rows[]`
- `current_interpretation`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. scope
2. last good witness
3. dormancy interval label
4. strongest return event
5. current interpretation

Example:

```text
Laptop seat     trusted at 10:14 yesterday     dormant ~17h     reappeared after hide + restart     long-offline return with guarded chronology
```

## Non-goals

This page does **not** decide the final safe action by itself.
It preserves the dormancy story so later review stops flattening all returns into `came back online`.
''',
    '809-stale-return-review-page-offline-edits-clock-confidence-and-source-reality-interface-spec.md': '''# Stale-return review page — offline edits, clock confidence, and source reality interface spec

## Purpose

The archive already had same-path winner review, source-witness work, next-opportunity review, and freshness invalidation.
What it still lacked was one review page for the return question:

> after dormancy, what exactly makes this return risky or safe: offline edits, clock drift, stale announcements, roster expiry, or no remaining full source?

AnonSync should therefore expose a first-class **stale-return review page** whenever a return is not obviously safe.

## Core decision

No seat or subject should silently jump from `uncertain` to `ordinary` just because it became visible again.
The review must preserve five truths:

1. return class under test
2. chronology-risk rows
3. source-reality rows
4. safest next action
5. strongest rejected sentence

## Fixed review order

1. **Return under test**
2. **Chronology risk review**
3. **Source and announcement reality**
4. **Safe action ladder**
5. **Allowed and rejected language**

## 1) Return under test

Show:

- reviewed seat / subject
- current re-entry class
- dormancy interval summary
- why this return is not yet ordinary by default

## 2) Chronology risk review

Publish separate rows for:

- offline local edits present or plausible
- reopen / restart re-indexing risk
- time or timezone invalid
- dormancy long enough that `latest` is only guarded
- no chronology risk presently supported

Each row must say whether it is:

- `supported`
- `plausible`
- `ruled out`
- `blocked by missing evidence`

## 3) Source and announcement reality

Publish separate rows for:

- live full source peer proved
- returning peer visible but full source not proved
- ghost announcement likely
- source absent despite announcement
- stale placeholder-only world likely

The operator must be able to answer:

> is the return actually fetch-capable, or did only the announcement survive?

## 4) Safe action ladder

Examples:

- normalize as ordinary wake
- keep under re-entry observation
- repair clocks first
- verify full source peers first
- reopen source witness
- reopen chronology / winner review
- avoid destructive reconciliation until stronger proof exists

Each action must preview its claim delta and its non-effects.

## 5) Allowed and rejected language

Required allowed examples:

- `The seat returned, but chronology confidence is guarded.`
- `The peer is visible again, but full source proof is incomplete.`
- `The announcement persists, but source reality is currently broken.`

Required rejected examples:

- `Everything is normal again.`
- `This is definitely the latest copy.`
- `The missing file will arrive now.`

## Compact rendering obligations

Any compact review card must still preserve:

- dominant stale-return risk
- source-reality verdict
- safest next action
- strongest rejected sentence

## Anti-clone rule

Do not clone workflows where `back online` or `peer visible again` can erase chronology, source, or dormancy risk without one explicit review object.
''',
    '810-re-entry-receipt-page-dormancy-facts-safe-sentence-and-reopen-boundary-interface-spec.md': '''# Re-entry receipt page — dormancy facts, safe sentence, and reopen boundary interface spec

## Purpose

The archive already had freshness receipts, opportunity receipts, and route receipts.
What it still lacked was the durable receipt for the question:

> after this dormancy interval, what exact return class was accepted, what sentence was judged safe, and what would reopen that judgment?

AnonSync should therefore issue a dedicated **re-entry receipt** whenever it resolves a stale-return question.

## Receipt fields

The receipt must preserve:

- receipt id
- incident id
- seat / subject scope
- dormancy interval
- last good witness
- current return witness
- re-entry class
- roster visibility state
- chronology confidence
- source-reality verdict
- strongest allowed sentence
- stronger rejected sentence
- supporting page ids (`807`, `808`, `809`)
- issued-at timestamp
- reopen conditions

## Required sections

### 1) Dormancy facts

State the durable dormancy basis, for example:

- `Hidden roster entry reappeared after 12 days; linkage continuity visible again, chronology still guarded.`
- `Peer returned after aging out of the roster; full source proof not yet restored.`
- `Seat resumed after offline editing period; clock validity blocks ordinary ordering claims.`

### 2) Safe current sentence

Publish one durable sentence, for example:

- `The seat returned, but should still be treated as a guarded re-entry.`
- `Visibility continuity returned; source continuity is not yet fully proved.`
- `The announcement remains visible, but no full source peer is currently proved.`
- `Ordinary participation was restored for this scope.`

### 3) Stronger rejected sentence

This is mandatory.
Examples:

- `Everything is normal again.`
- `This returning copy is definitely newest.`
- `The file is now fetchable.`

### 4) Reopen conditions

The receipt must say the judgment reopens if any of these happen:

- clocks or timezone drift reappear
- source-reality evidence changes materially
- dormancy class is revised by stronger witnesses
- local offline edits or divergence evidence newly appear
- freshness invalidation or later re-entry supersedes the basis

## Compact rendering obligations

Any compact receipt chip must still preserve:

- re-entry class
- chronology confidence
- safe current sentence
- reopen trigger summary

## Anti-clone rule

Do not clone receipts that merely say `back online`, `returned`, or `looks good now` without preserving dormancy facts, safe language, and reopen boundaries.
'''
}

for name, content in new_docs.items():
    (docs / name).write_text(content.strip() + '\n', encoding='utf-8')

prepend_map = {
    'README.md': '''## Revision addendum — rev0276: re-entry cases, dormancy truth, and stale-return safety

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
''',
    'docs/00-status.md': '''## Latest addendum — re-entry cases, dormancy truth, and stale-return safety after rev0275

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
''',
    'docs/10-resilio-sync-evaluation.md': '''## Revision addendum — dormant return, re-entry, and stale-claim fragmentation after rev0275

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
''',
    'docs/11-resilio-borrow-line-and-non-clone-scorecard.md': '''## Revision addendum — borrow dormancy candor, reject stale-return folklore after rev0275

### Borrow from current Resilio

- the candor that hidden offline devices are not necessarily unlinked and can reappear later
- the candor that offline-peer aging is a real roster event with a concrete 7-day default and tunable policy
- the candor that shutdown/re-open can be a chronology-shaping event rather than cosmetic resume
- the candor that time drift and ghost announcements can make a return visible but not yet trustworthy

### Do not clone from current Resilio

- the requirement that the operator mentally merge background notes, peer-aging rules, hidden-device behavior, clock warnings, and no-source warnings before deciding what returned
- the requirement that `back online` or `peer visible again` masquerade as full restored trust
- the lack of one product-owned object stating dormancy facts, return class, chronology confidence, and source reality together
- the lack of one durable receipt proving why the return was ordinary, guarded, or still unsafe to normalize

### New AnonSync scorecard rule

If the product cannot show dormancy interval, return class, roster visibility state, chronology confidence, source-reality verdict, strongest safe sentence, and reopen boundary in one durable chain, it has not yet earned the right to say `back`, `healthy again`, or `should catch up now`.
''',
    'docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md': '''## Revision addendum — clone-veto after rev0275: stale return may not collapse into one `back online` story

Add one more veto test:

7. **What exactly returned after dormancy: a normal participant, a hidden roster entry, an aged-out peer, a clock-invalid seat, or only a stale announcement with no remaining full source?**

If the answer still depends on remembering background/reopen notes, peer-aging settings, hidden-device behavior, clock warnings, and source-unavailable prose from several articles, the product is still cloning the wrong part of the Resilio contract.

The minimum replacement page family is now:

- `807-re-entry-case-page-dormancy-class-roster-return-and-safe-language-interface-spec.md`
- `808-dormancy-timeline-page-last-good-witness-hide-expiry-and-return-context-interface-spec.md`
- `809-stale-return-review-page-offline-edits-clock-confidence-and-source-reality-interface-spec.md`
- `810-re-entry-receipt-page-dormancy-facts-safe-sentence-and-reopen-boundary-interface-spec.md`
''',
    'docs/20-product-direction.md': '''## Revision addendum — product direction after rev0275: stale return must become a reviewed re-entry case

Another doctrine line now needs to be explicit:

- dormancy facts over flat `back online` language
- return class over one generic reappearance badge
- chronology confidence over ambient `latest` optimism
- source-reality verdict over announcement folklore
- durable re-entry receipts over remembered stale-return context

> AnonSync should model stale return as a reviewed re-entry case, not as a naked visibility change.

The operator should never have to reconstruct whether a returning seat was merely hidden, aged out of the roster, restarted into chronology uncertainty, suffering from invalid clocks, or only advertising ghost announcements with no remaining full source.
''',
    'docs/30-interface-spec.md': '''## Revision addendum — interface rule after rev0275: returning visibility must publish re-entry truth

Another interface rule now becomes mandatory:

- if a surface wants to say `back`, `online again`, `reappeared`, `healthy`, or `should catch up now`, it must publish a re-entry-case contract first
- that contract must preserve dormancy interval, return class, roster visibility state, chronology confidence, source-reality verdict, strongest safe sentence, and reopen boundary

No projection may flatten these into one plain presence badge without a direct path to the re-entry explanation.
''',
    'docs/40-architecture-decisions.md': '''## Revision addendum — architecture decision after rev0275: stale return must compile into a first-class re-entry case

Decision:

- serious post-dormancy return must be represented as an explicit re-entry case, not as a loose combination of presence badges, peer-aging state, warning rows, and remembered history

Why:

- current official Resilio docs still show that one honest return answer can depend on restart/reopen chronology effects, peer-expiration policy, hidden-device behavior, clock validity, and live source reality
- stale-return meaning collapses if dormancy facts, roster-return class, chronology confidence, and source-reality verdict are not preserved together
- normality language collapses if a seat can look visible again before it has earned ordinary trust again

Implications:

- create a `reentry_case` object with dormancy interval, return class, roster state, chronology confidence, and source-reality verdict
- create a `dormancy_timeline` object with last-good witness, hide/expiry rows, return events, and current interpretation
- create a `stale_return_review` object with chronology-risk rows, source/announcement rows, safe action ladder, and rejected stronger sentence
- create a `reentry_receipt` object with safe current sentence and reopen triggers

Rejected alternative:

- keep visibility, peer aging, clock warnings, and no-source symptoms as separate surfaces and let operators synthesize re-entry truth mentally

Reason rejected:

- that would recreate exactly the stale-return folklore and accidental overtrust this archive is explicitly trying not to clone
''',
    'docs/41-report-and-intervention-language.md': '''## Revision addendum — report family after rev0275: re-entry reports for stale-return honesty

The report grammar now needs one more family.

### 27) Re-entry-case report

Answers what exactly came back after dormancy and how trustworthy that return currently is.
It should always say:

- dormancy interval
- return class
- roster visibility state
- chronology confidence
- source-reality verdict

### 28) Dormancy-timeline report

Answers what happened between the last good witness and the current return.
It should always say:

- last good witness
- dormancy anchors
- hide / expiry / warning events
- return events
- current interpretation

### 29) Stale-return review report

Answers what makes the return risky or safe.
It should always say:

- dominant chronology risk
- source/announcement reality
- safest next action
- strongest safe sentence
- stronger forbidden sentence

### 30) Re-entry receipt

Answers what safe return judgment was issued and what would reopen it.
It should always say:

- return class
- chronology confidence
- safe current sentence
- stronger rejected sentence
- reopen conditions
''',
    'docs/50-roadmap.md': '''## Revision addendum — roadmap tranche after rev0275: re-entry cases and stale-return truth

Added this tranche to the roadmap:

- `806` Resilio dormant-return, re-entry, and stale-claim fragmentation evaluation
- `807` Re-entry case page
- `808` Dormancy timeline page
- `809` Stale-return review page
- `810` Re-entry receipt page

Why this tranche belongs now:

- the archive already owns freshness invalidation, next-observation opportunity, chronology-confidence review, and source-reality work
- the remaining gap was the contract between `visible again` and `safe to trust again`
- without this tranche, later lateness, winner, and catch-up conclusions can still overclaim from one returning peer row or one resumed runtime
''',
    'docs/64-critical-open-questions.md': '''## Revision addendum — critical open question after rev0275: how aggressive should stale-return quarantine be before ordinary wakeups feel ceremonial?

The archive now requires re-entry cases, dormancy timelines, stale-return review, and re-entry receipts.
What remains unresolved is the quarantine budget:

- when should the product auto-open a re-entry case versus treat the event as an ordinary wake or resume
- how long a dormancy interval or how much roster aging should automatically lower chronology confidence
- whether hidden-device reappearance should ever be normal by default or always begin guarded
- when ghost-announcement suspicion should block ordinary catch-up language versus merely lower confidence
- whether repaired clocks or newly proved source peers should automatically collapse the case back to ordinary participation or still require explicit review

This matters because weak quarantine recreates accidental overtrust, while overly strong quarantine could make ordinary healthy wakeups feel ceremonial.
''',
    'docs/sources.md': '''## Revision addendum — re-entry cases, dormancy truth, and stale-return safety after rev0275

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
'''
}

for rel, addition in prepend_map.items():
    path = root / rel
    original = path.read_text(encoding='utf-8')
    path.write_text(addition.strip() + '\n\n' + original, encoding='utf-8')

(root / 'update_rev0276.py').write_text("""from pathlib import Path\n\nroot = Path('.')\n\nnew_docs = {\n    'docs/806-resilio-dormant-return-reentry-and-stale-claim-fragmentation-evaluation.md': 'created in rev0276',\n    'docs/807-re-entry-case-page-dormancy-class-roster-return-and-safe-language-interface-spec.md': 'created in rev0276',\n    'docs/808-dormancy-timeline-page-last-good-witness-hide-expiry-and-return-context-interface-spec.md': 'created in rev0276',\n    'docs/809-stale-return-review-page-offline-edits-clock-confidence-and-source-reality-interface-spec.md': 'created in rev0276',\n    'docs/810-re-entry-receipt-page-dormancy-facts-safe-sentence-and-reopen-boundary-interface-spec.md': 'created in rev0276',\n}\n\nfor path_str, placeholder in new_docs.items():\n    path = root / path_str\n    if not path.exists():\n        path.write_text(placeholder + \"\\n\", encoding='utf-8')\n\nprint('rev0276 scaffold recorded; apply concrete document payloads from archive if replaying manually.')\n""", encoding='utf-8')
