# 476 — Official voter-information leave-page warnings, unsaved-changes dialogs, and loss-prevention truthfulness discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes where a voter may try to reload, close, navigate away, follow another link, or switch applications while meaningful in-progress state could still be lost or misunderstood**:
registration/update/application routes,
multi-step voter-help flows,
status-correction or upload paths,
routes with reviewable but not-yet-submitted progress,
and similar official pages where the route may look current and usable yet still fail the public because the only visible protection against loss is a generic browser confirmation, a vague “Leave site?” modal, or an implied promise that the page has already saved work when it has not.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help lane,
- `429`, which governs multi-step progress, review, and state preservation more broadly,
- `431`, which governs inactivity timeouts and lossless-expiry recovery,
- `439`, which governs hidden-return, history-restore, and parallel-tab freshness once the page later reappears,
- `459`, which governs answer-bearing overlays and route continuity more broadly,
- or `469`, which governs local-only saves, queued background sync, and office-acknowledged state truthfulness,
- or `477`, which governs post-submit redirects and browser repost prompts once a state-changing submit has already happened and the public risk has shifted from leaving with unsaved work to revisiting a maybe-replayed result state.

It adds one narrow rule:
**if an official voter-information route tries to prevent accidental loss when a voter leaves the page, the route should tell the truth about what is actually saved, what may still be lost, whether the warning is browser-generated or route-defined, and what recovery path controls next instead of implying that any leave-page warning guarantees preservation, submission, or office receipt.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and stresses clarity, structure, accessibility, usability, and usefulness. W3C WAI’s current **Multi-page Forms** tutorial matters because long or staged forms need continuity, repeated instructions, and safe progress through multiple pages. USWDS’s current **Modal** guidance matters because it includes a concrete unsaved-changes pattern (“Continue without saving” / “Go back”) while also saying modals should be used sparingly and kept simple. MDN’s current `beforeunload` guidance matters because modern browsers require sticky activation, show only a generic browser-specified string, and do not fire the event reliably in all cases, especially on mobile. MDN’s current `visibilitychange` guidance matters because the transition to hidden is the last reliably observable point for the page and is therefore a better place to think about automatic state preservation than to assume a later leave warning will always appear. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `w3c_wai_multi_page_forms_page`; xref: `uswds_modal_component_page`; xref: `mdn_beforeunload_event_page`; xref: `mdn_visibilitychange_event_page`)

That is enough to justify a compact control here.
A route may pass `429`, `431`, and `469` yet still fail the public because:
- the route implies “your work is protected” when the only protection is a browser-generated generic confirmation that may not appear,
- a custom unsaved-changes modal does not say whether the route saved locally, saved to the office, or saved nowhere,
- mobile app-switch or close behavior loses in-progress work with no truthful earlier warning because the office assumed `beforeunload` would catch it,
- a leave warning appears even when nothing meaningful would be lost, training voters to dismiss it as noise,
- or the route treats “a warning was shown” as if it were evidence of durable draft preservation or successful submission.

## This is not the same thing as drafts, timeouts, restore, or answer overlays

`429` asks whether a staged route preserves progress and review continuity across the task as a whole.

`431` asks whether inactivity limits are disclosed, warned, and recoverable.

`469` asks whether local-only save, queued send, and real office receipt stay visibly distinct.

`439` asks what happens when the page later returns through history, hidden-tab restore, or back/forward cache.

`459` asks whether answer-bearing overlays stay route-truthful and durably recoverable.

`476` asks a different question:
**at the moment a voter tries to leave, reload, or close the route, does the warning/recovery posture tell the truth about what is actually at risk and what state, if any, has already been preserved?**

A route may pass the earlier controls and still fail `476` if:
- a local draft exists, but the leave warning implies the office already has the submission,
- an inactivity timeout is handled well, but manual reload/close still creates misleading loss warnings,
- history restore works later, but the route never clearly stated what was or was not saved when the voter tried to leave,
- or a custom modal looks polished while hiding whether “Continue” loses nothing, some local draft state, or all unsent work.

## Not every risky route needs the same warning posture

This archive should not flatten all leave events into one behavior.
At least four distinct classes matter here:

1. **Browser-generated confirmation** — a `beforeunload`-style generic dialog the route may trigger only when unsaved state exists.
2. **Route-defined confirmation** — an office-controlled modal or inline blocker shown before destructive navigation inside the route.
3. **Preserve-on-hide / preserve-on-leave posture** — the route attempts local preservation when the page becomes hidden, while still staying honest about what was actually saved.
4. **No warning needed** — the route has already preserved enough state or the action is so low-risk that a leave warning would be more misleading than helpful.

Those are different public stories.
A route may need more than one.
But the office should not blur them into one vague promise that “your work is safe” merely because some confirmation or autosave mechanism exists somewhere.

## Generic browser dialogs are weak evidence and weak copy surfaces

MDN’s current `beforeunload` guidance says modern browsers require sticky activation before showing the dialog, show only a generic browser-specified string, and do not fire the event reliably in all cases. It also says the listener should be added only when users actually have unsaved changes, and removed again when it is not needed. (xref: `mdn_beforeunload_event_page`)

That makes the browser dialog a **bounded last-resort interruption**, not a trustworthy primary explanation surface.
For this archive, the office should therefore avoid public postures like:
- “the browser will warn you before anything is lost,”
- “closing this page always gives you a chance to save,”
- or “if you saw the dialog, your work was already preserved.”

A safer posture is:
- the route identifies whether unsaved state exists,
- the route warns when loss is real and material,
- the route explains saved-versus-unsaved state in its own ordinary UI before the risky moment when practicable,
- and any browser-generated dialog is treated as an additional bounded safeguard rather than as the only truthful explanation of loss risk.

## The hidden transition is better for preservation than for explanation

MDN’s current `visibilitychange` guidance says transition to hidden is the last reliably observable event for the page. That makes it important for autosave or compact state preservation work. (xref: `mdn_visibilitychange_event_page`)

But preservation work on hide does **not** by itself settle the public truth question.
If the route preserves something when hidden, it should still remain clear whether that means:
- local draft only,
- resumable but not submitted progress,
- queued-for-later send,
- or actual office receipt.

In other words:
**save-on-hide is helpful, but it must not silently convert a maybe-preserved local draft into a fake “submitted” or “nothing can be lost” story.**
That state-class truth still belongs to the route.

## Custom unsaved-changes confirmations should be explicit and bounded

USWDS’s current modal guidance gives a useful public-service pattern here: a simple unsaved-changes confirmation with a clear headline, a short statement of loss, and an explicit “Continue without saving” versus “Go back” choice. The same guidance also says modals should be used sparingly and should avoid unnecessary complexity. (xref: `uswds_modal_component_page`)

For `476`, that means a custom confirmation can be useful when it answers three questions plainly:
- What will be lost?
- What, if anything, has already been preserved?
- What does each choice do next?

The route should be more cautious about confirmations that:
- merely say “Are you sure?” without naming the loss,
- imply submission or office receipt when only local state exists,
- present “Leave” / “Stay” labels with no action-specific explanation,
- or stack a custom modal on top of a browser-generated dialog so the voter sees two inconsistent stories about the same risk.

## Mobile app-switch and close behavior deserve earlier honesty

MDN’s current `beforeunload` guidance is explicit that the event is not reliably fired in all cases, especially on mobile. (xref: `mdn_beforeunload_event_page`)

So the archive should not allow a public route to depend on a last-second exit dialog as the only safety rail for meaningful progress.
If losing work would materially change what the voter does next, then earlier in-route posture matters more:
- visible save/progress cues,
- explicit draft-versus-submitted state,
- reviewable next steps,
- and a help/restart lane that does not assume the user will always get one final chance to cancel leaving.

A route can honestly say “unsaved progress may be lost if you leave now.”
It is much riskier to behave as though every user will always receive a rescue dialog at the last moment.

## Reload, external handoff, and close are not the same story

For this archive, leave-risk review should not stop at the close-tab case.
The office should also review:
- ordinary reload/refresh,
- Back/Forward navigation,
- following help or policy links,
- opening official content in another window or application,
- sign-in or identity handoffs,
- and mobile app switching or background kill behavior.

Those may trigger different preservation and warning paths.
A route that is honest on same-tab close can still fail `476` if an external handoff or reload silently loses work while the route keeps implying it is protected.

## The leave warning must not impersonate office receipt

This is the most important boundary with `469` and `430`.
A leave warning is about **risk of loss before confirmed completion**.
It is not proof that:
- a draft was durably stored,
- a request was queued successfully,
- a submission reached the office,
- or a confirmation/receipt exists.

So the office should not let a route imply:
- “safe to leave” when only local volatile state exists,
- “saved” when the real state is merely “you may be able to resume on this device,”
- or “done” when the correct next state is still “submit,” “review,” “retry,” or “contact the office.”

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Leave-risk classification claim:** the office identified which voter-information routes have meaningful leave/reload/close loss risk.
2. **Mechanism-truthfulness claim:** the office distinguishes browser-generated leave confirmations from route-defined confirmations and does not describe either as stronger than they are.
3. **Saved-state boundary claim:** the route keeps unsaved, locally saved, queued, and office-acknowledged states visibly distinct at the leave moment.
4. **Conditional-warning claim:** browser or custom leave warnings are used when material unsaved state exists, not as constant ambient noise.
5. **Mobile/hidden-state humility claim:** the office does not assume a last-second leave warning will always appear and reviews earlier preservation posture accordingly.
6. **Recovery-route claim:** after a cancel, leave, reload, or accidental close, the route preserves a bounded restart/help/reopen path instead of forcing the voter to guess what the safest next step is.

## Canonical digest artifacts

Publish **digests of reviewed leave-risk posture**, not raw browsing telemetry.

- **Leave Warning Surface Digest (LWSD):** digest of reviewed routes, warning classes, and saved-state boundaries.
- **Unsaved-State Boundary Review Digest (USBRD):** optional digest proving that the route distinguishes unsaved, local-draft, queued, and office-acknowledged states at the leave moment.
- **Leave Recovery Route Digest (LRRD):** optional digest proving that cancel/leave/reopen paths route to a current safe official lane.

## What belongs in the public leave-warning payload

Keep the payload **small and state-class oriented**.
It usually needs only:
- surface identifier,
- jurisdiction identifier,
- reviewed route classes,
- leave-warning mechanism classes,
- saved-state boundary note,
- browser-dialog truthfulness note,
- custom-modal note,
- reload/close/mobile-loss note,
- recovery/help route,
- and last review time.

It does **not** need:
- raw session recordings,
- per-user exit telemetry,
- individualized draft contents,
- precise clickstreams of abandoned attempts,
- or device fingerprints collected merely to prove that the office thought about leave-risk honestly.

## Verification questions for third parties

A third-party verifier, journalist, watchdog, or accessibility reviewer should be able to ask:

- Which routes can still lose meaningful progress if the voter leaves, reloads, or closes the page?
- Does the route tell the truth about whether state is unsaved, local only, queued, or actually received by the office?
- Is any browser-generated dialog described with appropriate humility rather than as a guaranteed or richly explanatory warning?
- If the route uses a custom confirmation, does it clearly state the loss and the two choices in ordinary language?
- Does the route avoid relying on a last-second dialog as the only protection on mobile or app-switch paths?
- After leave/cancel/reopen, is there a bounded restart/help lane rather than a guesswork cliff?

## How this fits the family map

`476` belongs in the voter-facing public-answer-surfaces family because leaving a route is itself a public decision point.
The route may already be official and current, yet still fail because the last moment before departure lies about what is saved, what will be lost, or what the next safe step is.
It stays small by refusing to become a generic draft-storage handbook or a generic modal-pattern guide.
The archive only cares about the subset of leave-page warning behavior that changes the truthfulness, recoverability, or safety of official voter-information delivery.

## Minimal artifacts in this archive

- `artifacts/templates/official-voter-information-leave-warning-surface-payload.json`
- `artifacts/checklists/official-voter-information-leave-warning-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- `eac_effective_design_for_the_administration_of_federal_elections_page`
- `w3c_wai_multi_page_forms_page`
- `uswds_modal_component_page`
- `mdn_beforeunload_event_page`
- `mdn_visibilitychange_event_page`
