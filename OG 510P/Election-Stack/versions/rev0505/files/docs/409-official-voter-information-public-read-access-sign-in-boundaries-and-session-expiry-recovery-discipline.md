# 409 — Official voter-information public-read access, sign-in boundaries, and session-expiry recovery discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for the **public-read / account-boundary layer** around official voter-information websites:
whether current public-answer routes remain anonymously readable without authentication,
whether sign-in or account requirements are reserved for genuinely customized or private functions instead of becoming the default front door for general election information,
and whether session-expiry or re-authentication states preserve recoverable context and a visible help lane instead of collapsing the public route into a dead login shell.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help lane,
- `315`, which governs official account-identity and channel recognition,
- `374`, which governs site identity and trust cues,
- `375`, which governs official site-search surfaces,
- `391`, which governs crawlability, indexability, and canonical discovery,
- `405`, which governs anti-bot challenges and human-verification fail-open posture,
- `406`, which governs request-context variance and experiment boundaries,
- or `408`, which governs temporary overload, queue pages, and degraded-answer continuity.

It adds one narrow rule:
**if an election office expects voters, journalists, observers, or crawlers to rely on current official web pages for time-sensitive general answers, ordinary read-only public-answer routes should remain anonymously readable, sign-in should be reserved for genuinely customized or private functions, any authentication boundary should explain what private function it unlocks and preserve an ordinary no-auth help lane, and session-expiry / re-authentication states should preserve context rather than quietly replacing a current official answer with an account wall.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as a core responsibility for election officials and partners, and frames clarity, usability, accessibility, and accuracy as central design concerns for those materials. Digital.gov’s current digital-first and federal-website standards posture likewise emphasizes authoritative, effective, consistent public digital services. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `digital_gov_intro_federal_website_standards_page`)

Current access, search, and accessibility guidance is enough to justify a compact control here.
USWDS’s current **Sign-in form** guidance says sign-in is appropriate for customized or private content, says public content should remain accessible without sign-in where possible, and says automatic sign-out should provide adequate advance notice.
Google Search Central’s current technical requirements say Google can only index pages that are publicly accessible to Googlebot and not blocked from crawling.
Google Search Central’s current interstitial and page-experience guidance says intrusive dialogs or interstitials that obstruct the main content are poor user experience.
Section508.gov’s current accessible web design guide keeps non-interference and keyboard/alternate-access posture in play for the whole process, and W3C WAI’s current **Understanding Re-authenticating** says users should be able to continue an activity without losing data after re-authenticating when feasible. (xref: `uswds_sign_in_form_template_page`; xref: `google_search_central_technical_requirements_page`; xref: `google_search_central_avoid_intrusive_interstitials_page`; xref: `google_search_central_page_experience_page`; xref: `section508_guide_accessible_web_design_development_page`; xref: `w3c_wcag22_reauthenticating_page`)

That is enough to treat sign-in boundaries as a **public-answer integrity surface**.
A page can be current, indexed in principle, fast, JavaScript-resilient, cache-correct, challenge-free, and secure — yet still fail first contact because the visible experience is only a login prompt, expired-session notice, or account-creation wall where a public answer should have been.

## Public-read routes and customized/private routes are different classes

Election offices often operate both public-information routes and account-based workflows.
A voter dashboard, saved application, personalized notification preference center, or record-specific status tool may genuinely require authentication.
A deadline page, office/help page, polling-place explainer, or public notice page usually does not.

For this archive, the compact distinction is:
- general read-only answer pages are **public-read routes**,
- while record-specific, preference-specific, or draft-preserving workflows may be **auth-required routes**.

Those classes should not quietly inherit the same front door.
If a general public-answer route resolves to a sign-in shell by default, the office has turned identity plumbing into first-contact access control on public election information.

## Public answer pages should not quietly turn into sign-in prompts

USWDS’s current guidance is direct: public content should remain accessible without sign-in where possible, while sign-in is for customized or private content. (xref: `uswds_sign_in_form_template_page`)
Google Search Central’s technical requirements are equally blunt for discovery: if the office expects a page to be found through search, it must be publicly accessible to Googlebot rather than hidden behind login. (xref: `google_search_central_technical_requirements_page`)

For election information, that means the safe default is **not** “everything starts at the account wall.”
The bounded rule is:
- keep general read-only answers anonymously readable,
- classify the smaller set of genuinely private/customized routes separately,
- and do not let CMS, SSO, redesign, or vendor changes silently replace public-answer URLs with login prompts.

## If sign-in is required, explain what private function it unlocks and what remains public

Sometimes authentication really is the point.
A user-specific dashboard, a saved draft, or a personalized ballot-tracking preference center can be legitimately private.
That does **not** justify a generic account wall with no explanation.

For this archive, when an auth boundary is unavoidable, the public-facing surface should still tell the user:
- what private or customized function sign-in unlocks,
- what public information remains available without authentication,
- and how to reach the ordinary office/help lane without signing in.

That keeps the boundary honest.
It prevents “sign in to continue” from becoming a vague substitute for actual routing logic.

## Session expiry and re-authentication should preserve context rather than erase it

USWDS’s current sign-in guidance says automatic sign-out should provide adequate advance notice.
W3C WAI’s current re-authentication understanding material says a user should be able to continue an activity without data loss after re-authenticating when feasible. (xref: `uswds_sign_in_form_template_page`; xref: `w3c_wcag22_reauthenticating_page`)

That matters because many election flows are interrupted precisely when time pressure is highest.
A session timeout that dumps the voter at a blank sign-in screen may be merely annoying in a commerce app.
On a deadline-sensitive election workflow, it can destroy confidence, context, and recoverability.

For this archive, the compact rule is:
- give advance notice before timeout when feasible,
- preserve or restore the original task context when re-authentication is required,
- and do not let an expired-session shell silently replace a public-answer route that should have stayed public in the first place.

## Search and first-contact discovery should not land on account walls for public answers

Google Search Central’s technical requirements say Googlebot must be able to access the page, and pages behind login are not suitable as the main public discovery landing posture. (xref: `google_search_central_technical_requirements_page`)
Google’s interstitial guidance likewise reinforces that obstructive overlays or dialogs that prevent reaching the main content are a poor first-contact experience. (xref: `google_search_central_avoid_intrusive_interstitials_page`; xref: `google_search_central_page_experience_page`)

This archive does **not** claim every authenticated route must be crawlable.
It does say the office should know which routes are intended to be anonymous public landing pages and make sure those are the ones search, QR codes, emails, and other first-contact channels actually send people to.

## Keep authentication boundaries separate from anti-bot, variant, and overload posture

A sign-in wall is not the same thing as a CAPTCHA wall.
A session-expiry shell is not the same thing as hidden request-context variance.
An account prompt during overload is not the same thing as a temporary-unavailable holding page.

That is why this document stays separate from:
- `405`, which handles human-verification and WAF challenge posture,
- `406`, which handles cookie/geo/experiment-driven variant drift,
- and `408`, which handles temporary overload and queue/waitroom continuity.

The failure mode here is narrower:
**a public answer that should have remained anonymously readable instead resolved to a sign-in form, account wall, or expired-session shell.**

## Minimal state taxonomy

A compact policy can usually classify this surface with states such as:

- **critical_public_answer_routes_classified**
- **auth_required_routes_classified**
- **public_read_routes_do_not_require_sign_in**
- **auth_requirement_reason_visible**
- **public_help_lane_visible_without_auth**
- **session_timeout_warning_policy_defined**
- **reauthentication_context_preservation_defined_when_feasible**
- **public_routes_do_not_resolve_to_login_or_expired_session_shells**
- **crawler_visibility_for_public_read_routes_reviewed**
- **auth_boundary_review_current**

## Bounded reconstruction minimum

A public reconstruction should keep only enough detail to answer:

- which general official routes were classified as critical public-read answer pages,
- which routes were intentionally classified as auth-required,
- whether public-read routes remained anonymously readable,
- whether auth-required routes explained what private function they unlocked,
- whether the no-auth help/explanation lane stayed visible,
- whether timeout and re-authentication behavior warned users and preserved context when feasible,
- whether public answer routes avoided resolving to login or expired-session shells,
- whether crawler visibility for public-read routes was reviewed,
- and when the auth-boundary policy was last reviewed.

## Suggested payload fields

The payload for this surface can stay small.
Suggested fields include:

- `surface_id`
- `jurisdiction_id`
- `auth_boundary_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_public_answer_routes[]`
- `auth_required_route_classes[]`
- `public_read_boundary_note`
- `auth_requirement_reason_note`
- `anonymous_help_and_explanation_note`
- `session_timeout_and_warning_note`
- `reauthentication_context_preservation_note`
- `public_route_login_replacement_avoidance_note`
- `crawler_visibility_boundary_note`
- `feature_state_classes[]`
- `feature_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- optional `supersedes` / `superseded_by`

## Evidence to preserve

Preserve only what is needed to reconstruct policy:
- public-route and auth-route labels,
- public-vs-auth-required classification state,
- sign-in rationale state,
- anonymous help/explanation state,
- timeout and re-authentication policy state,
- public-route replacement-avoidance state,
- crawler-visibility boundary state,
- and review time.

Do **not** preserve credentials, auth tokens, session IDs, SSO traces, identity-provider traces, per-user login analytics, or raw authentication logs when bounded public-answer reconstruction is sufficient.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:

- Which current official routes were supposed to remain publicly readable without sign-in?
- Which routes were genuinely customized or private and intentionally auth-required?
- If sign-in was required, did the page explain what private function it unlocked?
- Could a user still reach the ordinary official help/contact lane without signing in?
- Did timeouts provide warning and preserve task context when re-authentication was required?
- Did a public-answer URL ever resolve to a login prompt or expired-session shell instead of the current official answer?
- Were crawler-visible public-read routes reviewed separately from private account routes?

## How this fits the family map

This is **not** a generic identity or SSO manual.
It is a bounded public-answer control.
Use it when an official voter-information page is current in principle, but first contact fails because the page resolved to a sign-in form, account wall, or expired-session shell.

The substantive voter question still lives in the ordinary surface families.
`409` only governs whether the current official answer remains publicly readable, honestly bounded when authentication is needed, and recoverable when sessions expire.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-public-read-access-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-public-read-access-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Digital.gov: requirements for delivering a digital-first public experience (xref: `digital_gov_requirements_digital_first_public_experience_page`)
- Digital.gov: introduction to federal website standards (xref: `digital_gov_intro_federal_website_standards_page`)
- USWDS: sign-in form guidance (xref: `uswds_sign_in_form_template_page`)
- Google Search Central: technical requirements (xref: `google_search_central_technical_requirements_page`)
- Google Search Central: avoid intrusive interstitials and dialogs (xref: `google_search_central_avoid_intrusive_interstitials_page`)
- Google Search Central: page experience (xref: `google_search_central_page_experience_page`)
- Section508.gov: guide to accessible web design and development (xref: `section508_guide_accessible_web_design_development_page`)
- W3C WAI: Understanding Re-authenticating (xref: `w3c_wcag22_reauthenticating_page`)
