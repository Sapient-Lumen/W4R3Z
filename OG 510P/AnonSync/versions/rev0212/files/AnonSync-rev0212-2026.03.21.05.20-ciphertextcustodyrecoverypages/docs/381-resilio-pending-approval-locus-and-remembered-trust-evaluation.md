# Resilio pending approval, approver locus, and remembered-trust evaluation

## Why this pass exists

The archive already had strong doctrine for offers, claim lanes, linked-seat authority, and grant lifecycle.
What it still lacked was one direct current Resilio evaluation for another ordinary seam:

> when a join is still pending, where does the product itself own the answer to `is the request real?`, `which seat can approve it?`, `what exactly am I seeing when I inspect it?`, and `why did remembered trust auto-approve or fail to auto-approve?`

Current official Resilio docs still show a useful, living product, but they also show that ordinary approval truth still leaks across several different article families at once:

- share-dialog security controls
- desktop guide and manual share flow
- folder-type and pending-icon guidance
- identity-linking guidance
- link-flow / certificate guidance
- connectivity and route troubleshooting

## Current official Resilio evidence that matters here

Current official docs still show an active v3 line through `3.1.2.1076`.
They also still say all of the following:

- By default, a person only needs to be approved once; the next time that person is shared to, approval is not necessary because Sync retains a certificate with their identity.
- The share dialog still lets the issuer require approval for `Only new peers` or `All peers`, while Standard-folder raw keys still do not use the approval mechanism at all.
- A remote device that adds the folder still sends an approval request to the issuer, and the issuer can inspect the claimant's name, IP address, fingerprint, and request receipt date before deciding.
- If the remote device stays in `Pending approval` but the issuer does not receive any request, the docs still classify that as a network-connectivity problem between the devices rather than a simple undecided request.
- Current functionality and identity docs still say approval can be granted from any linked device, not just the original issuing device, but only from linked seats where the folder is in `Selective Sync` or `Synced`.
- Folder-type guidance still says a pending folder can auto-connect later if the sharer has approved that user before and one of the sharer's devices is online.
- The link-flow article still says approval is a concrete certificate and ACL event: the claimant sends a locally generated public key, the approver reviews fingerprint and name, then the approver generates an X509 certificate and grants a concrete access level.

So current Resilio still contains a real but scattered answer to `why is this still pending, and who can decide it?`

## What Resilio still gets right

### 1) It treats approval as real identity-bearing work

Current docs still do better than many simpler sync tools by making approval about a claimant identity, fingerprint, and resulting certificate rather than about a disposable pop-up with no durable proof.
That instinct is strong and worth borrowing.

### 2) It keeps remembered-trust convenience

Current docs still preserve the practical idea that after you have approved a person once, later sharing can become simpler.
That convenience matters.
A serious sync product should not force full cold-start approval every time when the operator has deliberately created remembered trust.

### 3) It allows distributed approving across linked seats

Current docs still allow approval from linked devices instead of forcing the operator back to the one original issuer.
That is an operationally good idea, especially when one machine is asleep or headless.

### 4) It admits that `pending` can really be a route problem

The desktop guide still plainly says that a remote device can remain in `Pending approval` while the issuer receives no request at all, and that this points to network connectivity trouble.
That honesty is valuable.
A weaker product would let operators misread route failure as human indecision forever.

## Why this is still a good reason not to clone them

### 1) Pending state is still not one product-owned truth surface

The operator still has to cross-read several current docs to answer one ordinary question:

- is the claim actually waiting on me?
- did the request reach any approvable seat?
- should this have auto-approved already under remembered trust?
- which linked seat may approve it now?
- what proof am I really reviewing before I approve?

That is exactly the sort of ordinary question AnonSync should answer on one stable page.

### 2) Approver-locus truth is still half in product semantics, half in folklore

Current docs do say approval can happen from any linked device, but the actual boundary is narrower than that: the subject must be materially present there in `Selective Sync` or `Synced`.
That means `linked` is not the same as `eligible approver seat`.
Resilio's docs reveal that truth, but the interface contract still leaves too much of it implicit.

### 3) Remembered trust is useful, but its scope is still not surfaced cleanly

Current docs still expose pieces of the policy:

- previously approved peers may skip future prompts
- `All peers` can force fresh approval every time
- pending folders may auto-connect later if prior approval exists and one approving device is online

But the ordinary operator still lacks one page saying:

- what memory currently exists for this claimant
- how broad that remembered trust is
- why it applied or did not apply here
- what exact tightening action would narrow it safely

That is a good reason to remodel the behavior rather than clone it.

### 4) Identity proof is still real, but the review basis is scattered

Current docs still say that approval includes name, fingerprint, request date, and public-key / certificate flow.
That is strong.
But the answer to `what exactly am I approving?` still leaks across the share guide, desktop guide, and security article.
AnonSync should keep the good proof but collapse it into one explicit claim-inspection page.

## What AnonSync should borrow directly

- fingerprint-backed claimant inspection
- remembered-trust convenience as a deliberate product feature
- approval from another eligible linked seat
- honesty that `pending` can mean route failure rather than mere human indecision

## What AnonSync should adapt instead of clone

### 1) Pending claim must be its own page

A pending request should not be represented only by a pending folder icon or a missing sync start.
AnonSync should expose one page that classifies pending into explicit families such as:

- awaiting human decision
- awaiting request visibility on an eligible approver seat
- eligible for remembered auto-approval when qualifying seat becomes available
- reprompt forced by current policy
- blocked because no current seat is eligible to approve here

### 2) Claim inspection must be its own page

Approval should open one stable review surface for:

- claimant identity and name
- fingerprint and receipt evidence
- entry lane and resulting authority if approved
- remembered-trust history
- strongest next-safe decision

### 3) Approval authority must be its own page

The product should publish which current seats may approve and why.
It should not let `linked device` pretend to mean `current approver`.

### 4) Approval memory must be its own page

Remembered trust should be governable.
The operator should be able to see its scope, its origin, its next reprompt trigger, and the exact action needed to narrow or freeze it.

## Resulting replacement pages

This pass therefore adds four more ordinary page contracts:

1. **Pending claim** — request visibility, approver locus, and route gap
2. **Claim inspection** — requester proof, fingerprint, and approval basis
3. **Approval authority** — seat eligibility, subject presence, and fallback
4. **Approval memory** — auto-approval scope, reprompt boundary, and tightening

## Bottom line

Current Resilio docs still show a serious product with practical approval flows.
That is exactly why the comparison matters.

The stronger AnonSync line is now:

> borrow Resilio's identity-backed approval, linked-seat practicality, and remembered-trust convenience, but refuse any interface contract where `pending`, `approvable`, and `already trusted` remain only partly product-owned truths.
