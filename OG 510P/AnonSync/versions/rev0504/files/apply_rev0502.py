from pathlib import Path

base = Path(__file__).resolve().parent

def prepend(path: Path, text: str) -> None:
    original = path.read_text()
    path.write_text(text + original)

README_ADD = """## Revision addendum after rev0501 — audience-wide closure proof and residual-survival ceiling

This continuation archive advances the doctrine by tightening the next concrete seam after containment:
**what happens after the product can honestly say a relapse channel was watched and even intercepted, but before it can honestly say the governed audience is actually closed, that residual stale carriers have been retired, or that any surviving residue is fully enumerated rather than merely hoped away**.
It does eight things in one tranche:

1. Continues the archive after rev0501 with a new page family centered on audience-wide closure proof rather than interception alone.
2. Tightens the non-clone line again: borrow Resilio's candor about disconnect affecting one device while leaving files in place, remove affecting linked devices only, remote unlinked devices still retaining data, single-file transfer recipients keeping files after UI removal, recipients being able to reshare further, folder links expiring only for future connects, and Resilio being unable to centrally remove peer copies.
3. Adds one new **Resilio evaluation** page focused on why current audience-wide closure proof and residual-survival truth are still too fragmented to clone even though the ingredients are useful.
4. Adds one new **contract sheet** page so the operator must explicitly name governed audience slices, residual carriers, closure horizon, unknown-residue budget, and strongest honest closure sentence.
5. Adds one new **review** page that asks directly what proves the governed audience actually closed and which residual stale carriers still survive.
6. Adds one new **proof** page that preserves peer confirmations, link-expiry evidence, residual unknowns, and closure-ceiling truth instead of pretending that one disconnect, one expiry, or one cleanup act proves audience-wide closure.
7. Adds one new **timeline** page so intercept, revoke, expire, confirm, nonresponse, residue discovery, and closure become separate visible events.
8. Adds one new **lineage receipt** page that compresses the result into a portable audience-closure verdict with surviving residual audience and blocked stronger sentences still attached.

New docs in this tranche:

- `2152-resilio-remedy-hardening-attestation-audience-wide-closure-proof-and-residual-survival-ceiling-fragmentation-evaluation.md`
- `2153-remedy-hardening-attestation-closure-proof-contract-sheet-page-governed-audience-residual-carriers-and-proof-ceiling-interface-spec.md`
- `2154-remedy-hardening-attestation-closure-proof-review-page-after-containment-what-proves-the-governed-audience-actually-closed-and-what-residue-still-survives-interface-spec.md`
- `2155-remedy-hardening-attestation-closure-proof-page-link-expiry-peer-confirmation-residual-unknowns-and-closure-sentence-ceiling-interface-spec.md`
- `2156-remedy-hardening-attestation-closure-proof-timeline-page-intercept-revoke-expire-confirm-nonresponse-residue-discover-and-horizon-close-events-interface-spec.md`
- `2157-remedy-hardening-attestation-closure-proof-lineage-receipt-page-audience-closure-verdict-residual-survivors-and-blocked-stronger-sentences-interface-spec.md`

"""

STATUS_ADD = """## rev0502 — audience-wide closure proof and residual-survival ceiling

This tranche adds one more hard line to the doctrine:

- **auditable containment and automatic relapse interception are weaker than audience-wide closure proof and residual-survival truth**
- **one intercepted channel is weaker than a closed governed audience**
- **link expiry, disconnect, UI removal, and one-device cleanup are weaker than explicit residual-survivor accounting**
- **unknown residual audience and unknown stale carriers must stay explicit instead of dissolving into `we contained it` folklore**

What this tranche contributes to the larger doctrine:

- `we intercepted the relapse` can no longer silently stand in for `the governed audience actually closed`
- `the link expired` can no longer silently stand in for `already-reached peers or recipients no longer hold stale bytes`
- `the folder was removed from linked devices` can no longer silently stand in for `all relevant devices or audience slices are clean`
- `one peer was cleaned up` can no longer silently stand in for `residual survivors were enumerated`
- containment can no longer silently stand in for closure proof

What remains intentionally true:

- containment still matters
- recurrence watch still matters
- clean-state verification still matters
- exposure budgets still matter
- but none of those may substitute for one explicit answer about whether the governed audience actually closed, which stale carriers still survive, and what stronger sentence remains blocked because residual survival is still partly unknown

New docs added in this tranche:

- `2152-resilio-remedy-hardening-attestation-audience-wide-closure-proof-and-residual-survival-ceiling-fragmentation-evaluation.md`
- `2153-remedy-hardening-attestation-closure-proof-contract-sheet-page-governed-audience-residual-carriers-and-proof-ceiling-interface-spec.md`
- `2154-remedy-hardening-attestation-closure-proof-review-page-after-containment-what-proves-the-governed-audience-actually-closed-and-what-residue-still-survives-interface-spec.md`
- `2155-remedy-hardening-attestation-closure-proof-page-link-expiry-peer-confirmation-residual-unknowns-and-closure-sentence-ceiling-interface-spec.md`
- `2156-remedy-hardening-attestation-closure-proof-timeline-page-intercept-revoke-expire-confirm-nonresponse-residue-discover-and-horizon-close-events-interface-spec.md`
- `2157-remedy-hardening-attestation-closure-proof-lineage-receipt-page-audience-closure-verdict-residual-survivors-and-blocked-stronger-sentences-interface-spec.md`

## Current frontier after rev0502 — durable closure and late-survivor rediscovery truth

The next seam after **audience-wide closure proof and residual-survival truth** is now explicit:

- the archive can already say whether relapse channels are watched
- it can already say whether some relapse channels are actually intercepted
- it can now say whether the governed audience is provably closed or whether residual survivors remain
- it still needs to own the harder truth of **whether closure stays durable when late-surviving copies, long-offline peers, forwarded artifacts, or forgotten local residue resurface after the declared closure horizon**

This pass therefore keeps the next visible step explicit: **durable closure and late-survivor rediscovery truth**.

"""

RESILIO_ADD = """## Revision addendum after rev0501 — why remedy hardening attestation audience-wide closure proof and residual-survival truth now sit on the non-clone side

Current official Resilio docs are still admirably candid that `a relapse channel was intercepted`, `a folder was disconnected`, `a link expired`, `a transfer was removed from UI`, `linked devices no longer show the folder`, and `the governed audience is therefore closed` are not one flat truth.
`Disconnecting and Removing Folders` still says disconnect affects one device while leaving the folder in the file system, remove affects devices linked to your identity, and remote devices not linked to your identity may still keep the folder.
`Sharing single file` still says recipients can share the received files further and removing the file from Sync UI does not remove it from the device.
`Sync Share Dialog (Desktop)` still says folder-share links can expire after N days and can have click-count limits, which constrains future joins but does not itself prove that previously reached peers or recipients are now clean.
`Can Resilio team see and block/remove any Sync folders?` still says Resilio neither hosts nor can centrally modify or remove peer copies, and link distribution occurs on users' devices.
`User Management` still says linked devices under one identity all act as Owners, so the closure story depends on which audience slice actually held authority and bytes.
`Sharing a folder locally` still says local shares remain only on the configured device and do not auto-reconnect, which is useful topology candor but still separate from any portable closure proof.

This is strong closure-boundary candor.
It is also exactly why AnonSync should not clone the present contract.
One ordinary answer to `after containment, is the governed audience actually closed and what stale carriers still survive?` still depends on combining disconnect scope, linked-vs-unlinked device scope, single-file residue, folder-link expiry semantics, decentralized deletion limits, owner / linked-identity scope, and local-share topology.

So this tranche freezes a stronger replacement line: **governed audience slice, residual carrier set, closure horizon, explicit survivor ledger, closure evidence set, strongest honest closure sentence, and blocked stronger closure sentence become separate modeled truths.**

That is why this revision adds five more first-class pages: **closure-proof contract sheet**, **closure-proof review**, **closure-proof page**, **closure-proof timeline**, and **closure-proof lineage receipt**.

"""

PRODUCT_ADD = """## Product-direction addendum after rev0501 — audience-wide closure proof is first-class

AnonSync should not let `intercepted`, `expired`, `disconnected`, or `removed` stand in for whether the governed audience actually closed.
The product direction is now explicit:

- **audience-wide closure proof is first-class**
- **containment posture, closure posture, and survivor posture remain separate**
- **future access blocked is weaker than already-held residue retired**
- **one cleaned peer is weaker than a closed audience slice**
- **unknown residual survivors stay visible instead of being rounded down to zero**

That means future interface work should keep one stable family for:

- governed audience boundary
- residual carrier set
- closure horizon
- confirmed-closed slice count
- unknown / unconfirmed survivor set
- strongest honest closure sentence

The product should never force the operator to infer those truths from one expired link, one disconnect action, one removed folder, or one support-side statement that the issue is closed.

"""

SOURCES_ADD = """## rev0502 source set — remedy hardening attestation audience-wide closure proof and residual-survival truth

The most load-bearing source set for this pass was:

- Resilio's current `Disconnecting and Removing Folders` article, which still says disconnect affects one device while leaving the folder in the file system, remove affects devices linked to your identity, and remote devices not linked to your identity may still keep the folder.
- Resilio's current `Sharing single file` article, which still says recipients can share received files further, the link can be non-expiring, and removing the file from Sync UI does not remove it from the device.
- Resilio's current `Sync Share Dialog (Desktop)` article, which still says folder links can expire after N days or after N uses, constraining future connects but not itself proving already-reached recipients are now clean.
- Resilio's current `Can Resilio team see and block/remove any Sync folders?` article, which still says Resilio neither hosts nor can centrally modify or remove peer copies and does not control link distribution.
- Resilio's current `User Management` article, which still says all devices linked under one identity act as Owners, so closure scope depends on which audience slices actually held authority and bytes.
- Resilio's current `Sharing a folder locally` article, which still says local shares remain on the configured device only and require manual reconnect if the source share returns.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for candid closure-boundary ingredients
- but current Resilio still answers `after containment, is the governed audience actually closed and what stale carriers still survive?` too diffusely
- AnonSync should therefore prefer explicit remedy-hardening-attestation closure-proof sheets, closure-proof reviews, closure-proof pages, closure-proof timelines, and durable closure-proof lineage receipts over overloaded disconnect lore, expiry folklore, linked-device assumptions, one-time-transfer residue assumptions, and decentralized deletion limits

Primary sources:

- Disconnecting and Removing Folders
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- Sharing single file
  https://help.resilio.com/hc/en-us/articles/115000401010-Sharing-single-file

- Sync Share Dialog (Desktop)
  https://help.resilio.com/hc/en-us/articles/204790709-Sync-Share-Dialog-Desktop

- Can Resilio team see and block/remove any Sync folders?
  https://help.resilio.com/hc/en-us/articles/205451105-Can-Resilio-team-see-and-block-remove-any-Sync-folders

- User Management
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- Sharing a folder locally
  https://help.resilio.com/hc/en-us/articles/360011582500-Sharing-a-folder-locally

"""

def write(path: str, text: str) -> None:
    (base / path).write_text(text)

write('docs/2152-resilio-remedy-hardening-attestation-audience-wide-closure-proof-and-residual-survival-ceiling-fragmentation-evaluation.md', """# Resilio remedy-hardening attestation audience-wide closure proof and residual-survival ceiling fragmentation evaluation

## Why this seam matters now

The archive can already say:

- the outsider reached a clean state
- that clean state was watched across a named horizon
- relapse channels can be named
- some relapse channels can even be intercepted before further spread
- containment residue can be described more honestly than before

That is still weaker than a harder question:

**after interception or narrowing, is the governed audience actually closed, which stale carriers still survive, and what proof survives that closure claim later?**

A contained channel is not yet a closed audience.
A closed audience claim without a survivor ledger is not yet closure proof.

## Why current Resilio still leaves this too diffuse to clone

Current official Resilio material is candid about several partial-closure ingredients, but it still spreads them across separate pages:

- `Disconnecting and Removing Folders` says disconnect affects one device while leaving the folder in the file system, remove affects devices linked to your identity, and remote devices not linked to your identity may still keep the folder
- `Sharing single file` says recipients can share the received files further and removing the file from Sync UI does not remove it from the device
- `Sync Share Dialog (Desktop)` says links can expire after N days or after N uses, constraining future joins without proving that previously reached peers or recipients are now clean
- `Can Resilio team see and block/remove any Sync folders?` says Resilio neither hosts nor can centrally remove peer copies, so cleanup must happen on users' own devices
- `User Management` says linked devices under one identity all act as Owners, which means closure scope depends on which audience slices actually held authority and bytes
- `Sharing a folder locally` says local shares remain on the configured device only, do not auto-reconnect, and remain attached to source-share state

This is good closure-shaping candor.
It is not yet one first-class answer to **after containment, what audience slice is actually closed, what residual stale carriers still survive, and what portable evidence justifies the closure sentence that remains?**

## The non-clone line

AnonSync should not clone a contract where all of these are allowed to blur together:

- future joins are blocked
- linked devices were removed
- one peer was cleaned up
- recipients still keep already-downloaded files
- forwarded copies or local-share residues remain possible
- remote unlinked devices may still hold the folder
- the governed audience is therefore said to be closed

Those are separate truths.

## Product decision frozen in this tranche

This revision freezes a stronger line:

- **auditable containment and automatic relapse interception are weaker than audience-wide closure proof and residual-survival truth**
- **a contained channel is weaker than a closed governed audience**
- **link expiry, disconnect, and UI removal are weaker than explicit survivor accounting**
- **unknown residual survivors may never impersonate `closure succeeded`**

## What AnonSync should model explicitly instead

AnonSync should add one first-class family for:

- governed audience slice
- residual carrier set
- closure horizon
- confirmed-closed slice set
- unknown / unconfirmed survivor set
- closure evidence artifact set
- strongest honest closure sentence
- blocked stronger closure sentence

## Interface consequence

That is why this tranche adds five more first-class pages:

- **closure-proof contract sheet**
- **closure-proof review**
- **closure-proof page**
- **closure-proof timeline**
- **closure-proof lineage receipt**
""")

write('docs/2153-remedy-hardening-attestation-closure-proof-contract-sheet-page-governed-audience-residual-carriers-and-proof-ceiling-interface-spec.md', """# Remedy-hardening-attestation closure-proof contract sheet page — governed audience, residual carriers, and proof ceiling

## Purpose

This contract sheet exists so the archive can say exactly what closure claim is being attempted after containment.
It should prevent the operator from silently collapsing `future access blocked` into `audience closed`.

## Required sections

The page must render the same sections in the same order:

1. **Governed audience boundary**
2. **Residual carrier inventory**
3. **Closure horizon and evidence plan**
4. **Strongest honest closure sentence**

### 1) Governed audience boundary

This section must show:

- named audience slices in scope
- which slices are linked devices
- which slices are remote unlinked peers
- which slices are single-file recipients
- which slices are public or forwarded unknowns
- which slices are downstream dependents rather than direct holders

The operator must be able to answer: **who exactly are we trying to close?**

### 2) Residual carrier inventory

This section must list every stale-carrier class that may survive, including at least:

- still-synced folders
- disconnected-but-local folders
- linked-device removed copies
- unlinked remote copies
- single-file downloaded copies
- forwarded or reshared copies
- local-share attachments
- archive or hidden local residue
- screenshots, exports, or non-sync public artifacts if applicable

The operator must be able to answer: **what stale carriers may still exist even after containment?**

### 3) Closure horizon and evidence plan

This section must show:

- closure horizon length
- required confirmations per audience slice
- evidence classes allowed to count toward closure
- evidence classes that are informative but insufficient
- unknown-survivor budget
- automatic invalidators for the closure claim

The operator must be able to answer: **what proof would be enough, and what would still leave closure blocked?**

### 4) Strongest honest closure sentence

This section must preserve two separate sentences:

- strongest honest closure sentence now
- blocked stronger closure sentence

Examples:

- `future joins blocked, survivor set still partly unknown`
- `linked devices closed, remote unlinked closure unproven`
- `named recipients confirmed closed, forwarded copies still possible`
- `audience-wide closure not yet provable`

## Hard rules

The page must never:

- collapse link expiry into recipient cleanup
- collapse linked-device removal into unlinked-peer closure
- omit unknown or unconfirmed survivor slices
- emit `closed` without naming closure scope
""")

write('docs/2154-remedy-hardening-attestation-closure-proof-review-page-after-containment-what-proves-the-governed-audience-actually-closed-and-what-residue-still-survives-interface-spec.md', """# Remedy-hardening-attestation closure-proof review page — after containment, what proves the governed audience actually closed and what residue still survives?

## Purpose

This review page asks the one question containment cannot answer by itself:

**after we intercepted or narrowed the relapse, what proves the governed audience actually closed, and which stale carriers still survive?**

## Mandatory review prompts

The review must force explicit answers to at least:

1. Which audience slices are confirmed closed, and by what evidence?
2. Which audience slices are only inferred closed?
3. Which audience slices remain unknown or nonresponsive?
4. Which stale-carrier classes can still survive despite future access being blocked?
5. Which closure claim would become dishonest if a late-surviving copy were rediscovered tomorrow?

## Review buckets

### Confirmed-closed slices

For each slice, the page must show:

- slice name
- evidence class
- time of last confirming evidence
- whether the evidence proves byte retirement, merely disconnection, or only future-access blocking

### Unconfirmed or unknown slices

For each slice, the page must show:

- why closure is not yet proven
- whether the slice is expected to respond
- what residual stale carriers may survive there
- what stronger sentence stays blocked because of it

### Residual carrier review

The page must separately review at least:

- already-downloaded single-file copies
- disconnected local copies
- remote unlinked copies
- local-share derivatives
- forwarded/reshared artifacts
- hidden archive or placeholder-related residue where applicable

## Refusal rules

The review must refuse to bless a closure claim if:

- any required audience slice is still unknown and not explicitly tolerated by policy
- the proof only shows link expiry or approval revocation without recipient-side state evidence
- the proof only covers linked devices while the governed audience includes unlinked peers or recipients
- the survivor ledger is missing

## Output

The output must be one of:

- `closure proven for named slices only`
- `closure partly proven with explicit survivors`
- `closure blocked by unknown survivors`
- `closure claim collapsed`
""")

write('docs/2155-remedy-hardening-attestation-closure-proof-page-link-expiry-peer-confirmation-residual-unknowns-and-closure-sentence-ceiling-interface-spec.md', """# Remedy-hardening-attestation closure-proof page — link expiry, peer confirmation, residual unknowns, and closure sentence ceiling

## Purpose

This proof page preserves the evidence bundle for a closure claim.
It exists so the archive can distinguish `future access blocked` from `audience actually closed`.

## Minimum evidence families

The page must preserve at least these evidence families when applicable:

- peer-side confirmation of retirement or removal
- linked-device removal evidence
- unlinked-peer confirmation evidence
- single-file recipient retirement evidence
- link-expiry or click-budget exhaustion evidence
- approval revocation or share-right removal evidence
- residual local-share or local-folder evidence
- unknown-survivor ledger

## Evidence grading

Each evidence item must be graded as one of:

- proves byte retirement
- proves future access blocked only
- proves authority revoked only
- proves visibility changed only
- suggests but does not prove cleanup
- contradicts closure claim

## Required summary fields

The proof page must summarize at least:

- governed audience size in scope
- confirmed-closed slice count
- inferred-closed slice count
- unknown slice count
- known surviving residual-carrier count
- highest-severity unknown survivor class
- strongest honest closure sentence
- blocked stronger closure sentence

## Sentence ceiling rule

The page must never allow a stronger closure sentence than the weakest unresolved survivor fact permits.
For example:

- expired link without recipient proof must not justify `recipient closed`
- disconnect without filesystem retirement proof must not justify `device clean`
- linked-device removal without unlinked-peer evidence must not justify `audience closed`
- UI removal without local-byte retirement proof must not justify `residue retired`
""")

write('docs/2156-remedy-hardening-attestation-closure-proof-timeline-page-intercept-revoke-expire-confirm-nonresponse-residue-discover-and-horizon-close-events-interface-spec.md', """# Remedy-hardening-attestation closure-proof timeline page — intercept, revoke, expire, confirm, nonresponse, residue discover, and horizon close events

## Purpose

This page makes closure legible over time.
It exists so the archive can show not only that containment happened, but also whether later evidence actually closed the governed audience or merely narrowed it.

## Timeline events the page must support

The page must support at least:

- containment event fired
- share or approval revoked
- link expired
- click budget exhausted
- linked-device folder removed
- unlinked peer confirmed clean
- recipient confirmed retirement
- local-share residue discovered
- forwarded artifact discovered
- audience slice marked nonresponsive
- survivor ledger revised
- closure horizon closed
- late survivor discovered after closure

## Event requirements

Each event row must preserve:

- timestamp or bounded time window
- actor / audience slice / surface
- event class
- affected carrier class
- whether the event widened closure proof, narrowed it, contradicted it, or only changed future-access posture
- whether the strongest honest closure sentence changed

## Closure rule

The timeline must not allow `closure horizon closed` unless it also records:

- which slices were confirmed closed
- which slices remained unknown but tolerated
- what residual carriers still survived
- what evidence justified the final sentence anyway
- what stronger sentence stayed blocked despite closure

## Visual emphasis

The page should visually distinguish:

- containment events
- future-access-blocking events
- recipient confirmation events
- nonresponse / unknown-survivor events
- late-survivor discovery events
- final closure event
""")

write('docs/2157-remedy-hardening-attestation-closure-proof-lineage-receipt-page-audience-closure-verdict-residual-survivors-and-blocked-stronger-sentences-interface-spec.md', """# Remedy-hardening-attestation closure-proof lineage receipt page — audience closure verdict, residual survivors, and blocked stronger sentences

## Purpose

This receipt is the compact lineage object for later readers who need one portable answer to:

**after containment, is the governed audience actually closed, only partly closed, or still carrying known or unknown stale survivors elsewhere?**

## Receipt header

The receipt header must show at least:

- governed audience label
- corrected replacement identifier
- closure horizon class
- highest-severity open survivor class
- closure verdict

## Minimum body fields

The receipt body must preserve at least:

- confirmed-closed slice count
- inferred-closed slice count
- unknown slice count
- known residual survivor summary
- unknown residual survivor summary
- closure evidence summary
- strongest honest closure sentence
- blocked stronger closure sentence

## Verdict classes

The receipt must support at least:

- future access blocked only
- linked-slice closure only
- named-slice closure with explicit survivors
- closure partly proven with unknown survivors tolerated
- audience-wide closure not provable
- closure contradicted by late survivor
- insufficient closure proof

## Hard rules

The receipt must never:

- collapse `future joins blocked` into `audience closed`
- collapse `linked devices removed` into `all holders clean`
- omit unknown survivor slices
- omit known surviving carrier classes
- omit the blocked stronger sentence
""")

prepend(base / 'README.md', README_ADD)
prepend(base / 'docs/00-status.md', STATUS_ADD)
prepend(base / 'docs/10-resilio-sync-evaluation.md', RESILIO_ADD)
prepend(base / 'docs/20-product-direction.md', PRODUCT_ADD)
prepend(base / 'docs/sources.md', SOURCES_ADD)
