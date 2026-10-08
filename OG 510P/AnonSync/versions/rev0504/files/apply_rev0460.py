from pathlib import Path
from textwrap import dedent

root = Path('/mnt/data/workrev460')
docs = root / 'docs'

new_docs = {
    '1900-resilio-remedy-hardening-attestation-egress-governance-recipient-knownness-onward-sharing-and-off-world-memory-ceiling-evaluation.md': dedent('''
        # Resilio remedy hardening attestation egress governance, recipient knownness, onward-sharing, and off-world memory ceiling evaluation

        ## What current Resilio gets right

        Current official Resilio materials still deserve credit for being fairly candid that sharing is not one flat lane.
        That candor matters.

        The strongest current ingredients are:

        - current `Link structure and flow` docs still say folder sharing commonly travels by a link and that the receiving peer uses the temporary key in that link to request access from the owner
        - current `Sync Share Dialog (Desktop)` docs still say links can be copied to clipboard or sent through e-mail and messenger, approval can be required for only new peers or for all peers, and an unchecked approval option lets a peer who gets the link connect and start syncing automatically
        - the same share-dialog docs still say Advanced-folder Owners can share with other peers, while Standard folders have no Owner gate and all peers can share the folder further
        - current `What's the difference between Standard and Advanced folders?` docs still say Standard-folder peers can share the key they have without any limitations
        - current `User Management` docs still say Owners can invite new users to the folder and that all linked devices under one identity act as Owners
        - current `Sync Private Identity & Linking My Devices` docs still say once a remote user approves one device they can choose to auto-approve all linked devices for future sharing
        - current `Sharing single file` docs still say everyone who gets the generated link can download the shared files, there is no option to restrict number of usages or ban some devices, recipients can share the files further, and expiration can be disabled so the link never expires
        - current `Comprehensive guide to syncing (Desktop-Desktop)` docs still say keys or links can simply be copied to clipboard and sent using any convenient and trusted way
        - current `Disconnecting and Removing Folders` docs still say even after removal from linked devices the folder may still remain on other remote devices not linked to the personal identity

        Those are useful truths.
        They still do not add up to one typed answer to:

        > `after a ruling was corrected and our governed worlds were cleaned up, who outside governance might still hold it, who could further spread it, and what is the strongest honest global sentence we can still say?`

        ## Where the current contract still fragments

        The problem is not that Resilio hides sharing.
        The problem is that current outward-spread truth is still scattered across share dialogs, key versus link differences, owner privileges, linked-device trust expansion, file-send behavior, and remove/disconnect limits instead of being owned as one case-scoped off-world ceiling contract.

        Today an operator can often infer only weaker truths such as:

        - a link was generated once
        - some peers probably received or used it
        - one approval gate existed at one point
        - one recipient may have had onward-share rights
        - one single-file link may have been effectively public to whoever obtained it
        - one Standard key may still be portable without owner oversight
        - one linked family may silently widen future approval scope
        - one removal affected governed devices but not all remote holders

        Those are important clues.
        They are not the same as an explicit answer to `which egress lanes existed, which recipients are actually known, which onward-sharing rights existed, which disclosures are still revocable versus irrevocable, which off-world copies remain merely suspected, and what stronger global-forgetting sentence must remain blocked forever or until named evidence appears?`

        ## Why that matters for AnonSync

        AnonSync needs stronger language than `we erased our copies` or even `governed cohort is resurrection-resistant`.
        It needs to support claims such as:

        - the governed cohort is clean, but one historical share lane used a forwardable key whose downstream holders were never fully enumerated
        - all named recipients were notified and governed copies were erased, but one earlier Owner could have reshared before revocation and that downstream tree remains only partially known
        - a file-send link expired for new downloads, but previously delivered recipients can still hold or resend the bytes
        - the strongest honest sentence is `off-world memory ceiling unknown`, not because the product failed to clean up its own world, but because the original egress posture was intentionally wider than later governance can prove away
        - a case is safe for current governed use and even resurrection-resistant for the required cohort, while `globally forgotten` remains permanently blocked by historical externalization risk
        - one explicit, case-owned receipt should preserve that ceiling so later operators do not accidentally overstate what revocation or erase work achieved

        AnonSync therefore needs first-class objects for **egress-lane inventory, recipient-knownness class, onward-sharing authority, revocation reach ceiling, external-holder suspicion class, off-world memory ceiling, and blocked global sentence** rather than leaving operators to reconstruct that truth from share menus, permission prose, link TTLs, and removal caveats.

        ## Non-clone conclusion

        Borrow the candor.
        Do not clone the contract shape.

        Resilio's current docs still answer the key question — `who outside governance may still hold, forward, or remember this, and how global can our forgetting sentence honestly be?` — only by making the operator combine several partially overlapping operational surfaces:

        - link flow and landing-page mechanics
        - approval settings that differ between new peers and all peers
        - copy-to-clipboard and messenger delivery paths
        - Owner or Standard-key onward-sharing rights
        - linked-device auto-approval expansion for future sharing
        - file-send links that may never expire and cannot be usage-limited
        - disconnect or removal behavior that stops short of clearing unlinked remote holders

        That is enough to justify a harder product stance:

        > AnonSync is not cloning Resilio because governed-world cleanup is not the same thing as off-world closure, and current externalization truth is still reconstructed from sharing mechanics and permission articles instead of owned by one stable page family that says which egress lanes existed, who is known to have received them, what onward-sharing power existed, what can still be revoked, and which stronger global sentence is permanently blocked.
    ''').strip() + '\n',

    '1901-remedy-hardening-attestation-egress-governance-contract-sheet-page-share-lanes-recipient-knownness-and-off-world-ceiling-interface-spec.md': dedent('''
        # Remedy-hardening-attestation egress-governance contract sheet page — share lanes, recipient knownness, and off-world ceiling

        ## Purpose

        This page is the compact contract for a case whose governed worlds may already be cleaned up, but whose historical outward spread still imposes a ceiling on what the product may claim globally.
        It exists so the product can distinguish `governed cohort cleaned`, `all named recipients accounted for`, `off-world spread still partly unknowable`, and `global forgetting permanently blocked`.

        ## Core fields

        - case identifier
        - source copy-extirpation receipt identifier
        - current governing receipt identifier
        - current egress-governance class
        - current off-world memory ceiling class
        - total historical egress-lane count
        - fully enumerated egress-lane count
        - open-recipient-knownness gap count
        - onward-share-authority lane count
        - irrevocable disclosure lane count
        - revocable-disclosure lane count
        - expired-link lane count
        - never-expiring-link lane count
        - standard-key lane count
        - owner-reshare lane count
        - linked-family auto-approval lane count
        - named external-recipient count
        - suspected but unverified external-holder count
        - downstream-recipient-tree completeness class
        - strongest speakable global sentence
        - strongest blocked broader global sentence
        - next evidence that upgrades recipient closure confidence
        - next evidence that forces immediate downgrade or escalation

        ## Egress-governance classes

        The page must model at least these distinct classes:

        - egress inventory incomplete
        - egress inventory complete, recipient map incomplete
        - named recipients known, onward-sharing rights uncertain
        - named recipients known, onward-sharing tree incomplete
        - governed cohort closed, off-world holders partially known
        - governed cohort closed, off-world holders structurally unknowable
        - global forgetting blocked by historical open egress
        - global forgetting blocked by irrevocable externalization
        - named-recipient closure achieved for required cohort only
        - off-world ceiling acknowledged and durably receipted

        ## Egress-lane classes

        The page must support at least these lane types:

        - direct identity-based share
        - advanced-folder owner-mediated share
        - standard-key share
        - forwardable folder link
        - single-file transfer link
        - QR-mediated share
        - clipboard or messenger relay
        - email handoff
        - linked-device auto-approval expansion
        - local export packet or bundle handoff
        - manual copy-out outside product governance
        - unknown historical disclosure lane

        ## Recipient-knownness classes

        For each lane the page must preserve at least these classes:

        - recipient fully known and named
        - recipient cohort known but members not fully named
        - recipient inferred from evidence, not directly named
        - downstream holder possible through onward-sharing rights
        - downstream holder confirmed
        - downstream tree structurally unknowable
        - no evidence of receipt despite lane creation
        - lane existence suspected but not proven

        ## Fixed rendering order

        Every egress-governance contract sheet must render the same sections in the same order:

        1. **Strongest speakable global sentence**
        2. **Historical egress-lane inventory**
        3. **Recipient-knownness and onward-share authority**
        4. **Revocation reach and off-world ceiling**
        5. **Irrevocable disclosures and permanent blockers**
        6. **Blocked stronger global sentences**

        ## Hard rules

        The page must never silently upgrade:

        - `our governed hosts are clean` into `all recipients forgot`
        - `link expired` into `bytes unrecoverable`
        - `approval was required` into `all holders are named`
        - `owner revoked` into `downstream resharing undone`
        - `single-file link removed` into `all downloaded copies gone`
        - `no current external holder observed` into `global forgetting`

        ## Minimum operator questions answered

        The page must let a later operator answer, without hunting across other pages:

        - which outward lanes ever existed for this material
        - which of those lanes granted onward-sharing or open portability
        - which recipients are named, inferred, or structurally unknowable
        - what the current revocation reach actually covers
        - whether global forgetting is blocked by historical externalization alone
        - exactly which stronger sentence remains blocked and why
    ''').strip() + '\n',

    '1902-remedy-hardening-attestation-egress-governance-review-page-who-might-still-hold-or-reshare-this-outside-governance-interface-spec.md': dedent('''
        # Remedy-hardening-attestation egress-governance review page — who might still hold or reshare this outside governance?

        ## Review question

        Even if governed worlds are cleaned up, can the product honestly say who outside governance may still hold, relay, or remember this material — or do historical share lanes, owner rights, Standard keys, indefinite links, or prior deliveries still block any broader global sentence?

        ## Review panels

        ### 1) Historical lane inventory review

        Force the operator to enumerate every historical outward path by which the material or its enabling state could have crossed the governance boundary.
        The review must preserve at least these distinctions:

        - identity-approved share versus portable key or link
        - folder-share lane versus single-file transfer lane
        - one-time named handoff versus reusable lane
        - expiry-bound lane versus non-expiring lane
        - product-mediated lane versus manual relay outside product custody

        ### 2) Recipient-knownness review

        For every lane, require the operator to score who is actually known.
        The page must preserve at least these distinctions:

        - all direct recipients named
        - some recipients named, cohort wider than names
        - downstream holders possible because onward-sharing was allowed
        - downstream holders confirmed by evidence
        - historical holders structurally unknowable because the lane was portable or forwarded outside governance

        ### 3) Authority and propagation review

        Show, for each lane:

        - whether the recipient could only read, could write, or could reshare
        - whether linked-device or owner rules widened authority after the first approval
        - whether Standard-folder key semantics removed owner visibility over future spread
        - whether later revocation affected only future updates or could realistically retract already-delivered bytes

        ### 4) Off-world ceiling review

        The page must compute and show:

        - strongest honest current governed-cohort sentence
        - strongest honest named-recipient sentence
        - strongest honest global sentence
        - exact reason any broader sentence remains blocked
        - whether the blocker is temporary evidentiary debt or permanent historical unknowability

        ## Required outcomes

        The page must support outcomes such as:

        - `governed cohort clean; recipient tree still incomplete`
        - `all named direct recipients accounted for; onward-sharing rights keep downstream closure blocked`
        - `single-file link history makes off-world holder set structurally unknowable`
        - `global forgetting is blocked forever by historical externalization posture, even though current governed use is safe`
        - `named-recipient closure is honest for the required cohort only`

        ## Mandatory review discipline

        The review must reject any path that tries to treat these as equivalent:

        - approval required and recipients named
        - link expiry and copy extinction
        - owner revocation and downstream recall
        - no fresh sightings and no external holders
        - governed-world resurrection resistance and global forgetting

        ## Required warnings

        The page must render plain warnings when:

        - any Standard-key lane ever existed
        - any single-file link was configured to never expire
        - any recipient or owner had onward-sharing authority
        - any historical delivery happened through clipboard, messenger, or email relay without durable recipient accounting
        - any direct recipient is known but downstream resharing remains unverifiable
        - a case is about to be described as `forgotten globally` even though the ceiling is only `governed cohort clean`
    ''').strip() + '\n',

    '1903-remedy-hardening-attestation-egress-governance-proof-page-share-lanes-recipient-rights-and-global-forgetting-floor-interface-spec.md': dedent('''
        # Remedy-hardening-attestation egress-governance proof page — share lanes, recipient rights, and global forgetting floor

        ## Purpose

        This page is the durable proof that a case's outward-spread history was evaluated under explicit lane, recipient, authority, and off-world-ceiling rules.
        It must let a later verifier see not only that the product's own worlds were cleaned, but what historical egress posture still limits any claim about global forgetting or universal recall.

        ## Sections

        ### 1) Egress-governance header

        Publish:

        - case identifier
        - source copy-extirpation receipt identifier
        - current governing receipt identifier
        - current egress-governance class
        - current off-world memory ceiling class
        - required global sentence floor

        ### 2) Historical egress-lane table

        For each lane or lane cohort print:

        - lane identifier or cohort label
        - lane class
        - first known issue time
        - last known active time
        - expiry or disable status
        - initial permission or authority level
        - onward-sharing capability
        - whether the lane delivered bytes, metadata, or both

        ### 3) Recipient-knownness table

        For each lane print:

        - direct-recipient knownness class
        - direct-recipient count, if supportable
        - named-recipient list or cohort label
        - downstream-recipient-tree completeness class
        - evidence basis for knownness
        - exact blocker on broader closure language

        ### 4) Revocation-reach analysis

        The proof must score every relevant reach boundary:

        - can future access be blocked?
        - can already-delivered bytes be recalled?
        - can downstream resharing be proven absent?
        - can historical off-product forwarding be enumerated?
        - does link expiry affect only new pulls or all existing holders?
        - does owner removal or permission change reach unlinked or already-exported worlds?

        For each boundary print:

        - boundary class
        - currently open or closed
        - evidence supporting that assessment
        - still-exposed audience class
        - action that would narrow, but not overstate, the ceiling

        ### 5) Strongest speakable sentence block

        The page must compute and print:

        - strongest honest governed-cohort sentence
        - strongest honest named-recipient sentence
        - strongest honest global sentence
        - strongest blocked broader global sentence
        - exact reasons the broader sentence remains blocked

        ## Mandatory proof distinctions

        The proof must preserve at least these distinctions:

        - governed hosts erased versus external holders recalled
        - direct recipients named versus downstream tree complete
        - future access blocked versus already-delivered copies gone
        - lane expired versus lane historically externalized
        - no evidence of further spread versus further spread impossible
        - governed-world resurrection resistance versus global forgetting

        ## Claim ceilings

        The proof must never permit these sentences without direct support:

        - `everyone who ever got it is known`
        - `all downstream sharing was undone`
        - `expired link means nobody still has it`
        - `removal from our identity cleared all remotes`
        - `globally forgotten`
        - `cannot resurface from outside governance`
    ''').strip() + '\n',

    '1904-remedy-hardening-attestation-egress-governance-timeline-page-link-issue-approval-forward-expiry-and-externalization-events-interface-spec.md': dedent('''
        # Remedy-hardening-attestation egress-governance timeline page — link issue, approval, forward, expiry, and externalization events

        ## Purpose

        This page is the chronological spine for how the material crossed governance boundaries and how later revocation or closure attempts interacted with that history.
        It exists to preserve the difference between issuing a lane, approving a recipient, enabling onward-sharing, expiring future access, and proving nothing about already externalized copies.

        ## Event classes

        The timeline must support at least these event classes:

        - share lane created
        - share lane delivered
        - approval rule changed
        - direct recipient approved
        - linked-family trust widened
        - owner or reshare authority granted
        - standard-key lane observed
        - single-file link issued
        - link configured to never expire
        - link expired for new pulls
        - manual relay outside product custody observed
        - downstream holder confirmed
        - onward-sharing suspected
        - revocation attempt opened
        - future access blocked
        - named recipients notified
        - global sentence downgraded
        - global sentence ceiling acknowledged
        - off-world closure evidence added
        - permanent unknowability blocker receipted

        ## Required timeline columns

        Every event row must print at least:

        - event timestamp
        - actor or subsystem
        - event class
        - affected lane or cohort
        - prior off-world ceiling class
        - resulting off-world ceiling class
        - evidence attached
        - whether the event widened spread, narrowed spread, or only changed future access

        ## Required chronology guarantees

        The timeline must preserve:

        - whether bytes could have been delivered before approval rules tightened
        - whether onward-sharing rights existed before later revocation
        - whether link expiry happened after a long open-access window
        - whether recipient accounting happened before or after irreversible externalization
        - whether a case was ever overstated globally before the off-world ceiling was acknowledged
        - whether later evidence named more recipients without actually proving universal closure

        ## Required timeline summaries

        The page must compute and print:

        - first known governance-boundary crossing time
        - first time onward-sharing became possible
        - latest time a historically open lane could accept new pulls
        - first time the current strongest global sentence became speakable
        - latest time broader global language was explicitly blocked

        ## Blocking rules

        The timeline must never flatten:

        - lane issue into byte delivery
        - approval into recipient enumeration
        - expiry into recall
        - revocation into off-world deletion
        - named-recipient contact into downstream-tree closure
        - governed cleanup into global forgetting
    ''').strip() + '\n',

    '1905-remedy-hardening-attestation-egress-governance-lineage-receipt-page-governed-cohort-ceiling-and-blocked-global-sentences-interface-spec.md': dedent('''
        # Remedy-hardening-attestation egress-governance lineage receipt page — governed-cohort ceiling and blocked global sentences

        ## Purpose

        This page is the durable receipt that captures what level of off-world closure was honestly achieved for a case at a specific time.
        It must survive later review and show not merely that governed worlds were cleaned, but what historical egress posture remained, how much recipient closure was actually known, and which broader global sentence the product refused to make.

        ## Receipt header

        The receipt must print:

        - receipt identifier
        - case identifier
        - source copy-extirpation receipt identifier
        - current governing receipt identifier
        - current egress-governance class
        - current off-world memory ceiling class
        - required global sentence floor
        - receipt issuance time

        ## Receipt body

        The receipt must always include:

        - strongest speakable governed-cohort sentence
        - strongest speakable named-recipient sentence
        - strongest speakable global sentence
        - strongest blocked broader global sentence
        - total historical egress-lane count
        - onward-share-authority lane count
        - named external-recipient count
        - suspected or structurally unknowable external-holder count
        - exact reason broader global language is blocked

        ## Mandatory distinctions preserved by the receipt

        The receipt must preserve at least these distinctions:

        - governed cohort cleaned versus off-world closure proven
        - named recipients known versus all holders known
        - future access blocked versus already-delivered copies recalled
        - lane expired versus externalization ended
        - no current external sightings versus no external memory ceiling
        - named-recipient closure versus global forgetting

        ## Example speakable sentences

        The receipt should support outputs such as:

        - `governed cohort clean; off-world holder set incomplete`
        - `all named direct recipients accounted for; downstream resharing remains structurally unknowable`
        - `single-file historical disclosure means global forgetting is blocked even though current governed use is safe`
        - `named-recipient closure is honest for the required cohort only; stronger global language remains blocked by historical portable-key exposure`
        - `off-world ceiling acknowledged and receipted; no broader sentence claimed`

        ## Claim ceilings

        The receipt must never let later operators silently say:

        - `everyone forgot it`
        - `all external copies are gone`
        - `expiry proved recall`
        - `owner revocation eliminated downstream spread`
        - `global forgetting achieved` when the evidence only supports governed-cohort cleanup
        - `cannot reappear from outside governance` when historical externalization posture still blocks that sentence

        ## Precedence rules

        The receipt must make these rules explicit:

        - later recipient-discovery evidence can strengthen an older receipt, but only through a new receipt that explicitly owns the stronger sentence
        - later evidence of additional historical lanes automatically demotes prior global language until the lane is incorporated
        - a permanent unknowability blocker remains stronger than optimistic silence
        - governed-world extirpation receipts remain citable as history even when global forgetting stays blocked forever
    ''').strip() + '\n',
}

for name, content in new_docs.items():
    (docs / name).write_text(content)

readme_addendum = dedent('''
    ## Revision addendum after rev0459 — remedy hardening attestation egress governance, recipient knownness, and off-world memory ceiling

    This continuation archive advances the doctrine by tightening another concrete non-clone seam around **what remains honestly sayable after governed worlds are cleaned up, but historical share lanes may still have carried the ruling or its bytes beyond governance into recipients, downstream holders, and memory surfaces that are only partly known or permanently unknowable**.
    It does eight things in one tranche:

    1. Continues the archive after rev0459 with a new page family centered on what happens *after* copy extirpation and named-cohort resurrection resistance exist but *before* the product should pretend that global forgetting or universal recall is honest.
    2. Tightens the non-clone line again: borrow Resilio's candor about link flow, clipboard and messenger delivery, approval settings, Owner resharing, Standard-key portability, linked-family auto-approval expansion, single-file links that everyone with the link can download and may never expire, and removal that still leaves unlinked remotes; refuse any contract where the operator still has to reconstruct `who outside governance may still hold, forward, or remember this?` from scattered sharing articles.
    3. Adds one new **Resilio evaluation** document focused on why current remedy-hardening-attestation-egress-governance truth is still too fragmented to clone even though the ingredients are useful.
    4. Adds five new **interface specs** for remedy-hardening-attestation-egress-governance contract sheet, review, proof, timeline, and lineage receipt.
    5. Makes one hard product decision explicit: **governed-world resurrection resistance is weaker than explicit egress-governance accounting.**
    6. Makes another hard product decision explicit: **named direct-recipient closure is weaker than downstream-recipient-tree closure, and downstream-recipient-tree closure is weaker than an honestly owned off-world memory ceiling.**
    7. Makes a third hard product decision explicit: **link expiry, permission downgrade, or owner revocation must never impersonate byte recall, off-world forgetting, or global extinction.**
    8. Packages the result as another continuation archive whose new tranche makes the `historical egress lane / recipient-knownness class / onward-share authority / revocation reach / off-world memory ceiling / blocked global sentence / receipt` seam explicit in the reading order and page family.

    New docs in this tranche:

    - `1900-resilio-remedy-hardening-attestation-egress-governance-recipient-knownness-onward-sharing-and-off-world-memory-ceiling-evaluation.md`
    - `1901-remedy-hardening-attestation-egress-governance-contract-sheet-page-share-lanes-recipient-knownness-and-off-world-ceiling-interface-spec.md`
    - `1902-remedy-hardening-attestation-egress-governance-review-page-who-might-still-hold-or-reshare-this-outside-governance-interface-spec.md`
    - `1903-remedy-hardening-attestation-egress-governance-proof-page-share-lanes-recipient-rights-and-global-forgetting-floor-interface-spec.md`
    - `1904-remedy-hardening-attestation-egress-governance-timeline-page-link-issue-approval-forward-expiry-and-externalization-events-interface-spec.md`
    - `1905-remedy-hardening-attestation-egress-governance-lineage-receipt-page-governed-cohort-ceiling-and-blocked-global-sentences-interface-spec.md`

''').strip() + '\n\n\n'

readme_path = root / 'README.md'
readme_path.write_text(readme_addendum + readme_path.read_text())

sources_addendum = dedent('''
    ## rev0460 source set — remedy hardening attestation egress governance, recipient knownness, and off-world memory ceiling

    The most load-bearing source set for this pass was:

    - Resilio's current `Link structure and flow` article, which still says sharing commonly travels by a link and the receiving peer uses the temporary key in that link to request access from the owner.
    - Resilio's current `Sync Share Dialog (Desktop)` article, which still says links can be copied to clipboard or sent through e-mail and messenger, approval can be required for only new peers or all peers, unchecked approval lets a peer who gets the link connect and start syncing automatically, and Advanced-folder Owners can share with other peers.
    - Resilio's current `What's the difference between Standard and Advanced folders?` article, which still says Standard-folder peers can share the key they have without any limitations.
    - Resilio's current `User Management` article, which still says Owners can invite new users to the folder and that all linked devices under one identity act as Owners.
    - Resilio's current `Sync Private Identity & Linking My Devices` article, which still says once a remote user approves one device they can choose to auto-approve all linked devices for future sharing.
    - Resilio's current `Sharing single file` article, which still says everyone who gets the generated link can download the shared files, there is no option to restrict usage count or ban some devices, recipients can share the files further, and expiration can be disabled so the link never expires.
    - Resilio's current `Comprehensive guide to syncing (Desktop-Desktop)` article, which still says keys or links can simply be copied to clipboard and sent using any convenient and trusted way.
    - Resilio's current `Disconnecting and Removing Folders` article, which still says removal from linked devices may still leave the folder on remote devices not linked to the personal identity.

    Those sources were enough to tighten the line again:

    - current Resilio still deserves credit for candid externalization ingredients
    - but current Resilio still answers `who outside governance may still hold, forward, or remember this, and what global sentence is still honest?` too diffusely
    - AnonSync should therefore prefer explicit remedy-hardening-attestation-egress-governance sheets, egress-governance reviews, egress-governance proofs, egress-governance timelines, and durable egress-governance lineage receipts over overloaded share-dialog, key, link, permission, and removal language

    Primary sources:

    - Link structure and flow
      https://help.resilio.com/hc/en-us/articles/204754739-Link-structure-and-flow

    - Sync Share Dialog (Desktop)
      https://help.resilio.com/hc/en-us/articles/204790709-Sync-Share-Dialog-Desktop

    - What's the difference between Standard and Advanced folders?
      https://help.resilio.com/hc/en-us/articles/204754679-What-s-the-difference-between-Standard-and-Advanced-folders

    - User Management
      https://help.resilio.com/hc/en-us/articles/205471375-User-Management

    - Sync Private Identity & Linking My Devices
      https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

    - Sharing single file
      https://help.resilio.com/hc/en-us/articles/115000401010-Sharing-single-file

    - Comprehensive guide to syncing (Desktop-Desktop)
      https://help.resilio.com/hc/en-us/articles/204754939-Comprehensive-guide-to-syncing-Desktop-Desktop

    - Disconnecting and Removing Folders
      https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders


''').strip() + '\n\n\n'

sources_path = docs / 'sources.md'
sources_path.write_text(sources_addendum + sources_path.read_text())
