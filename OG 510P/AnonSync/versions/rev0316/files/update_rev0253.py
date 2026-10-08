from pathlib import Path
import re
from textwrap import dedent

root = Path(__file__).resolve().parent
docs = root / 'docs'

rev = 'rev0253'
ts = '2026.03.21.21.13'
codename = 'identityfatesurvivalcliff'
prev = 'rev0252'

readme_header = dedent(f'''
# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `{rev}`
- Timestamp: `{ts}` (America/New_York)
- Codename: `{codename}`

## What changed in this revision

This revision continues directly from `{prev}` and does seven concrete things:

1. Re-checks another current official Resilio Sync cluster around **identity-linking certificate takeover, identity renaming by unlink/recreate, uninstall guidance, subject-class fallout, and platform-specific byte deletion on iOS / Windows Phone**.
2. Sharpens the non-clone line again: borrow Resilio's candor that identity actions have real local consequences, while refusing any contract where an account-looking verb such as `unlink`, `rename identity`, `link running installs`, or `uninstall` quietly changes subject governance and byte survival by class and platform.
3. Adds one new **Resilio evaluation** document focused on how current Resilio still spreads one ordinary operator answer about `what survives this identity action on this seat?` across linking guidance, identity FAQ, uninstall guidance, and mobile-platform caveats.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: identity-action review, subject-fate matrix, preserve-before-identity-action, and identity-action receipt.
5. Extends the interface/workbench doctrine so every serious identity-changing action now publishes **requested verb, affected subject classes, app-removal effect, local-byte survival by platform, preserve-first alternatives, and strongest safe sentence** before commit.
6. Refreshes status-bearing doctrine documents — status, evaluation, scorecard, clone-veto tests, product direction, roadmap, open questions, sources, and README — so the new tranche is integrated rather than bolted on.
7. Packages the result as another continuation archive whose new tranche makes the `identity verb / subject fate / mobile deletion asymmetry` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's account-looking identity-action contract**

This time the evidence is especially clear around **linking two already-running installs, renaming identity only by unlinking and creating a new certificate, uninstall guidance that clears Advanced then Standard in sequence, and platform-specific file deletion on iOS / Windows Phone**.

Current official docs still openly distinguish real facts such as:

- linking two already-running Sync installs still causing one device to lose its certificate, remove Advanced folders from the app, and copy folders from the other instance
- iOS still deleting those Advanced folders from the file system when that certificate takeover happens
- changing identity name still requiring unlink + new identity creation, still removing Advanced folders from the instance, and still preserving Standard folders differently
- that preservation sentence still having a mobile carve-out: folders remain in the system except on iOS and Windows Phone
- uninstall guidance still telling operators to unlink from identity first, then remove remaining Standard shares, while desktop uninstall generally leaves previously shared folders in the file system
- iOS and Windows Phone uninstall still removing synced files from the device because of platform architecture
- the live Sync v3 line still appearing through `3.1.2.1076`

That candor is good.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed into several help pages before the product fully owns these questions:

- is this verb only changing identity or also evicting some subject classes from app governance
- which local bytes survive, and which are deleted because of platform architecture
- whether `Advanced`, `Standard`, and already-landed local files are surviving differently on this seat
- whether the safe next move is `unlink`, `rename`, `relink`, `export first`, `branch first`, or `do not proceed here`
- what later receipt can prove about the exact fate of each local subject after the action

AnonSync should therefore make **identity-action review** and **subject-fate matrix** first-class product objects.
Every serious identity-changing action should render requested verb, affected subject classes, app-removal effect, local-byte survival by platform, preserve-first alternatives, and receipt language before the product treats identity work as mere account housekeeping.

## Legacy revision notes preserved below
''').strip() + '\n\n'

status_add = dedent('''
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
''').strip() + '\n\n'

eval_add = dedent('''
## Revision addendum — identity actions, subject-class fallout, and mobile byte-deletion asymmetry after rev0252

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about identity linking, renaming an identity, uninstall sequencing, subject-class fallout, and platform-specific file deletion.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that identity verbs are not merely account verbs, but can change local subject governance and byte survival differently by class and platform?

> where do those same current docs still show that the ordinary operator answer about `what survives this identity action on this seat?` still depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says linking two already-running installs can make one device lose its certificate, remove Advanced folders from the app, and copy folders from the other instance, while iOS deletes those Advanced folders from the file system because of platform architecture.
- Resilio's current `Can I change the name of my Sync identity?` article, which still says renaming means unlinking and creating a new identity, removes Advanced folders from the instance, preserves Standard folders differently, and keeps folders in the system except on iOS and Windows Phone.
- Resilio's current `How to uninstall Sync?` article, which still says operators should unlink from identity first, then remove remaining Standard shares, and that iOS and Windows Phone uninstall removes synced files from the device.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the active v3 line through `3.1.2.1076`.

That is useful candor.
The non-clone problem is workflow ownership.
Current Resilio still lets one ordinary answer about `is this just identity housekeeping, or am I also dropping subjects and maybe deleting local bytes on this platform?` leak across linking docs, an identity FAQ, and uninstall guidance.

The archive now owes four more first-class pages:

- **Identity-action review**
- **Subject-fate matrix**
- **Preserve-before-identity-action**
- **Identity-action receipt**

These pages are required whenever an identity-looking verb could otherwise be flattened into `unlink`, `rename`, `link`, or `uninstall` without publishing requested verb, subject-class fallout, platform-local byte fate, preserve-first alternatives, and strongest safe sentence.
''').strip() + '\n\n'

scorecard_add = dedent('''
## Revision addendum — scorecard after rev0252: borrow identity-fallout candor, reject account-housekeeping folklore

Another current Resilio pass improves the scorecard in one more narrow place.

### Borrow

Keep borrowing these traits:

- admitting that identity actions have real subject-level consequences rather than only label/account effects
- admitting that Advanced and Standard subjects do not always survive the same identity verbs in the same way
- admitting that platform architecture can materially change whether local bytes remain or are deleted
- admitting that uninstall, unlink, and relink are not interchangeable continuity stories

### Refuse to clone

Do not clone these traits:

- making an account-looking verb such as `unlink` or `rename identity` quietly evict local subjects from app governance
- leaving operators to discover only later that mobile platforms delete local bytes where desktop would only remove app control
- spreading `what survives here?` across linking guidance, FAQ prose, and uninstall instructions
- flattening `removed from app`, `still on disk`, and `deleted on this platform` into one vague `unlinked` or `removed` sentence

### Stronger replacement

AnonSync should publish four first-class surfaces instead:

- **Identity-action review**
- **Subject-fate matrix**
- **Preserve-before-identity-action**
- **Identity-action receipt**

The governing rule is simple:

> if an identity verb can change local subject governance or byte survival, the product must state publicly which subject classes are affected, what survives on this platform, and what preserve-first alternatives still exist before commit.
''').strip() + '\n\n'

clone_veto_add = dedent('''
## Revision addendum — clone-veto after rev0252: identity verbs cannot hide subject fallout or platform delete cliffs

The interface clone-veto now adds another family.

If the operator still has to merge linking docs, identity-rename FAQ text, and uninstall guidance to answer any of the following, the clone-veto still fails:

1. **Is this action only changing identity lineage, or also removing some local subject classes from app governance?**
2. **Which subjects survive differently here: Advanced, Standard, or already-landed local bytes?**
3. **Will bytes remain on disk, leave the app only, or be deleted on this platform because of architecture?**
4. **What preserve-first alternative is safer here: export, branch, postpone, or use another seat?**
5. **What later receipt will prove the fate of each local subject after apply?**

Required page family for passing this veto:

- **Identity-action review**
- **Subject-fate matrix**
- **Preserve-before-identity-action**
- **Identity-action receipt**
''').strip() + '\n\n'

product_add = dedent('''
## Revision addendum — product direction after rev0252: identity work must publish local subject fate, not just credential change

The product direction should now be explicit on one more point:

- `unlink from identity` is not the same answer as `nothing local changes`
- `rename identity` is not the same answer as `label-only change`
- `link this running install` is not the same answer as `harmless family join`
- `remove from app` is not the same answer as `bytes survive on this platform`
- `uninstall` is not the same answer as `local files remain`

So AnonSync should publish identity-changing work as a first-class subject-fate object.
Every serious unlink / relink / rename / uninstall surface should show requested verb, affected subject classes, app-removal effect, local-byte survival by platform, preserve-first alternatives, and strongest safe sentence before the product treats the action as routine housekeeping.
''').strip() + '\n\n'

roadmap_add = dedent('''
## Revision addendum — roadmap after rev0252: schedule an identity-action tranche before broader account/profile polish

The roadmap should now explicitly include one identity-action tranche before any broad identity/profile/account polish is treated as complete.

That tranche should deliver:

- one compiled server-side identity-action object
- one operator-facing identity-action review page
- one subject-fate matrix page
- one preserve-before-identity-action page
- one identity-action receipt
- one compact workbench lane for current subject fallout and local-byte survival by platform

This should land before any effort that merely beautifies identity/profile surfaces, because the semantic gap is still more important than the visual gap.
''').strip() + '\n\n'

openq_add = dedent('''
## 0e) How much preserve-first friction should identity-changing verbs require before ordinary rename/unlink work feels ceremonial?

The archive now requires a first-class identity-action review whenever an account-looking verb can also change local subject governance or byte survival.
What remains unresolved is the ergonomics budget:

- when a low-risk identity relabel on a seat with no governed subjects may bypass the fuller preserve-first review
- whether seats with only replayable or already-exported subjects may take a denser confirmation path
- how strong the block should be when the current seat is on a platform with a known local-byte delete cliff
- whether repeated safe identity maintenance on one seat should earn narrower review without hiding subject fate again

This matters because too little friction recreates exactly the `unlink is just housekeeping` folklore the archive is trying to avoid, while too much friction can make healthy identity hygiene feel ceremonial.
''').strip() + '\n\n'

sources_add = dedent('''
## Revision addendum — identity actions, subject-class fallout, and mobile byte deletion after rev0252

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about identity linking, renaming an identity, uninstall sequencing, and platform-specific local-byte fate.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that identity verbs can change local subject governance and byte survival differently by class and platform?

> where do those same current docs still show that the ordinary operator answer about `what survives this identity action on this seat?` still depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says linking two already-running installs can make one device lose its certificate, remove Advanced folders from the app, copy folders from the other instance, and on iOS delete those Advanced folders from the file system.
- Resilio's current `Can I change the name of my Sync identity?` article, which still says renaming requires unlinking and creating a new identity, removes Advanced folders from the instance, leaves Standard folders in the instance, and keeps folders in the system except on iOS and Windows Phone.
- Resilio's current `How to uninstall Sync?` article, which still says operators should unlink from identity first, then remove remaining Standard shares, and that uninstall on iOS and Windows Phone removes synced files from the device.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the active v3 line through `3.1.2.1076`.

## Additional Resilio official sources emphasized in rev0253

- Sync Private Identity & Linking My Devices
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Can I change the name of my Sync identity?
  https://help.resilio.com/hc/en-us/articles/206163443-Can-I-change-the-name-of-my-Sync-identity

- How to uninstall Sync?
  https://help.resilio.com/hc/en-us/articles/204775029-How-to-uninstall-Sync

- Resilio Sync 3.0 change log
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log
''').strip() + '\n\n'

# New docs
new_docs = {
    '691-resilio-identity-action-subject-fate-and-mobile-delete-asymmetry-evaluation.md': dedent('''
        # Resilio identity-action, subject-fate, and mobile-delete asymmetry evaluation
        
        ## Why this pass exists
        
        The archive already had strong doctrine for seat lineage, identity replacement, severance ladders, and mobile storage.
        What it still lacked was one direct evaluation for a sharper seam:
        
        > when a product says `unlink`, `rename identity`, `link this running install`, or `uninstall`, is it describing credential housekeeping, or hiding a subject-class and platform-specific local-fate contract?
        
        Current official Resilio docs make that seam much sharper than a generic `identity changes have side effects` story.
        Across current linking, identity-rename, and uninstall docs they still say all of the following:
        
        - Linking two devices that are already running Sync can cause one device to lose its certificate and take over the certificate of the other.
        - When that happens, Advanced folders on the acquiring device are removed from the app and new folders from the other instance are copied.
        - On iOS, those Advanced folders are not only removed from the app; they are also deleted from the file system because of platform architecture.
        - Renaming identity is not a label edit; the current FAQ still says it requires unlinking the current identity and creating a new one so a new certificate is generated.
        - That same rename FAQ still says Advanced folders are removed from the instance, Standard folders remain in the instance, and folders remain in the system except on iOS and Windows Phone devices.
        - Current uninstall guidance still says operators should unlink from identity first and then remove the remaining Standard shares.
        - That same uninstall guidance still says uninstall on iOS and Windows Phone removes synced files from the device because of platform architecture, while desktop uninstall generally does not delete previously shared folders from the file system.
        - Current official Sync v3 docs still show the live line through `3.1.2.1076`.
        
        That is strong candor.
        It is also a very good reason not to clone the verb contract.
        
        ## What Resilio gets right
        
        ### 1) It admits that identity verbs are not purely abstract
        
        Current docs do not pretend that identity work is only cosmetic.
        They still admit that linking, unlinking, renaming, and uninstalling can affect real local subjects.
        That is worth borrowing.
        
        ### 2) It admits that subject classes do not all survive the same way
        
        The current rename and uninstall docs are especially useful because they do not flatten Advanced and Standard folders into one fate sentence.
        They still distinguish different local outcomes.
        That is the right instinct.
        
        ### 3) It admits that platform architecture changes byte survival
        
        Current iOS and Windows Phone caveats still say local byte survival is not universal.
        That honesty is important.
        A weaker product would hide the mobile delete cliff until after the action.
        
        ### 4) It admits that uninstall and unlink are not the same housekeeping story
        
        Current uninstall guidance still prescribes an identity action first and a share-removal action second.
        That sequencing implicitly admits that different verbs cut different parts of continuity.
        
        ## Why this is still a strong reason not to clone them
        
        The ordinary operator answer is still too fragmented.
        Current official docs still force too much reconstruction before the product fully owns these questions:
        
        - is this verb only changing identity lineage, or also evicting local subjects from app governance?
        - which local subject classes survive differently here?
        - are bytes staying on disk, disappearing from the app only, or being deleted because of platform architecture?
        - is the safer next move to preserve first, branch first, use another seat, or proceed now?
        - what later receipt proves the actual local fate after the action?
        
        That should not require stitching together linking docs, an identity FAQ, and uninstall guidance.
        
        ## The tighter AnonSync conclusion
        
        AnonSync should borrow the following from current Resilio more boldly:
        
        - explicit candor that identity verbs can have real local consequences
        - explicit candor that subject classes do not all survive the same action the same way
        - explicit candor that platform architecture changes the honest byte-survival sentence
        - explicit candor that some identity actions should be sequenced with preserve/remove work rather than treated as one abstract account operation
        
        But AnonSync should refuse the exact verb contract whenever one ordinary answer still depends on several articles.
        The product should not let `unlink`, `rename`, `link`, or `uninstall` stand without one owned surface that states:
        
        - requested identity verb
        - affected subject classes
        - app-removal effect
        - local-byte survival by platform
        - preserve-first alternatives
        - strongest safe sentence and stronger forbidden sentence
        
        ## Replacement pages added for this seam
        
        This pass therefore adds four more page-shaped obligations:
        
        1. **Identity-action review** — what verb is being attempted, what subject classes it changes, and what local-byte fate follows here.
        2. **Subject-fate matrix** — what survives in app governance, what stays on disk, and what is deleted on this platform.
        3. **Preserve-before-identity-action** — what safer export / branch / alternate-seat sequence is available before a destructive identity verb.
        4. **Identity-action receipt** — what later proves the requested verb, actual subject fallout, platform basis, and follow-up obligations.
        
        ## Bottom line
        
        The tighter no-clone reason is now this:
        
        > Resilio is current evidence that identity verbs have real operator consequences and should be described honestly; it is also current evidence that one account-looking action can still hide subject-class fallout and platform delete cliffs. AnonSync should copy the candor and refuse the overloaded housekeeping contract.
    ''').strip() + '\n',
    '692-identity-action-review-page-unlink-relink-rename-uninstall-and-subject-fate-interface-spec.md': dedent('''
        # Identity-action review page: unlink, relink, rename, uninstall, and subject fate interface spec
        
        ## Purpose
        
        This page exists because identity-looking verbs are not always pure account verbs.
        A seat can be asked to:
        
        - unlink from a family
        - create a fresh identity
        - accept certificate takeover from another running seat
        - uninstall after clearing local control
        
        and those actions can change local subject governance or byte survival differently by class and platform.
        
        The page must let an operator answer one blunt question without article archaeology:
        
        > if I continue this identity action here, what local subjects leave governance, what bytes survive on this platform, and what safer preserve-first branch still exists?
        
        ## Core decision
        
        AnonSync should make **identity-action review** first-class.
        Every identity-changing action must publish, in one stable object:
        
        - requested verb
        - target identity outcome
        - affected subject classes
        - app-removal effect
        - local-byte survival by platform
        - preserve-first alternatives
        - strongest safe sentence
        
        ## Fixed review order
        
        Every identity-action review page should render the same sections in the same order:
        
        1. **Verb now**
        2. **Subject fallout**
        3. **Platform-local byte fate**
        4. **Continuity preserved / lost**
        5. **Preserve-first alternatives**
        6. **Claim ceiling**
        
        ### 1) Verb now
        
        Show:
        
        - requested verb: `unlink`, `fresh-identity`, `certificate-takeover`, `uninstall`, `unknown`
        - initiating surface
        - target seat/identity outcome
        - whether the action is reversible, successor-only, or destructive
        
        The operator must be able to answer: **what identity verb is actually being committed?**
        
        ### 2) Subject fallout
        
        Show:
        
        - affected subject classes present on this seat
        - for each class: `unchanged`, `removed-from-governance`, `will-be-copied-in`, `will-require-manual-reclaim`, `unknown`
        - whether the effect is app-only or wider
        
        The operator must be able to answer: **which local subjects are changing governance state because of this verb?**
        
        ### 3) Platform-local byte fate
        
        Show:
        
        - current platform class
        - local-byte fate: `stay-on-disk`, `app-only-removal`, `platform-delete-cliff`, `unknown`
        - strongest platform reason
        - whether another seat would be safer for this action
        
        The operator must be able to answer: **what will happen to the local bytes on this platform?**
        
        ### 4) Continuity preserved / lost
        
        Show separately:
        
        - preserved continuity: local bytes, subject labels, history witnesses, linked relations, approvals, receipts
        - lost continuity: identity lineage, active governance, remembered approvals, on-seat control state
        
        The operator must be able to answer: **what continuity survives, and what definitely does not?**
        
        ### 5) Preserve-first alternatives
        
        Offer safer branches, for example:
        
        - `Preserve local bytes first`
        - `Create a branch/export before unlink`
        - `Move this action to a safer seat`
        - `Keep identity unchanged`
        - `Abort`
        
        The operator must be able to answer: **what safer sequence is still available before I cross the line?**
        
        ### 6) Claim ceiling
        
        Show:
        
        - strongest safe sentence
        - stronger forbidden sentence
        - evidence timestamp
        - main uncertainty if present
        
        Examples:
        
        - `This action changes seat identity and removes Advanced subjects from active governance on this seat, but local bytes remain on disk here.`
        - `This action is unsafe on this platform because governed bytes would be deleted locally.`
        - `This seat can complete the identity action only after you preserve the listed subjects elsewhere.`
        
        ## Main card
        
        The subject/seat workspace should expose an **Identity action** card with:
        
        - verb chip
        - subject-fallout chip
        - byte-fate chip
        - preserve-first chip
        - `Inspect identity action`
        
        ## Rules
        
        ### Rule 1 — identity verbs and subject fallout must stay adjacent
        
        The page may not let `unlink` or `rename` stand alone if local subject governance changes with it.
        
        ### Rule 2 — platform-local byte fate must be explicit
        
        The page may not reduce a platform delete cliff to generic removal language.
        
        ### Rule 3 — preserve-first alternatives must be real
        
        If a safer export/branch/alternate-seat path exists, the page must show it before destructive commit.
        
        ### Rule 4 — one verb may not hide several survival stories
        
        If a later operator could not tell `removed from app`, `still on disk`, and `deleted on this platform` apart from this page alone, the page is not explicit enough.
        
        ## Acceptance criteria
        
        A later operator can:
        
        - identify the exact identity verb being committed
        - see which local subject classes are affected
        - know whether bytes survive on this platform
        - choose a preserve-first branch when safer
        - quote one honest post-commit sentence without folklore
    ''').strip() + '\n',
    '693-subject-fate-matrix-page-action-class-app-removal-and-local-byte-survival-interface-spec.md': dedent('''
        # Subject-fate matrix page: action class, app removal, and local-byte survival interface spec
        
        ## Purpose
        
        Identity actions often affect more than one local subject class at once.
        The operator needs one matrix that answers:
        
        > for each governed subject class on this seat, what happens in the app, what happens on disk, and what platform rule explains the difference?
        
        ## Core decision
        
        AnonSync should publish **subject-fate matrix** as the proof-adjacent companion to identity-action review.
        The matrix is not a generic checklist.
        It is the typed local survival map for the current action.
        
        ## Columns
        
        Every row should show:
        
        1. subject class
        2. current local presence
        3. post-action governance state
        4. post-action byte state
        5. platform basis
        6. recovery path
        
        ## Required rows
        
        The page must include any class currently present on the seat, such as:
        
        - advanced-governed subject
        - standard-governed subject
        - landed local bytes without future governance
        - imported / copied payload branch
        - unknown / mixed class requiring manual inspection
        
        ## Value vocabulary
        
        ### Current local presence
        
        Use:
        
        - `present-and-governed`
        - `present-branch-only`
        - `listed-not-materialized`
        - `not-present`
        - `unknown`
        
        ### Post-action governance state
        
        Use:
        
        - `unchanged`
        - `removed-from-app`
        - `replaced-by-successor`
        - `manual-reclaim-required`
        - `copied-in`
        - `unknown`
        
        ### Post-action byte state
        
        Use:
        
        - `bytes-stay-local`
        - `bytes-deleted-local`
        - `bytes-unchanged-but-ungoverned`
        - `bytes-replaced`
        - `unknown`
        
        ### Platform basis
        
        Use short typed reasons:
        
        - `desktop-nondestructive`
        - `mobile-delete-cliff`
        - `subject-class-specific`
        - `receipt-only-evidence`
        - `unknown`
        
        ### Recovery path
        
        Use:
        
        - `none-needed`
        - `relink-later`
        - `manual-reimport`
        - `recover-from-other-seat`
        - `preserve-before-action`
        - `unknown`
        
        ## Main view
        
        The matrix should default to one dense table plus one plain-language summary sentence.
        
        Example summary sentence:
        
        `On this seat, Advanced subjects leave governance under the requested identity action; desktop bytes remain local, but this platform class would delete governed bytes if the same action ran on mobile.`
        
        ## Rules
        
        ### Rule 1 — app removal and byte removal must never share one unlabeled cell
        
        Governance loss and byte deletion are different fates and must always have different columns.
        
        ### Rule 2 — platform basis must be public
        
        If the local-byte fate changes because of platform architecture, the matrix must say so directly.
        
        ### Rule 3 — recovery path must be typed, not implied
        
        The matrix must never assume that `still on disk` means `easy to recover` without naming the actual recovery path.
        
        ### Rule 4 — mixed class must stay inspectable
        
        If the product cannot classify a row cleanly, it must show `unknown / mixed class requiring manual inspection` rather than bluffing.
        
        ## Acceptance criteria
        
        A later operator can:
        
        - see class-by-class fallout for the pending identity action
        - distinguish governance loss from byte deletion
        - understand whether platform architecture changes the result
        - know the next recovery rung for each affected row
    ''').strip() + '\n',
    '694-preserve-before-identity-action-page-export-branch-relink-and-safe-sequence-interface-spec.md': dedent('''
        # Preserve-before-identity-action page: export, branch, relink, and safe sequence interface spec
        
        ## Purpose
        
        Some identity actions should not be blocked outright, but they also should not be the first step.
        This page exists to answer:
        
        > if the requested identity action would drop governance or risk local byte loss here, what preserve-first sequence is safer and still sufficient?
        
        ## Core decision
        
        AnonSync should make **preserve-before-identity-action** first-class.
        The product must not force operators to improvise preservation around unlink / relink / rename / uninstall work.
        
        ## Required sequence choices
        
        The page should compare at least these candidate branches when relevant:
        
        - `Proceed now`
        - `Preserve locally, then proceed`
        - `Export / branch, then proceed`
        - `Move action to another seat`
        - `Abort`
        
        ## Fixed review order
        
        1. **Why preserve first**
        2. **Candidate safe sequences**
        3. **Resulting local state after sequence**
        4. **Cost / residue forecast**
        5. **Final recommended rung**
        
        ### 1) Why preserve first
        
        Show the exact trigger:
        
        - governance-loss trigger
        - platform delete-cliff trigger
        - uncertain subject-class trigger
        - missing recovery witness trigger
        
        ### 2) Candidate safe sequences
        
        For each sequence show:
        
        - ordered steps
        - required seat/platform
        - what is preserved before the identity action
        - what still remains at risk
        
        ### 3) Resulting local state after sequence
        
        Show:
        
        - local bytes after sequence
        - governance state after sequence
        - whether receipts/history remain inspectable
        - whether later relink/import is expected
        
        ### 4) Cost / residue forecast
        
        Show:
        
        - extra storage cost
        - extra branch/residue created
        - extra review work introduced
        - whether cleanup will later be required
        
        ### 5) Final recommended rung
        
        End with one explicit rung:
        
        - `safe to proceed now`
        - `preserve first on this seat`
        - `use another seat`
        - `block until classification improves`
        
        ## Rules
        
        ### Rule 1 — preserve-first is not an afterthought
        
        If the product already knows a destructive identity action has a safer prerequisite sequence, it must surface that sequence before the commit gate.
        
        ### Rule 2 — another seat is a valid alternative
        
        The page must be able to say that the right answer is to perform the identity action elsewhere.
        
        ### Rule 3 — residue must be forecast honestly
        
        Branching/exporting may create later cleanup work; the page must say so instead of pretending preservation is free.
        
        ## Acceptance criteria
        
        A later operator can:
        
        - understand why preserve-first review appeared
        - compare safer sequences instead of improvising
        - see the expected local state after each sequence
        - pick the narrowest sufficient safe rung
    ''').strip() + '\n',
    '695-identity-action-receipt-page-requested-verb-subject-fate-platform-basis-and-followup-proof-interface-spec.md': dedent('''
        # Identity-action receipt page: requested verb, subject fate, platform basis, and follow-up proof interface spec
        
        ## Purpose
        
        Identity work needs a durable receipt because later operators otherwise inherit folklore.
        The receipt must answer:
        
        > what identity verb was requested here, what actually happened to each local subject class, what platform rule shaped the byte result, and what follow-up work is still owed?
        
        ## Core decision
        
        AnonSync should publish a first-class **identity-action receipt** after every identity-changing action that had non-trivial subject fallout.
        
        ## Required receipt fields
        
        - `identity_action_receipt_id`
        - `requested_verb`
        - `effective_action_verdict`
        - `seat_ref`
        - `platform_class`
        - `subject_fate_rows[]`
        - `local_byte_survival_summary`
        - `platform_basis_summary`
        - `preserve_first_sequence_used`
        - `followup_required[]`
        - `strongest_safe_sentence`
        - `stronger_forbidden_sentence`
        - `evidence_timestamp`
        
        ## Receipt layout
        
        ### Header
        
        Show:
        
        - requested verb
        - effective verdict
        - seat
        - platform class
        - timestamp
        
        ### Subject-fate summary
        
        Show one compact matrix or list with:
        
        - subject class
        - governance result
        - byte result
        - recovery path
        
        ### Platform basis block
        
        Explain why the local-byte result was what it was on this platform.
        This block must be plain language, not only a raw enum.
        
        ### Follow-up block
        
        List remaining work, for example:
        
        - relink required
        - manual reimport required
        - cleanup residue later
        - recovery must be performed on another seat
        - no follow-up owed
        
        ## Compact row contract
        
        A trustworthy compact row should preserve the following order:
        
        1. requested verb
        2. effective action verdict
        3. strongest subject-fate summary
        4. byte-survival summary
        5. strongest next action
        
        Example:
        
        ```text
        Rename identity on Phone-A · fresh identity created · Advanced subjects left app governance · local synced bytes deleted on this platform by architecture rule · Recover on Desktop-B before relink
        ```
        
        ## Rules
        
        ### Rule 1 — requested verb and effective result must stay separate
        
        The receipt must preserve whether the operator asked for `rename`, `unlink`, `relink`, or `uninstall`, even if the effective local consequence was larger.
        
        ### Rule 2 — platform basis must be preserved, not inferred later
        
        If bytes were deleted or preserved because of platform architecture, the receipt must say so directly.
        
        ### Rule 3 — subject-fate rows must outlive the transient review UI
        
        Later operators should not have to reopen the original review to know what happened.
        
        ## Acceptance criteria
        
        A later operator can:
        
        - prove which identity verb was requested
        - prove what happened to each local subject class
        - prove why byte survival differed on this platform
        - know what follow-up work is still required
        - quote one safe post-action sentence without folklore
    ''').strip() + '\n'
}

# helper prepend

def prepend(path: Path, text: str):
    old = path.read_text()
    path.write_text(text + old)

# update README replacing header before legacy marker
readme = root / 'README.md'
old = readme.read_text()
marker = '## Legacy revision notes preserved below\n'
if marker in old:
    _, rest = old.split(marker, 1)
    readme.write_text(readme_header + marker + rest)
else:
    readme.write_text(readme_header + old)

# prepend addenda
prepend(docs / '00-status.md', status_add)
prepend(docs / '10-resilio-sync-evaluation.md', eval_add)
prepend(docs / '11-resilio-borrow-line-and-non-clone-scorecard.md', scorecard_add)
prepend(docs / '12-resilio-interface-clone-veto-tests-and-page-obligations.md', clone_veto_add)
prepend(docs / '20-product-direction.md', product_add)
prepend(docs / '50-roadmap.md', roadmap_add)
prepend(docs / '64-critical-open-questions.md', openq_add)
prepend(docs / 'sources.md', sources_add)

# create docs
for name, content in new_docs.items():
    (docs / name).write_text(content)

print('updated', rev)
