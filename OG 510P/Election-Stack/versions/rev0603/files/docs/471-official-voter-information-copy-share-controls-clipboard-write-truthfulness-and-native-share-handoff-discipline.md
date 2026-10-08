# 471. Official voter-information copy/share controls, clipboard-write truthfulness, and native-share handoff discipline

**Track:** Shared

This document defines a bounded control for **official voter-information routes that expose “Copy”, “Share”, “Copy link”, “Share this page”, “Share details”, “Copy office contact”, or similar handoff controls** where:

- the official answer is already on the right route,
- but the handoff control makes it unclear **what artifact will actually leave the page**,
- a “Copied” or “Shared” confirmation can appear even though the browser or operating system did not complete the handoff,
- the copied/shared artifact can omit the date, jurisdiction, office, or recovery path needed to keep the answer trustworthy off-page,
- or the route offers copy/share controls on URLs or snippets that are not actually safe to forward as authoritative official references.

The concern here is not simply that a page has share features.
It is the narrower failure mode where the office itself offers a handoff affordance, so the voter reasonably treats the copied/shared artifact as an **officially sanctioned portable pointer**, yet the handoff is stale, partial, misleading, blocked, or truthless about what left the page.

## Why this surface exists

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as core election communications and emphasizes clarity, accessibility, usability, and accuracy. USWDS’s current **Keep a record** guidance matters because it says public-service flows should help users keep a record that includes the site name, URL, date, successful-submission state when relevant, next steps, and reference numbers when possible. MDN’s current **Clipboard API** guidance matters because programmatic clipboard access is browser- and security-constrained, occurs only in secure contexts, and may require permission or transient user activation. MDN’s current **Clipboard.writeText()** guidance matters because it says the method returns a promise that resolves only once the system clipboard has been updated. MDN’s current **Web Share API** and **Navigator.share()** guidance matters because native share support is not universal, is secure-context limited, depends on transient activation, and uses device-specific share targets outside the office’s control; it also says user cancel, missing targets, blocked policy, invalid data, or transmission problems can reject the share promise rather than producing a successful handoff. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `uswds_keep_a_record_page`; xref: `mdn_clipboard_api_page`; xref: `mdn_clipboard_write_text_method_page`; xref: `mdn_web_share_api_page`; xref: `mdn_navigator_share_method_page`)

So this archive treats copy/share posture as its own public-surface problem:
**if the office offers a handoff control, the office should stay honest about what leaves the page, whether the handoff actually succeeded, and whether the resulting artifact remains safe and recoverable enough to function as an official pointer rather than a misleading souvenir.**

## This is distinct from adjacent surfaces

This document is intentionally narrow.
It is **not** the same as:

- `412`, which governs whether permission-gated browser/device capabilities stay optional and fail open when unavailable or denied;
- `413`, which governs leaving the official site or opening a materially different browsing context;
- `437`, which governs durable portable records such as print/save/PDF outputs;
- `438`, which governs whether the current live URL itself is safe to bookmark, copy, or forward later;
- `461`, which governs whether buttons and links tell the truth about navigation versus action;
- `381`, which governs QR codes and short-URL handoffs from print to digital;
- or `473`, which governs browser-generated or search-generated highlighted-text deep links that can circulate even when the office never exposed a Copy/Share control.

`471` exists only for the case where the office itself exposes a **copy/share control** and therefore implicitly vouches for the resulting handoff artifact.

If the operating system, browser, search result, or user later propagates a highlighted-text deep link on its own, that quoted-text handoff posture belongs to `473`.

## Copy/share controls should say what artifact is being handed off

A route fails this surface when the handoff control hides whether it is copying or sharing:

- the current page URL,
- a shortlink,
- a citation-safe snapshot URL,
- a page title plus URL,
- a generated status summary,
- an office phone/email/contact block,
- a confirmation/reference number,
- or another bounded text payload.

The archive does **not** require long labels everywhere.
It does require enough truth that a voter does not have to discover by trial and error whether `Copy`, `Copy link`, `Share`, or `Send` means:

- “copy the current URL,”
- “copy a safer public reference record,”
- “open the device share sheet with title + text + URL,”
- or “copy only the current control’s visible snippet.”

If the artifact differs materially from the full current page, the route should say so.
A copied office phone number is not the same thing as a copied public answer.
A copied short summary is not the same thing as a copied official record.
A share-sheet handoff is not the same thing as a durable citation-safe snapshot.

## Do not signal success before the handoff actually succeeds

MDN’s current clipboard and share guidance is useful here because it is concrete about success and failure semantics. `writeText()` resolves when the system clipboard has been updated. `navigator.share()` resolves or rejects asynchronously, and rejection reasons include user cancel, blocked policy, invalid or hostile data, missing targets, or transmission problems. (xref: `mdn_clipboard_write_text_method_page`; xref: `mdn_navigator_share_method_page`)

For this archive, that means a route should not:

- show `Copied!` before the clipboard write has actually resolved,
- show `Shared!` merely because the share sheet opened,
- silently collapse `user canceled`, `no share target`, `blocked by policy`, and `unsupported browser` into one fake-success outcome,
- or replace truthful outcome messaging with a decorative toast that implies the official handoff is complete when the browser has not confirmed it.

The route does **not** need to narrate browser internals.
It does need to distinguish:

- success,
- unsupported/unavailable,
- blocked/denied,
- canceled,
- and “use this fallback instead”

well enough that the voter is not misled into thinking the official reference already left the page.

## Native share is optional, not the only escape hatch

MDN’s current Web Share guidance says the feature is limited-availability, secure-context only, and must be triggered by transient activation from a UI event. The available targets depend on the device and may include email, messaging apps, contacts, Bluetooth, websites, or the clipboard. (xref: `mdn_web_share_api_page`; xref: `mdn_navigator_share_method_page`)

So for this archive:

- a native `Share` control may be helpful,
- but the route should not make native share support the only portable handoff path,
- and unsupported browsers or constrained environments should still have an ordinary recovery lane such as a visible copyable URL, a stable official link, a durable record, or an explicit help path.

This is especially important on election routes reached through locked-down devices, embedded browsers, assistive technology workflows, or older browsers where native share support may not exist or may behave differently than the office assumed.

## A copied/shared artifact should preserve enough authority and recovery context

USWDS’s current **Keep a record** guidance is important because it emphasizes preserving site name, URL, date, next steps, and reference numbers when those matter. That principle remains useful even when the artifact is smaller than a full printable record. (xref: `uswds_keep_a_record_page`)

For this archive, a copied/shared artifact should preserve enough context to keep later use honest.
Depending on the route, that can mean preserving some bounded subset of:

- office or jurisdiction identity,
- the governing page or route title,
- a stable official URL or safe destination,
- date or `as_of` state when freshness matters,
- the current official help lane,
- or a reference number / office contact needed for the next step.

The archive does **not** require every clipboard/share payload to become a mini-PDF.
It does require that the office’s own handoff control not strip the copied/shared artifact down so far that the result looks authoritative while losing the very facts that make it checkable.

## Do not offer copy/share controls for unsafe or non-forwardable routes without a safer substitute

A route may have a current answer on screen yet still be unsafe to forward directly because the current URL is personalized, stateful, secret-bearing, time-fragile, or otherwise non-share-safe.
That is the terrain of `438`.
`471` adds one narrower rule:
**if the office knows the current live route is not safe to forward directly, the page should not use a copy/share affordance that silently forwards that unsafe route as though it were the right official portable pointer.**

Bounded safe responses include:

- copying a share-safe canonical page instead of the current stateful URL,
- copying a bounded public summary plus the official help route,
- copying a citation-safe snapshot or public notice when exactness matters,
- or suppressing the unsafe handoff control and offering an ordinary record/help path instead.

The archive should not let “Share” become a covert leak of secret-bearing query strings, per-user state, or stale/local-only views.

## Share targets are outside the office’s control, so the office should keep the payload simple and recovery-rich

Once a route hands content to email, SMS, messaging, notes, or another app, the final presentation is no longer under the office’s control.
Titles may be dropped.
URLs may be previewed strangely.
Only one line may remain visible.
The receiving app may truncate the text.

That means the office should prefer a compact, truthful payload that survives degradation:

- avoid overpacked share text that assumes every target will preserve all fields,
- prefer one stable official pointer plus one compact context cue,
- and keep the ordinary help or recovery route nearby if the handed-off artifact later loses fidelity.

The archive does **not** require app-by-app optimization.
It requires humility about the fact that a native share sheet is a handoff to other systems, not a guarantee that the official context will remain perfectly formatted.

## Preserve bounded review evidence, not individualized sharing telemetry

The evidence posture here is about reconstructing whether the office reviewed copy/share truthfulness for important public-answer routes.
The archive should preserve:

- which official routes expose copy/share controls,
- what artifact class each control hands off,
- whether the route distinguishes share-safe versus unsafe current state,
- whether success/failure/cancel/unsupported outcomes were reviewed truthfully,
- whether the copied/shared artifact preserves bounded authority and recovery context,
- and when the review last occurred.

It should **not** require preserving:

- individualized share-target telemetry,
- contact lists,
- clipboard contents tied to named users,
- recipient addresses,
- forwarded message contents,
- or per-user sharing analytics merely to prove that the control once existed.

## Canonical digest artifacts

Publish **small digests of copy/share posture**, not sharing exhaust.

- **Copy/Share Surface Digest (CSSD):** digest of the bounded copy/share posture for an official route family.
- **Clipboard Truthfulness Digest (CTD):** optional digest describing copy outcome semantics and fallback posture.
- **Share Handoff Recovery Digest (SHRD):** optional digest describing share-safe substitution and recovery posture when native share or direct URL forwarding is unsafe.

## What belongs in the public copy/share payload

Keep the payload **small, route-aware, and handoff-focused**.

Recommended top-level fields:

- stable `surface_id`
- `jurisdiction_id` / election scope
- `copy_share_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `reviewed_copy_share_controls[]`
- `artifact_class_note`
- `copy_success_truthfulness_note`
- `share_success_truthfulness_note`
- `unsupported_or_denied_fallback_note`
- `share_safe_substitution_note`
- `authority_context_minimum_note`
- `native_share_boundary_note`
- `clipboard_or_share_permission_note`
- `public_help_route_uri`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:

- individualized share logs,
- recipient identities,
- contact selections,
- copied secret-bearing URLs,
- raw clipboard payload captures,
- or internal growth/engagement analytics that are not needed to reconstruct the bounded public posture.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:

- What artifact does each official copy/share control actually hand off?
- Does the route tell the truth about success versus cancel, unsupported, blocked, or failed handoff states?
- If the current URL is not safely forwardable, does the office substitute a safer public pointer instead of copying the unsafe state?
- Does the copied/shared artifact preserve enough office, route, freshness, or help context to stay checkable later?
- Is native share optional enough that unsupported environments still have a truthful public recovery path?
- Did the office preserve bounded review evidence without retaining individualized sharing telemetry?

## How this fits the family map

Copy/share controls, clipboard-write truthfulness, and native-share handoff posture is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if an office offers a copy/share affordance on an official voter-information route, the resulting handoff should stay honest enough that the office is not quietly minting a misleading portable pointer.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-copy-share-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-copy-share-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- USWDS: Keep a record (xref: `uswds_keep_a_record_page`)
- MDN: Clipboard API (xref: `mdn_clipboard_api_page`)
- MDN: Clipboard.writeText() (xref: `mdn_clipboard_write_text_method_page`)
- MDN: Web Share API (xref: `mdn_web_share_api_page`)
- MDN: Navigator.share() (xref: `mdn_navigator_share_method_page`)
