# Completion dispute contract sheet page: claim, counterclaim, witness, and burden interface spec

## Purpose

After the archive learned how to receive and accept fulfillment returns, it still needed one ordinary page for the next operator question:

> the assignee says the work is done, but the requester or downstream evidence disagrees — what exactly is being challenged, what counterevidence exists, and what burden still blocks closure?

## Core decision

AnonSync must expose one first-class **Completion dispute contract sheet** whenever a fulfillment attestation, accepted completion, or observed outcome is materially challenged.

## Fixed page order

1. **Dispute header**
2. **Challenged-claim card**
3. **Counterevidence card**
4. **Witness priority card**
5. **Burden and requested verdict card**
6. **Decision sentence**

### 1) Dispute header

Show:

- dispute id
- source fulfillment attestation id
- source mandate id
- challenger
- review owner
- opened time
- current dispute status
- strongest currently safe sentence
- latest superseding dispute or appeal id if any

Supported `dispute_status` values:

- `drafting`
- `opened-awaiting-evidence`
- `opened-awaiting-assignee-response`
- `under-adjudication`
- `upheld-original-return`
- `narrowed-original-return`
- `overturned-return`
- `rework-issued`
- `appeal-open`
- `closed`
- `superseded`

Hard rule:

A challenged completion claim may not remain silently `accepted` once a material dispute is opened.
The challenged state must remain visible until a verdict or superseding appeal is recorded.

### 2) Challenged-claim card

Required rows:

- challenged fulfillment sentence
- challenged scope
- original acceptance class if any
- claimant / assignee
- reviewer who accepted it if any
- precise thing the challenger says is wrong

Hard rule:

The product must store the original claimed sentence verbatim enough to judge the later challenge.
A dispute cannot target an ambiguous memory of `done`.

### 3) Counterevidence card

Required rows:

- counterevidence summary
- witness family per item
- freshness per item
- scope touched by each witness
- contradictions already known
- missing witness still requested

Supported `witness_family` values:

- `live-state`
- `history-event`
- `warning-or-error`
- `peer-topology`
- `path-or-mode-state`
- `file-level-artifact`
- `operator-note`
- `requester-observation`
- `delegate-response`

Hard rule:

Counterevidence must stay typed.
`It still looks wrong` is not enough unless attached to an explicit witness family and scope.

### 4) Witness priority card

Required rows:

- prioritized witness families for this dispute
- witness families that are weaker but still informative
- witness families currently invalidated by drift or staleness
- ordering basis used to compare conflicting witnesses
- unsafe shortcut the product must suppress

Hard rule:

The page must show how the product will rank contradictory witnesses.
A green badge must not silently outrank a file-level artifact or an invalid-time warning when the dispute concerns the missing file itself.

### 5) Burden and requested verdict card

Required rows:

- burden currently unmet
- party expected to answer next
- requested verdict
- rework requested if overturned or narrowed
- stronger blocked sentence
- appeal boundary

Supported `requested_verdict` values:

- `uphold-original-return`
- `narrow-original-scope`
- `overturn-return`
- `issue-rework`
- `reopen-underlying-case`
- `insufficient-evidence-yet`

Hard rule:

A dispute may not close with `looks fine now`.
The stored verdict request must say what stronger sentence is being sought or denied.

### 6) Decision sentence

Render one sentence only:

- `This dispute challenges [claim] for [scope], currently stands at [dispute_status], and still blocks the stronger sentence that [overclaim].`

## Required interactions

- **Attach counterevidence**
- **Request assignee response**
- **Change witness priority basis**
- **Narrow accepted scope**
- **Overturn and issue rework**
- **Escalate to appeal**

## Empty and failure states

If a dispute is opened with no counterevidence yet, show:

- `Challenge opened, but no typed counterevidence has been attached yet.`

If the challenged return was already superseded, show:

- `Challenge can no longer change the superseded return directly; open appeal or challenge the newer return.`
