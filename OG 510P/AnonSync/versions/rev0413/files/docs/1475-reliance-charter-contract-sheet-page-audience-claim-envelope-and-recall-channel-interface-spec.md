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
