## Revision addendum — escalation packets after rev0261: disclose witness coverage, not just included files

Any escalation packet derived from a multi-peer incident should now say whether the packet reflects:

- a complete required witness set
- a partial witness set with named missing participants
- an intentionally narrow sample with a reduced claim ceiling

Recipients should not have to infer witness completeness from attachment count alone.

# External escalation packet, packet freeze, and redaction review interface spec

## Purpose

The archive already has:

- diagnostic incidents
- evidence bundles
- convergence evidence bundles
- probe approval and minimization plans
- intervention receipts with post-action recompute

What still remained under-specified was the boundary where evidence leaves local custody.
That is a different decision from collecting the evidence in the first place.
The operator may now want to:

- send material to a support contact
- hand a packet to another trusted operator
- ask a teammate for diagnosis help
- post a minimized packet to a community forum
- preserve one sealed packet for later offline escalation

This document defines the interface contract for one first-class **external escalation packet**, one explicit **redaction review** surface, and one **frozen reviewed manifest** boundary.

## Core rule

No diagnostic evidence may leave local custody without a reviewed escalation packet that states:

1. who the recipient is
2. why the packet is being disclosed
3. which sealed evidence objects are included
4. what human orientation surface leads the packet
5. what was redacted, tokenized, or blocked
6. what cannot be recalled once sent
7. what exact frozen manifest left local custody

The product must never treat `export logs` or `send bundle` as self-explanatory.

## Why this needs its own spec

Current Resilio material is again useful but still externalizes meaning across support ritual:

- collect logs
- reproduce the issue for a while
- create feedback or send information to support
- use community/forum routes in some product lines
- gather crash artifacts or profiler data through separate support pages

That may work.
It is not one trustworthy disclosure surface.
AnonSync should keep a stricter split:

- **private incident evidence** is for local diagnosis first
- **shareable escalation packets** are recipient-specific frozen exports derived from reviewed evidence
- **not sending anything** is a normal, first-class outcome

## Public objects

### External escalation packet

A durable reviewed object for one disclosure attempt or one held-unsent draft.

Suggested fields:

- `external_escalation_packet_id`
- `diagnostic_incident_ref`
- `question_prompt`
- `recipient_class` (`trusted-operator`, `support-vendor`, `community-forum`, `private-archive`, `other`)
- `recipient_descriptor`
- `packet_state` (`draft`, `held-unsent`, `sealed`, `sent`, `expired`, `destroyed`)
- `orientation_surface_ref`
- `manifest_freeze_state` (`not-frozen`, `frozen-reviewed`, `sent`, `expired`)
- `redaction_profile_ref`
- `created_at`

### Packet artifact row

One candidate artifact for inclusion, omission, or block.

Suggested fields:

- `packet_artifact_row_id`
- `artifact_kind` (`incident-summary`, `timeline-summary`, `evidence-bundle-summary`, `route-snapshot`, `transfer-sample`, `crash-artifact`, `config-summary`, `screen-capture`, `note`)
- `source_ref`
- `inclusion_state` (`included`, `omitted`, `blocked`, `included-redacted`)
- `reason`
- `sensitivity_class` (`low`, `medium`, `high`, `secret-bearing`)

### Redaction decision row

One reviewable transformation or block applied to the outgoing packet.

Suggested fields:

- `redaction_decision_row_id`
- `field_family` (`paths`, `peer-ids`, `addresses`, `share-names`, `config-values`, `timestamps`, `crash-registers`, `other`)
- `treatment` (`full`, `basename-only`, `stable-token`, `rounded`, `summary-only`, `blocked`)
- `reason`
- `residual_risk`

### Frozen packet manifest

A stable member listing for the exact packet that may be sealed or sent.

Suggested fields:

- `frozen_packet_manifest_id`
- `packet_ref`
- `member_refs[]`
- `manifest_hash`
- `frozen_at`

### Disclosure receipt

A durable record that proves what left local custody.

Suggested fields:

- `disclosure_receipt_id`
- `external_escalation_packet_ref`
- `frozen_manifest_ref`
- `sealed_manifest_hash`
- `sent_artifact_refs[]`
- `redaction_profile_ref`
- `actor_ref`
- `sent_at`
- `delivery_channel`

## Fixed inspection order

Every escalation packet review should preserve this order:

1. **What unresolved question justifies disclosure**
2. **Recipient and disclosure posture**
3. **Packet orientation surface**
4. **Included artifacts, omitted artifacts, and frozen manifest**
5. **Redaction decisions and sensitive-field preview**
6. **Irreversibility and recipient-risk warnings**
7. **Hold locally, seal, send, or destroy**

### 1) What unresolved question justifies disclosure

This section should stop disclosure inflation.
Examples:

- `Need another operator to interpret repeated route contradictions`
- `Need vendor/support review of crash artifact signatures`
- `Need public forum advice, but only on minimized transfer symptoms`

### 2) Recipient and disclosure posture

This section should say exactly who is receiving the packet and under what trust model.
Examples:

- `trusted operator — recipient-specific sealed packet`
- `support vendor — sealed packet with tokenized network identifiers`
- `community forum — public minimized packet, no raw logs`
- `private archive — hold locally, no disclosure yet`

### 3) Packet orientation surface

The first thing the recipient should get is the story, not a directory listing.
This section should show the short incident summary or timeline that will lead the packet.

### 4) Included artifacts, omitted artifacts, and frozen manifest

The interface must list both inclusions and omissions and then freeze one reviewed manifest.
Examples:

- include: incident summary, evidence bundle summary, route snapshot, transfer samples
- omit: raw trace logs, unrelated incidents, full config, long retention notes
- freeze: one stable manifest hash before any send action becomes available

### 5) Redaction decisions and sensitive-field preview

This section should let the operator inspect how sensitive classes will appear to the recipient.
Examples:

- path basename only
- peer IDs tokenized but stable within this packet
- addresses reduced to subnet or blocked entirely
- timestamps rounded where exactness is not needed
- config values replaced with safe summaries

### 6) Irreversibility and recipient-risk warnings

Examples:

- `recipient may retain copies outside your control`
- `forum disclosures cannot be recalled`
- `vendor may need enough fidelity to correlate across attempts`
- `public packet is intentionally less diagnostic than sealed private packet`

### 7) Hold locally, seal, send, or destroy

Examples:

- `Keep held-unsent draft`
- `Freeze reviewed manifest and seal packet`
- `Send now and record disclosure receipt`
- `Destroy unsent draft`

## Public rules

### Rule 1 — disclosure is always recipient-specific

A packet suitable for one recipient class is not automatically suitable for another.
Retargeting a previously reviewed packet should therefore reopen through the reviewed recipient-target guard rather than silently inheriting the old disclosure review.

### Rule 2 — export uses frozen reviewed artifacts, not live workspace state

The product must export from the reviewed packet manifest, not by opportunistically sweeping current logs from disk.

### Rule 3 — no-send is a normal outcome

The operator may keep a packet private, held-unsent, or destroyed without the surface implying failure.

### Rule 4 — public/community escalation receives the strongest minimization defaults

If the recipient is effectively public, raw logs and rich identifiers should be blocked unless the operator explicitly escalates again.

### Rule 5 — disclosure warnings must be honest about recall limits

The surface must say when deletion can only be requested or cannot realistically be enforced.

### Rule 6 — one packet answers one question

The operator should not be encouraged to dump unrelated evidence just because an export surface exists.

### Rule 7 — post-send state remains visible locally

After sending, the archive should still show exactly what was disclosed, to whom, under what redaction posture, and from which frozen manifest.

## Dense row contract

A dense escalation row should preserve these labels in this order:

- `Question`
- `Recipient`
- `Orientation`
- `Included`
- `Redaction`
- `Manifest`
- `State`

## Acceptance test

This surface is good enough when a cautious operator can answer all of the following before and after disclosure:

- what precise unresolved question this packet is meant to help answer
- who the recipient is and what trust model applies
- what short orientation surface leads the packet
- which evidence is included and which is intentionally omitted
- how sensitive classes were redacted or blocked
- what cannot be recalled once the packet is sent
- what exact frozen manifest left local custody


## Companion

- `252-outbound-channel-execution-delivery-witness-and-claim-ceiling-interface-spec.md`


## Companion

- `253-shareable-artifact-carryforward-delta-ledger-and-refresh-notice-interface-spec.md`

- `258-issued-artifact-correction-notice-supersession-and-residual-reliance-interface-spec.md`
