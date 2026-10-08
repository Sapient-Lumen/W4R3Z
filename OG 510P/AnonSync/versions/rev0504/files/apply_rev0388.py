from pathlib import Path

root = Path('/mnt/data/work0387')
docs = root / 'docs'


def write(name: str, content: str):
    (docs / name).write_text(content.strip() + '\n', encoding='utf-8')


def prepend(path: Path, text: str):
    old = path.read_text(encoding='utf-8')
    path.write_text(text.strip() + '\n\n' + old, encoding='utf-8')

new_files = {
'1468-resilio-estate-certification-scope-exclusion-and-freshness-fragmentation-evaluation.md': '''
# Resilio estate certification, scope exclusion, and freshness fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- represent changed returns as parity debt
- settle many such debts through convergence campaigns
- publish bounded wins without lying about stragglers
- keep broader success language blocked until settlement proof really covered the claimed scope

What it still lacked was the next ordinary operator answer:

> after the campaigns, what exact estate scope can we now honestly certify as back in bounds, what is excluded, how fresh is the proof, and what event revokes that certification later?

That is the seam this pass locks.
The operator does not only need campaign truth.
They also need **estate certification truth**.
They need a durable answer to whether a meaningful estate, fleet, or governed family is now in-bounds again, not merely improving.

Current official Resilio material is useful here because it already exposes many inspection surfaces an operator would use when trying to answer that question manually:

- `Sync Main View (Desktop)`
- `How do I perform a search in Sync?`
- `Folder Types and Management`
- `Running Sync in configuration mode`
- `Sync Service Troubleshooting on Windows`
- `Settings on mobile platforms`
- `User Management`

## Current official Resilio evidence that matters here

Current official docs still show all of the following:

- `Sync Main View (Desktop)` still says the main UI lets operators filter connected and disconnected shares, perform search, enable or disable columns, and inspect a History lane that shows general syncing activity for the last 30 days. It also still says a green checkmark means files are synced with all connected peers. That is useful status inspection, but it is not yet a certification object.
- The same article still says the peers list shows `X of Y`, where `X` is online peers and `Y` includes offline peers, and that a peer offline for 7 days gets disconnected from the folder unless configured otherwise. So even the ordinary healthy-looking share view already has a horizon and freshness boundary built into it.
- `How do I perform a search in Sync?` still says search is available for folders, shared files, connected devices, and users in the UI. That is useful for locating evidence, but it is still a locator, not a scoped certification answer.
- `Folder Types and Management` still says disconnected folders remain visible for future action even though they have no folder path and take no space on the device. That means an estate can contain subjects that still belong to the logical set while no longer looking like ordinary active folders.
- The same article still shows that folder view can be customized with columns and sorting. That is useful inspection and triage support, but again it is not a durable statement of certified scope.
- `Running Sync in configuration mode` still says config mode is helpful for applying the same settings on a number of different machines, and still says that setting a non-default `storage_path` creates new settings there. So broad configuration alignment exists, but it can also create another settings world.
- `Sync Service Troubleshooting on Windows` still says switching the service to `Local System` creates another storage folder in another directory, after which the old added folders are absent and operators need to re-add and re-share or reconnect them. That is a strong example of an estate looking partially familiar while no longer being one continuous governed world.
- The same service article still says Web UI exposure may require separate config changes and a service restart. So even operator visibility is a separate certifiable plane, not just a byproduct of sync activity.
- `Settings on mobile platforms` still documents a separate mobile settings lane covering identity, auto-start, battery saver, auto-sleep, mobile data, proxy, listening port, and UPnP. That means current Resilio still has parallel settings and operating surfaces beyond the desktop main view.
- `User Management` still says peer disconnect suspends future updates while already-synchronized files remain in place. So visible bytes and future update rights can still diverge inside the estate.

So current Resilio still clearly admits serious certification truths:

- operators use many surfaces to inspect whether the estate looks healthy
- visible healthy activity is not the same thing as a durable estate-wide certification
- disconnected or partially detached subjects can remain in logical scope
- configuration, service principal, storage root, and mobile lanes can create scope or world boundaries
- status surfaces have freshness limits and horizon assumptions

But those truths still do not become one operator-facing **estate certification / explicit exclusions / freshness / revocation** object.

## What Resilio still gets right

### 1) It exposes several of the raw surfaces a careful operator would consult

Filters, search, columns, peer counts, history, configuration mode, service troubleshooting, and mobile settings are all real evidence planes.
That is worth borrowing.

### 2) It is honest that world changes can invalidate naive fleet-wide assumptions

Config `storage_path`, service principal changes, and detached or disconnected folder states all show that one installation family can fork into materially different operational worlds.
That matters.

### 3) It preserves that some non-active subjects still deserve operator attention

Disconnected folders and disconnected peers remain meaningful estate members for later action.
That is useful.

## Where current Resilio still fragments the operator answer

### A) There is no canonical certification object

A careful operator can inspect folders, peers, search results, history, service state, and settings.
But the product still does not give one place to answer:

- what exact scope is being certified
- which worlds or subjects are excluded
- how fresh the proof must be
- what weaker sentence still survives if certification is too broad

### B) There is no durable exclusions register tied to the stronger sentence

Current docs let operators learn that disconnected folders exist, that service or config changes can create new worlds, and that mobile has its own settings lane.
What they do not provide is one durable answer to:

- whether those subjects are inside the current certification scope
- whether they are intentionally excluded
- whether they block broader certification
- who owns their follow-on treatment

### C) There is no explicit revocation contract

Current surfaces expose activity, history, peer counts, and topology changes.
What they do not provide is one first-class certification answer to:

- what event revokes this certification
- what witness freshness window keeps it alive
- when quiet time is enough to preserve it
- what drift, exclusion change, or world fork automatically downgrades it

## Hard product decision unlocked by this pass

AnonSync should not let `campaigns completed` impersonate `estate certified`.
It should promote any material post-settlement confidence claim into a first-class **estate certification object** that separately expresses:

- certification target sentence
- exact certified scope
- explicit exclusions and whether they block broader certification
- witness classes and freshness window
- stronger blocked sentence
- automatic revocation triggers

That is the right next seam because it answers the operator question that always follows successful cleanup work:

> what exactly can we now certify as back in bounds, what remains outside that certificate, and how do we know when that certificate silently expires or is revoked?

## Replacement line for AnonSync

Borrow from Resilio:

- candor that operators inspect multiple evidence surfaces
- honesty that service, config, mobile, and disconnected states create real scope boundaries
- explicit admission that visible healthy status is narrower than universal truth

Do not clone from Resilio:

- any workflow where estate certification remains an informal synthesis across folders, devices, users, history, service state, and config state
- any contract where exclusions are only remembered in the operator's head
- any product shape where certification freshness and revocation are not explicit first-class data

AnonSync should instead ship explicit pages for:

- estate certification contract sheet
- estate certification shaping review
- estate certification proof
- estate certification timeline
- estate certification lineage receipt
''',
'1469-estate-certification-contract-sheet-page-scope-exclusions-and-freshness-target-interface-spec.md': '''
# Estate certification contract sheet page: scope, exclusions, and freshness target interface spec

## Purpose

After the archive learned how to settle many parity debts through convergence campaigns, it still needed one ordinary page for the next operator question:

> what exact estate scope are we trying to certify, what is explicitly excluded, and what witness freshness is required before the stronger sentence is allowed?

## Core decision

AnonSync must expose one first-class **Estate certification contract sheet** whenever an operator is trying to say that a meaningful estate, cohort, profile family, or governed surface is now in bounds again.

## Fixed page order

1. **Certification header**
2. **Target-sentence card**
3. **Covered-scope card**
4. **Explicit-exclusions card**
5. **Witness-and-freshness card**
6. **Decision sentence**

### 1) Certification header

Show:

- estate certification id
- linked baseline / profile / policy family
- linked convergence campaign ids
- certification owner
- created time
- next decision gate
- current certification status
- strongest currently safe sentence

Supported `current_certification_status` values:

- `drafting`
- `evidence-collecting`
- `awaiting-review`
- `certified-bounded-scope`
- `certified-family-scope`
- `blocked`
- `expired`
- `revoked`
- `retired`

Hard rule:

A certification effort may not be represented only as a vague `all clear` note once it is being used to upgrade estate-level confidence.

### 2) Target-sentence card

This card states what stronger sentence the certification is trying to earn.
Required rows:

- intended certified sentence
- current weaker safe sentence
- target certification scope
- minimum witness classes required
- freshness window required before certification
- broader blocked sentence if this scope is still too narrow

Supported `target_certification_scope` values:

- `single-policy-family`
- `single-linked-estate`
- `selected-bounded-subset`
- `single-world-only`
- `mixed-explicit-subset`

Hard rule:

The card must explicitly say what scope is being certified.
`estate healthy` is illegal without an enumerated scope boundary.

### 3) Covered-scope card

This card defines what is inside the certificate.
Required rows:

- included subject count
- included subject ids or cohorts
- inclusion rule
- included worlds or surfaces
- proof horizon for covered scope
- required completeness level

Supported `inclusion_rule` values:

- `all-known-subjects-in-family`
- `all-known-subjects-in-world`
- `all-subjects-settled-by-linked-campaigns`
- `explicit-bounded-selection`
- `manually-certified-subset`

Hard rule:

Coverage must be enumerable.
A certification target may not rely on `roughly all the important ones`.

### 4) Explicit-exclusions card

This card defines what is outside the certificate and why.
Required rows:

- excluded subject ids or cohorts
- exclusion class per item
- whether exclusion is allowed or blocking
- owner
- expiry or rereview date
- path to inclusion, successor certification, or reopen

Supported `exclusion_class` values:

- `not-yet-settled`
- `different-world`
- `unsupported-surface`
- `stale-witness`
- `temporary-waiver`
- `intentionally-out-of-scope`
- `reopened-problem`

Hard rule:

Every exclusion must remain visible next to the intended stronger sentence.
No silent scope trimming.

### 5) Witness-and-freshness card

This card defines what proof is acceptable.
Required rows:

- witness families required
- minimum freshness window
- oldest acceptable evidence age
- whether passive quiet time is sufficient
- revocation triggers armed at certification time
- downgrade sentence if freshness expires

Supported `witness_family` values:

- `settlement-proof`
- `attestation-proof`
- `live-health-proof`
- `topology-proof`
- `permission-or-rights-proof`
- `operator-reviewed-exception-proof`

Hard rule:

Freshness is part of the certification target, not a later footnote.

### 6) Decision sentence

Format:

> `This certification may target [intended certified sentence] for [target certification scope] only if [required witness families] are fresh through [freshness window] and the following exclusions remain explicitly bounded: [excluded cohorts]. Until then, the strongest safe sentence remains [current weaker safe sentence].`

## Required interactions

### A) `Narrow certification scope`

Lets the operator shrink the target scope without losing the excluded subjects.

### B) `Promote exclusion to blocker`

Turns a tolerated exclusion into a hard block for the stronger sentence.

### C) `Require fresh witness`

Raises the proof bar before certification can proceed.

### D) `Split separate certificate`

Moves a different world or lane into its own certification object instead of smuggling it into this one.

## Explicit anti-goals

Do not:

- let campaigns closing automatically mint an estate certificate
- let exclusions disappear into prose
- let freshness remain implied
- let `green enough` substitute for a scoped target sentence

## Why this page exists

Because once cleanup waves succeed, the next risk is not failure.
It is an oversized success claim.
''',
'1470-estate-certification-shaping-review-page-covered-bounded-excluded-and-blocking-scope-interface-spec.md': '''
# Estate certification shaping review page: covered, bounded, excluded, and blocking scope interface spec

## Purpose

After a certification target exists, the product needs one review page that decides whether the proposed scope is honest.
This is the page that answers:

> what actually belongs inside this certificate now, what must be excluded, what witness is still missing, and what broader claim remains blocked even if a bounded certificate is allowed?

## Page promise

This page must separate four things that operators often blur together:

- subjects truly covered now
- subjects intentionally excluded but bounded
- subjects that still block certification
- subjects that need a separate certificate rather than forced inclusion here

## Fixed page order

1. **Scope-review header**
2. **Covered-now card**
3. **Bounded-exclusion card**
4. **Blocking-gap card**
5. **Witness-sufficiency card**
6. **Approval sentence**

### 1) Scope-review header

Show:

- certification id
- proposed scope size
- covered-now count
- bounded-exclusion count
- blocker count
- current review verdict

Supported `current_review_verdict` values:

- `scope-honest-awaiting-witness`
- `bounded-cert-possible`
- `broader-scope-overclaimed`
- `must-split-separate-certificate`
- `blocked`

Hard rule:

The header must say whether the problem is proof insufficiency, scope overreach, or hidden world mismatch.
Those may not share one generic yellow state.

### 2) Covered-now card

Required rows:

- subjects fully supported by current proof
- supporting witness classes per cohort
- freshness of the oldest qualifying witness
- whether any subject depends on weaker inherited proof
- candidate strongest sentence for this covered subset

Hard rule:

Inherited proof must be named as inherited.
It may not masquerade as direct witness.

### 3) Bounded-exclusion card

Required rows:

- excluded subjects
- reason each subject is outside the current certificate
- whether exclusion is acceptable for bounded certification
- owner
- rereview horizon
- next action

Supported `acceptable_bounded_exclusion_reason` values:

- `different-world-needs-own-certificate`
- `temporary-waiver-already-governed`
- `out-of-scope-by-design`
- `stale-but-nonblocking-witness-for-broader-claim`

Hard rule:

A bounded certificate is allowed only when exclusions are truly bounded and do not invalidate the sentence for included scope.

### 4) Blocking-gap card

Required rows:

- blocking subjects or gaps
- why each blocks the stronger sentence
- whether the block is evidence, scope, or topology based
- earliest next retry point
- whether a narrower certificate remains allowed

Supported `blocking_gap_class` values:

- `missing-subject-proof`
- `stale-witness`
- `world-mismatch`
- `rights-mismatch`
- `unsettled-delta`
- `reopened-risk`

Hard rule:

Blockers must stay explicitly visible even when a bounded certificate is approved.

### 5) Witness-sufficiency card

Required rows:

- required witness families
- present witness families
- freshness verdict per family
- weak links
- passive-quiet-time acceptability
- additional proof needed before broader certification

Hard rule:

Passive quiet time may preserve freshness.
It may not silently upgrade a weak witness family into a strong one.

### 6) Approval sentence

Format:

> `It is safe to certify [covered subset] because its scope is explicitly bounded and supported by [fresh witness families]. It is not safe to certify [broader blocked sentence] because [blockers] remain outside current proof or outside this certificate's honest scope.`

## Required interactions

### A) `Approve bounded certificate`

Publishes a certificate only for the covered scope.

### B) `Refuse broader overclaim`

Forces the stronger sentence to stay blocked.

### C) `Split separate certificate`

Routes a different world or lane into another certification object.

### D) `Escalate blocker back to campaign or case`

Pushes unresolved subjects back into settlement or incident flow instead of hiding them.

## Explicit anti-goals

Do not:

- let coverage and exclusion merge into one progress bar
- let blockers vanish behind a bounded win
- let stale evidence pass because the story feels old and familiar
- let world mismatches be treated as harmless details

## Why this page exists

Because the hardest part of certification is not collecting a lot of green-looking evidence.
It is drawing the boundary that keeps that evidence honest.
''',
'1471-estate-certification-proof-page-certified-scope-freshness-and-revocation-triggers-interface-spec.md': '''
# Estate certification proof page: certified scope, freshness, and revocation triggers interface spec

## Purpose

After a certification is shaped, the product needs one durable page that proves what scope is truly certified right now.
This is the page that decides whether the archive has earned a real stronger sentence, for what scope, and for how long.

## Page promise

This page must answer:

> what exact scope is certified now, what evidence supports it, how fresh is that evidence, what exclusions remain, and what event revokes this certificate later?

## Fixed page order

1. **Certification outcome header**
2. **Certified-scope proof card**
3. **Witness-freshness card**
4. **Claim-and-ceiling card**
5. **Revocation-watch card**
6. **Outcome sentence**

### 1) Certification outcome header

Show:

- certification id
- certification time
- certifying owner
- certified scope size
- excluded scope size
- current certification outcome

Supported `current_certification_outcome` values:

- `certified-bounded-scope`
- `certified-family-scope`
- `not-yet-certified`
- `expired`
- `revoked`
- `retired`

Hard rule:

A certification cannot be green if its freshness window has already expired.

### 2) Certified-scope proof card

Required rows:

- included subjects or cohorts
- excluded subjects or cohorts
- included worlds or surfaces
- excluded worlds or surfaces
- proof completeness for included scope
- proof ceiling for broader scope

Hard rule:

The card must enumerate what is inside and outside the certificate.
A universal sentence is illegal when exclusions remain.

### 3) Witness-freshness card

Required rows:

- witness families used
- freshest timestamp per family
- oldest qualifying timestamp across required families
- certification freshness window
- next freshness expiry time
- whether passive quiet time is carrying any family

Hard rule:

The oldest qualifying witness controls certification freshness unless a stronger family-specific rule says otherwise.

### 4) Claim-and-ceiling card

Required rows:

- strongest safe certified sentence now
- exact scope of that sentence
- broader blocked sentence
- what would unlock the broader sentence
- surviving weaker sentence after expiry or revocation
- downgrade path

Hard rule:

The broader blocked sentence must stay visible even when the bounded certificate is strong.

### 5) Revocation-watch card

Required rows:

- armed revocation triggers
- trigger class per item
- automatic downgrade on trigger
- re-certification requirement
- owner of watch response
- whether trigger affects all scope or bounded subset only

Supported `revocation_trigger_class` values:

- `freshness-expired`
- `new-exclusion-created`
- `subject-reopened`
- `world-fork-detected`
- `rights-drift-detected`
- `attestation-withdrawn`
- `topology-changed-beyond-proof`

Hard rule:

A certificate without explicit revocation triggers is incomplete.

### 6) Outcome sentence

Format:

> `This proof certifies [strongest safe certified sentence now] for [exact scope of that sentence] using [witness families used], fresh through [next freshness expiry time]. It remains unsafe to say [broader blocked sentence] because [excluded scope / missing proof]. This certificate is revoked if [armed revocation triggers].`

## Required interactions

### A) `Publish certificate`

Issues the certificate only for the proved scope.

### B) `Revoke certificate now`

Withdraws the stronger sentence immediately when a revocation trigger is observed.

### C) `Renew freshness`

Updates freshness only when the required witness families are truly renewed.

### D) `Downgrade to weaker sentence`

Preserves a smaller safe claim after expiry or revocation.

## Explicit anti-goals

Do not:

- let certification survive stale evidence silently
- let one witness family cover for another missing family without saying so
- let exclusions disappear from the proof once certification turns green
- let revocation become tribal knowledge instead of product state

## Why this page exists

Because a certificate is only useful if the next operator can tell exactly what it covers and exactly how it dies.
''',
'1472-estate-certification-timeline-page-scope-change-freshness-renewal-and-revocation-events-interface-spec.md': '''
# Estate certification timeline page: scope change, freshness renewal, and revocation events interface spec

## Purpose

The archive already had campaign timelines.
Once estate certification becomes first-class, it also needs one timeline that shows when scope widened or narrowed, when freshness was renewed or allowed to age, and when the certificate was downgraded or revoked.

## Timeline promise

This page must answer:

> how did this certificate evolve over time, when did its covered scope change, when did evidence age or renew, and what event changed the strongest safe sentence?

## Event families

### 1) Scope-shape events

Supported values:

- `certificate-created`
- `scope-widened`
- `scope-narrowed`
- `exclusion-added`
- `exclusion-removed`
- `separate-certificate-split`

### 2) Witness events

Supported values:

- `required-witness-collected`
- `freshness-renewed`
- `weak-witness-rejected`
- `passive-quiet-window-accepted`
- `freshness-expiry-near`
- `freshness-expired`

### 3) Claim events

Supported values:

- `bounded-certificate-published`
- `family-certificate-published`
- `broader-claim-blocked`
- `broader-claim-unblocked`
- `downgraded-to-weaker-sentence`
- `certificate-retired`

### 4) Revocation events

Supported values:

- `subject-reopened`
- `world-fork-detected`
- `rights-drift-detected`
- `attestation-withdrawn`
- `certificate-revoked`
- `recertification-started`

## Required timeline controls

The page must let operators filter by:

- subject or cohort
- witness family
- claim effect
- exclusion class
- revocation trigger
- time window

## Required summary rail

Pinned above the timeline:

- current strongest safe sentence
- broader blocked sentence
- certified scope count
- excluded scope count
- next freshness expiry
- revocation triggers currently armed

## Explicit anti-goals

Do not:

- show only the initial publication event
- hide scope narrowing after a certificate was published
- collapse freshness expiry and revocation into generic churn
- let exclusion changes vanish once the current sentence looks good

## Why this page exists

Because a certificate is not only a verdict.
It is a living boundary whose truth changes when scope, freshness, or topology changes.
''',
'1473-estate-certification-lineage-receipt-page-certified-scope-exclusions-and-revocation-boundary-interface-spec.md': '''
# Estate certification lineage receipt page: certified scope, exclusions, and revocation boundary interface spec

## Purpose

After a certification is published, the next operator still needs one durable receipt that says what exact scope is certified, what remains explicitly excluded, how fresh the proof is, and what revokes the certificate.

## Receipt contract

This receipt is the handoff object for estate-level confidence.
It is not a victory memo.
It is a statement of certified scope, excluded scope, freshness horizon, and revocation boundary.

## Fixed page order

1. **Receipt header**
2. **Certified-scope card**
3. **Exclusions card**
4. **Freshness card**
5. **Claim-ceiling-and-revocation card**
6. **Handoff sentence**

### 1) Receipt header

Show:

- certification id
- receipt time
- certifying owner
- certification outcome
- included scope summary
- excluded scope summary

### 2) Certified-scope card

Required rows:

- included subject ids or cohorts
- included worlds or surfaces
- proof completeness for certified scope
- linked campaign ids
- next mandatory review

### 3) Exclusions card

Required rows:

- excluded subject ids or cohorts
- why each is outside the certificate
- whether each exclusion is tolerated or blocking for broader claims
- owner
- expiry
- next action

### 4) Freshness card

Required rows:

- witness families used
- oldest qualifying evidence timestamp
- freshness horizon
- next expiry time
- renewal requirement

### 5) Claim-ceiling-and-revocation card

Required rows:

- strongest safe certified sentence now
- exact scope of that sentence
- broader blocked sentence
- what would unlock it
- revocation triggers
- weaker sentence that survives after revocation or expiry

Hard rule:

The receipt must state the revocation boundary even when the certificate is currently healthy.

### 6) Handoff sentence

Format:

> `This receipt certifies [strongest safe certified sentence now] for [exact scope of that sentence], fresh through [next expiry time]. It remains unsafe to say [broader blocked sentence] because [excluded subjects / missing proof] remain outside the certified scope. This certificate is revoked if [revocation triggers].`

## Explicit anti-goals

Do not:

- turn a bounded certificate into a universal claim
- omit explicit exclusions because they were acceptable at the time
- hide freshness horizon after publication
- issue a receipt without revocation triggers

## Why this page exists

Because the archive should never again need a detective to determine what exactly was certified and what event quietly invalidated that confidence later.
'''
}

for name, content in new_files.items():
    write(name, content)

prepend(root / 'README.md', '''
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
''')

prepend(docs / '00-status.md', '''
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
''')

prepend(docs / '10-resilio-sync-evaluation.md', '''
## Revision addendum — estate certification, explicit exclusions, and revocation truth after rev0387

The next non-clone seam is now explicit: **current Resilio exposes many useful inspection surfaces, but still lacks one operator-facing estate-certification contract**.
Current official material remains useful and candid:

- `Sync Main View (Desktop)` still says the main UI lets operators filter connected/disconnected shares, perform search, enable/disable columns, inspect 30-day History, and interpret share status including a green check for files synced with connected peers
- the same article still says peer counts show online versus total peers and that peers offline for 7 days get disconnected from the folder unless configured otherwise
- `How do I perform a search in Sync?` still says search spans folders, shared files, connected devices, and users in the UI
- `Folder Types and Management` still says disconnected folders remain visible for future action even though they have no local path and take no device space
- the same article still says folder view can be customized with columns and sorting, which helps inspection but does not create a certificate
- `Running Sync in configuration mode` still says config mode is helpful for applying the same settings to a number of different machines, while also saying that a non-default `storage_path` creates new settings there
- `Sync Service Troubleshooting on Windows` still says switching the service to `Local System` creates another storage folder, after which old folders are absent until they are re-added / re-shared or reconnected
- `Settings on mobile platforms` still documents a separate mobile settings lane covering identity, power, and network controls
- `User Management` still says peer disconnect suspends future updates while synchronized files remain in place

That is enough to justify a sharper product stance:

- **borrow Resilio's candor that operators already inspect many surfaces to judge health**
- **borrow the honesty that service, config, mobile, and disconnected states create real scope boundaries**
- **do not clone a world where estate certification remains an informal synthesis instead of a durable scoped object with explicit exclusions, freshness, and revocation**

The replacement line for AnonSync is now stronger:

- model **estate certification** directly
- require exact scope and explicit exclusions next to every stronger sentence
- keep bounded certification legitimate without letting it impersonate universal certification
- make freshness and revocation first-class certificate fields
- preserve the weaker surviving sentence that remains after expiry or revocation
''')

prepend(docs / '11-resilio-borrow-line-and-non-clone-scorecard.md', '''
## Revision addendum — borrow line for estate certification after rev0387

### Borrow

Borrow from current Resilio:

- the willingness to expose several raw inspection surfaces: filters, columns, search, peer counts, history, disconnected-folder visibility, config mode, and service/mobile lanes
- the honesty that green activity is narrower than universal truth
- the admission that service principal changes, config `storage_path`, and disconnected states create meaningful world boundaries

### Do not clone

Do not clone from current Resilio:

- any workflow where an operator must mentally synthesize estate certification from folders, devices, users, history, settings, service state, and config state
- any contract where exclusions are only implied by what is not mentioned
- any product shape where freshness and revocation are not attached to the confidence claim itself

### Stronger replacement line

AnonSync should treat estate confidence as a first-class scoped artifact:

- explicit certification target
- explicit covered scope
- explicit exclusions and whether they are bounded or blocking
- explicit freshness horizon
- explicit revocation triggers
- explicit weaker sentence that survives after downgrade
''')

prepend(docs / '12-resilio-interface-clone-veto-tests-and-page-obligations.md', '''
## Revision addendum — clone-veto obligations for estate certification after rev0387

### New veto seam

A sync product fails the clone test on this seam if it cannot answer, in one operator-facing workflow:

- what exact estate scope is being certified
- which subjects, worlds, or surfaces are explicitly excluded
- whether those exclusions are bounded or blocking
- what witness families and freshness horizon support the stronger sentence
- what broader sentence is still blocked
- what event revokes the certificate later
- what weaker sentence survives after expiry or revocation

### New page obligations

This seam adds five more page obligations:

1. an **estate certification contract sheet** that preserves target sentence, covered scope, exclusions, witness families, freshness target, and broader blocked sentence
2. an **estate certification shaping review** that separates covered scope, bounded exclusions, blockers, and split-to-separate-certificate paths
3. an **estate certification proof** that records certified scope, evidence freshness, revocation triggers, and downgrade path
4. an **estate certification timeline** that preserves scope change, freshness renewal, exclusion change, downgrade, and revocation events
5. an **estate certification lineage receipt** that tells the next operator what exact scope was certified, what remained outside it, how fresh it is, and what revokes it

### Explicit clone vetoes

Do not clone any contract where:

- campaign closure automatically implies estate certification
- exclusions disappear because they were tolerated
- freshness is implied instead of stated
- revocation is tribal knowledge instead of product state
- bounded certificates can masquerade as family-wide or estate-wide truths
- the next operator cannot tell what weaker sentence survives when the stronger one expires or is revoked
''')

prepend(docs / '20-product-direction.md', '''
## Revision addendum — product direction shift toward estate certification and revocation truth after rev0387

The archive now has enough structure that the next product obligation becomes explicit:

- convergence campaigns can settle many debts honestly
- the next obligation is to decide what exact broader scope can now be certified, what remains outside that certificate, and what silently invalidates it later

This matters because the product is now deliberately choosing not to let `cleanup complete` impersonate `estate certified`.

The direction hardens around five decisions:

1. **campaign success and certification are separate product truths**
2. **every certificate needs exact scope and explicit exclusions**
3. **bounded certification is legitimate and should remain bounded**
4. **freshness is part of the confidence object itself**
5. **revocation must be automatic, visible, and downgrade to a weaker surviving sentence rather than disappearing into surprise**

This gives the archive a cleaner long-range direction:

- cases create controls
- controls can be trusted, suspended, re-armed, and settled through campaigns
- campaigns can reduce debt and settle cohorts honestly
- certifications can issue stronger scoped sentences only for the scope actually supported
- those certificates stay alive only while freshness and topology remain within their declared boundary
''')

prepend(docs / 'sources.md', '''
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
''')

print('apply_rev0388 complete')
