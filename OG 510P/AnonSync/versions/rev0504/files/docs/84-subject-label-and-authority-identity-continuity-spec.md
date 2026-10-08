# Subject-label and authority-identity continuity spec

The archive already has personal constellations, authority domains, successor cutover, compromise response, and execution-seat review.
This document answers a narrower seam those abstractions still left too loose:

> what must a real operator surface literally show when a human-facing name changes, a same-person claim appears, or a device wants to inherit an older subject's trust story, so AnonSync does not drift back into `rename means new certificate`, `same name means same peer`, or `link it and hope` folklore?

This is the naming/identity companion to `61-personal-constellation-and-authority-domain-spec.md`, the continuity companion to `67-link-and-constellation-join-interface-spec.md`, and the authority-safe relabel companion to `68-successor-cutover-and-rehome-interface-spec.md`.

## Why this needs its own spec

Resilio's docs make the seam unusually clear.
`Can I change the name of my Sync identity?` says the chosen identity name is used to generate the digital certificate, so there is no simple rename path; changing the name requires unlinking the current identity and generating a new certificate, which removes Advanced folders from that Sync instance and forces relink work on other devices.
`Sync Private Identity & Linking My Devices` says each install gets a unique certificate based on the selected identity name, that linked devices can auto-approve all linked devices for future sharing, that linking one configured device into another can cause the latter to take the former's identity name, fingerprint, and configured shares, and that linking two already-running devices can make one lose its certificate altogether.
The same guide says mixed v2/v3 linking can conflict on licensing and cost access to UI and share configuration, and that you cannot remotely unlink other devices.

The lesson is not merely that identity is important.
The lesson is that a useful product can still leave one of the most dangerous trust questions under-specified:

- is this a harmless label correction, or a new cryptographic authority?
- is this the same subject under a new name, or a new subject claiming the old name?
- is this a convenience-link action, a successor cutover, or an authority replacement with grant fallout?
- what future approvals, constellation defaults, or peer-visible labels change if I accept the new continuity story?

AnonSync should not clone that shape.

## Core rule

Human-facing labels, stable subject handles, and authority identities must remain separate public facts.
A rename may be:

- local-label-only
- peer-visible relabel with same authority
- alias add for history/search
- same-person new-authority claim
- authority replacement requiring broader review
- blocked / inspect-only

A rename may not silently regenerate authority, silently inherit future approvals, or silently merge a new authority into an older subject story just because the names look similar.

## Which actions are in scope

This spec is about any action where names and authority continuity could otherwise collapse together.
That includes at least:

- correcting or normalizing a device/person/workbench label
- changing what peers see for the same underlying authority
- preserving old labels as aliases for search and audit
- comparing a candidate new authority against an older known subject
- deciding whether a same-person claim is relabel, successor, replacement, or separate membership
- any action where label convenience could widen future approvals, contact trust, or constellation scope

Low-risk local notes can stay lighter.
High-signal label/identity continuity cases cannot.

## Vocabulary

### Subject label

A mutable human-facing name for one subject.
A label may be local-only, peer-visible, or constellation-scoped.
It is not proof of authority continuity.

### Authority identity

The stable cryptographic identity currently bound to a subject for trust, grants, approval memory, and peer recognition.
Authority identity is what continuity review protects.

### Alias record

A durable record connecting current and previous labels to the same subject and, where known, the same authority identity.
This exists so typo repair and renaming do not destroy auditability.

### Identity-continuity review

A reviewed case that answers whether a requested name/continuity action preserves the same authority, introduces a new authority, or requires broader successor/compromise/replacement handling.

### Identity-label receipt

A durable record proving what label changed, what authority continuity was preserved or replaced, and what share/constellation/grant fallout was accepted.

## Fixed review order

Every non-trivial naming or identity-continuity review should render the same sections in the same order:

1. **Requested naming or continuity action**
2. **Stable subject and authority continuity**
3. **Peer-visible label and approval fallout**
4. **Constellation, grant, and replacement fallout**
5. **Admissible actions**
6. **Receipt promise**

### 1) Requested naming or continuity action

This section should show:

- current subject label and stable subject handle
- requested new label or candidate alias
- current authority identity summary and candidate authority summary when relevant
- requested action class (`relabel-only`, `peer-visible-relabel`, `alias-add`, `same-person-new-authority`, `authority-replacement`, `inspect-only`)
- whether the action is low-risk naming hygiene, guarded continuity review, or high-signal trust replacement

The operator must be able to answer: **am I trying to rename, to preserve history, or to change the authority story itself?**

### 2) Stable subject and authority continuity

This section should show:

- whether the same authority remains active
- whether the subject handle remains the same while the label changes
- whether the candidate authority is merely related, successor-supported, authority-uncertain, or authority-replacing
- whether the action should stay here or escalate into successor, compromise, or constellation-join review

The operator must be able to answer: **is this still the same trusted subject, or a new authority wearing a familiar label?**

### 3) Peer-visible label and approval fallout

This section should show:

- whether the new label is local-only or peer-visible
- what peers/contacts will observe and when
- whether approval memory, trust hints, or peer-facing fingerprints stay valid under the requested change
- whether old labels remain searchable or visible as historical aliases

The operator must be able to answer: **who will see the new name, and what future trust shortcuts stay valid — if any?**

### 4) Constellation, grant, and replacement fallout

This section should show:

- whether constellation membership or member-class defaults stay the same
- whether future approvals, share visibility, or grant boundaries would widen, narrow, or be reset
- whether the action implies successor carry-forward, fresh join, authority rotation, or no trust fallout at all
- whether a separate replacement/rotation review is required before apply

The operator must be able to answer: **does this name change stay cosmetic, or does it change the larger trust graph?**

### 5) Admissible actions

This section should show:

- whether the honest next step is relabel now, add alias only, escalate to successor review, keep separate subjects, or block
- which shortcuts are forbidden because they would hide authority replacement
- whether the product can offer a safely compressed path because authority continuity is already proven
- what follow-up remains if the operator defers the broader review

The operator must be able to answer: **what can I safely do right now without lying about continuity?**

### 6) Receipt promise

This section should show:

- which identity-label receipt will exist after apply, defer, or refusal
- what it will later prove about labels, aliases, authority continuity, and any grant/constellation fallout
- whether later peer observation is still pending for peer-visible rename work
- where later audit survives if the action resumes from another channel

The operator must be able to answer: **what later evidence will prove that this was only a rename — or prove that it was not?**

## Public objects

### Subject alias record

Fields:

- `subject_alias_record_id`
- `subject_ref`
- `authority_identity_ref` nullable
- `current_label`
- `previous_labels[]`
- `peer_visible_label` nullable
- `label_scope` (`local-only`, `peer-visible`, `constellation-wide`, `mixed`)
- `continuity_class` (`same-authority`, `same-person-new-authority`, `authority-uncertain`, `authority-replaced`)
- `last_changed_at`
- `provenance_ref` nullable

### Identity-continuity review

Fields:

- `identity_continuity_review_id`
- `subject_ref`
- `requested_action` (`relabel-only`, `peer-visible-relabel`, `alias-add`, `same-person-new-authority`, `authority-replacement`, `inspect-only`)
- `current_authority_identity_ref` nullable
- `candidate_authority_identity_ref` nullable
- `continuity_expectation` (`same-authority`, `same-person-new-authority`, `authority-uncertain`, `authority-replacement`)
- `label_findings[]`
- `authority_findings[]`
- `grant_and_constellation_fallout[]`
- `action_options[]`
- `identity_continuity_report_ref`
- `generated_at`
- `expires_at` nullable

### Identity-label receipt

Fields:

- `identity_label_receipt_id`
- `review_ref`
- `subject_ref`
- `authority_continuity_summary`
- `label_change_summary`
- `grant_scope_summary`
- `constellation_scope_summary`
- `actor_ref`
- `created_at`

## What the surface must never imply

The naming/identity surface must never imply that these are the same thing:

- changing a label versus replacing a cryptographic authority
- seeing the same name versus proving the same trusted subject
- same-person convenience versus safe future-approval carry-forward
- hiding an offline row versus unlinking or revoking the remote subject
- linking a device into a constellation versus proving successor continuity
- correcting a typo versus accepting new blast radius on grants or authority domains

If the product compresses those differences, it has recreated the ritual it is trying to replace.

## CLI shape

Examples:

```text
anonsync subject show dev_laptop
anonsync subject relabel dev_laptop --label johnny-laptop --scope peer-visible --plan
anonsync subject alias add dev_laptop --alias johnnys-laptop
anonsync identity continuity prepare dev_laptop --candidate dev_new --claim same-person --plan
anonsync identity continuity show icr_01J...
anonsync identity continuity apply icr_01J...
anonsync receipts show ilr_01J...
```

The point is not the exact spelling.
The point is that label work and authority replacement work remain visibly different verbs.

## Workbench shape

The workbench should expose a dedicated naming/identity continuity view whenever a label change could alter peer recognition, approval carry-forward, or subject continuity.
That view should not hide cryptographic continuity inside an editable text field.

A minimal page should show:

- current label and stable subject handle
- current authority fingerprint summary
- previous labels / aliases
- requested new label and scope of visibility
- continuity verdict (`same-authority`, `same-person-new-authority`, `uncertain`, `replacement`)
- grant / constellation fallout summary
- admissible next actions
- receipt promise

This page may be compact.
It may not compress rename, alias, successor, and replacement into one casual `Save` action.
