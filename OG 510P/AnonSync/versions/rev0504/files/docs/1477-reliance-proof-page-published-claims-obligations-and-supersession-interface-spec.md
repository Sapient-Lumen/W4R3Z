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
