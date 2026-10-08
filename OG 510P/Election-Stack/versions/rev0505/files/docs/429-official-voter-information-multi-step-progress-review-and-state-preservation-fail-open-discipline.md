# 429 — Official voter-information multi-step progress, review, and state-preservation fail-open discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that split one public task across multiple steps, pages, or progressive states before the current answer/help lane can continue or a submission is finalized**:
registration, update, absentee, cure, replacement, appointment, or problem-report routes that stage questions across multiple pages,
flows that branch based on prior answers,
routes that expose a review/confirm step before final submission,
and similar public answer/help paths where the process shape itself becomes part of whether a voter can successfully reach the current official route.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help lane,
- `307`, which governs problem reporting and civil-rights escalation,
- `373`, which governs official forms/applications/affidavits more broadly,
- `374`, which governs interactive routers, selectors, and decision-path trace discipline,
- `409`, which governs sign-in boundaries and session-expiry recovery,
- `417`, which governs keyboard/focus continuity,
- `420`, which governs motion/interruption posture,
- `422`, which governs generic field purpose, autofill, and input-error recovery,
- `427`, which governs phone/email targets and verification-code gates,
- or `428`, which governs upload/camera-capture posture.

It adds one narrow rule:
**if an official voter-information route depends on a voter moving through multiple ordered steps before the current answer/help lane can continue or the official submission can be finalized, the office should keep step count/current position, optional-step posture, back/forward behavior, prior-answer invalidation rules, review-before-submit posture, and save/resume or bounded fallback clear enough that the answer does not depend on guessing how many stages remain, whether “Back” will erase work, or whether a corrected earlier answer will silently wipe later steps.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as a core election responsibility and emphasizes clarity, accessibility, usability, and audience-aware structure. Digital.gov’s current digital-first public-experience guidance says public digital services should be accessible, authoritative, user-centered, and mobile-first, and that digitized public forms and services should maximize self-service completion. USWDS’s current **Step indicator** guidance says teams should indicate where a user is in the process, provide separate forward/back navigation, place an explicit heading below the indicator, and test implementations for accessibility. USWDS’s current **Progress easily** pattern says teams should break long forms into small chunks, show users where they are in the process, warn before invalidating prior completed steps, allow save/resume when possible, and keep help available. W3C WAI’s current **Multi-page Forms** tutorial says long forms should be divided into logical steps, overall instructions should repeat on every page, optional stages should be recognizable, and progress should be explained. W3C’s current **Understanding SC 3.3.6: Error Prevention (All)** says users should be able to confirm, correct, or reverse submissions before finalization. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `uswds_step_indicator_component_page`; xref: `uswds_step_indicator_accessibility_tests_page`; xref: `uswds_progress_easily_page`; xref: `w3c_wai_multi_page_forms_page`; xref: `w3c_wcag22_error_prevention_all_page`)

That is enough to justify a compact control here.
A route can be current, accessible in each individual field, and even pass `422`, `427`, and `428`, yet still fail first contact because:
- the voter cannot tell how many steps remain,
- optional stages are not recognizable,
- a “Back” action or changed answer silently wipes later entries,
- the route offers save/resume but never says so,
- the route does **not** offer save/resume but implies the work will still be there,
- the final submission has no review/confirm posture,
- or a critical explanation opens off-page and causes the voter to lose their place in the process.

## This is not the same thing as router logic, generic field review, or upload review

`374` asks whether an official router or selector can justify the decision path that produced a result.

`422` asks whether a voter can tell what to type and recover from ordinary field errors.

`428` asks whether upload-dependent steps clearly explain file expectations and retry/help recovery.

`429` asks a different question:
**once the route itself spans multiple stages, can the voter tell where they are, move through the process without silent step loss, understand when earlier answers change later stages, and review or safely pause the process before an irreversible final action?**

A route may pass `374`, `422`, and `428` and still fail `429` if:
- step 3 of 5 looks identical to step 1 with no progress cue,
- a prior answer change silently clears two later sections,
- the user has no way to review all answers before final submission,
- the page hides critical instructions in a separate window that causes place-loss,
- or a long form supports save/resume in practice but never tells the voter up front.

## Tell the voter the process shape up front

W3C WAI’s current multi-page-forms guidance says the first step should explain how many steps will follow when possible, and each step should inform the user about the progress they are making. USWDS’s current step-indicator guidance says the current step should be visually distinct, each step needs an explicit heading, and navigation should be provided separately. (xref: `w3c_wai_multi_page_forms_page`; xref: `uswds_step_indicator_component_page`)

For this archive, that means a multi-step official route should make visible:
- the current step and, when practical, the total number of steps,
- whether a stage is optional or skippable,
- the heading for the current step independent of any progress bar,
- and the ordinary next/back/help controls needed to continue.

The rule is not “every flow must use a fancy progress bar.”
It is “do not make the voter guess the process shape.”

## Progress cues should not be the only orientation cue

USWDS’s current step-indicator guidance says each step needs an explicit heading, and its accessibility guidance says to use semantic heading levels, make completion status explicit, and indicate the current step with accessible state. The current accessibility tests also say teams need to test the component in project context, including zoom and screen-reader behavior. W3C WAI’s multi-page-forms guidance says page titles and main headings can both carry step information. (xref: `uswds_step_indicator_component_page`; xref: `uswds_step_indicator_accessibility_tests_page`; xref: `w3c_wai_multi_page_forms_page`)

For `429`, that means the current step should not be conveyed only by a visual bar or colored segment.
The route should preserve step meaning in page titles, headings, and other cues that survive assistive technology, zoom, or partial rendering.

## Warn before invalidating later steps

USWDS’s current **Progress easily** pattern says that if changes to answers may impact steps already completed, the route should inform the user of potential impacts and confirm before invalidating previous form entries. That point is unusually important for election routes, because a change in address, delivery method, document type, or eligibility answer can radically change the remaining official path. (xref: `uswds_progress_easily_page`)

For this archive, that means:
- changing an earlier answer should not silently wipe later work,
- the route should explain when the change will alter or remove later steps,
- and the voter should get a bounded chance to confirm before prior progress is discarded.

## Save/resume posture should be explicit, not implied

USWDS’s current **Progress easily** pattern says teams should allow users to save and resume when possible and tell them so up front, because some users need breaks or may be interrupted while completing difficult forms. W3C WAI’s multi-page-forms guidance also warns against unnecessary time limits and says time extensions should be possible when limits are required. (xref: `uswds_progress_easily_page`; xref: `w3c_wai_multi_page_forms_page`)

For `429`, that means a route should be honest about process persistence:
- if save/resume exists, say so early and say how it works at a bounded level,
- if the route does **not** preserve progress, do not imply that it does,
- and if interruption or timeout is likely, keep a visible first-party help or alternate lane available.

This surface does **not** require every public route to implement accounts or draft storage.
It requires that the voter not discover the persistence model only after losing their place.

## Review and confirm before finalizing important submissions

W3C’s current **Understanding SC 3.3.6: Error Prevention (All)** says users should have a way to confirm, correct, or reverse submissions before finalization. For election routes, that matters because the final step may create or alter a registration request, mail-ballot request, cure submission, contact preference, or another time-sensitive official record. (xref: `w3c_wcag22_error_prevention_all_page`)

For this archive, that means the process should keep a bounded review/confirm posture when the final action matters:
- show the voter what they are about to submit,
- allow correction before finalization,
- and avoid last-step surprises where the first time the voter sees a critical value is after the route has already committed it.

## Do not hide critical guidance off-page and cause place loss

USWDS’s current **Progress easily** pattern warns against hiding critical information behind links that navigate users away from the form, because they may become disoriented or lose their place. That warning is especially relevant for election routes that ask the voter to inspect ID rules, signature instructions, or deadline semantics mid-process. (xref: `uswds_progress_easily_page`)

For `429`, that means:
- essential explanatory content should stay on-screen or in a bounded same-context help posture when practical,
- off-page detours should not be the only way to understand a required step,
- and leaving the process should not quietly destroy safely preservable state.

## Test the whole staged route, not just the individual controls

USWDS’s current step-indicator accessibility tests say teams must test implementations in their own project context. That matters because a multi-step route can pass isolated component checks and still fail when focus, error messaging, save/resume hints, review summaries, or progress cues interact across pages or dynamic states. (xref: `uswds_step_indicator_accessibility_tests_page`)

That means `429` should review whether:
- the current step remains clear on mobile, at zoom, with keyboard navigation, and with screen readers,
- headings/titles and progress cues stay in sync,
- back/forward behavior preserves safely preservable state,
- invalidating earlier answers triggers a visible warning before later data is dropped,
- and review/help/save-resume cues remain visible at the moments people actually need them.

## Preserve bounded review evidence, not full user histories

This control is about public-answer integrity, not building a surveillance log of every step a voter took.
The evidence posture should therefore preserve:
- which public routes use multi-step or staged progression,
- whether current-step / total-step / optional-step cues were reviewed,
- whether invalidation warnings and review/confirm posture were reviewed,
- whether save/resume or non-persistence posture was made explicit,
- whether help remained visible,
- and when the review last occurred.

It should **not** require preserving full per-user clickstreams, completed draft contents, personal answers from real voters, long-lived session identifiers, screen recordings of real users, or exhaustive replay when bounded policy reconstruction is sufficient.

## What to test

- Can a voter tell the current step and, when practical, the total remaining process shape?
- Are optional or skippable stages recognizable before the voter enters them?
- Do page titles/headings and visible progress cues stay in sync?
- If a changed earlier answer invalidates later steps, is that warned about before later work is discarded?
- If save/resume exists, is it disclosed up front? If it does not exist, is non-persistence still honest and helpfully bounded?
- Is there a review/confirm posture before finalizing important submissions?
- Can a voter leave a help pane, correction step, or earlier page without losing safely preservable progress by surprise?

## Minimal companion artifacts

- Template payload: `artifacts/templates/official-voter-information-multi-step-progress-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-multi-step-progress-surface-checklist.md`
