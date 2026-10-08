# External-guidance source boundary, fetch snapshot, and frozen-review-basis interface spec

## Purpose

The archive already says that:

- outside instructions enter AnonSync as untrusted guidance objects
- copied commands and vendor prose must be translated into typed local objects before approval
- support packets, evidence bundles, and outside-product blocker detours are separate objects with separate truth states

What still remained under-specified was one smaller but now important source-truth seam:

> when outside guidance lives at a mutable URL, help-center page, ticket thread, forum reply, wiki page, or copied message, what proves the exact **frozen basis** that the operator actually reviewed and translated, instead of leaving later operators to treat one live source locator as though it were the stable reviewed instruction itself?

Real systems blur at least four different things into one `source link` row:

- the **live source locator** that may later redirect, drift, disappear, or change text
- the **fetched snapshot** of what the product actually saw at one moment
- the **quoted review basis** that local translation and approval were grounded on
- the **typed local objects** created from that basis

That flattening creates three different lies:

1. **live-source-as-basis** — the product behaves as though the currently visible page is the same object that was reviewed earlier;
2. **authority-collapse** — a reviewed host boundary, a successful fetch, and exact reviewed bytes/excerpts are treated as the same trust fact;
3. **drift-erases-history** — later edits to the upstream page silently rewrite what the older local review appears to have approved.

This document defines the interface contract for keeping those truths separate.

## Core rule

A live external source locator is not itself the reviewed basis.

AnonSync may keep one live locator for convenience and one current authority/fetch posture for follow-up.
But any local translation, approval, recipe, probe, or packet must point to one **frozen fetched snapshot** and one explicit **review basis excerpt set**.
Later drift checks may change what the product says about the live source now.
They must not rewrite the earlier local review basis or its receipts.

## Why this needs its own spec

`142-external-guidance-intake-and-translation-review-interface-spec.md` already says outside guidance is not self-executing and must be translated into typed local objects.
`140-external-escalation-packet-and-redaction-review-interface-spec.md` already keeps private evidence distinct from recipient-specific disclosure.
`245-external-blocker-handoff-followup-and-return-proof-interface-spec.md` already says browser / shell / vendor detours need typed return proof.

Those are necessary, but they still leave one important seam loose.
Without an explicit source-boundary and frozen-basis contract, the product can still lie by implication:

- a help-center URL may be stored as though it were the exact reviewed instruction
- a teammate paste may later be edited while older local review still appears current
- a forum or vendor page may redirect or disappear and erase what the operator originally saw
- a host allowlist or `official source` badge may be mistaken for exact quoted review basis
- a later translated recipe may appear grounded in the current live page rather than the exact snapshot and excerpts that were reviewed

Other comparison archives sharpened this seam in a directly portable way:

- a stable public surface is not the same thing as a candidate or live working tree
- allowed authority host is not the same thing as exact reviewed bytes
- exact reviewed bytes are not the same thing as imported downstream claims

AnonSync should import that discipline directly.

## Public objects

### External guidance source row

A compact read object describing one live outside source reference.

Suggested fields:

- `external_guidance_source_row_id`
- `guidance_intake_ref`
- `source_kind` (`official-doc`, `support-reply`, `forum-post`, `ticket-thread`, `wiki-page`, `teammate-note`, `copied-command-block`, `file-attachment`, `unknown`)
- `source_locator`
- `authority_posture` (`official-allowlisted`, `official-but-unpinned`, `known-third-party`, `private-human-source`, `unknown`, `blocked`)
- `fetch_path_class` (`manual-opened`, `product-fetched`, `ticket-attachment`, `copy-paste-only`, `quoted-in-message`, `redirect-followed`, `unknown`)
- `live_source_state_now` (`reachable-same`, `reachable-changed`, `redirected`, `gone`, `access-lost`, `not-rechecked`, `unknown`)
- `latest_snapshot_ref` nullable
- `latest_drift_check_ref` nullable
- `next_honest_action`

### Guidance fetch snapshot

A durable locally retained copy of what the product actually fetched or ingested at one moment.

Suggested fields:

- `guidance_fetch_snapshot_id`
- `guidance_intake_ref`
- `source_row_ref`
- `fetched_at`
- `fetch_actor` (`operator`, `daemon`, `imported-attachment`, `clipboard`, `unknown`)
- `retrieval_posture` (`verbatim-page`, `attachment-copy`, `quoted-excerpt-only`, `rendered-text-extract`, `unknown`)
- `snapshot_integrity_summary`
- `content_hash`
- `content_length`
- `title_at_fetch` nullable
- `redirect_chain_summary` nullable
- `warnings[]`

### Frozen guidance basis row

One explicit excerpt or clause set from a specific snapshot that local translation is allowed to rely on.

Suggested fields:

- `frozen_guidance_basis_row_id`
- `guidance_intake_ref`
- `snapshot_ref`
- `basis_kind` (`quoted-excerpt`, `clause-set`, `copied-command`, `field-value`, `attachment-section`, `operator-summary-backed-by-excerpts`)
- `basis_excerpt_summary`
- `basis_offsets_or_locator`
- `basis_completeness_state` (`exact-clause`, `multi-clause`, `partial-context`, `operator-summarized`, `unknown`)
- `authority_claim_at_review` (`host-only`, `snapshot-only`, `exact-excerpt-reviewed`, `human-source-stated`, `unknown`)
- `used_by_translation_refs[]`
- `used_by_receipt_refs[]`

### Guidance drift-check row

A durable comparison object describing what changed between the frozen snapshot and the live source later.

Suggested fields:

- `guidance_drift_check_row_id`
- `source_row_ref`
- `basis_snapshot_ref`
- `checked_at`
- `drift_verdict` (`same-visible-content`, `minor-presentation-change`, `material-text-change`, `redirected`, `unreachable`, `auth-changed`, `unknown`)
- `review_impact` (`none`, `followup-only`, `translation-should-be-rechecked`, `basis-no-longer-trustworthy`, `unknown`)
- `summary`
- `next_honest_action`

### Guidance basis receipt

A durable object proving the exact frozen local basis that a translated object or later decision relied on.

Suggested fields:

- `guidance_basis_receipt_id`
- `guidance_intake_ref`
- `source_row_ref`
- `snapshot_ref`
- `basis_row_refs[]`
- `translation_refs[]`
- `live_source_state_at_issue`
- `issued_at`
- `receipt_summary`

## Stable truth line

Every external-guidance lane should be classifiable along one durable line:

1. **Live source known** — there is a locator, but no fetched local snapshot yet
2. **Snapshot fetched** — the product has a retained local copy of what was seen
3. **Frozen basis selected** — one exact clause/excerpt set has been marked as the review basis
4. **Translated locally** — typed local objects exist and point back to that basis
5. **Live source drift checked** — the live page was later compared and classified
6. **Recheck required or still valid** — later drift may require follow-up, but does not rewrite the earlier basis receipt

The product must not pretend states 1, 2, 3, and 5 are the same.
`official page`, `fetched copy`, `exact reviewed excerpt`, and `still same upstream now` are materially different operator facts.

## Dense row contract

A compact guidance row may compress the story, but it must preserve one stable answer to five separate questions:

1. **Where is the live source?**
2. **What exact snapshot did we actually fetch?**
3. **Which frozen excerpt set is the approved review basis?**
4. **Which local translations depend on that basis?**
5. **Has the live source drifted since then?**

### Example rows

```text
Vendor article /logs-manual   Snapshot: 2026-03-20 12:11   Basis: exact excerpt set   Drift: not rechecked     Translate to probe
Support reply ticket-4821     Snapshot: message copy        Basis: copied command row   Drift: unreachable now   Keep receipt
Forum thread post 7           Snapshot: fetched page        Basis: partial-context       Drift: material change   Recheck
```

The row must not let one `Source` badge answer all of those questions.

## Fixed inspection order

Every guidance-basis surface should preserve this order:

1. **Live source and authority boundary**
2. **Fetched local snapshot**
3. **Frozen review basis excerpts**
4. **Translated local objects and unsupported residue**
5. **Drift checks and follow-up actions**

### 1) Live source and authority boundary

The surface should show:

- source kind and locator
- authority posture
- fetch path class
- whether the locator is still reachable / redirected / gone now

The operator should be able to answer:

> what outside source are we talking about, and how much authority does that locator itself honestly carry?

### 2) Fetched local snapshot

This section should show:

- when the snapshot was fetched or ingested
- how it was fetched
- integrity summary / content hash
- redirect or retrieval warnings

The operator should be able to answer:

> what exact local copy did the product actually see and retain?

### 3) Frozen review basis excerpts

This section should show:

- the exact excerpt or clause set the translation is grounded on
- whether context is full or partial
- whether the basis is host-only, snapshot-only, or exact-excerpt reviewed
- which later receipts point to this basis

The operator should be able to answer:

> what exact instruction text did we really review, not merely which page did we once visit?

### 4) Translated local objects and unsupported residue

This section should show:

- typed local objects created from the basis
- what was rejected or kept as note-only residue
- where translation narrowed or added local safety constraints

The operator should be able to answer:

> which approved local actions depend on this exact basis, and what did the product refuse to import?

### 5) Drift checks and follow-up actions

This section should show:

- whether the live source was rechecked
- whether it changed materially
- whether current translations should be rechecked
- admissible next actions

The operator should be able to answer:

> has upstream changed since our review, and does that affect follow-up without rewriting old receipts?

## Public rules

### Rule 1 — live locator is not the reviewed basis

A URL, ticket link, or forum permalink may remain the convenience entry point.
It must not stand in for the exact reviewed instruction basis.

### Rule 2 — authority host, fetched snapshot, and exact basis stay separate

An allowlisted or official host may justify fetch posture.
It does not by itself prove exact reviewed bytes or exact reviewed excerpt scope.

### Rule 3 — translation and approval must point to frozen basis rows

A translated recipe, probe, packet, or note must reference one snapshot and one explicit basis row set.
Approvals may not point only to a live locator.

### Rule 4 — later drift may trigger recheck, not receipt rewrite

A drift check may say the live source changed materially.
It must not mutate the meaning of older basis receipts that were already issued.

### Rule 5 — redirects and access loss are facts, not silent implementation details

If the original locator now redirects, requires login, or is gone, the product should say so explicitly.
That is follow-up truth, not background noise.

### Rule 6 — copied commands need exact-basis treatment too

A copied shell line or config snippet must not skip the snapshot/basis discipline merely because it came through chat or clipboard instead of a URL.

### Rule 7 — no translation from `official` to `safe`

An official source may still be over-broad, stale, or inapplicable.
Frozen basis and local translation review still apply.

## Example prompts

- `What exact excerpt did this recipe come from?`
- `Are we still looking at the same page we reviewed earlier?`
- `Did the source redirect or change after we approved this translation?`
- `Which local objects depend on this frozen basis?`
- `Was the host reviewed, or only the exact excerpt?`

## Anti-goals

- no approval that references only a live URL
- no silent redirect-following that rewrites the implied source boundary
- no treating host allowlisting as exact reviewed bytes
- no drift check that mutates historical basis receipts
- no copy-paste guidance lane that bypasses snapshot and basis discipline
