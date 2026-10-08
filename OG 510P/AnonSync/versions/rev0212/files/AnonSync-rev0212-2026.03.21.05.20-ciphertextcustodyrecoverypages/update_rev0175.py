from pathlib import Path
import shutil
import textwrap

src = Path('/mnt/data/rev0174_work/AnonSync-rev0174-2026.03.20.19.34-resiliopathcontinuitypages')
dst = Path('/mnt/data/rev0174_work/AnonSync-rev0175-2026.03.20.19.52-surfaceparitysavebackpages')
if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(src, dst)

# remove old update script if copied? keep all old, add new.

# New docs
new_docs = {
    'docs/22-resilio-surface-parity-external-edit-background-and-mobile-storage-evaluation.md': '''# Resilio surface parity, external edit, background delivery, and mobile storage evaluation

## Purpose

The archive already has stronger answers for shell acceleration, alert delivery, host cadence, path continuity, and repair ladders.
This document asks a narrower but still ordinary question that current Resilio docs keep making visible:

> when the same subject is opened, edited, cleared, backgrounded, or inspected from desktop, Linux/WebUI, Android, and iOS, where does the product itself own one stable answer, and where does the operator still have to remember platform folklore?

This is not a complaint that Resilio ignores platform reality.
It does not.
The problem is that the ordinary operator answer still leaks across too many platform-specific articles.

## Current Resilio evidence that matters

Current official docs still show all of the following at once:

- Linux has no OS integration, no tray icon, and no notifications outside Sync UI.
- Linux sharing, license-seat links, and activation still route through `Enter a key or link`, and WebUI remains the ordinary control surface there.
- Desktop can keep syncing while the window is hidden, Linux can run headlessly through WebUI, Android can run in the background but may still be stopped by task killers, auto-sleep, battery saver, or forbidden-network policy, and iOS cannot transfer data in the background.
- iOS `Open In...` editing works on a copied file, not a live bind; to propagate changes the edited copy must be sent back into Sync.
- iOS deletion from the local app can simply un-sync the file locally rather than issuing a global delete.
- Android share details expose path, archive toggle, relay/tracker/LAN/known-host settings, and `Clear` versus `Disconnect`, while iOS exposes a different but overlapping share-details grammar.
- iOS keeps files in its sandbox; storage accounting splits app data from user data; clearing local material depends on Selective Sync being enabled.
- iOS shared-link history, download retention, and on-device file presence still split between `Downloads`, `Shared links`, and the broader storage page.
- Android `Simple Mode` hides path/root choice and forces new shares into `Downloads/Sync`, while disabling it restores explicit location choice.

These are all useful facts.
The problem is that they still do not add up to one stable product-owned answer for ordinary cross-surface behavior.

## Where Resilio is genuinely good

### 1) It admits that surfaces are not equivalent

Resilio does not pretend that desktop shell, Linux/WebUI, Android, and iOS all expose the same verbs.
That honesty is good and AnonSync should keep it.

### 2) It is candid about iOS copy semantics

The iOS docs plainly say that external-app editing happens on a copy and that the edited file must be sent back.
That is much better than implying a live document bind that does not exist.

### 3) It is candid about background limits

The docs are also straightforward that Android background delivery is contingent, iOS background delivery is unavailable, and Linux headless control is WebUI-shaped.
AnonSync should keep that candor.

### 4) It exposes local-storage pressure as a first-class reality on mobile

Resilio still makes Selective Sync, placeholder clearing, sandbox storage, and share-specific downloads real user concepts instead of pretending that mobile storage is infinite.
That is useful and worth borrowing.

## Why this still does not earn cloning

### 1) The ordinary surface answer still fragments by platform article

A user asking `can I do this here?` still has to assemble the answer from Linux peculiarities, Android interface pages, iOS interface pages, background notes, and edit/storage peculiarities.
That is not one stable page contract.

### 2) External edit semantics still live in specialist lore

The iOS `copy out, edit elsewhere, send back` contract is honest, but it is not owned by a universal action page that would naturally explain `open`, `edit`, `save back`, and duplicate risk.

### 3) Freshness expectation is still scattered across background, battery, network, and task-killer notes

The operator still reconstructs `will this keep receiving updates while I am away?` from separate platform behavior notes rather than one page publishing current background eligibility and suspend gates.

### 4) Mobile storage truth is still split across multiple surfaces

On iOS in particular, the operator still needs several pages to answer:

- where the bytes physically live
- what counts as app data versus user data
- what `Clear synced files` or `Remove from this device` actually removes
- which things remain in history after local removal
- whether a removed local copy is reacquirable later

### 5) Surface asymmetry still leaks into creation and path choice

Android `Simple Mode`, iOS sandboxing, Linux WebUI, and desktop shell affordances all shape where work begins and what verbs are visible, but those facts still are not gathered into one surface-capability answer.

## What AnonSync should borrow

AnonSync should borrow all of these ideas:

- surface-specific capability honesty
- explicit copy-versus-live-bind edit semantics
- background-delivery candor with named suspend reasons
- mobile storage accounting and placeholder-based clearance
- explicit network and battery gates for delivery on constrained devices
- per-surface fallback paths when a stronger affordance is unavailable

## What AnonSync should refuse to clone

AnonSync should refuse these interface shapes:

- letting capability truth live mainly in platform-specific help pages
- hiding copy/export/save-back semantics inside one platform tutorial
- treating background freshness as a generic `online/offline` badge
- scattering local-storage truth across downloads, settings, and share-detail surfaces without one ordinary storage page
- letting creation/path-picking differences remain side effects of hidden simple-mode or sandbox assumptions

## The replacement page family this evaluation now requires

This pass therefore adds four more ordinary pages:

1. `309-surface-capability-page-action-parity-and-reason-coded-gaps-interface-spec.md`
2. `310-external-edit-review-page-copy-bind-saveback-and-duplicate-risk-interface-spec.md`
3. `311-background-delivery-page-suspend-gates-freshness-floor-and-catchup-risk-interface-spec.md`
4. `312-mobile-storage-page-sandbox-clearance-downloads-and-reacquireability-interface-spec.md`

The sharpened line is now:

> when Resilio keeps cross-surface truth honest only by spreading it across Linux/WebUI peculiarities, Android settings, iOS edit/storage caveats, and background notes, AnonSync should copy the honesty and replace the pages.
''',
    'docs/309-surface-capability-page-action-parity-and-reason-coded-gaps-interface-spec.md': '''# Surface capability page: action parity and reason-coded gaps interface spec

## Purpose

This page answers one ordinary question:

> what can this seat actually do from *this* surface right now, what is missing here, and why?

The page exists because `desktop`, `web`, `android`, `ios`, `cli`, and `narrow width` are not decorative skins.
They are capability projections with real gaps.

## Core decision

Every seat/surface pair must render one first-class **Surface capability** page.
That page owns:

- current surface identity
- action families that are available here
- action families that are unavailable here
- whether the gap is policy, platform, permissions, background state, or missing acceleration
- the strongest available fallback surface

The workbench must not force the operator to infer those truths from absent buttons.

## Primary layout

The page always renders the same regions in the same order:

1. surface strip
2. capability matrix
3. current blockers card
4. fallback / escalation card
5. recent parity receipts

### 1) Surface strip

Show:

- current surface label
- seat/runtime label
- confidence verdict: `full`, `reduced`, `degraded`, `projection-only`
- one next honest action

### 2) Capability matrix

Rows are action families, not raw buttons.
At minimum show rows for:

- open / reveal bytes
- edit in place
- external edit with save-back
- clear local bytes
- destroy globally
- restore / history access
- share / approve / revoke
- path choice / relocation
- background delivery
- diagnostic capture

Each row shows:

- `available here`
- `available with review`
- `available elsewhere only`
- `blocked`
- exact reason code

### 3) Current blockers card

Show the winning blockers, for example:

- platform sandbox
- no shell integration
- WebUI-only seat
- battery saver / auto-sleep
- forbidden network
- readonly permission
- background delivery unavailable
- missing local bytes

Each blocker names the verb family it constrains and whether the condition is mutable.

### 4) Fallback / escalation card

For every unavailable high-value action, show:

- strongest fallback action here
- stronger surface that can do the full action
- whether state or bytes must travel first
- what semantic loss the fallback introduces

### 5) Recent parity receipts

Receipts show:

- surface
- verb family
- parity verdict
- blocker or fallback reason
- who observed or approved it
- time

## Non-negotiable rules

### Rule 1 — missing UI is not a capability explanation

Absence of a control is never the primary answer.
The page must publish why the action is absent.

### Rule 2 — fallback must preserve semantic truth

If a surface can only export-copy rather than edit live, or can only queue work rather than finish it now, the page must say so explicitly.

### Rule 3 — capability must be reason-coded

`Unavailable` is insufficient.
Every gap needs a winning reason class the operator can inspect.

## Honest outputs

The page may conclude:

- `full parity here`
- `reduced but safe`
- `copy-based fallback only`
- `background-disabled surface`
- `escalate to stronger surface`

It may not collapse all surface differences into one generic `limited on mobile` or `web version` label.
''',
    'docs/310-external-edit-review-page-copy-bind-saveback-and-duplicate-risk-interface-spec.md': '''# External edit review page: copy, bind, save-back, and duplicate risk interface spec

## Purpose

This page owns the truth of opening a file in another application when the current surface cannot promise a live writable bind.
It answers:

> am I editing the real synced object, a temporary local materialization, or an exported copy; what must happen for changes to re-enter continuity; and what duplicate or replacement risk follows?

## Core decision

Whenever a seat offers `Open in...`, `Edit with...`, export-to-app, or similar cross-app flow, it must be backed by one first-class **External edit review** page.

That page owns:

- source object identity
- edit substrate: live bind / local materialization / exported copy
- write-back path
- replacement versus sibling-create expectation
- duplicate / stale-original risk
- save-back receipt state

## Primary layout

The page renders the same regions:

1. action strip
2. source / substrate card
3. save-back contract card
4. duplicate and stale-original risk card
5. receipts and recovery

### 1) Action strip

Show:

- file title
- chosen target app or tool
- substrate verdict: `live`, `materialized-local`, `copy-out`, `unknown`
- one next honest action

### 2) Source / substrate card

Show:

- current source path and byte posture
- whether the target app receives the original object handle or a copied payload
- whether edits can stream back automatically
- whether the source must stay present during editing

### 3) Save-back contract card

Show:

- `changes sync automatically`
- `must save back explicitly`
- `must import as replacement`
- `save-back blocked`

If explicit save-back is required, show the exact required route and whether the original must be replaced, removed first, or can coexist safely.

### 4) Duplicate and stale-original risk card

Show:

- whether the old original remains in place while editing
- whether save-back will create a sibling rather than overwrite the original
- whether remote peers would briefly observe disappearance then reappearance
- whether later local edits could target the stale original by mistake

### 5) Receipts and recovery

Show recent edit/export/import receipts and offer:

- `Reveal original`
- `Reveal edited import candidate`
- `Replace original now`
- `Keep both with explicit rename`
- `Discard detached copy`

## Rules

### Rule 1 — copy versus live bind must be explicit before launch

The page must not let the operator discover only afterward that the external app received a copy.

### Rule 2 — save-back is a first-class step

If write-back is not automatic, the required return path must be part of the action contract.

### Rule 3 — replacement and coexistence must stay separate

The page must distinguish `replace original`, `add as new sibling`, and `keep detached external copy`.

## Honest outputs

This page may conclude:

- `live edit`
- `copy edit with explicit save-back`
- `copy edit with sibling risk`
- `readonly export only`
- `edit blocked on this surface`

It may not compress all of those into one generic `Open in app` action.
''',
    'docs/311-background-delivery-page-suspend-gates-freshness-floor-and-catchup-risk-interface-spec.md': '''# Background delivery page: suspend gates, freshness floor, and catch-up risk interface spec

## Purpose

This page owns the answer to:

> while I am not staring at this surface, will this seat keep detecting, sending, and receiving changes; what can suspend that behavior; and what catch-up risk appears afterward?

The page exists because `online` is not an honest enough answer.
Background delivery depends on platform, runtime, battery, network, and byte posture.

## Core decision

Every seat must expose one first-class **Background delivery** page.
That page owns:

- platform background eligibility
- current suspend gates
- freshness floor while unattended
- wake or catch-up interval
- mutation-risk notes after offline / suspended periods

## Primary layout

The page renders the same regions:

1. background strip
2. eligibility card
3. suspend-gates stack
4. freshness and catch-up card
5. receipts and actions

### 1) Background strip

Show:

- current seat/surface
- verdict: `continuous`, `conditional`, `foreground-only`, `stopped`
- one next honest action

### 2) Eligibility card

Show:

- whether the platform/runtime can deliver in background at all
- whether hidden window / tray / headless web still counts as active runtime
- whether foreground-only constraints apply
- whether current byte posture or missing bytes weaken background usefulness

### 3) Suspend-gates stack

Show the currently winning gates in precedence order, for example:

- app fully closed
- battery saver
- auto-sleep
- forbidden network / Wi-Fi-only miss
- OS task killer or memory pressure
- host asleep or storage unavailable
- permission / connectivity block

Each gate shows:

- whether it merely delays or fully blocks
- whether remote changes are still accumulating elsewhere
- exact condition to clear the gate

### 4) Freshness and catch-up card

Show:

- expected unattended freshness floor
- next wake / poll / resume expectation if not continuous
- whether a restart or foreground return triggers re-index or catch-up scan
- whether offline local edits introduce stale-overwrite or conflict risk on resume

### 5) Receipts and actions

Receipts show suspension, resume, and catch-up events.
Actions may include:

- `Permit stronger background operation`
- `Change battery / sleep rule`
- `Allow network`
- `Open foreground catch-up now`
- `Reveal resume risk explanation`

## Rules

### Rule 1 — background truth must be platform-specific and current

The page must distinguish `desktop hidden but active`, `headless web runtime`, `android conditional background`, and `foreground-only` states.

### Rule 2 — suspend reasons must be named, not guessed

The page must publish the winning current gate instead of leaving the operator to guess whether nothing is happening because of battery, network, permissions, or platform law.

### Rule 3 — catch-up risk must stay adjacent to resume

If resume can re-index, overwrite stale edits, or otherwise widen risk, the page must state that before the operator trusts freshness.

## Honest outputs

The page may conclude:

- `continuous background delivery`
- `conditional background delivery`
- `foreground-only delivery`
- `suspended by battery or network gate`
- `resume carries stale-edit risk`

It may not flatten all of those into one generic `offline` or `paused` badge.
''',
    'docs/312-mobile-storage-page-sandbox-clearance-downloads-and-reacquireability-interface-spec.md': '''# Mobile storage page: sandbox, clearance, downloads, and reacquireability interface spec

## Purpose

This page answers:

> where do this seat's bytes actually live, what counts against local storage, what exactly will be removed by each cleanup action, and can the cleared material be reacquired later?

The page exists because mobile storage is a custody boundary, not just a quota bar.

## Core decision

Every constrained or sandboxed seat must expose one first-class **Mobile storage** page.
That page owns:

- storage container or sandbox facts
- app data versus user data accounting
- share-local bytes versus one-off downloads versus outbound shared-link residue
- cleanup verbs and their scope
- reacquireability of cleared bytes

## Primary layout

The page always renders the same regions:

1. storage strip
2. accounting card
3. residency classes card
4. cleanup action matrix
5. reacquireability and history card
6. receipts

### 1) Storage strip

Show:

- device / seat name
- storage container verdict: `sandboxed`, `shared filesystem`, `mixed`, `unknown`
- pressure verdict
- one next honest action

### 2) Accounting card

Show at minimum:

- app/runtime data
- user data inside synced shares
- one-off downloads
- outbound shared-link residue if modeled separately
- free / pressured / exhausted local capacity verdict

### 3) Residency classes card

Group local bytes by class:

- synced-share bytes
- placeholders only
- downloads from one-off send/share flows
- outbound share residue / transfer records
- service/runtime data

Each class shows whether it is visible in the filesystem, in app-local storage only, or both.

### 4) Cleanup action matrix

For each cleanup verb show exactly what it removes:

- `clear local synced files`
- `remove from this device`
- `remove from all devices`
- `delete download only`
- `clear history only`
- `purge app/runtime cache`

The matrix must publish:

- which residency classes are affected
- whether placeholders remain
n- whether transfer history remains
- whether remote peers are changed
- whether Selective Sync or another prerequisite is required

### 5) Reacquireability and history card

Show:

- whether cleared synced files are reacquirable later
- whether one-off downloads can be re-downloaded from history or require a live source again
- whether outbound-share records persist after local file removal
- what survives as a receipt after bytes are gone

### 6) Receipts

Show storage-clearing and reacquire receipts with before/after pressure deltas when known.

## Rules

### Rule 1 — local removal scope must be concrete

The page must say whether cleanup removes only local bytes, only UI history, both, or also remote copies.

### Rule 2 — reacquireability must stay adjacent to cleanup

Operators should not discover after clearing that the only full copy is gone or that history survived without bytes.

### Rule 3 — sandbox truth is public state

If the seat stores bytes inside an app sandbox or similarly constrained container, the page must say so explicitly.

## Honest outputs

This page may conclude:

- `local bytes clearable and safely reacquirable`
- `cleanup leaves history only`
- `cleanup removes local bytes but preserves remote continuity`
- `cleanup would strand the last local full copy`
- `storage pressure remains in app/runtime data`

It may not collapse all local cleanup into one generic `free up space` action.
'''
}
for rel, content in new_docs.items():
    p = dst / rel
    p.write_text(content)

# Append sections to existing docs
append_map = {
    'docs/10-resilio-sync-evaluation.md': '''

## Revision addendum — surface parity, external edit, background delivery, and mobile storage after rev0175

Current official Resilio docs still show another useful but scattered truth in an ordinary product seam:

- Linux/WebUI, desktop, Android, and iOS do not expose the same action families, and Resilio is better than average at admitting it
- iOS external-app editing is copy-based and requires explicit save-back into Sync
- Android background delivery is conditional, desktop hidden-window delivery stays active, Linux headless control is WebUI-shaped, and iOS background transfer is unavailable
- Android `Simple Mode` and mobile share settings materially change path choice, visibility, and local-storage behavior
- iOS storage, downloads, shared-link residue, and local clearing semantics still span several distinct pages and surfaces

That means the product ideas are useful, but the page contracts still do not earn cloning.

AnonSync should therefore add one-page answers for:

- **Surface capability** — what this surface can really do now, what it cannot, and why
- **External edit review** — whether another app gets a live bind or a copy, and what save-back contract applies
- **Background delivery** — whether unattended send/receive is continuous, conditional, foreground-only, or blocked
- **Mobile storage** — where bytes live locally, what each cleanup verb removes, and whether the bytes are reacquirable later
''',
    'docs/11-resilio-borrow-line-and-non-clone-scorecard.md': '''

## Further scorecard lines after rev0175

| Product line | Resilio signal | AnonSync verdict | Why we should not just clone it | AnonSync replacement |
| --- | --- | --- | --- | --- |
| Surface capability truth | Honest but article-shaped | **Adapt** | Resilio admits platform asymmetry, but the ordinary answer still depends on Linux peculiarities, Android/iOS UI docs, and separate behavior notes | `309-surface-capability-page-action-parity-and-reason-coded-gaps-interface-spec.md` |
| External edit semantics | Honest but too hidden | **Adapt** | iOS copy/edit/save-back truth is real, but it still lives in one platform tutorial instead of one ordinary review surface | `310-external-edit-review-page-copy-bind-saveback-and-duplicate-risk-interface-spec.md` |
| Background freshness | Real but scattered | **Adapt** | Continuous, conditional, and foreground-only delivery still require cross-reading background, battery, network, and platform pages | `311-background-delivery-page-suspend-gates-freshness-floor-and-catchup-risk-interface-spec.md` |
| Mobile storage and cleanup | Useful but split | **Adapt** | Sandbox, downloads, shared links, clear-local-files, and history residue remain spread across several mobile surfaces | `312-mobile-storage-page-sandbox-clearance-downloads-and-reacquireability-interface-spec.md` |

The sharpened line is now:

> when Resilio keeps cross-surface truth honest only by splitting it across Linux/WebUI peculiarities, Android settings, iOS edit/storage caveats, and background notes, AnonSync should copy the honesty and replace the pages.
''',
    'docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md': '''

### K) Surface asymmetry and save-back semantics

Current official Resilio docs still give useful facts here, but they still fail the clone tests in an ordinary seam:

- Linux/WebUI, desktop, Android, and iOS have materially different verb families
- iOS external edit is copy-based and needs explicit save-back
- Android background work is conditional while iOS background transfer is unavailable
- Android simple-mode and mobile storage choices materially alter path choice and local-byte semantics
- mobile cleanup truth is split across share details, downloads, storage pages, and history surfaces

That fails Test 1 and Test 3.
One ordinary question (`what can I do from this surface, what happens if I edit in another app, and what survives local cleanup?`) still does not have one stable page answer.

AnonSync should therefore refuse direct cloning and instead require:

- a first-class **Surface capability** page
- a first-class **External edit review** page
- a first-class **Background delivery** page
- a first-class **Mobile storage** page
''',
    'docs/20-product-direction.md': '''

## Revision addendum — surface parity, save-back, background freshness, and mobile storage after rev0175

The product direction now owes four more explicit ordinary surfaces:

- **Surface capability** so every surface can publish its real verbs, its missing verbs, and the winning reason for each gap
- **External edit review** so copy-based editing, explicit save-back, replacement, and sibling-risk stay visible before launch
- **Background delivery** so `continuous`, `conditional`, `foreground-only`, and `stopped` remain first-class operational answers rather than folklore
- **Mobile storage** so sandbox facts, app-versus-user-data accounting, cleanup scope, and reacquireability stay adjacent
''',
    'docs/30-interface-spec.md': '''

## Revision addendum — surface parity and mobile save-back page families after rev0175

The interface grammar must now also preserve four additional page families without semantic drift:

- **Surface capability** so every seat/surface pair can publish action parity, missing verbs, and reason-coded gaps
- **External edit review** so `open in another app` can publish copy-vs-live-bind, save-back contract, and duplicate risk
- **Background delivery** so unattended freshness, suspend gates, and catch-up risk have one stable grammar
- **Mobile storage** so sandbox, downloads, cleanup matrix, and reacquireability remain one answer instead of several scattered mobile views
''',
    'docs/38-operator-workbench-interface-spec.md': '''

## Revision addendum — workbench coverage for surface parity and save-back pages after rev0175

The workbench must now also preserve four additional page families without semantic drift:

- **Surface capability** so any action sheet, details drawer, or narrow view can explain why a verb is absent here and where it remains available
- **External edit review** so cross-app launches do not silently hide copy/export/save-back semantics
- **Background delivery** so unattended freshness and suspend reasons are inspectable without leaving the workbench
- **Mobile storage** so local pressure, cleanup scope, and reacquireability can be opened directly from constrained seats
''',
    'docs/40-architecture-decisions.md': '''

## ADR-180 — Surface parity must be reason-coded, not inferred from missing controls

**Decision:** Every seat/surface pair must publish a reason-coded capability matrix showing what verbs are available here, what verbs are unavailable, and which stronger surface can complete them.

**Why:** Current Resilio docs are candid that desktop, Linux/WebUI, Android, and iOS differ materially, but the ordinary answer still lives in separate platform articles rather than one stable page.

**Implications:**

- surface-capability becomes a first-class page and receipt family
- absent buttons no longer count as sufficient explanation
- fallback surfaces must remain semantically honest about what is lost here

## ADR-181 — External edit must declare copy-versus-live-bind before launch

**Decision:** Any cross-app edit flow must state whether the target app receives a live writable bind, a local materialization, or an exported copy, together with the exact save-back contract.

**Why:** Current Resilio docs honestly describe iOS copy-based editing, but only in a platform tutorial instead of next to the action itself.

**Implications:**

- external-edit-review becomes a first-class page
- save-back becomes an explicit step when required
- replacement, sibling-create, and detached-copy outcomes remain distinct

## ADR-182 — Background freshness must publish suspend gates and catch-up risk

**Decision:** Background delivery must model platform eligibility, current suspend gates, unattended freshness floor, and post-resume catch-up risk explicitly.

**Why:** Current Resilio docs are candid about desktop, Linux, Android, and iOS differences, but still spread the answer across background, battery, task-killer, network, and platform notes.

**Implications:**

- background-delivery becomes a first-class page and receipt family
- `online` is no longer treated as an adequate unattended-delivery answer
- stale-edit and resume risk remain adjacent to catch-up actions

## ADR-183 — Mobile storage is custody, not merely quota

**Decision:** Constrained or sandboxed seats must publish app/runtime data, synced user data, downloads, cleanup scope, and reacquireability on one ordinary page.

**Why:** Current Resilio docs still split mobile storage truth across share details, downloads, shared links, and storage settings.

**Implications:**

- mobile-storage becomes a first-class page
- cleanup verbs must publish local/remote/history scope before apply
- sandbox/container facts become public state rather than hidden implementation detail
''',
    'docs/50-roadmap.md': '''

## Revision addendum — surface parity and mobile-saveback tranche after rev0175

This revision adds another small but important page-contract tranche:

- explicit surface-capability / external-edit-review / background-delivery / mobile-storage pages so cross-surface truth does not remain platform-article folklore
- operators can tell which verbs are truly available on the current surface and why missing verbs are missing
- operators can tell whether another app will receive a live bind or a detached copy, and what explicit save-back path is required
- operators can tell whether unattended delivery is continuous, conditional, foreground-only, or stopped and what catch-up risk follows resume
- operators can tell where mobile bytes really live, what each cleanup verb removes, and whether the bytes can be reacquired later
''',
    'docs/sources.md': '''

## Revision addendum — surface parity, external edit, background delivery, and mobile storage after rev0175

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about platform asymmetry, copy-based external editing, background delivery limits, and mobile storage semantics.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly honest about different surface capabilities across desktop, Linux/WebUI, Android, and iOS?

> where do those same current docs still show that the ordinary operator answer about `can I do this here?`, `am I editing a live object or a copy?`, `will this keep syncing in the background?`, and `what exactly does clear/remove free locally?` still depends on several platform articles instead of one stable product-owned page?

The most load-bearing source set for this pass was:

- Resilio's current Linux/WebUI notes, which still say Linux has no OS integration, no tray icon, no notifications outside Sync UI, and ordinary sharing/license entry flows through `Enter a key or link`.
- Resilio's current Android/iOS interface pages, which still expose materially different share-detail verbs, network controls, and local cleanup behavior.
- Resilio's current iOS peculiarity and edit guides, which still say external-app editing is copy-based and that deletions from iOS may simply un-sync locally.
- Resilio's current background, auto-sleep, battery-saver, simple-mode, and network-interface notes, which still spread unattended-freshness truth across several mobile/platform articles.
- Resilio's current iOS storage and sharing pages, which still split sandbox storage, downloads, shared-link residue, and local cleanup/history semantics across multiple surfaces.

## Additional Resilio official sources emphasized in rev0175

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Guide to Linux, and Sync peculiarities  
  https://help.resilio.com/hc/en-us/articles/204762449-Guide-to-Linux-and-Sync-peculiarities

- Does Sync work in background?  
  https://help.resilio.com/hc/en-us/articles/206816823-Does-Sync-work-in-background

- Sync interface on Android  
  https://help.resilio.com/hc/en-us/articles/213500383-Sync-interface-on-Android

- Sync Interface on iOS devices  
  https://help.resilio.com/hc/en-us/articles/212016726-Sync-Interface-on-iOS-devices

- Sync for iOS Peculiarities  
  https://help.resilio.com/hc/en-us/articles/205506539-Sync-for-iOS-Peculiarities

- How to edit a document stored in Sync? (iOS)  
  https://help.resilio.com/hc/en-us/articles/204762379-How-to-edit-a-document-stored-in-Sync-iOS

- Storage Management on iOS  
  https://help.resilio.com/hc/en-us/articles/115001726304-Storage-Management-on-iOS

- Sharing files (iOS)  
  https://help.resilio.com/hc/en-us/articles/115001717390-Sharing-files-iOS

- Configuring Auto Sleep & Battery Saver (Android)  
  https://help.resilio.com/hc/en-us/articles/204762699-Configuring-Auto-Sleep-Battery-Saver-Android

- Simple Mode (Android)  
  https://help.resilio.com/hc/en-us/articles/205458155-Simple-Mode-Android

- Selective Sync (Mobile)  
  https://help.resilio.com/hc/en-us/articles/206217315-Selective-Sync-Mobile

- Setting network interface per share  
  https://help.resilio.com/hc/en-us/articles/360001411244-Setting-network-interface-per-share

- Syncing between a desktop computer and a mobile device  
  https://help.resilio.com/hc/en-us/articles/205451165-Syncing-between-a-desktop-computer-and-a-mobile-device
'''
}
for rel, content in append_map.items():
    p = dst / rel
    existing = p.read_text()
    if content.strip() not in existing:
        p.write_text(existing.rstrip() + '\n' + content)

# Update sources header
sources = dst / 'docs/sources.md'
stxt = sources.read_text()
stxt = stxt.replace('# Source notes through rev0174', '# Source notes through rev0175', 1)
sources.write_text(stxt)

# New README
readme = f'''# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0175`
- Timestamp: `2026.03.20.19.52` (America/New_York)
- Codename: `surfaceparitysavebackpages`

## What changed in this revision

This revision continues directly from `rev0174` and does seven concrete things:

1. Re-checks another cluster of current official Resilio Sync docs so the archive's non-clone stance now also covers surface asymmetry across desktop, Linux/WebUI, Android, and iOS.
2. Adds one new **Resilio evaluation** document focused on surface capability truth, copy-versus-live external editing, unattended delivery limits, and mobile storage semantics.
3. Sharpens the main Resilio evaluation, scorecard, and clone-veto notes with an eleventh-wave answer: borrow the candor about platform differences, refuse the article-shaped page contracts.
4. Adds four new **interface page specs** for the strongest ordinary seams in this pass: surface capability, external edit review, background delivery, and mobile storage.
5. Extends the core interface/workbench language with concrete surface expectations for those four pages so local web, CLI, mobile, and narrow surfaces can all project the same truth.
6. Refreshes product direction, architecture decisions, roadmap notes, status language, and source notes so the new tranche is integrated into the main archive rather than floating beside it.
7. Makes the archive's answer to `why not just clone Resilio here too?` tighter because each no-clone choice now points at an ordinary replacement page instead of spreading surface truth across Linux peculiarities, Android settings, iOS edit/storage caveats, and background notes.

## Current conclusion

We **still should not clone Resilio Sync wholesale**.

This pass makes the reason more precise in another ordinary but load-bearing part of the product:

> the parts worth copying from Resilio are still mostly **honest surface facts** — Linux/WebUI asymmetry, Android conditional background delivery, iOS copy-based external editing, and mobile-storage candor — while the parts worth changing are the **page contracts** around action parity, save-back, unattended freshness, and local-byte cleanup.

That means AnonSync should become **more explicit than Resilio about what the current surface can really do, whether another app is touching the live object or a copy, whether unattended delivery is continuous or conditional, and what local cleanup actually removes**.

## Recommended reading order

1. `docs/00-status.md`
2. `docs/10-resilio-sync-evaluation.md`
3. `docs/11-resilio-borrow-line-and-non-clone-scorecard.md`
4. `docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md`
5. `docs/22-resilio-surface-parity-external-edit-background-and-mobile-storage-evaluation.md`
6. `docs/309-surface-capability-page-action-parity-and-reason-coded-gaps-interface-spec.md`
7. `docs/310-external-edit-review-page-copy-bind-saveback-and-duplicate-risk-interface-spec.md`
8. `docs/311-background-delivery-page-suspend-gates-freshness-floor-and-catchup-risk-interface-spec.md`
9. `docs/312-mobile-storage-page-sandbox-clearance-downloads-and-reacquireability-interface-spec.md`
10. `docs/38-operator-workbench-interface-spec.md`
11. `docs/30-interface-spec.md`
12. `docs/20-product-direction.md`
13. `docs/40-architecture-decisions.md`
14. `docs/50-roadmap.md`
15. `docs/sources.md`

## Archive map for this revision

- `docs/22-resilio-surface-parity-external-edit-background-and-mobile-storage-evaluation.md` — eleventh-wave Resilio evaluation focused on action parity, copy-based editing, unattended freshness, and mobile storage semantics
- `docs/309-surface-capability-page-action-parity-and-reason-coded-gaps-interface-spec.md` — fixed page contract for per-surface verb availability, gaps, and honest fallback routes
- `docs/310-external-edit-review-page-copy-bind-saveback-and-duplicate-risk-interface-spec.md` — fixed page contract for copy-versus-live external editing and explicit save-back semantics
- `docs/311-background-delivery-page-suspend-gates-freshness-floor-and-catchup-risk-interface-spec.md` — fixed page contract for unattended delivery, suspend reasons, and resume/catch-up risk
- `docs/312-mobile-storage-page-sandbox-clearance-downloads-and-reacquireability-interface-spec.md` — fixed page contract for local mobile-byte accounting, cleanup scope, and reacquireability

All previously-added documents remain in place; this revision adds the next page tranche and refreshes the cross-cutting doctrine around it.
'''
(dst / 'README.md').write_text(readme)

status = '''# Status

## Scope of this revision

This revision is an in-place continuation of `rev0174`, driven by the current request and the now-current archive state:

- continue researching rather than merely polishing
- test the `do not clone Resilio wholesale` conclusion against current official docs again
- keep making every non-clone choice earn itself with a specific borrow/adapt/reject reason
- keep writing ordinary page contracts where the archive still has interface-shape gaps rather than only object-model doctrine
- stay narrow: prefer high-leverage operator pages over broad product sprawl
- in this pass specifically, force a cleaner answer for cross-surface capability truth, external edit/save-back semantics, unattended background freshness, and mobile local-storage semantics

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

The archive now contains:

- Revision: rev0175
- Timestamp: 2026.03.20.19.52 America/New_York
- Codename: surfaceparitysavebackpages

- one new eleventh-wave Resilio evaluation document:
  - `22-resilio-surface-parity-external-edit-background-and-mobile-storage-evaluation.md`
- four new interface page specs:
  - `309-surface-capability-page-action-parity-and-reason-coded-gaps-interface-spec.md`
  - `310-external-edit-review-page-copy-bind-saveback-and-duplicate-risk-interface-spec.md`
  - `311-background-delivery-page-suspend-gates-freshness-floor-and-catchup-risk-interface-spec.md`
  - `312-mobile-storage-page-sandbox-clearance-downloads-and-reacquireability-interface-spec.md`
- refreshed Resilio evaluation and clone-veto notes that now extend the non-clone line into surface capability, save-back truth, unattended freshness, and local-mobile-byte cleanup
- refreshed top-level docs, workbench notes, architecture decisions, roadmap notes, and source notes so the new page tranche is integrated into the archive rather than bolted on

## The new tighter answer in this revision

This pass intentionally leans on another ordinary question that still survives in current Resilio docs:

> when the same subject is opened, edited, cleared, or backgrounded from desktop, Linux/WebUI, Android, or iOS, where does the product itself own the answer, and where does the operator still have to remember platform folklore?

The answer in this revision is:

- **surface capability truth** is still too easy to infer from missing buttons and separate platform articles instead of one product-owned page
- **external edit/save-back semantics** are honest but still too hidden, especially where another app receives a copy rather than a live bind
- **background delivery** is real but still spread across platform, battery, network, and foreground/hidden-runtime notes instead of one ordinary freshness page
- **mobile storage cleanup truth** is useful but still split across share details, downloads, shared links, and storage settings

## Outcome

The archive's current posture stays the same, but the argument is stronger:

- borrow the cross-surface candor from Resilio
- refuse the exact interface contracts when one ordinary answer still requires cross-reading Linux/WebUI peculiarities, Android settings, iOS edit/storage caveats, and background notes
- replace each refusal with one sharper public page contract
'''
(dst / 'docs/00-status.md').write_text(status)

# write update script for traceability
update_script = dst / 'update_rev0175.py'
update_script.write_text(Path('/mnt/data/rev0174_work/update_rev0175.py').read_text())
