from pathlib import Path
from textwrap import dedent

base = Path(__file__).resolve().parent
docs = base / 'docs'


def prepend(path: Path, text: str) -> None:
    original = path.read_text()
    path.write_text(text + original)


README_ADD = dedent("""\
## Revision addendum after rev0496 — outsider actionable reliance and operator-free remediation

This continuation archive advances the doctrine by tightening the next concrete seam after outsider late-arrival trust and self-explaining supersession:
**what happens after a late outsider can find the corrected replacement, understand why it supersedes the stale thing, and even see authority proof, but before the product may honestly pretend that the outsider can actually remediate their stale reliance from that surface without operator intervention, hidden app knowledge, manual copy-paste rituals, or private follow-up support**.
It does eight things in one tranche:

1. Continues the archive after rev0496 with a new page family centered on whether a late outsider can safely act from the corrected replacement instead of merely trusting it in principle.
2. Tightens the non-clone line again: borrow Resilio's candor about app handoff, manual link entry, WebUI link limits, approval flows, mode selection, placeholder fetches, and client-specific folder-location steps; refuse any contract where the operator still has to reconstruct `can this outsider actually remediate from the corrected thing without help?` from scattered sharing, browser, mobile, and mode pages.
3. Adds one new **Resilio evaluation** document focused on why current outsider actionable reliance and operator-free remediation are still too fragmented to clone even though the ingredients are useful.
4. Adds five new **interface specs** for actionable-remedy contract sheet, review, proof, timeline, and lineage receipt.
5. Makes one hard product decision explicit: **outsider late-arrival trust and self-explaining supersession are weaker than outsider actionable reliance and operator-free remediation.**
6. Makes another hard product decision explicit: **a replacement that explains itself is weaker than a replacement that also tells the outsider exactly what to do next and lets them do it without support.**
7. Makes a third hard product decision explicit: **manual copy-paste steps, app-specific workarounds, hidden approval gates, or default placeholder states are not allowed to impersonate `outsiders can remediate themselves from here`.**
8. Packages the result as another continuation archive whose new tranche makes the `required client / required manual steps / operator dependency / remediation affordance class / strongest honest action sentence / blocked stronger operator-free sentence` seam explicit in the reading order and page family.

New docs in this tranche:

- `2122-resilio-remedy-hardening-attestation-outsider-actionable-reliance-and-operator-free-remediation-fragmentation-evaluation.md`
- `2123-remedy-hardening-attestation-actionable-remedy-contract-sheet-page-outsider-switchability-remediation-path-and-support-ceiling-interface-spec.md`
- `2124-remedy-hardening-attestation-actionable-remedy-review-page-if-a-late-outsider-trusts-the-corrected-thing-can-they-remediate-without-operator-intervention-interface-spec.md`
- `2125-remedy-hardening-attestation-actionable-remedy-proof-page-remediation-affordance-ledger-friction-points-and-action-sentence-ceiling-interface-spec.md`
- `2126-remedy-hardening-attestation-actionable-remedy-timeline-page-stale-found-corrected-trusted-acted-confirmed-and-remediation-horizon-closed-events-interface-spec.md`
- `2127-remedy-hardening-attestation-actionable-remedy-lineage-receipt-page-outsider-actionability-summary-operator-free-remediation-and-blocked-stronger-truth-sentences-interface-spec.md`

""")

STATUS_ADD = dedent("""\
## rev0497 — outsider actionable reliance and operator-free remediation ceiling

This tranche adds one more hard line to the doctrine:

- **outsider late-arrival trust and self-explaining supersession are weaker than outsider actionable reliance and operator-free remediation**
- **a replacement that proves itself is weaker than a replacement that also tells a late outsider exactly what to do next and lets them do it without support**
- **manual handoff rituals, app-specific entry points, hidden approval gates, and placeholder defaults are different truths from outsider actionability**
- **required client, required steps, environment dependence, and stale-residue risk must stay explicit instead of dissolving into `they can trust the correction` folklore**

What this tranche contributes to the larger doctrine:

- `the outsider can trust this replacement` can no longer silently stand in for `the outsider can remediate from it unaided`
- `the link can eventually be opened in some client` can no longer silently stand in for `the remedy path is operator-free`
- `the outsider can probably figure out the right menu` can no longer silently stand in for `the product gave a self-sufficient next step`
- `the corrected thing is reachable after approval` can no longer silently stand in for `the outsider can complete remediation without waiting on someone else`
- supersession trust can no longer silently stand in for actionability

What remains intentionally true:

- discoverability and supersession trust still matter
- operator-visible trust evidence still matters
- beneficiary and audience stale-reliance retirement still matter
- but none of those may substitute for one explicit answer about whether a late outsider can act from the corrected thing, in the environment they actually have, without hidden setup lore or support escalation

New docs added in this tranche:

- `2122-resilio-remedy-hardening-attestation-outsider-actionable-reliance-and-operator-free-remediation-fragmentation-evaluation.md`
- `2123-remedy-hardening-attestation-actionable-remedy-contract-sheet-page-outsider-switchability-remediation-path-and-support-ceiling-interface-spec.md`
- `2124-remedy-hardening-attestation-actionable-remedy-review-page-if-a-late-outsider-trusts-the-corrected-thing-can-they-remediate-without-operator-intervention-interface-spec.md`
- `2125-remedy-hardening-attestation-actionable-remedy-proof-page-remediation-affordance-ledger-friction-points-and-action-sentence-ceiling-interface-spec.md`
- `2126-remedy-hardening-attestation-actionable-remedy-timeline-page-stale-found-corrected-trusted-acted-confirmed-and-remediation-horizon-closed-events-interface-spec.md`
- `2127-remedy-hardening-attestation-actionable-remedy-lineage-receipt-page-outsider-actionability-summary-operator-free-remediation-and-blocked-stronger-truth-sentences-interface-spec.md`

## Current frontier after rev0497 — outsider remediation completion and self-verifying clean-state truth

The next seam after **outsider trustable supersession and operator-free remediation** is now explicit:

- the archive can already say whether the corrected replacement is findable
- it can already say whether the corrected replacement explains itself and why a late outsider should trust it
- it can now say whether a late outsider can actually act from that surface without operator follow-up or hidden client lore
- it still needs to own the harder truth of **whether the outsider actually completed remediation, retired their stale local residue, and can verify that clean state without reopening the operator-support loop**

This pass therefore makes the next possible step visible: **outsider remediation completion and self-verifying clean-state truth**.

""")

RESILIO_ADD = dedent("""\
## Revision addendum after rev0496 — why outsider actionable reliance and operator-free remediation now sit on the non-clone side

Current official Resilio docs are still admirably candid that `the replacement can be trusted`, `the outsider can open the link`, `the outsider can add the share`, and `the outsider can actually remediate stale reliance unaided` are not one flat truth.
`Link structure and flow` still says the landing page only hands off to the Sync application if the user confirms Sync is installed, and otherwise the link may need to be added manually.
`Configuring WebUI` still says adding shares by clicking the link or placing the link into the browser address box is not working with Sync using WebUI and requires manual entry through `+` then `Enter a key or link`.
`Sync doesn't start when opening Link in browser` still says browser handoff can fail and again prescribes manual paste into `+` then `Enter a key or link` as the workaround.
`Quick guide to syncing` still says the receiver must copy the delivered link or key, paste it into `+` then `Enter key or link`, select a folder location, click `Connect`, and may still need sender-side approval.
`Sharing single file` still says the receiver must paste the link through `+` then `Enter a key or link`, choose the files' location, and that everyone who gets the generated link can download the shared files with no way to restrict number of uses or devices.
`Syncing between a desktop computer and a mobile device` still says Android users must disable `Simple mode` first if they want to pick folder location and that mobile arrivals default to placeholders until the user taps the items they want in full.
`Synchronization Modes` still says `Disconnected` and `Selective Sync` are different arrival modes, with connected visibility not meaning full local availability.

This is useful implementation candor.
It is also exactly why AnonSync should not clone the present contract.
One ordinary answer to `if a late outsider trusts the corrected thing, can they actually remediate from it without support?` still depends on combining link-handoff behavior, browser workarounds, client-specific menus, sender approval posture, location selection, and arrival-mode knowledge scattered across separate pages.

So this tranche freezes a stronger replacement line: **trusted replacement / actionable remedy path / operator dependency / environment dependency / stale-local-residue risk / strongest honest action sentence** must be first-class and rendered together.

""")

PRODUCT_ADD = dedent("""\
## Product-direction addendum after rev0496 — supersession trust must graduate into explicit outsider actionability

AnonSync should not let a trustworthy-looking replacement masquerade as a self-sufficient remedy surface.
The product direction is now explicit:

- every correction flow that can explain why the replacement is authoritative must also state whether the outsider can actually remediate from that surface in the client and environment they have
- every remedy-bearing surface must declare the remediation affordance class that backs the action claim (`single-step apply`, `guided multi-step`, `copy-paste plus client setup`, `approval-gated`, `operator-assisted only`, `none`)
- every surface must declare required client, required manual steps, required approvals, and expected stale-local-residue risk
- the strongest sentence engine must preserve the difference between `outsider can trust this`, `outsider can start remediation`, and `outsider can complete remediation without support`
- the receipt family must stay portable enough that a later reader can tell whether actionability rests on same-surface affordances, linked instructions, private operator guidance, or inference only

That means future interface work should keep one stable family for:

- required client and environment
- remediation affordance class
- required manual step count
- approval or support dependency
- stale-local-residue risk class
- strongest honest action sentence ceiling

The product should never force the operator to infer those truths from a workaround article, a hidden menu path, a QR-only mobile path, a placeholder default, or the mere fact that the outsider could eventually open the corrected thing.

""")

SOURCES_ADD = dedent("""\
## rev0497 source set — outsider actionable reliance and operator-free remediation

The most load-bearing source set for this pass was:

- Resilio's current `Link structure and flow` article, which still says the landing page only hands off to the Sync application if Sync is installed and the link may also need to be added manually.
- Resilio's current `Configuring WebUI` article, which still says adding shares by clicking a link or putting it in the browser address box is not working with Sync using WebUI and requires manual entry through `+` then `Enter a key or link`.
- Resilio's current `Sync doesn't start when opening Link in browser` article, which still says browser handoff can fail and again prescribes pasting the link directly into `+` then `Enter a key or link` as the workaround.
- Resilio's current `Quick guide to syncing` article, which still says receivers must copy the delivered link or key, paste it into `+` then `Enter key or link`, select a folder location, click `Connect`, and may still need sender-side approval.
- Resilio's current `Sharing single file` article, which still says receivers must paste the link through `+` then `Enter a key or link`, choose the files' location, and that everyone with the link can download the files without device- or use-count restrictions.
- Resilio's current `Syncing between a desktop computer and a mobile device` article, which still says Android users must disable `Simple mode` to pick folder location and that mobile arrivals default to placeholders until the user taps items they want in full.
- Resilio's current `Synchronization Modes` article, which still says `Disconnected` and `Selective Sync` are distinct arrival modes and visibility is not the same as fully local data.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for candid remediation ingredients and workarounds
- but current Resilio still answers `can a late outsider actually remediate stale reliance from the corrected thing without support?` too diffusely
- AnonSync should therefore prefer explicit actionable-remedy contract sheets, actionable-remedy reviews, actionable-remedy proofs, actionable-remedy timelines, and durable actionable-remedy lineage receipts over overloaded link-opening lore, browser workarounds, client menus, approval dialogs, and placeholder-mode hints

Primary sources:

- Link structure and flow
  https://help.resilio.com/hc/en-us/articles/204754739-Link-structure-and-flow

- Configuring WebUI
  https://help.resilio.com/hc/en-us/articles/115001184490-Configuring-WebUI

- Sync doesn't start when opening Link in browser
  https://help.resilio.com/hc/en-us/articles/204753649-Sync-doesn-t-start-when-opening-Link-in-browser

- Quick guide to syncing
  https://help.resilio.com/hc/en-us/articles/205506699-Quick-guide-to-syncing

- Sharing single file
  https://help.resilio.com/hc/en-us/articles/115000401010-Sharing-single-file

- Syncing between a desktop computer and a mobile device
  https://help.resilio.com/hc/en-us/articles/205451165-Syncing-between-a-desktop-computer-and-a-mobile-device

- Synchronization Modes
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

""")

DOCS = {
    '2122-resilio-remedy-hardening-attestation-outsider-actionable-reliance-and-operator-free-remediation-fragmentation-evaluation.md': dedent("""\
    # Resilio remedy-hardening attestation outsider actionable reliance and operator-free remediation fragmentation evaluation

    ## Why this seam matters now

    The archive can already say:

    - the corrected replacement is discoverable
    - the corrected replacement can name what it supersedes
    - a late outsider may understand why the corrected thing is the legitimate successor
    - authority proof may now be explicit enough that trust no longer depends entirely on operator memory

    That is still weaker than a harder question:

    **if the late outsider trusts the corrected replacement, can they actually remediate their stale reliance from that surface without operator intervention, hidden client knowledge, or side-channel support?**

    Trust is not yet action.
    A self-explaining successor is weaker than a self-sufficient remedy path.
    Without an explicit actionability contract, `they know this is the right thing` quietly expands into folklore about `they can now fix their own stale state from here`.

    ## Why current Resilio still leaves this too diffuse to clone

    Current official Resilio material is candid about several actionability ingredients, but it still spreads them across separate pages:

    - `Link structure and flow` says the landing page hands off to Sync only if Sync is installed and the link may also be added manually
    - `Configuring WebUI` says clicking the link or typing it into the browser address bar does not add the share in WebUI and the user must instead use `+` then `Enter a key or link`
    - `Sync doesn't start when opening Link in browser` says browser handoff may fail and again prescribes manual paste into `+` then `Enter a key or link`
    - `Quick guide to syncing` says the receiver must copy the delivered link or key, paste it into `+` then `Enter key or link`, choose a folder location, click `Connect`, and may still depend on sender-side approval
    - `Sharing single file` says receivers again paste the link through `+` then `Enter a key or link`, choose a location, and that everyone with the link can download the files without device- or use-count restrictions
    - `Syncing between a desktop computer and a mobile device` says Android users must disable `Simple mode` if they want to choose the destination and that mobile arrivals default to placeholders until the user taps the specific items they want
    - `Synchronization Modes` says `Disconnected`, `Selective Sync`, and `Synced` are distinct arrival states so visibility is not the same thing as full local remedial availability

    This is good implementation candor.
    It is not yet one first-class answer to **if the outsider trusts the correction, what exactly do they do next, in which client, with what dependencies, and with what residual stale-state risk?**

    ## The non-clone line

    AnonSync should not clone a contract where all of these are allowed to blur together:

    - the outsider can verify the corrected replacement
    - the link can open in some environment
    - the user can manually paste the link somewhere else if browser handoff fails
    - the sender can approve the request if needed
    - the outsider can choose a location if they already know which client settings to change
    - placeholders can later be fetched by tapping the right items
    - the outsider therefore has an operator-free remediation path

    Those are separate truths.

    ## Product decision frozen in this tranche

    This revision freezes a stronger line:

    - **outsider late-arrival trust and self-explaining supersession are weaker than outsider actionable reliance and operator-free remediation**
    - **a corrected replacement that explains itself is weaker than a corrected replacement that also tells the outsider what to do next and lets them do it without support**
    - **manual client rituals, hidden mode toggles, approval gates, or placeholder defaults may never impersonate `the outsider can remediate themselves from here`**

    ## What AnonSync should model explicitly instead

    AnonSync should add one first-class family for:

    - required client and environment
    - remediation affordance class
    - required manual step count
    - approval dependency class
    - operator-support dependency class
    - stale-local-residue risk class
    - action confirmation class
    - strongest honest action sentence
    - blocked stronger operator-free sentence

    ## Interface consequence

    That is why this tranche adds five more first-class pages:

    - **actionable-remedy contract sheet**
    - **actionable-remedy review**
    - **actionable-remedy proof**
    - **actionable-remedy timeline**
    - **actionable-remedy lineage receipt**
    """),
    '2123-remedy-hardening-attestation-actionable-remedy-contract-sheet-page-outsider-switchability-remediation-path-and-support-ceiling-interface-spec.md': dedent("""\
    # Remedy-hardening-attestation actionable-remedy contract sheet page — outsider switchability, remediation path, and support ceiling

    ## Purpose

    This page is the operator-facing contract sheet for deciding whether a late outsider who trusts the corrected replacement can actually remediate their stale reliance from the surface they have.
    It exists to stop `this replacement is trustworthy` from being mistaken for `this replacement gives the outsider a self-sufficient next step`.

    ## Core question

    The page must answer:

    **what is the strongest honest sentence we can make about outsider actionability now, and what stronger operator-free remediation sentence is still blocked?**

    ## Required fields

    The contract sheet must capture at least:

    - stale artifact identifier
    - corrected replacement identifier
    - outsider-facing surface identifier
    - required client class
    - required environment class
    - remediation affordance class
    - required manual step count
    - approval dependency class
    - operator-support dependency class
    - stale-local-residue risk class
    - action confirmation class
    - strongest honest action sentence
    - blocked stronger operator-free sentence

    ## Remediation affordance classes

    The sheet must preserve at least:

    - trustable only, no action path shown
    - action path linked elsewhere
    - guided multi-step remediation
    - client-specific workaround required
    - approval-gated remediation
    - operator-assisted remediation only
    - same-surface operator-free remediation
    - remediation complete but clean-state proof still separate

    ## Support-dependency panel

    The page must force explicit answers to:

    - does the outsider need a specific app or client already installed?
    - does the outsider need to know a hidden menu path?
    - does the outsider need sender-side approval or reapproval?
    - does the outsider need to choose arrival mode, destination path, or placeholder behavior?
    - does the outsider need a human operator if the default handoff fails?

    ## Residue-risk panel

    The sheet must keep separate:

    - correction trusted
    - remediation started
    - remediation likely complete
    - stale local residue still plausible
    - stale local residue positively retired elsewhere

    ## Hard rules

    The page must never allow:

    - trust proof to silently stand in for actionability
    - one successful client path to erase failure on another outsider path
    - manual workaround knowledge to remain implicit in the action sentence
    - `can begin remediation` to render as `can finish remediation without support`
    """),
    '2124-remedy-hardening-attestation-actionable-remedy-review-page-if-a-late-outsider-trusts-the-corrected-thing-can-they-remediate-without-operator-intervention-interface-spec.md': dedent("""\
    # Remedy-hardening-attestation actionable-remedy review page — if a late outsider trusts the corrected thing, can they remediate without operator intervention?

    ## Purpose

    This page is the review surface for forcing the operator to confront whether outsider trust actually turns into outsider remediation.
    It exists to prevent the archive from settling for `they will understand the correction` when the harder question is `can they act on it now, in their real environment, without help?`

    ## Review question

    The review must force a direct answer to:

    **if a late outsider arrives at the corrected replacement and believes it, can they actually switch from stale reliance by following what the surface gives them, without operator intervention?**

    ## Required review prompts

    The page must ask at least:

    - what client does the outsider need right now?
    - what exact next step is visible from the corrected surface?
    - what hidden menu, setting, or workaround is still required?
    - is sender-side approval still a gate?
    - does the outsider land in full remediation, partial remediation, placeholder state, or disconnected visibility only?
    - what stale residue can remain even if the outsider follows the path correctly?
    - what stronger action sentence would be false if rendered now?

    ## Required comparison panel

    The review must keep side-by-side:

    - trusted replacement versus actionable remedy
    - action path linked elsewhere versus action path shown here
    - same-surface action versus client-specific workaround
    - can start remediation versus can finish without support
    - strongest honest action sentence versus blocked stronger sentence

    ## Interaction requirements

    The reviewer must be able to:

    - click any action blocker and see exactly what additional support it implies
    - open a path drawer that shows client, steps, approval state, and residue risk separately
    - downgrade the strongest sentence in one gesture when any support dependency remains active
    - compare desktop, WebUI, and mobile paths without losing sentence distinctions

    ## Hard rules

    The page must never allow:

    - `the outsider can trust this` to render as `the outsider can remediate from this`
    - a manual copy-paste workaround to remain implicit in the final sentence
    - one working path to hide that another named outsider path still needs support
    - placeholder visibility to render as completed remediation
    """),
    '2125-remedy-hardening-attestation-actionable-remedy-proof-page-remediation-affordance-ledger-friction-points-and-action-sentence-ceiling-interface-spec.md': dedent("""\
    # Remedy-hardening-attestation actionable-remedy proof page — remediation affordance ledger, friction points, and action sentence ceiling

    ## Purpose

    This page is the evidence-heavy surface for proving what a late outsider can actually do after trusting the corrected replacement.
    It exists to preserve exact action affordances, friction points, and blocked stronger sentences instead of collapsing everything into a vague `the corrected thing is usable` claim.

    ## Core proof question

    The page must answer:

    **what is the strongest evidence-backed sentence we can honestly make about outsider actionability now, and what stronger operator-free remediation sentence is still blocked?**

    ## Minimum evidence sections

    The proof page must contain:

    - receipt header
    - remediation-path ledger
    - client-and-environment ledger
    - friction and dependency ledger
    - residue and completion-risk ledger
    - strongest honest sentence / blocked stronger sentence panel

    ## Receipt header

    The header must show:

    - action identifier
    - stale artifact identifier
    - corrected replacement identifier
    - outsider-facing surface identifier
    - proof freshness timestamp
    - current actionable-remedy standing

    ## Remediation-path ledger

    For each named path show:

    - path class
    - required client
    - visible next step
    - manual steps remaining
    - approval requirement
    - expected result state
    - exclusions

    The ledger must make it impossible to merge `reachable`, `trustable`, `actionable`, and `complete`.

    ## Client-and-environment ledger

    For each environment show:

    - browser handoff state
    - WebUI support state
    - mobile destination-path state
    - arrival mode default
    - same-surface versus linked instructions
    - whether operator context is still needed

    ## Friction and dependency ledger

    Track at least:

    - app missing
    - browser handoff failure
    - manual paste workaround required
    - approval gate pending
    - hidden setting change required
    - placeholder fetch still required
    - destination choice ambiguity
    - support escalation required

    Every friction item must carry:

    - why it remains open
    - what sentence it blocks
    - whether it is environment-specific or universal

    ## Residue and completion-risk ledger

    The proof must preserve at least these states:

    - trustable only
    - remediation path present but not yet executed
    - remediation started
    - remediation likely partial
    - stale residue risk remains
    - operator-free remediation shown
    - remediation completion still separate

    ## Hard rules

    The page must never allow:

    - trust evidence to substitute for action evidence
    - one workaround to erase unresolved friction elsewhere
    - action-start evidence to substitute for completion evidence
    - client-specific success to silently stand in for environment-wide operator-free remediation
    """),
    '2126-remedy-hardening-attestation-actionable-remedy-timeline-page-stale-found-corrected-trusted-acted-confirmed-and-remediation-horizon-closed-events-interface-spec.md': dedent("""\
    # Remedy-hardening-attestation actionable-remedy timeline page — stale found, corrected, trusted, acted, confirmed, and remediation horizon closed events

    ## Purpose

    This page is the chronological surface for showing how outsider actionability evolved over time.
    It exists to stop the archive from flattening `the correction was eventually trusted` into `late outsiders could remediate themselves at every meaningful moment`.

    ## Core question

    The timeline must answer:

    **across the remediation horizon, when did the corrected replacement become trustworthy, when did it become actionable without support, and when did any later dependency or environment break reopen the need for operator help?**

    ## Required event classes

    The timeline must support at least:

    - stale artifact encountered
    - corrected replacement reached
    - supersession trusted
    - action path published
    - client workaround published
    - approval gate cleared
    - outsider remediation started
    - outsider remediation confirmed
    - environment break reopened support need
    - remediation horizon closed
    - receipt superseded

    ## Required lanes

    The page must show at least these lanes:

    - outsider discovery lane
    - trust and explanation lane
    - remediation path lane
    - friction and support lane
    - sentence-ceiling lane

    ## Per-event payload

    Every event must preserve:

    - event timestamp
    - actor or subsystem
    - affected client or surface
    - action consequence
    - evidence source
    - sentence consequence

    ## Visual rules

    The timeline must make these differences obvious:

    - trustworthy replacement versus actionable remedy
    - linked instructions versus same-surface action path
    - approval cleared versus operator-free path proven
    - remediation started versus remediation confirmed
    - quiet period versus support need positively checked and absent

    ## Required overlays

    The interface must support overlays for:

    - actionability strength over time
    - support dependency count over time
    - environment coverage over time
    - strongest honest action sentence changes

    ## Hard rules

    The page must never allow:

    - a trust event to silently stand in for an action event
    - one workaround publication to silently stand in for operator-free remediation
    - one confirmed outsider action to silently stand in for horizon-wide actionability
    - a quiet period to silently stand in for closed support risk
    """),
    '2127-remedy-hardening-attestation-actionable-remedy-lineage-receipt-page-outsider-actionability-summary-operator-free-remediation-and-blocked-stronger-truth-sentences-interface-spec.md': dedent("""\
    # Remedy-hardening-attestation actionable-remedy lineage receipt page — outsider actionability summary, operator-free remediation, and blocked stronger truth sentences

    ## Purpose

    This page is the portable receipt for carrying the outsider-actionability verdict into later review, audit, or dispute contexts.
    It exists so that a later reader can tell, without reopening the whole proof stack, whether a late outsider who trusts the corrected replacement can actually remediate stale reliance from that surface without support.

    ## Core output

    The receipt must answer:

    **what is the strongest honest sentence we can carry forward about outsider actionability now, and what stronger operator-free remediation sentence remains blocked?**

    ## Required header fields

    Show at least:

    - receipt identifier
    - action identifier
    - stale artifact identifier
    - corrected replacement identifier
    - outsider-facing surface identifier
    - proof freshness timestamp
    - current actionable-remedy standing

    ## Mandatory summary block

    The summary block must include:

    - required client class
    - remediation affordance class
    - required manual step count
    - approval dependency class
    - operator-support dependency class
    - stale-local-residue risk class
    - action confirmation class
    - highest-risk unresolved action blocker
    - strongest honest action sentence
    - blocked stronger operator-free sentence

    ## Mandatory sentence ladder

    The receipt must preserve at least these separations:

    - correction trustable only
    - action path discoverable only
    - action path requires client-specific workaround
    - action path requires approval or operator help
    - named surface operator-free for one environment
    - broader operator-free sentence blocked
    - remediation completion still separate

    ## Mandatory blocker block

    For every blocked stronger sentence show:

    - blocker name
    - blocker class
    - affected client or surface
    - whether the blocker is support dependency, environment dependence, or missing evidence
    - what stronger sentence it prevents

    ## Mandatory provenance block

    The receipt must preserve:

    - who assembled the action proof
    - what evidence sources were used
    - which action claims are direct proof
    - which action claims are inference only
    - when the remediation horizon is considered to end

    ## Interaction requirements

    The receipt must support:

    - expanding any blocker into full proof detail
    - opening the actionable-remedy map from the summary chip
    - comparing this receipt against the earlier supersession-trust receipt without losing sentence distinctions
    - exporting a compact version that still keeps the blocked stronger sentence visible

    ## Hard rules

    The receipt must never allow:

    - `replacement trustable` to render as `replacement actionable`
    - `action possible with help` to render as `operator-free remediation`
    - `one environment works` to erase unresolved action blockers elsewhere
    - the blocked stronger sentence to disappear from exported or compact views
    """),
}


for rel, text in DOCS.items():
    (docs / rel).write_text(text)

prepend(base / 'README.md', README_ADD)
prepend(docs / '00-status.md', STATUS_ADD)
prepend(docs / '10-resilio-sync-evaluation.md', RESILIO_ADD)
prepend(docs / '20-product-direction.md', PRODUCT_ADD)
prepend(docs / 'sources.md', SOURCES_ADD)

