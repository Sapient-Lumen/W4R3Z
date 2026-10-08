# Standing-approval memory and matched-arrival guardrail interface spec

## Purpose

The archive already says that approval-seat and approval horizon must be explicit when a request is first approved.
What still remained too easy to blur was what happens later when a new arrival matches remembered approval.

Resilio's current docs still keep that seam too implicit.
They say pending folders can automatically connect if the user has been approved before, the product retains approval with the person's identity so later sharing may skip fresh approval, and one approved device can be expanded to all linked devices for future sharing.
That is useful convenience.
It is not yet one trustworthy explanation of **what prior trust matched**, **what that match authorizes now**, or **what still requires a fresh local act on this machine**.

This document fixes that gap.

## Core rule

A remembered approval match is not the same thing as a local claim.

A local claim is not the same thing as a path bind.

A path bind is not the same thing as local materialization.

The interface should therefore keep four facts adjacent whenever prior trust is reused:

1. `Current arrival`
2. `Matched memory`
3. `Local outcome now`
4. `Receipt promise`

Any surface that collapses those back into one cheerful `Auto-connect` story has already started to recreate the Resilio seam we are explicitly rejecting.

## Stable remembered-trust line

Every remembered-approval case should be classifiable along one durable line:

1. **No match** — current arrival requires fresh review
2. **Matched, no auto-admit** — prior trust recognized, but only as evidence
3. **Matched, identity-only admit** — identity/contact trust is accepted, but no local claim exists yet
4. **Matched, claim-suggested** — the product may stage a claim suggestion, but bind/materialization still remain open
5. **Matched but guarded** — prior trust exists, but drift, age, or scope change forces fresh review
6. **Revoked / expired / stale** — remembered approval no longer authorizes reuse

The product must not pretend states 3 and 4 are the same.
`We know who this is` and `this machine has now claimed it` are materially different outcomes.

## Match queue row contract

A reviewed match queue should exist so later arrivals that intersect remembered approval can be triaged without pretending prior trust already finished every local step.

Every queue row should answer, in one stable order:

1. **Current arrival** — what appeared now
2. **Matched memory** — which standing approval matched and how strongly
3. **Local outcome now** — no claim, identity-only admit, claim-suggested, or blocked
4. **Next honest action** — review, suggest claim, require fresh review, tighten memory, or revoke memory
5. **Overflow / scope details** — secondary actions and drift consequences

### Example rows

```text
Photos-2026 from Maya       Match: photos-collab / exact   Claim not started    Review            Details
Archive from Studio-NAS     Match: backup-read / guarded    Identity-only admit  Fresh review      Details
Scans from Printer-NAS      Match: scans-drop / exact       Claim suggested      Suggest claim     Details
Finance from Maya           Match: none                     No admit             Fresh review      Details
```

The important part is that the row says **what matched** and **what that did not yet do locally**.
It must not imply that remembered trust already chose a path or fetched bytes.

## Review-pane contract

When the operator opens a matched-arrival row or a prepared match review, the pane should preserve one fixed section order:

1. **Arrival and match evidence**
2. **What prior trust actually covers**
3. **Local claim and bind effects**
4. **Admissible actions**
5. **Memory tighten / revoke options**
6. **Receipt promise**

### 1) Arrival and match evidence

This section should say:

- who or what arrived now
- which share, offer, or share class is in play
- which approval memory matched
- whether the match is exact, partial, stale, or blocked

The operator must be able to answer: **what matched what, and how strong is that match?**

### 2) What prior trust actually covers

This section should say:

- whether the remembered approval covered only identity trust, one share class, named members, or a broader reviewed scope
- whether the current arrival sits entirely inside that scope
- whether drift, last-use age, policy change, or authority change narrows the match
- whether a wider reuse would create more authority than the original memory promised

The operator must be able to answer: **what exactly does prior trust cover here, and where does it stop?**

### 3) Local claim and bind effects

This section should say:

- whether this machine has claimed the arrival yet
- whether any path is already chosen or still absent
- whether bytes will materialize now, later, or not at all
- whether the suggested local outcome is `identity-only`, `queue-admitted`, or `claim-suggested`

The operator must be able to answer: **what local act has actually happened here, and what has not?**

### 4) Admissible actions

This section should say:

- whether the honest next step is `Suggest claim`, `Require fresh review`, `Keep as evidence only`, `Tighten memory`, or `Revoke memory`
- which shortcuts are forbidden because they would hide local bind/materialization
- whether a safer narrower remembered-trust reuse is available from the same pane
- what later separate claim review remains if the operator takes the lower-friction path

The operator must be able to answer: **what can I safely do now without pretending a local claim already happened?**

### 5) Memory tighten / revoke options

This section should say:

- whether the matched approval should stay as-is, narrow, expire sooner, or be revoked
- whether the current arrival revealed the scope is broader than intended
- whether the product should keep reusing this memory for later arrivals
- what future friction change follows from tightening or revoking it

The operator must be able to answer: **what should happen to remembered trust itself after seeing this arrival?**

### 6) Receipt promise

This section should say:

- which receipt proves the match decision
- whether the receipt proves only recognition of prior trust or also a narrowed/revoked memory outcome
- whether a later separate claim receipt is still required
- what future expiry, review, or revocation remains open

The operator must be able to answer: **what later evidence will prove whether the product merely matched prior trust or actually changed local state?**

## Allowed primary verbs

### Good primary verbs

- `Suggest claim`
- `Require fresh review`
- `Use as evidence only`
- `Tighten memory`
- `Revoke memory`

### Dangerous ambiguous verbs

- `Auto-connect`
- `Approved before`
- `Reuse trust`
- `Accept automatically`
- `No review needed`

The archive does not ban those words in prose.
It bans them as the primary operator contract when they blur current arrival, local claim, and future remembered authority.

## Narrow auto-admit rules

A remembered-approval match may allow lower-friction outcomes, but only if those outcomes are named narrowly.

### Allowed narrow outcomes

- `identity-only` — prior trust satisfies identity/contact recognition only
- `queue-admitted` — arrival is admitted into a lower-friction queue, but no claim exists yet
- `claim-suggested` — claim drafting may be prefilled, but bind/materialization still remain future acts

### Forbidden hidden outcomes

- silently binding a default local path
- silently materializing bytes
- silently granting broader write/re-share/successor rights
- silently widening remembered scope because this arrival happened to fit

## Batch rules

Match queues may support batching, but only if the labels stay truthful.

### Acceptable labels

- `Suggest claim for 3 matched arrivals`
- `Require fresh review for 2 guarded matches`
- `Revoke 4 stale memories`

### Unacceptable labels

- `Connect selected`
- `Accept all approved-before`
- `Auto-connect all`

A batch bar may not speak for more local completion than every selected row actually shares.

## Dense and mobile rules

A dense row or mobile card may compress wording, but it must still preserve three cues:

- what matched
- what local state exists now
- whether the safe verb is lower-friction suggestion, fresh review, or memory tightening/revocation

`Prior trust matched · claim not started · Suggest claim` is acceptable compression.
`Auto-connect` is not.

## CLI contract

Minimal commands:

```text
anonsync approval match queue
anonsync approval match show apm_01J...
anonsync approval match review prepare apm_01J... --mode suggest-claim --plan
anonsync approval match review prepare apm_01J... --mode require-fresh-review --plan
anonsync approval match review prepare apm_01J... --mode tighten-memory --scope photos-collab --plan
anonsync approval match review show apmr_01J...
anonsync approval match apply apmr_01J...
anonsync approval memory show apr_01J...
anonsync approval memory revoke apr_01J...
```

These commands should answer:

- what arrived now
- which standing approval matched
- what the current local outcome is
- what still requires separate claim/bind/materialization review
- which receipt later proves the exact boundary of reused trust

## Workbench contract

The workbench should expose a `Standing approval matches` view distinct from `Approvals`, `Incoming shares`, and `Constellation`.
Its job is not merely to list matches.
Its job is to answer:

- what arrived now
- what prior trust matched
- what the local outcome is now
- which lower-friction action is honest
- what receipt will later prove whether local state changed

The queue should support:

- filtering by matched memory, scope class, drift/staleness, and current local outcome
- opening one fixed review drawer that preserves the section order above
- switching from `claim-suggested` to `fresh review` without losing sight of why the match was guarded
- tightening or revoking standing memory from the same surface without forcing a hidden admin detour

## Report-language integration

The shared report language should support at least these families here:

- `approval-match` — which current arrival matched which remembered approval and why
- `approval-memory-drift` — why a remembered match is guarded, stale, or narrower than it first appears
- `approval-auto-admit-boundary` — what the product may admit now without lying about local state

These reports should behave like any other report-backed finding: severity, freshness, scope, and safest next action remain explicit.

## Design tests

The model is not explicit enough if any of the following remains true:

- the operator can still watch a matched arrival appear as a live local folder without seeing that claim/bind/materialization were separate later acts
- `prior trust matched` and `this machine has now claimed it` still share one state label
- dense/mobile clients compress away the local outcome and leave only `approved before`
- a match can silently widen standing memory or rights instead of routing through review and receipts
- later audit cannot prove whether the product merely recognized prior trust or actually changed local state

## Freshness interaction

A remembered-approval match should always be allowed to point to the separate freshness surface defined in `106-approval-memory-freshness-cooling-and-touch-renewal-interface-spec.md` and to the later authorization-trace surface defined in `107-approval-memory-lineage-and-authorization-trace-interface-spec.md`.
`Matched` is not enough.
The row should also be able to say whether the matched trust was `fresh`, `cooling`, `stale`, `frozen`, or `revoked` when the current arrival appeared.
