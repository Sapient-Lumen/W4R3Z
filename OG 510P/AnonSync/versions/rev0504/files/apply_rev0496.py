from pathlib import Path
from textwrap import dedent

base = Path(__file__).resolve().parent
docs = base / 'docs'


def prepend(path: Path, text: str) -> None:
    original = path.read_text()
    path.write_text(text + original)


README_ADD = dedent("""\
## Revision addendum after rev0495 — outsider late-arrival trust and self-explaining supersession

This continuation archive advances the doctrine by tightening the next concrete seam after discoverability replacement and future resurfacing truth:
**what happens after a late outsider can be routed to the corrected replacement, but before the product may honestly pretend that the replacement itself explains why it supersedes the stale thing and why that supersession should be trusted without operator-side context, private memory, or hidden approval history**.
It does eight things in one tranche:

1. Continues the archive after rev0495 with a new page family centered on whether a late outsider who reaches the corrected thing can understand and verify why it is the legitimate successor.
2. Tightens the non-clone line again: borrow Resilio's candor about PKI, X.509 certificates, identity fingerprints, owner-only sharing on Advanced folders, approval details, and local-only naming; refuse any contract where the operator still has to reconstruct `will a late outsider know why this replacement should be trusted as the canonical successor?` from scattered identity, sharing, approval, landing-page, and UI-name notes.
3. Adds one new **Resilio evaluation** document focused on why current outsider late-arrival trust and self-explaining supersession are still too fragmented to clone even though the ingredients are useful.
4. Adds five new **interface specs** for supersession-trust contract sheet, review, proof, timeline, and lineage receipt.
5. Makes one hard product decision explicit: **discoverability replacement is weaker than outsider late-arrival trust and self-explaining supersession.**
6. Makes another hard product decision explicit: **routing a late outsider to the corrected replacement is weaker than the replacement carrying its own intelligible supersession explanation and authority proof.**
7. Makes a third hard product decision explicit: **operator-side fingerprints, remembered approvals, or local UI names are not allowed to impersonate `a late outsider can see why this is the legitimate successor`.**
8. Packages the result as another continuation archive whose new tranche makes the `superseded artifact / successor proof class / explanation carrier / outsider-verifiable trust class / strongest honest trust sentence / blocked stronger self-explaining sentence` seam explicit in the reading order and page family.

New docs in this tranche:

- `2116-resilio-remedy-hardening-attestation-outsider-late-arrival-trust-and-self-explaining-supersession-fragmentation-evaluation.md`
- `2117-remedy-hardening-attestation-supersession-trust-contract-sheet-page-outsider-verifiable-successor-proof-and-explanation-ceiling-interface-spec.md`
- `2118-remedy-hardening-attestation-supersession-trust-review-page-if-a-late-outsider-finds-the-corrected-thing-will-they-know-why-to-trust-it-interface-spec.md`
- `2119-remedy-hardening-attestation-supersession-trust-proof-page-successor-evidence-explanation-carrier-and-trust-sentence-ceiling-interface-spec.md`
- `2120-remedy-hardening-attestation-supersession-trust-timeline-page-stale-published-corrected-routed-explained-verified-and-trust-horizon-closed-events-interface-spec.md`
- `2121-remedy-hardening-attestation-supersession-trust-lineage-receipt-page-outsider-trust-summary-self-explaining-supersession-and-blocked-stronger-truth-sentences-interface-spec.md`

""")

STATUS_ADD = dedent("""\
## rev0496 — outsider late-arrival trust and self-explaining supersession ceiling

This tranche adds one more hard line to the doctrine:

- **discoverability replacement is weaker than outsider late-arrival trust and self-explaining supersession**
- **routing the outsider to the corrected thing is weaker than letting the corrected thing explain, on its own surface, what it supersedes and why to trust that claim**
- **private approval lore, remembered peer history, and operator-local identity context are different truths from outsider-visible successor trust**
- **successor proof class, explanation carrier, authority source, and outsider-verifiable trust must stay explicit instead of dissolving into `they found the right thing` folklore**

What this tranche contributes to the larger doctrine:

- `the late outsider can reach the corrected replacement` can no longer silently stand in for `the corrected replacement explains why it is authoritative`
- `the operator can inspect the requester fingerprint` can no longer silently stand in for `the outsider can verify the supersession from the surface they see`
- `the system remembers previously approved peers` can no longer silently stand in for `the late outsider understands why to trust this successor now`
- `the replacement has a better name in one UI` can no longer silently stand in for `the successor relation is self-explaining across outsider-facing surfaces`
- discoverability replacement can no longer silently stand in for outsider trustable supersession

What remains intentionally true:

- beneficiary and audience repair still matter
- public-claim retirement still matters
- discoverability replacement still matters
- operator-side identity and approval evidence still matters
- but none of those may substitute for one explicit answer about whether a late outsider who reaches the corrected thing can tell what it supersedes, who authorizes that supersession, and how strong the trust claim honestly is

New docs added in this tranche:

- `2116-resilio-remedy-hardening-attestation-outsider-late-arrival-trust-and-self-explaining-supersession-fragmentation-evaluation.md`
- `2117-remedy-hardening-attestation-supersession-trust-contract-sheet-page-outsider-verifiable-successor-proof-and-explanation-ceiling-interface-spec.md`
- `2118-remedy-hardening-attestation-supersession-trust-review-page-if-a-late-outsider-finds-the-corrected-thing-will-they-know-why-to-trust-it-interface-spec.md`
- `2119-remedy-hardening-attestation-supersession-trust-proof-page-successor-evidence-explanation-carrier-and-trust-sentence-ceiling-interface-spec.md`
- `2120-remedy-hardening-attestation-supersession-trust-timeline-page-stale-published-corrected-routed-explained-verified-and-trust-horizon-closed-events-interface-spec.md`
- `2121-remedy-hardening-attestation-supersession-trust-lineage-receipt-page-outsider-trust-summary-self-explaining-supersession-and-blocked-stronger-truth-sentences-interface-spec.md`

## Current frontier after rev0496 — outsider actionable reliance and operator-free remediation

The next seam after **discoverability replacement and outsider-trustable supersession** is now explicit:

- the archive can already say whether the beneficiary stayed switched
- it can now say whether the governed downstream audience retired stale dependencies
- it can now say whether named public representations were withdrawn, superseded, or left circulating
- it can now say whether late rediscovery has a named replacement route or still lands in stale residue
- it can now say whether the corrected replacement itself explains why it supersedes the stale thing and how strong that trust claim really is
- it still needs to own the harder truth of **whether a late outsider can safely act from that explanation without operator intervention, private follow-up, or hidden procedural knowledge**

This pass therefore makes the next possible step visible: **outsider actionable reliance and operator-free remediation**.

""")

RESILIO_ADD = dedent("""\
## Revision addendum after rev0495 — why outsider late-arrival trust and self-explaining supersession now sit on the non-clone side

Current official Resilio docs are still admirably candid that `the corrected replacement exists`, `a late outsider can be routed to it`, `the operator can verify a peer identity`, and `the replacement itself explains why it should be trusted as the canonical successor` are not one flat truth.
`What's the difference between Standard and Advanced folders?` still says Advanced folders are PKI-based, all connection operations are carried out with X.509 digital certificates, only Owners can share Advanced folders onward, and Advanced folders remember certificates of previously dealt-with users.
`Sync Private Identity & Linking My Devices` still says each Sync installation gets a unique digital certificate and fingerprint, and once a remote user approves a connection they can choose to automatically approve that identity on all linked devices for future sharing.
`Comprehensive guide to syncing (Desktop-Desktop)` still says the approving operator can click the requester's identity and review the person's name, IP address, fingerprint, and approval-request receipt date.
`Link structure and flow` still says the public landing page shows only basic folder information, while the actual fingerprint comparison, approval, certificate issuance, and ACL signing happen in the app-level flow after the request reaches the owner.
`Setting custom name for sync shares` still says custom names are local to Sync UI, do not rename the folder on disk, and do not propagate to other peers or linked devices, even though a generated link may carry a temporarily inserted name.

This is strong trust-ingredient candor.
It is also exactly why AnonSync should not clone the present contract.
One ordinary answer to `if a late outsider reaches the corrected replacement, will they know from that surface itself why it is the legitimate successor?` still depends on combining PKI notes, owner semantics, remembered approvals, private fingerprint review, landing-page minimalism, and local-only naming scattered across separate pages.

So this tranche freezes a stronger replacement line: **superseded artifact identifier, successor proof class, explanation carrier, outsider-verifiable trust class, strongest honest trust sentence, and blocked stronger self-explaining sentence must all become first-class and reviewable.**

""")

PRODUCT_ADD = dedent("""\
## Product-direction addendum after rev0495 — discoverability replacement must graduate into explicit outsider-trustable supersession

AnonSync should not let successful routing masquerade as trustworthy supersession.
The product direction is now explicit:

- every correction flow that can route late outsiders to a replacement must also name what the replacement says, on its own surface, about the stale thing it supersedes
- every trust-bearing surface must declare the successor proof class that backs the supersession claim (`signed supersession receipt`, `same-surface supersession banner`, `linked authority receipt`, `operator note only`, `none`)
- a replacement that the operator can privately explain must not silently count as a replacement that explains itself to a late outsider
- the strongest sentence engine must preserve the difference between `replacement found`, `replacement explained`, and `replacement explained with outsider-verifiable authority`
- the receipt family must stay portable enough that a later reader can tell whether trust rests on direct surface evidence, indirect operator context, or inference only

That means future interface work should keep one stable family for:

- superseded artifact identifier
- successor proof class
- explanation carrier set
- authority source
- outsider-verifiable trust class
- strongest honest trust sentence ceiling

The product should never force the operator to infer those truths from a remembered approval, a peer fingerprint drawer, a local custom name, or the mere fact that the corrected thing was reachable.

""")

SOURCES_ADD = dedent("""\
## rev0496 source set — outsider late-arrival trust and self-explaining supersession

The most load-bearing source set for this pass was:

- Resilio's current `What's the difference between Standard and Advanced folders?` article, which still says Advanced folders are based on PKI, connection operations use X.509 digital certificates, only Owners can share Advanced folders onward, and Advanced folders remember certificates of previously dealt-with users.
- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says each Sync installation gets a unique digital certificate and fingerprint, and a remote user can choose to automatically approve that identity on all linked devices for future sharing.
- Resilio's current `Comprehensive guide to syncing (Desktop-Desktop)` article, which still says the approving operator can inspect the requester's name, IP address, fingerprint, and approval request receipt date.
- Resilio's current `Link structure and flow` article, which still says the public landing page shows only basic folder information, while the fingerprint comparison, approval, certificate issuance, and ACL signing happen in the app-level approval flow.
- Resilio's current `Setting custom name for sync shares` article, which still says custom names are local to Sync UI, do not rename the folder on disk, and do not propagate to other peers or linked devices, even though a generated link may carry an inserted name.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for candid trust ingredients
- but current Resilio still answers `if a late outsider reaches the corrected replacement, will they know why to trust it as the legitimate successor without operator-side context?` too diffusely
- AnonSync should therefore prefer explicit supersession-trust contract sheets, supersession-trust reviews, supersession-trust proofs, supersession-trust timelines, and durable supersession-trust lineage receipts over overloaded PKI lore, approval dialogs, fingerprint drawers, landing-page minimalism, and local-only naming clues

Primary sources:

- What's the difference between Standard and Advanced folders?
  https://help.resilio.com/hc/en-us/articles/204754679-What-s-the-difference-between-Standard-and-Advanced-folders

- Sync Private Identity & Linking My Devices
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Comprehensive guide to syncing (Desktop-Desktop)
  https://help.resilio.com/hc/en-us/articles/204754939-Comprehensive-guide-to-syncing-Desktop-Desktop

- Link structure and flow
  https://help.resilio.com/hc/en-us/articles/204754739-Link-structure-and-flow

- Setting custom name for sync shares
  https://help.resilio.com/hc/en-us/articles/360011865879-Setting-custom-name-for-sync-shares

""")

DOCS = {
    '2116-resilio-remedy-hardening-attestation-outsider-late-arrival-trust-and-self-explaining-supersession-fragmentation-evaluation.md': dedent("""\
    # Resilio remedy-hardening attestation outsider late-arrival trust and self-explaining supersession fragmentation evaluation

    ## Why this seam matters now

    The archive can already say:

    - the beneficiary was legitimate
    - the beneficiary stayed on the canonical correction lane
    - the beneficiary noticed, acknowledged, adopted, and may have durably adhered to the corrected working state
    - the governed downstream audience may have retired stale dependencies for the named boundary
    - named public representations may have been withdrawn, superseded, or disclaimed
    - late rediscovery may now route a late outsider toward the corrected replacement instead of stale residue

    That is still weaker than a harder question:

    **if the late outsider does reach the corrected replacement, can they tell from that surface itself what it supersedes, who authorizes that supersession, and how much trust that claim honestly deserves?**

    Discoverability is not yet trust.
    A good route is weaker than a self-explaining successor.
    Without explicit successor proof and explanation, `they found the corrected thing` quietly expands into folklore about `they will also know why to trust it`.

    ## Why current Resilio still leaves this too diffuse to clone

    Current official Resilio material is candid about several trust ingredients, but it still spreads them across separate pages:

    - `What's the difference between Standard and Advanced folders?` says Advanced folders are based on PKI, all connection operations use X.509 certificates, only Owners can share Advanced folders onward, and Advanced folders remember certificates of previously dealt-with users
    - `Sync Private Identity & Linking My Devices` says each Sync installation has a unique digital certificate and fingerprint, and a remote user can choose to auto-approve that identity on all linked devices in future
    - `Comprehensive guide to syncing (Desktop-Desktop)` says the approving operator can inspect a requester's name, IP address, fingerprint, and approval-request receipt date before approving
    - `Link structure and flow` says the public landing page only shows basic folder information, while fingerprint comparison, approval, certificate issuance, and ACL signing happen inside the app-level approval path
    - `Setting custom name for sync shares` says custom names are local to one Sync UI and do not propagate, even though generated links may carry an inserted name

    This is good operational candor.
    It is not yet one first-class answer to **if a late outsider reaches the corrected replacement, will the surface itself explain why this is the legitimate successor, or does trust still depend on private operator context and prior approval history?**

    ## The non-clone line

    AnonSync should not clone a contract where all of these are allowed to blur together:

    - a corrected replacement is reachable
    - the operator can verify peer fingerprints in an approval flow
    - the system remembers previously trusted identities
    - only Owners can share Advanced folders onward
    - the public landing page shows some folder information
    - one link may carry a nicer inserted name
    - a late outsider therefore understands and trusts the supersession claim

    Those are separate truths.

    ## Product decision frozen in this tranche

    This revision freezes a stronger line:

    - **discoverability replacement is weaker than outsider late-arrival trust and self-explaining supersession**
    - **routing an outsider to the corrected replacement is weaker than the replacement carrying its own intelligible supersession explanation and authority proof**
    - **private approval evidence, remembered peer history, or local UI naming may never impersonate `the late outsider can see why this is the legitimate successor`**

    ## What AnonSync should model explicitly instead

    AnonSync should add one first-class family for:

    - superseded artifact identifier
    - corrected replacement identifier
    - successor proof class
    - explanation carrier set
    - authority source class
    - outsider-verifiable trust class
    - residual trust blocker set
    - trust horizon class
    - strongest honest trust sentence
    - blocked stronger self-explaining sentence

    ## Interface consequence

    That is why this tranche adds five more first-class pages:

    - **supersession-trust contract sheet**
    - **supersession-trust review**
    - **supersession-trust proof**
    - **supersession-trust timeline**
    - **supersession-trust lineage receipt**
    """),
    '2117-remedy-hardening-attestation-supersession-trust-contract-sheet-page-outsider-verifiable-successor-proof-and-explanation-ceiling-interface-spec.md': dedent("""\
    # Remedy-hardening-attestation supersession-trust contract sheet page — outsider-verifiable successor proof and explanation ceiling

    ## Purpose

    This page is the operator-facing sheet for deciding whether a late outsider who reaches the corrected replacement can tell, from that surface itself, what it supersedes and why to trust the supersession claim.
    It exists to stop `they found the corrected thing` from being mistaken for `they can understand and trust why it is the right thing`.

    ## Core question

    The page must answer:

    **for this named outsider-facing surface, what is the strongest honest sentence about whether the corrected replacement is self-explaining and trustable as the legitimate successor?**

    ## Minimum fields

    The contract sheet must show at least:

    - action identifier
    - stale artifact identifier
    - corrected replacement identifier
    - outsider-facing surface identifier
    - canonical correction identifier
    - successor proof class (`signed supersession receipt`, `same-surface supersession banner`, `linked authority receipt`, `operator note only`, `none`)
    - explanation carrier set (`replacement header`, `adjacent banner`, `landing-page notice`, `embedded watermark`, `linked receipt`, `manual explanation only`, `none`)
    - authority source class (`same authority as stale artifact`, `delegated authority`, `replacement-only authority`, `unclear`, `none`)
    - outsider-verifiable trust class
    - intended trust coverage threshold
    - current trust coverage threshold
    - unresolved trust blocker count
    - highest-risk unresolved trust blocker
    - strongest honest trust sentence now
    - blocked stronger self-explaining sentence now

    ## Standing ladder

    The page must support at least these distinct standings:

    - corrected replacement exists only
    - corrected replacement is reachable but trust is unexplained
    - supersession is claimed but authority remains opaque
    - explanation exists but only with operator-side context
    - named surface carries a self-explaining supersession claim
    - named surface carries outsider-verifiable supersession proof
    - broader outsider-trust sentence still blocked
    - later contradiction reopened trust risk
    - receipt superseded

    ## Required comparisons

    The sheet must compare:

    - replacement routed versus replacement explained
    - explanation shown versus authority proved
    - operator-verifiable trust versus outsider-verifiable trust
    - one named surface proof versus broader outsider-trust coverage
    - current best sentence versus blocked stronger self-explaining sentence

    ## Required layout

    ### Header

    Show:

    - correction name
    - stale artifact name
    - corrected replacement name
    - current supersession-trust standing
    - strongest honest trust sentence now

    ### Left column — intended trust contract

    Show:

    - required successor proof class
    - required explanation carrier set
    - required authority source class
    - required outsider-verifiable trust class
    - required trust coverage threshold

    ### Center column — observed trust facts

    Show:

    - visible supersession statement now
    - visible authority statement now
    - visible stale-artifact reference now
    - linked receipt or proof availability
    - local-only naming dependence
    - operator-context dependence
    - evidence freshness for trust surface

    Every row in this column must have:

    - current value
    - evidence source
    - whether it strengthens or weakens outsider trust

    ### Right column — consequence for truth

    Show:

    - whether only replacement reachability is proven
    - whether explanation exists without outsider-verifiable authority
    - whether the named surface is self-explaining now
    - whether broader outsider trust is still blocked
    - what stronger sentence remains blocked

    ### Footer decision rail

    The footer must make it impossible to flatten these into one answer:

    - replacement exists only
    - replacement reachable only
    - supersession explained only with operator context
    - named surface self-explaining
    - named surface outsider-verifiable
    - broader outsider-trust sentence still blocked

    ## Interaction requirements

    The interface must support:

    - clicking any successor-proof chip to open proof class, authority source, evidence age, and exclusions
    - comparing several explanation carriers side by side
    - filtering blockers to missing explanation, missing authority, naming ambiguity, or operator-context dependence
    - opening the blocked stronger sentence and seeing exactly which trust blockers keep it blocked

    ## Hard rules

    The page must never allow:

    - route success to silently become trust success
    - operator-side fingerprint review to silently become outsider-visible authority proof
    - local custom naming to silently become stable successor identity
    - one good trust surface to silently become broader outsider-trust safety
    """),
    '2118-remedy-hardening-attestation-supersession-trust-review-page-if-a-late-outsider-finds-the-corrected-thing-will-they-know-why-to-trust-it-interface-spec.md': dedent("""\
    # Remedy-hardening-attestation supersession-trust review page — if a late outsider finds the corrected thing, will they know why to trust it?

    ## Purpose

    This page is the forced-review surface for deciding whether late outsiders can understand and trust the supersession claim without extra operator help.
    It exists to stop the operator from exiting with a comforting story about routing or correction while the replacement still depends on hidden context to make sense.

    ## Opening question

    The page must ask, in plain language:

    **if a late outsider finds the corrected thing through this surface, will they be able to see what it supersedes, who says so, and why that claim deserves trust?**

    ## Required input block

    The review must collect at least:

    - stale artifact identifier
    - corrected replacement identifier
    - named outsider-facing surface
    - successor proof class
    - explanation carrier set
    - authority source class
    - outsider-verifiable trust class
    - unresolved trust blockers
    - strongest honest sentence candidate

    ## Forced review outcomes

    The page must force one of these outcomes:

    - corrected thing found but trust absent
    - supersession claimed but authority unclear
    - explanation exists only with operator help
    - named surface self-explaining but not independently verifiable
    - named surface outsider-verifiable and trustable
    - broader outsider-trust sentence still blocked
    - contradiction requires downgrade

    ## Required reviewer prompts

    The reviewer must answer, separately:

    - does the replacement explicitly name the stale thing it supersedes?
    - does the replacement explicitly name who authorizes the supersession?
    - is that authority visible on the same surface or only through a linked receipt?
    - could an outsider verify the claim without private operator memory?
    - does trust depend on a local-only name, remembered approval, or hidden app context?
    - what stronger sentence would be false if rendered now?

    ## Required comparison panel

    The review must keep side-by-side:

    - replacement routed versus replacement explained
    - explained versus authority-backed
    - authority-backed versus outsider-verifiable
    - named-surface trust versus broader outsider-trust coverage
    - strongest honest sentence versus blocked stronger sentence

    ## Interaction requirements

    The reviewer must be able to:

    - click any trust blocker and see exactly why it remains unresolved
    - open a proof drawer that shows successor proof, explanation carrier, authority source, and context dependence separately
    - downgrade the strongest sentence in one gesture when any blocker is marked active
    - compare several outsider surfaces before locking the receipt sentence

    ## Hard rules

    The page must never allow:

    - `they reached the corrected thing` to render as `they know why to trust it`
    - a private operator explanation to render as self-explaining supersession without an explicit inference badge
    - one linked proof to hide missing explanation on the visible surface
    - a remembered approval or local name to remain implicit in the final sentence
    """),
    '2119-remedy-hardening-attestation-supersession-trust-proof-page-successor-evidence-explanation-carrier-and-trust-sentence-ceiling-interface-spec.md': dedent("""\
    # Remedy-hardening-attestation supersession-trust proof page — successor evidence, explanation carrier, and trust sentence ceiling

    ## Purpose

    This page is the evidence-heavy surface for proving what a late outsider can actually understand and trust once they reach the corrected replacement.
    It exists to preserve the exact successor evidence, explanation carrier, and blocked stronger sentence instead of collapsing everything into a vague `this is the updated one` claim.

    ## Core proof question

    The page must answer:

    **what is the strongest evidence-backed sentence we can honestly make about outsider trust in the supersession now, and what stronger self-explaining sentence is still blocked?**

    ## Minimum evidence sections

    The proof page must contain:

    - receipt header
    - successor-relation ledger
    - explanation-carrier ledger
    - authority-and-verification ledger
    - blocker and contradiction ledger
    - strongest honest sentence / blocked stronger sentence panel

    ## Receipt header

    The header must show:

    - action identifier
    - stale artifact identifier
    - corrected replacement identifier
    - outsider-facing surface identifier
    - proof freshness timestamp
    - current supersession-trust standing

    ## Successor-relation ledger

    For each named surface show:

    - how the stale artifact is referenced
    - where the corrected replacement claims succession
    - successor proof class
    - evidence age
    - exclusions

    The ledger must make it impossible to merge `replacement exists`, `supersession is claimed`, and `supersession is proven`.

    ## Explanation-carrier ledger

    For each carrier show:

    - carrier class
    - same-surface or linked
    - outsider-visible wording state
    - ambiguity risk
    - whether operator context is still needed

    ## Authority-and-verification ledger

    The proof must preserve at least these distinct trust states:

    - authority absent
    - authority implied only
    - authority named but not verifiable by outsider
    - linked authority receipt available
    - same-surface outsider-verifiable authority shown
    - named surface trustable
    - broader outsider-trust sentence blocked

    ## Blocker and contradiction ledger

    Track at least:

    - stale artifact not explicitly named
    - successor proof missing or weak
    - authority source ambiguous
    - local-only naming dependence
    - operator-context dependence
    - later contradictory successor claim
    - trust drift after rename, move, or resharing

    Every blocker must carry:

    - why it remains open
    - what sentence it blocks
    - whether the blocker is direct contradiction or missing evidence

    ## Sentence panel

    The sentence panel must show:

    - strongest honest trust sentence now
    - strongest blocked stronger self-explaining sentence now
    - exact blockers for the stronger sentence
    - whether the current sentence rests on direct proof or inference

    ## Hard rules

    The page must never allow:

    - route evidence to substitute for trust evidence
    - operator-only fingerprint review to substitute for outsider-verifiable authority
    - one well-explained carrier to erase unresolved ambiguity elsewhere
    - direct-proof and inference-backed trust sentences to render as equivalent
    """),
    '2120-remedy-hardening-attestation-supersession-trust-timeline-page-stale-published-corrected-routed-explained-verified-and-trust-horizon-closed-events-interface-spec.md': dedent("""\
    # Remedy-hardening-attestation supersession-trust timeline page — stale published, corrected, routed, explained, verified, and trust horizon closed events

    ## Purpose

    This page is the chronological surface for showing how outsider trust in the supersession evolved over time.
    It exists to stop the archive from flattening `the corrected thing was eventually reachable` into `late outsiders could trust it at every meaningful moment`.

    ## Core question

    The timeline must answer:

    **across the trust horizon, when did the corrected replacement become reachable, when did it become self-explaining, and when did any later ambiguity or contradiction reopen the trust risk?**

    ## Required event classes

    The timeline must support at least:

    - stale artifact published
    - correction published
    - replacement route added
    - supersession explanation attached
    - authority receipt linked
    - outsider verification test passed
    - trust contradiction observed
    - rename or resharing reopened ambiguity
    - trust horizon closed
    - receipt superseded

    ## Required lanes

    The page must show at least these lanes:

    - source publication lane
    - replacement routing lane
    - explanation and authority lane
    - blocker and contradiction lane
    - sentence-ceiling lane

    ## Per-event payload

    Every event must preserve:

    - event timestamp
    - actor or subsystem
    - affected surface
    - trust consequence
    - evidence source
    - sentence consequence

    ## Visual rules

    The timeline must make these differences obvious:

    - replacement reachable versus replacement explained
    - explanation attached versus authority independently verifiable
    - one trust test passed versus horizon-wide outsider trust proved
    - no contradiction yet versus contradiction positively checked
    - rename or relabel versus genuine successor proof refresh

    ## Required overlays

    The interface must support overlays for:

    - successor proof strength over time
    - outsider-verifiable trust coverage over time
    - blocker count over time
    - strongest honest sentence changes

    ## Hard rules

    The page must never allow:

    - a routing event to silently stand in for a trust event
    - one explanation event to silently stand in for authority proof
    - one passed verification check to silently stand in for horizon-wide outsider trust
    - a quiet period to silently stand in for closed trust risk
    """),
    '2121-remedy-hardening-attestation-supersession-trust-lineage-receipt-page-outsider-trust-summary-self-explaining-supersession-and-blocked-stronger-truth-sentences-interface-spec.md': dedent("""\
    # Remedy-hardening-attestation supersession-trust lineage receipt page — outsider trust summary, self-explaining supersession, and blocked stronger truth sentences

    ## Purpose

    This page is the portable receipt for carrying the outsider-trust verdict into later review, audit, or dispute contexts.
    It exists so that a later reader can tell, without reopening the whole proof stack, whether a late outsider who reaches the corrected replacement can understand and trust why it supersedes the stale thing.

    ## Core output

    The receipt must answer:

    **what is the strongest honest sentence we can carry forward about outsider trust in the supersession, and what stronger self-explaining sentence remains blocked?**

    ## Required header fields

    Show at least:

    - receipt identifier
    - action identifier
    - stale artifact identifier
    - corrected replacement identifier
    - outsider-facing surface identifier
    - proof freshness timestamp
    - current supersession-trust standing

    ## Mandatory summary block

    The summary block must include:

    - successor proof class
    - explanation carrier set
    - authority source class
    - outsider-verifiable trust class
    - trust coverage threshold achieved
    - unresolved trust blocker count
    - highest-risk unresolved trust blocker
    - strongest honest trust sentence
    - blocked stronger self-explaining sentence

    ## Mandatory sentence ladder

    The receipt must preserve at least these separations:

    - corrected replacement exists only
    - corrected replacement reachable only
    - supersession explained only with operator context
    - named surface self-explaining
    - named surface outsider-verifiable
    - broader outsider-trust sentence blocked
    - later contradiction reopened trust risk

    ## Mandatory blocker block

    For every blocked stronger sentence show:

    - blocker name
    - blocker class
    - affected surface
    - whether the blocker is direct contradiction or missing evidence
    - what stronger sentence it prevents

    ## Mandatory provenance block

    The receipt must preserve:

    - who assembled the trust proof
    - what evidence sources were used
    - which trust claims are direct proof
    - which trust claims are inference only
    - when the trust horizon is considered to end

    ## Interaction requirements

    The receipt must support:

    - expanding any blocker into full proof detail
    - opening the supersession-trust map from the summary chip
    - comparing this receipt against the earlier discoverability receipt without losing sentence distinctions
    - exporting a compact version that still keeps the blocked stronger sentence visible

    ## Hard rules

    The receipt must never allow:

    - `replacement reachable` to render as `replacement trustable`
    - `authority exists somewhere` to erase missing same-surface explanation
    - `one trust surface is good` to erase unresolved ambiguity elsewhere
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
