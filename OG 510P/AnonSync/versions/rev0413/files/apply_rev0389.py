from pathlib import Path

root = Path(__file__).resolve().parent
docs = root / 'docs'


def write(name: str, content: str):
    (docs / name).write_text(content.strip() + '\n', encoding='utf-8')


def prepend(path: Path, text: str):
    old = path.read_text(encoding='utf-8')
    path.write_text(text.strip() + '\n\n' + old, encoding='utf-8')

new_files = {
'1474-resilio-certification-publication-audience-reliance-and-recall-fragmentation-evaluation.md': '''
# Resilio certification publication, audience reliance, and recall fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- settle return-delta debt
- converge a cohort without lying about stragglers
- certify bounded estate scope with explicit exclusions
- publish freshness and revocation truth for the stronger estate sentence

What it still lacked was the next ordinary operator answer:

> now that we can certify something, who exactly may rely on that sentence, what exact version of the sentence is safe for each audience, and how do we supersede or recall that claim later?

That is the seam this pass locks.
A certification object is not self-executing.
It becomes operational only when it is **published for reliance**.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose the raw ingredients an operator would use when trying to publish a trustable status update or handoff packet:

- `Sync Main View (Desktop)` still says the main UI exposes filter/search controls, a 30-day History lane, and settings/license details from the side menu. So ordinary operational truth is partly living in the UI.
- The same main-view article still says operators can enable or disable columns and inspect peer counts. So some audience-facing summary material already exists, but only as configurable UI state.
- `Collecting debug logs automatically` still says debug logging may be enabled from Preferences/Settings > Advanced, that Sync should be restarted to ensure logging is enabled, and that logs should collect for at least 15 minutes after reproducing the issue. That means some handoff-worthy evidence exists only after a staged capture ritual.
- `Collecting debug logs manually` still says technical support is available only for Sync Business customers and that Sync v3 users should instead rely on the forum and Help Center for functionality questions, with a separate web form for payments and licensing. So the correct destination for a packet already differs by audience and product posture.
- The same manual log article still says log paths vary across desktop, service, LocalService, Local System, Linux current-directory / storage-path, package installs, NAS, and Android. So a single `send the logs` instruction is not actually one stable publication lane.
- `Collecting crash reports, mini-dumps and core dumps` and `Where to collect logs on NAS?` still make crash and log artifact gathering platform-specific and support-lane-dependent. So not all evidence packets are created the same way.
- `Settings on mobile platforms` still documents a distinct Support section that links to Help Center articles, Sync Forum, and the contact-support form, and a distinct About section that shows the installed build/version. So mobile already separates support lane and build witness, but not as one unified reliance packet.
- `Running Sync in configuration mode` still says config mode is helpful for applying the same settings to many machines and that non-default `storage_path` creates new settings there. That means a handoff packet that ignores which world it came from can overclaim continuity.
- `Sync Private Identity & Linking My Devices` still warns against linking v2 and v3 devices because they may conflict on applied license and lose access to UI and share configuration. So even audience handoff across apparently related devices needs a version and world warning.

## What current Resilio still gets right

### 1) It exposes several real evidence planes

Main UI status, history, About/build/version surfaces, debug logs, crash artifacts, and support/contact routes are all real and worth borrowing.

### 2) It is candid that audience and lane matter

Business-support customers, Sync v3 self-serve users, desktop operators, mobile operators, and NAS operators do not all follow the same route.
That is important.

### 3) It preserves platform/world specificity

Service principals, config storage roots, NAS paths, and mobile settings all remind us that a published statement without world attribution can be misleading.

## Where current Resilio still fragments the operator answer

### A) There is no canonical publication object

Resilio gives the operator history, columns, logs, builds, crash dumps, forum routes, and support forms.
What it still does not give is one first-class object answering:

- which audience this packet is for
- which exact sentence that audience may rely on
- what exclusions and freshness ride with that sentence
- what evidence payload is attached versus merely referenced
- how supersession and recall will reach that audience later

### B) There is no explicit claim-envelope downgrade by audience

A working operator may be able to read nuanced status from the UI and support artifacts.
An executive, auditor, partner, or successor operator often cannot or should not receive the exact same envelope.
Current Resilio exposes the sources, but it still leaves the downgrade logic to operator folklore.

### C) There is no durable recall/supersession chain

The product exposes logs, builds, and support lanes, but not one durable answer to:

- which published statement is still current
- which newer packet supersedes an older one
- who has acknowledged the newer one
- what happens when an older forwarded screenshot or exported note keeps circulating after revocation

## Hard product decision unlocked by this pass

AnonSync should not let `estate certified` impersonate `safe for reliance by all audiences`.
It should promote any material publication of a stronger state claim into a first-class **reliance charter** that separately expresses:

- target audience
- safe claim envelope for that audience
- required inclusions and forbidden omissions
- freshness and supersession rule
- recall channel and acknowledgement state
- stronger blocked sentence that the packet must not imply

## Replacement line for AnonSync

Borrow from Resilio:

- candor that real evidence spans UI state, logs, builds, crash artifacts, and support lanes
- honesty that platform, world, and support posture matter to what a packet means
- separation of build/version witness from generic troubleshooting text

Do not clone from Resilio:

- any workflow where publication remains an improvised combination of screenshots, copied build strings, forum notes, and log attachments
- any contract where audience-specific claim downgrades are implicit rather than explicit
- any product shape where supersession and recall of earlier packets are tribal knowledge

AnonSync should instead ship explicit pages for:

- reliance charter contract sheet
- certification publication review
- reliance proof
- reliance timeline
- reliance lineage receipt
''',
'1475-reliance-charter-contract-sheet-page-audience-claim-envelope-and-recall-channel-interface-spec.md': '''
# Reliance charter contract sheet page: audience, claim envelope, and recall channel interface spec

## Purpose

After the archive learned how to certify bounded estate scope, it still needed one ordinary page for the next operator question:

> which audience is this certification being published to, what exact sentence may they rely on, and how will we retract or supersede it later?

## Core decision

AnonSync must expose one first-class **Reliance charter contract sheet** whenever a certification, campaign result, or incident closure is being published for someone else to act on.

## Fixed page order

1. **Publication header**
2. **Audience-and-intent card**
3. **Claim-envelope card**
4. **Attached-evidence card**
5. **Recall-and-supersession card**
6. **Decision sentence**

### 1) Publication header

Show:

- reliance charter id
- source estate certification id
- source campaign / case ids
- publication owner
- publication time
- live status
- latest superseding charter id if any
- strongest currently safe audience sentence

Supported `live_status` values:

- `drafting`
- `ready-to-publish`
- `published-active`
- `published-bounded`
- `published-superseded`
- `published-recalled`
- `expired`
- `retired`

Hard rule:

A certification is not considered published just because it exists internally.
A reliance charter is required once a different audience may act on the claim.

### 2) Audience-and-intent card

Required rows:

- target audience class
- intended decision enabled by this packet
- action the audience may take
- action the audience may not take
- acknowledgement required
- delivery channel

Supported `target_audience_class` values:

- `working-operator`
- `successor-operator`
- `incident-commander`
- `executive-reader`
- `auditor`
- `external-partner`
- `customer-facing`
- `mixed-explicit-list`

Supported `acknowledgement_required` values:

- `none`
- `receipt-only`
- `read-and-understood`
- `delegated-custody-accepted`
- `counter-sign-required`

Hard rule:

`all stakeholders` is illegal unless every recipient class shares the same permitted actions and blocked stronger sentence.

### 3) Claim-envelope card

Required rows:

- safe sentence for this audience
- unsafe overclaim to suppress
- certified scope carried into packet
- exclusions that must be shown
- freshness window carried into packet
- claim ceiling for stale copies

Supported `claim_ceiling_for_stale_copies` values:

- `none`
- `historical-context-only`
- `receipt-of-past-status-only`
- `may-trigger-manual-recheck`

Hard rule:

A packet may not omit exclusions or freshness merely because the source certificate already contains them.
If the audience can act on the packet, those truths must travel with it.

### 4) Attached-evidence card

Required rows:

- evidence summary included inline
- linked live certificate
- linked timeline / receipt ids
- attached artifacts included
- platform or world attribution
- evidence omitted on purpose

Supported `attached_artifacts_included` classes:

- `none`
- `summary-only`
- `certificate-and-receipt`
- `certificate-receipt-and-artifacts`
- `redacted-artifact-pack`

Hard rule:

A screenshot or copied sentence cannot impersonate a complete packet if it lacks live certificate link, scope, exclusions, freshness, or world attribution.

### 5) Recall-and-supersession card

Required rows:

- supersession trigger
- recall trigger
- recall channel
- who must receive recall
- stale-forward risk class
- unacknowledged-recipient count

Supported `recall_channel` values:

- `same-thread-update`
- `same-dashboard-live-link`
- `ticket-comment-and-alert`
- `operator-page-inbox`
- `mixed-explicit`

Supported `stale_forward_risk_class` values:

- `low`
- `moderate`
- `high`
- `severe`

Hard rule:

A packet is incomplete if it says what is true now but not how later revocation or supersession will reach the recipient.

### 6) Decision sentence

Use:

> Publish to [audience] with [safe sentence]. Include [required inclusions]. Suppress [unsafe overclaim]. Recall via [channel] on [trigger].

If blocked, use:

> Do not publish yet. The audience-safe packet is blocked by [missing element], so only [weaker internal sentence] is currently allowed.
''',
'1476-certification-publication-review-page-operator-exec-audit-and-successor-handoff-variants-interface-spec.md': '''
# Certification publication review page: operator, executive, audit, and successor-handoff variants interface spec

## Purpose

This review page helps the operator choose the correct publication variant instead of reusing one packet for audiences with different decision rights.

## Review question

> what exact version of the certification is safe for this audience to rely on, and what must be downgraded, hidden, or made explicit before publication?

## Fixed review branches

1. **Working-operator branch**
2. **Executive branch**
3. **Audit branch**
4. **Successor-operator handoff branch**
5. **External partner / customer branch**
6. **No-safe-publication branch**

### 1) Working-operator branch

Show:

- active certification sentence
- exact scope and exclusions
- freshness and revocation triggers
- linked receipts, timelines, and open blockers
- next permitted operational action
- next forbidden overclaim

Use when the audience may perform follow-on operational decisions.

### 2) Executive branch

Show:

- bounded high-level sentence
- why the sentence is bounded
- explicit exclusions summarized compactly
- freshness horizon
- required follow-up owner
- no raw log or forensic detail by default

Hard rule:

An executive packet may compress detail, but it may not widen the claim envelope.

### 3) Audit branch

Show:

- precise certified scope
- exclusions and why they are excluded
- evidence lineage ids
- witness freshness basis
- revocation and supersession chain
- redaction note if artifacts are withheld

Hard rule:

An audit packet may never rely only on dashboard prose.
It must include traceable lineage identifiers.

### 4) Successor-operator handoff branch

Show:

- working-operator packet fields
- unresolved obligations
- recall obligations still active
- next rereview time
- world attribution and path / service / config caveats
- stale packet handling instructions

Hard rule:

`shared for awareness` is weaker than `delegated custody accepted`.
The handoff branch must keep that difference explicit.

### 5) External partner / customer branch

Show:

- narrow safe sentence
- explicit service or data-impact implication
- actions the audience may take now
- actions still blocked
- how they will be told if the sentence is recalled

Hard rule:

This branch must never leak a stronger internal sentence just because internal operators can tolerate nuance.

### 6) No-safe-publication branch

Use when any of the following is true:

- source certification is not active
- exclusions are not yet explicit
- freshness already failed
- recall channel is missing
- world attribution is unknown
- the audience wants a stronger claim than the evidence allows

Decision sentence:

> No audience-safe publication yet. Keep this as internal operator truth only until [missing requirement] is satisfied.

## Cross-branch invariants

- one audience packet may not silently impersonate another
- stronger source truth may be deliberately downgraded, but weaker packets may not imply stronger source truth
- every published packet must name its supersession source
- every packet must preserve at least one explicit `do not infer` sentence
''',
'1477-reliance-proof-page-published-claims-obligations-and-supersession-interface-spec.md': '''
# Reliance proof page: published claims, obligations, and supersession interface spec

## Purpose

This page proves that a charter was actually published, to whom, with which safe sentence, and with what ongoing obligations.

## Core decision

Publishing a packet is a state change with its own proof burden.
Receipt, acknowledgement, delegated custody, and supersession are different truths.

## Required sections

### Publication proof

Show:

- publication channel actually used
- publication time
- recipients reached
- packet variant used
- linked live source certificate
- included exclusions and freshness badge

### Recipient state

Show counts for:

- delivered
- viewed
- acknowledged-receipt
- acknowledged-understanding
- delegated-custody-accepted
- recall-pending

Hard rule:

A green `sent` badge is weaker than audience reliance.
The page must never collapse transport success into decision-safe receipt.

### Active obligations

Show:

- rereview or renewal date inherited from source
- active recall obligations
- who must be notified on supersession
- who still holds stale copies
- whether the packet remains live-linked or snapshot-only

Supported `packet_linkage_class` values:

- `live-linked`
- `snapshot-with-live-pointer`
- `detached-snapshot`
- `redacted-detached-snapshot`

Hard rule:

Detached snapshots automatically cap the claim ceiling lower than live-linked packets.

### Supersession section

Show:

- superseding charter id
- supersession reason
- whether recipients were republished automatically
- stale packet treatment
- surviving weaker sentence for old packet holders

Supported `supersession_reason` values:

- `fresher-proof`
- `scope-change`
- `revocation-event`
- `audience-rebucket`
- `redaction-correction`
- `claim-downgrade`

Decision sentence:

> This packet is active for [audience] at [claim envelope]. It remains safe only until [freshness / trigger]. Supersede or recall through [channel] if [event].
''',
'1478-reliance-timeline-page-publication-acknowledgement-supersession-and-recall-events-interface-spec.md': '''
# Reliance timeline page: publication, acknowledgement, supersession, and recall events interface spec

## Purpose

This timeline preserves the life of a published claim after it leaves the internal operator workspace.

## Event classes

- `draft-created`
- `published`
- `delivery-confirmed`
- `receipt-acknowledged`
- `custody-accepted`
- `packet-forwarded`
- `freshness-nearing-expiry`
- `superseded`
- `recalled`
- `recipient-still-unacknowledged`
- `stale-copy-detected`
- `retired`

## Each event row must show

- event time
- actor
- audience class affected
- claim envelope at that time
- whether exclusions were visible
- whether freshness was still valid
- new obligation created
- stronger blocked sentence still blocked or newly unblocked

## Special render rules

### Packet forwarded

If the system knows a packet was forwarded or exported beyond the original recipient set, show:

- original audience
- downstream audience if known
- whether the downstream packet preserved exclusions and freshness
- stale-forward risk upgrade

Hard rule:

Forwarding never inherits a stronger claim ceiling by default.

### Superseded

When a packet is superseded, keep both:

- new active charter pointer
- old packet's surviving historical meaning

Hard rule:

`Superseded` does not mean `never existed`.
The timeline must still preserve what action the old packet safely enabled at the time.

### Recalled

When recalled, show:

- recall trigger
- audience notified so far
- recipients still pending notice
- weaker sentence that survives until confirmation

Hard rule:

Recall completion is not the same as recall issued.

## Decision sentence

Use:

> This published claim entered the world at [time], enabled [audience action], and is now [active/superseded/recalled]. Remaining live obligations: [list].
''',
'1479-reliance-lineage-receipt-page-audience-envelope-freshness-and-recall-boundary-interface-spec.md': '''
# Reliance lineage receipt page: audience envelope, freshness, and recall boundary interface spec

## Purpose

This receipt tells the next operator exactly what was published, to whom, with what safe sentence, and what later invalidated or superseded it.

## Required fields

- reliance charter id
- source certification id
- source proof ids
- audience class
- packet variant
- safe published sentence
- explicit exclusions carried
- freshness window carried
- delivery channel
- acknowledgement class reached
- live-link or snapshot class
- superseding charter if any
- recall boundary
- blocked stronger sentence

## Receipt footer sentence

Use:

> On [time], [safe sentence] was published to [audience] via [channel] as a [packet class]. It remained safe through [freshness / trigger] and was [superseded/recalled/retired] by [event]. The blocked stronger sentence stayed: [sentence].

## Hard rules

- the receipt must survive even after the packet is superseded
- a recalled packet still needs lineage, not silent disappearance
- the receipt must preserve whether recipients only received, acknowledged, or accepted custody
- the receipt must preserve whether the packet was live-linked or detached snapshot
- the receipt must tell the next operator what weaker sentence old packet holders may still believe unless recall is confirmed
''',
}

for name, content in new_files.items():
    write(name, content)

prepend(root / 'README.md', '''
## Revision addendum after rev0388 — certification publication, audience reliance, and recall truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **publication for reliance**.
It does eight things in one tranche:

1. Continues the archive after rev0388 with a new page family centered on who may safely act on a certification.
2. Tightens the non-clone line again: borrow Resilio's candor that UI state, history, build/version surfaces, debug logs, crash artifacts, support/forum lanes, mobile support, NAS log paths, config worlds, and mixed-version/device-world warnings are different evidence ingredients; refuse any contract where the operator still has to reconstruct `what exact sentence is safe for this audience to rely on, and how do we supersede or recall it later?` from several pages and ad hoc packets.
3. Adds one new **Resilio evaluation** document focused on why current publication and audience-reliance truth is still too fragmented to clone even though the evidence ingredients are useful.
4. Adds five new **interface specs** for reliance charter contract sheet, publication review, reliance proof, reliance timeline, and reliance lineage receipt.
5. Makes one hard product decision explicit: **a certificate is not self-executing; it becomes operational only through an audience-specific reliance charter.**
6. Makes another hard product decision explicit: **delivery, receipt, understanding, delegated custody, supersession, and recall are different public truths.**
7. Makes a third hard product decision explicit: **a stale forwarded snapshot is weaker than a live-linked packet, and `sent` is weaker than `safe to rely on`.**
8. Packages the result as another continuation archive whose new tranche makes the `audience / claim-envelope / publication-review / reliance-proof / recall-receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1474-resilio-certification-publication-audience-reliance-and-recall-fragmentation-evaluation.md`
- `1475-reliance-charter-contract-sheet-page-audience-claim-envelope-and-recall-channel-interface-spec.md`
- `1476-certification-publication-review-page-operator-exec-audit-and-successor-handoff-variants-interface-spec.md`
- `1477-reliance-proof-page-published-claims-obligations-and-supersession-interface-spec.md`
- `1478-reliance-timeline-page-publication-acknowledgement-supersession-and-recall-events-interface-spec.md`
- `1479-reliance-lineage-receipt-page-audience-envelope-freshness-and-recall-boundary-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's publication-for-reliance contract**

This time the reason is especially clear around **UI summary state, 30-day history, version/about witness, debug-log capture rituals, crash/core-dump collection, support-lane splits, mobile support surfaces, config-world attribution, and mixed-version handoff warnings**.
Current official materials simultaneously show that:

- current `Sync Main View (Desktop)` docs still say the UI exposes filters, search, columns, a 30-day History lane, and settings/license details
- current `Collecting debug logs automatically` docs still say debug capture may require enablement, restart, and at least 15 minutes of post-repro collection
- current `Collecting debug logs manually` docs still say Business customers have direct technical support while Sync v3 users are pushed toward the forum / Help Center plus a separate payments/licensing form
- the same manual log docs still say artifact locations vary across desktop, service principals, Linux storage paths, NAS, and Android
- current `Collecting crash reports, mini-dumps and core dumps` and `Where to collect logs on NAS?` docs still preserve platform-specific evidence lanes
- current `Settings on mobile platforms` docs still separate Support links from About/build witness on mobile
- current `Running Sync in configuration mode` docs still say config can apply the same settings on many machines while non-default `storage_path` creates a new settings world
- current `Sync Private Identity & Linking My Devices` docs still warn against linking v2 and v3 devices because of license/application conflicts and lost UI / share configuration access

That candor is useful.
The publication-for-reliance contract is the problem.
AnonSync should not clone a world where the operator still has to translate `dashboard looks green`, `history looks quiet`, `here are the logs`, `here is the build`, `forum vs support`, and `this came from that machine/world` into one stable answer about audience, safe sentence, exclusions, freshness, supersession, recall channel, and blocked stronger sentence by stitching together several pages and ad hoc packets.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because publication is a real contract with separate truths for audience, claim envelope, evidence payload, freshness, supersession, and recall, but the present contract still scatters the answer to `what exact sentence is safe for this audience to rely on, and how do we retract or supersede it later?` across several KB articles and improvised evidence packets instead of owning it as one stable page family.**
''')

prepend(docs / '00-status.md', '''
## Revision addendum — certification publication, audience reliance, and recall truth after rev0388

This tranche locks the next seam around **publication-for-reliance truth**.
The key decisions now made explicit in the archive are:

- **reliance charter is a first-class contract object rather than a side effect of an existing certificate**
- **audience class, safe claim envelope, attached evidence, freshness, supersession, and recall remain separate truths**
- **`sent` is weaker than `received`, `received` is weaker than `understood`, and `understood` is weaker than `delegated custody accepted`**
- **live-linked packets remain visibly stronger than detached snapshots or forwarded stale copies**
- **every serious published claim now needs one receipt that preserves who it was for, what exact sentence it allowed, what exclusions traveled with it, when it staled, and what event recalled or superseded it**

New docs added in this tranche:

- `1474-resilio-certification-publication-audience-reliance-and-recall-fragmentation-evaluation.md`
- `1475-reliance-charter-contract-sheet-page-audience-claim-envelope-and-recall-channel-interface-spec.md`
- `1476-certification-publication-review-page-operator-exec-audit-and-successor-handoff-variants-interface-spec.md`
- `1477-reliance-proof-page-published-claims-obligations-and-supersession-interface-spec.md`
- `1478-reliance-timeline-page-publication-acknowledgement-supersession-and-recall-events-interface-spec.md`
- `1479-reliance-lineage-receipt-page-audience-envelope-freshness-and-recall-boundary-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `we certified it` can no longer hide who is actually allowed to rely on which sentence
- audience downgrades now stay visibly separate from source truth so executive, audit, partner, and successor-operator packets cannot silently widen or flatten claims
- stale screenshots, forwarded exports, and detached snapshots now stay visibly weaker than live-linked packets
- supersession and recall now become first-class lifecycle events instead of buried follow-up chatter
- later operators can open one receipt and see what was published, to whom, with what ceiling, and what weaker sentence old packet holders may still retain unless recall is confirmed
''')

prepend(docs / '10-resilio-sync-evaluation.md', '''
## Revision addendum — Resilio publication-for-reliance evaluation after rev0388

Another current official Resilio pass still supports the same tightened judgment:

- **borrow Resilio's evidence candor**
- **do not clone Resilio's publication-for-reliance contract**

This time the key evidence cluster is:

- `Sync Main View (Desktop)` still exposes search, columns, peer counts, settings/license details, and a 30-day History lane
- `Collecting debug logs automatically` still requires enablement, restart, issue reproduction, and a post-repro collection window
- `Collecting debug logs manually` still splits Business direct support from Sync v3 forum / Help Center + payments/licensing form routes
- the same log docs still make artifact location depend on platform, service principal, and storage-path world
- `Collecting crash reports, mini-dumps and core dumps` and `Where to collect logs on NAS?` still keep crash/log evidence in platform-specific lanes
- `Settings on mobile platforms` still separates Support routing from About/build witness
- `Running Sync in configuration mode` still keeps many-machine configuration and new-world `storage_path` truth in a separate article
- `Sync Private Identity & Linking My Devices` still warns that linking v2 and v3 devices can conflict on license and lose UI / share configuration access

So current Resilio still deserves credit for exposing many real evidence ingredients.
But it still does not own one operator-facing answer to:

> what exact sentence is safe for this audience to rely on, what exclusions and freshness travel with it, and how do we supersede or recall that packet later?

That is the product gap this tranche makes explicit.
''')

prepend(docs / '11-resilio-borrow-line-and-non-clone-scorecard.md', '''
## Revision addendum — borrow line after rev0388: publication-for-reliance truth

### Borrow from Resilio

- keep build/version witness, UI summary state, logs, crash artifacts, and support-lane posture visibly distinct
- stay candid that platform, world, and version posture affect what a packet really means
- preserve that business-support versus self-serve/forum posture is a real routing difference

### Do not clone from Resilio

- do not make operators improvise audience packets from screenshots, copied build strings, and log attachments
- do not let one certification packet silently serve executive, audit, partner, and successor-operator audiences at once
- do not let supersession and recall live only in chat/thread folklore
- do not let stale forwarded snapshots impersonate live current truth

### New non-clone score

This seam remains **do not clone** because the raw ingredients are useful but the publication contract is still too diffuse.
AnonSync should ship explicit reliance charters, publication reviews, reliance proofs, timelines, and lineage receipts.
''')

prepend(docs / '12-resilio-interface-clone-veto-tests-and-page-obligations.md', '''
## Revision addendum — clone-veto obligations for publication-for-reliance after rev0388

### New veto seam

A sync product fails the clone test on this seam if it cannot answer, in one operator-facing workflow:

- which audience this packet is for
- what exact safe sentence that audience may rely on
- what exclusions and freshness travel with the packet
- what evidence is attached versus merely referenced
- what stronger sentence must still be suppressed
- what supersedes the packet later
- how recall reaches recipients still holding stale copies

### New page obligations

This seam adds five more page obligations:

1. a **reliance charter contract sheet** that preserves audience, claim envelope, exclusions, freshness, evidence payload, and recall channel
2. a **certification publication review** that separates working-operator, executive, audit, successor-handoff, and no-safe-publication branches
3. a **reliance proof** that records delivery, acknowledgement class, live-link versus snapshot class, and supersession posture
4. a **reliance timeline** that preserves publication, forward, acknowledgement, supersession, and recall events
5. a **reliance lineage receipt** that tells the next operator what was published, to whom, with what ceiling, and what weaker sentence may still survive in stale copies

### Explicit clone vetoes

Do not clone any contract where:

- a certificate is assumed to be safe for all audiences without an audience-specific packet
- exclusions or freshness disappear in executive or partner variants
- `sent` is treated as `safe to rely on`
- stale forwarded snapshots can masquerade as live truth
- supersession or recall is not first-class product state
- the next operator cannot tell what a stale packet holder may still believe unless recall is confirmed
''')

prepend(docs / '20-product-direction.md', '''
## Product-direction addendum after rev0388 — publication for reliance is first-class

AnonSync should not let internal certification truth stand in for safe audience reliance.
The product direction is now explicit:

- **publication for reliance is first-class**
- **audience, claim envelope, evidence payload, freshness, supersession, and recall remain separate**
- **delivery is weaker than receipt**
- **receipt is weaker than delegated reliance**
- **detached snapshots remain visibly weaker than live-linked packets**

That means future interface work should keep one stable family for:

- audience class
- safe sentence envelope
- required inclusions and explicit exclusions
- packet linkage class
- supersession / recall channel
- stale-copy downgrade and surviving weaker sentence

The product should never force the operator to infer those truths from a screenshot, an email forward, a copied build string, or a generic `status shared` badge.
''')

prepend(docs / 'sources.md', '''
## rev0389 source set — certification publication, audience reliance, and recall truth

The most load-bearing source set for this pass was:

- Resilio's current `Sync Main View (Desktop)` article, which still says the desktop UI exposes search, filters, customizable columns, a 30-day History lane, and settings/license details.
- Resilio's current `Collecting debug logs automatically` article, which still says debug logging may need to be enabled, Sync restarted, the issue reproduced, and logs collected for at least 15 minutes afterward.
- Resilio's current `Collecting debug logs manually` article, which still says direct technical support is available only for Sync Business customers while Sync v3 users should use the forum / Help Center for functionality questions and a separate web form for payments/licensing.
- The same manual log article, which still says log paths differ across desktop, service principals, Linux current-directory / storage_path worlds, NAS, and Android.
- Resilio's current `Collecting crash reports, mini-dumps and core dumps` article and `Where to collect logs on NAS?` article, which still keep platform-specific artifact capture and support-lane reality visible.
- Resilio's current `Settings on mobile platforms` article, which still separates Support routing from About/build witness on mobile.
- Resilio's current `Running Sync in configuration mode` article, which still says config mode is useful for applying the same settings across many machines and that non-default `storage_path` creates new settings there.
- Resilio's current `Sync Private Identity & Linking My Devices` article, which still warns that linking v2 and v3 devices may create license conflicts and lost UI / share configuration access.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for exposing several real evidence and support-routing ingredients
- but current Resilio still answers `what exact sentence is safe for this audience to rely on, and how do we supersede or recall it later?` too diffusely
- AnonSync should therefore prefer explicit reliance charters, publication reviews, reliance proofs, reliance timelines, and durable lineage receipts over improvised screenshot / log / note packets

Primary sources:

- Sync Main View (Desktop)
  https://help.resilio.com/hc/en-us/articles/204755009-Sync-Main-View-Desktop

- Collecting debug logs automatically
  https://help.resilio.com/hc/en-us/articles/360019430539-Collecting-debug-logs-automatically

- Collecting debug logs manually
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

- Collecting crash reports, mini-dumps and core dumps
  https://help.resilio.com/hc/en-us/articles/206214615-Collecting-crash-reports-mini-dumps-and-core-dumps

- Where to collect logs on NAS?
  https://help.resilio.com/hc/en-us/articles/205326945-Where-to-collect-logs-on-NAS

- Settings on mobile platforms
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- Running Sync in configuration mode
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Sync Private Identity & Linking My Devices
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices
''')

print('apply_rev0389 ready')
