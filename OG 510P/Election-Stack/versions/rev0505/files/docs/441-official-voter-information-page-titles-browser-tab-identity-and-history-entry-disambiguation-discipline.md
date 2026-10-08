# 441 — Official voter-information page titles, browser-tab identity, and history-entry disambiguation discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **the chrome-level identity of official voter-information routes as they appear before, during, and after ordinary navigation**:
HTML page titles,
browser-tab labels,
history-entry labels,
app-switcher or recent-items labels derived from the page title,
screen-reader first-contact title announcements,
and client-side title updates when a single-page application changes the effective route without a full reload.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `392`, which governs source identity and official-site recognition at the search/result level,
- `393`, which governs breadcrumb / FAQ structured-data eligibility,
- `396`, which governs freshness dates and byline-date cues,
- `438`, which governs whether a current official URL can be safely bookmarked, copied, or shared,
- `439`, which governs whether an already-open route stays fresh on return through history, restore, or duplicate tabs,
- or `440`, which governs what survives when the browser extracts a simplified reading surface from the page.

It adds one narrow rule:
**if an official voter-information route may be reselected, revisited, or distinguished through browser or app chrome, the route should expose a unique current page title that names the task or answer first, preserves enough office/jurisdiction context to disambiguate the route, and updates when client-side navigation changes the effective official state.**

## Why this is a distinct surface

The EAC's current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes clarity, structure, accessibility, usability, and accuracy. Federal website standards' current **HTML page title** standard says every public-facing page should have a unique HTML page title, that titles should be descriptive and concise, that the unique part should appear first, and that branding/site name should appear at the end. MDN's current `<title>` reference says the document title is shown in a browser tab and that a common navigation technique for assistive-technology users is to read the page title to infer what the page contains. MDN's current `document.title` reference says scripts can get or set the current document title. USWDS's current **banner** guidance says the banner should identify an official government site and should appear on every page, its current **header** guidance says the header helps users identify where they are, and its current **breadcrumb** guidance says breadcrumb text should use the same wording as the page title. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `federal_website_standards_html_page_title_page`; xref: `mdn_title_element_page`; xref: `mdn_document_title_property_page`; xref: `uswds_banner_component_page`; xref: `uswds_header_component_page`; xref: `uswds_breadcrumb_component_page`)

That is enough to justify a compact control here.
A route may pass `438`, `439`, and `440` yet still fail the public because:
- several official tabs all collapse into the same generic browser title such as “Elections” or “Voter Portal,”
- the page heading changes after lookup or route transition while the browser/tab title stays on the old shell label,
- the title names the agency but not the task, so a voter cannot tell whether the tab is registration status, polling place, cure, or ballot-tracking,
- the title names the task but drops the office/jurisdiction context, so state and county routes become hard to distinguish,
- a single-page application changes the effective route without updating the document title,
- or the live page is correct while the title shown in tabs, history, or assistive-technology title announcements remains stale, generic, or contradictory.

## This is not the same thing as share-safe URLs, freshness on return, or reader mode

`438` asks whether the current URL itself is portable, bookmark-safe, and free of secret-bearing query state.

`439` asks whether the already-open route stays fresh and internally consistent when the voter returns through history, restore, or duplicate tabs.

`440` asks whether the controlling answer survives extraction into a simplified reading surface.

`441` asks a different question:
**when the voter chooses among tabs, history entries, task-switcher cards, or first-contact title announcements, does the route carry a unique, current, task-legible identity that matches the actual official state now on screen?**

A route may pass the earlier controls and still fail `441` if:
- the URL is safe to keep but every saved tab still looks identical,
- the returned page is fresh but the tab title still names the old question or previous step,
- the simplified reading surface is fine while the browser chrome still labels the page as a generic landing shell,
- or the official banner/header on the page are correct but the title that users rely on to find the page again is too vague to distinguish it from neighboring official routes.

## Chrome-level identity is sometimes the entire way the voter finds the page again

Official voter-information routes are often revisited without re-reading the whole page.
The voter may choose a tab from a crowded browser strip, select a recent item from browser history, return through an app switcher, or rely on the title announced at first contact by assistive technology.

For this archive, that means the page title is not decorative SEO copy.
It is a public-surface label that often determines whether the voter returns to the right official answer lane at all.

## Task first, office context second, branding last

Federal website standards' current title guidance says the unique part of the page title should appear first and branding information such as site name, product, or agency should appear at the end. MDN's current `<title>` guidance likewise says important parts of the title should come earlier because text beyond ordinary display limits may be lost. (xref: `federal_website_standards_html_page_title_page`; xref: `mdn_title_element_page`)

For official voter-information routes, that implies a simple bounded posture:
- name the actual task or answer first,
- keep enough office or jurisdiction context to disambiguate the route,
- and let broad site branding trail rather than occupy the whole front of the title.

A title like “Check registration status — Example County Elections” is ordinarily safer than a title like “Example County Elections Portal” because the chrome-level choice point is usually about **which route this is**, not merely which government site owns it.

## The title should follow the effective route, not the outer shell

MDN's current `document.title` reference says scripts can set the current title of the document.
That makes title management a real implementation responsibility for single-page apps and lookup flows that change the effective route without a full document navigation. (xref: `mdn_document_title_property_page`)

For `441`, an office should review whether the title updates when:
- a generic landing shell turns into a specific lookup result,
- a multi-step route changes from data entry to review to confirmation,
- a status page changes from “pending” to “needs action” or another materially different state,
- or the application swaps between jurisdiction-specific or topic-specific subroutes without reloading the document.

What fails `441` is not “the site uses JavaScript.”
What fails `441` is letting the browser chrome keep advertising the wrong official state after the page has materially changed.

## Official identity cannot live only in the favicon or in-page header

USWDS's current banner guidance says the banner should identify the site as official and should appear on every page.
USWDS's current header guidance says the header helps users identify where they are. (xref: `uswds_banner_component_page`; xref: `uswds_header_component_page`)

That is complementary to `441`, not a substitute for it.
A banner and header help **once the page is open**.
The title helps the voter find the page **before reopening or re-reading it**.

So the bounded rule here is not “move all identity into the title.”
It is:
- keep on-page official identity visible,
- but do not assume the on-page header rescues a browser title that is too generic or stale to help the voter pick the right route in the first place.

## Title, heading, and breadcrumb should not fight one another

USWDS's current breadcrumb guidance says breadcrumb text should use the same wording as the page title. Federal website standards and MDN both say titles should be descriptive and purpose-bearing. (xref: `uswds_breadcrumb_component_page`; xref: `federal_website_standards_html_page_title_page`; xref: `mdn_title_element_page`)

For this archive, that means the page title, visible headline, and breadcrumb path do not need to be character-for-character identical.
But they should tell the same truth about:
- which official task or answer the page represents,
- which office or jurisdiction owns it,
- and whether the voter is on a landing page, a result page, a review step, or a confirmation state.

A route fails `441` when the visible page says one thing and the tab/history label says another, leaving the voter to choose among contradictory names for the same official state.

## Personalized or result pages need enough distinction without turning the title into a leak

A title can be highly useful without repeating every sensitive detail visible on the page.
For this archive, the safer bounded posture is to distinguish states and task lanes without stuffing the title with unnecessary personal data, long tokens, or brittle identifiers.

That means a route should prefer distinctions like:
- lookup result vs entry form,
- registration status vs ballot status,
- pending review vs submitted,
- county vs state office,
- or cure instructions vs ordinary FAQ,

rather than using the browser title as a dump of personal or secret-bearing state.

This is a control-family inference from the facts above plus the neighboring boundaries in `436` and `438`:
people choose tabs and history entries using visible chrome, so titles should help disambiguate official states without creating a new needless exposure surface.

## Must-distinguish states for chrome-level identity

For `441`, the title should stay distinct whenever the difference changes what the voter believes or does next.
That commonly includes distinctions like:
- landing page vs answer/result page,
- data-entry step vs review step vs confirmation step,
- current answer vs historical archive,
- general FAQ vs case-specific status,
- county office route vs state office route,
- and pending / needs action / completed outcome states when those meanings change the next step.

Not every page needs every distinction.
But when two routes carry materially different public meaning, the browser chrome should not flatten them into the same label.

## Preserve bounded evidence, not browser exhaust

The evidence posture here is about reconstructing whether chrome-level identity was reviewed and bounded.
The archive should preserve:
- which official routes were reviewed for page-title distinctness,
- the intended title pattern or title-state taxonomy,
- which route-state distinctions were required to stay visible in the title,
- whether client-side navigation updated the title,
- whether page title / heading / breadcrumb alignment was checked,
- and when the review last occurred.

It should **not** require preserving:
- named-user browsing histories,
- full browser-tab telemetry,
- per-user app-switcher traces,
- raw assistive-technology logs,
- or individualized title-capture exhaust when bounded policy reconstruction is sufficient.

## Canonical digest artifacts

Publish **small digests of browser-chrome identity posture**, not browsing histories.

- **Chrome Identity Surface Digest (CISD):** digest of the bounded page-title / browser-chrome identity policy for the official route.
- **Page Title Policy Digest (PTPD):** optional digest describing the current task-first title pattern and route-state taxonomy.
- **History Entry Disambiguation Digest (HEDD):** optional digest describing how materially different route states remain distinguishable in browser/history chrome.

## What belongs in the public browser-chrome identity payload

Keep the payload **small, route-aware, and title-focused**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `browser_chrome_identity_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_route_labels[]`
- `page_title_pattern_note`
- `task_first_labeling_note`
- `office_and_jurisdiction_context_note`
- `client_side_title_update_note`
- `title_heading_breadcrumb_alignment_note`
- `sensitive_title_data_minimization_note`
- `must_distinguish_states[]`
- `history_entry_disambiguation_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- named-user browsing histories,
- individualized tab snapshots,
- full browser history exports,
- copied assistive-technology traces,
- or secret-bearing route titles that expose more than the bounded policy requires.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Did the office review whether official voter-information routes are distinguishable by page title when viewed as browser tabs, history entries, or similar chrome-level labels?
- Does the title name the task or answer first and retain enough office/jurisdiction context to disambiguate the route?
- When client-side navigation changes the effective route or state, does the title change too?
- Are page title, heading, and breadcrumb aligned enough that a voter is not choosing among contradictory labels for the same official state?
- Did the office preserve bounded review evidence without retaining named-user browsing exhaust?

## How this fits the family map

Page titles, browser-tab identity, and history-entry disambiguation is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if an official voter-information route may be found again through browser or app chrome, the page title should stay unique, current, task-legible, and consistent enough with on-page official identity that the voter can choose the right route again without guesswork.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-browser-chrome-identity-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-browser-chrome-identity-surface-checklist.md`
