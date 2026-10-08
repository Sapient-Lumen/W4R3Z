# 472 — Official voter-information installable web apps, home-screen launches, and standalone identity discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that may be installed or relaunched from the operating system as web apps rather than revisited only through an ordinary browser tab**:
install prompts,
Add-to-Home-Screen or Add-to-Dock flows,
manifest-defined launch identity,
standalone display modes that hide ordinary browser chrome,
home-screen or Dock icons that look like ordinary apps,
and launch-entry behavior such as `start_url`, `scope`, or other install-surface defaults that can make a voter feel as though the office published a standalone app-like authority.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `384`, which governs native mobile apps, app-store listings, and store/download boundaries,
- `404`, which governs cache freshness, service-worker updates, and stale-answer eviction,
- `414`, which governs in-app browsers, webviews, and constrained containers,
- `438`, which governs whether the current official URL itself is safe to bookmark, copy, or forward,
- `441`, which governs ordinary page-title and browser-tab identity,
- `471`, which governs office-offered copy/share controls,
- `475`, which governs browser-origin web push notifications after opt-in rather than the installed shell or launch identity itself,
- or `490`, which governs browser-managed Reading List items, offline saved pages, and archived page copies rather than an installed shell relaunched from the operating system.

It adds one narrow rule:
**if an election office expects voters to install or relaunch official voter information as a web app or home-screen shortcut, the installed shell should remain clearly subordinate to the current official page/help lane, preserve visible official identity even when ordinary browser UI is reduced, keep launch entry predictable and safe, and fail open when installability or standalone behavior varies across browsers and operating systems.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as a core election responsibility and emphasizes clarity, accessibility, usability, and accuracy. MDN’s current **Making PWAs installable** guidance says supporting browsers can promote a web app for installation, that once installed it gets an app icon on the device, and that it can be launched as a standalone app rather than as a normal website in a browser. MDN’s current **display** manifest reference says `standalone` opens in a separate window without typical browser UI such as the URL bar, and MDN’s current manifest-members reference says the display mode determines how much browser UI is shown when launched in an operating-system context. MDN’s current **scope** reference says pages within scope can stay in an app-like interface while navigation outside scope causes the browser to show UI such as the URL bar to indicate the change in context. MDN’s current **start_url** reference says the launch URL is only a browser hint, may fall back to the installation page, and may be ignored or modified by browsers or users. MDN’s current install-prompt guidance says `beforeinstallprompt` is non-standard and currently only implemented in Chromium-based browsers, and says install UI should stay hidden by default on browsers that cannot install locally. web.dev’s current installation guidance says that on iOS and iPadOS the install name is user-editable, bookmarks and PWAs look the same on the home screen, and only standalone display mode is supported there. Apple’s current iPhone support guidance says Safari can add a site to the Home Screen as a web app that then opens like an app, and Apple’s current Mac support guidance says Safari web apps can be added to the Dock and later have their application name, URL, icon, and navigation controls changed in settings. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `mdn_pwa_installable_guide_page`; xref: `mdn_web_app_manifest_display_member_page`; xref: `mdn_web_app_manifest_members_reference_page`; xref: `mdn_web_app_manifest_scope_member_page`; xref: `mdn_web_app_manifest_start_url_member_page`; xref: `mdn_pwa_trigger_install_prompt_page`; xref: `web_dev_pwa_installation_page`; xref: `apple_support_iphone_turn_website_into_web_app_page`; xref: `apple_support_mac_use_safari_web_apps_page`)

That is enough to treat installed web-app posture as a distinct public-answer surface rather than merely an implementation flourish.
A voter can be looking at the correct official site, yet the installed shell can still mislead by:
- hiding the ordinary URL bar or browser identity cues,
- launching into the wrong entry point for the current election,
- presenting an install affordance that does not exist on the current platform,
- or making the installed shell look more fixed, official, or self-contained than the office can actually guarantee.

## This is not the same thing as native apps, ordinary tabs, or embedded browsers

`384` asks whether a native app and its app-store listing stay recognizable, current, and recoverable.

`414` asks what happens when the voter is already trapped inside a constrained browser container before any install flow matters.

`441` asks whether ordinary browser-tab titles and history labels stay truthful during normal web navigation.

`472` asks a different question:
**when the voter installs or relaunches the official site as an app-like shell from the device itself, does that shell stay visibly subordinate to the current official web authority instead of impersonating a self-sufficient rulebook?**

A route may pass `384`, `414`, and `441` yet still fail `472` if:
- the home-screen or Dock shell hides origin cues the office assumed users would always see,
- the launch entry is stale, personalized, or otherwise not the safest public starting point,
- install UI is advertised as available when the current browser does not support it,
- or the installed shell’s name/icon/URL can drift away from the office’s intended identity while the page itself provides too little recovery context.

## An installed web app is a convenience shell, not a new authority source

MDN’s current PWA guidance says that once installed, the web app is launched from the operating system like other apps. That makes the installed shell powerful as a convenience layer, but not as a new legal or operational authority. (xref: `mdn_pwa_installable_guide_page`)

For this archive, the controlling artifact remains the current official page, notice, or office/help route.
The install shell MAY help the voter reopen that route faster.
It MUST NOT quietly become a new “official app” authority layer that outranks the current website, current superseding notice, or live office-help route.

So the bounded posture is simple:
- keep install/use optional,
- keep browser/open-on-web/help recovery visible,
- and do not let “installed” imply “frozen, complete, or independently authoritative.”

## Standalone mode reduces browser chrome, so visible official identity must move into the route itself

MDN’s current `display` guidance says `standalone` opens without typical browser UI elements like the URL bar. MDN’s manifest-members reference likewise says display mode determines how much browser UI is shown when the app is launched from the operating system. (xref: `mdn_web_app_manifest_display_member_page`; xref: `mdn_web_app_manifest_members_reference_page`)

That means the office cannot rely only on ordinary browser chrome to signal:
- which office or jurisdiction the voter is on,
- whether the route is still on the official site,
- or how to get back to the broader official help lane.

A bounded install posture should therefore keep enough **in-content** identity visible when launched in standalone mode, such as:
- office or jurisdiction name,
- a legible current route/task label,
- a visible help or official-site path,
- and an ordinary way to reopen or verify the route in the browser when needed.

This is not a demand to plaster the full URL everywhere.
It is a demand not to let the installed shell become visually source-ambiguous the moment the URL bar disappears.

## Launch entry should be safe, current, and unsurprising

MDN’s current `start_url` guidance says the launch URL is only a browser hint, can fall back to the page from which installation began, and may be ignored or later modified by browsers or users. Its current `scope` guidance says pages within scope stay app-like while navigation outside scope can cause the browser to show URL-bar UI to indicate the context change. (xref: `mdn_web_app_manifest_start_url_member_page`; xref: `mdn_web_app_manifest_scope_member_page`)

For this archive, that means an installable official route should review whether the likely launch entry is:
- a durable current-election landing page,
- a safe public router path,
- or another bounded entry that the office is willing to stand behind as the default reopen point.

It should be much more careful about letting the effective launch entry become:
- a stale prior-election page,
- a personalized or secret-bearing path,
- a brittle single-result state,
- or an installation-time deep link whose meaning changes too easily later.

The office does **not** control every browser’s exact install behavior.
It **does** control whether the official route is designed so the likely launch entry is safe and recoverable.

## Install prompts are optional and platform-specific, not guaranteed office powers

MDN’s current install-prompt guidance says `beforeinstallprompt` is non-standard, currently Chromium-only, and that install UI should stay hidden by default on browsers that cannot install locally. MDN’s PWA-installable guidance further says install UI and promotion vary by browser and platform. (xref: `mdn_pwa_trigger_install_prompt_page`; xref: `mdn_pwa_installable_guide_page`)

So an election office should not:
- promise that an install prompt will appear everywhere,
- require installation before the voter can reach the answer/help lane,
- or treat a custom install button as though it were a universal browser feature.

The safer posture is:
- keep install invitations truthful and optional,
- expose them only where support is actually present,
- and preserve the ordinary browser route when install support is absent or declined.

An install button that appears everywhere but works only on some platforms is not a minor product bug here.
It is a public-answer integrity failure because it teaches the voter to expect an official route that may not exist on the device in hand.

## Home-screen and Dock shells can drift from office-chosen identity

web.dev’s current installation guidance says iOS/iPadOS install names are user-editable and that bookmarks and PWAs look the same on the home screen. Apple’s current Mac support guidance goes further: a Safari web app’s application name, URL, icon, and navigation controls can all be changed in settings after creation. (xref: `web_dev_pwa_installation_page`; xref: `apple_support_mac_use_safari_web_apps_page`)

That matters because the office may think it published one neat official shell, while the user’s device may later display:
- a renamed app,
- a custom icon,
- a changed launch URL,
- or a shell with fewer navigation controls than the office expected.

So the archive should treat the operating-system shell as a **convenience wrapper**, not as the whole identity proof.
The real identity proof still needs to survive inside the current route through visible office/jurisdiction cues and a recoverable official-site/help path.

## Some browsers can install sites as apps even without the office’s intended manifest posture

MDN’s current installable-PWA guidance says Chrome for desktop/Android, Safari for desktop, and Edge for desktop can let users install a site as an app even without a manifest file and without meeting ordinary installability criteria. (xref: `mdn_pwa_installable_guide_page`)

That is a useful caution:
not every installed election-information shell on a device proves that the office explicitly designed or endorsed a full app-like experience.
Sometimes the browser simply wrapped the site.

For this archive, that means the office should not overclaim:
- “download our app” when the reality is “install this website if your browser supports it,”
- or “the app guarantees the current official answer” when the installed wrapper may just be another way of reopening the website.

The public posture should describe what the office truly supports.

## Out-of-scope and browser-reveal transitions should fail open rather than look like a break-in reality

MDN’s current `scope` guidance says that when users navigate outside scope, browsers can show the URL bar to indicate the change in context. (xref: `mdn_web_app_manifest_scope_member_page`)

That is helpful, but only if the route stays understandable.
An installed election-information shell should therefore avoid making out-of-scope transitions feel like mysterious app failures.
If a voter leaves the app-like region to:
- view a different official host,
- open a help page,
- reach a file or handler,
- or recover from a stale launch path,

the route should preserve enough continuity that the voter understands they are still being routed through official recovery rather than being dropped into a suspicious or broken state.

## Keep install/use telemetry bounded and do not let launch markers become hidden identifiers

MDN’s current `start_url` guidance warns against encoding unique identifiers in launch URLs and notes privacy concerns around tracking launch source through parameters. (xref: `mdn_web_app_manifest_start_url_member_page`)

That matters here because install/reopen posture can become a tempting analytics surface.
The bounded rule for this archive is small:
- preserve policy-level review evidence about install support, launch entry, visible identity, and recovery posture,
- but avoid individualized install telemetry, persistent launch identifiers, or per-user start-URL markers when bounded public reconstruction is enough.

## Minimal state taxonomy

A compact policy can usually classify this surface with states such as:

- **install_shell_offered_as_optional_convenience**
- **standalone_identity_cues_reviewed**
- **browser_open_recovery_present**
- **launch_entry_is_safe_public_route**
- **start_url_scope_boundary_reviewed**
- **install_prompt_truthful_for_current_platforms**
- **unsupported_install_fails_open_to_browser_route**
- **user_editable_shell_identity_boundary_disclosed**
- **launch_tracking_identifiers_avoided**
- **installed_shell_not_treated_as_standalone_rulebook**

## Bounded installed-shell trace minimum

A public, bounded reconstruction should keep only enough detail to answer:
- whether the office intentionally supports installable web-app use for the reviewed routes,
- which install surfaces were reviewed (browser prompt, home screen, dock, etc.),
- what launch entry or `start_url` posture was intended,
- whether visible in-route official identity survives standalone launch,
- whether browser/open-on-web/help recovery exists,
- whether unsupported install flows fail open,
- whether user-editable shell drift was accounted for,
- and when the posture was last reviewed.

That is enough to reconstruct whether installed web-app use was treated as a bounded public-answer control.
It is not a reason to preserve per-user install logs or individualized launch histories.

## Minimal claim-set

A jurisdiction can publish a compact, verifiable claim-set:

1. **Optional-install claim:** installed web-app use is a convenience layer, not a prerequisite for reaching the official answer/help lane.
2. **Standalone-identity claim:** when ordinary browser chrome is reduced, the route still exposes enough visible official identity and recovery context to remain source-legible.
3. **Launch-entry claim:** the likely installed launch entry is a safe public route rather than a stale, secret-bearing, or overly brittle path.
4. **Install-prompt truthfulness claim:** install invitations reflect real platform support instead of pretending that a Chromium-only or platform-specific capability is universal.
5. **Shell-drift boundary claim:** the office accounts for the fact that names, icons, URLs, or controls may differ on user devices and does not treat the operating-system shell alone as proof of authority.
6. **Privacy-boundedness claim:** install/launch posture is reconstructed from bounded policy evidence rather than individualized install telemetry or hidden launch identifiers.

## Canonical digest artifacts

Publish **digests of install posture**, not raw device analytics.

- **Installed Web App Surface Digest (IWASD):** digest of the bounded install/launch posture for an official route family.
- **Standalone Identity Posture Digest (SIPD):** optional digest proving that standalone launches keep enough visible official identity and recovery context.
- **Launch Entry Boundary Digest (LEBD):** optional digest proving safe launch-entry, `start_url`, and scope-boundary posture.

## What belongs in the public payload

Keep the payload **small, launch-aware, and browser-humble**.

Recommended top-level fields:

- stable `surface_id`
- `jurisdiction_id`
- `installed_web_app_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `manifest_uri`
- `reviewed_install_surfaces[]`
- `install_optional_note`
- `visible_official_identity_note`
- `standalone_identity_note`
- `start_url_scope_boundary_note`
- `launch_entry_safety_note`
- `install_prompt_truthfulness_note`
- `unsupported_install_fallback_note`
- `open_in_browser_or_help_note`
- `user_editable_shell_boundary_note`
- `privacy_boundary_note`
- `last_verified_at`
- optional `supersedes` / `superseded_by`

Do **not** publish by default:
- individualized install counts tied to people,
- per-device launch histories,
- user-specific start URLs,
- hidden launch-marker parameters,
- or raw OS telemetry that is not needed to reconstruct the bounded public posture.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:

- Did the office treat installed web-app use as optional convenience rather than the only way to reach current official information?
- When the route launches in standalone mode, is the office/jurisdiction identity still visible without relying only on the missing URL bar?
- Is the likely launch entry a safe public route for the current election and task?
- Does the office avoid promising install behavior that is unavailable on the current browser or platform?
- If the installed shell’s name/icon/URL drifts on the device, does the route still provide enough official recovery context to re-anchor trust?
- Did the office preserve bounded policy evidence without turning install/use into individualized surveillance?

## How this fits the family map

Installable web apps, home-screen launches, and standalone identity is **not** a new underlying voter-question family bucket.
It is a delivery-shell control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if an office expects voters to install or relaunch official voter information as a web app, the installed shell should stay humble, source-legible, and recoverable instead of quietly impersonating a separate authoritative application.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-installed-web-app-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-installed-web-app-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- MDN: Making PWAs installable (xref: `mdn_pwa_installable_guide_page`)
- MDN: `display` manifest member (xref: `mdn_web_app_manifest_display_member_page`)
- MDN: Web app manifest members reference (xref: `mdn_web_app_manifest_members_reference_page`)
- MDN: `scope` manifest member (xref: `mdn_web_app_manifest_scope_member_page`)
- MDN: `start_url` manifest member (xref: `mdn_web_app_manifest_start_url_member_page`)
- MDN: Trigger installation from your PWA (xref: `mdn_pwa_trigger_install_prompt_page`)
- web.dev: Installation (xref: `web_dev_pwa_installation_page`)
- Apple Support: Turn a website into an app in Safari on iPhone (xref: `apple_support_iphone_turn_website_into_web_app_page`)
- Apple Support: Use Safari web apps on Mac (xref: `apple_support_mac_use_safari_web_apps_page`)
