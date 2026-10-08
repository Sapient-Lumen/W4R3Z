from pathlib import Path

base = Path(__file__).resolve().parent
docs = base / 'docs'

def prepend(path: Path, text: str) -> None:
    path.write_text(text + path.read_text())

README_ADD = """## Revision addendum after rev0493 — external representation retirement and public-claim truth

This continuation archive advances the doctrine by tightening the next concrete seam after governed-audience stale-dependency retirement:
**what happens after the named beneficiary stayed switched and the governed audience may even have stopped relying on stale state, but before the product may honestly pretend that public links, exported copies, screenshots, forwarded attachments, quoted summaries, and outsider-facing claim surfaces also stopped misdescribing reality**.
It does eight things in one tranche:

1. Continues the archive after rev0493 with a new page family centered on whether repair remained internal to the governed audience or also retired stale external representations and public-facing claim residue.
2. Tightens the non-clone line again: borrow Resilio's candor about share links, landing pages, permissioned share dialogs, email delivery, expiration and use-count controls, and one-time file-transfer residue; refuse any contract where the operator still has to reconstruct `did outsiders stop seeing or circulating stale public claims?` from scattered link, share, and transfer notes.
3. Adds one new **Resilio evaluation** document focused on why current external representation retirement and public-claim truth is still too fragmented to clone even though the ingredients are useful.
4. Adds five new **interface specs** for public-claim contract sheet, review, proof, timeline, and lineage receipt.
5. Makes one hard product decision explicit: **governed-audience stale-dependency retirement is weaker than external representation retirement and public-claim truth.**
6. Makes another hard product decision explicit: **withdrawing future access is weaker than retiring already-circulating outsider-facing representations.**
7. Makes a third hard product decision explicit: **a corrected internal audience, an expired link, or a superseded local copy are not allowed to impersonate `outsiders stopped receiving a stale public claim`.**
8. Packages the result as another continuation archive whose new tranche makes the `public surface boundary / representation carrier set / circulation residue / withdrawal coverage / strongest honest outsider-facing sentence / blocked stronger public-truth sentence` seam explicit in the reading order and page family.

New docs in this tranche:

- `2104-resilio-remedy-hardening-attestation-external-representation-retirement-and-public-claim-truth-fragmentation-evaluation.md`
- `2105-remedy-hardening-attestation-public-claim-contract-sheet-page-external-representation-scope-carrier-set-and-claim-ceiling-interface-spec.md`
- `2106-remedy-hardening-attestation-public-claim-review-page-did-external-representations-stop-misleading-outsiders-after-the-correction-interface-spec.md`
- `2107-remedy-hardening-attestation-public-claim-proof-page-representation-retirement-ledger-public-surface-coverage-and-claim-sentence-ceiling-interface-spec.md`
- `2108-remedy-hardening-attestation-public-claim-timeline-page-link-published-export-forwarded-public-copy-withdrawn-and-claim-horizon-closed-events-interface-spec.md`
- `2109-remedy-hardening-attestation-public-claim-lineage-receipt-page-public-representation-summary-residual-misstatement-risk-and-blocked-stronger-truth-sentences-interface-spec.md`

"""

STATUS_ADD = """## rev0494 — external representation retirement and public-claim truth ceiling

This tranche adds one more hard line to the doctrine:

- **governed-audience stale-dependency retirement is weaker than external representation retirement and public-claim truth**
- **repair inside the named audience is weaker than outsider-facing correction of public links, exports, forwards, screenshots, and quoted summaries**
- **link expiration, disconnect, approval, or supersession are weaker than positive proof that already-circulating stale representations stopped misleading outsiders**
- **public surfaces must stay explicit instead of dissolving into `the correction took effect` folklore**

What this tranche contributes to the larger doctrine:

- `the governed audience stopped relying on stale state` can no longer silently stand in for `outsiders stopped seeing or circulating stale public claims`
- `the link expired` can no longer silently stand in for `public representation retired`
- `the share was revoked` can no longer silently stand in for `already-forwarded copies disappeared`
- `the exported report was superseded internally` can no longer silently stand in for `public consumers no longer encounter the stale version`
- internal audience truth can no longer silently stand in for public-claim truth

What remains intentionally true:

- beneficiary adherence still matters
- governed-audience stale-dependency retirement still matters
- link expiration still matters
- revocation still matters
- internal supersession still matters
- but none of those may substitute for one explicit answer about whether external representations and public-facing claims were actually repaired, withdrawn, or still circulating with stale meaning

New docs added in this tranche:

- `2104-resilio-remedy-hardening-attestation-external-representation-retirement-and-public-claim-truth-fragmentation-evaluation.md`
- `2105-remedy-hardening-attestation-public-claim-contract-sheet-page-external-representation-scope-carrier-set-and-claim-ceiling-interface-spec.md`
- `2106-remedy-hardening-attestation-public-claim-review-page-did-external-representations-stop-misleading-outsiders-after-the-correction-interface-spec.md`
- `2107-remedy-hardening-attestation-public-claim-proof-page-representation-retirement-ledger-public-surface-coverage-and-claim-sentence-ceiling-interface-spec.md`
- `2108-remedy-hardening-attestation-public-claim-timeline-page-link-published-export-forwarded-public-copy-withdrawn-and-claim-horizon-closed-events-interface-spec.md`
- `2109-remedy-hardening-attestation-public-claim-lineage-receipt-page-public-representation-summary-residual-misstatement-risk-and-blocked-stronger-truth-sentences-interface-spec.md`

## Current frontier after rev0494 — discoverability replacement and future resurfacing truth

The next seam after **governed-audience reliance truth and external public-claim repair** is now explicit:

- the archive can already say whether one beneficiary stayed switched
- it can now say whether the governed downstream audience retired stale dependencies
- it can now say whether named public representations were withdrawn, superseded, or left circulating
- it still needs to own the harder truth of **whether search indexes, later rediscovery surfaces, quoted fragments, and future resurfacing channels now preferentially surface the corrected representation instead of the stale one**

This pass therefore makes the next possible step visible: **discoverability replacement and future resurfacing truth**.

"""

RESILIO_ADD = """## Revision addendum after rev0493 — why external representation retirement and public-claim truth now sit on the non-clone side

Current official Resilio docs are still admirably candid that `the named audience may now be correct`, `the link expired`, `the share uses approvals`, `the transfer finished`, and `outsiders stopped seeing or circulating stale public claims` are not one flat truth.
`Link structure and flow` still says Sync links open through a Resilio landing page that exposes basic folder info such as folder name and size.
`Sync Share Dialog (Desktop)` still says share links can be copied or dropped into e-mail or messengers, can have approval requirements, can expire after N days, and can have a click-count limit for new connections.
`Quick guide to syncing` still says the link or key is delivered by e-mail or other means of communication.
`Sharing single file` still says a file-transfer link can be made non-expiring, there is no option to restrict the number of uses or ban some devices from using the link, recipients can share received files further, and removing the file from Sync UI does not remove it from the device.

This is strong outsider-surface candor.
It is also exactly why AnonSync should not clone the present contract.
One ordinary answer to `granted that the governed internal audience is repaired, did stale outsider-facing representations also disappear or get superseded?` still depends on combining landing-page exposure, copy-pastable share links, e-mail delivery, expiration windows, click limits, one-time transfer residue, recipient resharing, and local-device persistence.

So this tranche freezes a stronger replacement line: **public surface boundary, representation carrier set, circulation path, withdrawal coverage, residual public residue, strongest honest outsider-facing sentence, and blocked stronger public-truth sentence must all become first-class and reviewable.**

"""

PRODUCT_ADD = """## Product-direction addendum after rev0493 — audience repair must graduate into explicit external representation retirement and public-claim truth

AnonSync should not let internal audience repair masquerade as public-truth repair.
The product direction is now explicit:

- every correction flow that can produce outward-facing artifacts must also name the public surface boundary that matters for this action
- every public-facing artifact class must remain explicit (`share links`, `landing pages`, `exported files`, `forwarded attachments`, `quoted summaries`, `screenshots`, `embedded copies`, `other`)
- expiring a link, revoking future access, or superseding one internal artifact must not silently count as retirement of already-circulating public representations
- the strongest sentence engine must preserve the difference between `internal audience repaired`, `named public surface repaired`, and `broader public truth still blocked`
- the receipt family must stay portable enough that a later reader can tell whether a stale public claim may still circulate even if the internal audience is clean

That means future interface work should keep one stable family for:

- public surface boundary
- representation carrier set
- circulation and forwarding path summary
- withdrawal / supersession / disclaimer status
- residual public residue set
- strongest honest outsider-facing sentence ceiling

The product should never force the operator to infer those truths from a green sync badge, an expired link, or a local deletion event.

"""

SOURCES_ADD = """## rev0494 source set — external representation retirement and public-claim truth

The most load-bearing source set for this pass was:

- Resilio's current `Link structure and flow` article, which still says folder links open through a Resilio landing page that shows basic info such as folder name and size.
- Resilio's current `Sync Share Dialog (Desktop)` article, which still says links can be copied into e-mail or messengers, can require approval, can expire after N days, and can carry a click-count limit.
- Resilio's current `Quick guide to syncing` article, which still says a link or key is delivered by e-mail or other means of communication.
- Resilio's current `Sharing single file` article, which still says file-transfer links may be made non-expiring, there is no option to restrict the number of uses or ban some devices from using the link, recipients can share the files further, and removing the file from Sync UI does not remove it from the device.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for candid external-surface ingredients
- but current Resilio still answers `did stale outsider-facing representations and public claims actually get retired?` too diffusely
- AnonSync should therefore prefer explicit public-claim contract sheets, public-claim reviews, public-claim proofs, public-claim timelines, and durable public-claim lineage receipts over overloaded link TTLs, approval toggles, click-count limits, share dialogs, and local device residue clues

Primary sources:

- Link structure and flow
  https://help.resilio.com/hc/en-us/articles/204754739-Link-structure-and-flow

- Sync Share Dialog (Desktop)
  https://help.resilio.com/hc/en-us/articles/204790709-Sync-Share-Dialog-Desktop

- Quick guide to syncing
  https://help.resilio.com/hc/en-us/articles/205506699-Quick-guide-to-syncing

- Sharing single file
  https://help.resilio.com/hc/en-us/articles/115000401010-Sharing-single-file

"""

DOCS = {
    '2104-resilio-remedy-hardening-attestation-external-representation-retirement-and-public-claim-truth-fragmentation-evaluation.md': """# Resilio remedy-hardening attestation external representation retirement and public-claim truth fragmentation evaluation

## Why this seam matters now

The archive can already say:

- the beneficiary was legitimate
- the beneficiary stayed on the canonical correction lane
- the beneficiary noticed, acknowledged, adopted, and may have durably adhered to the corrected working state
- the governed downstream audience may have retired stale dependencies for the named boundary

That is still weaker than a harder question:

**after the governed audience is repaired, did outsider-facing representations also stop misdescribing reality, or do old links, landing pages, forwarded files, screenshots, exported copies, quoted summaries, and other public-facing surfaces still circulate a stale claim?**

An internal audience-wide success claim is not a public-truth claim.
Public-truth requires a public surface boundary, representation carrier classes, circulation paths, retirement or disclaimer evidence, and explicit coverage language.
Without those, `the correction took effect` quietly expands into folklore about outsiders no longer being misled.

## Why current Resilio still leaves this too diffuse to clone

Current official Resilio material is candid about several outsider-facing representation surfaces, but it still spreads them across separate pages:

- `Link structure and flow` says Sync links open through a Resilio landing page and that page shows basic folder information such as folder name and size
- `Sync Share Dialog (Desktop)` says links can be copied or sent through e-mail or messengers, can require approval, can expire after N days, and can have a click-count limit
- `Quick guide to syncing` says the link or key is delivered by e-mail or other means of communication
- `Sharing single file` says a file-transfer link may be made non-expiring, there is no option to restrict the number of uses or ban some devices from using the link, recipients can share the received files further, and removing the file from Sync UI does not remove it from the device

This is good operational candor.
It is not yet one first-class answer to **did the named outsider-facing representations get retired, superseded, or still circulate with stale meaning?**

## The non-clone line

AnonSync should not clone a contract where all of these are allowed to blur together:

- the governed internal audience is repaired
- the old share link has expired for new connections
- the operator revoked future access
- the file transfer finished once
- the public link was copied into mail or messenger threads
- recipients can forward or reshare what they received
- the stale file still remains on devices that already downloaded it
- the landing page or forwarded artifact still carries an outdated representation
- outsiders therefore are no longer at risk of receiving a stale public claim

Those are separate truths.

## Product decision frozen in this tranche

This revision freezes a stronger line:

- **governed-audience stale-dependency retirement is weaker than external representation retirement and public-claim truth**
- **future-access revocation is weaker than retirement of already-circulating outsider-facing representations**
- **link expiration, approval, or one green transfer checkmark may never impersonate `outsiders stopped seeing or circulating a stale public claim`**

## What AnonSync should model explicitly instead

AnonSync should add one first-class family for:

- source audience-reliance receipt identifier
- public surface identifier
- public surface boundary rule
- representation carrier class set
- circulation path summary
- withdrawal / supersession / disclaimer carrier set
- public-surface coverage class
- unresolved stale-public-representation set
- strongest honest outsider-facing sentence
- blocked stronger public-truth sentence

## Interface consequence

That is why this tranche adds five more first-class pages:

- **public-claim contract sheet**
- **public-claim review**
- **public-claim proof**
- **public-claim timeline**
- **public-claim lineage receipt**
""",
    '2105-remedy-hardening-attestation-public-claim-contract-sheet-page-external-representation-scope-carrier-set-and-claim-ceiling-interface-spec.md': """# Remedy-hardening-attestation public-claim contract sheet page — external representation scope, carrier set, and claim ceiling

## Purpose

This page is the operator-facing sheet for deciding whether stale meaning retired only inside the governed audience or also across the outsider-facing representations that still describe the subject to third parties.
It exists to stop `the audience is repaired`, `the link expired`, or `the share was revoked` from being mistaken for `outsiders no longer encounter a stale public claim`.

## Core question

The page must answer:

**for this named public surface and representation carrier set, what is the strongest honest sentence about stale public-claim retirement now?**

## Minimum fields

The contract sheet must show at least:

- action identifier
- source audience-reliance receipt identifier
- public surface identifier
- public surface boundary rule
- canonical correction identifier
- representation carrier class set (`share links`, `landing pages`, `exported files`, `forwarded attachments`, `screenshots`, `quoted summaries`, `embedded copies`, `other`)
- circulation path summary
- withdrawal / supersession / disclaimer carrier set
- intended public-surface coverage class
- current public-surface coverage class
- unresolved stale-public-representation count
- highest-risk unresolved public surface
- strongest honest outsider-facing sentence now
- blocked stronger public-truth sentence now

## Standing ladder

The page must support at least these distinct standings:

- internal audience repaired only
- named public surface under review
- some public representations superseded, others still circulating
- link expired, but already-circulating representations still open
- disclaimer applied without full withdrawal
- named public surface repaired, broader public truth unproven
- later contradiction reopened public-claim risk
- receipt superseded

## Required comparisons

The sheet must compare:

- internal audience truth versus public-claim truth
- future-access revocation versus already-circulating representation retirement
- withdrawal versus disclaimer versus supersession
- named public surface versus broader public reach
- current best sentence versus blocked stronger public-truth sentence

## Required layout

### Header

Show:

- correction name
- public surface name
- current public-claim standing
- strongest honest outsider-facing sentence now

### Left column — intended public-truth contract

Show:

- public surface boundary rule
- representation carrier classes in scope
- circulation path summary
- required withdrawal / supersession / disclaimer carriers
- required coverage threshold

### Center column — observed representation facts

Show:

- active stale link count
- forwarded-copy residue count
- screenshot / quote residue count
- superseded export count
- withdrawn artifact count
- disclaimer coverage status
- evidence freshness for the public surface map

Every row in this column must have:

- current value
- evidence source
- whether it strengthens or weakens public-truth confidence

### Right column — consequence for truth

Show:

- whether only the internal audience is known-clean
- whether named public surfaces were repaired but broader public reach remains open
- whether stale outsider-facing artifacts still circulate
- whether the public-truth sentence is honest or still blocked
- what stronger sentence remains blocked

### Footer decision rail

The footer must make it impossible to flatten these into one answer:

- internal audience repaired only
- some public artifacts superseded
- link expired but public residue remains
- named public surface repaired
- broader public-truth sentence still blocked

## Interaction requirements

The interface must support:

- clicking the public-surface badge to open the exact boundary rule and exclusions
- clicking any public-representation chip to open its carrier, circulation path, age, and retirement status
- pinning one public surface while comparing several coverage thresholds
- filtering the surface map to links, exports, forwards, screenshots, quotes, or embedded copies

## Hard rules

The page must never allow:

- internal audience repair to silently become public-truth repair
- link expiration to silently become retirement of already-circulating artifacts
- one superseded export to silently become full public-surface repair
- a named public surface sentence to silently become broader public truth
""",
    '2106-remedy-hardening-attestation-public-claim-review-page-did-external-representations-stop-misleading-outsiders-after-the-correction-interface-spec.md': """# Remedy-hardening-attestation public-claim review page — did external representations stop misleading outsiders after the correction?

## Purpose

This page is the forced-review surface for deciding whether stale public meaning stopped circulating outside the governed audience.
It exists to stop the operator from exiting with a comfortable internal-repair story while old links, forwarded files, screenshots, exported copies, or quoted summaries still mislead outsiders.

## Opening question

The page must ask, in plain language:

**did external representations stop misleading outsiders after the correction, or do stale links, forwarded artifacts, screenshots, exports, or quoted summaries still circulate?**

## Required reviewer prompts

The reviewer must answer at least:

1. What is the exact public surface boundary?
2. Which representation carrier classes are positively repaired or withdrawn?
3. Which carrier classes remain inferred rather than directly proved?
4. Did we only revoke future access, or did we also address already-circulating public artifacts?
5. Which stale outsider-facing artifacts still remain active?
6. Is a disclaimer present where withdrawal or supersession was impossible?
7. What is the strongest honest outsider-facing sentence now?
8. What stronger sentence is still blocked, and by what missing coverage?

## Required answer states

The page must support at least:

- internal audience repaired only
- named links withdrawn only
- exports superseded but forwarded residue remains
- screenshots / quotes still active
- disclaimer applied without complete withdrawal
- named public surface repaired, broader public reach unproven
- later contradiction reopened public-claim risk

## Evidence discipline

For every answer, the review page must show:

- positive evidence
- contradictory evidence
- coverage gap
- sentence consequence

If any answer relies on inference rather than direct proof, that inference must be labeled and must cap the strongest sentence.

## Decision rail

The review must end with a forced choice among at least:

- only internal audience repair proven
- narrow public-surface repair proven
- named public surface repaired
- public-truth still blocked by circulating residue
- later contradiction reopened the question

## Comparison rail

The page must keep these pairs visibly separate:

- internal audience truth / public-claim truth
- future revocation / already-circulating artifact retirement
- withdrawal / disclaimer / supersession
- named public surface / broader public reach
- no contradiction seen / positive public-surface retirement proof

## Interaction requirements

The reviewer must be able to:

- click any unresolved public artifact and see why it remains unresolved
- open a surface coverage drawer that shows links, exports, forwards, screenshots, and quotes separately
- downgrade the strongest sentence in one gesture when any unresolved public carrier is marked active
- compare several candidate public-surface boundaries before locking the receipt sentence

## Hard rules

The page must never allow:

- the public surface boundary to remain implicit
- a revoked share to erase already-forwarded residue
- one repaired carrier class to hide other active carrier classes
- `probably no one still has it` to render as `public claim retired` without an explicit inference badge
""",
    '2107-remedy-hardening-attestation-public-claim-proof-page-representation-retirement-ledger-public-surface-coverage-and-claim-sentence-ceiling-interface-spec.md': """# Remedy-hardening-attestation public-claim proof page — representation-retirement ledger, public-surface coverage, and claim sentence ceiling

## Purpose

This page preserves the evidence needed to justify the strongest honest sentence about outsider-facing stale-public-claim retirement.
It is where the archive proves whether the correction repaired only an internal audience, a named public surface, or a broader outsider-facing representation set.

## Core sections

### 1. Public claim rail

Show:

- public surface identifier
- public surface boundary rule
- representation surface map version
- intended coverage threshold
- current strongest honest outsider-facing sentence

This rail must stay pinned while the operator scrolls.

### 2. Representation surface map

List links, landing pages, exported files, forwarded attachments, screenshots, quoted summaries, and embedded copies separately.
Each node must preserve:

- node identifier
- carrier class
- current retirement status (`withdrawn`, `superseded`, `disclaimed`, `likely retired`, `still active`, `unknown`)
- evidence source
- sentence effect

### 3. Retirement ledger

Each retirement row must preserve:

- retirement identifier
- public artifact or surface
- retirement carrier (`withdrawn`, `superseded`, `replaced with disclaimer`, `link expired`, `copy removed`, `other`)
- time retired or superseded
- proof source
- confidence class

### 4. Residual public-residue ledger

Each unresolved row must preserve:

- residue identifier
- public artifact or surface
- why stale public meaning remains possible
- last confirmed stale or unresolved time
- whether the residue is direct or downstream reshared
- whether it blocks the strongest public-truth sentence

### 5. Sentence ceiling panel

This panel must always show:

- strongest honest sentence now
- next stronger sentence blocked
- exact blockers
- whether the blocker is boundary ambiguity, carrier undercoverage, circulation residue, or evidence decay

## Visualization rules

The proof page must include:

- a public-surface coverage bar split into links, exports, forwards, screenshots, quotes, and embedded copies
- distinct visual treatment for `withdrawn`, `superseded`, `disclaimed`, `active stale`, and `unknown`
- an explicit count of unresolved public residues, not just percentage covered
- a marker whenever the page proves only named-public-surface repair rather than broader public truth

## Interaction requirements

The page must support:

- filtering the surface map by carrier class
- hovering over any uncovered public artifact to see why coverage is still missing
- expanding a residue row into the exact evidence bundle behind it
- exporting a narrow proof package for one named public surface without flattening carrier-class differences

## Hard rules

The page must never allow:

- one internal-audience receipt to satisfy a public-proof need
- link expiration to erase already-circulating public copies
- inferred carrier coverage to be styled like direct proof
- a stronger sentence to render unless every unresolved public residue has been named
""",
    '2108-remedy-hardening-attestation-public-claim-timeline-page-link-published-export-forwarded-public-copy-withdrawn-and-claim-horizon-closed-events-interface-spec.md': """# Remedy-hardening-attestation public-claim timeline page — link published, export forwarded, public copy withdrawn, and claim horizon closed events

## Purpose

This timeline shows how stale public meaning retires across outsider-facing representations rather than only inside the governed audience.
It exists so the operator can see when a representation was published, forwarded, superseded, disclaimed, or withdrawn, and when the named public surface could honestly be treated as repaired.

## Required event types

The timeline must support at least:

- correction published
- internal audience repaired
- share link generated
- link delivered externally
- landing page exposed
- export published
- export superseded
- forwarded attachment circulated
- screenshot or quote captured
- disclaimer published
- public copy withdrawn
- link expired
- future access revoked
- stale public residue discovered
- stale public residue retired
- public-claim horizon closed
- receipt superseded

## Interval semantics

This page must represent two different things at once:

- point events, such as `export superseded`
- state intervals, such as `stale link still reachable`, `forwarded residue still circulating`, or `named public surface repaired but broader public reach unresolved`

Intervals must not be collapsed into single dots.

## Required views

### Default chronological view

Show all events and intervals in order, with a pinned strongest honest outsider-facing sentence for the selected time.

### Carrier-class view

Group the timeline by links, exports, forwards, screenshots, quotes, and embedded copies so the operator can see where stale public meaning propagated and where it stopped.

### Closure view

Show only the evidence relevant to whether the public-claim horizon can honestly be closed as:

- internal audience repaired only
- narrow public-surface repair
- named public surface repaired
- broader public-truth sentence still blocked

## Interaction requirements

The timeline must support:

- scrubbing to any moment and seeing the strongest sentence that was honest at that time
- clicking any stale-public-residue interval to open the proof bundle behind it
- comparing two public-surface boundaries for the same correction without losing carrier labels
- collapsing internal-only events so outsider-facing retirement remains readable

## Hard rules

The timeline must never allow:

- `internal audience repaired` to occupy the same semantic lane as `named public surface repaired`
- a stale-public-residue interval to disappear merely because a later link expired
- `future access revoked` to overwrite `already-forwarded copy still circulating`
- a public-claim horizon to appear closed if the proof page still records unresolved public residue
""",
    '2109-remedy-hardening-attestation-public-claim-lineage-receipt-page-public-representation-summary-residual-misstatement-risk-and-blocked-stronger-truth-sentences-interface-spec.md': """# Remedy-hardening-attestation public-claim lineage receipt page — public representation summary, residual misstatement risk, and blocked stronger truth sentences

## Purpose

This receipt compresses the public-claim verdict into a portable record without flattening public-surface truth.
It exists so later readers can see whether the correction repaired only an internal audience, a named public surface, or the broader outsider-facing representation set.

## Minimum receipt fields

The receipt must show at least:

- receipt identifier
- public surface identifier
- source audience-reliance receipt identifier
- canonical correction identifier
- representation surface map version
- public surface boundary rule
- current public-surface coverage class
- unresolved stale-public-representation count
- strongest honest outsider-facing sentence
- blocked stronger public-truth sentence
- supersession state

## Required summary sentence

The receipt must render one sentence in plain language, such as:

- internal audience repaired; outsider-facing stale public claims remain possible
- named public links and exports superseded, but forwarded copies still block stronger public-truth sentence
- named public surface no longer misdescribes the correction; broader public rediscovery sentence remains blocked

The receipt must always preserve the blocked stronger sentence directly underneath.

## Required badges

Show compact badges for:

- internal-only / narrow public surface / named public surface repaired
- links / exports / forwards / screenshots / quotes / embedded copies
- public residue open / none seen / unresolved
- named-surface only / broader public blocked
- present-state surface map / decayed evidence warning

## Portable truth requirement

A reader opening only this receipt must still be able to tell:

- whether the result is internal-only or outsider-facing
- whether stale public residue remains
- which carrier classes were covered versus still unresolved
- whether the sentence is narrow to one named public surface
- whether a stronger broader-public sentence is still blocked

## Hard rules

The receipt must never allow:

- `internal audience repaired` to replace `public surface repaired`
- `link expired` to replace `forwarded copy retired`
- one covered carrier class to replace full public-surface coverage
- a named public-surface result to impersonate broader public truth
""",
}

prepend(base / 'README.md', README_ADD)
prepend(docs / '00-status.md', STATUS_ADD)
prepend(docs / '10-resilio-sync-evaluation.md', RESILIO_ADD)
prepend(docs / '20-product-direction.md', PRODUCT_ADD)
prepend(docs / 'sources.md', SOURCES_ADD)

for name, content in DOCS.items():
    (docs / name).write_text(content)
