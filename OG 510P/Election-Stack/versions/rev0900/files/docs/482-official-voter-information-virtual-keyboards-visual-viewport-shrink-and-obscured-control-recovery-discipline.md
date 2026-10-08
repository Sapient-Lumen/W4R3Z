# 482 — Official voter-information virtual keyboards, visual-viewport shrink, and obscured-control recovery discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that people use while a mobile or tablet on-screen keyboard is open and the visible viewport changes before the voter has completed the current official answer/help step**:
address and ZIP lookups,
registration-status searches,
request/help forms,
contact-target or code-entry steps,
search boxes on long official pages,
and similar routes where the page may be current in principle but the practical answer lane disappears once focus opens the keyboard.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `416`, which governs broader reflow, text-scaling, and small-viewport survivability,
- `422`, which governs field purpose, input hints, autofill, and ordinary input-error recovery,
- `444`, which governs sticky headers, fixed chrome, and unobscured target landing,
- `478`, which governs text-assistance mutation and IME composition before the value is actually committed,
- `481`, which governs browser-native constraint validation and durable correction messaging,
- `483`, which governs clipped or overlapped text caused by spacing overrides even when the keyboard is not the deciding stressor,
- or `413`, which governs jumps into external handlers or other contexts.

It adds one narrow rule:
**if an official voter-information route expects people to type while an on-screen keyboard is open, the current answer/help lane should remain materially usable while the keyboard changes what is visible, and critical controls or correction text should not be hidden below the keyboard without a truthful, recoverable way to continue.**

## Why this is a distinct surface

The EAC’s current election-design guidance treats election information materials as core public communications whose legibility and usability affect whether voters can act correctly. Digital.gov’s current digital-first public-experience requirements say federal digital services should be accessible, user-centered, and mobile-first across varying device sizes. USWDS’s current text-input and form guidance says mobile context matters and validation/error text should align with the input it explains. MDN’s current `VisualViewport` documentation is especially important because it says the on-screen keyboard can shrink the **visual viewport** without changing the **layout viewport**. MDN’s current viewport reference separately says the virtual keyboard affects viewport size and that `interactive-widget=resizes-content` can ask the page layout to adapt. MDN’s current `VirtualKeyboard` API documentation says browsers can also expose geometry information and `keyboard-inset-*` environment variables when authors opt out of the default behavior, but that API surface is experimental and browser-dependent. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `uswds_text_input_component_page`; xref: `uswds_form_component_page`; xref: `mdn_visualviewport_api_page`; xref: `mdn_meta_viewport_page`; xref: `mdn_virtualkeyboard_api_page`)

That is enough to justify a compact control here.
A route can pass ordinary small-screen review and still fail first contact because:
- focusing a field opens the keyboard and hides the submit, continue, help, or next-step control,
- inline error text appears beneath the keyboard while the page acts as though the correction is obvious,
- the current result card or office contact path is pushed out of view once the user begins typing,
- a fixed footer or sticky action bar collides with the keyboard and leaves no reachable continuation path,
- or the page assumes layout changes that never happen because only the visual viewport changed.

## This is not the same thing as generic small-screen reflow, field hints, or sticky headers

`416` asks whether the route remains readable and actionable on narrow viewports or enlarged text.

`422` asks whether the voter can understand what to enter, use sensible field hints, and recover from ordinary entry mistakes.

`444` asks whether persistent chrome such as sticky headers or banners obscures jump targets or revealed sections.

`481` asks whether browser-native validation messages and pre-submit blocking remain subordinate to durable authored correction text.

`482` asks a different question:
**while the on-screen keyboard is open and the visible viewport changes, can the voter still see enough of the current answer/help lane to continue honestly, or does the route hide its own operative controls, correction text, or recovery path beneath the keyboard?**

A route may pass the earlier controls and still fail `482` if:
- labels and hints are fine before focus, but the keyboard hides the only visible continue button,
- the page reflows acceptably at rest, but focused-entry state leaves the current result or help lane offscreen with no clear path back,
- sticky chrome is not the problem, but the keyboard plus a bottom action bar consumes the usable viewport,
- or browser-native validation fires, yet the correction cue sits where the voter cannot actually see it while the keyboard remains open.


If the decisive readability failure comes from increased line/paragraph/word/letter spacing rather than from the keyboard-open viewport itself, that belongs to `483` instead of `482`.

## The keyboard changes what is visible even when the page layout seems unchanged

MDN’s current `VisualViewport` documentation says the mobile web has both a layout viewport and a visual viewport, and that the on-screen keyboard can shrink the visual viewport without affecting the layout viewport. (xref: `mdn_visualviewport_api_page`)

That distinction matters because many public-service pages are authored as though “the page height” is one thing.
In practice, the voter may focus a field and immediately lose sight of:
- the first lines that explain the lookup,
- the error summary,
- the search results that were already visible,
- or the button that completes the public step.

So `482` is not a demand for perfect keyboard choreography on every device.
It is a demand not to treat the keyboard-open state as somebody else’s problem once the official route depends on typing.

## `interactive-widget=resizes-content` is a reviewed choice, not a magic guarantee

MDN’s current viewport reference says the browser’s virtual keyboard normally resizes only the visual viewport and that authors can request layout adaptation with `interactive-widget=resizes-content`. (xref: `mdn_meta_viewport_page`)

For this archive, that implies a narrow discipline:
- if the route depends on layout adaptation when the keyboard opens, review that behavior explicitly,
- if the route does **not** adapt layout, still make sure the voter can reach the hidden controls or dismiss the keyboard without losing context,
- and do not describe a browser-dependent resize behavior as though it were universal truth.

The rule is not “every route must use `interactive-widget=resizes-content`.”
The rule is “do not quietly depend on keyboard-resize folklore.”

## Experimental keyboard-geometry APIs are optional helpers, not the only safe path

MDN’s current `VirtualKeyboard` API documentation says authors can opt out of the default automatic behavior, obtain keyboard geometry, and use `keyboard-inset-*` CSS environment variables to adapt layout. It also marks the exposed `Navigator.virtualKeyboard` and related controls as experimental. (xref: `mdn_virtualkeyboard_api_page`)

That means `482` should be humble about support variance.
A public election route may use these APIs carefully, but it should not require them as the only way a voter can finish the task.
The route still needs a plain recovery story when those APIs are unavailable, unsupported, or simply not the browser’s chosen behavior.

## Error text, help, and action controls must remain practically reachable while typing

USWDS’s current form and text-input guidance is useful here because it frames form usability around field-adjacent help and mobile context. (xref: `uswds_form_component_page`; xref: `uswds_text_input_component_page`)

For `482`, that means a route should review at least four things together:
1. **focused field visibility** — the user can still tell which field is active and what it is for,
2. **current answer/help context** — the currently relevant result, office, or explanation is not completely stranded offscreen,
3. **correction visibility** — inline or page-level error/help text can still be found while the keyboard is open,
4. **continuation visibility** — submit, continue, search, reveal, or help controls remain reachable or the route gives a truthful way to dismiss the keyboard and continue without losing place.

The archive does **not** require every button to remain simultaneously visible with the keyboard open.
It requires that the voter not be left in a state where the page implicitly says “continue now” while the actual continuation path is hidden, clipped, or guesswork.

## Keep focused-entry state distinct from committed answer state

Typing is often an intermediate condition, not the final reviewed state.
A route fails `482` when keyboard-open posture makes the voter mistake provisional entry for a committed lookup, submitted request, or completed correction.
Examples include:
- a live result panel that scrolls away as the keyboard opens so the user no longer knows which result the page is reacting to,
- an auto-advancing or auto-submitting field whose decisive control is never clearly visible once the keyboard appears,
- or a review/confirmation step that is technically below the fold but effectively unreachable while typing.

This composes with `478`, `481`, and `477`.
The point is not to ban live update or focused-entry behavior.
It is to keep the route honest about what has merely been typed, what has actually been reviewed, and what has already been accepted.

## Minimal keyboard-open state taxonomy

A compact state taxonomy is enough:

1. **Resting pre-focus state** — the route is visible before any editable control is focused.
2. **Keyboard-open entry state** — a focused control has opened the on-screen keyboard and reduced the visible viewport.
3. **Keyboard-obscured-action risk state** — a continuation, help, or correction control is threatened by the keyboard-open viewport.
4. **Dismiss-and-resume state** — the route lets the voter hide the keyboard or move focus without losing the current place or meaning.
5. **Committed review state** — the route clearly shows the result, correction, or next step after the user finishes typing.
6. **Keyboard-open lane remains usable** — the current official answer/help path stays materially reachable across the reviewed focused-entry states.

## Preserve bounded reconstruction, not input telemetry exhaust

What matters here is bounded reconstruction of the office’s keyboard-open posture:
- which public routes were reviewed while the on-screen keyboard was open,
- which controls or correction lanes were deemed critical,
- whether layout adaptation, visual-viewport handling, or plain dismiss-and-resume posture was reviewed,
- whether focused-entry and committed-review states were kept distinct,
- and when the review last occurred.

Do **not** preserve by default:
- per-user keystroke logs,
- individualized viewport recordings,
- invasive session-replay archives,
- or fine-grained keyboard telemetry when a compact surface digest is enough.

## Claims this control should support

1. **Keyboard-open review claim:** the office identified important public routes that people use while the on-screen keyboard is open.
2. **Visible-continuation claim:** the route keeps a truthful continuation/help path visible or recoverable while the keyboard changes the visible viewport.
3. **Correction-visibility claim:** error/help text remains practically discoverable in the keyboard-open state rather than disappearing beneath the keyboard.
4. **Viewport-humility claim:** the route does not assume layout resize behavior that only some browsers expose, and any browser-specific adaptation posture is reviewed explicitly.
5. **Support-variance claim:** experimental keyboard-geometry APIs are treated as optional helpers rather than the route’s only safe path.
6. **State-boundary claim:** keyboard-open entry state stays distinct from committed result, accepted submission, or server-reviewed outcome state.

## Canonical digest artifacts

Publish **small digests of keyboard-open route posture**, not keystroke analytics.

- **Keyboard-Open Surface Digest (KOSD):** digest of reviewed routes, keyboard-open continuation posture, and last review time.
- **Visible Continuation Under Keyboard Digest (VCUKD):** optional digest describing how critical action/help controls remain reachable while typing.
- **Focused Entry vs Committed Review Digest (FECRD):** optional digest describing how the route keeps provisional entry state distinct from reviewed result/next-step state.

## What belongs in the public virtual-keyboard payload

Keep the payload **small, route-aware, and explicit about keyboard-open recovery posture**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `virtual_keyboard_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `keyboard_open_route_classes[]`
- `critical_controls[]`
- `visual_viewport_behavior_note`
- `layout_adaptation_note`
- `dismiss_and_resume_note`
- `error_or_help_visibility_note`
- `focused_entry_vs_committed_review_note`
- `support_variance_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- raw typed values,
- per-user viewport traces,
- session replays,
- or fine-grained keyboard telemetry merely to prove the posture was reviewed.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which public routes were reviewed while the on-screen keyboard was open?
- When the keyboard opens, can the voter still reach the current answer/help lane or a truthful dismiss-and-resume path?
- Are error/help messages still visible enough to correct the problem while typing?
- Does the route clearly separate provisional keyboard-open entry from committed result, accepted submission, or server-reviewed rejection?
- If browser-specific keyboard-geometry or resize features are used, did the office treat them as support-variant helpers rather than as a universal guarantee?
- Could a mobile voter finish the step without guessing where the hidden continue/help control went?

## How this fits the family map

Virtual-keyboard / visual-viewport / obscured-control recovery is **not** a new underlying voter-question family bucket.
It is a shared public-surface control that can apply to many voter-information routes whenever the decisive first-contact risk appears only after focus opens the on-screen keyboard.

Use it when the route is basically the right one, but typing itself changes what is visible enough that the current answer/help lane may disappear.
Keep using:
- `416` for broader small-screen and text-resize survivability,
- `422` for field-purpose and general input recovery,
- `444` for sticky-chrome obscuration,
- `478` for mutation/composition before commit,
- and `481` for browser-native validation/error-message posture.

This document only says that, if an office expects the public to type into an official route on mobile or tablet devices, the keyboard-open state should remain reviewable, recoverable, and honest rather than quietly hiding the very control or correction path the voter still needs.

## Sources (current anchors)

- EAC: Effective election design guidance (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Digital.gov: requirements for delivering a digital-first public experience (xref: `digital_gov_requirements_digital_first_public_experience_page`)
- USWDS: text input component (xref: `uswds_text_input_component_page`)
- USWDS: form component (xref: `uswds_form_component_page`)
- MDN: `VisualViewport` API (xref: `mdn_visualviewport_api_page`)
- MDN: `<meta name="viewport">` reference (xref: `mdn_meta_viewport_page`)
- MDN: `VirtualKeyboard` API (xref: `mdn_virtualkeyboard_api_page`)

## Companion artifacts

- Template payload: `artifacts/templates/official-voter-information-virtual-keyboard-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-virtual-keyboard-surface-checklist.md`
