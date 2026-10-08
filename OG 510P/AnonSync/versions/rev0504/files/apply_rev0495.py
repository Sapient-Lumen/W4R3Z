from pathlib import Path
from textwrap import dedent

base = Path(__file__).resolve().parent
docs = base / 'docs'

def prepend(path: Path, text: str) -> None:
    original = path.read_text()
    path.write_text(text + original)

README_ADD = dedent("""\
## Revision addendum after rev0494 — discoverability replacement and future resurfacing truth

This continuation archive advances the doctrine by tightening the next concrete seam after external representation retirement and public-claim truth:
**what happens after the operator withdrew, superseded, or disclaimed the named public artifacts, but before the product may honestly pretend that a latecomer who rediscovers the old thing will reliably land on the corrected replacement rather than the stale residue**.
It does eight things in one tranche:

1. Continues the archive after rev0494 with a new page family centered on whether the corrected representation became the thing that rediscovery surfaces actually return.
2. Tightens the non-clone line again: borrow Resilio's candor about landing-page behavior, local-only search, WebUI link-handling limits, local-only naming, and file-transfer residue; refuse any contract where the operator still has to reconstruct `if somebody finds the old thing later, will they be routed to the corrected replacement?` from scattered link, search, UI, and naming notes.
3. Adds one new **Resilio evaluation** document focused on why current discoverability replacement and future resurfacing truth is still too fragmented to clone even though the ingredients are useful.
4. Adds five new **interface specs** for discoverability contract sheet, review, proof, timeline, and lineage receipt.
5. Makes one hard product decision explicit: **external representation retirement is weaker than discoverability replacement and future resurfacing truth.**
6. Makes another hard product decision explicit: **withdrawing or superseding a stale artifact is weaker than making the corrected replacement the default late-arrival destination.**
7. Makes a third hard product decision explicit: **local search, local naming, or a manually-entered link path are not allowed to impersonate `outsiders who rediscover the stale thing will reliably find the corrected one`.**
8. Packages the result as another continuation archive whose new tranche makes the `rediscovery surface / canonical replacement pointer / late-arrival route / resurfacing horizon / strongest honest replacement-findability sentence / blocked stronger rediscovery-safe sentence` seam explicit in the reading order and page family.

New docs in this tranche:

- `2110-resilio-remedy-hardening-attestation-discoverability-replacement-and-future-resurfacing-truth-fragmentation-evaluation.md`
- `2111-remedy-hardening-attestation-discoverability-contract-sheet-page-canonical-replacement-surface-late-arrival-routing-and-resurfacing-ceiling-interface-spec.md`
- `2112-remedy-hardening-attestation-discoverability-review-page-if-someone-finds-the-old-thing-later-will-they-reliably-find-the-corrected-replacement-interface-spec.md`
- `2113-remedy-hardening-attestation-discoverability-proof-page-rediscovery-surface-map-replacement-routing-and-resurfacing-sentence-ceiling-interface-spec.md`
- `2114-remedy-hardening-attestation-discoverability-timeline-page-original-published-corrected-linked-deindexed-rediscovered-and-resurfacing-horizon-closed-events-interface-spec.md`
- `2115-remedy-hardening-attestation-discoverability-lineage-receipt-page-replacement-findability-summary-resurfacing-risk-and-blocked-stronger-truth-sentences-interface-spec.md`

""")

STATUS_ADD = dedent("""\
## rev0495 — discoverability replacement and future resurfacing truth ceiling

This tranche adds one more hard line to the doctrine:

- **external representation retirement is weaker than discoverability replacement and future resurfacing truth**
- **withdrawing or superseding the stale artifact is weaker than making the corrected replacement the default thing a latecomer finds**
- **public-surface cleanup, local searchability, and private operator legibility are different truths from outsider rediscovery safety**
- **search scope, landing-page behavior, canonical replacement pointers, and resurfacing channels must stay explicit instead of dissolving into `the public claim was repaired` folklore**

What this tranche contributes to the larger doctrine:

- `we withdrew the stale artifact` can no longer silently stand in for `late rediscovery now lands on the corrected replacement`
- `the link expires` can no longer silently stand in for `future resurfacing will be self-correcting`
- `the operator can still find the corrected item` can no longer silently stand in for `outsiders will find it when the stale thing resurfaces`
- `the stale thing is less visible in one surface` can no longer silently stand in for `replacement discoverability is now dominant across rediscovery surfaces`
- public-claim retirement can no longer silently stand in for future resurfacing truth

What remains intentionally true:

- governed-audience stale-dependency retirement still matters
- external representation retirement still matters
- disclaimer and supersession still matter
- local search and naming still matter
- but none of those may substitute for one explicit answer about whether later rediscovery of stale material now routes the outsider toward the corrected replacement or leaves stale meaning ambiently recoverable

New docs added in this tranche:

- `2110-resilio-remedy-hardening-attestation-discoverability-replacement-and-future-resurfacing-truth-fragmentation-evaluation.md`
- `2111-remedy-hardening-attestation-discoverability-contract-sheet-page-canonical-replacement-surface-late-arrival-routing-and-resurfacing-ceiling-interface-spec.md`
- `2112-remedy-hardening-attestation-discoverability-review-page-if-someone-finds-the-old-thing-later-will-they-reliably-find-the-corrected-replacement-interface-spec.md`
- `2113-remedy-hardening-attestation-discoverability-proof-page-rediscovery-surface-map-replacement-routing-and-resurfacing-sentence-ceiling-interface-spec.md`
- `2114-remedy-hardening-attestation-discoverability-timeline-page-original-published-corrected-linked-deindexed-rediscovered-and-resurfacing-horizon-closed-events-interface-spec.md`
- `2115-remedy-hardening-attestation-discoverability-lineage-receipt-page-replacement-findability-summary-resurfacing-risk-and-blocked-stronger-truth-sentences-interface-spec.md`

## Current frontier after rev0495 — outsider late-arrival trust and self-explaning supersession

The next seam after **public-claim repair and discoverability replacement** is now explicit:

- the archive can already say whether the beneficiary stayed switched
- it can now say whether the governed downstream audience retired stale dependencies
- it can now say whether named public representations were withdrawn, superseded, or left circulating
- it can now say whether late rediscovery has a named replacement route or still lands in stale residue
- it still needs to own the harder truth of **whether a late outsider who arrives through a stale artifact can understand and trust the supersession without operator-side context, private memory, or extra interpretation work**

This pass therefore makes the next possible step visible: **outsider late-arrival trust and self-explaining supersession**.

""")

RESILIO_ADD = dedent("""\
## Revision addendum after rev0494 — why discoverability replacement and future resurfacing truth now sit on the non-clone side

Current official Resilio docs are still admirably candid that `the stale public artifact was withdrawn`, `the corrected copy exists`, `the operator can search it locally`, `the share has a nicer display name`, and `a late outsider who rediscovers the old thing will reliably find the corrected replacement` are not one flat truth.
`Link structure and flow` still says folder links open through a Resilio landing page, that the page only shows basic folder information such as folder name and size, and that the hash parameters are not actually sent to Resilio's server.
`How do I perform a search in Sync?` still says search is a UI feature over folders and shared files, connected devices, and users, and on iOS it is only performed on the given subfolder level.
`Configuring WebUI` still says adding shares by clicking a link or placing the link into the browser address bar is not working with Sync using WebUI and requires manual entry through `Enter a key or link`.
`Setting custom name for sync shares` still says a custom name is applied only in Sync UI, does not rename the folder on disk, and does not propagate to other peers or devices linked with the identity, even though a generated link may embed a temporary share name.
`Sharing single file` still says file links can be made non-expiring, have no device or usage restriction, and recipients can share the files further.

This is strong rediscovery-surface candor.
It is also exactly why AnonSync should not clone the present contract.
One ordinary answer to `if somebody encounters the stale thing later, will they find the corrected replacement or just the stale residue again?` still depends on combining landing-page minimalism, local-only search scope, manual WebUI link entry, local-only naming, link-embedded names, non-expiring transfer links, and recipient resharing.

So this tranche freezes a stronger replacement line: **rediscovery surface, canonical replacement pointer, late-arrival route, resurfacing horizon, strongest honest replacement-findability sentence, and blocked stronger rediscovery-safe sentence must all become first-class and reviewable.**

""")

PRODUCT_ADD = dedent("""\
## Product-direction addendum after rev0494 — public-claim repair must graduate into explicit discoverability replacement

AnonSync should not let public-claim repair masquerade as late-arrival safety.
The product direction is now explicit:

- every correction flow that can leave stale artifacts discoverable later must also name the rediscovery surfaces that matter (`old links`, `landing pages`, `search surfaces`, `forwarded artifacts`, `screenshots`, `embedded references`, `quoted fragments`, `other`)
- every rediscovery surface must declare whether it points to the corrected replacement, merely disappears, or still routes the outsider back into stale residue
- a corrected copy that is easy for the operator to find must not silently count as a corrected replacement that outsiders will find
- the strongest sentence engine must preserve the difference between `public artifact retired`, `replacement exists`, and `late rediscovery preferentially finds the corrected replacement`
- the receipt family must stay portable enough that a later reader can tell whether stale resurfacing remains ambiently dangerous even when the original outward-facing artifact was withdrawn

That means future interface work should keep one stable family for:

- rediscovery surface boundary
- canonical replacement pointer class
- late-arrival route quality
- replacement coverage threshold
- residual resurfacing channel set
- strongest honest replacement-findability sentence ceiling

The product should never force the operator to infer those truths from a green review, a better file name in local UI, or the mere existence of a corrected export somewhere else.

""")

SOURCES_ADD = dedent("""\
## rev0495 source set — discoverability replacement and future resurfacing truth

The most load-bearing source set for this pass was:

- Resilio's current `Link structure and flow` article, which still says folder links open through a Resilio landing page that shows basic folder info such as folder name and size, and that the hash parameters are not actually sent to Resilio's server.
- Resilio's current `How do I perform a search in Sync?` article, which still says search is a UI feature over folders and shared files, connected devices, and users, and on iOS it is only performed on the given subfolder level.
- Resilio's current `Configuring WebUI` article, which still says adding shares by clicking a link or putting the link into the browser address bar is not working in Sync WebUI and instead requires manual entry via `Enter a key or link`.
- Resilio's current `Setting custom name for sync shares` article, which still says custom names apply only in the local Sync UI, do not rename the folder on disk, and do not propagate to other peers or linked devices, even though a generated share link may carry the inserted name.
- Resilio's current `Sharing single file` article, which still says file links may be made non-expiring, have no device or usage restriction, and allow recipients to share the files further.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for candid rediscovery ingredients
- but current Resilio still answers `if a stale thing resurfaces later, will the outsider reliably find the corrected replacement?` too diffusely
- AnonSync should therefore prefer explicit discoverability contract sheets, discoverability reviews, discoverability proofs, discoverability timelines, and durable discoverability lineage receipts over overloaded landing pages, local searches, local-only names, manual link-entry rules, and transfer-residue clues

Primary sources:

- Link structure and flow
  https://help.resilio.com/hc/en-us/articles/204754739-Link-structure-and-flow

- How do I perform a search in Sync?
  https://help.resilio.com/hc/en-us/articles/205457725-How-do-I-perform-a-search-in-Sync

- Configuring WebUI
  https://help.resilio.com/hc/en-us/articles/115001184490-Configuring-WebUI

- Setting custom name for sync shares
  https://help.resilio.com/hc/en-us/articles/360011865879-Setting-custom-name-for-sync-shares

- Sharing single file
  https://help.resilio.com/hc/en-us/articles/115000401010-Sharing-single-file

""")

DOCS = {
    '2110-resilio-remedy-hardening-attestation-discoverability-replacement-and-future-resurfacing-truth-fragmentation-evaluation.md': dedent("""\
    # Resilio remedy-hardening attestation discoverability replacement and future resurfacing truth fragmentation evaluation

    ## Why this seam matters now

    The archive can already say:

    - the beneficiary was legitimate
    - the beneficiary stayed on the canonical correction lane
    - the beneficiary noticed, acknowledged, adopted, and may have durably adhered to the corrected working state
    - the governed downstream audience may have retired stale dependencies for the named boundary
    - named public representations may have been withdrawn, superseded, or disclaimed

    That is still weaker than a harder question:

    **if somebody rediscovers the stale thing later, do they reliably find the corrected replacement, or does resurfacing still route them back into stale residue?**

    Public-claim repair is not automatically discoverability repair.
    Discoverability repair requires a rediscovery surface map, a canonical replacement pointer, a late-arrival route, and an explicit resurfacing horizon.
    Without those, `we corrected or withdrew the stale thing` quietly expands into folklore about outsiders now finding the right thing by default.

    ## Why current Resilio still leaves this too diffuse to clone

    Current official Resilio material is candid about several rediscovery and resurfacing ingredients, but it still spreads them across separate pages:

    - `Link structure and flow` says Sync links open through a Resilio landing page that shows basic folder information such as folder name and size, and that the hash parameters are not actually sent to Resilio's server
    - `How do I perform a search in Sync?` says search is a UI feature over folders, shared files, devices, and users, and on iOS it runs only at the current subfolder level
    - `Configuring WebUI` says clicking a link or placing it in the browser address bar does not add the share in Sync WebUI and requires manual entry instead
    - `Setting custom name for sync shares` says custom names are local to the Sync UI, do not rename the folder on disk, and do not propagate to other peers or linked devices, though a generated link can carry an inserted name
    - `Sharing single file` says file-transfer links can be made non-expiring, cannot restrict devices or usage count, and allow recipients to share the files further

    This is good operational candor.
    It is not yet one first-class answer to **if the stale thing resurfaces later, will the rediscovering outsider reach the corrected replacement or only another stale representation?**

    ## The non-clone line

    AnonSync should not clone a contract where all of these are allowed to blur together:

    - the stale artifact was withdrawn or superseded
    - a corrected replacement exists somewhere
    - the operator can still search it locally
    - one link landing page exists
    - WebUI can still accept a link via manual entry
    - the stale file-transfer link may remain non-expiring or be reshared
    - display names vary by local UI or by individual generated links
    - a later outsider therefore will reliably arrive at the corrected replacement

    Those are separate truths.

    ## Product decision frozen in this tranche

    This revision freezes a stronger line:

    - **external representation retirement is weaker than discoverability replacement and future resurfacing truth**
    - **withdrawing a stale artifact is weaker than giving late rediscovery a canonical route to the corrected replacement**
    - **local searchability, local naming, or manual WebUI recovery may never impersonate `late outsiders now reliably find the corrected replacement`**

    ## What AnonSync should model explicitly instead

    AnonSync should add one first-class family for:

    - source public-claim receipt identifier
    - rediscovery surface identifier
    - rediscovery surface boundary rule
    - canonical replacement pointer class
    - late-arrival route quality
    - replacement coverage threshold
    - residual resurfacing channel set
    - resurfacing horizon class
    - strongest honest replacement-findability sentence
    - blocked stronger rediscovery-safe sentence

    ## Interface consequence

    That is why this tranche adds five more first-class pages:

    - **discoverability contract sheet**
    - **discoverability review**
    - **discoverability proof**
    - **discoverability timeline**
    - **discoverability lineage receipt**
    """),
    '2111-remedy-hardening-attestation-discoverability-contract-sheet-page-canonical-replacement-surface-late-arrival-routing-and-resurfacing-ceiling-interface-spec.md': dedent("""\
    # Remedy-hardening-attestation discoverability contract sheet page — canonical replacement surface, late-arrival routing, and resurfacing ceiling

    ## Purpose

    This page is the operator-facing sheet for deciding whether a later outsider who rediscovers stale material will land on the corrected replacement or fall back into stale residue.
    It exists to stop `we withdrew the old thing`, `the corrected thing exists`, or `we can still find it locally` from being mistaken for `late rediscovery is now safe`.

    ## Core question

    The page must answer:

    **for this named rediscovery surface map, what is the strongest honest sentence about whether latecomers will find the corrected replacement rather than the stale thing?**

    ## Minimum fields

    The contract sheet must show at least:

    - action identifier
    - source public-claim receipt identifier
    - rediscovery surface identifier
    - rediscovery surface boundary rule
    - canonical correction identifier
    - canonical replacement pointer class (`redirect`, `supersession banner`, `replacement landing page`, `signed replacement receipt`, `manual explanation only`, `none`)
    - in-scope rediscovery surfaces (`old links`, `landing pages`, `search surfaces`, `forwarded artifacts`, `screenshots`, `embedded references`, `quoted fragments`, `other`)
    - late-arrival route quality
    - intended replacement coverage threshold
    - current replacement coverage threshold
    - unresolved resurfacing channel count
    - highest-risk resurfacing channel
    - strongest honest replacement-findability sentence now
    - blocked stronger rediscovery-safe sentence now

    ## Standing ladder

    The page must support at least these distinct standings:

    - stale artifact retired only
    - corrected replacement exists but rediscovery route unproven
    - some surfaces route to replacement, others still surface stale residue
    - redirect or pointer exists for one surface only
    - late-arrival route still needs operator context
    - named rediscovery surfaces now prefer corrected replacement
    - broader rediscovery safety still blocked
    - later contradiction reopened resurfacing risk
    - receipt superseded

    ## Required comparisons

    The sheet must compare:

    - public-claim repair versus discoverability replacement
    - stale artifact withdrawal versus canonical replacement routing
    - operator-local findability versus outsider late-arrival findability
    - surface-specific replacement success versus broader rediscovery safety
    - current best sentence versus blocked stronger rediscovery-safe sentence

    ## Required layout

    ### Header

    Show:

    - correction name
    - rediscovery surface-map name
    - current discoverability standing
    - strongest honest replacement-findability sentence now

    ### Left column — intended replacement contract

    Show:

    - rediscovery surface boundary rule
    - in-scope resurfacing channels
    - required canonical replacement pointer class
    - required late-arrival route quality
    - required replacement coverage threshold

    ### Center column — observed resurfacing facts

    Show:

    - old-link route status
    - landing-page replacement status
    - search-surface replacement status
    - forwarded-artifact pointer status
    - screenshot / quote disclaimer status
    - embedded-reference update status
    - evidence freshness for rediscovery map

    Every row in this column must have:

    - current value
    - evidence source
    - whether it strengthens or weakens rediscovery safety

    ### Right column — consequence for truth

    Show:

    - whether only artifact retirement is proven
    - whether replacement exists without safe rediscovery
    - whether named surfaces now route to the corrected replacement
    - whether broader resurfacing safety is still blocked
    - what stronger sentence remains blocked

    ### Footer decision rail

    The footer must make it impossible to flatten these into one answer:

    - stale artifact retired only
    - corrected replacement exists only
    - some surfaces route correctly
    - named rediscovery map is replacement-safe
    - broader rediscovery-safe sentence still blocked

    ## Interaction requirements

    The interface must support:

    - clicking any rediscovery-surface chip to open route quality, pointer class, evidence age, and exclusions
    - pinning one surface while comparing several replacement thresholds
    - filtering the surface map to links, landing pages, search surfaces, forwards, screenshots, quotes, or embedded references
    - opening the blocked stronger sentence and seeing exactly which unresolved resurfacing channels keep it blocked

    ## Hard rules

    The page must never allow:

    - public-claim retirement to silently become discoverability replacement
    - local operator findability to silently become outsider findability
    - one redirect to silently become full resurfacing safety
    - a named-surface result to silently become broader rediscovery safety
    """),
    '2112-remedy-hardening-attestation-discoverability-review-page-if-someone-finds-the-old-thing-later-will-they-reliably-find-the-corrected-replacement-interface-spec.md': dedent("""\
    # Remedy-hardening-attestation discoverability review page — if someone finds the old thing later, will they reliably find the corrected replacement?

    ## Purpose

    This page is the forced-review surface for deciding whether late rediscovery is safe.
    It exists to stop the operator from exiting with a comforting story about withdrawal or supersession while stale artifacts still resurface without a reliable route to the corrected replacement.

    ## Opening question

    The page must ask, in plain language:

    **if someone finds the old thing later, will they reliably find the corrected replacement, or are they still likely to fall back into stale residue?**

    ## Required reviewer prompts

    The reviewer must answer at least:

    1. What is the exact rediscovery surface boundary?
    2. Which surfaces positively point to the corrected replacement?
    3. Which surfaces merely hide the stale artifact without offering a replacement route?
    4. Which surfaces still require operator-side context or manual interpretation?
    5. Which stale artifacts remain ambiently rediscoverable?
    6. Is the replacement route durable across time, or only true right now?
    7. What is the strongest honest replacement-findability sentence now?
    8. What stronger sentence is still blocked, and by which unresolved resurfacing channels?

    ## Required answer states

    The page must support at least:

    - stale artifact retired only
    - replacement exists but not discoverably routed
    - one surface routes correctly, others still stale
    - search replacement still blocked
    - forwarded or embedded residue still resurfaces stale meaning
    - named rediscovery map routes to replacement
    - broader rediscovery safety unproven
    - later contradiction reopened resurfacing risk

    ## Evidence discipline

    For every answer, the review page must show:

    - positive evidence
    - contradictory evidence
    - coverage gap
    - sentence consequence

    If any answer relies on inference rather than direct proof, that inference must be labeled and must cap the strongest sentence.

    ## Decision rail

    The review must end with a forced choice among at least:

    - only artifact retirement proven
    - replacement exists but late-arrival route unproven
    - narrow rediscovery route proven
    - named rediscovery map replacement-safe
    - broader rediscovery-safe sentence still blocked
    - later contradiction reopened the question

    ## Comparison rail

    The page must keep these pairs visibly separate:

    - artifact retirement / replacement routing
    - operator-local findability / outsider findability
    - disappearance / supersession / redirect
    - named rediscovery surface / broader resurfacing horizon
    - no contradiction seen / positive rediscovery-safe proof

    ## Interaction requirements

    The reviewer must be able to:

    - click any unresolved resurfacing channel and see exactly why it remains unresolved
    - open a route-quality drawer that shows links, landing pages, search surfaces, forwards, screenshots, and embedded references separately
    - downgrade the strongest sentence in one gesture when any unresolved rediscovery surface is marked active
    - compare several candidate rediscovery boundaries before locking the receipt sentence

    ## Hard rules

    The page must never allow:

    - the rediscovery boundary to remain implicit
    - `the old thing is harder to find` to render as `latecomers will find the corrected one`
    - one repaired surface to hide other active rediscovery surfaces
    - `someone could ask us if confused` to render as `discoverability replaced` without an explicit inference badge
    """),
    '2113-remedy-hardening-attestation-discoverability-proof-page-rediscovery-surface-map-replacement-routing-and-resurfacing-sentence-ceiling-interface-spec.md': dedent("""\
    # Remedy-hardening-attestation discoverability proof page — rediscovery surface map, replacement routing, and resurfacing sentence ceiling

    ## Purpose

    This page is the evidence-heavy surface for proving what a later rediscovering outsider is most likely to encounter.
    It exists to preserve the exact route quality, residual resurfacing channels, and blocked stronger sentence instead of collapsing everything into a vague `we replaced it` claim.

    ## Core proof question

    The page must answer:

    **what is the strongest evidence-backed sentence we can honestly make about late rediscovery now, and what stronger rediscovery-safe sentence is still blocked?**

    ## Minimum evidence sections

    The proof page must contain:

    - receipt header
    - rediscovery surface map
    - canonical replacement pointer ledger
    - late-arrival route-quality ledger
    - residual resurfacing channel ledger
    - contradiction and drift ledger
    - strongest honest sentence / blocked stronger sentence panel

    ## Receipt header

    The header must show:

    - action identifier
    - source public-claim receipt identifier
    - rediscovery surface identifier
    - canonical correction identifier
    - proof freshness timestamp
    - current discoverability standing

    ## Rediscovery surface map

    For each in-scope surface show:

    - surface class
    - stale artifact identifier
    - replacement pointer class
    - outsider-visible route now
    - route evidence age
    - exclusions

    The surface map must make it impossible to merge `surface removed`, `surface superseded`, and `surface redirects to corrected replacement`.

    ## Replacement pointer ledger

    For each pointer show:

    - pointer class
    - who controls it
    - whether it is durable or ephemeral
    - whether it is visible without operator-side explanation
    - whether it survives ordinary resurfacing conditions

    ## Route-quality ledger

    The proof must preserve at least these distinct route states:

    - no route shown
    - replacement exists elsewhere
    - manual explanation required
    - disclaimer only
    - redirect or explicit supersession pointer shown
    - named surface replacement-safe
    - broader rediscovery-safe sentence blocked

    ## Resurfacing channel ledger

    Track at least:

    - old links still circulating
    - landing pages without replacement pointer
    - search surfaces without replacement preference
    - forwarded artifacts without correction banner
    - screenshots / quotes lacking supersession context
    - embedded references pointing to stale copies

    Every unresolved resurfacing channel must carry:

    - why it remains open
    - how likely late arrival is
    - what sentence it blocks

    ## Contradiction and drift ledger

    The page must preserve:

    - later rediscovery contradiction
    - route decay
    - renamed or moved replacement without updated pointer
    - stale artifact reappearance
    - scope expansion that reopens blocked channels

    ## Sentence panel

    The sentence panel must show:

    - strongest honest replacement-findability sentence now
    - strongest blocked stronger rediscovery-safe sentence now
    - exact blockers for the stronger sentence
    - whether the current sentence rests on direct proof or inference

    ## Hard rules

    The page must never allow:

    - proof of artifact retirement to substitute for proof of replacement routing
    - local operator search success to substitute for outsider rediscovery success
    - one good pointer to erase unresolved resurfacing elsewhere
    - a direct-proof sentence and an inference-backed sentence to render as equivalent
    """),
    '2114-remedy-hardening-attestation-discoverability-timeline-page-original-published-corrected-linked-deindexed-rediscovered-and-resurfacing-horizon-closed-events-interface-spec.md': dedent("""\
    # Remedy-hardening-attestation discoverability timeline page — original published, corrected, linked, deindexed, rediscovered, and resurfacing horizon closed events

    ## Purpose

    This page is the chronological surface for showing how late rediscovery safety evolved over time.
    It exists to stop the archive from flattening `we corrected it eventually` into `a late rediscovery was safe at every meaningful moment`.

    ## Core question

    The timeline must answer:

    **across the rediscovery horizon, when did stale material remain discoverable, when did replacement routing begin, and when did any later resurfacing reopen the risk?**

    ## Required event classes

    The timeline must support at least:

    - original published
    - stale artifact forwarded or embedded
    - correction published
    - replacement pointer added
    - stale artifact withdrawn
    - stale artifact deindexed or made harder to reach
    - rediscovery test passed
    - rediscovery contradiction observed
    - resurfacing channel reopened
    - resurfacing horizon closed
    - receipt superseded

    ## Required lanes

    The page must show at least these lanes:

    - source publication lane
    - correction and replacement lane
    - rediscovery surface lane
    - residual resurfacing lane
    - sentence-ceiling lane

    ## Per-event payload

    Every event must preserve:

    - event timestamp
    - actor or subsystem
    - affected rediscovery surface
    - route consequence
    - evidence source
    - sentence consequence

    ## Visual rules

    The timeline must make these differences obvious:

    - correction published versus replacement pointer added
    - stale artifact withdrawn versus stale artifact still discoverable through forwarding or embedding
    - deindexed versus redirected
    - one rediscovery test passed versus horizon-wide rediscovery safety proved
    - contradiction absent so far versus contradiction positively checked

    ## Required overlays

    The interface must support overlays for:

    - route-quality changes
    - resurfacing channel count over time
    - strongest honest sentence changes
    - blocked stronger sentence changes

    ## Hard rules

    The page must never allow:

    - a correction-publication event to silently stand in for replacement routing
    - a deindex event to silently stand in for outsider-safe redirect
    - one passed rediscovery check to silently stand in for full resurfacing-horizon safety
    - a quiet period to silently stand in for future resurfacing closure
    """),
    '2115-remedy-hardening-attestation-discoverability-lineage-receipt-page-replacement-findability-summary-resurfacing-risk-and-blocked-stronger-truth-sentences-interface-spec.md': dedent("""\
    # Remedy-hardening-attestation discoverability lineage receipt page — replacement findability summary, resurfacing risk, and blocked stronger truth sentences

    ## Purpose

    This page is the portable receipt for carrying the discoverability verdict into later review, audit, or dispute contexts.
    It exists so that a later reader can tell, without reopening the whole proof stack, whether rediscovery now tends to route outsiders to the corrected replacement or still leaves stale resurfacing risk alive.

    ## Core output

    The receipt must answer:

    **what is the strongest honest sentence we can carry forward about replacement findability for late rediscovery, and what stronger rediscovery-safe sentence remains blocked?**

    ## Required header fields

    Show at least:

    - receipt identifier
    - action identifier
    - source public-claim receipt identifier
    - rediscovery surface identifier
    - canonical correction identifier
    - proof freshness timestamp
    - current discoverability standing

    ## Mandatory summary block

    The summary block must include:

    - in-scope rediscovery surfaces
    - canonical replacement pointer class
    - current late-arrival route quality
    - replacement coverage threshold achieved
    - unresolved resurfacing channel count
    - highest-risk unresolved resurfacing channel
    - strongest honest replacement-findability sentence
    - blocked stronger rediscovery-safe sentence

    ## Mandatory sentence ladder

    The receipt must preserve at least these separations:

    - stale artifact retired only
    - corrected replacement exists only
    - some rediscovery surfaces route correctly
    - named rediscovery map replacement-safe
    - broader rediscovery-safe sentence blocked
    - later contradiction reopened resurfacing risk

    ## Mandatory blocker block

    For every blocked stronger sentence show:

    - blocker name
    - blocker class
    - affected surface
    - whether the blocker is direct contradiction or missing coverage
    - what stronger sentence it prevents

    ## Mandatory provenance block

    The receipt must preserve:

    - who assembled the rediscovery map
    - what evidence sources were used
    - which route claims are direct proof
    - which route claims are inference only
    - when the resurfacing horizon is considered to end

    ## Interaction requirements

    The receipt must support:

    - expanding any unresolved resurfacing channel into full proof detail
    - opening the rediscovery map from the summary chip
    - comparing this receipt against the earlier public-claim receipt without losing sentence distinctions
    - exporting a compact version that still keeps the blocked stronger sentence visible

    ## Hard rules

    The receipt must never allow:

    - `replacement exists` to render as `replacement is what latecomers will find`
    - `one route is safe` to erase unresolved routes elsewhere
    - `no contradiction yet` to render as `future resurfacing closed`
    - the blocked stronger sentence to disappear from exported or compact views
    """)
}

prepend(base / 'README.md', README_ADD)
prepend(docs / '00-status.md', STATUS_ADD)
prepend(docs / '10-resilio-sync-evaluation.md', RESILIO_ADD)
prepend(docs / '20-product-direction.md', PRODUCT_ADD)
prepend(docs / 'sources.md', SOURCES_ADD)

for name, content in DOCS.items():
    (docs / name).write_text(content)

print('rev0495 content written')
