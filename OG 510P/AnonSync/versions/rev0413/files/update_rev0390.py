from pathlib import Path

root = Path('/tmp/anonsync_cur')
docs = root / 'docs'

new_docs = {
    '1480-resilio-reliance-to-action-authority-delegation-and-recall-fragmentation-evaluation.md': '''# Resilio reliance-to-action authority, delegation, and recall fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- certify bounded estate scope
- publish an audience-safe reliance packet
- keep freshness, exclusions, supersession, and recall visible for that packet

What it still lacked was the next ordinary operator answer:

> now that someone received a packet, who is merely informed, who is allowed to decide, who is allowed to execute, who may re-delegate, and what happens to work already in motion when the packet is superseded or recalled?

That is the seam this pass locks.
A reliance packet is **not** a work order.
It becomes operational only when it is translated into an explicit **action mandate**.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose many real action-authority ingredients, but as separate sharing and approval surfaces rather than one canonical downstream-action contract:

- `Sync functionality in detail` still says folder permissions determine what a user can do with a shared folder, with three classes: Read Only, Read & Write, and Owner. It also still says permissions can be changed before, during, or after sharing, access can be revoked, and a requester’s approval can be altered at approval time. So action authority is real and mutable.
- The same functionality article still says that when devices are linked under one private identity, all linked devices act as Owners, and a folder can be shared and approval requests handled from any linked device. So action authority can expand through identity topology, not just one local button.
- `User Management` still says only users with Owner permission can invite new users, Owners also have full Read & Write permission, and peers with different identities may receive different permissions. It also still says a disconnect revokes future updates for that peer while already synchronized files remain. So the product already distinguishes between knowing, changing, sharing onward, and receiving future effects.
- `Sync Share Dialog (Desktop)` still says Advanced folders can be shared only by peers who have Owner access, whereas Standard folders have no Owner level and all peers can share the folder onward, with Read Only peers limited to sharing only a Read Only key. It also still keeps approval requirement, link expiry, and use-count limit in the share dialog. So the practical downstream authority contract changes with folder type, link mode, and security options.
- `Comprehensive guide to syncing (Desktop-Desktop)` still says manual sharing requires choosing the access mechanism (key, link, or QR), choosing the permission set for the remote device, and approving the connection if approval is required. It also still says the approver can inspect the requester’s name, IP address, fingerprint, and approval request receipt date before approving. So action enablement is already a small workflow with identity witness, not just permission labels.

## What current Resilio still gets right

### 1) It is candid that action authority is not one flat thing

Read Only, Read & Write, and Owner are genuinely different.
Approval, invitation, revoke, and onward-sharing rights differ.
That is worth borrowing.

### 2) It preserves some expiry and security truth

Link expiry, link-use limits, and approval rules all acknowledge that an authority grant can be temporary, conditional, or routed through a checkpoint.
That is useful.

### 3) It keeps folder-type and identity topology visible

Advanced versus Standard folders, linked-family ownership, and per-peer permission changes all show that the same apparent sharing action can mean different authority.
That is important.

## Where current Resilio still fragments the operator answer

### A) There is no canonical action-mandate object

Resilio gives the operator permission labels, share dialogs, approval checkpoints, requester fingerprints, and revoke/disconnect actions.
What it still does not give is one operator-facing object answering:

- whether this recipient is merely informed or actually authorized to act
- what exact action is authorized, required, or forbidden
- whether the authority may be re-delegated
- which world / scope / asset set the authority applies to
- when the mandate expires
- what supersedes or cancels work already queued or underway

### B) Reliance and authority still blur too easily

A recipient can receive a link, a packet, a status update, or a permission change.
Current Resilio exposes these ingredients, but still leaves the operator to infer whether the recipient may merely observe, approve, execute, or invite others.
That is too much ambiguity for serious downstream operations.

### C) Recall and execution cancellation are not one durable lane

Resilio can revoke access, disconnect a peer, expire a link, or require approval again.
Those are real controls.
But it still does not provide one durable product answer to:

- which already-issued instruction is still live
- which newer instruction supersedes it
- whether a recipient acknowledged the new one
- whether in-flight action must stop, continue, or complete under a weakened ceiling

## Hard product decision unlocked by this pass

AnonSync should not let `received the packet` impersonate `may act on the packet`.
It should promote any material downstream instruction into a first-class **action mandate** that separately expresses:

- recipient or actor class
- authority class
- allowed action set
- required action set
- forbidden action set
- re-delegation rights
- expiry and cancellation rule
- stronger blocked sentence the recipient must not infer

## Replacement line for AnonSync

Borrow from Resilio:

- candor that permissions, invitation rights, approval steps, and revoke flows are different things
- honesty that folder type, identity topology, and share mechanism affect what a recipient can do
- practical use of expiry, use-count limits, and requester fingerprint review before approval

Do not clone from Resilio:

- any workflow where a reliance packet quietly becomes an action order without an explicit authority object
- any contract where `can read status`, `can approve`, `can execute`, and `can re-share` are inferred from context instead of stated directly
- any product shape where superseding or canceling in-flight downstream action depends on thread folklore or human memory

AnonSync should instead ship explicit pages for:

- action mandate contract sheet
- mandate shaping review
- action authority proof
- mandate timeline
- mandate lineage receipt
''',
    '1481-action-mandate-contract-sheet-page-authority-scope-duties-and-expiry-interface-spec.md': '''# Action mandate contract sheet page: authority, scope, duties, and expiry interface spec

## Purpose

After the archive learned how to publish a reliance-safe packet, it still needed one ordinary page for the next operator question:

> does this recipient merely know something, or are they actually authorized or required to do something now?

## Core decision

AnonSync must expose one first-class **Action mandate contract sheet** whenever a certification, incident result, rollout decision, or remediation instruction is being turned into downstream action authority.

## Fixed page order

1. **Mandate header**
2. **Actor-and-authority card**
3. **Action-set card**
4. **Scope-and-preconditions card**
5. **Expiry-and-cancellation card**
6. **Decision sentence**

### 1) Mandate header

Show:

- action mandate id
- source reliance charter id
- source certificate / case / campaign ids
- issuing authority
- mandate owner
- issue time
- live status
- strongest currently safe action sentence

Supported `live_status` values:

- `drafting`
- `ready-to-issue`
- `issued-pending-acceptance`
- `issued-active`
- `issued-bounded`
- `superseded`
- `cancelled`
- `expired`
- `retired`

Hard rule:

A reliance charter may inform a recipient without granting action rights.
An action mandate is required once the recipient may approve, execute, or re-delegate work.

### 2) Actor-and-authority card

Required rows:

- target actor class
- named recipient or cohort
- authority class
- may re-delegate
- acceptance required
- source of authority

Supported `target_actor_class` values:

- `observer`
- `approver`
- `executor`
- `delegate-manager`
- `incident-commander`
- `successor-operator`
- `mixed-explicit-list`

Supported `authority_class` values:

- `inform-only`
- `observe-and-report`
- `approve-or-block`
- `execute-bounded`
- `execute-and-escalate`
- `execute-and-redelegate`
- `custodial-handoff-only`

Supported `acceptance_required` values:

- `none`
- `receipt-only`
- `accept-duty`
- `counter-sign-required`
- `dual-control-required`

Hard rule:

A role label like `operator` or `owner` is too weak by itself.
The mandate must say whether the recipient may observe, approve, execute, escalate, or re-delegate.

### 3) Action-set card

Required rows:

- allowed actions
- required actions
- forbidden actions
- optional actions needing recheck
- post-action proof expected
- stronger blocked overclaim

Supported `post_action_proof_expected` values:

- `none`
- `receipt-of-attempt`
- `execution-with-witness`
- `execution-and-outcome-proof`
- `execution-outcome-and-reconciliation-proof`

Hard rule:

A mandate must name both what the recipient may do and what they must not do.
`use your judgment` is illegal when the stronger sentence depends on bounded action.

### 4) Scope-and-preconditions card

Required rows:

- asset / scope covered
- excluded scope
- world / lane / platform boundary
- preconditions before action
- blocked-if conditions
- freshness dependency

Supported `freshness_dependency` values:

- `none`
- `must-be-current-at-start`
- `must-be-current-at-each-checkpoint`
- `expires-on-source-supersession`

Hard rule:

A mandate cannot float free of the world it was issued for.
If scope, platform, world, or preconditions differ, the authority must narrow accordingly.

### 5) Expiry-and-cancellation card

Required rows:

- expiry rule
- superseding event
- cancellation event
- in-flight action rule on cancel
- stale-copy risk class
- recall / cancel channel

Supported `in_flight_action_rule_on_cancel` values:

- `stop-immediately`
- `finish-current-step-then-hold`
- `complete-bounded-safe-close`
- `escalate-for-human-decision`

Supported `stale_copy_risk_class` values:

- `low`
- `moderate`
- `high`
- `severe`

Hard rule:

A mandate is incomplete if it says how to start but not how to stop when the source truth is superseded or recalled.

### 6) Decision sentence

Use:

> Issue mandate to [actor] with authority [class]. Allow [allowed actions]. Require [required actions]. Forbid [forbidden actions]. Cancel via [channel] on [event].

If blocked, use:

> Do not issue action authority yet. The recipient may currently rely only at [weaker level] because [missing authority element] blocks safe execution.
''',
    '1482-mandate-shaping-review-page-inform-observe-decide-execute-and-escalate-routing-interface-spec.md': '''# Mandate shaping review page: inform, observe, decide, execute, and escalate routing interface spec

## Purpose

Operators need one page that answers:

> given this packet and this recipient, are we informing them, asking them to watch, asking them to approve, asking them to execute, or asking them to take custody and route further?

## Core decision

AnonSync must separate downstream action into typed routes instead of letting one generic `notify` or `assign` verb carry too much meaning.

## Fixed page order

1. **Source summary rail**
2. **Recipient routing matrix**
3. **Action-authority conflict review**
4. **Cancellation and supersession review**
5. **Decision footer**

### 1) Source summary rail

Show:

- source reliance charter
- source certificate / case / campaign
- source safe sentence
- source blocked stronger sentence
- source freshness state
- source recall posture

Hard rule:

No route may be stronger than the source charter permits.

### 2) Recipient routing matrix

Each candidate recipient row must show:

- recipient / cohort
- chosen route
- why this route and not a stronger one
- acceptance class
- evidence payload carried
- first required checkpoint

Supported `chosen_route` values:

- `inform-only`
- `watch-and-report`
- `approve-or-block`
- `execute-bounded-step`
- `execute-sequence`
- `take-custody-and-redelegate`
- `no-safe-route`

Hard rule:

A recipient cannot land on `execute` if they only have reliance truth but no bounded authority.

### 3) Action-authority conflict review

Show conflicts for:

- source claim too weak for requested route
- actor role too broad or too vague
- recipient has technical reach but no delegated authority
- recipient has authority but lacks prerequisites
- re-delegation would escape source scope
- world / platform mismatch

Supported `conflict_outcome` values:

- `downgrade-to-inform`
- `downgrade-to-watch`
- `split-route`
- `require-counter-sign`
- `block-route`

Hard rule:

Technical ability does not grant action authority.
Operational seniority does not erase preconditions.

### 4) Cancellation and supersession review

Required rows:

- active superseding sources that would cancel this route
- stale-copy exposure risk
- recipients with queued work but no live link
- in-flight cancellation behavior
- recall acknowledgement gap
- human escalation fallback

Hard rule:

AnonSync must show which downstream routes remain dangerous because a stale packet may still be sitting in someone’s queue.

### 5) Decision footer

Use:

> Route [recipient] as [route]. Carry [evidence]. Require [checkpoint]. Downgrade or block [other route] because [reason].

If no route is safe, use:

> No safe downstream route yet. Keep the recipient at [weaker relation] until [authority or freshness gap] is resolved.
''',
    '1483-action-authority-proof-page-issued-mandate-acceptance-execution-and-revocation-interface-spec.md': '''# Action authority proof page: issued mandate, acceptance, execution, and revocation interface spec

## Purpose

Operators need one durable proof object for the harder question:

> what exact mandate was issued, who accepted it, what did they actually do, and what later revoked or superseded that authority?

## Core decision

AnonSync must preserve mandate truth as a lineage-bearing proof object rather than scattering it across tickets, chat, and memory.

## Fixed page order

1. **Mandate proof header**
2. **Authority issuance card**
3. **Acceptance-and-custody card**
4. **Execution-and-proof card**
5. **Revocation-and-aftereffects card**
6. **Decision footer**

### 1) Mandate proof header

Show:

- action mandate id
- live link to source reliance charter
- live link to source certificate / case / campaign
- current mandate state
- active strongest safe execution sentence
- blocked stronger sentence

Supported `current_mandate_state` values:

- `issued-not-yet-received`
- `received-not-accepted`
- `accepted-not-started`
- `executing`
- `executed-awaiting-proof`
- `executed-proved`
- `revoked-before-start`
- `revoked-mid-flight`
- `superseded`
- `expired`

### 2) Authority issuance card

Required rows:

- issuer
- issuance basis
- authority class granted
- scope granted
- explicit exclusions
- expiry / cancel condition

Hard rule:

A downstream action proof is incomplete unless the original authority boundary is preserved alongside the execution story.

### 3) Acceptance-and-custody card

Required rows:

- delivery state
- acceptance state
- accepted by
- delegated onward
- onward authority basis
- missing acknowledgement risk

Supported `acceptance_state` values:

- `not-required`
- `receipt-only`
- `accepted-duty`
- `counter-signed`
- `rejected`
- `timed-out`

Hard rule:

`sent` is weaker than `received`, and `received` is weaker than `accepted duty`.
A mandate cannot overclaim execution authority if custody was never accepted.

### 4) Execution-and-proof card

Required rows:

- execution status
- steps attempted
- proof attached
- outcome class
- residual debt created
- follow-on recheck due

Supported `outcome_class` values:

- `not-started`
- `attempted-no-change`
- `partial-execution`
- `bounded-success`
- `success-with-delta`
- `blocked`
- `stopped-on-recall`

Hard rule:

Execution proof must stay weaker than source truth when the result leaves residual delta, excluded scope, or unclosed reconciliation work.

### 5) Revocation-and-aftereffects card

Required rows:

- superseded by mandate id
- revocation event
- time of revocation
- queued work still exposed
- in-flight stop class used
- surviving weaker sentence after revocation

Hard rule:

Revocation must explain not only that the mandate died, but what surviving partial work, stale expectation, or weakened sentence remains afterward.

### 6) Decision footer

Use:

> Mandate [id] granted [authority] to [recipient], accepted at [state], executed to [outcome], and is now [current state]. Surviving weaker sentence: [sentence].
''',
    '1484-mandate-timeline-page-issue-acknowledgement-execution-supersession-and-cancel-events-interface-spec.md': '''# Mandate timeline page: issue, acknowledgement, execution, supersession, and cancel events interface spec

## Purpose

Operators need one event timeline that answers:

> when did this instruction become real, when did someone accept it, when did work start, and when did later supersession or cancellation change what was still safe to do?

## Core decision

AnonSync must give action mandates the same event rigor as incidents, campaigns, and certificates.

## Timeline event classes

Supported event classes:

- `issued`
- `delivered`
- `read`
- `accepted-duty`
- `counter-signed`
- `execution-started`
- `checkpoint-passed`
- `checkpoint-blocked`
- `execution-paused`
- `execution-completed`
- `proof-uploaded`
- `superseded`
- `cancelled`
- `revocation-acknowledged`
- `stale-copy-discovered`
- `reopened`

## Fixed page order

1. **Timeline header**
2. **Live mandate lane**
3. **Recipient acknowledgement lane**
4. **Execution lane**
5. **Supersession / cancel lane**
6. **Decision footer**

### 1) Timeline header

Show:

- mandate id
- source reliance charter id
- current state
- first unsafe stale point
- next required event

### 2) Live mandate lane

Show all issuance and expiry transitions with:

- event time
- actor
- summary
- sentence that became newly safe
- stronger sentence still blocked

### 3) Recipient acknowledgement lane

Show:

- which recipients only received
- which recipients accepted duty
- which recipients counter-signed
- which recipients never acknowledged
- which recipients were later recalled successfully

Hard rule:

A timeline that hides non-acknowledging recipients is too optimistic for serious delegated work.

### 4) Execution lane

Show:

- start time
- critical checkpoints
- proof attachments
- stop/hold points
- final bounded outcome
- residual debt or follow-on requirement

### 5) Supersession / cancel lane

Show:

- superseding mandate ids
- recall or cancellation issue time
- recipients reached versus not reached
- stale-copy discovery events
- surviving safe fallback instruction

Hard rule:

Supersession is not complete just because a newer mandate exists.
The timeline must show whether holders of the older one were actually reached.

### 6) Decision footer

Use:

> Timeline shows mandate [id] became actionable at [time], was accepted by [scope], executed to [bounded result], and was later [superseded/cancelled] with [remaining stale risk].
''',
    '1485-mandate-lineage-receipt-page-authority-scope-duty-state-and-recall-boundary-interface-spec.md': '''# Mandate lineage receipt page: authority, scope, duty state, and recall boundary interface spec

## Purpose

Later operators need one receipt that answers:

> what exact authority was issued here, to whom, for what scope, with what duty state, and what weaker sentence survived once the mandate expired or was recalled?

## Core decision

AnonSync must emit one durable **Mandate lineage receipt** whenever a meaningful action mandate is issued, superseded, or cancelled.

## Fixed page order

1. **Receipt header**
2. **Authority summary**
3. **Duty-state summary**
4. **Execution summary**
5. **Recall boundary summary**
6. **Next-operator sentence**

### 1) Receipt header

Show:

- mandate id
- receipt id
- issuer
- recipient / cohort
- issue time
- current archival state

Supported `current_archival_state` values:

- `historical-active-when-issued`
- `historical-superseded`
- `historical-cancelled`
- `historical-expired`
- `historical-retired`

### 2) Authority summary

Required rows:

- authority class granted
- source basis
- scope covered
- excluded scope
- re-delegation right
- expiry rule

### 3) Duty-state summary

Required rows:

- delivery state
- acceptance state
- execution state
- proof state
- unresolved acknowledgement gap

### 4) Execution summary

Required rows:

- action taken
- bounded outcome
- residual delta
- follow-on obligation
- strongest sentence earned

### 5) Recall boundary summary

Required rows:

- superseding mandate id if any
- cancel / recall event
- surviving weaker sentence after recall
- stale-copy risk that may persist
- next forbidden overclaim

Hard rule:

A receipt must preserve not just what was authorized once, but what became unsafe to assume later.

### 6) Next-operator sentence

Use:

> This receipt proves that [recipient] was granted [authority] for [scope], accepted duty at [state], reached [bounded outcome], and after [supersession/cancel] only [weaker sentence] remained safe.
'''
}

for name, content in new_docs.items():
    (docs / name).write_text(content, encoding='utf-8')


def prepend(path_str: str, block: str):
    path = root / path_str
    old = path.read_text(encoding='utf-8')
    path.write_text(block.rstrip() + '\n\n' + old, encoding='utf-8')

prepend('README.md', '''## Revision addendum after rev0389 — reliance-to-action authority, delegated mandate, and cancellation truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **reliance versus action authority**.
It does eight things in one tranche:

1. Continues the archive after rev0389 with a new page family centered on how a received packet becomes, or does not become, downstream authority.
2. Tightens the non-clone line again: borrow Resilio's candor that permissions, invitation rights, approval checkpoints, requester fingerprints, folder-type differences, link expiry, use-count limits, revoke/disconnect, and linked-identity owner expansion are all real authority ingredients; refuse any contract where the operator still has to reconstruct `who may merely know, who may decide, who may execute, who may re-delegate, and how stale instructions die` from several separate pages and gestures.
3. Adds one new **Resilio evaluation** document focused on why current reliance-to-action truth is still too fragmented to clone even though the authority ingredients are useful.
4. Adds five new **interface specs** for action mandate contract sheet, mandate shaping review, action authority proof, mandate timeline, and mandate lineage receipt.
5. Makes one hard product decision explicit: **a reliance packet is not a work order.**
6. Makes another hard product decision explicit: **observe, approve, execute, escalate, and re-delegate remain separate truths.**
7. Makes a third hard product decision explicit: **queued or in-flight work must publish how supersession or cancellation changes what is still safe to do.**
8. Packages the result as another continuation archive whose new tranche makes the `authority / action-set / scope / expiry / cancellation / receipt` seam explicit in the reading order and page family.

New docs in this tranche:

- `1480-resilio-reliance-to-action-authority-delegation-and-recall-fragmentation-evaluation.md`
- `1481-action-mandate-contract-sheet-page-authority-scope-duties-and-expiry-interface-spec.md`
- `1482-mandate-shaping-review-page-inform-observe-decide-execute-and-escalate-routing-interface-spec.md`
- `1483-action-authority-proof-page-issued-mandate-acceptance-execution-and-revocation-interface-spec.md`
- `1484-mandate-timeline-page-issue-acknowledgement-execution-supersession-and-cancel-events-interface-spec.md`
- `1485-mandate-lineage-receipt-page-authority-scope-duty-state-and-recall-boundary-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's reliance-to-action contract**
''')

prepend('docs/00-status.md', '''## Revision addendum — reliance-to-action authority, delegated mandate, and cancellation truth after rev0389

This tranche locks the next seam around **action-authority truth**.
The key decisions now made explicit in the archive are:

- **reliance and action authority are separate first-class objects**
- **`inform`, `watch`, `approve`, `execute`, `escalate`, and `re-delegate` remain separate routes**
- **a role label like `owner` or `operator` is weaker than an explicit authority class and action set**
- **every serious mandate now needs explicit scope, exclusions, preconditions, expiry, and cancellation behavior**
- **every serious issued instruction now gets one receipt that preserves who was empowered, what they were allowed or required to do, what they were forbidden to do, when the authority died, and what weaker sentence survived after recall**

New docs added in this tranche:

- `1480-resilio-reliance-to-action-authority-delegation-and-recall-fragmentation-evaluation.md`
- `1481-action-mandate-contract-sheet-page-authority-scope-duties-and-expiry-interface-spec.md`
- `1482-mandate-shaping-review-page-inform-observe-decide-execute-and-escalate-routing-interface-spec.md`
- `1483-action-authority-proof-page-issued-mandate-acceptance-execution-and-revocation-interface-spec.md`
- `1484-mandate-timeline-page-issue-acknowledgement-execution-supersession-and-cancel-events-interface-spec.md`
- `1485-mandate-lineage-receipt-page-authority-scope-duty-state-and-recall-boundary-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `received the packet` can no longer hide whether the recipient may actually act
- authority now stays bounded by scope, world, prerequisites, and freshness instead of by vague seniority or convenience
- cancellation and supersession now explicitly tell downstream actors whether to stop immediately, finish a bounded safe-close, or escalate
- later operators can open one receipt and see what action authority existed, who accepted it, what happened, and what became unsafe to assume later
''')

prepend('docs/10-resilio-sync-evaluation.md', '''## Revision addendum — Resilio reliance-to-action authority evaluation after rev0389

Another current official Resilio pass still supports the same tightened judgment:

- **borrow Resilio's permission candor**
- **do not clone Resilio's reliance-to-action contract**

This time the key evidence cluster is:

- `Sync functionality in detail` still says folder permissions determine what exactly a user can do, with Read Only, Read & Write, and Owner classes
- the same article still says access can be changed before, during, or after sharing, access can be revoked, and approval-time permissions can be altered
- the same article still says all linked devices under one private identity act as Owners and approvals can be handled from any linked device
- `User Management` still says only Owners can invite new users, different peers can receive different permissions, and disconnect revokes future updates while already-synced files remain
- `Sync Share Dialog (Desktop)` still says Advanced-folder sharing is owner-only, Standard folders omit Owner level, and the same dialog still keeps approval rules, expiry, and use-count limits
- `Comprehensive guide to syncing (Desktop-Desktop)` still says the operator must choose access mechanism, permission set, and possibly perform approval, and can inspect requester name, IP, fingerprint, and approval request receipt date before approving

So current Resilio still deserves credit for exposing many real authority ingredients.
But it still does not own one operator-facing answer to:

> who is merely informed, who may approve, who may execute, who may re-delegate, what exact action is allowed or required, and what later cancellation does to work already in motion?

That is the product gap this tranche makes explicit.
''')

prepend('docs/11-resilio-borrow-line-and-non-clone-scorecard.md', '''## Revision addendum — borrow line after rev0389: reliance-to-action authority truth

### Borrow from Resilio

- keep permission classes, invitation rights, approval steps, and revoke/disconnect effects visibly distinct
- stay candid that folder type, linked-identity topology, and share mechanism affect downstream authority
- preserve expiry, use-count, and requester-fingerprint review as real authority-shaping ingredients

### Do not clone from Resilio

- do not let a reliance packet silently become an action order
- do not let `can read`, `can approve`, `can execute`, and `can re-share` blur together
- do not let cancellation of in-flight downstream work live only in human memory or thread follow-up
- do not let role labels alone stand in for bounded action authority

### New non-clone score

This seam remains **do not clone** because the raw authority ingredients are useful but the downstream-action contract is still too diffuse.
AnonSync should ship explicit action mandates, shaping reviews, authority proofs, timelines, and lineage receipts.
''')

prepend('docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md', '''## Revision addendum — clone-veto obligations for reliance-to-action authority after rev0389

### New veto seam

A sync product fails the clone test on this seam if it cannot answer, in one operator-facing workflow:

- whether the recipient is informed, observing, approving, executing, or re-delegating
- what exact actions are allowed, required, and forbidden
- what scope, world, and freshness boundary the authority applies to
- what preconditions must hold before action starts
- what event cancels or supersedes the mandate later
- what in-flight action should do when cancellation arrives
- what weaker sentence survives after recall or expiry

### New page obligations

This seam adds five more page obligations:

1. an **action mandate contract sheet** that preserves actor class, authority class, action set, scope, exclusions, preconditions, expiry, and cancellation rules
2. a **mandate shaping review** that routes recipients to inform, watch, approve, execute, escalate, or no-safe-route outcomes
3. an **action authority proof** that records issuance, acceptance, execution, proof, supersession, and surviving weaker sentence
4. a **mandate timeline** that preserves issue, delivery, duty acceptance, execution checkpoints, supersession, cancellation, and stale-copy discovery events
5. a **mandate lineage receipt** that tells the next operator what exact authority existed, who accepted it, what outcome was reached, and what overclaim is now forbidden

### Explicit clone vetoes

Do not clone any contract where:

- receiving a status packet is treated as equivalent to having action authority
- role labels replace explicit action sets and scope boundaries
- cancellation kills a mandate in theory but leaves queued work and stale copies unexplained
- a recipient can re-delegate work without an explicit onward authority basis
''')

prepend('docs/20-product-direction.md', '''## Product-direction addendum after rev0389 — reliance is not action authority

AnonSync should not let publication-for-reliance stand in for downstream action permission.
The product direction is now explicit:

- **action mandates are first-class**
- **actor class, authority class, action set, preconditions, scope, expiry, and cancellation remain separate**
- **received is weaker than accepted duty**
- **accepted duty is weaker than executed with proof**
- **superseded or cancelled mandates must still explain what in-flight work and stale expectations survive**

That means future interface work should keep one stable family for:

- mandate issuance
- actor / authority routing
- allowed vs required vs forbidden action
- precondition and checkpoint logic
- cancellation / supersession behavior
- residual stale-copy or partial-work downgrade

The product should never force the operator to infer action authority from a share link, a role name, a forwarded packet, or a generic `owner` label alone.
''')

prepend('docs/sources.md', '''## rev0390 source set — reliance-to-action authority, delegated mandate, and cancellation truth

The most load-bearing source set for this pass was:

- Resilio's current `Sync functionality in detail` article, which still says folder permissions determine what exactly a user can do, lists Read Only / Read & Write / Owner, says permissions can change before, during, or after sharing, and says access can be revoked or altered during approval.
- The same functionality article, which still says linked devices under one private identity all act as Owners and that approval requests can be handled from any linked device.
- Resilio's current `User Management` article, which still says only Owners can invite new users, different peers can receive different permissions, and disconnect revokes future updates while already-synchronized files remain.
- Resilio's current `Sync Share Dialog (Desktop)` article, which still says Advanced folders can be shared only by Owners, Standard folders omit Owner level, and the dialog still carries approval requirement, link expiry, and use-count limit.
- Resilio's current `Comprehensive guide to syncing (Desktop-Desktop)` article, which still says manual sharing requires choosing an access mechanism, permission set, and folder location, may require approval, and allows inspecting requester name, IP address, fingerprint, and approval request receipt date before approving.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for exposing several real authority ingredients
- but current Resilio still answers `who may merely know, who may approve, who may execute, who may re-delegate, and what later cancellation does to work already in motion?` too diffusely
- AnonSync should therefore prefer explicit action mandates, routing reviews, authority proofs, timelines, and durable lineage receipts over improvised permission folklore

Primary sources:

- Sync functionality in detail
  https://help.resilio.com/hc/en-us/articles/204754389-Sync-functionality-in-detail

- User Management
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- Sync Share Dialog (Desktop)
  https://help.resilio.com/hc/en-us/articles/204790709-Sync-Share-Dialog-Desktop

- Comprehensive guide to syncing (Desktop-Desktop)
  https://help.resilio.com/hc/en-us/articles/204754939-Comprehensive-guide-to-syncing-Desktop-Desktop
''')

print('update_rev0390.py wrote new docs and prepended addenda')
