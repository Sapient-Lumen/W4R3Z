from pathlib import Path

root = Path('.')

def read(p):
    return (root / p).read_text()

def write(p, s):
    (root / p).write_text(s)


def replace_once(text, old, new, path):
    if old not in text:
        raise SystemExit(f"Missing expected text in {path}: {old[:80]!r}")
    return text.replace(old, new, 1)

new_doc = '''# Subject-label and authority-identity continuity spec

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
'''

write('docs/84-subject-label-and-authority-identity-continuity-spec.md', new_doc)

# README
p = 'README.md'
t = read(p)
t = replace_once(t, '- Revision: `rev0070`\n- Timestamp: `2026.03.17.17.27` (America/New_York)\n- Codename: `seatproofreachharbor`\n', '- Revision: `rev0071`\n- Timestamp: `2026.03.17.17.42` (America/New_York)\n- Codename: `aliasproofidentityharbor`\n', p)
t = replace_once(t, 'This revision continues directly from `rev0069` and does seven things:\n\n1. Re-checks **Resilio Sync** again with extra emphasis on runtime seat drift: current docs still let current-user, Local System, Local Service, service/config mode, and Linux headless operation open materially different path/state worlds.\n2. Sharpens the **non-clone rationale** into a stricter rule: AnonSync should not let a profile or principal switch silently change which state root is active, which targets are reachable, or whether freshness falls back to rescan-only on a workaround path.\n3. Adds a dedicated **execution-seat and runtime-profile reachability review spec** so the archive now says what a real operator surface must literally show before switching runtime principal, service seat, or host-local path view.\n4. Extends the **interface and daemon/API contract** with explicit execution-seat objects and reviewed seat-switch cases rather than treating service-account and install-mode changes as launch trivia.\n5. Extends the **workbench/interface pattern language** so current seat, target seat, path reachability, and notification/freshness downgrade are visible before apply.\n6. Adds additional **canonical interface flows** for switching from an interactive user seat to a service-style seat without silently losing inventory, path reachability, or freshness truth.\n7. Refreshes the **evaluation**, **ADRs**, **roadmap**, **open questions**, **status**, and **reading order** so future revisions keep runtime-seat continuity explicit.\n', 'This revision continues directly from `rev0070` and does seven things:\n\n1. Re-checks **Resilio Sync** again with extra emphasis on the naming/identity seam: current docs still tie the chosen identity name to certificate generation, make typo repair require unlink/new-certificate work, and let convenience linking overwrite the losing device\'s identity/fingerprint story.\n2. Sharpens the **non-clone rationale** into a stricter rule: AnonSync should not let a human-facing relabel silently become a new authority, a same-person claim silently inherit old trust, or a convenience link silently rewrite continuity.\n3. Adds a dedicated **subject-label and authority-identity continuity spec** so the archive now says what a real operator surface must literally show before relabeling a subject, preserving aliases, or accepting a new authority under a familiar name.\n4. Extends the **interface and daemon/API contract** with explicit alias records, identity-continuity reviews, and identity-label receipts rather than treating names, certificates, and future-approval carry-forward as one blurred action.\n5. Extends the **workbench/interface pattern language** so operators can correct names, inspect fingerprints, and compare same-person continuity claims without losing the distinction between label hygiene and trust replacement.\n6. Adds additional **canonical interface flows** for typo-safe relabeling and same-person continuity comparison without semantic drift between CLI and richer surfaces.\n7. Refreshes the **evaluation**, **ADRs**, **roadmap**, **open questions**, **status**, and **reading order** so future revisions keep label/authority continuity explicit.\n', p)
needle = '- a first-class personal-constellation / authority-domain surface so operators can tell which members belong to a convenience-linked set, what each member may see or do, how far approvals can travel, and when a local-looking action actually reaches the wider constellation\n'
ins = needle + '- a first-class subject-label / authority-identity continuity surface so operators can correct names, preserve aliases, compare fingerprints, and decide whether a same-person claim is harmless relabeling, successor continuity, or real authority replacement\n'
t = replace_once(t, needle, ins, p)
needle = '- `docs/83-execution-seat-and-runtime-profile-reachability-spec.md` — fixed execution-seat review anatomy for runtime-principal/service-seat switch, state continuity, reachable-target delta, notification/freshness downgrade, and seat-switch receipts\n'
ins = needle + '- `docs/84-subject-label-and-authority-identity-continuity-spec.md` — fixed naming/identity review anatomy for relabeling, alias preservation, same-person continuity claims, authority replacement fallout, and identity-label receipts\n'
t = replace_once(t, needle, ins, p)
t = replace_once(t, 'then `82-safety-critical-channel-parity-and-surface-capability-spec.md`, then `83-execution-seat-and-runtime-profile-reachability-spec.md`, then `41-report-and-intervention-language.md`', 'then `82-safety-critical-channel-parity-and-surface-capability-spec.md`, then `83-execution-seat-and-runtime-profile-reachability-spec.md`, then `84-subject-label-and-authority-identity-continuity-spec.md`, then `41-report-and-intervention-language.md`', p)
write(p, t)

# status
write('docs/00-status.md', '''# Status

## Scope of this revision

This revision is an in-place continuation of `rev0070`, driven by the current request:

- continue research and tighten the archive without letting it sprawl
- evaluate Resilio Sync further with enough care that the non-clone case stays evidence-based
- spend more time on interface specs rather than letting naming, certificate continuity, and same-person claims hide inside convenience linking or typo-repair ritual
- keep Linux-first, overlay-first, and least-privilege assumptions intact unless evidence truly breaks them
- keep turning support-lore seams into explicit product contracts
- make sure the archive has a better reason not to clone current Resilio naming/identity behavior as though a human-facing label, a cryptographic authority, and a convenience constellation were the same object
- make sure subject relabeling, alias preservation, peer-visible naming, successor continuity, and authority replacement stay visibly separate

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

The archive now contains:

- a deeper Resilio-derived warning that current identity naming still couples a user-visible label to certificate generation and can turn typo repair into unlink/new-certificate ritual
- a dedicated **subject-label and authority-identity continuity spec** that says what a real operator surface must show before renaming a subject, preserving an alias, or accepting a new authority under an old name
- stronger interface and daemon/API requirements so alias records, continuity reviews, and identity-label receipts become explicit public objects rather than side effects of linking or unlinking
- stronger workbench and pattern-language rules so operators can see label scope, authority continuity, peer-visible fallout, and constellation/grant consequences before apply
- additional canonical flows for typo-safe relabeling and same-person continuity comparison without semantic drift between CLI and richer surfaces
- roadmap, ADR, status, open-question, and README updates so future revisions keep naming and authority continuity explicit

## The main shift

`rev0070` proved that runtime-seat changes needed one explicit continuity/reachability contract rather than installer and service-account folklore.

`rev0071` applies the same discipline one layer closer to identity itself:

> a serious Linux-first workbench still is not specified tightly enough if the archive can define constellation membership, successor cutover, compromise response, and execution seats, yet still leave the next hard question loose: whether changing a visible name preserves the same trusted subject, whether an alias is only historical convenience, and whether a same-person claim is actually a new authority with blast radius.

That changes the archive in six specific ways:

- a human-facing label can now change without pretending authority changed too
- a new authority claiming an old name can no longer hide inside convenience linking or casual relabel actions
- peer-visible naming fallout is now separated from local-only hygiene and audit aliases
- future-approval and constellation fallout must now be visible before continuity changes are accepted
- the Resilio comparison now lands a sharper non-clone argument: the weak seam is not merely device linking, but the lack of one honest reviewed boundary between naming convenience and authority continuity
- future interface work now has a narrower quality bar for personal meshes, successor adoption, label cleanup, and replacement flows

## What still remains unresolved

This revision intentionally does **not** overclaim closure on several important questions:

- how much of transport identity and overlay publication should be device-wide, share-scoped, or policy-scoped
- how strong disclosure-narrowing guarantees should be before the product becomes noisy or dishonest about residue
- how aggressive the default review queue should be before it becomes noisy
- how much UI simplification is safe without recreating the hidden coupling the archive is trying to escape
- how much one-click automation an exit surface should allow before it starts hiding scope, residue, or follow-up obligations
- how aggressive default compromise freezes should be before the product starts turning suspicion into disruptive magic
- when long-offline or clock-uncertain peers should be allowed to resume writable participation without first-class re-entry review
- when remote delete or overwrite waves should always force destructive-replay review instead of ordinary sync progress
- when non-trivial conflicts should always force full reviewed adjudication instead of a safely compressed resolution path
- when same-host derivations should always force full local-derivation review instead of a safely compressed path
- when live authority changes should always force full authority-mutation review instead of a safely compressed access-change path
- when nested, overlapping, or root-boundary-sensitive topology changes should always force full topology review instead of a safely compressed path
- when writer contention, burst-save delay, or mixed external-writer risk should always force full contention review instead of a safely compressed path
- when RAM pressure, watcher ceilings, indexing cost, or path blockers should always force full capacity-fit review instead of a safely compressed path
- when discovered state, recovery material, or reviewed control exposure should always force full bring-up review instead of a safely compressed startup path
- how broad one reviewed mutation grant may be in v1 before explicit authority becomes either too reusable or too noisy
- when an obviously same-lineage local target may use a safely compressed custody review versus always opening the full ownership-and-lineage sheet
- how much low-risk cross-channel continuation may stay compressed before channel-parity honesty becomes either noisy or too magical
- how much low-risk runtime-seat switching may stay compressed before state continuity, path reachability, and freshness honesty become either noisy or too magical
- how much low-risk relabeling may stay compressed before the product starts hiding meaningful authority replacement or same-person continuity fallout behind harmless-looking naming affordances

## Files added in this revision

- `docs/84-subject-label-and-authority-identity-continuity-spec.md`

## Files updated in this revision

- `README.md`
- `docs/00-status.md`
- `docs/10-resilio-sync-evaluation.md`
- `docs/30-interface-spec.md`
- `docs/31-daemon-api-spec.md`
- `docs/32-interface-flows.md`
- `docs/38-operator-workbench-interface-spec.md`
- `docs/39-interface-pattern-language.md`
- `docs/40-architecture-decisions.md`
- `docs/50-roadmap.md`
- `docs/64-critical-open-questions.md`
''')

# evaluation
p = 'docs/10-resilio-sync-evaluation.md'
t = read(p)
insert = '''### 16o) Human labels, cryptographic authority, and same-person continuity are still coupled too tightly

Resilio's own docs expose another seam that matters more than it first appears.
`Can I change the name of my Sync identity?` says the chosen identity name is used to generate the digital certificate, so there is no simple rename path; changing the name requires unlinking the current identity and creating a new certificate, which removes Advanced folders from that instance and forces relink work elsewhere.
`Sync Private Identity & Linking My Devices` says each installation gets a unique certificate generated from the selected identity name, that linked devices can auto-approve all linked devices for future sharing, that linking one configured device into another can cause the latter to take the former's identity name, fingerprint, and configured shares, and that linking two already-running devices can make one lose its certificate entirely.
The same guide says mixed v2/v3 linking can conflict on licensing and cost access to UI and share configuration, and that you cannot remotely unlink other devices.

That is useful support knowledge.
It is not yet one public continuity model.

The practical consequence is that four different truths keep collapsing together:

- a harmless label correction
- peer-visible renaming for recognition
- same-person convenience linking
- real authority replacement with grant and approval fallout

If the operator still has to remember that fixing a typo means `unlink`, that `same name` is not `same certificate`, that convenience linking can overwrite the losing device's continuity story, and that future approvals may still key off the wider linked constellation, the interface is not explicit enough.

AnonSync should instead publish one public naming/identity model with:

- mutable human-facing labels separated from stable subject handles and cryptographic authority
- explicit alias history so old names remain searchable without pretending authority changed
- reviewed same-person continuity cases that say whether the candidate is the same authority, a successor-supported new authority, or an unrelated subject with a familiar name
- explicit grant/constellation fallout before any continuity claim is accepted
- durable identity-label receipts proving whether the action was cosmetic relabeling, peer-visible rename, or real authority replacement

'''
t = replace_once(t, '\n\n## Final judgment\n', '\n\n' + insert + '## Final judgment\n', p)
req = '''### Requirement 44 — subject naming and authority continuity must stay visibly separate

If the operator still has to remember that a typo fix means unlinking, that the same name does not prove the same authority, that convenience linking can rewrite the losing device's continuity story, and that future approvals may still travel across a wider linked constellation, the product has not actually exposed its naming/identity contract.

AnonSync should instead publish one public model with mutable labels, alias history, stable subject handles, explicit authority continuity reviews, and receipts that prove whether an action was only cosmetic relabeling or a real trust/continuity change.
'''
t = t.rstrip() + '\n\n' + req + '\n'
write(p, t)

# interface spec
p = 'docs/30-interface-spec.md'
t = read(p)
old = '''### Execution-seat receipt

A durable record proving whether a reviewed runtime-seat change preserved state continuity, degraded reachability/freshness, required rebind, or opened a clean runtime world.

Fields:

- `execution_seat_receipt_id`
- `review_ref`
- `source_execution_seat_ref`
- `target_execution_seat_ref`
- `continuity_summary`
- `reachability_summary`
- `freshness_summary`
- `outcome_summary`
- `actor_ref`
- `created_at`

### Plan
'''
new = '''### Execution-seat receipt

A durable record proving whether a reviewed runtime-seat change preserved state continuity, degraded reachability/freshness, required rebind, or opened a clean runtime world.

Fields:

- `execution_seat_receipt_id`
- `review_ref`
- `source_execution_seat_ref`
- `target_execution_seat_ref`
- `continuity_summary`
- `reachability_summary`
- `freshness_summary`
- `outcome_summary`
- `actor_ref`
- `created_at`

### Subject alias record

A durable mapping between mutable labels, stable subject handles, and known authority continuity.
This exists so typo repair, peer-visible rename, alias history, and same-person continuity do not collapse into one hidden identity ritual.

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

A durable, reviewed case for relabeling a subject or comparing a new authority claim without guessing whether the same person story still preserves the same trusted subject.

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

A durable record proving what label changed, what authority continuity was preserved or replaced, and what wider constellation or grant fallout was accepted.

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

### Plan
'''
t = replace_once(t, old, new, p)
write(p, t)

# daemon api
p = 'docs/31-daemon-api-spec.md'
t = read(p)
needle = 'Constellation membership should compose with contact, approval, policy, and release resources rather than shadowing them with a second hidden model.\n\n\n### Target custody and exclusive binding\n'
insert = '''Constellation membership should compose with contact, approval, policy, and release resources rather than shadowing them with a second hidden model.

### Subject naming and identity continuity

```text
GET   /v1/identity/subjects/{subject_ref}/alias
PATCH /v1/identity/subjects/{subject_ref}/alias
POST  /v1/identity/subjects/{subject_ref}:prepare-continuity-review
GET   /v1/identity/continuity/reviews/{identity_continuity_review_id}
POST  /v1/identity/continuity/reviews/{identity_continuity_review_id}:apply
GET   /v1/identity/continuity/receipts
GET   /v1/identity/continuity/receipts/{identity_label_receipt_id}
```

These resources exist so clients can answer one ordinary operator question without `rename means new certificate` folklore:

- what the current label, peer-visible label, stable subject handle, and authority fingerprint actually are
- whether a requested rename is local-only hygiene, peer-visible relabel, alias preservation, or a new-authority continuity claim
- whether the same authority remains active or the action really implies successor/replacement work
- what future approvals, constellation defaults, or grant boundaries would widen, narrow, or reset if the continuity story changes
- which receipt later proves that the action was cosmetic relabeling versus real trust fallout

A relabel response should answer at least:

- current and requested labels, with explicit visibility scope
- stable subject handle and current authority fingerprint summary
- whether the same authority remains intact
- whether previous labels remain searchable as aliases
- whether any peer observation is still pending
- which receipt will later prove the rename outcome

An identity-continuity review response should answer at least:

- current subject and candidate authority summaries
- whether the candidate is same-authority, same-person-new-authority, authority-uncertain, or authority-replacing
- whether the action can stay in this naming surface or must escalate into successor, compromise, or constellation review
- what constellation/grant/future-approval fallout would occur if accepted
- which actions remain admissible now: relabel-only, alias-only, keep separate, escalate, or block

### Target custody and exclusive binding
'''
t = replace_once(t, needle, insert, p)
write(p, t)

# flows
p = 'docs/32-interface-flows.md'
t = read(p)
append = '''

## Flow 123 — correct a device label typo without rotating authority

Goal: fix a peer-visible name while proving the same trusted subject and same authority remain in place.

```text
$ anonsync subject show dev_laptop
Subject: dev_laptop
Current label: jonnys-laptop
Peer-visible label: jonnys-laptop
Authority fingerprint: fp_9f2c...
Continuity class: same-authority
Previous labels: none

$ anonsync subject relabel dev_laptop --label johnny-laptop --scope peer-visible --plan
Identity continuity review: icr_01NV...

Requested action: peer-visible-relabel
Current subject: dev_laptop
Current authority: fp_9f2c...
Candidate authority: same as current

Continuity verdict:
  same-authority
  no grant or constellation widening

Peer-visible fallout:
  contacts will observe new label at next normal observation
  previous label will remain searchable as alias

Receipt promise:
  ilr_01NW... will prove relabel-only with unchanged authority

Safest next action: Apply relabel

$ anonsync subject relabel dev_laptop --label johnny-laptop --scope peer-visible --apply
Applied.
Receipt: ilr_01NW...
```

What this proves:

- a label correction does not silently regenerate authority
- peer-visible naming changes keep the same trust subject unless the review says otherwise
- alias history survives for audit and search

## Flow 124 — compare a same-person claim before accepting new authority under an old name

Goal: inspect a candidate replacement device that looks like the same human subject without pretending name similarity is enough proof.

```text
$ anonsync identity continuity prepare dev_laptop --candidate dev_laptop_new --claim same-person --plan
Identity continuity review: icr_01NX...

Current subject:
  label: johnny-laptop
  authority: fp_old_73...

Candidate subject:
  label: johnny-laptop
  authority: fp_new_11...

Continuity verdict:
  same-person-new-authority
  successor proof: missing
  automatic future-approval carry-forward: blocked

Grant and constellation fallout:
  3 future-approval paths would be reset
  2 linked members would remain separate unless successor review succeeds

Admissible actions:
  - keep separate subject
  - add alias only
  - open successor cutover review
  - reject same-person continuity claim

Receipt promise:
  no relabel receipt until one admissible action is chosen
```

What this proves:

- same label is not treated as same authority
- convenience continuity claims do not silently inherit approvals or grants
- successor/replacement work stays visibly separate from harmless rename hygiene
'''
t = t.rstrip() + append + '\n'
write(p, t)

# workbench
p = 'docs/38-operator-workbench-interface-spec.md'
t = read(p)
needle = '## Execution-seat and runtime-profile switch surface\n'
insert = '''## Identity and naming continuity page

The workbench should expose one page for naming a subject without lying about authority continuity.
This page is not profile polish.
It is where the product proves that a typo fix, a peer-visible rename, alias history, and a same-person continuity claim are not the same action.

The page should show at least:

- current label and stable subject handle
- current peer-visible label and visibility scope
- current authority fingerprint summary
- previous labels / aliases
- continuity verdict (`same-authority`, `same-person-new-authority`, `uncertain`, `replacement`)
- current and candidate grant / constellation fallout when relevant
- recent identity-label receipts and any pending peer observation

Its primary actions should be:

- relabel locally only
- prepare peer-visible relabel
- add or retire an alias
- compare a candidate same-person authority claim
- escalate into successor / compromise / constellation review when the continuity story is no longer cosmetic
- inspect recent identity-label receipts

No editable label field on this page should silently regenerate authority, inherit future approvals, or merge subjects just because their names look similar.

## Execution-seat and runtime-profile switch surface
'''
t = replace_once(t, needle, insert, p)
write(p, t)

# pattern language
p = 'docs/39-interface-pattern-language.md'
t = read(p)
needle = '## Pattern 17 — transfer cards must answer route, budget, and queue truth\n'
insert = '''## Pattern 16b — labels and authority continuity must not share one casual rename affordance

A good sync product should let operators fix names.
A trustworthy sync product should also make sure a name edit does not quietly become a trust rewrite.

Required rules:

- local-only relabel, peer-visible relabel, alias history, and authority replacement must remain visibly different actions
- the same label must not be treated as proof of the same authority, and a new label must not be treated as proof of authority rotation
- any action that would replace authority or inherit future approvals must escalate into continuity review rather than save inline from a text field
- peer-visible scope and alias retention must be shown before apply
- successor, compromise, or constellation review escalation must stay obvious when the continuity story stops being cosmetic

This matters because a product can define good subject handles, authority domains, and successor workflows on paper and still regress in practice if `Rename`, `Link`, or `Looks like the same laptop` quietly rewrites the trust story.

## Pattern 17 — transfer cards must answer route, budget, and queue truth
'''
t = replace_once(t, needle, insert, p)
write(p, t)

# ADR
p = 'docs/40-architecture-decisions.md'
t = read(p)
append = '''

## ADR-084 — Human-facing labels must stay separate from authority identity and same-person continuity

**Decision:** Non-trivial naming work should compile to one reviewed label/identity continuity model rather than depending on unlink/new-certificate ritual, convenience linking, or remembered fingerprint lore.

**Why:** Current Resilio docs still spread naming/continuity meaning across identity-name-generated certificates, rename-via-unlink behavior, linked-device auto-approval reach, configured-device takeover during linking, mixed-version linking warnings, and local-only unlink limits. AnonSync should keep mutable labels, stable subject handles, cryptographic authority, alias history, and same-person continuity visibly distinct.

**Consequences:**

- naming work gains a stable review grammar and durable identity-label receipts
- workbench and CLI both need explicit current-label/authority, peer-visible fallout, and grant/constellation-fallout sections
- harmless relabel, alias preservation, successor continuity, and authority replacement remain visibly different public actions
- convenience linking can no longer masquerade as safe continuity proof when the real effect is trust or approval blast-radius change
'''
t = t.rstrip() + append + '\n'
write(p, t)

# roadmap
p = 'docs/50-roadmap.md'
t = read(p)
t = replace_once(t, '- execution-seat, seat-switch-review, and seat-switch-receipt object model\n- target-custody-record, binding-collision-case, and custody-receipt object model\n', '- execution-seat, seat-switch-review, and seat-switch-receipt object model\n- subject-alias-record, identity-continuity-review, and identity-label-receipt object model\n- target-custody-record, binding-collision-case, and custody-receipt object model\n', p)
t = replace_once(t, '- inspect/compare/receipt surfaces for personal-constellation membership, member class, and authority-domain scope\n', '- inspect/compare/receipt surfaces for personal-constellation membership, member class, and authority-domain scope\n- inspect/relabel/alias/continuity surfaces for subject naming versus authority identity\n', p)
t = replace_once(t, '- operators can change a live member\'s access without falling back to folder-class switches, disconnect ritual, or remove/re-share folklore, and can prove later what authority boundary changed\n', '- operators can change a live member\'s access without falling back to folder-class switches, disconnect ritual, or remove/re-share folklore, and can prove later what authority boundary changed\n- operators can fix a device or peer label without silently rotating authority, and can tell when a familiar name is actually a new trusted subject with different blast radius\n', p)
t = replace_once(t, '- review-model projection for execution-seat and runtime-profile switching so rich and textual clients render the same continuity, reachability, and freshness sections\n', '- review-model projection for execution-seat and runtime-profile switching so rich and textual clients render the same continuity, reachability, and freshness sections\n- review-model projection for subject-label and authority-identity continuity so rich and textual clients render the same label, fingerprint, fallout, and receipt-promise sections\n', p)
t = replace_once(t, '- operators can tell whether switching runtime principal or service seat preserves the same state world, target reachability, and freshness guarantees or instead requires reviewed rebind or clean-seat start\n', '- operators can tell whether switching runtime principal or service seat preserves the same state world, target reachability, and freshness guarantees or instead requires reviewed rebind or clean-seat start\n- operators can tell whether a same-person rename/replacement request is cosmetic relabeling, alias history, successor continuity, or real authority replacement before any trust shortcuts are inherited\n', p)
write(p, t)

# open questions
p = 'docs/64-critical-open-questions.md'
t = read(p)
append = '''

## 52) How much low-risk relabeling can stay compressed before naming honesty becomes either noisy or too magical?

The archive is now clearer that mutable labels, stable subject handles, and cryptographic authority should use first-class continuity reviews and receipts, but one policy seam remains open:

- when should an obvious typo fix be allowed to apply from inline UI versus always opening the full continuity sheet
- how much alias history should remain peer-visible by default versus local-only for audit and search
- whether some same-authority relabels may safely preserve future-approval memory without re-showing broader blast radius every time
- when repeated same-person continuity claims should escalate into successor or compromise review because the naming story has stopped being ordinary hygiene

This matters because weak defaults recreate `rename means unlink`, `same name means same device`, and convenience-link folklore, while overly strict defaults could make harmless label cleanup feel ceremonial instead of trustworthy.
'''
t = t.rstrip() + append + '\n'
write(p, t)

