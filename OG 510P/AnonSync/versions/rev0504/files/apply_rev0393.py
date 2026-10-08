from pathlib import Path

root = Path(__file__).resolve().parent

def prepend(path: str, text: str):
    p = root / path
    original = p.read_text()
    p.write_text(text.rstrip() + "\n\n" + original)

def write(path: str, text: str):
    p = root / path
    p.write_text(text.rstrip() + "\n")

readme_add = '''## Revision addendum after rev0392 — appeal, precedent, and doctrine consistency truth

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
'''

status_add = '''## Revision addendum — status shift toward appeal, precedent, and doctrine consistency truth after rev0392

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
'''

resilio_eval_add = '''## Revision addendum — Resilio appeal, precedent, and doctrine evaluation after rev0392

Another current official Resilio pass still supports the same tightened judgment:

- **borrow Resilio's symptom candor and version honesty**
- **do not clone Resilio's precedent contract**

This time the key evidence cluster is:

- `My files don't sync` still says Status warnings usually link to KB explanations and operators may need to inspect warnings, History, peer state, or file queues before choosing a next step
- `Errors & Troubleshooting` and `Core warnings` still organize doctrine primarily as article clusters rather than one canonical ruling workspace
- `"Time difference" error`, `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time`, `Database error`, `Service files missing / Cannot identify destination folder`, and `Agent run out of system notify watchers` still each carry narrow symptom-specific interpretations and repair trees
- `Resilio Sync 3.0 change log` still shows that warning meaning and operator guidance can drift by version, for example with a fixed non-clickable `Can't download file` status and later improved warning text when a license cannot be applied
- `Collecting debug logs manually` and `Collecting crash reports, mini-dumps and core dumps` still say direct technical support is unavailable for Sync v3 and point users toward the community forum and Help Center for functionality issues

So current Resilio still deserves credit for exposing many useful doctrine fragments.
But it still does not own one operator-facing answer to:

> which prior ruling should bind this new case, when is the case distinguishable, and when did a later version, world change, or product fix overrule or sunset the older guidance?

That is why this pass again strengthens the non-clone line.
'''

scorecard_add = '''## Addendum after rev0392 — why appeal and precedent now sit on the non-clone side

Resilio still earns credit for symptom-specific candor.
Its current docs explain many warnings and operational edge cases directly, and its change logs do show when warning behavior or wording changes.
That stays on the **borrow** side.

What stays on the **do not clone** side is the doctrine contract:

- warning meaning still lives across many KB pages
- version drift still pushes doctrine into changelog archaeology
- Sync v3 still routes many unresolved edge cases toward forum/Help Center rather than one product-owned precedent object
- the operator still has to infer whether an old ruling is binding, merely persuasive, distinguishable, or superseded

So the line hardens again:

- **borrow articleized explanations, warning candor, and version honesty**
- **do not clone a product shape where precedent weight and overrule path live outside the operator workspace**
'''

clone_veto_add = '''## Addendum after rev0392 — new clone-veto test for precedent and appeal

A borrowed interface fails the clone test if it requires the operator to decide doctrine weight by memory.
The new veto questions are:

- can the operator see whether a prior ruling is `binding`, `presumptive`, `persuasive`, `informative-only`, or `superseded`?
- can the operator see the version window, world scope, and distinguishing facts that limit that ruling?
- can a later fix or product change explicitly weaken or sunset the older ruling without erasing history?
- can an appeal ask to uphold, distinguish, narrow, or overrule a precedent without free-text folklore?

If the answer is no, the interface is still cloning Resilio's scattered doctrine shape too closely.
'''

product_add = '''## Product-direction addendum after rev0392 — verdicts are not doctrine by default

AnonSync should not let a resolved dispute silently become guidance for the next dispute.
The product direction is now explicit:

- **precedent dockets are first-class**
- **binding, presumptive, persuasive, informative-only, and superseded guidance remain separate**
- **appeals can uphold, distinguish, narrow, overrule, or create doctrine**
- **version drift and world mismatch can weaken old doctrine without deleting it**
- **every meaningful doctrine sentence needs one receipt preserving scope, version window, and overrule path**

That means future interface work should keep one stable family for:

- precedent promotion from dispute verdicts
- appeal and distinguish review
- doctrine adoption or refusal
- version-scoped sunset and overrule logic
- durable doctrine receipts for later operators

The product should never force the operator to infer precedent weight from a warning title, a remembered forum thread, or a changelog note alone.
'''

sources_add = '''## rev0393 source set — appeal, precedent, and doctrine consistency truth

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
'''

write('docs/1498-resilio-appeal-precedent-and-doctrine-fragmentation-evaluation.md', '''# Resilio appeal, precedent, and doctrine fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- receive a contested completion claim
- adjudicate counterevidence
- issue a verdict and, if needed, spawn rework

What it still lacked was the next ordinary operator answer:

> when a new dispute looks similar to an older one, which earlier ruling should bind this case, when is the case distinguishable, and when did a later fix or version change make the old guidance only persuasive or even superseded?

That is the seam this pass locks.
A verdict is not yet doctrine merely because it happened once.
Symptom articles are not the same as precedent.
Version drift can weaken guidance without erasing history.
A later operator needs a durable doctrine object, not memory of which article felt closest.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose many useful doctrine fragments, but mostly as separate articles and channels:

- `My files don't sync` still says Status warnings usually link to KB explanations and that operators may need to inspect warnings, History, peer state, and queues before choosing a fix.
- `Errors & Troubleshooting` and `Core warnings` still organize issue interpretation as clusters of separate warning articles.
- `"Time difference" error` still says bad time or timezone can distort ordering and even produce empty file lists on mobile.
- `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time` still says a peer may announce files that later no source peer actually holds.
- `Database error` still offers a narrow repair ladder from restart to reconnect to all-peer re-add.
- `Service files missing / Cannot identify destination folder` still says the error may come from corrupted internal files or two instances touching the same folder and routes toward remove-and-add-back repair.
- `Agent run out of system notify watchers` still ties one warning to watcher exhaustion and periodic rescanning semantics.
- `Resilio Sync 3.0 change log` still shows that warning meaning and UI handling drift by version, including a fixed non-clickable `Can't download file` status and later improved warning text when a license cannot be applied.
- `Collecting debug logs manually` and `Collecting crash reports, mini-dumps and core dumps` still say direct technical support is unavailable for Sync v3 and route users toward the community forum and Help Center.

## What current Resilio still gets right

### 1) It preserves narrow symptom honesty

Resilio does not pretend every issue means the same thing.
Time skew, ghost-file announcements, watcher exhaustion, database corruption, and service-file corruption are treated as distinct problem families.
That is worth borrowing.

### 2) It keeps version drift visible in at least one channel

The change logs do admit that warning behavior, text, and UI affordances can change over time.
That honesty matters.

### 3) It still provides recoverable breadcrumbs

Warning pages, troubleshooting pages, and log-capture pages are real breadcrumbs for operators.
They are better than silence.

## Where current Resilio still fragments the operator answer

### A) There is no canonical precedent object

Resilio gives the operator warning articles, troubleshooting trees, logs, and change logs.
What it still does not give is one first-class object answering:

- which past ruling is being invoked for the current case
- whether that ruling is binding, presumptive, persuasive, or only informative
- what version window and world scope the ruling actually covered
- what distinguishing facts make the old ruling inapplicable here
- whether a later fix or version change overruled or sunset the old doctrine

### B) Doctrine weight is left to operator memory

A warning article may explain one issue.
A change log may later narrow, fix, or alter the meaning of that warning.
A support page may route users to forum or Help Center.
The operator must still remember how those parts fit together.

### C) Similar-looking cases can hide different world scopes

Time drift on mobile, watcher exhaustion on Linux, service-world corruption on Windows, and ghost-file behavior in selective-sync topologies are not the same class of ruling.
Current Resilio surfaces them separately, but it does not give one review object for distinguishing or relating them.

### D) Appeals and overruling are implicit rather than durable

Operators can read a newer article or a newer change log and infer that older advice is weaker.
What Resilio still does not give is one durable operator-facing record that a prior ruling has been upheld, narrowed, overruled, or sunset.

## Hard product decision unlocked by this pass

AnonSync should not let dispute consistency live in article memory, tribal recall, or changelog archaeology.
It should promote any materially reusable dispute verdict into a first-class **precedent docket** that separately expresses:

- source ruling
- analogy class
- binding weight
- version window
- world scope
- distinguishing facts
- appeal / overrule path
- sunset or supersession state

## Replacement line for AnonSync

Borrow from Resilio:

- explicit symptom families
- articleized explanations that name concrete failure modes
- version honesty when warning behavior or meaning changes

Do not clone from Resilio:

- any workflow where the operator must infer doctrine weight from scattered KB pages and change logs
- any contract where a later fix silently weakens old guidance without a visible overrule path
- any interface where similar cases cannot be explicitly marked as binding, persuasive, distinguishable, or superseded
- any product shape where forum or help-center routing becomes the only practical doctrine memory for v3 operators

AnonSync should instead ship explicit pages for:

- precedent docket contract sheet
- appeal and distinguish review
- precedent proof
- precedent timeline
- precedent lineage receipt
''')

write('docs/1499-precedent-docket-contract-sheet-page-source-ruling-analogy-and-binding-weight-interface-spec.md', '''# Precedent docket contract sheet page: source ruling, analogy, and binding weight interface spec

## Purpose

After the archive learned how to adjudicate disputed completion, it still needed one ordinary page for the next operator question:

> this new challenge looks like an older one — are we actually bound by that earlier ruling, merely guided by it, or free to distinguish it?

## Core decision

AnonSync must expose one first-class **Precedent docket contract sheet** whenever a dispute verdict, case closure, or doctrine update is being invoked for a later materially similar case.

## Fixed page order

1. **Precedent header**
2. **Source-ruling card**
3. **Analogy card**
4. **Binding-weight card**
5. **Version and world-scope card**
6. **Requested doctrine action card**
7. **Decision sentence**

### 1) Precedent header

Show:

- precedent docket id
- source verdict id
- current case id
- doctrine owner
- opened time
- current precedent status
- strongest currently safe sentence
- superseding precedent id if any

Supported `precedent_status` values:

- `drafting`
- `pending-analogy-review`
- `pending-appeal`
- `binding-active`
- `presumptive-active`
- `persuasive-only`
- `informative-only`
- `distinguished-for-current-case`
- `superseded`
- `sunset`
- `closed`

Hard rule:

A current case may not silently claim `same as before` without naming the actual source ruling and its current doctrine status.

### 2) Source-ruling card

Required rows:

- source verdict sentence
- source case scope
- source witness basis
- source remedy or ruling class
- source residual uncertainty if any
- source appeal history if any

Hard rule:

The page must preserve enough of the original ruling to judge whether the analogy is real.
A precedent docket cannot point at a vague remembered incident.

### 3) Analogy card

Required rows:

- claimed similarity summary
- material matching facts
- material mismatching facts
- disputed mismatches
- analogy class
- weakest safe claim about sameness

Supported `analogy_class` values:

- `same-facts`
- `close-analogy`
- `same-symptom-different-world`
- `same-symptom-different-version`
- `distinguishable`
- `gap-case`

Hard rule:

The product must store both matches and mismatches.
Similarity may not erase the facts that could later justify distinction or overrule.

### 4) Binding-weight card

Required rows:

- proposed binding weight
- who may assign or lower that weight
- what evidence would strengthen the weight
- what evidence would weaken the weight
- currently blocked stronger sentence

Supported `binding_weight` values:

- `binding`
- `presumptive`
- `persuasive`
- `informative-only`
- `superseded`

Hard rule:

Binding weight must be explicit.
The interface may not force the operator to infer weight from how confidently the earlier case was described.

### 5) Version and world-scope card

Required rows:

- source version window
- source world or lane scope
- current case version and world
- known drift since source ruling
- scope mismatch verdict
- sunset trigger already known

Hard rule:

A precedent cannot silently cross version or world boundaries.
If the current case differs by version, service world, mobile lane, config world, or other material axis, the page must say whether the older ruling still travels.

### 6) Requested doctrine action card

Required rows:

- requested doctrine action
- requested exception if any
- appeal requested or not
- proposed overrule basis if any
- downstream claim effect
- review owner next step

Supported `requested_doctrine_action` values:

- `apply-as-binding`
- `apply-as-presumptive`
- `treat-as-persuasive`
- `distinguish-current-case`
- `propose-overrule`
- `create-new-precedent`
- `sunset-old-precedent`

Hard rule:

The requested action must be one explicit doctrine move.
`Looks similar` is not a doctrine action.

### 7) Decision sentence

Render one sentence only:

- `This docket compares [current case] to [source ruling], currently treats the earlier ruling as [binding_weight], and still blocks the stronger sentence that [overclaim].`

## Required interactions

- **Attach source verdict**
- **Mark matching fact**
- **Mark distinguishing fact**
- **Assign or lower binding weight**
- **Open appeal / propose overrule**
- **Create new precedent instead**

## Empty and failure states

If no prior ruling has been attached, show:

- `No source ruling attached yet. This case cannot claim precedent weight.`

If the only attached ruling is already superseded, show:

- `Attached ruling is superseded. Use it for history only or attach a newer doctrine source.`
''')

write('docs/1500-appeal-and-distinguish-review-page-binding-persuasive-overruled-and-version-scoped-doctrine-interface-spec.md', '''# Appeal and distinguish review page: binding, persuasive, overruled, and version-scoped doctrine interface spec

## Purpose

After the archive learned how to attach precedent dockets, it still needed one ordinary workspace for the next harder question:

> should this earlier ruling actually govern the new case, should we distinguish it, or should we overrule or sunset it because the facts, version, or world changed too much?

## Core decision

AnonSync must expose one first-class **Appeal and distinguish review** page whenever precedent weight is being materially affirmed, narrowed, distinguished, overruled, or sunset.

## Fixed page order

1. **Review header**
2. **Precedent stack card**
3. **Distinguishing-facts card**
4. **Version-drift card**
5. **Appeal gate card**
6. **Proposed doctrine verdict card**
7. **Decision sentence**

### 1) Review header

Show:

- review id
- current case id
- active precedent dockets reviewed
- review owner
- current doctrine risk level
- current strongest safe sentence

Supported `doctrine_risk_level` values:

- `low-consistency-risk`
- `moderate-consistency-risk`
- `high-overrule-risk`
- `unknown-doctrine-risk`

### 2) Precedent stack card

For each attached precedent, show:

- source ruling id
- binding weight
- source version window
- source world scope
- current status
- why it was attached

Hard rule:

The page must support more than one precedent at once.
Operators should not have to compare doctrine one article at a time.

### 3) Distinguishing-facts card

Required rows:

- facts common to all attached precedents
- facts distinguishing the current case
- facts that weaken only some precedents
- facts still unresolved
- disputed distinction claims

Hard rule:

A distinction must name the fact that does the doctrinal work.
`This one feels different` is not enough.

### 4) Version-drift card

Required rows:

- version or release drift since each source ruling
- world or lane drift since each source ruling
- later fixes or wording changes already known
- whether drift weakens, leaves intact, or supersedes old doctrine
- strongest blocked sentence because drift remains unresolved

Hard rule:

Later fixes or warning-text changes cannot remain implicit.
If doctrine changed because the product changed, the review must say so.

### 5) Appeal gate card

Required rows:

- who may uphold doctrine as-is
- who may distinguish locally
n- who may overrule or sunset doctrine
- burden needed for overrule
- burden needed for emergency exception
- whether interim hold is allowed

Hard rule:

Not every reviewer may overrule doctrine.
The page must publish the gate.

### 6) Proposed doctrine verdict card

Supported `doctrine_verdict` values:

- `apply-binding-doctrine`
- `apply-presumptive-doctrine`
- `treat-as-persuasive-only`
- `distinguish-current-case`
- `narrow-existing-precedent`
- `overrule-existing-precedent`
- `sunset-existing-precedent`
- `create-new-precedent`
- `issue-interim-hold`

Required rows:

- proposed doctrine verdict
- exact scope affected
- who must be notified
- downstream case impact
- stronger allowed sentence if accepted
- stronger blocked sentence if rejected

Hard rule:

The verdict must name whether old doctrine survives, narrows, or dies.
A review may not quietly resolve the current case without updating doctrine state.

### 7) Decision sentence

Render one sentence only:

- `This review currently [doctrine_verdict] for [scope], based on [distinguishing fact or drift], and leaves [blocked sentence] unsafe until finalized.`

## Required interactions

- **Compare attached precedents side by side**
- **Mark material distinction**
- **Downgrade precedent weight**
- **Open overrule path**
- **Issue interim hold**
- **Finalize doctrine verdict**

## Failure and edge states

If all attached precedents are only informative, show:

- `No attached precedent currently binds this case. Create new doctrine or proceed with local case-only reasoning.`

If version drift is unresolved, show:

- `Doctrine comparison incomplete: product drift may have changed the meaning of the older ruling.`
''')

write('docs/1501-precedent-proof-page-doctrine-adopted-exception-allowed-and-overrule-path-interface-spec.md', '''# Precedent proof page: doctrine adopted, exception allowed, and overrule path interface spec

## Purpose

After the archive learned how to review and distinguish precedent, it still needed one proof page that answers:

> what doctrine now actually governs this class of case, what exceptions are allowed, and how would a later operator know whether they are allowed to overrule it?

## Core decision

AnonSync must expose one first-class **Precedent proof** page whenever doctrine is materially adopted, narrowed, distinguished, overruled, or sunset.

## Fixed page order

1. **Doctrine summary card**
2. **Binding-weight proof card**
3. **Scope and exception card**
4. **Version-window card**
5. **Overrule-path card**
6. **Decision sentence**

### 1) Doctrine summary card

Required rows:

- governing doctrine sentence
- source ruling ids
- current doctrine class
- doctrine owner
- adoption time
- current status

Supported `doctrine_class` values:

- `case-only`
- `local-precedent`
- `estate-precedent`
- `temporary-interim-doctrine`
- `sunset-doctrine`

### 2) Binding-weight proof card

Required rows:

- adopted binding weight
- why that weight is justified
- unresolved contradiction if any
- what would lower the weight
- what would strengthen the weight

Hard rule:

The proof must explain *why* the doctrine weight is safe.
Weight may not be ceremonial.

### 3) Scope and exception card

Required rows:

- covered case class
- explicit exclusions
- allowed exception path
- required distinction facts for exception
- weaker surviving sentence outside scope

Hard rule:

Exceptions may not remain folklore.
If doctrine can be bypassed, the proof must publish the gate and the narrower surviving sentence.

### 4) Version-window card

Required rows:

- version window covered
- world or lane window covered
- known sunset trigger
- known supersession trigger
- freshness or rereview target

Hard rule:

Every precedent proof must declare its version and world window.
There is no timeless doctrine by accident.

### 5) Overrule-path card

Required rows:

- who may propose overrule
- who may approve overrule
- required evidence for overrule
- interim-hold behavior
- recall obligations for dependent cases

Hard rule:

Overrule is a first-class path, not a hidden social maneuver.

### 6) Decision sentence

Render one sentence only:

- `Doctrine for [case class] is currently [doctrine class] with [binding weight], covers [scope], and may be overruled only through [overrule path].`

## Required interactions

- **Publish doctrine**
- **Attach exclusion**
- **Define exception gate**
- **Set rereview date**
- **Open overrule path**

## Failure state

If doctrine is still only case-specific, show:

- `No reusable doctrine published yet. This ruling remains case-only and may not be cited as binding.`
''')

write('docs/1502-precedent-timeline-page-ruling-appeal-overrule-sunset-and-version-drift-events-interface-spec.md', '''# Precedent timeline page: ruling, appeal, overrule, sunset, and version drift events interface spec

## Purpose

After the archive learned how to prove doctrine, it still needed one chronology page for operators asking:

> how did this doctrine become what it is now, and which later appeal, fix, or version drift event changed what we are allowed to claim?

## Core decision

AnonSync must expose one first-class **Precedent timeline** page for every materially reused doctrine path.

## Required event families

- source ruling issued
- precedent docket opened
- doctrine adopted
- exception granted
- distinction recorded
- appeal opened
- precedent narrowed
- precedent overruled
- precedent sunset
- version drift detected
- downstream recall sent

## Event-row schema

Each row must show:

- timestamp
- event family
- affected doctrine sentence
- old binding weight
- new binding weight
- scope delta
- who caused the change
- downstream cases affected
- stronger sentence newly allowed or blocked

## Hard rules

### 1) Version drift is a doctrine event

A later product fix or changed warning meaning must appear on the doctrine timeline if it changes how older rulings should be read.

### 2) Overrule cannot erase history

The timeline must preserve what doctrine existed before the overrule and which dependent cases were still shaped by it.

### 3) Appeal must be durable

An appeal cannot live only inside comments on the old ruling.
It must appear as a timeline event with visible effect on doctrine certainty.

## Empty state

If no reusable doctrine exists yet, show:

- `No doctrine timeline yet. The case history exists, but no reusable precedent has been adopted.`
''')

write('docs/1503-precedent-lineage-receipt-page-binding-weight-scope-version-window-and-overrule-boundary-interface-spec.md', '''# Precedent lineage receipt page: binding weight, scope, version window, and overrule boundary interface spec

## Purpose

After the archive learned how to track doctrine history, it still needed one final handoff page that answers:

> what exactly is the current doctrine sentence, how strong is it, where does it apply, and how could a later operator lawfully challenge or overrule it?

## Core decision

AnonSync must expose one first-class **Precedent lineage receipt** whenever doctrine is published for reuse beyond the originating case.

## Fixed page order

1. **Receipt header**
2. **Current doctrine sentence card**
3. **Binding-weight and scope card**
4. **Version and world window card**
5. **Overrule and exception boundary card**
6. **Blocked stronger sentence card**

### 1) Receipt header

Show:

- precedent receipt id
- governing doctrine id
- source ruling ids
- current doctrine owner
- publication time
- latest rereview time
- current status

### 2) Current doctrine sentence card

Required rows:

- exact current doctrine sentence
- case class covered
- explicit exclusions
- allowed citation class
- weaker sentence outside scope

### 3) Binding-weight and scope card

Required rows:

- binding weight
- scope breadth
- dependent active cases
- known exception count
- latest distinction recorded

### 4) Version and world window card

Required rows:

- minimum version covered
- maximum tested version covered
- world or lane applicability
- known drift beyond window
- sunset or rereview trigger

### 5) Overrule and exception boundary card

Required rows:

- who may distinguish locally
- who may overrule globally
- evidence needed for each
- interim hold rule
- recall obligations if doctrine changes

### 6) Blocked stronger sentence card

Required rows:

- strongest safe doctrine sentence
- strongest blocked overclaim
- what evidence would unlock it
- what evidence would collapse it

## Hard rule

A precedent receipt must let a later operator answer four questions immediately:

- what is the doctrine?
- how strong is it?
- where does it apply?
- how can it lawfully change?

If any of those are missing, the receipt is incomplete.

## Empty state

If the ruling never became reusable doctrine, show:

- `No precedent receipt: this ruling remains case-only and may not be reused as doctrine.`
''')

prepend('README.md', readme_add)
prepend('docs/00-status.md', status_add)
prepend('docs/10-resilio-sync-evaluation.md', resilio_eval_add)
prepend('docs/11-resilio-borrow-line-and-non-clone-scorecard.md', scorecard_add)
prepend('docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md', clone_veto_add)
prepend('docs/20-product-direction.md', product_add)
prepend('docs/sources.md', sources_add)

print('apply_rev0393 complete')
