# 438 — Official voter-information bookmarking, shared-link revisit continuity, and share-safe URL discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes where the office reasonably expects a voter, helper, journalist, observer, or later reviewer to bookmark, copy, text, email, forward, or revisit the current URL itself**:
status lookups,
submission-confirmation pages,
polling-place or hours answers,
appointment details,
case or cure status pages,
FAQ/help answers that offices explicitly tell the public to save or share,
and similar official routes where the page can be current and understandable on-screen yet still fail the public because the URL is not safe or durable enough to revisit, forward, or keep as part of the public record.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help lane,
- `379`, which governs redirects, expired pages, and stale-link recovery once a URL has already moved or aged out,
- `381`, which governs QR codes, short URLs, and printed-to-digital handoff posture,
- `388`, which governs shared-link previews and unfurls,
- `409`, which governs sign-in boundaries and session-expiry recovery,
- `429`, which governs multi-step state-preservation through staged flows,
- `430`, which governs whether a submission confirmation provides a reference-bearing record worth keeping,
- `436`, which governs shared-device exit and local-data clearing,
- or `437`, which governs whether a kept record remains faithful once it leaves the live page.

It adds one narrow rule:
**if an official voter-information route expects people to keep, copy, forward, bookmark, or later revisit the URL itself, the office should keep that URL share-safe enough that a later arrival reaches an equivalent current route or an explicit safe recovery path without leaking secrets, personal data, or one-browser-only hidden state into the link.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes clarity, accessibility, usability, hierarchy, and structure. Digital.gov’s current digital-first public-experience requirements say public digital services should be accessible, authoritative, secure by design/default, user-centered, discoverable, and mobile-first. USWDS’s current **Keep a record** guidance says successful public-service flows should provide a record that includes site name, URL, date, next steps, and reference numbers when possible. Digital.gov’s current plain-language guidance on **Links** and **Special cases** says links are part of navigation and content, should tell users exactly where they will go, and should be explicit about what the destination is. MDN’s current **Working with the History API** guide says modern web apps often update page content without full reloads and use `pushState()` / `replaceState()` to keep browser history entries aligned with current state. OWASP’s current **Information exposure through query strings in URL** page says sensitive data in URL parameters can leak through browser history, logs, caches, referrers, and shared systems, and that HTTPS alone does not solve the exposure. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `uswds_keep_a_record_page`; xref: `digital_gov_plain_language_links_page`; xref: `digital_gov_plain_language_special_cases_page`; xref: `mdn_working_with_history_api_page`; xref: `owasp_information_exposure_query_strings_page`)

That is enough to justify a compact control here.
A route can be current, printable, and even pass `379`, `430`, and `437`, yet still fail first contact because:
- the copied URL only works in the original browser tab,
- a helper who opens the shared link lands on a generic home page or start-over shell instead of the referenced answer,
- the URL carries a token, birth date, email, or other sensitive value that should never have become part of a shareable link,
- the visible answer changed in a single-page app but the browser URL never changed with it,
- the route tells the voter to keep or share the page but the kept URL points only to a session-bound waiting room,
- or the office expects bookmark/revisit behavior but provides no safe reference number or first-party recovery path when a fully share-safe URL is impossible.

## This is not the same thing as stale-link recovery, portable records, or confirmation existence

`379` asks whether old, moved, or expired URLs recover safely once they have already gone stale.

`430` asks whether a submission/result route gives the voter a record worth keeping.

`437` asks whether the kept record remains faithful when printed, saved to PDF, screenshotted, or otherwise carried out of the page.

`438` asks a different question:
**while the route is still current, can the user safely keep or forward the URL itself and later reach an equivalent current path without exposing secrets or depending on hidden browser state that nobody else can reconstruct?**

A route may pass `379`, `430`, and `437` and still fail `438` if:
- the print/PDF record is fine but the copied URL contains a one-time token,
- the confirmation page shows the right answer but its visible URL is only a transient session endpoint,
- the page can be revisited only inside the same tab because the app never reflected the current state into history,
- or a helper receives the shared link and lands on a login wall or generic dashboard with no safe path back to the referenced answer.

## If the office expects sharing or revisiting, the URL must be treated as part of the public record

USWDS’s current **Keep a record** guidance is unusually direct here: the kept record should include the site name, URL, date, and next-step/reference information when possible. (xref: `uswds_keep_a_record_page`)

For this archive, that means a route should decide whether an ordinary user is likely to:
- bookmark the page,
- copy the URL into notes,
- text or email the current answer to a helper,
- reopen the route later from browser history,
- or rely on the URL as part of the kept record alongside a case number or date.

If yes, the route needs a bounded share/revisit review.
The rule is not “every page must be publicly shareable.”
It is “do not imply that the URL is a usable record or helper handoff if revisiting it will quietly fail or leak sensitive state.”

## Share-safe URLs and session-only URLs are different classes

This archive should not flatten all current URLs into one bucket.
At least four materially different states matter here:

1. **Public share-safe URL** — the current official URL can be copied, bookmarked, or forwarded and later reopens the same current answer lane or an equivalent current wrapper.
2. **Personalized but revisit-safe URL** — the current URL can be revisited by the same authenticated user, but it is not suitable for forwarding because the destination is account- or case-specific.
3. **Session-bound or hidden-state URL** — the visible URL does not carry enough route meaning to reopen the same state outside the original browser/session context.
4. **Sensitive-in-URL failure state** — the visible URL exposes tokens, personal identifiers, or other values that should not be treated as a shareable record at all.

Those states are not the same problem.
A route may be legitimately personalized without being safe to forward.
A route may be safe to revisit by the same voter while still needing a different helper handoff.
And a route that puts secrets or PII into the URL has crossed from “inconvenient” into a real security/privacy failure. (xref: `owasp_information_exposure_query_strings_page`)

## Modern app state must not make the browser URL lie

MDN’s current History API guidance says many web apps update content without full page loads and use browser-history state to keep navigation coherent. (xref: `mdn_working_with_history_api_page`)

That matters here because an official route can look correct on-screen while the URL is stale, generic, or meaningless.
For `438`, if the page changes the controlling result, step, or answer state in a way the office expects a voter to revisit later, the route should review whether:
- the browser history entry changed with the answer state when appropriate,
- Back/Forward return to meaningful prior states instead of breaking the route,
- copy-link or share actions preserve the intended route rather than a generic launcher URL,
- and the visible URL is not merely an implementation artifact from a single-page shell.

The archive does **not** require every state transition to become a deep link.
It does require that the office not mistake hidden in-memory state for a shareable or bookmarkable public answer lane.

## Do not put secrets or personal data in shareable URLs

OWASP’s current query-string exposure guidance is a clean boundary here: sensitive data in URL parameters can leak through browser history, logs, caches, referrers, and shared systems, and HTTPS alone does not prevent that exposure. (xref: `owasp_information_exposure_query_strings_page`)

For `438`, that means official routes should avoid treating the URL as a convenient transport for:
- one-time auth or case-access tokens,
- birth dates, personal email addresses, phone numbers, or full identifiers,
- hidden status-query secrets,
- or other values the office would not want copied into a chat, screenshot, referrer log, or browser history.

If a route must remain personalized or secret-bearing, the office should say so clearly enough that the voter does not mistake that URL for a safe helper handoff.
In those cases the route should prefer:
- a safe reference number,
- a first-party re-entry path,
- a signed-in revisit path with clear expectations,
- or the authoritative help lane.

## Link meaning still matters when the URL is the artifact

Digital.gov’s current plain-language guidance says links should tell users exactly where they will go and should be explicit. USWDS’s current link guidance says a link connects users to another page or further information. (xref: `digital_gov_plain_language_special_cases_page`; xref: `digital_gov_plain_language_links_page`; xref: `uswds_link_component_page`)

That implies a bounded rule here:
if the office offers “Copy link,” “Share,” “Bookmark this page,” or equivalent instructions, the surrounding language should make clear whether the URL is:
- safe to share broadly,
- safe only for the same voter/account,
- merely a current-page convenience,
- or not a reliable record and therefore subordinate to a reference number or printable record.

A voter should not have to guess whether “Save this page” means “keep the URL,” “keep the case number,” “print the summary,” or “re-enter through your account later.”

## When fully share-safe linking is impossible, provide a bounded substitute

Some official routes are inherently personalized.
A ballot-status page, registration dashboard, or case-specific cure portal may never be safely forwardable as a public link.
That is fine.
What fails `438` is not privacy-preserving scoping.
What fails `438` is leaving the voter with no bounded alternative once the office has implied that the URL itself is worth keeping.

For this archive, good substitutes include:
- a reference number that is explicitly meant for later follow-up,
- a kept record whose printed/saved output names the first-party re-entry route,
- a stable signed-in landing path that reopens the case after re-authentication,
- or a help/contact lane that the office explicitly says controls later recovery.

This is how `438` stays distinct from `430` and `437`:
when the URL cannot safely do the job, the office should say what artifact or path does.

## Preserve bounded evidence, not raw shared-link telemetry

The evidence posture here is about reconstructing whether a route treated the URL as a safe/durable artifact.
The archive should preserve:
- which routes were expected to support bookmark/share/revisit behavior,
- whether the route was classified as public-share-safe, same-user revisit-safe, or non-shareable,
- whether visible URL/history state tracked the controlling answer state,
- whether sensitive parameters were prohibited,
- what substitute artifact/path controlled when the URL was not safely forwardable,
- and when the review last occurred.

It should **not** require preserving:
- raw copied URLs containing personal state,
- chat logs or emails where voters forwarded links,
- browser-history exports,
- referrer logs tied to named voters,
- or individualized sharing analytics when bounded policy reconstruction is sufficient.

## Canonical digest artifacts

Publish **small digests of share/revisit policy**, not raw shared URLs.

- **Share-Safe Link Surface Digest (SLSD):** digest of the bounded share/revisit policy payload for the official route.
- **Sensitive URL Parameter Policy Digest (SUPD):** optional digest describing which parameter classes are forbidden in shareable links and which routes must remain non-shareable.
- **Revisit Recovery Relationship Digest (RRRD):** optional digest describing the substitute record/reference/help path when a fully share-safe URL is impossible.

## What belongs in the public share/revisit payload

Keep the payload **small, route-aware, and URL-safety focused**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `share_safe_link_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_revisit_routes[]`
- `share_safe_url_required_note`
- `revisit_state_classes[]`
- `history_state_alignment_note`
- `sensitive_parameter_policy_note`
- `session_bound_url_policy_note`
- `safe_record_or_reference_fallback_note`
- `share_forwarding_note`
- `help_route_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- raw current URLs for personalized routes,
- secret-bearing query strings,
- copied links from real voter sessions,
- forwarding telemetry,
- or browser-history traces.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- If the office expected people to keep or share the current URL, was that URL actually safe and durable enough to revisit?
- Did the route distinguish public-share-safe, same-user-only, and non-shareable/personalized link states?
- Did visible URL/history state stay aligned with the controlling answer state in routes that changed content dynamically?
- Did the office avoid putting secrets or personal data into URLs the public was likely to copy or forward?
- When the URL could not safely do the job, did the route name a bounded substitute such as a reference number, signed-in re-entry path, printable record, or authoritative help lane?
- Did the archive preserve bounded policy evidence without collecting raw copied-link telemetry from real users?

## How this fits the family map

Share-safe URL and revisit continuity is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if a jurisdiction expects a voter to keep or pass along the current URL, that URL should not dissolve into hidden app state, generic restarts, or secret-bearing query strings the moment it leaves the original browser context.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-share-safe-link-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-share-safe-link-surface-checklist.md`
