# 431 — Official voter-information inactivity timeouts, advance warnings, and lossless-expiry recovery fail-open discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that keep a voter in an in-progress task long enough that inactivity timers, security expirations, or other ordinary time limits can wipe work or create outcome uncertainty before the voter reaches the answer/help lane cleanly**:
registration/update/application routes,
lookup or correction routes that hold partial progress,
identity-proof or upload paths that may expire mid-task,
multi-step routes with security or inactivity timers,
and similar public answer/help paths where the page can be current and individually accessible yet still fail first contact because the route times out before a slower, interrupted, or assistive-technology user can finish or safely resume.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help lane,
- `409`, which governs public-read access, sign-in boundaries, and generic re-authentication shells,
- `415`, which governs low-connectivity and intermittent-network degradation,
- `422`, which governs field purpose, autofill, and input-error recovery,
- `427`, which governs phone/email targets and verification-code gates,
- `429`, which governs multi-step progress, review, and state preservation more broadly,
- `430`, which governs explicit post-submit confirmation, retained records, and safe retry after the action has landed,
- or `476`, which governs leave-page warnings and unsaved-changes truthfulness when the voter actively tries to leave rather than simply timing out.

It adds one narrow rule:
**if an official voter-information route imposes an inactivity timeout or other ordinary time limit before the voter finishes, the office should disclose that limit early, warn before work expires, allow extension or preservation when practical, and keep post-expiry recovery clear enough that the voter does not have to guess whether progress was lost, whether a prior submit landed, or whether the only safe next step is to restart or call for help.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as a core election responsibility and emphasizes clarity, accessibility, usability, and audience-aware structure. Digital.gov’s current digital-first public-experience requirements say public digital services should be accessible, authoritative, mobile-friendly, and user-centered. W3C’s current **Understanding SC 2.2.1: Timing Adjustable** says users should be able to turn off, adjust, or extend time limits, including advance warning and at least 20 seconds to extend when the “extend” path is used. W3C’s current **Understanding SC 2.2.6: Timeouts** says users should be warned about inactivity durations that can cause data loss unless data is preserved for more than 20 hours, and says the best conforming posture is to preserve user data long enough that people can take breaks and return. W3C’s current **Understanding SC 2.2.5: Re-authenticating** says authenticated transactions should preserve the original activity and entered data through re-authentication when feasible. Section508.gov’s current accessible web design guide repeats the same timing-adjustable floor for federal web work. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `w3c_wcag22_timing_adjustable_page`; xref: `w3c_wcag22_timeouts_page`; xref: `w3c_wcag22_reauthenticating_page`; xref: `section508_guide_accessible_web_design_development_page`)

That is enough to justify a compact control here.
A route can be current, accessible, and even pass `422`, `427`, `429`, and `430`, yet still fail first contact because:
- the voter never learns the inactivity window until a last-second modal appears,
- the warning arrives too late or disappears before it can be reviewed,
- the route times out while the voter is looking up an address, ID, witness, or document,
- the timeout discards entered work without saying whether anything was preserved,
- a re-authentication or expiry jump returns the voter to a blank first step,
- or the voter cannot tell whether a nearly simultaneous submit attempt landed.

## This is not the same thing as multi-step progress, public-read auth shells, or post-submit confirmation

`429` asks whether a staged route keeps process shape, review posture, and invalidation risks clear **throughout the flow**.

`409` asks whether general official reading routes stay publicly readable and, when authentication exists, whether re-authentication shells preserve context rather than hijacking public first contact.

`430` asks whether, **after** the final action, the official route clearly states what happened, what record to keep, what to expect next, and whether retry is safe.

`431` asks a different question:
**before final completion, if a timer or inactivity rule can interrupt the route, did the office warn early enough, preserve enough, and explain expiry recovery well enough that an ordinary voter does not lose the answer lane just because they needed more time?**

If an expired or resumed route returns with preserved state but the governing public basis changed materially while the voter was away, `470` governs whether the original review still counts or whether visible re-review/restart/help is required.

A route may pass `429` and `430` and still fail `431` if:
- progress indicators are good but the inactivity window is never disclosed,
- a timeout warning appears only moments before expiry and cannot be extended with a simple action,
- the voter is dumped onto a blank route after re-authentication,
- or the route says “session expired” without saying whether partial data, uploaded files, or a previous submit survived.

## Tell the voter about the timeout before the route turns it into a surprise

W3C’s current **Understanding SC 2.2.6: Timeouts** says the best posture is to preserve user data for at least 20 hours, but when that is not practical the author should warn users about the duration of inactivity that will result in a timeout and should do so once at the beginning of the related task or process, not only at the last second. The same guidance says users should be able to decide whether they can complete the task, take a needed break, or prepare materials in advance. (xref: `w3c_wcag22_timeouts_page`)

For this archive, that means official routes should make visible, near the start of the process when practical:
- that an inactivity timeout or other time limit exists,
- how long inactivity can last before progress or data may be lost,
- whether the route preserves work, uploads, or only some fields,
- and whether a later re-authentication or resume step will restore the work or only the route location.

A countdown that appears only after the voter is already deep in the flow is not enough on its own.

## Warn before expiry and keep the extension action simple

W3C’s current **Understanding SC 2.2.1: Timing Adjustable** says that, where time limits are not turned off or broadly adjustable, an extension path should warn before the limit expires, give at least 20 seconds to respond, and allow repeated extension with a simple action. Section508.gov repeats the same timing-adjustable floor in its current accessible web design guide. (xref: `w3c_wcag22_timing_adjustable_page`; xref: `section508_guide_accessible_web_design_development_page`)

For `431`, that means an office should prefer one of these bounded postures when a timer exists:
- no timeout for the relevant public task,
- a configurable or clearly extendable timeout,
- or an early, accessible warning with a simple extension action and enough time to notice, understand, and act.

The rule is not “every election route must keep a session alive forever.”
It is “do not make ordinary slower completion or interruption silently fatal.”

## Preserve work and restore context whenever the activity or security model allows it

W3C’s current **Understanding SC 2.2.5: Re-authenticating** says authenticated transactions should allow the user to continue the activity without loss of data after re-authenticating. W3C’s current **Understanding SC 2.2.6: Timeouts** says preserving user data for long periods is the best way to help people take breaks and return later. (xref: `w3c_wcag22_reauthenticating_page`; xref: `w3c_wcag22_timeouts_page`)

For this archive, that means the route should preserve as much as is safely practical:
- entered fields,
- current step/context,
- uploaded-file state or a clear statement that upload must be redone,
- and any bounded review state that prevents accidental duplicate work.

If full preservation is impossible because of law, privacy, or security constraints, the route should say so explicitly **before** the voter reaches the risky stage rather than after the loss occurs.

## After expiry, say what was lost, what was kept, and what the safe next step is

A timeout or expiry page should not stop at “session expired.”
The voter needs the operational meaning:
- whether their work was preserved,
- whether any completed submit attempt landed,
- whether they should resume, re-authenticate, restart, or wait,
- and which ordinary help route controls if the state remains uncertain.

This is where `431` composes with `305`, `409`, `429`, and `430`.
The office does not need to publish internals about session stores or security controls.
It does need a bounded recovery posture that prevents the timeout page from becoming a dead end or a blind duplicate-submission trap.

## The timeout warning and expiry state should be accessible and reviewable

A timeout warning that is tiny, transient, off-screen, or impossible to review with assistive technology is not a real warning.
Because timeout and extension affordances alter what happens next, they should remain perceivable and operable with keyboard navigation, zoom, mobile layouts, and screen readers.
Where re-authentication is required, restoring the original task context matters more than perfectly preserving every animation or convenience cue. (xref: `w3c_wcag22_timing_adjustable_page`; xref: `w3c_wcag22_reauthenticating_page`)

For this archive, that means:
- the warning should appear in accessible text,
- the extension control should not depend on pointer-only or last-second choreography,
- and the expired-state page should explain the recovery path in durable page content rather than in a vanished toast.

## Keep timeout evidence bounded and privacy-aware

The archive should preserve only enough policy state to reconstruct what the official route promised about time limits and expiry recovery.
That can include:
- whether a timeout existed,
- when and how the office disclosed it,
- whether extension or preservation was available,
- whether re-authentication restored context,
- and what help/retry instructions were shown after expiry.

It should **not** require preserving real voter drafts, full session tokens, detailed inactivity telemetry, or replayable user timelines unless another independent obligation requires them.

## Canonical digest artifacts

Publish **small digests of timeout posture**, not session internals.

- **Timeout Warning Surface Digest (TWSD):** digest of the bounded timeout/expiry policy payload for the official route.
- **Expiry Recovery State Digest (ERSD):** optional digest describing what is preserved, restored, or lost after timeout.
- **Timeout Help and Safe-Restart Digest (THSD):** optional digest of restart, resume, re-authentication, and office-help guidance.

## What belongs in the public timeout-recovery payload

Keep the payload **small, current-state focused, and recovery-oriented**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `timeout_recovery_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_answer_routes[]`
- `reviewed_timeout_paths[]`
- `timeout_scope_note`
- `timeout_length_note`
- `advance_warning_note`
- `extension_or_adjustment_note`
- `data_preservation_note`
- `re_authentication_restore_note`
- `expired_state_recovery_note`
- `submit_uncertainty_note`
- `public_help_route_uri`
- `public_help_route_phone`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- real voter drafts,
- session identifiers or session-store internals,
- exhaustive inactivity telemetry,
- or per-user resume-token histories.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Could an ordinary voter learn early enough that the route had an inactivity timeout or other time limit?
- Did the route warn before work expired and, where practical, allow a simple extension or adjustment path?
- Did the office say whether work, files, and current step/context would be preserved?
- After expiry or re-authentication, could the voter tell what was restored, what was lost, and what safe next step applied?
- Did the route avoid turning timeout uncertainty into duplicate-submission guesswork?
- Were warning, extension, and expiry-recovery states accessible and reviewable?

## How this fits the family map

Official timeout and expiry-recovery posture is **not** a new underlying voter-question family bucket.
It is a high-stakes delivery-layer control over the same public tasks already modeled in `292–343` and the route-governance documents.

This document only says that, if a jurisdiction expects the public to stay in an official election route long enough for inactivity or time limits to matter, the route should disclose the limit early, warn before loss, preserve or restore context when practical, and keep timeout recovery bounded enough that the voter does not have to guess whether to wait, restart, re-authenticate, or call for help.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-timeout-recovery-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-timeout-recovery-surface-checklist.md`
