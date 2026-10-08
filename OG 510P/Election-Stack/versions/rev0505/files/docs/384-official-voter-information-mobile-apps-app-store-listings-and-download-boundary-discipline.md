# 384 — Official voter-information mobile apps, app-store listings, and download-boundary discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information mobile-app surfaces**:
app-store listing cards,
app names and subtitles,
developer names,
store-page contact and website cues,
privacy and data-safety disclosures,
accessibility labels,
listing screenshots and short descriptions where they materially shape public expectations,
download / install handoff,
and similar first-contact surfaces that many voters may treat as official before they ever reach the ordinary website.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `203`, which governs official channel directories,
- `305`, which governs the authoritative office/help route,
- `378`, which governs file-delivery and viewer handoffs,
- `381`, which governs QR / shortlink printed-to-digital handoffs,
- `382`, which governs general-web-search result presentation,
- or `383`, which governs persistent social-profile shells and bio-link handoffs.

It adds one narrow rule:
**if an election office publishes, endorses, or meaningfully routes voters toward a mobile app, the app-store and install-handoff layer should make the official publisher legible, keep official website/help recovery visible, keep privacy/accessibility disclosures current, and remain recoverable when a version, listing, or platform channel drifts stale.**

## Why this is a distinct surface

Current official and primary technical guidance is enough to justify a bounded control here.

Digital.gov's current **Delivering a digital-first public experience** guidance says public digital services must be mobile-friendly and explicitly says agencies should avoid building or maintaining unnecessary mobile apps.
Digital.gov's current **Connected Government Act** resource points to the U.S. Digital Registry as the resource to confirm the official status of public-facing mobile apps and mobile websites.
ADA.gov's current **Fact Sheet: New Rule on the Accessibility of Web Content and Mobile Apps Provided by State and Local Governments** says the Title II final rule has specific requirements for making state and local government mobile apps accessible.
EAC's current **Clearinghouse Resources on Accessibility** page keeps web and mobile content accessibility inside the live election-official accessibility lane.
EAC's current **DCo Votes app** Clearinghouse award page shows that at least some election offices now put essential election information into iOS/Android apps rather than only webpages.
Apple's current App Store Connect guidance says developer names appear on App Store product pages, privacy answers update the product page, and accessibility nutrition labels help users learn whether they can use the app before download.
Google Play's current developer guidance says the developer name and store-listing contact details appear on the store listing, the title/icon/developer name help users understand the app, and the Data safety section is shown before install.
That is enough to treat the app-store / download layer as a real voter-information surface rather than an implementation detail. (xref: `digital_gov_delivering_digital_first_public_experience_page`; xref: `digital_gov_connected_government_act_page`; xref: `ada_gov_web_mobile_apps_fact_sheet_page`; xref: `eac_clearinghouse_resources_accessibility_page`; xref: `eac_dco_votes_app_clearinghouse_award_page`; xref: `apple_app_store_connect_set_developer_name_page`; xref: `apple_app_store_connect_manage_app_privacy_page`; xref: `apple_app_store_connect_accessibility_nutrition_labels_page`; xref: `google_play_developer_account_information_page`; xref: `google_play_store_listing_best_practices_page`; xref: `google_play_data_safety_section_page`)

For some voters, the first “official” thing they decide to trust is not the website.
It is the App Store / Google Play card, the developer name, the privacy/disclosure panel, the install target, or the first app-open cue.
A stale listing, ambiguous publisher name, wrong bio website, or detached app for an old election can quietly misroute people before the canonical page is even opened.

## A mobile app is an optional routing layer, not the rule source

A voter-information app MAY help people reach current official information quickly.
It MUST NOT become a hidden authority layer that silently outranks the current official webpage, notice, hotline, office/help route, or superseding recovery page.

The controlling artifact remains the current official destination the jurisdiction stands behind.
The app layer should only do enough to:
- make the official publisher and jurisdiction recognizable,
- route people into the current official website/help lane when the app itself is stale, unavailable, or too narrow,
- keep store-facing disclosure surfaces current enough that users are not surprised by identity, privacy, or accessibility reality after install,
- and remain reconstructible later without turning routine app use into individualized surveillance.

## The app must earn its existence

Digital.gov's current digital-first guidance is explicit that agencies should avoid building or maintaining unnecessary mobile apps and should first ensure that public digital services are mobile-friendly. (xref: `digital_gov_delivering_digital_first_public_experience_page`)

That matters here because not every voter-information need justifies an app.
A bounded app policy should therefore begin with a simple discipline:
- if a mobile-friendly official website solves the problem clearly, prefer that;
- if the app exists, state what public function it performs that the ordinary site, notification feed, or saved-home-screen path does not;
- and if the app no longer earns its maintenance burden, retire it cleanly with explicit website/help recovery instead of leaving a zombie listing behind.

This keeps the archive from quietly normalizing “there is an app” as an integrity improvement by itself.
Sometimes it is.
Sometimes it is just another stale shell to maintain.

## The first trust decision often happens on the store listing

Apple's current guidance says the developer name appears under the app name on App Store product pages and displays when users install the app.
Google Play's current guidance says the developer name plus store-listing contact details appear on the store listing, and its listing best-practices page says the title, icon, and developer name are particularly helpful for users trying to find and understand the app. (xref: `apple_app_store_connect_set_developer_name_page`; xref: `google_play_developer_account_information_page`; xref: `google_play_store_listing_best_practices_page`)

So the archive should treat at least four listing-level identity cues as controlled surfaces:
1. **App name / subtitle state** — whether the title actually signals the office, jurisdiction, and general function.
2. **Developer identity state** — whether the publisher name reads like the expected official office or organization.
3. **Store contact / website state** — whether the website, email, or support contact points back to current official help.
4. **Listing visual identity state** — iconography/screenshots that materially affect official-source recognition.

The goal is not app-store optimization theater.
The goal is that a voter can tell whether the listing plausibly belongs to the official election office before installing it.

## Official-domain and help-lane recovery should remain visible

Digital.gov's U.S. Digital Registry posture and the broader `.gov` trust guidance support a simple recovery floor: a public-facing government app should stay tied back to recognizable official domains and channels rather than floating as a detached vendor object. (xref: `digital_gov_connected_government_act_page`; xref: `digital_gov_requirements_registration_use_gov_domains_page`; xref: `vote_gov_home_page`)

So a bounded app surface should usually keep visible:
- the current official website or office/help destination,
- current support contact,
- and a recovery path that still works if the app cannot be installed, the store listing is delayed, or the app has been retired.

If an app listing points only to a generic contractor site, expired microsite, or dead-end marketing page, the app surface is already drifting away from the authoritative lane.

## Privacy and data-safety disclosures are part of the public answer surface

Apple's current App Store Connect privacy guidance says apps distributed on the App Store must explain data handling practices, that these responses update the product page, that a privacy-policy URL is required for apps, and that developers are responsible for keeping responses accurate and up to date.
Google Play's current Data safety guidance says the Data safety section appears on the store listing before download, developers must provide complete and accurate declarations, a privacy policy is required even for apps that collect no user data, and the section should be updated when data practices change. (xref: `apple_app_store_connect_manage_app_privacy_page`; xref: `google_play_data_safety_section_page`)

That makes store privacy/disclosure metadata part of the voter-information trust surface.
It is not enough to say “the app is official.”
A voter should also not be surprised about basic data practices after installation.

For election information, the practical rule is small:
- disclose the real data practices of the released app version,
- keep privacy-policy and disclosure links current,
- do not let a store label imply less collection than the shipping app actually performs,
- and keep the ordinary website/help route available for people who do not want the app permissions or install path.

## Accessibility claims belong before download, not only after complaint

ADA.gov's current rulemaking materials make clear that state and local government mobile apps must be accessible.
EAC's current accessibility clearinghouse explicitly keeps web and mobile election information in the accessibility lane.
Apple's current accessibility-nutrition-label guidance says users can learn from the product page whether features such as VoiceOver or Larger Text are supported before download. (xref: `ada_gov_web_mobile_apps_fact_sheet_page`; xref: `eac_clearinghouse_resources_accessibility_page`; xref: `apple_app_store_connect_accessibility_nutrition_labels_page`)

That supports a bounded rule:
- accessibility claims for the app should not live only in a buried policy PDF or post-launch apology,
- store-facing accessibility disclosures and ordinary help text should not overclaim,
- and the website/help fallback should remain usable for people who cannot or do not wish to use the app.

The point is not to force every jurisdiction into a native-app strategy.
It is to ensure that, when an app exists, accessibility is visible early enough to matter.

## Version drift, election-scope drift, and stale-listing recovery

Apple and Google both treat store metadata as updateable, reviewable, and user-visible.
Apple says localized app information can be edited and may take time to appear.
Google says Data safety responses and developer-facing store details must stay accurate and current. (xref: `apple_app_store_connect_view_and_edit_app_information_page`; xref: `google_play_data_safety_section_page`; xref: `google_play_developer_account_information_page`)

That is enough to justify a bounded stale-state rule:
- do not leave an app marketed as the current official election guide if it is scoped to a past election,
- do not let store screenshots, descriptions, or keywords imply current statewide coverage when the shipping build only covers a narrower or older scope,
- and when an app is retired, unavailable, or no longer authoritative, provide visible website/help recovery rather than silent abandonment.

A stale listing is not only a product problem.
For voter information, it can become a quiet routing failure.

## Minimal app-state taxonomy

A small taxonomy is enough:

1. **Current official voter-information app with current official website/help recovery** — listing, developer identity, privacy metadata, and support route all point to current official channels.
2. **Current official app with limited scope clearly stated** — for example, a county-specific or election-worker-adjacent app whose scope is explicit and whose public listing does not overclaim.
3. **Legacy or deprecated app listing with successor recovery** — an older listing remains visible but clearly routes to the current website or replacement app.
4. **Temporarily unavailable or unsupported app with official fallback** — the store listing or official channel explains the status and routes people back to the canonical help lane.
5. **Uncertain / imitative / no-longer-official listing** — the office cannot currently attest that the listing is official or current, so public guidance routes users to the office/help lane instead of asking them to trust the app.

## Preserve bounded reconstruction, not app analytics exhaust

This archive should not treat app analytics as the public proof object.
What matters here is bounded reconstruction of the public-facing trust and routing layer.

Prefer **listing snapshots, version-to-scope mappings, developer-identity state, privacy/disclosure snapshots, accessibility-claim state, and official recovery links** over installation telemetry, per-user session logs, or ad-tech traces.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Official app claim:** one or more named app listings are official public voter-information app surfaces for scope `E`.
2. **Necessity / role claim:** the app serves a bounded public function beyond a merely mobile-friendly webpage, or else the office prefers the web path.
3. **Publisher-legibility claim:** app/store identity cues make the official publisher and jurisdiction recognizable.
4. **Disclosure claim:** privacy, data-safety, and accessibility store disclosures are materially current for the released version.
5. **Recovery claim:** the listing and app route users to current official website/help fallback when ordinary in-app use fails or the app is stale.
6. **Transition claim:** deprecated, replaced, or unsupported app listings have visible successor or website recovery.
7. **Trace-minimization claim:** bounded reconstruction is possible without individualized usage surveillance.

## Canonical digest artifacts

Publish **small digests of the app surface**, not full mobile-analytics exports.

- **Mobile App Surface Digest (MASD):** digest of the bounded mobile-app surface payload for a scope.
- **App Listing Metadata Digest (ALMD):** digest of store-visible name, developer identity, website/support, and scope state at time `T`.
- **App Disclosure Snapshot Digest (ADSD):** digest of privacy / data-safety / accessibility disclosure posture for a released version.
- **App Transition Digest (ATD):** digest of deprecation, replacement-app, or website-fallback transitions.

## What belongs in the public mobile-app payload

Keep the payload **small, publisher-legible, current-state-aware, and recovery-capable**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `mobile_app_surface_label`
- `official_app_listings[]`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `app_necessity_policy_note`
- `listing_identity_policy_note`
- `store_metadata_policy_note`
- `app_store_privacy_policy_note`
- `app_store_accessibility_policy_note`
- `deep_link_policy_note`
- `version_recovery_policy_note`
- `mobile_app_state_classes[]`
- `mobile_app_trace_policy`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `rights_escalation_uri`
- `latest_notice_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- individualized install or session logs,
- device identifiers,
- ad IDs,
- fine-grained permission histories tied to named people,
- or behavioral-profiling exports.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Which app listings were official at time `T`?
- Did the listing make the official publisher recognizable before install?
- Where did the listing route for website/help/privacy recovery?
- Were privacy/data-safety/accessibility disclosures materially current for the released version?
- Was the app clearly scoped as current, limited, deprecated, or replaced?
- Could a third party reconstruct the bounded app surface without individualized usage surveillance?

## How this fits the family map

A voter-information app is **not** a new canonical voter-question family bucket.
It is a packaging and routing shell that may sit around many different voter-help topics.

So the underlying question remains:
- which office is authoritative,
- which website or help lane is current,
- which notice, form, FAQ, or directory actually controls,
- or where the voter should escalate when ordinary self-service fails.

This document only says that, if an office expects the public to encounter an app-store listing or official mobile app as part of the voter-information path, the listing/install/disclosure layer should remain clearly official, current-routing, privacy-plain, accessibility-aware, stale-recoverable, and later reconstructible instead of acting as an orphaned or ambiguous authority shell.
