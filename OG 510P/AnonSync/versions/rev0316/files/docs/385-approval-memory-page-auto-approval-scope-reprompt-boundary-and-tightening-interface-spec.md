# Approval memory page: auto-approval scope, reprompt boundary, and tightening interface spec

## Purpose

The archive already has strong trust-promotion and remembered-approval doctrine.
This document makes the ordinary page concrete.

The page exists to answer one ordinary operator question:

> why did this claimant auto-approve, reprompt, or remain pending under current remembered-trust policy, and how can I deliberately tighten or widen that behavior?

## Core decision

Every serious approval system must own one first-class **Approval memory** page.
That page is the semantic home of:

- remembered-trust record
- scope of remembered trust
- reprompt policy and triggers
- auto-approval verdict for the current claim
- tightening / widening actions
- recent memory-change receipts

The product must not let `Only new peers` versus `All peers` language carry the whole semantic load by itself.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. claimant-memory strip
2. current-memory card
3. current-claim verdict card
4. reprompt-boundary card
5. tightening / widening card
6. recent memory-change receipts
7. expert details drawer

### 1) Claimant-memory strip

Show:

- claimant identity
- current subject or subject family
- current viewing seat
- strongest next-safe action
- whether the page is reviewing a live claim or a standing memory record

The strip should answer `whose remembered trust am I reviewing, and in what scope?`

### 2) Current-memory card

Show:

- whether a remembered trust record exists
- where it originated
- which seat created it
- current scope (`none`, `subject-only`, `seat-family`, `claim-lane-only`, `broader pending-policy memory`, `historical-only`)
- last time it was used successfully

This card should answer `what trust memory exists right now?`

### 3) Current-claim verdict card

Show one explicit verdict:

- `auto-approved because remembered trust matched current policy`
- `fresh prompt required because policy says all peers`
- `fresh prompt required because claim exceeded remembered scope`
- `pending because matching memory exists but no eligible approving seat is online`
- `no applicable remembered trust`

Also show:

- whether a broader memory record existed but was intentionally ignored
- whether current lane or resulting right exceeded the remembered ceiling

This card should answer `why did this claim behave this way?`

### 4) Reprompt-boundary card

Show:

- exact events that force reprompt (`every peer`, stronger requested right, new subject family, stale proof, security posture raised, memory manually frozen, etc.)
- exact events that allow reuse (`same claimant`, same or narrower right, same governed family, valid freshness window, etc.)
- whether reprompt is driven by standing policy or one-off subject override

This card should answer `when do I get asked again?`

### 5) Tightening / widening card

Offer only deliberate actions, for example:

- `freeze to subject-only memory`
- `require fresh approval for every future claim`
- `allow reuse for same claimant and narrower rights`
- `retire remembered trust entirely`
- `promote current approval to broader family memory`

Every action must preview the next likely change in auto-approval behavior.

### 6) Recent memory-change receipts

Show recent receipts with:

- claimant
- prior scope
- new scope
- current-claim verdict at the time
- deciding seat
- change reason

### 7) Expert details drawer

Hide raw cert chain references, memory lineage IDs, ACL links, and policy-override traces behind an expert drawer.
They matter, but they are not the semantic center.

## Compact row contract

A trustworthy compact row should preserve the following order:

1. claimant phrase
2. current-memory phrase
3. current-claim verdict phrase
4. reprompt boundary phrase
5. strongest next action

Example:

```text
Alex remembered at subject-family scope · current claim reprompted because policy requires all peers · next reprompt boundary remains every claim until policy relaxed · Keep strict or narrow to subject-only
```

## Mandatory fields

- `claimant_ref`
- `memory_record_ref` nullable
- `memory_scope`
- `memory_origin_ref`
- `memory_created_by_seat_ref`
- `memory_last_used_at` nullable
- `current_claim_ref` nullable
- `current_claim_verdict`
- `reprompt_triggers[]`
- `reuse_conditions[]`
- `policy_source`
- `available_memory_actions[]`
- `strongest_next_action`

## Review guarantees

This page must let the operator:

- see whether remembered trust exists at all
- understand why the current claim auto-approved, reprompted, or stayed pending
- predict the next reprompt boundary before changing policy
- tighten or widen remembered-trust scope deliberately instead of by folklore
