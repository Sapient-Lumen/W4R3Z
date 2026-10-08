from pathlib import Path

root = Path('/mnt/data/workrev459')
docs = root / 'docs'

new_docs = {
'1894-resilio-remedy-hardening-attestation-residual-copy-extirpation-reappearance-and-resurrection-resistance-fragmentation-evaluation.md': r'''# Resilio remedy hardening attestation residual-copy extirpation, reappearance, and resurrection-resistance fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials still deserve credit for admitting that corrective action does not equal forgetting.
That candor matters.

The strongest current ingredients are:

- current `Disconnecting and Removing Folders` docs still say disconnect stops keeping the folder in sync but the folder remains in the file system and can still be accessed through a file browser
- the same docs still say reconnect can later happen from the disconnected state and may propose a different default path, creating a new directory with an added index if a same-name folder already exists
- the same docs still say even after removal from linked devices the folder may still remain available on remote devices not linked to the personal identity
- current `User Management` docs still say revoking a peer suspends future updates while all files synchronized so far remain in the folder
- current `Using Archive for file versioning and restoring deleted files` docs still say older or deleted copies are moved to Archive on other peers, desktops keep them there for 30 days by default, and restoring is manual
- current `Folder Types and Management` docs still say pending folders can auto-connect after prior approval and disconnected folders remain visible for later action
- current `Sync Storage folder` docs still say configuration, auxiliary settings, and shares' database live in ordinary storage paths that vary by runtime context
- current `Running Sync in configuration mode` docs still say the same settings can be applied on a number of different machines and that if no storage path is entered a `.sync` storage folder is created near the launched binary
- current `How to uninstall Sync?` docs still say settings or storage folders may need explicit manual deletion after uninstall
- current `Cloning Sync` docs still say cloning is unsupported and can create strange non-transferring twins

Those are useful truths.
They still do not add up to one typed answer to:

> `after a ruling was revoked or superseded, was the old statement merely hidden, or were the remaining copies actually extirpated strongly enough that reappearance is blocked at the required floor?`

## Where the current contract still fragments

The problem is not that Resilio denies residue.
The problem is that current residue truth is still scattered across folder state, Archive, identity linkage, storage-world guidance, uninstall guidance, and unsupported-clone warnings instead of being owned as one case-scoped forgetting contract.

Today an operator can often infer only weaker truths such as:

- synchronization stopped for this device or peer
- local bytes still remain on disk
- a disconnected lane can later reconnect
- a same-name folder may be re-created on reconnect
- old versions may still exist in hidden Archive
- remote devices outside the linked identity may still retain the folder
- runtime settings and databases still live in storage paths that must be manually removed
- the same configuration may cause future machines to inherit the same risky default
- clone-born or rebuilt instances may preserve or reanimate stale authority in strange ways

Those are important clues.
They are not the same as an explicit answer to `which residual loci still contain the old ruling or its enabling state, which of those loci are merely retained versus scheduled to expire, which were actually erased with evidence, which can still reappear on reconnect or rebuild, and what is the strongest honest forgetting sentence we can say now?`

## Why that matters for AnonSync

AnonSync needs stronger closure language than `delivered`, `acknowledged`, or even `stale surface suppressed`.
It needs to support claims such as:

- the old ruling is hidden from current dashboards, but archived export packets still exist through the stated retention window
- reachable dependents acknowledged the correction, but one disconnected lane can still reconnect and re-materialize the stale state under a new default path
- internal copies were cryptographically or administratively erased for the required cohort, but external unverified copies remain residually possible
- uninstall or decommission was performed, but storage-root deletion evidence is still missing for one service-world host
- manual archive expiration has not yet passed, so `forgotten` language remains blocked even though downstream-safe language for current use is allowed
- the source is historical only for the governed live cohort, but not yet resurrection-resistant for fresh worlds or future reconnects
- the product can certify `hidden`, `disconnected`, `scheduled-to-expire`, `erased with receipt`, `reconnect-revivable`, `clone-risk-open`, and `resurrection-resistant at named floor` separately instead of flattening them into one optimistic all-clear badge

AnonSync therefore needs first-class objects for **residual locus inventory, erase obligation, retention horizon, reconnect reappearance risk, rebuild reappearance risk, clone ambiguity risk, forgetting floor, and resurrection-resistance class** rather than leaving operators to assemble that truth from disconnect menus, Archive defaults, storage paths, uninstall checklists, and unsupported-clone warnings.

## Non-clone conclusion

Borrow the candor.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `did the old ruling actually stop existing strongly enough that it cannot come back in any governed place that matters?` — only by making the operator combine several partially overlapping operational surfaces:

- disconnect and peer revocation that stop future updates but leave prior files present
- reconnect paths that can revive the same share into a different path
- Archive retention that keeps older copies for a time and supports only manual restore
- linked versus unlinked device boundaries that limit what one removal actually removes
- storage folders that preserve configuration, logs, identity details, and share databases in ordinary filesystem paths
- config mode that can stamp the same defaults onto more machines
- uninstall guidance that still depends on manual deletion of settings or storage paths
- unsupported cloning that explicitly warns of strange twin behavior

That is enough to justify a harder product stance:

> AnonSync is not cloning Resilio because suppression is not forgetting, disconnection is not extirpation, and current residue truth is still reconstructed from several operational articles instead of owned by one stable page family that says what still exists, where it still exists, when it expires, what was actually erased, and whether resurrection is still possible.
''',
'1895-remedy-hardening-attestation-copy-extirpation-contract-sheet-page-residual-loci-ttl-erase-receipts-and-resurrection-risk-interface-spec.md': r'''# Remedy-hardening-attestation copy-extirpation contract sheet page — residual loci, retention horizons, erase receipts, and resurrection risk

## Purpose

This page is the compact contract for a case whose corrective wave already reached and suppressed the required stale surfaces, but which still needs an explicit answer to whether the old ruling or its enabling state continues to exist anywhere that matters.
It exists so the product can distinguish `not currently shown` from `scheduled to expire`, `erased with proof`, and `resurrection-resistant at the required floor`.

## Core fields

- case identifier
- source revocation-delivery receipt identifier
- current governing receipt identifier
- current forgetting-governance class
- current resurrection-resistance class
- freeze-new-reliance flag
- total known residual loci count
- live residual loci count
- expiring residual loci count
- erase-obligation-open count
- erase-confirmed count
- unverifiable external-copy count
- reconnect-revivable lane count
- rebuild-revivable host count
- clone-ambiguity risk grade
- latest required retention horizon
- oldest unexpired residual timestamp
- latest erase receipt timestamp
- residual inventory owner class
- erase owner class
- retention owner class
- decommission owner class
- strongest blocked forgetting sentence
- strongest blocked resurrection-resistant sentence
- next evidence that upgrades forgetting confidence
- next evidence that forces immediate re-open or escalation

## Forgetting-governance classes

The page must model at least these distinct classes:

- residual inventory incomplete
- residual inventory complete, erase policy not yet assigned
- retention-only residue governs current floor
- erase required, execution pending
- erase attempted, receipt missing
- erased for reachable governed cohort
- erased plus retention-expired for named cohort
- external unverifiable residue preserved
- reconnect or rebuild resurrection risk open
- resurrection-resistant for named cohort only
- global forgetting sentence blocked

## Residual locus classes

The page must support at least these residual-locus classes:

- live local working copy
- disconnected local retained copy
- hidden Archive residue
- exported packet or bundle copy
- downstream mirrored artifact
- service storage database or identity state
- config template or rollout scaffold
- removable media or offline backup
- remote unlinked device copy
- unsupported clone or forked instance
- screenshot, report, or manual note derivative
- unknown external copy class

## Residual status classes

For each locus the page must preserve at least these states:

- currently live and user-visible
- hidden but intact
- disconnected but revivable
- retained until explicit TTL expiry
- erase required now
- erase requested, not confirmed
- erase confirmed with durable receipt
- unverifiable outside governance
- future host inheritance risk
- resurrected after previous suppression

## Fixed rendering order

Every copy-extirpation contract sheet must render the same sections in the same order:

1. **Strongest speakable forgetting sentence**
2. **Residual inventory summary**
3. **Retention horizons and expiry gates**
4. **Erase obligations and receipt status**
5. **Reappearance and resurrection risks**
6. **Blocked stronger sentences**

## Hard rules

The page must never silently upgrade:

- `hidden` into `erased`
- `disconnected` into `gone`
- `retention expired for one locus` into `forgotten everywhere`
- `remove from linked devices` into `remote extirpation`
- `uninstall performed` into `storage state erased`
- `no current dashboard exposure` into `resurrection-resistant`

## Minimum operator questions answered

The page must let a later operator answer, without hunting across other pages:

- what copies or enabling state still exist right now
- which copies are only waiting out a retention horizon
- which loci require explicit erase or decommission work
- which loci may reappear on reconnect, rebuild, or clone confusion
- what the strongest honest forgetting sentence is today
- exactly which stronger sentence remains blocked and why
''',
'1896-remedy-hardening-attestation-copy-extirpation-review-page-has-the-old-ruling-actually-been-forgotten-or-can-it-reappear-interface-spec.md': r'''# Remedy-hardening-attestation copy-extirpation review page — has the old ruling actually been forgotten or can it reappear?

## Review question

Can the product honestly present this old ruling as merely hidden, retained until a known expiry, erased for a named cohort, or resurrection-resistant at the required floor — or would reconnect, rebuild, unlinked remotes, Archive residue, or clone-born state still let the old ruling come back?

## Review panels

### 1) Residual inventory review

Force the operator to enumerate every known place the old ruling or its enabling state might still exist.
The review must preserve at least these distinctions:

- direct content copy
- derivative content copy
- hidden retained copy
- control-plane or database state that can reanimate the old claim
- future rollout template that can stamp the same stale state elsewhere
- suspected but unverified external copy

False upgrades to reject include:

- treating one cleaned local folder as proof that the same share is gone elsewhere
- treating suppressed presentation as proof that the source bytes or authority state are gone

### 2) Retention-horizon review

Ask whether a locus is supposed to persist for a defined period before natural expiry.
The review must separate:

- active retention window still open
- expiry time known but not yet reached
- expiry time reached but deletion unverified
- no retention allowed, immediate erase required
- permanent historical preservation intentionally allowed

The page must reject `forgotten` when the only current story is `still retained until TTL`.

### 3) Erase-evidence review

Ask what evidence proves that a required erase or decommission actually happened.
The review must classify evidence at least as:

- erase obligation created only
- erase attempted
- local actor attested
- host or service deletion observed
- cryptographic or signed erase receipt captured
- independent corroboration of erase

The page must reject `erased` when evidence only proves that a removal action was requested.

### 4) Reappearance review

Force explicit review of every path by which old state might come back:

- disconnected folder reconnect
- prior approval auto-connect
- default path recreation with indexed sibling
- storage-world migration or rebuild
- startup config or templated install
- unsupported clone or forked runtime
- manual Archive restore
- external mirror or backup restore

The page must reject `resurrection-resistant` when any required lane remains plausibly reactivatable.

### 5) Governance-boundary review

Ask which loci are truly governed versus merely hoped-for.
The review must separate:

- governed internal hosts
- governed internal people
- linked devices under one identity
- unlinked remotes outside direct authority
- external recipients with callback but no erase authority
- wholly unverifiable external surfaces

The page must reject `forgotten everywhere` when any required audience sits outside real governance.

## Review outputs

The review must be able to emit at least these decisions:

- inventory incomplete, forgetting sentence blocked
- hidden and disconnected only; forgetting blocked
- retained until named expiry; current use safe, forgetting blocked
- erase obligations open for required cohort
- erased for reachable governed cohort only
- resurrection risk open through reconnect or rebuild
- resurrection-resistant for named cohort only
- global forgetting sentence blocked by unverifiable external residue

## Required warnings

The page must render plain warnings when:

- the only evidence is a UI disappearance
- Archive or hidden storage paths were not inspected
- uninstall occurred without storage-root deletion evidence
- reconnect-capable lanes still exist
- configuration artifacts can still stamp the stale state onto new hosts
- clone ambiguity means two worlds may still diverge or later reappear
''',
'1897-remedy-hardening-attestation-copy-extirpation-proof-page-residual-loci-erase-evidence-and-resurrection-floor-interface-spec.md': r'''# Remedy-hardening-attestation copy-extirpation proof page — residual loci, erase evidence, and resurrection floor

## Purpose

This page is the durable proof that forgetting and extirpation were evaluated under explicit residual-inventory, retention, erase, reappearance, and governance-boundary rules.
It must let a later verifier see not only that the stale claim disappeared from current surfaces, but whether it still existed anywhere important and whether reappearance remained possible.

## Sections

### 1) Forgetting header

Publish:

- case identifier
- source revocation-delivery receipt identifier
- current governing receipt identifier
- current forgetting-governance class
- current resurrection-resistance class
- required forgetting floor

### 2) Residual inventory table

For each locus or locus cohort print:

- locus identifier or cohort label
- locus class
- host, audience, or world scope
- prior stale sentence or enabling state
- current residual status
- current visibility status
- governance boundary class
- required action class

### 3) Retention and expiry table

The proof must print explicit results for each retained locus:

- retention basis
- retention start time
- scheduled expiry time
- whether expiry is automatic or requires active cleanup
- whether expiry was independently verified
- current block imposed on stronger forgetting language

### 4) Erase and decommission evidence table

For each locus requiring action print:

- erase or decommission owner
- requested action
- evidence type
- last execution time
- receipt identifier, if any
- corroboration grade
- current completion status
- reopen trigger if evidence is later contradicted

### 5) Reappearance-path analysis

The proof must score every relevant reappearance path:

- reconnect path
- auto-connect after prior approval
- path recreation on reconnect
- service rebuild or migration path
- startup-config inheritance path
- archive restore path
- backup restore path
- clone or fork ambiguity path

For each path print:

- path class
- currently open or closed
- evidence supporting that assessment
- dependent audience still exposed
- action that would close the path

### 6) Strongest speakable sentence block

The page must compute and print:

- strongest honest current forgetting sentence
- strongest blocked stronger forgetting sentence
- strongest honest resurrection-resistance sentence
- exact reasons those stronger sentences remain blocked

## Mandatory proof distinctions

The proof must preserve at least these distinctions:

- no longer shown versus no longer present
- retained until expiry versus erased now
- erase requested versus erase proven
- erased for governed cohort versus erased for all audiences
- no current reconnect observed versus reconnect impossible
- current-use safe versus resurrection-resistant

## Claim ceilings

The proof must never permit these sentences without direct support:

- `forgotten everywhere`
- `all copies deleted`
- `cannot come back`
- `remote devices no longer have it` when those devices were outside governance
- `fresh installs are safe` when templates or storage artifacts still carry reappearance risk
''',
'1898-remedy-hardening-attestation-copy-extirpation-timeline-page-disconnect-retain-archive-expire-erase-and-reappear-events-interface-spec.md': r'''# Remedy-hardening-attestation copy-extirpation timeline page — disconnect, retain, archive, expire, erase, and reappear events

## Purpose

This page is the chronological spine for forgetting and extirpation.
It exists to preserve the difference between suppressing a stale surface, retaining hidden copies through a TTL, executing erase work, expiring retained loci, and discovering later reappearance through reconnect, rebuild, or restore.

## Event classes

The timeline must support at least these event classes:

- residual locus discovered
- residual locus classified
- retention window attached
- erase obligation opened
- erase requested
- erase confirmed
- storage root deleted
- decommission completed
- archive expiry reached
- expiry verification captured
- reconnect path opened
- reconnect path closed
- config template retired
- clone ambiguity detected
- reappearance observed
- forgetting sentence upgraded
- forgetting sentence downgraded
- resurrection-risk escalation opened
- named-cohort forgetting approved
- global forgetting blocked

## Required timeline columns

Every event row must print at least:

- event timestamp
- actor or subsystem
- event class
- affected locus or path
- prior forgetting class
- resulting forgetting class
- evidence attached
- whether the event upgrades speakability, preserves history, or reopens risk

## Required chronology guarantees

The timeline must preserve:

- whether suppression preceded erase or vice versa
- whether retention expiry passed before the product upgraded forgetting language
- whether decommission happened before or after uninstall claims
- whether reconnect or rebuild risk reopened the case after a prior stronger sentence
- whether clone ambiguity was discovered before or after a supposed closeout
- whether reappearance came from live reconnect, Archive restore, backup restore, or fresh-world inheritance

## Required timeline summaries

The page must compute and print:

- first residual-locus discovery time
- first erase-obligation time
- first erase-confirmation time
- latest unexpired-retention time
- latest reappearance or reopen time
- first time the current strongest forgetting sentence became speakable

## Blocking rules

The timeline must never flatten:

- disconnection into deletion
- expiry schedule into expiry completion
- uninstall into storage decommission
- temporary invisibility into forgetting
- previously closed path into permanently impossible path
''',
'1899-remedy-hardening-attestation-copy-extirpation-lineage-receipt-page-residual-copy-status-resurrection-risk-and-blocked-forgetting-sentences-interface-spec.md': r'''# Remedy-hardening-attestation copy-extirpation lineage receipt page — residual-copy status, resurrection risk, and blocked forgetting sentences

## Purpose

This page is the durable receipt that captures what level of forgetting and extirpation was honestly achieved for a case at a specific time.
It must survive later review and show not merely that stale presentation was suppressed, but what residual copies or enabling state remained, what expiry or erase work governed them, what reappearance risk stayed open, and which stronger forgetting sentence the product refused to make.

## Receipt header

The receipt must print:

- receipt identifier
- case identifier
- source revocation-delivery receipt identifier
- current governing receipt identifier
- current forgetting-governance class
- current resurrection-resistance class
- required forgetting floor
- receipt issuance time

## Receipt body

The receipt must always include:

- strongest speakable forgetting sentence
- strongest blocked broader forgetting sentence
- strongest blocked resurrection-resistant sentence
- total known residual loci count
- active retained-locus count
- erase-confirmed count
- unexpired-retention count
- reconnect-revivable path count
- rebuild-revivable path count
- unverifiable external-copy count
- exact reason broader forgetting is blocked

## Mandatory distinctions preserved by the receipt

The receipt must preserve at least these distinctions:

- hidden versus erased
- retained until expiry versus expired and verified gone
- erased for named cohort versus erased everywhere
- no current live surface versus no residual copy
- no observed reappearance versus reappearance impossible
- named-cohort forgetting versus global forgetting

## Example speakable sentences

The receipt should support outputs such as:

- `stale presentation suppressed; residual inventory incomplete`
- `all governed live surfaces suppressed; hidden Archive residue remains through the stated horizon`
- `erased for the required internal cohort; one unlinked remote copy remains outside governance`
- `retention expired and erase receipts captured for the named cohort, but rebuild inheritance risk still blocks resurrection-resistant language`
- `resurrection-resistant for the required governed cohort only; global forgetting remains blocked by unverifiable external residue`

## Claim ceilings

The receipt must never let later operators silently say:

- `the old ruling no longer exists`
- `nothing can bring it back`
- `all remotes forgot it`
- `historical only everywhere` when retained or unverifiable residual loci remain
- `fresh worlds are clean` when config, storage, or clone paths can still reanimate the stale state

## Precedence rules

The receipt must make these rules explicit:

- later erase evidence can strengthen an older receipt, but only through a new receipt that explicitly owns the stronger forgetting sentence
- later reappearance automatically demotes prior forgetting language until the path is reclosed
- retention expiry without verification is weaker than verified disappearance when the floor requires evidence
- suppression receipts remain citable as history even when stronger forgetting language is still blocked
''',
}

for name, text in new_docs.items():
    (docs / name).write_text(text + '\n', encoding='utf-8')

readme = root / 'README.md'
old_readme = readme.read_text(encoding='utf-8')
new_addendum = r'''## Revision addendum after rev0458 — remedy hardening attestation residual-copy extirpation, forgetting, and resurrection-resistance truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **whether a corrective wave that was properly delivered, acknowledged where required, and strong enough to suppress stale surfaces also actually removed or outlasted the old ruling strongly enough that it cannot later reappear in governed places that matter**.
It does eight things in one tranche:

1. Continues the archive after rev0458 with a new page family centered on what happens *after* revocation delivery and stale-surface suppression exist but *before* the product should pretend the old ruling is truly forgotten or resurrection-resistant.
2. Tightens the non-clone line again: borrow Resilio's candor about disconnect that leaves bytes present, reconnect that can recreate a path, removal that does not reach unlinked remotes, Archive retention, storage roots that preserve settings and share databases, config rollout across multiple machines, uninstall steps that still require manual deletion of settings or storage folders, and unsupported cloning; refuse any contract where the operator still has to reconstruct `does the old ruling still exist somewhere, and can it come back?` from scattered operational surfaces.
3. Adds one new **Resilio evaluation** document focused on why current remedy-hardening-attestation-copy-extirpation truth is still too fragmented to clone even though the ingredients are useful.
4. Adds five new **interface specs** for remedy-hardening-attestation-copy-extirpation contract sheet, review, proof, timeline, and lineage receipt.
5. Makes one hard product decision explicit: **stale-surface suppression is weaker than residual-copy governance.**
6. Makes another hard product decision explicit: **retained-until-expiry residue is weaker than erased-with-receipt residue, and erased-for-named-cohort residue is weaker than governed-world forgetting.**
7. Makes a third hard product decision explicit: **governed-world forgetting is weaker than resurrection-resistant standing, and `not currently visible` is never allowed to impersonate `cannot reappear`.**
8. Packages the result as another continuation archive whose new tranche makes the `residual locus / retention horizon / erase receipt / reconnect or rebuild risk / forgetting floor / resurrection-resistance class / receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1894-resilio-remedy-hardening-attestation-residual-copy-extirpation-reappearance-and-resurrection-resistance-fragmentation-evaluation.md`
- `1895-remedy-hardening-attestation-copy-extirpation-contract-sheet-page-residual-loci-ttl-erase-receipts-and-resurrection-risk-interface-spec.md`
- `1896-remedy-hardening-attestation-copy-extirpation-review-page-has-the-old-ruling-actually-been-forgotten-or-can-it-reappear-interface-spec.md`
- `1897-remedy-hardening-attestation-copy-extirpation-proof-page-residual-loci-erase-evidence-and-resurrection-floor-interface-spec.md`
- `1898-remedy-hardening-attestation-copy-extirpation-timeline-page-disconnect-retain-archive-expire-erase-and-reappear-events-interface-spec.md`
- `1899-remedy-hardening-attestation-copy-extirpation-lineage-receipt-page-residual-copy-status-resurrection-risk-and-blocked-forgetting-sentences-interface-spec.md`


'''
readme.write_text(new_addendum + old_readme, encoding='utf-8')

sources = docs / 'sources.md'
old_sources = sources.read_text(encoding='utf-8')
new_sources = r'''## rev0459 source set — remedy hardening attestation residual-copy extirpation, forgetting, and resurrection resistance

The most load-bearing source set for this pass was:

- Resilio's current `Disconnecting and Removing Folders` article, which still says disconnect leaves the folder in the file system, reconnect remains available, reconnect may propose a different default path and create a new directory, and removal from linked devices may still leave the folder on remote devices outside the linked identity.
- Resilio's current `User Management` article, which still says disconnect suspends future updates while the files synchronized so far remain in the folder.
- Resilio's current `Using Archive for file versioning and restoring deleted files` article, which still says older or deleted copies move to Archive on other peers, desktops keep them there for 30 days by default, and restoring is manual.
- Resilio's current `Folder Types and Management` article, which still says pending folders can auto-connect after prior approval and disconnected folders remain visible for later action.
- Resilio's current `Sync Storage folder` article, which still says configuration, auxiliary settings, and shares' database live in ordinary storage paths that vary by runtime context.
- Resilio's current `Running Sync in configuration mode` article, which still says the same settings can be applied on a number of different machines and that if no storage path is entered a `.sync` storage folder is created near the launched binary.
- Resilio's current `How to uninstall Sync?` article, which still says settings or storage folders may need explicit manual deletion after uninstall.
- Resilio's current `Cloning Sync` article, which still says cloning is unsupported and can create strange non-transferring twins.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for candid forgetting ingredients
- but current Resilio still answers `is the old ruling merely hidden, or actually gone strongly enough that it cannot later come back?` too diffusely
- AnonSync should therefore prefer explicit remedy-hardening-attestation-copy-extirpation sheets, copy-extirpation reviews, copy-extirpation proofs, copy-extirpation timelines, and durable copy-extirpation lineage receipts over overloaded disconnect, Archive, storage, config, uninstall, and clone language

Primary sources:

- Disconnecting and Removing Folders
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- User Management
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- Using Archive for file versioning and restoring deleted files
  https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files

- Folder Types and Management
  https://help.resilio.com/hc/en-us/articles/204762459-Folder-Types-and-Management

- Sync Storage folder
  https://help.resilio.com/hc/en-us/articles/206664690-Sync-Storage-folder

- Running Sync in configuration mode
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- How to uninstall Sync?
  https://help.resilio.com/hc/en-us/articles/204775029-How-to-uninstall-Sync

- Cloning Sync
  https://help.resilio.com/hc/en-us/articles/360018421940-Cloning-Sync


'''
sources.write_text(new_sources + old_sources, encoding='utf-8')
