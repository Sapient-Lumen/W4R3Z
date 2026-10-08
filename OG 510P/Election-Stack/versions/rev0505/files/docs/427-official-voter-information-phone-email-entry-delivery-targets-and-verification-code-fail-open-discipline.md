# 427 — Official voter-information phone/email entry, delivery targets, and verification-code fail-open discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that ask the public to enter or confirm a phone number or email address, send a verification or access code to that contact method, and sometimes require that code before the current answer/help lane can appear**:
registration-status or ballot-status routes that unlock a result after sending a code,
subscription or reminder enrollment pages that must confirm the delivery target,
issue-reporting or appointment-confirmation routes that send a one-time code before the next step,
and similar public answer/help paths where a voter must successfully use a phone or email channel before the official route becomes useful.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help lane and official contact-method routing,
- `307`, which governs problem reporting and civil-rights escalation,
- `370`, which governs official outbound emails/newsletters/reminders themselves,
- `405`, which governs anti-bot challenges and CAPTCHA/WAF boundaries,
- `409`, which governs public-read vs sign-in/session boundaries,
- `412`, which governs browser/device permission prompts,
- `421`, which governs pointer-operability,
- `422`, which governs generic field purpose, autofill, and error recovery,
- `425`, which governs personal-name entry,
- or `426`, which governs exact-string fixed-format identifiers.

It adds one narrow rule:
**if an official voter-information route depends on a voter entering a phone number or email address and sometimes typing a delivered verification code before the current answer/help lane can appear, the office should keep the required contact-method semantics, delivery-target expectations, autofill/paste posture, code-entry behavior, and bounded alternate recovery clear enough that the answer does not depend on guessing whether the route wanted a U.S. number, an SMS-capable mobile number, a shareable email inbox, or a code that can only be retyped by hand.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as a core election responsibility and emphasizes clarity, accessibility, usability, and audience-aware structure. Digital.gov’s current digital-first public-experience guidance says public digital services should be accessible, authoritative, user-centered, and mobile-first. USWDS’s current **Phone number** pattern says teams should say why a phone number is needed, clearly state if a U.S. number or SMS-capable mobile number is required, and use clear hint text; its current **Email address** pattern says teams should allow paste, consider autocomplete, avoid unnecessary re-entry, and provide meaningful error messages. MDN’s current references for `type="tel"`, `type="email"`, and `autocomplete` explain that telephone entry often needs a phone-optimized keypad without implying one global validation format, that email fields support browser-level format validation, and that browsers recognize digital-contact tokens like `tel`, `email`, and `one-time-code`. W3C’s current guidance on **Identify Input Purpose** and **On Input** reinforces programmatic field-purpose clarity and warns against surprise context changes. WCAG 2.2’s current **Accessible Authentication** guidance is framed around authentication, but it is still directly relevant here because it says people can be blocked by retyping one-time passcodes, and it highlights support for paste and alternate second-factor mechanisms. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `uswds_phone_number_pattern_page`; xref: `uswds_email_address_pattern_page`; xref: `mdn_input_type_tel_element_page`; xref: `mdn_input_type_email_element_page`; xref: `mdn_autocomplete_attribute_page`; xref: `mdn_webotp_api_page`; xref: `w3c_wcag21_identify_input_purpose_page`; xref: `w3c_wcag21_on_input_page`; xref: `w3c_wcag22_accessible_authentication_minimum_page`; xref: `w3c_wcag22_accessible_authentication_enhanced_page`)

That is enough to justify a compact control here.
A route can be current, generally accessible, and even pass `422` or `426`, yet still fail first contact because:
- the page silently requires a U.S. or SMS-capable mobile number,
- the voter enters a landline or shared office number and gets no meaningful recovery,
- the route rejects an ordinary but valid email format,
- autocomplete is absent or mis-scoped on repeated contact fields,
- the delivered code must be manually retyped even though the platform could assist,
- paste/autofill is blocked,
- or typing the last code digit silently auto-submits or changes context without warning.

## This is not the same thing as generic field-entry review or exact-identifier review

`422` asks whether the voter can generally tell what to type, preserve values, and recover from an ordinary input error.

`426` asks whether an exact fixed-format public token survives leading zeros, letters, separators, masks, and retry.

`427` asks a different question:
**once the route depends on a delivery target such as a phone number or email address, and sometimes on a follow-on code, can the voter tell what channel is required, enter it in an ordinary way, receive or paste the code without surprise behaviors, and reach a bounded alternate/help lane if delivery or verification fails?**

A route may pass `422` and still fail `427` if:
- it labels the field “Phone” but never says that SMS delivery is required,
- it forces re-entry of an email address without a safety rationale,
- it blocks paste of an email address or code,
- it uses segmented code boxes that trap correction or screen-reader review,
- it auto-submits on the last keystroke without warning,
- or it tells the voter merely “verification failed” without separating bad contact format, code expiration, delivery failure, and no-signal/no-inbox recovery.

## Say why the contact method is needed and what kind of contact method actually works

USWDS’s current phone and email patterns are useful because they are concrete. They say teams should tell users why a contact method is needed, why they may be contacted, and when. The phone pattern separately says to state clearly when a U.S. number or an SMS-capable mobile number is required. (xref: `uswds_phone_number_pattern_page`; xref: `uswds_email_address_pattern_page`)

For this archive, that means the route should say, near the field:
- whether the office needs a phone number, email address, or either one,
- whether the route specifically needs a U.S. number,
- whether the route specifically needs an SMS-capable mobile number,
- whether the route sends only a one-time code or may also send reminders/follow-up,
- and whether a bounded alternate contact or help lane exists if the voter cannot use that channel.

The rule is not “explain everything about notifications.”
It is “do not make the voter guess whether the public route wanted any phone number, a mobile phone able to receive texts, or a working email inbox that the voter can immediately access.”

## Let ordinary phone and email entry succeed without overfitting the parser

USWDS’s current phone and email patterns, together with MDN’s current `tel` and `email` references, point toward a narrow posture here:
- phone numbers are entered in many common formats and often benefit from phone-optimized mobile keypads,
- email fields can benefit from browser-level format checks,
- and neither should be made brittle through unnecessary local assumptions about what "real" user data looks like. (xref: `uswds_phone_number_pattern_page`; xref: `uswds_email_address_pattern_page`; xref: `mdn_input_type_tel_element_page`; xref: `mdn_input_type_email_element_page`)

For this archive, that means:
- allow ordinary paste into phone and email fields,
- do not reject common, valid email local-part characters or domains without a real policy reason,
- do not assume that every phone number the voter types can receive SMS unless the route has said that an SMS-capable mobile number is required,
- and do not make re-entry of the same address or number the default error-prevention strategy.

## Use programmatic field-purpose cues when the route collects contact data

W3C’s **Identify Input Purpose** guidance and MDN’s current `autocomplete` reference are directly useful here because contact fields are exactly the kind of user data for which field purpose should be machine-discernible. MDN also notes that repeating the same autocomplete token across different logical groups can cause the browser to fill every matching occurrence with the same value unless grouping tokens are used. (xref: `w3c_wcag21_identify_input_purpose_page`; xref: `mdn_autocomplete_attribute_page`)

That means `427` should review whether:
- phone fields use the correct digital-contact tokens,
- email fields use the correct tokens,
- repeated contact groups are distinguished when the route has more than one logical recipient or step,
- and the route keeps enough structure that assistive technology and browser autofill can help rather than guess.

This does **not** require aggressive autofill everywhere.
It requires the route not to sabotage the browser/assistive cues that make ordinary contact entry easier.

## Code-entry lanes should allow assistive help, paste, and predictable correction

MDN’s current WebOTP guidance says a field marked `autocomplete="one-time-code"` is worth including, and shows a `text` field with `autocomplete="one-time-code"` and `inputmode="numeric"`. WCAG 2.2’s current accessible-authentication guidance says people can be blocked by retyping one-time passcodes and highlights not blocking paste plus allowing other accessible factor mechanisms. (xref: `mdn_webotp_api_page`; xref: `w3c_wcag22_accessible_authentication_minimum_page`; xref: `w3c_wcag22_accessible_authentication_enhanced_page`)

For this archive, that means:
- a verification-code field should support paste,
- should stay reviewable and correctable with keyboard and screen reader,
- should not require manual transcription when a platform/browser assistive path is available,
- and should not make split-box choreography the only workable entry posture.

`427` does **not** require every office to implement WebOTP or passkeys.
It requires the office not to make code-entry unnecessarily harder than the platform already makes possible.

## Do not let typing the last code digit become an unannounced context change

W3C’s **On Input** guidance is small but directly relevant: if input changes context, users should be forewarned. (xref: `w3c_wcag21_on_input_page`)

For `427`, that means code-entry and contact-entry flows should be explicit about whether:
- the route auto-submits when a code is complete,
- the route advances focus automatically across segmented code boxes,
- a new step or spinner appears as soon as the contact method validates,
- or the route triggers a resend/change-method step on input completion.

Auto-advance and auto-submit are not forbidden here.
They are bounded by one rule:
**the voter should not have to discover by surprise that finishing input immediately changed context or committed the route.**

## Error recovery should distinguish contact-format problems, delivery failure, and code mismatch

A public voter-information route should not collapse all failure states into “invalid code” or “contact error.”
The recovery posture should separate at least:
- malformed or unsupported contact target,
- wrong channel type for the task (for example, a non-SMS phone number where SMS is required),
- code delivery not received,
- code expired,
- code mismatch,
- and too-many-attempt or temporary-send throttle states.

The entered contact target should survive retry when safe.
The route should keep a visible first-party help/contact lane for cases where automated delivery itself is the failure.
This surface is not satisfied if the office merely says “try again later” while clearing the contact data and hiding the support path.

## Preserve bounded review state, not real inboxes, phone lists, or code logs

This control is about public-answer integrity, not creating a sensitive archive of personal contact data or verification exhaust.
The evidence posture should therefore preserve:
- which public routes depend on a phone number, email address, or verification code,
- whether the route states if SMS-capable/U.S.-number constraints apply,
- whether ordinary paste/autofill/correction paths were reviewed,
- whether code-entry surprise-submit and recovery behavior were reviewed,
- and when the review last occurred.

It should **not** require preserving real voter phone numbers, real email addresses, live verification codes, full send logs tied to named voters, mailbox contents, SMS bodies containing active codes, or exhaustive authentication/session replay when bounded policy reconstruction is sufficient.

## What to test

- Can a voter tell whether the route wants a phone number, an email address, or either one?
- If the route needs a U.S. number or an SMS-capable mobile number, is that stated before failure?
- Do ordinary pasted phone numbers and email addresses survive without needless rejection?
- Are contact fields marked up in a way that lets assistive tech and browser autofill recognize their purpose?
- If the route sends a code, does code entry support paste, accessible review, and predictable correction?
- If the route auto-advances or auto-submits, is that predictable rather than surprising?
- When verification fails, does the page distinguish contact-format issues, delivery failure, expired code, and wrong-code states?
- Does a visible first-party help or alternate recovery lane remain available when automated delivery is the weak link?

## Minimal companion artifacts

- Template payload: `artifacts/templates/official-voter-information-contact-target-verification-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-contact-target-verification-surface-checklist.md`
