# 463 — Official voter-information tooltips, popovers, hover-help, and essential-answer visibility discipline

**Track:** Shared

This document defines a bounded control for **official voter-information routes that place clarifications, exceptions, definitions, or next-step meaning inside small help bubbles, tooltips, popovers, or similar transient disclosure layers** — for example info-icon bubbles, hover-help microcopy, question-mark hints, or button-triggered hint cards — where:

- the controlling official answer or exception appears only after hover or focus,
- the help layer disappears too quickly to read or compare,
- the trigger does not look interactive enough to be discovered,
- the disclosure covers the content it is meant to explain,
- or a small supplemental hint posture silently becomes the only place a voter can learn a deadline caveat, eligibility exception, or required next step.

The concern here is not merely that a page contains helper text.
It is the narrower failure mode where a voter is already on the right official route, but the route hides essential meaning inside **ephemeral or space-constrained help UI** and therefore makes the answer depend on discovering and successfully operating a hint bubble.

## Why this surface exists

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes clarity, understandability, accessibility, usability, and accuracy. USWDS’s current **Tooltip** guidance matters because it says tooltips are for helpful, non-critical information, work best as brief helper text, are a last resort for space-constrained UI, and should not hide information necessary for completing a task behind a tooltip interaction. The same guidance says tooltips should be discoverable, should be used only on elements that appear interactive, should avoid conflicting hover/focus events, and should not block page content; USWDS’s current tooltip accessibility tests also matter because teams are told to test tooltip behavior in the context of their own site, including zoom, keyboard, and screen-reader review. W3C’s current understanding guidance for **Content on Hover or Focus** matters because custom tooltips and other nonmodal hover/focus popups must be dismissible, hoverable, and persistent enough not to interfere with task completion. MDN’s current **ARIA tooltip role** reference matters because browser `title`-style hover tooltips are inaccessible to keyboard focus and touch, because important information should be visible text instead of hidden tooltip copy, and because tooltips are not supposed to become interactive mini-dialogs. WAI APG’s current **Tooltip Pattern** matters because it says tooltip widgets do not receive focus and that hover content with focusable elements should be implemented as a non-modal dialog instead. MDN’s current **HTML `popover` global attribute** reference matters because modern popovers are explicitly invoked by a control such as a button with `popovertarget` and appear in the top layer, which makes them a better fit than hover-only tooltip posture when the office truly needs a deliberate, persistent disclosure surface. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `uswds_tooltip_component_page`; xref: `uswds_tooltip_accessibility_tests_page`; xref: `w3c_wcag22_content_on_hover_or_focus_page`; xref: `mdn_tooltip_role_page`; xref: `w3c_wai_aria_apg_tooltip_pattern_page`; xref: `mdn_html_popover_global_attribute_page`)

So this archive treats tooltip/popover help posture as its own public-surface problem:
**the right official page may already be open, but the controlling clarification or exception lives in a transient hint layer whose trigger, persistence, or semantics are too weak to carry essential public meaning safely.**

## This is distinct from adjacent surfaces

This document is intentionally narrow.
It is **not** the same as:

- `421` touch target size, hover-revealed content, and pointer operability, which governs coarse-pointer survivability and no-hover equivalents across the route;
- `443` accordions/disclosures, which governs larger collapsed answer panels that remain part of the ordinary document flow;
- `459` answer overlays/dialogs/drawers, which governs larger user-triggered overlay surfaces with route continuity concerns;
- or `462` disabled controls and unlock-path legibility, which governs unavailable next-step posture rather than help-bubble meaning.

`463` exists only for the case where a route relies on **small transient hint layers** to carry meaning that may control interpretation of the official answer.

## Tooltips should stay supplemental, brief, and non-critical

USWDS’s current tooltip guidance is unusually direct: tooltips are for helpful, non-critical information, brief descriptions, and last-resort space-constrained UI, and teams should not hide information necessary for task completion behind a tooltip interaction. MDN’s current tooltip-role guidance adds the sharper principle: if information is important enough for a tooltip, it should often just be visible text. (xref: `uswds_tooltip_component_page`; xref: `mdn_tooltip_role_page`)

For this archive, a tooltip posture should not be asked to carry the only visible statement of:

- a deadline exception,
- a required document nuance,
- a jurisdiction rule that changes the answer,
- a payment/fee caveat,
- a ballot-return restriction,
- or the only explanation of why a visible route differs from a general expectation.

A tooltip may strengthen confidence or define a term.
It should not become the only place the voter can learn what actually controls.

## The trigger must be discoverable and honest about what it reveals

USWDS says tooltips should be discoverable and used only on elements that appear interactive, like buttons or links. That matters because hidden or decorative-looking info icons do not behave like reliable public-answer surfaces. (xref: `uswds_tooltip_component_page`)

So for this archive, a route should not:

- hide critical explanatory text behind an unlabeled symbol that does not look actionable,
- attach help text to tiny hover targets that are easy to miss,
- mix multiple overlapping hover/focus behaviors so the voter cannot tell which element owns the hint,
- or style the trigger so weakly that the existence of the extra meaning is effectively secret.

The public should be able to tell, in bounded form:

- that extra explanatory material exists,
- what control reveals it,
- whether the disclosure is supplemental or more substantial,
- and where the same meaning lives in durable text if it is important enough to control a decision.

## Hover/focus disclosures must stay dismissible, hoverable, and persistent enough to read

W3C’s current understanding guidance for **Content on Hover or Focus** says custom tooltips and other nonmodal hover/focus popups must be dismissible, hoverable, and persistent. MDN’s tooltip-role reference and APG’s tooltip pattern reinforce that the tooltip should remain available while the pointer moves to it and that `Escape` should dismiss it. (xref: `w3c_wcag22_content_on_hover_or_focus_page`; xref: `mdn_tooltip_role_page`; xref: `w3c_wai_aria_apg_tooltip_pattern_page`)

For this archive, a route fails when:

- the hint disappears the moment the pointer leaves the trigger,
- the voter cannot move onto the bubble to finish reading it,
- the bubble obscures the surrounding answer and cannot be dismissed cleanly,
- or keyboard users trigger the disclosure but cannot keep it open long enough to understand it.

This is especially important on public routes where a tooltip explains address-entry rules, ID nuances, ballot-style exceptions, or office-hour caveats that the voter may need to compare against the surrounding page.

## Tooltip semantics and popover semantics should not be mixed carelessly

MDN’s tooltip-role guidance and APG’s tooltip pattern both make clear that a tooltip is a non-interactive help bubble that does not receive focus. APG explicitly says that hover content with focusable elements should instead be made as a non-modal dialog. MDN’s current `popover` attribute guidance matters because modern popovers are invoked through an explicit control and enter the top layer, which makes them a more honest choice when the office really needs a deliberate, persistent, button-triggered disclosure. (xref: `mdn_tooltip_role_page`; xref: `w3c_wai_aria_apg_tooltip_pattern_page`; xref: `mdn_html_popover_global_attribute_page`)

So for this archive:

- a true tooltip should stay brief, supplementary, and non-interactive,
- a disclosure that contains links, buttons, long text, or multi-step instructions should not masquerade as a tooltip,
- and a popover/help card should not pretend to be “just a tooltip” when it is really carrying durable operational guidance.

The goal is not semantic purity for its own sake.
The goal is that the interaction model tells the truth about how much meaning is being hidden and how deliberately the voter must engage it.

## If the content is important, provide a durable visible path as well

USWDS says teams should explore other options for keeping content visible without a tooltip and should not use tooltips for critical information. MDN’s tooltip-role guidance similarly says to prefer clear visible descriptions when possible. (xref: `uswds_tooltip_component_page`; xref: `mdn_tooltip_role_page`)

For this archive, an office should prefer:

- inline helper text,
- short visible exception notes,
- adjacent explanatory copy,
- an explicit “More details” disclosure in document flow,
- or a deliberate button-triggered durable disclosure surface

when the information controls whether the voter proceeds, retries, chooses another path, or interprets a key rule correctly.

A route should not rely on a tooltip as the only durable repository of a governing exception and then expect voters to memorize it after the bubble disappears.

## Top-layer popovers should not cover or replace the controlling answer by surprise

MDN’s popover guidance says open popovers enter the top layer and are not influenced by parent overflow or positioning. That is useful when a deliberate help surface must escape clipping, but it also means popovers can cover surrounding answer text more forcefully than authors expect. USWDS’s tooltip guidance separately says tooltip positioning should avoid blocking content. (xref: `mdn_html_popover_global_attribute_page`; xref: `uswds_tooltip_component_page`)

So for this archive, a popover/help bubble should not:

- cover the exact deadline/help text it is meant to clarify,
- open in a way that makes the surrounding official answer look gone or contradicted,
- trap the voter into a tiny floating island whose close/return meaning is unclear,
- or create a stronger visual emphasis than the answer itself when the bubble is only supplemental.

If a disclosure needs this much weight, it may belong in the route body or in the answer-overlay family instead of in a hint-bubble posture.

## Preserve bounded review evidence, not hover exhaust

The evidence posture here is about reconstructing whether the office reviewed tooltip/popover truthfulness on important public routes.
The archive should preserve:

- which routes used tooltip/popover help for public meaning,
- which triggers were reviewed,
- whether the disclosed content was supplemental or controlling,
- whether a durable visible alternative existed for important meaning,
- whether dismissible/hoverable/persistent behavior was reviewed,
- and when the review last occurred.

It should **not** require preserving:

- individualized hover telemetry,
- cursor-path recordings,
- session replay,
- heatmaps,
- or per-user hesitation traces merely to prove that a help bubble once existed.

## Canonical digest artifacts

Publish **small digests of hint-layer posture**, not hover exhaust.

- **Hint Surface Digest (HSD):** digest of bounded tooltip/popover posture on a route family.
- **Essential Meaning Visibility Digest (EMVD):** optional digest describing which important rules remain visible outside transient help layers.
- **Durable Help Disclosure Digest (DHDD):** optional digest describing which disclosures use explicit persistent popover/disclosure posture rather than hover-only hints.

## What belongs in the public tooltip/popover payload

Keep the payload **small, route-aware, and meaning-visibility focused**.

Recommended top-level fields:

- stable `surface_id`
- `jurisdiction_id` / election scope
- `tooltip_popover_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `reviewed_disclosures[]`
- `supplemental_only_note`
- `essential_info_visibility_note`
- `trigger_discoverability_note`
- `hover_focus_behavior_note`
- `dismissible_hoverable_persistent_note`
- `tooltip_vs_popover_semantics_note`
- `durable_alternative_note`
- `overlay_collision_note`
- `keyboard_touch_note`
- `compact_mobile_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:

- per-user hover/focus traces,
- cursor heatmaps,
- raw analytics exports,
- session replay,
- or internal microcopy experiments that are not needed to reconstruct the bounded public posture.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:

- Which official routes depend on tooltip/popover help to explain public meaning?
- Is any critical rule, exception, or prerequisite hidden only in a transient hint layer?
- Do help bubbles remain readable long enough to use, including under zoom and keyboard review?
- Are tooltip semantics used only for brief, non-interactive supplemental help while more substantial disclosures use a more honest pattern?
- Does the route preserve the same governing meaning in visible or otherwise durable text when the information controls a real public decision?
- Did the office preserve bounded review evidence without retaining individualized hover exhaust?

## How this fits the family map

Tooltips, popovers, hover-help, and essential-answer visibility is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if an official voter-information route uses small help disclosures to explain the answer, the route should keep those disclosures supplemental enough, discoverable enough, and durable enough that the answer does not depend on mastering a fragile hint bubble.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-tooltip-popover-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-tooltip-popover-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- USWDS: Tooltip (xref: `uswds_tooltip_component_page`)
- USWDS: Tooltip accessibility tests (xref: `uswds_tooltip_accessibility_tests_page`)
- W3C: Understanding SC 1.4.13 Content on Hover or Focus (xref: `w3c_wcag22_content_on_hover_or_focus_page`)
- MDN: ARIA tooltip role (xref: `mdn_tooltip_role_page`)
- WAI-ARIA APG: Tooltip pattern (xref: `w3c_wai_aria_apg_tooltip_pattern_page`)
- MDN: HTML `popover` global attribute (xref: `mdn_html_popover_global_attribute_page`)
