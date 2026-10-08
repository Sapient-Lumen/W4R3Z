# 461. Official voter-information buttons, links, and action-destination truthfulness discipline

**Track:** Shared

This document defines a bounded control for **official voter-information routes where the controlling next step is exposed through visually prominent interactive controls** — buttons, CTA links, links styled as buttons, grouped action bars, inline action links, or similar controls — where:

- the right official route or next step already exists,
- but the control makes it hard to tell whether activation **navigates to another official page**, **submits or confirms**, **opens a dialog/drawer**, **downloads a file**, **starts a call/email route**, or **changes only the current page state**,
- multiple similarly styled controls collapse primary versus secondary meaning,
- or the visible wording and the underlying control semantics tell different stories about what will happen next.

The concern here is not simply that a page has buttons and links.
It is the narrower failure mode where a voter is already on the right official site, but the **control posture itself** obscures whether the next step is destination travel or in-page action, making the official route harder to predict, trust, and safely repeat.

## Why this surface exists

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes clarity, structure, accessibility, usability, and accuracy. USWDS’s current **Button** guidance matters because it says buttons are for important actions, says linking between a site’s pages should use regular links instead, says button text should clearly explain what will happen, and notes that screen readers handle links and buttons differently even when links are styled to look like buttons. USWDS’s current **Link** guidance matters because it says links are navigational elements that direct visitors to other locations or further information. USWDS’s current **Button group** guidance matters because it says teams should use the native `<button type="button">` element and not use `<a>` because it is a link. MDN’s current **Anchor (`<a>`)** reference matters because it says anchors create hyperlinks to pages, files, email addresses, locations in the same page, or other URL-addressable destinations, and that the content of the anchor should indicate the link’s destination. MDN’s current **ARIA `button` role** reference matters because it says buttons trigger a response/action and that authors should generally prefer native `<button>` elements to custom button roles. W3C’s current **Link Purpose (In Context)** guidance matters because it says users should be able to determine a link’s purpose from its text or associated context, and says continuity between the link text and the destination title is good practice. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `uswds_button_component_page`; xref: `uswds_link_component_page`; xref: `uswds_button_group_component_page`; xref: `mdn_html_anchor_element_page`; xref: `mdn_button_role_page`; xref: `w3c_wcag21_link_purpose_in_context_page`)

So this archive treats button/link posture as its own public-surface problem:
**the right official step may already exist, but the control that exposes it may misstate whether it goes somewhere, does something here, or commits an action the voter did not mean to take yet.**

## This is distinct from adjacent surfaces

This document is intentionally narrow.
It is **not** the same as:

- `413` external destinations and new-context handoffs, which governs leaving the official site or opening a materially different browsing context;
- `417` keyboard navigation and logical order, which governs broader sequential operability;
- `418` screen-reader semantics and labels, which governs broader nonvisual structure and programmatic naming;
- `447` cards and answer-tile disambiguation, which governs repeated card/collection items;
- `459` answer overlays/dialogs/drawers, which governs what happens after a control opens a transient answer layer;
- `460` navigation menus and fly-outs, which governs controlling destinations hidden inside expandable site navigation;
- or `471`, which governs copy/share controls once the action itself is to hand off a portable pointer or snippet rather than merely navigate or act in place.

`461` exists only for the case where the **control itself** — button, link, CTA, or grouped action — becomes directionally ambiguous about whether the voter is about to travel, submit, reveal, download, call, or act on the current page.

## Navigation controls should read like destinations; action controls should read like actions

USWDS’s current split is clear: use buttons for important actions, and use regular links for linking between a site’s pages. MDN’s current anchor reference says anchors create hyperlinks to destinations, while the button-role guidance says buttons trigger actions such as submit/open/cancel/command behavior. (xref: `uswds_button_component_page`; xref: `mdn_html_anchor_element_page`; xref: `mdn_button_role_page`)

For this archive, a route fails this surface when:

- a control that actually navigates to another official page is presented as though it merely toggles or confirms something locally,
- a control that actually submits or commits is phrased like harmless exploration,
- a link to another page is grouped with in-page controls so tightly that the voter cannot tell which actions are reversible,
- or the page makes “go somewhere else” and “do something now” look operationally interchangeable.

The archive does **not** require a purely visual distinction between every link and button style.
It requires that the control’s wording, grouping, and semantics tell a truthful story about what kind of step comes next.

## Button styling on links is allowed, but the destination truth must remain legible

USWDS’s current button guidance explicitly says teams may add button styles to links, and also warns that screen readers handle links and buttons differently. That means visual emphasis is not the problem by itself. The problem is when styling makes a destination control look like an immediate page-local action or when button language hides the fact that the user is leaving the current route. (xref: `uswds_button_component_page`)

So for this archive:

- a link may be visually emphasized like a button when the office wants to highlight an important destination,
- but the label and surrounding context should still make clear that the control goes to another page, file, or route,
- and a button-like appearance should not erase the ordinary expectations people have for links, such as opening a destination rather than toggling current-page state.

This is especially important on official routes that mix:

- `View polling place`,
- `Check registration status`,
- `Download sample ballot`,
- `Contact the office`,
- `Open details`,
- `Copy link`,
- or `Submit request`.

Those are not all the same kind of step, even if the design system gives them similarly prominent treatment.

## Labels should describe the next step and distinguish neighboring controls

USWDS’s current button guidance says button text should be short, action-based, and lead with a verb. W3C’s current link-purpose guidance says link purpose should be determinable from the text or its associated context, and that continuity between link text and destination title is good practice. MDN’s anchor guidance says anchor content should indicate the destination. (xref: `uswds_button_component_page`; xref: `w3c_wcag21_link_purpose_in_context_page`; xref: `mdn_html_anchor_element_page`)

For this archive, that means the route should avoid:

- several controls that all say `Continue`, `Learn more`, or `Details` while doing materially different things,
- one label used for multiple different destinations in the same answer lane,
- vague verbs that hide commitment versus exploration,
- or labels that imply one destination while landing on a differently titled official route.

A voter under time pressure should be able to tell:

- which control goes to the governing official page,
- which control performs a local action,
- which control starts a communication channel,
- and which control is optional secondary help.

## Grouped controls should preserve primary-versus-secondary meaning

USWDS’s current button-group guidance says grouped controls should preserve relationship semantics and use useful naming. In practice, that matters because official voter-information routes often present several adjacent CTAs at once: continue, save, download, contact, change answer, open map, or return to list. (xref: `uswds_button_group_component_page`)

A grouped-control lane fails this surface when:

- the primary governing route is visually indistinguishable from auxiliary or optional actions,
- a destructive or committing action sits beside a navigational link with nearly identical wording,
- the grouping hides whether controls are mutually exclusive next steps or parallel optional routes,
- or the same control cluster changes semantics between desktop and mobile layouts without making the change visible.

The archive is not asking for maximal design ceremony.
It is asking for enough truth that “these are related controls” does not collapse into “the voter cannot tell which one safely advances the official route.”

## Prefer native controls for the job they are actually doing

USWDS’s current button-group guidance says use the native `<button type="button">` element and do not use `<a>` because it is a link. MDN’s button-role guidance says authors should generally prefer native button elements over custom button roles. MDN’s anchor guidance separately makes clear that anchors are hyperlinks when `href` is present. (xref: `uswds_button_group_component_page`; xref: `mdn_button_role_page`; xref: `mdn_html_anchor_element_page`)

For this archive, native semantics matter because they preserve ordinary expectations:

- links behave like destinations,
- buttons behave like actions,
- assistive technology announces them differently,
- and keyboard behavior differs in ways voters may notice even if they never read the markup.

A route does **not** need custom widgets when ordinary buttons and links already express the truth.
If a control is really navigation, keep it honest as navigation.
If a control is really submit/open/copy/reveal behavior, keep it honest as an action.

## Page-change versus current-page-change posture should stay visible

Many official routes mix both types of step at once:

- a control that opens an answer overlay,
- a control that reveals more detail in the current card,
- a control that submits a lookup form,
- a control that downloads a PDF,
- a control that opens a phone or email route,
- and a control that navigates to the office/help page.

This archive does not forbid mixed action bars.
It says the route should preserve a bounded truth about **which controls keep the voter on the same page** and **which controls take the voter elsewhere or commit a step**.

If the control’s job is not navigation or page-local action at all, but copying/sharing an official portable pointer or summary, `471` governs that copy/share truthfulness layer rather than `461` treating it as an ordinary CTA.

A voter should not have to discover by surprise that:

- `View details` actually leaves the current route,
- `Check status` immediately submits instead of opening the status page,
- `Contact us` opens a mail client when the surrounding page made it sound like an office directory,
- or `Get help` downloads a PDF instead of opening the current official help page.

More specific controls such as overlays (`459`), downloads (`378`), and external handoffs (`413`) still govern those outcomes after they happen.
`461` only says the control should tell the truth before activation.

## Preserve bounded review evidence, not individualized interaction exhaust

The evidence posture here is about reconstructing whether the office reviewed control truthfulness for important answer-lane controls.
The archive should preserve:

- which official routes were reviewed for mixed button/link posture,
- which controls were classified as navigation versus in-page action versus submit/download/call/email,
- whether grouped controls preserved primary-versus-secondary meaning,
- whether link labels matched their destinations and button labels matched their actions,
- and when the review last occurred.

It should **not** require preserving:

- individualized click logs,
- session replay,
- per-user heatmaps,
- or detailed telemetry merely to prove that a label was once confusing.

## Canonical digest artifacts

Publish **small digests of control-truth posture**, not click exhaust.

- **Control Truth Surface Digest (CTSD):** digest of the bounded button/link posture for a route family.
- **Action/Destination Integrity Digest (ADID):** optional digest describing which controls are navigation, submission, overlay-opening, download, or communication routes.
- **Primary Action Separation Digest (PASD):** optional digest describing whether grouped controls preserve primary-versus-secondary meaning.

## What belongs in the public button/link payload

Keep the payload **small, route-aware, and next-step focused**.

Recommended top-level fields:

- stable `surface_id`
- `jurisdiction_id` / election scope
- `button_link_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `reviewed_controls[]`
- `control_semantics_note`
- `visual_emphasis_note`
- `label_truth_note`
- `primary_secondary_action_note`
- `same_page_vs_new_route_note`
- `submit_open_download_call_note`
- `keyboard_semantics_note`
- `destination_title_continuity_note`
- `compact_mobile_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:

- individualized click histories,
- raw funnel analytics,
- session replay,
- A/B experiment notes,
- or internal conversion-optimization commentary that is not needed to reconstruct the bounded public posture.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:

- Which official controls on this route are navigation destinations, and which are in-page or submit actions?
- Do visually prominent controls tell the truth about whether they will navigate, reveal, submit, download, call, or email?
- Are grouped controls clear about which path is primary, which is optional, and which is potentially committing?
- Do link labels match their destinations closely enough that the next page is not a surprise?
- Are native control semantics used honestly enough that voters are not asked to infer control type from styling alone?
- Did the office preserve bounded review evidence without retaining individualized interaction exhaust?

## How this fits the family map

Buttons, links, and action-destination truthfulness is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if an official voter-information route depends on CTA-like controls to move a voter toward the next governing step, the controls should stay honest enough that styling, grouping, and wording do not obscure whether the voter is about to go somewhere else or do something here.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-button-link-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-button-link-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- USWDS: Button (xref: `uswds_button_component_page`)
- USWDS: Link (xref: `uswds_link_component_page`)
- USWDS: Button group (xref: `uswds_button_group_component_page`)
- MDN: HTML anchor element (xref: `mdn_html_anchor_element_page`)
- MDN: ARIA `button` role (xref: `mdn_button_role_page`)
- W3C: Understanding SC 2.4.4 Link Purpose (In Context) (xref: `w3c_wcag21_link_purpose_in_context_page`)
