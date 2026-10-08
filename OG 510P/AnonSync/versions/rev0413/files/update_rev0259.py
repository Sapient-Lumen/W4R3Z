from pathlib import Path

root = Path('.')

def prepend(path_str, text):
    path = root / path_str
    old = path.read_text()
    path.write_text(text.rstrip() + "\n\n" + old)

# New docs
new_docs = {
    'docs/721-resilio-warning-taxonomy-blast-radius-and-least-strong-repair-evaluation.md': r'''# Resilio warning taxonomy, blast radius, and least-strong repair evaluation

## Why this seam matters

Another current official Resilio pass exposes a stronger non-clone reason than a generic `good troubleshooting docs` compliment.
Current official docs are actually fairly candid that a visible warning row is not one thing.
The current `Core warnings` article still separates tracker loss, low space on the default-folder-location disk, failed folder-list / identity sync, and license-management disablement.
The current `Service files missing / Cannot identify destination folder` article still says synchronization for that folder is suspended and that one repair path is remove/re-add after checking Archive and deleting `.sync`.
The current `Some internal tasks are taking time to complete` article still says the condition can be intermittent and recoverable rather than a hard stall.
The current `Time difference` article still says chronology trust is invalidated when peer clocks or timezone settings are wrong and that mobile devices may show only empty lists.
The current `Cannot download files` article still says a mesh may advertise files that later no peer still holds as full bytes.
The live Sync v3 line still runs through `3.1.2.1076`.

That candor is useful.
The non-clone problem is still warning ownership.
One ordinary operator answer is still reconstructed too late:

> **what kind of warning is this, how wide is it, what is the least-strong honest next rung, and what did acknowledging it actually change?**

## What current official docs still say

### 1) Resilio already distinguishes materially different warning classes

The current warning cluster already describes warnings with very different semantics:

- **recoverable hidden work** — `Some internal tasks are taking time to complete`
- **continuity damage** — `Service files missing`
- **chronology invalidation** — `Time difference`
- **source absence / ghost announcement** — `Cannot download files`
- **infrastructure / storage / identity-management conditions** — `Core warnings`

So the warning surface is already a taxonomy, even if the product does not compile it into one ordinary operator page family.

### 2) The blast radius changes by warning, but support prose still carries that answer

Current docs still imply very different scopes:

- `Service files missing` suspends synchronization **for that folder**
- `Time difference` invalidates chronology-sensitive comparison across peers and can empty mobile file lists
- `Cannot download files` is often a **subject/item-level** no-source problem rather than a full-seat failure
- `Some internal tasks...` can be **seat/resource pressure** without proving subject corruption
- `Core warnings` can describe account/identity sync trouble, tracker/bootstrap trouble, or storage-floor trouble

The operator still has to infer whether the current problem is item-scoped, subject-scoped, seat-scoped, or broader control-state damage.

### 3) The safest next rung is not the same across warnings

The current docs still imply very different least-strong actions:

- wait / observe for recoverable hidden work
- verify clocks for chronology invalidation
- restore a full source or accept absence for ghost-announced files
- disconnect/reconnect or remove/re-add for some local database or spine failures
- inspect identity/bootstrap/storage conditions for core warnings

That means a generic `Fix`, `Retry`, or `Dismiss` verb is too weakly typed.

### 4) Acknowledgement and repair residue still lack one durable product record

Current official docs still make it easy for an operator to remember only that a warning `went away`, not whether it:

- self-cleared after transient resource pressure
- was acknowledged without semantic repair
- required chronology repair
- required continuity reset
- still leaves residue or a claim ceiling afterward

## Why AnonSync should not clone this contract

AnonSync should borrow Resilio's candor that warning classes differ and that some warnings are recoverable while others are continuity-bearing.

AnonSync should **not** clone a contract where:

- one warning row does not publish its class and blast radius explicitly
- the least-strong safe next rung must be learned from scattered help pages
- acknowledgement can be mistaken for repair
- operators cannot reopen one durable record of what the warning meant, what changed, and what stronger sentence is still blocked

The product should instead own four ordinary surfaces:

1. **Warning page** — class, scope, safe sentence, and current seriousness
2. **Blocker scope** — seat / subject / item / hidden-state blast radius and unaffected neighbors
3. **Recovery rung** — least-widening repair ladder and escalation boundary
4. **Warning history** — acknowledgement, recurrence, residue, and proof continuity

## Tightened conclusion

Borrow Resilio's warning candor.
Do not clone a product contract where the operator still has to merge core-warning rows, one-off warning articles, and troubleshooting lore just to answer:

> **what kind of warning is this, how wide is it, what is the least-strong honest next move, and what did clearing it actually prove?**
''',
    'docs/722-warning-page-class-scope-and-safe-sentence-interface-spec.md': r'''# Warning page: class, scope, and safe sentence interface spec

## Purpose

Give one ordinary page that answers:

> what kind of warning is this, how serious is it, how wide is it, and what exact sentence is still safe to say right now?

This page exists because a warning row is often treated as self-explanatory when its true meaning may be transient load, chronology invalidation, source absence, continuity damage, or policy disablement.

## Core rule

Every durable warning must compile to a **warning record** with at least:

- warning class
- active scope / blast radius
- seriousness
- strongest safe sentence
- stronger forbidden sentence
- least-strong next rung
- current evidence and freshness

The UI may abbreviate the row, but it may not let the row outrun the record.

## Required sections

### 1) Warning now

Always show:

- warning title
- warning class (`transient-load`, `chronology-invalid`, `source-absent`, `continuity-damaged`, `storage-floor`, `bootstrap-failed`, `policy-disabled`, `unknown`)
- severity (`notice`, `degraded`, `blocked`, `unsafe-to-continue`, `unknown`)
- first seen / last seen / freshness of current evidence
- strongest safe sentence

Example safe sentences:

- `Work is delayed by local load; no continuity loss is proven.`
- `Chronology trust is invalid; winner claims are unsafe.`
- `This subject currently lacks a full byte source.`
- `Hidden control state for this subject is damaged; sync is suspended here.`

### 2) Scope and impact

Show which world is affected:

- item
- path group
n- subject/share
- seat/runtime
- identity/control plane
- storage root / default-folder disk

Also show unaffected neighbors when known.

### 3) Evidence basis

List the proofs that gave the warning its current class:

- current detectors / warning codes
- observed facts
- last successful contradictory proof if any
- freshness of the evidence
- whether the warning is self-reported, inferred, or externally corroborated

### 4) Safe wording boundary

The product must publish:

- strongest safe sentence
- stronger forbidden sentence
- why the stronger sentence is unsafe

Examples:

- safe: `Synchronization for this subject is suspended on this seat.`
- forbidden: `All local bytes are damaged.`
- safe: `No full source peer is currently proven.`
- forbidden: `The file is permanently gone.`

### 5) Next honest actions

Offer typed actions rather than generic `Fix`:

- `Inspect blocker scope`
- `Open recovery rung`
- `Collect stronger evidence`
- `Acknowledge with note`
- `Export warning packet`

## Required row grammar

A compact row should read like:

- `Chronology invalid · subject+peer pair · winner claims blocked`
- `Transient load · seat-local · wait or inspect motion basis`
- `Continuity damage · subject-local · reconnect or rebuild after archive check`
- `Source absent · item set · restore source or preserve absence verdict`

## Data model

- `warning_id`
- `warning_code`
- `warning_class`
- `severity`
- `scope_kind`
- `scope_ref`
- `first_seen_at`
- `last_seen_at`
- `evidence_freshness`
- `safe_sentence`
- `forbidden_sentence`
- `least_strong_next_rung`
- `ack_state`
- `history_ref`

## Failure this page prevents

Without this page, operators are pushed into support-lore reasoning and generic dismiss/retry behavior while the true warning class and blast radius remain implicit.

AnonSync should instead keep warning class, scope, evidence, and safe wording adjacent.
''',
    'docs/723-blocker-scope-page-seat-subject-item-and-hidden-state-blast-radius-interface-spec.md': r'''# Blocker scope page: seat, subject, item, and hidden-state blast radius interface spec

## Purpose

Answer the ordinary question:

> how wide is this problem really, what remains unaffected, and which stronger operations should stay blocked until scope is proven smaller?

This page exists because operators often jump from a warning row directly to a heavy repair without knowing whether the issue is item-local, subject-local, seat-local, or continuity-bearing hidden-state damage.

## Core rule

Every non-trivial warning must be able to open a **blocker scope** page.
The page must preserve both:

1. **affected scope** — the smallest world currently proven affected
2. **claim ceiling** — what stronger statements are still blocked because scope may be wider than currently proven

## Required sections

### 1) Smallest proven affected world

Show one primary scope class:

- `item-only`
- `path-subset`
- `subject/share`
- `seat/runtime`
- `identity/control-plane`
- `storage-root`
- `unknown-wider-than-current-proof`

Also show why that class won.

### 2) Possible wider spillover

List any wider worlds that remain plausible but unproven:

- sibling items in same subject
- all selective/hydrated descendants
- all subjects on same seat
- peers that depend on the same chronology or helper state
- hidden service/control state shared by several subjects

### 3) Unaffected neighbors

Whenever possible, prove what is currently outside the blast radius:

- other subjects still healthy on the same seat
- sibling items with fresh proof of availability
- route/discovery functioning even if one subject is blocked
- local bytes intact even if chronology or continuity is invalid

### 4) Stronger actions now blocked

Show which actions stay blocked until scope shrinks or proof improves:

- destructive replay
- successor/cutover approval
- winner/loser language
- detach / rebuild / branch promotion
- cohort-wide maintenance claims

### 5) Scope-tightening probes

Offer less-destructive scope probes first:

- inspect peer/item evidence
- inspect chronology evidence
- inspect control-spine integrity
- inspect source presence
- inspect storage-floor / resource evidence

## View grammar

A good scope summary line reads like:

- `Proven affected: this subject only · wider continuity spillover unproven`
- `Proven affected: seat-local load pressure · no subject corruption proven`
- `Proven affected: item set lacking source peers · seat remains healthy`
- `Proven affected: chronology invalid across peer pair · winner claims blocked beyond item subset`

## Data model

- `blocker_scope_id`
- `warning_id`
- `smallest_proven_scope_kind`
- `smallest_proven_scope_ref`
- `possible_wider_scopes[]`
- `unaffected_neighbors[]`
- `blocked_stronger_actions[]`
- `scope_probe_options[]`
- `claim_ceiling_summary`

## Failure this page prevents

Without this page, one subject-local warning can trigger seat-wide panic, or one seat-local load condition can provoke continuity-destroying repair.

AnonSync should instead force the product to state the smallest proven affected world and the stronger actions still blocked by uncertainty.
''',
    'docs/724-recovery-rung-page-least-widening-repair-and-escalation-boundary-interface-spec.md': r'''# Recovery rung page: least-widening repair and escalation boundary interface spec

## Purpose

Answer the ordinary question:

> what is the least-strong honest next move for this warning, what would a stronger move buy me, and what damage or widening comes with skipping ahead?

This page exists because troubleshooting lore often presents restart, rescan, reconnect, remove/re-add, restore-source, or rebuild actions as a loose list rather than a typed escalation ladder.

## Core rule

Every repairable warning must map to a **recovery rung ladder**.
The ladder must order actions from least-widening to strongest and must explain:

- what each rung proves
- what it does **not** prove
- what it risks mutating
- what stronger rung becomes justified only if the lower rung fails

## Required sections

### 1) Current least-strong recommended rung

Always publish:

- current recommended rung name
- why this rung is currently least-strong and sufficient
- what proof it may restore
- what evidence would justify escalation

Example rung kinds:

- `wait-and-observe`
- `inspect evidence`
- `refresh probe / rescan`
- `clock repair`
- `restore byte source`
- `disconnect / reconnect`
- `rebuild local database`
- `remove and re-add`
- `branch / preserve before destructive repair`

### 2) Full ladder

Render a compact table:

| Rung | Mutates live bytes? | Mutates continuity state? | Restores which proof? | Escalate when |
| --- | --- | --- | --- | --- |
| Observe | no | no | freshness only | condition persists beyond threshold |
| Rescan | no | no | index/detection proof | rescan contradicts nothing useful |
| Clock repair | no | no | chronology trust | drift remains or files still empty |
| Reconnect | maybe | local continuity state | route/local db proof | subject remains suspended |
| Remove/re-add | maybe | yes | clean local continuity | lower rungs failed and bytes preserved |

### 3) Skip-risk warning

If the operator skips the least-strong rung, show:

- what wider mutation occurs
- what evidence may be destroyed
- what future claims become weaker or stronger
- what preserve-first step is recommended first

### 4) Proof after success

Define the exact success witness for each rung:

- warning cleared with fresh evidence
- chronology trust restored
- source witness restored
- continuity rebuilt on this subject
- still blocked / escalate

### 5) Preserve-first branch

Whenever a stronger rung risks bytes or continuity evidence, offer:

- export witness packet
- preserve retained copy
- create clean branch
- snapshot local state

## Receipt rules

Every applied rung must emit a durable record of:

- requested rung
- rung actually used
- why it was justified
- what stronger rungs remained unused
- success witness or contradiction
- what residue still remains

## Data model

- `recovery_rung_review_id`
- `warning_id`
- `current_recommended_rung`
- `ladder[]`
- `skip_risk_summary`
- `preserve_first_options[]`
- `success_witness_contract`
- `applied_rung_receipt_ref`

## Failure this page prevents

Without this page, products slide from warning row to strong repair without proving why lighter rungs were insufficient.

AnonSync should instead make repair strength, mutation cost, and escalation proof explicit.
''',
    'docs/725-warning-history-page-acknowledgment-residue-evidence-and-recurrence-interface-spec.md': r'''# Warning history page: acknowledgment, residue, evidence, and recurrence interface spec

## Purpose

Answer the later question:

> this warning is gone or quieter now, but what exactly happened, what was merely acknowledged, what residue remains, and how often has this class come back?

This page exists because operators often remember only that a banner disappeared, not whether the system self-recovered, an operator acknowledged it, or a strong repair rebuilt continuity.

## Core rule

Every durable warning must have a **warning history** timeline.
The timeline must distinguish four different outcomes:

1. `self-cleared`
2. `acknowledged-no-repair`
3. `repair-applied`
4. `muted-but-recurrent`

The product must never flatten those into one `resolved` badge.

## Required sections

### 1) Warning lifecycle timeline

Show:

- first seen
- severity changes
- evidence changes
- acknowledgements
- applied repair rungs
- self-clear / recurrence events
- current residue state

### 2) Acknowledgment semantics

Whenever the user acknowledged the warning, preserve:

- who acknowledged it
- scope of acknowledgment
- whether visibility changed only locally or across collaborators
- what acknowledgment explicitly did **not** repair

### 3) Residue after clear

Even if the banner is gone, show whether residue remains:

- chronology repaired but loser fate still unknown
- continuity rebuilt but old local state discarded
- source absence cleared after a peer returned
- transient load self-cleared without structural mutation
- warning suppressed while detector remains degraded

### 4) Recurrence pattern

Show:

- recurrence count
- recurring class/fingerprint
- last interval between occurrences
- whether the same repair rung has failed repeatedly
- whether escalation is now recommended by history, not just current state

### 5) Exportable statement

The page must be able to emit one honest sentence such as:

- `Acknowledged locally; no repair was applied.`
- `Self-cleared after transient load; no continuity damage proved.`
- `Cleared after reconnect to same path; chronology remains valid.`
- `Recurred three times after the same local storage-floor condition.`

## Data model

- `warning_history_id`
- `warning_code`
- `scope_ref`
- `events[]`
- `ack_events[]`
- `repair_receipts[]`
- `self_clear_events[]`
- `recurrence_count`
- `residue_state`
- `exportable_statement`

## Failure this page prevents

Without this page, operators confuse silence with repair, forget recurrence, and lose the evidence trail needed to choose a stronger rung next time.

AnonSync should instead preserve warning memory as a first-class history object.
'''
}
for path, text in new_docs.items():
    (root / path).write_text(text.strip() + "\n")

# Prepend addenda to core docs
prepend('docs/00-status.md', r'''## Latest addendum — warning taxonomy, blocker scope, and least-strong repair after rev0258

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **warning page / blocker scope / recovery rung / warning history**

Current official Resilio docs are actually fairly candid that warnings are not one thing. The current `Core warnings` article still separates tracker/bootstrap trouble, low space on the default-folder-location disk, failed folder-list / identity sync, and license-management disablement. The current `Service files missing` article still says synchronization for that folder is suspended. The current `Some internal tasks are taking time to complete` article still says the condition can be intermittent and recoverable rather than a hard stall. The current `Time difference` article still says chronology trust is invalidated and mobile devices may show empty lists. The current `Cannot download files` article still says a tree may advertise files that no peer now holds as full bytes.
So the tighter non-clone line is:

> borrow Resilio's candor that warning classes differ, but refuse any product contract where operators still reconstruct `what kind of warning is this, how wide is it, what is the least-strong safe next rung, and what did acknowledgement really change` from one-off articles and troubleshooting lore.

That yields four more ordinary product-owned pages:

- **Warning page**
- **Blocker scope**
- **Recovery rung**
- **Warning history**''')

prepend('docs/10-resilio-sync-evaluation.md', r'''## Revision addendum — warning taxonomy, blast radius, and least-strong repair after rev0258

Another current official Resilio pass sharpens one more reason to **adapt, not clone**.
Current official Resilio docs are still admirably candid that warning rows do not all mean the same thing: the active v3 line still runs through `3.1.2.1076`; current `Core warnings` docs still separate tracker/bootstrap trouble, low space on the default-folder-location disk, failed folder-list / identity sync, and license-management disablement; current `Service files missing` docs still say synchronization for that folder is suspended and that repair may require remove/re-add after Archive check and `.sync` cleanup; current `Some internal tasks are taking time to complete` docs still say the condition may be intermittent and recoverable rather than a hard stall; current `Time difference` docs still say chronology trust is invalidated when peer clocks or timezone settings are wrong and that mobile may show empty lists; and current `Cannot download files` docs still say some announced items may have no remaining full source peers.

That candor is useful.
The non-clone problem is still warning ownership.
One ordinary operator answer is still scattered across warning articles and troubleshooting prose:

> what kind of warning is this, how wide is it, what is the least-strong honest next rung, and what did clearing or acknowledging it actually prove?

So this pass promotes four replacement pages:

- **Warning page** — class, seriousness, scope, and safe sentence
- **Blocker scope** — seat / subject / item / hidden-state blast radius and blocked stronger actions
- **Recovery rung** — least-widening repair ladder and escalation boundary
- **Warning history** — acknowledgement, repair, recurrence, and residue continuity''')

prepend('docs/11-resilio-borrow-line-and-non-clone-scorecard.md', r'''## Revision addendum — scorecard after rev0258: borrow warning candor, reject troubleshooting archaeology

Another current Resilio pass improves the scorecard in one more narrow place.

### Borrow

Keep borrowing these traits:

- admitting that warnings really are typed conditions rather than generic failure mood
- admitting that some warnings are recoverable transient load while others are chronology-bearing, source-bearing, or continuity-bearing
- admitting that the same visible severity band can still have very different blast radii
- admitting that some strong repairs should come only after archive check, clock repair, or source restoration

### Refuse to clone

Do not clone these traits:

- making operators infer blast radius from article lore instead of one blocker-scope page
- flattening acknowledgement and repair into the same `resolved` memory
- presenting `retry`, `dismiss`, or `fix` as if every warning had the same least-strong next step
- scattering the safe next rung across core warnings, one-off warning pages, and broad troubleshooting checklists

### Stronger replacement

AnonSync should publish four first-class surfaces instead:

- **Warning page**
- **Blocker scope**
- **Recovery rung**
- **Warning history**

The governing rule is simple:

> if a warning can change scope, repair strength, or safe wording, the product must publish its class, blast radius, least-strong next rung, and acknowledgement residue before the operator treats it as just another banner.''')

prepend('docs/20-product-direction.md', r'''## Revision addendum — warning taxonomy, blocker scope, and repair-ladder honesty after rev0258

The product direction now has to lock in one more explicit rule:

- **warnings are typed operational objects, not just colored banners**

Current official Resilio docs are good evidence that the underlying truth is already there: tracker/bootstrap warnings, low-space warnings, chronology-invalid warnings, source-absent warnings, continuity-damage warnings, and recoverable hidden-work warnings are all materially different. The product should therefore own that difference directly.

AnonSync should treat every serious warning as a compiled object with:

- warning class
- blast radius
- strongest safe sentence
- least-strong next rung
- recurrence / residue memory

That means `dismiss`, `retry`, and `resolved` are never enough on their own.
The product should instead require one ordinary page for warning meaning, one for blocker scope, one for least-widening repair, and one for durable warning history.''')

prepend('docs/50-roadmap.md', r'''## Latest roadmap addendum — promote warnings from banner folklore into typed repair objects

A further current Resilio pass suggests the roadmap should now reserve one explicit tranche for:

- warning-class posture instead of generic banner rows
- blocker-scope proof before heavy repair
- least-widening recovery ladders instead of troubleshooting folklore
- warning-history receipts that distinguish acknowledgement from real repair

Why this is next-worthy:

Current official docs are candid that `core warning`, `time difference`, `service files missing`, `cannot download files`, and `some internal tasks...` are different truths, but the least-strong safe action still leaks across several articles.
AnonSync should lock that down as ordinary product truth rather than support archaeology.''')

prepend('docs/64-critical-open-questions.md', r'''## 0i) How aggressive should warning typing and recurrence memory be before the product turns every transient condition into ceremony?

The archive now requires explicit warning pages, blocker-scope proof, least-widening recovery ladders, and warning-history timelines.
What remains unresolved is the calibration budget:

- when a transient load or one-off source absence should surface as a durable warning object versus a lighter notice
- how much recurrence should automatically upgrade a condition into a stronger repair recommendation
- whether acknowledgement should ever mute only the current seat, or whether some warning classes must remain constellation-visible until repaired
- how much residue history should remain attached after a warning self-clears so operators can still choose a stronger rung next time

This matters because weak typing recreates troubleshooting folklore, while over-strong typing can make ordinary transient conditions feel ceremonial and noisy.''')

prepend('docs/sources.md', r'''## Sources addendum — rev0259 warning taxonomy, blocker scope, and least-strong repair

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
- https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log''')

# README replacement section
readme = root / 'README.md'
old = readme.read_text()
new_header = r'''# AnonSync

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
'''
readme.write_text(new_header + "\n" + old)
