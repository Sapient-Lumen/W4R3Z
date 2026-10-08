# 470 — Official voter-information mid-flow version drift, expected-head review, and resumed-state honesty discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes where a voter may begin under one reviewed public basis and finish under another because the governing page, packet, rule summary, or status explanation changed while the voter was in progress or later resumed the route**:
forms whose controlling instructions change during completion,
status or correction routes resumed after a later official update,
multi-step flows whose reviewed public basis changes between step 1 and final submit,
queued/resumed routes that preserve progress but no longer rest on the same governing public head,
and similar public routes where the route may honestly preserve state yet no longer honestly preserve the basis the voter reviewed when they started.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `373`, which governs the visible edition/scope and acceptance semantics of the form or packet itself,
- `429`, which governs multi-step progress, review, and state preservation more broadly,
- `430`, which governs post-submit confirmation, reference numbers, and safe retry,
- `431`, which governs inactivity timeout warnings and expiry recovery,
- `439`, which governs history restore, hidden return, and parallel-tab freshness,
- `467`, which governs live operational heads versus citation-safe heads,
- `468`, which governs compact citation-head registers across mutable lineages,
- `469`, which governs local-only / queued / office-acknowledged state honesty,
- or `201`, which governs parity snapshots across official channels.

It adds one narrow rule:
**if a voter can continue, resume, or complete an official route after the governing reviewed public basis changed materially, the office should not silently treat that resumed interaction as though it were still proceeding under the original expected head.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications. Digital.gov’s current digital-first public-experience requirements say public digital services should be accessible, authoritative, secure by design/default, and user-centered. USWDS’s current **Progress easily** and **Keep a record** guidance says important public-service routes should make process state understandable and preserve a usable record of what happened. W3C WAI’s current multi-page-form guidance says staged public flows should preserve orientation and continuity. MDN’s current documentation on history/restore behavior, plus web.dev guidance on service-worker lifecycle and network reliability, makes clear that modern public-service routes can preserve or resume state across time, visibility changes, retries, and restored page instances without those continuity cues automatically proving that the governing reviewed basis stayed the same. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `uswds_progress_easily_page`; xref: `uswds_keep_a_record_page`; xref: `w3c_wai_multi_page_forms_page`; xref: `mdn_working_with_history_api_page`; xref: `mdn_pageshow_event_page`; xref: `mdn_popstate_event_page`; xref: `web_dev_network_reliability_page`; xref: `web_dev_service_worker_lifecycle_article`)

That is enough to justify a compact public-answer control here.
A route may pass `429`, `431`, `439`, `467`, and `469` and still fail the public because:
- the voter started under one reviewed rule/instruction head but a newer controlling head took effect before submit,
- a resumed draft or saved step is still present, but the basis the voter reviewed is no longer current,
- the route shows the same page shell and same local data yet the governing eligibility/deadline/instruction basis changed,
- the office preserves continuity but never says whether the earlier review still counts,
- or a final confirmation fails to say which head/version actually controlled the accepted outcome.

## Expected head is the reviewed public basis, not merely the same URL

For this archive, an **expected head** is the reviewed public basis the voter reasonably relied on when starting or last explicitly re-reviewing the route.
That basis may be represented by:
- a form/packet edition,
- a current rule/instruction page head,
- a current status explanation head,
- a citation-safe snapshot referenced by the route,
- or another bounded public head the office has chosen to treat as the controlling reviewed basis for the interaction.

A voter remaining on the same URL is **not** enough.
The office should not silently equate:
- same route,
- same browser state,
- same local draft,
- or same restored page instance
with **same governing reviewed basis**.

## This is not the same thing as local/queued state, timeout recovery, or citation heads alone

`469` asks where the meaningful state lives: local-only, queue-pending, or office-acknowledged.

`431` asks whether inactivity/expiry can wipe work and whether the route warns/recoveries clearly.

`467` and `468` ask what the current live head and citation-safe head are.

`479` asks whether a future route was speculatively fetched or prerendered before intentional view and whether that pre-activation state stayed safe and fresh enough to activate.

`470` asks a different question:
**after the voter has already begun or resumed an interaction, does the route tell the truth about whether the reviewed public basis they started under is still the basis that governs the next step, resumed step, or final acceptance?**

A route may pass the earlier controls and still fail `470` if:
- the draft is safely preserved but now rests on superseded instructions,
- the route resumes after timeout or history restore and implies nothing material changed,
- the latest live head is clearly named but the voter is never told whether their in-progress review must be refreshed,
- or the final receipt says “submitted” without saying which version/head actually controlled acceptance.

## Material basis change should trigger re-review, restart, or explicit handoff

Not every edit requires disruption.
Typos, cosmetic restyling, or non-substantive wording polish may leave the earlier reviewed basis effectively unchanged.

But when the change is **material** to the next action—deadline semantics, eligibility, office destination, witness/notary requirement, required attachment, signature method, accepted submission channel, or other action-shaping rule—the route should not glide forward as though the earlier review still controls.

Bounded safe responses include:
- require a visible re-review of the changed controlling section,
- restart only the affected bounded portion,
- preserve user-entered data while re-establishing the new expected head,
- or hand the voter to an authoritative help/status lane when silent continuation would be misleading.

The archive does **not** require discarding all progress whenever a head changes.
It does require honesty that progress continuity is not the same thing as review continuity.

## Resume and queued-send classes need expected-head honesty too

This matters especially when the route can be resumed later or can queue an action for later send.
A preserved draft or queued request may still exist, yet the expected head the voter reviewed may no longer control by the time the route resumes or actually sends.

That means a route should review whether it can visibly distinguish:
- **same state, same expected head**,
- **same state, newer expected head requires re-review**, and
- **state preserved, but safe completion now requires restart/help because the governing basis changed too much**.

This is where `470` composes with `469` instead of replacing it.
`469` answers where the state lives.
`470` answers whether the earlier review basis still governs that state.

## Historical basis may remain citable without remaining actionable

A route may correctly preserve the historical basis for records, citation, dispute review, or later explanation.
That does **not** mean the voter should keep acting under it.

For this archive, a route may honestly say both:
- “here is the head/version you previously reviewed,” and
- “a newer controlling head now governs the next action.”

This keeps records truthful without implying that an older basis remains safe to act upon.

## Final confirmations should identify the actual controlling basis when that matters

When a route reaches office acceptance, a confirmation/receipt should not make later reconstruction guesswork.
If the route crossed a material basis change before acceptance, the durable confirmation should identify enough to answer:
- which head/version actually controlled the accepted action,
- whether the voter re-reviewed the newer basis,
- and whether any earlier in-progress basis became historical-only rather than still actionable.

That can be small.
The goal is not a giant audit trail.
The goal is to stop later disputes from collapsing “the voter began under X” into “the office accepted under X” when the truth is “the office accepted under Y after visible re-review.”

## Preserve bounded evidence, not per-user replay exhaust

The evidence posture here is about reconstructing expected-head honesty without pretending every resumed interaction needs a full replay log.
The archive should preserve:
- which routes can span enough time or state that the expected head may drift,
- what classes of material change require re-review, restart, or help,
- whether preserved state can survive a head change,
- what cue identifies the current expected head,
- what cue identifies the previously reviewed head when it is no longer current,
- what confirmation/receipt posture names the actual accepted basis,
- and when the review last occurred.

It should **not** require publishing by default:
- per-voter state timelines,
- raw edit histories of each draft,
- exhaustive diff logs for every micro-edit,
- personalized resume telemetry,
- or individualized replay traces when bounded policy reconstruction is sufficient.

## Canonical digest artifacts

Publish **small digests of expected-head / version-drift posture**, not session-replay exhaust.

- **Expected-Head Drift Digest (EHDD):** digest of the bounded expected-head / re-review policy for the official route.
- **Basis-Change Review Digest (BCRD):** optional digest describing what classes of material change require re-review, restart, or authoritative help.
- **Resumed-Basis Honesty Digest (RBHD):** optional digest describing how resumed/queued/restored state indicates whether the earlier reviewed basis still controls.

## What belongs in the public expected-head payload

Keep the payload **small, route-aware, and basis-drift focused**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `expected_head_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_expected_head_routes[]`
- `expected_head_classes[]`
- `material_basis_change_note`
- `re_review_or_restart_policy_note`
- `resumed_state_expected_head_note`
- `queued_send_expected_head_note`
- `accepted_basis_confirmation_note`
- `historical_basis_reference_note`
- `authoritative_help_or_restart_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- individualized resume histories,
- per-user conflict traces,
- raw queue internals,
- full internal release boards,
- or giant version corpora when a bounded expected-head digest is sufficient.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Did the office identify which public routes can drift materially between start, resume, and acceptance?
- Could the voter tell whether the earlier reviewed basis still controlled after a return, resume, or queued send?
- Were material basis changes separated from cosmetic edits?
- When the governing basis changed, did the route require re-review, restart, or authoritative help instead of silently continuing?
- Did the final confirmation identify the actual controlling basis when that distinction mattered?

## How this fits the family map

Mid-flow version drift, expected-head review, and resumed-state honesty is **not** a new underlying voter-question family bucket.
It is a delivery-layer and evidence-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if a route can preserve or resume state across a material change in the governing public basis, the office should keep that expected-head boundary honest instead of implying unchanged authority from mere continuity.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-expected-head-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-expected-head-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Digital.gov: Requirements for a digital-first public experience (xref: `digital_gov_requirements_digital_first_public_experience_page`)
- USWDS: Progress easily (xref: `uswds_progress_easily_page`)
- USWDS: Keep a record (xref: `uswds_keep_a_record_page`)
- W3C WAI: Multi-page forms (xref: `w3c_wai_multi_page_forms_page`)
- MDN: Working with the History API (xref: `mdn_working_with_history_api_page`)
- MDN: `pageshow` event (xref: `mdn_pageshow_event_page`)
- MDN: `popstate` event (xref: `mdn_popstate_event_page`)
- web.dev: Service worker lifecycle (xref: `web_dev_service_worker_lifecycle_article`)
- web.dev: Network reliability (xref: `web_dev_network_reliability_page`)
